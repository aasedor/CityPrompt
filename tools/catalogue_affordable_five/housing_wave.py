"""Four source-specific affordable housing compositions after the Porchlight pilot."""
import math
import clay_core as C
from assemblies import (hole,faces,glazing,steps,sofa,bed,straight_stair,seated_guard,
    bathroom,shrub,garden_chair,rotate_new,small_tree,vertical_cladding,flat_roof)
from geometry import gable,kitchen

def aperture(f,h):
    if 'door' in h['id'].lower():f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber',panels=1)
    else:f.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2 if h['w']>1.5 else 1,frame='trim',depth=.23)

def internal_wall(f,name,a,b,z,top,doors):
    f.wall(name,a,b,z,top,depth=.12,role='interior',holes=doors)
    for h in doors:f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='timber',panels=1)

def canopy(name,x,y,z,w,depth=1.1,posts=False):
    C.box(name+' soffit',(x,y,z),(w,depth,.12),'timber','entry shelter')
    C.box(name+' weathering cap',(x,y,z+.095),(w+.1,depth+.1,.07),'roof','entry shelter')
    for xx in (x-w*.43,x+w*.43):
        if posts:
            C.box(name+' foot',(xx,y-depth*.40,.16),(.22,.22,.04),'hardware','entry shelter')
            C.box(name+' post',(xx,y-depth*.40,(z+.12)/2),(.12,.12,z-.18),'timber','entry shelter')
        else:
            C.beam(name+' seated wall bracket',(xx,y+depth*.47,z-.52),(xx,y-depth*.40,z-.065),.09,.09,'timber','entry shelter')

