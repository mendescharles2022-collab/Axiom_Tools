from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.parse import quote

PLAN_VERSION = 1
MANIFEST_NAME = "ROLLBACK_MANIFEST.json"
IDENTITY_RE = re.compile(r"^[A-Za-z0-9._+\-]+$")
ROLES = {"code", "config", "script", "asset"}


class RollbackError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def _safe_relative(raw: str) -> str:
    text = raw.replace("\\", "/").strip()
    pure = PurePosixPath(text)
    if not text or pure.is_absolute() or ".." in pure.parts or not pure.parts:
        raise RollbackError(f"Caminho relativo inválido no plano: {raw!r}")
    if pure.parts[0].endswith(":") or "\x00" in text:
        raise RollbackError(f"Caminho relativo inválido no plano: {raw!r}")
    return pure.as_posix()


def load_plan(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RollbackError(f"Plano inexistente: {path}") from exc
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RollbackError(f"Plano inválido: {exc}") from exc
    if not isinstance(data, dict) or data.get("version") != PLAN_VERSION:
        raise RollbackError(f"Plano deve ser objeto version={PLAN_VERSION}.")
    files = data.get("files")
    if not isinstance(files, list) or not files:
        raise RollbackError("Plano deve conter lista não vazia 'files'.")
    normalized = []
    seen = set()
    for idx, item in enumerate(files, start=1):
        if not isinstance(item, dict):
            raise RollbackError(f"Entrada #{idx} do plano deve ser objeto.")
        rel = _safe_relative(str(item.get("path", "")))
        if rel in seen:
            raise RollbackError(f"Caminho duplicado no plano: {rel}")
        seen.add(rel)
        role = str(item.get("role", "code")).strip().lower()
        if role not in ROLES:
            raise RollbackError(f"Role inválida para {rel}: {role!r}")
        normalized.append({"path": rel, "role": role})
    return {"version": PLAN_VERSION, "files": normalized}


def _validate_identity(value: str, field: str) -> str:
    value = value.strip()
    if not value or not IDENTITY_RE.fullmatch(value):
        raise RollbackError(f"{field} inválido: {value!r}")
    return value


def _copy_sqlite_consistent(source: Path, destination: Path) -> dict:
    source = source.resolve()
    if not source.is_file():
        raise RollbackError(f"Banco inexistente: {source}")
    uri = "file:" + quote(source.as_posix(), safe="/:") + "?mode=ro"
    source_conn = sqlite3.connect(uri, uri=True)
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        dest_conn = sqlite3.connect(destination)
        try:
            source_conn.backup(dest_conn)
            dest_conn.commit()
        finally:
            dest_conn.close()
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        source_conn.close()

    check = sqlite3.connect(destination)
    try:
        integrity = [row[0] for row in check.execute("PRAGMA integrity_check")]
        fk = [list(row) for row in check.execute("PRAGMA foreign_key_check")]
        user_version = int(check.execute("PRAGMA user_version").fetchone()[0])
    finally:
        check.close()
    if integrity != ["ok"]:
        raise RollbackError(f"Backup SQLite falhou no integrity_check: {integrity}")
    if fk:
        raise RollbackError(f"Backup SQLite possui violações de FK: {len(fk)}")
    return {
        "user_version": user_version,
        "integrity_check": "ok",
        "foreign_key_violations": 0,
    }


def create_bundle(
    *,
    source_root: Path,
    db_path: Path,
    plan: dict,
    output_dir: Path,
    app_version: str,
    schema_version: str,
    commit_sha: str,
) -> dict:
    source_root = source_root.resolve()
    db_path = db_path.resolve()
    output_dir = output_dir.resolve()
    if not source_root.is_dir():
        raise RollbackError(f"source-root inválido: {source_root}")
    if output_dir.exists():
        raise RollbackError(f"Destino já existe: {output_dir}")

    app_version = _validate_identity(app_version, "app_version")
    schema_version = _validate_identity(schema_version, "schema_version")
    commit_sha = _validate_identity(commit_sha, "commit_sha")

    normalized_plan = {"version": PLAN_VERSION, "files": []}
    seen = set()
    for item in plan.get("files", []):
        rel = _safe_relative(str(item.get("path", "")))
        if rel in seen:
            raise RollbackError(f"Caminho duplicado no plano: {rel}")
        seen.add(rel)
        role = str(item.get("role", "code")).strip().lower()
        if role not in ROLES:
            raise RollbackError(f"Role inválida para {rel}: {role!r}")
        normalized_plan["files"].append({"path": rel, "role": role})
    if not normalized_plan["files"]:
        raise RollbackError("Plano vazio.")

    partial = output_dir.with_name(output_dir.name + ".partial")
    if partial.exists():
        raise RollbackError(f"Destino parcial já existe: {partial}")
    partial.mkdir(parents=True)

    try:
        copied = []
        for item in normalized_plan["files"]:
            rel = item["path"]
            source = source_root / Path(*PurePosixPath(rel).parts)
            resolved = source.resolve()
            try:
                resolved.relative_to(source_root)
            except ValueError as exc:
                raise RollbackError(f"Arquivo fora de source-root: {rel}") from exc
            if source.is_symlink() or not source.is_file():
                raise RollbackError(f"Arquivo ausente/inválido no plano: {rel}")
            target = partial / "files" / Path(*PurePosixPath(rel).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            copied.append(
                {
                    "path": rel,
                    "role": item["role"],
                    "length": target.stat().st_size,
                    "sha256": sha256_file(target),
                }
            )

        db_target = partial / "database" / "axiom_tools.sqlite3"
        db_meta = _copy_sqlite_consistent(db_path, db_target)

        manifest = {
            "format_version": 1,
            "product": "Axiom Tools",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "app_version": app_version,
            "schema_version": schema_version,
            "commit_sha": commit_sha,
            "files": copied,
            "database": {
                "path": "database/axiom_tools.sqlite3",
                "length": db_target.stat().st_size,
                "sha256": sha256_file(db_target),
                **db_meta,
            },
        }
        manifest_payload = json.dumps(
            manifest,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        manifest["manifest_sha256"] = hashlib.sha256(manifest_payload).hexdigest().upper()
        (partial / MANIFEST_NAME).write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        partial.replace(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(partial, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Cria bundle local e verificável para rollback do Axiom Tools."
    )
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--app-version", required=True)
    parser.add_argument("--schema-version", required=True)
    parser.add_argument("--commit-sha", required=True)
    args = parser.parse_args()

    try:
        plan = load_plan(args.plan)
        manifest = create_bundle(
            source_root=args.source_root,
            db_path=args.db,
            plan=plan,
            output_dir=args.output_dir,
            app_version=args.app_version,
            schema_version=args.schema_version,
            commit_sha=args.commit_sha,
        )
    except RollbackError as exc:
        print(f"ROLLBACK_BUNDLE_ERRO: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ROLLBACK_BUNDLE_ERRO_INESPERADO: {exc}", file=sys.stderr)
        return 3

    print("ROLLBACK_BUNDLE_OK")
    print(f"Destino: {args.output_dir.resolve()}")
    print(f"Arquivos: {len(manifest['files'])}")
    print(f"Banco SHA256: {manifest['database']['sha256']}")
    print(f"Manifesto SHA256: {manifest['manifest_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
