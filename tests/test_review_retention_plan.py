from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "review_retention_plan.py"
spec = importlib.util.spec_from_file_location("review_retention_plan", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def plan() -> dict:
    return {
        "mode": "DRY_RUN_ONLY",
        "summary": {
            "rules": 1,
            "candidate_files": 1,
            "candidate_bytes": 3,
        },
        "rules": [
            {
                "id": "temp",
                "root": "temp",
                "matched": 1,
                "items": [
                    {
                        "path": "a.tmp",
                        "status": "CANDIDATE",
                        "age_days": 40.0,
                        "size": 3,
                        "mtime_ns": 123456789,
                        "sha256": "A" * 64,
                    }
                ],
            }
        ],
        "warning": "dry-run",
    }


def decisions_for(plan_doc: dict, **overrides) -> dict:
    item = {
        "rule_id": "temp",
        "path": "a.tmp",
        "category": "TEMPORARIO_PROCESSAMENTO",
        "decision": "ELIGIBLE",
        "reason": "Job concluído e temporário reconstruível.",
        "evidence": ["job-status:completed"],
    }
    item.update(overrides)
    return {
        "version": 1,
        "plan_sha256": module.canonical_hash(plan_doc),
        "decisions": [item],
    }


class RetentionReviewTests(unittest.TestCase):
    def test_safe_candidate_can_be_reviewed_as_eligible(self):
        plan_doc = plan()
        report = module.review_plan(plan_doc, decisions_for(plan_doc))
        self.assertEqual(report["mode"], "REVIEWED_NOT_AUTHORIZED")
        self.assertEqual(report["summary"]["eligible"], 1)
        self.assertEqual(report["summary"]["eligible_bytes"], 3)
        self.assertEqual(report["items"][0]["root"], "temp")
        self.assertEqual(report["items"][0]["sha256"], "A" * 64)
        self.assertEqual(report["items"][0]["mtime_ns"], 123456789)
        self.assertFalse(report["execution_authorized"])
        self.assertEqual(len(report["review_sha256"]), 64)

    def test_protected_category_cannot_be_eligible(self):
        plan_doc = plan()
        decisions = decisions_for(
            plan_doc,
            category="ORIGINAL_DOCUMENTAL",
        )
        with self.assertRaises(module.RetentionReviewError):
            module.review_plan(plan_doc, decisions)

    def test_eligible_requires_evidence(self):
        plan_doc = plan()
        decisions = decisions_for(plan_doc, evidence=[])
        with self.assertRaises(module.RetentionReviewError):
            module.review_plan(plan_doc, decisions)

    def test_missing_decision_is_rejected(self):
        plan_doc = plan()
        decisions = {
            "version": 1,
            "plan_sha256": module.canonical_hash(plan_doc),
            "decisions": [],
        }
        with self.assertRaises(module.RetentionReviewError):
            module.review_plan(plan_doc, decisions)

    def test_tampered_plan_hash_is_rejected(self):
        plan_doc = plan()
        decisions = decisions_for(plan_doc)
        plan_doc["rules"][0]["items"][0]["size"] = 999
        with self.assertRaises(module.RetentionReviewError):
            module.review_plan(plan_doc, decisions)

    def test_keep_is_allowed_for_protected_category(self):
        plan_doc = plan()
        decisions = decisions_for(
            plan_doc,
            category="BACKUP",
            decision="KEEP",
            reason="Backup protegido da versão estável anterior.",
            evidence=[],
        )
        report = module.review_plan(plan_doc, decisions)
        self.assertEqual(report["summary"]["keep"], 1)
        self.assertEqual(report["summary"]["eligible"], 0)
        self.assertEqual(report["items"][0]["root"], "temp")

    def test_decision_for_unknown_candidate_is_rejected(self):
        plan_doc = plan()
        decisions = decisions_for(plan_doc, path="other.tmp")
        with self.assertRaises(module.RetentionReviewError):
            module.review_plan(plan_doc, decisions)

    def test_invalid_root_in_plan_is_rejected(self):
        plan_doc = plan()
        plan_doc["rules"][0]["root"] = "../outside"
        decisions = decisions_for(plan_doc)
        with self.assertRaises(module.RetentionReviewError):
            module.review_plan(plan_doc, decisions)

    def test_missing_fingerprint_is_rejected(self):
        plan_doc = plan()
        plan_doc["rules"][0]["items"][0].pop("sha256")
        decisions = decisions_for(plan_doc)
        with self.assertRaises(module.RetentionReviewError):
            module.review_plan(plan_doc, decisions)


if __name__ == "__main__":
    unittest.main()
