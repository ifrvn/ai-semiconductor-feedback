"""Leakage-free temporal validation of observable historical proxies.

No claim to identify AI->chip causal feedback or chip fabrication capacity.
The Epoch proxy is sales-weighted *theoretical accelerator* performance/price,
NOT realized workload throughput or whole-system effective compute economics.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
from .calibration import load_epoch, load_sales, fit_log_linear

def _logs(rows: list[dict]) -> list[float]:
    return [math.log(row["performance_per_usd"]) for row in rows]

def _scores(actual: list[float], predicted: list[float]) -> dict:
    if not actual or len(actual)!=len(predicted):
        raise ValueError("Prediction/actual arrays must be nonempty and aligned")
    errors=[p-a for a,p in zip(actual,predicted)]
    return {"n":len(errors),
            "log_rmse":math.sqrt(sum(x*x for x in errors)/len(errors)),
            "log_mae":sum(abs(x) for x in errors)/len(errors),
            "log_bias":sum(errors)/len(errors),
            "geometric_rmse_factor":math.exp(math.sqrt(sum(x*x for x in errors)/len(errors)))}

def _forecast(train:list[dict], future:list[dict],method:str) -> list[float]:
    y=_logs(train)
    if method=="last_value":
        return [y[-1]]*len(future)
    if method=="historical_drift":
        annual_drift=(y[-1]-y[0])/(train[-1]["time"]-train[0]["time"])
        return [y[-1]+annual_drift*(item["time"]-train[-1]["time"]) for item in future]
    if method=="log_linear":
        fit=fit_log_linear(train)
        return [fit["intercept"]+fit["slope_log_per_year"]*item["time"] for item in future]
    raise ValueError("Unknown forecasting method")

METHODS=("last_value","historical_drift","log_linear")

def temporal_backtest(rows:list[dict],*,min_train:int=4,horizon:int=1)->dict:
    """Expanding windows: fit through t, forecast t+h without intermediate data."""
    if min_train<3 or horizon<1 or len(rows)<min_train+horizon:
        raise ValueError("Insufficient observations for rolling windows")
    if any(b["time"]<=a["time"] for a,b in zip(rows,rows[1:])):
        raise ValueError("Time must be strictly increasing")
    records=[]
    for train_end in range(min_train,len(rows)-horizon+1):
        train=rows[:train_end]
        holdout=[rows[train_end+horizon-1]]
        actual=_logs(holdout)[0]
        row={"origin":train[-1]["quarter"],"target":holdout[0]["quarter"],
             "horizon_quarters":horizon,"train_n":len(train),
             "actual_log_performance_per_usd":actual}
        for method in METHODS:
            row["forecast_"+method]=_forecast(train,holdout,method)[0]
        records.append(row)
    scores={m:_scores([r["actual_log_performance_per_usd"] for r in records],
                      [r["forecast_"+m] for r in records]) for m in METHODS}
    return {"horizon_quarters":horizon,"origin_count":len(records),"scores":scores,
            "predictions":records,
            "best_by_log_rmse":min(METHODS,key=lambda m:scores[m]["log_rmse"])}

def fixed_holdout(rows:list[dict],train_through:str="2024-Q4")->dict:
    cut=next((i+1 for i,r in enumerate(rows) if r["quarter"]==train_through),None)
    if cut is None or cut<3 or cut>=len(rows):
        raise ValueError("Invalid training cutoff")
    training=rows[:cut]
    holdout=rows[cut:]
    actual=_logs(holdout)
    return {"train_end":training[-1]["quarter"],
            "test_start":holdout[0]["quarter"],"test_end":holdout[-1]["quarter"],
            "train_n":len(training),"test_n":len(holdout),
            "scores":{m:_scores(actual,_forecast(training,holdout,m)) for m in METHODS},
            "observed":[{"quarter":r["quarter"],"log_performance_per_usd":a}
                        for r,a in zip(holdout,actual)]}

def sales_diagnostics(rows:list[dict])->dict:
    if len(rows)<2:
        raise ValueError("Need at least two annual revenue observations")
    if any(b["year"]!=a["year"]+1 for a,b in zip(rows,rows[1:])):
        raise ValueError("SIA years must be contiguous")
    growth=[{"year":b["year"],
             "nominal_revenue_growth_pct":100*(b["sales_billion_usd"]/a["sales_billion_usd"]-1)}
            for a,b in zip(rows,rows[1:])]
    return {"n_years":len(rows),"growth":growth,
            "capacity_inferred":False,
            "reason":"Nominal semiconductor revenue is not wafer/HBM/packaging/power capacity."}

def report()->dict:
    rows=load_epoch()
    sales=load_sales()
    return {
        "status":"real_historical_proxy_backtest; structural_model_NOT_calibrated",
        "epoch_source":"https://epoch.ai/data-insights/chip-performance-per-dollar",
        "sia_source":"https://www.semiconductors.org/global-annual-semiconductor-sales-increase-25-6-to-791-7-billion-in-2025/",
        "epoch_measure":"spending-weighted theoretical accelerator bit-operations per dollar (2025 USD)",
        "epoch_observation_count":len(rows),
        "holdout_2025":fixed_holdout(rows),
        "rolling_1q":temporal_backtest(rows,min_train=4,horizon=1),
        "rolling_4q":temporal_backtest(rows,min_train=4,horizon=4),
        "sia_revenue_audit":sales_diagnostics(sales),
        "identified_by_these_data":{
            "observable_price_performance_trend":"Descriptive association only",
            "AI_to_chip_causal_cost_feedback":False,
            "construction_delay_and_capacity_productivity":False,
            "manufacturing_capacity":False,
            "AI_capability_growth":False,
        },
        "validation_limitations":[
            "Same 12 quarterly source-derived grouped points are used in overlapping expanding windows; errors are dependent.",
            "Only 4 holdout quarters, and rolling horizon 4 has few origins.",
            "Time trends are not structural parameters, and cannot identify AI chip feedback.",
            "Epoch relative per-dollar TPP excludes utilization, networking, energy and full-server ownership costs.",
            "SIA nominal sales are not a measured capacity series; no sector-capacity fitting was performed.",
            "No causal identification, statistical confidence intervals or future forecast is implied.",
        ],
    }

def main()->None:
    parser=argparse.ArgumentParser(description="Historical out-of-time validation of AI chip price/performance proxy")
    parser.add_argument("--output",default="results/empirical_validation.json")
    args=parser.parse_args()
    results=report()
    destination=Path(args.output)
    destination.parent.mkdir(parents=True,exist_ok=True)
    destination.write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    for name in ("holdout_2025","rolling_1q","rolling_4q"):
        scores=results[name]["scores"]
        print(f"{name}: "+", ".join(f"{m} RMSE={scores[m]['log_rmse']:.4f}" for m in METHODS))
    print("Structural AI-to-chip coefficient: NOT IDENTIFIED")
    print(f"Wrote {destination}")

if __name__=="__main__":
    main()
