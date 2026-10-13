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

SLUG = 'clay-baronial-railway-hotel'
W, D = 58.0, 50.0                 # quadrangle footprint
WING = 14.0                       # wing depth; court 30 x 22 m
T = .40
G0 = .15
LEVELS = [4.6, 8.4, 12.2, 16.0, 19.8]
EAVE = 23.2
RIDGE = 29.8
TX, TW, TD, TOUT = -10.0, 10.0, 11.6, 1.6     # entrance tower centre x, width, depth (with projection), projection
TOWER_TOP = 34.0
BAY = 3.6
EPS = .002
SITE = (-W / 2 - 12.0, W / 2 + 8.0, -D / 2 - 14.0, D / 2 + 8.0)
PALETTE = dict(wall=(.66, .55, .49), joint=(.50, .41, .37), trim=(.22, .20, .18),
    pale=(.76, .72, .66), stone=(.74, .68, .60), roof=(.22, .24, .28), sand=(.70, .64, .52),
    foundation=(.46, .46, .45), glass=(.44, .50, .52), hardware=(.12, .12, .12),
    interior=(.80, .76, .68), floor=(.46, .44, .42), timber=(.36, .26, .16), blue=(.14, .22, .28),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.64, .62, .58), lead=(.42, .44, .46),
    rustic=(.62, .52, .46))


def manifest(version):
    h = TOWER_TOP + 6.0
    cams = G.camera_roster(W + 16.0, D + 16.0, h, [
        ('facade_close', (-30.0, -48.0, 6.0), (-10.0, -D / 2, 10.0), 45),
        ('architecture_close', (-54.0, -52.0, 20.0), (-W / 2 + 4.0, -D / 2 + 4.0, 16.0), 50),
        ('glass_close', (2.0, -36.0, 6.5), (6.0, -D / 2, 7.5), 50),
        ('entrance_tower', (-30.0, -62.0, 26.0), (TX, -D / 2, 24.0), 45),
        ('porte_cochere', (-22.0, -42.0, 2.0), (TX, -D / 2 - TOUT, 4.5), 40),
        ('corner_tourelle', (-50.0, -50.0, 24.0), (-W / 2, -D / 2, 24.0), 45),
        ('crow_gables', (14.0, -46.0, 22.0), (12.0, -D / 2, 25.0), 45),
        ('roof_court', (-60.0, -66.0, 56.0), (0.0, 0.0, 22.0), 45),
        ('interior', (-2.0, -D / 2 + 1.2, LEVELS[0] + 1.6), (-2.0, -D / 2 + 8.0, LEVELS[0] + 1.3), 50),
        ('rear_court', (6.0, 8.0, 3.0), (-10.0, -D / 2 + WING, 8.0), 40)])
    for c in cams:
        if c['name'] == 'front':          # eye level from the south-west on the street, tower at the left (locked front)
            c['location'] = (-40.0, -70.0, 1.7); c['target'] = (-2.0, -D / 2, 13.0); c['lens'] = 30; c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='chateauesque_grand_railway_hotel/variant_0 (scottish_baronial_granite_tower)',
        measurement_contract=dict(dimensions_m=dict(width=SITE[1] - SITE[0], depth=SITE[3] - SITE[2], height=h),
            observed_storeys=6, storey_programme='ground floor of public rooms, five guest-room storeys, attic rooms in the slate roof',
            plan='58 x 50 m quadrangle (top view) of 14 m wings around a 30 x 22 m court, streets south and west; entrance tower 10 m square on the south face a quarter in from the west corner, projecting 1.6 m',
            facade='bays at 3.6 m of sash windows 1.4 x 2.2 m with stone surrounds in rusticated granite; stone string courses at each floor; crow-stepped wall gables 5 m wide rising from the eaves every third bay on the street faces; eaves at 23.2 m',
            levels_m=[G0] + LEVELS, eave_m=EAVE, ridge_m=RIDGE,
            tower='square entrance tower to 34 m with a crenellated parapet, pointed-arch porte-cochere 5 x 7 m through the south wing to the court, round tourelles 2.2 m across at the two front corners from 13 m with conical caps to 39 m, crest panel over the arch',
            tourelles='round corner tourelles 4.8 m across corbelled out at 7 m with conical slate roofs to 31.5 m at the four outer corners',
            roof='steep slate hipped ring roof 23.2 to 29.8 m with gabled dormers between the wall gables, chimney stacks on the ridge',
            inferred='north and east faces repeat the grammar without wall gables; court faces plain; interiors are teaching assumptions'),
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
    """Frustum of revolution (r1 may be 0.001 for a point)."""
    vs = [(cx + r0 * math.cos(math.tau * i / segs), cy + r0 * math.sin(math.tau * i / segs), z0) for i in range(segs)]
    vs += [(cx + max(r1, .001) * math.cos(math.tau * i / segs), cy + max(r1, .001) * math.sin(math.tau * i / segs), z1) for i in range(segs)]
    fs = [tuple(range(segs - 1, -1, -1)), tuple(range(segs, 2 * segs))] + [(i, (i + 1) % segs, (i + 1) % segs + segs, i + segs) for i in range(segs)]
    return C.mesh(name, vs, fs, role, module)


