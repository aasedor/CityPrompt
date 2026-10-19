"""Riveted steel through-truss road bridge, authored from the locked catalogue views of
urban_vehicular_bridge / variant_1 (Industrial Steel Truss).

Read from the pixels (the top view governs the plan): a two-lane city street crossing a river that runs east-west
between concrete quays, the bridge running north-south. One span of two rust-red riveted Pratt trusses with inclined
end posts and laced verticals, gusset plates at the panel points, a top chord braced by latticed struts and X
laterals, latticed portal frames with knee braces over the roadway at both ends. The road deck between the trusses
carries two lanes with a double yellow centre line and white edge lines; outside each truss a concrete sidewalk with
a rust-red steel railing of pickets. The span rests on red-brick abutments with concrete caps at the quays; quay
railings run along the river; brick warehouses, street trees and parked cars make the context.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-steel-truss-road-bridge'
L = 34.0                                        # truss length between end bearings (top view), the bridge runs along y
NP = 7                                          # truss panels
QY = 14.5                                       # quay faces (y): the river is 29 m wide
XT = 6.5                                        # truss lines (x = +-6.5)
XR = 9.4                                        # sidewalk railings
X0, X1, Y0, Y1 = -XR - .3, XR + .3, -L / 2 - .5, L / 2 + .5
DECK = 5.0                                      # road surface and quay level above the water
HT = 7.5                                        # top chord above the bottom chord
T = .3
EPS = .002
PALETTE = dict(steel=(.44, .20, .12), steel2=(.36, .16, .10), gusset=(.40, .18, .11), water=(.08, .10, .10),
    concrete=(.72, .71, .68), quay=(.60, .59, .56), brick=(.50, .25, .18), joint=(.62, .58, .52), asphalt=(.24, .24, .25),
    white=(.92, .92, .90), yellow=(.82, .66, .16), paving=(.70, .68, .64), glass=(.20, .24, .27), dark=(.10, .10, .11),
    hardware=(.13, .14, .14), trim=(.80, .78, .74), wall=(.52, .27, .19), roof=(.50, .50, .50), interior=(.84, .80, .74),
    floor=(.58, .48, .38), planting=(.30, .44, .20), tree=(.28, .44, .18), timber=(.46, .34, .22), soil=(.22, .16, .10),
    car=(.42, .40, .36), car2=(.62, .60, .58), bus=(.86, .86, .84), pale=(.88, .88, .86), sand=(.70, .66, .58),
    blue=(.20, .30, .40), pot=(.60, .34, .22), stone=(.70, .68, .63))


def manifest(version):
    h = DECK + HT + 1.0
    zt = DECK + .15 + HT
    cams = G.camera_roster(X1 - X0, Y1 - Y0, h, [
        ('facade_close', (-24.0, -3.0, 8.5), (-XT, 0.0, 8.8), 40),
        ('architecture_close', (-12.0, -25.0, 12.0), (-XT, -L / 2 + 3.0, 10.5), 40),
        ('glass_close', (-10.5, -6.5, zt - .2), (-XT, -L / 2 + 2 * L / NP, zt - .4), 45),
        ('portal_frame', (0.0, -31.0, 7.5), (0.0, -L / 2 + 3.0, 10.0), 40),
        ('truss_panel', (-16.0, 3.0, 7.5), (-XT, 1.5, 8.2), 40),
        ('deck_sidewalk', (8.1, -12.0, DECK + 1.75), (8.1, 10.0, DECK + .9), 35),
        ('abutment', (-14.0, -4.0, 2.4), (-7.0, -QY + .4, 3.0), 35),
        ('roadway_inside', (1.8, -16.0, DECK + 1.6), (0.0, 12.0, DECK + 3.0), 28),
        ('river_underside', (15.0, 0.5, 1.4), (0.0, 0.0, 3.8), 35),
        ('rear_north', (-13.0, 36.0, 9.0), (0.0, QY, 8.0), 35)])
    for c in cams:
        if c['name'] == 'front':                     # the locked front: on the east sidewalk at the south end, looking north-west into the portal
            c.update(location=(8.4, -23.0, DECK + .15 + 1.6), target=(-1.5, 2.0, DECK + 4.5), lens=24, whole=False)
        elif c['name'] == 'front_corner':            # the locked oblique: high over the south-west quay, the span receding north-east
            c.update(location=(-15.0, -36.0, 24.0), target=(2.0, 4.0, 7.0), lens=30, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(40.0, -46.0, 40.0), target=(0.0, 0.0, 6.0), lens=30, whole=False)
        elif c['name'] == 'top':
            c.update(location=(0.0, 0.0, 100.0), target=(0.0, .001, 0.0), ortho_scale=68.0, whole=False)
        elif c['name'] == 'left_side':               # the west truss elevation from over the river
            c.update(location=(-46.0, -2.0, 9.0), target=(0.0, 0.0, 8.0), lens=35, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(46.0, 2.0, 9.0), target=(0.0, 0.0, 8.0), lens=35, whole=False)
        elif c['name'] == 'rear':                    # along the street from the north
            c.update(location=(1.0, 50.0, DECK + 2.5), target=(0.0, 0.0, DECK + 4.5), lens=35, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(32.0, 40.0, 24.0), target=(0.0, 0.0, 6.0), lens=35, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='urban_vehicular_bridge/variant_1 (Industrial Steel Truss)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=0, storey_programme='bridge: a two-lane street with sidewalks over a river; quays and warehouses are context',
            plan='34 m single-span through truss (top view) over a 29 m river between concrete quays, trusses 13 m apart, sidewalks outside them',
            section_m=dict(carriageway=[-6.2, 6.2], trusses=[-XT, XT], sidewalks=[[-XR, -XT - .3], [XT + .3, XR]], railings=[-XR, XR]),
            facade='two rust-red riveted Pratt trusses of seven panels with inclined end posts, laced verticals, gusset plates, latticed top struts and X laterals, latticed portals with knee braces',
            levels_m=[0.0, DECK, DECK + .15 + HT], inferred='the river bed, foundations and the warehouses are context; member sizes are teaching assumptions'),
        roof_contract=dict(type='open truss over the road; flat roofs on the context warehouses', datum_m=DECK, crowns_m=[h]),
        identity_contract=dict(owner='rust-red riveted through-truss with portal frames and overhead bracing over a two-lane road, outside sidewalks with rails, brick abutments'),
        material_contract=dict(profile='source-palette clay: rust-red steel with darker gussets, grey asphalt with yellow and white lines, pale concrete sidewalks and quays, red-brown brick, dark river water', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='two traffic lanes, two sidewalks'),
        street_contract=dict(kind='fixed_native_section', width_m=X1 - X0, axis='y', junction_finish='asphalt',
                             bands=['railing', 'sidewalk', 'truss', 'carriageway', 'truss', 'sidewalk', 'railing']),
        contact_contract=['River surface at grade zero', 'Abutments from the water at the quays', 'Trusses bearing on the abutments', 'Deck between and beside the trusses'],
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


# ---- Riveted steel through-truss road bridge ----

P = L / NP                                                                 # panel length
ZB = DECK + .15                                                            # bottom chord centre
ZT = ZB + HT                                                               # top chord centre
YN = [-L / 2 + i * P for i in range(NP + 1)]                               # panel points along y
BANK = 60.0
SW = .15                                                                   # sidewalk above the road


def node(x, i, top):
    return (x, YN[i], ZT if top else ZB)


def laced(b, a, c, w, d, n=None, role='steel'):
    """A built-up laced member from a to c: two flange bars d apart in the member's plane with zigzag lacing."""
    ax = [c[k] - a[k] for k in range(3)]
    Lm = math.sqrt(sum(v * v for v in ax))
    u = [v / Lm for v in ax]
    if abs(u[2]) > .95:                                                    # vertical member: flanges split along y
        off = (0.0, d / 2, 0.0)
    else:                                                                  # inclined or horizontal in the truss plane: split normal to it
        nrm = (0.0, -u[2], u[1]) if abs(u[0]) < .5 else (0.0, 0.0, 1.0)
        off = tuple(v * d / 2 for v in nrm)
    for s in (-1, 1):
        b.beam(role, tuple(a[k] + s * off[k] for k in range(3)), tuple(c[k] + s * off[k] for k in range(3)), w, .1)
    n = n or max(2, int(Lm / .45))
    for j in range(n):
        p0 = [a[k] + ax[k] * j / n - off[k] for k in range(3)]
        p1 = [a[k] + ax[k] * (j + 1) / n + off[k] for k in range(3)]
        if j % 2:
            p0 = [a[k] + ax[k] * j / n + off[k] for k in range(3)]
            p1 = [a[k] + ax[k] * (j + 1) / n - off[k] for k in range(3)]
        b.beam('steel2', tuple(p0), tuple(p1), w - .1, .045)


