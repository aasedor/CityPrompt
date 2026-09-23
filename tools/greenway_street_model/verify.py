"""Inspect delivered road fixture: full section, flush crossing, table and lamps."""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

root=Path(sys.argv[sys.argv.index('--')+1]);r=json.loads((root/'recipe.json').read_text())
assert abs(sum(b['width_m'] for b in r['bands'])-11)<1e-6
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(root/'assembly-preview.glb'))
obs=[o for o in bpy.context.scene.objects if o.type=='MESH']
pts=[o.matrix_world@Vector(p) for o in obs for p in o.bound_box]
assert all(math.isfinite(v) for p in pts for v in p)
assert abs(min(p.x for p in pts)+5.5)<.001 and abs(max(p.x for p in pts)-5.5)<.001
assert abs(min(p.y for p in pts)+24)<.001 and abs(max(p.y for p in pts)-24)<.001
deps=bpy.context.evaluated_depsgraph_get()
def height(x,y):
    hit,p,*_=bpy.context.scene.ray_cast(deps,Vector((x,y,10)),Vector((0,0,-1)))
    if hit:return p.z
    # GLB float32 band seams can miss an exactly-on-edge ray. Both adjacent
    # surfaces must exist within 0.1 mm and agree; one-sided support cannot pass.
    adjacent=[]
    for dx in (-.0001,.0001):
        ok,q,*_=bpy.context.scene.ray_cast(deps,Vector((x+dx,y,10)),Vector((0,0,-1)))
        assert ok,(x,y,'missing surface beside seam');adjacent.append(q.z)
    assert abs(adjacent[0]-adjacent[1])<.0002,(x,y,'discontinuous seam')
    return sum(adjacent)/2
for y in (-1.4,0,1.4):
    for i in range(105):
        x=-5.2+i*.1
        assert abs(height(x,y))<.01,(x,y,'crossing obstruction')
for x in (-4.4,4.4):
    for y,z in [(-5,.15),(-2.5,.075),(2.5,.075),(5,.15)]:assert abs(height(x,y)-z)<.005
for x in (-2,0,2):
    for y,z in [(5,0),(5.5,.0375),(7,.075),(8.5,.0375),(9,0)]:assert abs(height(x,y)-z)<.005
for p in r['fixture_positions']:
    assert 2.6+.24<abs(p['x'])<3.6-.24
    assert abs(p['y'])>3.5 and abs(p['z']-.15)<.001
result=dict(status='PASS_OFFLINE_GEOMETRY',checks=['exact 11 m section','48 m fixture extent','315 ray samples across unobstructed flush crossing','sidewalk ramp continuity','speed table rise and full width','lamps outside sidewalk and crossing'],runtime_tested=False)
(root/'geometry-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('PASS_OFFLINE_GEOMETRY')
