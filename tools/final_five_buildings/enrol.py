"""Enrol only exact independently staged candidates; preserve existing catalogue text."""
import argparse
import hashlib
import json
from pathlib import Path
from .specs import SPECS

def main():
    p=argparse.ArgumentParser();p.add_argument('family',choices=SPECS);p.add_argument('candidate');p.add_argument('--backup-dir',type=Path,required=True)
    a=p.parse_args();s=SPECS[a.family];root=Path(__file__).resolve().parents[2]
    library=json.loads((root/'seed/model-library/rlasm-architectural-clay/library.json').read_text())
    entry=next(e for e in library['entries'] if e['candidate']==a.candidate)
    if entry['archetype_id']!=s['slug'] or entry['variant_id']!=s['slug']+'-v1':raise ValueError('Identity mismatch')
    report=json.loads((Path(entry['external_evidence'])/'build-report.json').read_text())
    if report['runtime']['sha256']!=entry['model']['sha256']:raise ValueError('Entrance measurement model mismatch')
    cx,cy,_=report['native_bottom_center_m'];ex,ey,ew=s['entrance']
    entrance=dict(xM=round(ex-cx,9),yM=round(ey-cy,9),widthM=ew,
                  plotWidthM=entry['picker']['width'],plotDepthM=entry['picker']['depth'])
    parents=root/'frontend/src/data/buildingArchetypes.json';raw=parents.read_bytes();text=raw.decode('utf-8');data=json.loads(text)
    if any(v['id']==s['slug'] for v in data['archetypes']):raise ValueError('Already enrolled parent')
    a.backup_dir.mkdir(parents=True,exist_ok=True)
    backup=a.backup_dir/(parents.name+'.'+hashlib.sha256(raw).hexdigest()[:12]+'.bak')
    if not backup.exists():backup.write_bytes(raw)
    width,depth,height=s['dimensions'];photo='/archetypes/buildings/'+s['slug']+'/front.png'
    parent=dict(id=s['slug'],title=s['label'],aestheticCategory='contemporary_urban',description=s['description'],developmentType=s['type'],
        generationTags=[s['label'],'original design','RLASM 6.1','neighbourhood essentials'],thumbnailUrl=photo,
        minFloors=s['floors'],maxFloors=s['floors'],suggestedFloorHeight=height/s['floors'],
        suggestedWidth_m=width,suggestedDepth_m=depth,minWidth_m=width,maxWidth_m=width,minDepth_m=depth,maxDepth_m=depth,
        variants=[dict(id=s['slug']+'-v1',label=s['label'],description=s['description'],thumbnailUrl=photo,minFloors=s['floors'],maxFloors=s['floors'])])
    # Insert before final archetypes-array terminator without normalising other bytes.
    newline='\r\n' if b'\r\n' in raw else '\n'
    index=text.rfind(newline+'  ]')
    if index<0:raise ValueError('Unexpected catalogue ending')
    insert=','+newline+newline.join('    '+line for line in json.dumps(parent,indent=2,ensure_ascii=False).splitlines())
    changed=text[:index]+insert+text[index:]
    assert json.loads(changed)['archetypes']==data['archetypes']+[parent]
    parents.write_bytes(changed.encode('utf-8'))
    program_path=root/'frontend/src/features/zoningCatalogue/buildingPrograms.json'
    old=program_path.read_text(encoding='utf-8');program=dict(components=s['uses'],assumption=s['description']+' Teaching programme; not a surveyed or approved building.',revision=a.candidate,
        classification=dict(basis='teaching',evidence='Original source-locked building with explicit educational occupancy.'))
    if a.family=='seniors':program['assumption']+=' Independent dwellings; no medical care or assisted-living service assumed.'
    if a.family in ('health','transit'):
        program['review']='This '+('health-care use is not screened in the current district snapshot; review Health Care Service and the pharmacy tenancy.' if a.family=='health' else 'pavilion needs transport-operator/corridor approval and a use review. Only the cafe component is listed; the station is not assumed permitted by appearance.')
    addition=json.dumps({s['slug']+'-v1':program},indent=2,ensure_ascii=False)[1:-2]
    pos=old.rfind('\n}')
    new=old[:pos]+','+addition+old[pos:];json.loads(new);program_path.write_text(new,encoding='utf-8',newline='\n')
    roster_path=root/'frontend/src/data/finalFiveBuildingBatch.json';roster=json.loads(roster_path.read_text())
    roster['entries'].append(dict(archetype_id=s['slug'],variant_id=s['slug']+'-v1',candidate=a.candidate,entrance=entrance))
    roster_path.write_text(json.dumps(roster,indent=2)+'\n',encoding='utf-8')
    from .sync_plan_dims import main as sync_plan_dims
    sync_plan_dims()
    print('Enrolled exact local candidate. Refresh the reference availability index and restart the backend before browser testing.')

if __name__=='__main__':main()
