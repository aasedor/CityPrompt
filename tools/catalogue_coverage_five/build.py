"""Five exact original coverage studies: source-locked RLASM architectural clay."""
import argparse
import math
from pathlib import Path
import shutil
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
sys.path.append(str(HERE.parent/'catalogue_services_batch'))
import clay_core as C
from plan import SPECS,source_entry
from assemblies import hole,faces,glazing,steps,sofa,bed,flat_roof,desk,straight_stair,seated_guard,bathroom,vertical_cladding,rotate_new,shrub,small_tree,garden_chair

PALETTE=dict(wall=(.40,.43,.31),trim=(.82,.79,.67),roof=(.25,.27,.26),foundation=(.28,.29,.27),glass=(.34,.40,.40),hardware=(.075,.08,.08),interior=(.75,.72,.64),floor=(.49,.36,.22),timber=(.52,.34,.18),pale=(.66,.62,.52),planting=(.22,.29,.13),blue=(.12,.25,.28),brick=(.44,.23,.13),joint=(.17,.18,.16))
PALETTES={'horizon':dict(wall=(.76,.73,.66),trim=(.075,.085,.09),roof=(.14,.16,.18),timber=(.56,.34,.15),foundation=(.16,.17,.18)),
 'craftsman':dict(wall=(.33,.40,.44),trim=(.80,.77,.67),roof=(.20,.24,.28),timber=(.51,.34,.18),brick=(.43,.24,.16),foundation=(.35,.32,.27)),
 'mews':dict(wall=(.54,.37,.23),trim=(.09,.11,.12),roof=(.15,.18,.21),timber=(.54,.37,.23),brick=(.78,.74,.64),floor=(.59,.53,.45),pale=(.70,.68,.61),planting=(.27,.34,.17),joint=(.65,.62,.55)),
 'office':dict(wall=(.45,.24,.14),trim=(.095,.11,.12),roof=(.23,.25,.25),timber=(.57,.37,.17),brick=(.45,.24,.14),floor=(.62,.58,.49),pale=(.69,.67,.59),joint=(.36,.25,.19))}


def horizontal_cladding(f,span,z0,z1,holes,step=.22,role='wall',trim_clearance=0):
    for i in range(math.ceil((z1-z0)/step)):
        z=min(z1-.01,z0+(i+1)*step)
        spans=[(-span/2+trim_clearance,span/2-trim_clearance)]
        for h in holes:
            if h['z']-.018-trim_clearance<z<h['z']+h['h']+.018+trim_clearance:
                spans=[s for a,b in spans for s in ((a,min(b,h['u']-h['w']/2-trim_clearance)),(max(a,h['u']+h['w']/2+trim_clearance),b)) if s[1]-s[0]>.001]
        for a,b in spans:f.part('Clapboard shadow lip',(a+b)/2,-.009,z,b-a,.025,.018,role,'cladding',0)


def window(f,h,cols=1,rows=2,frame='trim'):
    f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=cols,rows=rows,frame=frame,depth=.23)
    for sign in (-1,1):f.part('Window casing',h['u']+sign*(h['w']/2+.05),-.025,h['z']+h['h']/2,.10,.07,h['h']+.13,frame,'window trim')
    for z in (h['z']-.07,h['z']+h['h']+.06):f.part('Window head sill casing',h['u'],-.025,z,h['w']+.20,.08,.12,frame,'window trim')


def masonry_courses(f,span,z0,z1,holes,step=.105,head_joints=False):
    for i in range(1,math.ceil((z1-z0)/step)):
        z=z0+i*step;spans=[(-span/2+.015,span/2-.015)]
        for h in holes:
            if h['z']-.025<z<h['z']+h['h']+.025:
                spans=[s for a,b in spans for s in ((a,min(b,h['u']-h['w']/2-.025)),(max(a,h['u']+h['w']/2+.025),b)) if s[1]-s[0]>.001]
        for a,b in spans:f.part('Shallow mortar bed joint',(a+b)/2,-.003,z,b-a,.006,.008,'joint','masonry joints',0)
    if head_joints:
        vertices=[];polygons=[]
        for row in range(math.ceil((z1-z0)/step)):
            a=z0+row*step+.004;b=min(z1,a+step-.008)
            if b<=a:continue
            for column in range(math.ceil(span/.25)+1):
                u=-span/2+column*.25+(row%2)*.125
                if not -span/2+.018<u<span/2-.018:continue
                if any(h['u']-h['w']/2-.03<u<h['u']+h['w']/2+.03 and a<h['z']+h['h']+.025 and b>h['z']-.025 for h in holes):continue
                offset=len(vertices)
                vertices.extend(f.p(u+du*.004,-.003+dd*.003,(a+b)/2+dz*(b-a)/2) for dz in (-1,1) for du,dd in [(-1,-1),(1,-1),(1,1),(-1,1)])
                polygons.extend(tuple(offset+i for i in face) for face in C.BOX_FACES)
        if vertices:C.mesh('Staggered brick mortar head joints',vertices,polygons,'joint','masonry joints',0)


def chassis(w,d,fluted=True):
    for y in (-d*.29,d*.29):
        for z,width,height in ((.16,.16,.045),(.245,.035,.14),(.33,.16,.045)):
            C.box('Permanent chassis beam',(0,y,z),(w-.3,width,height),'hardware','permanent chassis')
        for x in (-w*.43,-w*.21,0,w*.21,w*.43):C.box('Transport chassis bearing',(x,y,.06875),(.32,.32,.1375),'foundation','chassis bearings')
    for i in range(math.ceil(w)):
        C.box('Floor cross bearer',(-w/2+.4+i,0,.345),(.07,d-.2,.09),'hardware','permanent chassis')
    C.box('Raised insulated floor',(0,0,.415),(w,d,.07),'floor','floor')
    for f,span in zip(faces(w,d),[w,d,w,d]):
        f.part('Demountable skirt',0,.015,.21,span,.08,.42,'foundation','skirt')
        for i in range(math.ceil(span/.16) if fluted else 0):
            f.part('Skirt fluting',-span/2+(i+.5)*span/math.ceil(span/.16),-.03,.21,.018,.025,.42,'foundation','skirt',0)


def gable(name,cx,cy,w,d,eave,ridge,axis='x',role='roof',seams=False,gable_role='wall',fascia_role='trim',over=.20,flush_gable=False):
    # Build in a local system with ridge along x, then optionally rotate the assembly.
    before=set(C.objects())
    x0,x1=-w/2-over,w/2+over
    for yy in (-d/2-over,d/2+over):
        C.solid_surface(name+' roof plane',[(x0,0,ridge),(x1,0,ridge),(x1,yy,eave),(x0,yy,eave)],.14,role,name)
        if seams:
            for i in range(math.ceil(w/.42)+1):
                x=x0+(x1-x0)*i/math.ceil(w/.42)
                C.beam(name+' standing seam',(x,0,ridge+.02),(x,yy,eave+.02),.022,.025,role,name)
        C.beam(name+' seated eave fascia',(x0,yy,eave-.075),(x1,yy,eave-.075),.12,.14,fascia_role,name)
    C.beam(name+' ridge cap',(x0,0,ridge+.01),(x1,0,ridge+.01),.12,.08,role,name)
    inneredge=ridge-(ridge-eave)*(d/2)/(d/2+over)-.12
    for xx in (-w/2,w/2):
        if flush_gable:
            C.prism(name+' closed gable',[(-d/2,eave-.14),(d/2,eave-.14),(0,ridge-.14)],'x',xx if xx<0 else xx-.23,xx+.23 if xx<0 else xx,gable_role,name)
        else:C.prism(name+' closed gable',[(-d/2,eave-.15),(d/2,eave-.15),(d/2,inneredge),(0,ridge-.13),(-d/2,inneredge)],'x',xx-.11,xx+.11,gable_role,name)
        if name.startswith('Maple'):
            for i in range(1,math.ceil((ridge-eave)/.22)):
                z=eave+i*.22
                half=min(d/2,(d/2+over)*(ridge-.14-z)/(ridge-eave))
                if half>.01:C.box('Gable clapboard lip',(xx+math.copysign(.119,xx),0,z),(.022,half*2,.018),'wall','gable cladding',0)
        for yy in (-d/2-over,d/2+over):C.beam(name+' rake fascia',(xx+(over if xx>0 else -over),0,ridge-.06),(xx+(over if xx>0 else -over),yy,eave-.06),.13,.13,fascia_role,name)
    for obj in set(C.objects())-before:
        if axis=='y':obj.rotation_euler.z=math.pi/2
        obj.location.x+=cx;obj.location.y+=cy
    C.bpy.context.view_layer.update()


