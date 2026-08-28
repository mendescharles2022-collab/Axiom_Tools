from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import audit_sqlite_baseline as baseline


class CloneError(RuntimeError):
    pass


def clone_database(
    source: Path,
    destination: Path,
    *,
    include_row_counts: bool = True,
    require_structural_ok: bool = True,
) -> dict[str, Any]:
    source = source.resolve()
    destination = destination.resolve()

    if not source.is_file():
        raise CloneError(f"Banco de origem não encontrado: {source}")
    if source == destination:
        raise CloneError("Origem e destino não podem ser o mesmo arquivo.")
    if destination.exists():
        raise CloneError(
            f"Destino já existe; cópia não será sobrescrita: {destination}"
        )

    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".partial")
    if partial.exists():
        raise CloneError(
            f"Arquivo parcial já existe; revise antes de continuar: {partial}"
        )

    source_report = baseline.audit_database(
        source, include_row_counts=include_row_counts
    )
    if require_structural_ok and not source_report["summary"]["structural_ok"]:
        raise CloneError(
            "Baseline da origem possui divergência estrutural/FK; "
            "a cópia de migração foi bloqueada."
        )

    try:
        source_connection = baseline.connect_read_only(source)
        try:
            destination_connection = sqlite3.connect(partial)
            try:
                source_connection.backup(destination_connection)
                destination_connection.commit()
            finally:
                destination_connection.close()
        finally:
            source_connection.close()

        destination_report = baseline.audit_database(
            partial, include_row_counts=include_row_counts
        )

        mismatches: list[str] = []
        if (
            source_report["schema"]["sha256"]
            != destination_report["schema"]["sha256"]
        ):
            mismatches.append("schema_sha256")
        if (
            source_report["database"]["user_version"]
            != destination_report["database"]["user_version"]
        ):
            mismatches.append("user_version")
        if (
            source_report["database"]["application_id"]
            != destination_report["database"]["application_id"]
        ):
            mismatches.append("application_id")
        if (
            include_row_counts
            and source_report["row_counts"] != destination_report["row_counts"]
        ):
            mismatches.append("row_counts")
        if (
            source_report["summary"]["integrity_ok"]
            != destination_report["summary"]["integrity_ok"]
        ):
            mismatches.append("integrity_status")
        if (
            source_report["foreign_keys"]["violations"]
            != destination_report["foreign_keys"]["violations"]
        ):
            mismatches.append("foreign_key_violations")

        if mismatches:
            raise CloneError(
                "Cópia SQLite divergiu da origem nos controles: "
                + ", ".join(mismatches)
                + ". Interrompa a migração e revise se o banco estava ativo."
            )

        if (
            require_structural_ok
            and not destination_report["summary"]["structural_ok"]
        ):
            raise CloneError("Cópia gerada não passou na auditoria estrutural.")

        os.replace(partial, destination)

        return {
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "source": {
                "name": source.name,
                "schema_sha256": source_report["schema"]["sha256"],
                "user_version": source_report["database"]["user_version"],
                "structural_ok": source_report["summary"]["structural_ok"],
            },
            "destination": {
                "name": destination.name,
                "schema_sha256": destination_report["schema"]["sha256"],
                "user_version": destination_report["database"]["user_version"],
                "structural_ok": destination_report["summary"]["structural_ok"],
                "size_bytes": destination.stat().st_size,
            },
            "checks": {
                "schema_equal": True,
                "user_version_equal": True,
                "application_id_equal": True,
                "row_counts_compared": include_row_counts,
                "row_counts_equal": True if include_row_counts else None,
                "integrity_status_equal": True,
                "foreign_key_violations_equal": True,
            },
            "migration_ready_copy": bool(
                destination_report["summary"]["structural_ok"]
            ),
            "logical_invariants_evaluated": False,
        }
    except Exception:
        if partial.exists():
            partial.unlink(missing_ok=True)
        if destination.exists():
            # O destino só é promovido atomicamente após as validações.
            # Esta limpeza defensiva protege futuras alterações no código.
            destination.unlink(missing_ok=True)
        raise


def write_report(path: Path, report: dict[str, Any]) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Cria uma cópia SQLite consistente para ensaio de migração. "
            "Nunca sobrescreve o destino."
        )
    )
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--skip-row-counts", action="store_true")
    parser.add_argument(
        "--allow-structural-divergence",
        action="store_true",
        help=(
            "Uso diagnóstico. Permite copiar origem com integrity/FK divergente, "
            "mas não transforma a cópia em homologável."
        ),
    )
    args = parser.parse_args()

    try:
        report = clone_database(
            args.source,
            args.destination,
            include_row_counts=not args.skip_row_counts,
            require_structural_ok=not args.allow_structural_divergence,
        )
        if args.report:
            write_report(args.report, report)
    except (CloneError, baseline.DatabaseAuditError) as exc:
        print(f"SQLITE_CLONE_ERRO: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"SQLITE_CLONE_ERRO_INESPERADO: {exc}", file=sys.stderr)
        return 2

    print("SQLITE_CLONE_OK")
    print(f"Origem: {report['source']['name']}")
    print(f"Destino: {report['destination']['name']}")
    print(f"Schema: {report['destination']['schema_sha256']}")
    print("Invariantes lógicas V8: NÃO AVALIADAS")
    if args.report:
        print(f"Relatório: {args.report.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
