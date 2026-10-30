"""Four-sector investment / capacity / scarcity feedback model (uncalibrated).

Capacities measure normalized compatible AI-compute bundles per year, not wafers
or megawatts. Investment is a flow, capital a stock, with fixed sector delays.
"""
from __future__ import annotations
from dataclasses import dataclass, replace
from math import exp, isfinite

SECTORS=("wafer","hbm","packaging","power")

@dataclass(frozen=True)
class SectorParams:
    initial_capacity: tuple[float,...]=(1.15,.95,1.0,1.1)
    build_delay: tuple[float,...]=(3.,2.5,2.,4.)
    depreciation: tuple[float,...]=(.035,.04,.04,.025)
    capex_productivity: tuple[float,...]=(.13,.17,.18,.11)
    investment_weights: tuple[float,...]=(.27,.29,.26,.18)
    cost_weights: tuple[float,...]=(.28,.38,.16,.18)
    natural_cost_progress: tuple[float,...]=(.045,.025,.035,.01)
    ai_cost_progress: tuple[float,...]=(.035,.015,.025,.005)
    cost_floor: float=.30
    demand_growth: float=.11
    demand_income_elasticity: float=.35
    initial_demand: float=1.
    scarcity_elasticity: float=1.5
    maximum_markup: float=4.
    investment_fraction: float=.36
    expansion_project_financing: float=.75
    capacity_gap_response: float=.8
    maximum_gap_ratio: float=2.
    ai_research_fraction: float=.20
    external_funding: float=.14
    revenue_per_delivery: float=.8
    reinvestment_fraction: float=.45
    capital_decay: float=.05
    ai_ability_gain: float=.16
    ai_compute_exponent: float=.62
    ai_ceiling: float=12.
    ai_decay: float=.01
    chip_feedback: bool=True
    shock_year: float|None=None
    shock_sector: str="hbm"
    shock_multiplier: float=1.

    def validate(self):
        for k in ("initial_capacity","build_delay","depreciation","capex_productivity",
                  "investment_weights","cost_weights","natural_cost_progress","ai_cost_progress"):
            xs=getattr(self,k)
            if len(xs)!=4 or not all(isfinite(v) for v in xs):
                raise ValueError(f"{k} requires four finite values")
        if min((*self.initial_capacity,*self.build_delay,*self.capex_productivity))<=0:
            raise ValueError("Capacity, delay and investment conversion must be positive")
        if min((*self.depreciation,*self.investment_weights,*self.cost_weights,
                *self.natural_cost_progress,*self.ai_cost_progress))<0:
            raise ValueError("Shares and rates must be nonnegative")
        if abs(sum(self.investment_weights)-1)>1e-8 or abs(sum(self.cost_weights)-1)>1e-8:
            raise ValueError("Both share vectors must sum to 1")
        for k in ("cost_floor","demand_growth","demand_income_elasticity","initial_demand",
                  "scarcity_elasticity","maximum_markup","investment_fraction",
                  "ai_research_fraction","external_funding","revenue_per_delivery",
                  "reinvestment_fraction","capital_decay","expansion_project_financing",
                  "capacity_gap_response","maximum_gap_ratio","ai_ability_gain",
                  "ai_compute_exponent","ai_ceiling","ai_decay","shock_multiplier"):
            v=getattr(self,k)
            if not isfinite(v) or v<0:
                raise ValueError(f"{k} must be nonnegative and finite")
        if not 0<self.cost_floor<=1 or self.initial_demand<=0 or self.maximum_markup<1:
            raise ValueError("Bad price floor, demand or markup")
        if self.investment_fraction+self.ai_research_fraction>1:
            raise ValueError("Annual capital allocation exceeds available stock")
        if self.shock_sector not in SECTORS:
            raise ValueError("Unknown shock sector")
        if self.shock_year is not None and not isfinite(self.shock_year):
            raise ValueError("Shock year must be finite")

@dataclass(frozen=True)
class SectorState:
    year:float
    A:float
    B:float
    capacity:tuple[float,...]
    component_cost:tuple[float,...]
    requested_demand:float
    delivered:float
    bottleneck:str
    physical_cost:float
    market_price:float
    scarcity_markup:float
    investment:float
    ai_research_compute:float

