import unittest
from feedback_lab.uncertainty import run, quantile, sample_parameters
import random

class UncertaintyTests(unittest.TestCase):
    def test_quantiles(self):
        self.assertEqual(quantile([1,3,2],0),1)
        self.assertEqual(quantile([1,3,2],.5),2)
        self.assertEqual(quantile([1,3,2],1),3)
        self.assertAlmostEqual(quantile([0,10],.25),2.5)
        with self.assertRaises(ValueError):
            quantile([], .5)

    def test_reproducible_paired_runs(self):
        a=run(samples=8,seed=17,end_year=2028)
        b=run(samples=8,seed=17,end_year=2028)
        self.assertEqual(a,b)
        self.assertEqual(a["samples"],8)
        self.assertAlmostEqual(sum(a["baseline_bottleneck_fractions"].values()),1)
        self.assertIn("NOT_empirical_calibration",a["status"])

    def test_paired_cost_feedback(self):
        result=run(samples=12,seed=99,end_year=2032)
        effects=result["paired_feedback_effects"]
        self.assertLessEqual(effects["physical_cost_relative_change_pct"]["median"],0)
        self.assertAlmostEqual(effects["delivered_relative_change_pct"]["median"],0)
        for v in result["baseline"].values():
            self.assertLessEqual(v["p05"],v["median"])
            self.assertLessEqual(v["median"],v["p95"])

    def test_bounds(self):
        p,draw=sample_parameters(random.Random(1))
        self.assertLessEqual(p.investment_fraction+p.ai_research_fraction,1)
        self.assertGreater(min(p.build_delay),0)
        with self.assertRaises(ValueError):
            run(samples=0)
        with self.assertRaises(ValueError):
            run(end_year=2020)

if __name__=="__main__":
    unittest.main()
