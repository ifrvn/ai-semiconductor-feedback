# Model specification (v0.1)

All default states are normalized and parameters illustrative. Time is in years, derivatives describe annual changes. Euler step `dt=0.05` (18.25 days in approximate calendar terms). Neither a fitted model nor a physical law.

## Variables and auxiliary signals

```text
A: AI capability index                 dimensionless
C: per-effective-compute cost          normalized cost
Q: annual available compute capacity   normalized compute/year
T: commercialization delay             years
B: available investable capital        normalized capital stock
I_A = u_A B; I_Q = u_Q B                annual investment flows
H = min(I_A/C, theta Q)                available AI research compute/year
A_lag = A(t-T(t)); I_Qlag = I_Q(t-T(t))
```

## Equations

```text
dA/dt = eta_A H^alpha (1 + rho A/(A+A_s)) max(0, 1-A/A_max) - delta_A A
dC/dt = -(g_0 + flag_chip * g_A A_lag/(A_s+A_lag)) (C-C_min)
dQ/dt = kappa_Q I_Qlag/C_Q - delta_Q Q
dT/dt = omega_T(T_0-T) - flag_lag * kappa_T A/(A_s+A) (T-T_min)
Revenue = revenue_rate * A * H
dB/dt = s_B Revenue - I_A - I_Q - delta_B B + F(t)
```

Prehistory before 2026 uses constant initial `A` and `I_Q`. Linear interpolation is used within recorded history. When `T` decreases, lookup times shift appropriately. `dt < T_min` prevents querying uncomputed future points. Bounds enforce `C >= C_min`, `T >= T_min`, and positive `A,Q,B` for numerical safety.

## Interpretation

`A` is not an empirically identifiable single scalar without a fixed task suite. `C` should include compute, memory, networking, energy and utilization at the workload level; advertised FLOP/$ is insufficient. `Q` aggregates fabs, packaging and HBM into a single capacity bottleneck. `T` aggregates design-to-production delays. `B` abstracts corporate finance, government spending and investment allocation. Thus, a normalized model can demonstrate mechanisms but **cannot support defensible year-specific predictions without measurement**.

The counterfactual changes only feedback switches, with fixed remaining parameters and external forcing. This identifies a **within-model causal effect**, not an estimated real-world causal effect. Estimate historical confounders before making empirical claims. The rebound term for delay represents independent industry complexity; no-lag-feedback does not mean zero delay.

## Important limitations

1. Capacity-building delays in practice are distributed across cohorts; a delay on investment is a proxy.
2. A realistic capital model requires cash flows, investments, financing, interest rates and sector-level accounting, not the illustrative revenue proxy.
3. Compute-to-capability conversion varies by model scale, algorithms and benchmarks.
4. Parameter interactions, stochastic shocks, policy, energy availability and structural breaks are omitted.
5. Hard floors and a capability ceiling are scenario assumptions, not known universal limits.
6. Cross-scenario differences may reflect assumptions more than observable technological constraints.

## Numerical verification

Run unit tests and halve `dt`; inspect drift. For stiff or strongly delayed regimes, use a dedicated DDE solver and independently verify positivity and conservation rules.
