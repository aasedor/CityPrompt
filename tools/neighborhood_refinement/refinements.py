"""Finite school/fourplex corrections, retaining the source-led envelopes."""
import math
import random
import bpy
import geometry_core as C

def install(B):
    original_setup=C.setup
    def setup(palette,cameras,resolution):
        palette.update(glass=(.94,.97,.97),roof=(.39,.40,.40),lamp=(.95,.83,.62),
                       leaf=(.22,.31,.11),flower=(.57,.48,.30),ceiling=(.76,.75,.69))
        cams=original_setup(palette,cameras,resolution)
        bs=C.MATS['glass'].node_tree.nodes['Principled BSDF']
        bs.inputs['Alpha'].default_value=1
        bs.inputs['Transmission Weight'].default_value=1
        bs.inputs['Roughness'].default_value=.035
        bs.inputs['IOR'].default_value=1.45
        C.MATS['glass']['optical_profile']='clear neutral thin architectural glass'
        bs=C.MATS['lamp'].node_tree.nodes['Principled BSDF']
        bs.inputs['Emission Color'].default_value=(1,.82,.57,1)
        bs.inputs['Emission Strength'].default_value=3
        return cams
    C.setup=setup
    original_window=C.Face.window
    def window(self,ident,u,z,w,h,cols=2,rows=1,frame='trim',inset=.14,bar=.045,sill=True,curtain=False,depth=.27,kind='window'):
        # Source classroom sash: narrow outer lights and a wide central light.
        custom=cols==3 or ident=='stair window'
        if not custom:return original_window(self,ident,u,z,w,h,cols,rows,frame,inset,bar,sill,curtain,depth,kind)
        fractions=[0,.21,.79,1] if cols==3 else [0,.23,.77,1]
        heights=[0,.18,.80,1] if rows==2 else [0,1]
        original_window(self,ident,u,z,w,h,1,1,frame,inset,bar,False,False,depth,kind)
        for o in list(C.objects()):
            if o.name.startswith(ident+' optical pane'):bpy.data.objects.remove(o,do_unlink=True)
        for f in fractions[1:-1]:self.part(ident+' narrow sash',u+w*(f-.5),inset,z+h/2,bar,.09,h-.1,frame)
        for f in heights[1:-1]:self.part(ident+' unequal transom',u,inset,z+h*f,w-.1,.09,bar,frame)
        for a,b in zip(fractions,fractions[1:]):
            for c,d in zip(heights,heights[1:]):
                self.part(ident+' clear pane',u+w*((a+b)/2-.5),inset+.037,z+h*(c+d)/2,w*(b-a)-.05,.009,h*(d-c)-.05,'glass',soft=0)
        if curtain:
            for side in (-1,1):
                for j in range(4):self.part(ident+' pleated curtain',u+side*(w*.42-j*.025),.57,z+h*.49,.05,.035,h*.91,'interior',soft=0)
    C.Face.window=window
    B.plantbed=plantbed
    B.stair=stair
    B.roof_unit=roof_unit
    old_parapet=B.parapet
    def parapet(x0,x1,y0,y1,z,role='wall'):
        old_parapet(x0,x1,y0,y1,z,role)
        for i in range(int(x1-x0)-1):
            x=x0+.8+i
            C.box('membrane lap seam',(x,(y0+y1)/2,z-.369),(.008,y1-y0-.8,.004),'roof','roof',0)
        for i in range(1,int((y1-y0)/3)):
            C.box('membrane transverse joint',((x0+x1)/2,y0+i*3,z-.369),(x1-x0-.8,.008,.004),'roof','roof',0)
        for x in (x0+.42,x1-.42):C.box('parapet upstand flashing',(x,(y0+y1)/2,z-.28),(.06,y1-y0-.8,.2),'roof','roof',0)
    B.parapet=parapet

