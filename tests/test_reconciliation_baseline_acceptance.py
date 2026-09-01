from __future__ import annotations

import json
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
import plan_runtime_reconciliation as planner  # noqa: E402

POLICY = json.loads((ROOT / "config/runtime_reconciliation_plan_policy_v8.json").read_text(encoding="utf-8"))
H1 = "1" * 64
H2 = "2" * 64


def row(area: str, path: str, status: str) -> dict:
    runtime_hash = H1
    repo_hash = H2
    if status == "SAME":
        repo_hash = runtime_hash
    if status == "RUNTIME_ONLY":
        repo_hash = ""
    if status == "REPO_ONLY":
        runtime_hash = ""
    return {
        "area": area,
        "relative_path": path,
        "status": status,
        "runtime_sha256": runtime_hash,
        "repo_sha256": repo_hash,
        "runtime_size": 10 if runtime_hash else 0,
        "repo_size": 10 if repo_hash else 0,
    }


def make_plan(*, sensitive: bool = False) -> dict:
    rows = [
        row("src_root", "changed.py", "CHANGED"),
        row("src_root", "runtime.py", "RUNTIME_ONLY"),
        row("src_root", "repo.py", "REPO_ONLY"),
    ]
    if sensitive:
        rows.append(row("config_root", "app.toml", "CHANGED"))
    return planner.build_plan({"metadata": {}, "summary": {}, "rows": rows}, POLICY)


def completed_review(plan: dict, *, sensitive_decision: str = "KEEP_REPO") -> dict:
    review = skeleton_mod.build_skeleton(plan)
    review["mode"] = "RECONCILIATION_REVIEW_NOT_EXECUTION"
    decisions = {
        "changed.py": "KEEP_REPO",
        "runtime.py": "ADOPT_RUNTIME",
        "repo.py": "KEEP_REPO",
        "app.toml": sensitive_decision,
    }
    for item in review["items"]:
        item["decision"] = decisions[item["relative_path"]]
        item["reviewer"] = "Charles"
        item["reason"] = "Decisão revisada manualmente com evidência suficiente."
        item["evidence"] = ["evidence:manual-review"]
    return review


