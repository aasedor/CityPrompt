"""Create archetype-v7-v8 comparison boards for the signature-geometry pilot."""
from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TOOL_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOL_DIR.parents[1]
V8_INDEX = REPO_ROOT / "build" / "worldclass-v8" / "worldclass-library-index.json"
V7_INDEX = REPO_ROOT / "build" / "worldclass-v7" / "worldclass-library-index.json"
INK, MUTED, PAPER, CARD, LINE = "#101b2b", "#647084", "#f5f1e9", "#fffdf8", "#d8d0c2"
ACCENT, SUCCESS = "#9bd63a", "#42770b"


def font(size: int, bold: bool = False):
    candidates = (
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def contain(path: Path | None, size: tuple[int, int]) -> Image.Image:
    if not path or not path.exists():
        return Image.new("RGB", size, "#dedad2")
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, "#e9e6df")
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def reference_path(family_dir: Path) -> Path | None:
    grammar = json.loads((family_dir / "grammar.json").read_text(encoding="utf-8"))
    relative = str((grammar.get("source") or {}).get("thumbnail_url") or "").lstrip("/")
    candidate = REPO_ROOT / "frontend" / "public" / relative
    if candidate.exists():
        return candidate
    folder = candidate.parent
    for pattern in ("variant_0_thumb.jpg", "variant_0.png", "*_thumb.jpg", "variant_*.png"):
        matches = [folder / pattern] if "*" not in pattern else sorted(folder.glob(pattern))
        for match in matches:
            if match.exists():
                return match
    return None


def preview_path(item: dict | None) -> Path | None:
    if not item:
        return None
    return REPO_ROOT / item["output_directory"] / str(item.get("preview") or "")


def card(item: dict, v7: dict | None, width: int = 1016, height: int = 500) -> Image.Image:
    canvas = Image.new("RGB", (width, height), CARD)
    draw = ImageDraw.Draw(canvas)
    family_dir = REPO_ROOT / item["output_directory"]
    grammar = json.loads((family_dir / "grammar.json").read_text(encoding="utf-8"))
    signature = grammar.get("architectural_signature") or {}
    label = item["archetype_id"].replace("_", " ").title()
    draw.text((24, 15), label, fill=INK, font=font(23, True))
    identity = str(signature.get("identity") or "")
    draw.text((24, 47), textwrap.shorten(identity, width=132, placeholder="…"), fill=MUTED, font=font(13))

    image_y, image_h, pane_w, gap = 78, 292, 306, 17
    images = (
        ("ARCHETYPE", reference_path(family_dir)),
        ("V7 BASELINE", preview_path(v7)),
        ("V8 SIGNATURE", preview_path(item)),
    )
    for index, (caption, path) in enumerate(images):
        x = 24 + index * (pane_w + gap)
        canvas.paste(contain(path, (pane_w, image_h)), (x, image_y))
        draw.rectangle((x, image_y, x + pane_w - 1, image_y + image_h - 1), outline=LINE, width=2)
        tab_w = 128 if index else 108
        draw.rectangle((x, image_y, x + tab_w, image_y + 29), fill=INK if index < 2 else SUCCESS)
        draw.text((x + 9, image_y + 6), caption, fill="white", font=font(12, True))

    kits = signature.get("kits") or []
    draw.text((24, 390), "SIGNATURE KITS", fill=SUCCESS, font=font(13, True))
    draw.text((24, 414), "  ·  ".join(str(kit).replace("_", " ") for kit in kits), fill=INK, font=font(13))
    triangles = item.get("triangle_count") or 0
    metrics = f"{item.get('module_count', 0)} reusable modules  ·  {triangles:,} assembled triangles  ·  facade-sheet@3"
    draw.text((24, 450), metrics, fill=MUTED, font=font(13))
    draw.text((24, 474), "CITY PROMPT READY" if item.get("city_prompt_ready") else "CHECK BUILD",
              fill=SUCCESS if item.get("city_prompt_ready") else "#a33a2d", font=font(13, True))
    return canvas


def assemble(cards: list[Image.Image], columns: int, title: str) -> Image.Image:
    gap, margin, header_h = 22, 26, 154
    card_w, card_h = cards[0].size
    rows = (len(cards) + columns - 1) // columns
    width = margin * 2 + columns * card_w + (columns - 1) * gap
    height = header_h + margin + rows * card_h + (rows - 1) * gap + margin
    board = Image.new("RGB", (width, height), PAPER)
    draw = ImageDraw.Draw(board)
    draw.text((32, 24), title, fill=INK, font=font(35, True))
    subtitle = ("Catalogue archetype, v7 facade-sheet baseline, and v8 result with archetype-specific "
                "signature geometry plus podium / alternate-floor / crown Gemini bands.")
    draw.text((34, 75), subtitle, fill=MUTED, font=font(16))
    draw.rectangle((32, 127, width - 32, 134), fill=ACCENT)
    for index, item in enumerate(cards):
        x = margin + (index % columns) * (card_w + gap)
        y = header_h + margin + (index // columns) * (card_h + gap)
        board.paste(item, (x, y))
    return board


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v8-index", type=Path, default=V8_INDEX)
    parser.add_argument("--v7-index", type=Path, default=V7_INDEX)
    parser.add_argument("--out", type=Path, default=REPO_ROOT / "build" / "worldclass-v8" / "gallery")
    args = parser.parse_args()
    v8 = json.loads(args.v8_index.resolve().read_text(encoding="utf-8"))["families"]
    v7_payload = json.loads(args.v7_index.resolve().read_text(encoding="utf-8")) if args.v7_index.exists() else {}
    v7 = {item["archetype_id"]: item for item in v7_payload.get("families") or []}
    cards = [card(item, v7.get(item["archetype_id"])) for item in v8]
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    master = assemble(cards, 3, "Architect-Wow LEGO Library v8 · 20-family comparison")
    master_path = out / "architect-wow-v8-archetype-v7-v8.png"
    master.save(master_path, optimize=True)
    for start in range(0, len(cards), 4):
        page = assemble(cards[start:start + 4], 2, f"Architect-Wow v8 · Review board {start // 4 + 1}")
        page.save(out / f"architect-wow-v8-review-{start // 4 + 1:02d}.png", optimize=True)
    print(master_path)


if __name__ == "__main__":
    main()
