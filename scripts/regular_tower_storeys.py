#!/usr/bin/env python3
"""Finite source-locked local tower derivatives; no publication or Z scaling."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import shutil
import subprocess
import sys
import uuid
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = Path('C:/dev-artifacts/CityPrompt/tower-storey-options-20261027/regular')
CONTRACTS = {
    'blue': dict(candidate='glass_tower_podium_modern-clay-v003', variant='glass_tower_blue_reflective',
        family='blue-glass-office-tower', program='blue-glass-office-storey-program-v001',
        sha256='de6faa2fa3b7abe467b6902767f42e26d0f45813fa696b9aed1abfa5fe2c9c43',
        native=25, minimum=15, maximum=40, native_height=99.0, podium_storeys=3,
        podium_height=15.0, typical_height=3.5, roof_height=7.0,
        bands=[('podium', 0.0, 15.0, 3), ('floor', 18.5, 22.0, 1), ('roof', 92.0, 99.0, 0)],
        archetype='glass_tower_podium_modern', plot=[36.0, 34.0]),
    'plus15': dict(candidate='clay-plus15-glass-office-tower-clay-v006',variant='plus15_contemporary_glass',
        family='claude-plus15-glass-office-tower',program='plus15-glass-office-storey-program-v001',
        sha256='1f12b3c94ed7405e43fde35450b31a7e5561b937fd854ff8a0c92bc65db35851',
        native=17,minimum=10,maximum=35,native_height=82.66000366210938,podium_storeys=1,
        podium_height=14.0,typical_height=3.65,roof_height=10.26000366210938,
        bands=[('podium',0.0,14.0,1),('floor',43.2,46.85,1),('roof',72.4,82.66000366210938,0)],
        archetype='calgary_plus_15_connected_tower',plot=[55.0,86.0]),
    'slab': dict(candidate='clay-slab-balcony-tower-clay-v007',variant='midcentury_concrete_slab',
        family='claude-slab-balcony-tower',program='slab-balcony-storey-program-v001',
        sha256='042c09a9198f60fb0116ab93b6fd073309717a24a59925f31c2db1aed67d7d40',
        native=13,minimum=8,maximum=30,native_height=47.0,podium_storeys=3,
        podium_height=10.5,typical_height=2.95,roof_height=7.0,
        bands=[('podium',0.0,10.5,3),('floor',22.3,25.25,1),('roof',40.0,47.0,0)],
        archetype='west_end_mid_century_tower',plot=[41.0,41.0]),
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def assembly_plan(tower, storeys):
    spec = CONTRACTS[tower]
    if type(storeys) is not int or not spec['minimum'] <= storeys <= spec['maximum']:
        raise ValueError('Storey count is outside the finite authored programme')
    if storeys == spec['native']:
        return [dict(role='source', elevation_m=0.0)]
    parts = [dict(role='podium', elevation_m=0.0)]
    repeat = storeys - spec['podium_storeys']
    parts.extend(dict(role='floor', elevation_m=spec['podium_height'] + i * spec['typical_height']) for i in range(repeat))
    parts.append(dict(role='roof', elevation_m=spec['podium_height'] + repeat * spec['typical_height']))
    return parts


def derive(tower, source, output):
    spec = CONTRACTS[tower]
    source, output = Path(source), Path(output)
    if digest(source) != spec['sha256']:
        raise ValueError('Exact tower source hash differs from the reviewed source')
    if (output / 'program.json').exists():
        return load_program(tower, output)
    if output.exists() and any(output.iterdir()):
        raise ValueError('Partial derivation exists; preserve it and choose a new version')
    entry = next(row for row in json.loads((ROOT / 'seed/model-library/rlasm-architectural-clay/library.json').read_text(encoding='utf-8'))['entries'] if row['candidate'] == spec['candidate'])
    locked = []
    for reference in entry['references']:
        filename = Path(reference['repo_path']).name
        choices = [ROOT / reference['repo_path'], Path(entry['external_evidence'])/'sources'/filename,
            Path(entry['external_evidence'])/'source-package'/'locked-sources'/filename]
        path = next((p for p in choices if p.is_file() and digest(p) == reference['sha256']), None)
        if path is None:
            raise ValueError('Exact catalogue source is missing: '+reference['role'])
        locked.append((reference,path))
    sys.path.insert(0, str(ROOT))
    from tools.archetype_compiler.blender_locator import find_blender
    import trimesh
    output.mkdir(parents=True, exist_ok=True)
    (output/'sources').mkdir()
    source_records = []
    for reference,path in locked:
        target = output/'sources'/path.name
        shutil.copyfile(path,target)
        source_records.append(dict(reference,path=str(target.resolve())))
    (output/'source-lock.json').write_text(json.dumps(dict(status='SOURCE_HASHES_VERIFIED',references=source_records),indent=2)+'\n',encoding='utf-8')
    modules = []
    for role, lower, upper, occupied in spec['bands']:
        target = output / f'{spec["program"]}-{role}.glb'
        result = subprocess.run([find_blender(), '-b', '--python-exit-code', '1', '--python',
            str(ROOT / 'tools/archetype_compiler/blender_extract_vertical_module.py'), '--',
            str(source), str(target), str(lower), str(upper)], capture_output=True, text=True, timeout=180)
        if result.returncode:
            raise ValueError(result.stdout + result.stderr)
        scene = trimesh.load(target, force='scene', process=False)
        bounds = scene.bounds.tolist()
        if abs(bounds[0][1]) > .001 or abs(bounds[1][1] - (upper-lower)) > .001:
            raise ValueError(f'Incorrect vertical bounds for {role}: {bounds}')
        modules.append(dict(role=role, path=target.name, source_vertical_band_m=[lower, upper],
            native_dimensions_m=[bounds[1][0]-bounds[0][0], bounds[1][2]-bounds[0][2], upper-lower],
            source_frame_bounds_y_up_m=bounds, occupied_storeys=occupied,
            bytes=target.stat().st_size, sha256=digest(target)))
    program = dict(schema='cityprompt.authored-building-storey-program@1', id=spec['program'], method='RLASM 6.1',
        source=dict(candidate=spec['candidate'], variant_id=spec['variant'], path=str(source.resolve()), sha256=spec['sha256'],
            native_storeys=spec['native'], native_height_m=spec['native_height'], references=entry['references']),
        supported_storeys=dict(minimum=spec['minimum'], maximum=spec['maximum']),
        height_contract=dict(podium_storeys=spec['podium_storeys'], podium_height_m=spec['podium_height'],
            repeatable_storey_height_m=spec['typical_height'], roof_height_m=spec['roof_height']),
        placement_plot_m=spec['plot'], modules=modules,
        review=dict(status='independent_review_pending', seed_activation=False, keeper_claimed=False,
            notes=['Native storey selection uses unchanged whole source GLB bytes.',
                'Source-world XY retained; complete authored floor translations only; vertical scale remains one.',
                'Runtime integration and local browser verification remain NOT TESTED.']))
    (output / 'program.json').write_text(json.dumps(program, indent=2)+'\n', encoding='utf-8')
    return load_program(tower, output)


def load_program(tower, output):
    import trimesh
    spec = CONTRACTS[tower]
    output = Path(output)
    program = json.loads((output / 'program.json').read_text(encoding='utf-8'))
    if program['id'] != spec['program'] or program['source']['sha256'] != spec['sha256'] or digest(program['source']['path']) != spec['sha256']:
        raise ValueError('Programme source lock changed')
    if program['source'].get('references'):
        source_lock = json.loads((output/'source-lock.json').read_text(encoding='utf-8'))
        if [(r['role'],r['sha256']) for r in source_lock['references']] != [(r['role'],r['sha256']) for r in program['source']['references']]:
            raise ValueError('Catalogue source enrollment changed')
        for row in source_lock['references']:
            if digest(row['path']) != row['sha256']:
                raise ValueError('Catalogue source bytes changed')
    actual = [(m['role'], *m['source_vertical_band_m'], m['occupied_storeys']) for m in program['modules']]
    if actual != spec['bands']:
        raise ValueError('Authored band contract changed')
    source_bounds=trimesh.load(program['source']['path'],force='scene',process=False).bounds
    source_origin=[float((source_bounds[0][axis]+source_bounds[1][axis])/2) for axis in (0,2)]
    rows = []
    for module in program['modules']:
        target = output / module['path']
        if target.stat().st_size != module['bytes'] or digest(target) != module['sha256']:
            raise ValueError('Derived module bytes changed')
        role = module['role']
        width, depth, height = module['native_dimensions_m']
        lower,upper = module['source_vertical_band_m']
        if width <= 0 or depth <= 0 or abs(height-(upper-lower)) > .0001:
            raise ValueError('Module dimensions differ from the authored band')
        rows.append(dict(id=str(uuid.uuid5(uuid.NAMESPACE_URL, f'https://cityprompt.ai/local/{spec["program"]}/{role}')),
            name=f'{tower.title()} tower local {role}', variantId=spec['variant'],
            model_url=f'/api/v1/files/library/local-student-review/{module["sha256"]}.glb',
            metadata=dict(rlasm=dict(method='RLASM', method_version='6.1', delivery_format='architectural_clay_module_v1',
                runtime_enabled=True, continuous_resize_allowed=False, source_locked=True, variant_id=spec['variant'],
                candidate=spec['candidate'], model_sha256=module['sha256'], source_model_sha256=spec['sha256'],
                storey_program_id=spec['program'], local_pilot=True),
                lego=dict(enabled=True, family=spec['family'], role=role, width_m=width, depth_m=depth, height_m=height,
                    archetype_ids=[spec['archetype'], spec['variant']], reuse_keys=[spec['variant']],
                    min_floors=spec['minimum'], max_floors=spec['maximum'], repeatable_z=role=='floor',
                    occupied_storeys=module['occupied_storeys'], variant_key=spec['variant'],
                    source_variant_id=spec['variant'], generation_archetype_id=spec['variant'], allow_inset_footprint=True,
                    placement_contract=dict(mode='authored_storey_program', continuous_resize_allowed=False,
                        storey_program_id=spec['program'],source_frame_origin_xy_m=source_origin)))))
    return program, rows


def assemble(tower, output, storeys):
    import trimesh
    program, _ = load_program(tower, output)
    output = Path(output)
    target = output / f'{tower}-{storeys}-storeys.glb'
    if target.exists():
        raise ValueError('Comparison assembly exists; preserve it')
    plan = assembly_plan(tower, storeys)
    if plan[0]['role'] == 'source':
        shutil.copyfile(program['source']['path'], target)
    else:
        modules = {m['role']: output / m['path'] for m in program['modules']}
        result = trimesh.Scene()
        for index, part in enumerate(plan):
            scene = trimesh.load(modules[part['role']], force='scene', process=False)
            scene.apply_translation([0, part['elevation_m'], 0])
            for name in scene.graph.nodes_geometry:
                matrix, geometry = scene.graph[name]
                result.add_geometry(scene.geometry[geometry], transform=matrix, node_name=f'{index}-{name}', geom_name=f'{index}-{geometry}')
        target.write_bytes(result.export(file_type='glb'))
    return target


def boards(tower, output):
    """Letterboxed evidence only; never crop or retouch source or model pixels."""
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    output = Path(output)
    program,_ = load_program(tower,output)
    folders = sorted((output/'renders').iterdir(),key=lambda p:int(p.name.split('-')[-2]))
    if len(folders) != 3 or any(not (folder/'render-manifest.json').exists() for folder in folders):
        raise ValueError('Complete low, native and high render sets are required before boards')
    destination = output/'boards'
    destination.mkdir(exist_ok=False)
    sources = {r['role']:Path(r['path']) for r in json.loads((output/'source-lock.json').read_text())['references']}
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf',24)
    def label(canvas,xy,text):
        ImageDraw.Draw(canvas).text(xy,text,font=font,fill='#263238')
    def panel(canvas,path,box):
        x,y,w,h=box
        with Image.open(path) as original:
            image = ImageOps.contain(original.convert('RGB'),(w,h),Image.Resampling.LANCZOS)
        canvas.paste(image,(x+(w-image.width)//2,y+(h-image.height)//2))
    source_board=Image.new('RGB',(1800,620),'#f2f0e8')
    label(source_board,(20,15),program['source']['candidate']+' / LOCKED CATALOGUE SOURCES')
    for index,role in enumerate(('front','oblique','top')):
        label(source_board,(20+index*600,65),role)
        panel(source_board,sources[role],(10+index*600,105,580,490))
    source_board.save(destination/'locked-source-board.png')
    for folder in folders:
        phone=Image.new('RGB',(1080,1920),'#f2f0e8')
        label(phone,(24,24),folder.name+' / EXACT GLB DERIVATIVE')
        label(phone,(24,65),'Local review only. Native count retains original whole GLB.')
        for index,(role,view) in enumerate([('front','front'),('oblique','front_corner'),('top','aerial')]):
            y=130+index*555
            label(phone,(24,y),'SOURCE / '+role)
            label(phone,(552,y),'EXACT GLB / '+view)
            panel(phone,sources[role],(24,y+45,504,455))
            panel(phone,folder/(view+'.png'),(552,y+45,504,455))
        label(phone,(24,1830),'No AI generation. Full-resolution originals retained in renders/.')
        label(phone,(24,1870),'Independent review and classroom runtime checks are separate.')
        phone.save(destination/(folder.name+'-source-phone.png'))
        phone=Image.new('RGB',(1080,1920),'#f2f0e8')
        label(phone,(24,24),folder.name+' / CONSTRUCTION AND REPEAT SEAM')
        detail_views = ('architecture_close','glass_close','facade_close','roof_contact','lobby_contact','repeat_seam')
        if tower == 'plus15':
            detail_views = ('architecture_close','glass_close','facade_close','roof_contact','plus15_bridge','repeat_seam')
        elif tower == 'slab':
            detail_views = ('architecture_close','glass_close','balcony_close','roof_contact','fin_contact','repeat_seam')
        for index,view in enumerate(detail_views):
            x=24+(index%2)*528; y=110+(index//2)*555
            label(phone,(x,y),view)
            panel(phone,folder/(view+'.png'),(x,y+45,504,455))
        label(phone,(24,1830),'Letterboxing and labels only. No retouching, relighting or cropping.')
        phone.save(destination/(folder.name+'-construction-phone.png'))
    phone=Image.new('RGB',(1080,1920),'#f2f0e8')
    label(phone,(24,20),tower.upper()+' / FINITE AUTHORED STOREY OPTIONS')
    for index,folder in enumerate(folders):
        y=80+index*600
        label(phone,(24,y),folder.name)
        panel(phone,folder/'front_corner.png',(24,y+40,1032,540))
    phone.save(destination/'storey-options-phone.png')
    return destination


def validate_review(tower, output):
    output = Path(output)
    path = output/'independent-programme-review.json'
    if not path.is_file():
        raise ValueError('Independent programme review is required before local installation')
    review = json.loads(path.read_text(encoding='utf-8'))
    reviewer=review.get('reviewer')
    scope=review.get('scope')
    if (review.get('candidate') != CONTRACTS[tower]['program']
        or review.get('decision') != 'PASS_SCOPED_ARCHITECTURAL_CLAY_DERIVATIVE'
        or not isinstance(reviewer,str) or not reviewer.strip() or '/regular_tower_options' in reviewer
        or not isinstance(scope,str) or len(scope.strip())<40
        or 'architectural' not in scope.lower() or 'clay' not in scope.lower()
        or review.get('result_class')!='category_closure_only'
        or any(type(review.get(key)) is not int or review[key]!=0 for key in ('unresolved_p0','unresolved_p1'))
        or review.get('reviewed_programme_sha256') != digest(output/'program.json')):
        raise ValueError('Independent review does not pass or bind current programme bytes')
    return review


def existing_row_matches(existing,row,owner_id):
    return (str(existing.owner_id)==str(owner_id) and existing.is_public is False
        and existing.name==row['name'] and existing.category=='building'
        and existing.generation_engine=='rlasm' and existing.model_url==row['model_url']
        and existing.lod_urls=={'0':row['model_url']}
        and existing.tags==['local-student-review',row['variantId']]
        and existing.metadata_==row['metadata'])


def origin_migration_metadata(current, old, new, owner_id):
    """Only an exact task-owned preimage can gain the measured common origin."""
    without_origin=copy.deepcopy(new)
    del without_origin['metadata']['lego']['placement_contract']['source_frame_origin_xy_m']
    if (without_origin != old or current['id'] != old['id']
        or str(current['owner_id']) != str(owner_id) or current['is_public']
        or current['model_url'] != old['model_url']
        or current['metadata'] not in (old['metadata'],new['metadata'])):
        raise ValueError('Source-origin migration conflict; existing row preserved')
    return copy.deepcopy(new['metadata'])


def migrate_blue_source_origin(output, receipt, owner_id):
    """Narrow transactional migration of this task's three original Blue rows."""
    output,receipt=Path(output),Path(receipt)
    validate_review('blue',output)
    program,rows=load_program('blue',output)
    old_rows=json.loads(receipt.read_text(encoding='utf-8'))['blue']
    installed_path=output/'local-install-verification.json'
    installed=json.loads(installed_path.read_text(encoding='utf-8'))
    if len(old_rows)!=3 or {(r['id'],r['sha256']) for r in installed if r['binding']=='verified' and r['object']=='verified'} != {(r['id'],r['metadata']['rlasm']['model_sha256']) for r in old_rows}:
        raise ValueError('Exact original installation receipt is required; rows preserved')
    sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
    from app.core.config import get_settings
    from app.services.render_attempt_storage import _client
    from app.models.models import ModelLibraryEntry,User
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from scripts.classroom_model_library import object_matches
    settings=get_settings()
    if any(urlsplit(v).hostname not in {'localhost','127.0.0.1','::1'} for v in [settings.database_url,settings.s3_endpoint_url]):
        raise ValueError('Source-origin migration requires loopback services')
    engine=create_engine(settings.database_url_sync);client,bucket=_client()
    preimages=[];updates=[]
    try:
        with Session(engine) as database:
            owner=database.get(User,owner_id)
            if not owner or not owner.is_active:raise ValueError('Existing active task owner is required')
            for old,new in zip(old_rows,rows,strict=True):
                existing=database.get(ModelLibraryEntry,uuid.UUID(old['id']),with_for_update=True)
                if existing is None:raise ValueError('Original task row is missing; preserved')
                if not (existing_row_matches(existing,old,owner_id) or existing_row_matches(existing,new,owner_id)):
                    raise ValueError('Full original task binding differs; existing row preserved')
                current=dict(id=str(existing.id),owner_id=str(existing.owner_id),is_public=existing.is_public,
                    name=existing.name,category=existing.category,generation_engine=existing.generation_engine,
                    model_url=existing.model_url,lod_urls=copy.deepcopy(existing.lod_urls),tags=copy.deepcopy(existing.tags),
                    metadata=copy.deepcopy(existing.metadata_))
                metadata=origin_migration_metadata(current,old,new,owner_id)
                if object_matches(client,bucket,old)!='verified':raise ValueError('Original object differs; row preserved')
                preimages.append(current);updates.append((existing,metadata))
            preimage_path=output/'source-origin-migration-preimage.json'
            if preimage_path.exists():
                previous=json.loads(preimage_path.read_text(encoding='utf-8'))
                if previous['old_binding_receipt_sha256']!=digest(receipt) or previous['owner_id']!=str(owner_id):
                    raise ValueError('Existing migration preimage differs; preserved')
            else:
                preimage_path.write_text(json.dumps(dict(owner_id=str(owner_id),old_binding_receipt_sha256=digest(receipt),
                    original_install_receipt_sha256=digest(installed_path),rows=preimages,
                    origin_before=None,origin_after=rows[0]['metadata']['lego']['placement_contract']['source_frame_origin_xy_m']),indent=2)+'\n',encoding='utf-8')
            for existing,metadata in updates:existing.metadata_=metadata
            database.commit()
    finally:engine.dispose()
    report=synchronize('blue',output,owner_id=owner_id)
    (output/'source-origin-migration-verification.json').write_text(json.dumps(dict(rows=report,
        origin_before=None,origin_after=rows[0]['metadata']['lego']['placement_contract']['source_frame_origin_xy_m'],
        existing_ids_retained=True,geometry_and_source_unchanged=True),indent=2)+'\n',encoding='utf-8')
    return report


