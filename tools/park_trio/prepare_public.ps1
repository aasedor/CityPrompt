param(
    [Parameter(Mandatory=$true)][string]$RuntimePublicRoot,
    [Parameter(Mandatory=$true)][string]$OutputPublicRoot
)
$ErrorActionPreference='Stop'
$source=(Resolve-Path -LiteralPath $RuntimePublicRoot).Path
$destination=[IO.Path]::GetFullPath($OutputPublicRoot)
if ($source -eq $destination) { throw 'Use a separate external output directory.' }
New-Item -ItemType Directory -Path $destination -Force | Out-Null
# Preserve existing candidates. Reuse hydrated application assets without copying
# gigabytes of historical experiments or replacing any existing path.
foreach($item in Get-ChildItem -LiteralPath $source){
    $target=Join-Path $destination $item.Name
    if($item.Name -eq 'landscape-pilots' -and $item.PSIsContainer){
        New-Item -ItemType Directory -Path $target -Force | Out-Null
        foreach($child in Get-ChildItem -LiteralPath $item.FullName){
            $childTarget=Join-Path $target $child.Name
            if(Test-Path -LiteralPath $childTarget){continue}
            if($child.PSIsContainer){New-Item -ItemType Junction -Path $childTarget -Target $child.FullName | Out-Null}
            else{Copy-Item -LiteralPath $child.FullName -Destination $childTarget}
        }
    } elseif(-not (Test-Path -LiteralPath $target)) {
        if($item.PSIsContainer){New-Item -ItemType Junction -Path $target -Target $item.FullName | Out-Null}
        else{Copy-Item -LiteralPath $item.FullName -Destination $target}
    }
}
Write-Output "Prepared external public assets: $destination"
