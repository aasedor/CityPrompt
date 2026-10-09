"""Urban supermarket: four depthwise roof lanterns, transparent front and stocked aisles."""
import clay_core as C
import assemblies as A
import geometry as G

SLUG='final-urban-grocery'
W,D,EAVE,PEAK=20.,12.,5.3,7.0
PALETTE=dict(wall=(.51,.24,.12),joint=(.40,.32,.24),trim=(.065,.085,.085),pale=(.69,.65,.54),
    roof=(.40,.49,.54),foundation=(.43,.44,.42),glass=(.47,.57,.58),hardware=(.06,.07,.075),
    interior=(.75,.68,.51),floor=(.53,.52,.44),timber=(.49,.30,.14),planting=(.20,.34,.10),
    soil=(.16,.12,.075),red=(.58,.13,.07),yellow=(.79,.58,.12),blue=(.16,.29,.36))

def manifest(version):
    cams=G.camera_roster(22,16,7.1,[
        ('facade_close',(-6,-14,4),(-6,-6,2.8),38),
        ('architecture_close',(1,-13,2.3),(0,-5,2.0),26),
        ('glass_close',(-6,-9,2),(-6,-3,1.5),26),
        ('roof_contact',(8,-1,11),(6,3,6.3),35),
        ('passage',(0,-5.8,1.8),(0,4,2),20),
        ('courtyard',(15,1,3.2),(10,4,1.5),28),
        ('aisles',(-2,-1,1.8),(6,4,2),22),
        ('checkout',(8,-4.8,1.8),(4,-3.8,1.4),26),
        ('clerestory',(0,0,3.1),(5,4,6.5),22)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}',method=C.METHOD,archetype_id=SLUG,variant_id=SLUG+'-v1',
        representation_kind='architectural_clay',state='prework',keeper_claimed=False,runtime_seed_allowed=False,
        measurement_contract=dict(dimensions_m=dict(width=20.8,depth=14.2,height=7.1),observed_storeys=1,roof_lanterns=4,front_canopy_posts=4,
            inferred='Metric grocery layout original teaching assumption; oblique/top lock four longitudinal glazing strips.'),
        roof_contract=dict(type='continuous gently sloping metal roof with four narrow single-sided clerestory strips',eave_m=EAVE,peak_m=PEAK),
        identity_contract=dict(owner='brick sign fascia; broad transparent shopfront; four-post timber canopy; four parallel roof lanterns'),
        material_contract=dict(profile='source-palette architectural clay with brick courses, metal seams and timber canopy',textured_keeper=False),
        programme_contract=dict(storeys=1,ground='produce, stocked grocery aisles, checkout and rear service bay',roof='clerestory daylight into sales hall'),
        contact_contract=['Supported canopy','Complete roof lantern closures and flashings','Open entry','Clear grocery aisles'],
        runtime_contract=dict(scale='fixed_native_only',review='NOT TESTED'),camera_roster=cams,mandatory_review_views=[c['name'] for c in cams])

def hole(name,u,z,w,h,**kw):return dict(id=name,u=u,z=z,w=w,h=h,**kw)

