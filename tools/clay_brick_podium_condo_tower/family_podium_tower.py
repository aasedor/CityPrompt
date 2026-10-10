"""Brick-podium glass condominium tower, authored from the locked catalogue views of
condo_podium_tower / variant_0 (brick_podium_glass_tower).

Read from the pixels: a corner site with streets south and east. A two-storey red-brick podium
fills the lot with double-height storefront glazing between brick piers on the ground floor, a
dark canopy band, ribbon windows with precast sills on the second floor and a precast cornice. A
glass curtain-wall tower of eleven storeys stands flush with the two street faces at the corner;
the podium roof beyond it is an amenity terrace behind a glass balustrade. Balconies project in
vertical stacks on every tower face. A large pale metal mechanical penthouse with louvres sits on
the tower roof behind a guard rail.
"""
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-brick-podium-condo-tower'
PX, PY = (-21.0, 21.0), (-16.0, 16.0)      # podium footprint
TX, TY = (-9.0, 21.0), (-13.0, 8.0)        # tower footprint: flush with the east face, a 3 m terrace strip in front of the south face
T = .30
G0 = .15
L1, PODIUM = 5.0, 9.3                      # second-floor level, podium roof
FH, N = 3.0, 11
TROOF = PODIUM + N * FH                    # 42.3
TPAR = TROOF + .7
PENT = (-5.0, 17.0, -12.0, 4.0)            # penthouse footprint on the tower roof
PENT_H = 4.2
SPANDREL = .62                             # opaque band at each tower floor
MULLION = 1.5
PLATE = 1.5
EPS = .002
PALETTE = dict(wall=(.50, .22, .16), joint=(.36, .16, .12), trim=(.14, .15, .16),
    pale=(.76, .76, .74), stone=(.66, .64, .60), roof=(.70, .68, .64), sand=(.62, .60, .56),
    foundation=(.42, .42, .41), glass=(.50, .58, .60), hardware=(.30, .31, .33),
    interior=(.78, .74, .66), floor=(.44, .42, .40), timber=(.40, .28, .16), blue=(.14, .22, .28),
    planting=(.24, .42, .14), soil=(.19, .14, .08), concrete=(.62, .60, .56), metal=(.80, .80, .78),
    membrane=(.72, .70, .64), spandrel=(.70, .72, .72))
FLOORS = [PODIUM + i * FH for i in range(N)]


