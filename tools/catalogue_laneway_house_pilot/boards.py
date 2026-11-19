"""Phone review boards (1080 x 1920) for one laneway-house candidate directory. Needs Pillow.

    python3 tools/catalogue_laneway_house_pilot/boards.py <candidate directory>

Three boards set each locked reference over the model seen from a fitted camera; the
fourth collects the close views. Existing boards are never overwritten.
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
    views = ('facade_close', 'architecture_close', 'glass_close', 'entrance_contact', 'roof_contact', 'band_contact', 'balcony_contact', 'rear_side')
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
                      'Check: brick garage block with four lites in the door, glass-railed balcony\non its roof, porch under a flat canopy with a cedar post, sliding doors,\n'
                      'corner window in a dark box, dark floor band, panel band on the lane.\n'
                      'Fitted camera, 12 px RMS. The catalogue text describes a different,\nsingle-storey building; the images govern. Entourage is not in the model.')
    shared.comparison(directory, report, 'phone-oblique.png', 'Oblique view', source['oblique'], 'match_oblique',
                      'Check: projection of the garage block, balcony and canopy in front of\nthe upper storey, cedar end of the balcony, corner window wrapping onto\n'
                      'the lane face, four-panel band with its slots, hipped standing-seam roof.\nFitted camera, 14 px RMS.')
    shared.comparison(directory, report, 'phone-roof.png', 'Roof plan', source['top'], 'match_top',
                      'Check: near-square hipped roof with a short ridge front to back, standing\nseams square to each eave, the balcony deck and the dark canopy in front\n'
                      'of the street eave. The reference is a perspective from above; this is\northographic, so the ground features do not register.')
    construction(directory, report)
    print(json.dumps({'boards': sorted(path.name for path in (directory / 'boards').iterdir())}))


if __name__ == '__main__':
    main()