def truss(xt):
    """One Pratt truss: bottom chord, top chord, inclined end posts, laced verticals, double-bar diagonals with
    counters in the middle panel, gusset plates on both faces at every panel point."""
    b = Batch()
    b.beam('steel', (xt, YN[0] - .3, ZB), (xt, YN[-1] + .3, ZB), .5, .6)                     # bottom chord
    b.beam('steel', node(xt, 1, True), node(xt, NP - 1, True), .58, .62)                      # top chord
    for i0, i1 in ((0, 1), (NP, NP - 1)):                                                   # inclined end posts
        b.beam('steel', node(xt, i0, False), node(xt, i1, True), .62, .6, ext=.25)
    for i in range(1, NP):
        laced(b, (xt, YN[i], ZB + .3), (xt, YN[i], ZT - .31), .36, .34)
    mid = NP // 2
    for i in range(1, NP - 1):                                                            # Pratt diagonals: down towards mid-span
        if i < mid:
            pairs = [(node(xt, i, True), node(xt, i + 1, False))]
        elif i > mid:
            pairs = [(node(xt, i + 1, True), node(xt, i, False))]
        else:
            pairs = [(node(xt, i, True), node(xt, i + 1, False)), (node(xt, i + 1, True), node(xt, i, False))]
        for a, c in pairs:
            for s in (-1, 1):
                b.beam('steel', (a[0] + s * .12, a[1], a[2]), (c[0] + s * .12, c[1], c[2]), .07, .3)
    for i in range(NP + 1):                                                               # gusset plates and rivet rows
        for top in (False, True):
            if top and i in (0, NP):
                continue
            z = ZT if top else ZB
            for s in (-1, 1):
                b.box('gusset', xt + s * .335, YN[i], z + (-.1 if top else .25), .04, 1.15, 1.1)
                for r in range(3):
                    b.box('hardware', xt + s * .355, YN[i] - .4 + .4 * r, z + (-.1 if top else .25) + .35, .012, .06, .06)
    b.flush(f'truss {xt:+.0f}')