def manifest(version):
    h = TPAR + PENT_H + .5
    cams = G.camera_roster(PX[1] - PX[0], PY[1] - PY[0], h, [
        ('facade_close', (0.0, -34.0, 14.0), (6.0, TY[0], 18.0), 45),
        ('architecture_close', (-30.0, -30.0, 12.0), (-9.0, PY[0], 9.3), 50),
        ('glass_close', (12.0, -26.0, 22.0), (14.0, TY[0], 23.0), 50),
        ('podium_retail', (-12.0, -28.0, 2.2), (-6.0, PY[0], 2.8), 45),
        ('podium_setback', (-34.0, 2.0, 16.0), (-12.0, 2.0, 9.6), 45),
        ('balcony_stack', (28.0, -30.0, 24.0), (TX[1], -4.0, 24.0), 45),
        ('roof_crown', (-34.0, -40.0, 60.0), (6.0, -4.0, 44.0), 45),
        ('corner_entry', (30.0, -26.0, 2.2), (TX[1], TY[0], 2.6), 45),
        ('interior', (-3.0, -8.5, FLOORS[5] + 1.6), (-1.0, TY[0] - 1.5, FLOORS[5] + 1.1), 55),
        ('rear_lane', (0.0, 34.0, 5.0), (-4.0, PY[1], 4.0), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='condo_podium_tower/variant_0 (brick_podium_glass_tower)',
        measurement_contract=dict(dimensions_m=dict(width=PX[1] - PX[0], depth=PY[1] - PY[0], height=h),
            observed_storeys=N + 2, storey_programme='double-height retail ground floor, second podium storey, eleven tower storeys, mechanical penthouse',
            plan='podium 42 x 32 m and tower 30 x 21 m read from the top view (podium 640 x 480 px at 0.066 m/px); the tower is flush with the east street face, a balustraded terrace strip runs in front of its south face and the podium roof wraps it on the west and north',
            podium='brick piers on a 5.5 m bay with double-height storefronts, dark canopy band at 4.3 m, ribbon windows with precast sills on the second storey, precast cornice at 9.3 m, glass balustrade on the terrace',
            tower='glass curtain wall with continuous mullions at 1.5 m and a 0.62 m spandrel at every floor; five staggered balcony stacks on the south face and two on the other faces, projecting 1.5 m with glass balustrades; corner columns',
            levels_m=[G0, L1, PODIUM] + FLOORS[1:], roofs_m=[PODIUM, TROOF], parapet_m=TPAR,
            penthouse='22 x 16 m pale metal box 4.2 m high with louvre panels on the tower roof, rooftop units beside it, guard rail at the roof edge',
            inferred='eleven tower storeys counted from the balcony stacks in the front view; north and west faces repeat the grammar; interiors are teaching assumptions'),
        roof_contract=dict(type='flat membranes: podium terrace with pavers and planters, tower roof with gravel behind a 0.7 m parapet and guard rail, penthouse on a curb', datum_m=TROOF, crowns_m=[TPAR, TROOF + PENT_H]),
        identity_contract=dict(owner='red-brick two-storey podium with double-height storefronts and a roof terrace, glass tower flush with the corner, balcony stacks, pale mechanical penthouse'),
        material_contract=dict(profile='source-palette clay: red brick with recessed courses, precast bands, dark storefront frames, clear curtain-wall glass with pale spandrels and mullions, glass balustrades, pale metal penthouse', textured_keeper=False),
        programme_contract=dict(storeys=N + 2, ground='retail units and the residential lobby at the corner', second='amenity and offices', upper='eight apartments per floor around a central core', roof='mechanical penthouse'),
        contact_contract=['Grade-zero slab and sidewalks', 'Tower corner columns from grade to the parapet', 'Balcony plates cast with the floor slabs', 'Terrace balustrade on the podium parapet', 'Penthouse on the tower roof slab'],
        runtime_contract=dict(scale='fixed_native_only', installation='not installed', review='NOT TESTED'),
        camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])


def hole(name, u, z, w, h, **kw):
    return dict(id=name, u=u, z=z, w=w, h=h, **kw)


class Merge:
    def __init__(self, f):
        self.f = f; self.groups = {}

    def box(self, role, u, d, z, w, t, h):
        vs, fs = self.groups.setdefault(role, ([], []))
        o = len(vs)
        vs.extend(self.f.p(u + du * w / 2, d + dd * t / 2, z + dz * h / 2) for dz in (-1, 1) for du, dd in ((-1, -1), (1, -1), (1, 1), (-1, 1)))
        fs.extend(tuple(o + i for i in face) for face in C.BOX_FACES)

    def flush(self, module):
        for role, (vs, fs) in self.groups.items():
            if fs:
                C.mesh(f'{self.f.label} {module} {role}', vs, fs, role, module)
        self.groups = {}


def register(f, h, inset, kind, occupied):
    C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind=kind, clear_wall_cut=True,
        carrier_depth_m=T, frame_inset_m=inset, pane_inset_m=inset + .037, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space=occupied))


def framed(m, f, h, cols=1, rows=1, inset=.14, occupied='room', kind='window'):
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    per = .07
    for s in (-1, 1):
        m.box('trim', u + s * (w / 2 - per / 2), inset, z + hh / 2, per, .10, hh)
    m.box('trim', u, inset, z + hh - per / 2, w - 2 * per, .10, per)
    for i in range(1, cols):
        m.box('trim', u - w / 2 + w * i / cols, inset - .006, z + hh / 2, .05, .09, hh - 2 * per)
    for i in range(1, rows):
        m.box('trim', u, inset - .008, z + hh * i / rows, w - 2 * per, .085, .05)
    m.box('glass', u, inset + .037, z + hh / 2, w - 2 * per - .01, .009, hh - 2 * per - .01)
    register(f, h, inset, kind, occupied)


