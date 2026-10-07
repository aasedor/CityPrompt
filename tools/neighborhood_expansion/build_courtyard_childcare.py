"""Three inward-falling roof planes enclose a furnished childcare courtyard."""
from pathlib import Path
import math
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import delivery as D
from delivery import C, B, R, bpy
import build_library_pavilion as L  # Individual table, basin and toilet fixtures.

Z = .14
OBS = []
PALETTE = dict(B.PALETTE, wall=(.67,.29,.16), trim=(.79,.76,.65),
    timber=(.57,.37,.18), roof=(.16,.20,.24), interior=(.84,.81,.72),
    floor=(.65,.54,.38), furniture=(.41,.51,.30), ceiling=(.85,.82,.73),
    lamp=(.97,.89,.70), leaf=(.23,.32,.13), flower=(.67,.56,.28),
    grass=(.29,.37,.16), mirror=(.76,.79,.81), sand=(.67,.55,.35))

def hole(name,u,z,w,h,door=False):
    return dict(id=name,u=u,z=z,w=w,h=h,door=door)

def wall(face,a,b,holes=(),top=3.50,role='wall',depth=.30):
    face.wall(face.label,a,b,0,top,depth,role,holes)
    cuts=sorted((h for h in holes if h.get('door')),key=lambda h:h['u'])
    edges=[a]
    for h in cuts:edges.extend([h['u']-h['w']/2,h['u']+h['w']/2])
    edges.append(b)
    for lo,hi in zip(edges[::2],edges[1::2]):
        pts=[face.p(u,d,0) for u in (lo,hi) for d in (0,depth)]
        OBS.append([min(p[0] for p in pts),max(p[0] for p in pts),
                    min(p[1] for p in pts),max(p[1] for p in pts),0,top])
    for h in holes:
        u,z,w,ht=h['u'],h['z'],h['w'],h['h']
        if h.get('door'):
            for s in (-1,1):face.part(h['id']+' jamb',u+s*(w/2-.025),.08,z+ht/2,.05,.16,ht,'timber')
            face.part(h['id']+' lintel',u,.08,z+ht,w,.16,.06,'timber')
            # An inward ninety-degree leaf, hinged inside the carrier reveal.
            leaf=C.Face(face.p(u-w/2+.065,.12,0),face.n,face.t,h['id']+' open leaf')
            if role=='interior':leaf.part(h['id']+' open leaf',(w-.13)/2,0,z+ht/2,w-.13,.065,ht-.07,'timber','interior')
            else:leaf.window(h['id']+' open leaf',(w-.13)/2,z,w-.13,ht-.05,1,1,'timber',.03,.035,False,False,.08,'open glazed leaf')
        else:
            face.window(h['id'],u,z,w,ht,2 if w>1.8 else 1,1,'trim' if role=='wall' else 'timber',.16,.05,False,False,depth)
            if role=='wall':
                face.part(h['id']+' cream sill',u,-.015,z-.035,w+.16,.38,.075,'trim')
                for s in (-1,1):face.part(h['id']+' cream surround',u+s*(w/2+.055),-.025,z+ht/2,.11,.08,ht+.18,'trim')
                face.part(h['id']+' cream head',u,-.025,z+ht+.045,w+.22,.08,.11,'trim')

def ywall(name,y,a,b,doors=(),top=3.50,normal=1):
    wall(C.Face((0,y,0),(1,0,0),(0,normal,0),name),a,b,
         [hole(name+' door '+str(u),u,Z,1.25,2.30,True) for u in doors],top,'interior',.14)

def xwall(name,x,a,b,doors=(),normal=1):
    wall(C.Face((x,0,0),(0,1,0),(normal,0,0),name),a,b,
         [hole(name+' door '+str(u),u,Z,1.25,2.30,True) for u in doors],3.50,'interior',.14)

def roof_z(x,y):
    return max(.18*abs(x)+2.25,.18*y+2.79)

