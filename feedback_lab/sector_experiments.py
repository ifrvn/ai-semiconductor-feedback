"""Export four-sector dynamic counterfactuals as a self-contained CSV."""
from __future__ import annotations
import argparse,csv
from pathlib import Path
from .sector_capacity import SECTORS,scenarios,simulate_sectors

def annual_rows(end_year:float=2045.,dt:float=.05)->list[dict]:
    result=[]
    for name,params in scenarios().items():
        states=simulate_sectors(params,end_year=end_year,dt=dt)
        for year in range(2026,int(end_year)+1):
            s=min(states,key=lambda x:abs(x.year-year))
            if abs(s.year-year)>1e-7: continue
            row={"scenario":name,"year":s.year,"A":s.A,"B":s.B,
                 "requested_demand":s.requested_demand,"delivered":s.delivered,
                 "bottleneck":s.bottleneck,"physical_cost":s.physical_cost,
                 "market_price":s.market_price,"scarcity_markup":s.scarcity_markup,
                 "investment":s.investment,"ai_research_compute":s.ai_research_compute}
            for i,key in enumerate(SECTORS):
                row[f"capacity_{key}"]=s.capacity[i]
                row[f"component_cost_{key}"]=s.component_cost[i]
            result.append(row)
    return result

def main():
    parser=argparse.ArgumentParser(description="Multi-sector illustrative feedback scenarios")
    parser.add_argument("--end-year",type=float,default=2045.)
    parser.add_argument("--dt",type=float,default=.05)
    parser.add_argument("--output",default="results/sector_capacity.csv")
    args=parser.parse_args()
    data=annual_rows(args.end_year,args.dt)
    if not data: raise ValueError("No whole-year rows")
    path=Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)
    print(f"Wrote {len(data)} scenario/year records to {path}")
    for row in data:
        if abs(row["year"]-args.end_year)<1e-7:
            print(f"{row['scenario']}: A={row['A']:.3f} supply={row['delivered']:.3f} "
                  f"spot-price={row['market_price']:.3f} limiting={row['bottleneck']}")

if __name__=="__main__":
    main()
