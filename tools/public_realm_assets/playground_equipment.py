"""Finite, metre-scale timber play equipment for the reference playground.

Concept geometry: the model does not assert playground safety certification.
"""
import math
import scene as S


def record(name,before,x=0,y=0):
    S.RIGID[name]=([o for o in set(S.bpy.context.scene.objects)-before if o.type=='MESH'],x,y)
    S.PLACEMENTS.append(dict(kind=name,x=x,y=y,z=0,yaw=0,scale=1))


def deck(x,y,w,d,z):
    count=math.ceil(w/.15)
    for i in range(count):S.box('deck board',(x-w/2+(i+.5)*w/count,y,z-.035),(w/count-.008,d,.07),'timber')
    for dx in (-w/2+.12,w/2-.12):S.box('deck bearer',(x+dx,y,z-.17),(.14,d,.2),'timber')


def railing(a,b):
    length=math.dist(a,b);n=max(1,math.ceil(length/1.4))
    for i in range(n+1):
        p=[a[j]+(b[j]-a[j])*i/n for j in range(3)]
        S.beam('guard post',p,(p[0],p[1],p[2]+.95),.052,'timber',8)
    for z in (.14,.92):S.beam('guard rail',(a[0],a[1],a[2]+z),(b[0],b[1],b[2]+z),.035,'metal',8)
    for i in range(1,math.ceil(length/.14)):
        t=i/math.ceil(length/.14);p=[a[j]+(b[j]-a[j])*t for j in range(3)]
        S.beam('guard infill',(p[0],p[1],p[2]+.14),(p[0],p[1],p[2]+.92),.018,'timber',6)


def roof(x,y):
    # Individual sloping boards give the two pitched roofs physical edges.
    for side in (-1,1):
        for i in range(22):
            yy=y-1.65+(i+.5)*3.3/22
            S.beam('roof board',(x,yy,3.65),(x+side*1.72,yy,2.95),.083,'timber',4)
        for yy in (y-1.7,y+1.7):S.beam('gable fascia',(x,yy,3.68),(x+side*1.77,yy,2.95),.075,'timber',4)
    S.beam('ridge cap',(x,y-1.78,3.69),(x,y+1.78,3.69),.065,'timber',4)


def slide(x,y,dx,dy,mat):
    # A sloping trough and raised side lips, never a flat blue projection.
    for i in range(28):
        t=i/28;u=(i+1)/28
        a=(x+dx*t,y+dy*t,.10+.85*(1-t)**1.45)
        b=(x+dx*u,y+dy*u,.10+.85*(1-u)**1.45)
        length=math.hypot(dx,dy);nx=-dy/length*.44;ny=dx/length*.44
        S.mesh('slide bed',[(a[0]-nx,a[1]-ny,a[2]),(a[0]+nx,a[1]+ny,a[2]),
                            (b[0]+nx,b[1]+ny,b[2]),(b[0]-nx,b[1]-ny,b[2])],[(0,1,2,3)],mat)
        for sign in (-1,1):
            S.mesh('slide raised lip',[(a[0]+sign*nx,a[1]+sign*ny,a[2]),(b[0]+sign*nx,b[1]+sign*ny,b[2]),
                                      (b[0]+sign*nx,b[1]+sign*ny,b[2]+.18),(a[0]+sign*nx,a[1]+sign*ny,a[2]+.18)],[(0,1,2,3)],mat)
    for t in (.12,.55):
        z=.10+.85*(1-t)**1.45
        S.beam('slide support',(x+dx*t,y+dy*t,0),(x+dx*t,y+dy*t,z),.055,'metal',8)


