import pytest
from fastapi import HTTPException
from app.utils.parameter_builder import parse_parameters

def test_parse_parameters_without_robustness():

    result = parse_parameters(delta_r=1.0, robustness=False)
