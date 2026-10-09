"""Twenty metric site props, authored in Z-up and exported to Y-up GLB.

Python --dry-run performs no writes. Blender --id accessible-ramp creates the
pilot; omit --id for the finite twenty-object batch. Each output must be fresh.
Walking profiles use untransformed GLB local x/z and heights (before offset).
"""
import argparse
import json
import math
from pathlib import Path
import sys

SPECS = [
    ('outdoor-stairs', 'Outdoor stairs', 'Access & levels', 'Six 150 mm concrete risers, 300 mm treads, upper landing and twin handrails.'),
    ('accessible-ramp', 'Accessible ramp', 'Access & levels', 'Straight 1:12 concept ramp with 1.5 m landings, 1.8 m clear width and dual-height rails.'),
    ('modular-handrail', 'Modular handrail', 'Access & levels', 'Repeatable three-metre steel handrail with intermediate rail and bolted base plates.'),
    ('retaining-wall', 'Retaining wall', 'Access & levels', 'Three-metre precast retaining-wall segment with coping, joints and drainage outlets.'),
    ('refuge-island', 'Pedestrian refuge island', 'Traffic & safety', 'Raised rounded island ends around a ground-level pedestrian refuge with tactile strips.'),
    ('planted-curb-extension', 'Planted curb extension', 'Landscape', 'Curb extension with planted soil, flowering grasses and curb drainage openings.'),
    ('tactile-curb-ramp', 'Tactile curb ramp', 'Access & levels', 'Flush-entry ramp with flared sides, raised landing and tactile warning domes.'),
    ('covered-bike-parking', 'Covered bicycle parking', 'Shelters & markets', 'Open steel cycle canopy with six inverted-U bicycle stands.'),
    ('bicycle-locker', 'Bicycle locker', 'Street furniture', 'Two secure bicycle compartments with overhanging roof, vents and door handles.'),
    ('ev-charger', 'EV charging station', 'Street furniture', 'Twin-cable charging pedestal with screens, connectors and protective bollards.'),
    ('accessible-parking', 'Accessible parking bay', 'Traffic & safety', 'Concept parking bay and hatched access aisle with wheelchair symbol, wheel stop and sign; verify local requirements.'),
    ('loading-zone', 'Loading zone', 'Traffic & safety', 'Concept loading bay with curbside sign and yellow end markings; verify local requirements.'),
    ('waste-enclosure', 'Waste enclosure', 'Edges & gates', 'Slatted three-sided service enclosure with two lidded bins and open access.'),
    ('privacy-screen', 'Privacy screen', 'Edges & gates', 'Repeatable timber privacy panel with steel posts, horizontal slats and foot plates.'),
    ('public-art', 'Public art sculpture', 'Water & landmarks', 'Interwoven bronze ribbon sculpture on a low circular stone plinth.'),
    ('food-truck', 'Food truck', 'Shelters & markets', 'Parked catering truck with real serving opening, raised canopy, menu and counter.'),
    ('cafe-barrier', 'Cafe barrier', 'Edges & gates', 'Repeatable weighted cafe windbreak with metal frame and woven infill.'),
    ('community-noticeboard', 'Community noticeboard', 'Street furniture', 'Roofed timber community board with pinned notices and glazed-looking inset.'),
    ('rainwater-cistern', 'Rainwater cistern', 'Garden & growing', 'Ribbed collection tank with inlet, inspection lid, overflow pipe and tap.'),
    ('public-washroom', 'Public washroom', 'Shelters & markets', 'Small open-door washroom prop with toilet, basin, grab rails and interior clearance.'),
]


def walk_surface(kind):
    if kind == 'accessible-ramp':
        pairs = [(-5.1, 0), (-3.6, 0), (3.6, .6), (5.1, .6)]
        width, interpolation = 1.8, 'linear'
    elif kind == 'outdoor-stairs':
        pairs = [(-1.5, 0)]
        for i in range(6):
            z = round(-1.5+i*.3, 4)
            pairs.extend([(z, round(i*.15, 4)), (z, round((i+1)*.15, 4))])
        pairs.append((1.5, .9))
        width, interpolation = 1.8, 'step'
    elif kind == 'tactile-curb-ramp':
        pairs = [(-1.5, 0), (.3, .15), (1.5, .15)]
        width, interpolation = 1.5, 'linear'
    else:
        return None
    return dict(type='profile', width=width, interpolation=interpolation,
                stations=[dict(z=z, height=h) for z, h in pairs])


