# E7 Reconstruction Parameters

This folder contains E7 reconstruction parameter files to reproduce the clinical reconstructions from the multimodal_hc dataset.

## Files

- **`acdynPSF.txt`** - E7 parameters for the dynamic PSF+TOF reconstruction (acdynPSF)
  - 4 iterations, 5 subsets
  - 69 time frames (2s×20, 5s×10, 10s×15, 60s×6, 120s×10, 300s×8)
  - 440×440 matrix, no post-filtering
  - Matches the clinical acdynPSF reconstruction used throughout the dataset

## Usage

These parameter files can be used with Siemens E7 reconstruction software to process listmode data (.ptd files) with identical settings to the original dataset reconstructions.

> **Note**: Subject sub-017's acdynPSF image was reconstructed using E7 instead of the scanner's clinical software. 