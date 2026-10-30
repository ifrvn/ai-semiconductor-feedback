"""Scenario and matched counterfactual experiments."""
from __future__ import annotations
from dataclasses import replace
from .model import Parameters, State, simulate, yearly

SCENARIOS: dict[str, Parameters] = {
    "conservative": replace(Parameters(), ai_cost_progress=0.03,
                             lag_ai_efficiency=0.05, external_capital=0.07),
    "baseline": Parameters(),
    "accelerated": replace(Parameters(), ai_cost_progress=0.15,
                            lag_ai_efficiency=0.17, external_capital=0.16),
}

def compare(end_year: float = 2045, dt: float = 0.05) -> dict[str, list[State]]:
    return {name: yearly(simulate(p, end_year=end_year, dt=dt))
            for name, p in SCENARIOS.items()}

def counterfactual(params: Parameters = Parameters(), end_year: float = 2045,
                   dt: float = 0.05) -> dict[str, list[State]]:
    # Matched inputs, altered pathways only.
    variants = {
        "full_feedback": params,
        "no_chip_feedback": replace(params, ai_chip_feedback=False, ai_lag_feedback=False),
        "no_lag_feedback": replace(params, ai_lag_feedback=False),
    }
    return {name: yearly(simulate(p, end_year=end_year, dt=dt))
            for name, p in variants.items()}

def sensitivity(params: Parameters = Parameters(), end_year: float = 2045,
                dt: float = 0.05) -> list[dict[str, float | str]]:
    """One-at-a-time ±20% perturbation; structural uncertainty is not captured."""
    fields = ("ai_cost_progress", "lag_ai_efficiency", "eta_ai",
              "capacity_efficiency", "external_capital", "min_cost")
    results: list[dict[str, float | str]] = []
    for field in fields:
        for factor in (0.8, 1.0, 1.2):
            p = replace(params, **{field: getattr(params, field)*factor})
            final = simulate(p, end_year=end_year, dt=dt)[-1]
            results.append({"parameter":field, "factor":factor, "year":final.year,
                            "A":final.A, "C":final.C, "Q":final.Q,
                            "T":final.T, "B":final.B})
    return results
