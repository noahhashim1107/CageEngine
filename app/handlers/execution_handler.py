# app/handlers/execution_handler.py
import subprocess
import time
from typing import List

def run_algorithm(host_path, guest_path, delta_r, grid_resolution):
    
    # simulate algo by 30 seconds
    time.sleep(30) 
    
    # Replace with actual C++ binary call later                 
    # host.mol2 guest.mol2 +-delta_r grid.dat
    try:
        result = subprocess.run(
            ["echo", f"Simulating prediction for {host_path} and {guest_path}"],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception as error:
        return f"Error: {str(error)}"