from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPORT_VERSION = 1


class DatabaseAuditError(RuntimeError):
    pass


@dataclass(frozen=True)
class ForeignKeyViolation:
    table: str
    rowid: int | None
    parent: str
    fkid: int


def quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def canonical_hash(value: object) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def connect_read_only(database: Path) -> sqlite3.Connection:
    database = database.resolve()
    if not database.is_file():
        raise DatabaseAuditError(f"Banco não encontrado: {database}")
    try:
        connection = sqlite3.connect(
            database.as_uri() + "?mode=ro",
            uri=True,
            timeout=5.0,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only=ON")
        return connection
    except sqlite3.Error as exc:
        raise DatabaseAuditError(
            f"Falha ao abrir SQLite em modo somente leitura: {exc}"
        ) from exc


def scalar(connection: sqlite3.Connection, pragma: str) -> Any:
    row = connection.execute(pragma).fetchone()
    return None if row is None else row[0]


def schema_inventory(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT type, name, tbl_name, sql
        FROM sqlite_master
        WHERE type IN ('table', 'index', 'view', 'trigger')
        ORDER BY type, name
        """
    ).fetchall()
    return [
        {
            "type": row["type"],
            "name": row["name"],
            "table": row["tbl_name"],
            "sql": row["sql"],
        }
        for row in rows
    ]


def user_tables(inventory: list[dict[str, Any]]) -> list[str]:
    return sorted(
        item["name"]
        for item in inventory
        if item["type"] == "table" and not str(item["name"]).startswith("sqlite_")
    )


def table_row_counts(
    connection: sqlite3.Connection, tables: list[str]
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table in tables:
        row = connection.execute(
            f"SELECT COUNT(*) FROM {quote_identifier(table)}"
        ).fetchone()
        counts[table] = int(row[0])
    return counts


def declared_foreign_keys(
    connection: sqlite3.Connection, tables: list[str]
) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for table in tables:
        rows = connection.execute(
            f"PRAGMA foreign_key_list({quote_identifier(table)})"
        ).fetchall()
        if not rows:
            continue
        result[table] = [
            {
                "id": int(row["id"]),
                "seq": int(row["seq"]),
                "parent_table": row["table"],
                "from": row["from"],
                "to": row["to"],
                "on_update": row["on_update"],
                "on_delete": row["on_delete"],
                "match": row["match"],
            }
            for row in rows
        ]
    return result


def run_integrity_check(connection: sqlite3.Connection) -> list[str]:
    return [
        str(row[0])
        for row in connection.execute("PRAGMA integrity_check").fetchall()
    ]


def run_foreign_key_check(
    connection: sqlite3.Connection,
) -> list[ForeignKeyViolation]:
    violations: list[ForeignKeyViolation] = []
    for row in connection.execute("PRAGMA foreign_key_check").fetchall():
        violations.append(
            ForeignKeyViolation(
                table=str(row[0]),
                rowid=None if row[1] is None else int(row[1]),
                parent=str(row[2]),
                fkid=int(row[3]),
            )
        )
    return violations


def audit_database(
    database: Path, *, include_row_counts: bool = True
) -> dict[str, Any]:
    database = database.resolve()
    try:
        connection = connect_read_only(database)
        try:
            # Força leitura real logo no início para rejeitar arquivo não-SQLite.
            application_id = int(scalar(connection, "PRAGMA application_id") or 0)
            user_version = int(scalar(connection, "PRAGMA user_version") or 0)
            journal_mode = str(scalar(connection, "PRAGMA journal_mode") or "")
            page_size = int(scalar(connection, "PRAGMA page_size") or 0)
            page_count = int(scalar(connection, "PRAGMA page_count") or 0)
            freelist_count = int(scalar(connection, "PRAGMA freelist_count") or 0)
            encoding = str(scalar(connection, "PRAGMA encoding") or "")
            connection_fk_setting = int(
                scalar(connection, "PRAGMA foreign_keys") or 0
            )

            integrity_rows = run_integrity_check(connection)
            integrity_ok = bool(integrity_rows) and all(
                value.lower() == "ok" for value in integrity_rows
            )

            fk_violations = run_foreign_key_check(connection)
            foreign_keys_ok = len(fk_violations) == 0

            inventory = schema_inventory(connection)
            tables = user_tables(inventory)
            fk_definitions = declared_foreign_keys(connection, tables)
            row_counts = (
                table_row_counts(connection, tables)
                if include_row_counts
                else None
            )

            schema_canonical = [
                {
                    "type": item["type"],
                    "name": item["name"],
                    "table": item["table"],
                    "sql": item["sql"],
                }
                for item in inventory
            ]

            report: dict[str, Any] = {
                "report_version": REPORT_VERSION,
                "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                "database": {
                    "name": database.name,
                    "size_bytes": database.stat().st_size,
                    "application_id": application_id,
                    "user_version": user_version,
                    "journal_mode": journal_mode,
                    "page_size": page_size,
                    "page_count": page_count,
                    "freelist_count": freelist_count,
                    "encoding": encoding,
                    "connection_foreign_keys_setting": connection_fk_setting,
                    "opened_read_only": True,
                    "query_only": True,
                },
                "integrity": {
                    "ok": integrity_ok,
                    "rows": integrity_rows,
                },
                "foreign_keys": {
                    "ok": foreign_keys_ok,
                    "violations": [asdict(item) for item in fk_violations],
                    "declared_count": sum(
                        len(items) for items in fk_definitions.values()
                    ),
                    "definitions": fk_definitions,
                },
                "schema": {
                    "object_count": len(inventory),
                    "table_count": len(tables),
                    "tables": tables,
                    "objects": inventory,
                    "sha256": canonical_hash(schema_canonical),
                },
                "row_counts": row_counts,
                "logical_invariants": {
                    "status": "NOT_EVALUATED",
                    "reason": (
                        "As invariantes de negócio V8 dependem do schema operacional "
                        "reconciliado e são avaliadas em etapa separada."
                    ),
                },
                "summary": {
                    "structural_ok": integrity_ok and foreign_keys_ok,
                    "integrity_ok": integrity_ok,
                    "foreign_keys_ok": foreign_keys_ok,
                    "logical_invariants_evaluated": False,
                },
            }
            return report
        finally:
            connection.close()
    except DatabaseAuditError:
        raise
    except sqlite3.DatabaseError as exc:
        raise DatabaseAuditError(
            f"Arquivo não é um SQLite válido ou está ilegível: {exc}"
        ) from exc
    except sqlite3.Error as exc:
        raise DatabaseAuditError(f"Falha durante auditoria SQLite: {exc}") from exc


def write_report(path: Path, report: dict[str, Any]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audita uma base SQLite do Axiom Tools em modo somente leitura. "
            "Não executa migração nem correção."
        )
    )
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--skip-row-counts",
        action="store_true",
        help="Pula COUNT(*) por tabela para auditorias muito grandes.",
    )
    args = parser.parse_args()

    try:
        report = audit_database(
            args.database,
            include_row_counts=not args.skip_row_counts,
        )
        if args.output:
            write_report(args.output, report)
    except DatabaseAuditError as exc:
        print(f"SQLITE_AUDIT_ERRO: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"SQLITE_AUDIT_ERRO_INESPERADO: {exc}", file=sys.stderr)
        return 2

    summary = report["summary"]
    print(
        "SQLITE_AUDIT_OK"
        if summary["structural_ok"]
        else "SQLITE_AUDIT_DIVERGENTE"
    )
    print(f"Banco: {report['database']['name']}")
    print(f"user_version: {report['database']['user_version']}")
    print(f"Tabelas: {report['schema']['table_count']}")
    print(
        f"integrity_check: {'OK' if summary['integrity_ok'] else 'FALHA'}"
    )
    print(
        "foreign_key_check: "
        f"{'OK' if summary['foreign_keys_ok'] else 'FALHA'}"
    )
    print("Invariantes lógicas V8: NÃO AVALIADAS")
    if args.output:
        print(f"Relatório: {args.output.resolve()}")

    return 0 if summary["structural_ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
