from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

SPEC_VERSION = 1
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
FANOUT_POLICIES = {"BLOCK", "REPLICATE_EXPLICIT"}


class PerSourceMigrationError(RuntimeError):
    pass


def _ident(value: object, field: str, *, optional: bool = False) -> str | None:
    text = str(value or "").strip()
    if optional and not text:
        return None
    if not IDENT_RE.fullmatch(text):
        raise PerSourceMigrationError(f"{field} inválido: {text!r}")
    return text


def _ident_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise PerSourceMigrationError(f"{field} deve ser lista não vazia.")
    result: list[str] = []
    for item in value:
        ident = _ident(item, field)
        assert ident is not None
        result.append(ident)
    if len(set(result)) != len(result):
        raise PerSourceMigrationError(f"{field} contém duplicidade.")
    return result


def normalize_spec(spec: dict) -> dict:
    if not isinstance(spec, dict) or spec.get("version") != SPEC_VERSION:
        raise PerSourceMigrationError(f"Spec deve ser objeto version={SPEC_VERSION}.")
    fanout = str(spec.get("fanout_policy") or "BLOCK").strip().upper()
    if fanout not in FANOUT_POLICIES:
        raise PerSourceMigrationError(
            "fanout_policy deve ser BLOCK ou REPLICATE_EXPLICIT."
        )
    applicable_column = _ident(
        spec.get("source_applicable_column"),
        "source_applicable_column",
        optional=True,
    )
    applicable_value = spec.get("source_applicable_value", 1)
    if applicable_column and not isinstance(applicable_value, (str, int, float)):
        raise PerSourceMigrationError(
            "source_applicable_value deve ser escalar simples."
        )
    return {
        "version": SPEC_VERSION,
        "legacy_table": _ident(spec.get("legacy_table"), "legacy_table"),
        "source_table": _ident(spec.get("source_table"), "source_table"),
        "target_table": _ident(spec.get("target_table"), "target_table"),
        "key_columns": _ident_list(spec.get("key_columns"), "key_columns"),
        "legacy_decision_column": _ident(
            spec.get("legacy_decision_column"), "legacy_decision_column"
        ),
        "source_column": _ident(spec.get("source_column"), "source_column"),
        "source_applicable_column": applicable_column,
        "source_applicable_value": applicable_value,
        "target_decision_column": _ident(
            spec.get("target_decision_column"), "target_decision_column"
        ),
        "fanout_policy": fanout,
        "require_unique_target_identity": spec.get(
            "require_unique_target_identity", True
        )
        is True,
    }


