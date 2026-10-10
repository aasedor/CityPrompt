"""Converted brick mill mixed-use block, authored from the locked catalogue views of
industrial_brick_mixed_use / variant_0 (industrial_brick_original_mill).

Read from the pixels: a corner block of four storeys in red brick with streets south and west.
Segmental-arched shopfronts with dark frames fill the ground floor between brick piers; three
upper storeys carry segmental-arched windows in recessed panels between full-height pilasters,
a stone sill band over the ground floor and a dentil cornice under the parapet. A slate roof
pitches from a ridge along the long axis to raked gable parapets on the short faces; a glazed
rooftop pavilion with a terrace sits on the front slope over the western bays; a tall square
brick chimney rises at the north-east corner; rooflights sit on the rear slope.
"""
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-arched-mill-mixed-use'
W, D = 20.0, 22.0                # near-square block: gable faces south and north, four-bay faces along the west street and the rear
T = .34
G0 = .15
LEVELS = [4.6, 8.2, 11.8]
EAVE = 15.4
PAR = 16.0
RIDGE = 19.0
BAYS_LONG = 4
BAYS_GABLE = 4
PIL = .9                       # pilaster width
PAV = (-6.8, 8.7, 7.0, 2.9)     # rooftop pavilion y0, y1 along the west slope (73% of the ridge, open slate to the south), depth from the parapet, front wall height
DECK = (-7.2, D / 2 - T - .3)     # level deck under the pavilion with a railed terrace beyond its north end
CHIMNEY = (W / 2 - .9, -D / 2 + 7.0)    # on the rear wall line, a third of the way up from the street gable
EPS = .002
PALETTE = dict(wall=(.56, .30, .20), joint=(.40, .22, .14), trim=(.12, .12, .13),
    pale=(.72, .68, .60), stone=(.64, .60, .52), roof=(.30, .31, .34), sand=(.60, .56, .48),
    foundation=(.42, .42, .41), glass=(.50, .56, .58), hardware=(.28, .29, .31),
    interior=(.78, .74, .66), floor=(.44, .42, .40), timber=(.40, .28, .16), blue=(.14, .22, .28),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.62, .60, .56), metal=(.62, .64, .66),
    membrane=(.70, .70, .68))