def juniper():
    for cx in (-7.5,7.5):
        for cy in (-7.5,7.5):
            before=set(C.bpy.data.objects);start=len(C.OPENINGS);sign=1 if cx>0 else -1
            C.box('Cottage foundation',(0,0,.075),(7,7,.15),'foundation','foundation')
            ff=faces(7,7,label='Cottage ')
            front=[hole('Cottage front door',sign*1.30,.15,1.0,2.12),hole('Cottage living window',-sign*1.20,.72,2.0,1.48)]
            for i,f in enumerate(ff):
                hs=front if i==0 else [hole('Cottage rear bedroom window',1.50,1.0,1.25,1.35),hole('Cottage bath window',-1.60,1.72,.6,.62)] if i==2 else [hole('Cottage side sash',2.0 if i==1 else -2.0,1.0,.9,1.4)]
                if (i==1 and sign==1) or (i==3 and sign==-1):hs.append(hole('Private patio door',-sign*1.8,.15,.9,2.1))
                span=7 if i%2==0 else 6.54
                f.wall('Sage cottage envelope',-span/2,span/2,.15,2.82,depth=.23,holes=hs)
                for h in hs:aperture(f,h)
                vertical_cladding(f,span,.15,2.82,hs,spacing=.20,role='joint')
            C.box('Cottage ceiling',(0,0,2.77),(6.56,6.56,.10),'interior','ceiling')
            gable('Juniper entrance gable',0,0,7,7,2.96,6.0,axis='y',seams=True,over=.20,flush_gable=True)
            for f in (ff[0],ff[2]):
                for j in range(35):
                    u=-3.4+j*.2; top=5.86-abs(u)/3.5*3.04
                    f.part('Gable vertical timber seam',u,-.012,(2.82+top)/2,.014,.028,top-2.82,'joint','gable cladding',0)
            canopy('Cottage entry',sign*1.30,-3.99,2.47,1.45,.98)
            C.box('Cottage door approach',(sign*1.30,-4.02,.075),(1.55,1.06,.15),'foundation','entry')
            steps('Cottage entry step',sign*1.30,-4.55,1.55,.15,n=1,run=.35,role='foundation')
            f=C.Face((0,.65,0),(1,0,0),(0,1,0),'Cottage private rooms')
            internal_wall(f,'Bedroom and bath enclosure',-3.27,3.27,.15,2.72,[hole('Bedroom door',-2.65,.15,.82,2.05),hole('Bath door',1.4,.15,.82,2.05)])
            C.box('Bedroom sanitary separator',(.08,1.99,1.435),(.12,2.57,2.57),'interior','partitions')
            # A 1.12 m clear side approach connects the bedroom door to the bed.
            bed(-1.35,2.13,.15);bathroom(1.55,2.58,.15)
            sofa(1.35,-1.50,.15)
            before_k=set(C.bpy.data.objects);start_k=len(C.OPENINGS)
            # The compact run leaves .91 m at the bedroom approach; the fridge
            # stays inside the front wall instead of pinching either doorway.
            kitchen(0,0,.15,1.6);rotate_new(before_k,start_k,-2.78,-1.10,math.pi/2)
            for x,y in ((0,-1.7),(-1.5,1.95),(1.6,1.95)):C.qa_room_light('Cottage occupied room',(x,y,2.65),80,1.3)
            rotate_new(before,start,cx,cy,0)
            C.box('Private twelve square metre patio',(sign*12.5,cy-.50,.075),(3,4,.15),'pale','private outdoor space')
            garden_chair(sign*12.2,cy-.6,.15);garden_chair(sign*12.2,cy+.7,.15)
            C.box('Front cottage garden',(cx,cy-4.3,.035),(7,1.6,.07),'foundation','planting bed')
            for xx in (-2.5,-1.7,-.7,.3,2.7):
                if abs(xx-sign*1.3)>.9:shrub(cx+xx,cy-4.2,.07,.46)
            C.CONTACTS.append(dict(name='Independent cottage',centre=[cx,cy],storeys=1,units=1,private_patio_m2=12))
    C.box('Shared garden lawn',(0,0,.035),(8,22,.07),'planting','common outdoor space')
    # End at the rear cottage garden edge. Overlapping upward lawn/bed faces
    # at z=.07 produced pale streaks in the actual globe renderer.
    for x in (-7.5,7.5):C.box('Side common lawn',(x,-.8,.035),(7,6.4,.07),'planting','common outdoor space')
    C.box('Central garden spine',(0,0,.065),(1.15,24,.07),'pale','paths')
    C.box('Cross garden walk',(0,0,.065),(22,1.1,.07),'pale','paths')
    for x in (-8.8,8.8):C.box('Rear cottage door connector',(x,1.4,.04),(1.25,2.8,.08),'pale','paths')
    C.box('Street entrance walk',(0,-12.4,.04),(22,1.0,.08),'pale','paths')
    small_tree(.95,1.05,.07,3.5,.85)
    C.CONTACTS.append(dict(name='Cottage cluster programme',unit_area_m2=49,common_garden_envelope_m2=64,common_garden_min_dimension_m=8,site_approval=False))

def stacked_home(cx,z,index):
    # Each dwelling has enclosed bedrooms and bathroom behind its living room.
    p=C.Face((cx,1.0,0),(1,0,0),(0,1,0),'Stackyard private rooms '+str(index))
    internal_wall(p,'Private bedroom front partition',-3.27,3.27,z,z+2.98,[hole('Bedroom left door',-.65,z,.85,2.1),hole('Bedroom right door',.65,z,.85,2.1)])
    C.box('Stacked bedroom separation',(cx,3.15,z+1.49),(.12,4.15,2.98),'interior','partitions')
    bed(cx-1.7,3.65,z);bed(cx+1.7,3.65,z)
    bath=C.Face((cx,-1.15,0),(1,0,0),(0,-1,0),'Stackyard bath '+str(index))
    internal_wall(bath,'Sanitary room front',-3.26,-1.4,z,z+2.98,[hole('Bathroom door',-2.2,z,.82,2.1)])
    C.box('Sanitary side',(cx-1.34,-.04,z+1.49),(.12,2.18,2.98),'interior','partitions')
    bathroom(cx-2.18,.3,z)
    kitchen_objects=set(C.bpy.data.objects);kitchen_openings=len(C.OPENINGS)
    kitchen(0,0,z,2.15);rotate_new(kitchen_objects,kitchen_openings,cx+2.8,-1.50,math.pi/2)
    sofa(cx+.55,-3.7,z)
    for x,y in ((cx+.5,-2.5),(cx-1.7,3),(cx+1.7,3),(cx-2.1,-.25)):C.qa_room_light('Stacked occupied room',(x,y,z+2.84),80,1.25)

