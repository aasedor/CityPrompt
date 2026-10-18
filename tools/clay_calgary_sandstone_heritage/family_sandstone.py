"""Calgary sandstone heritage block, authored from the locked catalogue views of
calgary_sandstone_heritage / variant_0 (sandstone_romanesque_revival).

Read from the pixels (the top view governs the plan): a Richardsonian Romanesque civic block of rock-faced
buff sandstone round a square light court, on a city block with streets on all four sides. Four storeys over a
rusticated basement; corner pavilions that step forward of the wings and rise into steep slate pyramids, each
with a coped gable and pinnacles on its outward faces; steep slate hipped roofs over the wings. Small square
basement windows, paired rectangular first-floor windows, tall round-arched windows on the second floor and
arcades of small arches on the third, all with deep reveals and stone string courses. A deep round-arched
portal in the south-west pavilion. At the middle of the east front a square clock tower projects from the wing,
with tall lancets, clock faces on four sides, a belfry arcade, round corner turrets with copper caps and a tall
copper spire. Sidewalks, streets and trees round the block.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-calgary-sandstone-heritage'
H = 22.0                                        # half-size of the main wall planes
PP = .8                                         # pavilion projection
PW = 12.0                                       # pavilion width
X0, X1, Y0, Y1 = -H - PP, H + PP, -H - PP, H + PP
T = .6
BASE, F1, F2, F3 = 2.0, 2.0, 6.0, 10.4          # basement top; floor lines
EAVE = 15.0
RIDGE = 21.5
CX0, CX1, CY0, CY1 = -7.0, 7.0, -5.0, 8.0      # light court
TX0, TX1, TY0, TY1 = 17.0, 25.0, -4.0, 4.0     # clock tower, projecting 3 m from the east wing
TTOP, SPIRE = 26.0, 36.5
EPS = .002
PALETTE = dict(wall=(.54, .42, .25), joint=(.40, .31, .19), stone=(.63, .52, .34), arch=(.61, .50, .32),
    trim=(.20, .18, .16), frame=(.20, .18, .16), pale=(.88, .86, .82), roof=(.34, .35, .38), copper=(.64, .38, .28),
    sand=(.66, .60, .50), foundation=(.52, .42, .28), glass=(.20, .22, .24), hardware=(.07, .07, .08),
    interior=(.82, .78, .70), floor=(.56, .46, .36), timber=(.42, .30, .20), clock=(.93, .91, .86),
    planting=(.30, .44, .20), soil=(.22, .16, .10), concrete=(.70, .69, .66), white=(.95, .95, .93),
    asphalt=(.28, .28, .29), blue=(.20, .30, .40), pot=(.60, .34, .22), brick=(.55, .40, .26))


def manifest(version):
    h = SPIRE + .8
    cams = G.camera_roster(X1 - X0 + 3.0, Y1 - Y0 + 3.0, h, [
        ('facade_close', (-4.0, -60.0, 9.0), (-4.0, Y0, 9.0), 45),
        ('architecture_close', (36.0, -40.0, 20.0), (H, -H, 18.0), 45),
        ('glass_close', (-6.3, -36.0, 8.5), (-6.3, -H, 8.5), 45),
        ('clock_tower', (54.0, -14.0, 24.0), (TX1, 0.0, 26.0), 40),
        ('portal_arch', (-12.0, -40.0, 3.0), (-16.8, Y0, 3.0), 40),
        ('gables_pinnacles', (30.0, -46.0, 24.0), (16.8, Y0, 19.0), 40),
        ('east_side', (80.0, 0.0, 12.0), (X1, 0.0, 12.0), 45),
        ('roofs_court', (-30.0, -40.0, 60.0), (0.0, 2.0, 16.0), 40),
        ('interior', (-4.0, -H + 5.0, F2 + 1.6), (-10.0, -H, F2 + 2.0), 40),
        ('rear_north', (0.0, 80.0, 14.0), (0.0, Y1, 14.0), 45)])
    for c in cams:                       # the locked front and oblique look from the south-east
        if c['name'] == 'front':
            c['location'] = (36.0, -52.0, 1.6); c['target'] = (8.0, -16.0, 15.0); c['lens'] = 26; c['whole'] = False
        elif c['name'] == 'front_corner':
            lx, ly, lz = c['location']; c['location'] = (-lx, ly, lz)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='calgary_sandstone_heritage/variant_0 (sandstone_romanesque_revival)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=4, storey_programme='rusticated basement and four storeys of offices round a light court',
            plan='45.6 m square block round a 14 x 13 m light court (top view), corner pavilions stepping 0.8 m forward, a clock tower projecting from the middle of the east wing',
            facade='rock-faced buff sandstone; paired first-floor windows; round-arched second-floor windows; third-floor arcades; coped gables with pinnacles; deep arched portal',
            levels_m=[BASE, F2, F3, EAVE], roof_m=dict(eave=EAVE, ridge=RIDGE, tower=TTOP, spire=SPIRE),
            inferred='interiors, the light court elevations and the north and west fronts follow the visible grammar'),
        roof_contract=dict(type='steep slate hipped roofs round the court, taller slate pyramids over the corner pavilions, copper tower spire and turret caps', datum_m=EAVE, crowns_m=[RIDGE, TTOP, SPIRE]),
        identity_contract=dict(owner='rock-faced sandstone Romanesque civic block with round-arched arcades, gabled corner pavilions under slate pyramids and a clock tower with a copper spire'),
        material_contract=dict(profile='source-palette clay: buff sandstone with dark joints and lighter dressings, grey slate, copper spire and caps, white clock faces, dark frames', textured_keeper=False),
        programme_contract=dict(storeys=5, basement='archives and plant', upper='council chamber and offices'),
        contact_contract=['Grade-zero sidewalks and streets', 'Sandstone walls from grade', 'Roofs on the eave cornices', 'Tower from grade through the east wing'],
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


# ---- Calgary sandstone heritage block ----

def arch_head(f, h, rise, ring=.26, segs=10, ring_role='arch', dep=None):
    """Segmental or round head on a rectangular cut: brick spandrel infill above the curve (set 1 cm back so it
    never shares a plane with the wall face) and a proud brick ring of headers over it."""
    u, w, top = h['u'], h['w'], h['z'] + h['h']
    R = (w * w / 4 + rise * rise) / (2 * rise)
    cz = top - R
    a0 = math.asin(min(1.0, (w / 2) / R))
    arc = [(u + R * math.sin(-a0 + 2 * a0 * i / segs), cz + R * math.cos(-a0 + 2 * a0 * i / segs)) for i in range(segs + 1)]
    pts = [(u - w / 2 - .06, top - rise)] + arc + [(u + w / 2 + .06, top - rise)]
    vs, fs = [], []
    for (pu, pz) in pts:
        for d in (.01, (dep or T) - .01):
            vs.append(f.p(pu, d, pz)); vs.append(f.p(pu, d, top + .06))
    for i in range(len(pts) - 1):
        a, b = 4 * i, 4 * (i + 1)
        fs += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3)]
    n = 4 * (len(pts) - 1)
    fs += [(0, 1, 3, 2), (n, n + 2, n + 3, n + 1)]
    C.mesh(f'{h["id"]} spandrel', vs, fs, 'wall', 'arches')
    vs, fs = [], []
    for (pu, pz) in arc:
        r = math.hypot(pu - u, pz - cz)
        nu, nz = (pu - u) / r, (pz - cz) / r
        for d in (-.035, .02):
            vs.append(f.p(pu, d, pz)); vs.append(f.p(pu + nu * ring, d, pz + nz * ring))
    for i in range(segs):
        a, b = 4 * i, 4 * (i + 1)
        fs += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3)]
    n = 4 * segs
    fs += [(0, 1, 3, 2), (n, n + 2, n + 3, n + 1)]
    C.mesh(f'{h["id"]} arch ring', vs, fs, ring_role, 'arches')




def cone(b, role, cx, cy, z0, z1, r, n=12):
    """Cone or n-sided pyramid added to a Batch."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for i in range(n):
        a = 2 * math.pi * (i + .5) / n
        V.append((cx + r * math.cos(a), cy + r * math.sin(a), z0))
    V.append((cx, cy, z1))
    F.append(tuple(o + i for i in range(n - 1, -1, -1)))
    for i in range(n):
        F.append((o + i, o + (i + 1) % n, o + n))


