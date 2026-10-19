"""Timber covered footbridge, authored from the locked catalogue views of
urban_pedestrian_footbridge / variant_2 (Timber-Clad Covered Bridge).

Read from the pixels (the top view governs the plan): a contemporary covered footbridge running east-west over a
north-south stream between apartment blocks. Glulam portal frames at a regular pitch with knee braces under the tie
beams, diagonal glulam braces in the side bays, vertical timber louvres filling the two end bays and an upper band
of the middle bays, a thin glass balustrade along the open middle bays, a timber deck on deep glulam edge beams,
and a low-pitched standing-seam zinc roof with deep eaves and hipped ends. The deck runs out beyond the roof at both
ends onto stone-paved upper promenades with grey bar railings. Two round concrete piers with headstocks stand on
lower riverside paths at the water's edge; planted banks slope from the lower paths up to the promenades; brick
apartment blocks and trees as context.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-timber-covered-footbridge'
X0, X1, Y0, Y1 = -24.0, 24.0, -24.0, 24.0      # the bridge, the stream, its paths and banks
WX = 6.5                                        # half-width of the stream
LOWX, BANKX = 10.0, 12.5                        # lower riverside path to here; planted bank up to the promenade
LOW, UP = .6, 3.4                               # lower path and upper promenade levels above the water
ZD = UP + .05                                   # deck top
DX = 15.5                                       # deck half-length
RX = 13.0                                       # outermost frames
EAVE = ZD + 3.3
T = .3
EPS = .002
PALETTE = dict(water=(.16, .22, .20), timber=(.62, .42, .22), glulam=(.66, .45, .24), deck=(.58, .40, .22),
    roof=(.30, .32, .34), seam=(.24, .26, .28), concrete=(.68, .67, .64), paving=(.52, .50, .47), joint=(.40, .39, .37),
    stone=(.58, .56, .52), glass=(.62, .70, .72), hardware=(.30, .31, .32), planting=(.30, .44, .20), tree=(.28, .44, .18),
    grass=(.42, .52, .26), soil=(.30, .25, .18), brick=(.62, .38, .28), trim=(.86, .84, .80), wall=(.62, .38, .28),
    interior=(.84, .80, .74), floor=(.58, .48, .38), pale=(.88, .88, .86), white=(.95, .95, .93), sand=(.70, .66, .58),
    asphalt=(.30, .30, .31), blue=(.20, .30, .40), pot=(.60, .34, .22))


def manifest(version):
    h = EAVE + .8
    cams = G.camera_roster(X1 - X0, Y1 - Y0, h, [
        ('facade_close', (2.0, -15.0, ZD + 1.2), (2.0, -2.0, ZD + 1.8), 40),
        ('architecture_close', (-17.5, -4.5, ZD + 1.7), (-13.0, 0.0, ZD + 2.2), 35),
        ('glass_close', (-4.0, 1.0, ZD + 1.5), (-2.0, -2.1, ZD + .8), 35),
        ('portal_end', (-21.5, -.6, ZD + 1.7), (-13.0, 0.0, ZD + 1.9), 35),
        ('louvre_wall', (-10.6, -5.6, ZD + 1.6), (-11.7, -2.2, ZD + 1.8), 40),
        ('roof_eaves', (4.0, -9.0, ZD + 6.0), (2.0, -2.6, EAVE), 40),
        ('deck_inside', (-12.0, .2, ZD + 1.6), (6.0, 0.0, ZD + 1.0), 28),
        ('pier_abutment', (8.6, -10.5, LOW + 1.6), (9.4, 0.0, 2.1), 32),
        ('stream_under', (0.0, -14.0, 1.2), (0.0, 0.0, ZD - 1.4), 28),
        ('rear_north', (4.0, 22.0, ZD + 4.0), (0.0, 0.0, ZD + 1.5), 35)])
    for c in cams:                       # the locked front stands on the west promenade, south of the bridge
        if c['name'] == 'front':
            c.update(location=(-17.2, -7.8, ZD + 1.8), target=(-8.0, 1.5, ZD + 2.4), lens=22, whole=False)
        elif c['name'] == 'front_corner':                                      # the locked oblique: high in the south-west
            c.update(location=(-13.0, -23.0, 17.0), target=(2.0, 2.0, ZD + 1.0), lens=30, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(22.0, -26.0, 24.0), target=(0.0, 0.0, ZD), lens=32, whole=False)
        elif c['name'] == 'top':
            c.update(location=(0.0, 0.0, 70.0), target=(0.0, .001, 0.0), ortho_scale=46.0, whole=False)
        elif c['name'] == 'left_side':
            c.update(location=(-30.0, -3.0, ZD + 9.0), target=(0.0, 0.0, ZD + 1.0), lens=30, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(34.0, 4.0, ZD + 6.0), target=(0.0, 0.0, ZD + 1.5), lens=30, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(3.0, 30.0, ZD + 6.0), target=(0.0, 0.0, ZD + 1.0), lens=30, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(10.0, 30.0, 17.0), target=(0.0, 0.0, ZD), lens=30, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='urban_pedestrian_footbridge/variant_2 (Timber-Clad Covered Bridge)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=0, storey_programme='street option: a covered pedestrian footbridge over a stream; the blocks are context',
            plan='31 m timber deck (26 m under the roof) running east-west over a 13 m stream (top view), 4 m clear walk, piers on the lower paths',
            section_m=dict(stream=[-WX, WX], lower_path=[WX, LOWX], bank=[LOWX, BANKX], promenade=[BANKX, X1], deck_top=ZD, eave=EAVE),
            facade='glulam portal frames with knee braces and side diagonals, vertical timber louvres, glass balustrade, timber deck on glulam edge beams, standing-seam zinc roof with deep eaves and hipped ends, round concrete piers',
            levels_m=[0.0, LOW, UP, ZD, EAVE], inferred='the stream bed below the surface, the far ends of the paths and the blocks are context'),
        roof_contract=dict(type='low-pitched hipped standing-seam zinc roof over the frames', datum_m=EAVE, crowns_m=[h]),
        identity_contract=dict(owner='timber covered footbridge: glulam frames, vertical louvres and a grey standing-seam roof over a stream, concrete piers, stone-paved approaches'),
        material_contract=dict(profile='source-palette clay: warm glulam and louvres, timber deck, grey zinc roof, pale concrete piers, grey stone paving, dark green water, grey bar railings, planted banks, brick blocks', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='a covered walk over the stream; riverside paths beneath'),
        street_contract=dict(kind='fixed_native_section', width_m=2 * DX, axis='x', junction_finish='pavers',
                             bands=['promenade', 'bank', 'lower_path', 'stream', 'lower_path', 'bank', 'promenade']),
        contact_contract=['Stream surface at grade zero', 'Lower paths and banks from grade', 'Piers on the lower paths', 'Deck ends on the promenades'],
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
# ---- Timber covered footbridge ----

import random

RNG = random.Random(1911)                       # fixed seed: the same shrubs on every build
FRAMES = [-RX + 2.6 * i for i in range(11)]     # portal frames at a 2.6 m pitch
XA = 10.9                                       # abutment faces on the banks
XB = RX + .25                                   # edge beams run to here, seated on the abutments
ZR = ZD + 2.3                                   # rail under the louvre band of the middle bays


def cyl(b, role, cx, cy, z0, z1, r, n=20):
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


def tree(x, y, z, h=9.0, s=1.0):
    C.rod('Tree trunk', (x, y, z), (x + .2 * s, y + .1 * s, z + h * .5), .2 * s, 'timber', 'trees', 8)
    for i, (dx, dy, dz, r, rz) in enumerate(((0, 0, .72, 2.6, 2.2), (-1.4, .6, .62, 1.8, 1.6), (1.3, -.5, .6, 1.8, 1.5), (.2, .3, .88, 1.6, 1.3))):
        A.foliage(f'Tree crown {i}', (x + dx * s, y + dy * s, z + h * dz), (r * s, r * s, rz * s), role='tree', detail=2)


def ground():
    """The stream at grade zero, lower riverside paths, planted banks and the stone-paved upper promenades."""
    ya, yb = Y0 - 6.0, Y1 + 6.0
    C.box('Stream', (0.0, 0.0, .01), (2 * WX, yb - ya, .02), 'water', 'stream', 0)
    for s, side in ((-1, 'west'), (1, 'east')):
        C.box(f'Lower path {side}', (s * (WX + LOWX) / 2, 0.0, LOW / 2), (LOWX - WX, yb - ya, LOW), 'paving', 'paths', 0)
        pts = [(LOWX, 0.0), (BANKX, 0.0), (BANKX, UP), (LOWX, LOW)] if s > 0 else [(-BANKX, 0.0), (-LOWX, 0.0), (-LOWX, LOW), (-BANKX, UP)]
        C.prism(f'Planted bank {side}', pts, 'y', ya, yb, 'planting', 'banks')
        C.box(f'Promenade {side}', (s * (BANKX + X1 + 6.0) / 2, 0.0, UP / 2), (X1 + 6.0 - BANKX, yb - ya, UP), 'paving', 'promenades', 0)
    b = Batch()
    for s in (-1, 1):
        for k in range(int((yb - ya) / .6)):                                               # paving courses on the promenades
            y = ya + .3 + k * .6
            b.box('joint', s * (BANKX + X1 + 6.0) / 2, y, UP + .002, X1 + 6.0 - BANKX - .04, .025, .004)
        for k in range(int((X1 + 6.0 - BANKX) / 1.2)):
            b.box('joint', s * (BANKX + .6 + k * 1.2), 0.0, UP + .002, .025, yb - ya - .04, .004)
        for k in range(int((yb - ya) / .5)):                                               # and on the lower paths
            b.box('joint', s * (WX + LOWX) / 2, ya + .25 + k * .5, LOW + .002, LOWX - WX - .04, .025, .004)
    b.flush('paving joints')
    for i in range(36):                                                                     # shrubs and grasses on the banks
        s = -1 if i % 2 else 1
        x = s * RNG.uniform(LOWX + .4, BANKX - .4)
        y = RNG.uniform(Y0 + 1.0, Y1 - 1.0)
        if abs(y) < 3.2:
            continue
        zs = LOW + (UP - LOW) * (abs(x) - LOWX) / (BANKX - LOWX)
        A.foliage(f'Bank shrub {i}', (x, y, zs + .25), (RNG.uniform(.6, 1.0), RNG.uniform(.7, 1.2), RNG.uniform(.45, .7)), role='planting', detail=2)
    for i, (x, y, h) in enumerate(((-17.5, -12.0, 9.0), (21.5, -5.5, 8.5), (19.5, -20.0, 9.5), (-16.0, 17.0, 8.0), (-21.0, -19.0, 8.0), (-21.5, 6.5, 8.5))):
        tree(x, y, UP, h=h)


def railings():
    """Grey bar railings along the promenade edges (open where the deck lands) and along the water's edge."""
    b = Batch()
    for s in (-1, 1):
        x = s * (BANKX + .12)
        for ya, yb in ((Y0, -2.6), (2.6, Y1)):
            b.box('hardware', x, (ya + yb) / 2, UP + 1.1, .06, yb - ya, .05)
            b.box('hardware', x, (ya + yb) / 2, UP + .14, .05, yb - ya, .04)
            n = int((yb - ya) / 1.5)
            for i in range(n + 1):
                b.box('hardware', x, ya + (yb - ya) * i / n, UP + .56, .07, .07, 1.12)
            for i in range(int((yb - ya) / .24)):
                b.box('hardware', x, ya + .12 + i * .24, UP + .62, .02, .02, .92)
        x = s * (WX + .15)                                                                  # water's-edge rail on the lower paths
        b.box('hardware', x, 0.0, LOW + 1.05, .05, Y1 - Y0, .05)
        b.box('hardware', x, 0.0, LOW + .55, .035, Y1 - Y0, .035)
        for i in range(int((Y1 - Y0) / 2.0) + 1):
            b.box('hardware', x, Y0 + i * 2.0, LOW + .53, .06, .06, 1.06)
    b.flush('railings')


