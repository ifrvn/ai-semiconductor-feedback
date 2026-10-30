# Empirical data registry (not populated)

No fabricated historical data are bundled. To calibrate the model, add datasets with their original sources and transparent transformations.

Recommended schema per observation:
`date,metric,value,unit,geography,source_url,accessed_at,method,uncertainty_low,uncertainty_high,notes`.

Candidate source families (verify the exact series, dates, and definitions):
- Epoch AI hardware trends: https://epoch.ai/trends
- Stanford AI Index: https://aiindex.stanford.edu/report/
- SEMI fab equipment and capacity releases: https://www.semi.org/
- Company annual reports and SEC filings for capex, R&D and spending
- Published EDA adoption studies with comparison groups

Keep raw and processed data separate; document deflators and currency conversions; do not conflate FLOPs, GPU shipments, HBM bandwidth, utilization, or training spend. Do not interpolate absent data and represent uncertainty explicitly.
