from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ALLOWED_STATES = {
    "PENDENTE",
    "CONFERIDA",
    "DIVERGENTE",
    "JUSTIFICADA",
    "NAO_APLICAVEL",
    "IMPEDIDA_EXTERNAMENTE",
    "RETIFICACAO",
}
BLOCKING_STATES = {"PENDENTE", "DIVERGENTE", "RETIFICACAO"}


class DecisionError(RuntimeError):
    pass


def _text(value: object) -> str:
    return str(value or "").strip()


def _key(item: dict) -> tuple[str, str, str, str]:
    return (
        _text(item.get("competence")),
        _text(item.get("client_id")),
        _text(item.get("obligation")).upper(),
        _text(item.get("component")).upper(),
    )


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def evaluate(
    obligations: list[dict],
    decisions: list[dict],
    current_revisions: dict[str, int] | None = None,
    policy: dict | None = None,
) -> dict:
    current_revisions = current_revisions or {}
    policy = policy or {}
    allow_external_terminal = bool(policy.get("allow_external_impediment_as_terminal", True))
    terminal_states = {"CONFERIDA", "JUSTIFICADA", "NAO_APLICAVEL"}
    if allow_external_terminal:
        terminal_states.add("IMPEDIDA_EXTERNAMENTE")

    findings: list[dict] = []
    current: dict[tuple[str, str, str, str], dict] = {}

    for raw in obligations:
        if not isinstance(raw, dict):
            raise DecisionError("Obrigação deve ser objeto JSON.")
        key = _key(raw)
        if not all(key[:3]):
            raise DecisionError("competence, client_id e obligation são obrigatórios na obrigação.")
        if key in current:
            findings.append({"code": "DUPLICATE_OBLIGATION_KEY", "key": list(key)})
            continue
        state = _text(raw.get("state")).upper()
        if state not in ALLOWED_STATES:
            raise DecisionError(f"Estado inválido na obrigação {key}: {state}")
        current[key] = {
            "competence": key[0],
            "client_id": key[1],
            "obligation": key[2],
            "component": key[3],
            "state": state,
            "applicable": bool(raw.get("applicable", state != "NAO_APLICAVEL")),
            "source": "OBLIGATION_BASELINE",
        }

    seen_decision_ids: set[str] = set()
    for raw in decisions:
        if not isinstance(raw, dict):
            raise DecisionError("Decisão deve ser objeto JSON.")
        decision_id = _text(raw.get("decision_id"))
        if not decision_id:
            raise DecisionError("decision_id é obrigatório.")
        if decision_id in seen_decision_ids:
            findings.append({"code": "DUPLICATE_DECISION_ID", "decision_id": decision_id})
            continue
        seen_decision_ids.add(decision_id)

        key = _key(raw)
        if not all(key[:3]) or key[2] in {"*", "GLOBAL", "TODAS"}:
            findings.append({"code": "GLOBAL_OR_UNSCOPED_DECISION", "decision_id": decision_id})
            continue
        if key not in current:
            findings.append({"code": "DECISION_WITHOUT_OBLIGATION", "decision_id": decision_id, "key": list(key)})
            continue

        previous_state = _text(raw.get("previous_state")).upper()
        new_state = _text(raw.get("new_state")).upper()
        if new_state not in ALLOWED_STATES or previous_state not in ALLOWED_STATES:
            findings.append({"code": "INVALID_DECISION_STATE", "decision_id": decision_id})
            continue
        if previous_state != current[key]["state"]:
            findings.append({
                "code": "STALE_PREVIOUS_STATE",
                "decision_id": decision_id,
                "expected": current[key]["state"],
                "received": previous_state,
            })
            continue

        required_metadata = ["reason", "user_id", "timestamp", "origin", "correlation_id"]
        missing = [field for field in required_metadata if not _text(raw.get(field))]
        evidence = raw.get("evidence")
        if not isinstance(evidence, list):
            missing.append("evidence")
        if missing:
            findings.append({"code": "DECISION_METADATA_MISSING", "decision_id": decision_id, "fields": sorted(set(missing))})
            continue

        revision = raw.get("monthly_revision")
        revision_key = f"{key[0]}|{key[1]}"
        expected_revision = current_revisions.get(revision_key)
        if expected_revision is not None:
            try:
                revision_int = int(revision)
            except (TypeError, ValueError):
                revision_int = -1
            if revision_int != int(expected_revision):
                findings.append({
                    "code": "STALE_MONTHLY_REVISION",
                    "decision_id": decision_id,
                    "expected": int(expected_revision),
                    "received": revision,
                })
                continue

        current[key] = {
            **current[key],
            "state": new_state,
            "source": "MANUAL_DECISION",
            "decision_id": decision_id,
            "reason": _text(raw.get("reason")),
        }

    clients: dict[tuple[str, str], list[dict]] = {}
    for item in current.values():
        clients.setdefault((item["competence"], item["client_id"]), []).append(item)

    aggregate: list[dict] = []
    for (competence, client_id), items in sorted(clients.items()):
        applicable = [x for x in items if x["applicable"]]
        blockers = [x for x in applicable if x["state"] not in terminal_states]
        aggregate.append({
            "competence": competence,
            "client_id": client_id,
            "closable": not blockers,
            "blocking_keys": [
                [x["obligation"], x["component"], x["state"]] for x in sorted(blockers, key=lambda v: (v["obligation"], v["component"]))
            ],
        })

    report = {
        "version": 1,
        "audit": "B18_B23_DECISION_BY_SOURCE_OBLIGATION",
        "all_ok": not findings,
        "obligations": [current[key] for key in sorted(current)],
        "clients": aggregate,
        "findings": findings,
    }
    report["report_sha256"] = _canonical_hash(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida decisões por fonte/obrigação sem permitir conclusão global indevida.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        report = evaluate(
            payload.get("obligations", []),
            payload.get("decisions", []),
            payload.get("current_revisions", {}),
            payload.get("policy", {}),
        )
    except (OSError, json.JSONDecodeError, DecisionError) as exc:
        print(f"SOURCE_DECISION_ERROR: {exc}", file=sys.stderr)
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
