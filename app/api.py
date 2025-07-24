from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.handlers.file_handler import validate_file
from app.tasks import run_prediction_task, celery
from celery.result import AsyncResult
import logging

## removed previous functions and added to tasks, as i was unfamiliar with celery work and had to rework code include in github update

# FastAPI router
router = APIRouter()

# API endpoint for prediction
@router.post("/predict")

async def predict(
    
    host_files: List[UploadFile] = File(...),
    guest_files: List[UploadFile] = File(...),
    grid: str = Form("grid_4.dat"),
    delta_r: float = Form(...),
    is_robust: bool = Form(True)
   
):
    
    try:

        # file limit checks
        if len(host_files) > 500:
            raise HTTPException(status_code=400, detail="Maximum of 500 host files allowed")
        if len(guest_files) > 500:
            raise HTTPException(status_code=400, detail="Maximum of 500 guest files allowed")
        if len(host_files) + len(guest_files) > 1000:
            raise HTTPException(status_code=400, detail="Total file count must not exceed 1000 files")
        
        
        # Validate file types
        for file in host_files:
            validate_file(file, ".mol2")

        for file in guest_files:
            validate_file(file, ".mol2")
       
        
        if grid not in ["grid_2.dat", "grid_3.dat", "grid_4.dat"]:
            raise HTTPException(status_code=400, detail="Invalid grid selection")

        
        
        # Read and encode host and guest file contents 
        host_payloads = []
        for file in host_files:
            content = await file.read()
            host_payloads.append({
                "filename": file.filename,
                "content": content.decode("latin1")
            })

        guest_payloads = []
        for file in guest_files:
            content = await file.read()
            guest_payloads.append({
                "filename": file.filename,
                "content": content.decode("latin1")
            })

        

        # Submit celery task asynchronously 
        task = run_prediction_task.delay(

            host_payloads,
            guest_payloads,
            grid,
            delta_r,
            is_robust
        )

        return {"task_id": task.id, "status": "queued"}


    except HTTPException as help:
        raise help
    except Exception as error:
        logging.exception("Prediction request failed")
        raise HTTPException(status_code=500, detail=str(error))


# API endpoint for getting results
@router.get("/results/{task_id}")
async def get_result(task_id: str):
    task_result = AsyncResult(task_id, app=celery)

    if task_result.state == "PENDING":
        return {"status": "pending"}
    
    elif task_result.state == "SUCCESS":
        return {"status": "complete", "data": task_result.result}
    
    elif task_result.state == "FAILURE":
        return {
            "status": "error",
            "message": str(task_result.result)
        }
    
    else:
        return {"status": task_result.state}