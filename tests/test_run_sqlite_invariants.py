from __future__ import annotations

import importlib.util
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_sqlite_invariants.py"
spec = importlib.util.spec_from_file_location("run_sqlite_invariants", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def make_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        PRAGMA foreign_keys=ON;
        CREATE TABLE parent(id INTEGER PRIMARY KEY, name TEXT NOT NULL);
        CREATE TABLE child(
            id INTEGER PRIMARY KEY,
            parent_id INTEGER NOT NULL REFERENCES parent(id)
        );
        INSERT INTO parent(id,name) VALUES (1,'ok');
        INSERT INTO child(id,parent_id) VALUES (1,1);
        """
    )
    conn.commit()
    conn.close()


def valid_spec(
    sql: str = "SELECT id FROM child WHERE parent_id NOT IN (SELECT id FROM parent)",
):
    return {
        "version": 1,
        "invariants": [
            {"id": "fk.logical", "sql": sql, "severity": "error"}
        ],
    }


class InvariantRunnerTests(unittest.TestCase):
    def test_zero_rows_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "a.sqlite3"
            make_db(db)
            report = module.run_invariants(db, valid_spec())
            self.assertTrue(report["ok"])
            self.assertEqual(report["summary"]["passed"], 1)

    def test_rows_are_violations(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "a.sqlite3"
            make_db(db)
            report = module.run_invariants(db, valid_spec("SELECT id FROM child"))
            self.assertFalse(report["ok"])
            self.assertEqual(report["results"][0]["sample"][0]["id"], 1)

    def test_warning_does_not_fail_overall(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "a.sqlite3"
            make_db(db)
            spec_data = {
                "version": 1,
                "invariants": [
                    {
                        "id": "warn",
                        "sql": "SELECT id FROM child",
                        "severity": "warning",
                    }
                ],
            }
            report = module.run_invariants(db, spec_data)
            self.assertTrue(report["ok"])
            self.assertEqual(report["summary"]["warnings_failed"], 1)

    def test_duplicate_id_rejected(self):
        with self.assertRaises(module.InvariantError):
            module.normalize_spec(
                {
                    "version": 1,
                    "invariants": [
                        {"id": "x", "sql": "SELECT 1 WHERE 0"},
                        {"id": "x", "sql": "SELECT 1 WHERE 0"},
                    ],
                }
            )

    def test_unsupported_version_rejected(self):
        with self.assertRaises(module.InvariantError):
            module.normalize_spec(
                {
                    "version": 2,
                    "invariants": [{"id": "x", "sql": "SELECT 1 WHERE 0"}],
                }
            )

    def test_write_sql_is_blocked_and_database_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "a.sqlite3"
            make_db(db)
            before = db.read_bytes()
            spec_data = {
                "version": 1,
                "invariants": [
                    {
                        "id": "write",
                        "sql": (
                            "WITH q AS (SELECT 1) "
                            "UPDATE parent SET name='bad' WHERE id=1 RETURNING id"
                        ),
                    }
                ],
            }
            report = module.run_invariants(db, spec_data)
            self.assertFalse(report["ok"])
            self.assertTrue(report["results"][0]["error"])
            self.assertEqual(before, db.read_bytes())
            conn = sqlite3.connect(db)
            self.assertEqual(
                conn.execute("SELECT name FROM parent WHERE id=1").fetchone()[0],
                "ok",
            )
            conn.close()

    def test_pragma_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "a.sqlite3"
            make_db(db)
            report = module.run_invariants(db, valid_spec("PRAGMA user_version"))
            self.assertFalse(report["ok"])
            self.assertTrue(report["results"][0]["error"])

    def test_programmatic_spec_is_normalized(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "a.sqlite3"
            make_db(db)
            report = module.run_invariants(
                db,
                {
                    "version": 1,
                    "invariants": [{"id": "x", "sql": "SELECT 1 WHERE 0"}],
                },
            )
            self.assertTrue(report["ok"])


if __name__ == "__main__":
    unittest.main()
