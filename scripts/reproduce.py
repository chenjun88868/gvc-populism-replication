from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import os

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".mplconfig"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


DATA = ROOT / "data" / "analysis"
TABLES = ROOT / "outputs" / "tables"
FIGURES = ROOT / "outputs" / "figures"

for path in [TABLES, FIGURES]:
    path.mkdir(parents=True, exist_ok=True)


OUTCOMES = [
    "algebraic_connectivity_vitality_w",
    "efficiency_vitality_w",
    "flow_betweenness_log1p_w",
    "communicability_betweenness_asinh_w",
    "shannon_entropy_w",
    "participation_coefficient_w",
    "within_module_degree_zscore_w",
    "laplacian_centrality_log_w",
]

PAPER_OUTCOMES = [
    "algebraic_connectivity_vitality_w",
    "efficiency_vitality_w",
    "laplacian_centrality_log_w",
    "flow_betweenness_log1p_w",
    "within_module_degree_zscore_w",
    "shannon_entropy_w",
    "participation_coefficient_w",
]

SHORT = {
    "algebraic_connectivity_vitality_w": "ACV",
    "efficiency_vitality_w": "EV",
    "laplacian_centrality_log_w": "LC",
    "flow_betweenness_log1p_w": "FB",
    "within_module_degree_zscore_w": "WMDZ",
    "shannon_entropy_w": "SE",
    "participation_coefficient_w": "PC",
    "communicability_betweenness_asinh_w": "CB",
}

CONTROLS_L1 = ["lnGDP_lag1", "lnTradeOpen_lag1", "asinhFDI_lag1", "asinhInflation_winsor_lag1"]
CONTROLS_T2 = [
    "ln_gdp_t_minus_2",
    "ln_tradeopen_t_minus_2",
    "asinh_fdi_t_minus_2",
    "asinh_inflation_winsor_t_minus_2",
]


def stars(p_value: float) -> str:
    if pd.isna(p_value):
        return ""
    if p_value < 0.01:
        return "***"
    if p_value < 0.05:
        return "**"
    if p_value < 0.10:
        return "*"
    return ""


def fmt(value: float, digits: int = 3) -> str:
    if pd.isna(value):
        return ""
    text = f"{value:.{digits}f}"
    if text.startswith("-0.000"):
        text = text.replace("-0.000", "0.000", 1)
    return text


def coef_se(coef: float, se: float, p_value: float, digits: int = 3) -> str:
    return f"{fmt(coef, digits)}{stars(p_value)} ({fmt(se, digits)})"


def fit_cluster_ols(df: pd.DataFrame, formula: str, cluster: str = "country"):
    return smf.ols(formula, data=df).fit(
        cov_type="cluster",
        cov_kwds={"groups": df[cluster], "use_correction": True},
        use_t=True,
    )


def tidy_ols(result, outcome: str, model: str, terms: Iterable[str]) -> pd.DataFrame:
    conf = result.conf_int()
    rows = []
    for term in terms:
        if term not in result.params.index:
            continue
        rows.append(
            {
                "outcome": outcome,
                "model": model,
                "term": term,
                "coef": float(result.params[term]),
                "std_err_cluster_country": float(result.bse[term]),
                "t_value": float(result.tvalues[term]),
                "p_value": float(result.pvalues[term]),
                "ci_low": float(conf.loc[term, 0]),
                "ci_high": float(conf.loc[term, 1]),
                "stars": stars(float(result.pvalues[term])),
                "nobs": int(result.nobs),
                "r2": float(getattr(result, "rsquared", np.nan)),
                "adj_r2": float(getattr(result, "rsquared_adj", np.nan)),
                "clusters_country": int(result.model.data.frame["country"].nunique()),
                "formula": result.model.formula,
            }
        )
    return pd.DataFrame(rows)