def tower_face(f, lo, hi, stacks, flush=False, stagger=False):
    """Curtain-wall face: spandrel carrier with one glazed band per storey, continuous mullions, balcony stacks."""
    span = hi - lo
    first = 1.15 if flush else SPANDREL
    holes = [hole(f'{f.label} glazing band {i}', (lo + hi) / 2, zf + (first if i == 0 else SPANDREL), span - 1.0, FH - (first if i == 0 else SPANDREL) - .02, kind='band') for i, zf in enumerate(FLOORS)]
    # On the flush east face the carrier starts above the podium cornice (no coplanar faces with the podium carrier);
    # on the terrace faces it starts at the deck so the envelope is closed down to the terrace.
    z_start = PODIUM + .92 if flush else PODIUM - .02
    f.wall(f.label + ' spandrel carrier', lo, hi - EPS, z_start, TPAR, depth=T, role='spandrel', holes=holes)
    m = Merge(f)
    for h in holes:
        m.box('glass', h['u'], .10, h['z'] + h['h'] / 2, h['w'] - .02, .012, h['h'] - .02)
        register(f, h, .06, 'curtain wall', 'apartments around the core')
    # Continuous mullions proud of the facade, and a cap on each spandrel.
    n = round(span / MULLION)
    for i in range(n + 1):
        u = lo + .5 + (span - 1.0) * i / n
        m.box('trim', u, -.03, (z_start + TPAR) / 2, .08, .12, TPAR - z_start - .02)
    for zf in FLOORS[1:] + [TROOF]:
        m.box('pale', (lo + hi) / 2, -.11, zf + .02, span - 2 * EPS, .12, .10)
    # Balcony stacks: plate, glass balustrade and rail at every storey.
    for si, uc in enumerate(stacks):
        bw = 3.2 if stagger else 3.6
        for fi, zf in enumerate(FLOORS):
            if fi == 0 or (stagger and (fi + si) % 2):
                continue
            m.box('concrete', uc, -(PLATE + .2) / 2, zf + .05, bw, PLATE - .2 + .3, .20)
            m.box('glass', uc, -PLATE + .08, zf + .15 + .525, bw - .08, .02, 1.05)
            m.box('hardware', uc, -PLATE + .08, zf + .15 + 1.05 + .025, bw - .04, .06, .05)
            for e in (-1, 1):
                m.box('glass', uc + e * (bw / 2 - .03), -(PLATE - .2) / 2 - .02, zf + .15 + .525, .02, PLATE - .26, 1.05)
    m.flush('curtain wall')
    f.part('Tower parapet coping', (lo + hi) / 2, T / 2, TPAR + .03, span - 2 * EPS, T + .06, .06, 'pale', 'coping', 0)


