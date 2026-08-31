from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SCRIPT = ROOT / "scripts" / "validate_release_identity_chain.py"
spec = importlib.util.spec_from_file_location("validate_release_identity_chain", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)

COMMIT = "a" * 40


def write_identity(
    path: Path,
    *,
    state: str = "READY",
    release_version: str = "V5.6.14V8",
    schema_version: str = "8",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "[release]\n"
        "product = 'Axiom Tools'\n"
        f"state = '{state}'\n"
        f"release_version = '{release_version}'\n"
        f"schema_version = '{schema_version}'\n"
        "python_target = '3.12'\n"
        "platform_target = 'windows-x64'\n\n"
        "[policy]\n"
        "require_clean_git = true\n"
        "require_schema_version = true\n"
        "require_release_version = true\n",
        encoding="utf-8",
    )


def build_doc(identity: Path, **overrides) -> dict:
    doc = {
        "produto": "Axiom Tools",
        "versao_release": "V5.6.14V8",
        "schema_version": "8",
        "commit_sha": COMMIT,
        "python_target": "3.12",
        "plataforma_target": "windows-x64",
        "release_identity_sha256": module.provenance.sha256_file(identity),
    }
    doc.update(overrides)
    return doc


def runtime_doc(**overrides) -> dict:
    doc = {
        "product": "Axiom Tools",
        "release_version": "V5.6.14V8",
        "schema_version": "8",
        "commit_sha": COMMIT,
        "python_target": "3.12",
        "platform_target": "windows-x64",
    }
    doc.update(overrides)
    return doc


class ReleaseIdentityChainTests(unittest.TestCase):
    def test_matching_chain_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = Path(tmp) / "release_identity.toml"
            write_identity(identity)
            report = module.validate_identity_chain(
                identity_file=identity,
                build_document=build_doc(identity),
                runtime_document=runtime_doc(),
                installer_document=runtime_doc(),
            )
            self.assertTrue(report["ok"])
            self.assertEqual(report["mismatches"], [])
            self.assertEqual(report["expected"]["commit_sha"], COMMIT)

    def test_unreleased_identity_blocks_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = Path(tmp) / "release_identity.toml"
            write_identity(identity, state="UNRELEASED", release_version="", schema_version="")
            with self.assertRaises(module.IdentityChainError):
                module.validate_identity_chain(
                    identity_file=identity,
                    build_document={"ignored": True},
                    runtime_document={},
                    installer_document={},
                )

    def test_build_identity_hash_mismatch_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = Path(tmp) / "release_identity.toml"
            write_identity(identity)
            report = module.validate_identity_chain(
                identity_file=identity,
                build_document=build_doc(identity, release_identity_sha256="B" * 64),
                runtime_document=runtime_doc(),
                installer_document=runtime_doc(),
            )
            self.assertFalse(report["ok"])
            self.assertTrue(any("release_identity_sha256" in item for item in report["mismatches"]))

    def test_runtime_commit_divergence_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = Path(tmp) / "release_identity.toml"
            write_identity(identity)
            report = module.validate_identity_chain(
                identity_file=identity,
                build_document=build_doc(identity),
                runtime_document=runtime_doc(commit_sha="b" * 40),
                installer_document=runtime_doc(),
            )
            self.assertFalse(report["ok"])
            self.assertTrue(any("runtime.commit_sha" in item for item in report["mismatches"]))

    def test_installer_schema_divergence_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = Path(tmp) / "release_identity.toml"
            write_identity(identity)
            report = module.validate_identity_chain(
                identity_file=identity,
                build_document=build_doc(identity),
                runtime_document=runtime_doc(),
                installer_document=runtime_doc(schema_version="7"),
            )
            self.assertFalse(report["ok"])
            self.assertTrue(any("installer.schema_version" in item for item in report["mismatches"]))

    def test_release_version_divergence_in_build_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = Path(tmp) / "release_identity.toml"
            write_identity(identity)
            report = module.validate_identity_chain(
                identity_file=identity,
                build_document=build_doc(identity, versao_release="V5.6.14V7"),
                runtime_document=runtime_doc(),
                installer_document=runtime_doc(),
            )
            self.assertFalse(report["ok"])
            self.assertTrue(any("build.release_version" in item for item in report["mismatches"]))

    def test_invalid_runtime_commit_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            identity = Path(tmp) / "release_identity.toml"
            write_identity(identity)
            with self.assertRaises(module.IdentityChainError):
                module.validate_identity_chain(
                    identity_file=identity,
                    build_document=build_doc(identity),
                    runtime_document=runtime_doc(commit_sha="not-a-commit"),
                    installer_document=runtime_doc(),
                )


if __name__ == "__main__":
    unittest.main()
