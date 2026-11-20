"""Register a built rail street package as a local drawable street pilot. Dry run by default.

    python3 tools/rail_streets/install.py --package <build directory> --backups <directory> [--install]

Additive only: every registry file is spliced as text, so existing records keep their
exact bytes. Refuses to overwrite a different revision, module, card or lesson. Backups
of every changed file go to --backups. Runtime acceptance and publication remain separate.
Adapted from tools/stephen_avenue_street/install.py.
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

TRANSIT_LESSON = dict(
    eraIds=['late_twentieth', 'contemporary'], status='classified', profileId='transit_recent', formId='transit',
    styleIds=['contemporary_street'], constructionYear=None, dateBasis='approximate_design_association',
    referenceReviewed=False, priorStyleConfidence='Medium')
LESSONS = {
    'student_median_lrt_avenue_v1': dict(
        designPeriod='Late-twentieth-century and current light rail, drawn as a contemporary teaching section',
        eraRationale='Median light rail on arterials is a late-twentieth-century and current transit form; this section is generic, not a dated design.',
        canadianContext="Calgary's light rail, opened in 1981, runs largely at grade. Compare how a fenced median line affects crossings, turns and the streets either side.",
        internationalContext='Many North American cities run light rail in arterial medians; European tramways more often share the street or run on grass track.',
        sourceIds=['tod', 'complete', 'shared'], planningIds=['tod', 'complete'],
        designEvidence='A 34 m arterial with fenced ballasted double light-rail track and centre catenary poles in its median.'),
    'student_lrt_right_of_way_v1': dict(
        designPeriod='Late-twentieth-century and current light rail, drawn as a contemporary teaching section',
        eraRationale='Light rail on its own right-of-way beside roads and rail corridors is a late-twentieth-century and current form; this section is generic.',
        canadianContext="Calgary's light rail, opened in 1981, often runs on its own corridor beside major roads, with regional pathways alongside. Compare its barrier effect with a median line.",
        internationalContext='Separate rights-of-way let light rail run faster and more reliably than street running, at the cost of fewer crossing points.',
        sourceIds=['tod', 'complete', 'ecology'], planningIds=['tod', 'active'],
        designEvidence='A 20 m fenced corridor: ballasted double light-rail track with side masts, a regional pathway and a drainage swale.'),
    'student_high_speed_rail_line_v1': dict(
        eraIds=['postwar', 'contemporary'],
        designPeriod='High-speed rail since 1964, drawn as a contemporary slab-track section',
        eraRationale='Japan opened the first high-speed line in 1964; slab track, paired masts and security fencing reflect current practice.',
        canadianContext='Canada has no high-speed line in service; links such as Calgary to Edmonton have been studied for decades. Compare station access with the corridor\'s barrier effect.',
        internationalContext='Japan, Europe and China run large high-speed networks; lines are fully fenced and grade-separated, with no level crossings.',
        sourceIds=['tod', 'complete'], planningIds=['tod', 'compact'],
        designEvidence='A 30 m fenced corridor: double slab track on a low embankment with paired overhead-line masts, ditches and a maintenance road.'),
}


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


def splice_object(text, pairs, indent=2, key=None):
    """Add key/value pairs before the closing brace of a JSON object (the top level, or the
    object under `key`), at that object's member indentation."""
    if key is None:
        end = text.rindex('}')
        depth = indent
    else:
        start = re.search(r'"' + re.escape(key) + r'"\s*:\s*', text).end()
        _, consumed = json.JSONDecoder().raw_decode(text[start:])
        end = start + consumed - 1
        line = text[text.rfind('\n', 0, start) + 1:start]
        depth = len(line) - len(line.lstrip()) + indent
    body = text[:end].rstrip()
    pad = ' ' * depth
    lines = ',\n'.join(pad + json.dumps(k) + ': ' + json.dumps(v, indent=indent, ensure_ascii=False).replace('\n', '\n' + pad)
                       for k, v in pairs)
    return body + ',\n' + lines + '\n' + ' ' * (depth - indent) + text[end:]


