from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class BuildIdentityError(RuntimeError):
    pass


@dataclass(frozen=True)
class RuntimeBuildIdentity:
    product: str
    release_version: str
    commit_sha: str
    source_ref: str
    schema_version: str
    python_target: str
    platform_target: str
    build_timestamp: str
    manifest_sha256: str
    payload_manifest_sha256: str

    @property
    def short_commit(self) -> str:
        return self.commit_sha[:12]

    def health_payload(self, *, database_status: str, status: str = "ok") -> dict[str, Any]:
        return {
            "status": status,
            "product": self.product,
            "version": self.release_version,
            "build": self.short_commit,
            "schema": self.schema_version,
            "database": database_status,
        }


def _required(payload: dict[str, Any], key: str) -> str:
    value = str(payload.get(key) or "").strip()
    if not value:
        raise BuildIdentityError(f"missing required build field: {key}")
    return value


def load_build_identity(
    manifest_path: str | Path,
    *,
    runtime_schema_version: str | None = None,
) -> RuntimeBuildIdentity:
    path = Path(manifest_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise BuildIdentityError("build provenance is unavailable or invalid") from exc

    identity = RuntimeBuildIdentity(
        product=_required(payload, "produto"),
        release_version=_required(payload, "versao_release"),
        commit_sha=_required(payload, "commit_sha"),
        source_ref=_required(payload, "source_ref"),
        schema_version=_required(payload, "schema_version"),
        python_target=_required(payload, "python_target"),
        platform_target=_required(payload, "platform_target"),
        build_timestamp=_required(payload, "data_hora_build"),
        manifest_sha256=_required(payload, "hash_manifesto"),
        payload_manifest_sha256=_required(payload, "payload_manifest_sha256"),
    )

    if identity.product != "Axiom Tools":
        raise BuildIdentityError("build provenance belongs to another product")
    if len(identity.commit_sha) != 40:
        raise BuildIdentityError("commit_sha must contain the full git SHA")
    if len(identity.manifest_sha256) != 64 or len(identity.payload_manifest_sha256) != 64:
        raise BuildIdentityError("build hashes must be SHA-256 digests")
    if runtime_schema_version is not None and str(runtime_schema_version) != identity.schema_version:
        raise BuildIdentityError("runtime schema differs from build provenance")

    return identity


def startup_record(identity: RuntimeBuildIdentity, *, backend_port: int = 5201) -> dict[str, Any]:
    return {
        "event": "runtime_start",
        "product": identity.product,
        "version": identity.release_version,
        "commit": identity.short_commit,
        "schema": identity.schema_version,
        "backend_port": int(backend_port),
    }


def startup_log_line(identity: RuntimeBuildIdentity, *, backend_port: int = 5201) -> str:
    return json.dumps(
        startup_record(identity, backend_port=backend_port),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


__all__ = [
    "BuildIdentityError",
    "RuntimeBuildIdentity",
    "load_build_identity",
    "startup_log_line",
    "startup_record",
]
