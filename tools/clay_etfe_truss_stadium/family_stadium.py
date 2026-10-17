"""Contemporary steel and ETFE stadium bowl, authored from the locked catalogue views of
outdoor_sports_stadium / variant_0 (contemporary_steel_etfe_bowl).

Read from the pixels (the top view governs the plan): a rounded-rectangle bowl about 1.2 times as wide as it
is deep, on a city block with streets all round and a broad paved plaza. A glazed concourse at grade behind a
ring of raking steel V-columns; above it an exposed structural steel facade of crossing diagonals, clad on
the south and west, round the south-west corner, in a band of translucent silver-white diamond ETFE
cushions. Over the bowl a steel truss roof ring: a deep perimeter truss on the facade line, radial trusses
falling to an inner compression ring, translucent panels between them. Inside, a continuous seating bowl
rising from a natural-grass pitch whose long axis runs north-south.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-etfe-truss-stadium'
AX, AY, R = 96.0, 80.0, 26.0                    # facade line: 192 x 160 m rounded rectangle (top view)
X0, X1, Y0, Y1 = -AX, AX, -AY, AY
T = .30
G0 = .15
ZC = 7.0                                        # concourse level, top of the grade glazing
ZF = 26.0                                       # top of the facade, foot of the perimeter truss
ZT = 36.0                                       # top chord of the perimeter truss
IX, IY, IR = 56.0, 64.0, 16.0                   # inner compression ring (roof opening)
ZI0, ZI1 = 29.5, 33.0                           # bottom and top chords at the inner ring
PX, PY = 34.0, 52.0                             # pitch with run-off, long axis north-south
ZB = 22.0                                       # back row of the seating bowl
EPS = .002
PALETTE = dict(wall=(.70, .70, .68), joint=(.60, .60, .58), trim=(.62, .64, .66),
    pale=(.86, .86, .84), stone=(.66, .65, .62), roof=(.62, .62, .60), sand=(.70, .68, .64),
    foundation=(.46, .46, .45), glass=(.50, .58, .62), hardware=(.20, .21, .22),
    interior=(.62, .62, .60), floor=(.56, .56, .54), timber=(.48, .34, .22), blue=(.20, .30, .40),
    planting=(.26, .40, .18), soil=(.22, .16, .10), concrete=(.62, .62, .60), white=(.92, .92, .91),
    asphalt=(.28, .28, .29), steel=(.40, .42, .44), etfe=(.88, .89, .90), etfeback=(.54, .56, .58),
    seat=(.46, .48, .50), pitch=(.24, .40, .16), pitch2=(.28, .45, .19), line=(.92, .92, .90),
    track=(.52, .50, .46), paving=(.66, .65, .62))


def manifest(version):
    h = ZT + 2.0
    cams = G.camera_roster(X1 - X0 + 4.0, Y1 - Y0 + 4.0, h, [
        ('facade_close', (-34.0, -AY - 46.0, 14.0), (-34.0, -AY, 15.0), 40),
        ('architecture_close', (AX + 36.0, -AY - 36.0, 18.0), (AX - 16.0, -AY + 12.0, 17.0), 40),
        ('glass_close', (-6.0, -AY - 20.0, 3.0), (-6.0, -AY + 3.0, 3.6), 40),
        ('v_columns', (24.0, -AY - 18.0, 2.4), (24.0, -AY, 4.6), 32),
        ('etfe_cushions', (-AX - 26.0, -36.0, 15.0), (-AX, -36.0, 16.0), 45),
        ('roof_truss', (AX + 34.0, -AY - 34.0, 64.0), (AX - 24.0, -AY + 20.0, 30.0), 35),
        ('inner_ring', (0.0, -AY - 30.0, 110.0), (0.0, 8.0, 24.0), 30),
        ('seating_bowl', (-30.0, -16.0, 82.0), (18.0, 14.0, 6.0), 30),
        ('interior', (0.0, -PY - 11.0, 11.0), (0.0, 20.0, 1.0), 24),
        ('rear_north', (0.0, AY + 130.0, 30.0), (0.0, AY, 20.0), 35)])
    for c in cams:                       # the locked front looks at the south face from the street, at eye level
        if c['name'] == 'front':
            c['location'] = (-46.0, -AY - 78.0, 1.8); c['target'] = (22.0, -AY + 18.0, 19.0); c['lens'] = 22; c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='outdoor_sports_stadium/variant_0 (contemporary_steel_etfe_bowl)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=3, storey_programme='glazed concourse at grade, upper concourse behind the facade, continuous seating bowl to the back row, truss roof ring',
            plan='192 x 160 m rounded rectangle (top view); pitch 68 x 104 m with run-off, long axis north-south; inner roof opening 112 x 128 m',
            facade='raking steel V-columns before the grade glazing; exposed crossing steel diagonals to the roof; diamond ETFE cushion band on the south and west, round the south-west corner',
            levels_m=[G0, ZC, ZB, ZF], roof_m=dict(perimeter_truss=[ZF, ZT], inner_ring=[ZI0, ZI1]),
            inferred='tier count, concourse depth and the north and east facades are teaching assumptions; the north face is not visible in any source and repeats the exposed-steel grammar'),
        roof_contract=dict(type='steel truss roof ring: perimeter truss, radial trusses, inner compression ring, translucent panels; open over the pitch', datum_m=ZF, crowns_m=[ZT]),
        identity_contract=dict(owner='rounded-rectangle bowl, diamond ETFE band round the south-west corner, exposed steel diagonals elsewhere, truss roof ring with an inner compression ring, seating bowl round a north-south pitch'),
        material_contract=dict(profile='source-palette clay: silver-white ETFE cushions, dark grey structural steel, clear concourse glass, translucent roof panels, grey seats, green pitch, pale plaza paving', textured_keeper=False),
        programme_contract=dict(storeys=3, ground='concourse, entrances, concessions', bowl='continuous seating', roof='spectator canopy'),
        contact_contract=['Grade-zero plaza and streets', 'V-columns and facade diagonals founded at grade', 'Perimeter truss on the facade ring beam', 'Radial trusses spanning to the inner compression ring', 'Seating bowl on the concourse structure'],
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


# ---- contemporary steel and ETFE stadium ----

class Batch:
    """Merges boxes and oriented beams per role into one mesh each."""
    def __init__(self):
        self.g = {}

    def _quad_box(self, role, corners):
        V, F = self.g.setdefault(role, ([], []))
        o = len(V)
        V.extend(corners)
        F.extend(tuple(o + i for i in face) for face in C.BOX_FACES)

    def box(self, role, cx, cy, cz, sx, sy, sz):
        self._quad_box(role, [(cx + du * sx / 2, cy + dd * sy / 2, cz + dz * sz / 2) for dz in (-1, 1) for du, dd in ((-1, -1), (1, -1), (1, 1), (-1, 1))])

    def beam(self, role, a, b, w, d=None):
        d = d or w
        ax = [b[i] - a[i] for i in range(3)]
        L = math.sqrt(sum(v * v for v in ax))
        if L < 1e-6:
            return
        ax = [v / L for v in ax]
        ref = (0.0, 0.0, 1.0) if abs(ax[2]) < .95 else (0.0, 1.0, 0.0)
        s = (ax[1] * ref[2] - ax[2] * ref[1], ax[2] * ref[0] - ax[0] * ref[2], ax[0] * ref[1] - ax[1] * ref[0])
        n = math.sqrt(sum(v * v for v in s)); s = [v / n for v in s]
        u = (ax[1] * s[2] - ax[2] * s[1], ax[2] * s[0] - ax[0] * s[2], ax[0] * s[1] - ax[1] * s[0])
        pts = []
        for p in (a, b):
            for du, dd in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                pts.append(tuple(p[i] + du * w / 2 * s[i] + dd * d / 2 * u[i] for i in range(3)))
        self._quad_box(role, pts)

    def flush(self, module):
        for role, (V, F) in self.g.items():
            if F:
                C.mesh(f'{module} {role}', V, F, role, module)
        self.g = {}


NX, NY, NC = 16, 14, 6


def rr(ax, ay, r, nx=NX, ny=NY, nc=NC):
    """Rounded rectangle sampled with a fixed point count, so rings of different size loft cleanly.
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


