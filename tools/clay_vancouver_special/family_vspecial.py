"""Vancouver Special, authored from the locked catalogue views of
vancouver_special / variant_0.

Read from the pixels (the top view governs the plan): a boxy two-storey house on a street corner, the street
south and a side street east, under one wide low-pitched front-gable roof of brown-grey asphalt shingles with a
central ridge running front to back, deep overhangs, brown fascias and exposed outrigger blocks under the
front rake. The ground storey of the street front is red-orange brick veneer, the upper storey and every other
wall white stucco over an exposed concrete foundation. A long cantilevered balcony runs across the right two
thirds of the upper front with a white slab fascia and a grey aluminium picket railing, a three-panel sliding
door and a smaller window behind it; a wide three-light window sits on the upper left. Under the balcony the
white front door with a sidelight and two coach lamps opens off a raised concrete landing whose stair runs
down along the front; wide three-light windows with brick rowlock sills either side. On the east side small
upright windows, a side door to the lower suite with its own concrete stair, downpipes at the corners. A lawn,
shrubs, a front walk, sidewalks and boulevards on both streets, a board fence with a lattice top round the
back yard and a row of cedars at the rear corner.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-vancouver-special'
X0, X1, Y0, Y1 = -5.4, 5.4, -4.6, 4.6          # 10.8 m front, 9.2 m deep (top view proportion)
H = (X1 - X0) / 2                               # half-width: the ridge is on x = 0
T = .28
FL1 = .90                                       # raised ground floor over the crawl/foundation
FL2 = 3.95                                      # upper floor (the balcony level)
BR = 3.90                                       # top of the front brick, bottom of the upper stucco
EAVE = 6.95                                     # roof top surface over the wall line
RT = .22                                        # roof slab, vertical thickness
WT = EAVE - RT - .045                           # wall plate, just under the soffit lining
RISE = 2.0                                      # low front-gable roof (about 4 in 12)
OV, OVR = .60, .60                              # side eave and gable rake overhangs
BX0 = X0 + 3.3                                  # west end of the front balcony (it runs to the east corner)
BD = 1.30                                       # balcony projection
EPS = .002
PALETTE = dict(wall=(.93, .92, .89), brick=(.64, .36, .25), joint=(.80, .76, .70), concrete=(.71, .70, .67),
    foundation=(.62, .61, .58), roof=(.42, .37, .33), roofline=(.29, .26, .23), fascia=(.43, .31, .21),
    soffit=(.90, .88, .84), frame=(.30, .26, .22), glass=(.30, .36, .40), curtain=(.88, .86, .80),
    white=(.96, .96, .95), trim=(.90, .90, .88), rail=(.47, .45, .42), hardware=(.10, .10, .11), lamp=(.95, .90, .74),
    interior=(.86, .82, .76), floor=(.62, .56, .48), timber=(.55, .40, .26), planting=(.28, .42, .20),
    cedar=(.20, .32, .18), lawn=(.36, .52, .24), soil=(.24, .18, .12), paving=(.75, .74, .71), asphalt=(.30, .30, .31))


def manifest(version):
    h = EAVE + RISE + 1.4
    cams = G.camera_roster(X1 - X0 + 3.0, Y1 - Y0 + 3.0, h, [
        ('facade_close', (0.0, -17.0, 4.0), (0.0, Y0, 4.0), 40),
        ('architecture_close', (8.6, -9.4, 4.9), (X1 - .4, Y0 - .3, 6.5), 45),
        ('glass_close', (-3.8, Y0 - 4.0, 5.75), (-3.8, Y0, 5.75), 45),
        ('balcony_rail', (4.5, -11.5, 5.6), (1.2, Y0 - .6, 4.6), 40),
        ('entry_stair', (3.0, -11.0, 2.0), (-1.0, Y0 - 1.0, 1.5), 40),
        ('brick_base', (2.7, -10.0, 2.4), (2.7, Y0, 2.4), 40),
        ('east_side', (19.0, -1.0, 3.8), (X1, 0.0, 3.8), 40),
        ('side_entry', (X1 + 7.5, -4.5, 2.4), (X1 + .5, 1.1, 1.5), 40),
        ('roof_ridge', (-9.0, -15.0, 16.0), (0.0, 0.0, EAVE + 1.0), 40),
        ('interior', (2.4, 2.8, FL2 + 1.6), (2.6, Y0, FL2 + 1.4), 40)])
    for c in cams:                       # the locked front and oblique look from the south-east
        if c['name'] == 'front':
            c.update(location=(11.4, -14.6, 1.7), target=(1.2, -1.0, 3.8), lens=32, whole=False)   # from across the side street: east wall about half the front
        elif c['name'] == 'front_corner':                                      # the locked oblique: high from the south-south-east
            c.update(location=(10.0, -18.0, 16.0), target=(0.0, -1.2, 3.4), lens=35, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(-12.0, -17.0, 22.0), target=(0.0, -.5, 3.0), lens=35, whole=False)
        elif c['name'] == 'left_side':
            c.update(location=(-21.0, -2.0, 5.0), target=(X0, 0.0, 4.0), lens=35, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(23.0, 0.0, 4.8), target=(X1, 0.0, 4.2), lens=35, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(0.0, Y1 + 21.0, 8.5), target=(0.0, Y1, 3.6), lens=35, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(15.0, 19.0, 13.0), target=(0.0, 1.0, 4.0), lens=35, whole=False)
        elif c['name'] == 'top':                                               # plan view framed on the house and its yards
            c.update(location=(.5, -1.5, 40.0), target=(.5, -1.499, 0.0), ortho_scale=24.0, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='vancouver_special/variant_0 (vancouver_special_v0)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=2, storey_programme='raised ground floor (suite, entry hall) and the main living floor above off the front balcony',
            plan='10.8 x 9.2 m box (top view) under one front-gable roof with 0.6 m overhangs; balcony across the east two thirds of the front',
            facade='red-orange brick ground storey on the street front, white stucco above and on all other walls; bronze aluminium sliders; white door with sidelight; aluminium picket railings',
            levels_m=[FL1, FL2, WT], roof_m=dict(eave=EAVE, ridge=EAVE + RISE),
            inferred='interiors, the west face and the rear face are teaching assumptions; the rear carries a small upper deck as glimpsed in the front view'),
        roof_contract=dict(type='low front-gable asphalt-shingle roof, central ridge front to back, open rakes with outriggers, boxed eaves with gutters', datum_m=EAVE, crowns_m=[EAVE + RISE]),
        identity_contract=dict(owner='boxy two-storey Vancouver Special: low wide front gable, brick ground storey and stucco upper storey, long front balcony with aluminium railing, raised side-stair entry'),
        material_contract=dict(profile='source-palette clay: white stucco, red-orange brick with pale joints, grey concrete foundation and stairs, brown-grey shingles, brown fascia and outriggers, bronze window frames, grey aluminium railings', textured_keeper=False),
        programme_contract=dict(storeys=2, ground='entry hall and a ground-floor suite with its own side door', upper='main living floor and bedrooms off the front balcony'),
        contact_contract=['Grade-zero lawn, walks and sidewalks', 'Walls on a concrete foundation', 'Front landing and stair on grade', 'Roof on the wall plates'],
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
# ---- Vancouver Special ----

W = H + OV                                      # half-width of the roof plate at the eave edges
SLOPE = RISE / H
ZE = EAVE - OV * SLOPE                          # roof top at the eave edge
ZR = EAVE + RISE                                # ridge
YA, YB = Y0 - OVR, Y1 + OVR                     # rake lines
EWU, EDU = .05, 1.65                            # east wall: ground window / suite door centres (u = y), uppers stacked over them
ESY, SN, SG = EDU - .65, 5, .28                 # side landing south edge (landing centred on the door), flight steps and going


def zroof(x):
    """Top of the roof plate at x."""
    return EAVE + RISE * (1 - abs(x) / H)


def zsoffit(x):
    """Underside of the soffit lining at x."""
    return zroof(x) - RT - .042


def hexy(b, role, quad, y0, y1):
    """Closed block from a four-point (x, z) section carried along y (batched)."""
    b._hex(role, [(x, y0, z) for x, z in quad] + [(x, y1, z) for x, z in quad])


def chevron(name, top, thick, y0, y1, role, module):
    """Closed gable plate: a chevron section (eave, ridge, eave) of vertical thickness `thick`, carried along y."""
    pts = [(-W, top(-W)), (0.0, top(0.0)), (W, top(W)), (W, top(W) - thick), (0.0, top(0.0) - thick), (-W, top(-W) - thick)]
    vs = [(x, y, z) for y in (y0, y1) for x, z in pts]
    fs = [(5, 4, 1, 0), (4, 3, 2, 1), (7, 10, 11, 6), (8, 9, 10, 7)]          # end caps wound outward (-y at y0, +y at y1)
    fs += [(i, (i + 1) % 6, (i + 1) % 6 + 6, i + 6) for i in range(6)]
    return C.mesh(name, vs, fs, role, module)


def flight(start, n, top, go, sign):
    """(s, z) section of a solid concrete flight falling from a landing edge at s = start in direction sign;
    the first riser is buried 1 cm in the landing."""
    rise = top / n
    pts = [(start - sign * .01, 0.0)]
    for k in range(1, n):
        z = top - rise * k
        pts += [(start + sign * go * (k - 1) - (sign * .01 if k == 1 else 0.0), z), (start + sign * go * k, z)]
    pts.append((start + sign * go * (n - 1), 0.0))
    return pts


def rail(b, pts, z, h=1.0, spacing=.11, role='rail'):
    """Aluminium picket railing on a level run of plan points: top and bottom rails, square end posts (one post at
    each shared corner, never two coincident)."""
    for j, ((ax, ay), (cx, cy)) in enumerate(zip(pts, pts[1:])):
        L = math.hypot(cx - ax, cy - ay)
        k = j % 2                                    # alternate sections: overlapping corner ends never share a face plane
        b.beam(role, (ax, ay, z + h), (cx, cy, z + h), .06 - .004 * k, .04 + .004 * k, ext=.025)
        b.beam(role, (ax, ay, z + .08), (cx, cy, z + .08), .04 - .004 * k, .03 + .004 * k)
        n = max(2, int(L / spacing))
        for i in range(0 if j == 0 else 1, n + 1):
            px, py = ax + (cx - ax) * i / n, ay + (cy - ay) * i / n
            s = .05 if i in (0, n) else .018
            b.box(role, px, py, z + (h + .02) / 2, s, s, h - .02)


def rail_slope(b, a, c, h=1.0, n=7, role='rail', first=True):
    """Raked railing over a flight, from nosing point a down to nosing point c; first=False when a landing rail
    already stands a post at a."""
    b.beam(role, (a[0], a[1], a[2] + h), (c[0], c[1], c[2] + h), .052, .048, ext=.025)     # its own section, distinct from landing rails
    b.beam(role, (a[0], a[1], a[2] + .1), (c[0], c[1], c[2] + .1), .032, .038)
    for i in range(0 if first else 1, n + 1):
        p = [a[k] + (c[k] - a[k]) * i / n for k in range(3)]
        s = .05 if i in (0, n) else .018
        b.box(role, p[0], p[1], p[2] + h / 2, s, s, h)


def brick_veneer(f, lo, hi, z0, z1, holes, course=.075, brick=.22):
    """Red brick: fine bed joints and staggered head joints, cut round the openings and their sills."""
    G.brick_courses(f, lo, hi, z0, z1, holes, spacing=course)
    vs, fs = [], []
    for row in range(int((z1 - z0) / course)):
        zb = z0 + row * course
        u = lo + brick * (.5 + .5 * (row % 2))
        while u < hi - .02:
            if not any(h['u'] - h['w'] / 2 - .1 < u < h['u'] + h['w'] / 2 + .1 and h['z'] - .14 < zb + course and zb < h['z'] + h['h'] + .02 for h in holes):
                o = len(vs)
                vs += [f.p(u - .005, -.0025, zb + .006), f.p(u + .005, -.0025, zb + .006), f.p(u + .005, -.0025, zb + course), f.p(u - .005, -.0025, zb + course)]   # between bed joints, own plane: no T overlaps
                fs.append((o, o + 1, o + 2, o + 3))
            u += brick
    if fs:
        C.mesh(f.label + ' head joints', vs, fs, 'joint', 'brick joints')


def slider(m, f, h, cols=3, occupied='room', sill='alu', curtains=True, kind='window'):
    """Bronze aluminium slider set near the face, pale curtains drawn to the sides inside, a sill below."""
    framed(m, f, h, cols=cols, rows=1, inset=.10, occupied=occupied, kind=kind, frame='frame')
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    if curtains:
        for s in (-1, 1):
            m.box('curtain', u + s * (w / 2 - w * .12), T + .06, z + hh / 2, w * .3, .04, hh - .04)
    if sill == 'brick':                                          # rowlock brick sill, top just under the cut
        m.box('brick', u, -.05, z - .065, w + .16, .14, .12)
    elif sill == 'alu':
        m.box('frame', u, -.02, z - .024, w + .04, .06, .04)


def lamp(m, u, z):
    """Coach lamp on a wall bracket (face coordinates)."""
    m.box('hardware', u, -.05, z, .06, .1, .12)
    m.box('lamp', u, -.15, z - .05, .16, .16, .26)
    m.box('hardware', u, -.15, z + .1, .21, .21, .05)
    m.box('hardware', u, -.15, z - .2, .1, .1, .04)


def plinth(m, a, c, top=FL1 - .03):
    """Exposed concrete foundation proud of the stucco between u = a and u = c."""
    m.box('foundation', (a + c) / 2, -.02, top / 2, c - a, .04, top)


def downpipe(m, b, f, u, side):
    """Brown downpipe on the wall at u, swan-necked out under the soffit to the side eave gutter."""
    ztop = 6.3                                                                # clear under the soffit lining
    m.box('fascia', u, -.06, (ztop + .05) / 2, .08, .08, ztop - .05)
    m.box('fascia', u, -.115, .1, .1, .17, .08)                                 # shoe (back face clear of the pipe's)
    p = C.Vector(f.p(u, -.06, ztop))
    gx = side * (W + .11)
    b.beam('fascia', (p.x, p.y, ztop), (gx, p.y, ztop), .07, .07, ext=.03)     # thinner than pipe and outlet: ends buried, no shared planes
    b.box('fascia', gx, p.y, (ztop + ZE - .16) / 2, .08, .08, ZE - .16 - ztop + .04)   # up into the gutter outlet


def south_face():
    f = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south')
    g1 = hole('ground window west', X0 + 1.97, 1.95, 1.8, 1.45)
    g2 = hole('ground window east', X0 + 8.1, 1.95, 3.0, 1.45)
    door = hole('front door', X0 + 4.4, FL1 + .02, 1.0, 2.15, kind='door')
    side = hole('front sidelight', X0 + 3.68, FL1 + .02, .36, 2.15)
    w1 = hole('upper window west', X0 + 1.6, 5.05, 1.9, 1.4)
    w2 = hole('upper window middle', X0 + 4.85, 5.05, 1.3, 1.4)
    sd = hole('balcony sliding door', X0 + 8.1, FL2 + .02, 3.0, 2.43, kind='door')
    low, up = [g1, g2, door, side], [w1, w2, sd]
    f.wall('south brick carrier', X0, X1 - EPS, 0.0, BR, depth=T, role='brick', holes=low)
    f.wall('south stucco carrier', X0, X1 - EPS, BR, WT, depth=T, role='wall', holes=up)
    C.prism('South gable', [(X0, WT), (X1 - EPS, WT), (0.0, WT + RISE)], 'y', Y0, Y0 + T, 'wall', 'envelope')
    brick_veneer(f, X0 + .02, X1 - .02, .17, BR - .04, low)
    m = Merge(f)
    m.box('foundation', (X0 + X1) / 2, -.02, .08, X1 - X0 - .01, .04, .16)          # concrete strip under the brick
    m.box('white', (X0 + BX0) / 2 + .01, -.025, 3.76, BX0 - X0 + .02, .05, .28)      # floor band, flush with the balcony fascia
    for h in (g1, g2):
        slider(m, f, h, cols=3, occupied='suite' if h is g1 else 'entry hall', sill='brick')
    slider(m, f, w1, cols=3, occupied='bedroom')
    slider(m, f, w2, cols=2, occupied='living room')
    slider(m, f, sd, cols=3, occupied='living room', sill=None, kind='door')
    # White panelled front door and a glazed sidelight in one white casing.
    m.box('white', door['u'], .14, door['z'] + door['h'] / 2, door['w'] - .02, .05, door['h'] - .02)
    for zz, hh in ((.42, .62), (1.22, .62), (1.86, .42)):
        for s in (-1, 1):
            m.box('trim', door['u'] + s * .21, .108, door['z'] + zz + hh / 2 - .2, .34, .012, hh)
    m.box('hardware', door['u'] + .36, .1, door['z'] + 1.0, .05, .06, .14)
    register(f, door, .12, 'entry door', 'entry hall')
    framed(m, f, side, cols=1, rows=3, inset=.10, occupied='entry hall', frame='white')
    a, c = side['u'] - side['w'] / 2, door['u'] + door['w'] / 2
    for u in (a - .05, c + .05):
        m.box('white', u, -.025, door['z'] + door['h'] / 2 + .05, .1, .05, door['h'] + .1)
    m.box('white', (a + c) / 2, -.03, door['z'] + door['h'] + .055, c - a + .22, .06, .11)    # head proud of the posts on every side
    m.box('white', (side['u'] + side['w'] / 2 + door['u'] - door['w'] / 2) / 2, -.01, door['z'] + door['h'] / 2, .06, .04, door['h'])
    lamp(m, a - .38, FL1 + 2.0)
    lamp(m, c + .38, FL1 + 2.0)
    m.box('hardware', c + .42, -.03, FL1 + 1.2, .22, .05, .3)                         # slim wall mailbox
    m.flush('south')


def front_entry():
    """Raised concrete landing under the balcony, the stair running down eastwards along the front, railings."""
    b = Batch()
    lx0, lx1, ly0 = X0 + 3.1, X0 + 5.2, Y0 - 1.8
    sy0, sy1 = ly0, Y0 - .6
    n, go = 5, .28
    b.box('concrete', (lx0 + lx1) / 2, (ly0 + Y0 + .02) / 2, FL1 / 2, lx1 - lx0, Y0 + .02 - ly0, FL1)
    C.prism('Front stair', flight(lx1, n, FL1, go, 1), 'y', sy0, sy1, 'concrete', 'front entry')
    foot = lx1 + go * (n - 1)
    rail(b, [(lx0 + .04, Y0), (lx0 + .04, ly0 + .04), (lx1, ly0 + .04)], FL1)
    for y in (sy0 + .04, sy1 - .04):
        rail_slope(b, (lx1, y, FL1), (foot, y, FL1 / n), n=6, first=y > sy0 + .1)
    b.flush('front entry')
    C.box('Front walk', ((foot - .02 + lx1 + 2.3) / 2, (Y0 - 3.22 + sy1) / 2, .03), (lx1 + 2.3 - foot + .02, sy1 - Y0 + 3.22, .06), 'paving', 'site', 0)
    C.box('Front bed behind the stair', ((lx1 + foot) / 2 + .0, (sy1 + Y0 - .02) / 2, .03), (foot - lx1 + .02, Y0 - .02 - sy1, .06), 'soil', 'site', 0)
    C.box('Front bed west', ((X0 + .1 + lx0 - .02) / 2, (Y0 - 1.1 + Y0 - .02) / 2, .03), (lx0 - .02 - X0 - .1, 1.08, .06), 'soil', 'site', 0)
    for k, x in enumerate((X0 + .45, X0 + 1.2, X0 + 1.95, X0 + 2.65)):
        A.foliage(f'Front shrub {k}', (x, Y0 - .55, .44), (.42, .4, .4), detail=2)
    for k, x in enumerate((lx1 + .25, lx1 + .8)):
        A.foliage(f'Stair bed shrub {k}', (x, Y0 - .3, .4), (.26, .22, .36), detail=2)


def balcony():
    """Cantilevered front balcony: white slab and fascia, aluminium picket railing on three sides."""
    b = Batch()
    b.box('white', (BX0 + X1 - .01) / 2, (Y0 - BD + Y0 + .02) / 2, 3.76, X1 - .01 - BX0, BD + .02, .32)
    rail(b, [(BX0 + .04, Y0), (BX0 + .04, Y0 - BD + .04), (X1 - .05, Y0 - BD + .04), (X1 - .05, Y0)], 3.92, h=1.02)
    b.flush('balcony')


def east_face():
    e = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    # Sources: the front ~45% of the side wall is blank stucco; one ground window and the suite door sit mid-wall,
    # each with an upright upper window stacked over it; the rear third is blank.
    ups = [hole(f'east upper window {i}', u, 5.15, .75, 1.25) for i, u in enumerate((EWU, EDU))]
    gws = [hole('east ground window', EWU, 2.0, .75, 1.05)]
    sdoor = hole('suite side door', EDU, FL1 + .02, .9, 2.15, kind='door')
    e.wall('east carrier', Y0 + T, Y1 - T, 0.0, WT, depth=T, role='wall', holes=ups + gws + [sdoor])
    m = Merge(e)
    b = Batch()
    plinth(m, Y0 + T, ESY - SN * SG - .04)
    plinth(m, ESY + 1.33, Y1)
    for h in ups + gws:
        slider(m, e, h, cols=2)
    framed(m, e, sdoor, cols=1, rows=1, inset=.10, occupied='ground-floor suite', kind='door', frame='frame')   # near full-lite glazed door
    lamp(m, EDU - .75, FL1 + 2.0)
    for u in (Y0 + .12, Y1 - .12):
        downpipe(m, b, e, u, 1)
    m.flush('east')
    b.flush('east downpipes')


def side_entry():
    """The suite's own concrete landing at the side door and a flight running down towards the street."""
    b = Batch()
    b.box('concrete', (X1 - .02 + X1 + 1.05) / 2, ESY + .65, FL1 / 2, 1.07, 1.3, FL1)
    n, go = SN, SG
    C.prism('Side stair', flight(ESY, n, FL1, go, -1), 'x', X1 - .02, X1 + 1.0, 'concrete', 'side entry')
    foot = ESY - go * (n - 1)
    rail(b, [(X1 + .96, ESY), (X1 + .96, ESY + 1.26), (X1 + .02, ESY + 1.26)], FL1)
    rail_slope(b, (X1 + .96, ESY, FL1), (X1 + .96, foot, FL1 / n), n=6, first=False)
    b.flush('side entry')
    C.box('Side path', (X1 + .55, (Y0 - 3.22 + foot + .02) / 2, .03), (1.0, foot + .02 - Y0 + 3.22, .06), 'paving', 'site', 0)