def roofs():
    # Three disjoint fields share exact diagonal endpoints; no hidden overlap.
    patches=[('left',(-.18,0,2.25),[(-15.45,-12.45),(-7,-12.45),(-7,4),(-15.45,12.45)]),
             ('rear',(0,.18,2.79),[(-15.45,12.45),(-7,4),(7,4),(15.45,12.45)]),
             ('right',(.18,0,2.25),[(7,-12.45),(15.45,-12.45),(15.45,12.45),(7,4)])]
    for name,plane,poly in patches:
        def height(x,y):return plane[0]*x+plane[1]*y+plane[2]
        outline=[(x,y,height(x,y)) for x,y in poly]
        C.solid_surface(name+' standing seam field',outline,.12)
        C.solid_surface(name+' cedar soffit',[(x,y,z-.12) for x,y,z in outline],.055,'timber','roof')
        # Long seams follow the direction of water flow and terminate at joins.
        axis=0 if name=='rear' else 1
        for i in range(-31,32):
            v=i*.5;hits=[]
            for p,q in zip(poly,poly[1:]+poly[:1]):
                if (p[axis]<=v<q[axis]) or (q[axis]<=v<p[axis]):
                    t=(v-p[axis])/(q[axis]-p[axis]);hits.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
            if len(hits)==2:
                a,b=hits;C.beam(name+' seam',(*a,height(*a)+.016),(*b,height(*b)+.016),.018,.026,'roof','roof')
    for sign in (-1,1):
        C.beam('diagonal closed roof junction',(sign*15.45,12.45,5.056),(sign*7,4,3.535),.16,.045,'roof','roof')
        for y in (-12.46,12.46):
            if y<0:C.beam('sloped wing front fascia',(sign*15.46,y,4.95),(sign*7,y,3.43),.15,.20,'roof','roof')
        C.beam('high outer fascia',(sign*15.46,-12.45,4.95),(sign*15.46,12.45,4.95),.15,.20,'roof','roof')
        # Bounded gutters at the three low courtyard eaves; downpipes discharge
        # at planted edge basins rather than onto an occupied entrance.
        C.box('court eave gutter',(sign*7,-4.225,3.43),(.18,16.45,.16),'roof','roof')
        C.rod('downpipe',(sign*6.96,3.72,.22),(sign*6.96,3.72,3.45),.045,'roof','structure')
        C.box('rain basin',(sign*6.91,3.75,.17),(.48,.48,.06),'stone','site')
    C.box('rear high fascia',(0,12.46,4.95),(30.92,.15,.20),'roof','roof')
    C.box('rear low gutter',(0,4,3.43),(14.15,.18,.16),'roof','roof')
    # Headers seat on posts, rafters seat on headers and masonry.
    header_top=3.416
    for sign in (-1,1):
        C.box('veranda longitudinal header',(sign*7.45,-3.85,header_top-.12),(.22,16.6,.24),'timber','structure')
        for y in (-11.65,-7.65,-3.65,.35,4.45):
            C.box('veranda post foot',(sign*7.45,y,.19),(.25,.25,.10),'hardware','structure')
            C.box('veranda cedar post',(sign*7.45,y,(.24+header_top-.24)/2),(.20,.20,header_top-.48),'timber','structure')
        for y in (-11.65,-7.65,-3.65,.35):
            C.beam('veranda seated rafter',(sign*9,y,roof_z(9,y)-.285),(sign*7.1,y,roof_z(7.1,y)-.285),.14,.22,'timber','structure')
    C.box('rear veranda header',(0,4.45,header_top-.12),(15.1,.22,.24),'timber','structure')
    for x in (-3.75,0,3.75):
        C.box('rear veranda post foot',(x,4.45,.19),(.25,.25,.10),'hardware','structure')
        C.box('rear veranda cedar post',(x,4.45,(.24+header_top-.24)/2),(.20,.20,header_top-.48),'timber','structure')
        C.beam('rear veranda seated rafter',(x,6,roof_z(x,6)-.285),(x,4.1,roof_z(x,4.1)-.285),.14,.22,'timber','structure')

def cubbies(x,y,length=2.4):
    for zz in (.18,.61,1.04):C.box('low child cubby shelf',(x,y,Z+zz),(length,.43,.06),'timber','furniture')
    for i in range(5):C.box('floor-seated cubby divider',(x-length/2+i*length/4,y,Z+.535),(.05,.43,1.07),'timber','furniture')
    for i in range(4):C.box('cubby basket',(x-length*.375+i*length/4,y-.04,Z+.34),(.43,.31,.25),'furniture','furniture')

