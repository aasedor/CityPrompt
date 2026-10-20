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
CX, CY = 9.9, 17.2                              # deck chamfer: ends of the north/south and east/west chalet rows
X0, X1, Y0, Y1 = -17.0, 17.0, -23.5, 23.5      # the rink, deck and chalet ring
ICE = .16
TREE = (0.0, 1.0)                               # just north of centre (top view: about 47% from the north end)
EPS = .002
T = .3
PALETTE = dict(ice=(.86, .90, .93), white=(.95, .95, .94), glass=(.62, .70, .74), hardware=(.10, .10, .11),
    deck=(.21, .15, .10), timber=(.32, .21, .14), hut=(.30, .20, .13), snow=(.94, .95, .96), roof=(.94, .95, .96),
    planting=(.12, .30, .16), tree=(.10, .26, .14), tree2=(.07, .21, .11), flower=(.76, .10, .10), gold=(.86, .70, .30), pale=(.98, .92, .70),
    counter=(.46, .32, .20), interior=(.80, .56, .34), setts=(.20, .19, .18), joint=(.31, .30, .28), stone=(.72, .70, .66),
    wall=(.80, .74, .62), facade=(.80, .74, .62), facade2=(.62, .34, .26), facade3=(.84, .82, .78), troof=(.56, .26, .18),
    dark=(.12, .12, .13), trim=(.94, .94, .92), sand=(.66, .60, .50), concrete=(.70, .69, .66), asphalt=(.30, .30, .31),
    soil=(.22, .16, .10), floor=(.58, .48, .38), pot=(.60, .34, .22), blue=(.20, .30, .40), orange=(.90, .52, .14))


def manifest(version):
    h = 15.5
    cams = G.camera_roster(X1 - X0 + 6.0, Y1 - Y0 + 6.0, h, [
        ('facade_close', (3.0, -33.0, 5.5), (0.0, -21.6, 2.8), 40),
        ('architecture_close', (-9.0, -12.0, 4.0), (-15.0, -9.0, 2.0), 40),
        ('glass_close', (6.0, -12.0, 1.6), (RX, -6.0, .8), 40),
        ('christmas_tree', (0.0, -9.0, 4.0), (TREE[0], TREE[1], 6.0), 40),
        ('market_chalets', (9.0, 12.0, 3.2), (15.0, 15.0, 1.8), 40),
        ('dasher_boards', (-6.0, -15.5, 1.5), (-RX, -RY + 4.0, .7), 40),
        ('ice_surface', (0.0, -22.0, 8.0), (0.0, 0.0, 0.0), 40),
        ('square_aerial', (-30.0, -40.0, 34.0), (0.0, 0.0, 2.0), 40),
        ('interior', (-16.2, -3.6, 1.6), (-12.0, -2.6, 1.3), 50),
        ('rear_north', (8.0, 28.8, 11.5), (0.0, 4.0, 5.5), 28)])
    for c in cams:                       # the locked front stands on the ice by the east boards at the south end, looking NNW
        if c['name'] == 'front':
            c['location'] = (9.0, -14.0, 2.2); c['target'] = (5.6, 14.0, 6.6); c['lens'] = 19; c['whole'] = False   # tilted up about 5 deg, yawed about 4 deg west: tree, star, sky and the west row in frame
        elif c['name'] == 'aerial':                                            # steep enough that the near frontage clears the near chalet row
            c.update(location=(34.0, -42.0, 70.0), target=(0.0, -1.0, 0.0), lens=42)
        elif c['name'] == 'front_corner':                                      # the locked oblique looks north-east from high in the south-west
            c['location'] = (-24.0, -50.0, 36.0); c['target'] = (1.0, 2.0, 1.0); c['lens'] = 35
        elif c['name'] == 'left_side':                                         # side and rear views stand high in the lanes, the near roofs below the frame
            c.update(location=(-23.0, -4.0, 14.0), target=(0.0, 1.0, 5.5), lens=24, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(23.0, 4.0, 14.0), target=(0.0, 1.0, 5.5), lens=24, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(2.0, 28.8, 13.0), target=(0.0, 1.0, 5.5), lens=24, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(19.5, 25.5, 14.0), target=(0.0, 0.0, 1.0), lens=30, whole=False)
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


