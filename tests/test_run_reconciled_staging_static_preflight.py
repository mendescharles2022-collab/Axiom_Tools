from __future__ import annotations

import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_reconciliation_baseline_acceptance as acceptance_mod  # noqa: E402
import create_reconciliation_review_skeleton as skeleton_mod  # noqa: E402
import materialize_reconciled_staging as materializer  # noqa: E402
import plan_runtime_reconciliation as planner  # noqa: E402
import run_reconciled_staging_static_preflight as preflight  # noqa: E402

PLAN_POLICY = json.loads((ROOT / "config/runtime_reconciliation_plan_policy_v8.json").read_text(encoding="utf-8"))
STATIC_POLICY = json.loads((ROOT / "config/reconciled_staging_static_preflight_v8.json").read_text(encoding="utf-8"))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def app_code(variant: str = "ok") -> str:
    raw_assignment = (
        "    cliente.classificacao_inativacao = 'INATIVA'\n"
        if variant == "b34"
        else "    cliente.classificacao_inativacao = ClassificacaoInativacao.INATIVA\n"
    )
    get_body = (
        "    salvar_estado()\n    return 'ok'\n"
        if variant == "b02"
        else "    return 'ok'\n"
    )
    login_line = "" if variant == "b38" else "@login_required\n"
    guard_line = "" if variant == "b39" else "    filtrar_autorizados(ids)\n"
    gate_line = "" if variant == "b03" else "    autorizar_saida()\n"
    status_target = "Em conferência" if variant == "b11" else "Aguardando processamento"
    reprocess_prefix = (
        "    conn.execute('DELETE FROM processamento_arquivo WHERE id=?', (1,))\n"
        if variant == "b01"
        else ""
    )
    return f'''class Blueprint:
    def route(self, *args, **kwargs):
        return lambda fn: fn

bp = Blueprint()

def login_required(fn):
    return fn

def salvar_estado():
    return None

def filtrar_autorizados(ids):
    return ids

def autorizar_saida():
    return True

def gerar_pdf():
    autorizar_saida()
    return b"pdf"

def criar_candidato():
    return {{"ok": True}}

def promover_candidato(candidato):
    return candidato

def recalcular_conferencia():
    return True

@bp.route('/consulta', methods=['GET'])
def consultar():
{get_body}
@bp.route('/gerar', methods=['POST'])
{login_line}def gerar_saida(ids=None):
{guard_line}{gate_line}    return gerar_pdf()

def reprocessar_arquivo():
{reprocess_prefix}    candidato = criar_candidato()
    promover_candidato(candidato)
    recalcular_conferencia()
    return candidato

STATUS = {{"PRONTA": "{status_target}"}}

class ClassificacaoInativacao:
    INATIVA = object()

def classificar(cliente):
{raw_assignment}    return cliente
'''


def closing_code(variant: str = "ok") -> str:
    select_function = (
        "def carregar_fora():\n    return 'SELECT * FROM fechamento_mensal_cliente'\n"
        if variant == "b07_outside"
        else ""
    )
    update_sql = (
        "    cur = conn.execute('UPDATE fechamento_mensal_cliente SET status=? WHERE competencia=? AND cliente_id=?', params)\n"
        if variant == "b40"
        else "    cur = conn.execute('UPDATE fechamento_mensal_cliente SET status=? WHERE competencia=? AND cliente_id=? AND status=?', params)\n"
    )
    rowcount = "" if variant == "b40" else "    if cur.rowcount != 1:\n        raise RuntimeError('conflito')\n"
    return f'''def closing_scope():
    return []

def carregar_clientes():
    sql = "SELECT * FROM fechamento_mensal_cliente"
    closing_scope()
    return sql

def atualizar(conn, params):
{update_sql}{rowcount}    return cur

{select_function}'''