def north_face():
    n = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')                   # u = -x
    hs = [hole('rear upper window west', 3.5, 5.05, 1.4, 1.4), hole('rear upper window middle', .2, 5.05, 1.0, 1.4),
          hole('rear ground window west', 3.5, 1.95, 1.4, 1.2), hole('rear ground window east', -3.4, 1.95, 1.4, 1.2)]
    dk = hole('rear deck door', -3.4, FL2 + .02, 2.4, 2.43, kind='door')
    rd = hole('rear door', 0.0, FL1 + .02, .9, 2.15, kind='door')
    n.wall('north carrier', -X1 + EPS, -X0, 0.0, WT, depth=T, role='wall', holes=hs + [dk, rd])
    C.prism('North gable', [(X0, WT), (X1 - EPS, WT), (0.0, WT + RISE)], 'y', Y1 - T, Y1, 'wall', 'envelope')
    m = Merge(n)
    b = Batch()
    m.box('foundation', 0.0, -.02, (FL1 - .03) / 2, X1 - X0 + .08, .04, FL1 - .03)
    for h in hs:
        slider(m, n, h, cols=2, curtains=False)
    slider(m, n, dk, cols=2, occupied='living room', sill=None, curtains=False, kind='door')
    framed(m, n, rd, cols=1, rows=2, inset=.10, occupied='ground-floor suite', kind='door', frame='frame')
    m.box('frame', rd['u'], .11, rd['z'] + .55, rd['w'] - .1, .03, 1.0)
    lamp(m, .75, FL1 + 2.0)
    m.flush('north')
    # Rear sundeck off the upper floor at the east end, on two posts, and the suite's back stoop.
    b.box('timber', (1.7 + X1 - .01) / 2, (Y1 - .02 + Y1 + 1.5) / 2, FL2 - .125, X1 - .01 - 1.7, 1.52, .19)
    for x in (1.85, X1 - .15):
        b.box('timber', x, Y1 + 1.35, (FL2 - .22) / 2, .14, .14, FL2 - .22)
    rail(b, [(1.74, Y1), (1.74, Y1 + 1.46), (X1 - .05, Y1 + 1.46), (X1 - .05, Y1)], FL2 - .03)
    b.box('concrete', 0.0, (Y1 - .02 + Y1 + 1.1) / 2, FL1 / 2, 1.4, 1.12, FL1)
    C.prism('Rear stoop flight', flight(Y1 + 1.1, 5, FL1, .28, 1), 'x', -.6, .6, 'concrete', 'rear entry')
    for x in (-.56, .56):
        rail_slope(b, (x, Y1 + 1.1, FL1), (x, Y1 + 1.1 + .28 * 4, FL1 / 5), n=6)
    b.flush('rear deck and stoop')


