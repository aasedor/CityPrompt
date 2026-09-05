param(
    [Parameter(Mandatory=$true)][string]$SourceRoot,
    [int]$Port = 5174,
    [string]$ApiTarget = 'http://127.0.0.1:8001'
)
$ErrorActionPreference = 'Stop'
$pilotRepo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$sourceRepo = (Resolve-Path -LiteralPath $SourceRoot).Path
$pilotPublic = Join-Path $pilotRepo 'artifacts/park-pilot/public'
$trackedManifest = Get-Content -Raw -LiteralPath (Join-Path $PSScriptRoot 'candidate-manifest.json') | ConvertFrom-Json
$candidateDirectory = ([string]$trackedManifest.assets.pavilion.url).TrimStart('/') -replace '/[^/]+$', ''
$candidateManifest = Join-Path $pilotPublic "$candidateDirectory/manifest.json"
if (-not (Test-Path -LiteralPath $candidateManifest)) {
    throw 'Build the nine candidate assets first; see docs/NEIGHBOURHOOD_PARK_PILOT_2026-09-05.md.'
}
# Reuse hydrated public assets. Never replace or delete existing destinations.
Get-ChildItem -LiteralPath (Join-Path $sourceRepo 'frontend/public') | ForEach-Object {
    $destination = Join-Path $pilotPublic $_.Name
    if (-not (Test-Path -LiteralPath $destination)) {
        if ($_.PSIsContainer) { New-Item -ItemType Junction -Path $destination -Target $_.FullName | Out-Null }
        else { Copy-Item -LiteralPath $_.FullName -Destination $destination }
    }
}
$pilotModules = Join-Path $pilotRepo 'frontend/node_modules'
if (-not (Test-Path -LiteralPath $pilotModules)) {
    New-Item -ItemType Junction -Path $pilotModules -Target (Join-Path $sourceRepo 'frontend/node_modules') | Out-Null
}
$env:CITYPROMPT_PUBLIC_DIR = $pilotPublic
$env:VITE_ENV_DIR = Join-Path $sourceRepo 'frontend'
$env:API_PROXY_TARGET = $ApiTarget
Push-Location (Join-Path $pilotRepo 'frontend')
try { & npm.cmd run dev -- --host 127.0.0.1 --port $Port --strictPort }
finally { Pop-Location }
