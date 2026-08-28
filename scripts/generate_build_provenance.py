from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

PRODUCT = "Axiom Tools"
DEFAULT_PLATFORM = "windows-x64"
BUILD_PROVENANCE_NAME = "BUILD_PROVENANCE.json"

FORBIDDEN_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache",
    "data", "database", "databases", "db", "documentos", "documents",
    "uploads", "upload", "logs", "log", "backups", "backup", "temp", "tmp",
    "certificados", "certificates", "secrets", "tokens", "cache", "caches",
}
FORBIDDEN_EXTENSIONS = {
    ".sqlite", ".sqlite3", ".db", ".mdb", ".accdb",
    ".pfx", ".p12", ".p7b", ".p7c", ".cer", ".crt", ".der",
    ".pem", ".key", ".jks", ".kdb", ".kdbx",
}
SENSITIVE_FILENAMES = {
    ".env", "credentials.json", "credential.json", "secrets.json", "secret.json",
    "token.json", "tokens.json", "service-account.json", "service_account.json",
}
IDENTITY_RE = re.compile(r"^[A-Za-z0-9._+\-]+$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)


class ProvenanceError(RuntimeError):
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


def run_git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        raise ProvenanceError(f"Falha ao consultar Git ({' '.join(args)}): {detail}")
    return completed.stdout.strip()


def git_identity(repo_root: Path, allow_dirty: bool) -> dict[str, object]:
    commit = run_git(repo_root, "rev-parse", "HEAD")
    if not SHA_RE.fullmatch(commit):
        raise ProvenanceError(f"Commit Git inválido: {commit!r}")

    branch = run_git(repo_root, "rev-parse", "--abbrev-ref", "HEAD") or "DETACHED"
    dirty_lines = [
        line.rstrip()
        for line in run_git(repo_root, "status", "--porcelain=v1", "--untracked-files=all").splitlines()
        if line.strip()
    ]

    if dirty_lines and not allow_dirty:
        raise ProvenanceError(
            "Working tree não está limpa. Commit/stash das alterações é obrigatório antes do build."
        )

    return {
        "commit_sha": commit,
        "commit_short": commit[:12],
        "source_ref": branch,
        "working_tree_clean": not dirty_lines,
        "dirty_entries": dirty_lines if allow_dirty else [],
    }


def pyproject_version(repo_root: Path) -> str | None:
    path = repo_root / "pyproject.toml"
    if not path.is_file():
        return None
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ProvenanceError(f"pyproject.toml inválido: {exc}") from exc
    value = data.get("project", {}).get("version")
    return str(value) if value is not None else None


def forbidden_path(path: Path) -> bool:
    name = path.name.lower()
    if path.is_dir() and name in FORBIDDEN_DIRS:
        return True
    if path.is_file():
        if path.suffix.lower() in FORBIDDEN_EXTENSIONS:
            return True
        if name in SENSITIVE_FILENAMES or name.startswith(".env."):
            return True
    return False


def payload_manifest(payload_root: Path, output_path: Path) -> list[dict[str, object]]:
    payload_root = payload_root.resolve()
    output_path = output_path.resolve()
    entries: list[dict[str, object]] = []
    violations: list[str] = []

    for path in sorted(payload_root.rglob("*")):
        rel = path.relative_to(payload_root).as_posix()
        if path.resolve() == output_path:
            continue
        if path.is_symlink():
            violations.append(f"{rel} [symlink]")
            continue
        if forbidden_path(path):
            violations.append(rel + ("/" if path.is_dir() else ""))
            continue
        if not path.is_file():
            continue

        entries.append(
            {
                "path": rel,
                "length": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )

    if violations:
        raise ProvenanceError(
            "Payload contém conteúdo que não pode integrar build versionado:\n- "
            + "\n- ".join(sorted(set(violations)))
        )

    if not entries:
        raise ProvenanceError("Payload do build está vazio.")

    return entries


def validate_identity(value: str, field: str) -> str:
    value = value.strip()
    if not value or not IDENTITY_RE.fullmatch(value):
        raise ProvenanceError(
            f"{field} inválido; use apenas letras, números, ponto, hífen, sublinhado ou +."
        )
    return value


def build_provenance(
    *,
    repo_root: Path,
    payload_root: Path,
    output_path: Path,
    release_version: str,
    schema_version: str,
    python_target: str | None = None,
    platform_target: str = DEFAULT_PLATFORM,
    allow_dirty: bool = False,
    build_id: str | None = None,
) -> dict[str, object]:
    repo_root = repo_root.resolve()
    payload_root = payload_root.resolve()
    output_path = output_path.resolve()

    if not repo_root.is_dir():
        raise ProvenanceError(f"repo-root inválido: {repo_root}")
    if not payload_root.is_dir():
        raise ProvenanceError(f"payload-root inválido: {payload_root}")

    release_version = validate_identity(release_version, "release_version")
    schema_version = validate_identity(schema_version, "schema_version")
    platform_target = validate_identity(platform_target, "platform_target")
    python_target = validate_identity(
        python_target or f"{sys.version_info.major}.{sys.version_info.minor}",
        "python_target",
    )
    if build_id is not None:
        build_id = validate_identity(build_id, "build_id")

    git = git_identity(repo_root, allow_dirty=allow_dirty)
    files = payload_manifest(payload_root, output_path)
    files_hash = canonical_hash(files)

    provenance: dict[str, object] = {
        "produto": PRODUCT,
        "versao_release": release_version,
        "commit_sha": git["commit_sha"],
        "commit_short": git["commit_short"],
        "source_ref": git["source_ref"],
        "data_hora_build_utc": datetime.now(timezone.utc).isoformat(),
        "schema_version": schema_version,
        "python_target": python_target,
        "plataforma_target": platform_target,
        "working_tree_clean": git["working_tree_clean"],
        "dirty_entries": git["dirty_entries"],
        "source_pyproject_version": pyproject_version(repo_root),
        "payload_file_count": len(files),
        "payload_manifest_sha256": files_hash,
        "files": files,
    }
    if build_id is not None:
        provenance["build_id"] = build_id

    # Hash do conteúdo do manifesto sem o próprio hash, evitando autorreferência.
    provenance["hash_manifesto"] = canonical_hash(provenance)
    return provenance


def write_provenance(output_path: Path, provenance: dict[str, object]) -> None:
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gera manifesto verificável de proveniência para um build do Axiom Tools."
    )
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--payload-root", required=True, type=Path)
    parser.add_argument("--release-version", required=True)
    parser.add_argument("--schema-version", required=True)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--python-target", default=None)
    parser.add_argument("--platform-target", default=DEFAULT_PLATFORM)
    parser.add_argument("--build-id", default=None)
    parser.add_argument("--allow-dirty", action="store_true")
    args = parser.parse_args()

    output = args.output or (args.payload_root / BUILD_PROVENANCE_NAME)
    try:
        provenance = build_provenance(
            repo_root=args.repo_root,
            payload_root=args.payload_root,
            output_path=output,
            release_version=args.release_version,
            schema_version=args.schema_version,
            python_target=args.python_target,
            platform_target=args.platform_target,
            allow_dirty=args.allow_dirty,
            build_id=args.build_id,
        )
        write_provenance(output, provenance)
    except ProvenanceError as exc:
        print(f"BUILD_PROVENANCE_ERRO: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"BUILD_PROVENANCE_ERRO_INESPERADO: {exc}", file=sys.stderr)
        return 3

    print("BUILD_PROVENANCE_OK")
    print(f"Produto: {provenance['produto']}")
    print(f"Versão: {provenance['versao_release']}")
    print(f"Commit: {provenance['commit_short']}")
    print(f"Schema: {provenance['schema_version']}")
    print(f"Arquivos: {provenance['payload_file_count']}")
    print(f"Manifesto: {output.resolve()}")
    print(f"Hash: {provenance['hash_manifesto']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
