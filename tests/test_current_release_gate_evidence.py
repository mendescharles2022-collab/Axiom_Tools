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
        self.assertIn("github-actions:run/33452559940", evidence)
        self.assertIn("result:514-tests-OK", evidence)
        self.assertIn("powershell-smoke:POWERSHELL_B06_SMOKE_OK", evidence)
        self.assertIn(
            "powershell-consumer-smoke:POWERSHELL_B06_CONSUMER_SMOKE_OK",
            evidence,
        )
        self.assertIn("causal-map:28-of-28", evidence)
        self.assertIn(
            "commit:9939b660d17c68c6848cb8d9cb5e24fffefd38dd",
            evidence,
        )
        self.assertIn("artifact:v8-release-preflight#9780276903", evidence)
        self.assertIn(
            "artifact-sha256:511d75258d3f7f28a519708d61407963ef6bf2c0ecf8b74051252464b5432e1f",
            evidence,
        )
        for gate_id in gate.REQUIRED_EVIDENCE_GATES:
            if gate_id == "CI_TOOLING":
                continue
            self.assertEqual(report["gates"][gate_id]["status"], "NOT_RUN")


if __name__ == "__main__":
    unittest.main()
