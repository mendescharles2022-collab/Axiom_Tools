from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_regression_case_blocker_map.py"
spec = importlib.util.spec_from_file_location("validate_regression_case_blocker_map", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def registry() -> dict:
    return {
        "version": 1,
        "required_cases": [
            {"case_id": f"C{i:02d}", "number": i, "client": f"Cliente {i}", "mechanism": "x", "expected_result": "ok"}
            for i in range(1, 29)
        ],
    }


def blocker_registry() -> dict:
    return {
        "version": 1,
        "blockers": [{"id": f"B{i:02d}", "title": "x"} for i in range(1, 51)],
    }


def dependency_map() -> dict:
    return {
        "version": 1,
        "audit": "V8",
        "cases": [
            {"case_id": f"C{i:02d}", "blockers": [f"B{((i - 1) % 50) + 1:02d}"], "gate": "prova causal"}
            for i in range(1, 29)
        ],
        "controls": [{"case_id": "CTRL-X", "blockers": ["B29"], "gate": "controle"}],
    }


class DependencyMapTests(unittest.TestCase):
    def test_valid_map_covers_all_cases(self):
        report = module.validate_dependency_map(registry(), blocker_registry(), dependency_map())
        self.assertTrue(report["ok"])
        self.assertEqual(report["mapped_cases"], 28)
        self.assertEqual(report["controls"], 1)

    def test_unknown_blocker_is_rejected(self):
        doc = dependency_map()
        doc["cases"][0]["blockers"] = ["B99"]
        with self.assertRaises(module.DependencyMapError):
            module.validate_dependency_map(registry(), blocker_registry(), doc)

    def test_duplicate_case_is_rejected(self):
        doc = dependency_map()
        doc["cases"][-1]["case_id"] = "C01"
        with self.assertRaises(module.DependencyMapError):
            module.validate_dependency_map(registry(), blocker_registry(), doc)

    def test_duplicate_blocker_in_case_is_rejected(self):
        doc = dependency_map()
        doc["cases"][0]["blockers"] = ["B01", "B01"]
        with self.assertRaises(module.DependencyMapError):
            module.validate_dependency_map(registry(), blocker_registry(), doc)

    def test_missing_gate_is_rejected(self):
        doc = dependency_map()
        doc["cases"][0]["gate"] = ""
        with self.assertRaises(module.DependencyMapError):
            module.validate_dependency_map(registry(), blocker_registry(), doc)


if __name__ == "__main__":
    unittest.main()
