"""Prince's Island Park, Calgary, authored from the locked catalogue views of calgary_princes_island / variant_0.

Read from the pixels (the top view governs the plan; 1 m is about 22 px of it, the river on the east): a riverside
park on the island in the Bow. A timber pavilion with a planted sedum roof stands at the centre, rotated about 27
degrees off the river line: cedar board cladding, a fully glazed south-east face with dark mullions, a door and
corner glazing on the long south-west face, an open porch under the roof at the north-west end, slim timber posts
at the roof corners and a thin dark metal fascia. A wide pale-slab promenade with granite sett borders runs past
its south-west face from the south plaza to the north-west, crossed by a paved band to the west; two asphalt
cycle paths with yellow dashed centre lines run north-south, the western one inland, the eastern one rising onto
a raised concrete boardwalk with mesh railings on both sides along the rip-rap river bank. Lens-shaped kerbed
beds of ornamental grasses, perennials with pink, lavender and white flowers and shrubs fill the spaces between
the paths; groves of rounded deciduous trees stand north of the pavilion and along the boardwalk; timber benches
on dark steel frames and corten bins sit on the paving. North of the top-view frame the boardwalk lands on a
plaza at a concrete footbridge that crosses the Bow to a wooded far bank. The downtown skyline is context.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-princes-island-park'
X0, X1, Y0, Y1 = -29.0, 23.6, -23.0, 40.0      # park extents: west edge to the waterline, south plaza to the north lawn
WATER = 23.6                                    # straight waterline of the Bow along the east side
ZG = 1.0                                        # park grade above the river surface (the island ground is solid from 0)
YB = 34.0                                       # footbridge centre line
FAR = 58.0                                      # far bank edge
T = .3
EPS = .002
PALETTE = dict(water=(.20, .45, .48), riprap=(.30, .29, .27), rock=(.50, .49, .46), rock2=(.42, .41, .39), rock3=(.58, .56, .52),
    lawn=(.36, .50, .20), grass=(.45, .52, .24), grass2=(.64, .58, .32), planting=(.26, .42, .18), shrub=(.34, .48, .22),
    tree=(.25, .42, .16), tree2=(.33, .49, .20), bark=(.36, .28, .20), soil=(.30, .25, .18),
    flower=(.80, .44, .62), flower2=(.62, .48, .80), flower3=(.93, .90, .82),
    concrete=(.80, .78, .74), paving=(.74, .72, .68), sett=(.52, .51, .49), joint=(.60, .58, .55), curb=(.84, .82, .78),
    asphalt=(.30, .30, .31), yellow=(.86, .70, .20), deck=(.76, .75, .72),
    timber=(.62, .43, .26), wall=(.62, .43, .26), batten=(.52, .35, .20), post=(.56, .39, .23), fascia=(.20, .20, .21),
    sedum=(.45, .50, .22), sedum2=(.60, .50, .26), sedum3=(.36, .45, .19),
    glass=(.24, .30, .34), trim=(.17, .17, .18), interior=(.84, .80, .74), floor=(.58, .48, .38),
    steel=(.22, .22, .23), mesh=(.40, .40, .40), corten=(.50, .27, .14), bench=(.64, .47, .29), hardware=(.20, .20, .20))


def manifest(version):
    h = 14.0
    cams = G.camera_roster(FAR + 10.0 - X0, Y1 - Y0 + 4.0, h, [
        ('pavilion_close', (-9.0, -9.0, ZG + 1.7), (0.5, 0.0, ZG + 2.2), 30),
        ('glazing_close', (5.2, -10.0, ZG + 2.2), (2.6, -4.4, ZG + 1.9), 30),
        ('green_roof', (-14.0, -12.0, ZG + 13.0), (0.2, 0.2, ZG + 3.9), 35),
        ('porch_northwest', (-2.0, 14.0, ZG + 1.7), (1.0, 4.0, ZG + 2.0), 28),
        ('promenade_beds', (-14.6, 16.5, ZG + 1.7), (-6.0, -6.0, ZG + 1.0), 30),
        ('boardwalk', (13.0, -1.5, ZG + 1.9), (18.6, 26.0, ZG + 1.4), 30),
        ('riprap_bank', (34.0, -14.0, 5.0), (19.0, -2.0, .8), 34),
        ('bench_plaza', (2.0, -21.5, ZG + 1.5), (6.5, -18.5, ZG + .5), 30),
        ('footbridge', (12.0, 43.0, ZG + 6.0), (36.0, YB, ZG + .5), 30),
        ('west_path', (-23.0, -21.0, ZG + 1.7), (-24.0, 12.0, ZG + .8), 30)])
    for c in cams:
        if c['name'] == 'front':                                              # the locked front: on the promenade, looking north-east
            c.update(location=(-9.5, -12.5, ZG + 1.65), target=(4.0, 6.0, ZG + 3.0), lens=22, whole=False)
        elif c['name'] == 'front_corner':                                     # the locked oblique, high over the south plaza
            c.update(location=(-2.0, -34.0, ZG + 15.0), target=(3.0, 2.0, ZG + 0.0), lens=24, whole=False)
        elif c['name'] == 'aerial':                                           # the locked top: near-nadir over the pavilion
            c.update(location=(-1.0, -4.0, 78.0), target=(-1.0, -.6, 0.0), lens=34, whole=False)
        elif c['name'] == 'top':
            c.update(location=(19.0, 8.5, 120.0), target=(19.0, 8.501, 0.0), ortho_scale=100.0)
        elif c['name'] == 'left_side':                                        # from the west over the inland edge
            c.update(location=(-62.0, 0.0, 18.0), target=(0.0, 4.0, 2.0), lens=30, whole=False)
        elif c['name'] == 'right_side':                                       # from over the river, the bank and boardwalk square on
            c.update(location=(48.0, -16.0, 16.0), target=(8.0, 6.0, 2.0), lens=26, whole=False)
        elif c['name'] == 'rear':                                             # from the north lawn looking south over the park
            c.update(location=(-6.0, Y1 + 18.0, 16.0), target=(0.0, 0.0, 2.0), lens=26, whole=False)
        elif c['name'] == 'rear_side':                                        # from the far bank, north-east, over the footbridge
            c.update(location=(62.0, 50.0, 24.0), target=(10.0, 6.0, 1.5), lens=28, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype="calgary_princes_island/variant_0, modelled as Prince's Island Park",
        measurement_contract=dict(dimensions_m=dict(width=FAR + 10.0 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=1, storey_programme='park: a one-storey pavilion (cafe or washrooms) among paths, beds and trees',
            plan='park 52.6 x 63 m from the west edge to the waterline (top view: pavilion roof about 12.4 x 9.4 m rotated 27 degrees), the Bow 34 m wide, a footbridge at the north to a far bank',
            levels_m=dict(river=0.0, park_grade=ZG, boardwalk_deck=ZG + .45, pavilion_floor=ZG + .15, pavilion_eave=ZG + 3.6, green_roof=ZG + 4.1),
            facade='cedar board cladding, glazed south-east face with dark mullions, sedum roof with a dark fascia, timber posts; pale slab paving with sett borders, asphalt cycle paths with yellow dashes, a concrete boardwalk with mesh railings, rip-rap, kerbed planting beds, rounded deciduous trees',
            inferred='the north lawn, footbridge and far bank lie beyond the top view and follow the front and oblique; the skyline is context and not modelled; the river bed below the surface is not modelled'),
        roof_contract=dict(type='flat planted sedum roof with a thin dark fascia over the pavilion', datum_m=ZG + 3.6, crowns_m=[ZG + 4.15]),
        identity_contract=dict(owner="Prince's Island Park: a green-roofed timber pavilion on a wide slab promenade among lens-shaped beds of grasses and flowers, cycle paths with yellow dashes, a railed boardwalk along a rip-rap bank of the Bow, groves of rounded trees"),
        material_contract=dict(profile='source-palette clay: blue-green water, grey rip-rap, greens and golds of grasses and trees with pink, lavender and white flowers, pale slabs and granite setts, asphalt and yellow dashes, cedar, dark steel and glass, corten', textured_keeper=False),
        programme_contract=dict(storeys=1, ground='pavilion room with tables behind the glazed face, porch, paths for walking and cycling, benches, planting'),
        open_space_contract=dict(kind='fixed_native_park', axis='y', river_side='east',
                                 zones=['river', 'riprap', 'boardwalk', 'east_cycle_path', 'pavilion', 'promenade', 'planting_beds', 'west_cycle_path', 'groves', 'north_lawn', 'footbridge']),
        contact_contract=['River surface at grade zero', 'Island ground solid from the river to the park grade', 'Rip-rap from the water to the bank top',
                          'Paths, beds and the pavilion slab on the park ground', 'Boardwalk on a solid plinth', 'Footbridge on two piers and abutments'],
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
# ---- Prince's Island Park ----

import random

RNG = random.Random(1912)                       # fixed seed: the same plants, boulders and crowns on every build
CU, SU = math.cos(math.radians(27.0)), math.sin(math.radians(27.0))
EV = (CU, SU)                                   # pavilion short axis (towards the north-east)
EU = (-SU, CU)                                  # pavilion long axis (towards the north-west, the porch end)
PC = (0.2, 0.2)                                 # pavilion centre
ICO_V = [(-1, 1.618, 0), (1, 1.618, 0), (-1, -1.618, 0), (1, -1.618, 0), (0, -1, 1.618), (0, 1, 1.618), (0, -1, -1.618), (0, 1, -1.618),
         (1.618, 0, -1), (1.618, 0, 1), (-1.618, 0, -1), (-1.618, 0, 1)]
ICO_F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
         (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
OCT_V = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
OCT_F = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]


def px(u, v):
    """Top-view pixel to metres (22 px to the metre, origin near the pavilion centre, north up)."""
    return ((u - 620.0) / 22.0, (435.0 - v) / 22.0)


def L(u, v):
    """Pavilion local (u along the long axis, v along the short axis) to world x, y."""
    return (PC[0] + u * EU[0] + v * EV[0], PC[1] + u * EU[1] + v * EV[1])


def interp(x, table):
    if x <= table[0][0]:
        return table[0][1]
    for (a, fa), (b, fb) in zip(table, table[1:]):
        if x <= b:
            return fa + (fb - fa) * (x - a) / (b - a)
    return table[-1][1]


BANK_T = [(-40.0, 17.2), (-4.0, 17.0), (2.5, 16.6), (8.4, 18.7), (14.3, 20.1), (60.0, 20.3)]


def bank(y):
    """x of the top of the rip-rap bank at y (the riparian bed widens it to the south)."""
    return interp(y, BANK_T)


def slope_z(x, y):
    b = bank(y)
    return ZG - .04 - (x - b) / (WATER + .05 - b) * (ZG - .07)


def lump(b, role, cx, cy, cz, rx, ry, rz, jitter=.18):
    """A rounded low-poly lump (a jittered icosahedron): a boulder, a shrub or a sedum mound."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    s = 1 / 1.902
    for (x, y, z) in ICO_V:
        k = 1 + RNG.uniform(-jitter, jitter)
        V.append((cx + x * s * rx * k, cy + y * s * ry * k, cz + z * s * rz * k))
    F.extend(tuple(o + i for i in f) for f in ICO_F)


