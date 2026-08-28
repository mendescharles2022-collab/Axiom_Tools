from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TPL = ROOT / "src/axiom_tools/web/templates/documents/processing_report_view.html"
CSS = ROOT / "src/axiom_tools/web/static/css/processing-hub.css"
OPS = ROOT / "src/axiom_tools/modules/processing/operations.py"


class ReportA4V8Tests(unittest.TestCase):
    def test_report_view_has_type_specific_print_profile(self):
        text = TPL.read_text(encoding="utf-8")
        self.assertIn("ax-report-view--{{ tipo }}", text)
        self.assertIn("ax-report-table--{{ tipo }}", text)
        self.assertIn("ax-report-sheet", text)

    def test_print_contract_is_a4_portrait_and_repeats_header(self):
        text = CSS.read_text(encoding="utf-8")
        self.assertRegex(text, r"@page\s*\{\s*size:A4 portrait;\s*margin:8mm 7mm\s*\}")
        self.assertIn("display:table-header-group!important", text)
        self.assertIn("display:table-row-group!important", text)
        self.assertIn("page-break-inside:avoid!important", text)

    def test_print_contract_wraps_without_horizontal_min_width(self):
        text = CSS.read_text(encoding="utf-8")
        print_block = text[text.index("@media print{"):text.index("/* V5.6.14Q", text.index("@media print{"))]
        self.assertIn("table-layout:fixed!important", print_block)
        self.assertIn("overflow-wrap:anywhere!important", print_block)
        self.assertIn("white-space:normal!important", print_block)
        self.assertIn("box-sizing:border-box!important", print_block)
        self.assertNotRegex(print_block, r"min-width\s*:\s*[1-9][0-9]+px")

    def test_wide_reports_have_condensed_profile(self):
        text = CSS.read_text(encoding="utf-8")
        for tipo in ("darf", "conferencia", "conferidos", "divergencias", "auditoria"):
            self.assertIn(f".ax-report-view--{tipo} .ax-report-table table", text)
        self.assertIn("font-size:5.95pt!important", text)

    def test_pending_and_darf_have_explicit_column_profiles(self):
        text = CSS.read_text(encoding="utf-8")
        for idx in range(1, 7):
            self.assertIn(f".ax-report-table--pendencias th:nth-child({idx})", text)
        for idx in range(1, 12):
            self.assertIn(f".ax-report-table--darf th:nth-child({idx})", text)

    def test_report_shapes_match_print_profiles(self):
        text = OPS.read_text(encoding="utf-8")
        pend = re.search(r'if tipo == "pendencias":.*?"colunas":\[(.*?)\]', text, re.S)
        darf = re.search(r'if tipo == "darf":.*?"colunas":\[(.*?)\]', text, re.S)
        self.assertIsNotNone(pend)
        self.assertIsNotNone(darf)
        self.assertEqual(len(re.findall(r'"[^"]+"', pend.group(1))), 6)
        self.assertEqual(len(re.findall(r'"[^"]+"', darf.group(1))), 11)


if __name__ == "__main__":
    unittest.main()
