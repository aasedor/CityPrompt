[CmdletBinding()]
param(
    [string] $Repository = '.'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath $Repository).Path
$lines = @(& git -C $repo worktree list --porcelain)
$records = @()
$current = $null

foreach ($line in $lines) {
    if ($line.StartsWith('worktree ')) {
        if ($null -ne $current) { $records += [pscustomobject]$current }
        $current = [ordered]@{
            path = $line.Substring(9)
            head = $null
            branch = $null
            detached = $false
            locked = $false
            lock_reason = $null
        }
    }
    elseif ($null -eq $current) {
        continue
    }
    elseif ($line.StartsWith('HEAD ')) {
        $current.head = $line.Substring(5)
    }
    elseif ($line.StartsWith('branch ')) {
        $current.branch = $line.Substring(7).Replace('refs/heads/', '')
    }
    elseif ($line -eq 'detached') {
        $current.detached = $true
    }
    elseif ($line.StartsWith('locked')) {
        $current.locked = $true
        $current.lock_reason = $line.Substring(6).Trim()
    }
}
if ($null -ne $current) { $records += [pscustomobject]$current }

$result = foreach ($record in $records) {
    $statusLines = @(& git -C $record.path status --porcelain 2>$null)
    $statusExitCode = $LASTEXITCODE
    $statusOk = $statusExitCode -eq 0
    & git -C $repo merge-base --is-ancestor $record.head origin/main 2>$null
    $merged = $LASTEXITCODE -eq 0
    [pscustomobject]@{
        path = $record.path
        head = $record.head
        branch = $record.branch
        detached = $record.detached
        locked = $record.locked
        lock_reason = $record.lock_reason
        status_ok = $statusOk
        status_exit_code = $statusExitCode
        dirty = -not $statusOk -or $statusLines.Count -gt 0
        dirty_path_count = $statusLines.Count
        merged_into_origin_main = $merged
        removal_eligible = $merged -and $statusOk -and -not $record.locked -and $statusLines.Count -eq 0
    }
}

$result | ConvertTo-Json -Depth 4
