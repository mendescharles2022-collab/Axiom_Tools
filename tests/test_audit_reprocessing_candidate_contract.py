from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_reprocessing_candidate_contract.py"
spec = importlib.util.spec_from_file_location("audit_reprocessing_candidate_contract", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

POLICY = {
    "reprocess_name_patterns": ["reprocess"],
    "current_tables": ["processamento_arquivo", "processamento_item_pessoa"],
    "candidate_markers": ["candidato", "candidate"],
    "promotion_markers": ["promover", "promote"],
    "recalc_markers": ["recalcular", "conferencia", "recompute"],
}


def write(root: Path, text: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "service.py").write_text(text, encoding="utf-8")


class ReprocessingCandidateContractTests(unittest.TestCase):
    def test_destructive_delete_of_current_interpretation_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def reprocessar_arquivo(db):
    db.execute("DELETE FROM processamento_item_pessoa WHERE arquivo_id=?", (1,))
    db.execute("DELETE FROM processamento_arquivo WHERE id=?", (1,))
    db.commit()
    candidato = ler_novo()
    promover_candidato(candidato)
    recalcular_conferencia()
''')
            report = module.audit(root, POLICY)
            codes = [x["code"] for x in report["findings"]]
            self.assertIn("DESTRUCTIVE_CURRENT_DELETE", codes)
            self.assertIn("COMMIT_BEFORE_CANDIDATE", codes)
            self.assertFalse(report["all_ok"])

    def test_safe_candidate_then_promotion_then_recalc_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def reprocessar_arquivo(db):
    candidato = criar_candidato()
    validar_candidate(candidato)
    promover_candidato(candidato)
    recalcular_conferencia()
''')
            report = module.audit(root, POLICY)
            self.assertTrue(report["all_ok"], report)
            self.assertEqual(report["target_count"], 1)

    def test_missing_candidate_flow_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def reprocessar_arquivo():
    promover_resultado()
    recalcular_conferencia()
''')
            codes = [x["code"] for x in module.audit(root, POLICY)["findings"]]
            self.assertIn("MISSING_CANDIDATE_FLOW", codes)

    def test_missing_promotion_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def reprocessar_arquivo():
    candidato = criar_candidato()
    recalcular_conferencia(candidato)
''')
            codes = [x["code"] for x in module.audit(root, POLICY)["findings"]]
            self.assertIn("MISSING_PROMOTION_STEP", codes)

    def test_recalc_before_promotion_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def reprocessar_arquivo():
    candidato = criar_candidato()
    recalcular_conferencia(candidato)
    promover_candidato(candidato)
''')
            codes = [x["code"] for x in module.audit(root, POLICY)["findings"]]
            self.assertIn("RECALC_NOT_AFTER_PROMOTION", codes)

    def test_delete_of_unrelated_table_can_be_ignored_by_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, '''
def reprocessar_arquivo(db):
    candidato = criar_candidato()
    db.execute("DELETE FROM cache_temporario WHERE id=?", (1,))
    promover_candidato(candidato)
    recalcular_conferencia()
''')
            report = module.audit(root, POLICY)
            self.assertTrue(report["all_ok"], report)

    def test_no_target_is_blocked_when_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "def consultar():\n    return 1\n")
            report = module.audit(root, POLICY)
            self.assertIn("NO_REPROCESS_TARGET", [x["code"] for x in report["findings"]])

    def test_syntax_error_is_not_silenced(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, "def reprocessar_arquivo(:\n    pass\n")
            report = module.audit(root, POLICY)
            self.assertIn("PARSE_ERROR", [x["code"] for x in report["findings"]])


if __name__ == "__main__":
    unittest.main()
