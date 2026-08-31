from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from pathlib import Path
from urllib.parse import quote

SPEC_VERSION = 1
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class IdempotencyAuditError(RuntimeError):
    pass


def _identifier(value: object, field: str, *, optional: bool = False) -> str | None:
    text = str(value or "").strip()
    if optional and not text:
        return None
    if not IDENT_RE.fullmatch(text):
        raise IdempotencyAuditError(f"{field} inválido: {text!r}")
    return text


def _ident_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise IdempotencyAuditError(f"{field} deve ser lista não vazia.")
    result = []
    for item in value:
        ident = _identifier(item, field)
        assert ident is not None
        result.append(ident)
    if len(set(result)) != len(result):
        raise IdempotencyAuditError(f"{field} contém coluna duplicada.")
    return result


def _status_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise IdempotencyAuditError(f"{field} deve ser lista não vazia de strings.")
    result = [item.strip() for item in value]
    if len(set(result)) != len(result):
        raise IdempotencyAuditError(f"{field} contém status duplicado.")
    return result


def normalize_spec(spec: dict) -> dict:
    if not isinstance(spec, dict) or spec.get("version") != SPEC_VERSION:
        raise IdempotencyAuditError(f"Spec deve ser objeto version={SPEC_VERSION}.")
    max_attempts = spec.get("max_attempts")
    if not isinstance(max_attempts, int) or max_attempts < 1 or max_attempts > 1000:
        raise IdempotencyAuditError("max_attempts deve ser inteiro entre 1 e 1000.")
    terminal = _status_list(spec.get("terminal_statuses"), "terminal_statuses")
    retryable = _status_list(spec.get("retryable_statuses"), "retryable_statuses")
    overlap = sorted(set(terminal) & set(retryable))
    if overlap:
        raise IdempotencyAuditError(
            "Status não pode ser simultaneamente terminal e retryable: " + ", ".join(overlap)
        )
    return {
        "version": SPEC_VERSION,
        "table": _identifier(spec.get("table"), "table"),
        "id_column": _identifier(spec.get("id_column"), "id_column"),
        "idempotency_columns": _ident_list(
            spec.get("idempotency_columns"), "idempotency_columns"
        ),
        "status_column": _identifier(spec.get("status_column"), "status_column"),
        "attempt_column": _identifier(spec.get("attempt_column"), "attempt_column"),
        "next_retry_column": _identifier(
            spec.get("next_retry_column"), "next_retry_column", optional=True
        ),
        "max_attempts": max_attempts,
        "terminal_statuses": terminal,
        "retryable_statuses": retryable,
        "require_unique_index": spec.get("require_unique_index", True) is True,
        "allow_null_idempotency": spec.get("allow_null_idempotency", False) is True,
    }


