"""Generate deterministic, source-derived assets for the static research dashboard.

No new empirical inputs are downloaded or guessed at build time.
"""
from __future__ import annotations

import json
from pathlib import Path

from feedback_lab.calibration import load_epoch, fit_log_linear, load_sales
from feedback_lab.empirical_validation import report as validation_report
from feedback_lab.sector_experiments import annual_rows as sector_rows
from feedback_lab.dynamic_experiments import annual_rows as hardware_rows
from feedback_lab.uncertainty import run as uncertainty_run

ROOT = Path(__file__).resolve().parents[1]


def build() -> dict:
    quarterly = load_epoch()
    validation = validation_report()
    return {
        "schema": 1,
        "method": "committed observations and deterministic simulations",
        "caveat": "Observational hardware proxy and deliberately uncalibrated hypothetical simulations. Not a forecast.",
        "history": {
            "quarterly": quarterly,
            "trend": fit_log_linear(quarterly),
            "sales": load_sales(),
            "holdout": validation["holdout_2025"],
            "rolling_1q": validation["rolling_1q"],
            "rolling_4q": validation["rolling_4q"],
        },
        "sectors": sector_rows(end_year=2040),
        "hardware": hardware_rows(end_year=2040),
        "uncertainty": uncertainty_run(samples=64, seed=20261030, end_year=2035),
        "sources": {
            "epoch": "https://epoch.ai/data-insights/chip-performance-per-dollar",
            "sia": "https://www.semiconductors.org/global-annual-semiconductor-sales-increase-25-6-to-791-7-billion-in-2025/",
        },
    }


def main() -> None:
    output = ROOT / "site" / "data.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    result = build()
    output.write_text(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Built {output.relative_to(ROOT)} with {len(result['history']['quarterly'])} observed quarters and {len(result['sectors'])} sector scenario-years")


if __name__ == "__main__":
    main()
