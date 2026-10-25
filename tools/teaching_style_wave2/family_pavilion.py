"""Original reading pavilion: physical cusped arcades and supported rounded dome."""
import math

import bpy
import clay_core as C
from profiles import cusped_arch_curve

SUPPORT_FILES=('profiles.py',)


def specification(make_cameras):
    details=[
        ('facade_close',(-2,-12,2.9),(0,-5.9,2.65),36),
        ('architecture_close',(-9,-10,8.8),(0,0,6.25),38),
        ('glass_close',(-3.8,-8.8,2.2),(-3.8,-5.7,2.8),28),
        ('roof_contacts',(-2.8,-9.5,4.2),(-1.9,-6.1,4.85),40),
        ('reading_programme',(-1.1,-4.7,2.0),(4,-2.1,1.30),25),
        ('entrance_low',(1.4,-11.7,1.4),(0,-6.0,1.6),28),
    ]
    return dict(archetype_id='mughal_reading_pavilion',variant_id='cusped_arcade_central_dome',
        candidate='mughal-reading-pavilion-clay',title='Mughal-inspired reading pavilion',
        source_roles=('front','oblique','top','rear_oblique'),
        dimensions_m=dict(width=14.6,depth=14.6,height=8.30),floors=1,
        teaching=dict(description='Mughal architecture developed in South Asia through exchanges among Persian, Central Asian and local traditions. Repeated arches, symmetry, shaded pavilions and contrasts of red and pale stone are useful features to recognise here.',
            features=['Repeated cusped open arches','Projecting shaded roof with brackets','Pale central dome on a red drum'],
            main_idea='Order spaces through repetition, shade and a central focus.',
            source='https://whc.unesco.org/en/list/231/'),
        cameras=make_cameras(14.6,14.6,8.3,details),
        palette=dict(wall=(.43,.19,.125),trim=(.73,.63,.45),roof=(.37,.17,.11),
            floor=(.56,.48,.36),timber=(.25,.135,.060),interior=(.68,.59,.43),
            hardware=(.34,.21,.07),paper=(.84,.80,.66),cushion=(.56,.49,.35),
            bookgreen=(.10,.21,.13),bookred=(.34,.07,.038),bookcream=(.68,.54,.30)),
        roof_contract='One closed square deck and continuous bracket-supported projecting chajja. Low parapet and seated central octagonal drum carry a source-shaped low rounded dome and small finial. Four internal piers and crossing beams support the central roof zone.',
        programme_contract='Open-air reading room with visible bookshelves, open books on supported tables, chairs and low cushioned benches. A clear central cross connects front/rear and side arcades. No glass is present or implied.',
        contact_contract=['Twelve genuinely cut cusped outer arches, lined on front and back','Four internal bearing piers and crossing beams','Paired brackets physically seat below the roof slab','Native red plinth and three front/rear steps only','Dome shell seats on a closed octagonal drum'],
        measurement_notes=[
            'Source has exactly three arches on every repeated facade, low rounded cream dome, red octagonal drum, projecting cream chajja, red parapet and paired brackets at piers.',
            'Outer wall square12m, native plinth13.2m, roof eaves14.6m. Floor0.55m, spring2.85m, clear arch crown4.45m, roof top5.27m, parapet6.0m, dome7.67m, finial8.3m.',
            'Metric size is inferred by normalizing source front wall width to12m; rendered proportions override the prompt7m crown and requested strongly onion-shaped dome.',
            'The top source is high aerial, not an orthographic measured roof plan. All four compatible views are locked.',
            'Internal support grid, exact curved section, furniture plan and hidden weathering construction are architectural inferences; not surveyed or engineering-certified.',
            'glass_close is retained as the mandatory opening-section camera name, with glazing explicitly N/A: all twelve exterior arcades are open air.',
            'Only the source-native red plinth, pale floor lip and small centred steps are exported. There is no surrounding grey site platform or QA ground in the model.',
        ])


