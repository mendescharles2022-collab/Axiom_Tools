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

SCRIPT = SCRIPTS / "audit_state_transition_history.py"
spec = importlib.util.spec_from_file_location("audit_state_transition_history", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def policy(*, current=False, **overrides) -> dict:
    data = {
        "version": 1,
        "history_table": "fechamento_historico",
        "key_columns": ["competencia", "cliente_id"],
        "order_column": "id",
        "state_column": "status",
        "call_column": "chamada",
        "allowed_transitions": {
            "PRONTA": ["PRONTA", "ADIADA", "FECHADA"],
            "ADIADA": ["ADIADA", "PRONTA", "FECHADA"],
            "FECHADA": ["FECHADA"],
        },
        "call_floor_by_state": {"ADIADA": 2},
        "forbid_call_decrease": True,
        "require_history_for_current": True,
    }
    if current:
        data.update(
            {
                "current_table": "fechamento_atual",
                "current_state_column": "status",
                "current_call_column": "chamada",
            }
        )
    data.update(overrides)
    return data


def create_db(path: Path, *, current=False) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(
            """
            CREATE TABLE fechamento_historico (
                id INTEGER NOT NULL,
                competencia TEXT NOT NULL,
                cliente_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                chamada TEXT NOT NULL
            );
            """
        )
        if current:
            conn.executescript(
                """
                CREATE TABLE fechamento_atual (
                    competencia TEXT NOT NULL,
                    cliente_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    chamada TEXT NOT NULL
                );
                """
            )
        conn.commit()
    finally:
        conn.close()


def history(path: Path, rows: list[tuple]) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executemany(
            "INSERT INTO fechamento_historico(id, competencia, cliente_id, status, chamada) VALUES(?,?,?,?,?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()


def current(path: Path, rows: list[tuple]) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executemany(
            "INSERT INTO fechamento_atual(competencia, cliente_id, status, chamada) VALUES(?,?,?,?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class StateTransitionAuditTests(unittest.TestCase):
    def test_valid_second_call_history_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            history(
                db,
                [
                    (1, "2026-08", 10, "PRONTA", "1"),
                    (2, "2026-08", 10, "ADIADA", "2"),
                    (3, "2026-08", 10, "PRONTA", "2"),
                ],
            )
            self.assertTrue(module.audit_database(db, policy())["ok"])

    def test_tl_regression_back_to_first_call_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            history(
                db,
                [
                    (1, "2026-08", 77, "PRONTA", "1"),
                    (2, "2026-08", 77, "ADIADA", "2"),
                    (3, "2026-08", 77, "PRONTA", "1"),
                ],
            )
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            text = str(report["findings"])
            self.assertIn("CALL_DECREASE", text)
            self.assertIn("PROTECTED_CALL_FLOOR_REGRESSION", text)

    def test_adiada_in_first_call_violates_floor(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            history(db, [(1, "2026-08", 10, "ADIADA", "1")])
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("STATE_CALL_FLOOR_VIOLATION", str(report["findings"]))

    def test_forbidden_state_transition_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            history(
                db,
                [
                    (1, "2026-08", 10, "FECHADA", "2"),
                    (2, "2026-08", 10, "PRONTA", "2"),
                ],
            )
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("FORBIDDEN_STATE_TRANSITION", str(report["findings"]))

    def test_duplicate_transition_order_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            history(
                db,
                [
                    (1, "2026-08", 10, "PRONTA", "1"),
                    (1, "2026-08", 10, "ADIADA", "2"),
                ],
            )
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("DUPLICATE_TRANSITION_ORDER", str(report["findings"]))

    def test_invalid_history_call_value_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            history(db, [(1, "2026-08", 10, "PRONTA", "SEGUNDA")])
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("INVALID_CALL_VALUE", str(report["findings"]))

    def test_current_snapshot_matching_latest_history_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db, current=True)
            history(
                db,
                [
                    (1, "2026-08", 10, "PRONTA", "1"),
                    (2, "2026-08", 10, "ADIADA", "2"),
                ],
            )
            current(db, [("2026-08", 10, "ADIADA", "2")])
            report = module.audit_database(db, policy(current=True))
            self.assertTrue(report["ok"])
            self.assertEqual(report["summary"]["current_rows_checked"], 1)

    def test_current_snapshot_mismatch_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db, current=True)
            history(db, [(1, "2026-08", 10, "ADIADA", "2")])
            current(db, [("2026-08", 10, "PRONTA", "1")])
            report = module.audit_database(db, policy(current=True))
            self.assertFalse(report["ok"])
            self.assertIn("CURRENT_HISTORY_MISMATCH", str(report["findings"]))

    def test_current_without_valid_history_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db, current=True)
            current(db, [("2026-08", 10, "PRONTA", "1")])
            report = module.audit_database(db, policy(current=True))
            self.assertFalse(report["ok"])
            self.assertIn("CURRENT_WITHOUT_VALID_HISTORY", str(report["findings"]))

    def test_invalid_current_call_is_reported_not_raised(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db, current=True)
            history(db, [(1, "2026-08", 10, "ADIADA", "2")])
            current(db, [("2026-08", 10, "ADIADA", "SEGUNDA")])
            report = module.audit_database(db, policy(current=True))
            self.assertFalse(report["ok"])
            self.assertIn("CURRENT_INVALID_CALL_VALUE", str(report["findings"]))

    def test_invalid_latest_history_does_not_crash_current_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db, current=True)
            history(
                db,
                [
                    (1, "2026-08", 10, "ADIADA", "2"),
                    (2, "2026-08", 10, "PRONTA", "INVALIDA"),
                ],
            )
            current(db, [("2026-08", 10, "ADIADA", "2")])
            report = module.audit_database(db, policy(current=True))
            self.assertFalse(report["ok"])
            self.assertIn("INVALID_CALL_VALUE", str(report["findings"]))

    def test_audit_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            create_db(db)
            history(db, [(1, "2026-08", 10, "PRONTA", "1")])
            before = sha(db)
            report = module.audit_database(db, policy())
            after = sha(db)
            self.assertTrue(report["ok"])
            self.assertEqual(before, after)
            self.assertFalse(report["mutation_performed"])


if __name__ == "__main__":
    unittest.main()
