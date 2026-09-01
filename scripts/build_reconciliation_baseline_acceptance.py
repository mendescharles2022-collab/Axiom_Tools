from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import validate_reconciliation_review as review_validator


class BaselineAcceptanceError(RuntimeError):
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
        raise BaselineAcceptanceError(f"JSON inválido {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise BaselineAcceptanceError(f"JSON deve ser objeto: {path.name}")
    return value


def _plan_entry_map(plan: dict) -> dict[tuple[str, str], dict]:
    entries = plan.get("entries")
    if not isinstance(entries, list):
        raise BaselineAcceptanceError("Plano sem lista entries.")
    result: dict[tuple[str, str], dict] = {}
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("review_required") is not True:
            continue
        key = (
            str(entry.get("area") or "").strip(),
            str(entry.get("relative_path") or "").strip(),
        )
        if not all(key):
            raise BaselineAcceptanceError("Entrada revisável sem identidade.")
        if key in result:
            raise BaselineAcceptanceError(f"Entrada revisável duplicada: {key[0]}/{key[1]}")
        result[key] = entry
    return result


def build_acceptance(plan: dict, review: dict) -> dict:
    try:
        validation = review_validator.validate_review(plan, review)
    except review_validator.ReconciliationReviewError as exc:
        raise BaselineAcceptanceError(str(exc)) from exc

    if validation.get("review_complete") is not True:
        raise BaselineAcceptanceError("Revisão humana ainda não está completa.")
    if validation.get("baseline_ready") is not True:
        raise BaselineAcceptanceError("Revisão humana ainda não libera baseline.")
    if validation.get("automatic_write_allowed") is not False:
        raise BaselineAcceptanceError("Validação de revisão permitiu escrita automática indevida.")
    if validation.get("v8_homologated") is not False:
        raise BaselineAcceptanceError("Validação de revisão marcou homologação indevida.")

    plan_entries = _plan_entry_map(plan)
    review_items = review.get("items")
    if not isinstance(review_items, list):
        raise BaselineAcceptanceError("Revisão sem lista items.")

    decisions: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for item in review_items:
        if not isinstance(item, dict):
            raise BaselineAcceptanceError("Item de revisão inválido.")
        key = (
            str(item.get("area") or "").strip(),
            str(item.get("relative_path") or "").strip(),
        )
        if key not in plan_entries:
            raise BaselineAcceptanceError(f"Item não pertence ao plano revisável: {key[0]}/{key[1]}")
        if key in seen:
            raise BaselineAcceptanceError(f"Item duplicado na revisão: {key[0]}/{key[1]}")
        seen.add(key)
        entry = plan_entries[key]
        decisions.append({
            "area": key[0],
            "relative_path": key[1],
            "status": str(entry.get("status") or ""),
            "proposed_action": str(entry.get("proposed_action") or ""),
            "risk": str(entry.get("risk") or ""),
            "runtime_sha256": str(entry.get("runtime_sha256") or ""),
            "repo_sha256": str(entry.get("repo_sha256") or ""),
            "decision": str(item.get("decision") or "").strip().upper(),
            "reviewer": str(item.get("reviewer") or "").strip(),
            "reason": str(item.get("reason") or "").strip(),
            "evidence": list(item.get("evidence") or []),
        })

    if seen != set(plan_entries):
        raise BaselineAcceptanceError("Aceite não cobre exatamente todos os itens revisáveis.")

    decisions.sort(key=lambda item: (item["area"], item["relative_path"]))
    acceptance = {
        "version": 1,
        "mode": "RECONCILIATION_BASELINE_ACCEPTANCE_NOT_EXECUTION",
        "plan_sha256": str(plan["plan_sha256"]),
        "review_sha256": canonical_hash(review),
        "review_validation_sha256": str(validation["validation_sha256"]),
        "review_complete": True,
        "baseline_ready": True,
        "decision_counts": dict(validation.get("decision_counts") or {}),
        "decisions": decisions,
        "automatic_write_allowed": False,
        "execution_performed": False,
        "v8_homologated": False,
    }
    acceptance["acceptance_sha256"] = canonical_hash(acceptance)
    return acceptance


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Registra aceite imutável do baseline após revisão humana válida, sem executar reconciliação."
    )
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.output.exists():
        print("RECONCILIATION_BASELINE_ACCEPTANCE_ERRO: saída já existe e não será sobrescrita.", file=sys.stderr)
        return 2
    try:
        acceptance = build_acceptance(load_json(args.plan), load_json(args.review))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(acceptance, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (BaselineAcceptanceError, OSError) as exc:
        print(f"RECONCILIATION_BASELINE_ACCEPTANCE_ERRO: {exc}", file=sys.stderr)
        return 2

    print("RECONCILIATION_BASELINE_ACCEPTANCE_OK")
    print(f"Decisões: {len(acceptance['decisions'])}")
    print("Revisão completa: SIM")
    print("Baseline aceito: SIM")
    print("Execução realizada: NÃO")
    print("Escrita automática: NÃO")
    print("V8 homologada: NÃO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
