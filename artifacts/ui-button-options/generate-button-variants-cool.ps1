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

    $d = $Radius * 2
    if ($d -gt $Width) { $d = $Width }
    if ($d -gt $Height) { $d = $Height }

    $arc = [System.Drawing.RectangleF]::new($X, $Y, $d, $d)
    $path.AddArc($arc, 180, 90)
    $arc.X = $X + $Width - $d
    $path.AddArc($arc, 270, 90)
    $arc.Y = $Y + $Height - $d
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
        if ($null -ne $Brush) { $Graphics.FillPath($Brush, $path) }
        if ($null -ne $Pen) { $Graphics.DrawPath($Pen, $path) }
    } finally {
        $path.Dispose()
    }
}

function Fill-RoundedRectGradient {
    param(
        [System.Drawing.Graphics]$Graphics,
        [float]$X,
        [float]$Y,
        [float]$Width,
        [float]$Height,
        [float]$Radius,
        [System.Drawing.Color]$StartColor,
        [System.Drawing.Color]$EndColor,
        [float]$Angle = 90
    )

    $path = New-RoundedRectPath -X $X -Y $Y -Width $Width -Height $Height -Radius $Radius
    $rect = [System.Drawing.RectangleF]::new($X, $Y, $Width, $Height)
    $brush = [System.Drawing.Drawing2D.LinearGradientBrush]::new($rect, $StartColor, $EndColor, $Angle)
    try {
        $Graphics.FillPath($brush, $path)
    } finally {
        $brush.Dispose()
        $path.Dispose()
    }
}

function Add-SoftShadow {
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

    if ($Alpha -le 0) { return }

    $a1 = [Math]::Max(8, $Alpha)
    $a2 = [Math]::Max(6, [int]($Alpha * 0.55))

    $brush1 = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb($a1, 0, 0, 0))
    $brush2 = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb($a2, 0, 0, 0))
    try {
        Draw-RoundedRect -Graphics $Graphics -Brush $brush1 -Pen $null -X $X -Y ($Y + $OffsetY) -Width $Width -Height $Height -Radius $Radius
        Draw-RoundedRect -Graphics $Graphics -Brush $brush2 -Pen $null -X ($X - 1) -Y ($Y + $OffsetY + 3) -Width ($Width + 2) -Height ($Height + 2) -Radius ($Radius + 1)
    } finally {
        $brush1.Dispose()
        $brush2.Dispose()
    }
}

function New-BadgePath {
    param(
        [string]$Shape,
        [float]$X,
        [float]$Y,
        [float]$Size
    )

    $path = New-Object System.Drawing.Drawing2D.GraphicsPath
    switch ($Shape) {
        "hex" {
            $points = @(
                [System.Drawing.PointF]::new($X + $Size * 0.5, $Y),
                [System.Drawing.PointF]::new($X + $Size * 0.92, $Y + $Size * 0.24),
                [System.Drawing.PointF]::new($X + $Size * 0.92, $Y + $Size * 0.76),
                [System.Drawing.PointF]::new($X + $Size * 0.5, $Y + $Size),
                [System.Drawing.PointF]::new($X + $Size * 0.08, $Y + $Size * 0.76),
                [System.Drawing.PointF]::new($X + $Size * 0.08, $Y + $Size * 0.24)
            )
            $path.AddPolygon($points)
        }
        "diamond" {
            $points = @(
                [System.Drawing.PointF]::new($X + $Size * 0.5, $Y),
                [System.Drawing.PointF]::new($X + $Size, $Y + $Size * 0.5),
                [System.Drawing.PointF]::new($X + $Size * 0.5, $Y + $Size),
                [System.Drawing.PointF]::new($X, $Y + $Size * 0.5)
            )
            $path.AddPolygon($points)
        }
        "squircle" {
            $inner = New-RoundedRectPath -X $X -Y $Y -Width $Size -Height $Size -Radius ($Size * 0.34)
            $path.AddPath($inner, $false)
            $inner.Dispose()
        }
        default {
            $path.AddEllipse($X, $Y, $Size, $Size)
        }
    }
    $path.CloseFigure()
    return $path
}

