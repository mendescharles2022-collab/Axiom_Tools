from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_operational_ui_contract.py"
spec = importlib.util.spec_from_file_location("audit_operational_ui_contract", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def policy() -> dict:
    return {
        "contracts": [
            {
                "id": "B43_PENDENCIAS_COMPETENCIA_ATIVA",
                "globs": ["**/pendencias*.py", "**/pendencias*.html"],
                "min_files": 1,
                "require_any": [
                    {
                        "rule_id": "contexto_competencia_ativa",
                        "regexes": [r"competencia_ativa", r"competencia_trabalho"],
                    },
                    {
                        "rule_id": "proc_filtro_secundario",
                        "regexes": [r"request\.args\.get\(['\"]proc['\"]", r"proc_filter"],
                    },
                ],
                "forbid": [
                    {"rule_id": "proc_contexto_primario", "regex": r"default_proc|proc_default|contexto_primario\s*=\s*['\"]PROC"},
                ],
            },
            {
                "id": "B44_RELATORIO_A4",
                "globs": ["**/report*.css", "**/relatorio*.css", "**/report*.html", "**/relatorio*.html"],
                "min_files": 1,
                "require": [
                    {"rule_id": "a4_retrato", "regex": r"@page\s*\{[^}]*size\s*:\s*A4\s+portrait", "min": 1},
                    {"rule_id": "cabecalho_repetivel", "regex": r"thead[^{}]*\{[^}]*display\s*:\s*table-header-group", "min": 1},
                ],
                "require_any": [
                    {
                        "rule_id": "evitar_quebra_bloco",
                        "regexes": [r"break-inside\s*:\s*avoid", r"page-break-inside\s*:\s*avoid"],
                    }
                ],
                "forbid": [
                    {"rule_id": "orientacao_paisagem", "regex": r"size\s*:\s*A4\s+landscape"},
                ],
            },
            {
                "id": "B46_MONITOR_FONTE_UNICA",
                "globs": ["**/monitor*.py", "**/monitor*.html"],
                "min_files": 1,
                "require": [
                    {"rule_id": "status_operacional_canonico", "regex": r"status_operacional", "min": 1},
                ],
                "forbid": [
                    {"rule_id": "status_legado_primario", "regex": r"status_sessao_legacy|status_persistido_primario|duplo_status_primario"},
                ],
            },
            {
                "id": "B47_SINTEGRA_ATALHOS",
                "globs": ["**/inscri*.py", "**/inscri*.html", "**/cliente*.py", "**/cliente*.html"],
                "min_files": 2,
                "require_any": [
                    {"rule_id": "backend_sintegra", "regexes": [r"sintegra_go_url", r"sintegra_nacional_url"]},
                    {"rule_id": "atalho_visivel", "regexes": [r"href\s*=\s*['\"][^'\"]*sintegra"]},
                ],
            },
        ]
    }


class OperationalUiContractTests(unittest.TestCase):
    def _write_valid_fixture(self, root: Path) -> None:
        write(root, "views/pendencias.py", "competencia_ativa = get_competencia_ativa()\nproc_filter = request.args.get('proc')\n")
        write(root, "static/report.css", "@page { size: A4 portrait; }\nthead { display: table-header-group; }\ntr { break-inside: avoid; }\n")
        write(root, "views/monitor.py", "status_operacional = calcular_status_operacional()\n")
        write(root, "views/inscricoes.py", "sintegra_go_url = config.get('sintegra_go_url')\n")
        write(root, "templates/inscricoes.html", '<a href="{{ sintegra_go_url }}">Abrir Sintegra</a>\n')

    def test_valid_operational_ui_contract_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_valid_fixture(root)
            report = module.audit(root, policy())
            self.assertTrue(report["all_ok"], report)
            self.assertEqual(len(report["contracts"]), 4)

    def test_b43_requires_active_competence_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_valid_fixture(root)
            write(root, "views/pendencias.py", "proc_filter = request.args.get('proc')\n")
            report = module.audit(root, policy())
            finding = next(x for x in report["findings"] if x.get("contract_id") == "B43_PENDENCIAS_COMPETENCIA_ATIVA")
            self.assertEqual(finding["rule_id"], "contexto_competencia_ativa")

    def test_b43_rejects_proc_as_primary_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_valid_fixture(root)
            write(root, "views/pendencias.py", "competencia_ativa = get_competencia_ativa()\nproc_filter = request.args.get('proc')\ndefault_proc = ultimo_proc()\n")
            report = module.audit(root, policy())
            self.assertTrue(any(x.get("rule_id") == "proc_contexto_primario" for x in report["findings"]))

    def test_b44_requires_a4_portrait(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_valid_fixture(root)
            write(root, "static/report.css", "@page { size: A4; }\nthead { display: table-header-group; }\ntr { break-inside: avoid; }\n")
            report = module.audit(root, policy())
            self.assertTrue(any(x.get("rule_id") == "a4_retrato" for x in report["findings"]))

    def test_b44_rejects_landscape(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_valid_fixture(root)
            write(root, "static/report.css", "@page { size: A4 portrait; }\n@media print { .alt { size: A4 landscape; } }\nthead { display: table-header-group; }\ntr { page-break-inside: avoid; }\n")
            report = module.audit(root, policy())
            self.assertTrue(any(x.get("rule_id") == "orientacao_paisagem" for x in report["findings"]))

    def test_b44_requires_repeating_table_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_valid_fixture(root)
            write(root, "static/report.css", "@page { size: A4 portrait; }\ntr { break-inside: avoid; }\n")
            report = module.audit(root, policy())
            self.assertTrue(any(x.get("rule_id") == "cabecalho_repetivel" for x in report["findings"]))

    def test_b46_requires_canonical_operational_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_valid_fixture(root)
            write(root, "views/monitor.py", "status = calcular_status()\n")
            report = module.audit(root, policy())
            self.assertTrue(any(x.get("rule_id") == "status_operacional_canonico" for x in report["findings"]))

    def test_b46_rejects_legacy_primary_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_valid_fixture(root)
            write(root, "views/monitor.py", "status_operacional = calcular_status_operacional()\nstatus_sessao_legacy = carregar()\n")
            report = module.audit(root, policy())
            self.assertTrue(any(x.get("rule_id") == "status_legado_primario" for x in report["findings"]))

    def test_b47_requires_backend_and_visible_shortcut(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_valid_fixture(root)
            write(root, "templates/inscricoes.html", "<div>Inscrição Estadual</div>\n")
            report = module.audit(root, policy())
            self.assertTrue(any(x.get("rule_id") == "atalho_visivel" for x in report["findings"]))

    def test_missing_target_files_blocks_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = module.audit(root, policy())
            self.assertIn("UI_CONTRACT_FILES_MISSING", [x["code"] for x in report["findings"]])

    def test_duplicate_contract_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = policy()
            p["contracts"].append(dict(p["contracts"][0]))
            with self.assertRaises(module.UiContractError):
                module.audit(root, p)

    def test_invalid_regex_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            p = {"contracts": [{"id": "x", "globs": ["*.txt"], "min_files": 0, "require": [{"regex": "["}]}]}
            with self.assertRaises(module.UiContractError):
                module.audit(root, p)


if __name__ == "__main__":
    unittest.main()
