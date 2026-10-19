"""Weathering-steel footbridge, authored from the locked catalogue views of
urban_pedestrian_footbridge / variant_0 (Weathering Steel Truss).

Read from the pixels (the top view governs the plan): a rust-orange Cor-Ten Warren-truss footbridge in two straight
spans that meet at a bend, forming a V in plan with its apex at the north, beside a pale-roofed brick building on
the west side of a wide four-lane city street. One span crosses the street south-east to a landing on the far side;
the other runs south-west over the low ground beside the street. Each span is a pair of Warren trusses with bold
diagonals, a full top chord with cross ties and top bracing, a deck of perforated rust-brown plate, and grey
cable-mesh infill with a slim handrail along both inner faces. The spans land on brick stair towers; the apex
platform stands on two steel columns on the west sidewalk with a third tower behind it. Red-brick warehouses, a
glazed office block, street trees, a bus and cars as context.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-weathering-steel-footbridge'
X0, X1, Y0, Y1 = -36.0, 20.0, -24.0, 14.0      # the two spans, the apex and the three towers
RX = 9.0                                        # half-width of the carriageway (four lanes)
SW = 5.0                                        # sidewalks
ZD = 7.0                                        # deck top
HT = 3.4                                        # truss height to the top chord centre line
HW = 2.0                                        # truss centre lines either side of the deck axis
APEX = (-11.5, 4.0)
QA = (15.5, -18.5)                              # east landing (across the street)
QB = (-35.0, -19.0)                             # west landing
T = .3
EPS = .002
PALETTE = dict(rust=(.62, .27, .10), deck=(.42, .22, .12), mesh=(.48, .48, .47), hardware=(.30, .30, .31),
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


def along(p, u, s, v=0.0, z=0.0):
    """Point at distance s along unit u from p, offset v to the left of u, at height z."""
    return (p[0] + u[0] * s - u[1] * v, p[1] + u[1] * s + u[0] * v, z)


def manifest(version):
    h = ZD + HT + 4.4
    a, ua = APEX, UA
    cams = G.camera_roster(X1 - X0, Y1 - Y0, h, [
        ('facade_close', (11.0, -2.0, 1.7), along(a, ua, 17.0, 0.0, ZD + 1.5), 35),
        ('architecture_close', (-1.0, -1.0, ZD + 3.5), (APEX[0], APEX[1], ZD + 1.5), 35),
        ('glass_close', along(a, ua, 12.0, -1.0, ZD + 1.5), along(a, ua, 14.0, 1.8, ZD + .8), 35),
        ('truss_node', along(a, ua, 8.0, 6.0, ZD + 4.6), along(a, ua, 10.0, 2.0, ZD + 3.0), 40),
        ('mesh_infill', along(a, ua, 20.0, -1.0, ZD + 1.5), along(a, ua, 22.0, 1.75, ZD + .7), 35),
        ('deck_walk', along(a, ua, 4.5, 0.0, ZD + 1.6), along(a, ua, 30.0, 0.0, ZD + 1.2), 28),
        ('landing_stair', along(QA, ua, -7.0, 5.0, ZD + 1.0), (QA[0], QA[1], ZD + .5), 35),
        ('road_under', (2.0, -18.0, 1.6), (2.0, -6.0, ZD), 28),
        ('top_chord', along(a, ua, 15.0, 3.0, ZD + 9.0), along(a, ua, 18.0, 0.0, ZD + HT), 35),
        ('rear_north', (-2.0, 22.0, 15.0), (-6.0, -4.0, ZD), 32)])
    for c in cams:
        if c['name'] == 'front':                                              # the locked front: from inside the V, square to the east span
            c.update(location=along(a, ua, 17.0, -11.0, ZD + 2.5), target=along(a, ua, 17.0, 0.0, ZD + 1.6), lens=24, whole=False)
        elif c['name'] == 'front_corner':                                     # the locked oblique: high in the south, the apex beyond
            c.update(location=(-12.0, -40.0, 26.0), target=(-10.0, 0.0, ZD), lens=32, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(30.0, -40.0, 34.0), target=(-4.0, -6.0, ZD), lens=32, whole=False)
        elif c['name'] == 'top':
            c.update(location=(-8.0, -6.0, 90.0), target=(-8.0, -5.999, 0.0), ortho_scale=62.0, whole=False)
        elif c['name'] == 'left_side':
            c.update(location=(-60.0, -2.0, 14.0), target=(-10.0, -6.0, ZD), lens=30, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(45.0, -8.0, 14.0), target=(0.0, -6.0, ZD), lens=30, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(-6.0, 40.0, 26.0), target=(-6.0, -6.0, ZD), lens=30, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(-24.0, 40.0, 34.0), target=(-6.0, -6.0, ZD), lens=30, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='urban_pedestrian_footbridge/variant_0 (Weathering Steel Truss)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=0, storey_programme='street option: a two-span truss footbridge over a city street; the blocks are context',
            plan='two straight Warren-truss spans of about 33 and 35 m meeting at a bend (a V in plan, apex north, top view); the east span crosses a 28 m street with sidewalks',
            section_m=dict(carriageway=[-RX, RX], sidewalks=SW, deck_top=ZD, truss_height=HT, truss_lines=[-HW, HW]),
            facade='rust-orange Cor-Ten Warren trusses with bold diagonals, top chords with cross ties and bracing, perforated rust-brown deck, grey cable-mesh infill and handrail, brick stair towers, steel apex columns',
            levels_m=[0.0, ZD, ZD + HT], inferred='the tower interiors, the far streets and the blocks are context'),
        roof_contract=dict(type='open truss, no roof; flat roofs on the towers and blocks', datum_m=ZD, crowns_m=[ZD + HT + .3]),
        identity_contract=dict(owner='rust-orange Cor-Ten Warren truss footbridge with mesh infill over a road between brick buildings'),
        material_contract=dict(profile='source-palette clay: rust-orange weathering steel, rust-brown deck, grey mesh, red brick, pale roofs, glass office, dark asphalt with white and yellow lines', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='a footbridge over the street; the street, sidewalks and towers beneath'),
        street_contract=dict(kind='fixed_native_section', width_m=2 * (RX + SW), axis='y', junction_finish='concrete',
                             bands=['sidewalk', 'carriageway', 'sidewalk']),
        contact_contract=['Street and sidewalks at grade', 'Spans on the towers and the apex columns', 'Towers from grade'],
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

START = 3.2                                     # each span starts this far from the apex point


def hull(pts):
    """Convex hull, counter-clockwise (monotone chain)."""
    pts = sorted(set(pts))
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def span(name, u):
    """One straight span: two Warren trusses, top ties and bracing, floor beams, deck, mesh infill and handrails."""
    S = along(APEX, u, START)
    Q = QA if u is UA else QB
    L = math.hypot(Q[0] - S[0], Q[1] - S[1])
    n = max(4, round(L / 3.6))
    pl = L / n
    P = lambda s, v, z: along(S, u, s, v, z)
    b = Batch()
    for side in (-1, 1):
        v = side * HW
        b.beam('rust', P(0.0, v, ZD - .15), P(L, v, ZD - .15), .4, .45)                             # bottom chord
        b.beam('rust', P(pl * .5, v, ZD + HT), P(L - pl * .5, v, ZD + HT), .4, .42, ext=.2)          # top chord
        for i in range(n):                                                                       # Warren diagonals
            b.beam('rust', P(pl * i, v, ZD + .05), P(pl * (i + .5), v, ZD + HT - .1), .3, .3)
            b.beam('rust', P(pl * (i + .5), v, ZD + HT - .1), P(pl * (i + 1), v, ZD + .05), .3, .3)
        # Grey cable mesh and a slim handrail along the inner face.
        vi = side * (HW - .3)
        k = int(L / .22)
        for j in range(k + 1):
            b.beam('mesh', P(L * j / k, vi, ZD + .02), P(L * j / k, vi, ZD + 1.38), .016, .016)
        for z in (ZD + .35, ZD + .7, ZD + 1.05):
            b.beam('mesh', P(0.0, vi, z), P(L, vi, z), .014, .014)
        b.beam('hardware', P(0.0, vi, ZD + 1.42), P(L, vi, ZD + 1.42), .06, .06)
    for i in range(n):                                                                           # top ties and bracing
        b.beam('rust', P(pl * (i + .5), -HW, ZD + HT), P(pl * (i + .5), HW, ZD + HT), .26, .3)
        if i < n - 1:
            b.beam('rust', P(pl * (i + .5), -HW, ZD + HT + .02), P(pl * (i + 1.5), HW, ZD + HT + .02), .14, .14)
            b.beam('rust', P(pl * (i + .5), HW, ZD + HT + .04), P(pl * (i + 1.5), -HW, ZD + HT + .04), .14, .14)
    for i in range(n + 1):                                                                       # floor beams under the deck
        b.beam('rust', P(pl * i, -HW, ZD - .32), P(pl * i, HW, ZD - .32), .24, .3)
    b.beam('deck', P(0.0, 0.0, ZD - .05), P(L, 0.0, ZD - .05), 2 * (HW - .2), .1)                # perforated deck plate
    for j in range(int(L / .5)):
        b.beam('joint', P(.25 + j * .5, -(HW - .22), ZD + .002), P(.25 + j * .5, HW - .22, ZD + .002), .02, .004)
    b.flush(name)


def apex():
    """The bend: a deck platform joining the two spans, edge beams, posts and a top frame, mesh and rails on the free
    edges, two steel columns to the sidewalk, and the third stair tower behind it."""
    ends = []
    for u in (UA, UB):
        S = along(APEX, u, START)
        ends += [along(S, u, 0.0, HW + .2)[:2], along(S, u, 0.0, -HW - .2)[:2]]
    dx, dy = UA[0] + UB[0], UA[1] + UB[1]
    dl = math.hypot(dx, dy)
    dirn = (dx / dl, dy / dl)
    O = (APEX[0] - dirn[0] * 2.4, APEX[1] - dirn[1] * 2.4)
    tw = [(O[0] - dirn[1] * s * 1.7, O[1] + dirn[0] * s * 1.7) for s in (-1, 1)]       # a flat edge where the tower door opens
    poly = hull(ends + tw)
    C.prism('Apex deck', poly, 'z', ZD - .1, ZD, 'deck', 'apex')
    junction = {frozenset(ends[0:2]), frozenset(ends[2:4]), frozenset(tw)}
    b = Batch()
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        b.box('rust', p[0], p[1], (ZD - .4 + ZD + HT + .2) / 2, .36, .36, HT + .6)                 # posts at the corners
        b.beam('rust', (p[0], p[1], ZD + HT), (q[0], q[1], ZD + HT), .3, .34)                        # top frame
        if frozenset((p, q)) in junction:
            continue
        b.beam('rust', (p[0], p[1], ZD - .15), (q[0], q[1], ZD - .15), .32, .4)                      # edge beam
        L = math.hypot(q[0] - p[0], q[1] - p[1])
        ux, uy = (q[0] - p[0]) / L, (q[1] - p[1]) / L
        cx, cy = APEX
        nx, ny = -uy, ux
        if (cx - p[0]) * nx + (cy - p[1]) * ny < 0:
            nx, ny = -nx, -ny                                                                    # inward normal
        a = (p[0] + nx * .3, p[1] + ny * .3)
        c = (q[0] + nx * .3, q[1] + ny * .3)
        k = int(L / .22)
        for j in range(k + 1):
            x, y = a[0] + (c[0] - a[0]) * j / k, a[1] + (c[1] - a[1]) * j / k
            b.beam('mesh', (x, y, ZD + .02), (x, y, ZD + 1.38), .016, .016)
        b.beam('hardware', (a[0], a[1], ZD + 1.42), (c[0], c[1], ZD + 1.42), .06, .06)
        b.beam('rust', (p[0], p[1], ZD + .1), (q[0], q[1], ZD + HT - .1), .26, .26)                  # a diagonal in each free face
    for u in (UA, UB):                                                                           # columns to the sidewalk
        c = along(APEX, u, 1.6)
        b.box('rust', c[0], c[1], (ZD - .1) / 2, .5, .5, ZD - .1)
        b.box('concrete', c[0], c[1], .15, 1.0, 1.0, .3)
    b.flush('apex')
    tower('Apex tower', O, (-dirn[0], -dirn[1]))


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
    span('East span', UA)
    span('West span', UB)
    apex()
    tower('East tower', QA, UA)
    tower('West tower', QB, UB)
    block('Pale-roofed warehouse', -42.0, -15.0, 9.5, 34.0, 15.0, ['s', 'e'], roof='pale')
    block('West warehouse', -66.0, -44.0, -36.0, -6.0, 14.0, ['e', 'n'])
    block('South-east block', 18.5, 46.0, -48.0, -26.0, 12.0, ['w', 'n'], roof='pale')
    block('Glass office', 18.0, 44.0, 6.0, 34.0, 24.0, [], glazed=True)
    C.CONTACTS.append(dict(name='Two-span Cor-Ten truss footbridge over a city street: spans on brick towers and apex columns', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(30, -45, 45), fill=(-40, -25, 30), rear=(-20, 40, 30), target=(-6.0, -6.0, ZD), gain=3.2)
