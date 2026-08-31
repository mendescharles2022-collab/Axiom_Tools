from __future__ import annotations

import importlib.util
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_db_filesystem_bidirectional.py"
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("audit_db_filesystem_bidirectional", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def create_db(path: Path, rows: list[str]) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.execute("CREATE TABLE docs (id INTEGER PRIMARY KEY, path TEXT NOT NULL)")
        conn.executemany("INSERT INTO docs(path) VALUES (?)", [(value,) for value in rows])
        conn.commit()
    finally:
        conn.close()


def forward_spec() -> dict:
    return {
        "version": 1,
        "checks": [
            {
                "id": "docs_forward",
                "root": "docs",
                "sql": "SELECT id, path FROM docs",
                "path_column": "path",
                "id_column": "id",
            }
        ],
    }


def reverse_spec() -> dict:
    return {
        "version": 1,
        "scans": [
            {
                "id": "docs_reverse",
                "root": "docs",
                "glob": "**/*.pdf",
                "sql": "SELECT path FROM docs",
                "path_column": "path",
            }
        ],
    }


class BidirectionalDbFilesystemAuditTests(unittest.TestCase):
    def test_consistent_database_and_filesystem_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            managed = base / "managed"
            managed.mkdir()
            (managed / "a.pdf").write_bytes(b"a")
            db = base / "test.sqlite3"
            create_db(db, ["a.pdf"])

            report = module.audit_bidirectional(
                db, forward_spec(), reverse_spec(), {"docs": managed}
            )
            self.assertTrue(report["ok"])
            self.assertEqual(report["summary"]["findings"], 0)
            self.assertEqual(report["summary"]["forward_checks"], 1)
            self.assertEqual(report["summary"]["reverse_scans"], 1)

    def test_missing_index_and_missing_file_are_separated(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            managed = base / "managed"
            managed.mkdir()
            (managed / "orphan.pdf").write_bytes(b"orphan")
            db = base / "test.sqlite3"
            create_db(db, ["missing.pdf"])

            report = module.audit_bidirectional(
                db, forward_spec(), reverse_spec(), {"docs": managed}
            )
            self.assertFalse(report["ok"])
            self.assertEqual(report["summary"]["forward_findings"], 1)
            self.assertEqual(report["summary"]["reverse_findings"], 1)
            self.assertEqual(
                report["database_to_filesystem"]["results"][0]["findings"][0]["code"],
                "MISSING",
            )
            self.assertEqual(
                report["filesystem_to_database"]["results"][0]["findings"][0]["code"],
                "UNINDEXED_FILE",
            )

    def test_audit_does_not_mutate_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            managed = base / "managed"
            managed.mkdir()
            (managed / "a.pdf").write_bytes(b"a")
            db = base / "test.sqlite3"
            create_db(db, ["a.pdf"])

            conn = sqlite3.connect(db)
            try:
                before = conn.execute("SELECT id, path FROM docs ORDER BY id").fetchall()
            finally:
                conn.close()

            module.audit_bidirectional(
                db, forward_spec(), reverse_spec(), {"docs": managed}
            )

            conn = sqlite3.connect(db)
            try:
                after = conn.execute("SELECT id, path FROM docs ORDER BY id").fetchall()
            finally:
                conn.close()
            self.assertEqual(before, after)

    def test_reverse_write_query_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            managed = base / "managed"
            managed.mkdir()
            (managed / "a.pdf").write_bytes(b"a")
            db = base / "test.sqlite3"
            create_db(db, ["a.pdf"])
            bad_reverse = reverse_spec()
            bad_reverse["scans"][0]["sql"] = "DELETE FROM docs RETURNING path"

            report = module.audit_bidirectional(
                db, forward_spec(), bad_reverse, {"docs": managed}
            )
            self.assertFalse(report["ok"])
            self.assertEqual(report["summary"]["query_errors"], 1)

            conn = sqlite3.connect(db)
            try:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM docs").fetchone()[0], 1)
            finally:
                conn.close()


if __name__ == "__main__":
    unittest.main()
