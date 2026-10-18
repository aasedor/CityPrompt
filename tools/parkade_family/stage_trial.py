"""Stage exact independently passed parkade assets into a separate local trial."""
import argparse,hashlib,importlib,json,math,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from tools.catalogue_promotion import picker_assets,validate_review
from tools.seed_model_library import load_seed_library
from tools.parkade_family import specs as S

CANDIDATES={'classic':'classic-clay-v005','brick':'brick-clay-v001','green':'green-clay-v003','solar':'solar-clay-v001','courtyard':'courtyard-clay-v002'}


def copy_verified(src,dst):
    raw=src.read_bytes();dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():
        if dst.read_bytes()!=raw:raise ValueError('Refuse conflicting destination '+str(dst))
    else:
        with dst.open('xb') as output:output.write(raw)
    return dict(sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))


def preflight(candidate, expected_key):
    report=json.loads((candidate/'build-report.json').read_text(encoding='utf-8'))
    manifest=json.loads((candidate/'prework-manifest.json').read_text(encoding='utf-8'))
    review=json.loads((candidate/'review/independent.json').read_text(encoding='utf-8'))
    source=json.loads((candidate/'source-entry.json').read_text(encoding='utf-8'))
    slug=S.DESIGNS[expected_key]['slug']
    variant='classic-concrete-v1' if expected_key=='classic' else expected_key+'-v1'
    identity=(manifest['candidate'],slug,variant)
    if ((report['candidate'],manifest['archetype_id'],manifest['variant_id'])!=identity
        or source['archetype_id']!=slug or source['variant_id']!=variant
        or review.get('candidate')!=manifest['candidate']):raise ValueError('Candidate identity conflict')
    sha=report['runtime']['sha256']
    if (review.get('architectural_clay_pass') is not True or review.get('holistic_review_performed') is not True
        or review.get('unresolved_p0')!=0 or review.get('unresolved_p1')!=0 or not review.get('reviewer')
        or review.get('model_sha256')!=sha):raise ValueError('Independent model review missing')
    if hashlib.sha256((candidate/report['runtime']['path']).read_bytes()).hexdigest()!=sha:raise ValueError('Model changed')
    reviewed={record['sha256'] for record in review.get('inspected_files',[])}
    records=source['sources']
    if len(records)!=4 or {r['role'] for r in records}!={'front','top','oblique','ramp_section'}:raise ValueError('Four locked source roles required')
    locked={r['role']:(r['sha256'],r['bytes']) for r in manifest['source_contract']['sources']}
    for record in records:
        relative=Path(record['path'])
        if relative.as_posix()!='sources/'+record['role']+'.png':raise ValueError('Source role must use its exact copied path')
        raw=(candidate/relative).read_bytes();actual=(hashlib.sha256(raw).hexdigest(),len(raw))
        if actual!=(record['sha256'],record['bytes']) or actual!=locked.get(record['role']) or actual[0] not in reviewed:raise ValueError('Unreviewed or modified source: '+record['role'])
    return report,manifest


