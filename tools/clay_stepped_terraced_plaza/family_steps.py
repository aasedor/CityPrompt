"""Stepped terraced plaza, authored from the locked catalogue views of
stepped_terraced_plaza / variant_0 (stepped_terraced_plaza_v0).

Read from the pixels (the top view governs the plan): a Cycladic hillside stair-plaza, a long strip climbing
north between rows of white cubic houses. A narrow central stair with two metal handrails and a landing at
every terrace level; on each side broad terraces of white-rendered risers with two seating steps and stone-paved
platforms; a white parapet wall with terracotta pots of red geraniums along the east terraces and a narrow side
stair beyond it; a low white parapet on the west. White houses with blue doors and window frames step up the
slope on both sides, one draped in magenta bougainvillea; a blue-domed chapel at the top on the west and a
white belfry with a blue cupola at the foot on the east. A paved lower plaza at the bottom.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-stepped-terraced-plaza'
X0, X1, Y0, Y1 = -10.0, 10.0, -26.0, 26.0      # the stair-plaza strip, 20 m wide, 52 m long
NT = 8                                          # terraces
TL = (Y1 - Y0) / NT                             # terrace length (6.5 m)
TR = 1.1                                        # terrace rise
SX = 2.0                                        # half-width of the central stair
EP = 8.0                                        # east parapet line
T = .3
EPS = .002
PALETTE = dict(wall=(.94, .93, .90), white=(.95, .94, .91), stone=(.72, .64, .50), paving=(.70, .62, .50),
    joint=(.56, .50, .40), trim=(.18, .30, .58), blue=(.18, .30, .58), glass=(.20, .24, .28), hardware=(.45, .45, .42),
    pot=(.66, .36, .22), planting=(.26, .42, .18), flower=(.80, .12, .12), bougain=(.70, .16, .50),
    timber=(.56, .44, .30), interior=(.84, .80, .74), floor=(.62, .56, .48), pale=(.88, .88, .86),
    roof=(.90, .89, .86), dome=(.20, .34, .62), sand=(.74, .68, .58), soil=(.30, .22, .14), concrete=(.70, .69, .66),
    asphalt=(.30, .30, .31))


def manifest(version):
    h = NT * TR + 7.0
    cams = G.camera_roster(X1 - X0 + 16.0, Y1 - Y0 + 8.0, h, [
        ('facade_close', (0.0, Y0 - 10.0, 3.0), (0.0, Y0 + 10.0, 3.0), 45),
        ('architecture_close', (-6.0, Y0 + 6.0, 4.5), (-11.0, Y0 + 13.0, 3.4), 40),
        ('glass_close', (-5.5, Y0 + 9.0, TR * 2 + 1.6), (-10.0, Y0 + 10.5, TR * 2 + 1.4), 40),
        ('central_stair', (0.0, Y0 - 3.0, 2.2), (0.0, Y0 + 12.0, 3.5), 40),
        ('seating_terraces', (-7.0, Y0 + 5.0, 3.6), (-3.0, Y0 + 14.0, 2.4), 40),
        ('parapet_pots', (5.0, Y0 + 9.0, 4.4), (8.0, Y0 + 16.0, 3.6), 40),
        ('side_stair', (12.5, Y0 - 4.0, 3.0), (9.2, Y0 + 12.0, 3.5), 40),
        ('chapel_top', (2.0, Y1 - 6.0, NT * TR + 3.0), (-9.0, Y1 + 4.0, NT * TR + 3.5), 40),
        ('interior', (-12.0, Y0 + 13.0, TR * 2 + 1.6), (-10.0, Y0 + 9.0, TR * 2 + 1.4), 40),
        ('rear_north', (0.0, Y1 + 26.0, NT * TR + 8.0), (0.0, Y1 - 6.0, NT * TR), 45)])
    for c in cams:                       # the locked front looks up the stair from the lower plaza
        if c['name'] == 'front':
            c['location'] = (2.5, Y0 - 9.0, 1.7); c['target'] = (-.5, Y0 + 14.0, 5.0); c['lens'] = 24; c['whole'] = False
        elif c['name'] == 'front_corner':                                      # the locked oblique looks up the strip from high in the south
            c['location'] = (6.0, Y0 - 34.0, 30.0); c['target'] = (0.0, -2.0, 3.0); c['lens'] = 35
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='stepped_terraced_plaza/variant_0 (stepped_terraced_plaza_v0)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=0, storey_programme='open space: eight terraces climbing 8.8 m, flanked by one-storey houses',
            plan='20 x 52 m stair-plaza strip (top view): central stair, west and east terraces, east parapet and side stair, a lower plaza',
            facade='white-rendered risers and parapets, stone-paved platforms and treads, metal handrails, terracotta pots with geraniums, white houses with blue doors',
            levels_m=[TR * k for k in range(NT + 1)],
            inferred='the hillside below grade is not modelled: the terraces stand as solids on a level base; house interiors are assumptions'),
        roof_contract=dict(type='open space; flat white roofs on the flanking houses, a blue chapel dome and belfry cupola', datum_m=0.0, crowns_m=[NT * TR]),
        identity_contract=dict(owner='white Cycladic stair-plaza: central handrailed stair between terraced seating platforms, parapet with geranium pots, blue-trimmed white houses, chapel dome and belfry'),
        material_contract=dict(profile='source-palette clay: white render, warm stone paving and treads, blue doors and frames, terracotta pots, red geraniums, magenta bougainvillea, blue domes', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='stair, seating terraces, landings', edges='houses, a chapel, a belfry'),
        contact_contract=['Grade-zero lower plaza', 'Terrace solids from grade', 'Stair landings flush with the terraces', 'Houses on the terrace levels'],
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
        m.box(frame, u, inset - .012, z + hh / 2, .05, .04, hh - .02)               # glazing bars in front of the pane
        m.box(frame, u, inset - .012, z + hh * .55, w - .02, .04, .05)
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


def reveal(m, f, h, inset=.16, role='stone', jambs_only=False):
    """Lined reveal: thin liners inside the cut from the face to the frame (jambs only when the vertex budget asks)."""
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    for s in (-1, 1):
        m.box(role, u + s * (w / 2 - .02), inset / 2 - .01, z + hh / 2, .04, inset + .02, hh)
    if jambs_only:
        return
    m.box(role, u, inset / 2 - .01, z + hh - .02, w, inset + .02, .04)
    m.box(role, u, inset / 2 - .01, z + .02, w, inset + .02, .04)


def iron_balcony(m, f, u, z, w, depth=.8, role='hardware', slab='stone', spacing=.30):
    """Cantilevered balcony: stone slab with a merged iron lattice (top rail, end rails, mid rail, pickets)."""
    m.box(slab, u, -depth / 2 + .02, z - .10, w, depth + .04, .20)
    m.box(role, u, -depth + .04, z + .98, w, .05, .05)
    for e in (-1, 1):
        m.box(role, u + e * (w / 2 - .02), -depth / 2 + .02, z + .98, .05, depth - .04, .05)
    m.box(role, u, -depth + .04, z + .50, w, .03, .03)
    n = max(4, int(w / spacing))
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


def annulus(name, centre, axis, r_in, r_out, d0, d1, role, module, segs=24):
    """Ring (annulus) extruded along a unit axis from d0 to d1 about `centre`: a real frame with a hole, unlike rod()."""
    ax = C.Vector(axis).normalized()
    side = ax.cross(C.Vector((0, 0, 1)))
    if side.length < 1e-6:
        side = ax.cross(C.Vector((0, 1, 0)))
    side.normalize(); up = ax.cross(side).normalized()
    cen = C.Vector(centre)
    vs = []
    for d in (d0, d1):
        for r in (r_in, r_out):
            for i in range(segs):
                a = math.tau * i / segs
                vs.append(tuple(cen + ax * d + (side * math.cos(a) + up * math.sin(a)) * r))
    I0, O0, I1, O1 = 0, segs, 2 * segs, 3 * segs
    fs = []
    for i in range(segs):
        j = (i + 1) % segs
        fs.append((I0 + i, O0 + i, O0 + j, I0 + j))      # d0 end
        fs.append((I1 + j, O1 + j, O1 + i, I1 + i))      # d1 end
        fs.append((O0 + i, O1 + i, O1 + j, O0 + j))      # outer wall
        fs.append((I0 + j, I1 + j, I1 + i, I0 + i))      # inner wall
    return C.mesh(name, vs, fs, role, module)


def cut_rod(owner, centre, r, z0, z1, sides=48):
    """Boolean-subtract a vertical cylinder from `owner` (like clay_core.cut_box, for round cut-outs)."""
    cx, cy = centre
    cutter = C.rod('Cylinder cutter', (cx, cy, z0), (cx, cy, z1), r, 'wall', 'construction cutter', sides)
    cutter.data.materials.clear(); cutter.data.materials.append(owner.data.materials[0])
    C.bpy.context.view_layer.objects.active = owner
    mod = owner.modifiers.new('cylinder cut', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'; mod.object = cutter
    C.bpy.ops.object.modifier_apply(modifier=mod.name)
    C.remove_cutter(cutter)
    C.normalise(owner.data)


# ---- wave G shared helpers (copied into each wave G family; kept identical) ----

class Batch:
    """Merges boxes and oriented beams per role into one mesh each."""
    def __init__(self):
        self.g = {}

    def _hex(self, role, corners):
        V, F = self.g.setdefault(role, ([], []))
        o = len(V)
        V.extend(corners)
        F.extend(tuple(o + i for i in face) for face in C.BOX_FACES)

    def box(self, role, cx, cy, cz, sx, sy, sz):
        self._hex(role, [(cx + du * sx / 2, cy + dd * sy / 2, cz + dz * sz / 2) for dz in (-1, 1) for du, dd in ((-1, -1), (1, -1), (1, 1), (-1, 1))])

    def beam(self, role, a, b, w, d=None, ext=0.0):
        d = d or w
        ax = [b[i] - a[i] for i in range(3)]
        L = math.sqrt(sum(v * v for v in ax))
        if L < 1e-6:
            return
        ax = [v / L for v in ax]
        a = [a[i] - ax[i] * ext for i in range(3)]; b = [b[i] + ax[i] * ext for i in range(3)]
        ref = (0.0, 0.0, 1.0) if abs(ax[2]) < .95 else (0.0, 1.0, 0.0)
        s = (ax[1] * ref[2] - ax[2] * ref[1], ax[2] * ref[0] - ax[0] * ref[2], ax[0] * ref[1] - ax[1] * ref[0])
        n = math.sqrt(sum(v * v for v in s)); s = [v / n for v in s]
        u = (ax[1] * s[2] - ax[2] * s[1], ax[2] * s[0] - ax[0] * s[2], ax[0] * s[1] - ax[1] * s[0])
        pts = []
        for p in (a, b):
            for du, dd in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                pts.append(tuple(p[i] + du * w / 2 * s[i] + dd * d / 2 * u[i] for i in range(3)))
        self._hex(role, pts)

    def flush(self, module):
        for role, (V, F) in self.g.items():
            if F:
                C.mesh(f'{module} {role}', V, F, role, module)
        self.g = {}


def loft(name, rings, role, module, closed=True):
    """Loft a closed profile (list of 3D points) carried along a sequence of rings."""
    n, m = len(rings), len(rings[0])
    vs = [v for ring in rings for v in ring]
    fs = []
    for i in range(n if closed else n - 1):
        a, b = i * m, ((i + 1) % n) * m
        for j in range(m):
            k = (j + 1) % m
            fs.append((a + j, b + j, b + k, a + k))
    if not closed:
        fs.append(tuple(range(m - 1, -1, -1))); fs.append(tuple((n - 1) * m + j for j in range(m)))
    return C.mesh(name, vs, fs, role, module)


def pitched_roof(name, x0, x1, y0, y1, z, rise, hip_w=True, hip_e=True, axis='x', ov=.35, role='roof', module='roof'):
    """Pitched roof plate over a rectangle, ridge along `axis`; each end hipped or gabled (a gable end closes vertically)."""
    if axis == 'x':
        ym = (y0 + y1) / 2; half = (y1 - y0) / 2
        rx0 = x0 + half if hip_w else x0 - ov
        rx1 = x1 - half if hip_e else x1 + ov
        lower = [(x0 - ov, y0 - ov), (x1 + ov, y0 - ov), (x1 + ov, y1 + ov), (x0 - ov, y1 + ov)]
        upper = [(rx0, ym), (rx1, ym), (rx1, ym), (rx0, ym)]
        if not hip_w:
            lower[0] = (x0 - ov, y0 - ov); lower[3] = (x0 - ov, y1 + ov)
        if not hip_e:
            lower[1] = (x1 + ov, y0 - ov); lower[2] = (x1 + ov, y1 + ov)
    else:
        xm = (x0 + x1) / 2; half = (x1 - x0) / 2
        ry0 = y0 + half if hip_w else y0 - ov
        ry1 = y1 - half if hip_e else y1 + ov
        lower = [(x0 - ov, y0 - ov), (x1 + ov, y0 - ov), (x1 + ov, y1 + ov), (x0 - ov, y1 + ov)]
        upper = [(xm, ry0), (xm, ry0), (xm, ry1), (xm, ry1)]
    return strip(name, lower, upper, z - ov * rise / max(.01, (y1 - y0) / 2 if axis == 'x' else (x1 - x0) / 2), z + rise, role, module)


def gable_wall(name, x, y0, y1, z, rise, axis='x', t=None, role='wall', module='envelope'):
    """Triangular gable infill on a wall top; axis 'x' means the gable lies in the plane x = const."""
    t = t or T
    if axis == 'x':
        C.prism(name, [(y0, z), (y1, z), ((y0 + y1) / 2, z + rise)], 'x', x - t / 2, x + t / 2, role, module)
    else:
        C.prism(name, [(y0, z), (y1, z), ((y0 + y1) / 2, z + rise)], 'y', x - t / 2, x + t / 2, role, module)


def chimney(b, x, y, z0, z1, w=.9, d=.6, pots=2, role='brick', pot='pot', cap='stone'):
    """Brick stack with a projecting cap course and clay pots."""
    b.box(role, x, y, (z0 + z1) / 2, w, d, z1 - z0)
    b.box(cap, x, y, z1 + .06, w + .12, d + .12, .12)
    for k in range(pots):
        px = x - w / 2 + w * (k + .5) / pots
        b.box(pot, px, y, z1 + .12 + .25, .18, .18, .5)


# ---- Stepped terraced plaza ----

G_STEP = .32                                    # stair going
N_STEP = 7                                      # risers per terrace on the stairs


def yk(k):
    return Y0 + k * TL


def lv(k):
    return k * TR


def solid(b, x0, x1, ya, yb, top, nose=.03):
    """A white-rendered solid from grade with a stone tread plate on top, nosing over the riser below."""
    b.box('white', (x0 + x1) / 2, (ya + yb) / 2, (top - .06) / 2, x1 - x0, yb - ya, top - .06)
    b.box('stone', (x0 + x1) / 2, (ya - nose + yb) / 2, top - .03, x1 - x0, yb - ya + nose, .06)


def stair(b, x0, x1):
    """Continuous stair: seven risers at the start of each terrace, then a landing at the terrace level."""
    rise = TR / N_STEP
    for k in range(NT):
        for i in range(1, N_STEP + 1):
            solid(b, x0, x1, yk(k) + (i - 1) * G_STEP, yk(k) + i * G_STEP, lv(k) + i * rise)
        solid(b, x0, x1, yk(k) + N_STEP * G_STEP, yk(k + 1), lv(k + 1))


def stair_level(y):
    k = min(NT - 1, int((y - Y0) // TL))
    i = (y - yk(k)) / G_STEP
    return lv(k) + TR * min(1.0, math.ceil(max(i, 1e-6)) / N_STEP) if i < N_STEP else lv(k + 1)


def terraces(b, x0, x1):
    """Seating terraces: a seat step and a riser up to a broad stone-paved platform on each terrace."""
    for k in range(NT):
        solid(b, x0, x1, yk(k), yk(k) + .55, lv(k) + TR / 2)
        solid(b, x0, x1, yk(k) + .55, yk(k + 1), lv(k + 1))


def handrail(b, x):
    pts = []
    for k in range(NT):
        for i in range(N_STEP + 1):
            pts.append((yk(k) + i * G_STEP + .16, lv(k) + TR * i / N_STEP + .95))
        pts.append((yk(k + 1) - .2, lv(k + 1) + .95))
    for (ya, za), (yb, zb) in zip(pts, pts[1:]):
        b.beam('hardware', (x, ya, za), (x, yb, zb), .05, .05)
    for k in range(NT):
        for y in (yk(k) + .16, yk(k) + N_STEP * G_STEP + .16, yk(k) + (N_STEP * G_STEP + TL) / 2):
            z = stair_level(y)
            b.box('hardware', x, y, z + .475, .045, .045, .95)


def pot(b, x, y, z, s=1.0):
    """Terracotta pot of red geraniums."""
    cyl8(b, 'pot', x, y, z, z + .42 * s, .24 * s)
    b.box('pot', x, y, z + .44 * s, .54 * s, .54 * s, .05)
    for dx, dy in ((-.12, -.08), (.12, -.06), (0, .12), (0, 0)):
        b.box('planting', x + dx * s, y + dy * s, z + .58 * s, .26 * s, .26 * s, .22 * s)
    for dx, dy in ((-.1, -.1), (.12, .02), (-.02, .14), (.08, -.14), (0, 0)):
        b.box('flower', x + dx * s, y + dy * s, z + .73 * s, .11 * s, .11 * s, .1 * s)


def cyl8(b, role, cx, cy, z0, z1, r, n=8):
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for z in (z0, z1):
        for i in range(n):
            a = 2 * math.pi * (i + .5) / n
            V.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    F.append(tuple(o + i for i in range(n - 1, -1, -1)))
    F.append(tuple(o + n + i for i in range(n)))
    for i in range(n):
        j = (i + 1) % n
        F.append((o + i, o + j, o + n + j, o + n + i))


def plaza_strip():
    b = Batch()
    terraces(b, X0, -SX)
    stair(b, -SX, SX)
    terraces(b, SX, EP)
    for k in range(NT):                                                        # east parapet stepping with the terraces
        top = lv(k + 1) + .95
        b.box('white', EP + .2, (yk(k) + yk(k + 1)) / 2, top / 2, .4, TL, top)
        b.box('stone', EP + .2, (yk(k) + yk(k + 1)) / 2, top + .03, .48, TL, .06)
    stair(b, EP + .4, X1)
    # Top landing across the strip; the lower plaza.
    b.box('white', 0.0, Y1 + 2.5, (lv(NT) - .06) / 2, X1 - X0, 5.0, lv(NT) - .06)
    b.box('stone', 0.0, Y1 + 2.5 - .015, lv(NT) - .03, X1 - X0, 5.03, .06)
    b.flush('stair plaza')
    b = Batch()
    handrail(b, -.9)
    handrail(b, .9)
    b.flush('handrails')
    C.box('Lower plaza', (0.0, Y0 - 5.0, .02), (40.0, 10.0, .04), 'paving', 'site', 0)
    b = Batch()
    for k in range(-26, 27):
        b.box('joint', k * .75, Y0 - 5.0, .042, .02, 9.98, .004)
    for k in range(13):
        b.box('joint', 0.0, Y0 - 9.6 + k * .75, .042, 39.98, .02, .004)
    for k in range(NT):                                                        # pots on the east terraces by the parapet
        for dy in (1.6, 3.4, 5.2):
            pot(b, EP - .4, yk(k) + dy, lv(k + 1))
    for dy in (1.0, 3.0, 5.0):                                                 # and along the west edge of the lowest terraces
        pot(b, X0 + .9, yk(0) + dy, lv(1))
    for x in (-SX - .6, SX + .6):
        pot(b, x, Y0 - .6, .04, 1.1)
    b.box('white', X0 + .2, (yk(0) + .55 + yk(1)) / 2, lv(1) + .45, .4, TL - .55, .9)  # low west parapet on the first terrace
    b.flush('pots')
    C.CONTACTS.append(dict(name='Terrace and stair solids from grade; stone plates on every tread and platform'))


def house(label, x_face, ya, yb, base, h, facing, door=True, deep=7.0, extra=None):
    """A white cubic house: a facade wall with real cuts (blue door, blue-framed windows) backed by a solid."""
    if facing > 0:                                                             # faces east (+x)
        f = C.Face((x_face, 0, 0), (0, 1, 0), (-1, 0, 0), label)
        lo, hi = ya, yb
        bx0, bx1 = x_face - deep, x_face - T
    else:                                                                      # faces west (-x)
        f = C.Face((x_face, 0, 0), (0, -1, 0), (1, 0, 0), label)
        lo, hi = -yb, -ya
        bx0, bx1 = x_face + T, x_face + deep
    um = (lo + hi) / 2
    hs = []
    if door:
        hs.append(hole(f'{label} door', um, base, 1.0, 2.2, kind='door'))
        hs += [hole(f'{label} window {s:+d}', um + s * 1.9, base + .9, 1.0, 1.3) for s in (-1, 1) if abs(s * 1.9) + .7 < (hi - lo) / 2]
    else:
        hs += [hole(f'{label} window {i}', um + du, base + 1.0, .9, 1.2) for i, du in enumerate((-1.6, 1.6))]
    f.wall(f'{label} facade', lo, hi - EPS, 0.0, base + h, depth=T, role='wall', holes=hs)
    m = Merge(f)
    for hh in hs:
        if hh.get('kind') == 'door':
            m.box('blue', hh['u'], .16, hh['z'] + hh['h'] / 2, hh['w'] - .02, .05, hh['h'] - .02)
            m.box('glass', hh['u'], .125, hh['z'] + 1.55, .5, .02, .7)
            register(f, hh, .14, 'house door', 'house')
        else:
            framed(m, f, hh, cols=2, rows=2, inset=.12, occupied='house', frame='blue')
    m.box('white', um, T / 2 - .02, base + h + .1, hi - lo, T + .1, .2)
    m.flush(label)
    C.box(f'{label} body', ((bx0 + bx1) / 2, (ya + yb) / 2, (base + h) / 2), (bx1 - bx0, yb - ya, base + h), 'white', 'houses', 0)
    C.box(f'{label} roof', ((bx0 + bx1) / 2, (ya + yb) / 2, base + h + .08), (bx1 - bx0, yb - ya - .04, .16), 'roof', 'houses', 0)
    C.qa_room_light(f'{label} room', ((x_face + bx0) / 2 if facing > 0 else (x_face + bx1) / 2, (ya + yb) / 2, base + 1.6), 25, 1.6)


def edges():
    for k in range(1, NT):                                                     # west houses on the terrace levels
        house(f'west house {k}', X0, yk(k), yk(k + 1), lv(k + 1), 3.6 + .5 * (k % 2), 1)
    for k in range(NT):                                                        # east houses along the side stair
        house(f'east house {k}', X1, yk(k), yk(k + 1), lv(k + 1), 3.4 + .6 * ((k + 1) % 2), -1, door=False)
    C.box('West corner house', (X0 - 3.5, (yk(0) + yk(1)) / 2, 2.2), (7.0, TL - .04, 4.4), 'white', 'houses', 0)
    b = Batch()
    b.box('blue', X0 - 2.2, yk(0) - .03, 1.1, 1.0, .06, 2.2)
    b.box('blue', X0 - 5.0, yk(0) - .03, 1.7, 1.1, .06, 1.2)
    b.box('glass', X0 - 5.0, yk(0) - .05, 1.7, .9, .03, 1.0)
    for i in range(10):                                                        # a blue balcony rail on one east house
        b.box('blue', X1 - .35, yk(5) + 2.2 + i * .22, lv(6) + 2.9, .03, .03, .9)
    b.box('blue', X1 - .35, yk(5) + 3.2, lv(6) + 3.35, .05, 2.2, .05)
    b.box('white', X1 - .4, yk(5) + 3.2, lv(6) + 2.42, .9, 2.4, .1)
    for i in range(6):                                                         # timber pergola on another
        b.box('timber', X1 - 1.2, yk(3) + 1.2 + i * .8, lv(4) + 3.1, 2.4, .12, .12)
    for s in (0, 1):
        b.box('timber', X1 - 2.3, yk(3) + .9 + s * 3.5, lv(4) + 1.55, .12, .12, 3.1)
    b.flush('house details')
    # Bougainvillea over the second-terrace house and the lower east parapet.
    for i, (dy, dz, r) in enumerate(((1.2, 3.9, 1.3), (2.6, 4.3, 1.1), (3.6, 3.4, .9), (.4, 2.6, .8), (4.6, 4.6, .9))):
        A.foliage(f'Bougainvillea {i}', (X0 - .1, yk(1) + dy, lv(2) + dz), (.6, r, .7 * r), role='bougain')
    for i, (y, z) in enumerate(((yk(1) + 2.0, lv(2) + 1.2), (yk(1) + 3.2, lv(2) + 1.8))):
        A.foliage(f'Parapet bougainvillea {i}', (EP + .3, y, z), (.6, .9, .9), role='bougain')
    # The chapel at the top, west, and the belfry at the foot, east.
    cx, cy, base = -6.0, Y1 + 3.0, lv(NT)
    C.box('Chapel nave', (cx, cy, base + 2.2), (6.0, 4.0, 4.4), 'white', 'chapel', 0)
    b = Batch()
    cyl8(b, 'white', cx, cy, base + 4.4, base + 5.6, 1.9, 16)
    b.box('blue', cx, cy - 2.02, base + 1.1, 1.1, .05, 2.2)
    for s in (-1, 1):
        b.box('blue', cx + s * 1.8, cy - 2.02, base + 2.6, .6, .05, 1.0)
    b.box('white', cx, cy, base + 7.95, .12, .12, .7)
    b.box('white', cx, cy, base + 8.05, .45, .12, .1)
    b.flush('chapel')
    dome('Chapel dome', cx, cy, base + 5.6, 2.05, 2.2, [(1, 0), (.96, .3), (.8, .62), (.5, .88), (0, 1)], 'dome', 'chapel')
    bx, by = X1 + 3.0, Y0 - 4.0
    C.box('Belfry base', (bx, by, 2.5), (3.0, 3.0, 5.0), 'white', 'belfry', 0)
    b = Batch()
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.box('white', bx + sx * 1.15, by + sy * 1.15, 6.1, .7, .7, 2.2)
    b.box('white', bx, by, 7.4, 3.0, 3.0, .4)
    b.box('hardware', bx, by, 6.3, .6, .6, .7)
    b.box('blue', bx, by - 1.52, 2.0, 1.0, .05, 2.0)
    b.box('white', bx, by, 8.85, .1, .1, .7)
    b.box('white', bx, by, 9.0, .4, .1, .1)
    b.flush('belfry')
    dome('Belfry cupola', bx, by, 7.6, 1.3, 1.1, [(1, 0), (.9, .4), (.6, .78), (0, 1)], 'dome', 'belfry')
    # Backdrop: white houses beyond the top landing.
    for i, (x0, x1, h) in enumerate(((-10.0, -1.0, 4.0), (0.0, 4.5, 5.2), (4.5, 10.0, 4.4))):
        if i == 0:
            continue
        C.box(f'Top house {i}', ((x0 + x1) / 2, Y1 + 8.5, (lv(NT) + h) / 2), (x1 - x0 - .04, 7.0, lv(NT) + h), 'white', 'houses', 0)


def build():
    plaza_strip()
    edges()
    C.CONTACTS.append(dict(name='Cycladic stair-plaza climbing north between white houses', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(35, -45, 45), fill=(-40, -25, 30), rear=(-20, 40, 30), target=(0, 0, 4.0), gain=3.2)
