from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


class ScopeError(RuntimeError):
    pass


@dataclass
class FunctionInfo:
    file: str
    name: str
    lineno: int
    strings: list[tuple[int, str]]
    calls: set[str]


def _ident(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _ident(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _path_allowed(file: str, prefixes: tuple[str, ...]) -> bool:
    normalized = file.replace("\\", "/")
    return any(normalized.startswith(prefix.rstrip("/") + "/") or normalized == prefix.rstrip("/") for prefix in prefixes)


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(pattern.lower() in low for pattern in patterns)


def _collect(path: Path, root: Path, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionInfo:
    strings: list[tuple[int, str]] = []
    calls: set[str] = set()
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            strings.append((getattr(sub, "lineno", node.lineno), sub.value))
        elif isinstance(sub, ast.Call):
            call = _ident(sub.func)
            if call:
                calls.add(call)
    return FunctionInfo(path.relative_to(root).as_posix(), node.name, node.lineno, strings, calls)


def audit(root: Path, policy: dict) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise ScopeError(f"Raiz inválida: {root}")

    closing_table = str(policy.get("closing_table", "fechamento_mensal_cliente"))
    allowed_direct_sql_prefixes = tuple(policy.get("allowed_direct_sql_prefixes", ["modules/closing"]))
    live_scope_patterns = tuple(policy.get("live_scope_patterns", ["conferencia", "mesa", "chamada_atual", "clientes_conferencia"]))
    forbidden_live_statuses = tuple(str(x).upper() for x in policy.get("forbidden_live_statuses", ["FECHADA", "RETIFICACAO"]))
    facade_markers = tuple(policy.get("facade_markers", ["closing_scope", "closing.scope", "closing_service"]))
    require_facade_usage = bool(policy.get("require_facade_usage", False))
    require_target = bool(policy.get("require_target", True))

    functions: list[FunctionInfo] = []
    parse_errors: list[dict] = []
    for path in sorted(root.rglob("*.py")):
        if any(part in {".venv", "venv", "__pycache__"} for part in path.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as exc:
            parse_errors.append({"file": path.relative_to(root).as_posix(), "error": str(exc)})
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(_collect(path, root, node))

    findings: list[dict] = [{"code": "PARSE_ERROR", **item} for item in parse_errors]
    target_count = 0
    facade_usage_count = 0

    for fn in functions:
        if any(_contains_any(call, facade_markers) for call in fn.calls):
            facade_usage_count += 1

        for line, text in fn.strings:
            if closing_table.lower() in text.lower():
                target_count += 1
                if not _path_allowed(fn.file, allowed_direct_sql_prefixes):
                    findings.append({
                        "code": "DIRECT_CLOSING_SCOPE_SQL_OUTSIDE_DOMAIN",
                        "file": fn.file,
                        "function": fn.name,
                        "line": line,
                        "table": closing_table,
                    })

        if _contains_any(fn.name, live_scope_patterns):
            joined = "\n".join(text.upper() for _, text in fn.strings)
            for status in forbidden_live_statuses:
                if re.search(rf"\b{re.escape(status)}\b", joined):
                    findings.append({
                        "code": "FORBIDDEN_STATUS_IN_LIVE_SCOPE",
                        "file": fn.file,
                        "function": fn.name,
                        "line": fn.lineno,
                        "status": status,
                    })

    if require_target and target_count == 0:
        findings.append({"code": "NO_CLOSING_SCOPE_REFERENCE", "message": "Nenhuma referência ao universo mensal foi localizada."})
    if require_facade_usage and facade_usage_count == 0:
        findings.append({"code": "NO_CANONICAL_SCOPE_FACADE_USAGE", "message": "Nenhum consumo da fachada canônica foi localizado."})

    return {
        "version": 1,
        "audit": "B07_B09_B10_OPERATIONAL_SCOPE_CONTRACT",
        "all_ok": not findings,
        "closing_reference_count": target_count,
        "facade_usage_count": facade_usage_count,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita universo operacional canônico B07/B09/B10.")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        policy = json.loads(args.policy.read_text(encoding="utf-8"))
        report = audit(args.root, policy)
    except (OSError, json.JSONDecodeError, ScopeError) as exc:
        print(f"SCOPE_AUDIT_ERROR: {exc}", file=sys.stderr)
        return 2
    payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
