import nibabel as nib
import numpy as np
from multimodal_hc.utils import get_train_subjects, DATASET_ROOT
from multimodal_hc.preprocessing.tacs import extract_and_save_tac
from parse import parse

def main(sub, dataset_root, rec="acstatPSF", erosions=[0,1]):
    """Organ mean extraction for PET reconstrunctions"""

    if rec == "acstatPSF":
        derivatives = dataset_root / f"derivatives/pipeline-bodystat/{sub}"
        pet_path = next((dataset_root / sub).glob(f"ses-quadra/pet/*rec-{rec}_pet.nii.gz"))
        pipeline_root = dataset_root / f"derivatives/tacs"

    elif rec =="acdynPSF":
        derivatives = dataset_root / f"derivatives/pipeline-bodydyn/{sub}"
        pet_path = next((dataset_root / sub).glob("ses-quadra/pet/*acdyn*_pet.nii.gz"))
        pipeline_root = dataset_root / f"derivatives/tacs"
        
    elif rec == "acstatOSEMhead":
        derivatives = dataset_root / f"derivatives/pipeline-head1mm/{sub}"
        pet_path = next((dataset_root / sub).glob(f"ses-quadra/pet/*rec-{rec}_pet.nii.gz"))
        pipeline_root = dataset_root / f"derivatives/tacs"
    else:
        raise Exception("Unsupported reconstruction")
    
    #Aorta derivatives are ignored for non-dynamic acquisitions
    derivatives_aorta_sub = dataset_root / f"derivatives/niftidynamic/{sub}"

    for erosion in erosions:
        
        # Totalseg total
        totalseg_organs_tacs_path = (pipeline_root / sub) / f"{rec}/ts_total/erosion-{erosion}"
        if not totalseg_organs_tacs_path.exists() and rec in ["acstatPSF","acdynPSF"]:
            totalseg_path = next(derivatives.glob("ses-quadra/ct/*rec-br38f_seg-total*_dseg.nii.gz"))
            extract_and_save_tac(pet_path, totalseg_path,totalseg_organs_tacs_path,erosion)

        #Synthseg
        synthseg_tacs_path = (pipeline_root / sub) / f"{rec}/synthseg/erosion-{erosion}"
        if not synthseg_tacs_path.exists():
            synthseg_path = next(derivatives.glob("ses-vida/anat/*synthseg_*dseg.nii.gz"))
            extract_and_save_tac(pet_path, synthseg_path,synthseg_tacs_path,erosion)

        #Synthseg parc
        synthsegparc_tacs_path = (pipeline_root / sub) / f"{rec}/synthsegparc/erosion-{erosion}"
        if not synthsegparc_tacs_path.exists():
            synthsegparc_path = next(derivatives.glob("ses-vida/anat/*synthsegparc_*dseg.nii.gz"))
            extract_and_save_tac(pet_path, synthsegparc_path,synthsegparc_tacs_path,erosion)

        # Totalseg tissue
        tissue_tacs_path = (pipeline_root / sub) / f"{rec}/ts_tissue/erosion-{erosion}"
        if not tissue_tacs_path.exists() and rec in ["acstatPSF","acdynPSF"]:
            tissue_path = next(derivatives.glob("ses-quadra/ct/*rec-br38f_seg-tissue*_dseg.nii.gz"))
            extract_and_save_tac(pet_path,tissue_path,tissue_tacs_path,erosion)
        
        # Totalseg body
        body_tacs_path = (pipeline_root / sub) / f"{rec}/ts_body/erosion-{erosion}"
        if not body_tacs_path.exists():
            body_path = next(derivatives.glob("ses-quadra/ct/*rec-br38f_seg-body*_dseg.nii.gz"))
            extract_and_save_tac(pet_path,body_path,body_tacs_path,erosion)

        # Aorta segments (only for dynamic acquisition)
        aortasegments_tacs_path = (pipeline_root / sub) / f"{rec}/aortasegments/erosion-{erosion}"
        if not aortasegments_tacs_path.exists() and rec == "acdynPSF":
            aortasegments_path = next((derivatives_aorta_sub).glob("*aortasegments*.nii.gz"))
            extract_and_save_tac(pet_path,aortasegments_path,aortasegments_tacs_path,erosion)
    
    # Aorta VOIS (only for dynamic acquisition)
    for aortvois_path in (derivatives_aorta_sub).glob("*aortavois*.nii.gz"):
        voi_name = parse("{}seg-{voi_name}_dseg.nii.gz", aortvois_path.name).named["voi_name"]
        aortavois_tacs_path = (pipeline_root / sub) / f"{rec}/{voi_name}/erosion-0"
        if not aortavois_tacs_path.exists() and rec == "acdynPSF":
            extract_and_save_tac(pet_path,aortvois_path,aortavois_tacs_path,erosion=0)

    # Whole body
    whole_image_tacs_path = (pipeline_root / sub) / f"{rec}/totalimage/erosion-0"
    if not whole_image_tacs_path.exists():
        seg = nib.load(totalseg_path).get_fdata()
        seg = np.ones_like(seg,dtype="bool")
        extract_and_save_tac(pet_path,seg,whole_image_tacs_path,erosion=0)

if __name__ == "__main__":
    from tqdm import tqdm
    from concurrent.futures import ProcessPoolExecutor, as_completed

    subs = get_train_subjects()

    def worker(sub):
        for rec in ["acstatPSF","acdynPSF"]:
            main(sub,dataset_root=DATASET_ROOT,rec=rec)

    for sub in subs:
        worker(sub)

    with ProcessPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(worker, sub) for sub in subs]
        for future in tqdm(as_completed(futures), total=len(subs)):
            future.result()

