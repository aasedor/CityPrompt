"""Stage the finite brt-v004 candidate through the shared street delivery path.

Original source and derived bytes are locked independently. This does not add a
catalogue entry, change an existing saved fixture, or grant runtime acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path

from stage_street_pilots import stage_inspected

RECIPE_SHA = 'c18cdf29bc7474a90b1bbbc5531650faefb388e0366f6ce2d1ba98c75bbecb1c'
DERIVED = {
    'station_program': '22722b1515ca5cc0c34fabc7f32deb07733ba571c97a2a996fad7e347cbe65d3',
    'bus_symbol': 'ca2492e046c1102d61c59702315ae08c1609ca3f3106f304f208137c4e5a3347',
}


def checked(path, sha):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != sha:
        raise ValueError(f'BRT source or derived bytes changed: {path.name}')
    return data


def inspect(source: Path, derived: Path):
    recipe = json.loads(checked(source/'recipe.json', RECIPE_SHA))
    checked(source/'editable.blend', recipe['authoring_sha256'])
    checked(source/'assembly-preview.glb', recipe['assembly_sha256'])
    for script in recipe['scripts']:
        checked(source/'scripts'/script['path'], script['sha256'])
    extraction = json.loads((derived/'extraction.json').read_text())
    if extraction['sourceRecipeSha256'] != RECIPE_SHA or extraction['sourceAuthoringSha256'] != recipe['authoring_sha256']:
        raise ValueError('BRT extraction came from a different original')
    identity = recipe['source_lock']; variant = identity['variant_id']
    files = {f'{kind}.glb': checked(source/'modules'/module['path'], module['sha256'])
             for kind, module in recipe['modules'].items()}
    for kind, sha in DERIVED.items():
        if extraction['modules'][kind]['sha256'] != sha:
            raise ValueError('Unreviewed derived BRT module revision')
        files[f'{kind}.glb'] = checked(derived/f'{kind}.glb', sha)
    reference = identity['sources'][0]
    files['reference.png'] = checked(source/'sources/variant_0.png', reference['sha256'])
    sections = [dict(name=name, x=x, width=width, material=material) for name,x,width,material in [
        ('west_walk',-18.55,2.9,'paving'),('west_furniture',-16,2.2,'paving'),
        ('west_general_traffic',-9.5,10.8,'asphalt'),('west_bus_lane',-2.4,3.4,'asphalt'),
        ('refuge_median',0,1.4,'paving'),('east_bus_lane',2.4,3.4,'asphalt'),
        ('east_general_traffic',9.5,10.8,'asphalt'),('east_furniture',16,2.2,'paving'),('east_walk',18.55,2.9,'paving')]]
    program = dict(schemaVersion=1,adapter='brt-v004-v1',surfaceRegions=[],details=[],paving='source-stone',
                   pavingModuleM=[.65,.45],minLengthM=100,maxLengthM=480,preparedLevelOnly=True,
                   baseLiftM=.025,straightOnly=True,manualStops=True,
                   stopEnvelopeM=[21,33.5],minimumStopSpacingM=56.5,
                   sourceFiles={item['path']:item['sha256'] for item in recipe['scripts']},
                   sourceAuthoringSha256=recipe['authoring_sha256'],
                   palette=dict(paving=[.53,.50,.43],edge=[.35,.34,.29],soil=[.105,.073,.045],
                                asphalt=[.10,.115,.11],bus_red=[.36,.095,.065],paint=[.86,.86,.77],curb=[.48,.48,.42]))
    row = dict(id=variant,sourceArchetypeId=identity['archetype_id'],title=identity['title'],status='candidate',
               sourceRecipeSha256=RECIPE_SHA,sourceAssemblySha256=recipe['assembly_sha256'],referenceSha256=reference['sha256'],
               widthM=40,fixtureLengthM=100,routeAxis='local_y',junctionSurface='pavers',sections=sections,
               placements=[],treeWells=[],program=program,
               programSha256=hashlib.sha256(json.dumps(program,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
               modules={name[:-4]:dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),
                                      url=f'/street-kits/pilots/{variant}/{name}') for name,data in files.items() if name.endswith('.glb')},
               thumbnailUrl=f'/street-kits/pilots/{variant}/reference.png')
    return row, files


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('source','derived','public-root','manifest'):
        parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args()
    rows=stage_inspected([inspect(args.source,args.derived)],args.public_root,args.manifest,dry_run=args.dry_run)
    print('DRY_RUN_PASS' if args.dry_run else 'STAGED_CANDIDATE', rows[0]['id'])
