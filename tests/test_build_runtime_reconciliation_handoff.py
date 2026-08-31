from __future__ import annotations

import hashlib
import importlib.util
import json
import sqlite3
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

SCRIPT = SCRIPTS / "build_runtime_reconciliation_handoff.py"
spec = importlib.util.spec_from_file_location("build_runtime_reconciliation_handoff", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def create_runtime(root: Path, *, content: str = "x = 1\n") -> None:
    write(root / "app" / "src" / "pkg" / "a.py", content)
    write(root / "app" / "requirements.txt", "flask\n")


def create_db(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        conn.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY, status TEXT NOT NULL)")
        conn.execute("INSERT INTO jobs(status) VALUES ('OK')")
        conn.commit()
    finally:
        conn.close()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class RuntimeReconciliationHandoffTests(unittest.TestCase):
    def test_success_builds_separate_code_and_database_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            database = base / "operational.sqlite3"
            output = base / "handoff-output"
            create_runtime(runtime)
            create_db(database)

            result = module.build_handoff(
                runtime_root=runtime,
                database=database,
                output_dir=output,
                label="audit-v8",
            )

            handoff = output / result["handoff_dir"]
            code_zip = handoff / result["code_zip"]
            db_copy = handoff / result["database_copy"]
            manifest_path = handoff / result["manifest_file"]
            report_path = handoff / result["database_report"]

            self.assertTrue(code_zip.is_file())
            self.assertTrue(db_copy.is_file())
            self.assertTrue(manifest_path.is_file())
            self.assertTrue(report_path.is_file())
            self.assertNotEqual(code_zip, db_copy)

            with zipfile.ZipFile(code_zip) as archive:
                names = set(archive.namelist())
            self.assertIn("app/src/pkg/a.py", names)
            self.assertFalse(any(name.endswith((".sqlite", ".sqlite3", ".db")) for name in names))
            self.assertFalse(result["manifest"]["code_export"]["database_in_code_zip"])
            self.assertTrue(result["manifest"]["database_copy"]["kept_separate_from_code_zip"])
            self.assertEqual(result["manifest"]["source"]["database_selection"], "EXPLICIT")

    def test_manifest_hashes_match_generated_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            database = base / "operational.sqlite3"
            output = base / "out"
            create_runtime(runtime)
            create_db(database)

            result = module.build_handoff(
                runtime_root=runtime,
                database=database,
                output_dir=output,
                label="audit-v8",
            )
            handoff = output / result["handoff_dir"]
            manifest = json.loads((handoff / module.MANIFEST_NAME).read_text(encoding="utf-8"))

            self.assertEqual(
                manifest["code_export"]["zip_sha256"],
                sha256(handoff / manifest["code_export"]["zip"]),
            )
            self.assertEqual(
                manifest["database_copy"]["sha256"],
                sha256(handoff / manifest["database_copy"]["file"]),
            )
            manifest_hash = manifest.pop("manifest_sha256")
            self.assertEqual(manifest_hash, module.canonical_hash(manifest))

    def test_source_database_and_code_remain_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            source_file = runtime / "app" / "src" / "pkg" / "a.py"
            database = base / "operational.sqlite3"
            output = base / "out"
            create_runtime(runtime)
            create_db(database)
            code_before = sha256(source_file)
            db_before = sha256(database)

            result = module.build_handoff(
                runtime_root=runtime,
                database=database,
                output_dir=output,
                label="audit-v8",
            )

            self.assertEqual(code_before, sha256(source_file))
            self.assertEqual(db_before, sha256(database))
            self.assertFalse(result["manifest"]["source"]["source_mutation_performed"])
            self.assertEqual(
                result["manifest"]["source"]["database_sha256_before"], db_before
            )
            self.assertEqual(
                result["manifest"]["source"]["database_sha256_after"], db_before
            )

    def test_database_copy_is_sqlite_equivalent_for_schema_and_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            database = base / "operational.sqlite3"
            output = base / "out"
            create_runtime(runtime)
            create_db(database)

            result = module.build_handoff(
                runtime_root=runtime,
                database=database,
                output_dir=output,
                label="audit-v8",
            )
            handoff = output / result["handoff_dir"]
            copied = handoff / result["database_copy"]
            report = json.loads((handoff / result["database_report"]).read_text(encoding="utf-8"))
            conn = sqlite3.connect(copied)
            try:
                rows = conn.execute("SELECT id, status FROM jobs ORDER BY id").fetchall()
            finally:
                conn.close()
            self.assertEqual(rows, [(1, "OK")])
            self.assertEqual(
                report["source"]["schema_sha256"],
                report["destination"]["schema_sha256"],
            )
            self.assertEqual(
                result["manifest"]["database_copy"]["schema_sha256"],
                report["destination"]["schema_sha256"],
            )

    def test_single_runtime_sqlite_is_auto_discovered(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            output = base / "out"
            database = runtime / "data" / "operational.sqlite3"
            create_runtime(runtime)
            create_db(database)

            result = module.build_handoff(
                runtime_root=runtime,
                database=None,
                output_dir=output,
                label="audit-v8",
            )

            self.assertEqual(result["manifest"]["source"]["database_name"], "operational.sqlite3")
            self.assertEqual(
                result["manifest"]["source"]["database_selection"],
                "AUTO_DISCOVERED_SINGLE",
            )

    def test_multiple_runtime_sqlites_block_auto_selection(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            output = base / "out"
            create_runtime(runtime)
            create_db(runtime / "data" / "a.sqlite3")
            create_db(runtime / "database" / "b.db")

            with self.assertRaises(module.RuntimeHandoffError) as ctx:
                module.build_handoff(
                    runtime_root=runtime,
                    database=None,
                    output_dir=output,
                    label="audit-v8",
                )
            message = str(ctx.exception)
            self.assertIn("seleção automática bloqueada", message)
            self.assertIn("data/a.sqlite3", message)
            self.assertIn("database/b.db", message)
            self.assertFalse((output / "audit-v8-handoff").exists())

    def test_fake_sqlite_extension_is_ignored_by_autodiscovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            output = base / "out"
            create_runtime(runtime)
            write(runtime / "data" / "fake.sqlite3", "isto não é sqlite\n")
            create_db(runtime / "database" / "live.sqlite3")

            result = module.build_handoff(
                runtime_root=runtime,
                database=None,
                output_dir=output,
                label="audit-v8",
            )
            self.assertEqual(result["manifest"]["source"]["database_name"], "live.sqlite3")

    def test_sqlite_inside_backup_directory_is_not_auto_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            output = base / "out"
            create_runtime(runtime)
            create_db(runtime / "backups" / "old.sqlite3")
            create_db(runtime / "data" / "live.sqlite3")

            result = module.build_handoff(
                runtime_root=runtime,
                database=None,
                output_dir=output,
                label="audit-v8",
            )
            self.assertEqual(result["manifest"]["source"]["database_name"], "live.sqlite3")

    def test_autodiscovery_without_valid_sqlite_requires_explicit_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            output = base / "out"
            create_runtime(runtime)
            write(runtime / "data" / "fake.db", "texto\n")

            with self.assertRaises(module.RuntimeHandoffError) as ctx:
                module.build_handoff(
                    runtime_root=runtime,
                    database=None,
                    output_dir=output,
                    label="audit-v8",
                )
            self.assertIn("Nenhum SQLite válido", str(ctx.exception))

    def test_explicit_database_requires_valid_sqlite_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            output = base / "out"
            fake = base / "fake.sqlite3"
            create_runtime(runtime)
            write(fake, "texto\n")

            with self.assertRaises(module.RuntimeHandoffError) as ctx:
                module.build_handoff(
                    runtime_root=runtime,
                    database=fake,
                    output_dir=output,
                    label="audit-v8",
                )
            self.assertIn("cabeçalho SQLite válido", str(ctx.exception))

    def test_existing_handoff_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            database = base / "operational.sqlite3"
            output = base / "out"
            create_runtime(runtime)
            create_db(database)
            protected = output / "audit-v8-handoff"
            write(protected / "KEEP.txt", "preservar\n")

            with self.assertRaises(module.RuntimeHandoffError):
                module.build_handoff(
                    runtime_root=runtime,
                    database=database,
                    output_dir=output,
                    label="audit-v8",
                )
            self.assertEqual((protected / "KEEP.txt").read_text(encoding="utf-8"), "preservar\n")

    def test_output_inside_runtime_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            database = base / "operational.sqlite3"
            create_runtime(runtime)
            create_db(database)

            with self.assertRaises(module.RuntimeHandoffError):
                module.build_handoff(
                    runtime_root=runtime,
                    database=database,
                    output_dir=runtime / "temp" / "handoff",
                    label="audit-v8",
                )

    def test_database_inside_output_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            output = base / "out"
            database = output / "operational.sqlite3"
            create_runtime(runtime)
            create_db(database)

            with self.assertRaises(module.RuntimeHandoffError):
                module.build_handoff(
                    runtime_root=runtime,
                    database=database,
                    output_dir=output,
                    label="audit-v8",
                )

    def test_secret_failure_cleans_partial_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            database = base / "operational.sqlite3"
            output = base / "out"
            create_runtime(runtime, content='api_key = "sk_live_ABC123456789"\n')
            create_db(database)

            with self.assertRaises(module.runtime_export.ExportError):
                module.build_handoff(
                    runtime_root=runtime,
                    database=database,
                    output_dir=output,
                    label="audit-v8",
                )
            self.assertFalse((output / "audit-v8-handoff").exists())

    def test_invalid_label_is_blocked_before_output_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            database = base / "operational.sqlite3"
            output = base / "out"
            create_runtime(runtime)
            create_db(database)

            with self.assertRaises(module.RuntimeHandoffError):
                module.build_handoff(
                    runtime_root=runtime,
                    database=database,
                    output_dir=output,
                    label="../escape",
                )
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
