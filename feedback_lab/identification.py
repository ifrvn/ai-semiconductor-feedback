"""Transparent 2x2 difference-in-differences diagnostic for future project panels.

This is deliberately NOT run on the evidence ledger: those are incomparable
published summary statistics, not project-level untreated/treated panels.
"""
from __future__ import annotations
from collections import defaultdict
from math import log, sqrt

def did_2x2(rows: list[dict], *, outcome: str, log_outcome: bool=False) -> dict:
    """Two-period treatment-vs-control group mean changes.

    Required columns: unit, treated (bool), post (bool), and outcome value.
    Each unit needs exactly one pre and one post measurement.
    Standard errors intentionally omitted: correct inference must cluster on
    the assignment unit and ideally use an appropriate randomization design.
    """
    by_unit=defaultdict(dict)
    assignment={}
    for r in rows:
        unit=str(r["unit"])
        tr=r["treated"]
        post=r["post"]
        if not isinstance(tr,bool) or not isinstance(post,bool):
            raise ValueError("treated and post must be boolean")
        val=float(r[outcome])
        if log_outcome:
            if val <= 0:
                raise ValueError("Log outcome requires positive observations")
            val=log(val)
        if post in by_unit[unit]:
            raise ValueError("Duplicate unit/period")
        by_unit[unit][post]=val
        if unit in assignment and assignment[unit]!=tr:
            raise ValueError("Treatment assignment changed")
        assignment[unit]=tr
    groups={True:[],False:[]}
    for unit,states in by_unit.items():
        if set(states)!={False,True}:
            raise ValueError("Each unit needs pre and post observations")
        groups[assignment[unit]].append(states[True]-states[False])
    if any(len(x)<2 for x in groups.values()):
        raise ValueError("Require at least 2 units per group; no uncertainty is estimated")
    mean=lambda v: sum(v)/len(v)
    treated_change=mean(groups[True])
    control_change=mean(groups[False])
    return {"estimate":treated_change-control_change,
            "treated_mean_change":treated_change,
            "control_mean_change":control_change,
            "treated_units":len(groups[True]),
            "control_units":len(groups[False]),
            "scale":"log points" if log_outcome else "original outcome units",
            "standard_error":None,
            "limitations":"Requires parallel untreated trends, no anticipation/spillovers, stable measurement and credible assignment; no causal inference guaranteed."}
