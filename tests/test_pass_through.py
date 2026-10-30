import math
import unittest
from dataclasses import replace
from feedback_lab.pass_through import (
    component_shares, CostStructure, Intervention, evaluate,
    marginal_component_impact)
from feedback_lab.transmission import local_sensitivity, examples, bridge_to_simulator

class TransmissionTests(unittest.TestCase):
    def test_source_shares(self):
        shares=component_shares("2025-Q4")
        self.assertAlmostEqual(shares["memory"],0.6342,places=4)
        self.assertAlmostEqual(sum(shares.values()),1,places=12)
        self.assertGreater(shares["memory"],component_shares("2024-Q1")["memory"])

    def test_baseline_and_accounts(self):
        result=evaluate()
        self.assertAlmostEqual(result["cost_per_effective_work_index"],1)
        self.assertAlmostEqual(result["installed_cost_index"],1)
        self.assertAlmostEqual(sum(result["accounts"]["accelerator_components"].values())+
            sum(result["accounts"][k] for k in ("networking","energy","other_infrastructure","research_amortization")),1)

    def test_known_cost_share_transmission(self):
        self.assertAlmostEqual(marginal_component_impact("memory",.10),3.8052,places=3)
        self.assertAlmostEqual(marginal_component_impact("logic",.10),0.7758,places=3)
        self.assertGreater(marginal_component_impact("memory"),marginal_component_impact("logic"))

    def test_fixed_design_not_whole_system_cost(self):
        result=evaluate(Intervention(design_productivity_multiplier=3))
        self.assertAlmostEqual(result["cost_per_effective_work_index"],1-.08*(1-1/3))
        self.assertAlmostEqual(result["critical_path_time_reduction_pct"],10)
        self.assertAlmostEqual(result["accelerator_bom_cost_index"],1)

    def test_roofline_bottleneck_and_no_double_count(self):
        p=Intervention(compute_speedup=4,memory_bandwidth_speedup=1.2,
                       network_bandwidth_speedup=2)
        self.assertAlmostEqual(evaluate(p)["effective_throughput_index"],1.2)
        p=replace(p,logic_wafer_savings=.10,logic_yield_increase_points=.1)
        self.assertLess(evaluate(p)["installed_cost_index"],1)
        self.assertAlmostEqual(evaluate(p)["effective_throughput_index"],1.2)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            evaluate(Intervention(logic_yield_increase_points=.5))
        with self.assertRaises(ValueError):
            evaluate(structure=CostStructure(accelerator_fraction=.9,research_fraction=.2))
        with self.assertRaises(ValueError):
            evaluate(Intervention(compute_speedup=0.5))
        with self.assertRaises(ValueError):
            component_shares("1900-Q1")

    def test_examples(self):
        self.assertEqual(len(local_sensitivity()),8)
        self.assertEqual(len(examples()),5)

    def test_bridge(self):
        report=bridge_to_simulator(end_year=2028)
        self.assertLess(report["hypothetical_unit_cost_multiplier"],1)
        self.assertGreater(report["shock_A"],report["baseline_A"])

if __name__=="__main__":
    unittest.main()
