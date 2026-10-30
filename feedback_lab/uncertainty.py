"""Reproducible *assumption uncertainty*, not statistically calibrated confidence intervals.

Paired counterfactuals use the same parameter draw in both worlds. The model
has no empirical likelihood; ranges are analyst-defined exploratory priors.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
from dataclasses import replace
from pathlib import Path
from statistics import mean
from .sector_capacity import SectorParams, simulate_sectors

# Explicit, broad illustrative bounds. None are posterior credible intervals.
RANGES = {
    "demand_growth": (0.04, 0.18),
    "scarcity_elasticity": (0.5, 2.5),
    "investment_fraction": (0.22, 0.46),
    "ai_research_fraction": (0.10, 0.25),
    "ai_ability_gain": (0.08, 0.24),
    "ai_cost_progress_scale": (0.0, 2.0),
    "construction_delay_scale": (0.7, 1.5),
    "capex_productivity_scale": (0.6, 1.5),
}
FIELDS = ("A", "B", "delivered", "physical_cost", "market_price", "scarcity_markup")

def sample_parameters(rng: random.Random) -> tuple[SectorParams, dict[str, float]]:
    sampled = {name: rng.uniform(lo, hi) for name, (lo, hi) in RANGES.items()}
    p = SectorParams()
    p = replace(
        p,
        demand_growth=sampled["demand_growth"],
        scarcity_elasticity=sampled["scarcity_elasticity"],
        investment_fraction=sampled["investment_fraction"],
        ai_research_fraction=sampled["ai_research_fraction"],
        ai_ability_gain=sampled["ai_ability_gain"],
        ai_cost_progress=tuple(v * sampled["ai_cost_progress_scale"] for v in p.ai_cost_progress),
        build_delay=tuple(v * sampled["construction_delay_scale"] for v in p.build_delay),
        capex_productivity=tuple(v * sampled["capex_productivity_scale"] for v in p.capex_productivity),
    )
    p.validate()
    return p, sampled

def quantile(values: list[float], q: float) -> float:
    if not values or not 0 <= q <= 1:
        raise ValueError("Invalid quantile input")
    ordered=sorted(values)
    pos=(len(ordered)-1)*q
    lo=int(math.floor(pos))
    hi=int(math.ceil(pos))
    return ordered[lo]*(hi-pos)+ordered[hi]*(pos-lo) if lo!=hi else ordered[lo]

def summarize(rows: list[dict]) -> dict:
    result={}
    for field in FIELDS:
        values=[row[field] for row in rows]
        result[field]={"p05":quantile(values,.05),"median":quantile(values,.5),
                       "p95":quantile(values,.95),"mean":mean(values)}
    return result

def run(*, samples: int=100, seed: int=20261030, end_year: float=2035.,
        dt: float=.1) -> dict:
    if not 1 <= samples <= 10000:
        raise ValueError("samples must be between 1 and 10000")
    if not 2026 <= end_year <= 2060:
        raise ValueError("End year outside supported exploratory range")
    rng=random.Random(seed)
    baseline=[]
    no_feedback=[]
    paired=[]
    bottlenecks={}
    for i in range(samples):
        params, assumptions=sample_parameters(rng)
        on=simulate_sectors(params,end_year=end_year,dt=dt)[-1]
        off=simulate_sectors(replace(params,chip_feedback=False),end_year=end_year,dt=dt)[-1]
        b={name:getattr(on,name) for name in FIELDS}
        n={name:getattr(off,name) for name in FIELDS}
        baseline.append(b)
        no_feedback.append(n)
        # Within-draw contrasts preserve shared economic assumptions.
        paired.append({
            "A_relative_change_pct":100*(on.A/off.A-1),
            "market_price_relative_change_pct":100*(on.market_price/off.market_price-1),
            "physical_cost_relative_change_pct":100*(on.physical_cost/off.physical_cost-1),
            "delivered_relative_change_pct":100*(on.delivered/off.delivered-1),
        })
        bottlenecks[on.bottleneck]=bottlenecks.get(on.bottleneck,0)+1
    effects={}
    for key in paired[0]:
        values=[row[key] for row in paired]
        effects[key]={"p05":quantile(values,.05),"median":quantile(values,.5),
                      "p95":quantile(values,.95),"positive_fraction":sum(x>0 for x in values)/samples}
    return {
        "method":"seeded independent uniform assumption sampling with paired counterfactuals",
        "status":"exploratory_sensitivity_NOT_empirical_calibration",
        "seed":seed,"samples":samples,"end_year":end_year,"dt":dt,
        "assumed_ranges":{k:{"min":v[0],"max":v[1]} for k,v in RANGES.items()},
        "baseline":summarize(baseline),
        "no_ai_chip_feedback":summarize(no_feedback),
        "paired_feedback_effects":effects,
        "baseline_bottleneck_fractions":{k:v/samples for k,v in sorted(bottlenecks.items())},
        "limitations":[
            "Uniform independent bounds are analyst choices, not learned parameter distributions.",
            "Quantiles are sensitivity envelopes, NOT 90% confidence or credible intervals.",
            "No joint posterior, likelihood, structural identification or historical validation.",
            "The counterfactual disables only the chip-cost feedback channel.",
            "Paired model effects are conditional on this specific simplified four-sector structure.",
        ],
    }

def main() -> None:
    parser=argparse.ArgumentParser(description="Assumption sensitivity of multi-sector model")
    parser.add_argument("--samples",type=int,default=100)
    parser.add_argument("--seed",type=int,default=20261030)
    parser.add_argument("--end-year",type=float,default=2035.)
    parser.add_argument("--dt",type=float,default=.1)
    parser.add_argument("--output",default="results/uncertainty.json")
    args=parser.parse_args()
    result=run(samples=args.samples,seed=args.seed,end_year=args.end_year,dt=args.dt)
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Saved {result['samples']} paired draws to {out}")
    print("Quantiles reflect assumed parameter ranges; not empirical confidence intervals.")

if __name__=="__main__":
    main()
