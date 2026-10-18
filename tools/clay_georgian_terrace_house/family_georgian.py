"""Georgian terrace house, authored from the locked catalogue views of
georgian_terrace_house / variant_0 (georgian-terrace-house-early).

Read from the pixels (the top view governs the plan): the end house of a London terrace on the street (south)
beside a paved side passage (east), a lower stuccoed terrace to the west beyond a garden wall and gate. Three
storeys of yellow-brown stock brick, five bays, with six-over-six white sashes under gauged brick flat arches and
stone sills, the first-floor windows tallest and the centre one a French window with an iron balconette on the
stone doorcase below; a black panelled door with a rectangular fanlight between stone pilasters; a stone string
course and a brick plinth. A short parapet with a stone coping, then a steep grey slate mansard with five
dormers, a flat lead roof behind it with a skylight; the side walls rise as coped parapets carrying long
chimney stacks with rows of clay pots. A small hipped rear wing, a black lamp standard and a plane tree.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-georgian-terrace-house'
X0, X1, Y0, Y1 = -5.5, 5.5, -4.5, 4.5          # 11 m, five bays; 9 m deep
T = .35
G0 = .3
F1 = 3.8                                        # first floor (piano nobile)
F2 = 7.6
EAVE = 10.6                                     # top of the brick, foot of the parapet
MR = 2.6                                        # mansard rise above EAVE + .3
MRUN = 1.2                                      # mansard slope run from the wall line
BAYS = (-4.2, -2.1, 0.0, 2.1, 4.2)
EPS = .002
PALETTE = dict(wall=(.52, .42, .29), joint=(.68, .62, .52), rubbed=(.60, .48, .34), trim=(.94, .94, .92),
    pale=(.88, .88, .86), stone=(.84, .82, .76), roof=(.33, .36, .40), lead=(.42, .44, .46), sand=(.66, .62, .56),
    foundation=(.50, .42, .32), glass=(.22, .26, .29), hardware=(.07, .07, .08), interior=(.84, .80, .74),
    floor=(.58, .48, .38), timber=(.46, .34, .22), door=(.08, .09, .10), planting=(.30, .46, .20),
    soil=(.22, .16, .10), concrete=(.70, .69, .66), white=(.95, .95, .93), asphalt=(.28, .28, .29),
    brick=(.50, .40, .28), pot=(.70, .38, .24), paving=(.66, .64, .60), neighbour=(.64, .56, .42),
    stucco=(.92, .91, .88), blue=(.20, .30, .40))


def manifest(version):
    h = EAVE + .3 + MR + 2.4
    cams = G.camera_roster(X1 - X0 + 3.0, Y1 - Y0 + 3.0, h, [
        ('facade_close', (0.0, -22.0, 6.0), (0.0, Y0, 6.0), 45),
        ('architecture_close', (10.0, -15.0, 11.0), (X1, Y0, 10.5), 45),
        ('glass_close', (-2.1, -9.5, 5.4), (-2.1, Y0, 5.4), 45),
        ('doorcase_balconette', (2.0, -9.0, 2.6), (0.0, Y0, 3.0), 40),
        ('mansard_dormers', (1.5, -12.0, 15.5), (0.0, Y0 + .6, EAVE + 1.4), 40),
        ('chimney_stacks', (12.0, -10.0, 19.0), (X1, 0.0, EAVE + 3.5), 40),
        ('east_side', (17.0, 0.0, 6.0), (X1, 0.0, 6.0), 45),
        ('roof_lead', (-9.0, -10.0, 24.0), (0.0, .8, EAVE + 2.5), 40),
        ('interior', (2.5, 3.0, F1 + 1.6), (-1.5, Y0, F1 + 1.8), 40),
        ('rear_north', (0.0, 24.0, 6.5), (0.0, Y1, 6.5), 45)])
    for c in cams:                       # the locked front and oblique look from the south-east
        if c['name'] == 'front':
            c['location'] = (6.5, -15.0, 1.6); c['target'] = (-.5, -4.5, 6.8); c['lens'] = 24; c['whole'] = False
        elif c['name'] == 'front_corner':                                      # the locked oblique: close and high from the south-east
            c.update(location=(17.0, -24.0, 20.0), target=(0.0, -1.0, 6.5), lens=35, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(12.0, -18.0, 30.0), target=(0.0, 0.0, 6.0), lens=35, whole=False)
        elif c['name'] == 'left_side':                                        # over the lower neighbour, from the north-west
            c.update(location=(-24.0, 14.0, 18.0), target=(0.0, 0.0, 7.0), lens=35, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='georgian_terrace_house/variant_0 (georgian-terrace-house-early)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=4, storey_programme='three brick storeys (ground, piano nobile, second floor) and a mansard attic',
            plan='11 x 9 m five-bay end-of-terrace house (top view), a side passage east, a small hipped rear wing',
            facade='yellow-brown stock brick; six-over-six sashes under gauged flat arches; tall first-floor windows; stone doorcase with balconette; string course; coped parapet; slate mansard with five dormers',
            levels_m=[G0, F1, F2, EAVE], roof_m=dict(parapet=EAVE + .45, mansard_top=EAVE + .3 + MR),
            inferred='interiors, the rear face and the rear wing are teaching assumptions'),
        roof_contract=dict(type='steep slate mansard with five dormers behind a coped parapet, a flat lead roof with a skylight, side parapets with chimney stacks', datum_m=EAVE, crowns_m=[EAVE + .3 + MR]),
        identity_contract=dict(owner='five-bay yellow stock-brick Georgian house with white sashes, stone doorcase and balconette, slate mansard with dormers and potted chimney stacks'),
        material_contract=dict(profile='source-palette clay: yellow-brown stock brick with pale joints, rubbed-brick arches, white sashes, pale stone dressings, grey slate, terracotta pots, black door and iron', textured_keeper=False),
        programme_contract=dict(storeys=4, ground='hall and dining room', first='drawing rooms', second='bedrooms', attic='bedrooms in the mansard'),
        contact_contract=['Grade-zero pavement and passage', 'Brick walls from grade on a plinth', 'Mansard behind the coped parapet', 'Chimney stacks on the side parapets'],
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


# ---- Georgian terrace house ----

ZM = EAVE + .3 + MR                             # top of the mansard, the flat lead roof


ARCH = Batch()                                  # gauged flat arches, flushed once per elevation


def flat_arch(f, h, rise=.34, splay=.16):
    """Gauged flat arch: a flush splayed trapezoid of rubbed brick seated on the opening head, 5 mm proud."""
    top = h['z'] + h['h']
    pts = []
    for z, half in ((top, h['w'] / 2), (top + rise, h['w'] / 2 + splay)):
        pts += [f.p(h['u'] - half, -.005, z), f.p(h['u'] + half, -.005, z), f.p(h['u'] + half, 0.0, z), f.p(h['u'] - half, 0.0, z)]
    ARCH._hex('rubbed', pts)


def sash(m, f, h, occupied='room', lite=False):
    """Six-over-six white sash, stone sill, gauged brick flat arch over."""
    framed(m, f, h, cols=3, rows=4, inset=.12, occupied=occupied, lite=lite)
    m.box('trim', h['u'], .09, h['z'] + h['h'] / 2, h['w'] - .1, .1, .07)                    # meeting rail
    m.box('stone', h['u'], -.04, h['z'] - .06, h['w'] + .16, .14, .1)
    flat_arch(f, h)


def south_face():
    f = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south')
    door = hole('front door', 0.0, G0, 1.05, 2.3, kind='door')
    fan = hole('fanlight', 0.0, G0 + 2.42, 1.05, .45)
    french = hole('french window', 0.0, F1 + .05, 1.1, 2.75, kind='french window')
    gw = [hole(f'ground sash {u:+.1f}', u, 1.0, 1.05, 2.0) for u in BAYS if u != 0.0]
    w1 = [hole(f'first sash {u:+.1f}', u, F1 + .45, 1.05, 2.35) for u in BAYS if u != 0.0]
    w2 = [hole(f'second sash {u:+.1f}', u, F2 + .55, 1.05, 1.7) for u in BAYS]
    holes = [door, fan, french] + gw + w1 + w2
    f.wall('south carrier', X0, X1 - EPS, 0.0, EAVE + .45, depth=T, role='wall', holes=holes)
    G.brick_courses(f, X0 + .02, X1 - .02, .55, EAVE + .3, holes, spacing=.16)
    m = Merge(f)
    m.box('brick', 0.0, -.03, .26, X1 - X0 + .06, .06, .52)                                   # plinth
    m.box('stone', 0.0, -.05, F1 - .12, X1 - X0 + .1, .1, .2)                                # string course
    m.box('stone', 0.0, -.06, EAVE - .05, X1 - X0 + .14, .14, .16)                           # cornice band at the parapet foot
    m.box('stone', 0.0, T / 2 - .03, EAVE + .5, X1 - X0 + .1, T + .16, .1)                   # parapet coping
    for h in gw + w1 + w2:
        sash(m, f, h, occupied='room')
    # Black panelled door, rectangular fanlight, stone doorcase with an entablature carrying the balconette.
    m.box('door', 0.0, .16, door['z'] + door['h'] / 2, door['w'] - .02, .05, door['h'] - .02)
    for zz in (.55, 1.55):
        for s in (-1, 1):
            m.box('hardware', s * .24, .128, door['z'] + zz, .36, .012, .7)
    register(f, door, .14, 'entry door', 'hall')
    framed(m, f, fan, cols=3, rows=1, inset=.12, occupied='hall')
    for s in (-1, 1):
        m.box('stone', s * .82, -.07, (G0 + 3.2) / 2, .3, .14, 3.2 - G0)
        m.box('stone', s * .82, -.09, 3.25, .38, .18, .14)
    m.box('stone', 0.0, -.08, 3.4, 2.1, .16, .3)                                             # frieze
    m.box('stone', 0.0, -.3, F1 - .02, 2.4, .6, .14)                                          # cornice and balconette slab
    framed(m, f, french, cols=2, rows=5, inset=.12, occupied='drawing room', kind='french window')
    flat_arch(f, french)
    for s in (-1, 1):
        m.box('hardware', s * 1.1, -.55, F1 + .5, .04, .5, .04)
    m.box('hardware', 0.0, -.58, F1 + 1.0, 2.24, .04, .045)
    m.box('hardware', 0.0, -.58, F1 + .14, 2.24, .03, .03)
    for i in range(23):
        m.box('hardware', -1.1 + 2.2 * i / 22, -.58, F1 + .57, .018, .018, .86)
    m.flush('south')
    ARCH.flush('south arches')
    b = Batch()
    b.box('stone', 0.0, Y0 - .3, G0 / 2, 1.9, .6, G0)                                          # door step
    b.box('stone', 0.0, Y0 - .55, G0 / 4, 2.1, .3, G0 / 2)
    b.flush('door step')


def side_parapet(name, xa, xb, stacks):
    """Side wall above the eave: follows the mansard up and runs flat to the rear, stone coping on top."""
    pts = [(Y0 + T, EAVE), (Y0 + T, EAVE + .45), (Y0 + MRUN + .1, ZM + .35), (Y1 - T, ZM + .35), (Y1 - T, EAVE)]
    C.prism(name, pts, 'x', xa, xb, 'wall', 'parapets')
    b = Batch()
    xm = (xa + xb) / 2
    b.beam('stone', (xm, Y0 + T - .02, EAVE + .5), (xm, Y0 + MRUN + .1, ZM + .4), T + .14, .12, ext=.06)
    b.box('stone', xm, (Y0 + MRUN + .1 + Y1 - T) / 2, ZM + .41, T + .1, Y1 - T - Y0 - MRUN - .1 + .02, .12)
    # A long stack astride the parapet with a row of clay pots along it.
    xs = xm + (.03 - .44 + T / 2 if xa > 0 else .44 - .03 - T / 2)                     # outer face 3 cm proud of the side wall
    for yc, L, pots in stacks:                                                               # long stacks with rows of pots (top view)
        b.box('brick', xs, yc, ZM + .825, .88, L, 1.75)
        b.box('stone', xs, yc, ZM + 1.76, 1.0, L + .12, .12)
        for k in range(pots):
            b.box('pot', xs, yc - L / 2 + L * (k + .5) / pots, ZM + 2.12, .2, .2, .6)
    b.flush(name)


def side_and_rear():
    hd = (Y1 - Y0) / 2
    e = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    hs = [hole(f'east sash f{k}', .6, z, .7, hh) for k, (z, hh) in enumerate(((1.0, 2.0), (F1 + .45, 2.2), (F2 + .55, 1.6)))]  # one column of narrow sashes
    e.wall('east carrier', -hd + T, hd - T, 0.0, EAVE, depth=T, role='wall', holes=hs)
    G.brick_courses(e, -hd + T + .02, hd - T - .02, .55, EAVE - .02, hs, spacing=.16)
    m = Merge(e)
    m.box('brick', 0.0, -.03, .26, 2 * hd - 2 * T + .02, .06, .52)
    m.box('stone', 0.0, -.05, F1 - .12, 2 * hd - 2 * T + .02, .1, .2)
    for h in hs:
        framed(m, e, h, cols=2, rows=4, inset=.12, occupied='stair')
        m.box('trim', h['u'], .09, h['z'] + h['h'] / 2, h['w'] - .1, .1, .07)
        m.box('stone', h['u'], -.04, h['z'] - .06, h['w'] + .16, .14, .1)
        flat_arch(e, h, splay=.12)
    m.box('hardware', -hd + T + .25, -.07, EAVE / 2, .11, .11, EAVE)                         # downpipe at the front corner
    m.flush('east')
    ARCH.flush('east arches')
    w = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west')
    hs = [hole(f'west sash f{k}', 1.5, z, .95, hh) for k, (z, hh) in enumerate(((F1 + .45, 2.2), (F2 + .55, 1.6)))]
    w.wall('west carrier', -hd + T, hd - T, 0.0, EAVE, depth=T, role='wall', holes=hs)
    G.brick_courses(w, -hd + T + .02, hd - T - .02, .55, EAVE - .02, hs, spacing=.32)
    m = Merge(w)
    for h in hs:
        sash(m, w, h, lite=True)
    m.flush('west')
    ARCH.flush('west arches')
    side_parapet('East parapet', X1 - T, X1, [(-1.5, 3.4, 5)])
    side_parapet('West parapet', X0, X0 + T, [(-1.2, 3.1, 4), (2.6, 3.1, 4)])
    n = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')
    # Rear: the east column clears the low extension, the west column the hipped wing (rear faces u = -x).
    hs = [hole(f'rear sash east f{k}', -2.1, z, 1.0, hh) for k, (z, hh) in enumerate(((F1 + .45, 2.3), (F2 + .55, 1.7), (EAVE + .55, 1.4)))] + \
         [hole(f'rear sash west f{k}', 2.1, z, 1.0, hh) for k, (z, hh) in enumerate(((F2 + .55, 1.7), (EAVE + .55, 1.4)))]
    n.wall('north carrier', -X1, -X0 - EPS, 0.0, ZM + .35, depth=T, role='wall', holes=hs)
    G.brick_courses(n, -X1 + .02, -X0 - .02, .55, ZM + .3, hs, spacing=.32)
    m = Merge(n)
    for h in hs:
        sash(m, n, h)
    m.box('stone', 0.0, T / 2 - .03, ZM + .41, X1 - X0 + .1, T + .16, .12)
    m.flush('north')
    ARCH.flush('north arches')


def roof_and_inside():
    x0, x1 = X0 + T + .01, X1 - T - .01
    strip('Slate mansard', [(x0, Y0 + T + .02), (x1, Y0 + T + .02)], [(x1, Y0 + MRUN + .1), (x0, Y0 + MRUN + .1)][::-1],
          EAVE + .3, ZM, 'roof', 'roof', closed=False)
    # Upper roof: two shallow slate planes meeting at a mid-depth ridge, then a narrow lead strip at the rear.
    ya, yr, yb = Y0 + MRUN + .1, .4, Y1 - 1.6
    plate_x('Upper slate front', (ya, ZM), (yr, ZM + .28), x0, x1)
    plate_x('Upper slate rear', (yr, ZM + .28), (yb, ZM), x0, x1)
    C.box('Rear lead strip', ((x0 + x1) / 2, (yb + Y1 - T) / 2, ZM - .1), (x1 - x0, Y1 - T - yb, .2), 'lead', 'roof', 0)
    b = Batch()
    b.box('pale', -2.6, (yb + Y1 - T) / 2, ZM + .14, 1.4, .9, .28)                            # rooflight on the lead strip, west half
    b.box('glass', -2.6, (yb + Y1 - T) / 2 - .02, ZM + .3, 1.2, .7, .04)
    b.beam('stone', (x0, yr, ZM + .3), (x1, yr, ZM + .3), .16, .08)                            # ridge capping
    b.flush('upper roof')
    for u in BAYS:                                                                           # five dormers on the mansard slope
        dormer(u)
    # Rear: a two-storey hipped wing on the west half, a one-storey parapeted extension across the east half.
    wx0, wx1, wy1 = X0 + .4, X0 + 4.6, Y1 + 2.8
    rear_block('Rear wing', wx0, wx1, Y1, wy1, 7.0, [(1.0, 2.0), (F1 + .4, 2.1)])
    strip('Rear wing roof', [(wx0 - .25, Y1 - .05), (wx1 + .25, Y1 - .05), (wx1 + .25, wy1 + .25), (wx0 - .25, wy1 + .25)],
          [((wx0 + wx1) / 2 - .6, Y1 + 1.4), ((wx0 + wx1) / 2 + .6, Y1 + 1.4), ((wx0 + wx1) / 2 + .6, Y1 + 1.41), ((wx0 + wx1) / 2 - .6, Y1 + 1.41)],
          7.0 - .15, 7.9, 'roof', 'rear wing')
    rear_block('Rear extension', wx1, X1, Y1, Y1 + 2.6, 3.6, [(1.0, 2.0)], parapet=True)
    for z in (F1, F2, EAVE):
        C.box(f'Floor {z:.1f}', (0, 0, z - .12), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .24), 'floor', 'inside', 0)
    C.box('Ground floor', (0, 0, G0 - .1), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .2), 'floor', 'inside', 0)
    for z in (G0, F1, F2):
        for x in (-3.2, 0.0, 3.2):
            C.qa_room_light(f'Room {x:+.0f} {z:.0f}', (x, Y0 + 2.0, z + 2.0), 40, 2.2)
    for x in (-3.0, 3.0):
        C.qa_room_light(f'Attic {x:+.0f}', (x, Y0 + 1.6, EAVE + 1.4), 30, 1.6)
    C.CONTACTS.append(dict(name='Brick walls from grade on a plinth; mansard behind the parapet; stacks astride the side parapets', eave_m=EAVE))


def plate_x(name, a, c, x0, x1, t=.16, role='roof', module='roof'):
    """Closed sloped plate from (y, z) a to (y, z) c, extruded along x; its ends are thin faces."""
    vs = []
    for (y, z) in (a, c):
        for x in (x0, x1):
            vs += [(x, y, z), (x, y, z - t)]
    fs = [(0, 2, 6, 4), (1, 5, 7, 3), (0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6)]
    return C.mesh(name, vs, fs, role, module)


def rear_block(name, xa, xb, ya, yb, h, wins, parapet=False):
    """Rear wing or extension: a north wall with real cuts (white sashes, sills, flat arches) backed by a solid."""
    f = C.Face((0, yb, 0), (-1, 0, 0), (0, -1, 0), name)
    um = -(xa + xb) / 2
    hs = [hole(f'{name} window {k}', um, z, .95, hh) for k, (z, hh) in enumerate(wins)]
    f.wall(f'{name} wall', -xb, -xa - EPS, 0.0, h, depth=T, role='wall', holes=hs)
    G.brick_courses(f, -xb + .02, -xa - .02, .55, h - .05, hs, spacing=.32)
    m = Merge(f)
    for hh in hs:
        sash(m, f, hh)
    if parapet:
        m.box('stone', um, T / 2 - .03, h + .05, xb - xa + .06, T + .12, .1)
    m.flush(name)
    ARCH.flush(f'{name} arches')
    C.box(f'{name} body', ((xa + xb) / 2, (ya - .1 + yb - T) / 2, h / 2), (xb - xa, yb - T - ya + .1, h), 'wall', 'rear', 0)
    if parapet:
        C.box(f'{name} lead', ((xa + xb) / 2, (ya + yb - T) / 2, h - .25), (xb - xa - .4, yb - T - ya - .2, .1), 'lead', 'rear', 0)


def dormer(u):
    w = .85
    yf = Y0 + .55
    zb, zt = EAVE + .62, EAVE + 2.05
    b = Batch()
    for s in (-1, 1):                                                                        # slate cheeks
        b.box('roof', u + s * (w / 2 + .08), (yf + Y0 + MRUN + .5) / 2, (zb + zt) / 2, .16, Y0 + MRUN + .5 - yf, zt - zb)
    b.box('trim', u, yf + .06, zb + .07, w, .2, .14)                                          # sill
    b.box('trim', u, yf + .06, zt - .08, w + .1, .2, .16)                                     # head
    for s in (-1, 1):
        b.box('trim', u + s * (w / 2 - .035), yf + .1, (zb + zt) / 2, .07, .08, zt - zb - .1)
    b.box('trim', u, yf + .1, (zb + zt) / 2 + .1, w - .1, .07, .05)
    b.box('trim', u, yf + .1, (zb + zt) / 2 - .25, .04, .07, zt - zb - .6)
    b.box('glass', u, yf + .17, (zb + zt) / 2, w - .04, .01, zt - zb - .2)
    b.box('interior', u, (yf + .25 + Y0 + MRUN + .5) / 2, (zb + zt) / 2, w, Y0 + MRUN + .5 - yf - .25, zt - zb - .2)
    b.flush(f'dormer {u:+.1f}')
    C.prism(f'Dormer lead top {u:+.1f}', [(yf - .12, zt), (Y0 + MRUN + .5, zt), (Y0 + MRUN + .5, zt + .2), (yf - .12, zt + .1)], 'x', u - w / 2 - .24, u + w / 2 + .24, 'lead', 'dormers')


def site():
    C.box('Pavement', (0.0, Y0 - 2.1, .06), (44.0, 4.2, .12), 'paving', 'site', 0)
    C.box('Road', (0.0, Y0 - 8.2, .01), (44.0, 8.0, .02), 'asphalt', 'site', 0)
    C.box('Side passage', (X1 + 1.75, 2.0, .03), (3.5, 13.0, .06), 'concrete', 'site', 0)
    b = Batch()
    for k in range(-30, 30):
        b.box('joint', k * .9, Y0 - 2.1, .121, .02, 4.18, .004)
    b.box('brick', X1 + 3.65, 2.5, 1.1, .3, 13.6, 2.2)                                         # garden wall east of the passage
    b.box('brick', X1 + 3.65, Y0 + .1, 1.3, .55, .55, 2.6)
    b.box('stone', X1 + 3.65, Y0 + .1, 2.66, .66, .66, .12)
    b.box('brick', X0 - 1.0, Y0 + .7, 1.1, 2.0, .3, 2.2)                                       # garden wall and gate to the west
    b.box('timber', X0 - 1.0, Y0 + .53, 1.0, 1.1, .05, 1.9)
    b.box('brick', X0 - 2.15, Y0 + .7, 1.3, .55, .55, 2.6)
    b.box('stone', X0 - 2.15, Y0 + .7, 2.66, .66, .66, .12)
    b.box('hardware', X1 + .9, Y0 - 3.2, 2.4, .14, .14, 4.8)                                  # lamp standard and lantern
    b.box('hardware', X1 + .9, Y0 - 3.2, 4.9, .4, .4, .2)
    b.box('pale', X1 + .9, Y0 - 3.2, 4.65, .3, .3, .3)
    b.flush('street')
    street_tree(X0 - 3.0, Y0 - 3.0, z=.12, height=11.0, spread=3.2)
    # The lower Georgian terrace beyond the gate, as context: stucco ground storey, stock brick, slate roof, dormers, stacks.
    nx0, nx1, ny0, ny1 = X0 - 16.0, X0 - 2.5, Y0 + 1.0, Y0 + 10.0
    ne = 9.0
    f = C.Face((0, ny0, 0), (1, 0, 0), (0, 1, 0), 'neighbour front')
    us = [nx0 + 1.2 + i * 2.2 for i in range(6)]
    lower = [hole(f'neighbour ground {i}', u, .9, .9, 2.0) for i, u in enumerate(us) if i != 2] + [hole('neighbour door', us[2], .3, 1.0, 2.5, kind='door')]
    upper = [hole(f'neighbour f{k} {i}', u, z, .9, hh) for k, (z, hh) in enumerate(((F1 + .4, 2.1), (F2 + .1, 1.5))) for i, u in enumerate(us)]
    f.wall('neighbour stucco storey', nx0, nx1 - EPS, 0.0, 3.8, depth=.3, role='stucco', holes=lower)
    f.wall('neighbour brick storeys', nx0, nx1 - EPS, 3.8, ne, depth=.3, role='neighbour', holes=upper)
    m = Merge(f)
    for h in lower + upper:
        if h.get('kind') == 'door':
            m.box('door', h['u'], .16, h['z'] + h['h'] / 2, h['w'] - .02, .05, h['h'] - .02)
            register(f, h, .14, 'neighbour door', 'context')
        else:
            framed(m, f, h, cols=3, rows=4, inset=.12, occupied='context', lite=True)
    m.box('stone', (nx0 + nx1) / 2, -.06, ne - .1, nx1 - nx0 + .1, .14, .2)
    m.flush('neighbour front')
    C.box('Neighbour body', ((nx0 + nx1) / 2, (ny0 + .3 + ny1) / 2, ne / 2), (nx1 - nx0, ny1 - ny0 - .3, ne), 'neighbour', 'context', 0)
    pitched_roof('Neighbour slate roof', nx0, nx1, ny0, ny1, ne, 2.6, hip_w=True, hip_e=True, axis='x', ov=.2, role='roof', module='context')
    b = Batch()
    for u in us[1:5]:
        yd = ny0 + 1.0
        zd = ne + 2.6 * (1.0 / ((ny1 - ny0) / 2))
        b.box('roof', u, yd + .6, zd + .45, 1.0, 1.4, .9)
        b.box('trim', u, yd - .12, zd + .45, .8, .04, .7)
        b.box('glass', u, yd - .15, zd + .45, .6, .02, .55)
        b.box('lead', u, yd + .55, zd + .96, 1.2, 1.6, .12)
    for x in (nx0 + 4.4, nx0 + 8.8):
        b.box('brick', x, (ny0 + ny1) / 2, ne + 2.6 + .3, .8, 2.4, 1.4)
        for k in range(4):
            b.box('pot', x, (ny0 + ny1) / 2 - .9 + .6 * k, ne + 2.6 + 1.25, .2, .2, .5)
    b.flush('neighbour roof')


def build():
    site()
    south_face()
    side_and_rear()
    roof_and_inside()
    C.CONTACTS.append(dict(name='Five-bay Georgian end-of-terrace house on a London street, side passage east', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(30, -40, 35), fill=(-40, -20, 25), rear=(-15, 30, 25), target=(0, 0, 6.0), gain=4.0)
