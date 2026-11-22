"""Phone review boards (1080 x 1920) for one concert-hall candidate directory. Needs Pillow.

    python3 tools/catalogue_concert_hall_pilot/boards.py <candidate directory>

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
                      'Check: finned podium over a recessed glazed ground floor with doors;\nplanted roof with a winding path; two bronze shells meeting in a notch\n'
                      'at the back; the oculus showing timber walls, tiers and a stage.\nFitted camera, 31 px RMS. This view puts the oculus about 8 m further\n'
                      'west than the roof view does; the roof view governs plan positions.')
    shared.comparison(directory, report, 'phone-roof.png', 'Roof plan', source['top'], 'match_top',
                      'Check: podium outline, the west shell wrapping west and south, the east\nshell north-east and east, the radial notch at the north, the ring\n'
                      'under the west shell on the oculus, seating west and the dark stage\neast, the path loop. The pier, plaza and water are site, not model.')
    grid(directory, report, 'phone-construction.png', 'Construction and contact views',
         ('facade_close', 'architecture_close', 'glass_close', 'lip_contact', 'notch_contact', 'roof_garden', 'front_corner', 'rear_side'))
    grid(directory, report, 'phone-programme.png', 'Whole views and programme',
         ('front', 'left_side', 'right_side', 'rear', 'aerial', 'top', 'oculus_program', 'glass_close'))
    print(json.dumps({'boards': sorted(path.name for path in (directory / 'boards').iterdir())}))


if __name__ == '__main__':
    main()
