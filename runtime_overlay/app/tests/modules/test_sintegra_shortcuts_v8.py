from __future__ import annotations

import unittest
from pathlib import Path

from jinja2 import Environment

ROOT = Path(__file__).resolve().parents[2]
VIEW = ROOT / "src/axiom_tools/web/views/clients_views.py"
TPL = ROOT / "src/axiom_tools/web/templates/clients/detail.html"
CSS = ROOT / "src/axiom_tools/web/static/css/clients-ui-refinement.css"


class SintegraShortcutsV8Tests(unittest.TestCase):
    def test_backend_exposes_official_shortcuts(self):
        text = VIEW.read_text(encoding="utf-8")
        self.assertIn('sintegra_nacional="https://www.sintegra.gov.br/"', text)
        self.assertIn('sintegra_go="https://appasp.sefaz.go.gov.br/Sintegra/Consulta/default.asp"', text)

    def test_template_restores_goias_and_national_shortcuts(self):
        text = TPL.read_text(encoding="utf-8")
        self.assertIn("Consultar SEFAZ GO (Sintegra Goiás)", text)
        self.assertIn("Sintegra Nacional", text)
        self.assertIn('href="{{ sintegra_go }}"', text)
        self.assertIn('href="{{ sintegra_nacional }}"', text)

    def test_external_links_are_isolated_tabs(self):
        text = TPL.read_text(encoding="utf-8")
        block = text.split('class="ax-external-registry-shortcuts', 1)[1].split('</section>', 1)[0]
        self.assertGreaterEqual(block.count('target="_blank"'), 2)
        self.assertGreaterEqual(block.count('rel="noopener noreferrer"'), 2)

    def test_shortcut_block_never_posts_or_auto_overwrites(self):
        text = TPL.read_text(encoding="utf-8")
        block = text.split('<section class="ax-external-registry-shortcuts', 1)[1].split('</section>', 1)[0]
        self.assertNotIn("<form", block)
        self.assertIn("Nenhum dado externo altera o cadastro automaticamente", block)
        self.assertIn("Situação cadastral oficial e situação interna do cliente permanecem informações distintas", block)
        self.assertIn('href="#inscricoes"', block)

    def test_shortcut_shows_client_document_and_go_ie_context(self):
        text = TPL.read_text(encoding="utf-8")
        block = text.split('<section class="ax-external-registry-shortcuts', 1)[1].split('</section>', 1)[0]
        self.assertIn("format_cpf(cliente.documento)", block)
        self.assertIn("format_cnpj(cliente.documento)", block)
        self.assertIn("inscricao.tipo.value == 'IE'", block)
        self.assertIn("inscricao.uf == 'GO'", block)

    def test_template_and_css_are_structurally_valid(self):
        text = TPL.read_text(encoding="utf-8")
        Environment().parse(text)
        css = CSS.read_text(encoding="utf-8")
        self.assertIn(".ax-external-registry-shortcuts", css)
        self.assertIn(".ax-external-registry-shortcuts__actions", css)
        self.assertIn(".ax-external-registry-shortcuts__note", css)


if __name__ == "__main__":
    unittest.main()
