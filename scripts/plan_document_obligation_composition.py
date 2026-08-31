from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9A-Fa-f]{64}$")
RELATIONS = {
    "PRIMARY",
    "IDENTICO_FISICO",
    "REEMISSAO_EQUIVALENTE",
    "VERSAO_SUCESSORA",
    "SUBSTITUTIVO",
    "COMPLEMENTAR",
    "UNIDADE_DISTINTA",
    "COMPONENTE_ADITIVO",
    "RELACAO_INDETERMINADA",
}
VERSIONED_RELATIONS = {"REEMISSAO_EQUIVALENTE", "VERSAO_SUCESSORA", "SUBSTITUTIVO"}
ADDITIVE_RELATIONS = {"PRIMARY", "COMPLEMENTAR", "UNIDADE_DISTINTA", "COMPONENTE_ADITIVO"}


class CompositionError(RuntimeError):
    pass


def _money(value: object) -> Decimal:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise CompositionError(f"Valor monetário inválido: {value!r}") from exc
    if not amount.is_finite():
        raise CompositionError(f"Valor monetário não finito: {value!r}")
    return amount.quantize(Decimal("0.01"))


def _required_text(record: dict, field: str) -> str:
    value = str(record.get(field, "")).strip()
    if not value:
        raise CompositionError(f"Campo obrigatório ausente: {field}")
    return value


def _normalize_record(raw: dict) -> dict:
    if not isinstance(raw, dict):
        raise CompositionError("Cada evidência deve ser um objeto JSON.")
    evidence_id = _required_text(raw, "evidence_id")
    dimension = _required_text(raw, "dimension").upper()
    economic_key = _required_text(raw, "economic_key")
    component_key = _required_text(raw, "component_key")
    logical_fingerprint = _required_text(raw, "logical_fingerprint")
    physical_sha256 = _required_text(raw, "physical_sha256").upper()
    if not SHA256_RE.fullmatch(physical_sha256):
        raise CompositionError(f"SHA-256 inválido em {evidence_id}.")
    relation = str(raw.get("relation", "PRIMARY")).strip().upper() or "PRIMARY"
    if relation not in RELATIONS:
        raise CompositionError(f"Relação inválida em {evidence_id}: {relation}")
    relation_group = str(raw.get("relation_group", "")).strip() or None
    preferred_current = bool(raw.get("preferred_current", False))
    unit_key = str(raw.get("unit_key", "")).strip() or None
    return {
        "evidence_id": evidence_id,
        "dimension": dimension,
        "economic_key": economic_key,
        "component_key": component_key,
        "logical_fingerprint": logical_fingerprint,
        "physical_sha256": physical_sha256,
        "amount": _money(raw.get("amount")),
        "relation": relation,
        "relation_group": relation_group,
        "preferred_current": preferred_current,
        "unit_key": unit_key,
    }


