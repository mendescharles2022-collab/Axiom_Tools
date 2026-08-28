from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ProcessingPendingMonitorUxV8Tests(unittest.TestCase):
    def test_pending_route_exposes_active_competence_separately(self):
        text = (ROOT / "src/axiom_tools/web/views/documents_views.py").read_text(encoding="utf-8")
        self.assertIn('competencia_ativa=str(cfg.get("competencia_ativa") or "").strip()', text)
        self.assertIn('competencia=competencia,competencia_ativa=competencia_ativa', text)

    def test_pending_primary_axis_is_competence_and_proc_is_advanced(self):
        text = (ROOT / "src/axiom_tools/web/templates/documents/processing_pendencias.html").read_text(encoding="utf-8")
        form = text.split('<form class="ax-pending-filters"', 1)[1].split('</form>', 1)[0]
        self.assertLess(form.index('name="competencia"'), form.index('name="busca"'))
        self.assertIn('class="ax-pending-advanced"', form)
        self.assertIn('Chave PROC', form)
        self.assertIn('Todas as PROC desta competência', form)

    def test_pending_main_row_does_not_lead_with_proc(self):
        text = (ROOT / "src/axiom_tools/web/templates/documents/processing_pendencias.html").read_text(encoding="utf-8")
        main = text.split('<div class="ax-pending-main">', 1)[1].split('</div>', 1)[0]
        self.assertNotIn("item.chave_processamento or 'Sem PROC'", main)
        detail = text.split('<div class="collapse ax-pending-detail"', 1)[1]
        self.assertIn('<span>Chave PROC</span>', detail)

    def test_monitor_declares_single_live_execution_source(self):
        text = (ROOT / "src/axiom_tools/web/templates/documents/processing_monitor.html").read_text(encoding="utf-8")
        self.assertIn('Execução ao vivo tem uma única fonte: a aba Execução', text)
        self.assertIn('Uma verdade por função:', text)
        self.assertIn("processamento_pendencias", text)

    def test_monitor_moves_review_counts_out_of_primary_kpis(self):
        text = (ROOT / "src/axiom_tools/web/templates/documents/processing_monitor.html").read_text(encoding="utf-8")
        summary = text.split('<section class="ax-ops-summary ax-monitor-summary">', 1)[1].split('</section>', 1)[0]
        self.assertIn('Erros técnicos', summary)
        self.assertNotIn('<span>Revisão</span>', summary)
        self.assertNotIn('<span>Incompletos</span>', summary)
        self.assertIn('monitor.metricas.revisao', text)
        self.assertIn('monitor.metricas.incompletos', text)

    def test_monitor_proc_filter_is_advanced_and_competence_is_primary(self):
        text = (ROOT / "src/axiom_tools/web/templates/documents/processing_monitor.html").read_text(encoding="utf-8")
        form = text.split('class="ax-history-filters ax-history-filters--audit"', 1)[1].split('</form>', 1)[0]
        self.assertLess(form.index('name="competencia"'), form.index('name="busca"'))
        self.assertIn('class="ax-monitor-advanced"', form)
        self.assertIn('placeholder="Chave PROC"', form)
        self.assertIn('Atividade documental histórica', text)
        self.assertIn('Detalhes técnicos dos motores e pipeline', text)

    def test_v8_ux_has_layout_rules_for_advanced_filters(self):
        text = (ROOT / "src/axiom_tools/web/static/css/processing-hub.css").read_text(encoding="utf-8")
        self.assertIn(".ax-pending-advanced", text)
        self.assertIn(".ax-monitor-advanced", text)
        self.assertIn(".ax-monitor-tech", text)
        self.assertIn("grid-template-columns:repeat(4", text)


if __name__ == "__main__":
    unittest.main()
