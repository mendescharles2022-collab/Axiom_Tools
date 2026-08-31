from __future__ import annotations

import importlib.util
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SCRIPT = ROOT / "scripts" / "build_rollback_readiness_preflight.py"
spec = importlib.util.spec_from_file_location(
    "build_rollback_readiness_preflight", SCRIPT
)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def create_db(path: Path, *, invalid_closing: bool = False) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE fechamento_mensal_cliente (
                competencia TEXT NOT NULL,
                cliente_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                versao_atual INTEGER,
                PRIMARY KEY (competencia, cliente_id)
            );
            CREATE TABLE fechamento_mensal_versao (
                competencia TEXT NOT NULL,
                cliente_id INTEGER NOT NULL,
                versao INTEGER NOT NULL,
                PRIMARY KEY (competencia, cliente_id, versao)
            );
            """
        )
        if invalid_closing:
            conn.execute(
                "INSERT INTO fechamento_mensal_cliente VALUES ('08/2026',1,'FECHADA',NULL)"
            )
        else:
            conn.execute(
                "INSERT INTO fechamento_mensal_cliente VALUES ('08/2026',1,'FECHADA',1)"
            )
            conn.execute(
                "INSERT INTO fechamento_mensal_versao VALUES ('08/2026',1,1)"
            )
        conn.commit()
    finally:
        conn.close()


def invariant_spec() -> dict:
    return {
        "version": 1,
        "invariants": [
            {
                "id": "CLOSING_FECHADA_WITHOUT_VERSION",
                "severity": "error",
                "sql": (
                    "SELECT f.competencia, f.cliente_id FROM fechamento_mensal_cliente f "
                    "WHERE f.status='FECHADA' AND NOT EXISTS (SELECT 1 "
                    "FROM fechamento_mensal_versao v WHERE v.competencia=f.competencia "
                    "AND v.cliente_id=f.cliente_id)"
                ),
                "max_rows": 10,
            }
        ],
    }


def plan(include_config: bool = True) -> dict:
    files = [{"path": "app/main.py", "role": "code"}]
    if include_config:
        files.append({"path": "config/settings.example.json", "role": "config"})
    return {"version": 1, "files": files}


def fixture(base: Path, *, invalid_closing: bool = False):
    source = base / "source"
    (source / "app").mkdir(parents=True)
    (source / "config").mkdir(parents=True)
    (source / "app" / "main.py").write_text("VALUE = 1\n", encoding="utf-8")
    (source / "config" / "settings.example.json").write_text(
        '{"mode":"example"}\n', encoding="utf-8"
    )
    db = base / "axiom_tools.sqlite3"
    create_db(db, invalid_closing=invalid_closing)
    return source, db


class RollbackReadinessPreflightTests(unittest.TestCase):
    def test_valid_bundle_restore_and_database_preflight_are_ready(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source, db = fixture(base)
            work = base / "work"

            report = module.build_rollback_readiness(
                source_root=source,
                db_path=db,
                plan=plan(),
                invariant_spec=invariant_spec(),
                work_dir=work,
                app_version="5.6.14V8",
                schema_version="8",
                commit_sha="abc123",
            )

            self.assertTrue(report["summary"]["ready_for_windows_rehearsal"])
            self.assertTrue(report["summary"]["bundle_verified"])
            self.assertTrue(report["summary"]["restore_rehearsal_ok"])
            self.assertTrue(report["summary"]["restored_database_ok"])
            self.assertTrue(report["summary"]["source_unchanged"])
            self.assertEqual(report["coverage"]["roles_present"], ["code", "config"])
            self.assertTrue((work / "ROLLBACK_READINESS_PREFLIGHT.json").is_file())

    def test_plan_without_config_is_rejected(self):
        with self.assertRaises(module.RollbackReadinessError):
            module.normalize_plan(plan(include_config=False))

    def test_invalid_restored_database_blocks_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source, db = fixture(base, invalid_closing=True)

            report = module.build_rollback_readiness(
                source_root=source,
                db_path=db,
                plan=plan(),
                invariant_spec=invariant_spec(),
                work_dir=base / "work",
                app_version="5.6.14V8",
                schema_version="8",
                commit_sha="abc123",
            )

            self.assertFalse(report["summary"]["ready_for_windows_rehearsal"])
            self.assertFalse(report["summary"]["restored_database_ok"])
            self.assertTrue(report["summary"]["bundle_verified"])
            self.assertTrue(report["summary"]["restore_rehearsal_ok"])

    def test_existing_work_dir_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source, db = fixture(base)
            work = base / "work"
            work.mkdir()
            sentinel = work / "keep.txt"
            sentinel.write_text("keep\n", encoding="utf-8")

            with self.assertRaises(module.RollbackReadinessError):
                module.build_rollback_readiness(
                    source_root=source,
                    db_path=db,
                    plan=plan(),
                    invariant_spec=invariant_spec(),
                    work_dir=work,
                    app_version="5.6.14V8",
                    schema_version="8",
                    commit_sha="abc123",
                )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep\n")

    def test_source_files_and_database_remain_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source, db = fixture(base)
            normalized = module.normalize_plan(plan())
            before = module.snapshot_sources(source, db, normalized)

            module.build_rollback_readiness(
                source_root=source,
                db_path=db,
                plan=plan(),
                invariant_spec=invariant_spec(),
                work_dir=base / "work",
                app_version="5.6.14V8",
                schema_version="8",
                commit_sha="abc123",
            )

            after = module.snapshot_sources(source, db, normalized)
            self.assertEqual(before, after)

    def test_missing_source_file_cleans_partial_workdir(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source, db = fixture(base)
            (source / "config" / "settings.example.json").unlink()
            work = base / "work"

            with self.assertRaises(module.RollbackReadinessError):
                module.build_rollback_readiness(
                    source_root=source,
                    db_path=db,
                    plan=plan(),
                    invariant_spec=invariant_spec(),
                    work_dir=work,
                    app_version="5.6.14V8",
                    schema_version="8",
                    commit_sha="abc123",
                )
            self.assertFalse(work.exists())
            self.assertFalse(work.with_name("work.partial").exists())


if __name__ == "__main__":
    unittest.main()
