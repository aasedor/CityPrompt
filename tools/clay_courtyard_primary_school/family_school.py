"""Courtyard primary school with hall block, authored from the locked catalogue views of
ecole_republicaine / variant_3 (catalogue label 'Art Deco School'; the locked pixels show a
contemporary brick courtyard school and govern).

Read from the pixels: a mid-block corner site with party walls to the west and north; a
two-storey brick U around a south-facing playground; a two-storey hall block at the north
with a paved roof terrace, and a corten-clad third storey over the north-west block; a
south-east entrance block whose ground floor is an open concrete-framed passage under a
corten canopy that also roofs the east edge of the playground; strip windows with coloured
fins, full-height classroom glazing to the court, gravel roofs with perimeter rails, a
street fence with a gate, benches and a play structure.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G
from contract import subtract_openings

SLUG = 'clay-courtyard-primary-school'
SX0, SX1, SY0, SY1 = -20.0, 20.0, -23.0, 23.0     # site
T = .30
G0, U, ROOF, CROWN = .15, 4.00, 7.80, 8.30
P_ROOF, P_CROWN = 11.40, 11.90                    # corten third storey
CANOPY = 4.00
# Two-storey blocks (x0, x1, y0, y1)
NW = (-20.0, -3.0, -4.5, 23.0)      # north-west block carrying the corten storey on its north part
WW = (-20.0, -8.0, -23.0, -4.5)     # west wing
NB = (-3.0, 20.0, -4.5, 17.0)       # north hall block with the roof terrace
SE = (11.0, 20.0, -23.0, -4.5)      # east wing / entrance block, to the street line
PENT = (NW[0] + T + .4, NW[1] - T - .4, 0.4, NW[3] - T - .4)   # corten third storey
CX0, CX1, CY0, CY1 = -8.0, 11.0, -23.0, -4.5     # courtyard
EPS = .002
PALETTE = dict(wall=(.52, .36, .24), joint=(.38, .25, .16), trim=(.16, .11, .07),
    pale=(.58, .57, .54), stone=(.52, .51, .48), roof=(.52, .48, .42), sand=(.60, .58, .54),
    foundation=(.34, .34, .33), glass=(.50, .55, .54), hardware=(.09, .09, .095),
    interior=(.74, .70, .60), floor=(.42, .42, .40), timber=(.45, .32, .20), blue=(.14, .22, .28),
    planting=(.24, .42, .14), soil=(.19, .14, .08), corten=(.48, .22, .09), membrane=(.60, .59, .56),
    fin_red=(.70, .18, .14), fin_yellow=(.85, .68, .16), fin_green=(.36, .56, .20), fin_teal=(.14, .48, .50),
    court=(.16, .16, .17), play=(.26, .46, .18))


def manifest(version):
    h = P_CROWN + 1.1
    cams = G.camera_roster(SX1 - SX0, SY1 - SY0, h, [
        ('facade_close', (6.0, -40.0, 4.0), (10.0, SY0, 4.0), 45),
        ('architecture_close', (30.0, -34.0, 9.0), (16.0, SY0, 7.8), 50),
        ('glass_close', (26.0, -8.0, 2.4), (SX1, -1.0, 2.6), 50),
        ('entrance_passage', (22.0, -36.0, 2.0), (15.5, SY0, 2.2), 40),
        ('courtyard', (2.0, -36.0, 6.0), (0.0, -8.0, 3.5), 40),
        ('fins_close', (-4.0, -20.0, 6.0), (-8.0, -11.0, 5.8), 40),
        ('canopy_contact', (14.0, -34.0, 5.5), (8.0, -20.0, 4.0), 40),
        ('penthouse_terrace', (-30.0, -26.0, 20.0), (-6.0, 8.0, 10.0), 45),
        ('interior', (-2.0, -14.0, 2.4), (-8.0, -14.0, 2.0), 30),
        ('playground', (-6.0, -32.0, 3.2), (0.0, -14.0, 1.2), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='ecole_republicaine/variant_3 (ecole-republicaine-art-deco)',
        measurement_contract=dict(dimensions_m=dict(width=SX1 - SX0, depth=SY1 - SY0, height=h),
            observed_storeys=3, storey_programme='two-storey brick U with a third corten storey over the north-west block; fixed authored assembly',
            plan='mid-block corner site 570 x 650 px in the top view read as 40 x 46 m; party walls west and north; courtyard 210 x 260 px opening south',
            blocks=dict(north_west=NW, west_wing=WW, north_hall=NB, entrance_block=SE, courtyard=[CX0, CX1, CY0, CY1]),
            levels_m=[G0, U], roof_m=ROOF, parapet_m=CROWN - ROOF, penthouse_roof_m=P_ROOF, canopy_m=CANOPY,
            street_faces='brick with a concrete band at the first floor and at the parapet; ground large windows; upper strip windows with coloured fins',
            court_faces='full-height classroom glazing on the ground floor, strip windows with coloured fins above',
            entrance='open concrete-framed passage at the south-east corner under a corten canopy that continues over the east edge of the playground',
            roofs='gravel with perimeter rails on the wings; paved terrace on the hall block with a gravel panel at the north-east; corten storey with its own gravel roof',
            inferred='40 m street frontage calibrates the plan; the party walls are blank; interiors (classrooms, hall) are teaching assumptions; the catalogue label (Art Deco) conflicts with the pixels and the pixels govern.'),
        roof_contract=dict(type='flat gravel and paved roofs behind 0.5 m concrete parapets; corten third storey; corten canopy slab', datum_m=ROOF, crowns_m=[CROWN, P_CROWN]),
        identity_contract=dict(owner='brick U around a south playground, coloured window fins, corten third storey and corner canopy, open concrete entrance passage, street fence'),
        material_contract=dict(profile='source-palette clay: warm orange brick with recessed courses, pale concrete bands and columns, corten cladding, dark timber window frames, coloured fins, dark rubber court with a green play panel, gravel and paved roofs', textured_keeper=False),
        programme_contract=dict(storeys=3, ground='classrooms around the court, hall in the north block, entrance passage', upper='classrooms and offices', penthouse='staff room with terrace'),
        contact_contract=['Grade-zero slab and court', 'Entrance passage open at grade with concrete columns', 'Canopy slab bearing on the entrance block and on columns at the court', 'Corten storey seated on the north-west roof slab inside its parapet', 'Rail posts seated on copings', 'Fence on a concrete kerb with a gate'],
        runtime_contract=dict(scale='fixed_native_only', installation='not installed', review='NOT TESTED'),
        camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])


FIN_COLOURS = ['fin_red', 'fin_yellow', 'fin_green', 'fin_teal']
FLOORS = {}


def hole(name, u, z, w, h, **kw):
    return dict(id=name, u=u, z=z, w=w, h=h, **kw)


def lined(f, h, inset=.14, role='trim'):
    d = inset / 2 + .005
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    for s in (-1, 1):
        f.part('Reveal jamb liner', u + s * (w / 2 - .011), d, z + hh / 2, .022, inset + .01, hh, role, 'reveals', 0)
    f.part('Reveal head liner', u, d, z + hh - .011, w, inset + .01, .022, role, 'reveals', 0)
    f.part('Reveal sill liner', u, d, z + .011, w, inset + .01, .022, role, 'reveals', 0)


def strip_window(f, h, fins=True, cols=4):
    """Upper strip window with coloured fins between the lights, concrete sill."""
    f.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=cols, rows=1, frame='trim', depth=T, sill=False)
    lined(f, h)
    f.part('Concrete sill', h['u'], -.04, h['z'] - .05, h['w'] + .20, .26, .10, 'pale', 'window surrounds', 0)
    if fins:
        for i in range(1, cols):
            u = h['u'] - h['w'] / 2 + i * h['w'] / cols
            f.part('Coloured fin', u, -.18, h['z'] + h['h'] / 2, .12, .38, h['h'] + .02, FIN_COLOURS[(i + int(h['u'])) % 4], 'coloured fins', 0)


def classroom_glazing(f, h, cols=4):
    f.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=cols, rows=2, frame='trim', depth=T, sill=False, curtain=False)
    lined(f, h)


def brick(f, lo, hi, z0, z1, holes):
    G.brick_courses(f, lo, hi, z0, z1, holes, spacing=.30)


def bands(f, lo, hi):
    """Concrete first-floor band and parapet fascia (the parapet itself) on street and court elevations."""
    f.part('Floor band', (lo + hi) / 2, .09, U - .02, hi - lo - 2 * EPS, .30, .36, 'pale', 'concrete bands', 0)
    f.part('Parapet fascia', (lo + hi) / 2, .12, ROOF + .25, hi - lo - 2 * EPS, .36, .50, 'pale', 'concrete bands', 0)


def upstand(f, lo, hi):
    f.part('Brick parapet upstand', (lo + hi) / 2, T / 2, ROOF + .25, hi - lo, T, .50, 'wall', 'parapet', 0)


def elevation(face, lo, hi, ground, upper, blank=False, court=False):
    """One brick elevation between lo and hi (face u), two storeys, with its openings."""
    holes = ground + upper
    face.wall(face.label + f' carrier {lo:+.0f}', lo, hi, G0, ROOF, depth=T, holes=holes)
    if blank:
        brick(face, lo, hi, G0, ROOF, holes)
        upstand(face, lo, hi)
        return
    brick(face, lo, hi, G0, U - .20, ground)
    brick(face, lo, hi, U + .16, ROOF, upper)
    for h in ground:
        if h.get('kind') == 'door':
            face.door(h['id'], h['u'], h['z'], h['w'], h['h'], role='timber', panels=2, panel_cols=2); lined(face, h, inset=.19)
        elif h.get('kind') == 'passage':
            lined(face, h, inset=T, role='pale')
            C.OPENINGS.append(dict(id=h['id'], face=face.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='open passage', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None, face_origin=list(face.o), face_tangent=list(face.t), face_inward=list(face.n), occupied_space='open entrance passage'))
        else:
            classroom_glazing(face, h, cols=h.get('cols', 4))
    for h in upper:
        strip_window(face, h, fins=h.get('fins', True), cols=h.get('cols', 4))
    bands(face, lo, hi)


def block_faces(x0, x1, y0, y1, label):
    return dict(south=C.Face(((x0 + x1) / 2, y0, 0), (1, 0, 0), (0, 1, 0), label + ' south'),
                east=C.Face((x1, (y0 + y1) / 2, 0), (0, 1, 0), (-1, 0, 0), label + ' east'),
                north=C.Face(((x0 + x1) / 2, y1, 0), (-1, 0, 0), (0, -1, 0), label + ' north'),
                west=C.Face((x0, (y0 + y1) / 2, 0), (0, -1, 0), (1, 0, 0), label + ' west'))


def wing_roof(x0, x1, y0, y1, gravel=True, crown=CROWN, roof=ROOF, rail=True, name='Roof'):
    """Roof slab tiling the block footprint (1 cm inside its edges so outer faces stay inside the carriers)."""
    C.box(name + ' slab', ((x0 + x1) / 2, (y0 + y1) / 2, roof - .12), (x1 - x0 - .02, y1 - y0 - .02, .24), 'floor', 'roof', 0)
    C.box(name + (' gravel' if gravel else ' paving'), ((x0 + x1) / 2, (y0 + y1) / 2, roof + .02), (x1 - x0 - 2 * T - .02, y1 - y0 - 2 * T - .02, .04), 'roof' if gravel else 'membrane', 'roof', 0)


def edge(a, b, crown, rail=True, name='Coping'):
    """Coping box along a parapet run (centre line a->b) and a guard rail inset 0.3 m from both ends."""
    ax, ay = a; bx, by = b
    if abs(bx - ax) > abs(by - ay):
        C.box(name, ((ax + bx) / 2, ay, crown + .03), (abs(bx - ax), T + .06, .06), 'pale', 'coping', 0)
        ra, rb = (min(ax, bx) + .3, ay, crown + .06), (max(ax, bx) - .3, ay, crown + .06)
    else:
        C.box(name, (ax, (ay + by) / 2, crown + .03), (T + .06, abs(by - ay) - .064, .06), 'pale', 'coping', 0)
        ra, rb = (ax, min(ay, by) + .3, crown + .06), (ax, max(ay, by) - .3, crown + .06)
    if rail:
        C.railing(name + ' rail', ra, rb, height=1.0, spacing=1.0, role='hardware', bottom=.05)


def blocks():
    """Carriers for the four two-storey blocks; faces that abut another block are not built."""
    # North-west block: party walls west and north; east face exposed only above the hall block (y 17..23); south face onto the court for x -8..-3.
    F = block_faces(*NW, 'nw')
    dy = (NW[3] - NW[2]) / 2
    elevation(F['west'], -dy + T, dy, [], [], blank=True)      # u = -y: south end (u = dy) flush into the west-wing party wall
    elevation(F['north'], -(NW[1] - NW[0]) / 2, (NW[1] - NW[0]) / 2, [], [], blank=True)
    ex = F['east']   # u = y - 9.25
    lo, hi = 17.0 - 9.25 + EPS, dy - T
    elevation(ex, lo, hi, [hole('NW east ground window', (lo + hi) / 2, 1.0, 3.2, 2.4, cols=3)], [hole('NW east strip', (lo + hi) / 2, U + 1.1, 4.0, 1.9, cols=3, fins=False)])
    sf = F['south']  # u = x + 11.5; court-facing for x -8..-3 -> u 3.5..8.5
    elevation(sf, CX0 + 11.5 + EPS, 8.5, [hole('NW court glazing', 6.0, G0, 3.8, U - .45, cols=3)], [hole('NW court strip', 6.0, U + 1.1, 3.8, 1.9, cols=3)], court=True)
    # West wing: party wall west; street face south; court face east.
    F = block_faces(*WW, 'ww')
    dy = (WW[3] - WW[2]) / 2
    elevation(F['west'], -dy, dy - T, [], [], blank=True)      # u = -y: north end (u = -dy) flush into the NW party wall
    gs = [hole(f'West wing south ground window {i}', u, .9, 2.6, 2.6, cols=3) for i, u in enumerate((-3.6, 0.0, 3.6))]
    us = [hole('West wing south strip', 0.0, U + 1.1, 8.0, 1.9)]
    elevation(F['south'], -(WW[1] - WW[0]) / 2, (WW[1] - WW[0]) / 2, gs, us)
    ce = F['east']   # u = y + 13.75
    gc = [hole(f'West wing court glazing {i}', u, G0, 5.2, U - .45, cols=4) for i, u in enumerate((-6.5, -.5, 5.5))]
    uc = [hole(f'West wing court strip {i}', u, U + 1.1, 5.2, 1.9) for i, u in enumerate((-6.5, -.5, 5.5))]
    elevation(ce, -dy + T, dy, gc, uc, court=True)
    # North hall block: north face blank; east face to the street; south face to the court for x -3..11.
    F = block_faces(*NB, 'nb')
    dy = (NB[3] - NB[2]) / 2
    elevation(F['north'], -(NB[1] - NB[0]) / 2, (NB[1] - NB[0]) / 2, [], [], blank=True)
    ge = [hole(f'Hall east ground window {i}', u, .9, 4.2, 2.6) for i, u in enumerate((-7.0, -1.0, 5.0))]
    ue = [hole(f'Hall east strip {i}', u, U + 1.1, 6.0, 1.9) for i, u in enumerate((-6.5, 0.5, 7.5))]
    elevation(F['east'], -dy, dy - T, ge, ue)                 # u = y: south end (u = -dy) flush into the entrance block
    sf = F['south']   # u = x - 8.5; court-facing for x -3..11 -> u -11.5..2.5
    gcs = [hole(f'Hall court glazing {i}', u - 8.5, G0, 5.2, U - .45, cols=4) for i, u in enumerate((0.0, 6.5))]
    ucs = [hole(f'Hall court strip {i}', u - 8.5, U + 1.1, 5.2, 1.9) for i, u in enumerate((0.0, 6.5))]
    elevation(sf, -(NB[1] - NB[0]) / 2 + EPS, CX1 - 8.5 - EPS, gcs, ucs, court=True)
    # Entrance block: street faces south and east; court face west with a side opening into the passage.
    F = block_faces(*SE, 'se')
    dy = (SE[3] - SE[2]) / 2
    elevation(F['south'], -(SE[1] - SE[0]) / 2, (SE[1] - SE[0]) / 2, [hole('Entrance passage south', -1.6, G0, 3.6, U - .45, kind='passage'), hole('Entrance block south window', 2.6, .9, 2.4, 2.6, cols=2)], [hole('Entrance block south strip', 0.0, U + 1.1, 6.6, 1.9)])
    elevation(F['east'], -dy + T, dy, [hole(f'Entrance block east ground window {i}', u, .9, 3.0, 2.6, cols=3) for i, u in enumerate((-6.0, 0.0, 6.0))], [hole(f'Entrance block east strip {i}', u, U + 1.1, 5.0, 1.9) for i, u in enumerate((-5.5, 1.0, 7.0))])
    elevation(F['west'], -dy + T, dy, [hole('Entrance block court window', -4.0, .9, 3.0, 2.6, cols=3), hole('Entrance block court door', 2.0, G0, 1.6, 2.6, kind='door'), hole('Entrance block court window 2', 6.5, .9, 3.0, 2.6, cols=3)], [hole(f'Entrance block court strip {i}', u, U + 1.1, 5.0, 1.9) for i, u in enumerate((-5.5, 1.0, 7.0))])


def passage_and_canopy():
    """Open concrete-framed entrance passage at the south-east corner; corten canopy over it and the court's east edge."""
    x0, x1, y0, y1 = SE
    # The passage occupies the south 6.4 m of the entrance block ground floor between concrete columns; the doors sit at its north end.
    for xx in (x0 + .75, x0 + 5.05):
        C.box('Passage concrete column', (xx, y0 + .45, (G0 + U + .05) / 2), (.70, .60, U + .05 - G0), 'pale', 'entrance passage', 0)
    C.box('Passage concrete beam', (x0 + 2.9, y0 + .45, U - .22), (5.0, .60, .36), 'pale', 'entrance passage', 0)
    f = C.Face((x0 + 2.9, y0 + 3.6, 0), (1, 0, 0), (0, 1, 0), 'passage doors')
    dh = hole('Entrance doors', 0.0, G0, 2.4, 2.8)
    f.wall('Passage rear carrier', -1.8, 1.8, G0, U - .25, depth=.25, holes=[dh])
    f.door(dh['id'], dh['u'], dh['z'], dh['w'], dh['h'], role='timber', panels=2, panel_cols=2, inset=.12); lined(f, dh, inset=.12)
    for xx in (x0 + 1.1 - .125, x0 + 4.7 + .125):
        C.box('Passage side wall', (xx, y0 + T + 1.65, (G0 + U - .25) / 2), (.25, 3.3, U - .25 - G0), 'wall', 'entrance passage', 0)
    C.qa_room_light('Passage', (x0 + 2.9, y0 + 1.8, U - .5), 40, 2.4)
    # Corten canopy: slab over the passage mouth and along the court's east edge to the hall block.
    # Thin corten plate along the court's east edge from the street line to the hall block, on the block wall and three columns.
    cx0, cx1, cy0, cy1 = 5.5, x0 - EPS, y0 + .3, y1 - .3
    C.box('Corten canopy plate', ((cx0 + cx1) / 2, (cy0 + cy1) / 2, CANOPY + .06), (cx1 - cx0, cy1 - cy0, .12), 'corten', 'corten canopy', 0)
    C.box('Corten canopy fascia west', (cx0 + .03, (cy0 + cy1) / 2, CANOPY + .0), (.06, cy1 - cy0, .28), 'corten', 'corten canopy', 0)
    C.box('Corten canopy fascia south', ((cx0 + cx1) / 2, cy0 + .03, CANOPY + .0), (cx1 - cx0, .06, .28), 'corten', 'corten canopy', 0)
    C.box('Corten canopy fascia north', ((cx0 + cx1) / 2, cy1 - .03, CANOPY + .0), (cx1 - cx0, .06, .28), 'corten', 'corten canopy', 0)
    for yy in (cy0 + .6, (cy0 + cy1) / 2, cy1 - .6):
        C.box('Canopy concrete column', (cx0 + .5, yy, (G0 + CANOPY) / 2), (.40, .40, CANOPY - G0), 'pale', 'corten canopy', 0)
    C.box('Canopy bench', (cx0 + 2.6, cy0 + 6.0, .45), (.45, 3.0, .08), 'timber', 'playground', 0)
    for dy in (-1.2, 1.2):
        C.box('Canopy bench leg', (cx0 + 2.6, cy0 + 6.0 + dy, .21), (.4, .1, .42), 'hardware', 'playground', 0)


