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
        self.assertEqual({row["id"] for row in reports}, {
            "governed-rag", "monetary-simulator", "argusloop", "evidenceweave",
            "polyglot-relay", "context-atlas", "local-model-workbench",
            "notes-evidence-rag", "assistant-ledger", "rag-recruiter-demos",
            "tracelens", "continuity-router", "sourcegate", "qrcn", "jev-support-desk",
        })
        self.assertTrue(all(not row["production_ready"] and row["pending"] for row in reports))

    def test_inventory_separates_systems_repositories_and_demo_variants(self):
        inventory = self.manifest["inventory"]
        reports = validate(self.manifest)
        self.assertEqual(inventory["system_count"], 14)
        self.assertEqual(inventory["accessible_owned_repository_count"], 9)
        self.assertEqual(inventory["demo_variant_count"], 2)
        self.assertEqual(len(set(inventory["demo_variants"])), 2)
        system_ids = {row["id"] for row in reports} - {inventory["demo_group_id"]}
        self.assertEqual(len(system_ids), inventory["system_count"])
        self.assertIn("jev-support-desk", system_ids)

    def test_jev_acceptance_cannot_be_inferred_from_demo_or_reconstruction(self):
        project = next(row for row in self.manifest["projects"] if row["id"] == "jev-support-desk")
        self.assertFalse(project["production_ready"])
        self.assertEqual(len(project["gates"]), 5)
        self.assertTrue(all(gate["status"] == "pending" for gate in project["gates"]))
        self.assertIn("independently labeled", project["gates"][0]["requirement"])

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