def ring_tube(b, role, pts, zc, w, h, sides):
    """Closed tube swept round a closed counter-clockwise outline with mitred joints, so the bends round the rink
    corners leave no gaps. Cross-section: rectangle (sides=4) or an ellipse of `sides` points, w wide and h high."""
    V, F = b.g.setdefault(role, ([], []))
    o, n = len(V), len(pts)
    if sides == 4:
        sec = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    else:
        sec = [(w / 2 * math.cos(2 * math.pi * k / sides), h / 2 * math.sin(2 * math.pi * k / sides)) for k in range(sides)]
    for i in range(n):
        (px, py), (qx, qy), (rx, ry) = pts[i - 1], pts[i], pts[(i + 1) % n]
        def nrm(ax, ay, bx, by):
            L = math.hypot(bx - ax, by - ay)
            return (by - ay) / L, -(bx - ax) / L                                   # outward for a counter-clockwise ring
        n1, n2 = nrm(px, py, qx, qy), nrm(qx, qy, rx, ry)
        mx, my = n1[0] + n2[0], n1[1] + n2[1]
        L = math.hypot(mx, my); mx, my = mx / L, my / L
        sc = 1.0 / max(.5, mx * n1[0] + my * n1[1])                              # mitre length
        for (u, v) in sec:
            V.append((qx + mx * u * sc, qy + my * u * sc, zc + v))
    m = len(sec)
    for i in range(n):
        a, c = o + i * m, o + ((i + 1) % n) * m
        for k in range(m):
            k2 = (k + 1) % m
            F.append((a + k, c + k, c + k2, a + k2))


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
    # Deck trimmed to the chalet line: the corners are chamfered between the end of the side rows and the end
    # of the north and south rows, so no square pad sticks out past the chalet ring.
    deck = [(DX, -CY), (DX, CY), (CX, DY), (-CX, DY), (-DX, CY), (-DX, -CY), (-CX, -DY), (CX, -DY)]
    C.prism('Timber deck', deck, 'z', 0.0, .12, 'deck', 'rink')
    out = rink_outline(RX, RY, RR)
    C.prism('Ice', out, 'z', .12, ICE, 'ice', 'rink')
    b = Batch()
    for k in range(int(2 * DX / .6)):                                          # deck boards
        x = -DX + .3 + k * .6
        ym = DY if abs(x) <= CX else DY - (abs(x) - CX) * (DY - CY) / (DX - CX)     # clipped to the chamfered corners
        b.box('joint', x, 0.0, .121, .015, 2 * ym - .3, .004)
    # Dasher boards: white board, glass panel above, posts and a top rail, round the rounded outline.
    ring = out + [out[0]]
    for j, ((ax, ay), (cx, cy)) in enumerate(zip(ring, ring[1:])):
        L = math.hypot(cx - ax, cy - ay)
        b.beam('white', (ax, ay, .58), (cx, cy, .58), .12 + .006 * (j % 2), .92, ext=.02)        # alternate widths: no shared planes     # opaque white board to 1.04 m
        b.beam('glass', (ax, ay, 1.34), (cx, cy, 1.34), .03, .6, ext=.0)
        ux, uy = (cy - ay) / L, -(cx - ax) / L                                                    # outward normal
        b.beam('dark', (ax - ux * .07, ay - uy * .07, ICE + .07), (cx - ux * .07, cy - uy * .07, ICE + .07),
               .04 + .006 * (j % 2), .18, ext=.02)                                                # kick-plate at the ice, sunk 2 cm into it
        n = max(1, int(L / 2.0))
        for i in range(n):
            px, py = ax + (cx - ax) * i / n, ay + (cy - ay) * i / n
            b.box('hardware', px, py, 1.35, .06, .06, .62)
        # Lush garland laid along the top of the handrail, reading from the ice and the deck, with red baubles
        # and warm lights on both faces.
        nx, ny = (cy - ay) / L, -(cx - ax) / L                                                    # outward normal (ring is counter-clockwise)
        k = max(1, int(L / .55))
        for i in range(k):
            px, py = ax + (cx - ax) * (i + .5) / k, ay + (cy - ay) * (i + .5) / k
            s = -1 if i % 2 else 1                                                                # alternate ice and deck faces
            if i % 6 in (0, 3):                                                                   # extra warm lights on the ice-side face
                RAIL_LIGHTS.append((px - nx * .19, py - ny * .19, 1.97))
            if i % 3 == 2:
                RAIL_LIGHTS.append((px + s * nx * .19, py + s * ny * .19, 1.95))
            else:
                RAIL_BAUBLES.append((px + s * nx * .2, py + s * ny * .2, 1.8))
    ring_tube(b, 'timber', out, 1.7, .26, .1, 4)                                                  # timber handrail, one mitred loop
    ring_tube(b, 'planting', out, 1.86, .34, .24, 8)                                              # garland laid on the rail, one swept loop
    b.flush('boards')
    balls('Handrail garland baubles', 'flower', RAIL_BAUBLES, .075, 6, 4)
    balls('Handrail garland lights', 'pale', RAIL_LIGHTS, .04, 4, 2)
    # Tree island: white ring wall, glass ring, a dense layered fir with ornaments, lights and a star.
    b = Batch()
    tx, ty = TREE
    RI = 3.9                                                                     # island ring radius (top view: about 0.35 of the rink width)
    ring = [(tx + RI * math.cos(2 * math.pi * i / 28), ty + RI * math.sin(2 * math.pi * i / 28)) for i in range(29)]
    for k, ((ax, ay), (cx, cy)) in enumerate(zip(ring, ring[1:])):
        w = .3 + .01 * (k % 2)                                                   # alternate widths: no shared planes at joints
        b.beam('white', (ax, ay, ICE + .225), (cx, cy, ICE + .225), w, .45, ext=.04)
        b.beam('glass', (ax, ay, ICE + .75), (cx, cy, ICE + .75), .03, .6, ext=.0)
        b.beam('white', (ax, ay, ICE + 1.08), (cx, cy, ICE + 1.08), .08 + .01 * (k % 2), .06, ext=.02)
    ngon(b, 'tree2', tx, ty, ICE, ICE + .4, RI - .15, 28)                    # planter bed under the boughs
    ngon(b, 'timber', tx, ty, ICE + .3, ICE + 1.9, .32, 8)
    fir(b, tx, ty)
    b.flush('tree island')
    # Benches at the south-west of the ice; a penguin skating aid.
    b = Batch()
    for x in (-RX + 1.5, -RX + 3.5):
        b.box('counter', x, -RY + 3.0, ICE + .45, 1.6, .4, .06)
        for s in (-1, 1):
            b.box('hardware', x + s * .7, -RY + 3.0, ICE + .22, .05, .35, .44)
    px, py = 7.5, -5.5                                                           # penguin skating aid ahead of the east boards
    ngon(b, 'dark', px, py, ICE + .04, ICE + .78, .26, 10)                      # rounded body
    ngon(b, 'dark', px, py, ICE + .74, ICE + 1.02, .19, 10)                     # head
    b.box('white', px, py - .24, ICE + .45, .3, .06, .56)                       # belly
    b.box('orange', px, py - .27, ICE + .92, .1, .14, .06)                      # beak
    b.box('orange', px, py, ICE + .02, .7, .5, .04)                             # feet and runner
    for sx in (-1, 1):                                                          # handle bar on two posts
        b.box('hardware', px + sx * .28, py + .25, ICE + .9, .04, .04, .7)
    b.box('hardware', px, py + .25, ICE + 1.25, .6, .05, .05)
    b.flush('benches and aids')


