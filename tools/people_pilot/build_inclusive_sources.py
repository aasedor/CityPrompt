"""Nine clothed adult intermediates locked to the eight inclusive picker photos.

These helper rigs are never catalogue entries. Fixed groups are posed, fitted
and independently measured by build_inclusive.py --person-root OUTPUT.
"""
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_wardrobe import build_one, DESIGNS
from wardrobe_rules import outfit

ROOT = Path('C:/dev-artifacts/CityPrompt/people-inclusive-2026-10-23/clothed-sources')
DESCRIPTIONS = [
    ('people-pilot-commuter', '#c7775e', '#3b4149', '#e9e4da', False),
    ('people-community-ava', '#348981', '#35383e', '#e9e4da', False),
    ('people-community-mateo', '#bd7a68', '#343d51', '#e9e4da', False),
    ('people-community-clara', '#7c9682', '#536457', '#8e7e6b', True),
    ('people-pilot-neighbour', '#7c98aa', '#c6c0a9', '#4c4238', False),
    ('people-community-andre', '#687a8b', '#c9c7b5', '#e9e4da', False),
    ('people-community-noah', '#34485a', '#7b856d', '#e9e4da', False),
    ('people-community-imani', '#d3c29f', '#80755c', '#e9e4da', False),
    ('people-community-leo', '#7193ad', '#334e60', '#e9e4da', False),
]


if __name__ == '__main__':
    assert (ROOT / 'sources').exists(), 'Create sources junction to preserved CC0 downloads first'
    sources = {}
    for original, top, bottom, shoe, coat in DESCRIPTIONS:
        design = dict(DESIGNS[original], id='inclusive-source-' + original)
        wardrobe = outfit(top, bottom, shoe, opening=True, coat=coat, undershirt='#f1e8d6')
        if original == 'people-pilot-commuter':
            wardrobe = outfit('#c7775e', bottom, shoe)
        elif original == 'people-community-andre':
            wardrobe = outfit('#724154', bottom, shoe, sleeve='short', collar=True)
        elif original == 'people-community-mateo':
            wardrobe = outfit('#b08a4e', bottom, shoe, hoodie=True)
        elif original == 'people-community-noah':
            wardrobe = outfit('#34485a', bottom, shoe, sleeve='short', stripes=True)
        _, model = build_one(ROOT, design, wardrobe, render=False)
        sources[original] = {'path': str(model), 'sha256': hashlib.sha256(model.read_bytes()).hexdigest(),
                             'wardrobe': wardrobe}
    (ROOT / 'source-map.json').write_text(json.dumps(sources, indent=2) + '\n')