function Draw-Glyph {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string]$Kind,
        [float]$X,
        [float]$Y,
        [float]$Size,
        [System.Drawing.Color]$Color
    )

    $stroke = [Math]::Max(1.5, $Size * 0.11)
    $pen = [System.Drawing.Pen]::new($Color, $stroke)
    $pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
    $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
    $pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
    $brush = [System.Drawing.SolidBrush]::new($Color)

    try {
        switch ($Kind) {
            "boundary" {
                $pts = @(
                    [System.Drawing.PointF]::new($X + $Size * 0.52, $Y + $Size * 0.09),
                    [System.Drawing.PointF]::new($X + $Size * 0.85, $Y + $Size * 0.26),
                    [System.Drawing.PointF]::new($X + $Size * 0.79, $Y + $Size * 0.74),
                    [System.Drawing.PointF]::new($X + $Size * 0.5, $Y + $Size * 0.9),
                    [System.Drawing.PointF]::new($X + $Size * 0.2, $Y + $Size * 0.74),
                    [System.Drawing.PointF]::new($X + $Size * 0.15, $Y + $Size * 0.26)
                )
                $Graphics.DrawPolygon($pen, $pts)
            }
            "paths" {
                $Graphics.DrawBezier(
                    $pen,
                    [System.Drawing.PointF]::new($X + $Size * 0.05, $Y + $Size * 0.7),
                    [System.Drawing.PointF]::new($X + $Size * 0.32, $Y + $Size * 0.32),
                    [System.Drawing.PointF]::new($X + $Size * 0.7, $Y + $Size * 0.88),
                    [System.Drawing.PointF]::new($X + $Size * 0.95, $Y + $Size * 0.46)
                )
                $Graphics.DrawBezier(
                    $pen,
                    [System.Drawing.PointF]::new($X + $Size * 0.08, $Y + $Size * 0.38),
                    [System.Drawing.PointF]::new($X + $Size * 0.32, $Y + $Size * 0.06),
                    [System.Drawing.PointF]::new($X + $Size * 0.72, $Y + $Size * 0.58),
                    [System.Drawing.PointF]::new($X + $Size * 0.92, $Y + $Size * 0.2)
                )
            }
            "buildings" {
                $w = $Size * 0.14
                $gap = $Size * 0.06
                $baseX = $X + $Size * 0.16
                $Graphics.FillRectangle($brush, $baseX, $Y + $Size * 0.42, $w, $Size * 0.42)
                $Graphics.FillRectangle($brush, $baseX + $w + $gap, $Y + $Size * 0.24, $w, $Size * 0.6)
                $Graphics.FillRectangle($brush, $baseX + ($w + $gap) * 2, $Y + $Size * 0.1, $w, $Size * 0.74)
                $Graphics.FillRectangle($brush, $baseX + ($w + $gap) * 3, $Y + $Size * 0.3, $w, $Size * 0.54)
            }
            "parks" {
                $Graphics.FillEllipse($brush, $X + $Size * 0.18, $Y + $Size * 0.18, $Size * 0.42, $Size * 0.34)
                $Graphics.FillEllipse($brush, $X + $Size * 0.46, $Y + $Size * 0.2, $Size * 0.32, $Size * 0.3)
                $Graphics.FillRectangle($brush, $X + $Size * 0.44, $Y + $Size * 0.5, $Size * 0.08, $Size * 0.3)
                $Graphics.FillEllipse($brush, $X + $Size * 0.08, $Y + $Size * 0.55, $Size * 0.18, $Size * 0.12)
            }
        }
    } finally {
        $pen.Dispose()
        $brush.Dispose()
    }
}

