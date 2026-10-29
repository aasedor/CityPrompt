"""Hospital v006: bounded canopy-contact correction and building-only site.

The original head recipe and v003 GLB remain unchanged. Exact source views and
all other architectural grammar are inherited from the pinned family recipe.
"""
import family_hospital as previous
from family_hospital import *

def atrium():
    x0, x1, y0, y1 = ATR
    f = C.Face(((x0 + x1) / 2, y0, 0), (1, 0, 0), (0, 1, 0), 'atrium south')
    w = x1 - x0
    xr = x1 - .3                                                       # east return clear of the ward leg's corner column
    ZS = 5.9                                                           # storefront below the canopy line, diagrid net above
    C.box('Atrium south glass', ((x0 + xr) / 2, y0 + .05, (3.0 + ATR_TOP) / 2), (xr - x0 - .1, .03, ATR_TOP - 3.0), 'glass', 'atrium', 0)
    drums = (x0 + 2.2, xr - 2.2)
    edges = [x0 + .05] + [v for d in drums for v in (d - 1.15, d + 1.15)] + [xr - .05]
    for a, c in zip(edges[::2], edges[1::2]):                          # storefront glass between the revolving doors
        if c - a > .2:
            C.box('Atrium storefront glass', ((a + c) / 2, y0 + .05, (G0 + 3.0) / 2), (c - a, .03, 3.0 - G0), 'glass', 'atrium', 0)
    for xx, ye in ((x0 + .05, PB[2]), (xr, LEG[2])):
        C.box('Atrium return glass', (xx, (y0 + ye) / 2, (G0 + ATR_TOP) / 2), (.03, ye - y0, ATR_TOP - G0), 'glass', 'atrium', 0)
        C.box('Atrium return mullion', (xx, (y0 + ye) / 2, (G0 + ATR_TOP) / 2), (.1, .1, ATR_TOP - G0), 'steel', 'atrium', 0)
    C.box('Atrium closer', ((xr + x1) / 2, LEG[2] + .05, (G0 + ATR_TOP) / 2), (x1 - xr, .1, ATR_TOP - G0), 'steel', 'atrium', 0)
    C.OPENINGS.append(dict(id='atrium south glazing', face=f.label, u=0, z=G0, width=w, height=ATR_TOP - G0, kind='glass atrium', clear_wall_cut=True,
        carrier_depth_m=.1, frame_inset_m=0, pane_inset_m=.05, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='atrium hall'))
    b = Batch()
    b.box('steel', x0 + .12, y0 + .1, (G0 + ATR_TOP) / 2, .24, .24, ATR_TOP - G0)
    b.box('steel', xr - .12, y0 + .1, (G0 + ATR_TOP) / 2, .24, .24, ATR_TOP - G0)
    b.box('steel', (x0 + xr) / 2, y0 + .1, ATR_TOP - .1, xr - x0 - .5, .2, .2)        # between the edge posts, set back
    b.box('steel', (x0 + xr) / 2, y0 + .1, ZS, xr - x0 - .5, .2, .2)                   # canopy-line transom under the net
    b.box('steel', (x0 + xr) / 2, y0 + .02, 3.0, xr - x0 - .5, .14, .14)                # door-head transom
    for k in range(1, 6):                                               # straight storefront mullions
        x = x0 + .24 + (xr - x0 - .48) * k / 6
        if all(abs(x - d) > 1.25 for d in drums):
            b.box('steel', x, y0 + .02, (G0 + ZS) / 2, .08, .12, ZS - G0)
    b.flush('atrium frame')
    # Diagonal mullion net on the south glass.
    step = 2.4
    H = ATR_TOP - G0
    w = xr - x0
    mg = .26                                                           # members stop inside the edge posts
    u_of = lambda q: q - (x1 - x0) / 2                                 # net coordinate (0..w from the west post) to face u
    fam = {1: [], -1: []}
    for s in (1, -1):
        c = -H if s > 0 else 0.0
        c_end = w if s > 0 else w + H
        c += step / 2
        while c < c_end:
            lo, hi = (mg - c, w - mg - c) if s > 0 else (c - w + mg, c - mg)
            za, zb = max(ZS - G0 + .1, lo), min(H, hi)
            if zb - za > .15:
                d = -.03 if s > 0 else -.045                             # the two sets interpenetrate as one net
                C.beam('Atrium diagrid', f.p(u_of(c + s * za), d, G0 + za), f.p(u_of(c + s * zb), d, G0 + zb), .08, .08, 'steel', 'atrium')
                fam[s].append(c)
            c += step
    nb = Batch()
    for c1 in fam[1]:
        for c2 in fam[-1]:
            z, q = (c2 - c1) / 2, (c1 + c2) / 2
            if ZS - G0 + .1 < z < H and mg < q < w - mg:
                p = f.p(u_of(q), -.05, G0 + z)
                nb.box('steel', p[0], p[1], p[2], .16, .12, .16)            # node block at each crossing
    nb.flush('atrium diagrid nodes')
    # Glass roof, west glass above the clinical roof, entrance doors, bridges, a glass lift.
    w = x1 - x0
    C.box('Atrium roof glass', ((x0 + x1) / 2, (y0 + y1) / 2, ATR_TOP), (w, y1 - y0 - .02, .06), 'glass', 'atrium', 0)
    for xx in (x0 + .1, x1 - .1):
        C.box('Atrium top edge', (xx, (y0 + y1) / 2, ATR_TOP + .12), (.2, y1 - y0, .24), 'steel', 'atrium', 0)
    for k in range(9):
        C.box('Atrium roof rib', ((x0 + x1) / 2, y0 + (y1 - y0) * k / 8, ATR_TOP + .08), (w + .1, .14, .14), 'steel', 'atrium', 0)
    C.box('Atrium west glass', (x0 + .05, (y0 + y1) / 2, (PB_TOP + ATR_TOP) / 2 + .1), (.03, y1 - y0, ATR_TOP - PB_TOP - .2), 'glass', 'atrium', 0)
    for x in drums:
        C.rod('Revolving door drum', (x, y0 + .05, G0), (x, y0 + .05, 2.8), 1.1, 'glass', 'atrium', 16)      # set in the facade line
        C.rod('Revolving door canopy', (x, y0 + .05, 2.8), (x, y0 + .05, 3.05), 1.2, 'steel', 'atrium', 16)
        C.rod('Revolving door post', (x, y0 + .05, G0), (x, y0 + .05, 2.8), .07, 'steel', 'atrium', 8)
    C.box('Atrium lift', (x0 + 2.0, y1 - 3.0, (G0 + ATR_TOP - 2) / 2), (2.4, 2.4, ATR_TOP - 2 - G0), 'glass', 'atrium', 0)
    C.box('Atrium floor', ((x0 + x1) / 2, (y0 + y1) / 2, G0 / 2), (w, y1 - y0, G0), 'sand', 'atrium', 0)
    for z in (4.0, 14.0, 24.0):
        C.qa_room_light(f'Atrium {z:.0f}', ((x0 + x1) / 2, -10.0, z), 140, 6.0)
    C.box('Reception desk', ((x0 + x1) / 2, -14.0, G0 + .55), (4.0, 1.0, 1.1), 'pale', 'atrium', 0)
    # Entrance canopy: glass on a steel frame in front of the atrium, hung on tension rods, two posts.
    a, c, e, g = 7.0, 27.0, -36.0, -30.4
    C.box('Entrance canopy glass', ((a + c) / 2, (e + g) / 2, 5.6), (c - a, g - e, .06), 'glass', 'entrance canopy', 0)
    for yy in (e, g):
        C.box('Entrance canopy edge', ((a + c) / 2, yy, 5.48), (c - a, .16, .18), 'steel', 'entrance canopy', 0)
    for xx in (a, c):
        C.box('Entrance canopy edge', (xx, (e + g) / 2, 5.48), (.16, g - e - .16, .18), 'steel', 'entrance canopy', 0)
    # v004: plates bear on actual structural posts, not on glazing or cladding.
    # Both canopy ends have a closed clevis tied into the steel edge beam.
    leg_col = (21.0 + (LEG[1] + EXO)) / 2
    anchors = [((x0 + .12, y0 + .1, 14.0), (8.0, 11.5), .24),
               ((xr - .12, y0 + .1, 14.0), (15.0, 18.5), .24),
               ((leg_col, LEG[2] - EXO, BASE_TOP + (BB_TOP - BASE_TOP) / 5), (22.5, 26.0), .45)]
    for (ax, carrier_y, az), xs, carrier_depth in anchors:
        carrier_front = carrier_y - carrier_depth / 2
        plate_y = carrier_front - .04
        clevis_y = plate_y - .15
        C.box('Canopy rod anchor plate', (ax, plate_y, az), (.34, .32, .34), 'steel', 'entrance canopy', 0)
        C.box('Canopy upper clevis', (ax, clevis_y, az), (.16, .20, .18), 'steel', 'entrance canopy', 0)
        for x in xs:
            C.box('Canopy lower clevis', (x, e, 5.59), (.16, .20, .20), 'steel', 'entrance canopy', 0)
            C.rod('Canopy tension rod', (ax, clevis_y - .07, az), (x, e, 5.64), .03, 'steel', 'entrance canopy', 6)
        C.CONTACTS.append(dict(name='Canopy structural anchor', carrier_center=[ax, carrier_y, az],
            carrier_depth_m=carrier_depth, plate_center=[ax, plate_y, az], plate_size_m=[.34,.32,.34],
            upper_clevis_center=[ax,clevis_y,az], lower_steel_beam_y=e, lower_steel_beam_top=5.57))
    for x in (9.0, 25.0):
        C.rod('Canopy post', (x, e + .6, .14), (x, e + .6, 5.4), .12, 'steel', 'entrance canopy', 10)
    C.CONTACTS.append(dict(name='Atrium between the clinical block and the ward leg; entrance canopy on rods and two posts', atrium=list(ATR)))


