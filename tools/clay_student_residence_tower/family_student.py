"""Student residence tower with a glass roof dome, authored from the locked catalogue views of
student_residence_tower / variant_0 (contemporary_curtainwall_biophilic).

Read from the pixels (the top view governs the plan): a twelve-storey tower on a corner with streets
south and west. A two-storey glazed base between white columns under a white band, with a sloping
white soffit at its east end; above it a tall white blade with horizontal joints on the west face that
widens upward, leans out at the south and rises above the roof in a curved corner; a set-back planted glass strip
north of it; elsewhere floor-to-ceiling glass bands whose white slab edges tilt from floor to floor,
broken by recessed planted terraces; on the roof, behind a white steel lattice screen with glass, a
geodesic glass dome over the study lounge, a pale plant penthouse with rooftop units, a roof garden
and an open stair.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-student-residence-tower'
X0, X1, Y0, Y1 = -13.0, 13.0, -15.0, 15.0        # tower plate 26 x 30 m (top view)
BX1, BY0 = X1 + 1.2, Y0 - 1.2                     # base projects south and east
BLADE_X = (X0 - .3, X0 + 1.8)                     # white blade on the west face: outer and inner planes
BLADE_N = (Y0 + 16.0, Y0 + 22.5)                  # its north edge at the base and at the roof (it widens upward)
BLADE_LEAN = .9                                   # its south edge leans out past the south face by the roof
GW = X0 + 1.85                                    # set-back west glass line (behind the blade, open north of it)
T = .30
G0 = .15
BASE = [G0, 4.15]
BASE_TOP = 8.15
FH = 3.3
N = 10
LEVELS = [BASE_TOP + i * FH for i in range(N)]
ROOF = BASE_TOP + N * FH                          # 41.15
DOME = (2.5, -2.0, 6.0, 5.0)                      # centre x, y, radius, height
EPS = .002
PALETTE = dict(wall=(.90, .90, .88), joint=(.74, .74, .72), trim=(.16, .17, .18),
    pale=(.84, .84, .82), stone=(.76, .75, .72), roof=(.66, .65, .62), sand=(.72, .70, .66),
    foundation=(.42, .42, .41), glass=(.44, .54, .58), hardware=(.20, .21, .22),
    interior=(.82, .80, .76), floor=(.50, .48, .46), timber=(.50, .36, .22), blue=(.16, .30, .38),
    planting=(.28, .44, .18), soil=(.22, .16, .10), concrete=(.74, .73, .70), white=(.94, .94, .92),
    asphalt=(.30, .30, .31), membrane=(.70, .69, .66), domeglass=(.62, .72, .76))


def manifest(version):
    h = ROOF + DOME[3] + 1.5
    cams = G.camera_roster(X1 - X0 + 4.0, Y1 - Y0 + 4.0, h, [
        ('facade_close', (4.0, -36.0, 22.0), (5.0, Y0, 22.0), 45),
        ('architecture_close', (-24.0, -30.0, 18.0), (X0, Y0, 20.0), 45),
        ('glass_close', (8.0, -26.0, 14.0), (8.0, Y0, 15.0), 45),
        ('glazed_base', (6.0, -30.0, 2.5), (4.0, BY0, 4.0), 45),
        ('slab_edges', (24.0, -30.0, 30.0), (X1, -6.0, 28.0), 45),
        ('planted_terrace', (-2.0, -26.0, LEVELS[6] + 2.0), (1.0, Y0, LEVELS[6] + 1.0), 45),
        ('roof_dome', (22.0, -24.0, 58.0), (DOME[0], DOME[1], ROOF + 2.0), 40),
        ('lattice_screen', (-26.0, 24.0, 50.0), (-6.0, 8.0, ROOF + 1.2), 45),
        ('interior', (9.0, -10.0, LEVELS[4] + 1.6), (4.0, Y0 - 1.0, LEVELS[4] + 1.2), 60),
        ('rear_north', (2.0, 40.0, 18.0), (2.0, Y1, 20.0), 45)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='student_residence_tower/variant_0 (contemporary_curtainwall_biophilic)',
        measurement_contract=dict(dimensions_m=dict(width=BX1 - X0, depth=Y1 - BY0, height=h),
            observed_storeys=2 + N, storey_programme='two-storey glazed base (study commons, bike room, cafe), ten residence storeys, roof lounge under the dome',
            plan='26 x 30 m tower plate; base projecting 1.2 m south and east; white blade 2.1 m thick over about 75% of the west face, widening upward, with a set-back glass strip north of it; dome 12 m across near the roof centre (top view)',
            facade='white columns and band over the glazed base with a sloping white soffit at the east end; white wall mass with horizontal joints; glass bands with white slab edges tilting alternately from floor to floor; recessed planted terraces',
            levels_m=BASE + LEVELS + [ROOF],
            inferred='storey heights and interiors are teaching assumptions; the north and east faces are not visible in the front or oblique and repeat the visible grammar'),
        roof_contract=dict(type='flat roof garden behind a white lattice screen with glass; geodesic glass dome; plant penthouse', datum_m=ROOF, crowns_m=[ROOF + 2.4, ROOF + DOME[3]]),
        identity_contract=dict(owner='white wall mass beside glass bands with tilting slab edges, planted terrace recesses, glazed two-storey base, glass roof dome behind a lattice screen'),
        material_contract=dict(profile='source-palette clay: white panels and slab edges, clear glass with dark mullions, planting, pale penthouse, glass dome on white ribs', textured_keeper=False),
        programme_contract=dict(storeys=2 + N, base='study commons, cafe and bike room', upper='student rooms in clusters round shared kitchens', roof='dome lounge and garden'),
        contact_contract=['Grade-zero slab and sidewalks', 'Tower on the base slab', 'Terraces recessed into the floor plates', 'Dome and penthouse on the roof slab', 'Lattice screen on the roof edge'],
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


# ---- student residence tower ----

def tilt(k):
    """Slab-edge tilt for floor k: alternate rises and falls across the face (front view)."""
    return .7 if k % 2 == 0 else -.7


def glass_face(f, lo, hi, z0, z1, tag, terraces=(), tilted=True):
    """Floor-to-ceiling glass behind white slab edges that tilt from floor to floor; recessed planted terraces."""
    span = hi - lo
    h = hole(f'{tag} curtain wall', (lo + hi) / 2, z0 + .1, span - .4, z1 - z0 - .2, kind='band')
    f.wall(f'{tag} spandrel carrier', lo, hi - EPS, z0, z1, depth=T, role='trim', holes=[h])
    m = Merge(f)
    m.box('glass', h['u'], .14, h['z'] + h['h'] / 2, h['w'] - .02, .012, h['h'] - .02)
    register(f, h, .12, 'curtain wall', 'student rooms')
    k = 0
    u = lo + .9
    while u < hi - .5:
        m.box('trim', u, .08, h['z'] + h['h'] / 2, .06, .08, h['h'])
        u += 1.5
    m.flush(tag + ' glass')
    for i, z in enumerate([z0 + FH * j for j in range(int(round((z1 - z0) / FH)) + 1)]):
        t = tilt(i) if tilted else 0.0
        za, zb = z - .25 - t / 2, z - .25 + t / 2
        pa, pb = f.p(lo, 0, 0), f.p(hi, 0, 0)
        # Tilted white slab edge as a prism along the face normal.
        if abs(f.t[0]) > .5:
            xa, xb = (pa[0], pb[0]) if pa[0] < pb[0] else (pb[0], pa[0])
            ta, tb = (za, zb) if pa[0] < pb[0] else (zb, za)
            dep = (.7, 1.2, .9, 1.5, .8)[i % 5]                       # uneven slab-end projections
            y = pa[1]; d = -dep if f.n[1] > 0 else dep
            C.prism(f'{tag} slab edge', [(xa, ta), (xb, tb), (xb, tb + .42), (xa, ta + .42)], 'y', min(y, y + d), max(y, y + d), 'white', 'slab edges')
        else:
            ya, yb = (pa[1], pb[1]) if pa[1] < pb[1] else (pb[1], pa[1])
            ta, tb = (za, zb) if pa[1] < pb[1] else (zb, za)
            dep = (.7, 1.2, .9, 1.5, .8)[i % 5]
            x = pa[0]; d = -dep if f.n[0] > 0 else dep
            C.prism(f'{tag} slab edge', [(ya, ta), (yb, tb), (yb, tb + .42), (ya, ta + .42)], 'x', min(x, x + d), max(x, x + d), 'white', 'slab edges')
    for (u0, u1, fl) in terraces:                                     # deep planted terraces at the slab ends
        z = z0 + fl * FH
        m = Merge(f)
        m.box('white', (u0 + u1) / 2, -1.25, z - .12, u1 - u0, 2.5, .34)
        m.box('concrete', (u0 + u1) / 2, -2.2, z + .45, u1 - u0, .6, .8)
        m.box('planting', (u0 + u1) / 2, -2.2, z + .87, u1 - u0 - .1, .5, .05)
        m.box('glass', (u0 + u1) / 2, -2.48, z + 1.2, u1 - u0 - .1, .02, .7)
        m.flush(tag + ' terrace')
        for q in range(int((u1 - u0) / .9)):
            p = f.p(u0 + .45 + q * .9, -2.2, 0)
            A.shrub(p[0], p[1], z + .89, 1.0 + .3 * (q % 3))
        p = f.p((u0 + u1) / 2, -1.0, 0)
        A.small_tree(p[0], p[1], z + .05, 2.6, 1.1)


def blade_edges(z):
    """South and north edges (y) of the white blade at height z: it leans out at the south and widens northward."""
    zt = ROOF + 3.4 - 3.0
    ys = Y0 - BLADE_LEAN * min(1.0, max(0.0, (z - BASE_TOP) / (zt - BASE_TOP)))
    yn = BLADE_N[0] + (BLADE_N[1] - BLADE_N[0]) * min(1.0, max(0.0, (z - BASE_TOP) / (ROOF + 1.4 - BASE_TOP)))
    return ys, yn


def blade():
    """Tall white blade on the west face: leaning south edge, widening north edge, curved top corner above the roof,
    horizontal joints on its faces."""
    R = 3.0
    ys_top, zt = Y0 - BLADE_LEAN, ROOF + 3.4
    arc = [(ys_top + R - R * math.sin(a), zt - R + R * math.cos(a)) for a in [math.pi / 2 * i / 10 for i in range(11)]]
    poly = [(Y0, BASE_TOP), (BLADE_N[0], BASE_TOP), (BLADE_N[1], ROOF + 1.4)] + arc
    C.prism('White blade', poly, 'x', BLADE_X[0], BLADE_X[1], 'wall', 'white blade')
    vs, fs = [], []
    k = 1
    while BASE_TOP + k * FH / 2 < ROOF + .8:
        z = BASE_TOP + k * FH / 2
        ys, yn = blade_edges(z)
        for x in (BLADE_X[0] - .004,):
            o = len(vs)
            vs += [(x, ys + .05, z), (x, yn - .05, z), (x, yn - .05, z + .03), (x, ys + .05, z + .03)]
            fs.append((o, o + 1, o + 2, o + 3))
        o = len(vs)                                                     # joint returning round the south edge
        vs += [(BLADE_X[0] + .05, ys - .004, z), (BLADE_X[1] - .05, ys - .004, z), (BLADE_X[1] - .05, ys - .004, z + .03), (BLADE_X[0] + .05, ys - .004, z + .03)]
        fs.append((o, o + 1, o + 2, o + 3))
        k += 1
    C.mesh('White blade joints', vs, fs, 'joint', 'white blade')
    C.CONTACTS.append(dict(name='White blade on the base roof, rising through the roof screen line', blade_x=list(BLADE_X), north_edge=list(BLADE_N)))


def base():
    s = C.Face(((X0 + BX1) / 2, BY0, 0), (1, 0, 0), (0, 1, 0), 'base south')
    hw = (BX1 - X0) / 2
    holes_s = [hole(f'base south glazing {i}', -hw + 4.53 * (i + .5), G0, 3.9, BASE_TOP - .9 - G0, kind='storefront') for i in range(6)]
    s.wall('base south carrier', -hw, hw - EPS, G0, BASE_TOP, depth=T, role='white', holes=holes_s)
    m = Merge(s)
    for h in holes_s:
        framed(m, s, h, cols=3, rows=2, inset=.14, occupied='study commons', kind='storefront')
    m.box('white', 0, -.2, BASE_TOP - .45, 2 * hw, T + .4, .9)
    m.flush('base south')
    e = C.Face((BX1, (BY0 + Y1) / 2, 0), (0, 1, 0), (-1, 0, 0), 'base east')
    hd = (Y1 - BY0) / 2
    holes_e = [hole(f'base east glazing {i}', -hd + T + 4.4 * (i + .5), G0, 3.6, BASE_TOP - .9 - G0, kind='storefront') for i in range(7)]
    e.wall('base east carrier', -hd + T, hd - T, G0, BASE_TOP, depth=T, role='white', holes=holes_e)   # north end inside the north carrier
    m = Merge(e)
    for h in holes_e:
        framed(m, e, h, cols=3, rows=2, inset=.14, occupied='bike room and cafe', kind='storefront')
    m.box('white', 0, -.2, BASE_TOP - .45, 2 * hd - T, T + .4, .9)
    m.flush('base east')
    w = C.Face((X0, (BY0 + Y1) / 2, 0), (0, -1, 0), (1, 0, 0), 'base west')
    holes_w = [hole(f'base west glazing {i}', -hd + T + 4.4 * (i + .5), G0, 3.6, BASE_TOP - .9 - G0, kind='storefront') for i in range(7)]
    w.wall('base west carrier', -hd + T, hd - T, G0, BASE_TOP, depth=T, role='white', holes=holes_w)
    m = Merge(w)
    for h in holes_w:
        framed(m, w, h, cols=3, rows=2, inset=.14, occupied='study commons', kind='storefront')
    m.flush('base west')
    n = C.Face(((X0 + BX1) / 2, Y1, 0), (-1, 0, 0), (0, -1, 0), 'base north')
    n.wall('base north carrier', -hw, hw - EPS, G0, BASE_TOP, depth=T, role='white', holes=[])
    xs0, zs1 = BX1 - 7.0, 5.2                                                # the band sweeps down at the east end (front view)
    zband = lambda x: BASE_TOP - .9 if x <= xs0 else BASE_TOP - .9 + (zs1 - BASE_TOP + .9) * (x - xs0) / (BX1 - xs0)
    C.prism('Sloping band end', [(xs0, BASE_TOP - .85), (BX1, BASE_TOP - .85), (BX1, zs1)], 'y', BY0 - .65, BY0 + .1, 'white', 'base')
    for i in range(7):                                                       # white columns before the south glazing
        x = X0 + .6 + (BX1 - X0 - 1.2) * i / 6
        zt = zband(x) + .05
        C.box('Base column', (x, BY0 - .35, (G0 + zt) / 2), (.5, .5, zt - G0), 'white', 'base', 0)
    C.box('Base slab', ((X0 + BX1) / 2, (BY0 + Y1) / 2, G0 / 2), (BX1 - X0, Y1 - BY0, G0), 'foundation', 'base', 0)
    for z in (BASE[1], BASE_TOP):
        C.box('Base floor', ((X0 + BX1) / 2, (BY0 + Y1) / 2, z - .15), (BX1 - X0 - 2 * T, Y1 - BY0 - 2 * T, .3), 'floor', 'base', 0)
    C.box('Base roof edge', (X1 + .6, (BY0 + Y1) / 2, BASE_TOP + .05), (1.2, Y1 - BY0, .1), 'membrane', 'base', 0)
    C.box('Base roof edge', ((X0 + X1) / 2, BY0 + .6, BASE_TOP + .05), (X1 - X0, 1.2, .1), 'membrane', 'base', 0)
    for x in (-8.0, 0.0, 8.0):
        C.qa_room_light(f'Base commons {x:+.0f}', (x, BY0 + 4.0, BASE[1] - .5), 120, 5.0)
        C.box('Library shelving', (x, BY0 + 6.0, G0 + 1.0), (3.0, .4, 2.0), 'timber', 'base', 0)
        C.box('Study table', (x, BY0 + 3.0, G0 + .74), (2.4, 1.0, .05), 'timber', 'base', 0)


def tower():
    # South: glass from the blade to the east corner; west: set-back glass behind the blade, open north of it.
    s = C.Face(((BLADE_X[1] + X1) / 2, Y0, 0), (1, 0, 0), (0, 1, 0), 'tower south')
    hs = (X1 - BLADE_X[1]) / 2
    glass_face(s, -hs, hs, BASE_TOP, ROOF, s.label, terraces=((hs - 5.5, hs - .4, 2), (hs - 5.5, hs - .4, 5), (-hs + .4, -hs + 5.0, 3), (hs - 5.5, hs - .4, 8), (-hs + .4, -hs + 5.0, 6)))
    w = C.Face((GW, (Y0 + Y1) / 2, 0), (0, -1, 0), (1, 0, 0), 'tower west')
    hw = (Y1 - Y0) / 2
    glass_face(w, -hw + T, hw - T, BASE_TOP, ROOF, w.label)
    e = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'tower east')
    glass_face(e, Y0 + T, Y1 - T, BASE_TOP, ROOF, e.label, terraces=((-12.0, -7.0, 3), (7.0, 12.0, 6)))
    n = C.Face(((GW + X1) / 2, Y1, 0), (-1, 0, 0), (0, -1, 0), 'tower north')
    glass_face(n, -(X1 - GW) / 2, (X1 - GW) / 2, BASE_TOP, ROOF, n.label, tilted=False)
    blade()
    for i, z in enumerate(LEVELS[1:] + [ROOF]):
        if z < ROOF:
            C.box(f'Tower floor {i + 1}', ((GW + T + X1 - T) / 2, 0, z - .15), (X1 - T - GW - T, Y1 - Y0 - 2 * T, .3), 'floor', 'tower floors', 0)
    C.box('Tower roof slab', ((GW + T + X1 - T) / 2, 0, ROOF - .15), (X1 - T - GW - T, Y1 - Y0 - 2 * T, .3), 'floor', 'tower floors', 0)
    # Deep planted terraces on the set-back west strip north of the blade.
    for fl in (1, 2, 4, 5, 7, 9):
        z = BASE_TOP + fl * FH
        ya = blade_edges(z + FH)[1] + .2
        yb = Y1 - .3
        if yb - ya < 2.0:
            continue
        C.box('West strip terrace', ((X0 - .3 + GW - .02) / 2, (ya + yb) / 2, z - .17), (GW - .02 - X0 + .3, yb - ya, .34), 'white', 'west terraces', 0)
        C.box('West strip planter', (X0 + .05, (ya + yb) / 2, z + .4), (.7, yb - ya - .2, .8), 'concrete', 'west terraces', 0)
        C.box('West strip planting', (X0 + .05, (ya + yb) / 2, z + .82), (.6, yb - ya - .3, .05), 'planting', 'west terraces', 0)
        y = ya + .5
        q = 0
        while y < yb - .4:
            A.shrub(X0 + .05, y, z + .84, 1.0 + .35 * (q % 3)); y += .9; q += 1
        A.small_tree(X0 + 1.0, (ya + yb) / 2, z, 2.6, 1.0)
    C.box('Tower core', (2.0, 6.0, (BASE_TOP + ROOF) / 2), (8.0, 6.0, ROOF - BASE_TOP), 'concrete', 'core', 0)
    for z in LEVELS[::2]:
        C.qa_room_light(f'Rooms {z:.0f}', (5.0, Y0 + 3.0, z + FH - .5), 60, 6.0)
        C.qa_room_light(f'Rooms west {z:.0f}', (GW + 3.0, 10.0, z + FH - .5), 50, 5.0)
    zf = LEVELS[4]
    A.desk(6.0, Y0 + 2.4, zf); A.bed(10.0, Y0 + 3.0, zf); A.sofa(2.0, Y0 + 2.6, zf)


def roof():
    cx, cy, r, h = DOME
    C.box('Roof garden paving', ((GW + T + X1 - T) / 2, 0, ROOF + .01), (X1 - T - GW - T - .02, Y1 - Y0 - 2 * T - .02, .02), 'sand', 'roof', 0)
    # Lattice screen with glass round the roof edge, chamfered at the north-east and south-east corners, ending at the blade.
    c = 3.0
    path = [(BLADE_X[1] + .05, Y0 + .2), (X1 - .2 - c, Y0 + .2), (X1 - .2, Y0 + .2 + c), (X1 - .2, Y1 - .2 - c), (X1 - .2 - c, Y1 - .2),
            (X0 + .2, Y1 - .2), (X0 + .2, BLADE_N[1] + .3)]
    for (ax, ay), (bx, by) in zip(path, path[1:]):
        L = math.hypot(bx - ax, by - ay)
        C.beam('Screen glass', (ax, ay, ROOF + 1.2), (bx, by, ROOF + 1.2), .03, 2.2, 'glass', 'lattice screen')
        C.beam('Screen top rail', (ax, ay, ROOF + 2.35), (bx, by, ROOF + 2.35), .14, .14, 'white', 'lattice screen')
        n = max(1, int(L / 2.4))
        for i in range(n):
            p0 = (ax + (bx - ax) * i / n, ay + (by - ay) * i / n)
            p1 = (ax + (bx - ax) * (i + 1) / n, ay + (by - ay) * (i + 1) / n)
            C.beam('Screen lattice', (p0[0], p0[1], ROOF + .15), (p1[0], p1[1], ROOF + 2.3), .1, .1, 'white', 'lattice screen')
            C.beam('Screen lattice', (p0[0], p0[1], ROOF + 2.3), (p1[0], p1[1], ROOF + .15), .1, .1, 'white', 'lattice screen')
    # Geodesic glass dome on a white ring.
    C.rod('Dome ring', (cx, cy, ROOF), (cx, cy, ROOF + .5), r + .25, 'white', 'dome', 32)
    prof = [(1.0, 0.0), (.95, .35), (.72, .75), (0.0, 1.0)]
    dome('Glass dome', cx, cy, ROOF + .5, r, h, prof, 'domeglass', 'dome', segs=32, n=12)
    sp = [(r * pr, h * ph) for pr, ph in smooth_profile(prof, 12)]
    for k in range(16):
        rib_mesh('Dome rib', cx, cy, ROOF + .5, math.tau * k / 16, sp, .07, .02, 'white', 'dome')
    for frac in (.35, .65, .85):
        rr = r * smooth_profile(prof, 12)[int(frac * 12)][0]
        zz = ROOF + .5 + h * smooth_profile(prof, 12)[int(frac * 12)][1]
        annulus('Dome ring rib', (cx, cy, zz), (0, 0, 1), rr - .02, rr + .07, -.04, .04, 'white', 'dome', segs=32)
    # Plant penthouse with units, roof garden planters, open stair.
    C.box('Plant penthouse', (-1.0, 9.5, ROOF + 1.6), (12.0, 7.0, 3.2), 'pale', 'penthouse', 0)
    for x in (-5.0, -3.4, -1.8):
        C.box('Rooftop unit', (x, 8.6, ROOF + 3.6), (1.3, 1.0, .8), 'membrane', 'penthouse', 0)
        C.rod('Unit fan', (x, 8.6, ROOF + 4.0), (x, 8.6, ROOF + 4.06), .4, 'hardware', 'penthouse', 10)
    C.box('Duct box', (2.6, 10.6, ROOF + 3.5), (2.0, 1.4, .6), 'membrane', 'penthouse', 0)
    # Continuous garden beds along the north and east edges and a ring bed round the dome.
    for name, (x0b, x1b, y0b, y1b) in (('north', (X0 + 1.0, X1 - 4.0, Y1 - 2.3, Y1 - .7)), ('east', (X1 - 2.3, X1 - .7, Y0 + 3.6, Y1 - 3.6))):
        C.box(f'Roof bed {name}', ((x0b + x1b) / 2, (y0b + y1b) / 2, ROOF + .35), (x1b - x0b, y1b - y0b, .7), 'concrete', 'roof garden', 0)
        C.box(f'Roof bed {name} planting', ((x0b + x1b) / 2, (y0b + y1b) / 2, ROOF + .72), (x1b - x0b - .2, y1b - y0b - .2, .04), 'planting', 'roof garden', 0)
        L = max(x1b - x0b, y1b - y0b); along_x = (x1b - x0b) > (y1b - y0b)
        for q in range(int(L / 1.1)):
            t = .55 + q * 1.1
            A.shrub(x0b + t if along_x else (x0b + x1b) / 2, (y0b + y1b) / 2 if along_x else y0b + t, ROOF + .74, .9 + .3 * (q % 3))
    annulus('Dome ring bed', (cx, cy, ROOF), (0, 0, 1), r + .7, r + 1.9, 0, .6, 'concrete', 'roof garden', segs=32)
    annulus('Dome ring planting', (cx, cy, ROOF + .6), (0, 0, 1), r + .8, r + 1.8, 0, .04, 'planting', 'roof garden', segs=32)
    for q in range(14):
        a_ = math.tau * q / 14 + .2
        A.shrub(cx + (r + 1.3) * math.cos(a_), cy + (r + 1.3) * math.sin(a_), ROOF + .64, .8 + .3 * (q % 3))
    # Open stair up the penthouse's west side to its roof deck, with handrails.
    n_st, run, rise = 12, .4, 3.2 / 12
    for k in range(n_st):
        C.box('Roof stair tread', (-11.8 + k * run + run / 2, 7.2, ROOF + rise * (k + 1) - .05), (run + .02, 1.3, .1), 'white', 'roof stair', 0)
    for y in (6.52, 7.88):
        C.beam('Roof stair stringer', (-11.8, y, ROOF + .02), (-7.0, y, ROOF + 3.2), .06, .3, 'hardware', 'roof stair')
        C.beam('Roof stair handrail', (-11.8, y, ROOF + 1.0), (-7.0, y, ROOF + 4.2), .05, .05, 'hardware', 'roof stair')
        for k in (0, 6, 12):
            x = -11.8 + k * run
            C.beam('Roof stair post', (x, y, ROOF + rise * k), (x, y, ROOF + rise * k + 1.0), .05, .05, 'hardware', 'roof stair')
    C.qa_room_light('Dome lounge', (cx, cy, ROOF + 2.5), 80, 4.0)


def site():
    C.box('South sidewalk', (2.0, BY0 - 3.0, .07), (44.0, 6.0, .14), 'sand', 'site', 0)
    C.box('West sidewalk', (X0 - 3.0, (BY0 + Y1) / 2, .07), (6.0, Y1 - BY0, .14), 'sand', 'site', 0)
    C.box('South street', (2.0, BY0 - 11.0, .01), (54.0, 10.0, .02), 'asphalt', 'site', 0)
    C.box('West street', (X0 - 11.0, (BY0 + Y1) / 2, .01), (10.0, Y1 - BY0, .02), 'asphalt', 'site', 0)
    C.box('East lot', (BX1 + 3.0, (BY0 + Y1) / 2, .01), (6.0, Y1 - BY0, .02), 'concrete', 'site', 0)
    for x in (-10.0, 4.0, 16.0):
        street_tree(x, BY0 - 2.6, z=.14, height=7.0, spread=1.7)
    for y in (-6.0, 8.0):
        street_tree(X0 - 2.6, y, z=.14, height=7.0, spread=1.7)


def build():
    site()
    base()
    tower()
    roof()
    C.CONTACTS.append(dict(name='Tower on the base slab; white blade on the west face; dome and penthouse on the roof slab', roof_m=ROOF))


LIGHT_RIG = dict(key=(-60, -70, 80), fill=(70, -30, 60), rear=(-20, 70, 70), target=(0, 0, 20.0), gain=26.0)
