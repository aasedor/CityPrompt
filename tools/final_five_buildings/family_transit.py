"""Timber V-column civic waiting pavilion; canopy valley follows locked roof graph."""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG='final-transit-pavilion'
PALETTE=dict(wall=(.62,.54,.38),joint=(.46,.42,.33),trim=(.10,.12,.115),pale=(.70,.68,.60),
    roof=(.09,.115,.14),foundation=(.48,.49,.45),glass=(.50,.57,.55),hardware=(.065,.075,.08),
    interior=(.73,.66,.51),floor=(.49,.50,.43),timber=(.52,.33,.16),planting=(.26,.35,.12),
    soil=(.16,.12,.075),blue=(.13,.29,.36),yellow=(.70,.59,.26))

def roof_z(x):return 6.8+(4.6-6.8)*(x+14)/16.4 if x<=2.4 else 4.6+(5.1-4.6)*(x-2.4)/11.6

def manifest(version):
    cams=G.camera_roster(28,15,7,[
        ('facade_close',(-10,-14,4.4),(-7,-5.4,3.6),38),
        ('architecture_close',(0,-13,2.2),(0,-4.5,2),28),
        ('glass_close',(7,-7,2),(7,-2,1.8),26),
        ('roof_contact',(-6,-8,10),(2.4,0,4.6),32),
        ('passage',(0,-4.3,1.8),(0,3,1.8),22),
        ('courtyard',(10,-2,1.8),(6,2.5,1.8),22),
        ('tickets',(-3,1.8,1.85),(-5.8,3.7,1.2),24),
        ('waiting',(-2,-.7,1.7),(-5,-2.5,.7),24),
        ('canopy_support',(-9,-8,1.9),(-9,-5.4,3.5),24)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}',method=C.METHOD,archetype_id=SLUG,variant_id=SLUG+'-v1',
        representation_kind='architectural_clay',state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=dict(width=28,depth=13,height=6.96),observed_storeys=1,front_V_columns=4,
            valley_front_fraction=.586,inferred='Standalone educational pavilion. Native metrics and rear/service rooms inferred; transport corridor and tracks are separate.'),
        roof_contract=dict(type='asymmetric butterfly canopy across frontage; valley front-to-back',left_height_m=6.8,valley_height_m=4.6,right_height_m=5.1),
        identity_contract=dict(owner='four timber V supports; thin dark roof; stone left core; clear ticket/waiting hall and right cafe'),
        material_contract=dict(profile='source-palette architectural clay with stone courses, metal seams, timber members',textured_keeper=False),
        programme_contract=dict(storeys=1,ground='ticket machines, waiting benches, cafe counter and seating, service core',circulation='clear centre entry and rear exit'),
        contact_contract=['Four anchored V-columns','Canopy timber beams seated on columns','Sealed valley and edge flashings','Open central route'],
        runtime_contract=dict(scale='fixed_native_only',review='NOT TESTED'),camera_roster=cams,mandatory_review_views=[c['name'] for c in cams])

def hole(name,u,z,w,h,**kw):return dict(id=name,u=u,z=z,w=w,h=h,**kw)

def glass_bay(face,a,b,z0,za,zb,door=False):
    # Curtain wall has no opaque carrier. Structural perimeter frames own depth.
    for u,z in ((a,za),(b,zb)):face.part('Glazing structural mullion',u,.04,(z+z0)/2,.075,.14,z-z0,'trim','curtain wall',0)
    C.beam('Sloping window head',face.p(a,.04,za),face.p(b,.04,zb),.075,.14,'trim','curtain wall')
    if door:
        G.open_door(face,hole('Open concourse doors',(a+b)/2,z0,b-a,2.95))
        bottom=z0+2.95
    else:
        face.part('Glazing seated sill',(a+b)/2,.04,z0+.035,b-a,.14,.07,'trim','curtain wall',0)
        bottom=z0+.06
    poly=[face.p(a+.04,.09,bottom),face.p(b-.04,.09,bottom),face.p(b-.04,.09,zb-.04),face.p(a+.04,.09,za-.04)]
    G.optical_surface('Optical concourse glazing',poly,face.n,.009,'curtain wall')
    if not door:face.part('Horizontal curtain wall transom',(a+b)/2,.03,2.75,b-a,.1,.05,'trim','curtain wall',0)

