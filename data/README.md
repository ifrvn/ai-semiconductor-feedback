# Empirical data registry

Historical **source-derived observations are now included** in `raw/`. Values come from the cited published tables, not synthetic examples. The project contains no empirically estimated causal feedback coefficients.

## Available files

- `raw/epoch_chip_price_performance_2023_2025.csv`: 57 quarter/chip-group data points for 2023 Q1–2025 Q4, transcribed from [Epoch AI](https://epoch.ai/data-insights/chip-performance-per-dollar) (Venkat Somala, 2026-08-13). Price-performance is in relative H100-2025 units and spend is in billion constant-2025 USD. Original dataset published under CC-BY; credit Epoch AI when reusing. Values are rounded grouped observations; the original analysis uses underlying chip-level data.
- `raw/sia_global_sales_2022_2025.csv`: four annual nominal-revenue observations, with a direct source URL and release date for each. This is SIA's 2025 vintage, not the subsequent WSTS final 2025 figure. Annual sales are **not** capacity, wafer-starts or AI accelerator revenue.

See [calibration notes](../docs/calibration.md) for methodology, revisions and identification limitations. Run:

```bash
python -m feedback_lab.calibration
```

Outputs are written to `results/calibration.json`, which is intentionally gitignored so each user can regenerate it.

## Future datasets

For expanded fitting, track `date,metric,value,unit,geography,source_url,accessed_at,method,uncertainty_low,uncertainty_high,notes`. Store raw files separately from computed features. Verify publisher terms, original timestamps, data revisions and any inflation deflators.

Potential additional primary sources: [Epoch AI datasets](https://epoch.ai/data), [Stanford AI Index](https://aiindex.stanford.edu/report/), [SEMI](https://www.semi.org/), SEC company filings, and matched AI-assisted EDA or foundry-process studies.

Do **not** conflate hardware peak throughput, realized useful training/inference compute, AI capability, chip shipments, semiconductor sales, fab capacity or industry capital stock.
