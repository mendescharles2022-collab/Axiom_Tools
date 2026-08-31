from __future__ import annotations

import argparse
import hashlib
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

QUERY_RESULTS = {"COM_CONSIGNADO", "SEM_CONSIGNADO", "SEM_PROCURACAO", "ERRO_TECNICO"}
EXPECTED_STAGES = ["ECONSIGNADO", "DOMINIO", "ESOCIAL", "ECAC_DARF", "FGTS_DIGITAL", "CONFERENCIA"]


class EConsignadoError(RuntimeError):
    pass


def _text(value: object) -> str:
    return str(value or "").strip()


def _money(value: object) -> Decimal:
    try:
        result = Decimal(str(value or "0"))
    except (InvalidOperation, ValueError) as exc:
        raise EConsignadoError(f"Valor monetário inválido: {value!r}") from exc
    if not result.is_finite():
        raise EConsignadoError(f"Valor monetário não finito: {value!r}")
    return result.quantize(Decimal("0.01"))


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def validate(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise EConsignadoError("Payload deve ser objeto JSON.")
    competence = _text(payload.get("competence"))
    call = payload.get("call")
    orchestrator_command_id = _text(payload.get("orchestrator_command_id"))
    stages = [str(x).strip().upper() for x in payload.get("stages", [])]
    if not competence:
        raise EConsignadoError("competence é obrigatória.")

    findings: list[dict] = []

    if stages != EXPECTED_STAGES:
        findings.append({"code": "ORCHESTRATOR_STAGE_ORDER_INVALID", "expected": EXPECTED_STAGES, "received": stages})
    if not orchestrator_command_id:
        findings.append({"code": "ECONSIGNADO_NOT_BOUND_TO_ORCHESTRATOR_COMMAND"})

    eligible_list = [_text(x) for x in payload.get("eligible_client_ids", []) if _text(x)]
    queried_list = [_text(x) for x in payload.get("queried_client_ids", []) if _text(x)]
    eligible = set(eligible_list)
    queried = set(queried_list)
    if len(eligible_list) != len(eligible):
        findings.append({"code": "DUPLICATE_ELIGIBLE_CLIENT"})
    if len(queried_list) != len(queried):
        findings.append({"code": "DUPLICATE_QUERIED_CLIENT"})
    extra = sorted(queried - eligible)
    missing = sorted(eligible - queried)
    if extra:
        findings.append({"code": "QUERY_UNIVERSE_EXTRA_CLIENTS", "client_ids": extra})
    if missing:
        findings.append({"code": "QUERY_UNIVERSE_MISSING_CLIENTS", "client_ids": missing})

    future_call = {_text(x) for x in payload.get("future_call_client_ids", []) if _text(x)}
    sem_movimento = {_text(x) for x in payload.get("sem_movimento_non_applicable_client_ids", []) if _text(x)}
    future_queried = sorted(queried.intersection(future_call))
    sem_mov_queried = sorted(queried.intersection(sem_movimento))
    if future_queried:
        findings.append({"code": "FUTURE_CALL_CLIENT_QUERIED", "client_ids": future_queried})
    if sem_mov_queried:
        findings.append({"code": "SEM_MOVIMENTO_CLIENT_QUERIED", "client_ids": sem_mov_queried})

    snapshots = payload.get("snapshots", [])
    valid_history_by_client: dict[str, bool] = {}
    for snapshot in snapshots:
        if not isinstance(snapshot, dict):
            raise EConsignadoError("Snapshot deve ser objeto JSON.")
        client_id = _text(snapshot.get("client_id"))
        result = _text(snapshot.get("result")).upper()
        snapshot_id = _text(snapshot.get("snapshot_id"))
        if not client_id or not snapshot_id:
            findings.append({"code": "SNAPSHOT_IDENTITY_MISSING", "client_id": client_id or None})
            continue
        if result not in QUERY_RESULTS:
            findings.append({"code": "INVALID_QUERY_RESULT", "client_id": client_id, "result": result})
            continue
        if result != "ERRO_TECNICO":
            valid_history_by_client[client_id] = True
        elif valid_history_by_client.get(client_id) and not bool(snapshot.get("prior_valid_preserved", False)):
            findings.append({"code": "TECHNICAL_ERROR_DID_NOT_PRESERVE_PRIOR_VALID_SNAPSHOT", "client_id": client_id})
        if result == "SEM_PROCURACAO" and bool(snapshot.get("classified_as_technical_error", False)):
            findings.append({"code": "SEM_PROCURACAO_MISCLASSIFIED_AS_TECHNICAL_ERROR", "client_id": client_id})
        if result == "SEM_CONSIGNADO" and bool(snapshot.get("classified_as_technical_error", False)):
            findings.append({"code": "SEM_CONSIGNADO_MISCLASSIFIED_AS_TECHNICAL_ERROR", "client_id": client_id})

    for item in payload.get("obligations", []):
        if not isinstance(item, dict):
            raise EConsignadoError("Obrigação eConsignado deve ser objeto JSON.")
        client_id = _text(item.get("client_id"))
        mte_result = _text(item.get("mte_result")).upper()
        business_state = _text(item.get("business_state")).upper()
        required_sources = item.get("required_sources", {}) or {}
        if not isinstance(required_sources, dict):
            raise EConsignadoError(f"required_sources inválido para {client_id}.")
        sources_complete = all(bool(value) for value in required_sources.values()) if required_sources else False
        compatible = bool(item.get("sources_compatible", False))
        derived_from_context = bool(item.get("derived_from_context", False))

        if mte_result not in QUERY_RESULTS:
            findings.append({"code": "OBLIGATION_WITH_INVALID_MTE_RESULT", "client_id": client_id, "result": mte_result})
            continue

        if business_state in {"CONFERIDA", "JUSTIFICADA", "NAO_APLICAVEL", "IMPEDIDA_EXTERNAMENTE"} and not derived_from_context:
            findings.append({"code": "BUSINESS_STATE_DERIVED_FROM_QUERY_RESULT_ALONE", "client_id": client_id, "state": business_state})

        if mte_result == "COM_CONSIGNADO" and business_state == "CONFERIDA":
            if not sources_complete:
                findings.append({"code": "FALSE_CONFERRED_MISSING_SOURCE", "client_id": client_id})
            if not compatible:
                findings.append({"code": "FALSE_CONFERRED_INCOMPATIBLE_SOURCES", "client_id": client_id})

        active_employment = bool(item.get("active_employment", False))
        remuneration = _money(item.get("remuneration"))
        fgts_amount = _money(item.get("fgts_amount"))
        residual_only = mte_result == "COM_CONSIGNADO" and not active_employment and remuneration == 0 and fgts_amount == 0
        if residual_only:
            disposition = _text(item.get("residual_disposition")).upper()
            if disposition not in {"OBSERVACAO_A_CONFIRMAR", "NAO_BLOQUEANTE_JUSTIFICADA"}:
                findings.append({"code": "RESIDUAL_RETURN_BLOCKS_WITHOUT_CONTEXT", "client_id": client_id, "business_state": business_state})

        if bool(item.get("termination", False)) and mte_result == "COM_CONSIGNADO":
            if not bool(item.get("termination_components_separated", False)):
                findings.append({"code": "TERMINATION_COMPONENTS_NOT_SEPARATED", "client_id": client_id})

    report = {
        "version": 1,
        "audit": "B24_B25_B26_B27_ECONSIGNADO_CYCLE",
        "all_ok": not findings,
        "competence": competence,
        "call": call,
        "eligible_count": len(eligible),
        "queried_count": len(queried),
        "findings": findings,
    }
    report["report_sha256"] = _canonical_hash(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida eConsignado como Etapa 0 do ciclo e sem falso Conferido.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        report = validate(payload)
    except (OSError, json.JSONDecodeError, EConsignadoError) as exc:
        print(f"ECONSIGNADO_CONTRACT_ERROR: {exc}", file=sys.stderr)
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
