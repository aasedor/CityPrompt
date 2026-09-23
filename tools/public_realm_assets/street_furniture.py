"""Native reusable street details. Metres/Z-up, modest geometry, no bitmap facades."""
import math
import scene as S
import sports_furniture as F

BOUNDS={}


def bollard():
    S.beam('bollard plinth',(0,0,0),(0,0,.10),.14,'metal',12)
    S.beam('bollard shaft',(0,0,.1),(0,0,.92),.07,'metal',12)
    S.beam('reflective collar',(0,0,.75),(0,0,.82),.073,'cream',12)
    S.beam('bollard cap',(0,0,.92),(0,0,.98),.085,'metal',12)


def lantern():
    S.beam('lamp base',(0,0,0),(0,0,.25),.18,'metal',12)
    S.beam('lamp column',(0,0,.25),(0,0,3.22),.065,'metal',10)
    for z in (.3,2.9,3.16):S.beam('lamp collar',(0,0,z),(0,0,z+.06),.1,'metal',12)
    S.box('lantern sill',(0,0,3.24),(.45,.45,.08),'metal')
    S.box('frosted lantern',(0,0,3.52),(.29,.29,.46),'lamp_lens')
    for x in (-.18,.18):
        for y in (-.18,.18):S.beam('lantern frame',(x,y,3.26),(x,y,3.80),.018,'metal')
    S.mesh('lantern roof',[(-.29,-.29,3.82),(.29,-.29,3.82),(.29,.29,3.82),(-.29,.29,3.82),(0,0,4.03)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],'metal')


def shelter():
    # Roof 4.4 x 1.8, open front; seat tucked against rear glass.
    for x in (-2,2):
        for y in (-.7,.7):S.box('shelter post',(x,y,1.35),(.075,.075,2.7),'metal')
    S.box('thin shelter roof',(0,0,2.73),(4.4,1.8,.10),'metal')
    S.box('roof translucent inset',(0,0,2.792),(4.1,1.55,.024),'glass')
    for x in (-1,1):
        S.box('rear glass',(x,.70,1.40),(1.88,.018,2.2),'glass')
        S.box('glass safety stripe',(x,.682,1.12),(1.88,.01,.035),'cream')
    S.box('side windscreen',(-2,0,1.40),(.018,1.3,2.2),'glass')
    for yy in (.22,.34,.46):S.box('shelter seat slat',(0,yy,.46),(2.65,.10,.055),'timber')
    for x in (-1.1,1.1):S.box('shelter seat leg',(x,.34,.23),(.055,.40,.46),'metal')
    S.box('information panel',(1.45,.66,1.55),(.7,.035,1.0),'cream')
    for i in range(6):S.box('map diagram',(1.4,.633,1.25+i*.11),(.48,.012,.012),'sage')


def stop_pole():
    S.beam('stop pole',(0,0,0),(0,0,3.2),.038,'metal',10)
    S.box('stop sign',(0,0,2.86),(.6,.08,.60),'sage')
    S.box('bus icon body',(0,-.045,2.87),(.37,.012,.24),'cream')
    S.box('bus window',(0,-.054,2.91),(.28,.01,.08),'metal')
    for x in (-.13,.13):S.box('bus icon wheel',(x,-.055,2.70),(.06,.01,.045),'cream')
    S.box('timetable holder',(0,0,1.58),(.27,.06,.46),'cream')


def stall():
    for x in (-1.25,1.25):
        for y in (-.65,.65):S.box('stall frame',(x,y,1.22),(.065,.065,2.44),'timber')
    for x in (-.9,.9):S.box('counter leg',(x,0,.45),(.09,.85,.9),'timber')
    S.box('market counter',(0,0,.93),(2.6,1.35,.09),'timber')
    for i in range(10):
        x=-1.42+i*.284
        S.mesh('striped stall canopy',[(x,-.95,2.4),(x+.284,-.95,2.4),(x+.284,0,2.82),(x,0,2.82),
            (x,.95,2.4),(x+.284,.95,2.4)],[(0,1,2,3),(3,2,5,4)],'canvas' if i%2==0 else 'sage')
    for x in (-.85,0,.85):
        S.box('produce crate',(x,0,1.05),(.70,.83,.15),'timber')
        for i in range(3):
            for j in range(3):S.beam('produce',(x-.20+i*.2,-.23+j*.23,1.12),(x-.20+i*.2,-.23+j*.23,1.20),.083,'produce',8)


