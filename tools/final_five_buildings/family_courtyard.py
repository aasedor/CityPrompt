"""Seven-bay warm-brick perimeter block, authored from the locked October set."""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG='final-courtyard-block'
W,D,IW,ID=30.,24.4,15.,13.2
LEVELS=(.15,4.35,7.55,10.75)
ROOF=13.95
PALETTE=dict(wall=(.53,.30,.16),joint=(.39,.29,.20),trim=(.075,.13,.115),
    pale=(.64,.59,.48),roof=(.58,.59,.56),foundation=(.40,.41,.38),
    glass=(.47,.53,.51),hardware=(.055,.07,.065),interior=(.74,.68,.55),
    floor=(.49,.37,.23),timber=(.39,.23,.115),planting=(.21,.33,.095),
    blue=(.12,.23,.25),soil=(.19,.14,.08),flower=(.78,.69,.23))


def manifest(version):
    cams=G.camera_roster(W,D,14.65,[
        ('facade_close',(-9,-22,9),(-7,-12.2,7.7),52),
        ('architecture_close',(1.3,-18,2.2),(0,-10,1.8),38),
        ('glass_close',(-9,-15,2.1),(-9,-10,1.8),40),
        ('roof_contact',(-12,-17,18),(-11,-11,14.1),48),
        ('courtyard',(1,-4.8,1.85),(0,5,3.5),22),
        ('passage',(0,-11.9,1.8),(0,4,1.8),22),
        ('stairs',(10.7,-5.5,1.9),(10.7,2.9,4.8),24),
        ('upper_landing',(9.6,4.7,6),(10.7,0,4.8),24),
        ('interior',(-10,-7.5,5.95),(-10,-10.5,5.5),22),
        ('rear_entry',(0,17,2),(0,11.5,1.8),38)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}',method=C.METHOD,
        archetype_id=SLUG,variant_id=SLUG+'-v1',representation_kind='architectural_clay',
        state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=dict(width=W,depth=D,height=14.65),
            observed_storeys=4,front_bays=7,front_balcony_bays=[0,2,4,6],
            courtyard_m=[IW,ID],levels_m=LEVELS,
            inferred='30m frontage calibrates reference ratios. Hidden interiors and metric dimensions are original teaching assumptions.'),
        roof_contract=dict(type='continuous four-wing flat membrane with open ground-level courtyard',datum_m=ROOF,parapet_m=.7),
        identity_contract=dict(owner='seven-bay front; actual recessed balconies; through passage; stone podium; four-wing courtyard'),
        material_contract=dict(profile='source-palette architectural clay with physical brick coursing and stone joints',textured_keeper=False),
        programme_contract=dict(storeys=4,ground='six front shops and side shared rooms; open axial passage',upper='connected residential floors with illustrative furnished rooms',court='ground-level planted shared court',stairs='stacked supported flights in east wing with full floor apertures'),
        contact_contract=['Continuous grade-zero foundations','Open central passages','Recessed balcony cheeks and floors','Floor-cut internal stairs','Seated guards and planters'],
        runtime_contract=dict(scale='fixed_native_only',installation='not installed',review='NOT TESTED'),
        camera_roster=cams,mandatory_review_views=[c['name'] for c in cams])


def h(name,u,z,w,height,**kw):return dict(id=name,u=u,z=z,w=w,h=height,**kw)


def balcony(f,opening,level):
    u,w=opening['u'],opening['w'];z=LEVELS[level]
    # The main carrier ends at the recess. A real rear wall owns the glazing.
    back=C.Face(f.p(u,1.15,0),f.t,f.n,f.label+' balcony back')
    bh=h('Balcony garden door',0,z+.03,w-.24,2.57)
    G.wall(back,w,z,z+3.01,[bh])
    for sign in (-1,1):
        f.part('Recessed brick balcony cheek',u+sign*(w/2-.07),.58,z+1.50,.14,1.16,3.,'wall','balcony returns',0)
    f.part('Balcony stone bearing edge',u,.10,z-.085,w+.12,.43,.17,'pale','balcony slab',0)
    A.seated_guard('Open balcony guard',f.p(u-w/2+.10,.11,z),f.p(u+w/2-.10,.11,z),height=1.05,spacing=.14)
    # A small planter sits clear of the continuous doorway.
    f.part('Balcony planted container',u-w/2+.4,.52,z+.22,.44,.45,.44,'trim','balcony garden',0)
    x,y,_=f.p(u-w/2+.4,.52,z+.44);A.shrub(x,y,z+.44,.45)