def synchronize(tower, output, *, apply=False, owner_id=None):
    """Install additive private rows with the Brick pilot's loopback-only protocol."""
    if apply:
        validate_review(tower,output)
    sys.path[:0] = [str(ROOT), str(ROOT/'backend')]
    from app.core.config import get_settings
    from app.services.render_attempt_storage import _client
    from app.models.models import ModelLibraryEntry, User
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session
    from scripts.classroom_model_library import object_matches
    from scripts.private_local_pilot_ids import private_local_pilot_id
    settings = get_settings()
    if any(urlsplit(value).hostname not in {'localhost', '127.0.0.1', '::1'} for value in [settings.database_url, settings.s3_endpoint_url]):
        raise ValueError('Local programme requires loopback database and storage')
    program, rows = load_program(tower, output)
    engine = create_engine(settings.database_url_sync)
    client, bucket = _client()
    report = []
    try:
        with Session(engine) as database:
            owner = database.get(User, owner_id) if owner_id else None
            if not owner or not owner.is_active:
                raise ValueError('Supply an existing local --owner-id')
            for row, module in zip(rows, program['modules'], strict=True):
                legacy = database.get(ModelLibraryEntry, uuid.UUID(row['id']))
                selected_id = private_local_pilot_id(row['id'], owner_id, legacy.owner_id if legacy else None)
                row['id'] = str(selected_id)
                existing = legacy if legacy and legacy.id == selected_id else database.get(ModelLibraryEntry, selected_id)
                if existing and not existing_row_matches(existing,row,owner_id):
                    raise ValueError('Existing local programme row differs; preserved')
                status = object_matches(client, bucket, row)
                if status == 'conflict':
                    raise ValueError('Stored programme has different bytes; preserved')
                report.append(dict(role=module['role'], binding='verified' if existing else 'missing', object=status, id=row['id'], sha256=module['sha256']))
            if apply:
                for row, module, status in zip(rows, program['modules'], report, strict=True):
                    if status['object'] == 'missing':
                        with (Path(output) / module['path']).open('rb') as body:
                            client.put_object(Bucket=bucket, Key=row['model_url'].removeprefix('/api/v1/files/'), Body=body, ContentType='model/gltf-binary', IfNoneMatch='*')
                    if status['binding'] == 'missing':
                        database.add(ModelLibraryEntry(id=uuid.UUID(row['id']), owner_id=owner_id, name=row['name'], category='building',
                            model_url=row['model_url'], lod_urls={'0': row['model_url']}, generation_engine='rlasm', is_public=False,
                            tags=['local-student-review', CONTRACTS[tower]['variant']], metadata_=row['metadata']))
                database.commit()
    finally:
        engine.dispose()
    return synchronize(tower, output, owner_id=owner_id) if apply else report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('tower', choices=CONTRACTS)
    parser.add_argument('--artifacts', type=Path)
    parser.add_argument('--source', type=Path)
    parser.add_argument('--assemble', type=int, nargs='*')
    parser.add_argument('--boards', action='store_true')
    parser.add_argument('--install', action='store_true')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--migrate-source-origin',type=Path,help='Blue only: exact original full binding receipt')
    parser.add_argument('--owner-id', type=uuid.UUID)
    parser.add_argument('--env-file', type=Path)
    args = parser.parse_args()
    if args.env_file:
        from dotenv import load_dotenv
        load_dotenv(args.env_file)
    output = args.artifacts or ARTIFACTS / (args.tower+'-v001')
    if args.migrate_source_origin:
        if args.tower!='blue':raise ValueError('Only the original task-created Blue rows have a migration path')
        print(json.dumps(migrate_blue_source_origin(output,args.migrate_source_origin,args.owner_id),indent=2))
        return 0
    program, rows = derive(args.tower, args.source, output) if args.source else load_program(args.tower, output)
    for count in args.assemble or []:
        assemble(args.tower, output, count)
    if args.boards:
        boards(args.tower,output)
    report = synchronize(args.tower, output, apply=args.install, owner_id=args.owner_id) if args.install or args.verify else dict(program=program['id'], module_count=len(rows), publication=False)
    print(json.dumps(report, indent=2))
    return int(isinstance(report, list) and any(r['binding'] != 'verified' or r['object'] != 'verified' for r in report))


if __name__ == '__main__':
    raise SystemExit(main())