def shaped_arch(face,owner,name,u):
    clear=cusped_arch_curve(3.0,2.85,4.45)
    structural=cusped_arch_curve(3.07,2.85,4.485)
    polygon=[(u-1.535,.50),*[(u+x,z) for x,z in structural],(u+1.535,.50)]
    cutter=face.panel(name+' entire shaped carrier cutter',polygon,-.35,1.05,'wall','construction cutter')
    bpy.context.view_layer.objects.active=owner
    mod=owner.modifiers.new(name+' full thickness void','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name);C.remove_cutter(cutter);C.normalise(owner.data)
    inner=[(-1.5,.55),*clear,(1.5,.55)]
    outer=[(-1.66,.55),*cusped_arch_curve(3.32,2.85,4.61),(1.66,.55)]
    count=len(inner)
    verts=[face.p(u+x,depth,z) for depth,curve in [(-.055,outer),(-.055,inner),(.705,outer),(.705,inner)] for x,z in curve]
    faces=[]
    for i in range(count-1):
        j=i+1
        faces.extend([(i,j,count+j,count+i),(2*count+i,3*count+i,3*count+j,2*count+j),
                      (i,2*count+i,2*count+j,j),(count+i,count+j,3*count+j,3*count+i)])
    for i in (0,count-1):faces.append((i,count+i,3*count+i,2*count+i))
    C.mesh(name+' complete pale arch border and inner reveal',verts,faces,'trim','physical cusped arch lining')
    C.OPENINGS.append(dict(id=name,face=face.label,u=u,z=.55,width=3.0,height=3.90,
        kind='open-air cusped arch',aperture_shape='source-specific six-cusp half-profile',
        clear_wall_cut=True,carrier_depth_m=.65,frame_inset_m=-.055,pane_inset_m=None,
        face_origin=list(face.o),face_tangent=list(face.t),face_inward=list(face.n),
        glazing='N/A, deliberately open air',occupied_space='common open reading pavilion',
        structural_profile_clearance_m=.035,curve_points=len(clear)))


def bracket(face,u):
    # Extrude the curved stepped bracket section along its narrow width.
    section=[(.15,5.05),(-1.03,5.05),(-1.03,4.91),(-.83,4.86),
             (-.69,4.59),(-.54,4.54),(-.43,4.69),(.15,4.69)]
    verts=[face.p(u+dx,d,z) for dx in (-.075,.075) for d,z in section]
    n=len(section);faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]
    faces.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    C.mesh('Paired seated stone roof bracket',verts,faces,'trim','chajja brackets')


def lathe(name,profile,role,module,sides=96):
    # Full solid radial section; caller closes/reverses the profile as needed.
    verts=[(r*math.cos(i*math.tau/sides),r*math.sin(i*math.tau/sides),z)
           for r,z in profile for i in range(sides)]
    faces=[]
    for j in range(len(profile)-1):
        for i in range(sides):
            k=(i+1)%sides
            faces.append((j*sides+i,j*sides+k,(j+1)*sides+k,(j+1)*sides+i))
    faces.extend([tuple(range(sides-1,-1,-1)),tuple(range((len(profile)-1)*sides,len(profile)*sides))])
    obj=C.mesh(name,verts,faces,role,module)
    for poly in obj.data.polygons[:-2]:poly.use_smooth=True
    return obj


def dome():
    octagon=[(1.78*math.cos(math.pi/8+i*math.tau/8),1.78*math.sin(math.pi/8+i*math.tau/8)) for i in range(8)]
    C.prism('Closed red octagonal dome drum',octagon,'z',5.25,6.24,'wall','central dome support')
    for z in (5.89,6.22):
        rim=[(1.84*math.cos(math.pi/8+i*math.tau/8),1.84*math.sin(math.pi/8+i*math.tau/8)) for i in range(8)]
        C.prism('Dome drum seated stringcourse',rim,'z',z-.045,z+.045,'trim','central dome support')
    profile=[(1.53,6.24),(1.53,6.36),(1.49,6.61),(1.39,6.88),(1.23,7.13),
             (1.01,7.35),(.75,7.52),(.44,7.62),(.17,7.665),(.018,7.67)]
    inner=[(max(.012,r-.12),z-.10) for r,z in reversed(profile)]
    lathe('Closed pale rounded dome shell',profile+inner,'trim','source dome')
    # Source meridian joints remain narrow physical ribs, no painted texture.
    for i in range(16):
        angle=i*math.tau/16
        for a,b in zip(profile[:-2],profile[1:-1]):
            C.rod('Dome fine meridian joint',((a[0]+.008)*math.cos(angle),(a[0]+.008)*math.sin(angle),a[1]),
                  ((b[0]+.008)*math.cos(angle),(b[0]+.008)*math.sin(angle),b[1]),.012,'interior','dome fine joints',8)
    lathe('Seated small dome finial',[(.13,7.64),(.13,7.72),(.06,7.78),(.09,7.84),(.09,7.92),(.045,7.97),(.065,8.04),(.065,8.11),(.035,8.16),(.008,8.30)],'hardware','dome finial',32)


