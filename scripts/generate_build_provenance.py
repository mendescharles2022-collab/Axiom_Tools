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
DEFAULT_IDENTITY_REL = Path("config/release_identity.toml")

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
TEXT_EXTENSIONS = {
    ".py", ".ps1", ".js", ".ts", ".html", ".css", ".json", ".toml",
    ".yaml", ".yml", ".ini", ".cfg", ".conf", ".txt", ".md", ".bat", ".cmd",
}
ASSIGNMENT_RE = re.compile(
    r'''(?im)["']?(api[_-]?key|client[_-]?secret|secret|token|password|senha)["']?'''
    r'''\s*[:=]\s*["']([^"']{8,})["']'''
)
PRIVATE_KEY_RE = re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")
PLACEHOLDER_RE = re.compile(
    r"(example|dummy|placeholder|changeme|change-me|test|fake|mock|sample|fixture|"
    r"none|null|your_|seu_|not[-_ ]?a[-_ ]?real|env\[|getenv|os\.environ|"
    r"\$\{|%[^%]+%)",
    re.IGNORECASE,
)
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


def validate_identity(value: str, field: str) -> str:
    value = value.strip()
    if not value or not IDENTITY_RE.fullmatch(value):
        raise ProvenanceError(
            f"{field} inválido; use apenas letras, números, ponto, hífen, sublinhado ou +."
        )
    return value


def load_release_identity(identity_file: Path) -> dict[str, object]:
    identity_file = identity_file.resolve()
    if not identity_file.is_file():
        raise ProvenanceError(f"Arquivo canônico de release não encontrado: {identity_file}")

    try:
        data = tomllib.loads(identity_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ProvenanceError(f"Identidade de release inválida: {exc}") from exc

    release = data.get("release", {})
    policy = data.get("policy", {})
    product = str(release.get("product") or "").strip()
    state = str(release.get("state") or "").strip().upper()

    if product != PRODUCT:
        raise ProvenanceError(f"Produto divergente na identidade de release: {product!r}")
    if state != "READY":
        raise ProvenanceError(
            f"Release não está liberada para build final: state={state or 'AUSENTE'}. "
            "Enquanto estiver UNRELEASED, o build final deve permanecer bloqueado."
        )

    release_version = validate_identity(
        str(release.get("release_version") or ""), "release_version"
    )
    schema_version = validate_identity(
        str(release.get("schema_version") or ""), "schema_version"
    )
    python_target = validate_identity(
        str(release.get("python_target") or ""), "python_target"
    )
    platform_target = validate_identity(
        str(release.get("platform_target") or DEFAULT_PLATFORM), "platform_target"
    )

    if policy.get("require_clean_git", True) is not True:
        raise ProvenanceError("Política de release inválida: require_clean_git deve permanecer true.")
    if policy.get("require_schema_version", True) is not True:
        raise ProvenanceError("Política de release inválida: require_schema_version deve permanecer true.")
    if policy.get("require_release_version", True) is not True:
        raise ProvenanceError("Política de release inválida: require_release_version deve permanecer true.")

    return {
        "product": product,
        "state": state,
        "release_version": release_version,
        "schema_version": schema_version,
        "python_target": python_target,
        "platform_target": platform_target,
        "identity_file": str(identity_file),
        "identity_sha256": sha256_file(identity_file),
    }


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


def embedded_secret(path: Path) -> bool:
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return False
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return False

    if PRIVATE_KEY_RE.search(content):
        return True

    for match in ASSIGNMENT_RE.finditer(content):
        value = match.group(2).strip()
        if PLACEHOLDER_RE.search(value):
            continue
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
        if embedded_secret(path):
            violations.append(f"{rel} [possible-secret]")
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
    release_identity_sha256: str | None = None,
    release_identity_source: str | None = None,
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
        "release_identity_source": release_identity_source,
        "release_identity_sha256": release_identity_sha256,
        "payload_file_count": len(files),
        "payload_manifest_sha256": files_hash,
        "files": files,
    }
    if build_id is not None:
        provenance["build_id"] = build_id

    # Hash do conteúdo do manifesto sem o próprio hash, evitando autorreferência.
    provenance["hash_manifesto"] = canonical_hash(provenance)
    return provenance


def build_provenance_from_identity(
    *,
    repo_root: Path,
    payload_root: Path,
    output_path: Path,
    identity_file: Path | None = None,
    build_id: str | None = None,
) -> dict[str, object]:
    repo_root = repo_root.resolve()
    identity_file = (identity_file or (repo_root / DEFAULT_IDENTITY_REL)).resolve()
    identity = load_release_identity(identity_file)

    try:
        identity_source = identity_file.relative_to(repo_root).as_posix()
    except ValueError:
        identity_source = str(identity_file)

    return build_provenance(
        repo_root=repo_root,
        payload_root=payload_root,
        output_path=output_path,
        release_version=str(identity["release_version"]),
        schema_version=str(identity["schema_version"]),
        python_target=str(identity["python_target"]),
        platform_target=str(identity["platform_target"]),
        allow_dirty=False,
        build_id=build_id,
        release_identity_sha256=str(identity["identity_sha256"]),
        release_identity_source=identity_source,
    )


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
    parser.add_argument("--identity-file", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--build-id", default=None)
    args = parser.parse_args()

    output = args.output or (args.payload_root / BUILD_PROVENANCE_NAME)
    try:
        provenance = build_provenance_from_identity(
            repo_root=args.repo_root,
            payload_root=args.payload_root,
            output_path=output,
            identity_file=args.identity_file,
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