def low_basin(x,y):
    base=C.box('child handwash cabinet',(x,y,Z+.28),(1.8,.66,.56),'timber','furniture')
    top=C.box('child handwash counter',(x,y,Z+.60),(1.86,.70,.08),'stone','furniture')
    for dx in (-.45,.45):
        C.cut_box(base,'bowl clearance',(x+dx,y,Z+.56),(.54,.46,.36))
        C.cut_box(top,'counter opening',(x+dx,y,Z+.60),(.50,.42,.22))
        bowl=C.box('child sink bowl',(x+dx,y,Z+.49),(.54,.46,.25),'hardware','furniture')
        C.cut_box(bowl,'hollow basin',(x+dx,y,Z+.59),(.47,.39,.27))
        C.rod('child tap',(x+dx,y+.25,Z+.64),(x+dx,y+.25,Z+.85),.018,'hardware','furniture')
        C.rod('child tap spout',(x+dx,y+.25,Z+.85),(x+dx,y+.02,Z+.85),.018,'hardware','furniture')

def playhouse():
    x,y=3,0
    C.box('playhouse raised floor',(x,y,.22),(2.2,2,.16),'timber','furniture')
    f=C.Face((x,y-1,0),(1,0,0),(0,1,0),'playhouse front')
    wall(f,-1.1,1.1,[hole('playhouse small door',0,.30,.84,1.15,True)],1.485,'timber',.08)
    for sx in (-1,1):
        f=C.Face((x+sx*1.1,y,0),(0,1,0),(-sx,0,0),'playhouse flank')
        wall(f,-.92,.92,[hole('playhouse small window '+str(sx),0,.77,.70,.50)],1.485,'timber',.08)
    C.box('playhouse back',(x,y+.96,.8925),(2.2,.08,1.185),'timber','furniture')
    for yy in (y-1,y+.92):C.prism('playhouse gable',[(x-1.1,1.48),(x,2.135),(x+1.1,1.48)],'y',yy,yy+.08,'timber','furniture')
    for sx in (-1,1):C.solid_surface('playhouse roof',[(x,y-1.16,2.2),(x+sx*1.23,y-1.16,1.473),(x+sx*1.23,y+1.16,1.473),(x,y+1.16,2.2)],.06,'roof','furniture')
    # The play prop is intentionally not an adult walk destination.
    OBS.append([1.78,4.22,-1.18,1.18,Z,2.2])

