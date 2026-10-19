"""Tied-arch shared cycle and pedestrian bridge, authored from the locked catalogue views of
shared_cycle_pedestrian_bridge / variant_1 (Steel Arch Suspended Deck).

Read from the pixels (the top view governs the plan): a single-span bowstring bridge crossing a city canal between
brick-paved quays, its axis running west-east (the top view shows it slightly skewed; the model keeps it square to
the canal). Two silver-grey box-section steel arches spring from the deck edges at both quays and lean in towards
each other, joined near the crown by a row of straight cross ties; slim vertical hangers carry the deck edges. The
wide deck carries, north to south, a red cycle lane, a raised concrete planter of grasses and low shrubs, and a broad
pale footway, with steel picket railings on both edge ties. Brick apartment blocks stand on the quays and on a pier
in the canal; warehouse sheds and more blocks beyond as context.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-tied-arch-shared-bridge'
L = 44.0                                        # span between the arch springings
X0, X1, Y0, Y1 = -26.0, 26.0, -6.6, 6.6        # deck with its quay landings
ZQ = 2.6                                        # quay and deck level above the water
RISE = 10.0                                     # arch crown above the springing
HW = 6.15                                       # half-width to the edge-tie centre lines (arch springing)
LEAN = 1.1                                      # each arch leans in this far at the crown
CW = 20.0                                       # half-width of the canal
T = .3
EPS = .002
PALETTE = dict(water=(.14, .20, .22), arch=(.64, .68, .72), steel=(.48, .52, .56), hardware=(.22, .23, .25),
    red=(.50, .20, .16), path=(.74, .73, .70), concrete=(.48, .49, .50), planting=(.30, .42, .20),
    grass=(.50, .56, .30), straw=(.68, .58, .36), shrub=(.24, .36, .16), flower=(.62, .30, .22),
    rail=(.56, .58, .60), paving=(.52, .32, .26), quay=(.46, .30, .24), brick=(.56, .34, .26),
    brick2=(.70, .58, .44), dark=(.16, .17, .19), white=(.95, .95, .93), pale=(.88, .88, .86),
    roof=(.42, .42, .42), glass=(.24, .30, .34), wall=(.56, .34, .26), trim=(.92, .92, .90),
    interior=(.84, .80, .74), floor=(.58, .48, .38), stone=(.70, .64, .54), timber=(.46, .34, .22),
    tree=(.26, .42, .18), soil=(.30, .25, .18), sand=(.70, .66, .58), asphalt=(.30, .30, .31), blue=(.20, .30, .40))


def manifest(version):
    h = ZQ + RISE + 1.0
    cams = G.camera_roster(X1 - X0 + 6.0, Y1 - Y0 + 20.0, h, [
        ('facade_close', (2.0, -21.0, 3.0), (0.0, 0.0, ZQ + 3.4), 26),
        ('architecture_close', (-7.0, -17.0, ZQ + 13.0), (0.0, -4.0, ZQ + RISE - 1.0), 35),
        ('glass_close', (-8.0, -3.6, ZQ + 1.6), (-3.5, -6.2, ZQ + .8), 40),
        ('arch_springing', (-29.0, -13.0, ZQ + 2.4), (-L / 2, -HW, ZQ + 1.2), 40),
        ('hangers', (-15.0, -3.2, ZQ + 1.7), (10.0, -6.3, ZQ + 4.5), 35),
        ('planter_divider', (-15.0, 3.6, ZQ + 1.8), (-4.0, 1.4, ZQ + .5), 40),
        ('cycle_lane', (-21.0, 4.2, ZQ + 1.6), (10.0, 4.0, ZQ + .5), 35),
        ('deck_edge', (-9.0, -14.0, ZQ - .4), (-2.0, -6.3, ZQ - .5), 35),
        ('quay_under', (-11.0, -15.0, 1.3), (-CW, 0.0, 1.4), 35),
        ('rear_north', (2.0, 40.0, ZQ + 8.0), (0.0, 0.0, ZQ + 3.5), 35)])
    for c in cams:                       # the locked front stands on the west quay looking east along the deck
        if c['name'] == 'front':
            c.update(location=(-27.5, 1.2, ZQ + 1.7), target=(0.0, -1.5, ZQ + 3.6), lens=24, whole=False)
        elif c['name'] == 'front_corner':                                      # the locked oblique: high in the south-west
            c.update(location=(-30.0, -44.0, 30.0), target=(2.0, 1.0, ZQ + 3.0), lens=32, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(30.0, -40.0, 36.0), target=(0.0, 0.0, ZQ + 2.0), lens=35, whole=False)
        elif c['name'] == 'top':
            c.update(location=(0.0, -2.0, 90.0), target=(0.0, -1.999, 0.0), ortho_scale=62.0, whole=False)
        elif c['name'] == 'left_side':
            c.update(location=(-62.0, -2.0, 15.0), target=(0.0, 0.0, ZQ + 4.0), lens=35, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(62.0, -10.0, 12.0), target=(0.0, 0.0, ZQ + 4.0), lens=35, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(4.0, 46.0, 9.0), target=(0.0, 0.0, ZQ + 4.0), lens=35, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(10.0, 50.0, 34.0), target=(0.0, 0.0, ZQ + 3.0), lens=35, whole=False)   # over the canal, clear of the blocks
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='shared_cycle_pedestrian_bridge/variant_1 (Steel Arch Suspended Deck)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=0, storey_programme='street option: a tied-arch cycle and pedestrian bridge over a canal; the quays and blocks are context',
            plan='44 m span between quays across a 40 m canal (top view), 12.8 m deck: 3.6 m red cycle lane, 1.7 m raised planter, 6.5 m footway, edge ties',
            section_m=dict(cycle_lane=[2.3, 5.9], planter=[.6, 2.3], footway=[-5.9, .6], edge_ties=[5.9, 6.4], deck_level=ZQ, water=0.0),
            facade='silver-grey box arches leaning inward with cross ties, slim hangers, edge-tie girders, red cycle lane, planter of grasses and shrubs, pale footway, picket railings, brick quays',
            levels_m=[0.0, ZQ, ZQ + RISE], inferred='the deck structure, the canal width away from the bridge and the blocks are teaching assumptions; the skew in the top view is not modelled'),
        roof_contract=dict(type='open street option; no roof', datum_m=ZQ, crowns_m=[ZQ + RISE]),
        identity_contract=dict(owner='twin inclined steel tied arches with hangers over a canal, red cycle lane and pale footway split by a raised planter'),
        material_contract=dict(profile='source-palette clay: silver-grey steel, red cycle surface, pale concrete footway, green and straw grasses, grey planter, brick quays, dark canal water', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='cycle lane, footway, planter'),
        street_contract=dict(kind='fixed_native_section', width_m=Y1 - Y0, axis='x', junction_finish='pavers',
                             bands=['edge_tie', 'cycle_lane', 'planter', 'footway', 'edge_tie']),
        contact_contract=['Canal surface at grade zero', 'Quay walls from grade', 'Arch springings on abutments at the quays',
                          'Deck hung from the arches and landing on the quays', 'Blocks on the quays and a pier'],
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
# ---- Tied-arch shared cycle and pedestrian bridge ----

import random

RNG = random.Random(4417)                       # fixed seed: the same planting and trees on every build

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


def tuft(b, role, cx, cy, z0, h, r, n=4):
    """A clump of grass: a narrow leaning cone."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for i in range(n):
        a = 2 * math.pi * (i + RNG.random() * .3) / n
        V.append((cx + r * math.cos(a), cy + r * math.sin(a), z0))
    V.append((cx + RNG.uniform(-.1, .1), cy + RNG.uniform(-.1, .1), z0 + h))
    F.append(tuple(o + i for i in range(n - 1, -1, -1)))
    for i in range(n):
        F.append((o + i, o + (i + 1) % n, o + n))


