"""Verify actual delivered park surfaces and clear circulation, not only recipe metadata."""
import bpy
import json
import math
from pathlib import Path
import sys
from mathutils import Vector

root=Path(sys.argv[sys.argv.index('--')+1]);r=json.loads((root/'recipe.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(root/'assembly-preview.glb'))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
points=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
assert all(math.isfinite(v) for p in points for v in p)
w,d=r['dimensions_m'];assert all(abs(p.x)<=w/2+.001 and abs(p.y)<=d/2+.001 for p in points)
deps=bpy.context.evaluated_depsgraph_get()
def height(x,y,paving=False):
    hit,p,normal,index,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((x,y,1.6)),Vector((0,0,-1)))
    if hit:
        if paving:assert obj.data.materials[obj.data.polygons[index].material_index].name.startswith('pale'),(x,y,'route not paved')
        return p.z
    values=[]
    for dx in (-.0001,.0001):
        ok,q,normal,index,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((x+dx,y,1.6)),Vector((0,0,-1)))
        assert ok,(x,y,'unsupported walking surface');values.append(q.z)
        if paving:assert obj.data.materials[obj.data.polygons[index].material_index].name.startswith('pale')
    assert abs(values[0]-values[1])<.0002
    return sum(values)/2
samples=0
for x0,y0,x1,y1 in r['clear_routes']:
    for i in range(1,20):
        for j in range(1,8):
            x=x0+(x1-x0)*i/20;y=y0+(y1-y0)*j/8
            assert abs(height(x,y,True))<.006,(x,y,'walking obstruction');samples+=1
checks=['finite GLB geometry','full footprint containment',f'{samples} clear walking-surface rays']
if 'basin' in r:
    assert abs(height(-3.5,0)+.35)<.005
    assert abs(height(-5.25,0)+.175)<.005
    checks+=['actual open basin bottom at -0.35 m','sloped bank at half depth; no ground cap']
else:
    counts={k:sum(p['module']==k for p in r['placements']) for k in r['assets']}
    assert counts=={'picnic-table':4,'timber-pergola':1,'garden-bench':2,'garden-light':2}
    checks+=['four tables and one pergola','clear centre aisle under pergola']
result=dict(status='PASS_OFFLINE_GEOMETRY',checks=checks,runtime_tested=False)
(root/'geometry-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('PASS_OFFLINE_GEOMETRY',checks)
