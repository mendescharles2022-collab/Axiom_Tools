from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "BUILD_RUNTIME_HANDOFF_V8.ps1"


class RuntimeHandoffWindowsLauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SCRIPT.read_text(encoding="utf-8")

    def test_launcher_requires_runtime_database_and_output(self):
        self.assertRegex(cls_text := self.text, r"\[Parameter\(Mandatory = \$true\)\]\s*\[string\]\$RuntimeRoot")
        self.assertRegex(cls_text, r"\[Parameter\(Mandatory = \$true\)\]\s*\[string\]\$Database")
        self.assertRegex(cls_text, r"\[Parameter\(Mandatory = \$true\)\]\s*\[string\]\$OutputDir")

    def test_launcher_calls_canonical_python_handoff(self):
        self.assertIn('build_runtime_reconciliation_handoff.py', self.text)
        self.assertIn('"--runtime-root", $runtime', self.text)
        self.assertIn('"--database", $databasePath', self.text)
        self.assertIn('"--output-dir", $output', self.text)

    def test_launcher_does_not_hardcode_server_drive(self):
        self.assertIsNone(re.search(r"(?i)\b[A-Z]:\\(?:Programas|Axiom|Users|ProgramData)\\", self.text))

    def test_launcher_never_deletes_or_moves_operational_files(self):
        forbidden = ["Remove-Item", "Move-Item", "Clear-Content", "Set-Content"]
        for token in forbidden:
            self.assertNotIn(token, self.text)

    def test_launcher_validates_output_outside_runtime(self):
        self.assertIn("Test-IsInside -Child $output -Parent $runtime", self.text)
        self.assertIn("OutputDir deve ficar fora da árvore operacional", self.text)

    def test_launcher_validates_manifest_safety_flags(self):
        self.assertIn("RUNTIME_RECONCILIATION_HANDOFF_NOT_HOMOLOGATION", self.text)
        self.assertIn("source.source_mutation_performed", self.text)
        self.assertIn("code_export.database_in_code_zip", self.text)
        self.assertIn("database_copy.kept_separate_from_code_zip", self.text)
        self.assertIn('Write-Host "V8 homologada: NÃO"', self.text)

    def test_launcher_supports_venv_py_and_python_resolution(self):
        self.assertIn('.venv\\Scripts\\python.exe', self.text)
        self.assertIn('venv\\Scripts\\python.exe', self.text)
        self.assertIn('Get-Command py.exe', self.text)
        self.assertIn('Get-Command python.exe', self.text)
        self.assertIn('[string]$PythonExe', self.text)


if __name__ == "__main__":
    unittest.main()
