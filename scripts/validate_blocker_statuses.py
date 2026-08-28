from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

STATES = (
    "NAO_INICIADO",
    "INSPECAO_PENDENTE",
    "PRONTO_PARA_CORRIGIR",
    "EM_CORRECAO",
    "IMPLEMENTADO_NAO_TESTADO",
    "TESTE_EM_EXECUCAO",
    "CORRIGIDO_TESTADO",
    "CORRIGIDO_HOMOLOGADO",
    "BLOQUEADO_POR_RUNTIME",
)
BLOCKER_RE = re.compile(r"^B(?:0[1-9]|[1-4][0-9]|50)$")
COVERAGE_RE = re.compile(r"^[ECPR]+$")


class BlockerValidationError(RuntimeError):
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
        raise BlockerValidationError(f"JSON inválido {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise BlockerValidationError(f"JSON deve ser objeto: {path}")
    return data


def validate_registry(registry: dict) -> dict:
    if registry.get("version") != 1 or registry.get("audit") != "V8":
        raise BlockerValidationError("Registry deve ser version=1 audit=V8.")
    blockers = registry.get("blockers")
    if not isinstance(blockers, list) or len(blockers) != 50:
        raise BlockerValidationError("Registry deve conter exatamente 50 blockers.")

    ids: list[str] = []
    for item in blockers:
        if not isinstance(item, dict):
            raise BlockerValidationError("Blocker inválido no registry.")
        blocker_id = str(item.get("blocker_id", "")).strip()
        theme = str(item.get("theme", "")).strip()
        coverage = str(item.get("coverage", "")).strip()
        if not BLOCKER_RE.fullmatch(blocker_id):
            raise BlockerValidationError(f"ID inválido: {blocker_id!r}")
        if not theme:
            raise BlockerValidationError(f"Tema ausente: {blocker_id}")
        if not COVERAGE_RE.fullmatch(coverage):
            raise BlockerValidationError(
                f"Cobertura inválida em {blocker_id}: {coverage!r}"
            )
        ids.append(blocker_id)

    expected = [f"B{index:02d}" for index in range(1, 51)]
    if ids != expected or len(set(ids)) != 50:
        raise BlockerValidationError(
            "Registry deve conter B01–B50 em ordem, sem duplicidade."
        )
    return {"ids": ids, "hash": canonical_hash(registry)}


def _evidence(item: dict, field: str) -> list[str]:
    value = item.get(field, [])
    if not isinstance(value, list) or not all(
        isinstance(entry, str) and entry.strip() for entry in value
    ):
        raise BlockerValidationError(
            f"{field} deve ser lista de strings não vazias quando presente."
        )
    return [entry.strip() for entry in value]


def validate_statuses(
    registry: dict,
    status_doc: dict,
    final_mode: bool = False,
) -> dict:
    meta = validate_registry(registry)
    if status_doc.get("registry_sha256") != meta["hash"]:
        raise BlockerValidationError(
            "registry_sha256 não corresponde ao registry canônico."
        )
    raw = status_doc.get("blockers")
    if not isinstance(raw, list):
        raise BlockerValidationError("Status deve conter lista blockers.")

    by_id: dict[str, dict] = {}
    unknown: list[str] = []
    for item in raw:
        if not isinstance(item, dict):
            raise BlockerValidationError("Entrada de status inválida.")
        blocker_id = str(item.get("blocker_id", "")).strip()
        if blocker_id in by_id:
            raise BlockerValidationError(f"Status duplicado: {blocker_id}")
        if blocker_id not in meta["ids"]:
            unknown.append(blocker_id)

        state = str(item.get("state", "")).strip().upper()
        if state not in STATES:
            raise BlockerValidationError(
                f"Estado inválido em {blocker_id}: {state!r}"
            )

        code_evidence = _evidence(item, "code_evidence")
        test_evidence = _evidence(item, "test_evidence")
        runtime_evidence = _evidence(item, "runtime_evidence")
        homologation_evidence = _evidence(item, "homologation_evidence")

        if state in {"CORRIGIDO_TESTADO", "CORRIGIDO_HOMOLOGADO"}:
            if not code_evidence or not test_evidence:
                raise BlockerValidationError(
                    f"{state} exige code_evidence e test_evidence: {blocker_id}"
                )
        if state == "CORRIGIDO_HOMOLOGADO":
            if not runtime_evidence or not homologation_evidence:
                raise BlockerValidationError(
                    "CORRIGIDO_HOMOLOGADO exige runtime_evidence e "
                    f"homologation_evidence: {blocker_id}"
                )

        by_id[blocker_id] = {
            "state": state,
            "code_evidence": code_evidence,
            "test_evidence": test_evidence,
            "runtime_evidence": runtime_evidence,
            "homologation_evidence": homologation_evidence,
            "notes": str(item.get("notes", "")),
        }

    if unknown:
        raise BlockerValidationError(
            "Bloqueadores desconhecidos: " + ", ".join(unknown)
        )

    missing = [blocker_id for blocker_id in meta["ids"] if blocker_id not in by_id]
    state_counts = {
        state: sum(1 for value in by_id.values() if value["state"] == state)
        for state in STATES
    }
    complete = not missing
    homologated = state_counts["CORRIGIDO_HOMOLOGADO"]
    final_ok = complete and homologated == 50

    if final_mode and not final_ok:
        raise BlockerValidationError(
            "Estado final inválido: "
            f"missing={len(missing)} homologated={homologated}/50"
        )

    return {
        "registry_sha256": meta["hash"],
        "required": 50,
        "submitted": len(by_id),
        "missing": missing,
        "state_counts": state_counts,
        "complete": complete,
        "homologated": homologated,
        "final_ok": final_ok,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida estados/evidências dos 50 bloqueadores canônicos V8."
    )
    parser.add_argument("--registry", required=True, type=Path)
    parser.add_argument("--status", required=True, type=Path)
    parser.add_argument("--final", action="store_true")
    parser.add_argument(
        "--output", type=Path, default=Path("BLOCKER_STATUS_VALIDATION.json")
    )
    args = parser.parse_args()

    try:
        report = validate_statuses(
            load_json(args.registry),
            load_json(args.status),
            args.final,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except BlockerValidationError as exc:
        print(f"BLOCKER_STATUS_ERRO: {exc}", file=sys.stderr)
        return 2

    print("BLOCKER_STATUS_OK")
    print(f"Submetidos: {report['submitted']}/50")
    print(f"Homologados: {report['homologated']}/50")
    print(f"Final OK: {report['final_ok']}")
    print(f"Relatório: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
