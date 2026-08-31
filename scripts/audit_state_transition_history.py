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


class TransitionAuditError(RuntimeError):
    pass


def _ident(value: object, field: str, *, optional: bool = False) -> str | None:
    text = str(value or "").strip()
    if optional and not text:
        return None
    if not IDENT_RE.fullmatch(text):
        raise TransitionAuditError(f"{field} inválido: {text!r}")
    return text


def _ident_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise TransitionAuditError(f"{field} deve ser lista não vazia.")
    result: list[str] = []
    for item in value:
        ident = _ident(item, field)
        assert ident is not None
        result.append(ident)
    if len(set(result)) != len(result):
        raise TransitionAuditError(f"{field} contém duplicidade.")
    return result


def _state_list(value: object, field: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise TransitionAuditError(f"{field} deve ser lista de estados.")
    return [item.strip() for item in value]


def normalize_spec(spec: dict) -> dict:
    if not isinstance(spec, dict) or spec.get("version") != SPEC_VERSION:
        raise TransitionAuditError(f"Spec deve ser objeto version={SPEC_VERSION}.")

    raw_allowed = spec.get("allowed_transitions", {})
    if not isinstance(raw_allowed, dict):
        raise TransitionAuditError("allowed_transitions deve ser objeto.")
    allowed: dict[str, list[str]] = {}
    for state, targets in raw_allowed.items():
        source = str(state).strip()
        if not source:
            raise TransitionAuditError("Estado origem vazio em allowed_transitions.")
        allowed[source] = _state_list(
            targets, f"allowed_transitions.{source}", allow_empty=True
        )

    raw_floor = spec.get("call_floor_by_state", {})
    if not isinstance(raw_floor, dict):
        raise TransitionAuditError("call_floor_by_state deve ser objeto.")
    floor: dict[str, int] = {}
    for state, value in raw_floor.items():
        name = str(state).strip()
        if not name or not isinstance(value, int) or value < 1:
            raise TransitionAuditError(
                f"Floor inválido para estado {state!r}: {value!r}"
            )
        floor[name] = value

    current_table = _ident(spec.get("current_table"), "current_table", optional=True)
    current_state = _ident(
        spec.get("current_state_column"), "current_state_column", optional=True
    )
    current_call = _ident(
        spec.get("current_call_column"), "current_call_column", optional=True
    )
    if any([current_table, current_state, current_call]) and not all(
        [current_table, current_state, current_call]
    ):
        raise TransitionAuditError(
            "current_table/current_state_column/current_call_column devem ser informados juntos."
        )

    return {
        "version": SPEC_VERSION,
        "history_table": _ident(spec.get("history_table"), "history_table"),
        "key_columns": _ident_list(spec.get("key_columns"), "key_columns"),
        "order_column": _ident(spec.get("order_column"), "order_column"),
        "state_column": _ident(spec.get("state_column"), "state_column"),
        "call_column": _ident(spec.get("call_column"), "call_column"),
        "allowed_transitions": allowed,
        "call_floor_by_state": floor,
        "forbid_call_decrease": spec.get("forbid_call_decrease", True) is True,
        "current_table": current_table,
        "current_state_column": current_state,
        "current_call_column": current_call,
        "require_history_for_current": spec.get("require_history_for_current", True)
        is True,
    }


def load_spec(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise TransitionAuditError(f"Spec inexistente: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TransitionAuditError(f"Spec inválida: {exc}") from exc
    return normalize_spec(data)


def _q(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _connect(database: Path) -> sqlite3.Connection:
    path = database.resolve()
    if not path.is_file():
        raise TransitionAuditError(f"Banco inexistente: {path}")
    uri = "file:" + quote(path.as_posix(), safe="/:") + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA query_only=ON")
    return conn


def _columns(conn: sqlite3.Connection, table: str) -> list[str]:
    return [str(row[1]) for row in conn.execute(f"PRAGMA table_info({_q(table)})")]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def _key(row: sqlite3.Row | dict, columns: list[str]) -> tuple:
    return tuple(row[column] for column in columns)


def _key_dict(key: tuple, columns: list[str]) -> dict:
    return {columns[index]: key[index] for index in range(len(columns))}


def _parse_call(raw: object) -> int | None:
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def audit_database(database: Path, spec: dict) -> dict:
    policy = normalize_spec(spec)
    before_hash = sha256_file(database)
    conn = _connect(database)
    try:
        history_table = str(policy["history_table"])
        required_history = [
            *policy["key_columns"],
            str(policy["order_column"]),
            str(policy["state_column"]),
            str(policy["call_column"]),
        ]
        history_columns = _columns(conn, history_table)
        if not history_columns:
            raise TransitionAuditError(
                f"Tabela de histórico inexistente: {history_table}"
            )
        missing = sorted(set(required_history) - set(history_columns))
        if missing:
            raise TransitionAuditError(
                "Colunas ausentes no histórico: " + ", ".join(missing)
            )

        select_cols = ", ".join(_q(item) for item in required_history)
        order_cols = ", ".join(
            _q(item)
            for item in [*policy["key_columns"], str(policy["order_column"])]
        )
        history_rows = conn.execute(
            f"SELECT {select_cols} FROM {_q(history_table)} ORDER BY {order_cols}"
        ).fetchall()
        grouped: dict[tuple, list[sqlite3.Row]] = defaultdict(list)
        for row in history_rows:
            grouped[_key(row, policy["key_columns"])].append(row)

        findings: list[dict] = []
        last_valid_by_key: dict[tuple, tuple[str, int]] = {}
        for key, rows in grouped.items():
            seen_orders = set()
            previous: tuple[object, str, int] | None = None
            enforced_floor = 0
            for row in rows:
                order_value = row[str(policy["order_column"])]
                state = str(row[str(policy["state_column"])])
                raw_call = row[str(policy["call_column"])]

                if order_value in seen_orders:
                    findings.append(
                        {
                            "code": "DUPLICATE_TRANSITION_ORDER",
                            "severity": "block",
                            "key": _key_dict(key, policy["key_columns"]),
                            "order": order_value,
                        }
                    )
                seen_orders.add(order_value)

                call = _parse_call(raw_call)
                if call is None:
                    findings.append(
                        {
                            "code": "INVALID_CALL_VALUE",
                            "severity": "block",
                            "key": _key_dict(key, policy["key_columns"]),
                            "order": order_value,
                            "value": raw_call,
                        }
                    )
                    previous = None
                    continue

                own_floor = int(policy["call_floor_by_state"].get(state, 0))
                if own_floor and call < own_floor:
                    findings.append(
                        {
                            "code": "STATE_CALL_FLOOR_VIOLATION",
                            "severity": "block",
                            "key": _key_dict(key, policy["key_columns"]),
                            "order": order_value,
                            "state": state,
                            "call": call,
                            "required_floor": own_floor,
                        }
                    )
                enforced_floor = max(enforced_floor, own_floor)
                if enforced_floor and call < enforced_floor:
                    findings.append(
                        {
                            "code": "PROTECTED_CALL_FLOOR_REGRESSION",
                            "severity": "block",
                            "key": _key_dict(key, policy["key_columns"]),
                            "order": order_value,
                            "state": state,
                            "call": call,
                            "protected_floor": enforced_floor,
                        }
                    )

                if previous is not None:
                    prev_order, prev_state, prev_call = previous
                    if policy["forbid_call_decrease"] and call < prev_call:
                        findings.append(
                            {
                                "code": "CALL_DECREASE",
                                "severity": "block",
                                "key": _key_dict(key, policy["key_columns"]),
                                "from_order": prev_order,
                                "to_order": order_value,
                                "from_call": prev_call,
                                "to_call": call,
                                "from_state": prev_state,
                                "to_state": state,
                            }
                        )
                    allowed_targets = policy["allowed_transitions"].get(prev_state)
                    if allowed_targets is not None and state not in allowed_targets:
                        findings.append(
                            {
                                "code": "FORBIDDEN_STATE_TRANSITION",
                                "severity": "block",
                                "key": _key_dict(key, policy["key_columns"]),
                                "from_state": prev_state,
                                "to_state": state,
                                "from_order": prev_order,
                                "to_order": order_value,
                            }
                        )
                previous = (order_value, state, call)
                last_valid_by_key[key] = (state, call)

        current_checked = 0
        if policy["current_table"]:
            current_table = str(policy["current_table"])
            required_current = [
                *policy["key_columns"],
                str(policy["current_state_column"]),
                str(policy["current_call_column"]),
            ]
            current_columns = _columns(conn, current_table)
            if not current_columns:
                raise TransitionAuditError(
                    f"Tabela current inexistente: {current_table}"
                )
            missing_current = sorted(set(required_current) - set(current_columns))
            if missing_current:
                raise TransitionAuditError(
                    "Colunas ausentes no current: " + ", ".join(missing_current)
                )
            current_rows = conn.execute(
                f"SELECT {', '.join(_q(item) for item in required_current)} "
                f"FROM {_q(current_table)}"
            ).fetchall()
            for row in current_rows:
                current_checked += 1
                key = _key(row, policy["key_columns"])
                last = last_valid_by_key.get(key)
                if last is None:
                    if policy["require_history_for_current"]:
                        findings.append(
                            {
                                "code": "CURRENT_WITHOUT_VALID_HISTORY",
                                "severity": "block",
                                "key": _key_dict(key, policy["key_columns"]),
                            }
                        )
                    continue

                current_state = str(row[str(policy["current_state_column"])] )
                raw_current_call = row[str(policy["current_call_column"])]
                current_call = _parse_call(raw_current_call)
                if current_call is None:
                    findings.append(
                        {
                            "code": "CURRENT_INVALID_CALL_VALUE",
                            "severity": "block",
                            "key": _key_dict(key, policy["key_columns"]),
                            "value": raw_current_call,
                        }
                    )
                    continue

                history_state, history_call = last
                if current_state != history_state or current_call != history_call:
                    findings.append(
                        {
                            "code": "CURRENT_HISTORY_MISMATCH",
                            "severity": "block",
                            "key": _key_dict(key, policy["key_columns"]),
                            "history": {
                                "state": history_state,
                                "call": history_call,
                            },
                            "current": {
                                "state": current_state,
                                "call": current_call,
                            },
                        }
                    )

        after_hash = sha256_file(database)
        if before_hash != after_hash:
            findings.append(
                {"code": "DATABASE_CHANGED_DURING_AUDIT", "severity": "block"}
            )
        return {
            "version": 1,
            "mode": "READ_ONLY_STATE_TRANSITION_AUDIT",
            "database": {
                "name": database.name,
                "sha256_before": before_hash,
                "sha256_after": after_hash,
                "opened_read_only": True,
            },
            "policy": policy,
            "summary": {
                "history_rows": len(history_rows),
                "entities": len(grouped),
                "current_rows_checked": current_checked,
                "blocking_findings": len(findings),
            },
            "findings": findings,
            "ok": len(findings) == 0,
            "mutation_performed": False,
        }
    finally:
        conn.close()


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Reconstrói e audita transições de estado/chamada SQLite sem alterar o banco."
        )
    )
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument(
        "--output", type=Path, default=Path("STATE_TRANSITION_AUDIT.json")
    )
    args = parser.parse_args()
    try:
        report = audit_database(args.database, load_spec(args.spec))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except TransitionAuditError as exc:
        print(f"STATE_TRANSITION_AUDIT_ERRO: {exc}", file=sys.stderr)
        return 2
    print(
        "STATE_TRANSITION_AUDIT_OK"
        if report["ok"]
        else "STATE_TRANSITION_AUDIT_DIVERGENTE"
    )
    print(f"Entidades: {report['summary']['entities']}")
    print(f"Achados: {report['summary']['blocking_findings']}")
    print("Mutação: NÃO")
    return 0 if report["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
