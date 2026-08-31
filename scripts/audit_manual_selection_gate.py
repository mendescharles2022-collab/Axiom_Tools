from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import dataclass
from pathlib import Path


class SelectionGateError(RuntimeError):
    pass


@dataclass
class FunctionNode:
    file: str
    name: str
    lineno: int
    calls: set[str]
    parameters: set[str]


def _ident(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _ident(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _contains_any(text: str, patterns: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(pattern.lower() in low for pattern in patterns)


def _collect(path: Path, root: Path, node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionNode:
    calls: set[str] = set()
    params = {arg.arg for arg in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]}
    if node.args.vararg:
        params.add(node.args.vararg.arg)
    if node.args.kwarg:
        params.add(node.args.kwarg.arg)
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            name = _ident(sub.func)
            if name:
                calls.add(name)
    return FunctionNode(path.relative_to(root).as_posix(), node.name, node.lineno, calls, params)


def audit(root: Path, policy: dict) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise SelectionGateError(f"Raiz inválida: {root}")

    selection_markers = tuple(policy.get("selection_markers", ["selecion", "selected", "ids", "clientes_ids", "documentos_ids"]))
    generator_markers = tuple(policy.get("generator_markers", ["gerar", "imprimir", "entregar", "saida"]))
    guard_markers = tuple(policy.get("guard_markers", ["filtrar_autorizados", "intersect", "validar_selecao", "autorizar_saida_lote", "gate_saida"]))
    require_target = bool(policy.get("require_target", True))
    max_depth = int(policy.get("max_call_depth", 6))
    if max_depth < 0 or max_depth > 32:
        raise SelectionGateError("max_call_depth deve ficar entre 0 e 32")

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

    targets = [
        fn for fn in functions.values()
        if _contains_any(fn.name, selection_markers)
        or any(_contains_any(param, selection_markers) for param in fn.parameters)
    ]
    findings: list[dict] = [{"code": "PARSE_ERROR", **item} for item in parse_errors]
    if require_target and not targets:
        findings.append({"code": "NO_MANUAL_SELECTION_TARGET", "message": "Nenhum fluxo de seleção manual foi localizado."})

    for target in targets:
        reaches_generator = False
        reaches_guard = False
        generator_chains: list[list[str]] = []
        guard_chains: list[list[str]] = []
        stack: list[tuple[FunctionNode, list[str], int]] = [(target, [target.name], 0)]
        visited: set[tuple[str, str]] = set()
        while stack:
            current, chain, depth = stack.pop()
            key = (current.file, current.name)
            if key in visited:
                continue
            visited.add(key)
            for call in current.calls:
                if _contains_any(call, guard_markers):
                    reaches_guard = True
                    guard_chains.append(chain + [call])
                if _contains_any(call, generator_markers):
                    reaches_generator = True
                    generator_chains.append(chain + [call])
                if depth < max_depth:
                    for nested in local_targets(current, call):
                        stack.append((nested, chain + [nested.name], depth + 1))
        if reaches_generator and not reaches_guard:
            findings.append({
                "code": "MANUAL_SELECTION_REACHES_OUTPUT_WITHOUT_BACKEND_GUARD",
                "file": target.file,
                "function": target.name,
                "line": target.lineno,
                "generator_chains": generator_chains,
            })

    return {
        "version": 1,
        "audit": "B39_MANUAL_SELECTION_BACKEND_GATE",
        "all_ok": not findings,
        "target_count": len(targets),
        "targets": [{"file": x.file, "function": x.name, "line": x.lineno} for x in targets],
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita B39: seleção manual não é autorização de saída.")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        policy = json.loads(args.policy.read_text(encoding="utf-8"))
        report = audit(args.root, policy)
    except (OSError, json.JSONDecodeError, SelectionGateError) as exc:
        print(f"B39_AUDIT_ERROR: {exc}", file=sys.stderr)
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
