import math
import unittest
from feedback_lab.calibration import (load_epoch, fit_log_linear, load_sales,
                                      evaluate_holdout, build_report)

class CalibrationTests(unittest.TestCase):
    def test_source_rows_and_order(self):
        rows = load_epoch()
        self.assertEqual(len(rows), 12)
        self.assertEqual(rows[0]["quarter"], "2023-Q1")
        self.assertEqual(rows[-1]["quarter"], "2025-Q4")
        self.assertTrue(all(r["performance_per_usd"] > 0 for r in rows))

    def test_weighting_and_cost_reciprocal(self):
        first = load_epoch()[0]
        expected = (.63*.76 + .80*1.83 + 1.28*1.19)/(.76+1.83+1.19)
        self.assertAlmostEqual(first["performance_per_usd"], expected)
        self.assertAlmostEqual(first["implied_unit_cost"]*expected, 1)

    def test_historical_fit(self):
        rows=load_epoch()
        fit=fit_log_linear(rows)
        self.assertGreater(fit["growth_pct_per_year"], 0)
        self.assertLess(fit["growth_pct_per_year"], 100)
        holdout=evaluate_holdout(rows[:8],rows[8:])
        self.assertTrue(math.isfinite(holdout["holdout_log_rmse"]))
        self.assertEqual(holdout["test_quarters"],4)

    def test_sales_not_capacity(self):
        sales=load_sales()
        self.assertEqual([r["year"] for r in sales],[2022,2023,2024,2025])
        self.assertAlmostEqual(sales[-1]["sales_billion_usd"],791.7)
        report=build_report()
        self.assertEqual(report["structural_parameters_identified"],[])
        self.assertIn("NOT g0",report["hardware_price_performance"]["model_mapping"])

if __name__=="__main__":
    unittest.main()
