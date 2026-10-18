"""Amsterdam canal warehouse, authored from the locked catalogue views of
amsterdam_canal_warehouse / variant_0 (canal_warehouse_spice).

Read from the pixels (the top view governs the plan): a four-storey red-brown brick warehouse on the corner of a
canal quay (south) and a side street (east), a second canal beyond the street. Two gabled sections side by
side under parallel roofs running back from the quay, the eastern one wider and taller; each street gable has a
stone coping, raised shoulder piers at its feet, a pinnacle at the peak and a projecting hoist beam. On each
section's axis a stack of green glazed loading doors with green board shutters folded back flat on the wall,
over a round-arched timber cart door; small segmental-arched windows with dark frames and stone sills flank them;
iron wall anchors throughout. The long east wall carries rows of small segmental windows, tall arched windows
and a door on the ground floor, and a white timber cornice under the eave. Behind the gables the inner roof
slopes give way to a flat deck with round vents; a dormer on the east slope; brick chimneys. A brick-paved quay
with a low brick parapet to the canal, a tree and a lamp; an attached gabled canal house to the west.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-amsterdam-canal-warehouse'
X0, X1, Y0, Y1 = -10.0, 10.0, -8.0, 8.0        # 20 m quay front, 16 m deep
XM = -0.5                                       # wall line between the west (9.5 m) and east (10.5 m) sections
T = .40
G0 = .0
FL = [0.0, 4.2, 7.2, 10.2]                      # ground floor and three upper floors
EAVE = 11.6                                     # the top loading doors straddle it into the gables
SLOPE = 1.0                                     # both roofs share one pitch, so the valley sits on XM at the eave
XRW, XRE = (X0 + XM) / 2, (XM + X1) / 2
RW, RE = EAVE + SLOPE * (XM - X0) / 2, EAVE + SLOPE * (X1 - XM) / 2
PAR = .35                                       # gable parapet above the roof plane
EPS = .002
PALETTE = dict(wall=(.47, .24, .17), joint=(.66, .56, .48), arch=(.42, .20, .14), trim=(.13, .15, .13),
    pale=(.88, .88, .86), stone=(.80, .78, .72), roof=(.24, .25, .27), membrane=(.52, .52, .50),
    sand=(.62, .52, .44), foundation=(.40, .33, .29), glass=(.24, .28, .30), hardware=(.08, .08, .09),
    interior=(.84, .78, .70), floor=(.58, .48, .38), timber=(.47, .32, .19), green=(.22, .36, .25),
    planting=(.32, .46, .20), soil=(.22, .16, .10), concrete=(.66, .64, .60), white=(.95, .95, .93),
    asphalt=(.30, .30, .31), brick=(.53, .30, .22), pot=(.60, .34, .22), setts=(.50, .44, .40),
    paving=(.58, .42, .36), water=(.16, .22, .22), neighbour=(.62, .48, .40), blue=(.20, .30, .40))


def manifest(version):
    h = RE + PAR + 1.6
    cams = G.camera_roster(X1 - X0 + 3.0, Y1 - Y0 + 3.0, h, [
        ('facade_close', (4.0, -26.0, 7.5), (4.0, Y0, 7.5), 45),
        ('architecture_close', (16.0, -18.0, 14.0), (X1, Y0, 13.0), 45),
        ('glass_close', (1.0, -15.0, 8.7), (1.0, Y0, 8.7), 45),
        ('loading_doors', (6.5, -16.0, 9.0), (4.0, Y0, 9.0), 40),
        ('arched_doors', (XRE + 1.6, -15.0, 2.2), (XRE, Y0, 2.0), 40),
        ('gable_tops', (-1.0, -20.0, 22.0), (0.0, Y0, 17.5), 45),
        ('east_side', (26.0, 2.0, 7.0), (X1, 0.0, 7.0), 45),
        ('roof_deck', (-14.0, -12.0, 34.0), (0.0, 1.0, EAVE + 4.0), 40),
        ('interior', (6.5, 4.0, FL[1] + 1.6), (3.0, Y0, FL[1] + 1.6), 40),
        ('rear_north', (0.0, 34.0, 9.0), (0.0, Y1, 9.0), 45)])
    for c in cams:                       # the locked front and oblique look from the south-east
        if c['name'] == 'front':
            c['location'] = (18.0, -26.0, 1.6); c['target'] = (-1.0, -6.0, 9.5); c['lens'] = 26; c['whole'] = False
        elif c['name'] == 'front_corner':                                      # the locked oblique, from high in the south-east
            c['location'] = (26.0, -34.0, 26.0); c['target'] = (0.0, -1.0, 7.0); c['lens'] = 35; c['whole'] = False
        elif c['name'] == 'aerial':
            c['location'] = (22.0, -27.0, 36.0); c['target'] = (0.0, 0.0, 6.0); c['lens'] = 35; c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='amsterdam_canal_warehouse/variant_0 (canal_warehouse_spice)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=4, storey_programme='ground-floor cart bays and four storeys of storage lofts under the gables',
            plan='20 x 16 m corner warehouse (top view): a 9.5 m west and a 10.5 m east section, a 3.5 m quay south, a 4 m street east',
            facade='red-brown brick; twin coped street gables with shoulder piers, pinnacles and hoist beams; green loading doors and shutters over arched cart doors; segmental windows; iron anchors',
            levels_m=FL + [EAVE], roof_m=dict(eave=EAVE, ridges=[RW, RE]),
            inferred='interiors and the north face are teaching assumptions; the rear gables repeat the front outline without openings'),
        roof_contract=dict(type='two parallel gabled roofs behind coped gables, a flat vented deck between the ridges at the rear, a dormer and chimneys', datum_m=EAVE, crowns_m=[RW, RE]),
        identity_contract=dict(owner='twin-gabled brick canal warehouse with green shuttered loading-door stacks over arched cart doors, coped gables with hoist beams, on a canal quay'),
        material_contract=dict(profile='source-palette clay: red-brown brick with pale joints, darker arch rings, green doors and shutters, dark frames, stone sills, copings and springers, dark roof tiles', textured_keeper=False),
        programme_contract=dict(storeys=4, ground='cart bays and dispatch', upper='storage lofts', attic='hoist lofts under the gables'),
        contact_contract=['Grade-zero quay paving, street setts and canal', 'Brick walls from grade on a plinth', 'Coped gables on the quay wall', 'Roofs between the gables'],
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


# ---- Amsterdam canal warehouse ----

def arch_head(f, h, rise, ring=.26, segs=10, ring_role='arch'):
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
        for d in (.01, T - .01):
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


def anchors(m, us, z, s=.4):
    for u in us:
        m.box('hardware', u, -.03, z, .07, .04, s)


def window(m, f, h, rise=.18, occupied='loft', lite=False, ring=.26):
    framed(m, f, h, cols=2, rows=3 if h['h'] > 1 else 1, inset=.14, occupied=occupied, lite=lite)
    m.box('stone', h['u'], -.04, h['z'] - .06, h['w'] + .14, .14, .1)
    arch_head(f, h, rise, ring=ring)


def loading_bay(m, f, h):
    """Green glazed loading door (solid lower panels) with board shutters folded back flat either side."""
    framed(m, f, h, cols=2, rows=3, inset=.14, occupied='loft', frame='green')
    m.box('green', h['u'], .1, h['z'] + .45, h['w'] - .1, .04, .8)                     # solid lower panels in front of the glass
    m.box('stone', h['u'], -.04, h['z'] - .06, h['w'] + .14, .14, .1)
    for s in (-1, 1):
        cu = h['u'] + s * (h['w'] / 2 + .12 + h['w'] / 4)
        m.box('green', cu, -.06, h['z'] + h['h'] / 2 - .05, h['w'] / 2, .05, h['h'] - .2)
        for zz in (.35, h['h'] - .55):                                      # ledges and a brace
            m.box('trim', cu, -.092, h['z'] + zz, h['w'] / 2 - .04, .016, .08)
        m.box('trim', cu, -.092, h['z'] + h['h'] / 2 - .1, .07, .016, h['h'] - 1.1)
    arch_head(f, h, .22)


def cart_door(m, f, h, rise):
    m.box('timber', h['u'], .16, h['z'] + h['h'] / 2, h['w'] - .02, .06, h['h'] - .02)
    m.box('hardware', h['u'], .125, h['z'] + h['h'] / 2 - .1, .04, .012, h['h'] - .2)        # meeting stiles
    for k in range(1, 6):
        m.box('trim', h['u'] - h['w'] / 2 + h['w'] * k / 6, .127, h['z'] + h['h'] / 2 - .1, .025, .01, h['h'] - .3)
    for s in (-1, 1):                                                                       # stone springers and plinth blocks
        m.box('stone', h['u'] + s * (h['w'] / 2 + .14), -.04, h['z'] + h['h'] - rise - .1, .32, .14, .3)
        m.box('stone', h['u'] + s * (h['w'] / 2 + .14), -.04, .25, .32, .14, .5)
    m.box('stone', h['u'], -.05, h['z'] + h['h'] + .13, .34, .16, .4)                        # keystone
    register(f, h, .14, 'cart door', 'dispatch')
    arch_head(f, h, rise, ring=.32)


def section_holes(cu, hw, wu, door_w, door_h):
    door = hole(f'cart door {cu:+.0f}', cu, 0.0, door_w, door_h, kind='door')
    gw = [hole(f'ground window {cu + s * wu:+.1f}', cu + s * wu, .95, 1.15, 2.2) for s in (-1, 1)]
    bays = [hole(f'loading door {cu:+.0f} f{k}', cu, FL[k] + .45, 1.3, 2.35, kind='loading door') for k in (1, 2, 3)]
    ups = [hole(f'window {cu + s * wu:+.1f} f{k}', cu + s * wu, FL[k] + .75, .85, 1.5) for k in (1, 2) for s in (-1, 1)]
    return door, gw, bays, ups


PANEL = 1.0                                      # half-width of the gable panel round each top loading door
PANEL_H = 1.9


def split_top(h):
    """The top loading door straddles the eave: its lower part is cut in the wall, its upper part in a gable panel."""
    lo = hole(h['id'] + ' below eave', h['u'], h['z'], h['w'], EAVE - h['z'])
    hi = hole(h['id'] + ' above eave', h['u'], EAVE, h['w'], h['z'] + h['h'] - EAVE)
    return lo, hi


def gable_outline(z_off=PAR, notches=False):
    """M-shaped outline of the twin gables above the eave, in (x, z), clockwise from the west foot; with notches,
    the bottom edge steps up round the two loading-door panels."""
    top = [(X0, EAVE), (X0, EAVE + z_off), (XRW, RW + z_off), (XM, EAVE + z_off), (XRE, RE + z_off), (X1, EAVE + z_off), (X1, EAVE)]
    if not notches:
        return top
    bottom = []
    for xc in (XRE, XRW):
        bottom += [(xc + PANEL, EAVE), (xc + PANEL, EAVE + PANEL_H), (xc - PANEL, EAVE + PANEL_H), (xc - PANEL, EAVE)]
    return top + bottom


def rear_outline(z_off=PAR):
    xd = XRE - (RE - RW) / SLOPE
    return [(X0, EAVE), (X0, EAVE + z_off), (XRW, RW + z_off), (xd, RW + z_off), (XRE, RE + z_off), (X1, EAVE + z_off), (X1, EAVE)]


def gable_dressing(b, y, front=True):
    """Stone copings on the rakes, shoulder piers at the feet, a pinnacle at each peak and the hoist beams."""
    out = gable_outline()
    for i, ((xa, za), (xb, zb)) in enumerate(zip(out[1:-2], out[2:-1])):         # alternate widths: no shared side planes at joints
        b.beam('stone', (xa, y, za + .05), (xb, y, zb + .05), T + (.12 if i % 2 else .16), .14 + .02 * (i % 2), ext=.08)
    for x in (X0 + .33, XM, X1 - .33):
        b.box('wall', x, y, EAVE + .25, .72, T + .08, 1.3)
        b.box('stone', x, y, EAVE + .96, .86, T + .2, .14)
    for xr, zr in ((XRW, RW), (XRE, RE)):
        b.box('wall', xr, y, zr + PAR + .55, .8, T + .06, 1.1)
        b.box('stone', xr, y, zr + PAR + 1.16, .94, T + .18, .14)
        if front:
            b.box('timber', xr, Y0 - .6, zr - 1.9, .28, 1.4, .32)                              # hoist beam
            b.box('stone', xr, Y0 - .06, zr - 1.55, 1.0, .16, .2)                             # its stone hood


def south_face():
    f = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south')
    dw, gw_w, bays_w, ups_w = section_holes(XRW, 4.0, 2.4, 1.9, 3.3)
    de, gw_e, bays_e, ups_e = section_holes(XRE, 6.0, 3.0, 2.5, 3.6)
    tops = [split_top(bays_w[2]), split_top(bays_e[2])]
    holes = [dw, de] + gw_w + gw_e + bays_w[:2] + bays_e[:2] + [t[0] for t in tops] + ups_w + ups_e
    f.wall('south carrier', X0, X1 - EPS, 0.0, EAVE, depth=T, role='wall', holes=holes)
    G.brick_courses(f, X0 + .02, X1 - .02, .55, EAVE - .02, holes, spacing=.2)
    for xc, (lo, hi) in zip((XRW, XRE), tops):
        f.wall(f'gable panel {xc:+.0f}', xc - PANEL, xc + PANEL - EPS, EAVE, EAVE + PANEL_H, depth=T, role='wall', holes=[hi])
        G.brick_courses(f, xc - PANEL + .02, xc + PANEL - .02, EAVE + .02, EAVE + PANEL_H - .02, [hi], spacing=.2)
    m = Merge(f)
    m.box('foundation', 0, -.03, .26, X1 - X0 - .02, .06, .52)
    cart_door(m, f, dw, .95)
    cart_door(m, f, de, 1.25)
    for h in gw_w + gw_e + ups_w + ups_e:
        window(m, f, h, occupied='dispatch' if h['z'] < 4 else 'loft')
    for h in bays_w + bays_e:
        loading_bay(m, f, h)
    for k in (1, 2, 3):
        anchors(m, (X0 + .9, XRW - 1.75, XRW + 1.75, XM - .5, XM + .6, XRE - 1.75, XRE + 1.75, X1 - .9), FL[k] - .05)
    anchors(m, (X0 + .9, XM - .5, XM + .6, X1 - .9), EAVE - .5)
    m.box('hardware', XM, -.09, EAVE / 2 + .3, .12, .12, EAVE - .4)                          # downpipe from the valley
    m.flush('south')
    C.prism('South gables', gable_outline(notches=True), 'y', Y0, Y0 + T, 'wall', 'gables')
    b = Batch()
    gable_dressing(b, Y0 + T / 2)
    b.flush('south gables')


def side_and_rear():
    hd = (Y1 - Y0) / 2
    e = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    bays = (-6.0, -4.0, -2.0, 0.0, 2.0, 4.0, 6.0)
    ups = [hole(f'east window f{k} {i}', u, FL[k] + .8, .8, 1.45) for k in (1, 2) for i, u in enumerate(bays)] + \
          [hole(f'east window f3 {i}', u, FL[3] + .05, .7, .6) for i, u in enumerate(bays)]
    gd = [hole('east door', 0.0, 0.0, 1.2, 2.7, kind='door')]
    gw = [hole(f'east ground window {i}', u, .95, 1.0, 2.2) for i, u in enumerate(bays) if u != 0.0]
    hs = ups + gd + gw
    e.wall('east carrier', -hd + T, hd - T, 0.0, EAVE, depth=T, role='wall', holes=hs)
    G.brick_courses(e, -hd + T + .02, hd - T - .02, .55, EAVE - .02, hs, spacing=.2)
    m = Merge(e)
    m.box('foundation', 0, -.03, .26, 2 * hd - 2 * T - .02, .06, .52)
    for h in ups + gw:
        window(m, e, h, rise=.12 if h['h'] < 1 else (.16 if h['h'] < 2 else .3), occupied='dispatch' if h['z'] < 4 else 'loft', ring=.2 if h['h'] < 1 else .26)
    m.box('timber', 0.0, .16, 1.35, 1.18, .06, 2.68)
    register(e, gd[0], .14, 'side door', 'dispatch')
    arch_head(e, gd[0], .35)
    for k in (1, 2, 3):
        anchors(m, (-7.0, -5.0, -3.0, -1.0, 1.0, 3.0, 5.0, 7.0), FL[k] - .05)
    m.box('white', 0.0, -.155, EAVE - .5, 2 * hd + .1, .28, .4)                               # timber cornice tucked under the eave
    m.flush('east')
    w = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west party')
    w.wall('west party wall', -hd + T, hd - T, 0.0, EAVE, depth=T, role='wall', holes=[])
    n = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')
    us = (-7.0, -4.0, -1.0, 2.5, 5.5, 8.0)
    hs = [hole(f'rear window f{k} {i}', u, FL[k] + .8, .8, 1.45) for k in (1, 2) for i, u in enumerate(us)] + \
         [hole(f'rear window f3 {i}', u, FL[3] + .05, .7, .6) for i, u in enumerate(us)] + \
         [hole(f'rear ground window {i}', u, .95, 1.0, 2.0) for i, u in enumerate((-7.0, -1.0, 5.5))] + [hole('rear door', 2.5, 0.0, 1.8, 3.0, kind='door')]
    n.wall('north carrier', -X1, -X0 - EPS, 0.0, EAVE, depth=T, role='wall', holes=hs)
    G.brick_courses(n, -X1 + .02, -X0 - .02, .55, EAVE - .02, hs, spacing=.2)
    m = Merge(n)
    for k in (1, 2, 3):
        anchors(m, (-8.5, -5.5, -2.5, 1.0, 4.0, 6.8, 9.2), FL[k] - .05)
    m.box('foundation', 0, -.03, .26, X1 - X0 - .02, .06, .52)
    for h in hs:
        if h.get('kind') == 'door':
            m.box('timber', h['u'], .16, h['h'] / 2, h['w'] - .02, .06, h['h'] - .02)
            register(n, h, .14, 'rear cart door', 'dispatch')
            arch_head(n, h, .9, ring=.32)
        else:
            window(m, n, h, rise=.12 if h['h'] < 1 else (.16 if h['h'] < 1.8 else .3), occupied='loft', ring=.2 if h['h'] < 1 else .26)
    m.flush('north')
    C.prism('North gables', rear_outline(), 'y', Y1 - T, Y1, 'wall', 'gables')
    b = Batch()
    out = rear_outline()
    for i, ((xa, za), (xb, zb)) in enumerate(zip(out[1:-2], out[2:-1])):
        b.beam('stone', (xa, Y1 - T / 2, za + .05), (xb, Y1 - T / 2, zb + .05), T + (.12 if i % 2 else .16), .14 + .02 * (i % 2), ext=.08)
    b.flush('north gables')


def roof_and_inside():
    y0, y1 = Y0 + T + .01, Y1 - T - .01
    ov = .3
    for name, xa, xb, ridge in (('West roof', X0, XM, RW), ('East roof', XM, X1, RE)):
        xm = (xa + xb) / 2
        lower = [(xa - (ov if xa != XM else 0.0), y0), (xb + (ov if xb != XM else 0.0), y0), (xb + (ov if xb != XM else 0.0), y1), (xa - (ov if xa != XM else 0.0), y1)]
        upper = [(xm, y0), (xm, y0), (xm, y1), (xm, y1)]
        strip(name, lower, upper, EAVE - ov * SLOPE, ridge, 'roof', 'roof')
    # Behind the valley the inner slopes give way to a flat deck; a hipped plate climbs from the valley to it.
    yv, ys = Y0 + T + 1.2, Y0 + T + 1.2 + (RW - EAVE) / SLOPE
    xd = XRE - (RE - RW) / SLOPE
    zt = RW + .01                                                                             # the hip plate and deck stand just proud of the slopes
    vs = [(XRW, ys, zt), (xd, ys, zt), (XM, yv, EAVE + .04), (XRW, ys, zt - .2), (xd, ys, zt - .2), (XM, yv + .14, EAVE - .1)]
    C.mesh('Valley hip', vs, [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)], 'roof', 'roof')
    C.box('Roof deck', ((XRW + xd) / 2, (ys + y1) / 2, zt - .1), (xd - XRW, y1 - ys, .2), 'membrane', 'roof', 0)
    b = Batch()
    for k, y in enumerate((-.5, 1.2, 2.9, 4.6)):                                              # round deck vents (octagonal stand-ins)
        b.box('pale', XRW + 2.5, y, zt + .25, .5, .5, .5)
        b.box('hardware', XRW + 2.5, y, zt + .54, .62, .62, .08)
    b.box('pale', XRW + 2.2, 6.3, zt + .2, 1.6, 1.0, .4)                                       # rear roof light
    b.box('glass', XRW + 2.2, 6.3, zt + .42, 1.4, .8, .05)
    for (cx, cy) in ((XRW - 1.0, Y0 + 3.0), (XRE + 1.5, 4.5)):
        zr = (RW if cx < XM else RE) - abs(cx - (XRW if cx < XM else XRE)) * SLOPE
        chimney(b, cx, cy, zr - .4, zr + 1.3, w=.8, d=.6, pots=0)
    chimney(b, XRW + 1.2, 3.6, zt - .05, zt + 1.4, w=.8, d=.6, pots=0)                       # a stack standing on the deck
    # East-slope dormer: a white body facing east with a glazed front and a small pitched cap.
    dx, dy = X1 - 2.0, 1.5
    zf = EAVE + 2.0 * SLOPE
    b.box('glass', dx + .02, dy, zf + .5, .02, .9, .8)
    b.flush('roof furniture')
    C.box('Dormer body', (dx - .8, dy, zf + .45), (1.6, 1.4, 1.3), 'white', 'roof', 0)
    C.prism('Dormer cap', [(dy - .85, zf + 1.1), (dy + .85, zf + 1.1), (dy, zf + 1.65)], 'x', dx - 1.6, dx + .15, 'roof', 'roof')
    b = Batch()
    for x, ridge in ((X0 - ov - .08, None), (X1 + ov + .08, None)):
        b.box('hardware', x, 0.0, EAVE - ov * SLOPE + .02, .16, Y1 - Y0 - .1, .14)
    b.flush('gutters')
    for z in FL[1:] + [EAVE]:
        C.box(f'Floor {z:.1f}', (0, 0, z - .12), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .24), 'floor', 'inside', 0)
    C.box('Section wall', (XM, 0, EAVE / 2), (.3, Y1 - Y0 - 2 * T, EAVE - .02), 'interior', 'inside', 0)
    for k in range(4):
        for x in (XRW, XRE):
            C.qa_room_light(f'Loft {k} {x:.0f}', (x, Y0 + 2.4, FL[k] + 2.0), 45, 2.4)
    C.CONTACTS.append(dict(name='Brick walls from grade; coped twin gables on the quay and rear walls; roofs between them; deck between the ridges', eave_m=EAVE))


def site():
    QD, ES = 3.5, 4.0                                                                        # quay depth and street width (top view)
    xe = X1 + ES                                                                             # the east quay line
    C.box('Quay paving', ((X0 - 14.0 + xe) / 2, Y0 - QD / 2, .02), (xe - X0 + 14.0, QD, .04), 'paving', 'site', 0)
    C.box('East street', (X1 + ES / 2, (Y0 + Y1 + 14.0) / 2, .02), (ES, Y1 + 14.0 - Y0, .04), 'setts', 'site', 0)
    yc = Y0 - QD - .5                                                                        # south canal edge
    C.box('South canal', ((X0 - 14.0 + xe + .5) / 2, yc - 7.0, .005), (xe + .5 - X0 + 14.0, 14.0, .01), 'water', 'site', 0)
    C.box('East canal', (xe + .5 + 7.0, (yc - 14.0 + Y1 + 14.0) / 2, .005), (14.0, Y1 + 14.0 - yc + 14.0, .01), 'water', 'site', 0)
    b = Batch()
    b.box('brick', (X0 - 14.0 + xe + .5) / 2, Y0 - QD - .25, .3, xe + .5 - X0 + 14.0, .5, .56)  # low brick quay parapets that butt at the corner
    b.box('stone', (X0 - 14.0 + xe + .56) / 2, Y0 - QD - .25, .63, xe + .56 - X0 + 14.0, .62, .1)
    b.box('brick', xe + .25, (Y0 - QD + Y1 + 14.0) / 2, .3, .5, Y1 + 14.0 - Y0 + QD, .56)
    b.box('stone', xe + .25, (Y0 - QD + .06 + Y1 + 14.0) / 2, .63, .62, Y1 + 14.0 - Y0 + QD - .06, .1)
    for k in range(int((xe - X0 + 14.0) / .75)):
        b.box('joint', X0 - 14.0 + .375 + k * .75, Y0 - QD / 2, .042, .02, QD - .02, .004)
    for k in range(int((Y1 + 14.0 - Y0) / .75)):
        b.box('joint', X1 + ES / 2, Y0 + .375 + k * .75, .042, ES - .02, .02, .004)
    b.box('hardware', X0 - 1.5, Y0 - 2.8, 1.8, .12, .12, 3.6)                                # lamp standard
    b.box('hardware', X0 - 1.5, Y0 - 2.8, 3.85, .32, .32, .5)
    b.box('timber', xe + 6.0, 6.0, .45, 2.6, 13.0, .8)                                      # moored barge
    b.box('hardware', xe + 6.0, 8.5, 1.2, 2.0, 4.5, .9)
    b.flush('quay')
    street_tree(X0 - 5.0, Y0 - 1.9, z=.04, height=9.0, spread=2.4)
    # The attached gabled canal house to the west, as context: set back 10 cm, its east wall buried in ours.
    nx0, nx1 = X0 - 6.4, X0 + .15
    C.box('Neighbour house', ((nx0 + nx1) / 2, Y0 + 5.6, 5.25), (nx1 - nx0, 11.0, 10.5), 'neighbour', 'context', 0)
    C.prism('Neighbour gable', [(nx0, 10.5), (nx1, 10.5), ((nx0 + nx1) / 2, 14.0)], 'y', Y0 + .1, Y0 + 11.0, 'neighbour', 'context')
    b = Batch()
    for k in range(3):
        for u in (nx0 + 1.4, nx0 + 3.2, nx0 + 5.0):
            b.box('glass', u, Y0 + .08, 1.2 + k * 2.9 + .8, .9, .04, 1.5)
            b.box('white', u, Y0 + .07, 1.2 + k * 2.9 + .02, 1.1, .06, .1)
    b.box('glass', (nx0 + nx1) / 2, Y0 + .08, 11.6, .8, .04, 1.1)
    b.flush('neighbour')


def build():
    site()
    south_face()
    side_and_rear()
    roof_and_inside()
    C.CONTACTS.append(dict(name='Twin-gabled corner warehouse on a canal quay with a side street east', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(30, -45, 40), fill=(-40, -20, 30), rear=(-15, 35, 30), target=(0, 0, 8.0), gain=5.0)