def build_stage(base: Path, variant: str = "ok") -> tuple[Path, dict]:
    runtime = base / "runtime"
    repo = base / "repo"
    write(runtime / "src/runtime.py", "runtime_only = True\n")
    write(repo / "src/app.py", app_code(variant))
    write(repo / "src/modules/closing/service.py", closing_code(variant))
    if variant == "b07_outside":
        write(repo / "src/outside.py", "def carregar():\n    return 'SELECT * FROM fechamento_mensal_cliente'\n")
    write(repo / "src/inscricoes.py", "sintegra_go_url = 'https://www.sintegra.gov.br/'\n")
    write(
        repo / "templates/pendencias.html",
        "{{ competencia_ativa }} {{ request.args.get('proc') }}\n",
    )
    report_css = "@page { size: A4 landscape; }" if variant == "b44" else "@page { size: A4 portrait; }"
    write(
        repo / "templates/report.html",
        f"<style>{report_css} thead {{ display: table-header-group; }} .bloco {{ break-inside: avoid; }}</style>\n",
    )
    write(repo / "templates/monitor.html", "{{ status_operacional }}\n")
    sintegra_href = "/outro" if variant == "b47" else "/sintegra"
    write(repo / "templates/inscricoes.html", f'<a href="{sintegra_href}">Sintegra</a>\n')

    runtime_file = runtime / "src/runtime.py"
    row = {
        "area": "src_root",
        "relative_path": "runtime.py",
        "status": "RUNTIME_ONLY",
        "runtime_sha256": materializer.sha256_file(runtime_file),
        "repo_sha256": "",
        "runtime_size": runtime_file.stat().st_size,
        "repo_size": 0,
    }
    plan = planner.build_plan({"metadata": {}, "summary": {}, "rows": [row]}, PLAN_POLICY)
    review = skeleton_mod.build_skeleton(plan)
    review["mode"] = "RECONCILIATION_REVIEW_NOT_EXECUTION"
    item = review["items"][0]
    item["decision"] = "ADOPT_RUNTIME"
    item["reviewer"] = "Charles"
    item["reason"] = "Revisão manual concluída com evidência suficiente."
    item["evidence"] = ["evidence:manual-review"]
    acceptance = acceptance_mod.build_acceptance(plan, review)
    staging = base / "staging"
    materializer.materialize_staging(runtime, repo, staging, acceptance)
    return staging, acceptance


def contract(report: dict, contract_id: str) -> dict:
    return next(item for item in report["contracts"] if item["contract_id"] == contract_id)


def snapshot(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): preflight.sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