def _canonical_hash(value: object) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def plan_composition(records: list[dict]) -> dict:
    normalized = [_normalize_record(item) for item in records]
    findings: list[dict] = []
    decisions: dict[str, dict] = {}

    ids: set[str] = set()
    for record in normalized:
        evidence_id = record["evidence_id"]
        if evidence_id in ids:
            findings.append({"code": "DUPLICATE_EVIDENCE_ID", "evidence_id": evidence_id})
        ids.add(evidence_id)

    by_sha: dict[str, list[dict]] = defaultdict(list)
    for record in normalized:
        by_sha[record["physical_sha256"]].append(record)

    physically_excluded: set[str] = set()
    for sha, group in by_sha.items():
        if len(group) < 2:
            continue
        identities = {
            (r["dimension"], r["economic_key"], r["component_key"], r["logical_fingerprint"], r["amount"])
            for r in group
        }
        if len(identities) > 1:
            findings.append({
                "code": "PHYSICAL_HASH_IDENTITY_CONFLICT",
                "physical_sha256": sha,
                "evidence_ids": sorted(r["evidence_id"] for r in group),
            })
            continue
        canonical = sorted(group, key=lambda r: r["evidence_id"])[0]
        for record in group:
            if record is canonical:
                continue
            physically_excluded.add(record["evidence_id"])
            decisions[record["evidence_id"]] = {
                "action": "EXCLUDE_IDENTICAL_PHYSICAL",
                "canonical_evidence_id": canonical["evidence_id"],
            }

    active = [r for r in normalized if r["evidence_id"] not in physically_excluded]
    component_groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for record in active:
        component_groups[(record["dimension"], record["economic_key"], record["component_key"])].append(record)

    included_by_economic: dict[tuple[str, str], list[dict]] = defaultdict(list)
    invalid_economic: set[tuple[str, str]] = set()

    for component_identity, group in component_groups.items():
        dimension, economic_key, component_key = component_identity
        econ_identity = (dimension, economic_key)

        if any(r["relation"] == "RELACAO_INDETERMINADA" for r in group):
            findings.append({
                "code": "INDETERMINATE_RELATION_BLOCKS_COMPOSITION",
                "dimension": dimension,
                "economic_key": economic_key,
                "component_key": component_key,
                "evidence_ids": sorted(r["evidence_id"] for r in group),
            })
            invalid_economic.add(econ_identity)
            for record in group:
                decisions.setdefault(record["evidence_id"], {"action": "REVIEW_REQUIRED"})
            continue

        if len(group) == 1:
            record = group[0]
            if record["relation"] in VERSIONED_RELATIONS and not record["relation_group"]:
                findings.append({
                    "code": "VERSION_RELATION_WITHOUT_GROUP",
                    "evidence_id": record["evidence_id"],
                    "relation": record["relation"],
                })
                invalid_economic.add(econ_identity)
                decisions.setdefault(record["evidence_id"], {"action": "REVIEW_REQUIRED"})
                continue
            decisions.setdefault(record["evidence_id"], {"action": "INCLUDE_COMPONENT"})
            included_by_economic[econ_identity].append(record)
            continue

        relations = {r["relation"] for r in group}
        logicals = {r["logical_fingerprint"] for r in group}
        amounts = {r["amount"] for r in group}
        relation_groups = {r["relation_group"] for r in group if r["relation_group"]}
        preferred = [r for r in group if r["preferred_current"]]

        versioned = bool(relations.intersection(VERSIONED_RELATIONS))
        if versioned:
            if len(relation_groups) != 1:
                findings.append({
                    "code": "VERSION_GROUP_AMBIGUOUS",
                    "dimension": dimension,
                    "economic_key": economic_key,
                    "component_key": component_key,
                    "evidence_ids": sorted(r["evidence_id"] for r in group),
                })
                invalid_economic.add(econ_identity)
                continue
            if len(preferred) != 1:
                findings.append({
                    "code": "VERSION_GROUP_REQUIRES_ONE_CURRENT",
                    "dimension": dimension,
                    "economic_key": economic_key,
                    "component_key": component_key,
                    "preferred_count": len(preferred),
                })
                invalid_economic.add(econ_identity)
                continue
            current = preferred[0]
            if "REEMISSAO_EQUIVALENTE" in relations and len(amounts) != 1:
                findings.append({
                    "code": "EQUIVALENT_REISSUE_AMOUNT_DIVERGENCE",
                    "dimension": dimension,
                    "economic_key": economic_key,
                    "component_key": component_key,
                })
                invalid_economic.add(econ_identity)
                continue
            decisions[current["evidence_id"]] = {"action": "INCLUDE_CURRENT_VERSION"}
            included_by_economic[econ_identity].append(current)
            for record in group:
                if record is current:
                    continue
                decisions[record["evidence_id"]] = {
                    "action": "EXCLUDE_SUPERSEDED_OR_EQUIVALENT",
                    "current_evidence_id": current["evidence_id"],
                }
            continue

        if relations.issubset(ADDITIVE_RELATIONS):
            # Dois registros no mesmo component_key não podem ser somados por conveniência.
            findings.append({
                "code": "DUPLICATE_ECONOMIC_COMPONENT_WITHOUT_RELATION",
                "dimension": dimension,
                "economic_key": economic_key,
                "component_key": component_key,
                "logical_fingerprints": sorted(logicals),
                "evidence_ids": sorted(r["evidence_id"] for r in group),
            })
            invalid_economic.add(econ_identity)
            continue

        findings.append({
            "code": "UNSUPPORTED_COMPONENT_RELATION_SET",
            "dimension": dimension,
            "economic_key": economic_key,
            "component_key": component_key,
            "relations": sorted(relations),
        })
        invalid_economic.add(econ_identity)

    totals: list[dict] = []
    all_economic = sorted({(r["dimension"], r["economic_key"]) for r in normalized})
    for identity in all_economic:
        dimension, economic_key = identity
        included = included_by_economic.get(identity, [])
        if identity in invalid_economic:
            totals.append({
                "dimension": dimension,
                "economic_key": economic_key,
                "status": "REVIEW_REQUIRED",
                "total": None,
                "included_evidence_ids": sorted(r["evidence_id"] for r in included),
            })
            continue
        total = sum((r["amount"] for r in included), Decimal("0.00"))
        totals.append({
            "dimension": dimension,
            "economic_key": economic_key,
            "status": "COMPOSED",
            "total": format(total, ".2f"),
            "included_evidence_ids": sorted(r["evidence_id"] for r in included),
        })

    result = {
        "version": 1,
        "audit": "B12_B13_B14_B17_B50_DOCUMENT_OBLIGATION_COMPOSITION",
        "all_ok": not findings,
        "evidence_count": len(normalized),
        "decisions": decisions,
        "totals": totals,
        "findings": findings,
    }
    result["plan_sha256"] = _canonical_hash(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Planeja composição documental/econômica sem somar ou deduplicar cegamente.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        payload = json.loads(args.input.read_text(encoding="utf-8"))
        records = payload.get("evidence", payload) if isinstance(payload, dict) else payload
        if not isinstance(records, list):
            raise CompositionError("Entrada deve ser lista de evidências ou objeto com chave evidence.")
        report = plan_composition(records)
    except (OSError, json.JSONDecodeError, CompositionError) as exc:
        print(f"COMPOSITION_PLAN_ERROR: {exc}", file=sys.stderr)
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
