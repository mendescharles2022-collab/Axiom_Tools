from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config" / "operational_ui_contract_v8.json"
SCRIPT = ROOT / "scripts" / "audit_operational_ui_contract.py"
spec = importlib.util.spec_from_file_location("audit_operational_ui_contract_policy", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def canonical_policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def write_valid_fixture(root: Path) -> None:
    write(root, "views/pendencias.py", "competencia_ativa = get_competencia_ativa()\nproc_filter = request.args.get('proc')\n")
    write(root, "static/report.css", "@page { size: A4 portrait; }\nthead { display: table-header-group; }\ntr { break-inside: avoid; }\n")
    write(root, "views/monitor.py", "status_operacional = calcular_status_operacional()\n")
    write(root, "views/inscricoes.py", "sintegra_go_url = config.get('sintegra_go_url')\n")
    write(root, "templates/inscricoes.html", '<a href="{{ sintegra_go_url }}">Abrir Sintegra</a>\n')


class CanonicalOperationalUiPolicyTests(unittest.TestCase):
    def test_policy_has_exact_four_expected_contracts(self):
        policy = canonical_policy()
        ids = [item["id"] for item in policy["contracts"]]
        self.assertEqual(
            ids,
            [
                "B43_PENDENCIAS_COMPETENCIA_ATIVA",
                "B44_RELATORIO_A4",
                "B46_MONITOR_FONTE_UNICA",
                "B47_SINTEGRA_ATALHOS",
            ],
        )

    def test_canonical_policy_passes_valid_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_valid_fixture(root)
            report = module.audit(root, canonical_policy())
            self.assertTrue(report["all_ok"], report)

    def test_b47_backend_without_visible_link_is_blocked_by_canonical_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_valid_fixture(root)
            write(root, "templates/inscricoes.html", "<div>Inscrição Estadual</div>\n")
            report = module.audit(root, canonical_policy())
            self.assertTrue(
                any(
                    finding.get("contract_id") == "B47_SINTEGRA_ATALHOS"
                    and finding.get("rule_id") == "atalho_visivel"
                    for finding in report["findings"]
                ),
                report,
            )

    def test_b47_visible_link_without_backend_marker_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_valid_fixture(root)
            write(root, "views/inscricoes.py", "def inscricoes():\n    return []\n")
            report = module.audit(root, canonical_policy())
            self.assertTrue(
                any(
                    finding.get("contract_id") == "B47_SINTEGRA_ATALHOS"
                    and finding.get("rule_id") == "backend_sintegra"
                    for finding in report["findings"]
                ),
                report,
            )


if __name__ == "__main__":
    unittest.main()
