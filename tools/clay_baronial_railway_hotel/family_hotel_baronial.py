"""Scottish Baronial railway hotel, authored from the locked catalogue views of
chateauesque_grand_railway_hotel / variant_0 (scottish_baronial_granite_tower).

Read from the pixels: a six-storey pink-grey granite quadrangle around an open court, streets south and
west. A square entrance tower a quarter of the way along the south face with a pointed-arch porte-cochere
through to the court, a crenellated parapet and round tourelles with conical caps at its front corners;
round corner tourelles corbelled out above the first storey with conical slate roofs; crow-stepped wall
gables rising through the eaves; steep slate roofs with dormers and chimney stacks; sash windows with
stone surrounds in rusticated granite; an iron fence on a low wall with lawn strips and trees.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G
from contract import subtract_openings

SLUG = 'clay-baronial-railway-hotel'
W, D = 58.0, 50.0                 # quadrangle footprint
WING = 14.0                       # wing depth; court 30 x 22 m
T = .40
G0 = .15
LEVELS = [5.4, 9.3, 13.2, 17.1]   # tall ground floor plus four upper floors: five window rows below the eaves (v001 P0 1)
EAVE = 21.0
RIDGE = 31.0                      # steep slate roofs, about 55 degrees (v001 P1 12)
TX, TW, TD, TOUT = 0.0, 10.0, 11.6, 1.6       # entrance tower centred on the south face (locked top), width, depth (with projection), projection
TOWER_TOP = 34.0
PASS_W = 7.4                      # passage carrier width on the court face (arch 5 m between 1.2 m piers)
BAY = 4.8                         # about five bays from the tower to the corner tourelle (v001 P1 10)
EPS = .002
SITE = (-W / 2 - 12.0, W / 2 + 8.0, -D / 2 - 14.0, D / 2 + 8.0)
PALETTE = dict(wall=(.60, .47, .41), joint=(.40, .30, .27), trim=(.22, .20, .18),
    pale=(.76, .72, .66), stone=(.70, .62, .56), roof=(.20, .22, .26), sand=(.70, .64, .52),
    foundation=(.46, .46, .45), glass=(.44, .50, .52), hardware=(.12, .12, .12),
    interior=(.80, .76, .68), floor=(.46, .44, .42), timber=(.36, .26, .16), blue=(.14, .22, .28),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.64, .62, .58), lead=(.42, .44, .46),
    rustic=(.56, .44, .39))


def manifest(version):
    h = TOWER_TOP + 6.0
    cams = G.camera_roster(W + 16.0, D + 16.0, h, [
        ('facade_close', (-30.0, -48.0, 6.0), (-10.0, -D / 2, 10.0), 45),
        ('architecture_close', (-54.0, -52.0, 20.0), (-W / 2 + 4.0, -D / 2 + 4.0, 16.0), 50),
        ('glass_close', (2.0, -36.0, 6.5), (6.0, -D / 2, 7.5), 50),
        ('entrance_tower', (-22.0, -62.0, 26.0), (TX, -D / 2, 25.0), 45),
        ('porte_cochere', (-12.0, -44.0, 2.0), (TX, -D / 2 - TOUT, 4.5), 40),
        ('corner_tourelle', (-50.0, -50.0, 24.0), (-W / 2, -D / 2, 24.0), 45),
        ('crow_gables', (16.0, -48.0, 22.0), (12.0, -D / 2, 24.0), 45),
        ('roof_court', (-60.0, -66.0, 56.0), (0.0, 0.0, 22.0), 45),
        ('interior', (14.0, -D / 2 + 9.0, LEVELS[0] + 1.6), (14.0, -D / 2 + .5, LEVELS[0] + 1.4), 50),
        ('rear_court', (9.0, 6.0, 2.5), (TX, -D / 2 + WING, 7.0), 40)])
    for c in cams:
        if c['name'] == 'front':          # eye level from the south-west on the street, tower at the left (locked front)
            c['location'] = (-9.0, -64.0, 1.7); c['target'] = (12.0, -D / 2 + 2.0, 12.0); c['lens'] = 28; c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='chateauesque_grand_railway_hotel/variant_0 (scottish_baronial_granite_tower)',
        measurement_contract=dict(dimensions_m=dict(width=SITE[1] - SITE[0], depth=SITE[3] - SITE[2], height=h),
            observed_storeys=5, storey_programme='tall ground floor of public rooms, four guest-room storeys, attic rooms in the gables and dormers',
            plan='58 x 50 m quadrangle (top view) of 14 m wings around a 30 x 22 m paved court with four corner trees, streets south and west; entrance tower 10 m square centred on the south face, projecting 1.6 m',
            facade='bays at 4.8 m: tall ground-floor windows 1.8 x 3.4 m and sash windows 1.6 x 2.6 m with stone surrounds in rusticated granite with recessed joints; string courses at each floor; corbelled eaves course at 21.0 m; two-bay crow-stepped wall gables 9 m wide rising 7 m through the eaves with two windows each, beside the tower and the tourelles',
            levels_m=[G0] + LEVELS, eave_m=EAVE, ridge_m=RIDGE,
            tower='square entrance tower to 34 m with a crenellated parapet, pointed-arch porte-cochere 5 x 7 m through the south wing to the court, round tourelles 2.2 m across at the two front corners from 13 m with conical caps to 39 m, crest panel over the arch',
            tourelles='round corner tourelles 4.8 m across corbelled out at 7 m with cut windows and conical slate roofs to 31.5 m at the four outer corners; intermediate tourelles 3.2 m across corbelled out at 9 m on the west, east and north faces (locked top)',
            roof='steep slate hipped ring roof 21.0 to 31.0 m with gabled dormers between the wall gables, chimney stacks on the ridge',
            inferred='north and east faces repeat the grammar with tourelles and gables; court faces carry one central gable each; interiors are teaching assumptions'),
        roof_contract=dict(type='slate hipped ring roof with wall gables and dormers; flat tower roof behind crenellations; conical tourelle roofs', datum_m=EAVE, crowns_m=[RIDGE, TOWER_TOP, 39.0]),
        identity_contract=dict(owner='crenellated entrance tower with the porte-cochere and tourelles, conical corner tourelles, crow-stepped gables, steep slate roofs, rusticated granite with sash windows, iron fence and lawn'),
        material_contract=dict(profile='source-palette clay: pink-grey granite with recessed rustication, pale stone dressings, dark slate, lead flashings, dark sash frames, black iron', textured_keeper=False),
        programme_contract=dict(storeys=7, ground='reception, lounges and dining through the porte-cochere', upper='guest rooms off double-loaded corridors', roof='attic rooms in the dormers'),
        contact_contract=['Grade-zero slab and sidewalks', 'Tower on the south wing; tourelles on corbel cones from the first-storey wall', 'Wall gables continuing the carriers through the eaves; gable roofs into the main slopes', 'Dormers seated on the slopes', 'Chimneys on the ridge'],
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

def cone(name, cx, cy, z0, r0, z1, r1, role, module, segs=24):
    vs = [(cx + r0 * math.cos(math.tau * i / segs), cy + r0 * math.sin(math.tau * i / segs), z0) for i in range(segs)]
    vs += [(cx + max(r1, .001) * math.cos(math.tau * i / segs), cy + max(r1, .001) * math.sin(math.tau * i / segs), z1) for i in range(segs)]
    fs = [tuple(range(segs - 1, -1, -1)), tuple(range(segs, 2 * segs))] + [(i, (i + 1) % segs, (i + 1) % segs + segs, i + segs) for i in range(segs)]
    return C.mesh(name, vs, fs, role, module)


def pointed_fill(f, u, z_top, w, rise, role='stone', d0=-.03, d1=None):
    d1 = T + .02 if d1 is None else d1
    pts = [(-w / 2, z_top), (w / 2, z_top), (w / 2, z_top - rise)]
    for k in range(1, 8):
        x = w / 2 - w * k / 8
        pts.append((x, z_top - rise + ((w ** 2 - (abs(x) + w / 2) ** 2) ** .5) * rise / (w * .866)))
    pts.append((-w / 2, z_top - rise))
    f.panel('Pointed arch spandrel', [(u + a, b) for a, b in pts], d0, d1, role, 'arches')


def rustication(f, lo, hi, z0, z1, holes, spacing=.62, joint=.035):
    """Recessed granite coursing: joint grooves as dark strips sunk into the carrier face (v001 P1 11), batched."""
    vs, fs = [], []
    for row in range(int((z1 - z0) / spacing)):
        z = z0 + row * spacing
        for a, b in subtract_openings(lo, hi, z, z + joint, holes):
            o = len(vs)
            vs.extend([f.p(a, -.004, z), f.p(b, -.004, z), f.p(b, -.004, z + joint), f.p(a, -.004, z + joint), f.p(a, .05, z), f.p(b, .05, z), f.p(b, .05, z + joint), f.p(a, .05, z + joint)])
            fs.extend([(o, o + 1, o + 2, o + 3), (o + 7, o + 6, o + 5, o + 4), (o, o + 4, o + 5, o + 1), (o + 1, o + 5, o + 6, o + 2), (o + 2, o + 6, o + 7, o + 3), (o + 3, o + 7, o + 4, o)])
    if fs:
        C.mesh(f.label + ' rustication joints', vs, fs, 'joint', 'rustication')


def window_dressing(m, h, street):
    for sgn in (-1, 1):
        m.box('stone', h['u'] + sgn * (h['w'] / 2 + .10), -.03, h['z'] + h['h'] / 2, .20, T + .12, h['h'] + .20)
    m.box('stone', h['u'], -.05, h['z'] + h['h'] + .15, h['w'] + .50, T + .16, .22)
    m.box('stone', h['u'], -.07, h['z'] - .08, h['w'] + .36, T + .20, .12)


def elevation(f, lo, hi, street=True, gables=(), skip_bays=()):
    """One face: rusticated granite carrier, tall ground-floor windows, sash windows with stone dressings, string
    courses, corbelled eaves course; optional two-bay wall gables centred on bay boundaries given in `gables`."""
    span = hi - lo
    nb = max(1, round(span / BAY))
    pitch = span / nb
    holes = []
    for i in range(nb):
        if i in skip_bays:
            continue
        c = lo + pitch * (i + .5)
        holes.append(hole(f'{f.label} ground window {i}', c, 1.0, 1.8, 3.4, level=-1))
        for k, zl in enumerate(LEVELS):
            holes.append(hole(f'{f.label} window {i}-{k}', c, zl + .9, 1.6, 2.6, level=k))
    f.wall(f'{f.label} carrier', lo, hi - EPS, G0, EAVE + .30, depth=T, role='wall', holes=holes)
    if street:
        rustication(f, lo + .02, hi - .02, G0 + .35, EAVE - .5, holes)
    else:
        G.brick_courses(f, lo + .02, hi - .02, G0 + .3, EAVE - .4, holes, spacing=.95)
    m = Merge(f)
    for h in holes:
        if street:
            reveal(m, f, h, .16, 'stone')
        framed(m, f, h, cols=2, rows=2, occupied='guest room' if h['level'] >= 0 else 'lounge', lite=not street)
        if street:
            window_dressing(m, h, street)
        else:
            m.box('stone', h['u'], -.05, h['z'] + h['h'] + .15, h['w'] + .50, T + .16, .22)
    for zl in LEVELS:
        m.box('stone', (lo + hi) / 2, -.04, zl - .12, span - 2 * EPS, T + .14, .18)
    m.box('stone', (lo + hi) / 2, -.07, G0 + .55, span - 2 * EPS, T + .20, .40)          # plinth course
    # Corbelled eaves course: continuous corbel table under a projecting stone cornice (v001 P1 12).
    m.box('stone', (lo + hi) / 2, -.20, EAVE - .16, span - 2 * EPS, T + .46, .32)
    nc = max(2, int(span / 1.2))
    for i in range(nc + 1):
        m.box('stone', lo + .3 + (span - .6) * i / nc, -.14, EAVE - .52, .30, T + .34, .40)
    m.flush('facade')
    for gc in gables:
        crow_gable(f, gc, EAVE, holes)
    return pitch


def crow_gable(f, u, z_e, holes, w=9.0, rise_m=7.0):
    """Two-bay crow-stepped wall gable: the carrier plane continued through the eaves as a stepped stone-coped gable with
    two windows, and a slate gable roof whose ridge descends into the main slope (v001 P1 8, P0 6)."""
    k = (WING / 2) / (RIDGE - EAVE)          # run per metre of rise on the main slope
    rise, run = .60, .55
    steps_r = []
    x, z = w / 2, z_e + .40
    treads = [(w / 2, None, z_e + .40)]
    while x - run > .45:
        x -= run; z += rise
        steps_r.append((x, z))
    top = z
    pts = [(-w / 2, z_e - .6), (w / 2, z_e - .6), (w / 2, z_e + .40)]
    right = []
    xx, zz = w / 2, z_e + .40
    for (x2, z2) in steps_r:
        right += [(x2, zz), (x2, z2)]
        xx, zz = x2, z2
    pts += right + [(.45, top), (-.45, top)] + [(-a, b) for a, b in reversed(right)] + [(-w / 2, z_e + .40)]
    panel = f.panel(f'{f.label} crow gable {u:.0f}', [(u + a, b) for a, b in pts], -.05, T, 'wall', 'gables')
    m = Merge(f)
    for sgn in (-1, 1):
        ww, hw, zw = 1.6, 2.4, z_e + 1.0
        uu = u + sgn * 2.4
        f.cut(panel, f'{f.label} gable window cut {u:.0f}{sgn}', uu, zw, ww, hw, depth=T + .1)
        h = hole(f'{f.label} gable window {u:.0f}{sgn}', uu, zw, ww, hw)
        reveal(m, f, h, .16, 'stone'); framed(m, f, h, cols=2, rows=2, occupied='attic room')
        window_dressing(m, h, True)
    rustication(f, u - w / 2 + .02, u + w / 2 - .02, z_e + .3, top - .3, [hole('g', u + sgn * 2.4, z_e + 1.0, 1.6, 2.4) for sgn in (-1, 1)])
    # Copes: one block on every tread, from the eave tread up to the apex block, built from the same step vertices.
    tread_edges = [(w / 2, z_e + .40)] + steps_r
    for sgn in (-1, 1):
        for (xa, za), (xb, zb) in zip(tread_edges, tread_edges[1:]):
            # tread between xa (outer) and xb (inner) at height za (the lower of the pair)
            m.box('stone', u + sgn * ((xa + xb) / 2 + .03), -.10, za + .07, (xa - xb) + .14, T + .26, .16)
    m.box('stone', u, -.10, top + .07, 1.1, T + .26, .16)
    m.flush('gables')
    C.rod('Gable finial', f.p(u, -.02, top + .1), f.p(u, -.02, top + 1.0), .06, 'stone', 'gables', 6)
    # Slate gable roof behind the panel: two plates from the ridge to the eaves, the ridge descending into the main slope.
    z_apex = top - .30
    d_ridge = (z_apex - z_e) * k - .05
    for sgn in (-1, 1):
        a = f.p(u, T - .02, z_apex); b = f.p(u, d_ridge, z_e + d_ridge / k + .02)
        c_ = f.p(u + sgn * (w / 2 - .50), T - .02, z_e + .42); d_ = f.p(u + sgn * (w / 2 - .50), d_ridge, z_e + d_ridge / k - 1.6)
        vs = [a, b, d_, c_]
        vs += [(x, y, z - .18) for x, y, z in vs]
        C.mesh('Gable slate', vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 'roof', 'gables')


def roof_dormer(f, u, z_e, rise, run, w=1.9):
    k = run / rise
    d0 = .70
    z_em = z_e + d0 / k
    z_top = z_em + 2.30
    zw, hw, ww = z_em + .45, 1.5, .9
    front = f.panel(f'{f.label} dormer front', [(u - w / 2, z_em - .5), (u + w / 2, z_em - .5), (u + w / 2, z_top), (u, z_top + .75), (u - w / 2, z_top)], d0 - .16, d0 + .10, 'stone', 'dormers')
    f.cut(front, f'{f.label} dormer window cut', u, zw, ww, hw, depth=.30)
    g = C.Face(f.p(0, d0 - .16, 0), f.t, f.n, f.label + ' dormer')
    mg = Merge(g)
    h = hole(f'{f.label} dormer window {u:.1f}', u, zw, ww, hw)
    framed(mg, g, h, cols=1, rows=2, inset=.10, occupied='attic room', kind='dormer window')
    mg.flush('dormers')
    d_back = d0 + 2.4
    for sgn in (-1, 1):
        uu = u + sgn * (w / 2 - .14)
        pts = [(d0 - .12, z_em - .5), (d0 - .12, z_top - .03), (d_back, z_top - .03), (d_back, z_e + d_back / k - .9)]
        vs = [f.p(uu - .06, d, z) for d, z in pts] + [f.p(uu + .06, d, z) for d, z in pts]
        fs = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        C.mesh('Dormer cheek', vs, fs, 'stone', 'dormers')
    z_apex = z_top + .80
    d_ridge = (z_apex - z_e) * k - .1
    for sgn in (-1, 1):
        a = f.p(u, d0 - .32, z_apex); b = f.p(u, d_ridge, z_e + d_ridge / k + .02)
        c_ = f.p(u + sgn * (w / 2 + .22), d0 - .32, z_top - .10); d_ = f.p(u + sgn * (w / 2 + .22), d_ridge, z_e + d_ridge / k - .8)
        vs = [a, b, d_, c_]
        vs += [(x, y, z - .16) for x, y, z in vs]
        C.mesh('Dormer slate', vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 'roof', 'dormers')


def tourelle(cx, cy, r, base, top, cap_top, facing, windows=True, label='tourelle'):
    """Round corbelled tourelle: corbel cone, shaft with string courses and cut windows on the outward angles, conical
    slate roof and finial (v001 P0 5: windows are pockets cut into the shaft, framed and glazed inside)."""
    cone(f'{label} corbel', cx, cy, base - 2.2, .45, base, r, 'stone', 'tourelles', 28)
    shaft = C.rod(f'{label} shaft', (cx, cy, base), (cx, cy, top), r, 'wall', 'tourelles', 28)
    for zl in LEVELS:
        if zl > base + .5:
            C.rod(f'{label} string', (cx, cy, zl - .12), (cx, cy, zl + .06), r + .10, 'stone', 'tourelles', 28)
    if windows:
        for zl in [z for z in LEVELS if z > base + .5] + ([EAVE + .6] if top > EAVE + 3.4 else []):
            for da in (-32.0, 32.0):
                a = facing + math.radians(da)
                ux, uy = math.cos(a), math.sin(a)
                g = C.Face((cx + ux * (r - .05), cy + uy * (r - .05), 0), (-uy, ux, 0), (-ux, -uy, 0), f'{label} window face')
                h = hole(f'{label} window {zl:.0f}{da:+.0f}', 0.0, zl + .9, .9, 2.0)
                g.cut(shaft, h['id'] + ' cut', 0.0, zl + .9, .9, 2.0, depth=.55)
                mg = Merge(g)
                framed(mg, g, h, cols=1, rows=2, inset=.16, occupied='tourelle room', lite=False)
                mg.box('stone', 0.0, -.03, zl + .9 + 2.0 + .14, 1.3, .20, .20)
                mg.box('stone', 0.0, -.04, zl + .9 - .08, 1.2, .22, .12)
                mg.flush('tourelles')
    C.rod(f'{label} eaves', (cx, cy, top), (cx, cy, top + .35), r + .25, 'stone', 'tourelles', 28)
    cone(f'{label} roof', cx, cy, top + .35, r + .30, cap_top, 0.0, 'roof', 'tourelles', 28)
    C.rod(f'{label} finial', (cx, cy, cap_top - .1), (cx, cy, cap_top + 1.0), .06, 'hardware', 'tourelles', 6)


def tower():
    y0 = -D / 2 - TOUT
    x0, x1 = TX - TW / 2, TX + TW / 2
    front = C.Face((TX, y0, 0), (1, 0, 0), (0, 1, 0), 'tower front')
    arch = hole('Porte-cochere', 0.0, G0, 5.0, 7.0, kind='open arch')
    holes = [arch]
    for k, zl in enumerate(LEVELS):
        if zl < 7.5:
            continue
        for du in (-1.8, 1.8):
            holes.append(hole(f'tower window {k}{du:+.0f}', du, zl + .9, 1.5, 2.6, level=k))
    holes.append(hole('tower upper window', 0.0, EAVE + 1.6, 2.2, 3.6, level=9))
    front.wall('tower front carrier', -TW / 2, TW / 2, G0, TOWER_TOP - .20, depth=T, role='wall', holes=holes)
    rustication(front, -TW / 2 + .02, TW / 2 - .02, G0 + .35, TOWER_TOP - 1.6, holes)
    m = Merge(front)
    for h in holes[1:]:
        reveal(m, front, h, .16, 'stone'); framed(m, front, h, cols=2, rows=2, occupied='tower rooms')
        window_dressing(m, h, True)
    pointed_fill(front, 0.0, arch['z'] + arch['h'], arch['w'], 2.2, 'stone')
    m.box('stone', 0.0, -.10, arch['z'] + arch['h'] + .30, arch['w'] + 1.6, T + .26, .36)
    for sgn in (-1, 1):
        m.box('stone', sgn * (arch['w'] / 2 + .45), -.14, (G0 + arch['z'] + arch['h'] - 2.2) / 2, .70, T + .34, arch['z'] + arch['h'] - 2.2 - G0)
    m.box('stone', 0.0, -.12, arch['z'] + arch['h'] + 1.6, 2.4, T + .30, 1.6)      # crest panel
    m.box('wall', 0.0, -.20, arch['z'] + arch['h'] + 1.6, 1.6, T + .34, 1.1)
    for zl in LEVELS:
        if zl > 7.5:
            m.box('stone', 0.0, -.04, zl - .12, TW - 2 * EPS, T + .14, .18)
    m.box('stone', 0.0, -.18, TOWER_TOP - 1.3, TW - 2 * EPS, T + .42, .34)
    m.flush('tower')
    C.OPENINGS.append(dict(id=arch['id'], face='tower front', u=0.0, z=arch['z'], width=arch['w'], height=arch['h'], kind='open arch', clear_wall_cut=True, carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None,
        face_origin=list(front.o), face_tangent=list(front.t), face_inward=list(front.n), occupied_space='open porte-cochere passage to the court'))
    for sgn, label in ((-1, 'tower west'), (1, 'tower east')):
        x = TX + sgn * TW / 2
        f = C.Face((x, y0 + TD / 2, 0), (0, sgn, 0), (-sgn, 0, 0), label)
        hs = [hole(f'{label} window {k}', 0.0, zl + .9, 1.5, 2.6) for k, zl in enumerate(LEVELS) if zl > 7.5] + [hole(f'{label} upper window', 0.0, EAVE + 1.6, 1.8, 3.6)]
        f.wall(f'{label} carrier', -TD / 2 + T, TD / 2, G0, TOWER_TOP - .20, depth=T, role='wall', holes=hs)
        rustication(f, -TD / 2 + T + .02, TD / 2 - .02, G0 + .35, TOWER_TOP - 1.6, hs)
        mm = Merge(f)
        for h in hs:
            reveal(mm, f, h, .16, 'stone'); framed(mm, f, h, cols=2, rows=2, occupied='tower rooms')
            window_dressing(mm, h, True)
        mm.box('stone', 0.0, -.18, TOWER_TOP - 1.3, TD - T - 2 * EPS, T + .42, .34)
        mm.flush('tower')
    back = C.Face((TX, y0 + TD, 0), (-1, 0, 0), (0, -1, 0), 'tower back')
    bh = [hole('tower back window', 0.0, EAVE + 1.6, 1.8, 3.6)]
    back.wall('tower back carrier', -TW / 2 + T, TW / 2 - T, EAVE - 2.0, TOWER_TOP - .20, depth=T, role='wall', holes=bh)
    mb = Merge(back); framed(mb, back, bh[0], cols=2, rows=2, occupied='tower rooms', lite=True); mb.box('stone', 0.0, -.18, TOWER_TOP - 1.3, TW - 2 * T - 2 * EPS, T + .42, .34); mb.flush('tower')
    # Crenellated parapet: one merlon per position, corners not doubled (v001 P1 14).
    zt = TOWER_TOP - .20
    sides = ((x0, y0, x1, y0), (x1, y0, x1, y0 + TD), (x1, y0 + TD, x0, y0 + TD), (x0, y0 + TD, x0, y0))
    for (ax, ay, bx, by) in sides:
        C.beam('Parapet wall', (ax, ay, zt + .30), (bx, by, zt + .30), .40, .60, 'wall', 'parapet')
        L = math.hypot(bx - ax, by - ay); n = int(L / 1.2)
        for i in range(1, n):
            if i % 2 == 0:
                px, py = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
                C.box('Merlon', (px, py, zt + .60 + .45), (.70, .70, .90), 'wall', 'parapet', 0)
    for (px, py) in ((x0, y0), (x1, y0), (x1, y0 + TD), (x0, y0 + TD)):
        C.box('Corner merlon', (px, py, zt + .60 + .50), (.80, .80, 1.0), 'wall', 'parapet', 0)
    C.box('Tower roof', (TX, y0 + TD / 2, zt - .12), (TW - .2, TD - .2, .24), 'lead', 'parapet', 0)
    C.rod('Flagpole', (TX, y0 + TD / 2, zt), (TX, y0 + TD / 2, zt + 5.0), .05, 'hardware', 'parapet', 8)
    for sgn in (-1, 1):
        cx, cy = TX + sgn * (TW / 2 - .55), y0 + .55
        tourelle(cx, cy, 1.15, 13.2, TOWER_TOP + .9, TOWER_TOP + 5.0, math.radians(-90 + sgn * 20), windows=False, label=f'tower tourelle {sgn}')
    # Passage through the south wing: floor, side walls, ceiling, court-side pointed arch between two carriers.
    y1 = -D / 2 + WING
    C.box('Passage floor', (TX, (y0 + y1) / 2, G0 / 2 + .001), (5.0, y1 - y0, G0), 'foundation', 'passage', 0)
    for sgn in (-1, 1):
        C.box('Passage wall', (TX + sgn * 2.7, (y0 + T + y1 - T) / 2, (G0 + 7.3) / 2), (.40, y1 - y0 - 2 * T, 7.3 - G0), 'wall', 'passage', 0)
    C.box('Passage ceiling', (TX, (y0 + T + y1 - T) / 2, 7.45), (5.8, y1 - y0 - 2 * T, .30), 'stone', 'passage', 0)
    court_face = C.Face((TX, y1, 0), (-1, 0, 0), (0, -1, 0), 'passage court face')
    ca = hole('Court arch', 0.0, G0, 5.0, 7.0, kind='open arch')
    pw_holes = [hole(f'passage court window {k}', 0.0, zl + .9, 1.6, 2.6) for k, zl in enumerate(LEVELS) if zl > 7.5]
    court_face.wall('Passage court carrier', -PASS_W / 2, PASS_W / 2 - EPS, G0, EAVE + .30, depth=T, role='wall', holes=[ca] + pw_holes)
    pointed_fill(court_face, 0.0, ca['z'] + ca['h'], ca['w'], 2.2, 'stone')
    mp = Merge(court_face)
    for h in pw_holes:
        framed(mp, court_face, h, cols=2, rows=2, occupied='guest room', lite=True)
        mp.box('stone', h['u'], -.05, h['z'] + h['h'] + .15, h['w'] + .50, T + .16, .22)
    for zl in LEVELS:
        mp.box('stone', 0.0, -.04, zl - .12, PASS_W - 2 * EPS, T + .14, .18)
    mp.box('stone', 0.0, -.20, EAVE - .16, PASS_W - 2 * EPS, T + .46, .32)
    mp.flush('passage')
    C.OPENINGS.append(dict(id=ca['id'], face='passage court face', u=0.0, z=ca['z'], width=ca['w'], height=ca['h'], kind='open arch', clear_wall_cut=True, carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None,
        face_origin=list(court_face.o), face_tangent=list(court_face.t), face_inward=list(court_face.n), occupied_space='open porte-cochere passage'))
    C.qa_room_light('Passage', (TX, (y0 + y1) / 2, 6.5), 90, 4.0)
    C.CONTACTS.append(dict(name='Tower on the south wing slab and carriers; tourelles on corbel cones from the tower wall; parapet on the tower walls; passage through the south wing between the two court carriers', tower_top_m=TOWER_TOP))


def roofs_and_floors():
    outer = [(-W / 2, -D / 2), (W / 2, -D / 2), (W / 2, D / 2), (-W / 2, D / 2)]
    ridge = [(-W / 2 + WING / 2, -D / 2 + WING / 2), (W / 2 - WING / 2, -D / 2 + WING / 2), (W / 2 - WING / 2, D / 2 - WING / 2), (-W / 2 + WING / 2, D / 2 - WING / 2)]
    court = [(-W / 2 + WING, -D / 2 + WING), (W / 2 - WING, -D / 2 + WING), (W / 2 - WING, D / 2 - WING), (-W / 2 + WING, D / 2 - WING)]
    C.prism('Ground slab', outer, 'z', 0.0, G0, 'foundation', 'foundation')
    C.prism('Court paving', [(x * .99, y * .99) for x, y in court], 'z', G0, G0 + .03, 'stone', 'court')
    for x, y in ((-11.0, -7.0), (11.0, -7.0), (11.0, 7.0), (-11.0, 7.0)):     # four corner trees (locked top, v001 P1 16)
        street_tree(x, y, G0 + .03, height=7.0, spread=1.8)
        C.box('Court planter', (x, y, G0 + .2), (2.4, 2.4, .34), 'stone', 'court', 0)
    wings = [((-W / 2 + T, -D / 2 + T), (W / 2 - T, -D / 2 + WING)), ((-W / 2 + T, D / 2 - WING), (W / 2 - T, D / 2 - T)),
             ((-W / 2 + T, -D / 2 + WING - EPS), (-W / 2 + WING, D / 2 - WING + EPS)), ((W / 2 - WING, -D / 2 + WING - EPS), (W / 2 - T, D / 2 - WING + EPS))]
    for zl in LEVELS + [EAVE]:
        for (x0, y0), (x1, y1) in wings:
            slab = C.prism(f'Floor {zl:.1f}', [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 'z', zl - .28, zl, 'floor', 'occupied floors')
            if y1 <= -D / 2 + WING + .01 and zl < 8.0:
                C.cut_box(slab, 'Passage cut', (TX, (y0 + y1) / 2, zl - .14), (5.6, WING + 2.0, 1.0))
    for zl in LEVELS[:3]:
        C.qa_room_light(f'South rooms {zl:.1f}', (14.0, -D / 2 + 5.0, zl + 2.6), 120, 5.0)
        C.qa_room_light(f'West rooms {zl:.1f}', (-W / 2 + 5.0, 4.0, zl + 2.6), 60, 5.0)
    C.qa_room_light('Lounge', (14.0, -D / 2 + 6.0, LEVELS[0] - .9), 120, 6.0)
    C.qa_room_light('Interior view room', (14.0, -D / 2 + 4.5, LEVELS[0] + 3.4), 220, 5.0)
    # Court faces: side walls run into the front and rear walls (closed corners, v001 P0 4); the south court face is
    # built in two runs either side of the passage carrier; one central gable per face.
    cw, cd = W - 2 * WING, D - 2 * WING
    cf = A.faces(cw, cd, 0, 0, 'court ')
    for i, f in enumerate(cf):
        f = C.Face(f.o, f.t, f.n * -1, f.label)
        span = cw if i % 2 == 0 else cd
        lo, hi = (-span / 2, span / 2 - EPS) if i % 2 == 0 else (-span / 2 - T + .02, span / 2 + T - .02)
        if i == 0:
            elevation(C.Face(f.o, f.t, f.n, 'court front west'), lo, TX - PASS_W / 2, street=False)
            elevation(C.Face(f.o, f.t, f.n, 'court front east'), TX + PASS_W / 2, hi, street=False)
            continue
        elevation(f, lo, hi, street=False, gables=(0.0,))
    strip('Outer slate slopes', outer, ridge, EAVE, RIDGE, 'roof', 'roofs')
    strip('Court slate slopes', ridge, court, RIDGE, EAVE, 'roof', 'roofs')
    for (ax, ay), (bx, by) in zip(ridge, ridge[1:] + ridge[:1]):
        C.beam('Ridge lead', (ax, ay, RIDGE + .06), (bx, by, RIDGE + .06), .36, .14, 'lead', 'roofs')
    for x, y in ((-18.0, -D / 2 + WING / 2), (18.0, -D / 2 + WING / 2), (-W / 2 + WING / 2, 0.0), (W / 2 - WING / 2, 0.0), (-12.0, D / 2 - WING / 2), (12.0, D / 2 - WING / 2)):
        C.box('Chimney stack', (x, y, RIDGE + .9), (2.2, 1.1, 3.2), 'wall', 'chimneys', 0)
        C.box('Chimney cope', (x, y, RIDGE + 2.56), (2.5, 1.4, .16), 'stone', 'chimneys', 0)
        for dx in (-.6, 0.0, .6):
            C.rod('Chimney pot', (x + dx, y, RIDGE + 2.6), (x + dx, y, RIDGE + 3.3), .16, 'rustic', 'chimneys', 8)


def site():
    x0, x1, y0, y1 = SITE
    C.box('Street south', ((x0 + x1) / 2, y0 + 3.5, .004), (x1 - x0, 7.0, .008), 'concrete', 'street', 0)
    C.box('Street west', (x0 + 3.5, (y0 + 7.0 + y1) / 2, .004), (7.0, y1 - y0 - 7.0, .008), 'concrete', 'street', 0)
    C.box('Kerb south', ((x0 + 7.0 + x1) / 2, y0 + 7.06, .06), (x1 - x0 - 7.0, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb west', (x0 + 7.06, (y0 + 7.0 + y1) / 2, .06), (.12, y1 - y0 - 7.0, .12), 'stone', 'sidewalk', 0)
    C.box('South sidewalk', ((x0 + 7.0 + x1) / 2, (y0 + 7.0 + y0 + 10.0) / 2, .0075), (x1 - x0 - 7.0, 3.0, .015), 'foundation', 'sidewalk', 0)
    C.box('West sidewalk', ((x0 + 7.0 + x0 + 10.0) / 2, (y0 + 10.0 + y1) / 2, .0075), (3.0, y1 - y0 - 10.0, .015), 'foundation', 'sidewalk', 0)
    yf = y0 + 10.0
    xf = x0 + 10.0
    C.box('South lawn', ((-W / 2 + x1) / 2, (yf + (-D / 2 - TOUT)) / 2, .02), (x1 + W / 2, -D / 2 - TOUT - yf, .04), 'planting', 'lawn', 0)
    C.box('West lawn', ((xf + (-W / 2)) / 2, (yf + y1) / 2, .02), (-W / 2 - xf, y1 - yf, .04), 'planting', 'lawn', 0)
    C.box('East pavement', ((W / 2 + x1) / 2, (-D / 2 - TOUT + D / 2) / 2, .0075), (x1 - W / 2, D + TOUT, .015), 'foundation', 'sidewalk', 0)
    C.box('North pavement', ((xf + x1) / 2, (D / 2 + y1) / 2, .0075), (x1 - xf, y1 - D / 2, .015), 'foundation', 'sidewalk', 0)
    C.box('Entrance drive', (TX, (yf + (-D / 2 - TOUT)) / 2, .05), (7.0, -D / 2 - TOUT - yf + .2, .03), 'stone', 'lawn', 0)
    iron_fence((xf, yf), (TX - 4.0, yf), height=1.4, wall=.6, spacing=.40); iron_fence((TX + 4.0, yf), (x1 - 2.0, yf), height=1.4, wall=.6, spacing=.40)
    iron_fence((xf, y1 - 2.0), (xf, yf), height=1.4, wall=.6, spacing=.40)
    for sgn in (-1, 1):
        C.box('Gate pier', (TX + sgn * 4.2, yf, 1.1), (.8, .8, 2.2), 'stone', 'fence', 0); C.box('Gate pier cap', (TX + sgn * 4.2, yf, 2.28), (1.0, 1.0, .16), 'stone', 'fence', 0)
    for x in (-24.0, -14.0, 14.0, 24.0):
        street_tree(x, yf + 3.2, .02, height=8.0, spread=2.0)
    for y in (-12.0, 2.0, 14.0):
        street_tree(xf + 2.6, y, .02, height=8.0, spread=2.0)


def build():
    site()
    roofs_and_floors()
    south = C.Face((0, -D / 2, 0), (1, 0, 0), (0, 1, 0), 'south')
    west = C.Face((-W / 2, 0, 0), (0, -1, 0), (1, 0, 0), 'west')
    north = C.Face((0, D / 2, 0), (-1, 0, 0), (0, -1, 0), 'north')
    east = C.Face((W / 2, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    # Street runs end 0.3 m inside the tower side carriers so no face is shared at the junction (v001 P0 3).
    sw = C.Face(south.o, south.t, south.n, 'south west run'); se = C.Face(south.o, south.t, south.n, 'south east run')
    gx = TW / 2 + 1.0 + BAY            # wall gable centred on the two bays beside the tower
    elevation(sw, -W / 2, TX - TW / 2 + .3, street=True, gables=(-gx,))
    elevation(se, TX + TW / 2 - .3, W / 2, street=True, gables=(gx,))
    # West and east faces (u = -y and u = y): intermediate tourelles at y = +-9 with a two-bay gable beside each; the north
    # face has two tourelles at x = +-14 and a gable between.
    elevation(west, -D / 2 + T, D / 2 - T, street=True, gables=(-16.0, 16.0))
    elevation(east, -D / 2 + T, D / 2 - T, street=True, gables=(-16.0, 16.0))
    elevation(north, -W / 2, W / 2, street=False, gables=(0.0,))
    tower()
    for cx, cy, facing in ((-W / 2 + .9, -D / 2 + .9, math.radians(225)), (W / 2 - .9, -D / 2 + .9, math.radians(-45)), (W / 2 - .9, D / 2 - .9, math.radians(45)), (-W / 2 + .9, D / 2 - .9, math.radians(135))):
        tourelle(cx, cy, 2.4, 7.0, EAVE + 4.0, EAVE + 10.5, facing, label='corner tourelle')
    for cx, cy, facing in ((-W / 2 + .2, -9.0, math.radians(180)), (-W / 2 + .2, 9.0, math.radians(180)), (W / 2 - .2, -9.0, 0.0), (W / 2 - .2, 9.0, 0.0), (-14.0, D / 2 - .2, math.radians(90)), (14.0, D / 2 - .2, math.radians(90))):
        tourelle(cx, cy, 1.6, 9.0, EAVE + 3.0, EAVE + 8.0, facing, label='side tourelle')
    k_run = (WING / 2) / (RIDGE - EAVE)
    for f, lo, hi, gables, pitch_n in ((sw, -W / 2, TX - TW / 2 + .3, (-gx,), None), (se, TX + TW / 2 - .3, W / 2, (gx,), None), (west, -D / 2 + T, D / 2 - T, (-16.0, 16.0), None),
                                       (east, -D / 2 + T, D / 2 - T, (-16.0, 16.0), None), (north, -W / 2, W / 2, (0.0,), None)):
        nb = max(1, round((hi - lo) / BAY)); pitch = (hi - lo) / nb
        for i in range(nb):
            u = lo + pitch * (i + .5)
            if any(abs(u - g) < 5.2 for g in gables) or i in (0, nb - 1):
                continue
            if any(abs(u - g) < 7.4 for g in (-16.0, 16.0)) and f.label in ('west', 'east'):
                continue
            roof_dormer(f, u, EAVE, RIDGE - EAVE, WING / 2)
    A.sofa(16.0, -D / 2 + 6.0, LEVELS[0]); A.desk(12.0, -D / 2 + 4.0, LEVELS[0] + .05)
    C.box('Lounge partition', (20.0, -D / 2 + 6.0, LEVELS[0] + 1.7), (.16, 10.0, 3.4), 'interior', 'partitions', 0)


LIGHT_RIG = dict(key=(-60, -70, 70), fill=(70, -36, 50), rear=(-26, 70, 60), target=(0, 0, 16.0), gain=11.0)