def arch_pt(x, s):
    """Centre line of arch s (-1 south, +1 north): a parabola in a plane leaning in towards the deck axis."""
    f = 1 - (2 * x / L) ** 2
    return (x, s * (HW - LEAN * f), ZQ + .25 + RISE * f)


def railing(b, y, x0, x1, z, post=1.5, picket=.15):
    """Steel picket railing with a flat steel cap along the deck edge."""
    b.box('rail', (x0 + x1) / 2, y, z + 1.17, x1 - x0, .1, .06)
    b.box('rail', (x0 + x1) / 2, y, z + .1, x1 - x0, .05, .05)
    n = int((x1 - x0) / post)
    for i in range(n + 1):
        b.box('rail', x0 + (x1 - x0) * i / n, y, z + .58, .07, .07, 1.16)
    k = int((x1 - x0) / picket)
    for i in range(1, k):
        x = x0 + (x1 - x0) * i / k
        b.box('rail', x, y, z + .62, .02, .02, 1.0)


def canal_and_quays():
    C.box('Canal', (0.0, 0.0, .01), (2 * CW, 120.0, .02), 'water', 'canal', 0)
    b = Batch()
    for s in (-1, 1):
        for x0, x1, y0, y1 in ((CW + 4.5, CW + 50.0, -60.0, 60.0), (CW, CW + 4.5, -60.0, -6.45), (CW, CW + 4.5, 6.45, 60.0)):
            xc, yc = s * (x0 + x1) / 2, (y0 + y1) / 2                                         # quay fill and brick paving, cut round the deck end
            b.box('quay', xc, yc, (ZQ - .06) / 2, x1 - x0, y1 - y0, ZQ - .06)
            b.box('paving', xc, yc, ZQ - .03, x1 - x0, y1 - y0, .06)
        b.box('quay', s * (CW + 2.25), 0.0, (ZQ - 1.02) / 2, 4.5, 12.9, ZQ - 1.02)              # quay wall and bearing under the deck end
        for y0, y1 in ((-60.0, -6.8), (6.8, 60.0)):                                          # stone coping at the quay edge
            b.box('stone', s * (CW + .25), (y0 + y1) / 2, ZQ + .02, .7, y1 - y0, .14)
        for k in range(14):                                                                   # lamps along the quays
            y = -52.0 + k * 8.0
            if abs(y) < 9.0:
                continue
            b.box('dark', s * (CW + 1.6), y, ZQ + 2.2, .12, .12, 4.4)
            b.box('pale', s * (CW + 1.6), y, ZQ + 4.5, .28, .28, .3)
    for k in range(40):                                                                       # paving course lines on the west street
        b.box('quay', -CW - 9.0, -58.0 + k * 3.0, ZQ + .004, 9.0, .05, .01)
    b.flush('quays')


