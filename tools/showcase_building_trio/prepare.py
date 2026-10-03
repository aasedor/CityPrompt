"""Lock the finite September showcase batch without modifying catalogue sources."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

SPECS = {
    'market': ('food_hall_market_hall', 'market_historic_iron_glass', 'food_hall_market_hall', 0),
    'tower': ('art_deco_setback_tower', 'art_deco_cream_terracotta', 'art_deco_setback_tower', 0),
    'aquatic': ('aquatic_natatorium_complex', 'biophilic_mass_timber_pool', 'aquatic-natatorium-complex', 2),
}

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    entries = []
    for kind, (parent, variant, folder, index) in SPECS.items():
        sources = []
        for role, suffix in [('front', '.png'), ('oblique', '_angle_60.jpg'), ('top', '_angle_90.jpg')]:
            rel = f'frontend/public/archetypes/buildings/{folder}/variant_{index}{suffix}'
            data = (a.source_root / rel).read_bytes()
            revision = 'working_source_bytes'
            # The August Wave 13 commit replaced this front photograph with a clay
            # preview. Restore the original exact-variant photo only in this lock.
            if kind == 'tower' and role == 'front':
                data = subprocess.check_output(['git', 'show', f'e88d00708:{rel}'])
                revision = 'e88d00708'
            target = a.output / kind / Path(rel).name
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(data)
            sources.append(dict(role=role, path=str(target), repo_path=rel, bytes=len(data),
                                sha256=hashlib.sha256(data).hexdigest(), source_revision=revision))
        entries.append(dict(kind=kind, archetype_id=parent, variant_id=variant, sources=sources))
    (a.output / 'lock.json').write_text(json.dumps(dict(schema=1, entries=entries), indent=2)+'\n')
    print(json.dumps({'locked_buildings': len(entries), 'sources': sum(len(e['sources']) for e in entries)}))

if __name__ == '__main__':
    main()