class ReconciliationBaselineAcceptanceTests(unittest.TestCase):
    def test_safe_completed_review_builds_acceptance(self):
        plan = make_plan()
        review = completed_review(plan)
        acceptance = acceptance_mod.build_acceptance(plan, review)
        self.assertTrue(acceptance["review_complete"])
        self.assertTrue(acceptance["baseline_ready"])
        self.assertEqual(len(acceptance["decisions"]), 3)
        self.assertFalse(acceptance["automatic_write_allowed"])
        self.assertFalse(acceptance["execution_performed"])
        self.assertFalse(acceptance["v8_homologated"])

    def test_pending_review_is_rejected(self):
        plan = make_plan()
        review = skeleton_mod.build_skeleton(plan)
        with self.assertRaisesRegex(acceptance_mod.BaselineAcceptanceError, "não está completa"):
            acceptance_mod.build_acceptance(plan, review)

    def test_merge_required_is_rejected_as_not_baseline_ready(self):
        plan = make_plan()
        review = completed_review(plan)
        target = next(item for item in review["items"] if item["relative_path"] == "changed.py")
        target["decision"] = "MERGE_REQUIRED"
        with self.assertRaisesRegex(acceptance_mod.BaselineAcceptanceError, "não libera baseline"):
            acceptance_mod.build_acceptance(plan, review)

    def test_security_review_required_is_rejected_as_not_baseline_ready(self):
        plan = make_plan(sensitive=True)
        review = completed_review(plan, sensitive_decision="SECURITY_REVIEW_REQUIRED")
        with self.assertRaisesRegex(acceptance_mod.BaselineAcceptanceError, "não libera baseline"):
            acceptance_mod.build_acceptance(plan, review)

    def test_sensitive_keep_repo_can_be_accepted_with_evidence(self):
        plan = make_plan(sensitive=True)
        review = completed_review(plan, sensitive_decision="KEEP_REPO")
        acceptance = acceptance_mod.build_acceptance(plan, review)
        item = next(x for x in acceptance["decisions"] if x["relative_path"] == "app.toml")
        self.assertEqual(item["risk"], "CRITICAL")
        self.assertEqual(item["decision"], "KEEP_REPO")
        self.assertEqual(item["reviewer"], "Charles")
        self.assertTrue(item["evidence"])

    def test_sensitive_adopt_runtime_is_rejected_by_review_contract(self):
        plan = make_plan(sensitive=True)
        review = completed_review(plan, sensitive_decision="ADOPT_RUNTIME")
        with self.assertRaisesRegex(acceptance_mod.BaselineAcceptanceError, "incompatível"):
            acceptance_mod.build_acceptance(plan, review)

    def test_tampered_plan_is_rejected(self):
        plan = make_plan()
        review = completed_review(plan)
        plan["entries"][0]["status"] = "RUNTIME_ONLY"
        with self.assertRaisesRegex(acceptance_mod.BaselineAcceptanceError, "plan_sha256"):
            acceptance_mod.build_acceptance(plan, review)

    def test_tampered_review_metadata_is_rejected(self):
        plan = make_plan()
        review = completed_review(plan)
        review["items"][0]["risk"] = "CRITICAL"
        with self.assertRaisesRegex(acceptance_mod.BaselineAcceptanceError, "Metadado alterado"):
            acceptance_mod.build_acceptance(plan, review)

    def test_acceptance_binds_plan_review_and_validation_hashes(self):
        plan = make_plan()
        review = completed_review(plan)
        acceptance = acceptance_mod.build_acceptance(plan, review)
        self.assertEqual(acceptance["plan_sha256"], plan["plan_sha256"])
        self.assertEqual(acceptance["review_sha256"], acceptance_mod.canonical_hash(review))
        self.assertEqual(len(acceptance["review_validation_sha256"]), 64)
        self.assertEqual(len(acceptance["acceptance_sha256"]), 64)

    def test_acceptance_hash_is_stable_and_input_is_not_mutated(self):
        plan = make_plan()
        review = completed_review(plan)
        plan_before = deepcopy(plan)
        review_before = deepcopy(review)
        a1 = acceptance_mod.build_acceptance(plan, review)
        a2 = acceptance_mod.build_acceptance(plan, review)
        self.assertEqual(a1["acceptance_sha256"], a2["acceptance_sha256"])
        self.assertEqual(plan, plan_before)
        self.assertEqual(review, review_before)

    def test_acceptance_carries_exact_runtime_and_repo_hashes_from_plan(self):
        plan = make_plan()
        review = completed_review(plan)
        acceptance = acceptance_mod.build_acceptance(plan, review)
        by_path = {item["relative_path"]: item for item in acceptance["decisions"]}
        plan_by_path = {item["relative_path"]: item for item in plan["entries"] if item["review_required"]}
        for path, entry in plan_by_path.items():
            self.assertEqual(by_path[path]["runtime_sha256"], entry["runtime_sha256"])
            self.assertEqual(by_path[path]["repo_sha256"], entry["repo_sha256"])

    def test_cli_refuses_to_overwrite_existing_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan = make_plan()
            review = completed_review(plan)
            plan_path = root / "plan.json"
            review_path = root / "review.json"
            output = root / "acceptance.json"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            review_path.write_text(json.dumps(review), encoding="utf-8")
            output.write_text("preservar", encoding="utf-8")
            old_argv = sys.argv
            try:
                sys.argv = [
                    "build_reconciliation_baseline_acceptance.py",
                    "--plan", str(plan_path),
                    "--review", str(review_path),
                    "--output", str(output),
                ]
                self.assertEqual(acceptance_mod.main(), 2)
            finally:
                sys.argv = old_argv
            self.assertEqual(output.read_text(encoding="utf-8"), "preservar")


if __name__ == "__main__":
    unittest.main()
