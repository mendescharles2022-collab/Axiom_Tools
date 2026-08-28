from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_current_preflight as preflight  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CurrentPreflightTests(unittest.TestCase):
    def test_current_preflight_reflects_blocked_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "preflight"
            summary = preflight.build_current_preflight(ROOT, output)

            self.assertFalse(summary["final_ok"])
            self.assertEqual(summary["blockers_homologated"], 0)
            self.assertEqual(summary["regression_pass"], 0)
            self.assertEqual(summary["evidence_pass"], 1)
            self.assertEqual(summary["evidence_required"], 10)
            self.assertFalse(summary["release_ready"])
            self.assertFalse(summary["build_ok"])

    def test_current_preflight_creates_three_expected_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "preflight"
            preflight.build_current_preflight(ROOT, output)
            names = sorted(path.name for path in output.iterdir())
            self.assertEqual(
                names,
                [
                    "PREFLIGHT_SUMMARY.json",
                    "REGRESSION_RESULTS_CURRENT.json",
                    "V8_RELEASE_GATE_PREFLIGHT.json",
                ],
            )
            report = json.loads((output / "V8_RELEASE_GATE_PREFLIGHT.json").read_text(encoding="utf-8"))
            self.assertFalse(report["final_ok"])

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "preflight"
            output.mkdir()
            sentinel = output / "sentinel.txt"
            sentinel.write_text("keep\n", encoding="utf-8")

            with self.assertRaises(preflight.CurrentPreflightError):
                preflight.build_current_preflight(ROOT, output)

            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")

    def test_preflight_does_not_mutate_canonical_inputs(self):
        files = [
            ROOT / "config" / "blocker_registry_v8.json",
            ROOT / "config" / "blocker_status_v8_current.json",
            ROOT / "config" / "regression_cases_v8_202608.json",
            ROOT / "config" / "release_identity.toml",
            ROOT / "config" / "release_gate_evidence_v8_current.json",
        ]
        before = {str(path): sha256(path) for path in files}

        with tempfile.TemporaryDirectory() as tmp:
            preflight.build_current_preflight(ROOT, Path(tmp) / "preflight")

        after = {str(path): sha256(path) for path in files}
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
