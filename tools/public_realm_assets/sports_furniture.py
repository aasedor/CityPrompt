"""Small native sports amenities derived from the catalogue reference images.

Metric Z-up prototypes at the origin, shared by instances and exported as GLBs.
No people, logos, provider calls or building/clubhouse generation.
"""
import math
import scene as S
from mathutils import Vector

BOUNDS={}

def material(name,colour):
    m=S.bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*colour,1)
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*colour,1)
    m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.78
    S.MATS[name]=m

def player_bench():
    for y in (-.15,0,.15):S.box('bench slat',(0,y,.455),(3,.13,.055),'timber')
    for x in (-1.1,1.1):
        S.box('bench foot',(x,0,.035),(.15,.54,.07),'metal')
        S.box('bench leg',(x,0,.23),(.065,.3,.39),'metal')

def covered_bench():
    player_bench()
    for x in (-1.65,1.65):
        for y in (-.70,.72):
            h=2.66+y*.13
            S.box('shelter foot',(x,y,.045),(.22,.22,.09),'metal')
            S.box('shelter post',(x,y,h/2),(.12,.12,h),'timber')
        S.beam('roof carrier',(x,-.95,2.57),(x,.95,2.82),.07,'timber',4)
    # Thin folded roof and fascia, with an honest front-to-rear pitch.
    for i in range(15):
        y=-.94+i*.135;z=2.70+y*.13
        S.box('roof standing seam',(0,y,z),(3.85,.018,.06),'metal')
    S.mesh('roof sheet',[(-1.93,-1,2.57),(1.93,-1,2.57),(1.93,1,2.83),(-1.93,1,2.83)],[(0,1,2,3)],'shelter_roof')
    for y in (-.95,.95):S.box('timber fascia',(0,y,2.69+y*.13),(3.9,.09,.16),'timber')
    for z in (.68,.88,1.08):S.box('bench back slat',(0,.27,z),(3,.055,.10),'timber')

def bleachers():
    # Low three-row neighbourhood stand, open ground-level approach in front.
    for i in range(3):
        y=-.75+i*.68;z=.43+i*.33
        for yy in (-.13,.13):S.box('aluminium seat',(0,y+yy,z),(4.8,.235,.05),'aluminium')
        if i:S.box('foot board',(0,y-.33,z-.37),(4.8,.25,.045),'aluminium')
        for x in (-2.12,0,2.12):
            S.box('stand upright',(x,y,(z-.025)/2),(.065,.065,z-.025),'metal')
    for x in (-2.12,0,2.12):
        S.box('stand skid',(x,0,.035),(.13,2.05,.07),'metal')
        S.beam('raking support',(x,-.87,.24),(x,.81,.96),.03,'metal')
    for x in (-2.36,2.36):
        for y in (-.13,.90):S.beam('stand guard',(x,y,0),(x,y,1.95),.024,'metal')
        S.beam('side guard',(x,-.13,1.55),(x,.9,1.95),.024,'metal')
    for z in (1.35,1.65,1.95):S.beam('back rail',(-2.36,.9,z),(2.36,.9,z),.022,'metal')

def seat_wall():
    S.box('concrete seat plinth',(0,0,.21),(3.6,.65,.42),'warm_concrete')
    for i in range(24):S.box('seat wall timber cap',(-1.725+i*.15,0,.45),(.135,.69,.06),'timber')

def cafe_set():
    S.beam('round cafe table',(0,0,.71),(0,0,.75),.48,'timber',24)
    S.beam('table pedestal',(0,0,.035),(0,0,.71),.04,'metal',10)
    S.beam('table foot',(0,0,.01),(0,0,.035),.28,'metal',16)
    for yaw in (0,math.pi/2,math.pi,3*math.pi/2):
        c,s=math.cos(yaw),math.sin(yaw)
        pos=lambda x,y,z:(x*c-y*s,x*s+y*c,z)
        for x in (-.17,.17):
            for y in (.6,.94):S.beam('cafe chair leg',pos(x,y,0),pos(x,y,.46),.017,'metal',6)
            S.beam('cafe back upright',pos(x,.94,.40),pos(x,.94,.84),.016,'metal',6)
        for yy in (.63,.72,.81,.90):S.beam('chair seat',pos(-.2,yy,.45),pos(.2,yy,.45),.027,'timber',4)
        for z in (.65,.78):S.beam('chair back',pos(-.2,.94,z),pos(.2,.94,z),.035,'timber',4)

def parasol():
    cafe_set()
    S.beam('parasol mast',(0,0,0),(0,0,2.9),.035,'timber',10)
    for i in range(16):
        a=math.tau*i/16;b=math.tau*(i+1)/16
        va=(1.55*math.cos(a),1.55*math.sin(a),2.32);vb=(1.55*math.cos(b),1.55*math.sin(b),2.32)
        S.mesh('fabric canopy',[(0,0,2.86),va,vb],[(0,1,2)],'canvas' if i%2==0 else 'canvas_shade')
        if i%2==0:S.beam('parasol rib',(0,0,2.84),va,.012,'metal',5)

