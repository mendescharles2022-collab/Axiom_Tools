from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_dominio_extraction_contract.py"
spec = importlib.util.spec_from_file_location("validate_dominio_extraction_contract", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def prov(value, source, section, label):
    return {
        "value": value,
        "source": source,
        "section": section,
        "label": label,
        "page": 2,
        "rule": "REGRA_CANONICA_V8",
    }


def p_da_silva():
    return {
        "document": "21537-Extrato Mensal.pdf",
        "competence": "08/2026",
        "competence_method": "EXPLICITA_DOCUMENTO",
        "competence_evidence": "cabecalho competência 08/2026",
        "people": [
            {
                "line_type": "Contr.",
                "link": "Diretor",
                "category": "CONTRIBUINTE",
                "situation": "Trabalhando",
                "fgts": "0.00",
            }
        ],
        "aggregates": {"employees": 0, "contributors": 1},
        "fgts_monthly": prov("0.00", "INSS_FGTS_PIS_ISS_VALOR_FGTS", "INSS FGTS, PIS e ISS", "Valor do FGTS"),
        "federal_balance": prov("220.00", "APURACAO_TRIBUTOS_FEDERAIS_SALDO", "Apuração Tributos Federais", "Saldo à recolher"),
    }


def pecas_2a():
    return {
        "document": "Extrato Mensal.pdf",
        "competence": "07/2026",
        "competence_method": "EXPLICITA_DOCUMENTO",
        "competence_evidence": "cabecalho competência 07/2026",
        "people": [
            {"line_type": "Empr.", "link": "Celetista", "category": "EMPREGADO", "situation": "Trabalhando", "fgts": "209.57"},
            {"line_type": "Empr.", "link": "Celetista", "category": "EMPREGADO", "situation": "Trabalhando", "fgts": "136.00"},
            {"line_type": "Contr.", "link": "Diretor", "category": "CONTRIBUINTE", "situation": "Trabalhando", "fgts": "0.00"},
        ],
        "aggregates": {"employees": 2, "contributors": 1},
        "fgts_monthly": prov("345.57", "INSS_FGTS_PIS_ISS_VALOR_FGTS", "INSS FGTS, PIS e ISS", "Valor do FGTS"),
        "federal_balance": prov("518.44", "APURACAO_TRIBUTOS_FEDERAIS_SALDO", "Apuração Tributos Federais", "Saldo à recolher"),
    }


class DominioExtractionContractTests(unittest.TestCase):
    def test_p_da_silva_fixture_passes(self):
        report = module.validate(p_da_silva())
        self.assertTrue(report["all_ok"], report)
        self.assertEqual(report["derived_employees"], 0)
        self.assertEqual(report["derived_contributors"], 1)
        self.assertEqual(report["employee_fgts_sum"], "0.00")

    def test_2a_pecas_fixture_passes(self):
        report = module.validate(pecas_2a())
        self.assertTrue(report["all_ok"], report)
        self.assertEqual(report["derived_employees"], 2)
        self.assertEqual(report["derived_contributors"], 1)
        self.assertEqual(report["employee_fgts_sum"], "345.57")

    def test_director_working_cannot_be_employee(self):
        record = p_da_silva()
        record["people"][0]["category"] = "EMPREGADO"
        report = module.validate(record)
        codes = [x["code"] for x in report["findings"]]
        self.assertIn("DIRECTOR_CLASSIFIED_AS_EMPLOYEE", codes)
        self.assertIn("WORKING_STATUS_USED_AS_EMPLOYMENT_CATEGORY", codes)

    def test_contributor_line_cannot_be_employee(self):
        record = p_da_silva()
        record["people"][0]["link"] = "Outro"
        record["people"][0]["category"] = "EMPREGADO"
        report = module.validate(record)
        self.assertIn("CONTRIBUTOR_LINE_CLASSIFIED_AS_EMPLOYEE", [x["code"] for x in report["findings"]])

    def test_federal_must_use_authoritative_final_balance(self):
        record = p_da_silva()
        record["federal_balance"]["source"] = "GRADE_INTERMEDIARIA_CONTRIBUINTES"
        record["federal_balance"]["value"] = "0.00"
        report = module.validate(record)
        self.assertIn("FEDERAL_NONAUTHORITATIVE_SOURCE", [x["code"] for x in report["findings"]])

    def test_federal_field_requires_full_provenance(self):
        record = p_da_silva()
        record["federal_balance"]["page"] = None
        report = module.validate(record)
        finding = next(x for x in report["findings"] if x["code"] == "FIELD_PROVENANCE_INCOMPLETE")
        self.assertEqual(finding["field"], "federal_balance")

    def test_competence_requires_method_and_evidence(self):
        record = p_da_silva()
        record["competence_method"] = ""
        record["competence_evidence"] = ""
        report = module.validate(record)
        self.assertIn("COMPETENCE_PROVENANCE_MISSING", [x["code"] for x in report["findings"]])

    def test_fgts_aggregate_must_match_employee_detail(self):
        record = pecas_2a()
        record["fgts_monthly"]["value"] = "400.00"
        report = module.validate(record)
        self.assertIn("FGTS_INDIVIDUAL_AGGREGATE_MISMATCH", [x["code"] for x in report["findings"]])

    def test_fgts_must_use_authoritative_section(self):
        record = pecas_2a()
        record["fgts_monthly"]["source"] = "OUTRA_SECAO"
        report = module.validate(record)
        self.assertIn("FGTS_NONAUTHORITATIVE_SOURCE", [x["code"] for x in report["findings"]])

    def test_aggregate_people_counts_are_cross_checked(self):
        record = pecas_2a()
        record["aggregates"]["employees"] = 3
        report = module.validate(record)
        self.assertIn("EMPLOYEE_COUNT_MISMATCH", [x["code"] for x in report["findings"]])

    def test_missing_federal_authoritative_field_blocks(self):
        record = p_da_silva()
        record["federal_balance"] = {}
        report = module.validate(record)
        self.assertIn("FEDERAL_AUTHORITATIVE_FIELD_MISSING", [x["code"] for x in report["findings"]])

    def test_report_hash_is_stable(self):
        first = module.validate(p_da_silva())
        second = module.validate(p_da_silva())
        self.assertEqual(first["report_sha256"], second["report_sha256"])


if __name__ == "__main__":
    unittest.main()
