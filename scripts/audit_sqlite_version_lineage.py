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
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class VersionLineageAuditError(RuntimeError):
    pass


def _ident(value: object, field: str, *, optional: bool = False) -> str | None:
    text = str(value or "").strip()
    if optional and not text:
        return None
    if not IDENT_RE.fullmatch(text):
        raise VersionLineageAuditError(f"{field} inválido: {text!r}")
    return text


def _ident_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise VersionLineageAuditError(f"{field} deve ser lista não vazia.")
    result = []
    for item in value:
        ident = _ident(item, field)
        assert ident is not None
        result.append(ident)
    if len(set(result)) != len(result):
        raise VersionLineageAuditError(f"{field} contém duplicidade.")
    return result


def normalize_spec(spec: dict) -> dict:
    if not isinstance(spec, dict) or spec.get("version") != SPEC_VERSION:
        raise VersionLineageAuditError(f"Spec deve ser objeto version={SPEC_VERSION}.")
    required_statuses = spec.get("parent_current_required_statuses", [])
    if not isinstance(required_statuses, list) or not all(
        isinstance(item, str) and item.strip() for item in required_statuses
    ):
        raise VersionLineageAuditError(
            "parent_current_required_statuses deve ser lista de strings."
        )
    status_column = _ident(
        spec.get("parent_status_column"), "parent_status_column", optional=True
    )
    if required_statuses and not status_column:
        raise VersionLineageAuditError(
            "parent_status_column é obrigatório quando há statuses que exigem versão vigente."
        )
    current_flag_column = _ident(
        spec.get("version_current_flag_column"),
        "version_current_flag_column",
        optional=True,
    )
    current_flag_value = spec.get("version_current_flag_value", 1)
    if current_flag_column and not isinstance(current_flag_value, (str, int)):
        raise VersionLineageAuditError(
            "version_current_flag_value deve ser string ou inteiro."
        )
    return {
        "version": SPEC_VERSION,
        "parent_table": _ident(spec.get("parent_table"), "parent_table"),
        "version_table": _ident(spec.get("version_table"), "version_table"),
        "key_columns": _ident_list(spec.get("key_columns"), "key_columns"),
        "current_version_column": _ident(
            spec.get("current_version_column"), "current_version_column"
        ),
        "version_column": _ident(spec.get("version_column"), "version_column"),
        "parent_status_column": status_column,
        "parent_current_required_statuses": [item.strip() for item in required_statuses],
        "version_current_flag_column": current_flag_column,
        "version_current_flag_value": current_flag_value,
        "require_unique_version_index": spec.get(
            "require_unique_version_index", True
        )
        is True,
        "require_positive_version": spec.get("require_positive_version", True) is True,
    }


