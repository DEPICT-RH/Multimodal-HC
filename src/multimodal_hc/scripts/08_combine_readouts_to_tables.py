# %% [markdown]
# ## Means, TACS, and metadata
# Extensive metadata and original image files available at X

# %%
from multimodal_hc.utils import DATASET_ROOT, get_train_subjects, get_time_frames_midpoint
from multimodal_hc.utils import get_participant_metadata, get_norm_consts
from nifti_dynamic.tacs import load_tac
from nifti_dynamic.patlak import roi_patlak
from parse import parse
from tqdm import tqdm
import pandas as pd 
import os 
import json
import warnings
import numpy as np 


READOUTS_ROOT = DATASET_ROOT / "derivatives/readouts"
os.makedirs(READOUTS_ROOT,exist_ok=True)

def load_tsv(file_path):
    df = pd.read_csv(file_path,sep="\t")
    return {k:v for k,v in zip(list(df["index"]),list(df.name))}

region_names = {
    'ts_total' :load_tsv(next((DATASET_ROOT / "derivatives/totalsegmentator").glob("**/ct/*total*.tsv"))),
    'ts_body' : load_tsv(next((DATASET_ROOT / "derivatives/totalsegmentator").glob("**/ct/*body*.tsv"))),
    'ts_tissue' :load_tsv(next((DATASET_ROOT / "derivatives/totalsegmentator").glob("**/ct/*tissue*.tsv"))),
    'synthsegparc' : load_tsv(next((DATASET_ROOT / "derivatives/synthseg").glob("**/*synthseg*.tsv"))),
    'synthseg' : load_tsv(next((DATASET_ROOT / "derivatives/synthseg").glob("**/*synthseg*.tsv"))),
    'totalimage' : {1:"body"},
}

region_names_aorta = {1:"aorta_ascending",
    2:"aorta_top",
    3:"aorta_descending_upper",
    4:"aorta_descending_lower"}

def task_and_ix_to_region_name(task,ix):
    ix = int(ix)
    if task.startswith("niftidynamic"):
        return region_names_aorta[ix]
    else:
        return region_names[task][ix]

subs = get_train_subjects()



df_path = READOUTS_ROOT/"metadata.csv"
data = []
for sub in subs:
    x = get_participant_metadata(sub)
    x["SUV Denominator [Bq/mL]"] = get_norm_consts(sub)["suv"]
    x["SUL Decazes Denominator [Bq/mL]"] = get_norm_consts(sub)["sul_decazes"]
    x["SUL Janma Denominator [Bq/mL]"] = get_norm_consts(sub)["sul_janma"]
    x["SUL James Denominator [Bq/mL]"] = get_norm_consts(sub)["sul_james"]
    data.append(x)

df = pd.DataFrame(data)
df = df.rename({"InjectedRadioactivity":"Injected Activity [MBq]","participant_id":"Subject","weight":"Weight [kg]","demographic-group":"Demographic Group [Sex,Age]"},axis=1)
df = df.drop(["age","height","sex","blanket"],axis=1)
df.to_csv(df_path,index=False)

print("="*10 + "[Metadata Dataframe]" + "="*10,end="\n\n")
print("Columns:", list(df.columns),end="\n\n")
print("Subjects:", df["Subject"].nunique(),end="\n\n")
print(df["Demographic Group [Sex,Age]"].value_counts(),end="\n\n")


df_path = READOUTS_ROOT / "tacs.csv"
df_path_input_function = READOUTS_ROOT / "input_functions.csv"


data = []

