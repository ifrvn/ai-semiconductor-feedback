"""CLI and deterministic scenario comparisons for manufacturing-to-compute pass-through."""
from __future__ import annotations
import argparse
import csv
import json
from dataclasses import replace
from pathlib import Path
from .pass_through import (CostStructure, Intervention, component_shares,
                           evaluate, marginal_component_impact)
from .experiments import SCENARIOS
from .model import State, simulate

def examples() -> dict:
    shares=component_shares("2025-Q4")
    cases={
        "no_intervention": Intervention(),
        "design_3x_only": Intervention(design_productivity_multiplier=3),
        "logic_process_20pct": Intervention(logic_wafer_savings=.20),
        "memory_20pct": Intervention(memory_savings=.20),
        "balanced_hypothetical": Intervention(
            memory_savings=.10, logic_wafer_savings=.15,
            packaging_savings=.10, logic_yield_increase_points=.05,
            design_productivity_multiplier=2,
            compute_speedup=1.5, memory_bandwidth_speedup=1.2,
            network_bandwidth_speedup=1.1),
    }
    return {name:evaluate(case,shares=shares) for name,case in cases.items()}

def local_sensitivity() -> list[dict]:
    """Hypothetical 10% direct category input savings, fixed cost scope."""
    result=[]
    for period in ("2024-Q1","2025-Q4"):
        shares=component_shares(period)
        for component in shares:
            result.append({"period":period,"component":component,
                           "share_of_chip_bom":shares[component],
                           "system_cost_reduction_pct":marginal_component_impact(
                               component,.10,shares=shares)})
    return result

def bridge_to_simulator(
    intervention: Intervention = Intervention(memory_savings=.20),
    end_year: float=2035,
) -> dict:
    """One-time effective-compute cost shift into existing dynamic model.

    This is not a calibrated forecast, and does not re-estimate gA or alter
    underlying physical capacity or future yearly improvement rates.
    """
    change=evaluate(intervention)["cost_per_effective_work_index"]
    model=SCENARIOS["baseline"]
    reference=simulate(model,end_year=end_year)[-1]
    shock=simulate(model,start=State(C=change),end_year=end_year)[-1]
    return {
        "mode":"one_time_normalized_initial_cost_shock_only",
        "hypothetical_unit_cost_multiplier":change,
        "baseline_A":reference.A,
        "shock_A":shock.A,
        "relative_A_difference_pct":100*(shock.A/reference.A-1),
        "warning":"Not an observed treatment effect or prediction; holding capacity and future feedback parameters unchanged is a simplifying counterfactual.",
    }

def main() -> None:
    parser=argparse.ArgumentParser(description="Illustrative chip-cost-to-AI pass-through analysis")
    parser.add_argument("--output",default="results/transmission.json")
    args=parser.parse_args()
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    report={
        "status":"illustrative, not empirically calibrated",
        "source":"https://epoch.ai/data-insights/ai-chip-component-cost-shares",
        "component_shares_2025q4":component_shares("2025-Q4"),
        "scenarios":examples(),
        "one_at_a_time_sensitivity":local_sensitivity(),
        "one_time_bridge":bridge_to_simulator(),
    }
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for name,row in report["scenarios"].items():
        print(f"{name}: cost per work {row['cost_per_effective_work_index']:.4f}; critical-path reduction {row['critical_path_time_reduction_pct']:.2f}%")
    print(f"Wrote {output}")

if __name__=="__main__":
    main()
