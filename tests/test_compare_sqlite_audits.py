from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "compare_sqlite_audits.py"
spec = importlib.util.spec_from_file_location("compare_sqlite_audits", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def base_report():
    return {
        "database": {"name": "db.sqlite3", "user_version": 1},
        "integrity": {"ok": True, "rows": ["ok"]},
        "foreign_keys": {"ok": True, "violations": []},
        "schema": {
            "sha256": "A" * 64,
            "objects": [
                {
                    "type": "table",
                    "name": "a",
                    "table": "a",
                    "sql": "CREATE TABLE a(id INTEGER PRIMARY KEY)",
                }
            ],
        },
        "row_counts": {"a": 2},
        "summary": {
            "structural_ok": True,
            "integrity_ok": True,
            "foreign_keys_ok": True,
        },
    }


class CompareSqliteAuditsTests(unittest.TestCase):
    def test_identical_reports_have_no_regression(self):
        before = base_report()
        after = json.loads(json.dumps(before))
        result = module.compare_reports(before, after)
        self.assertTrue(result["summary"]["regression_free"])
        self.assertFalse(result["schema"]["schema_changed"])
        self.assertEqual(result["warnings"], [])

    def test_added_schema_object_requires_review_not_regression(self):
        before = base_report()
        after = json.loads(json.dumps(before))
        after["schema"]["sha256"] = "B" * 64
        after["schema"]["objects"].append(
            {
                "type": "table",
                "name": "b",
                "table": "b",
                "sql": "CREATE TABLE b(id INTEGER)",
            }
        )
        after["row_counts"]["b"] = 0
        result = module.compare_reports(before, after)
        self.assertTrue(result["summary"]["regression_free"])
        self.assertTrue(result["summary"]["requires_review"])
        self.assertEqual(result["schema"]["added_objects"][0]["name"], "b")

    def test_removed_object_is_warning(self):
        before = base_report()
        after = json.loads(json.dumps(before))
        after["schema"]["sha256"] = "C" * 64
        after["schema"]["objects"] = []
        after["row_counts"] = {}
        result = module.compare_reports(before, after)
        self.assertTrue(result["summary"]["regression_free"])
        self.assertTrue(
            any(
                warning["code"] == "SCHEMA_OBJECTS_REMOVED"
                for warning in result["warnings"]
            )
        )

    def test_new_fk_violation_is_regression(self):
        before = base_report()
        after = json.loads(json.dumps(before))
        after["foreign_keys"]["ok"] = False
        after["summary"]["foreign_keys_ok"] = False
        after["summary"]["structural_ok"] = False
        after["foreign_keys"]["violations"] = [
            {"table": "c", "rowid": 1, "parent": "p", "fkid": 0}
        ]
        result = module.compare_reports(before, after)
        self.assertFalse(result["summary"]["regression_free"])
        self.assertEqual(
            result["regressions"][0]["code"], "NEW_FOREIGN_KEY_VIOLATIONS"
        )

    def test_integrity_failure_after_success_is_regression(self):
        before = base_report()
        after = json.loads(json.dumps(before))
        after["summary"]["integrity_ok"] = False
        after["summary"]["structural_ok"] = False
        result = module.compare_reports(before, after)
        self.assertFalse(result["summary"]["regression_free"])
        self.assertTrue(
            any(
                item["code"] == "INTEGRITY_REGRESSION"
                for item in result["regressions"]
            )
        )

    def test_row_decrease_is_warning(self):
        before = base_report()
        after = json.loads(json.dumps(before))
        after["row_counts"]["a"] = 1
        result = module.compare_reports(before, after)
        self.assertTrue(result["summary"]["regression_free"])
        self.assertEqual(result["rows"]["decreases"][0]["delta"], -1)
        self.assertTrue(
            any(
                warning["code"] == "ROW_COUNT_DECREASES"
                for warning in result["warnings"]
            )
        )

    def test_invalid_report_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "invalid.json"
            path.write_text('{"database":{}}', encoding="utf-8")
            with self.assertRaises(module.ComparisonError):
                module.load_report(path)


if __name__ == "__main__":
    unittest.main()
