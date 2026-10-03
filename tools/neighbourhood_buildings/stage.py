"""Prepare an exact independently reviewed local building trial; never publish."""
import argparse,json,math,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from tools.catalogue_promotion import prepare,picker_assets

def main():
    p=argparse.ArgumentParser();p.add_argument('package',type=Path);p.add_argument('--apply',action='store_true');a=p.parse_args();root=a.package
    m=json.loads((root/'prework-manifest.json').read_text(encoding='utf-8'));r=json.loads((root/'build-report.json').read_text(encoding='utf-8'))
    expected={'university_library':'mass_timber_biophilic_barn','parisian_boulevard_corner':'parisian_corner_cafe_culture'}
    if expected.get(m['archetype_id'])!=m['variant_id']:raise ValueError('Outside the finite neighbourhood building batch')
    library=m['archetype_id']=='university_library';title='Mass-timber Library' if library else 'Corner Café & Apartments'
    candidate=m['candidate'];refs=[]
    for s in m['source_contract']['sources']:
        source=Path(s['original_path']);relative=source.as_posix().split('frontend/public/',1)[1]
        refs.append(dict(role=s['role'],repo_path='frontend/public/'+relative,bytes=s['bytes'],sha256=s['sha256']))
    # GLB dimensions are measured again by the promotion validator.
    import trimesh
    model=root/(candidate+'.glb');extents=trimesh.load(model,force='scene',process=False).extents
    width=math.ceil(float(extents[0])+4);depth=math.ceil(float(extents[2])+4)
    entry=dict(candidate=candidate,family='rlasm-clay-'+m['variant_id'].replace('_','-'),archetype_id=m['archetype_id'],variant_id=m['variant_id'],archetype_label='University Library' if library else 'Parisian Boulevard Corner',variant_label=title,native_floors=m['measurement_contract']['floors'],design_dimensions_m=m['measurement_contract']['dimensions_m'],references=refs,external_evidence=str(root),picker=dict(id='clay_'+m['variant_id'],description='Planted roof terraces, branching timber supports and a glazed reading hall.' if library else 'Ochre brick and cream stone apartments over a green-awning corner café.',group_id='civic' if library else 'mixed',reshape_mode='fixed_native',reshape_description='The complete building keeps its authored proportions within the plot.',width=width,depth=depth,max_size=140))
    spec=dict(entry=entry,model_file=model.name,review_file='independent-review.json',approval={},trial={})
    path=root/'local-trial-package.json'
    if path.exists() and json.loads(path.read_text(encoding='utf-8'))!=spec:raise ValueError('Do not replace a changed package')
    if not path.exists():path.write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
    if a.apply:
        backup=root/'before-registration';backup.mkdir(exist_ok=True)
        for relative in ('seed/model-library/rlasm-architectural-clay/library.json','frontend/src/features/pickPlace/publishedBuildingAssets.ts','frontend/src/data/classroomExpansion.json'):
            target=backup/relative.replace('/','__')
            if not target.exists():target.write_bytes((ROOT/relative).read_bytes())
    for f in prepare(ROOT,path,apply=a.apply,trial_only=True):print(f)
    if a.apply:
        path=ROOT/'frontend/src/data/classroomExpansion.json';data=json.loads(path.read_text(encoding='utf-8'))
        e=dict(domain='building',title=title,archetype_id=m['archetype_id'],variant_id=m['variant_id'],version=candidate,placement_id=entry['picker']['id'],sha256=r['runtime']['sha256'],asset_review='PASS_INDEPENDENT_ARCHITECTURAL_CLAY',runtime_status='NOT TESTED',completed=False)
        if any(v['variant_id']==e['variant_id'] for v in data['entries']):raise ValueError('Existing catalogue identity')
        data['entries'].append(e)
        library_payload=json.loads((ROOT/'seed/model-library/rlasm-architectural-clay/library.json').read_text(encoding='utf-8'))
        data['assets'].append(next(v for v in picker_assets(library_payload) if v['id']==e['placement_id']))
        path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
if __name__=='__main__':main()
