from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

SCRIPT = SCRIPTS / "audit_sqlite_cas_contract.py"
spec = importlib.util.spec_from_file_location("audit_sqlite_cas_contract", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def policy(**overrides) -> dict:
    data = {
        "version": 1,
        "block_unresolved_execute": False,
        "tables": [
            {
                "table": "fechamento_mensal_cliente",
                "key_columns": ["competencia", "cliente_id"],
                "cas_columns": ["status", "chamada", "revisao"],
                "require_rowcount_check": True,
            }
        ],
    }
    data.update(overrides)
    return data


class SqliteCasContractTests(unittest.TestCase):
    def test_update_only_by_business_key_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "conn.execute(\"UPDATE fechamento_mensal_cliente SET status=? WHERE competencia=? AND cliente_id=?\", params)\n",
            )
            report = module.audit_tree(root, policy())
            self.assertFalse(report["static_ok"])
            text = str(report["findings"])
            self.assertIn("MISSING_CAS_GUARD", text)
            self.assertIn("ROWCOUNT_NOT_CHECKED", text)

    def test_guarded_update_with_rowcount_check_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "cur = conn.execute(\"UPDATE fechamento_mensal_cliente SET status=? WHERE competencia=? AND cliente_id=? AND status=?\", params)\n"
                "if cur.rowcount != 1:\n    raise RuntimeError('conflito')\n",
            )
            report = module.audit_tree(root, policy())
            self.assertTrue(report["static_ok"])
            self.assertEqual(report["summary"]["protected_updates"], 1)

    def test_guard_without_rowcount_check_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "conn.execute(\"UPDATE fechamento_mensal_cliente SET status=? WHERE competencia=? AND cliente_id=? AND revisao=?\", params)\n",
            )
            report = module.audit_tree(root, policy())
            self.assertFalse(report["static_ok"])
            self.assertIn("ROWCOUNT_NOT_CHECKED", str(report["findings"]))

    def test_missing_business_key_column_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "cur = conn.execute(\"UPDATE fechamento_mensal_cliente SET status=? WHERE cliente_id=? AND status=?\", params)\n"
                "print(cur.rowcount)\n",
            )
            report = module.audit_tree(root, policy())
            self.assertFalse(report["static_ok"])
            self.assertIn("MISSING_KEY_COLUMNS:competencia", str(report["findings"]))

    def test_unrelated_table_is_ignored(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "a.py", "conn.execute(\"UPDATE outra SET x=? WHERE id=?\", p)\n")
            report = module.audit_tree(root, policy())
            self.assertTrue(report["static_ok"])
            self.assertEqual(report["summary"]["protected_updates"], 0)

    def test_multiline_lowercase_sql_is_recognized(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "cur = conn.execute('''\nupdate fechamento_mensal_cliente\nset status=?\nwhere competencia=? and cliente_id=? and chamada=?\n''', p)\n"
                "assert cur.rowcount == 1\n",
            )
            report = module.audit_tree(root, policy())
            self.assertTrue(report["static_ok"])

    def test_sql_constant_variable_is_resolved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(
                root / "a.py",
                "SQL = \"UPDATE fechamento_mensal_cliente SET status=? WHERE competencia=? AND cliente_id=? AND revisao=?\"\n"
                "cur = conn.execute(SQL, p)\n"
                "if cur.rowcount == 0:\n    raise RuntimeError('stale')\n",
            )
            report = module.audit_tree(root, policy())
            self.assertTrue(report["static_ok"])
            self.assertEqual(report["summary"]["protected_updates"], 1)

    def test_unresolved_execute_can_be_promoted_to_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "a.py", "conn.execute(build_sql(), p)\n")
            permissive = module.audit_tree(root, policy())
            strict_spec = policy(block_unresolved_execute=True)
            strict = module.audit_tree(root, strict_spec)
            self.assertTrue(permissive["static_ok"])
            self.assertEqual(permissive["summary"]["unresolved_execute_calls"], 1)
            self.assertFalse(strict["static_ok"])
            self.assertIn("UNRESOLVED_EXECUTE_SQL", str(strict["findings"]))


if __name__ == "__main__":
    unittest.main()