def main_structure():
    before=set(S.bpy.context.scene.objects)
    for x in (0,3.5):
        deck(x,6,2.8,2.8,.95);roof(x,6)
        for dx in (-1.22,1.22):
            for dy in (-1.22,1.22):
                S.box('tower timber column',(x+dx,6+dy,1.51),(.15,.15,3.02),'timber')
                S.box('post shoe',(x+dx,6+dy,.055),(.22,.22,.11),'metal')
        railing((x-1.35,7.35,.95),(x+1.35,7.35,.95))
        # Front slide / stair opening is physically open between guard panels.
        for a,b in ((x-1.35,x-.50),(x+.50,x+1.35)):railing((a,4.65,.95),(b,4.65,.95))
    deck(1.75,6,.8,1.7,.95)
    for yy in (5.15,6.85):railing((1.4,yy,.95),(2.1,yy,.95))
    # 11.4 m run / .95 m rise, with a full-width top landing and connector.
    for i in range(76):
        y=-5.8+(i+.5)*11.4/76;z=.95*(i+.5)/76
        S.box('ramp tread',(-5,y,z-.035),(1.8,11.4/76-.005,.07),'timber')
    for x in (-5.97,-4.03):railing((x,-5.8,0),(x,5.6,.95))
    for y in (-4,0,4,5.6):
        z=.95*(y+5.8)/11.4
        for x in (-5.75,-4.25):S.box('ramp support',(x,y,z/2),(.12,.12,z),'timber')
    deck(-3.65,6.5,4.5,1.8,.95)
    railing((-5.9,7.4,.95),(-1.4,7.4,.95));railing((-4.03,5.6,.95),(-1.4,5.6,.95))
    railing((4.85,4.65,.95),(4.85,5.48,.95));railing((4.85,6.52,.95),(4.85,7.35,.95))
    slide(0,4.6,0,-4.1,'slide_amber');slide(4.9,6,4.4,0,'slide_charcoal')
    for i in range(5):
        z=(i+1)*.19;y=3.2+i*.28
        S.box('climbing stair',(3.5,y,z/2),(.90,.28,z),'timber')
    for x in (2.94,4.06):S.beam('stair handrail',(x,3,.65),(x,4.5,1.75),.035,'metal',8)
    # A small game panel on the far side; exposed support stays visible.
    S.box('play panel',(3.5,7.34,1.55),(1.1,.045,.85),'play_green')
    for i in range(3):S.beam('play panel spinner',(3.17+i*.33,7.29,1.55),(3.17+i*.33,7.24,1.55),.12,'slide_amber',16)
    record('timber_ramp_two_tower_play_v2',before)


def swings(x,y):
    before=set(S.bpy.context.scene.objects)
    for dx in (-3.4,3.4):
        for dy in (-1.5,1.5):
            S.beam('swing timber leg',(x+dx,y+dy,0),(x+dx,y,3.05),.11,'timber',10)
            S.box('swing footing',(x+dx,y+dy,.045),(.26,.26,.09),'metal')
    S.beam('swing top beam',(x-3.65,y,3.05),(x+3.65,y,3.05),.13,'timber',10)
    for i,dx in enumerate((-1.6,1.6)):
        mat='play_green' if i==0 else 'metal'
        S.box('supported swing seat',(x+dx,y,.62),(.58,.54,.09),mat)
        S.box('swing back',(x+dx,y+.24,.98),(.58,.07,.73),mat)
        for side in (-1,1):
            S.beam('swing side support',(x+dx+side*.26,y-.23,.63),(x+dx+side*.26,y+.23,1.05),.028,'metal',8)
            for dy in (-.18,.18):S.beam('swing chain',(x+dx+side*.28,y+dy,.70),(x+dx+side*.31,y+dy*.25,2.92),.012,'metal',8)
    record('supported_swing_pair_v2',before,x,y)


def sensory(x,y):
    before=set(S.bpy.context.scene.objects)
    for dx in (-.85,.85):S.box('sensory post',(x+dx,y,.90),(.12,.12,1.8),'timber')
    S.box('sensory board',(x,y,1.02),(1.65,.10,1.3),'play_green')
    for i in range(3):
        for j in range(3):
            S.beam('sensory rotating disc',(x+(i-1)*.43,y-.06,.6+j*.4),(x+(i-1)*.43,y-.13,.6+j*.4),.14,'slide_amber',20)
            S.beam('sensory grip',(x+(i-1)*.43,y-.14,.6+j*.4),(x+(i-1)*.43,y-.19,.6+j*.4),.04,'metal',12)
    record('nine_disc_sensory_panel_v2',before,x,y)


def canopy(x,y):
    before=set(S.bpy.context.scene.objects)
    for dx in (-2.15,2.15):
        S.box('shelter upright',(x+dx,y+.65,1.32),(.16,.16,2.64),'timber')
        S.beam('shelter brace',(x+dx,y+.65,2),(x+dx,y-.8,2.55),.065,'timber',8)
    for i in range(32):S.box('shelter roof board',(x-2.5+(i+.5)*5/32,y,2.65),(5/32-.006,3.2,.10),'timber')
    for yy in (y-1.35,y+1.35):S.box('shelter fascia',(x,yy,2.61),(5,.12,.20),'timber')
    record('timber_seating_shelter_v2',before,x,y)
    for yy in (y-.45,y+.45):S.kit('backless_bench',x,yy,0,0,1)
