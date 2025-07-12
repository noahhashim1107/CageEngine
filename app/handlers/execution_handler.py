# app/handlers/execution_handler.py
import subprocess
from typing import List

def run_algorithm(host_path, guest_path, delta_r, grid_resolution):
    # Replace with actual C++ binary call later                   #CHANGE COMMENTS FOR EVERYTHING SAME AS LAPTOP
    # host.mol2 guest.mol2 --delta_r 2.5
    try:
        result = subprocess.run(
            ["echo", f"Simulating prediction for {host_path} and {guest_path}"],
            capture_output=True, text=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"