def load_spec(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise PerSourceMigrationError(f"Spec inexistente: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PerSourceMigrationError(f"Spec inválida: {exc}") from exc
    return normalize_spec(data)


def _q(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _connect(database: Path) -> sqlite3.Connection:
    path = database.resolve()
    if not path.is_file():
        raise PerSourceMigrationError(f"Banco inexistente: {path}")
    uri = "file:" + quote(path.as_posix(), safe="/:") + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [str(row[1]) for row in conn.execute(f"PRAGMA table_info({_q(table)})")]


def _unique_indexes(conn: sqlite3.Connection, table: str) -> list[list[str]]:
    result: list[list[str]] = []
    for row in conn.execute(f"PRAGMA index_list({_q(table)})"):
        if int(row[2]) != 1:
            continue
        name = str(row[1])
        result.append(
            [
                str(info[2])
                for info in conn.execute(f"PRAGMA index_info({_q(name)})")
                if info[2] is not None
            ]
        )
    return result


def _key(row: sqlite3.Row | dict, columns: list[str]) -> tuple:
    return tuple(row[column] for column in columns)


def _key_dict(key: tuple, columns: list[str]) -> dict:
    return {columns[index]: key[index] for index in range(len(columns))}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def plan_migration(database: Path, spec: dict) -> dict:
    policy = normalize_spec(spec)
    before_hash = sha256_file(database)
    conn = _connect(database)
    try:
        keys = policy["key_columns"]
        legacy_table = str(policy["legacy_table"])
        source_table = str(policy["source_table"])
        target_table = str(policy["target_table"])
        source_col = str(policy["source_column"])
        legacy_decision = str(policy["legacy_decision_column"])
        target_decision = str(policy["target_decision_column"])

        required = {
            legacy_table: [*keys, legacy_decision],
            source_table: [*keys, source_col],
            target_table: [*keys, source_col, target_decision],
        }
        if policy["source_applicable_column"]:
            required[source_table].append(str(policy["source_applicable_column"]))
        for table, required_cols in required.items():
            actual = _columns(conn, table)
            if not actual:
                raise PerSourceMigrationError(f"Tabela inexistente: {table}")
            missing = sorted(set(required_cols) - set(actual))
            if missing:
                raise PerSourceMigrationError(
                    f"Colunas ausentes em {table}: " + ", ".join(missing)
                )

        findings: list[dict] = []
        identity_cols = [*keys, source_col]
        unique_indexes = _unique_indexes(conn, target_table)
        unique_ok = any(
            [item.lower() for item in cols]
            == [item.lower() for item in identity_cols]
            for cols in unique_indexes
        )
        if policy["require_unique_target_identity"] and not unique_ok:
            findings.append(
                {
                    "code": "MISSING_UNIQUE_TARGET_IDENTITY",
                    "severity": "block",
                    "columns": identity_cols,
                }
            )

        key_sql = ", ".join(_q(item) for item in keys)
        legacy_duplicates = [
            dict(row)
            for row in conn.execute(
                f"SELECT {key_sql}, COUNT(*) AS row_count FROM {_q(legacy_table)} "
                f"GROUP BY {key_sql} HAVING COUNT(*) > 1 LIMIT 100"
            ).fetchall()
        ]
        if legacy_duplicates:
            findings.append(
                {
                    "code": "DUPLICATE_LEGACY_GLOBAL_STATE",
                    "severity": "block",
                    "sample": legacy_duplicates,
                }
            )

        target_identity_sql = ", ".join(_q(item) for item in identity_cols)
        target_duplicates = [
            dict(row)
            for row in conn.execute(
                f"SELECT {target_identity_sql}, COUNT(*) AS row_count FROM {_q(target_table)} "
                f"GROUP BY {target_identity_sql} HAVING COUNT(*) > 1 LIMIT 100"
            ).fetchall()
        ]
        if target_duplicates:
            findings.append(
                {
                    "code": "DUPLICATE_TARGET_IDENTITY",
                    "severity": "block",
                    "sample": target_duplicates,
                }
            )

        legacy_rows = conn.execute(
            f"SELECT {key_sql}, {_q(legacy_decision)} AS legacy_decision "
            f"FROM {_q(legacy_table)} ORDER BY {key_sql}"
        ).fetchall()

        source_where = ""
        source_params: tuple = ()
        if policy["source_applicable_column"]:
            source_where = f" WHERE {_q(str(policy['source_applicable_column']))} = ?"
            source_params = (policy["source_applicable_value"],)
        source_rows = conn.execute(
            f"SELECT {key_sql}, {_q(source_col)} AS source FROM {_q(source_table)}"
            + source_where,
            source_params,
        ).fetchall()
        sources_by_key: dict[tuple, list[str]] = defaultdict(list)
        for row in source_rows:
            source = str(row["source"] or "").strip()
            if source:
                sources_by_key[_key(row, keys)].append(source)

        target_rows = conn.execute(
            f"SELECT {key_sql}, {_q(source_col)} AS source, "
            f"{_q(target_decision)} AS target_decision FROM {_q(target_table)}"
        ).fetchall()
        target_by_identity: dict[tuple, object] = {}
        for row in target_rows:
            target_by_identity[
                (*_key(row, keys), str(row["source"] or "").strip())
            ] = row["target_decision"]

        planned: list[dict] = []
        already_migrated: list[dict] = []
        for row in legacy_rows:
            key = _key(row, keys)
            decision = row["legacy_decision"]
            sources = sorted(set(sources_by_key.get(key, [])))
            if not sources:
                findings.append(
                    {
                        "code": "LEGACY_STATE_WITHOUT_APPLICABLE_SOURCE",
                        "severity": "block",
                        "key": _key_dict(key, keys),
                        "legacy_decision": decision,
                    }
                )
                continue
            if len(sources) > 1 and policy["fanout_policy"] == "BLOCK":
                findings.append(
                    {
                        "code": "AMBIGUOUS_FANOUT",
                        "severity": "block",
                        "key": _key_dict(key, keys),
                        "legacy_decision": decision,
                        "sources": sources,
                    }
                )
                continue

            for source in sources:
                identity = (*key, source)
                existing = target_by_identity.get(identity)
                base = {
                    "key": _key_dict(key, keys),
                    "source": source,
                    "decision": decision,
                }
                if identity in target_by_identity:
                    if existing == decision:
                        already_migrated.append(base)
                    else:
                        findings.append(
                            {
                                "code": "TARGET_DECISION_CONFLICT",
                                "severity": "block",
                                **base,
                                "existing_decision": existing,
                            }
                        )
                    continue
                planned.append(base)

        after_hash = sha256_file(database)
        if before_hash != after_hash:
            findings.append(
                {"code": "DATABASE_CHANGED_DURING_PLAN", "severity": "block"}
            )

        return {
            "version": 1,
            "mode": "READ_ONLY_MIGRATION_PLAN_NOT_EXECUTED",
            "database": {
                "name": database.name,
                "sha256_before": before_hash,
                "sha256_after": after_hash,
                "opened_read_only": True,
            },
            "policy": policy,
            "schema": {
                "target_identity_unique_index_ok": unique_ok,
                "target_unique_indexes": unique_indexes,
            },
            "summary": {
                "legacy_rows": len(legacy_rows),
                "applicable_source_rows": len(source_rows),
                "planned_inserts": len(planned),
                "already_migrated": len(already_migrated),
                "blocking_findings": len(findings),
            },
            "planned_inserts": planned,
            "already_migrated": already_migrated,
            "findings": findings,
            "plan_ok": len(findings) == 0,
            "migration_executed": False,
        }
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Planeja migração de decisão global para decisão por fonte sem alterar SQLite."
    )
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument(
        "--output", type=Path, default=Path("PER_SOURCE_MIGRATION_PLAN.json")
    )
    args = parser.parse_args()
    try:
        report = plan_migration(args.database, load_spec(args.spec))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except PerSourceMigrationError as exc:
        print(f"PER_SOURCE_MIGRATION_ERRO: {exc}", file=sys.stderr)
        return 2
    print(
        "PER_SOURCE_MIGRATION_PLAN_OK"
        if report["plan_ok"]
        else "PER_SOURCE_MIGRATION_PLAN_BLOQUEADO"
    )
    print(f"Planejadas: {report['summary']['planned_inserts']}")
    print(f"Achados: {report['summary']['blocking_findings']}")
    print("Migração executada: NÃO")
    return 0 if report["plan_ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