def run_dynamic_tables() -> None:
    rename = {
        "populism_gov_l1_x_Africa-MiddleEast": "populism_gov_l1_x_Africa_MiddleEast",
        "Africa-MiddleEast_i": "Africa_MiddleEast_i",
    }
    rows = []

    baseline = pd.read_csv(DATA / "dynamic_baseline_full.csv").rename(columns=rename)
    baseline_specs = {
        "M1": ["populism_gov_annual_l1"],
        "M2": ["populism_gov_annual_l1", "lnGDP_lag1", "lnTradeOpen_lag1", "asinhFDI_lag1"],
        "M3": ["populism_gov_annual_l1", *CONTROLS_L1],
    }
    for outcome in OUTCOMES:
        lag = f"{outcome}_lag1"
        for model, variables in baseline_specs.items():
            needed = ["country", "year", outcome, lag, *variables]
            sample = baseline.dropna(subset=needed).copy()
            formula = f"{outcome} ~ {lag} + {' + '.join(variables)} + C(country) + C(year)"
            result = fit_cluster_ols(sample, formula)
            rows.append(tidy_ols(result, outcome, f"Baseline_{model}", [lag, *variables]))

    interaction_files = {
        "Openness_M3": ("dynamic_openness_m3.csv", ["populism_gov_annual_l1", "lnTradeOpen_lag1", "interaction_populism_tradeopen_lag1", "lnGDP_lag1", "asinhFDI_lag1", "asinhInflation_winsor_lag1"]),
        "Democracy_M3": ("dynamic_democracy_m3.csv", ["populism_gov_annual_l1", "v2x_polyarchy_l1", "interaction_populism_gov_l1_x_democracy_l1", *CONTROLS_L1]),
        "Region_M3": ("dynamic_region_m3.csv", ["populism_gov_l1_x_Europe", "populism_gov_l1_x_Asia", "populism_gov_l1_x_Americas", "populism_gov_l1_x_Africa_MiddleEast", *CONTROLS_L1]),
    }
    for model, (file_name, variables) in interaction_files.items():
        df = pd.read_csv(DATA / file_name).rename(columns=rename)
        for outcome in OUTCOMES:
            lag = f"{outcome}_lag1"
            formula = f"{outcome} ~ {lag} + {' + '.join(variables)} + C(country) + C(year)"
            result = fit_cluster_ols(df, formula)
            rows.append(tidy_ols(result, outcome, model, [lag, *variables]))

    dynamic_results = pd.concat(rows, ignore_index=True)
    dynamic_results.to_csv(TABLES / "dynamic_ols_results.csv", index=False)

    dml_global = run_dynamic_dml(pd.read_csv(DATA / "dynamic_dml_global.csv").rename(columns=rename), "DML_global")
    dml_americas = run_dynamic_dml(pd.read_csv(DATA / "dynamic_dml_americas.csv").rename(columns=rename), "DML_americas")
    pd.concat([dml_global, dml_americas], ignore_index=True).to_csv(TABLES / "dynamic_dml_results.csv", index=False)

    write_table1(dynamic_results)
    write_table2(dynamic_results)
    write_table3(pd.concat([dml_global, dml_americas], ignore_index=True))


