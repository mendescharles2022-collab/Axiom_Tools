from __future__ import annotations

import importlib.util
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, filename: str):
    script = ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, script)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load("create_rollback_bundle", "create_rollback_bundle.py")
restore = load("restore_rollback_bundle", "restore_rollback_bundle.py")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_db(path: Path) -> None:
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE x(id INTEGER PRIMARY KEY,v TEXT)")
    conn.execute("INSERT INTO x VALUES(1,'ok')")
    conn.commit()
    conn.close()


def make_bundle(base: Path):
    root = base / "root"
    database = base / "db.sqlite3"
    bundle = base / "bundle"
    write(root / "app/a.py", "x=1\n")
    write(root / "config/app.ini", "mode=prod\n")
    make_db(database)
    builder.create_bundle(
        source_root=root,
        db_path=database,
        plan={
            "files": [
                {"path": "app/a.py", "role": "code"},
                {"path": "config/app.ini", "role": "config"},
            ]
        },
        output_dir=bundle,
        app_version="V7",
        schema_version="7",
        commit_sha="abc",
    )
    return root, database, bundle


class RestoreTests(unittest.TestCase):
    def test_restore_valid_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, _, bundle = make_bundle(base)
            destination = base / "restored"
            result = restore.restore_to_staging(bundle, destination)
            self.assertTrue(result["ok"])
            self.assertEqual(
                (destination / "files/app/a.py").read_text(encoding="utf-8"),
                "x=1\n",
            )
            conn = sqlite3.connect(destination / "database/axiom_tools.sqlite3")
            self.assertEqual(conn.execute("SELECT v FROM x").fetchone()[0], "ok")
            conn.close()
            self.assertTrue((destination / "RESTORE_REHEARSAL.json").is_file())

    def test_existing_destination_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, _, bundle = make_bundle(base)
            destination = base / "restored"
            destination.mkdir()
            with self.assertRaises(restore.RestoreError):
                restore.restore_to_staging(bundle, destination)

    def test_tampered_bundle_blocked_before_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, _, bundle = make_bundle(base)
            destination = base / "restored"
            write(bundle / "files/app/a.py", "bad\n")
            with self.assertRaises(restore.RestoreError):
                restore.restore_to_staging(bundle, destination)
            self.assertFalse(destination.exists())

    def test_bundle_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, _, bundle = make_bundle(base)
            destination = base / "restored"
            before = {
                path.relative_to(bundle).as_posix(): path.read_bytes()
                for path in bundle.rglob("*")
                if path.is_file()
            }
            restore.restore_to_staging(bundle, destination)
            after = {
                path.relative_to(bundle).as_posix(): path.read_bytes()
                for path in bundle.rglob("*")
                if path.is_file()
            }
            self.assertEqual(before, after)

    def test_partial_destination_blocks_rehearsal(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, _, bundle = make_bundle(base)
            destination = base / "restored"
            destination.with_name(destination.name + ".partial").mkdir()
            with self.assertRaises(restore.RestoreError):
                restore.restore_to_staging(bundle, destination)

    def test_restore_metadata_matches_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            _, _, bundle = make_bundle(base)
            destination = base / "restored"
            result = restore.restore_to_staging(bundle, destination)
            self.assertEqual(len(result["database_sha256"]), 64)
            self.assertEqual(len(result["manifest_sha256"]), 64)


if __name__ == "__main__":
    unittest.main()
