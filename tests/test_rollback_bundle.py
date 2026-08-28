from __future__ import annotations

import importlib.util
import json
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
verify = load("verify_rollback_bundle", "verify_rollback_bundle.py")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_db(path: Path, bad_fk: bool = False) -> None:
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA foreign_keys=OFF")
    conn.execute("CREATE TABLE p(id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE c(id INTEGER PRIMARY KEY,pid INTEGER REFERENCES p(id))")
    conn.execute("INSERT INTO p VALUES(1)")
    conn.execute("INSERT INTO c VALUES(1,?)", (999 if bad_fk else 1,))
    conn.commit()
    conn.close()


def plan() -> dict:
    return {
        "version": 1,
        "files": [
            {"path": "app/a.py", "role": "code"},
            {"path": "config/app.ini", "role": "config"},
        ],
    }


class RollbackTests(unittest.TestCase):
    def test_valid_bundle_verifies(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "root"
            out = base / "bundle"
            database = base / "db.sqlite3"
            write(root / "app/a.py", "x=1\n")
            write(root / "config/app.ini", "mode=prod\n")
            make_db(database)
            builder.create_bundle(
                source_root=root,
                db_path=database,
                plan=plan(),
                output_dir=out,
                app_version="V7",
                schema_version="7",
                commit_sha="abc123",
            )
            report = verify.verify_bundle(out)
            self.assertTrue(report["ok"])
            self.assertEqual(report["file_count"], 2)

    def test_sources_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "root"
            out = base / "bundle"
            database = base / "db.sqlite3"
            write(root / "app/a.py", "x=1\n")
            write(root / "config/app.ini", "mode=prod\n")
            make_db(database)
            before_file = (root / "app/a.py").read_bytes()
            before_db = database.read_bytes()
            builder.create_bundle(
                source_root=root,
                db_path=database,
                plan=plan(),
                output_dir=out,
                app_version="V7",
                schema_version="7",
                commit_sha="abc123",
            )
            self.assertEqual(before_file, (root / "app/a.py").read_bytes())
            self.assertEqual(before_db, database.read_bytes())

    def test_traversal_rejected(self):
        with self.assertRaises(builder.RollbackError):
            builder.create_bundle(
                source_root=Path("."),
                db_path=Path("x"),
                plan={"files": [{"path": "../x", "role": "code"}]},
                output_dir=Path("y"),
                app_version="V",
                schema_version="1",
                commit_sha="a",
            )

    def test_existing_destination_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "root"
            out = base / "bundle"
            out.mkdir()
            database = base / "db.sqlite3"
            write(root / "app/a.py", "x=1\n")
            write(root / "config/app.ini", "x=1\n")
            make_db(database)
            with self.assertRaises(builder.RollbackError):
                builder.create_bundle(
                    source_root=root,
                    db_path=database,
                    plan=plan(),
                    output_dir=out,
                    app_version="V7",
                    schema_version="7",
                    commit_sha="a",
                )

    def test_tampered_file_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "root"
            out = base / "bundle"
            database = base / "db.sqlite3"
            write(root / "app/a.py", "x=1\n")
            write(root / "config/app.ini", "x=1\n")
            make_db(database)
            builder.create_bundle(
                source_root=root,
                db_path=database,
                plan=plan(),
                output_dir=out,
                app_version="V7",
                schema_version="7",
                commit_sha="a",
            )
            write(out / "files/app/a.py", "x=999\n")
            with self.assertRaises(verify.VerificationError):
                verify.verify_bundle(out)

    def test_extra_file_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "root"
            out = base / "bundle"
            database = base / "db.sqlite3"
            write(root / "app/a.py", "x=1\n")
            write(root / "config/app.ini", "x=1\n")
            make_db(database)
            builder.create_bundle(
                source_root=root,
                db_path=database,
                plan=plan(),
                output_dir=out,
                app_version="V7",
                schema_version="7",
                commit_sha="a",
            )
            write(out / "extra.txt", "oops")
            with self.assertRaises(verify.VerificationError):
                verify.verify_bundle(out)

    def test_fk_violation_blocks_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "root"
            out = base / "bundle"
            database = base / "db.sqlite3"
            write(root / "app/a.py", "x=1\n")
            write(root / "config/app.ini", "x=1\n")
            make_db(database, True)
            with self.assertRaises(builder.RollbackError):
                builder.create_bundle(
                    source_root=root,
                    db_path=database,
                    plan=plan(),
                    output_dir=out,
                    app_version="V7",
                    schema_version="7",
                    commit_sha="a",
                )
            self.assertFalse(out.exists())
            self.assertFalse(out.with_name(out.name + ".partial").exists())

    def test_manifest_tamper_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "root"
            out = base / "bundle"
            database = base / "db.sqlite3"
            write(root / "app/a.py", "x=1\n")
            write(root / "config/app.ini", "x=1\n")
            make_db(database)
            builder.create_bundle(
                source_root=root,
                db_path=database,
                plan=plan(),
                output_dir=out,
                app_version="V7",
                schema_version="7",
                commit_sha="a",
            )
            manifest_path = out / builder.MANIFEST_NAME
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            data["app_version"] = "EVIL"
            manifest_path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(verify.VerificationError):
                verify.verify_bundle(out)


if __name__ == "__main__":
    unittest.main()
