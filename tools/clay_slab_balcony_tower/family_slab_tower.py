"""Mid-century concrete slab apartment tower with balconies, authored from the locked catalogue
views of west_end_mid_century_tower / variant_0 (midcentury_concrete_slab).

Read from the pixels: a near-square tower of twelve apartment storeys over a recessed glazed
ground floor. Exposed concrete floor slabs run round every storey and project as balcony plates
with glass balustrades on the two outer bays of each face; the centre bay carries a brick
spandrel under a continuous window band; full-height concrete fin walls stand at the bay lines
and the corners. The roof is flat behind a low parapet with a two-storey concrete mechanical
penthouse at the centre-rear and rooftop units. Streets lie to the south (front) and west.
"""
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-slab-balcony-tower'
W, D = 22.0, 22.0
T = .30
G0 = .15
L0 = 4.6                       # ground storey (lobby and retail)
FH = 2.95                      # apartment storey
N = 12
ROOF = L0 + N * FH             # 42.95
PARAPET = ROOF + .70
FIN_U = 3.4                    # fin walls at the bay lines (centre bay about 31 percent of the face)
PLATE = 1.6                    # balcony projection
RECESS = 2.4                   # ground floor set back on the street faces
PENT = (-4.5, 4.5, -1.0, 7.0)  # penthouse footprint
ANNEX = (4.5, 8.0, 1.0, 5.0)   # lower annex beside it
EPS = .002
PALETTE = dict(wall=(.54, .30, .22), joint=(.40, .20, .14), trim=(.16, .17, .18),
    pale=(.70, .68, .64), stone=(.62, .60, .56), roof=(.70, .70, .68), sand=(.58, .56, .52),
    foundation=(.42, .42, .41), glass=(.52, .58, .58), hardware=(.30, .31, .33),
    interior=(.78, .74, .66), floor=(.44, .42, .40), timber=(.40, .28, .16), blue=(.14, .22, .28),
    planting=(.24, .42, .14), soil=(.19, .14, .08), concrete=(.62, .60, .56), accent=(.20, .50, .48),
    membrane=(.72, .72, .70))
STOREYS = [L0 + i * FH for i in range(N)]      # slab top of each apartment storey