for sub in tqdm(subs):
    tacs_root = (DATASET_ROOT / f"derivatives/tacs/{sub}/acdynPSF")
    tacs = list(tacs_root.glob("**/tac*"))

    # Load the TAC for each ROI with/without erosion
    for tac_roi_path in tacs:

        frame_time_start, frame_duration,mu_organ, std_organ, n_organ = load_tac(tac_roi_path)
        if (frame_duration==0).all():
            frame_duration = np.array(list(frame_time_start[1:]) + [4200]) - frame_time_start

        frame_time_middle = frame_time_start+frame_duration/2
        # Save data to dataframe
        frame_ixs = list(range(len(mu_organ)))            
        tags = parse('{}/tacs/{sub}/acdynPSF/{task}/erosion-{erosion}/tac_{ix}.csv',str(tac_roi_path)).named
        vals = {"PET Mean [Bq/mL]":mu_organ,"PET STD [Bq/mL]":std_organ,"Voxel Count":n_organ,"Frame Index":frame_ixs, "Frame Time Middle [s]":frame_time_middle}
        vals.update(tags)
        vals["Label Name"] = task_and_ix_to_region_name(vals["task"],vals["ix"])
        data.append(pd.DataFrame(vals))

# Rename and save 
df = pd.concat(data)
df = df.rename({"sub":"Subject","task":"Task","ix":"Label Index","erosion":"Erosion Iterations"},axis="columns")
df["Volume [mL]"] = df["Voxel Count"]*(1.65*1.65* 1.65) / 1000
df["Erosion Iterations"] = df["Erosion Iterations"].astype(int)
df = df[['Subject', 'Task','Label Index', 'Label Name', 'Erosion Iterations', 'Frame Index', 'Frame Time Middle [s]', 'PET Mean [Bq/mL]', 'PET STD [Bq/mL]', 'Voxel Count',  'Volume [mL]']]

df_input_functions = df[df.Task.str.startswith("aortavois")]
df_organs = df[~df.Task.str.startswith("aortavois")]
df_input_functions.to_csv(df_path_input_function)
df_organs.to_csv(df_path)


print("="*10 + "[Time Activity Curves Dataframe]" + "="*10,end="\n\n")
print("Columns:", list(df.columns),end="\n\n")
print("Segmentation tasks:", list(df["Task"].unique()),end="\n\n")
print("N Unique regions:", df["Label Name"].nunique(), end="\n\n")
print("Unique erosions:", df["Erosion Iterations"].unique(),end="\n\n")
print("Rows:",len(df),end="\n\n\n")

print("="*10 + "[Input Functions Time Activity Curves Dataframe]" + "="*10,end="\n\n")
print("Columns:", list(df_input_functions.columns),end="\n\n")
print("Segmentation tasks:", list(df_input_functions["Task"].unique()),end="\n\n")
print("N Unique regions:", df_input_functions["Label Name"].nunique(), end="\n\n")
print("Unique erosions:", df_input_functions["Erosion Iterations"].unique(),end="\n\n")
print("Rows:",len(df_input_functions))


df_path = READOUTS_ROOT/"means.csv"
data = []

for sub in tqdm(subs):
    tacs_root = (DATASET_ROOT / f"derivatives/tacs/{sub}/acstatPSF")

    tacs = list(tacs_root.glob("**/tac*"))
            
    # Load the ROI means for all regions (with/without eerosion)
    for tac_roi_path in tacs:
        _,_,mu_organ, std_organ, n_organ = load_tac(tac_roi_path)

        # Save data to dataframe
        tags = parse('{}/tacs/{sub}/acstatPSF/{task}/erosion-{erosion}/tac_{ix}.csv',str(tac_roi_path)).named
        vals = {"PET Mean [Bq/mL]":float(mu_organ.item()),"PET STD [Bq/mL]":float(std_organ.item()),"Voxel Count":int(n_organ.item())}
        vals.update(tags)
        vals["Label Name"] = task_and_ix_to_region_name(vals["task"],vals["ix"])
        data.append(vals)

# Rename and save 
df = pd.DataFrame(data)
df = df.rename({"sub":"Subject","task":"Task","ix":"Label Index","erosion":"Erosion Iterations"},axis="columns")
df["Volume [mL]"] = df["Voxel Count"]*(1.65*1.65* 2.0) / 1000
df["Erosion Iterations"] = df["Erosion Iterations"].astype(int)
df = df[['Subject', 'Task','Label Index', 'Label Name', 'Erosion Iterations', 'PET Mean [Bq/mL]', 'PET STD [Bq/mL]', 'Voxel Count', 'Volume [mL]']]
df.to_csv(df_path)

