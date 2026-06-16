## Segmentations and defacing
TotalSegmentator and SynthSeg segmentations were derived before defacing. Original image files and segmentations (including face_mask intermediates) are not provided due to privacy concerns. The BIDS sidecars of each segmentation file details the tool version and arguments used to generate the segmentation.

The preprocessing steps before `01_register_brain_mri.py` are summarized below:

Steps:
- TotalSegmentator v2.5.0 was run on CT (ac and br38f) and DIXONbody{IN/OUT/W} for tasks total, tissues, and body
- SynthSeg vXXX was run on MPRAGE and resampled to the MPRAGE using nearest neighbour interpolation
- TotalSegmentator v2.5.0 task face was run on the ac CT and MPRAGE MRI
- face masks were pixelated in 10mm blocks, and resampled to all other images using MPRAGE face_mask for MRI acquistions and CT facemask for PET and CT acquisitions. 
- face masks were applied to the images and segmentations

The scripts in this directory:
- The aorta VOI segmentations
- All files under readouts