def load_spec(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise VersionLineageAuditError(f"Spec inexistente: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VersionLineageAuditError(f"Spec inválida: {exc}") from exc
    return normalize_spec(data)


def _q(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _connect(database: Path) -> sqlite3.Connection:
    path = database.resolve()
    if not path.is_file():
        raise VersionLineageAuditError(f"Banco inexistente: {path}")
    uri = "file:" + quote(path.as_posix(), safe="/:") + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [str(row[1]) for row in conn.execute(f"PRAGMA table_info({_q(table)})")]


def _unique_indexes(conn: sqlite3.Connection, table: str) -> list[dict]:
    indexes = []
    for row in conn.execute(f"PRAGMA index_list({_q(table)})"):
        if int(row[2]) != 1:
            continue
        name = str(row[1])
        cols = [
            str(info[2])
            for info in conn.execute(f"PRAGMA index_info({_q(name)})")
            if info[2] is not None
        ]
        indexes.append({"name": name, "columns": cols})
    return indexes


def _rows(conn: sqlite3.Connection, sql: str, params: tuple = ()) -> list[dict]:
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def audit_database(database: Path, spec: dict) -> dict:
    policy = normalize_spec(spec)
    before_hash = sha256_file(database)
    conn = _connect(database)
    try:
        parent = str(policy["parent_table"])
        versions = str(policy["version_table"])
        parent_cols = _columns(conn, parent)
        version_cols = _columns(conn, versions)
        if not parent_cols:
            raise VersionLineageAuditError(f"Tabela pai inexistente: {parent}")
        if not version_cols:
            raise VersionLineageAuditError(f"Tabela de versões inexistente: {versions}")

        parent_required = [*policy["key_columns"], str(policy["current_version_column"])]
        if policy["parent_status_column"]:
            parent_required.append(str(policy["parent_status_column"]))
        version_required = [*policy["key_columns"], str(policy["version_column"])]
        if policy["version_current_flag_column"]:
            version_required.append(str(policy["version_current_flag_column"]))
        missing_parent = sorted(set(parent_required) - set(parent_cols))
        missing_versions = sorted(set(version_required) - set(version_cols))
        if missing_parent or missing_versions:
            raise VersionLineageAuditError(
                f"Colunas ausentes pai={missing_parent} versões={missing_versions}"
            )

        findings: list[dict] = []
        indexes = _unique_indexes(conn, versions)
        expected_index = [*policy["key_columns"], str(policy["version_column"])]
        unique_ok = any(
            [item.lower() for item in index["columns"]]
            == [item.lower() for item in expected_index]
            for index in indexes
        )
        if policy["require_unique_version_index"] and not unique_ok:
            findings.append(
                {
                    "code": "MISSING_UNIQUE_VERSION_INDEX",
                    "severity": "block",
                    "columns": expected_index,
                }
            )

        keys = ", ".join(_q(item) for item in policy["key_columns"])
        version_col = _q(str(policy["version_column"]))
        duplicates = _rows(
            conn,
            f"SELECT {keys}, {version_col} AS version_value, COUNT(*) AS duplicate_count "
            f"FROM {_q(versions)} GROUP BY {keys}, {version_col} HAVING COUNT(*) > 1 LIMIT 100",
        )
        if duplicates:
            findings.append(
                {"code": "DUPLICATE_VERSION_IDENTITY", "severity": "block", "sample": duplicates}
            )

        if policy["require_positive_version"]:
            invalid_versions = _rows(
                conn,
                f"SELECT {keys}, {version_col} AS version_value FROM {_q(versions)} "
                f"WHERE {version_col} IS NULL OR {version_col} <= 0 LIMIT 100",
            )
            if invalid_versions:
                findings.append(
                    {"code": "INVALID_VERSION_NUMBER", "severity": "block", "sample": invalid_versions}
                )

        join_keys = " AND ".join(
            f"v.{_q(item)} = p.{_q(item)}" for item in policy["key_columns"]
        )
        current_col = _q(str(policy["current_version_column"]))
        missing_current = _rows(
            conn,
            f"SELECT p.* FROM {_q(parent)} p WHERE p.{current_col} IS NOT NULL "
            f"AND NOT EXISTS (SELECT 1 FROM {_q(versions)} v WHERE {join_keys} "
            f"AND v.{version_col} = p.{current_col}) LIMIT 100",
        )
        if missing_current:
            findings.append(
                {"code": "CURRENT_VERSION_NOT_FOUND", "severity": "block", "sample": missing_current}
            )

        parent_join = " AND ".join(
            f"p.{_q(item)} = v.{_q(item)}" for item in policy["key_columns"]
        )
        orphans = _rows(
            conn,
            f"SELECT v.* FROM {_q(versions)} v WHERE NOT EXISTS "
            f"(SELECT 1 FROM {_q(parent)} p WHERE {parent_join}) LIMIT 100",
        )
        if orphans:
            findings.append(
                {"code": "ORPHAN_VERSION", "severity": "block", "sample": orphans}
            )

        if policy["parent_current_required_statuses"]:
            status_col = _q(str(policy["parent_status_column"]))
            placeholders = ",".join("?" for _ in policy["parent_current_required_statuses"])
            required_missing = _rows(
                conn,
                f"SELECT p.* FROM {_q(parent)} p WHERE p.{status_col} IN ({placeholders}) "
                f"AND p.{current_col} IS NULL LIMIT 100",
                tuple(policy["parent_current_required_statuses"]),
            )
            if required_missing:
                findings.append(
                    {
                        "code": "REQUIRED_CURRENT_VERSION_MISSING",
                        "severity": "block",
                        "sample": required_missing,
                    }
                )

        if policy["version_current_flag_column"]:
            flag_col = _q(str(policy["version_current_flag_column"]))
            flag_value = policy["version_current_flag_value"]
            multiple_flags = _rows(
                conn,
                f"SELECT {keys}, COUNT(*) AS current_count FROM {_q(versions)} "
                f"WHERE {flag_col} = ? GROUP BY {keys} HAVING COUNT(*) > 1 LIMIT 100",
                (flag_value,),
            )
            if multiple_flags:
                findings.append(
                    {
                        "code": "MULTIPLE_CURRENT_VERSIONS",
                        "severity": "block",
                        "sample": multiple_flags,
                    }
                )
            pointer_mismatch = _rows(
                conn,
                f"SELECT p.* FROM {_q(parent)} p WHERE EXISTS "
                f"(SELECT 1 FROM {_q(versions)} v WHERE {join_keys} AND v.{flag_col} = ? "
                f"AND (p.{current_col} IS NULL OR v.{version_col} <> p.{current_col})) LIMIT 100",
                (flag_value,),
            )
            if pointer_mismatch:
                findings.append(
                    {
                        "code": "CURRENT_POINTER_FLAG_MISMATCH",
                        "severity": "block",
                        "sample": pointer_mismatch,
                    }
                )

        after_hash = sha256_file(database)
        if before_hash != after_hash:
            findings.append(
                {"code": "DATABASE_CHANGED_DURING_AUDIT", "severity": "block"}
            )
        return {
            "version": 1,
            "mode": "READ_ONLY_VERSION_LINEAGE_AUDIT",
            "database": {
                "name": database.name,
                "sha256_before": before_hash,
                "sha256_after": after_hash,
                "opened_read_only": True,
            },
            "policy": policy,
            "schema": {
                "version_unique_index_ok": unique_ok,
                "unique_indexes": indexes,
            },
            "summary": {"blocking_findings": len(findings)},
            "findings": findings,
            "ok": len(findings) == 0,
            "mutation_performed": False,
        }
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audita linhagem/vigência de versões e retificações SQLite sem alterar o banco."
    )
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path("VERSION_LINEAGE_AUDIT.json"))
    args = parser.parse_args()
    try:
        report = audit_database(args.database, load_spec(args.spec))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except VersionLineageAuditError as exc:
        print(f"VERSION_LINEAGE_AUDIT_ERRO: {exc}", file=sys.stderr)
        return 2
    print("VERSION_LINEAGE_AUDIT_OK" if report["ok"] else "VERSION_LINEAGE_AUDIT_DIVERGENTE")
    print(f"Achados: {report['summary']['blocking_findings']}")
    print("Mutação: NÃO")
    return 0 if report["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
