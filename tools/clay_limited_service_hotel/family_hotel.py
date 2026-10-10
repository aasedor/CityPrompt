"""Four-storey limited-service highway hotel, authored from the locked catalogue views of
highway_motor_hotel / variant_2 (hotel_limited_service).

Read from the pixels: an L-plan four-storey block of beige and charcoal EIFS panels with
paired punched guest-room windows, a dark accent band under the parapet, a full-height
glazed lobby tower at the south-east corner, two glass-roofed porte-cocheres on stone-clad
piers (east and south), a one-storey glazed breakfast and pool wing with a rooflight at the
south-west, a white membrane roof with rooftop units, a parking court to the west and
north, a drive loop and a pylon sign toward the road on the east.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G
from contract import subtract_openings

SLUG = 'clay-limited-service-hotel'
T = .30
G0 = .15
LV = [4.0, 7.2, 10.4]              # upper floors
ROOF, CROWN = 13.6, 14.3
SB = (-16.0, 16.0, -20.0, 0.0)     # south block
NWG = (-6.4, 14.0, 0.0, 20.0)      # north wing
WG = (-28.0, -9.4, -23.0, -4.5)    # one-storey wing
WG_ROOF, WG_CROWN = 4.8, 5.3
TOWER = (9.0, 16.0, -20.0, -13.0)  # glazed lobby tower footprint
TOWER_H = 15.2
CANOPY_Z = 4.6
LOT = (-36.0, 28.0, -33.0, 26.0)   # site extent
EPS = .002
PALETTE = dict(wall=(.58, .52, .40), joint=(.46, .41, .32), trim=(.08, .08, .085),
    pale=(.70, .70, .68), stone=(.50, .45, .38), roof=(.80, .80, .78), sand=(.62, .57, .46),
    foundation=(.30, .30, .30), glass=(.50, .55, .54), hardware=(.09, .09, .095),
    interior=(.74, .70, .60), floor=(.40, .40, .39), timber=(.40, .30, .20), blue=(.14, .22, .28),
    planting=(.46, .40, .20), soil=(.19, .14, .08), charcoal=(.22, .22, .23), accent=(.10, .16, .34),
    cap=(.14, .14, .15), membrane=(.80, .80, .78))


def manifest(version):
    h = TOWER_H + .4
    cams = G.camera_roster(LOT[1] - LOT[0], LOT[3] - LOT[2], h, [
        ('facade_close', (36.0, -2.0, 5.0), (16.0, -6.0, 5.5), 45),
        ('architecture_close', (30.0, -36.0, 13.0), (12.0, -20.0, 12.0), 50),
        ('glass_close', (30.0, -4.0, 6.0), (16.0, -6.0, 6.0), 50),
        ('porte_cochere', (34.0, -20.0, 2.5), (20.0, -12.5, 3.5), 40),
        ('lobby_tower', (26.0, -40.0, 6.0), (12.5, -20.0, 7.0), 40),
        ('wing_contact', (-34.0, -38.0, 4.0), (-18.0, -23.0, 4.0), 40),
        ('parapet_corner', (26.0, -28.0, 17.0), (16.0, -20.0, 13.8), 40),
        ('roof_plant', (-10.0, -36.0, 24.0), (2.0, -8.0, 14.0), 45),
        ('interior', (30.0, -16.5, 2.2), (12.0, -16.5, 2.0), 30),
        ('rear_entry', (-14.0, 34.0, 3.0), (4.0, 20.0, 2.4), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='highway_motor_hotel/variant_2 (hotel_limited_service)',
        measurement_contract=dict(dimensions_m=dict(width=LOT[1] - LOT[0], depth=LOT[3] - LOT[2], height=h),
            observed_storeys=4, storey_programme='lobby level and three guest-room floors; one-storey wing; fixed authored assembly',
            plan='L-plan four-storey block (south block 32 x 20 m, north wing 20.4 x 20 m read from the 590 x 540 px top view at 0.075 m/px), one-storey wing 18.6 x 18.5 m at the south-west, glazed lobby tower 7 x 7 m at the south-east corner',
            windows='paired punched guest-room windows per 4 m bay on every floor; beige EIFS with charcoal sections; accent band under the parapet',
            canopies='glass-roofed porte-cocheres on stone piers projecting east (10 m) and south (10 m) from the lobby corner',
            levels_m=[G0] + LV, roof_m=ROOF, parapet_m=CROWN - ROOF, wing_roof_m=WG_ROOF, tower_m=TOWER_H,
            site='parking court west and north, drive loop east, pylon sign at the road',
            inferred='32 m south block calibrates the bay cadence; the west and north faces repeat the window grammar; interiors are teaching assumptions.'),
        roof_contract=dict(type='flat white membrane behind a dark parapet; rooftop units; one-storey wing roof with a rooflight; glass canopies', datum_m=ROOF, crowns_m=[CROWN, TOWER_H]),
        identity_contract=dict(owner='beige and charcoal EIFS L-block with paired windows, accent band, glazed lobby tower, stone-piered glass porte-cocheres, low glazed wing'),
        material_contract=dict(profile='source-palette clay: beige and charcoal EIFS with recessed panel joints, dark parapet cap and accent band, warm stone pier cladding, dark window frames, white membrane', textured_keeper=False),
        programme_contract=dict(storeys=4, ground='lobby, breakfast room and pool wing, ground-floor rooms', upper='double-loaded guest-room corridors', stairs='straight supported flights in the lobby tower'),
        contact_contract=['Grade-zero slab and lot', 'Lobby doors at slab level under the canopies', 'Canopy slabs on stone piers and the facade', 'Wing roof seated below the south block windows', 'Tower seated on the slab and tied to the block', 'Rooftop units on curbs'],
        runtime_contract=dict(scale='fixed_native_only', installation='not installed', review='NOT TESTED'),
        camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])


def hole(name, u, z, w, h, **kw):
    return dict(id=name, u=u, z=z, w=w, h=h, **kw)


def joints(f, lo, hi, z0, z1, holes, spacing=1.0):
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


def punched(f, name, u, z, w, h):
    """Punched window as a wall section: one lined reveal-and-frame ring through the carrier, pane behind it."""
    inset = .16
    ring = f.part(name + ' reveal and frame', u, (inset + .07) / 2, z + h / 2, w, inset + .07, h, 'trim', 'window frames', 0)
    f.cut(ring, name + ' frame clear', u, z + .07, w - .14, h - .14, inset + .07)
    f.part(name + ' pane', u, inset + .06, z + h / 2, w - .14, .008, h - .14, 'glass', 'window glazing', 0)
    C.OPENINGS.append(dict(id=name, face=f.label, u=u, z=z, width=w, height=h, kind='window', clear_wall_cut=True,
        carrier_depth_m=T, frame_inset_m=inset, pane_inset_m=inset + .06, face_origin=list(f.o), face_tangent=list(f.t),
        face_inward=list(f.n), occupied_space='guest room behind carrier', cols=1, rows=1))


def lined(f, h, inset=.14, role='trim'):
    d = inset / 2 + .005
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    for s in (-1, 1):
        f.part('Reveal jamb liner', u + s * (w / 2 - .011), d, z + hh / 2, .022, inset + .01, hh, role, 'reveals', 0)
    f.part('Reveal head liner', u, d, z + hh - .011, w, inset + .01, .022, role, 'reveals', 0)
    f.part('Reveal sill liner', u, d, z + .011, w, inset + .01, .022, role, 'reveals', 0)


def room_rows(lo, hi, floors, exposed=None, z_ground=1.0):
    """Paired windows per 4 m bay between lo and hi for the given floor datums."""
    holes = []
    n = max(1, int((hi - lo) // 4.0))
    margin = ((hi - lo) - n * 4.0) / 2
    for i in range(n):
        c = lo + margin + 2.0 + i * 4.0
        for lvl in floors:
            if exposed and not exposed(c, lvl):
                continue
            z = (z_ground if lvl == G0 else lvl + .9)
            for s in (-1, 1):
                holes.append(hole(f'Room window {c:+.1f} {lvl:.1f} {s}', c + s * .75, z, 1.0, 1.5))
    return holes


def elevation(f, lo, hi, holes, charcoal=None, extra=(), z1=CROWN):
    """EIFS elevation: carrier, panel joints, punched windows, accent band and parapet cap."""
    f.wall(f.label + ' carrier', lo, hi, G0, z1, depth=T, holes=holes + list(extra))
    joints(f, lo + .2, hi - .2, G0 + EPS, ROOF - 1.2 if z1 == CROWN else z1 - .5, holes + list(extra))
    for h in holes:
        punched(f, h['id'], h['u'], h['z'], h['w'], h['h'])
    if charcoal:
        for a, b in charcoal:
            f.part('Charcoal panel field', (a + b) / 2, -.012, (G0 + ROOF - 1.2) / 2, b - a, .024, ROOF - 1.2 - G0, 'charcoal', 'charcoal panels', 0)
    if z1 == CROWN:
        f.part('Accent band', (lo + hi) / 2, -.02, ROOF - .6, hi - lo - 2 * EPS, .04, 1.2 - .02, 'accent', 'accent band', 0)
        f.part('Parapet cap band', (lo + hi) / 2, -.025, (ROOF + CROWN) / 2, hi - lo - 2 * EPS, .05, CROWN - ROOF - .02, 'cap', 'parapet cap', 0)
    f.part('Base course', (lo + hi) / 2, -.02, .30, hi - lo - 2 * EPS, .04, .60, 'stone', 'base course', 0)


def face(x0, x1, y0, y1, side, label):
    if side == 'south': return C.Face(((x0 + x1) / 2, y0, 0), (1, 0, 0), (0, 1, 0), label)
    if side == 'north': return C.Face(((x0 + x1) / 2, y1, 0), (-1, 0, 0), (0, -1, 0), label)
    if side == 'east': return C.Face((x1, (y0 + y1) / 2, 0), (0, 1, 0), (-1, 0, 0), label)
    return C.Face((x0, (y0 + y1) / 2, 0), (0, -1, 0), (1, 0, 0), label)


def blocks():
    sx0, sx1, sy0, sy1 = SB
    nx0, nx1, ny0, ny1 = NWG
    wx0, wx1, wy0, wy1 = WG
    tx0, tx1, ty0, ty1 = TOWER
    # South block, east face (u = y): exposed y -20..0; the tower covers y -20..-13 (its own glass).
    f = face(*SB, 'east', 'south block east')
    lo = ty1 - (sy0 + sy1) / 2 + EPS
    holes = room_rows(lo + .2, 10.0 - T, [G0] + LV)
    elevation(f, lo, 10.0 - T, holes, charcoal=[(2.0, 6.0)])
    # South block, south face (u = x): exposed x -9.4..16 at ground (wing covers west part) and x -16..9 above; tower occupies x 9..16 at ground and above.
    f = face(*SB, 'south', 'south block south')
    def south_exposed(c, l):
        if c > tx0: return False
        if l == G0 and c < wx1 + .6: return False
        return True
    holes = room_rows(-16.0, 9.0, [G0] + LV, exposed=south_exposed)
    elevation(f, -16.0, tx0 - EPS, holes, charcoal=[(-12.0, -8.0)])
    # South block, west face (u = -y): ground exposed only for y -4.5..0; upper floors exposed all along.
    f = face(*SB, 'west', 'south block west')
    holes = room_rows(-10.0 + T, 10.0 - T, [G0] + LV, exposed=lambda c, l: (l not in (G0, LV[0])) or (c < -10.0 + 4.5 - 1.0))
    elevation(f, -10.0 + T, 10.0 - T, holes)
    # South block, north face (u = -x): exposed for x 14..16 and x -16..-6.4 (north wing covers the rest).
    f = face(*SB, 'north', 'south block north')
    holes = room_rows(6.4, 16.0, [G0] + LV)
    elevation(f, -16.0, 16.0, holes)
    # North wing: east, north and west faces.
    f = face(*NWG, 'east', 'north wing east')
    holes = room_rows(-10.0 + T, 10.0 - T, [G0] + LV)
    elevation(f, -10.0 + T, 10.0 - T, holes, charcoal=[(-9.0, -3.0), (3.0, 9.0)])
    f = face(*NWG, 'north', 'north wing north')
    holes = room_rows(-10.2, 10.2, [G0] + LV, exposed=lambda c, l: not (l == G0 and abs(c) < 2.5))
    door = hole('Rear entry doors', 0.0, G0, 2.4, 2.8, kind='door')
    elevation(f, -10.2, 10.2, holes, extra=[door])
    f.window(door['id'], door['u'], door['z'], door['w'], door['h'], cols=2, rows=1, frame='trim', depth=T, sill=False, kind='glazed door')
    lined(f, door)
    f.part('Rear entry canopy', 0.0, -.9, door['z'] + door['h'] + .25, 4.0, 1.8, .16, 'cap', 'rear entry', 0)
    f = face(*NWG, 'west', 'north wing west')
    holes = room_rows(-10.0 + T, 10.0 - T, [G0] + LV)
    elevation(f, -10.0 + T, 10.0 - T, holes, charcoal=[(-3.0, 3.0)])
    # One-storey wing: south, west and north faces, plus the short east face south of the block.
    for side, lo, hi, label in (('south', -(wx1 - wx0) / 2, (wx1 - wx0) / 2, 'wing south'), ('west', -(wy1 - wy0) / 2 + T, (wy1 - wy0) / 2 - T, 'wing west'),
                                ('north', -(wx1 - wx0) / 2 + (wx1 - sx0) + EPS, (wx1 - wx0) / 2, 'wing north')):
        f = face(*WG, side, label)
        n = max(1, int((hi - lo) // 4.2))
        glz = [hole(f'{label} glazing {i}', lo + (hi - lo) / 2 + (i - (n - 1) / 2) * 4.2, .9, 3.2, 2.6) for i in range(n)]
        f.wall(label + ' carrier', lo, hi, G0, WG_CROWN, depth=T, holes=glz)
        joints(f, lo + .2, hi - .2, G0 + EPS, WG_ROOF - .2, glz)
        for h in glz:
            f.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=3, rows=2, frame='trim', depth=T, sill=False)
            lined(f, h)
        f.part('Wing parapet cap band', (lo + hi) / 2, -.025, (WG_ROOF + WG_CROWN) / 2, hi - lo - 2 * EPS, .05, WG_CROWN - WG_ROOF - .02, 'cap', 'parapet cap', 0)
        f.part('Base course', (lo + hi) / 2, -.02, .30, hi - lo - 2 * EPS, .04, .60, 'stone', 'base course', 0)
    f = face(*WG, 'east', 'wing east')
    lo, hi = -(wy1 - wy0) / 2 + T, -(wy1 - wy0) / 2 + (sy0 - wy0) - EPS
    f.wall('wing east carrier', lo, hi, G0, WG_CROWN, depth=T, role='wall')
    f.part('Wing parapet cap band', (lo + hi) / 2, -.025, (WG_ROOF + WG_CROWN) / 2, hi - lo - 2 * EPS, .05, WG_CROWN - WG_ROOF - .02, 'cap', 'parapet cap', 0)


def tower():
    """Glazed lobby tower at the south-east corner: columns, slabs, curtain glazing on the south and east, doors."""
    x0, x1, y0, y1 = TOWER
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for xx, yy in ((x0 + .25, y0 + .25), (x1 - .25, y0 + .25), (x1 - .25, y1 - .25), (x0 + .25, y1 - .25)):
        C.box('Tower corner column', (xx, yy, G0 + (TOWER_H - G0) / 2), (.45, .45, TOWER_H - G0), 'trim', 'lobby tower', 0)
    for z in LV + [TOWER_H - .4]:
        C.box('Tower floor plate', (cx, cy, z - .10), (x1 - x0 - .6, y1 - y0 - .6, .20), 'floor', 'lobby tower', 0)
    for (px, py, tx, ty, span, label) in ((cx, y0 + .03, 1, 0, x1 - x0 - .5, 'south'), (x1 - .03, cy, 0, 1, y1 - y0 - .5, 'east')):
        C.box(f'Tower {label} glazing', (px, py, G0 + (TOWER_H - G0 - .4) / 2), (max(.012, span * abs(tx)), max(.012, span * abs(ty)), TOWER_H - G0 - .4), 'glass', 'tower glazing', 0)
        n = max(2, round(span / 1.5))
        for i in range(1, n):
            mx, my = px + tx * (-span / 2 + i * span / n), py + ty * (-span / 2 + i * span / n)
            C.box(f'Tower {label} mullion', (mx, my, G0 + (TOWER_H - G0 - .4) / 2), (max(.07, .12 * abs(ty)), max(.07, .12 * abs(tx)), TOWER_H - G0 - .4), 'trim', 'tower frame', 0)
        for z in LV + [CANOPY_Z + .6]:
            C.box(f'Tower {label} transom', (px, py, z), (max(.12, span * abs(tx)), max(.12, span * abs(ty)), .14), 'trim', 'tower frame', 0)
    C.box('Tower head', (cx, cy, TOWER_H - .2), (x1 - x0, y1 - y0, .40), 'cap', 'lobby tower', 0)
    C.box('Tower roof cap', (cx, cy, TOWER_H + .05), (x1 - x0 + .1, y1 - y0 + .1, .10), 'cap', 'lobby tower', 0)
    # Lobby doors in the south glazing and the east glazing at grade.
    for (px, py, tx, ty) in ((cx, y0 - .02, 1, 0), (x1 + .02, cy, 0, 1)):
        frame = C.box('Lobby door frame', (px, py, G0 + 1.5), (max(.08, 2.6 * tx), max(.08, 2.6 * ty), 3.0), 'trim', 'lobby doors', 0)
        C.cut_box(frame, 'Lobby door clear', (px, py, G0 + 1.42), (max(.3, 2.3 * tx), max(.3, 2.3 * ty), 2.74))
        C.box('Lobby door leaf glazing', (px, py, G0 + 1.42), (max(.012, 2.3 * tx), max(.012, 2.3 * ty), 2.72), 'glass', 'lobby doors', 0)
        C.box('Lobby door meeting stile', (px, py, G0 + 1.42), (max(.05, .05 * ty) if tx else .05, max(.05, .05 * tx) if ty else .05, 2.72), 'trim', 'lobby doors', 0)
        C.rod('Lobby door pull', (px + tx * .2 - ty * .05, py + ty * .2 + tx * .05, G0 + .9), (px + tx * .2 - ty * .05, py + ty * .2 + tx * .05, G0 + 1.5), .018, 'hardware', 'lobby doors', 8)
    C.qa_room_light('Lobby', (cx, cy, 3.6), 90, 3.0)
    C.qa_room_light('Lobby stair', (cx, cy, 9.0), 60, 3.0)
    G.stair('Lobby stair', cx - 1.5, y0 + .8, G0, LV[0], length=5.2, width=1.1, landing_gap=.12)


def canopies():
    """Glass-roofed porte-cocheres on stone-clad piers, east and south of the lobby corner."""
    for (x0, x1, y0, y1, label) in ((16.0 + EPS, 26.0, -16.5, -9.0, 'east'), (8.6, 16.0, -30.0, -20.0 - EPS, 'south')):
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        frame = C.box(f'Canopy {label} fascia frame', (cx, cy, CANOPY_Z + .25), (x1 - x0, y1 - y0, .50), 'cap', 'canopies', 0)
        C.cut_box(frame, f'Canopy {label} opening', (cx, cy, CANOPY_Z + .25), (x1 - x0 - .8, y1 - y0 - .8, .8))
        C.box(f'Canopy {label} glazing', (cx, cy, CANOPY_Z + .46), (x1 - x0 - .8, y1 - y0 - .8, .03), 'glass', 'canopies', 0)
        nb = 4 if label == 'east' else 3
        for i in range(1, nb):
            if label == 'east':
                C.beam(f'Canopy {label} rafter', (x0 + .4 + i * (x1 - x0 - .8) / nb, y0 + .4, CANOPY_Z + .40), (x0 + .4 + i * (x1 - x0 - .8) / nb, y1 - .4, CANOPY_Z + .40), .08, .14, 'trim', 'canopies')
            else:
                C.beam(f'Canopy {label} rafter', (x0 + .4, y0 + .4 + i * (y1 - y0 - .8) / nb, CANOPY_Z + .40), (x1 - .4, y0 + .4 + i * (y1 - y0 - .8) / nb, CANOPY_Z + .40), .08, .14, 'trim', 'canopies')
        piers = ((x1 - .6, y0 + .6), (x1 - .6, y1 - .6)) if label == 'east' else ((x0 + .6, y0 + .6), (x1 - .6, y0 + .6))
        for px, py in piers:
            C.box('Stone-clad pier', (px, py, (G0 + CANOPY_Z) / 2), (.9, .9, CANOPY_Z - G0), 'stone', 'canopies', 0)
            C.box('Pier cap', (px, py, CANOPY_Z - .02), (1.0, 1.0, .06), 'cap', 'canopies', 0)
    C.CONTACTS.append(dict(name='Porte-cochere canopies on stone piers and the lobby facade', soffit_m=CANOPY_Z, piers=4))


def roofs():
    sx0, sx1, sy0, sy1 = SB
    nx0, nx1, ny0, ny1 = NWG
    wx0, wx1, wy0, wy1 = WG
    for (x0, x1, y0, y1, name) in ((sx0 + T, sx1 - T, sy0 + T, sy1 - T, 'South block'), (nx0 + T, nx1 - T, sy1 - T + EPS, ny1 - T, 'North wing')):
        C.box(name + ' roof slab', ((x0 + x1) / 2, (y0 + y1) / 2, ROOF - .12), (x1 - x0, y1 - y0, .24), 'floor', 'roof', 0)
        C.box(name + ' membrane', ((x0 + x1) / 2, (y0 + y1) / 2, ROOF + .004), (x1 - x0 - .02, y1 - y0 - .02, .008), 'membrane', 'roof', 0)
    # Parapet copings on the exposed runs.
    runs = [((sx0, sy0 + T / 2), (TOWER[0], sy0 + T / 2)), ((sx1 - T / 2, TOWER[3]), (sx1 - T / 2, sy1)), ((nx1 + 0, sy1 - T / 2), (sx1, sy1 - T / 2)),
            ((nx1 - T / 2, sy1), (nx1 - T / 2, ny1 - T)), ((nx0, ny1 - T / 2), (nx1, ny1 - T / 2)), ((nx0 + T / 2, sy1), (nx0 + T / 2, ny1 - T)),
            ((sx0, sy1 - T / 2), (nx0, sy1 - T / 2)), ((sx0 + T / 2, sy0 + T), (sx0 + T / 2, sy1 - T))]
    for (ax, ay), (bx, by) in runs:
        if abs(bx - ax) > abs(by - ay):
            C.box('Coping', ((ax + bx) / 2, ay, CROWN + .03), (abs(bx - ax), T + .06, .06), 'cap', 'coping', 0)
        else:
            C.box('Coping', (ax, (ay + by) / 2, CROWN + .03), (T + .06, abs(by - ay) - .064, .06), 'cap', 'coping', 0)
    # Rooftop units.
    for x, y in ((-6.0, -10.0), (4.0, -6.0), (8.0, 12.0), (2.0, 4.0)):
        C.box('Rooftop unit curb', (x, y, ROOF + .15), (2.6, 1.8, .30), 'pale', 'rooftop plant', 0)
        C.box('Rooftop unit', (x, y, ROOF + .30 + .75), (2.4, 1.6, 1.5), 'pale', 'rooftop plant', 0)
        C.rod('Rooftop unit fan', (x - .5, y, ROOF + 1.80), (x - .5, y, ROOF + 1.95), .42, 'hardware', 'rooftop plant', 14)
    for x, y in ((-10.0, -4.0), (10.0, 16.0)):
        C.rod('Roof vent stack', (x, y, ROOF), (x, y, ROOF + 1.2), .18, 'pale', 'rooftop plant', 10)
    # One-storey wing roof: two slabs outside the south block footprint, rooflight, membrane.
    for (x0, x1, y0, y1) in ((wx0 + T, sx0 - EPS, wy0 + T, wy1 - T), (sx0 - EPS, wx1 - T, wy0 + T, sy0 - EPS)):
        C.box('Wing roof slab', ((x0 + x1) / 2, (y0 + y1) / 2, WG_ROOF - .12), (x1 - x0, y1 - y0, .24), 'floor', 'roof', 0)
        C.box('Wing membrane', ((x0 + x1) / 2, (y0 + y1) / 2, WG_ROOF + .004), (x1 - x0 - .02, y1 - y0 - .02, .008), 'membrane', 'roof', 0)
    C.box('Wing rooflight curb', (-22.0, -14.0, WG_ROOF + .25), (5.0, 3.6, .50), 'pale', 'roof', 0)
    C.prism('Wing rooflight glazing', [(-24.4, WG_ROOF + .50), (-22.0, WG_ROOF + 1.3), (-19.6, WG_ROOF + .50), (-19.6, WG_ROOF + .53), (-22.0, WG_ROOF + 1.33), (-24.4, WG_ROOF + .53)], 'y', -15.7, -12.3, 'glass', 'roof')
    wruns = [((wx0, wy0 + T / 2), (wx1, wy0 + T / 2)), ((wx0 + T / 2, wy0 + T), (wx0 + T / 2, wy1 - T)), ((wx0, wy1 - T / 2), (sx0, wy1 - T / 2)), ((wx1 - T / 2, wy0 + T), (wx1 - T / 2, sy0))]
    for (ax, ay), (bx, by) in wruns:
        if abs(bx - ax) > abs(by - ay):
            C.box('Wing coping', ((ax + bx) / 2, ay, WG_CROWN + .03), (abs(bx - ax), T + .06, .06), 'cap', 'coping', 0)
        else:
            C.box('Wing coping', (ax, (ay + by) / 2, WG_CROWN + .03), (T + .06, abs(by - ay) - .064, .06), 'cap', 'coping', 0)


def floors():
    sx0, sx1, sy0, sy1 = SB
    nx0, nx1, ny0, ny1 = NWG
    wx0, wx1, wy0, wy1 = WG
    C.box('Ground slab', ((sx0 + sx1) / 2, (sy0 + ny1) / 2, G0 / 2), (sx1 - sx0, ny1 - sy0, G0), 'foundation', 'foundation', 0)
    C.box('Wing slab', ((wx0 + sx0) / 2, (wy0 + wy1) / 2, G0 / 2), (sx0 - wx0, wy1 - wy0, G0), 'foundation', 'foundation', 0)
    C.box('Wing slab south', ((sx0 + wx1) / 2, (wy0 + sy0) / 2, G0 / 2), (wx1 - sx0, sy0 - wy0, G0), 'foundation', 'foundation', 0)
    C.box('Parking court', ((LOT[0] + sx1) / 2, (LOT[2] + LOT[3]) / 2, .0075), (sx1 - LOT[0], LOT[3] - LOT[2], .015), 'foundation', 'site', 0)
    C.box('Drive loop', ((sx1 + LOT[1]) / 2, (LOT[2] + LOT[3]) / 2, .0075), (LOT[1] - sx1, LOT[3] - LOT[2], .015), 'foundation', 'site', 0)
    C.box('Lawn verge east', (LOT[1] - 1.5, 0, .021), (3.0, LOT[3] - LOT[2], .012), 'planting', 'site', 0)
    C.box('Lawn panel south', (-4.0, -28.0, .021), (18.0, 5.0, .012), 'planting', 'site', 0)
    C.rod('Pylon sign post', (26.0, -30.0, 0), (26.0, -30.0, 6.0), .18, 'cap', 'site', 10)
    C.box('Pylon sign board', (26.0, -30.0, 6.8), (3.0, .3, 1.6), 'accent', 'site', 0)
    for lvl in LV:
        C.box('Guest floor south', ((sx0 + sx1) / 2, (sy0 + sy1) / 2, lvl - .075), (sx1 - sx0 - 2 * T, sy1 - sy0 - 2 * T, .15), 'floor', 'occupied floors', 0)
        C.box('Guest floor north', ((nx0 + nx1) / 2, (sy1 + ny1) / 2, lvl - .075), (nx1 - nx0 - 2 * T, ny1 - sy1 - T, .15), 'floor', 'occupied floors', 0)
    for z in LV:
        for x, y in ((-10.0, -10.0), (2.0, -10.0), (4.0, 10.0)):
            C.qa_room_light('Guest corridor', (x, y, z + 2.9), 60, 3.5)
    for x, y in ((-8.0, -10.0), (-20.0, -14.0), (4.0, 10.0)):
        C.qa_room_light('Ground room', (x, y, LV[0] - .5), 70, 3.5)
    for x, y in ((-10.0, -10.0), (2.0, -10.0), (2.0, 10.0)):
        for z in (G0, LV[1]):
            A.bed(x, y + 3.0, z)
    C.box('Breakfast counter', (-22.0, -8.0, G0 + .5), (4.0, .8, 1.0), 'timber', 'wing', 0)
    C.box('Pool basin', (-22.0, -17.0, G0 + .02), (8.0, 4.0, .04), 'blue', 'wing', 0)
    for i in range(6):
        C.box('Parked car', (LOT[0] + 6.0, -20.0 + i * 6.0, .75), (1.8, 4.4, 1.4), 'charcoal' if i % 2 else 'pale', 'site', 0)
    A.small_tree(LOT[0] + 2.0, 20.0, .015, height=6.0, spread=1.1)


def build():
    floors()
    blocks()
    tower()
    canopies()
    roofs()
    C.CONTACTS.append(dict(name='Lobby doors at slab level under the canopies', grade_m=0, step_m=G0))
    C.CONTACTS.append(dict(name='One-storey wing roof seated against the south block below its windows', roof_m=WG_ROOF))


LIGHT_RIG = dict(key=(-46, -60, 52), fill=(56, -28, 46), rear=(-24, 60, 50), target=(0, -4, 8.0), gain=9.0)