def kitchen(x,y,z,w=3.2):
    C.box('Kitchen cupboards',(x,y,z+.45),(w,.65,.9),'timber','kitchen')
    C.box('Kitchen counter',(x,y,z+.925),(w+.08,.70,.05),'pale','kitchen')
    C.box('Kitchen sink',(x+.5,y,z+.956),(.62,.42,.012),'hardware','kitchen')
    C.rod('Kitchen tap',(x+.5,y+.22,z+.94),(x+.5,y+.22,z+1.23),.018,'hardware','kitchen')
    C.rod('Kitchen tap spout',(x+.5,y+.22,z+1.23),(x+.5,y,z+1.23),.018,'hardware','kitchen')
    C.box('Refrigerator',(x-w/2-.42,y,z+.95),(.75,.72,1.9),'pale','kitchen')


def maple():
    w,d,floor,eave,ridge=14,4.8,.45,3.25,4.50
    chassis(w,d);ff=faces(w,d)
    front=[hole('Living pair',-4.8,1.05,1.70,1.45),hole('Kitchen sash',-1.9,1.25,.86,1.26),hole('Main entrance',0,floor,1.04,2.18),hole('Bedroom pair',3.0,1.05,1.8,1.45),hole('Bedroom sash',5.6,1.25,.90,1.26)]
    schedules=[front,[hole('Right end sash',0,1.15,1.00,1.37)],[hole('Rear bedroom',-4.5,1.25,1.15,1.25),hole('Rear bath',-.4,1.70,.75,.6),hole('Rear living',4.7,1.15,1.6,1.4)],[hole('Left end sash',0,1.15,1.05,1.37)]]
    for f,span,hs in zip(ff,[w,d,w,d],schedules):
        f.wall(f.label+' complete carrier',-span/2,span/2,floor,eave,depth=.23,holes=hs)
        for h in hs:
            if h['id']=='Main entrance':
                f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='trim',panels=2)
                # Real glazed top light, cut through the opaque leaf rather than painted glass.
                leaf=next(o for o in C.objects() if o.name.startswith('Main entrance recessed leaf'))
                f.cut(leaf,'Door top-light aperture',0,2.03,.65,.43,.23)
                for obj in list(C.objects()):
                    if obj.name.startswith('Main entrance door panel') and max(v.co.z for v in obj.data.vertices)>2.03:
                        C.cut_box(obj,'Door panel light opening',(0,-2.2,2.245),(.65,.8,.43))
                f.window('Entrance top light',0,2.03,.65,.43,cols=2,rows=2,frame='trim',sill=False,depth=.23)
            else:
                cols=2 if 'pair' in h['id'] else 1
                window(f,h,cols=cols)
                for c in range(cols):
                    u=h['u']-h['w']/2+h['w']*(c+.5)/cols
                    f.part('Divided upper sash vertical',u,.118,h['z']+h['h']*.75,.021,.035,h['h']*.5-.07,'trim','upper sash')
                f.part('Divided upper sash horizontal',h['u'],.116,h['z']+h['h']*.75,h['w']-.13,.035,.021,'trim','upper sash')
        horizontal_cladding(f,span,floor,eave,hs)
        for u in (-span/2+.05,span/2-.05):f.part('Corner board',u,-.027,(floor+eave)/2,.1,.055,eave-floor,'trim','corners')
    gable('Maple single gable',0,0,w,d,eave,ridge)
    C.box('Enclosed ceiling',(0,0,3.16),(13.56,4.36,.12),'interior','ceiling')
    # Porch floor projects beyond roof, as in the locked top reference.
    C.box('Porch seated skirt',(0,-3.17,.2075),(13.8,1.54,.415),'foundation','porch')
    for i in range(86):C.box('Porch skirt fluting',(-6.8+i*.16,-3.953,.2075),(.018,.025,.415),'foundation','porch',0)
    C.box('Porch timber floor',(0,-3.17,.4325),(14,1.54,.035),'timber','porch')
    for i in range(10):C.box('Porch plank groove',(0,-2.43-i*.16,.451),(14,.012,.004),'floor','porch')
    steps('Front entry ',0,-3.94,1.72,.45)
    C.solid_surface('Full porch lean-to roof',[(-7.12,-2.35,3.18),(7.12,-2.35,3.18),(7.12,-3.75,2.93),(-7.12,-3.75,2.93)],.11,'roof','porch roof')
    for i in range(35):
        x=-7.05+i*14.1/34
        C.beam('Porch roof seam',(x,-2.35,3.198),(x,-3.75,2.948),.025,.026,'roof','porch roof')
    C.box('Porch front bearing beam',(0,-3.63,2.835),(14.1,.19,.24),'trim','porch support')
    for x in (-6.7,-2.7,1.4,6.7):
        C.box('Porch post base',(x,-3.62,.545),(.29,.29,.19),'trim','porch support')
        C.box('Porch square post',(x,-3.62,1.6275),(.17,.17,2.255),'trim','porch support')
        C.box('Post capital',(x,-3.62,2.68),(.27,.24,.18),'trim','porch support')
    # Two bedrooms right, common living left, rear circulation reached from central foyer.
    for x in (1.05,4.25):C.box('Bedroom partition',(x,-.50,1.78),(.12,3.34,2.66),'interior','partitions')
    f=C.Face((0,1.17,0),(1,0,0),(0,1,0),'Bedroom corridor')
    hs=[hole('Bedroom '+str(i)+' interior door',u,.45,.86,2.1) for i,u in enumerate((2.0,5.1),1)]
    f.wall('Bedroom corridor wall',1.05,6.78,.45,3.11,depth=.12,role='interior',holes=hs)
    for h in hs:f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber',panels=1)
    sofa(-4.4,-.35,.45);kitchen(-3.8,1.77,.45,3.4)
    for x in (2.65,5.5):bed(x,-.50,.45)
    for x in (-4,0,2.6,5.4):C.qa_room_light('Maple room',(x,0,3.0),100,1.7)
    C.qa_room_light('Chassis',(0,0,.31),7,.5)
    for i,x in enumerate((-1,-3,-5)):
        light=C.bpy.data.lights.new('QA chassis point '+str(i),'POINT');light.energy=7;light.shadow_soft_size=.035
        obj=C.bpy.data.objects.new(light.name,light);C.bpy.context.collection.objects.link(obj);obj.location=(x,.1,.24)
    C.CONTACTS.append(dict(name='Maple chassis / independent porch',floor_m=.45,programme='One dwelling, two bedrooms; room plan is inferred. No transport certification.'))


