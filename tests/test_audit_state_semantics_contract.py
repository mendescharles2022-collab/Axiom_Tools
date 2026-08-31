from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_state_semantics_contract.py"
spec = importlib.util.spec_from_file_location("audit_state_semantics_contract", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

POLICY = {
    "forbidden_mappings": [
        {"id": "B11_PRONTA_CONFERENCIA", "source": "PRONTA", "target_regex": "confer"},
    ],
    "forbidden_function_pairs": [
        {"id": "B37_DUAL_SESSION_TRUTH", "left": "COM_PENDENCIAS", "right": "PROCESSAMENTO_CONCLUIDO"},
    ],
}


def write(root: Path, text: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "status.py").write_text(text, encoding="utf-8")


class StateSemanticsContractTests(unittest.TestCase):
    def test_pronta_mapped_to_em_conferencia_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
STATUS = {
    "PRONTA": "Em conferência",
    "FECHADA": "Fechada",
}
''')
            report = module.audit(root, POLICY)
            self.assertIn("FORBIDDEN_STATE_LABEL_MAPPING", [x["code"] for x in report["findings"]])

    def test_pronta_mapped_to_waiting_processing_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
STATUS = {
    "PRONTA": "Aguardando processamento",
}
''')
            report = module.audit(root, POLICY)
            self.assertTrue(report["all_ok"], report)

    def test_dual_session_truth_in_same_function_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def status_sessao(percentual):
    persistido = "COM_PENDENCIAS"
    if percentual == 100:
        return "PROCESSAMENTO_CONCLUIDO"
    return persistido
''')
            report = module.audit(root, POLICY)
            finding = next(x for x in report["findings"] if x["code"] == "FORBIDDEN_STATE_COOCCURRENCE")
            self.assertEqual(finding["rule_id"], "B37_DUAL_SESSION_TRUTH")

    def test_same_literals_in_different_functions_do_not_block(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def legado():
    return "COM_PENDENCIAS"
def label_novo():
    return "PROCESSAMENTO_CONCLUIDO"
''')
            report = module.audit(root, POLICY)
            self.assertTrue(report["all_ok"], report)

    def test_mapping_rule_is_case_insensitive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, 'STATUS = {"pronta": "EM CONFERENCIA"}\n')
            report = module.audit(root, POLICY)
            self.assertFalse(report["all_ok"])

    def test_unrelated_mapping_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, 'STATUS = {"PROCESSANDO": "Em processamento"}\n')
            report = module.audit(root, POLICY)
            self.assertTrue(report["all_ok"], report)

    def test_mapping_target_can_be_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "def x():\n    return 1\n")
            report = module.audit(root, {**POLICY, "require_mapping_target": True})
            self.assertIn("NO_STATE_MAPPING_TARGET", [x["code"] for x in report["findings"]])

    def test_syntax_error_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "def x(:\n    pass\n")
            report = module.audit(root, POLICY)
            self.assertIn("PARSE_ERROR", [x["code"] for x in report["findings"]])


if __name__ == "__main__":
    unittest.main()