def build():
    OBS.clear()
    bs=C.MATS['mirror'].node_tree.nodes['Principled BSDF'];bs.inputs['Metallic'].default_value=1;bs.inputs['Roughness'].default_value=.055
    C.box('earth base',(0,-1,.0125),(40,36,.025),'soil','site',0)
    C.box('site lawn',(0,.6,.0325),(40,32.8,.015),'grass','site',0)
    C.box('front lawn strip',(0,-18.25,.0325),(40,1.5,.015),'grass','site',0)
    for x in (-12,12):C.box('occupied side wing floor',(x,0,.08),(6,24,.12),'floor','floors',0)
    C.box('rear learning floor',(0,9,.08),(18,6,.12),'floor','floors',0)
    C.box('courtyard paving',(0,-3,.09),(18,18,.10),'paving','site',0)
    # Exterior carriers stop below the common timber roof lining.
    for sign in (-1,1):
        a,b=(-15,-9) if sign<0 else (9,15)
        front=C.Face((0,-12,0),(1,0,0),(0,1,0),'wing front '+str(sign))
        wall(front,a,b,[hole('front picture '+str(sign),sign*12,.65,2.6,2.30)],3.69)
        C.prism('sloped front masonry',[(a,3.68),(b,3.68),(b,roof_z(b,-12)-.17),(a,roof_z(a,-12)-.17)],'y',-12,-11.7,'wall')
        outer=C.Face((sign*15,0,0),(0,1,0),(-sign,0,0),'outer wing '+str(sign))
        flank_windows=(-9.2,-5.5,-2.3,1.0,5.0,10) if sign<0 else (-8.5,-3.5,1.0,5.3,10)
        wall(outer,-11.7,11.7,[hole('outer light '+str(sign)+' '+str(y),y,.80,2.2,2.3) for y in flank_windows],4.78)
        inner=C.Face((sign*9,0,0),(0,1,0),(sign,0,0),'court wing '+str(sign))
        hs=[hole('court door '+str(sign)+' '+str(y),y,Z,1.35,2.65,True) for y in ((-10,-4) if sign<0 else (-9,-1))]
        pane_sizes=((-7.9,1.3),(-5.9,.9),(0,2.2),(4.5,2.2)) if sign<0 else ((-5,2.2),(1.7,1.8),(4.6,2.2))
        hs += [hole('court glass '+str(sign)+' '+str(y),y,.45,width,2.75) for y,width in pane_sizes]
        wall(inner,-11.7,6,hs,3.70)
    rear=C.Face((0,12,0),(1,0,0),(0,-1,0),'outer rear')
    wall(rear,-15,15,[hole('rear daylight '+str(x),x,.9,2.2,2.2) for x in (-12,-8.5,-4,0,4,9,12.5)],4.78)
    court=C.Face((0,6,0),(1,0,0),(0,1,0),'rear court')
    hs=[hole('rear court glass '+str(x),x,.45,2.15 if x==0 else 1.8,2.75) for x in (-7.3,-3.7,0,3.7,7.3)]
    hs += [hole('rear classroom door '+str(x),x,Z,1.30,2.65,True) for x in (-5.5,5.5)]
    wall(court,-9,9,hs,3.70)
    # Separate occupied programme, with circulation through the learning rooms.
    ywall('reception to toddler',-7,-14.7,-9,[-9.9])
    ywall('toddler to rear corridor',3,-14.7,-9,[-9.9])
    xwall('nap corridor',-10.8,3.14,6.95,[5.2],-1)
    ywall('nap north enclosure',6.95,-14.7,-10.8)
    ywall('left support rooms',7.85,-14.7,-7,[-12,-8.5])
    xwall('staff to adult washroom',-10.7,7.99,11.7)
    xwall('adult WC to learning room',-7,7.85,11.7)
    ywall('preschool to rear corridor',3,9,14.7,[9.9])
    xwall('child washroom corridor',10.8,3.14,7.85,[4.6])
    ywall('kitchen front',7.85,7,14.7,[9.9])
    xwall('kitchen to learning room',7,7.85,11.7)
    for x in (-12,12):C.box('wing ceiling',(x,0,3.49),(5.42,23.42,.10),'ceiling','ceiling',0)
    C.box('rear ceiling',(0,9.0,3.49),(18.02,5.42,.10),'ceiling','ceiling',0)
    roofs()
    # Reception, low storage and adult supervision desk.
    C.box('reception desk',(-12.7,-8.4,Z+.38),(2.0,.8,.76),'timber','furniture')
    C.box('reception chair',(-12.7,-7.65,Z+.24),(.48,.45,.48),'furniture','furniture')
    cubbies(-12.4,-11.30,2.8)
    C.box('reception noticeboard',(-13,-7.035,1.7),(1.4,.075,.8),'timber','furniture')
    for y in (-5,-.6):L.table(-12.6,y,1.6,.75,True)
    cubbies(-12.7,2.55,2.7)
    for y in (-9,-4.5,.1):L.table(12.5,y,1.6,.75,True)
    cubbies(12.5,2.55,2.7)
    # Rear creative classroom with a clear front crossing aisle.
    for x in (-4,0,4):L.table(x,9.7,2.0,.8,True)
    cubbies(0,11.33,3.0)
    for x in (-5.7,5.7):
        C.box('reading rug',(x,10.0,Z+.018),(1.6,2.7,.036),'furniture','furniture')
        for y in (9.3,10.5):C.box('reading cushion',(x,y,Z+.20),(.65,.65,.36),'interior','furniture')
    # Four child cots, with unobstructed room entrance along its right edge.
    for x in (-13.9,-11.8):
        for y in (4.0,6.3):
            C.box('nap cot base',(x,y,Z+.15),(1.5,.72,.30),'timber','furniture')
            C.box('nap mattress',(x,y,Z+.36),(1.46,.68,.12),'interior','furniture')
            C.box('nap pillow',(x-.48,y,Z+.455),(.40,.56,.09),'furniture','furniture')
    L.table(-12.6,9.9,1.5,.75)
    L.basin(-8.5,11.31);L.toilet(-9.65,9.0)
    C.box('adult washroom mirror',(-7.013,10.5,1.75),(.03,1.1,.7),'mirror','furniture')
    low_basin(12.15,7.30)
    for x in (12,14):
        L.toilet(x,5.4)
        # Lowered fixtures are scaled together around the floor for child use.
        # Adult WC above retains its original height.
        for o in list(C.objects())[-3:]:
            for v in o.data.vertices:v.co.z=Z+(v.co.z-Z)*.74
    C.box('child privacy panel',(13,5.20,Z+.61),(.065,1.3,1.22),'timber','furniture')
    C.box('child basin mirror',(12.15,7.837,1.31),(1.8,.03,.56),'mirror','furniture')
    L.basin(10.0,11.30)
    C.box('kitchen fridge',(14.14,10.85,Z+1),(1,1,2),'ceiling','furniture')
    C.box('kitchen preparation cabinet',(12.1,11.31,Z+.44),(1.8,.70,.88),'timber','furniture')
    C.box('kitchen worktop',(12.1,11.31,Z+.91),(1.86,.75,.06),'stone','furniture')
    C.box('snack preparation table',(12.3,9,Z+.45),(1.6,.8,.9),'timber','furniture')
    # Secure low front fence; gate is modelled in its open review position.
    for a,b in [(-9,-1),(1,9)]:
        for zz in (.40,1.15):C.box('front fence rail',((a+b)/2,-12,Z+zz),(b-a,.08,.10),'timber','site')
        for i in range(round((b-a)/.14)+1):C.box('front fence slat',(a+(b-a)*i/round((b-a)/.14),-12,Z+.65),(.065,.085,1.30),'timber','site')
        for x in (a,b):C.box('fence post',(x,-12,Z+.72),(.16,.16,1.44),'timber','site')
    for y in (-11.93,-10.0):C.box('open gate end',(1.06,y,Z+.65),(.085,.10,1.30),'timber','site')
    for zz in (.40,1.15):C.box('open gate rail',(1.06,-10.96,Z+zz),(.085,2.02,.10),'timber','site')
    for i in range(14):C.box('open gate slat',(1.06,-11.93+i*.148,Z+.65),(.075,.065,1.30),'timber','site')
    C.box('front approach',(0,-13.8,.09),(3.2,3.6,.10),'paving','site',0)
    C.box('public sidewalk',(0,-16.65,.02),(40,1.7,.04),'paving','site',0)
    C.prism('public ramp',[(-17.1,0),(-17.1,.04),(-15.6,.14),(-15.6,0)],'x',-1.6,1.6,'paving','site')
    # Low planted play court with reserved circulation.
    C.box('courtyard lawn',(-3.7,-.55,Z+.0125),(5.4,6.2,.025),'grass','site',0)
    C.box('playhouse lawn',(3.6,.1,Z+.0125),(4.4,5.7,.025),'grass','site',0)
    C.box('sandbox sand',(-3.5,-6.1,Z+.06),(2.9,2.3,.12),'sand','site')
    for x in (-5.0,-2):C.box('sandbox long rim',(x,-6.1,Z+.16),(.13,2.56,.32),'timber','site')
    for y in (-7.35,-4.85):C.box('sandbox end rim',(-3.5,y,Z+.16),(3.12,.13,.32),'timber','site')
    playhouse()
    for y in (-7.5,-5.5):R.plantbed(4.0,y,2.5,.9)
    for x,y in [(-5.6,-9),(-5.6,2.8),(4.8,2.8)]:R.plantbed(x,y,1.1,1.0)
    B.bench(-5.7,-2.6);B.bench(5.4,1.9)
    # Exterior planting and bicycle storage are outside the secure court.
    for x in (-12,-6,6,12):R.plantbed(x,-14.7,3.6,1.8)
    for x,y,seed in [(-18,-10,801),(18,-10,802),(-18,10,803),(18,10,804)]:R.tree(x,y,seed)
    C.box('bicycle pad',(-17,-14.4,.09),(3,3,.10),'paving','site',0)
    C.box('bicycle connecting path',(-10.05,-16.0,.09),(16.9,.8,.10),'paving','site',0)
    C.prism('bicycle sidewalk ramp',[(-17.1,0),(-17.1,.04),(-16.4,.14),(-16.4,0)],'x',-18.5,-15.5,'paving','site')
    for x in (-17.7,-16.5):B.bikehoop(x,-14.4)
    for x,y in [(-12,-9.8),(-12,-4),(-12,0),(-12.5,5.2),(-12.4,10),(-8.5,9.8),(-4,9),(0,9),(4,9),(12,-9),(12,-4),(12,0),(12.7,6.5),(11.8,10)]:
        R.lamp(x,y,3.405,.75);C.qa_room_light('childcare room',(x,y,3.20),180,2.4)
    for o in bpy.context.scene.objects:
        if o.type=='LIGHT':o.visible_camera=False;o.visible_glossy=False;o.visible_transmission=False;o.data.specular_factor=0;o.data.transmission_factor=0