RAIL_BAUBLES, RAIL_LIGHTS = [], []


def balls(name, role, centres, r, seg, rings, small=(), rs=None):
    """One smooth-shaded mesh of low-poly UV spheres (seg x rings); centres listed in small get radius rs."""
    if not centres:
        return
    small = set(small)
    V, F = [], []
    for (x, y, z) in centres:
        rad = rs if (rs and (x, y, z) in small) else r
        o = len(V)
        V.append((x, y, z + rad))
        for k in range(1, rings):
            ph = math.pi * k / rings
            for j in range(seg):
                th = 2 * math.pi * j / seg
                V.append((x + rad * math.sin(ph) * math.cos(th), y + rad * math.sin(ph) * math.sin(th), z + rad * math.cos(ph)))
        V.append((x, y, z - rad))
        last = o + 1 + (rings - 1) * seg
        for j in range(seg):
            jn = (j + 1) % seg
            F.append((o, o + 1 + j, o + 1 + jn))
            for k in range(rings - 2):
                a, b_ = o + 1 + k * seg, o + 1 + (k + 1) * seg
                F.append((a + j, b_ + j, b_ + jn, a + jn))
            c = o + 1 + (rings - 2) * seg
            F.append((c + jn, c + j, last))
    obj = C.mesh(name, V, F, role, 'tree island')
    for f in obj.data.polygons:
        f.use_smooth = True


