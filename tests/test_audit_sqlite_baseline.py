from __future__ import annotations

import hashlib
import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_sqlite_baseline.py"
spec = importlib.util.spec_from_file_location("audit_sqlite_baseline", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def create_valid_db(path: Path) -> None:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys=ON")
    connection.execute("PRAGMA user_version=7")
    connection.execute(
        "CREATE TABLE parent(id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
    )
    connection.execute(
        "CREATE TABLE child("
        "id INTEGER PRIMARY KEY, "
        "parent_id INTEGER NOT NULL REFERENCES parent(id), "
        "value TEXT)"
    )
    connection.execute("CREATE INDEX idx_child_parent ON child(parent_id)")
    connection.execute(
        "CREATE VIEW child_view AS "
        "SELECT c.id, p.name FROM child c JOIN parent p ON p.id=c.parent_id"
    )
    connection.execute("INSERT INTO parent(id,name) VALUES(1,'P')")
    connection.execute(
        "INSERT INTO child(id,parent_id,value) VALUES(1,1,'C')"
    )
    connection.commit()
    connection.close()


class SqliteBaselineAuditTests(unittest.TestCase):
    def test_valid_database_passes_structural_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "valid.sqlite3"
            create_valid_db(db)

            report = module.audit_database(db)

            self.assertTrue(report["summary"]["structural_ok"])
            self.assertTrue(report["summary"]["integrity_ok"])
            self.assertTrue(report["summary"]["foreign_keys_ok"])
            self.assertFalse(report["summary"]["logical_invariants_evaluated"])
            self.assertEqual(report["database"]["user_version"], 7)
            self.assertTrue(report["database"]["opened_read_only"])
            self.assertTrue(report["database"]["query_only"])
            self.assertEqual(report["row_counts"]["parent"], 1)
            self.assertEqual(report["row_counts"]["child"], 1)
            self.assertEqual(report["foreign_keys"]["declared_count"], 1)
            self.assertIn(
                "child_view", {obj["name"] for obj in report["schema"]["objects"]}
            )

    def test_foreign_key_violation_is_detected_even_if_enforcement_was_off(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "broken_fk.sqlite3"
            connection = sqlite3.connect(db)
            connection.execute("PRAGMA foreign_keys=OFF")
            connection.execute("CREATE TABLE parent(id INTEGER PRIMARY KEY)")
            connection.execute(
                "CREATE TABLE child("
                "id INTEGER PRIMARY KEY, "
                "parent_id INTEGER REFERENCES parent(id))"
            )
            connection.execute("INSERT INTO child(id,parent_id) VALUES(1,999)")
            connection.commit()
            connection.close()

            report = module.audit_database(db)

            self.assertTrue(report["summary"]["integrity_ok"])
            self.assertFalse(report["summary"]["foreign_keys_ok"])
            self.assertFalse(report["summary"]["structural_ok"])
            violations = report["foreign_keys"]["violations"]
            self.assertEqual(len(violations), 1)
            self.assertEqual(violations[0]["table"], "child")
            self.assertEqual(violations[0]["parent"], "parent")

    def test_audit_does_not_mutate_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "readonly.sqlite3"
            create_valid_db(db)
            before_hash = file_hash(db)
            before_size = db.stat().st_size

            module.audit_database(db)

            after_hash = file_hash(db)
            self.assertEqual(before_hash, after_hash)
            self.assertEqual(before_size, db.stat().st_size)
            connection = sqlite3.connect(db)
            try:
                self.assertEqual(
                    connection.execute("SELECT COUNT(*) FROM child").fetchone()[0], 1
                )
            finally:
                connection.close()

    def test_invalid_non_sqlite_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "invalid.sqlite3"
            bad.write_text("this is not sqlite", encoding="utf-8")

            with self.assertRaises(module.DatabaseAuditError):
                module.audit_database(bad)

    def test_row_counts_can_be_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "valid.sqlite3"
            create_valid_db(db)

            report = module.audit_database(db, include_row_counts=False)

            self.assertIsNone(report["row_counts"])
            self.assertTrue(report["summary"]["structural_ok"])

    def test_report_does_not_expose_absolute_database_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            db = base / "private-folder" / "valid.sqlite3"
            db.parent.mkdir()
            create_valid_db(db)

            report = module.audit_database(db)
            serialized = json.dumps(report)

            self.assertEqual(report["database"]["name"], "valid.sqlite3")
            self.assertNotIn(str(db.resolve()), serialized)
            self.assertNotIn(str(db.parent.resolve()), serialized)

    def test_schema_hash_is_stable_for_unchanged_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "valid.sqlite3"
            create_valid_db(db)

            first = module.audit_database(db, include_row_counts=False)
            second = module.audit_database(db, include_row_counts=False)

            self.assertEqual(first["schema"]["sha256"], second["schema"]["sha256"])
            self.assertEqual(len(first["schema"]["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
