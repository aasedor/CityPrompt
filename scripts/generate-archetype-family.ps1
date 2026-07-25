<#
.SYNOPSIS
  Generate a modular LEGO building family from a real SiteForge archetype - one command.

.EXAMPLE
  .\scripts\generate-archetype-family.ps1 -ArchetypeId "nordic_timber_midrise"

.EXAMPLE
  .\scripts\generate-archetype-family.ps1 -ArchetypeId "nordic_timber_midrise" -VariantId "nordic_timber_charred_wood" -Floors 6

.EXAMPLE
  .\scripts\generate-archetype-family.ps1 -List
#>
param(
    [string]$ArchetypeId,
    [string]$VariantId,
    [int]$Floors,
    [double]$Width,
    [double]$Depth,
    [string]$Output,
    [string]$BlenderPath,
    [switch]$SkipThumbnail,
    [switch]$KeepBlend,
    [switch]$List,
    [switch]$Verbose2
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Frontend = Join-Path $RepoRoot "frontend"
$Tool = Join-Path $RepoRoot "tools\archetype_compiler"

function Fail($msg) {
    Write-Host ""
    Write-Host "  FAILED: $msg" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== SiteForge Archetype Family Generator ===" -ForegroundColor Cyan

# --- 1. verify Python -------------------------------------------------------
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { Fail "Python not found. Install Python 3.11+ from https://www.python.org/downloads/ (check 'Add to PATH')." }
$pyVersion = & python --version
Write-Host "  python : $pyVersion"

# --- 2. verify Node / npm ---------------------------------------------------
$node = Get-Command node -ErrorAction SilentlyContinue
$npm = Get-Command npm -ErrorAction SilentlyContinue
if (-not $node -or -not $npm) { Fail "Node.js/npm not found. Install Node 18+ from https://nodejs.org/." }
Write-Host "  node   : $(& node --version)"

# --- 3. frontend dependencies (the exporter runs through vite-node) ---------
if (-not (Test-Path (Join-Path $Frontend "node_modules\.bin"))) {
    Write-Host "  installing frontend dependencies (first run only, a few minutes)..." -ForegroundColor Yellow
    Push-Location $Frontend
    npm install
    if ($LASTEXITCODE -ne 0) { Pop-Location; Fail "npm install failed in $Frontend" }
    Pop-Location
}
Write-Host "  frontend deps: ok"

# --- list mode ---------------------------------------------------------------
if ($List) {
    Push-Location $Frontend
    npx vite-node (Join-Path $Tool "export_catalog.ts") -- --list
    Pop-Location
    exit $LASTEXITCODE
}

if (-not $ArchetypeId) {
    Write-Host ""
    Write-Host "  Usage: .\scripts\generate-archetype-family.ps1 -ArchetypeId `"nordic_timber_midrise`"" -ForegroundColor Yellow
    Write-Host "  Use -List to see all 223 available archetype ids."
    exit 2
}

# --- 4. locate Blender early so the error is friendly ------------------------
$locateArgs = @()
if ($BlenderPath) { $locateArgs += $BlenderPath }
$blender = & python (Join-Path $Tool "blender_locator.py") @locateArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host $blender
    Fail "Blender could not be located (see instructions above)."
}
Write-Host "  blender: $blender"

# --- 5. run the orchestrator --------------------------------------------------
$args2 = @("--archetype-id", $ArchetypeId)
if ($VariantId) { $args2 += @("--variant-id", $VariantId) }
if ($Floors) { $args2 += @("--floors", $Floors) }
if ($Width) { $args2 += @("--width", $Width) }
if ($Depth) { $args2 += @("--depth", $Depth) }
if ($Output) { $args2 += @("--output", $Output) }
if ($BlenderPath) { $args2 += @("--blender-path", $BlenderPath) }
if ($SkipThumbnail) { $args2 += "--skip-thumbnail" }
if ($KeepBlend) { $args2 += "--keep-blend" }
if ($Verbose2) { $args2 += "--verbose" }

Write-Host ""
& python (Join-Path $Tool "generate_family.py") @args2
$code = $LASTEXITCODE

Write-Host ""
if ($code -eq 0) {
    Write-Host "=== SUCCESS - open the *_preview.png / *_assembled.glb in the folder above ===" -ForegroundColor Green
} else {
    Write-Host "=== FAILED (exit $code) - read the error above; logs are in <output>\logs\ ===" -ForegroundColor Red
}
exit $code
