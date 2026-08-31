from __future__ import annotations

import unittest
from pathlib import Path

from axiom_tools.modules.processing.queue import _status_operacional_sessao

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "axiom_tools"


class PendingExecutionUxV8Tests(unittest.TestCase):
    def test_document_review_does_not_change_technical_session_status(self):
        self.assertEqual(
            _status_operacional_sessao(100, {"revisao": 8, "erros": 0}, "CONCLUIDO"),
            "PROCESSAMENTO_CONCLUIDO",
        )
        self.assertEqual(
            _status_operacional_sessao(50, {"revisao": 8, "erros": 0}, "PROCESSANDO"),
            "PROCESSANDO",
        )

    def test_real_technical_error_remains_visible(self):
        self.assertEqual(
            _status_operacional_sessao(100, {"revisao": 0, "erros": 1}, "COM_ERROS"),
            "PROCESSAMENTO_CONCLUIDO_COM_ERROS",
        )
        self.assertEqual(
            _status_operacional_sessao(50, {"revisao": 0, "erros": 1}, "PROCESSANDO"),
            "COM_ERROS",
        )

    def test_queue_no_longer_persists_com_pendencias_from_document_review(self):
        text = (SRC / "modules/processing/queue.py").read_text(encoding="utf-8")
        self.assertNotIn('status="COM_PENDENCIAS"', text)
        self.assertNotIn('status_operacional"]="COM_PENDENCIAS"', text)

    def test_execution_is_the_single_live_screen_and_pending_links_use_competence(self):
        text = (SRC / "web/templates/documents/processing_queue.html").read_text(encoding="utf-8")
        self.assertIn("<h1>Execução</h1>", text)
        self.assertNotIn("Monitor de Execução", text)
        self.assertIn("Única tela para acompanhar o processamento ao vivo", text)
        self.assertNotIn("processamento_pendencias',chave=detalhe.chave", text)
        self.assertGreaterEqual(text.count("processamento_pendencias',competencia=competencia_execucao"), 2)

    def test_pending_page_is_competence_first_and_proc_is_advanced(self):
        text = (SRC / "web/templates/documents/processing_pendencias.html").read_text(encoding="utf-8")
        self.assertIn("<h1>Pendências técnicas</h1>", text)
        self.assertIn("Competência em foco", text)
        self.assertIn('class="ax-pending-advanced"', text)
        primary = text.index('class="ax-pending-filters ax-pending-filters--primary"')
        advanced = text.index('class="ax-pending-advanced"')
        primary_block = text[primary:advanced]
        self.assertIn('name="competencia"', primary_block)
        self.assertNotIn('<select class="form-select form-select-sm" name="chave"', primary_block)
        self.assertNotIn('<select class="form-select form-select-sm" name="origem"', primary_block)
        advanced_block = text[advanced:]
        self.assertIn('name="chave"', advanced_block)
        self.assertIn('name="origem"', advanced_block)

    def test_pending_route_defaults_to_active_competence(self):
        text = (SRC / "web/views/documents_views.py").read_text(encoding="utf-8")
        start = text.index("def processamento_pendencias():")
        end = text.index('@bp.post("/processamento/pendencias/reprocessar-todas")')
        block = text[start:end]
        self.assertIn('if "competencia" not in request.args:', block)
        self.assertIn('competencia_ativa', block)

    def test_audit_is_historical_not_live_monitor(self):
        text = (SRC / "web/templates/documents/processing_monitor.html").read_text(encoding="utf-8")
        self.assertIn("Auditoria técnica", text)
        self.assertIn("O progresso ao vivo existe somente na aba Execução", text)

    def test_dashboard_does_not_create_second_monitor_label(self):
        text = (SRC / "web/templates/documents/processing.html").read_text(encoding="utf-8")
        self.assertNotIn("Monitor automático ativo", text)
        self.assertIn("Conexões automáticas ativas", text)
        self.assertNotIn("Monitor / Auditoria", text)


if __name__ == "__main__":
    unittest.main()
