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

SCRIPT = SCRIPTS / "audit_sqlite_idempotency_retry.py"
spec = importlib.util.spec_from_file_location("audit_sqlite_idempotency_retry", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def policy(**overrides) -> dict:
    data = {
        "version": 1,
        "table": "jobs",
        "id_column": "id",
        "idempotency_columns": ["competencia", "cliente_id", "tipo"],
        "status_column": "status",
        "attempt_column": "attempts",
        "next_retry_column": "next_retry_at",
        "max_attempts": 3,
        "terminal_statuses": ["DONE", "CANCELLED", "FAILED_FINAL"],
        "retryable_statuses": ["FAILED_RETRY", "PENDING_RETRY"],
        "require_unique_index": True,
        "allow_null_idempotency": False,
    }
    data.update(overrides)
    return data


def create_db(path: Path, *, unique=True, nullable_keys=False) -> None:
    conn = sqlite3.connect(path)
    try:
        null = "" if nullable_keys else " NOT NULL"
        conn.executescript(
            f"""
            CREATE TABLE jobs (
                id INTEGER PRIMARY KEY,
                competencia TEXT{null},
                cliente_id INTEGER{null},
                tipo TEXT{null},
                status TEXT NOT NULL,
                attempts INTEGER NOT NULL,
                next_retry_at TEXT
            );
            """
        )
        if unique:
            conn.execute(
                "CREATE UNIQUE INDEX ux_jobs_idem ON jobs(competencia, cliente_id, tipo)"
            )
        conn.commit()
    finally:
        conn.close()


def insert(path: Path, rows: list[tuple]) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executemany(
            "INSERT INTO jobs(id, competencia, cliente_id, tipo, status, attempts, next_retry_at) VALUES(?,?,?,?,?,?,?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class IdempotencyRetryAuditTests(unittest.TestCase):
    def test_valid_schema_and_rows_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "jobs.sqlite3"
            create_db(db)
            insert(
                db,
                [
                    (1, "2026-08", 10, "ECONSIGNADO", "DONE", 1, None),
                    (2, "2026-08", 11, "ECONSIGNADO", "FAILED_RETRY", 1, "2026-08-31T20:00:00"),
                ],
            )
            report = module.audit_database(db, policy())
            self.assertTrue(report["ok"])
            self.assertTrue(report["schema"]["idempotency_unique_index_ok"])

    def test_missing_unique_index_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "jobs.sqlite3"
            create_db(db, unique=False)
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("MISSING_UNIQUE_IDEMPOTENCY_INDEX", str(report["findings"]))

    def test_duplicate_idempotency_key_blocks_even_without_index_requirement(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "jobs.sqlite3"
            create_db(db, unique=False)
            insert(
                db,
                [
                    (1, "2026-08", 10, "ECONSIGNADO", "DONE", 1, None),
                    (2, "2026-08", 10, "ECONSIGNADO", "DONE", 1, None),
                ],
            )
            report = module.audit_database(db, policy(require_unique_index=False))
            self.assertFalse(report["ok"])
            self.assertIn("DUPLICATE_IDEMPOTENCY_KEY", str(report["findings"]))

    def test_null_idempotency_component_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "jobs.sqlite3"
            create_db(db, nullable_keys=True)
            insert(db, [(1, "2026-08", None, "ECONSIGNADO", "DONE", 1, None)])
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("NULL_IDEMPOTENCY_KEY", str(report["findings"]))

    def test_invalid_attempt_counter_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "jobs.sqlite3"
            create_db(db)
            insert(db, [(1, "2026-08", 10, "ECONSIGNADO", "DONE", 4, None)])
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("INVALID_ATTEMPT_COUNTER", str(report["findings"]))

    def test_retryable_job_at_attempt_limit_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "jobs.sqlite3"
            create_db(db)
            insert(
                db,
                [(1, "2026-08", 10, "ECONSIGNADO", "FAILED_RETRY", 3, "2026-09-01")],
            )
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("RETRYABLE_STATUS_AT_OR_ABOVE_LIMIT", str(report["findings"]))

    def test_terminal_job_cannot_keep_next_retry_schedule(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "jobs.sqlite3"
            create_db(db)
            insert(db, [(1, "2026-08", 10, "ECONSIGNADO", "DONE", 1, "2026-09-01")])
            report = module.audit_database(db, policy())
            self.assertFalse(report["ok"])
            self.assertIn("TERMINAL_JOB_STILL_SCHEDULED", str(report["findings"]))

    def test_audit_does_not_mutate_database(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "jobs.sqlite3"
            create_db(db)
            insert(db, [(1, "2026-08", 10, "ECONSIGNADO", "DONE", 1, None)])
            before = sha(db)
            report = module.audit_database(db, policy())
            after = sha(db)
            self.assertTrue(report["ok"])
            self.assertEqual(before, after)
            self.assertFalse(report["mutation_performed"])

    def test_missing_required_column_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "jobs.sqlite3"
            conn = sqlite3.connect(db)
            conn.execute("CREATE TABLE jobs(id INTEGER PRIMARY KEY, status TEXT)")
            conn.commit()
            conn.close()
            with self.assertRaises(module.IdempotencyAuditError):
                module.audit_database(db, policy())


if __name__ == "__main__":
    unittest.main()
