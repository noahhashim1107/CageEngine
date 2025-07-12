import os

from celery import Celery  

## Importing functions
from app.handlers.execution_handler import run_algorithm
from app.handlers.file_handler import save_files
from app.utils.parameter_builder import parse_parameters    


celery = Celery(
    
    "tasks",

    ## Specifying broker and backend (default RabbitMQ)
    broker=os.getenv("CELERY_BROKER_URL", "amqp://localhost:5672"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "rpc://")             
)

## Bind task to access "self" for retries/states
@celery.task(bind=True)

def run_prediction_task(self, host_file, guest_file, grid_file, delta_r, is_robust):
    
    try:

        ## Save files and parse parameters
        host_path, guest_path, grid_path = save_files(host_file, guest_file, grid_file)
        
        ## Parse delta r logic: returns list of one or three values
        deltas = parse_parameters(delta_r, is_robust)

        results = []

        
        ## Run algo for each delta r
        for r in deltas:

            result = run_algorithm(host_path, guest_path, r, grid_path)
            results.append({"delta_r" : r, "output": result})


        return {
            
            "status": "success",
            "results": results,
            "host_file": host_file.filename,
            "guest_file": guest_file.filename,
            "delta_r_values": deltas
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}