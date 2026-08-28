from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote

SPEC_VERSION = 1
ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")
SEVERITIES = {"error", "warning"}


class InvariantError(RuntimeError):
    pass


def _connect_read_only(db_path: Path) -> sqlite3.Connection:
    path = db_path.resolve()
    if not path.is_file():
        raise InvariantError(f"Banco inexistente: {path}")
    uri = "file:" + quote(path.as_posix(), safe="/:") + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only = ON")
    return conn


def normalize_spec(spec: dict) -> dict:
    if not isinstance(spec, dict):
        raise InvariantError("Especificação deve ser um objeto JSON.")
    version = spec.get("version")
    if version != SPEC_VERSION:
        raise InvariantError(
            f"Versão de especificação não suportada: {version!r}. Esperada: {SPEC_VERSION}."
        )
    raw = spec.get("invariants")
    if not isinstance(raw, list) or not raw:
        raise InvariantError("Especificação deve conter lista não vazia 'invariants'.")

    seen: set[str] = set()
    items: list[dict] = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise InvariantError(f"Invariante #{index} deve ser objeto.")
        ident = str(item.get("id", "")).strip()
        if not ident or not ID_RE.fullmatch(ident):
            raise InvariantError(f"ID inválido no invariante #{index}: {ident!r}")
        if ident in seen:
            raise InvariantError(f"ID duplicado: {ident}")
        seen.add(ident)

        sql = str(item.get("sql", "")).strip()
        if not sql:
            raise InvariantError(f"SQL ausente no invariante {ident}.")
        severity = str(item.get("severity", "error")).strip().lower()
        if severity not in SEVERITIES:
            raise InvariantError(f"Severity inválida em {ident}: {severity!r}")
        description = str(item.get("description", "")).strip()
        max_rows = item.get("max_rows", 50)
        if not isinstance(max_rows, int) or not (1 <= max_rows <= 1000):
            raise InvariantError(
                f"max_rows inválido em {ident}; use inteiro entre 1 e 1000."
            )
        items.append(
            {
                "id": ident,
                "description": description,
                "severity": severity,
                "sql": sql,
                "max_rows": max_rows,
            }
        )
    return {"version": SPEC_VERSION, "invariants": items}


def load_spec(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InvariantError(f"Especificação inexistente: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvariantError(f"Especificação inválida: {exc}") from exc
    return normalize_spec(data)


def _authorizer(action, arg1, arg2, dbname, source):
    denied = {
        sqlite3.SQLITE_INSERT,
        sqlite3.SQLITE_UPDATE,
        sqlite3.SQLITE_DELETE,
        sqlite3.SQLITE_CREATE_INDEX,
        sqlite3.SQLITE_CREATE_TABLE,
        sqlite3.SQLITE_CREATE_TEMP_INDEX,
        sqlite3.SQLITE_CREATE_TEMP_TABLE,
        sqlite3.SQLITE_CREATE_TEMP_TRIGGER,
        sqlite3.SQLITE_CREATE_TEMP_VIEW,
        sqlite3.SQLITE_CREATE_TRIGGER,
        sqlite3.SQLITE_CREATE_VIEW,
        sqlite3.SQLITE_DROP_INDEX,
        sqlite3.SQLITE_DROP_TABLE,
        sqlite3.SQLITE_DROP_TEMP_INDEX,
        sqlite3.SQLITE_DROP_TEMP_TABLE,
        sqlite3.SQLITE_DROP_TEMP_TRIGGER,
        sqlite3.SQLITE_DROP_TEMP_VIEW,
        sqlite3.SQLITE_DROP_TRIGGER,
        sqlite3.SQLITE_DROP_VIEW,
        sqlite3.SQLITE_ALTER_TABLE,
        sqlite3.SQLITE_REINDEX,
        sqlite3.SQLITE_ANALYZE,
        sqlite3.SQLITE_ATTACH,
        sqlite3.SQLITE_DETACH,
    }
    if action in denied:
        return sqlite3.SQLITE_DENY
    if action == sqlite3.SQLITE_PRAGMA:
        return sqlite3.SQLITE_DENY
    return sqlite3.SQLITE_OK


def run_invariants(db_path: Path, spec: dict) -> dict:
    normalized = normalize_spec(spec)
    results: list[dict] = []
    conn = _connect_read_only(db_path)
    try:
        conn.set_authorizer(_authorizer)
        for item in normalized["invariants"]:
            ident = item["id"]
            try:
                cursor = conn.execute(item["sql"])
                if cursor.description is None:
                    raise InvariantError(
                        f"{ident}: SQL não produziu conjunto de resultados."
                    )
                columns = [col[0] for col in cursor.description]
                rows = []
                truncated = False
                for idx, row in enumerate(cursor):
                    if idx >= item["max_rows"]:
                        truncated = True
                        break
                    rows.append(
                        {columns[i]: row[i] for i in range(len(columns))}
                    )
                passed = len(rows) == 0 and not truncated
                results.append(
                    {
                        "id": ident,
                        "description": item["description"],
                        "severity": item["severity"],
                        "passed": passed,
                        "violation_count_sample": len(rows),
                        "truncated": truncated,
                        "sample": rows,
                        "error": None,
                    }
                )
            except sqlite3.Error as exc:
                results.append(
                    {
                        "id": ident,
                        "description": item["description"],
                        "severity": item["severity"],
                        "passed": False,
                        "violation_count_sample": 0,
                        "truncated": False,
                        "sample": [],
                        "error": str(exc),
                    }
                )
    finally:
        conn.close()

    errors_failed = sum(
        1
        for result in results
        if not result["passed"] and result["severity"] == "error"
    )
    warnings_failed = sum(
        1
        for result in results
        if not result["passed"] and result["severity"] == "warning"
    )
    return {
        "spec_version": SPEC_VERSION,
        "database_name": db_path.name,
        "summary": {
            "total": len(results),
            "passed": sum(1 for result in results if result["passed"]),
            "errors_failed": errors_failed,
            "warnings_failed": warnings_failed,
        },
        "ok": errors_failed == 0,
        "results": results,
    }


def write_report(report: dict, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Executa invariantes lógicas SQLite somente leitura. "
            "Cada consulta deve retornar zero linhas quando válida."
        )
    )
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument(
        "--output", type=Path, default=Path("SQLITE_INVARIANTS_REPORT.json")
    )
    args = parser.parse_args()

    try:
        spec = load_spec(args.spec)
        report = run_invariants(args.db, spec)
        write_report(report, args.output)
    except InvariantError as exc:
        print(f"SQLITE_INVARIANTS_ERRO: {exc}", file=sys.stderr)
        return 2

    print("SQLITE_INVARIANTS_OK" if report["ok"] else "SQLITE_INVARIANTS_FALHA")
    print(f"Total: {report['summary']['total']}")
    print(f"Aprovadas: {report['summary']['passed']}")
    print(f"Erros: {report['summary']['errors_failed']}")
    print(f"Avisos: {report['summary']['warnings_failed']}")
    print(f"Relatório: {args.output.resolve()}")
    return 0 if report["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