def tower():
    x0, x1 = TX; y0, y1 = TY
    south = C.Face(((x0 + x1) / 2, y0, 0), (1, 0, 0), (0, 1, 0), 'tower south')
    east = C.Face((x1, (y0 + y1) / 2, 0), (0, 1, 0), (-1, 0, 0), 'tower east')
    north = C.Face(((x0 + x1) / 2, y1, 0), (-1, 0, 0), (0, -1, 0), 'tower north')
    west = C.Face((x0, (y0 + y1) / 2, 0), (0, -1, 0), (1, 0, 0), 'tower west')
    hw, hd = (x1 - x0) / 2, (y1 - y0) / 2
    tower_face(south, -hw, hw, tuple(-hw + hw * 2 * (k + .5) / 5 for k in range(5)), stagger=True)
    tower_face(north, -hw, hw, (-hw * .5, hw * .5))
    tower_face(east, -hd + T, hd - T, (-hd * .45, hd * .45), flush=True)
    tower_face(west, -hd + T, hd - T, (-hd * .45, hd * .45))
    for x in (x0, x1):
        for y in (y0, y1):
            C.box('Tower corner column', (x, y, (G0 + TPAR) / 2), (.70, .70, TPAR - G0), 'pale', 'tower columns', 0)
    # Floors, core and interiors.
    for i, zf in enumerate(FLOORS):
        C.box(f'Tower floor {i}', ((x0 + x1) / 2, (y0 + y1) / 2, zf - .13), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .26), 'floor', 'occupied floors', 0)
        C.qa_room_light(f'Tower south rooms {i}', ((x0 + x1) / 2, y0 + 4.0, zf + FH - .4), 80, 5.0)
        C.qa_room_light(f'Tower north rooms {i}', ((x0 + x1) / 2, y1 - 4.0, zf + FH - .4), 60, 5.0)
    C.box('Tower core', ((x0 + x1) / 2, (y0 + y1) / 2, (G0 + TROOF) / 2), (8.0, 5.0, TROOF - G0), 'concrete', 'core', 0)
    zf = FLOORS[5]
    for y in (y0 + 7.0,):
        C.box('Party wall', (x0 + 10.0, (y0 + T + y) / 2, zf + FH / 2), (.18, y - y0 - T, FH - .3), 'interior', 'partitions', 0)
        C.box('Party wall', (x0 + 20.0, (y0 + T + y) / 2, zf + FH / 2), (.18, y - y0 - T, FH - .3), 'interior', 'partitions', 0)
    A.sofa(x0 + 15.0, y0 + 2.6, zf); A.bed(x0 + 5.0, y0 + 3.5, zf); A.desk(x0 + 24.0, y0 + 3.0, zf)
    C.box('Tower roof slab', ((x0 + x1) / 2, (y0 + y1) / 2, TROOF - .12), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .24), 'floor', 'roof', 0)
    C.box('Tower roof gravel', ((x0 + x1) / 2, (y0 + y1) / 2, TROOF + .004), (x1 - x0 - 2 * T - .02, y1 - y0 - 2 * T - .02, .008), 'membrane', 'roof', 0)
    # Penthouse and rooftop plant.
    px0, px1, py0, py1 = PENT
    C.box('Penthouse curb', ((px0 + px1) / 2, (py0 + py1) / 2, TROOF + .15), (px1 - px0 + .3, py1 - py0 + .3, .30), 'concrete', 'penthouse', 0)
    C.box('Penthouse', ((px0 + px1) / 2, (py0 + py1) / 2, TROOF + .30 + PENT_H / 2), (px1 - px0, py1 - py0, PENT_H), 'metal', 'penthouse', 0)
    for k in range(5):
        C.box('Penthouse louvre', (px0 + 3.0 + k * 3.6, py0 - .05, TROOF + .30 + PENT_H / 2), (2.4, .10, PENT_H - 1.2), 'hardware', 'penthouse', 0)
    C.box('Penthouse east louvre', (px1 + .05, (py0 + py1) / 2, TROOF + .30 + PENT_H / 2), (.10, 8.0, PENT_H - 1.2), 'hardware', 'penthouse', 0)
    C.box('Penthouse west louvre', (px0 - .05, (py0 + py1) / 2, TROOF + .30 + PENT_H / 2), (.10, 8.0, PENT_H - 1.2), 'hardware', 'penthouse', 0)
    C.box('Penthouse north louvre', ((px0 + px1) / 2, py1 + .05, TROOF + .30 + PENT_H / 2), (12.0, .10, PENT_H - 1.2), 'hardware', 'penthouse', 0)
    C.box('Penthouse roof unit', ((px0 + px1) / 2 + 4.0, (py0 + py1) / 2, TROOF + .30 + PENT_H + .7), (2.4, 1.8, 1.4), 'hardware', 'rooftop plant', 0)
    for x, y in ((px0 + 4.0, py1 + 2.5), (px0 + 12.0, py1 + 2.5)):
        C.box('Rooftop unit', (x, y, TROOF + .9), (2.6, 1.8, 1.6), 'hardware', 'rooftop plant', 0)
    rail_run((x0 + .4, y0 + .4), (x1 - .4, y0 + .4), TPAR); rail_run((x1 - .4, y0 + .4), (x1 - .4, y1 - .4), TPAR)
    rail_run((x1 - .4, y1 - .4), (x0 + .4, y1 - .4), TPAR); rail_run((x0 + .4, y1 - .4), (x0 + .4, y0 + .4), TPAR)
    C.CONTACTS.append(dict(name='Tower corner columns from grade to the parapet; penthouse on a curb on the roof slab', top_m=TPAR))


def rail_run(a, b, z, height=1.05):
    ax, ay = a; bx, by = b
    C.beam('Guard rail', (ax, ay, z + height), (bx, by, z + height), .05, .05, 'hardware', 'guard rails')
    C.beam('Guard rail mid', (ax, ay, z + height * .5), (bx, by, z + height * .5), .03, .03, 'hardware', 'guard rails')
    n = max(1, round(((bx - ax) ** 2 + (by - ay) ** 2) ** .5 / 5.0))
    for i in range(n + 1):
        x = ax + (bx - ax) * i / n; y = ay + (by - ay) * i / n
        C.beam('Guard post', (x, y, z), (x, y, z + height), .05, .05, 'hardware', 'guard rails')


def glass_balustrade(a, b, z, height=1.1, inward=(0, 1)):
    ax, ay = a; bx, by = b
    length = ((bx - ax) ** 2 + (by - ay) ** 2) ** .5
    tx, ty = (bx - ax) / length, (by - ay) / length
    f = C.Face(((ax + bx) / 2, (ay + by) / 2, 0), (tx, ty, 0), (inward[0], inward[1], 0), 'balustrade')
    f.part('Terrace balustrade glass', 0, .0, z + height / 2 + .05, length - .05, .02, height - .05, 'glass', 'terrace', 0)
    f.part('Terrace balustrade rail', 0, .0, z + height + .08, length, .06, .05, 'hardware', 'terrace', 0)


