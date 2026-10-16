"""Garden-court senior residence, authored from the locked catalogue views of
senior_living_complex / variant_0 (senior_garden_courtyard).

Read from the pixels (the top view governs the plan): a ring of red-brick residence blocks round a
landscaped court. Two three-storey pavilions at the north (west and east) and one at the south-west,
a long east wing and a long south wing, all under copper standing-seam roofs: the pavilions hipped to
a flat top carrying rooftop units, the wings hipped to a ridge, every slope carrying gabled dormers.
One-storey brick loggias with round-arched openings and copper roofs link the blocks; on the link
between the north pavilions stands an octagonal glazed garden room with a copper roof and a glass
cupola. White-framed double-hung windows, iron balconies over arched garden doors on the court faces.
The court: brick paths, lawns and rose beds, a tiered fountain, a fenced garden of raised timber beds,
a timber pergola over a dining terrace. A circular lawn with a fountain and a drive loop lie north.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-garden-court-senior-residence'
T = .30
G0 = .15
FH = 3.3
EAVE = G0 + 3 * FH            # 10.05
LINK_EAVE = 4.4
EPS = .002
# Blocks (x0, x1, y0, y1) read from the top view at 0.10 m/px, origin at the court centre.
NW = (-31.5, -12.0, 9.0, 32.5)
NE = (14.0, 32.5, 9.0, 32.0)
SW = (-37.0, -15.0, -20.0, -5.0)
EW = (25.0, 36.5, -29.5, 2.5)
SO = (-14.5, 17.0, -31.5, -20.0)
LINKS = dict(north_west=(-12.0, -4.6, 9.4, 12.6), north_east=(4.6, 14.0, 9.4, 12.6), west=(-19.0, -15.0, -5.0, 9.0),
             east=(27.5, 31.5, 2.5, 9.0), south_west=(-21.0, -14.5, -28.5, -20.0), south_east=(17.0, 25.0, -29.5, -21.5))
HUB = (0.0, 9.0, 5.0)         # octagonal garden room centre and circumradius
HUB_H = 4.8
PALETTE = dict(wall=(.56, .29, .21), joint=(.42, .21, .16), trim=(.92, .90, .86),
    pale=(.90, .88, .84), stone=(.78, .74, .66), roof=(.80, .50, .32), sand=(.66, .46, .38),
    foundation=(.44, .44, .43), glass=(.50, .58, .62), hardware=(.12, .12, .12),
    interior=(.82, .78, .70), floor=(.48, .44, .40), timber=(.56, .40, .24), blue=(.14, .22, .28),
    planting=(.30, .46, .18), soil=(.24, .17, .10), concrete=(.66, .64, .60), membrane=(.80, .80, .78),
    copper=(.80, .50, .32), water=(.42, .56, .62), rose=(.70, .30, .36), lawn=(.34, .50, .20))


def manifest(version):
    h = EAVE + 4.2
    cams = G.camera_roster(74.0, 64.0, h, [
        ('facade_close', (-21.0, 0.0, 6.0), (-22.0, 9.0, 6.5), 40),
        ('architecture_close', (0.0, -12.0, 9.0), (0.0, 9.0, 5.0), 45),
        ('glass_close', (0.0, -2.5, 2.4), (0.0, 4.6, 2.6), 45),
        ('loggia_arcade', (-3.0, 1.0, 2.0), (-9.0, 9.4, 2.6), 45),
        ('dormer_roof', (-2.0, 2.0, 18.0), (-14.0, 20.0, 12.0), 45),
        ('hub_cupola', (6.0, -6.0, 14.0), (0.0, 9.0, 10.0), 40),
        ('garden_beds', (1.0, -19.0, 6.0), (6.0, -12.0, .6), 45),
        ('pergola_terrace', (6.5, -.5, 2.2), (17.0, -2.5, 2.0), 45),
        ('interior', (2.6, 11.0, 1.7), (-1.0, 5.0, 1.6), 60),
        ('court_view', (2.0, -18.5, 15.0), (2.0, 0.0, 0.0), 24)])
    r = 74.0 * 1.7
    for c in cams:          # the locked front and oblique look north over the court from above the south wing
        if c['name'] == 'front':
            c['location'] = (0.0, -r * .60, h * 3.4); c['target'] = (0.0, 2.0, 3.0)
        elif c['name'] == 'front_corner':
            c['location'] = (-r * .20, -r * .60, h * 4.8); c['target'] = (0.0, 0.0, 3.0)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='senior_living_complex/variant_0 (senior_garden_courtyard)',
        measurement_contract=dict(dimensions_m=dict(width=74.0, depth=64.0, height=h + 2.6),
            observed_storeys=3, storey_programme='three residential storeys under hipped copper roofs with dormers; one-storey linking loggias; one-storey octagonal garden room',
            plan='ring of five blocks round a 39 x 27 m court (top view at 0.10 m/px): north-west pavilion 19.5 x 23.5 m, north-east pavilion 18.5 x 23 m, south-west pavilion 22 x 15 m, east wing 11.5 x 32 m, south wing 31.5 x 11.5 m; six one-storey loggia links 4 to 8 m wide; octagonal garden room 10 m across on the north link',
            roofs='pavilions hipped at about 34 degrees to a flat top with rooftop units; wings hipped to a ridge; gabled dormers on every slope; loggias under hipped copper roofs; garden room under an eight-sided copper roof with a glazed cupola',
            facade='red brick with stone sills, white double-hung windows on a 3.6 m bay, arched garden doors with iron balconies above on the court faces',
            levels_m=[G0, G0 + FH, G0 + 2 * FH], eave_m=EAVE, link_eave_m=LINK_EAVE,
            inferred='storey height and interiors are teaching assumptions; the outer faces of the ring are not visible in the front or oblique and repeat the visible grammar; the front and oblique disagree on block positions, so the top view governs the plan'),
        roof_contract=dict(type='copper standing-seam hips; flat membrane tops on the pavilions', datum_m=EAVE, crowns_m=[EAVE + 4.0, HUB_H + 6.5]),
        identity_contract=dict(owner='brick pavilions and wings with hipped copper roofs and dormers round a garden court, arched brick loggias, octagonal glazed garden room with copper roof and glass cupola, fountain, raised garden beds, pergola'),
        material_contract=dict(profile='source-palette clay: red brick with recessed courses, copper roofs, white window frames and trim, black iron balconies and fences, brick paths, lawn and planting, timber beds and pergola', textured_keeper=False),
        programme_contract=dict(storeys=3, residences='assisted-living suites off double-loaded corridors', common='octagonal garden room (lounge and dining) on the north link; loggias as covered walks', court='walking paths, fountain, raised therapy garden, pergola dining'),
        contact_contract=['Grade-zero slabs, lawns and paths', 'Loggia links butted between the blocks', 'Garden room on the north link', 'Dormers seated on the roof slopes', 'Balconies bracketed off the court faces'],
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


# ---- garden-court senior residence ----

OV = .5          # eave overhang
BAY = 3.6


class Batch:
    """Collect arbitrary boxes and fans into one mesh per role (keeps the object count low)."""
    def __init__(self):
        self.g = {}

    def add(self, role, vs, fs):
        V, F = self.g.setdefault(role, ([], []))
        o = len(V); V.extend(vs); F.extend(tuple(o + i for i in f) for f in fs)

    def flush(self, module):
        for role, (V, F) in self.g.items():
            if F:
                C.mesh(f'{module} {role}', V, F, role, module)
        self.g = {}


def rib(b, p0, p1, t, role='roof'):
    """Standing seam: a thin bar on the roof surface from p0 up to p1 (t: unit tangent along the eave)."""
    vs = []
    for dz in (-.02, .05):
        for su, sd in ((-1, 0), (1, 0), (1, 1), (-1, 1)):
            p = p1 if sd else p0
            vs.append((p[0] + t[0] * su * .025, p[1] + t[1] * su * .025, p[2] + dz))
    b.add(role, vs, C.BOX_FACES)


def hip_roof(name, x0, x1, y0, y1, z, rise, flat=None, seams=True, dormers=(), module='roofs'):
    """Hipped copper roof from an eave rectangle (with overhang) to a flat top (flat = inset) or a ridge."""
    ex0, ex1, ey0, ey1 = x0 - OV, x1 + OV, y0 - OV, y1 + OV
    W, D = ex1 - ex0, ey1 - ey0
    run = flat if flat is not None else min(W, D) / 2 - .01
    k = rise / run
    lower = [(ex0, ey0), (ex1, ey0), (ex1, ey1), (ex0, ey1)]
    upper = [(ex0 + run, ey0 + run), (ex1 - run, ey0 + run), (ex1 - run, ey1 - run), (ex0 + run, ey1 - run)]
    strip(name, lower, upper, z, z + rise, 'roof', module)
    if flat is not None:
        C.box(name + ' flat top', ((x0 + x1) / 2, (y0 + y1) / 2, z + rise - .06), (W - 2 * run + .12, D - 2 * run + .12, .16), 'membrane', module, 0)
    # Soffit ring closing the eave between wall face and fascia.
    q = .05                                              # held back from the shell's eave face (coplanar faces render black)
    for (a, bb, c, d) in ((ex0 + q, ex1 - q, ey0 + q, y0), (ex0 + q, ex1 - q, y1, ey1 - q), (ex0 + q, x0, y0, y1), (x1, ex1 - q, y0, y1)):
        C.box(name + ' soffit', ((a + bb) / 2, (c + d) / 2, z - .12), (bb - a, d - c, .10), 'trim', module, 0)
    if seams:
        b = Batch()
        for (sx, sy), (tx, ty), L, (nx, ny) in ((((ex0, ey0)), (1, 0), W, (0, 1)), (((ex1, ey1)), (-1, 0), W, (0, -1)),
                                                (((ex1, ey0)), (0, 1), D, (-1, 0)), (((ex0, ey1)), (0, -1), D, (1, 0))):
            n = int(L / 1.0)
            for i in range(1, n):
                u = L * i / n
                reach = min(run, u, L - u) - .05
                if reach <= .1:
                    continue
                p0 = (sx + tx * u, sy + ty * u, z + .01)
                p1 = (p0[0] + nx * reach, p0[1] + ny * reach, z + .01 + reach * k)
                rib(b, p0, p1, (tx, ty))
        b.flush(name + ' standing seams')
    for side, u in dormers:
        dormer(name, side, u, ex0, ex1, ey0, ey1, z, k)


def dormer(name, side, u, ex0, ex1, ey0, ey1, z, k, w=1.5, hw=1.2, gr=.7, s_f=1.3, depth=1.5):
    """Gabled copper dormer seated on a slope: pentagon prism into the roof, white gable trim, glazed sash."""
    zb = z + s_f * k - .2
    pent = [(u - w / 2, zb), (u + w / 2, zb), (u + w / 2, zb + hw), (u, zb + hw + gr), (u - w / 2, zb + hw)]
    if side in ('south', 'north'):
        yf = ey0 + s_f if side == 'south' else ey1 - s_f
        lo, hi = (yf, yf + depth) if side == 'south' else (yf - depth, yf)
        C.prism(f'{name} dormer', pent, 'y', lo, hi, 'roof', 'dormers')
        sgn = -1 if side == 'south' else 1
        f = C.Face((0, yf, 0), (1, 0, 0), (0, -sgn, 0), name + ' dormer')
        uu = u
    else:
        xf = ex0 + s_f if side == 'west' else ex1 - s_f
        lo, hi = (xf, xf + depth) if side == 'west' else (xf - depth, xf)
        C.prism(f'{name} dormer', pent, 'x', lo, hi, 'roof', 'dormers')
        sgn = -1 if side == 'west' else 1
        f = C.Face((xf, 0, 0), (0, 1, 0), (-sgn, 0, 0), name + ' dormer')
        uu = u
    m = Merge(f)
    m.box('trim', uu, -.03, zb + hw * .55, w - .45, .05, hw * .9)                  # white sash surround
    m.box('glass', uu, -.06, zb + hw * .55, w - .75, .02, hw * .7)
    m.box('trim', uu, -.08, zb + hw * .55, w - .75, .03, .05)                       # meeting rail of the double-hung sash
    m.flush('dormers')


def arch_fill(b, f, u, zs, r, d0, d1, role='wall', n=7):
    """Brick spandrels in the two top corners of a rectangular hole, leaving a round-headed opening."""
    for s in (-1, 1):
        corner = (u + s * r, zs + r)
        pts = [(u + s * r, zs)] + [(u + s * r * math.cos(a), zs + r * math.sin(a)) for a in (math.pi / 2 * i / n for i in range(1, n))] + [(u, zs + r)]
        vs = [f.p(pu, d, pz) for d in (d0, d1) for pu, pz in [corner] + pts]
        m = len(pts) + 1
        fs = []
        for i in range(1, m - 1):
            fs.append((0, i, i + 1) if s < 0 else (0, i + 1, i))
            fs.append((m, m + i + 1, m + i) if s < 0 else (m, m + i, m + i + 1))
        loop = list(range(m))
        for i in range(m):
            a, c = loop[i], loop[(i + 1) % m]
            fs.append((a, c, c + m, a + m) if s > 0 else (c, a, a + m, c + m))
        b.add(role, vs, fs)


def arch_ring(b, f, u, zs, r0, r1, d0, d1, role='trim', n=10):
    vs, fs = [], []
    for i in range(n + 1):
        a = math.pi * i / n
        for rr in (r0, r1):
            for d in (d0, d1):
                vs.append(f.p(u + rr * math.cos(a), d, zs + rr * math.sin(a)))
    for i in range(n):
        o, q = 4 * i, 4 * (i + 1)
        fs += [(o + 0, o + 2, q + 2, q + 0), (o + 1, q + 1, q + 3, o + 3), (o + 0, q + 0, q + 1, o + 1), (o + 2, o + 3, q + 3, q + 2)]
    b.add(role, vs, fs)


def brick_face(f, lo, hi, court=False, balcony_u=None, lite=False, skip=(), ext=0.0):
    """Three-storey brick elevation: double-hung windows on a 3.6 m bay, arched garden door with an iron balcony over it."""
    span = hi - lo
    n = max(1, int(span / BAY))
    us = [lo + span * (i + .5) / n for i in range(n)]
    holes, arched = [], []
    for fi in range(3):
        z = G0 + fi * FH
        for k, u in enumerate(us):
            if fi == 0 and any(u + .9 > a and u - .9 < c for a, c in skip):
                continue                                         # ground bay behind a loggia that abuts this face
            if fi == 1 and any(u + .9 > a - OV - 2.0 and u - .9 < c + OV + 2.0 for a, c in skip):
                continue                                         # second-storey bays the loggia's hipped roof would reach
            if balcony_u is not None and abs(u - balcony_u) < .1:
                if fi == 0:
                    h = hole(f'{f.label} garden door', u, G0, 1.6, 2.1 + .8, kind='arched'); arched.append(h)
                elif fi == 1:
                    h = hole(f'{f.label} balcony door', u, z + .05, 1.3, 2.35, kind='door')
                else:
                    h = hole(f'{f.label} f3 window {k}', u, z + .65, 1.25, 1.85)
            else:
                h = hole(f'{f.label} f{fi + 1} window {k}', u, z + (.65 if fi == 2 else .85), 1.25, 1.85)
            holes.append(h)
    f.wall(f'{f.label} brick carrier', lo, hi - EPS, G0, EAVE, depth=T, holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, G0 + .02, EAVE - .3, holes, spacing=.2 if not lite else .4)
    m = Merge(f)
    b = Batch()
    for h in holes:
        if h.get('kind') == 'arched':
            arch_fill(b, f, h['u'], G0 + 2.1, .8, 0, T)
            framed(m, f, dict(h, h=2.1), cols=2, rows=2, inset=.14, occupied='residents lounge', kind='garden door')
            arch_ring(b, f, h['u'], G0 + 2.1, .8, 1.0, -.05, .02, 'joint', n=12)
            m.box('glass', h['u'], .16, G0 + 2.1 + .3, 1.4, .01, .55)                   # fanlight behind the arch
        elif h.get('kind') == 'door':
            framed(m, f, h, cols=2, rows=1, inset=.14, occupied='suite', kind='balcony door')
            iron_balcony(m, f, h['u'], h['z'] - .05, 3.0, depth=.9, spacing=.16)
        else:
            framed(m, f, h, cols=1, rows=2, inset=.12, occupied='suite', lite=lite)
            m.box('stone', h['u'], -.04, h['z'] - .06, h['w'] + .16, .14, .12)
            if not lite:
                m.box('stone', h['u'], -.03, h['z'] + h['h'] + .12, h['w'] + .24, .10, .24)   # flat stone lintel
    # Stone water table, left out where a loggia abuts; end faces return round the corners (ext) a step higher than
    # the neighbouring face's table so no two faces share a plane.
    cuts = sorted(skip)
    segs, a = [], lo - ext
    for c0, c1 in cuts:
        segs.append((a, c0)); a = max(a, c1)
    segs.append((a, hi + ext))
    for a, c in segs:
        if c - a > .5:
            m.box('stone', (a + c) / 2, -.05, G0 + .25 + (.01 if ext else 0), c - a, T + .10, .50 + (.02 if ext else 0))
    m.box('trim', (lo + hi) / 2, -.10, EAVE - .22, span - 2 * EPS, T + .20, .26)            # white frieze under the soffit
    m.flush('brick facades')
    b.flush(f.label + ' arches')
    return holes


def block(name, box, court_sides, balcony_sides=(), lite_sides=(), flat=None, rise=4.0, dormer_step=4.0):
    x0, x1, y0, y1 = box
    hw, hd = (x1 - x0) / 2, (y1 - y0) / 2
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    faces = dict(south=(C.Face((cx, y0, 0), (1, 0, 0), (0, 1, 0), name + ' south'), -hw, hw, lambda u: cx + u),
                 north=(C.Face((cx, y1, 0), (-1, 0, 0), (0, -1, 0), name + ' north'), -hw, hw, lambda u: cx - u),
                 east=(C.Face((x1, cy, 0), (0, 1, 0), (-1, 0, 0), name + ' east'), -hd + T, hd - T, lambda u: cy + u),
                 west=(C.Face((x0, cy, 0), (0, -1, 0), (1, 0, 0), name + ' west'), -hd + T, hd - T, lambda u: cy - u))
    for side, (f, lo, hi, _) in faces.items():
        span = hi - lo
        n = max(1, int(span / BAY))
        mid = lo + span * ((n // 2) + .5) / n
        skip = []
        for lx0, lx1, ly0, ly1 in LINKS.values():
            if side == 'south' and abs(ly1 - y0) < .01 and lx1 > x0 and lx0 < x1:
                skip.append((lx0 - cx, lx1 - cx))
            elif side == 'north' and abs(ly0 - y1) < .01 and lx1 > x0 and lx0 < x1:
                skip.append((cx - lx1, cx - lx0))
            elif side == 'east' and abs(lx0 - x1) < .01 and ly1 > y0 and ly0 < y1:
                skip.append((ly0 - cy, ly1 - cy))
            elif side == 'west' and abs(lx1 - x0) < .01 and ly1 > y0 and ly0 < y1:
                skip.append((cy - ly1, cy - ly0))
        brick_face(f, lo, hi, court=side in court_sides, balcony_u=mid if side in balcony_sides else None, lite=side in lite_sides or side not in court_sides, skip=skip,
                   ext=T + .27 if side in ('east', 'west') else 0.0)
    for i in range(3):
        z = G0 + i * FH
        C.box(f'{name} floor {i}', (cx, cy, z - .13 if i else G0 / 2), (x1 - x0 - (2 * T if i else 0), y1 - y0 - (2 * T if i else 0), .26 if i else G0), 'floor' if i else 'foundation', 'floors', 0)
        C.qa_room_light(f'{name} rooms {i}', (cx, cy, z + FH - .5), 90, 6.0)
    C.box(f'{name} attic slab', (cx, cy, EAVE - .13), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .26), 'floor', 'floors', 0)
    C.box(f'{name} corridor', (cx, cy, (G0 + EAVE) / 2), (max(1.0, x1 - x0 - 12.0), max(1.0, y1 - y0 - 12.0), EAVE - G0 - .4), 'interior', 'corridor', 0)
    # Dormers on every slope, spaced along the part of each slope that clears the hips.
    ex0, ex1, ey0, ey1 = x0 - OV, x1 + OV, y0 - OV, y1 + OV
    run = flat if flat is not None else min(ex1 - ex0, ey1 - ey0) / 2 - .01
    ds = []
    long_x = (ex1 - ex0) >= (ey1 - ey0)
    for side, L, origin in (('south', ex1 - ex0, ex0), ('north', ex1 - ex0, ex0), ('east', ey1 - ey0, ey0), ('west', ey1 - ey0, ey0)):
        if flat is None and ((side in ('east', 'west')) == long_x):
            continue                                     # no dormers on the hip ends of a ridge roof
        usable = L - 2 * (1.3 + 1.5 + 1.2)
        if usable < 0:
            continue
        n = max(1, int(usable / dormer_step) + 1)
        for i in range(n):
            ds.append((side, origin + L / 2 + (i - (n - 1) / 2) * dormer_step))
    hip_roof(name + ' roof', x0, x1, y0, y1, EAVE, rise, flat=flat, dormers=ds)
    if flat is not None:
        for k, (dx, dy) in enumerate(((-1.6, -1.0), (1.4, 1.2), (0.0, -2.6))):
            C.box(f'{name} rooftop unit', (cx + dx, cy + dy, EAVE + rise + .55), (1.3, 1.0, .9), 'membrane', 'rooftop plant', 0)


# Window bays that a loggia link covers on a block face (u ranges in face coordinates).
LINK_SKIPS = {}


def loggia(name, box, open_sides):
    """One-storey brick loggia: round arches on its open sides, paved floor, white ceiling, hipped copper roof."""
    x0, x1, y0, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    along_x = (x1 - x0) >= (y1 - y0)
    sides = dict(south=(C.Face((cx, y0, 0), (1, 0, 0), (0, 1, 0), name + ' south'), x1 - x0),
                 north=(C.Face((cx, y1, 0), (-1, 0, 0), (0, -1, 0), name + ' north'), x1 - x0),
                 east=(C.Face((x1, cy, 0), (0, 1, 0), (-1, 0, 0), name + ' east'), y1 - y0),
                 west=(C.Face((x0, cy, 0), (0, -1, 0), (1, 0, 0), name + ' west'), y1 - y0))
    b = Batch()
    for side in open_sides:
        f, span = sides[side]
        lo, hi = -span / 2, span / 2                     # full length: the arcade butts the block faces at both ends
        n = max(1, int((hi - lo) / 3.0))
        pitch = (hi - lo) / n
        r = min(1.15, (pitch - .7) / 2)
        holes = [hole(f'{f.label} arch {i}', lo + pitch * (i + .5), G0, 2 * r, 2.6 + r - G0, kind='arch') for i in range(n)]
        f.wall(f.label + ' arcade carrier', lo, hi - EPS, G0, LINK_EAVE, depth=T, holes=holes)
        G.brick_courses(f, lo + .02, hi - .02, G0 + .02, LINK_EAVE - .25, holes, spacing=.2)
        m = Merge(f)
        for h in holes:
            arch_fill(b, f, h['u'], 2.6, r, 0, T)
            arch_ring(b, f, h['u'], 2.6, r, r + .2, -.05, .02, 'joint', n=12)
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='open arcade arch', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='covered walk'))
            m.box('stone', h['u'] - h['w'] / 2 - .17, -.04, 2.6 - .06, .44, T + .1, .16)    # impost blocks overlapping the ring foot
            m.box('stone', h['u'] + h['w'] / 2 + .17, -.04, 2.6 - .06, .44, T + .1, .16)
        m.box('trim', 0, -.10, LINK_EAVE - .18, hi - lo - 2 * EPS, T + .20, .22)
        m.box('stone', 0, -.04, G0 + .15, hi - lo - 2 * EPS, T + .08, .30)
        m.flush('loggias')
    b.flush(name + ' arches')
    C.box(name + ' paving', (cx, cy, G0 / 2), (x1 - x0, y1 - y0, G0), 'sand', 'loggias', 0)
    C.box(name + ' ceiling', (cx, cy, LINK_EAVE - .08), (x1 - x0 - .02, y1 - y0 - .02, .16), 'pale', 'loggias', 0)
    hip_roof(name + ' roof', x0, x1, y0, y1, LINK_EAVE, 1.6, seams=True)
    C.qa_room_light(name + ' walk', (cx, cy, LINK_EAVE - .5), 40, 3.0)


def hub():
    """Octagonal glazed garden room with a copper roof and a glass cupola, on the north link."""
    cx, cy, R = HUB
    a = R * math.cos(math.pi / 8)
    w = 2 * R * math.sin(math.pi / 8)
    for k in range(8):
        th = math.pi / 4 * k
        f = C.Face((cx + a * math.cos(th), cy + a * math.sin(th), 0), (-math.sin(th), math.cos(th), 0), (-math.cos(th), -math.sin(th), 0), f'garden room face {k}')
        if k in (0, 4):              # east and west faces are covered by the loggia links
            continue
        m = Merge(f)
        if k in (2, 6):              # forecourt (north) and court (south) bays: glazed French doors under a transom
            dw, dh = 1.8, 2.55
            door = hole(f'garden room french doors {k}', 0, G0, dw, dh, kind='door')
            side = [hole(f'garden room sidelight {k} {e}', e * 1.35, .5, .44, dh - .35, kind='window') for e in (-1, 1)]
            tran = hole(f'garden room transom {k}', 0, G0 + dh + .3, w - .55, HUB_H - G0 - dh - .9, kind='window')
            f.wall(f.label + ' carrier', -w / 2 + .12, w / 2 - .12, G0, HUB_H, depth=.22, role='trim', holes=[door, tran] + side)
            framed(m, f, door, cols=2, rows=1, inset=.16, occupied='garden room lounge', kind='french door')
            for h in side:
                framed(m, f, h, cols=1, rows=2, inset=.08, occupied='garden room lounge', kind='sidelight')
            framed(m, f, tran, cols=3, rows=1, inset=.08, occupied='garden room lounge', kind='transom')
            # A pair of glazed French doors: heavy white casing, a meeting stile, kick rails, brass handles.
            for e in (-1, 1):
                m.box('trim', e * (dw / 2 + .09), -.07, G0 + dh / 2, .18, .14, dh + .05)
                m.box('trim', e * dw / 4, .02, G0 + .17, dw / 2 - .1, .08, .3)
                m.box('hardware', e * .14, -.02, G0 + 1.05, .05, .1, .22)
            m.box('trim', 0, -.085, G0 + dh + .1, dw + .4, .17, .2)                    # head, proud of the casings
            m.box('trim', 0, .02, G0 + dh / 2, .14, .1, dh)
            m.box('stone', 0, -.01, G0 + .03, w - .3, .72, .06)                   # threshold through the full wall depth
            m.box('stone', 0, -.62, .1, dw + .9, .5, .11)                         # projecting step where the path arrives
        else:
            h = hole(f'garden room glazing {k}', 0, .5, w - .55, HUB_H - 1.1, kind='window')
            f.wall(f.label + ' carrier', -w / 2 + .12, w / 2 - .12, G0, HUB_H, depth=.22, role='trim', holes=[h])
            framed(m, f, h, cols=3, rows=3, inset=.08, occupied='garden room lounge', kind='french window')
            m.box('stone', 0, -.04, G0 + .18, w - .2, .30, .36)
        m.box('trim', 0, -.06, HUB_H - .15, w + .1, .34, .30)
        m.flush('garden room')
    for k in range(8):
        th = math.pi / 4 * k + math.pi / 8
        C.rod('Garden room corner post', (cx + R * math.cos(th) * .985, cy + R * math.sin(th) * .985, G0), (cx + R * math.cos(th) * .985, cy + R * math.sin(th) * .985, HUB_H), .2, 'trim', 'garden room', 10)
    C.rod('Garden room floor', (cx, cy, 0), (cx, cy, G0), R + .1, 'sand', 'garden room', 16)
    C.rod('Garden room ceiling', (cx, cy, HUB_H - .2), (cx, cy, HUB_H), R - .05, 'pale', 'garden room', 16)
    lower = [(cx + (R + .6) * math.cos(math.pi / 4 * k + math.pi / 8), cy + (R + .6) * math.sin(math.pi / 4 * k + math.pi / 8)) for k in range(8)]
    upper = [(cx + 1.7 * math.cos(math.pi / 4 * k + math.pi / 8), cy + 1.7 * math.sin(math.pi / 4 * k + math.pi / 8)) for k in range(8)]
    zr = HUB_H + 2.4
    strip('Garden room roof', lower, upper, HUB_H, zr, 'roof', 'garden room')
    soff = [(cx + (R + .5) * math.cos(math.pi / 4 * k + math.pi / 8), cy + (R + .5) * math.sin(math.pi / 4 * k + math.pi / 8)) for k in range(8)]
    C.prism('Garden room soffit', soff, 'z', HUB_H - .16, HUB_H - .06, 'trim', 'garden room')
    b = Batch()
    for k in range(8):                                   # standing seams on each roof facet
        p, q = lower[k], lower[(k + 1) % 8]
        tx, ty = q[0] - p[0], q[1] - p[1]; L = math.hypot(tx, ty); tx, ty = tx / L, ty / L
        mx, my = (upper[k][0] + upper[(k + 1) % 8][0]) / 2, (upper[k][1] + upper[(k + 1) % 8][1]) / 2
        for i in range(1, 6):
            s = i / 6
            e = (p[0] + (q[0] - p[0]) * s, p[1] + (q[1] - p[1]) * s, HUB_H + .01)
            top = (upper[k][0] + (upper[(k + 1) % 8][0] - upper[k][0]) * s, upper[k][1] + (upper[(k + 1) % 8][1] - upper[k][1]) * s, zr + .01)
            rib(b, e, (e[0] + (top[0] - e[0]) * .96, e[1] + (top[1] - e[1]) * .96, e[2] + (top[2] - e[2]) * .96), (tx, ty))
    b.flush('garden room roof seams')
    C.rod('Cupola base ring', (cx, cy, zr - .25), (cx, cy, zr + .2), 1.9, 'trim', 'cupola', 24)
    C.rod('Cupola drum glass', (cx, cy, zr + .2), (cx, cy, zr + 1.3), 1.55, 'glass', 'cupola', 24)
    for k in range(8):
        th = math.pi / 4 * k
        C.rod('Cupola mullion', (cx + 1.58 * math.cos(th), cy + 1.58 * math.sin(th), zr + .2), (cx + 1.58 * math.cos(th), cy + 1.58 * math.sin(th), zr + 1.3), .05, 'trim', 'cupola', 6)
    C.rod('Cupola cornice', (cx, cy, zr + 1.3), (cx, cy, zr + 1.45), 1.75, 'trim', 'cupola', 24)
    dome('Cupola glass dome', cx, cy, zr + 1.45, 1.6, 1.15, [(1.0, 0.0), (.92, .4), (.62, .8), (0.0, 1.0)], 'glass', 'cupola', segs=24, n=10)
    for k in range(8):
        th = math.pi / 4 * k
        prof = [(1.6 * pr, 1.15 * ph) for pr, ph in smooth_profile([(1.0, 0.0), (.92, .4), (.62, .8), (0.0, 1.0)], 10)]
        rib_mesh('Cupola rib', cx, cy, zr + 1.45, th, prof, .05, .02, 'trim', 'cupola')
    C.rod('Cupola finial', (cx, cy, zr + 2.55), (cx, cy, zr + 3.1), .06, 'hardware', 'cupola', 8)
    C.rod('Cupola finial ball', (cx, cy, zr + 2.55), (cx, cy, zr + 2.75), .13, 'hardware', 'cupola', 10)
    # Lounge furniture and light.
    for k in range(5):
        th = math.tau * k / 5
        x, y = cx + 2.2 * math.cos(th), cy - .6 + 2.2 * math.sin(th)
        C.rod('Lounge table', (x, y, G0 + .7), (x, y, G0 + .75), .5, 'timber', 'garden room', 12)
        C.rod('Lounge table stem', (x, y, G0), (x, y, G0 + .7), .06, 'hardware', 'garden room', 6)
        A.garden_chair(x + .7, y, G0)
    C.qa_room_light('Garden room', (cx, cy, HUB_H - .6), 60, 5.0)
    C.CONTACTS.append(dict(name='Octagonal garden room between the north loggias, cupola on the roof ring', centre=[cx, cy]))


def path_box(name, x0, x1, y0, y1, z=.045, role='sand'):
    C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, z / 2), (x1 - x0, y1 - y0, z), role, 'garden', 0)


def ring(name, cx, cy, r0, r1, z, role):
    annulus(name, (cx, cy, 0), (0, 0, 1), r0, r1, 0, z, role, 'garden', segs=32)


def fountain(cx, cy, scale=1.0):
    C.rod('Fountain basin', (cx, cy, 0), (cx, cy, .55), 2.0 * scale, 'stone', 'fountain', 20)
    C.rod('Fountain water', (cx, cy, .55), (cx, cy, .58), 1.8 * scale, 'water', 'fountain', 20)
    C.rod('Fountain pedestal', (cx, cy, .58), (cx, cy, 1.25), .28 * scale, 'stone', 'fountain', 12)
    C.rod('Fountain bowl', (cx, cy, 1.25), (cx, cy, 1.45), .85 * scale, 'stone', 'fountain', 20)
    C.rod('Fountain bowl water', (cx, cy, 1.45), (cx, cy, 1.47), .75 * scale, 'water', 'fountain', 20)
    C.rod('Fountain upper stem', (cx, cy, 1.47), (cx, cy, 2.1), .14 * scale, 'stone', 'fountain', 8)
    C.rod('Fountain upper bowl', (cx, cy, 2.1), (cx, cy, 2.24), .45 * scale, 'stone', 'fountain', 16)
    C.rod('Fountain finial', (cx, cy, 2.24), (cx, cy, 2.7), .07 * scale, 'stone', 'fountain', 8)


def picket_fence(pts, height=1.1, spacing=.3, gaps=()):
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, by - ay)
        for z in (.12, height - .04):
            C.beam('Garden fence rail', (ax, ay, z), (bx, by, z), .04, .04, 'hardware', 'garden fence')
        n = max(1, int(L / spacing))
        for i in range(n + 1):
            x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
            if any(math.hypot(x - gx, y - gy) < gw for gx, gy, gw in gaps):
                continue
            post = i in (0, n)
            C.rod('Garden fence picket', (x, y, .03), (x, y, height + (.1 if post else 0)), .05 if post else .016, 'hardware', 'garden fence', 6)


def garden():
    # Site lawn under everything, the court lawn, paths and plazas a few millimetres above it.
    C.box('Site lawn', (0.0, 3.0, .006), (90.0, 82.0, .012), 'lawn', 'site', 0)
    C.box('Court lawn', (5.0, -5.5, .02), (39.8, 28.8, .016), 'lawn', 'garden', 0)
    ring('Court path ring', 0.0, -2.0, 5.6, 7.0, .045, 'sand')
    path_box('Court cross path north', -.8, .8, 4.0, 4.6, .046)
    path_box('Court spine path', -.8, .8, -19.9, -9.0, .045)
    path_box('Court east-west path', 7.0, 24.9, -3.0, -1.4, .045)
    path_box('Court west path', -14.9, -7.0, -3.0, -1.4, .045)
    path_box('Court east walk', 21.2, 22.8, -19.9, -3.0, .045)
    path_box('Court east walk north', 21.2, 22.8, -1.4, 8.9, .045)
    path_box('Fountain link path', -5.8, -4.2, -19.9, -14.5, .045)
    ring('Fountain plaza', -5.0, -11.5, 0.0, 3.0, .05, 'sand')
    path_box('Fountain plaza walk', -4.2, -.8, -12.3, -10.7, .045)
    fountain(-5.0, -11.5)
    for k in range(6):                                  # rose beds round the fountain plaza
        th = math.tau * k / 6 + .3
        x, y = -5.0 + 4.1 * math.cos(th), -11.5 + 4.1 * math.sin(th)
        C.rod('Rose bed', (x, y, .02), (x, y, .35), .9, 'rose', 'garden', 10)
        A.shrub(x, y, .35, .5)
    # Fenced therapy garden of raised timber beds.
    gx0, gx1, gy0, gy1 = 2.5, 9.5, -17.5, -6.5
    path_box('Therapy garden paving', gx0, gx1, gy0, gy1, .05)
    for i, x in enumerate((4.3, 7.7)):
        for j, y in enumerate((-16.0, -14.0, -12.0, -10.0, -8.0)):
            C.box('Raised bed', (x, y, .35), (1.4, 1.4, .6), 'timber', 'therapy garden', 0)
            C.box('Raised bed soil', (x, y, .66), (1.2, 1.2, .04), 'soil', 'therapy garden', 0)
            for k in range(2):
                A.shrub(x - .3 + k * .6, y, .68, .3 + .15 * ((i + j + k) % 3))
    picket_fence([(gx0, gy0), (gx1, gy0), (gx1, gy1), (gx0, gy1), (gx0, gy0)], gaps=((0.0 + (gx0 + gx1) / 2, gy1, .7),))
    # Timber pergola over a dining terrace (east side).
    px0, px1, py0, py1 = 13.5, 20.5, -6.5, 1.0
    path_box('Pergola terrace', px0, px1, py0, py1, .05)
    for x in (px0 + .2, (px0 + px1) / 2, px1 - .2):
        for y in (py0 + .2, py1 - .2):
            C.box('Pergola post', (x, y, 1.45), (.22, .22, 2.8), 'timber', 'pergola', 0)
    for y in (py0 + .2, py1 - .2):
        C.box('Pergola beam', ((px0 + px1) / 2, y, 2.95), (px1 - px0 + .8, .16, .32), 'timber', 'pergola', 0)
    for k in range(13):
        x = px0 - .2 + (px1 - px0 + .4) * k / 12
        C.box('Pergola rafter', (x, (py0 + py1) / 2, 3.18), (.08, py1 - py0 + .8, .16), 'timber', 'pergola', 0)
    for k in range(10):
        y = py0 - .2 + (py1 - py0 + .4) * k / 9
        C.box('Pergola slat', ((px0 + px1) / 2, y, 3.30), (px1 - px0 + .6, .06, .08), 'timber', 'pergola', 0)
    for x, y in ((15.2, -4.4), (18.6, -4.4), (15.2, -1.2), (18.6, -1.2)):
        C.box('Dining table', (x, y, .76), (1.4, .9, .05), 'timber', 'pergola', 0)
        C.box('Dining table base', (x, y, .4), (.12, .12, .74), 'hardware', 'pergola', 0)
        A.garden_chair(x - 1.15, y, .05); A.garden_chair(x + 1.15, y, .05)
    # Benches, ornamental trees and the large shade trees on the court's west side.
    for x, y in ((-2.6, -5.0), (3.4, 2.0), (-9.0, -9.5), (12.0, -2.2)):
        C.box('Garden bench', (x, y, .45), (1.6, .5, .06), 'timber', 'garden', 0)
        C.box('Garden bench back', (x, y + .23, .78), (1.6, .05, .4), 'timber', 'garden', 0)
        for e in (-1, 1):                                                  # cast-iron ends: leg, arm and back post
            C.box('Garden bench end', (x + e * .74, y, .24), (.06, .46, .40), 'hardware', 'garden', 0)
            C.box('Garden bench end', (x + e * .74, y + .23, .62), (.06, .06, .76), 'hardware', 'garden', 0)
            C.box('Garden bench arm', (x + e * .74, y, .66), (.06, .46, .05), 'hardware', 'garden', 0)
    for x, y in ((6.0, 4.0), (-7.5, 2.5), (10.0, -14.0), (17.0, -14.5), (-11.0, -16.5)):
        A.small_tree(x, y, .03, 4.2, 1.6)
    for x, y in ((-10.0, -7.5), (-31.0, -1.0), (12.0, -11.0)):
        street_tree(x, y, z=.03, height=9.0, spread=2.6)
    # North forecourt: circular lawn with a small fountain inside a path ring, the drive loop beyond.
    ring('Forecourt path ring', 1.0, 23.5, 6.2, 7.6, .045, 'sand')
    C.rod('Forecourt lawn', (1.0, 23.5, 0), (1.0, 23.5, .03), 6.2, 'lawn', 'forecourt', 32)
    path_box('Forecourt walk', .2, 1.8, 12.6, 15.9, .045)
    path_box('Forecourt drive walk', .2, 1.8, 31.1, 35.0, .045)
    fountain(1.0, 23.5, .7)
    dx0, dx1, dy = -11.0, 13.0, 37.0                                   # drive loop round an elongated planted island
    for y in (dy - 3.5, dy + 3.5):
        C.box('Drive lane', ((dx0 + dx1) / 2, y, .02), (dx1 - dx0, 3.0, .04), 'foundation', 'site', 0)
    annulus('Drive loop end', (dx0, dy, 0), (0, 0, 1), 2.0, 5.0, .0, .05, 'foundation', 'site', segs=24)
    annulus('Drive loop end', (dx1, dy, 0), (0, 0, 1), 2.0, 5.0, .0, .05, 'foundation', 'site', segs=24)
    C.box('Drive island', ((dx0 + dx1) / 2, dy, .1), (dx1 - dx0, 4.0, .2), 'lawn', 'site', 0)
    for x in (dx0, dx1):
        C.rod('Drive island end', (x, dy, 0), (x, dy, .19), 2.0, 'lawn', 'site', 20)
    for x in (-6.0, 1.0, 8.0):
        A.shrub(x, dy, .2, 1.0)
    path_box('Forecourt cross path', -5.2, 7.2, 22.8, 24.2, .046)
    C.box('North street', (1.5, 46.5, .02), (81.0, 7.0, .04), 'foundation', 'site', 0)   # butts the west street
    for x in (dx0, dx1):                                                 # the loop's curved ends meet the street
        C.box('Drive throat', (x, 41.55, .0225), (4.0, 2.9, .045), 'foundation', 'site', 0)
    for k in range(8):
        C.box('North street marking', (-34.0 + k * 9.8, 46.5, .045), (3.0, .15, .01), 'membrane', 'site', 0)
    C.box('West street', (-42.0, 3.0, .02), (6.0, 82.0, .04), 'foundation', 'site', 0)
    C.box('West sidewalk', (-38.5, 3.0, .025), (1.8, 82.0, .05), 'concrete', 'site', 0)
    for y in (-28.0, -14.0, 0.0, 14.0, 28.0):
        street_tree(-37.0, y, z=.03, height=8.0, spread=2.0)


def build():
    garden()
    block('north west', NW, court_sides=('south', 'east'), balcony_sides=('south',), lite_sides=('north', 'west'), flat=6.5)
    block('north east', NE, court_sides=('south', 'west'), balcony_sides=('south',), lite_sides=('north', 'east'), flat=6.5)
    block('south west', SW, court_sides=('east', 'north'), balcony_sides=('east',), lite_sides=('west', 'south'), flat=5.5)
    block('east wing', EW, court_sides=('west',), balcony_sides=('west',), lite_sides=('east', 'south'), flat=None, rise=3.8, dormer_step=4.2)
    block('south wing', SO, court_sides=('north',), balcony_sides=('north',), lite_sides=('south',), flat=None, rise=3.8, dormer_step=4.2)
    loggia('north west loggia', LINKS['north_west'], ('south', 'north'))
    loggia('north east loggia', LINKS['north_east'], ('south', 'north'))
    loggia('west loggia', LINKS['west'], ('east', 'west'))
    loggia('east loggia', LINKS['east'], ('east', 'west'))
    loggia('south west link', LINKS['south_west'], ('west', 'south'))
    loggia('south east link', LINKS['south_east'], ('north', 'south'))
    hub()
    C.CONTACTS.append(dict(name='Ring of five brick blocks joined by one-storey loggias round the garden court (top view governs the plan)', blocks=[NW, NE, SW, EW, SO]))


LIGHT_RIG = dict(key=(-70, -90, 70), fill=(80, -40, 60), rear=(-30, 90, 70), target=(0, 0, 5.0), gain=20.0)
