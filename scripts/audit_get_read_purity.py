from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

WRITE_SQL_RE = re.compile(r"\b(INSERT|UPDATE|DELETE|REPLACE|CREATE|DROP|ALTER)\b", re.I)


class PurityError(RuntimeError):
    pass


@dataclass
class FunctionNode:
    file: str
    name: str
    lineno: int
    is_get_route: bool
    calls: set[str]
    direct_mutations: list[dict]


def _ident(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _ident(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _route_methods(decorator: ast.AST) -> set[str] | None:
    if not isinstance(decorator, ast.Call):
        return None
    name = _ident(decorator.func).lower()
    if not (name.endswith(".route") or name == "route"):
        return None
    methods: set[str] = set()
    for kw in decorator.keywords:
        if kw.arg != "methods":
            continue
        if isinstance(kw.value, (ast.List, ast.Tuple, ast.Set)):
            for item in kw.value.elts:
                if isinstance(item, ast.Constant) and isinstance(item.value, str):
                    methods.add(item.value.upper())
    return methods or {"GET"}


def _function_info(path: Path, root: Path, node: ast.FunctionDef | ast.AsyncFunctionDef, mutator_markers: tuple[str, ...]) -> FunctionNode:
    is_get = False
    for decorator in node.decorator_list:
        methods = _route_methods(decorator)
        if methods is not None and "GET" in methods:
            is_get = True

    calls: set[str] = set()
    direct: list[dict] = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            call_name = _ident(sub.func)
            if call_name:
                calls.add(call_name)
                low = call_name.lower()
                if any(marker.lower() in low for marker in mutator_markers):
                    direct.append({"code": "MUTATOR_CALL", "line": getattr(sub, "lineno", node.lineno), "detail": call_name})
        elif isinstance(sub, ast.Constant) and isinstance(sub.value, str) and WRITE_SQL_RE.search(sub.value):
            direct.append({"code": "WRITE_SQL", "line": getattr(sub, "lineno", node.lineno), "detail": WRITE_SQL_RE.search(sub.value).group(1).upper()})
    return FunctionNode(path.relative_to(root).as_posix(), node.name, node.lineno, is_get, calls, direct)


def audit(root: Path, policy: dict) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise PurityError(f"Raiz inválida: {root}")
    mutator_markers = tuple(policy.get("mutator_markers", ["sincronizar", "salvar", "fechar", "promover", "recalcular", "commit", "flush"]))
    require_get_route = bool(policy.get("require_get_route", True))
    max_depth = int(policy.get("max_call_depth", 8))
    if max_depth < 0 or max_depth > 32:
        raise PurityError("max_call_depth deve ficar entre 0 e 32")

    functions: dict[tuple[str, str], FunctionNode] = {}
    by_name: dict[str, list[FunctionNode]] = {}
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
                info = _function_info(path, root, node, mutator_markers)
                functions[(info.file, info.name)] = info
                by_name.setdefault(info.name, []).append(info)

    get_routes = [fn for fn in functions.values() if fn.is_get_route]
    findings: list[dict] = [{"code": "PARSE_ERROR", **item} for item in parse_errors]
    if require_get_route and not get_routes:
        findings.append({"code": "NO_GET_ROUTE", "message": "Nenhuma rota GET foi localizada."})

    def local_call_targets(source: FunctionNode, call_name: str) -> list[FunctionNode]:
        short = call_name.split(".")[-1]
        same_file = [x for x in by_name.get(short, []) if x.file == source.file]
        return same_file or by_name.get(short, [])

    for route in get_routes:
        stack: list[tuple[FunctionNode, list[str], int]] = [(route, [route.name], 0)]
        visited: set[tuple[str, str]] = set()
        while stack:
            current, chain, depth = stack.pop()
            key = (current.file, current.name)
            if key in visited:
                continue
            visited.add(key)
            for mut in current.direct_mutations:
                findings.append({
                    "code": "GET_MUTATION_REACHABLE",
                    "route_file": route.file,
                    "route_function": route.name,
                    "route_line": route.lineno,
                    "mutation_file": current.file,
                    "mutation_function": current.name,
                    "call_chain": chain,
                    "mutation": mut,
                })
            if depth >= max_depth:
                continue
            for call in sorted(current.calls):
                for target in local_call_targets(current, call):
                    target_key = (target.file, target.name)
                    if target_key not in visited:
                        stack.append((target, chain + [target.name], depth + 1))

    return {
        "version": 1,
        "audit": "B02_GET_READ_PURITY",
        "all_ok": not findings,
        "get_route_count": len(get_routes),
        "get_routes": [{"file": x.file, "function": x.name, "line": x.lineno} for x in get_routes],
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita pureza de leitura das rotas GET da Conferência/B02.")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        policy = json.loads(args.policy.read_text(encoding="utf-8"))
        report = audit(args.root, policy)
    except (OSError, json.JSONDecodeError, PurityError) as exc:
        print(f"B02_AUDIT_ERROR: {exc}", file=sys.stderr)
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
