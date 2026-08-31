from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import stat
import sys
from pathlib import Path, PurePath

import audit_db_filesystem_links as base

SPEC_VERSION = 1
ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")


class ReverseLinkAuditError(RuntimeError):
    pass


def is_reparse_point(path: Path) -> bool:
    if path.is_symlink():
        return True
    try:
        if hasattr(path, "is_junction") and path.is_junction():
            return True
    except OSError:
        return True
    try:
        attrs = path.stat(follow_symlinks=False).st_file_attributes
    except (AttributeError, OSError):
        return False
    return bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400))


def validate_glob(raw: str) -> str:
    pattern = str(raw).strip().replace("\\", "/")
    if not pattern:
        raise ReverseLinkAuditError("glob vazio.")
    pure = PurePath(pattern)
    if pure.is_absolute() or ".." in pure.parts:
        raise ReverseLinkAuditError(f"glob inseguro: {raw!r}")
    if re.match(r"^[A-Za-z]:", pattern) or pattern.startswith("//"):
        raise ReverseLinkAuditError(f"glob absoluto/inseguro: {raw!r}")
    return pattern


def normalize_spec(spec: dict, roots: dict[str, Path]) -> dict:
    if not isinstance(spec, dict) or spec.get("version") != SPEC_VERSION:
        raise ReverseLinkAuditError(
            f"Spec deve ser objeto version={SPEC_VERSION}."
        )
    scans = spec.get("scans")
    if not isinstance(scans, list) or not scans:
        raise ReverseLinkAuditError("Spec deve conter scans.")

    seen: set[str] = set()
    normalized = []
    for idx, item in enumerate(scans, start=1):
        if not isinstance(item, dict):
            raise ReverseLinkAuditError(f"Scan #{idx} inválido.")
        ident = str(item.get("id", "")).strip()
        if not ID_RE.fullmatch(ident):
            raise ReverseLinkAuditError(f"ID inválido no scan #{idx}: {ident!r}")
        if ident in seen:
            raise ReverseLinkAuditError(f"ID duplicado: {ident}")
        seen.add(ident)

        root_key = str(item.get("root", "")).strip()
        if root_key not in roots:
            raise ReverseLinkAuditError(
                f"Raiz {root_key!r} não fornecida para {ident}."
            )
        sql = str(item.get("sql", "")).strip()
        path_column = str(item.get("path_column", "path")).strip()
        if not sql or not path_column:
            raise ReverseLinkAuditError(
                f"SQL/path_column ausente em {ident}."
            )

        normalized.append(
            {
                "id": ident,
                "root": root_key,
                "glob": validate_glob(item.get("glob", "**/*")),
                "sql": sql,
                "path_column": path_column,
                "allow_absolute": bool(item.get("allow_absolute", False)),
                "include_sha256": bool(item.get("include_sha256", False)),
            }
        )
    return {"version": SPEC_VERSION, "scans": normalized}


def relative_db_path(root: Path, raw: object, allow_absolute: bool) -> str:
    try:
        target = base.safe_target(root, str(raw), allow_absolute)
    except base.LinkAuditError as exc:
        raise ReverseLinkAuditError(str(exc)) from exc
    return target.relative_to(root.resolve()).as_posix()


def collect_indexed_paths(
    conn: sqlite3.Connection,
    scan: dict,
    root: Path,
) -> tuple[set[str], list[dict], int]:
    cursor = conn.execute(scan["sql"])
    if cursor.description is None:
        raise ReverseLinkAuditError(
            f"{scan['id']}: consulta sem conjunto de resultados."
        )
    columns = {item[0] for item in cursor.description}
    if scan["path_column"] not in columns:
        raise ReverseLinkAuditError(
            f"{scan['id']}: coluna {scan['path_column']!r} ausente."
        )

    indexed: set[str] = set()
    findings: list[dict] = []
    rows = 0
    for row in cursor:
        rows += 1
        raw = row[scan["path_column"]]
        try:
            rel = relative_db_path(root, raw, scan["allow_absolute"])
        except ReverseLinkAuditError as exc:
            findings.append(
                {
                    "path": str(raw),
                    "code": "UNSAFE_DB_PATH",
                    "detail": str(exc),
                }
            )
            continue
        indexed.add(rel)
    return indexed, findings, rows


