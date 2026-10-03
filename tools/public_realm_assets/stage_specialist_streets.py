"""Hash-verified delivery for the finite canal/bridge runtime candidates."""
import argparse
import hashlib
import json
from pathlib import Path

from stage_brt_runtime import checked
from stage_street_pilots import stage_inspected

LOCKS = {
    'canal-v005': dict(recipe='db99c735b29e2d9c9131d89f787fd137fb1f41523cbae55d8a15322e35535ef9', modules={
        'canal_ground':'08a85bab224aef14f3c720761d315d4ed76304527a065a6f6a3e89bf981d479b',
        'canal_crossing':'098f436d0df567456ec5df3568b8b286a02ec0021cc78f331cf53829c2934839',
        'canal_furnishings':'99142cd4af5257fc2fddb20bbf389df50133fe835160720f7aa0a001c213315f',
        'canal_tree':'0d899baf64da60cdb6e40096a2eefdd15cc69eb5147ffd69f184ca1c99274c95',
        'canal_bench':'a1765bfc10b83423d621479851523389fb06e9023b56cd41929c55be6f583411',
        'canal_lamp':'5316049c31be3a2dd68c641bc272c6c4c11a4fbac3480d9884c0a609bc00a2ca',
        'canal_bollard':'6b5422458e529bed849406937d9b3f847013e8f7a4b132652245f2a57c30385d'}),
    'bridge-v003': dict(recipe='45097473e6d0b948c507466c46862330bdb42fc19edd4575abb08e1d986bd34c',modules={
        'bridge_structure':'164db94c2990d603d03ca7a8fb064deb2110ddb88c452d567c4a8aa5978bef2d'}),
}


def inspect(source, derived, delivery):
    lock=LOCKS[delivery]
    recipe=json.loads(checked(source/'recipe.json',lock['recipe']))
    checked(source/'editable.blend',recipe['authoring_sha256'])
    checked(source/'assembly-preview.glb',recipe['assembly_sha256'])
    for script in recipe['scripts']:
        checked(source/'scripts'/script['path'],script['sha256'])
    extraction=json.loads((derived/'extraction.json').read_text())
    if extraction['sourceRecipeSha256']!=lock['recipe'] or extraction['sourceAuthoringSha256']!=recipe['authoring_sha256']:
        raise ValueError('Specialist modules have a different source')
    files={}
    for kind,sha in lock['modules'].items():
        if extraction['modules'][kind]['sha256']!=sha:
            raise ValueError('Unreviewed specialist module revision')
        files[kind+'.glb']=checked(derived/(kind+'.glb'),sha)
    identity=recipe['source_lock'];variant=identity['variant_id'];reference=identity['sources'][0]
    files['reference.png']=checked(source/'sources'/Path(reference['path']).name,reference['sha256'])
    canal=delivery=='canal-v005'
    sections=[dict(name=name,x=x,width=w,material=m) for name,x,w,m in (
        [('west_quay',-13.5,9,'paving'),('open_water',0,18,'water'),('east_quay',13.5,9,'paving')] if canal else
        [('west_support_reservation',-15,6,'grass'),('west_walk',-10.625,2.75,'paving'),('vehicle_deck',0,18.5,'asphalt'),('east_walk',10.625,2.75,'paving'),('east_support_reservation',15,6,'grass')])]
    program=dict(schemaVersion=1,adapter=delivery+'-v1',surfaceRegions=[],details=[],paving='source-native',
        pavingModuleM=[.30,.15] if canal else [.65,.45],minLengthM=80 if canal else 260,maxLengthM=320 if canal else 480,
        preparedLevelOnly=True,baseLiftM=0,straightOnly=True,
        groundOwnership='entire-canal-corridor-cutout' if canal else 'elevated-span-with-two-grounded-approaches',
        topology='outer-bank-edge-connections-original-arch-only' if canal else 'ground-endpoints-no-at-grade-span-intersections',
        sourceAuthoringSha256=recipe['authoring_sha256'],sourceFiles={s['path']:s['sha256'] for s in recipe['scripts']},
        palette=dict(water=[.055,.13,.12],brick=[.26,.13,.085],paving=[.31,.205,.14] if canal else [.53,.50,.43],
            roadbrick=[.22,.125,.08],coping=[.45,.45,.38],mortar=[.30,.265,.22],soil=[.105,.073,.045],
            concrete=[.49,.47,.42],asphalt=[.10,.115,.11],steel=[.49,.52,.50],paint=[.86,.86,.77]))
    if canal: program.update(nativeLengthM=80,channelWidthM=18,waterHeightM=-2.05,streetHeightM=.12,basinStationM=8,crossingStationM=60)
    else: program.update(structuralSpanM=84,fixedDeckLengthM=100,deckHeightM=4.3,endpointSectionM=24,minimumApproachM=80)
    row=dict(id=variant,sourceArchetypeId=identity['archetype_id'],title=identity['title'],status='candidate',
        sourceRecipeSha256=lock['recipe'],sourceAssemblySha256=recipe['assembly_sha256'],referenceSha256=reference['sha256'],
        widthM=36,fixtureLengthM=80 if canal else 100,routeAxis='local_y',junctionSurface='brick' if canal else 'pavers',
        sections=sections,placements=[],treeWells=[],program=program,
        programSha256=hashlib.sha256(json.dumps(program,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        modules={kind:dict(sha256=sha,bytes=len(files[kind+'.glb']),url=f'/street-kits/pilots/{variant}/{kind}.glb') for kind,sha in lock['modules'].items()},
        thumbnailUrl=f'/street-kits/pilots/{variant}/reference.png')
    return row,files


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('source','derived','public-root','manifest'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--delivery',choices=LOCKS,required=True);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args()
    rows=stage_inspected([inspect(a.source,a.derived,a.delivery)],a.public_root,a.manifest,dry_run=a.dry_run)
    print('DRY_RUN_PASS' if a.dry_run else 'STAGED_CANDIDATE',rows[0]['id'])
