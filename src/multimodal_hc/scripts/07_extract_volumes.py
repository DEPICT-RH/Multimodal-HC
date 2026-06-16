
import nibabel as nib
import numpy as np
from multimodal_hc.utils import get_train_subjects, DATASET_ROOT
import pandas as pd 

def get_volume_readouts_from_segmentation(segmentation_file):

    seg = nib.load(segmentation_file)
    assert seg.dataobj.dtype in [np.uint8,np.uint32,np.int32], seg.dataobj.dtype
    ml_per_vox = np.prod(seg.header.get_zooms())/1000
    ml_per_index = np.bincount(seg.get_fdata().astype(np.int16).flatten())*ml_per_vox
    ml_per_index_dict = {i:float(ml) for i,ml in zip(range(len(ml_per_index)),ml_per_index)}
    
    seg_mapping_file = str(segmentation_file).replace(".nii.gz",".tsv")
    df = pd.read_csv(seg_mapping_file,sep="\t")
    df["Volume [mL]"] = df["index"].map(ml_per_index_dict)
    df["Volume [mL]"] = df["Volume [mL]"].fillna(0.0)
    df = df.rename({"index":"Label Index","name":"Label Name"},axis=1)
    return df

def get_volume_readouts_from_subject(sub,dataset_root):
    totalsegmentator_root = (dataset_root / "derivatives/totalsegmentator") / sub
    synthseg_root = (dataset_root / "derivatives/synthseg") / sub
    dfs = []

    #DIXON segmentations
    for task in ["synthseg","synthsegparc"]:
        img_path = next((synthseg_root / "ses-vida/anat/").glob(f"*_seg-{task}_dseg.nii.gz"))
        df = get_volume_readouts_from_segmentation(img_path)
        df["Task"] = task
        df["Image"] = f"MR_MPRAGE"
        dfs.append(df)
    
    #DIXON segmentations
    for task in ["total","body","tissue"]:
        for phase in ["IN","OUT","W"]:
            img_path = next((totalsegmentator_root / "ses-vida/anat/").glob(f"*{phase}_seg-{task}_dseg.nii.gz"))
            df = get_volume_readouts_from_segmentation(img_path)
            df["Task"] = task
            df["Image"] = f"MR_DIXONbody{phase}"
            dfs.append(df)

    #CT segmentations
    for task in ["total","body","tissue"]:
        for rec in ["br38f","ac"]:
            img_path = next((totalsegmentator_root / "ses-quadra/ct/").glob(f"*{rec}_seg-{task}_dseg.nii.gz"))
            df = get_volume_readouts_from_segmentation(img_path)
            df["Task"] = task
            df["Image"] = "CT_"+rec
            dfs.append(df)

    df = pd.concat(dfs)
    return df

if __name__ == "__main__":
    from tqdm import tqdm
    from concurrent.futures import ProcessPoolExecutor, as_completed
    from pathlib import Path
    import os 

    subs = get_train_subjects()

    READOUTS_ROOT = DATASET_ROOT / ("derivatives/readouts")
    os.makedirs(READOUTS_ROOT,exist_ok=True)
    
    def worker(sub):
        df = get_volume_readouts_from_subject(sub, DATASET_ROOT)
        df["Subject"] = sub
        return df

    with ProcessPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(worker, sub) for sub in subs]
        dfs = [future.result() for future in tqdm(as_completed(futures), total=len(subs))]

    df = pd.concat(dfs)
    df.to_csv(str(READOUTS_ROOT/"volumes.csv"),index=False)