"""Synchronize a finite local street candidate and preserve existing recipe locks.

Stage and inspect source assets first. This operation activates ordinary local
authoring for one candidate; it never records visual approval or publication.
Run with the backend Python environment so capability fingerprints use the
same implementation as saved projects. --check is read-only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
FRONT = ROOT / 'frontend/src/data'
BACK = ROOT / 'backend/app/data'
COHORT = {
    'student_quiet_residential_street_v1', 'student_planted_shared_lane_v1',
    'brt_bus_rapid_transit_corridor_v0', 'amsterdam_gracht_v1', 'landmark_signature_bridge_v2',
    'student_cycle_avenue_v1', 'student_green_alley_v1', 'student_school_street_v1',
}


def read(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path: Path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')


def check():
    assert read(FRONT/'nativeStreetPilots.json') == read(BACK/'nativeStreetPilots.json'), 'Street registry mirrors differ'
    native = lambda root: [row for row in read(root/'classroomStarter.json')['entries']
                           if row['representation'] == 'native-modules']
    assert native(FRONT) == native(BACK), 'Street roster mirrors differ'
    from app.services.native_street_candidate_contract import native_street_runtime_capabilities
    native_street_runtime_capabilities.cache_clear()
    native_street_runtime_capabilities()
    print('PASS: native street registry, roster and executable capability locks agree')


def activate(manifest: Path, variant: str):
    if variant not in COHORT:
        raise ValueError('Only the explicitly scoped native streets may be added')
    check()
    matches = [row for row in read(manifest) if row['id'] == variant]
    if len(matches) != 1:
        raise ValueError('Choose exactly one staged candidate')
    row = matches[0]
    existing = read(FRONT/'nativeStreetPilots.json')
    previous = next((item for item in existing if item['id'] == variant), None)
    if previous is not None and previous != row:
        raise ValueError('An active revision cannot be overwritten; introduce an explicit version migration')
    from app.services.public_realm_lego import build_public_realm_capability_catalog, public_realm_capability_fingerprint
    catalog = build_public_realm_capability_catalog()
    history = read(BACK/'publicRealmCatalogHistory.json')
    history['catalogs'][catalog.fingerprint] = {
        f'{cap.family_id}@{cap.family_version}': public_realm_capability_fingerprint(cap)
        for cap in catalog.capabilities
    }
    from app.services.native_street_candidate_contract import build_native_street_candidate_catalog
    build_native_street_candidate_catalog(manifest)  # Validate all staged inputs before mutation.
    if previous is None:
        existing.append(row)
    entry = dict(domain='street', representation='native-modules', archetypeId=row['sourceArchetypeId'],
                 variantId=variant, revision=row['sourceRecipeSha256'], status='local-pilot-runtime-pending')
    rosters = {root: read(root/'classroomStarter.json') for root in (FRONT, BACK)}
    for roster in rosters.values():
        if not any(item.get('variantId') == variant and item['representation'] == 'native-modules'
                   for item in roster['entries']):
            roster['entries'].append(entry)
    write(BACK/'publicRealmCatalogHistory.json', history)
    for root in (FRONT, BACK):
        write(root/'nativeStreetPilots.json', existing)
        write(root/'classroomStarter.json', rosters[root])
    print(f'Activated local candidate {variant}; runtime acceptance remains pending. Run --check in a fresh process.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--add-local-candidate', choices=sorted(COHORT))
    args = parser.parse_args()
    if args.check:
        check()
    elif args.manifest and args.add_local_candidate:
        activate(args.manifest, args.add_local_candidate)
    else:
        parser.error('Use --check or --manifest PATH --add-local-candidate ID')
