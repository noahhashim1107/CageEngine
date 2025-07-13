import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, HTTPException




# a function for basic filetype validation to guard against bad uploads

def validate_file(file_dict, expected_ext: str):
    if not file_dict["filename"].lower().endswith(expected_ext):
        raise ValueError(f"Invalid file type for {file_dict['filename']}. Expected {expected_ext}")


# save uploaded files to disk (not used in current celery setup)
def save_files(host: UploadFile, guest: UploadFile, gridres: UploadFile):
    validate_file(host, ".mol2")
    validate_file(guest, ".mol2")
    validate_file(gridres, ".dat")

    host_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mol2")
    guest_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mol2")
    gridres_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".dat")

    with open(host_temp.name, "wb") as f:
        shutil.copyfileobj(host.file, f)

    with open(guest_temp.name, "wb") as f:
        shutil.copyfileobj(guest.file, f)

    with open(gridres_temp.name, "wb") as f:
        shutil.copyfileobj(gridres.file, f)

    return host_temp.name, guest_temp.name, gridres_temp.name


# reconstruct file from base64-like contnent and write to disk
def reconstruct_file(file_dict, suffix: str):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    
    with open(temp.name, "wb") as f:
        f.write(file_dict["content"].encode('latin1'))
    
    return temp.name

# delete temporary files to clean up disk space (optimisation)
def cleanup_temp_files(*filepaths):
    
    for path in filepaths:
       
        try:
            os.remove(path)

        except Exception as error:
            print(f"Warning: Failed to delete temp file {path} - {error}")