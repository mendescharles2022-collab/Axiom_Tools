from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "plan_runtime_reconciliation.py"
POLICY_PATH = ROOT / "config" / "runtime_reconciliation_plan_policy_v8.json"
SPEC = importlib.util.spec_from_file_location("plan_runtime_reconciliation_test", SCRIPT)
planner = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = planner
SPEC.loader.exec_module(planner)

H1 = "1" * 64
H2 = "2" * 64


def policy() -> dict:
    return json.loads(POLICY_PATH.read_text(encoding="utf-8"))


def row(area: str, path: str, status: str, runtime_hash: str = H1, repo_hash: str = H2) -> dict:
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


def diff(rows: list[dict]) -> dict:
    return {
        "metadata": {"runtime_layout": "src"},
        "summary": {},
        "rows": rows,
    }


class RuntimeReconciliationPlanTests(unittest.TestCase):
    def test_statuses_map_to_review_actions_without_writes(self):
        source = diff([
            row("src_root", "a.py", "SAME"),
            row("src_root", "b.py", "CHANGED"),
            row("src_root", "c.py", "RUNTIME_ONLY"),
            row("src_root", "d.py", "REPO_ONLY"),
        ])
        plan = planner.build_plan(source, policy())
        actions = {entry["relative_path"]: entry["proposed_action"] for entry in plan["entries"]}
        self.assertEqual(actions["a.py"], "NO_ACTION")
        self.assertEqual(actions["b.py"], "REVIEW_MERGE")
        self.assertEqual(actions["c.py"], "REVIEW_IMPORT_RUNTIME")
        self.assertEqual(actions["d.py"], "REVIEW_KEEP_REPO")
        self.assertFalse(plan["automatic_write_allowed"])
        self.assertTrue(all(entry["automatic_write"] is False for entry in plan["entries"]))
        self.assertFalse(plan["v8_homologated"])

    def test_sensitive_changed_config_requires_security_review(self):
        plan = planner.build_plan(diff([row("config_root", "app.toml", "CHANGED")]), policy())
        entry = plan["entries"][0]
        self.assertEqual(entry["proposed_action"], "SECURITY_REVIEW_REQUIRED")
        self.assertEqual(entry["risk"], "CRITICAL")

    def test_sensitive_runtime_only_release_identity_is_never_import_action(self):
        plan = planner.build_plan(
            diff([row("config_root", "release_identity.toml", "RUNTIME_ONLY")]),
            policy(),
        )
        self.assertEqual(plan["entries"][0]["proposed_action"], "SECURITY_REVIEW_REQUIRED")

    def test_sensitive_same_file_remains_no_action(self):
        plan = planner.build_plan(diff([row("config_root", "release_identity.toml", "SAME")]), policy())
        self.assertEqual(plan["entries"][0]["proposed_action"], "NO_ACTION")
        self.assertFalse(plan["entries"][0]["review_required"])

    def test_sensitive_path_pattern_outside_config_is_protected(self):
        plan = planner.build_plan(diff([row("src_root", "auth/session.py", "CHANGED")]), policy())
        self.assertEqual(plan["entries"][0]["proposed_action"], "SECURITY_REVIEW_REQUIRED")

    def test_duplicate_area_path_is_rejected(self):
        source = diff([row("src_root", "a.py", "CHANGED"), row("src_root", "a.py", "CHANGED")])
        with self.assertRaisesRegex(planner.ReconciliationPlanError, "duplicada"):
            planner.build_plan(source, policy())

    def test_path_traversal_is_rejected(self):
        with self.assertRaisesRegex(planner.ReconciliationPlanError, "inseguro"):
            planner.build_plan(diff([row("src_root", "../a.py", "CHANGED")]), policy())

    def test_same_with_different_hashes_is_rejected(self):
        bad = row("src_root", "a.py", "SAME")
        bad["repo_sha256"] = H2
        with self.assertRaisesRegex(planner.ReconciliationPlanError, "SAME com hashes divergentes"):
            planner.build_plan(diff([bad]), policy())

    def test_changed_with_equal_hashes_is_rejected(self):
        bad = row("src_root", "a.py", "CHANGED", H1, H1)
        with self.assertRaisesRegex(planner.ReconciliationPlanError, "CHANGED com hashes iguais"):
            planner.build_plan(diff([bad]), policy())

    def test_unknown_status_is_rejected(self):
        bad = row("src_root", "a.py", "CHANGED")
        bad["status"] = "AUTO_IMPORT"
        with self.assertRaisesRegex(planner.ReconciliationPlanError, "Status não permitido"):
            planner.build_plan(diff([bad]), policy())

    def test_policy_cannot_enable_automatic_write(self):
        p = policy()
        p["automatic_write_allowed"] = True
        with self.assertRaisesRegex(planner.ReconciliationPlanError, "proibir escrita automática"):
            planner.build_plan(diff([]), p)

    def test_input_is_not_mutated_and_plan_hash_is_stable(self):
        source = diff([row("src_root", "b.py", "CHANGED"), row("src_root", "a.py", "SAME")])
        original = deepcopy(source)
        first = planner.build_plan(source, policy())
        second = planner.build_plan(source, policy())
        self.assertEqual(source, original)
        self.assertEqual(first["plan_sha256"], second["plan_sha256"])
        self.assertEqual([entry["relative_path"] for entry in first["entries"]], ["a.py", "b.py"])

    def test_cli_refuses_to_overwrite_existing_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            diff_path = root / "diff.json"
            policy_path = root / "policy.json"
            output = root / "plan.json"
            diff_path.write_text(json.dumps(diff([row("src_root", "a.py", "SAME")])), encoding="utf-8")
            policy_path.write_text(json.dumps(policy()), encoding="utf-8")
            output.write_text("preservar", encoding="utf-8")
            old_argv = sys.argv
            try:
                sys.argv = [
                    "plan_runtime_reconciliation.py",
                    "--diff", str(diff_path),
                    "--policy", str(policy_path),
                    "--output", str(output),
                ]
                self.assertEqual(planner.main(), 2)
            finally:
                sys.argv = old_argv
            self.assertEqual(output.read_text(encoding="utf-8"), "preservar")


if __name__ == "__main__":
    unittest.main()
