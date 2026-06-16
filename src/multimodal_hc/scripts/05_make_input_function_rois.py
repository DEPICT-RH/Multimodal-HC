import os 
from nifti_dynamic.aorta_rois import extract_aorta_vois, extract_aorta_segments, average_early_pet_frames
import nibabel as nib
import numpy as np
from multimodal_hc.utils import get_train_subjects, load_sidecar,  DATASET_ROOT
from pathlib import Path
from tqdm import tqdm 
from nifti_dynamic.visualizations import plot_aorta_visualizations
from multimodal_hc.preprocessing.bids import create_derivatives_sidecar
from nibabel.processing import resample_from_to

def fix_aorta_sub_77(totalseg):
    fixed_aorta = nib.load(Path(__file__).parents[3]/"_aorta_fix/sub-077-aorta.nii.gz")
    fixed_aorta = resample_from_to(fixed_aorta,totalseg,order=0)
    return fixed_aorta.get_fdata()==1   

def main(sub, ml,px,dynamic_root):
    derivatives_root = dynamic_root / "derivatives"
    dyn_derivatives = derivatives_root / f"pipeline-bodydyn/{sub}"
    seg_derivatives = derivatives_root / f"niftidynamic/{sub}"
    dpet_path = next((dynamic_root / sub).glob("ses-quadra/pet/*acdyn*_pet.nii.gz"))
    totalseg_path = next(dyn_derivatives.glob("ses-quadra/ct/*br38f*total*_dseg.nii.gz"))
    aorta_segments_path = seg_derivatives / f"{sub}_seg-aortasegments_dseg.nii.gz"
    aorta_vois_path = seg_derivatives / f"{sub}_seg-aortavois_ml-{ml}_width-{px}_dseg.nii.gz"
    output_visualization_path =  Path(str(aorta_vois_path).replace(".nii.gz",".jpg"))
    print(output_visualization_path)
    sidecar = load_sidecar(dpet_path)
    frame_time_start = np.array(sidecar['FrameTimesStart'])


    os.makedirs(aorta_segments_path.parent,exist_ok=True)
    pet = average_early_pet_frames(dpet_path,frame_time_start,t_threshold=40)

    ## Prepare aorta mask from totalseg
    totalseg = nib.load(totalseg_path)
    aorta_mask = totalseg.get_fdata()==52
    if sub == "sub-077":
        aorta_mask = fix_aorta_sub_77(totalseg)
    aorta_mask = nib.Nifti1Image(aorta_mask.astype(np.int16),affine=totalseg.affine)

    #Extract mask
    aorta_segments = extract_aorta_segments(aorta_mask,pet)
    nib.save(aorta_segments,aorta_segments_path)
    create_derivatives_sidecar(
        aorta_segments_path, 
        reference=dpet_path,
        sources=[dpet_path,totalseg_path],
        Description="Aorta segments nifty_dynamic v0.3.1"
        )

    aorta_segments = nib.load(aorta_segments_path)
    if str(ml) == "full":
        aorta_vois = extract_aorta_vois(aorta_segments, pet, cylinder_width=px,use_full_length=True)
    else:
        aorta_vois = extract_aorta_vois(aorta_segments, pet, volume_ml=ml,cylinder_width=px)
    nib.save(aorta_vois,aorta_vois_path)

    # Create sidecars and visualization
    create_derivatives_sidecar(
        aorta_vois_path, 
        reference=dpet_path,
        sources=[dpet_path,totalseg_path],
        Description=f"Aorta vois nifti_dynamic v0.3.1, volume: {ml}ml, cylinder width: {px}pixels."
    )
    plot_aorta_visualizations(
        pet,
        aorta_segments,
        aorta_vois,
        output_visualization_path)


if __name__ == "__main__":
    subs = get_train_subjects()

if __name__ == "__main__":
    from multimodal_hc.utils import  DATASET_ROOT
    from concurrent.futures import ProcessPoolExecutor, as_completed

    subs = get_train_subjects()
    param_sets = [
        {
            "ml":"full",
            "px":3,
        },
        {
            "ml":1,
            "px":3,
        },
        {
            "ml":2,
            "px":5,
        },
    ]

    def worker(sub):
        for param in param_sets:
            main(sub,param["ml"],param["px"], DATASET_ROOT)

    with ProcessPoolExecutor(max_workers=12) as executor:
        futures = [executor.submit(worker, sub) for sub in subs]
        for future in tqdm(as_completed(futures), total=len(subs)):
            future.result()