def pointed_fill(f, u, z_top, w, rise, role='stone', d0=-.03, d1=None):
    """Spandrel above a pointed (two-centre) arch inside a rectangular cut."""
    d1 = T + .02 if d1 is None else d1
    pts = [(-w / 2, z_top), (w / 2, z_top), (w / 2, z_top - rise)]
    for k in range(1, 8):
        x = w / 2 - w * k / 8
        xx = abs(x)
        pts.append((x, z_top - rise + ((w ** 2 - (xx + w / 2) ** 2) ** .5) * rise / (w * .866)))   # arc centred on the opposite springing
    pts.append((-w / 2, z_top - rise))
    f.panel('Pointed arch spandrel', [(u + a, b) for a, b in pts], d0, d1, role, 'arches')


def roof_dormer(f, u, z_e, rise, run, w=1.7):
    """Small gabled dormer standing on a slope of rise/run: stone front with a sash window, cheeks, slate gable."""
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
    # cheeks back to the slope under the gable plates
    d_back = d0 + 2.4
    for sgn in (-1, 1):
        uu = u + sgn * (w / 2 - .06)
        pts = [(d0 - .16, z_em - .5), (d0 - .16, z_top), (d_back, z_top), (d_back, z_e + d_back / k - .9)]
        vs = [f.p(uu - .06, d, z) for d, z in pts] + [f.p(uu + .06, d, z) for d, z in pts]
        fs = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        C.mesh('Dormer cheek', vs, fs, 'stone', 'dormers')
    # two slate plates from the ridge (front apex back to where the ridge meets the slope) to the eaves
    z_apex = z_top + .80
    d_ridge = (z_apex - z_e) * k - .1
    for sgn in (-1, 1):
        a = f.p(u, d0 - .32, z_apex); b = f.p(u, d_ridge, z_e + d_ridge / k + .02)
        c_ = f.p(u + sgn * (w / 2 + .22), d0 - .32, z_top - .10); d_ = f.p(u + sgn * (w / 2 + .22), d_ridge, z_e + d_ridge / k - .8)
        vs = [a, b, d_, c_]
        t_ = .16
        vs += [(x, y, z - t_) for x, y, z in vs]
        C.mesh('Dormer slate', vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 'roof', 'dormers')


