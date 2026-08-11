"""Publish exact-reference comparison boards for the Eixample V96 pilot."""
from __future__ import annotations

import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
SOURCE = Path(r"C:\dev-artifacts\3D-Maps\eixample-v96-clay-v2")
OUT = REPO / "docs/reviews/catalogue-rollout-v96/eixample-geometry-conditioned-sticker-pilot"
REF = REPO / "frontend/public/archetypes/buildings/eixample-apartment-block"
PREFIX = "eixample-apartment-block-v96-conditioned-4_"
FONT = ImageFont.truetype("arial.ttf", 30)
SMALL = ImageFont.truetype("arial.ttf", 22)


def _panel(path: Path, size: tuple[int, int], label: str) -> Image.Image:
    with Image.open(path) as image:
        content = ImageOps.contain(image.convert("RGB"), (size[0] - 24, size[1] - 74))
    panel = Image.new("RGB", size, "#f4f1eb")
    panel.paste(content, ((size[0] - content.width) // 2, 54 + (size[1] - 74 - content.height) // 2))
    ImageDraw.Draw(panel).text((16, 14), label, fill="#1f2528", font=SMALL)
    return panel


def _board(name: str, title: str, items: list[tuple[Path, str]]) -> None:
    width, height = 1024, 720
    board = Image.new("RGB", (width * len(items), height + 72), "#d9dde0")
    draw = ImageDraw.Draw(board)
    draw.text((24, 18), title, fill="#15191b", font=FONT)
    for index, (path, label) in enumerate(items):
        board.paste(_panel(path, (width, height), label), (index * width, 72))
    board.save(OUT / name, quality=95)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    renders = {
        role: SOURCE / f"{PREFIX}{role}.png"
        for role in ("archetype_match", "street", "front_corner_oblique", "rear_corner_oblique",
                     "facade_close", "roof_audit", "aerial", "context")
    }
    for role, source in renders.items():
        shutil.copy2(source, OUT / f"render-{role}.png")
    _board("01-street-archetype-comparison.png", "Eixample V96 — exact street identity",
           [(REF / "variant_0.png", "Exact archetype"), (renders["archetype_match"], "V96 archetype-match"),
            (renders["facade_close"], "V96 façade registration close-up")])
    _board("02-oblique-all-elevation-comparison.png", "Eixample V96 — massing and all-elevation continuity",
           [(REF / "variant_0_angle_60.jpg", "Exact oblique reference"),
            (renders["front_corner_oblique"], "V96 front corner"),
            (renders["rear_corner_oblique"], "V96 rear corner")])
    _board("03-roof-courtyard-comparison.png", "Eixample V96 — roof ring and open courtyard",
           [(REF / "variant_0_angle_90.jpg", "Exact aerial reference"),
            (renders["roof_audit"], "V96 roof audit"), (renders["aerial"], "V96 context aerial")])


if __name__ == "__main__":
    main()
