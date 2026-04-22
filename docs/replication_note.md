# Replication Note

## Manuscript Covered

This package reproduces the manuscript version archived as `manuscript/writing_sample_current_version.pdf`.

## Purpose of the Package

The repository is structured as a journal-style replication package for the current draft of *Populism and GVC Resilience*. It is intentionally limited to the data, code, and manuscript artifacts required to reproduce the empirical content of the present version of the paper. The objective is to make the replication package both auditable and easy to run: raw provenance is retained in minimal form, analysis-ready datasets are frozen, and version-locked manuscript outputs are preserved separately from regenerated outputs.

## Included Materials

The package contains four core components.

1. **Analysis-ready data.** The `data/analysis/` directory contains the panels used in the baseline dynamic models, interaction specifications, dynamic DML exercises, and mechanism analyses.
2. **Locked result workbooks.** Version-locked regression-result workbooks are retained in `data/analysis/` because they correspond directly to the manuscript version covered by this package.
3. **Replication code.** The script `scripts/reproduce.py` regenerates the analytical tables, regression summaries, and figures distributed in `outputs/`.
4. **Exact manuscript assets.** The `manuscript/` directory and `_current` outputs preserve the exact tables and figures used in the archived writing-sample version.

## Replication Procedure

From the repository root, run:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/reproduce.py
```

The script writes regenerated files to `outputs/tables/` and `outputs/figures/`.

## Replication Targets

The package is designed to reproduce the empirical objects used in the current manuscript, including:

- baseline dynamic regression tables;
- interaction and heterogeneity tables;
- dynamic DML results;
- rule-mechanism estimates;
- WUI-mechanism estimates; and
- manuscript figures distributed in the current writing sample.

## Exact Files Preserved for Verification

The following files are retained as exact manuscript-version artifacts:

- `manuscript/table*_current.tex`
- `outputs/tables/table*_current_locked.tex`
- `outputs/figures/*_current.png`

These files allow the user to verify that the package corresponds to the archived manuscript version, even when regenerated outputs may reflect harmless formatting or runtime differences.

## Data Naming and Documentation

Dataset names are chosen to match their analytical role. For example, the dynamic-panel files begin with `dynamic_`, the two-step rule-mechanism files begin with `rule_step`, and the uncertainty mechanism file is stored as `wui_final_clean_panel.csv`. A concise inventory is available in `docs/data_inventory.md`.

## Environment and Reproducibility Standard

The replication code is written in Python and uses only repository-relative paths. The package is designed to separate upstream raw input, frozen analysis data, code, outputs, and manuscript assets in a way that aligns with standard empirical-research replication practice.

## Versioning Convention

This repository reflects the current manuscript version only. If the paper is revised later, the preferred archival practice is to preserve a new versioned manuscript snapshot rather than overwrite the locked assets associated with the present draft.
