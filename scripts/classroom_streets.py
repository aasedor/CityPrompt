"""Verify/stage the finite three native classroom street deliveries.

Default is read-only. Does not change original streets, seed project geometry,
run a browser, or grant runtime approval.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import struct
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.public_realm_assets.stage_street_pilots import stage_inspected

SEED=Path('seed/classroom-streets')
IDS={'student_cycle_avenue_v1','student_green_alley_v1','student_school_street_v1'}


def digest(data):return hashlib.sha256(data).hexdigest()


def inspect(root=ROOT):
    rows=json.loads((root/SEED/'manifest.json').read_text())
    if len(rows)!=3 or {r['id'] for r in rows}!=IDS:raise ValueError('Expected exactly three locked street types')
    result=[]
    for row in rows:
        package=root/SEED/row['id']
        recipe_bytes=(package/'source-recipe.json').read_bytes()
        if digest(recipe_bytes)!=row['sourceRecipeSha256']:raise ValueError('Changed source recipe')
        recipe=json.loads(recipe_bytes)
        if recipe['assembly']['sha256']!=row['sourceAssemblySha256']:raise ValueError('Changed original assembly lock')
        program=row['program']
        if digest(json.dumps(program,sort_keys=True,separators=(',',':')).encode())!=row['programSha256']:
            raise ValueError('Changed source detail program')
        if program['surfaceRegions']!=recipe['surface_regions']:raise ValueError('Changed ground ownership')
        for mesh in program['meshDetails']:
            p,i=mesh['positions'],mesh['indices']
            if not p or len(p)%3 or len(i)%3 or not all(math.isfinite(v) for v in p):raise ValueError('Invalid source detail vertices')
            if any(type(v)!=int or not 0<=v<len(p)//3 for v in i):raise ValueError('Invalid source detail triangle')
            if mesh['material'] not in program['palette']:raise ValueError('Missing source material')
        files={}
        for name,lock in row['modules'].items():
            if not re.fullmatch('[a-z][a-z0-9_]*',name):raise ValueError('Invalid module identity')
            data=(package/(name+'.glb')).read_bytes()
            if digest(data)!=lock['sha256'] or len(data)!=lock['bytes'] or lock['sha256']!=recipe['modules'][name]['sha256']:
                raise ValueError('Changed native module')
            magic,version,length,size,kind=struct.unpack('<4sIIII',data[:20])
            if magic!=b'glTF' or version!=2 or length!=len(data) or kind!=0x4E4F534A:raise ValueError('Invalid GLB')
            document=json.loads(data[20:20+size])
            if any('uri' in v for key in ('buffers','images') for v in document.get(key,[])):raise ValueError('External module dependency')
            files[name+'.glb']=data
        reference=(package/'reference.png').read_bytes()
        if digest(reference)!=row['referenceSha256']:raise ValueError('Changed reference image')
        files['reference.png']=reference
        result.append((row,files))
    return result


def write_cards(rows):
    path=ROOT/'frontend/src/data/classroomExpansion.json'
    data=json.loads(path.read_text())
    entries=[];assets=[]
    for row in rows:
        group='active' if row['id']=='student_cycle_avenue_v1' else 'alley' if row['id']=='student_green_alley_v1' else 'calming'
        entries.append(dict(domain='street',title=row['title'],archetype_id=row['sourceArchetypeId'],variant_id=row['id'],
            version=row['id'],placement_id=row['id'],sha256=row['sourceAssemblySha256'],asset_review='source_reconstruction_verified',runtime_status='NOT TESTED',completed=False))
        assets.append(dict(id=row['id'],kind='street',definitionVersion=1,readiness='pilot',label=row['title'],
            description=f"{row['widthM']} m wide; native planting and furniture on a drawn route.",thumbnail=row['thumbnailUrl'],
            model=dict(variantId=row['id'],revision=row['sourceRecipeSha256'],method='native_street_modules_v1'),
            calgaryGuide=dict(groupId=group,basis='form_reference'),reshapeMode='fixed_section_route',sectionWidth=row['widthM'],
            properties=dict(road_archetype_id=row['sourceArchetypeId'],road_selected_variant_id=row['id'],width=row['widthM'],
                pick_place_street_section=row['id'],pick_place_automatic_3d=True,pick_place_definition_version=1,
                community_3d_mask_existing_tiles=True,road_standard_citation='City Prompt reference-informed teaching concept')))
    data['entries']=[e for e in data['entries'] if e['domain']!='street']+entries
    data['assets']=[a for a in data['assets'] if a['kind']!='street']+assets
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--public-root',type=Path)
    parser.add_argument('--manifest',type=Path)
    parser.add_argument('--write-catalogue',action='store_true')
    args=parser.parse_args()
    inspected=inspect()
    if args.public_root:
        if not args.manifest:parser.error('--public-root needs --manifest')
        stage_inspected(inspected,args.public_root,args.manifest,dry_run=True)
        stage_inspected(inspected,args.public_root,args.manifest,dry_run=False)
    if args.write_catalogue:write_cards([row for row,_ in inspected])
    print('PASS: three native street sources/modules/programs; browser acceptance pending')


if __name__=='__main__':main()