def podium_face(f, lo, hi, corner_lobby=False, lane=False, garage=False):
    """Brick podium elevation: double-height storefronts between piers, canopy band, ribbon windows above, cornice."""
    span = hi - lo
    bay = 5.5
    n = max(2, int(span // bay))
    pitch = span / n
    holes = []
    for i in range(n):
        c = lo + pitch * (i + .5)
        if lane:
            if i == n // 2:
                holes.append(hole(f'{f.label} loading door', c, G0, 4.0, 4.2, kind='door'))
            elif i % 2 == 0:
                holes.append(hole(f'{f.label} ground window {i}', c, 1.4, pitch - 2.2, 2.2))
        elif garage and i == n - 1:
            holes.append(hole(f'{f.label} garage door', c, G0, 4.0, 4.2, kind='door'))
        elif corner_lobby and i == n - 1:
            holes.append(hole(f'{f.label} lobby doors', c + .4, G0, 2.6, 3.0, kind='door'))
            holes.append(hole(f'{f.label} lobby glazing', c + .4, 3.2, pitch - 1.4, L1 - .9 - 3.2))
        else:
            holes.append(hole(f'{f.label} storefront {i}', c, G0, pitch - 1.4, L1 - .6, kind='storefront'))
        holes.append(hole(f'{f.label} ribbon window {i}', c, L1 + 1.0, pitch - 1.8, 2.1))
    f.wall(f.label + ' podium carrier', lo, hi - EPS, G0, PODIUM + .9, depth=T, holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, G0, PODIUM + .9, holes, spacing=.15)
    m = Merge(f)
    for h in holes:
        if h.get('kind') == 'door' and (lane or 'garage' in h['id']):
            m.box('pale', h['u'], .22, h['z'] + h['h'] / 2, h['w'] - .06, .05, h['h'] - .02)
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='roll-up door', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=.19, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='loading'))
        elif h.get('kind') == 'door':
            framed(m, f, h, cols=2, occupied='residential lobby', kind='glazed door')
        elif h.get('kind') == 'storefront':
            framed(m, f, h, cols=3, rows=2, occupied='retail unit', kind='storefront')
        else:
            framed(m, f, h, cols=3, occupied='second-floor amenity and offices')
        if 'ribbon' in h['id']:
            m.box('stone', h['u'], -.05, h['z'] - .06, h['w'] + .30, .36, .12)
    # Canopy band over the storefronts, cornice at the podium roof.
    if not lane:
        m.box('trim', (lo + hi) / 2, -.45, L1 - .55, span - 2 * EPS, .90, .22)
    m.box('stone', (lo + hi) / 2, -.08, PODIUM + .95, span - 2 * EPS, T + .22, .32)
    m.flush('podium')


