from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath

import generate_build_provenance as provenance

REQUIRED_FIELDS = {
    "produto",
    "versao_release",
    "commit_sha",
    "schema_version",
    "python_target",
    "plataforma_target",
    "working_tree_clean",
    "dirty_entries",
    "release_identity_source",
    "release_identity_sha256",
    "payload_file_count",
    "payload_manifest_sha256",
    "files",
    "hash_manifesto",
}
SHA256_RE = re.compile(r"^[0-9A-Fa-f]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9A-Fa-f]{40}$")


class VerificationError(RuntimeError):
    pass


def no_duplicate_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise VerificationError(f"Chave JSON duplicada no manifesto: {key}")
        result[key] = value
    return result


def load_manifest(path: Path) -> dict[str, object]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise VerificationError(f"Não foi possível ler o manifesto: {exc}") from exc

    try:
        value = json.loads(raw, object_pairs_hook=no_duplicate_object)
    except VerificationError:
        raise
    except json.JSONDecodeError as exc:
        raise VerificationError(f"JSON de proveniência inválido: {exc}") from exc

    if not isinstance(value, dict):
        raise VerificationError("Manifesto de proveniência deve ser um objeto JSON.")

    missing = sorted(REQUIRED_FIELDS - set(value))
    if missing:
        raise VerificationError("Campos obrigatórios ausentes: " + ", ".join(missing))
    return value


def safe_relative_path(raw: object) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise VerificationError("Caminho vazio/inválido no manifesto de arquivos.")
    normalized = raw.replace("\\", "/").strip()
    pure = PurePosixPath(normalized)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts:
        raise VerificationError(f"Caminho inseguro no manifesto de arquivos: {raw!r}")
    if pure.parts[0].endswith(":") or "\x00" in normalized:
        raise VerificationError(f"Caminho inseguro no manifesto de arquivos: {raw!r}")
    if pure.name == provenance.BUILD_PROVENANCE_NAME:
        raise VerificationError("BUILD_PROVENANCE.json não pode fazer hash de si próprio.")
    return pure.as_posix()


