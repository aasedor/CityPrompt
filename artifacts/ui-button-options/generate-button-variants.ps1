param(
    [string]$InputPath = "Reference.png",
    [string]$OutputDir = "artifacts/ui-button-options"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Drawing

function New-Color {
    param(
        [Parameter(Mandatory = $true)][string]$Hex,
        [int]$Alpha = 255
    )
    $base = [System.Drawing.ColorTranslator]::FromHtml($Hex)
    return [System.Drawing.Color]::FromArgb($Alpha, $base.R, $base.G, $base.B)
}

function New-RoundedRectPath {
    param(
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height,
        [float]$Radius
    )

    $path = New-Object System.Drawing.Drawing2D.GraphicsPath

    if ($Radius -le 0) {
        $path.AddRectangle([System.Drawing.RectangleF]::new($X, $Y, $Width, $Height))
        return $path
    }

    $diameter = $Radius * 2
    if ($diameter -gt $Width) { $diameter = $Width }
    if ($diameter -gt $Height) { $diameter = $Height }

    $arc = [System.Drawing.RectangleF]::new($X, $Y, $diameter, $diameter)
    $path.AddArc($arc, 180, 90)

    $arc.X = $X + $Width - $diameter
    $path.AddArc($arc, 270, 90)

    $arc.Y = $Y + $Height - $diameter
    $path.AddArc($arc, 0, 90)

    $arc.X = $X
    $path.AddArc($arc, 90, 90)

    $path.CloseFigure()
    return $path
}

function Draw-RoundedRect {
    param(
        [System.Drawing.Graphics]$Graphics,
        [System.Drawing.Brush]$Brush,
        [System.Drawing.Pen]$Pen,
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height,
        [float]$Radius
    )

    $path = New-RoundedRectPath -X $X -Y $Y -Width $Width -Height $Height -Radius $Radius
    try {
        if ($null -ne $Brush) {
            $Graphics.FillPath($Brush, $path)
        }
        if ($null -ne $Pen) {
            $Graphics.DrawPath($Pen, $path)
        }
    } finally {
        $path.Dispose()
    }
}

function Draw-Icon {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string]$Kind,
        [float]$X,
        [float]$Y,
        [float]$Size,
        [System.Drawing.Color]$Color
    )

    $pen = [System.Drawing.Pen]::new($Color, [Math]::Max(1.6, $Size * 0.12))
    $pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
    $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
    $pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round

    $brush = [System.Drawing.SolidBrush]::new($Color)

    try {
        switch ($Kind) {
            "boundary" {
                $pts = @(
                    [System.Drawing.PointF]::new($X + $Size * 0.5, $Y),
                    [System.Drawing.PointF]::new($X + $Size * 0.92, $Y + $Size * 0.22),
                    [System.Drawing.PointF]::new($X + $Size * 0.86, $Y + $Size * 0.78),
                    [System.Drawing.PointF]::new($X + $Size * 0.5, $Y + $Size),
                    [System.Drawing.PointF]::new($X + $Size * 0.14, $Y + $Size * 0.78),
                    [System.Drawing.PointF]::new($X + $Size * 0.08, $Y + $Size * 0.22)
                )
                $Graphics.DrawPolygon($pen, $pts)
            }
            "paths" {
                $Graphics.DrawBezier(
                    $pen,
                    [System.Drawing.PointF]::new($X, $Y + $Size * 0.65),
                    [System.Drawing.PointF]::new($X + $Size * 0.3, $Y + $Size * 0.35),
                    [System.Drawing.PointF]::new($X + $Size * 0.7, $Y + $Size * 0.9),
                    [System.Drawing.PointF]::new($X + $Size, $Y + $Size * 0.45)
                )
                $Graphics.DrawBezier(
                    $pen,
                    [System.Drawing.PointF]::new($X, $Y + $Size * 0.35),
                    [System.Drawing.PointF]::new($X + $Size * 0.28, $Y + $Size * 0.08),
                    [System.Drawing.PointF]::new($X + $Size * 0.72, $Y + $Size * 0.55),
                    [System.Drawing.PointF]::new($X + $Size, $Y + $Size * 0.15)
                )
            }
            "buildings" {
                $w = $Size * 0.18
                $gap = $Size * 0.07
                $Graphics.FillRectangle($brush, $X + $gap, $Y + $Size * 0.45, $w, $Size * 0.5)
                $Graphics.FillRectangle($brush, $X + $w + $gap * 2, $Y + $Size * 0.2, $w, $Size * 0.75)
                $Graphics.FillRectangle($brush, $X + $w * 2 + $gap * 3, $Y + $Size * 0.05, $w, $Size * 0.9)
                $Graphics.FillRectangle($brush, $X + $w * 3 + $gap * 4, $Y + $Size * 0.32, $w, $Size * 0.63)
            }
            "parks" {
                $Graphics.FillEllipse($brush, $X + $Size * 0.15, $Y + $Size * 0.15, $Size * 0.55, $Size * 0.45)
                $Graphics.FillEllipse($brush, $X + $Size * 0.5, $Y + $Size * 0.2, $Size * 0.35, $Size * 0.35)
                $Graphics.FillRectangle($brush, $X + $Size * 0.42, $Y + $Size * 0.57, $Size * 0.1, $Size * 0.35)
            }
        }
    } finally {
        $pen.Dispose()
        $brush.Dispose()
    }
}

