"""Two bounded source-led neighborhood building prototypes. Run inside Blender.

Low-level mesh/opening utilities: geometry_core.py, copied unchanged from the
museum v004 review package. Every building composition below is newly authored.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

import bpy
from mathutils import Vector
sys.path.insert(0, str(Path(__file__).parent))
import geometry_core as C
import refinements as R
import walking as W
C.METHOD='RLASM v6.1 prototype'

ROOT = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[2]
PALETTE = {
    'wall':(.43,.17,.10), 'buff':(.68,.53,.32), 'trim':(.075,.087,.085),
    'stone':(.62,.59,.51), 'roof':(.40,.43,.44), 'hardware':(.09,.105,.10),
    'glass':(.58,.69,.70), 'timber':(.40,.24,.12), 'interior':(.72,.68,.57),
    'floor':(.48,.40,.28), 'furniture':(.29,.36,.33), 'soil':(.13,.105,.065),
    'plant':(.16,.24,.095), 'paving':(.49,.49,.45), 'sport':(.48,.33,.18)
}

def write(p,data):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

def texture_material(role,filename):
    m=C.MATS[role];m.name='SOURCE_'+role.upper();m['texture_free']=False
    m['source_conditioned']=True;m['tile_size_m']=2.4
    image=bpy.data.images.load(str(ROOT/'materials'/filename));image.pack()
    node=m.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;node.extension='REPEAT'
    m.node_tree.links.new(node.outputs['Color'],m.node_tree.nodes['Principled BSDF'].inputs['Base Color'])

def uv_all():
    for o in C.objects():
        o['representation_kind']='textured_architectural_prototype'
        uv=o.data.uv_layers.new(name='Metric masonry axes')
        for p in o.data.polygons:
            n=p.normal;axis=max(range(3),key=lambda i:abs(n[i]))
            for li in p.loop_indices:
                co=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
                uv.data[li].uv=((co.y if axis==0 else co.x)/2.4,(co.y if axis==2 else co.z)/2.4)

def hole(ident,u,z,w,h):return dict(id=ident,u=u,z=z,w=w,h=h)

def elevation(face,length,height,holes,bands=None,lintels=False):
    bands=bands or [(0,height,'wall')]
    for z0,z1,role in bands:face.wall(face.label+' carrier '+role,-length/2,length/2,z0,z1,.34,role,holes)
    for h in holes:
        face.window(h['id'],h['u'],h['z'],h['w'],h['h'],h.get('cols',2),h.get('rows',1),
                    'trim',.18,.045,sill=False,depth=.34,kind=h.get('kind','window'))
        if h.get('kind')!='door':
            face.part(h['id']+' stone sill',h['u'],.015,h['z']-.045,h['w']+.13,.42,.09,'stone','sills')
            if lintels:face.part(h['id']+' stone lintel',h['u'],.02,h['z']+h['h']+.13,h['w']+.28,.40,.26,'stone','lintels')

def parapet(x0,x1,y0,y1,z,role='wall'):
    for x in (x0+.14,x1-.14):
        C.box('side parapet',(x,(y0+y1)/2,z-.19),(.28,y1-y0,.38),role)
        C.box('side parapet coping',(x,(y0+y1)/2,z+.025),(.37,y1-y0+.10,.07),'roof')
    for y in (y0+.14,y1-.14):
        C.box('end parapet',((x0+x1)/2,y,z-.19),(x1-x0-.56,.28,.38),role)
        C.box('end parapet coping',((x0+x1)/2,y,z+.025),(x1-x0-.55,.37,.07),'roof')
    C.box('closed membrane roof',((x0+x1)/2,(y0+y1)/2,z-.47),(x1-x0-.35,y1-y0-.35,.20),'roof')

def plantbed(x,y,w,d):
    C.box('raised planter',(x,y,.18),(w,d,.36),'stone','site')
    C.box('contained soil',(x,y,.355),(w-.12,d-.12,.02),'soil','site',0)
    for i in range(max(3,round(w*2))):
        px=x-w*.43+(i+.5)*w*.86/max(3,round(w*2))
        for j in (-1,1):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(px,y+j*d*.20,.57))
            o=bpy.context.object;o.name='low planting';o.scale=(.24,.23,.30+.07*math.sin(i));o.data.materials.append(C.MATS['plant']);C.tag(o,'plant','site')
            bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)

def bench(x,y):
    for i in range(4):C.box('bench seat slat',(x,y+(i-1.5)*.10,.47),(1.8,.085,.065),'timber','site')
    for xx in (x-.65,x+.65):
        C.box('bench leg',(xx,y,.235),(.075,.36,.47),'hardware','site')
    for z in (.70,.84):C.box('bench back slat',(x,y+.23,z),(1.8,.07,.11),'timber','site')
    for xx in (x-.65,x+.65):C.box('bench back support',(xx,y+.24,.68),(.055,.055,.50),'hardware','site')

def bikehoop(x,y):
    C.rod('bike rack left',(x-.30,y,.045),(x-.30,y,.78),.028)
    C.rod('bike rack right',(x+.30,y,.045),(x+.30,y,.78),.028)
    C.rod('bike rack top',(x-.30,y,.78),(x+.30,y,.78),.028)

def desk(x,y,z,school=True):
    w=.95 if school else 1.25;d=.60
    C.box('desk top',(x,y,z+.75),(w,d,.055),'timber','furniture')
    for dx in (-w*.40,w*.40):
        for dy in (-.22,.22):C.box('desk leg',(x+dx,y+dy,z+.37),(.035,.035,.74),'hardware','furniture',0)
    C.box('chair seat',(x,y+.58,z+.43),(.42,.42,.045),'furniture','furniture')
    C.box('chair back',(x,y+.77,z+.69),(.42,.035,.44),'furniture','furniture')
    for dx in (-.16,.16):
        for dy in (.43,.72):C.box('chair leg',(x+dx,y+dy,z+.21),(.025,.025,.42),'hardware','furniture',0)

def sofa(x,y,z):
    C.box('sofa seat',(x,y,z+.38),(2.0,.83,.28),'furniture','interior')
    C.box('sofa back',(x,y+.40,z+.69),(2.0,.16,.62),'furniture','interior')
    for dx in (-.97,.97):C.box('sofa arm',(x+dx,y,z+.57),(.18,.85,.48),'furniture','interior')
    for dx in (-.8,.8):
        for dy in (-.3,.3):C.box('sofa foot',(x+dx,y+dy,z+.12),(.06,.06,.24),'timber','interior',0)
    C.box('coffee table',(x,y-1.1,z+.42),(1.1,.58,.055),'timber','interior')
    for dx in (-.4,.4):C.box('coffee table legs',(x+dx,y-1.1,z+.21),(.05,.40,.42),'hardware','interior')

def stair(x,y,z,rise,width=1.25):
    # Two real flights around a central well with a shared midlanding.
    count=11;run=2.75;r=rise/(count*2)
    for i in range(count):
        zz=z+(i+1)*r
        C.box('ascending stair tread',(x-width*.55,y+i*run/count,zz-r/2),(width,run/count+.02,r),'stone','circulation',0)
        zz2=z+rise/2+(i+1)*r
        C.box('return stair tread',(x+width*.55,y+(count-1-i)*run/count,zz2-r/2),(width,run/count+.02,r),'stone','circulation',0)
    C.box('half landing',(x,y+run+.40,z+rise/2-.09),(width*2.1,1.05,.18),'stone','circulation')
    for side in (-1,1):
        cx=x+side*width*.55
        za=z if side<0 else z+rise
        zb=z+rise/2
        C.prism('continuous stair waist',[(y-.13,za-.12),(y+run,zb-.12),(y+run,zb+.04),(y-.13,za+.04)],'x',cx-width/2,cx+width/2,'stone','circulation')
        xx=x+side*width*1.10
        C.beam('sloping handrail',(xx,y-.1,za+1),(xx,y+run,zb+1),.045,role='hardware')
        for j in range(6):
            zz=za+(zb-za)*j/5
            C.rod('stair guard',(xx,y+j*run/5,zz),(xx,y+j*run/5,zz+1),.018)

def roof_unit(x,y,z,w=3,d=2):
    C.box('equipment curb',(x,y,z+.09),(w,d,.18),'roof','roof_equipment')
    C.box('mechanical unit',(x,y,z+.52),(w-.25,d-.25,.85),'roof','roof_equipment')
    for i in range(8):
        zz=z+.16+i*.10
        for yy in (y-d/2-.03,y+d/2+.03):C.box('equipment louver',(x,yy,zz),(w,.05,.045),'hardware','roof_equipment',0)

def school():
    W,D,H=28,22,11.4;floor=.14
    C.box('site base',(0,0,.02),(32,30,.04),'paving','site',0)
    front=C.Face((-5,-11,0),(1,0,0),(0,1,0),'front classroom')
    holes=[]
    for level in range(3):
        for i,u in enumerate([-7.2,-3.7,-.2,3.3,6.8]):
            if level==0 and i>1:continue
            holes.append(dict(hole(f'classroom front {level}-{i}',u,level*3.8+.92,2.55,2.10),cols=3,rows=2))
    # The entrance aperture is full wall depth, glazed plane is 1.3 m behind it.
    holes.append(hole('entrance recess',3.1,.14,10.4,3.20))
    front.wall('front complete carrier',-9,9,0,H,.34,'wall',holes)
    for h in holes[:-1]:
        front.window(h['id'],h['u'],h['z'],h['w'],h['h'],3,2,'trim',.18,.045,sill=False,depth=.34)
        front.part(h['id']+' lintel',h['u'],.02,h['z']+h['h']+.13,h['w']+.28,.40,.26,'stone')
        front.part(h['id']+' sill',h['u'],.02,h['z']-.04,h['w']+.15,.42,.08,'stone')
    # Deep returns enclose entry; primary aperture is not duplicated in audit.
    for u in (-2.1,8.3):front.part('entrance return',u,.70,1.75,.30,1.42,3.22,'wall')
    front.part('entrance ceiling',3.1,.60,3.25,10.4,1.8,.20,'timber')
    front.part('entrance canopy edge',3.1,-.27,3.43,10.65,.74,.24,'roof')
    lobby=C.Face((-1.9,-9.7,0),(1,0,0),(0,1,0),'recessed lobby')
    lobby.window('lobby glazing',0,.14,10.10,2.99,8,2,'trim',.10,sill=False)
    for u in (-.72,.72):lobby.part('door pull',u,.015,1.35,.035,.09,.56,'hardware')
    for side,x,t,n in [('left',-14,(0,-1,0),(1,0,0)),('right upper',4,(0,1,0),(-1,0,0))]:
        f=C.Face((x,0,0),t,n,side)
        hs=[]
        for level in range(3):
            if side=='right upper' and level<2:continue
            for j,u in enumerate([-8,-3,2,7]):hs.append(dict(hole(f'{side} {level}-{j}',u,level*3.8+1,2.5,2),cols=3,rows=2))
        elevation(f,22,H,hs,lintels=True)
    back=C.Face((-5,11,0),(-1,0,0),(0,-1,0),'rear classroom')
    hs=[dict(hole(f'rear {level}-{j}',u,level*3.8+1,2.5,2),cols=3,rows=2) for level in range(3) for j,u in enumerate([-7,-3.5,0,3.5,7])]
    hs=[h for h in hs if not(h['z']<2 and h['u']==0)]+[dict(hole('rear exit',0,.14,1.8,2.4),kind='door')]
    elevation(back,18,H,hs,lintels=True)
    for level in range(3):
        z=level*3.8+.14
        slab=C.box('classroom floor slab',(-5,0,z-.07),(17.4,21.4,.14),'floor','floors',0)
        if level:C.cut_box(slab,'stairwell floor opening',(-5,6,z),(3.1,4.6,.6))
        # Front classrooms share a rear corridor; partitions terminate at real doors.
        if level:
            partition_h=3.0 if level==2 else 3.4
            for x in [-10.45,-6.95,-3.45,.05]:C.box('classroom partition',(x,-6.8,z+partition_h/2),(.12,7.8,partition_h),'interior','rooms',0)
            C.box('stair upper landing',(-5,3.65,z-.07),(3.1,1.2,.14),'floor','circulation')
            for x in (-6.46,-3.54):C.railing('stairwell side guard',(x,4.25,z),(x,8.28,z),height=1.02,spacing=.18)
            for x in [-12.2,-8.7,-5.2,-1.7,1.8]:
                for yy in [-8.5,-6.7,-4.9]:desk(x,yy,z)
                C.box('classroom teaching board',(x,-3.0,z+1.75),(2.45,.05,1.1),'furniture','rooms')
        else:
            for x in [-12.2,-8.7]:
                for yy in [-8,-6]:desk(x,yy,z)
        if level<2:stair(-5,4.2,z,3.8)
        C.qa_room_light('classroom interior',(-5,-6,z+3.2),900,10)
    parapet(-14,4,-11,11,H)
    # Gym's front band and other high windows share one measured datum.
    gf=C.Face((9,-11,0),(1,0,0),(0,1,0),'gym front')
    elevation(gf,10,8,[dict(hole('gym front clerestory',0,6.75,9.3,.95),cols=10)])
    gr=C.Face((14,0,0),(0,1,0),(-1,0,0),'gym right')
    gh=[dict(hole('gym side clerestory',0,6.75,20.5,.95),cols=16),dict(hole('gym side exit',7.5,.14,1.8,2.4),kind='door')]
    elevation(gr,22,8,gh)
    gb=C.Face((9,11,0),(-1,0,0),(0,-1,0),'gym rear')
    elevation(gb,10,8,[dict(hole('gym rear clerestory',0,6.75,9.3,.95),cols=10),dict(hole('gym rear exit',-2.5,.14,1.8,2.4),kind='door')])
    C.box('gym floor',(9,0,.09),(9.3,21.3,.18),'sport','gym')
    for yy in (-7.5,7.5):
        C.box('gym backboard',(9,yy,3.1),(1.7,.08,1.05),'interior','gym')
        C.beam('backboard support',(9,yy,3.5),(9,yy+(-3.3 if yy<0 else 3.3),4.8),.075,role='hardware')
    for xx in (5.1,12.9):C.box('gym court sideline',(xx,0,.187),(.045,17,.012),'interior','gym',0)
    for yy in (-8.5,0,8.5):C.box('gym court crossline',(9,yy,.187),(7.8,.045,.012),'interior','gym',0)
    parapet(4,14,-11,11,8)
    roof_unit(-5,2,11.03,4,2.4);roof_unit(9,2,7.63,3,2)
    C.qa_room_light('gym occupation',(9,0,6.2),1100,8)
    plantbed(-10,-12.5,6,1.4);plantbed(8,-12.5,9,1.4)
    bench(-5.8,-13.5);bench(4,-13.5)
    for x in [-12,-10.8,-9.6]:bikehoop(x,-14)
    return W,D,H

def fourplex():
    W,D,H=16,14,7.3
    C.box('site base',(0,0,.02),(20,22,.04),'paving','site',0)
    front=C.Face((0,-7,0),(1,0,0),(0,1,0),'front')
    hs=[]
    for level in range(2):
        for i,(u,w) in enumerate([(-6.5,.95),(-3.7,3.0),(3.7,3.0),(6.5,.95)]):
            hs.append(dict(hole(f'front apartment {level}-{i}',u,.92+3.45*level,w,1.95),cols=3 if w>2 else 1))
    hs+=[hole('central entrance recess',0,.12,2.15,7.0)]
    for z0,z1,role in [(0,3.45,'wall'),(3.45,H,'buff')]:front.wall('front '+role,-8,8,z0,z1,.34,role,hs)
    for h in hs[:-1]:
        front.window(h['id'],h['u'],h['z'],h['w'],h['h'],h['cols'],1,'trim',.18,sill=False,curtain=True,depth=.34)
        front.part(h['id']+' sill',h['u'],.02,h['z']-.045,h['w']+.11,.40,.09,'stone')
    for u in (-1.07,1.07):front.part('central brick return',u,.32,3.62,.20,.65,7.24,'wall')
    front.part('central entrance canopy',0,-.08,2.90,2.20,.95,.16,'trim')
    front.part('stair head spandrel',0,.45,6.85,1.94,.22,.70,'trim')
    lobby=C.Face((0,-6.5,0),(1,0,0),(0,1,0),'central stair')
    lobby.window('front entry door',0,.14,1.88,2.64,2,1,'trim',.10,sill=False,kind='door')
    lobby.window('stair window',0,3.12,1.88,3.23,2,1,'trim',.10,sill=False)
    for side,x,t,n in [('right',8,(0,1,0),(-1,0,0)),('left',-8,(0,-1,0),(1,0,0))]:
        f=C.Face((x,0,0),t,n,side)
        sh=[hole(f'{side} {level}-{j}',u,1+level*3.45,1.1,1.8) for level in range(2) for j,u in enumerate([-4.5,0,4.5])]
        elevation(f,14,H,sh,[(0,3.45,'wall'),(3.45,H,'buff')])
    back=C.Face((0,7,0),(-1,0,0),(0,-1,0),'rear')
    bh=[hole(f'rear {level}-{j}',u,1+level*3.45,1.9,1.8) for level in range(2) for j,u in enumerate([-5.65,-3.2,3.2,5.65])]
    bh += [dict(hole('rear shared door',0,.14,1.4,2.5),kind='door'),hole('rear stair window',0,4.4,1.4,1.8)]
    elevation(back,16,H,bh,[(0,3.45,'wall'),(3.45,H,'buff')])
    for level in range(2):
        z=.14+3.45*level
        slab=C.box('apartment floor',(0,0,z-.07),(15.35,13.35,.14),'floor','floors',0)
        if level:C.cut_box(slab,'stairwell cut',(0,-2.9,z),(2.45,4.6,.55))
        # Four physically separated apartment zones; common middle corridor.
        for s in (-1,1):
            x=s*1.90
            f=C.Face((x,0,0),(0,1,0),(-s,0,0),'apartment partition')
            opening=dict(hole(f'unit door {level}-{s}',1,z,1.0,2.2),kind='door')
            f.wall('apartment separating wall',-6.6,6.6,z,z+3.25,.13,'interior',[opening])
            f.door(opening['id'],1,z,1,2.2,'timber')
            # Furnished living room at front, sleeping area at rear.
            sofa(s*4.4,-4.2,z)
            desk(s*5.4,0,z,False)
            C.box('kitchen base',(s*6.8,2.1,z+.44),(1.1,2.3,.88),'interior','interior')
            C.box('kitchen worktop',(s*6.8,2.1,z+.90),(1.14,2.3,.045),'stone','interior')
            C.box('bed base',(s*4.7,5.45,z+.20),(1.8,2,.40),'timber','interior')
            C.box('bed mattress',(s*4.7,5.45,z+.49),(1.8,2,.19),'interior','interior')
            C.qa_room_light('apartment occupied room',(s*4.5,-3,z+2.9),230,4)
    stair(0,-4.9,.14,3.45,1.05)
    # Upper landing connects the return flight to the corridor and apartment doors.
    C.box('upper landing',(0,-5.25,3.51),(2.5,.85,.16),'floor','circulation')
    for x in (-1.20,1.20):C.railing('upper stairwell guard',(x,-4.825,3.59),(x,-.6,3.59),height=1.02,spacing=.18)
    parapet(-8,8,-7,7,H,'buff')
    for x,y in [(-3,2),(2,4),(3,-3)]:
        C.rod('roof vent',(x,y,6.94),(x,y,7.40),.085,'roof','roof_equipment')
        C.box('vent cap',(x,y,7.42),(.25,.25,.06),'roof','roof_equipment')
    plantbed(-4.7,-8.8,5.8,1.8);plantbed(4.7,-8.8,5.8,1.8)
    for x in [2.5,3.5]:bikehoop(x,-10.25)
    bench(-5,9)
    return W,D,H

def cameras(kind):
    school_mode=kind=='school';w=28 if school_mode else 16;d=22 if school_mode else 14;h=11.4 if school_mode else 7.3
    target=(0,0,h*.42)
    result=[]
    for name,loc in [('front',(0,-d*2.5,h*.62)),('front_corner',(w*1.6,-d*1.9,h*1.5)),('aerial',(w*1.3,-d*1.4,h*3.5)),('left_side',(-w*2.2,0,h*.7)),('right_side',(w*2.2,0,h*.7)),('rear',(0,d*2.8,h*.7)),('rear_side',(-w*1.6,d*1.9,h*1.5))]:
        result.append(dict(name=name,location=loc,target=target,whole=True,lens=52))
    tx=-8.7 if school_mode else -3.7;fy=-11 if school_mode else -7
    result.extend([
        dict(name='facade_close',location=(tx-3,fy-10,h*.68),target=(tx,fy,h*.60),whole=False,lens=48),
        dict(name='architecture_close',location=(4 if school_mode else 3,fy-8,4.5),target=(-1 if school_mode else 0,fy+.5,1.9),whole=False,lens=42),
        dict(name='glass_close',location=(tx-1.7,fy-4.4,2.0),target=(tx,fy+.3,1.9),whole=False,lens=48),
        dict(name='roof_contact',location=(w*.75,-d*.65,h*1.7),target=(w*.15,-d*.3,h-.4),whole=False,lens=44),
        dict(name='program_interior',location=(9,-7,3.5) if school_mode else (-6,-5,1.8),target=(9,4,2) if school_mode else (-3,-2,1.2),whole=False,lens=24)
    ])
    return result + R.extra_cameras(kind)

def main():
    global ROOT,REPO
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=['school','fourplex'],required=True);p.add_argument('--version',default='v001');p.add_argument('--dry-run',action='store_true');p.add_argument('--resolution',type=int,default=1280);p.add_argument('--output-root',type=Path,required=True);p.add_argument('--reference-repo',type=Path,default=REPO)
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);ROOT=a.output_root.resolve();REPO=a.reference_repo.resolve();kind=a.kind;candidate=kind+'-'+a.version;out=ROOT/candidate
    aid='neighborhood_elementary_school' if kind=='school' else 'neighborhood_fourplex'
    vid='school_compact_urban' if kind=='school' else 'fourplex_stacked_brick'
    ref=REPO/'frontend/public/archetypes/buildings'/aid.replace('_','-')
    sources=[]
    for role,name,authority in [('front','variant_0.png','original catalogue design'),('oblique','variant_0_oblique.png','generated continuation; unseen sides inferred'),('topology','variant_0_roof-study.png','generated high roof study; not true nadir and not metric authority')]:
        q=ref/name;assert q.is_file();sources.append(dict(archetype_id=aid,variant_id=vid,role=role,path='sources/'+name,original_path=str(q),bytes=q.stat().st_size,sha256=C.digest(q),authority=authority))
    camspec=cameras(kind)
    if a.dry_run:print(json.dumps(dict(candidate=candidate,sources=sources,cameras=len(camspec),geometry_written=False)));return
    out.mkdir(parents=True,exist_ok=False)
    for name in ['sources','scripts','textures','renders','review','evidence','boards']:(out/name).mkdir()
    for s in sources:shutil.copy2(s['original_path'],out/s['path'])
    for f in [Path(__file__),Path(C.__file__),Path(R.__file__),Path(W.__file__)]:shutil.copy2(f,out/'scripts'/f.name)
    shutil.copy2(ROOT/'reference-generation.json',out/'sources/reference-generation.json')
    for name in ['red_brick.png','buff_brick.png']:shutil.copy2(ROOT/'materials'/name,out/'textures'/name)
    manifest=dict(candidate=candidate,method='RLASM v6.1 prototype',archetype_id=aid,variant_id=vid,state='building',keeper_claimed=False,
                  source_contract={'sources':sources,'front_is_primary':True,'derived_views_are_design_assumptions':True},
                  mandatory_review_views=[s['name'] for s in camspec],camera_roster=camspec,
                  measurement_contract={'units':'metres, inferred design scale','dimensions_m':{'width':28 if kind=='school' else 16,'depth':22 if kind=='school' else 14,'height':11.4 if kind=='school' else 7.3},
                  'front_ratios':'School main block 18/28 width, gym10/28; 5 classroom window bays,3 storeys. Fourplex2 storeys,2 large and2 narrow windows per floor with central stair.',
                  'assumptions':['Rear and interior layouts are inferred; no surveyed plan exists.','School front pixels override original 48m-wide prose.','Roof-study image is high oblique despite generation requesting nadir; only topology is used.','No autonomous scaling or runtime catalogue promotion.']})
    write(out/'prework-manifest.json',manifest)
    cams=C.setup(PALETTE,camspec,a.resolution)
    bpy.context.scene.cycles.samples=24
    texture_material('wall','red_brick.png');texture_material('buff','buff_brick.png')
    (school if kind=='school' else fourplex)()
    if kind=='school':R.school_interiors()
    else:R.fourplex_interiors()
    R.circulation_corrections(kind)
    network=W.attach(kind)
    write(out/'evidence/walking-network.json',network)
    uv_all();bpy.context.view_layer.update()
    for o in C.objects():o['archetype_id']=aid;o['variant_id']=vid
    authored=C.objects();original=C.bounds(authored);assert abs(original[0][2])<.001,original
    aperture=C.aperture_audit();write(out/'evidence/carrier-aperture-audit.json',aperture)
    for s in camspec:
        if s['whole']:C.fit(cams[s['name']],s['target'])
    bpy.context.scene.camera=cams['front_corner']
    bpy.ops.wm.save_as_mainfile(filepath=str(out/(candidate+'.blend')))
    # Merge by material for practical runtime draw calls, preserving UVs and extras.
    for role in C.MATS:
        group=[o for o in C.objects() if o.get('cityprompt_semantic_role')==role]
        if not group:continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in group:o.select_set(True)
        bpy.context.view_layer.objects.active=group[0]
        if len(group)>1:bpy.ops.object.join()
        bpy.context.object.name=role
    W.embed(network)
    glb=out/(candidate+'.glb');bpy.ops.object.select_all(action='DESELECT')
    for o in C.objects():o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_materials='EXPORT',export_extras=True,export_cameras=False,export_lights=False,export_yup=True,export_texcoords=True,export_normals=True)
    payload=C.glb_json(glb)
    for o in list(C.objects()):bpy.data.objects.remove(o,do_unlink=True)
    old=set(bpy.context.scene.objects);bpy.ops.import_scene.gltf(filepath=str(glb))
    imported=[o for o in bpy.context.scene.objects if o not in old and o.type=='MESH']
    for o in imported:o['rlasm_building_object']=True
    bpy.context.view_layer.update();actual=C.bounds(imported)
    delta=max(abs(actual[i][j]-original[i][j]) for i in range(2) for j in range(3));assert delta<.001
    for s in camspec:
        bpy.context.scene.camera=cams[s['name']]
        if s['whole']:C.fit(cams[s['name']],s['target'])
        bpy.context.scene.render.filepath=str(out/'renders'/(s['name']+'.png'))
        bpy.ops.render.render(write_still=True);print('RENDER_COMPLETE '+s['name'],flush=True)
    report=dict(candidate=candidate,status='build_valid',keeper_claimed=False,runtime_activated=False,generic_fallback_count=0,
                materials_scope='Source-conditioned brick base-color maps; other surfaces use source-palette materials. Full keeper PBR certification not claimed.',
                native_bounds_m=actual,max_roundtrip_delta_m=delta,glb={'path':glb.name,'bytes':glb.stat().st_size,'sha256':C.digest(glb),'meshes':len(payload['meshes']),'textures':len(payload.get('textures',[])),**C.metrics(imported)},
                opening_count=len(C.OPENINGS),carrier_aperture_audit=aperture['status'],openings=C.OPENINGS,
                render_source='exported GLB reimport, no material or geometry substitution',independent_review='pending')
    write(out/'evidence/builder-evidence.json',report);write(out/'build-report.json',report)
    print('BUILD_COMPLETE '+json.dumps({'candidate':candidate,'glb':report['glb'],'apertures':aperture['status']}),flush=True)

if __name__=='__main__':
    R.install(sys.modules[__name__])
    main()
