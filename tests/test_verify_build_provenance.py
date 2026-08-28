from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generate_build_provenance as generator  # noqa: E402
import verify_build_provenance as verifier  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        capture_output=True,
        check=True,
    )
    return completed.stdout.strip()


def init_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.email", "tests@example.invalid")
    git(repo, "config", "user.name", "Axiom Tests")
    write(
        repo / "pyproject.toml",
        "[project]\nname='axiom-tools-fixture'\nversion='0.1.0'\n",
    )
    write(repo / "src" / "pkg" / "source.py", "VALUE = 1\n")
    write(
        repo / "config" / "release_identity.toml",
        "[release]\n"
        "product='Axiom Tools'\n"
        "state='READY'\n"
        "release_version='V5.6.14V8'\n"
        "schema_version='8'\n"
        "python_target='3.12'\n"
        "platform_target='windows-x64'\n\n"
        "[policy]\n"
        "require_clean_git=true\n"
        "require_schema_version=true\n"
        "require_release_version=true\n",
    )
    git(repo, "add", ".")
    git(repo, "commit", "-m", "fixture")


def build_fixture(base: Path) -> tuple[Path, Path, Path]:
    repo = base / "repo"
    payload = base / "payload"
    manifest_path = payload / generator.BUILD_PROVENANCE_NAME
    init_repo(repo)
    write(payload / "app" / "main.py", "VALUE = 10\n")
    manifest = generator.build_provenance_from_identity(
        repo_root=repo,
        payload_root=payload,
        output_path=manifest_path,
    )
    generator.write_provenance(manifest_path, manifest)
    return repo, payload, manifest_path


def rewrite_manifest(path: Path, mutator) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutator(data)
    data.pop("hash_manifesto", None)
    data["hash_manifesto"] = generator.canonical_hash(data)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


class VerifyBuildProvenanceTests(unittest.TestCase):
    def test_valid_build_passes_payload_and_source_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, payload, manifest = build_fixture(Path(tmp))
            result = verifier.verify_build(
                payload_root=payload,
                manifest_path=manifest,
                repo_root=repo,
            )
            self.assertEqual(result["versao_release"], "V5.6.14V8")
            self.assertEqual(result["schema_version"], "8")

    def test_payload_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, payload, manifest = build_fixture(Path(tmp))
            write(payload / "app" / "main.py", "TAMPERED = True\n")
            with self.assertRaises((verifier.VerificationError, generator.ProvenanceError)):
                verifier.verify_build(payload_root=payload, manifest_path=manifest, repo_root=repo)

    def test_extra_payload_file_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, payload, manifest = build_fixture(Path(tmp))
            write(payload / "app" / "extra.py", "VALUE = 2\n")
            with self.assertRaises((verifier.VerificationError, generator.ProvenanceError)):
                verifier.verify_build(payload_root=payload, manifest_path=manifest, repo_root=repo)

    def test_manifest_self_hash_detects_direct_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, payload, manifest = build_fixture(Path(tmp))
            data = json.loads(manifest.read_text(encoding="utf-8"))
            data["schema_version"] = "999"
            manifest.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(verifier.VerificationError):
                verifier.verify_build(payload_root=payload, manifest_path=manifest, repo_root=repo)

    def test_duplicate_payload_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, payload, manifest = build_fixture(Path(tmp))
            data = json.loads(manifest.read_text(encoding="utf-8"))
            duplicated = list(data["files"]) + [dict(data["files"][0])]
            with self.assertRaises(verifier.VerificationError):
                verifier.normalize_files(duplicated)

    def test_source_commit_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, payload, manifest = build_fixture(Path(tmp))
            write(repo / "new_source.py", "VALUE = 2\n")
            git(repo, "add", "new_source.py")
            git(repo, "commit", "-m", "different commit")
            with self.assertRaises(verifier.VerificationError):
                verifier.verify_build(payload_root=payload, manifest_path=manifest, repo_root=repo)

    def test_release_identity_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, _, manifest = build_fixture(Path(tmp))
            identity = repo / "config" / "release_identity.toml"
            write(
                identity,
                identity.read_text(encoding="utf-8").replace(
                    "schema_version='8'", "schema_version='9'"
                ),
            )
            data = json.loads(manifest.read_text(encoding="utf-8"))
            with self.assertRaises(verifier.VerificationError):
                verifier.verify_release_identity(repo, data)

    def test_manifest_must_live_inside_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo, payload, manifest = build_fixture(Path(tmp))
            outside = Path(tmp) / "outside.json"
            outside.write_bytes(manifest.read_bytes())
            with self.assertRaises(verifier.VerificationError):
                verifier.verify_build(payload_root=payload, manifest_path=outside, repo_root=repo)

    def test_duplicate_json_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text('{"produto":"Axiom Tools","produto":"Outro"}', encoding="utf-8")
            with self.assertRaises(verifier.VerificationError):
                verifier.load_manifest(path)


if __name__ == "__main__":
    unittest.main()