def horizon():
    w,d,floor=13.6,7.2,.45
    # Each factory transport section owns a permanent chassis; join at the centreline.
    for y in (-1.8,1.8):
        before=set(C.bpy.data.objects);o=len(C.OPENINGS);chassis(w,3.6,fluted=False);rotate_new(before,o,0,y,0)
    ff=faces(w,d)
    front=[hole('Living triple',-4.65,.70,3.1,2.0),hole('Entrance',-.45,floor,1.05,2.2),hole('Door sidelight',.36,floor,.43,2.2),hole('First bedroom window',2.50,.95,1.90,1.70),hole('Second bedroom window',5.15,.95,1.85,1.70)]
    sides=[hole('Side sash A',-1.9,1.10,.62,1.50),hole('Side sash B',1.6,1.10,.62,1.50)]
    rear=[hole('Rear bedroom',-4.6,1.10,1.9,1.50),hole('Rear bathroom',-.25,1.8,1.05,.60),hole('Rear kitchen',4.25,1.05,2.2,1.6)]
    for i,(f,span,hs) in enumerate(zip(ff,[w,d,w,d],[front,sides,rear,sides])):
        top=3.02 if i!=2 else 3.98
        f.wall('Horizon '+f.label+' carrier',-span/2,span/2,floor,top,depth=.23,holes=hs,role='timber' if i==0 else 'wall')
        for h in hs:
            if h['id']=='Entrance':f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber',panels=1)
            else:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=3 if 'triple' in h['id'] else 1,rows=1,frame='trim',depth=.23)
        if i==0:
            vertical_cladding(f,span,floor,top,front,role='timber')
            f.part('Ivory entrance pier',-1.82,-.029,(floor+top)/2,1.22,.058,top-floor,'wall','facade pier')
        if i in (1,3):
            poly=[(-3.6,3.0),(3.6,3.0),(3.6,3.98),(0,4.46),(0,3.36),(-3.6,3.03)]
            if i==3:poly=[(-u,z) for u,z in reversed(poly)]
            f.panel('Sealed stepped side roof infill',poly,0,.23,'wall','roof envelope')
    cler=C.Face((0,0,0),(1,0,0),(0,1,0),'Horizon clerestory')
    ch=hole('Seven-pane clerestory',0,3.66,12.8,.70)
    cler.wall('Clerestory supported carrier',-w/2,w/2,3.33,4.46,depth=.23,holes=[ch],role='wall')
    cler.window(ch['id'],ch['u'],ch['z'],ch['w'],ch['h'],cols=7,rows=1,frame='trim',depth=.23)
    for name,ya,yb,za,zb in [('Lower front roof',-3.9,.04,3.15,3.5),('Higher rear roof',-.20,3.9,4.60,4.10)]:
        pts=[(-7.05,ya,za),(7.05,ya,za),(7.05,yb,zb),(-7.05,yb,zb)]
        C.solid_surface(name,pts,.14,'roof','Horizon roof')
        C.solid_surface(name+' timber soffit',[(x,y,z-.14) for x,y,z in pts],.028,'timber','Horizon roof')
        for i in range(34):
            x=-7.0+i*14/33
            C.beam(name+' seam',(x,ya,za+.012),(x,yb,zb+.012),.023,.025,'roof','Horizon roof')
        for yy,zz in ((ya,za),(yb,zb)):C.box(name+' edge fascia',(0,yy,zz-.065),(14.1,.08,.15),'trim','Horizon roof')
        for xx in (-7.05,7.05):C.beam(name+' side fascia',(xx,ya,za-.065),(xx,yb,zb-.065),.08,.15,'trim','Horizon roof')
    C.box('Entrance supported landing',(-.25,-4.12,.2075),(2.4,1.04,.415),'foundation','entry')
    C.box('Entrance timber deck',(-.25,-4.12,.4325),(2.5,1.04,.035),'timber','entry')
    steps('Horizon entry ', -.25,-4.64,2.2,floor)
    C.box('Entry eyebrow',(-.25,-3.98,2.89),(2.8,.97,.18),'trim','entry canopy')
    C.box('Entry eyebrow timber soffit',(-.25,-3.98,2.79),(2.72,.95,.04),'timber','entry canopy')
    # A rear corridor connects two front bedrooms, a third rear bedroom and sanitary room.
    C.box('Bedroom centre partition',(3.9,-1.80,1.72),(.12,3.14,2.54),'interior','partitions')
    C.box('Bedroom living separation',(1.2,-1.80,1.72),(.12,3.14,2.54),'interior','partitions')
    for yy,x0,x1,us in ((-.23,1.2,6.57,(1.90,4.85)),(1.02,-1.2,6.57,(.0,3.0))):
        f=C.Face((0,yy,0),(1,0,0),(0,1,0),'Horizon rooms '+str(yy))
        hs=[hole('Room door '+str(u)+' '+str(yy),u,.45,.90,2.15) for u in us]
        f.wall('Room hall wall',x0,x1,.45,3.0,depth=.12,role='interior',holes=hs)
        for h in hs:f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber',panels=1)
    C.box('Bath side partition',(-1.2,2.26,1.72),(.12,2.5,2.54),'interior','partitions')
    C.box('Bath bedroom partition',(1.7,2.26,1.72),(.12,2.5,2.54),'interior','partitions')
    C.box('Front bedroom enclosed ceiling',(3.885,-1.8,2.98),(5.37,3.14,.08),'interior','ceiling')
    C.box('Rear rooms enclosed ceiling',(2.685,2.26,2.98),(7.77,2.5,.08),'interior','ceiling')
    for x in (2.60,5.20):bed(x,-2.05,floor)
    bed(4.3,2.20,floor);bathroom(.15,2.97,floor)
    sofa(-4.65,-1.65,floor);kitchen(-4.1,2.99,floor,3.2)
    for x,y,z in [(-4.5,-1,2.9),(-4,2,3.9),(2.5,-1,2.9),(5.2,-1,2.9),(4.3,2,2.85),(.15,2,2.85),(3,.4,3.3)]:C.qa_room_light('Horizon room',(x,y,z),90,1.7)
    for y in (-1.8,1.8):
        for i,x in enumerate((-1,-3,-5)):
            light=C.bpy.data.lights.new('QA Horizon chassis point','POINT');light.energy=7;light.shadow_soft_size=.035
            obj=C.bpy.data.objects.new(light.name,light);C.bpy.context.collection.objects.link(obj);obj.location=(x,y,.24)
    C.CONTACTS.append(dict(name='Horizon two transport sections',floor_m=.45,programme='One dwelling, three bedrooms; inferred conceptual sanitary room and circulation, not a certified housing plan.'))