def build(kind, S, bpy):
    box, beam = S.box, S.beam

    def label(text, xyz, size, mat='cream', floor=False):
        curve = bpy.data.curves.new('lettering', 'FONT')
        curve.body=text; curve.align_x='CENTER'; curve.align_y='CENTER'; curve.size=size
        curve.extrude=.0007; curve.resolution_u=2
        obj=bpy.data.objects.new(text,curve); bpy.context.collection.objects.link(obj)
        obj.location=xyz; obj.rotation_euler=(0,0,0) if floor else (math.pi/2,0,0)
        curve.materials.append(S.MATS[mat]); bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True); bpy.context.view_layer.objects.active=obj; bpy.ops.object.convert(target='MESH')

    def profile(name, width, pairs, mat='concrete', center=0):
        # z in the walk contract is Blender -y. Closed solid down to ground.
        verts=[]
        for q,h in pairs: verts.extend([(center-width/2,-q,h),(center+width/2,-q,h)])
        n=len(verts); verts.extend([(center-width/2,-pairs[0][0],-.015),(center+width/2,-pairs[0][0],-.015),(center-width/2,-pairs[-1][0],-.015),(center+width/2,-pairs[-1][0],-.015)])
        faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(pairs)-1)]
        faces += [(n,n+1,1,0),(n+2,2*len(pairs)-2,2*len(pairs)-1,n+3),(n,n+2,n+3,n+1),tuple([n]+list(range(0,n,2))+[n+2]),tuple([n+1,n+3]+list(reversed(range(1,n,2))))]
        S.mesh(name,verts,faces,mat)

    def rail(x, stations):
        for q,h in stations:
            box('rail base',(x,-q,h+.012),(.14,.14,.024),'steel')
            beam('upright',(x,-q,h+.02),(x,-q,h+1.02),.024,'steel',10)
        for a,b in zip(stations,stations[1:]):
            for rise in (.7,1.02):beam('continuous handrail',(x,-a[0],a[1]+rise),(x,-b[0],b[1]+rise),.025,'steel',12)

    def slats(width, depth, height, y=0):
        for x in (-width/2+.06,width/2-.06):
            box('post',(x,y,height/2),(.09,.09,height),'steel')
            box('foot plate',(x,y,.02),(.22,.20,.04),'steel')
        for i in range(int(height/.14)):
            box('timber slat',(0,y,.12+i*.14),(width,depth,.105),'timber')

    def wheel(x,y,z,r=.36):
        beam('rubber tyre',(x,y-.085,z),(x,y+.085,z),r,'dark',24)
        beam('alloy hub',(x,y-.091,z),(x,y+.091,z),r*.53,'steel',16)

    def tactile(y,z,width=1.5,slope=0):
        if slope:
            S.mesh('sloped tactile panel',[(x,y+dy,z+dy*slope+.004) for x,dy in [(-width/2,-.3),(width/2,-.3),(width/2,.3),(-width/2,.3)]],[(0,1,2,3)],'ochre')
        else:box('tactile panel',(0,y,z+.003),(width,.60,.006),'ochre')
        for i in range(int(width/.10)):
            for j in range(6):
                yy=y-.25+j*.10;zz=z+(yy-y)*slope
                beam('warning dome',(-width/2+.05+i*.10,yy,zz+.006),(-width/2+.05+i*.10,yy,zz+.011),.012,'ochre',8)

    if kind in ('accessible-ramp','outdoor-stairs'):
        surface=walk_surface(kind); pairs=[(s['z'],s['height']) for s in surface['stations']]
        profile('walking concrete',2.05,pairs)
        if kind=='accessible-ramp':
            stations=[(-5.0,0),(-3.6,0),(-1.2,.2),(1.2,.4),(3.6,.6),(5,.6)]
            for x in (-.99,.99):
                rail(x,stations)
                profile('wheel edge',.05,[(q,h+.08) for q,h in pairs],center=x)
            for q,h in [(-4.25,.001),(4.25,.601)]:
                for x in (-.5,0,.5):box('landing joint',(x,-q,h),(.008,1.4,.002),'steel')
        else:
            stations=[(-1.5,.15),(-.6,.6),(0,.9),(1.45,.9)]
            for x in (-.99,.99):rail(x,stations)
            for i in range(6):box('contrasting stair nosing',(0,1.5-i*.3-.025,(i+1)*.15+.002),(1.9,.05,.004),'ochre')
    elif kind=='modular-handrail':
        for x in (-1.4,0,1.4):
            box('bolted plate',(x,0,.015),(.18,.18,.03),'steel')
            beam('upright',(x,0,.03),(x,0,1.1),.027,'steel',12)
            for dx in (-.055,.055):beam('bolt',(x+dx,.055,.03),(x+dx,.055,.042),.01,'dark',6)
        for z in (.65,1.1):beam('rail',(-1.5,0,z),(1.5,0,z),.027,'steel',12)
    elif kind=='retaining-wall':
        box('footing',(0,0,.08),(3,.8,.16),'concrete')
        for i in range(6):box('precast panel',(-1.25+i*.5,0,.65),(.492,.30,1.05),'concrete')
        box('coping',(0,0,1.22),(3,.38,.10),'cream')
        for x in (-1,0,1):beam('drain outlet',(x,-.155,.3),(x,-.19,.3),.035,'dark',12)
    elif kind in ('refuge-island','planted-curb-extension'):
        if kind=='refuge-island':
            for y in (-1.65,1.65):
                sign=math.copysign(1,y)
                outline=[(-.9,sign*.9),(.9,sign*.9)]+[(.9*math.cos(i*math.pi/16),sign*(2.4+.9*math.sin(i*math.pi/16))) for i in range(17)]
                n=len(outline);verts=[(x,yy,z) for z in (0,.15) for x,yy in outline]
                S.mesh('solid rounded refuge nose',verts,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],'concrete')
                box('reflective bollard',(0,y, .6),(.14,.14,.90),'ochre')
                box('bollard reflector',(0,y-.075,.88),(.10,.012,.16),'cream')
            before=set(bpy.context.scene.objects)
            tactile(-.56,.001,1.7);tactile(.56,.001,1.7)
            for obj in set(bpy.context.scene.objects)-before:obj.rotation_euler.z=math.pi/2
        else:
            box('soil bed',(0,0,.09),(2.5,4.5,.18),'soil')
            for x in (-1.35,1.35):
                for y in (-1.6,0,1.6):box('curb with inlet gaps',(x,y,.11),(.2,1.2,.22),'concrete')
            for y in (-2.3,2.3):box('end curb',(0,y,.11),(2.9,.20,.22),'concrete')
            for i in range(5):
                for j in range(3):
                    x=-.9+j*.85;y=-1.8+i*.85
                    for k in range(7):
                        a=k*2.399; h=.3+.07*((i+j+k)%4)
                        beam('grass blade',(x,y,.18),(x+.16*math.cos(a),y+.16*math.sin(a),h+.18),.013,'green',5)
                    beam('flower stem',(x,y,.18),(x,y,.65),.008,'green',5)
                    beam('flower head',(x,y,.63),(x,y,.68),.055,'ochre',8)
    elif kind=='tactile-curb-ramp':
        profile('ramp',1.5,[(-1.5,0),(.3,.15),(1.5,.15)])
        # Flared triangular wedges descend to the two ramp edges.
        for sign in (-1,1):
            x=.75*sign;xx=1.25*sign
            S.mesh('sloping side flare',[(x,1.5,0),(xx,1.5,.15),(xx,-.3,.15),(x,-.3,.15),(xx,1.5,0),(xx,-.3,0),(x,-.3,0)],[(0,1,2,3),(0,4,1),(1,4,5,2),(2,5,6,3),(0,3,6,5,4)],'concrete')
            box('landing wing',((x+xx)/2,-.9,.075),(.5,1.2,.15),'concrete')
        tactile(1.2,.025,slope=-1/12)
    elif kind=='covered-bike-parking':
        for x in (-2.35,2.35):
            for y in (-1.0,1.0):
                box('column foot',(x,y,.025),(.25,.25,.05),'steel')
                box('canopy column',(x,y,1.3),(.09,.09,2.6),'steel')
        for y in (-1,1):box('roof carrier',(0,y,2.58),(5,.12,.20),'steel')
        for i in range(11):box('roof standing seam',(-2.5+i*.5,0,2.76),(.026,2.8,.045),'steel')
        box('opaque shelter roof',(0,0,2.72),(5.25,2.8,.07),'sage')
        for x in (-1.9,-1.14,-.38,.38,1.14,1.9):
            for y in (-.55,.55):beam('rack leg',(x,y,0),(x,y,.78),.035,'steel',12)
            beam('rack top',(x,-.55,.78),(x,.55,.78),.035,'steel',12)
    elif kind=='bicycle-locker':
        box('raised base',(0,0,.055),(1.85,2.2,.11),'steel')
        for x in (-.92,0,.92):box('locker side',(x,0,.68),(.035,2.2,1.3),'sage')
        box('rear panel',(0,1.08,.68),(1.85,.04,1.3),'sage')
        box('roof',(0,0,1.36),(1.94,2.3,.08),'steel')
        for x in (-.46,.46):
            box('locker door',(x,-1.085,.68),(.87,.045,1.22),'sage')
            box('recessed handle',(x+.27,-1.115,.8),(.04,.025,.16),'dark')
            for j in range(5):box('vent slot',(x,-1.112,.3+j*.045),(.42,.008,.012),'dark')
        label('BIKE  01     BIKE  02',(0,-1.119,1.13),.11)
    elif kind=='ev-charger':
        box('pedestal',(0,0,.08),(.72,.62,.16),'concrete')
        box('charger case',(0,0,.98),(.48,.36,1.8),'sage')
        box('screen surround',(0,-.19,1.38),(.35,.02,.4),'dark')
        box('display',(0,-.202,1.42),(.27,.008,.23),'blue')
        label('EV',(0,-.208,.92),.18)
        for sign in (-1,1):
            points=[(sign*(.27+.28*math.sin(t*math.pi)),0,1.6-1.15*math.sin(t*math.pi/2)) for t in [i/12 for i in range(13)]]
            points += [(sign*.3,-.12,1.08)]
            for a,b in zip(points,points[1:]):beam('charging cable',a,b,.018,'dark',8)
            box('charging connector',(sign*.31,-.13,1.08),(.08,.09,.19),'dark')
            beam('protection bollard',(sign*.75,.08,0),(sign*.75,.08,.8),.065,'steel',12)
    elif kind in ('accessible-parking','loading-zone'):
        w,d=(4,5.5) if kind=='accessible-parking' else (3,7)
        box('thin asphalt marking pad',(0,0,.008),(w,d,.016),'asphalt')
        for a,b in [((-w/2+.06,-d/2+.06),(w/2-.06,-d/2+.06)),((w/2-.06,-d/2+.06),(w/2-.06,d/2-.06)),((w/2-.06,d/2-.06),(-w/2+.06,d/2-.06)),((-w/2+.06,d/2-.06),(-w/2+.06,-d/2+.06))]:S.line(a,b,.07,z=.025)
        if kind=='accessible-parking':
            S.line((.55,-2.7),(.55,2.7),.07,z=.025)
            for y in [-2.5+i*.45 for i in range(11)]:S.line((.62,y),(1.92,min(y+.8,2.7)),.06,z=.025)
            box('blue accessible marking',(-.7,0,.019),(1.35,1.5,.009),'blue')
            # Recognizable wheelchair marking: ring, back, seat, bent leg and head.
            for i in range(24):
                a=i*math.tau/24;b=(i+1)*math.tau/24
                S.line((-.82+.34*math.cos(a),-.15+.34*math.sin(a)),(-.82+.34*math.cos(b),-.15+.34*math.sin(b)),.065,z=.027)
            for a,b in [((-.85,.5),(-.77,.05)),((-.77,.05),(-.35,.05)),((-.35,.05),(-.22,-.38)),((-.22,-.38),(.0,-.38))]:S.line(a,b,.075,z=.029)
            beam('wheelchair head',(-.88,.67,.025),(-.88,.67,.032),.11,'cream',16)
            box('wheel stop',(-.65,2.23,.065),(1.7,.17,.13),'concrete')
        else:
            label('LOADING',(0,0,.024),.40,'ochre',True)
            for y in (-3.05,3.05):box('yellow end stripe',(0,y,.023),(2.85,.10,.01),'ochre')
        beam('parking sign post',(-w/2+.2,d/2-.2,0),(-w/2+.2,d/2-.2,2.3),.028,'steel',10)
        box('parking sign',(-w/2+.2,d/2-.23,2.08),(.48,.04,.54),'blue' if kind=='accessible-parking' else 'cream')
        label('P' if kind=='accessible-parking' else 'LOAD',(-w/2+.2,d/2-.255,2.08),.27 if kind=='accessible-parking' else .095,'cream' if kind=='accessible-parking' else 'dark')
    elif kind=='waste-enclosure':
        slats(3.2,.065,1.85,y=1.15)
        for x in (-1.55,1.55):
            for j in range(13):box('side slat',(x,0,.12+j*.14),(.065,2.3,.105),'timber')
            box('front post',(x,-1.1,.92),(.10,.10,1.84),'steel')
        for x in (-.68,.68):
            box('wheeled bin',(x,.25,.64),(.88,.76,1.08),'sage')
            box('bin lid',(x,.25,1.21),(.95,.83,.10),'dark')
            box('lid handle',(x,-.14,1.26),(.24,.08,.06),'steel')
            for xx in (x-.32,x+.32):wheel(xx,.48,.11,.11)
    elif kind=='privacy-screen':slats(3,.075,1.9)
    elif kind=='public-art':
        beam('stone plinth',(0,0,0),(0,0,.20),.88,'concrete',40)
        for offset in (0,math.pi):
            verts=[]
            for i in range(49):
                t=i/48;angle=t*math.tau+offset;r=.45+.18*math.sin(math.pi*t)
                for edge in (-1,1):verts.append(((r+edge*.085)*math.cos(angle),(r+edge*.085)*math.sin(angle),.2+t*2.45))
            S.mesh('twisting bronze ribbon',verts,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(48)],'bronze')
        box('art plaque',(0,-.82,.23),(.36,.10,.06),'bronze')
    elif kind=='food-truck':
        box('chassis',(0,0,.48),(5.6,2.05,.18),'dark')
        box('kitchen body',(0.65,0,1.15),(4.1,2.0,.95),'sage')
        box('kitchen back',(0.65,1,1.98),(4.1,.06,.75),'sage')
        box('truck roof',(.65,0,2.42),(4.2,2.12,.12),'cream')
        for x in (-1.36,2.66):box('end wall',(x,0,1.98),(.08,2,.8),'sage')
        for x in (-1.02,2.32):box('hatch jamb',(x,-1,1.98),(.62,.05,.8),'sage')
        box('serving counter',(.65,-1.10,1.65),(2.75,.44,.09),'timber')
        canopy=box('raised hatch canopy',(.65,-1.42,2.45),(2.75,.90,.055),'ochre');canopy.rotation_euler.x=-.16
        box('interior worktop',(.65,.53,1.4),(3.5,.65,.1),'steel')
        box('cab',(-2,0,1.08),(1.3,2,.9),'cream')
        box('cab upper',(-2.02,0,1.85),(1.1,1.93,.68),'cream')
        box('cab windshield',(-2.59,0,1.88),(.015,1.68,.47),'blue')
        for y in (-.976,.976):box('side cab window',(-2.04,y,1.9),(.83,.015,.44),'blue')
        for x in (-1.95,1.85):
            for y in (-1.02,1.02):wheel(x,y,.4,.39)
        for y in (-.72,.72):box('headlamp',(-2.68,y,1.03),(.025,.27,.17),'ochre')
        box('menu',(.98,-1.037,1.16),(.65,.018,.67),'dark')
        label('MENU',(.98,-1.05,1.35),.10)
        for z in (.97,1.06,1.15):box('menu rule',(.98,-1.05,z),(.43,.008,.014),'cream')
        label('STREET KITCHEN',(.30,-1.04,.91),.13)
    elif kind=='cafe-barrier':
        for x in (-.95,.95):
            beam('weighted foot',(x,0,0),(x,0,.045),.22,'steel',20)
            beam('barrier post',(x,0,.045),(x,0,1.1),.025,'steel',10)
        for z in (.18,1.05):beam('barrier rail',(-.95,0,z),(.95,0,z),.018,'steel',10)
        box('woven panel',(0,0,.62),(1.8,.018,.76),'sage')
        label('CAFE',(0,-.015,.63),.17)
    elif kind=='community-noticeboard':
        for x in (-.78,.78):box('timber post',(x,0,1.18),(.13,.14,2.36),'timber')
        box('board frame',(0,0,1.58),(1.82,.16,1.20),'timber')
        box('recessed board',(0,-.09,1.58),(1.62,.02,1.01),'sage')
        for x,z,w,h in [(-.49,1.67,.38,.47),(0,1.74,.41,.36),(.49,1.58,.40,.59),(-.13,1.27,.5,.24)]:
            box('pinned notice',(x,-.107,z),(w,.009,h),'cream')
            beam('pin',(x,-.113,z+h/2-.035),(x,-.123,z+h/2-.035),.012,'bronze',8)
            for zz in (z-.06,z+.02):box('notice text',(x,-.113,zz),(w*.7,.006,.012),'steel')
        box('roof',(0,0,2.27),(2.05,.55,.09),'steel')
        label('COMMUNITY',(0,-.096,2.05),.13)
    elif kind=='rainwater-cistern':
        beam('tank base',(0,0,0),(0,0,.12),.82,'concrete',32)
        beam('tank shell',(0,0,.12),(0,0,1.9),.74,'sage',40)
        for z in [.23+i*.19 for i in range(9)]:beam('tank rib',(0,0,z),(0,0,z+.045),.763,'sage',40)
        beam('tank lid',(0,0,1.9),(0,0,1.97),.76,'steel',40)
        beam('inspection cap',(0,0,1.97),(0,0,2.04),.19,'dark',24)
        for a,b in [((.48,.1,1.95),(.48,.1,2.22)),((.48,.1,2.22),(.98,.1,2.22)),((-.62,0,1.78),(-.9,0,1.78)),((-.9,0,1.78),(-.9,0,.15))]:beam('inlet and overflow',a,b,.04,'steel',12)
        beam('water tap',(0,-.71,.38),(0,-.9,.38),.025,'bronze',12)
        beam('tap handle',(-.065,-.81,.44),(.065,-.81,.44),.012,'bronze',8)
    elif kind=='public-washroom':
        box('flush floor',(0,0,.018),(3,3.2,.036),'concrete')
        for x in (-1.43,1.43):box('side wall',(x,0,1.28),(.14,2.92,2.56),'cream')
        box('rear wall',(0,1.53,1.28),(3,.14,2.56),'cream')
        # Actual 1.1m wide open doorway and 2.2m clear headroom.
        for x in (-1.025,1.025):box('front pier',(x,-1.53,1.28),(.95,.14,2.56),'cream')
        box('door lintel',(0,-1.53,2.4),(1.1,.14,.32),'cream')
        for x in (-.57,.57):box('door jamb',(x,-1.62,1.1),(.045,.055,2.2),'timber')
        box('roof',(0,0,2.65),(3.28,3.48,.18),'sage')
        for x in (-1.40,1.40):
            for y in [-1.2+i*.3 for i in range(9)]:box('exterior timber batten',(x+math.copysign(.11,x),y,1.35),(.06,.07,2.35),'timber')
        box('toilet cistern',(-.75,1.23,.73),(.45,.20,.55),'cream')
        beam('toilet pedestal',(-.75,.87,.04),(-.75,.87,.37),.18,'cream',20)
        beam('toilet bowl',(-.75,.82,.33),(-.75,.82,.46),.27,'cream',24)
        beam('toilet seat',(-.75,.82,.46),(-.75,.82,.48),.235,'dark',24)
        box('basin cabinet',(.97,.45,.42),(.56,.57,.80),'timber')
        box('basin',(.97,.45,.85),(.62,.62,.09),'cream')
        box('basin hollow',(.97,.43,.899),(.43,.38,.007),'steel')
        beam('tap',(.97,.68,.9),(.97,.68,1.05),.018,'steel',10)
        box('mirror',(1.348,.45,1.45),(.012,.55,.66),'blue')
        for a,b in [((-1.29,.65,.8),(-1.29,1.25,.8)),((-.42,.88,.8),(-.42,1.35,.8))]:beam('grab rail',a,b,.025,'steel',12)
        box('interior ceiling light',(0,0,2.55),(.6,.6,.035),'cream')
        label('WC',(0,-1.612,2.40),.17,'steel')
    else:raise ValueError(kind)


