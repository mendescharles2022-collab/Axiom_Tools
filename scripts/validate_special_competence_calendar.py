from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

COMP_RE = re.compile(r"^(0[1-9]|1[0-2]|13)/(20\d{2})$")
SPECIAL_KINDS = {"THIRTEENTH", "DECEMBER"}
EXPLICIT_METHODS = {"EXPLICITA_DOCUMENTO", "PERIODO_APURACAO_EXPLICITO"}
SPECIAL_INFERRED_METHODS = {"CALENDARIO_ESOCIAL_EXCECAO", "CALENDARIO_ESPECIAL"}


class CalendarError(RuntimeError):
    pass


def _text(value: object) -> str:
    return str(value or "").strip()


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def validate(records: list[dict]) -> dict:
    findings: list[dict] = []
    normalized: list[dict] = []
    identities: set[tuple[str, str, str]] = set()

    for raw in records:
        if not isinstance(raw, dict):
            raise CalendarError("Cada registro deve ser objeto JSON.")
        document_id = _text(raw.get("document_id"))
        client_id = _text(raw.get("client_id"))
        competence = _text(raw.get("competence"))
        kind = _text(raw.get("competence_kind")).upper()
        method = _text(raw.get("method")).upper()
        evidence = _text(raw.get("evidence"))
        rule_id = _text(raw.get("calendar_rule_id"))
        if not document_id or not client_id or not competence:
            raise CalendarError("document_id, client_id e competence são obrigatórios.")
        match = COMP_RE.fullmatch(competence)
        if not match:
            findings.append({"code": "INVALID_COMPETENCE_FORMAT", "document_id": document_id, "competence": competence})
            continue
        month = int(match.group(1))
        year = match.group(2)
        if not method or not evidence:
            findings.append({"code": "SPECIAL_COMPETENCE_PROVENANCE_MISSING", "document_id": document_id})

        if month == 13:
            if kind != "THIRTEENTH":
                findings.append({"code": "THIRTEENTH_MISCLASSIFIED_AS_NORMAL_MONTH", "document_id": document_id, "kind": kind})
            if method not in EXPLICIT_METHODS | SPECIAL_INFERRED_METHODS:
                findings.append({"code": "THIRTEENTH_WITH_GENERIC_CALENDAR_METHOD", "document_id": document_id, "method": method})
            if method in SPECIAL_INFERRED_METHODS and not rule_id:
                findings.append({"code": "THIRTEENTH_INFERENCE_WITHOUT_EXCEPTION_RULE", "document_id": document_id})
        elif month == 12:
            if kind not in {"DECEMBER", "NORMAL"}:
                findings.append({"code": "DECEMBER_KIND_INVALID", "document_id": document_id, "kind": kind})
            if method.startswith("CALENDARIO") and method not in SPECIAL_INFERRED_METHODS:
                findings.append({"code": "DECEMBER_WITH_GENERIC_CALENDAR_METHOD", "document_id": document_id, "method": method})
            if method in SPECIAL_INFERRED_METHODS and not rule_id:
                findings.append({"code": "DECEMBER_INFERENCE_WITHOUT_EXCEPTION_RULE", "document_id": document_id})
        else:
            if kind in SPECIAL_KINDS:
                findings.append({"code": "SPECIAL_KIND_ON_NORMAL_MONTH", "document_id": document_id, "kind": kind})

        identity_kind = "THIRTEENTH" if month == 13 else ("DECEMBER" if month == 12 and kind == "DECEMBER" else "NORMAL")
        identity = (client_id, year, identity_kind)
        if identity in identities:
            findings.append({"code": "DUPLICATE_SPECIAL_COMPETENCE_IDENTITY", "document_id": document_id, "identity": list(identity)})
        identities.add(identity)
        normalized.append({
            "document_id": document_id,
            "client_id": client_id,
            "competence": competence,
            "competence_kind": kind,
            "method": method,
            "calendar_rule_id": rule_id or None,
            "identity_kind": identity_kind,
        })

    report = {
        "version": 1,
        "audit": "B33_SPECIAL_COMPETENCE_CALENDAR",
        "all_ok": not findings,
        "records": normalized,
        "findings": findings,
    }
    report["report_sha256"] = _canonical_hash(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida competência especial dezembro/13º sem tratar 13 como mês comum.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        records = payload.get("records", payload) if isinstance(payload, dict) else payload
        if not isinstance(records, list):
            raise CalendarError("Entrada deve ser lista ou objeto com chave records.")
        report = validate(records)
    except (OSError, json.JSONDecodeError, CalendarError) as exc:
        print(f"SPECIAL_CALENDAR_ERROR: {exc}", file=sys.stderr)
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