def gallery_stair(x,y,lower,upper,width=1.20):
    """Source-visible open treads carried on two dark stringers."""
    count=18;run=.26;rise=(upper-lower)/count
    for i in range(count):
        top=lower+(i+1)*rise;yy=y+(i+.5)*run
        C.box('Gallery open tread',(x,yy,top-.035),(width,run+.02,.07),'timber','external stairs')
        for side in (-1,1):
            xx=x+side*(width/2-.025)
            C.box('Gallery stair baluster',(xx,yy,top+.51),(.025,.025,1.02),'hardware','external stairs')
    for side in (-1,1):
        xx=x+side*(width/2-.14)
        C.beam('Gallery continuous stringer',(xx,y-.08,lower+.02),(xx,y+(count-.5)*run,upper-.12),.10,.18,'hardware','external stairs')
        C.box('Gallery stringer base shoe',(xx,y-.04,lower+.018),(.22,.30,.036),'hardware','external stairs')
        C.beam('Gallery stair handrail',(x+side*(width/2-.025),y+run*.5,lower+rise+1.02),(x+side*(width/2-.025),y+(count-.5)*run,upper+1.02),.045,.045,'hardware','external stairs')

def stackyard():
    low=.15;upper=3.35;top=6.62
    C.box('Stacked homes foundation',(0,0,.075),(21,11,.15),'foundation','foundation')
    front=[];rear=[]
    for lev,z in enumerate((low,upper)):
        for i,x in enumerate((-7,0,7)):
            front.extend([hole(f'Entry door {lev} {i}',x-2.1,z,1.05,2.3),hole(f'Living window {lev} {i}',x+.8,z+.73,2.65,1.68)])
            rear.extend([hole(f'Rear bedroom {lev} {i} {j}',x+u,z+.83,1.7,1.5) for j,u in enumerate((-1.8,1.8))])
    for i,f in enumerate(faces(21,11)):
        hs=front if i==0 else rear if i==2 else [hole(f'End sash {lev} {j}',u,z+.83,.9,1.5) for lev,z in enumerate((low,upper)) for j,u in enumerate((-3.8,0,3.8))]
        span=21 if i%2==0 else 10.54
        f.wall('Olive panel envelope',-span/2,span/2,low,top,depth=.23,holes=hs)
        for h in hs:aperture(f,h)
        vertical_cladding(f,span,low,top,hs,spacing=.46,role='joint')
        if i==0:
            accent=C.Face((0,-5.525,0),(1,0,0),(0,1,0),'Cedar door bays')
            for x in (-7,0,7):accent.wall('Cedar entry surround',x-2.92,x-1.27,low,top,depth=.035,role='timber',holes=front)
    C.box('Stacked occupied upper plate',(0,0,upper-.11),(20.56,10.56,.22),'floor','occupied floors')
    C.box('Stacked ceiling',(0,0,6.56),(20.56,10.56,.12),'interior','ceiling')
    for x in (-3.5,3.5):C.box('Full party separation',(x,0,3.41),(.16,10.54,6.52),'interior','partitions')
    for lev,z in enumerate((low,upper)):
        for i,x in enumerate((-7,0,7)):stacked_home(x,z,lev*3+i)
    # Gallery is seated on a beam/post grid and opens to two stair landings.
    C.box('Front gallery',(0,-6.50,upper-.11),(21,2.05,.22),'floor','gallery')
    C.box('Ground private patio',(0,-6.50,.075),(21,2.05,.15),'foundation','patios')
    C.box('Gallery edge bearer',(0,-7.32,3.08),(21.05,.20,.30),'trim','gallery support')
    for x in (-10.25,-3.5,3.5,10.25):
        C.box('Gallery column foot',(x,-7.32,.17),(.3,.3,.04),'hardware','gallery support')
        C.box('Gallery full column',(x,-7.32,3.40),(.16,.16,6.46),'trim','gallery support')
    seated_guard('Continuous gallery guard',(-10.30,-7.39,upper),(10.30,-7.39,upper))
    for sign in (-1,1):
        x=sign*11.16
        C.box('Stair upper landing',(x,-6.50,upper-.11),(1.4,2.05,.22),'floor','external stairs')
        C.box('Stair grounded base',(x,-10.25,.075),(1.6,5.50,.15),'foundation','external stairs')
        gallery_stair(x,-12.08,low,upper)
        for yy in (-7.12,-5.68):
            C.box('Stair landing founded pad',(x,yy,.075),(.40,.40,.15),'foundation','external stairs')
            C.box('Stair landing column',(x,yy,1.64),(.16,.16,2.98),'hardware','external stairs')
        seated_guard('Outer landing guard',(x+sign*.59,-7.36,upper),(x+sign*.59,-5.67,upper))
        seated_guard('Rear landing guard',(sign*10.50,-5.67,upper),(x+sign*.59,-5.67,upper))
        steps('Gallery base step',x,-13.0,1.6,.15,n=1,run=.35,role='foundation')
    flat_roof('Stackyard complete roof',0,-1,21.25,13.25,6.79,parapet=.25)
    for x in (-7,0,7):
        C.box('Private front approach',(x-2.1,-8.12,.075),(1.7,1.22,.15),'foundation','paths')
        steps('Home patio step',x-2.1,-8.73,1.7,.15,n=1,run=.3,role='foundation')
        garden_chair(x+1.8,-6.1,.15)
        for dx in (-.6,.2,1,1.8,2.6):shrub(x+dx,-8.05,0,.43)
    C.CONTACTS.append(dict(name='Six individual dwellings',storeys=2,units=6,upper_access='shared gallery and two supported stairs',legal_use='Multi-Residential Development, subject to parcel review'))

