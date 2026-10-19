"""Planted green bridge, authored from the locked catalogue views of
landscape_park_pedestrian_bridge / variant_2 (Planted Green Bridge).

Read from the pixels (the top view governs the plan): a straight, level pedestrian bridge running north-south
across a river between planted banks. A pale central path about 4 m wide runs between two deep planting beds of
grasses, shrubs, lavender, red flowers and small trees, each bed edged by a low steel rail with bollard lights on
the path side and a timber-capped steel picket railing on a weathering-steel edge beam on the outer side. Near
mid-river two elongated hexagonal viewing pods project from the beds, one each side, planted and railed, their
rusted steel fascias carried on concrete cross-heads and paired round columns standing in the water. Rip-rap
banks, a riverside path under the bridge on each bank, trees, a parking lot, and brick towers as context.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-planted-green-bridge'
X0, X1, Y0, Y1 = -16.0, 16.0, -40.0, 40.0      # deck with its pods (32 m) and an 80 m run across the river
ZD = 6.0                                        # path level above the water surface
PW = 2.0                                        # half-width of the central path
DW = 6.95                                       # half-width of the planted deck to the edge beams
RN, RS = 10.25, -10.0                           # north and south water lines
ZB = 2.2                                        # bank level
T = .3
EPS = .002
PALETTE = dict(water=(.20, .40, .44), rock=(.58, .56, .52), soil=(.30, .25, .18), grass=(.50, .58, .30),
    planting=(.22, .36, .14), shrub=(.16, .32, .12), tree=(.20, .38, .14), lavender=(.52, .42, .70),
    flower=(.82, .22, .12), straw=(.68, .62, .36), timber=(.52, .42, .30), corten=(.50, .24, .11),
    steel=(.20, .21, .22), rail=(.58, .59, .60), concrete=(.70, .69, .66), path=(.76, .74, .70),
    asphalt=(.30, .30, .31), white=(.95, .95, .93), brick=(.62, .38, .28), dark=(.16, .17, .19),
    pale=(.90, .90, .86), hardware=(.30, .30, .32), glass=(.24, .30, .34), wall=(.62, .38, .28),
    trim=(.92, .92, .90), interior=(.84, .80, .74), floor=(.58, .48, .38), stone=(.70, .64, .54),
    sand=(.70, .66, .58), blue=(.20, .30, .40), pot=(.60, .34, .22))


def manifest(version):
    h = 14.0
    cams = G.camera_roster(X1 - X0 + 6.0, Y1 - Y0 + 4.0, h, [
        ('facade_close', (34.0, 3.0, 4.5), (9.0, 3.0, 4.8), 40),
        ('architecture_close', (-24.0, -10.0, 9.5), (-13.0, 1.0, 5.6), 40),
        ('glass_close', (2.6, -12.0, ZD + 1.5), (2.0, -4.0, ZD + .9), 40),
        ('planting_bed', (-3.6, -22.0, ZD + 2.6), (-4.4, -12.0, ZD + .4), 40),
        ('central_path', (0.0, -34.0, ZD + 1.7), (0.0, 0.0, ZD + 1.1), 35),
        ('viewing_pod', (-4.0, -8.0, ZD + 3.6), (-11.5, 3.0, ZD + .4), 40),
        ('pier_column', (-26.0, -9.0, 2.2), (-11.5, .7, 2.6), 40),
        ('rail_bollard', (5.4, -18.0, ZD + 1.5), (7.0, -11.0, ZD + .9), 40),
        ('water_under', (14.0, -8.5, 1.0), (0.0, 4.0, 4.2), 35),
        ('rear_north', (0.0, 52.0, ZD + 6.0), (0.0, 8.0, ZD), 40)])
    for c in cams:                       # the locked front walks north along the path; the oblique stands high over it
        if c['name'] == 'front':
            c.update(location=(.3, -25.0, ZD + 1.6), target=(0.0, 10.0, ZD + 1.6), lens=24, whole=False)
        elif c['name'] == 'front_corner':
            c.update(location=(0.0, -30.0, ZD + 8.5), target=(0.0, 14.0, ZD - .5), lens=26, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(36.0, -42.0, 38.0), target=(0.0, 0.0, ZD - 1.0), lens=35, whole=False)
        elif c['name'] == 'top':
            c.update(location=(0.0, 0.0, 90.0), target=(0.0, .001, 0.0), ortho_scale=62.0, whole=False)
        elif c['name'] == 'left_side':
            c.update(location=(-48.0, -4.0, 11.0), target=(0.0, 0.0, ZD - 1.5), lens=35, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(48.0, 4.0, 11.0), target=(0.0, 0.0, ZD - 1.5), lens=35, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(-2.0, 30.0, ZD + 4.0), target=(0.0, -6.0, ZD), lens=28, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(34.0, 38.0, 24.0), target=(0.0, 0.0, ZD - 1.0), lens=35, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='landscape_park_pedestrian_bridge/variant_2 (Planted Green Bridge)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=0, storey_programme='street option: a level planted pedestrian bridge over a river; the banks, trees and blocks are context',
            plan='14 m deck (4 m path between two planting beds) on an 80 m run across a 20 m river (top view), two hexagonal planted viewing pods projecting 8.5 m each side near mid-river',
            section_m=dict(path=[-PW, PW], planting_beds=[PW, DW], edge_beams=[DW, DW + .3], deck_level=ZD, water=0.0, banks=ZB),
            facade='pale path, dense beds of grasses, shrubs, lavender, red flowers and small trees, low steel inner rails with bollard lights, timber-capped picket railings on weathering-steel edge beams, rusted pod fascias, concrete cross-heads and round columns',
            levels_m=[0.0, ZB, ZD], inferred='the deck structure under the planting, the far banks and the blocks are teaching assumptions; the bridge is shown as a section cut at both ends'),
        roof_contract=dict(type='open street option; no roof', datum_m=ZD, crowns_m=[h]),
        identity_contract=dict(owner='wide planted bridge with a central path between lush beds, railings and bollard lights, hexagonal planted viewing pods on concrete columns over water'),
        material_contract=dict(profile='source-palette clay: pale path, greens of shrubs and grasses with lavender and red flowers, weathering steel, grey steel rails, timber handrail caps, pale concrete, blue-green water, grey rip-rap', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='walking path, planting beds, viewing pods'),
        street_contract=dict(kind='fixed_native_section', width_m=2 * DW + .6, axis='y', junction_finish='pavers',
                             bands=['edge_rail', 'planting_bed', 'path', 'planting_bed', 'edge_rail'], pods=['west viewing pod', 'east viewing pod']),
        contact_contract=['River surface at grade zero', 'Columns standing in the water', 'Cross-heads under the pods and the deck girders',
                          'Land columns on the banks', 'Planting on the deck soil'],
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
# ---- Planted green bridge ----

import random

RNG = random.Random(2610)                       # fixed seed: the same planting on every build

PHI = (1 + 5 ** .5) / 2
ICO_V = [(-1, PHI, 0), (1, PHI, 0), (-1, -PHI, 0), (1, -PHI, 0), (0, -1, PHI), (0, 1, PHI), (0, -1, -PHI), (0, 1, -PHI),
         (PHI, 0, -1), (PHI, 0, 1), (-PHI, 0, -1), (-PHI, 0, 1)]
ICO_F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
         (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
ICO_N = math.sqrt(1 + PHI * PHI)


def blob(b, role, cx, cy, cz, rx, ry, rz, j=.12):
    """A low-poly planting mass: a jittered icosahedron merged into the batch."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for x, y, z in ICO_V:
        k = 1 + RNG.uniform(-j, j)
        V.append((cx + rx * k * x / ICO_N, cy + ry * k * y / ICO_N, max(0.0, cz + rz * k * z / ICO_N)))
    F.extend(tuple(o + i for i in f) for f in ICO_F)


