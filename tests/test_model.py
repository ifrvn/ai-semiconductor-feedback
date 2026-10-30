import unittest
from dataclasses import replace
from feedback_lab.model import Parameters, State, simulate, yearly
from feedback_lab.experiments import compare, counterfactual, sensitivity

class ModelTests(unittest.TestCase):
    def test_state_bounded_and_finite(self):
        p=Parameters()
        rows=simulate(p,end_year=2035)
        self.assertAlmostEqual(rows[-1].year,2035)
        for s in rows:
            self.assertGreater(s.A,0)
            self.assertGreaterEqual(s.C,p.min_cost)
            self.assertGreater(s.Q,0)
            self.assertGreaterEqual(s.T,p.min_lag)
            self.assertGreater(s.B,0)

    def test_parameter_validation(self):
        with self.assertRaises(ValueError):
            Parameters(u_ai=0.9,u_capacity=0.5).validate()
        with self.assertRaises(ValueError):
            simulate(dt=1.0)
        with self.assertRaises(ValueError):
            simulate(end_year=2020)

    def test_feedback_counterfactual(self):
        variants=counterfactual(end_year=2036)
        self.assertEqual(len(variants),3)
        self.assertGreaterEqual(variants["full_feedback"][-1].A,
                                variants["no_chip_feedback"][-1].A)
        self.assertLessEqual(variants["full_feedback"][-1].C,
                             variants["no_chip_feedback"][-1].C)

    def test_time_step_convergence(self):
        fine=simulate(end_year=2034,dt=0.025)[-1]
        coarse=simulate(end_year=2034,dt=0.05)[-1]
        self.assertLess(abs(fine.A-coarse.A),0.02)

    def test_experiments(self):
        self.assertEqual(set(compare(end_year=2028)),{"conservative","baseline","accelerated"})
        self.assertEqual(len(sensitivity(end_year=2028)),18)
        self.assertEqual(len(yearly(simulate(end_year=2028))),3)

if __name__=="__main__":
    unittest.main()
