# Phase 5: Multi-sector capacity, investment and scarcity

**Status: exploratory, uncalibrated structural simulation.** This extends but does not silently replace the earlier `dynamic_system.py` simulation. It has four separately financed sectors: advanced wafer fabrication, HBM, advanced packaging, and grid/power infrastructure.

## Reality check / evidence

SEMI's [2026-10-13 300mm fab outlook](https://www.semi.org/en/taxonomy/term/46781) projected **US$149 billion 2026** worldwide 300mm front-end fab equipment spending, and 13 fabs/lines beginning operations or shipping first silicon in 2026 versus 23 in 2027. These are industry-wide *forecasts*, not direct observations of AI accelerator deliveries. Earlier [SEMI memory outlook 2026-06-29](https://www.semi.org/en/semi-press-release/semi-projects-300mm-memory-equipment-investment-to-surpass-50-billion-dollars-in-2026) projected 300mm memory investments of $52bn for 2026 and $57bn for 2027. **These dollar values are contextual only; no attempt is made to convert them into normalized model capacity.** Memory output also covers non-HBM products.

## Structural representation

All states use illustrative normalized values with time in years. `q_i` is a **compatible annual AI-compute bundle capacity** contributed by each stage (not wafers per month, packages/year or MW; those require engineering conversion).

```text
i in {wafer, HBM, packaging, power}
I_i(t) = investment_fraction * B(t) * allocation_i
dq_i/dt = productivity_i * I_i(t-delay_i) - depreciation_i*q_i
dc_i/dt = -(g0_i + feedback_on*gAI_i*A/(2+A))*(c_i-cost_floor)

required_demand(t) = initial_demand*exp(demand_growth*time)*B^income_elasticity
deliveries(t) = min(required_demand(t), min_i(q_i))
physical_unit_cost(t) = sum_i(cost_weight_i*c_i)
scarcity_markup = min(maximum_markup, max(1, (demand/min_i(q_i))^elasticity))
market_price(t) = physical_unit_cost(t)*scarcity_markup
research_compute(t) = min(ai_research_fraction*B/market_price, deliveries)
dA/dt = ability_gain*research_compute^exponent*(1-A/A_ceiling)_+ - ai_decay*A
dB/dt = external_funding + reinvest_fraction*revenue_per_delivery*deliveries
        - (investment_fraction + ai_research_fraction + capital_decay)*B
```

Delayed capital commitments only become capacity once the full corresponding sector delay has passed. Pre-2026 investment commitments are **zero**, rather than fabricated historical capital stocks. Construction delays are fixed; AI cost progress affects physical per-unit component costs only. Scarcity affects the **market purchase price**, not physical production costs or the delivered supply count. Therefore scarcity does not create extra physical output.

The four cost weights and capital shares are synthetic scenario parameters. `physical_unit_cost` is an illustrative amortized normalized cost proxy; costs of a newly built plant are not consistently linked to `capex_productivity` yet, which is a limitation.

## Run and inspect

```bash
python -m feedback_lab.sector_experiments --output results/sector_capacity.csv
python -m unittest discover -s tests -v
```

The CSV provides each year's `A`, `B`, requested demand, delivered output, physical unit cost, market price, scarcity multiplier, investment spending, four capacities, four per-unit costs and the active supply bottleneck.

Scenarios:
- baseline
- no AI-to-chip cost feedback (AI-to-capability remains as modeled)
- one-time 2032 HBM capacity expansion
- 2031 packaging capacity shock
- 2031 power capacity shock

These are **counterfactual thought experiments**, not real 2031/2032 event predictions.

## Identification and limitations

- Real sectors produce different goods and power, so the common 'bundle' throughput metric is deliberately simplified; complementarity, inventories, redundancy, yields and substitution are omitted.
- Price response is an assumed scarcity function, not a market equilibrium fitted to bids or procurement contracts. The markup is capped only for numerical regularization.
- Capital spending is funded from an abstract stock, so the model does not yet include debt, interest, cash-flow timing, investment commitments on balance sheets, lead-time distributions, inventory, forward contracts or capex price inflation.
- No calibrated technology or AI-tool adoption coefficients are available; the current sector gAI parameters must NOT be described as observed causal effects.
- Price and R&D learning effects are separated to avoid double counting. A future joint architecture should reconcile this model with component-resolved performance gains and remove redundant cost state variables.
- Future calibration needs sector-specific wafer-start capacity, HBM supply converted to standardized bandwidth/capacity, package throughput, MW of dependable delivered power, lagged capex cohorts, and realized procurement prices rather than generic sales revenue.

## Recommended model audit

Check time step halving (0.05 vs 0.025 years), sector capacity conservation, shock isolation, and whether the announced bottleneck is the minimum capacity. Sensitivity to cost shares, capex delays, AI-feedback elasticities and investment allocation should be run before interpretation.
