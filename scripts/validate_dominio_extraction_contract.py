from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


class DominioContractError(RuntimeError):
    pass


def _text(value: object) -> str:
    return str(value or "").strip()


def _money(value: object, *, optional: bool = False) -> Decimal | None:
    if value is None and optional:
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise DominioContractError(f"Valor inválido: {value!r}") from exc
    if not result.is_finite():
        raise DominioContractError(f"Valor não finito: {value!r}")
    return result.quantize(Decimal("0.01"))


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def _validate_provenance(field_name: str, field: dict, findings: list[dict]) -> None:
    required = ["source", "section", "label", "page", "rule"]
    missing = [key for key in required if field.get(key) in (None, "")]
    if missing:
        findings.append({"code": "FIELD_PROVENANCE_INCOMPLETE", "field": field_name, "missing": missing})


def validate(record: dict, policy: dict | None = None) -> dict:
    if not isinstance(record, dict):
        raise DominioContractError("Extração deve ser objeto JSON.")
    policy = policy or {}
    tolerance = _money(policy.get("money_tolerance", "0.02")) or Decimal("0.02")

    document = _text(record.get("document"))
    competence = _text(record.get("competence"))
    competence_method = _text(record.get("competence_method"))
    competence_evidence = _text(record.get("competence_evidence"))
    if not document or not competence:
        raise DominioContractError("document e competence são obrigatórios.")

    findings: list[dict] = []
    if not competence_method or not competence_evidence:
        findings.append({"code": "COMPETENCE_PROVENANCE_MISSING"})

    people = record.get("people", [])
    if not isinstance(people, list):
        raise DominioContractError("people deve ser lista.")

    employees = 0
    contributors = 0
    employee_fgts_sum = Decimal("0.00")
    employee_fgts_known = True

    for index, person in enumerate(people):
        if not isinstance(person, dict):
            raise DominioContractError("Pessoa deve ser objeto JSON.")
        line_type = _text(person.get("line_type")).upper()
        link = _text(person.get("link")).upper()
        category = _text(person.get("category")).upper()
        situation = _text(person.get("situation")).upper()
        fgts = _money(person.get("fgts"), optional=True)

        is_director = "DIRETOR" in link
        is_contributor_line = line_type.startswith("CONTR")
        is_employee_line = line_type.startswith("EMPR")

        if is_director and category == "EMPREGADO":
            findings.append({"code": "DIRECTOR_CLASSIFIED_AS_EMPLOYEE", "person_index": index})
        if is_contributor_line and category == "EMPREGADO":
            findings.append({"code": "CONTRIBUTOR_LINE_CLASSIFIED_AS_EMPLOYEE", "person_index": index})
        if situation == "TRABALHANDO" and is_director and category == "EMPREGADO":
            findings.append({"code": "WORKING_STATUS_USED_AS_EMPLOYMENT_CATEGORY", "person_index": index})
        if is_employee_line and category not in {"EMPREGADO", "EMPLOYEE"}:
            findings.append({"code": "EMPLOYEE_LINE_NOT_CLASSIFIED_AS_EMPLOYEE", "person_index": index})

        if category in {"EMPREGADO", "EMPLOYEE"}:
            employees += 1
            if fgts is None:
                employee_fgts_known = False
            else:
                employee_fgts_sum += fgts
        elif category in {"CONTRIBUINTE", "CONTRIBUTOR"}:
            contributors += 1

    aggregates = record.get("aggregates", {}) or {}
    if not isinstance(aggregates, dict):
        raise DominioContractError("aggregates deve ser objeto JSON.")
    declared_employees = aggregates.get("employees")
    declared_contributors = aggregates.get("contributors")
    if declared_employees is not None and int(declared_employees) != employees:
        findings.append({"code": "EMPLOYEE_COUNT_MISMATCH", "declared": int(declared_employees), "derived": employees})
    if declared_contributors is not None and int(declared_contributors) != contributors:
        findings.append({"code": "CONTRIBUTOR_COUNT_MISMATCH", "declared": int(declared_contributors), "derived": contributors})

    fgts_field = record.get("fgts_monthly", {}) or {}
    if not isinstance(fgts_field, dict):
        raise DominioContractError("fgts_monthly deve ser objeto JSON.")
    if fgts_field:
        _validate_provenance("fgts_monthly", fgts_field, findings)
        fgts_value = _money(fgts_field.get("value"), optional=True)
        source = _text(fgts_field.get("source")).upper()
        if source and source != "INSS_FGTS_PIS_ISS_VALOR_FGTS":
            findings.append({"code": "FGTS_NONAUTHORITATIVE_SOURCE", "source": source})
        if fgts_value is not None and employee_fgts_known and abs(fgts_value - employee_fgts_sum) > tolerance:
            findings.append({
                "code": "FGTS_INDIVIDUAL_AGGREGATE_MISMATCH",
                "aggregate": format(fgts_value, ".2f"),
                "individual_sum": format(employee_fgts_sum, ".2f"),
            })

    federal_field = record.get("federal_balance", {}) or {}
    if not isinstance(federal_field, dict):
        raise DominioContractError("federal_balance deve ser objeto JSON.")
    if not federal_field:
        findings.append({"code": "FEDERAL_AUTHORITATIVE_FIELD_MISSING"})
    else:
        _validate_provenance("federal_balance", federal_field, findings)
        source = _text(federal_field.get("source")).upper()
        if source != "APURACAO_TRIBUTOS_FEDERAIS_SALDO":
            findings.append({"code": "FEDERAL_NONAUTHORITATIVE_SOURCE", "source": source})
        _money(federal_field.get("value"))

    result = {
        "version": 1,
        "audit": "B29_B30_B31_DOMINIO_EXTRACTION_CONTRACT",
        "all_ok": not findings,
        "document": document,
        "competence": competence,
        "derived_employees": employees,
        "derived_contributors": contributors,
        "employee_fgts_sum": format(employee_fgts_sum, ".2f") if employee_fgts_known else None,
        "findings": findings,
    }
    result["report_sha256"] = _canonical_hash(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida saída estruturada do parser Domínio contra contrato V8.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        record = json.loads(args.input.read_text(encoding="utf-8"))
        policy = json.loads(args.policy.read_text(encoding="utf-8")) if args.policy else {}
        report = validate(record, policy)
    except (OSError, json.JSONDecodeError, DominioContractError, ValueError) as exc:
        print(f"DOMINIO_CONTRACT_ERROR: {exc}", file=sys.stderr)
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
