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
deps=bpy.context.evaluated_depsgraph_get();samples=0;route_failures=[]
def check(x,y):
    # Tiny inward offset avoids exact triangle-edge precision ambiguity.
    # Border routes terminate exactly on the plot: keep the precision probe inside.
    px=max(-w/2+.0001,min(w/2-.0001,x+.000013))
    py=max(-d/2+.0001,min(d/2-.0001,y+.000021))
    hit,p,n,index,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((px,py,1.6)),Vector((0,0,-1)))
    if not hit:
        route_failures.append((x,y,'unsupported'));return
    if abs(p.z)>=.025:
        route_failures.append((x,y,p.z,obj.name,obj.data.materials[obj.data.polygons[index].material_index].name,'obstructed walking corridor'));return
    mat=obj.data.materials[obj.data.polygons[index].material_index].name
    if mat.split('.')[0] not in ('paving','runoff','edge','paint','court','asphalt','cycle','rubber'):
        route_failures.append((x,y,mat,'not a walking surface'))
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
    else:
        hit,p,n,index,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((x+.30,y+.12,.065)),Vector((0,0,-1)))
        assert hit and -.025<=p.z<=.025,(tree,'missing soft ground at root')
        mat=obj.data.materials[obj.data.polygons[index].material_index].name.split('.')[0]
        assert mat in ('soil','grass'),(tree,'hard ground across tree root',mat)
    tree_checks+=1
if route_failures:
    (root/'route-failures.json').write_text(json.dumps(route_failures,indent=2)+'\n')
    raise AssertionError(f'{len(route_failures)} route failures: {route_failures[:12]}')
ride_checks=0
elevated_checks=0
for route in r.get('elevated_access_routes',[]):
    a,b=route['a'],route['b'];dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);steps=math.ceil(length/.10)
    for i in range(steps+1):
        t=i/steps;z=a[2]+(b[2]-a[2])*t
        for fraction in (-.45,0,.45):
            off=route['width']*fraction;x=a[0]+dx*t-dy/length*off;y=a[1]+dy*t+dx/length*off
            hit,p,n,index,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((x,y,z+1.5)),Vector((0,0,-1)))
            assert hit and abs(p.z-z)<.025,(x,y,z,tuple(p),'elevated access is stepped or unsupported')
            mat=obj.data.materials[obj.data.polygons[index].material_index].name.split('.')[0]
            assert mat=='concrete',(x,y,z,mat,'not concrete access')
            elevated_checks+=1
for x,y,z in r.get('ride_ingress_checks',[]):
    hit,p,n,index,obj,matrix=bpy.context.scene.ray_cast(deps,Vector((x,y,z+1.5)),Vector((0,0,-1)))
    assert hit and abs(p.z-z)<.035,(x,y,z,tuple(p),'cycle ingress missing height match')
    mat=obj.data.materials[obj.data.polygons[index].material_index].name.split('.')[0]
    assert mat=='asphalt',(x,y,z,mat,'cycle entrance not connected asphalt')
    ride_checks+=1
result=dict(status='PASS_OFFLINE_GEOMETRY',model_sha256=r['assembly']['sha256'],checks=['self-contained GLB buffers','delivered byte hashes','finite metric bounds',f'{samples} clear material-aware route rays',f'{tree_checks} tree root openings checked'],runtime_tested=False)
if ride_checks:result['checks'].append(f'{ride_checks} measured full-width cycle ingress contacts')
if elevated_checks:result['checks'].append(f'{elevated_checks} measured full-width elevated access contacts')
(root/'geometry-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
