from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import build_reconciliation_baseline_acceptance as acceptance_mod  # noqa: E402
import create_reconciliation_review_skeleton as skeleton_mod  # noqa: E402
import materialize_reconciled_staging as materializer  # noqa: E402
import plan_runtime_reconciliation as planner  # noqa: E402
import verify_reconciled_staging as verifier  # noqa: E402

POLICY = json.loads((ROOT / "config/runtime_reconciliation_plan_policy_v8.json").read_text(encoding="utf-8"))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def diff_row(area: str, rel: str, status: str, runtime: Path, repo: Path) -> dict:
    runtime_file, repo_file, _ = materializer.decision_paths(runtime, repo, {"area": area, "relative_path": rel})
    runtime_hash = materializer.sha256_file(runtime_file) if runtime_file.is_file() else ""
    repo_hash = materializer.sha256_file(repo_file) if repo_file.is_file() else ""
    return {
        "area": area,
        "relative_path": rel,
        "status": status,
        "runtime_sha256": runtime_hash,
        "repo_sha256": repo_hash,
        "runtime_size": runtime_file.stat().st_size if runtime_file.is_file() else 0,
        "repo_size": repo_file.stat().st_size if repo_file.is_file() else 0,
    }


def build_fixture(base: Path, *, exclude_repo: bool = False) -> tuple[Path, dict]:
    runtime = base / "runtime"
    repo = base / "repo"
    write(runtime / "src/changed.py", "value = 'runtime'\n")
    write(runtime / "src/runtime.py", "runtime_only = True\n")
    write(repo / "src/changed.py", "value = 'repo'\n")
    write(repo / "src/repo.py", "repo_only = True\n")
    write(repo / "config/public.json", '{"mode":"safe"}\n')
    rows = [
        diff_row("src_root", "changed.py", "CHANGED", runtime, repo),
        diff_row("src_root", "runtime.py", "RUNTIME_ONLY", runtime, repo),
        diff_row("src_root", "repo.py", "REPO_ONLY", runtime, repo),
    ]
    plan = planner.build_plan({"metadata": {}, "summary": {}, "rows": rows}, POLICY)
    review = skeleton_mod.build_skeleton(plan)
    review["mode"] = "RECONCILIATION_REVIEW_NOT_EXECUTION"
    decisions = {
        "changed.py": "KEEP_REPO",
        "runtime.py": "ADOPT_RUNTIME",
        "repo.py": "EXCLUDE_WITH_REASON" if exclude_repo else "KEEP_REPO",
    }
    for item in review["items"]:
        item["decision"] = decisions[item["relative_path"]]
        item["reviewer"] = "Charles"
        item["reason"] = "Revisão manual concluída com evidência suficiente."
        item["evidence"] = ["evidence:manual-review"]
    acceptance = acceptance_mod.build_acceptance(plan, review)
    staging = base / "staging"
    materializer.materialize_staging(runtime, repo, staging, acceptance)
    return staging, acceptance


def load_report(staging: Path) -> dict:
    return json.loads((staging / materializer.REPORT_NAME).read_text(encoding="utf-8"))


def save_report(staging: Path, report: dict) -> None:
    payload = dict(report)
    payload.pop("report_sha256", None)
    report["report_sha256"] = verifier.canonical_hash(payload)
    (staging / materializer.REPORT_NAME).write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def rebuild_file_inventory(staging: Path, report: dict) -> None:
    files = []
    for path in sorted(staging.rglob("*")):
        if path.is_file() and not path.is_symlink() and path.name != materializer.REPORT_NAME:
            files.append({
                "relative_path": path.relative_to(staging).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": verifier.sha256_file(path),
            })
    report["staging_files"] = files
    report["file_count"] = len(files)
    report["tree_sha256"] = verifier.canonical_hash(files)
    save_report(staging, report)


def snapshot(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): verifier.sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


