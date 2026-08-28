from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from pathlib import Path, PurePosixPath

MANIFEST_NAME = "ROLLBACK_MANIFEST.json"


class VerificationError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()


def _safe(bundle: Path, raw: str) -> tuple[str, Path]:
    text = raw.replace("\\", "/").strip()
    pure = PurePosixPath(text)
    if (
        not text
        or pure.is_absolute()
        or ".." in pure.parts
        or pure.parts[0].endswith(":")
        or "\x00" in text
    ):
        raise VerificationError(f"Caminho inseguro no manifesto: {raw!r}")
    target = (bundle / Path(*pure.parts)).resolve()
    try:
        target.relative_to(bundle.resolve())
    except ValueError as exc:
        raise VerificationError(f"Caminho fora do bundle: {raw!r}") from exc
    return pure.as_posix(), target


def _canonical_manifest_hash(manifest: dict) -> str:
    payload = dict(manifest)
    payload.pop("manifest_sha256", None)
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest().upper()


def verify_bundle(bundle: Path) -> dict:
    bundle = bundle.resolve()
    if not bundle.is_dir():
        raise VerificationError(f"Bundle inválido: {bundle}")

    manifest_path = bundle / MANIFEST_NAME
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise VerificationError(f"Manifesto inválido: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("format_version") != 1:
        raise VerificationError("Formato de manifesto não suportado.")
    if manifest.get("manifest_sha256") != _canonical_manifest_hash(manifest):
        raise VerificationError("Hash próprio do manifesto divergente.")

    expected = {MANIFEST_NAME}
    files = manifest.get("files")
    if not isinstance(files, list):
        raise VerificationError("Lista files inválida.")
    seen = set()
    for item in files:
        if not isinstance(item, dict):
            raise VerificationError("Entrada files inválida.")
        rel, _ = _safe(bundle, str(item.get("path", "")))
        bundle_rel = "files/" + rel
        if bundle_rel in seen:
            raise VerificationError(f"Arquivo duplicado no manifesto: {bundle_rel}")
        seen.add(bundle_rel)
        expected.add(bundle_rel)
        actual = bundle / "files" / Path(*PurePosixPath(rel).parts)
        if actual.is_symlink() or not actual.is_file():
            raise VerificationError(f"Arquivo ausente/inválido: {bundle_rel}")
        if actual.stat().st_size != int(item.get("length", -1)):
            raise VerificationError(f"Tamanho divergente: {bundle_rel}")
        if sha256_file(actual) != str(item.get("sha256", "")).upper():
            raise VerificationError(f"SHA256 divergente: {bundle_rel}")

    database = manifest.get("database")
    if not isinstance(database, dict):
        raise VerificationError("Entrada database inválida.")
    db_rel, db_path = _safe(bundle, str(database.get("path", "")))
    expected.add(db_rel)
    if db_path.is_symlink() or not db_path.is_file():
        raise VerificationError("Banco do bundle ausente/inválido.")
    if db_path.stat().st_size != int(database.get("length", -1)):
        raise VerificationError("Tamanho do banco divergente.")
    if sha256_file(db_path) != str(database.get("sha256", "")).upper():
        raise VerificationError("SHA256 do banco divergente.")

    conn = sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)
    try:
        integrity = [row[0] for row in conn.execute("PRAGMA integrity_check")]
        fk = list(conn.execute("PRAGMA foreign_key_check"))
    finally:
        conn.close()
    if integrity != ["ok"]:
        raise VerificationError(f"Banco falhou integrity_check: {integrity}")
    if fk:
        raise VerificationError(f"Banco possui violações de FK: {len(fk)}")

    actual = {
        path.relative_to(bundle).as_posix()
        for path in bundle.rglob("*")
        if path.is_file() and not path.is_symlink()
    }
    extras = sorted(actual - expected)
    missing = sorted(expected - actual)
    if extras:
        raise VerificationError("Arquivos extras no bundle: " + ", ".join(extras))
    if missing:
        raise VerificationError("Arquivos faltando no bundle: " + ", ".join(missing))

    return {
        "ok": True,
        "app_version": manifest.get("app_version"),
        "schema_version": manifest.get("schema_version"),
        "commit_sha": manifest.get("commit_sha"),
        "file_count": len(files),
        "database_sha256": database.get("sha256"),
        "manifest_sha256": manifest.get("manifest_sha256"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifica integridade de bundle de rollback do Axiom Tools."
    )
    parser.add_argument("--bundle", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = verify_bundle(args.bundle)
    except VerificationError as exc:
        print(f"ROLLBACK_VERIFY_ERRO: {exc}", file=sys.stderr)
        return 2

    print("ROLLBACK_VERIFY_OK")
    for key, value in report.items():
        if key != "ok":
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
