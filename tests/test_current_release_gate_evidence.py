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
        self.assertIn("github-actions:run/33447254039", evidence)
        self.assertIn("result:371-tests-OK", evidence)
        self.assertIn("powershell-smoke:POWERSHELL_B06_SMOKE_OK", evidence)
        self.assertIn("causal-map:28-of-28", evidence)
        self.assertIn(
            "commit:e51bc61f13bbb21922b295eb57f8794a481962ed",
            evidence,
        )
        self.assertIn("artifact:v8-release-preflight#9778467287", evidence)
        self.assertIn(
            "artifact-sha256:4ce32783f1cd0d4fd2df6300d39d7a7cb3c87e2b4054fdbe3b06c1bfad2e6919",
            evidence,
        )
        for gate_id in gate.REQUIRED_EVIDENCE_GATES:
            if gate_id == "CI_TOOLING":
                continue
            self.assertEqual(report["gates"][gate_id]["status"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
