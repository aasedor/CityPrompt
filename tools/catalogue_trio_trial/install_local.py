"""Install reviewed trio candidates into the existing isolated local studio only.

No production dotenv, seed manifest, public bucket or project is modified.
The caller must supply the already configured isolated runtime bootstrap.
"""
import argparse, hashlib, importlib.util, json, sys, uuid
from pathlib import Path

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def checked_candidate(root):
    read=lambda name:json.loads((root/name).read_text(encoding='utf-8'))
    manifest=read('prework-manifest.json');report=read('build-report.json')
    review=read('evidence/independent-review.json');delivery=read('evidence/delivery-verification.json')
    assert review['architectural_clay_pass'] and review['holistic_review_performed']
    assert review['unresolved_p0']==review['unresolved_p1']==0
    assert delivery['status']=='PASS_DELIVERY_CHECKS'
    assert review['candidate']==manifest['candidate']==report['candidate']
    model=root/report['runtime']['path'];digest=sha(model)
    assert digest==report['runtime']['sha256']==delivery['model_sha256']==review['model_sha256']
    lo,hi=report['delivered_bounds_m'];dims=dict(width=hi[0]-lo[0],depth=hi[1]-lo[1],height=hi[2]-lo[2])
    assert abs(lo[2])<1e-4
    return manifest,report,review,model,digest,dims

def main():
    p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);p.add_argument('--candidate',type=Path,action='append',required=True);p.add_argument('--apply',action='store_true');p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
    candidates=[checked_candidate(root.resolve()) for root in a.candidate]
    if a.receipt.exists():raise FileExistsError('Use a new receipt path for every install checkpoint')
    spec=importlib.util.spec_from_file_location('isolated_studio_runtime',a.runtime.resolve());runtime=importlib.util.module_from_spec(spec);spec.loader.exec_module(runtime)
    s=runtime.settings
    assert s.database_url_sync.endswith('@127.0.0.1:55432/cityprompt_studio')
    assert s.s3_endpoint_url=='http://127.0.0.1:59002' and s.s3_bucket_name=='student-studio-2027'
    assert not s.openai_api_key and not s.gemini_api_key
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    from app.models.models import ModelLibraryEntry, User
    from app.api.v1.model_library import _get_s3_client
    from app.services.lego_assembly import is_runtime_rlasm_architectural_clay_entry
    rows=[]
    with Session(create_engine(s.database_url_sync)) as db:
        owner=db.scalar(select(User).where(User.email=='studio-smoke@example.com'));assert owner
        for m,r,review,model,digest,dims in candidates:
            variant=m['variant_id'];floors=m['measurement_contract']['storeys'];candidate=m['candidate']
            key=f'library/local-trio-2026-09-06/{model.name}';url='/api/v1/files/'+key
            metadata=dict(rlasm=dict(method='RLASM',method_version='6.1',delivery_format='architectural_clay',runtime_enabled=True,source_locked=True,candidate=candidate,archetype_id=m['archetype_id'],variant_id=variant,model_sha256=digest,review_status='independent_architectural_clay_pass',review_sha256=sha(model.parent/'evidence/independent-review.json'),continuous_resize_allowed=False,keeper_approved=False,canonical_promotion_approved=False,local_trial_only=True,native_dimensions_m=dims),
                lego=dict(enabled=True,family='local_trio_'+variant,role='assembled',width_m=dims['width'],depth_m=dims['depth'],height_m=dims['height'],archetype_ids=[m['archetype_id'],variant],reuse_keys=[variant],min_floors=floors,max_floors=floors,repeatable_z=False,variant_key=variant,lod=0,allowed_levels=[floors],native_floors=floors,source_variant_id=variant,generation_archetype_id=variant,footprint_compatibility=dict(placementMode='select_and_place',polygonFit=False,continuous_resize_allowed=False),placement_contract=dict(mode='fixed_landmark',continuous_resize_allowed=False),allow_inset_footprint=True))
            ident=uuid.uuid5(uuid.NAMESPACE_URL,'cityprompt/local-trio/'+candidate)
            for existing in db.scalars(select(ModelLibraryEntry)):
                em=(existing.metadata_ or {}).get('rlasm') or {}
                if existing.id!=ident and em.get('variant_id')==variant and em.get('runtime_enabled'):
                    raise RuntimeError('An active exact-variant model already exists; reconcile explicitly rather than replacing it')
            source=json.loads((model.parent/'source-entry.json').read_text())
            front=next(item for item in source['sources'] if item['role']=='front')
            thumbnail='/archetypes/buildings/'+candidate.split('-clay-')[0]+'/'+Path(front['path']).name
            row=ModelLibraryEntry(id=ident,owner_id=owner.id,name=m['title']+' — local trial',category='building',model_url=url,lod_urls={'0':url},thumbnail_url=thumbnail,is_public=True,generation_engine='rlasm',metadata_=metadata)
            assert is_runtime_rlasm_architectural_clay_entry(row)
            rows.append(dict(id=str(ident),candidate=candidate,sha256=digest,dimensions=dims,model_url=url))
            if a.apply:
                s3=_get_s3_client();s3.put_object(Bucket=s.s3_bucket_name,Key=key,Body=model.read_bytes(),ContentType='model/gltf-binary')
                assert hashlib.sha256(s3.get_object(Bucket=s.s3_bucket_name,Key=key)['Body'].read()).hexdigest()==digest
                db.merge(row)
        if a.apply:db.commit()
    receipt=dict(applied=a.apply,scope='isolated local studio only; user-requested trial',models=rows)
    a.receipt.parent.mkdir(parents=True,exist_ok=True)
    with a.receipt.open('x',encoding='utf-8') as f:json.dump(receipt,f,indent=2)
    print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
