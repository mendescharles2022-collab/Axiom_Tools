from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "CONSUME_RUNTIME_HANDOFF_V8.ps1"
WORKFLOW = ROOT / ".github" / "workflows" / "reconciliation-tests.yml"


class RuntimeHandoffConsumerWindowsLauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = SCRIPT.read_text(encoding="utf-8")
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_launcher_requires_handoff_repo_and_output(self):
        for name in ("HandoffDir", "RepoRoot", "OutputDir"):
            self.assertRegex(
                self.text,
                rf"\[Parameter\(Mandatory = \$true\)\]\s*\[string\]\${name}",
            )

    def test_launcher_calls_canonical_consumer(self):
        self.assertIn("consume_runtime_reconciliation_handoff.py", self.text)
        self.assertIn('"--handoff-dir", $handoff', self.text)
        self.assertIn('"--repo-root", $repo', self.text)
        self.assertIn('"--output-dir", $output', self.text)
        self.assertIn('"--reconciliation-policy", $policyPath', self.text)

    def test_launcher_never_deletes_or_moves_handoff_or_repo(self):
        for token in ("Remove-Item", "Move-Item", "Clear-Content", "Set-Content"):
            self.assertNotIn(token, self.text)

    def test_launcher_blocks_output_inside_handoff_or_repo(self):
        self.assertIn("Test-IsInside -Child $output -Parent $handoff", self.text)
        self.assertIn("Test-IsInside -Child $output -Parent $repo", self.text)
        self.assertIn("OutputDir deve ficar fora do handoff", self.text)
        self.assertIn("OutputDir deve ficar fora do repositório", self.text)

    def test_launcher_never_overwrites_existing_output(self):
        self.assertIn("Test-Path -LiteralPath $output", self.text)
        self.assertIn("não será sobrescrito", self.text)

    def test_launcher_supports_windows_powershell_without_iswindows_variable(self):
        self.assertNotIn("$IsWindows", self.text)
        self.assertIn("DirectorySeparatorChar -eq [char]92", self.text)
        self.assertIn('.venv\\Scripts\\python.exe', self.text)
        self.assertIn('"py.exe"', self.text)
        self.assertIn('"python.exe"', self.text)
        self.assertIn("Get-Command $commandName", self.text)

    def test_launcher_validates_plan_non_homologation_and_immutability(self):
        self.assertIn("handoff_unchanged", self.text)
        self.assertIn("internal_manifest_ok", self.text)
        self.assertIn("ready_for_reconciliation_review", self.text)
        self.assertIn("RECONCILIATION_PLAN.json", self.text)
        self.assertIn("automatic_reconciliation_write", self.text)
        self.assertIn("automatic_write_allowed", self.text)
        self.assertIn("reconciliation_plan_sha256", self.text)
        self.assertIn("plan.plan_sha256", self.text)
        self.assertIn("v8_homologated", self.text)
        self.assertIn('Write-Host "Escrita automática: NÃO"', self.text)
        self.assertIn('Write-Host "V8 homologada: NÃO"', self.text)

    def test_launcher_does_not_hardcode_server_drive(self):
        self.assertIsNone(
            re.search(r"(?i)\b[A-Z]:\\(?:Programas|Axiom|Users|ProgramData)\\", self.text)
        )

    def test_ci_executes_consumer_and_plan_powershell_smoke(self):
        self.assertIn("Smoke PowerShell B06 producer consumer and plan", self.workflow)
        self.assertIn("./scripts/BUILD_RUNTIME_HANDOFF_V8.ps1", self.workflow)
        self.assertIn("./scripts/CONSUME_RUNTIME_HANDOFF_V8.ps1", self.workflow)
        self.assertIn("POWERSHELL_B06_SMOKE_OK", self.workflow)
        self.assertIn("POWERSHELL_B06_CONSUMER_SMOKE_OK", self.workflow)
        self.assertIn("POWERSHELL_B06_PLAN_SMOKE_OK", self.workflow)
        self.assertIn("database_preflight_ok", self.workflow)
        self.assertIn("automatic_write_allowed", self.workflow)


if __name__ == "__main__":
    unittest.main()
