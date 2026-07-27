"""Create a compact gallery of the v21 alternate-footprint validation builds."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / "build" / "codex-lego-five-family-v21-shapes"
OUTPUT = BUILD / "five-family-v21-shape-matrix.png"

ITEMS = [
    ("London Mansion", "london-heritage-mansion-block-l-shape", "london-heritage-mansion-block", "L-SHAPE"),
    ("Industrial Loft", "industrial-brick-mixed-use-u-shape", "industrial-brick-mixed-use", "U-SHAPE"),
    ("Eixample Block", "eixample-apartment-block-courtyard", "eixample-apartment-block", "COURTYARD"),
    ("Modernist Civic", "modernist-civic-block-l-shape", "modernist-civic-block", "L-SHAPE"),
    ("Railway Hotel", "chateauesque-grand-railway-hotel-u-shape", "chateauesque-grand-railway-hotel", "U-SHAPE"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def fitted(path: Path, size: tuple[int, int]) -> Image.Image:
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source).convert("RGB")
    return ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)


def with_plan_inset(image: Image.Image, target: dict) -> Image.Image:
    """Overlay the exact segment plan so concavity remains legible in a street render."""
    result = image.copy()
    draw = ImageDraw.Draw(result)
    inset_w, inset_h = 160, 128
    left, top = result.width - inset_w - 14, 14
    draw.rounded_rectangle(
        (left, top, left + inset_w, top + inset_h), radius=10,
        fill="#fffdf8", outline="#17283b", width=2,
    )
    draw.text((left + 10, top + 7), "DRAWN PLAN", font=font(12, True), fill="#17283b")
    plan_top = top + 29
    width_m, depth_m = float(target["width_m"]), float(target["depth_m"])
    scale = min((inset_w - 24) / width_m, (inset_h - 42) / depth_m)
    origin_x = left + inset_w / 2
    origin_y = plan_top + (inset_h - 34) / 2
    for segment in target.get("segments", []):
        rotated = abs(float(segment["rotation_degrees"])) % 180 > 45
        segment_w = float(segment["thickness_m"] if rotated else segment["length_m"])
        segment_d = float(segment["length_m"] if rotated else segment["thickness_m"])
        cx = origin_x + float(segment["centre_x_m"]) * scale
        cy = origin_y + float(segment["centre_y_m"]) * scale
        box = (
            cx - segment_w * scale / 2,
            cy - segment_d * scale / 2,
            cx + segment_w * scale / 2,
            cy + segment_d * scale / 2,
        )
        draw.rectangle(box, fill="#5e8d60", outline="#214d32", width=2)
    return result


def main() -> None:
    width, margin, gap = 1920, 44, 24
    columns, card_w, card_h = 3, 594, 550
    header_h = 170
    canvas = Image.new("RGB", (width, header_h + 2 * card_h + gap + margin), "#f4f1e9")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 30), "PARAMETRIC FOOTPRINT VALIDATION", font=font(24, True), fill="#2f6940")
    draw.text((margin, 67), "The same LEGO families on five different geographic shapes", font=font(41, True), fill="#132234")
    draw.text(
        (margin, 123),
        "Fixed identity at entrances, corners, crowns and roofs; repeatable middle bays absorb polygon size and shape.",
        font=font(20), fill="#536170",
    )

    for index, (name, folder_name, slug, profile) in enumerate(ITEMS):
        row, column = divmod(index, columns)
        x = margin + column * (card_w + gap)
        y = header_h + row * (card_h + gap)
        folder = BUILD / folder_name
        manifest = json.loads((folder / f"{slug}_manifest.json").read_text(encoding="utf-8"))
        assembled = manifest["assembled"]
        target = assembled["footprint_target"]
        draw.rounded_rectangle((x, y, x + card_w, y + card_h), radius=18, fill="#fffdf8", outline="#d9d2c4", width=2)
        draw.rectangle((x, y, x + card_w, y + 42), fill="#2f6940")
        draw.text((x + 14, y + 10), profile, font=font(18, True), fill="white")
        render = fitted(folder / f"{slug}_preview.png", (card_w - 4, 400))
        canvas.paste(with_plan_inset(render, target), (x + 2, y + 42))
        draw.text((x + 16, y + 458), name, font=font(24, True), fill="#17283b")
        draw.text(
            (x + 16, y + 500),
            f"{target['width_m']:.0f} x {target['depth_m']:.0f} m  |  {assembled['floors']} floors  |  {assembled['triangle_count']:,} tris",
            font=font(16), fill="#65717d",
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT, quality=95)
    print(OUTPUT)


if __name__ == "__main__":
    main()
