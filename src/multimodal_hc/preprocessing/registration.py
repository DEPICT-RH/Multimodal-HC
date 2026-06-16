import ants
import numpy as np
from pathlib import Path

def register_rigid_ants(
    moving_path: Path,
    fixed_path: Path,
) -> np.ndarray:
    # Perform registration
    mytx = ants.registration(
        fixed=ants.image_read(str(fixed_path)),
        moving=ants.image_read(str(moving_path)),
        type_of_transform='Rigid',
        verbose=False
    )

    fwd_trns = ants.read_transform(mytx['fwdtransforms'][0])
    ## Create affine matrix
    rot = fwd_trns.parameters[:9].reshape(3, 3) #rotation
    t = fwd_trns.parameters[9:] #translation
    c = fwd_trns.fixed_parameters #center
    w = t + c - np.dot(rot, c) #offset
    aff = np.eye(4) 
    aff[:3, :3] = rot
    aff[:3, 3] = w
    flip_lps_ras = np.diag([-1, -1, 1,1])
    
    ## change from sitk space to nibabel space and invert to get mov2fix and not fix2mov
    aff_mr2pt = flip_lps_ras@np.linalg.inv(aff)@flip_lps_ras

    return aff_mr2pt