def bridge():
    # Deck: timber boards on cross joists between glulam edge beams seated on concrete abutments; beyond the roof the
    # boards run out onto the promenades as landings.
    C.box('Deck boards', (0.0, 0.0, ZD - .05), (2 * DX, 4.0, .1), 'deck', 'deck', 0)
    b = Batch()
    for k in range(int(2 * DX / .3)):
        b.box('joint', -DX + .15 + k * .3, 0.0, ZD + .002, .02, 3.98, .004)
    for s in (-1, 1):
        b.box('glulam', 0.0, s * 2.15, ZD - .16, 2 * XB, .3, .62)                             # straight edge beams, square ends
    for k in range(int(2 * XB / 1.3)):
        b.box('glulam', -XB + .65 + k * 1.3, 0.0, ZD - .28, .16, 4.0, .36)                    # cross joists
    b.flush('deck structure')
    # Portal frames: posts, tie beams with king posts, knee braces; wall plates stopping inside the end posts; a
    # ridge beam stopping short of the hips.
    b = Batch()
    for x in FRAMES:
        for s in (-1, 1):
            b.box('glulam', x, s * 2.15, (ZD + .14 + EAVE - .24) / 2, .26, .28, EAVE - .24 - ZD - .14)
            b.beam('glulam', (x, s * 2.04, EAVE - 1.35), (x, s * 1.15, EAVE - .2), .18, .14)
        b.box('glulam', x, 0.0, EAVE - .125, .24, 4.62, .25)
        b.box('glulam', x, 0.0, EAVE + .16, .18, .18, .32)
    for s in (-1, 1):
        b.box('glulam', 0.0, s * 2.15, EAVE - .4, 2 * RX - .04, .26, .2)
    b.box('glulam', 0.0, 0.0, EAVE + .43, 2 * (RX - .4), .2, .26)
    # Side frames by bay: the end bays filled with full-height louvres; the bay next to each portal carries one long
    # diagonal rising from the post foot on the portal side to the post head on the midspan side; the interior bays
    # are open, with knee braces at the post heads under a continuous rail. One layer of louvres fills the band
    # between that rail and the wall plate; a glass balustrade runs along the open bays and the landings.
    last = len(FRAMES) - 2
    for i in range(len(FRAMES) - 1):
        xa, xb = FRAMES[i], FRAMES[i + 1]
        end = i in (0, last)
        for s in (-1, 1):
            y = s * 2.15
            if i in (1, last - 1):
                p, q = (xa + .16, y, ZD + .3), (xb - .16, y, EAVE - .55)
                if i == last - 1:
                    p, q = (xb - .16, y, ZD + .3), (xa + .16, y, EAVE - .55)
                b.beam('glulam', p, q, .2, .26)
            elif not end:
                for xp, d in ((xa, 1), (xb, -1)):
                    b.beam('glulam', (xp + d * .1, y, ZR - .85), (xp + d * .85, y, ZR - .06), .14, .16)
            z0 = ZD + .16 if end else ZR + .08
            pitch = .19 if end else .2
            n = int((xb - xa - .3) / pitch)
            for k in range(n):
                b.box('timber', xa + .15 + (xb - xa - .3) * (k + .5) / n, y, (z0 + EAVE - .5) / 2, .06, .14, EAVE - .5 - z0)
            if end:
                b.box('glulam', (xa + xb) / 2, y, ZD + .2, xb - xa - .2, .2, .12)             # bottom rail of the end-bay louvres
        if not end:
            for s in (-1, 1):
                b.box('glulam', (xa + xb) / 2, s * 2.15, ZR, xb - xa - .2, .22, .16)          # rail under the louvre band
    for s in (-1, 1):
        b.box('glass', 0.0, s * 1.98, ZD + .64, FRAMES[-2] - FRAMES[1] - .3, .02, .96)
        b.box('hardware', 0.0, s * 1.98, ZD + 1.14, FRAMES[-2] - FRAMES[1] - .3, .05, .04)
        for sx in (-1, 1):
            xa, xb = sx * (RX + .2), sx * (DX - .05)
            b.box('glass', (xa + xb) / 2, s * 1.95, ZD + .5, abs(xb - xa), .02, 1.0)            # on the landing boards
            b.box('hardware', (xa + xb) / 2, s * 1.95, ZD + 1.02, abs(xb - xa), .05, .04)
    b.flush('frames')
    # Low-pitched hipped standing-seam zinc roof with deep eaves.
    ex, ey, rx = RX + .9, 2.8, RX - .3
    z_lo, z_hi = EAVE + .05, EAVE + .75
    strip('Zinc roof', [(-ex, -ey), (ex, -ey), (ex, ey), (-ex, ey)], [(-rx, -.02), (rx, -.02), (rx, .02), (-rx, .02)], z_lo, z_hi, 'roof', 'roof')
    b = Batch()
    zs = lambda y: z_lo + (z_hi - z_lo) * (ey - abs(y)) / (ey - .02)
    k = 0
    x = -rx + .3
    while x < rx - .2:
        for s in (-1, 1):
            b.beam('seam', (x, s * .06, zs(.06) + .025), (x, s * (ey - .02), zs(ey - .02) + .025), .03, .05)
        x += .55
    b.beam('seam', (-rx, 0.0, z_hi + .02), (rx, 0.0, z_hi + .02), .16, .06)
    b.flush('roof seams')
    for sx in (-1, 1):                          # boarded gable triangles under the hipped ends, kept below the roof sheet
        C.prism(f'End gable board {sx:+d}', [(-2.31, EAVE - .01), (2.31, EAVE - .01), (0.0, EAVE + .28)], 'x', sx * RX - .12, sx * RX + .12, 'timber', 'roof')
    # Concrete abutments cut into the banks: the edge beams and joists bear on their seats, the planted slope meets
    # their faces, and the paved promenade closes over their backs.
    for sx in (-1, 1):
        C.box(f'Abutment {sx:+d}', (sx * (XA + BANKX) / 2, 0.0, (LOW + ZD - .47) / 2), (BANKX - XA, 5.8, ZD - .47 - LOW), 'concrete', 'abutments', 0)
        C.box(f'Abutment cill {sx:+d}', (sx * (XA + .1), 0.0, ZD - .52), (.3, 5.9, .06), 'concrete', 'abutments', 0)
    # Round concrete piers on the lower paths, each with a concentric tapered headstock under the edge beams.
    b = Batch()
    for s in (-1, 1):
        cyl(b, 'concrete', s * 8.0, 0.0, LOW, ZD - 1.25, 1.0, 24)
    b.flush('piers')
    for s in (-1, 1):
        C.prism(f'Pier headstock {s:+d}', [(-1.0, ZD - 1.35), (1.0, ZD - 1.35), (2.45, ZD - .85), (2.45, ZD - .47), (-2.45, ZD - .47), (-2.45, ZD - .85)],
                'x', s * 8.0 - 1.0, s * 8.0 + 1.0, 'concrete', 'piers')


