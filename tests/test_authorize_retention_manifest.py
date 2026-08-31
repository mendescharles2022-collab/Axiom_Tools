from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

REVIEW_SCRIPT = ROOT / "scripts" / "review_retention_plan.py"
review_spec = importlib.util.spec_from_file_location("review_retention_plan", REVIEW_SCRIPT)
review_module = importlib.util.module_from_spec(review_spec)
assert review_spec and review_spec.loader
sys.modules[review_spec.name] = review_module
review_spec.loader.exec_module(review_module)

SCRIPT = ROOT / "scripts" / "authorize_retention_manifest.py"
spec = importlib.util.spec_from_file_location("authorize_retention_manifest", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def reviewed(decision: str = "ELIGIBLE", category: str = "TEMPORARIO_PROCESSAMENTO") -> dict:
    payload = {
        "version": 1,
        "mode": "REVIEWED_NOT_AUTHORIZED",
        "source_plan_sha256": "A" * 64,
        "summary": {
            "candidates": 1,
            "eligible": 1 if decision == "ELIGIBLE" else 0,
            "keep": 1 if decision == "KEEP" else 0,
            "blocked": 1 if decision == "BLOCK" else 0,
            "eligible_bytes": 3 if decision == "ELIGIBLE" else 0,
        },
        "items": [
            {
                "rule_id": "temp",
                "root": "temp",
                "path": "job/a.tmp",
                "category": category,
                "decision": decision,
                "reason": "Job concluído e temporário reconstruível.",
                "evidence": ["job-status:completed"] if decision == "ELIGIBLE" else [],
                "size": 3,
                "age_days": 40.0,
            }
        ],
        "execution_authorized": False,
        "warning": "review only",
    }
    payload["review_sha256"] = review_module.canonical_hash(payload)
    return payload


def confirmation(review_doc: dict, **overrides) -> dict:
    doc = {
        "version": 1,
        "review_sha256": review_doc["review_sha256"],
        "confirmation": module.CONFIRMATION_PHRASE,
        "approver": "Auditoria V8",
        "reference": "audit/B48/test",
    }
    doc.update(overrides)
    return doc


class RetentionAuthorizationTests(unittest.TestCase):
    def test_eligible_review_generates_non_executed_manifest(self):
        review_doc = reviewed()
        manifest = module.authorize_manifest(review_doc, confirmation(review_doc))
        self.assertEqual(manifest["mode"], "AUTHORIZED_MANIFEST_NOT_EXECUTED")
        self.assertEqual(manifest["summary"]["authorized_items"], 1)
        self.assertEqual(manifest["summary"]["authorized_bytes"], 3)
        self.assertEqual(manifest["items"][0]["root"], "temp")
        self.assertFalse(manifest["execution_performed"])
        self.assertEqual(len(manifest["manifest_sha256"]), 64)

    def test_wrong_confirmation_phrase_is_rejected(self):
        review_doc = reviewed()
        with self.assertRaises(module.RetentionAuthorizationError):
            module.authorize_manifest(
                review_doc,
                confirmation(review_doc, confirmation="APAGAR_AGORA"),
            )

    def test_tampered_review_is_rejected(self):
        review_doc = reviewed()
        confirmation_doc = confirmation(review_doc)
        review_doc["items"][0]["size"] = 999
        with self.assertRaises(module.RetentionAuthorizationError):
            module.authorize_manifest(review_doc, confirmation_doc)

    def test_confirmation_for_different_review_is_rejected(self):
        review_doc = reviewed()
        with self.assertRaises(module.RetentionAuthorizationError):
            module.authorize_manifest(
                review_doc,
                confirmation(review_doc, review_sha256="B" * 64),
            )

    def test_protected_category_cannot_be_smuggled_as_eligible(self):
        review_doc = reviewed(category="BACKUP")
        with self.assertRaises(module.RetentionAuthorizationError):
            module.authorize_manifest(review_doc, confirmation(review_doc))

    def test_keep_item_is_not_authorized_for_execution(self):
        review_doc = reviewed(decision="KEEP", category="BACKUP")
        manifest = module.authorize_manifest(review_doc, confirmation(review_doc))
        self.assertEqual(manifest["summary"]["authorized_items"], 0)
        self.assertEqual(manifest["items"], [])
        self.assertFalse(manifest["execution_performed"])

    def test_invalid_reference_is_rejected(self):
        review_doc = reviewed()
        with self.assertRaises(module.RetentionAuthorizationError):
            module.authorize_manifest(
                review_doc,
                confirmation(review_doc, reference="../segredo"),
            )

    def test_manifest_contains_only_relative_paths(self):
        review_doc = reviewed()
        manifest = module.authorize_manifest(review_doc, confirmation(review_doc))
        self.assertEqual(manifest["items"][0]["path"], "job/a.tmp")
        self.assertFalse(Path(manifest["items"][0]["path"]).is_absolute())

    def test_missing_root_on_eligible_item_is_rejected(self):
        review_doc = reviewed()
        review_doc["items"][0].pop("root")
        review_doc["review_sha256"] = review_module.canonical_hash(
            {key: value for key, value in review_doc.items() if key != "review_sha256"}
        )
        with self.assertRaises(module.RetentionAuthorizationError):
            module.authorize_manifest(review_doc, confirmation(review_doc))


if __name__ == "__main__":
    unittest.main()
