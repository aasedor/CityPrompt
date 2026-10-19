"""Calgary RiverWalk street option, authored from the locked catalogue views of
bow_river_pathway / variant_0 (Summer River Day).

Read from the pixels (the top view governs the plan): a straight run of Calgary's RiverWalk on the south bank of the
Bow. From the river inland: blue-green water, a rip-rap bank of grey boulders, a riparian strip of native grasses,
shrubs and cottonwoods, a slender bronze-coloured handrail on low posts, a wide pale concrete promenade with scored
joints shared by walkers and cyclists, then a building-side edge of stone-faced raised planters and gabion walls
with timber benches and small trees, and a row of pale-brick mid-rise apartment blocks with ground-floor patios. The
red helical-truss Peace Bridge lands on the far end of the promenade and crosses to a wooded far bank.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-calgary-riverwalk'
X0, X1, Y0, Y1 = -12.0, 4.0, -36.0, 36.0       # the section from the rip-rap toe to the building line, 72 m long
WATER, BANK, PLANT, RAIL, PROM, EDGE, BLD = -12.0, -9.0, -5.0, -4.7, 1.3, 4.0, 4.0
ZP = 1.2                                        # promenade level above the river surface
T = .3
EPS = .002
PALETTE = dict(water=(.20, .48, .50), riprap=(.56, .55, .52), rock=(.62, .61, .58), soil=(.30, .25, .18),
    grass=(.52, .58, .30), planting=(.30, .44, .20), tree=(.28, .44, .18), timber=(.46, .34, .22),
    concrete=(.78, .76, .72), joint=(.62, .60, .56), stone=(.70, .64, .54), gabion=(.58, .55, .50),
    hardware=(.36, .26, .18), rail=(.40, .30, .20), bench=(.52, .38, .24), red=(.70, .12, .12),
    wall=(.80, .74, .62), brick=(.80, .74, .62), trim=(.92, .92, .90), glass=(.24, .30, .34), pale=(.88, .88, .86),
    interior=(.84, .80, .74), floor=(.58, .48, .38), sand=(.70, .66, .58), asphalt=(.30, .30, .31), white=(.95, .95, .93),
    roof=(.66, .66, .64), blue=(.20, .30, .40), pot=(.60, .34, .22))


def manifest(version):
    h = 18.0
    cams = G.camera_roster(X1 - X0 + 6.0, Y1 - Y0 + 4.0, h, [
        ('facade_close', (-1.2, -24.0, 2.9), (-1.5, -8.0, 2.4), 45),
        ('architecture_close', (-6.0, -14.0, 3.5), (2.6, -6.0, 1.4), 40),
        ('glass_close', (-1.0, -4.0, 4.4), (BLD + 1.5, -2.0, 5.0), 40),
        ('promenade_section', (-1.5, Y0 - 6.0, 6.0), (-1.5, Y0 + 8.0, 0.8), 40),
        ('river_railing', (-2.0, -12.0, 2.9), (RAIL, -4.0, 2.5), 40),
        ('planters_benches', (-2.5, -10.0, 3.1), (2.6, -4.0, 2.2), 40),
        ('riprap_bank', (-22.0, -14.0, 5.0), (-10.0, -6.0, .6), 40),
        ('peace_bridge', (-6.0, -6.0, 3.0), (-24.0, 26.0, 4.0), 35),
        ('aerial_section', (-26.0, -46.0, 30.0), (-3.0, 0.0, 1.0), 35),
        ('rear_north', (-4.0, Y1 + 18.0, 8.0), (-4.0, Y1 - 10.0, 1.5), 40)])
    for c in cams:                       # the locked front stands on the promenade looking north towards the bridge
        if c['name'] == 'front':
            c.update(location=(.6, -26.0, 2.9), target=(-3.0, 4.0, 3.8), lens=24, whole=False)
        elif c['name'] == 'front_corner':                                      # the locked oblique, high over the building edge
            c.update(location=(-16.0, -44.0, 26.0), target=(-5.0, 8.0, 0.0), lens=30, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(10.0, -30.0, 40.0), target=(-8.0, 6.0, 0.0), lens=30, whole=False)
        elif c['name'] == 'top':
            c.update(location=(-8.0, 2.0, 90.0), target=(-8.0, 2.001, 0.0), ortho_scale=80.0)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='bow_river_pathway/variant_0 (Summer River Day), modelled as Calgary RiverWalk',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=0, storey_programme='street option: a riverside promenade section; the flanking blocks are context',
            plan='16 m section from the rip-rap toe to the building line (top view), 72 m long, the Peace Bridge landing at the north end',
            section_m=dict(riprap=[WATER, BANK], riparian_planting=[BANK, PLANT], rail=RAIL, promenade=[RAIL, PROM], building_edge=[PROM, EDGE]),
            facade='pale scored concrete promenade, bronze handrail, rip-rap, riparian planting and cottonwoods, stone-faced planters and gabions, timber benches, pale-brick blocks, the red Peace Bridge',
            levels_m=[0.0, ZP], inferred='the far bank, skyline and blocks are context; the river bed below the surface is not modelled'),
        roof_contract=dict(type='open street option; flat roofs on the context blocks', datum_m=ZP, crowns_m=[h]),
        identity_contract=dict(owner='Calgary RiverWalk: wide pale promenade between a planted rip-rap river bank with a slender rail and a building edge of stone planters and benches, the red Peace Bridge'),
        material_contract=dict(profile='source-palette clay: blue-green water, grey rip-rap, green grasses and cottonwoods, pale concrete with joints, bronze rail, stone and gabion planters, timber benches, pale brick, red bridge truss', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='walking and cycling promenade, benches, planting'),
        street_contract=dict(kind='fixed_native_section', width_m=X1 - X0, axis='y', junction_finish='pavers',
                             bands=['water', 'riprap', 'riparian_planting', 'rail', 'promenade', 'building_edge']),
        contact_contract=['River surface at grade zero', 'Rip-rap from the water to the planting strip', 'Promenade on its base', 'Planters and benches on the promenade'],
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


# ---- Calgary RiverWalk ----

import random

RNG = random.Random(1907)                       # fixed seed: the same boulders and tufts on every build


def bank_plate(name, xa, za, xb, zb, y0, y1, t=.3, role='riprap', module='bank'):
    """Closed sloped plate from (xa, za) to (xb, zb) along the river, thin end faces."""
    vs = []
    for (x, z) in ((xa, za), (xb, zb)):
        for y in (y0, y1):
            vs += [(x, y, z), (x, y, z - t)]
    fs = [(0, 2, 6, 4), (1, 5, 7, 3), (0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6)]
    return C.mesh(name, vs, fs, role, module)


def cottonwood(x, y, z, h=13.0, s=1.0):
    """Tall cottonwood: a leaning trunk, two limbs and an open, rounded crown of several masses."""
    C.rod('Cottonwood trunk', (x, y, z), (x + .3 * s, y + .2 * s, z + h * .55), .26 * s, 'timber', 'trees', 8)
    for dx, dy in ((-1.6, .4), (1.4, -.6)):
        C.rod('Cottonwood limb', (x + .2 * s, y, z + h * .45), (x + dx * s, y + dy * s, z + h * .72), .12 * s, 'timber', 'trees', 6)
    for i, (dx, dy, dz, r, rz) in enumerate(((0, 0, .78, 3.0, 2.6), (-1.8, .5, .7, 2.0, 1.8), (1.7, -.6, .68, 2.0, 1.7), (.3, .2, .92, 1.8, 1.5))):
        A.foliage(f'Cottonwood crown {i}', (x + dx * s, y + dy * s, z + h * dz), (r * s, r * s, rz * s), role='tree', detail=2)


def river_and_bank():
    C.box('Bow River', (-36.0, 0.0, .01), (48.0, Y1 - Y0 + 16.0, .02), 'water', 'river', 0)
    C.prism('Rip-rap bank', [(WATER, 0.0), (BANK, 0.0), (BANK, ZP - .12), (WATER, .03)], 'y', Y0 - 2.0, Y1 + 2.0, 'riprap', 'bank')   # a solid wedge from grade
    b = Batch()
    for i in range(520):                                                                      # loose boulders on the slope
        x = RNG.uniform(WATER + .1, BANK - .2)
        y = RNG.uniform(Y0 - 1.8, Y1 + 1.8)
        if 22.3 < y < 29.7 and x > BANK - 1.2:                                                 # clear of the bridge deck
            continue
        z = .02 + (x - WATER) / (BANK - WATER) * (ZP - .14)
        L = RNG.uniform(.35, .8)
        a = RNG.uniform(0, math.pi)
        b.beam('rock', (x - math.cos(a) * L / 2, y - math.sin(a) * L / 2, z + .12), (x + math.cos(a) * L / 2, y + math.sin(a) * L / 2, z + .14),
               RNG.uniform(.3, .55), RNG.uniform(.22, .38))
    b.flush('rip-rap boulders')
    # Riparian strip: soil berm, native grasses, shrubs, cottonwoods.
    C.box('Riparian soil', ((BANK + PLANT) / 2, 0.0, (ZP - .1) / 2), (PLANT - BANK, Y1 - Y0 + 4.0, ZP - .1), 'soil', 'riparian', 0)
    b = Batch()
    for i in range(400):                                                                      # clumps of tall thin blades
        x = RNG.uniform(BANK + .2, PLANT - .2)
        y = RNG.uniform(Y0 - 1.8, Y1 + 1.8)
        if 22.3 < y < 29.7:
            continue
        for j in range(4):
            h = RNG.uniform(.45, 1.0)
            a = RNG.uniform(0, 2 * math.pi)
            lean = RNG.uniform(.05, .22)
            b.beam('grass' if j % 2 else 'planting', (x, y, ZP - .1), (x + math.cos(a) * lean, y + math.sin(a) * lean, ZP - .1 + h), .05, .03)
    b.flush('native grasses')
    for i, y in enumerate((-30.0, -21.0, -11.0, -2.0, 8.0, 16.0, 33.0)):
        x = BANK + 1.6 + (i % 2) * .9
        if abs(y - 26.0) > 5.0:
            cottonwood(x, y, ZP - .1, h=12.0 + (i % 3) * 1.4)
    for i, y in enumerate((-26.0, -16.0, -7.0, 3.0, 12.0, 20.0, 30.0)):
        A.foliage(f'Riparian shrub {i}', (PLANT - .9, y, ZP + .3), (.9, 1.3, .7), role='planting', detail=1)
    # Far bank: a low grassy bank with trees where the bridge lands.
    C.box('Far bank', (-68.0, 0.0, .5), (24.0, Y1 - Y0 + 16.0, 1.0), 'grass', 'far bank', 0)
    for i, y in enumerate((-30.0, -18.0, -6.0, 6.0, 14.0, 36.0)):
        cottonwood(-60.0 - (i % 2) * 3.0, y, 1.0, h=13.0, s=1.1)


def promenade():
    C.box('Promenade base', ((RAIL - .15 + EDGE) / 2, 0.0, (ZP - .06) / 2), (EDGE - RAIL + .15, Y1 - Y0 + 4.0, ZP - .06), 'stone', 'promenade', 0)
    C.box('Promenade slab', ((RAIL - .15 + EDGE) / 2, 0.0, ZP - .03), (EDGE - RAIL + .15, Y1 - Y0 + 4.0, .06), 'concrete', 'promenade', 0)
    b = Batch()
    for k in range(int((Y1 - Y0 + 4.0) / 2.0) + 1):                                            # scored joints
        y = Y0 - 2.0 + k * 2.0
        b.box('joint', (RAIL + PROM) / 2 - .15, y, ZP + .002, PROM - RAIL + .28, .025, .004)
    for x in (RAIL + 2.0, RAIL + 4.0):
        b.box('joint', x, 0.0, ZP + .002, .025, Y1 - Y0 + 3.98, .004)
    # The slender bronze handrail on low posts along the river edge, open where the bridge lands.
    xr = RAIL - .1
    for ya, yc in ((Y0 - 2.0, 22.6), (29.4, Y1 + 2.0)):
        b.beam('rail', (xr, ya, ZP + 1.02), (xr, yc, ZP + 1.02), .06, .05)
        b.beam('rail', (xr, ya, ZP + .55), (xr, yc, ZP + .55), .035, .035)
        n = int((yc - ya) / 2.0)
        for i in range(n + 1):
            b.box('rail', xr, ya + (yc - ya) * i / n, ZP + .51, .06, .06, 1.02)
    for y in (-30.0, -18.0, -6.0, 6.0, 18.0, 33.0):                                           # lamp standards on the building side
        b.box('hardware', PROM - .3, y, ZP + 2.3, .12, .12, 4.6)
        b.box('pale', PROM - .3, y, ZP + 4.75, .3, .3, .35)
        b.box('hardware', PROM - .3, y, ZP + 4.97, .4, .4, .08)
    b.flush('promenade furniture')


def building_edge():
    """Stone-faced raised planters and gabion patio walls along the building side, timber benches between them."""
    b = Batch()
    y = Y0 + 1.0
    k = 0
    while y < Y1 - 3.0:
        L = 4.5 if k % 2 == 0 else 3.2
        if not (21.0 < y + L / 2 < 31.0):
            b.box('stone', (PROM + EDGE) / 2 - .1, y + L / 2, ZP + .3, EDGE - PROM - .4, L, .6)       # planter walls
            b.box('soil', (PROM + EDGE) / 2 - .1, y + L / 2, ZP + .61, EDGE - PROM - .6, L - .2, .04)
            for j in range(3):
                b.box('planting', PROM + .55 + j * .7, y + L * (j + .5) / 3, ZP + .9, .55, .7, .55)
        bench_y = y + L + .9
        if bench_y < Y1 - 1.0 and not (21.0 < bench_y < 31.0):
            b.box('bench', PROM - .05, bench_y, ZP + .46, .5, 1.6, .07)                         # timber bench facing the river
            b.box('bench', PROM + .17, bench_y, ZP + .72, .06, 1.6, .4)
            for s in (-1, 1):
                b.box('hardware', PROM - .05, bench_y + s * .65, ZP + .22, .45, .06, .44)
        y += L + 1.8
        k += 1
    for y0, y1 in ((Y0, -14.0), (-10.0, 8.0), (12.0, Y1)):                                   # gabion patio walls at the block line
        b.box('gabion', EDGE - .2, (y0 + y1) / 2, ZP + .45, .4, y1 - y0, .9)
        for i in range(int((y1 - y0) / .5)):
            b.box('hardware', EDGE - .41, y0 + .25 + i * .5, ZP + .45, .01, .02, .88)
    b.flush('building edge')
    for i, y in enumerate((-24.0, -6.0, 14.0)):
        A.foliage(f'Edge tree crown {i}', ((PROM + EDGE) / 2, y, ZP + 3.6), (1.3, 1.3, 1.6), role='tree', detail=2)
        C.rod('Edge tree trunk', ((PROM + EDGE) / 2, y, ZP), ((PROM + EDGE) / 2, y, ZP + 2.6), .1, 'timber', 'trees', 6)


def blocks():
    """Pale-brick mid-rise apartment blocks: a west face with real cuts and balconies, a body behind, patios at grade."""
    for name, y0, y1, nf in (('South block', Y0 - 2.0, -12.0, 6), ('Middle block', -12.0 + 3.5, 10.5, 5), ('North block', 14.0, Y1 + 2.0, 6)):
        f = C.Face((BLD + 1.5, 0, 0), (0, -1, 0), (1, 0, 0), name)
        lo, hi = -y1, -y0
        n = int((hi - lo) / 3.0)
        hs = []
        for k in range(nf):
            z = ZP + .3 + k * 3.0
            for j in range(n):
                u = lo + 1.5 + j * 3.0
                if k == 0:
                    hs.append(hole(f'{name} patio door {j}', u, ZP + .05, 1.6, 2.3, kind='patio door'))
                else:
                    hs.append(hole(f'{name} window f{k} {j}', u, z + .6, 1.6, 1.8))
        top = ZP + nf * 3.0 + .5
        f.wall(f'{name} west wall', lo, hi - EPS, 0.0, top, depth=T, role='brick', holes=hs)
        G.brick_courses(f, lo + .02, hi - .02, ZP + .1, top - .1, hs, spacing=.6)
        m = Merge(f)
        for h in hs:
            framed(m, f, h, cols=2, rows=1 if h['h'] < 2 else 2, inset=.14, occupied='flat', kind='door' if h.get('kind') else 'window', lite=True)
        for k in range(1, nf):                                                              # balconies with glass rails on alternate bays
            z = ZP + k * 3.0 + .1
            for j in range(0, n, 2):
                u = lo + 1.5 + j * 3.0
                m.box('trim', u + 1.5, -.7, z, 3.6, 1.4, .16)
                m.box('glass', u + 1.5, -1.38, z + .55, 3.6, .03, .9)
        m.box('trim', (lo + hi) / 2, -.06, top - .1, hi - lo + .1, .14, .2)
        m.flush(name)
        C.box(f'{name} body', (BLD + 1.5 + T + 6.0, (y0 + y1) / 2, top / 2), (12.0, y1 - y0, top), 'brick', 'blocks', 0)
        C.box(f'{name} plinth fill', ((EDGE + BLD + 1.5) / 2, (y0 + y1) / 2, (ZP - .03) / 2), (BLD + 1.5 - EDGE, y1 - y0, ZP - .03), 'stone', 'blocks', 0)
        C.box(f'{name} patio', ((EDGE + BLD + 1.5) / 2, (y0 + y1) / 2, ZP - .015), (BLD + 1.5 - EDGE, y1 - y0, .03), 'timber', 'blocks', 0)
        C.qa_room_light(f'{name} rooms', (BLD + 4.0, (y0 + y1) / 2, ZP + 2.0), 60, 4.0)
    for y0, y1 in ((-12.0, -8.5), (10.5, 14.0)):                                             # gaps between the blocks: lawn
        C.box(f'Gap lawn {y0:+.0f}', ((EDGE + BLD + 14.0) / 2, (y0 + y1) / 2, (ZP - .03) / 2), (BLD + 14.0 - EDGE, y1 - y0, ZP - .03), 'grass', 'blocks', 0)


def peace_bridge():
    """The red helical-truss Peace Bridge, landing on the promenade at the north end and crossing to the far bank."""
    yc, w, hgt = 26.0, 6.2, 4.4
    xa, xb = -58.0, RAIL - .1
    C.box('Bridge deck', ((xa + xb) / 2, yc, ZP - .2), (xb - xa, w, .4), 'white', 'bridge', 0)
    C.box('Bridge pier', (-34.0, yc, (ZP - .4) / 2), (3.0, 4.0, ZP - .4), 'stone', 'bridge', 0)
    b = Batch()
    n = int((xb - xa) / 2.4)
    def ring(x, a):
        return (x, yc + (w / 2) * math.cos(a), ZP + hgt * .5 + (hgt * .5) * math.sin(a))
    for i in range(n):
        x0 = xa + (xb - xa) * i / n
        x1 = xa + (xb - xa) * (i + 1) / n
        for k in range(8):                                                                   # two opposed helices of red tubes
            a0 = math.pi * (k / 8.0) * 2 - math.pi / 2
            a1 = a0 + math.pi / 4
            p0, p1 = ring(x0, a0), ring(x1, a1)
            q0, q1 = ring(x0, a1), ring(x1, a0)
            if p0[2] > ZP + .05 and p1[2] > ZP + .05:
                b.beam('red', p0, p1, .16, .16)
            if q0[2] > ZP + .05 and q1[2] > ZP + .05:
                b.beam('red', q0, q1, .16, .16)
    for s in (-1, 1):                                                                       # edge chords and glazed roof
        b.beam('red', (xa, yc + s * w / 2, ZP + .1), (xb, yc + s * w / 2, ZP + .1), .22, .22)
    b.box('glass', (xa + xb) / 2, yc, ZP + hgt - .05, xb - xa, w * .45, .04)
    b.box('rail', (xa + xb) / 2, yc - 1.2, ZP + .01, xb - xa, .9, .01)                        # cycle lane marking
    b.flush('peace bridge')


def build():
    river_and_bank()
    promenade()
    building_edge()
    blocks()
    peace_bridge()
    C.CONTACTS.append(dict(name='RiverWalk section: river, rip-rap, riparian strip, rail, promenade, planters, blocks; the Peace Bridge landing', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(35, -45, 45), fill=(-40, -25, 30), rear=(-20, 40, 30), target=(-4.0, 0, 2.0), gain=3.4)
