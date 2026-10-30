# Phase 6 — Assumption uncertainty, not calibration

This phase adds **reproducible scenario uncertainty** to the four-sector model. The available historical observations do not jointly identify the four-sector physical capacity, investment lead-time, AI-assisted cost-improvement and scarcity-price parameters. Reporting a calibrated posterior or a formal confidence interval would therefore be misleading.

## Reproduce

```sh
python -m feedback_lab.uncertainty --samples 200 --seed 20261030 --end-year 2035 --output results/uncertainty.json
python -m unittest discover -s tests -v
```

The program samples independent **uniform illustrative ranges** for demand growth, scarcity elasticity, capital allocation, AI R&D allocation, AI capability growth, chip-cost feedback strength, construction delays and investment-to-capacity productivity. Each sampled world is simulated twice with identical sampled assumptions, once with AI-to-chip cost feedback enabled and once disabled. It summarizes paired within-world differences rather than comparing unrelated random worlds.

For each outcome (AI capability A, B, delivered supply, physical cost, market price and markup), the output reports the 5th, 50th and 95th percentiles across sampled assumptions. These are **sensitivity quantiles only**; they are not probability statements about the real world, 90% confidence intervals or Bayesian credible intervals. The joint distribution is arbitrarily independent and uniform, not derived from historical data.

For feedback effects, the code reports paired relative changes in AI capability, market price, physical cost and delivered supply. The no-feedback scenario turns off the AI-to-chip-cost improvement channel **only**, leaving AI capability accumulation and capital allocation equations unchanged. Consequently the estimated differences cannot represent the total effect of AI on the semiconductor industry.

## Structural limitations

- The underlying four-sector capacity model is normalized and illustrative. Its prices are a stylized scarcity wedge, not an empirically fitted supply-demand equilibrium.
- Demand and capital stock are endogenous, but investment costs, contract pricing, inventories, financing constraints, capacity commissioning distributions, and cross-sector yield losses remain simplified.
- Independent uniform input bounds are analyst choices. Correlated shocks and heavy-tailed disruptions are absent.
- Monte Carlo convergence of sample quantiles does not imply model correctness or structural identification.
- In the present equations AI-to-chip feedback affects physical unit costs but not construction productivity or the physical supply flow directly; supply may remain unchanged between paired runs.
- The existing observed Epoch and SIA data do not calibrate the new parameters.

## Next empirical calibration

Collect sector-level annual/quarterly records of wafer starts and utilization, HBM bits shipped and effective bandwidth, advanced packaging output and scrap, reliable available MW, and lead-time investment cohorts. Convert each into common AI-system-equivalent throughput under a fixed workload and hardware generation. Use procurement contracts for realized market prices. Build a measurement model with units, source revisions and uncertainty, then estimate only the identifiable blocks using rolling temporal validation and posterior predictive checks.

For now, avoid extrapolating these quantiles into investment or technology forecasts.