def craftsman():
    w,d,floor=7.2,12.8,.60
    C.box('Brick crawlspace foundation',(0,0,.28),(w,d,.56),'brick','foundation')
    C.box('Main timber floor',(0,0,.58),(w,d,.04),'floor','floor')
    ff=faces(w,d)
    front=[hole('Craftsman triple sash',-1.23,1.22,3.05,1.62),hole('Craftsman entry',1.83,floor,1.08,2.25)]
    side=[hole('Side sash '+str(i),u,1.20,1.02,1.62) for i,u in enumerate((-3.9,-.65,2.55))]
    right=side+[hole('Rear garden exit',5.15,floor,.93,2.18)]
    rear=[hole('Rear bedroom sash',-1.9,1.2,1.08,1.62),hole('Rear bath sash',1.75,1.65,.82,.9)]
    for f,span,hs in zip(ff,[w,d,w,d],[front,right,rear,side]):
        f.wall('Craftsman '+f.label+' wall',-span/2,span/2,floor,3.55,depth=.23,holes=hs)
        for h in hs:
            if 'entry' in h['id'] or 'exit' in h['id']:
                f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber',panels=2)
                if 'entry' in h['id']:
                    for ob in [o for o in C.objects() if o.name.startswith(h['id']+' recessed leaf') or o.name.startswith(h['id']+' door panel')]:f.cut(ob,'Entry upper lights',h['u'],2.09,.75,.55,.23)
                    f.window('Craftsman door six lights',h['u'],2.09,.75,.55,cols=3,rows=2,frame='timber',sill=False,depth=.23)
            elif 'triple' in h['id']:
                cursor=h['u']-h['w']/2
                for j,pw in enumerate((.80,1.45,.80)):
                    pu=cursor+pw/2;cursor+=pw
                    f.window('Front individual sash '+str(j),pu,h['z'],pw,h['h'],cols=1,rows=1,frame='trim',depth=.23)
                    trans=h['z']+h['h']*.66
                    f.part('Craftsman sash transom',pu,.12,trans,pw-.13,.08,.045,'trim','sash')
                    topheight=h['h']*.34-.065
                    for k in range(1,4 if j==1 else 2):f.part('Upper-light muntin',pu-pw/2+pw*k/(4 if j==1 else 2),.11,trans+topheight/2,.019,.035,topheight,'trim','sash')
                    f.part('Upper-light crossbar',pu,.11,trans+topheight/2,pw-.13,.035,.019,'trim','sash')
                for sign in (-1,1):f.part('Triple sash outer casing',h['u']+sign*(h['w']/2+.055),-.025,h['z']+h['h']/2,.11,.07,h['h']+.15,'trim','trim')
                for z in (h['z']-.07,h['z']+h['h']+.06):f.part('Triple sash cap',h['u'],-.025,z,h['w']+.22,.08,.12,'trim','trim')
            else:
                window(f,h,cols=1)
                f.part('Side upper sash muntin',h['u'],.118,h['z']+h['h']*.75,.022,.035,h['h']*.5-.07,'trim','sash')
                f.part('Side upper sash crossbar',h['u'],.116,h['z']+h['h']*.75,h['w']-.13,.035,.021,'trim','sash')
        horizontal_cladding(f,span,floor,3.55,hs,step=.19,trim_clearance=.13)
        for u in (-span/2+.055,span/2-.055):f.part('Ivory corner board',u,-.026,2.075,.11,.055,2.95,'trim','corners')
        for z in (.12,.24,.36,.48):f.part('Foundation mortar course',0,-.007,z,span,.016,.01,'pale','brick joints',0)
    gable('Craftsman main',0,0,12.8,7.2,3.55,6.25,axis='y',gable_role='timber',fascia_role='timber')
    C.box('Sealed unoccupied attic floor',(0,0,3.47),(6.75,12.35,.12),'interior','ceiling')
    # Fine physical shingle joints on the main gables; the attic vent cuts the carrier.
    for sy in (-1,1):
        f=C.Face((0,sy*6.52,0),(1,0,0),(0,-sy,0),'Craftsman gable')
        for row in range(13):
            z=3.61+row*.19;half=max(0,(3.8)*(6.11-z)/2.7)
            if half<.05:continue
            f.part('Cedar shingle course',0,-.004,z,half*2,.018,.014,'timber','gable shingles',0)
            count=math.floor(half*2/.22)
            for j in range(count):
                u=-half+(j+.5)*2*half/count
                if sy<0 and abs(u)<.45 and 4.76<z<5.50:continue
                f.part('Cedar shingle edge',u,-.004,z-.085,.012,.018,.15,'timber','gable shingles',0)
    ventface=C.Face((0,-6.4,0),(1,0,0),(0,1,0),'Attic vent')
    for o in [o for o in C.objects() if o.name.startswith('Craftsman main closed gable')]:
        if sum((o.matrix_world@v.co).y for v in o.data.vertices)/len(o.data.vertices)<0:ventface.cut(o,'Through attic vent',0,4.8,.70,.64,.23)
    for o in [o for o in C.objects() if o.name.startswith('Cedar shingle')]:ventface.cut(o,'Vent clear through shingles',0,4.8,.70,.64,.25)
    for x in (-.39,.39):ventface.part('Vent side casing',x,-.15,5.12,.09,.10,.82,'timber','vent')
    for z in (4.755,5.485):ventface.part('Vent head sill',0,-.15,z,.86,.10,.09,'timber','vent')
    for j in range(7):ventface.part('Attic vent louver',0,.03,4.83+j*.09,.69,.15,.028,'timber','vent')
    C.box('Porch brick foundation',(0,-7.4,.27),(7.0,2,.54),'brick','porch')
    C.box('Porch timber floor',(0,-7.4,.57),(7.2,2,.06),'timber','porch')
    for i in range(13):C.box('Porch board seam',(0,-6.48-i*.15,.601),(7.2,.012,.003),'floor','porch',0)
    gable('Craftsman porch',0,-7.4,2,7.2,3.15,4.2,axis='y',fascia_role='timber')
    porchface=C.Face((0,-8.52,0),(1,0,0),(0,1,0),'Porch gable')
    for z in (3.26,3.45,3.64,3.83,4.02):
        half=max(0,3.8*(4.06-z)/1.05)
        if half>.01:porchface.part('Porch gable clapboard',0,-.001,z,half*2,.025,.018,'wall','porch gable')
    C.box('Porch supporting header',(0,-8.20,3.035),(7.10,.30,.25),'timber','porch support')
    for x in (-3.15,3.15):
        C.box('Porch brick pier',(x,-8.20,.81),(.65,.65,1.62),'brick','porch support')
        C.box('Brick pier stone cap',(x,-8.20,1.655),(.75,.75,.07),'pale','porch support')
        vs=[(x+sx*a,-8.20+sy*a,z) for z,a in ((1.69,.235),(2.91,.16)) for sx,sy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        C.mesh('Tapered timber post',vs,C.BOX_FACES,'timber','porch support')
        C.box('Timber post foot',(x,-8.20,1.735),(.55,.55,.09),'timber','porch support')
        for sx in (-1,1):C.beam('Timber bearing knee brace',(x,-8.20,2.52),(x+sx*.48,-8.20,2.95),.14,.16,'timber','porch support')
    C.box('Stair-side short brick pier',(.45,-8.20,.76),(.51,.61,1.52),'brick','porch support')
    C.box('Short pier cap',(.45,-8.20,1.555),(.61,.71,.07),'pale','porch support')
    C.railing('Low left porch rail',(-2.82,-8.20,.60),(.19,-8.20,.60),height=.88,role='timber',spacing=.15,bottom=.12)
    steps('Craftsman front brick step ',1.82,-8.40,2.35,.60,n=4,run=.28,role='brick')
    for i in range(4):C.box('Stair timber tread',(1.82,-8.4-(3.5-i)*.28,.15*(i+1)+.007),(2.39,.29,.014),'timber','entry steps')
    for x in (-3.73,3.73):
        for i in range(19):C.box('Main exposed rafter tail',(x,-6.15+i*.68,3.40),(.30,.10,.22),'timber','roof support')
    # Source shows a discreet garden door at the rear of the right side.
    before=set(C.bpy.data.objects);n=len(C.OPENINGS)
    C.box('Garden landing',(0,-.40,.30),(1.12,.80,.60),'timber','garden entry')
    steps('Garden steps ',0,-.80,1.05,.60,n=4,run=.26)
    rotate_new(before,n,3.6,5.15,math.pi/2)
    # Inferred two-bedroom layout, continuous side hall and a modest sanitary room.
    for yy in (0.2,3.3):
        C.box('Sleeping room crosswall',(-1.10,yy,2.015),(4.54,.12,2.83),'interior','partitions')
    hall=C.Face((1.17,0,0),(0,1,0),(-1,0,0),'Craftsman bedroom hall')
    hs=[hole('Bedroom hall door '+str(i),y,.60,.86,2.14) for i,y in enumerate((1.05,4.20),1)]
    hall.wall('Bedroom hall wall',.20,6.17,.60,3.43,depth=.12,role='interior',holes=hs)
    for h in hs:hall.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber',panels=1)
    bed(-1.25,1.75,.60);bed(-1.25,4.78,.60)
    sofa(-1.25,-4.2,.60);kitchen(-1.2,-.25,.60,2.5)
    # Bathroom is off the living/entry hall, with an actual door and enclosed fixtures.
    bathface=C.Face((0,-2.7,0),(1,0,0),(0,1,0),'Cottage bath')
    bh=hole('Bathroom entrance',2.45,.60,.78,2.12)
    bathface.wall('Bath front',1.6,3.37,.60,3.43,depth=.12,role='interior',holes=[bh]);bathface.door(bh['id'],bh['u'],bh['z'],bh['w'],bh['h'],role='timber',panels=1)
    C.box('Bath left wall',(1.6,-1.75,2.015),(.12,1.9,2.83),'interior','partitions')
    C.box('Bath back wall',(2.485,-.80,2.015),(1.77,.12,2.83),'interior','partitions')
    bathroom(2.45,-1.10,.60)
    for x,y in [(-1.25,-3),(2.1,-3),(-1.25,1.7),(-1.25,4.8),(2.3,2.5),(2.4,-1.6)]:C.qa_room_light('Craftsman room',(x,y,3.28),85,1.4)
    roofz=6.25-(6.25-3.55)*2.3/3.8
    C.solid_surface('Sloped seated roof vent flashing',[(x,y,6.25-(6.25-3.55)*x/3.8+.01) for x,y in [(2.16,3.66),(2.44,3.66),(2.44,3.94),(2.16,3.94)]],.04,'roof','roof vent')
    C.rod('Small sanitary roof vent',(2.3,3.8,roofz-.1),(2.3,3.8,roofz+.28),.033,'hardware','roof vent')
    C.CONTACTS.append(dict(name='Craftsman supported porch / unoccupied attic',floor_m=.6,occupied_storeys=1,main_ridge_m=6.25,porch_ridge_m=4.2,programme='Two bedrooms, kitchen/living, inferred sanitary room and side hall; not a permit-ready floor plan.'))


def mews_home(index,side,cy):
    before=set(C.bpy.data.objects);opening_start=len(C.OPENINGS)
    mirror=1 if side<0 else -1
    low,upper= .15,3.25
    C.box('Mews grounded foundation',(0,0,.075),(6,7,.15),'foundation','foundation')
    slab=C.box('Mews upper floor',(0,0,3.14),(5.58,6.58,.22),'floor','floor')
    sx=1.95*mirror;start=-2.60;length=18*.26
    C.cut_box(slab,'Full stair headroom void',(sx,start+length/2,3.14),(1.08,length,.6))
    ff=faces(6,7,label='Mews '+str(index)+' ')
    front=[hole('Home '+str(index)+' front door',-1.85*mirror,low,1.03,2.35),hole('Home '+str(index)+' living window',.70*mirror,.60,2.25,1.93)]
    front.extend(hole('Home '+str(index)+' front bedroom sash '+str(i),u,4.12,.90,1.72) for i,u in enumerate((-1.32,1.32)))
    rear=[hole('Home '+str(index)+' rear lower '+str(i),u,.95,1.12,1.55) for i,u in enumerate((-1.45,1.45))]
    rear.extend(hole('Home '+str(index)+' rear upper '+str(i),u,4.15,1.12,1.65) for i,u in enumerate((-1.45,1.45)))
    for face_index,(f,span) in enumerate(zip(ff,[6,7,6,7])):
        if face_index==0:hs=front
        elif face_index==2:hs=rear
        else:
            # Only end houses have external side windows. Party walls remain closed.
            exterior=(cy==-6 and ((side<0 and face_index==3) or (side>0 and face_index==1))) or (cy==6 and ((side<0 and face_index==1) or (side>0 and face_index==3)))
            hs=[hole('Home '+str(index)+' end upper '+str(i),u,4.15,.94,1.60) for i,u in enumerate((-1.35,1.35))] if exterior else []
        wallspan=span if face_index in (0,2) else span-.46
        f.wall('Mews lower brick carrier',-wallspan/2,wallspan/2,low,upper,depth=.23,role='brick',holes=hs)
        f.wall('Mews upper timber carrier',-wallspan/2,wallspan/2,upper,6.36,depth=.23,role='timber',holes=hs)
        for h in hs:
            if 'front door' in h['id']:f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber',panels=1)
            else:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2 if 'living' in h['id'] else 1,rows=1,frame='trim',depth=.23)
        if face_index in (0,2) or hs:
            vertical_cladding(f,span,upper,6.36,hs,spacing=.14)
            masonry_courses(f,span,low,upper,hs)
            f.part('Mews brick-to-timber flashing',0,-.025,upper,span,.065,.06,'pale','facade junction')
    gable('Mews home '+str(index),0,0,7,6,6.5,8.65,axis='y',seams=True,gable_role='timber',fascia_role='trim',over=0,flush_gable=True)
    for sy in (-1,1):
        f=C.Face((0,sy*3.5,0),(1,0,0),(0,-sy,0),'Mews timber gable')
        for i in range(43):
            x=-3+(i+.5)*6/43;top=8.51-abs(x)*2.15/3
            if top>6.36:f.part('Gable vertical timber seam',x,-.012,(6.36+top)/2,.014,.028,top-6.36,'timber','gable cladding',0)
    C.box('Mews sealed attic floor',(0,0,6.41),(5.55,6.55,.16),'interior','ceiling')
    stair=straight_stair('Home '+str(index)+' stair',sx,start,low,upper,width=1,run=.26,count=18)
    for dx in (-.63,.63):seated_guard('Upper void edge guard',(sx+dx,start-.09,upper),(sx+dx,start+length,upper))
    seated_guard('Upper front void guard',(sx-.63,start-.09,upper),(sx+.63,start-.09,upper),end_anchors=False)
    # Upper rooms occupy one side; the other side holds stairs, landing and a clear aisle.
    wallx=.15*mirror
    roomface=C.Face((wallx,0,0),(0,1,0),(-mirror,0,0),'Home '+str(index)+' upper rooms')
    hs=[hole('Home '+str(index)+' bedroom door',-.35,upper,.86,2.15),hole('Home '+str(index)+' bathroom door',2.15,upper,.82,2.15)]
    roomface.wall('Upper room and aisle separation',-3.27,3.27,upper,6.33,depth=.12,role='interior',holes=hs)
    for h in hs:roomface.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber',panels=1)
    C.box('Upper bedroom bathroom crosswall',(-1.37*mirror,.96,4.79),(2.80,.12,3.08),'interior','partitions')
    bed(-1.75*mirror,-1.35,upper);bathroom(-1.25*mirror,2.88,upper)
    sofa(-1.2*mirror,-.70,low);kitchen(-.5*mirror,2.83,low,2.5)
    for x,y,z in [(-1.2*mirror,-1,2.85),(-.6*mirror,2.1,2.85),(-1.3*mirror,-1.3,6.15),(-1.25*mirror,2.25,6.15),(1.0*mirror,.4,6.15)]:C.qa_room_light('Mews room',(x,y,z),95,1.5)
    rotate_new(before,opening_start,side*7.5,cy,math.pi/2 if side<0 else -math.pi/2)
    C.CONTACTS.append(dict(name='Mews home '+str(index),storeys=2,stair=stair,independent_grade_door=True,programme='One unstacked dwelling with inferred kitchen/living, upper bedroom, sanitary room and full-height stair opening.'))


