from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

SHA256_RE = re.compile(r"^[0-9A-Fa-f]{64}$")
AREA_RE = re.compile(r"^[a-z0-9_]+$")


class ReconciliationPlanError(RuntimeError):
    pass


def canonical_hash(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReconciliationPlanError(f"JSON inválido {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReconciliationPlanError(f"JSON deve ser objeto: {path.name}")
    return value


def validate_policy(policy: dict) -> dict:
    if policy.get("version") != 1:
        raise ReconciliationPlanError("Versão de política não suportada.")
    if policy.get("automatic_write_allowed") is not False:
        raise ReconciliationPlanError("A política deve proibir escrita automática.")

    allowed = policy.get("allowed_statuses")
    actions = policy.get("action_by_status")
    if not isinstance(allowed, list) or not allowed or not all(isinstance(x, str) for x in allowed):
        raise ReconciliationPlanError("allowed_statuses inválido.")
    if not isinstance(actions, dict) or set(actions) != set(allowed):
        raise ReconciliationPlanError("action_by_status deve cobrir exatamente allowed_statuses.")
    if any(not str(actions[item]).strip() for item in allowed):
        raise ReconciliationPlanError("Ação vazia na política.")

    sensitive_areas = policy.get("sensitive_areas", [])
    sensitive_patterns = policy.get("sensitive_path_patterns", [])
    if not isinstance(sensitive_areas, list) or not all(isinstance(x, str) for x in sensitive_areas):
        raise ReconciliationPlanError("sensitive_areas inválido.")
    if not isinstance(sensitive_patterns, list) or not all(isinstance(x, str) for x in sensitive_patterns):
        raise ReconciliationPlanError("sensitive_path_patterns inválido.")
    if not str(policy.get("sensitive_action") or "").strip():
        raise ReconciliationPlanError("sensitive_action ausente.")
    return policy


def safe_relative_path(raw: object) -> str:
    value = str(raw or "").strip()
    if not value or "\\" in value or "\x00" in value:
        raise ReconciliationPlanError(f"relative_path inválido: {value!r}")
    pure = PurePosixPath(value)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts or pure.parts[0].endswith(":"):
        raise ReconciliationPlanError(f"relative_path inseguro: {value!r}")
    return pure.as_posix()


def validate_hash(value: object, field: str, *, required: bool) -> str:
    text = str(value or "").strip().upper()
    if not text and not required:
        return ""
    if not SHA256_RE.fullmatch(text):
        raise ReconciliationPlanError(f"{field} inválido.")
    return text


def normalize_row(raw: object, policy: dict) -> dict:
    if not isinstance(raw, dict):
        raise ReconciliationPlanError("Linha de reconciliação deve ser objeto.")
    area = str(raw.get("area") or "").strip()
    if not AREA_RE.fullmatch(area):
        raise ReconciliationPlanError(f"Área inválida: {area!r}")
    path = safe_relative_path(raw.get("relative_path"))
    status = str(raw.get("status") or "").strip().upper()
    if status not in set(policy["allowed_statuses"]):
        raise ReconciliationPlanError(f"Status não permitido: {status!r}")

    runtime_required = status in {"SAME", "CHANGED", "RUNTIME_ONLY"}
    repo_required = status in {"SAME", "CHANGED", "REPO_ONLY"}
    runtime_hash = validate_hash(raw.get("runtime_sha256"), "runtime_sha256", required=runtime_required)
    repo_hash = validate_hash(raw.get("repo_sha256"), "repo_sha256", required=repo_required)

    if status == "RUNTIME_ONLY" and repo_hash:
        raise ReconciliationPlanError(f"RUNTIME_ONLY com repo_sha256: {area}/{path}")
    if status == "REPO_ONLY" and runtime_hash:
        raise ReconciliationPlanError(f"REPO_ONLY com runtime_sha256: {area}/{path}")
    if status == "SAME" and runtime_hash != repo_hash:
        raise ReconciliationPlanError(f"SAME com hashes divergentes: {area}/{path}")
    if status == "CHANGED" and runtime_hash == repo_hash:
        raise ReconciliationPlanError(f"CHANGED com hashes iguais: {area}/{path}")

    try:
        runtime_size = int(raw.get("runtime_size") or 0)
        repo_size = int(raw.get("repo_size") or 0)
    except (TypeError, ValueError) as exc:
        raise ReconciliationPlanError(f"Tamanho inválido: {area}/{path}") from exc
    if runtime_size < 0 or repo_size < 0:
        raise ReconciliationPlanError(f"Tamanho negativo: {area}/{path}")
    if status == "SAME" and runtime_size != repo_size:
        raise ReconciliationPlanError(f"SAME com tamanhos divergentes: {area}/{path}")

    return {
        "area": area,
        "relative_path": path,
        "status": status,
        "runtime_sha256": runtime_hash,
        "repo_sha256": repo_hash,
        "runtime_size": runtime_size,
        "repo_size": repo_size,
    }


def is_sensitive(row: dict, policy: dict) -> bool:
    if row["area"] in set(policy.get("sensitive_areas", [])):
        return True
    path = row["relative_path"].lower()
    return any(pattern.lower() in path for pattern in policy.get("sensitive_path_patterns", []))


def proposed_action(row: dict, policy: dict) -> tuple[str, str, str]:
    if row["status"] == "SAME":
        return str(policy["action_by_status"]["SAME"]), "LOW", "Conteúdo idêntico; nenhuma ação proposta."
    if is_sensitive(row, policy):
        return str(policy["sensitive_action"]), "CRITICAL", "Diferença em área/caminho sensível exige revisão humana explícita."
    action = str(policy["action_by_status"][row["status"]])
    if row["status"] == "CHANGED":
        return action, "HIGH", "Runtime e repositório possuem versões diferentes; merge/revisão obrigatória."
    if row["status"] == "RUNTIME_ONLY":
        return action, "MEDIUM", "Arquivo existe apenas no runtime; avaliar incorporação ao baseline."
    return action, "MEDIUM", "Arquivo existe apenas no repositório; avaliar se é patrimônio novo ou ausência do runtime."


def build_plan(diff: dict, policy: dict) -> dict:
    validate_policy(policy)
    rows_raw = diff.get("rows")
    if not isinstance(rows_raw, list):
        raise ReconciliationPlanError("Diff sem lista rows.")

    normalized: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for raw in rows_raw:
        row = normalize_row(raw, policy)
        key = (row["area"], row["relative_path"])
        if key in seen:
            raise ReconciliationPlanError(f"Linha duplicada: {row['area']}/{row['relative_path']}")
        seen.add(key)
        normalized.append(row)

    normalized.sort(key=lambda item: (item["area"], item["relative_path"]))
    entries: list[dict] = []
    for row in normalized:
        action, risk, reason = proposed_action(row, policy)
        entries.append({
            **row,
            "proposed_action": action,
            "risk": risk,
            "reason": reason,
            "automatic_write": False,
            "review_required": row["status"] != "SAME",
        })

    action_counts: dict[str, int] = {}
    risk_counts: dict[str, int] = {}
    for entry in entries:
        action_counts[entry["proposed_action"]] = action_counts.get(entry["proposed_action"], 0) + 1
        risk_counts[entry["risk"]] = risk_counts.get(entry["risk"], 0) + 1

    payload = {
        "version": 1,
        "mode": "READ_ONLY_RECONCILIATION_PLAN_NOT_EXECUTION",
        "automatic_write_allowed": False,
        "source_diff_sha256": canonical_hash(diff),
        "policy_sha256": canonical_hash(policy),
        "summary": {
            "total": len(entries),
            "review_required": sum(1 for entry in entries if entry["review_required"]),
            "actions": dict(sorted(action_counts.items())),
            "risks": dict(sorted(risk_counts.items())),
        },
        "entries": entries,
        "v8_homologated": False,
    }
    payload["plan_sha256"] = canonical_hash(payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera plano read-only para revisar diferenças runtime ↔ repositório.")
    parser.add_argument("--diff", required=True, type=Path, help="RECONCILIATION_DIFF.json")
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.output.exists():
        print("RECONCILIATION_PLAN_ERRO: saída já existe e não será sobrescrita.", file=sys.stderr)
        return 2
    try:
        diff = load_json(args.diff)
        policy = load_json(args.policy)
        plan = build_plan(diff, policy)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(plan, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (ReconciliationPlanError, OSError) as exc:
        print(f"RECONCILIATION_PLAN_ERRO: {exc}", file=sys.stderr)
        return 2

    print("RECONCILIATION_PLAN_OK")
    print(f"Itens: {plan['summary']['total']}")
    print(f"Revisão obrigatória: {plan['summary']['review_required']}")
    print("Escrita automática: NÃO")
    print("V8 homologada: NÃO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
