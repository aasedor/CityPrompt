"""Explicit adapter for two immutable 2026-09-24 deliveries; originals stay intact.

Recover ground ownership and non-placement details from the locked authoring
sources. This is executable program metadata, not visual/runtime acceptance.
"""
import hashlib
import json
from copy import deepcopy
from pathlib import Path

LOCKS = Path(__file__).with_name('original_street_delivery_locks.json')


def adapt_original(package: Path, source: dict, source_bytes: bytes) -> tuple[dict, dict | None]:
    lock = json.loads(LOCKS.read_text()).get(source['id'])
    if lock is None:
        return source, None
    if hashlib.sha256(source_bytes).hexdigest() != lock['recipeSha256']:
        raise ValueError('Original street recipe differs from its locked delivery')
    for name, digest in lock['files'].items():
        if hashlib.sha256((package/name).read_bytes()).hexdigest() != digest:
            raise ValueError(f'Original street source changed: {name}')
    recipe = deepcopy(source)
    width, length = recipe['dimensions_m']
    shared = recipe['kind'] == 'shared'
    recipe.update(fixed_width_m=width, fixture_length_m=length, pattern='brick' if shared else 'stone',
                  tree_wells=[], reference=f"{lock['sourceArchetypeId']}/reference.png",
                  image_references=[dict(path='renders/aerial.png', sha256=lock['files']['renders/aerial.png'],
                                         bytes=(package/'renders/aerial.png').stat().st_size)])
    details = []
    for region in recipe['surface_regions']:
        if region['material'] != 'soil':
            continue
        x,y,w,d = (region[k] for k in ('x','y','width','depth'))
        for xx in (x-w/2,x+w/2):
            details.append(dict(x=xx,y=y,width=.035,depth=d,z=.025,height=.05,material='metal'))
        for yy in (y-d/2,y+d/2):
            details.append(dict(x=x,y=yy,width=w,depth=.035,z=.025,height=.05,material='metal'))
    for section in recipe['sections']:
        if not section['name'].endswith('_garden'):
            continue
        sign=-1 if section['name'].startswith('west') else 1
        x=section['x']-sign*section['width']/2
        for a,b in ((-length/2,-1.65),(1.65,length/2)):
            details.append(dict(x=x,y=(a+b)/2,width=.05,depth=b-a,z=.006,height=0,material='edge'))
    if not shared:
        for x in (-2.85,2.85):
            for y in range(-22,23,2):
                if abs(y)>2:
                    details.append(dict(x=x,y=y+.225,width=.035,depth=.45,z=.008,height=0,material='metal'))
    program = dict(schemaVersion=1, adapter='original-community-street-v1',
                   sourceFiles=lock['files'], surfaceRegions=recipe['surface_regions'], details=details,
                   paving='brick' if shared else 'stone', pavingModuleM=recipe['metric_paving_module_m'],
                   minLengthM=length, maxLengthM=480, preparedLevelOnly=True,
                   baseLiftM=.025, sourceGroundTopM=0,
                   palette=dict(paving=[.53,.50,.43],edge=[.35,.34,.29],grass=[.21,.28,.105],
                                soil=[.105,.073,.045],metal=[.035,.049,.045],asphalt=[.10,.115,.11]))
    if shared:
        program['palette'].update({f'paving.tile{i}':[c*f for c in [.43,.34,.24]] for i,f in enumerate([.84,.96,1.06,1.12])})
    return recipe, program