def apartment_room(cx,side,z,width,depth,studio):
    # Front/rear suites face outward; the corridor stays clear at y=+-1.2.
    before=set(C.bpy.data.objects);start=len(C.OPENINGS)
    # Local suite y=0 at corridor, extends +y to outer wall.
    bath_width=2.0
    bath=C.Face((0,2.05,0),(1,0,0),(0,-1,0),'Suite bath entry')
    bath_end=-width/2+bath_width if studio else -.35
    bath_door=-width/2+1.2 if studio else -.95
    internal_wall(bath,'Enclosed bathroom',-width/2+.1,bath_end,z,z+2.98,[hole('Bathroom door',bath_door,z,.82,2.1)])
    C.box('Bathroom side',(bath_end+.06,1.05,z+1.49),(.12,2.10,2.98),'interior','partitions')
    bathroom(-width/2+1.10,.60,z)
    if studio:
        before_kitchen=set(C.bpy.data.objects);start_kitchen=len(C.OPENINGS)
        kitchen(0,0,z,2.1)
        rotate_new(before_kitchen,start_kitchen,width/2-.40,2.0,math.pi/2)
    else:kitchen(width/2-1.70,.48,z,2.1)
    if studio:
        bed(-width/2+1.2,depth-1.4,z)
        sofa(width/2-1.45,depth-1.2,z)
    else:
        divider=C.Face((-.35,0,0),(0,1,0),(1,0,0),'Bedroom divider')
        internal_wall(divider,'Private bedroom enclosure',2.1,depth,z,z+2.98,[hole('Bedroom door',2.8,z,.85,2.1)])
        bed(-width/2+1.65,depth-1.5,z);sofa(width/2-1.5,depth-1.4,z)
    for x,y in ((-width/2+1.1,.9),(-width/2+1.5,depth-1.4),(width/2-1.5,depth-1.5)):
        C.qa_room_light('Apartment occupied room',(x,y,z+2.82),80,1.25)
    rotate_new(before,start,cx,side*1.2,0 if side==1 else math.pi)

