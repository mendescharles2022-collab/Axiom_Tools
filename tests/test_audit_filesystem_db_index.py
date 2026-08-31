from __future__ import annotations

import importlib.util
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_filesystem_db_index.py"
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("audit_filesystem_db_index", SCRIPT)
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


def make_spec(sql: str = "SELECT path FROM docs") -> dict:
    return {
        "version": 1,
        "scans": [
            {
                "id": "managed_pdfs",
                "root": "docs",
                "glob": "**/*.pdf",
                "sql": sql,
                "path_column": "path",
            }
        ],
    }


class FilesystemDbIndexAuditTests(unittest.TestCase):
    def test_indexed_file_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            managed = base / "managed"
            managed.mkdir()
            (managed / "a.pdf").write_bytes(b"pdf-a")
            db = base / "test.sqlite3"
            create_db(db, ["a.pdf"])

            report = module.audit_reverse_links(db, make_spec(), {"docs": managed})
            self.assertTrue(report["ok"])
            self.assertEqual(report["summary"]["findings"], 0)
            self.assertEqual(report["results"][0]["physical_files"], 1)

    def test_unindexed_file_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            managed = base / "managed"
            managed.mkdir()
            (managed / "indexed.pdf").write_bytes(b"pdf-a")
            (managed / "orphan.pdf").write_bytes(b"pdf-b")
            db = base / "test.sqlite3"
            create_db(db, ["indexed.pdf"])

            report = module.audit_reverse_links(db, make_spec(), {"docs": managed})
            self.assertFalse(report["ok"])
            findings = report["results"][0]["findings"]
            self.assertTrue(
                any(
                    item["code"] == "UNINDEXED_FILE"
                    and item["path"] == "orphan.pdf"
                    for item in findings
                )
            )

    def test_nested_relative_path_is_matched(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            managed = base / "managed"
            nested = managed / "08-2026" / "cliente"
            nested.mkdir(parents=True)
            (nested / "guia.pdf").write_bytes(b"pdf")
            db = base / "test.sqlite3"
            create_db(db, ["08-2026/cliente/guia.pdf"])

            report = module.audit_reverse_links(db, make_spec(), {"docs": managed})
            self.assertTrue(report["ok"])

    def test_unsafe_db_path_is_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            managed = base / "managed"
            managed.mkdir()
            db = base / "test.sqlite3"
            create_db(db, ["../outside.pdf"])

            report = module.audit_reverse_links(db, make_spec(), {"docs": managed})
            self.assertFalse(report["ok"])
            findings = report["results"][0]["findings"]
            self.assertTrue(any(item["code"] == "UNSAFE_DB_PATH" for item in findings))

    def test_unsafe_glob_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            managed = Path(tmp) / "managed"
            managed.mkdir()
            spec_doc = make_spec()
            spec_doc["scans"][0]["glob"] = "../**/*.pdf"
            with self.assertRaises(module.ReverseLinkAuditError):
                module.normalize_spec(spec_doc, {"docs": managed})

    def test_write_query_is_blocked_and_database_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            managed = base / "managed"
            managed.mkdir()
            db = base / "test.sqlite3"
            create_db(db, ["a.pdf"])

            before = sqlite3.connect(db).execute("SELECT path FROM docs").fetchall()
            report = module.audit_reverse_links(
                db,
                make_spec("DELETE FROM docs RETURNING path"),
                {"docs": managed},
            )
            after = sqlite3.connect(db).execute("SELECT path FROM docs").fetchall()

            self.assertFalse(report["ok"])
            self.assertEqual(report["summary"]["query_errors"], 1)
            self.assertEqual(before, after)

    def test_sha256_is_optional_for_unindexed_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            managed = base / "managed"
            managed.mkdir()
            (managed / "orphan.pdf").write_bytes(b"pdf")
            db = base / "test.sqlite3"
            create_db(db, [])
            spec_doc = make_spec()
            spec_doc["scans"][0]["include_sha256"] = True

            report = module.audit_reverse_links(db, spec_doc, {"docs": managed})
            finding = next(
                item
                for item in report["results"][0]["findings"]
                if item["code"] == "UNINDEXED_FILE"
            )
            self.assertEqual(len(finding["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
