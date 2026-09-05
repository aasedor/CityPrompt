param(
    [Parameter(Mandatory=$true)][string]$SourceRoot,
    [Parameter(Mandatory=$true)][string]$ParkPublicRoot,
    [Parameter(Mandatory=$true)][string]$OutputRoot,
    [string]$CandidateManifest,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$repoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$basePublic = (Resolve-Path -LiteralPath (Join-Path $SourceRoot 'frontend/public')).Path
$parkPublic = (Resolve-Path -LiteralPath $ParkPublicRoot).Path
$output = [IO.Path]::GetFullPath($OutputRoot)
foreach ($source in @($basePublic, $parkPublic)) {
    if ($output.TrimEnd('\','/') -eq $source.TrimEnd('\','/') -or
        $output.StartsWith($source.TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase) -or
        $source.StartsWith($output.TrimEnd('\','/') + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Output must be separate from both source trees.'
    }
}
$manifestPath = if ($CandidateManifest) { (Resolve-Path -LiteralPath $CandidateManifest).Path } else { Join-Path $PSScriptRoot '../neighborhood_park_pilot/candidate-manifest.json' }
$manifest = Get-Content -Raw -LiteralPath $manifestPath | ConvertFrom-Json
$files = [Collections.Generic.List[object]]::new()
$bundleDirectory = $null
foreach ($asset in $manifest.assets.PSObject.Properties.Value) {
    $relative = [string]$asset.url
    if ($relative -notmatch '^/landscape-pilots/neighborhood-rustic-v[0-9]+/[a-z0-9-]+\.glb$') {
        throw "Unexpected pilot asset URL: $relative"
    }
    $relative = $relative.TrimStart('/')
    $assetDirectory = $relative.Substring(0, $relative.LastIndexOf('/'))
    if ($bundleDirectory -and $bundleDirectory -ne $assetDirectory) { throw 'A prepared park bundle must use one exact revision directory.' }
    $bundleDirectory = $assetDirectory
    $source = Join-Path $parkPublic $relative
    if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing asset: $source" }
    $hash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
    if ((Get-Item -LiteralPath $source).Length -ne $asset.bytes -or $hash -ne $asset.sha256) {
        throw "Candidate manifest mismatch: $source"
    }
    $files.Add(@{ source=$source; relative=$relative; sha256=$hash; bytes=$asset.bytes })
}
if (-not $bundleDirectory) { throw 'Candidate manifest contains no park assets.' }
foreach ($name in @('manifest.json','FOLIAGE_LICENSE.txt')) {
    $relative = "$bundleDirectory/$name"
    $source = Join-Path $parkPublic $relative
    $hash = (Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($name -eq 'manifest.json') {
        # The tracked manifest may have different whitespace; compare its data.
        $supplied = Get-Content -Raw -LiteralPath $source | ConvertFrom-Json | ConvertTo-Json -Depth 30 -Compress
        $tracked = $manifest | ConvertTo-Json -Depth 30 -Compress
        if ($supplied -ne $tracked) { throw 'Supplied park manifest differs from the reviewed candidate manifest.' }
    }
    $files.Add(@{ source=$source; relative=$relative; sha256=$hash; bytes=(Get-Item -LiteralPath $source).Length })
}
# Validate every destination before writing anything. A rerun is idempotent;
# a differing file is evidence to reconcile, never permission to overwrite it.
foreach ($file in $files) {
    $destination = Join-Path $output $file.relative
    if ((Test-Path -LiteralPath $destination) -and
        (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $file.sha256) {
        throw "Existing output differs; select a new versioned output root: $destination"
    }
}
$baseEntries = @(Get-ChildItem -LiteralPath $basePublic | Where-Object { $_.Name -ne 'landscape-pilots' })
foreach ($entry in $baseEntries) {
    $destination = Join-Path $output $entry.Name
    if (-not (Test-Path -LiteralPath $destination)) { continue }
    $existing = Get-Item -LiteralPath $destination -Force
    if ($entry.PSIsContainer) {
        if ($existing.LinkType -ne 'Junction' -or [IO.Path]::GetFullPath([string]$existing.Target) -ne $entry.FullName) {
            throw "Existing directory is not the intended shared asset junction: $destination"
        }
    } elseif ((Get-FileHash -LiteralPath $destination).Hash -ne (Get-FileHash -LiteralPath $entry.FullName).Hash) {
        throw "Existing shared file differs: $destination"
    }
}
$report = [ordered]@{
    schema='cityprompt.local-catalogue-public@1'; status='verified-local-pilot-not-new-asset-approval'
    sourcePublic=$basePublic; outputPublic=$output
    copiedPilotFiles=@($files | ForEach-Object { @{ path=$_.relative; sha256=$_.sha256; bytes=$_.bytes } })
    sharedBaseEntries=@($baseEntries.Name)
}
if (-not $DryRun) {
    New-Item -ItemType Directory -Path $output -Force | Out-Null
    foreach ($entry in $baseEntries) {
        $destination = Join-Path $output $entry.Name
        if (Test-Path -LiteralPath $destination) { continue }
        if ($entry.PSIsContainer) { New-Item -ItemType Junction -Path $destination -Target $entry.FullName | Out-Null }
        else { Copy-Item -LiteralPath $entry.FullName -Destination $destination }
    }
    foreach ($file in $files) {
        $destination = Join-Path $output $file.relative
        if (Test-Path -LiteralPath $destination) { continue }
        New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
        Copy-Item -LiteralPath $file.source -Destination $destination
        if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant() -ne $file.sha256) { throw "Copied asset changed: $destination" }
    }
    $report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path (Split-Path -Parent $output) 'prepared-assets.json') -Encoding utf8
}
$report | ConvertTo-Json -Depth 8