def ring(name,outer,inner,z,h,material):
    n=48;verts=[(r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),zz) for zz in (z,z+h) for r in (outer,inner) for i in range(n)]
    faces=[]
    for i in range(n):
        j=(i+1)%n;faces.extend([(i,j,2*n+j,2*n+i),(n+i,3*n+i,3*n+j,n+j),
                             (2*n+i,2*n+j,3*n+j,3*n+i),(i,n+i,n+j,j)])
    S.mesh(name,verts,faces,material)


def fountain():
    S.beam('basin base',(0,0,0),(0,0,.08),1.73,'warm_concrete',48)
    ring('stone basin rim',1.8,1.52,.08,.40,'warm_concrete')
    S.beam('fountain water',(0,0,.32),(0,0,.335),1.52,'water',48)
    S.beam('fountain pedestal',(0,0,.08),(0,0,1.16),.16,'warm_concrete',16)
    S.beam('upper bowl',(0,0,1.1),(0,0,1.19),.55,'warm_concrete',32)
    ring('upper bowl edge',.55,.48,1.19,.10,'warm_concrete')
    S.beam('upper water',(0,0,1.23),(0,0,1.24),.48,'water',32)
    for i in range(8):
        a=i*math.tau/8
        for j in range(8):
            t=j/8;u=(j+1)/8
            p=lambda v:((.50+v*.48)*math.cos(a),(.50+v*.48)*math.sin(a),1.24-.90*v*v)
            S.beam('thin water stream',p(t),p(u),.009,'water',5)


def trellis():
    S.box('raised bed base',(0,0,.06),(2.7,1,.12),'timber')
    for y in (-.47,.47):
        for z in (.18,.36,.54):S.box('raised bed board',(0,y,z),(2.8,.08,.16),'timber')
    for x in (-1.35,1.35):S.box('bed end',(x,0,.33),(.10,1,.60),'timber')
    S.box('raised soil',(0,0,.52),(2.6,.83,.05),'soil')
    for x in (-1.3,1.3):S.box('trellis post',(x,.39,1.24),(.08,.08,2.48),'timber')
    for i in range(9):S.box('trellis upright',(-1.2+i*.3,.4,1.57),(.025,.04,1.75),'timber')
    for i in range(7):S.box('trellis crossbar',(0,.40,.8+i*.26),(2.6,.03,.028),'timber')
    # Small separate leaves keep the lattice visible.
    for i in range(30):
        x=-1.15+(i*0.43)%2.3;z=.72+(i*0.31)%1.56
        S.mesh('climbing leaf',[(x-.12,.37,z),(x,.34,z+.19),(x+.12,.35,z),(x,.38,z-.06)],[(0,1,2),(0,2,3)],'vine')
    for i in range(7):
        x=-1.1+i*.36;S.beam('planter foliage',(x,0,.54),(x,.06,.94),.11,'vine',7)


def fence_panel():
    for x in (-1.45,1.45):S.box('fence post',(x,0,.9),(.12,.12,1.8),'timber')
    for z in (.4,1.35):S.box('fence rail',(0,.06,z),(3,.075,.10),'timber')
    for i in range(20):S.box('fence picket',(-1.425+i*.15,-.015,.86),(.10,.045,1.64),'timber')


def guard():
    for x in (-1.45,1.45):S.box('boardwalk guard post',(x,0,.58),(.13,.13,1.16),'timber')
    for z in (.14,1.10):S.box('boardwalk guard rail',(0,0,z),(3.05,.13,.12),'timber')
    for i in range(24):S.beam('guard infill',(-1.38+i*.12,0,.19),(-1.38+i*.12,0,1.05),.013,'metal')