def plan(package):
    row = read(package / 'row.json')
    bounds = read(package / 'module-bounds.json')
    card = read(package / 'card.json')
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
    image = (package / 'card.png').read_bytes()
    if hashlib.sha256(image).hexdigest() != row['referenceSha256']:
        raise ValueError('The card image is not the locked reference')
    files[PUBLIC / row['thumbnailUrl'].lstrip('/')] = image
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
    asset = dict(id=sid, kind='street', definitionVersion=1, readiness='pilot', label=row['title'], description=card['asset_description'],
                 thumbnail=row['thumbnailUrl'], model=dict(variantId=sid, revision=row['sourceRecipeSha256'], method='native_street_modules_v1'),
                 calgaryGuide=dict(groupId=card['group'], basis='form_reference'), reshapeMode='fixed_section_route', sectionWidth=row['widthM'],
                 properties=dict(road_archetype_id=row['sourceArchetypeId'], road_selected_variant_id=sid, width=row['widthM'], lane_count=card['lane_count'],
                                 pick_place_street_section=sid, pick_place_automatic_3d=True, pick_place_definition_version=1,
                                 community_3d_mask_existing_tiles=True,
                                 road_standard_citation='City Prompt original teaching section; not a City of Calgary or rail operator drawing'))
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
    shown = dict(label=card['label'], description=card['description'], styleIds=[], searchTags=card['search'])
    if sid in presentation and presentation[sid] != shown:
        raise ValueError('A different presentation card is already registered')
    if sid not in presentation:
        updates[presentation_path] = splice_object(presentation_path.read_text(encoding='utf-8'), [(sid, shown)])
    heroes_path = FRONT / 'catalogueHeroImages.json'
    heroes = read(heroes_path)
    if sid in heroes and heroes[sid] != row['thumbnailUrl']:
        raise ValueError('A different hero image is already registered')
    if sid not in heroes:
        updates[heroes_path] = splice_object(heroes_path.read_text(encoding='utf-8'), [(sid, row['thumbnailUrl'])])
    history_path = FRONT / 'cataloguePlanningHistory.json'
    history_text = history_path.read_text(encoding='utf-8')
    lesson = {**TRANSIT_LESSON, **LESSONS[sid], 'placementId': sid, 'domain': 'street_pathway', 'archetypeId': row['sourceArchetypeId'],
              'variantId': sid, 'modelMethod': 'native_street_modules_v1', 'modelRevision': row['sourceRecipeSha256']}
    existing = json.loads(history_text)['lessons'].get(sid)
    if existing is not None and existing != lesson:
        raise ValueError('A different planning-history lesson is already registered')
    if existing is None:
        updates[history_path] = splice_object(history_text, [(sid, lesson)], key='lessons')
    for path, data in files.items():
        if path.exists() and path.read_bytes() != data:
            raise ValueError(f'Conflicting public file at {path}')
    return row, updates, files


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
    parser.add_argument('--no-history', action='store_true', help='skip recording the catalogue fingerprint (when installing several in a row)')
    args = parser.parse_args()
    row, updates, files = plan(args.package)
    if not args.install:
        print(json.dumps({'dry_run': True, 'id': row['id'], 'files': sorted(str(p.relative_to(ROOT)) for p in [*updates, *files])}, indent=1))
        return
    for path, text in updates.items():
        backup = args.backups / path.relative_to(ROOT)
        if not backup.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
        json.loads(text)
        path.write_text(text, encoding='utf-8')
    for path, data in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    if args.no_history:
        print(json.dumps({'installed': row['id'], 'registry_files': len(updates), 'public_files': len(files), 'catalog': 'not recorded'}))
        return
    history = ROOT / 'backend/app/data/publicRealmCatalogHistory.json'
    backup = args.backups / history.relative_to(ROOT)
    if not backup.exists():
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(history, backup)
    result = subprocess.run([sys.executable, '-c', HISTORY], cwd=ROOT, capture_output=True, text=True, check=True)
    print(json.dumps({'installed': row['id'], 'registry_files': len(updates), 'public_files': len(files), 'catalog': result.stdout.strip()}))


if __name__ == '__main__':
    main()
