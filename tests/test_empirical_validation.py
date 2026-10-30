import math
import unittest
from feedback_lab.calibration import load_epoch,load_sales
from feedback_lab.empirical_validation import (report,temporal_backtest,
    fixed_holdout,sales_diagnostics,_forecast,_scores)

class EmpiricalValidationTests(unittest.TestCase):
    def test_real_data_splits(self):
        rows=load_epoch()
        x=fixed_holdout(rows)
        self.assertEqual((x["train_n"],x["test_n"]),(8,4))
        self.assertEqual(x["train_end"],"2024-Q4")
        self.assertEqual(x["test_start"],"2025-Q1")
        self.assertEqual(set(x["scores"]),{"last_value","historical_drift","log_linear"})

    def test_expanding_window_has_no_future_in_training(self):
        rows=load_epoch()
        for horizon,expected in ((1,8),(4,5)):
            x=temporal_backtest(rows,horizon=horizon)
            self.assertEqual(x["origin_count"],expected)
            for r in x["predictions"]:
                self.assertLess(r["origin"],r["target"])
                self.assertGreaterEqual(r["train_n"],4)

    def test_future_mutation_does_not_change_past_forecast(self):
        rows=load_epoch()
        original=_forecast(rows[:8],rows[8:9],"log_linear")
        altered=[dict(x) for x in rows]
        altered[8]["performance_per_usd"]=99999.
        self.assertEqual(original,_forecast(altered[:8],altered[8:9],"log_linear"))

    def test_methods_and_metrics(self):
        rows=load_epoch()
        self.assertAlmostEqual(_forecast(rows[:8],rows[8:9],"last_value")[0],
                               math.log(rows[7]["performance_per_usd"]))
        self.assertAlmostEqual(_scores([0.,1.],[0.,2.])["log_rmse"],math.sqrt(.5))
        with self.assertRaises(ValueError):
            _forecast(rows[:8],rows[8:9],"invalid")
        with self.assertRaises(ValueError):
            _scores([],[])
        with self.assertRaises(ValueError):
            temporal_backtest(rows[:4],horizon=4)

    def test_sales_scope_and_report(self):
        sales=sales_diagnostics(load_sales())
        self.assertFalse(sales["capacity_inferred"])
        result=report()
        self.assertEqual(result["epoch_observation_count"],12)
        self.assertFalse(result["identified_by_these_data"]["AI_to_chip_causal_cost_feedback"])
        for model in result["rolling_1q"]["scores"].values():
            self.assertTrue(math.isfinite(model["log_rmse"]))

if __name__=="__main__":
    unittest.main()
