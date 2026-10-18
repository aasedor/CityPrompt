"""Outdoor ice rink in a market square, authored from the locked catalogue views of
outdoor_ice_rink / variant_0 (outdoor_ice_rink_v0).

Read from the pixels (the top view governs the plan): a cobbled city square with a rounded-rectangle ice rink,
its long axis north-south, ringed by low white dasher boards with clear glass panels; a dark timber deck round
the boards; a tall decorated Christmas tree in a circular planter with a glass ring just north of the rink's
centre; a ring of dark timber market chalets with snow-laden pitched roofs, garlands and counters facing the ice,
four along each short side and six along each long side; benches by the ice; old town fronts round the square.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-ice-rink-market-square'
RX, RY, RR = 11.0, 17.0, 4.0                    # rink half-sizes and corner radius
DX, DY = 13.0, 19.5                             # timber deck half-sizes
X0, X1, Y0, Y1 = -17.0, 17.0, -23.5, 23.5      # the rink, deck and chalet ring
ICE = .16
TREE = (0.0, 5.0)
EPS = .002
T = .3
PALETTE = dict(ice=(.86, .90, .93), white=(.95, .95, .94), glass=(.62, .70, .74), hardware=(.10, .10, .11),
    deck=(.30, .22, .16), timber=(.32, .21, .14), hut=(.30, .20, .13), snow=(.94, .95, .96), roof=(.94, .95, .96),
    planting=(.12, .30, .16), tree=(.10, .26, .14), flower=(.76, .10, .10), gold=(.86, .70, .30), pale=(.98, .92, .70),
    counter=(.46, .32, .20), interior=(.80, .56, .34), setts=(.42, .40, .38), joint=(.30, .29, .28), stone=(.72, .70, .66),
    wall=(.80, .74, .62), facade=(.80, .74, .62), facade2=(.62, .34, .26), facade3=(.84, .82, .78), troof=(.56, .26, .18),
    dark=(.12, .12, .13), trim=(.94, .94, .92), sand=(.66, .60, .50), concrete=(.70, .69, .66), asphalt=(.30, .30, .31),
    soil=(.22, .16, .10), floor=(.58, .48, .38), pot=(.60, .34, .22), blue=(.20, .30, .40), orange=(.90, .52, .14))


def manifest(version):
    h = 15.5
    cams = G.camera_roster(X1 - X0 + 6.0, Y1 - Y0 + 6.0, h, [
        ('facade_close', (0.0, -40.0, 3.0), (0.0, Y0, 2.0), 45),
        ('architecture_close', (-9.0, -12.0, 4.0), (-15.0, -9.0, 2.0), 40),
        ('glass_close', (6.0, -12.0, 1.6), (RX, -6.0, .8), 40),
        ('christmas_tree', (0.0, -9.0, 4.0), (TREE[0], TREE[1], 6.0), 40),
        ('market_chalets', (9.0, 12.0, 3.2), (15.0, 15.0, 1.8), 40),
        ('dasher_boards', (-6.0, -15.5, 1.5), (-RX, -RY + 4.0, .7), 40),
        ('ice_surface', (0.0, -22.0, 8.0), (0.0, 0.0, 0.0), 40),
        ('square_aerial', (-30.0, -40.0, 34.0), (0.0, 0.0, 2.0), 40),
        ('interior', (-14.8, -3.0, 1.6), (-12.0, -3.0, 1.2), 40),
        ('rear_north', (0.0, 46.0, 14.0), (0.0, 10.0, 2.0), 45)])
    for c in cams:                       # the locked front stands on the ice at the south end, looking north
        if c['name'] == 'front':
            c['location'] = (-2.5, -15.5, 1.6); c['target'] = (1.0, 6.0, 4.0); c['lens'] = 24; c['whole'] = False
        elif c['name'] == 'front_corner':                                      # the locked oblique looks north-east from high in the south-west
            c['location'] = (-24.0, -50.0, 36.0); c['target'] = (1.0, 2.0, 1.0); c['lens'] = 35
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='outdoor_ice_rink/variant_0 (outdoor_ice_rink_v0)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=0, storey_programme='open space: an ice rink with a tree island, a timber deck, twenty market chalets',
            plan='22 x 34 m rounded rink (top view) on a 26 x 39 m deck, chalets four by six round it, in a cobbled square',
            facade='white dasher boards with glass panels, dark timber chalets with snowy pitched roofs, garlands and counters',
            levels_m=[0.0, .12, ICE], inferred='the town fronts are simplified context; chalet interiors are assumptions'),
        roof_contract=dict(type='open space; snow-covered pitched chalet roofs', datum_m=0.0, crowns_m=[h]),
        identity_contract=dict(owner='rounded ice rink with glass-topped dasher boards round a decorated tree island, framed by snowy market chalets on a timber deck in a cobbled square'),
        material_contract=dict(profile='source-palette clay: pale ice, white boards and clear glass, dark timber deck and chalets, white snow roofs, green garlands with red bows, a dark green tree with gold and red ornaments, grey setts', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='skating, market stalls, deck circulation, benches'),
        contact_contract=['Grade-zero setts', 'Deck on the setts, ice on the deck', 'Boards on the deck', 'Chalets on the deck and setts'],
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


# ---- Outdoor ice rink in a market square ----

def rink_outline(rx, ry, rr, n=6):
    """Rounded rectangle, counter-clockwise from the east side."""
    pts = []
    for cx, cy, a0 in ((rx - rr, ry - rr, 0), (-rx + rr, ry - rr, 90), (-rx + rr, -ry + rr, 180), (rx - rr, -ry + rr, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def ngon(b, role, cx, cy, z0, z1, r, n=12, cone=False):
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for i in range(n):
        a = 2 * math.pi * (i + .5) / n
        V.append((cx + r * math.cos(a), cy + r * math.sin(a), z0))
    if cone:
        V.append((cx, cy, z1))
        F.append(tuple(o + i for i in range(n - 1, -1, -1)))
        for i in range(n):
            F.append((o + i, o + (i + 1) % n, o + n))
        return
    for i in range(n):
        a = 2 * math.pi * (i + .5) / n
        V.append((cx + r * math.cos(a), cy + r * math.sin(a), z1))
    F.append(tuple(o + i for i in range(n - 1, -1, -1)))
    F.append(tuple(o + n + i for i in range(n)))
    for i in range(n):
        j = (i + 1) % n
        F.append((o + i, o + j, o + n + j, o + n + i))


def ice_and_boards():
    C.box('Timber deck', (0, 0, .06), (2 * DX, 2 * DY, .12), 'deck', 'rink', 0)
    out = rink_outline(RX, RY, RR)
    C.prism('Ice', out, 'z', .12, ICE, 'ice', 'rink')
    b = Batch()
    for k in range(int(2 * DX / .6)):                                          # deck boards
        x = -DX + .3 + k * .6
        b.box('joint', x, 0.0, .121, .015, 2 * DY - .02, .004)
    # Dasher boards: white board, glass panel above, posts and a top rail, round the rounded outline.
    ring = out + [out[0]]
    for (ax, ay), (cx, cy) in zip(ring, ring[1:]):
        L = math.hypot(cx - ax, cy - ay)
        b.beam('white', (ax, ay, .12 + .3), (cx, cy, .12 + .3), .12, .6, ext=.02)
        b.beam('glass', (ax, ay, .72 + .3), (cx, cy, .72 + .3), .03, .6, ext=.0)
        b.beam('white', (ax, ay, 1.36), (cx, cy, 1.36), .1, .06, ext=.03)
        n = max(1, int(L / 2.0))
        for i in range(n):
            px, py = ax + (cx - ax) * i / n, ay + (cy - ay) * i / n
            b.box('hardware', px, py, .97, .06, .06, .7)
    # Garland with bows along the east boards (seen in the front view), lights as pale beads.
    for (ax, ay), (cx, cy) in zip(ring, ring[1:]):
        if ax > RX - .1 and cx > RX - .1:
            b.beam('planting', (ax + .12, ay, 1.2), (cx + .12, cy, 1.2), .18, .18)
            for i in range(int(abs(cy - ay) / .8)):
                y = ay + (cy - ay) * i / max(1, int(abs(cy - ay) / .8))
                b.box('pale', ax + .22, y, 1.27, .06, .06, .06)
                if i % 3 == 0:
                    b.box('flower', ax + .22, y, 1.1, .08, .16, .16)
    b.flush('boards')
    # Tree island: white ring wall, glass ring, the tree in tiers with ornaments and a star.
    b = Batch()
    tx, ty = TREE
    ring = [(tx + 3.4 * math.cos(2 * math.pi * i / 24), ty + 3.4 * math.sin(2 * math.pi * i / 24)) for i in range(25)]
    for k, ((ax, ay), (cx, cy)) in enumerate(zip(ring, ring[1:])):
        w = .3 + .01 * (k % 2)                                                   # alternate widths: no shared planes at joints
        b.beam('white', (ax, ay, ICE + .225), (cx, cy, ICE + .225), w, .45, ext=.04)
        b.beam('glass', (ax, ay, ICE + .75), (cx, cy, ICE + .75), .03, .6, ext=.0)
        b.beam('white', (ax, ay, ICE + 1.08), (cx, cy, ICE + 1.08), .08 + .01 * (k % 2), .06, ext=.02)
    ngon(b, 'soil', tx, ty, ICE, ICE + .4, 3.25, 24)
    ngon(b, 'timber', tx, ty, ICE + .5, ICE + 1.6, .3, 8)
    tiers = [(1.4, 5.0, 2.7), (4.0, 8.0, 2.1), (6.6, 10.6, 1.5), (9.0, 12.6, .95), (11.2, 14.0, .5)]
    for z0, z1, r in tiers:
        ngon(b, 'tree', tx, ty, ICE + z0, ICE + z1, r, 14, cone=True)
    for k in range(70):                                                         # ornaments and lights spiralling up
        f = k / 70
        z = ICE + 1.8 + f * 11.0
        rr = 2.6 * (1 - f) + .35
        a = k * 2.4
        role = ('flower', 'gold', 'pale')[k % 3]
        b.box(role, tx + rr * math.cos(a), ty + rr * math.sin(a), z, .2, .2, .2)
    b.box('gold', tx, ty, ICE + 14.4, .2, .7, .7)
    b.flush('tree island')
    # Benches at the south-west of the ice; a penguin skating aid.
    b = Batch()
    for x in (-RX + 1.5, -RX + 3.5):
        b.box('counter', x, -RY + 3.0, ICE + .45, 1.6, .4, .06)
        for s in (-1, 1):
            b.box('hardware', x + s * .7, -RY + 3.0, ICE + .22, .05, .35, .44)
    b.box('dark', 4.5, -9.0, ICE + .45, .45, .4, .9)
    b.box('white', 4.5, -9.22, ICE + .45, .3, .05, .6)
    b.box('orange', 4.5, -9.3, ICE + .82, .1, .16, .06)
    b.box('orange', 4.5, -9.0, ICE + .02, .7, .5, .04)
    b.flush('benches and aids')


def plate(name, axis, eave, ridge, lo, hi, t=.14, role='snow', module='chalets'):
    """Closed sloped roof plate from eave (s, z) to ridge (s, z), extruded along axis between lo and hi."""
    vs = []
    for (s, z) in (eave, ridge):
        for a in (lo, hi):
            for dz in (0.0, -t):
                vs.append((a, s, z + dz) if axis == 'x' else (s, a, z + dz))
    fs = [(0, 2, 6, 4), (1, 5, 7, 3), (0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6)]
    return C.mesh(name, vs, fs, role, module)


def chalet(name, cx, cy, facing, length=3.6, depth=2.6):
    """Dark timber market chalet: walls, counter opening with a raised shutter, snowy pitched roof, eaves garland.
    facing: unit vector (fx, fy) from the chalet to the ice."""
    fx, fy = facing
    tx, ty = -fy, fx
    o = (cx - fx * depth / 2, cy - fy * depth / 2, 0)                            # back wall foot
    f = C.Face((cx + fx * depth / 2, cy + fy * depth / 2, 0), (tx, ty, 0), (-fx, -fy, 0), name)
    counter = hole(f'{name} counter', 0.0, 1.0, length - 1.0, 1.15)
    f.wall(f'{name} front', -length / 2, length / 2 - EPS, 0.0, 2.5, depth=.12, role='hut', holes=[counter])
    m = Merge(f)
    m.box('counter', 0.0, -.18, .98, length - .8, .5, .08)                        # counter board
    m.box('hut', 0.0, -.45, 2.32, length - .9, .9, .06)                         # shutter raised as an awning
    m.box('interior', 0.0, .8, 1.6, length - 1.2, .05, 1.2)                      # lit goods wall inside
    for i in range(5):
        m.box('pale', -length / 2 + .4 + i * (length - .8) / 4, -.06, 2.42, .06, .06, .06)
    register(f, counter, .06, 'stall counter', 'stall')
    m.flush(name)
    # Back and side walls as one closed body behind the front.
    size = (length, depth - .12, 2.5) if abs(tx) > .5 else (depth - .12, length, 2.5)
    C.box(f'{name} body', (cx - fx * .06, cy - fy * .06, 1.25), size, 'hut', 'chalets', 0)
    # Pitched roof, ridge along the chalet's length, snow on top; garland along the front eave.
    ov = .35
    half = depth / 2 + ov
    rise = 1.0
    if abs(tx) > .5:                                                             # ridge along x: timber gable, snowy plates
        C.prism(f'{name} gable', [(cy - depth / 2, 2.5), (cy + depth / 2 - .0, 2.5), (cy, 2.5 + rise * .92)], 'x', cx - length / 2, cx + length / 2, 'hut', 'chalets')
        for s in (-1, 1):
            plate(f'{name} roof {s:+d}', 'x', (cy + s * half, 2.5 - ov * rise / (depth / 2)), (cy, 2.5 + rise + .02), cx - length / 2 - ov, cx + length / 2 + ov)
    else:
        C.prism(f'{name} gable', [(cx - depth / 2, 2.5), (cx + depth / 2, 2.5), (cx, 2.5 + rise * .92)], 'y', cy - length / 2, cy + length / 2, 'hut', 'chalets')
        for s in (-1, 1):
            plate(f'{name} roof {s:+d}', 'y', (cx + s * half, 2.5 - ov * rise / (depth / 2)), (cx, 2.5 + rise + .02), cy - length / 2 - ov, cy + length / 2 + ov)
    b = Batch()
    ex, ey = cx + fx * (half - .05), cy + fy * (half - .05)
    b.beam('planting', (ex - tx * (length / 2 + .3), ey - ty * (length / 2 + .3), 2.3), (ex + tx * (length / 2 + .3), ey + ty * (length / 2 + .3), 2.3), .2, .2)
    b.box('flower', ex + fx * .12, ey + fy * .12, 2.6, .3 if abs(tx) > .5 else .12, .12 if abs(tx) > .5 else .3, .3)
    b.flush(f'{name} garland')
    C.qa_room_light(f'{name} light', (cx - fx * .3, cy - fy * .3, 1.9), 20, 1.0)


def chalets():
    for i, x in enumerate((-7.5, -2.5, 2.5, 7.5)):
        chalet(f'North chalet {i}', x, DY + 1.6, (0, -1))
        chalet(f'South chalet {i}', x, -DY - 1.6, (0, 1))
    for i, y in enumerate((-15.0, -9.0, -3.0, 3.0, 9.0, 15.0)):
        chalet(f'West chalet {i}', -DX - 1.6, y, (1, 0))
        chalet(f'East chalet {i}', DX + 1.6, y, (-1, 0))


def square():
    C.box('Square setts', (0, 0, .02), (70.0, 78.0, .04), 'setts', 'site', 0)
    b = Batch()
    for k in range(-46, 47):
        if abs(k * .75) > DX + .1:
            b.box('joint', k * .75, 0.0, .041, .015, 77.9, .004)
    for k in range(-52, 53):
        if abs(k * .75) > DY + .1:
            b.box('joint', 0.0, k * .75, .041, 69.9, .015, .004)
    for x, y in ((-DX - 4.2, -DY - 4.2), (DX + 4.2, -DY - 4.2), (-DX - 4.2, DY + 4.2), (DX + 4.2, DY + 4.2)):
        b.box('hardware', x, y, 2.2, .14, .14, 4.4)
        b.box('pale', x, y, 4.6, .36, .36, .4)
        b.box('hardware', x, y, 4.85, .46, .46, .1)
    b.flush('square furniture')
    # Old town fronts round the square, as context.
    for name, cx, cy, sx, sy, h, role, facing in (('North front', 0.0, 36.0, 46.0, 6.0, 15.0, 'facade3', (0, -1)),
                                                 ('West front', -32.0, 0.0, 6.0, 60.0, 11.0, 'facade2', (1, 0)),
                                                 ('East front', 32.0, 0.0, 6.0, 60.0, 14.0, 'facade', (-1, 0))):
        C.box(name, (cx, cy, h / 2), (sx, sy, h), role, 'context', 0)
        if facing[1]:
            C.prism(f'{name} roof', [(cy - sy / 2 - .3, h), (cy + sy / 2 + .3, h), (cy, h + 3.5)], 'x', cx - sx / 2, cx + sx / 2, 'troof', 'context')
        else:
            C.prism(f'{name} roof', [(cx - sx / 2 - .3, h), (cx + sx / 2 + .3, h), (cx, h + 3.5)], 'y', cy - sy / 2, cy + sy / 2, 'troof', 'context')
        b = Batch()
        fx, fy = facing
        span = sx if fy else sy
        n = int(span / 3.0)
        for i in range(n):
            u = -span / 2 + 1.5 + i * 3.0
            for z in range(int((h - 2) / 3.2)):
                zz = 1.4 + z * 3.2
                if fy:
                    x, y = cx + u, cy + fy * (sy / 2 + .02)
                    b.box('dark', x, y, zz + .9, 1.1, .04, 1.7)
                else:
                    x, y = cx + fx * (sx / 2 + .02), cy + u
                    b.box('dark', x, y, zz + .9, .04, 1.1, 1.7)
        b.flush(f'{name} windows')


def build():
    square()
    ice_and_boards()
    chalets()
    C.CONTACTS.append(dict(name='Ice rink with tree island and market chalets on a cobbled square', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(35, -45, 40), fill=(-40, -25, 30), rear=(-20, 40, 30), target=(0, 0, 2.0), gain=3.0)
