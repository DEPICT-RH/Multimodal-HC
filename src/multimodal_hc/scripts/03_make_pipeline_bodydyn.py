from multimodal_hc.utils import get_train_subjects
from tqdm import tqdm
from multimodal_hc.preprocessing.resampling import resample_and_save_bids

def main(sub,dataset_root):
    derivatives_root = dataset_root / "derivatives"

    default_args = {
        "pipeline_root":derivatives_root / "pipeline-bodydyn",
        "derivative_entities":"_space-individual",
        "Space": "Dynamic PET space",
        "overwrite":True
    }

    sub_dynamic_root = derivatives_root  / sub

    registration_matrix_head = derivatives_root / f"registration_matrices/{sub}/mr2petct_head.txt"

    # run make_pipeline_head and make_pipeline_bodstat to create registration_matrices
    assert registration_matrix_head.exists()

    target = next((dataset_root / sub).glob("ses-quadra/pet/*acdyn*_pet.nii.gz"))
    #Resample derivatives
    for seg in derivatives_root.glob(f"totalsegmentator/{sub}/**/ct/*.nii.gz"):
        resample_and_save_bids(seg,target,target,cval=0,order=0,**default_args)    
    
    for seg in derivatives_root.glob(f"synthseg/{sub}/**/*.nii.gz"):
        resample_and_save_bids(seg,target,target,cval=0,order=0,rigid_registration=registration_matrix_head,**default_args)
    
if __name__ == "__main__":
    from multimodal_hc.utils import DATASET_ROOT
    from concurrent.futures import ProcessPoolExecutor, as_completed

    subs = get_train_subjects()

    def worker(sub):
        return main(sub, DATASET_ROOT)

    with ProcessPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(worker, sub) for sub in subs]
        for future in tqdm(as_completed(futures), total=len(subs)):
            future.result()