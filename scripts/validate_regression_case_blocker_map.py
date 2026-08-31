from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CASE_RE = re.compile(r"^C(0[1-9]|1[0-9]|2[0-8])$")
BLOCKER_RE = re.compile(r"^B(0[1-9]|[1-4][0-9]|50)$")


class DependencyMapError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DependencyMapError(f"JSON inválido {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise DependencyMapError(f"JSON deve ser objeto: {path}")
    return payload


def _registry_case_ids(registry: dict) -> list[str]:
    required = registry.get("required_cases")
    if not isinstance(required, list) or len(required) != 28:
        raise DependencyMapError("Registry de regressão deve conter exatamente 28 required_cases.")
    ids: list[str] = []
    for item in required:
        if not isinstance(item, dict):
            raise DependencyMapError("Caso inválido no registry de regressão.")
        case_id = str(item.get("case_id", "")).strip()
        if not CASE_RE.fullmatch(case_id):
            raise DependencyMapError(f"case_id inválido no registry: {case_id!r}")
        ids.append(case_id)
    if len(set(ids)) != 28:
        raise DependencyMapError("Registry de regressão contém case_id duplicado.")
    return ids


def _blocker_ids(blocker_registry: dict) -> set[str]:
    blockers = blocker_registry.get("blockers")
    if not isinstance(blockers, list) or not blockers:
        raise DependencyMapError("Registry de bloqueadores deve conter lista blockers.")
    ids: set[str] = set()
    for item in blockers:
        if not isinstance(item, dict):
            raise DependencyMapError("Bloqueador inválido no registry.")
        blocker_id = str(item.get("id", "")).strip()
        if not BLOCKER_RE.fullmatch(blocker_id):
            raise DependencyMapError(f"ID de bloqueador inválido: {blocker_id!r}")
        if blocker_id in ids:
            raise DependencyMapError(f"Bloqueador duplicado no registry: {blocker_id}")
        ids.add(blocker_id)
    return ids


def validate_dependency_map(
    regression_registry: dict,
    blocker_registry: dict,
    dependency_map: dict,
) -> dict:
    if dependency_map.get("version") != 1:
        raise DependencyMapError("Dependency map version inválida.")
    if str(dependency_map.get("audit", "")).strip().upper() != "V8":
        raise DependencyMapError("Dependency map deve declarar audit=V8.")

    expected_cases = _registry_case_ids(regression_registry)
    known_blockers = _blocker_ids(blocker_registry)

    cases = dependency_map.get("cases")
    if not isinstance(cases, list) or len(cases) != 28:
        raise DependencyMapError("Dependency map deve conter exatamente 28 cases.")

    mapped: dict[str, list[str]] = {}
    blocker_usage: dict[str, int] = {key: 0 for key in known_blockers}
    for item in cases:
        if not isinstance(item, dict):
            raise DependencyMapError("Entrada inválida em cases.")
        case_id = str(item.get("case_id", "")).strip()
        if case_id in mapped:
            raise DependencyMapError(f"Caso duplicado no dependency map: {case_id}")
        if case_id not in expected_cases:
            raise DependencyMapError(f"Caso desconhecido no dependency map: {case_id}")
        blockers = item.get("blockers")
        if not isinstance(blockers, list) or not blockers:
            raise DependencyMapError(f"Caso sem bloqueadores associados: {case_id}")
        normalized = [str(value).strip() for value in blockers]
        if len(normalized) != len(set(normalized)):
            raise DependencyMapError(f"Bloqueador duplicado no caso {case_id}")
        unknown = [value for value in normalized if value not in known_blockers]
        if unknown:
            raise DependencyMapError(
                f"Bloqueador desconhecido em {case_id}: {', '.join(unknown)}"
            )
        gate = str(item.get("gate", "")).strip()
        if not gate:
            raise DependencyMapError(f"Gate causal ausente em {case_id}")
        mapped[case_id] = normalized
        for blocker_id in normalized:
            blocker_usage[blocker_id] += 1

    missing = [case_id for case_id in expected_cases if case_id not in mapped]
    if missing:
        raise DependencyMapError("Casos ausentes: " + ", ".join(missing))

    controls = dependency_map.get("controls", [])
    if not isinstance(controls, list):
        raise DependencyMapError("controls deve ser lista.")
    seen_controls: set[str] = set()
    for item in controls:
        if not isinstance(item, dict):
            raise DependencyMapError("Controle inválido.")
        control_id = str(item.get("case_id", "")).strip()
        if not control_id or control_id in seen_controls:
            raise DependencyMapError(f"Controle inválido/duplicado: {control_id!r}")
        seen_controls.add(control_id)
        blockers = item.get("blockers")
        if not isinstance(blockers, list) or not blockers:
            raise DependencyMapError(f"Controle sem bloqueadores: {control_id}")
        normalized = [str(value).strip() for value in blockers]
        unknown = [value for value in normalized if value not in known_blockers]
        if unknown:
            raise DependencyMapError(
                f"Bloqueador desconhecido no controle {control_id}: {', '.join(unknown)}"
            )
        if len(normalized) != len(set(normalized)):
            raise DependencyMapError(f"Bloqueador duplicado no controle {control_id}")
        if not str(item.get("gate", "")).strip():
            raise DependencyMapError(f"Gate causal ausente no controle {control_id}")
        for blocker_id in normalized:
            blocker_usage[blocker_id] += 1

    used = sorted(key for key, value in blocker_usage.items() if value)
    unused = sorted(key for key, value in blocker_usage.items() if not value)
    return {
        "required_cases": 28,
        "mapped_cases": len(mapped),
        "controls": len(controls),
        "known_blockers": len(known_blockers),
        "used_blockers": used,
        "unused_blockers": unused,
        "ok": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida o mapa causal C01-C28 -> B01-B50 da auditoria V8."
    )
    parser.add_argument("--regression-registry", required=True, type=Path)
    parser.add_argument("--blocker-registry", required=True, type=Path)
    parser.add_argument("--map", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=Path("REGRESSION_CASE_BLOCKER_MAP_VALIDATION.json"))
    args = parser.parse_args()

    try:
        report = validate_dependency_map(
            load_json(args.regression_registry),
            load_json(args.blocker_registry),
            load_json(args.map),
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except DependencyMapError as exc:
        print(f"REGRESSION_CASE_BLOCKER_MAP_ERRO: {exc}", file=sys.stderr)
        return 2

    print("REGRESSION_CASE_BLOCKER_MAP_OK")
    print(f"Casos: {report['mapped_cases']}/28")
    print(f"Bloqueadores usados: {len(report['used_blockers'])}/{report['known_blockers']}")
    print(f"Relatório: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
