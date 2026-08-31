from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

SCRIPT = SCRIPTS / "validate_temporal_competence_evidence.py"
spec = importlib.util.spec_from_file_location("validate_temporal_competence_evidence", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def policy(**overrides) -> dict:
    data = {
        "version": 1,
        "document_types": ["IRRF"],
        "document_type_field": "tipo_documento",
        "basis_date_field": "data_pagamento",
        "competence_field": "competencia",
        "method_field": "competencia_metodo",
        "evidence_field": "competencia_evidencias",
        "allowed_methods": ["PAGAMENTO_DOCUMENTO"],
        "required_evidence_tokens": ["pagamento", "2026"],
        "competence_rule": "SAME_MONTH_AS_BASIS_DATE",
        "allow_non_target_records": True,
    }
    data.update(overrides)
    return data


def record(**overrides) -> dict:
    data = {
        "tipo_documento": "IRRF",
        "data_pagamento": "2026-09-05",
        "competencia": "2026-09",
        "competencia_metodo": "PAGAMENTO_DOCUMENTO",
        "competencia_evidencias": ["Data de pagamento: 05/09/2026"],
        "competencia_folha": "2026-08",
    }
    data.update(overrides)
    return data


class TemporalCompetenceEvidenceTests(unittest.TestCase):
    def test_valid_irrf_payment_competence_passes(self):
        report = module.validate_records([record()], policy())
        self.assertTrue(report["ok"])
        self.assertEqual(report["summary"]["target_records_checked"], 1)

    def test_payroll_month_does_not_override_declared_payment_basis(self):
        item = record(competencia_folha="2026-08", competencia="2026-09")
        report = module.validate_records([item], policy())
        self.assertTrue(report["ok"])

    def test_competence_from_payroll_month_is_blocked_when_payment_is_next_month(self):
        item = record(competencia="2026-08")
        report = module.validate_records([item], policy())
        self.assertFalse(report["ok"])
        self.assertIn("TEMPORAL_COMPETENCE_MISMATCH", str(report["findings"]))

    def test_missing_or_invalid_payment_date_blocks(self):
        report = module.validate_records([record(data_pagamento="05/09/2026")], policy())
        self.assertFalse(report["ok"])
        self.assertIn("MISSING_OR_INVALID_TEMPORAL_BASIS", str(report["findings"]))

    def test_invalid_competence_format_blocks(self):
        report = module.validate_records([record(competencia="09/2026")], policy())
        self.assertFalse(report["ok"])
        self.assertIn("MISSING_OR_INVALID_COMPETENCE", str(report["findings"]))

    def test_wrong_competence_method_blocks(self):
        report = module.validate_records(
            [record(competencia_metodo="MES_ARQUIVO")], policy()
        )
        self.assertFalse(report["ok"])
        self.assertIn("INVALID_COMPETENCE_METHOD", str(report["findings"]))

    def test_missing_evidence_blocks(self):
        report = module.validate_records([record(competencia_evidencias=None)], policy())
        self.assertFalse(report["ok"])
        self.assertIn("MISSING_TEMPORAL_EVIDENCE", str(report["findings"]))

    def test_incomplete_evidence_blocks(self):
        report = module.validate_records(
            [record(competencia_evidencias=["competência calculada"])], policy()
        )
        self.assertFalse(report["ok"])
        self.assertIn("TEMPORAL_EVIDENCE_INCOMPLETE", str(report["findings"]))

    def test_non_target_records_are_skipped_when_target_exists(self):
        other = {
            "tipo_documento": "FGTS",
            "competencia": "qualquer",
        }
        report = module.validate_records([other, record()], policy())
        self.assertTrue(report["ok"])
        self.assertEqual(report["summary"]["non_target_records_skipped"], 1)

    def test_no_irrf_records_blocks_validation(self):
        report = module.validate_records(
            [{"tipo_documento": "FGTS"}], policy()
        )
        self.assertFalse(report["ok"])
        self.assertIn("NO_TARGET_RECORDS", str(report["findings"]))


if __name__ == "__main__":
    unittest.main()
