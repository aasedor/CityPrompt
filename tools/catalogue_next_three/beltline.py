"""Five-storey brick Beltline corner building, exact variant 1."""
import sys, math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import support as S
C=S.C
SLUG='calgary-beltline-mid-rise';PARENT='calgary_beltline_mid_rise';VARIANT='beltline_brick_modern';INDEX=1
TITLE='Beltline brick mixed-use mid-rise';WIDTH=31;DEPTH=31;HEIGHT=20;STOREYS=5
PALETTE=dict(wall=(.44,.21,.12),mortar=(.38,.28,.21),trim=(.13,.14,.12),coping=(.54,.52,.45),roof=(.25,.25,.22),
 foundation=(.45,.43,.37),glass=(.27,.33,.30),hardware=(.12,.13,.12),timber=(.34,.27,.16),
 interior=(.62,.57,.47),floor=(.42,.37,.28),metal=(.22,.23,.19),planter=(.25,.26,.19))
LEVELS=[.12,4.1,7.35,10.6,13.85]

def manifest(v):
    m=S.prework(sys.modules[__name__],v,dict(width=WIDTH,depth=DEPTH,height=HEIGHT),
        dict(front='Ground retail plus three brick residential storeys and one recessed metal-clad occupied roof storey. Tall central glazed stair bay, corner glazing, pale horizontal podium and terrace bands.',
             oblique='Square corner block with central projecting vertical bays on all sides, upper setback terraces and one central rooftop service enclosure.',
             top='Cross-shaped roof outline above square lower body: four short central projections, inset corner fields, central mechanical rectangle and bounded vents/skylights.',
             roof='Closed cross-outline flat upper roof, low perimeter brick coping, central service enclosure. Occupied terrace surrounds the inset upper floor.',
             programme='Mixed-use building with retail bays and entrance at ground, three full residential levels and occupied setback fifth floor.'),
        ['Dimensions inferred from floor/bay proportions, not surveyed.','Rear programme and interior unit divisions inferred; source oblique/top establish continued rear massing.',
         'Street trees, neighbouring buildings and public sidewalk are excluded; terrace planter boxes retained without unsupported foliage detail.',
         'No arbitrary scaling, storey multiplication or engineering compliance claimed.'],
        ['Ground walls seat on continuous perimeter foundation.','Terraces are occupied slabs with physical transparent guardrails and doors.',
         'Upper roof follows one cross-shaped outline, with bounded parapets and roof equipment.'],[
        dict(name='facade_close',location=(25,-35,12),target=(9,-14.8,8),whole=False),
        dict(name='architecture_close',location=(25,-29,22),target=(6,-13,14),whole=False),
        dict(name='glass_close',location=(12,-22,2.5),target=(11,-14.8,2.1),whole=False,lens=45),
        dict(name='roof_contact',location=(22,-26,32),target=(0,0,17.6),whole=False),
        dict(name='terrace_contact',location=(26,-18,14),target=(15,-4.7,10.5),whole=False)])
    for camera in m['camera_roster']:
        if camera['name'] in ('front_corner','aerial'):
            camera['location']=(abs(camera['location'][0]),*camera['location'][1:])
    return m

def window(face,h):
    face.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=h.get('cols',2),rows=h.get('rows',2),frame='trim',curtain=h.get('curtain',False),sill=False)

