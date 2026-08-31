param(
    [Parameter(Mandatory = $true)]
    [string]$RuntimeRoot,

    [Parameter(Mandatory = $true)]
    [string]$Database,

    [Parameter(Mandatory = $true)]
    [string]$OutputDir,

    [string]$Label = "axiom-tools-runtime-v8",

    [string]$PythonExe = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-FullPathSafe {
    param([Parameter(Mandatory = $true)][string]$Path)
    return [System.IO.Path]::GetFullPath($Path)
}

function Test-IsInside {
    param(
        [Parameter(Mandatory = $true)][string]$Child,
        [Parameter(Mandatory = $true)][string]$Parent
    )

    $childFull = (Get-FullPathSafe $Child).TrimEnd('\', '/')
    $parentFull = (Get-FullPathSafe $Parent).TrimEnd('\', '/')
    if ($childFull.Equals($parentFull, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $true
    }

    $prefix = $parentFull + [System.IO.Path]::DirectorySeparatorChar
    return $childFull.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)
}

function Resolve-PythonCommand {
    param(
        [string]$ExplicitPython,
        [string]$Runtime,
        [string]$ToolRoot
    )

    if ($ExplicitPython) {
        $explicit = Get-FullPathSafe $ExplicitPython
        if (-not (Test-Path -LiteralPath $explicit -PathType Leaf)) {
            throw "Python informado não existe: $explicit"
        }
        return [pscustomobject]@{ Exe = $explicit; Prefix = @() }
    }

    $candidates = @(
        (Join-Path $Runtime ".venv\Scripts\python.exe"),
        (Join-Path $Runtime "venv\Scripts\python.exe"),
        (Join-Path $ToolRoot ".venv\Scripts\python.exe"),
        (Join-Path $ToolRoot "venv\Scripts\python.exe")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return [pscustomobject]@{ Exe = (Get-FullPathSafe $candidate); Prefix = @() }
        }
    }

    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($py) {
        return [pscustomobject]@{ Exe = $py.Source; Prefix = @("-3") }
    }

    $python = Get-Command python.exe -ErrorAction SilentlyContinue
    if ($python) {
        return [pscustomobject]@{ Exe = $python.Source; Prefix = @() }
    }

    throw "Python não localizado. Informe -PythonExe ou disponibilize .venv/venv/py.exe/python.exe."
}

$toolRoot = Get-FullPathSafe (Join-Path $PSScriptRoot "..")
$pythonScript = Join-Path $PSScriptRoot "build_runtime_reconciliation_handoff.py"
$runtime = Get-FullPathSafe $RuntimeRoot
$databasePath = Get-FullPathSafe $Database
$output = Get-FullPathSafe $OutputDir

if (-not (Test-Path -LiteralPath $pythonScript -PathType Leaf)) {
    throw "Tooling B06 não encontrado: $pythonScript"
}
if (-not (Test-Path -LiteralPath $runtime -PathType Container)) {
    throw "RuntimeRoot não existe: $runtime"
}
if (-not (Test-Path -LiteralPath $databasePath -PathType Leaf)) {
    throw "Banco SQLite não existe: $databasePath"
}
if (Test-IsInside -Child $output -Parent $runtime) {
    throw "OutputDir deve ficar fora da árvore operacional do runtime."
}
if (Test-IsInside -Child $databasePath -Parent $output) {
    throw "O banco de origem não pode ficar dentro do OutputDir."
}
if ($Label -notmatch '^[A-Za-z0-9._-]+$') {
    throw "Label inválido. Use apenas letras, números, ponto, sublinhado ou hífen."
}

New-Item -ItemType Directory -Force -Path $output | Out-Null
$python = Resolve-PythonCommand -ExplicitPython $PythonExe -Runtime $runtime -ToolRoot $toolRoot

Write-Host "Axiom Tools V8 - Handoff de reconciliação B06"
Write-Host "Origem operacional será somente lida."
Write-Host "Banco será clonado para artefato separado; não entra no ZIP de código."

$arguments = @()
$arguments += $python.Prefix
$arguments += @(
    $pythonScript,
    "--runtime-root", $runtime,
    "--database", $databasePath,
    "--output-dir", $output,
    "--label", $Label
)

& $python.Exe @arguments
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    throw "Handoff B06 falhou com código $exitCode. Nenhuma homologação foi concedida."
}

$handoffDir = Join-Path $output ($Label + "-handoff")
$manifestPath = Join-Path $handoffDir "RUNTIME_HANDOFF_MANIFEST.json"
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Handoff terminou sem manifesto esperado: $manifestPath"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
if ($manifest.mode -ne "RUNTIME_RECONCILIATION_HANDOFF_NOT_HOMOLOGATION") {
    throw "Manifesto retornou modo inesperado: $($manifest.mode)"
}
if ($manifest.source.source_mutation_performed -ne $false) {
    throw "Manifesto não comprovou origem intacta. Interrompa a reconciliação."
}
if ($manifest.code_export.database_in_code_zip -ne $false) {
    throw "Manifesto indica banco dentro do ZIP de código. Interrompa a reconciliação."
}
if ($manifest.database_copy.kept_separate_from_code_zip -ne $true) {
    throw "Manifesto não comprovou separação código/banco. Interrompa a reconciliação."
}

Write-Host ""
Write-Host "RUNTIME_HANDOFF_WINDOWS_OK"
Write-Host ("Diretório do handoff: " + $handoffDir)
Write-Host ("ZIP de código/config: " + $manifest.code_export.zip)
Write-Host ("SQLite separado: " + $manifest.database_copy.file)
Write-Host ("Manifesto SHA-256: " + $manifest.manifest_sha256)
Write-Host "Origem alterada: NÃO"
Write-Host "V8 homologada: NÃO"
Write-Host "Próximo gate: reconciliar estes artefatos com o repositório e executar os preflights reais."