def bud(b, role, cx, cy, cz, r):
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    V.extend((cx + x * r, cy + y * r, cz + z * r * .8) for (x, y, z) in OCT_V)
    F.extend(tuple(o + i for i in f) for f in OCT_F)


def tuft(b, role, x, y, z, h, r):
    """A clump of grass: a narrow four-sided cone standing open on the soil it rises from."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for i in range(4):
        a = 2 * math.pi * i / 4 + RNG.uniform(0, 1)
        V.append((x + r * math.cos(a), y + r * math.sin(a), z))
    V.append((x + RNG.uniform(-.08, .08), y + RNG.uniform(-.08, .08), z + h))
    for i in range(4):
        F.append((o + i, o + (i + 1) % 4, o + 4))
    return V[o + 4]


def obox(b, role, cx, cy, cz, lx, ly, lz, ang):
    """Box rotated by ang (radians) about z."""
    c, s = math.cos(ang), math.sin(ang)
    pts = []
    for dz in (-1, 1):
        for du, dd in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            u, v = du * lx / 2, dd * ly / 2
            pts.append((cx + u * c - v * s, cy + u * s + v * c, cz + dz * lz / 2))
    b._hex(role, pts)


def cr(p0, p1, p2, p3, u):
    return tuple(.5 * (2 * p1[i] + (-p0[i] + p2[i]) * u + (2 * p0[i] - 5 * p1[i] + 4 * p2[i] - p3[i]) * u * u
                       + (-p0[i] + 3 * p1[i] - 3 * p2[i] + p3[i]) * u ** 3) for i in range(2))


def spline(pts, step=.8, closed=False):
    """Catmull-Rom samples through pts at about `step` metres."""
    n = len(pts)
    Q = pts if closed else [pts[0]] + list(pts) + [pts[-1]]
    out = []
    segs = n if closed else n - 1
    for k in range(segs):
        if closed:
            p0, p1, p2, p3 = Q[(k - 1) % n], Q[k], Q[(k + 1) % n], Q[(k + 2) % n]
        else:
            p0, p1, p2, p3 = Q[k], Q[k + 1], Q[k + 2], Q[k + 3]
        m = max(2, int(math.dist(p1, p2) / step))
        for i in range(m):
            out.append(cr(p0, p1, p2, p3, i / m))
    if not closed:
        out.append(tuple(pts[-1]))
    return out


def frames(samples):
    """(point, left normal, arc length) along an open polyline."""
    out, s = [], 0.0
    for i, p in enumerate(samples):
        a = samples[max(i - 1, 0)]; b = samples[min(i + 1, len(samples) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = math.hypot(tx, ty) or 1.0
        if i:
            s += math.dist(samples[i - 1], p)
        out.append((p, (-ty / n, tx / n), s))
    return out


def ribbon(name, fr, width, z0, ztop, role, module, off=0.0):
    """Closed slab along a path: rings of four points (bottom left, bottom right, top right, top left)."""
    rings = []
    for (p, n, s) in fr:
        zt = ztop(p, s) if callable(ztop) else ztop
        cx, cy = p[0] + n[0] * off, p[1] + n[1] * off
        l = (cx + n[0] * width / 2, cy + n[1] * width / 2); r = (cx - n[0] * width / 2, cy - n[1] * width / 2)
        rings.append([(l[0], l[1], z0), (r[0], r[1], z0), (r[0], r[1], zt), (l[0], l[1], zt)])
    return loft(name, rings, role, module, closed=False)


def clip(samples, lo=Y0 - .5, hi=Y1 + .5):
    return [p for p in samples if lo <= p[1] <= hi]


def area(poly):
    return .5 * sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))


def inside(pt, poly):
    x, y = pt
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            c = not c
        j = i
    return c


def offset(poly, d):
    """Offset a counter-clockwise closed polygon inwards by d (bisector offset; the outlines are smooth)."""
    out = []
    n = len(poly)
    for i in range(n):
        a, p, b = poly[i - 1], poly[i], poly[(i + 1) % n]
        e1 = (p[0] - a[0], p[1] - a[1]); e2 = (b[0] - p[0], b[1] - p[1])
        l1 = math.hypot(*e1) or 1; l2 = math.hypot(*e2) or 1
        n1 = (-e1[1] / l1, e1[0] / l1); n2 = (-e2[1] / l2, e2[0] / l2)
        bx, by = n1[0] + n2[0], n1[1] + n2[1]
        bl = math.hypot(bx, by) or 1
        k = d / max(.5, (bx * n1[0] + by * n1[1]) / bl)
        out.append((p[0] + bx / bl * k, p[1] + by / bl * k))
    return out


def ring_mesh(name, outer, inner, z0, z1, role, module):
    """A closed band between an outer and an inner outline (a kerb round a bed)."""
    n = len(outer)
    vs = [(x, y, z0) for x, y in outer] + [(x, y, z0) for x, y in inner] + [(x, y, z1) for x, y in outer] + [(x, y, z1) for x, y in inner]
    O0, I0, O1, I1 = 0, n, 2 * n, 3 * n
    fs = []
    for i in range(n):
        j = (i + 1) % n
        fs += [(O1 + i, O1 + j, I1 + j, I1 + i), (O0 + j, O0 + i, I0 + i, I0 + j), (O0 + i, O0 + j, O1 + j, O1 + i), (I0 + j, I0 + i, I1 + i, I1 + j)]
    return C.mesh(name, vs, fs, role, module)


def slab(name, poly, z0, z1, role, module):
    return C.prism(name, poly, 'z', z0, z1, role, module)


def outline(pxs, step=1.0):
    poly = spline([px(*p) for p in pxs], step, closed=True)
    return poly if area(poly) > 0 else poly[::-1]


# ---------------------------------------------------------------- ground, river, bank


def ground_and_river():
    ys = [Y0 - 1.0 + k * 1.0 for k in range(int(Y1 - Y0 + 2.0) + 1)]
    loft('Island ground', [[(X0 - 1.0, y, 0.0), (bank(y) + .06, y, 0.0), (bank(y) + .06, y, ZG), (X0 - 1.0, y, ZG)] for y in ys], 'lawn', 'ground', closed=False)
    loft('Rip-rap bank', [[(bank(y), y, 0.0), (WATER + .05, y, 0.0), (WATER + .05, y, .03), (bank(y), y, ZG - .04)] for y in ys], 'riprap', 'bank', closed=False)
    C.box('Bow River', ((WATER - .1 + FAR + .1) / 2, (Y0 + Y1) / 2, .01), (FAR + .2 - WATER + .1, Y1 - Y0 + 2.0, .02), 'water', 'river', 0)
    C.box('Far bank', (FAR + 5.0, (Y0 + Y1) / 2, ZG / 2), (10.0, Y1 - Y0 + 2.0, ZG), 'lawn', 'far bank', 0)
    b = Batch()
    y = Y0 - .6
    while y < Y1 + .6:                                     # packed rounded boulders over the slope, three greys
        x = bank(y) + .35
        while x < WATER - .2:
            r = RNG.uniform(.45, .7)
            xx = x + RNG.uniform(-.12, .12); yy = y + RNG.uniform(-.2, .2)
            if not abs(yy - YB) < 2.9:
                lump(b, RNG.choice(('rock', 'rock2', 'rock3')), xx, yy, max(slope_z(xx, yy) + r * .25, r * .75 * 1.05), r * 1.25, r * RNG.uniform(.95, 1.3), r * .75)
            x += r * 1.75
        y += 1.15
    for i in range(70):                                    # far bank stones at its waterline
        yy = RNG.uniform(Y0, Y1)
        if abs(yy - YB) < 2.6:
            continue
        r = RNG.uniform(.35, .55)
        lump(b, RNG.choice(('rock', 'rock2', 'rock3')), FAR + RNG.uniform(-.3, .3), yy, max(r * .55, r * .75 * 1.05) + .2, r * 1.2, r * 1.3, r * .75)
    b.flush('rip-rap boulders')
    b = Batch()
    for i in range(140):                                   # grasses in the joints along the top of the bank
        yy = RNG.uniform(Y0 - .5, Y1 + .5)
        if abs(yy - YB) < 2.9:
            continue
        xx = bank(yy) + RNG.uniform(.05, 1.3)
        tuft(b, 'grass2' if i % 3 else 'grass', xx, yy, slope_z(xx, yy) - .02, RNG.uniform(.4, .8), RNG.uniform(.1, .18))
    b.flush('bank grasses')


# ---------------------------------------------------------------- paths


def asphalt_path(name, pts):
    fr = frames(clip(spline(pts, 1.2)))
    ribbon(f'{name} asphalt', fr, 3.4, ZG - .02, ZG + .04, 'asphalt', 'cycle paths')
    for s in (-1, 1):                                       # flush concrete edges
        ribbon(f'{name} edge {s:+d}', fr, .2, ZG - .02, ZG + .046, 'curb', 'cycle paths', off=s * 1.78)
    b = Batch()
    last = -9.0
    for i in range(1, len(fr)):
        p, n, s = fr[i]
        if s - last >= 3.0:                                 # yellow dashes on the centre line, 1 m long every 3 m
            q = fr[i - 1][0]
            tx, ty = p[0] - q[0], p[1] - q[1]
            l = math.hypot(tx, ty) or 1
            b.beam('yellow', (p[0] - tx / l * .5, p[1] - ty / l * .5, ZG + .041), (p[0] + tx / l * .5, p[1] + ty / l * .5, ZG + .041), .1, .008)
            last = s
    b.flush(f'{name} markings')


def slab_path(name, pts, width, top, border=.45, step=1.6):
    """Pale slab paving with granite sett borders, transverse joints and a centre joint."""
    fr = frames(clip(spline(pts, 1.1)))
    ribbon(f'{name} slabs', fr, width, ZG - .02, ZG + top, 'paving', 'paving')
    if border:
        for s in (-1, 1):
            ribbon(f'{name} sett border {s:+d}', fr, border, ZG - .02, ZG + top + .006, 'sett', 'paving', off=s * (width / 2 - border / 2 + .01))
    b = Batch()
    last = -9.0
    inner = width / 2 - (border or 0)
    for p, n, s in fr[1:-1]:
        if s - last >= step:
            b.beam('joint', (p[0] + n[0] * inner, p[1] + n[1] * inner, ZG + top + .001), (p[0] - n[0] * inner, p[1] - n[1] * inner, ZG + top + .001), .03, .006)
            last = s
    b.flush(f'{name} joints')
    return fr


PLAZA = [(262, 590), (440, 592), (560, 600), (600, 690), (680, 782), (722, 808), (788, 808), (790, 940), (250, 940), (256, 760), (244, 700)]
PITS = [(-12.95, -11.1), (-11.4, -18.9)]


def paths():
    asphalt_path('West cycle path', [(-26.6, Y1 + 1.0), (-26.0, 30.0), (-24.8, 19.8), (-22.7, 10.7), (-19.8, 1.6), (-16.8, -5.7), (-19.1, -9.3), (-22.7, -13.0), (-23.4, -21.0), (-23.5, Y0 - 1.0)])
    asphalt_path('East cycle path', [(12.7, -3.2), (10.9, -8.4), (9.5, -13.9), (9.8, -21.0), (9.9, Y0 - 1.0)])
    slab_path('Promenade', [(-18.0, Y1 + 1.0), (-17.0, 30.0)] + [px(*p) for p in ((285, 0), (300, 100), (345, 200), (390, 300), (440, 400), (480, 500), (505, 600), (515, 660))], 5.0, .060)
    slab_path('West crossing', [px(*p) for p in ((300, 645), (130, 650))] + [(X0 - .6, -9.8)], 4.5, .066)
    slab_path('Bench link', [px(*p) for p in ((372, 305), (250, 312), (150, 328))], 2.5, .068, border=.3)
    slab_path('North path', [px(*p) for p in ((300, 50), (420, 15), (560, 25), (620, 80), (615, 200), (605, 290))], 2.6, .055, border=.3)
    slab_path('Bridge path', [px(560, 25), (3.6, 22.5), (10.5, 28.9), (15.4, 34.0)], 2.6, .0572, border=.3)
    poly = [px(*p) for p in PLAZA]
    poly = poly if area(poly) > 0 else poly[::-1]
    slab('South plaza', poly, ZG - .02, ZG + .054, 'paving', 'paving')
    b = Batch()
    beds = [outline(BEDS['B5'][0])]
    ok = lambda p: inside(p, poly) and not any(inside(p, q) for q in beds) and all(math.dist(p, c) > 1.5 for c in PITS)
    for k in range(-30, 30):                               # slab joints, 1.6 m grid
        for j in range(-30, 30):
            a = (-12.0 + k * 1.6, -24.0 + j * 1.6)
            for d in ((1.6, 0.0), (0.0, 1.6)):
                e = (a[0] + d[0], a[1] + d[1])
                if ok(a) and ok(e):
                    b.beam('joint', (a[0], a[1], ZG + .0545), (e[0], e[1], ZG + .0545), .03, .006)
    b.flush('plaza joints')


# ---------------------------------------------------------------- beds and planting

BEDS = {
    'B1': ([(160, 95), (215, 100), (260, 160), (300, 250), (285, 285), (225, 270), (180, 220), (158, 150)], (3.6, .5, 1.0)),
    'B2': ([(228, 360), (290, 335), (350, 350), (390, 420), (412, 510), (400, 570), (340, 575), (275, 520), (232, 440)], (3.6, .5, 1.1)),
    'B3': ([(25, 420), (110, 395), (160, 440), (190, 520), (185, 575), (140, 588), (70, 585), (25, 520)], (3.2, .55, .9)),
    'B4': ([(165, 712), (225, 705), (255, 760), (255, 925), (165, 925)], (3.2, .5, .9)),
    'B5': ([(452, 672), (492, 668), (530, 720), (558, 800), (560, 880), (520, 925), (455, 925), (442, 860), (440, 760)], (3.6, .6, .9)),
    'B6': ([(600, 612), (650, 586), (740, 536), (800, 512), (808, 590), (795, 700), (785, 795), (725, 798), (685, 770), (625, 700), (598, 650)], (3.2, .6, .8)),
    'B7': ([(925, 570), (950, 560), (975, 610), (988, 700), (990, 800), (990, 925), (890, 925), (880, 820), (885, 700), (905, 620)], (3.2, .5, 1.1)),
    'B8': ([(355, 80), (420, 60), (540, 85), (575, 150), (565, 250), (520, 320), (480, 330), (452, 290), (415, 215), (375, 140)], (2.2, .45, .3)),
    'B9': ([(655, 32), (720, -20), (980, -40), (970, 60), (950, 200), (905, 330), (860, 450), (825, 478), (795, 465), (700, 300), (670, 250), (665, 150)], (1.8, .4, .25)),
}


def bed(name, poly, dens, b):
    inner = offset(poly, .15)
    ring_mesh(f'{name} kerb', poly, inner, ZG - .02, ZG + .14, 'curb', 'beds')
    slab(f'{name} soil', offset(poly, .12), ZG - .02, ZG + .10, 'soil', 'beds')
    xs = [p[0] for p in inner]; ys = [p[1] for p in inner]
    a = abs(area(inner))
    td, sd, fd = dens
    core = offset(poly, .35)

    def spot():
        for _ in range(60):
            p = (RNG.uniform(min(xs), max(xs)), RNG.uniform(min(ys), max(ys)))
            if inside(p, core) and Y0 - .3 < p[1] < Y1 + .3:
                return p
        return None
    for i in range(int(td * a)):                            # ornamental grasses, green and gold
        p = spot()
        if p:
            tuft(b, ('grass', 'grass2', 'planting')[i % 3], p[0], p[1], ZG + .095, RNG.uniform(.5, 1.15), RNG.uniform(.14, .25))
    for i in range(int(sd * a)):                            # shrub masses
        p = spot()
        if p:
            r = RNG.uniform(.35, .75)
            lump(b, 'shrub' if i % 2 else 'planting', p[0], p[1], ZG + .1 + r * .45, r * 1.3, r * 1.3, r * 1.0, .22)
    for i in range(int(fd * a)):                            # perennials: a stem with a flower head, pink, lavender, white
        p = spot()
        if p:
            tip = tuft(b, 'planting', p[0], p[1], ZG + .095, RNG.uniform(.5, .85), .06)
            bud(b, ('flower', 'flower2', 'flower3', 'flower')[i % 4], tip[0], tip[1], tip[2], RNG.uniform(.09, .14))


def planting():
    b = Batch()
    for name, (pxs, dens) in BEDS.items():
        bed(f'Bed {name}', outline(pxs), dens, b)
    for i, c in enumerate(PITS):                             # tree pits in the south plaza
        poly = [(c[0] + 1.3 * math.cos(a * math.tau / 20), c[1] + 1.3 * math.sin(a * math.tau / 20)) for a in range(20)]
        bed(f'Tree pit {i}', poly, (3.0, 0.0, 0.0), b)
    b.flush('planting')


def park_tree(x, y, r, z=ZG + .09, k=0):
    """Rounded deciduous tree: a trunk, two limbs and a crown of four overlapping masses."""
    H = 2.4 * r + 3.0
    lean = ((.2, .1), (-.15, .2), (.1, -.2))[k % 3]
    top = (x + lean[0], y + lean[1], z + H * .55)
    C.rod('Tree trunk', (x, y, z - .05), top, .12 + .03 * r, 'bark', 'trees', 7)
    for i, a in enumerate((k * 1.3, k * 1.3 + 2.4)):
        C.rod('Tree limb', (x, y, z + H * .35), (x + math.cos(a) * r * .5, y + math.sin(a) * r * .5, z + H * .62), .06 + .015 * r, 'bark', 'trees', 6)
    A.foliage('Tree crown', (top[0], top[1], z + H * .7), (r * .85, r * .85, r * .75), role='tree' if k % 2 else 'tree2', detail=1)
    for j in range(3):
        a = k * .9 + j * math.tau / 3
        A.foliage('Tree crown mass', (top[0] + math.cos(a) * r * .5, top[1] + math.sin(a) * r * .5, z + H * (.58 + .04 * j)),
                  (r * .6, r * .6, r * .52), role='tree2' if (k + j) % 2 else 'tree', detail=1)


TREES = [((690, 40), 2.6), ((730, 170), 3.8), ((830, 330), 3.9), ((790, 60), 3.2), ((900, 90), 3.4), ((955, 25), 2.2), ((880, 230), 2.8),
         ((400, 120), 2.8), ((460, 190), 3.8), ((535, 130), 2.2), ((215, 200), 2.0), ((205, 110), 1.8), ((260, 410), 2.5),
         ((55, 455), 1.8), ((60, 540), 1.7), ((950, 850), 3.0), ((25, 140), 1.8)]


def trees():
    k = 0
    beds = [outline(p) for p, d in BEDS.values()]
    for (u, v), r in TREES:
        x, y = px(u, v)
        park_tree(x, y, r, z=ZG + .09 if any(inside((x, y), q) for q in beds) else ZG, k=k); k += 1
    for (x, y), r in zip(PITS, (3.6, 3.2)):
        park_tree(x, y, r, k=k); k += 1
    for (x, y), r in (((-20.5, 27.0), 3.4), ((-9.5, 30.0), 3.8), ((-2.0, 35.5), 3.0), ((4.5, 31.0), 3.2), ((9.0, 38.0), 2.8), ((13.5, 24.5), 3.0)):
        park_tree(x, y, r, z=ZG, k=k); k += 1
    for y in (-15.0, -3.0, 9.0, 22.0, 38.0):
        park_tree(FAR + 3.0 + (k % 2) * 2.5, y, 3.4, z=ZG, k=k); k += 1


# ---------------------------------------------------------------- boardwalk and footbridge

BW = [(12.6, -3.6), (14.6, 2.5), (16.9, 8.4), (18.1, 14.3), (18.3, 20.0), (18.3, 26.0), (18.2, 32.2)]
BWZ = [(-3.6, .042), (3.0, .45), (23.0, .45), (31.0, .068), (40.0, .068)]


def boardwalk():
    fr = frames(spline(BW, 1.0))
    zt = lambda p, s: ZG + interp(p[1], BWZ)
    ribbon('Boardwalk deck', fr, 3.2, ZG - .05, zt, 'deck', 'boardwalk')
    for s in (-1, 1):
        ribbon(f'Boardwalk kerb {s:+d}', fr, .18, ZG - .05, lambda p, t: zt(p, t) + .1, 'deck', 'boardwalk', off=s * 1.52)
    b = Batch()
    last = -9.0
    for p, n, s in fr[1:-1]:
        if s - last >= 2.4:                                  # transverse joints
            z = zt(p, s) + .001
            b.beam('joint', (p[0] + n[0] * 1.4, p[1] + n[1] * 1.4, z), (p[0] - n[0] * 1.4, p[1] - n[1] * 1.4, z), .03, .006)
            last = s
    for side in (-1, 1):                                     # dark steel railings with mesh panels on both kerbs
        posts = []
        last = -9.0
        for p, n, s in fr:
            if -2.6 < p[1] < 30.6 and s - last >= 1.8:
                posts.append((p[0] + n[0] * side * 1.52, p[1] + n[1] * side * 1.52, zt(p, s) + .1))
                last = s
        for q in posts:
            b.box('steel', q[0], q[1], q[2] + .5, .06, .06, 1.02)
        for q, r in zip(posts, posts[1:]):
            b.beam('steel', (q[0], q[1], q[2] + 1.0), (r[0], r[1], r[2] + 1.0), .07, .05, ext=.03)
            b.beam('steel', (q[0], q[1], q[2] + .08), (r[0], r[1], r[2] + .08), .04, .04, ext=.03)
            b.beam('mesh', (q[0], q[1], q[2] + .54), (r[0], r[1], r[2] + .54), .015, .84, ext=-.03)
    b.flush('boardwalk railings')
    slab('Bridge landing', [(14.6, YB - 2.4), (20.2, YB - 2.4), (20.2, YB + 2.4), (14.6, YB + 2.4)], ZG - .05, ZG + .055, 'paving', 'footbridge')


def bridge_z(x):
    t = min(1.0, max(0.0, (x - 19.6) / (FAR + 1.0 - 19.6)))
    return ZG + .06 + 1.2 * math.sin(math.pi * t)


def footbridge():
    """A concrete footbridge over the Bow at the north end: a cambered deck on two river piers and abutments, mesh railings."""
    xs = [19.6 + (FAR + 1.0 - 19.6) * i / 40 for i in range(41)]
    loft('Footbridge deck', [[(x, YB - 2.0, bridge_z(x) - .55), (x, YB + 2.0, bridge_z(x) - .55), (x, YB + 2.0, bridge_z(x)), (x, YB - 2.0, bridge_z(x))] for x in xs], 'deck', 'footbridge', closed=False)
    b = Batch()
    for s in (-1, 1):
        for x0, x1 in zip(xs, xs[1:]):
            b.beam('deck', (x0, YB + s * 1.9, bridge_z(x0) + .05), (x1, YB + s * 1.9, bridge_z(x1) + .05), .2, .2, ext=.01)
    for x in (31.5, 45.5):                                   # river piers with rounded noses
        zt = bridge_z(x) - .5
        b.box('concrete', x, YB, zt / 2, 1.0, 3.3, zt)
        for e in (-1, 1):
            V, F = b.g.setdefault('concrete', ([], []))
            C_ = 10
            o = len(V)
            for z in (0.0, zt):
                for i in range(C_ + 1):
                    a = math.pi * i / C_
                    V.append((x + .5 * math.cos(a), YB + e * (1.6 + .5 * math.sin(a)), z))
            m = C_ + 1
            F.append(tuple(range(m - 1, -1, -1))); F.append(tuple(m + i for i in range(m)))
            for i in range(C_):
                F.append((i, i + 1, m + i + 1, m + i))
            F.append((m - 1, 0, m, 2 * m - 1))
    zt = bridge_z(22.4) - .52
    b.box('concrete', 21.0, YB, zt / 2, 2.8, 4.6, zt)                       # near abutment on the rip-rap
    zt = bridge_z(FAR - 2.4) - .52
    b.box('concrete', FAR - 1.1, YB, zt / 2, 2.8, 4.6, zt)                 # far abutment
    for s in (-1, 1):                                       # railings
        posts = [(x, YB + s * 1.9, bridge_z(x) + .15) for x in xs[::2]]
        for q in posts:
            b.box('steel', q[0], q[1], q[2] + .5, .06, .06, 1.02)
        for q, r in zip(posts, posts[1:]):
            b.beam('steel', (q[0], q[1], q[2] + 1.0), (r[0], r[1], r[2] + 1.0), .07, .05, ext=.03)
            b.beam('mesh', (q[0], q[1], q[2] + .54), (r[0], r[1], r[2] + .54), .015, .84, ext=-.03)
    b.flush('footbridge')
    slab('Far landing', [(FAR - .4, YB - 2.4), (FAR + 4.0, YB - 2.4), (FAR + 4.0, YB + 2.4), (FAR - .4, YB + 2.4)], ZG - .05, ZG + .055, 'paving', 'footbridge')
    asphalt = [(FAR + 4.0, YB), (FAR + 9.8, YB)]
    ribbon('Far bank path', frames(spline(asphalt, 1.0)), 3.0, ZG - .02, ZG + .04, 'asphalt', 'footbridge')


# ---------------------------------------------------------------- pavilion

def batten_wall(m, lo, hi, z0, z1, hs, step=.3):
    """Vertical cedar battens on the outer face, stopped round every opening."""
    u = lo + .12
    while u < hi - .1:
        spans = [(z0 + .02, z1 - .02)]
        for h in hs:
            if h['u'] - h['w'] / 2 - .06 < u < h['u'] + h['w'] / 2 + .06:
                new = []
                for a, c in spans:
                    if c <= h['z'] - .06 or a >= h['z'] + h['h'] + .06:
                        new.append((a, c)); continue
                    if a < h['z'] - .06:
                        new.append((a, h['z'] - .06))
                    if c > h['z'] + h['h'] + .06:
                        new.append((h['z'] + h['h'] + .06, c))
                spans = new
        for a, c in spans:
            if c - a > .05:
                m.box('batten', u, -.012, (a + c) / 2, .05, .03, c - a)
        u += step


def door_m(m, f, h, inset=.12):
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    for s in (-1, 1):
        m.box('trim', u + s * (w / 2 - .03), inset, z + hh / 2, .06, .1, hh)
    m.box('trim', u, inset, z + hh - .03, w - .12, .1, .06)
    m.box('fascia', u, inset + .05, z + hh / 2 + .01, w - .12, .045, hh - .08)
    m.box('steel', u + w * .3, inset, z + 1.0, .03, .06, .3)
    register(f, h, inset, 'door', 'pavilion room')


Z0, Z1 = ZG + .14, ZG + 3.62


def pavilion():
    faces = {
        'SE': (C.Face((*L(-5.2, 0.0), 0.0), (*EV, 0.0), (*EU, 0.0), 'Pavilion south-east glazed face'), -3.6, 3.6,
               [hole('SE curtain wall', 0.0, ZG + .24, 6.6, 3.1)]),
        'SW': (C.Face((*L(0.0, -3.9), 0.0), (-EU[0], -EU[1], 0.0), (*EV, 0.0), 'Pavilion south-west face'), -3.4, 5.2,
               [hole('SW door', -1.6, ZG + .15, 1.0, 2.3, kind='door'), hole('SW corner glazing', 3.35, ZG + .24, 2.7, 3.1)]),
        'NE': (C.Face((*L(0.0, 3.9), 0.0), (*EU, 0.0), (-EV[0], -EV[1], 0.0), 'Pavilion north-east face'), -5.2, 3.4,
               [hole('NE clerestory a', -2.8, ZG + 2.3, 2.6, 1.0), hole('NE clerestory b', 0.4, ZG + 2.3, 2.6, 1.0)]),
        'NW': (C.Face((*L(3.4, 0.0), 0.0), (-EV[0], -EV[1], 0.0), (-EU[0], -EU[1], 0.0), 'Pavilion north-west porch face'), -3.6, 3.6,
               [hole('NW door a', -1.5, ZG + .15, .95, 2.2, kind='door'), hole('NW door b', 1.5, ZG + .15, .95, 2.2, kind='door')]),
    }
    for key, (f, lo, hi, hs) in faces.items():
        f.wall(f'Pavilion {key} wall', lo, hi, Z0, Z1, depth=T, role='timber', holes=hs)
        m = Merge(f)
        batten_wall(m, lo, hi, Z0, Z1, hs)
        for h in hs:
            if h.get('kind') == 'door':
                door_m(m, f, h)
            elif key == 'SE':
                framed(m, f, h, cols=5, rows=2, inset=.12, occupied='pavilion room', frame='trim')
            else:
                framed(m, f, h, cols=2 if h['w'] < 3.0 else 3, rows=2 if h['h'] > 2 else 1, inset=.12, occupied='pavilion room', frame='trim')
        m.flush(f'pavilion {key}')
    F0 = C.Face((*PC, 0.0), (*EU, 0.0), (*EV, 0.0), 'Pavilion frame')
    m = Merge(F0)
    m.box('paving', 0.0, 0.0, ZG + .025, 14.0, 11.0, .09)                       # paved apron
    m.box('concrete', 0.0, 0.0, ZG + .05, 12.3, 9.3, .2)                         # floor slab
    m.box('floor', -.9, 0.0, Z0 + .02, 7.9, 7.1, .04)                            # interior floor
    m.box('timber', 0.0, 0.0, ZG + 3.73, 12.4, 9.4, .24)                         # roof deck and timber soffit
    m.box('sedum3', 0.0, 0.0, ZG + 3.915, 12.2, 9.2, .14)                        # green roof build-up, planted
    for s in (-1, 1):                                                            # thin dark metal fascia
        m.box('fascia', 0.0, s * 4.73, ZG + 3.84, 12.52, .08, .5)
        m.box('fascia', s * 6.23, 0.0, ZG + 3.835, .08, 9.4, .49)
    for su in (-1, 1):                                                           # timber posts at the roof corners
        for sv in (-1, 1):
            m.box('post', su * 5.95, sv * 4.45, (ZG + .15 + ZG + 3.63) / 2, .2, .2, 3.48)
    for sv in (-1, 1):                                                           # porch beams at the open end
        m.box('post', 4.68, sv * 4.45, ZG + 3.5, 2.55, .16, .24)
    m.box('bench', -2.9, 0.0, ZG + .9, 1.0, 3.4, .06)                            # interior: long table and benches
    for su in (-1, 1):
        for sv in (-1, 1):
            m.box('steel', -2.9 + su * .4, sv * 1.5, ZG + .52, .05, .05, .72)
        m.box('bench', -2.9 + su * .85, 0.0, ZG + .58, .35, 3.2, .05)
        for sv in (-1, 1):
            m.box('steel', -2.9 + su * .85, sv * 1.4, ZG + .36, .05, .05, .42)
    m.box('interior', 2.6, 0.0, ZG + .62, .7, 5.0, .95)                          # counter along the back wall
    m.box('bench', 2.6, 0.0, ZG + 1.11, .78, 5.1, .04)
    m.flush('pavilion frame')
    b = Batch()
    roof = [(-6.0, 6.0), (-4.5, 4.5)]
    for i in range(90):                                                          # low sedum mounds, mottled, clear of the fascia
        u, v = RNG.uniform(-5.4, 5.4), RNG.uniform(-3.9, 3.9)
        x, y = L(u, v)
        r = RNG.uniform(.3, .55)
        lump(b, ('sedum', 'sedum2')[i % 2], x, y, ZG + 3.985 + r * .05, r * 1.3, r * 1.1, r * .3, .3)
    for i in range(130):
        u, v = RNG.uniform(*roof[0]), RNG.uniform(*roof[1])
        x, y = L(u, v)
        tuft(b, 'sedum2' if i % 2 else 'grass2', x, y, ZG + 3.98, RNG.uniform(.14, .26), .07)
    b.flush('green roof planting')
    C.qa_room_light('Pavilion room', (*L(-1.0, 0.0), ZG + 2.6), 120, 3.0)
    C.CONTACTS.append(dict(name='Pavilion: slab on the apron, walls on the slab, posts under the roof corners, sedum on the roof build-up', box=[*L(-6.2, -4.7), *L(6.2, 4.7)]))


# ---------------------------------------------------------------- furniture


def bench(b, x, y, ang):
    """Timber slat bench with a back on two dark steel end frames."""
    c, s = math.cos(ang), math.sin(ang)
    P = lambda u, v: (x + u * c - v * s, y + u * s + v * c)
    for k in range(4):
        q = P(0.0, -.2 + k * .12)
        obox(b, 'bench', q[0], q[1], ZG + .46, 2.0, .09, .04, ang)
    for k, z in enumerate((.62, .76)):
        q = P(0.0, .3 + k * .02)
        obox(b, 'bench', q[0], q[1], ZG + z, 2.0, .09, .12, ang)
    for e in (-.8, .8):
        for v, h in ((-.18, .44), (.24, .44)):
            q = P(e, v)
            obox(b, 'steel', q[0], q[1], ZG + .04 + h / 2, .06, .06, h, ang)
        q = P(e, .03); obox(b, 'steel', q[0], q[1], ZG + .42, .06, .5, .05, ang)
        q = P(e, .3); obox(b, 'steel', q[0], q[1], ZG + .66, .05, .05, .36, ang)


def furniture():
    b = Batch()
    for (u, v), ang in (((215, 300), math.radians(-65)), ((745, 840), math.radians(-45)), ((232, 690), 0.0)):
        x, y = px(u, v)
        bench(b, x, y, ang)
    for (u, v) in ((575, 860), (40, 110), (470, 470)):
        x, y = px(u, v)
        obox(b, 'corten', x, y, ZG + .48, .6, .45, 1.0, .4)
    b.flush('benches and bins')


def build():
    ground_and_river()
    paths()
    planting()
    trees()
    boardwalk()
    footbridge()
    pavilion()
    furniture()
    C.CONTACTS.append(dict(name="Prince's Island Park: island ground, rip-rap, river, paths, beds, trees, boardwalk, footbridge, pavilion", box=[X0, FAR + 10.0, Y0, Y1]))


LIGHT_RIG = dict(key=(-30, -40, 45), fill=(40, -20, 30), rear=(10, 45, 30), target=(0, 0, 2.0), gain=3.4)
