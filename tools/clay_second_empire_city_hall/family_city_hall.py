"""Second Empire civic hall with a central clock tower, authored from the locked catalogue views of
montreal_second_empire_civic / variant_0 (montreal_civic_city_hall).

Read from the pixels: a grey limestone block around an inner court with streets south and west. A
rusticated ground floor of round-arched windows, a piano nobile of tall pedimented windows with stone
balconies and iron rails, a second storey of hooded windows under a bracketed cornice, a steep slate
mansard with arched dormers and a flat zinc top with cresting; projecting corner pavilions with taller
square mansards; a projecting central pavilion with a columned porch reached by a broad stone stair,
carrying the square clock tower: stone shaft with tall arched openings, clock stage with four faces,
convex-concave cap and lantern. Iron fence on a low wall around a lawn forecourt.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-second-empire-city-hall'
W, D = 43.0, 36.0                 # block footprint; court 14 x 10 m inside
CW, CD = 14.0, 10.0               # inner court
T = .36
G0 = .15
L1, L2 = 5.2, 10.2                 # piano nobile and second storey floor levels
CORNICE = 14.4                    # top of the main cornice corona
MANS_H, MANS_IN = 3.8, 1.3        # mansard rise and horizontal set-in
UPPER_RISE = 2.2                  # hipped upper roof rise from the mansard top to the wing ridges (v001 P1 9)
PAV = 6.6                         # corner pavilion width along each face: two bays (v001 P1 10)
PAV_OUT = .6                      # pavilion projection
PAV_H = 7.6                       # pavilion mansard rise, about twice the wings (v001 P1 8)
CEN_W = 9.9                       # central pavilion width: three bays
TOWER = 7.6                       # tower side
T_SHAFT, T_CLOCK, T_CAP, T_LAN = 25.2, 29.6, 36.4, 39.6
PORCH_D = 3.6                     # porch depth from the central pavilion face
BAY = 3.3
EPS = .002
SITE = (-W / 2 - 9.0, W / 2 + 7.0, -D / 2 - 22.0, D / 2 + 7.0)
PALETTE = dict(wall=(.64, .57, .46), joint=(.48, .42, .34), trim=(.20, .18, .16),
    pale=(.74, .71, .64), stone=(.66, .64, .58), roof=(.24, .26, .30), sand=(.62, .58, .50),
    foundation=(.46, .46, .45), glass=(.44, .50, .52), hardware=(.12, .12, .12),
    interior=(.80, .76, .68), floor=(.46, .44, .42), timber=(.36, .26, .16), zinc=(.40, .44, .46),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.64, .62, .58), copper=(.36, .50, .44),
    rustic=(.58, .54, .47), clock=(.92, .90, .84), blue=(.14, .22, .28))


def manifest(version):
    h = T_LAN + 1.2
    cams = G.camera_roster(W + 12.0, D + 14.0, h, [
        ('facade_close', (-10.0, -40.0, 6.0), (-6.0, -D / 2, 8.0), 45),
        ('architecture_close', (-40.0, -44.0, 16.0), (-W / 2 + 6.0, -D / 2 + 4.0, 12.0), 50),
        ('glass_close', (-3.0, -31.0, 6.2), (-6.0, -D / 2, 7.2), 50),
        ('clock_tower', (-26.0, -52.0, 26.0), (0.0, -D / 2, 29.0), 45),
        ('porch_stair', (-14.0, -44.0, 3.0), (0.0, -D / 2 - 5.0, 5.0), 40),
        ('pavilion_mansard', (-40.0, -40.0, 22.0), (-W / 2 + 4.5, -D / 2 + 4.5, 17.5), 45),
        ('cornice_contact', (12.0, -32.0, 10.5), (12.0, -D / 2, 13.6), 45),
        ('roof_court', (-44.0, -50.0, 44.0), (0.0, 2.0, 16.0), 45),
        ('interior', (10.0, -D / 2 + 8.0, L1 + 1.6), (10.0, -D / 2 + .5, L1 + 1.5), 50),
        ('rear_court', (6.0, 4.0, 24.0), (-5.0, -3.5, 5.0), 40)])
    for c in cams:
        if c['name'] == 'front':          # eye level on the forecourt axis, the tower centred (locked front)
            c['location'] = (-6.0, -96.0, 1.7); c['target'] = (-1.0, -D / 2, 13.0); c['lens'] = 30; c['whole'] = False
        if c['name'] == 'top':
            c['location'] = (0, 0, 110.0); c['target'] = (0, .001, 0); c['ortho_scale'] = 78.0
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='montreal_second_empire_civic/variant_0 (montreal_civic_city_hall)',
        measurement_contract=dict(dimensions_m=dict(width=SITE[1] - SITE[0], depth=SITE[3] - SITE[2], height=h),
            observed_storeys=3, storey_programme='rusticated ground floor, piano nobile with balconies, second storey, slate mansard attic',
            plan='43 x 36 m limestone block around a 14 x 10 m inner court (top view), streets south and west; two-bay corner pavilions and a three-bay central pavilion project 0.6 m (bay rhythm 2/3/3/3/2, v001 P1 10)',
            facade='bays at 3.3 m: round-arched ground-floor windows 1.5 x 3.2 m in rustication; piano-nobile windows 1.5 x 3.0 m with pediment hoods, one continuous stone balcony with an iron rail across each pavilion; second-storey windows 1.4 x 2.4 m with cornice hoods; pilasters on the pavilions; bracketed cornice at 14.4 m',
            levels_m=[G0, L1, L2], cornice_m=CORNICE, mansard='3.8 m slate mansard set in 1.3 m with arched dormers at every bay, hipped zinc upper roofs rising 2.2 m to ridges along each wing; corner pavilions carry 7.6 m square mansards with one large raised dormer per outer face and a crested cap',
            tower='7.6 m square tower rising in the central pavilion face plane above the porch: stone shaft to 25.2 m with a pedimented arched aedicule per face and corner finials, clock stage to 29.6 m with four round faces under gablets, tall convex-concave zinc bell to 36.4 m, open lantern and finial to 39.6 m',
            porch='four-column stone porch 9.4 m wide and 3.6 m deep at the piano nobile over a rusticated arcade, crowned by a pediment at second-storey height; broad stone stair between balustraded cheeks to the forecourt',
            inferred='north and east faces repeat the grammar; court faces plain; interiors are teaching assumptions'),
        roof_contract=dict(type='slate mansard with zinc flat top and cresting; taller pavilion mansards; clock tower cap', datum_m=CORNICE, crowns_m=[CORNICE + MANS_H, CORNICE + PAV_H, T_LAN]),
        identity_contract=dict(owner='central clock tower over the columned porch and grand stair, corner pavilions with tall mansards, slate mansard with dormers, rusticated base, piano-nobile balconies, iron fence and lawn forecourt'),
        material_contract=dict(profile='source-palette clay: grey limestone with recessed rustication, dark slate mansards, zinc flats and cap, verdigris clock-stage trim, black iron, pale clock faces', textured_keeper=False),
        programme_contract=dict(storeys=4, ground='civic offices and records', upper='council chamber over the porch, offices', roof='attic offices in the mansard'),
        contact_contract=['Grade-zero slab and sidewalks', 'Porch columns bearing on the arcade piers', 'Stair bearing on the forecourt', 'Mansards seated on the cornice', 'Tower on the central pavilion walls', 'Dormers seated on the mansard slope'],
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

def arch_fill(f, u, z_top, w, rise, role='stone', d0=-.03, d1=None):
    """Spandrel panel filling the corners above a semicircular or segmental head inside a rectangular cut."""
    d1 = T + .02 if d1 is None else d1
    pts = [(-w / 2, z_top), (w / 2, z_top), (w / 2, z_top - rise)]
    for k in range(1, 8):
        x = w / 2 - w * k / 8
        pts.append((x, z_top - rise + rise * (1 - (2 * x / w) ** 2) ** .5))
    pts.append((-w / 2, z_top - rise))
    f.panel('Arch spandrel', [(u + a, b) for a, b in pts], d0, d1, role, 'arches')


def pediment(f, u, z, w, role='stone'):
    """Triangular pediment hood over a window: tympanum panel with a raking cornice."""
    f.panel('Pediment', [(u - w / 2, z - .04), (u + w / 2, z - .04), (u, z + w * .26)], -.18, .04, role, 'hoods')
    f.part('Pediment bed', u, -.14, z - .02, w + .16, .30, .12, role, 'hoods', 0)
    apex = z + w * .26
    for sgn in (-1, 1):
        C.beam('Pediment rake', f.p(u + sgn * (w / 2 + .10), -.19, z + .02), f.p(u, -.19, apex + .10), .12, .16, role, 'hoods')


def bay_openings(lo, hi, label):
    nb = max(1, round((hi - lo) / BAY))
    pitch = (hi - lo) / nb
    g, p, s = [], [], []
    for i in range(nb):
        c = lo + pitch * (i + .5)
        g.append(hole(f'{label} ground window {i}', c, 1.0, 1.5, 3.2, kind='arched window'))
        p.append(hole(f'{label} piano nobile window {i}', c, L1 + .8, 1.5, 2.9, kind='french window'))
        s.append(hole(f'{label} upper window {i}', c, L2 + .8, 1.4, 2.3))
    return pitch, g, p, s


def elevation(f, lo, hi, kind='wing', plain=False, returns=()):
    """One run of bays on a face: rusticated ground floor, piano nobile, second storey, cornice. kind: wing | pavilion | central."""
    span = hi - lo
    pitch, g, p, s = bay_openings(lo, hi, f.label)
    if kind == 'central':
        g = [hole('Entrance doors', 0.0, G0, 2.6, 3.6, kind='door')]        # the porch undercroft covers the centre; doors inside it
    holes = g + p + s
    f.wall(f'{f.label} carrier', lo, hi - EPS, G0, CORNICE + .45, depth=T, role='wall', holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, G0 + .25, L1 - .55, g, spacing=.52)
    m = Merge(f)
    for h in g:
        reveal(m, f, h, .16, 'rustic')
        if h.get('kind') == 'door':
            framed(m, f, h, cols=2, rows=2, inset=.20, occupied='entrance hall', kind='glazed door', frame='timber')
            m.box('rustic', h['u'], -.05, h['z'] + h['h'] + .16, h['w'] + .60, T + .16, .28)
            continue
        framed(m, f, h, cols=2, rows=2, occupied='ground-floor office', kind='arched window')
        arch_fill(f, h['u'], h['z'] + h['h'], h['w'], h['w'] / 2, 'rustic')
        m.box('rustic', h['u'], -.05, h['z'] - .10, h['w'] + .30, T + .16, .16)
    for h in p:
        reveal(m, f, h, .16, 'stone')
        framed(m, f, h, cols=2, rows=2, occupied='council offices', kind='french window')
        for sgn in (-1, 1):
            m.box('stone', h['u'] + sgn * (h['w'] / 2 + .13), -.05, h['z'] + h['h'] / 2, .26, T + .16, h['h'] + .26)
        m.box('stone', h['u'], -.06, h['z'] + h['h'] + .18, h['w'] + .62, T + .18, .24)
        if kind in ('pavilion', 'central'):
            pediment(f, h['u'], h['z'] + h['h'] + .30, h['w'] + .70)
            m.box('stone', h['u'], -.14, h['z'] - .10, h['w'] + .50, T + .34, .14)
        else:
            m.box('stone', h['u'], -.14, h['z'] - .10, h['w'] + .50, T + .34, .14)   # sill course
    for h in s:
        reveal(m, f, h, .16, 'stone')
        framed(m, f, h, cols=2, rows=2, occupied='offices', kind='window')
        for sgn in (-1, 1):
            m.box('stone', h['u'] + sgn * (h['w'] / 2 + .11), -.04, h['z'] + h['h'] / 2, .22, T + .14, h['h'] + .22)
        m.box('stone', h['u'], -.14, h['z'] + h['h'] + .22, h['w'] + .70, T + .34, .20)    # cornice hood
        m.box('stone', h['u'], -.10, h['z'] - .10, h['w'] + .40, T + .26, .14)
    if kind == 'pavilion':
        iron_balcony(m, f, (lo + hi) / 2, L1 + .8, span - 1.2, depth=.85)
        for i in range(1, round(span / pitch)):
            m.box('stone', lo + pitch * i, -.44, L1 + .40, .40, .80, .60)      # consoles under the balcony
    # Floor bands and the main cornice.
    m.box('stone', (lo + hi) / 2, -.07, L1 - .22, span - 2 * EPS, T + .22, .34)
    m.box('stone', (lo + hi) / 2, -.05, L2 - .16, span - 2 * EPS, T + .16, .22)
    if kind in ('pavilion', 'central'):
        for i in range(1, round(span / pitch)):
            u = lo + pitch * i
            m.box('stone', u, -.09, (L1 + CORNICE - .9) / 2, .62, T + .22, CORNICE - .9 - L1)
            m.box('stone', u, -.13, CORNICE - .98, .80, T + .30, .30)
    eave_cornice(m, lo, hi, CORNICE, T, .70)
    for u, side in returns:   # closed return of a projecting pavilion, overlapping the wing carrier so no face is shared
        m.box('wall', u + side * (T / 2 + .012), (T - .03 + PAV_OUT + T * .6) / 2, (G0 + CORNICE + .45) / 2, T, PAV_OUT + T * .6 - (T - .03), CORNICE + .45 - G0)   # starts behind the carrier front: no shared face
    m.flush('facade')
    return pitch


def mansard_dormer(f, u, z_e, rise, setin, w=1.7, role='stone', win=(1.0, 1.75), top=3.15):
    """Arched dormer standing on a mansard slope: front panel proud of the slope, cheeks back to the slope, small roof."""
    k = setin / rise                    # slope: inward run per metre of rise
    d0 = .30
    z_em = z_e + d0 / k                 # where the front emerges from the slope
    z_top = z_e + top
    ww, hw = win
    zw = z_e + 1.05
    front = f.panel(f'{f.label} dormer front', [(u - w / 2, z_em - .6), (u + w / 2, z_em - .6), (u + w / 2, z_top), (u - w / 2, z_top)], d0 - .16, d0 + .10, role, 'dormers')
    f.cut(front, f'{f.label} dormer window cut', u, zw, ww, hw, depth=.30)
    m = Merge(f)
    shift = d0 - .16
    # reuse framed() with a temporary face whose origin is shifted to the dormer front plane
    g = C.Face(f.p(0, shift, 0), f.t, f.n, f.label + ' dormer')
    mg = Merge(g)
    h = hole(f'{f.label} dormer window {u:.1f}', u, zw, ww, hw)
    framed(mg, g, h, cols=1, rows=2, inset=.10, occupied='attic office', kind='dormer window')
    mg.flush('dormers')
    arch_fill(g, u, zw + hw, ww, ww / 2, role, -.03, .28)
    # arched hood moulding and keystone on the front
    for i in range(10):
        a0, a1 = math.pi * i / 10, math.pi * (i + 1) / 10
        pa = g.p(u + math.cos(a0) * (ww / 2 + .10), -.06, zw + hw - ww / 2 + math.sin(a0) * (ww / 2 + .10))
        pb = g.p(u + math.cos(a1) * (ww / 2 + .10), -.06, zw + hw - ww / 2 + math.sin(a1) * (ww / 2 + .10))
        C.beam('Dormer hood', pa, pb, .12, .10, role, 'dormers')
    g.part('Dormer pediment', u, -.10, z_top - .12, w + .20, .22, .24, role, 'dormers', 0)
    # cheeks: polygon in (d, z) from the front back to the slope
    # roof line z = z_top - .02 + .14 * (d - (d0 - .30)) / 1.3 meets the slope z = z_e + d / k at d_meet
    d_meet = (z_top - .02 - z_e - .14 * (d0 - .30) / 1.3) / (1 / k - .14 / 1.3)
    z_meet = z_e + d_meet / k
    for sgn in (-1, 1):
        uu = u + sgn * (w / 2 - .14)
        pts = [(d0 - .12, z_em - .6), (d0 - .12, z_top - .03), (d_meet, z_meet), (d_meet, z_meet - .7)]
        vs = [f.p(uu - .06, d, z) for d, z in pts] + [f.p(uu + .06, d, z) for d, z in pts]
        fs = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        C.mesh('Dormer cheek', vs, fs, role, 'dormers')
    # roof plate from the front top back into the slope
    vs = [f.p(u - w / 2 - .14, d0 - .30, z_top - .02), f.p(u + w / 2 + .14, d0 - .30, z_top - .02), f.p(u + w / 2 + .14, d0 + 1.0, z_top + .12), f.p(u - w / 2 - .14, d0 + 1.0, z_top + .12)]
    vs += [f.p(u - w / 2 - .14, d0 - .30, z_top - .16), f.p(u + w / 2 + .14, d0 - .30, z_top - .16), f.p(u + w / 2 + .14, d0 + 1.0, z_top - .02), f.p(u - w / 2 - .14, d0 + 1.0, z_top - .02)]
    C.mesh('Dormer roof', vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 'zinc', 'dormers')


def wing_mansard(f, lo, hi, dormers=True, inner=False):
    """Outer mansard slope of one run between pavilions, as a strip in face coordinates, with dormers at each bay."""
    z0, z1 = CORNICE, CORNICE + MANS_H
    lower = [f.p(lo, 0.0, 0)[:2], f.p(hi, 0.0, 0)[:2]]
    upper = [f.p(lo, MANS_IN, 0)[:2], f.p(hi, MANS_IN, 0)[:2]]
    strip(f'{f.label} mansard', lower, upper, z0, z1, 'roof', 'mansard', closed=False)
    if dormers:
        nb = max(1, round((hi - lo) / BAY))
        pitch = (hi - lo) / nb
        for i in range(nb):
            mansard_dormer(f, lo + pitch * (i + .5), z0, MANS_H, MANS_IN)


def pavilion_roof(cx, cy, w, d, rise, setin, cresting=True, dormer_faces=()):
    """Square-plan truncated mansard on a pavilion: four slopes, zinc flat, cresting, corner finials."""
    lower = [(cx - w / 2, cy - d / 2), (cx + w / 2, cy - d / 2), (cx + w / 2, cy + d / 2), (cx - w / 2, cy + d / 2)]
    upper = [(cx - w / 2 + setin, cy - d / 2 + setin), (cx + w / 2 - setin, cy - d / 2 + setin), (cx + w / 2 - setin, cy + d / 2 - setin), (cx - w / 2 + setin, cy + d / 2 - setin)]
    strip('Pavilion mansard', lower, upper, CORNICE, CORNICE + rise, 'roof', 'mansard')
    C.prism('Pavilion flat', [(x + (.02 if x < cx else -.02), y + (.02 if y < cy else -.02)) for x, y in upper], 'z', CORNICE + rise - .14, CORNICE + rise + .06, 'zinc', 'mansard')
    if cresting:
        zc = CORNICE + rise + .06
        for (ax, ay), (bx, by) in zip(upper, upper[1:] + upper[:1]):
            C.beam('Cresting rail', (ax, ay, zc + .45), (bx, by, zc + .45), .04, .04, 'hardware', 'cresting')
            n = int(math.dist((ax, ay), (bx, by)) / .8)
            for i in range(n + 1):
                px, py = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
                C.rod('Cresting picket', (px, py, zc), (px, py, zc + .55), .018, 'hardware', 'cresting', 4)
        for x, y in upper:
            C.rod('Cresting finial', (x, y, zc), (x, y, zc + 1.1), .05, 'hardware', 'cresting', 6)


def tower():
    cx, cy = 0.0, -D / 2 - PAV_OUT + TOWER / 2
    half = TOWER / 2
    z0 = CORNICE + .47
    faces = A.faces(TOWER, TOWER, cx, cy, 'tower ')
    for i, f in enumerate(faces):
        lo, hi = -half, half - EPS
        if i in (1, 3):
            lo, hi = -half + T, half - T
        h1 = hole(f'{f.label} shaft opening', 0.0, CORNICE + 4.9, 2.0, 4.6, kind='arched louvre')
        h2 = hole(f'{f.label} shaft window', 0.0, CORNICE + 1.6, 1.4, 2.0)
        f.wall(f'{f.label} shaft carrier', lo, hi, z0, T_SHAFT, depth=T, role='stone', holes=[h1, h2])
        m = Merge(f)
        for h in (h1, h2):
            reveal(m, f, h, .16, 'stone')
            framed(m, f, h, cols=1, rows=3 if h is h1 else 2, inset=.18, occupied='tower stair', kind=h.get('kind', 'window'), frame='trim', glass='hardware' if h is h1 else 'glass')
        arch_fill(f, 0.0, h1['z'] + h1['h'], h1['w'], h1['w'] / 2, 'stone')
        m.box('stone', 0.0, -.05, h1['z'] - .12, h1['w'] + .6, T + .16, .20)
        m.box('stone', 0.0, -.06, h1['z'] + h1['h'] + .30, h1['w'] + 1.0, T + .18, .26)
        pediment(f, 0.0, h1['z'] + h1['h'] + .46, h1['w'] + 1.3)          # aedicule pediment over the arched opening
        for sgn in (-1, 1):                                                 # pilasters of the aedicule
            m.box('stone', sgn * (h1['w'] / 2 + .55), -.10, (h1['z'] - .3 + h1['z'] + h1['h']) / 2, .40, T + .22, h1['h'] + .3)
        for sgn in (-1, 1):   # corner pilasters
            m.box('stone', sgn * (half - .45), -.10, (z0 + T_SHAFT) / 2, .85, T + .22, T_SHAFT - z0)
        eave_cornice(m, -half - .1, half + .1, T_SHAFT, T, .55, modillions=True)
        m.flush('tower')
    for sx in (-1, 1):
        for sy in (-1, 1):
            C.box('Shaft corner finial base', (cx + sx * (half - .2), cy + sy * (half - .2), T_SHAFT + .25), (.6, .6, .5), 'stone', 'tower', 0)
            C.rod('Shaft corner finial', (cx + sx * (half - .2), cy + sy * (half - .2), T_SHAFT + .5), (cx + sx * (half - .2), cy + sy * (half - .2), T_SHAFT + 1.5), .12, 'stone', 'tower', 8)
    # Clock stage: slightly narrower, verdigris-trimmed, with four round faces.
    ch = TOWER / 2 - .3
    C.box('Clock stage', (cx, cy, (T_SHAFT + T_CLOCK) / 2), (2 * ch, 2 * ch, T_CLOCK - T_SHAFT), 'stone', 'tower', 0)
    C.box('Clock stage plinth', (cx, cy, T_SHAFT + .18), (2 * ch + .5, 2 * ch + .5, .36), 'stone', 'tower', 0)
    C.box('Clock stage cornice', (cx, cy, T_CLOCK - .25), (2 * ch + .9, 2 * ch + .9, .50), 'copper', 'tower', 0)
    C.box('Clock stage cap plinth', (cx, cy, T_CLOCK + .1), (2 * ch + .2, 2 * ch + .2, .20), 'copper', 'tower', 0)
    for (nx, ny) in ((0, -1), (1, 0), (0, 1), (-1, 0)):   # gablet over each clock face (v001 P1 7)
        gf = C.Face((cx + nx * (ch + .45), cy + ny * (ch + .45), 0), (-ny, nx, 0), (-nx, -ny, 0), 'clock gablet')
        gf.panel('Clock gablet', [(-2.2, T_CLOCK - .02), (2.2, T_CLOCK - .02), (0.0, T_CLOCK + 1.2)], -.12, .5, 'stone', 'tower')
        for sgn in (-1, 1):
            C.beam('Clock gablet rake', gf.p(sgn * 2.35, -.20, T_CLOCK + .02), gf.p(0.0, -.20, T_CLOCK + 1.32), .14, .16, 'copper', 'tower')
    zc = (T_SHAFT + T_CLOCK) / 2 + .1
    for (nx, ny) in ((0, -1), (1, 0), (0, 1), (-1, 0)):
        px, py = cx + nx * ch, cy + ny * ch
        q = lambda d, dz=0: (px + nx * d, py + ny * d, zc + dz)
        C.rod('Clock ring', q(0.0), q(.22), 1.55, 'copper', 'clocks', 32)
        C.rod('Clock face', q(.20), q(.26), 1.38, 'clock', 'clocks', 32)
        C.rod('Clock hub', q(.26), q(.30), .10, 'hardware', 'clocks', 8)
        tx, ty = -ny, nx
        for ang, length in ((math.radians(80), 1.05), (math.radians(-20), .75)):
            ex, ey, ez = px + nx * .29 + tx * math.cos(ang) * length, py + ny * .29 + ty * math.cos(ang) * length, zc + math.sin(ang) * length
            C.beam('Clock hand', q(.29), (ex, ey, ez), .07, .03, 'hardware', 'clocks')
        for k in range(12):
            a = math.tau * k / 12
            mx, my, mz = px + nx * .28 + tx * math.cos(a) * 1.2, py + ny * .28 + ty * math.cos(a) * 1.2, zc + math.sin(a) * 1.2
            C.rod('Clock mark', (mx - nx * .02, my - ny * .02, mz), (mx + nx * .02, my + ny * .02, mz), .05, 'hardware', 'clocks', 6)
        for sgn in (-1, 1):   # verdigris corner pilasters of the clock stage
            C.box('Clock stage pilaster', (px + tx * sgn * (ch - .35) + nx * .08, py + ty * sgn * (ch - .35) + ny * .08, (T_SHAFT + T_CLOCK) / 2), (.7 if nx else .3, .3 if nx else .7, T_CLOCK - T_SHAFT - .5), 'copper', 'tower', 0)
    # Convex-concave square cap, lantern and finial.
    BELL = [(1.0, 0.0), (1.07, .06), (1.10, .14), (1.06, .24), (.94, .36), (.76, .48), (.58, .60), (.42, .72), (.28, .84), (.16, .93), (0.0, 1.0)]
    square_cap('Tower cap', cx, cy, T_CLOCK + .2, ch + .15, T_CAP - T_CLOCK - .2, BELL, 'zinc', 'tower')
    for k in range(4):
        a = math.tau * k / 4 + math.pi / 4
        rib_mesh('Cap rib', cx, cy, T_CLOCK + .2, a, [(rf * (ch + .15) * math.sqrt(2), zf * (T_CAP - T_CLOCK - .2)) for rf, zf in smooth_profile(BELL, 28) if zf < .95], .16, .06, 'zinc', 'tower')
    C.rod('Lantern neck', (cx, cy, T_CAP - 1.2), (cx, cy, T_CAP + .1), .62, 'zinc', 'tower', 8)
    C.rod('Lantern base', (cx, cy, T_CAP), (cx, cy, T_CAP + .22), .95, 'zinc', 'tower', 8)
    for k in range(8):
        a = math.tau * k / 8
        C.beam('Lantern column', (cx + math.cos(a) * .72, cy + math.sin(a) * .72, T_CAP + .22), (cx + math.cos(a) * .72, cy + math.sin(a) * .72, T_CAP + 1.5), .09, .09, 'pale', 'tower')
    C.rod('Lantern cap ring', (cx, cy, T_CAP + 1.5), (cx, cy, T_CAP + 1.72), .98, 'zinc', 'tower', 8)
    dome('Lantern cupola', cx, cy, T_CAP + 1.72, .92, 1.1, [(1.0, 0.0), (1.0, .2), (.84, .5), (.5, .8), (0.0, 1.0)], 'zinc', 'tower', 24, 10)
    C.rod('Finial', (cx, cy, T_CAP + 2.7), (cx, cy, T_LAN), .06, 'hardware', 'tower', 8)
    C.rod('Finial ball', (cx, cy, T_LAN - .55), (cx, cy, T_LAN - .25), .18, 'hardware', 'tower', 12)
    C.CONTACTS.append(dict(name='Tower shaft rising out of the central pavilion mansard; clock stage on the shaft cornice; cap on the clock-stage cornice; lantern on a solid neck', shaft_top_m=T_SHAFT, cap_top_m=T_CAP))


def square_cap(name, cx, cy, z0, half, h, profile, role, module):
    """Square-plan swept cap: each profile ring is a square of half-width r(half)."""
    prof = smooth_profile(profile, 24)
    vs, fs = [], []
    rings = len(prof) - 1
    for j in range(rings + 1):
        r = max(half * prof[j][0], .001); zz = z0 + h * prof[j][1]
        for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append((cx + sx * r, cy + sy * r, zz))
    for j in range(rings):
        for i in range(4):
            a0 = j * 4 + i; a1 = j * 4 + (i + 1) % 4; b0 = (j + 1) * 4 + i; b1 = (j + 1) * 4 + (i + 1) % 4
            fs.append((a0, a1, b1, b0))
    fs.append((3, 2, 1, 0))
    C.mesh(name, vs, fs, role, module)


def porch_and_stair():
    """Four-column porch at the piano nobile over a rusticated arcade; broad stone stair to the forecourt."""
    y_face = -D / 2 - PAV_OUT
    y_front = y_face - PORCH_D
    pw = 9.4
    # Undercroft: arcade carriers on the front and both returns.
    front = C.Face((0, y_front, 0), (1, 0, 0), (0, 1, 0), 'porch front')
    holes = [hole('Porch arch 1', 0.0, G0, 2.4, 3.9, kind='open arch'), hole('Porch arch 0', -4.0, G0, 1.0, 3.2, kind='open arch'), hole('Porch arch 2', 4.0, G0, 1.0, 3.2, kind='open arch')]
    front.wall('Porch arcade carrier', -pw / 2, pw / 2, G0, L1 - .35, depth=T, role='rustic', holes=holes)
    G.brick_courses(front, -pw / 2 + .02, pw / 2 - .02, G0 + .25, L1 - .55, holes, spacing=.52)
    for h in holes:
        arch_fill(front, h['u'], h['z'] + h['h'], h['w'], h['w'] / 2, 'rustic')
        C.OPENINGS.append(dict(id=h['id'], face='porch front', u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='open arch', clear_wall_cut=True, carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None,
            face_origin=list(front.o), face_tangent=list(front.t), face_inward=list(front.n), occupied_space='open undercroft to the ground-floor entrance'))
    for sgn in (-1, 1):
        side = C.Face((sgn * pw / 2, (y_face + y_front) / 2, 0), (0, sgn, 0), (-sgn, 0, 0), f'porch side {sgn}')
        sh = [hole(f'Porch side arch {sgn}', 0.0, G0, 2.4, 3.9, kind='open arch')]
        side.wall(f'Porch side carrier {sgn}', -PORCH_D / 2 + T, PORCH_D / 2 - T, G0, L1 - .35, depth=T, role='rustic', holes=sh)
        arch_fill(side, 0.0, sh[0]['z'] + sh[0]['h'], 2.4, 1.2, 'rustic')
    C.box('Porch undercroft slab', (0, (y_face + y_front) / 2, G0 / 2 + .001), (pw - .1, PORCH_D - .1, G0), 'foundation', 'porch', 0)
    C.box('Porch platform', (0, (y_face + y_front) / 2 - .02, L1 - .18), (pw - .1, PORCH_D + .46, .36), 'stone', 'porch', 0)
    C.qa_room_light('Undercroft', (0, (y_face + y_front) / 2, L1 - .8), 60, 4.0)
    # Columns, entablature, balustrade at the second storey.
    for i in range(4):
        x = -pw / 2 + 1.0 + (pw - 2.0) * i / 3
        C.rod('Porch column', (x, y_front + .9, L1 + .36), (x, y_front + .9, L2 - .72), .36, 'stone', 'porch', 16)
        C.box('Porch column base', (x, y_front + .9, L1 + .18), (.95, .95, .36), 'stone', 'porch', 0)
        C.box('Porch column capital', (x, y_front + .9, L2 - .60), (.95, .95, .30), 'stone', 'porch', 0)
    C.box('Porch entablature', (0, y_front + .9, L2 - .22), (pw + .4, 1.5, .50), 'stone', 'porch', 0)
    C.box('Porch cornice', (0, y_front + .9, L2 + .10), (pw + .8, 1.9, .16), 'stone', 'porch', 0)
    # Pediment over the entablature, its tympanum set back, and a sloped roof running back to the pavilion face.
    pf = C.Face((0, y_front + .15, 0), (1, 0, 0), (0, 1, 0), 'porch pediment')
    pf.panel('Porch tympanum', [(-pw / 2 - .2, L2 + .18), (pw / 2 + .2, L2 + .18), (0.0, L2 + .18 + (pw / 2 + .2) * .30)], .18, 1.2, 'stone', 'porch')
    apex = L2 + .26 + (pw / 2 + .5) * .30
    for sgn in (-1, 1):
        C.beam('Porch pediment rake', pf.p(sgn * (pw / 2 + .5), -.10, L2 + .22), pf.p(0.0, -.10, apex + .10), .26, .34, 'stone', 'porch')
    pf.part('Porch pediment bed', 0.0, -.08, L2 + .20, pw + 1.0, .36, .16, 'stone', 'porch', 0)
    for sgn in (-1, 1):
        vs = [(0.0, y_front + .3, apex), (0.0, y_face + .2, apex + .3), (sgn * (pw / 2 + .5), y_face + .2, L2 + .46), (sgn * (pw / 2 + .5), y_front + .3, L2 + .16)]
        vs += [(x, y, z - .16) for x, y, z in vs]
        C.mesh('Porch roof', vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 'zinc', 'porch')
    for sgn in (-1, 1):   # side pilasters under the entablature ends
        C.box('Porch pier', (sgn * (pw / 2 - .5), y_front + .9, (L1 + .36 + L2 - .6) / 2), (.6, 1.1, L2 - .6 - L1 - .36), 'stone', 'porch', 0)
    # Piano-nobile balustrade at the platform edge, broken for the full stair width on newel piers (v001 P1 5).
    balustrade((-pw / 2 - .2, y_front + .2), (-3.4, y_front + .2), L1 + .02)
    balustrade((3.4, y_front + .2), (pw / 2 + .2, y_front + .2), L1 + .02)
    for sgn in (-1, 1):
        C.box('Stair head newel', (sgn * 3.25, y_front + .2, L1 + .62), (.5, .5, 1.24), 'stone', 'balustrades', 0)
        C.box('Stair head newel cap', (sgn * 3.25, y_front + .2, L1 + 1.30), (.62, .62, .12), 'stone', 'balustrades', 0)
    # Stair: 6 m wide, rising north to the platform.
    length = 6.2
    y_s = y_front - length
    G.stair('Grand stair', 0.0, y_s, G0, L1, length, 6.0, .15)
    for sgn in (-1, 1):
        C.prism('Stair cheek wall', [(y_s - .2, 0.0), (y_front - .02, L1 - .20), (y_front - .02, L1 + 1.0), (y_s - .2, 1.0)], 'x', sgn * 3.0 + sgn * .02, sgn * 3.0 + sgn * .30, 'stone', 'stairs')
        C.box('Stair newel', (sgn * 3.19, y_s - .3, .75), (.6, .6, 1.5), 'stone', 'stairs', 0)
        C.box('Stair newel cap', (sgn * 3.19, y_s - .3, 1.56), (.72, .72, .12), 'stone', 'stairs', 0)
    C.CONTACTS.append(dict(name='Porch columns on the platform over the arcade; platform on the arcade carriers; stair on the forecourt', platform_m=L1, entablature_m=L2))


def balustrade(a, b, z, skip=None, height=1.05):
    ax, ay = a; bx, by = b
    L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
    C.beam('Balustrade rail', (ax, ay, z + height - .06), (bx, by, z + height - .06), .22, .12, 'stone', 'balustrades')
    C.beam('Balustrade base', (ax, ay, z + .07), (bx, by, z + .07), .22, .14, 'stone', 'balustrades')
    n = int(L / .36)
    for i in range(n + 1):
        t = L * i / n
        if skip and skip[0] < (t - L / 2) < skip[1]:
            continue
        px, py = ax + ux * t, ay + uy * t
        C.rod('Baluster', (px, py, z + .12), (px, py, z + height - .10), .07, 'stone', 'balustrades', 8)


def court_and_floors():
    outer = [(-W / 2, -D / 2), (W / 2, -D / 2), (W / 2, D / 2), (-W / 2, D / 2)]
    court = [(-CW / 2, -CD / 2), (CW / 2, -CD / 2), (CW / 2, CD / 2), (-CW / 2, CD / 2)]
    C.prism('Ground slab', outer, 'z', 0.0, G0, 'foundation', 'foundation')
    C.prism('Court paving', [(x * .999, y * .999) for x, y in court], 'z', G0, G0 + .01, 'stone', 'court')
    wings = [((-W / 2 + T, -D / 2 + T), (W / 2 - T, -CD / 2)), ((-W / 2 + T, CD / 2), (W / 2 - T, D / 2 - T)),
             ((-W / 2 + T, -CD / 2 - EPS), (-CW / 2, CD / 2 + EPS)), ((CW / 2, -CD / 2 - EPS), (W / 2 - T, CD / 2 + EPS))]
    for zl in (L1, L2, CORNICE):
        for (x0, y0), (x1, y1) in wings:
            C.prism(f'Floor {zl:.1f}', [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 'z', zl - .30, zl, 'floor', 'occupied floors')
    for zl in (L1, L2):
        C.qa_room_light(f'South rooms {zl:.1f}', (0.0, -D / 2 + 6.0, zl + 2.6), 80, 5.0)
        C.qa_room_light(f'West rooms {zl:.1f}', (-W / 2 + 6.0, 2.0, zl + 2.6), 60, 5.0)
    C.qa_room_light('Ground floor', (-10.0, -D / 2 + 6.0, L1 - .9), 90, 6.0)
    # Court faces: plain stone with windows, their own cornice and mansard ring rising inward.
    cf = A.faces(CW, CD, 0, 0, 'court ')
    for i, f in enumerate(cf):
        f = C.Face(f.o, f.t, f.n * -1, f.label)     # court faces look into the court: inward is away from the court
        span = CW if i % 2 == 0 else CD
        lo, hi = (-span / 2, span / 2 - EPS) if i % 2 == 0 else (-span / 2 - T + .02, span / 2 + T - .02)   # side walls run into the front and rear walls: closed corners
        nb = max(1, int(span / 3.0))
        pitch = span / nb
        hs = []
        for k in range(nb):
            c = lo + pitch * (k + .5) + (0 if i % 2 == 0 else 0)
            hs.append(hole(f'{f.label} ground window {k}', c, 1.0, 1.4, 2.8))
            hs.append(hole(f'{f.label} first window {k}', c, L1 + .8, 1.4, 2.6))
            hs.append(hole(f'{f.label} second window {k}', c, L2 + .8, 1.3, 2.2))
        f.wall(f'{f.label} carrier', lo, hi, G0, CORNICE + .45, depth=T, role='wall', holes=hs)
        m = Merge(f)
        for h in hs:
            framed(m, f, h, cols=1, rows=1, occupied='offices')
            m.box('stone', h['u'], -.05, h['z'] + h['h'] + .14, h['w'] + .40, T + .16, .18)
            m.box('stone', h['u'], -.06, h['z'] - .08, h['w'] + .30, T + .18, .12)
        m.box('stone', 0.0, -.05, L1 - .20, span - 2 * EPS, T + .16, .26)
        eave_cornice(m, lo, hi, CORNICE, T, .40, modillions=False)
        m.flush('court')
    # Inner mansard ring around the court and the four flat zinc tops.
    lower = [(x, y) for x, y in court]
    upper = [(x + (MANS_IN if x > 0 else -MANS_IN), y + (MANS_IN if y > 0 else -MANS_IN)) for x, y in court]
    inner_ring = strip('Court mansard ring', lower[::-1], upper[::-1], CORNICE, CORNICE + MANS_H, 'roof', 'mansard')
    zt = CORNICE + MANS_H
    # Hipped zinc upper roofs over each wing: outer slope from the mansard top up to a ridge ring along the wing
    # centrelines, inner slope down to the court mansard top (v001 P1 9).
    flat_outer = [(-W / 2 + MANS_IN, -D / 2 + MANS_IN), (W / 2 - MANS_IN, -D / 2 + MANS_IN), (W / 2 - MANS_IN, D / 2 - MANS_IN), (-W / 2 + MANS_IN, D / 2 - MANS_IN)]
    wx, wy = ((W - CW) / 2 - 2 * MANS_IN) / 2, ((D - CD) / 2 - 2 * MANS_IN) / 2
    ridge = [(x + (wx if x < 0 else -wx), y + (wy if y < 0 else -wy)) for x, y in flat_outer]
    strip('Wing upper roof outer', flat_outer, ridge, zt + .04, zt + .04 + UPPER_RISE, 'zinc', 'mansard')
    strip('Wing upper roof inner', ridge, upper, zt + .04 + UPPER_RISE, zt + .04, 'zinc', 'mansard')
    for (ax, ay), (bx, by) in zip(ridge, ridge[1:] + ridge[:1]):
        C.beam('Ridge cap', (ax, ay, zt + .06 + UPPER_RISE), (bx, by, zt + .06 + UPPER_RISE), .30, .10, 'zinc', 'mansard')
    for x, y in ((-W / 2 + PAV + 4.0, -D / 2 + 4.5), (W / 2 - PAV - 4.0, D / 2 - 4.5), (-W / 2 + 4.5, D / 2 - PAV - 4.0), (W / 2 - 4.5, -D / 2 + PAV + 4.0)):
        C.box('Chimney stack', (x, y, zt + UPPER_RISE + .6), (1.3, 1.0, 2.6), 'stone', 'chimneys', 0)
        C.box('Chimney cap', (x, y, zt + UPPER_RISE + 1.98), (1.5, 1.2, .16), 'pale', 'chimneys', 0)
    # Council chamber behind the porch for the interior view.
    A.sofa(8.0, -D / 2 + 5.0, L1); A.desk(12.0, -D / 2 + 3.5, L1 + .05)
    C.box('Chamber partition', (15.0, -D / 2 + 6.5, L1 + 1.8), (.16, 11.0, 3.6), 'interior', 'partitions', 0)
    C.qa_room_light('Interior view room', (10.0, -D / 2 + 4.0, L1 + 3.6), 160, 5.0)


def site():
    x0, x1, y0, y1 = SITE
    yf = y0 + 8.5                      # fence line: street, kerb, 2.5 m sidewalk, fence
    C.box('Street south', ((x0 + x1) / 2, y0 + 3.0, .004), (x1 - x0, 6.0, .008), 'concrete', 'street', 0)
    C.box('Street west', (x0 + 3.0, (y0 + 6.0 + y1) / 2, .004), (6.0, y1 - y0 - 6.0, .008), 'concrete', 'street', 0)
    C.box('Kerb south', ((x0 + x1) / 2, y0 + 6.06, .06), (x1 - x0 - 6.0, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb west', (x0 + 6.06, (y0 + y1) / 2, .06), (.12, y1 - y0, .12), 'stone', 'sidewalk', 0)
    C.box('South sidewalk', ((x0 + 6.0 + x1) / 2, (y0 + 6.0 + yf) / 2, .0075), (x1 - x0 - 6.0, yf - y0 - 6.0, .015), 'foundation', 'sidewalk', 0)
    wx = -W / 2 - PAV_OUT
    C.box('West sidewalk', ((x0 + 6.0 + wx) / 2, (yf + y1) / 2, .0075), (wx - x0 - 6.0, y1 - yf, .015), 'foundation', 'sidewalk', 0)
    C.box('East sidewalk', ((W / 2 + PAV_OUT + x1) / 2, (yf + y1) / 2, .0075), (x1 - W / 2 - PAV_OUT, y1 - yf, .015), 'foundation', 'sidewalk', 0)
    C.box('North sidewalk', (0, (D / 2 + PAV_OUT + y1) / 2, .0075), (W + 2 * PAV_OUT, y1 - D / 2 - PAV_OUT, .015), 'foundation', 'sidewalk', 0)
    yb = -D / 2 - PAV_OUT
    C.box('Forecourt lawn', (0, (yf + .3 + yb) / 2, .02), (W + 2 * PAV_OUT, yb - yf - .3, .04), 'planting', 'forecourt', 0)
    C.box('Forecourt path', (0, (yf + yb) / 2, .05), (8.4, yb - yf, .02), 'stone', 'forecourt', 0)
    iron_fence((wx, yf), (-4.5, yf)); iron_fence((4.5, yf), (W / 2 + PAV_OUT, yf))
    for sgn in (-1, 1):
        C.box('Gate pier', (sgn * 4.7, yf, 1.2), (.7, .7, 2.4), 'stone', 'fence', 0); C.box('Gate pier cap', (sgn * 4.7, yf, 2.48), (.9, .9, .16), 'stone', 'fence', 0)
    iron_fence((wx, yf), (wx, yb - .4))
    iron_fence((W / 2 + PAV_OUT, yb - .4), (W / 2 + PAV_OUT, yf))
    for x in (-17.0, 17.0):
        street_tree(x, yf + 2.4, height=7.0)
    street_tree(x0 + 7.0, 12.0, height=8.0); street_tree(x0 + 7.0, -8.0, height=8.0)


def build():
    global CEN_D
    site()
    court_and_floors()
    # Outer faces: base plane and pavilion planes projecting PAV_OUT.
    def shifted(f, proj):
        return C.Face(f.o - f.n * proj, f.t, f.n, f.label)
    south = C.Face((0, -D / 2, 0), (1, 0, 0), (0, 1, 0), 'south')
    west = C.Face((-W / 2, 0, 0), (0, -1, 0), (1, 0, 0), 'west')
    north = C.Face((0, D / 2, 0), (-1, 0, 0), (0, -1, 0), 'north')
    east = C.Face((W / 2, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    # South: SW pavilion, run, central pavilion, run, SE pavilion.
    sp = shifted(south, PAV_OUT)
    elevation(C.Face(sp.o, sp.t, sp.n, 'south-west pavilion'), -W / 2 - PAV_OUT, -W / 2 + PAV, 'pavilion', returns=((-W / 2 + PAV, -1),))
    elevation(C.Face(south.o, south.t, south.n, 'south run west'), -W / 2 + PAV, -CEN_W / 2, 'wing')
    elevation(C.Face(sp.o, sp.t, sp.n, 'south central pavilion'), -CEN_W / 2, CEN_W / 2, 'central', returns=((-CEN_W / 2, 1), (CEN_W / 2, -1)))
    elevation(C.Face(south.o, south.t, south.n, 'south run east'), CEN_W / 2, W / 2 - PAV, 'wing')
    elevation(C.Face(sp.o, sp.t, sp.n, 'south-east pavilion'), W / 2 - PAV, W / 2 + PAV_OUT, 'pavilion', returns=((W / 2 - PAV, 1),))
    # West (u = -y): NW pavilion at u in [-D/2-.6, -D/2+9] is the north end; SW pavilion at the south end.
    wp = shifted(west, PAV_OUT)
    elevation(C.Face(wp.o, wp.t, wp.n, 'west south pavilion'), D / 2 - PAV, D / 2 + PAV_OUT - T, 'pavilion', returns=((D / 2 - PAV, 1),))
    elevation(C.Face(west.o, west.t, west.n, 'west run'), -D / 2 + PAV, D / 2 - PAV, 'wing')
    elevation(C.Face(wp.o, wp.t, wp.n, 'west north pavilion'), -D / 2 - PAV_OUT + T, -D / 2 + PAV, 'pavilion', returns=((-D / 2 + PAV, -1),))
    npv = shifted(north, PAV_OUT)
    elevation(C.Face(npv.o, npv.t, npv.n, 'north east pavilion'), -W / 2 - PAV_OUT, -W / 2 + PAV, 'pavilion', returns=((-W / 2 + PAV, -1),))
    elevation(C.Face(north.o, north.t, north.n, 'north run'), -W / 2 + PAV, W / 2 - PAV, 'wing')
    elevation(C.Face(npv.o, npv.t, npv.n, 'north west pavilion'), W / 2 - PAV, W / 2 + PAV_OUT, 'pavilion', returns=((W / 2 - PAV, 1),))
    ep = shifted(east, PAV_OUT)
    elevation(C.Face(ep.o, ep.t, ep.n, 'east south pavilion'), -D / 2 - PAV_OUT + T, -D / 2 + PAV, 'pavilion', returns=((-D / 2 + PAV, -1),))
    elevation(C.Face(east.o, east.t, east.n, 'east run'), -D / 2 + PAV, D / 2 - PAV, 'wing')
    elevation(C.Face(ep.o, ep.t, ep.n, 'east north pavilion'), D / 2 - PAV, D / 2 + PAV_OUT - T, 'pavilion', returns=((D / 2 - PAV, 1),))
    # Corner quoin posts hide the mitres of bands and cornices.
    for qx, qy in ((-W / 2 - PAV_OUT, -D / 2 - PAV_OUT), (W / 2 + PAV_OUT, -D / 2 - PAV_OUT), (W / 2 + PAV_OUT, D / 2 + PAV_OUT), (-W / 2 - PAV_OUT, D / 2 + PAV_OUT)):
        C.box('Corner quoin', (qx, qy, (CORNICE + .45) / 2), (1.1, 1.1, CORNICE + .45), 'stone', 'corner posts', 0)
        C.box('Corner cornice block', (qx + (.14 if qx > 0 else -.14), qy + (.14 if qy > 0 else -.14), CORNICE - .36), (1.62, 1.62, .72), 'stone', 'corner posts', 0)
    for qx, qy in ((-W / 2 + PAV, -D / 2 - .3), (W / 2 - PAV, -D / 2 - .3), (-CEN_W / 2, -D / 2 - .3), (CEN_W / 2, -D / 2 - .3),
                   (-W / 2 - .3, -D / 2 + PAV), (-W / 2 - .3, D / 2 - PAV), (-W / 2 + PAV, D / 2 + .3), (W / 2 - PAV, D / 2 + .3), (W / 2 + .3, -D / 2 + PAV), (W / 2 + .3, D / 2 - PAV)):
        C.box('Pavilion cornice return block', (qx, qy, CORNICE - .36), (1.2, 1.2, .72), 'stone', 'corner posts', 0)
    # Roofs: wing mansards with dormers, pavilion mansards, court ring (in court_and_floors), tower.
    wing_mansard(C.Face(south.o, south.t, south.n, 'south run west'), -W / 2 + PAV, -CEN_W / 2)
    wing_mansard(C.Face(south.o, south.t, south.n, 'south run east'), CEN_W / 2, W / 2 - PAV)
    wing_mansard(C.Face(west.o, west.t, west.n, 'west run'), -D / 2 + PAV, D / 2 - PAV)
    wing_mansard(C.Face(north.o, north.t, north.n, 'north run'), -W / 2 + PAV, W / 2 - PAV)
    wing_mansard(C.Face(east.o, east.t, east.n, 'east run'), -D / 2 + PAV, D / 2 - PAV)
    for cx, cy in ((-W / 2 + PAV / 2 - PAV_OUT / 2, -D / 2 + PAV / 2 - PAV_OUT / 2), (W / 2 - PAV / 2 + PAV_OUT / 2, -D / 2 + PAV / 2 - PAV_OUT / 2),
                   (W / 2 - PAV / 2 + PAV_OUT / 2, D / 2 - PAV / 2 + PAV_OUT / 2), (-W / 2 + PAV / 2 - PAV_OUT / 2, D / 2 - PAV / 2 + PAV_OUT / 2)):
        pavilion_roof(cx, cy, PAV + PAV_OUT, PAV + PAV_OUT, PAV_H, 1.7)
        # dormers on the two outer faces of each pavilion
        hp = (PAV + PAV_OUT) / 2
        outer = []
        outer.append(C.Face((cx, cy - hp, 0), (1, 0, 0), (0, 1, 0), 'pavilion south') if cy < 0 else C.Face((cx, cy + hp, 0), (-1, 0, 0), (0, -1, 0), 'pavilion north'))
        outer.append(C.Face((cx - hp, cy, 0), (0, -1, 0), (1, 0, 0), 'pavilion west') if cx < 0 else C.Face((cx + hp, cy, 0), (0, 1, 0), (-1, 0, 0), 'pavilion east'))
        kp = 1.7 / PAV_H
        for f in outer:
            raised = C.Face(f.o + f.n * (1.3 * kp), f.t, f.n, f.label)
            mansard_dormer(raised, 0.0, CORNICE + 1.3, PAV_H - 1.3, 1.7 - 1.3 * kp, w=2.6, win=(1.5, 2.3), top=3.9)
    CEN_D = 11.0
    pavilion_roof(0.0, -D / 2 - PAV_OUT + CEN_D / 2, CEN_W, CEN_D, MANS_H, MANS_IN, cresting=False)
    porch_and_stair()
    tower()


CEN_D = 11.0
LIGHT_RIG = dict(key=(-50, -60, 60), fill=(56, -30, 40), rear=(-20, 60, 50), target=(0, 0, 14.0), gain=9.0)
