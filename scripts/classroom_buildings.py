"""Finite classroom building selection; exact clay assets, additive local install.

Offline by default. --write-catalogue generates cards; --stage-public copies
locked references. --install/--verify use configured loopback services only.
This does not approve browser behaviour or replace existing model bindings.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.catalogue_promotion import LIBRARY, picker_assets, validate_review
from tools.rlasm_clay_library import _validate_payload, clay_seed_rows

SELECTION = Path('seed/classroom-buildings/selection.json')
EXPANSION = Path('frontend/src/data/classroomExpansion.json')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def load_selection(root=ROOT, *, hydrated=True):
    selection = read(root / SELECTION)
    library = read(root / LIBRARY)
    locks = selection['buildings']
    if selection.get('schema') != 'cityprompt.classroom-building-selection@1' or len(locks) != 8:
        raise ValueError('Expected the finite eight-building classroom selection')
    by_candidate = {entry['candidate']: entry for entry in library['entries']}
    if len({item['candidate'] for item in locks}) != len(locks):
        raise ValueError('Duplicate building candidate')
    selected = []
    baseline = {entry['variant_id'] for entry in read(root/'frontend/src/data/validationCatalogue.json')['entries'] if entry['domain']=='building'}
    for lock in locks:
        entry = by_candidate.get(lock['candidate'])
        if not entry or entry['model']['sha256'] != lock['sha256'] or entry['variant_id'] in baseline:
            raise ValueError('Missing, changed or already selected building')
        validate_review(entry, root)
        selected.append(entry)
    if len({entry['variant_id'] for entry in selected}) != 8:
        raise ValueError('Duplicate exact variant')
    payload = {**library, 'entries': selected}
    if hydrated:
        _validate_payload(payload, clay_root=(root/LIBRARY).parent, repo_root=root)
    return payload


def catalogue_records(payload):
    assets = picker_assets(payload)
    entries = []
    for entry, asset in zip(payload['entries'], assets):
        # New classroom placements are one complete model. Legacy saved repeat
        # plots keep their own flags and previously compiled geometry.
        asset.update(readiness='pilot', reshapeMode='fixed_native', definitionVersion=2,
                     reshapeDescription='One complete building at its native size. Resize its surrounding plot; use Place another for a second building.')
        asset['properties'].update(native_home_plot=False, native_plot_axes=True, pick_place_automatic_3d=True)
        entries.append(dict(domain='building', title=asset['label'], archetype_id=entry['archetype_id'],
                            variant_id=entry['variant_id'], version=entry['candidate'], placement_id=asset['id'],
                            sha256=entry['model']['sha256'], asset_review='PASS_INDEPENDENT_ARCHITECTURAL_CLAY',
                            runtime_status='NOT TESTED', completed=False))
    return entries, assets


def write_catalogue(payload, root=ROOT):
    data = read(root/EXPANSION)
    entries, assets = catalogue_records(payload)
    data['entries'] = [e for e in data['entries'] if e['domain'] != 'building'] + entries
    data['assets'] = [a for a in data['assets'] if a.get('zoneType') != 'building'] + assets
    (root/EXPANSION).write_text(json.dumps(data, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')


def stage_references(payload, public_root, root=ROOT):
    files = []
    for entry in payload['entries']:
        for ref in entry['references']:
            rel = Path(ref['repo_path']).relative_to('frontend/public')
            source, target = root/ref['repo_path'], public_root/rel
            if hashlib.sha256(source.read_bytes()).hexdigest() != ref['sha256']:
                raise ValueError('Source hash changed')
            if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() != ref['sha256']:
                raise ValueError('Existing public reference differs; preserve it')
            files.append((source, target))
    for source, target in files:
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    return len(files)


def install(payload, *, apply=False, owner_id=None):
    from scripts.classroom_model_library import synchronize, validate_target
    sys.path.insert(0, str(ROOT/'backend'))
    from app.core.config import get_settings
    from app.services.render_attempt_storage import _client
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    settings = get_settings()
    # Pending classroom candidates must never install into remote services.
    validate_target(settings, {}, local_trial=True)
    dependencies, rows = [], []
    for entry, row in zip(payload['entries'], clay_seed_rows(payload)):
        dependency = entry['candidate']
        dependencies.append(dict(id=dependency, path=str(LIBRARY.parent/entry['model']['path'])))
        rows.append(dict(id=row['id'], variantId=entry['variant_id'], name=row['name'],
                         model_url=row['model_url'], metadata=row['metadata'], modelDependency=dependency))
    engine = create_engine(settings.database_url_sync)
    client, bucket = _client()
    try:
        with Session(engine) as db:
            return synchronize(db, client, bucket, {'dependencies':dependencies}, rows,
                               apply=apply, owner_id=owner_id, root=ROOT)
    finally:
        engine.dispose()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-catalogue', action='store_true')
    parser.add_argument('--stage-public', type=Path)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--install', action='store_true')
    mode.add_argument('--verify', action='store_true')
    parser.add_argument('--owner-id', type=uuid.UUID)
    args=parser.parse_args()
    if args.install and not args.owner_id:
        parser.error('--install needs an existing local --owner-id')
    payload=load_selection()
    if args.write_catalogue:write_catalogue(payload)
    if args.stage_public:print('Verified/staged references:',stage_references(payload,args.stage_public))
    if args.install or args.verify:
        report=install(payload, apply=args.install, owner_id=args.owner_id)
        print(json.dumps(report,indent=2))
        if any(r['binding']!='verified' or r['object']!='verified' for r in report):return 1
    print('Eight exact classroom buildings verified. Browser acceptance remains pending.')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
