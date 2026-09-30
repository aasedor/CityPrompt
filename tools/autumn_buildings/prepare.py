"""Hash-lock the finite autumn building trio; catalogue sources remain unchanged."""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

SPECS = {
    'timber': ('nordic_timber_midrise', 'nordic_timber_mass_timber'),
    'villa': ('mediterranean_villa_estate', 'med_villa_tuscan'),
    'cinema': ('deco_theater_mainstreet', 'deco_theater_movie_palace'),
}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    entries = []
    for kind, (parent, variant) in SPECS.items():
        sources = []
        for role, suffix in [('front', '.png'), ('oblique', '_angle_60.jpg'), ('top', '_angle_90.jpg')]:
            rel = f'frontend/public/archetypes/buildings/{parent}/variant_0{suffix}'
            path = a.source_root / rel
            with Image.open(path) as im:
                im.verify()
            data = path.read_bytes()
            sources.append(dict(role=role, path=str(path.resolve()), repo_path=rel,
                                bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
        entries.append(dict(kind=kind, archetype_id=parent, variant_id=variant, sources=sources))
    a.output.mkdir(parents=True, exist_ok=False)
    (a.output / 'lock.json').write_text(json.dumps(dict(schema=1, entries=entries), indent=2)+'\n')
    print('Locked three exact variants and nine source images.')

if __name__ == '__main__':
    main()