def bracing():
    """Latticed top struts with knee braces, X laterals in the top chord plane, latticed portals at both ends."""
    b = Batch()
    for i in range(1, NP):
        y = YN[i]
        for dz in (.24, -.24):
            b.beam('steel', (-XT, y, ZT + dz), (XT, y, ZT + dz), .26, .1)
        n = 24
        for j in range(n):
            x0, x1 = -XT + 2 * XT * j / n, -XT + 2 * XT * (j + 1) / n
            b.beam('steel2', (x0, y, ZT + (-.24 if j % 2 == 0 else .24)), (x1, y, ZT + (.24 if j % 2 == 0 else -.24)), .2, .04)
        if 1 < i < NP - 1:
            for s in (-1, 1):                                                              # knee braces at the verticals
                b.beam('steel', (s * XT, y, ZT - 1.7), (s * (XT - 1.7), y, ZT - .26), .18, .14)
    for i in range(1, NP - 1):                                                           # X laterals
        for s in (-1, 1):
            b.beam('steel2', (-XT * s, YN[i], ZT - .12), (XT * s, YN[i + 1], ZT - .12), .14, .12)
    for i0, i1 in ((0, 1), (NP, NP - 1)):                                                # portals in the end-post plane
        def at(x, t):
            return (x, YN[i0] + (YN[i1] - YN[i0]) * t, ZB + (ZT - ZB) * t)
        tl = .8
        for t in (tl, tl - .1):
            b.beam('steel', at(-XT, t), at(XT, t), .26, .14)
        n = 20
        for j in range(n):
            t0, t1 = (tl - .1, tl) if j % 2 == 0 else (tl, tl - .1)
            xa, xc = -XT + 2 * XT * j / n, -XT + 2 * XT * (j + 1) / n
            b.beam('steel2', at(xa, t0), at(xc, t1), .2, .04)
        for s in (-1, 1):
            b.beam('steel', at(s * XT, .5), at(s * (XT - 2.2), tl - .1), .2, .16)
            b.box('hardware', s * (XT - .9), at(0, tl - .05)[1], at(0, tl - .05)[2] + .12, .5, .02, .26)  # builder's plate
    b.flush('bracing')