def referee_stand():
    # Stable freestanding observation chair; no generated person.
    for x in (-.42,.42):
        S.beam('chair ladder',(x,-.7,0),(x,.1,1.75),.025,'aluminium')
        S.beam('chair rear leg',(x,.55,0),(x,.1,1.75),.025,'aluminium')
        S.beam('chair side rail',(x,-.15,1.65),(x,-.15,2.40),.022,'aluminium')
        S.beam('chair hand rail',(x,-.15,2.40),(x,.40,2.40),.022,'aluminium')
        S.box('non slip foot',(x,-.7,.025),(.15,.18,.05),'padding')
        S.box('non slip foot',(x,.55,.025),(.15,.18,.05),'padding')
    for i in range(1,6):
        z=i*.28;y=-.7+.8*z/1.75
        S.beam('ladder tread',(-.42,y,z),(.42,y,z),.024,'aluminium')
    S.box('referee platform',(0,.12,1.7),(.9,.64,.06),'aluminium')
    S.box('referee seat',(0,.12,1.99),(.57,.45,.065),'timber')
    for x in (-.23,.23):S.beam('seat leg',(x,.12,1.73),(x,.12,1.96),.02,'metal')
    S.box('chair back',(0,.35,2.23),(.6,.055,.35),'timber')

def floodlight():
    S.box('light base',(0,0,.08),(.32,.32,.16),'metal')
    S.beam('court light mast',(0,0,.08),(0,0,6.5),.065,'metal',10)
    S.beam('head crossarm',(-.52,0,6.45),(.52,0,6.45),.034,'metal')
    for x in (-.38,.38):
        S.box('floodlight housing',(x,.08,6.48),(.46,.28,.17),'metal')
        S.box('floodlight lens',(x,.08,6.387),(.40,.23,.018),'lamp_lens')
        for xx in (-.12,0,.12):S.box('lens divider',(x+xx,.08,6.376),(.008,.23,.008),'aluminium')

def vine_pergola():
    w,d=7,3.3
    for x in (-3.35,3.35):
        for y in (-1.5,1.5):
            S.box('arbour post',(x,y,1.45),(.18,.18,2.9),'timber')
            S.box('arbour shoe',(x,y,.06),(.23,.23,.12),'metal')
            S.beam('arbour knee brace',(x,y,2.1),(x-math.copysign(.7,x),y,2.85),.065,'timber',4)
    for y in (-1.5,1.5):S.box('arbour beam',(0,y,2.9),(7.3,.18,.25),'timber')
    for i in range(23):S.box('arbour rafters',(-3.52+i*.32,0,3.08),(.09,3.6,.18),'timber')
    # Sparse vines read as foliage over structure, rather than a solid roof blob.
    for j in range(4):
        y=-1.2+j*.8
        for i in range(20):
            x=-3.2+i*.33;yy=y+.10*math.sin(i*1.7+j)
            S.beam('vine stem',(x,yy,3.21),(x+.33,y+.10*math.sin((i+1)*1.7+j),3.21),.012,'timber',4)
            for side in (-1,1):
                S.mesh('vine leaf',[(x,yy,3.22),(x+.10,yy+side*.25,3.25),(x+.26,yy+side*.34,3.21),(x+.28,yy+side*.12,3.25)],[(0,1,2),(0,2,3)],'vine')

def festoon():
    for x in (-3.1,3.1):
        S.beam('festoon pole',(x,0,0),(x,0,3.2),.04,'metal',8)
        S.box('festoon foot',(x,0,.04),(.24,.24,.08),'metal')
    for i in range(32):
        x=-3.1+i*6.2/32;xx=x+6.2/32
        z=lambda p:2.78+.4*(p/3.1)**2
        S.beam('light cable',(x,0,z(x)),(xx,0,z(xx)),.006,'metal',4)
        if i%3==0:
            S.beam('bulb stem',(x,0,z(x)),(x,0,z(x)-.08),.008,'metal',5)
            S.beam('festoon globe',(x,0,z(x)-.14),(x,0,z(x)-.08),.035,'lamp_lens',8)

BUILDERS={'player_bench':player_bench,'covered_player_bench':covered_bench,
          'spectator_bleachers':bleachers,'timber_seat_wall':seat_wall,
          'cafe_table_chairs':cafe_set,'cafe_parasol':parasol,
          'referee_stand':referee_stand,'court_floodlight':floodlight,
          'vine_pergola':vine_pergola,'festoon_lights':festoon}

def init():
    BOUNDS.clear()
    for name,colour in {'aluminium':(.53,.57,.57),'warm_concrete':(.49,.47,.41),
        'shelter_roof':(.12,.15,.14),'canvas':(.75,.70,.57),'canvas_shade':(.66,.61,.49),
        'lamp_lens':(.88,.86,.71),'vine':(.12,.23,.075)}.items():material(name,colour)
    for kind,builder in BUILDERS.items():
        before=set(S.bpy.context.scene.objects);builder()
        objects=list(set(S.bpy.context.scene.objects)-before)
        pts=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
        BOUNDS[kind]=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
        S.KIT[kind]=[o.data for o in objects]
        for o in objects:S.bpy.data.objects.remove(o,do_unlink=True)

def place(r,kind,x,y,yaw=0):
    objects=S.kit(kind,x,y,0,yaw)
    # Update object matrices before measuring the actual transformed vertices.
    S.bpy.context.view_layer.update()
    pts=[o.matrix_world@v.co for o in objects for v in o.data.vertices]
    bounds=[[min(p[i] for p in pts) for i in range(3)],[max(p[i] for p in pts) for i in range(3)]]
    r.setdefault('reference_assets',[]).append(dict(kind=kind,x=x,y=y,yaw=yaw,bounds_m=bounds,native_bounds_m=BOUNDS[kind]))
    return objects
