from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import run_sqlite_invariants as runner  # noqa: E402


def create_db(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
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
            natureza TEXT,
            snapshot TEXT
        );
        """
    )
    return conn


class ClosingConfirmedInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec = runner.load_spec(
            ROOT / "config" / "sqlite_invariants_closing_confirmed_v8.json"
        )

    def test_closed_client_with_matching_version_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            conn = create_db(db)
            conn.execute(
                "INSERT INTO fechamento_mensal_cliente VALUES (?,?,?,?)",
                ("08/2026", 1, "FECHADA", 1),
            )
            conn.execute(
                "INSERT INTO fechamento_mensal_versao VALUES (?,?,?,?,?)",
                ("08/2026", 1, 1, "FECHAMENTO", "{}"),
            )
            conn.commit()
            conn.close()

            report = runner.run_invariants(db, self.spec)
            self.assertTrue(report["ok"])
            self.assertEqual(report["summary"]["passed"], 2)

    def test_closed_client_without_any_version_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            conn = create_db(db)
            conn.execute(
                "INSERT INTO fechamento_mensal_cliente VALUES (?,?,?,?)",
                ("08/2026", 2, "FECHADA", None),
            )
            conn.commit()
            conn.close()

            report = runner.run_invariants(db, self.spec)
            self.assertFalse(report["ok"])
            failed = {item["id"] for item in report["results"] if not item["passed"]}
            self.assertIn("CLOSING_FECHADA_WITHOUT_VERSION", failed)

    def test_current_version_pointing_to_missing_version_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            conn = create_db(db)
            conn.execute(
                "INSERT INTO fechamento_mensal_cliente VALUES (?,?,?,?)",
                ("08/2026", 3, "PRONTA", 2),
            )
            conn.execute(
                "INSERT INTO fechamento_mensal_versao VALUES (?,?,?,?,?)",
                ("08/2026", 3, 1, "FECHAMENTO", "{}"),
            )
            conn.commit()
            conn.close()

            report = runner.run_invariants(db, self.spec)
            self.assertFalse(report["ok"])
            failed = {item["id"] for item in report["results"] if not item["passed"]}
            self.assertIn("CLOSING_CURRENT_VERSION_MUST_EXIST", failed)

    def test_open_client_without_version_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "db.sqlite3"
            conn = create_db(db)
            conn.execute(
                "INSERT INTO fechamento_mensal_cliente VALUES (?,?,?,?)",
                ("08/2026", 4, "PRONTA", None),
            )
            conn.commit()
            conn.close()

            report = runner.run_invariants(db, self.spec)
            self.assertTrue(report["ok"])


if __name__ == "__main__":
    unittest.main()