def fir(b, tx, ty):
    """A dense fir of thirteen overlapping drooping skirts: each skirt rises from a serrated ring of bough tips
    (tips jittered in reach and droop) to a collar round the trunk, with an underside back to the trunk; the
    next skirt up starts below the collar of the one beneath, so no trunk or soil shows from the side or above.
    Baubles and lights are seated proud of the bough tips, some baubles hang from the tips; a star tops it."""
    NT, zb0, top = 13, ICE + 1.05, ICE + 13.9
    orn = []
    for i in range(NT):
        f = i / (NT - 1)
        ro = .45 + 3.05 * (1 - f) ** 1.05                                        # reach of the tips
        zb = zb0 + i * .9                                                       # tip level
        h = .85 + .45 * ro                                                      # skirt height, tips to collar
        ri = .2 + .1 * ro                                                       # collar radius
        nt = max(8, int(2 * math.pi * ro / .5))                                 # bough tips round the skirt
        m = 2 * nt
        rot = i * .61
        role = 'tree' if i % 2 == 0 else 'tree2'
        V, F = b.g.setdefault(role, ([], []))
        o = len(V)
        rings = []
        for j in range(m):
            a = rot + 2 * math.pi * j / m
            tip = j % 2 == 0
            jit = math.sin(j * 2.37 + i * 1.71)
            r = ro * (1 + .07 * jit) if tip else ro * (.93 if i == 0 else .86)
            z = zb - .14 * abs(math.sin(j * 1.31 + i)) if tip else zb + .3 + .1 * h
            rm = .6 * r
            zm = zb + h * (1 - (rm - ri) / max(.01, r - ri)) + .1 * h           # drooping profile: fuller near the trunk
            rings.append((a, r, z, rm, zm, tip))
        for (a, r, z, rm, zm, tip) in rings:                                    # collar, mid, tips, underside
            ca, sa = math.cos(a), math.sin(a)
            V.append((tx + ri * ca, ty + ri * sa, zb + h))
            V.append((tx + rm * ca, ty + rm * sa, zm))
            V.append((tx + r * ca, ty + r * sa, z))
            V.append((tx + .5 * r * ca, ty + .5 * r * sa, zb + .22 * h))
            if tip:
                orn.append((tx, ty, a, r, z, rm, zm, i))
        V.append((tx, ty, zb + h + .05)); V.append((tx, ty, zb + .35 * h))
        c_top, c_bot = o + 4 * m, o + 4 * m + 1
        for j in range(m):
            k, n = o + 4 * j, o + 4 * ((j + 1) % m)
            F.append((k, n, c_top))
            F.append((k + 1, n + 1, n, k))
            F.append((k + 2, n + 2, n + 1, k + 1))
            F.append((k + 3, n + 3, n + 2, k + 2))
            F.append((c_bot, n + 3, k + 3))
    z_sp = zb0 + (NT - 1) * .9 + .6
    ngon(b, 'tree', tx, ty, z_sp, top, .42, 9, cone=True)                      # leader
    red, gold, lights = [], [], []
    for q, (x0, y0, a, r, z, rm, zm, i) in enumerate(orn):
        ca, sa = math.cos(a), math.sin(a)
        lights.append((x0 + 1.01 * r * ca, y0 + 1.01 * r * sa, z + .05))          # a warm light on every bough tip
        if q % 3 == 2:
            continue
        br = .15 if i < 9 else .11                                              # round bauble hung just under the tip
        rr = 1.02 * r + .06                                                     # proud of the tip: never buried in the skirt below
        (red if (q + i) % 2 else gold).append((x0 + rr * ca, y0 + rr * sa, z - .04 - br))
    balls('Tree baubles red', 'flower', red, .15, 8, 5, small=[p for p in red if p[2] > zb0 + 8.6], rs=.11)
    balls('Tree baubles gold', 'gold', gold, .15, 8, 5, small=[p for p in gold if p[2] > zb0 + 8.6], rs=.11)
    balls('Tree lights', 'pale', lights, .055, 4, 2)
    # Five-point star seated on the leader tip by a short gold stem: two crossed closed star prisms (one facing
    # north-south, one east-west) so it reads as a solid star from every side, its lowest inner point on the stem.
    zc = top + .38
    C.rod('Tree star stem', (tx, ty, top - .25), (tx, ty, zc), .07, 'gold', 'tree island', 10)
    star = []
    for k in range(10):
        a = math.pi / 2 + math.pi * k / 5
        rr = .55 if k % 2 == 0 else .22
        star.append((rr * math.cos(a), zc + rr * math.sin(a)))
    C.prism('Tree star', [(tx + u, z) for (u, z) in reversed(star)], 'y', ty - .08, ty + .08, 'gold', 'tree island')
    C.prism('Tree star cross', [(ty + u, z) for (u, z) in star], 'x', tx - .08, tx + .08, 'gold', 'tree island')


