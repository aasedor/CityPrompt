"""Halifax waterfront warehouse, authored from the locked catalogue views of
halifax_waterfront_warehouse / variant_0 (warehouse_privateers_wharf).

Read from the pixels (the top view governs the plan): a two-storey Italianate commercial warehouse on a street
corner, the street south and a side street east, a brick neighbour attached to the west. Red brick bays framed
by rusticated grey granite piers; a tall ground storey of dark-green framed shopfront glazing with transoms
and a double entrance door in the middle bay of the south front; a granite belt entablature; round-arched
upper windows in granite archivolts with keystones, a triplet, a single large arch and a pair across the south
front and pairs on the east side; a deep verdigris copper cornice with paired brackets; a brick parapet with a
copper coping and raised blocks over the piers, a larger raised panel over the middle bay. Ground-floor arched
windows in brick on the east side behind the corner shop. A flat membrane roof with brick chimneys on the rear
parapet; sidewalks, street trees and a lamp.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-halifax-waterfront-warehouse'
X0, X1, Y0, Y1 = -12.1, 12.1, -8.5, 8.5        # 24.2 m south front, 17 m east side
T = .45
G0 = .5                                         # granite plinth and ground floor
STEP = .3                                       # granite entrance step
BELT0, BELT1 = 4.9, 5.8                         # granite belt entablature
FRIEZE = 10.0
CORN = 11.15                                    # top of the copper cornice
PAR = 11.8                                      # parapet top
EPS = .002
PALETTE = dict(wall=(.42, .21, .15), joint=(.50, .48, .45), stone=(.70, .67, .60), arch=(.70, .67, .60),
    copper=(.42, .58, .52), frame=(.15, .25, .20), trim=(.15, .25, .20), pale=(.86, .86, .84),
    roof=(.34, .31, .28), sand=(.62, .58, .52), foundation=(.56, .54, .50), glass=(.20, .24, .26),
    hardware=(.07, .07, .08), interior=(.82, .78, .72), floor=(.56, .46, .36), timber=(.46, .34, .22),
    planting=(.30, .44, .20), soil=(.22, .16, .10), concrete=(.70, .69, .66), white=(.95, .95, .93),
    asphalt=(.28, .28, .29), brick=(.46, .26, .19), pot=(.60, .34, .22), neighbour=(.42, .27, .21), membrane=(.50, .50, .49),
    blue=(.20, .30, .40))


def manifest(version):
    h = PAR + 1.6
    cams = G.camera_roster(X1 - X0 + 3.0, Y1 - Y0 + 3.0, h, [
        ('facade_close', (0.0, -30.0, 6.0), (0.0, Y0, 6.0), 45),
        ('architecture_close', (18.0, -20.0, 12.0), (X1, Y0, 10.5), 45),
        ('glass_close', (-7.2, -16.0, 2.8), (-7.2, Y0, 2.8), 45),
        ('arched_windows', (0.0, -16.0, 8.4), (0.0, Y0, 8.4), 40),
        ('copper_cornice', (14.0, -15.0, 13.5), (9.0, Y0, 11.0), 40),
        ('granite_piers', (16.0, -14.0, 3.0), (X1, Y0, 3.5), 40),
        ('east_side', (30.0, 0.0, 6.0), (X1, 0.0, 6.0), 45),
        ('roof_chimneys', (-10.0, -16.0, 24.0), (0.0, 2.0, PAR), 40),
        ('interior', (3.0, 5.0, 2.2), (-3.0, Y0, 2.6), 40),
        ('rear_north', (0.0, 32.0, 7.0), (0.0, Y1, 7.0), 45)])
    for c in cams:                       # the locked front and oblique look from the south-east
        if c['name'] == 'front':
            c['location'] = (19.0, -24.0, 1.6); c['target'] = (2.5, -8.5, 6.5); c['lens'] = 24; c['whole'] = False
        elif c['name'] == 'front_corner':
            c.update(location=(24.0, -36.0, 28.0), target=(0.0, -1.0, 5.0), lens=35, whole=False)   # the locked oblique, high in the south-east
        elif c['name'] == 'left_side':                                         # high from the north-west, over the neighbour's roof
            c.update(location=(-30.0, 26.0, 22.0), target=(0.0, 0.0, 6.0), lens=35, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(36.0, 0.0, 7.0), target=(X1, 0.0, 6.0), lens=35, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(0.0, 38.0, 8.0), target=(0.0, Y1, 6.0), lens=35, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(30.0, 32.0, 18.0), target=(0.0, 0.0, 6.0), lens=35, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(26.0, -32.0, 34.0), target=(0.0, 0.0, 5.0), lens=35, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='halifax_waterfront_warehouse/variant_0 (warehouse_privateers_wharf)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=2, storey_programme='tall shop and warehouse floor, an upper loft floor',
            plan='24.2 x 17 m corner block (top view), a neighbour attached west',
            facade='red brick bays between rusticated granite piers; shopfront glazing and entrance; granite belt; round-arched upper windows with archivolts; verdigris copper bracketed cornice; parapet with raised blocks',
            levels_m=[G0, BELT1, FRIEZE, CORN, PAR], roof_m=dict(flat=CORN, parapet=PAR),
            inferred='interiors, the north wall and the west party wall are teaching assumptions'),
        roof_contract=dict(type='flat membrane roof inside a brick parapet with copper coping and raised blocks, brick chimneys on the rear parapet', datum_m=CORN, crowns_m=[PAR + .8]),
        identity_contract=dict(owner='two-storey Italianate brick-and-granite warehouse with round-arched upper windows, shopfront ground floor and a deep verdigris copper cornice'),
        material_contract=dict(profile='source-palette clay: red brick, grey granite with channelled joints, verdigris copper, dark-green frames, membrane roof', textured_keeper=False),
        programme_contract=dict(storeys=2, ground='shops and the entrance hall', upper='open loft offices'),
        contact_contract=['Grade-zero sidewalks and roads', 'Granite piers and brick walls from grade', 'Copper cornice on the walls', 'Roof inside the parapet'],
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


# ---- Halifax waterfront warehouse ----

def arch_head(f, h, rise, ring=.26, segs=16, ring_role='arch', course=None):
    """Segmental or round head on a rectangular cut: brick spandrel infill filling the cut's corners above the curve
    flush with the wall face (exactly the cut's width and height, so no recess reads at the shoulders), and a proud
    ring over it."""
    u, w, top = h['u'], h['w'], h['z'] + h['h']
    R = (w * w / 4 + rise * rise) / (2 * rise)
    cz = top - R
    a0 = math.asin(min(1.0, (w / 2) / R))
    arc = [(u + R * math.sin(-a0 + 2 * a0 * i / segs), cz + R * math.cos(-a0 + 2 * a0 * i / segs)) for i in range(segs + 1)]
    pts = [(u - w / 2, top - rise)] + arc + [(u + w / 2, top - rise)]
    vs, fs = [], []
    for (pu, pz) in pts:
        for d in (0.0, T - .01):
            vs.append(f.p(pu, d, pz)); vs.append(f.p(pu, d, top))
    for i in range(len(pts) - 1):
        a, b = 4 * i, 4 * (i + 1)
        fs += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3)]
    n = 4 * (len(pts) - 1)
    fs += [(0, 1, 3, 2), (n, n + 2, n + 3, n + 1)]
    C.mesh(f'{h["id"]} spandrel', vs, fs, 'wall', 'arches')
    if course:                                              # carry the wall's mortar courses across the spandrel corners
        z0, sp = course
        vs, fs = [], []
        k = math.ceil((top - rise - z0) / sp)
        while z0 + k * sp < top - .006:
            z = z0 + k * sp
            dz = z + .003 - cz
            half = math.sqrt(max(0.0, R * R - dz * dz)) if abs(dz) < R else 0.0
            for a, c in ((u - w / 2, u - half - .02), (u + half + .02, u + w / 2)):
                if c - a > .02:
                    o = len(vs)
                    vs += [f.p(a, -.002, z), f.p(c, -.002, z), f.p(c, -.002, z + .006), f.p(a, -.002, z + .006)]
                    fs.append((o, o + 1, o + 2, o + 3))
            k += 1
        if fs:
            C.mesh(f'{h["id"]} spandrel courses', vs, fs, 'joint', 'brick joints')
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




def street_face(label, origin, tangent, inward, lo, hi, corner_lo, corner_hi, piers, bays, wrap, wrap_hi=False):
    """A street front: carrier, granite piers, shopfronts or arched ground windows, arched upper windows,
    belt and copper cornice bands that reach the outer corner lines (the south front wraps the corner square)."""
    f = C.Face(origin, tangent, inward, label)
    holes, uppers, grounds = [], [], []
    for bay in bays:
        u, w, kind = bay['u'], bay['w'], bay['ground']
        if kind == 'glass':
            gs = [(hole(f'{label} shopfront {u:+.1f}', u, G0 + .05, w - .3, BELT0 - G0 - .25, kind='shopfront'), 'glass')]
        elif kind == 'door':                              # the entrance: a glazed double door on a granite step between sidelights
            gs = [(hole(f'{label} entrance {u:+.1f}', u, STEP, 2.2, BELT0 - .25 - STEP, kind='door'), 'door')] + \
                 [(hole(f'{label} sidelight {u + s * 1.8:+.1f}', u + s * 1.8, G0 + .05, 1.1, BELT0 - G0 - .25, kind='shopfront'), 'side') for s in (-1, 1)]
        elif kind == 'pair':                              # two shop lights divided by a brick pier
            gs = [(hole(f'{label} shop light {u + s * .95:+.1f}', u + s * .95, G0 + .05, 1.5, BELT0 - G0 - .25, kind='shopfront'), 'side') for s in (-1, 1)]
        else:                                             # tall narrow arched windows in brick
            gw = bay.get('gw', .75)                       # a triplet by default; bay['gdu'] sets other counts (east bay 3 is a pair)
            gs = [(hole(f'{label} ground arch {u + du:+.1f}', u + du, .95, gw, BELT0 - .4 - .95), 'arch') for du in bay.get('gdu', (-1.2, 0.0, 1.2))]
        for g, k in gs:
            grounds.append((g, k)); holes.append(g)
        for du, ww, hh in bay['upper']:
            h = hole(f'{label} arch {u + du:+.1f}', u + du, BELT1 + .55, ww, hh)
            uppers.append(h); holes.append(h)
    f.wall(f'{label} carrier', lo, hi - EPS, 0.0, PAR, depth=T, role='wall', holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, G0 + .05, FRIEZE - .02, holes, spacing=.16)
    m = Merge(f)

    def band(role, d, t, z, h):
        p = -(d - t / 2)
        a, c = (lo - p, hi + p) if wrap else (corner_lo, corner_hi + (p if wrap_hi else 0.0))      # wrap_hi: runs on round the far corner
        m.box(role, (a + c) / 2, d, z, c - a, t, h)
    pa, pc = (lo - .2, hi + .2) if wrap else (corner_lo, corner_hi + (.2 if wrap_hi else 0.0))                          # granite plinth, broken at the entrance
    cuts = sorted((g['u'] - g['w'] / 2, g['u'] + g['w'] / 2) for g, k in grounds if k == 'door')
    for c0, c1 in cuts + [(pc, pc)]:
        if c0 - pa > .05:
            m.box('stone', (pa + c0) / 2, -.1, G0 / 2, c0 - pa, .2, G0)
        pa = c1
    for g, kind in grounds:
        if kind in ('glass', 'side'):
            framed(m, f, g, cols=3 if kind == 'glass' else 1, rows=1, inset=.16, occupied='shop', kind='shopfront', frame='frame')
            m.box('frame', g['u'], .14, g['z'] + g['h'] - .9, g['w'] - .1, .1, .09)            # transom bar
            m.box('frame', g['u'], .1, g['z'] + .25, g['w'] - .1, .14, .5)                     # stall riser
        elif kind == 'door':
            framed(m, f, g, cols=2, rows=1, inset=.16, occupied='shop', kind='door', frame='frame')
            m.box('frame', g['u'], .14, g['z'] + 3.15, g['w'] - .1, .1, .1)                    # transom bar over the leaves
            m.box('frame', g['u'], .12, g['z'] + .5, g['w'] - .12, .08, .9)                    # panelled lower leaves
            m.box('frame', g['u'], .14, g['z'] + 1.6, .1, .1, 3.1)                             # meeting stiles
            m.box('stone', g['u'], -.25, (.11 + STEP) / 2, g['w'] + .6, .5, STEP - .11)         # granite step
            for s in (-1, 1):                                                                 # frame posts between door and sidelights
                m.box('frame', g['u'] + s * 1.175, -.02, (STEP + BELT0 - .25) / 2, .17, .06, BELT0 - .25 - STEP)
        else:
            framed(m, f, g, cols=2, rows=3, inset=.16, occupied='warehouse', frame='frame')
            m.box('stone', g['u'], -.05, g['z'] - .07, g['w'] + .2, .14, .12)
            arch_head(f, g, g['w'] / 2, ring=.2 if g['w'] < 1 else .24, course=(G0 + .05, .16))
    for h in uppers:
        framed(m, f, h, cols=2, rows=4, inset=.16, occupied='loft', frame='frame')
        m.box('stone', h['u'], -.06, h['z'] - .08, h['w'] + .34, .16, .14)
        ring = .3 if h['w'] >= 1 else .16                                                   # slimmer archivolts on the narrow triplet lights
        arch_head(f, h, h['w'] / 2, ring=ring, course=(G0 + .05, .16))
        m.box('stone', h['u'], -.06, h['z'] + h['h'] + ring / 2, ring, .14, ring * 1.4)        # keystone
        for s in (-1, 1):                                                                     # granite impost blocks at the springing
            m.box('stone', h['u'] + s * (h['w'] / 2 + ring * .57), -.05, h['z'] + h['h'] - h['w'] / 2 - .08, ring * 1.2, .1, .2)
    band('stone', -.18, .36, BELT0 + .3, .6)                                                  # belt entablature
    band('stone', -.24, .48, BELT1 - .15, .3)
    band('stone', -.08, .16, BELT1 + .4, .14)                                                 # sill course
    # Copper entablature: a frieze band, a bed moulding, modillions between the piers, corona and cymatium;
    # over every pier a pair of scrolled consoles carries a forward break of the cornice.
    band('copper', -.08, .16, FRIEZE + .22, .44)
    band('copper', -.16, .32, FRIEZE + .49, .1)
    band('copper', -.48, .96, CORN - .25, .3)
    band('copper', -.54, 1.08, CORN - .05, .1)
    n = int((hi - lo) / .75)
    for i in range(n):
        u = lo + .375 + (hi - lo - .75) * i / max(1, n - 1)
        if all(abs(u - pu) > pw / 2 + .25 for pu, pw, _ in piers):
            m.box('copper', u, -.36, FRIEZE + .645, .16, .72, .22)
    if wrap:
        # The cornice runs on past the west wall over the lower neighbour: close the back of that overhang with plates
        # in the wall plane following the profile (corona and cymatium out to the break, the frieze and bed below),
        # so no open slot shows between the layers from behind.
        m.box('copper', lo - .635, .045, CORN - .145, 1.37, .11, .49)                         # behind corona and cymatium
        m.box('copper', lo - .135, .0425, (FRIEZE + .02 + CORN - .37) / 2, .37, .095, CORN - .39 - FRIEZE)   # behind frieze and bed
    ca, cc = (lo - .15, hi + .15) if wrap else (corner_lo + .55, corner_hi - .55)
    m.box('copper', (ca + cc) / 2, T / 2 - .05, PAR + .05, cc - ca, T + .2, .1)                 # parapet coping
    for u, w, raised in piers:
        a = max(u - w / 2, corner_lo if not wrap else lo - .25)
        c = min(u + w / 2, corner_hi if not wrap else hi + .25)
        if not wrap and (u - w / 2 < lo or u + w / 2 > hi):
            a, c = max(u - w / 2, corner_lo), min(u + w / 2, corner_hi)
        if wrap and u + w / 2 >= hi - .01:
            c = hi + .25
        if wrap and u - w / 2 <= lo + .01:
            a = lo - .25
        m.box('stone', (a + c) / 2, -.125, FRIEZE / 2, c - a, .25, FRIEZE)
        for k in range(int(FRIEZE / .55)):
            if not (BELT0 - .1 < .3 + k * .55 < BELT1 + .1):
                m.box('joint', (a + c) / 2, -.252, .3 + k * .55, c - a + .004, .012, .03)
        m.box('stone', (a + c) / 2, -.2, FRIEZE - .15, c - a + .1, .4, .3)                      # pier cap under the frieze
        m.box('copper', (a + c) / 2, -.2, FRIEZE + .375, c - a + .1, .4, .75)                   # frieze breaking forward over the pier
        for s in (-1, 1):                                                                     # paired consoles
            cu = u + s * (w / 2 - .2)
            m.box('copper', cu, -.33, FRIEZE + .375, .22, .66, .77)
            m.box('copper', cu, -.22, FRIEZE - .2275, .18, .44, .445)
        ra, rc = a - .15, c + .15                                                             # cornice break over the pier
        if wrap and c >= hi + .2:
            ra, rc = ra, hi + 1.2
        if wrap and a <= lo - .2:
            ra = lo - 1.2
        if not wrap:
            ra, rc = max(ra, corner_lo), min(rc, corner_hi)
        m.box('copper', (ra + rc) / 2, -.6, CORN - .225, rc - ra, 1.2, .29)
        ca2, cc2 = ra - .06, rc + (.12 if wrap and c >= hi + .2 else .06)
        if wrap and a <= lo - .2:
            ca2 = lo - 1.32
        if not wrap:
            ca2, cc2 = max(ca2, corner_lo), min(cc2, corner_hi)
        m.box('copper', (ca2 + cc2) / 2, -.66, CORN + .07, cc2 - ca2, 1.32, .1)
        if raised:
            m.box('wall', u, T / 2, PAR + .4, w, T, .7)
            m.box('copper', u, T / 2 - .05, PAR + .8, w + .14, T + .2, .1)
    m.flush(label)
    return f


def build_faces():
    hd = (Y1 - Y0) / 2
    sp = [(X0 + .7, 1.4, True), (-3.1, 1.2, True), (3.1, 1.2, True), (X1 - .7, 1.4, True)]
    sb = [dict(u=-7.2, w=7.0, ground='glass', upper=[(-2.0, 1.1, 2.55), (0.0, 1.1, 2.55), (2.0, 1.1, 2.55)]),
          dict(u=0.0, w=5.0, ground='door', upper=[(0.0, 2.4, 2.85)]),
          dict(u=7.2, w=7.0, ground='glass', upper=[(-1.6, 1.4, 2.75), (1.6, 1.4, 2.75)])]
    street_face('south', (0, Y0, 0), (1, 0, 0), (0, 1, 0), X0, X1, X0, X1, sp, sb, True)
    # East side: the south corner pier is the south front's; the bays start behind it.
    ep = [(Y0 + .7, 1.4, False), (-2.55, 1.1, True), (2.55, 1.1, True), (Y1 - .7, 1.4, False)]
    eb = [dict(u=-5.1, w=4.0, ground='pair', upper=[(-.85, 1.0, 2.65), (.85, 1.0, 2.65)]),        # bay 1: archivolts clear of each other and of the corner pier
          dict(u=0.0, w=4.0, ground='arches', upper=[(-1.2, .8, 2.55), (0.0, .8, 2.55), (1.2, .8, 2.55)]),   # bay 2: triplet over triplet
          dict(u=5.1, w=4.0, ground='arches', gdu=(-.9, .9), gw=.85, upper=[(-.9, 1.05, 2.65), (.9, 1.05, 2.65)])]   # bay 3: pair over pair
    street_face('east', (X1, 0, 0), (0, 1, 0), (-1, 0, 0), -hd + T, hd - T, Y0, Y1, ep[1:], eb, False, wrap_hi=True)
    # The east bands return 1.4 m along the north wall, butting the east bands' wrapped ends at the corner line.
    nf = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north return')
    m = Merge(nf)
    for role, d, t, z, h in (('stone', -.1, .2, G0 / 2, G0), ('stone', -.18, .36, BELT0 + .3, .6), ('stone', -.24, .48, BELT1 - .15, .3),
                             ('stone', -.08, .16, BELT1 + .4, .14), ('copper', -.08, .16, FRIEZE + .22, .44), ('copper', -.16, .32, FRIEZE + .49, .1),
                             ('copper', -.48, .96, CORN - .25, .3), ('copper', -.54, 1.08, CORN - .05, .1)):
        m.box(role, -X1 + .7, d, z, 1.4, t, h)
    m.flush('north return')
    # The east face's south corner pier: a return of the south corner pier, butting it on the corner line.
    b = Batch()
    b.box('stone', X1 + .125, Y0 + .7, FRIEZE / 2, .25, 1.4, FRIEZE)
    b.box('stone', X1 + .2, Y0 + .725, FRIEZE - .15, .4, 1.45, .3)
    for k in range(int(FRIEZE / .55)):
        if not (BELT0 - .1 < .3 + k * .55 < BELT1 + .1):
            b.box('joint', X1 + .252, Y0 + .7, .3 + k * .55, .012, 1.404, .03)
    b.box('copper', X1 + .2, (Y0 - .39 + Y0 + 1.45) / 2, FRIEZE + .375, .4, 1.84, .75)          # frieze break over the corner pier, east face and corner
    b.box('copper', X1 + .33, Y0 + 1.2, FRIEZE + .375, .66, .22, .77)                         # east consoles of the corner pier
    b.box('copper', X1 + .22, Y0 + 1.2, FRIEZE - .2275, .44, .18, .445)
    b.box('copper', X1 + .33, Y0 + .2, FRIEZE + .375, .66, .22, .77)
    b.box('copper', X1 + .22, Y0 + .2, FRIEZE - .2275, .44, .18, .445)
    b.box('copper', X1 + .6, (Y0 + Y0 + 1.55) / 2, CORN - .225, 1.2, 1.55, .29)                 # the cornice break turning the corner
    b.box('copper', X1 + .66, (Y0 + Y0 + 1.61) / 2, CORN + .07, 1.32, 1.61, .1)
    b.box('wall', X1 - T / 2, (Y0 + T + Y0 + 1.4) / 2, PAR + .4, T, 1.4 - T, .7)
    b.box('copper', X1 - T / 2 + .05, (Y0 + .525 + Y0 + 1.47) / 2, PAR + .8, T + .2, .945, .1)
    b.box('stone', 0.0, Y0 + T / 2 - .03, PAR + .6, 5.0, T + .06, 1.2)                         # granite-faced raised panel over the middle bay
    b.box('copper', 0.0, Y0 + T / 2 - .05, PAR + 1.25, 5.2, T + .2, .1)
    b.box('stone', 0.0, Y0 - .1, PAR + .55, 3.2, .06, .55)
    b.flush('east corner pier')
    w = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west party')
    w.wall('west party wall', -hd + T, hd - T, 0.0, PAR, depth=T, role='wall', holes=[])
    G.brick_courses(w, -hd + T + .02, hd - T - .02, G0 + .05, PAR - .3, [], spacing=.16)     # free above the neighbour's annex
    m = Merge(w)
    m.box('copper', 0.0, T / 2 - .05, PAR + .04, Y1 - Y0 - .6, T + .2, .1)                      # copper coping on the west parapet too
    m.flush('west party')
    n = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')
    hs = [hole(f'rear window {i} f{k}', u, z, 1.1, 2.4) for k, z in enumerate((1.2, BELT1 + .8)) for i, u in enumerate((-8.0, -2.5, 3.0, 8.5))]
    n.wall('north carrier', -X1, -X0 - EPS, 0.0, PAR, depth=T, role='wall', holes=hs)
    G.brick_courses(n, -X1 + .02, -X0 - .02, G0 + .05, PAR - .3, hs, spacing=.16)
    m = Merge(n)
    for h in hs:
        framed(m, n, h, cols=2, rows=3, inset=.16, occupied='loft', frame='frame', lite=True)
        m.box('stone', h['u'], -.05, h['z'] - .07, h['w'] + .2, .12, .12)
    m.box('copper', 0.0, T / 2 - .05, PAR + .05, X1 - X0 + .1, T + .2, .1)
    m.flush('north')


def roof_and_inside():
    C.box('Roof membrane', (0, 0, CORN - .45), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .2), 'roof', 'roof', 0)
    b = Batch()
    for x in (-3.5, 5.0):                                                                    # chimneys on the rear parapet
        b.box('brick', x, Y1 - T / 2 - .1, PAR + .7, 1.2, .9, 1.4)                             # seated within the coping
        b.box('stone', x, Y1 - T / 2 - .1, PAR + 1.45, 1.32, 1.02, .1)
    b.box('pale', 6.5, -2.0, CORN - .2, .9, .9, .3)                                           # hatch and vents
    for x, y in ((-7.0, 1.0), (1.5, 2.5)):
        b.box('hardware', x, y, CORN - .15, .3, .3, .4)
    b.flush('roof furniture')
    C.box('Ground floor', (0, 0, G0 - .1), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .2), 'floor', 'inside', 0)
    C.box('Loft floor', (0, 0, BELT1 - .12), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .24), 'floor', 'inside', 0)
    for z in (G0, BELT1):
        for x in (-7.0, 0.0, 7.0):
            C.qa_room_light(f'Room {x:+.0f} {z:.0f}', (x, Y0 + 3.0, z + 2.6), 70, 3.0)
        C.qa_room_light(f'East room {z:.0f}', (X1 - 3.0, 2.0, z + 2.6), 60, 3.0)
    C.CONTACTS.append(dict(name='Granite piers and brick walls from grade; copper cornice on the walls; flat roof inside the parapet', cornice_m=CORN))


def site():
    SW, R = 4.4, 2.5                                                                         # sidewalk width and curb-return radius
    xc, yc = X1 + SW - R, Y0 - SW + R                                                        # the curb return's centre
    arc = [(xc + R * math.cos(-math.pi / 2 + math.pi / 2 * i / 10), yc + R * math.sin(-math.pi / 2 + math.pi / 2 * i / 10)) for i in range(11)]
    C.prism('Corner sidewalks', [(-20.0, Y0 - SW)] + arc + [(X1 + SW, Y1 + 12.0), (X1, Y1 + 12.0), (X1, Y0), (-20.0, Y0)], 'z', 0.0, .12, 'concrete', 'site')
    C.box('South street', (2.0, Y0 - SW - 5.0, .01), (60.0, 10.0, .02), 'asphalt', 'site', 0)
    C.box('East street', ((xc + X1 + SW + 10.0) / 2, (Y0 - SW + Y1 + 12.0) / 2, .01), (X1 + SW + 10.0 - xc, Y1 + 12.0 - Y0 + SW, .02), 'asphalt', 'site', 0)
    b = Batch()
    for k in range(-13, 18):
        if k * 1.5 < xc - .2:
            b.box('joint', k * 1.5, Y0 - SW / 2, .121, .02, SW - .02, .004)
    for k in range(0, 19):
        b.box('joint', X1 + SW / 2, Y0 + .75 + k * 1.5, .121, SW - .02, .02, .004)
    for k in range(9):                                                                      # crossing over the side street
        b.box('white', X1 + SW + .7 + k * 1.1, Y0 - SW / 2, .022, .5, 3.0, .008)
    b.box('hardware', X0 + 2.0, Y0 - 3.7, 2.2, .14, .14, 4.4)                                  # second lamp, south-west
    b.box('pale', X0 + 2.0, Y0 - 3.7, 4.6, .34, .34, .4)
    b.box('hardware', X0 + 2.0, Y0 - 3.7, 4.85, .44, .44, .1)
    b.box('hardware', X1 + 3.7, 2.0, 2.2, .14, .14, 4.4)                                       # lamp standard
    b.box('pale', X1 + 3.7, 2.0, 4.6, .34, .34, .4)
    b.box('hardware', X1 + 3.7, 2.0, 4.85, .44, .44, .1)
    b.box('soil', X1 + 3.4, 6.5, .125, 1.4, 1.4, .01)
    b.flush('street')
    street_tree(X0 - 2.5, Y0 - 2.6, z=.12, height=8.5, spread=2.6)
    street_tree(X1 + 3.4, 6.5, z=.12, height=8.0, spread=2.4)
    # The brick neighbour attached to the west, as context: its east wall buried in ours. The top view governs its
    # depth: the main block stops about 28% of the warehouse depth short of the north wall; a lower annex sits behind
    # it, then an alley, so the warehouse's west parapet stands free for its northern third.
    nx0, nx1 = X0 - 10.0, X0 + .15
    ny1 = Y0 + .72 * (Y1 - Y0)
    C.box('Neighbour block', ((nx0 + nx1) / 2, (Y0 + .4 + ny1) / 2, 5.25), (nx1 - nx0, ny1 - Y0 - .4, 10.5), 'neighbour', 'context', 0)
    ay1 = ny1 + .12 * (Y1 - Y0)
    C.box('Neighbour annex', ((nx0 + .4 + nx1) / 2, (ny1 - .1 + ay1) / 2, 2.1), (nx1 - nx0 - .4, ay1 - ny1 + .1, 4.2), 'neighbour', 'context', 0)
    C.box('Alley', ((nx0 + X0) / 2, (ay1 + Y1 + 6.0) / 2, .01), (X0 - nx0, Y1 + 6.0 - ay1, .02), 'asphalt', 'site', 0)
    b = Batch()
    for z in (.6, 4.4, 7.6):
        for u in (nx0 + 1.5, nx0 + 4.0, nx0 + 6.5):
            b.box('glass', u, Y0 + .38, z + 1.2, 1.2, .04, 2.2 if z < 1 else 1.9)
    for z in (4.9, 7.8):                                                                    # rear windows above the annex
        for u in (nx0 + 2.0, nx0 + 5.0, nx0 + 8.0):
            b.box('glass', u, ny1 + .02, z + .9, 1.1, .04, 1.7)
    for u in (nx0 + 2.5, nx0 + 7.0):                                                        # annex windows and door
        b.box('glass', u, ay1 + .02, 1.6, 1.2, .04, 1.4)
    b.box('frame', nx0 + 5.0, ay1 + .02, 1.1, 1.0, .04, 2.2)
    b.box('stone', (nx0 + nx1) / 2, Y0 + .25, 10.2, nx1 - nx0 - .3, .4, .4)
    b.box('stone', (nx0 + nx1 - .15) / 2, ny1 + .05, 10.3, nx1 - nx0 - .45, .14, .3)               # rear cornice band
    b.box('membrane', (nx0 + nx1 - .3) / 2, (Y0 + .45 + ny1 - .05) / 2, 10.525, nx1 - nx0 - .5, ny1 - Y0 - .5, .07)          # grey membrane roofs
    b.box('membrane', (nx0 + .4 + nx1 - .3) / 2, (ny1 + ay1 - .05) / 2, 4.225, nx1 - nx0 - .9, ay1 - ny1 - .05, .07)
    b.flush('neighbour')


def build():
    site()
    build_faces()
    roof_and_inside()
    C.CONTACTS.append(dict(name='Two-storey Italianate corner warehouse with a neighbour attached west', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(30, -45, 40), fill=(-40, -20, 30), rear=(-15, 35, 30), target=(0, 0, 6.0), gain=4.0)
