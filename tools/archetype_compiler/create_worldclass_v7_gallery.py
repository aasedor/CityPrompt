"""Create archetype-vs-model review boards for the twenty-family v7 build."""
from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parents[1]
DEFAULT_INDEX = REPO_ROOT / "build" / "worldclass-v7" / "worldclass-library-index.json"

INK = "#101b2b"
MUTED = "#647084"
PAPER = "#f5f1e9"
CARD = "#fffdf8"
LINE = "#d8d0c2"
ACCENT = "#9bd63a"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    names = (
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    )
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def contain(image: Image.Image, size: tuple[int, int], background: str = "#e9e6df") -> Image.Image:
    image = image.convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def reference_path(family_dir: Path) -> Path | None:
    grammar_path = family_dir / "grammar.json"
    if not grammar_path.exists():
        return None
    grammar = json.loads(grammar_path.read_text(encoding="utf-8"))
    relative = str((grammar.get("source") or {}).get("thumbnail_url") or "").lstrip("/")
    candidate = REPO_ROOT / "frontend" / "public" / relative
    if relative and candidate.exists():
        return candidate
    # Some older catalogue entries advertise ``hero.png`` while their checked-in
    # card set is named ``variant_0_thumb.jpg`` / ``variant_0.png``. Keep the
    # comparison board useful by resolving the real first variant in that folder.
    folder = candidate.parent
    if folder.exists():
        preferred = (
            "variant_0_thumb.jpg", "variant_0_thumb.png",
            "variant_0.png", "variant_0.jpg",
        )
        for name in preferred:
            fallback = folder / name
            if fallback.exists():
                return fallback
        for pattern in ("*_thumb.jpg", "*_thumb.png", "variant_*.png", "variant_*.jpg"):
            fallback = next(iter(sorted(folder.glob(pattern))), None)
            if fallback:
                return fallback
    return None


def card(item: dict, width: int = 780, height: int = 500) -> Image.Image:
    canvas = Image.new("RGB", (width, height), CARD)
    draw = ImageDraw.Draw(canvas)
    family_dir = REPO_ROOT / item["output_directory"]
    label = item["archetype_id"].replace("_", " ").title()
    draw.text((24, 18), label, fill=INK, font=font(24, True))
    draw.text((24, 50), item.get("group", ""), fill=MUTED, font=font(15))

    image_y, image_h, pane_w, gap = 82, 316, 354, 20
    ref = reference_path(family_dir)
    if ref:
        reference = contain(Image.open(ref), (pane_w, image_h))
    else:
        reference = Image.new("RGB", (pane_w, image_h), "#dedad2")
    preview = family_dir / str(item.get("preview") or "")
    if preview.exists():
        model = contain(Image.open(preview), (pane_w, image_h))
    else:
        model = Image.new("RGB", (pane_w, image_h), "#dedad2")
    left, right = 24, 24 + pane_w + gap
    canvas.paste(reference, (left, image_y))
    canvas.paste(model, (right, image_y))
    draw.rectangle((left, image_y, left + pane_w - 1, image_y + image_h - 1), outline=LINE, width=2)
    draw.rectangle((right, image_y, right + pane_w - 1, image_y + image_h - 1), outline=LINE, width=2)
    draw.rectangle((left, image_y, left + 112, image_y + 29), fill=INK)
    draw.text((left + 10, image_y + 6), "ARCHETYPE", fill="white", font=font(13, True))
    draw.rectangle((right, image_y, right + 122, image_y + 29), fill=INK)
    draw.text((right + 10, image_y + 6), "V7 MODEL", fill="white", font=font(13, True))

    status = "CITY PROMPT READY" if item.get("city_prompt_ready") else "CHECK BUILD"
    status_colour = "#42770b" if item.get("city_prompt_ready") else "#a33a2d"
    draw.text((24, 416), status, fill=status_colour, font=font(15, True))
    triangles = item.get("triangle_count")
    metrics = f"{item.get('module_count', 0)} reusable modules"
    if triangles:
        metrics += f"  ·  {triangles:,} assembled triangles"
    draw.text((24, 444), metrics, fill=INK, font=font(15))
    sheet_manifest = REPO_ROOT / item["facade_sheet_directory"] / "manifest.json"
    if sheet_manifest.exists():
        sheet = json.loads(sheet_manifest.read_text(encoding="utf-8"))
        model_name = str(sheet.get("model") or "generated facade")
        draw.text((24, 469), f"Facade: {model_name} · rectified repeatable bands", fill=MUTED, font=font(13))
    return canvas


def title_block(width: int, title: str, subtitle: str) -> Image.Image:
    header = Image.new("RGB", (width, 150), PAPER)
    draw = ImageDraw.Draw(header)
    draw.text((32, 24), title, fill=INK, font=font(35, True))
    for line_index, line in enumerate(textwrap.wrap(subtitle, width=108)):
        draw.text((34, 75 + line_index * 24), line, fill=MUTED, font=font(17))
    draw.rectangle((32, 127, width - 32, 134), fill=ACCENT)
    return header


def assemble(cards: list[Image.Image], columns: int, title: str, subtitle: str) -> Image.Image:
    gap, margin = 24, 28
    card_w, card_h = cards[0].size
    rows = (len(cards) + columns - 1) // columns
    width = margin * 2 + columns * card_w + (columns - 1) * gap
    height = 150 + margin + rows * card_h + (rows - 1) * gap + margin
    board = Image.new("RGB", (width, height), PAPER)
    board.paste(title_block(width, title, subtitle), (0, 0))
    for index, item in enumerate(cards):
        x = margin + (index % columns) * (card_w + gap)
        y = 150 + margin + (index // columns) * (card_h + gap)
        board.paste(item, (x, y))
    return board


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX)
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "build" / "worldclass-v7" / "gallery")
    args = parser.parse_args()
    index = json.loads(args.index.resolve().read_text(encoding="utf-8"))
    families = index.get("families") or []
    if not families:
        raise SystemExit("index contains no completed families")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    cards = [card(item) for item in families]
    subtitle = (
        "Catalogue archetype reference beside the generated modular GLB. Surface fidelity comes from "
        "Gemini rectified facade sheets; roofs, setbacks, cornices, canopies and key projections remain 3D."
    )
    master = assemble(cards, 4, "World-Class LEGO Library v7", subtitle)
    master_path = out / "worldclass-v7-archetype-comparison.png"
    master.save(master_path, optimize=True)
    for start in range(0, len(cards), 6):
        page_number = start // 6 + 1
        page = assemble(cards[start:start + 6], 2, f"V7 Comparison Board · {page_number}", subtitle)
        page.save(out / f"worldclass-v7-comparison-{page_number:02d}.png", optimize=True)
    print(master_path)


if __name__ == "__main__":
    main()
