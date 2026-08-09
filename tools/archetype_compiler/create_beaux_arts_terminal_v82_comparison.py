"""Publish the bounded V82 Blender-video-lessons terminal review set."""
from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO = Path(__file__).resolve().parents[2]
ARTIFACTS = REPO / "artifacts" / "video-lessons-v82" / "beaux-arts-terminal"
OUTPUT = REPO / "docs" / "reviews" / "beaux-arts-terminal-video-lessons-v82"
FAMILY = "beaux-arts-terminal-video-lessons-v82"
REFERENCE = REPO / "frontend" / "public" / "archetypes" / "buildings" / "intermodal-transit-hub"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def cover(path: Path, size: tuple[int, int], background: str = "#20272d") -> Image.Image:
    image = Image.open(path).convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    image = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = max(0, (image.width - size[0]) // 2)
    top = max(0, (image.height - size[1]) // 2)
    return image.crop((left, top, left + size[0], top + size[1]))


def contain(path: Path, size: tuple[int, int], background: str = "#20272d") -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def generated(view: str) -> Path:
    return ARTIFACTS / f"{FAMILY}_{view}.png"


def publish_files() -> None:
    generated_dir = OUTPUT / "generated"
    reports_dir = OUTPUT / "reports"
    generated_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    for view in (
        "preview", "archetype_match", "street", "front_corner_oblique",
        "rear_corner_oblique", "facade_close", "roof_audit", "aerial", "context",
    ):
        destination = generated_dir / f"{FAMILY}_{view}_eevee.png"
        if view != "preview" or not destination.exists():
            shutil.copy2(generated(view), destination)
    manifest = json.loads((ARTIFACTS / f"{FAMILY}_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("generator", {}).get("render_engine") == "CYCLES":
        shutil.copy2(generated("preview"), generated_dir / f"{FAMILY}_preview_cycles.png")
    for name in ("validation_report.json", "production_preflight.json"):
        shutil.copy2(ARTIFACTS / name, reports_dir / name)


def identity_board() -> Path:
    width, height = 2400, 1030
    board = Image.new("RGB", (width, height), "#11161b")
    draw = ImageDraw.Draw(board)
    draw.text((55, 28), "V82 Beaux-Arts terminal - archetype identity audit", font=font(42, True), fill="#f5f1e8")
    draw.text(
        (55, 86),
        "Modular arched orders | true entrance tunnels | occupied glazing | fixed clock landmark",
        font=font(23), fill="#aeb8c2",
    )
    tile = (750, 700)
    x_values = (35, 825, 1615)
    board.paste(cover(REFERENCE / "variant_1.png", tile), (x_values[0], 150))
    board.paste(contain(generated("archetype_match"), tile), (x_values[1], 150))
    board.paste(contain(generated("facade_close"), tile), (x_values[2], 150))
    labels = ("EXACT ARCHETYPE", "GENERATED EEVEE", "SECTION / MATERIAL CLOSE-UP")
    for x, label in zip(x_values, labels):
        draw.text((x + 12, 875), label, font=font(20, True), fill="#e8dcc6")
    finding = (
        "PROVISIONAL KEEPER - The two arched orders, offset clock tower and trainshed silhouette are image-faithful. "
        "The remaining gap is fine carved ornament and more legible warm activity behind the large upper glass."
    )
    draw.multiline_text(
        (55, 925), "\n".join(textwrap.wrap(finding, width=150)),
        font=font(21), fill="#d5dde4", spacing=7,
    )
    path = OUTPUT / "01-archetype-identity-comparison.png"
    board.save(path, optimize=True)
    return path


def roof_section_board() -> Path:
    width, height = 2400, 1420
    board = Image.new("RGB", (width, height), "#11161b")
    draw = ImageDraw.Draw(board)
    draw.text((55, 28), "V82 roof, side-depth and presentation audit", font=font(42, True), fill="#f5f1e8")
    draw.text(
        (55, 86),
        "Glass and metal are separate roof fields; iron ribs and purlins remain visible without an opaque backing",
        font=font(23), fill="#aeb8c2",
    )
    tile = (750, 540)
    x_values = (35, 825, 1615)
    rows = (
        (150, REFERENCE / "variant_1_angle_60.jpg", generated("aerial"), generated("rear_corner_oblique"),
         ("EXACT OBLIQUE", "GENERATED AERIAL", "GENERATED REAR / SIDE")),
        (790, REFERENCE / "variant_1_angle_90.jpg", generated("roof_audit"), generated("context"),
         ("EXACT ROOF PLAN", "GENERATED ROOF AUDIT", "GENERATED CONTEXT")),
    )
    for y, left, middle, right, labels in rows:
        board.paste(cover(left, tile), (x_values[0], y))
        board.paste(contain(middle, tile), (x_values[1], y))
        board.paste(contain(right, tile), (x_values[2], y))
        for x, label in zip(x_values, labels):
            draw.text((x + 12, y + 560), label, font=font(19, True), fill="#e8dcc6")
    path = OUTPUT / "02-roof-section-presentation-audit.png"
    board.save(path, optimize=True)
    return path


def renderer_parity_board() -> Path:
    width, height = 2400, 1010
    board = Image.new("RGB", (width, height), "#11161b")
    draw = ImageDraw.Draw(board)
    draw.text((55, 28), "V82 material parity - exact image, Eevee and Cycles", font=font(42, True), fill="#f5f1e8")
    draw.text(
        (55, 86),
        "Cycles reveals transmitted warm depth; Eevee remains the conservative automated/runtime proxy",
        font=font(23), fill="#aeb8c2",
    )
    tile = (750, 700)
    x_values = (35, 825, 1615)
    eevee = OUTPUT / "generated" / f"{FAMILY}_preview_eevee.png"
    cycles = OUTPUT / "generated" / f"{FAMILY}_preview_cycles.png"
    board.paste(cover(REFERENCE / "variant_1.png", tile), (x_values[0], 150))
    board.paste(contain(eevee, tile), (x_values[1], 150))
    board.paste(contain(cycles, tile), (x_values[2], 150))
    for x, label in zip(x_values, ("EXACT ARCHETYPE", "EEVEE 64 SAMPLES", "CYCLES 32 SAMPLES")):
        draw.text((x + 12, 875), label, font=font(20, True), fill="#e8dcc6")
    draw.text(
        (55, 930),
        "Inference: the geometry and physical material are working; upper-interior readability is mainly a real-time parity problem, while fine ornament is still a modeling gap.",
        font=font(20), fill="#d5dde4",
    )
    path = OUTPUT / "03-eevee-cycles-material-parity.png"
    board.save(path, optimize=True)
    return path


def write_review() -> None:
    summary = {
        "schema": "building-video-lessons-review@1",
        "pipeline_version": "v82",
        "family": FAMILY,
        "status": "provisional_keeper",
        "methods_proven": [
            "fixed landmark modules are separated from repeatable bay and rib modules",
            "physical roof glass occupies a distinct field with no opaque backing",
            "ground entrances are real through-passages with recessed doors and a shallow concourse",
            "medium-scale iron purlins, facade pilasters, cornice blocks and side windows prevent flat massing",
            "presentation lighting is an explicit recipe contract and does not enter the exported GLB",
            "metadata is selective and admitted only where all exact images agree",
        ],
        "remaining_gaps": [
            "fine carved Beaux-Arts ornament remains below the exact archetype",
            "upper-window interiors need stronger room-readable parallax in Eevee and runtime Three.js",
            "132272 triangles, 15 materials and 10.4 MB require a quality-preserving optimization pass",
            "City Prompt/Three.js still needs to be compared against the now-documented Cycles and Eevee baselines",
        ],
        "validation": "pass_with_budget_warnings",
    }
    (OUTPUT / "review-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    readme = """# Beaux-Arts terminal - V82 video-lessons pilot

Status: **provisional keeper**.

This bounded pilot applies the Blender-video synthesis to one reference-rich archetype. The exact images, not generic metadata, determine the long limestone headhouse, five upper arches, nine tunnel-like ground entrances, offset clock tower, red-brick trainshed walls, and the barrel roof's metal/glass/metal depth sequence.

The result fixes the prior structural failures: glass is not placed on an opaque roof, entrances are genuine spatial recesses, long side walls carry image-consistent glazing and depth, and the building is composed from explicit fixed and repeatable modules. It still needs a later ornament bake and a quality-preserving mesh/material consolidation before catalogue release.

The Cycles/Eevee audit confirms that the physical material and interior section work in the path tracer; the remaining dark-window gap is primarily real-time parity, while carved ornament remains a genuine modeling gap.

See `01-archetype-identity-comparison.png`, `02-roof-section-presentation-audit.png`, `03-eevee-cycles-material-parity.png`, and `review-summary.json`.
"""
    (OUTPUT / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    publish_files()
    identity = identity_board()
    roof = roof_section_board()
    parity = renderer_parity_board()
    write_review()
    print(identity)
    print(roof)
    print(parity)


if __name__ == "__main__":
    main()
