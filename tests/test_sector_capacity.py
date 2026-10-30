import unittest
from dataclasses import replace
from feedback_lab.sector_capacity import SectorParams,scenarios,simulate_sectors
from feedback_lab.sector_experiments import annual_rows

class MultiSectorTests(unittest.TestCase):
    def test_baseline(self):
        s=simulate_sectors(end_year=2026.)[0]
        self.assertEqual(s.bottleneck,"hbm")
        self.assertAlmostEqual(s.delivered,.95)
        self.assertAlmostEqual(s.physical_cost,1.)
        self.assertGreaterEqual(s.market_price,s.physical_cost)
    def test_no_technical_cost_progress(self):
        p=SectorParams(natural_cost_progress=(0.,)*4,ai_cost_progress=(0.,)*4)
        self.assertAlmostEqual(simulate_sectors(p,end_year=2035.)[-1].physical_cost,1.)
    def test_build_delay(self):
        p=SectorParams(depreciation=(0.,)*4)
        self.assertEqual(simulate_sectors(p,end_year=2027.)[-1].capacity,p.initial_capacity)
    def test_supply_demand_limit(self):
        p=SectorParams(initial_capacity=(2.,.5,2.,2.),initial_demand=3.)
        s=simulate_sectors(p,end_year=2026.)[0]
        self.assertEqual(s.bottleneck,"hbm")
        self.assertAlmostEqual(s.delivered,.5)
        self.assertGreater(s.scarcity_markup,1.)
    def test_capacity_shock(self):
        a=simulate_sectors(end_year=2032.)[-1]
        b=simulate_sectors(scenarios()["hbm_capacity_breakthrough"],end_year=2032.)[-1]
        self.assertGreater(b.capacity[1],a.capacity[1])
        self.assertAlmostEqual(b.capacity[0],a.capacity[0])
    def test_scarcity_is_not_physical_cost(self):
        p=SectorParams(initial_demand=.05,demand_growth=0.,demand_income_elasticity=0.,
                       natural_cost_progress=(0.,)*4,ai_cost_progress=(0.,)*4)
        s=simulate_sectors(p,end_year=2027.)[-1]
        self.assertAlmostEqual(s.market_price,1.)
    def test_convergence(self):
        a=simulate_sectors(end_year=2034.,dt=.05)[-1]
        b=simulate_sectors(end_year=2034.,dt=.025)[-1]
        self.assertLess(abs(a.A-b.A),.01)
        self.assertLess(abs(a.delivered-b.delivered),.01)
    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            simulate_sectors(SectorParams(investment_weights=(.5,)*4))
        with self.assertRaises(ValueError):
            simulate_sectors(SectorParams(build_delay=(0.,2.,2.,3.)))
        with self.assertRaises(ValueError):
            simulate_sectors(dt=3.)
    def test_export(self):
        self.assertEqual(len(annual_rows(end_year=2028.)),15)

if __name__=="__main__":unittest.main()
