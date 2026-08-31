from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SPEC_VERSION = 1
IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
UPDATE_RE = re.compile(
    r"\bUPDATE\s+(?P<table>[A-Za-z_][A-Za-z0-9_]*)\s+SET\s+.+?\s+WHERE\s+(?P<where>.+)",
    re.IGNORECASE | re.DOTALL,
)
COLUMN_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b\s*(?:=|IS\b|IN\s*\()", re.IGNORECASE)


class CasContractError(RuntimeError):
    pass


@dataclass(frozen=True)
class UpdateUsage:
    file: str
    line: int
    table: str
    sql: str
    where_columns: list[str]
    assigned_cursor: str | None
    rowcount_checked: bool


def _string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(
        isinstance(item, str) and IDENT_RE.fullmatch(item.strip()) for item in value
    ):
        raise CasContractError(f"{field} deve ser lista não vazia de identificadores SQL.")
    return [item.strip().lower() for item in value]


def normalize_spec(spec: dict) -> dict:
    if not isinstance(spec, dict) or spec.get("version") != SPEC_VERSION:
        raise CasContractError(f"Spec deve ser objeto version={SPEC_VERSION}.")
    raw_rules = spec.get("tables")
    if not isinstance(raw_rules, list) or not raw_rules:
        raise CasContractError("Spec deve conter lista não vazia 'tables'.")

    rules = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_rules, start=1):
        if not isinstance(raw, dict):
            raise CasContractError(f"Regra de tabela #{index} deve ser objeto.")
        table = str(raw.get("table") or "").strip().lower()
        if not IDENT_RE.fullmatch(table) or table in seen:
            raise CasContractError(f"Tabela inválida/duplicada na regra #{index}: {table!r}")
        seen.add(table)
        rules.append(
            {
                "table": table,
                "key_columns": _string_list(raw.get("key_columns"), f"{table}.key_columns"),
                "cas_columns": _string_list(raw.get("cas_columns"), f"{table}.cas_columns"),
                "require_rowcount_check": raw.get("require_rowcount_check", True) is True,
            }
        )
    return {
        "version": SPEC_VERSION,
        "tables": rules,
        "block_unresolved_execute": spec.get("block_unresolved_execute", False) is True,
    }


