"""Exact independently reviewed Claude building trials. Unreviewed candidates remain disabled.

Reviewed GLBs use the manifest-relative LFS object package by default.
--artifact-root retains support for an external models/ delivery. No regeneration.
Run from backend to use the same .env as the local server. Default is read-only.
"""
import argparse
import copy
import json
from pathlib import Path, PurePosixPath
import sys
import uuid
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.rlasm_clay_library import _validate_payload, clay_seed_rows
from tools.catalogue_promotion import validate_review, picker_assets, TRIAL_CHECKS
from scripts.classroom_model_library import synchronize

MANIFEST = ROOT / 'seed/claude-five-trial/library.json'
ALLOWED_CANDIDATES = {'clay-baronial-railway-hotel-clay-v006', 'clay-zinc-dome-corner-block-clay-v007', 'clay-grand-magasin-clay-v008', 'clay-modernista-market-hall-clay-v007', 'clay-second-empire-city-hall-clay-v010'}


def _require_hydrated(path, label):
    if not path.is_file():
        raise ValueError(f'Missing {label}: {path}. Run git lfs pull for the trial models and locked references, or supply a hydrated --artifact-root.')
    with path.open('rb') as stream:
        if stream.read(128).startswith(b'version https://git-lfs.github.com/spec/v1'):
            raise ValueError(f'Unhydrated Git LFS pointer for {label}: {path}. Run git lfs pull before checking or installing the trial.')


def _model_validation_layout(payload, artifacts, *, external_override=False):
    """Adapt only the approved durable location to the unchanged clay validator.

    Do not alter the manifest payload used for seeding or installed provenance.
    A package has one model layout; arbitrary parent paths and symlink escapes fail.
    """
    checked = copy.deepcopy(payload)
    validation_roots = set()
    durable_prefix = ('..', 'model-library', 'objects', 'claude-five', 'models')
    for entry in checked['entries']:
        raw = entry['model']['path']
        path = PurePosixPath(raw)
        if '\\' in raw or path.suffix != '.glb' or path.is_absolute():
            raise ValueError(f'Unsafe trial model path: {raw}')
        if len(path.parts) == 2 and path.parts[0] == 'models':
            validation_root = artifacts
        elif len(path.parts) == 6 and path.parts[:-1] == durable_prefix:
            validation_root = artifacts.parent / 'model-library/objects/claude-five'
        else:
            raise ValueError(f'Model path must use models/ or the approved Claude trial LFS object directory: {raw}')
        if external_override:
            validation_root = artifacts
        validation_root = validation_root.resolve()
        model = (validation_root / 'models' / path.name).resolve()
        if not model.is_relative_to(validation_root / 'models'):
            raise ValueError(f'Unsafe trial model path escapes its approved directory: {raw}')
        _require_hydrated(model, 'trial GLB')
        entry['model']['path'] = 'models/' + path.name
        validation_roots.add(validation_root)
    if len(validation_roots) != 1:
        raise ValueError('A trial package must use one consistent model layout')
    return checked, validation_roots.pop()


def load_bindings(artifacts=None, manifest=MANIFEST, repo=ROOT):
    payload = json.loads(Path(manifest).read_text(encoding='utf-8'))
    entries = payload['entries']
    if not entries or any(e['candidate'] not in ALLOWED_CANDIDATES for e in entries):
        raise ValueError('Only independently reviewed Claude local trials are enabled')
    for entry in entries:
        if entry.get('local_trial_only') is True:
            continue
        approval, trial = entry.get('activation', {}), entry.get('local_trial', {})
        model_hash = entry['model']['sha256']
        if (entry.get('local_trial_only') is not False
                or approval.get('authorized_by') != 'human_user'
                or not all(approval.get(k) for k in ('quote', 'date'))
                or approval.get('model_sha256') != model_hash
                or trial.get('model_sha256') != model_hash
                or not all(trial.get(k) for k in ('project_url', 'tested_by', 'tested_at', 'evidence'))
                or any(trial.get('checks', {}).get(k) is not True for k in TRIAL_CHECKS)):
            raise ValueError('Published Claude models require exact activation and completed local trial')
    artifact_root = Path(artifacts).resolve() if artifacts is not None else Path(manifest).resolve().parent
    checked, clay_root = _model_validation_layout(payload, artifact_root, external_override=artifacts is not None)
    for entry in entries:
        for reference in entry['references']:
            _require_hydrated(Path(repo) / reference['repo_path'], 'locked reference')
    _validate_payload(checked, clay_root=clay_root, repo_root=repo)
    for entry in entries:
        validate_review(entry, repo)
    picker_assets(payload)  # Native dimensions, clearance, identity and group contract.
    rows = list(clay_seed_rows(payload))
    for row, entry in zip(rows, entries):
        row['variantId'] = entry['variant_id']
        row['modelDependency'] = entry['candidate']
        row['metadata']['rlasm']['import_scope'] = 'local_trial_only'
        row['metadata']['rlasm']['source_delivery'] = entry['source']
    # Upload exactly the external bytes that were checked, without changing seed provenance.
    dependencies = checked['entries'] if artifacts is not None else entries
    return {'dependencies': [{'id':e['candidate'], 'path':e['model']['path']} for e in dependencies]}, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-root', type=Path,
                        help='Read models/<filename> from this external root; omit for the manifest-relative Git package')
    parser.add_argument('--owner-project-id', type=uuid.UUID)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--apply', action='store_true')
    modes.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    roster, rows = load_bindings(args.artifact_root)
    if not (args.apply or args.verify):
        print('PASS: exact model bytes, transformed dimensions, sources and independent review'); return
    sys.path.insert(0, str(ROOT/'backend'))
    from app.core.config import get_settings
    from app.models.models import Project
    from app.services.render_attempt_storage import _client
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    settings = get_settings()
    if any(urlsplit(v).hostname not in {'localhost','127.0.0.1','::1'} for v in (settings.database_url, settings.s3_endpoint_url)):
        raise ValueError('Local database and storage only')
    engine = create_engine(settings.database_url_sync)
    client, bucket = _client()
    try:
        with Session(engine) as db:
            owner = None
            if args.apply:
                project = db.get(Project, args.owner_project_id) if args.owner_project_id else None
                if project is None: raise ValueError('Provide an existing local owner project')
                owner = project.owner_id
            report = synchronize(db,client,bucket,roster,rows,apply=args.apply,owner_id=owner,
                                 root=args.artifact_root if args.artifact_root is not None else MANIFEST.parent)
            print(json.dumps(report))
            if any(r['binding'] != 'verified' or r['object'] != 'verified' for r in report):
                raise SystemExit(1)
    finally:
        engine.dispose()


if __name__ == '__main__': main()
