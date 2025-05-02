# OCToolkit: General OCT Acquisition & Analysis Toolkit

Welcome to **OCToolkit**, a versatile, modular toolkit for retinal OCT and OCT-A data acquisition, conversion, and analysis.

## Overview

OCToolkit provides:

* **Data Ingestion:** Support for HEYEX `.e2e` files, `.fds`, and other vendor formats
* **Conversion Modules:** Export to DICOM (slices, fundus, multi-frame volumes) and common image formats
* **Analysis Pipelines:** Segmentation, thickness mapping, layer quantification, OCT-A flow metrics
* **Visualization Tools:** Interactive B-scan viewers, en-face projections, 3D volume rendering
* **Batch Processing:** Command-line tools and scripts for large-scale studies
* **Extensibility:** Easily add new file readers, analysis modules, or export formats

## Project Structure

```
OCToolkit/
├─ README.md                # This overview
├─ conversion/              # .e2e → DICOM conversion programs
│  ├─ README.md             # Specific conversion instructions
│  └─ e2e_to_dcm.py         # Conversion script
├─ segmentation/            # OCT layer segmentation modules
├─ metrics/                 # Quantification pipelines (thickness, OCT-A flow)
├─ visualization/           # B-scan and volume viewers
└─ utils/                   # Utility functions (I/O, metadata handling)
```

## Installation

```bash
conda create -n octoolkit python=3.11 pip -y
conda activate octoolkit
pip install oct_converter pydicom numpy pillow
# add other dependencies for segmentation, visualization as needed
```

## Getting Started

1. **Convert** your raw `.e2e` scans: see `conversion/README.md`.
2. **Segment** layers: modules under `segmentation/`.
3. **Compute metrics**: scripts in `metrics/`.
4. **Visualize** results: launch tools in `visualization/`.

## Contributing

* Fork the repo and submit pull requests.
* Add new readers under `conversion/` or modules under `segmentation/`, `metrics/`, etc.
* Ensure code passes tests and includes documentation.

## License

Distributed under the MIT License.
See `LICENSE` for details.
