"""Source-locked low U-shaped roadside motor court; no surrounding road mesh."""
import sys, math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import support as S
C=S.C
SLUG='highway-motor-hotel';PARENT='highway_motor_hotel';VARIANT='hotel_roadside_motel';INDEX=0
TITLE='Classic courtyard motel';WIDTH=24;DEPTH=38;HEIGHT=7.3;STOREYS=1
PALETTE=dict(wall=(.70,.66,.52),mortar=(.56,.51,.40),trim=(.77,.73,.60),coping=(.53,.53,.45),roof=(.24,.25,.23),
 foundation=(.43,.43,.37),glass=(.27,.34,.31),hardware=(.14,.16,.14),timber=(.53,.45,.32),
 interior=(.66,.60,.49),floor=(.37,.31,.24),red=(.56,.17,.105),teal=(.12,.34,.31),sign=(.10,.25,.25))

def manifest(v):
    m = S.prework(sys.modules[__name__],v,dict(width=WIDTH,depth=DEPTH,height=HEIGHT),
        dict(front='Single-storey cream U-shaped motor court; left-front glazed office, paired alternating red/teal room doors, windows and under-window AC units; large roadside arrow sign.',
             oblique='Two parallel shallow gabled wings connected by rear guest wing; open vehicle court. Narrow concrete room access strips.',
             top='U-shaped continuous roof with two long longitudinal ridges joining one rear cross ridge. Top shows a second small sign not corroborated elsewhere; omit it.',
             roof='One closed U-shaped shallow roof, with shared rear hip/ridge junction nodes, cream fascia and front gable boarding.',
             programme='One-storey motor inn, court-facing guest rooms and glazed reception office.'),
        ['Metric dimensions inferred, not surveyed. Roof plan measures about 640:445 depth-to-width in the top source; courtyard clear width about 170:445. The model uses a 24m transverse body, 34m depth and 9.2m court.',
         'Room partitions, rear escape door and left outside windows are inferred. The source-visible right outside wall remains blank above its stripes.',
         'Vehicles, road, tall poplars and grass apron are context and excluded. Parking court is left open for student site design.',
         'Signs are constructed lettering and panel geometry; no photographic billboard.'],
        ['Each wing foundation contacts grade.','All room doors meet a connected raised access strip.',
         'Back roof junctions share actual ridge and valley vertices.','Pylon posts meet isolated footings.'],[
        dict(name='facade_close',location=(-1,-19,4.5),target=(-4.6,-9,1.6),whole=False),
        dict(name='architecture_close',location=(0,-17,6),target=(0,4,2.0),whole=False),
        dict(name='glass_close',location=(-7.3,-20,2),target=(-7.2,-15.8,1.7),whole=False,lens=45),
        dict(name='roof_contact',location=(-22,25,15),target=(-9,12,3.5),whole=False),
        dict(name='sign_contact',location=(20,-31,8),target=(8.3,-19,4.2),whole=False)])
    for camera in m['camera_roster']:
        if camera['name'] in ('front_corner','aerial'):
            camera['location']=(abs(camera['location'][0]),*camera['location'][1:])
    return m

def gable(name,x0,x1,y0,y1,eave=3.28,rise=1.25,axis='y'):
    if axis=='y':
        return C.mesh(name,[(x0,y0,eave),(x1,y0,eave),((x0+x1)/2,y0,eave+rise),
            (x0,y1,eave),(x1,y1,eave),((x0+x1)/2,y1,eave+rise)],
            [(0,2,1),(3,4,5),(0,1,4,3),(0,3,5,2),(1,2,5,4)],'roof','roof')
    return C.mesh(name,[(x0,y0,eave),(x0,y1,eave),(x0,(y0+y1)/2,eave+rise),
        (x1,y0,eave),(x1,y1,eave),(x1,(y0+y1)/2,eave+rise)],
        [(0,1,2),(3,5,4),(0,3,4,1),(0,2,5,3),(1,4,5,2)],'roof','roof')

