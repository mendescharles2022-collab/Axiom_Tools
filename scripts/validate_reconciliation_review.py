from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

DECISIONS = {
    "PENDING",
    "ADOPT_RUNTIME",
    "KEEP_REPO",
    "MERGE_REQUIRED",
    "EXCLUDE_WITH_REASON",
    "SECURITY_REVIEW_REQUIRED",
}
UNRESOLVED = {"PENDING", "MERGE_REQUIRED", "SECURITY_REVIEW_REQUIRED"}


class ReconciliationReviewError(RuntimeError):
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
        raise ReconciliationReviewError(f"JSON inválido {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReconciliationReviewError(f"JSON deve ser objeto: {path.name}")
    return value


def verify_plan(plan: dict) -> None:
    if plan.get("version") != 1 or plan.get("mode") != "READ_ONLY_RECONCILIATION_PLAN_NOT_EXECUTION":
        raise ReconciliationReviewError("Plano inválido ou incompatível.")
    if plan.get("automatic_write_allowed") is not False or plan.get("v8_homologated") is not False:
        raise ReconciliationReviewError("Plano não preserva contrato read-only/não homologado.")
    expected = str(plan.get("plan_sha256") or "").upper()
    payload = dict(plan)
    payload.pop("plan_sha256", None)
    if expected != canonical_hash(payload):
        raise ReconciliationReviewError("plan_sha256 inválido.")
    if not isinstance(plan.get("entries"), list):
        raise ReconciliationReviewError("Plano sem entries.")


def _required_map(plan: dict) -> dict[tuple[str, str], dict]:
    required: dict[tuple[str, str], dict] = {}
    for entry in plan["entries"]:
        if not isinstance(entry, dict) or entry.get("review_required") is not True:
            continue
        key = (str(entry.get("area") or "").strip(), str(entry.get("relative_path") or "").strip())
        if not all(key):
            raise ReconciliationReviewError("Entrada revisável do plano sem identidade.")
        if key in required:
            raise ReconciliationReviewError(f"Plano contém revisão duplicada: {key[0]}/{key[1]}")
        required[key] = entry
    return required


def _allowed_decisions(plan_entry: dict) -> set[str]:
    proposed = str(plan_entry.get("proposed_action") or "")
    if proposed == "SECURITY_REVIEW_REQUIRED":
        return {"PENDING", "SECURITY_REVIEW_REQUIRED", "KEEP_REPO"}
    if proposed == "REVIEW_MERGE":
        return {"PENDING", "MERGE_REQUIRED", "ADOPT_RUNTIME", "KEEP_REPO"}
    if proposed == "REVIEW_IMPORT_RUNTIME":
        return {"PENDING", "ADOPT_RUNTIME", "EXCLUDE_WITH_REASON"}
    if proposed == "REVIEW_KEEP_REPO":
        return {"PENDING", "KEEP_REPO", "EXCLUDE_WITH_REASON"}
    raise ReconciliationReviewError(f"Ação proposta desconhecida: {proposed!r}")


def _validate_evidence(item: dict, decision: str, label: str) -> None:
    reviewer = str(item.get("reviewer") or "").strip()
    reason = str(item.get("reason") or "").strip()
    evidence = item.get("evidence")
    if decision == "PENDING":
        if reviewer or reason or evidence not in ([], None):
            raise ReconciliationReviewError(f"PENDING não deve fingir revisão preenchida: {label}")
        return
    if len(reviewer) < 2:
        raise ReconciliationReviewError(f"Revisor obrigatório: {label}")
    if len(reason) < 8:
        raise ReconciliationReviewError(f"Motivo insuficiente: {label}")
    if not isinstance(evidence, list) or not evidence or not all(isinstance(x, str) and x.strip() for x in evidence):
        raise ReconciliationReviewError(f"Evidência obrigatória: {label}")


def validate_review(plan: dict, review: dict) -> dict:
    verify_plan(plan)
    required = _required_map(plan)
    if review.get("version") != 1:
        raise ReconciliationReviewError("Versão da revisão não suportada.")
    if review.get("mode") not in {
        "RECONCILIATION_REVIEW_SKELETON_NOT_EXECUTION",
        "RECONCILIATION_REVIEW_NOT_EXECUTION",
    }:
        raise ReconciliationReviewError("Modo da revisão inválido.")
    if review.get("automatic_write_allowed") is not False:
        raise ReconciliationReviewError("Revisão não pode permitir escrita automática.")
    if review.get("v8_homologated") is not False:
        raise ReconciliationReviewError("Revisão não pode homologar V8.")
    if str(review.get("plan_sha256") or "").upper() != str(plan["plan_sha256"]).upper():
        raise ReconciliationReviewError("Revisão não está vinculada ao plan_sha256 correto.")

    items = review.get("items")
    if not isinstance(items, list):
        raise ReconciliationReviewError("Revisão sem lista items.")
    seen: set[tuple[str, str]] = set()
    normalized: list[dict] = []
    for raw in items:
        if not isinstance(raw, dict):
            raise ReconciliationReviewError("Item de revisão inválido.")
        key = (str(raw.get("area") or "").strip(), str(raw.get("relative_path") or "").strip())
        label = f"{key[0]}/{key[1]}"
        if key not in required:
            raise ReconciliationReviewError(f"Decisão para item inexistente/não revisável: {label}")
        if key in seen:
            raise ReconciliationReviewError(f"Decisão duplicada: {label}")
        seen.add(key)
        plan_entry = required[key]
        for field in ("status", "proposed_action", "risk"):
            if str(raw.get(field) or "") != str(plan_entry.get(field) or ""):
                raise ReconciliationReviewError(f"Metadado alterado na revisão ({field}): {label}")
        decision = str(raw.get("decision") or "").strip().upper()
        if decision not in DECISIONS:
            raise ReconciliationReviewError(f"Decisão desconhecida: {label}")
        if decision not in _allowed_decisions(plan_entry):
            raise ReconciliationReviewError(f"Decisão incompatível com ação/risco do plano: {label}")
        if str(plan_entry.get("risk") or "") == "CRITICAL" and decision == "ADOPT_RUNTIME":
            raise ReconciliationReviewError(f"Conteúdo CRITICAL não pode ser adotado diretamente: {label}")
        _validate_evidence(raw, decision, label)
        normalized.append({
            "area": key[0],
            "relative_path": key[1],
            "decision": decision,
        })

    missing = sorted(set(required) - seen)
    if missing:
        raise ReconciliationReviewError(
            "Itens revisáveis sem decisão: " + ", ".join(f"{a}/{p}" for a, p in missing)
        )

    counts: dict[str, int] = {}
    for item in normalized:
        counts[item["decision"]] = counts.get(item["decision"], 0) + 1
    pending = sum(counts.get(item, 0) for item in UNRESOLVED)
    review_complete = counts.get("PENDING", 0) == 0
    baseline_ready = pending == 0
    result = {
        "version": 1,
        "mode": "RECONCILIATION_REVIEW_VALIDATION_NOT_EXECUTION",
        "plan_sha256": plan["plan_sha256"],
        "items_required": len(required),
        "items_validated": len(normalized),
        "decision_counts": dict(sorted(counts.items())),
        "review_complete": review_complete,
        "baseline_ready": baseline_ready,
        "automatic_write_allowed": False,
        "v8_homologated": False,
    }
    result["validation_sha256"] = canonical_hash(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida decisões humanas do plano de reconciliação sem executar alterações.")
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--require-baseline-ready", action="store_true")
    args = parser.parse_args()

    if args.output.exists():
        print("RECONCILIATION_REVIEW_ERRO: saída já existe e não será sobrescrita.", file=sys.stderr)
        return 2
    try:
        report = validate_review(load_json(args.plan), load_json(args.review))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (ReconciliationReviewError, OSError) as exc:
        print(f"RECONCILIATION_REVIEW_ERRO: {exc}", file=sys.stderr)
        return 2

    print("RECONCILIATION_REVIEW_OK")
    print(f"Itens: {report['items_validated']}/{report['items_required']}")
    print(f"Revisão completa: {'SIM' if report['review_complete'] else 'NÃO'}")
    print(f"Baseline liberado: {'SIM' if report['baseline_ready'] else 'NÃO'}")
    print("Escrita automática: NÃO")
    print("V8 homologada: NÃO")
    if args.require_baseline_ready and not report["baseline_ready"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
