import copy
import json
from pathlib import Path
import unittest

from release_gates import validate


class ReleaseGateTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((Path(__file__).resolve().parents[1] /
            "docs/RELEASE_GATES.json").read_text())

    def test_current_portfolio_does_not_claim_unverified_production_readiness(self):
        reports = validate(self.manifest)
        self.assertEqual(len(reports), 10)
        self.assertTrue(all(not row["production_ready"] and row["pending"] for row in reports))

    def test_forged_readiness_claim_rejected(self):
        self.manifest["projects"][0]["production_ready"] = True
        with self.assertRaises(ValueError):
            validate(self.manifest)

    def test_missing_release_gate_rejected(self):
        self.manifest["projects"][0]["gates"].pop()
        with self.assertRaises(ValueError):
            validate(self.manifest)

    def test_pass_without_evidence_rejected(self):
        self.manifest["projects"][0]["gates"][0]["status"] = "passed"
        with self.assertRaises(ValueError):
            validate(self.manifest)

    def test_duplicate_project_rejected(self):
        self.manifest["projects"].append(copy.deepcopy(self.manifest["projects"][0]))
        with self.assertRaises(ValueError):
            validate(self.manifest)
