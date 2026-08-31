from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_source_obligation_decisions.py"
spec = importlib.util.spec_from_file_location("validate_source_obligation_decisions", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def obligation(name: str, state: str = "PENDENTE", component: str = "") -> dict:
    return {
        "competence": "08/2026",
        "client_id": "c1",
        "obligation": name,
        "component": component,
        "state": state,
        "applicable": state != "NAO_APLICAVEL",
    }


def decision(name: str, previous: str, new: str, *, component: str = "", decision_id: str = "d1", revision: int = 3) -> dict:
    return {
        "decision_id": decision_id,
        "competence": "08/2026",
        "client_id": "c1",
        "obligation": name,
        "component": component,
        "previous_state": previous,
        "new_state": new,
        "reason": "motivo documentado",
        "user_id": "u1",
        "timestamp": "2026-08-31T12:00:00-03:00",
        "evidence": ["doc-1"],
        "origin": "CONFERENCIA",
        "correlation_id": "corr-1",
        "monthly_revision": revision,
    }


class SourceObligationDecisionTests(unittest.TestCase):
    def test_justify_darf_does_not_close_pending_fgts(self):
        obligations = [obligation("DARF"), obligation("FGTS")]
        decisions = [decision("DARF", "PENDENTE", "JUSTIFICADA")]
        report = module.evaluate(obligations, decisions, {"08/2026|c1": 3})
        self.assertTrue(report["all_ok"], report)
        self.assertFalse(report["clients"][0]["closable"])
        states = {x["obligation"]: x["state"] for x in report["obligations"]}
        self.assertEqual(states["DARF"], "JUSTIFICADA")
        self.assertEqual(states["FGTS"], "PENDENTE")

    def test_fgts_not_applicable_does_not_change_darf(self):
        obligations = [obligation("DARF"), obligation("FGTS")]
        decisions = [decision("FGTS", "PENDENTE", "NAO_APLICAVEL")]
        report = module.evaluate(obligations, decisions, {"08/2026|c1": 3})
        states = {x["obligation"]: x["state"] for x in report["obligations"]}
        self.assertEqual(states["DARF"], "PENDENTE")
        self.assertEqual(states["FGTS"], "NAO_APLICAVEL")
        self.assertFalse(report["clients"][0]["closable"])

    def test_external_impediment_can_be_terminal_by_policy(self):
        report = module.evaluate(
            [obligation("DARF")],
            [decision("DARF", "PENDENTE", "IMPEDIDA_EXTERNAMENTE")],
            {"08/2026|c1": 3},
            {"allow_external_impediment_as_terminal": True},
        )
        self.assertTrue(report["clients"][0]["closable"])

    def test_external_impediment_can_be_nonterminal_by_policy(self):
        report = module.evaluate(
            [obligation("DARF")],
            [decision("DARF", "PENDENTE", "IMPEDIDA_EXTERNAMENTE")],
            {"08/2026|c1": 3},
            {"allow_external_impediment_as_terminal": False},
        )
        self.assertFalse(report["clients"][0]["closable"])

    def test_global_decision_is_rejected(self):
        global_decision = decision("*", "PENDENTE", "JUSTIFICADA")
        report = module.evaluate([obligation("DARF")], [global_decision])
        self.assertIn("GLOBAL_OR_UNSCOPED_DECISION", [x["code"] for x in report["findings"]])

    def test_stale_monthly_revision_is_blocked(self):
        report = module.evaluate(
            [obligation("DARF")],
            [decision("DARF", "PENDENTE", "JUSTIFICADA", revision=2)],
            {"08/2026|c1": 3},
        )
        self.assertIn("STALE_MONTHLY_REVISION", [x["code"] for x in report["findings"]])
        self.assertEqual(report["obligations"][0]["state"], "PENDENTE")

    def test_stale_previous_state_is_blocked(self):
        report = module.evaluate(
            [obligation("DARF", "DIVERGENTE")],
            [decision("DARF", "PENDENTE", "JUSTIFICADA")],
        )
        self.assertIn("STALE_PREVIOUS_STATE", [x["code"] for x in report["findings"]])

    def test_component_scope_keeps_monthly_and_rescisory_separate(self):
        obligations = [obligation("FGTS", component="MENSAL"), obligation("FGTS", component="RESCISORIO")]
        decisions = [decision("FGTS", "PENDENTE", "CONFERIDA", component="MENSAL")]
        report = module.evaluate(obligations, decisions)
        states = {(x["obligation"], x["component"]): x["state"] for x in report["obligations"]}
        self.assertEqual(states[("FGTS", "MENSAL")], "CONFERIDA")
        self.assertEqual(states[("FGTS", "RESCISORIO")], "PENDENTE")
        self.assertFalse(report["clients"][0]["closable"])

    def test_decision_metadata_is_required(self):
        item = decision("DARF", "PENDENTE", "JUSTIFICADA")
        item["reason"] = ""
        item["evidence"] = None
        report = module.evaluate([obligation("DARF")], [item])
        self.assertIn("DECISION_METADATA_MISSING", [x["code"] for x in report["findings"]])

    def test_duplicate_decision_id_is_blocked(self):
        first = decision("DARF", "PENDENTE", "JUSTIFICADA", decision_id="same")
        second = decision("FGTS", "PENDENTE", "JUSTIFICADA", decision_id="same")
        report = module.evaluate([obligation("DARF"), obligation("FGTS")], [first, second])
        self.assertIn("DUPLICATE_DECISION_ID", [x["code"] for x in report["findings"]])


if __name__ == "__main__":
    unittest.main()
