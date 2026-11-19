"""Register a built Stephen Avenue package as a local drawable street pilot. Dry run by default.

    python3 tools/stephen_avenue_street/install.py --package <build directory> --backups <directory> [--install]

Additive only: every registry file is spliced as text, so existing records keep their
exact bytes. Refuses to overwrite a different revision, module or card. Backups of every
changed file go to --backups. Runtime acceptance and publication remain separate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONT, BACK = ROOT / 'frontend/src/data', ROOT / 'backend/app/data'
PUBLIC = ROOT / 'frontend/public'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def splice_list(text, values, key=None):
    """Append values at the end of a JSON list (the top level, or the list under `key`)."""
    start = text.index('[') if key is None else re.search(r'"' + re.escape(key) + r'"\s*:\s*', text).end()
    _, consumed = json.JSONDecoder().raw_decode(text[start:])
    end = start + consumed - 1
    existing = json.loads(text[start:end + 1])
    addition = ',\n'.join(json.dumps(v, indent=2, ensure_ascii=False) for v in values)
    return text[:end] + (',' if existing else '') + '\n' + addition + '\n' + text[end:]


def splice_object(text, pairs, indent=2):
    """Add key/value pairs before the closing brace of a top-level JSON object."""
    end = text.rindex('}')
    body = text[:end].rstrip()
    lines = ',\n'.join(' ' * indent + json.dumps(k) + ': ' + json.dumps(v, indent=indent, ensure_ascii=False).replace('\n', '\n' + ' ' * indent)
                       for k, v in pairs)
    return body + ',\n' + lines + '\n}\n'


def plan(package):
    row = read(package / 'row.json')
    bounds = read(package / 'module-bounds.json')
    recipe = read(package / 'recipe.json')
    sid = row['id']
    files = {}
    for kind, module in row['modules'].items():
        data = (package / 'modules' / f'{kind}.glb').read_bytes()
        if hashlib.sha256(data).hexdigest() != module['sha256'] or len(data) != module['bytes']:
            raise ValueError(f'{kind} module bytes differ from the row')
        if module['url'] != f'/street-kits/pilots/{sid}/{kind}.glb':
            raise ValueError(f'{kind} module URL is not the pilot convention')
        files[PUBLIC / module['url'].lstrip('/')] = data
    if set(bounds) != {m['sha256'] for m in row['modules'].values()}:
        raise ValueError('Module bounds do not cover exactly the modules')
    updates = {}
    for root in (FRONT, BACK):
        path = root / 'nativeStreetPilots.json'
        text = path.read_text(encoding='utf-8')
        old = next((r for r in json.loads(text) if r['id'] == sid), None)
        if old is not None and old != row:
            raise ValueError('A different revision of this street is already registered')
        if old is None:
            updates[path] = splice_list(text, [row])
        roster_path = root / 'classroomStarter.json'
        roster_text = roster_path.read_text(encoding='utf-8')
        release = dict(domain='street', representation='native-modules', archetypeId=row['sourceArchetypeId'], variantId=sid,
                       revision=row['sourceRecipeSha256'], status='local-pilot-runtime-pending')
        previous = next((e for e in json.loads(roster_text)['entries'] if e.get('variantId') == sid), None)
        if previous is not None and previous != release:
            raise ValueError('A different roster release is already registered')
        if previous is None:
            updates[roster_path] = splice_list(roster_text, [release], 'entries')
    bounds_path = FRONT / 'nativeStreetModuleBounds.json'
    bounds_text = bounds_path.read_text(encoding='utf-8')
    known = json.loads(bounds_text)
    for sha, value in bounds.items():
        if sha in known and known[sha] != value:
            raise ValueError('Existing bounds differ for immutable module bytes')
    new_bounds = [(k, v) for k, v in bounds.items() if k not in known]
    if new_bounds:
        updates[bounds_path] = splice_object(bounds_text, new_bounds)
    cards_path = FRONT / 'classroomExpansion.json'
    cards_text = cards_path.read_text(encoding='utf-8')
    cards = json.loads(cards_text)
    entry = dict(domain='street', title=row['title'], archetype_id=row['sourceArchetypeId'], variant_id=sid, version=sid, placement_id=sid,
                 sha256=row['sourceAssemblySha256'], asset_review='agent_native_visual_and_geometry_pass', runtime_status='NOT TESTED', completed=False)
    asset = dict(id=sid, kind='street', definitionVersion=1, readiness='pilot', label=row['title'],
                 description='20 m pedestrian mall: granite promenade, brick frontage, lindens, heritage lamps and cafe patios. Street only; no buildings.',
                 thumbnail=row['thumbnailUrl'], model=dict(variantId=sid, revision=row['sourceRecipeSha256'], method='native_street_modules_v1'),
                 calgaryGuide=dict(groupId='active', basis='form_reference'), reshapeMode='fixed_section_route', sectionWidth=row['widthM'],
                 properties=dict(road_archetype_id=row['sourceArchetypeId'], road_selected_variant_id=sid, width=row['widthM'], lane_count=0,
                                 pick_place_street_section=sid, pick_place_automatic_3d=True, pick_place_definition_version=1,
                                 community_3d_mask_existing_tiles=True,
                                 road_standard_citation='City Prompt original teaching concept after Stephen Avenue; not a City of Calgary drawing'))
    for field, ident, value in (('entries', 'variant_id', entry), ('assets', 'id', asset)):
        previous = [x for x in cards[field] if x.get(ident) == sid]
        if previous and previous[0] != value:
            raise ValueError(f'A different classroom {field[:-1]} is already registered')
        if not previous:
            cards_text = splice_list(cards_text, [value], field)
    if cards_text != cards_path.read_text(encoding='utf-8'):
        updates[cards_path] = cards_text
    presentation_path = FRONT / 'cataloguePresentation.json'
    presentation = read(presentation_path)
    card = dict(label=row['title'], description='Calgary\'s pedestrian mall as a street to draw: a granite promenade between brick frontage zones, with lindens, heritage lamps and cafe patios.',
                styleIds=[], searchTags=['street_pathway', 'stephen', 'avenue', 'pedestrian', 'mall', 'calgary', 'patio', 'heritage'])
    if sid in presentation and presentation[sid] != card:
        raise ValueError('A different presentation card is already registered')
    if sid not in presentation:
        updates[presentation_path] = splice_object(presentation_path.read_text(encoding='utf-8'), [(sid, card)])
    heroes_path = FRONT / 'catalogueHeroImages.json'
    heroes = read(heroes_path)
    if sid in heroes and heroes[sid] != row['thumbnailUrl']:
        raise ValueError('A different hero image is already registered')
    if sid not in heroes:
        updates[heroes_path] = splice_object(heroes_path.read_text(encoding='utf-8'), [(sid, row['thumbnailUrl'])])
    for path, data in files.items():
        if path.exists() and path.read_bytes() != data:
            raise ValueError(f'Conflicting public module bytes at {path}')
    if not (PUBLIC / row['thumbnailUrl'].lstrip('/')).is_file():
        raise ValueError('Missing hero image')
    return row, recipe, updates, files


HISTORY = r"""
import json, re, sys
from pathlib import Path
sys.path.insert(0, 'backend')
from app.services.public_realm_lego import build_public_realm_capability_catalog, public_realm_capability_fingerprint
path = Path('backend/app/data/publicRealmCatalogHistory.json')
original = path.read_text(encoding='utf-8')
history = json.loads(original)
catalog = build_public_realm_capability_catalog()
locks = {f'{c.family_id}@{c.family_version}': public_realm_capability_fingerprint(c) for c in catalog.capabilities}
retained = history['catalogs'].get(catalog.fingerprint)
if retained is not None and retained != locks:
    raise SystemExit('Historic public-realm catalogue cannot be overwritten')
