from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

MUTATING = {"POST", "PUT", "PATCH", "DELETE"}
ROUTE_CALL_NAMES = {"route", "get", "post", "put", "patch", "delete"}


class RouteAuditError(RuntimeError):
    pass


@dataclass(frozen=True)
class RouteRecord:
    file: str
    line: int
    function: str
    path: str | None
    methods: list[str]
    decorators: list[str]
    auth_markers: list[str]
    csrf_exempt: bool
    mutating: bool


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    if isinstance(node, ast.Call):
        return dotted_name(node.func)
    return ""


def decorator_name(node: ast.AST) -> str:
    return dotted_name(node.func if isinstance(node, ast.Call) else node)


def literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def extract_methods(decorator: ast.AST, route_name: str) -> list[str]:
    tail = route_name.split(".")[-1].lower()
    if tail in {"get", "post", "put", "patch", "delete"}:
        return [tail.upper()]
    methods = ["GET"]
    if isinstance(decorator, ast.Call):
        for keyword in decorator.keywords:
            if keyword.arg == "methods" and isinstance(
                keyword.value, (ast.List, ast.Tuple, ast.Set)
            ):
                found = []
                for item in keyword.value.elts:
                    value = literal_string(item)
                    if value:
                        found.append(value.upper())
                if found:
                    methods = sorted(set(found))
    return methods


def extract_path(decorator: ast.AST) -> str | None:
    if isinstance(decorator, ast.Call) and decorator.args:
        return literal_string(decorator.args[0])
    return None


def load_policy(path: Path | None) -> dict:
    default = {
        "auth_decorators": ["login_required"],
        "csrf_exempt_decorators": ["csrf.exempt"],
    }
    if path is None:
        return default
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RouteAuditError(f"Política inválida: {exc}") from exc
    if not isinstance(data, dict):
        raise RouteAuditError("Política deve ser objeto JSON.")
    auth = data.get("auth_decorators", default["auth_decorators"])
    csrf = data.get(
        "csrf_exempt_decorators", default["csrf_exempt_decorators"]
    )
    if not isinstance(auth, list) or not all(
        isinstance(item, str) and item.strip() for item in auth
    ):
        raise RouteAuditError("auth_decorators deve ser lista de strings.")
    if not isinstance(csrf, list) or not all(
        isinstance(item, str) and item.strip() for item in csrf
    ):
        raise RouteAuditError("csrf_exempt_decorators deve ser lista de strings.")
    return {
        "auth_decorators": [item.strip() for item in auth],
        "csrf_exempt_decorators": [item.strip() for item in csrf],
    }


def _matches_marker(decorator: str, markers: list[str]) -> bool:
    for marker in markers:
        if (
            decorator == marker
            or decorator.endswith("." + marker)
            or decorator.startswith(marker + "(")
        ):
            return True
        if decorator.endswith("." + marker.split(".")[-1]):
            return True
    return False


def scan_file(path: Path, root: Path, policy: dict) -> list[RouteRecord]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        raise RouteAuditError(f"Falha ao analisar {path}: {exc}") from exc

    records = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        route_decorators = []
        all_decorators = [decorator_name(item) for item in node.decorator_list]
        for decorator in node.decorator_list:
            name = decorator_name(decorator)
            if name.split(".")[-1].lower() in ROUTE_CALL_NAMES:
                route_decorators.append((decorator, name))

        for decorator, name in route_decorators:
            methods = extract_methods(decorator, name)
            mutating = bool(set(methods) & MUTATING)
            auth_markers = [
                item
                for item in all_decorators
                if _matches_marker(item, policy["auth_decorators"])
            ]
            csrf_exempt = any(
                _matches_marker(item, policy["csrf_exempt_decorators"])
                for item in all_decorators
            )
            records.append(
                RouteRecord(
                    file=path.relative_to(root).as_posix(),
                    line=node.lineno,
                    function=node.name,
                    path=extract_path(decorator),
                    methods=methods,
                    decorators=all_decorators,
                    auth_markers=auth_markers,
                    csrf_exempt=csrf_exempt,
                    mutating=mutating,
                )
            )
    return records


def audit_tree(root: Path, policy: dict) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise RouteAuditError(f"Raiz inválida: {root}")

    records = []
    errors = []
    for path in sorted(root.rglob("*.py")):
        if any(
            part in {".venv", "venv", "__pycache__"} for part in path.parts
        ):
            continue
        try:
            records.extend(scan_file(path, root, policy))
        except RouteAuditError as exc:
            errors.append(str(exc))

    findings = []
    for record in records:
        if record.mutating and not record.auth_markers:
            findings.append(
                {
                    "severity": "review",
                    "code": "MUTATING_ROUTE_WITHOUT_AUTH_MARKER",
                    "file": record.file,
                    "line": record.line,
                    "function": record.function,
                    "path": record.path,
                    "methods": record.methods,
                }
            )
        if record.csrf_exempt:
            findings.append(
                {
                    "severity": "review",
                    "code": "CSRF_EXEMPT_ROUTE",
                    "file": record.file,
                    "line": record.line,
                    "function": record.function,
                    "path": record.path,
                    "methods": record.methods,
                }
            )

    return {
        "policy": policy,
        "summary": {
            "routes": len(records),
            "mutating_routes": sum(1 for record in records if record.mutating),
            "mutating_without_auth_marker": sum(
                1
                for record in records
                if record.mutating and not record.auth_markers
            ),
            "csrf_exempt_routes": sum(
                1 for record in records if record.csrf_exempt
            ),
            "parse_errors": len(errors),
        },
        "routes": [asdict(record) for record in records],
        "findings": findings,
        "errors": errors,
        "status": "REVIEW_REQUIRED" if findings or errors else "NO_STATIC_FINDINGS",
        "disclaimer": (
            "Análise estática não prova autenticação/CSRF efetivos. "
            "Proteções globais, wrappers dinâmicos e configuração Flask-WTF "
            "devem ser validados no runtime."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inventaria rotas Flask e sinais estáticos de segurança."
    )
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--policy", type=Path, default=None)
    parser.add_argument(
        "--output", type=Path, default=Path("ROUTE_SECURITY_AUDIT.json")
    )
    args = parser.parse_args()

    try:
        policy = load_policy(args.policy)
        report = audit_tree(args.root, policy)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
    except RouteAuditError as exc:
        print(f"ROUTE_SECURITY_ERRO: {exc}", file=sys.stderr)
        return 2

    print("ROUTE_SECURITY_AUDIT_OK")
    for key, value in report["summary"].items():
        print(f"{key}: {value}")
    print(f"Status: {report['status']}")
    print(f"Relatório: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
