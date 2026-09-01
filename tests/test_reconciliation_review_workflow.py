from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import plan_runtime_reconciliation as planner  # noqa: E402
import create_reconciliation_review_skeleton as skeleton_mod  # noqa: E402
import validate_reconciliation_review as review_mod  # noqa: E402

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


def make_plan() -> dict:
    return planner.build_plan(
        {
            "metadata": {},
            "summary": {},
            "rows": [
                row("src_root", "same.py", "SAME"),
                row("src_root", "changed.py", "CHANGED"),
                row("src_root", "runtime.py", "RUNTIME_ONLY"),
                row("src_root", "repo.py", "REPO_ONLY"),
                row("config_root", "app.toml", "CHANGED"),
            ],
        },
        POLICY,
    )


def reviewed_item(item: dict, decision: str, *, reviewer: str = "Charles", reason: str = "Decisão revisada com evidência.", evidence: list[str] | None = None) -> dict:
    value = deepcopy(item)
    value["decision"] = decision
    value["reviewer"] = reviewer
    value["reason"] = reason
    value["evidence"] = evidence or ["evidence:manual-review"]
    return value


class ReconciliationReviewWorkflowTests(unittest.TestCase):
    def test_skeleton_contains_only_review_required_items(self):
        plan = make_plan()
        skeleton = skeleton_mod.build_skeleton(plan)
        self.assertEqual(len(skeleton["items"]), 4)
        self.assertNotIn("same.py", [item["relative_path"] for item in skeleton["items"]])
        self.assertTrue(all(item["decision"] == "PENDING" for item in skeleton["items"]))
        self.assertTrue(all(item["reviewer"] == "" for item in skeleton["items"]))
        self.assertFalse(skeleton["automatic_write_allowed"])
        self.assertFalse(skeleton["baseline_ready"])
        self.assertFalse(skeleton["v8_homologated"])

    def test_skeleton_is_bound_to_plan_hash(self):
        plan = make_plan()
        skeleton = skeleton_mod.build_skeleton(plan)
        self.assertEqual(skeleton["plan_sha256"], plan["plan_sha256"])

    def test_tampered_plan_is_rejected_by_skeleton_builder(self):
        plan = make_plan()
        plan["entries"][0]["status"] = "CHANGED"
        with self.assertRaisesRegex(skeleton_mod.ReconciliationReviewSkeletonError, "plan_sha256"):
            skeleton_mod.build_skeleton(plan)

    def test_pending_skeleton_validates_but_is_not_complete_or_ready(self):
        plan = make_plan()
        skeleton = skeleton_mod.build_skeleton(plan)
        report = review_mod.validate_review(plan, skeleton)
        self.assertEqual(report["items_required"], 4)
        self.assertEqual(report["items_validated"], 4)
        self.assertFalse(report["review_complete"])
        self.assertFalse(report["baseline_ready"])
        self.assertEqual(report["decision_counts"]["PENDING"], 4)

    def test_missing_review_item_is_blocked(self):
        plan = make_plan()
        skeleton = skeleton_mod.build_skeleton(plan)
        skeleton["items"].pop()
        with self.assertRaisesRegex(review_mod.ReconciliationReviewError, "sem decisão"):
            review_mod.validate_review(plan, skeleton)

    def test_unknown_or_same_item_decision_is_blocked(self):
        plan = make_plan()
        skeleton = skeleton_mod.build_skeleton(plan)
        fake = deepcopy(skeleton["items"][0])
        fake["relative_path"] = "same.py"
        skeleton["items"].append(fake)
        with self.assertRaisesRegex(review_mod.ReconciliationReviewError, "inexistente/não revisável"):
            review_mod.validate_review(plan, skeleton)

    def test_duplicate_decision_is_blocked(self):
        plan = make_plan()
        skeleton = skeleton_mod.build_skeleton(plan)
        skeleton["items"].append(deepcopy(skeleton["items"][0]))
        with self.assertRaisesRegex(review_mod.ReconciliationReviewError, "duplicada"):
            review_mod.validate_review(plan, skeleton)

    def test_review_cannot_change_plan_metadata(self):
        plan = make_plan()
        skeleton = skeleton_mod.build_skeleton(plan)
        skeleton["items"][0]["risk"] = "LOW"
        with self.assertRaisesRegex(review_mod.ReconciliationReviewError, "Metadado alterado"):
            review_mod.validate_review(plan, skeleton)

    def test_non_pending_decision_requires_reviewer_reason_and_evidence(self):
        plan = make_plan()
        skeleton = skeleton_mod.build_skeleton(plan)
        target = next(item for item in skeleton["items"] if item["relative_path"] == "changed.py")
        target["decision"] = "KEEP_REPO"
        with self.assertRaisesRegex(review_mod.ReconciliationReviewError, "Revisor obrigatório"):
            review_mod.validate_review(plan, skeleton)

    def test_pending_cannot_fake_filled_review(self):
        plan = make_plan()
        skeleton = skeleton_mod.build_skeleton(plan)
        skeleton["items"][0]["reviewer"] = "Charles"
        with self.assertRaisesRegex(review_mod.ReconciliationReviewError, "PENDING não deve fingir"):
            review_mod.validate_review(plan, skeleton)

    def test_sensitive_item_cannot_adopt_runtime(self):
        plan = make_plan()
        skeleton = skeleton_mod.build_skeleton(plan)
        target = next(item for item in skeleton["items"] if item["relative_path"] == "app.toml")
        target.update(reviewed_item(target, "ADOPT_RUNTIME"))
        with self.assertRaisesRegex(review_mod.ReconciliationReviewError, "incompatível"):
            review_mod.validate_review(plan, skeleton)

    def test_sensitive_security_review_can_be_complete_but_not_baseline_ready(self):
        plan = make_plan()
        skeleton = skeleton_mod.build_skeleton(plan)
        decisions = {
            "changed.py": "KEEP_REPO",
            "runtime.py": "ADOPT_RUNTIME",
            "repo.py": "KEEP_REPO",
            "app.toml": "SECURITY_REVIEW_REQUIRED",
        }
        skeleton["mode"] = "RECONCILIATION_REVIEW_NOT_EXECUTION"
        skeleton["items"] = [reviewed_item(item, decisions[item["relative_path"]]) for item in skeleton["items"]]
        report = review_mod.validate_review(plan, skeleton)
        self.assertTrue(report["review_complete"])
        self.assertFalse(report["baseline_ready"])
        self.assertEqual(report["decision_counts"]["SECURITY_REVIEW_REQUIRED"], 1)

    def test_all_safe_resolved_decisions_can_be_baseline_ready(self):
        plan = planner.build_plan(
            {
                "metadata": {},
                "summary": {},
                "rows": [
                    row("src_root", "changed.py", "CHANGED"),
                    row("src_root", "runtime.py", "RUNTIME_ONLY"),
                    row("src_root", "repo.py", "REPO_ONLY"),
                ],
            },
            POLICY,
        )
        skeleton = skeleton_mod.build_skeleton(plan)
        decisions = {"changed.py": "KEEP_REPO", "runtime.py": "ADOPT_RUNTIME", "repo.py": "KEEP_REPO"}
        skeleton["mode"] = "RECONCILIATION_REVIEW_NOT_EXECUTION"
        skeleton["items"] = [reviewed_item(item, decisions[item["relative_path"]]) for item in skeleton["items"]]
        report = review_mod.validate_review(plan, skeleton)
        self.assertTrue(report["review_complete"])
        self.assertTrue(report["baseline_ready"])
        self.assertFalse(report["automatic_write_allowed"])
        self.assertFalse(report["v8_homologated"])

    def test_merge_required_is_reviewed_but_not_baseline_ready(self):
        plan = planner.build_plan(
            {"metadata": {}, "summary": {}, "rows": [row("src_root", "changed.py", "CHANGED")]},
            POLICY,
        )
        skeleton = skeleton_mod.build_skeleton(plan)
        skeleton["mode"] = "RECONCILIATION_REVIEW_NOT_EXECUTION"
        skeleton["items"] = [reviewed_item(skeleton["items"][0], "MERGE_REQUIRED")]
        report = review_mod.validate_review(plan, skeleton)
        self.assertTrue(report["review_complete"])
        self.assertFalse(report["baseline_ready"])

    def test_runtime_only_can_be_excluded_with_explicit_reason_and_evidence(self):
        plan = planner.build_plan(
            {"metadata": {}, "summary": {}, "rows": [row("src_root", "runtime.py", "RUNTIME_ONLY")]},
            POLICY,
        )
        skeleton = skeleton_mod.build_skeleton(plan)
        skeleton["mode"] = "RECONCILIATION_REVIEW_NOT_EXECUTION"
        skeleton["items"] = [reviewed_item(skeleton["items"][0], "EXCLUDE_WITH_REASON")]
        report = review_mod.validate_review(plan, skeleton)
        self.assertTrue(report["baseline_ready"])

    def test_review_plan_hash_mismatch_is_blocked(self):
        plan = make_plan()
        skeleton = skeleton_mod.build_skeleton(plan)
        skeleton["plan_sha256"] = H2
        with self.assertRaisesRegex(review_mod.ReconciliationReviewError, "plan_sha256 correto"):
            review_mod.validate_review(plan, skeleton)

    def test_review_cannot_enable_automatic_write_or_homologate(self):
        plan = make_plan()
        skeleton = skeleton_mod.build_skeleton(plan)
        skeleton["automatic_write_allowed"] = True
        with self.assertRaisesRegex(review_mod.ReconciliationReviewError, "escrita automática"):
            review_mod.validate_review(plan, skeleton)
        skeleton = skeleton_mod.build_skeleton(plan)
        skeleton["v8_homologated"] = True
        with self.assertRaisesRegex(review_mod.ReconciliationReviewError, "homologar"):
            review_mod.validate_review(plan, skeleton)

    def test_skeleton_cli_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plan_path = root / "plan.json"
            output = root / "review.json"
            plan_path.write_text(json.dumps(make_plan()), encoding="utf-8")
            output.write_text("preservar", encoding="utf-8")
            old_argv = sys.argv
            try:
                sys.argv = ["create_reconciliation_review_skeleton.py", "--plan", str(plan_path), "--output", str(output)]
                self.assertEqual(skeleton_mod.main(), 2)
            finally:
                sys.argv = old_argv
            self.assertEqual(output.read_text(encoding="utf-8"), "preservar")


if __name__ == "__main__":
    unittest.main()
