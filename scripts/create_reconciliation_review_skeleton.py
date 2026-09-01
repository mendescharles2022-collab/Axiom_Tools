from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


class ReconciliationReviewSkeletonError(RuntimeError):
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
        raise ReconciliationReviewSkeletonError(f"JSON inválido {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        raise ReconciliationReviewSkeletonError(f"JSON deve ser objeto: {path.name}")
    return value


def verify_plan(plan: dict) -> None:
    if plan.get("version") != 1:
        raise ReconciliationReviewSkeletonError("Versão do plano não suportada.")
    if plan.get("mode") != "READ_ONLY_RECONCILIATION_PLAN_NOT_EXECUTION":
        raise ReconciliationReviewSkeletonError("Modo do plano inválido.")
    if plan.get("automatic_write_allowed") is not False:
        raise ReconciliationReviewSkeletonError("Plano não comprova escrita automática desativada.")
    if plan.get("v8_homologated") is not False:
        raise ReconciliationReviewSkeletonError("Plano contém homologação indevida.")
    expected = str(plan.get("plan_sha256") or "").upper()
    payload = dict(plan)
    payload.pop("plan_sha256", None)
    if expected != canonical_hash(payload):
        raise ReconciliationReviewSkeletonError("plan_sha256 inválido.")
    entries = plan.get("entries")
    if not isinstance(entries, list):
        raise ReconciliationReviewSkeletonError("Plano sem lista entries.")


def build_skeleton(plan: dict) -> dict:
    verify_plan(plan)
    items: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for entry in plan["entries"]:
        if not isinstance(entry, dict):
            raise ReconciliationReviewSkeletonError("Entrada do plano inválida.")
        if entry.get("review_required") is not True:
            continue
        area = str(entry.get("area") or "").strip()
        path = str(entry.get("relative_path") or "").strip()
        key = (area, path)
        if not area or not path:
            raise ReconciliationReviewSkeletonError("Entrada revisável sem identidade completa.")
        if key in seen:
            raise ReconciliationReviewSkeletonError(f"Entrada revisável duplicada: {area}/{path}")
        seen.add(key)
        items.append({
            "area": area,
            "relative_path": path,
            "status": str(entry.get("status") or ""),
            "proposed_action": str(entry.get("proposed_action") or ""),
            "risk": str(entry.get("risk") or ""),
            "decision": "PENDING",
            "reviewer": "",
            "reason": "",
            "evidence": [],
        })

    items.sort(key=lambda item: (item["area"], item["relative_path"]))
    skeleton = {
        "version": 1,
        "mode": "RECONCILIATION_REVIEW_SKELETON_NOT_EXECUTION",
        "plan_sha256": plan["plan_sha256"],
        "automatic_write_allowed": False,
        "review_complete": False,
        "baseline_ready": False,
        "items": items,
        "v8_homologated": False,
    }
    skeleton["review_skeleton_sha256"] = canonical_hash(skeleton)
    return skeleton


def main() -> int:
    parser = argparse.ArgumentParser(description="Cria esqueleto PENDING para revisão humana do plano de reconciliação.")
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.output.exists():
        print("RECONCILIATION_REVIEW_SKELETON_ERRO: saída já existe e não será sobrescrita.", file=sys.stderr)
        return 2
    try:
        skeleton = build_skeleton(load_json(args.plan))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(skeleton, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (ReconciliationReviewSkeletonError, OSError) as exc:
        print(f"RECONCILIATION_REVIEW_SKELETON_ERRO: {exc}", file=sys.stderr)
        return 2

    print("RECONCILIATION_REVIEW_SKELETON_OK")
    print(f"Itens pendentes: {len(skeleton['items'])}")
    print("Escrita automática: NÃO")
    print("Baseline liberado: NÃO")
    print("V8 homologada: NÃO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