def network():
    tris=[];routes=[]
    def rect(a,b,c,d,z=Z):
        p=[a,b,z];q=[c,b,z];r=[c,d,z];s=[a,d,z];tris.extend([[p,q,r],[p,r,s]])
    rect(-14.68,-11.68,-9,11.68);rect(9,-11.68,14.68,11.68);rect(-9,6,9,11.68)
    rect(-9,-12,9,6);rect(-1.6,-15.6,1.6,-12);rect(-18.5,-17.5,1.6,-17.1,.04)
    a=[-1.6,-17.1,.04];b=[1.6,-17.1,.04];c=[1.6,-15.6,Z];d=[-1.6,-15.6,Z];tris.extend([[a,b,c],[a,c,d]])
    rect(-18.5,-15.9,-15.5,-12.9);rect(-18.5,-16.4,-1.6,-15.6)
    a=[-18.5,-17.1,.04];b=[-15.5,-17.1,.04];c=[-15.5,-16.4,Z];d=[-18.5,-16.4,Z];tris.extend([[a,b,c],[a,c,d]])
    def route(name,points):routes.append(dict(name=name,points=[[x,y,Z] for x,y in points]))
    routes.append(dict(name='Public approach through gate',points=[[0,-17.3,.04],[0,-17.1,.04],[0,-15.6,Z],[0,-10,Z]]))
    route('Sheltered reception',[(0,-10),(-8,-10),(-10.2,-10),(-11.2,-10)])
    route('Reception to toddler',[(-9.9,-9),(-9.9,-5),(-10.8,-4)])
    route('Toddler garden door',[(-10.8,-4),(-8.2,-4)])
    route('Toddler to nap room',[(-9.9,0),(-9.9,5.2),(-12.5,5.2)])
    route('Staff room',[(-9.9,7.45),(-12,7.45),(-12,8.45),(-11.3,8.45),(-11.3,10.5)])
    route('Adult washroom',[(-9.9,6.9),(-8.5,6.9),(-8.5,9.7),(-8.5,10.3)])
    route('Rear learning room crossing',[(-9.9,7.58),(5.5,7.58)])
    route('Rear activity tables',[(-5.5,7.58),(-5.5,8.2),(-2,8.2),(2,8.2),(5.5,8.2)])
    route('Rear left courtyard doorway',[(-5.5,6.9),(-5.5,3.65)])
    route('Rear right courtyard doorway',[(5.5,6.9),(5.5,3.65)])
    route('Kitchen',[(5.5,6.9),(9.9,6.9),(9.9,9.7),(10.6,9.7)])
    route('Child washroom',[(9.9,6.9),(9.9,4.6),(11.3,4.6),(11.3,6.4),(12.1,6.4)])
    route('Preschool indoor connection',[(9.9,6.9),(9.9,1),(10.8,1)])
    route('Preschool garden entry',[(0,-10),(0,-9.4),(8.2,-9.4),(8.2,-9),(10.2,-9),(10.8,-9)])
    route('Preschool garden exit',[(10.8,-1),(8.2,-1)])
    route('Courtyard centre',[(0,-10),(0,3.65),(-5.5,3.65),(5.5,3.65)])
    route('Sandbox approach',[(0,-8.5),(-3.5,-8.5),(-3.5,-7.95)])
    route('Growing beds',[(0,-8.5),(2.2,-8.5),(4,-8.5)])
    route('Playhouse approach',[(0,-3),(3,-3),(3,-1.8)])
    route('Courtyard bench',[(0,-3.6),(-5.7,-3.6),(-5.7,-3.4)])
    routes.append(dict(name='Bicycle parking',points=[[0,-17.3,.04],[-17.1,-17.3,.04],[-17.1,-17.1,.04],[-17.1,-16.4,Z],[-17.1,-15.35,Z]]))
    for o in C.objects():
        mod=o.get('cityprompt_lego_module','');role=o.get('cityprompt_semantic_role','')
        eligible=mod in ('furniture','interior','site','structure') or 'open leaf' in o.name or o.name.startswith(('bike rack','young tree trunk'))
        if role in ('paving','soil','leaf','plant','flower','grass','sand') or any(s in o.name for s in ('ceiling','luminaire','diffuser','rafter','header','fascia','gutter','downpipe')):eligible=False
        if eligible:
            lo,hi=C.bounds([o]);OBS.append([lo[0],hi[0],lo[1],hi[1],lo[2],hi[2]])
    return dict(version=2,footprint=[40,36],entrance=[0,-17.3,.04],maxStepM=.18,triangles=tris,obstacles=OBS,
        portals=[[-1.6,1.6,-17.5,-16.9]],routes=routes,gardenExclusionProbes=[
            dict(name='front fence',point=[-3,-12,Z]),dict(name='open gate',point=[1.06,-11,Z]),
            dict(name='veranda post',point=[-7.45,-7.65,Z]),dict(name='playhouse',point=[3,0,Z]),
            dict(name='sandbox rim',point=[-5,-6.1,Z]),dict(name='bench',point=[-5.7,-2.6,Z]),
            dict(name='bicycle hoop',point=[-17.7,-14.4,Z])])

