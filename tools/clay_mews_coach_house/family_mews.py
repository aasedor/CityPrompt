"""London mews coach house, authored from the locked catalogue views of
london_mews_house / variant_0 (original stable conversion).

Read from the pixels (the top view governs the plan): the end house of a two-storey mews row on a street
corner, the cobbled mews south and a side street east. Painted white brick over a black plinth, a thin
white eaves band under a black gutter, a slate roof hipped at the corner end. On the south face a wide red
vertical-boarded coach-house door with a glazed transom, a white panelled front door with a fanlight, and
six-over-six sash windows on the upper floor; the attached white neighbour to the west carries the same
windows. Brick chimney stacks with clay pots on the party walls, two small skylights on the rear slope, a
plane tree and a black lamp standard on the pavement.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-mews-coach-house'
X0, X1, Y0, Y1 = -6.6, 8.6, -3.7, 3.7          # neighbour (x < 0) and the end house (x >= 0), 7.4 m deep
XN = 0.0                                        # party wall between the neighbour and the end house
T = .30
G0 = .15
Z1 = 3.6                                        # first floor, above the coach-door transom
EAVE = 7.4
RISE = 2.3                                      # hipped slate roof
EPS = .002
PALETTE = dict(wall=(.93, .93, .91), joint=(.89, .89, .87), settjoint=(.60, .59, .57), trim=(.95, .95, .94), pale=(.88, .88, .86),
    stone=(.74, .73, .70), roof=(.34, .36, .39), sand=(.70, .68, .64), foundation=(.14, .14, .15),
    glass=(.30, .36, .40), hardware=(.10, .10, .11), interior=(.86, .82, .76), floor=(.62, .56, .48),
    timber=(.48, .34, .22), blue=(.20, .30, .40), planting=(.30, .44, .20), soil=(.22, .16, .10),
    concrete=(.70, .69, .66), white=(.96, .96, .95), asphalt=(.28, .28, .29), door=(.56, .10, .08),
    brick=(.70, .58, .42), pot=(.76, .42, .26), setts=(.36, .35, .34), paving=(.72, .71, .68))


def manifest(version):
    h = EAVE + RISE + 1.4
    cams = G.camera_roster(X1 - X0 + 3.0, Y1 - Y0 + 3.0, h, [
        ('facade_close', (3.0, -16.0, 3.8), (3.0, Y0, 3.8), 45),
        ('architecture_close', (14.0, -11.0, 7.5), (X1, Y0, 6.4), 45),
        ('glass_close', (3.0, -7.0, 5.3), (3.0, Y0, 5.3), 45),
        ('coach_door', (2.85, -8.5, 1.9), (2.85, Y0, 1.9), 40),
        ('front_door', (6.6, -5.5, 1.6), (6.4, Y0, 1.7), 40),
        ('roof_chimneys', (2.0, -16.0, 14.0), (2.0, 0.0, EAVE + 1.5), 40),
        ('east_side', (19.0, 1.0, 4.2), (X1, 0.0, 4.2), 40),
        ('eaves_corner', (11.5, -7.5, 9.0), (X1, Y0, EAVE), 40),
        ('interior', (6.6, 2.6, Z1 + 1.6), (2.0, Y0, Z1 + 1.5), 40),
        ('rear_north', (1.0, 18.0, 5.0), (1.0, Y1, 5.0), 45)])
    for c in cams:                       # the locked front and oblique look from the south-east
        if c['name'] == 'front':
            c['location'] = (13.5, -15.0, 1.6); c['target'] = (1.0, -2.0, 4.2); c['lens'] = 28; c['whole'] = False
        elif c['name'] == 'front_corner':
            lx, ly, lz = c['location']; c['location'] = (-lx, ly, lz)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='london_mews_house/variant_0 (london-mews-house-original-stable)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=2, storey_programme='coach house and hall on the ground floor, living rooms above; the attached neighbour the same',
            plan='8.6 x 7.4 m end house and a 6.6 m attached neighbour (top view); hipped at the corner end, party gable west',
            facade='painted white brick on a black plinth; red boarded coach door with glazed transom; panelled front door with fanlight; six-over-six sashes',
            levels_m=[G0, Z1, EAVE], roof_m=dict(eave=EAVE, ridge=EAVE + RISE),
            inferred='interiors and the rear face are teaching assumptions; the rear repeats the visible grammar'),
        roof_contract=dict(type='slate roof hipped at the corner end with chimney stacks and two rear skylights', datum_m=EAVE, crowns_m=[EAVE + RISE]),
        identity_contract=dict(owner='white-painted brick mews house with red coach-house door, sash windows, hipped slate roof and chimney pots on a cobbled mews'),
        material_contract=dict(profile='source-palette clay: white paint, black plinth and gutter, red boarded door, grey slate, stock-brick stacks with orange pots, granite setts', textured_keeper=False),
        programme_contract=dict(storeys=2, ground='coach house (garage) and hall', upper='living rooms'),
        contact_contract=['Grade-zero setts and pavements', 'Walls on a black plinth', 'Roof on the eaves band', 'Stacks on the party walls'],
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


# ---- London mews coach house ----

UP = Z1 + .7                                    # upper sill line


def arch_head(f, h, rise, ring=.26, segs=10, ring_role='arch', spandrel=True):
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
    if spandrel:
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


def round_pots(name, centres, z0, h=.78, r=.13, sides=10):
    """Tall round terracotta pots, each a closed cylinder with a slightly wider rim band, merged into one mesh."""
    vs, fs = [], []
    for (px, py) in centres:
        for (za, zb, rr) in ((z0, z0 + h - .08, r), (z0 + h - .08, z0 + h, r + .025)):
            o = len(vs)
            for zz in (za, zb):
                for k in range(sides):
                    a = 2 * math.pi * k / sides
                    vs.append((px + rr * math.cos(a), py + rr * math.sin(a), zz))
            for k in range(sides):
                k2 = (k + 1) % sides
                fs.append((o + k, o + k2, o + sides + k2, o + sides + k))
            fs.append(tuple(o + k for k in range(sides))[::-1])
            fs.append(tuple(o + sides + k for k in range(sides)))
    C.mesh(name, vs, fs, 'pot', 'roof')


def sash(m, f, h, occupied='room', lite=False):
    """Six-over-six sash: each sash three lights by two, a heavier meeting rail, a dark sill below."""
    framed(m, f, h, cols=3, rows=4, inset=.12, occupied=occupied, lite=lite)
    if not lite:
        m.box('trim', h['u'], .1, h['z'] + h['h'] / 2, h['w'] - .1, .1, .08)
    m.box('hardware', h['u'], -.04, h['z'] - .06, h['w'] + .14, .14, .1)


def paired(m, f, h, occupied='room'):
    """Two sashes in one opening split by a dark central mullion."""
    w = (h['w'] - .12) / 2
    for s in (-1, 1):
        sub = dict(h, id=h['id'] + (' west' if s < 0 else ' east'), u=h['u'] + s * (w / 2 + .06), w=w)
        framed(m, f, sub, cols=3, rows=4, inset=.12, occupied=occupied)
        m.box('trim', sub['u'], .1, h['z'] + h['h'] / 2, w - .1, .1, .08)
    m.box('hardware', h['u'], .1, h['z'] + h['h'] / 2, .12, .14, h['h'])
    m.box('hardware', h['u'], -.04, h['z'] - .06, h['w'] + .14, .14, .1)


def face_courses(f, lo, hi, holes, heads=True, course=.08, brick=.24, top=None):
    """Painted brick: fine bed joints and staggered head joints, cut round the openings."""
    lo, hi, z0, z1 = lo + .02, hi - .02, G0 + .35, (top or EAVE) - .35
    G.brick_courses(f, lo, hi, z0, z1, holes, spacing=course)
    if not heads:
        return
    vs, fs = [], []
    for row in range(int((z1 - z0) / course)):
        zb = z0 + row * course
        u = lo + brick + (brick / 2) * (row % 2)
        while u < hi - .02:
            if not any(h['u'] - h['w'] / 2 - .02 < u < h['u'] + h['w'] / 2 + .02 and h['z'] - .1 < zb + course and zb < h['z'] + h['h'] + .1 for h in holes):
                o = len(vs)
                vs += [f.p(u - .004, -.002, zb), f.p(u + .004, -.002, zb), f.p(u + .004, -.002, zb + course), f.p(u - .004, -.002, zb + course)]
                fs.append((o, o + 1, o + 2, o + 3))
            u += brick
    if fs:
        C.mesh(f.label + ' head joints', vs, fs, 'joint', 'brick joints')


def south_face():
    f = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south')
    coach = hole('coach door', 2.85, G0, 4.4, 2.38, kind='coach door')
    transom = hole('coach transom', 2.85, G0 + 2.46, 4.4, .5)
    door = hole('front door', 6.35, G0, 1.05, 2.42, kind='door')
    fan = hole('front fanlight', 6.35, G0 + 2.5, 1.05, .46)
    pair = hole('upper paired sash', 1.65, UP, 1.8, 2.05)
    ups = [hole('upper sash middle', 4.15, UP, 1.05, 2.05), hole('upper sash east', 6.6, UP, 1.25, 2.15)]
    nb = [hole('neighbour door', -5.7, G0, 1.0, 2.42, kind='door'), hole('neighbour fanlight', -5.7, G0 + 2.5, 1.0, .46),
          hole('neighbour ground sash', -3.9, G0 + .75, 1.0, 2.0), hole('neighbour ground paired sash', -1.6, G0 + .75, 1.6, 2.1),
          hole('neighbour upper sash west', -3.9, UP, 1.0, 1.95), hole('neighbour upper sash east', -1.6, UP, 1.05, 1.95)]
    holes = [coach, transom, door, fan, pair] + ups + nb
    f.wall('south carrier', X0, X1 - EPS, 0.0, EAVE, depth=T, role='wall', holes=holes)
    face_courses(f, X0, X1, holes)
    m = Merge(f)
    m.box('foundation', (X0 + X1) / 2, -.03, .16, X1 - X0 - .02, .06, .32)                  # black plinth
    m.box('trim', (X0 + X1) / 2 + .03, -.04, Z1 - .12, X1 - X0 + .06, .08, .1)                     # first-floor string course
    # Red boarded coach door in a shallow reveal, transom of three groups of small lights above.
    m.box('door', coach['u'], .14, coach['z'] + coach['h'] / 2, coach['w'] - .02, .06, coach['h'] - .02)
    for k in range(1, 16):
        m.box('hardware', coach['u'] - coach['w'] / 2 + coach['w'] * k / 16, .105, coach['z'] + coach['h'] / 2, .018, .012, coach['h'] - .08)
    m.box('trim', coach['u'], .1, coach['z'] + coach['h'] + .04, coach['w'] + .02, .12, .08)
    framed(m, f, transom, cols=15, rows=1, inset=.12, occupied='coach house')
    for s in (-1, 1):
        m.box('trim', coach['u'] + s * coach['w'] / 6, .1, transom['z'] + transom['h'] / 2, .09, .1, transom['h'])
    register(f, coach, .12, 'coach-house door', 'coach house')
    for d, fl in ((door, fan), (nb[0], nb[1])):
        m.box('white', d['u'], .14, d['z'] + d['h'] / 2, d['w'] - .02, .05, d['h'] - .02)          # six-panel door leaf
        for zz in (.45, 1.15, 1.9):
            for s in (-1, 1):
                m.box('trim', d['u'] + s * .22, .108, d['z'] + zz, .32, .012, .5 if zz < 1.8 else .7)
        m.box('hardware', d['u'], .1, d['z'] + 1.55, .1, .04, .14)                            # knocker, knob, letterbox
        m.box('hardware', d['u'] + .3, .1, d['z'] + 1.05, .06, .04, .06)
        m.box('hardware', d['u'], .1, d['z'] + .95, .3, .04, .06)
        register(f, d, .12, 'entry door', 'hall')
        framed(m, f, fl, cols=1, rows=1, inset=.12, occupied='hall')
    paired(m, f, pair)
    for h in ups + [nb[2], nb[4], nb[5]]:
        sash(m, f, h)
    paired(m, f, nb[3])
    for h in [pair] + ups + [nb[4], nb[5]]:     # rectangular sashes under a shallow flush gauged arch (rise 0.1 of span), brick tympanum
        r = .1 * h['w']
        arch_head(f, dict(h, h=h['h'] + r), r, ring=.12, segs=8, ring_role='trim', spandrel=False)
    m.box('hardware', XN - .35, -.06, EAVE / 2, .1, .1, EAVE - .2)                              # downpipe by the party wall
    m.flush('south')


def other_faces():
    e = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    hd = (Y1 - Y0) / 2
    hs = [hole('east ground sash', 0.0, G0 + .9, 1.0, 2.0), hole('east upper sash', 0.0, UP, 1.0, 2.05)]   # one column (front, oblique)
    e.wall('east carrier', -hd + T, hd - T, 0.0, EAVE, depth=T, role='wall', holes=hs)
    face_courses(e, -hd + T, hd - T, hs)
    m = Merge(e)
    m.box('foundation', 0, -.03, .16, 2 * hd - 2 * T - .02, .06, .32)
    m.box('trim', -.04, -.04, Z1 - .12, 2 * hd + .08, .08, .1)
    for h in hs:
        sash(m, e, h)
    m.box('hardware', -hd + .5, -.06, EAVE / 2, .1, .1, EAVE - .2)
    m.flush('east')
    n = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')
    hs = [hole(f'rear sash {k}', u, UP, 1.0, 1.95) for k, u in enumerate((-7.6, -4.6, -1.6))] + \
         [hole(f'rear ground sash {k}', u, G0 + .9, 1.0, 1.9) for k, u in enumerate((-7.6, -1.6))] + [hole('rear door', -4.6, G0, 1.0, 2.3, kind='door')]
    n.wall('north carrier', -X1, -X0 - EPS, 0.0, EAVE, depth=T, role='wall', holes=hs)
    face_courses(n, -X1, -X0, hs, heads=False)
    m = Merge(n)
    m.box('foundation', -(X0 + X1) / 2, -.03, .16, X1 - X0 - .02, .06, .32)
    for h in hs:
        if h.get('kind') == 'door':
            framed(m, n, h, cols=2, rows=3, inset=.12, occupied='hall', kind='door', lite=True)
        else:
            sash(m, n, h)
    m.flush('north')
    w = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west party')
    w.wall('west party wall', -hd + T, hd - T, 0.0, EAVE, depth=T, role='wall', holes=[])


def upstand(name, x0, x1):
    """Coped brick party-wall upstand standing above the slates, corbelled past the eaves, hiding the roof ends."""
    pts = [(Y0 - .4, EAVE - .14), (Y0 - .4, EAVE + .2), (0.0, EAVE + RISE + .4), (Y1 + .4, EAVE + .2), (Y1 + .4, EAVE - .14)]
    C.prism(name, pts, 'x', x0, x1, 'brick', 'party walls')
    b = Batch()
    xm = (x0 + x1) / 2
    for i, (a, c) in enumerate(((pts[1], pts[2]), (pts[2], pts[3]))):
        b.beam('stone', (xm, a[0], a[1] + .05), (xm, c[0], c[1] + .05), x1 - x0 + (.1 if i else .14), .1 + .02 * i, ext=.05)
    b.flush(name)


def roof_and_inside():
    b = Batch()
    # White dentilled eaves band under the black gutter on the corner house's three street sides.
    for (cx, cy, sx, sy) in (((XN + X1) / 2 + .1, Y0 - .06, X1 - XN + .04, .12), (X1 + .06, 0.0, .12, Y1 - Y0)):
        b.box('white', cx, cy, EAVE - .14, sx, sy, .28)
    for k in range(int((X1 - XN) / .3)):
        b.box('white', XN + .3 + k * .3, Y0 - .16, EAVE - .2, .12, .08, .1)
    for k in range(int((Y1 - Y0) / .3)):
        b.box('white', X1 + .16, Y0 + .3 + k * .3, EAVE - .2, .08, .12, .1)
    b.box('white', (X0 + XN) / 2, Y0 - .06, EAVE - .14, XN - X0 - .04, .12, .28)
    ov, hd = .3, (Y1 - Y0) / 2
    slope = RISE / hd
    zg = EAVE - ov * slope + .02
    b.box('hardware', (X0 + X1 + .37) / 2, Y0 - .3, zg, X1 + .37 - X0, .14, .12)                # gutters, run on round the corner
    b.box('hardware', X1 + .3, (Y0 - .23 + Y1 + .37) / 2, zg, .14, Y1 - Y0 + .6, .12)
    for ga, gb in ((X0, -5.6 - .35), (-1.0 + .35, X1)):                        # rear gutter, broken by the back wing
        b.box('hardware', (ga + gb) / 2, Y1 + .3, zg, gb - ga, .14, .12)
    b.flush('eaves')
    # Two independent slate roofs between the party walls: the corner house hipped at the east end.
    xe = XN + .2
    strip('Corner house roof', [(xe, Y0 - ov), (X1 + ov, Y0 - ov), (X1 + ov, Y1 + ov), (xe, Y1 + ov)],
          [(xe, 0.0), (X1 - hd, 0.0), (X1 - hd, 0.0), (xe, 0.0)], EAVE - ov * slope, EAVE + RISE, 'roof', 'roof')
    strip('Neighbour roof', [(X0 + .2, Y0 - ov), (XN - .2, Y0 - ov), (XN - .2, Y1 + ov), (X0 + .2, Y1 + ov)],
          [(X0 + .2, 0.0), (XN - .2, 0.0), (XN - .2, 0.0), (X0 + .2, 0.0)], EAVE - ov * slope, EAVE + RISE, 'roof', 'roof')
    upstand('Party upstand', XN - .25, XN + .25)
    upstand('West party upstand', X0 - .02, X0 + .43)
    b = Batch()
    # One long stack on the end-house/neighbour party wall, running from just in front of the ridge back down the
    # rear slope in two steps: five tall round pots on the ridge section, four on the rear section (top source).
    # The west party wall stays a coped parapet with no stack.
    za, zb, zc = EAVE + RISE + 1.25, EAVE + RISE + .6, EAVE + .2
    secs = ((-.55, 1.15, za, 5), (1.15, 3.05, zb, 4))
    pots = []
    for i, (y0, y1, zt, n) in enumerate(secs):
        b.box('brick', XN, (y0 + y1) / 2, (zc + zt) / 2, .82, y1 - y0 + (.02 if i == 0 else 0), zt - zc)
        b.box('stone', XN, (y0 + y1) / 2, zt + .05, .94, y1 - y0 + .12, .1)
        b.box('brick', XN, (y0 + y1) / 2, zt - .32, .9, y1 - y0 + .08, .08)       # oversailing course below the cap
        rows = (((-.2, .2), (-.2, .2), (0.0,)) if n == 5 else ((-.2, .2), (-.2, .2)))   # clusters of 5 and 4 pots
        yc = y0 + .45 if i == 0 else y1 - .75
        pots += [(XN + dx, yc + .36 * r, zt + .1) for r, row in enumerate(rows) for dx in row]
    for zt in (za, zb):
        round_pots(f'Chimney pots {zt:.1f}', [(px, py) for (px, py, z) in pots if abs(z - zt - .1) < 1e-6], zt + .1)
    for x in (-1.5, -3.3):                                                    # two rooflights on the neighbour's front slope, west of the stack
        za, zb = (EAVE + RISE * (1 - y / hd) for y in (2.3, 1.5))
        b.beam('hardware', (x, -2.3, za + .05), (x, -1.5, zb + .05), .9, .08)
        b.beam('glass', (x, -2.25, za + .1), (x, -1.55, zb + .1), .78, .02)
    for s in (-1, 1):                                                         # hip and ridge cappings
        b.beam('pot', (X1 - hd, 0.0, EAVE + RISE + .03), (X1 + ov, s * (hd + ov), EAVE - ov * slope + .03), .12, .08)
    b.beam('pot', (xe, 0.0, EAVE + RISE + .04), (X1 - hd, 0.0, EAVE + RISE + .04), .14, .08)
    b.beam('pot', (X0 + .2, 0.0, EAVE + RISE + .04), (XN - .2, 0.0, EAVE + RISE + .04), .14, .08)
    b.flush('roof furniture')
    # The neighbour's hipped rear back-wing: a hollow two-storey wing about 70% of the bay wide, centred on it, its
    # ridge climbing out of the main rear slope at mid-height (two valleys) and running north to a hipped end.
    wx0, wx1, wy1, we, wr, ov = -5.6, -1.0, Y1 + 3.2, 6.4, 2.15, .25
    wn = C.Face((0, wy1, 0), (-1, 0, 0), (0, -1, 0), 'wing north')
    nh = [hole('wing north ground sash', 3.3, G0 + .9, .95, 1.8), hole('wing north upper sash', 3.3, Z1 + .5, .95, 1.75)]
    wn.wall('wing north carrier', -wx1, -wx0, 0.0, we, depth=T, role='wall', holes=nh)
    we_ = C.Face((wx1, 0, 0), (0, 1, 0), (-1, 0, 0), 'wing east')
    eh = [hole('wing east ground sash', Y1 + 1.55, G0 + .9, .95, 1.8), hole('wing east upper sash', Y1 + 1.55, Z1 + .5, .95, 1.75)]
    we_.wall('wing east carrier', Y1 - .01, wy1 - T, 0.0, we, depth=T, role='wall', holes=eh)
    ww = C.Face((wx0, 0, 0), (0, -1, 0), (1, 0, 0), 'wing west')
    ww.wall('wing west carrier', -(wy1 - T), -(Y1 - .01), 0.0, we, depth=T, role='wall', holes=[])
    for f, lo, hi, hs in ((wn, -wx1, -wx0, nh), (we_, Y1, wy1 - T, eh)):
        face_courses(f, lo, hi, hs, heads=False, top=we)
        m = Merge(f)
        m.box('foundation', (lo + hi) / 2, -.03, .16, hi - lo - .02, .06, .32)
        for h in hs:
            sash(m, f, h)
        m.flush(f.label)
    C.box('Wing first floor', ((wx0 + wx1) / 2, (Y1 + wy1 - T) / 2, Z1 - .12), (wx1 - wx0 - 2 * T, wy1 - Y1 - T, .24), 'floor', 'inside', 0)
    C.box('Wing ceiling', ((wx0 + wx1) / 2, (Y1 + wy1 - T) / 2, we - .12), (wx1 - wx0 - 2 * T + .02, wy1 - Y1 - T + .02, .24), 'floor', 'inside', 0)
    half = (wx1 - wx0) / 2
    yr = hd * (1 - (we + wr - EAVE) / RISE)             # where the wing ridge meets the main rear slope
    pitched_roof('Neighbour back wing roof', wx0, wx1, yr + ov, wy1, we, wr, hip_w=False, hip_e=True, axis='y', ov=ov)
    b = Batch()
    xm, zr, ze = (wx0 + wx1) / 2, we + wr, we - ov * wr / half
    b.beam('pot', (xm, yr, zr + .04), (xm, wy1 - half, zr + .04), .14, .08)
    for s in (-1, 1):
        b.beam('pot', (xm, wy1 - half, zr + .03), (xm + s * (half + ov), wy1 + ov, ze + .03), .12, .08)
        b.box('hardware', xm + s * (half + ov + .05), (Y1 + .45 + wy1 + ov) / 2, ze - .02, .14, wy1 + ov - Y1 - .45, .12)
    b.box('hardware', xm, wy1 + ov + .05, ze - .02, wx1 - wx0 + 2 * ov + .2, .14, .12)
    py, px = wy1 - .3, wx1 + .08                                              # downpipe 3 cm off the wing's east face
    b.box('hardware', wx1 + ov + .05, py, ze - .12, .12, .12, .14)                 # outlet under the gutter
    b.beam('hardware', (wx1 + ov + .05, py, ze - .17), (px, py, ze - .55), .1, .1)  # swan-neck back to the wall
    b.box('hardware', px, py, (ze - .55 + .14) / 2, .1, .1, ze - .55 - .14)
    b.beam('hardware', (px, py, .26), (px + .14, py, .06), .1, .1)                  # shoe
    for z in (1.2, 3.0, 4.8):
        b.box('hardware', wx1 + .02, py, z, .06, .14, .05)                        # wall clips
    b.flush('neighbour back wing')
    C.box('Ground floor slab', ((X0 + X1) / 2, 0, G0 / 2 + .05), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, G0 + .1), 'floor', 'inside', 0)
    C.box('First floor', ((X0 + X1) / 2, 0, Z1 - .12), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .24), 'floor', 'inside', 0)
    C.box('Ceiling', ((X0 + X1) / 2, 0, EAVE - .12), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .24), 'floor', 'inside', 0)
    C.box('Party wall', (XN, 0, EAVE / 2), (.2, Y1 - Y0 - 2 * T, EAVE - .02), 'interior', 'inside', 0)
    for x in (2.6, 6.4, -3.0):
        C.qa_room_light(f'Room {x:.0f}', (x, 0.0, Z1 + 2.2), 50, 2.5)
    C.qa_room_light('Coach house', (3.0, 0.0, 2.4), 40, 2.5)
    C.qa_room_light('Neighbour ground', (-3.0, 0.0, 2.2), 40, 2.5)
    C.CONTACTS.append(dict(name='Painted brick walls on a black plinth; two slate roofs between coped party upstands carrying the stacks', eave_m=EAVE))


def setts(b, x0, x1, y0, y1, along='x', L=.3, W=.18):
    """Granite setts in staggered courses: continuous course joints, staggered cross joints every stone length."""
    if along == 'x':
        for r in range(int((y1 - y0) / W) + 1):
            y = y0 + r * W
            b.box('settjoint', (x0 + x1) / 2, y, .041, x1 - x0 - .02, .014, .004)
            x = x0 + L * (.5 * (r % 2) + 1)
            while x < x1 - .05 and r * W + W <= y1 - y0:
                b.box('settjoint', x, y + W / 2, .041, .014, W - .01, .004)
                x += L
    else:
        for r in range(int((x1 - x0) / W) + 1):
            x = x0 + r * W
            b.box('settjoint', x, (y0 + y1) / 2, .041, .014, y1 - y0 - .02, .004)
            y = y0 + L * (.5 * (r % 2) + 1)
            while y < y1 - .05 and r * W + W <= x1 - x0:
                b.box('settjoint', x + W / 2, y, .041, W - .01, .014, .004)
                y += L


def site():
    yp = Y0 - 1.8
    C.box('South pavement west', ((X0 - 6.0 + .6) / 2, (yp + Y0) / 2, .06), (.6 - X0 + 6.0, Y0 - yp, .12), 'paving', 'site', 0)
    C.box('South pavement east', ((5.1 + X1 + 1.8) / 2, (yp + Y0) / 2, .06), (X1 + 1.8 - 5.1, Y0 - yp, .12), 'paving', 'site', 0)
    C.box('Coach apron setts', (2.85, (yp + Y0) / 2, .02), (4.5, Y0 - yp, .04), 'setts', 'site', 0)
    C.box('East pavement', (X1 + .9, (Y0 + 12.0) / 2, .06), (1.8, 12.0 - Y0, .12), 'paving', 'site', 0)
    C.box('Side lane setts', (X1 + 1.8 + 2.6, (yp - 7.0 + 12.0) / 2, .02), (5.2, 12.0 - yp + 7.0, .04), 'setts', 'site', 0)
    C.box('South road', ((X0 - 6.0 + X1 + 1.8) / 2, yp - 3.5, .01), (X1 + 1.8 - X0 + 6.0, 7.0, .02), 'asphalt', 'site', 0)
    b = Batch()
    setts(b, .6, 5.1, yp, Y0, along='x')
    setts(b, X1 + 1.8, X1 + 7.0, yp - 7.0, 12.0, along='x')
    for k in range(int((X1 + 1.8 - X0 + 6.0) / .9)):
        x = X0 - 6.0 + k * .9
        if not (.6 < x < 5.1):
            b.box('settjoint', x, (yp + Y0) / 2, .121, .015, Y0 - yp - .02, .004)
    b.box('hardware', X1 + .5, Y0 - 1.3, 2.6, .1, .1, 5.2)                    # slender lamp column and lantern
    b.box('hardware', X1 + .5, Y0 - 1.6, 5.15, .06, .6, .06)
    b.box('pale', X1 + .5, Y0 - 1.85, 4.95, .26, .26, .32)
    b.box('hardware', X1 + .5, Y0 - 1.85, 5.14, .34, .34, .06)
    # Coped brick garden wall enclosing the end house's rear yard: along the side street from the house's north-east
    # corner to the line of the neighbour's back wing, then back west to the wing; the red door between brick piers.
    gx, gy1, gh, dy0, dy1, dh = X1 - .16, Y1 + 3.2 - .18, 2.1, Y1 + 1.15, Y1 + 2.15, 1.95
    # Each wall run is its own closed box (no shared or coplanar faces): the north run stops inside the east run.
    for i, (a, c) in enumerate(((Y1 - .02, dy0 - .1), (dy1 + .1, gy1 + .12))):          # ends buried in the piers
        C.box(f'Garden wall east {i}', (gx, (a + c) / 2, gh / 2), (.24, c - a, gh), 'brick', 'street', 0)
    C.box('Garden wall over door', (gx, (dy0 + dy1) / 2, (dh + gh) / 2), (.22, dy1 - dy0, gh - dh), 'brick', 'street', 0)
    C.box('Garden wall north', ((-1.05 + gx - .1) / 2, gy1, gh / 2), (gx - .1 + 1.05, .24, gh), 'brick', 'street', 0)
    C.box('Garden wall east coping', (gx, (Y1 + gy1 + .17) / 2, gh + .04), (.34, gy1 + .17 - Y1, .08), 'stone', 'street', 0)
    C.box('Garden wall north coping', ((-1.05 + gx - .15) / 2, gy1, gh + .035), (gx - .15 + 1.05, .34, .07), 'stone', 'street', 0)
    for k, yy in enumerate((dy0 - .17, dy1 + .17)):                            # piers with stone caps
        C.box(f'Garden gate pier {k}', (gx, yy, (gh + .16) / 2), (.36, .34, gh + .16), 'brick', 'street', 0)
        b.box('stone', gx, yy, gh + .2, .44, .42, .08)
    b.box('timber', gx + .04, (dy0 + dy1) / 2, dh + .05, .16, dy1 - dy0 + .04, .1)   # timber head
    b.box('door', gx + .02, (dy0 + dy1) / 2, dh / 2, .05, dy1 - dy0 - .02, dh - .02) # boarded red door, set in
    for k in range(1, 5):
        b.box('hardware', gx + .05, dy0 + (dy1 - dy0) * k / 5, dh / 2, .012, .018, dh - .1)
    b.box('hardware', gx + .06, dy0 + .15, 1.0, .03, .06, .1)                 # latch
    b.flush('street')
    tx, ty = (X0 + XN) / 2, Y0 - 1.0                                          # plane tree on the pavement in front of the neighbour
    C.rod('Plane tree trunk', (tx, ty, .12), (tx, ty, 9.2), .22, 'timber', 'street planting', 8)
    C.rod('Plane tree limb', (tx, ty, 6.5), (tx - 1.2, ty - .6, 9.5), .1, 'timber', 'street planting', 6)
    for i, (dx, dy, z, rx, ry, rz) in enumerate(((0, -.6, 11.6, 3.1, 2.3, 2.5), (-1.4, -.9, 10.2, 1.9, 1.6, 1.5), (1.2, -1.1, 10.4, 1.8, 1.5, 1.5), (0, -.4, 13.2, 1.9, 1.6, 1.3))):
        A.foliage(f'Plane tree crown {i}', (tx + dx, ty + dy, z), (rx, ry, rz), detail=2)


def build():
    site()
    south_face()
    other_faces()
    roof_and_inside()
    C.CONTACTS.append(dict(name='Two-storey mews end house with attached neighbour on a cobbled mews', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(-30, -40, 30), fill=(40, -20, 25), rear=(-15, 30, 25), target=(1.5, 0, 4.0), gain=4.0)
