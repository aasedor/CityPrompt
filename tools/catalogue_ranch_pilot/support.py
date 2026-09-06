"""Small clay pilot utilities; compositions live in each exact-family builder."""
import argparse
import math
from pathlib import Path
import sys
import bpy
import bmesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / 'catalogue_duplex_pilot'))
import clay_core as C


def hip(name, x0, x1, y0, y1, eave, rise, role='roof'):
    # Four weathering planes and a closed bottom, ridge runs along longer Y.
    inset=min((x1-x0)/2,(y1-y0)/2)
    a,b=(y0+inset,y1-inset)
    if abs(a-b)<1e-4:b=a+.001
    xm=(x0+x1)/2
    return C.mesh(name,[(x0,y0,eave),(x1,y0,eave),(x1,y1,eave),(x0,y1,eave),
        (xm,a,eave+rise),(xm,b,eave+rise)],[(0,3,2,1),(0,1,4),(1,2,5,4),(2,3,5),(3,0,4,5)],role,'hip roof')


def union(owner,other):
    bpy.context.view_layer.objects.active=owner
    mod=owner.modifiers.new('Closed weathering union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=other
    bpy.ops.object.modifier_apply(modifier=mod.name)
    # Preserve only delivered owners in the role inventory.
    for names in C.MODULES.values():
        if other.name in names:names.remove(other.name)
    bpy.data.objects.remove(other,do_unlink=True);C.normalise(owner.data)


def stairs(x,y,top,width=1.4,count=4,direction=-1):
    for i in range(count):
        h=top*(count-i)/count
        C.box('Entrance step',(x,y+direction*(i+.5)*.29,h/2),(width,.30,h),'foundation','entrance stairs',.002)


def courses(face,length,z0,z1,holes,role='mortar',pitch=.19):
    for i in range(math.ceil((z1-z0)/pitch)):
        z=z0+i*pitch
        if z>z1:break
        spans=[(0,length)]
        for h in holes:
            if h['z']-.02<z<h['z']+h['h']+.02:
                a,b=h['u']-h['w']/2-.02,h['u']+h['w']/2+.02
                spans=[s for l,r in spans for s in [(l,min(r,a)),(max(l,b),r)] if s[1]-s[0]>.03]
        for a,b in spans:face.part('Course joint',(a+b)/2,-.002,z,b-a,.003,.008,role,'masonry courses',0)


def openings(face,length,z0,z1,holes,role='wall',joints=True):
    wall=face.wall(face.label,0,length,z0,z1,role=role,holes=holes)
    if joints:courses(face,length,z0,z1,holes)
    for h in holes:
        if h.get('door'):face.door(h['id'],h['u'],h['z'],h['w'],h['h'],glazed=h.get('glazed',False))
        else:face.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=h.get('cols',2),rows=h.get('rows',1),curtain=True)
    return wall


def room(x,y,z,w,d,h):
    C.box('Room floor',(x,y,z+.05),(w,d,.1),'floor','occupied room',0)
    C.box('Room ceiling',(x,y,z+h),(w,d,.12),'interior','occupied room',0)
    C.box('Room partition',(x,y+d*.28,z+h/2),(w,.12,h),'interior','occupied room',0)
    C.box('Table top',(x,y,z+.76),(1.4,.7,.07),'timber','occupied room',.006)
    for dx in (-.58,.58):
        for dy in (-.23,.23):C.box('Table leg',(x+dx,y+dy,z+.38),(.05,.05,.76),'timber','occupied room',0)
    C.box('Sofa seat',(x-1,y+.8,z+.43),(1.5,.65,.26),'interior','occupied room',.02)
    C.box('Sofa back',(x-1,y+1.08,z+.7),(1.5,.17,.65),'interior','occupied room',.02)
    C.qa_room_light('room',(x,y,z+h-.3),70,2)


def cameras(w,d,h):
    scale=max(w,d,h);t=(0,0,h*.46)
    return [dict(name=n,location=tuple(v*scale for v in p),target=t,**extra) for n,p,extra in [
        ('front',(0,-2.8,.45),{}),('front_corner',(-2.1,-2.5,1.15),{}),('aerial',(-2,-2.4,2.5),{}),
        ('top',(0,-.001,3.3),{'ortho_scale':scale*1.5}),('left_side',(-3,0,.5),{}),('right_side',(3,0,.5),{}),
        ('rear',(0,3,.5),{}),('rear_side',(2,2.6,1.3),{})]]


def run(module):
    p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);p.add_argument('--output',required=True)
    p.add_argument('--version',type=int,default=1);p.add_argument('--resolution',type=int,default=1440);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
    source=a.source_root/'frontend/public/archetypes/buildings'/module.SLUG
    sources=[dict(role=role,original_path=str(source/name),path='sources/'+name,bytes=(source/name).stat().st_size,sha256=C.digest(source/name))
        for role,name in [('front',f'variant_{module.INDEX}.png'),('oblique',f'variant_{module.INDEX}_angle_60.jpg'),('top',f'variant_{module.INDEX}_angle_90.jpg')]]
    entry=dict(archetype_id=module.PARENT,variant_id=module.VARIANT,_reference_root=str(source),directory='.',sources=sources)
    m=module.manifest(a.version)
    out=C.prepare_candidate(a,entry,m,module.__file__,[__file__])
    if out is None:return
    cams=C.setup(module.PALETTE,m['camera_roster'],a.resolution);module.build()
    # Large civic families need the same neutral illumination scaled to their envelope.
    if module.WIDTH>20:
        factor=module.WIDTH/11
        for obj in bpy.context.scene.objects:
            if obj.type=='LIGHT' and not obj.name.startswith('QA interior'):
                obj.location*=factor;obj.data.energy*=factor*factor;obj.data.size*=factor;C.look_at(obj,(0,0,module.HEIGHT*.4))
    for obj in C.objects():
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7)
        bmesh.ops.triangulate(bm,faces=list(bm.faces))
        zero=[f for f in bm.faces if f.calc_area()<1e-10]
        if zero:bmesh.ops.delete(bm,geom=zero,context='FACES_ONLY')
        bm.to_mesh(obj.data);bm.free();obj.data.update()
    C.deliver(out,m,cams)


def prework(module,version,dimensions,description,assumptions,contacts,extra_cameras):
    roster=cameras(module.WIDTH,module.DEPTH,module.HEIGHT)+extra_cameras
    return dict(candidate=f'{module.SLUG}-clay-v{version:03}',title=module.TITLE,method=C.METHOD,
        representation_kind='architectural_clay',archetype_id=module.PARENT,variant_id=module.VARIANT,state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=dimensions,storeys=module.STOREYS,source_measurements=description,hidden_assumptions=assumptions),
        roof_contract=description['roof'],material_contract=dict(profile='texture-free source-palette architectural clay',generic_texture_fallback=False),
        identity_contract=dict(owner='family-specific constructed silhouette, openings, roof and architectural relief',bitmap_stickers='not used in architectural clay'),
        programme_contract=description['programme'],contact_contract=contacts,camera_roster=roster,mandatory_review_views=[x['name'] for x in roster])