def cyl(b, role, cx, cy, z0, z1, r, n=12):
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


def disc(b, role, centre, normal, r, t=.08, n=24):
    """Flat disc standing proud of a wall along its horizontal outward normal (a clock face or its ring)."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    nx, ny = normal
    tx, ty = -ny, nx
    for d in (0.0, t):
        for i in range(n):
            a = 2 * math.pi * i / n
            V.append((centre[0] + nx * d + tx * r * math.cos(a), centre[1] + ny * d + ty * r * math.cos(a), centre[2] + r * math.sin(a)))
    F.append(tuple(o + i for i in range(n)))
    F.append(tuple(o + n + i for i in range(n - 1, -1, -1)))
    for i in range(n):
        j = (i + 1) % n
        F.append((o + i, o + j, o + n + j, o + n + i))


def window_set(m, f, h, kind):
    if kind == 'arch':
        framed(m, f, h, cols=2, rows=4, inset=.18, occupied='office', frame='frame')
        arch_head(f, h, h['w'] / 2, ring=.3)
        m.box('stone', h['u'], -.06, h['z'] - .07, h['w'] + .3, .16, .14)
    elif kind == 'pair':
        framed(m, f, h, cols=2, rows=3, inset=.18, occupied='office', frame='frame')
        m.box('stone', h['u'], .02, h['z'] + h['h'] / 2, .22, .3, h['h'])                     # stone mullion
        m.box('stone', h['u'], -.06, h['z'] - .07, h['w'] + .3, .16, .14)
        m.box('stone', h['u'], -.05, h['z'] + h['h'] + .2, h['w'] + .5, .12, .4)              # lintel
    else:
        framed(m, f, h, cols=2, rows=1, inset=.18, occupied='archive', frame='frame')


def segment(label, origin, tangent, inward, lo, hi, depth, bays, portal=None, ends=(0.0, 0.0)):
    """One straight run of the outer wall with its window tiers and string courses. ends: how far the bands run past
    lo and hi to reach the outer corner (a negative value means 'band depth', for the run that wraps the corner)."""
    f = C.Face(origin, tangent, inward, label)
    holes, kinds = [], []
    for u in bays:
        if portal is not None and abs(u - portal) < .1:
            holes.append(hole(f'{label} portal', u, 0.0, 3.4, 4.6, kind='door')); kinds.append('portal')
        else:
            holes.append(hole(f'{label} basement {u:+.1f}', u, .5, 1.0, .9)); kinds.append('base')
            holes.append(hole(f'{label} first {u:+.1f}', u, F1 + .7, 2.0, 2.3)); kinds.append('pair')
        holes.append(hole(f'{label} second {u:+.1f}', u, F2 + .6, 1.5, 3.4)); kinds.append('arch')
        for s in (-1, 1):
            holes.append(hole(f'{label} third {u + s * .62:+.1f}', u + s * .62, F3 + .7, .8, 2.3)); kinds.append('arch')
    f.wall(f'{label} carrier', lo, hi - EPS, 0.0, EAVE, depth=depth, role='wall', holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, .1, EAVE - .1, holes, spacing=.5)
    m = Merge(f)
    for z, hh, d in ((BASE - .1, .3, .2), (F2 + .35, .22, .14), (F3 + .3, .22, .14), (EAVE - .35, .7, .4)):
        a = lo - (d if ends[0] < 0 else ends[0])
        c = hi + (d if ends[1] < 0 else ends[1])
        runs = [(a, c)]
        if portal is not None and z < F2:
            runs = [(a, portal - 2.4), (portal + 2.4, c)]
        for ra, rc in runs:
            m.box('stone', (ra + rc) / 2, -d / 2, z, rc - ra, d, hh)
    for h, k in zip(holes, kinds):
        if k == 'portal':
            m.box('timber', h['u'], depth - .2, h['h'] / 2 - .4, h['w'] - .02, .1, h['h'] - .8)
            register(f, h, depth - .3, 'portal', 'entrance hall')
            arch_head(f, h, 1.7, ring=.6, dep=depth)
            for s in (-1, 1):
                m.box('stone', h['u'] + s * (h['w'] / 2 + .3), -.2, 1.6, .6, .4, 3.2)          # portal columns
        else:
            window_set(m, f, h, k)
    m.flush(label)
    return f


def gable(name, origin, tangent, inward, uc):
    """A coped gable on a pavilion face: the gable wall, coping beams, pinnacles, a stone-framed triplet in it."""
    f = C.Face(origin, tangent, inward, name)
    hw, rise = 4.6, 6.0
    p = lambda u, d, z: f.p(u, d, z)
    nx, ny = -inward[0], -inward[1]
    pts = []
    vs = [p(uc - hw, 0, EAVE), p(uc + hw, 0, EAVE), p(uc, 0, EAVE + rise), p(uc - hw, 1.0, EAVE), p(uc + hw, 1.0, EAVE), p(uc, 1.0, EAVE + rise)]
    C.mesh(f'{name} wall', vs, [(0, 1, 2), (3, 5, 4), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], 'wall', 'gables')
    b = Batch()
    for s in (-1, 1):
        b.beam('stone', p(uc + s * (hw + .1), .45, EAVE + .05), p(uc, .45, EAVE + rise + .1), 1.15 + .04 * (s > 0), .3, ext=.05)
        q = p(uc + s * (hw + .1), .45, 0)
        b.box('stone', q[0], q[1], EAVE + .5, .9, .9, 1.0)
        cone(b, 'stone', q[0], q[1], EAVE + 1.0, EAVE + 2.8, .35, 8)
    q = p(uc, .45, 0)
    b.box('stone', q[0], q[1], EAVE + rise + .5, .8, .8, 1.0)
    cone(b, 'stone', q[0], q[1], EAVE + rise + 1.0, EAVE + rise + 2.6, .32, 8)
    # Triplet of arched lights set in a proud stone frame (the gable is solid behind them).
    for du in (-.9, 0.0, .9):
        g = p(uc + du, -.05, 0)
        b.box('frame', g[0], g[1], EAVE + 1.85, .62 if inward[0] == 0 else .1, .1 if inward[0] == 0 else .62, 2.3)
        g = p(uc + du, -.1, 0)
        b.box('glass', g[0], g[1], EAVE + 1.85, .5 if inward[0] == 0 else .02, .02 if inward[0] == 0 else .5, 2.1)
    g = p(uc, -.08, 0)
    b.box('stone', g[0], g[1], EAVE + .62, 2.9 if inward[0] == 0 else .2, .2 if inward[0] == 0 else 2.9, .16)
    b.box('stone', g[0], g[1], EAVE + 3.15, 2.9 if inward[0] == 0 else .2, .2 if inward[0] == 0 else 2.9, .3)
    b.flush(name)
    # The cross roof behind the gable, running back into the pavilion pyramid.
    tri = [(uc - hw, EAVE + .1), (uc + hw, EAVE + .1), (uc, EAVE + rise + .1)]
    if inward[0] == 0:
        pts = [(f.p(u, 0, 0)[0], z) for u, z in tri]
        y0, y1 = sorted((f.p(0, .5, 0)[1], f.p(0, 5.0, 0)[1]))
        C.prism(f'{name} cross roof', pts, 'y', y0, y1, 'roof', 'roof')
    else:
        pts = [(f.p(u, 0, 0)[1], z) for u, z in tri]
        x0, x1 = sorted((f.p(0, .5, 0)[0], f.p(0, 5.0, 0)[0]))
        C.prism(f'{name} cross roof', pts, 'x', x0, x1, 'roof', 'roof')


FACES = [  # label, tangent, inward, main-plane origin fn, pavilion-plane origin fn
    ('south', (1, 0, 0), (0, 1, 0), lambda q: (0, -q, 0)),
    ('east', (0, 1, 0), (-1, 0, 0), lambda q: (q, 0, 0)),
    ('north', (-1, 0, 0), (0, -1, 0), lambda q: (0, q, 0)),
    ('west', (0, -1, 0), (1, 0, 0), lambda q: (-q, 0, 0))]


def outer_walls():
    pc = H - PW / 2 + PP / 2                                                       # pavilion centre offset along a face
    for label, t, n, org in FACES:
        wraps = label in ('south', 'north')
        plo = -(H + PP) if wraps else -(H + PP) + T + PP
        corner = -1.0 if wraps else T + PP
        for side, (a, c) in (('w', (plo, -H + PW - PP / 2)), ('e', (H - PW + PP / 2, -plo))):
            uc = -pc if side == 'w' else pc
            portal = uc if (label == 'south' and side == 'w') else None
            segment(f'{label} pavilion {side}', org(H + PP), t, n, a, c, T + PP, [uc - 3.6, uc, uc + 3.6], portal=portal,
                    ends=(corner, 0.0) if side == 'w' else (0.0, corner))
            gable(f'{label} gable {side}', org(H + PP), t, n, uc)
        lo, hi = -H + PW - PP / 2, H - PW + PP / 2
        if label == 'east':
            segment('east wing south', org(H), t, n, lo, TY0, T, [-8.4, -5.6])
            segment('east wing north', org(H), t, n, TY1, hi, T, [5.6, 8.4])
        else:
            segment(f'{label} wing', org(H), t, n, lo, hi, T, [-8.4, -4.2, 0.0, 4.2, 8.4])


def court():
    for label, o, t, n, lo, hi in (('court south', (0, CY0, 0), (-1, 0, 0), (0, -1, 0), -CX1 - .5, -CX0 + .5),
                                   ('court north', (0, CY1, 0), (1, 0, 0), (0, 1, 0), CX0 - .5, CX1 + .5),
                                   ('court west', (CX0, 0, 0), (0, 1, 0), (-1, 0, 0), CY0, CY1),
                                   ('court east', (CX1, 0, 0), (0, -1, 0), (1, 0, 0), -CY1, -CY0)):
        f = C.Face(o, t, n, label)
        k = max(1, int((hi - lo) / 3.0))
        hs = [hole(f'{label} {j} f{i}', lo + (hi - lo) * (j + .5) / k, z, 1.1, 2.0) for j in range(k) for i, z in enumerate((F1 + .7, F2 + .8, F3 + .8))]
        f.wall(f'{label} wall', lo, hi - EPS, 0.0, EAVE, depth=.5, role='wall', holes=hs)
        m = Merge(f)
        for h in hs:
            framed(m, f, h, cols=2, rows=3, inset=.16, occupied='office', frame='frame', lite=True)
        m.flush(label)
    C.box('Court paving', ((CX0 + CX1) / 2, (CY0 + CY1) / 2, .02), (CX1 - CX0, CY1 - CY0, .04), 'concrete', 'court', 0)


def roofs():
    ov = .45
    ridge = [(-14.5, -13.5), (14.5, -13.5), (14.5, 15.0), (-14.5, 15.0)]
    outer = [(-H - ov, -H - ov), (H + ov, -H - ov), (H + ov, H + ov), (-H - ov, H + ov)]
    inner = [(CX0 + ov, CY0 + ov), (CX1 - ov, CY0 + ov), (CX1 - ov, CY1 - ov), (CX0 + ov, CY1 - ov)]
    strip('Wing roofs outer', outer, ridge, EAVE - ov * .8, RIDGE, 'roof', 'roof')
    strip('Wing roofs inner', inner, ridge, EAVE - ov * .8, RIDGE, 'roof', 'roof')
    pcs = H + PP / 2 - PW / 2
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * pcs, sy * pcs
            r = PW / 2 + .45
            strip(f'Pavilion pyramid {sx:+d}{sy:+d}', [(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r), (cx - r, cy + r)],
                  [(cx - .4, cy - .4), (cx + .4, cy - .4), (cx + .4, cy + .4), (cx - .4, cy + .4)], EAVE - .3, EAVE + 9.5, 'roof', 'roof')
            b = Batch()
            b.box('copper', cx, cy, EAVE + 9.55, .9, .9, .2)
            cone(b, 'copper', cx, cy, EAVE + 9.65, EAVE + 11.0, .3, 8)
            b.flush(f'finial {sx:+d}{sy:+d}')
    for z in (BASE, F2, F3):
        for name, cx, cy, sx, sy in (('south', 0, (-H + T + CY0) / 2, 2 * H - 2 * T, CY0 + H - T), ('north', 0, (CY1 + H - T) / 2, 2 * H - 2 * T, H - T - CY1),
                                     ('west', (-H + T + CX0) / 2, (CY0 + CY1) / 2, CX0 + H - T, CY1 - CY0), ('east', (CX1 + H - T) / 2, (CY0 + CY1) / 2, H - T - CX1, CY1 - CY0)):
            C.box(f'Floor {name} {z:.0f}', (cx, cy, z - .14), (sx - .02, sy - .02, .24), 'floor', 'inside', 0)
    for x, y in ((-14.0, -H + 3.0), (0.0, -H + 3.0), (14.0, -H + 3.0), (H - 3.0, -10.0), (H - 3.0, 10.0), (-H + 3.0, 0.0)):
        for z in (BASE, F2, F3):
            C.qa_room_light(f'Room {x:+.0f} {y:+.0f} {z:.0f}', (x, y, z + 2.3), 70, 3.0)
    C.CONTACTS.append(dict(name='Sandstone walls from grade; roofs on the eave cornices; tower from grade through the east wing', eave_m=EAVE))


def tower():
    xc = (TX0 + TX1) / 2
    walls = (('tower east', (TX1, 0, 0), (0, 1, 0), (-1, 0, 0), TY0, TY1, 0.0, 0.0),
             ('tower south', (0, TY0, 0), (1, 0, 0), (0, 1, 0), TX0, TX1 - .8, 0.0, xc),
             ('tower north', (0, TY1, 0), (-1, 0, 0), (0, -1, 0), -(TX1 - .8), -TX0, 0.0, -xc),
             ('tower west', (TX0, 0, 0), (0, -1, 0), (1, 0, 0), -(TY1 - .8), -(TY0 + .8), EAVE, 0.0))
    b = Batch()
    for label, o, t, n, lo, hi, z0, uc in walls:
        f = C.Face(o, t, n, label)
        hs = [hole(f'{label} belfry {s:+d}', uc + s * 1.35, 23.0, .75, 1.9) for s in (-1, 0, 1)]
        if label == 'tower east':
            hs += [hole('tower portal', uc, 0.0, 3.0, 4.2, kind='door'), hole('tower window 1', uc, 7.0, 1.3, 2.8),
                   hole('tower window 2', uc, 11.0, 1.1, 2.4)] + [hole(f'tower lancet {s:+d}', uc + s * .75, 14.8, .75, 3.8) for s in (-1, 1)]
        f.wall(f'{label} wall', lo, hi - EPS, z0, TTOP, depth=.8, role='wall', holes=hs)
        G.brick_courses(f, lo + .02, hi - .02, z0 + .1, TTOP - .1, hs, spacing=.5)
        m = Merge(f)
        for h in hs:
            if h.get('kind') == 'door':
                m.box('timber', h['u'], .6, h['h'] / 2 - .3, h['w'] - .02, .1, h['h'] - .6)
                register(f, h, .5, 'tower portal', 'tower hall')
                arch_head(f, h, 1.5, ring=.5, dep=.8)
            else:
                framed(m, f, h, cols=2 if h['w'] > 1 else 1, rows=4, inset=.18, occupied='tower', frame='frame')
                arch_head(f, h, h['w'] / 2, ring=.22, dep=.8)
        m.box('stone', (lo + hi) / 2, -.12, TTOP - .3, hi - lo, .24, .6)                         # crown cornice
        m.box('stone', (lo + hi) / 2, -.1, 19.5, hi - lo, .2, .3)                                # clock-stage string course
        m.flush(label)
        out = (-n[0], -n[1])
        disc(b, 'stone', f.p(uc, 0.0, 21.4), out, 1.35, .06)
        disc(b, 'clock', f.p(uc, -.06, 21.4), out, 1.15, .06)
        for ang, r in ((math.radians(60), .9), (math.radians(-30), .65)):                         # hands
            b.beam('hardware', f.p(uc, -.15, 21.4), f.p(uc + r * math.cos(ang), -.15, 21.4 + r * math.sin(ang)), .06, .03)
    for x in (TX0, TX1):                                                                         # corner turrets with copper caps
        for y in (TY0, TY1):
            cyl(b, 'wall', x, y, 19.0, TTOP + .8, .75, 14)
            b.box('stone', x, y, 18.8, 1.2, 1.2, .4)
            cyl(b, 'stone', x, y, TTOP + .8, TTOP + 1.05, .9, 14)
            cone(b, 'copper', x, y, TTOP + 1.05, TTOP + 4.6, .9, 14)
    cone(b, 'copper', xc, 0.0, TTOP + .2, SPIRE, 4.6, 8)
    b.box('stone', xc, 0.0, TTOP + .05, 8.9, 8.9, .3)
    b.flush('tower crown')


def site():
    for name, cx, cy, sx, sy in (('South sidewalk', 0, Y0 - 3.0, 2 * X1 + 12.0, 6.0), ('North sidewalk', 0, Y1 + 3.0, 2 * X1 + 12.0, 6.0),
                                 ('East sidewalk', X1 + 3.0, 0, 6.0, 2 * Y1), ('West sidewalk', X0 - 3.0, 0, 6.0, 2 * Y1)):
        C.box(name, (cx, cy, .06), (sx, sy, .12), 'concrete', 'site', 0)
    for name, cx, cy, sx, sy in (('South street', 0, Y0 - 12.0, 2 * X1 + 36.0, 12.0), ('North street', 0, Y1 + 12.0, 2 * X1 + 36.0, 12.0),
                                 ('East street', X1 + 12.0, 0, 12.0, 2 * Y1 + 12.0), ('West street', X0 - 12.0, 0, 12.0, 2 * Y1 + 12.0)):
        C.box(name, (cx, cy, .01), (sx, sy, .02), 'asphalt', 'site', 0)
    b = Batch()
    for k in range(-22, 23):
        b.box('joint', k * 2.0, Y0 - 3.0, .121, .02, 5.98, .004)
    b.flush('sidewalk joints')
    for x in (-28.0, -14.0, 3.0, 26.0):
        street_tree(x, Y0 - 4.2, z=.12, height=10.0, spread=2.8)
    for y in (-18.0, 14.0):
        street_tree(X1 + 4.2, y, z=.12, height=10.0, spread=2.8)


def build():
    site()
    outer_walls()
    court()
    roofs()
    tower()
    C.CONTACTS.append(dict(name='Romanesque sandstone civic block with a clock tower on a city block', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(35, -45, 50), fill=(-45, -25, 35), rear=(-20, 40, 35), target=(0, 0, 12.0), gain=4.0)