def face_build(face,label):
    # Separate facade bays keep the actual window-wall sections legible.
    hs=[]
    for i,u in enumerate((3.3,8.0,14.7,21.3,27.0)):
        hs.append(dict(id=label+' retail '+str(i),u=u,z=.12 if i==2 else .20,w=3.8 if i!=2 else 3.0,h=3.48,cols=2,rows=1,door=i==2))
    face.wall('Retail masonry piers',0,30,.12,4.0,holes=hs)
    for h in hs:
        if h.get('door'):face.door(h['id'],h['u'],h['z'],h['w'],h['h'],glazed=True)
        else:window(face,h)
    # Three brick floors; centre is a continuous metal/glass vertical bay.
    for level,z in enumerate(LEVELS[1:4]):
        holes=[]
        for i,u in enumerate((1.5,6.3,9.8,20.2,23.7,28.5)):
            if label=='right' and i in (2,3):continue
            holes.append(dict(id=f'{label} apartment {level}-{i}',u=u,z=z+.42,w=3.0 if i in (0,5) else 2.12,h=2.45,cols=2,rows=2,curtain=True))
        holes.append(dict(id=f'{label} stair {level}',u=15,z=z+.05,w=3.35,h=3.02,cols=2,rows=2))
        balconies=[]
        if label=='right':
            balconies=[dict(id=f'right recessed balcony {level}-{u}',u=u,z=z+.12,w=2.7,h=3.02,balcony=True) for u in (10.3,19.7)]
            holes.extend(balconies)
        face.wall('Brick occupied storey',0,30,z,z+3.25,holes=holes)
        S.courses(face,30,z,z+3.25,holes,pitch=.095)
        for h in holes:
            if not h.get('balcony'):window(face,h)
        for h in balconies:
            back=C.Face(face.p(h['u']-1.35,1.8,0),face.t,face.n,h['id']+' back')
            door=dict(id=h['id']+' occupied room door',u=1.35,z=z+.12,w=2.1,h=2.72)
            back.wall('Recessed balcony back wall',0,2.7,z,z+3.25,holes=[door])
            back.door(door['id'],door['u'],door['z'],door['w'],door['h'],role='trim',glazed=True)
            for side in (-1,1):face.part('Full-depth balcony return',h['u']+side*1.38,1.02,z+1.625,.12,1.82,3.25,'wall','balcony return',0)
            face.part('Balcony floor nosing',h['u'],.86,z+.06,2.7,1.90,.12,'coping','balcony floor',0)
            face.part('Balcony transparent guard',h['u'],-.06,z+.68,2.54,.014,.95,'glass','balcony guard',0)
            face.part('Balcony top rail',h['u'],-.06,z+1.18,2.7,.045,.045,'trim','balcony guard',0)
            for side in (-1,1):face.part('Balcony guard post',h['u']+side*1.30,-.06,z+.65,.045,.045,1.12,'trim','balcony guard',0)
        for u in (1.5,28.5):
            face.part('Continuous corner metal spandrel',u,-.035,z+3.27,3,.13,.80,'metal','corner glazing',0)
            for side in (-1,1):face.part('Continuous corner vertical mullion',u+side*1.46,-.065,z+1.625,.075,.12,3.25,'trim','corner glazing',0)
        # Metal spandrel fills the centre gap; it never covers a carrier opening.
        for u in (13.05,16.95):face.part('Continuous dark metal spine frame',u,-.09,z+1.625,.55,.20,3.25,'metal','core piers',0)
        face.part('Central metal floor spandrel',15,-.035,z+3.185,3.35,.14,.23,'metal','core spandrel',0)
    for z in (4.02,13.72):face.part('Continuous pale horizontal band',15,-.10,z,30,.40,.43,'coping','belt course',0)
    face.part('Entry canopy',15,-.98,3.50,4.8,2.2,.20,'metal','entrance canopy',0)
    for u in (12.9,17.1):face.part('Ground canopy support',u,-1.85,1.72,.12,.12,3.44,'trim','canopy support',0)

def glass_rail(a,b,z):
    from mathutils import Vector
    a,b=Vector((*a,z)),Vector((*b,z));length=(b-a).length
    C.beam('Terrace top rail',a+Vector((0,0,1.08)),b+Vector((0,0,1.08)),.035,.04,'trim','terrace rail')
    count=max(1,math.ceil(length/1.5))
    for i in range(count+1):
        p=a.lerp(b,i/count);C.beam('Terrace guard post',p,p+Vector((0,0,1.08)),.035,.035,'trim','terrace rail')
    for i in range(count):
        p=a.lerp(b,(i+.5)/count)
        size=(length/count-.07,.012,.88) if abs(b.x-a.x)>abs(b.y-a.y) else (.012,length/count-.07,.88)
        C.box('Physical terrace glass',(p.x,p.y,z+.55),size,'glass','terrace glazing',0)

