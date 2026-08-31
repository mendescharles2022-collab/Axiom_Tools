from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import review_retention_plan as review

VERSION = 1
CONFIRMATION_PHRASE = "AUTORIZAR_MANIFESTO_SEM_EXECUTAR"
REFERENCE_RE = re.compile(r"^[A-Za-z0-9._:/# -]{3,120}$")


class RetentionAuthorizationError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RetentionAuthorizationError(f"JSON inválido {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RetentionAuthorizationError(f"JSON deve ser objeto: {path}")
    return payload


def computed_review_hash(review_doc: dict) -> str:
    if review_doc.get("mode") != "REVIEWED_NOT_AUTHORIZED":
        raise RetentionAuthorizationError(
            "Review deve ter mode=REVIEWED_NOT_AUTHORIZED."
        )
    stored = str(review_doc.get("review_sha256", "")).strip().upper()
    payload = dict(review_doc)
    payload.pop("review_sha256", None)
    calculated = review.canonical_hash(payload)
    if stored != calculated:
        raise RetentionAuthorizationError(
            "review_sha256 interno não corresponde ao conteúdo revisado."
        )
    return calculated


def validate_reference(reference: str) -> None:
    if not REFERENCE_RE.fullmatch(reference):
        raise RetentionAuthorizationError("reference inválida.")
    normalized = reference.replace("\\", "/")
    if (
        normalized.startswith("/")
        or normalized.endswith("/")
        or ".." in normalized.split("/")
        or "//" in normalized
    ):
        raise RetentionAuthorizationError("reference inválida/insegura.")


def authorize_manifest(review_doc: dict, confirmation: dict) -> dict:
    if confirmation.get("version") != VERSION:
        raise RetentionAuthorizationError(
            f"Confirmação deve ter version={VERSION}."
        )

    review_hash = computed_review_hash(review_doc)
    supplied_hash = str(confirmation.get("review_sha256", "")).strip().upper()
    if supplied_hash != review_hash:
        raise RetentionAuthorizationError(
            "review_sha256 da confirmação não corresponde à revisão."
        )

    phrase = str(confirmation.get("confirmation", "")).strip()
    if phrase != CONFIRMATION_PHRASE:
        raise RetentionAuthorizationError(
            "Frase de confirmação inválida."
        )

    approver = str(confirmation.get("approver", "")).strip()
    reference = str(confirmation.get("reference", "")).strip()
    if len(approver) < 2 or len(approver) > 120:
        raise RetentionAuthorizationError("approver inválido.")
    validate_reference(reference)

    items = review_doc.get("items")
    if not isinstance(items, list):
        raise RetentionAuthorizationError("Review sem lista items.")

    eligible = []
    for item in items:
        if not isinstance(item, dict):
            raise RetentionAuthorizationError("Item inválido na revisão.")
        if item.get("decision") != "ELIGIBLE":
            continue
        category = str(item.get("category", "")).strip().upper()
        if category not in review.SAFE_CATEGORIES:
            raise RetentionAuthorizationError(
                f"Item elegível com categoria não permitida: {item.get('path')!r}"
            )
        evidence = item.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            raise RetentionAuthorizationError(
                f"Item elegível sem evidência: {item.get('path')!r}"
            )
        rule_id = str(item.get("rule_id", "")).strip()
        path = str(item.get("path", "")).strip().replace("\\", "/")
        if not rule_id or not path or path.startswith("/") or ".." in Path(path).parts:
            raise RetentionAuthorizationError(
                f"Item elegível com identificação/caminho inseguro: {path!r}"
            )
        eligible.append(
            {
                "rule_id": rule_id,
                "path": path,
                "category": category,
                "size": int(item.get("size") or 0),
                "age_days": item.get("age_days"),
                "reason": str(item.get("reason", "")),
                "evidence": list(evidence),
            }
        )

    manifest = {
        "version": VERSION,
        "mode": "AUTHORIZED_MANIFEST_NOT_EXECUTED",
        "source_review_sha256": review_hash,
        "authorization": {
            "approver": approver,
            "reference": reference,
            "confirmation": CONFIRMATION_PHRASE,
        },
        "summary": {
            "authorized_items": len(eligible),
            "authorized_bytes": sum(item["size"] for item in eligible),
        },
        "items": eligible,
        "execution_performed": False,
        "warning": (
            "Este manifesto registra autorização documental, mas NÃO executa "
            "exclusão, movimentação ou alteração de arquivos. Antes de qualquer "
            "execução futura, o filesystem deverá ser revalidado contra este manifesto."
        ),
    }
    manifest["manifest_sha256"] = review.canonical_hash(manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Gera manifesto autorizado de retenção sem executar exclusão ou movimentação."
        )
    )
    parser.add_argument("--review", required=True, type=Path)
    parser.add_argument("--confirmation", required=True, type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("RETENTION_AUTHORIZED_MANIFEST.json"),
    )
    args = parser.parse_args()

    try:
        manifest = authorize_manifest(
            load_json(args.review),
            load_json(args.confirmation),
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except RetentionAuthorizationError as exc:
        print(f"RETENTION_AUTHORIZATION_ERRO: {exc}", file=sys.stderr)
        return 2

    print("RETENTION_AUTHORIZATION_OK")
    print(f"Itens autorizados: {manifest['summary']['authorized_items']}")
    print(f"Bytes autorizados: {manifest['summary']['authorized_bytes']}")
    print("Execução realizada: NÃO")
    print(f"Manifest SHA256: {manifest['manifest_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
