"""Copy reviewed generated originals unchanged; never overwrite source locks."""
import argparse
import json
from pathlib import Path
import shutil
from .references import ROOT, digest, image_size, source_entry


def capture(slug):
    batch = json.loads(Path(__file__).with_name('batch-reference-capture.json').read_text())
    family = next(f for f in batch['families'] if f['slug'] == slug)
    target = ROOT / 'frontend/public/archetypes/buildings' / slug
    target.mkdir(parents=True, exist_ok=False)
    for r in family['records']:
        p = target / r['file']
        shutil.copy2(r['generated_path'], p)
        r.update(sha256=digest(p), bytes=p.stat().st_size, dimensions_px=image_size(p))
    family.update(origin=batch['origin'], generation_tool=batch['generation_tool'], date=batch['date'])
    (target/'generation-provenance.json').write_text(json.dumps(family, indent=2), encoding='utf-8')
    return source_entry(ROOT, slug)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('slug')
    print(json.dumps(capture(p.parse_args().slug), indent=2))
