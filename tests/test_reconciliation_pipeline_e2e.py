from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPORTER = ROOT / "scripts" / "export_runtime_reconciliation.py"
AUDITOR = ROOT / "scripts" / "audit_runtime_reconciliation.py"

sys.path.insert(0, str(ROOT / "scripts"))
import export_runtime_reconciliation as exporter  # noqa: E402


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_runtime(root: Path) -> None:
    write(root / "app" / "src" / "pkg" / "a.py", "VALUE = 1\n")
    write(root / "app" / "tests" / "test_a.py", "VALUE = 2\n")
    write(root / "app" / "pyproject.toml", "[project]\nname='runtime-fixture'\nversion='1.0.0'\n")
    # Dados que nunca podem aparecer no pacote de reconciliação.
    write(root / "database" / "prod.sqlite3", "fake-db")
    write(root / "documentos" / "cliente.pdf", "fake-pdf")


def build_repo_reference(root: Path) -> None:
    write(root / "src" / "pkg" / "a.py", "VALUE = 1\n")
    write(root / "tests" / "test_a.py", "VALUE = 2\n")
    write(root / "pyproject.toml", "[project]\nname='runtime-fixture'\nversion='1.0.0'\n")


def run_auditor(runtime_root: Path, repo_root: Path, report: Path, *, fail_on_diff: bool = True):
    command = [
        sys.executable,
        str(AUDITOR),
        "--runtime-root",
        str(runtime_root),
        "--repo-root",
        str(repo_root),
        "--output-dir",
        str(report),
    ]
    if fail_on_diff:
        command.append("--fail-on-diff")
    return subprocess.run(command, text=True, capture_output=True, check=False)


class ReconciliationPipelineE2ETests(unittest.TestCase):
    def test_export_zip_audit_identical_runtime_and_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            repo = base / "repo"
            out = base / "out"
            extracted = base / "extracted"
            report = base / "report"

            build_runtime(runtime)
            build_repo_reference(repo)

            result = exporter.export_runtime(runtime, out, "e2e")
            self.assertTrue(result.zip_path.is_file())
            self.assertGreater(result.file_count, 0)

            with zipfile.ZipFile(result.zip_path) as zf:
                zf.extractall(extracted)

            self.assertFalse((extracted / "database").exists())
            self.assertFalse((extracted / "documentos").exists())

            completed = run_auditor(extracted, repo, report)
            self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
            self.assertIn("RECONCILIATION_AUDIT_OK", completed.stdout)
            self.assertIn("Manifesto: OK", completed.stdout)

            payload = json.loads((report / "RECONCILIATION_DIFF.json").read_text(encoding="utf-8"))
            self.assertGreaterEqual(payload["summary"]["SAME"], 3)
            self.assertEqual(payload["summary"]["CHANGED"], 0)
            self.assertEqual(payload["summary"]["RUNTIME_ONLY"], 0)
            self.assertEqual(payload["summary"]["REPO_ONLY"], 0)

    def test_pipeline_returns_diff_when_repo_diverges(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            repo = base / "repo"
            out = base / "out"
            extracted = base / "extracted"
            report = base / "report"

            build_runtime(runtime)
            build_repo_reference(repo)
            result = exporter.export_runtime(runtime, out, "e2e")
            with zipfile.ZipFile(result.zip_path) as zf:
                zf.extractall(extracted)

            write(repo / "src" / "pkg" / "a.py", "VALUE = 999\n")
            completed = run_auditor(extracted, repo, report)

            self.assertEqual(completed.returncode, 3, completed.stderr + completed.stdout)
            payload = json.loads((report / "RECONCILIATION_DIFF.json").read_text(encoding="utf-8"))
            self.assertGreaterEqual(payload["summary"]["CHANGED"], 1)

    def test_pipeline_rejects_tampered_export_before_comparison(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            repo = base / "repo"
            out = base / "out"
            extracted = base / "extracted"
            report = base / "report"

            build_runtime(runtime)
            build_repo_reference(repo)
            result = exporter.export_runtime(runtime, out, "e2e")
            with zipfile.ZipFile(result.zip_path) as zf:
                zf.extractall(extracted)

            write(extracted / "app" / "src" / "pkg" / "a.py", "TAMPERED = True\n")
            completed = run_auditor(extracted, repo, report)

            self.assertEqual(completed.returncode, 2)
            self.assertIn("manifesto", completed.stderr.lower())
            self.assertFalse((report / "RECONCILIATION_DIFF.json").exists())


if __name__ == "__main__":
    unittest.main()
