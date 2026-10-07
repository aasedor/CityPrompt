"""Finite, additive pathway recipes. Dry run by default; --install --count 1 pilots.

These are surface-only teaching designs, not Calgary standard sections. Old
entries are immutable. Backups and assembly recipes stay in the output folder.
"""
import argparse
import hashlib
import json
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'backend'))
FRONT = ROOT / 'frontend/src/data'
BACK = ROOT / 'backend/app/data'
DESIGNS = [
    ('garden_gravel_path_v1', 'Garden gravel path', 1.5, 'multi_use_trail', 'gravel', [.49, .40, .28]),
    ('concrete_neighbourhood_walk_v1', 'Concrete neighbourhood walk', 1.8, 'campus_pedestrian_spine', 'concrete', [.56, .54, .49]),
    ('brick_courtyard_path_v1', 'Brick courtyard path', 2.0, 'campus_pedestrian_spine', 'brick', [.34, .17, .105]),
    ('timber_garden_walk_v1', 'Timber garden walk', 2.0, 'halifax_waterfront_boardwalk', 'timber', [.32, .23, .15]),
    ('asphalt_shared_path_v1', 'Asphalt shared path', 3.0, 'multi_use_trail', 'asphalt', [.075, .082, .080]),
]

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

def recipe(design):
    key, title, width, parent, finish, color = design
    length = 6
    palette = {'paving': color, 'edge': [v * .57 for v in color]}
    for i, factor in enumerate([.88, .97, 1.04, 1.10]):
        palette[f'paving.tile{i}'] = [round(v * factor, 4) for v in color]
    details = []
    if finish == 'concrete':
        details = [dict(x=0, y=y, width=width, depth=.008, z=.001, height=0, material='edge') for y in [-3, -1.5, 0, 1.5, 3]]
    # A bounded deterministic fine aggregate pattern. No external modules,
    # planting envelopes or objects obstruct the complete clear path width.
    rng = random.Random(key)
    mesh = dict(material='aggregate', positions=[], indices=[])
    if finish in ('gravel', 'asphalt', 'concrete'):
        palette['aggregate'] = [round(v * (1.14 if finish != 'concrete' else .94), 4) for v in color]
        for _ in range(int(width * length * 26)):
            size = rng.uniform(.009, .024) if finish == 'gravel' else rng.uniform(.003, .010)
            x, y = rng.uniform(-width/2 + size, width/2 - size), rng.uniform(-length/2 + size, length/2 - size)
            n = len(mesh['positions']) // 3
            mesh['positions'] += [round(v, 5) for v in [x-size,y,.0015,x+size,y,.0015,x,y+size,.0015]]
            mesh['indices'] += [n,n+1,n+2]
    program = dict(schemaVersion=1, adapter='narrow-pathway-v1',
        surfaceRegions=[dict(x=0,y=0,width=width,depth=length,material='paving')],
        details=details, meshDetails=[mesh] if mesh['positions'] else [],
        paving='brick' if finish in ('brick','timber') else finish,
        pavingModuleM=[.22,.11] if finish=='brick' else [width,.16],
        minLengthM=2, maxLengthM=300, preparedLevelOnly=True,
        baseLiftM=.025, palette=palette)
    assembly = dict(units='metres', axes='X across, Y along, Z up', origin='surface centre',
        widthM=width, lengthM=length, program=program, placements=[], modules={})
    hero = ROOT / f'frontend/public/archetypes/streets/narrow-pathways/{key}.png'
    if not hero.exists():
        raise ValueError(f'Missing reviewed photographic reference: {hero}')
    row = dict(id=key, sourceArchetypeId=parent, title=title, status='candidate',
        sourceRecipeSha256=digest(assembly), sourceAssemblySha256=digest(assembly),
        referenceSha256=hashlib.sha256(hero.read_bytes()).hexdigest(),
        widthM=width, fixtureLengthM=length, routeAxis='local_y', junctionSurface='brick' if finish=='brick' else 'pavers',
        sections=[dict(name='clear_walk',x=0,width=width,material='paving')],
        placements=[], modules={}, treeWells=[], thumbnailUrl=f'/archetypes/streets/narrow-pathways/{key}.png',
        program=program, programSha256=digest(program))
    return row, assembly

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--count',type=int,choices=[1,5],default=1)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--install',action='store_true')
    args=parser.parse_args()
    rows=[]
    for design in DESIGNS[:args.count]:
        row, assembly=recipe(design)
        rows.append(row)
        write(args.output/f"{row['id']}-assembly.json",assembly)
    write(args.output/'manifest.json',rows)
    if not args.install:
        print(f'Dry run: {len(rows)} recipes; zero provider calls; source unchanged')
        return
    from app.services.public_realm_lego import build_public_realm_capability_catalog, public_realm_capability_fingerprint
    catalog=build_public_realm_capability_catalog()
    history=read(BACK/'publicRealmCatalogHistory.json')
    history['catalogs'][catalog.fingerprint]={f'{c.family_id}@{c.family_version}':public_realm_capability_fingerprint(c) for c in catalog.capabilities}
    updates={BACK/'publicRealmCatalogHistory.json':history}
    for root in (FRONT,BACK):
        pilots=read(root/'nativeStreetPilots.json')
        roster=read(root/'classroomStarter.json')
        for row in rows:
            old=next((p for p in pilots if p['id']==row['id']),None)
            if old is not None and old != row:
                raise ValueError('An existing pathway revision cannot be overwritten')
            if old is None:
                pilots.append(row)
                roster['entries'].append(dict(domain='street',representation='native-modules',archetypeId=row['sourceArchetypeId'],variantId=row['id'],revision=row['sourceRecipeSha256'],status='local-pilot-runtime-pending'))
        updates[root/'nativeStreetPilots.json']=pilots
        updates[root/'classroomStarter.json']=roster
    for path,value in updates.items():
        backup=args.output/'backups'/path.relative_to(ROOT)
        backup.parent.mkdir(parents=True,exist_ok=True)
        if not backup.exists(): shutil.copy2(path,backup)
        write(path,value)
    print(f'Installed {len(rows)} local pathway recipes; old entries unchanged; no publication')

if __name__=='__main__': main()
