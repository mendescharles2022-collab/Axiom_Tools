from __future__ import annotations

import unittest
from pathlib import Path

from axiom_tools.modules.closing import service as closing

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE = ROOT / 'src' / 'axiom_tools' / 'web' / 'templates' / 'conference' / 'index.html'


class ClosingStatesV8Tests(unittest.TestCase):
    def test_pronta_is_waiting_processing_not_conference(self):
        self.assertEqual(closing.STATUS['PRONTA'], 'Aguardando processamento')

    def test_retification_has_own_label(self):
        self.assertEqual(closing.STATUS['RETIFICACAO'], 'Retificação detectada')

    def test_conference_template_exposes_retification_scope(self):
        text = TEMPLATE.read_text(encoding='utf-8')
        self.assertIn('value="RETIFICACOES"', text)
        self.assertIn('Retificações', text)
        self.assertIn('retificações em fluxo próprio', text)


if __name__ == '__main__':
    unittest.main()
