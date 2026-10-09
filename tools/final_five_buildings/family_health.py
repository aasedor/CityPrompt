"""Seven-bay civic clinic with a real L plan, pharmacy and covered drop-off."""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG='final-health-centre'
W,D,H=28.,22.,8.2
PALETTE=dict(wall=(.43,.18,.105),joint=(.31,.23,.17),trim=(.19,.18,.13),
    pale=(.75,.71,.62),roof=(.73,.73,.68),foundation=(.43,.45,.43),
    glass=(.50,.59,.57),hardware=(.045,.055,.06),interior=(.76,.75,.65),
    floor=(.59,.61,.55),timber=(.52,.31,.14),planting=(.22,.35,.11),
    blue=(.19,.37,.39),soil=(.15,.11,.07))


def manifest(version):
    cams=G.camera_roster(35,D,H,[
        ('facade_close',(-9,-19,7),(-8,-11,5.6),44),
        ('architecture_close',(3,-18,2.3),(0,-10,2),30),
        ('glass_close',(7.3,-16,2.2),(8,-10.8,1.9),26),
        ('roof_contact',(-8,3,12),(-10,8,8.3),32),
        ('passage',(0,-10.5,1.8),(0,-3,1.8),22),
        ('courtyard',(11.8,9.6,3.5),(3,4,1.2),22),
        ('stairs',(-10,-1,1.9),(-10,6.8,4.8),24),
        ('upper_landing',(-8.4,8,5.8),(-10,6.2,4.4),24),
        ('consulting_room',(-8.3,5,2),(-12.1,8.5,1.4),22),
        ('pharmacy',(10,-9.5,1.85),(11,-3.5,1.7),22),
        ('dropoff',(-23,-5,2.8),(-13,-5,3.2),30)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}',method=C.METHOD,
        archetype_id=SLUG,variant_id=SLUG+'-v1',representation_kind='architectural_clay',
        state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=dict(width=35,depth=D,height=H+.55),observed_storeys=2,
            front_bays=7,front_wing_m=[28,9],rear_left_wing_m=[10.5,13],
            inferred='Front door calibrates metric scale; hidden consulting rooms and circulation are original educational assumptions.'),
        roof_contract=dict(type='continuous L-shaped flat membrane',datum_m=H,parapet_m=.45),
        identity_contract=dict(owner='seven red-brick bays; central pale portico; right pharmacy; left vehicle canopy'),
        material_contract=dict(profile='source-palette architectural clay with physical brick coursing',textured_keeper=False),
        programme_contract=dict(storeys=2,ground='reception, waiting, pharmacy, consulting rooms',upper='consulting and administration',stairs='open floor-cut stair in left wing'),
        contact_contract=['Seated two-column entrance portico','Supported dropoff roof','Open public doors','Floor-cut stair'],
        runtime_contract=dict(scale='fixed_native_only',review='NOT TESTED'),
        camera_roster=cams,mandatory_review_views=[c['name'] for c in cams])


def hole(name,u,z,w,h,**kw):return dict(id=name,u=u,z=z,w=w,h=h,**kw)


