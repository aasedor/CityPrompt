"""Publish the approved Old Montreal V98 Sticker LEGO evidence package."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "frontend/public/archetypes/buildings/old-montreal-warehouse-loft"
CANONICAL = Path(r"C:\dev-artifacts\3D-Maps\sticker-batch-01\old-montreal-textile-v98\beauty-canonical-r11")
EXTENDED = Path(r"C:\dev-artifacts\3D-Maps\sticker-batch-01\old-montreal-textile-v98\beauty-extended-r11")
OUTPUT = ROOT / "docs/reviews/catalogue-rollout-v98/sticker-method-batch-01/old-montreal-textile-mill"


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    names = ["arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _cover(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - size[0]) // 2
    top = (resized.height - size[1]) // 2
    return resized.crop((left, top, left + size[0], top + size[1]))


def _contain(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    panel = Image.new("RGB", size, "#20262b")
    panel.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return panel


def _board(filename: str, title: str, items: list[tuple[Path, str]], *, cover: bool = True) -> None:
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


def _copy_evidence() -> None:
    sources = {
        "render-canonical-archetype_match.png": CANONICAL / "old-montreal-textile-mill-v98-canonical_archetype_match.png",
        "render-canonical-front_corner_oblique.png": CANONICAL / "old-montreal-textile-mill-v98-canonical_front_corner_oblique.png",
        "render-canonical-facade_close.png": CANONICAL / "old-montreal-textile-mill-v98-canonical_facade_close.png",
        "render-canonical-roof_audit.png": CANONICAL / "old-montreal-textile-mill-v98-canonical_roof_audit.png",
        "render-canonical-rear_corner_oblique.png": CANONICAL / "old-montreal-textile-mill-v98-canonical_rear_corner_oblique.png",
        "render-extended-archetype_match.png": EXTENDED / "old-montreal-textile-mill-v98-extended_archetype_match.png",
        "render-extended-front_corner_oblique.png": EXTENDED / "old-montreal-textile-mill-v98-extended_front_corner_oblique.png",
        "render-extended-facade_close.png": EXTENDED / "old-montreal-textile-mill-v98-extended_facade_close.png",
        "render-extended-roof_audit.png": EXTENDED / "old-montreal-textile-mill-v98-extended_roof_audit.png",
        "render-extended-rear_corner_oblique.png": EXTENDED / "old-montreal-textile-mill-v98-extended_rear_corner_oblique.png",
        "validation-canonical.json": CANONICAL / "validation_report.json",
        "validation-extended.json": EXTENDED / "validation_report.json",
    }
    for target, source in sources.items():
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, OUTPUT / target)


def _machine_evidence() -> None:
    tiers = {}
    for name, folder in (("canonical", CANONICAL), ("extended", EXTENDED)):
        manifest_path = next(folder.glob("*_manifest.json"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        tiers[name] = {
            "dimensions": manifest["dimensions"],
            "assembled": manifest["assembled"],
            "validation": json.loads((folder / "validation_report.json").read_text(encoding="utf-8"))["status"],
            "render_count": len(manifest["renders"]),
        }
    (OUTPUT / "machine-evidence.json").write_text(
        json.dumps({"schema": "siteforge.sticker-method-machine-evidence@1", "tiers": tiers}, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    _copy_evidence()
    _machine_evidence()
    _board(
        "01-exact-reference-comparison.png",
        "Old Montreal Textile Mill V98 — exact archetype comparison",
        [
            (REFERENCE / "variant_2.png", "EXACT ARCHETYPE"),
            (CANONICAL / "old-montreal-textile-mill-v98-canonical_archetype_match.png", "CANONICAL · 25 × 20 m · 96.0"),
            (EXTENDED / "old-montreal-textile-mill-v98-extended_archetype_match.png", "EXTENDED · 35 × 20 m · 95.5"),
        ],
    )
    _board(
        "02-oblique-reference-comparison.png",
        "Oblique massing, corner hierarchy and whole-bay extension",
        [
            (REFERENCE / "variant_2_angle_60.jpg", "EXACT 60° REFERENCE"),
            (CANONICAL / "old-montreal-textile-mill-v98-canonical_front_corner_oblique.png", "CANONICAL OBLIQUE"),
            (EXTENDED / "old-montreal-textile-mill-v98-extended_front_corner_oblique.png", "EXTENDED OBLIQUE"),
        ],
    )
    _board(
        "03-roof-reference-comparison.png",
        "Roof identity and all-surface coverage",
        [
            (REFERENCE / "variant_2_angle_90.jpg", "EXACT ROOF REFERENCE"),
            (CANONICAL / "old-montreal-textile-mill-v98-canonical_roof_audit.png", "CANONICAL ROOF AUDIT"),
            (EXTENDED / "old-montreal-textile-mill-v98-extended_roof_audit.png", "EXTENDED ROOF AUDIT"),
        ],
        cover=False,
    )
    _board(
        "04-size-matrix-close.png",
        "Floor stickers, openings and constant-scale surface treatment",
        [
            (CANONICAL / "old-montreal-textile-mill-v98-canonical_facade_close.png", "5-BAY CANONICAL"),
            (EXTENDED / "old-montreal-textile-mill-v98-extended_facade_close.png", "7-BAY EXTENDED"),
        ],
    )


if __name__ == "__main__":
    main()
