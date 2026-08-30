<#
.SYNOPSIS
Copies directories into a SHA-256-addressed artifact store and optionally
removes the verified source copy.

.DESCRIPTION
Every payload file is hashed before copy and rehashed at the destination. The
source is removed only when -RemoveSource is supplied and the complete
destination verification succeeds. Existing matching objects are verified and
reused. The command never follows a source outside -AllowedSourceRoot.
#>
[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [Parameter(Mandatory = $true)]
    [string] $AllowedSourceRoot,

    [Parameter(Mandatory = $true)]
    [string[]] $SourcePath,

    [Parameter(Mandatory = $true)]
    [string] $StoreRoot,

    [switch] $RemoveSource
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-ResolvedDirectory([string] $Path) {
    $resolved = (Resolve-Path -LiteralPath $Path).Path
    if (-not (Test-Path -LiteralPath $resolved -PathType Container)) {
        throw "Not a directory: $resolved"
    }
    return [System.IO.Path]::GetFullPath($resolved)
}

function Get-FileRecords([string] $Root) {
    $records = @(
        Get-ChildItem -LiteralPath $Root -Recurse -File -Force |
            ForEach-Object {
                [pscustomobject]@{
                    path = [System.IO.Path]::GetRelativePath($Root, $_.FullName).Replace('\', '/')
                    bytes = [int64]$_.Length
                    sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
                }
            } |
            Sort-Object path
    )
    return $records
}

function Get-RecordsDigest([object[]] $Records) {
    $canonical = $Records | ConvertTo-Json -Depth 5 -Compress
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($canonical)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $sha.Dispose()
    }
}

function Assert-MatchingRecords([object[]] $Expected, [object[]] $Actual, [string] $Label) {
    $expectedJson = $Expected | ConvertTo-Json -Depth 5 -Compress
    $actualJson = $Actual | ConvertTo-Json -Depth 5 -Compress
    if ($expectedJson -cne $actualJson) {
        throw "Artifact verification failed for $Label"
    }
}

$sourceRoot = Get-ResolvedDirectory $AllowedSourceRoot
$sourcePrefix = $sourceRoot.TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
$storeFull = [System.IO.Path]::GetFullPath($StoreRoot)
New-Item -ItemType Directory -Path $storeFull -Force | Out-Null
$results = @()

foreach ($source in $SourcePath) {
    $sourceFull = Get-ResolvedDirectory $source
    if (-not ($sourceFull + [System.IO.Path]::DirectorySeparatorChar).StartsWith(
        $sourcePrefix,
        [System.StringComparison]::OrdinalIgnoreCase
    )) {
        throw "Source is outside allowed root: $sourceFull"
    }

    $records = @(Get-FileRecords $sourceFull)
    $treeHash = Get-RecordsDigest $records
    $objectRoot = Join-Path (Join-Path $storeFull 'sha256') $treeHash
    $payloadRoot = Join-Path $objectRoot 'payload'
    $manifestPath = Join-Path $objectRoot 'archive-manifest.json'

    if (-not (Test-Path -LiteralPath $payloadRoot)) {
        $stagingRoot = Join-Path $storeFull ('staging-' + [guid]::NewGuid().ToString('N'))
        $stagingPayload = Join-Path $stagingRoot 'payload'
        New-Item -ItemType Directory -Path $stagingRoot -Force | Out-Null
        Copy-Item -LiteralPath $sourceFull -Destination $stagingPayload -Recurse -Force
        $copied = @(Get-FileRecords $stagingPayload)
        Assert-MatchingRecords $records $copied $sourceFull
        New-Item -ItemType Directory -Path (Split-Path $objectRoot -Parent) -Force | Out-Null
        Move-Item -LiteralPath $stagingRoot -Destination $objectRoot
    }

    $verified = @(Get-FileRecords $payloadRoot)
    Assert-MatchingRecords $records $verified $sourceFull

    $manifest = [ordered]@{
        schema = 'cityprompt.content-addressed-artifact@1'
        tree_sha256 = $treeHash
        source_name = [System.IO.Path]::GetFileName($sourceFull)
        source_path_at_archive = $sourceFull
        archived_utc = [DateTime]::UtcNow.ToString('o')
        file_count = $records.Count
        total_bytes = [int64](($records | Measure-Object bytes -Sum).Sum)
        payload = 'payload'
        files = $records
    }
    $manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding utf8

    $removed = $false
    if ($RemoveSource) {
        if ($PSCmdlet.ShouldProcess($sourceFull, "Remove verified source directory")) {
            Remove-Item -LiteralPath $sourceFull -Recurse -Force
            $removed = $true
        }
    }

    $results += [pscustomobject]@{
        source = $sourceFull
        tree_sha256 = $treeHash
        object = $objectRoot
        files = $records.Count
        bytes = [int64](($records | Measure-Object bytes -Sum).Sum)
        source_removed = $removed
    }
}

$results | ConvertTo-Json -Depth 5
