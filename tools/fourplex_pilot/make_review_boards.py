"""Assemble external 1080×1920 source/geometry review boards for this pilot."""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True, type=Path)
parser.add_argument("--renders", required=True, type=Path)
parser.add_argument("--output", required=True, type=Path)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)

SIZE = (1080, 1920)
BG = "#f5f3ef"
INK = "#24272b"
SUB = "#5b6165"
font_path = Path("C:/Windows/Fonts/arial.ttf")
bold_path = Path("C:/Windows/Fonts/arialbd.ttf")
def font(size: int, bold: bool = False):
    return ImageFont.truetype(str(bold_path if bold else font_path), size)

def base(title: str, subtitle: str):
    im = Image.new("RGB", SIZE, BG)
    draw = ImageDraw.Draw(im)
    draw.text((52, 48), title, fill=INK, font=font(47, True))
    draw.text((54, 112), subtitle, fill=SUB, font=font(25))
    draw.line((52, 159, 1028, 159), fill="#c9c6c0", width=2)
    return im

def fit(im: Image.Image, source: Path, box: tuple[int, int, int, int]):
    picture = Image.open(source).convert("RGB")
    x0, y0, x1, y1 = box
    picture = ImageOps.contain(picture, (x1-x0, y1-y0), Image.Resampling.LANCZOS)
    x = x0 + (x1-x0-picture.width)//2
    y = y0 + (y1-y0-picture.height)//2
    im.paste(picture, (x, y))
    ImageDraw.Draw(im).rectangle(box, outline="#b9b6b0", width=2)

first = base("REFERENCE → FOURPLEX", "Photo-locked street elevation · local RLASM 6.1 pilot")
d = ImageDraw.Draw(first)
d.text((54, 188), "SOURCE · OBLIQUE PHOTO", fill=INK, font=font(27, True))
fit(first, args.source, (52, 236, 1028, 920))
d.text((54, 961), "MODEL · MATCHED FRONT CORNER", fill=INK, font=font(27, True))
fit(first, args.renders/"front_corner.png", (52, 1008, 1028, 1692))
d.text((54, 1744), "Source-supported: repeated gables, charcoal/ivory siding, dark brick,", fill=SUB, font=font(23))
d.text((54, 1780), "independent stoops, black rails and landscaped street frontage.", fill=SUB, font=font(23))
d.text((54, 1840), "Candidate only · hidden elevations and dimensions are inferred.", fill=INK, font=font(22, True))
first.save(args.output/"01_source_front.png")

second = base("BUILDING & ACCESS", "Aerial, rear, end walls and entry circulation")
d = ImageDraw.Draw(second)
views = [
    ("AERIAL / ROOF", "aerial.png"), ("REAR / EXITS", "rear_side.png"),
    ("LEFT END", "left_side.png"), ("RIGHT END", "right_side.png"),
    ("FRONT ENTRY", "entry_circulation.png"), ("WINDOW DETAIL", "glass_close.png"),
]
for i, (label, name) in enumerate(views):
    col, row = i%2, i//2
    x0 = 52+col*500
    y0 = 195+row*520
    d.text((x0, y0), label, fill=INK, font=font(24, True))
    fit(second, args.renders/name, (x0, y0+44, x0+470, y0+442))
d.text((54, 1776), "Rear design and room arrangement are visual inferences from one photo.", fill=SUB, font=font(21))
d.text((54, 1835), "No measured plans, rear photo or top source supplied.", fill=INK, font=font(22, True))
second.save(args.output/"02_building_access.png")

print(args.output)
