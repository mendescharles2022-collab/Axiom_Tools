from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import clone_sqlite_for_migration as sqlite_clone
import export_runtime_reconciliation as runtime_export

HANDOFF_VERSION = 1
MANIFEST_NAME = "RUNTIME_HANDOFF_MANIFEST.json"
DB_REPORT_NAME = "RUNTIME_DATABASE_CLONE_REPORT.json"
LABEL_RE = re.compile(r"^[A-Za-z0-9._-]+$")


class RuntimeHandoffError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_hash(value: object) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def _assert_output_outside_runtime(runtime_root: Path, output_dir: Path) -> None:
    runtime_root = runtime_root.resolve()
    output_dir = output_dir.resolve()
    try:
        output_dir.relative_to(runtime_root)
    except ValueError:
        return
    raise RuntimeHandoffError(
        "Diretório de saída deve ficar fora da raiz operacional do Axiom Tools."
    )


def _assert_database_not_output(database: Path, output_dir: Path) -> None:
    database = database.resolve()
    output_dir = output_dir.resolve()
    try:
        database.relative_to(output_dir)
    except ValueError:
        return
    raise RuntimeHandoffError(
        "Banco de origem não pode estar dentro do diretório de saída do handoff."
    )


def _safe_label(label: str) -> str:
    text = label.strip()
    if not LABEL_RE.fullmatch(text):
        raise RuntimeHandoffError(
            "Label inválido; use apenas letras, números, ponto, sublinhado ou hífen."
        )
    return text


def _remove_artifact(path: Path) -> None:
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        path.unlink(missing_ok=True)


def build_handoff(
    *,
    runtime_root: Path,
    database: Path,
    output_dir: Path,
    label: str = "runtime-v8",
    include_row_counts: bool = True,
) -> dict:
    runtime_root = runtime_root.resolve()
    database = database.resolve()
    output_dir = output_dir.resolve()
    label = _safe_label(label)

    if not runtime_root.is_dir():
        raise RuntimeHandoffError(f"Raiz operacional inválida: {runtime_root}")
    if not database.is_file():
        raise RuntimeHandoffError(f"Banco operacional não encontrado: {database}")
    _assert_output_outside_runtime(runtime_root, output_dir)
    _assert_database_not_output(database, output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    handoff_dir = output_dir / f"{label}-handoff"
    if handoff_dir.exists():
        raise RuntimeHandoffError(
            f"Destino do handoff já existe: {handoff_dir.name}"
        )

    runtime_hash_before = None
    database_hash_before = sha256_file(database)
    handoff_dir.mkdir(parents=True)
    export_result = None
    try:
        export_result = runtime_export.export_runtime(
            runtime_root,
            handoff_dir,
            f"{label}-code",
        )

        db_copy = handoff_dir / f"{label}-database.sqlite3"
        db_report = sqlite_clone.clone_database(
            database,
            db_copy,
            include_row_counts=include_row_counts,
            require_structural_ok=False,
        )
        sqlite_clone.write_report(handoff_dir / DB_REPORT_NAME, db_report)

        database_hash_after = sha256_file(database)
        if database_hash_after != database_hash_before:
            raise RuntimeHandoffError(
                "Banco operacional mudou durante a coleta; descarte o handoff e repita."
            )

        code_zip = export_result.zip_path
        manifest = {
            "version": HANDOFF_VERSION,
            "mode": "RUNTIME_RECONCILIATION_HANDOFF_NOT_HOMOLOGATION",
            "product": "Axiom Tools",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "label": label,
            "source": {
                "runtime_root_name": runtime_root.name,
                "database_name": database.name,
                "database_sha256_before": database_hash_before,
                "database_sha256_after": database_hash_after,
                "source_mutation_performed": False,
            },
            "code_export": {
                "zip": code_zip.name,
                "zip_sha256": sha256_file(code_zip),
                "file_count": export_result.file_count,
                "stage_directory": export_result.stage.name,
                "database_in_code_zip": False,
            },
            "database_copy": {
                "file": db_copy.name,
                "sha256": sha256_file(db_copy),
                "size_bytes": db_copy.stat().st_size,
                "schema_sha256": db_report["destination"]["schema_sha256"],
                "user_version": db_report["destination"]["user_version"],
                "structural_ok": db_report["destination"]["structural_ok"],
                "migration_ready_copy": db_report["migration_ready_copy"],
                "report": DB_REPORT_NAME,
                "kept_separate_from_code_zip": True,
            },
            "warnings": [
                "Este handoff não homologa a V8.",
                "A cópia SQLite pode preservar divergências estruturais do runtime para diagnóstico.",
                "O banco permanece separado do ZIP versionável de código/configuração.",
            ],
        }
        manifest["manifest_sha256"] = canonical_hash(manifest)
        manifest_path = handoff_dir / MANIFEST_NAME
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        return {
            "handoff_dir": handoff_dir.name,
            "manifest": manifest,
            "manifest_file": MANIFEST_NAME,
            "code_zip": code_zip.name,
            "database_copy": db_copy.name,
            "database_report": DB_REPORT_NAME,
        }
    except Exception:
        _remove_artifact(handoff_dir)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Coleta em uma única execução o handoff seguro B06: código/config em ZIP "
            "e cópia SQLite consistente separada, unidos por manifesto SHA-256."
        )
    )
    parser.add_argument("--runtime-root", required=True, type=Path)
    parser.add_argument("--database", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--label", default="runtime-v8")
    parser.add_argument("--skip-row-counts", action="store_true")
    args = parser.parse_args()

    try:
        result = build_handoff(
            runtime_root=args.runtime_root,
            database=args.database,
            output_dir=args.output_dir,
            label=args.label,
            include_row_counts=not args.skip_row_counts,
        )
    except (
        RuntimeHandoffError,
        runtime_export.ExportError,
        sqlite_clone.CloneError,
    ) as exc:
        print(f"RUNTIME_HANDOFF_ERRO: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"RUNTIME_HANDOFF_ERRO_INESPERADO: {exc}", file=sys.stderr)
        return 3

    print("RUNTIME_HANDOFF_OK")
    print(f"Diretório: {result['handoff_dir']}")
    print(f"Manifesto: {result['manifest_file']}")
    print(f"Código: {result['code_zip']}")
    print(f"Banco: {result['database_copy']}")
    print(f"Relatório DB: {result['database_report']}")
    print(f"Manifesto SHA256: {result['manifest']['manifest_sha256']}")
    print("Origem alterada: NÃO")
    print("V8 homologada: NÃO")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
