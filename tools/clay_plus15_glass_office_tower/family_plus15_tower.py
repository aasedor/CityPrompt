"""Contemporary glass office tower with a Plus 15 bridge, authored from the locked catalogue views of
calgary_plus_15_connected_tower / variant_2 (plus15_contemporary_glass).

Read from the pixels: a square curtain-wall tower on a downtown corner. Every office floor reads
as a pale spandrel band under a dark vision band divided by closely spaced mullions; pale corner
columns run the full height. The ground floor is a double-height glazed lobby recessed behind a
perimeter colonnade. An enclosed glazed Plus 15 bridge leaves the west end of the south face at
the second level and crosses the street on piers. The roof carries a green roof around an
L-shaped glazed and louvred mechanical penthouse with rooftop units in its yard.
"""
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-plus15-glass-office-tower'
W = D = 36.0
T = .30
G0 = .15
L1 = 6.4                     # lobby storey (double height)
FH, N = 3.65, 16
ROOF = L1 + N * FH           # 64.8
PAR = ROOF + 1.2
SPANDREL = 1.05
MULLION = 1.5
COL = 1.0                    # colonnade column
RECESS = 3.2                 # lobby glazing behind the colonnade
BRIDGE_X = (-13.0, -8.6)     # Plus 15 bridge leaves the south face here
BRIDGE_Z = (4.6, 7.8)
BRIDGE_LEN = 24.0
PENT = [(-9.0, 9.0, -2.0, 10.0), (-9.0, 1.0, -10.0, -2.0)]   # L-shaped penthouse
PENT_H = 5.2
EPS = .002
PALETTE = dict(wall=(.74, .75, .74), joint=(.60, .61, .60), trim=(.78, .79, .78),
    pale=(.80, .80, .78), stone=(.70, .69, .66), roof=(.78, .78, .76), sand=(.64, .62, .58),
    foundation=(.44, .44, .43), glass=(.30, .36, .40), hardware=(.30, .31, .33),
    interior=(.80, .78, .72), floor=(.46, .45, .43), timber=(.40, .28, .16), blue=(.14, .22, .28),
    planting=(.30, .42, .18), soil=(.22, .17, .10), concrete=(.68, .66, .62), metal=(.82, .83, .82),
    membrane=(.84, .84, .82), lightglass=(.56, .64, .66))
FLOORS = [L1 + i * FH for i in range(N)]


