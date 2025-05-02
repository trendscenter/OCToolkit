import argparse
import os
import json
import datetime
import io
from pathlib import Path

import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import generate_uid, ExplicitVRLittleEndian
from PIL import Image
from pydicom.uid import SecondaryCaptureImageStorage

from oct_converter.readers import E2E
from oct_converter.dicom import create_dicom_from_oct

def write_dataset(ds: FileDataset, out_path: Path):
    ds.save_as(str(out_path))
    print(f"✅ Saved: {out_path.name}")

def create_fundus_dicom_from_array(arr: np.ndarray, patient_id: str, laterality: str, scan_type: str) -> FileDataset:
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID    = SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID          = ExplicitVRLittleEndian
    file_meta.ImplementationClassUID     = generate_uid()

    ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0"*128)
    ds.SOPClassUID = SecondaryCaptureImageStorage
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    ds.is_little_endian = True
    ds.is_implicit_VR  = False

    # … the rest of your tags as before …
    ds.PatientName     = patient_id
    ds.PatientID       = patient_id
    ds.Modality        = "CF"
    ds.SeriesDescription = f"{scan_type} Fundus"
    ds.ImageLaterality = laterality
    now = datetime.datetime.now()
    ds.StudyDate       = now.strftime("%Y%m%d")
    ds.StudyTime       = now.strftime("%H%M%S")
    ds.StudyInstanceUID  = generate_uid()
    ds.SeriesInstanceUID = generate_uid()
    ds.SeriesNumber      = 1
    ds.InstanceNumber    = 1
    ds.ImageType         = ["ORIGINAL","PRIMARY","PROJECTION"]

    # Image data (2D grayscale)
    ds.Rows    = arr.shape[0]
    ds.Columns = arr.shape[1]
    ds.SamplesPerPixel           = 1
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.BitsAllocated   = 16
    ds.BitsStored      = 16
    ds.HighBit         = 15
    ds.PixelRepresentation = 0
    ds.PixelData       = (arr.astype(np.uint16)).tobytes()

    return ds

def make_multiframe_dcm(slice_datasets, output_path: Path, laterality: str, scan_type: str):
    ds0 = slice_datasets[0]
    meta = ds0.file_meta

    ds = FileDataset(str(output_path), {}, file_meta=meta, preamble=b"\0"*128)
    ds.is_little_endian = True
    ds.is_implicit_VR  = False

    for tag in ("PatientName","PatientID","StudyInstanceUID","SeriesInstanceUID"):
        setattr(ds, tag, getattr(ds0, tag))
    ds.Modality        = "OCT"
    ds.SeriesDescription = f"{scan_type} Volume"
    ds.ImageLaterality = laterality
    ds.NumberOfFrames  = len(slice_datasets)
    ds.SamplesPerPixel           = ds0.SamplesPerPixel
    ds.PhotometricInterpretation = ds0.PhotometricInterpretation
    ds.Rows    = ds0.Rows
    ds.Columns = ds0.Columns
    ds.BitsAllocated   = ds0.BitsAllocated
    ds.BitsStored      = ds0.BitsStored
    ds.HighBit         = ds0.HighBit
    ds.PixelRepresentation = ds0.PixelRepresentation
    ds.PixelData = b"".join([d.PixelData for d in slice_datasets])

    ds.SOPInstanceUID = generate_uid()
    ds.SOPClassUID    = meta.MediaStorageSOPClassUID
    ds.SeriesNumber   = 1
    ds.InstanceNumber = 1
    ds.ImageType      = ["ORIGINAL","PRIMARY","VOLUME"]
    now = datetime.datetime.now()
    ds.StudyDate = now.strftime("%Y%m%d")
    ds.StudyTime = now.strftime("%H%M%S")

    ds.save_as(str(output_path))
    print(f"✅ Multi-frame saved: {output_path.name}")

def detect_scan_type(metadata: dict) -> str:
    """Return 'OCTA' if metadata suggests angiography, else 'OCT'."""
    for v in metadata.values():
        if isinstance(v, str) and ("OCTA" in v.upper() or "ANGIO" in v.upper()):
            return "OCTA"
        if isinstance(v, list):
            for x in v:
                if isinstance(x, str) and ("OCTA" in x.upper() or "ANGIO" in x.upper()):
                    return "OCTA"
    # fallback on series_description or modality
    sd = metadata.get("series_description","") or metadata.get("modality","")
    if "OCTA" in sd.upper() or "ANGIO" in sd.upper():
        return "OCTA"
    return "OCT"

def convert_e2e_to_dicom(input_file: str, output_dir: str):
    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    base = Path(input_file).stem
    up = base.upper()
    laterality = "R" if up.endswith("_OD") else "L" if up.endswith("_OS") else ""

    e2e = E2E(input_file)
    # read metadata once
    try:
        md = e2e.read_all_metadata()
    except:
        md = {}

    scan_type = detect_scan_type(md)            # OCTA vs OCT
    st_lower = scan_type.lower()                # "octa" or "oct"

    # 1) Save metadata.json
    mpath = outdir / "metadata.json"
    with open(mpath, "w") as f:
        json.dump(md, f, indent=2)
    print(f"📄 Saved metadata.json")

    # 2) Fundus: native or projection
    fundus_ok = False
    try:
        raw_f = e2e.read_fundus_image()
        imgs = raw_f if isinstance(raw_f, list) else [raw_f]
        img = imgs[0].image
        arr = np.asarray(img)
        fundus_ok = True
    except:
        try:
            vol = e2e.read_oct_volume()
            sli = vol.data if hasattr(vol,"data") else (vol if isinstance(vol,list) else [])
            if sli:
                stack = np.stack([s.astype(np.float32) for s in sli],axis=0)
                arr = np.max(stack,axis=0)
                fundus_ok = True
        except:
            pass

    if fundus_ok:
        ds_fundus = create_fundus_dicom_from_array(arr, md.get("patient_id",""), laterality, scan_type)
        fp = outdir / f"{base}_{st_lower}_fundus.dcm"
        write_dataset(ds_fundus, fp)
    else:
        print("⚠️  No fundus available")

    # 3) OCT(/OCTA) slices → per-slice DICOMs
    raw_out = create_dicom_from_oct(input_file, str(outdir))
    paths = [Path(p) for p in (raw_out if isinstance(raw_out,list) else [raw_out])]
    slice_ds = []
    for idx, p in enumerate(sorted(paths), start=1):
        ds = pydicom.dcmread(str(p))
        ds.ImageLaterality = laterality
        ds.SeriesDescription = f"{scan_type} B-scan"
        out = outdir / f"{base}_{st_lower}_bscan_{idx:03}.dcm"
        write_dataset(ds, out)
        slice_ds.append(ds)
        if p.name != out.name:
            p.unlink()

    # 4) Merge into multi-frame
    mf = outdir / f"{base}_{st_lower}_multiframe.dcm"
    make_multiframe_dcm(slice_ds, mf, laterality, scan_type)

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Convert .e2e → OCT/OCTA DICOM suite")
    p.add_argument("--input_file",  required=True, help="HEYEX .e2e file")
    p.add_argument("--output_dir",  required=True, help="Output directory")
    args = p.parse_args()

    convert_e2e_to_dicom(args.input_file, args.output_dir)