def apartment(kind):
    studio=kind=='switchback';levels=4 if studio else 3;d=14 if studio else 13
    low=.15;step=3.3;walltop=low+levels*step;roofz=walltop+.1
    C.box('Apartment grounded foundation',(0,0,.075),(24,d,.15),'foundation','foundation')
    frontage={};allfaces=faces(24,d,label=kind+' ')
    for side_index,f in enumerate(allfaces):
        hs=[]
        for lev in range(levels):
            z=low+lev*step
            if side_index in (0,2):
                xs=(-7.05,-4.95,-1.05,1.05,4.95,7.05) if studio else (-6.85,-3.40,3.40,6.85)
                hs += [hole(f'Apartment window {side_index} {lev} {i}',x,z+(.55 if studio else .75),1.4 if studio else 2.55,2.25 if studio else 1.78) for i,x in enumerate(xs)]
                for x in (-10.50,10.50):
                    if lev==0 and side_index==0 and studio:hs.append(hole('Core entrance door '+str(x),x,z,1.25,2.3))
                    else:hs.append(hole(f'Core sash {side_index} {lev} {x}',x,z+.9,.72,1.45))
                if not studio:
                    if lev==0:hs.append(hole('Main entrance door' if side_index==0 else 'Rear garden door',0,z,1.60,2.4))
                    elif side_index==0:hs.append(hole('Centre lounge sash '+str(lev),0,z+.75,.85,1.78))
            else:
                ys=(-3.8,3.8) if studio else (-4.2,0,4.2)
                hs += [hole(f'End circulation sash {side_index} {lev} {j}',y,z+.85,.7 if studio else 1.1,1.5) for j,y in enumerate(ys)]
        span=24 if side_index%2==0 else d-.46
        f.wall('Complete apartment carrier',-span/2,span/2,low,walltop,depth=.23,holes=hs)
        for h in hs:
            if 'entrance door' in h['id'].lower() or 'garden door' in h['id'].lower():glazing(f,h,door=True,cols=2 if h['w']>1.3 else 1)
            else:
                aperture(f,h)
                if studio and h['id'].startswith('Apartment window'):
                    f.part('Studio low window transom',h['u'],.128,h['z']+h['h']*.28,h['w']-.13,.085,.055,'trim','source window divisions',0)
        frontage[side_index]=hs
        if side_index%2==0:
            accent=C.Face(f.p(0,-.025,0),f.t,f.n,kind+' facade accents')
            if studio:
                for j,(a,b) in enumerate(((-9,-3),(-3,3),(3,9))):
                    accent.wall('Source studio colour bay',a,b,low,walltop,depth=.035,holes=hs,role='olive' if j==1 else 'ochre')
            else:
                for x,w in ((-10.5,1.50),(0,2.10),(10.5,1.50)):
                    accent.wall('Cedar vertical accent',x-w/2,x+w/2,low,walltop,depth=.035,holes=hs,role='timber')
                    # Individual timber joints remain cut around every window.
                    sub=C.Face(accent.p(x,-.004,0),accent.t,accent.n,'Cedar joints')
                    local=[{**h,'u':h['u']-x,'w':h['w']+.14,'z':h['z']-.10,'h':h['h']+.20} for h in hs]
                    vertical_cladding(sub,w,low,walltop,local,spacing=.13,role='joint')
        if studio:
            for lev in range(1,levels):f.part('Module floor joint',0,-.05 if side_index%2==0 else -.004,low+lev*step,span,.014,.025,'joint','rainscreen joints',0)
    for lev in range(levels):
        z=low+lev*step
        if lev:
            slab=C.box('Apartment occupied floor',(0,0,z-.11),(23.56,d-.44,.22),'floor','floors')
            for x in (-10.5,10.5):C.cut_box(slab,'Stair floor aperture',(x,-2.06,z-.11),(1.18,4.68,.50))
        for side in (-1,1):
            f=C.Face((0,side*1.2,0),(1,0,0),(0,side,0),'Shared corridor')
            xs=(-6,0,6) if studio else (-5,5)
            doors=[hole('Apartment entry '+str(j),x,z,.93,2.2) for j,x in enumerate(xs)]
            # Centre axis is an actual passage on the ground, and upper front lounge.
            if not studio and (side==-1 or lev==0):doors.append(hole('Centre passage',0,z,2.10,3.0))
            f.wall('Corridor envelope',-9,9,z,z+3.08,depth=.12,role='interior',holes=doors)
            for h in doors:
                if h['id']!='Centre passage':f.door(h['id'],h['u'],z,.93,2.2,role='timber',panels=1)
            suite_d=d/2-1.43
            if studio:
                centres=(-6,0,6);width=5.88
                for x in (-3,3):C.box('Studio party wall',(x,side*(1.2+suite_d/2),z+1.54),(.12,suite_d,3.08),'interior','partitions')
            else:
                centre_strip=1.11 if (side==-1 or lev==0) else .06
                width=9-centre_strip-.12;centres=(-(9+centre_strip)/2,(9+centre_strip)/2)
                for x in ((-1.11,1.11) if centre_strip>1 else (0,)):
                    C.box('Apartment centre separation',(x,side*(1.2+suite_d/2),z+1.54),(.12,suite_d,3.08),'interior','partitions')
            for x in centres:apartment_room(x,side,z,width,suite_d,studio)
        for x in (-9,9):
            f=C.Face((x,0,0),(0,1,0),(1 if x>0 else -1,0,0),'Enclosed end stair')
            internal_wall(f,'Circulation core separator',-d/2+.23,d/2-.23,z,z+3.08,[hole('Core corridor door',.78,z,1.15,2.25)])
        if lev<levels-1:
            for x in (-10.5,10.5):gallery_stair(x,-4.40,z,z+step,width=1.10)
        if lev:
            for x in (-10.5,10.5):
                for dx in (-.68,.68):seated_guard('Stairwell slab guard',(x+dx,-4.49,z),(x+dx,.37,z))
                seated_guard('Stairwell lower end',(x-.68,-4.49,z),(x+.68,-4.49,z),end_anchors=False)
        # Reserved lift enclosure: physical shaft and closed doors, no claim of operation.
        lift=C.Face((10.5,3.5,0),(1,0,0),(0,1,0),'Reserved lift')
        lh=[hole('Lift landing door',0,z,1.0,2.15)]
        lift.wall('Lift front wall',-.95,.95,z,z+3.08,depth=.12,holes=lh,role='interior')
        lift.door('Lift landing door',0,z,1.0,2.15,role='trim',panels=2)
        for xx in (9.61,11.39):C.box('Lift shaft side',(xx,4.46,z+1.54),(.12,1.9,3.08),'interior','reserved lift shaft')
        C.box('Lift shaft rear',(10.5,5.35,z+1.54),(1.9,.12,3.08),'interior','reserved lift shaft')
        for x in (-10.5,10.5):C.qa_room_light('Stair corridor',(x,.7,z+2.9),100,1.4)
        for x in (-6,0,6):C.qa_room_light('Common hall',(x,0,z+2.95),100,1.3)
    C.box('Top occupied ceiling',(0,0,walltop-.06),(23.56,d-.44,.12),'interior','ceiling')
    flat_roof(kind+' closed roof',0,0,24,d,roofz,parapet=.25)
    entry_xs=(-10.5,10.5) if studio else (0,)
    for x in entry_xs:
        C.box('Apartment entry landing',(x,-d/2-.75,.075),(2.5,1.6,.15),'foundation','entry')
        steps('Entry step',x,-d/2-1.55,2.5,.15,n=1,run=.35,role='foundation')
        if x<0 or not studio:canopy('Apartment entrance',x,-d/2-.65,2.80,2.45,1.5,posts=True)
    if not studio:
        C.box('Rear garden entrance landing',(0,d/2+.60,.075),(2.2,1.3,.15),'foundation','entry')
    for x in range(-8,9,2):
        if all(abs(x-entry)>1.5 for entry in entry_xs):shrub(x,-d/2-.8,0,.46)
    C.CONTACTS.append(dict(name='Apartment programme',storeys=levels,units=24 if studio else 12,units_per_floor=6 if studio else 4,permanent_transport_chassis=False,accessibility_certified=False,lift='reserved enclosed shaft only',construction='authored modular intent' if studio else 'authored conventional assembly'))

