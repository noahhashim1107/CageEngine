import pytest
import os
import tempfile
from app.tasks import run_prediction_task
from unittest.mock import patch

@pytest.fixture
def dummy_file():

    return {
        "filename": "dummy.mol2",
        "content": "dummy content"
    }


@pytest.fixture
def temp_grid_file():

    # create a temporary grid file to satisfy the existence check
    temp_dir = "/app/grids"
    os.makedirs(temp_dir, exist_ok = True)
    temp_path = os.path.join(temp_dir, "grid_4.dat")
    with open(temp_path, "w") as f:
        f.write("grid content")
    yield temp_path
    os.remove(temp_path)


@patch("app.handlers.execution_handler.run_algorithm", return_value = "simulated")
def test_run_prediction_task_success(mock_algo, dummy_file, temp_grid_file):

    result = run_prediction_task(
        
        host_files = [dummy_file],
        guest_files = [dummy_file],
        grid_name = "grid_4.dat",
        delta_r = 0.3,
        is_robust = True
    )

    
    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert "runtime" in result
    assert "results" in result
    assert isinstance(result["results"], list)
    assert result["results"][0]["caging_results"] in ["strong cage", "weak cage", "not a cage"]


@patch("app.handlers.execution_handler.run_algorithm", return_value = "simulated")
def test_run_prediction_task_without_robustness(mock_algo, dummy_file, temp_grid_file):

    result = run_prediction_task(

        host_files = [dummy_file],
        guest_files = [dummy_file],
        grid_name = "grid_4.dat",
        delta_r = 0.2,
        is_robust = False
    )

    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert len(result["results"]) == 1
    assert result["results"][0]["caging_results"] in ["cage", "not a cage"]


def test_run_prediction_task_invalid_grid(dummy_file):

    # run without creating the grid file on purpose

    result = run_prediction_task(

        host_files = [dummy_file],
        guest_files = [dummy_file],
        grid_name = "nonexistent.dat",
        delta_r = 0.3,
        is_robust = True
    )

    assert result["status"] == "error"
    assert "Grid file nonexistent.dat not found" in result["message"]