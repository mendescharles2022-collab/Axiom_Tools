from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_get_read_purity.py"
spec = importlib.util.spec_from_file_location("audit_get_read_purity", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

POLICY = {
    "mutator_markers": ["sincronizar", "salvar", "fechar", "promover", "recalcular", "commit"],
    "max_call_depth": 8,
}


def write(root: Path, text: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "views.py").write_text(text, encoding="utf-8")


class GetReadPurityTests(unittest.TestCase):
    def test_pure_get_route_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
class BP:
    def route(self, *args, **kwargs):
        return lambda f: f
bp = BP()
@bp.route("/conferencia")
def conferencia():
    return montar_projecao()
def montar_projecao():
    return []
''')
            report = module.audit(root, POLICY)
            self.assertTrue(report["all_ok"], report)

    def test_direct_mutator_call_in_get_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
class BP:
    def route(self, *args, **kwargs): return lambda f: f
bp = BP()
@bp.route("/conferencia", methods=["GET"])
def conferencia():
    sincronizar_resultados_conferencia()
    return []
''')
            report = module.audit(root, POLICY)
            self.assertIn("GET_MUTATION_REACHABLE", [x["code"] for x in report["findings"]])

    def test_indirect_mutation_through_helper_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
class BP:
    def route(self, *args, **kwargs): return lambda f: f
bp = BP()
@bp.route("/processamento/guias")
def guias():
    return montar_conferencia()
def montar_conferencia():
    return conferir_cliente()
def conferir_cliente():
    fechar_cliente()
    return {}
''')
            report = module.audit(root, POLICY)
            finding = next(x for x in report["findings"] if x["code"] == "GET_MUTATION_REACHABLE")
            self.assertEqual(finding["call_chain"], ["guias", "montar_conferencia", "conferir_cliente"])

    def test_write_sql_literal_in_get_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
class BP:
    def route(self, *args, **kwargs): return lambda f: f
bp = BP()
@bp.route("/fechamento")
def tela(db):
    db.execute("UPDATE fechamento_mensal_cliente SET status='FECHADA'")
    return "ok"
''')
            report = module.audit(root, POLICY)
            finding = next(x for x in report["findings"] if x["code"] == "GET_MUTATION_REACHABLE")
            self.assertEqual(finding["mutation"]["code"], "WRITE_SQL")

    def test_post_only_route_is_not_a_get_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
class BP:
    def route(self, *args, **kwargs): return lambda f: f
bp = BP()
@bp.route("/acao", methods=["POST"])
def acao():
    salvar_decisao()
''')
            report = module.audit(root, {**POLICY, "require_get_route": False})
            self.assertTrue(report["all_ok"], report)
            self.assertEqual(report["get_route_count"], 0)

    def test_get_and_post_route_is_still_a_get_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
class BP:
    def route(self, *args, **kwargs): return lambda f: f
bp = BP()
@bp.route("/misturada", methods=["GET", "POST"])
def misturada():
    salvar_decisao()
''')
            report = module.audit(root, POLICY)
            self.assertFalse(report["all_ok"])
            self.assertEqual(report["get_route_count"], 1)

    def test_no_get_route_blocks_when_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "def helper():\n    return 1\n")
            report = module.audit(root, POLICY)
            self.assertIn("NO_GET_ROUTE", [x["code"] for x in report["findings"]])

    def test_syntax_error_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "def quebrado(:\n    pass\n")
            report = module.audit(root, {**POLICY, "require_get_route": False})
            self.assertIn("PARSE_ERROR", [x["code"] for x in report["findings"]])


if __name__ == "__main__":
    unittest.main()
