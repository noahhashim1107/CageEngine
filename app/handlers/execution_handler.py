# app/handlers/execution_handler.py
import subprocess
import time
from typing import Optional

def run_algorithm(host_path: str, guest_path: str, delta_r: float, grid_path: str, simulate: bool = True,) -> str:
    
    
   # if simulate:
    # simulate algo by 30 seconds
        #time.sleep(3) 
        #return f"Simulated prediction for {host_path} and (guest_path)"
    
    # Replace with actual C++ algo call later                 
   
    try:

        result = subprocess.run(
            [
           
                "./algo", # replace with algo
                host_path,
                guest_path,
                f"{delta_r}",
                grid_path
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    
    except subprocess.CalledProcessError as e:
        return f"Execution failed: {e.stderr.strip()}"
    except Exception as e:
        return f"Unhandled error during execution: {str(e)}"