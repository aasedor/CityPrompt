"""Weathering-steel footbridge, authored from the locked catalogue views of
urban_pedestrian_footbridge / variant_0 (Weathering Steel Truss).

Read from the pixels (the top view governs the plan): a rust-orange Cor-Ten Warren-truss footbridge in two straight
arms mitred into one sharp V (included angle about 92 degrees), its apex at the north beside the corner of a
pale-roofed brick building on the west sidewalk of a wide city street. The crossing arm leaves the apex about 70
degrees to the street axis to a landing on the far side; the land arm runs about 22 degrees off the street axis,
south-south-west along the kerb. Each arm is a pair of Warren trusses with bold diagonals and a deep fascia bottom
chord; the chords of both arms run to one outer and one inner corner node. Overhead, one transverse tie and one
diagonal per bay zig-zag along each arm, with members radiating from the outer apex node. The deck is rust-brown
plate; a fine diamond stainless cable net hangs from slim posts and a dark handrail inside both trusses. The arms land
on brick stair towers and one steel pier carries the outer apex node. Red-brick warehouses, a glazed office block,
street trees, a bus and cars as context.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-weathering-steel-footbridge'
X0, X1, Y0, Y1 = -30.0, 23.0, -32.0, 10.0      # the two arms, the apex and the two towers
RX = 9.0                                        # half-width of the carriageway (four lanes)
SW = 5.0                                        # sidewalks
ZD = 7.0                                        # deck top
HT = 3.4                                        # truss height to the top chord centre line
HW = 2.0                                        # truss centre lines either side of the deck axis
APEX = (-11.5, 4.0)
AA, AB = math.radians(70.0), math.radians(22.0)     # crossing arm 70 degrees to the street axis, land arm 22 degrees off it
QA = (APEX[0] + 30.0 * math.sin(AA), APEX[1] - 30.0 * math.cos(AA))      # east landing (across the street)
QB = (APEX[0] - 32.0 * math.sin(AB), APEX[1] - 32.0 * math.cos(AB))      # south-west landing
T = .3
EPS = .002
PALETTE = dict(rust=(.62, .27, .10), deck=(.42, .22, .12), mesh=(.70, .70, .68), hardware=(.30, .30, .31),
    brick=(.55, .28, .20), wall=(.55, .28, .20), trim=(.80, .78, .74), glass=(.34, .44, .48), pale=(.80, .79, .76),
    concrete=(.70, .69, .66), asphalt=(.24, .24, .25), sand=(.62, .60, .56), white=(.95, .95, .93), yellow=(.86, .70, .20),
    planting=(.30, .44, .20), tree=(.28, .44, .18), timber=(.42, .30, .20), soil=(.30, .25, .18), interior=(.84, .80, .74),
    floor=(.58, .48, .38), stone=(.62, .60, .56), joint=(.50, .49, .47), roof=(.40, .39, .38), blue=(.20, .30, .40),
    red=(.62, .14, .12), dark=(.12, .12, .13), pot=(.60, .34, .22))


def unit(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    return dx / L, dy / L, L


UA = unit(APEX, QA)
UB = unit(APEX, QB)
BIS = ((UA[0] + UB[0]) / math.hypot(UA[0] + UB[0], UA[1] + UB[1]), (UA[1] + UB[1]) / math.hypot(UA[0] + UB[0], UA[1] + UB[1]))   # into the V
TANH = math.tan(math.acos(UA[0] * UB[0] + UA[1] * UB[1]) / 2)        # tangent of the half included angle


def along(p, u, s, v=0.0, z=0.0):
    """Point at distance s along unit u from p, offset v to the left of u, at height z."""
    return (p[0] + u[0] * s - u[1] * v, p[1] + u[1] * s + u[0] * v, z)


def manifest(version):
    h = ZD + HT + 4.4
    a, ua = APEX, UA
    cams = G.camera_roster(X1 - X0, Y1 - Y0, h, [
        ('facade_close', along(a, ua, 14.0, 9.0, 1.7), along(a, ua, 17.0, 0.0, ZD + 1.2), 35),
        ('architecture_close', (APEX[0] + BIS[0] * 12.0, APEX[1] + BIS[1] * 12.0, ZD + 2.0), (APEX[0], APEX[1], ZD + 1.5), 35),
        ('glass_close', along(a, ua, 12.0, -1.0, ZD + 1.5), along(a, ua, 14.0, 1.8, ZD + .8), 35),
        ('truss_node', along(a, ua, 8.0, 6.0, ZD + 4.6), along(a, ua, 10.0, 2.0, ZD + 3.0), 40),
        ('mesh_infill', along(a, ua, 20.0, -1.0, ZD + 1.5), along(a, ua, 22.0, 1.75, ZD + .7), 35),
        ('deck_walk', along(a, ua, 4.5, 0.0, ZD + 1.6), along(a, ua, 30.0, 0.0, ZD + 1.2), 28),
        ('landing_stair', along(QA, ua, -7.0, 5.0, ZD + 1.0), (QA[0], QA[1], ZD + .5), 35),
        ('road_under', (2.0, -18.0, 1.6), (2.0, -1.0, ZD), 28),
        ('top_chord', along(a, ua, 15.0, 3.0, ZD + 9.0), along(a, ua, 18.0, 0.0, ZD + HT), 35),
        ('rear_north', (-2.0, 22.0, 15.0), (-6.0, -4.0, ZD), 32)])
    for c in cams:
        if c['name'] == 'front':                                              # the locked front: from inside the V, square to the east span
            c.update(location=along(a, ua, 14.0, -10.0, ZD + 2.4), target=along(a, ua, 19.0, 0.0, ZD + 1.6), lens=24, whole=False)
        elif c['name'] == 'front_corner':                                     # the locked oblique: high in the south, the apex beyond
            c.update(location=(-12.0, -40.0, 26.0), target=(-8.0, -4.0, ZD), lens=32, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(30.0, -40.0, 34.0), target=(-4.0, -6.0, ZD), lens=32, whole=False)
        elif c['name'] == 'top':
            c.update(location=(-3.0, -10.0, 90.0), target=(-3.0, -9.999, 0.0), ortho_scale=60.0, whole=False)
        elif c['name'] == 'left_side':
            c.update(location=(-72.0, -4.0, 40.0), target=(-4.0, -8.0, ZD), lens=30, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(50.0, -22.0, 22.0), target=(-4.0, -6.0, ZD), lens=30, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(4.0, 40.0, 30.0), target=(-6.0, -8.0, ZD), lens=30, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(-24.0, 40.0, 40.0), target=(-6.0, -6.0, ZD), lens=30, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='urban_pedestrian_footbridge/variant_0 (Weathering Steel Truss)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=0, storey_programme='street option: a two-span truss footbridge over a city street; the blocks are context',
            plan='two straight Warren-truss arms of about 30 and 32 m mitred into one sharp V (included angle about 92 degrees, apex north, top view); the crossing arm is about 70 degrees to the 28 m street, the land arm about 22 degrees off it along the west kerb',
            section_m=dict(carriageway=[-RX, RX], sidewalks=SW, deck_top=ZD, truss_height=HT, truss_lines=[-HW, HW]),
            facade='rust-orange Cor-Ten Warren trusses with bold diagonals, top chords with cross ties and bracing, deep fascia bottom chords, zig-zag top bracing radiating from the apex node, rust-brown plate deck, fine diamond stainless cable net on slim posts with a dark handrail, brick stair towers, one steel pier under the outer apex node',
            levels_m=[0.0, ZD, ZD + HT], inferred='the tower interiors, the far streets and the blocks are context'),
        roof_contract=dict(type='open truss, no roof; flat roofs on the towers and blocks', datum_m=ZD, crowns_m=[ZD + HT + .3]),
        identity_contract=dict(owner='rust-orange Cor-Ten Warren truss footbridge with mesh infill over a road between brick buildings'),
        material_contract=dict(profile='source-palette clay: rust-orange weathering steel, rust-brown deck, grey mesh, red brick, pale roofs, glass office, dark asphalt with white and yellow lines', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='a footbridge over the street; the street, sidewalks and towers beneath'),
        street_contract=dict(kind='fixed_native_section', width_m=2 * (RX + SW), axis='y', junction_finish='concrete',
                             bands=['sidewalk', 'carriageway', 'sidewalk']),
        contact_contract=['Street and sidewalks at grade', 'Arms on the towers and the apex pier', 'Towers and pier from grade'],
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
# ---- Weathering-steel truss footbridge ----

ZB = ZD - .25                                   # deep fascia bottom chord centre (ZD - .56 to ZD + .06)
ARMS = {}


def inner_sign(u):
    """+1 when the left of u faces into the V, else -1."""
    return 1.0 if (-u[1]) * BIS[0] + u[0] * BIS[1] > 0 else -1.0


def corner(m, z=0.0):
    """The mitre point of the two lines offset m into the V (m < 0: outside the V) at height z; it lies on the bisector."""
    k = m / math.sin(math.atan(TANH))
    return (APEX[0] + BIS[0] * k, APEX[1] + BIS[1] * k, z)


def arm(u, Q):
    """Panel geometry of one arm: the inner truss line starts at the inner corner node, the outer one at the outer
    node; whole Warren panels run from the inner node to the tower face, so every bay closes on a node."""
    L = math.hypot(Q[0] - APEX[0], Q[1] - APEX[1])
    s0 = HW / TANH
    n = max(4, round((L - s0) / 3.6))
    pl = (L - s0) / n
    return dict(u=u, L=L, s0=s0, n=n, pl=pl, sg=inner_sign(u),
                bot=[s0 + k * pl for k in range(n + 1)], top=[s0 + (k + .5) * pl for k in range(n)])


def ribbon(vs, fs, p, q, w):
    """Flat strand from p to q, w wide, in the vertical plane of the strand's truss line."""
    dz = q[2] - p[2]
    dh = math.hypot(q[0] - p[0], q[1] - p[1])
    L = math.hypot(dh, dz) or 1.0
    hx, hy = ((q[0] - p[0]) / dh, (q[1] - p[1]) / dh) if dh > 1e-9 else (0.0, 0.0)
    ou, oz = -dz / L * w / 2, dh / L * w / 2                                   # in-plane normal to the strand
    o = len(vs)
    vs += [(p[0] - hx * ou, p[1] - hy * ou, p[2] - oz), (q[0] - hx * ou, q[1] - hy * ou, q[2] - oz),
           (q[0] + hx * ou, q[1] + hy * ou, q[2] + oz), (p[0] + hx * ou, p[1] + hy * ou, p[2] + oz)]
    fs.append((o, o + 1, o + 2, o + 3))


