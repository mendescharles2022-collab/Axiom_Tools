from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_document_identity_binding.py"
spec = importlib.util.spec_from_file_location("validate_document_identity_binding", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def doc(**overrides):
    value = {
        "document_id": "d1",
        "discovered": True,
        "indexed": True,
        "conference_eligible": True,
        "client_id": "c1",
        "binding_method": "IDENTIDADE_EXTRAIDA",
        "binding_evidence": "CPF do documento confere com cadastro",
        "binding_confidence": 0.99,
        "extracted_identity": {"cpf": "123.456.789-01"},
        "client_identity": {"cpf": "12345678901"},
        "requires_unit_identity": False,
        "client_unit_identities": [],
    }
    value.update(overrides)
    return value


class DocumentIdentityBindingTests(unittest.TestCase):
    def test_valid_bound_document_passes(self):
        report = module.validate([doc()])
        self.assertTrue(report["all_ok"], report)

    def test_conference_document_must_be_discovered(self):
        report = module.validate([doc(discovered=False)])
        self.assertIn("CONFERENCE_DOCUMENT_NOT_DISCOVERED", [x["code"] for x in report["findings"]])

    def test_conference_document_must_be_indexed(self):
        report = module.validate([doc(indexed=False)])
        self.assertIn("CONFERENCE_DOCUMENT_NOT_INDEXED", [x["code"] for x in report["findings"]])

    def test_binding_requires_client_and_provenance(self):
        report = module.validate([doc(client_id="", binding_method="", binding_evidence="")])
        codes = [x["code"] for x in report["findings"]]
        self.assertIn("CONFERENCE_DOCUMENT_WITHOUT_CLIENT_BINDING", codes)
        self.assertIn("BINDING_PROVENANCE_MISSING", codes)

    def test_binding_confidence_policy_is_enforced(self):
        report = module.validate([doc(binding_confidence=0.70)], {"min_binding_confidence": 0.80})
        self.assertIn("BINDING_CONFIDENCE_BELOW_POLICY", [x["code"] for x in report["findings"]])

    def test_cpf_mismatch_blocks(self):
        report = module.validate([doc(extracted_identity={"cpf": "11111111111"})])
        self.assertIn("CPF_BINDING_MISMATCH", [x["code"] for x in report["findings"]])

    def test_cnpj_mismatch_blocks(self):
        record = doc(
            extracted_identity={"cnpj": "11111111000111"},
            client_identity={"cnpj": "22222222000122"},
        )
        report = module.validate([record])
        self.assertIn("CNPJ_BINDING_MISMATCH", [x["code"] for x in report["findings"]])

    def test_rural_pf_requires_caepf_beyond_cpf(self):
        record = doc(
            requires_unit_identity=True,
            unit_identity_kind="CAEPF",
            extracted_unit_identity="",
            client_unit_identities=["12345678901234"],
        )
        report = module.validate([record])
        codes = [x["code"] for x in report["findings"]]
        self.assertIn("EXTRACTED_UNIT_IDENTITY_MISSING", codes)
        self.assertIn("CPF_MATCH_WITHOUT_REQUIRED_CAEPF", codes)

    def test_rural_pf_caepf_match_passes(self):
        record = doc(
            requires_unit_identity=True,
            unit_identity_kind="CAEPF",
            extracted_unit_identity="123.456.789/0123-4",
            client_unit_identities=["12345678901234"],
            extracted_identity={"cpf": "12345678901", "caepf": "12345678901234"},
            client_identity={"cpf": "12345678901", "caepf": ["12345678901234"]},
        )
        report = module.validate([record])
        self.assertTrue(report["all_ok"], report)

    def test_unit_identity_mismatch_blocks(self):
        record = doc(
            requires_unit_identity=True,
            unit_identity_kind="MATRICULA",
            extracted_unit_identity="1001",
            client_unit_identities=["2002"],
        )
        report = module.validate([record])
        self.assertIn("UNIT_IDENTITY_BINDING_MISMATCH", [x["code"] for x in report["findings"]])

    def test_caepf_extracted_against_client_list_is_checked(self):
        record = doc(
            extracted_identity={"cpf": "12345678901", "caepf": "99999999999999"},
            client_identity={"cpf": "12345678901", "caepf": ["12345678901234", "55555555555555"]},
        )
        report = module.validate([record])
        self.assertIn("CAEPF_BINDING_MISMATCH", [x["code"] for x in report["findings"]])

    def test_duplicate_document_id_blocks(self):
        report = module.validate([doc(), doc()])
        self.assertIn("DUPLICATE_DOCUMENT_ID", [x["code"] for x in report["findings"]])

    def test_report_hash_is_stable(self):
        first = module.validate([doc()])
        second = module.validate([doc()])
        self.assertEqual(first["report_sha256"], second["report_sha256"])


if __name__ == "__main__":
    unittest.main()
