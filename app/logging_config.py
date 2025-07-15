import logging
import os

LOG_DIR = "logs"
LOG_FILE = "predictions.log"
os.makedirs(LOG_DIR, exist_ok=True)

def configure_logging():
    
    logging.basicConfig(

        filename=os.path.join(LOG_DIR, LOG_FILE),
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    
    )