# Dynamic component feedback experiments (v0.4)

This is an **uncalibrated illustration**, not a year-specific technology forecast. Unlike the original five-state model, aggregate effective cost **C is derived each step**, never also integrated with an independent decline equation.

## State and cost accounts

A, Q, T and B evolve using the prior model's equations. Each of memory (HBM), logic, packaging, auxiliary chip parts, networking and energy has a separate normalized cost index c_i(t). Four chip component reference shares s_i come from Epoch AI's **2025 Q4** accelerator component spending proportions (not total ownership costs). Full-system fraction r=.60 and fixed amortized research fraction f=.08 are explicitly *hypothetical*. Let z=1-r-f, networking/energy shares of z be n=e=.35.

Cost before workload speed adjustment is:

    total_cost = r * sum_i(s_i*c_i) + z*(n*c_network + e*c_energy + 1-n-e) + f

The throughput/energy/power constraint is:

    v = min(v_compute, v_memory, v_network, v_power)
    C = total_cost / v
    H = min(u_ai*B/C, theta*Q)

Each component follows:

    dc_i/dt = -(g0_i + gAI_i * A(t-T)/(As+A(t-T)))*(c_i-c_floor)

Compute, memory bandwidth and network bandwidth have independent throughput growth rates, with autonomous and lagged AI-driven terms. Power headroom has its own growth and optional constraint drag. The scalar T changes endogenously with AI support. All series start normalized to 1.

AI-to-chip and AI-to-delay feedback can be disabled together. There is no independent aggregate C decline or a second global yield discount. No measured AI-induced improvements are assumed.

## Compare scenarios

```bash
python -m feedback_lab.dynamic_experiments --output results/dynamic_components.csv
python -m unittest discover -s tests -v
```

- **baseline**: hypothetical category-specific improvements.
- **no_ai_chip_feedback**: shut off AI-to-chip improvements, holding investments and direct AI-model self-improvement as in baseline.
- **memory_breakthrough**: one-time assumed 2032 HBM price improvement and bandwidth jump.
- **energy_constraint**: annual power headroom drag; distinct from electricity unit cost.
- **fast_logic_only**: cheaper logic without automatically improving memory bandwidth.

Output includes per-year capability, effective cost, capacity, commercialization lag, capital, six cost accounts, three throughput capacities, power headroom, active limiting channel and training compute. All years and parameters are *demonstration settings*, not validated predictions.

## Important limitations

1. The min-throughput rule is a stylized fixed-workload proxy, not a measured roofline. In particular all baseline channel capacities are normalized to 1, so any small power constraint can become the bottleneck.
2. Power availability is not the same as energy unit price. A faster chip may cost more and draw more power; upgrades and consumption remain exogenous in this version.
3. The fixed 2025 component spending mix cannot predict future product mix, HBM demand or packaging scrap.
4. The Q state is still aggregated; separate wafer/HBM/packaging physical supply capacities and their investment cohorts are not modeled.
5. Historical market revenues do not calibrate these physical capacity parameters; AI-tool productivity evidence does not identify gAI_i.
6. The current model uses explicit Euler steps and linear interpolation of historical lagged states; rerun with half dt as a numerical robustness check.

Next: estimate actual workload cost breakdown, matched AI-aided chip-design gains and per-component causal pass-through. Do not present illustrative scenarios as historical or empirical projections.