def deck():
    xa, xb = -CW - 4.5, CW + 4.5                                                             # the deck lands 4.5 m onto each quay
    b = Batch()
    b.box('steel', 0.0, 0.0, ZQ - .675, xb - xa, 11.8, .65)                                   # deck plate, underside
    for s in (-1, 1):
        b.box('arch', 0.0, s * 6.15, ZQ - .425, xb - xa, .5, 1.35)                            # edge ties (the bowstring)
    b.box('red', 0.0, 4.1, ZQ - .18, xb - xa, 3.6, .36)                                      # cycle lane, top at ZQ
    b.box('path', 0.0, -2.65, ZQ - .18, xb - xa, 6.5, .36)                                    # footway, top at ZQ
    for x0, x1 in ((xa, -21.5), (21.5, xb)):                                                  # footway over the planter line at the ends
        b.box('path', (x0 + x1) / 2, 1.45, ZQ - .18, x1 - x0, 1.7, .36)
    for s in (-1, 1):                                                                         # planter: long walls, end walls, soil
        b.box('concrete', 0.0, .675 if s < 0 else 2.225, ZQ + .095, 43.0, .15, .91)
        b.box('concrete', s * 21.425, 1.45, ZQ + .095, .15, 1.4, .91)
    b.box('planting', 0.0, 1.45, ZQ + .18, 42.7, 1.4, .54)                                   # soil, top ZQ + .45
    for k in range(15):                                                                       # cycle lane centre dashes
        b.box('white', -21.0 + k * 3.0, 4.1, ZQ + .002, 1.2, .12, .012)
    for x in (-23.0, 23.0):                                                                   # cycle symbols as pale lozenges near the ends
        b.box('white', x, 4.1, ZQ + .002, .9, .5, .012)
    b.flush('deck')
    b = Batch()
    for s in (-1, 1):
        railing(b, s * 5.95, -L / 2 + 1.2, L / 2 - 1.2, ZQ + .25)
    b.flush('railings')


def arches():
    b = Batch()
    n = 30
    for s in (-1, 1):
        pts = [arch_pt(-L / 2 + L * i / n, s) for i in range(n + 1)]
        for p, q in zip(pts, pts[1:]):
            b.beam('arch', p, q, .9, 1.1, ext=.04)
        for x in (-12.0, -6.0, 0.0, 6.0, 12.0):                                               # straight cross ties near the crown
            if s > 0:
                p, q = arch_pt(x, 1), arch_pt(x, -1)
                b.box('arch', x, 0.0, p[2] - .05, .45, abs(p[1] - q[1]), .55)
        for k in range(13):                                                                   # vertical hangers to the edge ties
            x = -18.0 + k * 3.0
            p = arch_pt(x, s)
            b.beam('hardware', (x, p[1], p[2] - .5), (x, s * 6.3, ZQ + .25), .06, .06)
    for sx in (-1, 1):                                                                        # concrete abutments under the springings
        for s in (-1, 1):
            b.box('concrete', sx * 22.4, s * 6.15, ZQ - .2, 2.4, 1.7, 1.2 + .02 * (s > 0))
            b.box('concrete', sx * 22.4, s * 6.15, (ZQ - .8) / 2, 2.0, 1.4, ZQ - .8)
    b.flush('arches')


