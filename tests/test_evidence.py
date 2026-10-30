import unittest
from feedback_lab.evidence import audit
from feedback_lab.identification import did_2x2

class EvidenceTests(unittest.TestCase):
    def test_evidence_audit(self):
        report=audit()
        self.assertGreater(report["total_studies"],0)
        self.assertEqual(report["total_studies"],len(report["study_summaries"]))
        self.assertEqual(sum(report["evidence_tiers"].values()),report["total_studies"])
        self.assertFalse(report["causal_sector_feedback_identified"])
        self.assertIsNone(report["ai_cost_progress_estimate"])
        self.assertAlmostEqual(report["kanarik_virtual_game_comparison"]["relative_cost_reduction_pct"],50.47619047619)

    def test_simple_did(self):
        rows=[]
        for treated in (False,True):
            for i in range(3):
                unit=f"{treated}-{i}"
                for post in (False,True):
                    rows.append({"unit":unit,"treated":treated,"post":post,
                        "hours":100+i+(-5 if post else 0)+(-10 if treated and post else 0)})
        result=did_2x2(rows,outcome="hours")
        self.assertAlmostEqual(result["estimate"],-10)
        self.assertIsNone(result["standard_error"])

    def test_reject_unpaired(self):
        with self.assertRaises(ValueError):
            did_2x2([{"unit":"x","treated":True,"post":False,"hours":30}],outcome="hours")

if __name__=="__main__":
    unittest.main()