def cable_net(vs, fs, u, v, sa, sb, z0, z1, cell=.08, w=.007):
    """Fine diamond-weave stainless cable net between sa and sb along the truss line at offset v."""
    h = z1 - z0
    for sgn in (1, -1):
        c = sa - h if sgn > 0 else sa
        cend = sb if sgn > 0 else sb + h
        while c <= cend:
            # strand: s = c + sgn * t, z = z0 + t, clipped to sa <= s <= sb, 0 <= t <= h
            t0, t1 = 0.0, h
            if sgn > 0:
                t0, t1 = max(t0, sa - c), min(t1, sb - c)
            else:
                t0, t1 = max(t0, c - sb), min(t1, c - sa)
            if t1 - t0 > .02:
                ribbon(vs, fs, along(APEX, u, c + sgn * t0, v, z0 + t0), along(APEX, u, c + sgn * t1, v, z0 + t1), w)
            c += cell


def span(name, u, Q):
    """One straight arm: two Warren trusses with deep fascia bottom chords, overhead ties with one diagonal per bay,
    floor beams, deck plate, diamond cable net on slim posts and a handrail inside both trusses."""
    g = arm(u, Q)
    ARMS[name] = g
    L, s0, n, sg, bot, top = g['L'], g['s0'], g['n'], g['sg'], g['bot'], g['top']
    P = lambda s, v, z: along(APEX, u, s, v, z)
    b = Batch()
    zt = ZD + HT
    for inner in (True, False):
        v = sg * HW if inner else -sg * HW
        ss = s0 if inner else -s0                                            # the line starts on its corner node
        b.beam('rust', P(ss, v, ZB), P(L + .15, v, ZB), .3, .62)                                   # deep fascia bottom chord, seated in the tower
        b.beam('rust', P(ss, v, zt), P(L, v, zt), .4, .42)                                         # top chord to the corner node
        b.beam('rust', P(L, v, ZB - .25), P(L, v, zt + .2), .38, .38)                               # end post at the tower
        for k in range(n):                                                                         # Warren diagonals
            b.beam('rust', P(bot[k], v, ZD + .05), P(top[k], v, zt - .1), .3, .3)
            b.beam('rust', P(top[k], v, zt - .1), P(bot[k + 1], v, ZD + .05), .3, .3)
        if not inner:                                                                              # the outer corner panel
            b.beam('rust', P(-s0, v, zt - .1), P(bot[0], v, ZD + .05), .3, .3)
        out = 1.0 if v > 0 else -1.0                                                               # bolt-hole row on the fascia
        k = int((L - ss) / .45)
        for j in range(1, k):
            s = ss + j * .45
            b.beam('hardware', P(s, v + out * .14, ZB - .12), P(s, v + out * .17, ZB - .12), .07, .07)
    for s in top + [L]:                                                                            # overhead transverse ties
        b.beam('rust', P(s, -HW, zt), P(s, HW, zt), .26, .3)
    ties = top + [L]
    for k in range(len(ties) - 1):                                                                 # one diagonal per bay, zig-zag
        va, vb = (sg * HW, -sg * HW) if k % 2 == 0 else (-sg * HW, sg * HW)
        b.beam('rust', P(ties[k], va, zt + .03), P(ties[k + 1], vb, zt + .03), .16, .16)
    for s in bot:                                                                                  # floor beams under the deck
        b.beam('rust', P(s, -HW, ZD - .32), P(s, HW, ZD - .32), .24, .3)
    b.flush(name)
    # Deck plate, mitred into the V: one quad per arm meeting the other on the bisector.
    m = HW - .1
    sm = m / TANH
    poly = [P(-sm, -sg * m, 0)[:2], P(L, -sg * m, 0)[:2], P(L, sg * m, 0)[:2], P(sm, sg * m, 0)[:2]]
    area = sum(poly[i][0] * poly[(i + 1) % 4][1] - poly[(i + 1) % 4][0] * poly[i][1] for i in range(4))
    C.prism(f'{name} deck', poly if area > 0 else poly[::-1], 'z', ZD - .1, ZD, 'deck', 'deck')
    b = Batch()
    for s in bot[1:-1]:                                                                            # plate joints at the panel points
        b.beam('joint', P(s, -m + .02, ZD + .002), P(s, m - .02, ZD + .002), .02, .004)
    b.flush(f'{name} deck joints')
    # Cable net, slim posts, a bottom cable and the dark handrail, inside both trusses.
    vs, fs = [], []
    b = Batch()
    for inner in (True, False):
        mi = (HW - .3) if inner else -(HW - .3)
        vi = sg * mi
        sa = mi / TANH
        cable_net(vs, fs, u, vi, sa, L, ZD + .06, ZD + 1.36)
        b.beam('mesh', P(sa, vi, ZD + .06), P(L, vi, ZD + .06), .02, .02)
        npst = max(2, round((L - sa) / 1.6))
        for j in range(1, npst + 1):
            s = sa + (L - sa) * j / npst
            b.beam('mesh', P(s, vi, ZD), P(s, vi, ZD + 1.4), .04, .04)
        b.beam('hardware', P(sa, vi, ZD + 1.42), P(L, vi, ZD + 1.42), .06, .06)
    C.mesh(f'{name} cable net', vs, fs, 'mesh', 'mesh')
    b.flush(f'{name} rails')