def circulation():
    """Visible connected clay circulation programme; no code-compliance claim."""
    levels = [G0, 5., 9., 13., 17., 21., 25., 29.]
    xa, xb, ya, yb = 15., 17.1, -25., -20.5
    width = 1.55
    def flight(name, x, ystart, yend, lower, upper):
        count = math.ceil((upper-lower)/.175)
        pts=[(ystart,lower)]
        for k in range(count):
            y0=ystart+(yend-ystart)*k/count; y1=ystart+(yend-ystart)*(k+1)/count
            z=lower+(upper-lower)*(k+1)/count
            pts.extend([(y0,z),(y1,z)])
        pts.extend([(yend,upper-.18),(ystart,max(0.,lower-.18))])
        C.prism(name,pts,'x',x-width/2,x+width/2,'pale','atrium circulation')
        for xx in (x-width/2+.04,x+width/2-.04):
            C.beam(name+' handrail',(xx,ystart,lower+1.),(xx,yend,upper+1.),.05,.05,'steel','atrium circulation')
            for k in range(0,count,3):
                yy=ystart+(yend-ystart)*(k+.5)/count; zz=lower+(upper-lower)*(k+1)/count
                C.box(name+' baluster',(xx,yy,zz+.5),(.04,.04,1.),'steel','atrium circulation',0)
    for idx,(lower,upper) in enumerate(zip(levels,levels[1:])):
        mid=(lower+upper)/2
        flight(f'Atrium up {idx}',xa,ya,yb,lower,mid)
        flight(f'Atrium return {idx}',xb,yb,ya,mid,upper)
        C.box('Atrium half landing',((xa+xb)/2,yb+.7,mid-.1),(xb-xa+width,1.4,.2),'pale','atrium circulation',0)
        C.railing('Mid landing rear guard',(xa-width/2,yb+1.35,mid),(xb+width/2,yb+1.35,mid),height=1.05,spacing=.25,role='steel')
        # Full landings join both clinical and ward floor edges; terminals are cut through real carriers below.
        C.box('Connected atrium gallery',(17.,ya-.8,upper-.12),(8.5,1.6,.24),'concrete','atrium circulation',0)
        C.railing('Gallery front guard',(13.1,ya-1.57,upper),(20.9,ya-1.57,upper),height=1.05,spacing=.25,role='steel')
        C.qa_room_light('Gallery fill '+str(idx),(17.,ya-2.,upper+2.),220,3.)
        for xx,tag in ((13.,'clinical east'),(21.,'ward leg west')):
            if xx==13. and upper>=PB_TOP: continue
            carriers=[o for o in C.objects() if o.type=='MESH' and tag in o.name]
            for obj in carriers:
                C.cut_box(obj,'Connected gallery portal',(xx,ya-.8,upper+1.35),(1.2,1.6,2.7))
        C.CONTACTS.append(dict(name='Atrium connected gallery and switchback stair',floor_m=upper,
            landing_x=[12.75,21.25],landing_y=[ya-1.6,ya],portal_y=ya-.8,portal_height_m=2.7))
    C.qa_room_light('Reception neutral fill',(17.,-15.,4.),350,5.)


