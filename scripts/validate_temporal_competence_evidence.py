from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

SPEC_VERSION = 1
COMPETENCE_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
RULES = {"SAME_MONTH_AS_BASIS_DATE"}


class TemporalCompetenceError(RuntimeError):
    pass


def _strings(value: object, field: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or (not value and not allow_empty) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise TemporalCompetenceError(f"{field} deve ser lista de strings.")
    return [item.strip() for item in value]


def normalize_spec(spec: dict) -> dict:
    if not isinstance(spec, dict) or spec.get("version") != SPEC_VERSION:
        raise TemporalCompetenceError(f"Spec deve ser objeto version={SPEC_VERSION}.")
    rule = str(spec.get("competence_rule") or "").strip().upper()
    if rule not in RULES:
        raise TemporalCompetenceError(
            "competence_rule suportada: SAME_MONTH_AS_BASIS_DATE."
        )
    basis_field = str(spec.get("basis_date_field") or "").strip()
    if not basis_field or not basis_field.isidentifier():
        raise TemporalCompetenceError(f"basis_date_field inválido: {basis_field!r}")
    competence_field = str(spec.get("competence_field") or "competencia").strip()
    method_field = str(spec.get("method_field") or "competencia_metodo").strip()
    evidence_field = str(spec.get("evidence_field") or "competencia_evidencias").strip()
    for field_name, field_value in [
        ("competence_field", competence_field),
        ("method_field", method_field),
        ("evidence_field", evidence_field),
    ]:
        if not field_value.isidentifier():
            raise TemporalCompetenceError(f"{field_name} inválido: {field_value!r}")
    return {
        "version": SPEC_VERSION,
        "document_types": _strings(spec.get("document_types"), "document_types"),
        "document_type_field": str(
            spec.get("document_type_field") or "tipo_documento"
        ).strip(),
        "basis_date_field": basis_field,
        "competence_field": competence_field,
        "method_field": method_field,
        "evidence_field": evidence_field,
        "allowed_methods": _strings(spec.get("allowed_methods"), "allowed_methods"),
        "required_evidence_tokens": _strings(
            spec.get("required_evidence_tokens", []),
            "required_evidence_tokens",
            allow_empty=True,
        ),
        "competence_rule": rule,
        "allow_non_target_records": spec.get("allow_non_target_records", True) is True,
    }


def load_spec(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise TemporalCompetenceError(f"Spec inexistente: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TemporalCompetenceError(f"Spec inválida: {exc}") from exc
    return normalize_spec(data)


def load_records(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise TemporalCompetenceError(f"Arquivo de registros inexistente: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TemporalCompetenceError(f"Registros inválidos: {exc}") from exc
    if isinstance(data, dict):
        data = data.get("records")
    if not isinstance(data, list):
        raise TemporalCompetenceError("Registros devem ser lista ou objeto com lista 'records'.")
    if not all(isinstance(item, dict) for item in data):
        raise TemporalCompetenceError("Cada registro deve ser objeto JSON.")
    return data


def _parse_iso_date(raw: object) -> date | None:
    if not isinstance(raw, str):
        return None
    text = raw.strip()
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _expected_competence(basis: date, rule: str) -> str:
    if rule == "SAME_MONTH_AS_BASIS_DATE":
        return f"{basis.year:04d}-{basis.month:02d}"
    raise AssertionError(rule)


def validate_records(records: list[dict], spec: dict) -> dict:
    policy = normalize_spec(spec)
    target_types = set(policy["document_types"])
    findings: list[dict] = []
    checked = 0
    skipped = 0

    for index, record in enumerate(records):
        document_type = str(record.get(policy["document_type_field"]) or "").strip()
        if document_type not in target_types:
            if policy["allow_non_target_records"]:
                skipped += 1
                continue
            findings.append(
                {
                    "code": "UNEXPECTED_DOCUMENT_TYPE",
                    "severity": "block",
                    "index": index,
                    "document_type": document_type,
                }
            )
            continue

        checked += 1
        basis_raw = record.get(policy["basis_date_field"])
        basis = _parse_iso_date(basis_raw)
        if basis is None:
            findings.append(
                {
                    "code": "MISSING_OR_INVALID_TEMPORAL_BASIS",
                    "severity": "block",
                    "index": index,
                    "field": policy["basis_date_field"],
                    "value": basis_raw,
                }
            )
            continue

        expected = _expected_competence(basis, policy["competence_rule"])
        competence = str(record.get(policy["competence_field"]) or "").strip()
        if not COMPETENCE_RE.fullmatch(competence):
            findings.append(
                {
                    "code": "MISSING_OR_INVALID_COMPETENCE",
                    "severity": "block",
                    "index": index,
                    "value": competence,
                }
            )
        elif competence != expected:
            findings.append(
                {
                    "code": "TEMPORAL_COMPETENCE_MISMATCH",
                    "severity": "block",
                    "index": index,
                    "basis_date": basis.isoformat(),
                    "expected_competence": expected,
                    "actual_competence": competence,
                }
            )

        method = str(record.get(policy["method_field"]) or "").strip()
        if method not in set(policy["allowed_methods"]):
            findings.append(
                {
                    "code": "INVALID_COMPETENCE_METHOD",
                    "severity": "block",
                    "index": index,
                    "value": method,
                    "allowed": policy["allowed_methods"],
                }
            )

        evidence = record.get(policy["evidence_field"])
        if not isinstance(evidence, list) or not all(
            isinstance(item, str) and item.strip() for item in evidence
        ):
            findings.append(
                {
                    "code": "MISSING_TEMPORAL_EVIDENCE",
                    "severity": "block",
                    "index": index,
                }
            )
            continue
        evidence_text = "\n".join(evidence).lower()
        missing_tokens = [
            token
            for token in policy["required_evidence_tokens"]
            if token.lower() not in evidence_text
        ]
        if missing_tokens:
            findings.append(
                {
                    "code": "TEMPORAL_EVIDENCE_INCOMPLETE",
                    "severity": "block",
                    "index": index,
                    "missing_tokens": missing_tokens,
                }
            )

    if checked == 0:
        findings.append(
            {
                "code": "NO_TARGET_RECORDS",
                "severity": "block",
                "document_types": policy["document_types"],
            }
        )

    return {
        "version": 1,
        "mode": "TEMPORAL_COMPETENCE_EVIDENCE_VALIDATION",
        "policy": policy,
        "summary": {
            "records": len(records),
            "target_records_checked": checked,
            "non_target_records_skipped": skipped,
            "blocking_findings": len(findings),
        },
        "findings": findings,
        "ok": len(findings) == 0,
        "parser_modified": False,
        "disclaimer": (
            "A regra temporal é declarada pela política. Este validador não inventa regra tributária; "
            "ele prova se o resultado do parser está coerente com a base temporal configurada e com a evidência registrada."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida competência temporal e proveniência de resultados de parser."
    )
    parser.add_argument("--records", required=True, type=Path)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument(
        "--output", type=Path, default=Path("TEMPORAL_COMPETENCE_REPORT.json")
    )
    args = parser.parse_args()
    try:
        report = validate_records(load_records(args.records), load_spec(args.spec))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except TemporalCompetenceError as exc:
        print(f"TEMPORAL_COMPETENCE_ERRO: {exc}", file=sys.stderr)
        return 2
    print(
        "TEMPORAL_COMPETENCE_OK"
        if report["ok"]
        else "TEMPORAL_COMPETENCE_DIVERGENTE"
    )
    print(f"Registros-alvo: {report['summary']['target_records_checked']}")
    print(f"Achados: {report['summary']['blocking_findings']}")
    print("Parser modificado: NÃO")
    return 0 if report["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