def hammock():
    for x in (-2,2):
        S.beam('hammock post',(x,0,0),(x,0,1.85),.085,'timber',10)
        S.beam('hammock suspension',(x,0,1.65),(math.copysign(1.65,x),0,1.30),.013,'cream')
    for i in range(24):
        x=-1.65+i*3.3/24;xx=x+3.3/24
        p=lambda a,b:(a,b*(.50*(1-(a/1.9)**2)),.58+.72*(a/1.65)**2+.1*b*b)
        S.mesh('woven hammock',[p(x,-1),p(xx,-1),p(xx,1),p(x,1)],[(0,1,2,3)],'canvas' if i%3 else 'terracotta')
    for i in range(9):
        y=-.32+i*.08
        for side in (-1,1):S.beam('hammock end cords',(side*1.65,y,1.32),(side*2,0,1.65),.006,'cream',4)


def kiosk():
    S.box('kiosk plinth',(0,0,.06),(2.5,2.2,.12),'warm_concrete')
    S.box('kiosk lower body',(0,0,.54),(2.3,2,.95),'sage')
    for x in (-1.1,1.1):
        for y in (-.95,.95):S.box('kiosk post',(x,y,1.70),(.075,.075,2.35),'metal')
    for y in (-.96,.96):
        S.box('kiosk display frame',(0,y,1.60),(2.2,.065,1.1),'metal')
        for i in range(4):
            for j in range(2):
                S.box('magazine cover',(-.8+i*.53,y-math.copysign(.05,-y),1.32+j*.50),(.39,.012,.38),'cream' if (i+j)%2 else 'terracotta')
    S.mesh('kiosk hipped roof',[(-1.45,-1.3,2.55),(1.45,-1.3,2.55),(1.45,1.3,2.55),(-1.45,1.3,2.55),(0,0,3.1)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],'metal')
    S.box('kiosk counter',(0,-1.04,1.05),(2.45,.35,.10),'timber')


BUILDERS={'heritage_lantern':lantern,'street_bollard':bollard,'transit_shelter':shelter,
          'transit_stop_pole':stop_pole,'market_stall':stall,'stone_fountain':fountain,
          'planted_trellis':trellis,'timber_fence_panel':fence_panel,'boardwalk_guard':guard,
          'boardwalk_hammock':hammock,'promenade_kiosk':kiosk,
          'cafe_table_chairs':F.cafe_set,'cafe_parasol':F.parasol,'timber_seat_wall':F.seat_wall}


def init():
    BOUNDS.clear()
    for name,c in {'cream':(.79,.74,.62),'lamp_lens':(.90,.87,.66),'sage':(.10,.20,.16),
        'canvas':(.74,.68,.54),'canvas_shade':(.62,.57,.44),'warm_concrete':(.52,.49,.40),
        'water':(.10,.32,.34),'glass':(.49,.68,.68),'terracotta':(.49,.21,.10),
        'vine':(.13,.24,.065),'produce':(.42,.18,.06)}.items():F.material(name,c)
    glass=S.MATS['glass'].node_tree.nodes['Principled BSDF'];glass.inputs['Transmission Weight'].default_value=.80
    glass.inputs['Roughness'].default_value=.18
    for kind,builder in BUILDERS.items():
        before=set(S.bpy.context.scene.objects);builder();objects=list(set(S.bpy.context.scene.objects)-before)
        pts=[v.co for o in objects for v in o.data.vertices]
        BOUNDS[kind]=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
        S.KIT[kind]=[o.data for o in objects]
        for o in objects:S.bpy.data.objects.remove(o,do_unlink=True)


def place(r,kind,x,y,yaw=0):
    objects=S.kit(kind,x,y,0,yaw);S.bpy.context.view_layer.update()
    pts=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
    r.setdefault('reference_assets',[]).append(dict(kind=kind,x=x,y=y,yaw=yaw,
        bounds_m=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]],native_bounds_m=BOUNDS[kind]))
    return objects
