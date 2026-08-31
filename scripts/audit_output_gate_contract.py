from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path


class GateError(RuntimeError):
    pass


@dataclass
class FunctionNode:
    file: str
    name: str
    lineno: int
    calls: set[str]
    literals: set[str]
    is_mutating_route: bool


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
        if kw.arg == "methods" and isinstance(kw.value, (ast.List, ast.Tuple, ast.Set)):
            for item in kw.value.elts:
                if isinstance(item, ast.Constant) and isinstance(item.value, str):
                    methods.add(item.value.upper())
    return methods or {"GET"}


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(pattern.lower() in low for pattern in patterns)


def _collect(path: Path, root: Path, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionNode:
    calls: set[str] = set()
    literals: set[str] = set()
    mutating_route = False
    for decorator in node.decorator_list:
        methods = _route_methods(decorator)
        if methods and methods.intersection({"POST", "PUT", "PATCH", "DELETE"}):
            mutating_route = True
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            name = _ident(sub.func)
            if name:
                calls.add(name)
        elif isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            literals.add(sub.value)
    return FunctionNode(path.relative_to(root).as_posix(), node.name, node.lineno, calls, literals, mutating_route)


def audit(root: Path, policy: dict) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise GateError(f"Raiz inválida: {root}")

    entrypoint_patterns = tuple(policy.get("entrypoint_patterns", ["gerar", "imprimir", "entregar", "saida", "output"]))
    generator_markers = tuple(policy.get("generator_markers", ["gerar_pdf", "gerar_saida", "imprimir", "entregar"]))
    gate_markers = tuple(policy.get("gate_markers", ["autorizar_saida", "output_gate", "gate_saida"]))
    forbidden_auth_literals = {str(x).upper() for x in policy.get("forbidden_auth_literals", ["PROCESSADO"])}
    required_auth_literals = {str(x).upper() for x in policy.get("required_auth_literals", ["FECHADA"])}
    require_entrypoint = bool(policy.get("require_entrypoint", True))
    max_depth = int(policy.get("max_call_depth", 8))
    if max_depth < 0 or max_depth > 32:
        raise GateError("max_call_depth deve ficar entre 0 e 32")

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
                info = _collect(path, root, node)
                functions[(info.file, info.name)] = info
                by_name.setdefault(info.name, []).append(info)

    def local_targets(source: FunctionNode, call_name: str) -> list[FunctionNode]:
        short = call_name.split(".")[-1]
        same_file = [x for x in by_name.get(short, []) if x.file == source.file]
        return same_file or by_name.get(short, [])

    entrypoints = [
        fn for fn in functions.values()
        if fn.is_mutating_route or _contains_any(fn.name, entrypoint_patterns)
    ]
    findings: list[dict] = [{"code": "PARSE_ERROR", **item} for item in parse_errors]
    if require_entrypoint and not entrypoints:
        findings.append({"code": "NO_OUTPUT_ENTRYPOINT", "message": "Nenhum entrypoint de saída foi localizado."})

    for entry in entrypoints:
        reachable_gate = False
        reaches_generator = _contains_any(entry.name, generator_markers)
        observed_literals: set[str] = set(x.upper() for x in entry.literals)
        stack: list[tuple[FunctionNode, list[str], int]] = [(entry, [entry.name], 0)]
        visited: set[tuple[str, str]] = set()
        generator_chains: list[list[str]] = []

        while stack:
            current, chain, depth = stack.pop()
            key = (current.file, current.name)
            if key in visited:
                continue
            visited.add(key)
            observed_literals.update(x.upper() for x in current.literals)
            for call in current.calls:
                if _contains_any(call, gate_markers):
                    reachable_gate = True
                if _contains_any(call, generator_markers):
                    reaches_generator = True
                    generator_chains.append(chain + [call])
                if depth < max_depth:
                    for target in local_targets(current, call):
                        stack.append((target, chain + [target.name], depth + 1))

        if reaches_generator and not reachable_gate:
            findings.append({
                "code": "OUTPUT_PATH_WITHOUT_GATE",
                "file": entry.file,
                "function": entry.name,
                "line": entry.lineno,
                "generator_chains": generator_chains,
            })
        if reaches_generator and forbidden_auth_literals.intersection(observed_literals) and not required_auth_literals.intersection(observed_literals):
            findings.append({
                "code": "FORBIDDEN_AUTH_SIGNAL_WITHOUT_CLOSED_STATE",
                "file": entry.file,
                "function": entry.name,
                "line": entry.lineno,
                "forbidden_literals": sorted(forbidden_auth_literals.intersection(observed_literals)),
            })

    return {
        "version": 1,
        "audit": "B03_SINGLE_OUTPUT_GATE",
        "all_ok": not findings,
        "entrypoint_count": len(entrypoints),
        "entrypoints": [{"file": x.file, "function": x.name, "line": x.lineno} for x in entrypoints],
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita o contrato B03 de gate único de autorização de saídas.")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        policy = json.loads(args.policy.read_text(encoding="utf-8"))
        report = audit(args.root, policy)
    except (OSError, json.JSONDecodeError, GateError) as exc:
        print(f"B03_AUDIT_ERROR: {exc}", file=sys.stderr)
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
