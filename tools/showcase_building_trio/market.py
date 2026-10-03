"""A complete iron market hall, measured from its three locked views."""
import math

def build(B):
    C=B.C;box=B.box
    # Ground is a single grounded, inset market floor; no private city context.
    box('continuous market foundation',(0,0,.10),(34,48,.20),'foundation','base')
    box('brick market paving',(0,0,.23),(33.6,47.6,.06),'floor','base')
    for y in range(-23,24):
        box('paving joint',(0,y,.266),(33.5,.014,.008),'stone','paving joints')
    # Whole masonry side and rear elevations, with real through openings.
    sides=B.faces(34,48)
    for face in (sides[1],sides[3]):
        holes=[dict(id=f'{face.label} arched-bay {i}',u=3+i*5.25,z=1.0,w=2.55,h=5.8,cols=2,rows=4) for i in range(9) if i!=4]
        holes.append(dict(id=face.label+' side entrance',u=24,z=.26,w=5,h=7.04,cols=3,rows=3,door=True))
        B.open_wall(face,48,.26,8.5,holes)
        for u in (20.65,27.35):face.part('side portal masonry pier',u,-.20,4.3,.64,.85,8.6,'stone','side entrance',0)
        # The arch ring and masonry above it shape the real central bay.
        for i in range(32):
            a=math.pi*i/32;b=math.pi*(i+1)/32
            p=lambda t,r:face.p(24+r*math.cos(t),-.28,4.8+r*math.sin(t))
            C.beam('side entrance stone arch',p(a,2.7),p(b,2.7),.40,.60,'stone','side entrance')
        for i in range(24):
            u=21.5+(i+.5)*5/24;z=4.8+math.sqrt(max(0,6.25-(u-24)**2))
            face.part('arch masonry spandrel',u,-.01,(z+8.5)/2,5/24,.40,8.5-z,'wall','side entrance',0)
        verts=[face.p(20.5,-.24,8.5),face.p(27.5,-.24,8.5),face.p(24,-.24,12.8)]
        C.solid_surface('side entrance masonry gable',verts,.35,'wall','side entrance')
        for u in (20.5,27.5):C.beam('side gable stone coping',face.p(u,-.32,8.6),face.p(24,-.32,12.9),.24,.32,'stone','side entrance')
        for i in range(10):
            face.part('brick pilaster',.4+i*5.24,-.06,4.25,.42,.42,8,'wall','masonry piers',0)
        for z in (7.6,8.3):face.part('continuous limestone string',24,-.08,z,48,.48,.22,'stone','masonry cornice',0)
        for u in (10.75,37.25):face.part('split limestone base course',u,-.08,.6,21.5,.48,.22,'stone','masonry cornice',0)
    rear=sides[2]
    B.open_wall(rear,34,.26,8.5,[dict(id='rear loading entrance',u=17,z=.26,w=5,h=4.3,cols=3,rows=2),
        *[dict(id=f'rear window {i}',u=u,z=1,w=2.4,h=5.7,rows=4) for i,u in enumerate((4,9,25,30))]])
    # Two front shops flank a truly open central nave.
    front=sides[0]
    for u0,u1 in ((0,7.8),(26.2,34)):
        f=C.Face(front.p(u0,0,0),(1,0,0),(0,1,0),f'front shop {u0}')
        B.open_wall(f,u1-u0,.26,4.65,[dict(id=f'shopfront {u0}',u=(u1-u0)/2,z=.26,w=5.6,h=3.5,cols=3,rows=2)],role='timber')
        f.part('recessed upper shop wall',(u1-u0)/2,3.4,6.15,u1-u0,.12,2.6,'interior','gallery back',0)
        C.railing('front gallery balustrade',f.p(.3,-.02,4.82),f.p(u1-u0-.3,-.02,4.82),1.08,.20,'trim')
        for u in [i*.65+.5 for i in range(11)]:
            for sign in (-1,1):C.beam('gallery diamond scroll',f.p(u-.25,-.055,5.32),f.p(u,-.055,5.32+sign*.30),.025,.025,'trim','front ironwork')
            for sign in (-1,1):C.beam('gallery diamond scroll',f.p(u+.25,-.055,5.32),f.p(u,-.055,5.32+sign*.30),.025,.025,'trim','front ironwork')
    for x in (-16.55,16.55):
        for z in [i*.52+.52 for i in range(16)]:box('front dressed corner block',(x,-23.7,z),(.9,.85,.48),'stone','quoins')
    # The entire roof uses a continuous barrel, side lean-tos and a sealed ridge monitor.
    half=9.4;spring=11;rise=6.5
    def roof(x):return spring+rise*math.sqrt(max(0,1-(x/half)**2))
    count=48
    xs=sorted(set([-half+2*half*i/count for i in range(count+1)]+[-1.55,1.55]))
    for a,b in zip(xs,xs[1:]):
        if abs((a+b)/2)<1.55:continue
        C.solid_surface('vault glass strip',[(a,-24,roof(a)),(b,-24,roof(b)),(b,24,roof(b)),(a,24,roof(a))],.035,'glass','barrel glazing')
    for x in (-1.55,1.55):
        box('monitor glazed side',(x,0,18),( .035,48,1.1),'glass','ridge monitor')
        for y in range(-24,25,2):C.beam('monitor upright',(x,y,roof(x)-.08),(x,y,18.6),.06,.06,'trim','ridge monitor')
    C.solid_surface('sealed monitor roof',[(-1.58,-24,18.6),(0,-24,19.05),(0,24,19.05),(-1.58,24,18.6)],.05,'glass','ridge monitor')
    C.solid_surface('sealed monitor roof',[(0,-24,19.05),(1.58,-24,18.6),(1.58,24,18.6),(0,24,19.05)],.05,'glass','ridge monitor')
    for y in (-24,24):C.prism('monitor closed end',[(-1.55,17.35),(-1.55,18.6),(0,19.05),(1.55,18.6),(1.55,17.35)],'y',y-.018,y+.018,'glass','ridge monitor')
    for x in (-1.55,0,1.55):C.beam('monitor longitudinal ridge',(x,-24,19.05 if x==0 else 18.6),(x,24,19.05 if x==0 else 18.6),.08,.08,'trim','ridge monitor')
    for side in (-1,1):
        # Opaque standing-seam fields surround narrow longitudinal skylights.
        for x0,x1,role in ((9.4,11.4,'roof'),(11.4,13.0,'glass'),(13.0,16.9,'roof')):
            z=lambda x:11-(x-9.4)*2.4/7.5
            ys=(-24,-20.5,-15.5,-10.5,-5.5,-3.5,3.5,5.5,10.5,15.5,20.5,24)
            for y0,y1 in zip(ys,ys[1:]):
                if y0==-3.5:continue
                material=role if role!='glass' or any(abs((y0+y1)/2-c)<2.51 for c in (-18,-8,8,18)) else 'roof'
                C.solid_surface('side aisle roof field',[(side*x0,y0,z(x0)),(side*x1,y0,z(x1)),(side*x1,y1,z(x1)),(side*x0,y1,z(x0))],.05,material,'aisle roof')
        for y in (-3.5,3.5):
            C.solid_surface('transverse entrance roof',[(side*9.4,y,11),(side*17.36,y,8.6),(side*17.36,0,12.8),(side*9.4,0,12.8)],.07,'roof','side entrance roof')
        C.prism('closed inboard portal gable',[(-3.5,11),(3.5,11),(0,12.8)],'x',side*9.4-.025,side*9.4+.025,'glass','side entrance roof')
        for i in range(97):
            y=-24+i*.5
            if abs(y)<3.5:continue
            C.beam('side roof standing seam',(side*9.4,y,11.035),(side*16.9,y,8.635),.025,.045,'trim','aisle structure')
        C.beam('side continuous gutter',(side*16.9,-24,8.58),(side*16.9,24,8.58),.17,.18,'trim','drainage')
    for y in range(-24,25,4):
        B.curve_beam('vault rib',[(x,y,roof(x)) for x in xs],.105,.17,'trim','iron roof frame')
        for x in (-9.4,9.4):
            C.rod('iron nave column',(x,y,.26),(x,y,11),.11,'trim','nave structure')
            box('column foot',(x,y,.44),(.48,.48,.36),'trim','nave structure')
            for direction in (-1,1):
                end=x+direction*1.45;top=10.34 if abs(end)>9.4 else 10.9
                C.beam('column knee brace',(x,y,9.0),(end,y,top),.12,.12,'trim','nave structure')
        C.beam('iron tie',( -9.4,y,11),(9.4,y,11),.09,.16,'trim','nave structure')
    for x in [i*.65 for i in range(-14,15) if abs(i*.65)>1.55]:
        C.beam('fine vault glazing seam',(x,-24,roof(x)+.018),(x,24,roof(x)+.018),.026,.035,'trim','glazing seams')
    for i in range(61):
        y=-24+i*.8
        if i%5==0:continue  # Primary ribs already occupy each four-metre station.
        for side in (-1,1):
            segment=[x for x in xs if x*side>=1.55-1e-6]
            B.curve_beam('secondary curved barrel glazing seam',[(x,y,roof(x)+.025) for x in segment],.035,.045,'trim','glazing seams')
    # End vault glass and radiating ironwork above the open ground-floor entry.
    for y in (-24,24):
        for side in (-1,1):
            C.prism('closed aisle end glazing',[(side*9.4,8.5),(side*16.9,8.5),(side*16.9,8.6),(side*9.4,11)],'y',y-.025,y+.025,'glass','end glazing')
            C.beam('aisle end frame',(side*9.4,y,11),(side*16.9,y,8.6),.075,.12,'trim','end ironwork')
        if y>0:box('rear clerestory closure',(0,y,9.75),(18.8,.05,2.5),'glass','end glazing')
        for a,b in zip(xs,xs[1:]):C.prism('glazed end clerestory',[(a,11),(b,11),(b,roof(b)),(a,roof(a))],'y',y-.018,y+.018,'glass','end glazing')
        for x in [i*1.2 for i in range(-7,8)]:C.beam('end vertical mullion',(x,y,11),(x,y,roof(x)),.07,.07,'trim','end ironwork')
        for x in (-9.4,9.4):C.beam('entrance portal',(x,y,.26),(x,y,11),.18,.22,'trim','entry frame')
        C.beam('entrance cross girder',(-9.4,y,8.8),(9.4,y,8.8),.16,.35,'trim','entry frame')
        C.beam('entrance upper girder chord',(-9.4,y,9.83),(9.4,y,9.83),.16,.16,'trim','entry frame')
        for x in range(-9,9):
            C.beam('lattice girder diagonal',(x,y,9),(x+1,y,9.8),.045,.045,'trim','entry lattice')
            C.beam('lattice girder diagonal',(x,y,9.8),(x+1,y,9),.045,.045,'trim','entry lattice')
    # Shop galleries carry actual counters, shelving and product displays.
    for side in (-1,1):
        x=side*12.6
        box('gallery supported floor',(x,0,4.7),(7.3,47,.24),'floor','gallery structure')
        for y in range(-20,24,8):
            for xx in (side*9.5,side*15.9):C.beam('gallery bearing post',(xx,y,.26),(xx,y,4.6),.17,.17,'trim','gallery supports')
        # A full-width break for the staircase at the rear.
        C.railing('gallery balustrade',(side*9.2,-23,4.82),(side*9.2,21.45,4.82),1.12,.22,'trim')
        for level in (.26,4.82):
            for j,y in enumerate((-18,-10,-2,6,14)):
                if level<1 and y==-2:continue  # Clear passage from both side doors to the nave.
                box('vendor back wall',(side*15.9,y,level+1.8),(.16,6.5,3.6),'timber','market stalls')
                box('vendor counter',(side*11.5,y,level+.9),(1.0,4.5,1.05),'timber','market stalls')
                box('stone counter top',(side*11.5,y,level+1.45),(1.16,4.65,.08),'stone','market stalls')
                for z in (.8,1.65,2.5):box('display shelf',(side*15.45,y,level+z),(.8,5.8,.06),'timber','market stalls')
                for k in range(8):
                    box('display produce crate',(side*11.5,y-1.7+k*.48,level+1.64),(.52,.38,.3),'bronze' if k%2 else 'leaf','market produce')
                for yy in (y-3.1,y+3.1):box('stall partition',(side*13.5,yy,level+1.55),(4.8,.12,3.1),'timber','market stalls')
        # Wide, supported straight flights along each gallery, unobstructed landings.
        steps=27;rise=4.56/steps;run=.29
        for i in range(steps):box('gallery stair tread',(side*7.6,13.8+i*run,.26+(i+1)*rise/2),(2.25,run+.02,(i+1)*rise),'stone','gallery stair')
        for sx in (side*7.6-1.05,side*7.6+1.05):C.railing('stair handrail',(sx,13.8,.26),(sx,21.48,4.82),1.04,.25,'trim')
        box('stair top landing',(side*8.35,22.35,4.7),(3.7,1.8,.24),'floor','gallery stair')
        C.railing('landing rear guard',(side*6.5,23.22,4.82),(side*10.2,23.22,4.82),1.12,.22,'trim')
        C.railing('landing inner return',(side*6.5,21.5,4.82),(side*6.5,23.22,4.82),1.12,.22,'trim')
    for x in (-4.6,4.6):
        for y in (-17,-10,-3,4,11):B.table(x,y,.26)
    B.label('MARKET HALL',(0,-24.16,8.87),.49)
    C.CONTACTS.extend([dict(name='iron vault and side aisle union',status='Shared springline and continuous edge gutter; ridge monitor closes every face.'),
                       dict(name='market program',status='Eighteen stocked stalls, connected upper galleries and two complete stairs; central entry and aisle remain open.')])
    for y in (-16,0,16):C.qa_room_light('market daylight',(0,y,10),900,8)
