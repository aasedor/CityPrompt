"""Phone review boards (1080 x 1920) for one crescent candidate directory. Needs Pillow.

    python3 tools/catalogue_crescent_terrace_pilot/boards.py <candidate directory>

Three boards set each locked reference over the model seen from an approximate camera;
the fourth collects the close views. Existing boards are never overwritten.
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


def construction(directory, report):
    board, draw = shared.sheet('Construction and contact views', report)
    views = ('facade_close', 'architecture_close', 'glass_close', 'entrance_contact', 'end_contact', 'corner_close', 'roof_contact', 'rear_ground')
    for k, view in enumerate(views):
        x, y = 36 + (k % 2) * 510, 150 + (k // 2) * 430
        board.paste(shared.fitted(directory / 'renders' / f'{view}.png', 498, 374), (x, y + 34))
        draw.text((x, y), view, fill=shared.INK, font=shared.font(22))
    shared.save(board, directory / 'boards' / 'phone-construction.png')


def main():
    directory = Path(sys.argv[1])
    report = json.loads((directory / 'build-report.json').read_text(encoding='utf-8'))
    source = {lock['role']: lock for lock in report['sources']}
    shared.comparison(directory, report, 'phone-street.png', 'Street view', source['front'], 'match_front',
                      'Check: three storeys, plain ground storey, giant Ionic order, one sash to\na bay, iron guards, entablature, balustrade, stacks with pots, railings.\n'
                      'Known differences: the reference sashes have no glazing bars; ashlar\njoints and the sunken areas are left out. Entourage is not in the model.')
    shared.comparison(directory, report, 'phone-oblique.png', 'Oblique view', source['oblique'], 'match_oblique',
                      'Check: half-ellipse plan, about twenty houses, the order on the convex\nside and the six-bay end, slate ranges, party stacks, dormers, hipped end.\n'
                      'Known differences: the camera is approximate; sunken areas, bridges\nand the lead-covered roof additions are left out.')
    shared.comparison(directory, report, 'phone-roof.png', 'Roof plan', source['top'], 'match_top',
                      'The reference roof plan shows a different building: about ten houses\nin a short block that is concave on both long sides. The street view and\n'
                      'oblique govern the plan. This image informs roof character only:\nslate ranges, a lead flat, a stack at each party wall, hipped ends.')
    construction(directory, report)
    print(json.dumps({'boards': sorted(path.name for path in (directory / 'boards').iterdir())}))


if __name__ == '__main__':
    main()
