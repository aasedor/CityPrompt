"""Compose the reference/atlas/PBR/fixed-geometry comparison sheet."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parents[1]
SCHEDULE = json.loads((TOOL_DIR / "neighborhood_park_sources.json").read_text(encoding="utf-8"))
TEXTURE_ROOT = REPO_ROOT / "frontend/public/park-skins/neighborhood-park"
ARTIFACT_ROOT = REPO_ROOT / "artifacts/neighborhood-park-reference-skins-v2"


def font(size: int, bold: bool = False):
    for name in ("arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def panel(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(image.convert("RGB"), size, method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))


def pbr_panel(texture_dir: Path, size: tuple[int, int]) -> Image.Image:
    width, height = size
    gap = 8
    normal = panel(Image.open(texture_dir / "normal.png"), (width, int(height * 0.62)))
    half = (width - gap) // 2
    map_height = height - normal.height - gap
    rough_l = ImageOps.fit(Image.open(texture_dir / "roughness.jpg").convert("L"), (half, map_height), method=Image.Resampling.LANCZOS)
    ao_l = ImageOps.fit(Image.open(texture_dir / "ao.jpg").convert("L"), (width - half - gap, map_height), method=Image.Resampling.LANCZOS)
    rough = ImageOps.colorize(rough_l, "#11151a", "#f5f1e7")
    ao = ImageOps.colorize(ao_l, "#172018", "#ffffff")
    result = Image.new("RGB", size, "#111714")
    result.paste(normal, (0, 0))
    result.paste(rough, (0, normal.height + gap))
    result.paste(ao, (half + gap, normal.height + gap))
    draw = ImageDraw.Draw(result)
    draw.rectangle((0, 0, 106, 30), fill="#15221dd9")
    draw.text((10, 6), "NORMAL", font=font(14, True), fill="white")
    draw.rectangle((0, normal.height + gap, 128, normal.height + gap + 30), fill="#15221dd9")
    draw.text((10, normal.height + gap + 6), "ROUGHNESS", font=font(14, True), fill="white")
    draw.rectangle((half + gap, normal.height + gap, half + gap + 52, normal.height + gap + 30), fill="#15221dd9")
    draw.text((half + gap + 10, normal.height + gap + 6), "AO", font=font(14, True), fill="white")
    return result


def main() -> None:
    gap, label_w, panel_w, panel_h = 18, 270, 410, 285
    header_h, footer_h = 160, 72
    width = label_w + panel_w * 4 + gap * 6
    height = header_h + panel_h * 4 + gap * 5 + footer_h
    sheet = Image.new("RGB", (width, height), "#f3f1ec")
    draw = ImageDraw.Draw(sheet)
    draw.text((gap, 24), "NEIGHBORHOOD PARK — PARISIAN ATLAS METHOD", font=font(34, True), fill="#16251f")
    draw.text((gap, 72), "One fixed LEGO geometry. Four skins taken directly from the existing archetype images.", font=font(20), fill="#45564f")
    draw.text((gap, 106), "Hard reference → rectified full-park atlas → derived PBR → continuous XY projection", font=font(18, True), fill="#795331")
    headings = ("ARCHETYPE REFERENCE", "RECTIFIED ATLAS", "DERIVED PBR", "SAME LEGO GEOMETRY")
    for index, heading in enumerate(headings):
        x = label_w + gap * 2 + index * (panel_w + gap)
        draw.text((x, header_h - 34), heading, font=font(14, True), fill="#52615b")

    for row, (variant_id, variant) in enumerate(SCHEDULE["variants"].items()):
        y = header_h + row * (panel_h + gap)
        draw.rounded_rectangle((gap, y, label_w + gap, y + panel_h), radius=16, fill="#172720")
        draw.text((gap + 22, y + 30), f"0{row + 1}", font=font(20, True), fill="#bf9165")
        words = variant["label"].split()
        line1 = " ".join(words[:2])
        line2 = " ".join(words[2:])
        draw.text((gap + 22, y + 76), line1, font=font(25, True), fill="white")
        if line2:
            draw.text((gap + 22, y + 108), line2, font=font(25, True), fill="white")
        draw.text((gap + 22, y + 186), "same topology", font=font(15), fill="#aebcb5")
        draw.text((gap + 22, y + 211), "reference atlas skin", font=font(15), fill="#aebcb5")
        draw.text((gap + 22, y + 244), "0 API calls", font=font(15, True), fill="#d1a779")

        source = Image.open(REPO_ROOT / variant["source"])
        atlas = Image.open(TEXTURE_ROOT / variant_id / "albedo.jpg")
        render = Image.open(ARTIFACT_ROOT / "renders" / f"{variant_id}.png")
        images = (
            panel(source, (panel_w, panel_h)),
            panel(atlas, (panel_w, panel_h)),
            pbr_panel(TEXTURE_ROOT / variant_id, (panel_w, panel_h)),
            panel(render, (panel_w, panel_h)),
        )
        for column, item in enumerate(images):
            x = label_w + gap * 2 + column * (panel_w + gap)
            mask = Image.new("L", item.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, panel_w - 1, panel_h - 1), radius=14, fill=255)
            sheet.paste(item, (x, y), mask)

    draw.text((gap, height - 44), "Pilot gate: visually review these four skins before any broader park-family rollout.", font=font(17, True), fill="#46564f")
    output = ARTIFACT_ROOT / "neighborhood-park-parisian-method-comparison.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, optimize=True)
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