def cameras():
    cams=[]
    for n,loc in [('front',(0,-54,11)),('front_corner',(-40,-42,26)),('aerial',(32,-35,48)),('left_side',(-52,0,12)),('right_side',(52,0,12)),('rear',(0,49,15)),('rear_side',(37,37,27))]:
        cams.append(dict(name=n,location=loc,target=(0,0,2),whole=True,lens=52))
    for n,loc,target,lens in [
        ('facade_close',(-18,-23,7),(-10,-10,2),33),('architecture_close',(-5,-16,2.5),(-8.7,-9,1.7),26),
        ('glass_close',(-17,-9.2,2),(-12,-9.2,1.2),35),('roof_contact',(-16,14,14),(-8,5,3.8),36),
        ('roof_right_contact',(17,15,14),(8,5,3.8),36),('veranda_contact',(-5,-6,2.3),(-7.45,-3.65,3.1),28),
        ('program_interior',(-10.8,-6.3,1.7),(-12.5,-1.5,1.0),22),('reception',(-10.8,-11.1,1.7),(-12.8,-9,1.1),22),
        ('toddler_reverse',(-13.8,1.6,1.7),(-10,-4,1.2),22),('preschool',(9.7,-10.7,1.7),(12.5,-3,1.1),22),
        ('preschool_reverse',(13.8,1.5,1.7),(10,-8,1.2),22),('rear_classroom',(-6.2,6.5,1.7),(1,9.7,1.1),22),
        ('rear_classroom_reverse',(6.2,11.3,1.7),(-1,7.5,1.2),22),('nap_room',(-11.1,5.15,1.7),(-13.5,5.2,.7),16),
        ('nap_reverse',(-14.4,5.2,1.6),(-11.8,5.2,.65),16),
        ('staff_room',(-14.2,8.7,1.7),(-12,10,1),22),('staff_reverse',(-11.15,11.2,1.8),(-12.8,8.8,1),20),
        ('adult_washroom',(-7.5,9.6,1.7),(-9,10.7,1),20),
        ('adult_toilet',(-10.1,8.35,1.6),(-9.6,9,.65),20),('adult_mirror',(-9.7,10.1,1.7),(-7,10.5,1.75),28),
        ('adult_sink',(-7.5,10.1,1.7),(-8.6,11.3,1),26),('child_washroom',(12.9,3.6,1.7),(13,6.2,.8),20),
        ('child_sinks',(11.3,6.25,1.6),(12.2,7.3,.8),26),('child_toilets',(13,3.7,1.6),(13,5.4,.6),18),
        ('kitchen',(10.3,8.5,1.8),(12.1,10.8,1.1),20),('kitchen_sink',(9,10.1,1.8),(10,11.3,1),28),
        ('kitchen_reverse',(14.3,8.5,1.8),(10.6,11.1,1),20),
        ('courtyard',(0,-10,2.5),(0,1,1.0),24),('playhouse',(5,-4,2.5),(3,0,1),28),
        ('public_approach',(4,-18,1.4),(0,-15.8,.2),26),('garden_gate',(3,-14,1.7),(0,-11,1.0),26),
        ('veranda_route',(-8.3,-10.5,1.7),(-8.3,3,1.5),22),('rear_corridor',(-9.5,7.58,1.7),(8,7.58,1.5),22),
        ('bicycles',(-20,-18,3),(-17,-14.4,.8),28)]:cams.append(dict(name=n,location=loc,target=target,whole=False,lens=lens))
    return cams

if __name__=='__main__':
    D.run(__file__,'childcare-courtyard-prework.json','childcare-courtyard',PALETTE,cameras,build,network,
          'childcare-courtyard-terracotta.png',[1.92,2.0],extra_scripts=[L.__file__])
