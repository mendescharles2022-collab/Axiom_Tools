from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "BUILD_RUNTIME_HANDOFF_V8.ps1"
WORKFLOW = ROOT / ".github" / "workflows" / "reconciliation-tests.yml"


class RuntimeHandoffWindowsLauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SCRIPT.read_text(encoding="utf-8")
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_launcher_requires_runtime_and_output_but_database_is_optional(self):
        text = self.text
        self.assertRegex(text, r"\[Parameter\(Mandatory = \$true\)\]\s*\[string\]\$RuntimeRoot")
        self.assertRegex(text, r"\[Parameter\(Mandatory = \$true\)\]\s*\[string\]\$OutputDir")
        self.assertRegex(text, r"\[string\]\$Database = \"\"")
        self.assertNotRegex(text, r"\[Parameter\(Mandatory = \$true\)\]\s*\[string\]\$Database")

    def test_launcher_calls_canonical_python_handoff(self):
        self.assertIn("build_runtime_reconciliation_handoff.py", self.text)
        self.assertIn('"--runtime-root", $runtime', self.text)
        self.assertIn('"--output-dir", $output', self.text)
        self.assertIn('$arguments += @("--database", $databasePath)', self.text)

    def test_database_argument_is_only_added_when_explicit(self):
        self.assertIn("if ($databasePath) {", self.text)
        self.assertIn('$arguments += @("--database", $databasePath)', self.text)
        self.assertIn("autodiscovery conservadora", self.text)
        self.assertIn("exatamente um SQLite válido", self.text)

    def test_launcher_does_not_hardcode_server_drive(self):
        self.assertIsNone(re.search(r"(?i)\b[A-Z]:\\(?:Programas|Axiom|Users|ProgramData)\\", self.text))

    def test_launcher_never_deletes_or_moves_operational_files(self):
        forbidden = ["Remove-Item", "Move-Item", "Clear-Content", "Set-Content"]
        for token in forbidden:
            self.assertNotIn(token, self.text)

    def test_launcher_validates_output_outside_runtime(self):
        self.assertIn("Test-IsInside -Child $output -Parent $runtime", self.text)
        self.assertIn("OutputDir deve ficar fora da árvore operacional", self.text)

    def test_explicit_database_still_validates_location(self):
        self.assertIn("$databasePath -and -not (Test-Path", self.text)
        self.assertIn("$databasePath -and (Test-IsInside -Child $databasePath -Parent $output)", self.text)

    def test_launcher_validates_manifest_safety_flags(self):
        self.assertIn("RUNTIME_RECONCILIATION_HANDOFF_NOT_HOMOLOGATION", self.text)
        self.assertIn("source.source_mutation_performed", self.text)
        self.assertIn("code_export.database_in_code_zip", self.text)
        self.assertIn("database_copy.kept_separate_from_code_zip", self.text)
        self.assertIn("source.database_selection", self.text)
        self.assertIn('Write-Host "V8 homologada: NÃO"', self.text)

    def test_launcher_supports_venv_py_and_python_resolution(self):
        self.assertIn('.venv\\Scripts\\python.exe', self.text)
        self.assertIn('venv\\Scripts\\python.exe', self.text)
        self.assertIn("Get-Command py.exe", self.text)
        self.assertIn("Get-Command python.exe", self.text)
        self.assertIn("[string]$PythonExe", self.text)

    def test_ci_triggers_when_powershell_launcher_changes(self):
        self.assertGreaterEqual(self.workflow.count('- "scripts/*.ps1"'), 2)

    def test_ci_executes_real_powershell_launcher_smoke(self):
        self.assertIn("Smoke PowerShell B06 launcher", self.workflow)
        self.assertIn("shell: pwsh", self.workflow)
        self.assertIn("./scripts/BUILD_RUNTIME_HANDOFF_V8.ps1", self.workflow)
        self.assertIn("POWERSHELL_B06_SMOKE_OK", self.workflow)
        self.assertIn("AUTO_DISCOVERED_SINGLE", self.workflow)


if __name__ == "__main__":
    unittest.main()
