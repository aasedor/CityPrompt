"""Cable-stayed circular cycle bridge, authored from the locked catalogue views of
dedicated_cycle_bridge / variant_1 (Cable-Stayed Ring Bridge).

Read from the pixels (the top view governs the plan): a circular cycle and footbridge floats over a large road
intersection. Its ring deck, red-surfaced with white dashed markings and white railings on both edges, sits on a
white box girder and hangs from a single tall slender steel pylon on a round island at the centre of the junction
by a fan of radial cables meeting at a collar high on the mast. A few slender concrete columns stand under the
ring, and a straight ramp leaves the ring at its south-west and runs south down to the street. Beneath, two broad
roads cross with lane markings, zebra and dotted crossings, red cycle paths and footways; brick houses with pitched
roofs, a few brick blocks of flats and trees stand in the corner plots.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-cable-stayed-cycle-ring'
R_IN, R_OUT = 30.6, 36.0                        # ring deck inner and outer radii (top view: about 0.15 of the radius)
RM = (R_IN + R_OUT) / 2
DZ = 6.6                                        # deck surface level above the road
GD = 1.1                                        # box-girder depth below the surface
COLLAR, MAST = 48.0, 60.0                       # cable collar and mast top
RAMP_A = math.radians(-122.0)                   # where the ramp leaves the ring (top view: south-west, heading south)
RAMP_L = 58.0                                   # ramp length down to the street
X0, X1, Y0, Y1 = -R_OUT, R_OUT, -R_OUT - RAMP_L, R_OUT
T = .3
EPS = .002
PALETTE = dict(white=(.92, .92, .90), red=(.62, .30, .26), rail=(.90, .90, .88), cable=(.85, .85, .84),
    steel=(.82, .83, .84), concrete=(.66, .65, .62), asphalt=(.26, .26, .27), lane=(.94, .94, .92),
    cycle=(.58, .30, .26), paving=(.62, .58, .54), grass=(.40, .50, .26), planting=(.30, .44, .20), tree=(.28, .44, .18),
    timber=(.42, .32, .22), soil=(.30, .25, .18), brick=(.55, .32, .24), brick2=(.62, .40, .30), roof=(.30, .28, .27),
    trim=(.90, .89, .86), glass=(.24, .30, .34), dark=(.14, .15, .16), hardware=(.18, .18, .19), pale=(.88, .88, .86),
    interior=(.84, .80, .74), floor=(.58, .48, .38), stone=(.70, .68, .64), joint=(.52, .50, .47), sand=(.70, .66, .58),
    wall=(.80, .74, .62), blue=(.20, .30, .40), pot=(.60, .34, .22))


def manifest(version):
    h = MAST
    rx, ry = RAMP_A, RAMP_A
    cams = G.camera_roster(2 * R_OUT + 10.0, 2 * R_OUT + RAMP_L, h * .4, [
        ('facade_close', (-44.0, 20.0, 3.4), (-30.0, 12.0, 5.6), 40),
        ('architecture_close', (-14.0, -8.0, 9.5), (-27.0, -14.6, 6.0), 40),
        ('glass_close', (RM * math.cos(math.radians(160)), RM * math.sin(math.radians(160)), DZ + 1.6),
                        (RM * math.cos(math.radians(130)), RM * math.sin(math.radians(130)), DZ + 1.0), 40),
        ('pylon_head', (14.0, -22.0, 52.0), (0.0, 0.0, 51.0), 40),
        ('cable_fan', (-6.0, -44.0, 12.0), (0.0, 0.0, 30.0), 28),
        ('ring_deck', (RM * math.cos(math.radians(205)), RM * math.sin(math.radians(205)), DZ + 1.7),
                      (RM * math.cos(math.radians(170)), RM * math.sin(math.radians(170)), DZ + .8), 30),
        ('ramp_landing', (R_OUT * math.cos(RAMP_A) + 9.0, R_OUT * math.sin(RAMP_A) - RAMP_L - 4.0, 1.7),
                         (R_OUT * math.cos(RAMP_A), R_OUT * math.sin(RAMP_A) - RAMP_L * .5, 3.5), 35),
        ('column_support', (RM * math.cos(math.radians(15)) + 9.0, RM * math.sin(math.radians(15)) - 7.0, 1.7),
                           (RM * math.cos(math.radians(15)), RM * math.sin(math.radians(15)), 4.0), 35),
        ('intersection_under', (0.0, -22.0, 1.7), (0.0, 22.0, 6.0), 26),
        ('rear_north', (6.0, 96.0, 24.0), (0.0, 0.0, 9.0), 35)])
    for c in cams:                       # the locked front stands by the ramp at deck height, looking east across the ring
        if c['name'] == 'front':
            c.update(location=(-60.0, -16.0, 8.6), target=(0.0, 2.0, 15.0), lens=22, whole=False)
        elif c['name'] == 'front_corner':                                      # the locked oblique, higher, from the south-west
            c.update(location=(-62.0, -30.0, 24.0), target=(0.0, 2.0, 12.0), lens=24, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(-70.0, -80.0, 70.0), target=(0.0, -10.0, 6.0), lens=30, whole=False)
        elif c['name'] == 'top':
            c.update(location=(0.0, -4.0, 140.0), target=(0.0, -3.999, 0.0), ortho_scale=96.0, whole=False)
        elif c['name'] == 'left_side':
            c.update(location=(-100.0, 6.0, 22.0), target=(0.0, 0.0, 10.0), lens=30, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(100.0, -6.0, 22.0), target=(0.0, 0.0, 10.0), lens=30, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(-8.0, 100.0, 20.0), target=(0.0, 0.0, 10.0), lens=30, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(78.0, 80.0, 40.0), target=(0.0, 0.0, 8.0), lens=30, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='dedicated_cycle_bridge/variant_1 (Cable-Stayed Ring Bridge)',
        measurement_contract=dict(dimensions_m=dict(width=2 * R_OUT, depth=2 * R_OUT + RAMP_L, height=h),
            observed_storeys=0, storey_programme='bridge: a circular cycle and footbridge over a road intersection',
            plan='72 m ring (top view), a 5.4 m deck, one straight ramp leaving the south-west of the ring and running south',
            section_m=dict(deck=[R_IN, R_OUT], deck_level=DZ, girder_depth=GD, collar=COLLAR, mast=MAST),
            facade='red cycle surface with white dashed markings, white railings on both edges, white box girder, radial steel cables, a slender steel pylon, concrete columns',
            levels_m=[0.0, DZ, COLLAR, MAST], inferred='the corner plots and their houses are simplified context; ramp length is an assumption'),
        roof_contract=dict(type='open bridge deck; no roof', datum_m=DZ, crowns_m=[MAST]),
        identity_contract=dict(owner='circular red cycle ring hung by radial cables from a single tall central pylon over a road intersection, white railings, a ramp'),
        material_contract=dict(profile='source-palette clay: red cycle surface, white girder and railings, pale steel pylon and cables, grey concrete columns, dark asphalt with white markings, red cycle paths, brick context', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='road intersection, cycle paths and footways', deck='cycling and walking round the ring'),
        street_contract=dict(kind='fixed_native_section', width_m=R_OUT - R_IN, axis='ring', junction_finish='ramp',
                             bands=['inner railing', 'cycle deck', 'outer railing']),
        contact_contract=['Roads and plots at grade', 'Columns and pylon island from grade', 'Ring deck on its columns and cables', 'Ramp from the ring down to the street'],
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
# ---- Cable-stayed circular cycle bridge ----

NR = 96                                          # ring segments


def at(r, a, z):
    return (r * math.cos(a), r * math.sin(a), z)


def ring_loft(name, prof, role, module='ring'):
    """Loft a closed (r, z) profile right round the ring."""
    rings = [[at(r, 2 * math.pi * i / NR, z) for r, z in prof] for i in range(NR)]
    loft(name, rings, role, module, closed=True)


def tube(name, pts, role, module, n=16):
    """Closed tapered tube through (z, r) stations on the vertical axis at the origin."""
    rings = [[(r * math.cos(2 * math.pi * j / n), r * math.sin(2 * math.pi * j / n), z) for j in range(n)] for z, r in pts]
    loft(name, rings, role, module, closed=False)


def disc(name, cx, cy, z0, z1, r, role, module, n=32):
    rings = [[(cx + r * math.cos(2 * math.pi * j / n), cy + r * math.sin(2 * math.pi * j / n), z) for j in range(n)] for z in (z0, z1)]
    loft(name, rings, role, module, closed=False)


def ramp_line():
    """The ramp axis: x, the start inside the deck, the end of the level run, the foot at the street."""
    xr = RM * math.cos(RAMP_A)
    ys = -math.sqrt(RM * RM - xr * xr)                                       # on the deck centre line
    yf = -math.sqrt(R_OUT * R_OUT - xr * xr) - 3.0                            # level for 3 m past the ring edge
    ye = yf - RAMP_L
    return xr, ys, yf, ye


def ramp_z(y):
    xr, ys, yf, ye = ramp_line()
    if y >= yf:
        return DZ - .01
    return .08 + (DZ - .09) * (y - ye) / (yf - ye)


def deck():
    ring_loft('Ring girder', [(R_IN, DZ - .06), (R_OUT, DZ - .06), (R_OUT - .4, DZ - GD), (R_IN + .4, DZ - GD)], 'white')
    ring_loft('Ring cycle surface', [(R_IN + .14, DZ - .09), (R_OUT - .14, DZ - .09), (R_OUT - .14, DZ), (R_IN + .14, DZ)], 'red')
    for nm, r0, r1 in (('inner', R_IN, R_IN + .15), ('outer', R_OUT - .15, R_OUT)):
        ring_loft(f'Ring {nm} kerb', [(r0, DZ - .07), (r1, DZ - .07), (r1, DZ + .12), (r0, DZ + .12)], 'white')
    b = Batch()
    for i in range(64):                                                      # white dashed markings on the red surface
        a0 = 2 * math.pi * i / 64
        a1 = a0 + 2 * math.pi / 64 * .45
        b.beam('lane', at(RM, a0, DZ + .006), at(RM, a1, DZ + .006), .12, .01)
    xr, ys, yf, ye = ramp_line()
    for i in range(int((yf - ye) / 3.0)):                                    # and down the ramp
        y0 = yf - 1.0 - i * 3.0
        b.beam('lane', (xr, y0, ramp_z(y0) + .006), (xr, y0 - 1.3, ramp_z(y0 - 1.3) + .006), .12, .01)
    b.flush('deck markings')


def railings():
    b = Batch()
    xr, ys, yf, ye = ramp_line()
    gap = lambda p: abs(p[0] - xr) < 2.45 and p[1] < 0
    for r, n in ((R_IN + .07, 88), (R_OUT - .07, 104)):
        pts = [at(r, 2 * math.pi * i / n, DZ) for i in range(n)]
        for i in range(n):
            p, q = pts[i], pts[(i + 1) % n]
            if r > RM and (gap(p) or gap(q)):
                continue
            b.box('rail', p[0], p[1], DZ + .12 + .54, .07, .07, 1.08)
            for z, w in ((1.18, .07), (.66, .04), (.30, .04)):
                b.beam('rail', (p[0], p[1], DZ + z), (q[0], q[1], DZ + z), w, w)
    for s in (-1, 1):                                                        # ramp railings, from the ring edge to the foot
        x = xr + s * 2.2
        y = -math.sqrt(R_OUT * R_OUT - x * x) - .05
        ys_ = []
        while y > ye + .5:
            ys_.append(y); y -= 2.2
        for ya, yb in zip(ys_, ys_[1:]):
            b.box('rail', x, ya, ramp_z(ya) + .6, .07, .07, 1.2)
            for z, w in ((1.18, .07), (.66, .04), (.30, .04)):
                b.beam('rail', (x, ya, ramp_z(ya) + z), (x, yb, ramp_z(yb) + z), w, w)
    b.flush('railings')


def ramp():
    xr, ys, yf, ye = ramp_line()
    D = .9
    yb = ye + (yf - ye) * (D - .08) / (DZ - .09)                               # where the girder soffit meets the street
    poly = [(ys, DZ - .03), (yf, DZ - .03), (ye, .05), (ye, 0.0), (yb, 0.0), (yf, DZ - .03 - D), (ys, DZ - .03 - D)]
    C.prism('Ramp girder', poly, 'x', xr - 2.3, xr + 2.3, 'white', 'ramp')
    top = [(ys, DZ - .06), (yf, DZ - .06), (ye, .06), (ye, .1), (yf, DZ - .01), (ys, DZ - .01)]
    C.prism('Ramp cycle surface', top, 'x', xr - 2.12, xr + 2.12, 'red', 'ramp')
    b = Batch()
    for y in (yf - 10.0, yf - 22.0, yf - 34.0):                              # ramp columns
        zt = ramp_z(y) - D + .02
        if zt > 1.0:
            b.box('concrete', xr, y, zt / 2, .9, .9, zt)
    b.flush('ramp columns')


def pylon_and_cables():
    disc('Pylon island', 0.0, 0.0, 0.0, .22, 3.4, 'concrete', 'pylon')
    disc('Pylon island kerb', 0.0, 0.0, 0.0, .26, 3.6, 'white', 'pylon', 32)
    tube('Pylon mast', [(.2, .78), (COLLAR - 2.0, .55), (COLLAR + 3.0, .42), (MAST, .2)], 'steel', 'pylon')
    disc('Pylon base', 0.0, 0.0, .2, 1.4, 1.15, 'steel', 'pylon', 24)
    disc('Cable collar', 0.0, 0.0, COLLAR - .9, COLLAR + .9, .95, 'steel', 'pylon', 24)
    b = Batch()
    n = 30
    for i in range(n):
        a = 2 * math.pi * (i + .5) / n
        b.beam('cable', at(.85, a, COLLAR), at(R_IN + .25, a, DZ - .35), .07, .07)
        b.box('steel', *at(R_IN + .05, a, DZ - .5), .3, .3, .5)                 # anchor bracket on the inner girder face
    b.flush('cables')


def columns():
    b = Batch()
    for deg in (40.0, 140.0, 215.0, 320.0):
        x, y, _ = at(RM, math.radians(deg), 0.0)
        zt = DZ - GD + .05
        b.box('concrete', x, y, zt / 2, 1.5, 1.5, zt)
        b.box('concrete', x, y, zt - .2, 2.2, 2.2, .4)                         # bearing head
    b.flush('ring columns')


def street():
    E = 112.0
    C.box('North-south road', (0.0, 0.0, .015), (22.0, 2 * E, .03), 'asphalt', 'street', 0)
    for s in (-1, 1):
        C.box(f'East-west road {s:+d}', (s * (11.0 + E) / 2, 0.0, .015), (E - 11.0, 24.0, .03), 'asphalt', 'street', 0)
    for s in (-1, 1):
        for t in (-1, 1):                                                    # cycle paths and footways along the north-south road
            C.box(f'NS cycle path {s:+d}{t:+d}', (s * 12.25, t * (12.0 + E) / 2, .025), (2.5, E - 12.0, .05), 'cycle', 'street', 0)
            C.box(f'NS footway {s:+d}{t:+d}', (s * 14.75, t * (12.0 + E) / 2, .04), (2.5, E - 12.0, .08), 'paving', 'street', 0)
            C.box(f'EW cycle path {s:+d}{t:+d}', (s * (16.0 + E) / 2, t * 13.25, .025), (E - 16.0, 2.5, .05), 'cycle', 'street', 0)
            C.box(f'EW footway {s:+d}{t:+d}', (s * (16.0 + E) / 2, t * 15.75, .04), (E - 16.0, 2.5, .08), 'paving', 'street', 0)
            C.box(f'Plot {s:+d}{t:+d}', (s * (16.0 + E) / 2, t * (17.0 + E) / 2, .0125), (E - 16.0, E - 17.0, .025), 'grass', 'plots', 0)
    b = Batch()
    for k in range(-34, 35):                                                  # lane lines
        y = k * 3.2
        if abs(y) > 13.0:
            for x in (-5.5, 0.0, 5.5):
                b.box('lane', x, y, .033, .14 if x else .18, 1.6, .006)
        x = k * 3.2
        if abs(x) > 12.0:
            for y in (-6.0, 0.0, 6.0):
                b.box('lane', x, y, .033, 1.6, .14 if y else .18, .006)
    for s in (-1, 1):                                                        # stop lines, zebra and dotted crossings
        b.box('lane', s * 2.75, s * -12.6, .033, 5.5, .35, .006)
        b.box('lane', s * -12.4, s * -3.0, .033, .35, 6.0, .006)
        for i in range(10):
            b.box('lane', -9.0 + i * 2.0, s * 18.0, .033, .9, 3.2, .006)
            b.box('lane', s * 19.0, -10.0 + i * 2.2, .033, 3.2, .9, .006)
        for i in range(14):
            b.box('lane', s * 11.2, -10.4 + i * 1.6, .053, .4, .4, .006)
    b.flush('road markings')
    for x, y in ((-24.0, 24.0), (24.0, 26.0), (-26.0, -22.0), (30.0, -22.0), (-46.0, 20.0), (46.0, -20.0), (20.0, 46.0), (-30.0, -58.0)):
        street_tree(x, y, z=.025, height=10.0, spread=2.6)


def context():
    """Brick houses with pitched roofs and blocks of flats in the corner plots: proud-framed windows with sills."""
    def windows(b, face, axis, lo, hi, z0, floors, sign):
        n = int((hi - lo) / 3.0)
        for k in range(floors):
            for j in range(n):
                u = lo + 1.5 + j * 3.0
                z = z0 + .9 + k * 3.0
                if axis == 'y':                                              # face in a plane y = face, facing sign*y
                    b.box('dark', u, face + sign * .02, z + .75, 1.2, .04, 1.4)
                    for s in (-1, 1):
                        b.box('trim', u + s * .66, face + sign * .05, z + .75, .12, .1, 1.62)
                    b.box('trim', u, face + sign * .05, z + 1.52, 1.44, .1, .12)
                    b.box('trim', u, face + sign * .09, z - .02, 1.5, .18, .1)
                else:
                    b.box('dark', face + sign * .02, u, z + .75, .04, 1.2, 1.4)
                    for s in (-1, 1):
                        b.box('trim', face + sign * .05, u + s * .66, z + .75, .1, .12, 1.62)
                    b.box('trim', face + sign * .05, u, z + 1.52, .1, 1.44, .12)
                    b.box('trim', face + sign * .09, u, z - .02, .18, 1.5, .1)
    blocks = (('Flats north-east', 44.0, 66.0, 34.0, 58.0, 13.0), ('Flats south-east', 46.0, 72.0, -72.0, -46.0, 10.0))
    for name, x0, x1, y0, y1, h in blocks:
        C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), 'brick', 'context', 0)
        C.box(f'{name} parapet cap', ((x0 + x1) / 2, (y0 + y1) / 2, h + .06), (x1 - x0 + .2, y1 - y0 + .2, .12), 'trim', 'context', 0)
        b = Batch()
        windows(b, x0, 'x', y0, y1, 0.0, int(h / 3.0) - 0, -1)
        windows(b, y0 if y0 > 0 else y1, 'y', x0, x1, 0.0, int(h / 3.0), -1 if y0 > 0 else 1)
        b.flush(f'{name} windows')
    houses = (('Houses north-west', -76.0, -40.0, 36.0, 46.0), ('Houses south-west', -78.0, -44.0, -54.0, -44.0), ('Houses north', -34.0, -20.0, 40.0, 50.0))
    for name, x0, x1, y0, y1 in houses:
        C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, 3.2), (x1 - x0, y1 - y0, 6.4), 'brick2', 'context', 0)
        pitched_roof(f'{name} roof', x0, x1, y0, y1, 6.4, 3.4, hip_w=False, hip_e=False, axis='x', ov=.3, role='roof', module='context')
        b = Batch()
        face = y0 if y0 > 0 else y1
        windows(b, face, 'y', x0, x1, -.4, 2, -1 if y0 > 0 else 1)
        b.flush(f'{name} windows')


def build():
    street()
    context()
    columns()
    deck()
    ramp()
    railings()
    pylon_and_cables()
    C.CONTACTS.append(dict(name='Circular cycle bridge on columns and radial cables from a central pylon over a road intersection; ramp to the street', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(40, -50, 60), fill=(-50, -30, 40), rear=(-25, 50, 40), target=(0, 0, 8.0), gain=4.0)