def lerp_ring(a, b, f):
    return [(p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f, p[2] + (q[2] - p[2]) * f, p[3] + (q[3] - p[3]) * f) for p, q in zip(a, b)]


def bowl():
    """Continuous seating bowl: a stepped section lofted between the pitch edge and the back row."""
    inner, outer = rr(PX + 6.0, PY + 6.0, 8.0), rr(AX - 9.0, AY - 9.0, R - 6.0)
    NS = 14
    z0 = 1.4
    prof = [(0.0, G0), (0.0, z0)]
    for k in range(NS):
        f1 = (k + 1) / NS
        za = z0 + (ZB - z0) * k / NS
        zb = z0 + (ZB - z0) * (k + 1) / NS
        prof += [(f1, za), (f1, zb)]
    prof += [(1.0, ZB + 1.1), (1.0 + .02, ZB + 1.1), (1.0 + .02, ZC), (.62, G0 + 3.2), (.62, G0)]
    rings = []
    for p, q in zip(inner, outer):
        ring = []
        for f, z in prof:
            ring.append((p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f, z))
        rings.append(ring[::-1])
    loft('Seating bowl', rings, 'seat', 'bowl')                          # grey seat rows read as the stepped treads
    b = Batch()
    for i in range(0, len(inner), 7):                                     # aisle stairs
        p, q = inner[i], outer[i]
        b.beam('pale', (p[0], p[1], z0 + .05), (q[0] + (p[0] - q[0]) * .02, q[1] + (p[1] - q[1]) * .02, ZB + .05), 1.4, .12)
    b.flush('bowl seats')
    C.CONTACTS.append(dict(name='Seating bowl from the pitch edge to the back row, on the concourse structure', rows=NS, back_row_m=ZB))


