"""Compose one zoomable contact sheet for every Meshy park catalog v3 brief."""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--wave",
        action="append",
        nargs=3,
        required=True,
        metavar=("BATCH", "REVIEW", "ARTIFACT_ROOT"),
    )
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def contain(path: Path, size: tuple[int, int]) -> Image.Image:
    canvas = Image.new("RGB", size, "#252b29")
    if not path.is_file():
        draw = ImageDraw.Draw(canvas)
        draw.line((30, 30, size[0] - 30, size[1] - 30), fill="#8c4d4a", width=6)
        draw.line((size[0] - 30, 30, 30, size[1] - 30), fill="#8c4d4a", width=6)
        draw.text((22, size[1] // 2 - 10), "NOT GENERATED", fill="#f0bbb5", font=font(18, bold=True))
        return canvas
    image = Image.open(path).convert("RGB")
    ratio = min(size[0] / image.width, size[1] / image.height)
    image = image.resize(
        (max(1, round(image.width * ratio)), max(1, round(image.height * ratio))),
        Image.Resampling.LANCZOS,
    )
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def main() -> None:
    options = parse_args()
    records: list[dict[str, object]] = []
    total_credits = 0
    for batch_value, review_value, artifact_value in options.wave:
        batch = json.loads(Path(batch_value).resolve().read_text(encoding="utf-8"))
        review = json.loads(Path(review_value).resolve().read_text(encoding="utf-8"))
        accepted = {item["assetId"] for item in review["accepted"]}
        rejected = {item["assetId"]: item["reason"] for item in review["rejected"]}
        total_credits += review["creditsUsed"]
        for item in batch["objects"]:
            asset_id = item["assetId"]
            records.append(
                {
                    **item,
                    "artifactRoot": Path(artifact_value).resolve(),
                    "status": "accepted" if asset_id in accepted else "rejected",
                    "reason": rejected.get(asset_id),
                }
            )

    columns = 4
    if len(records) % columns:
        raise ValueError("Catalog rows must contain four archetype variants")
    family_count = len(records) // columns
    width, header_h, margin, gap = 1800, 190, 28, 14
    row_header_h, card_h, row_gap = 42, 300, 20
    row_h = row_header_h + card_h + row_gap
    card_w = (width - margin * 2 - gap * (columns - 1)) // columns
    image_h = 224
    height = header_h + family_count * row_h + margin
    canvas = Image.new("RGB", (width, height), "#e9e5dc")
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, width, header_h - 14), fill="#202725")
    draw.text((margin, 28), "CITY PROMPT PARK LEGO — COMPLETE MESHY GENERATION SHEET", fill="#ffffff", font=font(30, bold=True))
    accepted_count = sum(item["status"] == "accepted" for item in records)
    rejected_count = len(records) - accepted_count
    draw.text(
        (margin, 78),
        f"{len(records)} archetype-variant briefs  •  {accepted_count} promoted  •  {rejected_count} rejected / incomplete  •  {total_credits:,} Meshy credits",
        fill="#b8d2c1",
        font=font(21),
    )
    draw.text(
        (margin, 118),
        "Normalized runtime GLBs — exact variant routing — no people or large buildings",
        fill="#9fb2a6",
        font=font(18),
    )

    for family_index in range(family_count):
        family_records = records[family_index * columns : (family_index + 1) * columns]
        family = str(family_records[0]["family"])
        top = header_h + family_index * row_h
        draw.rectangle((margin, top, width - margin, top + row_header_h - 4), fill="#313a36")
        draw.text(
            (margin + 14, top + 8),
            f"{family_index + 1:02d}  {family.replace('-', ' ').upper()}",
            fill="#ffffff",
            font=font(18, bold=True),
        )
        for column, item in enumerate(family_records):
            left = margin + column * (card_w + gap)
            card_top = top + row_header_h
            asset_id = str(item["assetId"])
            object_dir = Path(item["artifactRoot"]) / asset_id
            runtime = object_dir / "previews" / "front-three-quarter.png"
            thumbnail = object_dir / "meshy-thumbnail.png"
            preview = contain(runtime if runtime.is_file() else thumbnail, (card_w, image_h))
            canvas.paste(preview, (left, card_top))
            status = str(item["status"])
            status_color = "#2d8654" if status == "accepted" else "#bd4a45"
            draw.rectangle((left, card_top + image_h, left + card_w, card_top + card_h), fill="#f8f5ed")
            draw.rectangle((left, card_top, left + 8, card_top + card_h), fill=status_color)
            draw.text(
                (left + 16, card_top + image_h + 10),
                "PROMOTED" if status == "accepted" else "REJECTED / INCOMPLETE",
                fill=status_color,
                font=font(14, bold=True),
            )
            label = "\n".join(textwrap.wrap(asset_id.replace("-v1", ""), width=46)[:2])
            draw.multiline_text((left + 16, card_top + image_h + 34), label, fill="#27302c", font=font(14), spacing=2)

    options.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(options.output, optimize=True)
    print(options.output)
    print(f"{width}x{height}; {len(records)} briefs; {accepted_count} promoted; {rejected_count} rejected/incomplete")


if __name__ == "__main__":
    main()