def tuft(b, role, cx, cy, z0, h, r, n=5):
    """A clump of grass or a flower spike: a narrow leaning cone."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for i in range(n):
        a = 2 * math.pi * (i + RNG.random() * .3) / n
        V.append((cx + r * math.cos(a), cy + r * math.sin(a), z0))
    V.append((cx + RNG.uniform(-.12, .12), cy + RNG.uniform(-.12, .12), z0 + h))
    F.append(tuple(o + i for i in range(n - 1, -1, -1)))
    for i in range(n):
        F.append((o + i, o + (i + 1) % n, o + n))


def cyl(b, role, cx, cy, z0, z1, r, n=14):
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for z in (z0, z1):
        for i in range(n):
            a = 2 * math.pi * (i + .5) / n
            V.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    F.append(tuple(o + i for i in range(n - 1, -1, -1)))
    F.append(tuple(o + n + i for i in range(n)))
    for i in range(n):
        j = (i + 1) % n
        F.append((o + i, o + j, o + n + j, o + n + i))


def railing(b, pts, z, post=1.6, picket=.2):
    """Steel picket railing with a timber cap along a polyline at base level z."""
    for (ax, ay), (cx, cy) in zip(pts, pts[1:]):
        L = math.hypot(cx - ax, cy - ay)
        b.beam('timber', (ax, ay, z + 1.07), (cx, cy, z + 1.07), .14, .06, ext=.04)
        b.beam('rail', (ax, ay, z + .12), (cx, cy, z + .12), .05, .04, ext=.02)
        b.beam('rail', (ax, ay, z + .98), (cx, cy, z + .98), .05, .04, ext=.0)
        n = max(1, int(L / post))
        for i in range(n + 1):
            t = i / n
            b.box('rail', ax + (cx - ax) * t, ay + (cy - ay) * t, z + .52, .06, .06, 1.0)
        k = max(1, int(L / picket))
        for i in range(1, k):
            t = i / k
            b.box('rail', ax + (cx - ax) * t, ay + (cy - ay) * t, z + .55, .018, .018, .86)


def pod_poly(s):
    """Elongated half-hexagon viewing pod on side s (-1 west, +1 east), read from the top view."""
    pts = [(DW, 10.0), (12.0, 10.0), (15.5, 6.5), (15.5, 0.0), (11.0, -3.0), (DW, -3.5)]
    return [(s * x, y) for x, y in pts]


def inset(poly, d):
    cx = sum(p[0] for p in poly) / len(poly); cy = sum(p[1] for p in poly) / len(poly)
    out = []
    for x, y in poly:
        if abs(abs(x) - DW) < 1e-6:                                                         # the edge on the deck stays put
            out.append((x, y + (-d if y > cy else d)))
        else:
            dx, dy = x - cx, y - cy
            L = math.hypot(dx, dy)
            out.append((x - dx / L * d * 1.2, y - dy / L * d * 1.2))
    return out


def ccw(poly):
    a = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]))
    return poly if a > 0 else poly[::-1]


def river_and_banks():
    C.box('River', (0.0, (RN + RS) / 2, .01), (140.0, RN - RS, .02), 'water', 'river', 0)
    C.prism('North bank', [(RN, 0.0), (70.0, 0.0), (70.0, ZB), (RN + 2.6, ZB)], 'x', -70.0, 70.0, 'grass', 'banks')
    C.prism('South bank', [(RS, 0.0), (RS - 2.6, ZB), (-70.0, ZB), (-70.0, 0.0)], 'x', -70.0, 70.0, 'grass', 'banks')
    b = Batch()
    for side, y0, y1 in ((1, RN, RN + 2.6), (-1, RS, RS - 2.6)):                              # rip-rap boulders on both slopes
        for i in range(260):
            x = RNG.uniform(-69.0, 69.0)
            f = RNG.random()
            y = y0 + (y1 - y0) * f
            z = ZB * f
            r = RNG.uniform(.35, .7)
            blob(b, 'rock', x, y, z + .05, r * 1.3, r, r * .7, j=.2)
    b.flush('rip-rap')
    b = Batch()
    for y0, y1 in ((RN + 3.4, RN + 6.0), (RS - 3.4, RS - 6.0)):                             # riverside paths passing under the bridge
        lo, hi = min(y0, y1), max(y0, y1)
        b.box('asphalt', 0.0, (lo + hi) / 2, ZB + .015, 139.8, hi - lo, .05)
        yr = RN + 3.0 if y0 > 0 else RS - 3.0
        for x0, x1 in ((-69.0, -7.5), (7.5, 69.0)):                                           # bank guard rails, broken under the deck
            b.box('rail', (x0 + x1) / 2, yr, ZB + .78, x1 - x0, .08, .1)
            b.box('rail', (x0 + x1) / 2, yr, ZB + .45, x1 - x0, .06, .06)
            for k in range(int((x1 - x0) / 2.5) + 1):
                b.box('rail', x0 + k * 2.5, yr, ZB + .42, .08, .08, .84)
    b.box('asphalt', 21.0, 31.0, ZB + .015, 22.0, 16.0, .05)                                  # parking lot north-east, with bays
    for k in range(10):
        b.box('white', 11.5 + k * 2.4, 31.0, ZB + .045, .1, 5.0, .012)
    b.box('asphalt', -24.0, -32.0, ZB + .015, 30.0, 14.0, .05)                                # parking south-west
    for x, y in ((-12.0, RN + 7.0), (12.0, RS - 7.0), (-30.0, RS - 7.0), (30.0, RN + 7.0)):   # lamps
        b.box('dark', x, y, ZB + 2.2, .12, .12, 4.4)
        b.box('pale', x, y, ZB + 4.55, .3, .3, .35)
    b.flush('bank paths')


def tree(b, x, y, z, h=9.0, s=1.0):
    """Broadleaf tree: a trunk and a rounded crown of overlapping masses."""
    b.box('timber', x, y, z + h * .28, .35 * s, .35 * s, h * .56)
    for dx, dy, dz, r in ((0, 0, .7, 2.8), (-1.5, .6, .62, 2.0), (1.4, -.7, .6, 2.1), (.4, 1.3, .66, 1.9), (-.3, -1.2, .82, 1.8)):
        blob(b, 'tree', x + dx * s, y + dy * s, z + h * dz, r * s, r * s, r * .85 * s)


def bank_planting():
    b = Batch()
    for cx, cy, n, sx, sy in ((-34.0, 22.0, 14, 18.0, 9.0), (34.0, 16.0, 8, 12.0, 4.0), (-36.0, -18.0, 10, 16.0, 5.0),
                              (32.0, -22.0, 12, 16.0, 8.0), (-14.0, 26.0, 5, 6.0, 6.0), (14.0, -26.0, 4, 6.0, 5.0)):
        for i in range(n):
            tree(b, cx + RNG.uniform(-sx, sx), cy + RNG.uniform(-sy, sy), ZB, RNG.uniform(7.5, 11.0), RNG.uniform(.85, 1.15))
    for i in range(70):                                                                       # shrubs along the water's edge
        x = RNG.choice((-1, 1)) * RNG.uniform(9.0, 60.0)
        y = RNG.choice((RN + 2.9, RS - 2.9))
        blob(b, 'shrub', x, y, ZB + .5, 1.1, .8, .8)
    b.flush('bank trees')
    b = Batch()
    for x0, y0, x1, y1, h in ((-46.0, 48.0, -24.0, 62.0, 30.0), (-18.0, 52.0, 4.0, 64.0, 22.0), (12.0, 46.0, 30.0, 60.0, 38.0),
                              (34.0, 50.0, 52.0, 66.0, 26.0)):
        b.box('brick', (x0 + x1) / 2, (y0 + y1) / 2, ZB + h / 2 - .01, x1 - x0, y1 - y0, h)
        for k in range(int((h - 3) / 3.2)):                                                 # window bands on the faces toward the river
            b.box('dark', (x0 + x1) / 2, y0 - .03, ZB + 2.2 + k * 3.2, x1 - x0 - 1.0, .06, 1.4)
            b.box('dark', x0 - .03 if x0 > 0 else x1 + .03, (y0 + y1) / 2, ZB + 2.2 + k * 3.2, .06, y1 - y0 - 1.0, 1.4)
    b.flush('context blocks')


def deck():
    b = Batch()
    b.box('concrete', 0.0, 0.0, 5.525, 2 * DW, Y1 - Y0, .65)                                  # deck slab 5.2..5.85
    b.box('path', 0.0, 0.0, 5.92, 2 * PW, Y1 - Y0, .16)                                       # pale path, top at ZD
    for s in (-1, 1):
        b.box('steel', s * (PW + .04), 0.0, 6.03, .08, Y1 - Y0, .38)                           # path-side curbs
        b.box('planting', s * (DW + PW + .08) / 2, 0.0, 5.995, DW - PW - .08, Y1 - Y0, .31)     # bed soil, top 6.15
        for y0, y1 in ((Y0, -3.5), (10.0, Y1)):                                               # weathering-steel edge beams, open at the pod
            b.box('corten', s * (DW + .15), (y0 + y1) / 2, 5.725, .3, y1 - y0, 1.45)
        b.box('steel', s * 4.5, 0.0, 4.6, .4, Y1 - Y0, 1.2)                                     # main girders 4.0..5.2
    for k in range(int((Y1 - Y0) / 5.0) + 1):
        b.box('steel', 0.0, Y0 + k * 5.0 if k * 5.0 < Y1 - Y0 else Y1 - .2, 4.75, 8.6, .3, .9)
    b.flush('deck')
    b = Batch()                                                                               # cross paths from the main path to the pods
    for s in (-1, 1):
        b.box('path', s * (DW + PW + .08) / 2, 5.0, 6.075, DW - PW - .08, 1.6, .17)
    b.flush('pod paths')
    # Supports: a river pier line under the deck and the pods; land columns on the banks.
    b = Batch()
    b.box('concrete', 0.0, .7, 3.7, 11.0, 2.4, .6)
    for x in (-3.5, 3.5):
        cyl(b, 'concrete', x, .7, .005, 3.4, .62, 16)
    for s in (-1, 1):
        b.box('concrete', s * 11.5, .7, 3.9, 6.0, 2.6, 1.0)
        for x in (10.0, 13.0):
            cyl(b, 'concrete', s * x, .7, .005, 3.4, .68, 16)
    for y in (-30.0, -18.0, 18.0, 30.0):
        for x in (-4.5, 4.5):
            cyl(b, 'concrete', x, y, ZB - .02, 4.0, .45, 12)
    b.flush('supports')
    # Railings: timber-capped pickets on the edge beams, a low steel rail with bollard lights along the path.
    b = Batch()
    for s in (-1, 1):
        for y0, y1 in ((Y0, -3.5), (10.0, Y1)):
            railing(b, [(s * (DW + .15), y0), (s * (DW + .15), y1)], 6.45)
        for y0, y1 in ((Y0 + .3, 4.1), (5.9, Y1 - .3)):
            for z in (.55, .95):
                b.beam('rail', (s * (PW + .2), y0, 6.15 + z), (s * (PW + .2), y1, 6.15 + z), .04, .04)
            k = int((y1 - y0) / 2.0)
            for i in range(k + 1):
                b.box('rail', s * (PW + .2), y0 + (y1 - y0) * i / k, 6.15 + .5, .05, .05, 1.0)
        for i in range(17):                                                                   # bollard lights by the path
            y = Y0 + 2.5 + i * 4.8
            if 3.0 < y < 7.0:
                continue
            cyl(b, 'rail', s * (PW + .35), y, 6.1, 7.05, .11, 10)
            cyl(b, 'pale', s * (PW + .35), y, 7.05, 7.17, .1, 10)
    b.flush('railings')


def pods():
    for s in (-1, 1):
        poly = ccw(pod_poly(s))
        C.prism(f'Pod slab {s:+d}', poly, 'z', 5.2, 5.85, 'concrete', 'pods')
        C.prism(f'Pod walk {s:+d}', poly, 'z', 5.84, 6.0, 'path', 'pods')
        C.prism(f'Pod bed {s:+d}', ccw(inset(pod_poly(s), 1.0)), 'z', 5.99, 6.15, 'planting', 'pods')
        frame = [(x * .97 + (s * .2 if abs(abs(x) - DW) < 1e-6 else 0), y * .97 + .1) for x, y in pod_poly(s)]
        C.prism(f'Pod frame {s:+d}', ccw(frame), 'z', 4.4, 5.2, 'steel', 'pods')
        b = Batch()
        pts = pod_poly(s)
        edges = list(zip(pts, pts[1:]))
        for (ax, ay), (cx, cy) in edges:                                                      # rusted fascia round the outer edges
            b.beam('corten', (ax, ay, 5.55), (cx, cy, 5.55), .3, 1.9, ext=.15)         # top 6.5, clear of the edge-beam tops
        b.flush(f'pod fascia {s:+d}')
        b = Batch()
        railing(b, pts, 6.5)
        b.flush(f'pod railing {s:+d}')


def planting():
    """Dense, varied beds: shrubs, grasses, lavender, red flowers and a few small trees, kept clear of the path."""
    b = Batch()
    zs = 6.15
    for s in (-1, 1):
        y = Y0 + .6
        while y < Y1 - .6:
            if 4.0 < y < 6.0:
                y += 2.0
                continue
            x = s * RNG.uniform(PW + .9, DW - .7)
            blob(b, 'shrub', x, y, zs + .35, RNG.uniform(.6, .95), RNG.uniform(.6, .95), RNG.uniform(.45, .7))
            for k in range(3):                                                                # grasses
                tuft(b, RNG.choice(('grass', 'straw', 'grass')), s * RNG.uniform(PW + .5, DW - .3), y + RNG.uniform(-.7, .7),
                     zs, RNG.uniform(.7, 1.3), RNG.uniform(.18, .3))
            if RNG.random() < .7:                                                             # lavender drifts
                lx = s * RNG.uniform(PW + .5, DW - .5)
                for k in range(3):
                    tuft(b, 'lavender', lx + RNG.uniform(-.3, .3), y + RNG.uniform(-.4, .4), zs, RNG.uniform(.5, .8), .16)
            if RNG.random() < .5:                                                             # red flowers
                fx, fy = s * RNG.uniform(PW + .6, DW - .5), y + RNG.uniform(-.6, .6)
                for k in range(4):
                    blob(b, 'flower', fx + RNG.uniform(-.3, .3), fy + RNG.uniform(-.3, .3), zs + RNG.uniform(.5, .8), .09, .09, .08, j=.05)
                blob(b, 'planting', fx, fy, zs + .25, .45, .45, .3)
            y += RNG.uniform(1.2, 1.7)
        for y in (-30.0, -17.0, 15.0, 26.0, 36.0):                                            # small trees in the beds
            tree(b, s * 4.6, y + RNG.uniform(-1, 1), zs, RNG.uniform(4.5, 6.0), .55)
    for s in (-1, 1):                                                                         # the pods: a planted mound inside the walk
        poly = inset(pod_poly(s), 1.4)
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
        for i in range(70):
            x, y = RNG.uniform(min(xs), max(xs)), RNG.uniform(min(ys), max(ys))
            inside = all((bx - ax) * (y - ay) - (by - ay) * (x - ax) >= -.01 for (ax, ay), (bx, by) in zip(ccw(poly), ccw(poly)[1:] + ccw(poly)[:1]))
            if not inside:
                continue
            r = RNG.random()
            if r < .45:
                blob(b, 'shrub', x, y, zs + .35, RNG.uniform(.6, 1.0), RNG.uniform(.6, 1.0), RNG.uniform(.45, .75))
            elif r < .8:
                tuft(b, RNG.choice(('grass', 'straw')), x, y, zs, RNG.uniform(.8, 1.3), .25)
            else:
                tuft(b, 'lavender', x, y, zs, .7, .18)
        tree(b, s * 11.5, 5.5, zs, 5.5, .6)
        tree(b, s * 9.0, 1.0, zs, 4.8, .5)
    b.flush('planting')


def build():
    river_and_banks()
    bank_planting()
    deck()
    pods()
    planting()
    C.CONTACTS.append(dict(name='Planted bridge: path between beds on a girder deck, pods on cross-heads and columns in the river, banks with paths', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(35, -45, 45), fill=(-40, -25, 30), rear=(-20, 40, 30), target=(0.0, 0.0, 4.0), gain=3.4)
