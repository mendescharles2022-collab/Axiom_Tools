from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

WRITE_SQL_RE = re.compile(r"\b(DELETE\s+FROM|UPDATE|INSERT\s+INTO|REPLACE\s+INTO)\s+([A-Za-z_][A-Za-z0-9_]*)", re.I)
DELETE_SQL_RE = re.compile(r"\bDELETE\s+FROM\s+([A-Za-z_][A-Za-z0-9_]*)", re.I)


class ContractError(RuntimeError):
    pass


@dataclass(frozen=True)
class FunctionInfo:
    file: str
    name: str
    lineno: int
    end_lineno: int
    identifiers: tuple[str, ...]
    string_literals: tuple[str, ...]
    commit_lines: tuple[int, ...]
    candidate_lines: tuple[int, ...]
    promotion_lines: tuple[int, ...]
    recalc_lines: tuple[int, ...]
    destructive_deletes: tuple[dict, ...]


def _ident(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _ident(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return ""


def _contains_marker(text: str, markers: tuple[str, ...]) -> bool:
    low = text.lower()
    return any(marker.lower() in low for marker in markers)


def _collect_function(path: Path, root: Path, node: ast.FunctionDef | ast.AsyncFunctionDef, policy: dict) -> FunctionInfo:
    candidate_markers = tuple(policy.get("candidate_markers", ["candidato", "candidate"]))
    promotion_markers = tuple(policy.get("promotion_markers", ["promover", "promote"]))
    recalc_markers = tuple(policy.get("recalc_markers", ["recalcular", "conferencia", "recompute"]))
    current_tables = {str(x).lower() for x in policy.get("current_tables", [])}

    identifiers: list[str] = []
    strings: list[str] = []
    commit_lines: list[int] = []
    candidate_lines: list[int] = []
    promotion_lines: list[int] = []
    recalc_lines: list[int] = []
    destructive: list[dict] = []

    for sub in ast.walk(node):
        if isinstance(sub, (ast.Name, ast.Attribute)):
            value = _ident(sub)
            if value:
                identifiers.append(value)
                if _contains_marker(value, candidate_markers):
                    candidate_lines.append(getattr(sub, "lineno", node.lineno))
                if _contains_marker(value, promotion_markers):
                    promotion_lines.append(getattr(sub, "lineno", node.lineno))
                if _contains_marker(value, recalc_markers):
                    recalc_lines.append(getattr(sub, "lineno", node.lineno))
        elif isinstance(sub, ast.Call):
            call_name = _ident(sub.func)
            if call_name.lower().endswith(".commit") or call_name.lower() == "commit":
                commit_lines.append(getattr(sub, "lineno", node.lineno))
        elif isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            text = sub.value
            strings.append(text)
            line = getattr(sub, "lineno", node.lineno)
            if _contains_marker(text, candidate_markers):
                candidate_lines.append(line)
            if _contains_marker(text, promotion_markers):
                promotion_lines.append(line)
            if _contains_marker(text, recalc_markers):
                recalc_lines.append(line)
            for match in DELETE_SQL_RE.finditer(text):
                table = match.group(1)
                if not current_tables or table.lower() in current_tables:
                    destructive.append({"line": line, "table": table, "sql": "DELETE FROM"})

    return FunctionInfo(
        file=path.relative_to(root).as_posix(),
        name=node.name,
        lineno=node.lineno,
        end_lineno=getattr(node, "end_lineno", node.lineno),
        identifiers=tuple(sorted(set(identifiers))),
        string_literals=tuple(strings),
        commit_lines=tuple(sorted(set(commit_lines))),
        candidate_lines=tuple(sorted(set(candidate_lines))),
        promotion_lines=tuple(sorted(set(promotion_lines))),
        recalc_lines=tuple(sorted(set(recalc_lines))),
        destructive_deletes=tuple(destructive),
    )


def audit(root: Path, policy: dict) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise ContractError(f"Raiz inválida: {root}")

    name_patterns = tuple(str(x).lower() for x in policy.get("reprocess_name_patterns", ["reprocess"]))
    require_target = bool(policy.get("require_target", True))
    require_candidate = bool(policy.get("require_candidate", True))
    require_promotion = bool(policy.get("require_promotion", True))
    require_recalc_after_promotion = bool(policy.get("require_recalc_after_promotion", True))

    targets: list[FunctionInfo] = []
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
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if any(pattern in node.name.lower() for pattern in name_patterns):
                targets.append(_collect_function(path, root, node, policy))

    findings: list[dict] = []
    for error in parse_errors:
        findings.append({"code": "PARSE_ERROR", **error})

    if require_target and not targets:
        findings.append({"code": "NO_REPROCESS_TARGET", "message": "Nenhuma função de reprocessamento foi localizada."})

    for fn in targets:
        for item in fn.destructive_deletes:
            findings.append({
                "code": "DESTRUCTIVE_CURRENT_DELETE",
                "file": fn.file,
                "function": fn.name,
                **item,
            })
        if require_candidate and not fn.candidate_lines:
            findings.append({
                "code": "MISSING_CANDIDATE_FLOW",
                "file": fn.file,
                "function": fn.name,
                "line": fn.lineno,
            })
        if require_promotion and not fn.promotion_lines:
            findings.append({
                "code": "MISSING_PROMOTION_STEP",
                "file": fn.file,
                "function": fn.name,
                "line": fn.lineno,
            })
        if fn.commit_lines and fn.candidate_lines and min(fn.commit_lines) < min(fn.candidate_lines):
            findings.append({
                "code": "COMMIT_BEFORE_CANDIDATE",
                "file": fn.file,
                "function": fn.name,
                "line": min(fn.commit_lines),
            })
        if require_recalc_after_promotion and fn.promotion_lines:
            if not fn.recalc_lines or min(fn.recalc_lines) <= min(fn.promotion_lines):
                findings.append({
                    "code": "RECALC_NOT_AFTER_PROMOTION",
                    "file": fn.file,
                    "function": fn.name,
                    "line": fn.lineno,
                })

    return {
        "version": 1,
        "audit": "B01_REPROCESSING_CANDIDATE_CONTRACT",
        "all_ok": not findings,
        "target_count": len(targets),
        "targets": [
            {
                "file": fn.file,
                "function": fn.name,
                "line": fn.lineno,
                "candidate_lines": list(fn.candidate_lines),
                "promotion_lines": list(fn.promotion_lines),
                "recalc_lines": list(fn.recalc_lines),
                "commit_lines": list(fn.commit_lines),
                "destructive_delete_count": len(fn.destructive_deletes),
            }
            for fn in targets
        ],
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita o contrato B01 de reprocessamento por candidato.")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        policy = json.loads(args.policy.read_text(encoding="utf-8"))
        report = audit(args.root, policy)
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        print(f"B01_AUDIT_ERROR: {exc}", file=sys.stderr)
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