def _standardize_train_test(x_train: np.ndarray, x_test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    mean = x_train.mean(axis=0)
    std = x_train.std(axis=0, ddof=0)
    std = np.where(std == 0, 1.0, std)
    return (x_train - mean) / std, (x_test - mean) / std


def _make_folds(n: int, n_splits: int = 5, seed: int = 42) -> list[np.ndarray]:
    idx = np.arange(n)
    rng = np.random.default_rng(seed)
    rng.shuffle(idx)
    return list(np.array_split(idx, n_splits))


def _crossfit_lasso_residuals(w: np.ndarray, target: np.ndarray, alpha: float, seed: int) -> np.ndarray:
    folds = _make_folds(len(target), n_splits=5, seed=seed)
    residuals = np.empty(len(target))
    for fold_id, test_idx in enumerate(folds):
        train_idx = np.concatenate([folds[j] for j in range(len(folds)) if j != fold_id])
        x_train, x_test = _standardize_train_test(w[train_idx], w[test_idx])
        x_train = sm.add_constant(x_train, has_constant="add")
        x_test = sm.add_constant(x_test, has_constant="add")
        fit = sm.OLS(target[train_idx], x_train).fit_regularized(alpha=alpha, L1_wt=1.0)
        pred = np.asarray(fit.predict(x_test))
        residuals[test_idx] = target[test_idx] - pred
    return residuals


def run_dynamic_dml(df: pd.DataFrame, model_name: str) -> pd.DataFrame:
    w_df = pd.concat(
        [
            df[CONTROLS_L1].reset_index(drop=True),
            pd.get_dummies(df["country"], prefix="country", drop_first=True, dtype=float).reset_index(drop=True),
            pd.get_dummies(df["year"].astype(int).astype(str), prefix="year", drop_first=True, dtype=float).reset_index(drop=True),
        ],
        axis=1,
    )
    w = w_df.to_numpy(dtype=float)
    d = df["populism_gov_annual_l1"].to_numpy(dtype=float)
    rows = []
    for outcome in OUTCOMES:
        y = df[outcome].to_numpy(dtype=float)
        lag = df[f"{outcome}_lag1"].to_numpy(dtype=float)
        y_resid = _crossfit_lasso_residuals(w, y, alpha=0.001, seed=42)
        d_resid = _crossfit_lasso_residuals(w, d, alpha=0.001, seed=43)
        lag_resid = _crossfit_lasso_residuals(w, lag, alpha=0.001, seed=44)
        final = pd.DataFrame({"y_resid": y_resid, "d_resid": d_resid, "lag_resid": lag_resid, "country": df["country"].values})
        result = smf.ols("y_resid ~ d_resid + lag_resid", data=final).fit(
            cov_type="cluster",
            cov_kwds={"groups": final["country"], "use_correction": True},
            use_t=True,
        )
        conf = result.conf_int()
        for term, mapped in [("d_resid", "populism_gov_annual_l1"), ("lag_resid", f"{outcome}_lag1")]:
            rows.append(
                {
                    "outcome": outcome,
                    "model": model_name,
                    "term": mapped,
                    "coef": float(result.params[term]),
                    "std_err_cluster_country": float(result.bse[term]),
                    "p_value": float(result.pvalues[term]),
                    "ci_low": float(conf.loc[term, 0]),
                    "ci_high": float(conf.loc[term, 1]),
                    "stars": stars(float(result.pvalues[term])),
                    "nobs": int(result.nobs),
                    "r2": float(result.rsquared),
                    "clusters_country": int(df["country"].nunique()),
                    "alpha_fixed": 0.001,
                }
            )
    return pd.DataFrame(rows)


@dataclass
class RuleDMLResult:
    model_name: str
    treatment: str
    theta: float
    se: float
    p_value: float
    ci_low: float
    ci_high: float
    n_obs: int
    n_countries: int
    n_years: int
    r2_final: float


def _make_group_folds(groups: Iterable, n_splits: int = 5, seed: int = 42):
    groups_arr = np.asarray(list(groups))
    unique_groups = pd.unique(groups_arr)
    rng = np.random.default_rng(seed)
    shuffled = unique_groups.copy()
    rng.shuffle(shuffled)
    return [(np.flatnonzero(~np.isin(groups_arr, fg)), np.flatnonzero(np.isin(groups_arr, fg))) for fg in np.array_split(shuffled, min(n_splits, len(unique_groups)))]


def _ridge_predict(x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, alpha: float = 1.0) -> np.ndarray:
    x_train, x_test = _standardize_train_test(x_train, x_test)
    y_mean = y_train.mean()
    y_center = y_train - y_mean
    xtx = x_train.T @ x_train
    params = np.linalg.solve(xtx + alpha * np.eye(xtx.shape[0]), x_train.T @ y_center)
    return y_mean + x_test @ params


def _rule_dml_plr(df: pd.DataFrame, outcome: str, treatment: str, x_df: pd.DataFrame, seed: int) -> RuleDMLResult:
    y = df[outcome].to_numpy(dtype=float)
    d = df[treatment].to_numpy(dtype=float)
    x = x_df.to_numpy(dtype=float)
    groups = df["country_text_id"].to_numpy()
    y_hat = np.zeros(len(df))
    d_hat = np.zeros(len(df))
    for train_idx, test_idx in _make_group_folds(groups, n_splits=5, seed=seed):
        y_hat[test_idx] = _ridge_predict(x[train_idx], y[train_idx], x[test_idx])
        d_hat[test_idx] = _ridge_predict(x[train_idx], d[train_idx], x[test_idx])
    final = sm.OLS(y - y_hat, sm.add_constant(d - d_hat)).fit(
        cov_type="cluster",
        cov_kwds={"groups": pd.Categorical(groups).codes},
    )
    ci_low, ci_high = final.conf_int()[1]
    return RuleDMLResult("", treatment, float(final.params[1]), float(final.bse[1]), float(final.pvalues[1]), float(ci_low), float(ci_high), len(df), df["country_text_id"].nunique(), df["year"].nunique(), float(final.rsquared))


def _rule_design(df: pd.DataFrame, base_cols: list[str]) -> pd.DataFrame:
    return pd.concat(
        [
            df[base_cols].reset_index(drop=True),
            pd.get_dummies(df["country_text_id"], prefix="cty", drop_first=True).reset_index(drop=True),
            pd.get_dummies(df["year"].astype(int), prefix="yr", drop_first=True).reset_index(drop=True),
        ],
        axis=1,
    ).astype(float)


def run_rule_mechanism() -> None:
    step1 = pd.read_csv(DATA / "rule_step1_regression_sample.csv")
    models = {
        "Model1_Basic": ["populism_gov_annual_l2_z"],
        "Model2_Main": ["populism_gov_annual_l2_z", "rule_based_governance_t_minus_2"],
        "Model3_Extended": ["populism_gov_annual_l2_z", "rule_based_governance_t_minus_2", *CONTROLS_T2],
    }
    rows = []
    for model, regressors in models.items():
        formula = f"rule_based_governance_t_minus_1 ~ {' + '.join(regressors)} + C(country_text_id) + C(year)"
        result = smf.ols(formula, data=step1).fit(cov_type="cluster", cov_kwds={"groups": step1["country_text_id"]})
        conf = result.conf_int()
        for term in regressors:
            rows.append(
                {
                    "model": model,
                    "term": term,
                    "coef": result.params[term],
                    "std_err_cluster_country": result.bse[term],
                    "p_value": result.pvalues[term],
                    "ci_low": conf.loc[term, 0],
                    "ci_high": conf.loc[term, 1],
                    "nobs": int(result.nobs),
                    "r2": result.rsquared,
                    "clusters_country": step1["country_text_id"].nunique(),
                }
            )
    pd.DataFrame(rows).to_csv(TABLES / "rule_step1_results.csv", index=False)
    write_table4(pd.DataFrame(rows))

    global_results = run_rule_step2_dml(pd.read_csv(DATA / "rule_step2_dml_global_panel.csv"), "global")
    americas_results = run_rule_step2_dml(pd.read_csv(DATA / "rule_step2_dml_americas_panel.csv"), "americas")
    rule_step2 = pd.concat([global_results, americas_results], ignore_index=True)
    rule_step2.to_csv(TABLES / "rule_step2_dml_results.csv", index=False)
    write_table5(rule_step2)


def run_rule_step2_dml(df: pd.DataFrame, sample_name: str) -> pd.DataFrame:
    pop_raw = "populism_gov_annual_l2"
    pop_z = "populism_gov_annual_l2_z"
    df = df.copy()
    df[pop_z] = (df[pop_raw] - df[pop_raw].mean()) / df[pop_raw].std(ddof=0)
    rows = []
    for idx, outcome in enumerate(OUTCOMES, start=1):
        lag = f"{outcome}_t_minus_1"
        needed = ["country_text_id", "country_name", "year", outcome, lag, pop_z, pop_raw, "rule_based_governance_t_minus_1", *CONTROLS_T2]
        sample = df.loc[df[needed].notna().all(axis=1), needed].sort_values(["country_text_id", "year"]).reset_index(drop=True)
        base_x = [lag, *CONTROLS_T2]
        x1 = _rule_design(sample, base_x)
        x2 = _rule_design(sample, ["rule_based_governance_t_minus_1", *base_x])
        x3 = _rule_design(sample, [pop_z, *base_x])
        res1 = _rule_dml_plr(sample, outcome, pop_z, x1, seed=1000 + idx * 10 + 1)
        res2 = _rule_dml_plr(sample, outcome, pop_z, x2, seed=1000 + idx * 10 + 2)
        res3 = _rule_dml_plr(sample, outcome, "rule_based_governance_t_minus_1", x3, seed=1000 + idx * 10 + 3)
        rows.append(
            {
                "sample": sample_name,
                "outcome": outcome,
                "n_obs_common_sample": len(sample),
                "model1_pop_theta": res1.theta,
                "model1_pop_se": res1.se,
                "model1_pop_p": res1.p_value,
                "model2_pop_theta": res2.theta,
                "model2_pop_se": res2.se,
                "model2_pop_p": res2.p_value,
                "model3_rule_theta": res3.theta,
                "model3_rule_se": res3.se,
                "model3_rule_p": res3.p_value,
            }
        )
    return pd.DataFrame(rows)


def run_wui_mechanism() -> None:
    df = pd.read_csv(DATA / "wui_final_clean_panel.csv")
    rows = []
    first_stage = fit_cluster_ols(
        df.dropna(subset=["wui_ln1p", "populism_gov_annual_l1", *CONTROLS_L1]),
        f"wui_ln1p ~ populism_gov_annual_l1 + {' + '.join(CONTROLS_L1)} + C(country) + C(year)",
    )
    first_coef = first_stage.params["populism_gov_annual_l1"]
    first_p = first_stage.pvalues["populism_gov_annual_l1"]
    for outcome in PAPER_OUTCOMES:
        lag = f"{outcome}_lag1"
        total_formula = f"{outcome} ~ populism_gov_annual_l2 + {lag} + {' + '.join(CONTROLS_L1)} + C(country) + C(year)"
        full_formula = f"{outcome} ~ populism_gov_annual_l2 + wui_ln1p_lag1 + {lag} + {' + '.join(CONTROLS_L1)} + C(country) + C(year)"
        total = fit_cluster_ols(df.dropna(subset=[outcome, lag, "populism_gov_annual_l2", *CONTROLS_L1]), total_formula)
        full = fit_cluster_ols(df.dropna(subset=[outcome, lag, "populism_gov_annual_l2", "wui_ln1p_lag1", *CONTROLS_L1]), full_formula)
        rows.append(
            {
                "outcome": outcome,
                "first_stage_pop_coef": first_coef,
                "first_stage_pop_p": first_p,
                "total_pop_coef": total.params["populism_gov_annual_l2"],
                "total_pop_p": total.pvalues["populism_gov_annual_l2"],
                "full_pop_coef": full.params["populism_gov_annual_l2"],
                "full_pop_p": full.pvalues["populism_gov_annual_l2"],
                "full_wui_coef": full.params["wui_ln1p_lag1"],
                "full_wui_p": full.pvalues["wui_ln1p_lag1"],
                "nobs": int(full.nobs),
                "clusters_country": df["country"].nunique(),
            }
        )
    wui = pd.DataFrame(rows)
    wui["pop_abs_shrink_share"] = (wui["total_pop_coef"].abs() - wui["full_pop_coef"].abs()) / wui["total_pop_coef"].abs()
    wui.to_csv(TABLES / "wui_mechanism_results.csv", index=False)
    write_table6(wui)


def make_figures() -> None:
    df = pd.read_csv(DATA / "dynamic_region_m3.csv").rename(
        columns={"populism_gov_l1_x_Africa-MiddleEast": "populism_gov_l1_x_Africa_MiddleEast"}
    )
    americas = df[df["Region_i_model"].eq("Americas")].copy()
    pivot = americas.pivot_table(index="country", columns="year", values="populism_gov_annual_l1", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(10, 4.8))
    im = ax.imshow(pivot, aspect="auto", cmap="YlOrRd")
    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, rotation=90, fontsize=7)
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=8)
    ax.set_title("Lagged government populism in the Americas sample")
    fig.colorbar(im, ax=ax, label="Populism(t-1)")
    fig.tight_layout()
    fig.savefig(FIGURES / "popgov_americas_heatmap.png", dpi=300)
    plt.close(fig)

    summary = df.groupby(["Region_i_model", "year"])["populism_gov_annual_l1"].quantile([0.25, 0.5, 0.75]).unstack().reset_index()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for region, sub in summary.groupby("Region_i_model"):
        sub = sub.sort_values("year")
        x = sub["year"].to_numpy(dtype=float)
        q25 = sub[0.25].to_numpy(dtype=float)
        med = sub[0.5].to_numpy(dtype=float)
        q75 = sub[0.75].to_numpy(dtype=float)
        ax.plot(x, med, label=region)
        ax.fill_between(x, q25, q75, alpha=0.12)
    ax.set_title("Regional median and interquartile range of lagged populism")
    ax.set_xlabel("Year")
    ax.set_ylabel("Populism(t-1)")
    ax.legend(frameon=False, ncol=2)
    fig.tight_layout()
    fig.savefig(FIGURES / "popgov_region_trend.png", dpi=300)
    plt.close(fig)

    outcome = "laplacian_centrality_log_w"
    formula = (
        f"{outcome} ~ {outcome}_lag1 + populism_gov_l1_x_Europe + populism_gov_l1_x_Asia + "
        "populism_gov_l1_x_Americas + populism_gov_l1_x_Africa_MiddleEast + "
        "lnGDP_lag1 + lnTradeOpen_lag1 + asinhFDI_lag1 + asinhInflation_winsor_lag1 + C(country) + C(year)"
    )
    result = smf.ols(formula, data=df).fit()
    influence = result.get_influence()
    plot_df = df[["country", "year", "Region_i_model"]].copy()
    plot_df["leverage"] = influence.hat_matrix_diag
    plot_df["cooks_d"] = influence.cooks_distance[0]
    plot_df["is_americas"] = plot_df["Region_i_model"].eq("Americas")
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    size = 30 + 900 * np.sqrt(plot_df["cooks_d"].clip(lower=0))
    other = ~plot_df["is_americas"]
    if other.any():
        ax.scatter(
            plot_df.loc[other, "leverage"],
            plot_df.loc[other, "cooks_d"],
            s=size[other],
            alpha=0.45,
            color="#7f8c8d",
            label="Other regions",
        )
    if plot_df["is_americas"].any():
        ax.scatter(
            plot_df.loc[plot_df["is_americas"], "leverage"],
            plot_df.loc[plot_df["is_americas"], "cooks_d"],
            s=size[plot_df["is_americas"]],
            alpha=0.75,
            color="#c0392b",
            label="Americas",
        )
    ax.set_title("Influence diagnostics for Populism × Americas model")
    ax.set_xlabel("Leverage")
    ax.set_ylabel("Cook's distance")
    fig.tight_layout()
    fig.savefig(FIGURES / "popxamericas_influence.png", dpi=300)
    plt.close(fig)


