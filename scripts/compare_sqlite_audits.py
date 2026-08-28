from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class ComparisonError(RuntimeError):
    pass


def load_report(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ComparisonError(f"Relatório inválido {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ComparisonError(f"Relatório deve ser objeto JSON: {path}")
    for key in ("database", "integrity", "foreign_keys", "schema", "summary"):
        if key not in data:
            raise ComparisonError(
                f"Relatório sem seção obrigatória '{key}': {path}"
            )
    return data


def schema_object_map(
    report: dict[str, Any]
) -> dict[tuple[str, str], dict[str, Any]]:
    objects = report.get("schema", {}).get("objects")
    if not isinstance(objects, list):
        raise ComparisonError("schema.objects ausente ou inválido.")
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for item in objects:
        if not isinstance(item, dict):
            raise ComparisonError("Entrada inválida em schema.objects.")
        obj_type = str(item.get("type") or "")
        name = str(item.get("name") or "")
        if not obj_type or not name:
            raise ComparisonError("Objeto de schema sem type/name.")
        key = (obj_type, name)
        if key in result:
            raise ComparisonError(f"Objeto de schema duplicado: {obj_type}:{name}")
        result[key] = item
    return result


def fk_violation_key(item: dict[str, Any]) -> tuple[Any, ...]:
    return (
        item.get("table"),
        item.get("rowid"),
        item.get("parent"),
        item.get("fkid"),
    )


def compare_reports(
    before: dict[str, Any], after: dict[str, Any]
) -> dict[str, Any]:
    before_objects = schema_object_map(before)
    after_objects = schema_object_map(after)

    before_keys = set(before_objects)
    after_keys = set(after_objects)

    added_objects = [
        {
            "type": key[0],
            "name": key[1],
            "table": after_objects[key].get("table"),
        }
        for key in sorted(after_keys - before_keys)
    ]
    removed_objects = [
        {
            "type": key[0],
            "name": key[1],
            "table": before_objects[key].get("table"),
        }
        for key in sorted(before_keys - after_keys)
    ]
    changed_objects = []
    for key in sorted(before_keys & after_keys):
        if before_objects[key].get("sql") != after_objects[key].get("sql"):
            changed_objects.append(
                {
                    "type": key[0],
                    "name": key[1],
                    "table_before": before_objects[key].get("table"),
                    "table_after": after_objects[key].get("table"),
                }
            )

    before_fk = before.get("foreign_keys", {}).get("violations") or []
    after_fk = after.get("foreign_keys", {}).get("violations") or []
    if not isinstance(before_fk, list) or not isinstance(after_fk, list):
        raise ComparisonError("foreign_keys.violations inválido.")
    before_fk_map = {fk_violation_key(item): item for item in before_fk}
    after_fk_map = {fk_violation_key(item): item for item in after_fk}

    new_fk_violations = [
        after_fk_map[key]
        for key in sorted(set(after_fk_map) - set(before_fk_map), key=str)
    ]
    resolved_fk_violations = [
        before_fk_map[key]
        for key in sorted(set(before_fk_map) - set(after_fk_map), key=str)
    ]

    before_counts = before.get("row_counts")
    after_counts = after.get("row_counts")
    row_deltas: dict[str, dict[str, int | None]] | None = None
    row_decreases: list[dict[str, Any]] = []
    if isinstance(before_counts, dict) and isinstance(after_counts, dict):
        row_deltas = {}
        for table in sorted(set(before_counts) | set(after_counts)):
            before_value = before_counts.get(table)
            after_value = after_counts.get(table)
            before_int = int(before_value) if before_value is not None else None
            after_int = int(after_value) if after_value is not None else None
            delta = (
                None
                if before_int is None or after_int is None
                else after_int - before_int
            )
            row_deltas[table] = {
                "before": before_int,
                "after": after_int,
                "delta": delta,
            }
            if delta is not None and delta < 0:
                row_decreases.append(
                    {
                        "table": table,
                        "before": before_int,
                        "after": after_int,
                        "delta": delta,
                    }
                )

    before_integrity = bool(before.get("summary", {}).get("integrity_ok"))
    after_integrity = bool(after.get("summary", {}).get("integrity_ok"))
    before_fk_ok = bool(before.get("summary", {}).get("foreign_keys_ok"))
    after_fk_ok = bool(after.get("summary", {}).get("foreign_keys_ok"))

    regressions: list[dict[str, Any]] = []
    if before_integrity and not after_integrity:
        regressions.append(
            {
                "code": "INTEGRITY_REGRESSION",
                "detail": "integrity_check passou antes e falhou depois.",
            }
        )
    if new_fk_violations:
        regressions.append(
            {
                "code": "NEW_FOREIGN_KEY_VIOLATIONS",
                "detail": (
                    f"{len(new_fk_violations)} nova(s) violação(ões) de FK."
                ),
            }
        )

    warnings: list[dict[str, Any]] = []
    if removed_objects:
        warnings.append(
            {
                "code": "SCHEMA_OBJECTS_REMOVED",
                "detail": (
                    f"{len(removed_objects)} objeto(s) de schema removido(s); "
                    "exige justificativa de migração."
                ),
            }
        )
    if row_decreases:
        warnings.append(
            {
                "code": "ROW_COUNT_DECREASES",
                "detail": (
                    f"{len(row_decreases)} tabela(s) com redução de registros; "
                    "exige justificativa."
                ),
            }
        )

    return {
        "before": {
            "database_name": before.get("database", {}).get("name"),
            "user_version": before.get("database", {}).get("user_version"),
            "schema_sha256": before.get("schema", {}).get("sha256"),
            "structural_ok": before.get("summary", {}).get("structural_ok"),
        },
        "after": {
            "database_name": after.get("database", {}).get("name"),
            "user_version": after.get("database", {}).get("user_version"),
            "schema_sha256": after.get("schema", {}).get("sha256"),
            "structural_ok": after.get("summary", {}).get("structural_ok"),
        },
        "schema": {
            "added_objects": added_objects,
            "removed_objects": removed_objects,
            "changed_objects": changed_objects,
            "schema_changed": (
                before.get("schema", {}).get("sha256")
                != after.get("schema", {}).get("sha256")
            ),
        },
        "foreign_keys": {
            "before_ok": before_fk_ok,
            "after_ok": after_fk_ok,
            "new_violations": new_fk_violations,
            "resolved_violations": resolved_fk_violations,
        },
        "rows": {
            "deltas": row_deltas,
            "decreases": row_decreases,
        },
        "regressions": regressions,
        "warnings": warnings,
        "summary": {
            "regression_free": len(regressions) == 0,
            "requires_review": bool(
                warnings or changed_objects or added_objects
            ),
            "logical_invariants_evaluated": False,
        },
    }


def write_report(path: Path, report: dict[str, Any]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compara relatórios SQLite baseline antes/depois de uma migração."
    )
    parser.add_argument("--before", required=True, type=Path)
    parser.add_argument("--after", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    try:
        report = compare_reports(
            load_report(args.before), load_report(args.after)
        )
        if args.output:
            write_report(args.output, report)
    except ComparisonError as exc:
        print(f"SQLITE_COMPARE_ERRO: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"SQLITE_COMPARE_ERRO_INESPERADO: {exc}", file=sys.stderr)
        return 2

    print(
        "SQLITE_COMPARE_OK"
        if report["summary"]["regression_free"]
        else "SQLITE_COMPARE_REGRESSION"
    )
    print(f"Objetos adicionados: {len(report['schema']['added_objects'])}")
    print(f"Objetos removidos: {len(report['schema']['removed_objects'])}")
    print(f"Objetos alterados: {len(report['schema']['changed_objects'])}")
    print(
        f"Novas violações FK: {len(report['foreign_keys']['new_violations'])}"
    )
    print(f"Avisos: {len(report['warnings'])}")
    print("Invariantes lógicas V8: NÃO AVALIADAS")
    if args.output:
        print(f"Relatório: {args.output.resolve()}")

    return 0 if report["summary"]["regression_free"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
