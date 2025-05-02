# OCToolkit: OCT Acquisition & Analysis Toolkit

A general-purpose toolkit for working with retinal OCT and OCT-A data. It provides:

* Conversion of HEYEX `.e2e` files to DICOM format (individual slices, fundus images, multi-frame volumes)
* Automatic detection of OCT versus OCT-A scans
* Metadata extraction and masking examples for privacy
* Extensible modules for acquisition and downstream analysis

## Features

1. **Metadata Extraction**
   Reads all available metadata from the `.e2e` and saves it to `metadata.json`.

2. **Fundus Handling**

   * Attempts to read the native fundus image from the `.e2e`.
   * If unavailable, generates a maximum-intensity projection from the OCT volume.
   * Saves fundus image as a standard Secondary Capture DICOM (`<base>_fundus.dcm`).

3. **Scan Type Detection**
   Scans metadata for keywords (`OCTA`, `Angio`) to classify as **OCT** or **OCT-A**, affecting filenames and DICOM tags.

4. **Per-Slice Conversion**
   Calls the `oct_converter` library to create per-slice DICOMs. Filenames follow:

   ```
   <base>_<scan_type>_bscan_001.dcm ... _bscan_NNN.dcm
   ```

   Laterality (`R` or `L`) is set in the `ImageLaterality` DICOM tag based on `_OD`/`_OS` in filename.

5. **Multi-Frame DICOM**
   Merges individual slice DICOMs into a single multi-frame volume:

   ```
   <base>_<scan_type>_multiframe.dcm
   ```

6. **Clean Output**
   All generated files are placed under a single output directory.

## Requirements

* Python 3.9–3.11
* [`oct_converter`](https://github.com/marksgraham/OCT-Converter)
* `pydicom`
* `numpy`
* `Pillow`

Install dependencies via Conda (recommended):

```bash
conda create -n oct2dcm python=3.11 pip -y
conda activate oct2dcm
pip install oct_converter pydicom numpy pillow
```

## Usage

```bash
python e2e_to_dcm.py \
  --input_file path/to/SUBJ001_OD.E2E \
  --output_dir /path/to/output_dir
```

### Output Directory Structure

* `metadata.json`
* `<base>_<scan_type>_fundus.dcm`
* `<base>_<scan_type>_bscan_001.dcm` ...
* `<base>_<scan_type>_multiframe.dcm`

Where `<scan_type>` is `oct` or `octa`.

## Example

```bash
python e2e_to_dcm.py \
  --input_file /data/SUBJ001_OS.E2E \
  --output_dir ./dicom_output
```

Generates:

```
dicom_output/metadata.json
dicom_output/SUBJ001_OS_oct_fundus.dcm
dicom_output/SUBJ001_OS_oct_bscan_001.dcm
...
dicom_output/SUBJ001_OS_oct_multiframe.dcm
```

## License

MIT License
