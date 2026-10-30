import runpy
import unittest
from pathlib import Path

class DashboardDataTests(unittest.TestCase):
    def test_export_schema(self):
        namespace=runpy.run_path(str(Path(__file__).resolve().parents[1]/"site/build_data.py"))
        data=namespace["build"]()
        self.assertEqual(data["schema"],1)
        self.assertEqual(len(data["history"]["quarterly"]),12)
        self.assertEqual(len(data["sectors"]),75)
        self.assertEqual(len(data["hardware"]),75)
        self.assertEqual(data["uncertainty"]["samples"],64)
        self.assertEqual(data["history"]["holdout"]["test_n"],4)
        self.assertIn("NOT",data["uncertainty"]["status"])

if __name__=="__main__":
    unittest.main()
