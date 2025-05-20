# TACI_python_version

TACI_Python_version is a python-based 3D calcium imaging analysis pipeline used in drosophila.

---

## Table of Contents

- [Installation](#installation)
- [Description](#description)
- [File Overview](#file-overview)
- [Input and Output File Organization](#input-and-output-file-organization)
- [Usage Instructions](#usage-instructions)
  - [Generate Background](#generate-background)
  - [Individual ΔF/F₀ Calculation](#individual-Δff₀-calculation)
  - [Merging Results](#merging-results)
- [Example Directory Structures](#example-directory-structures)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Contact](#contact)

---

## Installation and python testing

1. Clone or download this repository.
2. Create a python virtrual environment.
3. Install dependencies:
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
4. Test scripts usging demo data
   ```bash
   python .\CIAanalysis_120min.py -i path/demo_analysis --merge --cell_type DOWC
   python .\CITbind_dynamic.py -i path/demo_cbind -n 2

## Description 
These python scripts allows batch processing and analysis of calcium imaging datasets collected from Drosophila larvae or other small model systems. 
The pipline has three main stages:
1. Fluorescence extraction using TrackMate in ImageJ<br>
   insert the user manual for the steps in Trackmate here!
2. Primary Analysis (CIAnalysis_120min.py)<br>
   This is the main script for the processing individual calcium imaging datasets.<br>
   It automatially: 
   **•** Generates background values from background_i.xlsx<br>
   **•** Extracts fluorescence change <br>
   &nbsp; &nbsp; &nbsp; &nbsp; **•** **DOCC**: Uses the first timepoint fluorescence as F₀<br>
   &nbsp; &nbsp; &nbsp; &nbsp; **•** **DOWC**: Uses the minimum fluorescence in the first cooling and warming cycle as Fmin<br>
   **•** Merges individual neuron results into a summary CSV and plot <br>
Supporting modules that run internally:<br>

| File Name                    | Description                                                  |
|------------------------------|--------------------------------------------------------------|
| `Generate_background.py`     | Generates background list creation.                          |
| `individual_dFoverF0_1.py`   | ΔF/F0 calculation for DOCC.                                  |
| `individual_dFoverF0_DOWC.py`| ΔF/Fmin calculation for DOwC.                                |
| `merge_dFoverF0_1.py`        | Merges all neuron result files into a combined dataset.      |
| `utility.py`                 | Shared utility functions across all modules.                 |

3. Temperature Binding (CITbind_dynamic.py) <br>
After individual sample processing,  this script combines temperature data and calcium imaging results and generates aligned dual-axis plots.<br>
**•** Generate summarized time-synchronized combined CSVs<br>
**•** Generate plots of ΔF/F₀ and temperature (two versions: default and y-range limited)<br>

4.  Summary Visualization (data_summary.py) <br>
Once all individual samples have been processed, this script: <br>
**•** Computes mean ± SEM<br>
**•** Outputs a stacked plot (combined_gradient_plot.png) showing:<br>
&nbsp; &nbsp; &nbsp; &nbsp; **•** Top panel: Average ΔF/F₀ or ΔF/Fmin<br>
&nbsp; &nbsp; &nbsp; &nbsp; **•** Bottom panel: Temperature curve<br>


