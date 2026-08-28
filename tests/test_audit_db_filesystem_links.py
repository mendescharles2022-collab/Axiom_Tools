from __future__ import annotations

import hashlib
import importlib.util
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_db_filesystem_links.py"
spec = importlib.util.spec_from_file_location("audit_db_filesystem_links", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def write(path: Path, data: bytes = b"x") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def make_db(
    path: Path,
    file_path: str = "a.pdf",
    size: int | None = None,
    sha: str | None = None,
) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE docs(id INTEGER PRIMARY KEY,path TEXT,size INTEGER,sha TEXT)"
    )
    conn.execute(
        "INSERT INTO docs VALUES(1,?,?,?)",
        (file_path, size, sha),
    )
    conn.commit()
    conn.close()


def check_spec(
    *,
    size: bool = False,
    sha: bool = False,
    sql: str = "SELECT id,path,size,sha FROM docs",
) -> dict:
    item = {
        "id": "docs",
        "root": "documents",
        "sql": sql,
        "path_column": "path",
        "id_column": "id",
    }
    if size:
        item["size_column"] = "size"
    if sha:
        item["sha256_column"] = "sha"
    return {"version": 1, "checks": [item]}


class DbFilesystemAuditTests(unittest.TestCase):
    def test_existing_file_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "docs"
            root.mkdir()
            write(root / "a.pdf")
            database = base / "d.sqlite"
            make_db(database)
            report = module.audit_links(
                database,
                check_spec(),
                {"documents": root},
            )
            self.assertTrue(report["ok"])

    def test_missing_file_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "docs"
            root.mkdir()
            database = base / "d.sqlite"
            make_db(database)
            report = module.audit_links(
                database,
                check_spec(),
                {"documents": root},
            )
            self.assertEqual(
                report["results"][0]["findings"][0]["code"],
                "MISSING",
            )

    def test_traversal_flagged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "docs"
            root.mkdir()
            database = base / "d.sqlite"
            make_db(database, "../x")
            report = module.audit_links(
                database,
                check_spec(),
                {"documents": root},
            )
            self.assertEqual(
                report["results"][0]["findings"][0]["code"],
                "UNSAFE_PATH",
            )

    def test_size_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "docs"
            root.mkdir()
            write(root / "a.pdf", b"abc")
            database = base / "d.sqlite"
            make_db(database, "a.pdf", 99)
            report = module.audit_links(
                database,
                check_spec(size=True),
                {"documents": root},
            )
            self.assertEqual(
                report["results"][0]["findings"][0]["code"],
                "SIZE_MISMATCH",
            )

    def test_sha_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "docs"
            root.mkdir()
            write(root / "a.pdf", b"abc")
            database = base / "d.sqlite"
            make_db(database, "a.pdf", None, "0" * 64)
            report = module.audit_links(
                database,
                check_spec(sha=True),
                {"documents": root},
            )
            self.assertEqual(
                report["results"][0]["findings"][0]["code"],
                "SHA256_MISMATCH",
            )

    def test_matching_sha_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "docs"
            root.mkdir()
            data = b"abc"
            write(root / "a.pdf", data)
            expected = hashlib.sha256(data).hexdigest()
            database = base / "d.sqlite"
            make_db(database, "a.pdf", None, expected)
            report = module.audit_links(
                database,
                check_spec(sha=True),
                {"documents": root},
            )
            self.assertTrue(report["ok"])

    def test_write_query_is_blocked_and_db_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "docs"
            root.mkdir()
            write(root / "a.pdf")
            database = base / "d.sqlite"
            make_db(database)
            before = database.read_bytes()
            bad_spec = check_spec(
                sql="UPDATE docs SET path='x' RETURNING id,path,size,sha"
            )
            report = module.audit_links(
                database,
                bad_spec,
                {"documents": root},
            )
            self.assertEqual(report["summary"]["query_errors"], 1)
            self.assertEqual(before, database.read_bytes())

    def test_unknown_root_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "docs"
            root.mkdir()
            with self.assertRaises(module.LinkAuditError):
                module.normalize_spec(
                    check_spec(),
                    {"other": root},
                )


if __name__ == "__main__":
    unittest.main()
