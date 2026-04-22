# Populism and GVC Resilience Replication Package

This repository organizes the data, code, manuscript assets, and outputs needed to reproduce the current writing-sample version of the paper in `manuscript/writing_sample_current_version.pdf`.

## Repository layout

- `data/raw/`: minimal upstream source file retained for audit.
- `data/analysis/`: frozen analysis-ready panels and locked regression-result workbooks used for the current manuscript.
- `scripts/reproduce.py`: master Python script that regenerates analytical tables, diagnostics, and figures from the packaged data.
- `outputs/tables/`: generated tables and regression-result CSV files.
- `outputs/figures/`: regenerated figures plus `_current` figure files copied from the current manuscript folder.
- `manuscript/`: current PDF, LaTeX manuscript, and exact table `.tex` files used in the current paper draft.

## How to reproduce

From the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/reproduce.py
```

The script writes all generated outputs to `outputs/`.

## What is exact vs. regenerated

- `manuscript/table*_current.tex` and `outputs/tables/table*_current_locked.tex` are the exact table files used in the current paper version.
- `outputs/figures/*_current.png` are the exact figure images currently embedded in the manuscript.
- `scripts/reproduce.py` regenerates the packaged analysis outputs from the frozen data panels and result workbooks included in this repository.

This structure is intentional: it preserves the exact version used in the Yale predoc application while also providing clean Python code and analysis-ready data for replication.

## Core replication inputs

- Dynamic main models: `data/analysis/dynamic_*`
- Rule-mechanism step 1: `data/analysis/rule_step1_regression_sample.csv`
- Rule-mechanism step 2: `data/analysis/rule_step2_dml_*`
- WUI mechanism: `data/analysis/wui_final_clean_panel.csv`

## Notes

- All code uses relative paths.
- The package is organized around the current manuscript version rather than the entire historical project archive.
- Intermediate locked result workbooks are retained because they correspond directly to the current paper draft and prevent drift from later reruns.
