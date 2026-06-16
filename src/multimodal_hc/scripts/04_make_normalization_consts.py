import nibabel as nib
from multimodal_hc.utils import get_train_subjects
from tqdm import tqdm
from multimodal_hc.preprocessing.normalization import *
from multimodal_hc.utils import *
from multimodal_hc.preprocessing.utils import *
from multimodal_hc.preprocessing.bids import *
import pandas as pd 
import os 

def main(sub,static_root):
    
    sub_root = static_root / sub
    derivatives_root = static_root / "derivatives"
    pipeline_root= derivatives_root / "pet_norm_consts"
    
    pet_path = next(sub_root.glob("ses-quadra/pet/*acstatPSF_pet.nii.gz"))
    ts_total_path = next(derivatives_root.glob(f"totalsegmentator/{sub}/**/*br38f*total*.nii.gz"))
    ts_tissue_path = next(derivatives_root.glob(f"totalsegmentator/{sub}/**/*br38f*tissue*.nii.gz"))
    
    ts_total_nii = nib.load(ts_total_path)
    ts_tissue_nii = nib.load(ts_tissue_path)
    
    metadata = get_participant_metadata(sub)
    weight = metadata["weight"]
    dose = metadata["InjectedRadioactivity"]*1e6 
    sex = metadata["sex"]
    height = metadata["height"]
    
    if not (save_path:=((pipeline_root/sub) / "suv.txt")).exists():
        const = SUV(injected_dose=dose,patient_weight=weight)
        save_constant_bids(const,save_path,description="Body weight SUV",sources=[pet_path])
    
    if not (save_path:=((pipeline_root/sub) / "sul_janma.txt")).exists():
        const = SUL_janma(injected_dose=dose,patient_weight=weight,patient_height=height,patient_sex=sex)
        save_constant_bids(const,save_path,description="Lean body mass normalized SUV (SUL) using the Janmahasatian LBM formula https://doi.org/10.2165/00003088-200544100-00004",sources=[pet_path])
    
    if not (save_path:=((pipeline_root/sub) / "sul_james.txt")).exists():
        const = SUL_james(injected_dose=dose,patient_weight=weight,patient_height=height,patient_sex=sex)
        save_constant_bids(const,save_path,description="Lean body mass normalized SUV (SUL) using James LBM formula https://doi.org/10.2967/jnumed.113.136986",sources=[pet_path])
    
    if not (save_path:=((pipeline_root/sub) / "sul_decazes.txt")).exists():
        const = SUL_decazes(injected_dose=dose,patient_weight=weight,ts_total_nii=ts_total_nii,ts_tissue_nii=ts_tissue_nii)
        save_constant_bids(const,save_path,description="Lean body mass normalized SUV (SUL) using CT and VI equation from Decazes et al. 2016",sources=[pet_path,ts_total_path,ts_tissue_path])
    
    
def add_constants_to_participants_tsv(sub,dataset_root):
    derivatives_root = dataset_root / "derivatives"
    pipeline_root= derivatives_root / "pet_norm_consts"
    pipeline_root= derivatives_root / "pet_norm_consts"
    rows = []

    for sub in subs:
        row = {"participant_id":sub}
        for const_file in (pipeline_root/sub).glob("*.txt"):
            const_name = os.path.basename(const_file).replace(".txt","")
            with open(const_file,"r") as handle:
                row[const_name+"_const"] = float(handle.read())
                
        rows.append(row)
    df_consts = pd.DataFrame(rows)
    df_particpants = pd.read_csv(dataset_root/"participants.tsv",sep="\t")
    df_particpants = pd.merge(df_particpants,df_consts,on="participant_id",how="left",suffixes=("_left",""))
    df_particpants = df_particpants.drop(columns=[c for c in df_particpants.columns if c.endswith("_left")])
    df_particpants.to_csv(dataset_root/"participants.tsv",sep="\t",index=False)

if __name__ == "__main__":
    from multimodal_hc.utils import DATASET_ROOT
    
    subs = get_train_subjects()
    for sub in tqdm(subs):
        main(sub,DATASET_ROOT)

    add_constants_to_participants_tsv(subs,DATASET_ROOT)
