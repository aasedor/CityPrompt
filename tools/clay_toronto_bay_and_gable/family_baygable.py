"""Toronto bay-and-gable house, authored from the locked catalogue views of
toronto_bay_and_gable_house / variant_0.

Read from the pixels (the top view governs the plan): a detached two-and-a-half-storey red-brick house on a
street corner, the street to the south and a side street to the west. On the south front a steep cross gable
with an ornate pierced bargeboard, a curved fretwork arch and a spike finial over a triple attic window, above
a two-storey canted bay with stained-glass transoms, buff stone sill and lintel bands and a small slate skirt
roof between the floors. East of the bay a hipped entrance porch on turned posts with a spindle frieze, a dark
green door with a transom and a stone stair down to a brick walk. A steep slate main roof: a front section
gabled to west and east with a brick chimney at the east gable, a hipped rear section behind it. A rough stone
foundation with basement windows, a long west side elevation of tall sashes facing the side street, a low iron
fence round the front lawn, sidewalks and street trees.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-toronto-bay-and-gable-house'
X0, X1, Y0, Y1 = -3.8, 3.8, -5.5, 5.5         # 7.6 m wide, 11.0 m deep main block; street front at Y0
T = .30
G0 = .90                                        # top of the stone foundation (water table)
F1 = .95                                        # raised ground floor
F2 = 4.25                                       # upper floor
EAVE = 7.25
YR = Y0 + 2.9                                   # east-west ridge of the front roof section
ZR = EAVE + 3.2                                 # main ridge
XC, HW = -1.2, 2.6                              # front cross gable: centre line and half width (x -3.8 to 1.4)
ZC = EAVE + 3.0                                 # cross-gable ridge, just under the main ridge
BP, BF = .75, .85                               # canted bay: projection and half front width
EPS = .002
PALETTE = dict(wall=(.62, .33, .24), joint=(.70, .55, .47), trim=(.42, .32, .22), pale=(.86, .84, .80),
    stone=(.76, .70, .58), roof=(.34, .35, .37), foundation=(.55, .53, .50), glass=(.30, .36, .40),
    stained=(.80, .56, .26), hardware=(.10, .10, .11), interior=(.86, .82, .76), floor=(.62, .56, .48),
    timber=(.50, .40, .28), door=(.14, .27, .21), planting=(.30, .44, .20), grass=(.38, .50, .24),
    paving=(.72, .71, .68), asphalt=(.28, .28, .29), walk=(.56, .32, .24), brick=(.60, .32, .23), pot=(.66, .40, .30))


def manifest(version):
    h = ZC + 1.1
    cams = G.camera_roster(X1 - X0 + 4.0, Y1 - Y0 + 4.0, h, [
        ('bay_window', (XC + .4, Y0 - 11.0, 3.9), (XC + .4, Y0 - BP, 3.9), 40),
        ('gable_bargeboard', (XC, Y0 - 9.0, 9.4), (XC, Y0, 8.7), 45),
        ('porch_entrance', (2.6, Y0 - 7.0, 1.9), (2.3, Y0, 2.0), 40),
        ('porch_frieze', (.2, Y0 - 4.6, 2.5), (2.4, Y0 - 1.9, 3.3), 35),
        ('west_side', (X0 - 15.0, 0.0, 4.6), (X0, 0.0, 4.6), 40),
        ('west_gable', (X0 - 9.0, YR, 9.2), (X0, YR, 8.6), 45),
        ('roof_chimney', (9.0, -13.0, 17.0), (1.0, -1.0, 9.6), 40),
        ('foundation_fence', (-2.0, Y0 - 6.5, 1.1), (-1.6, Y0 - 2.6, .7), 40),
        ('interior', (XC, Y0 - .3, F1 + 1.6), (XC + .8, Y0 + 5.0, F1 + 1.3), 30),
        ('rear_north', (0.0, Y1 + 17.0, 5.0), (0.0, Y1, 5.0), 45)])
    for c in cams:                       # the locked front looks from the south-south-west at eye level
        if c['name'] == 'front':
            c['location'] = (-7.0, Y0 - 12.8, 1.6); c['target'] = (-.2, Y0 + 2.5, 5.0); c['lens'] = 28; c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='toronto_bay_and_gable_house/variant_0',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=2, storey_programme='two full storeys over a raised stone foundation and a half-storey attic in the gables',
            plan='7.6 x 11.0 m detached corner house (top view); canted bay and porch on the south front, side street to the west',
            facade='red brick with buff stone sill and lintel bands; two-storey canted bay under an ornate front gable; hipped porch on turned posts',
            levels_m=[F1, F2, EAVE], roof_m=dict(eave=EAVE, ridge=ZR, cross_gable=ZC),
            inferred='interiors, the east and rear faces and metric dimensions are teaching assumptions; the rear repeats the visible grammar'),
        roof_contract=dict(type='steep slate roof: front section gabled east and west, hipped rear section, front cross gable with bargeboard and finial; brick chimney at the east gable',
            datum_m=EAVE, crowns_m=[ZR, ZC]),
        identity_contract=dict(owner='Toronto bay-and-gable: red-brick house with a two-storey canted bay under a steep ornamented front gable, a side entrance porch and a steep slate roof'),
        material_contract=dict(profile='source-palette clay: red brick, buff stone bands, grey rubble foundation, grey slate, brown painted woodwork, green door, amber stained-glass transoms', textured_keeper=False),
        programme_contract=dict(storeys=2, ground='parlour in the bay, hall and stair behind the porch', upper='bedrooms; attic room in the front gable'),
        contact_contract=['Grade-zero lawn, walks and sidewalks', 'Brick walls on a stone foundation', 'Roofs on the eaves and gable walls', 'Porch on a stone base and stair'],
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
# ---- Toronto bay-and-gable house ----

S1 = (ZR - EAVE) / (YR - Y0)                    # front roof section slope (east-west ridge)
S2 = (ZC - EAVE) / HW                           # cross-gable slope
S3 = (ZR - EAVE) / ((X1 - X0) / 2)              # hipped rear section slope
OV = .40                                        # horizontal eave overhang of the front section
ZE = EAVE - S1 * OV                             # every eave edge sits at this height
OVX = (ZC - ZE) / S2 - HW                       # cross-gable side overhang, so its valleys meet the eave
OVR = (EAVE - ZE) / S3                          # rear section overhang (same eave height)
OVM = OVR                                       # main gable rakes overhang to meet the rear eaves
OVF = .50                                       # front gable rake projects past the gable wall
YG = YR + (ZR - EAVE) / S1                      # north eave line of the front section
YH = Y1 - (X1 - X0) / 2                         # end of the rear ridge (hip)
YV = Y0 + (ZC - EAVE) / S1                      # cross-gable valley apex on the main front slope
W1, H1 = F1 + .55, 2.05                         # ground-floor sash sill and height
W2, H2 = F2 + .55, 1.95                         # upper-floor sash sill and height
PX0, PX1, PD = 1.00, 3.95, 2.10                  # porch x extent and depth
SQ = math.sqrt(.5)


def zs(x, y): return EAVE + S1 * (y - Y0)
def zn(x, y): return ZR - S1 * (y - YR)
def zx(x, y): return ZC - S2 * abs(x - XC)
def zrw(x, y): return ZR - S3 * abs(x)
def zrn(x, y): return ZR - S3 * (y - YH)


def plate(name, pts, zf, t=.18, role='roof', module='roof'):
    """Roof plate over an xy polygon, every vertex on the plane zf; wound counter-clockwise from above."""
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area < 0:
        pts = pts[::-1]
    return C.solid_surface(name, [(x, y, zf(x, y)) for x, y in pts], t, role, module)


def sash(m, f, h, occupied='room', stone=True, transom=True, lite=False):
    """Tall one-over-one sash with a stained-glass transom light, a stone sill and a stone lintel."""
    framed(m, f, h, cols=1, rows=1, inset=.12, occupied=occupied, lite=lite)
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    if not lite:
        m.box('trim', u, .1, z + (hh - .48) * .5, w - .1, .1, .07)                  # meeting rail
        if transom:
            m.box('trim', u, .1, z + hh - .48, w - .1, .1, .07)
            m.box('stained', u, .145, z + hh - .25, w - .16, .006, .34)
    if stone:
        m.box('stone', u, -.05, z - .07, w + .24, .2, .14)
        m.box('stone', u, -.03, z + hh + .12, w + .3, .14, .24)


def courses(f, lo, hi, holes, z0=G0 + .05, z1=EAVE - .05):
    G.brick_courses(f, lo + .02, hi - .02, z0, z1, holes, spacing=.085)


def tri_courses(f, u0, u1, z0, zap, holes, spacing=.085):
    """Mortar courses clipped to a gable triangle (base u0..u1 at z0, apex at zap over the middle)."""
    uc, half = (u0 + u1) / 2, (u1 - u0) / 2
    vs, fs = [], []
    z = z0 + .05
    while z < zap - .45:
        hw = half * (zap - z - .1) / (zap - z0) - .06
        for a, c in G.subtract_openings(uc - hw, uc + hw, z, z + .006, holes):
            o = len(vs)
            vs += [f.p(a, -.002, z), f.p(c, -.002, z), f.p(c, -.002, z + .006), f.p(a, -.002, z + .006)]
            fs.append((o, o + 1, o + 2, o + 3))
        z += spacing
    if fs:
        C.mesh(f.label + ' gable mortar courses', vs, fs, 'joint', 'brick joints')


def shifted(f, d, label):
    o = f.o - f.n * d
    return C.Face(tuple(o), tuple(f.t), tuple(f.n), label)


def wall_face(f, lo, hi, holes, base_holes=(), top=EAVE, name=None):
    """Stone foundation carrier (proud by 4 cm) under a brick carrier; returns the face Merge."""
    name = name or f.label
    fo = shifted(f, .04, f.label + ' foundation')
    fo.wall(name + ' foundation carrier', lo, hi, 0.0, G0, depth=T + .04, role='foundation', holes=list(base_holes))
    G.brick_courses(fo, lo + .02, hi - .02, .12, G0 - .06, list(base_holes), spacing=.27)
    f.wall(name + ' carrier', lo, hi, G0, top, depth=T, role='wall', holes=holes)
    courses(f, lo, hi, holes, z1=top - .05)
    m = Merge(f)
    mb = Merge(fo)
    mb.box('stone', (lo + hi) / 2, -.05, G0 - .04, hi - lo + .06, .12, .1)        # bevelled water table
    for h in base_holes:
        framed(mb, fo, h, cols=2, rows=1, inset=.14, occupied='basement', lite=True)
        C.OPENINGS[-1]['carrier_depth_m'] = T + .04
    mb.flush(fo.label)
    return m


def south_face():
    f = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south')
    door = hole('front door', 1.75, F1, .95, 2.3, kind='door')
    tr = hole('front door transom', 1.75, F1 + 2.38, .95, .42)
    up = hole('upper sash over porch', 2.15, W2, 1.0, H2)
    holes = [hole('bay opening ground', XC, F1, 2 * (BF + BP) - .6, 2.75), hole('bay opening upper', XC, F2, 2 * (BF + BP) - .6, 2.7),
             door, tr, up]
    m = wall_face(f, X0, X1, holes)
    # Dark green four-panel door, glazed upper panels, stained transom, stone threshold.
    m.box('door', door['u'], .16, door['z'] + door['h'] / 2, door['w'] - .02, .05, door['h'] - .02)
    for zz, hh in ((.5, .7), (1.35, .6)):
        for s in (-1, 1):
            m.box('trim', door['u'] + s * .2, .125, door['z'] + zz, .3, .02, hh)
    m.box('glass', door['u'], .125, door['z'] + 1.85, .62, .02, .55)
    m.box('hardware', door['u'] + .33, .12, door['z'] + 1.05, .06, .05, .12)
    register(f, door, .12, 'entry door', 'hall')
    framed(m, f, tr, cols=1, rows=1, inset=.12, occupied='hall')
    m.box('stained', tr['u'], .145, tr['z'] + tr['h'] / 2, tr['w'] - .16, .006, tr['h'] - .16)
    m.box('stone', tr['u'], -.03, tr['z'] + tr['h'] + .12, tr['w'] + .3, .14, .24)
    m.box('stone', door['u'], -.06, F1 - .03, door['w'] + .2, .2, .06)
    sash(m, f, up)
    m.flush('south')


def west_face():
    f = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west')
    holes = [hole(f'west ground sash {k}', -y, W1, .95, H1) for k, y in enumerate((-4.4, -2.5, 2.0, 4.2))] + \
            [hole(f'west upper sash {k}', -y, W2, .95, H2) for k, y in enumerate((-4.4, -2.5, -.3, 2.0, 4.2))]
    base = [hole(f'west basement {k}', -y, .3, .75, .42) for k, y in enumerate((-3.4, 1.0, 3.2))]
    m = wall_face(f, -(Y1 - T), -(Y0 + T), holes, base)
    for h in holes:
        sash(m, f, h)
    m.box('hardware', -(Y0 + .45), -.08, EAVE / 2, .1, .1, EAVE - .1)                # downpipe at the front corner
    m.flush('west')


def east_face():
    f = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    holes = [hole(f'east ground sash {k}', y, W1, .95, H1) for k, y in enumerate((-4.2, -.9, 2.8))] + \
            [hole(f'east upper sash {k}', y, W2, .95, H2) for k, y in enumerate((-4.2, -.9, 2.8))]
    base = [hole(f'east basement {k}', y, .3, .75, .42) for k, y in enumerate((-1.6, 2.2))]
    m = wall_face(f, Y0 + T, Y1 - T, holes, base)
    for h in holes:
        sash(m, f, h, transom=False)
    m.box('hardware', Y1 - .6, -.08, EAVE / 2, .1, .1, EAVE - .1)
    m.flush('east')


def north_face():
    f = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')
    door = hole('rear door', -2.3, F1, .95, 2.25, kind='door')
    holes = [hole('rear ground sash 0', 2.4, W1, .95, H1), hole('rear ground sash 1', .1, W1, .95, H1), door] + \
            [hole(f'rear upper sash {k}', u, W2, .95, H2) for k, u in enumerate((2.4, 0.0, -2.4))]
    base = [hole('rear basement', 1.2, .3, .75, .42)]
    m = wall_face(f, -X1, -X0, holes, base)
    for h in holes:
        if h.get('kind') == 'door':
            framed(m, f, h, cols=1, rows=3, inset=.12, occupied='kitchen', kind='door', lite=True)
            m.box('stone', h['u'], -.03, h['z'] + h['h'] + .12, h['w'] + .3, .14, .24)
        else:
            sash(m, f, h, transom=False)
    m.flush('north')
    # Rear stoop: stone landing and steps down to grade at the kitchen door.
    b = Batch()
    b.box('stone', 2.3, Y1 + .54, (F1 - .02) / 2, 1.5, 1.0, F1 - .02)                      # landing (north face u = -x)
    for i in range(1, 4):
        hh = (F1 - .02) * (4 - i) / 4
        b.box('stone', 2.3, Y1 + 1.04 + .3 * (i - .5), hh / 2, 1.5, .3, hh)
    b.flush('rear stoop')


def bay():
    """Two-storey canted bay under the front gable: carriers on the three faces, stone bands, slate skirt roof."""
    A_ = (XC - BF - BP, Y0); B_ = (XC - BF, Y0 - BP); C_ = (XC + BF, Y0 - BP); D_ = (XC + BF + BP, Y0)
    L = BP / SQ / 2
    faces = [(C.Face(((A_[0] + B_[0]) / 2, (A_[1] + B_[1]) / 2, 0), (SQ, -SQ, 0), (SQ, SQ, 0), 'bay west'), -L - .3, L, .55),
             (C.Face((XC, Y0 - BP, 0), (1, 0, 0), (0, 1, 0), 'bay front'), -BF, BF, 1.15),
             (C.Face(((C_[0] + D_[0]) / 2, (C_[1] + D_[1]) / 2, 0), (SQ, SQ, 0), (-SQ, SQ, 0), 'bay east'), -L, L + .3, .55)]
    for f, lo, hi, w in faces:
        holes = [hole(f.label + ' ground sash', 0.0, W1, w, H1), hole(f.label + ' upper sash', 0.0, W2, w, H2)]
        base = [hole(f.label + ' basement', 0.0, .3, .8, .42)] if f.label == 'bay front' else []
        m = wall_face(f, lo, hi, holes, base)
        for h in holes:
            sash(m, f, h, occupied='parlour bay', stone=False)
        e0, e1 = (lo + .3 if lo < -L else lo) - .1, (hi - .3 if hi > L else hi) + .1
        for zb in (W1 - .07, W2 - .07):                                              # continuous stone sill bands
            m.box('stone', (e0 + e1) / 2, -.05, zb, e1 - e0, .2, .14)
        for zb in (W1 + H1 + .12, W2 + H2 + .12):                                    # continuous stone lintel bands
            m.box('stone', (e0 + e1) / 2, -.03, zb, e1 - e0, .14, .24)
        m.flush(f.label)
    # Slate skirt roof between the floors and the cornice and flat cap at the top.
    pts = [A_, B_, C_, D_]

    def offset(d, yback):
        segs = [(pts[i], pts[i + 1]) for i in range(3)]
        nrm = []
        for (a, c) in segs:
            tx, ty = c[0] - a[0], c[1] - a[1]; ln = math.hypot(tx, ty)
            nrm.append((ty / ln, -tx / ln))
        out = []
        for i in range(4):
            if i in (0, 3):
                n = nrm[0] if i == 0 else nrm[2]
                a = segs[0] if i == 0 else segs[2]
                tx, ty = a[1][0] - a[0][0], a[1][1] - a[0][1]
                px, py = pts[i][0] + n[0] * d, pts[i][1] + n[1] * d
                t = (yback - py) / ty                                                  # slide along the face back to the wall line
                out.append((px + tx * t, yback))
            else:
                n0, n1 = nrm[i - 1], nrm[i]
                mx, my = n0[0] + n1[0], n0[1] + n1[1]; k = d / (1 + n0[0] * n1[0] + n0[1] * n1[1])
                out.append((pts[i][0] + mx * k, pts[i][1] + my * k))
        return out
    strip('Bay skirt roof', offset(.42, Y0 + .02), offset(-.04, Y0 + .02), 3.95, 4.36, 'roof', 'bay', closed=False)
    b = Batch()
    cor = offset(.16, Y0 + .01)
    for i in range(3):
        b.beam('trim', (*cor[i], EAVE - .16), (*cor[i + 1], EAVE - .16), .34, .30, ext=.1)
        b.beam('trim', (*cor[i], EAVE - .38), (*cor[i + 1], EAVE - .38), .22, .12, ext=.06)
    b.flush('bay cornice')
    C.prism('Bay cap', offset(.20, Y0 + .02)[::-1], 'z', EAVE - .02, EAVE + .04, 'trim', 'bay')
    inner = offset(-T, Y0 + T)
    for z in (F1, F2):
        C.prism(f'Bay floor {z:.1f}', inner[::-1], 'z', z - .22, z, 'floor', 'inside')
    C.prism('Bay ceiling', inner[::-1], 'z', EAVE - .22, EAVE - .02, 'floor', 'inside')


def gables():
    """Brick gable walls (carriers with attic windows): the front cross gable and the west and east gables."""
    f = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south')
    g = C.prism('Front gable', [(X0, EAVE), (XC + HW, EAVE), (XC, ZC - .12)], 'y', Y0, Y0 + T, 'wall', 'envelope')
    g['rlasm_wall_carrier'] = True
    att = [hole('attic centre window', XC, EAVE + .4, .66, 1.3), hole('attic west window', XC - .62, EAVE + .4, .4, .95),
           hole('attic east window', XC + .62, EAVE + .4, .4, .95)]
    for h in att:
        f.cut(g, h['id'] + ' full carrier cut', h['u'], h['z'], h['w'], h['h'], T)
    m = Merge(f)
    for h in att:
        framed(m, f, h, cols=1, rows=2, inset=.12, occupied='attic room')
        m.box('stained', h['u'], .145, h['z'] + h['h'] - .2, h['w'] - .16, .006, .26)
    m.box('stone', XC, -.05, EAVE + .33, 1.95, .2, .12)                                 # shared stone sill
    for h in att:
        m.box('stone', h['u'], -.03, h['z'] + h['h'] + .1, h['w'] + .2, .12, .2)
    m.flush('front gable')
    tri_courses(f, X0, XC + HW, EAVE, ZC - .12, att)
    w = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west')
    g = C.prism('West gable', [(Y0, EAVE), (YG, EAVE), (YR, ZR - .12)], 'x', X0, X0 + T, 'wall', 'envelope')
    g['rlasm_wall_carrier'] = True
    wa = [hole('west attic window', -YR, EAVE + .45, 1.1, 1.25)]
    w.cut(g, wa[0]['id'] + ' full carrier cut', -YR, EAVE + .45, 1.1, 1.25, T)
    m = Merge(w)
    framed(m, w, wa[0], cols=2, rows=2, inset=.12, occupied='attic room')
    m.box('stone', -YR, -.05, EAVE + .38, 1.34, .2, .14)
    m.box('stone', -YR, -.03, EAVE + 1.82, 1.4, .14, .24)
    m.flush('west gable')
    tri_courses(w, -YG, -Y0, EAVE, ZR - .12, wa)
    C.prism('East gable', [(Y0, EAVE), (YG, EAVE), (YR, ZR - .12)], 'x', X1 - T, X1, 'wall', 'envelope')['rlasm_wall_carrier'] = True
    e = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    tri_courses(e, Y0, YG, EAVE, ZR - .12, [])


def roofs():
    zx_e = XC + HW + OVX
    plate('Main front slope', [(X0 - OVM, Y0 - OV), (XC - HW - OVX, Y0 - OV), (XC, YV), (zx_e, Y0 - OV), (X1 + OVM, Y0 - OV),
                                (X1 + OVM, YR), (X0 - OVM, YR)], zs)
    yc = YR + (S3 / S1) * (X1 + OVM)
    plate('Main rear slope west', [(0.0, YR), (X0 - OVM, YR), (X0 - OVM, yc)], zn)
    plate('Main rear slope east', [(0.0, YR), (X1 + OVM, YR), (X1 + OVM, yc)], zn)
    plate('Cross gable west slope', [(XC - HW - OVX, Y0 - OVF), (XC, Y0 - OVF), (XC, YV), (XC - HW - OVX, Y0 - OV)], zx)
    plate('Cross gable east slope', [(XC, Y0 - OVF), (zx_e, Y0 - OVF), (zx_e, Y0 - OV), (XC, YV)], zx)
    plate('Rear section west slope', [(0.0, YR), (0.0, YH), (X0 - OVR, Y1 + OVR), (X0 - OVR, yc)], zrw)
    plate('Rear section east slope', [(0.0, YR), (X1 + OVR, yc), (X1 + OVR, Y1 + OVR), (0.0, YH)], zrw)
    plate('Rear section hip', [(0.0, YH), (X1 + OVR, Y1 + OVR), (X0 - OVR, Y1 + OVR)], zrn)
    b = Batch()
    up = .06
    b.beam('roof', (X0 - OVM, YR, ZR + up), (X1 + OVM, YR, ZR + up), .16, .1)                       # ridges and hips
    b.beam('roof', (0.0, YR, ZR + up), (0.0, YH, ZR + up), .16, .1)
    for s in (-1, 1):
        b.beam('roof', (0.0, YH, ZR + up), (s * (X1 + OVR), Y1 + OVR, ZE + up), .14, .08)
    b.beam('roof', (XC, Y0 - OVF, ZC + up), (XC, YV, ZC + up), .14, .08)
    # Plain painted fascias on the main gable rakes and the rear eaves; gutters and downpipes.
    for x in (X0 - OVM + .03, X1 + OVM - .03):
        b.beam('trim', (x, Y0 - OV, ZE - .1), (x, YR, ZR - .1), .05, .24, ext=.03)
        b.beam('trim', (x, YR, ZR - .1), (x, yc, ZE - .1), .05, .24, ext=.03)
    b.beam('trim', (zx_e, Y0 - OV - .03, ZE - .1), (X1 + OVM, Y0 - OV - .03, ZE - .1), .05, .24)
    b.beam('hardware', (zx_e + .1, Y0 - OV - .1, ZE - .1), (X1 + OVM, Y0 - OV - .1, ZE - .1), .14, .12)
    for s in (-1, 1):
        x = s * (X1 + OVR - .03)
        b.beam('trim', (x, yc, ZE - .1), (x, Y1 + OVR, ZE - .1), .05, .24)
        b.beam('hardware', (x + s * .06, yc + .2, ZE - .1), (x + s * .06, Y1 + OVR - .05, ZE - .1), .12, .12)
    b.beam('trim', (X0 - OVR, Y1 + OVR - .03, ZE - .1), (X1 + OVR, Y1 + OVR - .03, ZE - .1), .05, .24)
    b.beam('hardware', (X0 - OVR + .05, Y1 + OVR + .03, ZE - .1), (X1 + OVR - .05, Y1 + OVR + .03, ZE - .1), .12, .12)
    # Soffits under the eaves (painted boards) where the walls meet the overhangs.
    b.box('trim', (zx_e + X1 + OVM) / 2 - .2, Y0 - OV / 2, EAVE - .06, X1 + OVM - zx_e + .4, OV, .06)
    for s in (-1, 1):
        b.box('trim', s * (X1 + OVR / 2), (YG + Y1 + OVR) / 2, EAVE - .06, OVR, Y1 + OVR - YG, .06)
    b.box('trim', 0.0, Y1 + OVR / 2, EAVE - .06, X1 - X0 + 2 * OVR, OVR, .06)
    chimney(b, X1 - .55, YR, EAVE + 1.6, ZR + 1.0, w=.9, d=.62, pots=2, role='brick', pot='pot', cap='stone')
    b.box('brick', X1 - .55, YR, ZR + .55, 1.02, .74, .1)                           # oversailing course
    b.flush('roof furniture')


def bargeboard():
    """Ornate front gable: pierced bargeboard with roundels and drops, a fretwork arch, finial and pendant."""
    y = Y0 - OVF + .04
    b = Batch()
    ends = [(XC - HW - OVX, ZE), (XC + HW + OVX, ZE)]
    for (xe, ze) in ends:
        top = (XC, ZC - .12); bot = (xe, ze - .12)
        b.beam('trim', (top[0], y, top[1]), (bot[0], y, bot[1]), .07, .30, ext=.04)          # bargeboard plank
        L = math.hypot(bot[0] - top[0], bot[1] - top[1])
        ux, uz = (bot[0] - top[0]) / L, (bot[1] - top[1]) / L
        nx, nz = uz, -ux                                                              # normal pointing down
        if nz > 0:
            nx, nz = -nx, -nz
        lo = [(top[0] + nx * .52, top[1] + nz * .52), (bot[0] + nx * .52, bot[1] + nz * .52)]
        b.beam('trim', (lo[0][0], y, lo[0][1]), (lo[1][0], y, lo[1][1]), .05, .07)           # lower rail of the pierced band
        k = 0
        s = .45
        while s < L - .3:
            cx, cz = top[0] + ux * s + nx * .34, top[1] + uz * s + nz * .34
            annulus(f'Bargeboard roundel {xe:.1f} {k}', (cx, y, cz), (0, 1, 0), .06, .11, -.03, .03, 'trim', 'gable ornament', segs=12)
            dx, dz = top[0] + ux * (s + .22) + nx * .62, top[1] + uz * (s + .22) + nz * .62
            b.box('trim', dx, y, dz, .06, .05, .18)                                           # drop
            b.box('trim', dx, y, dz - .12, .1, .06, .08)
            s += .45
            k += 1
    # Fretwork arch over the attic windows, tied into the bargeboards, with spindles above it.
    cz0, R = EAVE + 1.05, 1.5
    arc = [(XC + R * math.cos(math.radians(a)), cz0 + R * math.sin(math.radians(a))) for a in range(18, 163, 9)]
    for i in range(len(arc) - 1):
        b.beam('trim', (arc[i][0], y + .03, arc[i][1]), (arc[i + 1][0], y + .03, arc[i + 1][1]), .06, .14, ext=.02)
    for (ax, az) in arc[1:-1:2]:
        ztop = zx(ax, 0) - .55
        if ztop > az + .1:
            b.box('trim', ax, y + .03, (az + ztop) / 2, .045, .045, ztop - az)
    b.beam('trim', (XC - .9, y + .05, EAVE + 2.55), (XC + .9, y + .05, EAVE + 2.55), .05, .1)   # collar
    # Finial and pendant at the apex; carved brackets at the gable feet.
    C.rod('Gable finial', (XC, y, ZC - .2), (XC, y, ZC + 1.0), .045, 'trim', 'gable ornament', 8)
    b.box('trim', XC, y, ZC + .2, .16, .16, .2)
    b.box('trim', XC, y, ZC + .62, .1, .1, .14)
    C.rod('Gable pendant', (XC, y, ZC - .2), (XC, y, ZC - 1.05), .05, 'trim', 'gable ornament', 8)
    b.box('trim', XC, y, ZC - 1.05, .14, .14, .14)
    for x in (X0 + .12, XC + HW - .12):
        for k in range(3):
            b.box('trim', x, Y0 - .12 - .1 * k, EAVE - .22 - .12 * k, .14, .2, .14)
    # Painted cornice across the gable base either side of the bay.
    for (a, c) in ((X0, XC - BF - BP), (XC + BF + BP, XC + HW)):
        b.box('trim', (a + c) / 2, Y0 - .12, EAVE - .1, c - a, .26, .2)
    b.flush('gable ornament')


def porch():
    """Hipped entrance porch on turned posts with a spindle frieze, iron balustrade and a stone stair."""
    xm, yf = (PX0 + PX1) / 2, Y0 - PD
    C.box('Porch base', (xm, Y0 - PD / 2, (F1 - .08) / 2), (PX1 - PX0, PD, F1 - .08), 'foundation', 'porch', 0)
    C.box('Porch deck', (xm, Y0 - (PD + .03) / 2, F1 - .04), (PX1 - PX0 + .06, PD + .03, .08), 'timber', 'porch', 0)
    b = Batch()
    for zz in (.3, .6):
        b.box('joint', xm, yf - .002, zz, PX1 - PX0 - .04, .006, .012)                 # stone courses on the base
    posts = [(PX0 + .14, yf + .14), (PX1 - .14, yf + .14)]
    zt = 3.55
    for (px, py) in posts:
        b.box('trim', px, py, F1 + .12, .18, .18, .24)
        C.rod('Porch post', (px, py, F1 + .24), (px, py, zt - .2), .06, 'trim', 'porch', 10)
        for zz, r, hh in ((F1 + .7, .085, .3), (F1 + 1.6, .08, .18), (zt - .55, .085, .3)):
            C.rod('Porch post turning', (px, py, zz), (px, py, zz + hh), r, 'trim', 'porch', 10)
        b.box('trim', px, py, zt - .14, .18, .18, .14)
    b.box('trim', xm, yf + .14, zt + .07, PX1 - PX0 + .1, .2, .3)                      # beams
    for x in (PX0 + .14, PX1 - .14):
        b.box('trim', x, (yf + Y0) / 2, zt + .07, .2, PD, .3)
    # Spindle frieze under the beams, front and sides, with curved corner brackets.
    zf0, zf1 = zt - .32, zt - .08
    runs = [((PX0 + .24, yf + .14), (PX1 - .24, yf + .14)), ((PX0 + .14, yf + .24), (PX0 + .14, Y0 - .05)),
            ((PX1 - .14, yf + .24), (PX1 - .14, Y0 - .05))]
    for (a, c) in runs:
        b.beam('trim', (a[0], a[1], zf0), (c[0], c[1], zf0), .05, .05)
        b.beam('trim', (a[0], a[1], zf1), (c[0], c[1], zf1), .05, .05)
        L = math.hypot(c[0] - a[0], c[1] - a[1]); n = int(L / .1)
        for i in range(1, n):
            t = i / n
            b.box('trim', a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t, (zf0 + zf1) / 2, .025, .025, zf1 - zf0)
    for (px, py) in posts:
        for dx, dy in ((1 if px < xm else -1, 0), (0, 1)):
            b.beam('trim', (px + dx * .1, py + dy * .1, zf0 - .35), (px + dx * .45, py + dy * .45, zf0 - .02), .05, .07)
    # Iron balustrade: west side, the front west of the stair, east side.
    sx0, sx1 = 2.35, PX1 - .26
    rails = [((PX0 + .14, Y0 - .05), (PX0 + .14, yf + .24)), ((PX0 + .24, yf + .14), (sx0, yf + .14)),
             ((PX1 - .14, yf + .24), (PX1 - .14, Y0 - .05))]
    for (a, c) in rails:
        b.beam('hardware', (a[0], a[1], F1 + .92), (c[0], c[1], F1 + .92), .05, .04)
        b.beam('hardware', (a[0], a[1], F1 + .12), (c[0], c[1], F1 + .12), .04, .03)
        L = math.hypot(c[0] - a[0], c[1] - a[1]); n = max(2, int(L / .11))
        for i in range(n + 1):
            t = i / n
            b.box('hardware', a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t, F1 + .52, .018, .018, .8)
    b.flush('porch')
    # Hipped porch roof: front plane and two hip triangles against the wall.
    ov, ze, zw = .22, zt + .22, 4.25
    xw, xe, yfr = PX0 - ov, PX1 + ov, yf - ov
    xa, xb = xw + 1.15, xe - 1.15

    def zf(x, y):
        return ze + (zw - ze) * (y - yfr) / (Y0 - yfr)

    def zwh(x, y):
        return ze + (zw - ze) * (x - xw) / (xa - xw)

    def zeh(x, y):
        return ze + (zw - ze) * (xe - x) / (xe - xb)
    plate('Porch roof front', [(xw, yfr), (xe, yfr), (xb, Y0), (xa, Y0)], zf, t=.12)
    plate('Porch roof west hip', [(xw, yfr), (xa, Y0), (xw, Y0)], zwh, t=.12)
    plate('Porch roof east hip', [(xe, yfr), (xe, Y0), (xb, Y0)], zeh, t=.12)
    b = Batch()
    b.beam('trim', (xw, yfr - .02, ze - .08), (xe, yfr - .02, ze - .08), .04, .18)
    b.beam('trim', (xw - .02, yfr, ze - .08), (xw - .02, Y0, ze - .08), .04, .18)
    b.beam('trim', (xe + .02, yfr, ze - .08), (xe + .02, Y0, ze - .08), .04, .18)
    b.beam('hardware', (xw, yfr - .09, ze - .1), (xe, yfr - .09, ze - .1), .12, .1)
    b.beam('roof', (xw, yfr, ze + .03), (xa, Y0, zw + .03), .1, .06)
    b.beam('roof', (xe, yfr, ze + .03), (xb, Y0, zw + .03), .1, .06)
    b.beam('trim', (xa, Y0 - .03, zw + .02), (xb, Y0 - .03, zw + .02), .06, .1)       # flashing board on the wall
    # Stone stair down to the brick walk, iron handrails both sides.
    r, run, n = F1 / 5, .30, 4
    yb = yf - n * run
    prof = [(yf + .02, 0.0), (yb, 0.0)]
    for i in range(n):
        prof += [(yb + i * run, (i + 1) * r), (yb + (i + 1) * run, (i + 1) * r)]
    prof += [(yf + .02, F1 - .08)]
    C.prism('Porch stair', prof, 'x', sx0, sx1, 'stone', 'porch')
    for x in (sx0 + .05, sx1 - .05):
        b.beam('hardware', (x, yb + .1, r + .9), (x, yf, F1 + .9), .05, .04)
        for k in range(n):
            b.box('hardware', x, yb + .15 + k * run, r * (k + 1) + .45, .025, .025, .9)
    b.flush('porch roof')


def interior():
    xi0, xi1, yi0, yi1 = X0 + T, X1 - T, Y0 + T, Y1 - T
    C.box('Ground floor', ((xi0 + xi1) / 2, (yi0 + yi1) / 2, F1 - .11), (xi1 - xi0, yi1 - yi0, .22), 'floor', 'inside', 0)
    C.box('Upper floor', ((xi0 + xi1) / 2, (yi0 + yi1) / 2, F2 - .12), (xi1 - xi0, yi1 - yi0, .24), 'floor', 'inside', 0)
    C.box('Attic floor', ((xi0 + xi1) / 2, (yi0 + yi1) / 2, EAVE - .12), (xi1 - xi0, yi1 - yi0, .24), 'floor', 'inside', 0)
    C.box('Hall partition', (.75, yi0 + 3.2, (F1 + F2) / 2 - .12), (.12, 6.4, F2 - F1 - .24), 'interior', 'inside', 0)
    C.box('Upper partition', ((xi0 + xi1) / 2, .6, (F2 + EAVE) / 2 - .12), (xi1 - xi0, .12, EAVE - F2 - .24), 'interior', 'inside', 0)
    C.box('Ground partition', ((xi0 + xi1) / 2, 1.2, (F1 + F2) / 2 - .12), (xi1 - xi0, .12, F2 - F1 - .24), 'interior', 'inside', 0)
    # Parlour fireplace on the cross partition: brick breast, dark firebox, timber mantel, overmantel glass.
    yp = 1.2 - .06
    C.box('Parlour chimney breast', (XC, yp - .2, (F1 + F2) / 2 - .12), (1.7, .4, F2 - F1 - .24), 'brick', 'inside', 0)
    C.box('Parlour firebox', (XC, yp - .41, F1 + .45), (.75, .04, .8), 'hardware', 'inside', 0)
    C.box('Parlour mantel shelf', (XC, yp - .48, F1 + 1.25), (1.9, .22, .08), 'trim', 'inside', 0)
    for s in (-1, 1):
        C.box('Parlour mantel pilaster', (XC + s * .6, yp - .44, F1 + .62), (.16, .1, 1.24), 'trim', 'inside', 0)
    C.box('Parlour overmantel mirror', (XC, yp - .41, F1 + 2.0), (1.0, .03, 1.1), 'glass', 'inside', 0)
    for name, loc, p in (('Parlour', (XC, Y0 + 2.0, F2 - .5), 45), ('Hall', (2.2, Y0 + 2.0, F2 - .5), 30),
                         ('Kitchen', (0, 3.4, F2 - .5), 35), ('Front bedroom', (XC, Y0 + 2.0, EAVE - .5), 40),
                         ('Rear bedroom', (0, 3.0, EAVE - .5), 35), ('Attic', (XC, Y0 + 1.6, EAVE + 1.6), 25)):
        C.qa_room_light(name, loc, p, 2.0)


def site():
    yw = Y0 - 4.0                                   # back of the front sidewalk
    xw = X0 - 1.6                                   # back of the side-street sidewalk
    C.box('Lawn', ((xw + X1 + 3.5) / 2, (yw + Y1 + 3.0) / 2, .015), (X1 + 3.5 - xw, Y1 + 3.0 - yw, .03), 'grass', 'site', 0)
    C.box('Front sidewalk', ((X0 - 5.2 + X1 + 8.0) / 2, yw - .9, .05), (X1 + 8.0 - X0 + 5.2, 1.8, .1), 'paving', 'site', 0)
    C.box('Side sidewalk', (xw - .8, (yw + Y1 + 3.0) / 2, .05), (1.6, Y1 + 3.0 - yw, .1), 'paving', 'site', 0)
    C.box('Side boulevard', (xw - 2.6, (yw + Y1 + 3.0) / 2, .02), (2.0, Y1 + 3.0 - yw, .04), 'grass', 'site', 0)
    C.box('Side street curb', (xw - 3.675, (yw - 1.8 + Y1 + 3.0) / 2, .07), (.15, Y1 + 3.0 - yw + 1.8, .14), 'paving', 'site', 0)
    C.box('Front curb', ((X0 - 5.2 + X1 + 8.0) / 2, yw - 1.875, .07), (X1 + 8.0 - X0 + 5.2, .15, .14), 'paving', 'site', 0)
    C.box('Front street', ((X0 - 12.0 + X1 + 8.0) / 2, yw - 5.45, .005), (X1 + 8.0 - X0 + 12.0, 7.0, .01), 'asphalt', 'site', 0)
    C.box('Side street', (xw - 7.25, (yw - 1.95 + Y1 + 3.0) / 2, .005), (7.0, Y1 + 3.0 - yw + 1.95, .01), 'asphalt', 'site', 0)
    b = Batch()
    for k in range(int((X1 + 8.0 - X0 + 5.2) / 1.5)):
        b.box('joint', X0 - 5.2 + k * 1.5, yw - .9, .101, .02, 1.78, .004)
    for k in range(int((Y1 + 3.0 - yw) / 1.5)):
        b.box('joint', xw - .8, yw + k * 1.5, .101, 1.58, .02, .004)
    for k in range(9):                                                           # centre line of the side street
        b.box('pale', xw - 7.25, yw - 1.0 + k * 2.4, .012, .12, 1.2, .004)
    # Brick walk from the stair to the sidewalk.
    yb = Y0 - PD - 4 * .30
    C.box('Brick walk', ((2.35 + PX1 - .26) / 2, (yb + yw) / 2, .03), (PX1 - .26 - 2.35, yb - yw, .06), 'walk', 'site', 0)
    for k in range(int((yb - yw) / .2)):
        b.box('joint', (2.35 + PX1 - .26) / 2, yw + .1 + k * .2, .061, PX1 - .26 - 2.35 - .02, .012, .004)
    b.flush('site joints')
    # Low iron fence round the front lawn; shrubs in the beds.
    yfc = Y0 - 2.9
    iron_fence((X0 - .7, Y0 - .3), (X0 - .7, yfc), height=.95, wall=.14, spacing=.13)
    iron_fence((X0 - .7, yfc), (2.25, yfc), height=.95, wall=.14, spacing=.13)
    for (x, y, h) in ((X0 - .1, Y0 - 1.2, .8), (XC + 1.3, Y0 - 1.25, .7), (XC - 1.5, Y0 - 1.3, .7), (PX1 + .6, Y0 - .7, 1.0),
                      (PX1 + .6, Y0 - 1.9, .8), (X0 - .9, 1.5, .9)):
        A.shrub(x, y, .03, h)
    street_tree(xw - 2.6, Y0 + 1.0, z=.04, height=9.0, spread=2.0)
    street_tree(xw - 2.6, Y1 - .5, z=.04, height=8.0, spread=1.8)
    street_tree(X1 + 3.2, Y0 + 3.5, z=.03, height=8.5, spread=2.0)
    C.rod('Hydro pole', (xw - 3.2, Y1 + 2.0, .04), (xw - 3.2, Y1 + 2.0, 9.5), .14, 'timber', 'street', 8)


def build():
    site()
    south_face()
    west_face()
    east_face()
    north_face()
    bay()
    gables()
    roofs()
    bargeboard()
    porch()
    interior()
    C.CONTACTS.append(dict(name='Detached two-and-a-half-storey bay-and-gable house on a corner lot', box=[X0, X1, Y0, Y1], eave_m=EAVE,
                           ridge_m=ZR))


LIGHT_RIG = dict(key=(-28, -36, 30), fill=(34, -22, 24), rear=(-12, 32, 26), target=(0, -1, 4.8), gain=4.0)
