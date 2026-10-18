"""Write only the finite opt-in local trial identity overlay."""
import json,re
from pathlib import Path
from specs import DESIGNS
ROOT=Path(__file__).resolve().parents[2]


def main():
    path=ROOT/'backend/app/data/parkade_trial_dims.json';new=[]
    for key,b in DESIGNS.items():
        w,d=b['dimensions'];w+=4;d+=4;variant='classic-concrete-v1' if key=='classic' else key+'-v1'
        new.append(dict(id=b['slug'],title=b['label'],development_type='mobility_infrastructure',aesthetic_category='original_parkade',district_kit=None,generation_tags=['parkade','parking garage','structured parking',b['style']],min_floors=b['levels'],max_floors=b['levels'],usable=True,has_variants=True,variant_ids=[variant],default_variant_id=variant,suggested_w_m=w,suggested_d_m=d,min_w_m=w,max_w_m=200,min_d_m=d,max_d_m=200,suggested_area_sqm=w*d))
    content=json.dumps(dict(archetypes=new),indent=2)+'\n'
    if path.exists() and json.loads(path.read_text(encoding='utf-8'))!=json.loads(content):raise ValueError('Refuse conflicting trial dimensions')
    path.write_text(content,encoding='utf-8')
    print('Registered five local-only overlay identities')


if __name__=='__main__':main()
