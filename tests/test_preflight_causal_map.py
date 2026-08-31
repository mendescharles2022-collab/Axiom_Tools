from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_current_preflight as preflight  # noqa: E402


class PreflightCausalMapTests(unittest.TestCase):
    def test_current_preflight_reports_valid_causal_map(self):
        with tempfile.TemporaryDirectory() as tmp:
            summary = preflight.build_current_preflight(
                ROOT, Path(tmp) / "preflight"
            )
            self.assertTrue(summary["causal_map_ok"])
            self.assertEqual(summary["causal_cases_mapped"], 28)
            self.assertEqual(summary["causal_known_blockers"], 50)
            self.assertGreater(summary["causal_used_blockers"], 0)

    def test_invalid_causal_map_blocks_preflight_and_cleans_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            config = repo / "config"
            config.mkdir(parents=True)

            for name in (
                "blocker_registry_v8.json",
                "blocker_status_v8_current.json",
                "regression_cases_v8_202608.json",
                "regression_case_blocker_map_v8_202608.json",
                "release_identity.toml",
                "release_gate_evidence_v8_current.json",
            ):
                shutil.copy2(ROOT / "config" / name, config / name)

            map_path = config / "regression_case_blocker_map_v8_202608.json"
            payload = json.loads(map_path.read_text(encoding="utf-8"))
            payload["cases"][0]["blockers"] = ["B99"]
            map_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

            output = base / "preflight"
            with self.assertRaises(preflight.dependency_map.DependencyMapError):
                preflight.build_current_preflight(repo, output)

            self.assertFalse(output.exists())
            self.assertFalse(output.with_name(output.name + ".partial").exists())


if __name__ == "__main__":
    unittest.main()
