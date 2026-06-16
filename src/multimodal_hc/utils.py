from pathlib import Path
from dotenv import load_dotenv
import os 
import json
import numpy as np
import pandas as pd

load_dotenv()

DATASET_ROOT = Path(os.environ["DATASET_ROOT"])




def get_train_subjects():
    return  [
        "sub-000", "sub-001", "sub-002", "sub-004", "sub-005", "sub-006", "sub-008", "sub-009", 
        "sub-010", "sub-013", "sub-014", "sub-015", "sub-018", "sub-019", "sub-020", "sub-021", 
        "sub-022", "sub-024", "sub-025", "sub-026", "sub-027", "sub-028", "sub-029", "sub-030", 
        "sub-032", "sub-034", "sub-036", "sub-038", "sub-039", "sub-040", "sub-042", "sub-043", 
        "sub-044", "sub-047", "sub-048", "sub-049", "sub-050", "sub-051", "sub-052", "sub-054", 
        "sub-055", "sub-056", "sub-057", "sub-058", "sub-059", "sub-060", "sub-062", "sub-063", 
        "sub-065", "sub-066", "sub-067", "sub-068", "sub-069", "sub-070", "sub-071", "sub-072", 
        "sub-073", "sub-074", "sub-075", "sub-076", "sub-077", "sub-078", "sub-080", "sub-081", 
        "sub-082", "sub-083", "sub-084", "sub-085", "sub-086", "sub-087", "sub-088", "sub-089",
        "sub-090", "sub-091", "sub-092", "sub-093", "sub-094", "sub-095", "sub-096", "sub-098"
    ]


def get_train_subjects():
    return  [
        "sub-000", "sub-001"
    ]
    
def get_test_subjects():
    return [ 
        "sub-061", "sub-035", "sub-097", "sub-045", "sub-017", "sub-007", "sub-003", "sub-031",
        "sub-037", "sub-016", "sub-064", "sub-041", "sub-011", "sub-012", "sub-079", "sub-033",
        "sub-046", "sub-053", "sub-023", "sub-099"
    ]

def load_sidecar(image_path):
    with open(str(image_path).replace(".nii.gz",".json"),"r") as handle:
        return json.load(handle)
    
def get_time_frames_midpoint(sub):
    dpet_path = next((DATASET_ROOT / sub).glob("ses-quadra/pet/*acdyn*_pet.nii.gz"))
    sidecar = load_sidecar(dpet_path)
    frame_time_start = np.array(sidecar['FrameTimesStart'])
    frame_time_duration = np.array(sidecar["FrameDuration"])
    return frame_time_start + frame_time_duration/2

def get_participant_metadata(sub):
    df = pd.read_csv(DATASET_ROOT / "participants.tsv",sep="\t")
    row = df[df.participant_id == sub].iloc[0].to_dict()
    row["InjectedRadioactivity"] = load_sidecar(next((DATASET_ROOT / sub).glob("ses-quadra/pet/*acstat*_pet.nii.gz")))["InjectedRadioactivity"]
    return row

def get_norm_consts(sub):
    norm_consts = {}
    for p in (DATASET_ROOT / "derivatives/pet_norm_consts").glob(f"{sub}/*.txt"):
        with open(p,"r") as handle:
            norm_consts[p.stem] = float(handle.read())
    return norm_consts
