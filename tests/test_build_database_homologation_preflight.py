from __future__ import annotations

import importlib.util
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SCRIPT = ROOT / "scripts" / "build_database_homologation_preflight.py"
spec = importlib.util.spec_from_file_location(
    "build_database_homologation_preflight", SCRIPT
)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def create_database(path: Path, *, closed_without_version: bool = False) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            PRAGMA foreign_keys=ON;
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
            CREATE TABLE docs (
                id INTEGER PRIMARY KEY,
                path TEXT NOT NULL
            );
            """
        )
        if closed_without_version:
            conn.execute(
                "INSERT INTO fechamento_mensal_cliente VALUES ('08/2026', 1, 'FECHADA', NULL)"
            )
        else:
            conn.execute(
                "INSERT INTO fechamento_mensal_cliente VALUES ('08/2026', 1, 'FECHADA', 1)"
            )
            conn.execute(
                "INSERT INTO fechamento_mensal_versao VALUES ('08/2026', 1, 1)"
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
                "description": "FECHADA precisa de versão.",
                "sql": (
                    "SELECT f.competencia, f.cliente_id "
                    "FROM fechamento_mensal_cliente f "
                    "WHERE f.status='FECHADA' AND NOT EXISTS ("
                    "SELECT 1 FROM fechamento_mensal_versao v "
                    "WHERE v.competencia=f.competencia "
                    "AND v.cliente_id=f.cliente_id)"
                ),
                "max_rows": 10,
            },
            {
                "id": "CLOSING_CURRENT_VERSION_MUST_EXIST",
                "severity": "error",
                "description": "versao_atual precisa existir.",
                "sql": (
                    "SELECT f.competencia, f.cliente_id, f.versao_atual "
                    "FROM fechamento_mensal_cliente f "
                    "WHERE f.versao_atual IS NOT NULL AND NOT EXISTS ("
                    "SELECT 1 FROM fechamento_mensal_versao v "
                    "WHERE v.competencia=f.competencia "
                    "AND v.cliente_id=f.cliente_id "
                    "AND v.versao=f.versao_atual)"
                ),
                "max_rows": 10,
            },
        ],
    }


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


class DatabaseHomologationPreflightTests(unittest.TestCase):
    def test_valid_snapshot_passes_structural_and_logical_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.sqlite3"
            create_database(db)

            report = module.build_database_preflight(db, invariant_spec())

            self.assertTrue(report["summary"]["all_ok"])
            self.assertTrue(report["summary"]["integrity_ok"])
            self.assertTrue(report["summary"]["foreign_keys_ok"])
            self.assertTrue(report["summary"]["logical_invariants_ok"])
            self.assertEqual(report["summary"]["logical_passed"], 2)
            self.assertTrue(report["summary"]["source_unchanged"])
            self.assertIsNone(report["filesystem_links"])

    def test_logical_violation_blocks_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.sqlite3"
            create_database(db, closed_without_version=True)

            report = module.build_database_preflight(db, invariant_spec())

            self.assertFalse(report["summary"]["all_ok"])
            self.assertTrue(report["summary"]["structural_ok"])
            self.assertFalse(report["summary"]["logical_invariants_ok"])
            self.assertEqual(report["logical_invariants"]["summary"]["errors_failed"], 1)

    def test_preflight_does_not_mutate_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.sqlite3"
            create_database(db)
            before = module.file_snapshot(db)

            module.build_database_preflight(db, invariant_spec())

            after = module.file_snapshot(db)
            self.assertEqual(before, after)

    def test_missing_half_of_filesystem_specs_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.sqlite3"
            create_database(db)
            with self.assertRaises(module.DatabasePreflightError):
                module.build_database_preflight(
                    db,
                    invariant_spec(),
                    forward_spec=forward_spec(),
                )

    def test_filesystem_audit_can_be_included_in_same_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            db = base / "test.sqlite3"
            managed = base / "docs"
            managed.mkdir()
            target = managed / "a.pdf"
            target.write_bytes(b"pdf")
            create_database(db)
            conn = sqlite3.connect(db)
            try:
                conn.execute("INSERT INTO docs(path) VALUES ('a.pdf')")
                conn.commit()
            finally:
                conn.close()

            report = module.build_database_preflight(
                db,
                invariant_spec(),
                forward_spec=forward_spec(),
                reverse_spec=reverse_spec(),
                roots={"docs": managed},
            )

            self.assertTrue(report["summary"]["all_ok"])
            self.assertTrue(report["summary"]["filesystem_links_evaluated"])
            self.assertTrue(report["summary"]["filesystem_links_ok"])

    def test_unindexed_file_blocks_integrated_preflight(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            db = base / "test.sqlite3"
            managed = base / "docs"
            managed.mkdir()
            (managed / "orphan.pdf").write_bytes(b"pdf")
            create_database(db)

            report = module.build_database_preflight(
                db,
                invariant_spec(),
                forward_spec=forward_spec(),
                reverse_spec=reverse_spec(),
                roots={"docs": managed},
            )

            self.assertFalse(report["summary"]["all_ok"])
            self.assertFalse(report["summary"]["filesystem_links_ok"])
            self.assertGreater(
                report["filesystem_links"]["summary"]["reverse_findings"], 0
            )

    def test_invalid_invariant_spec_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.sqlite3"
            create_database(db)
            with self.assertRaises(module.DatabasePreflightError):
                module.build_database_preflight(
                    db,
                    {"version": 99, "invariants": []},
                )


if __name__ == "__main__":
    unittest.main()
