from fastapi import APIRouter, UploadFile, File, Form
from app.handlers.file_handler import save_files
from app.handlers.execution_handler import run_algorithm

router = APIRouter()

@router.post("/predict")

async def predict(
    
    host_file: UploadFile = File(...),
    guest_file: UploadFile = File(...),
   
    delta_r: float = Form(...),
    gridres_file: UploadFile = File(...)
):
    
   # 1 save uploaded files
    host_path, guest_path, gridres_path = save_files(host_file, guest_file, gridres_file)

    # 2 build args and run algorithm
    result = run_algorithm(host_path, guest_path, delta_r, gridres_path) 
    
    # 3 return output
    return {
        "result": result,
        "host_filename": host_file.filename,
        "guest_filename": guest_file.filename,
        "parameters": {
            "delta_r": delta_r
        },
        "gridres_filename": gridres_file.filename
    }