"""Compose paged archetype -> Meshy -> runtime visual-QA sheets for catalog v3."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", required=True, type=Path)
    parser.add_argument("--batch", required=True, type=Path)
    parser.add_argument("--review", type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--page-size", type=int, default=8)
    return parser.parse_args()


def image_panel(path: Path, size: tuple[int, int], *, cover: bool) -> Image.Image:
    if not path.is_file():
        canvas = Image.new("RGB", size, "#343a37")
        ImageDraw.Draw(canvas).text((16, 16), f"MISSING\n{path.name}", fill="#e7aaa5")
        return canvas
    image = Image.open(path).convert("RGB")
    ratio = max(size[0] / image.width, size[1] / image.height) if cover else min(
        size[0] / image.width, size[1] / image.height
    )
    image = image.resize(
        (max(1, round(image.width * ratio)), max(1, round(image.height * ratio))),
        Image.Resampling.LANCZOS,
    )
    if cover:
        left = max(0, (image.width - size[0]) // 2)
        top = max(0, (image.height - size[1]) // 2)
        return image.crop((left, top, left + size[0], top + size[1]))
    canvas = Image.new("RGB", size, "#222725")
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def main() -> None:
    options = parse_args()
    repo = Path(__file__).resolve().parents[2]
    batch = json.loads(options.batch.resolve().read_text(encoding="utf-8"))
    review = (
        json.loads(options.review.resolve().read_text(encoding="utf-8"))
        if options.review and options.review.is_file()
        else None
    )
    accepted = {item["assetId"]: item for item in review.get("accepted", [])} if review else {}
    rejected = {item["assetId"]: item for item in review.get("rejected", [])} if review else {}
    objects = batch["objects"]
    options.output_dir.mkdir(parents=True, exist_ok=True)

    width, margin, gap, cell_w, cell_h = 1680, 34, 20, 510, 270
    row_h, header_h = 354, 150
    page_count = (len(objects) + options.page_size - 1) // options.page_size
    for page_index in range(page_count):
        page_objects = objects[
            page_index * options.page_size : (page_index + 1) * options.page_size
        ]
        canvas = Image.new(
            "RGB", (width, header_h + row_h * len(page_objects) + margin), "#eeeae0"
        )
        draw = ImageDraw.Draw(canvas)
        font = ImageFont.load_default()
        draw.rectangle((0, 0, width, header_h - 12), fill="#242a28")
        draw.text((margin, 24), "PARK LEGO - MESHY EXACT-VARIANT CATALOG V3", fill="white", font=font)
        draw.text(
            (margin, 52),
            "ARCHETYPE REFERENCE  |  ISOLATED MULTIVIEW  |  GENERATED / NORMALIZED RUNTIME",
            fill="#c8d8cd",
            font=font,
        )
        status = (
            f"{review['generatedCount']} generated - {review['acceptedCount']} accepted - "
            f"{review['rejectedCount']} rejected - {review['creditsUsed']} credits "
            f"({review['balanceBefore']} -> {review['balanceAfter']})"
            if review
            else "PRE-NORMALIZATION VISUAL GATE - no people or large buildings permitted"
        )
        draw.text((margin, 82), status, fill="#acc2b2", font=font)
        draw.text((margin, 108), f"{batch['batchId']} - page {page_index + 1}/{page_count}", fill="#acc2b2", font=font)

        for row_index, item in enumerate(page_objects):
            top = header_h + row_index * row_h
            asset_id = item["assetId"]
            is_rejected = asset_id in rejected
            draw.rectangle(
                (18, top + 2, width - 18, top + row_h - 10),
                fill="#f8f5ed",
                outline="#b94a48" if is_rejected else "#a8b7ac",
                width=3,
            )
            object_dir = options.artifact_root / asset_id
            runtime = object_dir / "previews" / "front-three-quarter.png"
            thumbnail = object_dir / "meshy-thumbnail.png"
            panels = (
                image_panel(repo / item["references"][0], (cell_w, cell_h), cover=True),
                image_panel(object_dir / "multiview-1.png", (cell_w, cell_h), cover=False),
                image_panel(runtime if runtime.is_file() else thumbnail, (cell_w, cell_h), cover=False),
            )
            for column, panel in enumerate(panels):
                canvas.paste(panel, (margin + column * (cell_w + gap), top + 48))
            draw.text((margin, top + 16), asset_id, fill="#29332f", font=font)
            if is_rejected:
                verdict = f"REJECT - {rejected[asset_id]['reason']}"
                verdict_color = "#a12f2d"
            elif asset_id in accepted:
                verdict = f"ACCEPT - {item['placementRole']} - {item['dimensionsM']} m"
                verdict_color = "#287044"
            else:
                verdict = f"PENDING - {item['placementRole']} - {item['dimensionsM']} m"
                verdict_color = "#6b5b28"
            draw.text((width - 760, top + 16), verdict[:118], fill=verdict_color, font=font)
            draw.text(
                (margin, top + 324),
                f"{item['archetypeId']} / {', '.join(item['variantIds'])}",
                fill="#4c5752",
                font=font,
            )

        output = options.output_dir / f"{batch['batchId']}-page-{page_index + 1:02d}.png"
        canvas.save(output, optimize=True)
        print(output)


if __name__ == "__main__":
    main()