def apex():
    """The bend: the chords of both arms meet on one outer and one inner corner node. The outer node carries a corner
    post that runs down to grade as the single steel pier. Overhead, as in the sources, a collar tie crosses the corner
    between the first top-chord node of each outer truss, and two struts rise from the inner corner node to those same
    nodes: a triangle with a crossbar, with no members fanning from the outer apex."""
    zt = ZD + HT
    po, pi = corner(-HW), corner(HW)
    b = Batch()
    b.box('rust', po[0], po[1], (zt + .26) / 2, .55, .55, zt + .26)                                # outer node post and pier
    b.box('rust', po[0], po[1], zt + .29, .63, .63, .06)                                           # post cap
    b.box('concrete', po[0], po[1], .15, 1.1, 1.1, .3)
    b.box('rust', pi[0], pi[1], (ZB - .31 + zt + .26) / 2, .5, .5, zt + .26 - (ZB - .31))         # inner node post
    b.box('rust', pi[0], pi[1], zt + .29, .58, .58, .06)                                           # post cap
    b.beam('rust', (po[0], po[1], ZD - .32), (pi[0], pi[1], ZD - .32), .24, .3)                    # apex floor beam
    ends = [along(APEX, g['u'], g['top'][0], -g['sg'] * HW, zt) for g in ARMS.values()]          # first outer top-chord nodes
    b.beam('rust', ends[0], ends[1], .26, .3)                                                      # collar tie across the corner
    for q in ends:
        b.beam('rust', (pi[0], pi[1], zt + .03), (q[0], q[1], zt + .03), .2, .2)                  # struts from the inner node
    b.flush('apex')


