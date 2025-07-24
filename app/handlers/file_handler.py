import os
import shutil
import tempfile
from fastapi import UploadFile, HTTPException


def validate_file(file, expected_ext: str):
    
   # checks if the uploaded file (UploadFile or dict) has the expected extension
    
    filename = file["filename"] if isinstance(file, dict) else file.filename

    if not filename.lower().endswith(expected_ext):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type for {filename}. Expected {expected_ext}"
        )


def reconstruct_file(file_dict: dict, suffix: str) -> str:
    """
    reconstructs a file from a dictionary payload with 'filename' and 'content',
    writes it to disk as a temporary file, and returns the path.
    """
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)

    with open(temp.name, "wb") as f:
        f.write(file_dict["content"].encode("latin1"))  # latin1 for byte for byte decoding

    return temp.name


def cleanup_temp_files(*filepaths: str):
    """
    Deletes temporary files passed as arguments
    Logs warning if file deletion fails
    """
    for path in filepaths:
        try:
            os.remove(path)
        except Exception as error:
            print(f"Warning: Failed to delete temp file {path} - {error}")