def west_face():
    w = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west')                    # u = -y
    hs = [hole(f'west upper window {i}', u, 5.15, .75, 1.25) for i, u in enumerate((-2.2, 1.8))] + \
         [hole(f'west ground window {i}', u, 2.2, .75, 1.0) for i, u in enumerate((-2.2, 1.8))]
    w.wall('west carrier', -(Y1 - T), -(Y0 + T), 0.0, WT, depth=T, role='wall', holes=hs)
    m = Merge(w)
    b = Batch()
    plinth(m, -Y1, -(Y0 + T))
    for h in hs:
        slider(m, w, h, cols=2, curtains=False)
    for u in (-(Y0 + .12), -(Y1 - .12)):
        downpipe(m, b, w, u, -1)
    m.flush('west')
    b.flush('west downpipes')


def roof():
    """Low front-gable roof: shingle plate, soffit lining, rake and eave fascias, gutters, outriggers."""
    chevron('Roof plate', zroof, RT, YA, YB, 'roof', 'roof')
    chevron('Soffit lining', lambda x: zroof(x) - RT - .012, .03, YA - .014, YB + .014, 'soffit', 'roof')   # bedded into both rake fascias: no slot under the rakes
    b = Batch()
    for s in (-1, 1):
        for y in (YA - .03, YB + .03):                                       # rake fascias, proud of the plate ends
            k = (s + 1) // 2                                                  # the two rakes of a gable differ by a few mm: no shared planes at the apex
            # deep enough that its underside drops below the soffit lining, so the lining's end is buried in the board
            b.beam('fascia', (s * (W + .055), y, ZE - RT / 2 - .01), (0.0, y, ZR - RT / 2 - .01), .05 - .006 * k, .30 - .006 * k, ext=.03)
            # corner return: a fascia block flush-wrapping the rake foot, the eave fascia and the gutter end, slightly
            # thicker than the rake board so no faces coincide; eave fascia and gutter stop inside it
            b.box('fascia', s * (W + .0825), y, ZE - .12, .205, .056, .345)
        b.box('fascia', s * (W + .03), (YA + YB) / 2, ZE - RT / 2 + .005, .05, YB - YA + .06, RT + .07)
        b.box('fascia', s * (W + .11), (YA + YB) / 2, ZE - .1, .12, YB - YA + .06, .13)                 # gutters
        k = 1
        while W - k * .25 > .2:                                               # shingle course butts
            x0 = s * (W - k * .25)
            x1 = x0 - s * .05
            hexy(b, 'roofline', [(x0, zroof(x0) - .01), (x0, zroof(x0) + .012), (x1, zroof(x1) + .004), (x1, zroof(x1) - .01)], YA + .01, YB - .01)
            xt = x0 - s * .16                                                 # staggered tab joints up the exposed course
            y = YA + .1 + .17 * (k % 2)
            while y < YB - .1:
                hexy(b, 'roofline', [(x0, zroof(x0) - .004), (x0, zroof(x0) + .008), (xt, zroof(xt) + .006), (xt, zroof(xt) - .004)], y - .008, y + .008)
                y += .34
            k += 1
    hexy(b, 'roofline', [(-.17, zroof(.17) - .01), (0.0, ZR + .035), (.17, zroof(.17) - .01), (0.0, ZR - .06)], YA + .01, YB - .01)   # ridge cap
    for yf, sg in ((Y0, -1), (Y1, 1)):                                       # exposed outrigger blocks under both rakes
        for x in (0.0, -2.9, 2.9, -5.7, 5.7):
            ztop = zsoffit(max(0.0, abs(x) - .07)) + .005
            y0, y1 = yf - sg * .1, yf + sg * (OVR - .07)
            b.box('fascia', x, (y0 + y1) / 2, ztop - .1, .14, abs(y1 - y0), .2)
    b.flush('roof trim')