def deck():
    """Concrete slab on floor beams and stringers between the quays; asphalt road between the trusses; raised
    sidewalks outside them with picket railings."""
    C.box('Deck slab', (0.0, 0.0, (4.35 + DECK - .04) / 2), (2 * XR + .2, 2 * QY, DECK - .04 - 4.35), 'concrete', 'deck', 0)
    C.box('Bridge road', (0.0, 0.0, DECK - .02), (12.4, 2 * QY, .04), 'asphalt', 'deck', 0)
    b = Batch()
    for i in range(NP + 1):
        if abs(YN[i]) < QY - .3:
            b.box('steel2', 0.0, YN[i], 3.95, 2 * XR - .4, .45, .8)                              # floor beams
    for x in (-4.5, -1.5, 1.5, 4.5, -XT, XT):
        b.box('steel2', x, 0.0, 4.12, .32, 2 * QY - .02, .46)                                      # stringers
    for s in (-1, 1):
        b.box('concrete', s * (XT + .3 + XR) / 2 + s * .06, 0.0, DECK - .04 + (SW + .04) / 2, XR - XT - .18, 2 * QY, SW + .04)   # sidewalk
        b.box('concrete', s * 6.31, 0.0, DECK - .04 + .1, .24, 2 * QY, .2)                         # kerb by the truss
    lines(b, -QY, QY)
    b.flush('deck')
    b = Batch()
    for s in (-1, 1):
        railing(b, s * XR, -(QY + .3), QY + .3)
    b.flush('railings')


def lines(b, y0, y1):
    for x in (-.11, .11):
        b.box('yellow', x, (y0 + y1) / 2, DECK + .003, .1, y1 - y0, .006)
    for x in (-5.6, 5.6):
        b.box('white', x, (y0 + y1) / 2, DECK + .003, .12, y1 - y0, .006)


def railing(b, x, y0, y1):
    """Rust-red steel railing along y at x: posts, top and bottom rails, pickets."""
    z0 = DECK + SW
    b.beam('steel', (x, y0, z0 + 1.08), (x, y1, z0 + 1.08), .1, .1)
    b.beam('steel', (x, y0, z0 + .12), (x, y1, z0 + .12), .08, .08)
    y = y0
    k = 0
    while y <= y1:
        if k % 14 == 0:
            b.box('steel', x, y, z0 + .55, .1, .1, 1.1)
        else:
            b.box('steel', x, y, z0 + .6, .03, .03, .9)
        y += .14
        k += 1


