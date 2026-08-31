from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_operational_scope_contract.py"
spec = importlib.util.spec_from_file_location("audit_operational_scope_contract", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

POLICY = {
    "closing_table": "fechamento_mensal_cliente",
    "allowed_direct_sql_prefixes": ["modules/closing"],
    "live_scope_patterns": ["conferencia", "mesa", "clientes_conferencia"],
    "forbidden_live_statuses": ["FECHADA", "RETIFICACAO"],
    "facade_markers": ["closing_scope"],
}


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class OperationalScopeContractTests(unittest.TestCase):
    def test_direct_sql_inside_closing_domain_is_allowed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "modules/closing/service.py", '''
def competencia(db):
    return db.execute("SELECT * FROM fechamento_mensal_cliente WHERE competencia=?")
''')
            report = module.audit(root, POLICY)
            self.assertTrue(report["all_ok"], report)

    def test_direct_sql_outside_closing_domain_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "modules/processing/central.py", '''
def carregar(db):
    return db.execute("SELECT * FROM fechamento_mensal_cliente WHERE status='PRONTA'")
''')
            report = module.audit(root, POLICY)
            self.assertIn("DIRECT_CLOSING_SCOPE_SQL_OUTSIDE_DOMAIN", [x["code"] for x in report["findings"]])

    def test_closed_status_in_live_conference_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "modules/closing/service.py", '''
def clientes_conferencia(db):
    return db.execute("SELECT * FROM fechamento_mensal_cliente WHERE status IN ('PRONTA','FECHADA')")
''')
            report = module.audit(root, POLICY)
            codes = [x["code"] for x in report["findings"]]
            self.assertIn("FORBIDDEN_STATUS_IN_LIVE_SCOPE", codes)

    def test_retification_status_in_live_conference_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "modules/closing/service.py", '''
def mesa_conferencia(db):
    return db.execute("SELECT * FROM fechamento_mensal_cliente WHERE status IN ('PRONTA','RETIFICACAO')")
''')
            report = module.audit(root, POLICY)
            finding = next(x for x in report["findings"] if x["code"] == "FORBIDDEN_STATUS_IN_LIVE_SCOPE")
            self.assertEqual(finding["status"], "RETIFICACAO")

    def test_historical_query_outside_live_function_does_not_trigger_live_status_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "modules/closing/report.py", '''
def historico(db):
    return db.execute("SELECT * FROM fechamento_mensal_cliente WHERE status='FECHADA'")
''')
            report = module.audit(root, POLICY)
            self.assertTrue(report["all_ok"], report)

    def test_facade_usage_can_be_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "modules/closing/service.py", '''
def competencia(db):
    return db.execute("SELECT * FROM fechamento_mensal_cliente")
''')
            report = module.audit(root, {**POLICY, "require_facade_usage": True})
            self.assertIn("NO_CANONICAL_SCOPE_FACADE_USAGE", [x["code"] for x in report["findings"]])

    def test_facade_usage_satisfies_requirement(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "modules/closing/service.py", '''
def competencia(db):
    return db.execute("SELECT * FROM fechamento_mensal_cliente")
''')
            write(root, "web/views.py", '''
def processamento():
    return closing_scope.liberados_chamada_atual("08/2026")
''')
            report = module.audit(root, {**POLICY, "require_facade_usage": True})
            self.assertTrue(report["all_ok"], report)

    def test_no_reference_blocks_when_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "service.py", "def consultar():\n    return []\n")
            report = module.audit(root, POLICY)
            self.assertIn("NO_CLOSING_SCOPE_REFERENCE", [x["code"] for x in report["findings"]])

    def test_syntax_error_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "bad.py", "def x(:\n    pass\n")
            report = module.audit(root, {**POLICY, "require_target": False})
            self.assertIn("PARSE_ERROR", [x["code"] for x in report["findings"]])


if __name__ == "__main__":
    unittest.main()
