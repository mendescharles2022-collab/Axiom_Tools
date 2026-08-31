from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "plan_retention_cleanup.py"
spec = importlib.util.spec_from_file_location("plan_retention_cleanup", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def write(path: Path, data: bytes = b"x", mtime: float | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    if mtime is not None:
        os.utime(path, (mtime, mtime))


def policy(
    age: float = 30,
    glob: str = "**/*",
    extensions: list[str] | None = None,
) -> dict:
    rule = {
        "id": "temp",
        "root": "temp",
        "glob": glob,
        "older_than_days": age,
    }
    if extensions is not None:
        rule["extensions"] = extensions
    return {"version": 1, "rules": [rule]}


class RetentionPlannerTests(unittest.TestCase):
    def test_old_file_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = 1_700_000_000
            write(root / "a.tmp", b"abc", now - 40 * 86400)
            report = module.plan_cleanup({"temp": root}, policy(), now)
            self.assertEqual(report["summary"]["candidate_files"], 1)
            self.assertEqual(report["summary"]["candidate_bytes"], 3)
            item = report["rules"][0]["items"][0]
            self.assertEqual(item["status"], "CANDIDATE")
            self.assertEqual(len(item["sha256"]), 64)
            self.assertIsInstance(item["mtime_ns"], int)

    def test_recent_file_kept(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = 1_700_000_000
            write(root / "a.tmp", b"x", now - 2 * 86400)
            report = module.plan_cleanup({"temp": root}, policy(), now)
            item = report["rules"][0]["items"][0]
            self.assertEqual(item["status"], "KEEP_RECENT")
            self.assertNotIn("sha256", item)
            self.assertIsInstance(item["mtime_ns"], int)

    def test_extension_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = 1_700_000_000
            write(root / "a.pdf", mtime=now - 40 * 86400)
            write(root / "b.tmp", mtime=now - 40 * 86400)
            report = module.plan_cleanup(
                {"temp": root},
                policy(extensions=[".tmp"]),
                now,
            )
            self.assertEqual(report["summary"]["candidate_files"], 1)
            self.assertEqual(report["rules"][0]["items"][0]["path"], "b.tmp")

    def test_negative_age_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(module.RetentionError):
                module.normalize_policy(policy(-1), {"temp": root})

    def test_unknown_root_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(module.RetentionError):
                module.normalize_policy(policy(), {"other": root})

    def test_unsafe_glob_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(module.RetentionError):
                module.normalize_policy(policy(glob="../*"), {"temp": root})

    def test_no_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            now = 1_700_000_000
            target = root / "a.tmp"
            write(target, b"abc", now - 40 * 86400)
            before = target.read_bytes()
            module.plan_cleanup({"temp": root}, policy(), now)
            self.assertTrue(target.exists())
            self.assertEqual(target.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