def quays_and_abutments():
    """Concrete quays with jointed faces and railings; red-brick abutments with concrete caps under the span."""
    C.box('River', (0.0, 0.0, .005), (2 * BANK, 2 * QY, .01), 'water', 'site', 0)
    for sy in (-1, 1):
        ya, yb = sorted((sy * QY, sy * BANK))
        ym = (ya + yb) / 2
        C.box(f'Bank {sy:+d}', (0.0, ym, (DECK - .04) / 2), (2 * BANK, yb - ya, DECK - .04), 'quay', 'site', 0)
        C.box(f'Bank road {sy:+d}', (0.0, ym, DECK - .02), (12.4, yb - ya, .04), 'asphalt', 'site', 0)
        b = Batch()
        for sx in (-1, 1):
            b.box('paving', sx * (6.2 + BANK) / 2, ym, DECK - .04 + (SW + .04) / 2, BANK - 6.2, yb - ya, SW + .04)
        lines(b, ya, yb)
        q = sy * QY
        for x in [-BANK + 1.5 + 3.0 * k for k in range(40)]:                                      # quay face joints
            if abs(x) > 10.6:
                b.box('joint', x, q - sy * .002, DECK / 2, .03, .008, DECK - .3)
        for z in (1.2, 2.4, 3.6):
            for sx in (-1, 1):
                b.box('joint', sx * (10.4 + BANK) / 2, q - sy * .002, z, BANK - 10.4, .008, .03)
        b.box('concrete', 0.0, q + sy * .25, DECK + SW / 2, 2 * BANK, .5, SW + .02)                 # quay edge kerb
        b.flush(f'bank {sy:+d}')
        b = Batch()
        for sx in (-1, 1):
            a0, a1 = sorted((sx * XR, sx * BANK))
            xr = sy * (QY + .3)
            b.beam('steel', (a0, xr, DECK + SW + 1.08), (a1, xr, DECK + SW + 1.08), .08, .1)
            b.beam('steel', (a0, xr, DECK + SW + .12), (a1, xr, DECK + SW + .12), .07, .07)
            x = a0
            k = 0
            while x <= a1:
                b.box('steel', x, xr, DECK + SW + .6, .03 if k % 14 else .1, .03 if k % 14 else .1, .9 if k % 14 else 1.1)
                x += .14
                k += 1
        b.flush(f'quay railing {sy:+d}')
        # Abutment: brick from the water to a concrete cap under the slab, standing 0.6 m forward of the quay face.
        yf = sy * (QY - .6)
        ya2, yb2 = sorted((yf, sy * (QY + .5)))
        C.box(f'Abutment {sy:+d}', (0.0, (ya2 + yb2) / 2, 2.0), (20.4, yb2 - ya2, 4.0), 'brick', 'abutments', 0)
        ya3, yb3 = sorted((sy * (QY - .7), sy * QY))
        C.box(f'Abutment cap {sy:+d}', (0.0, (ya3 + yb3) / 2, 4.185), (20.8, yb3 - ya3, .37), 'concrete', 'abutments', 0)
        b = Batch()
        for z in [.25 + .25 * k for k in range(15)]:
            b.box('joint', 0.0, yf - sy * .002, z, 20.38, .008, .02)
        for z in [.25 + .25 * k for k in range(15)]:
            x = -10.0 + (.3 if (z * 4) % 2 else 0.0)
            while x < 10.0:
                b.box('joint', x, yf - sy * .002, z + .125, .02, .008, .23)
                x += .6
        for sx in (-1, 1):                                                                       # bearing shoes under the end posts
            b.box('steel2', sx * XT, sy * (L / 2), DECK + .02, .9, 1.2, .2)
        b.flush(f'abutment {sy:+d} brickwork')


