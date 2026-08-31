from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_output_gate_contract.py"
spec = importlib.util.spec_from_file_location("audit_output_gate_contract", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

POLICY = {
    "entrypoint_patterns": ["gerar", "imprimir", "entregar", "saida"],
    "generator_markers": ["gerar_pdf", "gerar_saida", "imprimir_documento", "entregar_documento"],
    "gate_markers": ["autorizar_saida", "output_gate", "gate_saida"],
    "forbidden_auth_literals": ["PROCESSADO"],
    "required_auth_literals": ["FECHADA"],
}


def write(root: Path, text: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "delivery.py").write_text(text, encoding="utf-8")


class OutputGateContractTests(unittest.TestCase):
    def test_generation_with_canonical_gate_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def gerar_cliente(cliente_id):
    autorizar_saida(cliente_id, estado="FECHADA")
    return gerar_pdf(cliente_id)
''')
            report = module.audit(root, POLICY)
            self.assertTrue(report["all_ok"], report)

    def test_direct_generation_without_gate_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def gerar_cliente(cliente_id):
    return gerar_pdf(cliente_id)
''')
            report = module.audit(root, POLICY)
            self.assertIn("OUTPUT_PATH_WITHOUT_GATE", [x["code"] for x in report["findings"]])

    def test_route_bypass_without_gate_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
class BP:
    def route(self, *args, **kwargs): return lambda f: f
bp = BP()
@bp.route("/gerar/<int:id>", methods=["POST"])
def rota(id):
    return gerar_pdf(id)
''')
            report = module.audit(root, POLICY)
            self.assertFalse(report["all_ok"])

    def test_gate_inside_generator_protects_callers(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
class BP:
    def route(self, *args, **kwargs): return lambda f: f
bp = BP()
@bp.route("/gerar", methods=["POST"])
def rota():
    return gerar_saida(1)
def gerar_saida(cliente_id):
    autorizar_saida(cliente_id, estado="FECHADA")
    return gerar_pdf(cliente_id)
''')
            report = module.audit(root, POLICY)
            self.assertTrue(report["all_ok"], report)

    def test_processado_as_authorization_without_fechada_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def gerar_cliente(status):
    if status == "PROCESSADO":
        autorizar_saida(1)
        return gerar_pdf(1)
''')
            report = module.audit(root, POLICY)
            self.assertIn("FORBIDDEN_AUTH_SIGNAL_WITHOUT_CLOSED_STATE", [x["code"] for x in report["findings"]])

    def test_processado_literal_with_closed_state_is_not_flagged_by_signal_rule(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def gerar_cliente(status):
    estado_final = "FECHADA"
    tecnico = "PROCESSADO"
    autorizar_saida(1, estado=estado_final)
    return gerar_pdf(1)
''')
            report = module.audit(root, POLICY)
            self.assertTrue(report["all_ok"], report)

    def test_indirect_generator_without_gate_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def entregar_cliente(cliente_id):
    return preparar(cliente_id)
def preparar(cliente_id):
    return gerar_pdf(cliente_id)
''')
            report = module.audit(root, POLICY)
            finding = next(x for x in report["findings"] if x["code"] == "OUTPUT_PATH_WITHOUT_GATE")
            self.assertTrue(any("preparar" in chain for chain in finding["generator_chains"]))

    def test_no_entrypoint_blocks_when_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "def consultar():\n    return 1\n")
            report = module.audit(root, POLICY)
            self.assertIn("NO_OUTPUT_ENTRYPOINT", [x["code"] for x in report["findings"]])

    def test_syntax_error_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "def gerar_cliente(:\n    pass\n")
            report = module.audit(root, {**POLICY, "require_entrypoint": False})
            self.assertIn("PARSE_ERROR", [x["code"] for x in report["findings"]])


if __name__ == "__main__":
    unittest.main()