def bookshelf(x,y):
    for dx in (-.77,.77):C.box('Reading shelf side',(x+dx,y,1.43),(.07,.42,1.76),'timber','reading shelves')
    C.box('Reading shelf back',(x,y+.19,1.43),(1.61,.04,1.76),'timber','reading shelves')
    for k in range(5):
        z=.61+k*.42
        C.box('Open book shelf',(x,y,z),(1.60,.42,.06),'timber','reading shelves')
        if k==4:continue
        for i in range(12):
            h=.26+.012*((i+k)%4)
            C.box('Individual bound volume',(x-.70+i*.125,y-.04,z+.035+h/2),(.09,.27,h),('bookgreen','bookred','bookcream')[i%3],'reading books',0)


def reading_table(x,y):
    top=1.38
    C.box('Reading tabletop',(x,y,top),(1.65,.86,.09),'timber','reading tables')
    for dx in (-.66,.66):
        for dy in (-.29,.29):C.box('Reading table leg',(x+dx,y+dy,.94),(.065,.065,.78),'timber','reading tables')
    # Two visibly open pages meet at their low spine on the worktop.
    C.solid_surface('Open book left page',[(x-.35,y-.20,top+.055),(x-.02,y-.20,top+.080),
        (x-.02,y+.23,top+.080),(x-.35,y+.23,top+.055)],.012,'paper','open reading books')
    C.solid_surface('Open book right page',[(x-.02,y-.20,top+.080),(x+.31,y-.20,top+.055),
        (x+.31,y+.23,top+.055),(x-.02,y+.23,top+.080)],.012,'paper','open reading books')
    for dx in (-.48,.48):
        xx=x+dx;yy=y-.85
        C.box('Reading chair seat',(xx,yy,1.04),(.43,.43,.07),'timber','reading chairs')
        for a in (-.16,.16):
            for b in (-.16,.16):C.box('Chair bearing leg',(xx+a,yy+b,.79),(.045,.045,.48),'timber','reading chairs',0)
        for a in (-.16,.16):C.box('Chair back stile',(xx+a,yy-.18,1.25),(.045,.045,.80),'timber','reading chairs')
        C.box('Reading chair back',(xx,yy-.18,1.53),(.38,.055,.16),'timber','reading chairs')


def bench(x,y):
    C.box('Bench timber seat',(x,y,1.03),(.70,2.12,.10),'timber','reading benches')
    outward=1 if x>0 else -1
    C.box('Bench backed frame',(x+outward*.30,y,1.26),(.065,2.10,.63),'timber','reading benches')
    for yy in (-.87,.87):
        for xx in (-.24,.24):C.box('Bench support',(x+xx,y+yy,.77),(.07,.07,.44),'timber','reading benches')
    for yy in (-.65,0,.65):
        C.box('Bench seat cushion',(x,y+yy,1.12),(.60,.59,.12),'cushion','reading benches',.025)
        C.box('Bench back cushion',(x+outward*.20,y+yy,1.37),(.13,.55,.42),'interior','reading benches',.025)


