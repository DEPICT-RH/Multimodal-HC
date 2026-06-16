from pathlib import Path
from dotenv import load_dotenv
import os 
import json
import re 
import nibabel as nib
import numpy as np
import pandas as pd
from scipy.ndimage import binary_erosion

def save_numpy_array(
    array: np.ndarray,
    output_path: Path,
) -> None:
    """Save array to file."""
    output_path.parent.mkdir(exist_ok=True, parents=True)
    np.savetxt(output_path, array)


def get_head_center(totalseg_img_path):
    """Returns world-coordinates of brain center"""
    seg = nib.load(totalseg_img_path)
    ixs = np.where(seg.get_fdata() == 90)
    center_vox = np.array([(np.min(x)+np.max(x))/2 for x in ixs]+[1])
    center_world = seg.affine@center_vox
    return center_world[:3]


def get_voxmap_around_centerpoint(center_point,isotropic_mm,size_mm):
    """Creates (shape, affine) isotropic voxmap of world-space-size `size_mm` around `center_point`"""
    shape = tuple(round(x/isotropic_mm) for x in size_mm)
    affine = np.diag([-isotropic_mm,isotropic_mm,isotropic_mm,1])
    offset = np.array(size_mm)/2
    offset[0] = -offset[0]
    affine[:3,-1] = center_point-offset
    return shape, affine


def binary_erode(arr,n):
    if n==0:
        return arr
    new_mask = np.zeros_like(arr)
    un = list(np.unique(arr))
    un.remove(0)
    for k in un:
        m = arr==k
        m = binary_erosion(m,iterations=n)
        new_mask[m] = k
    return new_mask