def podium():
    x0, x1 = PX; y0, y1 = PY
    south = C.Face(((x0 + x1) / 2, y0, 0), (1, 0, 0), (0, 1, 0), 'podium south')
    east = C.Face((x1, (y0 + y1) / 2, 0), (0, 1, 0), (-1, 0, 0), 'podium east')
    north = C.Face(((x0 + x1) / 2, y1, 0), (-1, 0, 0), (0, -1, 0), 'podium north')
    west = C.Face((x0, (y0 + y1) / 2, 0), (0, -1, 0), (1, 0, 0), 'podium west')
    hw, hd = (x1 - x0) / 2, (y1 - y0) / 2
    podium_face(south, -hw, hw, corner_lobby=True)
    podium_face(east, -hd + T, hd - T, garage=True)
    podium_face(north, -hw, hw, lane=True)
    podium_face(west, -hd + T, hd - T)
    C.box('Ground slab', (0, 0, G0 / 2), (x1 - x0, y1 - y0, G0), 'foundation', 'foundation', 0)
    C.box('Second floor', (0, 0, L1 - .13), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .26), 'floor', 'occupied floors', 0)
    C.box('Podium roof slab', (0, 0, PODIUM - .13), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .26), 'floor', 'roof', 0)
    C.box('Terrace pavers', (0, 0, PODIUM + .004), (x1 - x0 - 2 * T - .02, y1 - y0 - 2 * T - .02, .008), 'sand', 'terrace', 0)
    for x in (-15.0, -5.0, 5.0, 15.0):
        C.qa_room_light(f'Retail {x:+.0f}', (x, y0 + 5.0, L1 - .5), 90, 5.0)
        C.qa_room_light(f'Offices {x:+.0f}', (x, y0 + 5.0, PODIUM - .5), 60, 5.0)
    for x in (-12.0, 8.0):
        A.desk(x, y0 + 4.0, L1 + .05)
    # Terrace balustrade on the podium parapet along the west and north, planters, benches.
    z = PODIUM + .9
    glass_balustrade((x0 + .2, y0 + .2), (x0 + .2, y1 - .2), z, inward=(1, 0))
    glass_balustrade((x0 + .2, y1 - .2), (TX[0] - .2, y1 - .2), z, inward=(0, -1))
    glass_balustrade((TX[0] - .2, y1 - .2), (x1 - .2, y1 - .2), z, inward=(0, -1))
    glass_balustrade((TX[0] - .2, y0 + .2), (x1 - .2, y0 + .2), z, inward=(0, 1))
    glass_balustrade((x1 - .2, y0 + .2), (x1 - .2, TY[0] - .2), z, inward=(-1, 0))
    for x in (-4.0, 4.0, 12.0):
        C.box('South terrace planter', (x, TY[0] - 1.4, PODIUM + .3), (2.2, 1.0, .60), 'concrete', 'terrace', 0)
        C.box('South terrace planting', (x, TY[0] - 1.4, PODIUM + .62), (2.0, .8, .04), 'planting', 'terrace', 0)
    for x, y in ((x0 + 3.0, 0.0), (x0 + 3.0, 10.0), (0.0, y1 - 3.0), (8.0, y1 - 3.0)):
        C.box('Terrace planter', (x, y, PODIUM + .35), (2.6, 1.2, .70), 'concrete', 'terrace', 0)
        C.box('Terrace planter soil', (x, y, PODIUM + .72), (2.4, 1.0, .04), 'planting', 'terrace', 0)
        A.shrub(x, y, PODIUM + .72, .7)
    C.box('Terrace bench', (x0 + 6.0, 4.0, PODIUM + .22), (1.8, .5, .44), 'timber', 'terrace', 0)
    C.CONTACTS.append(dict(name='Podium roof terrace with glass balustrade on the parapet, planters bearing on the slab', terrace_m=PODIUM))


def site():
    x0, x1 = PX; y0, y1 = PY
    ext = 6.0
    C.box('South sidewalk', ((x0 + x1) / 2, y0 - ext / 2, .0075), (x1 - x0 + 2 * ext, ext, .015), 'foundation', 'sidewalk', 0)
    C.box('East sidewalk', (x1 + ext / 2, (y0 + y1) / 2, .0075), (ext, y1 - y0, .015), 'foundation', 'sidewalk', 0)
    C.box('Kerb south', ((x0 + x1) / 2, y0 - ext + .06, .06), (x1 - x0 + 2 * ext, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb east', (x1 + ext - .06, (y0 + y1) / 2, .06), (.12, y1 - y0, .12), 'stone', 'sidewalk', 0)
    C.box('Rear lane', ((x0 + x1) / 2, y1 + 3.0, .0075), (x1 - x0 + 2 * ext, 6.0, .015), 'foundation', 'lane', 0)
    C.box('West lot', (x0 - 3.0, (y0 + y1) / 2, .0075), (6.0, y1 - y0, .015), 'foundation', 'lane', 0)
    for x in (-15.0, -4.0, 7.0):
        street_tree(x, y0 - 3.8)
    street_tree(x1 + 3.8, 5.0)


def street_tree(x, y, z=.015, height=7.0, spread=1.5):
    C.rod('Street tree trunk', (x, y, z), (x, y, z + height * .55), .14, 'timber', 'street planting', 8)
    for dx, dy in ((-.5, -.2), (.5, -.1), (.0, .5)):
        tip = (x + dx * spread, y + dy * spread, z + height * .72)
        C.rod('Street tree branch', (x, y, z + height * .5), tip, .06, 'timber', 'street planting', 6)
        A.foliage('Street tree crown', tip, (.9 * spread, .9 * spread, 1.3), detail=1)


def build():
    site()
    podium()
    tower()
    C.CONTACTS.append(dict(name='Tower flush with the south and east podium faces; podium terrace wraps the west and north', tower_m=list(TX) + list(TY)))


LIGHT_RIG = dict(key=(-60, -70, 70), fill=(70, -30, 50), rear=(-20, 70, 60), target=(0, 0, 22.0), gain=11.0)
