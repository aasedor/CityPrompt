"""Finite complete landmark assemblies, derived from exact authored clay sources.

Generation is offline. Explicit --install adds reviewed private loopback rows
and objects only; public catalogue activation and paid generation are absent.
Native choices always copy the reviewed GLB bytes. Alternate assemblies rebuild
the source schedule at unchanged storey pitches; no mesh clipping or Z scaling.
Run one pilot and obtain independent review before the next finite build.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tokenize
import types
import uuid
from datetime import datetime, timezone
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = Path('C:/dev-artifacts/CityPrompt/tower-storey-options-20261027/landmarks')
SOURCES = {
    'twisted': dict(
        variant_id='glass_tower_twisted', candidate='glass-tower-twisted-clay-v005',
        native_storeys=40, counts=[20, 30, 40],
        native_review='review/independent-review.json',
        directory='C:/dev-artifacts/CityPrompt/skyscraper-trio-2026-09-08/twisted-v005',
        model_sha256='932dc2152becbf9e74f2c7d83f314d6f93853be9794c628852a5e4154d010978',
        builder='twisted.py', builder_sha256='6c73ca68498bf67b8f6d8a7c6dc4a6f9846cab6da6755db6ce139a90ad1302d4',
        width_m=46., depth_m=46.,
    ),
    'gilded': dict(
        variant_id='art_deco_cream_terracotta', candidate='showcase-tower-clay-v005',
        native_storeys=17, counts=[17, 25, 35],
        native_review='review/independent-architectural-clay-review.json',
        directory='C:/dev-artifacts/CityPrompt/showcase-nine-2026-09-27/buildings/tower-v005',
        model_sha256='a0b4f53281c43b0cd3a98f057a5da4ea0de5f56476e7a6227074d79e61a54b80',
        builder='tower.py', builder_sha256='5d09bad4216326375bacdb695e9bd2718d50585b59c63bbed2b42f3e5db5618a',
        width_m=32., depth_m=28.,
    ),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def programme_for(family: str, storeys: int) -> dict:
    if family not in SOURCES or type(storeys) is not int or storeys not in SOURCES[family]['counts']:
        raise ValueError('Unsupported explicit landmark storey choice')
    s = SOURCES[family]
    p = dict(
        schema='cityprompt.authored-building-storey-program@1',
        id=f"{s['variant_id']}-authored-heights-v001", assembly_strategy='select_authored_assembly',
        source_variant_id=s['variant_id'], source_revision=s['candidate'],
        source_model_sha256=s['model_sha256'], occupied_storeys=storeys,
        supported_storeys=s['counts'], minimum=min(s['counts']), maximum=max(s['counts']),
        native_storeys=s['native_storeys'], native_exact_copy=storeys == s['native_storeys'],
        vertical_scale=1, horizontal_scale_mode='native_complete_assembly',
        target_footprint_m=dict(width=s['width_m'], depth=s['depth_m']),
        review_state='independent_review_pending', runtime_integration='NOT TESTED',
        runtime_seed_allowed=False, keeper_claimed=False,
    )
    if family == 'twisted':
        lower, upper = {20: (9, 9), 30: (14, 14), 40: (20, 18)}[storeys]
        garden = 10 + lower * 3.4
        upper_base = garden + 4
        crown = upper_base + upper * 3.4
        p.update(lobby_height_m=10, garden_height_m=4, garden_base_m=garden,
                 crown_base_m=crown, height_m=round(crown + 4.5, 6),
                 stacks=[dict(floors=n, base_m=base, top_m=base+n*3.4,
                              floor_pitch_m=3.4, rotation_degrees=[-12, 12])
                         for n, base in [(lower, 10), (upper, upper_base)]],
                 identity_contract=['Full trussed and glazed lobby retained',
                     'Two complete five-sided rotating office stacks, each -12 to +12 degrees',
                     'Whole planted transfer garden, guards, supports and core access retained',
                     'Whole mechanical crown, roof plant and crescent garden retained'])
    else:
        # 16:9 keeps the principal shaft/next setback ratio nearest native7:4,
        # while the two upper occupied tiers remain equal and fully retained.
        counts = {17: [2, 7, 4, 2, 2], 25: [2, 11, 6, 3, 3], 35: [2, 16, 9, 4, 4]}[storeys]
        tiers = []
        z = 0.
        for i, (w, d, n) in enumerate(zip([32, 31, 25, 19.4, 13.4], [28, 27, 22, 17, 11.6], counts)):
            top = round(z + n * (3.6 if i == 0 else 3.4), 6)
            tiers.append(dict(width_m=w, depth_m=d, floors=n, base_m=z, top_m=top,
                              floor_pitch_m=3.6 if i == 0 else 3.4))
            z = top
        p.update(tiers=tiers, crown_base_m=z, height_m=round(z + 10.4, 6),
                 identity_contract=['Dark two-storey retail/mezzanine podium retained',
                     'All four occupied cross-plan setback stages retained',
                     'Native terracotta openings, pier width, capitals and sunburst relief retained',
                     'Complete octagonal lantern, eight gilded buttresses, shoulder roof and finial rigid translated'])
    return p


def private_binding(contract: dict) -> dict:
    """Proposed private row only. Caller must gate installation on exact review.

    Native source pin and all alternatives share one finite programme family.
    This function never installs rows and never mutates the original public row.
    """
    family=next(k for k,v in SOURCES.items() if v['variant_id']==contract['source_variant_id'])
    spec=SOURCES[family]
    native=contract['occupied_storeys']==spec['native_storeys']
    if native and contract['sha256']!=spec['model_sha256']:
        raise ValueError('Native programme row must retain the exact original source hash')
    candidate=spec['candidate'] if native else contract['candidate']
    n=contract['occupied_storeys'];dims=contract['native_dimensions_m']
    rlasm=dict(method='RLASM',method_version='6.1',delivery_format='architectural_clay_module_v1',
        runtime_enabled=True,continuous_resize_allowed=False,source_locked=True,local_pilot=True,
        candidate=candidate,variant_id=spec['variant_id'],source_model_sha256=spec['model_sha256'],
        model_sha256=contract['sha256'],storey_program_id=contract['id'])
    lego=dict(enabled=True,family=contract['id'],role='assembled',repeatable_z=False,
        width_m=dims['width'],depth_m=dims['depth'],height_m=dims['height'],
        archetype_ids=[spec['variant_id']],reuse_keys=[spec['variant_id']],
        native_floors=n,occupied_storeys=n,min_floors=n,max_floors=n,
        variant_key=spec['variant_id'],source_variant_id=spec['variant_id'],
        generation_archetype_id=spec['variant_id'],allow_inset_footprint=True,
        placement_contract=dict(mode='authored_storey_program',continuous_resize_allowed=False,
                                storey_program_id=contract['id']))
    return dict(id=str(uuid.uuid5(uuid.NAMESPACE_URL,f"https://cityprompt.ai/local/{contract['id']}/{n}")),
        is_public=False,variantId=spec['variant_id'],name=f"{spec['variant_id']} local authored {n} storeys",
        model_url=f"/api/v1/files/library/local-student-review/{contract['sha256']}.glb",
        modelDependency=f'assembled:{n}',metadata=dict(rlasm=rlasm,lego=lego),
        source_path=contract['path'],source_bytes=contract['bytes'],source_sha256=contract['sha256'])


def twisted_camera_roster(roster: list[dict], programme: dict) -> list[dict]:
    result=copy.deepcopy(roster)
    if programme['native_exact_copy']:
        return result
    lower=programme['stacks'][0]
    middle=(lower['base_m']+lower['top_m'])/2
    for camera in result:
        if camera['name'] in ('facade_close','glass_close'):
            camera['target']=[*camera['target'][:2],middle]
            camera['location']=[*camera['location'][:2],middle+(5 if camera['name']=='facade_close' else 2)]
    return result


def normal_surface_geometry(outline: list[tuple], thickness: float):
    """Retain the exact front plane and thicken inward along its own normal."""
    if len(outline)<3 or thickness<=0:
        raise ValueError('A pane needs a valid outline and positive thickness')
    a,b,d=outline[0],outline[1],outline[-1]
    u=[b[i]-a[i] for i in range(3)];v=[d[i]-a[i] for i in range(3)]
    normal=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
    length=sum(x*x for x in normal)**.5
    if length<1e-10:
        raise ValueError('Pane outline is degenerate')
    normal=[x/length for x in normal]
    n=len(outline)
    vertices=list(outline)+[tuple(p[i]-normal[i]*thickness for i in range(3)) for p in outline]
    faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]+[(i,i+n,(i+1)%n+n,(i+1)%n) for i in range(n)]
    return vertices,faces


def _replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f'Exact authored expression changed: {old}')
    return text.replace(old, new)


def _numeric_datums(text: str, mapping: dict[float, float]) -> str:
    """Replace audited absolute datums, leaving dimensions/strings untouched."""
    tokens = []
    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        if token.type == tokenize.NUMBER and float(token.string) in mapping:
            token = token._replace(string=repr(round(mapping[float(token.string)], 8)))
        tokens.append(token)
    return tokenize.untokenize(tokens)


def adapt_builder(family: str, storeys: int, path: Path) -> str:
    p = programme_for(family, storeys)
    s = SOURCES[family]
    if sha256(path) != s['builder_sha256']:
        raise ValueError('Exact authored source hash differs; refusing adaptation')
    code = path.read_text(encoding='utf-8')
    if family == 'twisted':
        lower, upper = p['stacks']
        code = _replace_once(code, '[(10,20),(82,18)]', repr([(10, lower['floors']), (upper['base_m'], upper['floors'])]))
        # Numeric datums only. Native dimensions (.35 columns, 9m core etc.)
        # remain unchanged. Core walls are re-authored to the new top datum.
        garden_delta = p['garden_base_m'] - 78
        crown_delta = p['crown_base_m'] - 143.2
        mapping = {v: v + garden_delta for v in [78, 78.35, 78.4, 79.5, 80, 80.2, 82, 88]}
        mapping.update({v: v + crown_delta for v in [143, 143.2, 143.45, 143.85, 144.1, 144.2, 144.35, 144.6, 146, 146.2, 147.7, 170]})
        mapping[71.6] = p['crown_base_m'] / 2
        code = _numeric_datums(code, mapping)
        # Numeric replacement also sees upper-base and garden numbers inserted
        # above. For these choices the new values do not collide with originals.
        code = _replace_once(code, 'STOREYS=40', f'STOREYS={storeys}')
    else:
        old = 'tiers=[(32,28,0,7.2,2),(31,27,7.2,31,7),(25,22,31,44.6,4),\n           (19.4,17,44.6,51.4,2),(13.4,11.6,51.4,58.2,2)]'
        schedule = [(t['width_m'], t['depth_m'], t['base_m'], t['top_m'], t['floors']) for t in p['tiers']]
        code = _replace_once(code, old, 'tiers=' + repr(schedule))
        before, crown = code.split('    # Octagonal lantern:', 1)
        crown, after = crown.split('    # Source front entrance hierarchy', 1)
        delta = p['crown_base_m'] - 58.2
        datums = {float(t.string) for t in tokenize.generate_tokens(io.StringIO(crown).readline)
                  if t.type == tokenize.NUMBER and float(t.string) >= 58.2}
        crown = _numeric_datums(crown, {v: v + delta for v in datums})
        code = before + '    # Octagonal lantern:' + crown + '    # Source front entrance hierarchy' + after
        code = _replace_once(code,"C.solid_surface('lantern optical bay'","B.normal_solid_surface('lantern optical bay'")
    compile(code, str(path), 'exec')
    return code


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _json(path: Path, value: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def locked_sources(spec: dict, catalogue_entry: dict) -> list[dict]:
    source=Path(spec['directory'])
    archived=json.loads((source/'source-entry.json').read_text(encoding='utf-8'))
    if archived['variant_id']!=spec['variant_id']:
        raise ValueError('Archived reference variant differs from exact source')
    result=[]
    for reference in catalogue_entry['references']:
        match=next((r for r in archived['sources'] if r['role']==reference['role'] and r['sha256']==reference['sha256']),None)
        if match is None:
            raise ValueError('Catalogue and archived exact reference hashes differ')
        path=source/match['path']
        if path.stat().st_size!=reference['bytes'] or sha256(path)!=reference['sha256']:
            raise ValueError('Exact reference bytes changed')
        result.append(dict(role=reference['role'],original_path=str(path),path='sources/'+Path(reference['repo_path']).name,
                           bytes=reference['bytes'],sha256=reference['sha256']))
    return result


def build_worker(a):
    """Blender-only execution; imports occur after offline source checks."""
    p = programme_for(a.family, a.storeys)
    s = SOURCES[a.family]
    source = Path(s['directory'])
    native = source / (s['candidate'] + '.glb')
    if sha256(native) != s['model_sha256']:
        raise ValueError('Native source GLB hash changed')
    if p['native_exact_copy']:
        if a.dry_run:
            print(json.dumps(dict(dry_run=True, native_exact_copy=True, source_hash=s['model_sha256'], no_geometry_written=True)))
            return
        a.output.mkdir(parents=True, exist_ok=False)
        target = a.output / native.name
        shutil.copy2(native, target)
        assert sha256(target) == s['model_sha256']
        dimensions = json.loads((source/'build-report.json').read_text())['native_dimensions_m']
        p.update(path=str(target), sha256=sha256(target), bytes=target.stat().st_size,
                 review_state='original_reviewed_exact_bytes', native_dimensions_m=dimensions,
                 target_footprint_m=dict(width=dimensions['width'], depth=dimensions['depth']))
        _json(a.output/'assembly-contract.json', p)
        _json(a.output/'proposed-private-row.json',private_binding(p))
        return
    code = adapt_builder(a.family, a.storeys, source/'scripts'/s['builder'])
    staging = OUTPUT_ROOT / '_authoring-inputs' / f'{a.family}-{a.storeys}-v{a.version:03d}'
    staging.mkdir(parents=True, exist_ok=True)
    adapted = staging/s['builder']
    if adapted.exists() and adapted.read_text(encoding='utf-8') != code:
        raise ValueError('Immutable adapted authoring source differs')
    if not adapted.exists():
        adapted.write_text(code, encoding='utf-8')
    sys.path.insert(0, str(source/'scripts'))
    import clay_core as C
    # Never update progress files in the immutable original bundle.
    C.ROOT = OUTPUT_ROOT
    module = types.ModuleType('landmark_authored_builder')
    module.__file__ = str(adapted)
    sys.modules[module.__name__] = module
    exec(compile(code, str(adapted), 'exec'), module.__dict__)
    if a.family == 'twisted':
        manifest = module.manifest(1)
        manifest['camera_roster']=twisted_camera_roster(manifest['camera_roster'],p)
        palette = module.PALETTE
        build = module.build
    else:
        B = _load('landmark_showcase_utilities', source/'scripts/build.py')
        B.normal_solid_surface=lambda name,outline,thickness,role,module:C.mesh(name,*normal_surface_geometry(outline,thickness),role,module)
        B.SPECS['tower'].update(height=p['height_m'], floors=a.storeys)
        palette = dict(B.PALETTE)
        palette.update(wall=(.66,.57,.40), stone=(.72,.64,.49), trim=(.30,.24,.12), foundation=(.08,.09,.08), roof=(.34,.34,.29))
        manifest = copy.deepcopy(json.loads((source/'prework-manifest.json').read_text()))
        roster = B.camera_roster('tower')
        # Crown proof cameras move with complete lantern, entrance stays fixed.
        for cam in roster:
            if cam['name'] in ('architecture_close', 'crown_contact'):
                cam['location'] = [*cam['location'][:2], cam['location'][2]+p['height_m']-68.6]
                cam['target'] = [*cam['target'][:2], cam['target'][2]+p['height_m']-68.6]
        manifest['camera_roster'] = roster
        build = lambda: module.build(B)
        C.fit = B.efficient_fit
    manifest.update(candidate=f"{s['candidate']}-storeys-{a.storeys:02d}-v{a.version:03d}", state='independent_review_pending',
                    runtime_seed_allowed=False, mandatory_review_views=[c['name'] for c in manifest['camera_roster']],
                    storey_programme=p)
    manifest['measurement_contract'].update(dimensions_m=dict(width=s['width_m'], depth=s['depth_m'], height=p['height_m']), storeys=a.storeys, floors=a.storeys)
    manifest['programme_contract'] = p['identity_contract']
    manifest['limitations'] = ['Alternate authored-height interpretation; original catalogue image shows native height.',
        'Architectural clay only; runtime placement, ground, editing and capture NOT TESTED.',
        'Independent scoped architectural-clay review required before local activation.']
    # Source images remain exact originals, not tall/short invented references.
    library = json.loads((ROOT/'seed/model-library/rlasm-architectural-clay/library.json').read_text())
    entries = library['entries'] if isinstance(library, dict) else library
    item = next(e for e in entries if e['candidate'] == s['candidate'])
    sources = locked_sources(s, item)
    entry = dict(archetype_id=item['archetype_id'], variant_id=s['variant_id'], directory='.', sources=sources)
    out = C.prepare_candidate(a, entry, manifest, __file__, [adapted, source/'scripts'/'support.py'] if a.family=='twisted' else [adapted, source/'scripts'/'build.py'])
    if out is None:
        return
    cams = C.setup(palette, manifest['camera_roster'], a.resolution)
    C.bpy.context.scene.cycles.samples = 24
    # Same broad neutral lighting as original source with envelope-based reach.
    factor = s['width_m']/11
    for obj in C.bpy.context.scene.objects:
        if obj.type == 'LIGHT' and not obj.name.startswith('QA interior'):
            obj.location *= factor
            obj.data.energy *= factor*factor
            obj.data.size *= factor
            C.look_at(obj, (0,0,p['height_m']*.4))
        if obj.type == 'CAMERA':
            obj.data.clip_end = 2000
    if a.family == 'gilded':
        # Preserve source bevels without per-object dependency graph rebuilds.
        def bevel(obj, width=.012, segments=1):
            if width > 0:
                m=obj.modifiers.new('Construction edge chamfer','BEVEL');m.width=width;m.segments=segments;m.limit_method='ANGLE'
        C.bevel = bevel
        C.bpy.ops.object.light_add(type='SUN')
        sun=C.bpy.context.object;sun.rotation_euler=(.45,-.5,-.45);sun.data.energy=2.2;sun.data.angle=.14
    build()
    import bmesh
    modified=[obj for obj in C.objects() if obj.modifiers]
    if modified:
        C.bpy.ops.object.select_all(action='DESELECT')
        for obj in modified:
            obj.select_set(True)
        C.bpy.context.view_layer.objects.active=modified[0]
        C.bpy.ops.object.convert(target='MESH')
    for obj in C.objects():
        bm=bmesh.new();bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
        bmesh.ops.triangulate(bm,faces=list(bm.faces))
        zero=[f for f in bm.faces if f.calc_area()<1e-10]
        if zero:bmesh.ops.delete(bm,geom=zero,context='FACES_ONLY')
        bm.to_mesh(obj.data);bm.free();obj.data.update()
    # Bounding-box fitting avoids millions of repeated projection operations.
    if a.family == 'twisted':
        B = _load('landmark_camera_utilities', Path(SOURCES['gilded']['directory'])/'scripts/build.py')
        C.fit = B.efficient_fit
    report = C.deliver(out, manifest, cams)
    p.update(path=str(out/report['runtime']['path']), sha256=report['runtime']['sha256'],
             bytes=report['runtime']['bytes'], native_dimensions_m=report['native_dimensions_m'],
             target_footprint_m=dict(width=report['native_dimensions_m']['width'],depth=report['native_dimensions_m']['depth']),
             candidate=manifest['candidate'])
    _json(out/'assembly-contract.json', p)
    _json(out/'proposed-private-row.json',private_binding(p))


def finish_evidence(output: Path):
    """Letterboxed review boards and deterministic exact-byte delivery checks.

    This records no visual approval. The reviewer must open every original.
    """
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    import math
    import trimesh
    manifest = json.loads((output/'prework-manifest.json').read_text())
    contract = json.loads((output/'assembly-contract.json').read_text())
    report = json.loads((output/'build-report.json').read_text())
    family = next(k for k,v in SOURCES.items() if v['variant_id'] == contract['source_variant_id'])
    original = Path(SOURCES[family]['directory'])
    font = 'C:/Windows/Fonts/arial.ttf'
    def label(canvas, xy, value, size=25):
        ImageDraw.Draw(canvas).text(xy, value, font=ImageFont.truetype(font,size), fill='#273438')
    def panel(canvas, path, xy, wh):
        with Image.open(path) as source:
            im=ImageOps.contain(source.convert('RGB'),wh,Image.Resampling.LANCZOS)
        canvas.paste(im,(xy[0]+(wh[0]-im.width)//2,xy[1]+(wh[1]-im.height)//2))
    boards=output/'boards'
    if (boards/'delivery-board-provenance.json').exists():
        raise ValueError('Completed evidence boards are immutable')
    source={s['role']:output/s['path'] for s in manifest['source_contract']['sources']}
    board=Image.new('RGB',(1800,600),'#f1efe6')
    label(board,(20,15),'EXACT LOCKED NATIVE CATALOGUE SOURCES',29)
    for i,role in enumerate(('front','oblique','top')):
        label(board,(20+i*600,65),role)
        panel(board,source[role],(10+i*600,105),(580,480))
    board.save(boards/'locked-source-board.png')
    phone=Image.new('RGB',(1080,1920),'#f1efe6')
    label(phone,(25,20),'COMPLETE AUTHORED HEIGHT / ARCHITECTURAL CLAY',28)
    label(phone,(25,68),f"Native {contract['native_storeys']} -> authored {contract['occupied_storeys']} storeys; Z scale 1",24)
    label(phone,(25,115),'CATALOGUE SOURCE: NATIVE HEIGHT',24)
    panel(phone,source['front'],(25,155),(1030,630))
    label(phone,(25,815),f"EXACT NATIVE GLB / {contract['native_storeys']} STOREYS",22)
    label(phone,(550,815),f"COMPLETE ALTERNATE / {contract['occupied_storeys']} STOREYS",22)
    panel(phone,original/'renders/front_corner.png',(25,865),(505,500))
    panel(phone,output/'renders/front_corner.png',(550,865),(505,500))
    label(phone,(25,1395),'ALTERNATE ROOF / CROWN',23)
    panel(phone,output/'renders/top.png',(25,1440),(1030,350))
    label(phone,(25,1820),'Catalogue reference shows native height; alternate is a design interpretation.',21)
    label(phone,(25,1860),'Exact GLB renders. Runtime and independent review remain separate.',21)
    phone.save(boards/'phone-source-comparison.png')
    phone=Image.new('RGB',(1080,1920),'#f1efe6')
    label(phone,(25,20),'CONTACTS / OCCUPIED PROGRAM / EXACT GLB',29)
    close=['architecture_close','glass_close','facade_close']
    close += ['lobby_contact','garden_contact','roof_contact'] if family=='twisted' else ['entrance_access','crown_contact','aerial']
    for i,role in enumerate(close):
        x=25+i%2*530;y=110+i//2*550
        label(phone,(x,y),role.replace('_',' '),24)
        panel(phone,output/'renders'/f'{role}.png',(x,y+45),(500,460))
    label(phone,(25,1820),'No geometry, material or lighting override after GLB reimport.',23)
    label(phone,(25,1860),'Full resolution originals retained in renders/.',23)
    phone.save(boards/'phone-construction.png')
    views=manifest['mandatory_review_views']
    board=Image.new('RGB',(1920,math.ceil(len(views)/4)*405+75),'#f1efe6')
    label(board,(20,15),manifest['candidate'],27)
    for i,role in enumerate(views):
        x=i%4*480;y=75+i//4*405
        label(board,(x+10,y),role,22)
        panel(board,output/'renders'/f'{role}.png',(x+8,y+35),(464,360))
    board.save(boards/'all-views-contact.png')
    inputs=list(source.values())+[original/'renders/front_corner.png']+sorted((output/'renders').glob('*.png'))
    _json(boards/'delivery-board-provenance.json', dict(operation='Letterboxing and labels only; no generated content or retouching',
        inputs=[dict(path=str(path),sha256=sha256(path)) for path in inputs]))
    checks={}
    for item in manifest['source_contract']['sources']:
        path=output/item['path']
        checks['source '+item['role']]=path.stat().st_size==item['bytes'] and sha256(path)==item['sha256']
    for item in manifest['provenance']['scripts']:
        checks['script '+item['path']]=sha256(output/item['path'])==item['sha256']
    path=Path(contract['path'])
    checks['exact model hash']=sha256(path)==contract['sha256']==report['runtime']['sha256']
    checks['exact native source hash']=sha256(original/(SOURCES[family]['candidate']+'.glb'))==contract['source_model_sha256']
    checks['roundtrip bounds']=report['max_roundtrip_delta_m']<1e-4
    checks['zero grade']=abs(report['delivered_bounds_m'][0][2])<1e-5
    checks['authored height']=abs(report['native_dimensions_m']['height']-contract['height_m'])<1e-4
    checks['carrier apertures']=report['carrier_aperture_audit']=='PASS_CARRIER_APERTURES'
    modules=report['authoring_modules']
    if family=='twisted':
        offices=contract['occupied_storeys']-2
        # +2 terminal stack slabs, one lobby foundation and one garden deck.
        checks['authored occupied office floors']=len(modules['floor slabs'])==offices+4
        checks['office fitout accompanies every floor']=len(modules['office fitout'])==offices*12
        checks['transfer structure preserved']=len(modules['transfer structure'])==4
    else:
        checks['authored occupied floor slabs']=len(modules['occupied storeys'])==contract['occupied_storeys']
        checks['all five closed setback roofs']=len(modules['setback roof'])==5
    scene=trimesh.load(path,force='scene',process=False)
    checks['finite meshes']=all(math.isfinite(float(v)) for mesh in scene.geometry.values() for row in mesh.vertices for v in row)
    checks['nonzero triangles']=all((mesh.area_faces>1e-12).all() for mesh in scene.geometry.values())
    for role in views:
        with Image.open(output/'renders'/f'{role}.png') as im:
            checks['render '+role]=list(im.size)==report['render_resolution']
            im.verify()
    for role,margin in report['camera_safety_margin'].items():
        checks['camera '+role]=min(margin['xmin'],margin['ymin'],1-margin['xmax'],1-margin['ymax'])>=.074
    result=dict(status='PASS_DELIVERY_CHECKS' if all(checks.values()) else 'FAIL_DELIVERY_CHECKS',
                checks=checks, model_sha256=contract['sha256'], independent_visual_review='pending',runtime_integration='NOT TESTED')
    _json(output/'evidence/delivery-verification.json',result)
    # Retain every shared gate and every unrun check visibly in the full template.
    template=(ROOT/'docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md').read_text(encoding='utf-8')
    template=template.replace('<archetype / exact variant>',contract['source_variant_id'])
    template=template.replace('- Model SHA-256 or procedural recipe ID/revision/hash:', '- Model SHA-256 or procedural recipe ID/revision/hash: '+contract['sha256'])
    template=template.replace('- Kind: building / street or path / park or open space','- Kind: building')
    template+='\n\nOffline delivery: '+manifest['candidate']+'; finite authored height '+str(contract['height_m'])+' m.\n'
    template+='All runtime checks remain NOT TESTED. This task performed no database installation, browser placement, terrain or capture trial.\n'
    template+='Asset review: independent scoped architectural-clay review pending. Publication/activation: not performed.\n'
    (output/'evidence/runtime-integration-review.md').write_text(template,encoding='utf-8')
    print(json.dumps(result,indent=2))
    return result


def validate_local_target(database_url: str, storage_url: str):
    allowed={'localhost','127.0.0.1','::1'}
    if any(urlsplit(value).hostname not in allowed for value in (database_url,storage_url)):
        raise ValueError('Landmark installation requires loopback database and storage')


def require_independent_review(review: dict, contract: dict):
    reviewer=review.get('reviewer','')
    if isinstance(reviewer,dict):
        reviewer=reviewer.get('agent','')
    passed=(review.get('architectural_clay_pass') is True or review.get('status')=='PASS_INDEPENDENT_ARCHITECTURAL_CLAY')
    if (not passed or review.get('model_sha256')!=contract['sha256']
        or not isinstance(reviewer,str) or not reviewer.strip() or '/landmark_tower_options' in reviewer
        or any(type(review.get(k)) is not int or review[k]!=0 for k in ('unresolved_p0','unresolved_p1'))
        or 'clay' not in str(review.get('scope','')).lower()):
        raise ValueError('Exact independent architectural-clay review is absent or has open findings')


def existing_row_matches(existing, row: dict, owner_id) -> bool:
    return (str(existing.owner_id)==str(owner_id) and existing.is_public is False
        and existing.name==row['name'] and existing.category=='building'
        and existing.generation_engine=='rlasm' and existing.model_url==row['model_url']
        and existing.lod_urls=={'0':row['model_url']}
        and existing.tags==['local-student-review',row['variantId']]
        and existing.metadata_==row['metadata'])


def load_completed_programme(family: str, artifacts: Path = OUTPUT_ROOT):
    """Fail closed on missing counts, changed bytes, wrong dimensions or review."""
    import trimesh
    spec=SOURCES[family]
    source=Path(spec['directory'])/(spec['candidate']+'.glb')
    if sha256(source)!=spec['model_sha256']:
        raise ValueError('Exact landmark source hash changed')
    candidates=[]
    for path in artifacts.glob('*/assembly-contract.json'):
        contract=json.loads(path.read_text(encoding='utf-8'))
        pixel_record=path.parent/'evidence/builder-pixel-review.json'
        if pixel_record.exists() and json.loads(pixel_record.read_text()).get('decision') in {'visual_rework_required','rejected','superseded'}:
            continue
        if contract.get('source_variant_id')==spec['variant_id']:
            candidates.append((path,contract))
    selected=[];rows=[]
    for n in spec['counts']:
        matches=[(path,c) for path,c in candidates if c.get('occupied_storeys')==n]
        if len(matches)!=1:
            raise ValueError(f'Exactly one reviewed complete {family} {n}-storey assembly is required')
        path,c=matches[0];expected=programme_for(family,n)
        if any(c.get(k)!=expected[k] for k in ('id','source_variant_id','source_revision','source_model_sha256','occupied_storeys','supported_storeys','native_storeys','native_exact_copy','height_m','vertical_scale')):
            raise ValueError('Landmark programme source, count or height contract changed')
        model=Path(c['path'])
        if model.resolve().parent!=path.parent.resolve() or model.stat().st_size!=c['bytes'] or sha256(model)!=c['sha256']:
            raise ValueError('Complete landmark assembly bytes changed')
        scene=trimesh.load(model,force='scene',process=False)
        bounds=scene.bounds
        dimensions=dict(width=bounds[1][0]-bounds[0][0],height=bounds[1][1]-bounds[0][1],depth=bounds[1][2]-bounds[0][2])
        if abs(bounds[0][1])>1e-4 or abs(dimensions['height']-c['height_m'])>1e-4 or any(abs(dimensions[k]-c['native_dimensions_m'][k])>1e-4 for k in dimensions):
            raise ValueError('Complete landmark native dimensions or grade changed')
        review_path=(Path(spec['directory'])/spec['native_review']) if c['native_exact_copy'] else path.parent/'review/independent-review.json'
        review=json.loads(review_path.read_text(encoding='utf-8'))
        require_independent_review(review,c)
        if c['native_exact_copy'] and c['sha256']!=spec['model_sha256']:
            raise ValueError('Native landmark bytes are not the exact original')
        selected.append(dict(contract=c,contract_path=str(path),review_path=str(review_path),review_sha256=sha256(review_path)))
        rows.append(private_binding(c))
    return selected,rows


def synchronize_private(family: str, artifacts: Path = OUTPUT_ROOT, *, apply=False, owner_id=None):
    # Offline source, geometry and review checks precede any environment access.
    selected,rows=load_completed_programme(family,artifacts)
    sys.path[:0]=[str(ROOT),str(ROOT/'backend')]
    from app.core.config import get_settings
    from app.services.render_attempt_storage import _client
    from app.models.models import ModelLibraryEntry, User
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from scripts.classroom_model_library import object_matches
    settings=get_settings()
    validate_local_target(settings.database_url,settings.s3_endpoint_url)
    engine=create_engine(settings.database_url_sync);client,bucket=_client()
    public_ids=[];report=[]
    try:
        with Session(engine) as database:
            owner=database.get(User,owner_id) if owner_id else None
            if not owner or not owner.is_active:
                raise ValueError('Supply an existing active local --owner-id')
            public_rows=database.execute(select(ModelLibraryEntry).where(ModelLibraryEntry.is_public.is_(True))).scalars().all()
            def snapshot(items):
                return {str(item.id):dict(name=item.name,model_url=item.model_url,metadata=copy.deepcopy(item.metadata_),owner=str(item.owner_id),public=item.is_public) for item in items}
            public_before=snapshot(public_rows)
            public_ids=list(public_before)
            # Check every DB/storage conflict before the first mutation.
            for row in rows:
                existing=database.get(ModelLibraryEntry,uuid.UUID(row['id']))
                if existing and not existing_row_matches(existing,row,owner_id):
                    raise ValueError('Existing landmark row differs or is public; preserved without overwrite')
                status=object_matches(client,bucket,row)
                if status=='conflict':
                    raise ValueError('Stored landmark object has different bytes; preserved without overwrite')
                report.append(dict(id=row['id'],storeys=row['metadata']['lego']['native_floors'],sha256=row['source_sha256'],
                    binding='verified' if existing else 'missing',object=status))
            if apply:
                for row,status in zip(rows,report,strict=True):
                    if status['object']=='missing':
                        with Path(row['source_path']).open('rb') as body:
                            client.put_object(Bucket=bucket,Key=row['model_url'].removeprefix('/api/v1/files/'),Body=body,
                                ContentType='model/gltf-binary',IfNoneMatch='*')
                        if object_matches(client,bucket,row)!='verified':
                            raise ValueError('Installed landmark failed exact SHA-256 storage readback')
                    if status['binding']=='missing':
                        database.add(ModelLibraryEntry(id=uuid.UUID(row['id']),owner_id=owner_id,name=row['name'],category='building',
                            model_url=row['model_url'],lod_urls={'0':row['model_url']},generation_engine='rlasm',is_public=False,
                            tags=['local-student-review',row['variantId']],metadata_=row['metadata']))
                database.commit()
                database.expire_all()
                public_after=snapshot(database.execute(select(ModelLibraryEntry).where(ModelLibraryEntry.is_public.is_(True))).scalars().all())
                if public_after!=public_before:
                    raise ValueError('Public row readback differs; this installer never updates public entries')
    finally:
        engine.dispose()
    if apply:
        # A separate DB session and fresh object GET verify the committed state.
        verified=synchronize_private(family,artifacts,owner_id=owner_id)
        receipt=dict(family=family,programme=rows[0]['metadata']['rlasm']['storey_program_id'],rows=verified,
            public_rows_unchanged=True,public_row_ids=public_ids,
            source_reviews=[dict(path=s['review_path'],sha256=s['review_sha256']) for s in selected],
            publication=False,private_local_trial_only=True)
        _json(artifacts/f"{family}-private-install-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.json",receipt)
        if any(r['binding']!='verified' or r['object']!='verified' for r in verified):
            raise ValueError('Private landmark installation readback is incomplete')
        return verified
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--family', choices=SOURCES, required=True)
    parser.add_argument('--storeys', type=int)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--resolution', type=int, default=1440)
    parser.add_argument('--version',type=int,default=1)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--worker', action='store_true')
    parser.add_argument('--artifacts',type=Path,default=OUTPUT_ROOT)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--install',action='store_true')
    mode.add_argument('--verify',action='store_true')
    parser.add_argument('--owner-id',type=uuid.UUID)
    parser.add_argument('--env-file',type=Path)
    parser.add_argument('--blender', default='C:/Program Files/Blender Foundation/Blender 5.1/blender.exe')
    args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    a = parser.parse_args(args)
    if a.install or a.verify:
        if a.env_file:
            from dotenv import load_dotenv
            load_dotenv(a.env_file)
        result=synchronize_private(a.family,a.artifacts,apply=a.install,owner_id=a.owner_id)
        print(json.dumps(result,indent=2))
        raise SystemExit(int(any(row['binding']!='verified' or row['object']!='verified' for row in result)))
    if a.storeys is None or a.output is None:
        parser.error('Building requires --storeys and --output')
    programme_for(a.family, a.storeys)
    resolved = a.output.resolve()
    if not resolved.is_relative_to(OUTPUT_ROOT.resolve()) or resolved == OUTPUT_ROOT.resolve():
        raise ValueError('Candidate output must stay in the dedicated external landmark root')
    if a.worker:
        build_worker(a)
    else:
        command=[a.blender,'--background','--python-exit-code','1','--python',str(Path(__file__).resolve()),'--',*args,'--worker']
        raise SystemExit(subprocess.call(command))


if __name__ == '__main__':
    main()
