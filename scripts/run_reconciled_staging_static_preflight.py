from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath

import audit_classificacao_inativacao_contract as classification_audit
import audit_get_read_purity as get_purity_audit
import audit_manual_selection_gate as manual_selection_audit
import audit_operational_scope_contract as scope_audit
import audit_operational_ui_contract as ui_audit
import audit_output_gate_contract as output_gate_audit
import audit_reprocessing_candidate_contract as reprocessing_audit
import audit_route_security as route_security_audit
import audit_sqlite_cas_contract as cas_audit
import audit_state_semantics_contract as state_semantics_audit
import verify_reconciled_staging as staging_verifier

POLICY_MODE = "RECONCILED_STAGING_STATIC_PREFLIGHT_POLICY"
REPORT_MODE = "RECONCILED_STAGING_STATIC_PREFLIGHT_READ_ONLY"


class StaticPreflightError(RuntimeError):
    pass


def canonical_hash(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise StaticPreflightError(f"JSON inválido {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise StaticPreflightError(f"JSON deve ser objeto: {path.name}")
    return value


def normalize_policy(policy: dict) -> dict:
    if not isinstance(policy, dict) or policy.get("version") != 1:
        raise StaticPreflightError("Política deve ser objeto version=1.")
    if policy.get("audit") != "V8" or policy.get("mode") != POLICY_MODE:
        raise StaticPreflightError("Identidade da política de preflight inválida.")
    policies = policy.get("policies")
    external = policy.get("external_policies")
    required = {"B01", "B02", "B03", "B07_B09_B10", "B11_B37", "B34", "B38", "B39", "B40"}
    if not isinstance(policies, dict) or set(policies) != required:
        raise StaticPreflightError("Conjunto de políticas internas do preflight está incompleto/divergente.")
    if not isinstance(external, dict) or set(external) != {"B43_B44_B46_B47"}:
        raise StaticPreflightError("Política UI externa ausente/divergente.")
    return policy


def safe_policy_path(policy_root: Path, relative: object) -> Path:
    text = str(relative or "").replace("\\", "/").strip()
    pure = PurePosixPath(text)
    if not text or pure.is_absolute() or ".." in pure.parts or "\x00" in text:
        raise StaticPreflightError(f"Caminho de política externa inseguro: {relative!r}")
    path = (policy_root / Path(*pure.parts)).resolve()
    try:
        path.relative_to(policy_root.resolve())
    except ValueError as exc:
        raise StaticPreflightError("Política externa sai da raiz canônica.") from exc
    if not path.is_file() or path.is_symlink():
        raise StaticPreflightError(f"Política externa ausente/inválida: {text}")
    return path


def snapshot_tree(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise StaticPreflightError(f"Symlink proibido no staging: {rel}")
        if path.is_file():
            result[rel] = sha256_file(path)
    return result


def contract_result(
    contract_id: str,
    blockers: list[str],
    audit_name: str,
    ok: bool,
    target_count: int,
    findings: list[dict],
    *,
    policy_sha256: str,
    extra: dict | None = None,
    force_applicable: bool = False,
) -> dict:
    if not ok:
        status = "FAIL"
    elif target_count == 0 and not force_applicable:
        status = "NOT_APPLICABLE"
    else:
        status = "PASS"
    value = {
        "contract_id": contract_id,
        "blockers": blockers,
        "audit": audit_name,
        "status": status,
        "target_count": int(target_count),
        "finding_count": len(findings),
        "findings": findings,
        "policy_sha256": policy_sha256,
    }
    if extra:
        value["coverage"] = extra
    return value


def run_preflight(staging_dir: Path, acceptance: dict, policy_root: Path, policy: dict) -> dict:
    staging_dir = staging_dir.resolve()
    policy_root = policy_root.resolve()
    if not staging_dir.is_dir():
        raise StaticPreflightError("Diretório de staging inválido.")
    if not policy_root.is_dir():
        raise StaticPreflightError("Raiz canônica de políticas inválida.")
    try:
        policy_root.relative_to(staging_dir)
    except ValueError:
        pass
    else:
        raise StaticPreflightError("Raiz de políticas não pode ficar dentro do staging auditado.")

    normalized_policy = normalize_policy(policy)
    before = snapshot_tree(staging_dir)
    try:
        verification = staging_verifier.verify_staging(staging_dir, acceptance)
    except staging_verifier.StagingVerificationError as exc:
        raise StaticPreflightError(f"Staging não passou pela verificação da Etapa 84: {exc}") from exc

    policies = normalized_policy["policies"]
    policy_hashes = {key: canonical_hash(value) for key, value in policies.items()}

    external_path = safe_policy_path(
        policy_root,
        normalized_policy["external_policies"]["B43_B44_B46_B47"],
    )
    ui_policy = load_json(external_path)
    external_policy = {
        "relative_path": external_path.relative_to(policy_root).as_posix(),
        "file_sha256": sha256_file(external_path),
        "canonical_sha256": canonical_hash(ui_policy),
    }

    try:
        b01 = reprocessing_audit.audit(staging_dir, policies["B01"])
        b02 = get_purity_audit.audit(staging_dir, policies["B02"])
        b03 = output_gate_audit.audit(staging_dir, policies["B03"])
        b_scope = scope_audit.audit(staging_dir, policies["B07_B09_B10"])
        b_state = state_semantics_audit.audit(staging_dir, policies["B11_B37"])
        b34 = classification_audit.audit_tree(staging_dir, policies["B34"])
        b38 = route_security_audit.audit_tree(staging_dir, policies["B38"])
        b39 = manual_selection_audit.audit(staging_dir, policies["B39"])
        b40 = cas_audit.audit_tree(staging_dir, policies["B40"])
        b_ui = ui_audit.audit(staging_dir, ui_policy)
    except (
        reprocessing_audit.ContractError,
        get_purity_audit.PurityError,
        output_gate_audit.GateError,
        scope_audit.ScopeError,
        state_semantics_audit.StateSemanticsError,
        classification_audit.ClassificationContractError,
        route_security_audit.RouteAuditError,
        manual_selection_audit.SelectionGateError,
        cas_audit.CasContractError,
        ui_audit.UiContractError,
        ValueError,
    ) as exc:
        raise StaticPreflightError(f"Falha estrutural ao executar auditor estático: {exc}") from exc

    contracts: list[dict] = []
    contracts.append(contract_result(
        "B01_REPROCESSING_CANDIDATE",
        ["B01"],
        b01["audit"],
        bool(b01["all_ok"]),
        int(b01["target_count"]),
        list(b01["findings"]),
        policy_sha256=policy_hashes["B01"],
    ))
    contracts.append(contract_result(
        "B02_GET_READ_PURITY",
        ["B02"],
        b02["audit"],
        bool(b02["all_ok"]),
        int(b02["get_route_count"]),
        list(b02["findings"]),
        policy_sha256=policy_hashes["B02"],
    ))
    contracts.append(contract_result(
        "B03_SINGLE_OUTPUT_GATE",
        ["B03"],
        b03["audit"],
        bool(b03["all_ok"]),
        int(b03["entrypoint_count"]),
        list(b03["findings"]),
        policy_sha256=policy_hashes["B03"],
    ))

    scope_findings = list(b_scope["findings"])
    if b_scope["closing_reference_count"] > 0 and b_scope["facade_usage_count"] == 0:
        scope_findings.append({
            "code": "NO_CANONICAL_SCOPE_FACADE_USAGE",
            "message": "Há referências ao universo mensal, mas nenhuma fachada canônica foi localizada.",
        })
    contracts.append(contract_result(
        "B07_B09_B10_OPERATIONAL_SCOPE",
        ["B07", "B09", "B10"],
        b_scope["audit"],
        not scope_findings,
        int(b_scope["closing_reference_count"]),
        scope_findings,
        policy_sha256=policy_hashes["B07_B09_B10"],
        extra={"facade_usage_count": int(b_scope["facade_usage_count"])},
    ))
    contracts.append(contract_result(
        "B11_B37_STATE_SEMANTICS",
        ["B11", "B37"],
        b_state["audit"],
        bool(b_state["all_ok"]),
        int(b_state["mapping_target_count"]),
        list(b_state["findings"]),
        policy_sha256=policy_hashes["B11_B37"],
    ))
    contracts.append(contract_result(
        "B34_CLASSIFICACAO_INATIVACAO",
        ["B34"],
        "B34_CLASSIFICATION_ENUM_CONTRACT",
        bool(b34["static_ok"]),
        int(b34["summary"]["usages"]),
        list(b34["findings"]),
        policy_sha256=policy_hashes["B34"],
        extra={"parse_errors": int(b34["summary"]["parse_errors"])},
    ))

    route_findings = list(b38["findings"])
    route_findings.extend({"code": "PARSE_ERROR", "detail": error} for error in b38["errors"])
    contracts.append(contract_result(
        "B38_ROUTE_SECURITY_STATIC",
        ["B38"],
        "B38_ROUTE_SECURITY_STATIC_SIGNALS",
        not route_findings,
        int(b38["summary"]["routes"]),
        route_findings,
        policy_sha256=policy_hashes["B38"],
        extra={
            "mutating_routes": int(b38["summary"]["mutating_routes"]),
            "runtime_validation_still_required": True,
        },
    ))
    contracts.append(contract_result(
        "B39_MANUAL_SELECTION_GATE",
        ["B39"],
        b39["audit"],
        bool(b39["all_ok"]),
        int(b39["target_count"]),
        list(b39["findings"]),
        policy_sha256=policy_hashes["B39"],
    ))
    contracts.append(contract_result(
        "B40_SQLITE_CAS_STATIC",
        ["B40"],
        "B40_SQLITE_CAS_STATIC_CONTRACT",
        bool(b40["static_ok"]),
        int(b40["summary"]["protected_updates"]),
        list(b40["findings"]),
        policy_sha256=policy_hashes["B40"],
        extra={
            "unresolved_execute_calls": int(b40["summary"]["unresolved_execute_calls"]),
            "runtime_concurrency_test_still_required": True,
        },
    ))

    ui_blockers = {
        "B43_PENDENCIAS_COMPETENCIA_ATIVA": ["B43"],
        "B44_RELATORIO_A4": ["B44"],
        "B46_MONITOR_FONTE_UNICA": ["B46"],
        "B47_SINTEGRA_ATALHOS": ["B47"],
    }
    ui_findings_by_id: dict[str, list[dict]] = {key: [] for key in ui_blockers}
    for finding in b_ui["findings"]:
        contract_id = str(finding.get("contract_id") or "")
        if contract_id in ui_findings_by_id:
            ui_findings_by_id[contract_id].append(finding)
    for ui_item in b_ui["contracts"]:
        contract_id = str(ui_item["contract_id"])
        if contract_id not in ui_blockers:
            raise StaticPreflightError(f"Contrato UI canônico inesperado: {contract_id}")
        findings = ui_findings_by_id[contract_id]
        contracts.append(contract_result(
            contract_id,
            ui_blockers[contract_id],
            b_ui["audit"],
            bool(ui_item["ok"]) and not findings,
            len(ui_item["matched_files"]),
            findings,
            policy_sha256=external_policy["canonical_sha256"],
            extra={"matched_files": list(ui_item["matched_files"])},
            force_applicable=True,
        ))

    after = snapshot_tree(staging_dir)
    if before != after:
        raise StaticPreflightError("Preflight estático alterou a árvore de staging.")

    counts = {
        status: sum(1 for item in contracts if item["status"] == status)
        for status in ("PASS", "FAIL", "NOT_APPLICABLE")
    }
    result = {
        "version": 1,
        "mode": REPORT_MODE,
        "staging_verification_sha256": str(verification["verification_sha256"]),
        "acceptance_sha256": str(verification["acceptance_sha256"]),
        "tree_sha256": str(verification["tree_sha256"]),
        "policy_manifest_sha256": canonical_hash(normalized_policy),
        "inline_policy_sha256": policy_hashes,
        "external_policy": external_policy,
        "contracts": contracts,
        "summary": {
            "contracts": len(contracts),
            **counts,
            "static_preflight_ok": counts["FAIL"] == 0,
        },
        "staging_unchanged": True,
        "source_write_performed": False,
        "operational_deployment_performed": False,
        "blocker_status_promotions_performed": False,
        "runtime_validation_still_required": True,
        "v8_homologated": False,
    }
    result["preflight_sha256"] = canonical_hash(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Executa contratos estáticos sobre staging reconciliado previamente verificado, sem alterar a árvore."
    )
    parser.add_argument("--staging-dir", required=True, type=Path)
    parser.add_argument("--acceptance", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--policy-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    staging = args.staging_dir.resolve()
    output = args.output.resolve()
    try:
        output.relative_to(staging)
    except ValueError:
        pass
    else:
        print("RECONCILED_STATIC_PREFLIGHT_ERRO: saída não pode ficar dentro do staging.", file=sys.stderr)
        return 2
    if output.exists():
        print("RECONCILED_STATIC_PREFLIGHT_ERRO: saída já existe e não será sobrescrita.", file=sys.stderr)
        return 2
    try:
        report = run_preflight(
            staging,
            load_json(args.acceptance),
            args.policy_root,
            load_json(args.policy),
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (StaticPreflightError, OSError) as exc:
        print(f"RECONCILED_STATIC_PREFLIGHT_ERRO: {exc}", file=sys.stderr)
        return 2

    print("RECONCILED_STATIC_PREFLIGHT_OK")
    for key in ("PASS", "FAIL", "NOT_APPLICABLE"):
        print(f"{key}: {report['summary'][key]}")
    print(f"Estático sem falhas: {'SIM' if report['summary']['static_preflight_ok'] else 'NÃO'}")
    print("Staging alterado: NÃO")
    print("Status de blockers promovidos: NÃO")
    print("Validação runtime ainda necessária: SIM")
    print("V8 homologada: NÃO")
    return 0 if report["summary"]["static_preflight_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