def build():
    C.box('Station foundation',(0,0,.075),(24,9,.15),'foundation','foundation',0)
    C.box('Covered forecourt',(0,-5.5,.075),(28,2,.15),'pale','forecourt',0)
    # Roof planes are geometrically closed, with separate metal cap/timber soffit.
    for xa,xb in [(-14,2.4),(2.4,14)]:
        q=[(xa,-6.5,roof_z(xa)),(xb,-6.5,roof_z(xb)),(xb,6.5,roof_z(xb)),(xa,6.5,roof_z(xa))]
        C.solid_surface('Timber roof structure',q,.23,'timber','canopy roof')
        C.solid_surface('Standing seam weather roof',[(x,y,z+.025) for x,y,z in q],.06,'roof','roof cap')
        for y in (-6.5,6.5):C.beam('Seated perimeter fascia',(xa,y,roof_z(xa)),(xb,y,roof_z(xb)),.15,.30,'roof','roof fascia')
        for j in range(math.ceil((xb-xa)/.48)):
            x=xa+(j+.5)*(xb-xa)/math.ceil((xb-xa)/.48)
            C.beam('Metal roof raised seam',(x,-6.46,roof_z(x)+.0345),(x,6.46,roof_z(x)+.0345),.026,.025,'roof','standing seams',0)
    C.box('Continuous valley gutter',(2.4,0,4.61),(.16,13,.12),'roof','valley flashing',0)
    for x in (-14,14):C.beam('Outer roof rake',(x,-6.5,roof_z(x)),(x,6.5,roof_z(x)),.13,.30,'roof','rake flashing')
    # Four visible V supports, steel feet and roof-bearing timber rails.
    for x in (-9,-3,4,10):
        C.box('Anchored steel foot',(x,-5.4,.20),(.62,.62,.10),'hardware','column foot',0)
        C.box('Steel V-column shoe',(x,-5.4,.66),(.35,.36,.86),'hardware','column foot',0)
        for sign in (-1,1):
            xx=x+sign*.72
            C.beam('Timber V-column',(x+sign*.1,-5.4,.88),(xx,-5.4,roof_z(xx)-.20),.24,.30,'timber','V columns')
    for y in (-5.4,4.35):
        for xa,xb in [(-12,2.4),(2.4,12)]:C.beam('Canopy supporting beam',(xa,y,roof_z(xa)-.22),(xb,y,roof_z(xb)-.22),.25,.28,'timber','roof beams')
    # Pale stone core has actual service door and a side window.
    front=C.Face((0,-4.5,0),(1,0,0),(0,1,0),'station front')
    core_front=C.Face((-10,-4.5,0),(1,0,0),(0,1,0),'stone front')
    core_front.panel('Stone core front',[(-2,.15),(2,.15),(2,roof_z(-8)-.23),(-2,roof_z(-12)-.23)],0,.28)
    G.brick_courses(core_front,-2,2,.15,roof_z(-8)-.25,[],spacing=.18)
    core_left=C.Face((-12,0,0),(0,-1,0),(1,0,0),'stone left')
    leftlow=roof_z(-11.72)-.23
    G.wall(core_left,8.44,.15,leftlow,[hole('Service side door',1,.15,1.1,2.6,open=True)],courses=True)
    C.prism('Slope seated left wall cap',[(-12,leftlow),(-11.72,leftlow),(-12,roof_z(-12)-.23)],'y',-4.22,4.22,'wall','core closure')
    core_inner=C.Face((-8,0,0),(0,1,0),(-1,0,0),'service room')
    innerlow=roof_z(-8)-.23
    G.wall(core_inner,8.44,.15,innerlow,[hole('Staff doorway',2,.15,1.1,2.6,open=True)])
    C.prism('Slope seated inner wall cap',[(-8.28,innerlow),(-8,innerlow),(-8.28,roof_z(-8.28)-.23)],'y',-4.22,4.22,'wall','core closure')
    rear=C.Face((0,4.5,0),(-1,0,0),(0,-1,0),'station rear')
    rear.panel('Core rear',[ (8,.15),(12,.15),(12,roof_z(-12)-.23),(8,roof_z(-8)-.23)],0,.28)
    for f in (front,rear):
        edges=(-8,-5.5,-3,-1.5,1.5,4.1,6.7,9.3,12) if f==front else (-12,-9.3,-6.7,-4.1,-1.5,1.5,3,5.5,8)
        for a,b in zip(edges,edges[1:]):
            xa=a if f==front else -a;xb=b if f==front else -b
            glass_bay(f,a,b,.15,roof_z(xa)-.27,roof_z(xb)-.27,door=a==-1.5)
    east=C.Face((12,0,0),(0,1,0),(-1,0,0),'cafe east')
    for a,b in zip((-4.36,-2.2,0,2.2),(-2.2,0,2.2,4.36)):glass_bay(east,a,b,.15,roof_z(12)-.27,roof_z(12)-.27)
    # Actual ticket machines and waiting benches, leaving the centre route free.
    for x in (-6.9,-5.8,-4.7):
        C.box('Ticket machine cabinet',(x,3.7,1.15),(.72,.42,2.0),'trim','ticketing',0)
        C.box('Ticket touchscreen',(x,3.47,1.52),(.51,.03,.55),'blue','ticketing',0)
        C.box('Fare slot',(x,3.45,.92),(.32,.045,.045),'hardware','ticketing',0)
    for x,y in [(-5,-2.5),(-5,.6)]:
        C.box('Waiting bench seat',(x,y,.63),(3.2,.56,.12),'timber','waiting',0)
        C.box('Waiting bench back',(x,y+.28,.98),(3.2,.10,.62),'timber','waiting',0)
        for dx in (-1.2,1.2):C.box('Bench anchored leg',(x+dx,y,.36),(.12,.42,.42),'hardware','waiting',0)
    C.box('Cafe service counter',(8,2.9,.7),(5,.8,1.1),'timber','cafe',0)
    C.box('Cafe counter top',(8,2.9,1.30),(5.15,.95,.1),'pale','cafe',0)
    C.box('Coffee machine',(7,3,1.65),(.7,.5,.6),'hardware','cafe',0)
    for x in (5.5,9):
        C.box('Cafe table',(x,-1.2,.92),(1.1,.75,.08),'timber','cafe',0)
        C.box('Table foot',(x,-1.2,.52),(.12,.12,.74),'hardware','cafe',0)
        A.garden_chair(x-.8,-1.2,.15);A.garden_chair(x+.8,-1.2,.15)
    for x in (-5,0,6,10):C.qa_room_light('Occupied public hall',(x,0,3.9),200,3)
    # Tactile entry strip is physical paving, no height obstacle.
    C.box('Tactile forecourt strip',(0,-6.12,.158),(26,.30,.016),'yellow','wayfinding',0)
    C.CONTACTS.append(dict(name='Unobstructed concourse route',width_m=3,front_to_rear=True))