def roof_unit(x,y,z,w=3,d=2):
    C.box('screen bearing curb',(x,y,z+.08),(w,d,.16),'roof','roof_equipment')
    for dx in (-w/2,w/2):
        for dy in (-d/2,d/2):C.box('screen upright',(x+dx,y+dy,z+.6),(.055,.055,1.05),'hardware','roof_equipment')
    for i in range(10):
        zz=z+.22+i*.085
        for dy in (-d/2,d/2):C.box('screen long louver',(x,y+dy,zz),(w,.055,.045),'roof','roof_equipment',0)
        for dx in (-w/2,w/2):C.box('screen end louver',(x+dx,y,zz),(.055,d,.045),'roof','roof_equipment',0)
    C.box('fan cabinet',(x+w*.22,y,z+.46),(w*.35,d*.7,.60),'roof','roof_equipment')
    C.rod('visible duct barrel',(x-w*.27,y-d*.28,z+.5),(x-w*.27,y+d*.28,z+.5),.25,'roof','roof_equipment',20)
    C.rod('duct cross connection',(x-w*.27,y,z+.5),(x+w*.08,y,z+.5),.18,'roof','roof_equipment',20)
    fx=x+w*.22;fz=z+.775
    for i in range(24):
        a=i*math.tau/24;b=(i+1)*math.tau/24
        C.rod('fan perimeter',(fx+.28*math.cos(a),y+.28*math.sin(a),fz),(fx+.28*math.cos(b),y+.28*math.sin(b),fz),.014,'hardware','roof_equipment',6)
    for i in range(4):
        a=i*math.pi/4
        C.beam('fan safety grille',(fx-.27*math.cos(a),y-.27*math.sin(a),fz),(fx+.27*math.cos(a),y+.27*math.sin(a),fz),.018,role='hardware')

def stair(x,y,z,rise,width=1.25):
    r=rise/22;start=y-.125;end=start+2.75
    for side in (-1,1):
        points=[]
        for i in range(11):
            a=start+i*.25;b=a+.25
            zz=z+(i+1)*r if side<0 else z+rise-i*r
            points.extend([(a,zz),(b,zz)])
        if side<0:points.extend([(end,z+rise/2-.28),(start,max(.04,z-.28))])
        else:points.extend([(end,z+rise/2-.28),(start,z+rise-.28)])
        cx=x+side*width*.55
        C.prism('continuous stepped stair flight',points,'x',cx-width/2,cx+width/2,'stone','circulation')
        xx=x+side*width*1.1;za=z if side<0 else z+rise
        C.beam('outer stair rail',(xx,start,za+1),(xx,end,z+rise/2+1),.045,role='hardware')
        for j in range(9):
            zz=za+(z+rise/2-za)*j/8
            C.rod('outer guard post',(xx,start+2.75*j/8,zz),(xx,start+2.75*j/8,zz+1),.018)
    C.box('connected half landing',(x,y+3.15,z+rise/2-.09),(width*2.1,1.05,.18),'stone','circulation')
    C.railing('half landing rear guard',(x-width*1.05,y+3.65,z+rise/2),(x+width*1.05,y+3.65,z+rise/2),spacing=.15)

def leaf_cluster(x,y,z,r,seed):
    rng=random.Random(seed)
    # Individual small leaf blades keep the silhouette open, no sphere crowns.
    vs=[];fs=[]
    for i in range(320):
        a=rng.random()*math.tau;rr=r*math.sqrt(rng.random());zz=z+rng.uniform(-r*.55,r*.55)
        px=x+rr*math.cos(a);py=y+rr*math.sin(a);s=rng.uniform(.035,.075)
        tilt=rng.uniform(-1,1);az=rng.random()*math.tau
        dx=s*math.cos(az);dy=s*math.sin(az);dz=s*tilt
        n=len(vs);vs.extend([(px-dx,py-dy,zz-dz),(px+dy*.45,py-dx*.45,zz+s*.4),(px+dx,py+dy,zz+dz),(px-dy*.45,py+dx*.45,zz-s*.4)])
        fs.append((n,n+1,n+2,n+3))
    C.mesh('individual leaves',vs,fs,'leaf','landscape')

def plantbed(x,y,w,d):
    C.box('low concrete planting edge',(x,y,.12),(w,d,.24),'stone','site')
    C.box('mulched planted soil',(x,y,.245),(w-.12,d-.12,.025),'soil','site',0)
    rng=random.Random(round(x*100+y*10))
    for i in range(max(3,round(w*1.4))):
        px=x-w*.43+(i+.5)*w*.86/max(3,round(w*1.4));py=y+rng.uniform(-d*.3,d*.3)
        C.rod('shrub stem',(px,py,.25),(px,py,.68),.017,'timber','landscape',6)
        leaf_cluster(px,py,.68,.34,i+int(abs(x)*30))
        for j in range(13):
            a=j*math.tau/13;reach=.18+.12*rng.random()
            C.beam('ornamental grass blade',(px,py,.26),(px+math.cos(a)*reach,py+math.sin(a)*reach,.56+rng.random()*.20),.014,role='plant',soft=0)

