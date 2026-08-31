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

SCRIPT = SCRIPTS / "plan_per_source_state_migration.py"
spec = importlib.util.spec_from_file_location("plan_per_source_state_migration", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def policy(**overrides) -> dict:
    data = {
        "version": 1,
        "legacy_table": "decisao_global",
        "source_table": "fontes_aplicaveis",
        "target_table": "decisao_fonte",
        "key_columns": ["competencia", "cliente_id"],
        "legacy_decision_column": "decisao",
        "source_column": "fonte",
        "source_applicable_column": "aplicavel",
        "source_applicable_value": 1,
        "target_decision_column": "decisao",
        "fanout_policy": "BLOCK",
        "require_unique_target_identity": True,
    }
    data.update(overrides)
    return data


def create_db(path: Path, *, unique_target=True) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE decisao_global (
                competencia TEXT NOT NULL,
                cliente_id INTEGER NOT NULL,
                decisao TEXT NOT NULL
            );
            CREATE TABLE fontes_aplicaveis (
                competencia TEXT NOT NULL,
                cliente_id INTEGER NOT NULL,
                fonte TEXT NOT NULL,
                aplicavel INTEGER NOT NULL
            );
            CREATE TABLE decisao_fonte (
                competencia TEXT NOT NULL,
                cliente_id INTEGER NOT NULL,
                fonte TEXT NOT NULL,
                decisao TEXT NOT NULL
            );
            """
        )
        if unique_target:
            conn.execute(
                "CREATE UNIQUE INDEX ux_decisao_fonte ON decisao_fonte(competencia, cliente_id, fonte)"
            )
        conn.commit()
    finally:
        conn.close()


def insert(path: Path, table: str, rows: list[tuple]) -> None:
    conn = sqlite3.connect(path)
    try:
        if table == "legacy":
            conn.executemany(
                "INSERT INTO decisao_global(competencia, cliente_id, decisao) VALUES(?,?,?)",
                rows,
            )
        elif table == "source":
            conn.executemany(
                "INSERT INTO fontes_aplicaveis(competencia, cliente_id, fonte, aplicavel) VALUES(?,?,?,?)",
                rows,
            )
        elif table == "target":
            conn.executemany(
                "INSERT INTO decisao_fonte(competencia, cliente_id, fonte, decisao) VALUES(?,?,?,?)",
                rows,
            )
        else:
            raise AssertionError(table)
        conn.commit()
    finally:
        conn.close()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PerSourceMigrationPlannerTests(unittest.TestCase):
    def test_single_applicable_source_generates_one_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert(db, "legacy", [("2026-08", 10, "IMPEDIDO")])
            insert(db, "source", [("2026-08", 10, "ECAC", 1)])
            report = module.plan_migration(db, policy())
            self.assertTrue(report["plan_ok"])
            self.assertEqual(report["summary"]["planned_inserts"], 1)
            self.assertEqual(report["planned_inserts"][0]["source"], "ECAC")

    def test_multiple_sources_block_implicit_fanout(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert(db, "legacy", [("2026-08", 10, "IMPEDIDO")])
            insert(
                db,
                "source",
                [("2026-08", 10, "ECAC", 1), ("2026-08", 10, "FGTS", 1)],
            )
            report = module.plan_migration(db, policy())
            self.assertFalse(report["plan_ok"])
            self.assertEqual(report["summary"]["planned_inserts"], 0)
            self.assertIn("AMBIGUOUS_FANOUT", str(report["findings"]))

    def test_explicit_replicate_policy_can_plan_multiple_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert(db, "legacy", [("2026-08", 10, "SEM_MOVIMENTO")])
            insert(
                db,
                "source",
                [("2026-08", 10, "ESOCIAL", 1), ("2026-08", 10, "FGTS", 1)],
            )
            report = module.plan_migration(
                db, policy(fanout_policy="REPLICATE_EXPLICIT")
            )
            self.assertTrue(report["plan_ok"])
            self.assertEqual(report["summary"]["planned_inserts"], 2)

    def test_existing_same_decision_is_already_migrated(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert(db, "legacy", [("2026-08", 10, "IMPEDIDO")])
            insert(db, "source", [("2026-08", 10, "ECAC", 1)])
            insert(db, "target", [("2026-08", 10, "ECAC", "IMPEDIDO")])
            report = module.plan_migration(db, policy())
            self.assertTrue(report["plan_ok"])
            self.assertEqual(report["summary"]["planned_inserts"], 0)
            self.assertEqual(report["summary"]["already_migrated"], 1)

    def test_existing_conflicting_decision_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert(db, "legacy", [("2026-08", 10, "IMPEDIDO")])
            insert(db, "source", [("2026-08", 10, "ECAC", 1)])
            insert(db, "target", [("2026-08", 10, "ECAC", "LIBERADO")])
            report = module.plan_migration(db, policy())
            self.assertFalse(report["plan_ok"])
            self.assertIn("TARGET_DECISION_CONFLICT", str(report["findings"]))

    def test_legacy_without_applicable_source_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert(db, "legacy", [("2026-08", 10, "IMPEDIDO")])
            insert(db, "source", [("2026-08", 10, "ECAC", 0)])
            report = module.plan_migration(db, policy())
            self.assertFalse(report["plan_ok"])
            self.assertIn(
                "LEGACY_STATE_WITHOUT_APPLICABLE_SOURCE", str(report["findings"])
            )

    def test_missing_unique_target_identity_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db, unique_target=False)
            report = module.plan_migration(db, policy())
            self.assertFalse(report["plan_ok"])
            self.assertIn("MISSING_UNIQUE_TARGET_IDENTITY", str(report["findings"]))

    def test_duplicate_legacy_global_state_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert(
                db,
                "legacy",
                [("2026-08", 10, "IMPEDIDO"), ("2026-08", 10, "LIBERADO")],
            )
            insert(db, "source", [("2026-08", 10, "ECAC", 1)])
            report = module.plan_migration(db, policy())
            self.assertFalse(report["plan_ok"])
            self.assertIn("DUPLICATE_LEGACY_GLOBAL_STATE", str(report["findings"]))

    def test_duplicate_target_identity_blocks_when_index_requirement_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db, unique_target=False)
            insert(
                db,
                "target",
                [
                    ("2026-08", 10, "ECAC", "A"),
                    ("2026-08", 10, "ECAC", "B"),
                ],
            )
            report = module.plan_migration(
                db, policy(require_unique_target_identity=False)
            )
            self.assertFalse(report["plan_ok"])
            self.assertIn("DUPLICATE_TARGET_IDENTITY", str(report["findings"]))

    def test_planner_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            insert(db, "legacy", [("2026-08", 10, "IMPEDIDO")])
            insert(db, "source", [("2026-08", 10, "ECAC", 1)])
            before = sha(db)
            report = module.plan_migration(db, policy())
            after = sha(db)
            self.assertTrue(report["plan_ok"])
            self.assertEqual(before, after)
            self.assertFalse(report["migration_executed"])


if __name__ == "__main__":
    unittest.main()
