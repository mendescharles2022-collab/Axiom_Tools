from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import audit_filesystem_db_index as fs_safety
import authorize_retention_manifest as authorization
import plan_retention_cleanup as planner
import review_retention_plan as review


class RetentionRevalidationError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RetentionRevalidationError(f"JSON inválido {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RetentionRevalidationError(f"JSON deve ser objeto: {path}")
    return payload


def verify_manifest(manifest: dict) -> str:
    if manifest.get("mode") != "AUTHORIZED_MANIFEST_NOT_EXECUTED":
        raise RetentionRevalidationError(
            "Manifesto deve ter mode=AUTHORIZED_MANIFEST_NOT_EXECUTED."
        )
    if manifest.get("execution_performed") is not False:
        raise RetentionRevalidationError(
            "Manifesto indica execução ou estado ambíguo."
        )
    stored = str(manifest.get("manifest_sha256", "")).strip().upper()
    payload = dict(manifest)
    payload.pop("manifest_sha256", None)
    calculated = review.canonical_hash(payload)
    if stored != calculated:
        raise RetentionRevalidationError(
            "manifest_sha256 não corresponde ao conteúdo autorizado."
        )
    auth = manifest.get("authorization")
    if not isinstance(auth, dict):
        raise RetentionRevalidationError("Manifesto sem authorization.")
    if auth.get("confirmation") != authorization.CONFIRMATION_PHRASE:
        raise RetentionRevalidationError(
            "Manifesto sem confirmação canônica."
        )
    return calculated


def safe_target(root: Path, raw_path: str) -> Path:
    text = str(raw_path).strip().replace("\\", "/")
    path = Path(text)
    if not text or path.is_absolute() or ".." in path.parts:
        raise RetentionRevalidationError(f"Caminho relativo inseguro: {text!r}")
    target = (root.resolve() / path).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise RetentionRevalidationError(
            f"Caminho resolve fora da raiz autorizada: {text!r}"
        ) from exc
    return target


def has_reparse_component(root: Path, raw_path: str) -> bool:
    current = root.resolve()
    for part in Path(raw_path).parts:
        current = current / part
        if current.exists() or current.is_symlink():
            if fs_safety.is_reparse_point(current):
                return True
    return False


def revalidate_manifest(
    manifest: dict,
    roots: dict[str, Path],
) -> dict:
    manifest_hash = verify_manifest(manifest)
    items = manifest.get("items")
    if not isinstance(items, list):
        raise RetentionRevalidationError("Manifesto sem lista items.")

    findings = []
    checked = []
    seen: set[tuple[str, str]] = set()
    for item in items:
        if not isinstance(item, dict):
            raise RetentionRevalidationError("Item inválido no manifesto.")
        root_key = str(item.get("root", "")).strip()
        rel = str(item.get("path", "")).strip().replace("\\", "/")
        category = str(item.get("category", "")).strip().upper()
        key = (root_key, rel)
        if key in seen:
            raise RetentionRevalidationError(
                f"Item duplicado no manifesto: {root_key}/{rel}"
            )
        seen.add(key)

        if root_key not in roots:
            raise RetentionRevalidationError(
                f"Raiz autorizada não fornecida: {root_key!r}"
            )
        if category not in review.SAFE_CATEGORIES:
            raise RetentionRevalidationError(
                f"Categoria não executável no manifesto: {category!r}"
            )
        expected_size = item.get("size")
        expected_mtime = item.get("mtime_ns")
        expected_sha = str(item.get("sha256", "")).strip().upper()
        if not isinstance(expected_size, int) or expected_size < 0:
            raise RetentionRevalidationError(
                f"Tamanho esperado inválido: {root_key}/{rel}"
            )
        if not isinstance(expected_mtime, int) or expected_mtime < 0:
            raise RetentionRevalidationError(
                f"mtime_ns esperado inválido: {root_key}/{rel}"
            )
        if not review.SHA_RE.fullmatch(expected_sha):
            raise RetentionRevalidationError(
                f"SHA-256 esperado inválido: {root_key}/{rel}"
            )

        root = roots[root_key].resolve()
        target = safe_target(root, rel)
        item_findings = []
        if has_reparse_component(root, rel):
            item_findings.append("REPARSE_POINT")
        elif not target.exists():
            item_findings.append("MISSING")
        elif not target.is_file():
            item_findings.append("NOT_FILE")
        else:
            stat = target.stat()
            current_sha = planner.sha256_file(target)
            if stat.st_size != expected_size:
                item_findings.append("SIZE_CHANGED")
            if stat.st_mtime_ns != expected_mtime:
                item_findings.append("MTIME_CHANGED")
            if current_sha != expected_sha:
                item_findings.append("SHA256_CHANGED")

            checked.append(
                {
                    "root": root_key,
                    "path": rel,
                    "category": category,
                    "size": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                    "sha256": current_sha,
                    "status": "READY" if not item_findings else "CHANGED",
                }
            )

        for code in item_findings:
            findings.append(
                {
                    "root": root_key,
                    "path": rel,
                    "code": code,
                }
            )
        if item_findings and not any(
            current.get("root") == root_key and current.get("path") == rel
            for current in checked
        ):
            checked.append(
                {
                    "root": root_key,
                    "path": rel,
                    "category": category,
                    "status": "BLOCKED",
                }
            )

    ready = not findings
    return {
        "version": 1,
        "mode": "PREEXECUTION_REVALIDATED_NOT_EXECUTED",
        "source_manifest_sha256": manifest_hash,
        "summary": {
            "authorized_items": len(items),
            "checked_items": len(checked),
            "findings": len(findings),
            "ready": ready,
        },
        "items": checked,
        "findings": findings,
        "execution_performed": False,
        "ready_for_execution": ready,
        "warning": (
            "Revalidação concluída em modo somente leitura. Nenhum arquivo foi "
            "apagado ou movido. Uma futura execução deve consumir exatamente este "
            "estado revalidado e rechecá-lo imediatamente antes da mutação."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Revalida manifesto autorizado de retenção contra o filesystem sem executar exclusão."
        )
    )
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--root-map", action="append", default=[])
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("RETENTION_PREEXECUTION_REVALIDATION.json"),
    )
    args = parser.parse_args()

    try:
        roots = planner.parse_root_map(args.root_map)
        report = revalidate_manifest(load_json(args.manifest), roots)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (
        RetentionRevalidationError,
        planner.RetentionError,
        OSError,
    ) as exc:
        print(f"RETENTION_REVALIDATION_ERRO: {exc}", file=sys.stderr)
        return 2

    print(
        "RETENTION_REVALIDATION_READY"
        if report["ready_for_execution"]
        else "RETENTION_REVALIDATION_BLOCKED"
    )
    print(f"Itens: {report['summary']['authorized_items']}")
    print(f"Achados: {report['summary']['findings']}")
    print("Execução realizada: NÃO")
    return 0 if report["ready_for_execution"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
