from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import audit_db_filesystem_bidirectional as links
import audit_db_filesystem_links as link_base
import audit_sqlite_baseline as baseline
import run_sqlite_invariants as invariants

REPORT_VERSION = 1


class DatabasePreflightError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def file_snapshot(path: Path) -> dict:
    resolved = path.resolve()
    if not resolved.is_file():
        raise DatabasePreflightError(f"Banco inexistente: {resolved}")
    stat = resolved.stat()
    return {
        "name": resolved.name,
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sha256": sha256_file(resolved),
    }


def load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise DatabasePreflightError(f"JSON inválido {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise DatabasePreflightError(f"JSON deve ser objeto: {path}")
    return payload


def build_database_preflight(
    database: Path,
    invariant_spec: dict,
    *,
    include_row_counts: bool = True,
    forward_spec: dict | None = None,
    reverse_spec: dict | None = None,
    roots: dict[str, Path] | None = None,
) -> dict:
    database = database.resolve()
    if (forward_spec is None) != (reverse_spec is None):
        raise DatabasePreflightError(
            "Auditoria de acervo exige forward_spec e reverse_spec juntos."
        )
    if forward_spec is not None and not roots:
        raise DatabasePreflightError(
            "Auditoria de acervo exige roots autorizadas."
        )

    before = file_snapshot(database)

    try:
        structural = baseline.audit_database(
            database,
            include_row_counts=include_row_counts,
        )
    except baseline.DatabaseAuditError as exc:
        raise DatabasePreflightError(str(exc)) from exc

    try:
        logical = invariants.run_invariants(database, invariant_spec)
    except invariants.InvariantError as exc:
        raise DatabasePreflightError(str(exc)) from exc

    acervo = None
    if forward_spec is not None and reverse_spec is not None:
        assert roots is not None
        try:
            acervo = links.audit_bidirectional(
                database,
                forward_spec,
                reverse_spec,
                roots,
            )
        except (
            link_base.LinkAuditError,
            links.reverse.ReverseLinkAuditError,
        ) as exc:
            raise DatabasePreflightError(str(exc)) from exc

    after = file_snapshot(database)
    source_unchanged = before == after

    structural_ok = bool(structural["summary"]["structural_ok"])
    logical_ok = bool(logical["ok"])
    acervo_ok = None if acervo is None else bool(acervo["ok"])
    all_ok = (
        source_unchanged
        and structural_ok
        and logical_ok
        and (acervo_ok is not False)
    )

    return {
        "report_version": REPORT_VERSION,
        "mode": "READ_ONLY_HOMOLOGATION_PREFLIGHT",
        "database_snapshot": {
            "before": before,
            "after": after,
            "unchanged_during_audit": source_unchanged,
        },
        "structural": structural,
        "logical_invariants": logical,
        "filesystem_links": acervo,
        "summary": {
            "source_unchanged": source_unchanged,
            "integrity_ok": bool(structural["summary"]["integrity_ok"]),
            "foreign_keys_ok": bool(structural["summary"]["foreign_keys_ok"]),
            "structural_ok": structural_ok,
            "logical_invariants_ok": logical_ok,
            "logical_total": int(logical["summary"]["total"]),
            "logical_passed": int(logical["summary"]["passed"]),
            "filesystem_links_evaluated": acervo is not None,
            "filesystem_links_ok": acervo_ok,
            "all_ok": all_ok,
        },
        "warning": (
            "Preflight somente leitura. Resultado válido apenas para a fotografia "
            "SHA-256 registrada; não executa migração, saneamento ou alteração do banco."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Consolida integrity_check, foreign_key_check, invariantes lógicas e "
            "opcionalmente banco ↔ filesystem em uma cópia SQLite do Axiom Tools."
        )
    )
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--invariants", required=True, type=Path)
    parser.add_argument("--forward-spec", type=Path, default=None)
    parser.add_argument("--reverse-spec", type=Path, default=None)
    parser.add_argument("--root-map", action="append", default=[])
    parser.add_argument("--skip-row-counts", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("DATABASE_HOMOLOGATION_PREFLIGHT.json"),
    )
    args = parser.parse_args()

    try:
        roots = (
            link_base.parse_root_map(args.root_map)
            if args.forward_spec or args.reverse_spec
            else None
        )
        report = build_database_preflight(
            args.database,
            load_json(args.invariants),
            include_row_counts=not args.skip_row_counts,
            forward_spec=(
                load_json(args.forward_spec) if args.forward_spec else None
            ),
            reverse_spec=(
                load_json(args.reverse_spec) if args.reverse_spec else None
            ),
            roots=roots,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (
        DatabasePreflightError,
        link_base.LinkAuditError,
        OSError,
    ) as exc:
        print(f"DATABASE_HOMOLOGATION_PREFLIGHT_ERRO: {exc}", file=sys.stderr)
        return 2

    print(
        "DATABASE_HOMOLOGATION_PREFLIGHT_OK"
        if report["summary"]["all_ok"]
        else "DATABASE_HOMOLOGATION_PREFLIGHT_FALHA"
    )
    print(f"Banco: {report['database_snapshot']['before']['name']}")
    print(f"SHA256: {report['database_snapshot']['before']['sha256']}")
    print(
        "integrity_check: "
        f"{'OK' if report['summary']['integrity_ok'] else 'FALHA'}"
    )
    print(
        "foreign_key_check: "
        f"{'OK' if report['summary']['foreign_keys_ok'] else 'FALHA'}"
    )
    print(
        "invariantes: "
        f"{report['summary']['logical_passed']}/{report['summary']['logical_total']}"
    )
    print(
        "snapshot imutável durante auditoria: "
        f"{'SIM' if report['summary']['source_unchanged'] else 'NÃO'}"
    )
    print(f"Relatório: {args.output.resolve()}")
    return 0 if report["summary"]["all_ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