def pitch():
    C.box('Pitch apron', (0, 0, .08), (2 * (PX + 6.0) + 2.0, 2 * (PY + 6.0) + 2.0, .16), 'track', 'pitch', 0)
    n = 12
    for k in range(n):
        y = -PY + (k + .5) * 2 * PY / n
        C.box('Pitch stripe', (0, y, .2), (2 * PX, 2 * PY / n, .08), 'pitch' if k % 2 else 'pitch2', 'pitch', 0)
    b = Batch()
    w = .14
    for x in (-PX + 2.0, PX - 2.0):
        b.box('line', x, 0, .25, w, 2 * PY - 4.0, .02)
    for y in (-PY + 2.0, 0.0, PY - 2.0):
        b.box('line', 0, y, .25, 2 * PX - 4.0, w, .02)
    for k in range(32):
        t0, t1 = k * math.tau / 32, (k + 1) * math.tau / 32
        b.beam('line', (9.15 * math.cos(t0), 9.15 * math.sin(t0), .25), (9.15 * math.cos(t1), 9.15 * math.sin(t1), .25), w, .02)
    for s in (-1, 1):
        yb = s * (PY - 2.0)
        for x0, x1, dy in ((-20.15, 20.15, 16.5), (-9.16, 9.16, 5.5)):
            b.box('line', 0, yb - s * dy, .25, x1 - x0, w, .02)
            for x in (x0, x1):
                b.box('line', x, yb - s * dy / 2, .25, w, dy, .02)
        b.box('white', 0, yb + s * .9, .26 + 2.44, 7.44, .12, .12)
        for x in (-3.72, 3.72):
            b.box('white', x, yb + s * .9, .26 + 1.22, .12, .12, 2.44)
    b.flush('pitch markings')