class ReconciledStagingStaticPreflightTests(unittest.TestCase):
    def test_valid_staging_passes_all_13_static_contracts_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp))
            before = snapshot(staging)
            report = preflight.run_preflight(staging, acceptance, ROOT, deepcopy(STATIC_POLICY))
            self.assertEqual(report["summary"]["contracts"], 13)
            self.assertEqual(report["summary"]["PASS"], 13)
            self.assertEqual(report["summary"]["FAIL"], 0)
            self.assertEqual(report["summary"]["NOT_APPLICABLE"], 0)
            self.assertTrue(report["summary"]["static_preflight_ok"])
            self.assertTrue(report["staging_unchanged"])
            self.assertFalse(report["source_write_performed"])
            self.assertFalse(report["operational_deployment_performed"])
            self.assertFalse(report["blocker_status_promotions_performed"])
            self.assertTrue(report["runtime_validation_still_required"])
            self.assertFalse(report["v8_homologated"])
            self.assertEqual(snapshot(staging), before)

    def test_b01_destructive_reprocessing_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp), "b01")
            report = preflight.run_preflight(staging, acceptance, ROOT, deepcopy(STATIC_POLICY))
            self.assertEqual(contract(report, "B01_REPROCESSING_CANDIDATE")["status"], "FAIL")

    def test_b02_get_mutation_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp), "b02")
            report = preflight.run_preflight(staging, acceptance, ROOT, deepcopy(STATIC_POLICY))
            self.assertEqual(contract(report, "B02_GET_READ_PURITY")["status"], "FAIL")

    def test_b03_output_without_gate_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp), "b03")
            report = preflight.run_preflight(staging, acceptance, ROOT, deepcopy(STATIC_POLICY))
            self.assertEqual(contract(report, "B03_SINGLE_OUTPUT_GATE")["status"], "FAIL")

    def test_b07_direct_closing_sql_outside_domain_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp), "b07_outside")
            report = preflight.run_preflight(staging, acceptance, ROOT, deepcopy(STATIC_POLICY))
            self.assertEqual(contract(report, "B07_B09_B10_OPERATIONAL_SCOPE")["status"], "FAIL")

    def test_b11_pronta_mapped_to_conference_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp), "b11")
            report = preflight.run_preflight(staging, acceptance, ROOT, deepcopy(STATIC_POLICY))
            self.assertEqual(contract(report, "B11_B37_STATE_SEMANTICS")["status"], "FAIL")

    def test_b34_raw_string_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp), "b34")
            report = preflight.run_preflight(staging, acceptance, ROOT, deepcopy(STATIC_POLICY))
            self.assertEqual(contract(report, "B34_CLASSIFICACAO_INATIVACAO")["status"], "FAIL")

    def test_b38_mutating_route_without_auth_marker_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp), "b38")
            report = preflight.run_preflight(staging, acceptance, ROOT, deepcopy(STATIC_POLICY))
            self.assertEqual(contract(report, "B38_ROUTE_SECURITY_STATIC")["status"], "FAIL")

    def test_b39_manual_selection_without_guard_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp), "b39")
            report = preflight.run_preflight(staging, acceptance, ROOT, deepcopy(STATIC_POLICY))
            self.assertEqual(contract(report, "B39_MANUAL_SELECTION_GATE")["status"], "FAIL")

    def test_b40_unguarded_update_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp), "b40")
            report = preflight.run_preflight(staging, acceptance, ROOT, deepcopy(STATIC_POLICY))
            self.assertEqual(contract(report, "B40_SQLITE_CAS_STATIC")["status"], "FAIL")

    def test_b44_landscape_fails_ui_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp), "b44")
            report = preflight.run_preflight(staging, acceptance, ROOT, deepcopy(STATIC_POLICY))
            self.assertEqual(contract(report, "B44_RELATORIO_A4")["status"], "FAIL")

    def test_b47_missing_visible_sintegra_link_fails_ui_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp), "b47")
            report = preflight.run_preflight(staging, acceptance, ROOT, deepcopy(STATIC_POLICY))
            self.assertEqual(contract(report, "B47_SINTEGRA_ATALHOS")["status"], "FAIL")

    def test_tampered_stage_is_blocked_before_static_contracts(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp))
            write(staging / "src/app.py", "tampered = True\n")
            with self.assertRaisesRegex(preflight.StaticPreflightError, "Etapa 84"):
                preflight.run_preflight(staging, acceptance, ROOT, deepcopy(STATIC_POLICY))

    def test_policy_root_inside_staging_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp))
            with self.assertRaisesRegex(preflight.StaticPreflightError, "Raiz de políticas"):
                preflight.run_preflight(staging, acceptance, staging, deepcopy(STATIC_POLICY))

    def test_policy_hashes_and_external_ui_policy_are_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp))
            report = preflight.run_preflight(staging, acceptance, ROOT, deepcopy(STATIC_POLICY))
            self.assertEqual(report["policy_manifest_sha256"], preflight.canonical_hash(STATIC_POLICY))
            ui_path = ROOT / "config/operational_ui_contract_v8.json"
            self.assertEqual(report["external_policy"]["file_sha256"], preflight.sha256_file(ui_path))
            self.assertEqual(len(report["inline_policy_sha256"]), 9)

    def test_cli_refuses_output_inside_staging(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            staging, acceptance = build_stage(base)
            acceptance_path = base / "acceptance.json"
            policy_path = base / "policy.json"
            acceptance_path.write_text(json.dumps(acceptance), encoding="utf-8")
            policy_path.write_text(json.dumps(STATIC_POLICY), encoding="utf-8")
            old_argv = sys.argv
            try:
                sys.argv = [
                    "run_reconciled_staging_static_preflight.py",
                    "--staging-dir", str(staging),
                    "--acceptance", str(acceptance_path),
                    "--policy", str(policy_path),
                    "--policy-root", str(ROOT),
                    "--output", str(staging / "forbidden.json"),
                ]
                self.assertEqual(preflight.main(), 2)
            finally:
                sys.argv = old_argv
            self.assertFalse((staging / "forbidden.json").exists())

    def test_not_applicable_is_distinct_from_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_stage(Path(tmp))
            policy = deepcopy(STATIC_POLICY)
            policy["policies"]["B01"]["reprocess_name_patterns"] = ["nao_existe"]
            report = preflight.run_preflight(staging, acceptance, ROOT, policy)
            self.assertEqual(contract(report, "B01_REPROCESSING_CANDIDATE")["status"], "NOT_APPLICABLE")
            self.assertTrue(report["summary"]["static_preflight_ok"])


if __name__ == "__main__":
    unittest.main()
