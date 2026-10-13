import argparse, hashlib, io, json, struct
from pathlib import Path
import trimesh
from PIL import Image

HOLD = {'neighborhood-park-corten-planter-bench-v1', 'urban-pocket-park-concrete-timber-seat-v1'}

def inspect(path, expected_hash, expected_size):
    data = path.read_bytes()
    if len(data) != expected_size or hashlib.sha256(data).hexdigest() != expected_hash:
        raise ValueError('Source checksum/size mismatch')
    magic, version, size = struct.unpack_from('<4sII', data)
    if (magic, version, size) != (b'glTF', 2, len(data)):
        raise ValueError('Not a complete GLB v2')
    length, kind = struct.unpack_from('<II', data, 12)
    if kind != 0x4e4f534a: raise ValueError('Missing JSON chunk')
    gltf = json.loads(data[20:20+length])
    if any('uri' in b for b in gltf.get('buffers', [])) or any('uri' in i for i in gltf.get('images', [])):
        raise ValueError('External/data URI dependency is not accepted')
    scene = trimesh.load(path, force='scene', process=False)
    lo, hi = scene.bounds; dims = hi-lo
    if min(dims) <= 0: raise ValueError('Empty geometry')
    bin_start = 20+length+8
    texture_sizes=[]
    for image in gltf.get('images', []):
        v=gltf['bufferViews'][image['bufferView']]; start=bin_start+v.get('byteOffset',0)
        with Image.open(io.BytesIO(data[start:start+v['byteLength']])) as im: texture_sizes.append(list(im.size))
    primitives=[p for m in gltf.get('meshes',[]) for p in m['primitives']]
    return {'sha256': expected_hash, 'bytes': len(data), 'dimensions':[float(dims[0]),float(dims[2]),float(dims[1])],
        'source_y_up_bounds':scene.bounds.tolist(), 'offset':[-float((lo[0]+hi[0])/2),-float(lo[1]),-float((lo[2]+hi[2])/2)],
        'triangles':sum(gltf['accessors'][p['indices']]['count']//3 for p in primitives if 'indices' in p),
        'vertices':sum(gltf['accessors'][p['attributes']['POSITION']]['count'] for p in primitives),
        'draw_calls':len(primitives),'materials':len(gltf.get('materials',[])), 'texture_sizes':texture_sizes,
        'texture_memory_estimate_bytes':sum(w*h*4*4//3 for w,h in texture_sizes),
        'extensions_required':gltf.get('extensionsRequired',[])}

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    old=json.loads((args.source/'handoff/older_142_inventory.json').read_text())['models']
    new=json.loads((args.source/'handoff/new_54_inventory.json').read_text())
    existing=json.loads((Path(__file__).resolve().parents[1]/'frontend/src/features/parks/detailCatalogueExtras.json').read_text())
    by_hash={e.get('sha256'):e['id'] for e in existing}
    records=[]
    for m in old:
        c=m.get('corrected_copy');sha=c['corrected_sha256'] if c else m['sha256'];size=c['corrected_bytes'] if c else m['bytes']
        row={'id':m['asset_id'],'name':m['name'],'category':m['category'],'source_original_sha256':m['sha256'],'preferred_sha256':sha,'source_url':c['drive_model_url'] if c else m['drive_model_url'],'correction':c,'status':'download_pending'}
        file=args.source/'models'/f"{m['asset_id']}.glb"
        if file.exists():
            try:
                row['metrics']=inspect(file,sha,size)
                row['status']='held_functional_review' if m['asset_id'] in HOLD else 'runtime_qa_pending'
                if sha in by_hash:row.update(status='already_present',canonical_id=by_hash[sha])
            except Exception as e:row.update(status='validation_failed',error=str(e))
        records.append(row)
    for m in new:
        records.append({'id':m['concept_id'],'name':m['display_name'],'category':m['category'],'status':'held_rework' if 'REWORK' in m['qa_status'] else 'export_blocked','source':m})
    assert len(records)==196 and len({r['id'] for r in records})==196
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(records,indent=2)+'\n')
    from collections import Counter
    print(dict(Counter(r['status'] for r in records)))
if __name__=='__main__': main()
