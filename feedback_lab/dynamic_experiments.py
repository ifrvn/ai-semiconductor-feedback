"""Export normalized dynamic scenarios; not forecasts."""
from __future__ import annotations
import argparse
import csv
from dataclasses import asdict
from pathlib import Path
from .dynamic_system import simulate_components, scenarios

def annual_rows(end_year:float=2045.,dt:float=.05)->list[dict]:
    rows=[]
    for name,config in scenarios().items():
        samples=simulate_components(config,end_year=end_year,dt=dt)
        for year in range(2026,int(end_year)+1):
            s=min(samples,key=lambda r:abs(r.year-year))
            if abs(s.year-year)<1e-7:
                rows.append({"scenario":name,**asdict(s)})
    return rows

def main()->None:
    parser=argparse.ArgumentParser(description="Illustrative dynamic component scenarios")
    parser.add_argument("--end-year",type=float,default=2045.)
    parser.add_argument("--dt",type=float,default=.05)
    parser.add_argument("--output",default="results/dynamic_components.csv")
    args=parser.parse_args()
    rows=annual_rows(args.end_year,args.dt)
    if not rows:
        raise ValueError("No whole-year observations")
    dest=Path(args.output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open("w",newline="",encoding="utf-8") as file:
        writer=csv.DictWriter(file,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} hypothetical scenario-year observations to {dest}")
    for row in rows:
        if abs(row["year"]-args.end_year)<1e-7:
            print(f"{row['scenario']}: A={row['A']:.3f}, C={row['C']:.3f}, bottleneck={row['bottleneck']}")

if __name__=="__main__":
    main()
