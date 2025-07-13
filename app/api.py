from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.handlers.file_handler import validate_file
from app.tasks import run_prediction_task 
import logging

## removed previous functions and added to tasks, as i was unfamiliar with celery work and had to rework code include in github update

# FastAPI router
router = APIRouter()

# API endpoint for prediction
@router.post("/predict")

async def predict(
    
    host_file: UploadFile = File(...),
    guest_file: UploadFile = File(...),
    gridres_file: UploadFile = File(...),
    
    delta_r: float = Form(...),
    
    is_robust: bool = Form(True)
   
):
    
    try:

        # Validate file types
        validate_file(host_file, ".mol2")
        validate_file(guest_file, ".mol2")
        validate_file(gridres_file, ".dat")

        # Read file contents in bytes
        host_bytes = await host_file.read()
        guest_bytes = await guest_file.read()
        gridres_bytes = await gridres_file.read()

        # Submit celery task asynchronously 
        task = run_prediction_task.delay(

            {
                "filename": host_file.filename,
                "content": host_bytes.decode('latin1')
            },
            
            {
                "filename": guest_file.filename,
                "content": guest_bytes.decode('latin1')
            },
            
            {
                "filename": gridres_file.filename,
                "content": gridres_bytes.decode('latin1')
            },
            
            delta_r,
            is_robust
        )

        return {"task_id": task.id, "status": "queued"}


    except HTTPException as help:
        raise help
    except Exception as error:
        logging.exception("Prediction request failed")
        raise HTTPException(status_code=500, details=str(error))

 