def mews():
    C.box('Mews landscaped compound base',(0,0,.05),(23,23,.1),'foundation','landscape base')
    C.box('Continuous court path',(0,-.7,.125),(1.7,21.6,.05),'pale','court paths')
    for side in (-1,1):
        for i,cy in enumerate((-6,0,6)):
            mews_home((i+1) if side<0 else (i+4),side,cy)
            C.box('Private patio 7.5 square metres',(side*2.75,cy-1,.125),(2.5,3,.05),'pale','private patios')
            C.box('Direct grade entrance walk',(side*2.40,cy-1.85,.125),(3.10,1.02,.05),'pale','court paths')
            C.box('Low patio divider',(side*2.75,cy+.62,.52),(2.50,.18,.84),'brick','garden walls')
            C.box('Patio divider coping',(side*2.75,cy+.62,.955),(2.56,.23,.03),'pale','garden walls')
            garden_chair(side*2.75,cy-.45,.15)
            for x in (side*1.20,side*2.20,side*3.2):
                for y in (cy+1.1,cy+1.8,cy+2.5):shrub(x,y,.1,.52+(abs(x)%1)*.15)
            for y in (cy-2.9,cy-.6,cy+.2):shrub(side*1.16,y,.1,.48)
            # A narrow planted margin and grounded front garden soften the block ends.
        for yy in (-3,3):
            C.box('Shared roof valley flashing',(side*7.5,yy,6.49),(7.02,.16,.04),'trim','roof valleys')
        for y in (-10.7,-9.7):
            for x in (side*4.7,side*6,side*8,side*9.8):shrub(x,y,.1,.6)
        C.box('Front garden boundary',(side*6.5,-11,.53),(9.4,.18,.86),'brick','garden walls')
        C.box('Front wall coping',(side*6.5,-11,.975),(9.45,.24,.03),'pale','garden walls')
        small_tree(side*7.5,-10.3,.1,3.2,spread=.6)
    small_tree(-1.20,.95,.1,3.6);small_tree(1.20,-5.2,.1,3.4)
    C.box('Rear sitting terrace',(0,10.1,.125),(5.4,2.4,.05),'pale','court paths')
    C.box('Shared bench seat',(0,10.45,.57),(2.4,.48,.10),'timber','garden furniture')
    C.box('Shared bench back',(0,10.64,.86),(2.4,.06,.52),'timber','garden furniture')
    for x in (-.90,.90):C.box('Bench grounded leg',(x,10.45,.33),(.12,.4,.40),'hardware','garden furniture')
    # Thin seams keep paving legible at student-view scale without texture cards.
    for y in range(-11,11):C.box('Court paving joint',(0,y,.152),(1.7,.013,.003),'foundation','paving joints',0)
    C.CONTACTS.append(dict(name='Mews court',private_patios=6,each_private_patio_m=[2.5,3],continuous_central_path_m=1.7,complete_zoning_parcel=False,minimum_MG_parcel_m2=750))


