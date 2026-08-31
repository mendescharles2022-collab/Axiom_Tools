from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_regression_case_blocker_map.py"
spec = importlib.util.spec_from_file_location(
    "validate_regression_case_blocker_map_current", SCRIPT
)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class CurrentDependencyMapTests(unittest.TestCase):
    def test_current_map_is_complete_and_valid(self):
        report = module.validate_dependency_map(
            module.load_json(ROOT / "config" / "regression_cases_v8_202608.json"),
            module.load_json(ROOT / "config" / "blocker_registry_v8.json"),
            module.load_json(
                ROOT / "config" / "regression_case_blocker_map_v8_202608.json"
            ),
        )

        self.assertTrue(report["ok"])
        self.assertEqual(report["mapped_cases"], 28)
        self.assertEqual(report["known_blockers"], 50)
        self.assertEqual(report["controls"], 1)
        self.assertGreater(len(report["used_blockers"]), 0)


if __name__ == "__main__":
    unittest.main()
