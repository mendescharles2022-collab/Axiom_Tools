from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from axiom_tools.core.build_identity import (
    BuildIdentityError,
    load_build_identity,
    startup_log_line,
)


def valid_manifest() -> dict:
    return {
        "produto": "Axiom Tools",
        "versao_release": "V8",
        "commit_sha": "a" * 40,
        "source_ref": "audit-v8-runtime-reconciliation",
        "schema_version": "8",
        "python_target": "3.12",
        "platform_target": "windows-x64",
        "data_hora_build": "2026-08-28T20:00:00-03:00",
        "hash_manifesto": "b" * 64,
        "payload_manifest_sha256": "c" * 64,
    }


def write_manifest(base: Path, payload: dict) -> Path:
    path = base / "build_provenance.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class BuildIdentityV8Tests(unittest.TestCase):
    def test_manifest_drives_runtime_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = load_build_identity(write_manifest(Path(tmp), valid_manifest()))
            self.assertEqual(identity.product, "Axiom Tools")
            self.assertEqual(identity.release_version, "V8")
            self.assertEqual(identity.short_commit, "a" * 12)
            self.assertEqual(identity.schema_version, "8")

    def test_schema_mismatch_blocks_runtime_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(BuildIdentityError):
                load_build_identity(
                    write_manifest(Path(tmp), valid_manifest()),
                    runtime_schema_version="7",
                )

    def test_missing_required_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = valid_manifest()
            del payload["commit_sha"]
            with self.assertRaises(BuildIdentityError):
                load_build_identity(write_manifest(Path(tmp), payload))

    def test_other_product_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = valid_manifest()
            payload["produto"] = "Outro Sistema"
            with self.assertRaises(BuildIdentityError):
                load_build_identity(write_manifest(Path(tmp), payload))

    def test_invalid_hash_lengths_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = valid_manifest()
            payload["hash_manifesto"] = "123"
            with self.assertRaises(BuildIdentityError):
                load_build_identity(write_manifest(Path(tmp), payload))

    def test_health_payload_exposes_only_operational_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = load_build_identity(write_manifest(Path(tmp), valid_manifest()))
            health = identity.health_payload(database_status="ok")
            self.assertEqual(
                set(health),
                {"status", "product", "version", "build", "schema", "database"},
            )
            self.assertNotIn("source_ref", health)
            self.assertNotIn("manifest_sha256", health)
            self.assertNotIn("payload_manifest_sha256", health)

    def test_startup_log_is_structured_and_consistent(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = load_build_identity(write_manifest(Path(tmp), valid_manifest()))
            record = json.loads(startup_log_line(identity, backend_port=5201))
            self.assertEqual(record["product"], "Axiom Tools")
            self.assertEqual(record["version"], "V8")
            self.assertEqual(record["commit"], "a" * 12)
            self.assertEqual(record["schema"], "8")
            self.assertEqual(record["backend_port"], 5201)


if __name__ == "__main__":
    unittest.main()
