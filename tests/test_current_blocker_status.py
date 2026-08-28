from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_blocker_statuses.py"
REGISTRY_PATH = ROOT / "config" / "blocker_registry_v8.json"
STATUS_PATH = ROOT / "config" / "blocker_status_v8_current.json"

spec = importlib.util.spec_from_file_location("validate_blocker_statuses", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

REGISTRY = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
STATUS = json.loads(STATUS_PATH.read_text(encoding="utf-8"))


class CurrentBlockerStatusTests(unittest.TestCase):
    def test_current_snapshot_is_complete_and_valid(self):
        report = module.validate_statuses(REGISTRY, STATUS)
        self.assertTrue(report["complete"])
        self.assertEqual(report["submitted"], 50)
        self.assertEqual(report["missing"], [])

    def test_current_snapshot_has_no_false_homologation(self):
        report = module.validate_statuses(REGISTRY, STATUS)
        self.assertEqual(report["homologated"], 0)
        self.assertFalse(report["final_ok"])


if __name__ == "__main__":
    unittest.main()
