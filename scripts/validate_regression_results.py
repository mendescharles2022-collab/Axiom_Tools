from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

STATUSES = {"PASS", "FAIL", "NOT_RUN", "BLOCKED"}


class RegressionValidationError(RuntimeError):
    pass


def canonical_hash(obj: object) -> str:
    payload = json.dumps(
        obj,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RegressionValidationError(f"JSON inválido {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RegressionValidationError(f"JSON deve ser objeto: {path}")
    return data


def validate_registry(registry: dict) -> dict:
    if registry.get("version") != 1:
        raise RegressionValidationError("Registry version inválida.")
    required = registry.get("required_cases")
    if not isinstance(required, list) or len(required) != 28:
        raise RegressionValidationError(
            "Registry deve conter exatamente 28 required_cases."
        )

    ids = []
    numbers = []
    for item in required:
        if not isinstance(item, dict):
            raise RegressionValidationError("Caso inválido no registry.")
        ids.append(str(item.get("case_id", "")))
        numbers.append(item.get("number"))
        for field in (
            "case_id",
            "number",
            "client",
            "mechanism",
            "expected_result",
        ):
            if item.get(field) in (None, ""):
                raise RegressionValidationError(
                    f"Campo ausente no registry: {field}"
                )

    if (
        len(set(ids)) != 28
        or len(set(numbers)) != 28
        or sorted(numbers) != list(range(1, 29))
    ):
        raise RegressionValidationError(
            "IDs/números dos 28 casos são inválidos ou duplicados."
        )

    return {"ids": ids, "hash": canonical_hash(registry)}


def validate_results(
    registry: dict,
    results: dict,
    final_mode: bool = False,
) -> dict:
    metadata = validate_registry(registry)
    entries = results.get("results")
    if not isinstance(entries, list):
        raise RegressionValidationError("results deve conter lista results.")
    if results.get("registry_sha256") != metadata["hash"]:
        raise RegressionValidationError(
            "registry_sha256 não corresponde ao registry canônico."
        )

    by_id = {}
    unknown = []
    for item in entries:
        if not isinstance(item, dict):
            raise RegressionValidationError("Resultado inválido.")
        case_id = str(item.get("case_id", "")).strip()
        if case_id in by_id:
            raise RegressionValidationError(
                f"Resultado duplicado: {case_id}"
            )
        if case_id not in metadata["ids"]:
            unknown.append(case_id)

        status = str(item.get("status", "")).upper()
        if status not in STATUSES:
            raise RegressionValidationError(
                f"Status inválido em {case_id}: {status}"
            )

        evidence = item.get("evidence", [])
        if not isinstance(evidence, list) or not all(
            isinstance(value, str) and value.strip() for value in evidence
        ):
            raise RegressionValidationError(
                f"Evidence inválida em {case_id}."
            )
        if status == "PASS" and not evidence:
            raise RegressionValidationError(
                f"PASS sem evidência: {case_id}"
            )

        by_id[case_id] = {
            "status": status,
            "evidence_count": len(evidence),
            "notes": str(item.get("notes", "")),
        }

    if unknown:
        raise RegressionValidationError(
            "Casos desconhecidos: " + ", ".join(unknown)
        )

    missing = [case_id for case_id in metadata["ids"] if case_id not in by_id]
    status_counts = {
        status: sum(
            1 for item in by_id.values() if item["status"] == status
        )
        for status in sorted(STATUSES)
    }
    complete = not missing
    final_ok = complete and status_counts["PASS"] == 28

    if final_mode and not final_ok:
        raise RegressionValidationError(
            "Regressão final incompleta: "
            f"missing={len(missing)} statuses={status_counts}"
        )

    return {
        "registry_sha256": metadata["hash"],
        "required": 28,
        "submitted": len(by_id),
        "missing": missing,
        "status_counts": status_counts,
        "complete": complete,
        "final_ok": final_ok,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Valida cobertura/evidência da regressão canônica V8 de 08/2026."
        )
    )
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--final", action="store_true")
    parser.add_argument(
        "--output", type=Path, default=Path("REGRESSION_VALIDATION.json")
    )
    args = parser.parse_args()

    try:
        report = validate_results(
            load_json(args.registry),
            load_json(args.results),
            args.final,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
            + "\n",
            encoding="utf-8",
        )
    except RegressionValidationError as exc:
        print(f"REGRESSION_VALIDATION_ERRO: {exc}", file=sys.stderr)
        return 2

    print("REGRESSION_VALIDATION_OK")
    print(f"Submetidos: {report['submitted']}/28")
    print(f"Final OK: {report['final_ok']}")
    print(f"Relatório: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
