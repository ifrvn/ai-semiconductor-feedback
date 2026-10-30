# Phase 7 — Real-observation calibration and out-of-time validation

This project has **not** calibrated the full AI-semiconductor feedback system. This phase validates one identifiable *observable proxy*: quarterly purchase-weighted theoretical accelerator performance per dollar from [Epoch AI](https://epoch.ai/data-insights/chip-performance-per-dollar), 2023 Q1–2025 Q4. An independent [SIA annual global semiconductor revenue release](https://www.semiconductors.org/global-annual-semiconductor-sales-increase-25-6-to-791-7-billion-in-2025/) is included as an **economic scale audit**, never treated as productive capacity.

## Run

```bash
python -m feedback_lab.empirical_validation --output results/empirical_validation.json
python -m unittest discover -s tests -v
```

No packages outside the Python standard library are required. Outputs are reproducible from committed CSV inputs.

## Defined experiments

The predictor is `y_q = log(weighted_theoretical_TPP_per_2025_USD)`; three **forecast methods**:

1. `last_value`: the last observed quarterly level; no trend.
2. `historical_drift`: extrapolate the slope from the earliest to latest observations in the training window; no future values.
3. `log_linear`: fit ordinary least squares on the past log proxy and extrapolate to the target quarter (equal weighting of quarters). This is descriptive; not a fit to the structural feedback equation.

**Fixed chronological holdout:** train 2023 Q1 through 2024 Q4 (8 quarters); test 2025 Q1 through Q4 (4 quarters). All 4 holdout predictions are generated from the one 2024 Q4 training set, not updated on 2025 data.

**Expanding-origin validation:** start with 4 quarters and advance the training cut one quarter at a time. Forecast one quarter ahead (8 origins) or exactly four quarters ahead (5 origins); for four quarters ahead, **intervening quarters are not provided to the model**. Calendar time is fractional-year, so the forecasting horizon is respected without padding.

**Metrics:** log RMSE, log MAE, signed log bias and exponentiated RMSE as a multiplicative error factor. The log metric prevents large-level quarters dominating error solely due to scale. No confidence intervals are reported: four out-of-time points and overlapping rolling origin errors do not support conventional independent observations.

## Important reconciliation

The existing `feedback_lab.calibration` descriptive historical trend and source's circa 49%/year may differ because the committed data are **rounded chip-group aggregate cells**, not original unrounded chip-level observations and Epoch's exact fit. The model-selection question is answered only by the out-of-time results, not by maximizing in-sample fit.

SIA nominal USD revenue series (2022–2025) cannot be converted to wafer-start capacity, HBM bandwidth capacity, advanced packaging throughput, or physical power without independent engineering and price/unit conversion. Four annual samples cannot identify capital formation delays or causal AI-assisted EDA gains.

The feedback, lead time, market-price markup and sector investment terms in `sector_capacity.py` and `dynamic_system.py` remain **illustrative and uncalibrated**. Backtest skill on price/performance is not proof of the structural model.

## Data quality and future acquisition

Before any structural estimation, acquire versioned observed per-sector supply, capital commitments by vintage, commissioned operating capacity, chip-level realized procurement price, representative workload utilization and AI-assisted development outcomes with matched control groups. Preserve units, times, release dates, methodology and revisions. Split train/validation chronologically, compare naïve baselines, audit forecast errors and identify which structural parameters have enough information. If the data do not identify a parameter, report that as a result rather than force an estimate.

The 2026 published Epoch series describes chip *sales* and theoretical TPP, not actual deployment; it is therefore distinct from realized training throughput.
