from __future__ import annotations

import hashlib
import importlib.util
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

SCRIPT = SCRIPTS / "audit_sqlite_version_lineage.py"
spec = importlib.util.spec_from_file_location("audit_sqlite_version_lineage", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def policy(**overrides) -> dict:
    data = {
        "version": 1,
        "parent_table": "fechamento_mensal_cliente",
        "version_table": "fechamento_mensal_versao",
        "key_columns": ["competencia", "cliente_id"],
        "current_version_column": "versao_atual",
        "version_column": "versao",
        "parent_status_column": "status",
        "parent_current_required_statuses": ["FECHADA"],
        "version_current_flag_column": "vigente",
        "version_current_flag_value": 1,
        "require_unique_version_index": True,
        "require_positive_version": True,
    }
    data.update(overrides)
    return data


def create_db(path: Path, *, unique=True) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE fechamento_mensal_cliente (
                competencia TEXT NOT NULL,
                cliente_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                versao_atual INTEGER
            );
            CREATE TABLE fechamento_mensal_versao (
                competencia TEXT NOT NULL,
                cliente_id INTEGER NOT NULL,
                versao INTEGER NOT NULL,
                vigente INTEGER NOT NULL DEFAULT 0,
                payload TEXT
            );
            """
        )
        if unique:
            conn.execute(
                "CREATE UNIQUE INDEX ux_fechamento_versao ON fechamento_mensal_versao(competencia, cliente_id, versao)"
            )
        conn.commit()
    finally:
        conn.close()


def insert_parent(path: Path, row: tuple) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        "INSERT INTO fechamento_mensal_cliente(competencia, cliente_id, status, versao_atual) VALUES(?,?,?,?)",
        row,
    )
    conn.commit()
    conn.close()


def insert_versions(path: Path, rows: list[tuple]) -> None:
    conn = sqlite3.connect(path)
    conn.executemany(
        "INSERT INTO fechamento_mensal_versao(competencia, cliente_id, versao, vigente, payload) VALUES(?,?,?,?,?)",
        rows,
    )
    conn.commit()
    conn.close()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class VersionLineageAuditTests(unittest.TestCase):
    def test_valid_lineage_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert_parent(db, ("2026-08", 10, "FECHADA", 2))
            insert_versions(
                db,
                [
                    ("2026-08", 10, 1, 0, "original"),
                    ("2026-08", 10, 2, 1, "retificacao"),
                ],
            )
            report = module.audit_database(db, policy())
            self.assertTrue(report["ok"])

    def test_newer_candidate_does_not_have_to_be_current(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert_parent(db, ("2026-08", 10, "FECHADA", 1))
            insert_versions(
                db,
                [
                    ("2026-08", 10, 1, 1, "vigente"),
                    ("2026-08", 10, 2, 0, "candidato-nao-promovido"),
                ],
            )
            report = module.audit_database(db, policy())
            self.assertTrue(report["ok"])

    def test_missing_unique_version_index_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db, unique=False)
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("MISSING_UNIQUE_VERSION_INDEX", str(report["findings"]))

    def test_duplicate_version_identity_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db, unique=False)
            insert_parent(db, ("2026-08", 10, "ABERTA", None))
            insert_versions(
                db,
                [
                    ("2026-08", 10, 1, 0, "a"),
                    ("2026-08", 10, 1, 0, "b"),
                ],
            )
            report = module.audit_database(
                db,
                policy(require_unique_version_index=False),
            )
            self.assertFalse(report["ok"])
            self.assertIn("DUPLICATE_VERSION_IDENTITY", str(report["findings"]))

    def test_parent_pointer_to_missing_version_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert_parent(db, ("2026-08", 10, "FECHADA", 9))
            insert_versions(db, [("2026-08", 10, 1, 0, "a")])
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("CURRENT_VERSION_NOT_FOUND", str(report["findings"]))

    def test_closed_parent_without_current_version_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert_parent(db, ("2026-08", 10, "FECHADA", None))
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("REQUIRED_CURRENT_VERSION_MISSING", str(report["findings"]))

    def test_multiple_current_flags_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert_parent(db, ("2026-08", 10, "FECHADA", 2))
            insert_versions(
                db,
                [
                    ("2026-08", 10, 1, 1, "a"),
                    ("2026-08", 10, 2, 1, "b"),
                ],
            )
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("MULTIPLE_CURRENT_VERSIONS", str(report["findings"]))

    def test_pointer_and_current_flag_mismatch_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert_parent(db, ("2026-08", 10, "FECHADA", 2))
            insert_versions(
                db,
                [
                    ("2026-08", 10, 1, 1, "a"),
                    ("2026-08", 10, 2, 0, "b"),
                ],
            )
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("CURRENT_POINTER_FLAG_MISMATCH", str(report["findings"]))

    def test_orphan_version_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert_versions(db, [("2026-08", 999, 1, 0, "orfa")])
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("ORPHAN_VERSION", str(report["findings"]))

    def test_audit_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert_parent(db, ("2026-08", 10, "FECHADA", 1))
            insert_versions(db, [("2026-08", 10, 1, 1, "a")])
            before = sha(db)
            report = module.audit_database(db, policy())
            after = sha(db)
            self.assertTrue(report["ok"])
            self.assertEqual(before, after)
            self.assertFalse(report["mutation_performed"])


if __name__ == "__main__":
    unittest.main()
