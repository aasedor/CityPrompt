param(
    [Parameter(Mandatory=$true)][string]$PreparedPublicRoot,
    [Parameter(Mandatory=$true)][string]$SourceRoot,
    [int]$Port = 5174,
    [string]$ApiTarget = 'http://127.0.0.1:8002'
)
$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$publicRoot = (Resolve-Path -LiteralPath $PreparedPublicRoot).Path
$report = Get-Content -Raw -LiteralPath (Join-Path (Split-Path -Parent $publicRoot) 'prepared-assets.json') | ConvertFrom-Json
if ($report.schema -ne 'cityprompt.local-catalogue-public@1' -or [IO.Path]::GetFullPath($report.outputPublic) -ne $publicRoot) {
    throw 'Prepare this explicit public root with prepare_public.ps1 first.'
}
foreach ($file in $report.copiedPilotFiles) {
    if ((Get-FileHash -LiteralPath (Join-Path $publicRoot $file.path) -Algorithm SHA256).Hash.ToLowerInvariant() -ne $file.sha256) {
        throw "Prepared runtime asset changed: $($file.path)"
    }
}
$env:CITYPROMPT_PUBLIC_DIR = $publicRoot
$env:VITE_ENV_DIR = (Resolve-Path -LiteralPath (Join-Path $SourceRoot 'frontend')).Path
$env:API_PROXY_TARGET = $ApiTarget
Push-Location (Join-Path $repoRoot 'frontend')
try { & npm.cmd run dev -- --host 127.0.0.1 --port $Port --strictPort }
finally { Pop-Location }
