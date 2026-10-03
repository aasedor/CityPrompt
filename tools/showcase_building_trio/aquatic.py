"""Source-shaped planted glulam vault with an inhabited aquatic interior."""
import math
import random

def build(B):
    C=B.C;box=B.box;w=38;d=56
    box('continuous foundation',(0,0,.10),(w,d,.20),'foundation','base')
    box('pool deck',(0,0,.23),(37.6,55.6,.06),'floor','deck')
    def roof(x):return 6.9+9.4*max(0,math.sin(math.pi*(x+10)/28))**.92
    xs=[-10+28*i/80 for i in range(81)]
    # The three locked views show a substantial planted service block, twelve
    # discrete lights, a west-shoulder strip and one grouped east-slope PV run.
    lights=[(x,y,2.2,2.2) for x in (0,7) for y in (-18,-6,6,18)]
    wing_lights=[(-14.5,y,2.2,2.2) for y in (-18,-6,6,18)]
    strip=(-7,-4.8)
    pv_runs=((-25,-12),(-10.8,13),(14.2,25))
    # Lower service wing is a complete enclosing volume; timber boards are
    # physical, with a repeated schedule that continues around the rear.
    for face,L in zip(B.faces(w,d),(w,d,w,d)):
        if face.label=='front':continue
        top=7.0 if face.label!='left' else 12.0
        holes=[]
        if face.label=='right':holes=[dict(id=f'east pool glazing {i}',u=3+i*5.0,z=.4,w=4.35,h=6.15,cols=3,rows=3) for i in range(11)]
        elif face.label=='rear':holes=[dict(id=f'rear glazing {i}',u=3+i*4.0,z=.4,w=3.0,h=5.9,cols=2,rows=3) for i in range(9)]
        else:holes=[dict(id=f'service clerestory {i}',u=3+i*5,z=8.3,w=3.5,h=2.8,cols=2) for i in range(11)]
        B.open_wall(face,L,.26,top,holes,role='cladding' if face.label=='left' else 'timber')
        for u in [i*.25 for i in range(int(L/.25)+1)]:
            # Boards only where the carrier exists; windows never get painted over.
            for z0,z1 in ((.28,.4),(6.65,top)) if face.label=='right' else ((.28,.4),):
                if z1>z0:face.part('timber board joint',u,-.02,(z0+z1)/2,.016,.012,z1-z0,'trim','cladding joints',0)
            if face.label=='left':face.part('charcoal service board seam',u,-.012,4.34,.018,.02,7.88,'hardware','cladding joints',0)
    B.open_wall(C.Face((-19,-28,0),(1,0,0),(0,1,0),'service front'),9,.26,12,
                [dict(id=f'wing front window {u} {z}',u=u,z=z,w=1.0,h=2.5,cols=1) for u in (2,6) for z in (1,6)],role='cladding')
    box('service wing rear upper closure',(-14.5,27.84,9.5),(9,.32,5),'cladding','service wing')
    box('service wing upper inner closure',(-10.08,0,9.50),(.16,56,5.22),'cladding','service wing')
    box('east eave closed roof',(18.5,0,7.0),(1.1,56,.24),'roof','roof envelope')
    box('east front closure',(18.5,-27.84,3.62),(1,.32,6.72),'timber','envelope')
    # Front and rear arched glulam structure, plus an honest full-span interior.
    for y in [-28+i*7 for i in range(9)]:
        B.curve_beam('glulam vault rib',[(x,y,roof(x)-.6) for x in xs],.30,.60,'timber','vault structure')
        for x in (-10,18):box('glulam column',(x,y,(roof(x)-.6)/2),(.38,.48,roof(x)-.6),'timber','vault structure')
    for x in [-9+i*2.0 for i in range(14)]:C.beam('roof longitudinal purlin',(x,-28,roof(x)-.48),(x,28,roof(x)-.48),.16,.22,'timber','roof purlins')
    # The photograph's entrance arch descends to ground independently of the
    # high side eaves. It frames the full glazing, rather than ending in midair.
    arch=[(-10+28*i/80,-28.02,.42+15.2*math.sqrt(max(0,1-((-10+28*i/80-4)/14)**2))) for i in range(81)]
    B.curve_beam('grounded monumental entry arch',arch,.56,.80,'timber','entrance arch')
    for x in (-10,18):box('entry arch stone foot',(x,-28.02,.25),(.85,.95,.5),'stone','entrance arch')
    def roof_cells(xcuts, holes, height, label, slot=None):
        xc=sorted(set(xcuts+[v for x,y,ww,dd in holes for v in (x-ww/2,x+ww/2)]+(list(slot) if slot else [])))
        yc=sorted({-28,28,*[v for x,y,ww,dd in holes for v in (y-dd/2,y+dd/2)]})
        for a,b in zip(xc,xc[1:]):
            for c,d in zip(yc,yc[1:]):
                mx,my=(a+b)/2,(c+d)/2
                if any(abs(mx-x)<ww/2 and abs(my-y)<dd/2 for x,y,ww,dd in holes):continue
                glazing=slot and slot[0]<mx<slot[1]
                C.solid_surface(label+' strip glass' if glazing else label+' planted deck',
                    [(a,c,height(a)),(b,c,height(b)),(b,d,height(b)),(a,d,height(a))],
                    .05 if glazing else .24,'glass' if glazing else 'roof','roof envelope')
        for i,(x,y,ww,dd) in enumerate(holes):
            a,b=x-ww/2,x+ww/2;c,d=y-dd/2,y+dd/2
            z=max(height(a),height(b))+.20
            # Open curb sides support level optical glass above a real hole.
            for xx in (a,b):
                C.prism(label+' skylight curb',[(c,height(xx)-.20),(d,height(xx)-.20),(d,z),(c,z)],'x',xx-.05,xx+.05,'timber','rooflight')
            for yy in (c,d):
                C.prism(label+' skylight end curb',[(a,height(a)-.20),(b,height(b)-.20),(b,z),(a,z)],'y',yy-.05,yy+.05,'timber','rooflight')
            box(label+f' skylight optical pane {i}',(x,y,z+.025),(ww,dd,.05),'glass','rooflight')
            for xx in (a,b):box(label+' light cap rail',(xx,y,z+.06),(.09,dd+.12,.09),'hardware','rooflight')
            for yy in (c,d):box(label+' light cap rail',(x,yy,z+.06),(ww,.09,.09),'hardware','rooflight')
            box(label+' skylight glazing bar',(x,y,z+.065),(.06,dd,.08),'hardware','rooflight')
    roof_cells(xs,lights,roof,'vault',strip)
    roof_cells([-19,-10],wing_lights,lambda x:12.1,'service wing')
    for x in strip:C.beam('rooflight seated curb',(x,-28,roof(x)+.03),(x,28,roof(x)+.03),.10,.20,'hardware','rooflight')
    for y in range(-28,29,2):C.beam('rooflight transom',(strip[0],y,roof(strip[0])+.05),(strip[1],y,roof(strip[1])+.05),.07,.08,'hardware','rooflight')
    # End glazing is trimmed to the constructed arch. Ground doors live in this
    # same transparent facade plane, with clear circulation beyond them.
    for y in (-24,27.65):
        for i in range(14):
            a=-10+i*2;b=a+2;za=roof(a)-.24;zb=roof(b)-.24
            C.prism('arch end optical panel',[(a,.28),(b,.28),(b,zb),(a,za)],'y',y-.025,y+.025,'glass','arched gable glazing')
            C.beam('glulam gable mullion',(a,y,.26),(a,y,za),.13,.16,'timber','gable frame')
        for z in (3.0,6.4,9.8,13.2):
            inside=[x for x in xs if roof(x)>z+.5]
            C.beam('gable horizontal transom',(min(inside),y,z),(max(inside),y,z),.14,.18,'timber','gable frame')
    # Entrance doors are separately framed and leaf-sized, with seating outside
    # the entrance line; the photo's deep timber canopy carries back to the arch.
    for x in (2.9,5.1):
        for dx in (-.95,.95):box('entry door stile',(x+dx,-24.10,1.62),(.08,.12,2.7),'hardware','entrance')
        box('entry door head',(x,-24.10,2.98),(1.98,.12,.10),'hardware','entrance')
        C.rod('door pull',(x+.65,-24.22,1.1),(x+.65,-24.22,1.9),.023,'hardware','entrance')
    box('recessed entrance canopy',(4,-25.0,3.5),(5.0,2.0,.25),'timber','entrance')
    box('entrance canopy metal cap',(4,-25.0,3.65),(5.1,2.08,.06),'hardware','entrance')
    wall_rng=random.Random(401)
    for x in (-5,12.5):
        box('entrance planted flank backing',(x,-24.14,1.75),(5.0,.24,3.0),'cladding','entrance')
        vv=[];ff=[]
        for i in range(2300):
            xx=x+wall_rng.uniform(-2.42,2.42);zz=wall_rng.uniform(.33,3.18)
            yy=-24.33-wall_rng.uniform(0,.13);r=wall_rng.uniform(.045,.12);n=len(vv)
            vv.extend([(xx-r,yy,zz),(xx,yy-.08,zz+r),(xx+r,yy,zz),(xx,yy+.02,zz-r)])
            ff.extend([(n,n+1,n+2),(n,n+2,n+3)])
        C.mesh('native entrance living wall',vv,ff,'leaf','entrance planting')
    # The porch is genuinely four metres deep; a timber deck, seats and
    # enclosed sides connect the outside arch to the recessed door plane.
    box('deep porch timber deck',(4,-26,.30),(27.5,3.9,.08),'timber','porch')
    for x in (-5.5,13.5):
        box('porch bench seat',(x,-26,.78),(2.4,.56,.12),'timber','porch furniture')
        for dx in (-.9,.9):box('porch bench foot',(x+dx,-26,.54),(.14,.45,.42),'hardware','porch furniture')
    for y in (-13,13):
        # Tall louver shafts are independently supported, capped and perforated.
        box('ventilation shaft',(18.35,y,6.0),(1.2,1.8,12),'hardware','vent towers')
        for z in [i*.22+.22 for i in range(54)]:box('ventilation timber louvre',(19.02,y,z),(.11,1.85,.11),'timber','vent towers')
        box('vent tower cap',(18.35,y,12.1),(1.45,2.05,.18),'hardware','vent towers')
    # Pool programme: correctly sized lane basin, continuous deck, lane ropes,
    # starting blocks, lifesaving station, showers and changing-room partitions.
    px,py=0,0;pw,pd=16,25
    box('pool ceramic basin',(px,py,.285),(pw+.5,pd+.5,.05),'white','pool basin')
    box('water plane',(px,py,.32),(pw,pd,.035),'water','pool water')
    for x in (-8.18,8.18):box('pool stone coping',(x,0,.39),(.35,25.7,.18),'stone','pool coping')
    for y in (-12.68,12.68):box('pool stone coping',(0,y,.39),(16,.35,.18),'stone','pool coping')
    for i in range(1,8):
        x=-8+i*2
        C.rod('lane rope',(x,-12.4,.365),(x,12.4,.365),.028,'white','pool lane lines',8)
        for j in range(0,50,2):box('lane rope float',(x,-12.25+j*.5,.37),(.10,.35,.08),'bronze','pool lane floats')
    for i in range(8):
        x=-7+i*2
        box('starting block post',(x,13.4,.55),(.18,.25,.55),'hardware','pool blocks')
        box('starting block platform',(x,13.4,.85),(.62,.62,.10),'white','pool blocks')
        for y in (-11,11):box('underwater lane marker',(x,y,.343),(1.15,.08,.006),'hardware','pool markings')
    for y in (-17,-9,-1,7,15):
        box('pool bench',(12.6,y,.72),(2.1,.55,.12),'timber','pool furniture')
        for x in (11.9,13.3):box('pool bench leg',(x,y,.47),(.12,.43,.41),'hardware','pool furniture')
    for y in (-14,-6,2,10,18):box('changing room partition',(-14.5,y,2.0),(8.0,.16,3.5),'interior','service program')
    for x in (-14,12):
        for y in (-21,21):B.table(x,y,.26)
    # Source-specific planted roof: dense low foliage, protected PV strips and
    # rooflights; deterministic mesh, no distant textured lawn pretending grass.
    rng=random.Random(279);verts=[];polys=[]
    for _ in range(29000):
        x=rng.uniform(-18.8,17.8);y=rng.uniform(-27.8,27.8)
        wing=x<-10;holes=wing_lights if wing else lights
        if any(abs(x-hx)<hw/2+.15 and abs(y-hy)<hd/2+.15 for hx,hy,hw,hd in holes):continue
        if not wing and (strip[0]-.15<x<strip[1]+.15 or (12.0<x<14.8 and any(lo-.1<y<hi+.1 for lo,hi in pv_runs))):continue
        z=(12.1 if wing else roof(x))+.02;h=rng.uniform(.10,.28);ww=rng.uniform(.035,.095);n=len(verts)
        verts.extend([(x-ww,y,z),(x+ww,y,z),(x+.025,y+.025,z+h),(x,y-ww,z),(x,y+ww,z),(x+.04,y,z+h*.8)])
        polys.extend([(n,n+1,n+2),(n+3,n+4,n+5)])
    C.mesh('native roof meadow',verts,polys,'leaf','living roof')
    a,b=12.2,14.6
    for lo,hi in pv_runs:
        count=math.ceil((hi-lo)/1.9);pitch=(hi-lo)/count
        for j in range(count):
            y=lo+j*pitch;end=y+pitch-.06
            C.solid_surface('photovoltaic panel',[(a,y,roof(a)+.20),(b,y,roof(b)+.20),(b,end,roof(b)+.20),(a,end,roof(a)+.20)],.045,'solar','solar arrays')
            for xx in (a,b):C.beam('solar panel rail',(xx,y,roof(xx)+.20),(xx,end,roof(xx)+.20),.03,.035,'hardware','solar arrays')
    B.label('AQUATIC CENTRE',(4,-26.07,3.50),.30)
    for y in (-16,0,16):C.qa_room_light('pool daylight',(0,y,10),900,8)
    C.CONTACTS.extend([dict(name='glulam vault',status='28m vault beside 9m planted wing; 8 vault and 4 wing rooflights with real roof openings; shoulder strip, one east-slope PV run in three groups, two louvre towers and 4m deep entrance porch.'),
        dict(name='aquatic program',status='Eight pool lanes, starting blocks, full deck perimeter, changing-room wing and bench seating.')])