def manifest(version):
    h = PARAPET + 6.5
    cams = G.camera_roster(W + 2 * PLATE, D + 2 * PLATE, h, [
        ('facade_close', (-16.0, -24.0, 12.0), (-4.0, -D / 2, 16.0), 45),
        ('architecture_close', (-20.0, -20.0, 30.0), (-8.0, -D / 2, 32.0), 50),
        ('glass_close', (-6.0, -18.0, 20.5), (-2.0, -D / 2, 21.5), 50),
        ('balcony_close', (10.0, -19.0, 24.0), (7.5, -D / 2 - 1.0, 23.5), 45),
        ('fin_contact', (-14.0, -16.0, 2.5), (-5.1, -D / 2 - .8, 3.0), 40),
        ('lobby_entry', (-6.0, -22.0, 2.0), (0.0, -D / 2 + RECESS, 2.2), 45),
        ('roof_penthouse', (-26.0, -30.0, 58.0), (0.0, 3.0, 46.0), 45),
        ('base_corner', (-24.0, -24.0, 4.0), (-W / 2, -D / 2, 5.0), 40),
        ('interior', (-7.0, -4.0, L0 + 6 * FH + 1.6), (-8.0, -D / 2 - 1.5, L0 + 6 * FH + 1.2), 60),
        ('rear_lane', (12.0, 30.0, 4.0), (2.0, D / 2, 3.0), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='west_end_mid_century_tower/variant_0 (midcentury_concrete_slab)',
        measurement_contract=dict(dimensions_m=dict(width=W + 2 * PLATE, depth=D + 2 * PLATE, height=h),
            observed_storeys=N + 1, storey_programme='recessed glazed ground floor with lobby and retail; twelve apartment storeys; mechanical penthouse',
            plan='square 22 x 22 m read from the 600 x 600 px roof in the top view at 0.037 m/px; balcony plates project 1.6 m on the outer bays of every face',
            facade='per face: balcony bay, centre bay with brick spandrel and window band, balcony bay; concrete fin walls at the bay lines and corners; exposed slab edge every storey',
            levels_m=[G0, L0] + STOREYS[1:], roof_m=ROOF, parapet_m=PARAPET, storey_height_m=FH,
            penthouse='9 x 8 m concrete box 6.2 m high at the centre-rear of the roof with a louvre, a door and rooftop units',
            inferred='the oblique balcony stacks read as twelve to thirteen storeys; twelve are authored, the most the 1 MiB clay budget carries with every balcony and window band built; north and east faces repeat the grammar; interiors are teaching assumptions'),
        roof_contract=dict(type='flat membrane behind a 0.7 m parapet; penthouse and rooftop units on curbs', datum_m=ROOF, crowns_m=[PARAPET, ROOF + 6.2, ROOF + 7.0]),
        identity_contract=dict(owner='exposed concrete slab edges with projecting balcony plates and glass balustrades, brick spandrel centre bays, full-height concrete fins, recessed glazed base, rooftop penthouse'),
        material_contract=dict(profile='source-palette clay: warm brick spandrels with recessed courses, board-marked concrete slabs and fins, dark aluminium frames, clear glass balustrades, pale membrane roof', textured_keeper=False),
        programme_contract=dict(storeys=N + 1, ground='lobby, mail room and a corner retail unit behind the recessed glazing', upper='four apartments per floor with living rooms opening onto the balconies', roof='mechanical penthouse'),
        contact_contract=['Grade-zero slab and sidewalks', 'Ground-floor columns from slab to the first floor plate', 'Balcony plates cast with the slab edge band', 'Fin walls from grade to the parapet', 'Penthouse on the roof slab'],
        runtime_contract=dict(scale='fixed_native_only', installation='not installed', review='NOT TESTED'),
        camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])


def hole(name, u, z, w, h, **kw):
    return dict(id=name, u=u, z=z, w=w, h=h, **kw)


class Merge:
    """Collect boxes in face coordinates and flush them as one mesh per role (keeps object count low)."""
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


def glazing(m, f, h, cols=1, rows=1, inset=.14, occupied='apartment', kind='window'):
    """Opening fill: dark frame ring, mullions and one pane, drawn into the merged meshes."""
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
    # The carrier cut (0.30 m) gives the jamb, head and sill returns; frames sit 0.14 m inside it.
    C.OPENINGS.append(dict(id=h['id'], face=f.label, u=u, z=z, width=w, height=hh, kind=kind, clear_wall_cut=True,
        carrier_depth_m=T, frame_inset_m=inset, pane_inset_m=inset + .037, face_origin=list(f.o), face_tangent=list(f.t),
        face_inward=list(f.n), occupied_space=occupied, cols=cols, rows=rows))


def tower_face(f, span, street, inset=0.0, side=False):
    """One face of the apartment storeys: carrier from the first slab to the parapet, three bays per storey."""
    half = span / 2
    holes = []
    for i, zf in enumerate(STOREYS):
        for s in (-1, 1):
            holes.append(hole(f'{f.label} balcony glazing {i}{"L" if s < 0 else "R"}', s * (FIN_U + (half - FIN_U) / 2), zf + .08, half - FIN_U - .9, FH - .45, kind='balcony'))
        holes.append(hole(f'{f.label} window band {i}', 0.0, zf + .78, 2 * FIN_U - 1.0, FH - .78 - .21, kind='band'))
    z0 = L0 - .16
    f.wall(f.label + ' carrier', -half + inset, half - inset - EPS, z0, PARAPET, depth=T, holes=holes)
    m = Merge(f)
    for h in holes:
        if h['kind'] == 'balcony':
            glazing(m, f, h, cols=2, occupied='living room opening onto the balcony', kind='glazed door')
        else:
            glazing(m, f, h, cols=1, occupied='bedrooms')
    # Brick courses on the centre-bay spandrels only.
    for i, zf in enumerate(STOREYS):
        G.brick_courses(f, -FIN_U + .35, FIN_U - .35, zf + .14, zf + .76, [], spacing=.075)
    # Slab edge band every storey and at the roof; balcony plates and balustrades on the outer bays.
    for i, zf in enumerate(STOREYS + [ROOF]):
        if i < N:
            m.box('concrete', 0.0, -.05, zf - .02, span - 2 * EPS, .40, .30)
        else:
            # Thick pale concrete roof slab and parapet band over the brick; side faces butt into the front and rear bands.
            pw = span - 2 * EPS - (2 * (T + .12) if side else 0.0)
            m.box('concrete', 0.0, (T - .25 + .06) / 2, (ROOF - .17 + PARAPET + .02) / 2, pw, T + .25 + .06, PARAPET + .02 - (ROOF - .17))
        if i < N:
            for s in (-1, 1):
                bw = half - FIN_U - .3
                uc = s * (FIN_U + .15 + bw / 2)
                m.box('concrete', uc, -(PLATE + .23) / 2, zf - .07, bw, PLATE - .23, .22)
                m.box('glass', uc, -PLATE + .06, zf + .565, bw - .10, .02, 1.05)
                m.box('hardware', uc, -PLATE + .06, zf + 1.115, bw - .06, .06, .05)
    m.flush('facade')
    # Fin walls at the bay lines, grade to parapet, projecting past the balcony plates' inner half.
    for u in (-FIN_U, FIN_U):
        f.part('Fin wall', u, -(PLATE - .05) / 2 + .05, (G0 + ROOF + .10) / 2, .32, PLATE - .05 + .10, ROOF + .10 - G0, 'concrete', 'fins', 0)


def corner_fins():
    for sx in (-1, 1):
        for sy in (-1, 1):
            x = sx * (W / 2 + PLATE / 2 - .22); y = sy * (D / 2 - .16)
            C.box('Corner fin', (x, y, (G0 + ROOF + .10) / 2), (PLATE + .18, .32, ROOF + .10 - G0), 'concrete', 'fins', 0)
            C.box('Corner fin return', (sx * (W / 2 - .16), sy * (D / 2 + PLATE / 2 - .22), (G0 + ROOF + .10) / 2), (.32, PLATE + .18, ROOF + .10 - G0), 'concrete', 'fins', 0)


def ground_floor(f_front, f_right, f_rear, f_left):
    """Recessed glazed lobby and retail on the two street faces; brick walls with a garage door on the others."""
    # Recessed carriers butt into each other at the south-west corner and into the brick ground walls at their far ends.
    spans = {f_front: (-W / 2 + RECESS + T, W / 2 - T), f_left: (-D / 2 + T, D / 2 - RECESS)}
    for f in (f_front, f_left):
        lo, hi = spans[f]
        g = C.Face(f.o + f.n * RECESS, f.t, f.n, f.label + ' recessed ground')
        mid = (lo + hi) / 2
        holes = []
        if f is f_front:
            holes.append(hole('Lobby doors', mid, G0, 2.4, 2.6, kind='door'))
            holes.append(hole(g.label + ' storefront L', (lo + .6 + mid - 1.6) / 2, G0, (mid - 1.6) - (lo + .6), L0 - .9))
            holes.append(hole(g.label + ' storefront R', (mid + 1.6 + hi - .6) / 2, G0, (hi - .6) - (mid + 1.6), L0 - .9))
        else:
            holes.append(hole(g.label + ' storefront L', (lo + .6 + mid - .5) / 2, G0, (mid - .5) - (lo + .6), L0 - .9))
            holes.append(hole(g.label + ' storefront R', (mid + .5 + hi - .6) / 2, G0, (hi - .6) - (mid + .5), L0 - .9))
        g.wall(g.label + ' carrier', lo, hi, G0, L0 - .3, depth=T, role='concrete', holes=holes)
        m = Merge(g)
        for h in holes:
            if h.get('kind') == 'door':
                glazing(m, g, h, cols=2, occupied='lobby', kind='glazed door')
            else:
                glazing(m, g, h, cols=3, rows=1, occupied='lobby and retail', kind='storefront')
        m.flush('ground glazing')
        if f is f_front:
            f.part('Entrance canopy', -FIN_U - 2.0, -.95, L0 - 1.3, 6.0, 2.3, .22, 'concrete', 'canopy', 0)
            f.part('Entrance canopy upstand', -FIN_U - 2.0, -2.0, L0 - 1.1, 6.0, .20, .40, 'concrete', 'canopy', 0)
            C.CONTACTS.append(dict(name='Lobby doors at slab level under a cantilevered canopy', grade_m=0, canopy_m=L0 - 1.3))
        for u in (-FIN_U, 0.0, FIN_U):
            f.part('Ground column', u, RECESS * .35, (G0 + L0 - .3) / 2, .55, .55, L0 - .3 - G0, 'concrete', 'ground columns', 0)
    for f, span, door, inset in ((f_rear, W, True, 0.0), (f_right, D, False, T)):
        half = span / 2
        holes = [hole(f.label + ' garage door', -4.0, G0, 4.6, 3.2, kind='door')] if door else [hole(f.label + ' ground window', 2.0, 1.2, 3.0, 1.8)]
        f.wall(f.label + ' ground carrier', -half + inset, half - inset - EPS, G0, L0 - .3 + EPS, depth=T, holes=holes)
        G.brick_courses(f, -half + inset + .02, half - inset - .02, G0, L0 - .3, holes, spacing=.075)
        m = Merge(f)
        for h in holes:
            if h.get('kind') == 'door':
                m.box('pale', h['u'], .22, h['z'] + h['h'] / 2, h['w'] - .06, .05, h['h'] - .02)
                for k in range(1, 6):
                    m.box('hardware', h['u'], .19, h['z'] + k * h['h'] / 6, h['w'] - .10, .02, .03)
                C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='roll-up door', clear_wall_cut=True,
                    carrier_depth_m=T, frame_inset_m=.19, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='parking entry'))
            else:
                glazing(m, f, h, cols=2, occupied='service room')
        m.flush('ground')
    C.CONTACTS.append(dict(name='Ground columns from the slab to the first floor plate under the recessed street faces', grade_m=0, top_m=L0 - .3))


