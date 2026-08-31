from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path


class UiContractError(RuntimeError):
    pass


def _relative_files(root: Path, globs: list[str]) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if any(fnmatch.fnmatch(rel, pattern) for pattern in globs):
            files.append(path)
    return sorted(set(files))


def _compile(pattern: str) -> re.Pattern[str]:
    try:
        return re.compile(pattern, re.I | re.M | re.S)
    except re.error as exc:
        raise UiContractError(f"Regex inválida: {pattern!r}: {exc}") from exc


def audit(root: Path, policy: dict) -> dict:
    root = root.resolve()
    if not root.is_dir():
        raise UiContractError(f"Raiz inválida: {root}")
    contracts = policy.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        raise UiContractError("policy.contracts deve ser lista não vazia.")

    findings: list[dict] = []
    results: list[dict] = []
    seen_ids: set[str] = set()

    for raw in contracts:
        if not isinstance(raw, dict):
            raise UiContractError("Cada contrato deve ser objeto JSON.")
        contract_id = str(raw.get("id") or "").strip()
        if not contract_id:
            raise UiContractError("Contrato sem id.")
        if contract_id in seen_ids:
            raise UiContractError(f"Contrato duplicado: {contract_id}")
        seen_ids.add(contract_id)

        globs = raw.get("globs")
        if not isinstance(globs, list) or not globs:
            raise UiContractError(f"{contract_id}: globs deve ser lista não vazia.")
        files = _relative_files(root, [str(x) for x in globs])
        min_files = int(raw.get("min_files", 1))
        if len(files) < min_files:
            findings.append({
                "code": "UI_CONTRACT_FILES_MISSING",
                "contract_id": contract_id,
                "matched_files": len(files),
                "minimum": min_files,
            })

        texts: list[tuple[str, str]] = []
        for path in files:
            rel = path.relative_to(root).as_posix()
            try:
                texts.append((rel, path.read_text(encoding="utf-8")))
            except UnicodeDecodeError:
                findings.append({"code": "UI_CONTRACT_NON_UTF8_FILE", "contract_id": contract_id, "file": rel})

        combined = "\n\n".join(f"### FILE:{rel}\n{text}" for rel, text in texts)
        local_findings_before = len(findings)

        for requirement in raw.get("require", []):
            if not isinstance(requirement, dict):
                raise UiContractError(f"{contract_id}: requirement inválido.")
            rule_id = str(requirement.get("rule_id") or "").strip() or "required"
            pattern = _compile(str(requirement.get("regex") or ""))
            minimum = int(requirement.get("min", 1))
            maximum = requirement.get("max")
            count = len(pattern.findall(combined))
            if count < minimum:
                findings.append({
                    "code": "UI_REQUIRED_PATTERN_MISSING",
                    "contract_id": contract_id,
                    "rule_id": rule_id,
                    "count": count,
                    "minimum": minimum,
                })
            if maximum is not None and count > int(maximum):
                findings.append({
                    "code": "UI_REQUIRED_PATTERN_TOO_MANY",
                    "contract_id": contract_id,
                    "rule_id": rule_id,
                    "count": count,
                    "maximum": int(maximum),
                })

        for any_group in raw.get("require_any", []):
            if not isinstance(any_group, dict):
                raise UiContractError(f"{contract_id}: require_any inválido.")
            rule_id = str(any_group.get("rule_id") or "").strip() or "required_any"
            patterns = any_group.get("regexes")
            if not isinstance(patterns, list) or not patterns:
                raise UiContractError(f"{contract_id}/{rule_id}: regexes deve ser lista não vazia.")
            matches = [p for p in patterns if _compile(str(p)).search(combined)]
            if not matches:
                findings.append({
                    "code": "UI_REQUIRED_ANY_PATTERN_MISSING",
                    "contract_id": contract_id,
                    "rule_id": rule_id,
                })

        for forbidden in raw.get("forbid", []):
            if not isinstance(forbidden, dict):
                raise UiContractError(f"{contract_id}: forbid inválido.")
            rule_id = str(forbidden.get("rule_id") or "").strip() or "forbidden"
            pattern = _compile(str(forbidden.get("regex") or ""))
            matches = pattern.findall(combined)
            if matches:
                findings.append({
                    "code": "UI_FORBIDDEN_PATTERN_FOUND",
                    "contract_id": contract_id,
                    "rule_id": rule_id,
                    "count": len(matches),
                })

        results.append({
            "contract_id": contract_id,
            "matched_files": [rel for rel, _ in texts],
            "ok": len(findings) == local_findings_before,
        })

    return {
        "version": 1,
        "audit": "B43_B44_B46_B47_OPERATIONAL_UI_CONTRACT",
        "all_ok": not findings,
        "contracts": results,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita contratos estáticos de UI operacional V8.")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        policy = json.loads(args.policy.read_text(encoding="utf-8"))
        report = audit(args.root, policy)
    except (OSError, json.JSONDecodeError, UiContractError, ValueError) as exc:
        print(f"UI_CONTRACT_ERROR: {exc}", file=sys.stderr)
        return 2
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
