param(
    [Parameter(Mandatory = $true)]
    [string]$HandoffDir,

    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,

    [Parameter(Mandatory = $true)]
    [string]$OutputDir,

    [string]$Invariants = "",
    [string]$ReconciliationPolicy = "",
    [string]$PythonExe = "",
    [switch]$SkipRowCounts,
    [switch]$FailOnDiff,
    [switch]$RequireDbOk
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Resolve-FullPath([string]$PathValue) {
    return [System.IO.Path]::GetFullPath($PathValue)
}

function Test-IsInside([string]$Child, [string]$Parent) {
    $childPath = (Resolve-FullPath $Child).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $parentPath = (Resolve-FullPath $Parent).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    $isWindowsPath = [System.IO.Path]::DirectorySeparatorChar -eq [char]92
    $comparison = if ($isWindowsPath) { [System.StringComparison]::OrdinalIgnoreCase } else { [System.StringComparison]::Ordinal }
    if ($childPath.Equals($parentPath, $comparison)) { return $true }
    return $childPath.StartsWith($parentPath + [System.IO.Path]::DirectorySeparatorChar, $comparison)
}

function Resolve-Python([string]$Explicit, [string]$RepositoryRoot) {
    if ($Explicit) {
        $candidate = Resolve-FullPath $Explicit
        if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            throw "PythonExe não encontrado: $candidate"
        }
        return $candidate
    }

    foreach ($relative in @(".venv\Scripts\python.exe", "venv\Scripts\python.exe")) {
        $candidate = Join-Path $RepositoryRoot $relative
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return (Resolve-FullPath $candidate)
        }
    }

    foreach ($commandName in @("py.exe", "python.exe", "python", "py")) {
        $command = Get-Command $commandName -ErrorAction SilentlyContinue
        if ($command) { return $command.Source }
    }
    throw "Python não encontrado. Informe -PythonExe explicitamente."
}

$handoff = Resolve-FullPath $HandoffDir
$repo = Resolve-FullPath $RepoRoot
$output = Resolve-FullPath $OutputDir

if (-not (Test-Path -LiteralPath $handoff -PathType Container)) {
    throw "HandoffDir inválido: $handoff"
}
if (-not (Test-Path -LiteralPath $repo -PathType Container)) {
    throw "RepoRoot inválido: $repo"
}
if (Test-IsInside -Child $output -Parent $handoff) {
    throw "OutputDir deve ficar fora do handoff."
}
if (Test-IsInside -Child $output -Parent $repo) {
    throw "OutputDir deve ficar fora do repositório."
}
if (Test-Path -LiteralPath $output) {
    throw "OutputDir já existe e não será sobrescrito: $output"
}

$python = Resolve-Python -Explicit $PythonExe -RepositoryRoot $repo
$consumer = Join-Path $PSScriptRoot "consume_runtime_reconciliation_handoff.py"
if (-not (Test-Path -LiteralPath $consumer -PathType Leaf)) {
    throw "Consumidor canônico não encontrado: $consumer"
}

$arguments = @(
    $consumer,
    "--handoff-dir", $handoff,
    "--repo-root", $repo,
    "--output-dir", $output
)

if ($Invariants) {
    $invariantPath = Resolve-FullPath $Invariants
    if (-not (Test-Path -LiteralPath $invariantPath -PathType Leaf)) {
        throw "Arquivo de invariantes não encontrado: $invariantPath"
    }
    $arguments += @("--invariants", $invariantPath)
}
if ($ReconciliationPolicy) {
    $policyPath = Resolve-FullPath $ReconciliationPolicy
    if (-not (Test-Path -LiteralPath $policyPath -PathType Leaf)) {
        throw "Política de reconciliação não encontrada: $policyPath"
    }
    $arguments += @("--reconciliation-policy", $policyPath)
}
if ($SkipRowCounts) { $arguments += "--skip-row-counts" }
if ($FailOnDiff) { $arguments += "--fail-on-diff" }
if ($RequireDbOk) { $arguments += "--require-db-ok" }

Write-Host "Axiom Tools V8 - Consumo seguro do handoff B06"
Write-Host "O handoff e o repositório serão somente lidos; resultados irão para staging separado."
& $python @arguments
if ($LASTEXITCODE -ne 0) {
    throw "Consumidor B06 retornou código $LASTEXITCODE."
}

$reportPath = Join-Path $output "RUNTIME_HANDOFF_CONSUMPTION.json"
$planPath = Join-Path $output "RECONCILIATION_PLAN.json"
if (-not (Test-Path -LiteralPath $reportPath -PathType Leaf)) {
    throw "Relatório final de consumo não foi gerado."
}
if (-not (Test-Path -LiteralPath $planPath -PathType Leaf)) {
    throw "Plano de reconciliação não foi gerado."
}
$report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json
$plan = Get-Content -LiteralPath $planPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($report.handoff_unchanged -ne $true) {
    throw "Relatório não comprova handoff intacto."
}
if ($report.internal_manifest_ok -ne $true) {
    throw "Relatório não comprova manifesto interno válido."
}
if ($report.ready_for_reconciliation_review -ne $true) {
    throw "Relatório não liberou revisão de reconciliação."
}
if ($report.automatic_reconciliation_write -ne $false) {
    throw "Consumidor não pode permitir escrita automática de reconciliação."
}
if ($plan.automatic_write_allowed -ne $false) {
    throw "Plano de reconciliação não pode permitir escrita automática."
}
if ($report.reconciliation_plan_sha256 -ne $plan.plan_sha256) {
    throw "Hash do plano diverge do relatório de consumo."
}
if ($report.v8_homologated -ne $false -or $plan.v8_homologated -ne $false) {
    throw "Consumidor/plano não podem marcar V8 como homologada."
}

Write-Host "RUNTIME_HANDOFF_CONSUMER_WINDOWS_OK"
Write-Host "Handoff intacto: SIM"
Write-Host "Plano: $([System.IO.Path]::GetFileName($planPath))"
Write-Host "Revisão obrigatória: $($report.reconciliation_review_required)"
Write-Host "Escrita automática: NÃO"
Write-Host "Relatório: $([System.IO.Path]::GetFileName($reportPath))"
Write-Host "V8 homologada: NÃO"