def crow_gable(f, u, z_e, w=5.2, apex=28.6, run_per_rise=14.0 / (29.8 - 23.2) / 2):
    """Crow-stepped wall gable: the carrier continued through the eaves as a stepped stone-coped gable with a window,
    and a slate gable roof running back into the main slope."""
    pts = [(-w / 2, z_e - .5), (w / 2, z_e - .5), (w / 2, z_e + .3)]
    rise, run = .60, .42
    x, z = w / 2, z_e + .3
    right = []
    while x - run > .30:
        x -= run; right.append((x, z)); z += rise; right.append((x, z))
    top = z
    pts += right + [(.30, top), (-.30, top)] + [(-a, b) for a, b in reversed(right)] + [(-w / 2, z_e + .3)]
    panel = f.panel(f'{f.label} crow gable', [(u + a, b) for a, b in pts], -.06, T, 'wall', 'gables')
    zw, hw, ww = z_e + .9, 2.0, 1.3
    f.cut(panel, f'{f.label} gable window cut', u, zw, ww, hw, depth=T + .1)
    m = Merge(f)
    h = hole(f'{f.label} gable window {u:.1f}', u, zw, ww, hw)
    reveal(m, f, h, .16, 'stone'); framed(m, f, h, cols=2, rows=2, occupied='attic room')
    for sgn in (-1, 1):
        m.box('stone', u + sgn * (ww / 2 + .11), -.03, zw + hw / 2, .22, T + .12, hw + .22)
    m.box('stone', u, -.05, zw + hw + .17, ww + .56, T + .16, .24)
    # stone copes on every step
    for (a, b) in right:
        pass
    steps = right[1::2]
    for sgn in (-1, 1):
        prev_x = w / 2
        for (x, z) in steps:
            m.box('stone', u + sgn * (x + (prev_x - x) / 2 - .02), -.09, z + .06, prev_x - x + .06, T + .24, .14)
            prev_x = x
    m.box('stone', u, -.09, top + .06, .70, T + .24, .14)
    m.flush('gables')
    C.rod('Gable finial', f.p(u, -.02, top + .1), f.p(u, -.02, top + .9), .05, 'stone', 'gables', 6)
    # slate gable roof behind the panel, ridge descending into the main slope
    k = run_per_rise
    z_apex = top - .25
    d_ridge = (z_apex - z_e) * k - .05
    for sgn in (-1, 1):
        a = f.p(u, T - .02, z_apex); b = f.p(u, d_ridge, z_e + d_ridge / k + .02)
        c_ = f.p(u + sgn * (w / 2 - .30), T - .02, z_e + .35); d_ = f.p(u + sgn * (w / 2 - .30), d_ridge, z_e + d_ridge / k - 1.4)
        vs = [a, b, d_, c_]
        vs += [(x, y, z - .18) for x, y, z in vs]
        C.mesh('Gable slate', vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 'roof', 'gables')


def elevation(f, lo, hi, street=True, gables=(), skip=()):
    """One face: rusticated granite carrier with sash windows and stone dressings; optional wall gables at bay indices."""
    span = hi - lo
    nb = max(1, round(span / BAY))
    pitch = span / nb
    holes = []
    for i in range(nb):
        if i in skip:
            continue
        c = lo + pitch * (i + .5)
        holes.append(hole(f'{f.label} ground window {i}', c, 1.0, 1.5, 2.6, kind='window', level=-1))
        for k, zl in enumerate(LEVELS):
            holes.append(hole(f'{f.label} window {i}-{k}', c, zl + .9, 1.4, 2.2, level=k))
    f.wall(f'{f.label} carrier', lo, hi - EPS, G0, EAVE + .30, depth=T, role='wall', holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, G0 + .3, EAVE - .4, holes, spacing=.58 if street else .95)
    m = Merge(f)
    for h in holes:
        if street:
            reveal(m, f, h, .16, 'stone')
        framed(m, f, h, cols=2, rows=2, occupied='guest room' if h['level'] >= 0 else 'lounge', lite=not street)
        if street:
            for sgn in (-1, 1):
                m.box('stone', h['u'] + sgn * (h['w'] / 2 + .10), -.03, h['z'] + h['h'] / 2, .20, T + .12, h['h'] + .20)
            m.box('stone', h['u'], -.07, h['z'] - .08, h['w'] + .36, T + .20, .12)
        m.box('stone', h['u'], -.05, h['z'] + h['h'] + .15, h['w'] + .50, T + .16, .22)
    for zl in LEVELS:
        m.box('stone', (lo + hi) / 2, -.04, zl - .12, span - 2 * EPS, T + .14, .18)
    m.box('stone', (lo + hi) / 2, -.07, G0 + .55, span - 2 * EPS, T + .20, .40)          # plinth course
    m.box('stone', (lo + hi) / 2, -.16, EAVE - .20, span - 2 * EPS, T + .38, .34)        # eaves course
    m.flush('facade')
    for i in gables:
        crow_gable(f, lo + pitch * (i + .5), EAVE)
    return pitch


