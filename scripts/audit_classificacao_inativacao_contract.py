from __future__ import annotations

import argparse
import ast
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

SPEC_VERSION = 1
CANONICAL = {"ENUM_MEMBER", "STRING_VALUE"}


class ClassificationContractError(RuntimeError):
    pass


@dataclass(frozen=True)
class Usage:
    file: str
    line: int
    context: str
    expression: str
    value_kind: str
    value_text: str


def dotted_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = dotted_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _string_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ClassificationContractError(
            f"{field} deve ser lista não vazia de strings."
        )
    return [item.strip() for item in value]


def normalize_spec(spec: dict) -> dict:
    if not isinstance(spec, dict) or spec.get("version") != SPEC_VERSION:
        raise ClassificationContractError(
            f"Spec deve ser objeto version={SPEC_VERSION}."
        )
    field = str(spec.get("field_name") or "classificacao_inativacao").strip()
    if not field.isidentifier():
        raise ClassificationContractError(f"field_name inválido: {field!r}")
    canonical = str(spec.get("canonical_representation") or "").strip().upper()
    if canonical not in CANONICAL:
        raise ClassificationContractError(
            "canonical_representation deve ser ENUM_MEMBER ou STRING_VALUE."
        )
    enum_types = _string_list(spec.get("enum_types", []), "enum_types")
    return {
        "version": SPEC_VERSION,
        "field_name": field,
        "canonical_representation": canonical,
        "enum_types": enum_types,
        "allow_raw_string_literals": spec.get("allow_raw_string_literals", False)
        is True,
        "allow_none": spec.get("allow_none", True) is True,
        "allow_dynamic": spec.get("allow_dynamic", False) is True,
    }