def delayed(history:list[tuple[float,tuple[float,...]]],target:float,index:int)->float:
    # No commitments before the first actual investment date. Never linearly\n    # interpolate between a synthetic prehistory zero and first real commitment.
    if len(history) < 2 or target < history[1][0]: return 0.
    for j in range(1,len(history)):
        t1,v1=history[j]
        if target<=t1:
            t0,v0=history[j-1]
            w=(target-t0)/(t1-t0)
            return v0[index]*(1-w)+v1[index]*w
    return history[-1][1][index]

def simulate_sectors(p:SectorParams=SectorParams(), *, end_year:float=2045.,
                     start_year:float=2026.,dt:float=.05)->list[SectorState]:
    p.validate()
    if not 0<dt<min(p.build_delay) or end_year<start_year:
        raise ValueError("Invalid timestep or horizon")
    year=start_year
    A=B=1.
    capacities=list(p.initial_capacity)
    costs=[1.]*4
    # initial pre-history and contemporaneous investment at t0
    history=[(start_year-max(p.build_delay)-1,(0.,)*4)]
    shock_done=False
    output=[]
    while True:
        demand=p.initial_demand*exp(p.demand_growth*(year-start_year))*B**p.demand_income_elasticity
        cap=min(capacities)
        delivered=min(demand,cap)
        bottleneck=SECTORS[capacities.index(cap)]
        physical=sum(w*x for w,x in zip(p.cost_weights,costs))
        markup=min(p.maximum_markup,max(1.,(demand/max(cap,1e-12))**p.scarcity_elasticity))
        price=physical*markup
        # Internal investment reduces B; project financing is spent directly.
        investment=p.investment_fraction*B+p.expansion_project_financing
        pressures=[min(p.maximum_gap_ratio,max(0.,demand/max(c,1e-12)-1.))
                   for c in capacities]
        scores=[w*(1.+p.capacity_gap_response*g)
                for w,g in zip(p.investment_weights,pressures)]
        total_score=sum(scores)
        commitments=tuple(investment*s/total_score for s in scores)
        research=min(p.ai_research_fraction*B/max(price,1e-12),delivered)
        output.append(SectorState(year,A,B,tuple(capacities),tuple(costs),demand,
                                  delivered,bottleneck,physical,price,markup,
                                  investment,research))
        if year>=end_year-1e-10:break
        history.append((year,commitments))
        step=min(dt,end_year-year)
        lagged=[delayed(history,year-p.build_delay[i],i) for i in range(4)]
        signal=A/(2+A) if p.chip_feedback else 0.
        dA=p.ai_ability_gain*research**p.ai_compute_exponent*max(0,1-A/p.ai_ceiling)-p.ai_decay*A
        # Revenue proxy depends on physical deliveries, not hypothetical demand.
        dB=p.external_funding+p.reinvestment_fraction*p.revenue_per_delivery*delivered-(
            p.investment_fraction+p.ai_research_fraction+p.capital_decay)*B
        for i in range(4):
            capacities[i]=max(1e-10,capacities[i]+step*(
                p.capex_productivity[i]*lagged[i]-p.depreciation[i]*capacities[i]))
            cost_rate=p.natural_cost_progress[i]+p.ai_cost_progress[i]*signal
            costs[i]=p.cost_floor+(costs[i]-p.cost_floor)*exp(-cost_rate*step)
        A=max(1e-10,A+dA*step)
        B=max(1e-10,B+dB*step)
        before=year
        year=round(year+step,10)
        if p.shock_year is not None and not shock_done and before<p.shock_year<=year:
            capacities[SECTORS.index(p.shock_sector)]*=p.shock_multiplier
            shock_done=True
        if not all(isfinite(v) for v in (A,B,*capacities,*costs)):
            raise ArithmeticError("Non-finite state")
    return output

def scenarios()->dict[str,SectorParams]:
    base=SectorParams()
    return {
        "baseline":base,
        "no_ai_chip_feedback":replace(base,chip_feedback=False),
        "hbm_capacity_breakthrough":replace(base,shock_year=2032.,shock_sector="hbm",shock_multiplier=1.6),
        "packaging_shortage":replace(base,shock_year=2031.,shock_sector="packaging",shock_multiplier=.65),
        "power_shortage":replace(base,shock_year=2031.,shock_sector="power",shock_multiplier=.65),
    }
