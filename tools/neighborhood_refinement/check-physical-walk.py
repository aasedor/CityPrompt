"""Check sampled app-solver paths against the exact reimported GLB."""
import bpy,json,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
p=Path(sys.argv[sys.argv.index('--')+1]);report=json.loads((p/'evidence/walking-solver-review.json').read_text())
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(p/(p.name+'.glb')))
vertices=[];faces=[]
for obj in bpy.context.scene.objects:
    if obj.type!='MESH' or obj.name in ('glass','leaf','plant','flower'):continue
    offset=len(vertices);vertices.extend(obj.matrix_world@v.co for v in obj.data.vertices)
    faces.extend(tuple(offset+i for i in face.vertices) for face in obj.data.polygons)
tree=BVHTree.FromPolygons(vertices,faces)
bad=[];checked=0
for i,s in enumerate(report['samples']):
    if i%3:continue
    x,y,z=s['point'];checked+=1
    floor=tree.ray_cast(Vector((x,y,z+.08)),Vector((0,0,-1)),.25)
    head=tree.ray_cast(Vector((x,y,z+.20)),Vector((0,0,1)),1.60)
    if floor[0] is None or abs(floor[0].z-z)>.085 or head[0] is not None:
        bad.append(dict(route=s['route'],point=s['point'],floor_z=None if floor[0] is None else floor[0].z,head_hit=None if head[0] is None else list(head[0])))
out=dict(candidate=p.name,samples_checked=checked,failures=bad,pass_physical_route=not bad,scope='Floor contact within 85 mm and 1.80 m head clearance along app-solver routes; not building-code certification.')
(p/'evidence/physical-walking-review.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
if bad:sys.exit(1)
