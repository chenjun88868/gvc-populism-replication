# Populism and GVC Resilience

**Replication Package and Research Coding Sample**

This repository contains the curated replication files for the current manuscript version of *Populism and GVC Resilience*, archived in `manuscript/writing_sample_current_version.pdf`. The project studies how populist governments are associated with changes in global value chain resilience using cross-national panel data, dynamic specifications, double machine learning exercises, and mechanism analyses. The repository is organized as a self-contained empirical research package: it includes frozen analysis-ready datasets, version-locked manuscript assets, and Python scripts that regenerate the tables, regression summaries, and figures reported in the current draft.

## At a Glance

- **Research question:** How is populist governance related to the resilience of countries' positions in global value chains?
- **Data:** Frozen cross-national analysis panels packaged for the current manuscript version.
- **Methods:** Dynamic panel regressions, interaction models, double machine learning, and mechanism tests.
- **Deliverable:** A clean replication package that reproduces the tables and figures used in the current writing sample.

## Replication Note

This repository contains the replication materials for the manuscript version stored in `manuscript/writing_sample_current_version.pdf`. The package is intentionally scoped to the materials used in the current paper version rather than the full historical project archive. Every file retained here is included for one of two reasons:

1. it is required to regenerate the empirical outputs used in the paper; or
2. it is preserved as an exact manuscript asset tied to the current draft.

The package includes:

- analysis-ready panel datasets for the baseline models, interaction models, dynamic DML exercises, and mechanism analyses;
- locked result workbooks corresponding to the manuscript version currently on file;
- Python code that regenerates tables, regression-result exports, and figures from the packaged data; and
- exact manuscript tables and figures retained for version verification.

A more formal replication note is provided in `docs/replication_note.md`.

## Replication Scope

Running the packaged workflow reproduces the empirical materials used in the current manuscript version, including:

- the baseline dynamic specifications;
- the interaction and heterogeneity specifications;
- the dynamic DML results;
- the two-step rule mechanism analysis;
- the WUI mechanism analysis; and
- the manuscript figures currently included in the writing sample.

The repository therefore supports both analytical replication and direct comparison against the exact assets embedded in the current draft.

## Quick Start

From the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/reproduce.py
```

The script writes regenerated outputs to `outputs/tables/` and `outputs/figures/`.

## Expected Outputs

After running `scripts/reproduce.py`, the repository produces:

- regression-result CSV files in `outputs/tables/`;
- publication-style LaTeX tables in `outputs/tables/`;
- regenerated manuscript figures in `outputs/figures/`; and
- outputs that can be checked against the exact manuscript assets preserved in the repository.

## Repository Structure

- `data/raw/`: minimal upstream source file retained for audit and provenance.
- `data/analysis/`: frozen analysis-ready panels and locked result workbooks used for the current manuscript version.
- `scripts/reproduce.py`: master Python script that regenerates analytical tables, diagnostics, and figures.
- `outputs/tables/`: generated regression summaries and LaTeX tables.
- `outputs/figures/`: regenerated figures together with version-locked `_current` figure files.
- `manuscript/`: current PDF, LaTeX manuscript, and exact table files used in the current paper draft.
- `docs/data_inventory.md`: concise inventory of the packaged datasets.
- `docs/replication_note.md`: formal note describing scope, workflow, and versioning.

## Exact Assets and Regenerated Files

The repository distinguishes between exact manuscript assets and regenerated outputs.

- `manuscript/table*_current.tex` and `outputs/tables/table*_current_locked.tex` are the exact table files used in the current manuscript version.
- `outputs/figures/*_current.png` are the exact figure files currently embedded in the draft.
- `scripts/reproduce.py` regenerates analytical outputs from the frozen analysis datasets and locked result workbooks included in `data/analysis/`.

This structure preserves the exact paper version used as a writing sample while also providing a clean, rerunnable replication workflow.

## Data Documentation

The data packaged in `data/analysis/` are named to reflect their analytical role and manuscript mapping. A concise inventory is available in `docs/data_inventory.md`, including the baseline panel, interaction samples, DML panels, and mechanism-analysis files.

## Computing Environment

The replication code is written in Python and relies on the packages listed in `requirements.txt`. All scripts use relative paths so the repository can be reproduced from the project root without machine-specific edits.

## Versioning Note

This package is organized around the current manuscript version, not the entire project history. If a later draft changes the analytical sample, outputs, or presentation files, the recommended practice is to freeze a new manuscript version and preserve the earlier locked assets rather than overwrite them in place.
