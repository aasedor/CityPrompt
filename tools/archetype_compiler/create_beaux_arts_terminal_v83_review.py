"""Build the bounded V82-versus-V83 Beaux-Arts terminal review boards."""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps


REPO = Path(__file__).resolve().parents[2]
V82 = REPO / "artifacts/video-lessons-v82/beaux-arts-terminal"
V83 = REPO / "artifacts/video-lessons-v83/beaux-arts-terminal"
REFERENCE = REPO / "frontend/public/archetypes/buildings/intermodal-transit-hub"
OUTPUT = REPO / "docs/reviews/beaux-arts-terminal-surface-story-v83"
FAMILY_82 = "beaux-arts-terminal-video-lessons-v82"
FAMILY_83 = "beaux-arts-terminal-surface-story-v83"


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    candidates = [Path("C:/Windows/Fonts") / name, Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


TITLE = font(34, bold=True)
LABEL = font(23, bold=True)
BODY = font(18)


def panel(path: Path, size: tuple[int, int], label: str, note: str) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image = ImageOps.fit(image, (size[0], size[1] - 78), method=Image.Resampling.LANCZOS)
    card = Image.new("RGB", size, "#15191d")
    card.paste(image, (0, 78))
    draw = ImageDraw.Draw(card)
    draw.text((16, 10), label, font=LABEL, fill="#f1eee7")
    draw.text((16, 43), note, font=BODY, fill="#adb8c2")
    return card


def board(title: str, cards: list[Image.Image], destination: Path) -> None:
    gap = 16
    margin = 24
    header = 72
    width = sum(card.width for card in cards) + gap * (len(cards) - 1) + margin * 2
    height = max(card.height for card in cards) + header + margin
    canvas = Image.new("RGB", (width, height), "#0d1013")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 18), title, font=TITLE, fill="#f6f2e9")
    x = margin
    for card in cards:
        canvas.paste(card, (x, header))
        x += card.width + gap
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, quality=95)


def difference_panel(source: Path, roundtrip: Path, size: tuple[int, int]) -> Image.Image:
    left = Image.open(source).convert("RGB")
    right = Image.open(roundtrip).convert("RGB").resize(left.size, Image.Resampling.LANCZOS)
    delta = np.abs(np.asarray(left, dtype=np.int16) - np.asarray(right, dtype=np.int16)).mean(axis=2)
    heat = np.zeros((*delta.shape, 3), dtype=np.uint8)
    strength = np.clip(delta * 7.0, 0, 255).astype(np.uint8)
    heat[..., 0] = strength
    heat[..., 1] = (strength * 0.35).astype(np.uint8)
    heat[..., 2] = (255 - strength) // 8
    image = Image.fromarray(heat, "RGB")
    image = ImageEnhance.Contrast(image).enhance(1.15)
    temp = OUTPUT / "_difference.png"
    image.save(temp)
    result = panel(temp, size, "Absolute difference", "99.23% mean pixel similarity")
    temp.unlink()
    return result


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    size = (570, 520)
    board(
        "V83 surface-story pilot — archetype versus controlled baseline",
        [
            panel(REFERENCE / "variant_1.png", size, "Archetype", "ornamented stone, deep glass, layered tower"),
            panel(V82 / f"{FAMILY_82}_archetype_match.png", size, "V82 baseline", "correct massing; uniform surfaces and plain tower"),
            panel(V83 / f"{FAMILY_83}_archetype_match.png", size, "V83 pilot", "baked stone courses, patina bands, tower hierarchy"),
        ],
        OUTPUT / "01-archetype-before-after.png",
    )
    board(
        "Roof and non-boxy massing — reference versus pipeline passes",
        [
            panel(REFERENCE / "variant_1_angle_90.jpg", size, "Archetype roof plan", "pale mineral terrace + framed glass barrel vault"),
            panel(V82 / f"{FAMILY_82}_roof_audit.png", size, "V82 roof audit", "flat uniform headhouse surface"),
            panel(V83 / f"{FAMILY_83}_roof_audit.png", size, "V83 roof audit", "mineral variation + side/rear parapets"),
        ],
        OUTPUT / "02-roof-before-after.png",
    )
    board(
        "Neutral material/export QA — Blender source versus imported GLB",
        [
            panel(V83 / "neutral_source.png", size, "Source .blend", "plain studio lighting; no context or colour grade"),
            panel(V83 / "neutral_glb_roundtrip.png", size, "Re-imported GLB", "same camera and lighting after catalogue export"),
            difference_panel(V83 / "neutral_source.png", V83 / "neutral_glb_roundtrip.png", size),
        ],
        OUTPUT / "03-neutral-glb-parity.png",
    )
    for filename in (
        f"{FAMILY_83}_archetype_match.png",
        f"{FAMILY_83}_aerial.png",
        f"{FAMILY_83}_facade_close.png",
        "surface_finish_report.json",
    ):
        shutil.copy2(V83 / filename, OUTPUT / filename)
    print(OUTPUT)


if __name__ == "__main__":
    main()
