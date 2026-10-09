"""Five-storey independent seniors residence with three balcony columns and terrace wing."""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG='final-seniors-apartments'
LEVELS=(.15,4.15,7.35,10.55,13.75)
ROOF=16.95
PALETTE=dict(wall=(.66,.51,.31),joint=(.48,.43,.33),trim=(.24,.24,.17),
    pale=(.66,.64,.55),roof=(.47,.49,.46),foundation=(.40,.42,.39),glass=(.50,.57,.52),
    hardware=(.06,.075,.07),interior=(.77,.71,.57),floor=(.54,.44,.30),
    timber=(.52,.32,.14),planting=(.19,.31,.095),soil=(.15,.12,.075),blue=(.20,.34,.34))

def manifest(version):
    cams=G.camera_roster(40,22,19,[
        ('facade_close',(-8,-17,10),(-5.3,-8,8.8),44),
        ('architecture_close',(2,-17,2.4),(0,-8,2.2),34),
        ('glass_close',(17,-10,2),(16,-5,1.9),26),
        ('roof_contact',(5,-8,23),(0,1,18),42),
        ('passage',(0,-7.8,1.85),(0,-1,1.85),22),
        ('courtyard',(19,3,6),(13,-1,4.7),22),
        ('stairs',(-8,-2,1.9),(-8,5.8,4.7),24),
        ('upper_landing',(-6.6,6.5,5.8),(-8,2,4.7),24),
        ('apartment',(3,-3.8,8.9),(0,-6,8.9),22),
        ('lounge',(13,-3,1.85),(18,-6.7,1.85),22)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}',method=C.METHOD,archetype_id=SLUG,variant_id=SLUG+'-v1',
        representation_kind='architectural_clay',state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=dict(width=32,depth=18.3,height=19.15),observed_storeys=5,balcony_columns=3,
            main_block_m=[24,16],lounge_wing_m=[8,13.6],inferred='Metric scale, hidden rooms and independent-living occupancy are teaching assumptions.'),
        roof_contract=dict(type='flat main roof plus occupied single-storey wing terrace',datum_m=ROOF),
        identity_contract=dict(owner='buff brick, three recessed balcony columns, narrow end windows, timber entrance and right terrace wing'),
        material_contract=dict(profile='source-palette architectural clay; physical brick courses and timber fins',textured_keeper=False),
        programme_contract=dict(storeys=5,ground='lobby and common lounge',upper='independent apartments',terrace='shared garden reached from second floor',stairs='continuous floor-cut stair; lift core illustrative only'),
        contact_contract=['Open main entry','Terrace connected to upper floor','Seated railings','Supported entrance canopy','Clear staircase'],
        runtime_contract=dict(scale='fixed_native_only',review='NOT TESTED'),camera_roster=cams,mandatory_review_views=[c['name'] for c in cams])

def hole(name,u,z,w,h,**kw):return dict(id=name,u=u,z=z,w=w,h=h,**kw)

