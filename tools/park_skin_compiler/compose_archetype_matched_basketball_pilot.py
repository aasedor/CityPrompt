"""Compose a mobile reference-versus-generated acceptance sheet."""
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


def rounded_paste(sheet: Image.Image, image: Image.Image, position, radius=14) -> None:
    mask = Image.new("L", image.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, image.width - 1, image.height - 1), radius=radius, fill=255)
    sheet.paste(image, position, mask)


def tag(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=font(16, True))
    draw.rounded_rectangle((x, y, x + box[2] + 26, y + 36), radius=8, fill=fill)
    draw.text((x + 13, y + 7), text, font=font(16, True), fill="white")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    references = REPO_ROOT / "frontend/public/archetypes/openspaces/basketball-court"
    rows = (
        ("BASE / COURTSIDE", references / "variant_0.png", args.render_dir / "generated_base.png", (0.5, 0.54), (0.5, 0.55)),
        ("60° / HIGH OBLIQUE", references / "variant_0_angle_60.jpg", args.render_dir / "generated_angle_60.png", (0.5, 0.53), (0.5, 0.5)),
        ("90° / TOP REGISTRATION", references / "variant_0_angle_90.jpg", args.render_dir / "generated_angle_90.png", (0.5, 0.5), (0.5, 0.5)),
    )

    width, height = 1600, 2180
    sheet = Image.new("RGB", (width, height), "#f2f0eb")
    draw = ImageDraw.Draw(sheet)
    draw.text((32, 25), "ARCHETYPE-MATCHED LEGO + 3D DEPTH PILOT", font=font(36, True), fill="#15251f")
    draw.text((32, 76), "Basketball court v0 · reference views reconciled before modeling · metric assets remain reusable", font=font(19), fill="#46574f")
    draw.text((32, 112), "LEFT: catalogue target   ·   RIGHT: generated 3D pilot", font=font(18, True), fill="#795431")

    panel_w, panel_h, gap = 754, 535, 20
    start_y = 164
    for index, (label, reference_path, generated_path, ref_center, gen_center) in enumerate(rows):
        y = start_y + index * 584
        reference = fit(reference_path, (panel_w, panel_h), ref_center)
        generated = fit(generated_path, (panel_w, panel_h), gen_center)
        rounded_paste(sheet, reference, (32, y))
        rounded_paste(sheet, generated, (32 + panel_w + gap, y))
        tag(draw, 48, y + 14, f"REFERENCE · {label}", "#14241e")
        tag(draw, 48 + panel_w + gap, y + 14, f"GENERATED · {label}", "#805029")

    result_y = 1932
    draw.rounded_rectangle((32, result_y, width - 32, height - 30), radius=16, fill="#172820")
    draw.text((56, result_y + 24), "PILOT RESULT", font=font(20, True), fill="#d4a775")
    draw.text((56, result_y + 62), "The generated scene now carries the same urban-court identity: dark asphalt, full white linework,", font=font(17), fill="#e7eee9")
    draw.text((56, result_y + 92), "galvanized enclosure, paired hoops, lights, brick street walls, benches, trees and reference-matched cameras.", font=font(17), fill="#e7eee9")
    draw.text((56, result_y + 132), "Catalogue boundary remains clean: LEGO owns horizontal surfaces; reusable GLBs own standing depth.", font=font(17, True), fill="#e7eee9")
    draw.text((56, result_y + 172), "People are intentionally excluded from the reusable park-model acceptance bar.", font=font(16), fill="#b9c8c0")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.output, optimize=True)
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
