from __future__ import annotations

import importlib.util
import json
import sqlite3
import stat
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_runtime_reconciliation_handoff as builder  # noqa: E402

SPEC = importlib.util.spec_from_file_location(
    "consume_runtime_reconciliation_handoff_test",
    SCRIPTS / "consume_runtime_reconciliation_handoff.py",
)
consumer = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = consumer
SPEC.loader.exec_module(consumer)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_db(path: Path, status: str = "OK") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        conn.execute("CREATE TABLE smoke (id INTEGER PRIMARY KEY, status TEXT NOT NULL)")
        conn.execute("INSERT INTO smoke(status) VALUES (?)", (status,))
        conn.commit()
    finally:
        conn.close()


def write_invariants(path: Path, expected: str = "OK") -> None:
    payload = {
        "version": 1,
        "invariants": [
            {
                "id": "smoke_status",
                "description": "status deve permanecer no valor esperado",
                "severity": "error",
                "sql": f"SELECT id, status FROM smoke WHERE status <> '{expected}'",
                "max_rows": 10,
            }
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def make_fixture(base: Path, *, runtime_text: str = "x = 1\n", repo_text: str = "x = 1\n", db_status: str = "OK") -> tuple[Path, Path, Path, Path]:
    runtime = base / "runtime"
    repo = base / "repo"
    handoff_output = base / "handoff-output"
    invariants = base / "invariants.json"
    write(runtime / "src/pkg/a.py", runtime_text)
    write(repo / "src/pkg/a.py", repo_text)
    database = runtime / "operational.sqlite3"
    make_db(database, db_status)
    write_invariants(invariants)
    result = builder.build_handoff(
        runtime_root=runtime,
        database=database,
        output_dir=handoff_output,
        label="test-v8",
    )
    return handoff_output / result["handoff_dir"], repo, invariants, database


class ConsumeRuntimeHandoffTests(unittest.TestCase):
    def test_valid_handoff_is_consumed_without_mutating_handoff(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff, repo, invariants, _ = make_fixture(base)
            before = consumer.snapshot_tree(handoff)
            result = consumer.consume_handoff(
                handoff,
                repo,
                base / "consumed",
                invariants_path=invariants,
            )
            self.assertTrue(result["handoff_unchanged"])
            self.assertTrue(result["internal_manifest_ok"])
            self.assertTrue(result["database_preflight_ok"])
            self.assertEqual(result["diff_summary"]["CHANGED"], 0)
            self.assertEqual(before, consumer.snapshot_tree(handoff))
            self.assertFalse(result["v8_homologated"])

    def test_runtime_difference_is_reported_not_hidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff, repo, invariants, _ = make_fixture(base, repo_text="x = 2\n")
            result = consumer.consume_handoff(
                handoff,
                repo,
                base / "consumed",
                invariants_path=invariants,
            )
            self.assertGreater(result["diff_summary"]["CHANGED"], 0)
            self.assertTrue(result["ready_for_reconciliation_review"])

    def test_database_preflight_failure_is_preserved_as_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff, repo, invariants, _ = make_fixture(base, db_status="ERRO")
            result = consumer.consume_handoff(
                handoff,
                repo,
                base / "consumed",
                invariants_path=invariants,
            )
            self.assertFalse(result["database_preflight_ok"])
            self.assertFalse(result["v8_homologated"])

    def test_tampered_code_zip_is_blocked_before_extraction(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff, repo, invariants, _ = make_fixture(base)
            manifest = consumer.load_json(handoff / consumer.MANIFEST_NAME)
            code_zip = handoff / manifest["code_export"]["zip"]
            with code_zip.open("ab") as stream:
                stream.write(b"tamper")
            output = base / "consumed"
            with self.assertRaisesRegex(consumer.HandoffConsumptionError, "ZIP de código diverge"):
                consumer.consume_handoff(handoff, repo, output, invariants_path=invariants)
            self.assertFalse(output.exists())

    def test_tampered_database_is_blocked_before_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff, repo, invariants, _ = make_fixture(base)
            manifest = consumer.load_json(handoff / consumer.MANIFEST_NAME)
            database = handoff / manifest["database_copy"]["file"]
            with database.open("ab") as stream:
                stream.write(b"tamper")
            with self.assertRaisesRegex(consumer.HandoffConsumptionError, "cópia SQLite diverge"):
                consumer.consume_handoff(handoff, repo, base / "consumed", invariants_path=invariants)

    def test_manifest_logical_hash_tamper_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff, repo, invariants, _ = make_fixture(base)
            path = handoff / consumer.MANIFEST_NAME
            manifest = consumer.load_json(path)
            manifest["source"]["source_mutation_performed"] = True
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(consumer.HandoffConsumptionError, "manifesto diverge"):
                consumer.consume_handoff(handoff, repo, base / "consumed", invariants_path=invariants)

    def test_output_inside_handoff_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff, repo, invariants, _ = make_fixture(base)
            with self.assertRaisesRegex(consumer.HandoffConsumptionError, "dentro do handoff"):
                consumer.consume_handoff(handoff, repo, handoff / "consumed", invariants_path=invariants)

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff, repo, invariants, _ = make_fixture(base)
            output = base / "consumed"
            output.mkdir()
            marker = output / "keep.txt"
            marker.write_text("preservar", encoding="utf-8")
            with self.assertRaisesRegex(consumer.HandoffConsumptionError, "já existe"):
                consumer.consume_handoff(handoff, repo, output, invariants_path=invariants)
            self.assertEqual(marker.read_text(encoding="utf-8"), "preservar")

    def test_zip_path_traversal_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            archive_path = base / "bad.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("../escape.txt", "x")
            with self.assertRaisesRegex(consumer.HandoffConsumptionError, "Caminho inseguro"):
                consumer.safe_extract_zip(archive_path, base / "extract")
            self.assertFalse((base / "escape.txt").exists())

    def test_zip_symlink_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            archive_path = base / "bad.zip"
            info = zipfile.ZipInfo("link")
            info.create_system = 3
            info.external_attr = (stat.S_IFLNK | 0o777) << 16
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr(info, "target")
            with self.assertRaisesRegex(consumer.HandoffConsumptionError, "Symlink proibido"):
                consumer.safe_extract_zip(archive_path, base / "extract")

    def test_database_report_schema_mismatch_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            handoff, repo, invariants, _ = make_fixture(base)
            manifest_path = handoff / consumer.MANIFEST_NAME
            manifest = consumer.load_json(manifest_path)
            report_path = handoff / manifest["database_copy"]["report"]
            report = consumer.load_json(report_path)
            report["destination"]["schema_sha256"] = "0" * 64
            report_path.write_text(json.dumps(report), encoding="utf-8")
            # O relatório não faz parte do hash externo próprio, mas deve cruzar semanticamente com o manifesto.
            with self.assertRaisesRegex(consumer.HandoffConsumptionError, "Schema SHA-256"):
                consumer.consume_handoff(handoff, repo, base / "consumed", invariants_path=invariants)


if __name__ == "__main__":
    unittest.main()