def tree(x,y,seed):
    C.rod('young tree trunk',(x,y,.04),(x,y,2.4),.065,'timber','landscape')
    for i in range(9):
        a=i*2.4;z=1.6+i*.16;px=x+math.cos(a)*.65;py=y+math.sin(a)*.65
        C.rod('branch',(x,y,z),(px,py,z+.55),.022,'timber','landscape',7)
        leaf_cluster(px,py,z+.6,.52,seed+i)

def lamp(x,y,z,w=1.2):
    C.box('ceiling luminaire housing',(x,y,z),(w,.28,.07),'trim','interior')
    C.box('warm diffuser',(x,y,z-.042),(w-.07,.22,.025),'lamp','interior',0)

def open_door(face,ident,u,z,w,h):
    # Door held at 90 degrees leaves the actual portal open for walking.
    for side in (-1,1):face.part(ident+' jamb',u+side*(w/2-.025),.07,z+h/2,.05,.14,h,'trim')
    face.part(ident+' lintel',u,.07,z+h,w,.14,.06,'trim')
    face.part(ident+' open leaf',u-w/2+.045,w/2,z+h/2,.06,w-.09,h-.06,'timber')

def hoop(x,y,sign):
    cy=y+sign*.38;z=2.85
    for i in range(32):
        a=i*math.tau/32;b=(i+1)*math.tau/32
        C.rod('basketball rim',(x+.225*math.cos(a),cy+.225*math.sin(a),z),(x+.225*math.cos(b),cy+.225*math.sin(b),z),.014,'flower','gym',6)
    for i in range(12):
        a=i*math.tau/12
        C.rod('basketball net',(x+.22*math.cos(a),cy+.22*math.sin(a),z),(x+.12*math.cos(a+.3),cy+.12*math.sin(a+.3),z-.38),.006,'ceiling','gym',5)
    C.beam('rim bracket',(x,y,z),(x,cy,z),.04,role='hardware')

