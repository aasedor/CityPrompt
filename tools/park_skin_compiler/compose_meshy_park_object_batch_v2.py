"""Compose the mobile-friendly archetype -> Meshy -> runtime QA sheet for batch v2."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", required=True, type=Path)
    parser.add_argument(
        "--batch",
        type=Path,
        default=Path(__file__).with_name("meshy_park_object_batch_v2.json"),
    )
    parser.add_argument(
        "--review",
        type=Path,
        default=Path(__file__).with_name("meshy_park_object_batch_v2_review.json"),
    )
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def cover(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    ratio = max(size[0] / image.width, size[1] / image.height)
    image = image.resize((round(image.width * ratio), round(image.height * ratio)), Image.Resampling.LANCZOS)
    left = max(0, (image.width - size[0]) // 2)
    top = max(0, (image.height - size[1]) // 2)
    return image.crop((left, top, left + size[0], top + size[1]))


def contain(path: Path, size: tuple[int, int], background: str = "#222725") -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def main() -> None:
    options = args()
    repo = Path(__file__).resolve().parents[2]
    batch = json.loads(options.batch.resolve().read_text(encoding="utf-8"))
    review = json.loads(options.review.resolve().read_text(encoding="utf-8"))
    accepted = {item["assetId"]: item for item in review["accepted"]}
    rejected = {item["assetId"]: item for item in review["rejected"]}
    width, margin, gap, cell_w, cell_h = 1680, 34, 20, 510, 270
    row_h, header_h = 344, 150
    canvas = Image.new("RGB", (width, header_h + row_h * len(batch["objects"]) + margin), "#eeeae0")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.rectangle((0, 0, width, header_h - 12), fill="#242a28")
    draw.text((margin, 24), "PARK LEGO - MESHY ARCHETYPE OBJECT BATCH V2", fill="white", font=font)
    draw.text((margin, 52), "ARCHETYPE REFERENCE  |  ISOLATED MULTIVIEW  |  CLEAN 12K / 512 PBR RUNTIME GLB", fill="#c8d8cd", font=font)
    draw.text(
        (margin, 82),
        f"{review['generatedCount']} generated - {review['acceptedCount']} accepted - {review['rejectedCount']} rejected - "
        f"{review['creditsUsed']} credits ({review['balanceBefore']} -> {review['balanceAfter']}) - no people or buildings",
        fill="#acc2b2",
        font=font,
    )

    for index, item in enumerate(batch["objects"]):
        top = header_h + index * row_h
        asset_id = item["assetId"]
        is_rejected = asset_id in rejected
        draw.rectangle(
            (18, top + 2, width - 18, top + row_h - 10),
            fill="#f8f5ed",
            outline="#b94a48" if is_rejected else "#a8b7ac",
            width=3,
        )
        reference = repo / item["references"][0]
        object_dir = options.artifact_root / asset_id
        source = object_dir / "multiview-1.png"
        runtime = object_dir / "previews" / "front-three-quarter.png"
        thumbnail = object_dir / "meshy-thumbnail.png"
        panels = [
            cover(reference, (cell_w, cell_h)),
            contain(source, (cell_w, cell_h)),
            contain(runtime if runtime.is_file() else thumbnail, (cell_w, cell_h)),
        ]
        for column, panel in enumerate(panels):
            left = margin + column * (cell_w + gap)
            canvas.paste(panel, (left, top + 42))
        draw.text((margin, top + 16), asset_id, fill="#29332f", font=font)
        if is_rejected:
            verdict = f"REJECT - {rejected[asset_id]['reason']}"
        else:
            role = accepted[asset_id].get("registeredRole", item["placementRole"])
            verdict = f"ACCEPT - {role} - {item['dimensionsM']} m"
        draw.text((width - 720, top + 16), verdict[:112], fill="#a12f2d" if is_rejected else "#287044", font=font)
        for column, label in enumerate(("ARCHETYPE", "MESHY MULTIVIEW", "RUNTIME QA")):
            draw.text((margin + column * (cell_w + gap) + 8, top + 318), label, fill="#4c5752", font=font)

    options.output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(options.output, optimize=True)
    print(options.output)


if __name__ == "__main__":
    main()