def block(name, xf, facing, y0, y1, top, nf, depth=12.0):
    """Brick apartment block as context: the face toward the stream with real cuts and balconies, a body behind."""
    if facing < 0:                                                                          # the face looks west (-x)
        f = C.Face((xf, 0, 0), (0, -1, 0), (1, 0, 0), name)
        lo, hi = -y1, -y0
        bx = xf + T + (depth - T) / 2
    else:                                                                                   # the face looks east (+x)
        f = C.Face((xf, 0, 0), (0, 1, 0), (-1, 0, 0), name)
        lo, hi = y0, y1
        bx = xf - T - (depth - T) / 2
    n = int((hi - lo) / 3.0)
    hs = []
    for k in range(nf):
        for j in range(n):
            u = lo + 1.5 + j * 3.0
            hs.append(hole(f'{name} window f{k} {j}', u, UP + .9 + k * 3.0, 1.4, 1.7) if k else hole(f'{name} door {j}', u, UP + .05, 1.4, 2.3, kind='patio door'))
    f.wall(f'{name} wall', lo, hi - EPS, 0.0, top, depth=T, role='brick', holes=hs)
    G.brick_courses(f, lo + .02, hi - .02, UP + .1, top - .1, hs, spacing=.6)
    m = Merge(f)
    for h in hs:
        framed(m, f, h, cols=2, rows=1 if h['h'] < 2 else 2, inset=.14, occupied='flat', kind='door' if h.get('kind') else 'window', lite=True)
    for k in range(1, nf):
        z = UP + k * 3.0 + .1
        for j in range(0, n, 2):
            u = lo + 1.5 + j * 3.0
            m.box('trim', u, -.7, z, 2.4, 1.4, .16)
            m.box('glass', u, -1.38, z + .55, 2.4, .03, .9)
    m.box('trim', (lo + hi) / 2, -.06, top - .1, hi - lo + .1, .14, .2)
    m.flush(name)
    C.box(f'{name} body', (bx, (y0 + y1) / 2, top / 2), (depth - T, y1 - y0, top), 'brick', 'blocks', 0)
    C.qa_room_light(f'{name} rooms', (xf + facing * -3.0, (y0 + y1) / 2, UP + 2.0), 60, 4.0)


def build():
    ground()
    railings()
    bridge()
    block('North-east block', 16.0, -1, 8.0, 32.0, UP + 13.0, 4)
    block('South-west block', -17.0, 1, -32.0, -13.0, UP + 10.0, 3)
    block('North-west block', -19.0, 1, 12.0, 30.0, UP + 10.0, 3)
    C.CONTACTS.append(dict(name='Covered timber footbridge over a stream: piers on the lower paths, deck ends on the promenades', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(30, -45, 40), fill=(-40, -25, 30), rear=(-20, 40, 30), target=(0, 0, ZD), gain=3.2)
