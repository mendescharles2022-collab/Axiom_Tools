from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote

SPEC_VERSION = 1
ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
SHA_RE = re.compile(r"^[0-9A-Fa-f]{64}$")


class LinkAuditError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def connect_ro(db: Path) -> sqlite3.Connection:
    path = db.resolve()
    if not path.is_file():
        raise LinkAuditError(f"Banco inexistente: {path}")
    uri = "file:" + quote(path.as_posix(), safe="/:") + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def _authorizer(action, arg1, arg2, dbname, source):
    denied = {
        sqlite3.SQLITE_INSERT,
        sqlite3.SQLITE_UPDATE,
        sqlite3.SQLITE_DELETE,
        sqlite3.SQLITE_CREATE_INDEX,
        sqlite3.SQLITE_CREATE_TABLE,
        sqlite3.SQLITE_CREATE_TRIGGER,
        sqlite3.SQLITE_CREATE_VIEW,
        sqlite3.SQLITE_DROP_INDEX,
        sqlite3.SQLITE_DROP_TABLE,
        sqlite3.SQLITE_DROP_TRIGGER,
        sqlite3.SQLITE_DROP_VIEW,
        sqlite3.SQLITE_ALTER_TABLE,
        sqlite3.SQLITE_ATTACH,
        sqlite3.SQLITE_DETACH,
        sqlite3.SQLITE_REINDEX,
        sqlite3.SQLITE_ANALYZE,
    }
    if action in denied or action == sqlite3.SQLITE_PRAGMA:
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def parse_root_map(values: list[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for raw in values:
        if "=" not in raw:
            raise LinkAuditError(f"root-map inválido: {raw!r}")
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not ID_RE.fullmatch(key) or not value:
            raise LinkAuditError(f"root-map inválido: {raw!r}")
        if key in result:
            raise LinkAuditError(f"root-map duplicado: {key}")
        root = Path(value).resolve()
        if not root.is_dir():
            raise LinkAuditError(f"Raiz inexistente para {key}: {root}")
        result[key] = root
    if not result:
        raise LinkAuditError("Ao menos um --root-map é obrigatório.")
    return result


def normalize_spec(spec: dict, roots: dict[str, Path]) -> dict:
    if not isinstance(spec, dict) or spec.get("version") != SPEC_VERSION:
        raise LinkAuditError(f"Spec deve ser objeto version={SPEC_VERSION}.")
    checks = spec.get("checks")
    if not isinstance(checks, list) or not checks:
        raise LinkAuditError("Spec deve conter checks.")

    seen = set()
    normalized = []
    for idx, item in enumerate(checks, start=1):
        if not isinstance(item, dict):
            raise LinkAuditError(f"Check #{idx} inválido.")
        ident = str(item.get("id", "")).strip()
        if not ID_RE.fullmatch(ident):
            raise LinkAuditError(f"ID inválido no check #{idx}: {ident!r}")
        if ident in seen:
            raise LinkAuditError(f"ID duplicado: {ident}")
        seen.add(ident)
        sql = str(item.get("sql", "")).strip()
        path_column = str(item.get("path_column", "path")).strip()
        root_key = str(item.get("root", "")).strip()
        if not sql or not path_column:
            raise LinkAuditError(f"SQL/path_column ausente em {ident}.")
        if root_key not in roots:
            raise LinkAuditError(
                f"Raiz {root_key!r} não fornecida para {ident}."
            )
        normalized.append(
            {
                "id": ident,
                "sql": sql,
                "path_column": path_column,
                "root": root_key,
                "id_column": str(item.get("id_column", "id")).strip() or "id",
                "size_column": str(item.get("size_column", "")).strip() or None,
                "sha256_column": str(item.get("sha256_column", "")).strip() or None,
                "required": bool(item.get("required", True)),
                "allow_absolute": bool(item.get("allow_absolute", False)),
            }
        )
    return {"version": SPEC_VERSION, "checks": normalized}


def safe_target(root: Path, raw: str, allow_absolute: bool) -> Path:
    text = str(raw).strip()
    if not text:
        raise LinkAuditError("Caminho vazio.")
    path = Path(text)
    if path.is_absolute():
        if not allow_absolute:
            raise LinkAuditError(f"Caminho absoluto não permitido: {text}")
        target = path.resolve()
    else:
        target = (root / path).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise LinkAuditError(f"Caminho fora da raiz: {text}") from exc
    return target


def audit_links(
    db_path: Path,
    spec: dict,
    roots: dict[str, Path],
) -> dict:
    normalized = normalize_spec(spec, roots)
    conn = connect_ro(db_path)
    conn.set_authorizer(_authorizer)
    results = []
    try:
        for check in normalized["checks"]:
            findings = []
            error = None
            scanned = 0
            try:
                cursor = conn.execute(check["sql"])
                if cursor.description is None:
                    raise LinkAuditError(
                        f"{check['id']}: consulta sem resultados."
                    )
                columns = {item[0] for item in cursor.description}
                required_columns = {
                    check["path_column"],
                    check["id_column"],
                }
                if not required_columns.issubset(columns):
                    raise LinkAuditError(
                        f"{check['id']}: colunas obrigatórias ausentes: "
                        f"{sorted(required_columns - columns)}"
                    )

                for row in cursor:
                    scanned += 1
                    record_id = row[check["id_column"]]
                    raw = row[check["path_column"]]
                    try:
                        target = safe_target(
                            roots[check["root"]],
                            raw,
                            check["allow_absolute"],
                        )
                    except LinkAuditError as exc:
                        findings.append(
                            {
                                "id": record_id,
                                "path": str(raw),
                                "code": "UNSAFE_PATH",
                                "detail": str(exc),
                            }
                        )
                        continue

                    if target.is_symlink():
                        findings.append(
                            {
                                "id": record_id,
                                "path": str(raw),
                                "code": "SYMLINK",
                                "detail": "Link simbólico/reparse não aceito.",
                            }
                        )
                        continue
                    if not target.exists():
                        if check["required"]:
                            findings.append(
                                {
                                    "id": record_id,
                                    "path": str(raw),
                                    "code": "MISSING",
                                    "detail": "Arquivo obrigatório ausente.",
                                }
                            )
                        continue
                    if not target.is_file():
                        findings.append(
                            {
                                "id": record_id,
                                "path": str(raw),
                                "code": "NOT_FILE",
                                "detail": "Destino existe, mas não é arquivo.",
                            }
                        )
                        continue

                    if check["size_column"]:
                        expected_size = row[check["size_column"]]
                        if (
                            expected_size is not None
                            and target.stat().st_size != int(expected_size)
                        ):
                            findings.append(
                                {
                                    "id": record_id,
                                    "path": str(raw),
                                    "code": "SIZE_MISMATCH",
                                    "detail": (
                                        f"esperado={expected_size} "
                                        f"atual={target.stat().st_size}"
                                    ),
                                }
                            )

                    if check["sha256_column"]:
                        expected_sha = str(
                            row[check["sha256_column"]] or ""
                        ).upper()
                        if expected_sha:
                            if not SHA_RE.fullmatch(expected_sha):
                                findings.append(
                                    {
                                        "id": record_id,
                                        "path": str(raw),
                                        "code": "INVALID_EXPECTED_SHA256",
                                        "detail": expected_sha,
                                    }
                                )
                            else:
                                actual_sha = sha256_file(target)
                                if actual_sha != expected_sha:
                                    findings.append(
                                        {
                                            "id": record_id,
                                            "path": str(raw),
                                            "code": "SHA256_MISMATCH",
                                            "detail": (
                                                f"esperado={expected_sha} "
                                                f"atual={actual_sha}"
                                            ),
                                        }
                                    )
            except (
                sqlite3.Error,
                LinkAuditError,
                ValueError,
                TypeError,
            ) as exc:
                error = str(exc)

            results.append(
                {
                    "id": check["id"],
                    "scanned": scanned,
                    "finding_count": len(findings),
                    "findings": findings,
                    "error": error,
                }
            )
    finally:
        conn.close()

    query_errors = sum(1 for item in results if item["error"])
    findings = sum(item["finding_count"] for item in results)
    return {
        "database_name": db_path.name,
        "summary": {
            "checks": len(results),
            "query_errors": query_errors,
            "findings": findings,
        },
        "ok": query_errors == 0 and findings == 0,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audita vínculos banco ↔ filesystem do Axiom Tools sem escrever no banco."
        )
    )
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--root-map", action="append", default=[])
    parser.add_argument(
        "--output", type=Path, default=Path("DB_FILESYSTEM_AUDIT.json")
    )
    args = parser.parse_args()

    try:
        roots = parse_root_map(args.root_map)
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        report = audit_links(args.db, spec, roots)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
    except (
        LinkAuditError,
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        print(f"DB_FILESYSTEM_AUDIT_ERRO: {exc}", file=sys.stderr)
        return 2

    print("DB_FILESYSTEM_AUDIT_OK" if report["ok"] else "DB_FILESYSTEM_AUDIT_FALHA")
    print(f"Checks: {report['summary']['checks']}")
    print(f"Erros: {report['summary']['query_errors']}")
    print(f"Achados: {report['summary']['findings']}")
    print(f"Relatório: {args.output.resolve()}")
    return 0 if report["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
