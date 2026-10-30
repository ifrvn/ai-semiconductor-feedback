"""Minimal five-state DDE-like simulator with explicit time-stepping.

History is interpolated at t - T(t). All parameters are illustrative.
This is NOT a validated semiconductor or AI forecasting model.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from math import isfinite
from typing import Callable


@dataclass(frozen=True)
class State:
    year: float = 2026.0
    A: float = 1.0
    C: float = 1.0
    Q: float = 1.0
    T: float = 2.5
    B: float = 1.0


@dataclass(frozen=True)
class Parameters:
    # Investment shares, flow conversion and cap on available production.
    u_ai: float = 0.20
    u_capacity: float = 0.25
    theta: float = 0.65
    # Capability production (no instant self-bootstrapping).
    eta_ai: float = 0.18
    compute_exponent: float = 0.65
    self_improvement: float = 0.30
    ability_scale: float = 2.0
    ability_ceiling: float = 12.0
    decay_ai: float = 0.01
    # Cost dynamics; feedback toggle turns off ONLY AI contribution.
    natural_cost_progress: float = 0.06
    ai_cost_progress: float = 0.08
    min_cost: float = 0.12
    # Capacity changes from lagged investment.
    capacity_efficiency: float = 0.33
    capacity_capex: float = 1.0
    decay_capacity: float = 0.07
    # Commercialization delay and non-AI complexity rebound.
    min_lag: float = 0.75
    lag_ai_efficiency: float = 0.11
    lag_rebound: float = 0.025
    baseline_lag: float = 2.5
    # Capital growth, reinvestment, depreciation, external injection.
    revenue_rate: float = 0.52
    reinvestment_share: float = 0.48
    capital_decay: float = 0.05
    external_capital: float = 0.10
    # Counterfactual switches
    ai_chip_feedback: bool = True
    ai_lag_feedback: bool = True

    def validate(self) -> None:
        for key, val in vars(self).items():
            if isinstance(val, bool):
                continue
            if not isfinite(val):
                raise ValueError(f"{key} must be finite")
            if val < 0:
                raise ValueError(f"{key} cannot be negative")
        if self.u_ai + self.u_capacity > 1:
            raise ValueError("Investment shares must total at most one")
        if self.min_cost <= 0 or self.capacity_capex <= 0:
            raise ValueError("Costs must be positive")
        if self.ability_scale <= 0 or self.ability_ceiling <= 1:
            raise ValueError("Ability scale and ceiling invalid")
        if self.min_lag <= 0 or self.baseline_lag < self.min_lag:
            raise ValueError("Delay bounds invalid")

def _sample(history: list[tuple[float, float]], when: float) -> float:
    """Piecewise linear history, constant prehistory before first point."""
    if when <= history[0][0]:
        return history[0][1]
    for i in range(1, len(history)):
        t1, v1 = history[i]
        if when <= t1:
            t0, v0 = history[i-1]
            w = (when-t0)/(t1-t0)
            return v0 + w*(v1-v0)
    return history[-1][1]


def simulate(
    params: Parameters = Parameters(),
    *,
    start: State = State(),
    end_year: float = 2045.0,
    dt: float = 0.05,
    external_capital_fn: Callable[[float], float] | None = None,
) -> list[State]:
    """Forward Euler with lagged signals sampled from time history.

    dt must be smaller than the minimum modeled delay, ensuring causal
    lookups. Halving dt is recommended as a convergence check.
    """
    params.validate()
    if dt <= 0 or dt >= params.min_lag:
        raise ValueError("dt must lie between 0 and min_lag")
    if end_year < start.year:
        raise ValueError("end_year must not precede start")
    if min(start.A, start.C, start.Q, start.B) <= 0:
        raise ValueError("Initial A, C, Q and B must be positive")
    if start.T < params.min_lag:
        raise ValueError("Initial T must respect min_lag")
    out = [start]
    a_history = [(start.year, start.A)]
    iq_history = [(start.year, params.u_capacity * start.B)]
    s = start
    while s.year < end_year - 1e-10:
        h = min(dt, end_year - s.year)
        lag_a = _sample(a_history, s.year - s.T)
        lag_iq = _sample(iq_history, s.year - s.T)
        ai_inv = params.u_ai * s.B
        capacity_inv = params.u_capacity * s.B
        compute = min(ai_inv/s.C, params.theta*s.Q)
        ability_multiplier = 1 + params.self_improvement*s.A/(params.ability_scale+s.A)
        dA = (params.eta_ai*compute**params.compute_exponent*ability_multiplier
              *max(0, 1-s.A/params.ability_ceiling) - params.decay_ai*s.A)
        progress = params.natural_cost_progress
        if params.ai_chip_feedback:
            progress += params.ai_cost_progress*lag_a/(params.ability_scale+lag_a)
        dC = -progress*(s.C-params.min_cost)
        dQ = params.capacity_efficiency*lag_iq/params.capacity_capex - params.decay_capacity*s.Q
        dT = params.lag_rebound*(params.baseline_lag-s.T)
        if params.ai_lag_feedback:
            dT -= params.lag_ai_efficiency*s.A/(params.ability_scale+s.A)*(s.T-params.min_lag)
        # Revenue proxy, not observed industry profit; capital flows are annual.
        revenue = params.revenue_rate*s.A*compute
        extra = (params.external_capital if external_capital_fn is None
                 else external_capital_fn(s.year))
        dB = params.reinvestment_share*revenue-ai_inv-capacity_inv-params.capital_decay*s.B+extra
        s = State(year=round(s.year+h, 10),
                  A=max(1e-10, s.A+h*dA),
                  C=max(params.min_cost, s.C+h*dC),
                  Q=max(1e-10, s.Q+h*dQ),
                  T=max(params.min_lag, s.T+h*dT),
                  B=max(1e-10, s.B+h*dB))
        if not all(isfinite(v) for v in (s.A,s.C,s.Q,s.T,s.B)):
            raise ArithmeticError("Model diverged; inspect parameters")
        out.append(s)
        a_history.append((s.year,s.A))
        iq_history.append((s.year,capacity_inv))
    return out


def yearly(states: list[State]) -> list[State]:
    """Select states nearest integer calendar years without resimulation."""
    out = []
    for year in range(round(states[0].year), round(states[-1].year)+1):
        nearest = min(states, key=lambda s: abs(s.year-year))
        if abs(nearest.year-year) < 1e-6:
            out.append(nearest)
    return out