def warehouses():
    """Brick warehouses round the bridge as context: a face towards the river with real cuts, a body behind."""
    for name, x0, x1, ya, yb, h in (('NW warehouse', -52.0, -16.0, 22.0, 48.0, 16.0), ('NE warehouse', 16.0, 46.0, 24.0, 44.0, 11.5),
                                     ('SW warehouse', -48.0, -16.0, -48.0, -24.0, 18.5), ('SE warehouse', 16.0, 52.0, -50.0, -24.0, 13.0)):
        south = ya > 0
        yf = ya if south else yb
        if south:
            f = C.Face((0, yf, 0), (1, 0, 0), (0, 1, 0), name)
            lo, hi = x0, x1
        else:
            f = C.Face((0, yf, 0), (-1, 0, 0), (0, -1, 0), name)
            lo, hi = -x1, -x0
        top = DECK + SW + h
        nf = int((h - 1.5) / 3.6)
        hs = [hole(f'{name} window {k} {j}', lo + 2.0 + 3.2 * j, DECK + SW + 1.1 + 3.6 * k, 1.8, 2.2)
              for k in range(nf) for j in range(int((hi - lo - 2.5) / 3.2))]
        f.wall(f'{name} river face', lo, hi - EPS, DECK + SW, top, depth=T, role='wall', holes=hs)
        G.brick_courses(f, lo + .02, hi - .02, DECK + SW + .1, top - .1, hs, spacing=.5)
        m = Merge(f)
        for hh in hs:
            framed(m, f, hh, cols=3, rows=3, inset=.14, occupied='loft', frame='dark', lite=True)
            m.box('stone', hh['u'], -.05, hh['z'] - .06, hh['w'] + .2, .12, .12)
        m.box('stone', (lo + hi) / 2, -.06, top - .15, hi - lo + .1, .16, .3)
        m.flush(name)
        yb0, yb1 = (yf + T, yb) if south else (ya, yf - T)
        C.box(f'{name} body', ((x0 + x1) / 2, (yb0 + yb1) / 2, (DECK + SW + top) / 2), (x1 - x0, yb1 - yb0, top - DECK - SW), 'wall', 'context', 0)
        C.box(f'{name} roof', ((x0 + x1) / 2, (ya + yb) / 2, top + .05), (x1 - x0 - .2, yb - ya - .2, .1), 'roof', 'context', 0)
        C.qa_room_light(f'{name} rooms', ((x0 + x1) / 2, yf + (3.0 if south else -3.0), DECK + SW + 2.0), 60, 4.0)


def street():
    for sy in (-1, 1):
        for y in (30.0, 38.0, 46.0):
            for sx in (-1, 1):
                street_tree(sx * 8.6, sy * y, z=DECK + SW, height=7.5, spread=2.0)
    b = Batch()

    def car(x, y, role, ln=4.5):
        b.box(role, x, y, DECK + .7, 1.8, ln, .8)
        b.box('glass', x, y - .2, DECK + 1.4, 1.6, ln * .5, .6)
        for dy in (-ln / 2 + .8, ln / 2 - .8):
            for s in (-1, 1):
                b.box('dark', x + s * .75, y + dy, DECK + .35, .3, .8, .7)
    car(-3.0, -6.0, 'car')
    car(-3.0, 5.0, 'car2')
    car(3.0, 30.0, 'car')
    b.box('bus', -3.0, 26.0, DECK + 1.8, 2.5, 12.0, 2.9)                                         # a bus on the north approach
    for s in (-1, 1):
        b.box('glass', -3.0 + s * 1.26, 26.0, DECK + 2.3, .03, 11.0, 1.0)
    for dy in (-4.5, 4.5):
        for s in (-1, 1):
            b.box('dark', -3.0 + s * 1.0, 26.0 + dy, DECK + .4, .3, .9, .8)
    b.flush('traffic')


def build():
    quays_and_abutments()
    deck()
    truss(-XT)
    truss(XT)
    bracing()
    warehouses()
    street()
    C.CONTACTS.append(dict(name='Single-span through-truss bridge on brick abutments at the quays; deck between and beside the trusses', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(35, -45, 40), fill=(-40, -25, 30), rear=(-20, 40, 30), target=(0, 0, 7.0), gain=3.6)
