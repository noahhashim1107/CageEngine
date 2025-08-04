import pytest
from fastapi import HTTPException
from app.utils.parameter_builder import parse_parameters

def test_parse_parameters_without_robustness():

    result = parse_parameters(delta_r = 1.0, robustness = False)
    assert result["delta_r_values"] == [0.0]
    assert result["is_robust"] is False


def test_parse_parameters_with_robustness():

    result = parse_parameters(delta_r = 0.3, robustness = True)
    assert sorted(result["delta_r_values"]) == [-0.3, 0.0, 0.3]
    assert result["is_robust"] is True


def test_parse_parameters_invalid_float():
    
    with pytest.raises(HTTPException):
        parse_parameters(delta_r = "epic fail", robustness = True)