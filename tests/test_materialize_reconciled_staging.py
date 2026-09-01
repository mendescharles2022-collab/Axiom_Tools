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
import materialize_reconciled_staging as staging_mod  # noqa: E402
import plan_runtime_reconciliation as planner  # noqa: E402

POLICY = json.loads((ROOT / "config/runtime_reconciliation_plan_policy_v8.json").read_text(encoding="utf-8"))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def diff_row(area: str, rel: str, status: str, runtime: Path, repo: Path) -> dict:
    runtime_file, repo_file, _ = staging_mod.decision_paths(runtime, repo, {"area": area, "relative_path": rel})
    runtime_hash = staging_mod.sha256_file(runtime_file) if runtime_file.is_file() else ""
    repo_hash = staging_mod.sha256_file(repo_file) if repo_file.is_file() else ""
    return {
        "area": area,
        "relative_path": rel,
        "status": status,
        "runtime_sha256": runtime_hash,
        "repo_sha256": repo_hash,
        "runtime_size": runtime_file.stat().st_size if runtime_file.is_file() else 0,
        "repo_size": repo_file.stat().st_size if repo_file.is_file() else 0,
    }


def make_sources(base: Path) -> tuple[Path, Path]:
    runtime = base / "runtime"
    repo = base / "repo"
    write(runtime / "src/changed.py", "value = 'runtime'\n")
    write(runtime / "src/runtime.py", "runtime_only = True\n")
    write(repo / "src/changed.py", "value = 'repo'\n")
    write(repo / "src/repo.py", "repo_only = True\n")
    write(repo / "config/public.json", '{"mode":"safe"}\n')
    return runtime, repo


def make_acceptance(runtime: Path, repo: Path, decisions: dict[str, str] | None = None) -> dict:
    rows = [
        diff_row("src_root", "changed.py", "CHANGED", runtime, repo),
        diff_row("src_root", "runtime.py", "RUNTIME_ONLY", runtime, repo),
        diff_row("src_root", "repo.py", "REPO_ONLY", runtime, repo),
    ]
    plan = planner.build_plan({"metadata": {}, "summary": {}, "rows": rows}, POLICY)
    review = skeleton_mod.build_skeleton(plan)
    review["mode"] = "RECONCILIATION_REVIEW_NOT_EXECUTION"
    selected = {
        "changed.py": "KEEP_REPO",
        "runtime.py": "ADOPT_RUNTIME",
        "repo.py": "KEEP_REPO",
    }
    if decisions:
        selected.update(decisions)
    for item in review["items"]:
        item["decision"] = selected[item["relative_path"]]
        item["reviewer"] = "Charles"
        item["reason"] = "Revisão manual concluída com evidência suficiente."
        item["evidence"] = ["evidence:manual-review"]
    return acceptance_mod.build_acceptance(plan, review)


