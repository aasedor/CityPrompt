"""Phone review boards (1080 x 1920) for one silo-cluster candidate directory. Needs Pillow.

    python3 tools/catalogue_silo_cluster_pilot/boards.py <candidate directory>

Two boards set each locked reference over the model seen from a fitted camera; the other
two collect the construction and contact views and the programme views. Existing boards
are never overwritten. The variant has no usable street view, so there is no street board.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('clay_review_boards', ROOT / 'tools' / 'catalogue_plus15_concrete_pilot' / 'boards.py')
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)


def grid(directory, report, name, title, views):
    board, draw = shared.sheet(title, report)
    for k, view in enumerate(views):
        x, y = 36 + (k % 2) * 510, 150 + (k // 2) * 430
        board.paste(shared.fitted(directory / 'renders' / f'{view}.png', 498, 374), (x, y + 34))
        draw.text((x, y), view, fill=shared.INK, font=shared.font(22))
    shared.save(board, directory / 'boards' / name)


def main():
    directory = Path(sys.argv[1])
    report = json.loads((directory / 'build-report.json').read_text(encoding='utf-8'))
    source = {lock['role']: lock for lock in report['sources']}
    shared.comparison(directory, report, 'phone-oblique.png', 'Oblique view', source['oblique'], 'match_oblique',
                      'Check: two rows of concrete silos with ribbed caps and railings, the\nshaft proud of the front row, the head house and its ventilators, the\n'
                      'gallery over the caps on steel frames, the walkways, the sheds and\nbays. Fitted camera, 30 px RMS: the left group\'s silos are spaced\n'
                      'unevenly in the reference. Rail yards and sheds around are site.')
    shared.comparison(directory, report, 'phone-roof.png', 'Roof plan', source['top'], 'match_top',
                      'Check: two rows of eight caps, the front row parted round the shaft,\nthe gallery along the middle, the head house with its ridge north-south\n'
                      'and two ventilators, the sheds and pads at the front. The reference\nleans tall parts north; this view is orthographic.')
    grid(directory, report, 'phone-construction.png', 'Construction and contact views',
         ('facade_close', 'architecture_close', 'glass_close', 'caps_close', 'gallery_close', 'bays_contact', 'base_contact', 'rear_side'))
    grid(directory, report, 'phone-programme.png', 'Whole views',
         ('front', 'front_corner', 'left_side', 'right_side', 'rear', 'rear_side', 'aerial', 'top'))
    print(json.dumps({'boards': sorted(path.name for path in (directory / 'boards').iterdir())}))


if __name__ == '__main__':
    main()