def school_interiors():
    # Replace incomplete partitions, retaining the envelope, slabs and two stairs.
    for o in list(C.objects()):
        if o.name.startswith(('classroom partition','classroom teaching board','stair upper landing','desk','chair')):bpy.data.objects.remove(o,do_unlink=True)
    for o in list(bpy.context.scene.objects):
        if o.type=='LIGHT' and o.name.startswith('QA interior classroom'):bpy.data.objects.remove(o,do_unlink=True)
    for level in range(3):
        z=.14+3.8*level;top=(3.8*(level+1)) if level<2 else 10.9
        ceiling=C.box('classroom ceiling',(-5,0,top-.05),(17.4,21.4,.10),'ceiling','rooms',0)
        if level<2:C.cut_box(ceiling,'ceiling stair aperture',(-5,6.25,top),(3.1,4.4,.5))
        rooms=[(-10.275,6.65),(-3.45,7),(1.825,3.55)] if level else [(-10.275,6.65)]
        for x,width in rooms:
            f=C.Face((x,-2.8,0),(1,0,0),(0,-1,0),'classroom corridor')
            door=width/2-.72
            hh=[dict(id=f'classroom door {level} {x}',u=door,z=z,w=.95,h=2.2)]
            f.wall('classroom corridor wall',-width/2,width/2,z,top-.1,.13,'interior',hh)
            open_door(f,hh[0]['id'],door,z,.95,2.2)
            C.box('teaching board',(x-.6,-2.96,z+1.65),(max(1.1,width-2.4),.035,1.2),'furniture','rooms')
            import build_neighborhood as B
            for dx in ([-2.1,-.7,.7,2.1] if width>5 else [-.6,.6]):
                for yy in (-8.7,-6.9,-5.1):B.desk(x+dx,yy,z)
            for dx in (-width*.23,width*.23):
                for yy in (-8,-4.6):lamp(x+dx,yy,top-.14)
                C.qa_room_light('individual classroom',(x+dx,-6.6,top-.4),160,2.5)
            C.box('classroom bookcase',(x-width/2+.25,-4.0,z+.8),(.38,1.5,1.6),'timber','rooms')
            for k in range(15):C.box('classroom coloured books',(x-width/2+.04,-4.65+k*.085,z+1.0),(.30,.055,.40),'furniture','rooms',0)
        for x in ([-6.95,.05] if level else [-6.95]):
            C.box('classroom full partition',(x,-6.75,(z+top-.1)/2),(.12,7.75,top-.1-z),'interior','rooms',0)
        lamp(-5,1,top-.14,2)
        C.qa_room_light('stair and corridor',(-5,3,top-.35),550,5)
        if level:
            C.box('full upper arrival landing',(-5,3.62,z-.07),(3.1,1.2,.14),'floor','circulation')
            C.railing('rear stair aperture guard',(-6.5,8.44,z),(-3.5,8.44,z),spacing=.14)
        C.box('corridor notice board',(-11.5,-2.69,z+1.5),(1.4,.04,.85),'timber','rooms')
        for k in range(8):C.box('school coat cubby',(-12.8+k*.31,1,z+.65),(.27,.35,1.3),'furniture','rooms')
    # Main hall threshold: wide sidelights around a paired doorway and transom.
    for o in list(C.objects()):
        if o.name.startswith(('lobby glazing','door pull')):bpy.data.objects.remove(o,do_unlink=True)
    f=C.Face((-1.9,-9.7,0),(1,0,0),(0,1,0),'recessed lobby')
    for x in (-3.1,3.1):f.window('entrance sidelight '+str(x),x,.14,3.55,2.35,3,1,'trim',.10,sill=False)
    f.window('entrance transom',0,2.55,10.1,.58,8,1,'trim',.10,sill=False)
    for x in (-.6,.6):
        # Open paired glazed leaves, handles attached to actual leaves.
        d=C.Face((-1.9+x*2,-9.7,0),(0,1,0),(1 if x<0 else -1,0,0),'entry open leaf')
        d.window('paired glazed door '+str(x),.55,.14,1.1,2.35,1,1,'trim',.05,sill=False,kind='door')
        d.part('door push bar',.55,-.025,1.25,.9,.04,.035,'hardware')
    for i in range(36):C.box('canopy soffit slat',(-7+ i*.285,-10.2,3.13),(.22,1.65,.045),'timber','entry')
    for x in (-5.6,-1.9,1.8):lamp(x,-10.2,3.10,.22)
    for yy,sign in [(-7.5,1),(7.5,-1)]:hoop(9,yy,sign)
    for yy in (-6,0,6):
        lamp(9,yy,7.45,2)
        C.box('gym wall pad',(13.55,yy-1 if yy==6 else yy,1.25),(.18,1.6,2),'furniture','gym')
    tree(-14.9,-12.7,110);tree(13.7,-12.8,120)
    for x in (-10,9):C.box('forecourt lawn',(x,-14.3,.048),(7,1.0,.018),'plant','site',0)
    for y in (-14,-12.8,-11.6):C.box('entry paving joint',(-1.9,y,.047),(5.3,.025,.01),'stone','site',0)
    C.prism('graded entrance apron',[(-12.5,.04),(-11,.14),(-9.5,.14),(-9.5,.04)],'x',-7.1,3.2,'paving','site')

def extra_cameras(kind):
    if kind=='school':return [
        dict(name='corridor',location=(-12,0,1.75),target=(-3,-1,1.5),lens=24,whole=False),
        dict(name='stair_lower',location=(-5,2,1.7),target=(-5,6,2.7),lens=22,whole=False),
        dict(name='stair_landing',location=(-5.1,2.7,5.5),target=(-4.1,5.5,4),lens=24,whole=False),
        dict(name='top_landing',location=(-5.5,2.6,9.3),target=(-4,5.5,8),lens=24,whole=False),
        dict(name='classroom',location=(-12.8,-3.6,5.5),target=(-9.5,-8,4.8),lens=24,whole=False),
        dict(name='classroom_teaching',location=(-12.7,-9.6,5.6),target=(-9.7,-3.0,5.4),lens=24,whole=False),
        dict(name='gym_connection',location=(-1.5,-.5,1.8),target=(7,-.5,1.7),lens=28,whole=False)]
    return [dict(name='stair_lower',location=(0,-6.1,1.7),target=(0,-2,2.3),lens=23,whole=False),
            dict(name='stair_landing',location=(.65,-5.6,5.15),target=(0,-1,4),lens=24,whole=False),
            dict(name='apartment_access',location=(0,-.5,5.15),target=(0,2.5,4.8),lens=24,whole=False),
            dict(name='kitchen_bedroom',location=(-5.8,.2,1.7),target=(-4.9,5,1.3),lens=24,whole=False),
            dict(name='dwelling_entry',location=(0,2,5.1),target=(-3,1,4.8),lens=24,whole=False),
            dict(name='bathroom',location=(-3.05,1.15,1.95),target=(-3.10,2.65,1.1),lens=18,whole=False)]

