"""Compose mobile reference-versus-generated sheets for the five-park batch."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT = REPO_ROOT / "tools/park_skin_compiler/park_archetype_batch.json"


def font(size: int, bold: bool = False):
    names = ("arialbd.ttf", "DejaVuSans-Bold.ttf") if bold else ("arial.ttf", "DejaVuSans.ttf")
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def fit(path: Path, size: tuple[int, int]) -> Image.Image:
    return ImageOps.fit(Image.open(path).convert("RGB"), size, Image.Resampling.LANCZOS)


def rounded_paste(sheet: Image.Image, image: Image.Image, position, radius=14) -> None:
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, image.width - 1, image.height - 1), radius=radius, fill=255)
    sheet.paste(image, position, mask)


def tag(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=font(16, True))
    draw.rounded_rectangle((x, y, x + box[2] + 26, y + 36), radius=8, fill=fill)
    draw.text((x + 13, y + 7), text, font=font(16, True), fill="white")


def compose_one(item: dict, render_root: Path, output_root: Path) -> Path:
    refs = REPO_ROOT / "frontend/public/archetypes/openspaces" / item["slug"]
    generated = render_root / item["slug"]
    rows = (
        ("BASE", refs / "variant_0.png", generated / "generated_base.png"),
        ("60 DEG / HIGH OBLIQUE", refs / "variant_0_angle_60.jpg", generated / "generated_angle_60.png"),
        ("90 DEG / TOP REGISTRATION", refs / "variant_0_angle_90.jpg", generated / "generated_angle_90.png"),
    )
    width, height = 1600, 2180
    sheet = Image.new("RGB", (width, height), "#f2f0eb")
    draw = ImageDraw.Draw(sheet)
    draw.text((32, 24), item["label"].upper(), font=font(34, True), fill="#15251f")
    draw.text((32, 72), "LEGO registered surface + reusable metric 3D depth kit", font=font(19), fill="#46574f")
    draw.text((32, 108), "LEFT: catalogue target   /   RIGHT: generated building-free park layer", font=font(18, True), fill="#795431")
    panel_w, panel_h, gap = 754, 535, 20
    start_y = 164
    for index, (label, reference_path, generated_path) in enumerate(rows):
        y = start_y + index * 584
        rounded_paste(sheet, fit(reference_path, (panel_w, panel_h)), (32, y))
        rounded_paste(sheet, fit(generated_path, (panel_w, panel_h)), (32 + panel_w + gap, y))
        tag(draw, 48, y + 14, f"REFERENCE / {label}", "#14241e")
        tag(draw, 48 + panel_w + gap, y + 14, f"GENERATED / {label}", "#805029")
    result_y = 1932
    draw.rounded_rectangle((32, result_y, width - 32, height - 30), radius=16, fill="#172820")
    draw.text((56, result_y + 24), "LAYER CONTRACT", font=font(20, True), fill="#d4a775")
    draw.text((56, result_y + 62), f"Envelope: {item['envelopeM'][0]} x {item['envelopeM'][1]} m / metricScale 1.0 / {len(item['depthAssets'])} reusable GLB modules", font=font(17), fill="#e7eee9")
    draw.text((56, result_y + 100), "The generated park layer contains no people and no large buildings.", font=font(17, True), fill="#e7eee9")
    draw.text((56, result_y + 138), "Large buildings remain visible in the catalogue target only and will be rendered separately downstream.", font=font(16), fill="#b9c8c0")
    draw.text((56, result_y + 174), "LEGO owns the registered ground; the exported kit owns identity-bearing equipment and depth.", font=font(16), fill="#b9c8c0")
    output = output_root / f"{item['slug']}-comparison-mobile.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, optimize=True)
    return output


def compose_overview(items: list[dict], render_root: Path, output_root: Path) -> Path:
    width, height = 1600, 1870
    sheet = Image.new("RGB", (width, height), "#f2f0eb")
    draw = ImageDraw.Draw(sheet)
    draw.text((36, 28), "FIVE-PARK LEGO + 3D DEPTH BATCH", font=font(38, True), fill="#15251f")
    draw.text((36, 82), "Generated layer only / no people / larger buildings rendered separately", font=font(20), fill="#46574f")
    panel_w, panel_h = 744, 480
    for index, item in enumerate(items):
        col = index % 2
        row = index // 2
        x = 36 + col * 780
        y = 142 + row * 552
        image = fit(render_root / item["slug"] / "generated_angle_60.png", (panel_w, panel_h))
        rounded_paste(sheet, image, (x, y))
        tag(draw, x + 16, y + 14, item["label"].upper(), "#805029")
        draw.text((x + 8, y + panel_h + 12), f"{item['envelopeM'][0]} x {item['envelopeM'][1]} m / {len(item['depthAssets'])} reusable modules", font=font(17, True), fill="#24362e")
    y = 1792
    draw.rounded_rectangle((36, y, width - 36, height - 28), radius=14, fill="#172820")
    draw.text((58, y + 20), "Batch demonstrates five different surface-to-depth handoffs without coupling park kits to the building renderer.", font=font(17, True), fill="#e7eee9")
    output = output_root / "five-park-overview-mobile.png"
    sheet.save(output, optimize=True)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    items = json.loads(CONTRACT.read_text(encoding="utf-8"))["archetypes"]
    for item in items:
        print(f"wrote {compose_one(item, args.render_root, args.output_root)}")
    print(f"wrote {compose_overview(items, args.render_root, args.output_root)}")


if __name__ == "__main__":
    main()
