from fastapi import HTTPException
from typing import Optional

# parse delta_r and robustness mode into a list of values for prediction
def parse_parameters(
        
        delta_r: Optional[float] = 0.0,
        robustness: Optional[bool] = False
):
    
    is_robust = robustness or False

    if is_robust:
        
        if delta_r is None:
            raise HTTPException(status_code=400, detail="delta_r is required when robustness is enabled.")
        
        try:
            delta_r = float(delta_r)
        
        except ValueError:
            raise HTTPException(status_code=400, detail="detail_r must be a float.")
        
        # generate 3 values: -r, 0 +r
        delta_r_values = [-delta_r, 0, delta_r]
    
    else:
        delta_r = 0.0
        delta_r_values = [0.0]

    
    return {
        "delta_r": delta_r,
        "robustness": is_robust,
        "runs": len(delta_r_values),
        "delta_r_values": delta_r_values
    }
        

 
    