def tower(name, Q, u):
    """Brick stair tower: the face toward the span carries the deck doorway, a ground door and a stair slot window."""
    ux, uy = u[0], u[1]
    vx, vy = -uy, ux
    f = C.Face((Q[0], Q[1], 0), (vx, vy, 0), (ux, uy, 0), name)
    top = ZD + HT + .4
    door = hole(f'{name} deck door', 0.0, ZD, 2.4, 2.6, kind='door')
    gdoor = hole(f'{name} ground door', 0.0, 0.0, 1.6, 2.5, kind='door')
    slot = hole(f'{name} stair window', 1.55, 1.2, .6, 4.6)
    f.wall(f'{name} front', -2.3, 2.3 - EPS, 0.0, top, depth=T, role='brick', holes=[door, gdoor, slot])
    G.brick_courses(f, -2.28, 2.28, .2, top - .1, [door, gdoor, slot], spacing=.5)
    m = Merge(f)
    for h, occ in ((door, 'deck lobby'), (gdoor, 'stair hall')):
        framed(m, f, h, cols=2, rows=2, inset=.14, occupied=occ, kind='door', frame='hardware')
    framed(m, f, slot, cols=1, rows=4, inset=.14, occupied='stair', frame='hardware')
    m.box('rust', 0.0, -.3, 2.7, 2.4, .6, .12)                                                   # canopy over the ground door
    m.box('pale', 0.0, T / 2 - .03, top + .06, 4.7, T + .16, .12)
    m.flush(name)
    body = [(Q[0] + ux * T + vx * s * 2.3, Q[1] + uy * T + vy * s * 2.3) for s in (-1, 1)]
    body += [(Q[0] + ux * 4.6 + vx * s * 2.3, Q[1] + uy * 4.6 + vy * s * 2.3) for s in (1, -1)]
    if (body[1][0] - body[0][0]) * (body[2][1] - body[0][1]) - (body[1][1] - body[0][1]) * (body[2][0] - body[0][0]) < 0:
        body = body[::-1]
    C.prism(f'{name} body', body, 'z', 0.0, top, 'brick', 'towers')
    C.qa_room_light(f'{name} hall', (Q[0] + ux * 1.6, Q[1] + uy * 1.6, ZD + 1.4), 40, 1.6)
    C.qa_room_light(f'{name} stair', (Q[0] + ux * 1.6, Q[1] + uy * 1.6, 2.0), 40, 1.6)