def floors_and_roof():
    C.box('Ground slab', (0, 0, G0 / 2), (W + 2 * PLATE, D + 2 * PLATE, G0), 'foundation', 'foundation', 0)
    for i, zf in enumerate(STOREYS[1:], 1):
        C.box(f'Floor plate {i}', (0, 0, zf - .15), (W - 2 * T, D - 2 * T, .30), 'floor', 'occupied floors', 0)
        C.qa_room_light(f'Front apartments {i}', (0, -D / 2 + 3.5, zf + FH - .4), 90, 4.0)
        C.qa_room_light(f'Rear apartments {i}', (0, D / 2 - 3.5, zf + FH - .4), 60, 4.0)
    C.qa_room_light('Front apartments 0', (0, -D / 2 + 3.5, L0 + FH - .4), 90, 4.0)
    C.box('First floor plate', (0, 0, L0 - .15), (W - 2 * T, D - 2 * T, .30), 'floor', 'occupied floors', 0)
    C.box('Roof slab', (0, 0, ROOF - .12), (W - 2 * T, D - 2 * T, .24), 'floor', 'roof', 0)
    C.box('Roof membrane', (0, 0, ROOF + .004), (W - 2 * T - .02, D - 2 * T - .02, .008), 'membrane', 'roof', 0)
    # Furnished storey behind the interior camera.
    zf = STOREYS[6]
    A.sofa(-8.0, -6.5, zf); A.desk(-3.0, -8.0, zf); A.bed(5.0, -7.0, zf)
    # Mechanical penthouse at the centre-rear, two storeys, with a louvre, a door and an elevator overrun.
    x0, x1, y0, y1 = PENT
    C.box('Penthouse', ((x0 + x1) / 2, (y0 + y1) / 2, ROOF + 3.1), (x1 - x0, y1 - y0, 6.2), 'concrete', 'penthouse', 0)
    C.box('Penthouse louvre', ((x0 + x1) / 2 - 1.5, y0 - .04, ROOF + 4.2), (2.0, .08, 1.6), 'hardware', 'penthouse', 0)
    for k in range(6):
        C.box('Penthouse louvre blade', ((x0 + x1) / 2 - 1.5, y0 - .10, ROOF + 3.5 + k * .27), (1.9, .06, .06), 'pale', 'penthouse', 0)
    C.box('Penthouse door', ((x0 + x1) / 2 + 2.0, y0 - .03, ROOF + 1.1), (1.0, .06, 2.2), 'trim', 'penthouse', 0)
    C.box('Elevator overrun', (x1 - 2.0, y1 - 2.0, ROOF + 6.6), (3.5, 3.5, .8), 'concrete', 'penthouse', 0)
    ax0, ax1, ay0, ay1 = ANNEX
    C.box('Penthouse annex', ((ax0 + ax1) / 2, (ay0 + ay1) / 2, ROOF + 1.6), (ax1 - ax0, ay1 - ay0, 3.2), 'concrete', 'penthouse', 0)
    C.box('Annex door', (ax1 + .03, (ay0 + ay1) / 2, ROOF + 1.1), (.06, 1.0, 2.2), 'trim', 'penthouse', 0)
    for x, y in ((-7.5, -6.0), (7.0, -7.0), (-7.5, 6.0)):
        C.box('Rooftop unit curb', (x, y, ROOF + .12), (2.2, 1.6, .24), 'pale', 'rooftop plant', 0)
        C.box('Rooftop unit', (x, y, ROOF + .24 + .55), (2.0, 1.4, 1.1), 'hardware', 'rooftop plant', 0)
    C.rod('Roof vent', (-2.0, -6.0, ROOF), (-2.0, -6.0, ROOF + 1.4), .22, 'hardware', 'rooftop plant', 10)
    C.CONTACTS.append(dict(name='Penthouse and rooftop units bearing on the roof slab', roof_m=ROOF))