if retained is None:
    start = re.search(r'"catalogs"\s*:\s*', original).end()
    _, consumed = json.JSONDecoder().raw_decode(original[start:])
    end = start + consumed - 1
    entry = json.dumps(catalog.fingerprint) + ': ' + json.dumps(locks, indent=2)
    path.write_text(original[:end] + ',\n' + entry + '\n' + original[end:], encoding='utf-8')
print(catalog.fingerprint, 'added' if retained is None else 'already recorded', len(locks))
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--package', required=True, type=Path)
    parser.add_argument('--backups', required=True, type=Path)
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    row, _, updates, files = plan(args.package)
    if not args.install:
        print(json.dumps({'dry_run': True, 'id': row['id'], 'files': sorted(str(p.relative_to(ROOT)) for p in [*updates, *files])}, indent=1))
        return
    for path, text in updates.items():
        backup = args.backups / path.relative_to(ROOT)
        if not backup.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
        path.write_text(text, encoding='utf-8')
        json.loads(path.read_text(encoding='utf-8'))
    for path, data in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    history = ROOT / 'backend/app/data/publicRealmCatalogHistory.json'
    backup = args.backups / history.relative_to(ROOT)
    if not backup.exists():
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(history, backup)
    result = subprocess.run([sys.executable, '-c', HISTORY], cwd=ROOT, capture_output=True, text=True, check=True)
    print(json.dumps({'installed': row['id'], 'registry_files': len(updates), 'modules': len(files), 'catalog': result.stdout.strip()}))


if __name__ == '__main__':
    main()
