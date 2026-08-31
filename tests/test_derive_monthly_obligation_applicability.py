from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "derive_monthly_obligation_applicability.py"
spec = importlib.util.spec_from_file_location("derive_monthly_obligation_applicability", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def base(**overrides):
    value = {
        "client_id": "c1",
        "competence": "08/2026",
        "profile": "NORMAL",
        "mei": False,
        "dae_expected": False,
        "generic_fgts_expected": True,
        "fgts_authoritative_base_available": True,
        "fgts_authoritative_amount": "100.00",
        "federal_authoritative_available": True,
        "federal_gross": "200.00",
        "federal_deductions": "20.00",
        "federal_balance": "180.00",
        "absence_integral": False,
        "monetary_incidence": True,
    }
    value.update(overrides)
    return value


class MonthlyApplicabilityTests(unittest.TestCase):
    def test_fgts_zero_authoritative_overrides_generic_expectation(self):
        report = module.derive(base(fgts_authoritative_amount="0.00", generic_fgts_expected=True))
        fgts = report["obligations"]["FGTS_DIGITAL"]
        self.assertFalse(fgts["applicable"])
        self.assertEqual(fgts["reason"], "VALOR_AUTORITATIVO_ZERO")
        self.assertTrue(fgts["generic_expectation_overridden"])

    def test_positive_fgts_authoritative_remains_applicable_even_with_absence(self):
        report = module.derive(base(absence_integral=True, monetary_incidence=False, fgts_authoritative_amount="80.00"))
        self.assertTrue(report["obligations"]["FGTS_DIGITAL"]["applicable"])
        self.assertEqual(report["obligations"]["FGTS_DIGITAL"]["reason"], "INCIDENCIA_AUTORITATIVA_POSITIVA")

    def test_mei_dae_suppresses_generic_fgts_digital(self):
        report = module.derive(base(profile="MEI", mei=True, dae_expected=True, fgts_authoritative_base_available=False, fgts_authoritative_amount=None))
        self.assertFalse(report["obligations"]["FGTS_DIGITAL"]["applicable"])
        self.assertEqual(report["obligations"]["FGTS_DIGITAL"]["reason"], "PERFIL_MEI_RECOLHIMENTO_VIA_DAE")
        self.assertTrue(report["obligations"]["DAE"]["applicable"])

    def test_non_mei_dae_is_not_applicable(self):
        report = module.derive(base())
        self.assertFalse(report["obligations"]["DAE"]["applicable"])
        self.assertEqual(report["obligations"]["DAE"]["reason"], "PERFIL_NAO_MEI")

    def test_federal_balance_uses_gross_minus_deductions(self):
        report = module.derive(base(federal_gross="500.00", federal_deductions="120.00", federal_balance="380.00"))
        self.assertTrue(report["all_ok"], report)
        self.assertTrue(report["obligations"]["DARF_FOLHA"]["applicable"])
        self.assertEqual(report["obligations"]["DARF_FOLHA"]["balance"], "380.00")

    def test_deductions_can_zero_federal_balance(self):
        report = module.derive(base(federal_gross="500.00", federal_deductions="500.00", federal_balance="0.00"))
        darf = report["obligations"]["DARF_FOLHA"]
        self.assertFalse(darf["applicable"])
        self.assertEqual(darf["reason"], "SALDO_AUTORITATIVO_ZERO")

    def test_inconsistent_federal_net_balance_blocks(self):
        report = module.derive(base(federal_gross="500.00", federal_deductions="100.00", federal_balance="450.00"))
        self.assertIn("FEDERAL_NET_BALANCE_INCONSISTENT", [x["code"] for x in report["findings"]])
        self.assertFalse(report["all_ok"])

    def test_integral_absence_without_monetary_incidence_makes_sources_not_applicable_when_no_authoritative_base(self):
        report = module.derive(base(
            fgts_authoritative_base_available=False,
            fgts_authoritative_amount=None,
            federal_authoritative_available=False,
            federal_gross=None,
            federal_deductions=None,
            federal_balance=None,
            absence_integral=True,
            monetary_incidence=False,
            absence_reason="FALTAS_INTEGRAIS",
        ))
        self.assertFalse(report["obligations"]["FGTS_DIGITAL"]["applicable"])
        self.assertFalse(report["obligations"]["DARF_FOLHA"]["applicable"])
        self.assertEqual(report["obligations"]["FGTS_DIGITAL"]["absence_reason"], "FALTAS_INTEGRAIS")

    def test_absence_does_not_override_authoritative_positive_fgts(self):
        report = module.derive(base(
            fgts_authoritative_amount="90.00",
            absence_integral=True,
            monetary_incidence=False,
            absence_reason="ACIDENTE",
        ))
        self.assertTrue(report["obligations"]["FGTS_DIGITAL"]["applicable"])

    def test_generic_fgts_expectation_is_fallback_only_without_authoritative_base(self):
        report = module.derive(base(
            fgts_authoritative_base_available=False,
            fgts_authoritative_amount=None,
            generic_fgts_expected=True,
        ))
        self.assertTrue(report["obligations"]["FGTS_DIGITAL"]["applicable"])
        self.assertEqual(report["obligations"]["FGTS_DIGITAL"]["evidence_strength"], "GENERIC_PROFILE")

    def test_no_fgts_evidence_and_no_generic_expectation_requires_review(self):
        report = module.derive(base(
            fgts_authoritative_base_available=False,
            fgts_authoritative_amount=None,
            generic_fgts_expected=False,
        ))
        self.assertIn("FGTS_APPLICABILITY_EVIDENCE_INSUFFICIENT", [x["code"] for x in report["findings"]])
        self.assertEqual(report["obligations"]["FGTS_DIGITAL"]["state"], "REVIEW_REQUIRED")

    def test_missing_authoritative_federal_balance_requires_review(self):
        report = module.derive(base(federal_authoritative_available=True, federal_balance=None))
        self.assertIn("FEDERAL_AUTHORITATIVE_BALANCE_MISSING", [x["code"] for x in report["findings"]])

    def test_report_hash_is_stable(self):
        first = module.derive(base())
        second = module.derive(base())
        self.assertEqual(first["report_sha256"], second["report_sha256"])


if __name__ == "__main__":
    unittest.main()