def build():
    # Non-overlapping slabs preserve the L-shaped exterior and open garden.
    for x,y,w,d in [(0,-6.5,28,9),(-8.75,4.5,10.5,13)]:
        C.box('Clinic foundation',(x,y,.075),(w,d,.15),'foundation','foundation',0)
        for z in (4.15,):
            fy=y if y<0 else 4.22
            fd=d-.56 if y<0 else d
            floor=C.box('Occupied clinic floor',(x,fy,z-.075),(w-.56,fd,.15),'floor','floors',0)
            if y>0 and z>1:C.cut_box(floor,'Stair aperture',(-10,4,z),(1.9,6.3,.6))
        C.box('L shaped membrane roof',(x,fy,H-.11),(w-.56,fd,.22),'roof','roof',0)
    front=C.Face((0,-11,0),(1,0,0),(0,1,0),'clinic front')
    hs=[hole('Clinic main entrance',-1.7,.15,4.8,3.05,open=True),hole('Pharmacy entrance',12,.15,2.1,3.05,open=True)]
    for i in (0,1,4,5):hs.append(hole('Waiting room glazing '+str(i),-12+i*4,.55,2.75,2.7,cols=3))
    for i in range(7):hs.append(hole('Consulting window '+str(i),-12+i*4,4.7,2.75,2.55,cols=3))
    G.wall(front,W,.15,H,hs,courses=True)
    for i in range(7):
        for j in range(3):front.part('Upper timber sun fin',-12+i*4+1.48+j*.14,-.20,5.975,.075,.42,2.6,'timber','sun fins',0)
    faces=[(C.Face((14,-6.5,0),(0,1,0),(-1,0,0),'east end'),8.44),
           (C.Face((5.25,-2,0),(-1,0,0),(0,-1,0),'garden south'),17.5),
           (C.Face((-3.5,4.36,0),(0,1,0),(-1,0,0),'garden west'),12.72),
           (C.Face((-8.75,11,0),(-1,0,0),(0,-1,0),'rear clinic'),10.5),
           (C.Face((-14,0,0),(0,-1,0),(1,0,0),'dropoff side'),21.44)]
    for f,span in faces:
        count=max(2,round(span/3.5));windows=[]
        for level,z in enumerate((.15,4.15)):
            for i in range(count):
                u=-span/2+(i+.5)*span/count
                windows.append(hole(f.label+f' window {level}-{i}',u,z+.6,1.7,2.35))
        if f.label=='dropoff side':
            windows=[v for v in windows if not(v['z']<1 and abs(v['u']-5)<3)]
            windows.append(hole('Covered accessible entrance',5,.15,2.4,3,open=True))
        if f.label=='garden south':
            windows=[v for v in windows if not(v['z']<1 and abs(v['u'])<2)]
            windows.append(hole('Garden entry',0,.15,2.2,3,open=True))
        G.wall(f,span,.15,H,windows,courses=True)
    for f,span in [(front,W),*faces]:
        f.part('Brick parapet',0,.14,H+.2,span,.28,.4,'wall','parapet',0)
        f.part('Pale seated coping',0,.14,H+.45,span+.04,.35,.10,'pale','roof coping',0)
    # Continuous pier closes the re-entrant L corner omitted by the inset slabs.
    C.box('Garden inner corner pier',(-3.64,-2.14,(.15+H+.4)/2),(.28,.28,H+.25),'wall','corner closure',0)
    C.box('Garden inner corner coping',(-3.64,-2.14,H+.45),(.28,.28,.10),'pale','roof coping',0)
    # Civic portico is a frame with clear headroom, not a solid entrance slab.
    for x in (-5.4,2):
        C.box('Stone entrance column',(x,-12,1.925),(.55,1.25,3.55),'pale','portico',0)
        C.box('Stone column footing',(x,-12,.075),(.65,1.35,.15),'pale','portico',0)
    C.box('Slender inset portico support',(-3.9,-12,1.925),(.22,.35,3.55),'pale','portico',0)
    C.box('Slender portico footing',(-3.9,-12,.075),(.32,.45,.15),'pale','portico',0)
    C.box('Stone entrance entablature',(-1.7,-12,3.98),(8,1.25,.56),'pale','portico',0)
    C.box('Pharmacy doorway canopy',(12,-11.65,3.52),(3.3,1.3,.25),'pale','pharmacy',0)
    # Left vehicle drop-off: two outer columns and an attached bearing beam.
    C.box('Dropoff canopy roof',(-17.5,-5,3.95),(7,5,.25),'roof','dropoff',0)
    for y in (-7.1,-2.9):C.box('Dropoff outer column',(-20.6,y,1.99),(.40,.40,3.98),'pale','dropoff',0)
    C.box('Dropoff attached beam',(-14.2,-5,3.75),(.35,5,.25),'pale','dropoff',0)
    G.stair('Clinical stair',-10,1,.15,4.15,length=6)
    for x in (-10.98,-9.02):A.seated_guard('Stair aperture guard',(x,.85,4.15),(x,7.15,4.15),spacing=.16)
    A.seated_guard('Stair near-end upper guard',(-10.98,.85,4.15),(-9.02,.85,4.15),spacing=.16)
    # Reception and rows of identifiable waiting chairs.
    C.box('Reception curved desk approximation',(0,-4.4,.72),(4,.8,1.14),'timber','reception',0)
    C.box('Reception worktop',(0,-4.4,1.32),(4.15,.92,.07),'pale','reception',0)
    for x in (-6,-4,4,6):
        for y in (-7.8,-5.8):A.garden_chair(x,y,.15)
    # Pharmacy shelving stays clear of both entrances and the central aisle.
    for x in (8.3,12.8):
        for y in (-6.95,-3.05):C.box('Pharmacy shelf upright',(x,y,1.2),(.45,.065,2.1),'interior','pharmacy shelving',0)
        for z in (.6,1.15,1.7,2.25):
            C.box('Pharmacy shelf',(x,-5,z),(.45,4,.08),'interior','pharmacy shelving',0)
            for j in range(10):C.box('Pharmacy carton',(x,-6.7+j*.37,z+.16),(.27,.22,.24),'blue' if j%3 else 'pale','pharmacy stock',0)
    C.box('Dispensing counter',(10.5,-3,.7),(3.4,.65,1.1),'timber','pharmacy counter',0)
    # Consult rooms have partial internal dividers, examination couches, desks,
    # basins and cabinetry; the corridor remains open along the stair.
    for z in (.15,4.15):
        for y in (2.2,8.5):C.qa_room_light('Consulting wing light',(-10,y,z+3.25),350,3)
        for y in (2.2,8.5):
            C.box('Consultation divider',(-12,y+1.2,z+1.4),(3.6,.14,2.8),'interior','rooms',0)
            C.box('Exam couch base',(-12.1,y,z+.42),(1.6,.68,.75),'pale','exam furniture',0)
            C.box('Exam mattress',(-12.1,y,z+.84),(1.7,.76,.13),'blue','exam furniture',0)
            C.box('Clinical cabinet',(-6.2,y,z+.55),(.75,1.1,1.1),'interior','exam furniture',0)
            A.desk(-7.6,y,z)
        for x in (-7,0,7):
            if z>1:A.desk(x,-7,z);A.garden_chair(x,-5.8,z)
            C.qa_room_light('Clinic occupied floor',(x,-6,z+3.1),230,4)
    for x,y in [(-10,8),(-11,0),(8,-7)]:
        C.box('Mechanical curb',(x,y,H+.12),(1.6,1.3,.24),'hardware','roof equipment',0)
        C.box('Clinic mechanical unit',(x,y,H+.52),(1.4,1.1,.6),'roof','roof equipment',0)
    # Garden is an attached component inside the L, not an unexplained void.
    C.box('Therapeutic garden soil',(5.25,4.5,.065),(17.1,12.6,.13),'soil','garden',0)
    # Two smooth winding paths subdivide planted islands, matching the source plan.
    paths=[];path_solids=[]
    for branch in (0,1):
        points=[]
        for i in range(41):
            y=-1.8+i*12.6/40
            x=5.25+math.sin((y+1.8)/12.6*math.pi*2)*(2.3 if branch==0 else -3.7)
            if branch:x+=3*math.sin((y+1.8)/12.6*math.pi)
            points.append((x,y))
        paths.append(points)
        verts=[]
        for i,(x,y) in enumerate(points):
            p=points[max(0,i-1)];q=points[min(40,i+1)];dx=q[0]-p[0];dy=q[1]-p[1];length=math.hypot(dx,dy)
            verts.extend([(x-dy/length*.8,y+dx/length*.8,.15),(x+dy/length*.8,y-dx/length*.8,.15)])
        outline=[p[:2] for p in verts[::2]]+[p[:2] for p in reversed(verts[1::2])]
        path_solids.append(C.prism('Winding garden path',outline,'z',0,.15,'pale','garden paths'))
    path_solids.append(C.box('Garden social terrace',(8.5,8.6,.075),(6.3,3.8,.15),'pale','garden',0))
    walking=path_solids[0]
    def merge_surface(other,operation):
        modifier=walking.modifiers.new('One continuous bounded garden surface','BOOLEAN')
        modifier.operation=operation;modifier.solver='EXACT';modifier.object=other
        C.bpy.context.view_layer.objects.active=walking
        C.bpy.ops.object.modifier_apply(modifier=modifier.name)
        C.bpy.data.objects.remove(other,do_unlink=True)
    for other in path_solids[1:]:merge_surface(other,'UNION')
    boundary=C.box('Garden surface clipping volume',(5.25,4.5,.075),(17.1,12.6,.3),'pale','garden paths',0)
    merge_surface(boundary,'INTERSECT')
    def near_path(x,y):
        return min(math.hypot(x-px,y-py) for pts in paths for px,py in pts)<1.35 or (5.2<x<12 and 6.6<y<10.6)
    for i in range(17):
        for j in range(12):
            x=-2.6+i*.94;y=-.7+j*.95
            if not near_path(x,y):A.shrub(x,y,.13,.43+(i+j)%3*.09)
    for x,y in [(-1.7,1),(-1.7,8),(2,8.8),(10,4.3),(11,1)]:A.small_tree(x,y,.13,3.0,.65)
    C.box('Garden social table',(8.5,8.6,.88),(1.6,1.3,.12),'timber','garden furniture',0)
    for x in (7.9,9.1):
        for y in (8.1,9.1):C.box('Social table leg',(x,y,.5),(.08,.08,.7),'hardware','garden furniture',0)
    for x,y in [(7.3,8.6),(9.7,8.6),(8,7.4),(9,7.4)]:A.garden_chair(x,y,.15)
    C.CONTACTS.append(dict(name='Main clinic and pharmacy entrances',clear=True,ground_datum_m=.15))
