"""Compose 1080x1920 phone comparison boards: locked source beside the matched render role."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

PAIRS = [('front', 'front.png', 'Locked front'), ('oblique', 'front_corner.png', 'Locked oblique'), ('top', 'aerial.png', 'Locked top')]
DETAIL = ['facade_close', 'architecture_close', 'glass_close', 'arched_windows', 'corner_entry', 'roof_pavilion', 'chimney_contact', 'shopfront', 'interior', 'rear_yard', 'left_side', 'right_side', 'rear', 'rear_side', 'top']


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
        if Path(path).is_file():
            img.paste(fit(Image.open(path), cw, ch), (x, y))
        else:
            d.rectangle([x, y, x + cw, y + ch], outline=(120, 40, 40)); d.text((x + 10, y + 10), 'missing: ' + Path(path).name, fill=(255, 120, 120), font=font)
        label(d, (x, y), text, font)
    img.save(out, 'PNG'); return out


def main():
    p = argparse.ArgumentParser(); p.add_argument('--candidate', required=True); a = p.parse_args()
    root = Path(a.candidate); entry = json.loads((root / 'source-entry.json').read_text())
    src = {s['role']: root / s['path'] for s in entry['sources']}
    cells = []
    for role, render, text in PAIRS:
        cells += [(src[role], text), (root / 'renders' / render, 'Render ' + render[:-4])]
    boards = [board(root / 'boards' / 'phone-01-source-vs-render.png', entry['archetype_id'] + ' - source vs render', cells)]
    detail = [(root / 'renders' / (n + '.png'), n) for n in DETAIL if (root / 'renders' / (n + '.png')).is_file()]
    for k in range(0, len(detail), 6):
        boards.append(board(root / 'boards' / f'phone-{2 + k // 6:02d}-details.png', entry['archetype_id'] + f' - details {k // 6 + 1}', detail[k:k + 6]))
    for b in boards: print(b)


if __name__ == '__main__':
    main()
