"""Empirical proxy calibration from explicitly attributed historical observations.

Fit log(price-performance) = intercept + slope*time with ordinary least
squares. This is a descriptive hardware proxy, NOT identification of the
structural five-state model or the causal AI-to-semiconductor feedback.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EPOCH = ROOT / "data/raw/epoch_chip_price_performance_2023_2025.csv"
SIA = ROOT / "data/raw/sia_global_sales_2022_2025.csv"


def load_epoch(path: Path = EPOCH) -> list[dict]:
    buckets: dict[str, list[tuple[float, float]]] = {}
    with path.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            period = row["quarter"]
            performance = float(row["performance_per_usd_relative_to_h100_2025"])
            spending = float(row["spending_billion_2025_usd"])
            if performance <= 0 or spending <= 0:
                raise ValueError("Performance and spending must be positive")
            buckets.setdefault(period, []).append((performance, spending))
    points = []
    for period, pairs in sorted(buckets.items()):
        year, quarter = period.split("-Q")
        time = int(year) + (int(quarter) - 0.5) / 4
        total_spend = sum(spend for _, spend in pairs)
        value = sum(perf * spend for perf, spend in pairs) / total_spend
        points.append({"quarter": period, "time": time,
                       "performance_per_usd": value,
                       "implied_unit_cost": 1.0 / value,
                       "spending_billion_2025_usd": total_spend})
    if len(points) < 4:
        raise ValueError("At least four quarterly observations required")
    return points


def fit_log_linear(points: list[dict]) -> dict:
    """OLS on ln(performance/dollar); equal weight per quarter."""
    if len(points) < 3:
        raise ValueError("At least three points required")
    x = [p["time"] for p in points]
    y = [math.log(p["performance_per_usd"]) for p in points]
    xm = sum(x) / len(x)
    ym = sum(y) / len(y)
    sxx = sum((v - xm) ** 2 for v in x)
    if sxx <= 0:
        raise ValueError("Insufficient date variation")
    slope = sum((a-xm)*(b-ym) for a, b in zip(x, y))/sxx
    intercept = ym-slope*xm
    resid = [v-(intercept+slope*t) for t,v in zip(x,y)]
    rmse = math.sqrt(sum(e*e for e in resid)/len(resid))
    return {"slope_log_per_year": slope, "growth_factor_per_year": math.exp(slope),
            "growth_pct_per_year": 100*math.expm1(slope),
            "log_rmse_in_sample": rmse,
            "intercept": intercept, "n": len(points)}


def evaluate_holdout(train: list[dict], test: list[dict]) -> dict:
    model = fit_log_linear(train)
    pred = [model["intercept"] + model["slope_log_per_year"]*p["time"]
            for p in test]
    actual = [math.log(p["performance_per_usd"]) for p in test]
    rmse = math.sqrt(sum((a-b)**2 for a,b in zip(actual,pred))/len(test))
    return {"train_quarters": len(train), "test_quarters": len(test),
            "holdout_log_rmse": rmse,
            "holdout_geometric_error_factor": math.exp(rmse)}


def load_sales(path: Path = SIA) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = [{"year": int(r["year"]),
                 "sales_billion_usd": float(r["global_sales_billion_usd"])}
                for r in csv.DictReader(f)]
    if any(r["sales_billion_usd"] <= 0 for r in rows):
        raise ValueError("Sales must be positive")
    return sorted(rows, key=lambda r:r["year"])


def build_report() -> dict:
    quarterly = load_epoch()
    train, test = quarterly[:8], quarterly[8:]  # 2023–24 / 2025
    all_fit = fit_log_linear(quarterly)
    sales = load_sales()
    yoy = [{"year":b["year"],
            "growth_pct":100*(b["sales_billion_usd"]/a["sales_billion_usd"]-1)}
           for a,b in zip(sales,sales[1:]) if b["year"]==a["year"]+1]
    return {
        "status": "partial_observational_proxy_calibration_only",
        "hardware_price_performance": {
            "metric": "Sales-weighted theoretical bit-operations/s per 2025 USD; no memory, networking, energy or utilization",
            "observations": quarterly,
            "train_2023_2024": fit_log_linear(train),
            "holdout_2025": evaluate_holdout(train,test),
            "full_sample_descriptive_fit": all_fit,
            "published_growth_pct_per_year": 49,
            "published_90pct_range_growth_pct": [36,66],
            "model_mapping": "observable effective-C proxy trend only; NOT g0 or gA",
        },
        "semiconductor_market": {
            "metric": "Global semiconductor sales, nominal USD billion; revenue, NOT capacity Q",
            "observations": sales, "year_over_year": yoy,
        },
        "structural_parameters_identified": [],
        "structural_parameters_not_identified": [
            "ai_cost_progress","lag_ai_efficiency","eta_ai",
            "capacity_efficiency","capital allocation","capex",
            "reinvestment_share","commercialization delay",
            "AI capability mapping","whole-system effective compute cost",
        ],
        "limitations": [
            "Epoch grouped values are rounded; recomputation may differ from source's unrounded regression.",
            "2025 is a single temporal holdout, not an independent sample.",
            "Sales are cyclical and not equivalent to chips manufactured, compute capacity or inflation-adjusted capital.",
            "No observed AI-enabled chip-design treatment/control sample; causal feedback remains unestimated.",
            "Do not use the inferred hardware proxy rate as a calibrated coefficient of the five-state model.",
        ],
        "sources": [
            "https://epoch.ai/data-insights/chip-performance-per-dollar",
            "https://www.semiconductors.org/global-semiconductor-sales-decrease-8-2-in-2023-market-rebounds-late-in-year/",
            "https://www.semiconductors.org/global-semiconductor-sales-increase-19-1-in-2024-double-digit-growth-projected-in-2025/",
            "https://www.semiconductors.org/global-annual-semiconductor-sales-increase-25-6-to-791-7-billion-in-2025/",
        ],
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Historical proxy calibration (not causal model fitting)")
    parser.add_argument("--output", default="results/calibration.json")
    args = parser.parse_args()
    report=build_report()
    output=Path(args.output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    f=report["hardware_price_performance"]["full_sample_descriptive_fit"]
    h=report["hardware_price_performance"]["holdout_2025"]
    print(f"Hardware proxy price/performance CAGR: {f['growth_pct_per_year']:.1f}% (descriptive)")
    print(f"2025 holdout log RMSE: {h['holdout_log_rmse']:.3f}")
    print("Structural AI→chip feedback coefficients: NOT IDENTIFIED")
    print(f"Wrote {output}")

if __name__ == "__main__":
    main()
