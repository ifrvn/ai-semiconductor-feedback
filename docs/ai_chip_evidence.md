# Phase 2 — Evidence for AI-to-semiconductor feedback

**Review date:** 2026-10-30. Evidence below is a *curated evidence ledger*, not a causal-effect meta-analysis. The ledger records published comparisons but deliberately does not combine them into an estimate of the cost-feedback parameter `ai_cost_progress` or lag-feedback parameter `lag_ai_efficiency`.

## Evidence hierarchy and interpretation

| Example | Observation | What is actually measured | Major limitation |
|---|---|---|---|
| Kanarik et al., Nature (2023) | USD 105k best expert human vs USD 52k median hybrid human-first / Bayesian algorithm-last | Virtual plasma-etch **process development cost-to-target** | A controlled virtual process game; not live foundry costs |
| Google / Nature (2021), AlphaChip | Under six hours to produce floorplans matching or exceeding humans on reported metrics | **One physical-design workflow** | Not a whole chip development cycle; independent reproducibility debate matters |
| Synopsys (2023) | ST reports 3× productivity, SK hynix up to 5% die area improvement | Vendor/customer case studies in EDA | Selection, metric definition, no matched controls |
| Xu et al., JMS (2024) | Approximately 17.6% higher efficiency than traditional manual method | Yield ramp-up framework comparison | Does not prove realized sector-level chip cost decline |
| Busch et al., IJPR (2025 online) | Predictive R² on a selected subset up to 0.496 versus full-sample 0.192 | Predictive performance on wafer records | Different evaluation subsets, **not** actual yield improvement |

Source URLs and machine-readable numeric observations live in `data/evidence/ai_semiconductor_studies.csv`. Raw paper claims are not converted to model-wide benefits. The Kanarik comparison has heterogeneous estimands (best individual expert vs distribution median hybrid) and must not be reported as an unbiased average treatment effect.

## Why the structural feedback effect remains unidentifiable

A sector-wide parameter linking AI capability `A` to effective compute cost `C` requires measurements on the *same common economic scale* and enough variation to separate:
- AI-assisted EDA design productivity vs manufacturing yield;
- fabrication/packaging process innovation vs compute utilization;
- time from design start to tape-out vs time from taped-out chip to volume shipment;
- secular technology improvements, product-mix shifts, supply constraints and financial incentives.

Even strong local experimental evidence about a virtual etch game does **not** identify the sector-wide dynamic coefficient `g_A`. A threefold EDA-task speedup cannot be plugged in as a threefold overall cost or two-thirds reduction in commercialization time.

## Proposed identification design (prospective)

Collect a project-level dataset with randomized or staggered AI-tool rollout:
`project_id,team_id,technology_node,process_family,start_date,design_complexity,ai_access_start,ai_usage_intensity,baseline_pdk,baseline_tools,tapeout_date,validation_date,volume_ramp_date,engineering_hours,design_revisions,wafer_yield,defect_rate,tool_cost,other_costs`.

Preferred: randomized access by team/cluster with preregistered outcomes and assignment-based intent-to-treat (ITT), reported alongside take-up rates. If only observational rollout is available, document treatment selection, pretrends and calendar changes; use contemporary staggered-adoption estimators rather than blindly applying two-way fixed effects under heterogeneous treatment timing.

Primary outcome examples:
1. Log(total engineering-hours / accepted design), accounting for rework and quality.
2. Log(real cost to hit a fixed etch/defect/timing target), including test resource costs.
3. Days from validated design start to **qualified production**, not one workflow's run time.
4. Validated yield of comparable wafers at matched node, product and process maturity.

Cluster uncertainty by team/fab/project hierarchy; report attrition, failures, and negative results. The five-state simulation can then incorporate externally estimated task-level elasticities with documented pass-through rates to `C` and `T`; without pass-through evidence, use only bounded scenario ranges.

## Reproducible numerical tools

`python -m feedback_lab.evidence --output results/evidence_audit.json` validates the ledger and reports each study's metrics and cautions without pooling incomparable designs. `feedback_lab.identification` provides a simple paired-change difference-in-differences diagnostic for *future properly collected project panels*, not these published aggregated figures.

**Policy:** do not mistake predictive R², vendor case studies, virtual optimization experiments or workflow speedups for directly measured causal manufacturing cost savings.
