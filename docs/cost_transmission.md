# Cost transmission model (phase 3, exploratory)

**Scope and caveat.** This deliberately separates an observed *accelerator component mix* from assumed *full-system cost shares*. It is a bookkeeping/sensitivity model, not an empirical estimate of AI-induced cost reductions or a complete total-cost-of-ownership calculator.

## Source

[Epoch AI, Venkat Somala, 2026-05-21](https://epoch.ai/data-insights/ai-chip-component-cost-shares), under CC BY. Data: `data/raw/epoch_component_shares_2024q1_2025q4.csv`.

| Bucket | 2024 Q1 | 2025 Q4 |
|---|---:|---:|
| HBM memory | 51.87% | 63.42% |
| Logic die | 14.16% | 12.93% |
| Advanced packaging | 18.89% | 14.82% |
| Other components | 15.08% | 8.83% |

These percentages refer to **aggregated accelerator-component expenditure across four vendors** (Nvidia, AMD, Google, Amazon), **not** unit-level costs for a fixed chip, nor a full AI data center. Their changes reflect mix and volume as well as prices. They are not estimates of the returns to AI tools. Source values rounded to two decimal places; slight sums are normalized.

## Accounting

Let component shares `s_i` sum to one and `r` be the accelerator-component share of a normalized installed-and-research cost unit. Let `f` be separately accounted amortized R&D cost share and `z=1-r-f` be the remaining non-chip infrastructure share. The default values **r=0.60 and f=0.08 are hypothetical**; no published source is claimed for these weights.

```text
chip_BOM_ratio = Σ_i s_i * category_cost_factor_i
fixed_R&D_ratio = 1 / design_productivity_multiplier
other_ratio = z * (other_share + network_share*(1-network_saving)
                    + energy_share*(1-energy_saving))
installed_cost_ratio = r*chip_BOM_ratio + f*fixed_R&D_ratio + other_ratio
effective_throughput = min(compute_speedup, memory_bandwidth_speedup,
                           network_bandwidth_speedup)
cost_per_effective_work_ratio = installed_cost_ratio / effective_throughput
```

Note: baseline throughput in each channel is normalized to one. This is a *stylized roofline bottleneck*; real workloads need measured arithmetic intensity, memory demand, communication and occupancy. The resulting total unit is **not** a standardized dollar per FLOP. Where a speedup physically requires an additional component or power cost, those extra costs must be added to the appropriate account to avoid optimistic results.

Logic manufacturing and packaging yields are applied **once**, inside their individual component factor:

```text
logic_factor = (1 - wafer_saving) * baseline_logic_yield / improved_logic_yield
packaging_factor = (1 - packaging_saving) * baseline_packaging_yield / improved_packaging_yield
```

These factors are first-order cost-accounting proxies. In reality package failures may scrap HBM and logic together, so the true cross-component pass-through needs an assembly-yield model. **Do not** apply a second whole-system yield multiplier or claim that these equations measure actual foundry unit costs. R&D productivity changes only the non-BOM R&D account; manufacturing gains do not automatically follow.

## Time effects

`critical_path_time_reduction = design_share_of_critical_path*(1-1/productivity_multiplier)`.

This is Amdahl-style time accounting and assumes the specified time share is serial, improvable and on the critical path. The assumption must be established from project schedules, not from general task speedups. In real projects, a 3× faster task that occupies 15% of the critical path yields at most a 10% reduction *under these simplifications*. Fixed amortized R&D cost savings and schedule savings are **different outputs**; do not sum them.

## Reproducible analysis

```bash
python -m feedback_lab.transmission --output results/transmission.json
python -m unittest discover -s tests -v
```

Examples include a 20% logic cost reduction, a 20% HBM reduction, a 3× design-productivity improvement and an explicitly hypothetical combined case. One-at-a-time sensitivity measures changes in the normalized total under 10% price reductions for a single accelerator component.

The bridge experiment uses a **one-time starting effective-compute cost shock** in the five-state simulator, holding all other dynamic parameters fixed. This is not an actual calibrated integration. A production-grade version needs a joint cost/capacity model whose component costs evolve over time and where physical upgrades are paid for, avoiding adding both external cost declines and the same internally modeled AI-induced declines.

## Example for 2025 Q4 source mix and hypothetical r=60%

At fixed throughput, a *hypothetical* 10% HBM component price reduction yields about `0.60 * 0.6342 * 0.10 = 3.8052%` lower combined cost; a 10% logic die reduction yields `0.60 * 0.1293 * 0.10 = 0.7758%`. The difference is **weighting arithmetic**, not evidence that AI will reduce HBM prices by 10%.

## Next identification and validation steps

1. Replace r, f, network/energy weights with workload-specific infrastructure amortization and operational data.
2. Model wafer area/defect density, packaging assembly yields and cross-component scrap explicitly, with data.
3. Collect AI-tool adoption experiments linked to process/design records and measure causal improvements *per account*.
4. Collect fixed-workload delivered tokens/s, utilization, memory and network bottlenecks, and energy cost to estimate dollars per effective task.
5. Re-estimate causal time/cost pass-through from project design start to qualified shipments using multiple process generations.
6. Propagate source uncertainty and intervention uncertainty; only then claim an empirically calibrated feedback coefficient.
