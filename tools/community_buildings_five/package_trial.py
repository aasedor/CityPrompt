"""Create one immutable local-trial package from reviewed exact candidate bytes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from plan import SPECS

def main():
    p=argparse.ArgumentParser();p.add_argument('kind',choices=SPECS);p.add_argument('candidate',type=Path)
    a=p.parse_args();root=Path(__file__).resolve().parents[2];s=SPECS[a.kind]
    report=json.loads((a.candidate/'build-report.json').read_text(encoding='utf-8'));candidate=report['candidate']
    sources=json.loads((a.candidate/'source-entry.json').read_text(encoding='utf-8'))['sources'];refs=[]
    for source in sources:
        rel=Path('frontend/public/archetypes/buildings')/s['directory']/Path(source['path']).name
        dest=root/rel;raw=dest.read_bytes()
        if raw.startswith(b'version https://git-lfs.github.com/spec/v1'):
            if ('oid sha256:'+source['sha256']) not in raw.decode():raise ValueError('Source differs from committed LFS identity')
            shutil.copyfile(a.candidate/source['path'],dest)
        if hashlib.sha256(dest.read_bytes()).hexdigest()!=source['sha256']:raise ValueError('Changed authoritative source')
        refs.append(dict(role=source['role'],repo_path=rel.as_posix(),bytes=source['bytes'],sha256=source['sha256']))
    model=a.candidate/(candidate+'.glb')
    import trimesh
    dims=trimesh.load(model,force='scene',process=False).extents
    groups=dict(grocer='mixed',hall='civic',cabin='civic',inglewood='shops',shops='shops')
    descriptions=dict(grocer='Corner grocery with one home above and an internal stair.',hall='High clerestory windows, a covered entrance and community activity rooms.',
        cabin='Log recreation shelter with a covered porch and shared activity room.',inglewood='Brick corner shops with upstairs offices and supported balconies.',shops='Four neighbourhood shops, each with its own entrance.')
    entry=dict(candidate=candidate,family='rlasm-clay-'+s['title'],archetype_id=s['parent'],variant_id=s['variant'],archetype_label=s['label'],variant_label=s['label'],
        native_floors=s['floors'],design_dimensions_m=s['dimensions'],references=refs,external_evidence=str(a.candidate.resolve()),
        picker=dict(id='community_'+s['title'].replace('-','_'),description=descriptions[a.kind],group_id=groups[a.kind],reshape_mode='fixed_native',
            reshape_description='One complete building. Enlarge or rotate its plot; the building keeps its authored dimensions.',
            width=round(float(dims[0])+4,1),depth=round(float(dims[2])+4,1),max_size=max(60,round(float(max(dims))+10,1))))
    package=dict(entry=entry,model_file=model.name,review_file='review/independent.json',approval={},trial={})
    with (a.candidate/'trial-package.json').open('x',encoding='utf-8') as f:json.dump(package,f,indent=2);f.write('\n')
    print(a.candidate/'trial-package.json')

if __name__=='__main__':main()
