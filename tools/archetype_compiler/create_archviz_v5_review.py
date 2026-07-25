"""Create v5 review boards from the generated pilot, AI sources and references."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BG = "#0d1217"
CARD = "#172028"
LINE = "#34434e"
TEXT = "#f5f1e8"
MUTED = "#aab7c1"
GREEN = "#9be875"
BLUE = "#71c9ef"
AMBER = "#e9b968"


def font(size: int, bold: bool = False):
    root = Path("C:/Windows/Fonts")
    path = root / ("segoeuib.ttf" if bold else "segoeui.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def cover(path: Path, size: tuple[int, int], anchor_y: float = 0.48) -> Image.Image:
    image = Image.open(path).convert("RGB")
    scale = max(size[0] / image.width, size[1] / image.height)
    image = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    left = max(0, (image.width - size[0]) // 2)
    top = max(0, round((image.height - size[1]) * anchor_y))
    return image.crop((left, top, left + size[0], top + size[1]))


def contain(path: Path, size: tuple[int, int], fill: str = CARD) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, fill)
    result.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return result


def wrap(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, width: int, face, fill: str, gap: int = 5) -> int:
    line = ""
    rows: list[str] = []
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=face) <= width:
            line = trial
        else:
            rows.append(line)
            line = word
    if line:
        rows.append(line)
    for row in rows:
        draw.text((x, y), row, font=face, fill=fill)
        y += face.size + gap
    return y


def comparison(repo: Path, output: Path) -> Path:
    board = Image.new("RGB", (1920, 1080), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 28), "LEGO Archviz v5 · archetype fidelity + model-quality pilot", font=font(40, True), fill=TEXT)
    draw.text((48, 82), "Mass Timber Biophilic Infill · same procedural family, upgraded material and depth stack", font=font(20), fill=MUTED)
    sources = (
        ("ARCHETYPE IMAGE", repo / "frontend/public/archetypes/buildings/contemporary_midrise/variant_0.png"),
        ("V4 · PROCEDURAL PBR", repo / "build/lego-photoreal-v4/mass-timber/mass-timber-biophilic-tower_preview.png"),
        ("V5 · GPT MATERIALS + CYCLES", repo / "build/lego-archviz-v5/mass-timber/mass-timber-biophilic-tower_preview.png"),
    )
    x_positions = (48, 666, 1284)
    for index, ((label, path), x) in enumerate(zip(sources, x_positions)):
        draw.rounded_rectangle((x, 130, x + 588, 735), radius=18, fill=CARD, outline=LINE, width=2)
        board.paste(cover(path, (564, 520), 0.44), (x + 12, 142))
        draw.text((x + 18, 686), label, font=font(18, True), fill=GREEN if index == 2 else TEXT)
    draw.text((48, 782), "What changed", font=font(24, True), fill=GREEN)
    wrap(draw, "AI-derived engineered timber and room interiors; visible room depth behind dielectric glazing; varied window atlas cells by bay and level; botanical planter silhouettes; corrected non-flat AO; denoised Cycles QA.", 48, 823, 1130, font(21), TEXT)
    draw.text((1260, 782), "Verified output", font=font(24, True), fill=BLUE)
    wrap(draw, "139,640 triangles · 16 materials · 6 modular GLBs + assembled family · validation PASS · quality-first 11.9 MB assembled asset.", 1260, 823, 610, font(21), TEXT)
    draw.line((48, 1012, 1872, 1012), fill=LINE, width=2)
    draw.text((48, 1033), "V5 resembles the archetype in massing, timber grid, glazing rhythm, balcony pattern and green roof—not by pixel-copying the image.", font=font(18), fill=MUTED)
    path = output / "v5_archetype_comparison.png"
    board.save(path, optimize=True)
    return path


def materials(repo: Path, output: Path) -> Path:
    board = Image.new("RGB", (1920, 1080), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 28), "GPT Image as an architectural material source—not a pasted façade", font=font(40, True), fill=TEXT)
    draw.text((48, 82), "De-lit source → seam repair → calibrated PBR maps → UV-selected interior layers", font=font(20), fill=MUTED)
    root = repo / "tools/archetype_compiler/textures_archviz_v5"
    cards = (
        ("ENGINEERED TIMBER SOURCE", root / "clt/gpt-image-source.png", "Front elevation · 2 m coverage · albedo + normal + roughness"),
        ("EIGHT-ROOM INTERIOR ATLAS", root / "_shared/interior-atlas-gpt-v1.png", "Different cells appear behind recessed, coated glazing"),
        ("SEDUM ROOF SOURCE", root / "sedum_roof/gpt-image-source.png", "Top-down botanical variation · roof equipment remains geometry"),
    )
    x_positions = (48, 666, 1284)
    for (title, path, note), x in zip(cards, x_positions):
        draw.rounded_rectangle((x, 130, x + 588, 794), radius=18, fill=CARD, outline=LINE, width=2)
        board.paste(contain(path, (564, 520)), (x + 12, 142))
        draw.text((x + 18, 686), title, font=font(18, True), fill=GREEN)
        wrap(draw, note, x + 18, 723, 548, font(17), MUTED)
    draw.text((48, 842), "Why this works", font=font(24, True), fill=BLUE)
    wrap(draw, "The generated images supply difficult natural variation. Blender still controls physical scale, UVs, surface response, construction geometry, glass, AO and export. This keeps the model editable and lighting-aware.", 48, 884, 1140, font(21), TEXT)
    draw.text((1260, 842), "Production upgrade", font=font(24, True), fill=AMBER)
    wrap(draw, "Substance Sampler should replace luminance-derived normal/roughness for hero materials; KTX2 should follow before catalogue rollout.", 1260, 884, 610, font(21), TEXT)
    path = output / "v5_material_pipeline.png"
    board.save(path, optimize=True)
    return path


def quality_bar(repo: Path, output: Path, reference: Path) -> Path:
    board = Image.new("RGB", (1920, 1080), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 28), "Quality-bar comparison · capture-grade context vs authored real-time building", font=font(38, True), fill=TEXT)
    draw.text((48, 82), "The reference is a photogrammetric urban scene; v5 is a modular proposed-design asset rendered in an intentionally simple QA city.", font=font(19), fill=MUTED)
    left = cover(reference, (894, 638), 0.5)
    right = cover(repo / "build/lego-archviz-v5/mass-timber/mass-timber-biophilic-tower_aerial.png", (894, 638), 0.46)
    board.paste(left, (48, 126)); board.paste(right, (978, 126))
    draw.rectangle((48, 126, 942, 764), outline=LINE, width=2)
    draw.rectangle((978, 126, 1872, 764), outline=LINE, width=2)
    draw.text((66, 724), "REFERENCE · PHOTOGRAMMETRY", font=font(18, True), fill=TEXT)
    draw.text((996, 724), "V5 · AUTHORED GLTF / CYCLES QA", font=font(18, True), fill=GREEN)
    draw.text((48, 810), "Closest route to the reference", font=font(24, True), fill=BLUE)
    wrap(draw, "Keep the real terrain, trees and surrounding city from Photorealistic 3D Tiles; clip the scanned source building; seat this authored GLB on terrain. For an existing hero building, use photogrammetry/LiDAR rather than procedural reconstruction.", 48, 852, 1824, font(21), TEXT)
    draw.line((48, 1012, 1872, 1012), fill=LINE, width=2)
    draw.text((48, 1033), "The remaining visible gap is mostly context capture, unique silhouette/massing and delivery LOD—not another generic texture pass.", font=font(18), fill=AMBER)
    path = output / "v5_quality_bar.png"
    board.save(path, optimize=True)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--quality-reference", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (args.output or repo / "docs/lego_archviz_v5").resolve()
    output.mkdir(parents=True, exist_ok=True)
    for result in (comparison(repo, output), materials(repo, output), quality_bar(repo, output, args.quality_reference.resolve())):
        print(result)


if __name__ == "__main__":
    main()
