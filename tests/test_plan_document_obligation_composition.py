from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "plan_document_obligation_composition.py"
spec = importlib.util.spec_from_file_location("plan_document_obligation_composition", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def sha(char: str) -> str:
    return char * 64


def ev(
    evidence_id: str,
    *,
    dimension: str = "FGTS",
    amount: str = "100.00",
    physical: str = "A",
    logical: str | None = None,
    economic: str = "EMPRESA:08-2026",
    component: str = "MENSAL",
    relation: str = "PRIMARY",
    relation_group: str | None = None,
    current: bool = False,
    unit: str | None = None,
) -> dict:
    return {
        "evidence_id": evidence_id,
        "dimension": dimension,
        "amount": amount,
        "physical_sha256": sha(physical),
        "logical_fingerprint": logical or f"LOG-{evidence_id}",
        "economic_key": economic,
        "component_key": component,
        "relation": relation,
        "relation_group": relation_group,
        "preferred_current": current,
        "unit_key": unit,
    }


class DocumentObligationCompositionTests(unittest.TestCase):
    def test_single_component_passes(self):
        report = module.plan_composition([ev("g1", amount="345.57")])
        self.assertTrue(report["all_ok"], report)
        self.assertEqual(report["totals"][0]["total"], "345.57")

    def test_identical_physical_file_is_not_counted_twice(self):
        a = ev("a", physical="B", logical="MESMO", amount="100.00")
        b = ev("b", physical="B", logical="MESMO", amount="100.00")
        report = module.plan_composition([a, b])
        self.assertTrue(report["all_ok"], report)
        self.assertEqual(report["totals"][0]["total"], "100.00")
        self.assertEqual(report["decisions"]["b"]["action"], "EXCLUDE_IDENTICAL_PHYSICAL")

    def test_same_physical_hash_with_conflicting_identity_blocks(self):
        a = ev("a", physical="C", component="MENSAL")
        b = ev("b", physical="C", component="RESCISORIO")
        report = module.plan_composition([a, b])
        self.assertIn("PHYSICAL_HASH_IDENTITY_CONFLICT", [x["code"] for x in report["findings"]])
        self.assertFalse(report["all_ok"])

    def test_hashes_different_reissue_equivalent_counts_once(self):
        a = ev(
            "old",
            physical="D",
            logical="GUIA-1",
            relation="REEMISSAO_EQUIVALENTE",
            relation_group="G1",
        )
        b = ev(
            "new",
            physical="E",
            logical="GUIA-1-REEMITIDA",
            relation="REEMISSAO_EQUIVALENTE",
            relation_group="G1",
            current=True,
        )
        report = module.plan_composition([a, b])
        self.assertTrue(report["all_ok"], report)
        self.assertEqual(report["totals"][0]["total"], "100.00")
        self.assertEqual(report["decisions"]["old"]["action"], "EXCLUDE_SUPERSEDED_OR_EQUIVALENT")

    def test_equivalent_reissue_with_different_amount_blocks(self):
        a = ev("old", physical="F", amount="100.00", relation="REEMISSAO_EQUIVALENTE", relation_group="G2")
        b = ev("new", physical="1", amount="110.00", relation="REEMISSAO_EQUIVALENTE", relation_group="G2", current=True)
        report = module.plan_composition([a, b])
        self.assertIn("EQUIVALENT_REISSUE_AMOUNT_DIVERGENCE", [x["code"] for x in report["findings"]])

    def test_version_group_requires_exactly_one_current(self):
        a = ev("old", physical="2", relation="VERSAO_SUCESSORA", relation_group="G3")
        b = ev("new", physical="3", relation="VERSAO_SUCESSORA", relation_group="G3")
        report = module.plan_composition([a, b])
        self.assertIn("VERSION_GROUP_REQUIRES_ONE_CURRENT", [x["code"] for x in report["findings"]])
        self.assertEqual(report["totals"][0]["status"], "REVIEW_REQUIRED")

    def test_two_primary_records_same_component_do_not_sum_blindly(self):
        a = ev("a", physical="4", amount="129.68", component="MESMA-PARCELA")
        b = ev("b", physical="5", amount="259.36", component="MESMA-PARCELA")
        report = module.plan_composition([a, b])
        self.assertIn("DUPLICATE_ECONOMIC_COMPONENT_WITHOUT_RELATION", [x["code"] for x in report["findings"]])
        self.assertIsNone(report["totals"][0]["total"])

    def test_indeterminate_relation_never_sums_automatically(self):
        record = ev("amb", physical="6", relation="RELACAO_INDETERMINADA")
        report = module.plan_composition([record])
        self.assertIn("INDETERMINATE_RELATION_BLOCKS_COMPOSITION", [x["code"] for x in report["findings"]])
        self.assertEqual(report["decisions"]["amb"]["action"], "REVIEW_REQUIRED")

    def test_jair_federal_once_and_fgts_by_matricula_adds(self):
        records = [
            ev(
                "fed-m1",
                dimension="FEDERAL",
                amount="511.43",
                physical="7",
                economic="JAIR:08-2026:FEDERAL",
                component="FEDERAL-CONSOLIDADO",
                relation="REEMISSAO_EQUIVALENTE",
                relation_group="FED-JAIR",
            ),
            ev(
                "fed-m2",
                dimension="FEDERAL",
                amount="511.43",
                physical="8",
                economic="JAIR:08-2026:FEDERAL",
                component="FEDERAL-CONSOLIDADO",
                relation="REEMISSAO_EQUIVALENTE",
                relation_group="FED-JAIR",
                current=True,
            ),
            ev(
                "fgts-m1",
                dimension="FGTS",
                amount="129.68",
                physical="9",
                economic="JAIR:08-2026:FGTS",
                component="MATRICULA-1",
                relation="UNIDADE_DISTINTA",
                unit="M1",
            ),
            ev(
                "fgts-m2",
                dimension="FGTS",
                amount="259.36",
                physical="A",
                economic="JAIR:08-2026:FGTS",
                component="MATRICULA-2",
                relation="UNIDADE_DISTINTA",
                unit="M2",
            ),
        ]
        report = module.plan_composition(records)
        self.assertTrue(report["all_ok"], report)
        totals = {(x["dimension"], x["economic_key"]): x["total"] for x in report["totals"]}
        self.assertEqual(totals[("FEDERAL", "JAIR:08-2026:FEDERAL")], "511.43")
        self.assertEqual(totals[("FGTS", "JAIR:08-2026:FGTS")], "389.04")

    def test_monthly_and_rescisory_are_distinct_additive_components(self):
        records = [
            ev("mensal", physical="B", amount="80.00", economic="EMP:FGTS", component="MENSAL", relation="PRIMARY"),
            ev("resc", physical="C", amount="120.00", economic="EMP:FGTS", component="RESCISORIO", relation="COMPONENTE_ADITIVO"),
        ]
        report = module.plan_composition(records)
        self.assertTrue(report["all_ok"], report)
        self.assertEqual(report["totals"][0]["total"], "200.00")

    def test_leosmar_equivalent_documents_do_not_double(self):
        records = [
            ev("leo1", physical="D", amount="220.00", economic="LEOSMAR:FED", component="FED", relation="REEMISSAO_EQUIVALENTE", relation_group="LEO"),
            ev("leo2", physical="E", amount="220.00", economic="LEOSMAR:FED", component="FED", relation="REEMISSAO_EQUIVALENTE", relation_group="LEO", current=True),
        ]
        report = module.plan_composition(records)
        self.assertTrue(report["all_ok"], report)
        self.assertEqual(report["totals"][0]["total"], "220.00")

    def test_plan_hash_is_stable_for_same_input(self):
        records = [ev("x", physical="F")]
        first = module.plan_composition(records)
        second = module.plan_composition(records)
        self.assertEqual(first["plan_sha256"], second["plan_sha256"])

    def test_invalid_sha_is_rejected(self):
        record = ev("x")
        record["physical_sha256"] = "not-a-sha"
        with self.assertRaises(module.CompositionError):
            module.plan_composition([record])


if __name__ == "__main__":
    unittest.main()
