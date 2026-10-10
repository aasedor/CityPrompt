"""District energy centre, authored from the locked catalogue views of
central_utilities_plant_energy_centre / variant_1 (transparent_plant_showcase_urban).

Read from the pixels: a corner block of two volumes. The lower west volume is a two-storey
buff-brick frame with full-height glazed bays that expose the plant room, a board-formed
concrete panel in the upper corner bay, a recessed entrance bay, and a membrane roof
carrying two three-fan cooling banks, duct runs, a cluster of three slender flues and one
hourglass exhaust stack. The taller east volume is clad in corten panels with a narrow
slot window and carries two rooftop units. Streets lie to the west and south.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G
from contract import subtract_openings

SLUG = 'clay-energy-centre'
T = .30
G0 = .15
WB = (-18.0, 1.0, -17.0, 17.0)       # west glazed plant block
EB = (1.0, 18.0, -17.0, 17.0)        # east corten block
L1, W_ROOF, W_CROWN = 5.6, 11.6, 12.2
E_ROOF, E_CROWN = 14.2, 14.8
BAY = 5.6
EPS = .002
PALETTE = dict(wall=(.56, .42, .26), joint=(.42, .30, .18), trim=(.08, .08, .085),
    pale=(.60, .60, .58), stone=(.48, .47, .44), roof=(.66, .66, .64), sand=(.60, .56, .48),
    foundation=(.36, .36, .36), glass=(.50, .55, .54), hardware=(.10, .10, .11),
    interior=(.74, .70, .62), floor=(.40, .40, .39), timber=(.40, .30, .20), blue=(.14, .22, .28),
    planting=(.24, .42, .14), soil=(.19, .14, .08), corten=(.46, .22, .10), concrete=(.52, .51, .48),
    steel=(.62, .64, .66), teal=(.18, .48, .46), membrane=(.66, .66, .64))


def manifest(version):
    h = W_ROOF + 10.5
    cams = G.camera_roster(EB[1] - WB[0] + 8.0, WB[3] - WB[2] + 8.0, h, [
        ('facade_close', (-30.0, -26.0, 5.0), (-10.0, WB[2], 5.0), 45),
        ('architecture_close', (-24.0, -30.0, 12.0), (-4.0, WB[2], 10.0), 50),
        ('glass_close', (-28.0, -12.0, 3.0), (WB[0], -4.0, 3.2), 50),
        ('plant_window', (-6.0, -28.0, 2.4), (-6.0, WB[2], 2.6), 40),
        ('stack_contact', (-30.0, -30.0, 20.0), (-10.0, -6.0, 15.0), 45),
        ('corten_block', (30.0, -30.0, 10.0), (EB[1], -4.0, 8.0), 45),
        ('roof_plant', (-34.0, 10.0, 22.0), (-8.0, 2.0, 12.5), 45),
        ('corner_entry', (-30.0, -22.0, 2.2), (WB[0], -12.0, 2.4), 40),
        ('interior', (-10.0, -26.0, 2.0), (-10.0, -6.0, 2.4), 30),
        ('rear_service', (-10.0, 30.0, 4.0), (-4.0, WB[3], 3.0), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='central_utilities_plant_energy_centre/variant_1 (transparent_plant_showcase_urban)',
        measurement_contract=dict(dimensions_m=dict(width=EB[1] - WB[0] + 8.0, depth=WB[3] - WB[2] + 8.0, height=h),
            observed_storeys=2, storey_programme='two tall plant levels in the west block, three in the corten block; fixed authored assembly',
            plan='two abutting blocks read from the 560 x 560 px top view at 0.064 m/px: west glazed block 19 x 34 m, east corten block 17 x 34 m; streets west and south',
            west_block='buff brick piers on a 5.6 m bay with full-height glazed bays and transoms; board-formed concrete panel over the corner bay; recessed entrance bay at the south end of the west face',
            east_block='corten panel cladding 14.2 m to the roof with a narrow slot window on the south face',
            roof='membrane; two three-fan cooling banks on the west edge, duct runs, three slender flues at the centre, one hourglass stack with a dark cap; two rooftop units on the corten block',
            levels_m=[G0, L1], roofs_m=[W_ROOF, E_ROOF],
            inferred='36 m frontage calibrates the bays; north and east faces are not visible and repeat the grammar with service doors; plant interiors are teaching assumptions.'),
        roof_contract=dict(type='flat membranes behind low parapets; rooftop plant, flues and stack seated on curbs', datum_m=W_ROOF, crowns_m=[W_CROWN, E_CROWN, W_ROOF + 10.5]),
        identity_contract=dict(owner='brick-framed glass plant showcase with a concrete corner panel, corten tower block, cooling banks, flue cluster and hourglass stack'),
        material_contract=dict(profile='source-palette clay: buff brick with recessed courses, dark curtain-wall mullions, board-formed concrete, corten panels with joints, galvanised steel plant, pale membrane', textured_keeper=False),
        programme_contract=dict(storeys=2, ground='plant hall with chillers, pumps and pipework visible through the glazing', upper='mezzanine with switchgear and air handling', east='boiler house and stair'),
        contact_contract=['Grade-zero slab and sidewalks', 'Entrance threshold at slab level in the recessed bay', 'Curtain-wall bays between brick piers from plinth to parapet', 'Rooftop plant on curbs; flues and stack on bases', 'Corten block abuts the west block along one line'],
        runtime_contract=dict(scale='fixed_native_only', installation='not installed', review='NOT TESTED'),
        camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])


def hole(name, u, z, w, h, **kw):
    return dict(id=name, u=u, z=z, w=w, h=h, **kw)


def lined(f, h, inset=.14, role='trim'):
    d = inset / 2 + .005
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    for s in (-1, 1):
        f.part('Reveal jamb liner', u + s * (w / 2 - .011), d, z + hh / 2, .022, inset + .01, hh, role, 'reveals', 0)
    f.part('Reveal head liner', u, d, z + hh - .011, w, inset + .01, .022, role, 'reveals', 0)
    f.part('Reveal sill liner', u, d, z + .011, w, inset + .01, .022, role, 'reveals', 0)


def glazed_bay(f, h, cols=3, rows=4):
    f.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=cols, rows=rows, frame='trim', depth=T, sill=False)
    lined(f, h)


def corten_joints(f, lo, hi, z0, z1, holes, spacing=1.2):
    vertices, faces = [], []
    n = max(1, round((hi - lo) / spacing))
    for i in range(1, n):
        u = lo + i * (hi - lo) / n
        spans = [(z0, z1)]
        for h in holes:
            if h['u'] - h['w'] / 2 - .01 < u < h['u'] + h['w'] / 2 + .01:
                spans = [s for a, b in spans for s in ((a, min(b, h['z'])), (max(a, h['z'] + h['h']), b)) if s[1] - s[0] > .001]
        for a, b in spans:
            o = len(vertices)
            vertices.extend([f.p(u - .006, -.002, a), f.p(u + .006, -.002, a), f.p(u + .006, -.002, b), f.p(u - .006, -.002, b)])
            faces.append((o, o + 1, o + 2, o + 3))
    for z in (4.0, 7.5, 11.0):
        for a, b in subtract_openings(lo, hi, z - .006, z + .006, holes):
            o = len(vertices)
            vertices.extend([f.p(a, -.002, z - .006), f.p(b, -.002, z - .006), f.p(b, -.002, z + .006), f.p(a, -.002, z + .006)])
            faces.append((o, o + 1, o + 2, o + 3))
    if faces:
        C.mesh(f.label + ' corten joints', vertices, faces, 'joint', 'panel joints')


def face(x0, x1, y0, y1, side, label):
    if side == 'south': return C.Face(((x0 + x1) / 2, y0, 0), (1, 0, 0), (0, 1, 0), label)
    if side == 'north': return C.Face(((x0 + x1) / 2, y1, 0), (-1, 0, 0), (0, -1, 0), label)
    if side == 'east': return C.Face((x1, (y0 + y1) / 2, 0), (0, 1, 0), (-1, 0, 0), label)
    return C.Face((x0, (y0 + y1) / 2, 0), (0, -1, 0), (1, 0, 0), label)


def brick_frame_face(f, lo, hi, bays, concrete_bay=None, entrance_bay=None, inset_ends=True):
    """Brick pier elevation: full-height glazed bays between 1 m piers; optional concrete upper panel and entrance bay."""
    holes = []
    for i, c in enumerate(bays):
        if i == concrete_bay:
            holes.append(hole(f'{f.label} ground glazing {i}', c, G0, BAY - 1.0, L1 - .3, cols=3, rows=2))
            holes.append(hole(f'{f.label} upper glazing {i}', c, 9.4, BAY - 1.0, W_ROOF - .6 - 9.4, cols=3, rows=1))
        elif i == entrance_bay:
            holes.append(hole(f'{f.label} entrance bay', c, G0, BAY - 1.0, W_ROOF - .6 - G0, kind='entrance'))
        else:
            holes.append(hole(f'{f.label} glazed bay {i}', c, G0, BAY - 1.0, W_ROOF - .6 - G0))
    f.wall(f.label + ' carrier', lo, hi, G0, W_CROWN, depth=T, holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, G0, W_CROWN, holes, spacing=.075)
    for h in holes:
        if h.get('kind') == 'entrance':
            # Recessed entrance: glazed screen set 1.2 m back with doors, soffit and side returns in brick colour.
            lined(f, h, inset=1.2, role='wall')
            f.window(h['id'] + ' screen', h['u'], h['z'], h['w'], h['h'], cols=3, rows=3, frame='trim', inset=1.2, depth=T, sill=False, kind='glazed door')
            for du in (-.12, .12):
                C.rod('Entrance door pull', f.p(h['u'] + du, 1.2 - .02, h['z'] + .9), f.p(h['u'] + du, 1.2 - .02, h['z'] + 1.5), .018, 'hardware', 'door hardware')
            f.part('Entrance threshold', h['u'], .6, G0 - .005, h['w'], 1.2, .03, 'concrete', 'entrance', 0)
        elif 'upper glazing' in h['id']:
            glazed_bay(f, h, cols=3, rows=1)
        elif 'ground glazing' in h['id']:
            glazed_bay(f, h, cols=3, rows=2)
            # Board-formed concrete panel above the ground glazing, flush in the bay.
            f.part('Board-formed concrete panel', h['u'], T / 2, (L1 - .3 + G0 + 9.4) / 2, h['w'] + .02, T, 9.4 - (L1 - .3 + G0), 'concrete', 'concrete panel', 0)
            for k in range(1, 10):
                f.part('Board mark', h['u'], -.004, L1 - .15 + k * (9.4 - L1 + .15) / 10, h['w'] - .1, .008, .012, 'joint', 'concrete panel', 0)
        else:
            glazed_bay(f, h, cols=3, rows=4)
    f.part('Parapet coping', (lo + hi) / 2, T / 2, W_CROWN + .03, hi - lo - 2 * EPS, T + .06, .06, 'pale', 'coping', 0)
    f.part('Plinth', (lo + hi) / 2, -.02, .25, hi - lo - 2 * EPS, .04, .50, 'concrete', 'plinth', 0)


def west_block():
    x0, x1, y0, y1 = WB
    # South face (u = x): three bays of 5.6 across 19 m with 1 m piers; corner bay (east end) carries the concrete panel.
    f = face(*WB, 'south', 'west block south')
    bays = [x0 + 1.0 + BAY / 2 + i * BAY for i in range(3)]
    brick_frame_face(f, x0, x1 - EPS, bays, concrete_bay=2)
    # West face (u = -y): six bays; entrance in the southmost bay.
    f = face(*WB, 'west', 'west block west')
    bays = [-(y1 - 1.0 - BAY / 2 - i * BAY) for i in range(6)]   # u = -y, listed north to south
    brick_frame_face(f, -(y1 - y0) / 2 + T, (y1 - y0) / 2 - T, bays, entrance_bay=5)
    # North face: brick with service openings.
    f = face(*WB, 'north', 'west block north')
    nh = [hole('North louvre bay 0', -4.0, 1.0, 3.0, 2.5), hole('North service door', 4.0, G0, 2.4, 3.2, kind='door')]
    f.wall('west block north carrier', -(x1 - x0) / 2, (x1 - x0) / 2 - EPS, G0, W_CROWN, depth=T, holes=nh)
    G.brick_courses(f, -(x1 - x0) / 2 + .02, (x1 - x0) / 2 - .02, G0, W_CROWN, nh, spacing=.075)
    for h in nh:
        if h.get('kind') == 'door':
            f.part(h['id'] + ' leaf', h['u'], .22, h['z'] + h['h'] / 2, h['w'] - .06, .05, h['h'] - .02, 'pale', 'service door', 0)
            lined(f, h, inset=.19, role='pale')
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='roll-up door', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=.19, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='plant hall'))
        else:
            lined(f, h, inset=.14, role='pale')
            for k in range(6):
                f.part('Louvre blade', h['u'], .16, h['z'] + .2 + k * (h['h'] - .4) / 5, h['w'] - .05, .06, .10, 'hardware', 'louvres', 0)
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='louvre', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=.16, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='plant hall'))
    f.part('Parapet coping', 0, T / 2, W_CROWN + .03, x1 - x0 - 2 * EPS, T + .06, .06, 'pale', 'coping', 0)
    # Floors and roof.
    C.box('West slab', ((x0 + x1) / 2, (y0 + y1) / 2, G0 / 2), (x1 - x0, y1 - y0, G0), 'foundation', 'foundation', 0)
    mez = C.box('Mezzanine', ((x0 + x1) / 2 + 1.5, (y0 + y1) / 2, L1 - .075), (x1 - x0 - 2 * T - 3.0, y1 - y0 - 2 * T, .15), 'floor', 'occupied floors', 0)
    C.railing('Mezzanine edge guard', (x0 + T + 3.0, y0 + T + .2, L1), (x0 + T + 3.0, y1 - T - .2, L1), height=1.05, spacing=.3, role='hardware')
    C.box('West roof slab', ((x0 + x1) / 2, (y0 + y1) / 2, W_ROOF - .12), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .24), 'floor', 'roof', 0)
    C.box('West roof membrane', ((x0 + x1) / 2, (y0 + y1) / 2, W_ROOF + .004), (x1 - x0 - 2 * T - .02, y1 - y0 - 2 * T - .02, .008), 'membrane', 'roof', 0)
    G.stair('Plant stair', x0 + 2.0, 4.0, G0, L1, length=5.8, width=1.1, landing_gap=.12)


def east_block():
    x0, x1, y0, y1 = EB
    for side in ('south', 'east', 'north'):
        f = face(*EB, side, f'east block {side}')
        span = (x1 - x0) if side in ('south', 'north') else (y1 - y0)
        lo, hi = (-span / 2 + (EPS if side == 'south' else 0), span / 2) if side in ('south', 'north') else (-span / 2 + T, span / 2 - T)
        if side == 'north':
            lo, hi = -span / 2, span / 2 - EPS
        holes = []
        if side == 'south':
            holes = [hole('Corten slot window', 2.5, 2.0, 1.2, 9.0, cols=1, rows=3)]
        elif side == 'east':
            holes = [hole('East service door', -8.0, G0, 2.4, 3.2, kind='door'), hole('East louvre', 6.0, 3.0, 4.0, 2.4)]
        f.wall(f'east block {side} carrier', lo, hi, G0, E_CROWN, depth=T, role='corten', holes=holes)
        corten_joints(f, lo + .3, hi - .3, G0 + EPS, E_CROWN - EPS, holes)
        for h in holes:
            if h.get('kind') == 'door':
                f.part(h['id'] + ' leaf', h['u'], .22, h['z'] + h['h'] / 2, h['w'] - .06, .05, h['h'] - .02, 'pale', 'service door', 0)
                lined(f, h, inset=.19, role='pale')
                C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='roll-up door', clear_wall_cut=True,
                    carrier_depth_m=T, frame_inset_m=.19, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='boiler house'))
            elif 'louvre' in h['id'].lower():
                lined(f, h, inset=.14, role='pale')
                for k in range(6):
                    f.part('Louvre blade', h['u'], .16, h['z'] + .2 + k * (h['h'] - .4) / 5, h['w'] - .05, .06, .10, 'hardware', 'louvres', 0)
                C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='louvre', clear_wall_cut=True,
                    carrier_depth_m=T, frame_inset_m=.16, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='boiler house'))
            else:
                f.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=1, rows=3, frame='trim', depth=T, sill=False)
                lined(f, h, role='corten')
        f.part('Corten parapet coping', (lo + hi) / 2, T / 2, E_CROWN + .03, hi - lo - 2 * EPS, T + .06, .06, 'corten', 'coping', 0)
    # West side of the corten block above the west block roof.
    f = face(*EB, 'west', 'east block west')
    f.wall('east block west upper carrier', -(y1 - y0) / 2 + T, (y1 - y0) / 2 - T, W_ROOF - .24, E_CROWN, depth=T, role='corten')
    corten_joints(f, -(y1 - y0) / 2 + T + .3, (y1 - y0) / 2 - T - .3, W_ROOF + EPS, E_CROWN - EPS, [])
    f.part('Corten parapet coping', 0, T / 2, E_CROWN + .03, y1 - y0 - 2 * T - 2 * EPS, T + .06, .06, 'corten', 'coping', 0)
    C.box('East slab', ((x0 + x1) / 2, (y0 + y1) / 2, G0 / 2), (x1 - x0, y1 - y0, G0), 'foundation', 'foundation', 0)
    for z in (L1, 9.6):
        C.box('East floor', ((x0 + x1) / 2, (y0 + y1) / 2, z - .075), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .15), 'floor', 'occupied floors', 0)
    C.box('East roof slab', ((x0 + x1) / 2, (y0 + y1) / 2, E_ROOF - .12), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .24), 'floor', 'roof', 0)
    C.box('East roof membrane', ((x0 + x1) / 2, (y0 + y1) / 2, E_ROOF + .004), (x1 - x0 - 2 * T - .02, y1 - y0 - 2 * T - .02, .008), 'membrane', 'roof', 0)
    for x, y in ((x0 + 8.0, y0 + 8.0), (x0 + 8.0, y1 - 8.0)):
        C.box('Rooftop unit curb', (x, y, E_ROOF + .15), (3.2, 2.6, .30), 'pale', 'rooftop plant', 0)
        C.box('Rooftop unit', (x, y, E_ROOF + .30 + .9), (3.0, 2.4, 1.8), 'steel', 'rooftop plant', 0)
        C.rod('Rooftop unit fan', (x - .6, y, E_ROOF + 2.1), (x - .6, y, E_ROOF + 2.3), .5, 'hardware', 'rooftop plant', 14)
    C.qa_room_light('Boiler house', ((x0 + x1) / 2, 0, 9.0), 90, 4.0)


def rooftop_plant():
    x0, x1, y0, y1 = WB
    z = W_ROOF
    # Two three-fan cooling banks along the west edge.
    for yc in (y0 + 7.0, y1 - 7.0):
        bx = x0 + 4.0
        C.box('Cooling bank curb', (bx, yc, z + .15), (3.4, 7.0, .30), 'pale', 'rooftop plant', 0)
        C.box('Cooling bank body', (bx, yc, z + .30 + 1.1), (3.2, 6.8, 2.2), 'steel', 'rooftop plant', 0)
        for k in (-1, 0, 1):
            C.rod('Cooling fan cowl', (bx, yc + k * 2.2, z + 2.5), (bx, yc + k * 2.2, z + 2.75), .95, 'hardware', 'rooftop plant', 16)
        C.rod('Cooling bank header', (bx + 1.8, yc - 3.2, z + 1.6), (bx + 1.8, yc + 3.2, z + 1.6), .22, 'steel', 'rooftop plant', 12)
    # Duct runs from the banks across the roof to the corten block.
    for yc, dz in ((y0 + 7.0, 1.0), (y1 - 7.0, 1.4)):
        C.box('Duct run', ((x0 + 5.8 + x1 - 1.0) / 2, yc, z + dz), (x1 - 1.0 - x0 - 5.8, 1.2, .9), 'steel', 'rooftop plant', 0)
        for xx in (x0 + 8.0, x0 + 12.0):
            C.box('Duct support', (xx, yc, z + (dz - .45) / 2 + .0), (.2, 1.0, dz - .45), 'pale', 'rooftop plant', 0)
    C.box('Duct cross run', (x0 + 10.0, 0.0, z + 1.2), (1.2, (y1 - 7.0) - (y0 + 7.0), .9), 'steel', 'rooftop plant', 0)
    # Flue cluster: three slender flues on a common base at the centre.
    C.box('Flue base', (x0 + 12.5, 0.0, z + .25), (2.6, 1.4, .50), 'concrete', 'flues', 0)
    for k in (-1, 0, 1):
        C.rod('Slender flue', (x0 + 12.5 + k * .8, 0.0, z + .5), (x0 + 12.5 + k * .8, 0.0, z + 6.5), .22, 'steel', 'flues', 12)
        C.rod('Flue cap', (x0 + 12.5 + k * .8, 0.0, z + 6.5), (x0 + 12.5 + k * .8, 0.0, z + 6.7), .30, 'hardware', 'flues', 12)
    C.box('Flue brace', (x0 + 12.5, 0.0, z + 4.0), (2.2, .10, .10), 'pale', 'flues', 0)
    # Hourglass exhaust stack toward the south-west with a dark cap.
    sx, sy = x0 + 7.0, y0 + 11.5
    C.box('Stack base', (sx, sy, z + .3), (2.6, 2.6, .60), 'concrete', 'stack', 0)
    C.rod('Stack lower cone', (sx, sy, z + .6), (sx, sy, z + 3.2), .9, 'steel', 'stack', 16)
    C.rod('Stack waist', (sx, sy, z + 3.2), (sx, sy, z + 7.0), .5, 'steel', 'stack', 16)
    C.rod('Stack upper flare', (sx, sy, z + 7.0), (sx, sy, z + 9.6), .8, 'steel', 'stack', 16)
    C.rod('Stack cap', (sx, sy, z + 9.6), (sx, sy, z + 10.3), .85, 'hardware', 'stack', 16)
    for k in range(4):
        a = math.tau * k / 4
        C.beam('Stack guy strut', (sx + math.cos(a) * 1.2, sy + math.sin(a) * 1.2, z + .6), (sx + math.cos(a) * .55, sy + math.sin(a) * .55, z + 5.0), .07, .07, 'pale', 'stack')
    C.CONTACTS.append(dict(name='Cooling banks, flues and stack on curbs and bases on the west roof', roof_m=W_ROOF))


def plant_interior():
    x0, x1, y0, y1 = WB
    for i, (x, y) in enumerate(((-12.0, -10.0), (-6.0, -10.0), (-12.0, -2.0), (-6.0, 2.0), (-12.0, 8.0))):
        C.box('Chiller unit', (x, y, G0 + 1.1), (3.0, 1.6, 2.2), 'teal' if i % 2 else 'steel', 'plant', 0)
        C.rod('Chiller header pipe', (x - 1.5, y + .9, G0 + 2.6), (x + 1.5, y + .9, G0 + 2.6), .16, 'steel', 'plant', 10)
    for y in (-13.0, 4.0):
        C.rod('Main pipe run', (x0 + 1.5, y, G0 + 4.3), (x1 - 1.5, y, G0 + 4.3), .22, 'steel', 'plant', 12)
    for x in (-14.0, -8.0, -2.0):
        C.rod('Riser pipe', (x, -13.0, G0 + .2), (x, -13.0, G0 + 4.3), .14, 'steel', 'plant', 10)
    for x in (-13.0, -6.0):
        for y in (-11.0, 0.0, 11.0):
            C.qa_room_light('Plant hall', (x, y, L1 - .4), 110, 3.5)
            C.qa_room_light('Mezzanine', (x, y, W_ROOF - .5), 70, 3.5)
    C.box('Switchgear line-up', (-8.0, 10.0, L1 + 1.0), (6.0, .9, 2.0), 'hardware', 'plant', 0)
    C.box('Control desk', (-14.0, -14.0, G0 + .5), (2.0, .8, 1.0), 'timber', 'plant', 0)


def site():
    x0, x1, y0, y1 = WB[0], EB[1], WB[2], WB[3]
    C.box('South sidewalk', ((x0 + x1) / 2, y0 - 2.0, .0075), (x1 - x0 + 4.0, 4.0, .015), 'foundation', 'sidewalk', 0)
    C.box('West sidewalk', (x0 - 2.0, (y0 + y1) / 2, .0075), (4.0, y1 - y0, .015), 'foundation', 'sidewalk', 0)
    C.box('Kerb south', ((x0 + x1) / 2, y0 - 3.94, .06), (x1 - x0 + 4.0, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb west', (x0 - 3.94, (y0 + y1) / 2, .06), (.12, y1 - y0, .12), 'stone', 'sidewalk', 0)
    C.box('East service yard', (x1 + 2.0, (y0 + y1) / 2, .0075), (4.0, y1 - y0, .015), 'foundation', 'sidewalk', 0)
    for y in (-8.0, 6.0):
        street_tree(x0 - 2.4, y)
    street_tree(6.0, y0 - 2.4)


def street_tree(x, y, z=.015, height=6.0, spread=1.3):
    C.rod('Street tree trunk', (x, y, z), (x, y, z + height * .55), .14, 'timber', 'street planting', 8)
    for i, (dx, dy) in enumerate(((-.5, -.2), (.5, -.1), (.0, .5))):
        tip = (x + dx * spread, y + dy * spread, z + height * .72)
        C.rod('Street tree branch', (x, y, z + height * .5), tip, .06, 'timber', 'street planting', 6)
        A.foliage('Street tree crown', tip, (.9 * spread, .9 * spread, 1.2), detail=1)


def build():
    site()
    west_block()
    east_block()
    rooftop_plant()
    plant_interior()
    C.CONTACTS.append(dict(name='Recessed entrance bay with threshold at slab level', grade_m=0, recess_m=1.2))
    C.CONTACTS.append(dict(name='Corten block abuts the west block along x = 1.0 from grade to its parapet', line_m=1.0))


LIGHT_RIG = dict(key=(-40, -52, 48), fill=(50, -24, 42), rear=(-20, 52, 46), target=(0, 0, 8.0), gain=9.0)
