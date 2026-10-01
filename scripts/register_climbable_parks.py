"""Bounded, repeatable local registration of the three climbable park concepts.

Requires actual model, geometry, walking and author visual-review evidence.
This records a local pilot; it does not imply independent or human approval.
"""
import argparse
import hashlib
import json
from pathlib import Path
from register_classroom_park import register

ROOT=Path(__file__).resolve().parents[1]
SPECS={
 'student_quarry_garden_v1':dict(archetype='student_quarry_garden',thumbnail_slug='quarry-garden',
     description='Descend three stone stair flights into a planted quarry garden. Connected terraces, a reflecting pool and a return-to-entrance control.'),
 'student_spiral_lookout_v1':dict(archetype='student_spiral_lookout',thumbnail_slug='spiral-lookout-park',
     description='Climb a continuous spiral promenade to a landscaped lookout. Follow the same generous path back down or return to the entrance.'),
 'student_cascade_water_garden_v1':dict(archetype='student_cascade_water_garden',thumbnail_slug='cascade-water-garden',
     description='Walk up either side of three cascading pools, cross the upper garden and descend the opposite stairway.'),
}


def main():
    p=argparse.ArgumentParser();p.add_argument('--package',type=Path,required=True);p.add_argument('--dry-run',action='store_true')
    args=p.parse_args();package=args.package
    recipe=json.loads((package/'recipe.json').read_text(encoding='utf-8'));spec=dict(SPECS[recipe['id']])
    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    model_hash=digest(package/'assembly-preview.glb')
    assert model_hash==recipe['assembly']['sha256']
    review=json.loads((package/'visual-review.json').read_text(encoding='utf-8'))
    assert review['status']=='PASS_AUTHOR_VISUAL_REVIEW' and review['model_sha256']==model_hash
    for item in review['inspected_files']:
        assert digest(package/item['path'])==item['sha256']
    walk=json.loads((package/'walking-verification.json').read_text(encoding='utf-8'))
    assert walk['status']=='PASS' and walk['model_sha256']==model_hash
    assert walk.get('body_clearance_width_m',0)>=.44
    assert len(recipe['walking']['triangles'])>0 and recipe['walking']['routes']
    spec.update(key='climbable-'+package.name,sha256=model_hash,
                entrance=dict(x=0,y=-recipe['dimensions_m'][1]/2,widthM=3.5,arrivalY=-recipe['dimensions_m'][1]/2+1))
    if args.dry_run:
        print('PASS_REGISTRATION_PREFLIGHT',recipe['id']);return
    backup=package/'before-registration';backup.mkdir(exist_ok=True)
    for relative in ['frontend/src/data/nativeParks.json','backend/app/data/nativeParks.json','frontend/src/data/classroomExpansion.json']:
        target=backup/relative.replace('/','__')
        if not target.exists():target.write_bytes((ROOT/relative).read_bytes())
    register(package,specs={recipe['id']:spec})
    seed=ROOT/'seed/classroom-parks'/spec['key']
    for name in ['walking-verification.json','visual-review.json']:(seed/name).write_bytes((package/name).read_bytes())
    for item in review['inspected_files']:
        target=seed/item['path'];target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((package/item['path']).read_bytes())
    layouts=json.loads((ROOT/'frontend/src/data/nativeParks.json').read_text(encoding='utf-8'))['layouts']
    layout=next(l for l in layouts if l['variantId']==recipe['id'])
    for asset in [*layout['assets'].values(),layout['thumbnail']]:
        data=(ROOT/asset['archivePath']).read_bytes()
        assert hashlib.sha256(data).hexdigest()==asset['sha256']
        target=ROOT/'frontend/public'/asset['url'].lstrip('/')
        if target.exists() and target.read_bytes()!=data:raise ValueError(f'Preserved existing public file: {target}')
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    print('STAGED_EXACT_MODEL_AND_THUMBNAIL',recipe['id'])

if __name__=='__main__':main()
