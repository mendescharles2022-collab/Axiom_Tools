from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_release_gate as gate  # noqa: E402


class CurrentReleaseGateEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / "config" / "release_gate_evidence_v8_current.json"
        cls.document = json.loads(cls.path.read_text(encoding="utf-8"))

    def test_current_evidence_is_valid_but_not_final(self):
        report = gate.validate_evidence_manifest(self.document)
        self.assertFalse(report["final_ok"])
        self.assertEqual(report["pass_count"], 1)
        self.assertEqual(report["required"], 10)
        self.assertEqual(report["gates"]["CI_TOOLING"]["status"], "PASS")

    def test_current_ci_evidence_is_traceable(self):
        report = gate.validate_evidence_manifest(self.document)
        evidence = report["gates"]["CI_TOOLING"]["evidence"]
        self.assertIn("github-actions:run/33462473281", evidence)
        self.assertIn("result:584-tests-OK", evidence)
        self.assertIn("powershell-smoke:POWERSHELL_B06_SMOKE_OK", evidence)
        self.assertIn(
            "powershell-consumer-smoke:POWERSHELL_B06_CONSUMER_SMOKE_OK",
            evidence,
        )
        self.assertIn(
            "powershell-plan-smoke:POWERSHELL_B06_PLAN_SMOKE_OK",
            evidence,
        )
        self.assertIn(
            "powershell-review-skeleton-smoke:POWERSHELL_B06_REVIEW_SKELETON_SMOKE_OK",
            evidence,
        )
        self.assertIn("causal-map:28-of-28", evidence)
        self.assertIn(
            "commit:100bb40521a80e976a6d78dca8c0e30aad2eed3f",
            evidence,
        )
        self.assertIn("artifact:v8-release-preflight#9783649332", evidence)
        self.assertIn(
            "artifact-sha256:8951579403ccb548511567e6f90d7c04ae3eb9ea1f97f206a5c0c32b4ca8d5b1",
            evidence,
        )
        for gate_id in gate.REQUIRED_EVIDENCE_GATES:
            if gate_id == "CI_TOOLING":
                continue
            self.assertEqual(report["gates"][gate_id]["status"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
