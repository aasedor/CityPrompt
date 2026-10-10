"""Anchored L-plaza supermarket with parking court, authored from the locked catalogue views
of commercial_strip_mall / variant_1 (strip_anchored_l_plaza).

Read from the pixels: a single-storey L-plan plaza on a prairie highway lot. The anchor
grocery sits at the west end as a taller box with a projecting entrance tower and a green
sign band, a lower cafe wing on its west flank; an inline run of glazed shop fronts under
a continuous canopy runs east along the north edge of the parking court; an end-cap wing
turns south along the east edge with a drive-through at its southern end. Beige EIFS over
a brick base with brick pilasters, dark cornice bands, flat roofs with rooftop units, a
striped parking court with cars, a pylon sign at the road and lawn verges.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G
from contract import subtract_openings

SLUG = 'clay-anchored-plaza-supermarket'
T = .30
G0 = .15
ANCHOR = (-40.0, -4.0, 0.0, 30.0)        # grocery box
CAFE = (-46.0, -40.0, 0.0, 14.0)         # low cafe wing
INLINE = (-4.0, 40.0, 16.0, 30.0)        # inline shops
ENDCAP = (40.0, 54.0, -16.0, 30.0)       # end-cap wing
A_ROOF, A_CROWN = 8.0, 8.8
S_ROOF, S_CROWN = 5.8, 6.5
TOWER_TOP = 11.2
CANOPY_Z = 3.9
LOT = (-50.0, 58.0, -40.0, 34.0)
EPS = .002
PALETTE = dict(wall=(.62, .55, .42), joint=(.50, .44, .33), trim=(.09, .09, .09),
    pale=(.70, .70, .68), stone=(.44, .30, .20), roof=(.72, .70, .64), sand=(.68, .60, .46),
    foundation=(.34, .34, .34), glass=(.50, .55, .54), hardware=(.10, .10, .11),
    interior=(.76, .72, .62), floor=(.42, .42, .40), timber=(.40, .30, .20), blue=(.14, .22, .28),
    planting=(.46, .42, .22), soil=(.19, .14, .08), cap=(.24, .18, .13), green=(.14, .42, .18),
    cream=(.90, .88, .80), tan=(.52, .44, .32), car=(.30, .32, .36))


def manifest(version):
    h = TOWER_TOP + .4
    cams = G.camera_roster(LOT[1] - LOT[0], LOT[3] - LOT[2], h, [
        ('facade_close', (-30.0, -24.0, 4.0), (-18.0, ANCHOR[2], 5.0), 45),
        ('architecture_close', (-32.0, -16.0, 10.0), (-18.0, ANCHOR[2], 9.0), 50),
        ('glass_close', (-12.0, -10.0, 2.6), (-8.0, ANCHOR[2], 2.4), 50),
        ('anchor_entrance', (-18.0, -22.0, 2.4), (-18.0, ANCHOR[2], 3.0), 40),
        ('inline_shops', (0.0, 0.0, 3.0), (16.0, INLINE[2], 3.0), 40),
        ('endcap_corner', (30.0, -30.0, 3.0), (ENDCAP[0], -8.0, 3.2), 40),
        ('parking_court', (-10.0, -60.0, 10.0), (4.0, -8.0, 1.5), 45),
        ('roof_units', (-56.0, -30.0, 22.0), (-20.0, 14.0, 8.5), 45),
        ('interior', (-18.0, -14.0, 2.0), (-18.0, 10.0, 2.0), 30),
        ('rear_service', (10.0, 46.0, 4.0), (-10.0, ANCHOR[3], 3.0), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='commercial_strip_mall/variant_1 (strip_anchored_l_plaza)',
        measurement_contract=dict(dimensions_m=dict(width=LOT[1] - LOT[0], depth=LOT[3] - LOT[2], height=h),
            observed_storeys=1, storey_programme='single-storey retail with a taller anchor box; fixed authored assembly',
            plan='L-plan read from the top view: anchor 36 x 30 m with a 6 m cafe wing, inline run 44 x 14 m along the north edge, end-cap wing 14 x 46 m along the east edge; parking court inside the L, road to the south',
            anchor='entrance tower projecting from the south face with a green sign band; glazed entrance and storefront; stockroom and loading at the rear',
            inline='glazed shop fronts on a 6 m module under a continuous canopy, brick pilasters, sign band, dark cornice',
            endcap='shops facing the court; drive-through lane at the south end',
            heights_m=dict(anchor_roof=A_ROOF, shops_roof=S_ROOF, tower=TOWER_TOP, canopy=CANOPY_Z),
            site='striped parking court with cars, pylon sign at the south-west, lawn verges, road along the south',
            inferred='module dimensions calibrated from the 1000 px lot width; the rear faces are not visible and carry service doors; interiors are teaching assumptions.'),
        roof_contract=dict(type='flat membranes behind EIFS parapets; rooftop units on curbs; taller anchor roof; entrance tower cap', datum_m=S_ROOF, crowns_m=[S_CROWN, A_CROWN, TOWER_TOP]),
        identity_contract=dict(owner='L-plan plaza wrapping a parking court, anchor with projecting sign tower, continuous shop canopy, brick base and pilasters, pylon sign'),
        material_contract=dict(profile='source-palette clay: beige EIFS with recessed joints, orange-brown brick base and pilasters with recessed courses, dark cornice caps, green sign band, dark storefront frames, pale membrane', textured_keeper=False),
        programme_contract=dict(storeys=1, anchor='grocery sales floor with aisles and checkouts behind the storefront', inline='six tenant units', endcap='three tenant units and a drive-through'),
        contact_contract=['Grade-zero slab and lot', 'Storefront thresholds at slab level under the canopy', 'Canopy on wall brackets along the inline run', 'Tower projects from the anchor face to grade', 'Rooftop units on curbs', 'Pylon sign on a brick base'],
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


def joints(f, lo, hi, z0, z1, holes, spacing=1.5):
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
            vertices.extend([f.p(u - .005, -.002, a), f.p(u + .005, -.002, a), f.p(u + .005, -.002, b), f.p(u - .005, -.002, b)])
            faces.append((o, o + 1, o + 2, o + 3))
    if faces:
        C.mesh(f.label + ' panel joints', vertices, faces, 'joint', 'panel joints')


def face(x0, x1, y0, y1, side, label):
    if side == 'south': return C.Face(((x0 + x1) / 2, y0, 0), (1, 0, 0), (0, 1, 0), label)
    if side == 'north': return C.Face(((x0 + x1) / 2, y1, 0), (-1, 0, 0), (0, -1, 0), label)
    if side == 'east': return C.Face((x1, (y0 + y1) / 2, 0), (0, 1, 0), (-1, 0, 0), label)
    return C.Face((x0, (y0 + y1) / 2, 0), (0, -1, 0), (1, 0, 0), label)


def storefront(f, h):
    f.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=h.get('cols', 3), rows=1, frame='trim', depth=T, sill=False, kind='storefront')
    lined(f, h)
    f.part('Storefront base', h['u'], -.02, G0 + .2, h['w'] + .1, .04, .40, 'stone', 'storefront base', 0)


def elevation(f, lo, hi, holes, crown, brick_base=True, pilasters=(), sign_band=False, cornice=True):
    f.wall(f.label + ' carrier', lo, hi, G0, crown, depth=T, holes=holes)
    joints(f, lo + .3, hi - .3, 1.3, crown - .9, holes)
    for h in holes:
        if h.get('kind') == 'door':
            f.part(h['id'] + ' leaf', h['u'], .22, h['z'] + h['h'] / 2, h['w'] - .06, .05, h['h'] - .02, 'pale', 'service doors', 0)
            lined(f, h, inset=.19, role='pale')
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='service door', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=.19, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='back of house'))
        else:
            storefront(f, h)
    if brick_base:
        for a, b in subtract_openings(lo + .02, hi - .02, G0, 1.2, holes):
            if b - a > .1:
                f.part('Brick base', (a + b) / 2, -.03, (G0 + 1.2) / 2, b - a, .06, 1.2 - G0, 'stone', 'brick base', 0)
    for u in pilasters:
        f.part('Brick pilaster', u, -.12, (G0 + crown - .9) / 2, .9, .24, crown - .9 - G0, 'stone', 'pilasters', 0)
        f.part('Pilaster cap', u, -.14, crown - .86, 1.0, .28, .08, 'cream', 'pilasters', 0)
    if sign_band:
        f.part('Sign band', (lo + hi) / 2, -.03, crown - 1.6, hi - lo - .2, .06, 1.0, 'cream', 'sign band', 0)
    if cornice:
        f.part('Cornice cap', (lo + hi) / 2, -.06, crown - .40, hi - lo - 2 * EPS, .12, .80, 'cap', 'cornice', 0)
        f.part('Parapet coping', (lo + hi) / 2, T / 2, crown + .03, hi - lo - 2 * EPS, T + .06, .06, 'cap', 'coping', 0)


def anchor():
    x0, x1, y0, y1 = ANCHOR
    # South face: storefront glazing flanking the entrance; the tower projects in front of the entrance.
    f = face(*ANCHOR, 'south', 'anchor south')
    tx = -18.0 - (x0 + x1) / 2          # tower centre in face u
    holes = [hole('Anchor entrance doors', tx, G0, 5.0, 3.2, cols=4), hole('Anchor storefront west', tx - 8.0, G0, 8.0, 3.4, cols=5), hole('Anchor storefront east', tx + 8.0, G0, 8.0, 3.4, cols=5)]
    elevation(f, -(x1 - x0) / 2, (x1 - x0) / 2, holes, A_CROWN, pilasters=(tx - 13.0, tx - 4.0, tx + 4.0, tx + 13.0), sign_band=False)
    f.part('Anchor canopy', tx, -1.2, CANOPY_Z + .2, 24.0, 2.4, .35, 'cap', 'canopies', 0)
    # Entrance tower: projecting EIFS frame with the green sign panel, rising above the parapet.
    tw, tp = 10.0, 1.6
    cx = -18.0
    C.box('Tower west pier', (cx - tw / 2 + .6, y0 - tp / 2, (G0 + TOWER_TOP) / 2), (1.2, tp, TOWER_TOP - G0), 'tan', 'entrance tower', 0)
    C.box('Tower east pier', (cx + tw / 2 - .6, y0 - tp / 2, (G0 + TOWER_TOP) / 2), (1.2, tp, TOWER_TOP - G0), 'tan', 'entrance tower', 0)
    C.box('Tower head', (cx, y0 - tp / 2, TOWER_TOP - 1.4), (tw, tp, 2.8), 'tan', 'entrance tower', 0)
    C.box('Tower cap', (cx, y0 - tp / 2, TOWER_TOP + .05), (tw + .2, tp + .2, .10), 'cap', 'entrance tower', 0)
    C.box('Tower sign panel', (cx, y0 - tp - .03, 6.4), (tw - 2.4, .06, 2.2), 'green', 'entrance tower', 0)
    C.box('Tower sign lettering bar', (cx, y0 - tp - .07, 6.4), (tw - 4.0, .02, .7), 'cream', 'entrance tower', 0)
    C.box('Tower return wall', (cx, y0 - .15, (G0 + TOWER_TOP - 2.8) / 2 + 4.2), (tw - 2.4, .30, 2.0), 'tan', 'entrance tower', 0)
    # Side faces.
    f = face(*ANCHOR, 'east', 'anchor east')
    lo, hi = -(y1 - y0) / 2 + T, (y1 - y0) / 2 - T
    eh = [hole('Anchor east window', -11.0, 1.4, 3.0, 2.0)]
    elevation(f, lo, lo + (INLINE[2] - y0) - EPS, eh, A_CROWN)
    f.wall('anchor east upper carrier', lo + (INLINE[2] - y0), hi, S_CROWN - .24, A_CROWN, depth=T)
    f.part('Cornice cap', (lo + (INLINE[2] - y0) + hi) / 2, -.06, A_CROWN - .40, hi - lo - (INLINE[2] - y0) - 2 * EPS, .12, .80, 'cap', 'cornice', 0)
    f.part('Parapet coping', (lo + (INLINE[2] - y0) + hi) / 2, T / 2, A_CROWN + .03, hi - lo - (INLINE[2] - y0) - 2 * EPS, T + .06, .06, 'cap', 'coping', 0)
    f = face(*ANCHOR, 'west', 'anchor west')
    lo, hi = -(y1 - y0) / 2 + T, (y1 - y0) / 2 - T
    f.wall('anchor west lower carrier', lo, (y1 - CAFE[3]) - (y1 - y0) / 2 - EPS, G0, A_CROWN, depth=T)          # exposed north of the cafe wing
    f.wall('anchor west upper carrier', (y1 - CAFE[3]) - (y1 - y0) / 2, hi, S_CROWN - .24, A_CROWN, depth=T)     # above the cafe roof
    f.part('Cornice cap', 0, -.06, A_CROWN - .40, hi - lo - 2 * EPS, .12, .80, 'cap', 'cornice', 0)
    f.part('Parapet coping', 0, T / 2, A_CROWN + .03, hi - lo - 2 * EPS, T + .06, .06, 'cap', 'coping', 0)
    f = face(*ANCHOR, 'north', 'anchor north')
    nh = [hole('Anchor loading door', -8.0, G0, 4.0, 4.2, kind='door'), hole('Anchor rear door', 6.0, G0, 1.1, 2.4, kind='door')]
    elevation(f, -(x1 - x0) / 2, (x1 - x0) / 2, nh, A_CROWN, brick_base=True)
    C.box('Loading dock', (x0 + 8.0 + 0, y1 + 1.4, .55), (6.0, 2.8, 1.1), 'foundation', 'loading dock', 0)
    # Cafe wing.
    f = face(*CAFE, 'south', 'cafe south')
    ch = [hole('Cafe storefront', 0.0, G0, 4.6, 3.2, cols=3)]
    elevation(f, -(CAFE[1] - CAFE[0]) / 2, (CAFE[1] - CAFE[0]) / 2 - EPS, ch, S_CROWN, sign_band=True)
    f.part('Cafe canopy', 0.0, -1.0, CANOPY_Z + .2, 5.6, 2.0, .30, 'cap', 'canopies', 0)
    f = face(*CAFE, 'west', 'cafe west')
    wh = [hole('Cafe west window 0', -3.5, 1.0, 3.0, 2.2), hole('Cafe west window 1', 2.5, 1.0, 3.0, 2.2)]
    elevation(f, -(CAFE[3] - CAFE[2]) / 2 + T, (CAFE[3] - CAFE[2]) / 2 - T, wh, S_CROWN)
    f = face(*CAFE, 'north', 'cafe north')
    elevation(f, -(CAFE[1] - CAFE[0]) / 2, (CAFE[1] - CAFE[0]) / 2 - EPS, [], S_CROWN)
    roof(*ANCHOR, A_ROOF, units=((-30.0, 20.0), (-22.0, 24.0), (-12.0, 20.0), (-30.0, 8.0), (-10.0, 8.0)))
    roof(*CAFE, S_ROOF, units=((-43.0, 7.0),))
    C.CONTACTS.append(dict(name='Entrance tower piers to grade in front of the anchor doors', grade_m=0, height_m=TOWER_TOP))


def inline_and_endcap():
    x0, x1, y0, y1 = INLINE
    f = face(*INLINE, 'south', 'inline south')
    n = 7
    pil, holes = [], []
    for i in range(n):
        c = -(x1 - x0) / 2 + (i + .5) * (x1 - x0) / n
        holes.append(hole(f'Inline shop front {i}', c, G0, (x1 - x0) / n - 1.6, 3.2, cols=3))
        if i:
            pil.append(-(x1 - x0) / 2 + i * (x1 - x0) / n)
    elevation(f, -(x1 - x0) / 2 + EPS, (x1 - x0) / 2, holes, S_CROWN, pilasters=pil, sign_band=True)
    f.part('Inline canopy', 0, -1.2, CANOPY_Z + .15, x1 - x0 - .4, 2.4, .30, 'cap', 'canopies', 0)
    for u in pil + [-(x1 - x0) / 2 + .5, (x1 - x0) / 2 - .5]:
        C.beam('Canopy bracket', f.p(u, -.05, CANOPY_Z + 1.6), f.p(u, -2.2, CANOPY_Z + .3), .06, .06, 'hardware', 'canopies')
    f = face(*INLINE, 'north', 'inline north')
    nh = [hole(f'Inline rear door {i}', -(x1 - x0) / 2 + (i + .5) * (x1 - x0) / n, G0, 1.1, 2.4, kind='door') for i in range(n)]
    elevation(f, -(x1 - x0) / 2 + EPS, (x1 - x0) / 2, nh, S_CROWN)
    roof(*INLINE, S_ROOF, units=((4.0, 24.0), (16.0, 22.0), (28.0, 24.0)))
    # End-cap wing: shops facing west into the court, drive-through at the south end.
    x0, x1, y0, y1 = ENDCAP
    f = face(*ENDCAP, 'west', 'endcap west')
    span = y1 - y0
    holes = []
    pil = []
    # Face u = -y: north end u = -span/2 (y = y1); the inline run occupies y 16..30 so shops start south of y = 16.
    u_start = -(INLINE[2] - (y0 + y1) / 2)        # u at y = 16
    for i in range(4):
        c = u_start + (i + .5) * 7.0
        holes.append(hole(f'Endcap shop front {i}', c, G0, 5.4, 3.2, cols=3))
        pil.append(u_start + (i + 1) * 7.0)
    holes.append(hole('Drive-through window', u_start + 4 * 7.0 + 2.5, 1.0, 1.4, 1.4, cols=1))
    elevation(f, u_start + EPS, span / 2 - T, holes, S_CROWN, pilasters=pil[:-1], sign_band=True)
    f.wall('endcap west rear carrier', -span / 2 + T, u_start - EPS, S_CROWN - .24, S_CROWN, depth=T)
    f.part('Endcap canopy', u_start + 14.0, -1.2, CANOPY_Z + .15, 27.6, 2.4, .30, 'cap', 'canopies', 0)
    for u in pil[:-1] + [u_start + .5, u_start + 27.5]:
        C.beam('Canopy bracket', f.p(u, -.05, CANOPY_Z + 1.6), f.p(u, -2.2, CANOPY_Z + .3), .06, .06, 'hardware', 'canopies')
    f = face(*ENDCAP, 'south', 'endcap south')
    sh = [hole('Endcap south window', -2.0, 1.0, 4.0, 2.2, cols=3)]
    elevation(f, -(x1 - x0) / 2, (x1 - x0) / 2, sh, S_CROWN, sign_band=True)
    f = face(*ENDCAP, 'east', 'endcap east')
    eh = [hole(f'Endcap rear door {i}', -16.0 + i * 8.0, G0, 1.1, 2.4, kind='door') for i in range(4)]
    eh.append(hole('Drive-through service window', 18.0, 1.0, 1.4, 1.4, cols=1))
    elevation(f, -span / 2 + T, span / 2 - T, eh, S_CROWN)
    f = face(*ENDCAP, 'north', 'endcap north')
    elevation(f, -(x1 - x0) / 2, (x1 - x0) / 2, [], S_CROWN)
    roof(*ENDCAP, S_ROOF, units=((47.0, 20.0), (47.0, 6.0), (47.0, -8.0)))
    # Drive-through lane markings and a bollard pair at the south end.
    C.box('Drive-through lane', (x0 - 2.5, (y0 + 0.0) / 2 - 2.0, .018), (3.5, 12.0, .006), 'cream', 'site', 0)
    for dy in (-1.2, 1.2):
        C.rod('Drive-through bollard', (x0 - 1.0, -10.0 + dy, 0), (x0 - 1.0, -10.0 + dy, .9), .09, 'cap', 'site', 10)


def roof(x0, x1, y0, y1, z, units=()):
    C.box('Roof slab', ((x0 + x1) / 2, (y0 + y1) / 2, z - .12), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .24), 'floor', 'roof', 0)
    C.box('Roof membrane', ((x0 + x1) / 2, (y0 + y1) / 2, z + .004), (x1 - x0 - 2 * T - .02, y1 - y0 - 2 * T - .02, .008), 'roof', 'roof', 0)
    for ux, uy in units:
        C.box('Rooftop unit curb', (ux, uy, z + .15), (2.4, 1.6, .30), 'pale', 'rooftop plant', 0)
        C.box('Rooftop unit', (ux, uy, z + .30 + .7), (2.2, 1.4, 1.4), 'pale', 'rooftop plant', 0)
        C.rod('Rooftop unit fan', (ux - .5, uy, z + 1.70), (ux - .5, uy, z + 1.85), .40, 'hardware', 'rooftop plant', 12)
    C.box('Ground slab', ((x0 + x1) / 2, (y0 + y1) / 2, G0 / 2), (x1 - x0, y1 - y0, G0), 'foundation', 'foundation', 0)


def site():
    lx0, lx1, ly0, ly1 = LOT
    C.box('Parking court', ((lx0 + lx1) / 2, (ly0 + ly1) / 2, .0075), (lx1 - lx0, ly1 - ly0, .015), 'foundation', 'site', 0)
    C.box('Lawn verge south', ((lx0 + lx1) / 2, ly0 - 3.0, .021), (lx1 - lx0 + 8.0, 6.0, .012), 'planting', 'site', 0)
    C.box('Road', ((lx0 + lx1) / 2, ly0 - 9.5, .0075), (lx1 - lx0 + 8.0, 7.0, .015), 'floor', 'site', 0)
    # Parking stripes as one batched mesh.
    vertices, faces = [], []
    for row_y, length in ((-6.0, 5.0), (-16.0, 5.0), (-30.0, 5.0)):
        x = -36.0
        while x < 36.0:
            o = len(vertices)
            vertices.extend([(x - .06, row_y, .016), (x + .06, row_y, .016), (x + .06, row_y + length, .016), (x - .06, row_y + length, .016)])
            faces.append((o, o + 1, o + 2, o + 3)); x += 2.8
    C.mesh('Parking stripes', vertices, faces, 'cream', 'site')
    for i, (x, y) in enumerate(((-30.0, -3.5), (-22.0, -3.5), (-8.0, -3.5), (6.0, -3.5), (-26.0, -13.5), (-4.0, -13.5), (14.0, -13.5), (-18.0, -27.5), (2.0, -27.5), (22.0, -27.5))):
        C.box('Parked car body', (x, y, .65), (1.8, 4.4, .9), 'car' if i % 3 else 'pale', 'site', 0)
        C.box('Parked car cabin', (x, y + .2, 1.35), (1.6, 2.4, .6), 'trim', 'site', 0)
    C.box('Pylon sign base', (lx0 + 4.0, ly0 + 3.0, .6), (1.6, .8, 1.2), 'stone', 'site', 0)
    C.box('Pylon sign post', (lx0 + 4.0, ly0 + 3.0, 3.6), (.5, .4, 4.8), 'tan', 'site', 0)
    C.box('Pylon sign board', (lx0 + 4.0, ly0 + 3.0, 7.0), (3.2, .3, 2.6), 'green', 'site', 0)
    C.box('Pylon sign panel', (lx0 + 4.0, ly0 + 2.82, 7.0), (2.8, .02, 2.0), 'cream', 'site', 0)
    for x in (-10.0, 20.0):
        C.box('Court planter', (x, -20.0, .35), (1.4, 8.0, .7), 'stone', 'site', 0)
        C.box('Court planter shrubs', (x, -20.0, .95), (1.1, 7.6, .5), 'planting', 'site', 0)
    for x in (58.0,):
        for y in (-20.0, 0.0, 20.0):
            C.rod('Shelterbelt tree trunk', (x, y, .015), (x, y, 4.0), .15, 'timber', 'street planting', 8)
            A.foliage('Shelterbelt crown', (x, y, 6.0), (1.6, 1.6, 3.2), detail=1)


def programme():
    x0, x1, y0, y1 = ANCHOR
    for i in range(6):
        x = x0 + 6.0 + i * 5.0
        C.box('Grocery aisle shelving', (x, 16.0, G0 + 1.0), (1.0, 18.0, 2.0), 'pale', 'grocery', 0)
    for i in range(4):
        C.box('Checkout', (-26.0 + i * 3.0, 3.5, G0 + .5), (2.0, .9, 1.0), 'tan', 'grocery', 0)
    for x in (-32.0, -20.0, -8.0):
        for y in (6.0, 18.0, 26.0):
            C.qa_room_light('Sales floor', (x, y, A_ROOF - .6), 150, 5.0)
    C.qa_room_light('Cafe', (-43.0, 7.0, S_ROOF - .5), 70, 3.5)
    for i in range(7):
        x = INLINE[0] + (i + .5) * (INLINE[1] - INLINE[0]) / 7
        C.box('Tenant counter', (x, INLINE[2] + 5.0, G0 + .5), (3.0, .8, 1.0), 'tan', 'tenants', 0)
        C.qa_room_light('Tenant', (x, INLINE[2] + 6.0, S_ROOF - .5), 60, 3.5)
    for i in range(4):
        y = INLINE[2] - (i + .5) * 7.0
        C.box('Tenant counter', (ENDCAP[0] + 5.0, y, G0 + .5), (.8, 3.0, 1.0), 'tan', 'tenants', 0)
        C.qa_room_light('Endcap tenant', (ENDCAP[0] + 6.0, y, S_ROOF - .5), 60, 3.5)


def build():
    site()
    anchor()
    inline_and_endcap()
    programme()
    C.CONTACTS.append(dict(name='Storefront thresholds at slab level under the continuous canopy', grade_m=0))
    C.CONTACTS.append(dict(name='Pylon sign on a brick base at the road verge', grade_m=0))


LIGHT_RIG = dict(key=(-70, -90, 70), fill=(80, -40, 60), rear=(-30, 90, 70), target=(0, 0, 5.0), gain=20.0)
