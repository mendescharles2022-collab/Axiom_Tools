param(
    [Parameter(Mandatory = $true)]
    [string]$Root,

    [string]$OutputDir = "",

    [string]$Label = "runtime-reconciliation-v8"
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Assert-UnderRoot {
    param(
        [string]$Path,
        [string]$Base
    )

    $resolvedPath = [System.IO.Path]::GetFullPath($Path)
    $resolvedBase = [System.IO.Path]::GetFullPath($Base).TrimEnd('\') + '\'

    if (-not $resolvedPath.StartsWith($resolvedBase, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Caminho fora da raiz permitida: $resolvedPath"
    }
}

function Copy-IfExists {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$Base
    )

    if (-not (Test-Path -LiteralPath $Source)) {
        return $false
    }

    Assert-UnderRoot -Path $Source -Base $Base

    $parent = Split-Path -Parent $Destination
    if ($parent -and -not (Test-Path -LiteralPath $parent)) {
        New-Item -ItemType Directory -Path $parent -Force | Out-Null
    }

    if ((Get-Item -LiteralPath $Source).PSIsContainer) {
        Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
    }
    else {
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
    }

    return $true
}

function Remove-ForbiddenContent {
    param([string]$Stage)

    $forbiddenDirectoryNames = @(
        '.git', '.venv', 'venv', '__pycache__', '.pytest_cache',
        'data', 'database', 'databases', 'db', 'documentos', 'documents',
        'uploads', 'upload', 'logs', 'log', 'backups', 'backup', 'temp', 'tmp',
        'certificados', 'certificates', 'secrets', 'tokens', 'cache', 'caches'
    )

    Get-ChildItem -LiteralPath $Stage -Directory -Recurse -Force |
        Sort-Object FullName -Descending |
        Where-Object { $forbiddenDirectoryNames -contains $_.Name.ToLowerInvariant() } |
        ForEach-Object { Remove-Item -LiteralPath $_.FullName -Recurse -Force }

    $forbiddenExtensions = @(
        '.sqlite', '.sqlite3', '.db', '.mdb', '.accdb',
        '.pfx', '.p12', '.p7b', '.p7c', '.cer', '.crt', '.der',
        '.pem', '.key', '.jks', '.kdb', '.kdbx',
        '.zip', '.7z', '.rar'
    )

    Get-ChildItem -LiteralPath $Stage -File -Recurse -Force |
        Where-Object {
            ($forbiddenExtensions -contains $_.Extension.ToLowerInvariant()) -or
            ($_.Name -match '^\.env($|\.)') -or
            ($_.Name -match '(?i)(secret|token|credential|senha|password)')
        } |
        ForEach-Object { Remove-Item -LiteralPath $_.FullName -Force }
}

function Assert-NoForbiddenContent {
    param([string]$Stage)

    $violations = New-Object System.Collections.Generic.List[string]

    Get-ChildItem -LiteralPath $Stage -File -Recurse -Force | ForEach-Object {
        $relative = $_.FullName.Substring($Stage.Length).TrimStart('\')
        $lowerName = $_.Name.ToLowerInvariant()
        $ext = $_.Extension.ToLowerInvariant()

        if ($ext -in @('.sqlite', '.sqlite3', '.db', '.pfx', '.p12', '.pem', '.key')) {
            $violations.Add($relative)
        }

        if ($lowerName -match '^\.env($|\.)' -or $lowerName -match '(secret|token|credential|senha|password)') {
            $violations.Add($relative)
        }
    }

    if ($violations.Count -gt 0) {
        throw "Exportação bloqueada: conteúdo potencialmente sensível encontrado:`n$($violations -join "`n")"
    }
}

$resolvedRoot = (Resolve-Path -LiteralPath $Root).Path

if (-not $OutputDir) {
    $OutputDir = Join-Path $resolvedRoot 'temp'
}

if (-not (Test-Path -LiteralPath $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$stage = Join-Path $OutputDir "$Label-$timestamp"
$zipPath = "$stage.zip"

if (Test-Path -LiteralPath $stage) {
    throw "Diretório de staging já existe: $stage"
}

New-Item -ItemType Directory -Path $stage -Force | Out-Null

$copied = New-Object System.Collections.Generic.List[string]

# Whitelist deliberada. O script não faz espelhamento cego da raiz operacional.
$candidates = @(
    @{ Source = 'app\src'; Destination = 'app\src' },
    @{ Source = 'app\tests'; Destination = 'app\tests' },
    @{ Source = 'app\scripts'; Destination = 'app\scripts' },
    @{ Source = 'app\migrations'; Destination = 'app\migrations' },
    @{ Source = 'app\alembic'; Destination = 'app\alembic' },
    @{ Source = 'scripts'; Destination = 'scripts' },
    @{ Source = 'app\pyproject.toml'; Destination = 'app\pyproject.toml' },
    @{ Source = 'app\requirements.txt'; Destination = 'app\requirements.txt' },
    @{ Source = 'app\requirements-dev.txt'; Destination = 'app\requirements-dev.txt' },
    @{ Source = 'pyproject.toml'; Destination = 'pyproject.toml' },
    @{ Source = 'requirements.txt'; Destination = 'requirements.txt' }
)

foreach ($candidate in $candidates) {
    $source = Join-Path $resolvedRoot $candidate.Source
    $destination = Join-Path $stage $candidate.Destination

    if (Copy-IfExists -Source $source -Destination $destination -Base $resolvedRoot) {
        $copied.Add($candidate.Source)
    }
}

# Entrypoints Python conhecidos são copiados apenas da raiz/app, sem varrer dados arbitrários.
$entrypointRoots = @($resolvedRoot, (Join-Path $resolvedRoot 'app'))
foreach ($entryRoot in $entrypointRoots) {
    if (-not (Test-Path -LiteralPath $entryRoot)) {
        continue
    }

    Get-ChildItem -LiteralPath $entryRoot -File -Filter '*.py' -Force | ForEach-Object {
        $relativeBase = if ($entryRoot -eq $resolvedRoot) { '' } else { 'app' }
        $destinationDir = if ($relativeBase) { Join-Path $stage $relativeBase } else { $stage }
        if (-not (Test-Path -LiteralPath $destinationDir)) {
            New-Item -ItemType Directory -Path $destinationDir -Force | Out-Null
        }
        Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $destinationDir $_.Name) -Force
        $copied.Add((Join-Path $relativeBase $_.Name))
    }
}

Remove-ForbiddenContent -Stage $stage
Assert-NoForbiddenContent -Stage $stage

$manifestPath = Join-Path $stage 'RECONCILIATION_MANIFEST.csv'
$inventoryPath = Join-Path $stage 'RECONCILIATION_INFO.txt'

$files = Get-ChildItem -LiteralPath $stage -File -Recurse -Force |
    Where-Object { $_.FullName -ne $manifestPath -and $_.FullName -ne $inventoryPath } |
    Sort-Object FullName

$manifest = foreach ($file in $files) {
    [pscustomobject]@{
        RelativePath = $file.FullName.Substring($stage.Length).TrimStart('\')
        Length       = $file.Length
        SHA256       = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
        LastWriteUtc = $file.LastWriteTimeUtc.ToString('o')
    }
}

$manifest | Export-Csv -LiteralPath $manifestPath -NoTypeInformation -Encoding UTF8

$info = @(
    'Axiom Tools - exportação segura para reconciliação V8',
    "Gerado em: $((Get-Date).ToString('o'))",
    "Raiz lida: $resolvedRoot",
    "Staging: $stage",
    "Arquivos exportados: $($manifest.Count)",
    '',
    'Candidatos encontrados:',
    ($copied | Sort-Object -Unique | ForEach-Object { "- $_" }),
    '',
    'Proibições aplicadas:',
    '- sem banco SQLite/DB',
    '- sem documentos/uploads',
    '- sem certificados/chaves',
    '- sem .env/tokens/credenciais',
    '- sem logs/backups/temp/cache',
    '- sem .venv/__pycache__',
    '',
    'Este exportador não altera nem remove arquivos da raiz operacional.'
)
$info | Set-Content -LiteralPath $inventoryPath -Encoding UTF8

if (Test-Path -LiteralPath $zipPath) {
    Remove-Item -LiteralPath $zipPath -Force
}

Compress-Archive -LiteralPath (Join-Path $stage '*') -DestinationPath $zipPath -CompressionLevel Optimal

$zipHash = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash

Write-Host "EXPORT_V8_OK" -ForegroundColor Green
Write-Host "Stage: $stage"
Write-Host "ZIP:   $zipPath"
Write-Host "SHA256: $zipHash"
Write-Host "Arquivos: $($manifest.Count)"
Write-Host "A raiz operacional não foi modificada."