class VerifyReconciledStagingTests(unittest.TestCase):
    def test_valid_staging_verifies_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_fixture(Path(tmp))
            before = snapshot(staging)
            result = verifier.verify_staging(staging, acceptance)
            self.assertTrue(result["verification_ok"])
            self.assertTrue(result["staging_unchanged"])
            self.assertEqual(result["decisions_verified"], 3)
            self.assertFalse(result["operational_deployment_performed"])
            self.assertFalse(result["source_write_performed"])
            self.assertFalse(result["v8_homologated"])
            self.assertEqual(snapshot(staging), before)

    def test_file_tamper_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_fixture(Path(tmp))
            write(staging / "src/changed.py", "tampered = True\n")
            with self.assertRaisesRegex(verifier.StagingVerificationError, "SHA-256 divergente"):
                verifier.verify_staging(staging, acceptance)

    def test_extra_file_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_fixture(Path(tmp))
            write(staging / "src/extra.py", "extra = True\n")
            with self.assertRaisesRegex(verifier.StagingVerificationError, "Conteúdo do staging diverge"):
                verifier.verify_staging(staging, acceptance)

    def test_missing_file_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_fixture(Path(tmp))
            (staging / "src/changed.py").unlink()
            with self.assertRaisesRegex(verifier.StagingVerificationError, "ausente/inválido"):
                verifier.verify_staging(staging, acceptance)

    def test_report_tamper_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_fixture(Path(tmp))
            report = load_report(staging)
            report["file_count"] += 1
            (staging / materializer.REPORT_NAME).write_text(json.dumps(report), encoding="utf-8")
            with self.assertRaisesRegex(verifier.StagingVerificationError, "report_sha256"):
                verifier.verify_staging(staging, acceptance)

    def test_different_valid_acceptance_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            staging, acceptance = build_fixture(base / "one")
            _, other_acceptance = build_fixture(base / "two", exclude_repo=True)
            self.assertNotEqual(acceptance["acceptance_sha256"], other_acceptance["acceptance_sha256"])
            with self.assertRaisesRegex(verifier.StagingVerificationError, "vinculado ao aceite"):
                verifier.verify_staging(staging, other_acceptance)

    def test_reforged_report_cannot_hide_wrong_decision_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_fixture(Path(tmp))
            report = load_report(staging)
            report["applied_decisions"][0]["target_relative_path"] = "src/other.py"
            save_report(staging, report)
            with self.assertRaisesRegex(verifier.StagingVerificationError, "applied_decisions diverge"):
                verifier.verify_staging(staging, acceptance)

    def test_excluded_file_recreated_is_rejected_even_with_reforged_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_fixture(Path(tmp), exclude_repo=True)
            write(staging / "src/repo.py", "recreated = True\n")
            report = load_report(staging)
            rebuild_file_inventory(staging, report)
            with self.assertRaisesRegex(verifier.StagingVerificationError, "Arquivo excluído reapareceu"):
                verifier.verify_staging(staging, acceptance)

    def test_secret_inserted_is_rejected_even_with_reforged_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_fixture(Path(tmp))
            write(staging / "config/public.json", '{"password":"real-secret-123456"}\n')
            report = load_report(staging)
            rebuild_file_inventory(staging, report)
            with self.assertRaisesRegex(verifier.StagingVerificationError, "possível segredo"):
                verifier.verify_staging(staging, acceptance)

    def test_symlink_inserted_is_rejected_when_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_fixture(Path(tmp))
            link = staging / "src/link.py"
            try:
                os.symlink(staging / "src/changed.py", link)
            except (OSError, NotImplementedError):
                self.skipTest("symlink indisponível")
            with self.assertRaisesRegex(verifier.StagingVerificationError, "Symlink proibido"):
                verifier.verify_staging(staging, acceptance)

    def test_tree_hash_tamper_is_rejected_even_with_valid_report_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_fixture(Path(tmp))
            report = load_report(staging)
            report["tree_sha256"] = "F" * 64
            save_report(staging, report)
            with self.assertRaisesRegex(verifier.StagingVerificationError, "tree_sha256"):
                verifier.verify_staging(staging, acceptance)

    def test_applied_decision_duplicate_is_rejected_even_with_valid_report_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            staging, acceptance = build_fixture(Path(tmp))
            report = load_report(staging)
            report["applied_decisions"].append(deepcopy(report["applied_decisions"][0]))
            save_report(staging, report)
            with self.assertRaisesRegex(verifier.StagingVerificationError, "duplicada"):
                verifier.verify_staging(staging, acceptance)

    def test_cli_refuses_existing_output_without_touching_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            staging, acceptance = build_fixture(base)
            acceptance_path = base / "acceptance.json"
            output = base / "verification.json"
            acceptance_path.write_text(json.dumps(acceptance), encoding="utf-8")
            output.write_text("preservar", encoding="utf-8")
            old_argv = sys.argv
            try:
                sys.argv = [
                    "verify_reconciled_staging.py",
                    "--staging-dir", str(staging),
                    "--acceptance", str(acceptance_path),
                    "--output", str(output),
                ]
                self.assertEqual(verifier.main(), 2)
            finally:
                sys.argv = old_argv
            self.assertEqual(output.read_text(encoding="utf-8"), "preservar")


if __name__ == "__main__":
    unittest.main()
