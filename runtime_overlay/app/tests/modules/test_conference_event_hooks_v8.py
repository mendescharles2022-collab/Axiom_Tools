from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class ConferenceEventHooksV8Tests(unittest.TestCase):
    def test_manual_decision_uses_explicit_sync_command(self):
        text = (ROOT / 'src' / 'axiom_tools' / 'web' / 'views' / 'conference_views.py').read_text(encoding='utf-8')
        self.assertIn('sincronizar_conferencia_competencia(conexao, competencia)', text)
        self.assertNotIn('conferencia_competencia(conexao, competencia, "", "", "CICLO")', text)

    def test_worker_recalculates_after_persisting_processed_item(self):
        text = (ROOT / 'src' / 'axiom_tools' / 'modules' / 'processing' / 'worker.py').read_text(encoding='utf-8')
        marker = 'sincronizar_conferencia_competencia(con, str(prow["competencia"]))'
        self.assertIn(marker, text)
        self.assertGreater(text.index(marker), text.index('_checkpoint_final(con,item,estado,pid)'))


if __name__ == '__main__':
    unittest.main()
