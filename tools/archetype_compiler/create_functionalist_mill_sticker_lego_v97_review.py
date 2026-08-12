"""Publish exact-reference and three-tier LEGO review boards for V97."""
from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
SOURCE = Path(r"C:\dev-artifacts\3D-Maps\functional-mill-v97-v3")
OUT = REPO / "docs/reviews/catalogue-rollout-v97/functionalist-mill-sticker-lego-pilot"
REF = REPO / "frontend/public/archetypes/buildings/functionalist_brick_industrial"
FONT = ImageFont.truetype("arial.ttf", 30)
SMALL_FONT = ImageFont.truetype("arial.ttf", 21)


def render(size_id: str, role: str) -> Path:
    return SOURCE / size_id / f"functionalist-brick-mill-v97-{size_id}_{role}.png"


def panel(path: Path, size: tuple[int, int], label: str) -> Image.Image:
    with Image.open(path) as source:
        content = ImageOps.contain(source.convert("RGB"), (size[0] - 24, size[1] - 78))
    result = Image.new("RGB", size, "#f2efe9")
    result.paste(content, ((size[0] - content.width) // 2, 58 + (size[1] - 78 - content.height) // 2))
    ImageDraw.Draw(result).text((16, 15), label, fill="#1b2023", font=SMALL_FONT)
    return result


def board(name: str, title: str, items: list[tuple[Path, str]]) -> None:
    panel_width, panel_height = 900, 650
    result = Image.new("RGB", (panel_width * len(items), panel_height + 72), "#d6dade")
    ImageDraw.Draw(result).text((24, 18), title, fill="#131719", font=FONT)
    for index, (path, label) in enumerate(items):
        result.paste(panel(path, (panel_width, panel_height), label), (index * panel_width, 72))
    result.save(OUT / name, quality=95)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for size_id in ("small", "canonical", "large"):
        for role in ("archetype_match", "front_corner_oblique", "facade_close", "roof_audit"):
            shutil.copy2(render(size_id, role), OUT / f"render-{size_id}-{role}.png")
    board("01-canonical-archetype-comparison.png", "V97 — exact Functionalist mill archetype comparison", [
        (REF / "variant_1.png", "Exact archetype — street identity"),
        (render("canonical", "archetype_match"), "Canonical — 50 × 40 m / 5 floors"),
        (render("canonical", "facade_close"), "Canonical — bay/sticker registration close-up"),
    ])
    board("02-lego-size-matrix-street.png", "V97 — discrete LEGO size matrix (constant 5 m modules)", [
        (render("small", "archetype_match"), "Small — 35 × 30 m / 4 floors / 149 carriers"),
        (render("canonical", "archetype_match"), "Canonical — 50 × 40 m / 5 floors / 232 carriers"),
        (render("large", "archetype_match"), "Large — 65 × 50 m / 6 floors / 335 carriers"),
    ])
    board("03-lego-size-matrix-roof.png", "V97 — roof closure and fixed identity across sizes", [
        (render("small", "roof_audit"), "Small — closed three-face hip ends"),
        (render("canonical", "roof_audit"), "Canonical — repeatable 5 m roof strips"),
        (render("large", "roof_audit"), "Large — fixed three-chimney identity"),
    ])
    board("04-oblique-reference-and-extremes.png", "V97 — oblique massing at both LEGO extremes", [
        (REF / "variant_1_angle_60.jpg", "Exact oblique archetype"),
        (render("small", "front_corner_oblique"), "Small oblique"),
        (render("large", "front_corner_oblique"), "Large oblique"),
    ])


if __name__ == "__main__":
    main()