def manifest(version):
    h = RIDGE + 8.0
    cams = G.camera_roster(W, D, h, [
        ('facade_close', (-26.0, -8.0, 6.0), (-W / 2, 0.0, 7.0), 45),
        ('architecture_close', (-24.0, -26.0, 14.0), (-W / 2, -D / 2, 13.5), 50),
        ('glass_close', (-16.0, -6.0, 2.2), (-W / 2, -4.0, 2.4), 50),
        ('arched_windows', (-6.0, -24.0, 9.0), (-4.0, -D / 2, 9.5), 45),
        ('corner_entry', (-24.0, -24.0, 2.4), (-W / 2, -D / 2, 2.6), 45),
        ('roof_pavilion', (-38.0, -26.0, 26.0), (-6.0, -2.0, 18.0), 45),
        ('chimney_contact', (26.0, -26.0, 24.0), (CHIMNEY[0], CHIMNEY[1], 19.0), 45),
        ('shopfront', (-16.0, 4.0, 1.8), (-W / 2, 8.0, 2.2), 45),
        ('interior', (-2.0, -4.0, LEVELS[1] + 1.6), (-W / 2 - 1.0, -6.0, LEVELS[1] + 1.4), 60),
        ('rear_yard', (30.0, 10.0, 6.0), (W / 2, 3.0, 5.0), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='industrial_brick_mixed_use/variant_0 (industrial_brick_original_mill)',
        measurement_contract=dict(dimensions_m=dict(width=W, depth=D, height=h),
            observed_storeys=4, storey_programme='retail ground floor behind arched shopfronts; three loft storeys; glazed rooftop pavilion',
            plan='22 x 20 m near-square corner block read from the top view and the four-bay rhythm of both street faces; the eaves face runs along the west street and the gable face along the south street; ridge along the long axis',
            facade='four bays on every face; brick pilasters 0.9 m between recessed panels; segmental-arched shopfronts 3.3 x 3.8 m; arched windows 2.4 x 2.7 m on each upper storey; stone sill band at 4.6 m; dentil cornice at 15.4 m',
            levels_m=[G0] + LEVELS, eave_m=EAVE, parapet_m=PAR, ridge_m=RIDGE,
            roof='slate planes to a ridge at 19 m; raked gable parapets on the south and north faces; glazed pavilion 15.5 x 7 m cut into the west slope over a level deck, open slate to the south and a railed terrace beyond its north end; chimney 2.2 m square to 26 m on the rear wall line in the southern third; four rooflights on the east slope',
            inferred='the north gable and the east (rear) face are not visible in any source and repeat the grammar with a loading door; interiors are teaching assumptions'),
        roof_contract=dict(type='pitched slate with gable parapets; glazed pavilion on the front slope; chimney through the rear slope', datum_m=EAVE, crowns_m=[RIDGE, RIDGE + 7.0]),
        identity_contract=dict(owner='red-brick mill with arched shopfronts and arched windows between pilasters, dentil cornice, slate roof with raked gables, glazed rooftop pavilion, tall corner chimney'),
        material_contract=dict(profile='source-palette clay: red brick with recessed courses, pale stone band and copings, dark metal frames, dark slate, glazed pavilion', textured_keeper=False),
        programme_contract=dict(storeys=4, ground='retail and cafe units with the residential lobby at the corner', upper='loft apartments', roof='shared rooftop pavilion and terrace'),
        contact_contract=['Grade-zero slab and sidewalks', 'Pilasters from the stone band to the cornice', 'Roof planes bearing on the eaves walls inside the parapet', 'Pavilion bearing on a level deck over the front slope', 'Chimney from grade through the rear slope'],
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


def framed(m, f, h, cols=1, rows=1, inset=.16, occupied='room', kind='window'):
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    per = .07
    for s in (-1, 1):
        m.box('trim', u + s * (w / 2 - per / 2), inset, z + hh / 2, per, .10, hh)
    m.box('trim', u, inset, z + hh - per / 2, w - 2 * per, .10, per)
    m.box('trim', u, inset, z + per / 2, w - 2 * per, .10, per)
    for i in range(1, cols):
        m.box('trim', u - w / 2 + w * i / cols, inset - .006, z + hh / 2, .05, .09, hh - 2 * per)
    for i in range(1, rows):
        m.box('trim', u, inset - .008, z + hh * i / rows, w - 2 * per, .085, .05)
    m.box('glass', u, inset + .037, z + hh / 2, w - 2 * per - .01, .009, hh - 2 * per - .01)
    register(f, h, inset, kind, occupied)


def arch_fill(f, u, z_top, w, rise, module='arches'):
    """Brick spandrel filling the top corners of a rectangular cut so the head reads as a segmental arch."""
    pts = [(-w / 2, z_top), (w / 2, z_top), (w / 2, z_top - rise)]
    for k in range(1, 7):
        x = w / 2 - w * k / 7
        pts.append((x, z_top - rise + rise * (1 - (2 * x / w) ** 2)))
    pts.append((-w / 2, z_top - rise))
    f.panel('Segmental arch spandrel', [(u + a, b) for a, b in pts], -.025, T + .02, 'wall', module)


def elevation(f, lo, hi, bays, blind=(), ground='shops', gable=False):
    """Brick elevation: pilastered bays with arched openings on every storey; optional raked gable above the cornice."""
    span = hi - lo
    pitch = span / bays
    holes = []
    for i in range(bays):
        c = lo + pitch * (i + .5)
        if i in blind:
            continue
        if ground == 'shops':
            holes.append(hole(f'{f.label} shopfront {i}', c, G0, pitch - 2 * PIL + .2, 3.8, kind='shop'))
        elif ground == 'rear' and i == bays // 2:
            holes.append(hole(f'{f.label} loading door', c, G0, 3.0, 3.6, kind='door'))
        else:
            holes.append(hole(f'{f.label} ground window {i}', c, 1.0, pitch - 2 * PIL - .4, 2.6))
        for k, zl in enumerate(LEVELS):
            holes.append(hole(f'{f.label} window {i}-{k}', c, zl + .55, 2.4, 2.7))
    top = PAR
    f.wall(f.label + ' carrier', lo, hi - EPS, G0, top, depth=T, holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, G0, top, holes, spacing=.30)
    m = Merge(f)
    for h in holes:
        if h.get('kind') == 'shop':
            framed(m, f, h, cols=3, rows=1, occupied='shop', kind='storefront')
            arch_fill(f, h['u'], h['z'] + h['h'], h['w'], .45)
        elif h.get('kind') == 'door':
            m.box('pale', h['u'], .24, h['z'] + h['h'] / 2 - .02, h['w'] - .20, .05, h['h'] - .10)
            for sgn in (-1, 1):
                m.box('trim', h['u'] + sgn * (h['w'] / 2 - .05), .14, h['z'] + h['h'] / 2, .10, .20, h['h'])
            m.box('trim', h['u'], .14, h['z'] + h['h'] - .05, h['w'] - .20, .20, .10)
            m.box('stone', h['u'], .08, h['z'] + .03, h['w'] + .20, .40, .06)
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='roll-up door', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=.19, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='loading'))
        else:
            framed(m, f, h, cols=2, rows=1, occupied='loft apartment')
            arch_fill(f, h['u'], h['z'] + h['h'], h['w'], .32)
            m.box('stone', h['u'], -.04, h['z'] - .06, h['w'] + .24, T + .14, .12)
    # Pilasters (proud), recessed-panel reveal lines, stone band, dentil cornice, coping.
    for i in range(bays + 1):
        u = lo + pitch * i
        if i == 0: u += PIL / 2 - .01
        elif i == bays: u -= PIL / 2 - .01
        m.box('wall', u, -.06, (LEVELS[0] + EAVE) / 2, PIL, .12 + .04, EAVE - LEVELS[0] - 2 * EPS)
    m.box('stone', (lo + hi) / 2, -.07, LEVELS[0] + .08, span - 2 * EPS, T + .20, .28)
    m.box('stone', (lo + hi) / 2, -.09, EAVE - .18, span - 2 * EPS, T + .24, .36)
    for i in range(int(span / .6)):
        m.box('wall', lo + .3 + i * .6, -.14, EAVE - .50, .30, .14, .22)
    if gable:
        hw = span / 2
        f.panel('Gable parapet', [(-hw, top - EPS), (hw, top - EPS), (0, RIDGE + .5)], 0, T, 'wall', 'gables')
        for s in (-1, 1):
            C.beam('Gable coping', f.p(s * hw, -.04, top + .02), f.p(0, -.04, RIDGE + .52), .20, T + .08, 'stone', 'coping')
    else:
        m.box('stone', (lo + hi) / 2, T / 2, top + .03, span - 2 * EPS, T + .10, .06)
    m.flush('facade')


def roof():
    y0, y1 = -D / 2 + T, D / 2 - T
    t = .22
    west = C.prism('Slate plane west', [(-W / 2 + .2, EAVE), (0, RIDGE), (0, RIDGE - t), (-W / 2 + .2, EAVE - t)], 'y', y0, y1, 'roof', 'main roof')
    C.prism('Slate plane east', [(W / 2 - .2, EAVE), (0, RIDGE), (0, RIDGE - t), (W / 2 - .2, EAVE - t)], 'y', y0, y1, 'roof', 'main roof')
    C.beam('Ridge', (0, y0, RIDGE + .03), (0, y1, RIDGE + .03), .20, .10, 'metal', 'main roof')
    for zl in LEVELS:
        C.box(f'Floor {zl:.1f}', (0, 0, zl - .14), (W - 2 * T, D - 2 * T, .28), 'floor', 'occupied floors', 0)
        C.qa_room_light(f'West lofts {zl:.1f}', (-W / 2 + 4.0, -6.0, zl + 3.0), 90, 5.0)
        C.qa_room_light(f'East lofts {zl:.1f}', (W / 2 - 4.0, 6.0, zl + 3.0), 70, 5.0)
    C.box('Ground slab', (0, 0, G0 / 2), (W, D, G0), 'foundation', 'foundation', 0)
    C.qa_room_light('Shops', (-W / 2 + 4.0, -4.0, LEVELS[0] - .6), 110, 6.0)
    zl = LEVELS[1]
    A.sofa(-5.5, -4.0, zl); A.bed(-6.0, 2.0, zl); A.desk(-6.0, -9.0, zl + .05)
    C.box('Loft partition', (-5.0, -1.0, zl + 1.6), (8.0, .16, 3.2), 'interior', 'partitions', 0)
    # Rooftop pavilion cut into the west slope: level deck, glazed box with a metal frame, flat roof just above the ridge.
    py0, py1, depth, ph = PAV
    dy0, dy1 = DECK
    x0 = -W / 2 + .6; x1 = x0 + depth
    zd = EAVE + .9
    C.cut_box(west, 'Pavilion roof cut', ((x0 + .9 + x1) / 2, (dy0 + dy1) / 2, (EAVE + RIDGE) / 2), (x1 - x0 - .9, dy1 - dy0, RIDGE - EAVE + 2.0))
    C.box('Pavilion deck', ((x0 + x1) / 2, (dy0 + dy1) / 2, zd - .15), (depth + .6, dy1 - dy0, .30), 'concrete', 'pavilion', 0)
    C.box('Pavilion base', ((x0 + x1) / 2 - .3, (dy0 + dy1) / 2, (EAVE - .3 + zd - .3) / 2), (depth, dy1 - dy0, zd - .3 - (EAVE - .3)), 'wall', 'pavilion', 0)
    C.box('Pavilion floor', ((x0 + x1) / 2, (py0 + py1) / 2, zd + .004), (depth, py1 - py0, .008), 'floor', 'pavilion', 0)
    top = RIDGE + .35
    for x in (x0 + .9, x1):
        C.box('Pavilion glazing', (x, (py0 + py1) / 2, (zd + top) / 2), (.03, py1 - py0, top - zd - .1), 'glass', 'pavilion', 0)
    for y in (py0, py1):
        C.box('Pavilion end glazing', ((x0 + .9 + x1) / 2, y, (zd + top) / 2), (x1 - x0 - .9, .03, top - zd - .1), 'glass', 'pavilion', 0)
    for y in [py0 + (py1 - py0) * k / 8 for k in range(9)]:
        for x in (x0 + .9, x1):
            C.box('Pavilion mullion', (x, y, (zd + top) / 2), (.10, .10, top - zd), 'metal', 'pavilion', 0)
    C.box('Pavilion roof', ((x0 + .9 + x1) / 2, (py0 + py1) / 2, top + .08), (x1 - x0 - .9 + .4, py1 - py0 + .4, .16), 'metal', 'pavilion', 0)
    C.box('Pavilion roof glazing', ((x0 + .9 + x1) / 2, (py0 + py1) / 2, top + .18), (x1 - x0 - 1.3, py1 - py0 - .4, .03), 'glass', 'pavilion', 0)
    C.railing('Terrace rail west', (x0 - .05, dy0 + .1, zd), (x0 - .05, dy1 - .1, zd), height=1.05, spacing=.9, role='hardware')
    C.railing('Terrace rail north', (x0 - .05, dy1 - .1, zd), (x1 + .25, dy1 - .1, zd), height=1.05, spacing=.9, role='hardware')
    C.railing('Terrace rail south', (x0 - .05, dy0 + .1, zd), (x1 + .25, dy0 + .1, zd), height=1.05, spacing=.9, role='hardware')
    C.qa_room_light('Pavilion', ((x0 + x1) / 2, (py0 + py1) / 2, top - .4), 60, 4.0)
    # Rooflights on the east slope, chimney on the rear eave beside the street gable.
    for y in (-5.0, 3.0):
        for x in (3.0, 6.5):
            z = EAVE + (RIDGE - EAVE) * (W / 2 - x) / (W / 2)
            C.box('Rooflight', (x, y, z + .25), (1.4, 1.6, .5), 'metal', 'rooflights', 0)
    cx, cy = CHIMNEY
    C.box('Chimney stack', (cx, cy, (G0 + RIDGE + 6.5) / 2), (2.2, 2.2, RIDGE + 6.5 - G0), 'wall', 'chimney', 0)
    C.box('Chimney cap', (cx, cy, RIDGE + 6.55), (2.6, 2.6, .30), 'stone', 'chimney', 0)
    C.box('Chimney cap course', (cx, cy, RIDGE + 6.2), (2.45, 2.45, .20), 'stone', 'chimney', 0)
    C.CONTACTS.append(dict(name='Slate planes on the eaves walls inside the parapet; pavilion on a level deck cut into the west slope; chimney through the east eave', eave_m=EAVE, ridge_m=RIDGE))


def site():
    ext = 6.0
    C.box('South sidewalk', (0, -D / 2 - ext / 2, .0075), (W + 2 * ext, ext, .015), 'foundation', 'sidewalk', 0)
    C.box('West sidewalk', (-W / 2 - ext / 2, ext / 2, .0075), (ext, D + ext, .015), 'foundation', 'sidewalk', 0)
    C.box('Kerb south', (0, -D / 2 - ext + .06, .06), (W + 2 * ext, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb west', (-W / 2 - ext + .06, ext / 2, .06), (.12, D + ext, .12), 'stone', 'sidewalk', 0)
    C.box('Rear yard', (W / 2 + 5.0, 3.0, .0075), (10.0, D + 6.0, .015), 'foundation', 'yard', 0)
    C.box('North yard', (0, D / 2 + 3.0, .0075), (W, 6.0, .015), 'foundation', 'yard', 0)
    for x, y in ((-W / 2 - 3.6, -8.0), (-W / 2 - 3.6, 6.0), (4.0, -D / 2 - 3.6)):
        street_tree(x, y)


def street_tree(x, y, z=.015, height=7.0, spread=1.5):
    C.rod('Street tree trunk', (x, y, z), (x, y, z + height * .55), .14, 'timber', 'street planting', 8)
    for dx, dy in ((-.5, -.2), (.5, -.1), (.0, .5)):
        tip = (x + dx * spread, y + dy * spread, z + height * .72)
        C.rod('Street tree branch', (x, y, z + height * .5), tip, .06, 'timber', 'street planting', 6)
        A.foliage('Street tree crown', tip, (.9 * spread, .9 * spread, 1.3), detail=1)


def build():
    site()
    f_front, f_right, f_rear, f_left = A.faces(W, D)
    elevation(f_left, -D / 2 + T, D / 2 - T, BAYS_LONG, ground='shops')                  # west street face
    elevation(f_right, -D / 2 + T, D / 2 - T, BAYS_LONG, ground='rear')                  # east rear face
    elevation(f_front, -W / 2, W / 2, BAYS_GABLE, ground='shops', gable=True)            # south street gable
    elevation(f_rear, -W / 2, W / 2, BAYS_GABLE, blind=(0,), ground='windows', gable=True)  # north gable
    roof()


LIGHT_RIG = dict(key=(-30, -40, 40), fill=(40, -20, 30), rear=(-16, 40, 36), target=(0, 0, 9.0), gain=6.0)
