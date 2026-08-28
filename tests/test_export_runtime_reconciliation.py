from __future__ import annotations

import csv
import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_runtime_reconciliation.py"
spec = importlib.util.spec_from_file_location("export_runtime_reconciliation", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class RuntimeExporterTests(unittest.TestCase):
    def test_export_copies_whitelist_and_excludes_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "runtime"
            out = base / "out"
            write(root / "app" / "src" / "pkg" / "a.py", "x=1\n")
            write(root / "app" / "tests" / "test_a.py", "ok=True\n")
            write(root / "database" / "prod.sqlite3", "db")
            write(root / "documentos" / "cliente.pdf", "pdf")

            result = module.export_runtime(root, out, "case")
            self.assertTrue((result.stage / "app/src/pkg/a.py").exists())
            self.assertTrue((result.stage / "app/tests/test_a.py").exists())
            self.assertFalse((result.stage / "database").exists())
            self.assertFalse((result.stage / "documentos").exists())
            self.assertTrue(result.zip_path.exists())

    def test_export_manifest_covers_payload_exactly(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "runtime"
            out = base / "out"
            write(root / "app" / "src" / "pkg" / "a.py", "x=1\n")
            write(root / "app" / "pyproject.toml", "[project]\nname='x'\n")

            result = module.export_runtime(root, out, "case")
            manifest = result.stage / module.MANIFEST_NAME
            with manifest.open("r", encoding="utf-8", newline="") as f:
                rows = list(csv.DictReader(f))
            listed = {row["RelativePath"] for row in rows}
            actual = {
                path.relative_to(result.stage).as_posix()
                for path in result.stage.rglob("*")
                if path.is_file() and path.name not in {module.MANIFEST_NAME, module.INFO_NAME}
            }
            self.assertEqual(listed, actual)
            self.assertEqual(result.file_count, len(actual))

    def test_export_blocks_hardcoded_secret_and_cleans_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "runtime"
            out = base / "out"
            write(root / "app" / "src" / "pkg" / "a.py", 'api_key = "REAL_SECRET_123456"\n')

            with self.assertRaises(module.ExportError):
                module.export_runtime(root, out, "case")
            self.assertEqual(list(out.glob("case-*")), [])

    def test_export_rejects_unsafe_label(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "runtime"
            write(root / "app" / "src" / "a.py", "x=1\n")
            with self.assertRaises(module.ExportError):
                module.export_runtime(root, Path(tmp) / "out", "../escape")

    def test_export_zip_contains_manifest_and_info(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "runtime"
            write(root / "app" / "src" / "a.py", "x=1\n")
            result = module.export_runtime(root, base / "out", "case")
            with zipfile.ZipFile(result.zip_path) as zf:
                names = set(zf.namelist())
            self.assertIn(module.MANIFEST_NAME, names)
            self.assertIn(module.INFO_NAME, names)
            self.assertIn("app/src/a.py", names)

    def test_export_rejects_symlink_in_whitelisted_tree(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "runtime"
            write(root / "app" / "src" / "a.py", "x=1\n")
            outside = base / "outside.py"
            write(outside, "x=2\n")
            link = root / "app" / "src" / "link.py"
            try:
                link.symlink_to(outside)
            except (OSError, NotImplementedError):
                self.skipTest("Ambiente não permite criação de symlink")
            with self.assertRaises(module.ExportError):
                module.export_runtime(root, base / "out", "case")


if __name__ == "__main__":
    unittest.main()