def load_spec(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise CasContractError(f"Spec inexistente: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CasContractError(f"Spec inválida: {exc}") from exc
    return normalize_spec(data)


def _literal_string(node: ast.AST, constants: dict[str, str]) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Name):
        return constants.get(node.id)
    return None


def _collect_constants(tree: ast.AST) -> dict[str, str]:
    constants: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if (
            isinstance(target, ast.Name)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            constants[target.id] = node.value.value
    return constants


def _cursor_name_for_call(tree: ast.AST, call: ast.Call) -> str | None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and node.value is call and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                return target.id
    return None


def _rowcount_checked(tree: ast.AST, cursor_name: str | None, call: ast.Call) -> bool:
    if cursor_name:
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr == "rowcount":
                if isinstance(node.value, ast.Name) and node.value.id == cursor_name:
                    return True
    # Também aceita encadeamento explícito: conn.execute(...).rowcount
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "rowcount" and node.value is call:
            return True
    return False


def _is_execute_call(node: ast.Call) -> bool:
    func = node.func
    return isinstance(func, ast.Attribute) and func.attr in {"execute", "executemany"}


def _where_columns(where: str) -> list[str]:
    return sorted({match.group(1).lower() for match in COLUMN_RE.finditer(where)})


def scan_file(path: Path, root: Path, rules_by_table: dict[str, dict]) -> tuple[list[UpdateUsage], list[dict], list[str]]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        return [], [], [f"{path.relative_to(root).as_posix()}: {exc}"]

    constants = _collect_constants(tree)
    usages: list[UpdateUsage] = []
    unresolved: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not _is_execute_call(node) or not node.args:
            continue
        sql = _literal_string(node.args[0], constants)
        if sql is None:
            unresolved.append(
                {
                    "file": path.relative_to(root).as_posix(),
                    "line": node.lineno,
                    "code": "UNRESOLVED_EXECUTE_SQL",
                }
            )
            continue
        match = UPDATE_RE.search(sql.strip().rstrip(";"))
        if not match:
            continue
        table = match.group("table").lower()
        if table not in rules_by_table:
            continue
        cursor_name = _cursor_name_for_call(tree, node)
        usages.append(
            UpdateUsage(
                file=path.relative_to(root).as_posix(),
                line=node.lineno,
                table=table,
                sql=" ".join(sql.split()),
                where_columns=_where_columns(match.group("where")),
                assigned_cursor=cursor_name,
                rowcount_checked=_rowcount_checked(tree, cursor_name, node),
            )
        )
    return usages, unresolved, []


def audit_tree(root: Path, spec: dict) -> dict:
    normalized = normalize_spec(spec)
    root = root.resolve()
    if not root.is_dir():
        raise CasContractError(f"Raiz inválida: {root}")
    rules_by_table = {item["table"]: item for item in normalized["tables"]}

    usages: list[UpdateUsage] = []
    unresolved: list[dict] = []
    errors: list[str] = []
    for path in sorted(root.rglob("*.py")):
        if any(part in {".venv", "venv", "__pycache__"} for part in path.parts):
            continue
        found, unresolved_found, file_errors = scan_file(path, root, rules_by_table)
        usages.extend(found)
        unresolved.extend(unresolved_found)
        errors.extend(file_errors)

    findings: list[dict] = []
    for usage in usages:
        rule = rules_by_table[usage.table]
        columns = set(usage.where_columns)
        missing_keys = sorted(set(rule["key_columns"]) - columns)
        present_guards = sorted(set(rule["cas_columns"]) & columns)
        violations = []
        if missing_keys:
            violations.append("MISSING_KEY_COLUMNS:" + ",".join(missing_keys))
        if not present_guards:
            violations.append("MISSING_CAS_GUARD")
        if rule["require_rowcount_check"] and not usage.rowcount_checked:
            violations.append("ROWCOUNT_NOT_CHECKED")
        if violations:
            findings.append(
                {
                    "code": "UNSAFE_STATE_UPDATE",
                    "severity": "block",
                    **asdict(usage),
                    "cas_columns_present": present_guards,
                    "violations": violations,
                }
            )

    if normalized["block_unresolved_execute"]:
        for item in unresolved:
            findings.append({"severity": "block", **item})
    if errors:
        findings.append(
            {"code": "PARSE_ERRORS", "severity": "block", "count": len(errors)}
        )

    return {
        "version": 1,
        "mode": "STATIC_CAS_AUDIT_NO_MUTATION",
        "policy": normalized,
        "summary": {
            "protected_updates": len(usages),
            "unsafe_updates": sum(
                1 for item in findings if item.get("code") == "UNSAFE_STATE_UPDATE"
            ),
            "unresolved_execute_calls": len(unresolved),
            "parse_errors": len(errors),
            "blocking_findings": len(findings),
        },
        "updates": [asdict(item) for item in usages],
        "unresolved_execute_calls": unresolved,
        "errors": errors,
        "findings": findings,
        "static_ok": len(findings) == 0,
        "mutation_performed": False,
        "disclaimer": (
            "A auditoria cobre SQL UPDATE resolvível estaticamente em execute/executemany. "
            "ORM, SQL construído dinamicamente e semântica transacional real exigem validação adicional."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audita compare-and-set de UPDATEs SQLite de estado sem alterar código ou banco."
    )
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path("SQLITE_CAS_AUDIT.json"))
    args = parser.parse_args()
    try:
        report = audit_tree(args.root, load_spec(args.spec))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except CasContractError as exc:
        print(f"SQLITE_CAS_AUDIT_ERRO: {exc}", file=sys.stderr)
        return 2

    print("SQLITE_CAS_AUDIT_OK" if report["static_ok"] else "SQLITE_CAS_AUDIT_DIVERGENTE")
    print(f"Updates protegidos: {report['summary']['protected_updates']}")
    print(f"Updates inseguros: {report['summary']['unsafe_updates']}")
    print(f"SQL não resolvido: {report['summary']['unresolved_execute_calls']}")
    print("Mutação: NÃO")
    return 0 if report["static_ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