def render(S,bpy,path,dims):
    from mathutils import Vector
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24
    scene.render.resolution_x=640;scene.render.resolution_y=560;scene.render.resolution_percentage=100
    scene.world.color=(.65,.65,.65)
    ground=S.box('render ground',(0,0,-.035),(100,100,.04),'render-ground')
    approach=1 if path.stem in ('outdoor-stairs','accessible-ramp','tactile-curb-ramp') else -1
    bpy.ops.object.camera_add(location=(max(dims)*1.1,approach*max(dims)*1.4,max(dims)*1.0))
    camera=bpy.context.object;target=Vector((0,0,dims[2]*.40))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO';camera.data.ortho_scale=max(math.hypot(dims[0],dims[1])*1.35,dims[2]*1.8,1.5)
    scene.camera=camera
    bpy.ops.object.light_add(type='AREA',location=(3,-4,9));bpy.context.object.data.energy=1600;bpy.context.object.data.shape='DISK';bpy.context.object.data.size=7
    bpy.ops.object.light_add(type='AREA',location=(-4,2,6));bpy.context.object.data.energy=1000;bpy.context.object.data.size=6
    scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG';scene.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--id',choices=[s[0] for s in SPECS]);parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--render',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else None)
    specs=[s for s in SPECS if not args.id or s[0]==args.id]
    if args.dry_run:print(json.dumps(dict(objects=[s[0] for s in specs],paid_calls=0)));return
    import bpy
    from mathutils import Vector
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'public_realm_assets'));import scene as S
    args.output.mkdir(parents=True,exist_ok=False)
    palette={'concrete':(.48,.47,.43),'cream':(.83,.83,.76),'steel':(.16,.20,.20),'dark':(.026,.032,.032),'sage':(.22,.36,.31),'timber':(.42,.27,.13),'ochre':(.85,.51,.045),'green':(.20,.31,.10),'soil':(.12,.082,.04),'asphalt':(.11,.125,.13),'blue':(.085,.28,.46),'bronze':(.51,.27,.09),'paint':(.85,.86,.80),'render-ground':(.68,.69,.67)}
    for name,color in palette.items():
        m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
        shader=m.node_tree.nodes['Principled BSDF'];shader.inputs['Base Color'].default_value=(*color,1)
        shader.inputs['Roughness'].default_value=.40 if name in ('steel','bronze') else .78
        shader.inputs['Metallic'].default_value=.55 if name in ('steel','bronze') else 0
        m.use_backface_culling=False;S.MATS[name]=m
    S.MATS['kit']=bpy.data.materials.new('unused kit');catalogue=[]
    for slug,label,category,description in specs:
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        build(slug,S,bpy);bpy.context.view_layer.update()
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
        # Profile caps and mirrored flares need consistent outward winding.
        import bmesh
        for obj in objects:
            bm=bmesh.new();bm.from_mesh(obj.data)
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
            bm.to_mesh(obj.data);bm.free()
        bounds=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
        low=[min(v[i] for v in bounds) for i in range(3)];high=[max(v[i] for v in bounds) for i in range(3)]
        dims=[round(high[i]-low[i],4) for i in range(3)]
        info=S.export(args.output/(slug+'.glb'),objects);triangles=0
        for o in objects:o.data.calc_loop_triangles();triangles+=len(o.data.loop_triangles)
        record=dict(id='detail-site-'+slug,label=label,category=category,description=description,dimensions=dims,
                    url='/street-kits/site-details-v1/'+slug+'.glb',color='#688779',kind='object',
                    offset=[round(-(low[0]+high[0])/2,5),round(-low[2],5),round((low[1]+high[1])/2,5)],
                    sourceKit='site-details-v1',sha256=info['sha256'],triangles=triangles,
                    meshes=len({o.data.materials[0].name for o in objects}),bytes=info['bytes'])
        if walk_surface(slug):record['walkSurface']=walk_surface(slug)
        assert record['meshes']<=10,(slug,record['meshes'])
        catalogue.append(record)
        if args.render:render(S,bpy,args.output/(slug+'.png'),dims)
    (args.output/'catalogue.json').write_text(json.dumps(catalogue,indent=2)+'\n')
    print(json.dumps(dict(built=len(catalogue),bytes=sum(m['bytes'] for m in catalogue))))


if __name__=='__main__':main()
