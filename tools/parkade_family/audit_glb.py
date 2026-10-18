"""Measure actual reimported GLB walking seams, ramp surfaces and headroom.

These bounded rays are geometry QA, not swept-path/accessibility certification.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
import specs as S


def main():
    p=argparse.ArgumentParser();p.add_argument('glb',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(a.glb))
    bpy.context.view_layer.update();vertices=[];faces=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH' or not any(m and m.name.startswith(('CLAY_DECK','CLAY_CONCRETE')) for m in obj.data.materials):continue
        offset=len(vertices);vertices.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        faces.extend(tuple(offset+i for i in face.vertices) for face in obj.data.polygons)
    tree=BVHTree.FromPolygons(vertices,faces,all_triangles=False)
    checks=[]
    def supported(name,x,y,z):
        hit=tree.ray_cast(Vector((x,y,z+.05)),Vector((0,0,-1)),.08)[0]
        checks.append(dict(name=name,point_m=[x,y,z],hit_m=list(hit) if hit is not None else None,
            passed=hit is not None and abs(hit.z-z)<.001))
    for level,z in enumerate(S.LEVELS[1:],1):
        for sign in (-1,1):
            for x in (25.05,25.15,25.25):supported(f'stair landing to deck L{level+1}',sign*x,-17,z)
            hit=tree.ray_cast(Vector((sign*30.2,-15,z-.32)),Vector((-sign,0,0)),.8)[0]
            checks.append(dict(name=f'No opaque side beam across glazed tower L{level+1}',
                side=sign,hit_m=list(hit) if hit is not None else None,passed=hit is None))
    clearances=[]
    for level in range(3):
        for x in (-22,-10,0,10,22):
            z=S.ramp_height(level,x)
            for y in (11.76,14.75,17.74):
                supported(f'ramp {level+1} surface',x,y,z)
                if level<2:
                    hit=tree.ray_cast(Vector((x,y,z+.05)),Vector((0,0,1)),4)[0]
                    clearance=None if hit is None else hit.z-z
                    clearances.append(clearance)
                    checks.append(dict(name=f'ramp {level+1} headroom',point_m=[x,y,z],
                        clearance_m=clearance,passed=clearance is not None and clearance>=2.4))
        for x in (-26.5,26.5):
            for z in (S.LEVELS[level],S.LEVELS[level+1]):supported('ramp end landing',x,14.75,z)
    result=dict(model_sha256=hashlib.sha256(a.glb.read_bytes()).hexdigest(),checks=checks,
        status='PASS' if all(c['passed'] for c in checks) else 'FAIL',
        minimum_measured_ramp_headroom_m=min(c for c in clearances if c is not None),
        limitation='Sparse exact-GLB surface rays; no swept path, code, slope terrain or dynamic collision certification.')
    with a.output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(dict(status=result['status'],checks=len(checks),failed=sum(not c['passed'] for c in checks))))
    if result['status']!='PASS':raise RuntimeError('Actual GLB geometry audit failed; see immutable receipt')


if __name__=='__main__':main()
