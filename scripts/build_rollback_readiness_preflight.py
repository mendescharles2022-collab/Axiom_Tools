from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path, PurePosixPath

import build_database_homologation_preflight as db_preflight
import create_rollback_bundle as bundle
import restore_rollback_bundle as restore
import verify_rollback_bundle as verify

REPORT_VERSION = 1
REQUIRED_ROLES = {"code", "config"}


class RollbackReadinessError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RollbackReadinessError(f"JSON inválido {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise RollbackReadinessError(f"JSON deve ser objeto: {path}")
    return payload


def normalize_plan(plan: dict) -> dict:
    if not isinstance(plan, dict) or plan.get("version") != bundle.PLAN_VERSION:
        raise RollbackReadinessError(
            f"Plano deve ser objeto version={bundle.PLAN_VERSION}."
        )
    files = plan.get("files")
    if not isinstance(files, list) or not files:
        raise RollbackReadinessError("Plano de rollback vazio.")

    normalized = []
    seen = set()
    roles = set()
    for item in files:
        if not isinstance(item, dict):
            raise RollbackReadinessError("Entrada inválida no plano de rollback.")
        try:
            rel = bundle._safe_relative(str(item.get("path", "")))
        except bundle.RollbackError as exc:
            raise RollbackReadinessError(str(exc)) from exc
        if rel in seen:
            raise RollbackReadinessError(f"Caminho duplicado no plano: {rel}")
        seen.add(rel)
        role = str(item.get("role", "code")).strip().lower()
        if role not in bundle.ROLES:
            raise RollbackReadinessError(f"Role inválida para {rel}: {role!r}")
        roles.add(role)
        normalized.append({"path": rel, "role": role})

    missing_roles = sorted(REQUIRED_ROLES - roles)
    if missing_roles:
        raise RollbackReadinessError(
            "Plano não cobre papéis mínimos: " + ", ".join(missing_roles)
        )
    return {"version": bundle.PLAN_VERSION, "files": normalized}


def snapshot_sources(source_root: Path, db_path: Path, plan: dict) -> dict:
    source_root = source_root.resolve()
    if not source_root.is_dir():
        raise RollbackReadinessError(f"source-root inválido: {source_root}")

    files = []
    for item in plan["files"]:
        rel = item["path"]
        target = source_root / Path(*PurePosixPath(rel).parts)
        resolved = target.resolve()
        try:
            resolved.relative_to(source_root)
        except ValueError as exc:
            raise RollbackReadinessError(f"Arquivo fora de source-root: {rel}") from exc
        if target.is_symlink() or not target.is_file():
            raise RollbackReadinessError(f"Arquivo ausente/inválido: {rel}")
        stat = target.stat()
        files.append(
            {
                "path": rel,
                "role": item["role"],
                "length": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
                "sha256": bundle.sha256_file(target),
            }
        )

    try:
        database = db_preflight.file_snapshot(db_path)
    except db_preflight.DatabasePreflightError as exc:
        raise RollbackReadinessError(str(exc)) from exc

    return {
        "files": files,
        "database": database,
    }


def build_rollback_readiness(
    *,
    source_root: Path,
    db_path: Path,
    plan: dict,
    invariant_spec: dict,
    work_dir: Path,
    app_version: str,
    schema_version: str,
    commit_sha: str,
) -> dict:
    normalized_plan = normalize_plan(plan)
    source_root = source_root.resolve()
    db_path = db_path.resolve()
    work_dir = work_dir.resolve()
    if work_dir.exists():
        raise RollbackReadinessError(f"work-dir já existe: {work_dir}")

    before = snapshot_sources(source_root, db_path, normalized_plan)
    partial = work_dir.with_name(work_dir.name + ".partial")
    if partial.exists():
        raise RollbackReadinessError(f"work-dir parcial já existe: {partial}")
    partial.mkdir(parents=True)

    try:
        bundle_dir = partial / "rollback-bundle"
        restored_dir = partial / "restore-rehearsal"

        try:
            manifest = bundle.create_bundle(
                source_root=source_root,
                db_path=db_path,
                plan=normalized_plan,
                output_dir=bundle_dir,
                app_version=app_version,
                schema_version=schema_version,
                commit_sha=commit_sha,
            )
        except bundle.RollbackError as exc:
            raise RollbackReadinessError(str(exc)) from exc

        try:
            verification = verify.verify_bundle(bundle_dir)
        except verify.VerificationError as exc:
            raise RollbackReadinessError(str(exc)) from exc

        try:
            rehearsal = restore.restore_to_staging(bundle_dir, restored_dir)
        except restore.RestoreError as exc:
            raise RollbackReadinessError(str(exc)) from exc

        restored_db = restored_dir / "database" / "axiom_tools.sqlite3"
        try:
            restored_db_report = db_preflight.build_database_preflight(
                restored_db,
                invariant_spec,
                include_row_counts=True,
            )
        except db_preflight.DatabasePreflightError as exc:
            raise RollbackReadinessError(str(exc)) from exc

        after = snapshot_sources(source_root, db_path, normalized_plan)
        source_unchanged = before == after
        restored_db_ok = bool(restored_db_report["summary"]["all_ok"])
        all_ok = (
            source_unchanged
            and bool(verification.get("ok"))
            and bool(rehearsal.get("ok"))
            and restored_db_ok
        )

        report = {
            "report_version": REPORT_VERSION,
            "mode": "ROLLBACK_READINESS_REHEARSAL_ONLY",
            "identity": {
                "app_version": manifest["app_version"],
                "schema_version": manifest["schema_version"],
                "commit_sha": manifest["commit_sha"],
            },
            "coverage": {
                "required_roles": sorted(REQUIRED_ROLES),
                "roles_present": sorted(
                    {item["role"] for item in normalized_plan["files"]}
                ),
                "file_count": len(normalized_plan["files"]),
                "database_included": True,
            },
            "source_snapshot": {
                "before": before,
                "after": after,
                "unchanged_during_rehearsal": source_unchanged,
            },
            "bundle": {
                "manifest_sha256": manifest["manifest_sha256"],
                "database_sha256": manifest["database"]["sha256"],
                "verification": verification,
            },
            "restore_rehearsal": rehearsal,
            "restored_database_preflight": restored_db_report,
            "summary": {
                "source_unchanged": source_unchanged,
                "bundle_verified": bool(verification.get("ok")),
                "restore_rehearsal_ok": bool(rehearsal.get("ok")),
                "restored_database_ok": restored_db_ok,
                "ready_for_windows_rehearsal": all_ok,
            },
            "warning": (
                "Este preflight cria bundle e restaura somente em staging novo. "
                "Não substitui arquivos da instalação e não prova ainda rollback físico Windows."
            ),
        }
        (partial / "ROLLBACK_READINESS_PREFLIGHT.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        partial.replace(work_dir)
        return report
    except Exception:
        shutil.rmtree(partial, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Cria e verifica um ensaio completo de prontidão de rollback V8 em staging, "
            "sem sobrescrever a instalação."
        )
    )
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--invariants", required=True, type=Path)
    parser.add_argument("--work-dir", required=True, type=Path)
    parser.add_argument("--app-version", required=True)
    parser.add_argument("--schema-version", required=True)
    parser.add_argument("--commit-sha", required=True)
    args = parser.parse_args()

    try:
        report = build_rollback_readiness(
            source_root=args.source_root,
            db_path=args.db,
            plan=load_json(args.plan),
            invariant_spec=load_json(args.invariants),
            work_dir=args.work_dir,
            app_version=args.app_version,
            schema_version=args.schema_version,
            commit_sha=args.commit_sha,
        )
    except RollbackReadinessError as exc:
        print(f"ROLLBACK_READINESS_ERRO: {exc}", file=sys.stderr)
        return 2

    print(
        "ROLLBACK_READINESS_OK"
        if report["summary"]["ready_for_windows_rehearsal"]
        else "ROLLBACK_READINESS_FALHA"
    )
    print(f"Arquivos cobertos: {report['coverage']['file_count']}")
    print(f"Bundle: {report['bundle']['manifest_sha256']}")
    print(
        "Origem inalterada: "
        f"{'SIM' if report['summary']['source_unchanged'] else 'NÃO'}"
    )
    print("Instalação substituída: NÃO")
    return 0 if report["summary"]["ready_for_windows_rehearsal"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