def scan_filesystem(root: Path, pattern: str) -> tuple[list[Path], list[dict]]:
    files: list[Path] = []
    findings: list[dict] = []
    root_resolved = root.resolve()
    for candidate in root.glob(pattern):
        try:
            candidate_resolved = candidate.resolve()
            candidate_resolved.relative_to(root_resolved)
        except (OSError, ValueError):
            findings.append(
                {
                    "path": candidate.name,
                    "code": "UNSAFE_FILESYSTEM_ENTRY",
                    "detail": "Entrada resolve para fora da raiz autorizada.",
                }
            )
            continue
        if is_reparse_point(candidate):
            findings.append(
                {
                    "path": candidate.relative_to(root).as_posix(),
                    "code": "REPARSE_POINT",
                    "detail": "Junction/symlink/reparse point não é auditado como arquivo gerenciado.",
                }
            )
            continue
        if candidate.is_file():
            files.append(candidate)
    return files, findings


def audit_reverse_links(
    db_path: Path,
    spec: dict,
    roots: dict[str, Path],
) -> dict:
    normalized = normalize_spec(spec, roots)
    conn = base.connect_ro(db_path)
    conn.set_authorizer(base._authorizer)
    results = []
    try:
        for scan in normalized["scans"]:
            findings: list[dict] = []
            error = None
            indexed_rows = 0
            indexed_unique = 0
            physical_files = 0
            try:
                root = roots[scan["root"]]
                indexed, db_findings, indexed_rows = collect_indexed_paths(
                    conn, scan, root
                )
                indexed_unique = len(indexed)
                findings.extend(db_findings)

                files, fs_findings = scan_filesystem(root, scan["glob"])
                findings.extend(fs_findings)
                physical_files = len(files)
                for path in files:
                    rel = path.relative_to(root).as_posix()
                    if rel in indexed:
                        continue
                    finding = {
                        "path": rel,
                        "code": "UNINDEXED_FILE",
                        "detail": "Arquivo físico existe na raiz gerenciada, mas não foi retornado pelo índice SQL configurado.",
                        "size": path.stat().st_size,
                    }
                    if scan["include_sha256"]:
                        finding["sha256"] = base.sha256_file(path)
                    findings.append(finding)
            except (
                sqlite3.Error,
                base.LinkAuditError,
                ReverseLinkAuditError,
                OSError,
                ValueError,
                TypeError,
            ) as exc:
                error = str(exc)

            results.append(
                {
                    "id": scan["id"],
                    "root": scan["root"],
                    "glob": scan["glob"],
                    "indexed_rows": indexed_rows,
                    "indexed_unique_paths": indexed_unique,
                    "physical_files": physical_files,
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
            "scans": len(results),
            "query_errors": query_errors,
            "findings": findings,
        },
        "ok": query_errors == 0 and findings == 0,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audita filesystem → banco do Axiom Tools em modo somente leitura, "
            "identificando arquivos físicos não indexados."
        )
    )
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--root-map", action="append", default=[])
    parser.add_argument(
        "--output", type=Path, default=Path("FILESYSTEM_DB_INDEX_AUDIT.json")
    )
    args = parser.parse_args()

    try:
        roots = base.parse_root_map(args.root_map)
        spec = json.loads(args.spec.read_text(encoding="utf-8"))
        report = audit_reverse_links(args.db, spec, roots)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
    except (
        ReverseLinkAuditError,
        base.LinkAuditError,
        OSError,
        UnicodeDecodeError,
        json.JSONDecodeError,
    ) as exc:
        print(f"FILESYSTEM_DB_INDEX_AUDIT_ERRO: {exc}", file=sys.stderr)
        return 2

    print(
        "FILESYSTEM_DB_INDEX_AUDIT_OK"
        if report["ok"]
        else "FILESYSTEM_DB_INDEX_AUDIT_FALHA"
    )
    print(f"Scans: {report['summary']['scans']}")
    print(f"Erros: {report['summary']['query_errors']}")
    print(f"Achados: {report['summary']['findings']}")
    print(f"Relatório: {args.output.resolve()}")
    return 0 if report["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
