from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sqlite3
import sys
from pathlib import Path, PurePosixPath

SCRIPT_DIR = Path(__file__).resolve().parent
VERIFY_SCRIPT = SCRIPT_DIR / "verify_rollback_bundle.py"


def _load_verifier():
    spec = importlib.util.spec_from_file_location(
        "verify_rollback_bundle", VERIFY_SCRIPT
    )
    if not spec or not spec.loader:
        raise RuntimeError(f"Não foi possível carregar {VERIFY_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


verifier = _load_verifier()


class RestoreError(RuntimeError):
    pass


def restore_to_staging(bundle: Path, destination: Path) -> dict:
    bundle = bundle.resolve()
    destination = destination.resolve()
    if destination.exists():
        raise RestoreError(f"Destino já existe: {destination}")

    try:
        verification = verifier.verify_bundle(bundle)
    except verifier.VerificationError as exc:
        raise RestoreError(f"Bundle inválido: {exc}") from exc

    manifest = json.loads(
        (bundle / verifier.MANIFEST_NAME).read_text(encoding="utf-8")
    )
    partial = destination.with_name(destination.name + ".partial")
    if partial.exists():
        raise RestoreError(f"Destino parcial já existe: {partial}")
    partial.mkdir(parents=True)

    try:
        for item in manifest["files"]:
            rel = PurePosixPath(item["path"])
            source = bundle / "files" / Path(*rel.parts)
            target = partial / "files" / Path(*rel.parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

        db_source = bundle / Path(
            *PurePosixPath(manifest["database"]["path"]).parts
        )
        db_target = partial / "database" / "axiom_tools.sqlite3"
        db_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(db_source, db_target)

        for item in manifest["files"]:
            rel = PurePosixPath(item["path"])
            target = partial / "files" / Path(*rel.parts)
            if target.stat().st_size != int(item["length"]):
                raise RestoreError(
                    f"Tamanho divergente após restauração: {item['path']}"
                )
            if verifier.sha256_file(target) != str(item["sha256"]).upper():
                raise RestoreError(
                    f"SHA256 divergente após restauração: {item['path']}"
                )

        if db_target.stat().st_size != int(manifest["database"]["length"]):
            raise RestoreError("Tamanho do banco divergente após restauração.")
        if verifier.sha256_file(db_target) != str(
            manifest["database"]["sha256"]
        ).upper():
            raise RestoreError("SHA256 do banco divergente após restauração.")

        conn = sqlite3.connect(
            f"file:{db_target.as_posix()}?mode=ro", uri=True
        )
        try:
            integrity = [
                row[0] for row in conn.execute("PRAGMA integrity_check")
            ]
            fk = list(conn.execute("PRAGMA foreign_key_check"))
        finally:
            conn.close()
        if integrity != ["ok"]:
            raise RestoreError(
                f"Banco restaurado falhou integrity_check: {integrity}"
            )
        if fk:
            raise RestoreError(
                f"Banco restaurado possui violações de FK: {len(fk)}"
            )

        (partial / "RESTORE_REHEARSAL.json").write_text(
            json.dumps(
                {
                    "product": "Axiom Tools",
                    "source_manifest_sha256": manifest["manifest_sha256"],
                    "app_version": manifest.get("app_version"),
                    "schema_version": manifest.get("schema_version"),
                    "commit_sha": manifest.get("commit_sha"),
                    "file_count": len(manifest["files"]),
                    "database_sha256": manifest["database"]["sha256"],
                    "verification": verification,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        partial.replace(destination)
        return {
            "ok": True,
            "destination": destination.name,
            "file_count": len(manifest["files"]),
            "database_sha256": manifest["database"]["sha256"],
            "manifest_sha256": manifest["manifest_sha256"],
        }
    except Exception:
        shutil.rmtree(partial, ignore_errors=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Restaura bundle V8 em diretório novo para ensaio de rollback; "
            "nunca sobrescreve instalação existente."
        )
    )
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--destination", required=True, type=Path)
    args = parser.parse_args()

    try:
        result = restore_to_staging(args.bundle, args.destination)
    except RestoreError as exc:
        print(f"ROLLBACK_RESTORE_ERRO: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ROLLBACK_RESTORE_ERRO_INESPERADO: {exc}", file=sys.stderr)
        return 3

    print("ROLLBACK_RESTORE_OK")
    print(f"Destino: {args.destination.resolve()}")
    print(f"Arquivos: {result['file_count']}")
    print(f"Banco SHA256: {result['database_sha256']}")
    print(f"Manifesto SHA256: {result['manifest_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
