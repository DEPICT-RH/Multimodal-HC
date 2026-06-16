#A multimodal total-body dynamic 18F-FDG PET/CT/MRI dataset of 100 healthy humans

📊 **[Data Explorer](https://hedypet.depict.dk)** | 📥 **[Get NIfTI Data](https://huggingface.co/datasets/DEPICT-RH/Multimodal-HC)** | 📥 **[Get Listmode Data](https://doi.org/10.70883/JZJH3431)** | 📄 **[Read Publication](https://doi.org/10.xxxx/xxxxxxx)**

## Overview

The Multimodal-HC dataset provides comprehensive multimodal imaging data from 100 healthy participants, stratified by age and sex to capture physiological variation across the adult lifespan. This dataset addresses the critical need for normative reference data in quantitative PET imaging research.

### Dataset Highlights ✨

**Raw Imaging Data**
- **100 healthy participants** (18-100 years, stratified by age and sex) 👥
- **Multiple PET reconstructions** (static and dynamic, with/without attenuation correction) 🔄
- **Listmode PET data** (.ptd format) for retrospective reconstruction harmonization 📊
- **Topogram and Low-dose CT** for anatomical reference and attenuation correction 🩻
- **Whole-body DIXON MRI and T1 MPRAGE** for soft tissue characterization 🧲

**Processed Derivatives**
- **Anatomical segmentations** TotalSegmentator (organs, tissue, and bodyparts), SynthSeg (brain), and nifti_dynamic (input functions) 🧩
- **Pre-extracted time-activity curves** for all organs and tissues 📈
- **Normalization constants** (SUV, SUL, Patlak Ki) ⚖️

## How to Acquire Data 📥

> **Note**: Only 80 train/validation subjects are currently available. The remaining 20 test subjects are released upon completion of the 2026 BIC-MAC Challenge held in conjuction with MICCAI.

### Pre-computed readouts 
The repository includes pre-computed quantitative measures in the `readouts/` folder. For all segmented regions we have extracted:
- Time-activity curves (TACs)
- Static SUV/SUL measurements
- Patlak Ki values for different input functions and number of frames
- Participant metadata and demographics

🌐 **Explore the data interactively**: [https://hedypet.depict.dk](https://hedypet.depict.dk)

### Full Image Data (Application Required)
Apply for complete imaging data (PET/CT/MRI) by signing up at [datacatalog.publicneuro.eu](https://datacatalog.publicneuro.eu/dataset/super/V2) and completing the Data User Agreement.

## Installation & Setup ⚙️

1. **Clone the repository:**
```bash
git clone https://github.com/depict-rh/Multimodal-HC.git
cd Multimodal-HC
```

2. **Install the package:**
```bash
uv sync
source .venv/bin/activate
#or with conda
conda env create -f environment.yml
conda activate multimodal-hc
```


3. **Set up environment variables:**
Set the required environment variables in a `.env` file or in the terminal:
```bash
DATASET_ROOT=/path/to/multimodal_hc/train
```

## Usage Examples

### Load NIfTI images
```python
import nibabel as nib
from multimodal_hc.utils import DATASET_ROOT

sub = "sub-000"
raw_root = DATASET_ROOT / sub
totalsegmentator_root = DATASET_ROOT / "derivatives/totalsegmentator" / sub

# Load images
pet_raw = nib.load(next(raw_root.glob("**/*acstatPSF*.nii.gz")))
ct_raw = nib.load(next(raw_root.glob("**/*br38f_ct.nii.gz")))
seg_total = nib.load(next(totalsegmentator_root.glob("**/*br38f*seg-total*.nii.gz")))
```

### Analyze pre-computed readouts
```python
import pandas as pd
from multimodal_hc.utils import DATASET_ROOT

df = pd.read_pickle(DATASET_ROOT/'derivatives/readouts/means.csv')
metadata = pd.read_csv(DATASET_ROOT/'derivatives/readouts/metadata.csv')

# Merge with metadata and calculate SUV
df = df.merge(metadata[['Subject', 'SUV Denominator [Bq/mL]']], on='Subject')
df['SUV Mean'] = df['PET Mean [Bq/mL]'] / df['SUV Denominator [Bq/mL]']

# Filter for non-eroded data and calculate mean SUV by organ
organ_means = df[df["Erosion Iterations"] == 0].groupby('Label Name')['SUV Mean'].mean()
print(f"Top 5 organs by SUV:\n{organ_means.sort_values(ascending=False).head()}")
```

**Output:**
```
Top 5 organs by SUV:
seg_region_name
urinary_bladder              27.772495
ctx-lh-transversetemporal    10.941400
ctx-rh-transversetemporal    10.897202
ctx-lh-precuneus              9.888452
Right-Putamen                 9.848088
```

## Data Processing Pipeline 🔧

See `src/scripts` for reproducibility of readouts, normalization constants, and image-derived input functions.

## Reconstruction Reproducibility 🔧

E7 reconstruction parameter files are provided in the `reconstructions/` folder to enable reproduction of the clinical reconstructions from listmode data.

## Citation 📝

If you use this dataset, please cite:

```bibtex
@article{hinge2024multimodal-hc,
  title={....},
  author={....},
  journal={Scientific Data},
  year={2025},
  publisher={Nature},
  doi={10.xxxx/xxxxxxx}
}
```

## Data Notes
- The dynamic acquisition of sub-017 was reconstructed using E7 instead of scanner software (see `reconstructions/` folder for E7 parameters)
- Raw data and head reconstructions for subject sub-098 were lost
- TOPOGRAM for subject sub-084 was lost

## Acknowledgments

We thank Siemens Healthineers for funding, the Danish Blood Donor Study for recruitment, and all participants who contributed to this research. Special thanks to the teams at Rigshospitalet for data acquisition and technical support.
