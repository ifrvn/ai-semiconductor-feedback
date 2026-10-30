# Historical data and calibration: scope and reproducibility

**As of 2026-10-30**, this repository contains an *observational proxy fit*, **not a calibrated five-state causal model**. The distinction is deliberate: fitting a few aggregated public series to many latent variables and delayed feedback effects would yield spurious parameter precision.

## Sources and direct observations

1. **Epoch AI**, Venkat Somala (2026-08-13), [AI chips purchased: performance per dollar](https://epoch.ai/data-insights/chip-performance-per-dollar), data for 2023 Q1 through 2025 Q4. File `data/raw/epoch_chip_price_performance_2023_2025.csv` transcribes the **rounded grouped quarter–chip values** and their 2025-USD spending. Attribution: Epoch AI, CC-BY. Performance per dollar is measured relative to an H100 at its 2025 price; costs here are **accelerator purchase costs**, not total installed compute. Year-end epochs reflect *sold* rather than installed devices.

2. **Semiconductor Industry Association (SIA/WSTS)**, [2023 annual sales](https://www.semiconductors.org/global-semiconductor-sales-decrease-8-2-in-2023-market-rebounds-late-in-year/), [2024 annual sales with March 2025 revision](https://www.semiconductors.org/global-semiconductor-sales-increase-19-1-in-2024-double-digit-growth-projected-in-2025/), [2025 annual sales](https://www.semiconductors.org/global-annual-semiconductor-sales-increase-25-6-to-791-7-billion-in-2025/). File `data/raw/sia_global_sales_2022_2025.csv`. **2024 is revised to USD 630.5 bn**. **2025 is USD 791.7 bn in the Feb 2026 SIA release**; later final WSTS releases report USD 795.6 bn. We keep SIA's dated vintage explicitly rather than silently mixing revisions. Nominal sales are not deflated and **must not be interpreted as effective compute capacity**.

We use the source values as transcribed, without silently imputing missing records. Verify against original web pages when changing the dataset. Do not use the published 49% CAGR as an independent extra observation when fitting the quarterly values from which it was derived.

## Reproduction

```sh
python -m feedback_lab.calibration --output results/calibration.json
python -m unittest discover -s tests -v
```

The program constructs for each quarter:

```text
P_q = sum_i(spending_iq * performance_per_dollar_iq) / sum_i(spending_iq)
C_proxy_q = 1 / P_q
```

It then estimates `log(P_q) = a + b * year_q + residual_q` with equal quarterly weights. It reports `exp(b) - 1` as the annual *descriptive* growth of performance per dollar. It trains on 2023–2024 (8 quarters) and evaluates on the 2025 holdout (4 quarters) with log RMSE. A full-sample trend is also reported. This is not a stable confidence interval; economic time series can be autocorrelated and undergo structural breaks.

The original Epoch article reports about **49%/year**, **90% bootstrap interval 36%–66%**. The repository uses rounded values and grouping; results may differ slightly. The model-cost series is a **proxy**, not `C` in the complete model: it omits the effects of HBM, networking, electricity, utilization, deployment lag and financing.

For SIA, report annual nominal revenue and yearly growth rates as **context**. Do not use a revenue growth rate to fit capacity `Q`.

## Structural identifiability

The real scientific target is a lagged causal effect of AI capability on cost improvement or design-cycle compression (e.g. `ai_cost_progress`, `lag_ai_efficiency`). The observable quarterly hardware price-performance trend alone cannot separate:
- non-AI improvements in process, architecture and packaging;
- AI-enabled improvements in design and yield;
- changes in product mix, scarcity, purchase pricing and vendor margins.

Neither the AI capability state `A`, physical capacity `Q`, commercialization delay `T`, nor reinvestable capital stock `B` is measured by these two files. **All structural parameters remain uncalibrated**. Even using the observed cost trend as `natural_cost_progress` is invalid: the model includes a floor and additional technological drivers, while the observed series is the reciprocal of a sales-weighted theoretical-throughput proxy.

## Next empirical work

- Acquire and clean workload-level **realized** training/inference throughput, HBM bandwidth, networking, power and utilization data with consistent workloads.
- Obtain chip fab process outcomes or EDA project metrics **before/after AI-tool adoption**, with matched non-adopters and controlled process/node effects. Estimate differences-in-differences or staggered adoption event studies; assess selection and parallel-trends assumptions.
- Build capital panels from company financial filings and evaluate fab capacity in wafer starts, HBM supply, and advanced packaging separately.
- Align timing of AI tool release, design start, tape-out, qualification, wafer production and shipment.
- Bootstrap at an appropriate cluster unit, run rolling holdouts and sensitivity to revisions, deflators, lags and metric definitions.
- Only then fit jointly observable blocks; report posterior/practical identifiability and predictive performance versus simpler models.

**Do not publish numerical forecasts from the exploratory five-variable model as evidence-based projections.**
