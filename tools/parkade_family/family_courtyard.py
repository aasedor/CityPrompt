"""Mobility Courtyard: fixed original ring parkade and inhabited mobility edge.

Composition extends the shared audited frame. No scaling or scene publication.
"""
import math

COURTYARD = (-8., 8., -7., 7.)
CAFE = (-12., 0., -24., -17.5)
BIKE_HUB = (3., 18., -24., -17.5)
SOIL_WELLS = [(a,b,c,d) for a,b in ((-6.9,-2.),(2.,6.9))
              for c,d in ((-5.9,-2.),(2.,5.9))]
FRONT_SCREEN_BAYS = ((-19,-13),(-11,-5),(-3,3),(5,11),(13,19),(21,26))
SCREEN_ROLES = ('screen_teal','screen_terracotta','screen_ochre')
PALETTE = dict(screen_teal=(.035,.30,.31), screen_terracotta=(.60,.23,.12),
               screen_ochre=(.68,.43,.09))
SPEC = dict(key='courtyard',slug='parkade-mobility-courtyard',label='Mobility Courtyard Parkade',
    width=64,depth=48,levels=4,courtyard=COURTYARD,
    marking_exclusions=[CAFE,BIKE_HUB],
    description='Open central planted court, permeable coloured fins, street cafe and open bicycle hub; fixed native original design.')


def court_paving_panels():
    """Partition the ground court around actual root openings, with no backing slab."""
    xs=(-8.,-6.9,-2.,2.,6.9,8.)
    ys=(-7.,-5.9,-2.,2.,5.9,7.)
    return [(a,b,c,d) for a,b in zip(xs,xs[1:]) for c,d in zip(ys,ys[1:])
            if not any(x0<(a+b)/2<x1 and y0<(c+d)/2<y1 for x0,x1,y0,y1 in SOIL_WELLS)]


def front_fins():
    return [(a+i*.7,SCREEN_ROLES[index%3])
            for index,(a,b) in enumerate(FRONT_SCREEN_BAYS) for i in range(int((b-a)/.7)+1)]


