#%%
from hedypet.utils import get_train_subjects
from tqdm import tqdm
from hedypet.preprocessing.resampling import resample_and_save_bids

def main(sub,dataset_root):

    derivatives_root = dataset_root / "derivatives"

    default_args = {
        "pipeline_root":derivatives_root / "pipeline-bodystat",
        "derivative_entities":"_space-individual",
        "Space": "Static PET space"
    }
        
    sub_root = dataset_root / sub
    registration_matrix_head = derivatives_root / f"registration_matrices/{sub}/mr2petct_head.txt"

    assert registration_matrix_head.exists()

    target = next(sub_root.glob("ses-quadra/pet/*acstatPSF_pet.nii.gz"))
    
    #Resample derivatives
    for seg in derivatives_root.glob(f"totalsegmentator/{sub}/**/ct/*.nii.gz"):
        resample_and_save_bids(seg,target,target,cval=0,order=0,**default_args)    

    for seg in derivatives_root.glob(f"synthseg/{sub}/**/*.nii.gz"):
        resample_and_save_bids(seg,target,target,cval=0,order=0,rigid_registration=registration_matrix_head,**default_args)  

if __name__ == "__main__":
    from hedypet.utils import DATASET_ROOT
    from multiprocessing import Pool
    
    subs = get_train_subjects()
    
    def worker(sub):
        return main(sub, DATASET_ROOT)
    
    with Pool(12) as pool:
        list(tqdm(pool.imap(worker, subs), total=len(subs)))
    
# %%
