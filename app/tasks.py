import os
import time
import logging
import random # since algo not implememnted

from celery import Celery
from kombu import Queue, Exchange

from app.handlers.execution_handler import run_algorithm
from app.handlers.file_handler import validate_file, reconstruct_file, cleanup_temp_files
from app.utils.parameter_builder import parse_parameters



celery = Celery(
    
    "tasks",

    ## Specifying broker and backend (default RabbitMQ)
    broker=os.getenv("CELERY_BROKER_URL", "amqp://cageengine:deva02@rabbitmq:5672//"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "rpc://")             
)


# Queue configuration for better observation and message routing
celery.conf.task_queues = (

    Queue('celery', Exchange('celery'), routing_key='celery', durable=True),
)
celery.conf.task_default_queue = 'celery'
celery.conf.task_default_exchange = 'celery'
celery.conf.task_default_routing_key = 'celery'

# Enable monitoring events (for RabbitMQ UI visibility) - currently does not work
celery.conf.worker_send_task_events = True
celery.conf.task_send_sent_event = True


# Celery task for running prediciton algo asynchronously
## Bind task to access "self" for retries/states
@celery.task(bind=True)

def run_prediction_task(self, host_files, guest_files, grid_name, delta_r, is_robust):
    
    try:

        # show runtime and log
        start_time = time.time()
        logging.info(f"[STARTED] Task ID: {self.request.id} | Grid: {grid_name} | Params: delta_r={delta_r}, robust={is_robust}")
        
       
        # validate and rebuild file types for celery
        host_paths = []
        guest_paths = []

        
        for f in host_files:
            validate_file(f, ".mol2")
            path = reconstruct_file(f, suffix=".mol2")
            host_paths.append((f["filename"], path))

        for f in guest_files:
            validate_file(f, ".mol2")
            path = reconstruct_file(f, suffix=".mol2")
            guest_paths.append((f["filename"], path))


        # locate grid file (in a folder)

        grid_dir = "/app/grids"
        grid_path = os.path.join(grid_dir, grid_name)
        if not os.path.exists(grid_path):
            raise Exception(f"Grid file {grid_name} not found")
        
        
        # gets delta_r variants 
        deltas = parse_parameters(delta_r, is_robust)

        
        # Run algo for each delta r
        results = []
        run_id = 0

        for host_name, host_path in host_paths:
            for guest_name, guest_path in guest_paths:
                pair_runs = []
                for r in deltas["delta_r_values"]:
                    
                    output = run_algorithm(host_path, guest_path, r, grid_path)

                    caging_result = random.choice(["strong cage", "weak cage", "not a cage"])

                    pair_runs.append({
                        "run_id": run_id,
                        "delta_r": r,
                        "caging_result": caging_result
                    })
                    run_id += 1

                results.append({
                    "host": host_name,
                    "guest": guest_name,
                    "runs": pair_runs
                })

        
        # Time between task start and finish
        runtime = round(time.time() - start_time, 2)
        logging.info(f"[COMPLETED] Task ID: {self.request.id} | Runtime: {runtime}s")


        return {
            "status": "success",
            "runtime": f"{runtime}s",
            "grid_used": grid_name,
            "parameters": deltas,
            "results": results
        }
    
    except Exception as error:
        logging.exception(f"[FAILED] Task ID: {self.request.id} | Error: {str(error)}")
        return {"status": "error", "message": str(error)}
      
    
    
    finally:  # Cleans tempfiles up even on failure
         
        cleanup_temp_files(*[p for _, p in host_paths], *[p for _, p in guest_paths])