function Add-Shadow {
    param(
        [System.Drawing.Graphics]$Graphics,
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height,
        [float]$Radius,
        [int]$Alpha,
        [int]$OffsetY
    )

    $shadowBrush = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb($Alpha, 0, 0, 0))
    try {
        Draw-RoundedRect -Graphics $Graphics -Brush $shadowBrush -Pen $null -X $X -Y ($Y + $OffsetY) -Width $Width -Height $Height -Radius $Radius
    } finally {
        $shadowBrush.Dispose()
    }
}

function Draw-Variant {
    param(
        [string]$VariantId,
        [string]$VariantLabel,
        [hashtable]$Style
    )

    $src = [System.Drawing.Bitmap]::new($InputPath)
    try {
        $canvas = [System.Drawing.Bitmap]::new($src.Width, $src.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
        $g = [System.Drawing.Graphics]::FromImage($canvas)
        try {
            $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
            $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
            $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit
            $g.DrawImage($src, 0, 0, $src.Width, $src.Height)

            $labels = @(
                @{ title = "Site Boundary"; subtitle = "Polygon"; icon = "boundary"; iconColor = "#F59E0B" },
                @{ title = "Streets + Paths"; subtitle = "Line"; icon = "paths"; iconColor = "#3B82F6" },
                @{ title = "Buildings"; subtitle = "Polygon"; icon = "buildings"; iconColor = "#7C3AED" },
                @{ title = "Parks / Plazas"; subtitle = "Polygon"; icon = "parks"; iconColor = "#22C55E" }
            )

            $activeIndex = 2
            $panelWidth = [Math]::Round($src.Width * $Style.PanelWidthFactor)
            $panelHeight = [Math]::Round($src.Height * $Style.PanelHeightFactor)
            $panelX = [Math]::Round(($src.Width - $panelWidth) / 2)
            $panelY = $src.Height - $panelHeight - [Math]::Round($src.Height * 0.03)
            $panelRadius = $Style.PanelRadius

            if ($Style.DrawPanelShadow) {
                Add-Shadow -Graphics $g -X $panelX -Y $panelY -Width $panelWidth -Height $panelHeight -Radius $panelRadius -Alpha $Style.PanelShadowAlpha -OffsetY $Style.PanelShadowOffset
            }

            if ($Style.DrawPanel) {
                $panelBrush = [System.Drawing.SolidBrush]::new((New-Color $Style.PanelFillHex $Style.PanelFillAlpha))
                $panelPen = [System.Drawing.Pen]::new((New-Color $Style.PanelBorderHex $Style.PanelBorderAlpha), $Style.PanelBorderWidth)
                try {
                    Draw-RoundedRect -Graphics $g -Brush $panelBrush -Pen $panelPen -X $panelX -Y $panelY -Width $panelWidth -Height $panelHeight -Radius $panelRadius
                } finally {
                    $panelBrush.Dispose()
                    $panelPen.Dispose()
                }
            }

            $innerPadding = $Style.InnerPadding
            $buttonGap = $Style.ButtonGap
            $buttonHeight = $panelHeight - $innerPadding * 2
            $buttonWidth = [Math]::Floor(($panelWidth - $innerPadding * 2 - $buttonGap * 3) / 4)

            $titleFont = [System.Drawing.Font]::new("Segoe UI Semibold", $Style.TitleFontSize, [System.Drawing.FontStyle]::Regular)
            $subtitleFont = [System.Drawing.Font]::new("Segoe UI", $Style.SubtitleFontSize, [System.Drawing.FontStyle]::Regular)
            try {
                for ($i = 0; $i -lt 4; $i++) {
                    $item = $labels[$i]
                    $btnX = $panelX + $innerPadding + ($buttonWidth + $buttonGap) * $i
                    $btnY = $panelY + $innerPadding
                    $isActive = ($i -eq $activeIndex)

                    $fillHex = if ($isActive) { $Style.ActiveFillHex } else { $Style.ButtonFillHex }
                    $fillAlpha = if ($isActive) { $Style.ActiveFillAlpha } else { $Style.ButtonFillAlpha }
                    $borderHex = if ($isActive) { $Style.ActiveBorderHex } else { $Style.ButtonBorderHex }
                    $borderAlpha = if ($isActive) { $Style.ActiveBorderAlpha } else { $Style.ButtonBorderAlpha }

                    $btnBrush = [System.Drawing.SolidBrush]::new((New-Color $fillHex $fillAlpha))
                    $btnPen = [System.Drawing.Pen]::new((New-Color $borderHex $borderAlpha), $Style.ButtonBorderWidth)
                    try {
                        Draw-RoundedRect -Graphics $g -Brush $btnBrush -Pen $btnPen -X $btnX -Y $btnY -Width $buttonWidth -Height $buttonHeight -Radius $Style.ButtonRadius
                    } finally {
                        $btnBrush.Dispose()
                        $btnPen.Dispose()
                    }

                    if ($isActive -and $Style.DrawActiveGlow) {
                        $glowPen = [System.Drawing.Pen]::new((New-Color $Style.ActiveGlowHex $Style.ActiveGlowAlpha), $Style.ActiveGlowWidth)
                        try {
                            Draw-RoundedRect -Graphics $g -Brush $null -Pen $glowPen -X ($btnX + 0.8) -Y ($btnY + 0.8) -Width ($buttonWidth - 1.6) -Height ($buttonHeight - 1.6) -Radius ($Style.ButtonRadius - 1)
                        } finally {
                            $glowPen.Dispose()
                        }
                    }

                    $iconSize = $Style.IconSize
                    $iconX = $btnX + $Style.IconLeft
                    $iconY = $btnY + $Style.IconTop
                    $iconColorHex = if ($isActive -and $Style.ActiveIconColorHex) { $Style.ActiveIconColorHex } else { $item.iconColor }
                    Draw-Icon -Graphics $g -Kind $item.icon -X $iconX -Y $iconY -Size $iconSize -Color (New-Color $iconColorHex 255)

                    $titleHex = if ($isActive) { $Style.ActiveTitleHex } else { $Style.TitleHex }
                    $subtitleHex = if ($isActive) { $Style.ActiveSubtitleHex } else { $Style.SubtitleHex }
                    $titleBrush = [System.Drawing.SolidBrush]::new((New-Color $titleHex 255))
                    $subtitleBrush = [System.Drawing.SolidBrush]::new((New-Color $subtitleHex 255))
                    try {
                        $g.DrawString($item.title, $titleFont, $titleBrush, [System.Drawing.PointF]::new($btnX + $Style.TextLeft, $btnY + $Style.TitleTop))
                        $g.DrawString($item.subtitle, $subtitleFont, $subtitleBrush, [System.Drawing.PointF]::new($btnX + $Style.TextLeft, $btnY + $Style.SubtitleTop))
                    } finally {
                        $titleBrush.Dispose()
                        $subtitleBrush.Dispose()
                    }
                }
            } finally {
                $titleFont.Dispose()
                $subtitleFont.Dispose()
            }

            $tagFont = [System.Drawing.Font]::new("Segoe UI Semibold", 11, [System.Drawing.FontStyle]::Regular)
            $tagBrush = [System.Drawing.SolidBrush]::new((New-Color "#111827" 220))
            $tagBgBrush = [System.Drawing.SolidBrush]::new((New-Color "#F9FAFB" 210))
            $tagPen = [System.Drawing.Pen]::new((New-Color "#D1D5DB" 210), 1.0)
            try {
                $tagWidth = 130
                $tagHeight = 26
                $tagX = 16
                $tagY = 14
                Draw-RoundedRect -Graphics $g -Brush $tagBgBrush -Pen $tagPen -X $tagX -Y $tagY -Width $tagWidth -Height $tagHeight -Radius 13
                $g.DrawString($VariantLabel, $tagFont, $tagBrush, [System.Drawing.PointF]::new($tagX + 12, $tagY + 4.8))
            } finally {
                $tagFont.Dispose()
                $tagBrush.Dispose()
                $tagBgBrush.Dispose()
                $tagPen.Dispose()
            }

            if (-not (Test-Path -LiteralPath $OutputDir)) {
                New-Item -Path $OutputDir -ItemType Directory | Out-Null
            }
            $outPath = Join-Path $OutputDir "button-ui-$VariantId.png"
            $canvas.Save($outPath, [System.Drawing.Imaging.ImageFormat]::Png)
        } finally {
            $g.Dispose()
            $canvas.Dispose()
        }
    } finally {
        $src.Dispose()
    }
}

$styles = @(
    @{
        Id = "01"
        Label = "Option 1 - Clean Cards"
        PanelWidthFactor = 0.56
        PanelHeightFactor = 0.19
        PanelRadius = 14
        DrawPanel = $true
        DrawPanelShadow = $true
        PanelShadowAlpha = 40
        PanelShadowOffset = 4
        PanelFillHex = "#FFFFFF"
        PanelFillAlpha = 228
        PanelBorderHex = "#E5E7EB"
        PanelBorderAlpha = 235
        PanelBorderWidth = 1.2
        InnerPadding = 10
        ButtonGap = 8
        ButtonRadius = 10
        ButtonFillHex = "#FFFFFF"
        ButtonFillAlpha = 215
        ButtonBorderHex = "#E5E7EB"
        ButtonBorderAlpha = 255
        ButtonBorderWidth = 1.0
        ActiveFillHex = "#EAF3FF"
        ActiveFillAlpha = 255
        ActiveBorderHex = "#60A5FA"
        ActiveBorderAlpha = 255
        DrawActiveGlow = $false
        ActiveGlowHex = "#3B82F6"
        ActiveGlowAlpha = 90
        ActiveGlowWidth = 1.6
        TitleHex = "#0F172A"
        ActiveTitleHex = "#1E3A8A"
        SubtitleHex = "#6B7280"
        ActiveSubtitleHex = "#1D4ED8"
        TitleFontSize = 8.5
        SubtitleFontSize = 7.3
        IconSize = 14
        IconLeft = 8
        IconTop = 7
        TextLeft = 8
        TitleTop = 25
        SubtitleTop = 39
        ActiveIconColorHex = "#2563EB"
    },
    @{
        Id = "02"
        Label = "Option 2 - Glass"
        PanelWidthFactor = 0.58
        PanelHeightFactor = 0.2
        PanelRadius = 18
        DrawPanel = $true
        DrawPanelShadow = $true
        PanelShadowAlpha = 55
        PanelShadowOffset = 6
        PanelFillHex = "#0F172A"
        PanelFillAlpha = 112
        PanelBorderHex = "#FFFFFF"
        PanelBorderAlpha = 105
        PanelBorderWidth = 1.3
        InnerPadding = 11
        ButtonGap = 10
        ButtonRadius = 12
        ButtonFillHex = "#FFFFFF"
        ButtonFillAlpha = 32
        ButtonBorderHex = "#E2E8F0"
        ButtonBorderAlpha = 95
        ButtonBorderWidth = 1.0
        ActiveFillHex = "#DBEAFE"
        ActiveFillAlpha = 165
        ActiveBorderHex = "#93C5FD"
        ActiveBorderAlpha = 240
        DrawActiveGlow = $true
        ActiveGlowHex = "#60A5FA"
        ActiveGlowAlpha = 130
        ActiveGlowWidth = 1.8
        TitleHex = "#E2E8F0"
        ActiveTitleHex = "#0F172A"
        SubtitleHex = "#CBD5E1"
        ActiveSubtitleHex = "#1D4ED8"
        TitleFontSize = 8.2
        SubtitleFontSize = 7.0
        IconSize = 14
        IconLeft = 8
        IconTop = 7
        TextLeft = 8
        TitleTop = 25
        SubtitleTop = 39
        ActiveIconColorHex = "#1D4ED8"
    },
    @{
        Id = "03"
        Label = "Option 3 - Dark Dock"
        PanelWidthFactor = 0.54
        PanelHeightFactor = 0.18
        PanelRadius = 20
        DrawPanel = $true
        DrawPanelShadow = $true
        PanelShadowAlpha = 90
        PanelShadowOffset = 7
        PanelFillHex = "#111827"
        PanelFillAlpha = 228
        PanelBorderHex = "#1F2937"
        PanelBorderAlpha = 255
        PanelBorderWidth = 1.0
        InnerPadding = 10
        ButtonGap = 8
        ButtonRadius = 16
        ButtonFillHex = "#1F2937"
        ButtonFillAlpha = 235
        ButtonBorderHex = "#334155"
        ButtonBorderAlpha = 255
        ButtonBorderWidth = 1.0
        ActiveFillHex = "#FEF3C7"
        ActiveFillAlpha = 255
        ActiveBorderHex = "#F59E0B"
        ActiveBorderAlpha = 255
        DrawActiveGlow = $true
        ActiveGlowHex = "#FBBF24"
        ActiveGlowAlpha = 120
        ActiveGlowWidth = 2.0
        TitleHex = "#E5E7EB"
        ActiveTitleHex = "#78350F"
        SubtitleHex = "#9CA3AF"
        ActiveSubtitleHex = "#92400E"
        TitleFontSize = 8.3
        SubtitleFontSize = 7.0
        IconSize = 14
        IconLeft = 8
        IconTop = 7
        TextLeft = 8
        TitleTop = 25
        SubtitleTop = 39
        ActiveIconColorHex = "#B45309"
    },
    @{
        Id = "04"
        Label = "Option 4 - Floating Pills"
        PanelWidthFactor = 0.6
        PanelHeightFactor = 0.17
        PanelRadius = 24
        DrawPanel = $false
        DrawPanelShadow = $false
        PanelShadowAlpha = 0
        PanelShadowOffset = 0
        PanelFillHex = "#000000"
        PanelFillAlpha = 0
        PanelBorderHex = "#000000"
        PanelBorderAlpha = 0
        PanelBorderWidth = 0.0
        InnerPadding = 0
        ButtonGap = 10
        ButtonRadius = 18
        ButtonFillHex = "#FFFFFF"
        ButtonFillAlpha = 226
        ButtonBorderHex = "#E5E7EB"
        ButtonBorderAlpha = 255
        ButtonBorderWidth = 1.0
        ActiveFillHex = "#DCFCE7"
        ActiveFillAlpha = 255
        ActiveBorderHex = "#22C55E"
        ActiveBorderAlpha = 255
        DrawActiveGlow = $true
        ActiveGlowHex = "#34D399"
        ActiveGlowAlpha = 100
        ActiveGlowWidth = 1.8
        TitleHex = "#111827"
        ActiveTitleHex = "#14532D"
        SubtitleHex = "#6B7280"
        ActiveSubtitleHex = "#166534"
        TitleFontSize = 8.4
        SubtitleFontSize = 7.1
        IconSize = 14
        IconLeft = 10
        IconTop = 8
        TextLeft = 10
        TitleTop = 25
        SubtitleTop = 39
        ActiveIconColorHex = "#15803D"
    },
    @{
        Id = "05"
        Label = "Option 5 - Compact Grid"
        PanelWidthFactor = 0.5
        PanelHeightFactor = 0.2
        PanelRadius = 12
        DrawPanel = $true
        DrawPanelShadow = $true
        PanelShadowAlpha = 45
        PanelShadowOffset = 5
        PanelFillHex = "#F8FAFC"
        PanelFillAlpha = 220
        PanelBorderHex = "#CBD5E1"
        PanelBorderAlpha = 255
        PanelBorderWidth = 1.0
        InnerPadding = 8
        ButtonGap = 6
        ButtonRadius = 7
        ButtonFillHex = "#FFFFFF"
        ButtonFillAlpha = 240
        ButtonBorderHex = "#D1D5DB"
        ButtonBorderAlpha = 255
        ButtonBorderWidth = 1.0
        ActiveFillHex = "#EDE9FE"
        ActiveFillAlpha = 255
        ActiveBorderHex = "#8B5CF6"
        ActiveBorderAlpha = 255
        DrawActiveGlow = $false
        ActiveGlowHex = "#8B5CF6"
        ActiveGlowAlpha = 0
        ActiveGlowWidth = 0.0
        TitleHex = "#1F2937"
        ActiveTitleHex = "#4C1D95"
        SubtitleHex = "#64748B"
        ActiveSubtitleHex = "#6D28D9"
        TitleFontSize = 7.9
        SubtitleFontSize = 6.7
        IconSize = 13
        IconLeft = 7
        IconTop = 6
        TextLeft = 7
        TitleTop = 22
        SubtitleTop = 35
        ActiveIconColorHex = "#6D28D9"
    }
)

foreach ($style in $styles) {
    Draw-Variant -VariantId $style.Id -VariantLabel $style.Label -Style $style
}

Write-Output "Generated $(($styles | Measure-Object).Count) button UI variants in $OutputDir"
