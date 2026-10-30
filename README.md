# AI–Semiconductor Feedback Lab

A reproducible **exploratory** Python model of the co-evolution of AI capabilities, effective compute cost, semiconductor capacity, commercialization delay, and investable capital.

> **Research caveat:** All default coefficients and starting values are *illustrative and uncalibrated*. The outputs are scenarios, **not** forecasts for 2030–2045. No causal effect of AI on semiconductor R&D is assumed to have been empirically established.

## Model

Five states (normalized except delay):

- `A`: AI capability index (higher is better)
- `C`: price per unit of effective computation (lower is better)
- `Q`: annual deliverable effective-compute capacity
- `T`: commercialization lag in years
- `B`: investable capital stock

Flows: `I_A = u_A B`, `I_Q = u_Q B`; usable AI R&D compute `H = min(I_A/C, theta*Q)`. AI-driven chip improvements use **past AI capability** `A(t-T(t))`; capacity investment uses **past committed investment** `I_Q(t-T(t))`. Delay histories are interpolated linearly. The delay for capacity is a deliberately simplified proxy for factory build-out, not a full vintage-capital model.

The model applies finite lower bounds to cost and lag; a stage-specific capability ceiling; depreciation; and a capacity bottleneck. Its equations and assumptions are documented in [docs/model.md](docs/model.md).

## Quick start

Requires Python 3.11+; no dependencies for simulation, CSV export, testing, or sensitivity runs.

```bash
python -m feedback_lab simulate --scenario baseline --output results/baseline.csv
python -m feedback_lab compare --output results/comparison.csv
python -m feedback_lab sensitivity --output results/sensitivity.csv
python -m unittest discover -s tests -v
```

Optional visualization:

```bash
pip install -e ".[plot]"
python -m feedback_lab plot --input results/comparison.csv --output results/comparison.png
```

CSV data can be plotted with other tools without installing matplotlib.

## Project layout

- `feedback_lab/model.py`: parameter validation, bounded delay simulation, sampled history
- `feedback_lab/experiments.py`: scenarios, no-feedback counterfactual, one-at-a-time sensitivity
- `feedback_lab/__main__.py`: command-line interface and CSV export
- `tests/`: numerical constraints and counterfactual tests
- `data/README.md`: provenance and empirical calibration plan
- `docs/model.md`: equations, assumptions and limitations

## Historical observations and partial calibration

The repository now includes attributed historical rows from Epoch AI (2023 Q1–2025 Q4 quarterly AI-chip theoretical price-performance) and SIA (2022–2025 global semiconductor sales). These datasets are **not** sufficient to identify the five-state dynamic model's causal parameters.

```bash
python -m feedback_lab.calibration --output results/calibration.json
```

This computes spending-weighted quarterly hardware price-performance, estimates a descriptive log-linear trend, evaluates a 2025 temporal holdout, and generates a JSON report of **identified vs. unidentified** quantities. See [methodology and limitations](docs/calibration.md). Source records retain dates, units and attribution. No observed inputs are fabricated.

## AI-to-chip causal evidence (Phase 2)

An attributed [study evidence ledger](data/evidence/ai_semiconductor_studies.csv) and [methodology note](docs/ai_chip_evidence.md) now distinguish controlled virtual experiments, EDA vendor case studies, industrial predictive validation and production outcomes.

```bash
python -m feedback_lab.evidence --output results/evidence_audit.json
```

The output explicitly flags the sector-wide feedback parameters as **unidentified**. The `feedback_lab.identification.did_2x2` utility provides a paired pre/post comparison for a future project-level treated/control panel (not yet available); it does **not** manufacture effect estimates or statistical confidence.

## Cost transmission from AI-assisted chip R&D (Phase 3)

The [pass-through model](docs/cost_transmission.md) separates source-derived accelerator component costs from **hypothetical** data-center cost shares, yield gains, design-time productivity, and realized workload throughput. It avoids interpreting local EDA gains as industry-wide savings.

```bash
python -m feedback_lab.transmission --output results/transmission.json
```

The report includes disjoint cost accounts, hypothetical interventions, one-at-a-time sensitivity using 2024 vs 2025 component mixes, and a one-time cost-shock bridge into the five-state simulator (explicitly **not calibrated**). Source: [Epoch AI component shares](https://epoch.ai/data-insights/ai-chip-component-cost-shares), 2026-05-21.

## Dynamic chip-component feedback (Phase 4)

The [dynamic component model](docs/dynamic_components.md) integrates separate normalized cost paths for HBM, logic, packaging, auxiliary parts, networking and energy, as well as independent compute/memory/network throughput and power headroom. It **replaces** the aggregate cost differential equation inside this experiment with a derived effective-compute price, preventing duplicate savings. All coefficients are hypothetical.

```bash
python -m feedback_lab.dynamic_experiments --output results/dynamic_components.csv
```

Five scenarios compare baseline trends, removal of AI-to-chip feedback, a hypothetical memory breakthrough, an energy bottleneck, and faster logic progress alone. See [assumptions and limitations](docs/dynamic_components.md). These runs are not empirical forecasts.

## Four-sector capacity, investment and scarcity (Phase 5)

The [four-sector capacity model](docs/sector_capacity.md) separates wafer fabrication, HBM, advanced packaging and power, with independent investment allocation, construction delays, depreciation, supply-constrained deliveries, and a **separate scarcity market-price wedge**. All coefficients and shocks are scenario assumptions, not empirical forecasts.

```bash
python -m feedback_lab.sector_experiments --output results/sector_capacity.csv
```

Compare baseline, no AI-to-chip-cost improvement, HBM capacity expansion, packaging shortage and power shortage. This is a complementary exploratory model, not yet a joint, empirically calibrated integration with the component throughput model.

## Uncertainty and identifiability (Phase 6)

The [uncertainty study](docs/uncertainty.md) draws reproducible, analyst-defined ranges for the four-sector model, runs paired AI-feedback/no-feedback counterfactuals, and reports sensitivity quantiles. **These are not empirical confidence intervals or calibrated forecasts.**

```bash
python -m feedback_lab.uncertainty --samples 200 --seed 20261030 --output results/uncertainty.json
```

## Research agenda

1. Build a provenance-controlled dataset from primary sources, with dated observations, units, inflation adjustment and uncertainty intervals.
2. Separate AI architecture/algorithmic progress from hardware price-performance.
3. Identify causal adoption effects of AI tools in chip design/manufacturing with treatment and control cohorts.
4. Calibrate parameters using historical data and held-out periods.
5. Compare `feedback`, `no-feedback`, and `no-lag-reduction` with matched investments and shocks.
6. Run parameter uncertainty and structural sensitivity analyses before making predictions.

MIT licensed. Contributions should document sources and assumptions; please avoid labeling illustrative scenarios as empirical forecasts.
