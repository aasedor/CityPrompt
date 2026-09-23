"""Delivered path corridor widths, clear travel bands and cross-connection."""
import bpy
import json
import math
from pathlib import Path
import sys
from mathutils import Vector

root=Path(sys.argv[sys.argv.index('--')+1]);r=json.loads((root/'recipe.json').read_text())
assert [b['width_m'] for b in r['bands']]==[2.5,.5,3,2]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(root/'assembly-preview.glb'))
pts=[o.matrix_world@Vector(v) for o in bpy.context.scene.objects if o.type=='MESH' for v in o.bound_box]
assert all(math.isfinite(v) for p in pts for v in p)
assert all(abs(p.x)<=4.001 and abs(p.y)<=18.001 for p in pts)
deps=bpy.context.evaluated_depsgraph_get()
def height(x,y):
    hit,p,*_=bpy.context.scene.ray_cast(deps,Vector((x,y,2)),Vector((0,0,-1)))
    assert hit,(x,y,'missing surface');return p.z
samples=0
for x in (-3.8,-2.75,-1.7,-.8,.5,1.8):
    for i in range(70):
        assert abs(height(x,-17.5+i*.5))<.012,(x,i,'travel obstruction');samples+=1
for x in (-3.8,-2.75,-1.7,-1.25,-.8,.5,1.8,2.5,3.8):
    for y in (-1.4,0,1.4):assert abs(height(x,y))<.012,(x,y,'crossing blocked');samples+=1
for y in (-4,4):assert abs(height(-1.25,y)-.08)<.005
result=dict(status='PASS_OFFLINE_GEOMETRY',checks=['8 m section with 2.5 m footpath and 3 m cycle track','finite full-envelope geometry',f'{samples} unobstructed travel and crossing rays','raised divider outside flush crossing'],runtime_tested=False)
(root/'geometry-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print('PASS_OFFLINE_GEOMETRY')