def manifest(version):
    h = PAR + PENT_H + .5
    cams = G.camera_roster(W, D + 10.0, h, [
        ('facade_close', (-10.0, -40.0, 20.0), (0.0, -D / 2, 24.0), 45),
        ('architecture_close', (-34.0, -34.0, 14.0), (-W / 2, -D / 2, 10.0), 50),
        ('glass_close', (8.0, -30.0, 30.0), (10.0, -D / 2, 31.0), 50),
        ('plus15_bridge', (-30.0, -36.0, 6.0), (-10.8, -D / 2 - 10.0, 6.2), 45),
        ('lobby_entry', (-6.0, -36.0, 2.4), (2.0, -D / 2 + RECESS, 3.0), 45),
        ('curtain_grid', (26.0, -30.0, 40.0), (W / 2, -6.0, 42.0), 50),
        ('roof_terrace', (-50.0, -50.0, 82.0), (-6.0, 2.0, 66.0), 45),
        ('crown_penthouse', (30.0, -46.0, 76.0), (0.0, 2.0, 68.0), 45),
        ('interior', (-4.0, 4.0, FLOORS[8] + 1.6), (-6.0, -D / 2 - 1.0, FLOORS[8] + 1.3), 60),
        ('rear_service', (10.0, 40.0, 4.0), (0.0, D / 2, 3.5), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='calgary_plus_15_connected_tower/variant_2 (plus15_contemporary_glass)',
        measurement_contract=dict(dimensions_m=dict(width=W, depth=D + BRIDGE_LEN, height=h),
            observed_storeys=N + 1, storey_programme='double-height lobby on a colonnade, sixteen office floors, mechanical penthouse',
            plan='square 36 x 36 m read from the 520 x 520 px roof in the top view at 0.069 m/px; the Plus 15 bridge leaves the west end of the south face and crosses the street southward',
            facade='every floor: 1.05 m pale spandrel band and a 2.6 m dark vision band with mullions at 1.5 m; pale corner columns and a parapet band; lobby glazing recessed 3.2 m behind a colonnade of 1 m columns on a 6 m bay',
            levels_m=[G0, L1] + FLOORS[1:], roof_m=ROOF, parapet_m=PAR, storey_height_m=FH,
            bridge='enclosed glazed bridge 4.4 m wide from 4.6 to 7.8 m, 24 m long on two piers',
            roof='green roof beds around an L-shaped glazed and louvred penthouse 5.2 m high with rooftop units in its yard',
            inferred='sixteen office floors read from the spandrel bands in the oblique view (16 to 18); north and west faces repeat the grammar; interiors are teaching assumptions'),
        roof_contract=dict(type='flat membrane with vegetated beds behind a 1.2 m parapet band; penthouse on a curb', datum_m=ROOF, crowns_m=[PAR, ROOF + PENT_H + .3]),
        identity_contract=dict(owner='pale spandrel bands and close mullions over dark glass, corner columns, recessed double-height lobby on a colonnade, Plus 15 bridge, green roof with glazed penthouse'),
        material_contract=dict(profile='source-palette clay: pale aluminium spandrels and mullions, dark reflective glass, pale concrete columns, pale metal penthouse with louvres, green roof beds', textured_keeper=False),
        programme_contract=dict(storeys=N + 1, ground='lobby, elevator bank and retail behind the colonnade', upper='open office floors around a central core', roof='mechanical penthouse and amenity green roof'),
        contact_contract=['Grade-zero slab and sidewalks', 'Colonnade columns from the slab to the first floor plate', 'Corner columns from grade to the parapet', 'Bridge bearing on the tower face and two street piers', 'Penthouse on a curb on the roof slab'],
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


def framed(m, f, h, cols=1, rows=1, inset=.14, occupied='room', kind='window', frame='hardware'):
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    per = .07
    for s in (-1, 1):
        m.box(frame, u + s * (w / 2 - per / 2), inset, z + hh / 2, per, .10, hh)
    m.box(frame, u, inset, z + hh - per / 2, w - 2 * per, .10, per)
    for i in range(1, cols):
        m.box(frame, u - w / 2 + w * i / cols, inset - .006, z + hh / 2, .05, .09, hh - 2 * per)
    for i in range(1, rows):
        m.box(frame, u, inset - .008, z + hh * i / rows, w - 2 * per, .085, .05)
    m.box('lightglass', u, inset + .037, z + hh / 2, w - 2 * per - .01, .009, hh - 2 * per - .01)
    register(f, h, inset, kind, occupied)


def tower_face(f, lo, hi):
    span = hi - lo
    holes = [hole(f'{f.label} vision band {i}', (lo + hi) / 2, zf + SPANDREL, span - 1.4, FH - SPANDREL - .02, kind='band') for i, zf in enumerate(FLOORS)]
    f.wall(f.label + ' spandrel carrier', lo, hi - EPS, L1 - .32, PAR, depth=T, role='pale', holes=holes)
    m = Merge(f)
    for h in holes:
        m.box('glass', h['u'], .10, h['z'] + h['h'] / 2, h['w'] - .02, .012, h['h'] - .02)
        register(f, h, .06, 'curtain wall', 'open office floor')
    n = round((span - 1.4) / MULLION)
    for i in range(n + 1):
        u = lo + .7 + (span - 1.4) * i / n
        m.box('metal', u, -.04, (L1 - .32 + PAR) / 2, .09, .14, PAR - L1 + .30)
    for zf in FLOORS[1:] + [ROOF]:
        m.box('metal', (lo + hi) / 2, -.05, zf - .02, span - 2 * EPS, .12, .10)
    m.flush('curtain wall')
    f.part('Parapet band', (lo + hi) / 2, -.03, PAR - .6 + .02, span - 2 * EPS, T + .08, 1.2, 'pale', 'coping', 0)


def lobby_face(f, lo, hi, doors=False, bridge=False):
    """Recessed double-height lobby glazing behind the colonnade."""
    g = C.Face(f.o + f.n * RECESS, f.t, f.n, f.label + ' lobby')
    span = hi - lo
    holes = []
    n = 3
    for i in range(n):
        c = lo + span * (i + .5) / n
        w = span / n - 1.2
        if doors and i == 1:
            holes.append(hole(g.label + ' doors', c, G0, 3.6, 3.0, kind='door'))
            holes.append(hole(g.label + ' glazing over doors', c, 3.2, w, L1 - .6 - 3.2))
            for s in (-1, 1):
                holes.append(hole(g.label + f' door side glazing {s}', c + s * (1.8 + (w - 3.6) / 4), G0, (w - 3.6) / 2 - .2, 3.0))
        else:
            holes.append(hole(g.label + f' glazing {i}', c, G0, w, L1 - .6))
    g.wall(g.label + ' carrier', lo + RECESS, hi - RECESS - EPS, G0, L1 - .32, depth=T, role='concrete', holes=holes)
    m = Merge(g)
    for h in holes:
        if h.get('kind') == 'door':
            framed(m, g, h, cols=3, occupied='lobby', kind='glazed door')
        else:
            framed(m, g, h, cols=4, rows=2 if h['h'] > 4 else 1, occupied='lobby and retail', kind='storefront')
    m.flush('lobby glazing')
    for i in range(7):
        u = lo + .5 + (span - 1.0) * i / 6
        f.part('Colonnade column', u, RECESS * .3, (G0 + L1 - .32) / 2, COL, COL, L1 - .32 - G0, 'concrete', 'colonnade', 0)
    f.part('First floor edge', 0.0, RECESS / 2, L1 - .16, span - 2 * EPS, RECESS, .32, 'concrete', 'colonnade', 0)


def bridge():
    x0, x1 = BRIDGE_X; z0, z1 = BRIDGE_Z
    y0 = -D / 2; y1 = y0 - BRIDGE_LEN
    xc = (x0 + x1) / 2; yc = (y0 + y1) / 2
    C.box('Bridge deck', (xc, yc, z0 + .2), (x1 - x0, BRIDGE_LEN, .40), 'concrete', 'plus15 bridge', 0)
    C.box('Bridge roof', (xc, yc, z1 - .15), (x1 - x0 + .2, BRIDGE_LEN, .30), 'metal', 'plus15 bridge', 0)
    for s in (-1, 1):
        x = xc + s * ((x1 - x0) / 2 - .02)
        C.box('Bridge glazing', (x, yc, (z0 + .4 + z1 - .3) / 2), (.03, BRIDGE_LEN - .4, z1 - .3 - z0 - .4), 'lightglass', 'plus15 bridge', 0)
        for k in range(1, 8):
            C.box('Bridge mullion', (x, y0 - k * BRIDGE_LEN / 8, (z0 + z1) / 2), (.10, .08, z1 - z0 - .4), 'metal', 'plus15 bridge', 0)
    C.box('Bridge end wall', (xc, y1 + .15, (z0 + z1) / 2), (x1 - x0 + .2, .30, z1 - z0 + .1), 'concrete', 'plus15 bridge', 0)
    for y in (y0 - 7.0, y0 - 17.0):
        C.box('Bridge pier', (xc, y, (G0 + z0) / 2), (1.0, 1.0, z0 - G0), 'concrete', 'plus15 bridge', 0)
    C.CONTACTS.append(dict(name='Plus 15 bridge bearing on the south face and two street piers', level_m=z0))


def roof_and_penthouse():
    C.box('Roof slab', (0, 0, ROOF - .12), (W - 2 * T, D - 2 * T, .24), 'floor', 'roof', 0)
    C.box('Roof membrane', (0, 0, ROOF + .004), (W - 2 * T - .02, D - 2 * T - .02, .008), 'membrane', 'roof', 0)
    for (x0, x1, y0, y1) in ((-15.5, -11.0, -15.0, 15.0), (11.0, 15.5, -15.0, 15.0), (-11.0, 11.0, 11.0, 15.0), (-11.0, 11.0, -15.0, -11.0)):
        C.box('Green roof bed', ((x0 + x1) / 2, (y0 + y1) / 2, ROOF + .18), (x1 - x0, y1 - y0, .36), 'soil', 'green roof', 0)
        C.box('Green roof planting', ((x0 + x1) / 2, (y0 + y1) / 2, ROOF + .40), (x1 - x0 - .2, y1 - y0 - .2, .08), 'planting', 'green roof', 0)
    for (x0, x1, y0, y1) in PENT:
        C.box('Penthouse', ((x0 + x1) / 2, (y0 + y1) / 2, ROOF + .3 + PENT_H / 2), (x1 - x0, y1 - y0, PENT_H), 'metal', 'penthouse', 0)
    for s, y in ((-1, PENT[0][2]), (1, PENT[0][3])):
        C.box('Penthouse glazing', (0.0, y + s * .06, ROOF + .3 + PENT_H / 2 + .3), (16.0, .08, PENT_H - 1.8), 'lightglass', 'penthouse', 0)
    C.box('Penthouse west louvre', (PENT[0][0] - .06, 4.0, ROOF + .3 + PENT_H / 2), (.08, 10.0, PENT_H - 1.6), 'hardware', 'penthouse', 0)
    for x, y in ((4.0, -6.0), (7.0, -6.0)):
        C.box('Rooftop unit', (x, y, ROOF + .9), (2.2, 2.2, 1.6), 'hardware', 'rooftop plant', 0)
        C.rod('Rooftop fan', (x, y, ROOF + 1.7), (x, y, ROOF + 1.9), .7, 'metal', 'rooftop plant', 14)
    C.CONTACTS.append(dict(name='Penthouse and green roof beds bearing on the roof slab', roof_m=ROOF))


def floors_and_site():
    C.box('Ground slab', (0, 0, G0 / 2), (W, D, G0), 'foundation', 'foundation', 0)
    for i, zf in enumerate(FLOORS):
        C.box(f'Office floor {i}', (0, 0, zf - .13), (W - 2 * T, D - 2 * T, .26), 'floor', 'occupied floors', 0)
        if i % 2 == 0:
            C.qa_room_light(f'Offices south {i}', (0, -D / 2 + 6.0, zf + FH - .4), 120, 7.0)
            C.qa_room_light(f'Offices north {i}', (0, D / 2 - 6.0, zf + FH - .4), 90, 7.0)
    C.box('Core', (0, 0, (G0 + ROOF) / 2), (12.0, 9.0, ROOF - G0), 'concrete', 'core', 0)
    C.qa_room_light('Lobby', (0, -8.0, L1 - .8), 140, 8.0)
    zf = FLOORS[8]
    for x in (-10.0, -4.0, 4.0, 10.0):
        A.desk(x, -D / 2 + 3.5, zf + .05)
    for x in (-8.0, 8.0):
        A.desk(x, -D / 2 + 9.0, zf + .05)
    for x in (-10.0, 6.0):
        A.sofa(x, -D / 2 + 6.0, G0)
    C.box('Reception desk', (3.0, -6.0, G0 + .55), (4.0, .9, 1.1), 'timber', 'lobby', 0)
    for x, y in ((-W / 2 - .35, -D / 2 - .35), (W / 2 + .35, -D / 2 - .35), (-W / 2 - .35, D / 2 + .35), (W / 2 + .35, D / 2 + .35)):
        C.box('Corner column', (x, y, (G0 + PAR) / 2), (1.0, 1.0, PAR - G0), 'pale', 'corner columns', 0)
    ext = 8.0
    for name, loc, size in (('South sidewalk', (0, -D / 2 - ext / 2, .0075), (W + 2 * ext, ext, .015)), ('North sidewalk', (0, D / 2 + ext / 2, .0075), (W + 2 * ext, ext, .015)),
                            ('West sidewalk', (-W / 2 - ext / 2, 0, .0075), (ext, D, .015)), ('East sidewalk', (W / 2 + ext / 2, 0, .0075), (ext, D, .015))):
        C.box(name, loc, size, 'foundation', 'sidewalk', 0)
    C.box('South street', (0, -D / 2 - ext - 10.0, .004), (W + 2 * ext, 20.0, .008), 'hardware', 'street', 0)
    C.box('Far sidewalk', (0, -D / 2 - ext - 20.0 - 3.0, .0075), (W + 2 * ext, 6.0, .015), 'foundation', 'sidewalk', 0)
    for x in (-12.0, 2.0, 14.0):
        street_tree(x, -D / 2 - 5.5)
    street_tree(W / 2 + 5.5, 6.0)


def street_tree(x, y, z=.015, height=7.0, spread=1.5):
    C.rod('Street tree trunk', (x, y, z), (x, y, z + height * .55), .14, 'timber', 'street planting', 8)
    for dx, dy in ((-.5, -.2), (.5, -.1), (.0, .5)):
        tip = (x + dx * spread, y + dy * spread, z + height * .72)
        C.rod('Street tree branch', (x, y, z + height * .5), tip, .06, 'timber', 'street planting', 6)
        A.foliage('Street tree crown', tip, (.9 * spread, .9 * spread, 1.3), detail=1)


def build():
    floors_and_site()
    f_front, f_right, f_rear, f_left = A.faces(W, D)
    for f, inset in ((f_front, 0.0), (f_rear, 0.0), (f_right, T), (f_left, T)):
        tower_face(f, -W / 2 + inset, W / 2 - inset)
    lobby_face(f_front, -W / 2, W / 2, doors=True, bridge=True)
    lobby_face(f_left, -D / 2 + T, D / 2 - T)
    lobby_face(f_right, -D / 2 + T, D / 2 - T)
    lobby_face(f_rear, -W / 2, W / 2)
    bridge()
    roof_and_penthouse()
    C.CONTACTS.append(dict(name='Corner columns from grade to the parapet; colonnade columns from the slab to the first floor edge', top_m=PAR))


LIGHT_RIG = dict(key=(-80, -90, 100), fill=(90, -40, 70), rear=(-30, 90, 90), target=(0, 0, 32.0), gain=14.0)
