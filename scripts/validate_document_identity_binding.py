from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

DIGITS_RE = re.compile(r"\D+")


class IdentityBindingError(RuntimeError):
    pass


def _digits(value: object) -> str:
    return DIGITS_RE.sub("", str(value or ""))


def _text(value: object) -> str:
    return str(value or "").strip()


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def validate(records: list[dict], policy: dict | None = None) -> dict:
    policy = policy or {}
    min_binding_confidence = float(policy.get("min_binding_confidence", 0.80))
    if min_binding_confidence < 0 or min_binding_confidence > 1:
        raise IdentityBindingError("min_binding_confidence deve ficar entre 0 e 1.")

    findings: list[dict] = []
    normalized: list[dict] = []
    ids: set[str] = set()

    for raw in records:
        if not isinstance(raw, dict):
            raise IdentityBindingError("Cada documento deve ser um objeto JSON.")
        document_id = _text(raw.get("document_id"))
        if not document_id:
            raise IdentityBindingError("document_id é obrigatório.")
        if document_id in ids:
            findings.append({"code": "DUPLICATE_DOCUMENT_ID", "document_id": document_id})
        ids.add(document_id)

        discovered = bool(raw.get("discovered", False))
        indexed = bool(raw.get("indexed", False))
        conference_eligible = bool(raw.get("conference_eligible", False))
        client_id = _text(raw.get("client_id"))
        binding_method = _text(raw.get("binding_method"))
        binding_evidence = _text(raw.get("binding_evidence"))
        try:
            confidence = float(raw.get("binding_confidence", 0))
        except (TypeError, ValueError) as exc:
            raise IdentityBindingError(f"binding_confidence inválida em {document_id}.") from exc
        if confidence < 0 or confidence > 1:
            raise IdentityBindingError(f"binding_confidence fora de 0..1 em {document_id}.")

        extracted = raw.get("extracted_identity") or {}
        client = raw.get("client_identity") or {}
        if not isinstance(extracted, dict) or not isinstance(client, dict):
            raise IdentityBindingError(f"Identidades devem ser objetos em {document_id}.")

        requires_unit_identity = bool(raw.get("requires_unit_identity", False))
        unit_kind = _text(raw.get("unit_identity_kind")).upper()
        extracted_unit = _digits(raw.get("extracted_unit_identity"))
        client_units = {_digits(x) for x in (raw.get("client_unit_identities") or []) if _digits(x)}

        record = {
            "document_id": document_id,
            "discovered": discovered,
            "indexed": indexed,
            "conference_eligible": conference_eligible,
            "client_id": client_id,
            "binding_method": binding_method,
            "binding_evidence": binding_evidence,
            "binding_confidence": confidence,
            "requires_unit_identity": requires_unit_identity,
            "unit_identity_kind": unit_kind or None,
            "extracted_unit_identity": extracted_unit or None,
            "client_unit_identities": sorted(client_units),
        }
        normalized.append(record)

        if conference_eligible and not discovered:
            findings.append({"code": "CONFERENCE_DOCUMENT_NOT_DISCOVERED", "document_id": document_id})
        if conference_eligible and not indexed:
            findings.append({"code": "CONFERENCE_DOCUMENT_NOT_INDEXED", "document_id": document_id})
        if conference_eligible and not client_id:
            findings.append({"code": "CONFERENCE_DOCUMENT_WITHOUT_CLIENT_BINDING", "document_id": document_id})
        if conference_eligible and (not binding_method or not binding_evidence):
            findings.append({"code": "BINDING_PROVENANCE_MISSING", "document_id": document_id})
        if conference_eligible and confidence < min_binding_confidence:
            findings.append({
                "code": "BINDING_CONFIDENCE_BELOW_POLICY",
                "document_id": document_id,
                "confidence": confidence,
                "minimum": min_binding_confidence,
            })

        extracted_cpf = _digits(extracted.get("cpf"))
        client_cpf = _digits(client.get("cpf"))
        extracted_cnpj = _digits(extracted.get("cnpj"))
        client_cnpj = _digits(client.get("cnpj"))
        extracted_caepf = _digits(extracted.get("caepf"))
        client_caepfs = {_digits(x) for x in (client.get("caepf") if isinstance(client.get("caepf"), list) else [client.get("caepf")]) if _digits(x)}

        if extracted_cpf and client_cpf and extracted_cpf != client_cpf:
            findings.append({"code": "CPF_BINDING_MISMATCH", "document_id": document_id})
        if extracted_cnpj and client_cnpj and extracted_cnpj != client_cnpj:
            findings.append({"code": "CNPJ_BINDING_MISMATCH", "document_id": document_id})
        if extracted_caepf and client_caepfs and extracted_caepf not in client_caepfs:
            findings.append({"code": "CAEPF_BINDING_MISMATCH", "document_id": document_id})

        if requires_unit_identity:
            if not unit_kind:
                findings.append({"code": "UNIT_IDENTITY_KIND_MISSING", "document_id": document_id})
            if not extracted_unit:
                findings.append({"code": "EXTRACTED_UNIT_IDENTITY_MISSING", "document_id": document_id})
            if not client_units:
                findings.append({"code": "CLIENT_UNIT_IDENTITY_MISSING", "document_id": document_id})
            if extracted_unit and client_units and extracted_unit not in client_units:
                findings.append({
                    "code": "UNIT_IDENTITY_BINDING_MISMATCH",
                    "document_id": document_id,
                    "unit_identity_kind": unit_kind or None,
                })

        # PF rural/CAEPF: CPF pode identificar a pessoa, mas não substitui a unidade operacional.
        if requires_unit_identity and unit_kind == "CAEPF":
            if not client_cpf:
                findings.append({"code": "RURAL_PF_CLIENT_CPF_MISSING", "document_id": document_id})
            if not extracted_cpf:
                findings.append({"code": "RURAL_PF_EXTRACTED_CPF_MISSING", "document_id": document_id})
            if extracted_cpf and client_cpf and extracted_cpf == client_cpf and not extracted_unit:
                findings.append({"code": "CPF_MATCH_WITHOUT_REQUIRED_CAEPF", "document_id": document_id})

    report = {
        "version": 1,
        "audit": "B15_B16_DISCOVERY_IDENTITY_BINDING",
        "all_ok": not findings,
        "document_count": len(normalized),
        "documents": normalized,
        "findings": findings,
    }
    report["report_sha256"] = _canonical_hash(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida descoberta→índice→identidade→vínculo sem mutar o acervo.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        records = payload.get("documents", payload) if isinstance(payload, dict) else payload
        if not isinstance(records, list):
            raise IdentityBindingError("Entrada deve ser lista ou objeto com chave documents.")
        policy = json.loads(args.policy.read_text(encoding="utf-8")) if args.policy else {}
        report = validate(records, policy)
    except (OSError, json.JSONDecodeError, IdentityBindingError) as exc:
        print(f"IDENTITY_BINDING_ERROR: {exc}", file=sys.stderr)
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
