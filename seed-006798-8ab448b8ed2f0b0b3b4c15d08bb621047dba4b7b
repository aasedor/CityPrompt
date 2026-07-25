"""Create the tracked review boards for the Kinnaird-quality Lego pilot."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BG = "#0c1116"
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


def cover(path: Path, size: tuple[int, int], anchor_y: float = 0.5) -> Image.Image:
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


def comparison(reference: Path, render_root: Path, output: Path) -> Path:
    board = Image.new("RGB", (1920, 1080), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 26), "Kinnaird quality pilot - reference vs modular builder", font=font(38, True), fill=TEXT)
    draw.text((48, 79), "A design-language comparison, not a geometric copy of the source building", font=font(20), fill=MUTED)
    pilot = render_root / "london-heritage-mansion-portland-stone_preview.png"
    board.paste(cover(reference, (894, 610), 0.48), (48, 122))
    board.paste(cover(pilot, (894, 610), 0.44), (978, 122))
    draw.rectangle((48, 122, 942, 732), outline=LINE, width=2)
    draw.rectangle((978, 122, 1872, 732), outline=LINE, width=2)
    draw.text((66, 690), "REFERENCE - KINNAIRD HOUSE", font=font(18, True), fill=TEXT)
    draw.text((996, 690), "V6 - LEGO HERITAGE STONE KIT", font=font(18, True), fill=GREEN)

    columns = (
        (48, "REFERENCE DELIVERY", BLUE,
         "53.9k triangles / 30.1k vertices. Bespoke low-poly shell. 4K baked PBR textures plus two emissive variants."),
        (670, "MATCHED DESIGN READ", GREEN,
         "Base-body-crown hierarchy, dark multi-pane windows, rustication, pediments, dentilled cornice, dormers, chimneys, corner pavilions, portico and balustrade."),
        (1292, "PILOT DELIVERY", AMBER,
         "106.7k triangles / 9.1 MB assembled. Six reusable GLB modules. GPT-derived stone and slate PBR sources. 256 px baked AO per delivery module."),
    )
    for x, title, color, body in columns:
        draw.text((x, 774), title, font=font(21, True), fill=color)
        wrap(draw, body, x, 812, 580, font(19), TEXT)
    draw.line((48, 1008, 1872, 1008), fill=LINE, width=2)
    draw.text((48, 1028), "Honest gap: the pilot reaches the same architectural-detail category, but Kinnaird remains more efficient and has richer unique baked relief.",
              font=font(17), fill=MUTED)
    draw.text((1405, 1053), "Reference: 99.Miles / Sketchfab / CC BY", font=font(14), fill=MUTED)
    path = output / "v6_kinnaird_quality_comparison.png"
    board.save(path, optimize=True)
    return path


def views(render_root: Path, output: Path) -> Path:
    board = Image.new("RGB", (1920, 1080), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 26), "London Heritage Mansion Block - final Cycles review", font=font(38, True), fill=TEXT)
    draw.text((48, 79), "The same modular family at street, oblique and aerial review distances", font=font(20), fill=MUTED)
    family = "london-heritage-mansion-portland-stone"
    cards = (
        ("STREET DETAIL", render_root / f"{family}_street.png", 0.48),
        ("OBLIQUE HERO", render_root / f"{family}_preview.png", 0.44),
        ("AERIAL / ROOF", render_root / f"{family}_aerial.png", 0.40),
    )
    for x, (title, path, anchor) in zip((48, 666, 1284), cards):
        draw.rounded_rectangle((x, 126, x + 588, 824), radius=18, fill=CARD, outline=LINE, width=2)
        board.paste(cover(path, (564, 620), anchor), (x + 12, 138))
        draw.text((x + 18, 779), title, font=font(18, True), fill=GREEN)
    draw.text((48, 866), "Builder modules", font=font(23, True), fill=BLUE)
    wrap(draw, "Podium + two repeatable body variants + upper + crown + mansard roof. The roof module independently composes dormers, four occupied pavilions, chimneys, a lantern and lead top deck.",
         48, 904, 1120, font(20), TEXT)
    draw.text((1260, 866), "Validated pilot", font=font(23, True), fill=AMBER)
    wrap(draw, "25.9 m tall / 24 x 18 m footprint / 106,702 triangles / 9.1 MB / AO baked / validation PASS.",
         1260, 904, 610, font(20), TEXT)
    path = output / "v6_final_views.png"
    board.save(path, optimize=True)
    return path


def materials(texture_root: Path, output: Path) -> Path:
    board = Image.new("RGB", (1920, 1080), BG)
    draw = ImageDraw.Draw(board)
    draw.text((48, 26), "GPT Image material sources - editable PBR, not pasted facades", font=font(38, True), fill=TEXT)
    draw.text((48, 79), "Generated source -> deterministic seam repair -> albedo + normal + roughness -> metric box UVs", font=font(20), fill=MUTED)
    cards = (
        ("PORTLAND STONE SOURCE", texture_root / "heritage_portland_stone/gpt-image-source.png"),
        ("STONE DERIVED NORMAL", texture_root / "heritage_portland_stone/normal.png"),
        ("WELSH SLATE SOURCE", texture_root / "welsh_slate/gpt-image-source.png"),
    )
    for x, (title, path) in zip((48, 666, 1284), cards):
        draw.rounded_rectangle((x, 126, x + 588, 824), radius=18, fill=CARD, outline=LINE, width=2)
        board.paste(contain(path, (564, 620)), (x + 12, 138))
        draw.text((x + 18, 779), title, font=font(18, True), fill=GREEN)
    draw.text((48, 866), "Why the split matters", font=font(23, True), fill=BLUE)
    wrap(draw, "Image generation supplies believable mineral and slate variation. Blender retains control of physical scale, silhouette, reveals, frames, glazing, occupancy, AO and export, so every building remains relightable and modular.",
         48, 904, 1820, font(20), TEXT)
    path = output / "v6_material_pipeline.png"
    board.save(path, optimize=True)
    return path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--render-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    repo = args.repo.resolve()
    output = (args.output or repo / "docs/lego_kinnaird_v6").resolve()
    output.mkdir(parents=True, exist_ok=True)
    for result in (
        comparison(args.reference.resolve(), args.render_root.resolve(), output),
        views(args.render_root.resolve(), output),
        materials(repo / "tools/archetype_compiler/textures_kinnaird_v6", output),
    ):
        print(result)


if __name__ == "__main__":
    main()
