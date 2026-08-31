from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_manual_selection_gate.py"
spec = importlib.util.spec_from_file_location("audit_manual_selection_gate", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

POLICY = {
    "selection_markers": ["selecion", "selected", "ids", "clientes_ids", "documentos_ids"],
    "generator_markers": ["gerar", "imprimir", "entregar", "saida"],
    "guard_markers": ["filtrar_autorizados", "intersect", "validar_selecao", "autorizar_saida_lote", "gate_saida"],
}


def write(root: Path, text: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "views.py").write_text(text, encoding="utf-8")


class ManualSelectionGateTests(unittest.TestCase):
    def test_selected_ids_with_backend_filter_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def gerar_selecionados(clientes_ids):
    autorizados = filtrar_autorizados(clientes_ids)
    return gerar_saida(autorizados)
''')
            report = module.audit(root, POLICY)
            self.assertTrue(report["all_ok"], report)

    def test_selected_ids_direct_to_generator_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def gerar_selecionados(clientes_ids):
    return gerar_saida(clientes_ids)
''')
            report = module.audit(root, POLICY)
            self.assertIn("MANUAL_SELECTION_REACHES_OUTPUT_WITHOUT_BACKEND_GUARD", [x["code"] for x in report["findings"]])

    def test_guard_can_live_in_called_service(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def entregar_selecionados(documentos_ids):
    return service(documentos_ids)
def service(ids):
    ids = validar_selecao(ids)
    return entregar_documento(ids)
''')
            report = module.audit(root, POLICY)
            self.assertTrue(report["all_ok"], report)

    def test_indirect_generator_without_guard_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def imprimir_selecionados(ids):
    return preparar(ids)
def preparar(ids):
    return imprimir_documentos(ids)
''')
            report = module.audit(root, POLICY)
            self.assertFalse(report["all_ok"])

    def test_selection_target_without_output_is_not_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def salvar_selecionados(ids):
    return list(ids)
''')
            report = module.audit(root, POLICY)
            self.assertTrue(report["all_ok"], report)

    def test_parameter_name_can_define_selection_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def processar(clientes_ids):
    return gerar_saida(clientes_ids)
''')
            report = module.audit(root, POLICY)
            self.assertFalse(report["all_ok"])
            self.assertEqual(report["target_count"], 1)

    def test_no_target_blocks_when_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "def consultar():\n    return 1\n")
            report = module.audit(root, POLICY)
            self.assertIn("NO_MANUAL_SELECTION_TARGET", [x["code"] for x in report["findings"]])

    def test_syntax_error_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "def selecionados(:\n    pass\n")
            report = module.audit(root, {**POLICY, "require_target": False})
            self.assertIn("PARSE_ERROR", [x["code"] for x in report["findings"]])


if __name__ == "__main__":
    unittest.main()