def outer_face(f,span,bays,front=False):
    centres=[-span/2+(i+.5)*span/bays for i in range(bays)]
    openings=[]
    for i,u in enumerate(centres):
        if i==bays//2:
            openings.append(h('Through passage',u,.15,3.2,3.72,passage=True))
        else:
            openings.extend([h(f'Shop {i} display',u-.42,.42,2.17,2.85),h(f'Shop {i} entrance',u+1.24,.15,1.02,3.12,open=True)])
    f.wall(f.label+' stone ground storey',-span/2,span/2,.15,4.35,depth=.28,role='pale',holes=openings)
    for hole in openings:
        if hole.get('passage'):continue
        if hole.get('open'):G.open_door(f,hole)
        else:f.window(hole['id'],hole['u'],hole['z'],hole['w'],hole['h'],cols=2,depth=.28)
    for level in (1,2,3):
        z=LEVELS[level]
        hs=[h(f'{f.label} L{level} bay{i}',u,z if i%2==0 else z+.62,3.10 if i%2==0 else 2.55,2.96 if i%2==0 else 1.96,balcony=i%2==0)
            for i,u in enumerate(centres)]
        # Adjacent storeys meet on one datum; overlapping carriers flicker.
        f.wall(f.label+' upper brick',-span/2,span/2,z,z+3.20,depth=.28,holes=hs)
        G.brick_courses(f,-span/2,span/2,z,z+3.2,hs)
        for hole in hs:
            if hole['balcony']:balcony(f,hole,level)
            else:f.window(hole['id'],hole['u'],hole['z'],hole['w'],hole['h'],cols=3,depth=.28,curtain=True)
            f.part('Pale lintel',hole['u'],-.035,hole['z']+hole['h']+.07,hole['w']+.20,.34,.14,'pale','window heads',0)
    f.part('Continuous podium cornice',0,-.075,4.25,span+.08,.45,.18,'pale','cornice',0)
    for i,u in enumerate(centres):
        if i==bays//2:continue
        f.panel('Supported canvas shop awning',[(u-1.67,3.63),(u+1.67,3.63),(u+1.67,3.20),(u-1.67,3.20)],-.95,-.90,'trim','shop canopy')
        # Sloped weathering surface rather than a floating vertical panel.
        C.solid_surface('Shop sloped awning',[f.p(u-1.67,-.04,3.67),f.p(u+1.67,-.04,3.67),f.p(u+1.67,-.95,3.23),f.p(u-1.67,-.95,3.23)],.04,'trim','shop canopy')
        for du in (-1.58,1.58):C.beam('Awning bracket',f.p(u+du,.02,2.98),f.p(u+du,-.94,3.22),.035,.035,'hardware','shop canopy')


def side_face(f):
    hs=[]
    for level,z in enumerate(LEVELS):
        for i in range(7):
            u=-D/2+(i+.5)*D/7
            hs.append(h(f'Side level{level} bay{i}',u,z+.65,1.75,2.1))
    hs += [h('Side communal entrance',0,.15,1.5,2.8,open=True)]
    # Remove window overlapping the central entrance.
    hs=[v for v in hs if not(v['id']=='Side level0 bay3')]
    G.wall(f,D-.56,.15,ROOF,hs,courses=True)
    for z in LEVELS[1:]:f.part('Side pale floor band',0,-.03,z-.05,D,.32,.12,'pale','side bands',0)


