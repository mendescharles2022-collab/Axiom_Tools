from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import generate_build_provenance as provenance

SHA40_RE = re.compile(r"^[0-9a-fA-F]{40}$")


class IdentityChainError(RuntimeError):
    pass


def load_json(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IdentityChainError(f"JSON inválido {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise IdentityChainError(f"JSON deve ser objeto: {path}")
    return payload


def require_text(document: dict, key: str, label: str) -> str:
    value = str(document.get(key) or "").strip()
    if not value:
        raise IdentityChainError(f"{label}: campo ausente/vazio {key}.")
    return value


def runtime_identity(document: dict, label: str) -> dict[str, str]:
    product = require_text(document, "product", label)
    version = require_text(document, "release_version", label)
    schema = require_text(document, "schema_version", label)
    commit = require_text(document, "commit_sha", label)
    python_target = require_text(document, "python_target", label)
    platform_target = require_text(document, "platform_target", label)

    if product != provenance.PRODUCT:
        raise IdentityChainError(f"{label}: produto divergente: {product!r}")
    if not SHA40_RE.fullmatch(commit):
        raise IdentityChainError(f"{label}: commit_sha inválido: {commit!r}")

    return {
        "product": product,
        "release_version": version,
        "schema_version": schema,
        "commit_sha": commit.lower(),
        "python_target": python_target,
        "platform_target": platform_target,
    }


def build_identity(document: dict) -> dict[str, str]:
    product = require_text(document, "produto", "build")
    version = require_text(document, "versao_release", "build")
    schema = require_text(document, "schema_version", "build")
    commit = require_text(document, "commit_sha", "build")
    python_target = require_text(document, "python_target", "build")
    platform_target = require_text(document, "plataforma_target", "build")
    identity_sha = require_text(document, "release_identity_sha256", "build").upper()

    if product != provenance.PRODUCT:
        raise IdentityChainError(f"build: produto divergente: {product!r}")
    if not SHA40_RE.fullmatch(commit):
        raise IdentityChainError(f"build: commit_sha inválido: {commit!r}")
    if not provenance.SHA_RE.fullmatch(commit):
        raise IdentityChainError(f"build: commit_sha fora do formato Git: {commit!r}")
    if not re.fullmatch(r"[0-9A-F]{64}", identity_sha):
        raise IdentityChainError("build: release_identity_sha256 inválido.")

    return {
        "product": product,
        "release_version": version,
        "schema_version": schema,
        "commit_sha": commit.lower(),
        "python_target": python_target,
        "platform_target": platform_target,
        "release_identity_sha256": identity_sha,
    }


def compare_fields(
    expected: dict[str, str],
    actual: dict[str, str],
    label: str,
    fields: tuple[str, ...],
) -> list[str]:
    mismatches = []
    for field in fields:
        if expected[field] != actual[field]:
            mismatches.append(
                f"{label}.{field}: esperado={expected[field]!r} atual={actual[field]!r}"
            )
    return mismatches


def validate_identity_chain(
    *,
    identity_file: Path,
    build_document: dict,
    runtime_document: dict,
    installer_document: dict,
) -> dict:
    try:
        release = provenance.load_release_identity(identity_file)
    except provenance.ProvenanceError as exc:
        raise IdentityChainError(str(exc)) from exc

    build = build_identity(build_document)
    runtime = runtime_identity(runtime_document, "runtime")
    installer = runtime_identity(installer_document, "installer")

    release_expected = {
        "product": str(release["product"]),
        "release_version": str(release["release_version"]),
        "schema_version": str(release["schema_version"]),
        "python_target": str(release["python_target"]),
        "platform_target": str(release["platform_target"]),
    }
    release_fields = (
        "product",
        "release_version",
        "schema_version",
        "python_target",
        "platform_target",
    )

    mismatches = []
    mismatches.extend(compare_fields(release_expected, build, "build", release_fields))

    actual_identity_sha = provenance.sha256_file(identity_file.resolve()).upper()
    if build["release_identity_sha256"] != actual_identity_sha:
        mismatches.append(
            "build.release_identity_sha256: não corresponde ao arquivo canônico"
        )

    chain_expected = {
        **release_expected,
        "commit_sha": build["commit_sha"],
    }
    chain_fields = release_fields + ("commit_sha",)
    mismatches.extend(compare_fields(chain_expected, runtime, "runtime", chain_fields))
    mismatches.extend(compare_fields(chain_expected, installer, "installer", chain_fields))

    return {
        "version": 1,
        "product": provenance.PRODUCT,
        "release_identity_sha256": actual_identity_sha,
        "expected": chain_expected,
        "sources": {
            "build": build,
            "runtime": runtime,
            "installer": installer,
        },
        "mismatches": mismatches,
        "ok": not mismatches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Valida que release identity, build, runtime/health e instalador "
            "declaram a mesma versão, schema, plataforma e commit."
        )
    )
    parser.add_argument("--identity", required=True, type=Path)
    parser.add_argument("--build", required=True, type=Path)
    parser.add_argument("--runtime", required=True, type=Path)
    parser.add_argument("--installer", required=True, type=Path)
    parser.add_argument(
        "--output", type=Path, default=Path("RELEASE_IDENTITY_CHAIN.json")
    )
    args = parser.parse_args()

    try:
        report = validate_identity_chain(
            identity_file=args.identity,
            build_document=load_json(args.build),
            runtime_document=load_json(args.runtime),
            installer_document=load_json(args.installer),
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except IdentityChainError as exc:
        print(f"RELEASE_IDENTITY_CHAIN_ERRO: {exc}", file=sys.stderr)
        return 2

    print("RELEASE_IDENTITY_CHAIN_OK" if report["ok"] else "RELEASE_IDENTITY_CHAIN_FALHA")
    print(f"Divergências: {len(report['mismatches'])}")
    return 0 if report["ok"] else 4


if __name__ == "__main__":
    raise SystemExit(main())
