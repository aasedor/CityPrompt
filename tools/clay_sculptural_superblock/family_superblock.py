"""Sculptural white residential superblock, authored from the locked catalogue views of
residential_superblock / variant_0 (parametric_sculptural_white).

Read from the pixels (the top view governs the plan): a perimeter block about 1.4 times as wide as it is
deep on a street corner, streets south and west, wrapped round a rounded inner court. Fluid white bands at
every floor: on the straight street faces they read as spandrels between white piers (punched windows);
round the rounded corners they thin out and project as sinuous balconies over ribbon glazing. The roof line
swoops up to nine storeys at the south-west corner and falls along the south wing to a three-storey podium
at the south-east corner, where a twisting fourteen-storey tower with spiralling white blades rises and
ends in an open loop. A glazed retail ground floor recessed behind sculpted white piers; terraced planting
in the court; roof terraces with skylights.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-sculptural-superblock'
AX, AY, R = 30.0, 22.0, 9.0                     # outer contour: 60 x 44 m rounded rectangle (top view)
X0, X1, Y0, Y1 = -AX, AX, -AY, AY
CX, CY, CR = 16.0, 9.0, 6.0                     # inner court contour: wings 14 m (east-west) and 13 m (north-south) deep
T = .30
G0 = .15
Z1 = 4.5                                        # top of the retail ground floor
FH = 3.1                                        # residential storey height
TX, TY = 21.0, -13.0                            # twisting tower centre over the south-east corner block
TOWER_STOREYS = 16
ZTOP = Z1 + (TOWER_STOREYS - 1) * FH
EPS = .002
PALETTE = dict(wall=(.93, .92, .90), joint=(.84, .83, .81), trim=(.70, .72, .73),
    pale=(.90, .90, .88), stone=(.80, .79, .76), roof=(.66, .66, .64), sand=(.76, .74, .70),
    foundation=(.56, .56, .55), glass=(.40, .48, .54), hardware=(.24, .25, .26),
    interior=(.84, .80, .74), floor=(.62, .58, .52), timber=(.50, .36, .22), blue=(.20, .30, .40),
    planting=(.28, .42, .18), soil=(.22, .16, .10), concrete=(.72, .71, .68), white=(.95, .95, .94),
    asphalt=(.30, .30, .31), paving=(.74, .73, .70))


def manifest(version):
    h = ZTOP + 9.0
    cams = G.camera_roster(X1 - X0 + 4.0, Y1 - Y0 + 4.0, h, [
        ('facade_close', (-16.0, -46.0, 14.0), (-16.0, Y0, 14.0), 45),
        ('architecture_close', (44.0, -40.0, 28.0), (TX, TY, 28.0), 45),
        ('glass_close', (-8.0, -34.0, 2.8), (-8.0, Y0, 2.8), 45),
        ('balcony_bands', (-44.0, -36.0, 18.0), (X0 + 4.0, Y0 + 4.0, 17.0), 45),
        ('twisting_tower', (48.0, -8.0, 34.0), (TX, TY, 33.0), 40),
        ('tower_loop', (34.0, -52.0, 62.0), (TX, TY, ZTOP + 2.0), 40),
        ('courtyard', (-4.0, -16.0, 52.0), (0.0, 2.0, 2.0), 32),
        ('roof_terraces', (-44.0, 34.0, 50.0), (-12.0, 6.0, 28.0), 40),
        ('interior', (X0 + 10.0, -3.0, Z1 + 3 * FH + 1.6), (X0, 3.0, Z1 + 3 * FH + 1.4), 35),
        ('rear_north', (0.0, 70.0, 16.0), (0.0, Y1, 14.0), 45)])
    for c in cams:                       # the locked front looks at the south-west corner from the street, at eye level
        if c['name'] == 'front':
            c['location'] = (-42.0, -68.0, 1.8); c['target'] = (4.0, -12.0, 19.0); c['lens'] = 24; c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='residential_superblock/variant_0 (parametric_sculptural_white)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=16, storey_programme='retail ground floor; apartments on eight upper floors round the court, the south wing dipping to about five storeys mid-block; a sixteen-storey twisting tower rising from the nine-storey south-east corner block',
            plan='60 x 44 m rounded perimeter block (top view) round a 32 x 18 m rounded court; twisting tower about 22 x 16 m flaring to 26 x 18 m over the south-east corner block',
            facade='white spandrel bands and piers (punched windows) on the straight street faces, thinning to sinuous projecting balcony bands over ribbon glazing round the corners; recessed retail glazing behind sculpted white piers',
            levels_m=[G0, Z1, Z1 + 8 * FH, ZTOP], storey_height_m=FH,
            inferred='storey counts round the ring, interiors and the north face are teaching assumptions; the tower loop is read from the oblique and top views'),
        roof_contract=dict(type='swooping flat roof terraces behind a white parapet band, skylights; twisting tower ending in an open loop', datum_m=Z1 + 8 * FH, crowns_m=[ZTOP, ZTOP + 7.0]),
        identity_contract=dict(owner='fluid white perimeter block with sinuous balcony bands, swooping roof line, twisting looped tower at the south-east corner, rounded court'),
        material_contract=dict(profile='source-palette clay: white composite bands and piers, clear and grey glass, pale paving, planted court', textured_keeper=False),
        programme_contract=dict(storeys=14, ground='shops and lobbies', upper='apartments with balconies', court='terraced garden'),
        contact_contract=['Grade-zero sidewalks, court and streets', 'Ring on the retail ground floor and sculpted piers', 'Tower on the south-east podium roof', 'Loop springing from the tower blades'],
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


# ---- sculptural white residential superblock ----

class Batch:
    """Merges boxes, oriented boxes and beams per role into one mesh each."""
    def __init__(self):
        self.g = {}

    def _hex(self, role, corners):
        V, F = self.g.setdefault(role, ([], []))
        o = len(V)
        V.extend(corners)
        F.extend(tuple(o + i for i in face) for face in C.BOX_FACES)

    def box(self, role, cx, cy, cz, sx, sy, sz):
        self._hex(role, [(cx + du * sx / 2, cy + dd * sy / 2, cz + dz * sz / 2) for dz in (-1, 1) for du, dd in ((-1, -1), (1, -1), (1, 1), (-1, 1))])

    def obox(self, role, x, y, nx, ny, w, d0, d1, z0, z1):
        """Box aligned to a facade: w along the tangent, from depth d0 to d1 along the outward normal (nx, ny)."""
        tx, ty = -ny, nx
        pts = []
        for z in (z0, z1):
            for du, dd in ((-1, d0), (1, d0), (1, d1), (-1, d1)):
                pts.append((x + tx * du * w / 2 + nx * dd, y + ty * du * w / 2 + ny * dd, z))
        self._hex(role, pts)

    def flush(self, module):
        for role, (V, F) in self.g.items():
            if F:
                C.mesh(f'{module} {role}', V, F, role, module)
        self.g = {}


NX, NY, NC = 24, 15, 14


def rr(ax, ay, r, nx=NX, ny=NY, nc=NC):
    """Rounded rectangle sampled with a fixed point count, so the outer and court contours pair up.
    Starts at the south end of the south-east corner and runs anticlockwise. Returns (x, y, nx, ny)."""
    corners = [((ax - r, -(ay - r)), -90.0, ny), ((ax - r, ay - r), 0.0, nx), ((-(ax - r), ay - r), 90.0, ny), ((-(ax - r), -(ay - r)), 180.0, nx)]
    pts = []
    for k, ((cx, cy), a0, segs) in enumerate(corners):
        for i in range(nc):
            t = math.radians(a0 + 90.0 * i / nc)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t), math.cos(t), math.sin(t)))
        t = math.radians(a0 + 90.0)
        e = (cx + r * math.cos(t), cy + r * math.sin(t))
        (nx_, ny_), na, _ = corners[(k + 1) % 4]
        tn = math.radians(na)
        s = (nx_ + r * math.cos(tn), ny_ + r * math.sin(tn))
        for i in range(segs):
            f = i / segs
            pts.append((e[0] + (s[0] - e[0]) * f, e[1] + (s[1] - e[1]) * f, math.cos(t), math.sin(t)))
    return pts


def off(p, d, z):
    return (p[0] + p[2] * d, p[1] + p[3] * d, z)


def loft(name, rings, role, module, closed=True):
    """Loft a closed profile (list of 3D points) carried round a sequence of rings."""
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


def runs(mask):
    """Contiguous runs of True round a closed sequence; a full ring is returned as (indices, True)."""
    n = len(mask)
    if all(mask):
        return [(list(range(n)), True)]
    start = next(i for i in range(n) if not mask[i])
    out, cur = [], []
    for k in range(1, n + 1):
        i = (start + k) % n
        if mask[i]:
            cur.append(i)
        elif cur:
            out.append((cur, False)); cur = []
    if cur:
        out.append((cur, False))
    return out


OUT, INN = rr(AX, AY, R), rr(CX, CY, CR)
N = len(OUT)
STOREYS = [(-180, 9.0), (-140, 9.7), (-112, 9.2), (-97, 7.0), (-86, 4.6), (-77, 4.6), (-66, 9.0), (0, 9.0), (60, 8.7), (90, 8.7), (135, 9.0), (180, 9.0)]


def storeys(p):
    a = math.degrees(math.atan2(p[1] / AY, p[0] / AX))
    for (a0, s0), (a1, s1) in zip(STOREYS, STOREYS[1:]):
        if a0 <= a <= a1:
            f = (a - a0) / (a1 - a0)
            f = f * f * (3 - 2 * f)                                           # smooth the swoop
            return s0 + (s1 - s0) * f
    return 9.0


H = [Z1 + (storeys(p) - 1) * FH for p in OUT]


def corner_weight(p, ax, ay, r):
    dx, dy = (ax - r) - abs(p[0]), (ay - r) - abs(p[1])
    if dx <= 0 and dy <= 0:
        return 1.0
    return max(0.0, 1.0 - max(dx, dy) / 2.5)


WO = [corner_weight(p, AX, AY, R) for p in OUT]


TZONE = [math.hypot(p[0] - TX, p[1] - TY) < 10.5 for p in OUT]       # roof under the tower: no parapet, planters or skylights


def lerp_pt(p, q, f, z):
    return (p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f, z)


def ring_block():
    GO = [-.45 - .55 * w for w in WO]                                     # glass line: shallow on the street faces, deep behind balconies
    # Retail ground floor: recessed glazing, sculpted white piers carrying arches under the first floor band.
    rings = [[off(p, -1.63, G0), off(p, -1.57, G0), off(p, -1.57, Z1 - .02), off(p, -1.63, Z1 - .02)] for p in OUT]
    loft('Retail glazing', rings, 'glass', 'ground')
    rings = [[off(p, 1.17, G0), off(p, 1.23, G0), off(p, 1.23, Z1 - .02), off(p, 1.17, Z1 - .02)] for p in INN]
    loft('Court glazing', rings, 'glass', 'ground')
    b = Batch()
    for i, p in enumerate(OUT):
        b.obox('trim', p[0], p[1], p[2], p[3], .12, -1.68, -1.52, G0, Z1 - .02)
        if i % 4 == 0:
            b.obox('white', p[0], p[1], p[2], p[3], 1.1, -1.5, .25, G0, Z1 - 1.0)
        q = INN[i]
        b.obox('trim', q[0], q[1], q[2], q[3], .12, 1.12, 1.28, G0, Z1 - .02)
    b.flush('ground floor')
    rings = []
    for i, p in enumerate(OUT):
        zb = Z1 - .06 - 1.45 * (1.0 - math.sin(math.pi * (i % 4) / 4.0))
        rings.append([off(p, -1.5, zb), off(p, .25, zb), off(p, .25, Z1), off(p, -1.5, Z1)])
    loft('Retail arches', rings, 'white', 'ground')
    # Upper glass walls between the floor bands, up to the underside of the roof.
    rings = [[off(p, g - .03, Z1), off(p, g + .03, Z1), off(p, g + .03, h - .38), off(p, g - .03, h - .38)] for p, h, g in zip(OUT, H, GO)]
    loft('Street glazing', rings, 'glass', 'upper')
    rings = [[off(p, .97, Z1), off(p, 1.03, Z1), off(p, 1.03, h - .38), off(p, .97, h - .38)] for p, h in zip(INN, H)]
    loft('Court glazing upper', rings, 'glass', 'upper')
    # Floor bands: full-depth slabs that project as thin balconies with glass balustrades on the rounded corners and
    # as solid spandrels on the straight street faces, where white piers between them leave tall punched windows.
    b = Batch()
    k = 0
    while True:
        z = Z1 + k * FH
        mask = [z + 1.1 <= h - .45 for h in H]
        if not any(mask):
            break
        for idx, closed in runs(mask):
            rings = []
            for i in idx:
                p, q, w, g = OUT[i], INN[i], WO[i], GO[i]
                proj = .25 + 1.45 * w
                t = 1.0 - .65 * w
                rings.append([off(q, -.45, z), off(q, -.45, z + .35), off(p, g + .08, z + .35), off(p, g + .08, z + t), off(p, proj - .06, z + t), off(p, proj, z)])
            loft(f'Floor band {k}', rings, 'white', 'bands', closed=closed)
            sub = [i for i in idx if WO[i] > .5]
            for run, _ in runs([i in sub for i in range(N)]) if sub else []:
                rings = [[off(OUT[i], .15 + 1.45 * WO[i], z + .35), off(OUT[i], .21 + 1.45 * WO[i], z + .35), off(OUT[i], .21 + 1.45 * WO[i], z + 1.35), off(OUT[i], .15 + 1.45 * WO[i], z + 1.35)] for i in run]
                if len(rings) > 1:
                    loft(f'Balcony balustrade {k}', rings, 'glass', 'bands', closed=False)
            for i in idx:
                p, w, g = OUT[i], WO[i], GO[i]
                if w == 0.0 and i % 2 == 0:
                    b.obox('white', p[0], p[1], p[2], p[3], 1.9, g - .02, .2, z + 1.0, min(z + FH, H[i] - .38))
        k += 1
    b.flush('piers')
    # Roof: slab, the swooping white parapet band following the roof line, linear skylights and a glazed penthouse.
    rings = [[off(q, -.4, h - .45), off(q, -.4, h), off(p, -.9, h), off(p, -.9, h - .45)] for p, q, h in zip(OUT, INN, H)]
    loft('Roof slab', rings, 'roof', 'roof')
    open_mask = [not z_ for z_ in TZONE]
    for idx, closed in runs(open_mask):
        rings = [[off(OUT[i], -1.15, H[i] - .4), off(OUT[i], .35, H[i] - .4), off(OUT[i], .35, H[i] + 1.1), off(OUT[i], -1.15, H[i] + 1.1)] for i in idx]
        loft('Roof parapet band', rings, 'white', 'roof', closed=closed)
        rings = [[off(INN[i], -.55, H[i] - .4), off(INN[i], -.55, H[i] + .9), off(INN[i], .7, H[i] + .9), off(INN[i], .7, H[i] - .4)] for i in idx]
        loft('Court parapet band', rings, 'white', 'roof', closed=closed)
    sky = [not TZONE[i] and H[i] >= Z1 + 6 * FH for i in range(N)]
    for idx, closed in runs(sky):
        if len(idx) < 3:
            continue
        idx = idx[1:-1]
        rings = []
        for i in idx:
            p, q, h = OUT[i], INN[i], H[i]
            a_, c_ = lerp_pt(p, q, .44, 0), lerp_pt(p, q, .56, 0)
            rings.append([(a_[0], a_[1], h + .02), (c_[0], c_[1], h + .02), (c_[0], c_[1], h + .45), (a_[0], a_[1], h + .45)])
        loft('Linear skylight frame', rings, 'pale', 'roof', closed=False)
        rings = [[(r[3][0], r[3][1], r[3][2]), (r[2][0], r[2][1], r[2][2]), (r[2][0], r[2][1], r[2][2] + .06), (r[3][0], r[3][1], r[3][2] + .06)] for r in rings]
        loft('Linear skylight glass', rings, 'glass', 'roof', closed=False)
    pent = [i for i, p in enumerate(OUT) if -152.0 < math.degrees(math.atan2(p[1] / AY, p[0] / AX)) < -118.0]
    if len(pent) > 1:
        hp = max(H[i] for i in pent)
        rings = [[lerp_pt(OUT[i], INN[i], .3, H[i]), lerp_pt(OUT[i], INN[i], .7, H[i]), lerp_pt(OUT[i], INN[i], .7, hp + 2.8), lerp_pt(OUT[i], INN[i], .3, hp + 2.8)] for i in pent]
        loft('Glazed penthouse', rings, 'glass', 'roof', closed=False)
        rings = [[lerp_pt(OUT[i], INN[i], .26, hp + 2.8), lerp_pt(OUT[i], INN[i], .74, hp + 2.8), lerp_pt(OUT[i], INN[i], .74, hp + 3.15), lerp_pt(OUT[i], INN[i], .26, hp + 3.15)] for i in pent]
        loft('Penthouse roof', rings, 'white', 'roof', closed=False)
        C.qa_room_light('Penthouse', lerp_pt(OUT[pent[len(pent) // 2]], INN[pent[len(pent) // 2]], .5, hp + 1.8), 80, 4.0)
    b = Batch()
    for i in (12, 40, 52, 70, 86, 100, 116):                                # terrace planters, inside the court parapet
        if i >= N or TZONE[i]:
            continue
        q, h = INN[i], H[i]
        b.obox('planting', q[0], q[1], q[2], q[3], 3.0, .9, 1.8, h, h + .55)
    b.flush('roof terraces')
    for k in range(1, 8, 2):
        C.qa_room_light(f'Apartments west {k}', (X0 + 5.0, 0.0, Z1 + k * FH + 2.4), 120, 4.0)
        C.qa_room_light(f'Apartments south {k}', (-14.0, Y0 + 5.0, Z1 + k * FH + 2.4), 120, 4.0)
    C.qa_room_light('Retail', (-10.0, Y0 + 6.0, 3.6), 260, 8.0)
    C.CONTACTS.append(dict(name='Ring of floor bands on the retail ground floor, arches and sculpted piers; roof line from 9 storeys at the south-west dipping mid-south, 9 storeys at the south-east and east', storey_height_m=FH))


def ellipse(rx, ry, phi, n=36, cx=TX, cy=TY):
    c, s = math.cos(phi), math.sin(phi)
    return [(cx + rx * math.cos(t) * c - ry * math.sin(t) * s, cy + rx * math.cos(t) * s + ry * math.sin(t) * c) for t in (k * math.tau / n for k in range(n))]


def tower():
    zp = Z1 + 8 * FH                                                    # the roof of the nine-storey corner block
    levels = [zp + k * FH for k in range(int(round((ZTOP - zp) / FH)) + 1)]
    span = levels[-1] - zp

    def shape(z):
        f = (z - zp) / span
        return 9.6 + 3.0 * f * f, 7.2 + 1.8 * f * f, math.radians(-40.0 + 115.0 * f), TX + 1.5 * f, TY - 1.0 * f

    def pt(z, rs, t):
        rx, ry, phi, cx, cy = shape(z)
        c, s = math.cos(phi), math.sin(phi)
        x, y = rx * rs * math.cos(t), ry * rs * math.sin(t)
        return (cx + x * c - y * s, cy + x * s + y * c, z)

    zs = [zp + span * k / (3 * (len(levels) - 1)) for k in range(3 * (len(levels) - 1) + 1)]   # finer than the floors
    n = 36
    rings = [[pt(z, .86, k * math.tau / n) for k in range(n)] for z in zs]
    vs = [v for r_ in rings for v in r_]
    fs = []
    for i in range(len(rings) - 1):
        for j in range(n):
            k = (j + 1) % n
            fs.append((i * n + j, i * n + k, (i + 1) * n + k, (i + 1) * n + j))
    fs.append(tuple(range(n - 1, -1, -1))); fs.append(tuple((len(rings) - 1) * n + j for j in range(n)))
    C.mesh('Tower glazing', vs, fs, 'glass', 'tower')
    for k, z in enumerate(levels):                                          # floor plates, rims just inside the blades
        pts = [pt(z, .97, j * math.tau / n)[:2] for j in range(n)]
        C.prism(f'Tower floor {k}', pts, 'z', z - .15, z + .45, 'white', 'tower')
        if k % 3 == 1:
            C.qa_room_light(f'Tower {k}', (shape(z)[3], shape(z)[4], z + 2.3), 60, 3.0)
    # Two broad white blades spiralling up the tower, and an open twisted loop springing from their tops.
    BW = .62
    for side in (0.0, math.pi):
        brings = []
        for z in zs:
            prof = [pt(z, 1.2, side - BW + 2 * BW * k / 8) for k in range(9)] + [pt(z, .99, side + BW - 2 * BW * k / 8) for k in range(9)]
            brings.append(prof)
        loft('Tower blade', brings, 'white', 'tower', closed=False)
    rx, ry, phi, cx, cy = shape(levels[-1])
    c, s = math.cos(phi), math.sin(phi)
    base_side = (-s, c, 0.0)
    path = []
    R0 = rx * 1.095
    for k in range(33):
        t = math.pi * k / 32
        path.append((cx + R0 * math.cos(t) * c, cy + R0 * math.cos(t) * s, levels[-1] + 9.0 * math.sin(t)))
    lrings = []
    for k, p in enumerate(path):
        a, b = path[max(0, k - 1)], path[min(len(path) - 1, k + 1)]
        tv = [b[i] - a[i] for i in range(3)]; L = math.sqrt(sum(v * v for v in tv)); tv = [v / L for v in tv]
        sv = list(base_side)
        nv = [tv[1] * sv[2] - tv[2] * sv[1], tv[2] * sv[0] - tv[0] * sv[2], tv[0] * sv[1] - tv[1] * sv[0]]
        tw = math.radians(70.0) * math.sin(math.pi * k / 32)                  # the ribbon twists about its own axis
        sw = [sv[i] * math.cos(tw) + nv[i] * math.sin(tw) for i in range(3)]
        nw = [nv[i] * math.cos(tw) - sv[i] * math.sin(tw) for i in range(3)]
        lrings.append([tuple(p[i] + sw[i] * u + nw[i] * v for i in range(3)) for u, v in ((-2.6, -.35), (2.6, -.35), (2.6, .35), (-2.6, .35))])
    loft('Tower loop', lrings, 'white', 'tower', closed=False)
    C.CONTACTS.append(dict(name='Twisting tower on the roof of the nine-storey south-east block; loop springing from the tops of the blades', base_m=zp, top_m=levels[-1]))


def court_and_site():
    C.box('Court paving', (0, 0, .05), (2 * CX, 2 * CY, .1), 'paving', 'court', 0)
    for k, (ax, ay, r, z) in enumerate(((CX - 3.0, CY - 2.2, CR - 1.6, .5), (CX - 6.0, CY - 4.2, CR - 3.0, .9))):
        ring = rr(ax, ay, r)
        rings = [[(p[0] - p[2] * .9, p[1] - p[3] * .9, .1), (p[0], p[1], .1), (p[0], p[1], z), (p[0] - p[2] * .9, p[1] - p[3] * .9, z)] for p in ring]
        loft(f'Court terrace {k}', rings, 'stone', 'court')
        rings = [[(p[0] - p[2] * .85, p[1] - p[3] * .85, z), (p[0] - p[2] * .05, p[1] - p[3] * .05, z), (p[0] - p[2] * .05, p[1] - p[3] * .05, z + .08), (p[0] - p[2] * .85, p[1] - p[3] * .85, z + .08)] for p in ring]
        loft(f'Court planting {k}', rings, 'planting', 'court')
    for x, y in ((-9.0, 2.0), (6.0, -3.0), (10.0, 3.5)):
        A.small_tree(x, y, .1, 5.5, 1.8)
    C.box('Sidewalk', (0, 0, .03), (2 * AX + 10.0, 2 * AY + 10.0, .06), 'paving', 'site', 0)
    C.box('South street', (0, Y0 - 11.0, .01), (2 * AX + 50.0, 12.0, .02), 'asphalt', 'site', 0)
    C.box('West street', (X0 - 11.0, (Y0 - 5.0 + Y1 + 15.0) / 2, .01), (12.0, Y1 + 15.0 - (Y0 - 5.0), .02), 'asphalt', 'site', 0)   # stops at the south street
    for x in (-24.0, -12.0, 0.0, 12.0, 24.0):
        street_tree(x, Y0 - 3.4, z=.06, height=8.0, spread=2.2)
    for y in (-10.0, 6.0):
        street_tree(X0 - 3.4, y, z=.06, height=8.0, spread=2.2)


def build():
    court_and_site()
    ring_block()
    tower()
    C.CONTACTS.append(dict(name='Superblock: ring of white bands round a court, twisting looped tower at the south-east', block=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(-70, -90, 80), fill=(80, -50, 60), rear=(-40, 80, 70), target=(0, 0, 16.0), gain=20.0)