def build():
    fs=A.faces(W,D)
    C.box('Market slab',(0,0,.075),(W,D,.15),'foundation','foundation',0)
    hs=[hole('Market open entrance',0,.15,2.5,3.2,open=True)]
    for x,w in [(-6.6,5.7),(-2.4,1.8),(2.4,1.8),(6.6,5.7)]:hs.append(hole('Market display window',x,.5,w,3.0,cols=3))
    G.wall(fs[0],W,.15,EAVE,hs,courses=True)
    G.wall(fs[2],W,.15,6.,[hole('Rear service doorway',0,.15,2.5,3,open=True)],courses=True)
    for f in (fs[1],fs[3]):
        hs=[hole('Goods delivery doorway',4,.15,1.5,2.8,open=True)] if f==fs[1] else []
        G.wall(f,D-.56,.15,3.5,hs,courses=True)
        # Opaque timber above lower masonry follows the sloping roof carrier.
        x=9.86 if f==fs[1] else -9.86
        C.prism('Upper timber side wall',[(-5.72,3.5),(5.72,3.5),(5.72,5.984),(-5.72,5.316)],'x',x-.14,x+.14,'timber','upper service elevation')
        for j in range(95):
            y=-5.7+j*.12;z=EAVE+(y+6)/12*.7
            C.box('Timber vertical board joint',(x+(.142 if x>0 else -.142),y,(3.5+z)/2),(.004,.009,z-3.5),'joint','timber joints',0)
    def rz(y):return EAVE+(y+6)/12*.7
    roof=C.solid_surface('Continuous sloping metal carrier',[(-10,-6,rz(-6)),(10,-6,rz(-6)),(10,6,rz(6)),(-10,6,rz(6))],.14,'roof','roof')
    centres=(-6,-2,2,6)
    for x in centres:
        left,right=x-.19,x+.19;y0,y1=-5.8,5.8
        C.cut_box(roof,'Narrow clerestory roof well',(x,0,6),(.30,11.52,3))
        def lz(y):return EAVE+.10+(y-y0)/(y1-y0)*(PEAK-EAVE-.10)
        quad=[(left,y0,lz(y0)),(right,y0,lz(y0)),(right,y1,lz(y1)),(left,y1,lz(y1))]
        C.solid_surface('Standing seam lantern plane',quad,.14,'roof','lantern roof')
        # Edge flashing and real frame posts connect glazing to roof and curb.
        for xx in (left,right):
            C.beam('Lantern sloped flashing',(xx,y0,lz(y0)+.020),(xx,y1,PEAK+.020),.045,.05,'trim','roof flashing')
            C.beam('Lantern bottom curb',(xx,y0,rz(y0)),(xx,y1,rz(y1)),.06,.12,'trim','lantern frame')
        C.prism('Opaque lantern cheek',[(y0,rz(y0)),(y1,rz(y1)),(y1,lz(y1)),(y0,lz(y0))],'x',left-.015,left+.015,'roof','roof closure')
        for i in range(1,15):
            ya=y0+(y1-y0)*(i-1)/14;yb=y0+(y1-y0)*i/14
            G.optical_surface('Single clerestory optical pane',[(right,ya,rz(ya)+.02),(right,yb,rz(yb)+.02),(right,yb,lz(yb)-.03),(right,ya,lz(ya)-.03)],(1,0,0),.012,'clerestory glass')
            if i>1:C.beam('Clerestory vertical mullion',(right,ya,rz(ya)),(right,ya,lz(ya)),.04,.04,'trim','lantern frame')
        for yy in (y0,y1):
            C.box('Lantern end closure',(x,yy,(rz(yy)+lz(yy))/2),(.38,.035,lz(yy)-rz(yy)),'roof','roof closure',0)
    for j in range(42):
        xx=-9.85+j*.48
        if all(abs(xx-x)>.25 for x in centres):C.beam('Physical standing seam',(xx,-6,rz(-6)+.010),(xx,6,rz(6)+.010),.024,.024,'roof','roof seams',0)
    C.box('Timber entrance canopy beam',(0,-7.1,3.75),(20.8,2.2,.25),'timber','canopy',0)
    C.box('Canopy weathering cap',(0,-7.1,3.91),(20.8,2.2,.08),'roof','canopy',0)
    for x in (-9.5,-3.9,3.9,9.5):
        C.box('Canopy seated post',(x,-7.9,1.8125),(.14,.16,3.625),'trim','canopy',0)
    # Produce tables with crates and individual low-poly produce; clear centre entry.
    for x in (-7.3,-3.8):
        C.box('Produce timber display',(x,-3.8,.63),(2.6,1.6,.96),'timber','produce',0)
        for i in range(5):
            for j in range(3):
                C.box('Produce crate',(x-1.0+i*.5,-4.3+j*.5,1.17),(.46,.46,.12),'pale','produce',0)
                for k in range(3):
                    C.box('Produce fruit',(x-1.13+i*.5+k*.12,-4.3+j*.5,1.295),(.10,.16,.13),'red' if i%2 else 'yellow','produce',0)
    for x in (-7.5,-4,4,7.5):
        for z in (.55,1.15,1.75,2.35):
            C.box('Double sided grocery shelf',(x,1.7,z),(1.1,4.7,.10),'timber','aisles',0)
            for y in range(0,4):
                for sign in (-1,1):C.box('Shelf grocery package',(x+sign*.28,y,z+.2),(.42,.65,.30),'blue' if y%3 else 'yellow','stock',0)
        for y in (-.65,4.05):C.box('Shelf end upright',(x,y,1.5),(1.1,.10,2.7),'trim','aisles',0)
    for x in (4.3,7.6):
        C.box('Checkout counter',(x,-3.8,.65),(2.6,1.0,1.0),'timber','checkout',0)
        C.box('Checkout conveyor',(x-.5,-3.8,1.19),(1.3,.76,.08),'hardware','checkout',0)
        C.box('Checkout till screen',(x+.7,-3.85,1.55),(.42,.1,.35),'blue','checkout',0)
        C.box('Checkout till pedestal',(x+.7,-3.85,1.2625),(.09,.09,.225),'hardware','checkout',0)
    # Ceiling structure and pendant fittings seat on the real roof framing.
    for y in (-4,0,4):
        C.beam('Sales hall structural beam',(-9.85,y,rz(y)-.24),(9.85,y,rz(y)-.24),.20,.24,'timber','structure')
        for x in (-6,0,6):
            C.rod('Pendant drop',(x,y,rz(y)-.35),(x,y,3.5),.016,'hardware','lighting',8)
            C.box('Pendant diffuser',(x,y,3.45),(.5,.5,.15),'pale','lighting',0)
            C.qa_room_light('Grocery occupied aisle',(x,y,4.6),260,4)
    # Rear service shelving and goods carts keep service route legible.
    for x in (-6,6):C.box('Back stock cabinet',(x,5.25,1.3),(3,.65,2.3),'pale','service',0)
    # Source receiving corner: bounded timber screen and protected goods door.
    C.box('Receiving service pad',(11.225,4.75,.075),(2.45,5.3,.15),'foundation','service yard',0)
    for y in (2.8,5.2):C.rod('Receiving protective bollard',(10.8,y,.15),(10.8,y,1.25),.085,'yellow','service yard')
    for y in (3.5,5.4,7.3):C.box('Receiving screen post',(12.35,y,1.125),(.10,.10,1.95),'hardware','service yard',0)
    for x in (10.1,11.2):C.box('Receiving rear screen post',(x,7.3,1.125),(.10,.10,1.95),'hardware','service yard',0)
    for i in range(12):
        z=.32+i*.145
        C.box('Receiving side screen slat',(12.35,5.4,z),(.075,3.8,.11),'timber','service yard',0)
        C.box('Receiving rear screen slat',(11.175,7.3,z),(2.35,.075,.11),'timber','service yard',0)
    C.CONTACTS.append(dict(name='Four timber canopy supports',count=4,entry_clear_width_m=2.5))
