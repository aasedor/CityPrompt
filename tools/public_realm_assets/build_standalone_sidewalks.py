"""Bounded, additive standalone sidewalks: dry run, --install --count 1, then 3.

Prepared-level conceptual pedestrian surfaces, with no provider calls or modules.
Existing catalogue entries and historic recipe contracts remain immutable.
"""
import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
FRONT = ROOT / 'frontend/src/data'
BACK = ROOT / 'backend/app/data'
DESIGNS = [
    ('standalone_narrow_sidewalk_v1', 'Standalone narrow sidewalk', 1.5, 'plain', [.62, .61, .58]),
    ('standalone_neighbourhood_sidewalk_v1', 'Standalone neighbourhood sidewalk', 2.0, 'slabs', [.61, .60, .56]),
    ('standalone_urban_sidewalk_v1', 'Standalone urban sidewalk', 3.0, 'paved', [.60, .59, .55]),
]

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def recipe(design):
    key, title, width, finish, color = design
    length = 6
    palette = {'paving': color, 'edge': [.46, .45, .42], 'edge_strip': [.32, .33, .32]}
    for i, factor in enumerate([.97, .99, 1.01, 1.03]):
        palette[f'paving.tile{i}'] = [round(v * factor, 4) for v in color]
    details = []
    regions = [dict(x=0, y=0, width=width, depth=length, material='paving')]
    if finish == 'slabs':
        details = [dict(x=0, y=y, width=width, depth=.006, z=.001, height=0, material='edge')
                   for y in [-3, -1.5, 0, 1.5, 3]]
    if finish == 'paved':
        # The reviewed reference has one flush charcoal strip within the width.
        strip = .2
        regions += [dict(x=width / 2 - strip / 2, y=0, width=strip, depth=length, material='edge_strip')]
    program = dict(schemaVersion=1, adapter='narrow-pathway-v1',
        surfaceRegions=regions, details=details, meshDetails=[],
        paving='brick' if finish == 'paved' else 'concrete', pavingModuleM=[.6, .4],
        minLengthM=max(2, width), maxLengthM=300, preparedLevelOnly=True,
        baseLiftM=.025, palette=palette)
    assembly = dict(units='metres', axes='X across, Y along, Z up', origin='surface centre',
        widthM=width, lengthM=length, program=program, placements=[], modules={})
    thumbnail = f'/archetypes/streets/standalone-sidewalks/{key}.png'
    hero = ROOT / ('frontend/public' + thumbnail)
    if not hero.is_file():
        raise ValueError(f'Missing reviewed photographic reference: {hero}')
    row = dict(id=key, sourceArchetypeId='campus_pedestrian_spine', title=title, status='candidate',
        sourceRecipeSha256=digest(assembly), sourceAssemblySha256=digest(assembly),
        referenceSha256=hashlib.sha256(hero.read_bytes()).hexdigest(),
        widthM=width, fixtureLengthM=length, routeAxis='local_y', junctionSurface='pavers',
        sections=[dict(name='clear_walk', x=0, width=width, material='paving')],
        placements=[], modules={}, treeWells=[], thumbnailUrl=thumbnail,
        program=program, programSha256=digest(program))
    return row, assembly

def append_json(text, values, key=None):
    """Splice at the container end; retain every existing object byte."""
    if not values:
        return text
    start = text.index('[') if key is None else re.search(r'"' + re.escape(key) + r'"\s*:\s*', text).end()
    _, consumed = json.JSONDecoder().raw_decode(text[start:])
    end = start + consumed - 1
    existing = json.loads(text[start:end + 1])
    addition = ',\n'.join(json.dumps(value, indent=2, ensure_ascii=False) for value in values)
    return text[:end] + (',' if existing else '') + '\n' + addition + '\n' + text[end:]

def install(rows, output):
    from app.services.public_realm_lego import build_public_realm_capability_catalog, public_realm_capability_fingerprint
    catalog = build_public_realm_capability_catalog()
    history_path = BACK / 'publicRealmCatalogHistory.json'
    original = history_path.read_text(encoding='utf-8')
    history = json.loads(original)
    locks = {f'{c.family_id}@{c.family_version}': public_realm_capability_fingerprint(c) for c in catalog.capabilities}
    retained = history['catalogs'].get(catalog.fingerprint)
    if retained is not None and retained != locks:
        raise ValueError('Historic public-realm catalogue cannot be overwritten')
    updates = {}
    if retained is None:
        start = re.search(r'"catalogs"\s*:\s*', original).end()
        _, consumed = json.JSONDecoder().raw_decode(original[start:])
        end = start + consumed - 1
        entry = json.dumps(catalog.fingerprint) + ': ' + json.dumps(locks, indent=2)
        updates[history_path] = original[:end] + (',' if history['catalogs'] else '') + '\n' + entry + '\n' + original[end:]
    for root in (FRONT, BACK):
        pilot_path, roster_path = root / 'nativeStreetPilots.json', root / 'classroomStarter.json'
        pilot_text, roster_text = pilot_path.read_text(encoding='utf-8'), roster_path.read_text(encoding='utf-8')
        pilots, roster = json.loads(pilot_text), json.loads(roster_text)
        additions, releases = [], []
        for row in rows:
            old = next((p for p in pilots if p['id'] == row['id']), None)
            release = dict(domain='street', representation='native-modules', archetypeId=row['sourceArchetypeId'],
                variantId=row['id'], revision=row['sourceRecipeSha256'], status='local-pilot-runtime-pending')
            old_release = next((r for r in roster['entries'] if r.get('variantId') == row['id']), None)
            if (old is not None and old != row) or (old_release is not None and old_release != release):
                raise ValueError('An existing sidewalk revision cannot be overwritten')
            if old is None:
                additions.append(row)
            if old_release is None:
                releases.append(release)
        updates[pilot_path] = append_json(pilot_text, additions)
        updates[roster_path] = append_json(roster_text, releases, 'entries')
        assert json.loads(updates[pilot_path])[:len(pilots)] == pilots
        assert json.loads(updates[roster_path])['entries'][:len(roster['entries'])] == roster['entries']
    if json.loads(updates[FRONT / 'nativeStreetPilots.json']) != json.loads(updates[BACK / 'nativeStreetPilots.json']):
        raise ValueError('Frontend/backend native street manifests disagree')
    def native_releases(path):
        return [r for r in json.loads(updates[path])['entries'] if r['representation'] == 'native-modules']
    if native_releases(FRONT / 'classroomStarter.json') != native_releases(BACK / 'classroomStarter.json'):
        raise ValueError('Frontend/backend classroom manifests disagree')
    for path, text in updates.items():
        if path.read_text(encoding='utf-8') == text:
            continue
        backup = output / 'backups' / path.relative_to(ROOT)
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            shutil.copy2(path, backup)
        path.write_text(text, encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count', type=int, choices=[1, 3], default=1)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    rows = []
    for design in DESIGNS[:args.count]:
        row, assembly = recipe(design)
        rows.append(row)
        write(args.output / f"{row['id']}-assembly.json", assembly)
    write(args.output / 'manifest.json', rows)
    if args.install:
        install(rows, args.output)
        print(f'Installed {len(rows)} local sidewalk recipes; original entries retained; no publication')
    else:
        print(f'Dry run: {len(rows)} sidewalk recipes; zero provider calls; source unchanged')

if __name__ == '__main__':
    main()
