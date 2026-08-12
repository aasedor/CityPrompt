"""Publish the approved Daylight Sawtooth Factory V98 evidence package."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "frontend/public/archetypes/buildings/daylight_factory"
CANONICAL = Path(r"C:\dev-artifacts\3D-Maps\sticker-batch-01\daylight-sawtooth-v98\approved-canonical")
EXTENDED = Path(r"C:\dev-artifacts\3D-Maps\sticker-batch-01\daylight-sawtooth-v98\approved-extended")
OUTPUT = ROOT / "docs/reviews/catalogue-rollout-v98/sticker-method-batch-01/daylight-sawtooth-factory"


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    for name in ("arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _cover(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    image = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left, top = (image.width - size[0]) // 2, (image.height - size[1]) // 2
    return image.crop((left, top, left + size[0], top + size[1]))


def _contain(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    panel = Image.new("RGB", size, "#20262b")
    panel.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return panel


def _board(filename: str, title: str, items: list[tuple[Path, str]], cover: bool = True) -> None:
    panel_w, panel_h = 700, 540
    board = Image.new("RGB", (panel_w * len(items), panel_h + 112), "#e7e4dd")
    draw = ImageDraw.Draw(board)
    draw.text((32, 22), title, fill="#182026", font=_font(30, True))
    for index, (path, label) in enumerate(items):
        x = index * panel_w
        panel = _cover(path, (panel_w, panel_h)) if cover else _contain(path, (panel_w, panel_h))
        board.paste(panel, (x, 112))
        draw.rectangle((x, 76, x + panel_w, 112), fill="#182026")
        draw.text((x + 18, 82), label, fill="#ffffff", font=_font(20, True))
    board.save(OUTPUT / filename, optimize=True)


def _copy_and_machine_evidence() -> None:
    tiers = {}
    for tier, folder in (("canonical", CANONICAL), ("extended", EXTENDED)):
        family = f"daylight-sawtooth-factory-v98-{tier}"
        for view in ("archetype_match", "front_corner_oblique", "rear_corner_oblique", "facade_close", "roof_audit", "aerial"):
            shutil.copy2(folder / f"{family}_{view}.png", OUTPUT / f"render-{tier}-{view}.png")
        shutil.copy2(folder / "validation_report.json", OUTPUT / f"validation-{tier}.json")
        manifest = json.loads((folder / f"{family}_manifest.json").read_text(encoding="utf-8"))
        tiers[tier] = {
            "dimensions": manifest["dimensions"],
            "assembled": manifest["assembled"],
            "validation": json.loads((folder / "validation_report.json").read_text(encoding="utf-8"))["status"],
            "production_preflight": json.loads((folder / "production_preflight.json").read_text(encoding="utf-8"))["status"],
            "render_count": len(manifest["renders"]),
        }
    (OUTPUT / "machine-evidence.json").write_text(
        json.dumps({"schema": "siteforge.sticker-method-machine-evidence@1", "tiers": tiers}, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    _copy_and_machine_evidence()
    _board("01-exact-reference-comparison.png", "Daylight Sawtooth Factory V98 — exact identity comparison", [
        (REFERENCE / "variant_0.png", "EXACT ARCHETYPE"),
        (CANONICAL / "daylight-sawtooth-factory-v98-canonical_archetype_match.png", "CANONICAL · 60 × 40 m"),
        (EXTENDED / "daylight-sawtooth-factory-v98-extended_archetype_match.png", "EXTENDED · 80 × 40 m"),
    ])
    _board("02-oblique-reference-comparison.png", "Massing, singular dock and whole-tooth extension", [
        (REFERENCE / "variant_0_angle_60.jpg", "EXACT 60° REFERENCE"),
        (CANONICAL / "daylight-sawtooth-factory-v98-canonical_front_corner_oblique.png", "CANONICAL · SIX TEETH"),
        (EXTENDED / "daylight-sawtooth-factory-v98-extended_front_corner_oblique.png", "EXTENDED · EIGHT TEETH"),
    ])
    _board("03-roof-reference-comparison.png", "Same-handed northlights, physical grid and hollow chimney", [
        (REFERENCE / "variant_0_angle_90.jpg", "EXACT AERIAL REFERENCE"),
        (CANONICAL / "daylight-sawtooth-factory-v98-canonical_aerial.png", "CANONICAL AERIAL"),
        (EXTENDED / "daylight-sawtooth-factory-v98-extended_aerial.png", "EXTENDED AERIAL"),
    ], cover=False)
    _board("04-size-matrix-close.png", "Physical glazing, recessed workshop depth and constant material scale", [
        (CANONICAL / "daylight-sawtooth-factory-v98-canonical_facade_close.png", "CANONICAL CLOSE"),
        (EXTENDED / "daylight-sawtooth-factory-v98-extended_facade_close.png", "EXTENDED CLOSE"),
    ])


if __name__ == "__main__":
    main()
