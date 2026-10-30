"""Audit heterogeneous public evidence without pooling incomparable effect sizes."""
from __future__ import annotations
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LEDGER=ROOT/"data/evidence/ai_semiconductor_studies.csv"
VALID={"controlled_virtual_comparison","peer_reviewed_benchmark",
       "vendor_claim","observational_comparison","observational_predictive_validation"}

def audit(path: Path=LEDGER) -> dict:
    with path.open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    if not rows:
        raise ValueError("Evidence ledger is empty")
    seen=set()
    for row in rows:
        identifier=row["study_id"]
        if not identifier or identifier in seen:
            raise ValueError("Missing or duplicated study ID")
        seen.add(identifier)
        if row["evidence_tier"] not in VALID:
            raise ValueError(f"Unknown evidence tier: {identifier}")
        if not row["source_url"].startswith("https://"):
            raise ValueError(f"Missing verifiable URL: {identifier}")
        for key in ("baseline_value","treatment_value"):
            if row[key]:
                float(row[key])
    kanarik=next(r for r in rows if r["study_id"]=="kanarik2023")
    relative=(float(kanarik["baseline_value"])-float(kanarik["treatment_value"]))/float(kanarik["baseline_value"])
    return {
        "total_studies":len(rows),
        "evidence_tiers":{tier:sum(r["evidence_tier"]==tier for r in rows)
                          for tier in sorted(VALID)},
        "kanarik_virtual_game_comparison":{
            "expert_reference_usd":float(kanarik["baseline_value"]),
            "hybrid_median_usd":float(kanarik["treatment_value"]),
            "relative_cost_reduction_pct":100*relative,
            "warning":"Best expert vs median hybrid in controlled virtual setting; not sector-wide ATE"
        },
        "causal_sector_feedback_identified":False,
        "ai_cost_progress_estimate":None,
        "ai_lag_feedback_estimate":None,
        "study_summaries":[{"study_id":r["study_id"],
                            "domain":r["domain"],"evidence_tier":r["evidence_tier"],
                            "reported_effect":r["reported_effect"],
                            "interpretation":r["interpretation"],"source_url":r["source_url"]}
                           for r in rows],
    }

def main() -> None:
    import argparse
    parser=argparse.ArgumentParser(description="Audit empirical study claims, without meta-analysis")
    parser.add_argument("--output",default="results/evidence_audit.json")
    args=parser.parse_args()
    destination=Path(args.output)
    destination.parent.mkdir(parents=True,exist_ok=True)
    result=audit()
    destination.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"Audited {result['total_studies']} claims; sector-wide feedback: NOT IDENTIFIED")
    print(f"Wrote {destination}")

if __name__=="__main__":
    main()