def latex_tabular(header: list[str], body: list[list[str]]) -> str:
    lines = ["\\begin{tabular}{" + "l" + "c" * (len(header) - 1) + "}", "\\toprule", " & ".join(header) + " \\\\", "\\midrule"]
    for row in body:
        lines.append(" & ".join(row) + " \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    return "\n".join(lines)


def write_table1(results: pd.DataFrame) -> None:
    body = []
    for model in ["M1", "M2", "M3"]:
        body.append([f"Panel {model} Populism$_{{t-1}}$"] + [
            coef_se(
                *results.query("model == @model_name and outcome == @outcome and term == 'populism_gov_annual_l1'")[["coef", "std_err_cluster_country", "p_value"]].iloc[0],
            )
            for outcome in PAPER_OUTCOMES
            for model_name in [f"Baseline_{model}"]
        ])
        if model == "M1":
            body.append(["$\\rho$ (lagged Y)"] + [
                coef_se(
                    *results.query("model == 'Baseline_M1' and outcome == @outcome and term == @lag")[["coef", "std_err_cluster_country", "p_value"]].iloc[0],
                )
                for outcome in PAPER_OUTCOMES
                for lag in [f"{outcome}_lag1"]
            ])
        body.append(["N"] + [
            str(int(results.query("model == @model_name and outcome == @outcome and term == 'populism_gov_annual_l1'")["nobs"].iloc[0]))
            for outcome in PAPER_OUTCOMES
            for model_name in [f"Baseline_{model}"]
        ])
    (TABLES / "table1_baseline_dynamic.tex").write_text(latex_tabular(["", *[SHORT[o] for o in PAPER_OUTCOMES]], body), encoding="utf-8")


def write_table2(results: pd.DataFrame) -> None:
    sections = [
        ("Populism $\\times$ Openness", "Openness_M3", "interaction_populism_tradeopen_lag1"),
        ("Populism $\\times$ Democracy", "Democracy_M3", "interaction_populism_gov_l1_x_democracy_l1"),
        ("Populism $\\times$ Americas", "Region_M3", "populism_gov_l1_x_Americas"),
    ]
    body = []
    for label, model, term in sections:
        body.append([label] + [
            coef_se(*results.query("model == @model and outcome == @outcome and term == @term")[["coef", "std_err_cluster_country", "p_value"]].iloc[0])
            for outcome in PAPER_OUTCOMES
        ])
    (TABLES / "table2_interactions.tex").write_text(latex_tabular(["", *[SHORT[o] for o in PAPER_OUTCOMES]], body), encoding="utf-8")


def write_table3(results: pd.DataFrame) -> None:
    body = []
    for model, label in [("DML_global", "Global sample"), ("DML_americas", "Americas subsample")]:
        body.append([label] + [
            coef_se(*results.query("model == @model and outcome == @outcome and term == 'populism_gov_annual_l1'")[["coef", "std_err_cluster_country", "p_value"]].iloc[0])
            for outcome in PAPER_OUTCOMES
        ])
        body.append(["R$^2$"] + [
            fmt(results.query("model == @model and outcome == @outcome and term == 'populism_gov_annual_l1'")["r2"].iloc[0], 3)
            for outcome in PAPER_OUTCOMES
        ])
    (TABLES / "table3_dml.tex").write_text(latex_tabular(["", *[SHORT[o] for o in PAPER_OUTCOMES]], body), encoding="utf-8")


def write_table4(results: pd.DataFrame) -> None:
    terms = ["populism_gov_annual_l2_z", "rule_based_governance_t_minus_2", *CONTROLS_T2]
    models = ["Model1_Basic", "Model2_Main", "Model3_Extended"]
    body = []
    for term in terms:
        row = [term]
        for model in models:
            sub = results[(results["model"].eq(model)) & (results["term"].eq(term))]
            row.append("" if sub.empty else coef_se(sub["coef"].iloc[0], sub["std_err_cluster_country"].iloc[0], sub["p_value"].iloc[0]))
        body.append(row)
    body.append(["N"] + [str(int(results[results["model"].eq(m)]["nobs"].iloc[0])) for m in models])
    body.append(["R$^2$"] + [fmt(results[results["model"].eq(m)]["r2"].iloc[0], 3) for m in models])
    (TABLES / "table4_rule_step1.tex").write_text(latex_tabular(["", "M1", "M2", "M3"], body), encoding="utf-8")


def write_table5(results: pd.DataFrame) -> None:
    selected_global = ["algebraic_connectivity_vitality_w", "flow_betweenness_log1p_w", "shannon_entropy_w", "participation_coefficient_w", "laplacian_centrality_log_w"]
    selected_americas = ["shannon_entropy_w", "participation_coefficient_w", "laplacian_centrality_log_w"]
    body = [["Panel A: Global", "", "", ""]]
    for outcome in selected_global:
        sub = results[(results["sample"].eq("global")) & (results["outcome"].eq(outcome))].iloc[0]
        body.append([SHORT[outcome], coef_se(sub["model1_pop_theta"], sub["model1_pop_se"], sub["model1_pop_p"]), coef_se(sub["model2_pop_theta"], sub["model2_pop_se"], sub["model2_pop_p"]), coef_se(sub["model3_rule_theta"], sub["model3_rule_se"], sub["model3_rule_p"])])
    body.append(["Panel B: Americas", "", "", ""])
    for outcome in selected_americas:
        sub = results[(results["sample"].eq("americas")) & (results["outcome"].eq(outcome))].iloc[0]
        body.append([SHORT[outcome], coef_se(sub["model1_pop_theta"], sub["model1_pop_se"], sub["model1_pop_p"]), coef_se(sub["model2_pop_theta"], sub["model2_pop_se"], sub["model2_pop_p"]), coef_se(sub["model3_rule_theta"], sub["model3_rule_se"], sub["model3_rule_p"])])
    (TABLES / "table5_rule_step2_dml.tex").write_text(latex_tabular(["Outcome", "M1: Populism", "M2: Populism + Rule", "M3: Rule"], body), encoding="utf-8")


def write_table6(results: pd.DataFrame) -> None:
    body = [
        ["First-stage Populism $\\rightarrow$ WUI"] + [fmt(results["first_stage_pop_coef"].iloc[0], 3)] * len(PAPER_OUTCOMES),
        ["First-stage p-value"] + [fmt(results["first_stage_pop_p"].iloc[0], 3)] * len(PAPER_OUTCOMES),
        ["Total Populism effect"] + [fmt(results.loc[results["outcome"].eq(o), "total_pop_coef"].iloc[0], 3) for o in PAPER_OUTCOMES],
        ["Total p-value"] + [fmt(results.loc[results["outcome"].eq(o), "total_pop_p"].iloc[0], 3) for o in PAPER_OUTCOMES],
        ["Populism after WUI"] + [fmt(results.loc[results["outcome"].eq(o), "full_pop_coef"].iloc[0], 3) for o in PAPER_OUTCOMES],
        ["WUI coefficient"] + [fmt(results.loc[results["outcome"].eq(o), "full_wui_coef"].iloc[0], 3) for o in PAPER_OUTCOMES],
        ["WUI p-value"] + [fmt(results.loc[results["outcome"].eq(o), "full_wui_p"].iloc[0], 3) for o in PAPER_OUTCOMES],
    ]
    (TABLES / "table6_wui_mechanism.tex").write_text(latex_tabular(["", *[SHORT[o] for o in PAPER_OUTCOMES]], body), encoding="utf-8")


def main() -> None:
    run_dynamic_tables()
    run_rule_mechanism()
    run_wui_mechanism()
    make_figures()
    for idx in range(1, 7):
        source = ROOT / "manuscript" / f"table{idx}_current.tex"
        if source.exists():
            (TABLES / f"table{idx}_current_locked.tex").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Replication complete. Outputs written under: {ROOT / 'outputs'}")


if __name__ == "__main__":
    main()