def concourse():
    """Glazed concourse at grade, recessed 3 m behind the facade line, under the concourse slab."""
    gl = rr(AX - 3.0, AY - 3.0, R - 3.0)
    rings = [[off(p, -.03, G0), off(p, .03, G0), off(p, .03, ZC - .5), off(p, -.03, ZC - .5)] for p in gl]
    loft('Concourse glazing', rings, 'glass', 'concourse')
    b = Batch()
    for i, p in enumerate(gl):
        q = gl[(i + 1) % len(gl)]
        for f in (0.0, .5):
            mx, my = p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f
            b.box('trim', mx, my, (G0 + ZC - .5) / 2, .14, .14, ZC - .5 - G0)
        b.beam('trim', off(p, 0, ZC - .45), off(q, 0, ZC - .45), .2, .12)
        b.beam('trim', off(p, 0, 2.6), off(q, 0, 2.6), .12, .1)
    for i in (12, 54, 72, 79):                                          # entrance canopies over the doors (east, west, south)
        p = gl[i]
        b.box('hardware', p[0] + p[2] * .9, p[1] + p[3] * .9, 3.2, 7.0 if abs(p[3]) > .5 else 1.8, 1.8 if abs(p[3]) > .5 else 7.0, .3)
    b.flush('concourse frames')
    outer, back = rr(AX, AY, R), rr(AX - 9.0, AY - 9.0, R - 6.0)
    rings = [[off(p, .0, ZC - .5), off(p, .0, ZC), off(q, 0, ZC), off(q, 0, ZC - .5)] for p, q in zip(back, outer)]
    loft('Concourse slab', rings, 'concrete', 'concourse')
    inner = rr(AX - 3.0, AY - 3.0, R - 3.0)
    rings = [[off(p, -6.0, G0 + .02), off(p, -6.0, ZC - .5), off(p, -5.7, ZC - .5), off(p, -5.7, G0 + .02)] for p in inner]
    loft('Concourse back wall', rings, 'interior', 'concourse')
    C.qa_room_light('Concourse south', (0, -AY + 6.0, 4.0), 900, 20.0)
    C.qa_room_light('Concourse west', (-AX + 6.0, 0, 4.0), 900, 20.0)