def extra_geometry(ctx):
    import clay_core as C
    z0=ctx['datums'][0]
    top=ctx['datums'][-1]
    assert (ctx['width'],ctx['depth'],ctx['levels']) == (64,48,4), 'Fixed native courtyard assembly only'
    assert abs(z0-.15)<1e-6 and abs(top-10.05)<1e-6

    def box(name,loc,size,role='steel',module='courtyard detail'):
        return C.box(name,loc,size,role,module,0)

    def plate(name,rect,z,thickness=.15,role='deck',module='courtyard ground'):
        a,b,c,d=rect
        return box(name,((a+b)/2,(c+d)/2,z-thickness/2),(b-a,d-c,thickness),role,module)

    def guard(name,a,b):
        for h in (.32,.68,1.1):
            C.beam(name+' horizontal rail',(a[0],a[1],a[2]+h),(b[0],b[1],b[2]+h),.045,.045,'steel','courtyard guards')
        n=math.ceil(math.dist(a,b)/1.5)
        for i in range(n+1):
            p=tuple(a[j]+(b[j]-a[j])*i/n for j in range(3))
            C.beam(name+' seated post',p,(p[0],p[1],p[2]+1.1),.055,.055,'steel','courtyard guards')

    # Whole court topology: the shared frame removes slabs, beams and columns
    # inside this opening. The court carries only ground paths and exposed beds.
    for rect in court_paving_panels():plate('Courtyard ground path with real root opening',rect,z0)
    for rect in SOIL_WELLS:
        plate('Exposed soil root well',rect,z0,.15,'soil','courtyard planting')
        a,b,c,d=rect;x=(a+b)/2;y=(c+d)/2
        C.rod('Tree trunk rooted in soil',(x,y,.12),(x,y,2.55),.10,'timber','courtyard planting',8)
        for dx,dy in ((-.65,-.4),(.65,.35),(-.2,.65)):
            C.rod('Supported tree branch',(x,y,1.75),(x+dx,y+dy,2.8),.045,'timber','courtyard planting',7)
        # Low-poly ellipsoidal crowns, kept fully inside each soil well.
        vertices=[(x,y,4.25)]
        for r,z in ((.75,3.95),(1.25,3.3),(1.15,2.65),(.55,2.3)):
            vertices.extend((x+r*math.cos(i*math.tau/8),y+r*.83*math.sin(i*math.tau/8),z) for i in range(8))
        vertices.append((x,y,2.15))
        faces=[(0,1+i,1+(i+1)%8) for i in range(8)]
        faces.extend((1+j*8+i,1+j*8+(i+1)%8,1+(j+1)*8+(i+1)%8,1+(j+1)*8+i) for j in range(3) for i in range(8))
        faces.extend((33,25+(i+1)%8,25+i) for i in range(8))
        C.mesh('Tree crown above rooted open soil',vertices,faces,'foliage','courtyard planting')
    for x in (-8.25,8.25):
        for y in (-7.25,7.25):
            box('Court corner ground-bearing column',(x,y,(top+z0)/2),(.5,.5,top-z0),'concrete','courtyard frame')
    for z in ctx['datums'][1:]:
        for y in (-7.25,7.25):box('Court edge beam outside aperture',(0,y,z-.32),(17,.5,.5),'concrete','courtyard frame')
        for x in (-8.25,8.25):box('Court side beam outside aperture',(x,0,z-.32),(.5,14,.5),'concrete','courtyard frame')
        for y in (-7.15,7.15):guard('Court transverse open guard',(-8.15,y,z),(8.15,y,z))
        for x in (-8.15,8.15):guard('Court longitudinal open guard',(x,-7.15,z),(x,7.15,z))

    # Physical fins, attached at both ends to continuous supporting rails.
    for z in ctx['datums'][1:]:
        h=1.6 if z==top else 2.45
        for a,b in FRONT_SCREEN_BAYS:
            for zz in (z+.18,z+h):box('Screen front carrier',( (a+b)/2,-23.74,zz),(b-a+.2,.12,.10),'steel','coloured ventilation screens')
        for x,role in front_fins():
            box('Permeable front coloured fin',(x,-23.74,z+(.18+h)/2),(.15,.36,h-.18),role,'coloured ventilation screens')
        for side in (-1,1):
            for zz in (z+.18,z+h):box('Side screen carrier',(side*31.8,2.6,zz),(.12,25.4,.10),'steel','coloured ventilation screens')
            for i in range(37):
                y=-10+i*.7
                box('Permeable side coloured fin',(side*31.8,y,z+(.18+h)/2),(.36,.15,h-.18),SCREEN_ROLES[(i//9)%3],'coloured ventilation screens')

    # Cafe uses the actual deck as floor and next deck as weather enclosure.
    # Frame columns x=-12,-6,0 divide glazing; opaque owners never back panes.
    for x in (-11.88,-.12):box('Cafe side enclosed wall',(x,-20.75,1.475),(.24,6.5,2.65),'concrete','cafe room')
    box('Cafe rear enclosed wall',(-6,-17.62,1.475),(11.76,.24,2.65),'concrete','cafe room')
    for x in (-11.88,-.12):box('Cafe side closure to deck soffit',(x,-20.75,3.0),(.24,6.5,.4),'concrete','cafe room')
    box('Cafe rear closure to deck soffit',(-6,-17.62,3.0),(11.76,.24,.4),'concrete','cafe room')
    box('Cafe storefront head to frame soffit',(-6,-23.75,2.85),(11.76,.24,.10),'steel','cafe room')
    # At the front only the piers and frames own the carrier. Open door stays empty.
    glass_segments=((-11.75,-6.25),(-5.75,-2.2),(-.6,-.25))
    for a,b in glass_segments:
        box('Cafe recessed optical storefront',((a+b)/2,-23.77,1.475),(b-a-.08,.012,2.57),'glass','cafe glazing')
        for x in (a+.02,b-.02):box('Cafe storefront jamb',(x,-23.83,1.475),(.04,.10,2.65),'steel','cafe glazing')
        for z in (.19,2.76):box('Cafe storefront rail',((a+b)/2,-23.83,z),(b-a,.10,.08),'steel','cafe glazing')
    for x in (-2.2,-.6):box('Cafe open doorway reveal',(x,-23.83,1.475),(.065,.20,2.65),'steel','cafe glazing')
    box('Cafe open doorway head',(-1.4,-23.83,2.765),(1.6,.20,.07),'steel','cafe glazing')
    # Pane-free entrance keeps at least 1.53m clear to the occupied room.
    C.OPENINGS.append(dict(id='courtyard-cafe-open-door',kind='open public doorway',face='front',
        u=0,z=z0,width=1.535,height=2.58,clear_wall_cut=True,carrier_depth_m=.24,
        face_origin=[-1.4,-23.83,0],face_tangent=[1,0,0],face_inward=[0,1,0]))
    box('Cafe slender canopy',(-6,-23.48,2.96),(12,1.04,.18),'steel','cafe room')
    box('Cafe service counter body',(-6,-18.9,.66),(7.2,.8,1.02),'timber','cafe furniture')
    box('Cafe service counter top',(-6,-18.9,1.22),(7.4,.95,.10),'steel','cafe furniture')
    box('Cafe espresso machine body',(-4.5,-18.9,1.5),(.9,.50,.48),'steel','cafe furniture')
    for x in (-4.8,-4.2):C.rod('Cafe espresso portafilter',(x,-19.16,1.4),(x,-19.4,1.4),.035,'steel','cafe furniture',8)
    for x in (-9,-5):
        box('Cafe table top',(x,-21.7,.88),(1.2,.9,.10),'timber','cafe furniture')
        C.rod('Cafe table pedestal',(x,-21.7,z0),(x,-21.7,.83),.065,'steel','cafe furniture',8)
        for y in (-22.65,-20.75):
            box('Cafe chair seat',(x,y,.61),(.48,.48,.07),'timber','cafe furniture')
            box('Cafe chair back',(x,y+(.21 if y>-21.7 else -.21),.89),(.48,.06,.55),'timber','cafe furniture')
            for dx in (-.18,.18):
                for dy in (-.18,.18):box('Cafe chair grounded leg',(x+dx,y+dy,.37),(.035,.035,.44),'steel','cafe furniture')

    # Bicycle hub stays open on the street and rear: no decorative false room.
    for x in (3.15,17.85):
        for y in (-23.8,-17.7):box('Bicycle canopy seated post',(x,y,1.5),(.16,.16,2.7),'steel','bicycle hub')
    plate('Bicycle hub shelter roof',(3,18,-24,-17.5),3.12,.27,'steel','bicycle hub')
    for x in (5,7,9,11,13,15,17):
        points=[(x-.45,-22.5,z0),(x-.45,-22.5,.75)]
        points.extend((x+.45*math.cos(math.pi-i*math.pi/6),-22.5,.75+.45*math.sin(math.pi-i*math.pi/6)) for i in range(7))
        points.extend([(x+.45,-22.5,z0)])
        for a,b in zip(points,points[1:]):
            if math.dist(a,b)>1e-5:C.rod('Grounded inverted U cycle hoop',a,b,.035,'steel','bicycle hub',8)
    for x in (5,9,13):
        # Recognisable two-wheel bicycle with actual triangular frame, saddle,
        # handlebar and spokes; parked beside its corresponding ground hoop.
        y=-22.25;r=.34;wheelz=z0+r
        for wx in (x-.65,x+.65):
            pts=[(wx+r*math.cos(i*math.tau/12),y,wheelz+r*math.sin(i*math.tau/12)) for i in range(12)]
            for a,b in zip(pts,pts[1:]+pts[:1]):C.rod('Bicycle open wheel tyre',a,b,.026,'steel','parked bicycles',6)
            for i in (0,3,6,9):C.rod('Bicycle wheel spoke',(wx,y,wheelz),pts[i],.009,'steel','parked bicycles',5)
        rear=(x-.65,y,wheelz);front=(x+.65,y,wheelz);crank=(x-.05,y,wheelz-.05)
        saddle=(x-.25,y,1.02);head=(x+.38,y,1.02)
        for a,b in ((rear,crank),(rear,saddle),(saddle,crank),(saddle,head),(head,crank),(head,front)):
            C.rod('Bicycle physical triangle frame',a,b,.022,'screen_teal','parked bicycles',6)
        box('Bicycle saddle',(x-.27,y,1.08),(.25,.13,.055),'steel','parked bicycles')
        C.rod('Bicycle handlebar stem',head,(x+.4,y,1.2),.018,'steel','parked bicycles',6)
        C.rod('Bicycle handlebar',(x+.4,y-.2,1.2),(x+.4,y+.2,1.2),.018,'steel','parked bicycles',6)
