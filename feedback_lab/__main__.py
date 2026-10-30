"""CLI: run simulations, counterfactuals, sensitivity and optional plots."""
import argparse
import csv
from pathlib import Path
from .model import State, yearly, simulate
from .experiments import SCENARIOS, compare, counterfactual, sensitivity

STATE_COLS = ("year", "A", "C", "Q", "T", "B")

def write_csv(path: str, records: list[dict]) -> None:
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

def flatten(groups: dict[str, list[State]]) -> list[dict]:
    return [{"scenario":name, **{col:getattr(s,col) for col in STATE_COLS}}
            for name, states in groups.items() for s in states]

def plot(input_file: str, output: str) -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise SystemExit('Install optional plotting: pip install -e ".[plot]"') from exc
    series = {}
    with open(input_file, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            series.setdefault(row.get("scenario","simulation"), []).append(row)
    fig, ax = plt.subplots()
    for name, rows in series.items():
        ax.plot([float(r["year"]) for r in rows],
                [float(r["A"]) for r in rows], label=name)
    ax.set(xlabel="Year", ylabel="AI capability index (illustrative)")
    ax.legend()
    fig.tight_layout()
    dest=Path(output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(dest,dpi=160)
    plt.close(fig)

def main() -> None:
    parser=argparse.ArgumentParser(description="Exploratory AI–chip feedback simulator")
    sub=parser.add_subparsers(dest="command",required=True)
    for command in ("simulate","compare","counterfactual","sensitivity"):
        p=sub.add_parser(command)
        p.add_argument("--output",default=f"results/{command}.csv")
        p.add_argument("--end-year",type=float,default=2045)
        p.add_argument("--dt",type=float,default=0.05)
        if command=="simulate":
            p.add_argument("--scenario",choices=SCENARIOS,default="baseline")
    p=sub.add_parser("plot")
    p.add_argument("--input",required=True)
    p.add_argument("--output",default="results/chart.png")
    args=parser.parse_args()
    if args.command=="plot":
        plot(args.input,args.output)
        print(args.output)
        return
    if args.command=="simulate":
        rows=flatten({args.scenario:yearly(simulate(SCENARIOS[args.scenario],
                                   end_year=args.end_year,dt=args.dt))})
    elif args.command=="compare":
        rows=flatten(compare(args.end_year,args.dt))
    elif args.command=="counterfactual":
        rows=flatten(counterfactual(end_year=args.end_year,dt=args.dt))
    else:
        rows=sensitivity(end_year=args.end_year,dt=args.dt)
    write_csv(args.output,rows)
    print(f"Wrote {len(rows)} rows to {args.output}")

if __name__=="__main__":
    main()
