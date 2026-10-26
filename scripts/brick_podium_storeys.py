#!/usr/bin/env python3
"""Derive/check a finite local Brick Podium tower programme from exact source bytes.

Generated GLBs stay in external artifacts. Installation is private, loopback
only, additive and refuses conflicting rows or bytes. No publication pathway.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = Path('C:/dev-artifacts/CityPrompt/student-review-20261026/brick-podium-storeys-v001')
SOURCE = 'clay-brick-podium-condo-tower-clay-v006'
SOURCE_HASH = '1ce717fb6f9246312cb359b4808e726088447f12d2c571954cb33a6a91dd0869'
VARIANT = 'brick_podium_glass_tower'
FAMILY = 'claude-brick-podium-condo-tower'
PROGRAM = 'brick-podium-condo-storey-program-v001'
# Keep all terrace furniture plus the first tower storey in the fixed lower
# assembly. A clean ordinary middle floor contains complete balcony/glass bays.
BANDS = [('podium', 0, 12.3, 3), ('floor', 15.3, 18.3, 1), ('roof', 42.3, 50.1, 0)]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def derive(source: Path, output: Path):
    if digest(source) != SOURCE_HASH:
        raise ValueError('Brick Podium source differs from reviewed v006 bytes')
    sys.path.insert(0, str(ROOT))
    from tools.archetype_compiler.blender_locator import find_blender
    import trimesh
    output.mkdir(parents=True, exist_ok=True)
    if (output / 'program.json').exists():
        return load_program(output)  # Never overwrite a completed derivation.
    modules = []
    for role, lower, upper, storeys in BANDS:
        path = output / f'{PROGRAM}-{role}.glb'
        if path.exists():
            raise ValueError(f'Partial derivation exists; preserve and choose a new output: {path}')
        result = subprocess.run([find_blender(), '-b', '--python-exit-code', '1', '--python',
            str(ROOT / 'tools/archetype_compiler/blender_extract_vertical_module.py'), '--',
            str(source), str(path), str(lower), str(upper)], capture_output=True, text=True, timeout=180)
        if result.returncode:
            raise ValueError(result.stdout + result.stderr)
        scene = trimesh.load(path, force='scene', process=False)
        bounds = scene.bounds.tolist()
        dimensions = [bounds[1][0]-bounds[0][0], bounds[1][2]-bounds[0][2], upper-lower]
        if abs(bounds[0][1]) > .001 or abs(bounds[1][1]-(upper-lower)) > .001:
            raise ValueError(f'Clipped {role} has incorrect vertical bounds: {bounds}')
        modules.append(dict(role=role, path=path.name, source_vertical_band_m=[lower, upper],
            native_dimensions_m=dimensions, source_frame_bounds_y_up_m=bounds,
            occupied_storeys=storeys, bytes=path.stat().st_size, sha256=digest(path)))
    program = dict(schema='cityprompt.authored-building-storey-program@1', id=PROGRAM, method='RLASM 6.1',
        source=dict(candidate=SOURCE, variant_id=VARIANT, path=str(source.resolve()), sha256=SOURCE_HASH,
                    native_storeys=13, native_height_m=50.1),
        supported_storeys=dict(minimum=13, maximum=40, recommended_minimum=15, recommended_maximum=40),
        height_contract=dict(podium_storeys=3, podium_height_m=12.3, repeatable_storey_height_m=3, roof_height_m=7.8),
        modules=modules, review=dict(status='LOCAL_PILOT_PENDING_BROWSER_REVIEW', seed_activation=False,
            keeper_claimed=False, notes=['Exact native 13-storey source remains unchanged.',
                'Complete podium terrace plus first tower floor retained; ordinary floor repeats at 3m.',
                'Source XY coordinates and tower/crown offsets retained; no vertical mesh scaling.']))
    (output / 'program.json').write_text(json.dumps(program, indent=2)+'\n', encoding='utf-8')
    return load_program(output)


def load_program(output: Path):
    program = json.loads((output / 'program.json').read_text(encoding='utf-8'))
    if program['id'] != PROGRAM or program['source']['sha256'] != SOURCE_HASH or digest(program['source']['path']) != SOURCE_HASH:
        raise ValueError('Programme source lock changed')
    if [(row['role'], *row['source_vertical_band_m'], row['occupied_storeys']) for row in program['modules']] != BANDS:
        raise ValueError('Authored band contract changed')
    rows = []
    for module in program['modules']:
        path = output / module['path']
        if path.stat().st_size != module['bytes'] or digest(path) != module['sha256']:
            raise ValueError(f"Changed derived module: {module['role']}")
        role = module['role']
        width, depth, height = module['native_dimensions_m']
        rows.append(dict(id=str(uuid.uuid5(uuid.NAMESPACE_URL, f'https://cityprompt.ai/local/{PROGRAM}/{role}')),
            name=f'Brick Podium Condo Tower local {role}', variantId=VARIANT,
            model_url=f'/api/v1/files/library/local-student-review/{module["sha256"]}.glb',
            metadata=dict(rlasm=dict(method='RLASM', method_version='6.1', delivery_format='architectural_clay_module_v1',
                runtime_enabled=True, continuous_resize_allowed=False, source_locked=True, variant_id=VARIANT,
                candidate=SOURCE, model_sha256=module['sha256'], source_model_sha256=SOURCE_HASH,
                storey_program_id=PROGRAM, local_pilot=True),
                lego=dict(enabled=True, family=FAMILY, role=role, width_m=width, depth_m=depth, height_m=height,
                    archetype_ids=['condo_podium_tower', VARIANT], reuse_keys=[VARIANT], min_floors=13, max_floors=40,
                    repeatable_z=role=='floor', occupied_storeys=module['occupied_storeys'], variant_key=VARIANT,
                    source_variant_id=VARIANT, generation_archetype_id=VARIANT, allow_inset_footprint=True,
                    placement_contract=dict(mode='authored_storey_program', continuous_resize_allowed=False, storey_program_id=PROGRAM)))))
    return program, rows


def synchronize(output: Path, *, apply=False, owner_id=None):
    sys.path[:0] = [str(ROOT), str(ROOT/'backend')]
    from app.core.config import get_settings
    from app.services.render_attempt_storage import _client
    from app.models.models import ModelLibraryEntry, User
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from scripts.classroom_model_library import object_matches
    settings = get_settings()
    if any(urlsplit(value).hostname not in {'localhost', '127.0.0.1', '::1'}
           for value in [settings.database_url, settings.s3_endpoint_url]):
        raise ValueError('Brick Podium local pilot requires loopback database and storage')
    program, rows = load_program(output)
    engine = create_engine(settings.database_url_sync)
    client, bucket = _client()
    report = []
    try:
        with Session(engine) as database:
            owner = database.get(User, owner_id) if owner_id else None
            if not owner or not owner.is_active:
                raise ValueError('Supply an existing local --owner-id')
            for row, module in zip(rows, program['modules'], strict=True):
                existing = database.get(ModelLibraryEntry, uuid.UUID(row['id']))
                if existing and (existing.is_public or existing.owner_id != owner_id or existing.model_url != row['model_url'] or existing.metadata_ != row['metadata']):
                    raise ValueError('Existing local pilot row differs; it was not overwritten')
                status = object_matches(client, bucket, row)
                if status == 'conflict':
                    raise ValueError('Stored local pilot has different bytes; it was not overwritten')
                report.append(dict(role=module['role'], binding='verified' if existing else 'missing', object=status,
                                   id=row['id'], sha256=module['sha256']))
            if apply:
                for row, module, status in zip(rows, program['modules'], report, strict=True):
                    if status['object'] == 'missing':
                        with (output / module['path']).open('rb') as body:
                            client.put_object(Bucket=bucket, Key=row['model_url'].removeprefix('/api/v1/files/'), Body=body,
                                              ContentType='model/gltf-binary', IfNoneMatch='*')
                    if status['binding'] == 'missing':
                        database.add(ModelLibraryEntry(id=uuid.UUID(row['id']), owner_id=owner_id, name=row['name'],
                            category='building', model_url=row['model_url'], lod_urls={'0':row['model_url']}, generation_engine='rlasm',
                            is_public=False, tags=['local-student-review', VARIANT], metadata_=row['metadata']))
                database.commit()
    finally:
        engine.dispose()
    if apply:
        return synchronize(output, owner_id=owner_id)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts', type=Path, default=ARTIFACTS)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--owner-id', type=uuid.UUID)
    parser.add_argument('--env-file', type=Path, help='Optional local backend environment file; values are never printed')
    args = parser.parse_args()
    if args.env_file:
        from dotenv import load_dotenv
        load_dotenv(args.env_file)
    program, rows = derive(args.source, args.artifacts) if args.source else load_program(args.artifacts)
    report = synchronize(args.artifacts, apply=args.install, owner_id=args.owner_id) if args.install or args.verify else {
        'program':program['id'], 'module_count':len(rows), 'source_sha256':SOURCE_HASH, 'publication':False}
    print(json.dumps(report, indent=2))
    return int(isinstance(report, list) and any(row['binding'] != 'verified' or row['object'] != 'verified' for row in report))


if __name__ == '__main__':
    raise SystemExit(main())
