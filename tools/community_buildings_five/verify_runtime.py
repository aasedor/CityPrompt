"""Read-only local API/model delivery check for the exact installed batch."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import httpx


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--user-id',required=True)
    p.add_argument('--project-id',required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    root=Path(__file__).resolve().parents[2]
    sys.path.insert(0,str(root/'backend'))
    from app.core.security import create_access_token
    headers={'Authorization':'Bearer '+create_access_token(a.user_id,role='editor')}
    roster=json.loads((root/'frontend/src/data/communityBuildingBatch.json').read_text(encoding='utf-8'))['entries']
    library=json.loads((root/'seed/model-library/rlasm-architectural-clay/library.json').read_text(encoding='utf-8'))['entries']
    results=[]
    with httpx.Client(base_url='http://127.0.0.1:8011',headers=headers,timeout=60) as client:
        for row in roster:
            entry=next(e for e in library if e['candidate']==row['candidate'])
            payload=dict(target_width_m=entry['picker']['width'],target_depth_m=entry['picker']['depth'],
                target_floors=entry['native_floors'],archetype_id=row['variant_id'],model_revision=row['candidate'],
                allow_forced_fit=False,project_id=a.project_id)
            response=client.post('/api/v1/lego-assembly/plan',json=payload)
            response.raise_for_status();plan=response.json()
            assert plan['archetype_id']==row['variant_id']
            assert plan['fit']['native_scale_locked'] is True
            assert len(plan['instances'])==1
            instance=plan['instances'][0]
            assert instance['scale']==[1,1,1]
            assert instance['variant_key']==row['variant_id']
            assert instance['model_url'].endswith('/'+row['candidate']+'.glb')
            model=client.get(instance['model_url']);model.raise_for_status()
            digest=hashlib.sha256(model.content).hexdigest()
            assert digest==entry['model']['sha256']
            assert model.content[:4]==b'glTF'
            references=[]
            for ref in entry['references']:
                image=httpx.get('http://127.0.0.1:5181/'+ref['repo_path'].removeprefix('frontend/public/'),timeout=30)
                image.raise_for_status()
                assert hashlib.sha256(image.content).hexdigest()==ref['sha256']
                references.append(dict(role=ref['role'],status=image.status_code,sha256=ref['sha256']))
            results.append(dict(candidate=row['candidate'],plan_status=response.status_code,
                model_status=model.status_code,bytes=len(model.content),sha256=digest,
                scale=instance['scale'],height_m=plan['assembled_height_m'],references=references))
    a.output.write_text(json.dumps(dict(status='PASS',scope='Authenticated native plan and exact model delivery; not walking or terrain QA',results=results),indent=2)+'\n')
    print(f'PASS: {len(results)} exact native plans, model hashes and reference sets; report {a.output}')


if __name__=='__main__':main()
