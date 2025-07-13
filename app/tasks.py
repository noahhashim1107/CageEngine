import os
import logging

from celery import Celery  

from app.handlers.execution_handler import run_algorithm
from app.handlers.file_handler import validate_file, reconstruct_file, cleanup_temp_files
from app.utils.parameter_builder import parse_parameters



celery = Celery(
    
    "tasks",

    ## Specifying broker and backend (default RabbitMQ)
    broker=os.getenv("CELERY_BROKER_URL", "amqp://localhost:5672"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "rpc://")             
)

# Celery task for running prediciton algo asynchronously
## Bind task to access "self" for retries/states
@celery.task(bind=True)

def run_prediction_task(self, host_file, guest_file, gridres_file, delta_r, is_robust):
    
    try:

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
        for r in deltas:

            output = run_algorithm(host_path, guest_path, r, gridres_path)
            results.append({"delta_r" : r, "output": output})

        # Cleanup temp files
        cleanup_temp_files(host_path, guest_path, gridres_path)

        return {
            
            "status": "success",
            "results": results,
            "host_file": host_file["filename"],
            "guest_file": guest_file["filename"],
            "parameters": {
                "delta_r": delta_r,
                "robustness": is_robust
            }
        }
    
    except Exception as error:
        logging.exception("Celery task failed")
        return {"status": "error", "message": str(error)}