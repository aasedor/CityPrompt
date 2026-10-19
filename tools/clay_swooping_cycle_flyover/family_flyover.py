"""Swooping elevated cycle flyover, authored from the locked catalogue views of
dedicated_cycle_bridge / variant_0 (Elevated Swooping Flyover).

Read from the pixels (the top view governs the plan): a narrow ribbon of cycle deck swoops in an S over a city
street junction, running west to east in two broad bends, high enough to clear the traffic. The deck carries a dark
surface with a white dashed centre line between tall, solid-looking bright orange parapets of close vertical slats
under a flat orange handrail; its pale underside sits on slender concrete columns that split into a Y under the deck.
Beneath run a broad east-west road with a planted median and a north-south street, with footways, street trees and
planted beds; brick blocks stand on the four corners, a flat-roofed office with rooftop plant to the north-east,
pitched slate and orange-tiled roofs elsewhere. Both ends ramp down beyond the junction.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-swooping-cycle-flyover'
DZ = 6.2                                        # deck surface over the junction
DW = 6.2                                        # deck between the parapets (about 1.4 traffic lanes)
PH = 1.25                                       # parapet height above the surface
X0, X1, Y0, Y1 = -225.0, 225.0, -30.0, 16.0     # the ribbon's plan extent with its ramps and at-grade paths
ROAD_Y0, ROAD_Y1 = -17.0, 6.0                   # the east-west road
NS_X0, NS_X1 = -22.0, -8.0                      # the north-south street
T = .3
EPS = .002
PALETTE = dict(orange=(.80, .16, .045), deck=(.30, .30, .31), lane=(.94, .94, .92), under=(.74, .73, .70),
    concrete=(.72, .71, .68), asphalt=(.25, .25, .26), paving=(.60, .57, .54), kerb=(.70, .69, .66),
    grass=(.38, .48, .24), planting=(.30, .44, .20), tree=(.28, .44, .18), timber=(.42, .32, .22), soil=(.30, .25, .18),
    brick=(.52, .30, .22), brick2=(.60, .36, .26), roof=(.24, .24, .26), tile=(.70, .34, .20), trim=(.90, .89, .86),
    glass=(.24, .30, .34), dark=(.14, .15, .16), hardware=(.18, .18, .19), pale=(.88, .88, .86), white=(.93, .93, .91),
    interior=(.84, .80, .74), floor=(.58, .48, .38), stone=(.70, .68, .64), joint=(.52, .50, .47), sand=(.70, .66, .58),
    wall=(.80, .74, .62), blue=(.20, .30, .40), pot=(.60, .34, .22), red=(.62, .30, .26))


def manifest(version):
    h = 26.0
    cams = G.camera_roster(X1 - X0, 120.0, h, [
        ('facade_close', (4.0, -31.5, 2.4), (14.0, -21.0, 5.4), 40),
        ('architecture_close', (-2.0, -30.0, 9.5), (8.0, -14.0, 6.0), 40),
        ('glass_close', (22.0, -27.5, DZ + 1.6), (34.0, -25.0, DZ + .9), 40),
        ('y_column', (11.0, -30.5, 1.8), (15.5, -19.2, 4.0), 40),
        ('ramp_curve', (50.0, -31.0, 14.0), (14.0, -14.0, DZ), 32),
        ('parapet_panel', (-8.0, 8.0, DZ + 1.8), (-20.0, 14.0, DZ + .8), 40),
        ('deck_surface', (2.0, 1.0, DZ + 1.7), (-14.0, 13.0, DZ + .6), 34),
        ('street_under', (-15.0, -12.0, 1.7), (-15.0, 14.0, 5.5), 30),
        ('landing_ramp', (-197.0, -33.0, 2.4), (-168.0, -23.0, 2.0), 30),
        ('rear_north', (-15.0, 46.0, 18.0), (-6.0, 2.0, 6.0), 35)])
    for c in cams:                       # the locked front rides the east bend, looking west along the ribbon
        if c['name'] == 'front':
            c.update(location=(46.0, -22.0, DZ + 3.4), target=(-14.0, 12.0, DZ - .5), lens=24, whole=False)
        elif c['name'] == 'front_corner':                                      # the locked oblique, high from the south-east
            c.update(location=(-12.0, -60.0, 32.0), target=(4.0, -4.0, 4.0), lens=26, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(-40.0, -110.0, 80.0), target=(0.0, -4.0, 3.0), lens=30, whole=False)
        elif c['name'] == 'top':
            c.update(location=(0.0, -4.0, 160.0), target=(0.0, -3.999, 0.0), ortho_scale=200.0, whole=False)
        elif c['name'] == 'left_side':
            c.update(location=(-252.0, -4.0, 34.0), target=(-60.0, -8.0, 4.0), lens=35, whole=False)   # down the east-west road, clear of the blocks
        elif c['name'] == 'right_side':
            c.update(location=(252.0, -30.0, 30.0), target=(60.0, 0.0, 4.0), lens=35, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(-15.0, 95.0, 30.0), target=(-8.0, 0.0, 5.0), lens=30, whole=False)      # down the north-south street
        elif c['name'] == 'rear_side':
            c.update(location=(170.0, 46.0, 46.0), target=(0.0, -6.0, 4.0), lens=28, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='dedicated_cycle_bridge/variant_0 (Elevated Swooping Flyover)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=DZ + PH),
            observed_storeys=0, storey_programme='bridge: an elevated cycle ribbon swooping over a street junction',
            plan='an S-shaped ribbon about 160 m across the junction (top view) in two broad bends, then 100 m ramps at about 6% down to at-grade cycle paths at both ends',
            section_m=dict(deck_width=DW, deck_level=DZ, parapet_height=PH),
            facade='dark deck with a white dashed centre line, tall near-solid orange parapet screens with close slats on the inner face and a slim cap, pale underside, slender round tapered concrete Y-columns in the median and on the footways',
            levels_m=[0.0, DZ, DZ + PH], inferred='the ramps and at-grade paths beyond the junction (outside the sources) and the corner blocks are simplified context'),
        roof_contract=dict(type='open bridge deck; no roof', datum_m=DZ, crowns_m=[DZ + PH]),
        identity_contract=dict(owner='sinuous orange-parapeted cycle ribbon on Y-columns swooping in S-curves over a street junction'),
        material_contract=dict(profile='source-palette clay: bright orange parapets and handrail, dark deck with white marking, pale underside and concrete columns, dark asphalt, pale footways, planted medians, brick context', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='street junction, footways and planted medians', deck='cycling'),
        street_contract=dict(kind='fixed_native_section', width_m=DW, axis='ribbon', junction_finish='ramp',
                             bands=['parapet', 'cycle deck', 'parapet']),
        contact_contract=['Streets and plots at grade', 'Y-columns from grade', 'Deck on its columns', 'Ramps down to grade at both ends'],
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
# ---- Swooping cycle flyover ----

# Centre line (top view): the S over the junction, then long straight approaches that ramp down to at-grade cycle
# paths on the south footway (west) and the north footway (east).
CTRL = [(-270.0, -25.0), (-225.0, -25.0), (-180.0, -25.0), (-135.0, -23.5), (-100.0, -19.5), (-71.0, -11.0), (-48.0, 2.0),
        (-27.0, 12.0), (-11.0, 12.5), (0.0, 3.0), (13.0, -17.0), (29.0, -25.0), (48.0, -21.0), (63.0, -8.0), (80.0, 2.0),
        (98.0, 7.0), (120.0, 10.0), (150.0, 10.0), (185.0, 10.0), (225.0, 10.0), (270.0, 10.0)]
XA, XB = -78.0, 84.0                            # the deck is level at DZ between these x
LR = 100.0                                      # ramp length along the ribbon (about 6% average gradient)
ZF = .06                                        # path surface at grade
GX = 225.0                                      # half-length of the street scene
TREES = ((-60.0, -9.0), (-90.0, -9.0), (-130.0, -9.0), (30.0, -9.0), (100.0, -9.0), (140.0, -9.0), (-34.0, 9.5), (-56.0, 9.5),
         (8.0, 9.5), (-4.0, -22.0), (60.0, -24.0), (-26.0, -26.0), (-44.0, -27.0), (110.0, 14.0), (35.0, 9.5), (-120.0, 12.0))


def _centre(step=1.4):
    raw = []
    for i in range(1, len(CTRL) - 2):
        p0, p1, p2, p3 = CTRL[i - 1], CTRL[i], CTRL[i + 1], CTRL[i + 2]
        L = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
        n = max(2, int(L / step))
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            raw.append(tuple(.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                   + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in (0, 1)))
    raw.append(CTRL[-2])
    return [p for p in raw if abs(p[0]) <= GX - 2.0]


def path():
    """Centre line samples (x, y, z, left normal x, left normal y, arc length): level at DZ over the junction, ramping
    down over LR metres of ribbon at each end to the at-grade path, with 10 m vertical curves at the knees."""
    raw = _centre()
    s = [0.0]
    for i in range(1, len(raw)):
        s.append(s[-1] + math.hypot(raw[i][0] - raw[i - 1][0], raw[i][1] - raw[i - 1][1]))
    sa = next(s[i] for i, p in enumerate(raw) if p[0] >= XA)
    sb = next(s[i] for i in range(len(raw) - 1, -1, -1) if raw[i][0] <= XB)
    zr = [ZF + (DZ - ZF) * min(1.0, max(0.0, 1 - (sa - si) / LR if si < sa else 1 - (si - sb) / LR if si > sb else 1.0)) for si in s]
    z = []
    for i, si in enumerate(s):                                                # box filter = parabolic knees
        acc = [zr[j] for j in range(max(0, i - 12), min(len(s), i + 13)) if abs(s[j] - si) <= 5.0]
        z.append(sum(acc) / len(acc))
    out = []
    for i, (x, y) in enumerate(raw):
        a = raw[max(0, i - 1)]; b = raw[min(len(raw) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty); tx, ty = tx / L, ty / L
        out.append((x, y, max(ZF, z[i]), -ty, tx, s[i]))
    return out


def split(P):
    """The raised ribbon (from the last at-grade sample at the west foot to the first at the east foot) and the two
    at-grade path runs beyond the feet."""
    up = [i for i, p in enumerate(P) if p[2] > ZF + .004]
    i0, i1 = max(0, up[0] - 1), min(len(P) - 1, up[-1] + 1)
    return P[i0:i1 + 1], P[:i0 + 1], P[i1:]


def ribbon(name, P, lo, hi, z_lo, z_hi, role, module, floor=0.0):
    """Loft a rectangle across the ribbon from offset lo to hi (left normal) and from z+z_lo to z+z_hi, clamped
    at grade so no vertex goes below it."""
    rings = []
    for x, y, z, nx, ny, _ in P:
        zb = max(floor, z + z_lo); zt = max(zb + .02, z + z_hi)
        rings.append([(x + nx * lo, y + ny * lo, zb), (x + nx * hi, y + ny * hi, zb), (x + nx * hi, y + ny * hi, zt), (x + nx * lo, y + ny * lo, zt)])
    loft(name, rings, role, module, closed=False)


def resample(P, d):
    """Points every d metres of arc length along P, linearly interpolated."""
    out, j = [], 0
    s = P[0][5]
    while s <= P[-1][5]:
        while P[j + 1][5] < s:
            j += 1
        a, b = P[j], P[j + 1]
        t = (s - a[5]) / max(1e-6, b[5] - a[5])
        out.append(tuple(a[k] + (b[k] - a[k]) * t for k in range(6)))
        s += d
    return out


def free_ground(x, y):
    """A column foot may stand in the planted median or on a footway, never in a traffic lane, the north-south
    street or a crossing, nor on a street tree."""
    if any(math.hypot(x - tx, y - ty) < 2.6 for tx, ty in TREES):
        return False
    median = -10.1 < y < -7.9 and (x < -41.0 or x > -3.0)
    foot = (ROAD_Y1 + .9 < y < 16.5 or -32.5 < y < ROAD_Y0 - .9) and not (NS_X0 - 1.2 < x < NS_X1 + 1.2)
    return median or foot


def columns():
    """Column stations: (foot x, foot y, deck z, centre x, centre y, normal x, normal y, foot offset). Greedy along
    the ribbon, 14-34 m apart, each foot on free ground somewhere under the deck."""
    P, _, _ = split(path())
    h = DW / 2
    out, last = [], -1e9
    for x, y, z, nx, ny, s in resample(P, 1.0):
        if z < 1.3 or s - last < 14.0:
            continue
        for o in sorted([(-h + .8) + k * (DW - 1.6) / 10 for k in range(11)], key=abs):
            fx, fy = x + nx * o, y + ny * o
            if free_ground(fx, fy):
                out.append((fx, fy, z, x, y, nx, ny, o)); last = s
                break
    return out


def tapered(V, F, p0, p1, r0, r1, segs=20):
    """A round tapered rod from p0 (radius r0) to p1 (radius r1), capped, appended to one mesh."""
    ax = [p1[i] - p0[i] for i in range(3)]
    L = math.sqrt(sum(v * v for v in ax)); ax = [v / L for v in ax]
    ref = (0.0, 0.0, 1.0) if abs(ax[2]) < .95 else (1.0, 0.0, 0.0)
    u = (ax[1] * ref[2] - ax[2] * ref[1], ax[2] * ref[0] - ax[0] * ref[2], ax[0] * ref[1] - ax[1] * ref[0])
    n = math.sqrt(sum(v * v for v in u)); u = [v / n for v in u]
    w = (ax[1] * u[2] - ax[2] * u[1], ax[2] * u[0] - ax[0] * u[2], ax[0] * u[1] - ax[1] * u[0])
    o = len(V)
    for p, r in ((p0, r0), (p1, r1)):
        for k in range(segs):
            a = 2 * math.pi * k / segs
            V.append(tuple(p[i] + r * (math.cos(a) * u[i] + math.sin(a) * w[i]) for i in range(3)))
    for k in range(segs):
        k2 = (k + 1) % segs
        F.append((o + k, o + k2, o + segs + k2, o + segs + k))
    F.append(tuple(o + k for k in range(segs - 1, -1, -1))); F.append(tuple(o + segs + k for k in range(segs)))


def bar_screen(V, F, P, c, s, z0, z1, sp=.16, w=.045, d=.03):
    """Close vertical orange bars centred at offset c (left normal) between z0 and z1: each bar a front and a back
    face (its ends sink into the bottom rail and the cap, so no top or bottom face shows), with open gaps between."""
    for x, y, z, nx, ny, _ in resample(P, sp)[1:-1]:
        tx, ty = ny, -nx
        for o in (c + s * d, c - s * d):
            k = len(V)
            V += [(x + nx * o - tx * w, y + ny * o - ty * w, z + z0), (x + nx * o + tx * w, y + ny * o + ty * w, z + z0),
                  (x + nx * o + tx * w, y + ny * o + ty * w, z + z1), (x + nx * o - tx * w, y + ny * o - ty * w, z + z1)]
            F.append((k, k + 1, k + 2, k + 3))


def round_rail(name, P, c, hw, zc, hh, role='orange', module='parapets', n=10):
    """A smooth rounded top rail: an elliptical section (half-width hw, half-height hh) centred at offset c and
    zc above the deck, lofted along P with smooth shading so the curve shows no chord facets."""
    rings = []
    for x, y, z, nx, ny, _ in P:
        rings.append([(x + nx * (c + hw * math.cos(2 * math.pi * k / n)), y + ny * (c + hw * math.cos(2 * math.pi * k / n)),
                       z + zc + hh * math.sin(2 * math.pi * k / n)) for k in range(n)])
    obj = loft(name, rings, role, module, closed=False)
    for f in obj.data.polygons[:-2]:
        f.use_smooth = True


def flat_quads(name, quads, role, module):
    """Road and deck markings as single top faces (no hidden sides)."""
    V, F = [], []
    for q in quads:
        k = len(V); V += list(q); F.append((k, k + 1, k + 2, k + 3))
    if F:
        C.mesh(name, V, F, role, module)


def rect(cx, cy, z, sx, sy):
    return [(cx - sx / 2, cy - sy / 2, z), (cx + sx / 2, cy - sy / 2, z), (cx + sx / 2, cy + sy / 2, z), (cx - sx / 2, cy + sy / 2, z)]


def flyover():
    P, west, east = split(path())
    h = DW / 2
    ribbon('Deck girder', P, -h - .07, h + .07, -.80, -.04, 'under', 'deck')
    ribbon('Deck surface', P, -h - .06, h + .06, -.08, 0.0, 'deck', 'deck')
    # Each edge: a smooth orange fascia band wrapping the deck edge (its foot above the pale soffit), a reveal, then
    # a screen of close vertical orange bars between a bottom rail and a rounded top rail.
    BV, BF = [], []
    for s, nm in ((-1, 'south'), (1, 'north')):
        lo, hi = sorted((s * (h + .05), s * (h + .19)))
        ribbon(f'Fascia {nm}', P, lo, hi, -.66, -.06, 'orange', 'parapets')
        lo, hi = sorted((s * h, s * (h + .14)))
        ribbon(f'Parapet bottom rail {nm}', P, lo, hi, -.05, .12, 'orange', 'parapets')
        bar_screen(BV, BF, P, s * (h + .07), s, .08, PH - .06)
        round_rail(f'Parapet top rail {nm}', P, s * (h + .07), .095, PH - .05, .05)
    C.mesh('Parapet bars', BV, BF, 'orange', 'parapets')
    # Dashed white centre line on the deck and on the at-grade paths: 2 m dashes every 5 m.
    quads = []
    for run in (P, west, east):
        if len(run) < 2:
            continue
        pts = resample(run, 1.0)
        for i in range(0, len(pts) - 2, 5):
            a, c = pts[i], pts[i + 2]
            quads.append([(a[0] - a[3] * .07, a[1] - a[4] * .07, a[2] + .006), (c[0] - c[3] * .07, c[1] - c[4] * .07, c[2] + .006),
                          (c[0] + c[3] * .07, c[1] + c[4] * .07, c[2] + .006), (a[0] + a[3] * .07, a[1] + a[4] * .07, a[2] + .006)])
    flat_quads('Centre line', quads, 'lane', 'deck')
    # At-grade cycle paths beyond the ramp feet, with low kerbs.
    for nm, run in (('west', west), ('east', east)):
        if len(run) < 2:
            continue
        ribbon(f'Cycle path {nm}', run, -h - .06, h + .06, -.04, 0.0, 'deck', 'deck', floor=.0)
        for s in (-1, 1):
            lo, hi = sorted((s * (h + .06), s * (h + .3)))
            ribbon(f'Cycle path kerb {nm} {s:+d}', run, lo, hi, -.04, .06, 'kerb', 'deck', floor=.0)
    # Slender round Y-columns: a tapered shaft splitting into two tapered arms seated in the soffit; short round posts
    # where the ramp is low. Every foot stands in the median or on a footway.
    V, F = [], []
    for fx, fy, z, x, y, nx, ny, o in columns():
        soffit = z - .80
        if soffit < 2.4:
            tapered(V, F, (fx, fy, 0.0), (fx, fy, soffit + .08), .34, .26)
            continue
        zf = soffit - min(2.3, .45 * soffit)
        tapered(V, F, (fx, fy, 0.0), (fx, fy, zf + .25), .42, .31)
        for side in (-1, 1):
            oa = max(-DW / 2 + .9, min(DW / 2 - .9, o + side * 1.7))
            p0, p1 = (fx, fy, zf), (x + nx * oa, y + ny * oa, soffit + .1)
            at = lambda zz: tuple(p0[i] + (p1[i] - p0[i]) * (zz - p0[2]) / (p1[2] - p0[2]) for i in range(3))
            tapered(V, F, p0, at(soffit + .45), .26, .35)                   # sunk well into the deck: no rim below the soffit
            ra = .26 + (.35 - .26) * (soffit - .55 - p0[2]) / (soffit + .45 - p0[2])
            dx, dy, dz = (p1[i] - p0[i] for i in range(3))
            sn = math.hypot(dx, dy) / math.sqrt(dx * dx + dy * dy + dz * dz)      # tilt of the arm from vertical
            rb = min(.5, .34 / max(sn, .01))
            tapered(V, F, at(soffit - .55), at(soffit + .06 + rb * sn), ra - .01, rb)  # flared head; its top face wholly inside the deck
    obj = C.mesh('Y-columns', V, F, 'concrete', 'columns')
    for f in obj.data.polygons:
        f.use_smooth = len(f.vertices) == 4


def streets():
    C.box('Ground', (0.0, -8.0, .01), (2 * GX, 220.0, .02), 'paving', 'site', 0)
    C.box('East-west road', (0.0, (ROAD_Y0 + ROAD_Y1) / 2, .02), (2 * GX, ROAD_Y1 - ROAD_Y0, .04), 'asphalt', 'site', 0)
    for y0, y1 in ((ROAD_Y1, 110.0), (-120.0, ROAD_Y0)):
        C.box(f'North-south street {y0:+.0f}', ((NS_X0 + NS_X1) / 2, (y0 + y1) / 2, .02), (NS_X1 - NS_X0, y1 - y0, .04), 'asphalt', 'site', 0)
    b = Batch()
    for x0, x1 in ((-GX, -40.0), (-4.0, GX)):                                 # planted median beds on the east-west road
        b.box('kerb', (x0 + x1) / 2, -9.0, .08, x1 - x0, 2.6, .16)
        b.box('planting', (x0 + x1) / 2, -9.0, .22, x1 - x0 - .3, 2.2, .14)
    for x0, x1 in ((-36.0, -26.0), (40.0, 58.0), (118.0, 134.0)):              # low shrub masses on the median under the ribbon
        for k in range(int((x1 - x0) / 2.2)):
            b.box('tree', x0 + 1.1 + k * 2.2, -9.0 + (.25 if k % 2 else -.25), .55, 1.8, 1.5, .7)
    b.flush('road beds')
    marks = []
    for k in range(-70, 71):                                                  # lane lines, as flat top faces
        x = k * 3.2
        if not (NS_X0 - 1 < x < NS_X1 + 1) and abs(x) < GX - 1:
            for y in (-13.0, -4.0, 1.5):
                marks.append(rect(x, y, .046, 1.6, .14))
    for k in range(-34, 35):
        y = k * 3.2
        if (y > ROAD_Y1 + 1 or y < ROAD_Y0 - 1) and abs(y - (ROAD_Y1 + 2.6)) > 2.6 and abs(y - (ROAD_Y0 - 2.6)) > 2.6:
            marks.append(rect((NS_X0 + NS_X1) / 2, y, .046, .14, 1.6))         # stopping clear of the crossings
    for i in range(7):                                                        # zebra crossings
        marks.append(rect(NS_X0 + 1.5 + i * 1.8, ROAD_Y1 + 2.6, .046, .8, 3.0))
        marks.append(rect(NS_X0 + 1.5 + i * 1.8, ROAD_Y0 - 2.6, .046, .8, 3.0))
    for i in range(10):
        marks.append(rect(72.0, ROAD_Y0 + 1.4 + i * 2.2, .046, 3.0, .9))
    flat_quads('Road markings', marks, 'lane', 'site')
    P = path()
    for x, y in TREES:                                                        # no street tree grows through the ribbon
        if all(math.hypot(x - p[0], y - p[1]) > DW / 2 + 3.0 for p in P):
            street_tree(x, y, z=.04, height=9.0, spread=2.4)


def context():
    """Brick blocks on the four corners with proud-framed windows and sills; roofs read from the top view."""
    def windows(b, face, axis, lo, hi, floors, sign, w=1.3, hh=1.6, pitch=3.2, big=False, frames=None):
        n = int((hi - lo) / pitch)
        for k in range(floors):
            for j in range(n):
                u = lo + pitch / 2 + j * pitch
                z = 1.0 + k * 3.4
                ww, wh = (w * 1.5, hh * 1.4) if big else (w, hh)
                fw, fh, fp = (ww + .24) / 2, (wh + .24) / 2, face + sign * .06       # the proud frame's face (its sides never read)
                if axis == 'y':                                                  # a proud frame, the pane standing forward of it, a sill
                    frames.append([(u - fw, fp, z + wh / 2 - fh), (u + fw, fp, z + wh / 2 - fh), (u + fw, fp, z + wh / 2 + fh), (u - fw, fp, z + wh / 2 + fh)])
                    b.box('glass' if big else 'dark', u, face + sign * .07, z + wh / 2, ww, .04, wh)
                    b.box('trim', u, face + sign * .1, z - .1, ww + .34, .2, .1)
                else:
                    frames.append([(fp, u - fw, z + wh / 2 - fh), (fp, u + fw, z + wh / 2 - fh), (fp, u + fw, z + wh / 2 + fh), (fp, u - fw, z + wh / 2 + fh)])
                    b.box('glass' if big else 'dark', face + sign * .07, u, z + wh / 2, .04, ww, wh)
                    b.box('trim', face + sign * .1, u, z - .1, .2, ww + .34, .1)
    blocks = (('Office north-east', 2.0, 72.0, 18.0, 78.0, 24.0, 'brick', 'flat', True),
              ('Block north-west', -100.0, -30.0, 18.0, 70.0, 20.0, 'brick2', 'slate', False),
              ('Block south-east', 2.0, 86.0, -96.0, -34.0, 15.0, 'brick2', 'tile', False),
              ('Block south-west', -100.0, -30.0, -96.0, -34.0, 17.0, 'brick', 'flat', False))
    for name, x0, x1, y0, y1, h, role, roof, big in blocks:
        C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), role, 'context', 0)
        if roof == 'flat':
            C.box(f'{name} coping', ((x0 + x1) / 2, (y0 + y1) / 2, h + .08), (x1 - x0 + .2, y1 - y0 + .2, .16), 'trim', 'context', 0)
            b = Batch()
            for i, (dx, dy, sx, sy, sz) in enumerate(((.3, .5, 8.0, 6.0, 2.6), (.6, .4, 10.0, 5.0, 2.0), (.45, .7, 5.0, 5.0, 3.0))):
                b.box('pale', x0 + (x1 - x0) * dx, y0 + (y1 - y0) * dy, h + .16 + sz / 2, sx, sy, sz)
            b.flush(f'{name} roof plant')
        else:
            pitched_roof(f'{name} roof', x0, x1, y0, y1, h, 6.5, hip_w=True, hip_e=True, axis='x', ov=.3,
                         role='roof' if roof == 'slate' else 'tile', module='context')
        b, frames = Batch(), []
        floors = int((h - 1.5) / 3.4)
        face = y0 if y0 > 0 else y1
        windows(b, face, 'y', x0, x1, floors, -1 if y0 > 0 else 1, big=big, frames=frames)
        xf = x0 if x0 > 0 else x1                                             # the face towards the north-south street
        windows(b, xf, 'x', y0, y1, floors, -1 if x0 > 0 else 1, big=big, frames=frames)
        b.flush(f'{name} windows')
        flat_quads(f'{name} window frames', frames, 'trim', 'context')


def build():
    streets()
    context()
    flyover()
    C.CONTACTS.append(dict(name='Elevated cycle ribbon on Y-columns over a street junction, ramping to grade at both ends', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(50, -60, 60), fill=(-60, -30, 40), rear=(-30, 60, 40), target=(0, -4, 4.0), gain=4.0)
