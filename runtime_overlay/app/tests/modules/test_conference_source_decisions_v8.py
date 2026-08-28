from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path

from axiom_tools.modules.processing.conference import _agregar_decisoes_fontes
from axiom_tools.modules.processing.operations import (
    decisoes_conferencia_fontes,
    salvar_conferencia_fonte,
    salvar_conferencia_manual,
)

ROOT = Path(__file__).resolve().parents[2]


def make_con() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute("CREATE TABLE clientes(id INTEGER PRIMARY KEY,nome TEXT,documento TEXT,nome_apresentacao TEXT)")
    con.execute("INSERT INTO clientes(id,nome,documento) VALUES(1,'Cliente','12345678901')")
    return con


class ConferenceSourceDecisionV8Tests(unittest.TestCase):
    def test_decision_is_persisted_only_for_selected_source(self):
        con = make_con()
        salvar_conferencia_fonte(con, "08/2026", 1, "DARF", "JUSTIFICADO", "Procuração revogada")
        decisoes = decisoes_conferencia_fontes(con, "08/2026", 1)
        self.assertEqual(set(decisoes), {"DARF"})
        self.assertEqual(decisoes["DARF"]["status_manual"], "JUSTIFICADO")
        con.close()

    def test_legacy_global_decision_is_not_propagated_to_sources(self):
        con = make_con()
        salvar_conferencia_manual(con, "08/2026", 1, "CONFERIDO", "Legado")
        self.assertEqual(decisoes_conferencia_fontes(con, "08/2026", 1), {})
        con.close()

    def test_invalid_source_is_rejected(self):
        con = make_con()
        with self.assertRaises(ValueError):
            salvar_conferencia_fonte(con, "08/2026", 1, "GLOBAL", "CONFERIDO", "")
        con.close()

    def test_darf_justified_does_not_hide_fgts_divergence(self):
        checks = {
            "inss": {"status": "DIVERGENTE"},
            "fgts": {"status": "DIVERGENTE"},
            "econsignado": {"status": "NAO_APLICAVEL"},
        }
        agregado, detalhe = _agregar_decisoes_fontes(
            checks,
            {"DARF": {"status_manual": "JUSTIFICADO", "observacao": "Justificado"}},
            exibir_fgts=True,
            exibir_econsignado=False,
        )
        self.assertEqual(agregado, "DIVERGENTE")
        self.assertEqual(detalhe["DARF"]["final"], "JUSTIFICADO")
        self.assertEqual(detalhe["FGTS"]["final"], "DIVERGENTE")

    def test_all_applicable_sources_resolved_can_close_as_justified(self):
        checks = {
            "inss": {"status": "DIVERGENTE"},
            "fgts": {"status": "CONFERIDO"},
            "econsignado": {"status": "NAO_APLICAVEL"},
        }
        agregado, _ = _agregar_decisoes_fontes(
            checks,
            {"DARF": {"status_manual": "JUSTIFICADO"}},
            exibir_fgts=True,
            exibir_econsignado=False,
        )
        self.assertEqual(agregado, "JUSTIFICADO")

    def test_pending_econsignado_keeps_aggregate_incomplete(self):
        checks = {
            "inss": {"status": "CONFERIDO"},
            "fgts": {"status": "CONFERIDO"},
            "econsignado": {"status": "CONFERIDO"},
        }
        agregado, detalhe = _agregar_decisoes_fontes(
            checks,
            {"ECONSIGNADO": {"status_manual": "PENDENTE"}},
            exibir_fgts=True,
            exibir_econsignado=True,
        )
        self.assertEqual(agregado, "INCOMPLETO")
        self.assertEqual(detalhe["ECONSIGNADO"]["final"], "PENDENTE")

    def test_web_routes_use_source_specific_writer(self):
        for rel in (
            "src/axiom_tools/web/views/conference_views.py",
            "src/axiom_tools/web/views/documents_views.py",
        ):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("salvar_conferencia_fonte", text)
            self.assertNotIn("salvar_conferencia_manual(", text)
            self.assertIn('request.form.get("fonte"', text)

    def test_templates_post_explicit_source_and_no_global_status_binding(self):
        for rel in (
            "src/axiom_tools/web/templates/conference/index.html",
            "src/axiom_tools/web/templates/documents/processing_guias.html",
        ):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn('name="fonte"', text)
            self.assertIn("Decisão manual por obrigação", text)
            self.assertNotIn("x.status_manual=='CONFERIDO'", text)


if __name__ == "__main__":
    unittest.main()