def plate(name, axis, eave, ridge, lo, hi, t=.14, role='snow', module='chalets'):
    """Closed sloped roof plate from eave (s, z) to ridge (s, z), extruded along axis between lo and hi."""
    vs = []
    for (s, z) in (eave, ridge):
        for a in (lo, hi):
            for dz in (0.0, -t):
                vs.append((a, s, z + dz) if axis == 'x' else (s, a, z + dz))
    fs = [(0, 2, 6, 4), (1, 5, 7, 3), (0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6)]
    return C.mesh(name, vs, fs, role, module)


def chalet(name, cx, cy, facing, width=4.4, depth=3.6):
    """Dark timber market chalet, gable end to the ice: a counter in the gable wall with a raised shutter, hollow
    walls round a goods wall at the back, a snowy pitched roof with its ridge running toward the ice, garlands
    with lights on the front rakes, a wreath in the gable and a red bow at the apex. facing: unit vector to the ice."""
    fx, fy = facing
    tx, ty = -fy, fx
    H0, rise, ov = 2.4, 1.3, .35
    f = C.Face((cx + fx * depth / 2, cy + fy * depth / 2, 0), (tx, ty, 0), (-fx, -fy, 0), name)
    counter = hole(f'{name} counter', 0.0, 1.0, width - 1.4, 1.15)
    f.wall(f'{name} front', -width / 2, width / 2 - EPS, 0.0, H0, depth=.12, role='hut', holes=[counter])
    m = Merge(f)
    m.box('counter', 0.0, -.18, .98, width - 1.2, .5, .08)                       # counter board
    m.box('hut', 0.0, -.45, 2.22, width - 1.3, .9, .06)                         # shutter raised as an awning
    m.box('interior', 0.0, depth - .25, 1.5, width - .5, .06, 1.6)              # lit goods wall at the back
    for k in range(3):
        m.box('counter', 0.0, depth - .45, .9 + .45 * k, width - .7, .35, .04)        # shelves
    m.box('floor', 0.0, depth / 2, .03, width - .26, depth - .14, .06)
    register(f, counter, .06, 'stall counter', 'stall')
    m.flush(name)
    b = Batch()
    for s in (-1, 1):                                                           # side walls and back wall (hollow stall)
        p = (cx + tx * s * (width / 2 - .06), cy + ty * s * (width / 2 - .06))
        b.box('hut', p[0], p[1], H0 / 2, .12 if abs(tx) > .5 else depth - .12, depth - .12 if abs(tx) > .5 else .12, H0)
    q = (cx - fx * (depth / 2 - .06), cy - fy * (depth / 2 - .06))
    b.box('hut', q[0], q[1], H0 / 2, width - .24 if abs(tx) > .5 else .12, .12 if abs(tx) > .5 else width - .24, H0)
    b.flush(f'{name} walls')
    # The gable volume (ridge along the facing axis) closes the top; snowy roof plates overhang the gables and eaves.
    half = width / 2 + ov
    zeave = H0 - ov * rise / (width / 2)
    if abs(fx) > .5:                                                             # facing east or west: ridge along x
        C.prism(f'{name} gable', [(cy - width / 2, H0), (cy + width / 2, H0), (cy, H0 + rise * .92)], 'x', cx - depth / 2, cx + depth / 2, 'hut', 'chalets')
        for s in (-1, 1):
            plate(f'{name} roof {s:+d}', 'x', (cy + s * half, zeave), (cy, H0 + rise + .02), cx - depth / 2 - ov, cx + depth / 2 + ov)
    else:                                                                        # facing north or south: ridge along y
        C.prism(f'{name} gable', [(cx - width / 2, H0), (cx + width / 2, H0), (cx, H0 + rise * .92)], 'y', cy - depth / 2, cy + depth / 2, 'hut', 'chalets')
        for s in (-1, 1):
            plate(f'{name} roof {s:+d}', 'y', (cx + s * half, zeave), (cx, H0 + rise + .02), cy - depth / 2 - ov, cy + depth / 2 + ov)
    b = Batch()
    d = depth / 2 + .1                                                           # wreath plane just in front of the gable wall
    P = lambda u, z: (cx + fx * d + tx * u, cy + fy * d + ty * u, z)
    top = H0 + rise * .92 - .12
    zr = H0 + rise + .02
    under = lambda u: zr + (zeave - zr) * abs(u) / half - .14                  # underside of the snow plate
    dg = depth / 2 + ov - .1                                                     # rake garland hung under the front edge of the roof
    Q = lambda u, z: (cx + fx * dg + tx * u, cy + fy * dg + ty * u, z)
    for s in (-1, 1):
        u0, u1 = s * (half - .15), s * .12
        b.beam('planting', Q(u0, under(u0) - .1), Q(u1, under(u1) - .1), .16, .16, ext=0.0)
        for i in range(1, 7):
            u = u0 + (u1 - u0) * i / 7
            b.box('pale', *Q(u, under(u) - .22), .07, .07, .07)
    wz = H0 + .42
    for i in range(10):                                                          # wreath in the gable
        a0, a1 = 2 * math.pi * i / 10, 2 * math.pi * (i + 1) / 10
        b.beam('planting', P(.28 * math.cos(a0), wz + .28 * math.sin(a0)), P(.28 * math.cos(a1), wz + .28 * math.sin(a1)), .1 + .012 * (i % 2), .1 + .012 * (i % 2), ext=0.0)
    b.box('flower', *P(0.0, wz - .3), .16, .16, .16)
    bx, by, bz = Q(0.0, under(0.0) - .14)
    b.box('flower', bx, by, bz, .34 if abs(tx) > .5 else .14, .14 if abs(tx) > .5 else .34, .2)     # bow at the apex
    # Outward faces trimmed like the front: a garland with lights under the rear rakes and a red bow at the rear
    # apex, and a garland with lights along both outer eaves, so every chalet reads decorated from the lanes.
    R = lambda u, z: (cx - fx * dg + tx * u, cy - fy * dg + ty * u, z)
    for s in (-1, 1):
        u0, u1 = s * (half - .15), s * .12
        b.beam('planting', R(u0, under(u0) - .1), R(u1, under(u1) - .1), .16 + .01, .16, ext=0.0)
        for i in range(1, 6):
            u = u0 + (u1 - u0) * i / 6
            b.box('pale', *R(u, under(u) - .22), .07, .07, .07)
        ue = s * (half - .22)                                                    # eave garland just inside the eave edge
        ze = under(ue) - .1
        ea = depth / 2 + ov - .3
        b.beam('planting', (cx - fx * ea + tx * ue, cy - fy * ea + ty * ue, ze), (cx + fx * ea + tx * ue, cy + fy * ea + ty * ue, ze), .15, .15, ext=0.0)
        for i in range(5):
            e = -ea + 2 * ea * (i + .5) / 5
            b.box('pale', cx + fx * e + tx * ue, cy + fy * e + ty * ue, ze - .12, .07, .07, .07)
    rx, ry, rz = R(0.0, under(0.0) - .14)
    b.box('flower', rx, ry, rz, .34 if abs(tx) > .5 else .14, .14 if abs(tx) > .5 else .34, .2)     # red bow at the rear apex
    da = depth / 2 + .93                                                         # garland along the awning's front edge
    b.beam('planting', (cx + fx * da - tx * (width / 2 - .75), cy + fy * da - ty * (width / 2 - .75), 2.1),
           (cx + fx * da + tx * (width / 2 - .75), cy + fy * da + ty * (width / 2 - .75), 2.1), .14, .14)
    L = depth + 2 * ov                                                           # dark timber ridge board: the ridge reads from above
    b.beam('timber', (cx - fx * L / 2, cy - fy * L / 2, zr + .02), (cx + fx * L / 2, cy + fy * L / 2, zr + .02), .14, .1)
    b.flush(f'{name} garlands')
    C.qa_room_light(f'{name} light', (cx - fx * .6, cy - fy * .6, 2.0), 20, 1.0)


