from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_econsignado_cycle_contract.py"
spec = importlib.util.spec_from_file_location("validate_econsignado_cycle_contract", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def payload(**overrides):
    value = {
        "competence": "08/2026",
        "call": 1,
        "orchestrator_command_id": "cycle-1",
        "stages": ["ECONSIGNADO", "DOMINIO", "ESOCIAL", "ECAC_DARF", "FGTS_DIGITAL", "CONFERENCIA"],
        "eligible_client_ids": ["c1"],
        "queried_client_ids": ["c1"],
        "future_call_client_ids": [],
        "sem_movimento_non_applicable_client_ids": [],
        "snapshots": [
            {"snapshot_id": "s1", "client_id": "c1", "result": "SEM_CONSIGNADO"},
        ],
        "obligations": [],
    }
    value.update(overrides)
    return value


def obligation(**overrides):
    value = {
        "client_id": "c1",
        "mte_result": "COM_CONSIGNADO",
        "business_state": "CONFERIDA",
        "required_sources": {"dominio": True, "fgts": True},
        "sources_compatible": True,
        "derived_from_context": True,
        "active_employment": True,
        "remuneration": "2000.00",
        "fgts_amount": "160.00",
        "termination": False,
    }
    value.update(overrides)
    return value


class EConsignadoCycleContractTests(unittest.TestCase):
    def test_valid_stage_zero_cycle_passes(self):
        report = module.validate(payload(obligations=[obligation()]))
        self.assertTrue(report["all_ok"], report)

    def test_econsignado_must_be_first_processing_stage(self):
        stages = ["DOMINIO", "ECONSIGNADO", "ESOCIAL", "ECAC_DARF", "FGTS_DIGITAL", "CONFERENCIA"]
        report = module.validate(payload(stages=stages))
        self.assertIn("ORCHESTRATOR_STAGE_ORDER_INVALID", [x["code"] for x in report["findings"]])

    def test_cycle_must_bind_to_orchestrator_command(self):
        report = module.validate(payload(orchestrator_command_id=""))
        self.assertIn("ECONSIGNADO_NOT_BOUND_TO_ORCHESTRATOR_COMMAND", [x["code"] for x in report["findings"]])

    def test_query_universe_cannot_include_future_call(self):
        report = module.validate(payload(
            eligible_client_ids=["c1"],
            queried_client_ids=["c1", "c2"],
            future_call_client_ids=["c2"],
        ))
        codes = [x["code"] for x in report["findings"]]
        self.assertIn("QUERY_UNIVERSE_EXTRA_CLIENTS", codes)
        self.assertIn("FUTURE_CALL_CLIENT_QUERIED", codes)

    def test_query_universe_cannot_include_nonapplicable_sem_movimento(self):
        report = module.validate(payload(
            eligible_client_ids=["c1"],
            queried_client_ids=["c1", "c2"],
            sem_movimento_non_applicable_client_ids=["c2"],
        ))
        self.assertIn("SEM_MOVIMENTO_CLIENT_QUERIED", [x["code"] for x in report["findings"]])

    def test_missing_eligible_client_is_reported(self):
        report = module.validate(payload(eligible_client_ids=["c1", "c2"], queried_client_ids=["c1"]))
        self.assertIn("QUERY_UNIVERSE_MISSING_CLIENTS", [x["code"] for x in report["findings"]])

    def test_sem_consignado_is_valid_not_technical_error(self):
        report = module.validate(payload(snapshots=[{
            "snapshot_id": "s1", "client_id": "c1", "result": "SEM_CONSIGNADO", "classified_as_technical_error": False
        }]))
        self.assertTrue(report["all_ok"], report)

    def test_sem_procuracao_misclassified_as_technical_error_blocks(self):
        report = module.validate(payload(snapshots=[{
            "snapshot_id": "s1", "client_id": "c1", "result": "SEM_PROCURACAO", "classified_as_technical_error": True
        }]))
        self.assertIn("SEM_PROCURACAO_MISCLASSIFIED_AS_TECHNICAL_ERROR", [x["code"] for x in report["findings"]])

    def test_technical_error_after_valid_snapshot_must_preserve_previous(self):
        snapshots = [
            {"snapshot_id": "s1", "client_id": "c1", "result": "COM_CONSIGNADO"},
            {"snapshot_id": "s2", "client_id": "c1", "result": "ERRO_TECNICO", "prior_valid_preserved": False},
        ]
        report = module.validate(payload(snapshots=snapshots))
        self.assertIn("TECHNICAL_ERROR_DID_NOT_PRESERVE_PRIOR_VALID_SNAPSHOT", [x["code"] for x in report["findings"]])

    def test_daf_castro_cannot_be_conferred_with_missing_source(self):
        item = obligation(required_sources={"dominio": True, "comunicado": False, "fgts": False})
        report = module.validate(payload(obligations=[item]))
        self.assertIn("FALSE_CONFERRED_MISSING_SOURCE", [x["code"] for x in report["findings"]])

    def test_incompatible_sources_cannot_be_conferred(self):
        item = obligation(sources_compatible=False)
        report = module.validate(payload(obligations=[item]))
        self.assertIn("FALSE_CONFERRED_INCOMPATIBLE_SOURCES", [x["code"] for x in report["findings"]])

    def test_query_result_alone_cannot_be_business_conclusion(self):
        item = obligation(derived_from_context=False)
        report = module.validate(payload(obligations=[item]))
        self.assertIn("BUSINESS_STATE_DERIVED_FROM_QUERY_RESULT_ALONE", [x["code"] for x in report["findings"]])

    def test_dl_residual_return_can_be_observation_without_blocking_by_itself(self):
        item = obligation(
            business_state="PENDENTE",
            active_employment=False,
            remuneration="0.00",
            fgts_amount="0.00",
            residual_disposition="OBSERVACAO_A_CONFIRMAR",
            derived_from_context=True,
        )
        report = module.validate(payload(obligations=[item]))
        self.assertNotIn("RESIDUAL_RETURN_BLOCKS_WITHOUT_CONTEXT", [x["code"] for x in report["findings"]])

    def test_residual_return_without_nonblocking_disposition_blocks(self):
        item = obligation(
            business_state="DIVERGENTE",
            active_employment=False,
            remuneration="0.00",
            fgts_amount="0.00",
            residual_disposition="",
        )
        report = module.validate(payload(obligations=[item]))
        self.assertIn("RESIDUAL_RETURN_BLOCKS_WITHOUT_CONTEXT", [x["code"] for x in report["findings"]])

    def test_termination_requires_monthly_and_guarantee_components_separated(self):
        item = obligation(termination=True, termination_components_separated=False)
        report = module.validate(payload(obligations=[item]))
        self.assertIn("TERMINATION_COMPONENTS_NOT_SEPARATED", [x["code"] for x in report["findings"]])

    def test_report_hash_is_stable(self):
        first = module.validate(payload())
        second = module.validate(payload())
        self.assertEqual(first["report_sha256"], second["report_sha256"])


if __name__ == "__main__":
    unittest.main()
