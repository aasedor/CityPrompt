"""Chamfered corner block with a domed turret, authored from the locked catalogue views of
barcelona_corner_chamfer / variant_0 (chamfer_classic).

Read from the pixels: a three-storey Eixample corner block with streets south and west. The
ground floor is rusticated stone with tall arched shop openings; above it a stone piano nobile
with a continuous iron balcony, then a second brick storey with individual balconies, stone surrounds and
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
LEVELS = [5.0, 9.2]              # ground floor of shops and two brick residential storeys: both locked sources show exactly three storeys (the taller blocks beside it are neighbours)
CORNICE = 13.1
PAR = CORNICE + 1.3
SKIRT_H = .60                    # copper skirt seated on the projecting dome-foot cornice disc (no stone drum: both sources)
DISC_R = 4.2                     # dome-foot cornice disc radius: about 1 m beyond the frieze all round
CZ_UP = .70                      # copper eave height above the parapet line
RIBS = 8                         # continuous seated copper ribs (sources: about eight)
DOME_R, DOME_H = 3.3, 5.8        # ribbed copper dome, pointed profile about as tall as it is wide
DRUM_R, DRUM_H = DOME_R, SKIRT_H # legacy names kept for the manifest
# Dome meridian profile (radius fraction, height fraction): slightly bulbous above the skirt, then curving to a point.
DOME_PROFILE = [(1.0, 0.0), (1.04, .10), (1.03, .24), (.96, .40), (.84, .55), (.66, .70), (.46, .83), (.26, .93), (.10, .985), (0.0, 1.0)]
NECK_R = .62                     # solid octagonal neck carrying the lantern out of the dome apex
BAY_OUT = 2.4                    # bow bay projection from the chamfer plane
EPS = .002
PALETTE = dict(wall=(.60, .39, .25), joint=(.44, .28, .18), trim=(.18, .26, .22),
    pale=(.76, .70, .58), stone=(.72, .66, .54), roof=(.62, .34, .22), sand=(.70, .64, .52),
    foundation=(.46, .46, .45), glass=(.46, .52, .54), hardware=(.14, .13, .13),
    interior=(.80, .76, .68), floor=(.46, .44, .42), timber=(.36, .26, .16), blue=(.14, .22, .28),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.64, .62, .58), copper=(.46, .24, .17),
    membrane=(.62, .34, .22), rustic=(.66, .60, .48))

# The chamfer face: from the south face end to the west face end at 45 degrees.
CX0, CY0 = -W / 2 + CH / math.sqrt(2), -D / 2          # chamfer start on the south face
CX1, CY1 = -W / 2, -D / 2 + CH / math.sqrt(2)          # chamfer end on the west face
CMX, CMY = (CX0 + CX1) / 2, (CY0 + CY1) / 2
CN = (-1 / math.sqrt(2), -1 / math.sqrt(2))              # outward normal of the chamfer


def manifest(version):
    h = PAR + CZ_UP + SKIRT_H + DOME_H + 5.5
    cams = G.camera_roster(W, D, h, [
        ('facade_close', (-6.0, -28.0, 6.5), (2.0, -D / 2, 8.0), 45),
        ('architecture_close', (-32.0, -30.0, 15.0), (CMX, CMY, 13.5), 50),
        ('glass_close', (-4.0, -20.0, 2.2), (0.0, -D / 2, 2.6), 50),
        ('chamfer_dome', (-34.0, -34.0, 23.0), (CMX - 1.0, CMY - 1.0, 17.0), 45),
        ('balcony_ironwork', (-8.0, -22.0, 9.0), (-4.0, -D / 2, 9.8), 45),
        ('ground_arcade', (-26.0, -24.0, 2.0), (CMX, CMY, 2.8), 45),
        ('cornice_contact', (7.0, -24.0, CORNICE - 4.2), (10.0, -D / 2, CORNICE - .3), 45),
        ('roof_terrace', (-36.0, -40.0, 33.0), (0.0, 0.0, 14.0), 45),
        ('interior', (1.0, -4.5, LEVELS[0] + 1.6), (1.0, -D / 2 - 1.0, LEVELS[0] + 1.3), 55),
        ('rear_court', (12.0, 32.0, 10.0), (4.0, D / 2, 8.0), 40)])
    for c in cams:
        if c['name'] == 'front':          # eye-level view centred on the chamfer along its normal, both wings receding (v007 P1 5)
            c['location'] = (CMX + CN[0] * 46.0, CMY + CN[1] * 46.0, 1.7); c['target'] = (CMX, CMY, 11.0); c['lens'] = 30
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='barcelona_corner_chamfer/variant_0 (chamfer_classic)',
        measurement_contract=dict(dimensions_m=dict(width=W, depth=D, height=h),
            observed_storeys=3, storey_programme='rusticated stone ground floor of tall narrow shop openings; two brick residential storeys, the first with a continuous iron balcony; flat tiled roof with the dome turret',
            plan='30 x 26 m corner block read from the top view (roof 480 x 420 px at 0.062 m/px) with a 9 m chamfer at the south-west corner carrying the bowed bay',
            facade='four bays on the south and west faces of French windows 1.3 x 2.8 m with stone surrounds in brick; continuous iron balcony at the first floor and individual balconies above; tall narrow flat-headed shop openings 1.6 x 4.4 m with transoms on wide rusticated stone piers; round-arched glazed entrance on the chamfer between projecting piers; heavy bracketed cornice projecting about 0.85 m at 13.1 m with a balustraded parapet to 14.4 m',
            levels_m=[G0] + LEVELS, cornice_m=CORNICE, parapet_m=PAR, storeys_recorded='both locked sources show ground plus two upper storeys; v001 to v004 carried one storey too many and v005 corrects it',
            chamfer='continuously bowed stone bay projecting 2.4 m on seven close facets: five tall lights per level between round stone columns, one curved iron railing on a curved stone sill at each level, solid stone returns; bow wall and frieze rising solid to a round dome-foot cornice disc projecting about 1 m with a bed mould, copper eave and skirt, pierced copper arch cresting on the disc lip (no balustrade, no recessed drum); copper dome 6.6 m across and 5.8 m high with a pointed profile, eight continuous seated ribs and four smooth copper round dormers with bonnet hoods at 45 percent of its height; open lantern on a solid octagonal neck out of the apex, copper bulb and finial',
            roof='flat terracotta tiles; pyramid rooflight 5 m square; two small rooflights; three chimney stacks',
            inferred='north and east faces are not visible and repeat the grammar without balconies; interiors are teaching assumptions'),
        roof_contract=dict(type='flat tiled roof behind a balustraded parapet; dome turret on the chamfer bay; rooflights and chimneys on the slab', datum_m=CORNICE, crowns_m=[PAR, PAR + CZ_UP + SKIRT_H + DOME_H, PAR + CZ_UP + SKIRT_H + DOME_H + .45 + 3.5]),
        identity_contract=dict(owner='chamfered corner with the two-level glazed bow and copper dome, iron balconies on tall French windows in brick, rusticated pier-and-lintel shop floor, cornice and balustrade'),
        material_contract=dict(profile='source-palette clay: warm brick with recessed courses, pale stone ground floor, surrounds and cornice, black iron balconies, dark green frames, terracotta tiles, copper dome', textured_keeper=False),
        programme_contract=dict(storeys=5, ground='shops with the residential entrance on the chamfer', upper='two apartments per floor; a salon in the bow', roof='shared terrace around the rooflights'),
        contact_contract=['Grade-zero slab and sidewalks', 'Bowed bay bearing on the rusticated ground floor', 'Balconies cantilevered from the carriers', 'Dome-foot cornice disc on the frieze pedestal; copper skirt and dome on the disc', 'Chimneys and rooflights on the roof slab'],
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
    for k in range(1, 12):
        x = w / 2 - w * k / 12
        pts.append((x, z_top - rise + rise * (1 - (2 * x / w) ** 2) ** .5))   # elliptical head: a semicircle when rise = w / 2
    pts.append((-w / 2, z_top - rise))
    f.panel('Arch spandrel', [(u + a, b) for a, b in pts], -.03, T + .02, role, 'arches')


def iron_balcony(m, f, u, z, w, depth=.8):
    """Cantilevered iron balcony: stone slab with a merged black lattice (top rail, end rails, pickets)."""
    m.box('stone', u, -depth / 2 + .02, z - .10, w, depth + .04, .20)
    m.box('hardware', u, -depth + .04, z + .98, w, .05, .05)
    for e in (-1, 1):
        m.box('hardware', u + e * (w / 2 - .02), -depth / 2 + .02, z + .98, .05, depth - .04, .05)
    m.box('hardware', u, -depth + .04, z + .50, w, .03, .03)
    n = max(4, int(w / .22))
    for i in range(n + 1):
        m.box('hardware', u - w / 2 + .02 + (w - .04) * i / n, -depth + .04, z + .55, .03, .03, .86)


def cornice(m, lo, hi, span):
    """Heavy stone cornice: bed mould, a row of block modillions and a corona projecting about 0.85 m with a shadowed soffit."""
    m.box('stone', (lo + hi) / 2, -.12, CORNICE - .56, span - 2 * EPS, T + .24, .28)
    n = max(2, int(span / .95))
    for i in range(n + 1):
        m.box('stone', lo + .35 + (span - .70) * i / n, -.44, CORNICE - .24, .26, .48, .36)
    m.box('stone', (lo + hi) / 2, -.35, CORNICE + .17, span - 2 * EPS, T + .70, .46)


def elevation(f, lo, hi, bays, ground='shops', balconies=True, plain=False):
    span = hi - lo
    pitch = span / bays
    gholes, uholes = [], []
    for i in range(bays):
        c = lo + pitch * (i + .5)
        if ground == 'shops':
            gholes.append(hole(f'{f.label} shop opening {i}', c, G0, 1.6, 4.4, kind='shop'))
        elif i % 2 == 0:
            gholes.append(hole(f'{f.label} ground window {i}', c, 1.2, 1.6, 2.4))
        for k, zl in enumerate(LEVELS):
            uholes.append(hole(f'{f.label} window {i}-{k}', c, zl + .12, 1.3, 2.8, kind='french'))
    # Rusticated stone ground carrier and brick upper carrier, split at the piano-nobile band.
    f.wall(f.label + ' ground carrier', lo, hi - EPS, G0, LEVELS[0] - .30, depth=T, role='rustic', holes=gholes)
    f.wall(f.label + ' upper carrier', lo, hi - EPS, LEVELS[0] - .30, CORNICE + .25, depth=T, holes=uholes)
    if not plain:
        G.brick_courses(f, lo + .02, hi - .02, G0 + .3, LEVELS[0] - .5, gholes, spacing=.8)
        G.brick_courses(f, lo + .02, hi - .02, LEVELS[0] + .2, CORNICE - .8, uholes, spacing=.45)
    m = Merge(f)
    for h in gholes:
        if h.get('kind') == 'shop':
            framed(m, f, h, cols=1, rows=2, occupied='shop', kind='storefront')
            m.box('stone', h['u'], -.05, h['z'] + h['h'] + .13, min(h['w'] + .9, pitch - .30), T + .16, .22)   # flat lintel over the piers
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
    cornice(m, lo, hi, span)
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
    holes = [hole('Entrance doors', 0.0, G0, 2.6, 4.3, kind='door')]
    for k, zl in enumerate(LEVELS):
        pass
    f.wall('chamfer ground carrier', -half, half, G0, LEVELS[0] - .30, depth=T, role='rustic', holes=[holes[0]])
    f.wall('chamfer upper carrier', -half, half, LEVELS[0] - .30, CORNICE + .25, depth=T, role='stone', holes=holes[1:])   # stone beside the bay, not brick strips (v007 P1 4)
    G.brick_courses(f, -half + .02, half - .02, G0 + .3, LEVELS[0] - .5, holes, spacing=.8)
    m = Merge(f)
    for h in holes:
        if h.get('kind') == 'door':
            framed(m, f, h, cols=2, rows=2, occupied='residential entrance hall', kind='glazed door')
            arch_fill(f, h['u'], h['z'] + h['h'], h['w'], h['w'] / 2, role='stone')          # round arch head over the transom
            m.box('stone', h['u'], -.08, h['z'] + h['h'] + .17, h['w'] + 1.3, T + .22, .30)   # frieze band over the arch
            for sgn in (-1, 1):                                                               # projecting rusticated piers with console capitals
                m.box('rustic', h['u'] + sgn * (h['w'] / 2 + .55), -.18, (G0 + LEVELS[0] - .70) / 2, .70, T + .36, LEVELS[0] - .70 - G0)
                m.box('stone', h['u'] + sgn * (h['w'] / 2 + .55), -.26, LEVELS[0] - .52, .90, T + .52, .36)
        else:
            framed(m, f, h, cols=2, occupied='attic salon')
            m.box('stone', h['u'], -.05, h['z'] + h['h'] + .18, h['w'] + .70, T + .16, .26)
    m.box('stone', 0.0, -.06, LEVELS[0] - .15, CH - 2 * EPS, T + .20, .30)
    m.flush('chamfer')
    # Bowed bay over the piano nobile and the storey above: a continuous bow on seven close facets projecting BAY_OUT,
    # five tall lights per level between round stone columns, solid stone returns at the ends, one curved stone sill
    # course and one curved iron railing per level (v007 P1 4).
    z0, z1 = LEVELS[0], CORNICE - .30
    facets = 7
    A0 = CH / 2 - .6
    def arc(Aa, Bb, n=facets, inset=0.0, a0=0.0, a1=math.pi):
        return [(CMX + tx * (-math.cos(a0 + (a1 - a0) * i / n) * Aa) + nx * (math.sin(a0 + (a1 - a0) * i / n) * Bb - inset),
                 CMY + ty * (-math.cos(a0 + (a1 - a0) * i / n) * Aa) + ny * (math.sin(a0 + (a1 - a0) * i / n) * Bb - inset)) for i in range(n + 1)]
    pts = arc(A0, BAY_OUT)
    for i in range(facets):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        length = math.dist((ax, ay), (bx, by))
        ux, uy = (bx - ax) / length, (by - ay) / length
        inx, iny = -uy, ux
        if inx * nx + iny * ny > 0:
            inx, iny = -inx, -iny
        g = C.Face(((ax + bx) / 2, (ay + by) / 2, 0), (ux, uy, 0), (inx, iny, 0), f'bay facet {i}')
        end = i in (0, facets - 1)
        fh = [] if end else [hole(f'Bay light {i}-0', 0.0, LEVELS[0] + .90, length - .36, 2.9),
                             hole(f'Bay light {i}-1', 0.0, LEVELS[1] + .90, length - .36, 2.7)]
        g.wall(f'bay facet {i} carrier', -length / 2, length / 2, z0, z1, depth=T, role='stone', holes=fh)
        mb = Merge(g)
        if not end:
            framed(mb, g, fh[0], cols=1, rows=2, occupied='salon', kind='window')
            framed(mb, g, fh[1], cols=1, rows=2, occupied='bedroom', kind='window')
        mb.box('stone', 0.0, -.05, LEVELS[1] - .25, length - .02, T + .16, .28)
        mb.flush('bay')
    for i in range(1, facets):
        jx, jy = pts[i]
        d = math.dist((jx, jy), (CMX, CMY)); jx, jy = jx + (CMX - jx) / d * .08, jy + (CMY - jy) / d * .08
        C.rod('Bay column', (jx, jy, LEVELS[0] + .08), (jx, jy, z1 - .02), .19, 'stone', 'bay columns', 12)
        C.rod('Bay column base', (jx, jy, LEVELS[0] + .06), (jx, jy, LEVELS[0] + .30), .24, 'stone', 'bay columns', 12)
        C.rod('Bay column capital', (jx, jy, z1 - .40), (jx, jy, z1 - .02), .24, 'stone', 'bay columns', 12)
    # Bay floors, one curved stone sill course and one curved iron railing per level over the five lights; their straight
    # edges sit 0.15 m inside the chamfer carrier so no face shares the chamfer plane.
    ga0, ga1 = math.pi / facets, math.pi * (facets - 1) / facets
    for zl in LEVELS:
        C.prism('Bay floor', arc(A0 - .2, BAY_OUT - .25, 10, .15), 'z', zl - .12, zl + .08, 'floor', 'bay floors')
        half_ring('Bay sill course', arc(A0 - .10, BAY_OUT - .10, 24, .15), arc(A0 + .34, BAY_OUT + .34, 24, .15), zl - .14, zl + .07, 'stone', 'bay floors')
        rail = arc(A0 + .22, BAY_OUT + .22, 34, 0.0, ga0, ga1)
        for k, (px_, py_) in enumerate(rail):
            C.rod('Bay rail picket', (px_, py_, zl + .07), (px_, py_, zl + .92), .016, 'hardware', 'bay railing', 6)
        for (px_, py_), (qx_, qy_) in zip(rail, rail[1:]):
            C.beam('Bay rail top', (px_, py_, zl + .95), (qx_, qy_, zl + .95), .045, .045, 'hardware', 'bay railing')
            C.beam('Bay rail mid', (px_, py_, zl + .50), (qx_, qy_, zl + .50), .03, .03, 'hardware', 'bay railing')
        for (px_, py_) in (rail[0], rail[-1]):
            C.rod('Bay rail end post', (px_, py_, zl + .07), (px_, py_, zl + .98), .035, 'hardware', 'bay railing', 8)
    # Corbel course under the bow: console blocks hanging from the piano-nobile floor edge.
    for (bx_, by_) in arc(A0 - .55, BAY_OUT - .60, 6, .15)[1:-1]:
        C.box('Bow corbel', (bx_, by_, LEVELS[0] - .12 - .36), (.40, .40, .72), 'stone', 'bay floors', 0)
    C.prism('Bay cornice', arc(A0 + .40, BAY_OUT + .40, 12, .15), 'z', z1 - .02, z1 + .55, 'stone', 'bay roof')
    cx, cy = CMX, CMY
    cz = PAR + CZ_UP
    # Bow frieze rising solid from the bay cornice to the dome foot, a moulding at mid-height; then the round dome-foot
    # cornice disc projecting about 1 m beyond the frieze all round on a bed mould, directly under the copper eave
    # (sources: strongly projecting cornice disc; v007 P1 1). The disc clears the corner pilaster caps.
    C.prism('Bow frieze', arc(A0, BAY_OUT, 16, .15), 'z', z1 + .55, cz - .50, 'stone', 'bay roof')
    C.prism('Frieze moulding', arc(A0 + .14, BAY_OUT + .14, 16, .15), 'z', z1 + 1.12, z1 + 1.26, 'stone', 'bay roof')
    C.rod('Frieze pedestal', (cx, cy, CORNICE - .10), (cx, cy, cz - .50), 2.75, 'stone', 'turret', 24)
    C.rod('Dome foot bed mould', (cx, cy, cz - .84), (cx, cy, cz - .50), DOME_R + .50, 'stone', 'turret', 32)
    C.rod('Dome foot cornice disc', (cx, cy, cz - .50), (cx, cy, cz - .05), DISC_R, 'stone', 'turret', 32)
    C.rod('Copper eave', (cx, cy, cz - .05), (cx, cy, cz + .16), DOME_R + .22, 'copper', 'turret', 32)
    C.rod('Copper skirt', (cx, cy, cz + .16), (cx, cy, cz + SKIRT_H), DOME_R + .04, 'copper', 'turret', 32)
    dz = cz + SKIRT_H
    # Pierced copper cresting on the disc lip: 28 small open arches on slender posts with ball finials, light between them.
    rc, nc, zb_, zt_ = DISC_R - .28, 28, cz - .05, cz + .60
    ring = [(cx + rc * math.cos(math.tau * k / nc), cy + rc * math.sin(math.tau * k / nc)) for k in range(nc + 1)]
    for k in range(nc):
        pa, pb = ring[k], ring[k + 1]
        am = math.tau * (k + .5) / nc; pm = (cx + rc * math.cos(am), cy + rc * math.sin(am))
        C.rod('Cresting post', (pa[0], pa[1], zb_), (pa[0], pa[1], zt_ - .16), .035, 'copper', 'turret', 6)
        C.rod('Cresting finial', (pa[0], pa[1], zt_ - .16), (pa[0], pa[1], zt_ + .10), .07, 'copper', 'turret', 6)
        C.beam('Cresting arch', (pa[0], pa[1], zt_ - .18), (pm[0], pm[1], zt_ + .02), .05, .05, 'copper', 'turret')
        C.beam('Cresting arch', (pm[0], pm[1], zt_ + .02), (pb[0], pb[1], zt_ - .18), .05, .05, 'copper', 'turret')
        C.beam('Cresting rail', (pa[0], pa[1], zb_ + .14), (pb[0], pb[1], zb_ + .14), .04, .04, 'copper', 'turret')
    dome(cx, cy, dz, DOME_R, DOME_H, segs=48, profile=DOME_PROFILE)
    # Eight continuous ribs seated on the shell: each follows the meridian profile in 27 short beams from the foot to
    # the lantern collar, its section half-embedded in the copper so no daylight shows between rib and shell (v007 P1 3).
    sp = smooth_profile(DOME_PROFILE, 30)
    base = math.atan2(CN[1], CN[0])
    for k in range(RIBS):
        a = base + math.tau * k / RIBS                     # between the dormers, which sit at odd multiples of 22.5 degrees
        prof = [(rf * DOME_R, zf * DOME_H) for rf, zf in sp if zf <= .905]
        for (r0, h0), (r1, h1) in zip(prof, prof[1:]):
            C.beam('Dome rib', (cx + math.cos(a) * (r0 + .07), cy + math.sin(a) * (r0 + .07), dz + h0 - .015),
                   (cx + math.cos(a) * (r1 + .07), cy + math.sin(a) * (r1 + .07), dz + h1 + .015), .17, .17, 'copper', 'turret')
    # Four smooth copper round dormers at 45 percent of the dome height with curved bonnet hoods merging into the shell (v007 P1 2).
    nr, nz = .91, .42                                       # dome surface normal at 45 percent height (radial, vertical)
    for da in (-67.5, -22.5, 22.5, 67.5):
        a = base + math.radians(da)
        ux, uy = math.cos(a), math.sin(a)
        px, py, pz = cx + ux * DOME_R * .92, cy + uy * DOME_R * .92, dz + DOME_H * .45
        n = (ux * nr, uy * nr, nz)
        q = lambda d: (px + n[0] * d, py + n[1] * d, pz + n[2] * d)
        tx_, ty_ = -uy, ux                                  # tangent; up vector on the surface
        up = (-ux * nz, -uy * nz, nr)
        C.rod('Dome dormer', q(-.40), q(.26), .52, 'copper', 'turret', 20)
        C.rod('Dome dormer rim', q(.24), q(.32), .56, 'copper', 'turret', 20)
        C.rod('Dome dormer glass', q(.26), q(.29), .42, 'trim', 'turret', 20)
        bonnet(q, (tx_, ty_, 0.0), up, .64, .74, .36, -.60)
    # Solid octagonal neck out of the apex carries the lantern; the base disc sits on the neck, never on daylight.
    lz = dz + DOME_H + .45
    C.rod('Lantern neck', (cx, cy, dz + DOME_H * .80), (cx, cy, lz + .02), NECK_R, 'copper', 'turret', 8)
    C.rod('Lantern base', (cx, cy, lz), (cx, cy, lz + .25), .9, 'copper', 'turret', 8)
    for k in range(8):
        a = math.tau * k / 8
        C.beam('Lantern column', (cx + math.cos(a) * .7, cy + math.sin(a) * .7, lz + .25), (cx + math.cos(a) * .7, cy + math.sin(a) * .7, lz + 1.6), .08, .08, 'pale', 'turret')
    C.rod('Lantern cap ring', (cx, cy, lz + 1.6), (cx, cy, lz + 1.8), .95, 'copper', 'turret', 8)
    dome(cx, cy, lz + 1.8, .9, 1.0, profile=DOME_PROFILE)
    C.rod('Finial', (cx, cy, lz + 2.75), (cx, cy, lz + 3.5), .07, 'hardware', 'turret', 8)
    # Square mitred pilasters at the chamfer corners (their faces bisect the corner angle) close the course, cornice and
    # balustrade ends of both neighbouring faces; square quoins at the three right-angle corners.
    for (qx, qy), (ox_, oy_) in (((CX0, CY0), (0, -1)), ((CX1, CY1), (-1, 0))):
        bxv, byv = ox_ + nx, oy_ + ny
        bl = (bxv ** 2 + byv ** 2) ** .5; bxv, byv = bxv / bl, byv / bl
        pf = C.Face((qx, qy, 0), (-byv, bxv, 0), (-bxv, -byv, 0), 'corner pilaster')
        pf.part('Chamfer corner pilaster', 0.0, 0.0, (PAR + .16) / 2, .95, .95, PAR + .16, 'stone', 'corner posts', 0)
        pf.part('Chamfer corner capital', 0.0, 0.0, CORNICE - .12, 2.05, 2.05, 1.12, 'stone', 'corner posts', 0)
        pf.part('Chamfer corner base', 0.0, 0.0, LEVELS[0] - .07, 1.25, 1.25, .46, 'stone', 'corner posts', 0)
    for (qx, qy) in ((-W / 2 - .1, D / 2 + .1), (W / 2 + .1, D / 2 + .1), (W / 2 + .1, -D / 2 - .1)):
        C.box('Corner quoin', (qx, qy, (PAR + .16) / 2), (1.3, 1.3, PAR + .16), 'stone', 'corner posts', 0)
        C.box('Corner quoin capital', (qx + (.14 if qx > 0 else -.14), qy + (.14 if qy > 0 else -.14), CORNICE - .12), (1.92, 1.92, 1.12), 'stone', 'corner posts', 0)
    C.CONTACTS.append(dict(name='Bowed bay on the rusticated ground floor; copper skirt on the bay cornice pedestal; lantern on a solid neck out of the dome apex; corner posts at every corner', bay_top_m=z1, dome_top_m=dz + DOME_H))


def bonnet(q, t, up, r0, r1, d0, d1, steps=6, arcs=11):
    """Copper bonnet hood over a round dormer: the upper half of a flaring shell from radius r0 at depth d0 (the dormer
    rim) back and outward to radius r1 at depth d1 (into the dome), with a small thickness."""
    def ring(d, r, lift):
        c = q(d)
        return [tuple(c[i] + up[i] * lift + (t[i] * math.cos(math.pi * j / (arcs - 1)) + up[i] * math.sin(math.pi * j / (arcs - 1))) * r for i in range(3)) for j in range(arcs)]
    rings_o = [ring(d0 + (d1 - d0) * j / steps, r0 + (r1 - r0) * j / steps, .55 * (j / steps) ** 2) for j in range(steps + 1)]
    rings_i = [ring(d0 + (d1 - d0) * j / steps, r0 + (r1 - r0) * j / steps - .07, .55 * (j / steps) ** 2) for j in range(steps + 1)]
    vs, fs = [], []
    for rg in rings_o + rings_i:
        vs.extend(rg)
    O = lambda j, k: j * arcs + k
    I = lambda j, k: (steps + 1) * arcs + j * arcs + k
    for j in range(steps):
        for k in range(arcs - 1):
            fs.append((O(j, k), O(j, k + 1), O(j + 1, k + 1), O(j + 1, k)))
            fs.append((I(j + 1, k), I(j + 1, k + 1), I(j, k + 1), I(j, k)))
        fs.append((O(j, 0), O(j + 1, 0), I(j + 1, 0), I(j, 0)))
        fs.append((I(j, arcs - 1), I(j + 1, arcs - 1), O(j + 1, arcs - 1), O(j, arcs - 1)))
    for k in range(arcs - 1):
        fs.append((I(0, k), I(0, k + 1), O(0, k + 1), O(0, k)))
        fs.append((O(steps, k), O(steps, k + 1), I(steps, k + 1), I(steps, k)))
    C.mesh('Dome dormer bonnet', vs, fs, 'copper', 'turret')


def half_ring(name, inner, outer, z0, z1, role, module):
    """Closed band between two open polylines (same point count) extruded from z0 to z1."""
    n = len(inner)
    vs = [(x, y, z0) for x, y in inner] + [(x, y, z0) for x, y in outer] + [(x, y, z1) for x, y in inner] + [(x, y, z1) for x, y in outer]
    I0, O0, I1, O1 = 0, n, 2 * n, 3 * n
    fs = []
    for i in range(n - 1):
        fs.append((I1 + i, O1 + i, O1 + i + 1, I1 + i + 1))      # top
        fs.append((I0 + i + 1, O0 + i + 1, O0 + i, I0 + i))      # bottom
        fs.append((O0 + i, O0 + i + 1, O1 + i + 1, O1 + i))      # outer side
        fs.append((I0 + i + 1, I0 + i, I1 + i, I1 + i + 1))      # inner side
    fs.append((I0, O0, O1, I1)); fs.append((O0 + n - 1, I0 + n - 1, I1 + n - 1, O1 + n - 1))
    C.mesh(name, vs, fs, role, module)


def smooth_profile(profile, n=30):
    """Catmull-Rom resample of a (radius, height) polyline so the shell reads as a swept surface, not a stack of cones."""
    pts = [profile[0]] + list(profile) + [profile[-1]]
    out = []
    segs = len(profile) - 1
    for i in range(n + 1):
        t = i / n * segs
        k = min(int(t), segs - 1); u = t - k
        p0, p1, p2, p3 = pts[k], pts[k + 1], pts[k + 2], pts[k + 3]
        out.append(tuple(.5 * ((2 * p1[c]) + (-p0[c] + p2[c]) * u + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * u * u + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * u * u * u) for c in range(2)))
    out[-1] = (0.0, out[-1][1])
    return out


def dome(cx, cy, z0, r, h, rings=5, segs=48, profile=None):
    vs, fs = [], []
    prof = smooth_profile(profile) if profile else [(math.cos(math.pi / 2 * j / rings), math.sin(math.pi / 2 * j / rings)) for j in range(rings + 1)]
    rings = len(prof) - 1
    for j in range(rings + 1):
        rr = max(r * prof[j][0], .001); zz = z0 + h * prof[j][1]
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
    A.sofa(-2.0, -D / 2 + 6.0, zl); A.desk(3.5, -D / 2 + 3.0, zl + .05)
    C.box('Salon partition', (-4.5, -D / 2 + 5.0, zl + 1.6), (.16, 8.0, 3.2), 'interior', 'partitions', 0)


def site():
    ext = 6.0
    C.box('South sidewalk', (0, -D / 2 - ext / 2, .0075), (W + 2 * ext, ext, .015), 'foundation', 'sidewalk', 0)
    C.box('West sidewalk', (-W / 2 - ext / 2, ext / 2, .0075), (ext, D + ext, .015), 'foundation', 'sidewalk', 0)
    C.box('Kerb south', (0, -D / 2 - ext + .06, .06), (W + 2 * ext, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb west', (-W / 2 - ext + .06, .06, .06), (.12, D + 2 * ext - .12, .12), 'stone', 'sidewalk', 0)
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