def roofs():
    wing_roof(*WW, gravel=True, name='West wing roof')
    wing_roof(*SE, gravel=True, name='Entrance block roof')
    wing_roof(*NB, gravel=False, name='Hall terrace')
    wing_roof(*NW, gravel=False, name='North-west roof')
    C.box('Hall terrace gravel panel', (NB[1] - 6.5, NB[3] - 6.5, ROOF + .045), (12.0, 12.0, .05), 'roof', 'roof', 0)
    # Movement-joint cover strips over the block junctions so the tiled slabs read as one roof.
    for (ax, ay, bx, by) in ((WW[0] + T, WW[3], WW[1] - T, WW[3]), (NW[1], NW[2] + T, NW[1], NB[3] - T), (SE[0] + T, SE[3], SE[1] - T, SE[3])):
        if ax == bx:
            C.box('Roof joint cover', (ax, (ay + by) / 2, ROOF + .05), (.36, by - ay, .03), 'pale', 'roof', 0)
        else:
            C.box('Roof joint cover', ((ax + bx) / 2, ay, ROOF + .05), (bx - ax, .36, .03), 'pale', 'roof', 0)
    C.box('Hall terrace rooflight', (4.0, 6.0, ROOF + .35), (2.4, 2.4, .62), 'pale', 'roof', 0)
    C.box('Hall terrace rooflight glazing', (4.0, 6.0, ROOF + .68), (2.2, 2.2, .04), 'glass', 'roof', 0)
    h = T / 2
    # West wing: party west (no rail), street south, court east.
    edge((WW[0] + h, WW[2] + T), (WW[0] + h, WW[3]), CROWN, rail=False)
    edge((WW[0], WW[2] + h), (WW[1], WW[2] + h), CROWN)
    edge((WW[1] - h, WW[2] + T), (WW[1] - h, WW[3]), CROWN)
    # North-west block: party west and north, short east run above the hall, court-facing south run x -8..-3.
    edge((NW[0] + h, NW[2]), (NW[0] + h, NW[3] - T), CROWN, rail=False)
    edge((NW[0], NW[3] - h), (NW[1], NW[3] - h), CROWN, rail=False)
    edge((NW[1] - h, NB[3]), (NW[1] - h, NW[3] - T), CROWN)
    edge((CX0, NW[2] + h), (NW[1], NW[2] + h), CROWN)
    # Hall block: north blank with rail, street east, court-facing south x -3..11.
    edge((NB[0], NB[3] - h), (NB[1], NB[3] - h), CROWN)
    edge((NB[1] - h, NB[2] + T), (NB[1] - h, NB[3] - T), CROWN)
    edge((NB[0], NB[2] + h), (CX1, NB[2] + h), CROWN)
    # Entrance block: south, east and west (court) runs.
    edge((SE[0], SE[2] + h), (SE[1], SE[2] + h), CROWN)
    edge((SE[1] - h, SE[2] + T), (SE[1] - h, SE[3]), CROWN)
    edge((SE[0] + h, SE[2] + T), (SE[0] + h, SE[3]), CROWN)
    # Corten third storey on the north-west block, inset from the parapet.
    px0, px1, py0, py1 = PENT
    F = dict(south=C.Face(((px0 + px1) / 2, py0, 0), (1, 0, 0), (0, 1, 0), 'penthouse south'),
             east=C.Face((px1, (py0 + py1) / 2, 0), (0, 1, 0), (-1, 0, 0), 'penthouse east'),
             north=C.Face(((px0 + px1) / 2, py1, 0), (-1, 0, 0), (0, -1, 0), 'penthouse north'),
             west=C.Face((px0, (py0 + py1) / 2, 0), (0, -1, 0), (1, 0, 0), 'penthouse west'))
    for label, f in F.items():
        span = (px1 - px0) if label in ('south', 'north') else (py1 - py0)
        holes = []
        if label == 'east':
            holes = [hole(f'Penthouse east window {i}', u, ROOF + 1.0, 4.0, 2.2, cols=3) for i, u in enumerate((-7.0, -1.0, 5.0))]
        elif label == 'south':
            holes = [hole('Penthouse south window', 3.0, ROOF + 1.0, 5.0, 2.2, cols=3), hole('Penthouse terrace door', -4.0, ROOF, 1.2, 2.4, kind='door')]
        lo, hi = (-span / 2, span / 2) if label in ('south', 'north') else (-span / 2 + T, span / 2 - T)
        f.wall(f'Penthouse carrier {label}', lo, hi, ROOF, P_CROWN, depth=T, role='corten', holes=holes)
        for h in holes:
            if h.get('kind') == 'door':
                f.door(h['id'], h['u'], h['z'], h['w'], h['h'], role='trim', panels=1); lined(f, h, inset=.19, role='corten')
            else:
                f.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=h.get('cols', 3), rows=1, frame='trim', depth=T, sill=False)
                lined(f, h, role='corten')
        # Corten panel joints.
        vertices, faces = [], []
        n = max(1, round(span / 1.5))
        for i in range(1, n):
            u = lo + i * (hi - lo) / n
            spans = [(ROOF + EPS, P_CROWN - EPS)]
            for h in holes:
                if h['u'] - h['w'] / 2 - .01 < u < h['u'] + h['w'] / 2 + .01:
                    spans = [s for a, b in spans for s in ((a, min(b, h['z'])), (max(a, h['z'] + h['h']), b)) if s[1] - s[0] > .001]
            for a, b in spans:
                o = len(vertices); vertices.extend([f.p(u - .006, -.002, a), f.p(u + .006, -.002, a), f.p(u + .006, -.002, b), f.p(u - .006, -.002, b)]); faces.append((o, o + 1, o + 2, o + 3))
        if faces:
            C.mesh(f.label + ' corten joints', vertices, faces, 'joint', 'panel joints')
    C.box('Penthouse roof slab', ((px0 + px1) / 2, (py0 + py1) / 2, P_ROOF - .12), (px1 - px0 - 2 * T, py1 - py0 - 2 * T, .24), 'floor', 'roof', 0)
    C.box('Penthouse gravel', ((px0 + px1) / 2, (py0 + py1) / 2, P_ROOF + .02), (px1 - px0 - 2 * T - .02, py1 - py0 - 2 * T - .02, .04), 'roof', 'roof', 0)
    for s, (cx, cy, sx, sy) in dict(south=((px0 + px1) / 2, py0 + T / 2, px1 - px0, T + .06), north=((px0 + px1) / 2, py1 - T / 2, px1 - px0, T + .06),
                                   west=(px0 + T / 2, (py0 + py1) / 2, T + .06, py1 - py0 - 2 * T - .064), east=(px1 - T / 2, (py0 + py1) / 2, T + .06, py1 - py0 - 2 * T - .064)).items():
        C.box(f'Penthouse coping {s}', (cx, cy, P_CROWN + .03), (sx, sy, .06), 'corten', 'coping', 0)
    C.railing('Penthouse rail', (px0 + .3, py0 + T / 2, P_CROWN + .06), (px1 - .3, py0 + T / 2, P_CROWN + .06), height=1.0, spacing=1.0, role='hardware', bottom=.05)
    C.railing('Penthouse rail east', (px1 - T / 2, py0 + .3, P_CROWN + .06), (px1 - T / 2, py1 - .3, P_CROWN + .06), height=1.0, spacing=1.0, role='hardware', bottom=.05)
    C.box('Penthouse plant unit', (px0 + 3.0, py1 - 3.0, P_ROOF + .7), (2.2, 1.6, 1.3), 'pale', 'rooftop plant', 0)
    C.box('Penthouse rooflight', (px1 - 4.0, py0 + 4.0, P_ROOF + .3), (1.8, 1.8, .5), 'pale', 'roof', 0)
    # Terrace between the corten storey and the hall roof: paved; the NW block's remaining roof south of the penthouse is paved too.
    C.box('Terrace access door housing', (NB[0] + 2.0, NB[2] + 2.0, ROOF + 1.3), (2.4, 2.4, 2.6), 'wall', 'roof', 0)
    C.box('Terrace housing cap', (NB[0] + 2.0, NB[2] + 2.0, ROOF + 2.63), (2.5, 2.5, .06), 'pale', 'roof', 0)


