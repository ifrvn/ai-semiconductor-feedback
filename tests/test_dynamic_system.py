import unittest
from dataclasses import replace
from feedback_lab.dynamic_system import Dynamics, simulate_components, scenarios
from feedback_lab.dynamic_experiments import annual_rows

class DynamicSystemTests(unittest.TestCase):
    def test_normalization(self):
        s=simulate_components(end_year=2026)[0]
        self.assertAlmostEqual(s.C,1.)
        self.assertAlmostEqual(s.effective_speed,1.)
        self.assertAlmostEqual(s.research_compute,.2)

    def test_all_scenarios(self):
        for name,p in scenarios().items():
            states=simulate_components(p,end_year=2035)
            self.assertGreater(states[-1].A,0,name)
            self.assertGreater(states[-1].C,0,name)
            self.assertGreater(states[-1].Q,0,name)
        self.assertEqual(len(annual_rows(end_year=2028)),15)

    def test_no_double_cost_improvement(self):
        p=Dynamics(rates=(0.,)*6,ai_rates=(0.,)*6,
                   throughput_rates=(0.,)*3,ai_throughput_rates=(0.,)*3,
                   power_growth=0.)
        s=simulate_components(p,end_year=2030)[-1]
        self.assertAlmostEqual(s.C,1.)

    def test_memory_vs_energy(self):
        base=simulate_components(scenarios()["baseline"],end_year=2035)[-1]
        memory=simulate_components(scenarios()["memory_breakthrough"],end_year=2035)[-1]
        self.assertLess(memory.memory,base.memory)
        self.assertGreater(memory.memory_speed,base.memory_speed)
        self.assertLess(memory.C,base.C)
        energy=simulate_components(scenarios()["energy_constraint"],end_year=2035)[-1]
        self.assertEqual(energy.bottleneck,"power")
        self.assertLess(energy.effective_speed,base.effective_speed)

    def test_step_convergence(self):
        a=simulate_components(end_year=2032,dt=.05)[-1]
        b=simulate_components(end_year=2032,dt=.025)[-1]
        self.assertLess(abs(a.C-b.C),.002)
        self.assertLess(abs(a.A-b.A),.002)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            simulate_components(Dynamics(memory_price_cut=1))
        with self.assertRaises(ValueError):
            simulate_components(dt=1)
        with self.assertRaises(ValueError):
            simulate_components(end_year=2020)

if __name__=="__main__":
    unittest.main()
