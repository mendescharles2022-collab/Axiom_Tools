from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import audit_db_filesystem_links as forward
import audit_filesystem_db_index as reverse


class BidirectionalAuditError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BidirectionalAuditError(f"JSON inválido {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise BidirectionalAuditError(f"JSON deve ser objeto: {path}")
    return payload


def audit_bidirectional(
    db_path: Path,
    forward_spec: dict,
    reverse_spec: dict,
    roots: dict[str, Path],
) -> dict:
    forward_report = forward.audit_links(db_path, forward_spec, roots)
    reverse_report = reverse.audit_reverse_links(db_path, reverse_spec, roots)

    forward_findings = int(forward_report["summary"]["findings"])
    reverse_findings = int(reverse_report["summary"]["findings"])
    query_errors = int(forward_report["summary"]["query_errors"]) + int(
        reverse_report["summary"]["query_errors"]
    )

    return {
        "database_name": db_path.name,
        "summary": {
            "forward_checks": int(forward_report["summary"]["checks"]),
            "reverse_scans": int(reverse_report["summary"]["scans"]),
            "query_errors": query_errors,
            "forward_findings": forward_findings,
            "reverse_findings": reverse_findings,
            "findings": forward_findings + reverse_findings,
        },
        "ok": bool(forward_report["ok"] and reverse_report["ok"]),
        "database_to_filesystem": forward_report,
        "filesystem_to_database": reverse_report,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Executa auditoria bidirecional banco ↔ filesystem do Axiom Tools "
            "em modo somente leitura."
        )
    )
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--forward-spec", required=True, type=Path)
    parser.add_argument("--reverse-spec", required=True, type=Path)
    parser.add_argument("--root-map", action="append", default=[])
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("DB_FILESYSTEM_BIDIRECTIONAL_AUDIT.json"),
    )
    args = parser.parse_args()

    try:
        roots = forward.parse_root_map(args.root_map)
        report = audit_bidirectional(
            args.db,
            load_json(args.forward_spec),
            load_json(args.reverse_spec),
            roots,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (
        BidirectionalAuditError,
        forward.LinkAuditError,
        reverse.ReverseLinkAuditError,
        OSError,
        ValueError,
        TypeError,
    ) as exc:
        print(f"DB_FILESYSTEM_BIDIRECTIONAL_ERRO: {exc}", file=sys.stderr)
        return 2

    print(
        "DB_FILESYSTEM_BIDIRECTIONAL_OK"
        if report["ok"]
        else "DB_FILESYSTEM_BIDIRECTIONAL_FALHA"
    )
    print(f"Checks banco→filesystem: {report['summary']['forward_checks']}")
    print(f"Scans filesystem→banco: {report['summary']['reverse_scans']}")
    print(f"Erros SQL: {report['summary']['query_errors']}")
    print(f"Achados: {report['summary']['findings']}")
    print(f"Relatório: {args.output.resolve()}")
    return 0 if report["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