def street():
    C.box('Ground', (-8.0, -5.0, .005), (130.0, 110.0, .01), 'sand', 'site', 0)
    C.box('Carriageway', (0.0, -5.0, .02), (2 * RX, 110.0, .02), 'asphalt', 'street', 0)
    for s in (-1, 1):
        C.box(f'Sidewalk {s:+d}', (s * (RX + SW / 2), -5.0, .085), (SW, 110.0, .15), 'concrete', 'street', 0)
    b = Batch()
    for s in (-1, 1):
        b.box('yellow', s * .15, -5.0, .032, .12, 110.0, .004)                                      # double yellow centre line
        for k in range(12):
            b.box('white', s * RX / 2, -58.0 + k * 9.5, .032, .14, 3.0, .004)                         # lane lines
        for k in range(36):
            b.box('joint', s * (RX + SW / 2), -59.0 + k * 3.0, .162, SW - .04, .03, .004)
    b.box('white', 4.5, 16.0, 1.75, 2.5, 12.0, 3.2)                                               # a bus
    b.box('dark', 4.5, 16.0, 2.2, 2.54, 11.0, 1.0)
    for x, y in ((-4.5, -26.0), (4.5, -8.0), (-4.5, 26.0)):
        b.box('dark', x, y, .55, 1.8, 4.4, .8)
        b.box('glass', x, y + .2, 1.2, 1.6, 2.4, .6)
    b.flush('street')
    for x, y in ((12.0, 4.0), (12.0, 20.0), (12.0, -32.0), (-12.0, -32.0)):
        street_tree(x, y, z=.16, height=7.5, spread=2.0)