def site():
    ext = 6.0
    C.box('South sidewalk', (0, -D / 2 - PLATE - ext / 2, .0075), (W + 2 * PLATE + 2 * ext, ext, .015), 'foundation', 'sidewalk', 0)
    C.box('West sidewalk', (-W / 2 - PLATE - ext / 2, 0, .0075), (ext, D + 2 * PLATE, .015), 'foundation', 'sidewalk', 0)
    C.box('Kerb south', (0, -D / 2 - PLATE - ext + .06, .06), (W + 2 * PLATE + 2 * ext, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb west', (-W / 2 - PLATE - ext + .06, 0, .06), (.12, D + 2 * PLATE, .12), 'stone', 'sidewalk', 0)
    C.box('Rear lane', (0, D / 2 + PLATE + 3.0, .0075), (W + 2 * PLATE + 2 * ext, 6.0, .015), 'foundation', 'lane', 0)
    C.box('East lawn', (W / 2 + PLATE + 3.0, 0, .02), (6.0, D + 2 * PLATE, .04), 'planting', 'landscape', 0)
    for x in (-8.0, 8.0):
        C.box('Planter', (x, -D / 2 - PLATE - 1.0, .3), (3.0, .9, .6), 'concrete', 'landscape', 0)
        C.box('Planter soil', (x, -D / 2 - PLATE - 1.0, .62), (2.8, .7, .04), 'planting', 'landscape', 0)
    for x, y in ((-14.0, -D / 2 - PLATE - 4.2), (-W / 2 - PLATE - 4.2, 7.0)):
        street_tree(x, y)


def street_tree(x, y, z=.015, height=7.0, spread=1.5):
    C.rod('Street tree trunk', (x, y, z), (x, y, z + height * .55), .14, 'timber', 'street planting', 8)
    for dx, dy in ((-.5, -.2), (.5, -.1), (.0, .5)):
        tip = (x + dx * spread, y + dy * spread, z + height * .72)
        C.rod('Street tree branch', (x, y, z + height * .5), tip, .06, 'timber', 'street planting', 6)
        A.foliage('Street tree crown', tip, (.9 * spread, .9 * spread, 1.3), detail=1)


def build():
    site()
    floors_and_roof()
    f_front, f_right, f_rear, f_left = A.faces(W, D)
    for f, span, street, inset, side in ((f_front, W, True, 0.0, False), (f_left, D, True, T, True), (f_right, D, False, T, True), (f_rear, W, False, 0.0, False)):
        tower_face(f, span, street, inset, side)
    corner_fins()
    ground_floor(f_front, f_right, f_rear, f_left)
    C.CONTACTS.append(dict(name='Balcony plates cast with the slab edge band on every apartment storey', storeys=N, projection_m=PLATE))
    C.CONTACTS.append(dict(name='Fin walls and corner fins from grade to the parapet', top_m=PARAPET))


LIGHT_RIG = dict(key=(-50, -60, 70), fill=(60, -30, 50), rear=(-20, 60, 60), target=(0, 0, 22.0), gain=10.0)
