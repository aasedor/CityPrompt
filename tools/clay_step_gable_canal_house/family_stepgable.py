"""Amsterdam step-gable canal house, authored from the locked catalogue views of
amsterdam_step_gable_house / variant_0 (step_gable_gothic).

Read from the pixels (the top view governs the plan): a narrow, deep four-storey house of dark red-brown brick
on a canal-side street, its stepped (crow-stepped) gable facing the street, a side alley to the east. Three
bays of white-framed small-paned sash windows on each upper floor, a single window in the gable, a panelled
door up a short stone stoop, iron wall anchors at the floor lines, a steep dark tiled roof with its ridge
running back from the street, a brick chimney on the east slope. Plain brick side walls with a few small
windows. A tree and a black lamp standard on the brick-paved street.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-step-gable-canal-house'
X0, X1, Y0, Y1 = -3.3, 3.3, -6.0, 6.0          # 6.6 m wide, 12 m deep
T = .36
G0 = .15
Z1 = .9                                         # raised ground floor up the stoop, over a half-basement
F1 = 5.1                                        # first floor
FH = 3.6
EAVE = F1 + 2 * FH                              # top of the side walls, foot of the stepped gable
STEPS = 4                                       # crow steps each side above the first gable tier
TIER0 = 1.6                                     # first gable tier (holds the gable window)
STEP_H, STEP_RUN = 1.0, .62
EPS = .002
PALETTE = dict(wall=(.31, .15, .10), joint=(.56, .48, .42), band=(.27, .13, .09), trim=(.95, .95, .93), pale=(.88, .88, .86),
    stone=(.80, .78, .72), roof=(.10, .10, .11), sand=(.62, .52, .44), foundation=(.36, .30, .27),
    glass=(.26, .30, .33), hardware=(.08, .08, .09), interior=(.84, .78, .70), floor=(.58, .48, .38),
    timber=(.46, .32, .20), blue=(.20, .30, .40), planting=(.32, .46, .20), soil=(.22, .16, .10),
    concrete=(.66, .64, .60), white=(.96, .96, .95), asphalt=(.30, .30, .31), door=(.22, .10, .06),
    brick=(.55, .32, .24), pot=(.62, .34, .22), setts=(.48, .40, .36), paving=(.60, .52, .46))


def manifest(version):
    h = EAVE + TIER0 + STEPS * STEP_H + 1.0
    cams = G.camera_roster(X1 - X0 + 3.0, Y1 - Y0 + 3.0, h, [
        ('facade_close', (0.0, -20.0, 8.0), (0.0, Y0, 8.0), 45),
        ('architecture_close', (8.0, -14.0, 14.0), (X1, Y0, 13.5), 45),
        ('glass_close', (0.0, Y0 - 5.0, F1 + 1.6), (0.0, Y0, F1 + 1.6), 45),
        ('stepped_gable', (2.0, -19.0, EAVE + 3.0), (0.0, Y0, EAVE + 3.0), 40),
        ('entrance_stoop', (2.0, Y0 - 7.5, 2.0), (0.0, Y0, 2.3), 35),
        ('wall_anchors', (6.0, -9.0, F1 + 1.0), (1.0, Y0, F1 + .5), 45),
        ('east_side', (15.0, -1.0, 7.0), (X1, 0.0, 7.0), 45),
        ('roof_chimney', (-9.0, -12.0, 24.0), (0.5, 0.0, EAVE + 3.0), 40),
        ('interior', (2.0, 4.0, F1 + 1.6), (-.6, Y0, F1 + 1.6), 40),
        ('rear_north', (0.0, 22.0, 9.0), (0.0, Y1, 9.0), 45)])
    for c in cams:                       # the locked front and oblique look from the south-east
        if c['name'] == 'front':
            c['location'] = (11.0, -24.0, 1.6); c['target'] = (-.6, -6.0, 9.0); c['lens'] = 26; c['whole'] = False
        elif c['name'] == 'front_corner':                                      # the locked oblique: close and high from the south-east
            c.update(location=(17.0, -27.0, 21.0), target=(0.0, -2.0, 8.0), lens=35, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(12.0, -19.0, 32.0), target=(0.0, 0.0, 8.0), lens=35, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='amsterdam_step_gable_house/variant_0 (step_gable_gothic)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=4, storey_programme='raised ground floor over a half-basement, two upper floors, a gable attic',
            plan='6.6 x 12 m narrow-front house (top view), ridge running back from the street, alley east',
            facade='dark red-brown brick; a door between two tall ground windows; two floors of three white small-paned sashes; a crow-stepped gable with one window; iron anchors; a stoop to the door',
            levels_m=[G0, Z1, F1, F1 + FH, EAVE], gable_m=dict(foot=EAVE, steps=STEPS + 1),
            inferred='interiors and the rear are teaching assumptions; the rear gable repeats the front grammar'),
        roof_contract=dict(type='steep dark tiled roof between stepped gables, a brick chimney on the east slope', datum_m=EAVE, crowns_m=[EAVE + TIER0 + STEPS * STEP_H]),
        identity_contract=dict(owner='narrow dark-brick canal house with a crow-stepped street gable, white small-paned sashes, wall anchors and a stoop'),
        material_contract=dict(profile='source-palette clay: dark red-brown brick with pale joints, white sash frames, stone stoop and step copings, black anchors and lamp, dark roof tiles', textured_keeper=False),
        programme_contract=dict(storeys=4, ground='hall and front room up the stoop', upper='rooms', attic='store under the gable'),
        contact_contract=['Grade-zero brick paving and stoop', 'Brick walls from grade', 'Stepped gable on the front wall', 'Roof between the gables'],
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


# ---- Amsterdam step-gable canal house ----

def brick_bond(f, lo, hi, z0, z1, holes, course=.1, brick=.25):
    """Pale mortar: bed joints every course and staggered head joints, both cut round the openings."""
    G.brick_courses(f, lo, hi, z0, z1, holes, spacing=course)
    vs, fs = [], []
    for row in range(int((z1 - z0) / course)):
        zb = z0 + row * course
        off = (brick / 2) * (row % 2)
        u = lo + off + brick
        while u < hi - .02:
            if not any(h['u'] - h['w'] / 2 - .02 < u < h['u'] + h['w'] / 2 + .02 and h['z'] - .02 < zb + course < h['z'] + h['h'] + .4 for h in holes):
                o = len(vs)
                vs += [f.p(u - .004, -.002, zb), f.p(u + .004, -.002, zb), f.p(u + .004, -.002, zb + course), f.p(u - .004, -.002, zb + course)]
                fs.append((o, o + 1, o + 2, o + 3))
            u += brick
    if fs:
        C.mesh(f.label + ' head joints', vs, fs, 'joint', 'brick joints')


def gable_tiers():
    """(z0, z1, half-width) of each gable tier above the eaves: a full-width first tier, then the crow steps."""
    hw = (X1 - X0) / 2
    tiers = [(EAVE, EAVE + TIER0, hw)]
    for k in range(STEPS):
        z0 = EAVE + TIER0 + k * STEP_H
        tiers.append((z0, z0 + STEP_H, hw - STEP_RUN * (k + 1.5)))
    return tiers


def anchors(m, us, z):
    """Vertical wrought-iron wall anchors with a short cross pin."""
    for u in us:
        m.box('hardware', u, -.03, z, .07, .04, .55)


def slope_plate(name, a, c, y0, y1, t=.18, role='roof', module='roof'):
    """A closed sloped roof plate from eave point a to ridge point c (x, z), between y0 and y1; ends are thin faces."""
    vs = []
    for (x, z) in (a, c):
        for y in (y0, y1):
            vs += [(x, y, z), (x, y, z - t)]
    # 0:a y0 top 1:a y0 bot 2:a y1 top 3:a y1 bot 4:c y0 top 5:c y0 bot 6:c y1 top 7:c y1 bot
    fs = [(0, 2, 6, 4), (1, 5, 7, 3), (0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6)]
    return C.mesh(name, vs, fs, role, module)


def gable(f, front=True):
    """Crow-stepped gable on a street face: brick tiers, stone copings on each step, the gable window."""
    tiers = gable_tiers()
    for k, (z0, z1, hw) in enumerate(tiers):
        holes = [hole(f'{f.label} gable window', 0.0, z0 + .2, 1.0, 1.3)] if k == 0 else []
        f.wall(f'{f.label} gable tier {k}', -hw, hw - EPS, z0, z1, depth=T, role='wall', holes=holes)
        brick_bond(f, -hw + .02, hw - .02, z0 + .02, z1 - .02, holes)
        m = Merge(f)
        if holes:
            framed(m, f, holes[0], cols=2, rows=3, inset=.12, occupied='attic', lite=not front)
            m.box('stone', 0.0, -.04, z0 + .14, 1.14, .14, .1)
        for s in (-1, 1):                                                      # stone coping on each step
            m.box('stone', s * (hw - .22), (T - .1) / 2 - .05, z1 + .06, .48 + (.08 * (k % 2)), T + .1 + .02 * (k % 2), .12)
        m.flush(f'{f.label} gable {k}')
    zt = tiers[-1][1]
    C.box(f'{f.label} gable pinnacle', (f.p(0, T / 2, zt + .45)), (.7, T, .9), 'wall', 'gable', 0)
    C.box(f'{f.label} pinnacle cap', (f.p(0, T / 2, zt + .96)), (.86, T + .12, .12), 'stone', 'gable', 0)


def south_face():
    f = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south')
    door = hole('front door', 0.0, Z1, 1.0, 2.35, kind='door')
    transom = hole('door transom', 0.0, Z1 + 2.47, 1.0, .6)
    gw = [hole(f'ground window {s:+d}', s * 1.95, Z1 + .55, 1.05, 2.9) for s in (-1, 1)]
    base = [hole(f'basement window {s:+d}', s * 1.95, .1, .8, .5) for s in (-1, 1)]
    ups = [hole(f'sash f{k} {i}', u, F1 + k * FH + .5, 1.0, 2.25) for k in range(2) for i, u in enumerate((-2.0, 0.0, 2.0))]
    holes = [door, transom] + gw + base + ups
    f.wall('south carrier', X0, X1 - EPS, 0.0, EAVE, depth=T, role='wall', holes=holes)
    brick_bond(f, X0 + .02, X1 - .02, .7, EAVE - .02, holes)
    m = Merge(f)
    m.box('foundation', 0, -.03, .05, X1 - X0 - .02, .06, .1)
    for z in (F1 - .2, F1 + FH - .2):                                        # brick string courses at the floor lines
        m.box('band', 0, -.03, z, X1 - X0 + .02, .06, .18)
    for h in gw:
        framed(m, f, h, cols=3, rows=6, inset=.12, occupied='room')
        m.box('trim', h['u'], .1, h['z'] + h['h'] * .62, h['w'] - .1, .1, .08)
        m.box('stone', h['u'], -.04, h['z'] - .06, h['w'] + .12, .12, .1)
    for h in ups:
        framed(m, f, h, cols=3, rows=4, inset=.12, occupied='room')
        m.box('trim', h['u'], .1, h['z'] + h['h'] / 2, h['w'] - .1, .1, .08)
        m.box('stone', h['u'], -.04, h['z'] - .06, h['w'] + .12, .12, .1)
    for h in base:
        framed(m, f, h, cols=2, rows=1, inset=.12, occupied='basement')
    # Dark mahogany panelled door, diamond-glazed transom, white surround.
    m.box('door', door['u'], .16, door['z'] + door['h'] / 2, door['w'] - .02, .06, door['h'] - .02)
    for zz in (.35, 1.0, 1.7):
        for s in (-1, 1):
            m.box('door', door['u'] + s * .22, .125, door['z'] + zz + .2, .32, .012, .5)
    m.box('hardware', door['u'] + .3, .12, door['z'] + 1.05, .05, .03, .05)
    register(f, door, .14, 'entry door', 'hall')
    framed(m, f, transom, cols=1, rows=1, inset=.12, occupied='hall')
    tz, th = transom['z'] + .07, transom['h'] - .14
    b = Batch()
    for a, c in (((-.43, 0), (0, .5)), ((0, .5), (.43, 0)), ((.43, 0), (0, -.5)), ((0, -.5), (-.43, 0))):
        p0 = f.p(a[0], .1, tz + th / 2 + a[1] * th)
        p1 = f.p(c[0], .1, tz + th / 2 + c[1] * th)
        b.beam('white', p0, p1, .035, .035)
    b.flush('transom diamond')
    for s in (-1, 1):                                                          # white door surround
        m.box('white', door['u'] + s * (door['w'] / 2 + .08), -.04, Z1 + 1.55, .16, .1, 3.1)
    m.box('white', door['u'], -.06, Z1 + 3.18, door['w'] + .5, .14, .16)
    for z in (F1 - .55, F1 + FH - .55, EAVE - .45):
        anchors(m, (-2.95, -1.0, 1.0, 2.95), z)
    m.flush('south')
    gable(f)
    # Stone stoop: steps that butt (no overlapping solids), a landing at the door, iron rails with newels.
    b = Batch()
    n = 4
    rise = Z1 / (n + 1)
    run = .32
    land = .6
    b.box('stone', door['u'], Y0 - land / 2, Z1 / 2, 1.9, land, Z1)
    for k in range(n):
        y_hi = Y0 - land - k * run
        top = Z1 - rise * (k + 1)
        b.box('stone', door['u'], y_hi - run / 2, top / 2, 1.9, run, top)
    y_foot = Y0 - land - n * run
    for s in (-1, 1):
        x = door['u'] + s * .9
        b.box('hardware', x, y_foot + .1, .5, .06, .06, 1.0)                   # newel at the foot
        b.box('hardware', x, Y0 - .1, (Z1 + Z1 + .95) / 2, .06, .06, .95)        # post at the wall
        b.beam('hardware', (x, y_foot + .1, 1.0), (x, Y0 - .05, Z1 + .95), .05, .05)
        b.beam('hardware', (x, y_foot + .1, .55), (x, Y0 - .05, Z1 + .5), .03, .03)
    b.flush('stoop')


def side_and_rear():
    hd = (Y1 - Y0) / 2
    e = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    hs = [hole(f'east window f{k}', 1.4, F1 + k * FH + .9, .7, 1.1) for k in range(2)] + \
         [hole(f'east ground window {i}', u, Z1 + .7, .85, 2.5) for i, u in enumerate((1.4, 3.8))] + [hole('east vent', 3.8, .12, .5, .35)]
    e.wall('east carrier', -hd + T, hd - T, 0.0, EAVE, depth=T, role='wall', holes=hs)
    brick_bond(e, -hd + T + .02, hd - T - .02, .7, EAVE - .02, hs)
    m = Merge(e)
    m.box('foundation', 0, -.03, .05, 2 * hd - 2 * T - .02, .06, .1)
    for h in hs:
        framed(m, e, h, cols=2, rows=1 if h['h'] < .5 else (4 if h['h'] > 2 else 2), inset=.12, occupied='room')
        if h['h'] > .5:
            m.box('stone', h['u'], -.04, h['z'] - .06, h['w'] + .12, .12, .1)
    for z in (F1 - .55, F1 + FH - .55, EAVE - .45):
        anchors(m, (-4.5, -1.5, 2.6, 5.2), z)
    m.box('hardware', hd - T - .3, -.07, EAVE / 2, .1, .1, EAVE - .2)            # downpipe
    m.flush('east')
    w = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west')
    hs = [hole(f'west window f{k}', 1.5, F1 + k * FH + .9, .7, 1.1) for k in range(2)] + [hole('west ground window', -2.0, Z1 + .7, .85, 2.5)]
    w.wall('west carrier', -hd + T, hd - T, 0.0, EAVE, depth=T, role='wall', holes=hs)
    G.brick_courses(w, -hd + T + .02, hd - T - .02, .7, EAVE - .02, hs, spacing=.2)
    m = Merge(w)
    m.box('foundation', 0, -.03, .3, 2 * hd - 2 * T - .02, .06, .6)
    for h in hs:
        framed(m, w, h, cols=2, rows=2, inset=.12, occupied='room', lite=True)
    for z in (F1 - .55, F1 + FH - .55, EAVE - .45):
        anchors(m, (-4.5, -1.0, 2.5, 5.2), z)
    m.flush('west')
    n = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')
    hs = [hole(f'rear sash f{k} {i}', u, F1 + k * FH + .5, 1.0, 2.0) for k in range(2) for i, u in enumerate((-1.6, 1.6))] + \
         [hole('rear door', 0.0, Z1, 1.0, 2.3, kind='door')]
    n.wall('north carrier', X0, X1 - EPS, 0.0, EAVE, depth=T, role='wall', holes=hs)
    brick_bond(n, X0 + .02, X1 - .02, .7, EAVE - .02, hs)
    m = Merge(n)
    m.box('foundation', 0, -.03, .05, X1 - X0 - .02, .06, .1)
    for h in hs:
        if h.get('kind') == 'door':
            m.box('door', h['u'], .16, h['z'] + h['h'] / 2, h['w'] - .02, .06, h['h'] - .02)
            register(n, h, .14, 'rear door', 'hall')
        else:
            framed(m, n, h, cols=3, rows=4, inset=.12, occupied='room')
            m.box('trim', h['u'], .1, h['z'] + h['h'] / 2, h['w'] - .1, .1, .08)
            m.box('stone', h['u'], -.04, h['z'] - .06, h['w'] + .12, .12, .1)
    for z in (F1 - .55, F1 + FH - .55, EAVE - .45):
        anchors(m, (-2.95, 0.0, 2.95), z)
    m.flush('north')
    # A plain raked rear gable, coped, with the chimney at its apex (top view).
    hw = (X1 - X0) / 2
    rise = TIER0 + STEPS * STEP_H - .4
    pts = [(-hw, EAVE), (hw, EAVE), (hw, EAVE + .14), (0.0, EAVE + rise + .26), (-hw, EAVE + .14)]
    C.prism('Rear gable', [(-x, z) for x, z in pts], 'y', Y1 - T, Y1, 'wall', 'gable')
    b = Batch()
    for i, s in enumerate((-1, 1)):
        b.beam('stone', (s * (hw + .05), Y1 - T / 2, EAVE + .16), (0.0, Y1 - T / 2, EAVE + rise + .3), T + .1 + .04 * i, .12, ext=.04)
    chimney(b, 0.0, Y1 - T / 2, EAVE + rise - .2, EAVE + rise + 1.3, w=.9, d=.6, pots=2)
    b.flush('rear gable')
    gv = [hole('rear gable window', 0.0, EAVE + .5, .8, 1.0)]
    gf = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north gable')
    m = Merge(gf)
    m.box('trim', 0.0, -.03, EAVE + 1.0, .9, .06, 1.1)
    m.box('glass', 0.0, -.065, EAVE + 1.0, .72, .02, .92)
    m.box('trim', 0.0, -.08, EAVE + 1.0, .05, .02, .92)
    m.flush('north gable')


def roof_and_inside():
    hw = (X1 - X0) / 2
    rise = TIER0 + STEPS * STEP_H - .4
    ov = .3
    y0, y1 = Y0 + T + .01, Y1 - T - .01
    slope = rise / hw
    for s in (-1, 1):
        slope_plate(f'Tiled roof {"west" if s < 0 else "east"}', (s * (hw + ov), EAVE - ov * slope), (0.0, EAVE + rise), y0, y1)
    b = Batch()
    for x in (X0 - .22, X1 + .22):                                             # gutters between the gables only
        b.box('hardware', x, 0.0, EAVE - ov * slope + .02, .16, y1 - y0 - .1, .14)
    for s in (-1, 1):                                                          # white eave cornice boards
        b.box('white', s * (hw + .08), 0.0, EAVE - .6, .14, y1 - y0 - .1, .4)
    b.flush('roof furniture')
    for z in (Z1, F1, F1 + FH):
        C.box(f'Floor {z:.1f}', (0, 0, z - .12), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .24), 'floor', 'inside', 0)
    C.box('Attic floor', (0, 0, EAVE - .12), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .24), 'floor', 'inside', 0)
    for z in (Z1, F1, F1 + FH):
        C.qa_room_light(f'Front room {z:.0f}', (0, Y0 + 2.2, z + 2.2), 40, 2.4)
    C.qa_room_light('Attic', (0, Y0 + 1.5, EAVE + 1.0), 20, 1.4)
    C.CONTACTS.append(dict(name='Brick walls from grade; stepped gables on the street and rear walls; roof plates between them', eave_m=EAVE))


def site():
    C.box('Street paving', (0, Y0 - 7.0, .02), (30.0, 14.0, .04), 'setts', 'site', 0)
    C.box('East alley', (X1 + 2.0, 4.0 + .0, .021), (4.0, 20.0, .042), 'paving', 'site', 0)
    b = Batch()
    for k in range(-20, 21):
        b.box('joint', k * .7, Y0 - 7.0, .042, .02, 13.9, .004)
    b.box('hardware', -5.2, Y0 - 1.6, 1.8, .12, .12, 3.6)                    # lamp standard
    b.box('hardware', -5.2, Y0 - 1.6, 3.85, .32, .32, .5)
    b.flush('street')
    C.rod('Street tree trunk', (-8.0, Y0 - 3.0, .04), (-8.0, Y0 - 3.0, 8.0), .2, 'timber', 'street planting', 8)
    for i, (dx, dy, z, r, h) in enumerate(((0, 0, 10.4, 2.5, 3.4), (.7, -.4, 8.4, 1.9, 2.0), (-.6, .3, 12.6, 1.6, 1.6))):
        A.foliage(f'Street tree crown {i}', (-8.0 + dx, Y0 - 3.0 + dy, z), (r, r, h), detail=2)


def build():
    site()
    south_face()
    side_and_rear()
    roof_and_inside()
    C.CONTACTS.append(dict(name='Narrow step-gable canal house on a brick-paved street, alley east', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(-30, -45, 40), fill=(40, -20, 30), rear=(-15, 35, 30), target=(0, 0, 8.0), gain=4.0)