function Draw-Badge {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string]$Shape,
        [string]$IconKind,
        [float]$X,
        [float]$Y,
        [float]$Size,
        [System.Drawing.Color]$StartColor,
        [System.Drawing.Color]$EndColor,
        [System.Drawing.Color]$BorderColor,
        [System.Drawing.Color]$GlyphColor
    )

    $path = New-BadgePath -Shape $Shape -X $X -Y $Y -Size $Size
    $rect = [System.Drawing.RectangleF]::new($X, $Y, $Size, $Size)
    $brush = [System.Drawing.Drawing2D.LinearGradientBrush]::new($rect, $StartColor, $EndColor, 45.0)
    $pen = [System.Drawing.Pen]::new($BorderColor, 1.0)
    try {
        $Graphics.FillPath($brush, $path)
        $Graphics.DrawPath($pen, $path)
    } finally {
        $pen.Dispose()
        $brush.Dispose()
        $path.Dispose()
    }

    Draw-Glyph -Graphics $Graphics -Kind $IconKind -X ($X + $Size * 0.12) -Y ($Y + $Size * 0.12) -Size ($Size * 0.76) -Color $GlyphColor
}

function Draw-VariantTag {
    param(
        [System.Drawing.Graphics]$Graphics,
        [string]$Text
    )

    $tagX = 16
    $tagY = 12
    $tagW = 215
    $tagH = 28
    $bg = [System.Drawing.SolidBrush]::new((New-Color "#FFFFFF" 214))
    $pen = [System.Drawing.Pen]::new((New-Color "#D1D5DB" 215), 1.0)
    $font = [System.Drawing.Font]::new("Segoe UI Semibold", 11.0, [System.Drawing.FontStyle]::Regular)
    $brush = [System.Drawing.SolidBrush]::new((New-Color "#111827" 245))
    try {
        Draw-RoundedRect -Graphics $Graphics -Brush $bg -Pen $pen -X $tagX -Y $tagY -Width $tagW -Height $tagH -Radius 14
        $Graphics.DrawString($Text, $font, $brush, [System.Drawing.PointF]::new($tagX + 11, $tagY + 5.2))
    } finally {
        $bg.Dispose()
        $pen.Dispose()
        $font.Dispose()
        $brush.Dispose()
    }
}

