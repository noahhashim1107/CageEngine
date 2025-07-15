import os
import time
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
        for r in deltas:

            output = run_algorithm(host_path, guest_path, r, gridres_path)
            results.append({"delta_r" : r, "output": output})

        
        # Dummy parser as algo has not been inputed properly yet, uses resultsto generate basic "summary"
        if any("strong" in r["output"].lower() for r in results):
            summary = "strong cage"
        
        elif any("weak" in r["output"].lower() for r in results):
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
            "results": results,
            "host_file": host_file["filename"],
            "guest_file": guest_file["filename"],
            "grid_file": gridres_file["filename"],
            "parameters": {
                "delta_r": delta_r,
                "robustness": is_robust
            },
            "raw_outputs": results
        }
    
    except Exception as error:
        logging.exception(f"[FAILED] Task ID: {self.request.id} | Error: {str(error)}")
        return {"status": "error", "message": str(error)}
      
    
    
    finally:  # Cleans tempfiles up even on failure
         
        cleanup_temp_files(host_path, guest_path, gridres_path)