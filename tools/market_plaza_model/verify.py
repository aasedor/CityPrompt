"""Inspect delivered GLBs, whole-module fit and advertised clear circulation."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

def load(path):
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(path))
    obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
    pts=[o.matrix_world@Vector(p) for o in obs for p in o.bound_box]
    assert pts and all(math.isfinite(v) for p in pts for v in p)
    return [[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]

def overlap(a,b):return a[0]<b[2]-1e-5 and a[2]>b[0]+1e-5 and a[1]<b[3]-1e-5 and a[3]>b[1]+1e-5

root=Path(sys.argv[sys.argv.index('--')+1]);recipe=json.loads((root/'recipe.json').read_text())
bounds={k:load(root/v['path']) for k,v in recipe['assets'].items()}
for k,(lo,hi) in bounds.items():assert abs(lo[2])<.001,(k,lo)
boxes=[]
for p in recipe['placements']:
    lo,hi=bounds[p['module']];a=p['rotation'];c,s=math.cos(a),math.sin(a)
    corners=[(p['x']+x*c-y*s,p['y']+x*s+y*c) for x in (lo[0],hi[0]) for y in (lo[1],hi[1])]
    b=[min(x for x,y in corners),min(y for x,y in corners),max(x for x,y in corners),max(y for x,y in corners)]
    assert b[0]>=-16 and b[2]<=16 and b[1]>=-14 and b[3]<=14
    assert not overlap(b,[-2,-14,2,14]),('north-south route',p)
    assert not overlap(b,[-16,2,16,5]),('east-west route',p)
    assert not overlap(b,[-6,-7,6,7]),('event square',p)
    assert not any(overlap(b,other) for other in boxes),('module collision',p)
    boxes.append(b)
counts={k:sum(p['module']==k for p in recipe['placements']) for k in bounds}
assert counts=={'market-stall':6,'timber-bench':4,'prairie-planter':4,'plaza-light':4},counts
load(root/'assembly-preview.glb')
result=dict(status='PASS_OFFLINE_GEOMETRY',module_bounds_m=bounds,counts=counts,
    checks=['GLB finite geometry','module feet at zero','whole furniture fit','no module overlap','four entrances and crossing corridors clear','12 x 14 m event area clear'],
    runtime_tested=False)
(root/'geometry-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('PASS_OFFLINE_GEOMETRY',counts)
