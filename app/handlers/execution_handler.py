# app/handlers/execution_handler.py
import subprocess

def run_algorithm(host_path: str, guest_path: str, delta_r: float, grid_path: str, simulate: bool = True,) -> str:
    
    
    if simulate:
        return f"Simulated prediction for {host_path} and {guest_path}"
    
    try:
       
       result = subprocess.run(
           [
              
               "./algo",
               host_path,
               guest_path,
               f"{delta_r}",
               grid_path

           ],
           
           capture_output = True,
           text = True,
           check = True
       )
       
       return result.stdout.strip()
    
    except subprocess.CalledProcessError as e:
        return f"Execution failed: {e.stderr.strip()}"
    
    except Exception as e:
        return f"Unhandled error during execution: {str(e)}"