def aspen():apartment('aspen')
def switchback():apartment('switchback')

DETAILS={
 'juniper':[
  ('facade_close',(7.5,-19,5),(7.5,-11,1.8)),('architecture_close',(10,-15,3.2),(8.8,-11.5,1.6)),
  ('glass_close',(6,-14,2),(6.3,-10.9,1.4)),('roof_contact',(13,-12,7),(10.8,-10.5,3.3)),
  ('side_projection',(16,-13,7),(10.8,-7.5,2.8)),
  ('courtyard',(0,-7,4),(0,3,1)),('private_patio',(17,-12,5),(12.5,-7.5,.3)),
  ('interior',(10.35,-10.45,2.3),(8,-8.4,1.1)),('bedroom',(4.65,-6.35,2.6),(5.95,-5.3,.8)),
  ('bathroom',(10.15,-6.6,2.5),(9,-5,.7))],
 'stackyard':[
  ('facade_close',(4,-21,7),(0,-5.5,3.5)),('architecture_close',(-7,-11,2.7),(-9.1,-5.6,1.5)),
  ('glass_close',(1,-9,2),(.8,-5.45,1.5)),('roof_contact',(14,-13,10),(10,-7.3,6.7)),
  ('side_projection',(19,-12,7),(10.5,-1,3.5)),
  ('stairs',(14,-14,3),(11.16,-8,3)),('upper_landing',(11.25,-7.0,5.05),(5,-6.4,3.6)),
  ('stair_contact',(13,-9,5.0),(11.16,-7.5,3.3)),('interior',(-2.9,-4.8,2.3),(.8,-1.7,1.1)),
  ('bedroom',(-2.8,1.5,2.7),(-1.6,3.6,.7)),('bathroom',(-1.60,-.80,2.65),(-2.2,.3,.6))]
}

