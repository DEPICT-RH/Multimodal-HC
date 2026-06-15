#%%
from hedypet.preprocessing.registration import register_rigid_ants
from hedypet.preprocessing.resampling import resample_series
from hedypet.preprocessing.utils import get_head_center, get_voxmap_around_centerpoint, save_numpy_array
from hedypet.utils import get_train_subjects
from tqdm import tqdm
import numpy as np
import tempfile 
from pathlib import Path


def main(sub, dataset_root):

    derivatives_root = dataset_root / "derivatives"

    sub_root = dataset_root / sub

    registration_matrix = derivatives_root / f"registration_matrices2/{sub}/mr2petct_head.txt"

    if not registration_matrix.exists():

        totalseg = next(derivatives_root.glob(f"totalsegmentator/{sub}/**/*br38f*total*dseg.nii.gz"))

        # Create target voxmap centered around brain
        center_head_arr = get_head_center(totalseg)
        target = get_voxmap_around_centerpoint(center_head_arr,1, (179,230,205))

        #Crop CT to head region and 
        ct = next(sub_root.glob("ses-quadra/ct/*br38f_ct.nii.gz"))
        mr = next(sub_root.glob("ses-vida/anat/*MPRAGE*_T1w.nii.gz"))
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_cropped_ct = Path(temp_dir) / "tmp.nii.gz"
            resample_series(
                ct,
                target,
                tmp_cropped_ct,
                cval=-1024,
                order=3,
                mode= "constant",
            )
            aff = register_rigid_ants(moving_path=mr,fixed_path=tmp_cropped_ct)

        save_numpy_array(aff,registration_matrix)

if __name__ == "__main__":
    from hedypet.utils import DATASET_ROOT
    from multiprocessing import Pool
    
    subs = get_train_subjects()
    
    def worker(sub):
        return main(sub,DATASET_ROOT)
    
    with Pool(1) as pool:
        list(tqdm(pool.imap(worker, subs), total=len(subs)))