def court_face(f,span,bays):
    centres=[-span/2+(i+.5)*span/bays for i in range(bays)]
    for level,z in enumerate(LEVELS):
        hs=[]
        for i,u in enumerate(centres):
            is_balcony=level>0 and i in (0,bays//2,bays//2+1,bays-1)
            width=3.2 if level==0 and i==bays//2 else 1.35 if level==0 else 1.65
            hs.append(h(f'Court L{level} bay{i}',u,z if is_balcony or not level else z+.60,
                        width,2.96 if is_balcony else 2.05 if level else 2.8,
                        open=level==0,balcony=is_balcony))
        top=LEVELS[level+1] if level<3 else ROOF
        f.wall(f.label+' occupied brick level',-span/2,span/2,z,top,depth=.28,holes=hs)
        G.brick_courses(f,-span/2,span/2,z,top,hs)
        for hole in hs:
            if hole['balcony']:balcony(f,hole,level)
            elif hole['open']:G.open_door(f,hole)
            else:f.window(hole['id'],hole['u'],hole['z'],hole['w'],hole['h'],cols=2,depth=.28)
        if level:f.part('Court stone stringcourse',0,-.10,z-.07,span,.14,.14,'pale','court bands',0)


def build():
    # Complete ring: shared corner slabs are not duplicated.
    front_depth=(D-ID)/2
    blocks=[(0,-(D+ID)/4,W,front_depth),(0,(D+ID)/4,W,front_depth),
            (-(W+IW)/4,0,(W-IW)/2,ID),((W+IW)/4,0,(W-IW)/2,ID)]
    for cx,cy,w,d in blocks:
        C.box('Complete wing foundation',(cx,cy,.075),(w,d,.15),'foundation','foundation',0)
        for level,z in enumerate(LEVELS):
            thickness=.15 if level==0 else .18
            # Exposed floor/roof end faces must not coincide with wall faces.
            sw,sd=(w-.56,d-.56) if cx==0 else (w-.56,d+.56)
            slab=C.box('Occupied ring floor',(cx,cy,z-thickness/2),(sw,sd,thickness),'floor','occupied floors',0)
            if cx>0 and level>0:
                C.cut_box(slab,'Through-floor stair aperture',(10.7,0,z),(1.75,6.20,.60))
                for xx in (9.8,11.6):A.seated_guard('Stairwell guard',(xx,-3.1,z),(xx,3.1,z),spacing=.16)
                if z==LEVELS[-1]:A.seated_guard('Stairwell near-end guard',(9.8,-3.1,z),(11.6,-3.1,z),spacing=.16)
        rw,rd=(w-.56,d-.56) if cx==0 else (w-.56,d+.56)
        C.box('Continuous wing roof',(cx,cy,ROOF-.1),(rw,rd,.20),'roof','roof',0)
    # Ground-floor finish does not extend below grade.
    C.box('Ground court paving',(0,0,.075),(IW,ID,.15),'foundation','courtyard',0)
    fs=A.faces(W,D)
    outer_face(fs[0],W,7,True);outer_face(fs[2],W,7)
    side_face(fs[1]);side_face(fs[3])
    inward=[C.Face((0,-ID/2,0),(-1,0,0),(0,-1,0),'court south'),
            C.Face((0,ID/2,0),(1,0,0),(0,1,0),'court north'),
            C.Face((-IW/2,0,0),(0,1,0),(-1,0,0),'court west'),
            C.Face((IW/2,0,0),(0,-1,0),(1,0,0),'court east')]
    for f,span in zip(inward,(IW,IW,ID,ID)):court_face(f,span,7 if span==IW else 5)
    # Inward wall runs meet at the court vertex, leaving the outward 28cm
    # square unowned. A solid corner pier closes that shaft at every level.
    for sx in (-1,1):
        for sy in (-1,1):
            C.box('Continuous inner corner pier',(sx*(IW/2+.14),sy*(ID/2+.14),(.15+ROOF+.64)/2),
                  (.28,.28,ROOF+.64-.15),'wall','court corner junctions',0)
            # Existing coping runs extend 3cm beyond their wall endpoints.
            # This cap starts at those ends; it does not duplicate their tops.
            C.box('Inner corner coping closure',(sx*(IW/2+.18),sy*(ID/2+.18),ROOF+.675),
                  (.30,.30,.07),'pale','court corner junctions',0)
    # The axial court doors are full openings. Clear passage has no opaque end cap.
    for sign in (-1,1):
        for xx in (-1.73,1.73):
            C.box('Stone passage return',(xx,sign*(D+ID)/4,1.96),(.26,front_depth-.56,3.62),'pale','passage',0)
        C.box('Passage soffit',(0,sign*(D+ID)/4,3.91),(3.2,front_depth-.56,.18),'pale','passage',0)
        y=-D/2 if sign<0 else D/2
        C.prism('Gentle full passage threshold',[(-1.6,y), (1.6,y),(1.6,y+sign*.9),(-1.6,y+sign*.9)],'z',0,.15,'foundation','entrance')
    for f,span in [(fs[0],W),(fs[1],D-.56),(fs[2],W),(fs[3],D-.56),*zip(inward,(IW,IW,ID,ID))]:
        f.part('Brick roof parapet',0,.14,ROOF+.32,span,.28,.64,'wall','parapet',0)
        f.part('Stone coping',0,.14,ROOF+.675,span+.06,.38,.07,'pale','coping',0)
    for x in (-11,11):
        for y in (-8.7,8.7):
            C.box('Mechanical roof curb',(x,y,ROOF+.15),(1.9,1.5,.30),'hardware','roof equipment',0)
            C.box('Mechanical unit',(x,y,ROOF+.65),(1.7,1.3,.8),'roof','roof equipment',0)
            for j in range(9):C.box('Mechanical louver',(x-.76+j*.19,y-.657,ROOF+.66),(.04,.02,.65),'trim','roof equipment',0)
    for i in range(3):G.stair('Internal stair '+str(i),10.7,-3,LEVELS[i],LEVELS[i+1],length=6,landing_gap=.10)
    # Shared court paths stay at ground level and retain a clear centre axis.
    for x in (-5.4,5.4):
        for y in (-3.9,3.9):
            C.box('Garden bed',(x,y,.32),(2.0,2.0,.34),'pale','garden bed',0)
            C.box('Garden soil',(x,y,.50),(1.8,1.8,.03),'soil','garden bed',0)
            A.small_tree(x,y,.51,3.3,.8)
    for x in (-2.8,2.8):
        for y in (-2.8,2.8):
            C.box('Perennial border',(x,y,.27),(1.1,1.8,.24),'pale','garden bed',0)
            for dy in (-.5,0,.5):A.shrub(x,y+dy,.40,.65)
    for x in (-4.5,4.5):
        for y in (-.8,.8):A.garden_chair(x,y,.15)
    # A central planted island and perimeter borders match the nadir garden.
    # The entrance axis bifurcates around the island with two clear 1.6m paths.
    for x,y,w,d in [(0,0,2.2,2.2),(-6.65,0,.65,7),(6.65,0,.65,7),
                    (-3.8,-5.8,3,.55),(3.8,-5.8,3,.55),(-3.8,5.8,3,.55),(3.8,5.8,3,.55)]:
        C.box('Planted courtyard border',(x,y,.29),(w,d,.28),'pale','garden bed',0)
        C.box('Recessed bed soil',(x,y,.44),(w-.1,d-.1,.04),'soil','garden bed',0)
        for j in range(max(2,int(max(w,d)/.55))):
            t=(j+.5)/max(2,int(max(w,d)/.55))-.5
            A.shrub(x+t*(w-.25) if w>d else x,y+t*(d-.25) if d>=w else y,.46,.47)
    for x in (-4.7,4.7):
        C.box('Court bench slatted seat',(x,0,.64),(.55,2.4,.12),'timber','garden furniture',0)
        for y in (-.9,.9):C.box('Bench seated leg',(x,y,.36),(.4,.12,.42),'hardware','garden furniture',0)
    # Shelves, varied goods, cafe seating and hanging lights make the retail
    # programme legible through the actual cut storefronts.
    for sign in (-1,1):
        for index,x in enumerate((-12.85,-8.57,-4.28,4.28,8.57,12.85)):
            y=sign*7.25
            if index%2==0:
                for z in (.55,1.15,1.75,2.35):
                    C.box('Retail stocked shelf',(x,y,z),(2.7,.42,.08),'timber','retail programme',0)
                    for j in range(7):
                        C.box('Retail display package',(x-1.13+j*.37,y,z+.17),(.23,.27,.26),'interior' if j%2 else 'blue','retail goods',0)
                for dx in (-1.35,1.35):C.box('Shelf upright',(x+dx,y,1.45),(.06,.4,2.7),'trim','retail programme',0)
            else:
                C.box('Cafe table top',(x,sign*10.3,.88),(1.3,.7,.09),'timber','cafe programme',0)
                C.box('Cafe table pedestal',(x,sign*10.3,.5),(.12,.12,.75),'hardware','cafe programme',0)
                A.garden_chair(x-.9,sign*10.3,.15);A.garden_chair(x+.9,sign*10.3,.15)
            C.rod('Pendant suspension',(x,sign*10.2,3.3),(x,sign*10.2,4.1),.018,'hardware','retail lighting',8)
            C.box('Pendant diffuser',(x,sign*10.2,3.25),(.34,.34,.15),'pale','retail lighting',0)
    # Illustrative room programme is visible through glazing, with clear aisles.
    for level,z in enumerate(LEVELS):
        for sign in (-1,1):
            for x in (-10.5,-6.3,6.3,10.5):
                y=sign*9.15
                if level:
                    A.sofa(x,y,z);A.bed(x,sign*10.6,z)
                else:
                    C.box('Shop counter',(x,y,z+.47),(2.2,.7,.94),'timber','shop fixtures',0)
                    C.box('Shop display',(x,y-.1,z+1.02),(1.9,.5,.15),'interior','shop fixtures',0)
                C.qa_room_light('Occupied room',(x,y,z+2.9),170,3)
    C.CONTACTS.append(dict(name='Axial ground-level passage',width_m=3.2,clear_height_m=3.72,grade_m=.15))
