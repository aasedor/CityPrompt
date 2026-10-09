"""Append only this finite batch to the backend's trusted design inventory."""
import json
import re
from pathlib import Path


def main():
    root=Path(__file__).resolve().parents[2]
    roster=json.loads((root/'frontend/src/data/finalFiveBuildingBatch.json').read_text(encoding='utf-8'))['entries']
    parents=json.loads((root/'frontend/src/data/buildingArchetypes.json').read_text(encoding='utf-8'))['archetypes']
    path=root/'backend/app/data/archetype_plan_dims.json'
    text=path.read_text(encoding='utf-8');data=json.loads(text);existing={row['id'] for row in data['archetypes']}
    additions=[]
    for row in roster:
        if row['archetype_id'] in existing:continue
        p=next(p for p in parents if p['id']==row['archetype_id'])
        w,d=p['suggestedWidth_m'],p['suggestedDepth_m']
        additions.append(dict(id=p['id'],title=p['title'],development_type=p['developmentType'],
            aesthetic_category=p['aestheticCategory'],district_kit=None,generation_tags=p['generationTags'],
            min_floors=p['minFloors'],max_floors=p['maxFloors'],usable=True,has_variants=True,
            variant_ids=[row['variant_id']],default_variant_id=row['variant_id'],suggested_w_m=w,suggested_d_m=d,
            min_w_m=w,max_w_m=w,min_d_m=d,max_d_m=d,suggested_area_sqm=w*d))
    if not additions:return
    index=text.rfind('\n ]')
    if index<0:raise ValueError('Unexpected dimensions inventory ending')
    insertion=''.join(',\n'+'\n'.join('  '+line for line in json.dumps(row,indent=1,ensure_ascii=False).splitlines()) for row in additions)
    changed=text[:index]+insertion+text[index:]
    changed=re.sub(r'("count"\s*:\s*)\d+',lambda m:m[1]+str(len(data['archetypes'])+len(additions)),changed,count=1)
    assert json.loads(changed)['archetypes']==data['archetypes']+additions
    path.write_text(changed,encoding='utf-8',newline='\n')
    print('Added trusted design identities: '+', '.join(row['id'] for row in additions))


if __name__=='__main__':main()
