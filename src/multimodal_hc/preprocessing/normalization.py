import numpy as np

def lbm_james(patient_weight, patient_height, patient_sex):
    if patient_sex == "F":
        LBM = 1.07*patient_weight-148*(patient_weight/(patient_height*100))**2
    elif patient_sex == "M":
        LBM = 1.10*patient_weight-128*(patient_weight/(patient_height*100))**2
    else:
        raise Exception()
    return LBM

def lbm_janma(patient_weight, patient_height, patient_sex): 
    if patient_sex == "F":
        LBM = 9.27*10**3*patient_weight/(8.78*10**3+244*(patient_weight/patient_height**2))
    elif patient_sex == "M":
        LBM = 9.27*10**3*patient_weight/(6.68*10**3+216*(patient_weight/patient_height**2))
    else:
        raise Exception()
    return LBM

def lbm_ct_decazes(patient_weight, ts_total_nii, ts_tissue_nii):

    totalseg_img =ts_total_nii.get_fdata() 

    # https://jnm.snmjournals.org/content/jnumed/57/5/753.full.pdf

    ## Cannot use V20: Vertex to Ischia-20cm due to FOV limit
    ## We use VI: Vertex to Ischia
    _,_,zs = np.where(np.isin(totalseg_img,[77,78]))
    ischia_bottom = np.min(zs)
    _,_,zs = np.where(np.isin(totalseg_img,[91]))
    cervex = np.max(zs)
    ml_per_vox = np.prod(ts_tissue_nii.header.get_zooms()) / 1000
    counts = np.bincount(np.asanyarray(ts_tissue_nii.dataobj)[...,ischia_bottom:cervex+1].flatten())

    subcutaneous_fat = float(counts[1]*ml_per_vox)
    torso_fat = float(counts[2]*ml_per_vox)

    density_fat = 0.923
    fbm_VI_inside = (subcutaneous_fat+torso_fat)*density_fat / 1000 #to kg
    lbm_VI = patient_weight - (fbm_VI_inside / 0.716) 
    return lbm_VI

def SUV(injected_dose, patient_weight):
    suv = (injected_dose / (patient_weight*1000))
    return  suv

def SUL_james(injected_dose, patient_weight, patient_height, patient_sex):
    lbm = lbm_james(patient_weight, patient_height, patient_sex)
    return injected_dose / (lbm*1000)

def SUL_janma(injected_dose, patient_weight, patient_height, patient_sex):
    lbm = lbm_janma(patient_weight, patient_height, patient_sex)
    return injected_dose / (lbm*1000)

def SUL_decazes(injected_dose, patient_weight, ts_total_nii,ts_tissue_nii):
    lbm = lbm_ct_decazes(patient_weight, ts_total_nii,ts_tissue_nii)
    return injected_dose / (lbm*1000)

