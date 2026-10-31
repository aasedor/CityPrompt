"""Install the finite nine-style local review handoff; never publish a roster.

Only bridge-owned locked modules are copied. Existing source scene GLBs and
saved identities are preserved, and manifest insertion preserves existing text.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'backend'))
from app.services.native_source_bridge import SOURCE_BRIDGE_SOURCES,validate_source_bridge_profile


def digest(data):
    return hashlib.sha256(data).hexdigest()


def atomic_module_copy(destination,data):
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists() and destination.read_bytes()==data:return
    temporary=destination.with_suffix(destination.suffix+'.review-tmp')
    temporary.write_bytes(data)
    if digest(temporary.read_bytes())!=digest(data):raise ValueError('Module copy verification failed')
    temporary.replace(destination)


def append_rows(path,rows,refresh=False,write=True):
    original=path.read_text(encoding='utf-8')
    existing=json.loads(original)
    incoming=[]
    for row in rows:
        old=next((item for item in existing if item['id']==row['id']),None)
        if old is not None:
            if old!=row:
                previous=json.dumps(old,indent=2,ensure_ascii=False)
                if not refresh or original.count(previous)!=1:
                    raise ValueError(f'Review row changed after installation: {row["id"]}')
                original=original.replace(previous,json.dumps(row,indent=2,ensure_ascii=False),1)
        else:incoming.append(row)
    if incoming:
        end=original.rfind(']')
        insertion=',\n'.join(json.dumps(row,indent=2,ensure_ascii=False) for row in incoming)
        original=original[:end].rstrip()+(',\n' if existing else '\n')+insertion+'\n'+original[end:]
    if write:path.write_text(original,encoding='utf-8')
    return original


def append_roster_array(text,key,items,identity,refresh):
    start=text.index('[',text.index('\n  "'+key+'"'))
    existing,end=json.JSONDecoder().raw_decode(text,start)
    incoming=[]
    for item in items:
        old=next((value for value in existing if value[identity]==item[identity]),None)
        if old is None:incoming.append(item)
        elif old!=item:
            previous=json.dumps(old,indent=2,ensure_ascii=False)
            formatted='\n'.join('    '+line for line in previous.splitlines())
            if not refresh or text.count(formatted)!=1:
                raise ValueError('Conflicting local bridge roster entry')
            replacement='\n'.join('    '+line for line in json.dumps(item,indent=2,ensure_ascii=False).splitlines())
            text=text.replace(formatted,replacement,1)
            start=text.index('[',text.index('\n  "'+key+'"'));existing,end=json.JSONDecoder().raw_decode(text,start)
    if incoming:
        addition=',\n'.join('\n'.join('    '+line for line in json.dumps(item,indent=2,ensure_ascii=False).splitlines()) for item in incoming)
        text=text[:end-1].rstrip()+(',\n' if existing else '\n')+addition+'\n  '+text[end-1:]
    return text


def install(batch,mirror=None,refresh=False):
    batch=Path(batch).resolve()
    receipt_path=batch/'installation-receipt.json'
    previous=json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    previous_locks={item['url']:item['sha256'] for item in previous.get('files',[])}
    if refresh and previous.get('variants')!=9:raise ValueError('No complete task-owned local installation receipt to refresh')
    rows=[];receipts=[];pending=[]
    reference_rows=json.loads((ROOT/'frontend/src/data/publicRealmRelease20261023.json').read_text(encoding='utf-8'))['models']
    for path in sorted(batch.rglob('nativeStreetPilot.json')):
        row=json.loads(path.read_text(encoding='utf-8'))
        if row['id'] not in SOURCE_BRIDGE_SOURCES:continue
        # Sparse installs may not hydrate the older canonical variant artwork.
        # Reuse the exact existing reviewed photographic hero, with a new path
        # under the authoritative archetype root; never use a blank fallback.
        hero_relative=Path(row['thumbnailUrl'].lstrip('/'))
        hero_candidates=[ROOT/'frontend/public'/hero_relative,*([Path(mirror)/hero_relative] if mirror else [])]
        valid=lambda data:data.startswith(b'\x89PNG\r\n\x1a\n') or data.startswith(b'\xff\xd8')
        if not any(candidate.exists() and valid(candidate.read_bytes()) for candidate in hero_candidates):
            original=next(item['asset']['thumbnail'] for item in reference_rows if item['runtime_sha256']==row['sourceAssemblySha256'])
            relative=Path(original.lstrip('/'))
            candidates=[ROOT/'frontend/public'/relative,*([Path(mirror)/relative] if mirror else [])]
            source=next(candidate for candidate in candidates if candidate.exists() and valid(candidate.read_bytes()))
            data=source.read_bytes()
            target=Path('archetypes/streets')/row['sourceArchetypeId'].replace('_','-')/(row['id'].replace('_','-')+source.suffix)
            row.update(thumbnailUrl='/'+target.as_posix(),thumbnailSha256=digest(data),thumbnailOriginalUrl=original)
            for destination_root in [ROOT/'frontend/public',*([Path(mirror)] if mirror else [])]:
                destination=destination_root/target
                if destination.exists() and destination.read_bytes()!=data:raise ValueError('Conflicting photographic hero')
                pending.append((destination,data))
        validate_source_bridge_profile(row)
        source=ROOT/f'frontend/public/street-kits/claude-20261023/{row["sourceAssemblySha256"]}.glb'
        if digest(source.read_bytes())!=row['sourceAssemblySha256']:raise ValueError('Original source hash mismatch')
        for kind,lock in row['modules'].items():
            data=(path.parent/(kind+'.glb')).read_bytes()
            if data[:4]!=b'glTF' or len(data)!=lock['bytes'] or digest(data)!=lock['sha256']:
                raise ValueError(f'Unverified module: {row["id"]}/{kind}')
            relative=Path(lock['url'].lstrip('/'))
            if relative.is_absolute() or '..' in relative.parts:raise ValueError('Invalid module path')
            for target_root in [ROOT/'frontend/public',*([Path(mirror).resolve()] if mirror else [])]:
                destination=target_root/relative
                if destination.exists() and destination.read_bytes()!=data:
                    if not refresh or digest(destination.read_bytes())!=previous_locks.get(lock['url']):
                        raise ValueError(f'Conflicting module: {destination}')
                pending.append((destination,data))
            receipts.append({'variant':row['id'],'kind':kind,**lock})
        rows.append(row)
    if len(rows)!=9 or {row['id'] for row in rows}!=SOURCE_BRIDGE_SOURCES.keys():
        raise ValueError('The exact finite nine-style handoff is incomplete or duplicated')
    if refresh:
        old_rows=json.loads((ROOT/'frontend/src/data/nativeBridgePilots.json').read_text())
        new_rows={row['id']:row for row in rows}
        for row in old_rows:
            if row['id'] in SOURCE_BRIDGE_SOURCES:
                validate_source_bridge_profile(row)
                for kind,lock in row['modules'].items():
                    new_lock=new_rows[row['id']]['modules'][kind]
                    destination=ROOT/'frontend/public'/lock['url'].lstrip('/')
                    if (lock['url'] not in previous_locks or digest(destination.read_bytes()) not in
                        {lock['sha256'],new_lock['sha256'],previous_locks[lock['url']]}):
                        raise ValueError('Existing row is not the task-owned previous installation')
        archive=batch/f'installation-before-{digest(receipt_path.read_bytes())[:12]}.json'
        if not archive.exists():archive.write_bytes(receipt_path.read_bytes())
    manifests=[]
    for folder in ['frontend/src/data','backend/app/data']:
        bridge_manifest=ROOT/folder/'nativeBridgePilots.json'
        manifests.append((bridge_manifest,append_rows(bridge_manifest,rows,refresh,write=False)))
        roster=ROOT/folder/'classroomStarter.json'
        entries=[];dependencies=[]
        for row in rows:
            deps=[]
            for lock in row['modules'].values():
                relative=lock['url'].lstrip('/');identity='public:'+relative;deps.append(identity)
                dependencies.append({'id':identity,'location':'public','path':relative,'sha256':lock['sha256'],'bytes':lock['bytes']})
            if row.get('thumbnailSha256'):
                relative=row['thumbnailUrl'].lstrip('/');identity='public:'+relative;deps.append(identity)
                hero=next(data for destination,data in pending if destination==ROOT/'frontend/public'/relative)
                dependencies.append({'id':identity,'location':'public','path':relative,'sha256':digest(hero),'bytes':len(hero)})
            entries.append({'domain':'street','representation':'native-modules','archetypeId':row['sourceArchetypeId'],
                'variantId':row['id'],'placementId':row['id'],'revision':row['sourceRecipeSha256'],
                'status':'local-pilot-runtime-pending','review':{'asset':'derived-pilot-pending','runtime':'NOT TESTED'},'dependencies':deps})
        text=roster.read_text(encoding='utf-8')
        backup=batch/'backups'/folder/'classroomStarter.json'
        if not backup.exists():backup.parent.mkdir(parents=True,exist_ok=True);backup.write_text(text,encoding='utf-8')
        text=append_roster_array(text,'entries',entries,'variantId',refresh)
        if 'dependencies' in json.loads(text):
            text=append_roster_array(text,'dependencies',dependencies,'id',refresh)
        manifests.append((roster,text))
    # Validate all source bytes, ownership receipts and complete manifest edits
    # before writing. Exact-current files permit recovery after interruption.
    for destination,data in pending:
        atomic_module_copy(destination,data)
    for destination,text in manifests:
        temporary=destination.with_suffix('.review-tmp')
        temporary.write_text(text,encoding='utf-8');temporary.replace(destination)
    evidence=ROOT/'tools/drawn_bridge_routes/provenance/remaining-source-spans-v1.json'
    evidence.write_text(json.dumps({'schemaVersion':1,'status':'local_runtime_review',
        'sourceScenesUnchanged':True,'variants':[{key:row[key] for key in
            ('id','sourceAssemblySha256','sourceRecipeSha256','programSha256','referenceSha256')} for row in rows],
        'modules':receipts},indent=2)+'\n',encoding='utf-8')
    result={'variants':len(rows),'modules':len(receipts),'bytes':sum(item['bytes'] for item in receipts),
            'sourceScenesUnchanged':True,'publication':False,'files':receipts}
    (batch/'installation-receipt.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch',required=True);parser.add_argument('--mirror');parser.add_argument('--refresh-local',action='store_true')
    args=parser.parse_args();result=install(args.batch,args.mirror,args.refresh_local)
    print(json.dumps({key:value for key,value in result.items() if key!='files'}))