def tower():
    y0 = -D / 2 - TOUT
    x0, x1 = TX - TW / 2, TX + TW / 2
    front = C.Face((TX, y0, 0), (1, 0, 0), (0, 1, 0), 'tower front')
    arch = hole('Porte-cochere', 0.0, G0, 5.0, 7.0, kind='open arch')
    holes = [arch]
    for k, zl in enumerate(LEVELS):
        if zl < 7.5:
            continue
        for du in (-1.6, 1.6):
            holes.append(hole(f'tower window {k}{du:+.0f}', du, zl + .9, 1.3, 2.2, level=k))
    holes.append(hole('tower upper window', 0.0, EAVE + 1.2, 2.0, 3.0, level=9))
    front.wall('tower front carrier', -TW / 2, TW / 2, G0, TOWER_TOP - .20, depth=T, role='wall', holes=holes)
    G.brick_courses(front, -TW / 2 + .02, TW / 2 - .02, G0 + .3, TOWER_TOP - 1.4, holes, spacing=.58)
    m = Merge(front)
    for h in holes[1:]:
        reveal(m, front, h, .16, 'stone'); framed(m, front, h, cols=2, rows=2, occupied='tower rooms')
        for sgn in (-1, 1):
            m.box('stone', h['u'] + sgn * (h['w'] / 2 + .10), -.03, h['z'] + h['h'] / 2, .20, T + .12, h['h'] + .20)
        m.box('stone', h['u'], -.05, h['z'] + h['h'] + .15, h['w'] + .50, T + .16, .22)
    pointed_fill(front, 0.0, arch['z'] + arch['h'], arch['w'], 2.2, 'stone')
    m.box('stone', 0.0, -.10, arch['z'] + arch['h'] + .30, arch['w'] + 1.6, T + .26, .36)   # hood course over the arch
    for sgn in (-1, 1):
        m.box('stone', sgn * (arch['w'] / 2 + .45), -.14, (G0 + arch['z'] + arch['h'] - 2.2) / 2, .70, T + .34, arch['z'] + arch['h'] - 2.2 - G0)
    m.box('stone', 0.0, -.12, arch['z'] + arch['h'] + 1.5, 2.4, T + .30, 1.6)                 # crest panel
    m.box('wall', 0.0, -.20, arch['z'] + arch['h'] + 1.5, 1.6, T + .34, 1.1)
    for zl in LEVELS:
        if zl > 7.5:
            m.box('stone', 0.0, -.04, zl - .12, TW - 2 * EPS, T + .14, .18)
    m.box('stone', 0.0, -.18, TOWER_TOP - 1.3, TW - 2 * EPS, T + .42, .34)                   # corbel course under the parapet
    m.flush('tower')
    C.OPENINGS.append(dict(id=arch['id'], face='tower front', u=0.0, z=arch['z'], width=arch['w'], height=arch['h'], kind='open arch', clear_wall_cut=True, carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None,
        face_origin=list(front.o), face_tangent=list(front.t), face_inward=list(front.n), occupied_space='open porte-cochere passage to the court'))
    # Side and back carriers of the tower (plain above the roof), passage walls and ceiling, court-side arch.
    for sgn, label in ((-1, 'tower west'), (1, 'tower east')):
        x = TX + sgn * TW / 2
        f = C.Face((x, y0 + TD / 2, 0), (0, sgn, 0), (-sgn, 0, 0), label)
        hs = [hole(f'{label} window {k}', 0.0, zl + .9, 1.3, 2.2) for k, zl in enumerate(LEVELS) if zl > 7.5] + [hole(f'{label} upper window', 0.0, EAVE + 1.2, 1.6, 3.0)]
        f.wall(f'{label} carrier', -TD / 2 + T, TD / 2, G0, TOWER_TOP - .20, depth=T, role='wall', holes=hs)
        mm = Merge(f)
        for h in hs:
            framed(mm, f, h, cols=2, rows=2, occupied='tower rooms')
            m2 = mm
            m2.box('stone', h['u'], -.05, h['z'] + h['h'] + .15, h['w'] + .50, T + .16, .22)
        mm.box('stone', 0.0, -.18, TOWER_TOP - 1.3, TD - T - 2 * EPS, T + .42, .34)
        mm.flush('tower')
    back = C.Face((TX, y0 + TD, 0), (-1, 0, 0), (0, -1, 0), 'tower back')
    back.wall('tower back carrier', -TW / 2 + T, TW / 2 - T, EAVE - 2.0, TOWER_TOP - .20, depth=T, role='wall', holes=[hole('tower back window', 0.0, EAVE + 1.2, 1.6, 3.0)])
    mb = Merge(back); framed(mb, back, hole('tower back window', 0.0, EAVE + 1.2, 1.6, 3.0), cols=2, rows=2, occupied='tower rooms'); mb.box('stone', 0.0, -.18, TOWER_TOP - 1.3, TW - 2 * T - 2 * EPS, T + .42, .34); mb.flush('tower')
    # Crenellated parapet: ring wall with merlons.
    zt = TOWER_TOP - .20
    for (ax, ay, bx, by) in ((x0, y0, x1, y0), (x1, y0, x1, y0 + TD), (x1, y0 + TD, x0, y0 + TD), (x0, y0 + TD, x0, y0)):
        L = math.hypot(bx - ax, by - ay); n = int(L / 1.2)
        C.beam('Parapet wall', (ax, ay, zt + .30), (bx, by, zt + .30), .40, .60, 'wall', 'parapet')
        for i in range(n + 1):
            if i % 2 == 0:
                px, py = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
                C.box('Merlon', (px, py, zt + .60 + .45), (.70, .70, .90), 'wall', 'parapet', 0)
    C.box('Tower roof', (TX, y0 + TD / 2, zt - .12), (TW - .2, TD - .2, .24), 'lead', 'parapet', 0)
    C.rod('Flagpole', (TX, y0 + TD / 2, zt), (TX, y0 + TD / 2, zt + 5.0), .05, 'hardware', 'parapet', 8)
    # Front-corner tourelles: corbel cone, round shaft, conical cap, finial.
    for sgn in (-1, 1):
        cx, cy = TX + sgn * (TW / 2 - .55), y0 + .55
        cone('Tourelle corbel', cx, cy, 11.2, .25, 13.2, 1.15, 'stone', 'tourelles', 20)
        C.rod('Tourelle shaft', (cx, cy, 13.2), (cx, cy, TOWER_TOP + .9), 1.15, 'wall', 'tourelles', 20)
        C.rod('Tourelle string', (cx, cy, TOWER_TOP + .9), (cx, cy, TOWER_TOP + 1.2), 1.30, 'stone', 'tourelles', 20)
        cone('Tourelle cap', cx, cy, TOWER_TOP + 1.2, 1.32, TOWER_TOP + 5.0, 0.0, 'roof', 'tourelles', 20)
        C.rod('Tourelle finial', (cx, cy, TOWER_TOP + 4.9), (cx, cy, TOWER_TOP + 5.8), .05, 'hardware', 'tourelles', 6)
        for zl in (16.0, 19.8, 23.6, 27.4):
            px, py = cx + sgn * .0 - 0.0, cy - 1.15
            C.box('Tourelle slit', (cx, cy - 1.12, zl + 1.0), (.40, .12, 1.4), 'hardware', 'tourelles', 0)
    # Passage through the south wing: floor, side walls, ceiling, court-side pointed arch.
    y1 = -D / 2 + WING
    C.box('Passage floor', (TX, (y0 + y1) / 2, G0 / 2 + .001), (5.0, y1 - y0, G0), 'foundation', 'passage', 0)
    for sgn in (-1, 1):
        C.box('Passage wall', (TX + sgn * 2.7, (y0 + T + y1 - T) / 2, (G0 + 7.3) / 2), (.40, y1 - y0 - 2 * T, 7.3 - G0), 'wall', 'passage', 0)
    C.box('Passage ceiling', (TX, (y0 + T + y1 - T) / 2, 7.45), (5.8, y1 - y0 - 2 * T, .30), 'stone', 'passage', 0)
    court_face = C.Face((TX, y1, 0), (-1, 0, 0), (0, -1, 0), 'passage court face')
    ca = hole('Court arch', 0.0, G0, 5.0, 7.0, kind='open arch')
    court_face.wall('Passage court carrier', -4.5, 4.5, G0, LEVELS[0] - .30, depth=T, role='wall', holes=[ca])
    pointed_fill(court_face, 0.0, ca['z'] + ca['h'], ca['w'], 2.2, 'stone')
    C.OPENINGS.append(dict(id=ca['id'], face='passage court face', u=0.0, z=ca['z'], width=ca['w'], height=ca['h'], kind='open arch', clear_wall_cut=True, carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None,
        face_origin=list(court_face.o), face_tangent=list(court_face.t), face_inward=list(court_face.n), occupied_space='open porte-cochere passage'))
    C.qa_room_light('Passage', (TX, (y0 + y1) / 2, 6.5), 70, 4.0)
    C.CONTACTS.append(dict(name='Tower on the south wing slab and carriers; tourelles on corbel cones from the tower wall; parapet on the tower walls; passage through the south wing', tower_top_m=TOWER_TOP))