def construct():
    C.box('Source native red plinth',(0,0,.24),(13.2,13.2,.48),'wall','native foundation',0)
    C.box('Source native pale floor lip',(0,0,.515),(13.30,13.30,.07),'floor','native foundation',0)
    for sign in (-1,1):
        for i in range(3):
            height=(i+1)*.55/3
            y=sign*(7.38-i*.31)
            C.box('Centred native approach step',(0,y,height/2),(3.70,.34,height),'trim','entry steps',0)
    front=C.Face((0,-6,0),(1,0,0),(0,1,0),'front arcade')
    rear=C.Face((0,6,0),(1,0,0),(0,-1,0),'rear arcade')
    left=C.Face((-6,0,0),(0,1,0),(1,0,0),'left arcade')
    right=C.Face((6,0,0),(0,1,0),(-1,0,0),'right arcade')
    for face in (front,rear,left,right):
        lo,hi=(-6,6) if face in (front,rear) else (-5.35,5.35)
        owner=face.wall('Complete red arcade carrier',lo,hi,.55,5.05,depth=.65)
        for u in (-3.8,0,3.8):shaped_arch(face,owner,face.label+' arch'+str(u),u)
        for u in (-5.65,-1.90,1.90,5.65):
            face.part('Pier seated red foot',u,.30,.64,1.0,.86,.18,'wall','pier bases')
            face.part('Pier pale narrow foot band',u,.30,.75,.91,.84,.07,'trim','pier bases')
            for offset in (-.13,.13):bracket(face,u+offset)
            face.part('Pier capital bearing band',u,.30,4.86,.85,.82,.15,'wall','pier capitals')
    for x in (-1.9,1.9):
        for y in (-1.9,1.9):
            C.box('Internal bearing pier',(x,y,2.70),(.64,.64,4.30),'wall','interior support grid')
            C.box('Internal pier foot',(x,y,.65),(.82,.82,.20),'wall','interior support grid')
            C.box('Internal pier capital',(x,y,4.72),(.90,.90,.30),'trim','interior support grid')
        C.box('Continuous crossing roof beam X',(x,0,4.87),(.43,11.4,.36),'timber','crossing roof support')
        C.box('Continuous crossing roof beam Y',(0,x,4.87),(11.4,.43,.36),'timber','crossing roof support')
    C.box('Closed square weathering deck',(0,0,5.16),(14.6,14.6,.22),'trim','source chajja roof',0)
    C.box('Source red weathering surface within parapets',(0,0,5.285),(11.70,11.70,.035),'roof','source chajja roof',0)
    for axis in ('x','y'):
        for sign in (-1,1):
            loc=(sign*6,0,5.58) if axis=='x' else (0,sign*6,5.58)
            size=(.30,12.3,.62) if axis=='x' else (11.7,.30,.62)
            C.box('Continuous red parapet',loc,size,'wall','roof parapet',0)
            caploc=(sign*6,0,5.955) if axis=='x' else (0,sign*6,5.955)
            capsize=(.41,12.41,.09) if axis=='x' else (11.59,.41,.09)
            C.box('Seated pale parapet coping',caploc,capsize,'trim','roof parapet',0)
    for face in (front,rear,left,right):
        for u in (-5.65,-1.9,1.9,5.65):face.part('Pale parapet pier cap',u,.08,5.70,.30,.44,.76,'trim','parapet cadence',0)
    dome()
    for x in (-3.6,3.6):reading_table(x,-2.7);bookshelf(x,1.60)
    for x in (-5.10,5.10):
        for y in (-3.65,3.65):bench(x,y)
    C.CONTACTS.extend([
        dict(name='Arcade wall and support system',outer_arches=12,internal_piers=4,crossing_beams=4,carrier_depth_m=.65,notes='Every curved arch is cut through its complete carrier. Inner and outer stone linings have full depth and back faces.'),
        dict(name='Source native plinth and approach',floor_m=.55,risers=3,rise_m=.55/3,tread_m=.31,width_m=3.7,notes='Source-native stepped plinth, not an accessible-route claim or a surrounding site installation.'),
        dict(name='Open-air section',glazing='N/A: no panes, screens or optical textures',glass_close_role='Mandatory opening-section proof under legacy camera name'),
    ])
    for x,y in [(-3,-2),(3,-2),(-3,2),(3,2)]:C.qa_room_light('pavilion reading',(x,y,4.5),120,2.5)
