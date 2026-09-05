"""Verify actual delivered geometry, not pre-export bounding-box estimates."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

import numpy as np
import trimesh


def verify(root):
    manifest=json.loads((root/'manifest.json').read_text())
    results=[]
    for name,asset in manifest['assets'].items():
        path=root/Path(asset['url']).name; raw=path.read_bytes()
        length=struct.unpack_from('<I',raw,12)[0]; gltf=json.loads(raw[20:20+length])
        scene=trimesh.load(path,force='scene',process=False)
        checks=dict(hash=hashlib.sha256(raw).hexdigest()==asset['sha256'],bytes=len(raw)==asset['bytes'],
                    ground=bool(abs(scene.bounds[0][1])<1e-5),
                    dimensions=bool(np.allclose(scene.extents[[0,2,1]],asset['dimensionsM'],atol=1e-4)),
                    meshCount=len(gltf['meshes'])==asset['meshCount'])
        if name.startswith('tree'):
            points=np.concatenate([trimesh.transform_points(scene.geometry[scene.graph[node][1]].vertices,scene.graph[node][0]) for node in scene.graph.nodes_geometry])
            checks['crownRadius']=bool(np.sqrt(points[:,0]**2+points[:,2]**2).max()<=3.0001)
            checks['alphaMask']=any(m.get('alphaMode')=='MASK' and m.get('alphaCutoff')==.25 for m in gltf['materials'])
        if name=='boulders':
            contacts=[]
            for node in scene.graph.nodes_geometry:
                transform,geometry=scene.graph[node]
                # Weld exported UV/normal seams only for connected-rock audit.
                mesh=scene.geometry[geometry].copy();mesh.merge_vertices(merge_tex=True,merge_norm=True)
                neighbours=[set() for _ in mesh.vertices]
                for a,b,c in mesh.faces:
                    neighbours[a].update((b,c));neighbours[b].update((a,c));neighbours[c].update((a,b))
                unseen=set(range(len(mesh.vertices)))
                while unseen:
                    stack=[unseen.pop()];component=[]
                    while stack:
                        vertex=stack.pop();component.append(vertex)
                        following=neighbours[vertex]&unseen;unseen.difference_update(following);stack.extend(following)
                    contacts.append(float(trimesh.transform_points(mesh.vertices[component],transform)[:,1].min()))
            checks['everyRockGrounded']=len(contacts)==4 and all(abs(y)<1e-5 for y in contacts)
        results.append(dict(name=name,checks=checks))
    return dict(status='PASS' if all(all(r['checks'].values()) for r in results) else 'FAIL',
                totalBytes=sum(a['bytes'] for a in manifest['assets'].values()),assets=results)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('candidate',type=Path);args=parser.parse_args()
    result=verify(args.candidate);print(json.dumps(result,indent=2))
    raise SystemExit(0 if result['status']=='PASS' else 1)
