import os
import time
import logging

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

def run_prediction_task(self, host_file, guest_file, gridres_file, delta_r, is_robust):
    
    try:

        # simulate task by 30 seconds
        time.sleep(30)
        
        #show runtime
        start_time = time.time()

        logging.info(f"[STARTED] Task ID: {self.request.id} | Files: {host_file['filename']}, {guest_file["filename"]} | Params: delta=r{delta_r}, robust={is_robust}")

        #validate file types for celery
        validate_file(host_file, ".mol2")
        validate_file(guest_file, ".mol2")
        validate_file(gridres_file, ".dat")

        ## rebuild temp files
        host_path = reconstruct_file(host_file, suffix=".mol2")
        guest_path = reconstruct_file(guest_file, suffix=".mol2")
        gridres_path = reconstruct_file(gridres_file, suffix=".dat")

        ## Parse delta r logic: returns list of one or three values
        deltas = parse_parameters(delta_r, is_robust)

        
        ## Run algo for each delta r
        results = []
        for i, r in enumerate(deltas["delta_r_values"], start=1):

            output = run_algorithm(host_path, guest_path, r, gridres_path)
            
            # Dummy parser as algo has not been inputed properly yet, uses resultsto generate basic "summary"
            if "strong" in output.lower():
                parsed = "strong"
            
            elif "weak" in output.lower():
                parsed = "weak"
            
            else:
                parsed = "none"
            
            
            results.append({
                "run_id": i,
                "delta_r": r,
                "raw_output": output.strip(),  # trim whitespace
                "parsed_result": parsed # for algo implementation
            })

        # Determine summary

        if any(r["parsed_result"] == "strong" for r in results):
            summary = "strong cage"
        
        elif any(r["parsed_result"] == "weak" for r in results):
            summary = "weak cage"
        
        else:
            summary = "not a cage"
        
        

        
        # Time between task start and finish
        runtime = round(time.time() - start_time, 2)

        logging.info(f"[COMPLETED] Task ID: {self.request.id} | Summary: {summary} | Runtime: {runtime}s")


        return {
            
            "status": "success",
            "summary": summary,
            "runtime": f"{runtime}s",
            "files": {
                "host": host_file["filename"],
                "guest": guest_file["filename"],
                "grid": gridres_file["filename"]
            },
            "parameters": deltas,
            "results": results
        }
    
    except Exception as error:
        logging.exception(f"[FAILED] Task ID: {self.request.id} | Error: {str(error)}")
        return {"status": "error", "message": str(error)}
      
    
    
    finally:  # Cleans tempfiles up even on failure
         
        cleanup_temp_files(host_path, guest_path, gridres_path)