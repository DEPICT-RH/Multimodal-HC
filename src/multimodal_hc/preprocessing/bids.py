
import json
import os
import re

def save_constant_bids(constant, save_path,description,sources):
    os.makedirs(save_path.parent,exist_ok=True)
    with open(save_path,"w") as handle:
        handle.write(str(constant))

    create_derivatives_sidecar(save_path, None ,sources,Description=description)

def path_to_bids_uri(image_path):
    dataset_root , sub,  relative_path = re.split("/(sub-.{3})/",str(image_path))
    dataset_name = os.path.basename(dataset_root)
    return f"bids:{dataset_name}:{sub}/{relative_path}"



def make_derivative_name(img_path,pipeline_root,derivative_entities,suffix=None):
    _ , sub,  relative_path = re.split("/(sub-.{3})/",str(img_path))
    source, _suffix,_ = re.split("(_[^_]*\.nii\.gz)", relative_path)
    if suffix is None:
        suffix=_suffix
    out_path = (pipeline_root / sub) / (source + derivative_entities +suffix)
    return out_path

def create_derivatives_sidecar(image_path,reference, sources=[],**kwargs):
    if str(image_path).endswith(".nii.gz"):
        outjson = str(image_path).replace(".nii.gz",".json")
    else:
        outjson = str(image_path.parent / (image_path.stem +".json"))
    sources = [path_to_bids_uri(source) for source in sources]
    try:
        ref_uri = path_to_bids_uri(reference)
    except:
        ref_uri = None
    sidecar = {
            "SpatialReference": ref_uri,
            "Sources":sources,
        }
    sidecar.update(**kwargs)
    os.makedirs(os.path.dirname(outjson),exist_ok=True)
    with open(outjson,"w") as handle:
        json.dump(sidecar,handle,sort_keys=True,indent=4)