def planter():
    b = Batch()
    z = ZQ + .45
    x = -21.0
    while x < 21.0:
        blob(b, RNG.choice(('shrub', 'planting', 'shrub', 'grass')), x, 1.45 + RNG.uniform(-.2, .2), z + .2, RNG.uniform(.4, .55), RNG.uniform(.38, .5), RNG.uniform(.25, .36))
        for k in range(3):                                                                    # soft mounded grasses, not spikes
            tuft(b, RNG.choice(('grass', 'straw', 'straw')), x + RNG.uniform(-.35, .35), 1.45 + RNG.uniform(-.45, .45), z, RNG.uniform(.4, .7), RNG.uniform(.2, .3), n=5)
        if RNG.random() < .3:
            blob(b, 'flower', x + RNG.uniform(-.3, .3), 1.45 + RNG.uniform(-.4, .4), z + .12, .3, .25, .14)
        x += RNG.uniform(.5, .75)
    b.flush('planter')


def tree(b, x, y, z, h=8.0, s=1.0):
    b.box('timber', x, y, z + h * .28, .3 * s, .3 * s, h * .56)
    for dx, dy, dz, r in ((0, 0, .72, 2.4), (-1.2, .5, .64, 1.7), (1.2, -.6, .62, 1.8), (.1, .2, .86, 1.6)):
        blob(b, 'tree', x + dx * s, y + dy * s, z + h * dz, r * s, r * s, r * .85 * s)


def context():
    b = Batch()
    for x0, y0, x1, y1, h, role in ((-50.0, 10.0, -26.0, 34.0, 22.0, 'brick2'), (-12.0, -46.0, 12.0, -24.0, 12.0 + ZQ, 'brick'),
                                    (26.0, -40.0, 46.0, -14.0, 18.0, 'brick'), (28.0, 16.0, 56.0, 40.0, 28.0, 'brick'),
                                    (-56.0, -40.0, -30.0, -14.0, 16.0, 'brick2')):
        zb = 0.0 if x0 > -CW and x1 < CW else ZQ - .02
        top = zb + h
        b.box(role, (x0 + x1) / 2, (y0 + y1) / 2, (zb + top) / 2, x1 - x0, y1 - y0, top - zb)
        b.box('roof', (x0 + x1) / 2, (y0 + y1) / 2, top + .1, x1 - x0 - .6, y1 - y0 - .6, .2)
        for k in range(int((top - zb - 3.0) / 3.1)):                                         # window bands toward the bridge
            z = zb + 2.0 + k * 3.1
            yf = y0 - .03 if y0 > 0 else y1 + .03
            b.box('dark', (x0 + x1) / 2, yf, z, x1 - x0 - 1.2, .06, 1.5)
            xf = x0 - .03 if x0 > 0 else x1 + .03
            if not (x0 > -CW and x1 < CW):
                b.box('dark', xf, (y0 + y1) / 2, z, .06, y1 - y0 - 1.2, 1.5)
    for y in (-30.0, -18.0, 14.0, 24.0, 40.0, 50.0):                                          # street trees on the west quay
        tree(b, -CW - 3.6, y, ZQ, RNG.uniform(7.0, 9.0), .8)
    b.flush('context')
    pitched_roof('Warehouse sheds roof', 30.0, 70.0, 46.0, 60.0, ZQ + 7.0, 3.0, hip_w=False, hip_e=False, axis='x', ov=.3, role='roof', module='context')
    C.box('Warehouse sheds', (50.0, 53.0, (ZQ + 7.0 + ZQ - .02) / 2), (40.0, 14.0, 7.02), 'brick', 'context', 0)


def build():
    canal_and_quays()
    deck()
    arches()
    planter()
    context()
    C.CONTACTS.append(dict(name='Tied-arch bridge: deck hung from two leaning arches, springings on quay abutments, canal between brick quays', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(35, -45, 45), fill=(-40, -25, 30), rear=(-20, 40, 30), target=(0.0, 0.0, 4.0), gain=3.2)
