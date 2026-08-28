from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import generate_build_provenance as provenance  # noqa: E402


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
    git(repo, "add", ".")
    git(repo, "commit", "-m", "fixture")


def write_identity(
    path: Path,
    *,
    state: str = "READY",
    release_version: str = "V5.6.14V8",
    schema_version: str = "8",
    require_clean_git: bool = True,
) -> None:
    clean = "true" if require_clean_git else "false"
    write(
        path,
        "[release]\n"
        "product = 'Axiom Tools'\n"
        f"state = '{state}'\n"
        f"release_version = '{release_version}'\n"
        f"schema_version = '{schema_version}'\n"
        "python_target = '3.12'\n"
        "platform_target = 'windows-x64'\n\n"
        "[policy]\n"
        f"require_clean_git = {clean}\n"
        "require_schema_version = true\n"
        "require_release_version = true\n",
    )


class BuildProvenanceTests(unittest.TestCase):
    def test_clean_repo_generates_traceable_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            payload = base / "payload"
            output = payload / provenance.BUILD_PROVENANCE_NAME
            init_repo(repo)
            write(payload / "app" / "main.py", "VALUE = 10\n")

            result = provenance.build_provenance(
                repo_root=repo,
                payload_root=payload,
                output_path=output,
                release_version="V5.6.14V8",
                schema_version="8",
            )

            self.assertEqual(result["produto"], "Axiom Tools")
            self.assertEqual(result["versao_release"], "V5.6.14V8")
            self.assertEqual(result["schema_version"], "8")
            self.assertEqual(result["source_ref"], "main")
            self.assertTrue(result["working_tree_clean"])
            self.assertEqual(result["source_pyproject_version"], "0.1.0")
            self.assertEqual(result["payload_file_count"], 1)
            self.assertEqual(len(result["commit_sha"]), 40)
            self.assertEqual(len(result["payload_manifest_sha256"]), 64)
            self.assertEqual(len(result["hash_manifesto"]), 64)
            self.assertEqual(result["files"][0]["path"], "app/main.py")

    def test_dirty_repo_is_blocked_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            payload = base / "payload"
            init_repo(repo)
            write(payload / "app.py", "VALUE = 1\n")
            write(repo / "src" / "pkg" / "source.py", "VALUE = 999\n")

            with self.assertRaises(provenance.ProvenanceError):
                provenance.build_provenance(
                    repo_root=repo,
                    payload_root=payload,
                    output_path=payload / provenance.BUILD_PROVENANCE_NAME,
                    release_version="V8",
                    schema_version="8",
                )

    def test_allow_dirty_records_dirty_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            payload = base / "payload"
            init_repo(repo)
            write(payload / "app.py", "VALUE = 1\n")
            write(repo / "src" / "pkg" / "source.py", "VALUE = 2\n")

            result = provenance.build_provenance(
                repo_root=repo,
                payload_root=payload,
                output_path=payload / provenance.BUILD_PROVENANCE_NAME,
                release_version="V8",
                schema_version="8",
                allow_dirty=True,
            )

            self.assertFalse(result["working_tree_clean"])
            self.assertTrue(result["dirty_entries"])

    def test_sensitive_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            payload = base / "payload"
            init_repo(repo)
            write(payload / "app.py", "VALUE = 1\n")
            write(payload / "database" / "prod.sqlite3", "fake-db")

            with self.assertRaises(provenance.ProvenanceError):
                provenance.build_provenance(
                    repo_root=repo,
                    payload_root=payload,
                    output_path=payload / provenance.BUILD_PROVENANCE_NAME,
                    release_version="V8",
                    schema_version="8",
                )

    def test_hardcoded_secret_in_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            payload = base / "payload"
            init_repo(repo)
            write(payload / "app.py", 'api_key = "REAL_SECRET_123456"\n')

            with self.assertRaises(provenance.ProvenanceError):
                provenance.build_provenance(
                    repo_root=repo,
                    payload_root=payload,
                    output_path=payload / provenance.BUILD_PROVENANCE_NAME,
                    release_version="V8",
                    schema_version="8",
                )

    def test_payload_change_changes_manifest_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            payload = base / "payload"
            init_repo(repo)
            target = payload / "app.py"
            write(target, "VALUE = 1\n")

            first = provenance.build_provenance(
                repo_root=repo,
                payload_root=payload,
                output_path=payload / provenance.BUILD_PROVENANCE_NAME,
                release_version="V8",
                schema_version="8",
            )
            write(target, "VALUE = 2\n")
            second = provenance.build_provenance(
                repo_root=repo,
                payload_root=payload,
                output_path=payload / provenance.BUILD_PROVENANCE_NAME,
                release_version="V8",
                schema_version="8",
            )

            self.assertNotEqual(
                first["payload_manifest_sha256"],
                second["payload_manifest_sha256"],
            )
            self.assertNotEqual(first["hash_manifesto"], second["hash_manifesto"])

    def test_existing_output_file_is_not_hashed_into_itself(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            payload = base / "payload"
            output = payload / provenance.BUILD_PROVENANCE_NAME
            init_repo(repo)
            write(payload / "app.py", "VALUE = 1\n")
            write(output, "old manifest\n")

            result = provenance.build_provenance(
                repo_root=repo,
                payload_root=payload,
                output_path=output,
                release_version="V8",
                schema_version="8",
            )

            paths = {item["path"] for item in result["files"]}
            self.assertNotIn(provenance.BUILD_PROVENANCE_NAME, paths)
            self.assertEqual(paths, {"app.py"})

    def test_empty_payload_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            payload = base / "payload"
            init_repo(repo)
            payload.mkdir()

            with self.assertRaises(provenance.ProvenanceError):
                provenance.build_provenance(
                    repo_root=repo,
                    payload_root=payload,
                    output_path=payload / provenance.BUILD_PROVENANCE_NAME,
                    release_version="V8",
                    schema_version="8",
                )

    def test_invalid_release_identity_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            payload = base / "payload"
            init_repo(repo)
            write(payload / "app.py", "VALUE = 1\n")

            with self.assertRaises(provenance.ProvenanceError):
                provenance.build_provenance(
                    repo_root=repo,
                    payload_root=payload,
                    output_path=payload / provenance.BUILD_PROVENANCE_NAME,
                    release_version="V8 FINAL COM ESPAÇO",
                    schema_version="8",
                )

    def test_unreleased_identity_blocks_final_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            identity = base / "release_identity.toml"
            write_identity(
                identity,
                state="UNRELEASED",
                release_version="",
                schema_version="",
            )

            with self.assertRaises(provenance.ProvenanceError):
                provenance.load_release_identity(identity)

    def test_ready_identity_drives_official_build_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / "repo"
            payload = base / "payload"
            output = payload / provenance.BUILD_PROVENANCE_NAME
            init_repo(repo)
            write_identity(repo / "config" / "release_identity.toml")
            git(repo, "add", "config/release_identity.toml")
            git(repo, "commit", "-m", "release identity")
            write(payload / "app.py", "VALUE = 1\n")

            result = provenance.build_provenance_from_identity(
                repo_root=repo,
                payload_root=payload,
                output_path=output,
            )

            self.assertEqual(result["versao_release"], "V5.6.14V8")
            self.assertEqual(result["schema_version"], "8")
            self.assertEqual(result["python_target"], "3.12")
            self.assertEqual(result["plataforma_target"], "windows-x64")
            self.assertEqual(result["release_identity_source"], "config/release_identity.toml")
            self.assertEqual(len(result["release_identity_sha256"]), 64)
            self.assertTrue(result["working_tree_clean"])

    def test_release_policy_cannot_disable_clean_git(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            identity = base / "release_identity.toml"
            write_identity(identity, require_clean_git=False)

            with self.assertRaises(provenance.ProvenanceError):
                provenance.load_release_identity(identity)


if __name__ == "__main__":
    unittest.main()