def guest_face(face,length,count,office=False):
    hs=[];pitch=length/count
    for i in range(count):
        base=i*pitch
        isoffice=office and i==0
        hs.extend([dict(id=f'room {i} window',u=base+pitch*(.30 if i%2==0 else .70),z=.35 if isoffice else 1.05,w=1.9 if isoffice else 1.45,h=2.50 if isoffice else 1.48,office=isoffice),
                   dict(id=f'room {i} door',u=base+pitch*(.78 if i%2==0 else .22),z=.13,w=.89,h=2.22,door=True,glazed=isoffice)])
    face.wall('Court-facing guest wall',0,length,.12,3.27,holes=hs)
    for i,h in enumerate(hs):
        if h.get('door'):face.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='red' if (i//2)%2 else 'teal',panels=1,glazed=h.get('glazed',False))
        else:
            face.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,curtain=True)
            if h.get('office'):continue
            face.part('Guestroom packaged AC',h['u'],-.10,.65,.83,.22,.41,'coping','AC',.004)
            for k in range(5):face.part('AC open grille relief',h['u'],-.216,.49+k*.068,.71,.015,.025,'hardware','AC',0)
    face.part('Cream continuous eave fascia',length/2,-.38,3.20,length,.14,.22,'trim','fascia',0)

def text_object(text,loc,size,role):
    import bpy
    bpy.ops.object.text_add(location=loc,rotation=(math.pi/2,0,0))
    obj=bpy.context.object;obj.data.body=text;obj.data.align_x='CENTER';obj.data.size=size;obj.data.extrude=.012
    obj.data.materials.append(C.MATS[role]);bpy.ops.object.convert(target='MESH');C.tag(obj,role,'pylon lettering')