def fourplex_interiors():
    for o in list(C.objects()):
        if o.name.startswith(('stair window bearing','front entry door','unit door')):bpy.data.objects.remove(o,do_unlink=True)
    # Slim sidelight, open entrance leaf and an unbroken clear upper stair light.
    f=C.Face((0,-6.5,0),(1,0,0),(0,1,0),'central entrance')
    f.part('entry dark transom spandrel',0,.10,2.905,1.95,.14,.43,'trim')
    f.part('stair top dark closure',0,.10,6.46,1.95,.14,.22,'trim')
    f.window('entry sidelight',-.70,.14,.42,2.55,1,1,'trim',.10,sill=False)
    f.part('entry door right jamb',.93,.10,1.415,.055,.12,2.55,'trim')
    d=C.Face((-.43,-6.5,0),(0,1,0),(1,0,0),'open entry')
    d.window('open entry glass leaf',.58,.14,1.16,2.55,1,1,'trim',.08,sill=False,kind='door')
    for level in range(2):
        z=.14+level*3.45;top=3.45*(level+1) if not level else 6.87
        ce=C.box('complete apartment ceiling',(0,0,top-.04),(15.4,13.4,.08),'ceiling','rooms',0)
        if not level:
            C.cut_box(ce,'stair ceiling opening',(0,-2.9,top),(2.45,4.6,.5))
            C.cut_box(ce,'double height stair front ceiling',(0,-6.2,top),(2.15,1.0,.5))
        else:
            upper=next(o for o in C.objects() if o.name.startswith('apartment floor') and max(v.co.z for v in o.data.vertices)>3)
            C.cut_box(upper,'unbroken stair light floor void',(0,-6.2,z),(2.15,1.0,.5))
            C.railing('front stair light guard',(-1.06,-5.69,z),(1.06,-5.69,z),spacing=.14)
        for s in (-1,1):
            f=C.Face((s*1.9,0,0),(0,1,0),(-s,0,0),'dwelling entrance')
            open_door(f,f'dwelling {level} {s}',1,z,1,2.2)
            C.box('unit door number',(s*1.82,.4,z+1.6),(.035,.12,.14),'hardware','rooms')
            f=C.Face((s*4.8,3.45,0),(1,0,0),(0,1,0),'bedroom partition')
            f.wall('bedroom wall',-2.7,2.7,z,top-.1,.12,'interior',[dict(id='bedroom access',u=0,z=z,w=.95,h=2.15)])
            open_door(f,'bedroom door',0,z,.95,2.15)
            C.box('kitchen backsplash',(s*7.32,2.1,z+1.18),(.035,2.3,.5),'stone','interior')
            C.box('kitchen sink',(s*6.8,2.1,z+.931),(.63,.55,.03),'hardware','interior')
            for k in range(4):C.box('kitchen cupboard handle',(s*6.22,1.3+k*.6,z+.58),(.03,.17,.025),'hardware','interior')
            C.box('bed pillow',(s*4.7,6.10,z+.64),(1.3,.42,.13),'ceiling','interior')
            C.box('cooktop',(s*6.8,1.3,z+.94),(.75,.58,.035),'hardware','interior')
            for dx in (-.19,.19):
                for dy in (-.14,.14):C.box('cooktop burner',(s*6.8+dx,1.3+dy,z+.965),(.22,.19,.012),'stone','interior',0)
            C.box('refrigerator',(s*6.9,.38,z+.95),(.78,.70,1.90),'ceiling','interior')
            C.box('fridge door seam',(s*6.49,.38,z+1.42),(.018,.70,.022),'hardware','interior',0)
            C.box('fridge handle',(s*6.47,.62,z+1.10),(.04,.04,.5),'hardware','interior')
            # Compact enclosed bath beside the kitchen, with a real doorway.
            bx=s*3.05
            f=C.Face((bx,1.75,0),(1,0,0),(0,1,0),'bathroom front')
            f.wall('bath front partition',-.80,.80,z,top-.1,.10,'interior',[dict(id='bath doorway',u=0,z=z,w=.95,h=2.1)])
            # Outward swing, outer hinge: the leaf clears both the vanity and entry.
            door=C.Face((bx,1.75,0),(-s,0,0),(0,-1,0),'outward bathroom door')
            open_door(door,'bath door',0,z,.95,2.1)
            for xx in (bx-.8,bx+.8):C.box('bath side partition',(xx,2.6,(z+top-.1)/2),(.10,1.7,top-.1-z),'interior','rooms',0)
            C.box('bath vanity',(bx-.42,3.0,z+.4),(.58,.5,.8),'timber','interior')
            C.box('bath basin',(bx-.42,3.0,z+.83),(.59,.52,.10),'ceiling','interior')
            C.box('toilet pedestal',(bx+.35,2.85,z+.22),(.34,.46,.44),'ceiling','interior')
            C.box('toilet cistern',(bx+.35,3.18,z+.54),(.4,.16,.68),'ceiling','interior')
            C.box('bath mirror',(bx-.42,3.36,z+1.4),(.6,.025,.8),'glass','interior')
            C.box('shower tray',(bx-.40,2.18,z+.04),(.66,.66,.08),'ceiling','interior')
            C.rod('shower riser',(bx-.72,2.18,z+.6),(bx-.72,2.18,z+2.05),.017,'hardware','interior')
            C.rod('shower arm',(bx-.72,2.18,z+2.05),(bx-.38,2.18,z+2.05),.017,'hardware','interior')
            C.box('shower head',(bx-.38,2.18,z+2.02),(.20,.20,.035),'hardware','interior')
            lamp(bx,2.6,top-.15,.35)
            C.qa_room_light('bathroom proof',(bx,2.6,top-.35),80,1.0)
            for yy in (-3,1,5):lamp(s*4.5,yy,top-.15,.8)
        lamp(0,-5.8,top-.18,.35)
        C.qa_room_light('clear stair volume',(0,-3,top-.3),300,3)
    for x,y in [(-3,2),(2,4),(3,-3)]:C.box('vent flashing boot',(x,y,6.97),(.46,.46,.08),'hardware','roof_equipment')
    tree(8.7,-8.9,200)
    C.railing('rear stair aperture guard',(-1.2,-.60,3.59),(1.2,-.60,3.59),spacing=.14)
    C.prism('graded entry garden walk',[(-8.5,.04),(-7,.14),(-6.5,.14),(-6.5,.04)],'x',-.45,.96,'paving','site')
    for x in (-4.8,4.8):C.box('front low meadow',(x,-10.3,.05),(5.6,.7,.025),'plant','site',0)

