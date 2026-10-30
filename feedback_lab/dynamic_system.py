"""Component-resolved dynamic feedback simulation; all coefficients illustrative."""
from __future__ import annotations
from dataclasses import dataclass, replace, asdict
from math import exp, isfinite
from .model import Parameters, State, _sample
from .pass_through import CostStructure, component_shares

PARTS=("memory","logic","packaging","auxiliary","networking","energy")

@dataclass(frozen=True)
class Dynamics:
    base: Parameters = Parameters()
    structure: CostStructure = CostStructure()
    # Autonomous cost progress rates by year.
    rates: tuple[float,...] = (.035,.065,.035,.015,.030,.015)
    # Additional AI-driven rates scaled by lagged AI/(scale+lagged AI).
    ai_rates: tuple[float,...] = (.035,.060,.025,.005,.010,0.)
    floor: float = .20
    # compute/memory/network hardware throughput growth rates (annual).
    throughput_rates: tuple[float,...] = (.070,.045,.035)
    ai_throughput_rates: tuple[float,...] = (.025,.020,.008)
    power_growth: float = .025
    power_drag: float = 0.
    breakthrough_year: float | None = None
    memory_price_cut: float = 0.
    memory_bandwidth_jump: float = 1.
    ai_feedback: bool = True

    def validate(self) -> None:
        self.base.validate()
        self.structure.validate()
        if not 0 < self.floor <= 1 or not 0 <= self.memory_price_cut < 1:
            raise ValueError("Invalid floor or shock")
        if self.memory_bandwidth_jump < 1:
            raise ValueError("Bandwidth must not be cut by a breakthrough")
        if len(self.rates)!=6 or len(self.ai_rates)!=6:
            raise ValueError("Six cost category rates required")
        if len(self.throughput_rates)!=3 or len(self.ai_throughput_rates)!=3:
            raise ValueError("Three throughput channel rates required")
        seq=(*self.rates,*self.ai_rates,*self.throughput_rates,
             *self.ai_throughput_rates,self.power_growth,self.power_drag)
        if not all(isfinite(x) for x in seq):
            raise ValueError("Rates must be finite")
        if min((*self.rates,*self.ai_rates,*self.throughput_rates,
                *self.ai_throughput_rates,self.power_growth)) < 0:
            raise ValueError("Progress rates must be nonnegative")
        if self.breakthrough_year is not None and not isfinite(self.breakthrough_year):
            raise ValueError("Breakthrough year must be finite")

@dataclass(frozen=True)
class Snapshot:
    year:float
    A:float
    C:float
    Q:float
    T:float
    B:float
    memory:float
    logic:float
    packaging:float
    auxiliary:float
    networking:float
    energy:float
    compute_speed:float
    memory_speed:float
    network_speed:float
    power_headroom:float
    effective_speed:float
    bottleneck:str
    research_compute:float

def simulate_components(p: Dynamics=Dynamics(), *, end_year:float=2045.,
                        dt:float=.05, start:State=State()) -> list[Snapshot]:
    """Derive C from disjoint component accounts, never integrate a second C equation."""
    p.validate()
    base=p.base
    if dt<=0 or dt>=base.min_lag or end_year<start.year:
        raise ValueError("Invalid dt or end year")
    if min(start.A,start.C,start.Q,start.B)<=0 or start.T<base.min_lag:
        raise ValueError("Invalid initial states")
    if abs(start.C-1)>1e-10:
        raise ValueError("Initial C must equal normalized component cost 1")
    mix=component_shares("2025-Q4")
    factors=[1.]*6
    speeds=[1.]*3
    power=1.
    A,Q,T,B=start.A,start.Q,start.T,start.B
    year=start.year
    a_history=[(year,A)]
    iq_history=[(year,base.u_capacity*B)]
    triggered=False
    rows=[]
    structure=p.structure
    r=structure.accelerator_fraction
    f=structure.research_fraction
    z=1-r-f
    network_weight=structure.networking_share_of_residual
    energy_weight=structure.energy_share_of_residual
    while True:
        channels=(*speeds,power)
        speed=min(channels)
        limiting=("compute","memory","network","power")[channels.index(speed)]
        bom=sum(mix[key]*factors[i] for i,key in enumerate(PARTS[:4]))
        total=(r*bom+z*(network_weight*factors[4]+energy_weight*factors[5]
               +1-network_weight-energy_weight)+f)
        C=total/speed
        H=min(base.u_ai*B/C,base.theta*Q)
        rows.append(Snapshot(year,A,C,Q,T,B,*factors,*speeds,power,speed,limiting,H))
        if year>=end_year-1e-9:
            break
        h=min(dt,end_year-year)
        lag_a=_sample(a_history,year-T)
        lag_inv=_sample(iq_history,year-T)
        influence=lag_a/(base.ability_scale+lag_a) if p.ai_feedback else 0.
        dA=(base.eta_ai*H**base.compute_exponent
            *(1+base.self_improvement*A/(base.ability_scale+A))
            *max(0,1-A/base.ability_ceiling)-base.decay_ai*A)
        dQ=base.capacity_efficiency*lag_inv/base.capacity_capex-base.decay_capacity*Q
        dT=base.lag_rebound*(base.baseline_lag-T)
        if p.ai_feedback and base.ai_lag_feedback:
            dT-=base.lag_ai_efficiency*A/(base.ability_scale+A)*(T-base.min_lag)
        dB=(base.reinvestment_share*(base.revenue_rate*A*H)
            -(base.u_ai+base.u_capacity)*B-base.capital_decay*B+base.external_capital)
        for i in range(6):
            rate=p.rates[i]+p.ai_rates[i]*influence
            factors[i]=p.floor+(factors[i]-p.floor)*exp(-rate*h)
        for i in range(3):
            speeds[i]*=exp((p.throughput_rates[i]+p.ai_throughput_rates[i]*influence)*h)
        power*=exp((p.power_growth-p.power_drag)*h)
        oldyear=year
        year=round(year+h,10)
        if (p.breakthrough_year is not None and not triggered
                and oldyear<p.breakthrough_year<=year):
            factors[0]=max(p.floor,factors[0]*(1-p.memory_price_cut))
            speeds[1]*=p.memory_bandwidth_jump
            triggered=True
        A=max(1e-10,A+h*dA)
        Q=max(1e-10,Q+h*dQ)
        T=max(base.min_lag,T+h*dT)
        B=max(1e-10,B+h*dB)
        if not all(isfinite(v) for v in (A,Q,T,B,power,*factors,*speeds)):
            raise ArithmeticError("Nonfinite dynamic state")
        a_history.append((year,A))
        iq_history.append((year,base.u_capacity*B))
    return rows

def scenarios()->dict[str,Dynamics]:
    baseline=Dynamics()
    return {
        "baseline":baseline,
        "no_ai_chip_feedback":replace(baseline,ai_feedback=False),
        "memory_breakthrough":replace(baseline,breakthrough_year=2032.,
                                      memory_price_cut=.20,memory_bandwidth_jump=1.35),
        "energy_constraint":replace(baseline,power_drag=.07),
        "fast_logic_only":replace(baseline,rates=(.035,.15,.035,.015,.03,.015),
                                  ai_rates=(.035,.12,.025,.005,.01,0.)),
    }
