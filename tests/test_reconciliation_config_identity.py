from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


exporter = load_module(
    "export_runtime_reconciliation_config_test",
    ROOT / "scripts" / "export_runtime_reconciliation.py",
)
auditor = load_module(
    "audit_runtime_reconciliation_config_test",
    ROOT / "scripts" / "audit_runtime_reconciliation.py",
)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ReconciliationConfigIdentityTests(unittest.TestCase):
    def test_export_includes_safe_config_and_release_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            write(runtime / "app" / "src" / "pkg" / "a.py", "VALUE=1\n")
            write(
                runtime / "app" / "config" / "release_identity.toml",
                'release_version="UNRELEASED"\nschema_version="UNRELEASED"\n',
            )
            write(runtime / "app" / "config" / "defaults.toml", 'mode="safe"\n')

            result = exporter.export_runtime(runtime, base / "out", "case")

            self.assertTrue(
                (result.stage / "app/config/release_identity.toml").is_file()
            )
            self.assertTrue((result.stage / "app/config/defaults.toml").is_file())

    def test_export_excludes_sensitive_config_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            write(runtime / "app" / "src" / "a.py", "VALUE=1\n")
            write(runtime / "app" / "config" / ".env", "PASSWORD=not-exported\n")
            write(
                runtime / "app" / "config" / "credentials.json",
                '{"user":"not-exported"}\n',
            )
            write(runtime / "app" / "config" / "safe.toml", 'mode="safe"\n')

            result = exporter.export_runtime(runtime, base / "out", "case")

            self.assertFalse((result.stage / "app/config/.env").exists())
            self.assertFalse(
                (result.stage / "app/config/credentials.json").exists()
            )
            self.assertTrue((result.stage / "app/config/safe.toml").is_file())

    def test_hardcoded_secret_inside_safe_named_config_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            write(runtime / "src" / "a.py", "VALUE=1\n")
            write(
                runtime / "config" / "settings.toml",
                'api_key = "sk_live_ABC123456789"\n',
            )

            with self.assertRaises(exporter.ExportError):
                exporter.export_runtime(runtime, base / "out", "case")

    def test_export_info_does_not_expose_absolute_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime-private-root"
            out = base / "private-output"
            write(runtime / "src" / "a.py", "VALUE=1\n")

            result = exporter.export_runtime(runtime, out, "case")
            info = (result.stage / exporter.INFO_NAME).read_text(encoding="utf-8")

            self.assertNotIn(str(runtime.resolve()), info)
            self.assertNotIn(str(out.resolve()), info)
            self.assertNotIn(str(result.stage.resolve()), info)

    def test_auditor_compares_release_identity_without_absolute_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            runtime = base / "runtime"
            repo = base / "repo"
            report = base / "report"
            write(runtime / "app" / "src" / "pkg" / "a.py", "VALUE=1\n")
            identity = 'release_version="UNRELEASED"\nschema_version="UNRELEASED"\n'
            write(runtime / "app" / "config" / "release_identity.toml", identity)
            write(repo / "src" / "pkg" / "a.py", "VALUE=1\n")
            write(repo / "config" / "release_identity.toml", identity)

            result = exporter.export_runtime(runtime, base / "out", "case")
            rows, metadata = auditor.audit_runtime(result.stage, repo, report)

            identity_rows = [
                row
                for row in rows
                if row.area == "config_app"
                and row.relative_path == "release_identity.toml"
            ]
            self.assertEqual(len(identity_rows), 1)
            self.assertEqual(identity_rows[0].status, "SAME")
            self.assertTrue(metadata["config_compared"])
            self.assertTrue(metadata["release_identity_compared"])

            report_text = (report / "RECONCILIATION_DIFF.json").read_text(
                encoding="utf-8"
            )
            self.assertNotIn(str(runtime.resolve()), report_text)
            self.assertNotIn(str(repo.resolve()), report_text)
            self.assertNotIn(str(result.stage.resolve()), report_text)


if __name__ == "__main__":
    unittest.main()
