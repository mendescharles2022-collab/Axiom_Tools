from __future__ import annotations

import csv
import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_runtime_reconciliation.py"
spec = importlib.util.spec_from_file_location("audit_runtime_reconciliation", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_manifest(root: Path, files: list[Path]) -> None:
    with (root / module.MANIFEST_NAME).open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["RelativePath", "Length", "SHA256", "LastWriteUtc"],
        )
        writer.writeheader()
        for path in files:
            writer.writerow(
                {
                    "RelativePath": path.relative_to(root).as_posix(),
                    "Length": path.stat().st_size,
                    "SHA256": hashlib.sha256(path.read_bytes()).hexdigest().upper(),
                    "LastWriteUtc": "",
                }
            )


class ReconciliationAuditTests(unittest.TestCase):
    def test_compare_area_classifies_all_states(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            repo = base / "repo"
            write(runtime / "same.py", "x=1\n")
            write(repo / "same.py", "x=1\n")
            write(runtime / "changed.py", "x=2\n")
            write(repo / "changed.py", "x=3\n")
            write(runtime / "runtime_only.py", "x=4\n")
            write(repo / "repo_only.py", "x=5\n")

            rows = module.compare_area("src", runtime, repo)
            states = {row.relative_path: row.status for row in rows}
            self.assertEqual(states["same.py"], "SAME")
            self.assertEqual(states["changed.py"], "CHANGED")
            self.assertEqual(states["runtime_only.py"], "RUNTIME_ONLY")
            self.assertEqual(states["repo_only.py"], "REPO_ONLY")

    def test_manifest_verification_detects_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "app" / "src" / "pkg" / "a.py"
            write(target, "a=1\n")
            build_manifest(root, [target])

            ok, errors = module.verify_manifest(root)
            self.assertTrue(ok)
            self.assertEqual(errors, [])

            target.write_text("a=999\n", encoding="utf-8")
            ok, errors = module.verify_manifest(root)
            self.assertFalse(ok)
            self.assertTrue(any("divergente" in error.lower() for error in errors))

    def test_forbidden_content_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "app" / "src" / "safe.py", "ok=True\n")
            write(root / "database" / "prod.sqlite3", "not-a-real-db")
            violations = module.find_forbidden(root)
            self.assertTrue(any("database/" in item for item in violations))
            self.assertTrue(any("prod.sqlite3" in item for item in violations))


if __name__ == "__main__":
    unittest.main()