def circulation_corrections(kind):
    if kind=='school':
        # Connect gym and lobby through the real separating carrier.
        owner=next(o for o in C.objects() if o.name.startswith('right upper carrier'))
        C.cut_box(owner,'gym lobby through door',(4,-.5,1.39),(1.2,1.8,2.5))
        C.box('gym doorway continuous floor',(4,-.5,.09),(1.0,1.8,.18),'floor','circulation',0)
        f=C.Face((4,-.5,0),(0,1,0),(-1,0,0),'gym connection')
        open_door(f,'gym lobby door',0,.14,1.8,2.5)
        # Cut upper floor back to the same stair aperture as its ceiling.
        for o in list(C.objects()):
            if o.name.startswith('classroom floor slab'):
                z=max(v.co.z for v in o.data.vertices)
                if z>1:C.cut_box(o,'aligned full stair opening',(-5,6.25,z),(3.1,4.4,.6))
    # Guard the inner well edges without crossing either arrival landing.
    x,y,w,rise,levels=(-5,4.2,1.25,3.8,2) if kind=='school' else (0,-4.9,1.05,3.45,1)
    for level in range(levels):
        z=.14+level*rise
        for side in (-1,1):
            xx=x+side*.05*w;za=z if side<0 else z+rise
            C.beam('inner stair handrail',(xx,y,za+1),(xx,y+2.75,z+rise/2+1),.035,role='hardware')
            for j in range(7):
                zz=za+(z+rise/2-za)*j/6
                C.rod('inner well baluster',(xx,y+2.75*j/6,zz),(xx,y+2.75*j/6,zz+1),.014)