def corner_tourelle(cx, cy, base=7.0, top=25.6, r=2.4):
    cone('Corner tourelle corbel', cx, cy, base - 2.2, .4, base, r, 'stone', 'tourelles', 28)
    C.rod('Corner tourelle shaft', (cx, cy, base), (cx, cy, top), r, 'wall', 'tourelles', 28)
    for zl in LEVELS:
        if zl > base:
            C.rod('Corner tourelle string', (cx, cy, zl - .12), (cx, cy, zl + .06), r + .10, 'stone', 'tourelles', 28)
            for a in (math.radians(200), math.radians(245), math.radians(290)):
                ax, ay = cx + math.cos(a) * (r - .02), cy + math.sin(a) * (r - .02)
                C.beam('Corner tourelle window', (ax + math.cos(a) * -.30, ay + math.sin(a) * -.30, zl + .9), (ax + math.cos(a) * .015, ay + math.sin(a) * .015, zl + 2.9), .9, .9, 'hardware', 'tourelles')
    C.rod('Corner tourelle eaves', (cx, cy, top), (cx, cy, top + .35), r + .25, 'stone', 'tourelles', 28)
    cone('Corner tourelle roof', cx, cy, top + .35, r + .30, top + 6.3, 0.0, 'roof', 'tourelles', 28)
    C.rod('Corner tourelle finial', (cx, cy, top + 6.2), (cx, cy, top + 7.2), .06, 'hardware', 'tourelles', 6)