function Draw-ToolBarVariant {
    param(
        [System.Drawing.Graphics]$Graphics,
        [int]$CanvasWidth,
        [int]$CanvasHeight,
        [hashtable]$Style
    )

    $tools = @(
        @{ title = "Site Boundary"; subtitle = "Polygon"; icon = "boundary" },
        @{ title = "Streets + Paths"; subtitle = "Line"; icon = "paths" },
        @{ title = "Buildings"; subtitle = "Polygon"; icon = "buildings" },
        @{ title = "Parks / Plazas"; subtitle = "Polygon"; icon = "parks" }
    )

    $activeIndex = 2

    $panelWidth = [Math]::Round($CanvasWidth * $Style.PanelWidthFactor)
    $panelHeight = [Math]::Round($CanvasHeight * $Style.PanelHeightFactor)
    $panelX = [Math]::Round(($CanvasWidth - $panelWidth) / 2)
    $panelY = $CanvasHeight - $panelHeight - [Math]::Round($CanvasHeight * $Style.BottomMarginFactor)

    if ($Style.DrawPanelShadow) {
        Add-SoftShadow -Graphics $Graphics -X $panelX -Y $panelY -Width $panelWidth -Height $panelHeight -Radius $Style.PanelRadius -Alpha $Style.PanelShadowAlpha -OffsetY $Style.PanelShadowOffset
    }

    if ($Style.DrawPanel) {
        Fill-RoundedRectGradient `
            -Graphics $Graphics `
            -X $panelX `
            -Y $panelY `
            -Width $panelWidth `
            -Height $panelHeight `
            -Radius $Style.PanelRadius `
            -StartColor (New-Color $Style.PanelStartHex $Style.PanelStartAlpha) `
            -EndColor (New-Color $Style.PanelEndHex $Style.PanelEndAlpha) `
            -Angle 90

        $panelPen = [System.Drawing.Pen]::new((New-Color $Style.PanelBorderHex $Style.PanelBorderAlpha), $Style.PanelBorderWidth)
        try {
            Draw-RoundedRect -Graphics $Graphics -Brush $null -Pen $panelPen -X $panelX -Y $panelY -Width $panelWidth -Height $panelHeight -Radius $Style.PanelRadius
        } finally {
            $panelPen.Dispose()
        }
    }

    $innerPad = $Style.InnerPadding
    $buttonGap = $Style.ButtonGap
    $buttonHeight = $panelHeight - $innerPad * 2
    $buttonWidth = [Math]::Floor(($panelWidth - $innerPad * 2 - $buttonGap * 3) / 4)

    $titleFont = [System.Drawing.Font]::new("Segoe UI Semibold", $Style.TitleFontSize, [System.Drawing.FontStyle]::Regular)
    $subtitleFont = [System.Drawing.Font]::new("Segoe UI", $Style.SubtitleFontSize, [System.Drawing.FontStyle]::Regular)

    try {
        for ($i = 0; $i -lt 4; $i++) {
            $tool = $tools[$i]
            $isActive = ($i -eq $activeIndex)

            $btnX = $panelX + $innerPad + ($buttonWidth + $buttonGap) * $i
            $btnY = $panelY + $innerPad

            if ($Style.ButtonShadowAlpha -gt 0) {
                Add-SoftShadow -Graphics $Graphics -X $btnX -Y $btnY -Width $buttonWidth -Height $buttonHeight -Radius $Style.ButtonRadius -Alpha $Style.ButtonShadowAlpha -OffsetY $Style.ButtonShadowOffset
            }

            $startHex = if ($isActive) { $Style.ActiveStartHex } else { $Style.InactiveStartHex }
            $endHex = if ($isActive) { $Style.ActiveEndHex } else { $Style.InactiveEndHex }
            $startAlpha = if ($isActive) { $Style.ActiveStartAlpha } else { $Style.InactiveStartAlpha }
            $endAlpha = if ($isActive) { $Style.ActiveEndAlpha } else { $Style.InactiveEndAlpha }

            Fill-RoundedRectGradient `
                -Graphics $Graphics `
                -X $btnX `
                -Y $btnY `
                -Width $buttonWidth `
                -Height $buttonHeight `
                -Radius $Style.ButtonRadius `
                -StartColor (New-Color $startHex $startAlpha) `
                -EndColor (New-Color $endHex $endAlpha) `
                -Angle $Style.ButtonGradientAngle

            $borderHex = if ($isActive) { $Style.ActiveBorderHex } else { $Style.ButtonBorderHex }
            $borderAlpha = if ($isActive) { $Style.ActiveBorderAlpha } else { $Style.ButtonBorderAlpha }
            $btnPen = [System.Drawing.Pen]::new((New-Color $borderHex $borderAlpha), $Style.ButtonBorderWidth)
            try {
                Draw-RoundedRect -Graphics $Graphics -Brush $null -Pen $btnPen -X $btnX -Y $btnY -Width $buttonWidth -Height $buttonHeight -Radius $Style.ButtonRadius
            } finally {
                $btnPen.Dispose()
            }

            if ($Style.DrawActiveGlow -and $isActive) {
                $glowPen = [System.Drawing.Pen]::new((New-Color $Style.ActiveGlowHex $Style.ActiveGlowAlpha), $Style.ActiveGlowWidth)
                try {
                    Draw-RoundedRect -Graphics $Graphics -Brush $null -Pen $glowPen -X ($btnX + 0.8) -Y ($btnY + 0.8) -Width ($buttonWidth - 1.6) -Height ($buttonHeight - 1.6) -Radius ($Style.ButtonRadius - 1)
                } finally {
                    $glowPen.Dispose()
                }
            }

            if ($Style.DrawTopAccent) {
                $accentColors = $Style.BadgePalette[$i]
                $accentStart = New-Color $accentColors.start 240
                $accentEnd = New-Color $accentColors.end 240
                Fill-RoundedRectGradient `
                    -Graphics $Graphics `
                    -X ($btnX + 5) `
                    -Y ($btnY + 4) `
                    -Width ($buttonWidth - 10) `
                    -Height 3 `
                    -Radius 1.5 `
                    -StartColor $accentStart `
                    -EndColor $accentEnd `
                    -Angle 0
            }

            $badge = $Style.BadgePalette[$i]
            $glyphHex = if ($isActive -and $Style.ActiveGlyphHex) { $Style.ActiveGlyphHex } else { $Style.GlyphHex }
            Draw-Badge `
                -Graphics $Graphics `
                -Shape $Style.BadgeShape `
                -IconKind $tool.icon `
                -X ($btnX + $Style.BadgeLeft) `
                -Y ($btnY + $Style.BadgeTop) `
                -Size $Style.BadgeSize `
                -StartColor (New-Color $badge.start 255) `
                -EndColor (New-Color $badge.end 255) `
                -BorderColor (New-Color $Style.BadgeBorderHex $Style.BadgeBorderAlpha) `
                -GlyphColor (New-Color $glyphHex 255)

            $titleHex = if ($isActive) { $Style.ActiveTitleHex } else { $Style.TitleHex }
            $subtitleHex = if ($isActive) { $Style.ActiveSubtitleHex } else { $Style.SubtitleHex }
            $titleBrush = [System.Drawing.SolidBrush]::new((New-Color $titleHex 255))
            $subtitleBrush = [System.Drawing.SolidBrush]::new((New-Color $subtitleHex 255))
            try {
                $Graphics.DrawString($tool.title, $titleFont, $titleBrush, [System.Drawing.PointF]::new($btnX + $Style.TextLeft, $btnY + $Style.TitleTop))
                $Graphics.DrawString($tool.subtitle, $subtitleFont, $subtitleBrush, [System.Drawing.PointF]::new($btnX + $Style.TextLeft, $btnY + $Style.SubtitleTop))
            } finally {
                $titleBrush.Dispose()
                $subtitleBrush.Dispose()
            }
        }
    } finally {
        $titleFont.Dispose()
        $subtitleFont.Dispose()
    }
}

function Render-Variant {
    param(
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

            Draw-ToolBarVariant -Graphics $g -CanvasWidth $src.Width -CanvasHeight $src.Height -Style $Style
            Draw-VariantTag -Graphics $g -Text $Style.Label

            if (-not (Test-Path -LiteralPath $OutputDir)) {
                New-Item -Path $OutputDir -ItemType Directory | Out-Null
            }

            $outPath = Join-Path $OutputDir ("button-ui-cool-{0}.png" -f $Style.Id)
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
        Label = "Option 1 - Neon Orbit"
        PanelWidthFactor = 0.63
        PanelHeightFactor = 0.205
        BottomMarginFactor = 0.03
        DrawPanel = $true
        DrawPanelShadow = $true
        PanelRadius = 20
        PanelShadowAlpha = 78
        PanelShadowOffset = 7
        PanelStartHex = "#090E1D"
        PanelStartAlpha = 222
        PanelEndHex = "#23183A"
        PanelEndAlpha = 220
        PanelBorderHex = "#6366F1"
        PanelBorderAlpha = 140
        PanelBorderWidth = 1.3
        InnerPadding = 10
        ButtonGap = 8
        ButtonRadius = 13
        ButtonShadowAlpha = 0
        ButtonShadowOffset = 0
        InactiveStartHex = "#111827"
        InactiveStartAlpha = 242
        InactiveEndHex = "#1F2937"
        InactiveEndAlpha = 240
        ActiveStartHex = "#3B82F6"
        ActiveStartAlpha = 248
        ActiveEndHex = "#7C3AED"
        ActiveEndAlpha = 248
        ButtonGradientAngle = 90
        ButtonBorderHex = "#374151"
        ButtonBorderAlpha = 255
        ActiveBorderHex = "#A78BFA"
        ActiveBorderAlpha = 255
        ButtonBorderWidth = 1.1
        DrawActiveGlow = $true
        ActiveGlowHex = "#A78BFA"
        ActiveGlowAlpha = 130
        ActiveGlowWidth = 2.0
        DrawTopAccent = $false
        BadgeShape = "circle"
        BadgeSize = 19
        BadgeLeft = 8
        BadgeTop = 6
        BadgeBorderHex = "#FFFFFF"
        BadgeBorderAlpha = 185
        BadgePalette = @(
            @{ start = "#F59E0B"; end = "#F97316" },
            @{ start = "#38BDF8"; end = "#2563EB" },
            @{ start = "#8B5CF6"; end = "#6D28D9" },
            @{ start = "#22C55E"; end = "#059669" }
        )
        GlyphHex = "#FFFFFF"
        ActiveGlyphHex = "#FFFFFF"
        TitleHex = "#E5E7EB"
        SubtitleHex = "#9CA3AF"
        ActiveTitleHex = "#FFFFFF"
        ActiveSubtitleHex = "#E0E7FF"
        TitleFontSize = 8.5
        SubtitleFontSize = 7.1
        TextLeft = 8
        TitleTop = 28
        SubtitleTop = 41
    },
    @{
        Id = "02"
        Label = "Option 2 - Signal Tiles"
        PanelWidthFactor = 0.62
        PanelHeightFactor = 0.19
        BottomMarginFactor = 0.034
        DrawPanel = $true
        DrawPanelShadow = $true
        PanelRadius = 14
        PanelShadowAlpha = 44
        PanelShadowOffset = 5
        PanelStartHex = "#FFFFFF"
        PanelStartAlpha = 242
        PanelEndHex = "#EEF2FF"
        PanelEndAlpha = 236
        PanelBorderHex = "#C7D2FE"
        PanelBorderAlpha = 240
        PanelBorderWidth = 1.0
        InnerPadding = 8
        ButtonGap = 7
        ButtonRadius = 8
        ButtonShadowAlpha = 0
        ButtonShadowOffset = 0
        InactiveStartHex = "#F8FAFC"
        InactiveStartAlpha = 252
        InactiveEndHex = "#F1F5F9"
        InactiveEndAlpha = 252
        ActiveStartHex = "#0EA5E9"
        ActiveStartAlpha = 250
        ActiveEndHex = "#2563EB"
        ActiveEndAlpha = 250
        ButtonGradientAngle = 90
        ButtonBorderHex = "#CBD5E1"
        ButtonBorderAlpha = 255
        ActiveBorderHex = "#1D4ED8"
        ActiveBorderAlpha = 255
        ButtonBorderWidth = 1.0
        DrawActiveGlow = $false
        ActiveGlowHex = "#1D4ED8"
        ActiveGlowAlpha = 0
        ActiveGlowWidth = 0.0
        DrawTopAccent = $true
        BadgeShape = "hex"
        BadgeSize = 18
        BadgeLeft = 8
        BadgeTop = 6
        BadgeBorderHex = "#FFFFFF"
        BadgeBorderAlpha = 210
        BadgePalette = @(
            @{ start = "#FB923C"; end = "#F97316" },
            @{ start = "#60A5FA"; end = "#2563EB" },
            @{ start = "#A78BFA"; end = "#7C3AED" },
            @{ start = "#4ADE80"; end = "#16A34A" }
        )
        GlyphHex = "#FFFFFF"
        ActiveGlyphHex = "#FFFFFF"
        TitleHex = "#1E293B"
        SubtitleHex = "#64748B"
        ActiveTitleHex = "#FFFFFF"
        ActiveSubtitleHex = "#DBEAFE"
        TitleFontSize = 8.3
        SubtitleFontSize = 7.0
        TextLeft = 8
        TitleTop = 27
        SubtitleTop = 39.5
    },
    @{
        Id = "03"
        Label = "Option 3 - Aurora Glass"
        PanelWidthFactor = 0.64
        PanelHeightFactor = 0.2
        BottomMarginFactor = 0.028
        DrawPanel = $true
        DrawPanelShadow = $true
        PanelRadius = 22
        PanelShadowAlpha = 60
        PanelShadowOffset = 6
        PanelStartHex = "#0F172A"
        PanelStartAlpha = 118
        PanelEndHex = "#1E293B"
        PanelEndAlpha = 106
        PanelBorderHex = "#E2E8F0"
        PanelBorderAlpha = 105
        PanelBorderWidth = 1.3
        InnerPadding = 10
        ButtonGap = 9
        ButtonRadius = 14
        ButtonShadowAlpha = 0
        ButtonShadowOffset = 0
        InactiveStartHex = "#FFFFFF"
        InactiveStartAlpha = 42
        InactiveEndHex = "#E2E8F0"
        InactiveEndAlpha = 32
        ActiveStartHex = "#22D3EE"
        ActiveStartAlpha = 180
        ActiveEndHex = "#0EA5E9"
        ActiveEndAlpha = 170
        ButtonGradientAngle = 45
        ButtonBorderHex = "#E2E8F0"
        ButtonBorderAlpha = 95
        ActiveBorderHex = "#67E8F9"
        ActiveBorderAlpha = 210
        ButtonBorderWidth = 1.0
        DrawActiveGlow = $true
        ActiveGlowHex = "#67E8F9"
        ActiveGlowAlpha = 120
        ActiveGlowWidth = 1.9
        DrawTopAccent = $false
        BadgeShape = "diamond"
        BadgeSize = 18
        BadgeLeft = 9
        BadgeTop = 7
        BadgeBorderHex = "#FFFFFF"
        BadgeBorderAlpha = 180
        BadgePalette = @(
            @{ start = "#FDBA74"; end = "#FB923C" },
            @{ start = "#93C5FD"; end = "#3B82F6" },
            @{ start = "#C4B5FD"; end = "#8B5CF6" },
            @{ start = "#86EFAC"; end = "#22C55E" }
        )
        GlyphHex = "#FFFFFF"
        ActiveGlyphHex = "#FFFFFF"
        TitleHex = "#E2E8F0"
        SubtitleHex = "#CBD5E1"
        ActiveTitleHex = "#082F49"
        ActiveSubtitleHex = "#0C4A6E"
        TitleFontSize = 8.2
        SubtitleFontSize = 7.0
        TextLeft = 8
        TitleTop = 28
        SubtitleTop = 40.5
    },
    @{
        Id = "04"
        Label = "Option 4 - Noir Gold"
        PanelWidthFactor = 0.61
        PanelHeightFactor = 0.192
        BottomMarginFactor = 0.03
        DrawPanel = $true
        DrawPanelShadow = $true
        PanelRadius = 16
        PanelShadowAlpha = 90
        PanelShadowOffset = 7
        PanelStartHex = "#09090B"
        PanelStartAlpha = 234
        PanelEndHex = "#18181B"
        PanelEndAlpha = 230
        PanelBorderHex = "#FDE68A"
        PanelBorderAlpha = 145
        PanelBorderWidth = 1.2
        InnerPadding = 9
        ButtonGap = 8
        ButtonRadius = 11
        ButtonShadowAlpha = 0
        ButtonShadowOffset = 0
        InactiveStartHex = "#111827"
        InactiveStartAlpha = 246
        InactiveEndHex = "#1F2937"
        InactiveEndAlpha = 244
        ActiveStartHex = "#FCD34D"
        ActiveStartAlpha = 255
        ActiveEndHex = "#D97706"
        ActiveEndAlpha = 255
        ButtonGradientAngle = 90
        ButtonBorderHex = "#374151"
        ButtonBorderAlpha = 255
        ActiveBorderHex = "#F59E0B"
        ActiveBorderAlpha = 255
        ButtonBorderWidth = 1.0
        DrawActiveGlow = $true
        ActiveGlowHex = "#FCD34D"
        ActiveGlowAlpha = 110
        ActiveGlowWidth = 1.6
        DrawTopAccent = $false
        BadgeShape = "squircle"
        BadgeSize = 18
        BadgeLeft = 8
        BadgeTop = 6.5
        BadgeBorderHex = "#FDE68A"
        BadgeBorderAlpha = 190
        BadgePalette = @(
            @{ start = "#F59E0B"; end = "#B45309" },
            @{ start = "#60A5FA"; end = "#1D4ED8" },
            @{ start = "#FCD34D"; end = "#F59E0B" },
            @{ start = "#4ADE80"; end = "#166534" }
        )
        GlyphHex = "#F9FAFB"
        ActiveGlyphHex = "#111827"
        TitleHex = "#E5E7EB"
        SubtitleHex = "#A1A1AA"
        ActiveTitleHex = "#111827"
        ActiveSubtitleHex = "#3F3F46"
        TitleFontSize = 8.25
        SubtitleFontSize = 6.95
        TextLeft = 8
        TitleTop = 27
        SubtitleTop = 39.5
    },
    @{
        Id = "05"
        Label = "Option 5 - Pop Chips"
        PanelWidthFactor = 0.67
        PanelHeightFactor = 0.182
        BottomMarginFactor = 0.032
        DrawPanel = $false
        DrawPanelShadow = $false
        PanelRadius = 0
        PanelShadowAlpha = 0
        PanelShadowOffset = 0
        PanelStartHex = "#000000"
        PanelStartAlpha = 0
        PanelEndHex = "#000000"
        PanelEndAlpha = 0
        PanelBorderHex = "#000000"
        PanelBorderAlpha = 0
        PanelBorderWidth = 0.0
        InnerPadding = 0
        ButtonGap = 12
        ButtonRadius = 20
        ButtonShadowAlpha = 52
        ButtonShadowOffset = 5
        InactiveStartHex = "#FFFFFF"
        InactiveStartAlpha = 238
        InactiveEndHex = "#F8FAFC"
        InactiveEndAlpha = 238
        ActiveStartHex = "#FDF2F8"
        ActiveStartAlpha = 255
        ActiveEndHex = "#E0E7FF"
        ActiveEndAlpha = 255
        ButtonGradientAngle = 90
        ButtonBorderHex = "#D1D5DB"
        ButtonBorderAlpha = 255
        ActiveBorderHex = "#8B5CF6"
        ActiveBorderAlpha = 255
        ButtonBorderWidth = 1.2
        DrawActiveGlow = $true
        ActiveGlowHex = "#C084FC"
        ActiveGlowAlpha = 90
        ActiveGlowWidth = 1.7
        DrawTopAccent = $false
        BadgeShape = "circle"
        BadgeSize = 20
        BadgeLeft = 10
        BadgeTop = 7
        BadgeBorderHex = "#FFFFFF"
        BadgeBorderAlpha = 225
        BadgePalette = @(
            @{ start = "#FDBA74"; end = "#FB7185" },
            @{ start = "#93C5FD"; end = "#60A5FA" },
            @{ start = "#C4B5FD"; end = "#A78BFA" },
            @{ start = "#6EE7B7"; end = "#34D399" }
        )
        GlyphHex = "#FFFFFF"
        ActiveGlyphHex = "#FFFFFF"
        TitleHex = "#111827"
        SubtitleHex = "#6B7280"
        ActiveTitleHex = "#4C1D95"
        ActiveSubtitleHex = "#6D28D9"
        TitleFontSize = 8.5
        SubtitleFontSize = 7.1
        TextLeft = 10
        TitleTop = 29
        SubtitleTop = 42
    }
)

foreach ($style in $styles) {
    Render-Variant -Style $style
}

Write-Output "Generated $(($styles | Measure-Object).Count) cool button variants in $OutputDir"
