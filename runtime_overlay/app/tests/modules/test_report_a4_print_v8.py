from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "axiom_tools"


class ReportA4PrintV8Tests(unittest.TestCase):
    def test_report_template_uses_single_table_with_repeatable_header(self):
        text = (SRC / "web/templates/reports/view.html").read_text(encoding="utf-8")
        self.assertIn('class="ax-report-table"', text)
        self.assertIn("<thead>", text)
        self.assertIn("<tbody>", text)

    def test_print_css_is_a4_portrait_with_controlled_margins(self):
        css = (SRC / "web/static/css/processing-hub.css").read_text(encoding="utf-8")
        self.assertIn("@page{size:A4 portrait;margin:8mm 7mm}", css)

    def test_print_table_never_requires_horizontal_overflow(self):
        css = (SRC / "web/static/css/processing-hub.css").read_text(encoding="utf-8")
        self.assertIn(".ax-report-table{width:100%!important;max-width:100%!important;overflow:visible!important}", css)
        self.assertIn("table-layout:fixed!important", css)
        self.assertIn("overflow-wrap:anywhere!important", css)
        self.assertIn("white-space:normal!important", css)

    def test_header_repeats_and_rows_avoid_page_split(self):
        css = (SRC / "web/static/css/processing-hub.css").read_text(encoding="utf-8")
        self.assertIn(".ax-report-table thead{display:table-header-group}", css)
        self.assertIn(".ax-report-table tr{break-inside:avoid;page-break-inside:avoid}", css)


if __name__ == "__main__":
    unittest.main()
