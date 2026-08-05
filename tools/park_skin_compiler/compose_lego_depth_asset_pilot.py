"""Compose the mobile-friendly LEGO surface + authored depth pilot sheet."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[2]


def font(size: int, bold: bool = False):
    names = ("arialbd.ttf", "DejaVuSans-Bold.ttf") if bold else ("arial.ttf", "DejaVuSans.ttf")
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def fit(path: Path, size: tuple[int, int], centering=(0.5, 0.5)) -> Image.Image:
    return ImageOps.fit(Image.open(path).convert("RGB"), size, Image.Resampling.LANCZOS, centering=centering)


def contain(path: Path, size: tuple[int, int], background="#e9e7e1") -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, background)
    result.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return result


def rounded_paste(sheet: Image.Image, image: Image.Image, position, radius=14) -> None:
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, image.width - 1, image.height - 1), radius=radius, fill=255)
    sheet.paste(image, position, mask)


def label(draw: ImageDraw.ImageDraw, xy, text: str, fill="#14241e") -> None:
    x, y = xy
    box = draw.textbbox((0, 0), text, font=font(15, True))
    draw.rounded_rectangle((x, y, x + box[2] + 24, y + 34), radius=8, fill=fill)
    draw.text((x + 12, y + 7), text, font=font(15, True), fill="white")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = REPO_ROOT / "artifacts/neighborhood-park-lego-depth-pilot"
    references = REPO_ROOT / "frontend/public/archetypes/openspaces/basketball-court"

    width, height = 2000, 1510
    sheet = Image.new("RGB", (width, height), "#f3f1ec")
    draw = ImageDraw.Draw(sheet)
    draw.text((32, 24), "LEGO PARK + AUTHORED 3D DEPTH — BASKETBALL PILOT", font=font(37, True), fill="#15251f")
    draw.text((32, 75), "One semantic ground grammar, one exact program envelope, reusable metric assets seated at 1:1 scale.", font=font(20), fill="#46574f")
    draw.text((32, 111), "The source renders define equipment language and count; the LEGO process owns all horizontal surfaces.", font=font(18, True), fill="#795431")

    top_y, ref_w, ref_h, gap = 160, 460, 338, 18
    ref_paths = [
        references / "variant_0.png",
        references / "variant_0_angle_60.jpg",
        references / "variant_0_angle_90.jpg",
    ]
    ref_labels = ("ARCHETYPE BASE", "ARCHETYPE 60°", "ARCHETYPE 90°")
    for index, (path, text) in enumerate(zip(ref_paths, ref_labels)):
        x = 32 + index * (ref_w + gap)
        rounded_paste(sheet, fit(path, (ref_w, ref_h), (0.5, 0.48)), (x, top_y))
        label(draw, (x + 12, top_y + 12), text)

    outcome_x = 32 + 3 * (ref_w + gap)
    draw.rounded_rectangle((outcome_x, top_y, width - 32, top_y + ref_h), radius=16, fill="#172820")
    draw.text((outcome_x + 24, top_y + 24), "PILOT CONTRACT", font=font(18, True), fill="#d4a775")
    for index, line in enumerate((
        "72 × 54 m parcel",
        "32 × 19 m envelope",
        "metric scale = 1.0",
        "GLBs contain no ground",
        "0 API calls",
    )):
        draw.text((outcome_x + 24, top_y + 72 + index * 43), f"• {line}", font=font(17), fill="#e7eee9")

    row_y, image_h = 540, 470
    panel_w = 955
    surface = fit(root / "renders/surface_only_overview.png", (panel_w, image_h), (0.5, 0.53))
    combined = fit(root / "renders/combined_overview.png", (panel_w, image_h), (0.5, 0.53))
    rounded_paste(sheet, surface, (32, row_y))
    rounded_paste(sheet, combined, (1013, row_y))
    label(draw, (48, row_y + 16), "A — LEGO SURFACE ONLY")
    label(draw, (1029, row_y + 16), "B — SAME SURFACE + DEPTH GLBs", "#7b4b26")

    lower_y, lower_h = 1040, 405
    plan = contain(root / "layout/plan.png", (720, lower_h))
    top = fit(root / "renders/combined_top.png", (720, lower_h), (0.5, 0.5))
    rounded_paste(sheet, plan, (32, lower_y))
    rounded_paste(sheet, top, (772, lower_y))
    label(draw, (48, lower_y + 16), "SEMANTIC PLAN")
    label(draw, (788, lower_y + 16), "TOP REGISTRATION CHECK")
    method_x = 1512
    draw.rounded_rectangle((method_x, lower_y, width - 32, lower_y + lower_h), radius=16, fill="#172820")
    draw.text((method_x + 24, lower_y + 24), "RESULT", font=font(19, True), fill="#d4a775")
    lines = (
        "YES — the systems combine.",
        "",
        "The surface remains adaptive",
        "and material-driven. The court",
        "kit supplies silhouette, shadows",
        "and recognizable equipment.",
        "",
        "Next gate: repeat on one rotated",
        "or irregular parcel, then add a",
        "module-level playground asset.",
    )
    for index, line in enumerate(lines):
        draw.text((method_x + 24, lower_y + 72 + index * 29), line, font=font(16, index == 0), fill="#e7eee9")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output, optimize=True)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