def block(name, x0, x1, y0, y1, h, faces, role='brick', roof='roof', glazed=False):
    """Context block: windowed walls on the faces that look at the bridge, a body behind, a flat roof with plant."""
    if glazed:
        C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), 'glass', 'context', 0)
        C.box(f'{name} core', ((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0 - 1.2, y1 - y0 - 1.2, h - .2), 'interior', 'context', 0)   # offices behind the glass
        b = Batch()
        for k in range(int((x1 - x0) / 1.5) + 1):                                              # mullions
            for y in (y0 - .03, y1 + .03):
                b.box('trim', x0 + k * (x1 - x0) / int((x1 - x0) / 1.5), y, h / 2, .12, .1, h)
        for k in range(int((y1 - y0) / 1.5) + 1):
            for x in (x0 - .03, x1 + .03):
                b.box('trim', x, y0 + k * (y1 - y0) / int((y1 - y0) / 1.5), h / 2, .1, .12, h)
        for z in range(4, int(h), 4):
            b.box('trim', (x0 + x1) / 2, (y0 + y1) / 2, z, x1 - x0 + .1, y1 - y0 + .1, .3)
        b.box('trim', (x0 + x1) / 2, (y0 + y1) / 2, h + .3, x1 - x0 + .1, y1 - y0 + .1, .6)
        b.box('pale', (x0 + x1) / 2, (y0 + y1) / 2, h + 1.6, (x1 - x0) * .5, (y1 - y0) * .4, 2.0)
        b.flush(name)
        return
    bx0, bx1, by0, by1 = x0, x1, y0, y1
    for fc in faces:
        if fc == 's':
            f = C.Face((0, y0, 0), (1, 0, 0), (0, 1, 0), f'{name} south'); lo, hi = x0, x1; by0 = y0 + T
        elif fc == 'n':
            f = C.Face((0, y1, 0), (-1, 0, 0), (0, -1, 0), f'{name} north'); lo, hi = -x1, -x0; by1 = y1 - T
        elif fc == 'e':
            f = C.Face((x1, 0, 0), (0, 1, 0), (-1, 0, 0), f'{name} east'); lo, hi = y0, y1; bx1 = x1 - T
            lo += T if 's' in faces else 0.0; hi -= T if 'n' in faces else 0.0
        else:
            f = C.Face((x0, 0, 0), (0, -1, 0), (1, 0, 0), f'{name} west'); lo, hi = -y1, -y0; bx0 = x0 + T
            lo += T if 'n' in faces else 0.0; hi -= T if 's' in faces else 0.0
        n = int((hi - lo) / 3.0)
        hs = [hole(f'{f.label} window f{k} {j}', lo + (hi - lo) * (j + .5) / n, 1.4 + k * 3.6, 1.3, 2.0) for k in range(int((h - 1.5) / 3.6)) for j in range(n)]
        f.wall(f'{f.label} wall', lo, hi - EPS, 0.0, h, depth=T, role=role, holes=hs)
        m = Merge(f)
        for hh in hs:
            framed(m, f, hh, cols=2, rows=2, inset=.14, occupied='offices', lite=True)
        m.flush(f.label)
    C.box(f'{name} body', ((bx0 + bx1) / 2, (by0 + by1) / 2, h / 2), (bx1 - bx0, by1 - by0, h), role, 'context', 0)
    C.box(f'{name} roof', ((x0 + x1) / 2, (y0 + y1) / 2, h + .06), (x1 - x0, y1 - y0, .12), roof, 'context', 0)
    b = Batch()
    for k in range(3):
        b.box('pale', x0 + (x1 - x0) * (.3 + .2 * k), (y0 + y1) / 2, h + .62, 1.6, 1.2, 1.0)
    b.flush(f'{name} plant')
    C.qa_room_light(f'{name} rooms', ((x0 + x1) / 2, (y0 + y1) / 2, 4.0), 60, 4.0)


def build():
    street()
    span('Crossing arm', UA, QA)
    span('Land arm', UB, QB)
    apex()
    tower('East tower', QA, UA)
    tower('West tower', QB, UB)
    block('Pale-roofed warehouse', -42.0, -14.2, 7.6, 34.0, 15.0, ['s', 'e'], roof='pale')     # the apex at its corner
    block('West warehouse', -58.0, -32.0, -50.0, -16.0, 10.0, ['e', 'n'])
    block('South-east block', 18.5, 46.0, -48.0, -26.0, 12.0, ['w', 'n'], roof='pale')
    block('Glass office', 18.0, 44.0, 6.0, 34.0, 24.0, [], glazed=True)
    C.CONTACTS.append(dict(name='V-plan Cor-Ten truss footbridge over a city street: arms on brick towers and one apex pier', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(30, -45, 45), fill=(-40, -25, 30), rear=(-20, 40, 30), target=(-6.0, -6.0, ZD), gain=3.2)