def roofs_and_floors():
    outer = [(-W / 2, -D / 2), (W / 2, -D / 2), (W / 2, D / 2), (-W / 2, D / 2)]
    ridge = [(-W / 2 + WING / 2, -D / 2 + WING / 2), (W / 2 - WING / 2, -D / 2 + WING / 2), (W / 2 - WING / 2, D / 2 - WING / 2), (-W / 2 + WING / 2, D / 2 - WING / 2)]
    court = [(-W / 2 + WING, -D / 2 + WING), (W / 2 - WING, -D / 2 + WING), (W / 2 - WING, D / 2 - WING), (-W / 2 + WING, D / 2 - WING)]
    C.prism('Ground slab', outer, 'z', 0.0, G0, 'foundation', 'foundation')
    C.prism('Court lawn', [(x * .99, y * .99) for x, y in court], 'z', G0, G0 + .03, 'planting', 'court')
    C.prism('Court drive', [(-W / 2 + WING + .3, -D / 2 + WING - .01), (W / 2 - WING - .3, -D / 2 + WING - .01), (W / 2 - WING - .3, -D / 2 + WING + 6.0), (-W / 2 + WING + .3, -D / 2 + WING + 6.0)], 'z', G0 + .03, G0 + .05, 'stone', 'court')
    for x, y in ((-8.0, 6.0), (8.0, 6.0), (0.0, 1.0)):
        street_tree(x, y, G0 + .03, height=7.0, spread=1.8)
    wings = [((-W / 2 + T, -D / 2 + T), (W / 2 - T, -D / 2 + WING)), ((-W / 2 + T, D / 2 - WING), (W / 2 - T, D / 2 - T)),
             ((-W / 2 + T, -D / 2 + WING - EPS), (-W / 2 + WING, D / 2 - WING + EPS)), ((W / 2 - WING, -D / 2 + WING - EPS), (W / 2 - T, D / 2 - WING + EPS))]
    for zl in LEVELS + [EAVE]:
        for (x0, y0), (x1, y1) in wings:
            slab = C.prism(f'Floor {zl:.1f}', [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 'z', zl - .28, zl, 'floor', 'occupied floors')
            if y1 <= -D / 2 + WING + .01 and zl < 8.0:
                C.cut_box(slab, 'Passage cut', (TX, (y0 + y1) / 2, zl - .14), (5.6, WING + 2.0, 1.0))
    for zl in LEVELS[:3]:
        C.qa_room_light(f'South rooms {zl:.1f}', (6.0, -D / 2 + 5.0, zl + 2.6), 70, 5.0)
        C.qa_room_light(f'West rooms {zl:.1f}', (-W / 2 + 5.0, 4.0, zl + 2.6), 60, 5.0)
    C.qa_room_light('Lounge', (4.0, -D / 2 + 6.0, LEVELS[0] - .9), 90, 6.0)
    # Court faces.
    cw, cd = W - 2 * WING, D - 2 * WING
    cf = A.faces(cw, cd, 0, 0, 'court ')
    for i, f in enumerate(cf):
        f = C.Face(f.o, f.t, f.n * -1, f.label)
        span = cw if i % 2 == 0 else cd
        lo, hi = (-span / 2, span / 2 - EPS) if i % 2 == 0 else (-span / 2 + T, span / 2 - T)
        skip = ()
        if i == 0:     # the south wing court face carries the passage arch at TX (u = x)
            nb = max(1, round(span / BAY)); pitch = span / nb
            skip = tuple(j for j in range(nb) if abs(lo + pitch * (j + .5) - TX) < 3.0)
        elevation(f, lo, hi, street=False, skip=skip)
    # Hipped ring roof: outer slopes to the ridge ring, inner slopes down to the court eaves.
    strip('Outer slate slopes', outer, ridge, EAVE, RIDGE, 'roof', 'roofs')
    strip('Court slate slopes', ridge, court, RIDGE, EAVE, 'roof', 'roofs')
    for (ax, ay), (bx, by) in zip(ridge, ridge[1:] + ridge[:1]):
        C.beam('Ridge lead', (ax, ay, RIDGE + .06), (bx, by, RIDGE + .06), .36, .14, 'lead', 'roofs')
    for x, y in ((-20.0, -D / 2 + WING / 2), (6.0, -D / 2 + WING / 2), (20.0, -D / 2 + WING / 2), (-W / 2 + WING / 2, 6.0), (-W / 2 + WING / 2, -6.0), (W / 2 - WING / 2, 0.0), (-12.0, D / 2 - WING / 2), (12.0, D / 2 - WING / 2)):
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
    yf = y0 + 10.0     # fence line
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
    for x in (-22.0, 2.0, 14.0, 24.0):
        street_tree(x, yf + 2.6, .02, height=9.0, spread=2.2)
    for y in (-12.0, 2.0, 14.0):
        street_tree(xf + 2.6, y, .02, height=9.0, spread=2.2)


def build():
    site()
    roofs_and_floors()
    south = C.Face((0, -D / 2, 0), (1, 0, 0), (0, 1, 0), 'south')
    west = C.Face((-W / 2, 0, 0), (0, -1, 0), (1, 0, 0), 'west')
    north = C.Face((0, D / 2, 0), (-1, 0, 0), (0, -1, 0), 'north')
    east = C.Face((W / 2, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    # South face in two runs either side of the tower; wall gables every third bay on the street faces.
    sw = C.Face(south.o, south.t, south.n, 'south west run'); se = C.Face(south.o, south.t, south.n, 'south east run')
    elevation(sw, -W / 2, TX - TW / 2, street=True, gables=(1,))
    elevation(se, TX + TW / 2, W / 2, street=True, gables=(1, 4, 7))
    elevation(west, -D / 2 + T, D / 2 - T, street=True, gables=(2, 5, 8, 11))
    elevation(north, -W / 2, W / 2, street=False)
    elevation(east, -D / 2 + T, D / 2 - T, street=False)
    tower()
    for cx, cy in ((-W / 2 + .9, -D / 2 + .9), (W / 2 - .9, -D / 2 + .9), (W / 2 - .9, D / 2 - .9), (-W / 2 + .9, D / 2 - .9)):
        corner_tourelle(cx, cy)
    # Dormers between the wall gables on the outer slopes.
    k_run = (WING / 2) / (RIDGE - EAVE)
    for f, lo, hi, gables in ((sw, -W / 2, TX - TW / 2, (1,)), (se, TX + TW / 2, W / 2, (1, 4, 7)), (west, -D / 2 + T, D / 2 - T, (2, 5, 8, 11)),
                              (north, -W / 2, W / 2, ()), (east, -D / 2 + T, D / 2 - T, ())):
        nb = max(1, round((hi - lo) / BAY)); pitch = (hi - lo) / nb
        for i in range(nb):
            if i in gables or i in (0, nb - 1):
                continue
            if i % 2 == (0 if f.label in ('north', 'east') else 1):
                continue
            roof_dormer(f, lo + pitch * (i + .5), EAVE, RIDGE - EAVE, WING / 2)
    A.sofa(2.0, -D / 2 + 6.0, LEVELS[0]); A.desk(-3.0, -D / 2 + 4.0, LEVELS[0] + .05)
    C.box('Lounge partition', (8.0, -D / 2 + 6.0, LEVELS[0] + 1.7), (.16, 10.0, 3.4), 'interior', 'partitions', 0)


LIGHT_RIG = dict(key=(-60, -70, 70), fill=(70, -36, 50), rear=(-26, 70, 60), target=(0, 0, 16.0), gain=11.0)
