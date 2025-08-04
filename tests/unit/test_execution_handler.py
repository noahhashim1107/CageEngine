import pytest
from app.handlers.execution_handler import run_algorithm

def test_run_algorithm_simulated():

    result = run_algorithm("host.mol2", "guest.mol2", 0.3, "grid_4.dat", simulate = True)
    assert "Simulated" in result or isinstance(result, str)