from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path


class StateSemanticsError(RuntimeError):
    pass


def _string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def audit(root: Path, policy: dict) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise StateSemanticsError(f"Raiz inválida: {root}")

    forbidden_mappings = list(policy.get("forbidden_mappings", []))
    forbidden_pairs = list(policy.get("forbidden_function_pairs", []))
    require_mapping_target = bool(policy.get("require_mapping_target", False))
    parse_errors: list[dict] = []
    findings: list[dict] = []
    mapping_target_count = 0

    for path in sorted(root.rglob("*.py")):
        if any(part in {".venv", "venv", "__pycache__"} for part in path.parts):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as exc:
            parse_errors.append({"file": path.relative_to(root).as_posix(), "error": str(exc)})
            continue

        rel = path.relative_to(root).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                for key_node, value_node in zip(node.keys, node.values):
                    key = _string(key_node) if key_node is not None else None
                    value = _string(value_node)
                    if key is None or value is None:
                        continue
                    mapping_target_count += 1
                    for rule in forbidden_mappings:
                        source = str(rule.get("source", ""))
                        target_regex = str(rule.get("target_regex", ""))
                        if key.upper() == source.upper() and re.search(target_regex, value, re.I):
                            findings.append({
                                "code": "FORBIDDEN_STATE_LABEL_MAPPING",
                                "file": rel,
                                "line": getattr(node, "lineno", 1),
                                "source": key,
                                "target": value,
                                "rule_id": rule.get("id"),
                            })

            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                literals = {
                    sub.value.upper()
                    for sub in ast.walk(node)
                    if isinstance(sub, ast.Constant) and isinstance(sub.value, str)
                }
                for rule in forbidden_pairs:
                    left = str(rule.get("left", "")).upper()
                    right = str(rule.get("right", "")).upper()
                    if left in literals and right in literals:
                        findings.append({
                            "code": "FORBIDDEN_STATE_COOCCURRENCE",
                            "file": rel,
                            "function": node.name,
                            "line": node.lineno,
                            "left": left,
                            "right": right,
                            "rule_id": rule.get("id"),
                        })

    findings = [{"code": "PARSE_ERROR", **item} for item in parse_errors] + findings
    if require_mapping_target and mapping_target_count == 0:
        findings.append({"code": "NO_STATE_MAPPING_TARGET", "message": "Nenhum mapeamento literal de estado foi localizado."})

    return {
        "version": 1,
        "audit": "B11_B37_STATE_SEMANTICS_CONTRACT",
        "all_ok": not findings,
        "mapping_target_count": mapping_target_count,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita semântica de estados B11/B37.")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        policy = json.loads(args.policy.read_text(encoding="utf-8"))
        report = audit(args.root, policy)
    except (OSError, json.JSONDecodeError, StateSemanticsError) as exc:
        print(f"STATE_SEMANTICS_AUDIT_ERROR: {exc}", file=sys.stderr)
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
