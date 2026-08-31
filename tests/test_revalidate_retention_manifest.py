from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

SCRIPT = ROOT / "scripts" / "revalidate_retention_manifest.py"
spec = importlib.util.spec_from_file_location("revalidate_retention_manifest", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def manifest_for(path: Path, root_key: str = "temp", rel: str = "job/a.tmp") -> dict:
    stat = path.stat()
    payload = {
        "version": 1,
        "mode": "AUTHORIZED_MANIFEST_NOT_EXECUTED",
        "source_review_sha256": "A" * 64,
        "authorization": {
            "approver": "Auditoria V8",
            "reference": "audit/B48/test",
            "confirmation": module.authorization.CONFIRMATION_PHRASE,
        },
        "summary": {
            "authorized_items": 1,
            "authorized_bytes": stat.st_size,
        },
        "items": [
            {
                "rule_id": "temp",
                "root": root_key,
                "path": rel,
                "category": "TEMPORARIO_PROCESSAMENTO",
                "size": stat.st_size,
                "age_days": 40.0,
                "mtime_ns": stat.st_mtime_ns,
                "sha256": module.planner.sha256_file(path),
                "reason": "Temporário reconstruível.",
                "evidence": ["job-status:completed"],
            }
        ],
        "execution_performed": False,
        "warning": "not executed",
    }
    payload["manifest_sha256"] = module.review.canonical_hash(payload)
    return payload


class RetentionRevalidationTests(unittest.TestCase):
    def test_unchanged_file_is_ready_without_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "managed"
            target = root / "job" / "a.tmp"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"abc")
            before = target.read_bytes()
            manifest = manifest_for(target)

            report = module.revalidate_manifest(manifest, {"temp": root})

            self.assertTrue(report["ready_for_execution"])
            self.assertEqual(report["summary"]["findings"], 0)
            self.assertFalse(report["execution_performed"])
            self.assertEqual(target.read_bytes(), before)

    def test_same_size_replacement_is_blocked_by_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "managed"
            target = root / "job" / "a.tmp"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"abc")
            manifest = manifest_for(target)

            target.write_bytes(b"xyz")
            os.utime(target, None)
            report = module.revalidate_manifest(manifest, {"temp": root})

            codes = {item["code"] for item in report["findings"]}
            self.assertFalse(report["ready_for_execution"])
            self.assertIn("SHA256_CHANGED", codes)

    def test_missing_file_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "managed"
            target = root / "job" / "a.tmp"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"abc")
            manifest = manifest_for(target)
            target.unlink()

            report = module.revalidate_manifest(manifest, {"temp": root})
            self.assertFalse(report["ready_for_execution"])
            self.assertEqual(report["findings"][0]["code"], "MISSING")

    def test_tampered_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "managed"
            target = root / "job" / "a.tmp"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"abc")
            manifest = manifest_for(target)
            manifest["items"][0]["size"] = 999

            with self.assertRaises(module.RetentionRevalidationError):
                module.revalidate_manifest(manifest, {"temp": root})

    def test_unknown_root_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "managed"
            target = root / "job" / "a.tmp"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"abc")
            manifest = manifest_for(target, root_key="other")

            with self.assertRaises(module.RetentionRevalidationError):
                module.revalidate_manifest(manifest, {"temp": root})

    def test_path_traversal_is_rejected_even_with_valid_manifest_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "managed"
            target = root / "job" / "a.tmp"
            target.parent.mkdir(parents=True)
            target.write_bytes(b"abc")
            manifest = manifest_for(target)
            manifest["items"][0]["path"] = "../outside.tmp"
            manifest.pop("manifest_sha256")
            manifest["manifest_sha256"] = module.review.canonical_hash(manifest)

            with self.assertRaises(module.RetentionRevalidationError):
                module.revalidate_manifest(manifest, {"temp": root})

    def test_symlink_candidate_is_blocked_when_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "managed"
            real = root / "real.tmp"
            real.parent.mkdir(parents=True)
            real.write_bytes(b"abc")
            link = root / "job" / "a.tmp"
            link.parent.mkdir(parents=True)
            try:
                link.symlink_to(real)
            except (OSError, NotImplementedError):
                self.skipTest("Ambiente não permite symlink")
            manifest = manifest_for(real, rel="job/a.tmp")

            report = module.revalidate_manifest(manifest, {"temp": root})
            self.assertFalse(report["ready_for_execution"])
            self.assertEqual(report["findings"][0]["code"], "REPARSE_POINT")


if __name__ == "__main__":
    unittest.main()