def load_spec(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ClassificationContractError(f"Spec inexistente: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ClassificationContractError(f"Spec inválida: {exc}") from exc
    return normalize_spec(data)


def _subscript_key(node: ast.Subscript) -> str | None:
    key = node.slice
    if isinstance(key, ast.Constant) and isinstance(key.value, str):
        return key.value
    return None


def is_field(node: ast.AST, field: str) -> bool:
    if isinstance(node, ast.Name):
        return node.id == field
    if isinstance(node, ast.Attribute):
        return node.attr == field
    if isinstance(node, ast.Subscript):
        return _subscript_key(node) == field
    return False


def _is_enum_path(text: str, enum_types: list[str]) -> bool:
    return any(
        text == enum_type
        or text.startswith(enum_type + ".")
        or ("." + enum_type + ".") in text
        for enum_type in enum_types
    )


def value_kind(node: ast.AST, enum_types: list[str]) -> str:
    if isinstance(node, ast.Constant):
        if node.value is None:
            return "NONE"
        if isinstance(node.value, str):
            return "RAW_STRING"
        return "DYNAMIC"
    text = dotted_name(node)
    if text and text.endswith(".value") and _is_enum_path(text, enum_types):
        return "ENUM_VALUE"
    if text and _is_enum_path(text, enum_types):
        return "ENUM_MEMBER"
    return "DYNAMIC"


def _source_text(source: str, node: ast.AST) -> str:
    return ast.get_source_segment(source, node) or ""


def _iter_compare_values(node: ast.Compare, field: str) -> list[ast.AST]:
    values: list[ast.AST] = []
    if is_field(node.left, field):
        values.extend(node.comparators)
    for index, comparator in enumerate(node.comparators):
        if is_field(comparator, field):
            values.append(node.left if index == 0 else node.comparators[index - 1])
    expanded: list[ast.AST] = []
    for value in values:
        if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
            expanded.extend(value.elts)
        else:
            expanded.append(value)
    return expanded


def scan_file(path: Path, root: Path, spec: dict) -> tuple[list[Usage], list[str]]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        return [], [f"{path.relative_to(root).as_posix()}: {exc}"]

    field = spec["field_name"]
    enum_types = spec["enum_types"]
    usages: list[Usage] = []

    def add(node: ast.AST, value: ast.AST, context: str) -> None:
        usages.append(
            Usage(
                file=path.relative_to(root).as_posix(),
                line=getattr(node, "lineno", 0),
                context=context,
                expression=_source_text(source, node),
                value_kind=value_kind(value, enum_types),
                value_text=_source_text(source, value),
            )
        )

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if is_field(target, field):
                    add(node, node.value, "ASSIGN")
        elif isinstance(node, ast.AnnAssign):
            if is_field(node.target, field) and node.value is not None:
                add(node, node.value, "ASSIGN")
        elif isinstance(node, ast.Compare):
            for value in _iter_compare_values(node, field):
                add(node, value, "COMPARE")
    return usages, []


def _allowed(kind: str, spec: dict) -> bool:
    if kind == "NONE":
        return spec["allow_none"]
    if kind == "DYNAMIC":
        return spec["allow_dynamic"]
    if spec["canonical_representation"] == "ENUM_MEMBER":
        return kind == "ENUM_MEMBER"
    if kind == "ENUM_VALUE":
        return True
    return kind == "RAW_STRING" and spec["allow_raw_string_literals"]


def audit_tree(root: Path, spec: dict) -> dict:
    normalized = normalize_spec(spec)
    root = root.resolve()
    if not root.is_dir():
        raise ClassificationContractError(f"Raiz inválida: {root}")

    usages: list[Usage] = []
    errors: list[str] = []
    for path in sorted(root.rglob("*.py")):
        if any(part in {".venv", "venv", "__pycache__"} for part in path.parts):
            continue
        found, file_errors = scan_file(path, root, normalized)
        usages.extend(found)
        errors.extend(file_errors)

    findings = []
    for usage in usages:
        if not _allowed(usage.value_kind, normalized):
            findings.append(
                {
                    "code": "INCOMPATIBLE_REPRESENTATION",
                    "severity": "block",
                    **asdict(usage),
                    "expected": normalized["canonical_representation"],
                }
            )

    kinds = sorted(set(item.value_kind for item in usages))
    semantic_kinds = set(kinds) & {"RAW_STRING", "ENUM_MEMBER", "ENUM_VALUE"}
    if "ENUM_MEMBER" in semantic_kinds and (
        "RAW_STRING" in semantic_kinds or "ENUM_VALUE" in semantic_kinds
    ):
        findings.append(
            {
                "code": "MIXED_ENUM_AND_STRING_REPRESENTATION",
                "severity": "block",
                "kinds": sorted(semantic_kinds),
            }
        )
    if errors:
        findings.append(
            {"code": "PARSE_ERRORS", "severity": "block", "count": len(errors)}
        )

    return {
        "version": 1,
        "mode": "STATIC_CONTRACT_AUDIT_NO_AUTOFIX",
        "policy": normalized,
        "summary": {
            "usages": len(usages),
            "kinds": kinds,
            "parse_errors": len(errors),
            "blocking_findings": len(findings),
        },
        "usages": [asdict(item) for item in usages],
        "errors": errors,
        "findings": findings,
        "static_ok": len(findings) == 0,
        "autofix_performed": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audita contrato string/Enum de classificacao_inativacao sem alterar código."
    )
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("CLASSIFICACAO_INATIVACAO_AUDIT.json"),
    )
    args = parser.parse_args()
    try:
        report = audit_tree(args.root, load_spec(args.spec))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except ClassificationContractError as exc:
        print(f"CLASSIFICACAO_INATIVACAO_ERRO: {exc}", file=sys.stderr)
        return 2

    print(
        "CLASSIFICACAO_INATIVACAO_OK"
        if report["static_ok"]
        else "CLASSIFICACAO_INATIVACAO_DIVERGENTE"
    )
    print(f"Usos: {report['summary']['usages']}")
    print(f"Achados: {report['summary']['blocking_findings']}")
    print("Autofix: NÃO")
    return 0 if report["static_ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