def inside():
    for z, name in ((FL1, 'Ground floor'), (FL2, 'Upper floor')):
        C.box(name, (0, 0, z - .12), (X1 - X0 - 2 * T + .04, Y1 - Y0 - 2 * T + .04, .24), 'floor', 'inside', 0)
    C.box('Ceiling', (0, 0, WT - .14), (X1 - X0 - 2 * T + .04, Y1 - Y0 - 2 * T + .04, .24), 'interior', 'inside', 0)
    for (x, y) in ((-3.0, -2.2), (2.6, -2.2), (0.0, 2.6)):
        C.qa_room_light(f'Upper {x:+.0f}{y:+.0f}', (x, y, FL2 + 2.1), 45, 2.2)
        C.qa_room_light(f'Ground {x:+.0f}{y:+.0f}', (x, y, FL1 + 2.1), 35, 2.2)
    C.CONTACTS.append(dict(name='Brick front and stucco walls on a concrete foundation; front-gable roof on the wall plates', eave_m=EAVE, ridge_m=ZR))


def fence(b, a, c, h=1.5, lat=.32, first=True):
    """Board fence with a lattice top between plan points a and c; posts every 2.4 m."""
    (ax, ay), (cx, cy) = a, c
    L = math.hypot(cx - ax, cy - ay)
    ux, uy = (cx - ax) / L, (cy - ay) / L
    b.beam('timber', (ax, ay, h / 2 + .02), (cx, cy, h / 2 + .02), .04, h - .04)
    for z in (h + .04, h + lat + .06):
        b.beam('timber', (ax, ay, z), (cx, cy, z), .07, .05)
    k = 0
    while k * .3 < L - .3:
        s0, s1 = k * .3, k * .3 + .3
        p0, p1 = (ax + ux * s0, ay + uy * s0), (ax + ux * s1, ay + uy * s1)
        b.beam('timber', (p0[0], p0[1], h + .06), (p1[0], p1[1], h + lat + .04), .02, .015)
        b.beam('timber', (p1[0], p1[1], h + .06), (p0[0], p0[1], h + lat + .04), .02, .015)
        k += 1
    posts = [i * 2.4 for i in range(int(L / 2.4) + 1)] + ([L] if L - int(L / 2.4) * 2.4 > .3 else [])
    for s in posts[0 if first else 1:]:
        b.box('timber', ax + ux * s, ay + uy * s, (h + lat + .14) / 2, .1, .1, h + lat + .14)


