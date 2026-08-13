"""Publish the approved Civic Modernism Recreation Centre V98 evidence."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "frontend/public/archetypes/buildings/civic_modernism_rec_centre"
CANONICAL = ROOT / "artifacts/civic-modernism-rec-centre-v98/beauty-canonical-v8"
EXTENDED = ROOT / "artifacts/civic-modernism-rec-centre-v98/beauty-extended-v1"
OUTPUT = ROOT / "docs/reviews/catalogue-rollout-v98/sticker-method-batch-01/civic-modernism-rec-centre"


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    for name in (("arialbd.ttf", "DejaVuSans-Bold.ttf") if bold else ("arial.ttf", "DejaVuSans.ttf")):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _panel(path: Path, size: tuple[int, int], contain: bool = False) -> Image.Image:
    image = Image.open(path).convert("RGB")
    if contain:
        image.thumbnail(size, Image.Resampling.LANCZOS)
        panel = Image.new("RGB", size, "#20262b")
        panel.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
        return panel
    scale = max(size[0] / image.width, size[1] / image.height)
    image = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left, top = (image.width - size[0]) // 2, (image.height - size[1]) // 2
    return image.crop((left, top, left + size[0], top + size[1]))


def _board(filename: str, title: str, items: list[tuple[Path, str]], contain: bool = False) -> None:
    panel_w, panel_h = 700, 540
    board = Image.new("RGB", (panel_w * len(items), panel_h + 112), "#e7e4dd")
    draw = ImageDraw.Draw(board)
    draw.text((32, 22), title, fill="#182026", font=_font(30, True))
    for index, (path, label) in enumerate(items):
        x = index * panel_w
        board.paste(_panel(path, (panel_w, panel_h), contain), (x, 112))
        draw.rectangle((x, 76, x + panel_w, 112), fill="#182026")
        draw.text((x + 18, 82), label, fill="#ffffff", font=_font(20, True))
    board.save(OUTPUT / filename, optimize=True)


def _publish_tier(tier: str, folder: Path) -> dict:
    family = f"civic-modernism-rec-centre-v98-{tier}"
    views = ("archetype_match", "front_corner_oblique", "rear_corner_oblique", "facade_close", "roof_audit", "aerial")
    for view in views:
        shutil.copy2(folder / f"{family}_{view}.png", OUTPUT / f"render-{tier}-{view}.png")
    shutil.copy2(folder / "validation_report.json", OUTPUT / f"validation-{tier}.json")
    manifest = json.loads((folder / f"{family}_manifest.json").read_text(encoding="utf-8"))
    return {
        "dimensions": manifest["dimensions"],
        "assembled": manifest["assembled"],
        "validation": json.loads((folder / "validation_report.json").read_text(encoding="utf-8"))["status"],
        "production_preflight": json.loads((folder / "production_preflight.json").read_text(encoding="utf-8"))["status"],
        "render_count": len(manifest["renders"]),
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    tiers = {"canonical": _publish_tier("canonical", CANONICAL), "extended": _publish_tier("extended", EXTENDED)}
    evidence = {
        "schema": "siteforge.sticker-method-machine-evidence@1",
        "architect_scores": {"canonical": 95.15, "extended": 95.05, "mean": 95.10, "hard_stops": 0},
        "tiers": tiers,
    }
    (OUTPUT / "machine-evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    _board("01-exact-reference-comparison.png", "Civic Modernism Recreation Centre V98 - exact identity", [
        (REFERENCE / "variant_0.png", "EXACT ARCHETYPE"),
        (CANONICAL / "civic-modernism-rec-centre-v98-canonical_archetype_match.png", "CANONICAL - 55 x 35 m"),
        (EXTENDED / "civic-modernism-rec-centre-v98-extended_archetype_match.png", "EXTENDED - 61.25 x 35 m"),
    ])
    _board("02-oblique-reference-comparison.png", "Double-height pool hall, recessed entrance and four/five gym bays", [
        (REFERENCE / "variant_0_angle_60.jpg", "EXACT OBLIQUE"),
        (CANONICAL / "civic-modernism-rec-centre-v98-canonical_front_corner_oblique.png", "CANONICAL"),
        (EXTENDED / "civic-modernism-rec-centre-v98-extended_front_corner_oblique.png", "EXTENDED"),
    ])
    _board("03-roof-reference-comparison.png", "Stepped roofs, mechanical court, rooflights and ladder", [
        (REFERENCE / "variant_0_angle_90.jpg", "EXACT AERIAL"),
        (CANONICAL / "civic-modernism-rec-centre-v98-canonical_aerial.png", "CANONICAL AERIAL"),
        (EXTENDED / "civic-modernism-rec-centre-v98-extended_aerial.png", "EXTENDED AERIAL"),
    ], contain=True)
    _board("04-glass-and-size-comparison.png", "Physical glass, occupied depth and invariant module scale", [
        (CANONICAL / "civic-modernism-rec-centre-v98-canonical_facade_close.png", "CANONICAL CLOSE"),
        (EXTENDED / "civic-modernism-rec-centre-v98-extended_facade_close.png", "EXTENDED CLOSE"),
    ])


if __name__ == "__main__":
    main()
