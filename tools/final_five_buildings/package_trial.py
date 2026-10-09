"""Prepare an exact-model local trial; independent pass remains enforced by promotion."""
import argparse
import hashlib
import json
from pathlib import Path
import trimesh
from .specs import SPECS

def main():
    p=argparse.ArgumentParser();p.add_argument('family',choices=SPECS);p.add_argument('candidate',type=Path)
    a=p.parse_args();root=Path(__file__).resolve().parents[2];s=SPECS[a.family]
    report=json.loads((a.candidate/'build-report.json').read_text());refs=[]
    for source in json.loads((a.candidate/'source-entry.json').read_text())['sources']:
        rel=Path('frontend/public/archetypes/buildings')/s['slug']/Path(source['path']).name
        raw=(root/rel).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=source['sha256']:raise ValueError('Authoritative source changed')
        refs.append(dict(role=source['role'],repo_path=rel.as_posix(),bytes=len(raw),sha256=source['sha256']))
    model=a.candidate/report['runtime']['path'];dims=trimesh.load(model,force='scene',process=False).extents
    entry=dict(candidate=report['candidate'],family='rlasm-clay-'+s['slug'],archetype_id=s['slug'],variant_id=s['slug']+'-v1',
        archetype_label=s['label'],variant_label=s['label'],native_floors=s['floors'],
        design_dimensions_m=dict(zip(('width','depth','height'),s['dimensions'])),references=refs,external_evidence=str(a.candidate.resolve()),
        picker=dict(id=s['slug'].replace('-','_'),description=s['description'],group_id=s['group'],reshape_mode='fixed_native',
            reshape_description='Complete authored building. Rotate or enlarge its plot; architecture retains its native dimensions.',
            width=round(float(dims[0])+4,1),depth=round(float(dims[2])+4,1),max_size=max(65,round(float(max(dims))+10,1))))
    package=dict(entry=entry,model_file=model.name,review_file='review/independent.json',approval={},trial={})
    with (a.candidate/'trial-package.json').open('x',encoding='utf-8') as f:json.dump(package,f,indent=2);f.write('\n')

if __name__=='__main__':main()