def source_snapshot(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): staging_mod.sha256_file(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


class MaterializeReconciledStagingTests(unittest.TestCase):
    def test_valid_acceptance_materializes_only_staging(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime, repo = make_sources(base)
            acceptance = make_acceptance(runtime, repo)
            out = base / "staging"
            before_runtime = source_snapshot(runtime)
            before_repo = source_snapshot(repo)
            report = staging_mod.materialize_staging(runtime, repo, out, acceptance)
            self.assertEqual((out / "src/changed.py").read_text(), "value = 'repo'\n")
            self.assertEqual((out / "src/runtime.py").read_text(), "runtime_only = True\n")
            self.assertEqual((out / "src/repo.py").read_text(), "repo_only = True\n")
            self.assertEqual(source_snapshot(runtime), before_runtime)
            self.assertEqual(source_snapshot(repo), before_repo)
            self.assertTrue(report["staging_materialization_performed"])
            self.assertFalse(report["repository_write_performed"])
            self.assertFalse(report["runtime_write_performed"])
            self.assertFalse(report["operational_deployment_performed"])
            self.assertFalse(report["v8_homologated"])

    def test_runtime_only_exclude_does_not_import_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime, repo = make_sources(base)
            acceptance = make_acceptance(runtime, repo, {"runtime.py": "EXCLUDE_WITH_REASON"})
            out = base / "staging"
            staging_mod.materialize_staging(runtime, repo, out, acceptance)
            self.assertFalse((out / "src/runtime.py").exists())

    def test_repo_only_exclude_removes_file_from_staging_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime, repo = make_sources(base)
            acceptance = make_acceptance(runtime, repo, {"repo.py": "EXCLUDE_WITH_REASON"})
            out = base / "staging"
            staging_mod.materialize_staging(runtime, repo, out, acceptance)
            self.assertFalse((out / "src/repo.py").exists())
            self.assertTrue((repo / "src/repo.py").is_file())

    def test_stale_runtime_hash_is_blocked_before_output_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime, repo = make_sources(base)
            acceptance = make_acceptance(runtime, repo)
            write(runtime / "src/runtime.py", "changed_after_acceptance = True\n")
            out = base / "staging"
            with self.assertRaisesRegex(staging_mod.StagingMaterializationError, "SHA-256 divergente em runtime"):
                staging_mod.materialize_staging(runtime, repo, out, acceptance)
            self.assertFalse(out.exists())

    def test_stale_repo_hash_is_blocked_before_output_creation(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime, repo = make_sources(base)
            acceptance = make_acceptance(runtime, repo)
            write(repo / "src/changed.py", "changed_after_acceptance = True\n")
            out = base / "staging"
            with self.assertRaisesRegex(staging_mod.StagingMaterializationError, "SHA-256 divergente em repositório"):
                staging_mod.materialize_staging(runtime, repo, out, acceptance)
            self.assertFalse(out.exists())

    def test_tampered_acceptance_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime, repo = make_sources(base)
            acceptance = make_acceptance(runtime, repo)
            acceptance["decisions"][0]["decision"] = "ADOPT_RUNTIME"
            with self.assertRaisesRegex(staging_mod.StagingMaterializationError, "acceptance_sha256"):
                staging_mod.materialize_staging(runtime, repo, base / "staging", acceptance)

    def test_output_inside_runtime_or_repo_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime, repo = make_sources(base)
            acceptance = make_acceptance(runtime, repo)
            for out in (runtime / "staging", repo / "staging"):
                with self.assertRaisesRegex(staging_mod.StagingMaterializationError, "não pode ficar dentro"):
                    staging_mod.materialize_staging(runtime, repo, out, acceptance)

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime, repo = make_sources(base)
            acceptance = make_acceptance(runtime, repo)
            out = base / "staging"
            out.mkdir()
            write(out / "keep.txt", "preservar")
            with self.assertRaisesRegex(staging_mod.StagingMaterializationError, "já existe"):
                staging_mod.materialize_staging(runtime, repo, out, acceptance)
            self.assertEqual((out / "keep.txt").read_text(), "preservar")

    def test_destination_collision_between_runtime_layouts_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            repo = base / "repo"
            write(runtime / "app/src/a.py", "app = True\n")
            write(runtime / "src/a.py", "root = True\n")
            write(repo / "src/a.py", "repo = True\n")
            rows = [
                diff_row("src_app", "a.py", "CHANGED", runtime, repo),
                diff_row("src_root", "a.py", "CHANGED", runtime, repo),
            ]
            plan = planner.build_plan({"metadata": {}, "summary": {}, "rows": rows}, POLICY)
            review = skeleton_mod.build_skeleton(plan)
            review["mode"] = "RECONCILIATION_REVIEW_NOT_EXECUTION"
            for item in review["items"]:
                item["decision"] = "KEEP_REPO"
                item["reviewer"] = "Charles"
                item["reason"] = "Revisão manual concluída com evidência suficiente."
                item["evidence"] = ["evidence:manual-review"]
            acceptance = acceptance_mod.build_acceptance(plan, review)
            with self.assertRaisesRegex(staging_mod.StagingMaterializationError, "Colisão de destino"):
                staging_mod.materialize_staging(runtime, repo, base / "staging", acceptance)

    def test_embedded_secret_in_adopted_runtime_is_blocked_and_stage_cleaned(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime, repo = make_sources(base)
            write(runtime / "src/runtime.py", 'password = "real-secret-123456"\n')
            acceptance = make_acceptance(runtime, repo)
            out = base / "staging"
            with self.assertRaisesRegex(staging_mod.StagingMaterializationError, "possível segredo"):
                staging_mod.materialize_staging(runtime, repo, out, acceptance)
            self.assertFalse(out.exists())

    def test_repo_symlink_is_blocked_when_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime, repo = make_sources(base)
            link = repo / "src/link.py"
            try:
                os.symlink(repo / "src/changed.py", link)
            except (OSError, NotImplementedError):
                self.skipTest("symlink indisponível")
            acceptance = make_acceptance(runtime, repo)
            with self.assertRaisesRegex(staging_mod.StagingMaterializationError, "Symlink proibido"):
                staging_mod.materialize_staging(runtime, repo, base / "staging", acceptance)

    def test_report_hash_and_tree_hash_are_stable_for_same_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime, repo = make_sources(base)
            acceptance = make_acceptance(runtime, repo)
            r1 = staging_mod.materialize_staging(runtime, repo, base / "staging1", deepcopy(acceptance))
            r2 = staging_mod.materialize_staging(runtime, repo, base / "staging2", deepcopy(acceptance))
            self.assertEqual(r1["tree_sha256"], r2["tree_sha256"])
            self.assertEqual(r1["report_sha256"], r2["report_sha256"])


if __name__ == "__main__":
    unittest.main()