def build():
    C.box('Ground bearing foundation',(0,0,.06),(30,30,.12),'foundation','base',0)
    for name,o,t,n in [('front',(-15,-15,0),(1,0,0),(0,1,0)),('right',(15,-15,0),(0,1,0),(-1,0,0)),
                       ('rear',(15,15,0),(-1,0,0),(0,-1,0)),('left',(-15,15,0),(0,-1,0),(1,0,0))]:
        face_build(C.Face(o,t,n,name),name)
    for z in LEVELS:
        C.box('Complete floor slab',(0,0,z+.04),(29.6,29.6,.16),'floor','occupied floors',0)
        if z<13:
            C.box('Enclosed central core',(0,0,z+1.5),(5.5,7.5,3.0),'interior','service core',0)
            for x in (-9,9):
                for y in (-9,9):
                    C.box('Residential room division',(x,y+3,z+1.53),(10.5,.14,2.90),'interior','partitions',0)
                    C.box('Occupied table',(x,y,z+.77),(1.4,.7,.08),'timber','furniture',.004)
                    for dx in (-.58,.58):C.box('Table supports',(x+dx,y,z+.42),(.07,.50,.78),'timber','furniture',0)
                    C.qa_room_light('occupied bay',(x,y,z+2.9),110,3)
    # Recessed upper floor: one connected cross-shaped footprint.
    outline=[(-13.2,-13.2),(-2.4,-13.2),(-2.4,-15),(2.4,-15),(2.4,-13.2),(13.2,-13.2),
             (13.2,-2.4),(15,-2.4),(15,2.4),(13.2,2.4),(13.2,13.2),(2.4,13.2),(2.4,15),
             (-2.4,15),(-2.4,13.2),(-13.2,13.2),(-13.2,2.4),(-15,2.4),(-15,-2.4),(-13.2,-2.4)]
    z=13.85
    for i,a in enumerate(outline):
        b=outline[(i+1)%len(outline)];dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy)
        f=C.Face((*a,0),(dx/length,dy/length,0),(-dy/length,dx/length,0),'upper '+str(i))
        hs=[]
        if length>3:
            count=max(1,int(length/3.1))
            hs=[dict(id=f'upper {i} door {k}',u=(k+.5)*length/count,z=z+.13,w=min(2.25,length/count-.55),h=2.65,cols=2,rows=2) for k in range(count)]
        f.wall('Metal upper occupied wall',0,length,z,17.0,role='metal',holes=hs)
        for k,h in enumerate(hs):
            if k==0:f.door(h['id'],h['u'],h['z'],h['w'],h['h'],role='trim',glazed=True)
            else:window(f,h)
        seam_vertices=[];seam_faces=[]
        for k in range(math.ceil(length/.38)):
            u=(k+.5)*.38
            if u>length:continue
            spans=[(z,17.0)]
            for opening in hs:
                if abs(u-opening['u']) < opening['w']/2+.04:
                    lo,hi=opening['z']-.04,opening['z']+opening['h']+.04
                    spans=[s for a,b in spans for s in [(a,min(b,lo)),(max(a,hi),b)] if s[1]-s[0]>.02]
            for lo,hi in spans:
                offset=len(seam_vertices)
                seam_vertices.extend(f.p(u+du*.023/2,-.022+dd*.045/2,vz) for vz in (lo,hi) for du,dd in [(-1,-1),(1,-1),(1,1),(-1,1)])
                seam_faces.extend(tuple(offset+idx for idx in face) for face in C.BOX_FACES)
        if seam_vertices:C.mesh('Continuous panel seams with aperture gaps',seam_vertices,seam_faces,'trim','upper metal seam')
        f.part('Bounded roof parapet',length/2,.12,17.14,length,.27,.28,'wall','roof parapet',0)
        f.part('Parapet coping',length/2,.12,17.30,length,.32,.06,'coping','coping',0)
    roof=C.prism('Complete cross-shaped weathering roof',outline,'z',16.91,17.04,'roof','roof')
    # Terrace edge keeps physical glass with actual posts and gaps.
    for x in (-14.65,14.65):
        glass_rail((x,-14.65),(x,-2.6),13.9);glass_rail((x,2.6),(x,14.65),13.9)
    for y in (-14.65,14.65):
        glass_rail((-14.65,y),(-2.6,y),13.9);glass_rail((2.6,y),(14.65,y),13.9)
    for x in (-13.8,13.8):
        for y in (-13.8,13.8):
            C.box('Terrace planter box',(x,y,14.23),(1,1,.58),'planter','terrace planter',.008)
            C.box('Planter soil',(x,y,14.52),(.87,.87,.04),'timber','terrace planter',0)
    C.box('Roof service enclosure',(0,0,18.38),(7.8,9.0,2.70),'metal','service enclosure',0)
    C.box('Service enclosure coping',(0,0,19.77),(8.0,9.2,.13),'coping','service roof',0)
    C.box('Service access leaf',(0,-4.51,18.04),(1,.065,1.95),'trim','roof access',0)
    for x in (-3.91,3.91):
        for i in range(23):C.box('Service enclosure side standing seam',(x,-4.35+i*.39,18.38),(.045,.025,2.68),'trim','service metal seam',0)
    for y in (-4.51,4.51):
        for i in range(20):
            x=-3.7+i*.39
            if y<0 and abs(x)<.58:continue
            C.box('Service enclosure end standing seam',(x,y,18.38),(.025,.045,2.68),'trim','service metal seam',0)
    for i in range(3):
        x=-2.4+i*2.4
        C.box('Roof HVAC cabinet',(x,1,20.12),(1.0,1.4,.62),'coping','HVAC',.01)
    for x,y in [(-6,-5),(7,6),(-7,6),(6,-5)]:
        C.rod('Roof vent riser',(x,y,17.01),(x,y,17.85),.14,'coping','roof vent')
        C.rod('Vent weather cap',(x,y,17.84),(x,y,17.95),.22,'coping','roof vent')
    for x in (-2,1):
        # Cut real skylight apertures through the roof; curbs are four returns.
        import bpy
        cutter=C.box('Temporary skylight cut',(x,-7,17.0),(2.0,2.9,1.0),'roof','temporary cutter',0)
        bpy.context.view_layer.objects.active=roof
        mod=roof.modifiers.new('Full-depth rooflight opening','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
        bpy.ops.object.modifier_apply(modifier=mod.name)
        for names in C.MODULES.values():
            if cutter.name in names:names.remove(cutter.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
        for dx in (-1.1,1.1):C.box('Rooflight side curb',(x+dx,-7,17.2),(.2,3.3,.33),'coping','rooflight',0)
        for dy in (-1.55,1.55):C.box('Rooflight end curb',(x,-7+dy,17.2),(2.0,.2,.33),'coping','rooflight',0)
        C.box('Rooflight pane',(x,-7,17.39),(2.2,3.1,.03),'glass','rooflight',0)

if __name__=='__main__':S.run(sys.modules[__name__])
