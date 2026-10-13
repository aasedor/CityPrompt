"""Modernista iron-and-glass market hall, authored from the locked catalogue views of
barcelona_mercat / variant_0 (mercat_modernista).

Read from the pixels: a single-storey square hall on a paved plaza. Four gabled iron-and-glass wings
in a pinwheel cross around a square central lantern with a pyramidal roof (top view); the gable ends
carry great semicircular iron arches with stained-glass tympana, a wrought-iron crest and a coat of
arms, the south one over the main entrance between stone piers; lower aisle roofs fill the four corner
quadrants with small gablets along their eaves; the perimeter is a tiled dado wall with cast-iron
columns, iron-framed glazing above and coloured canvas awnings over every bay; stalls of produce inside.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-modernista-market-hall'
S = 46.0                          # square hall side
HW = 9.0                          # wing half-width (18 m wings)
EAVE_A = 6.8                      # aisle (quadrant) eave at the outer walls
EAVE_W = 10.0                     # wing eave over the quadrant roofs
RIDGE = 15.0                      # wing ridge
LANT = 7.0                        # central lantern half-side
LANT_TOP, LANT_APEX = 18.0, 21.6
DADO = 1.3
T = .30
G0 = .15
BAY = 4.6
EPS = .002
PLAZA = 14.0
PALETTE = dict(wall=(.62, .54, .44), joint=(.46, .40, .32), trim=(.16, .18, .17),
    pale=(.78, .74, .66), stone=(.72, .66, .56), roof=(.44, .42, .38), sand=(.70, .64, .52),
    foundation=(.52, .52, .50), glass=(.46, .54, .56), hardware=(.14, .16, .15),
    interior=(.80, .76, .68), floor=(.50, .48, .44), timber=(.40, .28, .16), blue=(.14, .22, .28),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.64, .62, .58), tile=(.40, .50, .46),
    stain_red=(.62, .16, .14), stain_gold=(.84, .64, .20), stain_blue=(.20, .34, .58), stain_green=(.24, .48, .30),
    awning_red=(.70, .14, .10), awning_yellow=(.86, .68, .16), awning_blue=(.16, .30, .60), gilt=(.80, .64, .26), produce=(.62, .32, .16))


def manifest(version):
    h = LANT_APEX + 2.5
    cams = G.camera_roster(S + 2 * PLAZA, S + 2 * PLAZA, h, [
        ('facade_close', (-14.0, -42.0, 5.0), (-4.0, -S / 2, 7.0), 45),
        ('architecture_close', (-40.0, -40.0, 14.0), (-S / 2 + 6.0, -S / 2 + 6.0, 8.0), 50),
        ('glass_close', (-10.0, -34.0, 3.0), (-6.0, -S / 2, 4.0), 50),
        ('great_arch', (-6.0, -52.0, 6.0), (0.0, -S / 2, 9.0), 40),
        ('aisle_arcade', (-30.0, -36.0, 3.0), (-14.0, -S / 2, 4.0), 40),
        ('lantern_roofs', (-40.0, -46.0, 30.0), (0.0, 0.0, 15.0), 45),
        ('crest_contact', (6.0, -40.0, 15.0), (0.0, -S / 2, 15.5), 45),
        ('plaza_awnings', (30.0, -38.0, 4.0), (10.0, -S / 2, 4.0), 40),
        ('interior', (0.0, -S / 2 + 2.0, 1.7), (0.0, 8.0, 5.0), 35),
        ('rear_court', (30.0, 40.0, 8.0), (0.0, S / 2, 8.0), 40)])
    for c in cams:
        if c['name'] == 'front':          # eye level on the plaza axis facing the great arch (locked front)
            c['location'] = (-12.0, -62.0, 1.7); c['target'] = (-2.0, -S / 2, 8.0); c['lens'] = 30; c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='barcelona_mercat/variant_0 (mercat_modernista)',
        measurement_contract=dict(dimensions_m=dict(width=S + 2 * PLAZA, depth=S + 2 * PLAZA, height=h),
            observed_storeys=1, storey_programme='single-storey market hall with a central lantern',
            plan='46 x 46 m square hall (top view) on a paved plaza: four 18 m gabled wings in a cross around a 14 m square lantern, lower aisle roofs in the four corner quadrants',
            section='tiled dado 1.3 m, cast-iron columns at 4.6 m with iron-framed glazing to the aisle eave at 6.8 m; wing eaves at 10 m over the quadrant roofs with clerestory glazing; wing ridges at 15 m; lantern to 18 m with a pyramid roof to 21.6 m',
            gables='each gable end a semicircular iron arch 16 m across with a glazed tympanum (stained glass on the south), iron lattice spandrels, bargeboards and a wrought-iron crest; the south gable over the main entrance between stone piers',
            perimeter='coloured canvas awnings over every bay, gablets along the quadrant eaves, bollards and trees on the plaza',
            inferred='the north and east gables repeat the south grammar with clear glass; interiors are stalls as teaching assumptions'),
        roof_contract=dict(type='gabled iron roofs with glazed strips, pyramid lantern roof, lean-to quadrant roofs', datum_m=EAVE_A, crowns_m=[RIDGE, LANT_APEX]),
        identity_contract=dict(owner='great iron gable arches with stained glass and crests, pinwheel of gabled wings around the square lantern, tiled dado with cast-iron columns and glazing, coloured awnings, plaza'),
        material_contract=dict(profile='source-palette clay: patterned tile dado in green-grey, dark cast iron, glass, stained-glass colour panels, brown-grey roof plates with glass strips, red, yellow and blue canvas awnings, stone piers', textured_keeper=False),
        programme_contract=dict(storeys=1, ground='market stalls in four aisles meeting under the lantern', upper='none', roof='lantern ventilation'),
        contact_contract=['Grade-zero slab and plaza', 'Columns on the dado plinth', 'Wing walls on interior columns over the quadrant roofs', 'Gable screens between the stone piers on the plinth', 'Lantern on the wing ridges', 'Awnings on arms from the columns'],
        runtime_contract=dict(scale='fixed_native_only', installation='not installed', review='NOT TESTED'),
        camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])
# ---- shared clay helpers (copied into each wave C family; kept identical) ----


def hole(name, u, z, w, h, **kw):
    return dict(id=name, u=u, z=z, w=w, h=h, **kw)


class Merge:
    """Batch many small boxes in face coordinates into one mesh per role."""
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


def framed(m, f, h, cols=1, rows=1, inset=.16, occupied='room', kind='window', frame='trim', glass='glass', lite=False):
    """Frame, bars and a single recessed pane inside a cut hole; no bevelled bars (black-corner issue of the window helper).
    lite: one dark frame plate behind the pane, for faces no source shows (vertex budget)."""
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    per = .07
    if lite:
        m.box(frame, u, inset + .06, z + hh / 2, w - .01, .08, hh - .01)
        m.box(glass, u, inset + .01, z + hh / 2, w - .03, .009, hh - .03)
        register(f, h, inset, kind, occupied)
        return
    for s in (-1, 1):
        m.box(frame, u + s * (w / 2 - per / 2), inset, z + hh / 2, per, .10, hh)
    m.box(frame, u, inset, z + hh - per / 2, w - 2 * per, .10, per)
    m.box(frame, u, inset, z + per / 2, w - 2 * per, .10, per)
    for i in range(1, cols):
        m.box(frame, u - w / 2 + w * i / cols, inset - .006, z + hh / 2, .05, .09, hh - 2 * per)
    for i in range(1, rows):
        m.box(frame, u, inset - .008, z + hh * i / rows, w - 2 * per, .085, .05)
    m.box(glass, u, inset + .037, z + hh / 2, w - 2 * per - .01, .009, hh - 2 * per - .01)
    register(f, h, inset, kind, occupied)


def reveal(m, f, h, inset=.16, role='stone'):
    """Lined reveal: four thin liners inside the cut from the face to the frame."""
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    for s in (-1, 1):
        m.box(role, u + s * (w / 2 - .02), inset / 2 - .01, z + hh / 2, .04, inset + .02, hh)
    m.box(role, u, inset / 2 - .01, z + hh - .02, w, inset + .02, .04)
    m.box(role, u, inset / 2 - .01, z + .02, w, inset + .02, .04)


def iron_balcony(m, f, u, z, w, depth=.8, role='hardware', slab='stone'):
    """Cantilevered balcony: stone slab with a merged iron lattice (top rail, end rails, mid rail, pickets)."""
    m.box(slab, u, -depth / 2 + .02, z - .10, w, depth + .04, .20)
    m.box(role, u, -depth + .04, z + .98, w, .05, .05)
    for e in (-1, 1):
        m.box(role, u + e * (w / 2 - .02), -depth / 2 + .02, z + .98, .05, depth - .04, .05)
    m.box(role, u, -depth + .04, z + .50, w, .03, .03)
    n = max(4, int(w / .30))
    for i in range(n + 1):
        m.box(role, u - w / 2 + .02 + (w - .04) * i / n, -depth + .04, z + .55, .03, .03, .86)
    for e in (-1, 1):
        m.box(role, u + e * (w / 2 - .02), -depth / 2 + .02, z + .55, .03, .03, .86)


def smooth_profile(profile, n=30):
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


def dome(name, cx, cy, z0, r, h, profile, role, module, segs=48, n=24):
    """Closed dome of revolution from a (radius fraction, height fraction) profile."""
    vs, fs = [], []
    prof = smooth_profile(profile, n)
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
    return C.mesh(name, vs, fs, role, module)


def rib_mesh(name, cx, cy, z0, a, prof, width, stand, role, module):
    """One continuous rib: rectangular section swept along a (radius, height) meridian, inner face sunk into the shell."""
    ux, uy = math.cos(a), math.sin(a)
    tx, ty = -uy, ux
    vs, fs = [], []
    n = len(prof)
    for i, (r, h) in enumerate(prof):
        r0, h0 = prof[max(i - 1, 0)]; r1, h1 = prof[min(i + 1, n - 1)]
        dr, dh = r1 - r0, h1 - h0
        L = math.hypot(dr, dh) or 1.0
        nr, nz = dh / L, -dr / L
        if nr < 0: nr, nz = -nr, -nz
        for dn in (-.06, stand + width):
            for dt in (-width / 2, width / 2):
                vs.append((cx + ux * (r + nr * dn) + tx * dt, cy + uy * (r + nr * dn) + ty * dt, z0 + h + nz * dn))
    for i in range(n - 1):
        o = i * 4
        fs += [(o + 2, o + 3, o + 7, o + 6), (o + 1, o + 0, o + 4, o + 5), (o + 0, o + 2, o + 6, o + 4), (o + 3, o + 1, o + 5, o + 7)]
    fs += [(0, 1, 3, 2), ((n - 1) * 4 + 2, (n - 1) * 4 + 3, (n - 1) * 4 + 1, (n - 1) * 4 + 0)]
    C.mesh(name, vs, fs, role, module)


def strip(name, lower, upper, z_lo, z_hi, role, module, closed=True):
    """Closed sloped band between two polygons with the same point count (a hip, mansard or valley ring). Thin shell: a
    second surface is offset below so the band reads as a plate."""
    n = len(lower)
    assert len(upper) == n
    t = .18
    vs = [(x, y, z_lo) for x, y in lower] + [(x, y, z_hi) for x, y in upper] + [(x, y, z_lo - t) for x, y in lower] + [(x, y, z_hi - t) for x, y in upper]
    L0, U0, L1, U1 = 0, n, 2 * n, 3 * n
    fs = []
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        j = (i + 1) % n
        fs.append((L0 + i, L0 + j, U0 + j, U0 + i))       # top surface
        fs.append((U1 + i, U1 + j, L1 + j, L1 + i))       # underside
        fs.append((L0 + j, L0 + i, L1 + i, L1 + j))       # eave edge
        fs.append((U0 + i, U0 + j, U1 + j, U1 + i))       # upper edge
    if not closed:
        fs.append((L0, U0, U1, L1)); fs.append((U0 + n - 1, L0 + n - 1, L1 + n - 1, U1 + n - 1))
    return C.mesh(name, vs, fs, role, module)


def street_tree(x, y, z=.015, height=8.0, spread=1.8):
    C.rod('Street tree trunk', (x, y, z), (x, y, z + height * .55), .16, 'timber', 'street planting', 8)
    for dx, dy in ((-.5, -.2), (.5, -.1), (.0, .5)):
        tip = (x + dx * spread, y + dy * spread, z + height * .72)
        C.rod('Street tree branch', (x, y, z + height * .5), tip, .06, 'timber', 'street planting', 6)
        A.foliage('Street tree crown', tip, (.9 * spread, .9 * spread, 1.3), detail=1)


def iron_fence(a, b, height=1.6, wall=.5, spacing=.26, role='hardware'):
    """Railing on a low stone wall between a and b (ground points)."""
    ax, ay = a; bx, by = b
    L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
    C.beam('Fence wall', (ax, ay, wall / 2), (bx, by, wall / 2), .30, wall, 'stone', 'fence')
    C.beam('Fence top rail', (ax, ay, wall + height - .03), (bx, by, wall + height - .03), .04, .04, role, 'fence')
    C.beam('Fence mid rail', (ax, ay, wall + .12), (bx, by, wall + .12), .035, .035, role, 'fence')
    n = max(2, int(L / spacing))
    for i in range(n + 1):
        px, py = ax + ux * L * i / n, ay + uy * L * i / n
        post = i % 10 == 0
        C.rod('Fence picket', (px, py, wall), (px, py, wall + height + (.12 if post else 0)), .035 if post else .014, role, 'fence', 6)


def eave_cornice(m, lo, hi, z, span_t=T, proj=.70, role='stone', modillions=True):
    """Projecting cornice at z (top of the corona): bed mould, modillions, corona."""
    span = hi - lo
    m.box(role, (lo + hi) / 2, -.10, z - .62, span - 2 * EPS, span_t + .20, .26)
    if modillions:
        n = max(2, int(span / .95))
        for i in range(n + 1):
            m.box(role, lo + .30 + (span - .60) * i / n, -(proj * .55), z - .32, .24, proj * 1.1 - .06, .34)
    m.box(role, (lo + hi) / 2, -(proj / 2 - .02), z - .13, span - 2 * EPS, span_t + proj, .26)
    m.box(role, (lo + hi) / 2, -(proj / 2 - .02), z, span - 2 * EPS, span_t + proj - .10, .06)


# ---- building ----

def quad(name, p0, p1, p2, p3, t, role, module):
    """Thin plate from four world points (top surface), thickness t straight down."""
    vs = [p0, p1, p2, p3] + [(x, y, z - t) for x, y, z in (p0, p1, p2, p3)]
    C.mesh(name, vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], role, module)


def tri(name, p0, p1, p2, t, role, module):
    vs = [p0, p1, p2] + [(x, y, z - t) for x, y, z in (p0, p1, p2)]
    C.mesh(name, vs, [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], role, module)


def outer_faces():
    return [C.Face((0, -S / 2, 0), (1, 0, 0), (0, 1, 0), 'south'), C.Face((S / 2, 0, 0), (0, 1, 0), (-1, 0, 0), 'east'),
            C.Face((0, S / 2, 0), (-1, 0, 0), (0, -1, 0), 'north'), C.Face((-S / 2, 0, 0), (0, -1, 0), (1, 0, 0), 'west')]


def aisle_wall(f, lo, hi, colour_offset=0):
    """Dado wall, cast-iron columns, iron-framed glazing to the aisle eave, coloured awning per bay."""
    nb = max(1, round((hi - lo) / BAY)); pitch = (hi - lo) / nb
    f.wall(f'{f.label} dado {lo:.0f}', lo, hi - EPS, G0, DADO, depth=T, role='tile', holes=())
    m = Merge(f)
    m.box('stone', (lo + hi) / 2, -.05, G0 + .20, hi - lo - 2 * EPS, T + .14, .40)       # plinth
    m.box('stone', (lo + hi) / 2, -.04, DADO + .08, hi - lo - 2 * EPS, T + .12, .16)      # dado cope
    G.brick_courses(f, lo + .02, hi - .02, G0 + .7, DADO - .1, (), spacing=.30)
    m.box('hardware', (lo + hi) / 2, T / 2, EAVE_A - .10, hi - lo - 2 * EPS, .28, .34)   # eaves beam
    for i in range(nb + 1):
        u = lo + pitch * i
        uu = min(max(u, lo + .22), hi - .22)
        a = f.p(uu, T / 2, DADO + .16); b = f.p(uu, T / 2, EAVE_A - .26)
        C.rod(f'{f.label} column', a, b, .17, 'hardware', 'columns', 10)
        C.rod(f'{f.label} column base', f.p(uu, T / 2, DADO + .14), f.p(uu, T / 2, DADO + .46), .24, 'hardware', 'columns', 10)
        C.rod(f'{f.label} column capital', f.p(uu, T / 2, EAVE_A - .62), f.p(uu, T / 2, EAVE_A - .26), .24, 'hardware', 'columns', 10)
        for sgn in (-1, 1):   # brackets
            if (sgn < 0 and i == 0) or (sgn > 0 and i == nb):
                continue
            C.beam('Column bracket', f.p(uu, T / 2, EAVE_A - 1.6), f.p(uu + sgn * 1.1, T / 2, EAVE_A - .32), .08, .08, 'hardware', 'columns')
    for i in range(nb):
        c = lo + pitch * (i + .5)
        w = pitch - .50
        # glazing panel between columns: glass sheet with an iron frame and a transom
        m.box('glass', c, T / 2, (DADO + .22 + EAVE_A - .34) / 2, w - .10, .012, EAVE_A - .34 - DADO - .22)
        m.box('hardware', c, T / 2, DADO + .22, w, .07, .08)
        m.box('hardware', c, T / 2, EAVE_A - .40, w, .07, .08)
        m.box('hardware', c, T / 2, DADO + 2.6, w, .06, .07)
        for k in range(1, 3):
            m.box('hardware', c - w / 2 + w * k / 3, T / 2, (DADO + .22 + EAVE_A - .34) / 2, .06, .06, EAVE_A - .34 - DADO - .22)
        # semicircular iron fanlight bars at the head (decorative arch within the bay)
        rr = w / 2 - .04
        for j in range(6):
            a0, a1 = math.pi * j / 6, math.pi * (j + 1) / 6
            C.beam('Bay arch', f.p(c + math.cos(a0) * rr, T / 2, EAVE_A - .44 - rr + math.sin(a0) * rr), f.p(c + math.cos(a1) * rr, T / 2, EAVE_A - .44 - rr + math.sin(a1) * rr), .06, .06, 'hardware', 'columns')
        C.OPENINGS.append(dict(id=f'{f.label} glazed bay {lo:.0f}-{i}', face=f.label, u=c, z=DADO + .22, width=w, height=EAVE_A - .34 - DADO - .22, kind='iron framed glazing above the dado', clear_wall_cut=False,
            carrier_depth_m=T, frame_inset_m=T / 2, pane_inset_m=T / 2, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='market hall'))
        # awning: sloped canvas on two arms, scalloped valance
        role = ('awning_red', 'awning_yellow', 'awning_blue')[(i + colour_offset) % 3]
        out = 1.9
        lower = [f.p(c - w / 2, -out, 0)[:2], f.p(c + w / 2, -out, 0)[:2]]
        upper = [f.p(c - w / 2, -.02, 0)[:2], f.p(c + w / 2, -.02, 0)[:2]]
        strip(f'{f.label} awning {i}', lower, upper, DADO + 2.30, DADO + 3.05, role, 'awnings', closed=False)
        m.box(role, c, -out + .02, DADO + 2.12, w, .04, .30)
        for k in range(int(w / .5) + 1):
            m.box(role, c - w / 2 + w * k / int(w / .5), -out + .02, DADO + 1.94, .26, .04, .10)
        m.box('hardware', c, -out + .05, DADO + 2.32, w + .04, .05, .05)
        for sgn in (-1, 1):
            C.beam('Awning arm', f.p(c + sgn * (w / 2 - .2), .0, DADO + 3.05), f.p(c + sgn * (w / 2 - .2), -out + .08, DADO + 2.32), .05, .05, 'hardware', 'awnings')
    m.flush('aisle wall')


def gable_end(f, main=False):
    """Great semicircular iron arch screen between stone piers under a gable with lattice spandrels and a crest."""
    half = HW
    R_ = 7.6
    zc = EAVE_W - 1.6                  # arch springing
    # Stone piers at both ends.
    for sgn in (-1, 1):
        u = sgn * (half - .70)
        f.part(f'{f.label} gable pier', u, T / 2 + .1, (G0 + EAVE_W + .2) / 2, 1.40, 1.60, EAVE_W + .2 - G0, 'stone', 'gable piers', 0)
        f.part(f'{f.label} gable pier cap', u, T / 2 + .1, EAVE_W + .35, 1.70, 1.90, .30, 'stone', 'gable piers', 0)
        f.part(f'{f.label} gable pier base', u, T / 2 + .1, G0 + .35, 1.70, 1.90, .70, 'stone', 'gable piers', 0)
    # Screen: a glass panel of arch shape (rectangle below the springing plus the semicircle), the entrance cut out.
    pts = [(-R_, DADO + .1), (R_, DADO + .1), (R_, zc)]
    for k in range(1, 16):
        a = math.pi * k / 16
        pts.append((R_ * math.cos(a), zc + R_ * math.sin(a)))
    pts.append((-R_, zc))
    screen = f.panel(f'{f.label} arch screen', pts, T / 2 - .006, T / 2 + .006, 'glass', 'gable screen')
    f.cut(screen, f'{f.label} entrance cut', 0.0, G0, 5.2, 5.4, depth=.4)
    m = Merge(f)
    # Stained-glass or clear tympanum: radial segments as coloured panels inside the semicircle for the main gable.
    if main:
        cols = ('stain_red', 'stain_gold', 'stain_blue', 'stain_green')
        for k in range(8):
            a0, a1 = math.pi * k / 8, math.pi * (k + 1) / 8
            am = (a0 + a1) / 2
            for rr, size in ((R_ * .78, .95), (R_ * .50, .80)):
                m.box(cols[(k + int(rr)) % 4], math.cos(am) * rr, T / 2 - .02, zc + math.sin(am) * rr, size, .02, size)
        m.box('stain_gold', 0.0, T / 2 - .03, zc + R_ * .30, 1.8, .03, 1.8)       # coat-of-arms shield
        m.box('stain_red', 0.0, T / 2 - .04, zc + R_ * .30, 1.2, .02, 1.2)
    else:
        m.box('stain_gold', 0.0, T / 2 - .03, zc + R_ * .34, 1.8, .03, 1.8)
        m.box('stain_red', 0.0, T / 2 - .04, zc + R_ * .34, 1.2, .02, 1.2)
    # Iron bars: radial and ring bars over the tympanum, mullions and transoms below.
    for k in range(9):
        a = math.pi * k / 8
        C.beam('Tympanum radial', f.p(0.0, T / 2 - .05, zc), f.p(math.cos(a) * (R_ - .25), T / 2 - .05, zc + math.sin(a) * (R_ - .25)), .07, .07, 'hardware', 'gable screen')
    for rr in (R_ * .35, R_ * .66):
        for k in range(12):
            a0, a1 = math.pi * k / 12, math.pi * (k + 1) / 12
            C.beam('Tympanum ring', f.p(math.cos(a0) * rr, T / 2 - .05, zc + math.sin(a0) * rr), f.p(math.cos(a1) * rr, T / 2 - .05, zc + math.sin(a1) * rr), .06, .06, 'hardware', 'gable screen')
    for u in (-5.6, -2.9, 2.9, 5.6):
        m.box('hardware', u, T / 2 - .05, (DADO + .1 + zc) / 2, .09, .09, zc - DADO - .1)
    for z in (DADO + .1, 5.6, zc - .05):
        m.box('hardware', 0.0, T / 2 - .05, z, 2 * R_, .09, .09)
    for sgn in (-1, 1):   # entrance jambs and head
        m.box('hardware', sgn * 2.65, T / 2 - .06, (G0 + 5.4) / 2, .16, .16, 5.4 - G0)
    m.box('hardware', 0.0, T / 2 - .06, 5.48, 5.5, .16, .16)
    # The great arch ring: thick iron archivolt with gilt rosettes, and the gable lattice spandrels to the bargeboards.
    for k in range(16):
        a0, a1 = math.pi * k / 16, math.pi * (k + 1) / 16
        pa = f.p(math.cos(a0) * (R_ + .32), T / 2 - .25, zc + math.sin(a0) * (R_ + .32)); pb = f.p(math.cos(a1) * (R_ + .32), T / 2 - .25, zc + math.sin(a1) * (R_ + .32))
        C.beam('Archivolt', pa, pb, .62, .52, 'hardware', 'great arch')
        am = (a0 + a1) / 2
        C.rod('Archivolt rosette', f.p(math.cos(am) * (R_ + .32), T / 2 - .52, zc + math.sin(am) * (R_ + .32)), f.p(math.cos(am) * (R_ + .32), T / 2 - .60, zc + math.sin(am) * (R_ + .32)), .20, 'gilt', 'great arch', 8)
    apex = RIDGE + .55
    for sgn in (-1, 1):
        C.beam('Bargeboard', f.p(sgn * (half + .60), T / 2 - .25, EAVE_W - .45), f.p(0.0, T / 2 - .25, apex), .26, .40, 'hardware', 'great arch')
        C.beam('Bargeboard lower', f.p(sgn * (half + .60), T / 2 - .25, EAVE_W - .85), f.p(0.0, T / 2 - .25, apex - .40), .14, .14, 'hardware', 'great arch')
        # lattice spandrel between the arch and the raking edge: diagonals
        for k in range(1, 7):
            u = sgn * (.9 + k * 1.15)
            z_top = apex - (apex - EAVE_W + .45) * abs(u) / (half + .60) - .25
            z_bot = zc + (max(R_ ** 2 - u ** 2, 0.0)) ** .5 + .35 if abs(u) < R_ else EAVE_W - .3
            if z_top > z_bot + .3:
                m.box('hardware', u, T / 2 - .12, (z_top + z_bot) / 2, .08, .08, z_top - z_bot)
    # Horizontal tie at the springing line across the gable and the eaves cornice ends.
    m.box('hardware', 0.0, T / 2 - .12, EAVE_W - .30, 2 * half + 1.0, .20, .24)
    # Wrought-iron crest at the apex and finial spikes along the bargeboards.
    for k in range(5):
        a = math.pi * (k + .5) / 5
        rr = 1.4
        C.beam('Crest scroll', f.p(0.0, T / 2 - .25, apex + .2), f.p(math.cos(a) * rr, T / 2 - .25, apex + .2 + math.sin(a) * rr), .05, .05, 'hardware', 'crest')
    C.rod('Crest finial', f.p(0.0, T / 2 - .25, apex), f.p(0.0, T / 2 - .25, apex + 2.6), .06, 'hardware', 'crest', 6)
    C.rod('Crest ball', f.p(0.0, T / 2 - .25, apex + 2.2), f.p(0.0, T / 2 - .25, apex + 2.5), .18, 'gilt', 'crest', 8)
    for sgn in (-1, 1):
        for k in range(1, 4):
            u = sgn * k * 2.4
            z = apex - (apex - EAVE_W + .45) * abs(u) / (half + .60)
            C.rod('Bargeboard spike', f.p(u, T / 2 - .25, z + .15), f.p(u, T / 2 - .25, z + .95), .035, 'hardware', 'crest', 6)
    m.flush('gable screen')
    C.OPENINGS.append(dict(id=f'{f.label} entrance', face=f.label, u=0.0, z=G0, width=5.2, height=5.4, kind='open entrance', clear_wall_cut=True, carrier_depth_m=.012, frame_inset_m=None, pane_inset_m=None,
        face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='market hall'))
    C.OPENINGS.append(dict(id=f'{f.label} arch screen', face=f.label, u=0.0, z=DADO + .1, width=2 * R_, height=zc + R_ - DADO - .1, kind='glazed iron arch screen', clear_wall_cut=False, carrier_depth_m=.012, frame_inset_m=0.0, pane_inset_m=0.0,
        face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='market hall'))


def wing_roofs():
    """Four gabled wings from the lantern walls to the gable ends; glazed strips; clerestory walls over the quadrant roofs."""
    t = .18
    for axis in ('y', 'x'):
        for sgn in (-1, 1):
            # cross-section in (across, z): eaves at +-HW, ridge at 0
            lo, hi = sgn * LANT, sgn * (S / 2 + .60)
            lo, hi = min(lo, hi), max(lo, hi)
            for side in (-1, 1):
                pts = [(0.0, RIDGE), (side * (HW + .5), EAVE_W - .5 * (RIDGE - EAVE_W) / HW), (side * (HW + .5), EAVE_W - .5 * (RIDGE - EAVE_W) / HW - t), (0.0, RIDGE - t)]
                C.prism(f'Wing roof {axis}{sgn}{side}', pts, 'y' if axis == 'y' else 'x', lo, hi, 'roof', 'wing roofs')
                # glazed strip along the slope (long rooflight) with iron edge bars
                g0, g1 = lo + 1.0, hi - 1.6
                a_lo, a_hi = side * 2.4, side * 6.4
                za = RIDGE - abs(a_lo) * (RIDGE - EAVE_W) / HW + .03; zb = RIDGE - abs(a_hi) * (RIDGE - EAVE_W) / HW + .03
                if axis == 'y':
                    quad(f'Wing rooflight {axis}{sgn}{side}', (a_lo, g0, za), (a_hi, g0, zb), (a_hi, g1, zb), (a_lo, g1, za), .04, 'glass', 'wing roofs')
                else:
                    quad(f'Wing rooflight {axis}{sgn}{side}', (g0, a_lo, za), (g0, a_hi, zb), (g1, a_hi, zb), (g1, a_lo, za), .04, 'glass', 'wing roofs')
            # ridge cap and purlin lines
            if axis == 'y':
                C.beam('Ridge cap', (0.0, lo, RIDGE + .06), (0.0, hi, RIDGE + .06), .30, .12, 'hardware', 'wing roofs')
            else:
                C.beam('Ridge cap', (lo, 0.0, RIDGE + .06), (hi, 0.0, RIDGE + .06), .30, .12, 'hardware', 'wing roofs')
    # Clerestory walls of the wings over the quadrant roofs: glazed trapezoids on iron posts, from the lantern corner
    # (where the quadrant roof reaches EAVE_W) out to the gable piers (quadrant eave at EAVE_A).
    k_slope = (EAVE_W - EAVE_A) / (S / 2 - HW)
    for axis in ('y', 'x'):
        for sgn in (-1, 1):
            for side in (-1, 1):
                # wall plane: axis 'y' wings have walls at x = side*HW running in y from sgn*HW to sgn*(S/2 - .7)
                pts = []
                u0, u1 = sgn * HW, sgn * (S / 2 - 1.4)
                for u in (u0, u1):
                    z_q = EAVE_W - k_slope * (abs(u) - HW)        # quadrant roof height at this point along the wall
                    pts.append((u, z_q - .35))
                pts.append((u1, EAVE_W + .30)); pts.append((u0, EAVE_W + .30))
                if axis == 'y':
                    f = C.Face((side * HW, 0, 0), (0, 1, 0), (-side, 0, 0), f'clerestory y{sgn}{side}')
                else:
                    f = C.Face((0, side * HW, 0), (1, 0, 0), (0, -side, 0), f'clerestory x{sgn}{side}')
                f.panel(f'{f.label} glazing', pts, -.006, .006, 'glass', 'clerestory')
                m = Merge(f)
                m.box('hardware', (u0 + u1) / 2, 0.0, EAVE_W + .18, abs(u1 - u0), .22, .28)
                n = max(1, round(abs(u1 - u0) / BAY))
                for i in range(n + 1):
                    u = u0 + (u1 - u0) * i / n
                    z_q = EAVE_W - k_slope * (abs(u) - HW)
                    m.box('hardware', u, 0.0, (z_q - .35 + EAVE_W + .04) / 2, .12, .12, EAVE_W + .04 - z_q + .35)
                m.flush('clerestory')
                C.OPENINGS.append(dict(id=f'{f.label} glazing', face=f.label, u=(u0 + u1) / 2, z=EAVE_A, width=abs(u1 - u0), height=EAVE_W - EAVE_A, kind='clerestory glazing', clear_wall_cut=False,
                    carrier_depth_m=.012, frame_inset_m=0.0, pane_inset_m=0.0, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='market hall'))
    # Quadrant roofs: two triangular plates per corner rising from the outer eaves to the wing corner at EAVE_W.
    for sx in (-1, 1):
        for sy in (-1, 1):
            oc = (sx * (S / 2 + .6), sy * (S / 2 + .6), EAVE_A - .05)
            ic = (sx * HW, sy * HW, EAVE_W - .02)
            ex = (sx * HW, sy * (S / 2 + .6), EAVE_A - .05)
            ey = (sx * (S / 2 + .6), sy * HW, EAVE_A - .05)
            tri(f'Quadrant roof {sx}{sy}a', oc, ex, ic, .16, 'roof', 'quadrant roofs')
            tri(f'Quadrant roof {sx}{sy}b', oc, ic, ey, .16, 'roof', 'quadrant roofs')
            # gablets along the two outer eaves (locked front: small gables over every other bay)
            for k in range(1, 3):
                for along in ('x', 'y'):
                    d = HW + k * 4.6 + .2
                    if along == 'x':
                        cx, cy = sx * d, sy * (S / 2 + .3)
                        f = C.Face((cx, cy, 0), (sx * 1.0, 0, 0), (0, -sy, 0), f'gablet {sx}{sy}{k}x')
                    else:
                        cx, cy = sx * (S / 2 + .3), sy * d
                        f = C.Face((cx, cy, 0), (0, sy * 1.0, 0), (-sx, 0, 0), f'gablet {sx}{sy}{k}y')
                    zb = EAVE_A - .3
                    f.panel(f'{f.label} front', [(-1.6, zb), (1.6, zb), (1.6, zb + 1.1), (0.0, zb + 2.3), (-1.6, zb + 1.1)], -.02, .12, 'hardware', 'gablets')
                    f.panel(f'{f.label} glass', [(-1.2, zb + .2), (1.2, zb + .2), (1.2, zb + 1.0), (0.0, zb + 1.95), (-1.2, zb + 1.0)], -.03, -.01, 'glass', 'gablets')
                    for sgn in (-1, 1):
                        a = f.p(sgn * 1.75, -.05, zb + 1.0); b = f.p(0.0, -.05, zb + 2.42)
                        C.beam('Gablet barge', a, b, .10, .16, 'hardware', 'gablets')
                        c_ = f.p(sgn * 1.75, 1.5, zb + 1.0 + 1.5 * k_slope * .0 + .35); d_ = f.p(0.0, 1.5, zb + 2.42 + .35)
                        quad(f'{f.label} slate', f.p(sgn * 1.75, -.05, zb + 1.0), f.p(0.0, -.05, zb + 2.42), d_, c_, .10, 'roof', 'gablets')
    # Central lantern on the ridges: square glazed clerestory with iron posts and a pyramid roof with a finial.
    L = LANT
    C.box('Lantern base ring', (0, 0, RIDGE - .6), (2 * L + .6, 2 * L + .6, 1.2), 'roof', 'lantern', 0)
    lf = A.faces(2 * L, 2 * L, 0, 0, 'lantern ')
    for f in lf:
        f.panel(f'{f.label} glazing', [(-L, RIDGE), (L, RIDGE), (L, LANT_TOP - .3), (-L, LANT_TOP - .3)], -.006, .006, 'glass', 'lantern')
        m = Merge(f)
        for i in range(7):
            m.box('hardware', -L + 2 * L * i / 6, 0.0, (RIDGE + LANT_TOP - .3) / 2, .14, .14, LANT_TOP - .3 - RIDGE)
        m.box('hardware', 0.0, 0.0, LANT_TOP - .34, 2 * L, .22, .30)
        m.box('hardware', 0.0, 0.0, RIDGE + .05, 2 * L, .16, .12)
        m.flush('lantern')
    C.OPENINGS.append(dict(id='lantern glazing', face='lantern', u=0.0, z=RIDGE, width=2 * L, height=LANT_TOP - .3 - RIDGE, kind='lantern glazing', clear_wall_cut=False, carrier_depth_m=.012, frame_inset_m=0.0, pane_inset_m=0.0,
        face_origin=[0, -L, 0], face_tangent=[1, 0, 0], face_inward=[0, 1, 0], occupied_space='market hall'))
    o = L + .6
    apex = (0.0, 0.0, LANT_APEX)
    for (p0, p1) in (((-o, -o), (o, -o)), ((o, -o), (o, o)), ((o, o), (-o, o)), ((-o, o), (-o, -o))):
        tri('Lantern roof', (p0[0], p0[1], LANT_TOP - .2), (p1[0], p1[1], LANT_TOP - .2), apex, .16, 'roof', 'lantern')
        quad('Lantern rooflight', (p0[0] * .78 + p1[0] * .22, p0[1] * .78 + p1[1] * .22, LANT_TOP - .1 + .01), (p0[0] * .22 + p1[0] * .78, p0[1] * .22 + p1[1] * .78, LANT_TOP - .1 + .01),
             ((p0[0] * .22 + p1[0] * .78) * .35, (p0[1] * .22 + p1[1] * .78) * .35, LANT_TOP - .1 + (LANT_APEX - LANT_TOP + .1) * .65 + .01), ((p0[0] * .78 + p1[0] * .22) * .35, (p0[1] * .78 + p1[1] * .22) * .35, LANT_TOP - .1 + (LANT_APEX - LANT_TOP + .1) * .65 + .01), .04, 'glass', 'lantern')
    C.rod('Lantern finial', (0, 0, LANT_APEX - .2), (0, 0, LANT_APEX + 2.0), .07, 'hardware', 'lantern', 6)
    C.rod('Lantern ball', (0, 0, LANT_APEX + 1.5), (0, 0, LANT_APEX + 1.85), .22, 'gilt', 'lantern', 8)
    C.CONTACTS.append(dict(name='Wing roofs between the lantern and the gable screens; clerestory walls on interior columns over the quadrant roofs; lantern base ring on the four ridges', ridge_m=RIDGE, lantern_top_m=LANT_TOP))


def interior():
    outline = [(-S / 2, -S / 2), (S / 2, -S / 2), (S / 2, S / 2), (-S / 2, S / 2)]
    C.prism('Hall slab', outline, 'z', 0.0, G0, 'foundation', 'foundation')
    # Interior cast-iron columns on the wing lines carry the clerestory walls; arched iron trusses across each wing.
    for axis in ('y', 'x'):
        for sgn in (-1, 1):
            for side in (-1, 1):
                n = 3
                for i in range(n + 1):
                    u = sgn * (HW + (S / 2 - 1.4 - HW) * i / n)
                    x, y = (side * HW, u) if axis == 'y' else (u, side * HW)
                    C.rod('Hall column', (x, y, G0), (x, y, EAVE_W - .3), .20, 'hardware', 'hall columns', 10)
                    C.rod('Hall column capital', (x, y, EAVE_W - .8), (x, y, EAVE_W - .3), .30, 'hardware', 'hall columns', 10)
            for i in range(1, 4):
                u = sgn * (HW + (S / 2 - 1.6 - HW) * i / 4)
                pts = []
                for k in range(13):
                    a = math.pi * k / 12
                    pts.append((-math.cos(a) * (HW - .3), EAVE_W - 1.2 + math.sin(a) * (RIDGE - EAVE_W + .4)))
                for (a_, za), (b_, zb) in zip(pts, pts[1:]):
                    pa = (a_, u, za) if axis == 'y' else (u, a_, za); pb = (b_, u, zb) if axis == 'y' else (u, b_, zb)
                    C.beam('Hall truss', pa, pb, .14, .30, 'hardware', 'trusses')
                for a_ in (-HW + .3, HW - .3):
                    pa = (a_, u, EAVE_W - 1.2) if axis == 'y' else (u, a_, EAVE_W - 1.2); pb = (a_, u, EAVE_W - .3) if axis == 'y' else (u, a_, EAVE_W - .3)
                    C.beam('Hall truss post', pa, pb, .14, .14, 'hardware', 'trusses')
    # Stalls: timber counters with produce boxes along the four aisles and around the lantern.
    for (x, y, w, d) in ((-5.5, -14.0, 3.2, 8.0), (5.5, -14.0, 3.2, 8.0), (-5.5, 14.0, 3.2, 8.0), (5.5, 14.0, 3.2, 8.0),
                         (-14.0, -5.5, 8.0, 3.2), (-14.0, 5.5, 8.0, 3.2), (14.0, -5.5, 8.0, 3.2), (14.0, 5.5, 8.0, 3.2),
                         (-15.0, -15.0, 6.0, 3.0), (15.0, -15.0, 6.0, 3.0), (-15.0, 15.0, 6.0, 3.0), (15.0, 15.0, 6.0, 3.0)):
        C.box('Stall counter', (x, y, G0 + .45), (w, d, .90), 'timber', 'stalls', 0)
        C.box('Stall produce', (x, y, G0 + 1.05), (w - .3, d - .3, .30), 'produce', 'stalls', 0)
        C.box('Stall canopy', (x, y, G0 + 2.9), (w + .4, d + .4, .08), 'awning_red' if (x + y) > 0 else 'awning_yellow', 'stalls', 0)
        for sx in (-1, 1):
            for sy in (-1, 1):
                C.rod('Stall post', (x + sx * (w / 2 - .1), y + sy * (d / 2 - .1), G0 + .9), (x + sx * (w / 2 - .1), y + sy * (d / 2 - .1), G0 + 2.86), .03, 'hardware', 'stalls', 6)
    C.qa_room_light('Hall south', (0.0, -12.0, 8.0), 160, 8.0); C.qa_room_light('Hall north', (0.0, 12.0, 8.0), 120, 8.0)
    C.qa_room_light('Hall east', (12.0, 0.0, 8.0), 120, 8.0); C.qa_room_light('Hall west', (-12.0, 0.0, 8.0), 120, 8.0)
    C.qa_room_light('Lantern', (0.0, 0.0, 12.0), 140, 8.0)


def plaza():
    ext = PLAZA
    C.box('Plaza paving', (0, 0, .0075), (S + 2 * ext, S + 2 * ext, .015), 'foundation', 'plaza', 0)
    for u in range(-5, 6):
        C.rod('Bollard', (u * 4.2, -S / 2 - 7.0, .015), (u * 4.2, -S / 2 - 7.0, .9), .08, 'hardware', 'plaza', 6)
    for x, y in ((-S / 2 - 8.0, -14.0), (-S / 2 - 8.0, 2.0), (-S / 2 - 8.0, 18.0), (S / 2 + 8.0, -14.0), (S / 2 + 8.0, 2.0), (S / 2 + 8.0, 18.0), (-20.0, S / 2 + 8.0), (0.0, S / 2 + 8.0), (20.0, S / 2 + 8.0)):
        street_tree(x, y, .015, height=9.0, spread=2.4)
    for sgn in (-1, 1):
        C.rod('Lamp post', (sgn * 16.0, -S / 2 - 9.0, .015), (sgn * 16.0, -S / 2 - 9.0, 6.0), .08, 'hardware', 'plaza', 8)
        C.rod('Lamp head', (sgn * 16.0, -S / 2 - 9.0, 6.0), (sgn * 16.0, -S / 2 - 9.0, 6.5), .25, 'pale', 'plaza', 8)


def build():
    plaza()
    interior()
    faces = outer_faces()
    for i, f in enumerate(faces):
        span = S
        lo, hi = (-span / 2, span / 2 - EPS) if i % 2 == 0 else (-span / 2 + T, span / 2 - T)
        aisle_wall(f, lo, -HW - 1.4, colour_offset=i)
        aisle_wall(f, HW + 1.4, hi, colour_offset=i + 1)
        gable_end(f, main=(i == 0))
    wing_roofs()


LIGHT_RIG = dict(key=(-46, -54, 50), fill=(50, -28, 36), rear=(-20, 54, 44), target=(0, 0, 8.0), gain=7.5)
