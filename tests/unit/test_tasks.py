import pytest
from app.tasks import run_prediction_task

def test_task_runs_and_returns_dict():

    dummy_file = {
        "filename": "dummy.mol2",
        "content" : "dummy stuff"
    }

    result = run_prediction_task(
        host_files = [dummy_file],
        guest_files = [dummy_file],
        grid_name = "grid_4.dat",
        delta_r = 0.3,
        is_robust = False
    )

    assert isinstance(result, dict)
    assert "status" in result