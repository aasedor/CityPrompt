$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

if (-not (Test-Path $edge)) {
  throw "Microsoft Edge not found at $edge"
}

$concepts = @(
  "terrain-atlas",
  "city-pulse",
  "canopy-workbench",
  "studio-orbit"
)

Add-Type -AssemblyName System.Drawing
$profileDir = Join-Path $root ".edge-profile"
New-Item -ItemType Directory -Force -Path $profileDir | Out-Null

foreach ($name in $concepts) {
  $htmlPath = Join-Path $root "$name.html"
  $pngPath = Join-Path $root "$name.png"
  $jpgPath = Join-Path $root "$name.jpg"
  $uri = "file:///" + ($htmlPath -replace "\\", "/")

  & $edge `
    --headless `
    --disable-gpu `
    --disable-crash-reporter `
    --hide-scrollbars `
    --user-data-dir=$profileDir `
    --force-device-scale-factor=2 `
    --window-size=1660,1060 `
    --run-all-compositor-stages-before-draw `
    --virtual-time-budget=2500 `
    --screenshot=$pngPath `
    $uri | Out-Null

  $image = [System.Drawing.Image]::FromFile($pngPath)
  $bitmap = New-Object System.Drawing.Bitmap($image)
  $codec = [System.Drawing.Imaging.ImageCodecInfo]::GetImageEncoders() | Where-Object { $_.MimeType -eq "image/jpeg" }
  $encoder = [System.Drawing.Imaging.Encoder]::Quality
  $params = New-Object System.Drawing.Imaging.EncoderParameters(1)
  $params.Param[0] = New-Object System.Drawing.Imaging.EncoderParameter($encoder, [long]92)
  $bitmap.Save($jpgPath, $codec, $params)
  $bitmap.Dispose()
  $image.Dispose()
}
