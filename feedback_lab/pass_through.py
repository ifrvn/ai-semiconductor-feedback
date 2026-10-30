"""Transparent task-to-system cost transmission model.

Input component weights are sourced separately; all intervention parameters and
system-wide weights are *illustrative*, not fitted causal coefficients.

C = [(1-r-f)*system_fixed + r*accelerator_BOM + f*R&D_burden] / useful_throughput
with system_fixed further partitioned into non-chip components.
Careful: cost accounts are disjoint; yield improvements enter only their
respective manufacturing factor, not a second general cost reduction term.
"""
from __future__ import annotations

import csv
import math
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Mapping

RAW = Path(__file__).resolve().parents[1] / "data/raw/epoch_component_shares_2024q1_2025q4.csv"
COMPONENTS = ("memory", "logic", "packaging", "auxiliary")


def component_shares(period: str = "2025-Q4", path: Path = RAW) -> dict[str, float]:
    """Source-derived accelerator component mix; NOT full data-center TCO."""
    with path.open(encoding="utf-8", newline="") as file:
        rows = [r for r in csv.DictReader(file) if r["period"] == period]
    result = {row["component"]: float(row["share_pct"])/100 for row in rows}
    if set(result) != set(COMPONENTS):
        raise ValueError(f"Invalid or missing component mix for {period}")
    if any(not math.isfinite(v) or v < 0 for v in result.values()):
        raise ValueError("Component shares must be finite and nonnegative")
    if abs(sum(result.values())-1) > 0.0002:
        raise ValueError("Component shares must total 100% (rounding tolerance)")
    # Normalize published rounded observations (some quarters total 99.99%).
    total = sum(result.values())
    return {k: v/total for k, v in result.items()}


@dataclass(frozen=True)
class CostStructure:
    # Scope: full installed-compute economic unit, not the chip bill of materials.
    # The two shares below are explicitly SCENARIO ASSUMPTIONS, not Epoch measurements.
    accelerator_fraction: float = 0.60
    research_fraction: float = 0.08
    # Residual = non-accelerator fraction; its breakdown is another assumption.
    networking_share_of_residual: float = 0.35
    energy_share_of_residual: float = 0.35

    def validate(self) -> None:
        for value in asdict(self).values():
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError("All cost fractions must lie in [0,1]")
        if self.accelerator_fraction + self.research_fraction > 1:
            raise ValueError("System cost accounts cannot overlap")
        if self.networking_share_of_residual + self.energy_share_of_residual > 1:
            raise ValueError("Residual cost shares cannot overlap")


@dataclass(frozen=True)
class Intervention:
    # Direct cost interventions (fractions saved); no inferred causal estimates.
    memory_savings: float = 0.0
    logic_wafer_savings: float = 0.0
    packaging_savings: float = 0.0
    auxiliary_savings: float = 0.0
    networking_savings: float = 0.0
    energy_savings: float = 0.0
    # Manufacturing yield changes apply within their cost bucket only.
    baseline_logic_yield: float = 0.70
    logic_yield_increase_points: float = 0.0
    baseline_packaging_yield: float = 0.85
    packaging_yield_increase_points: float = 0.0
    # Design productivity is fixed-R&D amortization; critical-path schedule separate.
    design_productivity_multiplier: float = 1.0
    design_share_of_critical_path: float = 0.15
    # Effective throughput bottlenecks for an identical fixed workload.
    compute_speedup: float = 1.0
    memory_bandwidth_speedup: float = 1.0
    network_bandwidth_speedup: float = 1.0
    # In this simplified roofline, each baseline capacity normalized to 1.
    # No speedup from improved cost alone, and no compound double counting.
    
    def validate(self) -> None:
        for name in ("memory_savings","logic_wafer_savings","packaging_savings",
                     "auxiliary_savings","networking_savings","energy_savings",
                     "logic_yield_increase_points","packaging_yield_increase_points",
                     "design_share_of_critical_path"):
            val = getattr(self,name)
            if not math.isfinite(val) or not 0 <= val <= 1:
                raise ValueError(f"{name} must be a fraction in [0,1]")
        for name in ("baseline_logic_yield", "baseline_packaging_yield"):
            val=getattr(self,name)
            if not math.isfinite(val) or not 0 < val <= 1:
                raise ValueError(f"{name} must be a yield in (0,1]")
        if self.baseline_logic_yield + self.logic_yield_increase_points > 1 + 1e-12:
            raise ValueError("Logic yield cannot exceed one")
        if self.baseline_packaging_yield + self.packaging_yield_increase_points > 1 + 1e-12:
            raise ValueError("Packaging yield cannot exceed one")
        for name in ("design_productivity_multiplier","compute_speedup",
                     "memory_bandwidth_speedup","network_bandwidth_speedup"):
            val=getattr(self,name)
            if not math.isfinite(val) or val < 1:
                raise ValueError(f"{name} must be finite and >= 1")


