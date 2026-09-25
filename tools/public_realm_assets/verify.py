"""Verify delivered GLB, hashes and physical walking corridors, not only recipes."""
import bpy, json, math, sys, hashlib, struct
from pathlib import Path
from mathutils import Vector
root=Path(sys.argv[sys.argv.index('--')+1]);r=json.loads((root/'recipe.json').read_text())
for record in [r['assembly'],*r.get('modules',{}).values(),*([r['sport_asset']] if 'sport_asset' in r else [])]:
    p=root/record['path']
    if not p.exists():p=root/'modules'/record['path']
    data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==record['sha256'];assert len(data)==record['bytes']
    assert data[:4]==b'glTF';n=struct.unpack_from('<I',data,12)[0];g=json.loads(data[20:20+n])
    assert all('uri' not in b for b in g.get('buffers',[]));assert all('uri' not in i for i in g.get('images',[]))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(root/'assembly-preview.glb'))
objects=[o for o in bpy.context.scene.objects if o.type=='MESH'];w,d=r['dimensions_m']
pts=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
assert all(math.isfinite(v) for p in pts for v in p)
assert all(abs(p.x)<=w/2+.05 and abs(p.y)<=d/2+.05 for p in pts)
deps=bpy.context.evaluated_depsgraph_get();samples=0
def check(x,y):
    # Tiny inward offset avoids exact triangle-edge precision ambiguity.
    hit,p,n,index,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((x+.000013,y+.000021,1.6)),Vector((0,0,-1)))
    assert hit,(x,y,'unsupported')
    assert abs(p.z)<.025,(x,y,p.z,'obstructed walking corridor')
    mat=obj.data.materials[obj.data.polygons[index].material_index].name
    assert mat.split('.')[0] in ('paving','runoff','edge','paint','court','asphalt','cycle'),(x,y,mat,'not a walking surface')
for route in r['clear_routes']:
    a,b=route['a'],route['b'];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
    for i in range(math.ceil(length/.35)+1):
        t=i/math.ceil(length/.35)
        for fraction in (-.45,0,.45):
            off=route['width']*fraction
            check(a[0]+dx*t-dy/length*off,a[1]+dy*t+dx/length*off);samples+=1
# Every tree root must resolve to soft ground or its paired physical well.
# Ray below the low foliage at an offset clear of the authored trunk.
tree_checks=0
for tree in r['placements']:
    if tree['kind'] not in ('shade_tree','grove_tree','ornamental_tree'):continue
    x,y=tree['x'],tree['y'];surface='grass'
    for region in r['surface_regions']:
        if abs(x-region['x'])<=region['width']/2 and abs(y-region['y'])<=region['depth']/2:surface=region['material']
    assert surface in ('grass','soil'),(tree,'tree without soft root opening')
    well=next((well for well in r.get('tree_wells',[]) if well['x']==x and well['y']==y),None)
    if well:
        hit,p,n,index,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((x+.30,y+.12,.065)),Vector((0,0,-1)))
        assert hit and -.005<=p.z<=.055,(tree,'missing tree-well surface')
        mat=obj.data.materials[obj.data.polygons[index].material_index].name.split('.')[0]
        assert mat in ('soil','kit_linear_vertex_colour'),(tree,'pavement across tree well',mat)
    tree_checks+=1
result=dict(status='PASS_OFFLINE_GEOMETRY',checks=['self-contained GLB buffers','delivered byte hashes','finite metric bounds',f'{samples} clear material-aware route rays',f'{tree_checks} tree root openings checked'],runtime_tested=False)
(root/'geometry-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
