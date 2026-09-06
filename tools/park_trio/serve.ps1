param(
    [Parameter(Mandatory=$true)][string]$PublicRoot,
    [Parameter(Mandatory=$true)][string]$SourceRoot,
    [int]$Port=5174
)
$ErrorActionPreference='Stop'
$taskRoot=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../..'))
$resolvedPublic=(Resolve-Path -LiteralPath $PublicRoot).Path
$candidateRoot=Join-Path $resolvedPublic 'landscape-pilots/park-trio-v3'
$manifests=Get-ChildItem -LiteralPath $candidateRoot -Filter manifest.json -Recurse
foreach($kind in @('cinema','garden','concert')){
    if(-not (Test-Path -LiteralPath (Join-Path $candidateRoot "$kind/manifest.json"))){throw "Missing candidate: $kind"}
}
foreach($manifest in $manifests){
    $data=Get-Content -LiteralPath $manifest.FullName -Raw | ConvertFrom-Json
    foreach($asset in $data.assets.PSObject.Properties.Value){
        $file=Join-Path $manifest.DirectoryName $asset.file
        if((Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant() -ne $asset.sha256){throw "Changed candidate: $file"}
    }
}
$env:CITYPROMPT_PUBLIC_DIR=$resolvedPublic
$env:VITE_ENV_DIR=(Resolve-Path -LiteralPath (Join-Path $SourceRoot 'frontend')).Path
$env:API_PROXY_TARGET='http://127.0.0.1:8002'
$env:VITE_PARK_TRIO_TRIAL='true'
Push-Location (Join-Path $taskRoot 'frontend')
try { & npm.cmd run dev -- --host 127.0.0.1 --port $Port --strictPort }
finally { Pop-Location }
