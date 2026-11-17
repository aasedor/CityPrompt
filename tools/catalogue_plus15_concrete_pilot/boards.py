"""Phone review boards (1080 x 1920) for one candidate directory. Needs Pillow.

    python3 tools/catalogue_plus15_concrete_pilot/boards.py <candidate directory>

Three boards set each locked reference over the model seen from a fitted camera; the
fourth collects the close views. Existing boards are never overwritten.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SIZE = (1080, 1920)
INK, PAPER, RULE = (34, 36, 40), (246, 244, 240), (196, 192, 184)


def font(size):
    return ImageFont.load_default(size=size)


def fitted(path, width, height):
    image = Image.open(path).convert('RGB')
    scale = min(width / image.width, height / image.height)
    return image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)


def sheet(title, report):
    board = Image.new('RGB', SIZE, PAPER)
    draw = ImageDraw.Draw(board)
    draw.text((36, 30), title, fill=INK, font=font(40))
    draw.text((36, 84), f'{report["candidate"]}   model {report["model"]["sha256"][:12]}', fill=(110, 110, 112), font=font(22))
    draw.line([(36, 124), (SIZE[0] - 36, 124)], fill=RULE, width=2)
    return board, draw


def comparison(directory, report, name, title, source, render, note):
    board, draw = sheet(title, report)
    y = 150
    for label, path in ((f'Reference: {source["repo_path"].rsplit("/", 1)[1]}', ROOT / source['repo_path']),
                        (f'Clay model, fitted camera: renders/{render}.png', directory / 'renders' / f'{render}.png')):
        draw.text((36, y), label, fill=INK, font=font(24))
        image = fitted(path, SIZE[0] - 72, 756)
        board.paste(image, ((SIZE[0] - image.width) // 2, y + 36))
        y += 36 + 756 + 22
    draw.multiline_text((36, y), note, fill=INK, font=font(21), spacing=7)
    save(board, directory / 'boards' / name)


def construction(directory, report):
    board, draw = sheet('Construction and contact views', report)
    views = ('facade_close', 'corner_close', 'architecture_close', 'entrance_contact', 'glass_close', 'bridge_contact',
             'bridge_junction', 'roof_contact')
    for k, view in enumerate(views):
        x, y = 36 + (k % 2) * 510, 150 + (k // 2) * 430
        image = fitted(directory / 'renders' / f'{view}.png', 498, 374)
        board.paste(image, (x, y + 34))
        draw.text((x, y), view, fill=INK, font=font(22))
    save(board, directory / 'boards' / 'phone-construction.png')


def save(board, path):
    if path.exists():
        raise SystemExit(f'{path} exists; boards are never overwritten')
    path.parent.mkdir(parents=True, exist_ok=True)
    board.save(path)


def main():
    directory = Path(sys.argv[1])
    report = json.loads((directory / 'build-report.json').read_text(encoding='utf-8'))
    source = {lock['role']: lock for lock in report['sources']}
    comparison(directory, report, 'phone-street.png', 'Street view', source['front'], 'match_front',
               'Check: five storeys, four ribbon and band pairs, cap strip and shadow line,\ngranite piers, entrance bay, walkway at the third storey.\n'
               'Known difference: the reference shows more penthouse above the parapet\nthan its own roof plan allows. Entourage is not part of the model.')
    comparison(directory, report, 'phone-oblique.png', 'Oblique view', source['oblique'], 'match_oblique',
               'Check: massing, penthouse size and panels, door and louvre, open well,\nroof items, walkway position and section.\n'
               'Known difference: the walkway is a 9 m length with a glazed end;\nthe reference runs on to a neighbour.')
    comparison(directory, report, 'phone-roof.png', 'Roof plan', source['top'], 'match_top',
               'Check: footprint ratio, centred penthouse, well in the rear east corner,\nwalkway position on the east flank, hatch, vent, unit and conduit runs.')
    construction(directory, report)
    print(json.dumps({'boards': sorted(path.name for path in (directory / 'boards').iterdir())}))


if __name__ == '__main__':
    main()
