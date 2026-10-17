"""Campus lecture hall under a barrel vault, authored from the locked catalogue views of
campus_lecture_hall_complex / variant_0 (parametric_vaulted_pavilion).

Read from the pixels (the top view governs the plan): a near-square block on a street corner, streets
south and west. A full-height glazed ground floor behind white branching Y-columns, recessed under a
three-storey sculpted white composite-panel mass with horizontal slot windows. A screen of tall vertical
aluminium fins wraps the west face and turns the south-west corner. Over the whole block a barrel vault
spans east-west, springing from the top of the mass at the east and west edges, ringed by white arch
ribs: its crown a field of white pillowed membrane cushions on a rib grid, its lower flanks clear glazing
on the same grid. Under the vault four angular white masses with dark louvred sloping faces rise from the
roof terrace in a pinwheel. Wide steps and planting along the south front.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-vaulted-lecture-hall'
X0, X1, Y0, Y1 = -17.0, 17.0, -17.0, 17.0      # 34 x 34 m block (top view)
T = .30
G0 = .6                                         # podium above the plaza
Z1 = 7.2                                        # top of the double-height glazed ground floor
TM = .9                                         # deep white-mass carrier, so the slot windows read carved
ZT = 17.0                                       # top of the white mass, roof terrace
ZS = ZT + .6                                    # vault springing on beams over the outer parapet edges
VH = 12.0                                       # vault rise (semi-elliptic, flatter than a half-circle)
XV = X1 - .35                                   # vault half-span east-west, on the springing beams at the parapet edges
VY = (-12.5, 12.5)                              # vault length north-south; open ends
CROWN = 11.0                                    # half-width of the membrane crown; glazed flanks outside it
REC = 1.6                                       # ground-floor glazing recessed under the mass
EPS = .002
PALETTE = dict(wall=(.92, .91, .89), joint=(.84, .83, .81), trim=(.80, .81, .82),
    pale=(.90, .90, .89), stone=(.82, .81, .78), roof=(.78, .78, .76), sand=(.80, .79, .76),
    foundation=(.60, .60, .58), glass=(.56, .64, .68), hardware=(.30, .31, .33),
    interior=(.86, .82, .76), floor=(.66, .62, .56), timber=(.62, .46, .30), blue=(.20, .30, .40),
    planting=(.30, .44, .18), soil=(.22, .16, .10), concrete=(.74, .73, .70), white=(.96, .96, .95),
    membrane=(.93, .93, .92), fin=(.78, .79, .80), louvre=(.30, .31, .33), asphalt=(.30, .30, .31),
    vglass=(.70, .76, .80))


def manifest(version):
    h = ZS + VH + 1.0
    cams = G.camera_roster(X1 - X0 + 4.0, Y1 - Y0 + 4.0, h, [
        ('facade_close', (6.0, -40.0, 12.0), (6.0, Y0, 12.0), 45),
        ('architecture_close', (30.0, -34.0, 22.0), (8.0, Y0, 20.0), 45),
        ('glass_close', (0.0, -28.0, 3.0), (0.0, Y0 + REC, 3.2), 45),
        ('y_columns', (-6.0, -27.0, 3.0), (-2.0, Y0, 4.6), 40),
        ('fin_screen', (-36.0, -20.0, 10.0), (X0, -4.0, 10.0), 45),
        ('vault_ribs', (-6.0, -44.0, 36.0), (0.0, -4.0, ZS + 8.0), 45),
        ('roof_masses', (30.0, 30.0, 44.0), (0.0, 0.0, ZT + 3.0), 45),
        ('entrance_steps', (-12.0, -30.0, 3.0), (-4.0, Y0 - 1.0, 1.0), 45),
        ('interior', (6.0, -4.0, G0 + 1.7), (-8.0, Y0 + REC, G0 + 2.8), 40),
        ('rear_north', (0.0, 48.0, 14.0), (0.0, Y1, 14.0), 45)])
    for c in cams:                       # the locked front looks at the south-west corner from the street, at eye level
        if c['name'] == 'front':
            c['location'] = (-16.0, -56.0, 1.8); c['target'] = (2.0, -4.0, 14.0); c['lens'] = 26; c['whole'] = False
        elif c['name'] == 'front_corner':
            lx, ly, lz = c['location']; c['location'] = (-lx, ly, lz)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='campus_lecture_hall_complex/variant_0 (parametric_vaulted_pavilion)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0 + 1.6, depth=Y1 - Y0, height=h),
            observed_storeys=4, storey_programme='glazed ground-floor lobby, three storeys of lecture halls and seminar rooms in the white mass, a vaulted hall and roof terrace above',
            plan='34 x 34 m block (top view); vault 30 m east-west by 23 m north-south over the middle of the roof; four angular masses in a pinwheel under its flanks and ends; fin screen on the west face',
            facade='white composite panels with horizontal slot windows; tall vertical aluminium fins on the west face turning the south-west corner; full-height ground-floor glazing behind branching Y-columns',
            levels_m=[G0, Z1, ZT], vault_m=dict(springing=ZS, rise=VH),
            inferred='storey heights and interiors are teaching assumptions; the north face is not visible in any source and repeats the visible grammar'),
        roof_contract=dict(type='barrel vault of pillowed membrane with glazed flanks on white arch ribs over a roof terrace with four sloped louvred masses', datum_m=ZT, crowns_m=[ZS + VH]),
        identity_contract=dict(owner='full-width barrel vault with pillowed crown and glazed flanks, white sculpted mass, fin screen, Y-column glazed base, pinwheel louvred masses'),
        material_contract=dict(profile='source-palette clay: white composite panel, white ribs, white membrane cushions, clear glass, aluminium fins, dark louvres, pale paving', textured_keeper=False),
        programme_contract=dict(storeys=4, ground='lobby and foyer', upper='lecture theatres and seminar rooms', vault='multi-purpose hall and roof terrace'),
        contact_contract=['Podium on the plaza with steps', 'White mass on the ground-floor core and Y-columns', 'Vault ribs springing from the top of the mass', 'Louvred masses on the roof terrace'],
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


# ---- campus lecture hall under a barrel vault ----

class Batch:
    def __init__(self):
        self.g = {}

    def box(self, role, cx, cy, cz, sx, sy, sz):
        V, F = self.g.setdefault(role, ([], []))
        o = len(V)
        V.extend((cx + du * sx / 2, cy + dd * sy / 2, cz + dz * sz / 2) for dz in (-1, 1) for du, dd in ((-1, -1), (1, -1), (1, 1), (-1, 1)))
        F.extend(tuple(o + i for i in face) for face in C.BOX_FACES)

    def flush(self, module):
        for role, (V, F) in self.g.items():
            if F:
                C.mesh(f'{module} {role}', V, F, role, module)
        self.g = {}


def vz(x):
    """Height of the vault surface over x (east-west section): a semi-ellipse springing at the parapet edges."""
    s = max(0.0, 1.0 - (x / XV) ** 2)
    return ZS + VH * s ** .5


def vnormal(x):
    h = .01
    dz = (vz(min(XV, x + h)) - vz(max(-XV, x - h))) / (min(XV, x + h) - max(-XV, x - h))
    n = math.hypot(dz, 1.0)
    return (-dz / n, 1.0 / n)


def shell(name, xs, ys, role, module, t=.14):
    """Thin shell over the vault surface between the x stations xs and the y stations ys."""
    nx, ny = len(xs), len(ys)
    vs = []
    for off in (0.0, -t):
        for j, y in enumerate(ys):
            for i, x in enumerate(xs):
                vs.append((x, y, vz(x) + off))
    fs = []
    L = nx * ny
    for j in range(ny - 1):
        for i in range(nx - 1):
            a, b, c, d = j * nx + i, j * nx + i + 1, (j + 1) * nx + i + 1, (j + 1) * nx + i
            fs.append((a, d, c, b)); fs.append((L + a, L + b, L + c, L + d))
    for i in range(nx - 1):                                              # ends
        for j in (0, ny - 1):
            a, b = j * nx + i, j * nx + i + 1
            fs.append((a, b, L + b, L + a) if j == 0 else (b, a, L + a, L + b))
    for j in range(ny - 1):                                              # long edges
        for i in (0, nx - 1):
            a, b = j * nx + i, (j + 1) * nx + i
            fs.append((b, a, L + a, L + b) if i == 0 else (a, b, L + b, L + a))
    return C.mesh(name, vs, fs, role, module)


def pillows(xs, ys, bulge=.55, m=4):
    """Pillowed membrane cushions, one per rib-grid cell, bulging along the vault normal."""
    vs, fs = [], []
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            o = len(vs)
            for b_ in range(m + 1):
                for a_ in range(m + 1):
                    u, v = a_ / m, b_ / m
                    x = xs[i] + (xs[i + 1] - xs[i]) * u
                    y = ys[j] + (ys[j + 1] - ys[j]) * v
                    k = bulge * math.sin(math.pi * u) * math.sin(math.pi * v) + .03
                    nx_, nz_ = vnormal(x)
                    vs.append((x + nx_ * k, y, vz(x) + nz_ * k))
            for b_ in range(m):
                for a_ in range(m):
                    q = o + b_ * (m + 1) + a_
                    fs.append((q, q + 1, q + m + 2, q + m + 1))
    C.mesh('Vault membrane cushions', vs, fs, 'membrane', 'vault')


def vault():
    ya, yb = VY
    ny = 8
    ys = [ya + (yb - ya) * j / ny for j in range(ny + 1)]
    nc = 10
    xc = [-CROWN + 2 * CROWN * i / nc for i in range(nc + 1)]
    shell('Vault membrane crown', xc, ys, 'membrane', 'vault', t=.16)
    pillows(xc, ys)
    flank = []
    for side in (-1, 1):
        xs = [side * (CROWN + (XV - CROWN) * i / 6) for i in range(7)]
        flank += xs[1:]
        if side < 0:
            xs = xs[::-1]
        shell('Vault glazed flank', xs, ys, 'vglass', 'vault', t=.05)
    # Rib grid: arch ribs across at every y station (heavy at the open ends), straight ribs along at every x station.
    def arch(y, w, d, name):
        n = 32
        pts = [(-XV + 2 * XV * k / n) for k in range(n + 1)]
        for a, c in zip(pts, pts[1:]):
            C.beam(name, (a, y, vz(a) + d / 2 - .05), (c, y, vz(c) + d / 2 - .05), w, d, 'white', 'vault ribs')
    for j, y in enumerate(ys):
        end = j in (0, ny)
        arch(y, .7 if end else .22, .9 if end else .26, 'Vault end rib' if end else 'Vault arch rib')
        for x in (-XV, XV):                                               # rib feet bedded on the springing beams
            C.box('Vault rib foot', (x, y, ZS + .45), (.75, (.9 if end else .45), .9), 'white', 'vault ribs', 0)
    for x in sorted(set([round(v, 3) for v in xc + flank])):
        if abs(abs(x) - XV) < .01:
            continue
        C.beam('Vault longitudinal rib', (x, ya, vz(x) + .08), (x, yb, vz(x) + .08), .18, .24, 'white', 'vault ribs')
    for x in (-XV, XV):                                                   # springing beams on the parapet edges
        C.box('Vault springing beam', (x, 0, ZT + .3), (.7, yb - ya + 1.4, .6), 'white', 'vault ribs', 0)
    C.CONTACTS.append(dict(name='Vault ribs spring from beams on the outer parapet edges; ends open', springing_m=ZS))


def mass_face(f, lo, hi, holes, z0, z1, tag):
    f.wall(f'{tag} white carrier', lo, hi - EPS, z0, z1, depth=TM, role='wall', holes=holes)
    m = Merge(f)
    for k in range(1, int((z1 - z0) / 1.6) + 1):                       # panel joints
        z = z0 + k * 1.6
        if z < z1 - .2:
            m.box('joint', (lo + hi) / 2, -.004, z, hi - lo - 2 * EPS, .008, .03)
    for h in holes:
        reveal(m, f, h, inset=.62, role='white')                          # deep carved slot reveals
        framed(m, f, h, cols=max(2, round(h['w'] / 1.6)), rows=1, inset=.62, occupied='seminar room')
    m.flush(tag)


def white_mass():
    hw = (X1 - X0) / 2
    s = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'mass south')
    slots = [hole('south slot upper', 8.5, 13.2, 7.0, 1.4, kind='slot'), hole('south slot lower', 8.5, 8.6, 7.0, 1.4, kind='slot')]
    mass_face(s, -hw, hw, slots, Z1, ZT, s.label)
    e = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'mass east')
    slots = [hole('east slot upper', -4.0, 13.2, 8.0, 1.4, kind='slot'), hole('east slot lower', -4.0, 8.6, 8.0, 1.4, kind='slot')]
    mass_face(e, -hw + TM, hw - TM, slots, Z1, ZT, e.label)
    n = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'mass north')
    slots = [hole('north slot', 0.0, 13.2, 10.0, 1.4, kind='slot')]
    mass_face(n, -hw, hw, slots, Z1, ZT, n.label)
    w = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'mass west')
    mass_face(w, -hw + TM, hw - TM, [], Z1, ZT, w.label)
    inner = (X1 - X0 - 2 * TM, Y1 - Y0 - 2 * TM)
    C.box('Mass soffit', (0, 0, Z1 - .3), (X1 - X0 - 2 * REC - .02, Y1 - Y0 - 2 * REC - .02, .2), 'wall', 'mass', 0)
    C.box('Mass soffit outer', (0, 0, Z1 - .1), (X1 - X0 - .02, Y1 - Y0 - .02, .2), 'wall', 'mass', 0)
    C.box('Roof terrace', (0, 0, ZT - .15), (inner[0], inner[1], .3), 'floor', 'mass', 0)
    C.box('Roof terrace paving', (0, 0, ZT + .01), (inner[0] - .02, inner[1] - .02, .02), 'roof', 'mass', 0)
    C.box('Mass floor', (0, 0, 12.1 - .15), (inner[0], inner[1], .3), 'floor', 'mass', 0)
    for z in (Z1, 12.1):
        C.qa_room_light(f'Seminar {z:.0f}', (8.0, Y0 + 4.0, z + 2.6), 80, 6.0)
        C.qa_room_light(f'Seminar east {z:.0f}', (X1 - 4.0, -4.0, z + 2.6), 60, 5.0)
    # Fin screen on the west face, turning the south-west corner onto the south face; standing on the podium.
    b = Batch()
    for k in range(int((Y1 - Y0 - 1.0) / .75) + 1):
        y = Y0 + .5 + k * .75
        dz = .4 * math.sin(k * .45)
        b.box('fin', X0 - .75, y, (G0 + ZT + dz) / 2, .9, .14, ZT + dz - G0)
    for k in range(0, 9):
        x = X0 - .25 + k * .75
        b.box('fin', x, Y0 - .75, (G0 + ZT) / 2, .14, .9, ZT - G0)
    for z in (Z1 - .3, ZT - .4):                                          # fin rails, meeting at the corner and tied back
        b.box('hardware', X0 - .45, (Y0 - .52 + Y1 - .3) / 2, z, .14, Y1 - .3 - (Y0 - .52), .12)
        b.box('hardware', (X0 - .38 + X0 + 6.2) / 2, Y0 - .45, z, X0 + 6.2 - (X0 - .38), .14, .12)
    b.flush('fin screen')
    C.CONTACTS.append(dict(name='Fin screen standing on the podium, on rails tied back to the white mass', face='west'))


def louvred_masses():
    """Four large angular white masses in a rotated pinwheel on the roof terrace, rising inward under the vault; each
    sloping face a dark louvre panel in a white frame, with light vertical louvre lines."""
    b = Batch()
    for i, (cx, cy) in enumerate(((-8.0, -11.6), (8.5, -11.6), (8.0, 11.6), (-8.5, 11.6))):   # astride the open vault ends
        th = math.atan2(-cy, -cx) + math.radians(28.0)
        cu, su = math.cos(th), math.sin(th)
        L, W = 7.0, 6.0
        lo_z, hi_z = ZT + 2.2, ZT + 8.4

        def P(u, v):
            return (cx + u * cu - v * su, cy + u * su + v * cu)

        foot = [P(-L / 2, -W / 2), P(L / 2, -W / 2), P(L / 2, W / 2), P(-L / 2, W / 2)]
        tops = []
        for (x, y), u in zip(foot, (-L / 2, L / 2, L / 2, -L / 2)):
            z = lo_z + (hi_z - lo_z) * (u + L / 2) / L
            z = min(z, vz(max(-XV, min(XV, x))) - 1.4)                  # always clear of the vault
            tops.append(z)
        vs = [(x, y, ZT) for x, y in foot] + [(x, y, z) for (x, y), z in zip(foot, tops)]
        fs = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        C.mesh(f'Roof mass {i}', vs, fs, 'white', 'roof masses')

        def top_at(u, v, lift):
            f_u = (u + L / 2) / L; f_v = (v + W / 2) / W
            za = tops[0] + (tops[1] - tops[0]) * f_u
            zb = tops[3] + (tops[2] - tops[3]) * f_u
            x, y = P(u, v)
            return (x, y, za + (zb - za) * f_v + lift)

        ins = .45
        pv = [top_at(u, v, .02) for u, v in ((-L / 2 + ins, -W / 2 + ins), (L / 2 - ins, -W / 2 + ins), (L / 2 - ins, W / 2 - ins), (-L / 2 + ins, W / 2 - ins))]
        pv += [(x, y, z + .06) for x, y, z in pv]
        C.mesh(f'Roof mass louvre panel {i}', pv, fs, 'louvre', 'roof masses')
        nlines = int((W - 2 * ins) / .45)
        for k in range(1, nlines):
            v = -W / 2 + ins + (W - 2 * ins) * k / nlines
            a, c = top_at(-L / 2 + ins, v, .1), top_at(L / 2 - ins, v, .1)
            C.beam('Louvre blade line', a, c, .05, .03, 'fin', 'roof masses')
    C.qa_room_light('Vault hall', (0, 0, ZT + 6.0), 260, 12.0)
    C.CONTACTS.append(dict(name='Four angular masses in a rotated pinwheel on the roof terrace, kept clear under the vault'))


def ground_floor():
    # Recessed double-height glazing on all four sides, under the mass; Y-columns on the south and east fronts.
    for name, f, lo, hi in (('south', C.Face((0, Y0 + REC, 0), (1, 0, 0), (0, 1, 0), 'ground south'), X0 + REC, X1 - REC),
                            ('east', C.Face((X1 - REC, 0, 0), (0, 1, 0), (-1, 0, 0), 'ground east'), Y0 + REC + T, Y1 - REC - T),
                            ('north', C.Face((0, Y1 - REC, 0), (-1, 0, 0), (0, -1, 0), 'ground north'), -(X1 - REC), -(X0 + REC)),
                            ('west', C.Face((X0 + REC, 0, 0), (0, -1, 0), (1, 0, 0), 'ground west'), -(Y1 - REC - T), -(Y0 + REC + T))):
        span = hi - lo
        n = max(1, round(span / 3.2))
        p = span / n
        holes = []
        for k in range(n):
            u = lo + p * (k + .5)
            if name == 'south' and k in (n // 2 - 1, n // 2):
                holes.append(hole(f'{name} entry {k}', u, G0, p - .3, 3.0, kind='door'))
                holes.append(hole(f'{name} entry transom {k}', u, G0 + 3.25, p - .3, Z1 - .5 - G0 - 3.25))
            else:
                holes.append(hole(f'{name} glazing {k}', u, G0, p - .3, Z1 - .5 - G0))
        f.wall(f'{name} ground carrier', lo, hi - EPS, G0, Z1 - .4, depth=T, role='trim', holes=holes)
        m = Merge(f)
        for h in holes:
            door = h.get('kind') == 'door'
            framed(m, f, h, cols=2, rows=1 if door or h['h'] < 4 else 4, inset=.12, occupied='lobby', kind=h.get('kind', 'window'), lite=name == 'north')
        m.flush(f.label)
    trunk = G0 + 3.4
    for x in (-10.0, -3.5, 3.0, 9.5):                                    # branching Y-columns, south front
        y = Y0 + .6
        C.rod('Y column trunk', (x, y, G0), (x, y, trunk), .22, 'white', 'columns', 12)
        C.rod('Y column node', (x, y, trunk - .35), (x, y, trunk + .35), .34, 'white', 'columns', 12)
        for e in (-1, 1):
            C.beam('Y column branch', (x, y, trunk - .1), (x + e * 2.2, y, Z1 - .25), .3, .3, 'white', 'columns')
    for yy in (-8.0, 0.0, 8.0):                                          # and on the east front
        x = X1 - .6
        C.rod('Y column trunk', (x, yy, G0), (x, yy, trunk), .22, 'white', 'columns', 12)
        C.rod('Y column node', (x, yy, trunk - .35), (x, yy, trunk + .35), .34, 'white', 'columns', 12)
        for e in (-1, 1):
            C.beam('Y column branch', (x, yy, trunk - .1), (x, yy + e * 2.2, Z1 - .25), .3, .3, 'white', 'columns')
    C.box('Podium', (0, 0, G0 / 2), (X1 - X0 + 3.2, Y1 - Y0 + 3.2, G0), 'stone', 'podium', 0)
    for k in range(3):                                                   # wide steps along the south front
        top = G0 * (3 - k - 1) / 3 + G0 / 3
        C.box('Podium step', (-1.0, Y0 - 1.6 - .2 - k * .4, top / 2), (24.0, .4, top), 'stone', 'podium', 0)
    C.box('Lobby core', (6.0, 7.0, (G0 + Z1 - .4) / 2), (8.0, 6.0, Z1 - .4 - G0), 'wall', 'lobby', 0)
    C.beam('Lobby stair', (-6.0, -6.0, G0 + .1), (-6.0, 5.0, Z1 - .5), 2.0, .3, 'white', 'lobby')
    C.qa_room_light('Lobby', (0, -6.0, Z1 - 1.5), 220, 9.0)
    C.qa_room_light('Lobby west', (-9.0, -9.0, G0 + 3.0), 120, 6.0)
    C.CONTACTS.append(dict(name='White mass on the lobby core and Y-columns over recessed double-height glazing; podium with steps on the plaza', recess_m=REC))


def site():
    C.box('Plaza', (0, -1.5, .03), (X1 - X0 + 12.0, Y1 - Y0 + 9.0, .06), 'sand', 'site', 0)
    C.box('South street', (0, Y0 - 13.0, .01), (X1 - X0 + 40.0, 10.0, .02), 'asphalt', 'site', 0)
    C.box('West street', (X0 - 11.0, 0, .01), (10.0, Y1 - Y0 + 8.0, .02), 'asphalt', 'site', 0)
    for x0, x1 in ((-14.0, -10.0), (8.0, 14.0)):
        C.box('Planter bed', ((x0 + x1) / 2, Y0 - 4.6, .2), (x1 - x0, 1.6, .34), 'planting', 'site', 0)
        for k in range(int(x1 - x0)):
            A.shrub(x0 + .5 + k, Y0 - 4.6, .36, .6)
    for x, y in ((-20.0, -12.0), (-20.0, 4.0), (20.0, -20.0), (-6.0, -21.0)):
        street_tree(x, y, z=.06, height=8.0, spread=2.2)


def build():
    site()
    ground_floor()
    white_mass()
    louvred_masses()
    vault()
    C.CONTACTS.append(dict(name='Lecture hall: white mass over glazed base, fin screen, barrel vault with louvred masses beneath', block=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(-60, -80, 70), fill=(70, -40, 50), rear=(-30, 70, 60), target=(0, 0, 14.0), gain=18.0)