def build():
    for x in (-8.3,8.3):
        C.box('Wing foundation',(x,1,.06),(7.4,34,.12),'foundation','base',0)
        C.box('Wing floor',(x,1,.14),(7.0,33.6,.10),'floor','floor',0)
        C.box('Wing ceiling',(x,1,3.15),(7.0,33.6,.14),'interior','ceiling',0)
    C.box('Rear foundation',(0,15,.06),(9.2,6,.12),'foundation','base',0)
    C.box('Rear floor',(0,15,.14),(9.2,5.6,.10),'floor','floor',0)
    C.box('Rear ceiling',(0,15,3.15),(9.2,5.6,.14),'interior','ceiling',0)
    left=C.Face((-4.6,-16,0),(0,1,0),(-1,0,0),'left guest wing')
    right=C.Face((4.6,12,0),(0,-1,0),(1,0,0),'right guest wing')
    rear=C.Face((-4.6,12,0),(1,0,0),(0,1,0),'rear guest wing')
    guest_face(left,28,7,office=True);guest_face(right,28,7);guest_face(rear,9.2,3)
    for label,x,sgn in [('left outside',-12,1),('right outside',12,-1)]:
        f=C.Face((x,-16,0),(0,1,0),(sgn,0,0),label)
        hs=[dict(id=label+str(i),u=3+i*5.4,z=1.4,w=.8,h=.85) for i in range(6)] if x<0 else []
        S.openings(f,34,.12,3.27,hs,joints=False)
        for z,role in [(1.08,'teal'),(1.38,'red')]:f.part('Continuous vintage stripe',17,-.013,z,34,.023,.18,role,'stripe',0)
    back=C.Face((12,18,0),(-1,0,0),(0,-1,0),'inferred back')
    hs=[dict(id='rear secondary door',u=12,z=.12,w=.95,h=2.2,door=True)]
    hs += [dict(id=f'rear light {i}',u=u,z=1.40,w=.9,h=.8) for i,u in enumerate((3,8,16,21))]
    S.openings(back,24,.12,3.27,hs,joints=False)
    for x,label in [(-12,'left office'),(4.6,'right gable')]:
        f=C.Face((x,-16,0),(1,0,0),(0,1,0),label)
        hs=[dict(id='office glazing',u=4.8,z=.45,w=4.0,h=2.25)] if x<0 else []
        S.openings(f,7.4,.12,3.28,hs,joints=False)
        C.prism(label+' closed triangular gable',[(x,3.27),(x+7.4,3.27),(x+3.7,4.40)],'y',-16.50,-15.85,'trim','gable')
        for i in range(27):
            u=(i+.5)*7.4/27;top=3.27+1.13*(1-abs(u-3.7)/3.7)
            C.box('Gable board joint',(x+u,-16.508,(top+3.27)/2),(.012,.012,max(.015,top-3.27)),'mortar','gable boarding',0)
        if x>0:
            for z,role in [(1.08,'teal'),(1.38,'red')]:f.part('Front stripe',3.7,-.014,z,7.4,.028,.18,role,'stripe',0)
    # One explicit weathering graph: no ridge continues past the shared rear node.
    vs=[(-12.38,-16.48,3.28),(-8.3,-16.48,4.53),(-4.22,-16.48,3.28),
        (-4.22,11.62,3.28),(-8.3,15,4.53),(-12.38,18.38,3.28),
        (12.38,-16.48,3.28),(8.3,-16.48,4.53),(4.22,-16.48,3.28),
        (4.22,11.62,3.28),(8.3,15,4.53),(12.38,18.38,3.28)]
    C.mesh('Closed U roof with shared hip nodes',vs,[(0,1,4,5),(1,2,3,4),(3,9,10,4),
        (5,4,10,11),(6,11,10,7),(7,10,9,8),(0,2,1),(6,7,8),(0,5,11,6,8,9,3,2)],'roof','roof')
    for x in (-12.36,12.36):C.box('Outer eave fascia',(x,1,3.22),(.16,34.9,.22),'trim','fascia',0)
    for x in (-8.3,8.3):
        for sign in (-1,1):C.beam('Front gable fascia',(x+sign*4.06,-16.50,3.26),(x,-16.50,4.55),.15,.16,'trim','roof edge')
    # Connected narrow access strips, not a site-wide ground replacement apron.
    for x in (-4.1,4.1):C.box('Court room access strip',(x,-2,.065),(1.0,28,.13),'foundation','access',0)
    C.box('Rear connected access',(0,11.5,.065),(9.2,1,.13),'foundation','access',0)
    for x in (-8.3,8.3):
        for i in range(7):
            y=-14+i*4
            C.box('Guestroom partition',(x,y+1.85,1.65),(6.95,.13,3.02),'interior','occupied room',0)
            if x<0 and i==0:
                C.box('Reception counter',(-8.3,-14,.70),(2.6,.65,1.2),'timber','reception',.015)
                C.box('Reception worktop',(-8.3,-14,1.33),(2.7,.72,.08),'trim','reception',.005)
                C.qa_room_light('reception',(-8.3,-14,2.85),75,2)
                continue
            C.box('Bed plinth',(x,y,.40),(1.75,2.0,.45),'timber','guestroom bed',.01)
            C.box('Bed mattress',(x,y,.68),(1.72,1.98,.22),'interior','guestroom bed',.02)
            C.box('Bed pillow',(x,y+.65,.84),(1.35,.40,.15),'trim','guestroom bed',.02)
            C.qa_room_light('guest room',(x,y,2.85),50,1.8)
    # Exact sign hierarchy, vector lettering, supported rather than floating.
    before_sign={o.name for o in C.objects()}
    for x in (8.2,13.8):
        C.box('Pylon footing',(x,-19,.10),(.58,.58,.20),'foundation','sign foundation',0)
        C.rod('Pylon post',(x,-19,.10),(x,-19,6.45),.11,'trim','sign support')
    C.prism('Stepped teal pylon panel',[(7.65,3.97),(14.35,3.97),(14.35,5.4),(13.95,5.4),(13.95,5.72),(7.65,5.72)],'y',-19.13,-18.87,'sign','sign')
    C.prism('Sloping upper dark panel',[(7.65,5.60),(13.4,5.60),(13.15,6.30),(7.65,6.30)],'y',-19.13,-18.87,'hardware','sign')
    C.prism('Slender left pylon blade',[(7.45,3.35),(7.13,6.82),(7.50,6.58),(7.82,6.89),(7.75,3.35)],'y',-19.17,-18.83,'trim','sign blade')
    text_object('MOTEL',(11,-19.15,4.08),1.65,'red')
    text_object('MOTOR HOTEL',(11,-19.155,5.33),.50,'trim')
    text_object('HIGHWAY',(10.65,-19.15,5.69),.73,'red')
    C.prism('Directional arrow',[(7.8,6.42),(13.7,6.42),(13.7,6.12),(14.7,6.72),(13.7,7.22),(13.7,6.92),(7.8,6.92)],'y',-19.13,-18.85,'trim','sign arrow')
    for i in range(30):C.rod('Arrow bulb',(8+i*.19,-19.17,6.68),(8+i*.19,-19.20,6.68),.032,'timber','sign bulbs',8)
    for obj in C.objects():
        if obj.name not in before_sign:obj.location.x-=2.7

if __name__=='__main__':S.run(sys.modules[__name__])
