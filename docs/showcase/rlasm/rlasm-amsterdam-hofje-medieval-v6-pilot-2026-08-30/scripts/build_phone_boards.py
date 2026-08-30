from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence"
W, H = 1080, 1920
BG = (20, 23, 22)
PAPER = (236, 232, 218)
INK = (238, 238, 230)
MUTED = (169, 173, 164)
ACCENT = (176, 93, 53)


def font(size: int, bold: bool = False):
    names = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for name in names:
        if Path(name).is_file():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


F_TITLE = font(45, True)
F_SUB = font(23)
F_LABEL = font(23, True)
F_SMALL = font(18)


def fit(path: Path, box: tuple[int, int, int, int], crop: bool = False) -> Image.Image:
    img = Image.open(path).convert("RGB")
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    ratio = max(bw / img.width, bh / img.height) if crop else min(bw / img.width, bh / img.height)
    size = (max(1, round(img.width * ratio)), max(1, round(img.height * ratio)))
    img = img.resize(size, Image.Resampling.LANCZOS)
    if crop:
        left = max(0, (img.width - bw) // 2)
        top = max(0, (img.height - bh) // 2)
        img = img.crop((left, top, left + bw, top + bh))
    return img


def panel(board: Image.Image, draw: ImageDraw.ImageDraw, path: Path, box, label: str, crop=False):
    x0, y0, x1, y1 = box
    draw.rectangle((x0, y0, x1, y1), fill=(7, 9, 8), outline=(112, 116, 108), width=2)
    label_h = 42
    image_box = (x0 + 3, y0 + label_h, x1 - 3, y1 - 3)
    img = fit(path, image_box, crop=crop)
    ix = image_box[0] + (image_box[2] - image_box[0] - img.width) // 2
    iy = image_box[1] + (image_box[3] - image_box[1] - img.height) // 2
    board.paste(img, (ix, iy))
    draw.rectangle((x0, y0, x1, y0 + label_h), fill=(9, 12, 11))
    draw.text((x0 + 13, y0 + 8), label, fill=INK, font=F_LABEL)


def header(draw: ImageDraw.ImageDraw, title: str, subtitle: str):
    draw.text((38, 30), title, fill=INK, font=F_TITLE)
    draw.text((40, 88), subtitle, fill=MUTED, font=F_SUB)
    draw.rectangle((40, 128, 1040, 134), fill=ACCENT)


def comparison_board():
    board = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(board)
    header(draw, "SOURCE ↔ MODEL", "Amsterdam Hofje / hofje_medieval / variant 0 • RLASM v6.1")
    panel(board, draw, ROOT / "references/catalogue/variant_0.png", (40, 165, 1040, 680), "LOCKED FRONT SOURCE")
    panel(board, draw, ROOT / "renders/front.png", (40, 710, 1040, 1225), "v023 FRONT — COMPLETE ENVELOPE")
    panel(board, draw, ROOT / "references/catalogue/variant_0_angle_60.jpg", (40, 1255, 525, 1695), "LOCKED 60° SOURCE", crop=True)
    panel(board, draw, ROOT / "renders/aerial.png", (555, 1255, 1040, 1695), "v023 AERIAL", crop=True)
    draw.text((42, 1730), "SOURCE LOCK", fill=ACCENT, font=F_LABEL)
    draw.text((42, 1768), "front 99728a7d…f925  •  60° b4311cde…75a  •  top 79228135…f482", fill=INK, font=F_SMALL)
    draw.text((42, 1810), "Pixels govern • no sibling mixing • benchmark models used only as method/quality references", fill=MUTED, font=F_SMALL)
    draw.text((42, 1850), "Identity carried by U-plan, pavilion gable, multi-light bays, pantile roof graph, gates and formal court.", fill=MUTED, font=F_SMALL)
    board.save(OUT / "source-model-comparison-phone.png")


def proof_board():
    board = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(board)
    header(draw, "PHYSICAL / MATERIAL / DETAIL", "Native render proof • filenames and metadata are not evidence")
    panel(board, draw, ROOT / "renders/glass_close.png", (40, 165, 525, 610), "OPENING SECTION", crop=True)
    panel(board, draw, ROOT / "renders/gate_contact_close.png", (555, 165, 1040, 610), "GATE / GRADE CONTACT", crop=True)
    panel(board, draw, ROOT / "renders/dormer_contact_close.png", (40, 640, 525, 1085), "DORMER / FLASHING CONTACT", crop=True)
    panel(board, draw, ROOT / "renders/architecture_close.png", (555, 640, 1040, 1085), "PAVILION SIGNATURE", crop=True)
    panel(board, draw, ROOT / "renders/program_interior.png", (40, 1115, 525, 1570), "COMMUNAL KITCHEN", crop=True)
    panel(board, draw, ROOT / "references/source-conditioned-material-board.png", (555, 1115, 1040, 1570), "SOURCE MATERIAL AUTHORITY", crop=True)
    panel(board, draw, ROOT / "renders/roof_contact_close.png", (40, 1600, 1040, 1840), "ROOF PENETRATION / LEAD HOOD", crop=True)
    draw.text((42, 1862), "Geometry owns cuts, returns, frames, panes, depth, roof fields, load paths and contacts.", fill=MUTED, font=F_SMALL)
    board.save(OUT / "physical-material-detail-proof-phone.png")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    comparison_board()
    proof_board()
    for name in ("source-model-comparison-phone.png", "physical-material-detail-proof-phone.png"):
        path = OUT / name
        with Image.open(path) as image:
            assert image.size == (1080, 1920), (path, image.size)
        print(path)