def floors():
    C.box('Ground slab', (0, 0, G0 / 2), (SX1 - SX0, SY1 - SY0, G0), 'foundation', 'foundation', 0)
    C.box('South sidewalk', (0, SY0 - 2.0, .0075), (SX1 - SX0 + 4.0, 4.0, .015), 'foundation', 'sidewalk', 0)
    C.box('East sidewalk', (SX1 + 2.0, 0, .0075), (4.0, SY1 - SY0, .015), 'foundation', 'sidewalk', 0)
    C.box('Kerb south', (0, SY0 - 3.94, .06), (SX1 - SX0 + 4.0, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb east', (SX1 + 3.94, 0, .06), (.12, SY1 - SY0, .12), 'stone', 'sidewalk', 0)
    FLOORS.clear()
    for name, (x0, x1, y0, y1) in dict(NW=NW, WW=WW, NB=NB, SE=SE).items():
        FLOORS[name] = C.box('Upper floor ' + name, ((x0 + x1) / 2, (y0 + y1) / 2, U - .075), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .15), 'floor', 'occupied floors', 0)
    C.box('Penthouse floor', ((PENT[0] + PENT[1]) / 2, (PENT[2] + PENT[3]) / 2, ROOF + .05), (PENT[1] - PENT[0] - 2 * T, PENT[3] - PENT[2] - 2 * T, .02), 'floor', 'occupied floors', 0)
    # Courtyard: dark rubber surface with the green play panel; fence and gate on the street line.
    C.box('Court rubber surface', ((CX0 + CX1) / 2, (CY0 + CY1) / 2, G0 + .01), (CX1 - CX0, CY1 - CY0, .02), 'court', 'playground', 0)
    C.box('Play lawn panel', (-0.5, -12.0, G0 + .025), (8.0, 8.0, .01), 'play', 'playground', 0)
    C.box('Court kerb', ((CX0 + CX1) / 2, CY0 + .15, G0 + .12), (CX1 - CX0, .30, .24), 'pale', 'playground', 0)
    C.railing('Court fence west', (CX0 + .2, CY0 + .15, G0 + .24), (-1.0, CY0 + .15, G0 + .24), height=1.3, spacing=.22, role='hardware')
    C.railing('Court fence east', (1.0, CY0 + .15, G0 + .24), (6.0 - .2, CY0 + .15, G0 + .24), height=1.3, spacing=.22, role='hardware')
    C.railing('Court gate', (-.9, CY0 + .15, G0 + .24), (.9, CY0 + .15, G0 + .24), height=1.3, spacing=.22, role='fin_red')
    # Play structure and benches.
    px, py = -0.5, -12.0
    for dx, dy, role in ((-1.2, 0, 'fin_red'), (1.2, 0, 'fin_yellow'), (0, 1.2, 'fin_green')):
        C.box('Play house', (px + dx, py + dy, G0 + .9), (1.0, 1.0, 1.5), role, 'playground', 0)
        C.prism('Play house roof', [(px + dx - .65, G0 + 1.65), (px + dx + .65, G0 + 1.65), (px + dx, G0 + 2.1)], 'y', py + dy - .6, py + dy + .6, 'fin_teal', 'playground')
    C.prism('Play slide', [(py - 1.2, G0 + 1.2), (py - 3.2, G0 + .15), (py - 3.2, G0 + .35), (py - 1.2, G0 + 1.4)], 'x', px - .4, px + .4, 'pale', 'playground')
    for x in (-6.5, -3.0):
        C.box('Court bench', (x, CY0 + 1.0, .45), (2.4, .45, .08), 'timber', 'playground', 0)
        for dx in (-1.0, 1.0):
            C.box('Court bench leg', (x + dx, CY0 + 1.0, .21), (.1, .4, .42), 'hardware', 'playground', 0)
    street_tree(-13.0, SY0 - 2.4)
    street_tree(SX1 + 2.0, 8.0)


def street_tree(x, y, z=.015, height=6.5, spread=1.3):
    C.rod('Street tree trunk', (x, y, z), (x, y, z + height * .55), .14, 'timber', 'street planting', 8)
    for i, (dx, dy) in enumerate(((-.5, -.2), (.5, -.1), (.0, .5))):
        tip = (x + dx * spread, y + dy * spread, z + height * .72)
        C.rod('Street tree branch', (x, y, z + height * .5), tip, .06, 'timber', 'street planting', 6)
        A.foliage('Street tree crown', tip, (.9 * spread, .9 * spread, 1.2), detail=1)


def programme():
    for x, y in ((-14.0, -18.0), (-14.0, -11.0), (-14.0, -4.0), (3.0, 4.0), (10.0, 4.0)):
        for dx in (-1.6, 1.6):
            C.box('Classroom table', (x + dx, y, G0 + .62), (1.4, .7, .05), 'timber', 'classrooms', 0)
            for ddx in (-.6, .6):
                C.box('Table leg', (x + dx + ddx, y, G0 + .3), (.05, .05, .6), 'trim', 'classrooms', 0)
        C.qa_room_light('Classroom', (x, y, U - .4), 70, 3.2)
    for x, y in ((-14.0, -14.0), (-14.0, -4.0), (3.0, 4.0), (10.0, 4.0), (15.5, -9.5)):
        C.qa_room_light('Upper classroom', (x, y, ROOF - .4), 60, 3.2)
    C.qa_room_light('Hall', (8.0, 10.0, ROOF - .5), 110, 4.5)
    C.qa_room_light('Penthouse', (-11.0, 11.0, P_ROOF - .4), 60, 3.5)
    A.sofa(-9.0, 10.0, ROOF + .06)
    C.box('Hall stage', (8.0, 14.0, G0 + .35), (8.0, 3.0, .6), 'timber', 'hall', 0)
    for name, x, y in (('SE', 14.0, -10.5), ('WW', -11.0, -22.0)):
        y_end = y + 4.6
        C.cut_box(FLOORS[name], 'Stair aperture ' + name, (x, y_end - 1.9, U), (1.4, 3.6, .6))
        C.railing('Stair guard ' + name, (x + .8, y_end - 3.7, U), (x + .8, y_end - .1, U), height=1.02, spacing=.30, role='hardware')
        C.railing('Stair end guard ' + name, (x + .8, y_end - .1, U), (x - .8, y_end - .1, U), height=1.02, spacing=.30, role='hardware')
        G.stair('Stair ' + name, x, y, G0, U, length=4.6, width=1.2, landing_gap=.12)


def build():
    floors()
    blocks()
    passage_and_canopy()
    roofs()
    programme()
    C.CONTACTS.append(dict(name='Entrance passage open at grade between concrete columns', grade_m=0, clear_height_m=U - .55))
    C.CONTACTS.append(dict(name='Corten canopy on the entrance block beam and two court columns', soffit_m=CANOPY))
    C.CONTACTS.append(dict(name='Court fence on a concrete kerb with a red gate', grade_m=G0))


LIGHT_RIG = dict(key=(-40, -56, 48), fill=(50, -26, 42), rear=(-22, 56, 46), target=(0, -2, 6.0), gain=9.0)
