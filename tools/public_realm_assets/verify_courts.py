"""Reimported-mesh checks for the bounded ten-court batch, without a browser."""
import json, math, runpy, sys
from pathlib import Path
from mathutils import Vector

base=runpy.run_path(str(Path(__file__).with_name('verify.py')))
r,root,bpy,deps,result=(base[k] for k in ('r','root','bpy','deps','result'))

def ray(x,y,z):
    return bpy.context.scene.ray_cast(deps,Vector((x,y,z)),Vector((0,0,-1)))

try:
    # Detect overlapping top faces in the actual exported floor meshes.
    tops={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or not o.data.materials:continue
        mat=o.data.materials[0].name.split('.')[0]
        if mat in ('runoff','court','sand','gravel','bocce_lane'):
            tops[mat]=max(tops.get(mat,-math.inf),max((o.matrix_world@Vector(v)).z for v in o.bound_box))
    for name in ('court','sand','gravel'):
        if name in tops:assert tops[name]-tops['runoff']>.004,(r['sport'],'coplanar playing-surface underlay')
    if r['sport']=='bocce':
        assert tops['bocce_lane']-tops['gravel']>.004,(r['sport'],'coplanar bocce lane and surrounding gravel')
    samples=0
    allowed={'paving','edge','runoff','court','sand','sand_grain','gravel','gravel_grain','bocce_lane','paint','key'}
    for route in r['sport_access_routes']:
        a,b=route['a'],route['b'];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);n=math.ceil(length/.18)
        for i in range(n+1):
            for fraction in (-.45,0,.45):
                off=route['width']*fraction
                x=a[0]+dx*i/n-dy/length*off;y=a[1]+dy*i/n+dx/length*off
                hit,p,_,idx,obj,_=ray(x+.000013,y+.000021,2)
                assert hit and abs(p.z)<.025,(r['sport'],x,y,'blocked court entrance',p.z)
                mat=obj.data.materials[obj.data.polygons[idx].material_index].name.split('.')[0]
                assert mat in allowed,(r['sport'],mat,'wrong entrance surface')
                samples+=1
    cy=r['fixed_program']['center'][1]
    equipment_checks=0
    for equipment in r.get('equipment',[]):
        if equipment['kind'].endswith('_hoop'):
            hit,p,*_=ray(equipment['x']+equipment['radius'],equipment['y']+cy,4.5)
            assert hit and abs(p.z-equipment['z'])<.025,(r['sport'],'rim height',p.z)
        else:
            hit,p,*_=ray(.013,cy,r['net_center_m']+.3)
            assert hit and abs(p.z-r['net_center_m'])<.012,(r['sport'],'net center height',p.z)
        equipment_checks+=1
    mw,md=r['module_m'];crowns=0
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or not any(name in o.name for name in ('grove_tree','ornamental_tree')):continue
        pts=[o.matrix_world@Vector(v) for v in o.bound_box]
        x0,x1=min(p.x for p in pts),max(p.x for p in pts);y0,y1=min(p.y for p in pts),max(p.y for p in pts)
        assert x1<=-mw/2 or x0>=mw/2 or y1<=cy-md/2 or y0>=cy+md/2,(r['sport'],o.name,'tree intrudes into fixed sport reserve')
        crowns+=1
    # A padel enclosure must have physical transparent end/side walls and open doors.
    if r['sport']=='padel':
        for start,direction in (((0,cy,1.5),(0,1,0)),((0,cy,1.5),(0,-1,0)),((0,cy+7.1,1.5),(1,0,0)),((0,cy+7.1,1.5),(-1,0,0))):
            hit,_,_,idx,obj,_=bpy.context.scene.ray_cast(deps,Vector(start),Vector(direction))
            mat=obj.data.materials[obj.data.polygons[idx].material_index]
            assert hit and mat.name.split('.')[0]=='glass',(mat.name,'missing padel glass')
        for y in (-.6,.6):
            hit,*_=bpy.context.scene.ray_cast(deps,Vector((-6,cy+y,1.2)),Vector((1,0,0)),distance=2)
            assert not hit,'padel door blocked'
    assert r['triangles']<350000,(r['sport'],'triangle budget')
    assert r['mesh_instances']<260,(r['sport'],'mesh budget')
    result['checks'] += ['no coplanar sport underlay',f'{samples} court-entry width rays',f'{equipment_checks} measured net/rim heights',f'{crowns} tree-part envelopes outside sport reserve','bounded triangles and mesh instances']
    result['browser_tested']=False
    (root/'geometry-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('PASS_SPORTS_ASSET',r['id'],json.dumps(result))
except Exception as exc:
    (root/'geometry-verification.json').write_text(json.dumps(dict(status='FAIL_OFFLINE_SPORTS',failure=str(exc),runtime_tested=False),indent=2)+'\n',encoding='utf-8')
    raise
