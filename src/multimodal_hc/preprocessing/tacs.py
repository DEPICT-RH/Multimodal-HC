from nifti_dynamic.tacs import extract_multiple_tacs, save_tac
import nibabel as nib
import numpy as np
from multimodal_hc.preprocessing.bids import create_derivatives_sidecar
from multimodal_hc.preprocessing.utils import binary_erode
from multimodal_hc.utils import load_sidecar

def extract_and_save_tac(dpet_path,seg_path,tac_save_folder,erosion):
    if isinstance(seg_path, np.ndarray):
        seg = seg_path
        sources = [dpet_path]
    else:
        seg = nib.load(seg_path).get_fdata()
        seg = binary_erode(seg,erosion)
        sources = [dpet_path,seg_path]
    
    dpet_json = load_sidecar(dpet_path)
    create_derivatives_sidecar(tac_save_folder.parent,reference=None,sources=sources)
    print(f"Extracting TACs to {tac_save_folder}")
    tacs_mean, tacs_std, tacs_n = extract_multiple_tacs(dpet_path, seg)
    for k in tacs_mean:
        save_tac(
            tac_save_folder/f"tac_{k}.csv",
                tacs_mean[k],
                tacs_std[k],
                tacs_n[k],
                dpet_json["FrameTimesStart"] if "FrameTimesStart" in dpet_json else [0]*len(tacs_mean[k]),
                dpet_json["FrameDuration"] if "FrameDuration" in dpet_json else [0]*len(tacs_mean[k]),
            )
