param(
    [Parameter(Mandatory = $true)]
    [string]$Root,

    [string]$OutputDir = "",

    [string]$Label = "runtime-reconciliation-v8",

    [string]$PythonExe = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$engine = Join-Path $PSScriptRoot "export_runtime_reconciliation.py"
if (-not (Test-Path -LiteralPath $engine -PathType Leaf)) {
    throw "Motor Python de exportação não encontrado: $engine"
}

if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
    throw "Raiz operacional inválida: $Root"
}

if (-not $PythonExe) {
    $candidates = @(
        (Join-Path $Root ".venv\Scripts\python.exe"),
        (Join-Path $Root "app\.venv\Scripts\python.exe")
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            $PythonExe = $candidate
            break
        }
    }
}

if (-not $PythonExe) {
    $pythonCommand = Get-Command python.exe -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    }
    if ($pythonCommand) {
        $PythonExe = $pythonCommand.Source
    }
}

if (-not $PythonExe -or -not (Test-Path -LiteralPath $PythonExe -PathType Leaf)) {
    throw "Python não encontrado. Informe -PythonExe com o caminho do python.exe usado pelo Axiom Tools."
}

$engineArgs = @(
    $engine,
    "--root", $Root,
    "--label", $Label
)

if ($OutputDir) {
    $engineArgs += @("--output-dir", $OutputDir)
}

Write-Host "Iniciando exportação segura para reconciliação V8..."
Write-Host "Python: $PythonExe"
Write-Host "Raiz:   $Root"

& $PythonExe @engineArgs
$exitCode = $LASTEXITCODE

if ($exitCode -ne 0) {
    throw "Exportação V8 falhou com código $exitCode. Nenhum pacote deve ser usado para reconciliação."
}

Write-Host "Launcher Windows concluído com sucesso." -ForegroundColor Green
