from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "phone"
OUT.mkdir(parents=True, exist_ok=True)

BG = (7, 13, 17)
PANEL = (15, 25, 31)
EDGE = (73, 98, 111)
WHITE = (238, 242, 244)
MINT = (133, 221, 181)
MUTED = (164, 180, 189)


def font(size, bold=False):
    names = ["arialbd.ttf" if bold else "arial.ttf", "segoeuib.ttf" if bold else "segoeui.ttf"]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


def fit_crop(path, width, height):
    image = Image.open(path).convert("RGB")
    ratio = max(width / image.width, height / image.height)
    resized = image.resize((round(image.width * ratio), round(image.height * ratio)), Image.Resampling.LANCZOS)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def label(draw, x, y, text, color=MINT, size=24):
    draw.text((x, y), text, fill=color, font=font(size, True))


def comparison_board():
    canvas = Image.new("RGB", (1080, 1920), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((42, 38), "RLASM v6.1 — RAW-PHOTO PILOT", fill=WHITE, font=font(39, True))
    draw.text((42, 91), "Barcelona Modernist Printing House · candidate v7", fill=MUTED, font=font(24))
    rows = [
        ("FRONT / MATERIAL + BAY IDENTITY", "references/catalogue/variant_2.png", "renders/front.png"),
        ("60° / MASSING + ENVELOPE", "references/catalogue/variant_2_angle_60.jpg", "renders/front_corner.png"),
        ("TOP / PLAN + T-LANTERN TOPOLOGY", "references/catalogue/variant_2_angle_90.jpg", "renders/aerial.png"),
    ]
    y = 150
    for title, source, model in rows:
        draw.rounded_rectangle((30, y, 1050, y + 535), radius=16, fill=PANEL, outline=EDGE, width=2)
        label(draw, 48, y + 18, title)
        label(draw, 48, y + 57, "LOCKED SOURCE", size=19)
        label(draw, 551, y + 57, "PHYSICAL MODEL", size=19)
        canvas.paste(fit_crop(ROOT / source, 485, 430), (48, y + 91))
        canvas.paste(fit_crop(ROOT / model, 481, 430), (551, y + 91))
        y += 552
    draw.text((42, 1826), "Exact variant-2 photos only · no prebuilt model · no generic material fallback", fill=MUTED, font=font(21))
    draw.text((42, 1861), "Builder review board — independent keeper decision still required", fill=MINT, font=font(21, True))
    canvas.save(OUT / "barcelona-modernist-printing-house-comparison-01.png", optimize=True)


def detail_board():
    canvas = Image.new("RGB", (1080, 1920), BG)
    draw = ImageDraw.Draw(canvas)
    draw.text((42, 38), "RLASM v6.1 — PHYSICAL PROOF", fill=WHITE, font=font(39, True))
    draw.text((42, 91), "Identity · opening depth · roof contact · visible program", fill=MUTED, font=font(24))
    cells = [
        ("REGISTERED PRINTING ROSETTE", "renders/architecture_close.png"),
        ("RECESSED GLASS + OCCUPIED DEPTH", "renders/glass_close.png"),
        ("CLOSED T-LANTERN + CURB CONTACT", "renders/roof_lantern_close.png"),
        ("VISIBLE PLATEN PRESS WORKFLOW", "renders/printing_press_close.png"),
    ]
    positions = [(30, 150), (550, 150), (30, 982), (550, 982)]
    for (title, path), (x, y) in zip(cells, positions):
        draw.rounded_rectangle((x, y, x + 500, y + 794), radius=16, fill=PANEL, outline=EDGE, width=2)
        label(draw, x + 18, y + 18, title, size=18)
        canvas.paste(fit_crop(ROOT / path, 464, 720), (x + 18, y + 59))
    draw.text((42, 1826), "Close views are evidence, not substitutes for whole-envelope review.", fill=MUTED, font=font(21))
    draw.text((42, 1861), "Status: NOT A KEEPER until independent zero-P0/P1 review", fill=MINT, font=font(21, True))
    canvas.save(OUT / "barcelona-modernist-printing-house-details-02.png", optimize=True)


comparison_board()
detail_board()
