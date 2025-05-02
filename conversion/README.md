# Conversion Module: HEYEX `.e2e` → DICOM

This conversion script transforms HEYEX `.e2e` files into standard DICOM format, producing:

* **Per-slice B-scans** (`<base>_<scan>_bscan_XXX.dcm`)
* **Fundus images** (`<base>_<scan>_fundus.dcm`) (native or projected)
* **Multi-frame volumes** (`<base>_<scan>_multiframe.dcm`)

It also:

* **Detects** OCT vs. OCT-Angiography (OCT-A) scans
* **Embeds** patient laterality (OD=R, OS=L) from filename
* **Extracts** and saves metadata (`metadata.json`)

## Usage

```bash
python e2e_to_dcm.py \
  --input_file path/to/SUBJ001_OD.E2E \
  --output_dir path/to/dicom_output
```

### Output Files

* `metadata.json`
* `<base>_oct[_angiography]_fundus.dcm`
* `<base>_oct[_angiography]_bscan_001.dcm` ...
* `<base>_oct[_angiography]_multiframe.dcm`

Replace `oct` with `octa` if OCT-A is detected.

## Dependencies

* `oct_converter`
* `pydicom`
* `numpy`
* `Pillow`

Install via:

```bash
pip install oct_converter pydicom numpy pillow
```

## Script Details

* **Input:** HEYEX `.e2e` file
* **Output:** DICOM files in a single directory
* **Laterality:** Parsed from `_OD`/\_`OS` suffix in filename
* **Scan Type:** Determined by metadata keywords (`OCTA`, `Angio`)

```bash
# Example
python e2e_to_dcm.py \
  --input_file /data/SUBJ001_OS.E2E \
  --output_dir ./dicom_output
```

Generates:

```
dicom_output/
├─ metadata.json
├─ SUBJ001_OS_oct_fundus.dcm
├─ SUBJ001_OS_oct_bscan_001.dcm
└─ SUBJ001_OS_oct_multiframe.dcm
```
