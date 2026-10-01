"""Register only the two reviewed local park pilots; preserve existing bindings."""
import argparse, hashlib, json, shutil
from pathlib import Path
from register_classroom_park import register
ROOT=Path(__file__).resolve().parents[1]
SPECS={
 'student_treetop_walk_v1':dict(archetype='student_treetop_walk',thumbnail_slug='treetop-walk-park',description='Climb two broad stair flights to a woodland promenade and shaded lookout. A separate ground path leads to a quiet resting glade.'),
 'student_terraced_rose_v1':dict(archetype='student_terraced_rose',thumbnail_slug='terraced-rose-garden',description='Explore three richly planted rose terraces, paired stairways, a fountain and flowering pergolas.'),
}
def main():
    p=argparse.ArgumentParser();p.add_argument('--package',required=True,type=Path);p.add_argument('--dry-run',action='store_true');a=p.parse_args();folder=a.package
    read=lambda f:json.loads((folder/f).read_text(encoding='utf-8'));digest=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
    r=read('recipe.json');spec=dict(SPECS[r['id']]);model=digest(folder/'assembly-preview.glb')
    assert r['assembly']['sha256']==model
    deliverables={f'modules/{m["path"]}':m['sha256'] for m in r['modules'].values()}
    deliverables.update(r['source_build_files'])
    for relative,sha in deliverables.items():assert digest(folder/relative)==sha
    visual=read('visual-review.json');assert visual['status']=='PASS_AUTHOR_VISUAL_REVIEW' and visual['model_sha256']==model
    assert len(visual['inspected_files'])>=7
    for evidence in visual['inspected_files']:assert digest(folder/evidence['path'])==evidence['sha256']
    walking=read('walking-verification.json');assert walking['status']=='PASS' and walking['model_sha256']==model and walking['body_clearance_width_m']>=.44
    spec.update(key='garden-'+folder.name,sha256=model,entrance=dict(x=0,y=-32,widthM=4,arrivalY=-31))
    if a.dry_run:print('PASS_REGISTRATION_PREFLIGHT',r['id']);return
    backup=folder/'before-registration';backup.mkdir(exist_ok=True)
    for relative in ['frontend/src/data/nativeParks.json','backend/app/data/nativeParks.json','frontend/src/data/classroomExpansion.json']:
        target=backup/relative.replace('/','__')
        if not target.exists():target.write_bytes((ROOT/relative).read_bytes())
    register(folder,specs={r['id']:spec})
    seed=ROOT/'seed/classroom-parks'/spec['key']
    for name in ['walking-verification.json','visual-review.json']:(seed/name).write_bytes((folder/name).read_bytes())
    for relative in deliverables:
        target=seed/relative;target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and target.read_bytes()!=(folder/relative).read_bytes():raise ValueError('Preserved seed deliverable: '+str(target))
        shutil.copyfile(folder/relative,target)
    for evidence in visual['inspected_files']:
        dest=seed/evidence['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(folder/evidence['path'],dest)
    layouts=json.loads((ROOT/'frontend/src/data/nativeParks.json').read_text(encoding='utf-8'))['layouts']
    layout=next(l for l in layouts if l['variantId']==r['id'])
    for asset in [*layout['assets'].values(),layout['thumbnail']]:
        data=(ROOT/asset['archivePath']).read_bytes();assert hashlib.sha256(data).hexdigest()==asset['sha256']
        target=ROOT/'frontend/public'/asset['url'].lstrip('/')
        if target.exists() and target.read_bytes()!=data:raise ValueError('Preserved existing public asset: '+str(target))
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    print('STAGED_EXACT_MODEL_AND_THUMBNAIL',r['id'])
if __name__=='__main__':main()