def office():
    low,upper,walltop=.15,3.55,7.05
    def outline(w,d,court,back):
        return [(-w/2,-d/2),(-court/2,-d/2),(-court/2,back),(court/2,back),(court/2,-d/2),(w/2,-d/2),(w/2,d/2),(-w/2,d/2)]
    footprint=outline(14,12,7,2)
    inside=outline(13.58,11.58,7.42,2.21)
    C.prism('Office U foundation',footprint,'z',0,low,'foundation','foundation')
    slab=C.prism('Continuous office upper floor',inside,'z',upper-.22,upper,'floor','floor')
    sx,start,length=-6.0,-3.2,5.4
    C.cut_box(slab,'Office stair full headroom void',(sx,start+length/2,upper-.11),(1.08,length,.6))
    # A physically reserved vertical core, without claiming a certified lift design.
    C.cut_box(slab,'Reserved vertical core floor void',(5.80,3.80,upper-.11),(1.22,1.22,.6))
    segments=[
      (C.Face((-5.25,-6,0),(1,0,0),(0,1,0),'Office left front'),3.5,'front'),
      (C.Face((5.25,-6,0),(1,0,0),(0,1,0),'Office right front'),3.5,'front'),
      (C.Face((-7,0,0),(0,-1,0),(1,0,0),'Office left outer'),11.54,'outer'),
      (C.Face((7,0,0),(0,1,0),(-1,0,0),'Office right outer'),11.54,'outer'),
      (C.Face((0,6,0),(-1,0,0),(0,-1,0),'Office rear'),14,'rear'),
      (C.Face((-3.5,-2,0),(0,1,0),(-1,0,0),'Office left court'),7.54,'court'),
      (C.Face((3.5,-2,0),(0,-1,0),(1,0,0),'Office right court'),7.54,'court'),
      (C.Face((0,2,0),(1,0,0),(0,1,0),'Office court entrance'),7.46,'entry')]
    for index,(f,span,kind) in enumerate(segments):
        hs=[]
        positions=[0] if kind=='front' else [-3.6,0,3.6] if kind=='outer' else [-5.25,-1.75,1.75,5.25] if kind=='rear' else [-2,2] if kind=='court' else [-2.35,0,2.35]
        for level,z in enumerate((.68,4.08)):
            for u in positions:
                if kind=='entry' and level==0 and u==0:hs.append(hole('Office central double entry',0,low,1.55,2.44));continue
                width=2.08 if kind=='front' else 2.30 if kind=='court' else 1.90 if kind=='entry' and level==1 and u==0 else 1.24
                hs.append(hole(f.label+' window '+str(level)+' '+str(u),u,z,width,2.23))
        f.wall(f.label+' brick carrier',-span/2,span/2,low,walltop,depth=.23,role='brick',holes=hs)
        for h in hs:
            glazing(f,h,door='double entry' in h['id'],cols=2 if kind in ('front','court') or 'double entry' in h['id'] else 1)
            if 'double entry' in h['id']:f.part('Entry top-light transom',0,.128,2.27,h['w']-.13,.09,.045,'trim','entry glazing')
        masonry_courses(f,span,low,walltop,hs,head_joints=True)
        if kind=='court':
            f.part('Court metal spandrel',0,-.02,3.43,span,.05,.46,'trim','court facade')
            for u in ((-3.43 if index==5 else 3.43),0):
                for k in (-2,-1,0,1,2):
                    fin=u+k*.13
                    for zz in (.44,3.43,6.70):f.part('Fin fixing bracket',fin,-.075,zz,.045,.17,.045,'hardware','fin support')
                    f.part('Full height timber court fin',fin,-.17,3.57,.070,.22,6.46,'timber','court fins')
    # One closed U roof and two single-piece rings avoid internal parapets at wing joins.
    C.prism('Continuous U roof',inside,'z',6.85,7.05,'roof','roof')
    C.prism('Continuous roof weathering membrane',outline(13.66,11.66,7.34,2.17),'z',7.05,7.054,'roof','roof membrane')
    def roof_ring(name,outer,inner,z0,z1,role):
        owner=C.prism(name,outer,'z',z0,z1,role,'parapet')
        cutter=C.prism(name+' cutter',inner,'z',z0-.1,z1+.1,role,'construction cutter')
        C.bpy.context.view_layer.objects.active=owner
        mod=owner.modifiers.new('Open continuous U roof well','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
        C.bpy.ops.object.modifier_apply(modifier=mod.name);C.remove_cutter(cutter);C.normalise(owner.data)
    roof_ring('Continuous brick parapet',footprint,outline(13.64,11.64,7.36,2.18),7.05,7.34,'brick')
    roof_ring('Continuous dark coping',outline(14.08,12.08,6.92,1.96),outline(13.56,11.56,7.44,2.22),7.34,7.40,'trim')
    for x in (-5.25,5.25):
        for y in (-4,-2,0,2,4):C.box('Roof membrane seam',(x,y,7.055),(3.1,.012,.004),'joint','roof membrane',0)
    for y in (3.4,4.8):C.box('Connector roof membrane seam',(0,y,7.055),(7,.012,.004),'joint','roof membrane',0)
    stair=straight_stair('Office stair',sx,start,low,upper,width=1,run=.27,count=20)
    for dx in (-.63,.63):seated_guard('Office stair void guard',(sx+dx,start-.09,upper),(sx+dx,start+length,upper))
    seated_guard('Office void front guard',(sx-.63,start-.09,upper),(sx+.63,start-.09,upper),end_anchors=False)
    # Lift reservation has solid enclosing walls and actual door openings on both levels.
    corefaces=faces(1.5,1.5,5.8,3.8,'Reserved core ')
    for i,f in enumerate(corefaces):
        hs=[hole('Reserved lift door '+str(level),0,z,.86,2.25) for level,z in enumerate((low,upper))] if i==3 else []
        span=1.5 if i in (0,2) else 1.18
        f.wall(f.label+' enclosure',-span/2,span/2,low,6.85,depth=.16,role='interior',holes=hs)
        for h in hs:f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='hardware',panels=2)
    for z in (low,upper):
        before=set(C.bpy.data.objects);opening_start=len(C.OPENINGS)
        desk(0,0,z);rotate_new(before,opening_start,-5.1,-4.40,-math.pi/2)
        for y in (-4.25,-.65):
            before=set(C.bpy.data.objects);opening_start=len(C.OPENINGS)
            desk(0,0,z);rotate_new(before,opening_start,5.1,y,math.pi/2)
        # Meeting furniture leaves the central entry and rear cross-connection clear.
        C.box('Meeting table',(0,4.65,z+.76),(2.6,.92,.08),'timber','office furniture')
        for x in (-1.05,1.05):
            for y in (4.32,4.98):C.box('Meeting table leg',(x,y,z+.36),(.065,.065,.72),'hardware','office furniture')
        for x in (-.78,.78):garden_chair(x,5.30,z)
        for x,y in [(-5.1,-4.3),(-5.1,0),(-5.1,4.4),(0,4.2),(5.1,-4),(5.1,0),(5.0,4.6)]:C.qa_room_light('Office room',(x,y,z+2.92),125,1.7)
    C.box('Reception counter',(-2.35,3.00,.65),(1.35,.72,1.0),'timber','reception')
    C.box('Reception worktop',(-2.35,3.00,1.18),(1.45,.80,.06),'pale','reception')
    # Source garden is contained inside the U; furniture and trees remain clear of glazing.
    C.box('Courtyard grounded base',(0,-2,.05),(7,8,.10),'foundation','landscape base')
    C.box('Central entrance paving',(0,-2,.125),(2.2,8,.05),'pale','court paths')
    C.box('Entrance cross paving',(0,1.2,.125),(7,1.6,.05),'pale','court paths')
    for side in (-1,1):
        C.box('Timber garden bench seat',(side*1.55,-2.7,.56),(.48,2.1,.12),'timber','garden furniture')
        for y in (-3.48,-1.92):C.box('Bench grounded pedestal',(side*1.55,y,.30),(.38,.16,.40),'timber','garden furniture')
        for y in (-5.4,-3.6,-1.5,-.2):shrub(side*2.65,y,.10,.56)
        for y in (-4.6,-2.5,-.8):shrub(side*2.12,y,.10,.45)
    small_tree(-2.4,-4.2,.1,3.0,spread=.45)
    for y in [i*.55-5.8 for i in range(14)]:C.box('Court paver joint',(0,y,.152),(2.2,.013,.003),'foundation','paving joints',0)
    C.CONTACTS.append(dict(name='Compact courtyard office',storeys=2,authored_footprint_m2=112,authored_gross_floor_area_m2=224,stair=stair,lift='Enclosed reserved core only; not an approved accessibility solution.',programme='Two enclosed office floors, reception, desks, meeting areas and one internal stair. Interior and rear facade are inferred.'))