def chalets():
    # Free-standing huts: roof widths 4.3 m and 4.9 m on 5.3 m and 6.0 m centres leave about 1 m of setts between eaves.
    for i, x in enumerate((-7.95, -2.65, 2.65, 7.95)):
        chalet(f'North chalet {i}', x, DY + 2.1, (0, -1), width=3.6)
        chalet(f'South chalet {i}', x, -DY - 2.1, (0, 1), width=3.6)
    for i, y in enumerate((-15.0, -9.0, -3.0, 3.0, 9.0, 15.0)):
        chalet(f'West chalet {i}', -DX - 2.1, y, (1, 0), width=4.2)
        chalet(f'East chalet {i}', DX + 2.1, y, (-1, 0), width=4.2)


FW, FN, FS = 26.8, 32.5, -47.0                                                 # context fronts: lanes about 6 m wide round the market


def square():
    ys0, ys1 = FS + 3.0, FN - 3.0
    C.box('Square setts', (0, (ys0 + ys1) / 2, .02), (2 * FW, ys1 - ys0, .04), 'setts', 'site', 0)
    b = Batch()
    V, Fj = b.g.setdefault('joint', ([], []))

    def quad(x0, y0, x1, y1):
        o = len(V)
        V.extend([(x0, y0, .041), (x1, y0, .041), (x1, y1, .041), (x0, y1, .041)])
        Fj.append((o, o + 1, o + 2, o + 3))
    CW, SL = .35, .6                                                             # sett course width and length
    for k in range(int((ys1 - ys0) / CW)):                                      # coursed setts: bed joints and staggered cross joints
        y = ys0 + k * CW
        spans = [(-FW + 3.05, FW - 3.05)] if abs(y + CW / 2) > DY + .05 else [(-FW + 3.05, -DX - .05), (DX + .05, FW - 3.05)]
        for (xa, xb) in spans:
            quad(xa, y + CW - .015, xb, y + CW + .015)
            x = xa + (SL / 2) * (k % 2) + SL
            while x < xb - .1:
                quad(x - .014, y + .02, x + .014, y + CW - .02)
                x += SL
    for x, y in ((-DX - 4.2, -DY - 4.2), (DX + 4.2, -DY - 4.2), (-DX - 4.2, DY + 4.2), (DX + 4.2, DY + 4.2)):
        b.box('hardware', x, y, 2.2, .14, .14, 4.4)
        b.box('pale', x, y, 4.6, .36, .36, .4)
        b.box('hardware', x, y, 4.85, .46, .46, .1)
    b.flush('square furniture')
    # Old town fronts close round the square, as context: framed windows with sills, ground-floor doors.
    yl = (FS + 3.0 + FN - 3.0) / 2
    for name, cx, cy, sx, sy, h, role, facing in (('North front', 0.0, FN, 2 * FW + 6.0, 6.0, 15.0, 'facade3', (0, -1)),
                                                 ('West front', -FW, yl, 6.0, FN - FS - 6.0, 11.0, 'facade2', (1, 0)),
                                                 ('East front', FW, yl, 6.0, FN - FS - 6.0, 14.0, 'facade', (-1, 0)),
                                                 ('South front', 0.0, FS, 2 * FW + 6.0, 6.0, 12.5, 'facade', (0, 1))):
        C.box(name, (cx, cy, h / 2), (sx, sy, h), role, 'context', 0)
        if facing[1]:
            C.prism(f'{name} roof', [(cy - sy / 2 - .3, h), (cy + sy / 2 + .3, h), (cy, h + 3.5)], 'x', cx - sx / 2, cx + sx / 2, 'troof', 'context')
        else:
            C.prism(f'{name} roof', [(cx - sx / 2 - .3, h), (cx + sx / 2 + .3, h), (cx, h + 3.5)], 'y', cy - sy / 2, cy + sy / 2, 'troof', 'context')
        b = Batch()
        fx, fy = facing
        span = sx if fy else sy
        face = (cx + fx * sx / 2, cy + fy * sy / 2)                              # the front plane, facing the square
        tx, ty = -fy, fx

        def put(role, u, d, z, w, t, hh):
            x, y = face[0] + tx * u + fx * d, face[1] + ty * u + fy * d
            b.box(role, x, y, z, w if abs(tx) > .5 else t, t if abs(tx) > .5 else w, hh)
        n = int((span - 3.0) / 3.0)
        for i in range(n):
            u = -span / 2 + 3.0 + i * 3.0
            if i % 4 == 1:                                                       # a door every fourth bay
                put('timber', u, .03, 1.3, 1.2, .06, 2.6)
                put('trim', u, .05, 2.7, 1.5, .1, .14)
            for zl in range(int((h - 3.3) / 3.2) + 1):              # window rows up to the eaves on every front
                zz = 1.4 + zl * 3.2
                if zl == 0 and i % 4 == 1:
                    continue
                put('dark', u, .01, zz + .9, 1.0, .02, 1.6)
                for sgn in (-1, 1):
                    put('trim', u + sgn * .56, .05, zz + .9, .12, .1, 1.6)                # jambs stop under the head: no shared faces
                put('trim', u, .05, zz + 1.76, 1.24, .1, .12)
                put('trim', u, .09, zz + .03, 1.36, .18, .1)                   # sill
        b.flush(f'{name} windows')


def build():
    square()
    ice_and_boards()
    chalets()
    C.CONTACTS.append(dict(name='Ice rink with tree island and market chalets on a cobbled square', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(35, -45, 40), fill=(-40, -25, 30), rear=(-20, 40, 30), target=(0, 0, 2.0), gain=3.0)
