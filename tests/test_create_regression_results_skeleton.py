from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import create_regression_results_skeleton as skeleton  # noqa: E402
import validate_regression_results as regression  # noqa: E402


class RegressionSkeletonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry_path = ROOT / "config" / "regression_cases_v8_202608.json"
        cls.registry = regression.load_json(cls.registry_path)

    def test_skeleton_has_exact_28_not_run_cases(self):
        document = skeleton.build_skeleton(self.registry)
        self.assertEqual(len(document["results"]), 28)
        self.assertEqual(
            [item["case_id"] for item in document["results"]],
            [f"C{index:02d}" for index in range(1, 29)],
        )
        self.assertTrue(all(item["status"] == "NOT_RUN" for item in document["results"]))

    def test_skeleton_validates_but_is_not_final(self):
        document = skeleton.build_skeleton(self.registry)
        report = regression.validate_results(self.registry, document, final_mode=False)
        self.assertTrue(report["complete"])
        self.assertFalse(report["final_ok"])
        self.assertEqual(report["status_counts"]["NOT_RUN"], 28)

    def test_registry_hash_is_bound_to_canonical_registry(self):
        document = skeleton.build_skeleton(self.registry)
        expected = regression.canonical_hash(self.registry)
        self.assertEqual(document["registry_sha256"], expected)

    def test_existing_destination_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "results.json"
            path.write_text("original\n", encoding="utf-8")
            with self.assertRaises(skeleton.RegressionSkeletonError):
                skeleton.write_skeleton(path, skeleton.build_skeleton(self.registry))
            self.assertEqual(path.read_text(encoding="utf-8"), "original\n")

    def test_written_skeleton_roundtrips_through_validator(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "results.json"
            skeleton.write_skeleton(path, skeleton.build_skeleton(self.registry))
            loaded = json.loads(path.read_text(encoding="utf-8"))
            report = regression.validate_results(self.registry, loaded, final_mode=False)
            self.assertEqual(report["submitted"], 28)
            self.assertFalse(report["final_ok"])


if __name__ == "__main__":
    unittest.main()
