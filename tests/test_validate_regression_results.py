from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_regression_results.py"
REGISTRY_PATH = ROOT / "config" / "regression_cases_v8_202608.json"

spec = importlib.util.spec_from_file_location("validate_regression_results", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

REGISTRY = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def results(status: str = "PASS", count: int = 28, evidence: bool = True) -> dict:
    registry_hash = module.canonical_hash(REGISTRY)
    return {
        "registry_sha256": registry_hash,
        "results": [
            {
                "case_id": f"C{index:02d}",
                "status": status,
                "evidence": [f"evidence-{index}"] if evidence else [],
            }
            for index in range(1, count + 1)
        ],
    }


class RegressionResultValidatorTests(unittest.TestCase):
    def test_registry_has_exact_28(self):
        metadata = module.validate_registry(REGISTRY)
        self.assertEqual(len(metadata["ids"]), 28)

    def test_all_pass_with_evidence_final_ok(self):
        report = module.validate_results(REGISTRY, results(), True)
        self.assertTrue(report["final_ok"])

    def test_pass_without_evidence_rejected(self):
        with self.assertRaises(module.RegressionValidationError):
            module.validate_results(REGISTRY, results(evidence=False))

    def test_missing_case_detected_nonfinal(self):
        report = module.validate_results(REGISTRY, results(count=27))
        self.assertFalse(report["complete"])
        self.assertEqual(report["missing"], ["C28"])

    def test_missing_case_blocks_final(self):
        with self.assertRaises(module.RegressionValidationError):
            module.validate_results(REGISTRY, results(count=27), True)

    def test_fail_status_blocks_final(self):
        data = results()
        data["results"][0]["status"] = "FAIL"
        with self.assertRaises(module.RegressionValidationError):
            module.validate_results(REGISTRY, data, True)

    def test_registry_hash_mismatch_rejected(self):
        data = results()
        data["registry_sha256"] = "0" * 64
        with self.assertRaises(module.RegressionValidationError):
            module.validate_results(REGISTRY, data)

    def test_duplicate_result_rejected(self):
        data = results()
        data["results"].append(dict(data["results"][0]))
        with self.assertRaises(module.RegressionValidationError):
            module.validate_results(REGISTRY, data)


if __name__ == "__main__":
    unittest.main()