def stage(evidence, public, keys=None):
    selected={key:value for key,value in CANDIDATES.items() if keys is None or key in keys}
    old=json.loads((ROOT/'seed/claude-five-trial/library.json').read_text(encoding='utf-8'))
    payload={key:old[key] for key in ('schema','method','method_version','delivery_format','runtime_policy')}
    payload.update(created_at='2026-10-17T00:00:00Z',updated_at='2026-10-17',reference_authority='frontend/public/archetypes/buildings',
        activation=dict(authorized_by='human_user',keeper_approval_implied=False,quote='Can you design 5 parkades? 2 normal and 3 innovative ones. Sounds wonderful. Please proceed.',scope='Local trial only; no publication, push or deployment.'),entries=[])
    # Inspect every candidate before copying anything into runtime locations.
    for key,directory in selected.items():
        preflight(evidence/directory,key)
    for key,directory in selected.items():
        candidate=evidence/directory;r,m=preflight(candidate,key);slug=S.DESIGNS[key]['slug']
        targets=[(candidate/r['runtime']['path'],ROOT/'seed/model-library/rlasm-architectural-clay/models'/r['runtime']['path']),
                 (candidate/r['runtime']['path'],public/'models/parkade-pilot'/r['runtime']['path']),
                 (candidate/'review/independent.json',ROOT/'seed/model-library/rlasm-architectural-clay/evidence'/(m['candidate']+'.json'))]
        for role in ('front','oblique','top','ramp_section'):
            for base in (ROOT/'frontend/public',public):targets.append((candidate/'sources'/(role+'.png'),base/'archetypes/buildings'/slug/(role+'.png')))
        for base in (ROOT/'frontend/public',public):targets.append((candidate/'renders/front_corner.png',base/'archetypes/buildings'/slug/'model-preview.png'))
        for src,dst in targets:
            if dst.exists() and dst.read_bytes()!=src.read_bytes():raise ValueError('Refuse conflicting destination '+str(dst))
    for key,directory in selected.items():
        candidate=evidence/directory;r=json.loads((candidate/'build-report.json').read_text());m=json.loads((candidate/'prework-manifest.json').read_text());slug=S.DESIGNS[key]['slug'];dimensions=r['native_dimensions_m'];refs=[]
        modelDst=ROOT/'seed/model-library/rlasm-architectural-clay/models'/r['runtime']['path'];copy_verified(candidate/r['runtime']['path'],modelDst)
        copy_verified(modelDst,public/'models/parkade-pilot'/modelDst.name)
        for role in ('front','oblique','top','ramp_section'):
            rel=Path('frontend/public/archetypes/buildings')/slug/(role+'.png');meta=copy_verified(candidate/'sources'/(role+'.png'),ROOT/rel)
            copy_verified(ROOT/rel,public/'archetypes/buildings'/slug/(role+'.png'))
            if role!='ramp_section':refs.append(dict(role=role,repo_path=rel.as_posix(),**meta))
        # Catalogue thumbnail derives from the exact reviewed GLB, separately from source references.
        copy_verified(candidate/'renders/front_corner.png',public/'archetypes/buildings'/slug/'model-preview.png')
        copy_verified(candidate/'renders/front_corner.png',ROOT/'frontend/public/archetypes/buildings'/slug/'model-preview.png')
        reviewRel=Path('seed/model-library/rlasm-architectural-clay/evidence')/(m['candidate']+'.json');reviewMeta=copy_verified(candidate/'review/independent.json',ROOT/reviewRel)
        e=dict(candidate=m['candidate'],family=slug,archetype_id=slug,archetype_label=S.DESIGNS[key]['label'],variant_id=m['variant_id'],variant_label=S.DESIGNS[key]['label'],runtime_enabled=True,local_trial_only=True,native_floors=S.DESIGNS[key]['levels'],design_dimensions_m=m['measurement_contract']['dimensions_m'],
            source=dict(commit='original-local-authored-design',path=str(candidate/r['runtime']['path']),original_bytes_unchanged=True,units='metres',up_axis='+Y',limitations='Fixed native architectural clay; no engineering, accessibility, capacity or terrain certification. No working doors or editable floor count.'),
            model=dict(path='../model-library/rlasm-architectural-clay/models/'+modelDst.name,**{k:r['runtime'][k] for k in ('sha256','bytes')},native_dimensions_m=dimensions,mesh_count=r['runtime']['meshes'],material_count=r['runtime']['materials'],texture_count=0,image_count=0),references=refs,
            review=dict(repo_path=reviewRel.as_posix(),sha256=reviewMeta['sha256'],status='PASS_INDEPENDENT_ARCHITECTURAL_CLAY',unresolved_p0=0,unresolved_p1=0),
            picker=dict(id=slug.replace('-','_'),description=S.DESIGNS[key]['identity']+' Fixed-size architectural clay local trial.',group_id='parkades',reshape_mode='fixed_native',reshape_description='Move and rotate the complete parkade; resizing the surrounding plot preserves its native geometry and fixed levels.',width=math.ceil((dimensions['width']+4)*10-1e-7)/10,depth=math.ceil((dimensions['depth']+4)*10-1e-7)/10,max_size=200))
        validate_review(e,ROOT);payload['entries'].append(e)
    dest=ROOT/'seed/parkade-family-trial/library.json';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(json.dumps(payload,indent=2)+'\n')
    load_seed_library(dest)
    assets=picker_assets(payload)
    for asset,e in zip(assets,payload['entries']):
        asset['properties'].update(height=e['model']['native_dimensions_m']['height'],height_m=e['model']['native_dimensions_m']['height'])
    (ROOT/'frontend/src/data/parkadeFamilyTrial.json').write_text(json.dumps(dict(assets=assets),indent=2)+'\n')
    print(json.dumps(dict(candidates=len(assets),bytes=sum(e['model']['bytes'] for e in payload['entries']),local_only=True)))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('evidence',type=Path);p.add_argument('public',type=Path);p.add_argument('--key',action='append',choices=list(CANDIDATES));a=p.parse_args();stage(a.evidence,a.public,a.key)
