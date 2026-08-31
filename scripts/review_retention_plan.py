from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

VERSION = 1
ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
SHA_RE = re.compile(r"^[0-9A-Fa-f]{64}$")

SAFE_CATEGORIES = {
    "TEMPORARIO_PROCESSAMENTO",
    "CACHE_RECONSTRUIVEL",
    "UPLOAD_TRANSITORIO",
}
PROTECTED_CATEGORIES = {
    "ORIGINAL_DOCUMENTAL",
    "ARQUIVO_GERENCIADO",
    "VERSAO_HISTORICA",
    "SAIDA_FINAL",
    "BACKUP",
}
KNOWN_CATEGORIES = SAFE_CATEGORIES | PROTECTED_CATEGORIES | {
    "LOG",
    "OUTRO_REVISAR",
}
DECISIONS = {"ELIGIBLE", "KEEP", "BLOCK"}


class RetentionReviewError(RuntimeError):
    pass


def canonical_hash(obj: object) -> str:
    payload = json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RetentionReviewError(f"JSON inválido {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RetentionReviewError(f"JSON deve ser objeto: {path}")
    return payload


def candidate_keys(plan: dict) -> dict[tuple[str, str], dict]:
    if plan.get("mode") != "DRY_RUN_ONLY":
        raise RetentionReviewError("Plano deve ter mode=DRY_RUN_ONLY.")
    rules = plan.get("rules")
    if not isinstance(rules, list):
        raise RetentionReviewError("Plano sem lista rules.")

    result: dict[tuple[str, str], dict] = {}
    for rule in rules:
        if not isinstance(rule, dict):
            raise RetentionReviewError("Regra inválida no plano.")
        rule_id = str(rule.get("id", "")).strip()
        root_key = str(rule.get("root", "")).strip()
        if not ID_RE.fullmatch(rule_id):
            raise RetentionReviewError(f"ID de regra inválido: {rule_id!r}")
        if not ID_RE.fullmatch(root_key):
            raise RetentionReviewError(
                f"Raiz lógica inválida em {rule_id}: {root_key!r}"
            )
        items = rule.get("items")
        if not isinstance(items, list):
            raise RetentionReviewError(f"Items inválidos em {rule_id}.")
        for item in items:
            if not isinstance(item, dict):
                raise RetentionReviewError(f"Item inválido em {rule_id}.")
            if item.get("status") != "CANDIDATE":
                continue
            rel = str(item.get("path", "")).strip().replace("\\", "/")
            if not rel or rel.startswith("/") or ".." in Path(rel).parts:
                raise RetentionReviewError(
                    f"Path candidato inválido em {rule_id}: {rel!r}"
                )
            key = (rule_id, rel)
            if key in result:
                raise RetentionReviewError(
                    f"Candidato duplicado no plano: {rule_id}/{rel}"
                )
            result[key] = {
                "root": root_key,
                "item": item,
            }
    return result


def review_plan(plan: dict, decisions_doc: dict) -> dict:
    if decisions_doc.get("version") != VERSION:
        raise RetentionReviewError(f"Decisões devem ter version={VERSION}.")

    expected_hash = canonical_hash(plan)
    supplied_hash = str(decisions_doc.get("plan_sha256", "")).strip().upper()
    if not SHA_RE.fullmatch(supplied_hash) or supplied_hash != expected_hash:
        raise RetentionReviewError(
            "plan_sha256 não corresponde ao dry-run revisado."
        )

    candidates = candidate_keys(plan)
    raw_decisions = decisions_doc.get("decisions")
    if not isinstance(raw_decisions, list):
        raise RetentionReviewError("decisions deve ser lista.")

    reviewed: dict[tuple[str, str], dict] = {}
    for raw in raw_decisions:
        if not isinstance(raw, dict):
            raise RetentionReviewError("Decisão inválida.")
        rule_id = str(raw.get("rule_id", "")).strip()
        rel = str(raw.get("path", "")).strip().replace("\\", "/")
        key = (rule_id, rel)
        if key not in candidates:
            raise RetentionReviewError(
                f"Decisão aponta para candidato inexistente: {rule_id}/{rel}"
            )
        if key in reviewed:
            raise RetentionReviewError(
                f"Decisão duplicada: {rule_id}/{rel}"
            )

        category = str(raw.get("category", "")).strip().upper()
        decision = str(raw.get("decision", "")).strip().upper()
        reason = str(raw.get("reason", "")).strip()
        evidence = raw.get("evidence", [])

        if category not in KNOWN_CATEGORIES:
            raise RetentionReviewError(
                f"Categoria inválida em {rule_id}/{rel}: {category!r}"
            )
        if decision not in DECISIONS:
            raise RetentionReviewError(
                f"Decisão inválida em {rule_id}/{rel}: {decision!r}"
            )
        if not reason:
            raise RetentionReviewError(
                f"Motivo obrigatório em {rule_id}/{rel}."
            )
        if not isinstance(evidence, list) or not all(
            isinstance(value, str) and value.strip() for value in evidence
        ):
            raise RetentionReviewError(
                f"Evidence inválida em {rule_id}/{rel}."
            )

        if category in PROTECTED_CATEGORIES and decision == "ELIGIBLE":
            raise RetentionReviewError(
                f"Categoria protegida não pode ser ELIGIBLE: {rule_id}/{rel}"
            )
        if decision == "ELIGIBLE":
            if category not in SAFE_CATEGORIES:
                raise RetentionReviewError(
                    f"ELIGIBLE exige categoria reconstruível/transitória: {rule_id}/{rel}"
                )
            if not evidence:
                raise RetentionReviewError(
                    f"ELIGIBLE exige evidência: {rule_id}/{rel}"
                )

        candidate = candidates[key]
        item = candidate["item"]
        reviewed[key] = {
            "rule_id": rule_id,
            "root": candidate["root"],
            "path": rel,
            "category": category,
            "decision": decision,
            "reason": reason,
            "evidence": evidence,
            "size": int(item.get("size") or 0),
            "age_days": item.get("age_days"),
        }

    missing = [
        f"{rule_id}/{rel}"
        for rule_id, rel in sorted(candidates)
        if (rule_id, rel) not in reviewed
    ]
    if missing:
        raise RetentionReviewError(
            "Candidatos sem decisão: " + ", ".join(missing)
        )

    ordered = [reviewed[key] for key in sorted(reviewed)]
    eligible = [item for item in ordered if item["decision"] == "ELIGIBLE"]
    keep = [item for item in ordered if item["decision"] == "KEEP"]
    blocked = [item for item in ordered if item["decision"] == "BLOCK"]

    reviewed_payload = {
        "version": VERSION,
        "mode": "REVIEWED_NOT_AUTHORIZED",
        "source_plan_sha256": expected_hash,
        "summary": {
            "candidates": len(ordered),
            "eligible": len(eligible),
            "keep": len(keep),
            "blocked": len(blocked),
            "eligible_bytes": sum(item["size"] for item in eligible),
        },
        "items": ordered,
        "execution_authorized": False,
        "warning": (
            "Revisão concluída, mas nenhuma exclusão foi autorizada. "
            "Confirmação explícita e revalidação do filesystem ainda são obrigatórias."
        ),
    }
    reviewed_payload["review_sha256"] = canonical_hash(reviewed_payload)
    return reviewed_payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Revisa um dry-run de retenção do Axiom Tools sem apagar ou mover arquivos."
        )
    )
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--decisions", required=True, type=Path)
    parser.add_argument(
        "--output", type=Path, default=Path("RETENTION_REVIEW.json")
    )
    args = parser.parse_args()

    try:
        report = review_plan(load_json(args.plan), load_json(args.decisions))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except RetentionReviewError as exc:
        print(f"RETENTION_REVIEW_ERRO: {exc}", file=sys.stderr)
        return 2

    print("RETENTION_REVIEW_OK")
    print(f"Candidatos: {report['summary']['candidates']}")
    print(f"Elegíveis para etapa de confirmação: {report['summary']['eligible']}")
    print("Execução autorizada: NÃO")
    print(f"Review SHA256: {report['review_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
