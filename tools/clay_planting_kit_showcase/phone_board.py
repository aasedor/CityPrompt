"""Compose 1080x1920 phone boards of the kit showcase renders (no locked sources: renders only, six per board)."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def fit(img, w, h):
    img = img.convert('RGB'); r = min(w / img.width, h / img.height)
    img = img.resize((max(1, int(img.width * r)), max(1, int(img.height * r))), Image.LANCZOS)
    canvas = Image.new('RGB', (w, h), (28, 28, 30)); canvas.paste(img, ((w - img.width) // 2, (h - img.height) // 2))
    return canvas


def label(draw, xy, text, font):
    draw.rectangle([xy[0], xy[1], xy[0] + 8 + draw.textlength(text, font=font), xy[1] + 30], fill=(0, 0, 0))
    draw.text((xy[0] + 4, xy[1] + 4), text, fill=(255, 255, 255), font=font)


def board(out, title, cells, cols=2):
    W, H = 1080, 1920
    img = Image.new('RGB', (W, H), (18, 18, 20)); d = ImageDraw.Draw(img)
    try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 20)
    except Exception: font = ImageFont.load_default()
    d.text((16, 12), title, fill=(255, 255, 255), font=font)
    rows = (len(cells) + cols - 1) // cols
    cw, ch = (W - 16 * (cols + 1)) // cols, (H - 60 - 16 * (rows + 1)) // rows
    for i, (path, text) in enumerate(cells):
        x = 16 + (i % cols) * (cw + 16); y = 60 + (i // cols) * (ch + 16)
        img.paste(fit(Image.open(path), cw, ch), (x, y)); label(d, (x, y), text, font)
    img.save(out, 'PNG'); return out


def main():
    p = argparse.ArgumentParser(); p.add_argument('--candidate', required=True); a = p.parse_args()
    root = Path(a.candidate)
    roster = [c['name'] for c in json.loads((root / 'prework-manifest.json').read_text())['camera_roster']]
    cells = [(root / 'renders' / (n + '.png'), n) for n in roster if (root / 'renders' / (n + '.png')).is_file()]
    for k in range(0, len(cells), 6):
        print(board(root / 'boards' / f'phone-{1 + k // 6:02d}-kit-showcase.png', f'planting kit showcase - {k // 6 + 1}', cells[k:k + 6]))


if __name__ == '__main__':
    main()
