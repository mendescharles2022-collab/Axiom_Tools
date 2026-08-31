from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_special_competence_calendar.py"
spec = importlib.util.spec_from_file_location("validate_special_competence_calendar", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def rec(**overrides):
    value = {
        "document_id": "d1",
        "client_id": "c1",
        "competence": "13/2026",
        "competence_kind": "THIRTEENTH",
        "method": "EXPLICITA_DOCUMENTO",
        "evidence": "PA 13/2026",
        "calendar_rule_id": "",
    }
    value.update(overrides)
    return value


class SpecialCompetenceCalendarTests(unittest.TestCase):
    def test_explicit_thirteenth_passes(self):
        report = module.validate([rec()])
        self.assertTrue(report["all_ok"], report)
        self.assertEqual(report["records"][0]["identity_kind"], "THIRTEENTH")

    def test_thirteenth_cannot_be_normal_month(self):
        report = module.validate([rec(competence_kind="NORMAL")])
        self.assertIn("THIRTEENTH_MISCLASSIFIED_AS_NORMAL_MONTH", [x["code"] for x in report["findings"]])

    def test_thirteenth_generic_calendar_method_blocks(self):
        report = module.validate([rec(method="CALENDARIO_ESOCIAL")])
        self.assertIn("THIRTEENTH_WITH_GENERIC_CALENDAR_METHOD", [x["code"] for x in report["findings"]])

    def test_inferred_thirteenth_requires_exception_rule(self):
        report = module.validate([rec(method="CALENDARIO_ESOCIAL_EXCECAO", calendar_rule_id="")])
        self.assertIn("THIRTEENTH_INFERENCE_WITHOUT_EXCEPTION_RULE", [x["code"] for x in report["findings"]])

    def test_inferred_thirteenth_with_rule_passes(self):
        report = module.validate([rec(method="CALENDARIO_ESOCIAL_EXCECAO", calendar_rule_id="13O_2026")])
        self.assertTrue(report["all_ok"], report)

    def test_december_generic_calendar_method_blocks(self):
        report = module.validate([rec(
            competence="12/2026",
            competence_kind="DECEMBER",
            method="CALENDARIO_ESOCIAL",
            evidence="janela dezembro",
        )])
        self.assertIn("DECEMBER_WITH_GENERIC_CALENDAR_METHOD", [x["code"] for x in report["findings"]])

    def test_december_inferred_with_exception_rule_passes(self):
        report = module.validate([rec(
            competence="12/2026",
            competence_kind="DECEMBER",
            method="CALENDARIO_ESOCIAL_EXCECAO",
            evidence="janela dezembro",
            calendar_rule_id="DEZEMBRO_2026",
        )])
        self.assertTrue(report["all_ok"], report)

    def test_normal_month_cannot_use_thirteenth_kind(self):
        report = module.validate([rec(
            competence="11/2026",
            competence_kind="THIRTEENTH",
            method="EXPLICITA_DOCUMENTO",
            evidence="11/2026",
        )])
        self.assertIn("SPECIAL_KIND_ON_NORMAL_MONTH", [x["code"] for x in report["findings"]])

    def test_december_and_thirteenth_are_distinct_identities(self):
        december = rec(
            document_id="dec",
            competence="12/2026",
            competence_kind="DECEMBER",
            method="EXPLICITA_DOCUMENTO",
            evidence="12/2026",
        )
        thirteenth = rec(document_id="13")
        report = module.validate([december, thirteenth])
        self.assertTrue(report["all_ok"], report)
        identities = {x["identity_kind"] for x in report["records"]}
        self.assertEqual(identities, {"DECEMBER", "THIRTEENTH"})

    def test_duplicate_thirteenth_identity_blocks(self):
        report = module.validate([rec(document_id="a"), rec(document_id="b")])
        self.assertIn("DUPLICATE_SPECIAL_COMPETENCE_IDENTITY", [x["code"] for x in report["findings"]])

    def test_special_competence_requires_provenance(self):
        report = module.validate([rec(method="", evidence="")])
        self.assertIn("SPECIAL_COMPETENCE_PROVENANCE_MISSING", [x["code"] for x in report["findings"]])

    def test_invalid_competence_format_blocks(self):
        report = module.validate([rec(competence="14/2026")])
        self.assertIn("INVALID_COMPETENCE_FORMAT", [x["code"] for x in report["findings"]])

    def test_report_hash_is_stable(self):
        first = module.validate([rec()])
        second = module.validate([rec()])
        self.assertEqual(first["report_sha256"], second["report_sha256"])


if __name__ == "__main__":
    unittest.main()