DETAILS={'maple':[
 ('facade_close',(8,-16,6),(0,-2.5,2.1)),('architecture_close',(2.5,-7,2.2),(0,-2.4,1.6)),
 ('glass_close',(-5.8,-5.1,2.2),(-4.8,-2.3,1.7)),('roof_contact',(7,-8,7),(3,-2.3,3.2)),
 ('side_projection',(14,-7,4),(6.8,-1.1,2.2)),('interior',(-.3,-1.6,1.8),(-4.7,1.3,1.45)),
 ('bedroom',(4.08,-1.98,2.75),(2.65,-.5,.6)),('bed_contact',(3.93,-1.75,.7),(3.25,-1.15,.58)),
 ('furniture_contact',(-2.9,-1.55,.67),(-3.45,-.60,.5)),
 ('corridor',(.3,1.78,1.8),(4.5,1.65,1.35)),('chassis',(0,-1.05,.24),(-4.5,1.38,.22)),
 ('porch_contact',(4,-6,2.4),(1.4,-3.62,1.6))],
 'horizon':[
 ('facade_close',(9,-17,6),(1,-3.6,2.2)),('architecture_close',(2,-7,2.2),(-.3,-3.6,1.6)),
 ('glass_close',(-5,-6,2.1),(-4.65,-3.6,1.7)),('roof_contact',(8,-9,7),(0,0,3.8)),
 ('side_projection',(15,-8,5),(6.8,0,2.5)),('interior',(-.4,-2.5,2.1),(-4.4,.4,1.4)),
 ('bedroom',(6.3,-3.28,2.75),(5.2,-2.0,.6)),('corridor',(.5,.43,1.8),(5.8,.43,1.4)),
 ('chassis',(0,-2.25,.24),(-4.5,-.75,.22)),('clerestory_inside',(-4,2.8,2.8),(-3,0,4.0)),
 ('bed_contact',(6.2,-3.25,.49),(5.84,-2.87,.485))],
 'craftsman':[
 ('facade_close',(8,-17,6),(0,-6.8,2.8)),('architecture_close',(5,-12,3.4),(2.8,-8.2,2.0)),
 ('glass_close',(-3,-9,2.3),(-1.25,-6.4,2.05)),('roof_contact',(8,-14,10),(0,-6.3,4.5)),
 ('side_projection',(13,-4,5),(3.6,0,2.2)),('interior',(2.5,-5.8,2.1),(-1.5,-2.3,1.5)),
 ('bedroom',(.9,.55,2.95),(-1.25,1.75,.8)),('corridor',(2.3,5.8,2),(2.1,.1,1.5)),
 ('post_contact',(4.3,-10,2.4),(3.15,-8.2,1.7)),('garden_entry',(7,8,3),(3.6,5.15,1.4)),
 ('attic_vent',(2,-10,6),(0,-6.4,5.1))],
 'mews':[
 ('facade_close',(-1,-10,5),(-4,-6,3.6)),('architecture_close',(-1,-8,2.2),(-4,-7.85,1.3)),
 ('glass_close',(-1.7,-5.3,2),(-4,-5.3,1.5)),('roof_contact',(0,-7,11),(-5,-3,6.7)),
 ('side_projection',(-17,-13,6),(-8,-9,3.8)),('interior',(-4.6,-6,1.8),(-9,-7.2,1.4)),
 ('bedroom',(-4.5,-8.55,5.8),(-6.15,-7.75,3.7)),('stairs',(-4.55,-5.2,1.9),(-9.1,-4.05,3.0)),
 ('upper_landing',(-10.38,-3.38,4.9),(-7.5,-5.2,3.5)),('stair_contact',(-10.3,-4.8,3.8),(-9.58,-4.05,3.25)),
 ('bathroom',(-8.75,-8.5,5),(-10.2,-7.25,4.0)),('court',(0,-15,3),(0,0,3)),
 ('bed_contact',(-4.8,-6.55,3.285),(-5.33,-7.11,3.285))],
 'office':[
 ('facade_close',(11,-17,8),(0,-1,3.7)),('architecture_close',(0,-3,2.2),(0,2,1.6)),
 ('glass_close',(5.1,-8.8,1.8),(5.1,-5.8,1.7)),('roof_contact',(-8,-3,12),(-4,2,7.05)),
 ('side_projection',(-15,-7,6),(-7,0,3.5)),('interior',(4.0,-5.5,2.1),(4.4,.4,1.6)),
 ('stairs',(-4.05,-4.5,2.2),(-6,0,2.7)),('upper_landing',(-4.20,3.7,5.3),(-6,1.7,3.9)),
 ('stair_contact',(-4.8,3.3,4.1),(-6,2.2,3.55)),('reception',(1.8,2.45,2.1),(-2.2,3,1.3)),
 ('reserved_core',(3.1,4.3,4.8),(5.05,3.8,4.675)),('fin_contact',(-2.9,-.4,3.65),(-3.4,-2,3.43)),
 ('court',(0,-12,3),(0,1,3))]}


