"""Chamfered corner block with a domed turret, authored from the locked catalogue views of
barcelona_corner_chamfer / variant_0 (chamfer_classic).

Read from the pixels: a five-storey Eixample corner block with streets south and west. The
ground floor is rusticated stone with tall arched shop openings; above it a stone piano nobile
with a continuous iron balcony, then three storeys of warm brick with stone surrounds and
individual iron balconies on tall French windows, a heavy stone cornice and a balustraded
parapet. The 45-degree chamfer carries a bowed stone bay with glazing between columns, crowned
by a round drum, a copper dome and a lantern. The flat terracotta-tiled roof carries a pyramid
rooflight, small rooflights and chimney stacks.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-chamfer-corner-dome-block'
W, D = 24.0, 24.0               # four bays each side of the chamfer, street edge about 3.5 dome diameters
CH = 9.0                      # chamfer length along the 45-degree face
T = .34
G0 = .15
LEVELS = [5.0, 9.2, 13.0]        # ground floor, piano nobile, two brick storeys (the sources show ground plus three)
CORNICE = 16.8
PAR = CORNICE + 1.3
DRUM_R, DRUM_H = 2.6, 1.6        # short drum under a wider copper dome
DOME_R, DOME_H = 3.3, 3.4
EPS = .002
PALETTE = dict(wall=(.62, .42, .28), joint=(.46, .30, .20), trim=(.18, .26, .22),
    pale=(.76, .70, .58), stone=(.72, .66, .54), roof=(.62, .34, .22), sand=(.70, .64, .52),
    foundation=(.46, .46, .45), glass=(.46, .52, .54), hardware=(.14, .13, .13),
    interior=(.80, .76, .68), floor=(.46, .44, .42), timber=(.36, .26, .16), blue=(.14, .22, .28),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.64, .62, .58), copper=(.56, .30, .18),
    membrane=(.62, .34, .22), rustic=(.66, .60, .48))

# The chamfer face: from the south face end to the west face end at 45 degrees.
CX0, CY0 = -W / 2 + CH / math.sqrt(2), -D / 2          # chamfer start on the south face
CX1, CY1 = -W / 2, -D / 2 + CH / math.sqrt(2)          # chamfer end on the west face
CMX, CMY = (CX0 + CX1) / 2, (CY0 + CY1) / 2
CN = (-1 / math.sqrt(2), -1 / math.sqrt(2))              # outward normal of the chamfer


def manifest(version):
    h = PAR + DRUM_H + 8.0
    cams = G.camera_roster(W, D, h, [
        ('facade_close', (-6.0, -28.0, 8.0), (2.0, -D / 2, 10.0), 45),
        ('architecture_close', (-32.0, -30.0, 18.0), (CMX, CMY, 17.0), 50),
        ('glass_close', (-4.0, -20.0, 2.2), (0.0, -D / 2, 2.6), 50),
        ('chamfer_dome', (-34.0, -34.0, 27.0), (CMX - 1.0, CMY - 1.0, 21.0), 45),
        ('balcony_ironwork', (-8.0, -22.0, 9.0), (-4.0, -D / 2, 9.8), 45),
        ('ground_arcade', (-26.0, -24.0, 2.0), (CMX, CMY, 2.8), 45),
        ('cornice_contact', (8.0, -26.0, 16.0), (10.0, -D / 2, 16.8), 45),
        ('roof_terrace', (-36.0, -40.0, 38.0), (0.0, 0.0, 18.0), 45),
        ('interior', (-6.0, -3.0, LEVELS[0] + 1.6), (-8.0, -D / 2 - 1.0, LEVELS[0] + 1.3), 55),
        ('rear_court', (12.0, 32.0, 10.0), (4.0, D / 2, 8.0), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='barcelona_corner_chamfer/variant_0 (chamfer_classic)',
        measurement_contract=dict(dimensions_m=dict(width=W, depth=D, height=h),
            observed_storeys=4, storey_programme='stone ground floor of shops; stone piano nobile; two brick residential storeys; flat tiled roof with dome turret',
            plan='30 x 26 m corner block read from the top view (roof 480 x 420 px at 0.062 m/px) with a 9 m chamfer at the south-west corner carrying the bowed bay',
            facade='four bays on the south and west faces of French windows 1.3 x 2.8 m with stone surrounds in brick; continuous iron balcony at the first floor and individual balconies above; flat-headed pier-and-lintel shop openings 3.2 x 4.2 m with transoms in rusticated stone; cornice at 19.6 m with a balustraded parapet to 20.9 m',
            levels_m=[G0] + LEVELS, cornice_m=CORNICE, parapet_m=PAR, storeys_recorded='the sources read ground plus three upper storeys; v001 carried four and was corrected',
            chamfer='bowed stone bay projecting 1.6 m: two glazed levels between stone pilasters (about 70 percent glass), a solid top storey with small windows and an iron balcony under the wrapping cornice; round drum 5.2 m across and 1.6 m high above the parapet with oriented windows; wider copper dome 6.6 m across with three porthole oculi and cresting on its overhang; open lantern with a copper bulb and finial',
            roof='flat terracotta tiles; pyramid rooflight 5 m square; two small rooflights; three chimney stacks',
            inferred='north and east faces are not visible and repeat the grammar without balconies; interiors are teaching assumptions'),
        roof_contract=dict(type='flat tiled roof behind a balustraded parapet; dome turret on the chamfer bay; rooflights and chimneys on the slab', datum_m=CORNICE, crowns_m=[PAR, PAR + .1 + DRUM_H + .3 + DOME_H, PAR + .1 + DRUM_H + 3.6 + 3.3]),
        identity_contract=dict(owner='chamfered corner with the two-level glazed bow and copper dome, iron balconies on tall French windows in brick, rusticated pier-and-lintel shop floor, cornice and balustrade'),
        material_contract=dict(profile='source-palette clay: warm brick with recessed courses, pale stone ground floor, surrounds and cornice, black iron balconies, dark green frames, terracotta tiles, copper dome', textured_keeper=False),
        programme_contract=dict(storeys=5, ground='shops with the residential entrance on the chamfer', upper='two apartments per floor; a salon in the bow', roof='shared terrace around the rooflights'),
        contact_contract=['Grade-zero slab and sidewalks', 'Bowed bay bearing on the rusticated ground floor', 'Balconies cantilevered from the carriers', 'Drum and dome bearing on the bay roof', 'Chimneys and rooflights on the roof slab'],
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


def framed(m, f, h, cols=1, rows=1, inset=.16, occupied='apartment', kind='window'):
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


def arch_fill(f, u, z_top, w, rise, role='rustic'):
    pts = [(-w / 2, z_top), (w / 2, z_top), (w / 2, z_top - rise)]
    for k in range(1, 7):
        x = w / 2 - w * k / 7
        pts.append((x, z_top - rise + rise * (1 - (2 * x / w) ** 2)))
    pts.append((-w / 2, z_top - rise))
    f.panel('Arch spandrel', [(u + a, b) for a, b in pts], -.03, T + .02, role, 'arches')


def iron_balcony(m, f, u, z, w, depth=.8):
    """Cantilevered iron balcony: stone slab with a merged black lattice (top rail, end rails, pickets)."""
    m.box('stone', u, -depth / 2 + .02, z - .10, w, depth + .04, .20)
    m.box('hardware', u, -depth + .04, z + .98, w, .05, .05)
    for e in (-1, 1):
        m.box('hardware', u + e * (w / 2 - .02), -depth / 2 + .02, z + .98, .05, depth - .04, .05)
    n = max(3, int(w / .48))
    for i in range(n + 1):
        m.box('hardware', u - w / 2 + .02 + (w - .04) * i / n, -depth + .04, z + .55, .025, .025, .86)


def elevation(f, lo, hi, bays, ground='shops', balconies=True, plain=False):
    span = hi - lo
    pitch = span / bays
    gholes, uholes = [], []
    for i in range(bays):
        c = lo + pitch * (i + .5)
        if ground == 'shops':
            gholes.append(hole(f'{f.label} shop arch {i}', c, G0, 3.2, 4.2, kind='shop'))
        elif i % 2 == 0:
            gholes.append(hole(f'{f.label} ground window {i}', c, 1.2, 1.6, 2.4))
        for k, zl in enumerate(LEVELS):
            uholes.append(hole(f'{f.label} window {i}-{k}', c, zl + .12, 1.3, 2.8 if k < 2 else 2.4, kind='french'))
    # Rusticated stone ground carrier and brick upper carrier, split at the piano-nobile band.
    f.wall(f.label + ' ground carrier', lo, hi - EPS, G0, LEVELS[0] - .30, depth=T, role='rustic', holes=gholes)
    f.wall(f.label + ' upper carrier', lo, hi - EPS, LEVELS[0] - .30, CORNICE + .25, depth=T, holes=uholes)
    if not plain:
        G.brick_courses(f, lo + .02, hi - .02, G0 + .3, LEVELS[0] - .5, gholes, spacing=.8)
        G.brick_courses(f, lo + .02, hi - .02, LEVELS[0] + .2, CORNICE - .8, uholes, spacing=.45)
    m = Merge(f)
    for h in gholes:
        if h.get('kind') == 'shop':
            framed(m, f, h, cols=2, rows=2, occupied='shop', kind='storefront')
            m.box('stone', h['u'], -.05, h['z'] + h['h'] + .17, min(h['w'] + .9, pitch - .30), T + .16, .30)   # flat lintel over the piers
        else:
            framed(m, f, h, cols=1, occupied='service')
    for h in uholes:
        if plain:
            framed(m, f, h, cols=1, rows=1, occupied='apartment', kind='french window')
            continue
        framed(m, f, h, cols=2, rows=1, occupied='apartment', kind='french window')
        for sgn in (-1, 1):
            m.box('stone', h['u'] + sgn * (h['w'] / 2 + .12), -.04, h['z'] + h['h'] / 2, .24, T + .14, h['h'] + .24)
        m.box('stone', h['u'], -.05, h['z'] + h['h'] + .18, h['w'] + .70, T + .16, .26)
        if balconies and h['z'] > LEVELS[1] - .1 and h['z'] < CORNICE - 1.0:
            iron_balcony(m, f, h['u'], h['z'], h['w'] + .9)
    m.box('stone', (lo + hi) / 2, -.06, LEVELS[0] - .15, span - 2 * EPS, T + .20, .30)
    if balconies:
        iron_balcony(m, f, (lo + hi) / 2, LEVELS[0], span - .4, depth=.9)
    m.box('stone', (lo + hi) / 2, -.20, LEVELS[1] - .22, span - 2 * EPS, .40, .18)
    m.box('stone', (lo + hi) / 2, -.28, CORNICE - .30, span - 2 * EPS, T + .56, .60)
    m.box('stone', (lo + hi) / 2, -.10, CORNICE + .08, span - 2 * EPS, T + .20, .16)
    # Open balustrade: stone rail on balusters over the cornice band.
    m.box('stone', (lo + hi) / 2, T / 2 - .02, PAR + .04, span - 2 * EPS, T + .12, .14)
    nb = int(span / .72)
    for i in range(nb + 1):
        m.box('pale', lo + .2 + (span - .4) * i / max(1, nb), T / 2 - .02, (CORNICE + .25 + PAR) / 2, .14, .14, PAR - CORNICE - .27)
    m.flush('facade')


def chamfer_bay():
    """Bowed stone bay on the chamfer: three faceted carriers with glazing between stone columns, drum, dome, lantern."""
    nx, ny = CN
    tx, ty = -ny, nx          # tangent along the chamfer from the west end to the south end
    half = CH / 2
    # Chamfer wall itself (ground floor and parapet band) as a carrier with the entrance.
    f = C.Face((CMX, CMY, 0), (tx, ty, 0), (-nx, -ny, 0), 'chamfer')
    holes = [hole('Entrance doors', 0.0, G0, 2.8, 4.0, kind='door')]
    for k, zl in enumerate(LEVELS):
        pass
    f.wall('chamfer ground carrier', -half, half, G0, LEVELS[0] - .30, depth=T, role='rustic', holes=[holes[0]])
    f.wall('chamfer upper carrier', -half, half, LEVELS[0] - .30, CORNICE + .25, depth=T, holes=holes[1:])
    G.brick_courses(f, -half + .02, half - .02, G0 + .3, LEVELS[0] - .5, holes, spacing=.8)
    m = Merge(f)
    for h in holes:
        if h.get('kind') == 'door':
            framed(m, f, h, cols=2, rows=2, occupied='residential entrance hall', kind='glazed door')
            m.box('stone', h['u'], -.05, h['z'] + h['h'] + .17, h['w'] + .9, T + .16, .30)
        else:
            framed(m, f, h, cols=2, occupied='attic salon')
            m.box('stone', h['u'], -.05, h['z'] + h['h'] + .18, h['w'] + .70, T + .16, .26)
    m.box('stone', 0.0, -.06, LEVELS[0] - .15, CH - 2 * EPS, T + .20, .30)
    m.box('stone', 0.0, T / 2 - .02, PAR + .04, CH - 2 * EPS, T + .12, .14)
    for i in range(int(CH / .72) + 1):
        m.box('pale', -half + .2 + (CH - .4) * i / int(CH / .72), T / 2 - .02, (CORNICE + .25 + PAR) / 2, .14, .14, PAR - CORNICE - .27)
    m.flush('chamfer')
    # Bowed bay over the piano nobile and the two storeys above: five facets projecting 1.6 m.
    z0, z1 = LEVELS[0], CORNICE - .30
    facets = 5
    r_out = 1.6
    pts = [(CMX + tx * (-math.cos(math.pi * i / facets) * (CH / 2 - 1.0)) + nx * math.sin(math.pi * i / facets) * r_out,
            CMY + ty * (-math.cos(math.pi * i / facets) * (CH / 2 - 1.0)) + ny * math.sin(math.pi * i / facets) * r_out) for i in range(facets + 1)]
    for i in range(facets):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        length = math.dist((ax, ay), (bx, by))
        ux, uy = (bx - ax) / length, (by - ay) / length
        inx, iny = -uy, ux
        if inx * nx + iny * ny > 0:
            inx, iny = -inx, -iny
        g = C.Face(((ax + bx) / 2, (ay + by) / 2, 0), (ux, uy, 0), (inx, iny, 0), f'bay facet {i}')
        # The two short end facets return into the chamfer wall and stay solid stone; the three outer facets carry the glazing.
        end = i in (0, facets - 1)
        fh = [] if end else [hole(f'Bay glazing {i}-0', 0.0, LEVELS[0] + .25, length - .6, 3.5),
                             hole(f'Bay glazing {i}-1', 0.0, LEVELS[1] + .25, length - .6, 3.0),
                             hole(f'Bay window {i}-2', 0.0, LEVELS[2] + .3, 1.1, 2.0)]
        g.wall(f'bay facet {i} carrier', -length / 2, length / 2, z0, z1, depth=T, role='stone', holes=fh)
        mb = Merge(g)
        if not end:
            framed(mb, g, fh[0], cols=2, rows=2, occupied='salon', kind='window')
            framed(mb, g, fh[1], cols=2, rows=2, occupied='bedroom', kind='window')
            framed(mb, g, fh[2], cols=1, rows=1, occupied='attic salon', kind='window')
        mb.box('stone', 0.0, -.05, LEVELS[1] - .2, length - .02, T + .16, .28)
        mb.box('stone', 0.0, -.05, LEVELS[2] - .2, length - .02, T + .16, .28)
        iron_balcony(mb, g, 0.0, LEVELS[2], length - .3, depth=.7)
        mb.flush('bay')
        for e in (-1, 1):
            cx_, cy_ = g.p(e * (length / 2 - .2), -.12, 0)[:2]
            C.box('Bay column', (cx_, cy_, (LEVELS[0] + LEVELS[2]) / 2 - .15), (.42, .42, LEVELS[2] - LEVELS[0] - .3), 'stone', 'bay columns', 0)
    # Bay floors, wrapping cornice ring, drum with oriented windows, dome with oculi and cresting, open lantern.
    cx, cy = CMX + nx * .3, CMY + ny * .3
    for zl in LEVELS:
        C.rod('Bay floor', (cx, cy, zl - .12), (cx, cy, zl + .08), CH / 2 - .6, 'floor', 'bay floors', 16)
    C.rod('Bay cornice', (cx, cy, z1 - .02), (cx, cy, z1 + .55), CH / 2 + .1, 'stone', 'bay roof', 20)
    C.rod('Bay parapet', (cx, cy, z1 + .55), (cx, cy, PAR + .28), DRUM_R + .9, 'stone', 'turret', 20)
    cz = PAR + .28
    C.rod('Drum', (cx, cy, cz), (cx, cy, cz + DRUM_H), DRUM_R, 'stone', 'turret', 20)
    for k in range(8):
        a = math.tau * k / 8 + math.pi / 8
        ox, oy = cx + math.cos(a) * DRUM_R, cy + math.sin(a) * DRUM_R
        wf = C.Face((ox, oy, 0), (-math.sin(a), math.cos(a), 0), (-math.cos(a), -math.sin(a), 0), f'drum window {k}')
        wf.part('Drum window frame', 0.0, -.03, cz + DRUM_H / 2, .95, .08, DRUM_H - .7, 'pale', 'turret', 0)
        wf.part('Drum window glass', 0.0, -.08, cz + DRUM_H / 2, .75, .02, DRUM_H - .9, 'glass', 'turret', 0)
    C.rod('Drum cornice', (cx, cy, cz + DRUM_H), (cx, cy, cz + DRUM_H + .3), DOME_R + .15, 'stone', 'turret', 20)
    dz = cz + DRUM_H + .3
    dome(cx, cy, dz, DOME_R, DOME_H)
    # Porthole oculi sit on the dome surface, their rims normal to it (never a box pushed through the shell).
    for k in range(3):
        a = math.tau * k / 3 + math.pi / 4
        t = math.radians(38)
        px, py, pz = cx + math.cos(a) * DOME_R * math.cos(t), cy + math.sin(a) * DOME_R * math.cos(t), dz + DOME_H * math.sin(t)
        nx_, ny_, nz_ = math.cos(t) * math.cos(a) / DOME_R, math.cos(t) * math.sin(a) / DOME_R, math.sin(t) / DOME_H
        nl = (nx_ ** 2 + ny_ ** 2 + nz_ ** 2) ** .5
        nx_, ny_, nz_ = nx_ / nl, ny_ / nl, nz_ / nl
        C.rod('Dome oculus rim', (px - nx_ * .12, py - ny_ * .12, pz - nz_ * .12), (px + nx_ * .08, py + ny_ * .08, pz + nz_ * .08), .42, 'pale', 'turret', 14)
        C.rod('Dome oculus glass', (px + nx_ * .02, py + ny_ * .02, pz + nz_ * .02), (px + nx_ * .10, py + ny_ * .10, pz + nz_ * .10), .30, 'glass', 'turret', 14)
    for k in range(16):
        a = math.tau * k / 16
        C.beam('Dome cresting', (cx + math.cos(a) * (DOME_R + .02), cy + math.sin(a) * (DOME_R + .02), dz + .3), (cx + math.cos(a) * (DOME_R + .02), cy + math.sin(a) * (DOME_R + .02), dz + .95), .05, .05, 'hardware', 'turret')
    lz = dz + DOME_H + .2
    C.rod('Lantern base', (cx, cy, lz), (cx, cy, lz + .25), .9, 'copper', 'turret', 12)
    for k in range(8):
        a = math.tau * k / 8
        C.beam('Lantern column', (cx + math.cos(a) * .7, cy + math.sin(a) * .7, lz + .25), (cx + math.cos(a) * .7, cy + math.sin(a) * .7, lz + 1.6), .08, .08, 'pale', 'turret')
    C.rod('Lantern cap ring', (cx, cy, lz + 1.6), (cx, cy, lz + 1.8), .95, 'copper', 'turret', 12)
    dome(cx, cy, lz + 1.8, .9, 1.0)
    C.rod('Finial', (cx, cy, lz + 2.75), (cx, cy, lz + 3.5), .07, 'hardware', 'turret', 8)
    # Corner posts close the mitres where the proud courses, cornice and balustrade of neighbouring faces meet.
    for (qx, qy) in ((CX0, CY0), (CX1, CY1)):
        C.rod('Chamfer corner pilaster', (qx, qy, 0.0), (qx, qy, PAR + .16), .44, 'stone', 'corner posts', 16)
        C.rod('Chamfer corner capital', (qx, qy, CORNICE - .66), (qx, qy, CORNICE + .22), .82, 'stone', 'corner posts', 16)
    for (qx, qy) in ((-W / 2 - .1, D / 2 + .1), (W / 2 + .1, D / 2 + .1), (W / 2 + .1, -D / 2 - .1)):
        C.box('Corner quoin', (qx, qy, (PAR + .16) / 2), (1.3, 1.3, PAR + .16), 'stone', 'corner posts', 0)
    C.CONTACTS.append(dict(name='Bowed bay on the rusticated ground floor; drum and dome on the bay cornice; corner posts at every corner', bay_top_m=z1, dome_top_m=dz + DOME_H))


def dome(cx, cy, z0, r, h, rings=5, segs=16):
    vs, fs = [], []
    for j in range(rings + 1):
        a = math.pi / 2 * j / rings
        rr = r * math.cos(a); zz = z0 + h * math.sin(a)
        for i in range(segs):
            b = math.tau * i / segs
            vs.append((cx + rr * math.cos(b), cy + rr * math.sin(b), zz))
    for j in range(rings):
        for i in range(segs):
            a0 = j * segs + i; a1 = j * segs + (i + 1) % segs
            b0 = (j + 1) * segs + i; b1 = (j + 1) * segs + (i + 1) % segs
            fs.append((a0, a1, b1, b0))
    fs.append(tuple(range(segs - 1, -1, -1)))
    C.mesh('Copper dome', vs, fs, 'copper', 'turret')


def roof_and_interior():
    outline = [(CX0, -D / 2), (W / 2, -D / 2), (W / 2, D / 2), (-W / 2, D / 2), (-W / 2, CY1)]
    inner = [(CX0 + .14, -D / 2 + T), (W / 2 - T, -D / 2 + T), (W / 2 - T, D / 2 - T), (-W / 2 + T, D / 2 - T), (-W / 2 + T, CY1 + .14)]
    C.prism('Ground slab', outline, 'z', 0.0, G0, 'foundation', 'foundation')
    for zl in LEVELS:
        C.prism(f'Floor {zl:.1f}', inner, 'z', zl - .28, zl, 'floor', 'occupied floors')
        C.qa_room_light(f'South rooms {zl:.1f}', (-4.0, -D / 2 + 4.0, zl + 2.6), 80, 5.0)
        C.qa_room_light(f'West rooms {zl:.1f}', (-W / 2 + 4.0, 2.0, zl + 2.6), 60, 5.0)
    C.qa_room_light('Shops', (-2.0, -D / 2 + 4.0, LEVELS[0] - .8), 110, 6.0)
    C.prism('Roof slab', inner, 'z', CORNICE - .24, CORNICE, 'floor', 'roof')
    C.prism('Roof tiles', [(x * .999, y * .999) for x, y in inner], 'z', CORNICE, CORNICE + .008, 'membrane', 'roof')
    # Pyramid rooflight, small rooflights, chimneys.
    px, py, ps, ph = 2.0, 1.0, 5.0, 2.2
    vs = [(px - ps / 2, py - ps / 2, CORNICE + .3), (px + ps / 2, py - ps / 2, CORNICE + .3), (px + ps / 2, py + ps / 2, CORNICE + .3), (px - ps / 2, py + ps / 2, CORNICE + .3), (px, py, CORNICE + .3 + ph)]
    C.mesh('Pyramid rooflight', vs, [(3, 2, 1, 0), (0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], 'glass', 'rooflights')
    C.box('Pyramid rooflight curb', (px, py, CORNICE + .15), (ps + .2, ps + .2, .30), 'stone', 'rooflights', 0)
    for x, y in ((-3.0, 5.0), (7.0, -4.0)):
        C.box('Rooflight curb', (x, y, CORNICE + .2), (1.9, 1.5, .4), 'stone', 'rooflights', 0)
        C.box('Rooflight', (x, y, CORNICE + .55), (1.7, 1.3, .3), 'glass', 'rooflights', 0)
    for x, y in ((8.0, 8.0), (-8.0, 8.5), (9.5, -7.0)):
        C.box('Chimney stack', (x, y, CORNICE + 1.3), (1.2, 1.2, 2.6), 'stone', 'chimneys', 0)
        C.box('Chimney cap', (x, y, CORNICE + 2.68), (1.5, 1.5, .16), 'pale', 'chimneys', 0)
    zl = LEVELS[0]
    A.sofa(-2.0, -D / 2 + 6.0, zl)


def site():
    ext = 6.0
    C.box('South sidewalk', (0, -D / 2 - ext / 2, .0075), (W + 2 * ext, ext, .015), 'foundation', 'sidewalk', 0)
    C.box('West sidewalk', (-W / 2 - ext / 2, ext / 2, .0075), (ext, D + ext, .015), 'foundation', 'sidewalk', 0)
    C.box('Kerb south', (0, -D / 2 - ext + .06, .06), (W + 2 * ext, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb west', (-W / 2 - ext + .06, 0, .06), (.12, D + 2 * ext, .12), 'stone', 'sidewalk', 0)
    C.box('Rear court', (0, D / 2 + 3.0, .0075), (W, 6.0, .015), 'foundation', 'court', 0)
    street_tree(4.0, -D / 2 - 3.6)
    street_tree(-W / 2 - 3.6, 6.0)


def street_tree(x, y, z=.015, height=8.0, spread=1.8):
    C.rod('Street tree trunk', (x, y, z), (x, y, z + height * .55), .16, 'timber', 'street planting', 8)
    for dx, dy in ((-.5, -.2), (.5, -.1), (.0, .5)):
        tip = (x + dx * spread, y + dy * spread, z + height * .72)
        C.rod('Street tree branch', (x, y, z + height * .5), tip, .06, 'timber', 'street planting', 6)
        A.foliage('Street tree crown', tip, (.9 * spread, .9 * spread, 1.3), detail=1)


def build():
    site()
    roof_and_interior()
    # South face runs from the chamfer start to the east corner; west face from the chamfer end to the north corner.
    south = C.Face(((CX0 + W / 2) / 2, -D / 2, 0), (1, 0, 0), (0, 1, 0), 'south')
    west = C.Face((-W / 2, (CY1 + D / 2) / 2, 0), (0, -1, 0), (1, 0, 0), 'west')
    north = C.Face((0, D / 2, 0), (-1, 0, 0), (0, -1, 0), 'north')
    east = C.Face((W / 2, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    elevation(south, -(W / 2 - CX0) / 2, (W / 2 - CX0) / 2, 4, ground='shops')
    elevation(west, -(D / 2 - CY1) / 2 + T, (D / 2 - CY1) / 2, 4, ground='shops')
    elevation(north, -W / 2, W / 2, 4, ground='plain', balconies=False, plain=True)
    elevation(east, -D / 2 + T, D / 2 - T, 4, ground='plain', balconies=False, plain=True)
    chamfer_bay()


LIGHT_RIG = dict(key=(-34, -40, 44), fill=(40, -20, 32), rear=(-16, 40, 40), target=(0, 0, 11.0), gain=6.5)