print("="*10 + "[Means Dataframe]" + "="*10,end="\n\n")
print("Columns:", list(df.columns),end="\n\n")
print("Segmentation tasks:", list(df["Task"].unique()),end="\n\n")
print("N Unique regions:", df["Label Name"].nunique(), end="\n\n")
print("Unique erosions:", df["Erosion Iterations"].unique(),end="\n\n")
print("Rows:",len(df))

warnings.filterwarnings("ignore")

df_path = READOUTS_ROOT/"patlak_ki.csv"

#Number of last frames to perform Patlak regression on
frames = [2,3,4,5,6,7,8]
ki_data = []

for sub in tqdm(subs):

    #Find all TACs (organs, input functions, and with/without erosion)
    tacs_root = (DATASET_ROOT / f"derivatives/tacs/{sub}/acdynPSF")
    tacs = list(tacs_root.glob("**/tac*"))

    #Divide into input function TACs and ROI tacs
    tacs_if = [x for x in tacs if "aortavois" in str(x)]
    tacs_roi = [x for x in tacs if "aorta" not in str(x)]
    
    # For each input function
    for tac_if_path in tacs_if:
        frame_time_start, frame_duration,tac_if, _, _ = load_tac(tac_if_path)
        if (frame_duration==0).all():
            frame_duration = np.array(list(frame_time_start[1:]) + [4200]) - frame_time_start

        t_middle = frame_time_start+frame_duration/2
        # For each organ
        for tac_roi_path in tacs_roi:
            _,_, tac_organ, _, n = load_tac(tac_roi_path)
        
            # For different number of regression Frames
            for frame in frames:

                # Run Patlak analysis
                slope, intercept, X, Y = roi_patlak(tac_organ,tac_if,t_middle,frame)

                # And parse the data for the dataframe
                tags_if = parse('{}/tacs/{}/acdynPSF/{task}/erosion-{erosion}/tac_{ix}.csv',str(tac_if_path)).named
                tags_organ = parse('{}/tacs/{sub}/acdynPSF/{task}/erosion-{erosion}/tac_{ix}.csv',str(tac_roi_path)).named
                if_tag = tags_if["task"]+"_"+task_and_ix_to_region_name(tags_if["task"], tags_if["ix"])
                series = {"Patlak Ki":float(slope),"Voxel Count":int(n[0]),"Regression Frames":frame}
                series["Input Function Identifier"] = if_tag
                series.update(tags_organ)
                series["Label Name"] = task_and_ix_to_region_name(series["task"], series["ix"])
                
                ki_data.append(series)
                
# Rename and save 
df = pd.DataFrame(ki_data)
df = df.rename({"sub":"Subject","task":"Task","ix":"Label Index","erosion":"Erosion Iterations"},axis="columns")
df["Volume [mL]"] = df["Voxel Count"]*(1.65*1.65* 1.65) / 1000
df["Erosion Iterations"] = df["Erosion Iterations"].astype(int)
df = df[['Subject','Task',  'Label Index', 'Label Name', 'Erosion Iterations', 'Input Function Identifier', 'Regression Frames', 'Patlak Ki', 'Voxel Count', 'Volume [mL]']]
df.to_csv(df_path)

print("="*10 + "[Patlak Dataframe]" + "="*10,end="\n\n")
print("Columns:", list(df.columns),end="\n\n")
print("Segmentation tasks:", list(df["Task"].unique()),end="\n\n")
print("N Unique regions:", df["Label Name"].nunique(), end="\n\n")
print("Unique erosions:", df["Erosion Iterations"].unique(),end="\n\n")
print("Unique patlak frames:", df["Regression Frames"].unique(),end="\n\n")
print("Unique input functions" , df["Input Function Identifier"].unique(),end="\n\n")
print("Rows:",len(df))