def cameras(kind):
    d=SPECS[kind]['dimensions_m'];scale=max(d['width'],d['depth'])/34
    basic=[('front',(0,-64,12)),('front_corner',(46,-58,32)),('aerial',(39,-49,69)),('top',(0,0,90)),('left_side',(-64,0,12)),('right_side',(64,0,12)),('rear',(0,64,12)),('rear_side',(-46,58,32))]
    out=[dict(name=n,location=tuple(v*scale for v in loc),target=(0,.001 if n=='top' else 0,0 if n=='top' else d['height']*.4),**({'ortho_scale':max(d['width'],d['depth'])*1.2} if n=='top' else {})) for n,loc in basic]
    wide={'interior','corridor','chassis','stairs','court'}
    if kind=='office':wide.update(('upper_landing','reserved_core'))
    return out+[dict(name=n,location=loc,target=t,whole=False,lens=16 if n=='bedroom' else 24 if n in wide else 42) for n,loc,t in DETAILS[kind]]


def manifest(kind,version):
    s=SPECS[kind];cams=cameras(kind)
    return dict(candidate=f'{s["slug"]}-clay-v{version:03d}',method=C.METHOD,representation_kind='architectural_clay',archetype_id=s['id'],variant_id=s['variant'],state='prework',keeper_claimed=False,runtime_seed_allowed=False,
      measurement_contract=dict(dimensions_m=s['dimensions_m'],observed_storeys=s['storeys'],reference_reconciliation=s.get('reference_reconciliation','Nominal metric design; generated references govern topology.'),source_measurements=['Exact original references govern roof, massing and opening cadence.'],hidden_assumptions=['Metric dimensions are authored, not surveyed.','Hidden interiors and rear construction are inferred.','Top reference is conceptual, not a georeferenced orthophoto.']),
      roof_contract=dict(authority='Locked original pixels; complete supported weathering envelope.'),identity_contract=dict(owner='Source-specific physical geometry',bitmap_stickers='None in architectural clay.'),material_contract=dict(profile='Source-palette untextured clay',limitations='Final textured keeper stage remains separate.'),programme_contract=dict(storeys=s['storeys'],description=s['program'],uses=s['uses'],legal_approval=False),contact_contract=['Grade-zero support.','Through-carrier apertures.','Complete supported roofs and access.'],runtime_contract=dict(scale='fixed_native_only',resizing=False,installation='not installed',review='NOT TESTED'),camera_roster=cams,mandatory_review_views=[c['name'] for c in cams])


def prepare(a,entry,m):
    out=Path(a.output).resolve()
    if not out.is_relative_to(Path('C:/dev-artifacts/CityPrompt').resolve()):raise ValueError('Output must be external')
    if a.dry_run:print('DRY_RUN_PASS '+m['candidate']);return None
    out.mkdir(parents=True,exist_ok=False)
    for name in ('sources','scripts','renders','review','evidence','boards'):(out/name).mkdir()
    for s in entry['sources']:
        shutil.copy2(s['original_path'],out/s['path']);assert C.digest(out/s['path'])==s['sha256']
    shutil.copy2(Path(entry['_reference_root'])/'generation-provenance.json',out/'sources/generation-provenance.json')
    scripts=[Path(C.__file__),Path(__file__),HERE/'assemblies.py',HERE/'plan.py',HERE/'designs.json']
    for p in scripts:shutil.copy2(p,out/'scripts'/p.name)
    C.write_json(out/'source-entry.json',{k:v for k,v in entry.items() if not k.startswith('_')})
    m['source_contract']=dict(sources=entry['sources'],exact_variant_only=True,origin='original_generated_design',generated_references_explicitly_requested=True,not_surveyed=True)
    m['provenance']=dict(scripts=[dict(path='scripts/'+p.name,sha256=C.digest(out/'scripts'/p.name)) for p in scripts],blender_version=C.bpy.app.version_string,python_version=sys.version,build_started_utc=C.utc(),generation_api_calls_during_build=0,reference_generation='built-in image_gen; exact prompts in source provenance',render_source='actual optimized GLB reimport only')
    C.write_json(out/'prework-manifest.json',m);return out


def main():
    p=argparse.ArgumentParser();p.add_argument('--kind',choices=list(SPECS),required=True);p.add_argument('--source-root',type=Path,required=True);p.add_argument('--output',required=True);p.add_argument('--version',type=int,default=1);p.add_argument('--resolution',type=int,default=1440);p.add_argument('--dry-run',action='store_true')
    a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);m=manifest(a.kind,a.version);out=prepare(a,source_entry(a.kind,a.source_root),m)
    if out is None:return
    cams=C.setup(dict(PALETTE,**PALETTES.get(a.kind,{})),m['camera_roster'],a.resolution);C.bevel=lambda *args,**kwargs:None
    for obj in C.bpy.context.scene.objects:
        if obj.type=='LIGHT':obj.location*=2;obj.data.energy*=4;obj.data.size*=2
        if obj.name=='QA ground - excluded':obj.scale*=6
    globals()[a.kind]()
    for obj in C.objects():
        bm=C.bmesh.new();bm.from_mesh(obj.data);C.bmesh.ops.triangulate(bm,faces=list(bm.faces));C.bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_area()<=1e-10],context='FACES_ONLY');bm.to_mesh(obj.data);bm.free();obj.data.update()
    C.deliver(out,m,cams)


if __name__=='__main__':main()