def site():
    # A compact entrance approach only; no surrounding roads or block-wide pad.
    C.box('Entrance approach', (17.0, -33.2, .07), (20.2, 6.4, .14), 'concrete', 'entrance approach', 0)


def build():
    site()
    clinical_block()
    ward_block()
    atrium()
    circulation()
    C.CONTACTS.append(dict(name='Building-only hospital; compact entry approach, no roads', plan=[PB, LEG, BAR, ATR]))


def manifest(version):
    if version != 6:
        raise ValueError('This bounded corrected recipe only authors hospital v006.')
    result = previous.manifest(version)
    result['correction_contract'] = dict(previous_candidate='clay-braced-frame-hospital-clay-v003',
        scope='Canopy rods attach through bearing plates and clevises to real steel posts; lower ends bear on steel canopy edge; no surrounding streets.',
        original_glb_changed=False, context_roads_included=False, visible_atrium_circulation=True)
    extra = [
        ('canopy_west_anchor', (11.3,-34.3,15.1), (13.12,-30.06,14.0),55),
        ('canopy_east_anchor', (18.7,-34.1,15.2), (20.58,-30.06,14.0),55),
        ('canopy_ward_anchor', (24.6,-32.2,15.6), (26.55,-28.365,14.6),55),
        ('canopy_front_anchors', (17.0,-66.0,14.0), (17.0,-36.0,5.6),45),
    ]
    for camera in result['camera_roster']:
        if camera['name']=='interior':
            camera.update(location=(19.4,-29.,2.1),target=(15.9,-23.,5.1),lens=22)
    result['camera_roster'] += [dict(name=name,location=location,target=target,lens=lens,whole=False)
                               for name,location,target,lens in extra]
    result['mandatory_review_views'] = [c['name'] for c in result['camera_roster']]
    result['measurement_contract']['dimensions_m']['depth'] = 63.0
    return result