def evaluate(intervention: Intervention = Intervention(), *,
             structure: CostStructure = CostStructure(),
             shares: Mapping[str,float] | None = None) -> dict:
    """Account for costs and workload throughput separately.

    One unit of cost = baseline combined cost; hence no claims about dollars.
    Yield-adjusted *category* ratios are reduced by higher known-good output
    per process input, using a first-order accounting approximation.
    Research productivity affects only the separate R&D account.
    """
    intervention.validate()
    structure.validate()
    shares = component_shares() if shares is None else dict(shares)
    if set(shares) != set(COMPONENTS) or any(
            not math.isfinite(x) or x < 0 for x in shares.values()
        ) or abs(sum(shares.values())-1)>1e-8:
        raise ValueError("Component shares must be a nonnegative distribution")

    logic_yield_factor = intervention.baseline_logic_yield / (
        intervention.baseline_logic_yield+intervention.logic_yield_increase_points)
    package_yield_factor = intervention.baseline_packaging_yield / (
        intervention.baseline_packaging_yield+intervention.packaging_yield_increase_points)
    factors={
        "memory":1-intervention.memory_savings,
        "logic":(1-intervention.logic_wafer_savings)*logic_yield_factor,
        "packaging":(1-intervention.packaging_savings)*package_yield_factor,
        "auxiliary":1-intervention.auxiliary_savings,
    }
    chip_cost = sum(shares[name]*factors[name] for name in COMPONENTS)
    residual = 1-structure.accelerator_fraction-structure.research_fraction
    other_share = 1-structure.networking_share_of_residual-structure.energy_share_of_residual
    infrastructure_cost = residual * (
        other_share
        +structure.networking_share_of_residual*(1-intervention.networking_savings)
        +structure.energy_share_of_residual*(1-intervention.energy_savings))
    research_cost=structure.research_fraction/intervention.design_productivity_multiplier
    total_cost=structure.accelerator_fraction*chip_cost+infrastructure_cost+research_cost
    effective_speedup=min(intervention.compute_speedup,
                          intervention.memory_bandwidth_speedup,
                          intervention.network_bandwidth_speedup)
    unit_effective_cost=total_cost/effective_speedup
    schedule_fraction_saved=intervention.design_share_of_critical_path*(
        1-1/intervention.design_productivity_multiplier)
    return {
        "accelerator_bom_cost_index":chip_cost,
        "installed_cost_index":total_cost,
        "effective_throughput_index":effective_speedup,
        "cost_per_effective_work_index":unit_effective_cost,
        "cost_per_effective_work_reduction_pct":100*(1-unit_effective_cost),
        "critical_path_time_reduction_pct":100*schedule_fraction_saved,
        "accounts":{
            "accelerator_components":{name:structure.accelerator_fraction*shares[name]*factors[name]
                                      for name in COMPONENTS},
            "networking":residual*structure.networking_share_of_residual*(1-intervention.networking_savings),
            "energy":residual*structure.energy_share_of_residual*(1-intervention.energy_savings),
            "other_infrastructure":residual*other_share,
            "research_amortization":research_cost,
        },
        "input_scope":"Epoch component shares plus hypothetical full-system weights and interventions",
    }


def marginal_component_impact(
    component: str, reduction_fraction: float = 0.10, *,
    structure: CostStructure = CostStructure(),
    shares: Mapping[str,float] | None = None,
) -> float:
    """Full-system cost reduction in percentage points from single BOM price cut."""
    if component not in COMPONENTS:
        raise ValueError("Unknown component")
    if not 0 <= reduction_fraction <= 1:
        raise ValueError("Reduction outside [0,1]")
    key={"memory":"memory_savings","logic":"logic_wafer_savings",
         "packaging":"packaging_savings","auxiliary":"auxiliary_savings"}[component]
    result=evaluate(replace(Intervention(),**{key:reduction_fraction}),
                    structure=structure,shares=shares)
    return result["cost_per_effective_work_reduction_pct"]
