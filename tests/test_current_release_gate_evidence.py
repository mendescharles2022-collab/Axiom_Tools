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
        self.assertIn("github-actions:run/33446425395", evidence)
        self.assertIn("result:338-tests-OK", evidence)
        self.assertIn("powershell-smoke:POWERSHELL_B06_SMOKE_OK", evidence)
        self.assertIn("causal-map:28-of-28", evidence)
        self.assertIn(
            "commit:49b9093fcd3060f020dd3dfbb7eee58d2913a7bf",
            evidence,
        )
        self.assertIn("artifact:v8-release-preflight#9778186417", evidence)
        self.assertIn(
            "artifact-sha256:3e7d358b201025096378ba505b35fbd237c38c76f52f8c0cf69a921e6d9a7d42",
            evidence,
        )
        for gate_id in gate.REQUIRED_EVIDENCE_GATES:
            if gate_id == "CI_TOOLING":
                continue
            self.assertEqual(report["gates"][gate_id]["status"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