def facade():
    """Raking V-columns at grade, crossing diagonals to the roof ring, ring beams, and the ETFE band."""
    ring = rr(AX, AY, R)
    n = len(ring)
    b = Batch()
    for i in range(n):
        p, q = ring[i], ring[(i + 1) % n]
        mid = ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)
        b.beam('steel', (p[0], p[1], G0), (mid[0], mid[1], ZC), .55)            # V-columns
        b.beam('steel', (q[0], q[1], G0), (mid[0], mid[1], ZC), .55)
        b.beam('steel', (p[0], p[1], ZC), (q[0], q[1], ZF), .5)                 # crossing diagonals
        b.beam('steel', (q[0], q[1], ZC), (p[0], p[1], ZF), .5)
        for z in (ZC, (ZC + ZF) / 2, ZF):
            b.beam('steel', (p[0], p[1], z), (q[0], q[1], z), .6, .7)          # ring beams
        b.beam('steel', off(p, 0, ZB + 1.0), off(p, -9.0, ZB + 1.0), .4)      # ties back to the bowl
        b.box('foundation', p[0], p[1], G0 / 2 + .1, 1.0, 1.0, G0 + .2)
    b.flush('facade steel')
    # ETFE band: south and west faces round the south-west corner.
    fine = rr(AX + .6, AY + .6, R + .6, 64, 56, 24)
    sel = [p for p in fine if p[0] < 34.0 and p[1] < 14.0 and (p[2] < -.3 or p[3] < -.3)]
    s = [0.0]
    for p, q in zip(sel, sel[1:]):
        s.append(s[-1] + math.hypot(q[0] - p[0], q[1] - p[1]))
    L = s[-1]

    def at(t, d, z):
        t = min(max(t, 0.0), L)
        k = max(0, min(len(s) - 2, next((i for i in range(len(s) - 1) if s[i + 1] >= t), len(s) - 2)))
        f = (t - s[k]) / max(1e-9, s[k + 1] - s[k])
        p, q = sel[k], sel[k + 1]
        x, y = p[0] + (q[0] - p[0]) * f, p[1] + (q[1] - p[1]) * f
        nx, ny = p[2] + (q[2] - p[2]) * f, p[3] + (q[3] - p[3]) * f
        m = math.hypot(nx, ny)
        return (x + nx / m * (d - .6), y + ny / m * (d - .6), z)

    E0, E1 = ZC + 1.2, ZF - .4
    rings = [[at(t, .2, E0), at(t, .4, E0), at(t, .4, E1), at(t, .2, E1)] for t in s]
    loft('ETFE backing', rings, 'etfeback', 'etfe', closed=False)
    a, hb = 3.0, 1.9
    vs, fs = [], []
    rows = int((E1 - E0) / hb) - 1
    for r_ in range(rows + 1):
        zc = E0 + hb + r_ * hb
        for k in range(int(L / (2 * a)) + 2):
            tc = (2 * k + (r_ % 2)) * a
            if tc - a < 0 or tc + a > L or zc - hb < E0 - .01 or zc + hb > E1 + .01:
                continue
            o = len(vs)
            vs += [at(tc, .6, zc + hb), at(tc + a, .6, zc), at(tc, .6, zc - hb), at(tc - a, .6, zc), at(tc, 1.05, zc)]
            fs += [(o, o + 4, o + 1), (o + 1, o + 4, o + 2), (o + 2, o + 4, o + 3), (o + 3, o + 4, o)]
            fs += [(o, o + 1, o + 2, o + 3)]
    C.mesh('ETFE cushions', vs, fs, 'etfe', 'etfe')
    b = Batch()
    for z in (E0 - .1, E1 + .1):
        for t0, t1 in zip(s, s[1:]):
            b.beam('pale', at(t0, .62, z), at(t1, .62, z), .3, .3)
    b.flush('etfe edges')
    C.CONTACTS.append(dict(name='ETFE cushions on a backing band hung off the facade diagonals, south and west round the south-west corner', band_m=[E0, E1]))