for kind,d,levels in (('aspen',13,3),('switchback',14,4)):
    DETAILS[kind]=[
      ('facade_close',(4,-24,10),(0,-d/2,5)),('architecture_close',(-7,-11,3.8),(-10.5 if kind=='switchback' else 0,-d/2,1.7)),
      ('glass_close',(-6,-d/2-3,2),(-6,-d/2+.1,1.5)),('roof_contact',(17,-14,levels*3.3+4),(11,-d/2,levels*3.3)),
      ('side_projection',(20,-5,9),(12,0,6)),('interior',(-8.6,-3.8,2.5),(-4.8,-4,1.2)),
      ('bedroom',(-4.8,-3.4,2.5) if kind=='switchback' else (-1.55,-3.52,2.5),(-4.26,-5.37,.8) if kind=='switchback' else (-2.82,-4.77,.8)),
      ('bathroom',(-4.9,-3,2.4) if kind=='switchback' else (-4.05,-2.95,2.4),(-4.1,-1.8,.7) if kind=='switchback' else (-2.3,-1.8,.7)),
      ('corridor',(-7.8,.2,2), (7.5,.2,1.4)),('stairs',(-10.6,-5.6,1.9),(-10.5,-1.1,3.0)),
      ('upper_landing',(-11.6,1.0,5.9),(-10.45,-1.2,3.45)),('stair_contact',(-11.6,.9,4.0),(-10.5,.15,3.45)),
      ('lift',(10.5,.55,2),(10.5,3.5,1.3)),
      ('stair_headroom',(-10.5,-3.4,1.95),(-10.5,-.3,3.95))]