def load_spec(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise IdempotencyAuditError(f"Spec inexistente: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IdempotencyAuditError(f"Spec inválida: {exc}") from exc
    return normalize_spec(data)


def _q(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _connect_read_only(database: Path) -> sqlite3.Connection:
    path = database.resolve()
    if not path.is_file():
        raise IdempotencyAuditError(f"Banco inexistente: {path}")
    uri = "file:" + quote(path.as_posix(), safe="/:") + "?mode=ro"
    try:
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA query_only=ON")
        return conn
    except sqlite3.Error as exc:
        raise IdempotencyAuditError(f"Falha ao abrir SQLite read-only: {exc}") from exc


def _table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [str(row[1]) for row in conn.execute(f"PRAGMA table_info({_q(table)})")]


def _unique_indexes(conn: sqlite3.Connection, table: str) -> list[dict]:
    result = []
    for row in conn.execute(f"PRAGMA index_list({_q(table)})"):
        if int(row[2]) != 1:
            continue
        name = str(row[1])
        columns = [
            str(info[2])
            for info in conn.execute(f"PRAGMA index_info({_q(name)})")
            if info[2] is not None
        ]
        result.append({"name": name, "columns": columns})
    return result


def _unique_covers(indexes: list[dict], keys: list[str]) -> bool:
    expected = [item.lower() for item in keys]
    for index in indexes:
        columns = [str(item).lower() for item in index["columns"]]
        if columns == expected:
            return True
    return False


def _rows(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def audit_database(database: Path, spec: dict) -> dict:
    normalized = normalize_spec(spec)
    conn = _connect_read_only(database)
    try:
        table = str(normalized["table"])
        columns = _table_columns(conn, table)
        if not columns:
            raise IdempotencyAuditError(f"Tabela inexistente: {table}")
        required = [
            str(normalized["id_column"]),
            *normalized["idempotency_columns"],
            str(normalized["status_column"]),
            str(normalized["attempt_column"]),
        ]
        if normalized["next_retry_column"]:
            required.append(str(normalized["next_retry_column"]))
        missing = sorted(set(required) - set(columns))
        if missing:
            raise IdempotencyAuditError(
                "Colunas obrigatórias ausentes: " + ", ".join(missing)
            )

        indexes = _unique_indexes(conn, table)
        unique_ok = _unique_covers(indexes, normalized["idempotency_columns"])
        findings: list[dict] = []
        if normalized["require_unique_index"] and not unique_ok:
            findings.append(
                {
                    "code": "MISSING_UNIQUE_IDEMPOTENCY_INDEX",
                    "severity": "block",
                    "columns": normalized["idempotency_columns"],
                }
            )

        key_sql = ", ".join(_q(item) for item in normalized["idempotency_columns"])
        duplicates = _rows(
            conn,
            f"SELECT {key_sql}, COUNT(*) AS duplicate_count FROM {_q(table)} "
            f"GROUP BY {key_sql} HAVING COUNT(*) > 1 LIMIT 100",
        )
        if duplicates:
            findings.append(
                {
                    "code": "DUPLICATE_IDEMPOTENCY_KEY",
                    "severity": "block",
                    "sample": duplicates,
                }
            )

        if not normalized["allow_null_idempotency"]:
            null_where = " OR ".join(
                f"{_q(item)} IS NULL" for item in normalized["idempotency_columns"]
            )
            nulls = _rows(
                conn,
                f"SELECT {_q(str(normalized['id_column']))} AS row_id FROM {_q(table)} "
                f"WHERE {null_where} LIMIT 100",
            )
            if nulls:
                findings.append(
                    {
                        "code": "NULL_IDEMPOTENCY_KEY",
                        "severity": "block",
                        "sample": nulls,
                    }
                )

        attempt = _q(str(normalized["attempt_column"]))
        invalid_attempts = _rows(
            conn,
            f"SELECT {_q(str(normalized['id_column']))} AS row_id, {attempt} AS attempts "
            f"FROM {_q(table)} WHERE {attempt} IS NULL OR {attempt} < 0 OR {attempt} > ? LIMIT 100",
            (normalized["max_attempts"],),
        )
        if invalid_attempts:
            findings.append(
                {
                    "code": "INVALID_ATTEMPT_COUNTER",
                    "severity": "block",
                    "sample": invalid_attempts,
                }
            )

        status = _q(str(normalized["status_column"]))
        retryable_placeholders = ",".join("?" for _ in normalized["retryable_statuses"])
        exhausted = _rows(
            conn,
            f"SELECT {_q(str(normalized['id_column']))} AS row_id, {status} AS status, {attempt} AS attempts "
            f"FROM {_q(table)} WHERE {status} IN ({retryable_placeholders}) AND {attempt} >= ? LIMIT 100",
            tuple(normalized["retryable_statuses"]) + (normalized["max_attempts"],),
        )
        if exhausted:
            findings.append(
                {
                    "code": "RETRYABLE_STATUS_AT_OR_ABOVE_LIMIT",
                    "severity": "block",
                    "sample": exhausted,
                }
            )

        if normalized["next_retry_column"]:
            next_retry = _q(str(normalized["next_retry_column"]))
            terminal_placeholders = ",".join("?" for _ in normalized["terminal_statuses"])
            terminal_scheduled = _rows(
                conn,
                f"SELECT {_q(str(normalized['id_column']))} AS row_id, {status} AS status, {next_retry} AS next_retry "
                f"FROM {_q(table)} WHERE {status} IN ({terminal_placeholders}) "
                f"AND {next_retry} IS NOT NULL LIMIT 100",
                tuple(normalized["terminal_statuses"]),
            )
            if terminal_scheduled:
                findings.append(
                    {
                        "code": "TERMINAL_JOB_STILL_SCHEDULED",
                        "severity": "block",
                        "sample": terminal_scheduled,
                    }
                )

        return {
            "version": 1,
            "mode": "READ_ONLY_IDEMPOTENCY_RETRY_AUDIT",
            "database": {"name": database.name, "opened_read_only": True},
            "policy": normalized,
            "schema": {
                "columns": columns,
                "unique_indexes": indexes,
                "idempotency_unique_index_ok": unique_ok,
            },
            "summary": {
                "blocking_findings": len(findings),
                "duplicate_keys": len(duplicates),
                "invalid_attempt_rows": len(invalid_attempts),
                "exhausted_retryable_rows": len(exhausted),
            },
            "findings": findings,
            "ok": len(findings) == 0,
            "mutation_performed": False,
        }
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audita idempotência/retry de jobs SQLite em modo somente leitura."
    )
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path("IDEMPOTENCY_RETRY_AUDIT.json"))
    args = parser.parse_args()
    try:
        report = audit_database(args.database, load_spec(args.spec))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except IdempotencyAuditError as exc:
        print(f"IDEMPOTENCY_RETRY_AUDIT_ERRO: {exc}", file=sys.stderr)
        return 2
    print("IDEMPOTENCY_RETRY_AUDIT_OK" if report["ok"] else "IDEMPOTENCY_RETRY_AUDIT_DIVERGENTE")
    print(f"Achados: {report['summary']['blocking_findings']}")
    print("Mutação: NÃO")
    return 0 if report["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
