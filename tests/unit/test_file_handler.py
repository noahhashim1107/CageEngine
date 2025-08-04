import pytest
from fastapi import UploadFile, HTTPException
from app.handlers.file_handler import validate_file, reconstruct_file, cleanup_temp_files

def test_validate_file_accepts_correct_extension():

    file = {"filename": "sample.mol2"}
    validate_file(file, ".mol2") # should not raise


def test_validate_file_rejects_wrong_extension():

    file = {"filename": "wrong.txt"}
    with pytest.raises(HTTPException):
        validate_file(file, ".mol2")


def test_reconstruct_and_cleanup():

    content_dict = {"filename": "host.mol2", "content": "not real mol2 data buddy"}
    path = reconstruct_file(content_dict, suffix= ".mol2")
    assert path.endswith(".mol2")

    cleanup_temp_files(path) # should not throw