def normalize_files(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        raise VerificationError("Campo files deve ser uma lista.")

    normalized: list[dict[str, object]] = []
    seen: set[str] = set()

    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise VerificationError(f"Entrada files[{index}] não é objeto.")

        path = safe_relative_path(item.get("path"))
        if path in seen:
            raise VerificationError(f"Caminho duplicado no manifesto do payload: {path}")
        seen.add(path)

        length = item.get("length")
        if not isinstance(length, int) or isinstance(length, bool) or length < 0:
            raise VerificationError(f"Length inválido para {path}")

        sha = item.get("sha256")
        if not isinstance(sha, str) or not SHA256_RE.fullmatch(sha):
            raise VerificationError(f"SHA-256 inválido para {path}")

        normalized.append(
            {
                "path": path,
                "length": length,
                "sha256": sha.upper(),
            }
        )

    if not normalized:
        raise VerificationError("Manifesto do payload está vazio.")

    paths = [item["path"] for item in normalized]
    if paths != sorted(paths):
        raise VerificationError("Manifesto do payload não está em ordem canônica por caminho.")
    return normalized


def verify_manifest_self_hash(manifest: dict[str, object]) -> None:
    expected = manifest.get("hash_manifesto")
    if not isinstance(expected, str) or not SHA256_RE.fullmatch(expected):
        raise VerificationError("hash_manifesto inválido.")

    base = dict(manifest)
    base.pop("hash_manifesto", None)
    actual = provenance.canonical_hash(base)
    if actual != expected.upper():
        raise VerificationError("hash_manifesto divergente; manifesto foi alterado.")


def verify_payload(payload_root: Path, manifest_path: Path, manifest: dict[str, object]) -> None:
    declared = normalize_files(manifest.get("files"))

    count = manifest.get("payload_file_count")
    if not isinstance(count, int) or isinstance(count, bool) or count != len(declared):
        raise VerificationError("payload_file_count divergente da lista files.")

    declared_hash = manifest.get("payload_manifest_sha256")
    if not isinstance(declared_hash, str) or not SHA256_RE.fullmatch(declared_hash):
        raise VerificationError("payload_manifest_sha256 inválido.")
    actual_declared_hash = provenance.canonical_hash(declared)
    if actual_declared_hash != declared_hash.upper():
        raise VerificationError("payload_manifest_sha256 divergente da lista files.")

    actual = provenance.payload_manifest(payload_root, manifest_path)
    if actual != declared:
        declared_map = {str(item["path"]): item for item in declared}
        actual_map = {str(item["path"]): item for item in actual}
        missing = sorted(set(declared_map) - set(actual_map))
        extra = sorted(set(actual_map) - set(declared_map))
        changed = sorted(
            path
            for path in set(declared_map) & set(actual_map)
            if declared_map[path] != actual_map[path]
        )
        details: list[str] = []
        if missing:
            details.append("ausentes=" + ",".join(missing))
        if extra:
            details.append("extras=" + ",".join(extra))
        if changed:
            details.append("alterados=" + ",".join(changed))
        raise VerificationError(
            "Payload diverge do manifesto" + (": " + "; ".join(details) if details else ".")
        )


def verify_release_identity(repo_root: Path, manifest: dict[str, object]) -> None:
    source = manifest.get("release_identity_source")
    expected_hash = manifest.get("release_identity_sha256")
    if not isinstance(source, str) or not source.strip():
        raise VerificationError("release_identity_source ausente/inválido.")
    if not isinstance(expected_hash, str) or not SHA256_RE.fullmatch(expected_hash):
        raise VerificationError("release_identity_sha256 ausente/inválido.")

    source_path = (repo_root / source).resolve()
    try:
        source_path.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise VerificationError("release_identity_source aponta para fora do repositório.") from exc

    if not source_path.is_file():
        raise VerificationError(f"Identidade de release não encontrada: {source}")
    if provenance.sha256_file(source_path) != expected_hash.upper():
        raise VerificationError("Arquivo canônico de release não corresponde ao hash do build.")

    identity = provenance.load_release_identity(source_path)
    pairs = (
        ("versao_release", "release_version"),
        ("schema_version", "schema_version"),
        ("python_target", "python_target"),
        ("plataforma_target", "platform_target"),
    )
    for manifest_key, identity_key in pairs:
        if str(manifest.get(manifest_key)) != str(identity.get(identity_key)):
            raise VerificationError(
                f"{manifest_key} diverge da identidade canônica de release."
            )


def verify_source_repo(repo_root: Path, manifest: dict[str, object]) -> None:
    commit = manifest.get("commit_sha")
    if not isinstance(commit, str) or not GIT_SHA_RE.fullmatch(commit):
        raise VerificationError("commit_sha inválido no manifesto.")

    if manifest.get("working_tree_clean") is not True:
        raise VerificationError("Build final registra working_tree_clean diferente de true.")
    dirty_entries = manifest.get("dirty_entries")
    if dirty_entries not in ([], None):
        raise VerificationError("Build final contém dirty_entries.")

    git = provenance.git_identity(repo_root.resolve(), allow_dirty=False)
    if str(git["commit_sha"]).lower() != commit.lower():
        raise VerificationError(
            "Commit do repositório atual diverge do commit registrado no build."
        )

    verify_release_identity(repo_root.resolve(), manifest)


def verify_build(
    *,
    payload_root: Path,
    manifest_path: Path | None = None,
    repo_root: Path | None = None,
) -> dict[str, object]:
    payload_root = payload_root.resolve()
    if not payload_root.is_dir():
        raise VerificationError(f"payload-root inválido: {payload_root}")

    manifest_path = (manifest_path or (payload_root / provenance.BUILD_PROVENANCE_NAME)).resolve()
    try:
        manifest_path.relative_to(payload_root)
    except ValueError as exc:
        raise VerificationError("Manifesto deve estar dentro do payload verificado.") from exc
    if not manifest_path.is_file():
        raise VerificationError(f"Manifesto não encontrado: {manifest_path}")

    manifest = load_manifest(manifest_path)
    if manifest.get("produto") != provenance.PRODUCT:
        raise VerificationError("Produto inválido no manifesto de build.")

    verify_manifest_self_hash(manifest)
    verify_payload(payload_root, manifest_path, manifest)

    if repo_root is not None:
        verify_source_repo(repo_root.resolve(), manifest)

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verifica integridade e proveniência de um build do Axiom Tools."
    )
    parser.add_argument("--payload-root", required=True, type=Path)
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Quando informado, também confirma commit Git e identidade canônica da fonte.",
    )
    args = parser.parse_args()

    try:
        manifest = verify_build(
            payload_root=args.payload_root,
            manifest_path=args.manifest,
            repo_root=args.repo_root,
        )
    except (VerificationError, provenance.ProvenanceError) as exc:
        print(f"BUILD_VERIFY_ERRO: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"BUILD_VERIFY_ERRO_INESPERADO: {exc}", file=sys.stderr)
        return 3

    print("BUILD_VERIFY_OK")
    print(f"Produto: {manifest['produto']}")
    print(f"Versão: {manifest['versao_release']}")
    print(f"Commit: {str(manifest['commit_sha'])[:12]}")
    print(f"Schema: {manifest['schema_version']}")
    print(f"Arquivos: {manifest['payload_file_count']}")
    print(f"Hash: {manifest['hash_manifesto']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