def roof():
    outer, inner = rr(AX, AY, R), rr(IX, IY, IR)
    n = len(outer)
    b = Batch()
    for i in range(n):
        p, q = outer[i], outer[(i + 1) % n]
        b.beam('steel', (p[0], p[1], ZT), (q[0], q[1], ZT), .7, .7)                # perimeter truss top chord
        b.beam('steel', (p[0], p[1], ZF + .4), (q[0], q[1], ZT), .45)             # perimeter truss webs
        b.beam('steel', (q[0], q[1], ZF + .4), (p[0], p[1], ZT), .45)
        b.beam('steel', (p[0], p[1], ZF), (p[0], p[1], ZT), .45)
        pi, qi = inner[i], inner[(i + 1) % n]
        for z in (ZI0, ZI1):
            b.beam('steel', (pi[0], pi[1], z), (qi[0], qi[1], z), .8, .8)          # inner compression ring
        b.beam('steel', (pi[0], pi[1], ZI0), (qi[0], qi[1], ZI1), .4)
        b.beam('steel', (pi[0], pi[1], ZI0), (pi[0], pi[1], ZI1), .4)
        # Radial truss: top chord, bottom chord and a zigzag web.
        top = lambda f: (p[0] + (pi[0] - p[0]) * f, p[1] + (pi[1] - p[1]) * f, ZT + (ZI1 - ZT) * f)
        bot = lambda f: (p[0] + (pi[0] - p[0]) * f, p[1] + (pi[1] - p[1]) * f, ZF + .4 + (ZI0 - ZF - .4) * f)
        b.beam('steel', top(0), top(1), .5, .6)
        if i % 2:
            continue                                                           # odd bays carry a rafter only
        b.beam('steel', bot(0), bot(1), .4)
        k = 5
        for j in range(k):
            b.beam('steel', bot(j / k), top((j + 1) / k), .3)
            b.beam('steel', top((j + 1) / k), bot((j + 1) / k), .3)
        if i % 2 == 0:                                                         # cross bracing in the roof plane
            pj = outer[(i + 2) % n]; pij = inner[(i + 2) % n]
            for f0, f1 in ((0.0, .5), (.5, 1.0)):
                a0 = (p[0] + (pi[0] - p[0]) * f0, p[1] + (pi[1] - p[1]) * f0, ZT + (ZI1 - ZT) * f0 + .4)
                a1 = (pj[0] + (pij[0] - pj[0]) * f1, pj[1] + (pij[1] - pj[1]) * f1, ZT + (ZI1 - ZT) * f1 + .4)
                b.beam('steel', a0, a1, .2)
    for f in (.25, .5, .75):                                                 # purlin rings
        ring = lerp_ring(outer, inner, f)
        for i in range(n):
            p, q = ring[i], ring[(i + 1) % n]
            z = ZT + (ZI1 - ZT) * f + .38
            b.beam('steel', (p[0], p[1], z), (q[0], q[1], z), .22, .22)
    b.flush('roof steel')
    strip('Roof panels', [(p[0], p[1]) for p in outer], [(p[0], p[1]) for p in inner], ZT + .5, ZI1 + .5, 'glass', 'roof')
    C.CONTACTS.append(dict(name='Perimeter truss on the facade ring beam; radial trusses to the inner compression ring', perimeter_m=[ZF, ZT], inner_m=[ZI0, ZI1]))


def site():
    C.box('Plaza', (0, 0, .03), (2 * AX + 36.0, 2 * AY + 36.0, .06), 'paving', 'site', 0)
    C.box('South street', (0, -AY - 32.0, .01), (2 * AX + 120.0, 16.0, .02), 'asphalt', 'site', 0)
    C.box('East street', (AX + 32.0, 0, .01), (16.0, 2 * AY + 48.0, .02), 'asphalt', 'site', 0)
    C.box('West street', (-AX - 32.0, 0, .01), (16.0, 2 * AY + 48.0, .02), 'asphalt', 'site', 0)
    b = Batch()
    for x in range(-90, 91, 30):
        b.box('hardware', x, -AY - 21.0, 4.0, .2, .2, 8.0)
        b.box('hardware', x + .6, -AY - 21.0, 8.0, 1.4, .3, .2)
    b.flush('site lighting')
    for x in (-110.0, -70.0, 60.0, 100.0):
        street_tree(x, -AY - 22.5, z=.06, height=9.0, spread=2.4)
    for y in (-60.0, 0.0, 60.0):
        street_tree(-AX - 22.0, y, z=.06, height=9.0, spread=2.4)


def scale_review_scene():
    """Grow the excluded review ground and the camera range to a 200 m building; widen the review lights."""
    for o in C.bpy.data.objects:
        if o.type == 'CAMERA':
            o.data.clip_end = 2500.0
        elif o.type == 'LIGHT' and o.name.startswith('QA ') and o.name[3:] in ('key', 'fill', 'rear'):
            o.data.size = 80.0
    g = C.bpy.data.objects.get('QA ground - excluded')
    if g:
        g.scale = (6.0, 6.0, 1.0)


def build():
    scale_review_scene()
    site()
    pitch()
    bowl()
    concourse()
    facade()
    roof()
    C.CONTACTS.append(dict(name='Stadium: glazed concourse, ETFE and steel facade, seating bowl, truss roof ring', block=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(-260, -330, 300), fill=(320, -160, 200), rear=(-140, 300, 240), target=(0, 0, 14.0), gain=260.0)