def build():
    fs=A.faces(24,16)
    C.box('Main foundation',(0,0,.075),(24,16,.15),'foundation','foundation',0)
    for z in LEVELS[1:]:
        floor=C.box('Residential floor',(0,0,z-.09),(23.44,15.44,.18),'floor','floors',0)
        C.cut_box(floor,'Stair full aperture',(-8,3,z),(1.9,6.3,.7))
        for x in (-8.98,-7.02):A.seated_guard('Stair floor guard',(x,-.15,z),(x,6.15,z),spacing=.16)
        if z==LEVELS[-1]:A.seated_guard('Stair near-end upper guard',(-8.98,-.15,z),(-7.02,-.15,z),spacing=.16)
    C.box('Main roof diaphragm',(0,0,ROOF-.1),(23.44,15.44,.2),'roof','roof',0)
    front=fs[0]
    ground=[hole('Main lobby doors',0,.15,2.5,3.1,open=True)]
    for x in (-9.8,-6.4,6.4,9.8):ground.append(hole('Ground lounge window',x,.6,2.35,2.8,cols=3))
    G.wall(front,24,.15,4.15,ground,courses=True)
    for level in range(1,5):
        z=LEVELS[level];hs=[hole('Recessed apartment balcony',x,z,4.35,2.96) for x in (-5.3,0,5.3)]
        hs += [hole('End apartment window',x,z+.45,1.8,2.5) for x in (-9.8,9.8)]
        front.wall('Occupied upper front',-12,12,z,z+3.2,depth=.28,holes=hs)
        G.brick_courses(front,-12,12,z,z+3.2,hs)
        for h in hs:
            if h['w']<2:front.window(h['id'],h['u'],h['z'],h['w'],h['h'],cols=2,rows=2,curtain=True);continue
            x=h['u'];back=C.Face(front.p(x,1.45,0),front.t,front.n,'apartment balcony back')
            G.wall(back,4.35,z,z+3.0,[hole('Balcony glazing',0,z+.03,3.9,2.65,cols=3)])
            for sign in (-1,1):front.part('Balcony recessed cheek',x+sign*2.105,.73,z+1.5,.14,1.46,3,'timber','balcony',0)
            front.part('Balcony bearing slab',x,.16,z-.08,4.45,.4,.16,'pale','balcony',0)
            # The locked facade has three clear infill panels, not dense pickets.
            for xx in (x-2,x-2/3,x+2/3,x+2):
                C.box('Seated balcony post',(xx,-7.78,z+.525),(.045,.045,1.05),'hardware','balcony',0)
            for zz in (z+.045,z+1.035):
                C.box('Balcony continuous rail',(x,-7.78,zz),(4.04,.045,.045),'hardware','balcony',0)
            for j in range(3):
                lo=x-2+j*4/3+.035;hi=lo+4/3-.07
                G.optical_surface('Clear balcony infill',[(lo,-7.78,z+.075),(hi,-7.78,z+.075),
                    (hi,-7.78,z+1.01),(lo,-7.78,z+1.01)],(0,1,0),module='balcony')
            A.garden_chair(x-.9,-7.1,z);A.garden_chair(x+.8,-7.1,z)
            C.box('Balcony planted container',(x+1.55,-6.95,z+.22),(.48,.50,.44),'trim','balcony',0)
            A.shrub(x+1.55,-6.95,z+.44,.5)
    for f,span in [(fs[1],15.44),(fs[2],24),(fs[3],15.44)]:
        hs=[];count=4 if span<20 else 7
        for level,z in enumerate(LEVELS):
            for i in range(count):
                u=-span/2+(i+.5)*span/count
                hs.append(hole(f.label+f' window{level}-{i}',u,z+.65,1.65,2.15))
        if f==fs[1]:
            hs=[h for h in hs if h['z']>1 and not(h['z']<5 and abs(h['u']+2)<2)]
            hs.append(hole('Exposed rear ground window',6.8,.8,1.2,2.15))
            hs += [hole('Lounge connecting doorway',-2,.15,2.3,3,open=True),hole('Shared terrace doorway',-2,4.15,2.3,2.8,open=True)]
        if f==fs[2]:
            hs=[h for h in hs if not(h['z']<1 and abs(h['u'])<1)]
            hs.append(hole('Rear residential exit',0,.15,1.5,2.8,open=True))
        G.wall(f,span,.15,ROOF,hs,courses=True)
    for f,span in [(fs[0],24),(fs[1],15.44),(fs[2],24),(fs[3],15.44)]:
        f.part('Buff brick roof parapet',0,.14,ROOF+.2,span,.28,.4,'wall','parapet',0)
        f.part('Seated metal coping',0,.14,ROOF+.44,span+.04,.36,.08,'trim','coping',0)
    # Warm timber portal with actual side-fin support and clear central doors.
    for x in (-4.3,-3.9,-3.5,-3.1,-2.7,2.7,3.1,3.5,3.9,4.3):
        C.box('Timber entrance screen fin',(x,-8.8,1.95),(.14,1.6,3.6),'timber','entrance canopy',0)
    C.box('Supported portal roof',(0,-8.85,3.91),(9.2,1.9,.25),'roof','entrance canopy',0)
    # Low right wing with an occupied garden above; no duplicate shared west wall.
    C.box('Lounge foundation',(16,-1.2,.075),(8,13.6,.15),'foundation','foundation',0)
    C.box('Garden terrace slab',(15.81,-1.2,4.05),(7.82,13.04,.20),'pale','terrace floor',0)
    wingfaces=[(C.Face((16,-8,0),(1,0,0),(0,1,0),'lounge front'),8),
               (C.Face((20,-1.2,0),(0,1,0),(-1,0,0),'lounge east'),13.04),
               (C.Face((15.86,5.6,0),(-1,0,0),(0,-1,0),'lounge rear'),8.28)]
    for f,span in wingfaces:
        count=3 if span<9 else 5
        hs=[hole('Shared lounge daylight',-span/2+(i+.5)*span/count,.6,1.65,2.5) for i in range(count)]
        G.wall(f,span,.15,4.15,hs,courses=True)
        A.seated_guard('Terrace protective guard',f.p(-span/2,.16,4.15),f.p(span/2,.16,4.15),height=1.1,spacing=.16)
    for x,y,w,d in [(19.05,-1.2,1.1,11.8),(15.5,-7.1,5.4,.9),(15.5,4.65,5.4,1.),
                    (17.8,-1.2,2.5,.8),(17.8,-5.7,2.5,.8)]:
        C.box('Terrace planting trough',(x,y,4.42),(w,d,.54),'pale','terrace garden',0)
        for i in range(int(max(w,d)/.55)):
            t=(i+.5)/int(max(w,d)/.55)-.5
            A.shrub(x+t*w if w>d else x,y+t*d if d>w else y,4.7,.55)
    C.box('Shared terrace dining table',(16,1.5,4.95),(2.2,1.2,.12),'timber','terrace furniture',0)
    for x in (15.1,16.9):
        for y in (1.05,1.95):C.box('Table seated leg',(x,y,4.52),(.08,.08,.74),'hardware','terrace furniture',0)
    for x,y in [(14.5,1.5),(17.5,1.5),(15.3,.2),(16.7,.2),(15.3,2.8),(16.7,2.8)]:A.garden_chair(x,y,4.15)
    C.box('Umbrella weighted foot',(16,1.5,4.23),(.5,.5,.16),'pale','terrace furniture',0)
    C.rod('Dining umbrella pole',(16,1.5,4.23),(16,1.5,7.1),.035,'hardware','terrace furniture')
    ring=[(16+1.8*math.cos(i*math.pi/4),1.5+1.8*math.sin(i*math.pi/4),6.72) for i in range(8)]
    C.mesh('Folded cream umbrella',[(16,1.5,7.1),*ring],[(0,i+1,(i+1)%8+1) for i in range(8)],'pale','terrace furniture')
    A.sofa(15.8,-2.4,4.15)
    for x in (14.8,16.5):A.garden_chair(x,-4.6,4.15)
    for x,y in [(19,3.8),(19,-6.1)]:A.small_tree(x,y,4.7,2.2,.45)
    for i in range(4):G.stair('Resident stair '+str(i),-8,0,LEVELS[i],LEVELS[i+1],length=6)
    for level,z in enumerate(LEVELS):
        for x in (-5.3,0,5.3):
            if level:A.bed(x,-2,z);A.sofa(x,-4.8,z)
            else:A.sofa(x,-3.6,z)
            C.qa_room_light('Occupied apartment',(x,-3,z+2.9),160,3)
    for x in (14,17):
        for y in (-5,2):A.sofa(x,y,.15);C.qa_room_light('Common lounge',(x,y,3.3),180,3)
    for x,y,w,d,h in [(1,3,3,3,1.8),(-3,3,2.2,2,1.0),(5,4,1.4,1.5,1.1),(-2,-4,1.8,1.4,.8)]:
        C.box('Mechanical seated curb',(x,y,ROOF+.12),(w+.2,d+.2,.24),'hardware','plant',0)
        C.box('Rooftop mechanical equipment',(x,y,ROOF+.24+h/2),(w,d,h),'roof','plant',0)
    C.CONTACTS.append(dict(name='Five occupied floors plus one-storey lounge',floors=5,terrace_datum=4.15))