def site():
    ys0, ys1 = Y0 - 3.2, Y0 - 5.0                                             # south sidewalk
    xe0, xe1 = X1 + 1.7, X1 + 3.5                                             # east sidewalk
    yn, xw = Y1 + 3.0, X0 - .9                                                # rear and west fence lines
    yfar, xfar = yn + 8.0, xw - 6.0
    C.box('Front lawn', ((xw + xe0) / 2, (ys0 + Y0 - .02) / 2, .02), (xe0 - xw, Y0 - .02 - ys0, .04), 'lawn', 'site', 0)
    C.box('East side yard', ((X1 + .02 + xe0) / 2, (Y0 - .02 + yn) / 2, .02), (xe0 - X1 - .02, yn - Y0 + .02, .04), 'lawn', 'site', 0)
    C.box('West side yard', ((xw + X0 - .02) / 2, (Y0 - .02 + yn) / 2, .02), (X0 - .02 - xw, yn - Y0 + .02, .04), 'lawn', 'site', 0)
    C.box('Back yard', (0.0, (Y1 + .02 + yn) / 2, .02), (X1 - X0 + .04, yn - Y1 - .02, .04), 'lawn', 'site', 0)
    C.box('South sidewalk', ((xfar + xe1) / 2, (ys1 + ys0) / 2, .05), (xe1 - xfar, ys0 - ys1, .1), 'paving', 'site', 0)
    C.box('East sidewalk', ((xe0 + xe1) / 2, (ys0 + yfar) / 2, .05), (xe1 - xe0, yfar - ys0, .1), 'paving', 'site', 0)
    C.box('South boulevard', ((xfar + xe1 + 1.4) / 2, ys1 - .7, .02), (xe1 + 1.4 - xfar, 1.4, .04), 'lawn', 'site', 0)
    C.box('East boulevard', (xe1 + .7, (ys1 + yfar) / 2, .02), (1.4, yfar - ys1, .04), 'lawn', 'site', 0)
    C.box('South curb', ((xfar + xe1 + 1.55) / 2, ys1 - 1.475, .075), (xe1 + 1.55 - xfar, .15, .15), 'concrete', 'site', 0)
    C.box('East curb', (xe1 + 1.475, (ys1 - 1.4 + yfar) / 2, .075), (.15, yfar - ys1 + 1.4, .15), 'concrete', 'site', 0)
    C.box('South street', ((xfar + xe1 + 10.55) / 2, ys1 - 1.55 - 4.5, .01), (xe1 + 10.55 - xfar, 9.0, .02), 'asphalt', 'site', 0)
    C.box('East street', (xe1 + 1.55 + 4.5, (ys1 - 1.55 + yfar) / 2, .01), (9.0, yfar - ys1 + 1.55, .02), 'asphalt', 'site', 0)
    b = Batch()
    for k in range(int((xe1 - xfar) / 1.5)):                                  # sidewalk scoring
        b.box('joint', xfar + 1.5 * (k + 1), (ys1 + ys0) / 2, .101, .02, ys0 - ys1 - .04, .004)
    for k in range(int((yfar - ys0) / 1.5)):
        b.box('joint', (xe0 + xe1) / 2, ys0 + 1.5 * (k + 1), .101, xe1 - xe0 - .04, .02, .004)
    for k in range(int((xe1 + 10.0 - xfar) / 4.0)):                           # centre dashes and edge lines
        b.box('white', xfar + 1.0 + 4.0 * k, ys1 - 6.05, .022, 2.0, .12, .004)
    for k in range(int((yfar - ys1) / 4.0)):
        b.box('white', xe1 + 6.05, ys1 + 1.0 + 4.0 * k, .022, .12, 2.0, .004)
    fence(b, (xw, Y0 + 1.0), (xw, yn))
    fence(b, (xw, yn), (X1 + 1.3, yn), first=False)
    fence(b, (X1 + 1.3, yn), (X1 + 1.3, 1.9), first=False)
    b.flush('site')
    for k, y in enumerate((3.0, 3.8, 4.6, 5.4, 6.2, 7.0)):                         # cedar row inside the rear corner fence
        A.foliage(f'Cedar {k}', (X1 + .85, y, 1.65), (.38, .38, 1.6), role='cedar', detail=2)
    street_tree(X0 - 1.5, ys1 - .7, z=.04, height=7.5, spread=2.2)
    street_tree(xe1 + .7, Y1 + 16.0, z=.04, height=8.0, spread=2.2)   # behind the rear_side camera plane, clear of its frame


def build():
    site()
    south_face()
    front_entry()
    balcony()
    east_face()
    side_entry()
    north_face()
    west_face()
    roof()
    inside()
    C.CONTACTS.append(dict(name='Corner Vancouver Special with front and side stairs, balcony, lawn and fenced back yard', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(-30, -40, 30), fill=(40, -20, 25), rear=(-15, 30, 25), target=(0, -1.0, 4.0), gain=3.5)
