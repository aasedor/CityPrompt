"""Halifax Public Gardens, authored from the locked catalogue views of halifax_public_gardens / variant_0
(halifax_public_gardens_v0).

Read from the pixels (the top view governs the plan): a fenced rectangular Victorian garden block, its long axis
north-south, between city streets on all four sides. A straight brick-paved axis runs from the main south gate to the
north fence; an east-west cross path meets it at a round paved circle holding an octagonal white bandstand with a
pink-copper ogee roof, a balustrade, fretwork arches and a front stair, ringed by a flower bed. A great oval loop path
leaves the axis in a Y well north of the bandstand, swells out to cross the cross path near the side fences and comes
straight back south to the gate, so the axis, the cross path and the loop frame four leaf-shaped inner lawns, each with a long
planted carpet bed of white hydrangeas, lavender, purple and pink flowers, and four outer lawns under big mature
shade trees. Granite edging lines every path. A black wrought-iron picket fence on a granite curb closes the block;
the south front has a grand gate of two tall brick piers on granite bases with iron lanterns, an iron arch bearing
the gilded sign HALIFAX PUBLIC GARDENS / FOUNDED 1867 under a crest, double iron gates thrown open, and two lower
ball-capped side piers with gates where the loop paths enter. Benches line the loop, lamp posts stand at the circle
and the side entrances; brick mid-rises and a glass office block line the streets as context.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-halifax-public-gardens'
FX, FS, FN = 21.6, -29.2, 28.0                  # fence line: half-width, south and north (top view, 0.08 m per pixel)
AXW, CRW = 1.6, 2.2                             # axis and cross-path half-widths
LA, YJ = 14.6, 20.0                             # loop centre line crosses the cross path at x = +-LA; joins the axis in a Y at y = YJ
LX, LY = 6.2, -13.6                             # lower loop: straight legs at x = +-LX south of y = LY
LW = 1.2                                        # loop half-width
RC = 7.6                                        # paved circle round the bandstand
BED0, BED1 = 4.0, 5.2                           # flower ring round the bandstand
SW, SN, SS = 24.6, 31.0, -35.2                  # outer sidewalk lines (west/east, north, south)
ST = 9.0                                        # street width
ZA, ZC, ZL, ZF, ZO = .070, .076, .064, .088, .094   # paving tops: axis, cross, loop, forecourt, circle (no shared planes;
                                                    # the loop is lowest, so its ends die under the axis and forecourt)
ZK = .067                                       # paving top of the corner fillets where the paths meet
ZG = .04                                        # lawn top
EPS = .002
T = .3
PALETTE = dict(grass=(.34, .50, .20), grass2=(.40, .56, .24), paving=(.64, .53, .48), joint=(.46, .38, .35), granite=(.76, .75, .72),
    soil=(.25, .18, .12), white=(.93, .93, .89), lavender=(.62, .56, .80), purple=(.44, .31, .60), pink=(.88, .58, .68), magenta=(.74, .30, .52),
    shrub=(.20, .36, .15), tree=(.26, .44, .17), tree2=(.20, .37, .13), timber=(.33, .24, .17), hardware=(.07, .07, .08), gold=(.80, .63, .28),
    brick=(.60, .30, .22), stone=(.73, .71, .67), copper=(.75, .49, .41), copper2=(.60, .37, .30), paint=(.94, .93, .89), deck=(.60, .58, .54),
    shadow=(.19, .19, .20), glass=(.62, .70, .74), pale=(.98, .92, .70), concrete=(.77, .76, .73), asphalt=(.30, .30, .31), mark=(.92, .92, .90),
    bench=(.42, .31, .22), facade=(.62, .36, .28), facade2=(.80, .76, .68), facade3=(.46, .56, .63), dark=(.15, .17, .19), troof=(.46, .46, .46),
    trim=(.88, .87, .84))


def manifest(version):
    h = 14.0
    cams = G.camera_roster(2 * FX + 6.0, FN - FS + 6.0, h, [
        ('gate_arch', (1.5, -36.0, 2.2), (0.0, -29.2, 5.0), 32),
        ('gate_piers_fence', (-14.6, -36.0, 2.4), (-6.0, -29.2, 1.6), 30),
        ('bandstand', (2.5, -14.0, 1.9), (0.0, 0.0, 3.6), 30),
        ('bandstand_roof', (-6.5, -8.0, 9.0), (0.0, 0.0, 5.2), 34),
        ('carpet_beds', (-1.0, -20.0, 3.4), (-6.5, -8.0, .3), 32),
        ('inner_lawn_beds', (2.0, 18.0, 4.0), (-6.0, 6.5, .3), 30),
        ('loop_benches', (-3.0, 17.0, 2.0), (-12.5, 9.0, .8), 32),
        ('mature_trees', (-1.0, -27.0, 3.2), (-13.0, -14.0, 6.0), 28),
        ('side_entrance', (-27.5, 7.0, 2.2), (-21.6, 0.0, 1.4), 30),
        ('rear_north', (0.0, 36.0, 9.0), (0.0, 14.0, 1.0), 34)])
    for c in cams:
        if c['name'] == 'front':                  # the locked front: on the plaza outside the gate, east of the axis, looking north-north-west
            c.update(location=(7.6, -37.4, 1.65), target=(-4.6, -10.6, 3.6), lens=25, whole=False)
        elif c['name'] == 'front_corner':         # the locked oblique: high over the south street, looking north up the axis
            c.update(location=(0.0, -49.0, 27.0), target=(0.0, -5.0, 0.0), lens=30, whole=False)
        elif c['name'] == 'top':                  # the locked top view: the block with both side streets, north up
            c.update(location=(0.0, -.6, 120.0), target=(0.0, -.599, 0.0), ortho_scale=95.6, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(16.0, -52.0, 72.0), target=(0.0, -2.0, 0.0), lens=30, whole=False)   # over the south street, clear of every roof
        elif c['name'] == 'left_side':
            c.update(location=(-30.5, -6.0, 15.0), target=(0.0, 0.0, 1.5), lens=22, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(30.5, 6.0, 15.0), target=(0.0, 0.0, 1.5), lens=22, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(0.0, 38.5, 17.0), target=(0.0, -2.0, 0.0), lens=24, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(-30.0, 39.5, 24.0), target=(0.0, 0.0, 1.0), lens=28, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='halifax_public_gardens/variant_0 (halifax_public_gardens_v0)',
        measurement_contract=dict(dimensions_m=dict(width=2 * FX, depth=FN - FS, height=h),
            observed_storeys=0, storey_programme='open space: a fenced Victorian public garden with a bandstand; the street blocks are context',
            plan='43.2 x 57.2 m fenced block (top view at about 0.08 m per pixel): axis, cross path, paved bandstand circle, loop path joining the axis in a Y, filleted paving at every junction, four inner leaf-shaped carpet-bed lawns, four outer tree lawns',
            facade='black wrought-iron picket fence on a granite curb, brick gate piers with lanterns and a gilded iron sign arch, white octagonal bandstand with a pink-copper ogee roof',
            levels_m=[0.0, ZG, ZA, ZO, 1.0], inferred='the north and side entrances, bed planting mixes and the street blocks are teaching assumptions'),
        roof_contract=dict(type='open space; octagonal ogee copper bandstand roof', datum_m=0.0, crowns_m=[8.3]),
        identity_contract=dict(owner='fenced Victorian public garden: grand brick-and-iron sign gate, white octagonal bandstand with a copper roof at the centre of a paved circle, oval loop and cross paths framing leaf-shaped carpet beds of hydrangeas, mature shade trees'),
        material_contract=dict(profile='source-palette clay: warm brick pavers with granite edging, fresh green lawns, white hydrangeas with lavender, purple and pink flowers on dark mulch, deep green trees, black iron, red brick piers, gold lettering, white bandstand, pink-copper roof', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='strolling, sitting, bandstand concerts, horticultural display'),
        contact_contract=['Grade-zero streets and lawns', 'Paths on the lawn', 'Bandstand plinth on the paved circle', 'Fence curb and piers on grade'],
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
# ---- Halifax Public Gardens ----

import random
from shapely.geometry import LineString, Point, Polygon, box as sbox
from shapely.ops import unary_union

RNG = random.Random(1867)                       # fixed seed: the same flower mounds on every build
ICO_V = [(-1, 1.618, 0), (1, 1.618, 0), (-1, -1.618, 0), (1, -1.618, 0), (0, -1, 1.618), (0, 1, 1.618), (0, -1, -1.618), (0, 1, -1.618),
         (1.618, 0, -1), (1.618, 0, 1), (-1.618, 0, -1), (-1.618, 0, 1)]
ICO_F = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
         (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
FORE_Y, TIP_X, TIP_R = -23.6, 3.3, 1.7          # forecourt top edge and the rounded tips of the two inner south lawns


def lump(b, role, cx, cy, cz, rx, ry, rz, jitter=.16):
    """A rounded low-poly mound (a jittered icosahedron): a flower clump, a hydrangea or a shrub."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    s = 1 / 1.902
    for (x, y, z) in ICO_V:
        k = 1 + RNG.uniform(-jitter, jitter)
        V.append((cx + x * s * rx * k, cy + y * s * ry * k, cz + z * s * rz * k))
    F.extend(tuple(o + i for i in f) for f in ICO_F)


def dome(b, role, cx, cy, z0, rx, ry, h, seg=6):
    """A grounded rounded shrub lobe: a flat base ring sunk 3 cm below the surface at z0, a bulging belly ring, a
    shoulder ring and a crown point, so it sits on the ground like a plant and never balances on a vertex."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    ph = RNG.uniform(0, math.pi)
    for dz, k in ((-.03, .96), (h * .40, 1.06), (h * .76, .74)):
        for i in range(seg):
            a = ph + 2 * math.pi * i / seg
            j = 1 + RNG.uniform(-.07, .07)
            V.append((cx + math.cos(a) * rx * k * j, cy + math.sin(a) * ry * k * j, z0 + dz))
    top, bot = o + 3 * seg, o + 3 * seg + 1
    V.append((cx, cy, z0 + h)); V.append((cx, cy, z0 - .03))
    for r in range(2):
        for i in range(seg):
            a, c = o + r * seg + i, o + r * seg + (i + 1) % seg
            F.append((a, c, c + seg, a + seg))
    for i in range(seg):
        F.append((o + 2 * seg + i, o + 2 * seg + (i + 1) % seg, top))
        F.append((o + (i + 1) % seg, o + i, bot))


def shrub(b, role, x, y, z0, r, h):
    """A free-standing shrub or hydrangea as a cluster of grounded lobes: a broad green base with flower heads (white,
    pink or purple) or more foliage lobes on top."""
    dome(b, 'shrub', x, y, z0, r, r * RNG.uniform(.9, 1.0), h * .62, 7)
    lobes = 3 if r < .85 else 4
    for k in range(lobes):
        a = 2 * math.pi * k / lobes + RNG.uniform(-.3, .3)
        d = r * .42
        dome(b, role, x + math.cos(a) * d, y + math.sin(a) * d, z0 + h * .28, r * .52, r * .5, h * .66)
    dome(b, role, x, y, z0 + h * .40, r * .5, r * .5, h * .6)


def mound(b, role, x, y, zb, w, h):
    """A planted mound w wide and h high standing on a surface at zb (the lump's lowest point stays at or above zb - 2 cm)."""
    lump(b, role, x, y, zb + .47 * h, w / 2, w / 2, h / 2)


def ngon(b, role, cx, cy, z0, z1, r, n=12, phase=.5, cone=False):
    """Vertical n-gon prism (or cone) added to a Batch."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for i in range(n):
        a = 2 * math.pi * (i + phase) / n
        V.append((cx + r * math.cos(a), cy + r * math.sin(a), z0))
    if cone:
        V.append((cx, cy, z1))
        F.append(tuple(o + i for i in range(n - 1, -1, -1)))
        for i in range(n):
            F.append((o + i, o + (i + 1) % n, o + n))
        return
    for i in range(n):
        a = 2 * math.pi * (i + phase) / n
        V.append((cx + r * math.cos(a), cy + r * math.sin(a), z1))
    F.append(tuple(o + i for i in range(n - 1, -1, -1)))
    F.append(tuple(o + n + i for i in range(n)))
    for i in range(n):
        j = (i + 1) % n
        F.append((o + i, o + j, o + n + j, o + n + i))


def spike(b, role, x, y, z0, z1, w, tip):
    """A square picket with a pyramid spear point: one closed mesh."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    h = w / 2
    for z in (z0, z1):
        V.extend([(x - h, y - h, z), (x + h, y - h, z), (x + h, y + h, z), (x - h, y + h, z)])
    V.append((x, y, z1 + tip))
    F.append((o + 3, o + 2, o + 1, o + 0))
    for i in range(4):
        j = (i + 1) % 4
        F.append((o + i, o + j, o + 4 + j, o + 4 + i))
        F.append((o + 4 + i, o + 4 + j, o + 8))


def balls(name, role, centres, r, seg=8, rings=5, module='gates'):
    """One smooth-shaded mesh of low-poly UV spheres."""
    V, F = [], []
    for (x, y, z) in centres:
        o = len(V)
        V.append((x, y, z + r))
        for k in range(1, rings):
            ph = math.pi * k / rings
            for j in range(seg):
                th = 2 * math.pi * j / seg
                V.append((x + r * math.sin(ph) * math.cos(th), y + r * math.sin(ph) * math.sin(th), z + r * math.cos(ph)))
        V.append((x, y, z - r))
        last = o + 1 + (rings - 1) * seg
        for j in range(seg):
            jn = (j + 1) % seg
            F.append((o, o + 1 + j, o + 1 + jn))
            for k in range(rings - 2):
                a, b_ = o + 1 + k * seg, o + 1 + (k + 1) * seg
                F.append((a + j, b_ + j, b_ + jn, a + jn))
            c = o + 1 + (rings - 2) * seg
            F.append((c + jn, c + j, last))
    obj = C.mesh(name, V, F, role, module)
    for f in obj.data.polygons:
        f.use_smooth = True


# ---------------------------------------------------------------- plan geometry

def resample(pts, ds):
    """Equal arc-length resampling of a dense polyline."""
    out = [pts[0]]
    acc = 0.0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, by - ay)
        while acc + L >= ds:
            t = (ds - acc) / L
            ax, ay = ax + (bx - ax) * t, ay + (by - ay) * t
            out.append((ax, ay))
            L = math.hypot(bx - ax, by - ay); acc = 0.0
        acc += L
    if math.hypot(out[-1][0] - pts[-1][0], out[-1][1] - pts[-1][1]) > ds * .3:
        out.append(pts[-1])
    else:
        out[-1] = pts[-1]
    return out


def bezier(p0, p1, p2, p3, n=40):
    return [tuple((1 - u) ** 3 * p0[c] + 3 * (1 - u) ** 2 * u * p1[c] + 3 * (1 - u) * u * u * p2[c] + u ** 3 * p3[c] for c in range(2))
            for u in (i / n for i in range(n))]


def loop_half(s):
    """One half of the loop centre line (s = -1 west, +1 east): from the south gate up the straight leg, out through
    an S-bend to the cross path, then up a broad arc that swings in and joins the axis in a Y at y = YJ, as the top
    view shows (no right-angle T). Tangent-continuous; its north end dies under the higher axis paving."""
    pts = [(s * LX, FS - .05 + (LY - FS + .05) * i / 20) for i in range(20)]
    pts += bezier((s * LX, LY), (s * LX, LY + 5.6), (s * LA, -5.4), (s * LA, 0.0))
    pts += bezier((s * LA, 0.0), (s * LA, 10.0), (s * 3.6, 16.0), (0.0, YJ), 60) + [(0.0, YJ)]
    return resample(pts, .25)


LOOPS = [loop_half(-1), loop_half(1)]


def offsets(pts, d):
    """Offset a polyline sideways by d (positive to the left of travel)."""
    out = []
    for i, (x, y) in enumerate(pts):
        ax, ay = pts[max(i - 1, 0)]; bx, by = pts[min(i + 1, len(pts) - 1)]
        L = math.hypot(bx - ax, by - ay)
        out.append((x - (by - ay) / L * d, y + (bx - ax) / L * d))
    return out


def ccw(poly):
    area = sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(len(poly)))
    return poly if area > 0 else poly[::-1]


def seg_dist(px, py, pts):
    best = 1e9
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2)) if L2 > 0 else 0.0
        best = min(best, math.hypot(px - ax - t * dx, py - ay - t * dy))
    return best


def in_fore(x, y, m=0.0):
    return FS - .1 < y < FORE_Y - m and abs(x) < LX + LW - m and math.hypot(abs(x) - TIP_X, y - FORE_Y) > TIP_R + m


REGIONS = dict(
    axis=lambda x, y, m: abs(x) < AXW - m and FS - .1 < y < FN + .1,
    cross=lambda x, y, m: abs(y) < CRW - m and abs(x) < FX + .1,
    circle=lambda x, y, m: math.hypot(x, y) < RC - m,
    loop=lambda x, y, m: min(seg_dist(x, y, L) for L in LOOPS) < LW - m,
    fore=lambda x, y, m: in_fore(x, y, m))


def paved(x, y, skip=(), m=.06):
    """True where another paved area covers the point (with a margin), so edging and joints stop at junctions."""
    return any(f(x, y, m) for k, f in REGIONS.items() if k not in skip)


def runs(points, skip, m=.06):
    """Split a sampled edge into maximal runs of points not covered by other paved areas."""
    out, cur = [], []
    for p in points:
        if paved(p[0], p[1], skip, m):
            if len(cur) > 1:
                out.append(cur)
            cur = []
        else:
            cur.append(p)
    if len(cur) > 1:
        out.append(cur)
    return out


def edging(b, pts, skip, straight=False, z=.07, h=.08, w=.10):
    """Granite path edging laid along a sampled edge, broken where another path crosses."""
    for k, run in enumerate(runs(pts, skip)):
        if straight:
            (ax, ay), (bx, by) = run[0], run[-1]
            b.beam('granite', (ax, ay, z), (bx, by, z), w, h + .004 * (k % 2), ext=.0)
            continue
        for i, ((ax, ay), (bx, by)) in enumerate(zip(run, run[1:])):
            b.beam('granite', (ax, ay, z), (bx, by, z), w + .004 * (i % 2), h + .004 * (i % 2), ext=.02)


def line(a, b, ds=.25):
    (ax, ay), (bx, by) = a, b
    n = max(1, int(math.hypot(bx - ax, by - ay) / ds))
    return [(ax + (bx - ax) * i / n, ay + (by - ay) * i / n) for i in range(n + 1)]


def arc(cx, cy, r, a0, a1, ds=.35):
    n = max(2, int(abs(a1 - a0) * r / ds))
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


# ---------------------------------------------------------------- ground, streets and paths

def ground():
    C.box('Garden lawn', (0.0, (FS + FN) / 2, ZG / 2), (2 * FX - .1, FN - FS - .1, ZG), 'grass', 'lawns', 0)
    for s in (-1, 1):                                                          # lawn strips outside the south fence
        C.box('Outer lawn strip', (s * (10.0 + FX) / 2, (FS - 2.8 + FS) / 2 - .02, .05), ((FX - 10.0) - .04, 2.76, .1), 'grass2', 'lawns', 0)
        C.box('Side sidewalk', (s * (SW + FX + .05) / 2, (FS - 2.8 + FN) / 2, .06), (SW - FX - .05, FN - FS + 2.8, .12), 'concrete', 'sidewalks', 0)
        C.box('Side street', (s * (SW + .02 + ST / 2), (SS - ST + SN + ST) / 2, .01), (ST - .04, SN - SS + 2 * ST, .02), 'asphalt', 'streets', 0)
        C.box('Far sidewalk', (s * (SW + ST + 1.2), (SS - ST + SN + ST) / 2, .06), (2.36, SN - SS + 2 * ST, .12), 'concrete', 'sidewalks', 0)
    C.box('North sidewalk', (0.0, (FN + SN) / 2, .064), (2 * SW, SN - FN, .12), 'concrete', 'sidewalks', 0)
    C.box('South sidewalk', (0.0, (SS + FS - 2.8) / 2, .064), (2 * SW, FS - 2.8 - SS, .12), 'concrete', 'sidewalks', 0)
    C.box('South gate plaza', (0.0, FS - 1.4, .055), (20.0 - .04, 2.76, .11), 'paving', 'plaza', 0)
    C.box('North street', (0.0, SN + ST / 2, .0105), (2 * (SW + ST) - .04, ST - .04, .021), 'asphalt', 'streets', 0)
    C.box('South street', (0.0, SS - ST / 2, .0105), (2 * (SW + ST) - .04, ST - .04, .021), 'asphalt', 'streets', 0)
    C.box('North far sidewalk', (0.0, SN + ST + 1.2, .064), (2 * (SW + ST + 2.38), 2.36, .12), 'concrete', 'sidewalks', 0)
    b = Batch()
    for s in (-1, 1):                                                          # granite street curbs
        b.box('granite', s * SW, (SN + SS) / 2, .07, .18, SN - SS + .18, .14)
        b.box('granite', s * (SW + ST), (SS - ST + SN + ST) / 2, .072, .18, SN - SS + 2 * ST, .144)
    b.box('granite', 0.0, SN, .072, 2 * SW + .18, .18, .144)
    b.box('granite', 0.0, SS, .072, 2 * SW + .18, .18, .144)
    b.box('granite', 0.0, SN + ST, .074, 2 * (SW + ST) + .18, .18, .148)
    for k in range(-8, 8):                                                     # lane markings
        b.box('mark', -(SW + ST / 2), k * 4.0 + 1.0, .0235, .12, 2.0, .006)
        b.box('mark', SW + ST / 2, k * 4.0 + 1.0, .0235, .12, 2.0, .006)
    for k in range(-5, 6):
        b.box('mark', k * 4.0 + 2.0, SN + ST / 2, .0235, 2.0, .12, .006)
        b.box('mark', k * 4.0 + 2.0, SS - ST / 2, .0235, 2.0, .12, .006)
    for k in range(int(2 * SW / 2.0)):                                         # sidewalk scoring
        x = -SW + 1.0 + k * 2.0
        b.box('joint', x, (SS + FS - 2.8) / 2, .1255, .025, FS - 2.8 - SS - .1, .003)
        b.box('joint', x, (FN + SN) / 2, .1255, .025, SN - FN - .1, .003)
    for s in (-1, 1):
        for k in range(int((FN - FS + 2.8) / 2.0)):
            b.box('joint', s * (SW + FX) / 2, FS - 2.8 + 1.0 + k * 2.0, .1215, SW - FX - .2, .025, .003)
    for k in range(int(20.0 / .45)):                                           # brick plaza courses outside the gate
        b.box('joint', -10.0 + .25 + k * .45, FS - 1.4, .1115, .02, 2.7, .003)
    b.flush('streets and plaza')


def strip_mesh(name, A, B, z0, z1, role, module):
    """Closed slab between two matched polylines (A[i] and B[i] form a cross-section): quads only, no large n-gon
    to triangulate, so long curved paths and beds cannot fold."""
    n = len(A)
    V = [(x, y, z1) for x, y in A] + [(x, y, z1) for x, y in B] + [(x, y, z0) for x, y in A] + [(x, y, z0) for x, y in B]
    a1, b1, a0, b0 = 0, n, 2 * n, 3 * n
    F = []
    for i in range(n - 1):
        F.append((a1 + i, a1 + i + 1, b1 + i + 1, b1 + i))                   # top
        F.append((b0 + i, b0 + i + 1, a0 + i + 1, a0 + i))                   # bottom
        F.append((a0 + i, a0 + i + 1, a1 + i + 1, a1 + i))                   # side along A
        F.append((b1 + i, b1 + i + 1, b0 + i + 1, b0 + i))                   # side along B
    F.append((a0, a1, b1, b0)); F.append((b0 + n - 1, b1 + n - 1, a1 + n - 1, a0 + n - 1))
    return C.mesh(name, V, F, role, module)


def ribbon(name, pts, hw, z0, z1, module='paths'):
    left, right = offsets(pts, hw), offsets(pts, -hw)
    strip_mesh(name, left, right, z0, z1, 'paving', module)
    return left, right


def paths():
    b = Batch()
    C.box('Axis path', (0.0, (FS + FN) / 2, (.02 + ZA) / 2), (2 * AXW, FN - FS + .1, ZA - .02), 'paving', 'paths', 0)
    C.box('Cross path', (0.0, 0.0, (.025 + ZC) / 2), (2 * FX + .1, 2 * CRW, ZC - .025), 'paving', 'paths', 0)
    for k, L in enumerate(LOOPS):
        ribbon(f'Loop path {"west" if k == 0 else "east"}', L[::3] if (len(L) - 1) % 3 == 0 else L[::3] + [L[-1]], LW, .03, ZL)
    C.prism('Bandstand circle', [(RC * math.cos(2 * math.pi * i / 64), RC * math.sin(2 * math.pi * i / 64)) for i in range(64)], 'z', .04, ZO, 'paving', 'paths')
    xs = sorted(set([round(-LX - LW + i * .3, 4) for i in range(int(2 * (LX + LW) / .3) + 1)] + [LX + LW, -AXW, AXW, -LX + LW, LX - LW]))
    top = [(x, FORE_Y - math.sqrt(max(0.0, TIP_R ** 2 - (abs(x) - TIP_X) ** 2)) if abs(abs(x) - TIP_X) < TIP_R else FORE_Y) for x in xs]
    strip_mesh('Gate forecourt', [(x, FS - .05) for x in xs], top, .035, ZF, 'paving', 'paths')
    # The long paths stay plain brick colour (plank-like transverse joints read as a boardwalk); the circle keeps
    # its concentric and radial courses.
    for r in (5.8, 6.4, 7.0):                                                  # concentric courses on the circle
        ring = arc(0.0, 0.0, r, 0.0, 2 * math.pi, 1.0)
        for i, ((ax, ay), (cx, cy)) in enumerate(zip(ring, ring[1:])):
            b.beam('joint', (ax, ay, ZO + .0025), (cx, cy, ZO + .0025), .022 + .002 * (i % 2), .003, ext=.01)
    for k in range(24):
        a = 2 * math.pi * k / 24
        b.beam('joint', (5.3 * math.cos(a), 5.3 * math.sin(a), ZO + .0025), (7.5 * math.cos(a), 7.5 * math.sin(a), ZO + .0025), .022, .003)
    b.flush('paver joints')
    # Broad filleted paving where the paths meet, so every lawn reads as a soft-cornered island, then granite
    # edging along the lawn outlines.
    shapes = path_shapes()
    union = unary_union(list(shapes.values()))
    fil = []
    for key_a, key_b, cx, cy, r in junctions():
        pair = shapes[key_a].union(shapes[key_b])
        piece = pair.buffer(r, 16).buffer(-r, 16).difference(pair).intersection(Point(cx, cy).buffer(r * 2.6 + 1.6, 24))
        fil.append(piece)
    fil = unary_union(fil).buffer(.02).intersection(GARDEN)
    for k, g in enumerate(polys(fil)):
        if g.area > .03:
            C.prism(f'Path junction fillet {k}', list(g.simplify(.015).exterior.coords)[:-1], 'z', .036, ZK, 'paving', 'paths')
    paved_all = union.union(fil)
    b = Batch()
    for g in polys(GARDEN.difference(paved_all)):
        if g.area < .2:
            continue
        pts = list(g.simplify(.02).exterior.coords)
        for i, ((ax, ay), (cx2, cy2)) in enumerate(zip(pts, pts[1:])):
            if on_fence(ax, ay) and on_fence(cx2, cy2):
                continue
            if math.hypot(cx2 - ax, cy2 - ay) < .01:
                continue
            b.beam('granite', (ax, ay, .07), (cx2, cy2, .07), .10 + .004 * (i % 2), .08 + .004 * (i % 2), ext=.02)
    b.flush('path edging')
    return paved_all


GARDEN = sbox(-FX + .12, FS + .12, FX - .12, FN - .12)


def on_fence(x, y):
    return abs(x) > FX - .2 or y < FS + .2 or y > FN - .2


def polys(g):
    return [g] if g.geom_type == 'Polygon' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']


def path_shapes():
    """The paved areas as plan polygons; paths are carried past the fence so the fillets never act at the fence."""
    xs = [-LX - LW + i * .25 for i in range(int(2 * (LX + LW) / .25) + 1)]
    top = [(x, FORE_Y - math.sqrt(max(0.0, TIP_R ** 2 - (abs(x) - TIP_X) ** 2)) if abs(abs(x) - TIP_X) < TIP_R else FORE_Y) for x in xs]
    S = dict(axis=sbox(-AXW, FS - 6, AXW, FN + 6), cross=sbox(-FX - 6, -CRW, FX + 6, CRW), circle=Point(0, 0).buffer(RC, 32),
             fore=Polygon([(xs[0], FS - 6)] + top + [(xs[-1], FS - 6)]))
    for k, L in enumerate(LOOPS):
        S[f'loop{k}'] = LineString([(x, FS - 6 if y < FS + .1 else y) for x, y in L]).buffer(LW, 16, cap_style=2)
    return S


def junctions():
    """(path, path, corner centre, fillet radius) for every lawn corner: circle with axis and with cross path,
    loop with cross path, and the small rounded tips where each loop arc meets the axis."""
    out = []
    for sy in (-1, 1):
        out.append(('circle', 'axis', 0.0, sy * math.sqrt(RC * RC - AXW * AXW), 2.0))
    for s in (-1, 1):
        out.append(('circle', 'cross', s * math.sqrt(RC * RC - CRW * CRW), 0.0, 2.0))
        out.append((f'loop{0 if s < 0 else 1}', 'cross', s * LA, 0.0, 2.2))
        L = LOOPS[0 if s < 0 else 1]
        edge = LineString(offsets(L, s * LW))                               # the inner (lawn) edge of the north arc
        tip = edge.intersection(LineString([(s * AXW, 4.0), (s * AXW, YJ)]))
        if not tip.is_empty:
            p = tip if tip.geom_type == 'Point' else min(tip.geoms, key=lambda q: q.y)
            out.append((f'loop{0 if s < 0 else 1}', 'axis', p.x, p.y, .7))
    return out


# ---------------------------------------------------------------- planting

FLOWERS = ('lavender', 'purple', 'pink', 'magenta')


def smooth(pts, n=10):
    """Catmull-Rom curve through the control points."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            u = k / n
            out.append(tuple(.5 * (2 * p1[c] + (-p0[c] + p2[c]) * u + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * u * u
                                   + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * u ** 3) for c in range(2)))
    out.append(pts[-1])
    return out


def bed_outline(spine, width):
    """Leaf-shaped bed: a smooth spine with a width that tapers to points at both ends."""
    pts = resample(smooth(spine), .25)
    L = len(pts) - 1
    left, right = [], []
    for i, (x, y) in enumerate(pts):
        ax, ay = pts[max(i - 1, 0)]; bx, by = pts[min(i + 1, L)]
        d = math.hypot(bx - ax, by - ay)
        nx, ny = -(by - ay) / d, (bx - ax) / d
        w = width / 2 * max(.05, math.sin(math.pi * i / L)) ** .55
        left.append((x + nx * w, y + ny * w)); right.append((x - nx * w, y - ny * w))
    return pts, left, right


def carpet_bed(name, spine, width):
    """A raised mulch bed with granite-free soft edge, planted in bands: white hydrangea mounds along the spine,
    lavender and purple either side, low pink and magenta at the edges."""
    pts, left, right = bed_outline(spine, width)
    strip_mesh(name, left[::2] + ([left[-1]] if len(left) % 2 == 0 else []), right[::2] + ([right[-1]] if len(right) % 2 == 0 else []), .02, .10, 'soil', 'flower beds')
    b = Batch()
    L = len(pts) - 1
    for i in range(1, L, 3):
        x, y = pts[i]
        w = width / 2 * math.sin(math.pi * i / L) ** .55
        ax, ay = pts[i - 1]; bx, by = pts[i + 1]
        d = math.hypot(bx - ax, by - ay); nx, ny = -(by - ay) / d, (bx - ax) / d
        if (i // 3) % 2 == 0:
            mound(b, 'white', x, y, .10, 1.1, .85)                             # hydrangea mound on the spine
        else:
            mound(b, 'shrub', x, y, .10, 1.0, .7)
        for side in (-1, 1):
            j = i // 3
            for f, role, hgt in ((.5, FLOWERS[(j + (side > 0)) % 2] if j % 3 else 'shrub', .55), (.84, FLOWERS[2 + j % 2] if j % 3 != 1 else 'shrub', .4)):
                if w * f < .35:
                    continue
                mound(b, role, x + side * nx * w * f, y + side * ny * w * f, .10, .85, hgt)
    b.flush(name)


def border(name, x0, x1, y0, y1, colours=('white', 'shrub', 'lavender')):
    """A straight shrub-and-flower border along a path."""
    C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, .06), (x1 - x0, y1 - y0, .08), 'soil', 'flower beds', 0)
    b = Batch()
    n = max(2, int((y1 - y0) / .8))
    for i in range(n):
        y = y0 + .4 + (y1 - y0 - .8) * i / (n - 1)
        role = colours[i % len(colours)]
        hgt = .75 if role == 'white' else .55
        mound(b, role, (x0 + x1) / 2 + RNG.uniform(-.15, .15), y, .10, (x1 - x0) * 1.0, hgt)
    b.flush(name)


def shade_tree(name, x, y, h, r):
    """A broad mature deciduous tree: a stout trunk, limbs and a domed crown of overlapping masses."""
    C.rod(f'{name} trunk', (x, y, ZG - .01), (x + .15, y + .1, h * .5), .18 + .025 * r, 'timber', 'trees', 8)
    for k in range(3):
        a = 2 * math.pi * k / 3 + .4
        C.rod(f'{name} limb', (x + .1, y, h * .38), (x + math.cos(a) * r * .5, y + math.sin(a) * r * .5, h * .6), .07 + .012 * r, 'timber', 'trees', 6)
    A.foliage(f'{name} crown', (x, y, h * .64), (r * .86, r * .86, r * .58), role='tree', detail=3 if r > 5 else 2)
    for k in range(6):
        a = 2 * math.pi * k / 6 + RNG.uniform(0, .5)
        rr = r * (.55 if k % 2 else .62)
        A.foliage(f'{name} crown mass', (x + math.cos(a) * r * .5, y + math.sin(a) * r * .5, h * (.54 + .07 * (k % 3))),
                  (rr, rr * RNG.uniform(.85, 1.1), r * .42), role='tree2' if k % 2 else 'tree', detail=2 if k in (0, 3) else 1)
    A.foliage(f'{name} crown top', (x - .2 * r, y + .1 * r, h * .64 + r * .42), (r * .5, r * .5, r * .32), role='tree', detail=1)


TREES = [('South-west giant', -12.8, -14.0, 14.5, 7.0), ('South-west elm', -18.4, -7.4, 10.0, 3.4), ('South-west small', -19.2, -22.6, 6.5, 2.2),
         ('South-east giant', 15.0, -17.0, 14.0, 6.8), ('South-east elm', 19.2, -4.8, 9.0, 3.0), ('South-east small', 19.4, -10.6, 7.5, 2.5),
         ('West row 1', -18.6, 12.4, 12.0, 4.6), ('West row 2', -18.8, 21.6, 13.0, 4.8), ('North-west', -12.4, 25.4, 12.0, 4.2),
         ('East row 1', 19.2, 14.0, 11.0, 4.0), ('East row 2', 16.6, 22.8, 11.0, 3.8), ('East small', 18.4, 3.9, 8.5, 2.6),
         ('North-east', 9.0, 25.6, 11.5, 4.0), ('North-west small', -7.2, 25.8, 9.0, 2.8)]


def planting():
    # Four inner carpet beds (top view: long leaves across each inner lawn).
    for sx in (-1, 1):
        carpet_bed(f'South inner bed {"west" if sx < 0 else "east"}', [(sx * 3.3, -22.6), (sx * 3.4, -17.0), (sx * 3.6, -12.4), (sx * 5.0, -8.4), (sx * 9.4, -3.6)], 2.8)
        carpet_bed(f'North inner bed {"west" if sx < 0 else "east"}', [(sx * 2.7, 12.0), (sx * 5.0, 9.6), (sx * 8.0, 6.8), (sx * 11.4, 3.6)], 3.0)
        border(f'North axis border {"west" if sx < 0 else "east"}', *(sorted((sx * (AXW + .45), sx * (AXW + 1.65)))), YJ + .9, 26.8)
    # The flower ring round the bandstand, broken at the stair.
    a0, a1 = math.radians(-69), math.radians(249)
    n = int((a1 - a0) * BED1 / .3)
    strip_mesh('Bandstand flower ring', [(BED1 * math.cos(a0 + (a1 - a0) * i / n), BED1 * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)],
               [(BED0 * math.cos(a0 + (a1 - a0) * i / n), BED0 * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)], .06, .13, 'soil', 'flower beds')
    b = Batch()
    for r in (BED0, BED1):
        pts = arc(0.0, 0.0, r, a0, a1, .4)
        for i, ((ax, ay), (cx, cy)) in enumerate(zip(pts, pts[1:])):
            b.beam('granite', (ax, ay, .125), (cx, cy, .125), .10 + .004 * (i % 2), .07 + .004 * (i % 2), ext=.02)
    for k, (x, y) in enumerate(arc(0.0, 0.0, 4.6, a0 + .08, a1 - .08, .62)):
        role = ('white', 'pink', 'lavender', 'magenta', 'white', 'purple')[k % 6]
        hgt = .7 if role == 'white' else .42
        mound(b, role, x, y, .13, .75, hgt)
    # Shrubs and hydrangeas along the fence and by the gates (top view: round shrubs at the south corners and gates).
    for (x, y, r, role) in ((-10.6, -27.4, .9, 'shrub'), (10.4, -27.4, .9, 'shrub'), (-19.8, -27.6, .8, 'white'), (-18.4, -27.8, .7, 'pink'),
                            (19.6, -27.6, .8, 'white'), (18.2, -27.8, .7, 'purple'), (-20.2, -1.0 - 3.0, .9, 'shrub'), (20.2, -4.2, .9, 'shrub'),
                            (-20.4, 5.0, .8, 'white'), (20.4, 5.2, .8, 'shrub'), (4.4, 19.6, 1.2, 'white'), (-4.8, 17.6, 1.0, 'white'),
                            (-20.4, -16.0, .7, 'shrub'), (20.4, -24.0, .8, 'shrub'), (6.0, 26.6, .9, 'shrub'), (-4.0, 26.8, .8, 'pink')):
        shrub(b, role, x, y, ZG, r, 1.3 * r)
    for s in (-1, 1):                                                          # low hedges along the outer lawn strips
        for k in range(8):
            dome(b, 'shrub', s * (11.0 + k * 1.3), FS - .9, .10, .72, .66, .8, 7)
    b.flush('planting')
    for t in TREES:
        shade_tree(*t)


# ---------------------------------------------------------------- bandstand

AP, RP = 3.3, 3.3                               # plinth apothem; post radius (to the octagon corners)


def side_frame(k, a):
    """Centre, tangent and outward normal of plinth side k (k = 0 faces south) at apothem a."""
    th = -math.pi / 2 + k * math.pi / 4
    n = (math.cos(th), math.sin(th))
    return (n[0] * a, n[1] * a), (-n[1], n[0]), n


def bandstand():
    R8 = AP / math.cos(math.pi / 8)
    octo = lambda r: [(r * math.cos(math.pi / 8 + k * math.pi / 4 - math.pi / 2), r * math.sin(math.pi / 8 + k * math.pi / 4 - math.pi / 2)) for k in range(8)]
    C.prism('Bandstand plinth', octo(R8), 'z', .05, .95, 'shadow', 'bandstand')
    C.prism('Bandstand deck', octo((AP + .16) / math.cos(math.pi / 8)), 'z', .95, 1.05, 'paint', 'bandstand')
    C.prism('Bandstand floor', octo((AP - .05) / math.cos(math.pi / 8)), 'z', 1.04, 1.065, 'deck', 'bandstand')
    b = Batch()
    L = 2 * R8 * math.sin(math.pi / 8)
    for k in range(1, 8):                                                      # lattice skirt panels on seven sides
        (cx, cy), (tx, ty), (nx, ny) = side_frame(k, AP)
        P = lambda u, d, z: (cx + tx * u + nx * d, cy + ty * u + ny * d, z)
        b.beam('paint', P(-L / 2, .05, .85), P(L / 2, .05, .85), .1, .14)
        b.beam('paint', P(-L / 2, .05, .14), P(L / 2, .05, .14), .1, .16)
        for s in (-1, 1):
            b.beam('paint', P(s * (L / 2 - .19), .06, .5), P(s * (L / 2 - .01), .06, .5), .12, .9)
        u0, u1, z0, z1 = -L / 2 + .2, L / 2 - .2, .22, .78
        for fam in (1, -1):
            c = u0 - (z1 - z0)
            while c < u1 + (z1 - z0):
                seg = []                                                       # the diagonal u = c + fam * (z - z0), clipped to the panel
                for z in (z0, z1):
                    u = c + fam * (z - z0)
                    if u0 <= u <= u1:
                        seg.append((u, z))
                for u in (u0, u1):
                    z = z0 + (u - c) / fam
                    if z0 < z < z1:
                        seg.append((u, z))
                if len(seg) >= 2:
                    seg.sort()
                    (ua, za), (ub, zb) = seg[0], seg[-1]
                    if math.hypot(ub - ua, zb - za) > .08:
                        b.beam('paint', P(ua, .04 + .012 * (fam > 0), za), P(ub, .04 + .012 * (fam > 0), zb), .035, .03)
                c += .38
    # Front stair on the south side between low cheek walls.
    rise = (1.05 - ZO) / 6
    for i in range(5):
        y0 = -AP - (5 - i) * .32
        b.box('paint', 0.0, (y0 - AP + .05) / 2, (.06 + ZO + (i + 1) * rise) / 2, 2.2 - .004 * i, -AP + .05 - y0, ZO + (i + 1) * rise - .06)
    for x0, x1 in ((1.105, 1.305), (-1.305, -1.105)):
        C.prism('Bandstand stair cheek', [(-AP + .02, .06), (-AP - 1.75, .06), (-AP - 1.75, .36), (-AP + .02, 1.17)], 'x', x0, x1, 'paint', 'bandstand')
    # Eight posts on bases with capitals; balustrades on seven sides; frieze and fretwork arches.
    corners = [(RP * math.cos(math.pi / 8 + k * math.pi / 4 - math.pi / 2), RP * math.sin(math.pi / 8 + k * math.pi / 4 - math.pi / 2)) for k in range(8)]
    for (x, y) in corners:
        b.box('paint', x, y, 1.155, .26, .26, .2)
        ngon(b, 'paint', x, y, 1.24, 3.54, .085, 10)
        b.box('paint', x, y, 3.615, .24, .24, .19)
    for k in range(8):
        (ax, ay), (cx, cy) = corners[k - 1], corners[k]                        # side k lies between corners k-1 and k
        mx, my = (ax + cx) / 2, (ay + cy) / 2
        south = my < -3.0 and abs(mx) < .5
        Lk = math.hypot(cx - ax, cy - ay)
        ux, uy = (cx - ax) / Lk, (cy - ay) / Lk
        P = lambda u, z: (ax + ux * u, ay + uy * u, z)
        if not south:
            b.beam('paint', P(.13, 1.96), P(Lk - .13, 1.96), .09 + .004 * (k % 2), .07)
            b.beam('paint', P(.13, 1.18), P(Lk - .13, 1.18), .08, .06)
            n = int((Lk - .3) / .14)
            for i in range(n):
                u = .2 + (Lk - .4) * (i + .5) / n
                b.box('paint', *P(u, 1.565), .05, .05, .74)
        b.beam('paint', P(-.02, 3.83), P(Lk + .02, 3.83), .14 + .006 * (k % 2), .26, ext=.0)
        prev = None
        for i in range(11):                                                    # the arch: low at the posts, touching the frieze at mid-span
            u = .12 + (Lk - .24) * i / 10
            z = 3.22 + .46 * (1 - (2 * u / Lk - 1) ** 2)
            if prev:
                b.beam('paint', P(prev[0], prev[1]), P(u, z), .06 + .004 * (i % 2), .07, ext=.015)
            prev = (u, z)
        for f in (.2, .32, .68, .8):                                           # fretwork spandrel sticks
            u = Lk * f
            z = 3.22 + .46 * (1 - (2 * f - 1) ** 2)
            b.beam('paint', P(u, z + .02), P(u, 3.69), .035, .035)
        b.beam('paint', P(.15, 3.46), P(Lk * .32, 3.46), .035, .035)
        b.beam('paint', P(Lk * .68, 3.46), P(Lk - .15, 3.46), .035, .035)
    b.flush('bandstand')
    # Ogee copper roof: octagonal rings flaring at the eaves, hip rolls on the corners, a finial.
    prof = [(4.35, 3.82), (4.35, 3.96), (3.78, 4.20), (3.10, 4.58), (2.40, 5.10), (1.70, 5.78), (1.05, 6.50), (.50, 7.10), (.16, 7.42)]
    rings = [[(r * math.cos(math.pi / 8 + k * math.pi / 4 - math.pi / 2), r * math.sin(math.pi / 8 + k * math.pi / 4 - math.pi / 2), z) for k in range(8)] for (r, z) in prof]
    loft('Bandstand roof', rings, 'copper', 'bandstand roof', closed=False)
    b = Batch()
    for k in range(8):
        a = math.pi / 8 + k * math.pi / 4 - math.pi / 2
        for (r0, z0), (r1, z1) in zip(prof[1:], prof[2:]):
            b.beam('copper2', (math.cos(a) * (r0 + .02), math.sin(a) * (r0 + .02), z0 + .04), (math.cos(a) * (r1 + .02), math.sin(a) * (r1 + .02), z1 + .04), .11 + .004 * (k % 2), .09, ext=.10)
    ngon(b, 'copper2', 0.0, 0.0, 3.82 - .01, 3.97, 4.42, 8, phase=.5 - .0)                 # eave fascia ring (slightly proud of the roof edge)
    ngon(b, 'copper2', 0.0, 0.0, 7.30, 7.78, .11, 10)
    ngon(b, 'copper2', 0.0, 0.0, 8.0, 8.62, .045, 8, cone=True)
    b.flush('bandstand roof trim')
    balls('Bandstand finial ball', 'copper2', [(0.0, 0.0, 7.92)], .2, 10, 6, 'bandstand roof')


# ---------------------------------------------------------------- gate, fence, piers

def pier(b, x, y, tall):
    """Brick gate pier on a granite base with a stone cap (sunk joints: no shared planes)."""
    if tall:
        b.box('stone', x, y, .35, 1.0, 1.0, .7)
        b.box('stone', x, y, .745, 1.08, 1.08, .11)
        b.box('brick', x, y, 2.275, .84, .84, 2.97)
        b.box('stone', x, y, 2.36, .9, .9, .12)
        b.box('stone', x, y, 3.83, 1.04, 1.04, .16)
        b.box('stone', x, y, 3.955, .92, .92, .11)
    else:
        b.box('stone', x, y, .25, .74, .74, .5)
        b.box('brick', x, y, 1.22, .6, .6, 1.46)
        b.box('stone', x, y, 2.015, .76, .76, .15)
        b.box('stone', x, y, 2.125, .62, .62, .09)
        ngon(b, 'stone', x, y, 2.16, 2.26, .1, 10)


def lantern(b, x, y, z):
    """Iron lantern on a pier cap: base, corner posts, glass, a pyramid roof and finial."""
    b.box('hardware', x, y, z + .06, .5, .5, .12)
    b.box('pale', x, y, z + .52, .38, .38, .82)
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.box('hardware', x + sx * .22, y + sy * .22, z + .52, .05, .05, .84)
    b.box('hardware', x, y, z + .95, .52, .52, .06)
    ngon(b, 'hardware', x, y, z + .96, z + 1.36, .4, 4, phase=.5, cone=True)
    ngon(b, 'hardware', x, y, z + 1.3, z + 1.55, .035, 6)
    for sx in (-1, 1):                                                         # scroll brackets under the base
        b.beam('hardware', (x + sx * .16, y, z + .02), (x + sx * .34, y, z - .25), .04, .04)


def leaf(b, hx, hy, ux, uy, W, h0, h1, spacing=.13, rings=True):
    """An iron gate leaf hinged at (hx, hy), running W along (ux, uy): stiles, rails, pickets and an arched top."""
    P = lambda u, z: (hx + ux * u, hy + uy * u, z)
    top = lambda u: h0 + (h1 - h0) * (u / W) ** 1.4
    for u in (.04, W - .04):
        b.beam('hardware', P(u, .1), P(u, top(u) + .05), .07, .07)
    for z in (.18, .95, 1.25):
        b.beam('hardware', P(.04, z), P(W - .04, z), .05, .05)
    prev = None
    for i in range(9):
        u = .04 + (W - .08) * i / 8
        if prev:
            b.beam('hardware', P(prev, top(prev)), P(u, top(u)), .05, .06, ext=.01)
        prev = u
    n = int(W / spacing)
    for i in range(1, n):
        u = W * i / n
        x, y, _ = P(u, 0)
        spike(b, 'hardware', x, y, .18, top(u) + .08, .024, .11)
    for i in range(int(W / .3) if rings else 0):                               # diamond band between the middle rails
        u = .3 * (i + .5)
        c = P(u, 1.1)
        for k in range(4):
            a0, a1 = 2 * math.pi * k / 4, 2 * math.pi * (k + 1) / 4
            b.beam('hardware', (c[0] + ux * .11 * math.cos(a0), c[1] + uy * .11 * math.cos(a0), 1.1 + .11 * math.sin(a0)),
                   (c[0] + ux * .11 * math.cos(a1), c[1] + uy * .11 * math.cos(a1), 1.1 + .11 * math.sin(a1)), .025, .025, ext=.01)


def fence_run(b, a, c, top_z=.41):
    """Granite curb with a black iron picket fence: rails, spear pickets and finial posts."""
    (ax, ay), (cx, cy) = a, c
    L = math.hypot(cx - ax, cy - ay)
    ux, uy = (cx - ax) / L, (cy - ay) / L
    b.beam('granite', (ax - ux * .16, ay - uy * .16, top_z / 2), (cx + ux * .16, cy + uy * .16, top_z / 2), .32, top_z)
    b.beam('granite', (ax - ux * .19, ay - uy * .19, top_z + .015), (cx + ux * .19, cy + uy * .19, top_z + .015), .38, .05)
    for z in (.55, 1.46):
        b.beam('hardware', (ax, ay, z), (cx, cy, z), .035, .04)
    n = max(2, int(L / .36))
    for i in range(1, n):
        x, y = ax + ux * L * i / n, ay + uy * L * i / n
        spike(b, 'hardware', x, y, top_z + .02, 1.56, .022, .1)
    m = max(1, int(L / 2.6))
    for i in range(m + 1):
        x, y = ax + ux * L * i / m, ay + uy * L * i / m
        b.box('hardware', x, y, (top_z + .02 + 1.72) / 2, .07, .07, 1.72 - top_z - .02)
        ngon(b, 'hardware', x, y, 1.70, 1.84, .07, 4, phase=0.0)
        ngon(b, 'hardware', x, y, 1.82, 1.98, .07, 4, phase=0.0, cone=True)


def sign_arch():
    """The gilded iron sign arch between the tall piers, with the date plaque and crest."""
    zb = lambda x: 4.08 + 1.0 * (1 - (x / 3.9) ** 2)
    xs = [-3.86 + 7.72 * i / 24 for i in range(25)]
    y0 = FS
    band = [[(x, y0 - .04, zb(x)), (x, y0 + .04, zb(x)), (x, y0 + .04, zb(x) + .78), (x, y0 - .04, zb(x) + .78)] for x in xs]
    loft('Gate sign arch', band, 'hardware', 'gates', closed=False)
    for s in (-1, 1):
        for z0 in (.04, .70):
            strip_ = [[(x, y0 + s * .035, zb(x) + z0), (x, y0 + s * .058, zb(x) + z0), (x, y0 + s * .058, zb(x) + z0 + .05), (x, y0 + s * .035, zb(x) + z0 + .05)] for x in xs]
            loft('Gate sign gilt border', strip_, 'gold', 'gates', closed=False)
    b = Batch()
    letters = 'HALIFAX PUBLIC GARDENS'
    span = 6.2
    for s in (-1, 1):
        y = y0 + s * .05
        for i, ch in enumerate(letters):
            if ch == ' ':
                continue
            x = -span / 2 + span * (i + .5) / len(letters)
            z = zb(x) + .22
            b.box('gold', x - .06, y, z + .17, .035, .03, .34)                 # abstract gilt letters: two stems and a bar
            b.box('gold', x + .06, y, z + .17, .035, .03, .34)
            b.box('gold', x, y, z + .17 + (.1 if i % 2 else -.02), .13, .031, .035)
        b.box('gold', 0.0, y0 + s * .038, 4.91, 2.6, .016, .035)                # FOUNDED 1867 plaque: gilt borders and figures
        b.box('gold', 0.0, y0 + s * .038, 4.57, 2.6, .016, .035)
        for i in range(11):
            if i == 7:
                continue
            x = -1.05 + 2.1 * i / 10
            b.box('gold', x, y0 + s * .04, 4.74, .1, .02, .2)
    b.box('hardware', 0.0, y0, 4.74, 2.7, .07, .38)                            # the plaque hangs under the crown of the arch
    for x in (-.6, .6):
        b.box('hardware', x, y0, (4.92 + zb(.6) + .03) / 2, .04, .04, zb(.6) + .03 - 4.92)
    # Crest medallion over the crown of the arch, with scrolls either side.
    zc = zb(0) + .78 + .45
    b.box('hardware', 0.0, y0, zb(0) + .78 + .06, .2, .06, .14)
    V, F = b.g.setdefault('hardware', ([], []))
    o = len(V)
    for yy in (y0 - .05, y0 + .05):
        for k in range(14):
            a = 2 * math.pi * k / 14
            V.append((.36 * math.cos(a), yy, zc + .42 * math.sin(a)))
    F.append(tuple(o + k for k in range(13, -1, -1))); F.append(tuple(o + 14 + k for k in range(14)))
    for k in range(14):
        j = (k + 1) % 14
        F.append((o + k, o + j, o + 14 + j, o + 14 + k))
    for s in (-1, 1):
        b.box('gold', 0.0, y0 + s * .058, zc, .3, .02, .36)
        b.box('gold', 0.0, y0 + s * .062, zc - .2, .16, .02, .1)
    for s in (-1, 1):                                                          # C-scrolls rising from the band to the crest and over the lanterns
        for (cx, cz, r, a0, a1) in ((s * .75, zb(.75) + .78 + .24, .24, 0, 2 * math.pi * .8), (s * 2.3, zb(2.3) + .78 + .2, .2, 0, 2 * math.pi * .8),
                                    (s * 3.3, zb(3.3) + .78 + .18, .18, 0, 2 * math.pi * .8)):
            prev = None
            for i in range(11):
                a = a0 + (a1 - a0) * i / 10 if s > 0 else math.pi - (a0 + (a1 - a0) * i / 10)
                p = (cx + r * math.cos(a), y0, cz + r * math.sin(a))
                if prev:
                    b.beam('hardware', prev, p, .035, .035, ext=.008)
                prev = p
        b.beam('hardware', (s * .3, y0, zb(.3) + .76), (s * .75 + s * .1, y0, zb(.75) + .78 + .45), .04, .04)
    b.flush('gate sign')


def gates_and_fence():
    b = Batch()
    for s in (-1, 1):
        pier(b, s * 4.0, FS, True)
        lantern(b, s * 4.0, FS, 4.0)
        pier(b, s * 8.0, FS, False)
        for y in (-2.85, 2.85):
            pier(b, s * FX, y, False)
        pier(b, s * 2.45, FN, False)
    b.flush('gate piers')
    balls('Pier ball finials', 'stone', [(s * 8.0, FS, 2.46) for s in (-1, 1)] + [(s * FX, y, 2.46) for s in (-1, 1) for y in (-2.85, 2.85)]
          + [(s * 2.45, FN, 2.46) for s in (-1, 1)], .23, 10, 6)
    sign_arch()
    b = Batch()
    c, sn = math.cos(math.radians(75)), math.sin(math.radians(75))
    leaf(b, -3.56, FS, c, sn, 3.5, 2.2, 2.75)                                 # main double gate thrown open into the forecourt
    leaf(b, 3.56, FS, -c, sn, 3.5, 2.2, 2.75)
    for s in (-1, 1):                                                          # side gates where the loop paths enter
        leaf(b, s * 4.44, FS, s * c, sn, 1.6, 1.75, 1.95, .14, False)
        leaf(b, s * 7.68, FS, -s * c, sn, 1.6, 1.75, 1.95, .14, False)
    b.flush('gate leaves')
    b = Batch()
    for s in (-1, 1):
        fence_run(b, (s * 8.32, FS), (s * (FX - .02), FS), .41)
        fence_run(b, (s * FX, FS + .2), (s * FX, -3.17), .40)
        fence_run(b, (s * FX, 3.17), (s * FX, FN - .2), .40)
        fence_run(b, (s * 2.77, FN), (s * (FX - .02), FN), .41)
    for s in (-1, 1):                                                          # corner posts
        for y in (FS, FN):
            b.box('hardware', s * FX, y, 1.1, .14, .14, 1.4)
            ngon(b, 'hardware', s * FX, y, 1.8, 2.05, .09, 8, cone=True)
    b.flush('fence')


# ---------------------------------------------------------------- furniture and context

def bench(b, x, y, fx, fy, z0=.02):
    """Victorian park bench facing (fx, fy): timber slats on cast-iron ends."""
    tx, ty = fy, -fx
    P = lambda u, d, z: (x + tx * u + fx * d, y + ty * u + fy * d, z + z0 - .02)
    for d, z in ((.18, .45), (.04, .45), (-.10, .45)):
        b.beam('bench', P(-.9, d, z), P(.9, d, z), .12, .035)
    for z in (.7, .86):
        b.beam('bench', P(-.9, -.22, z), P(.9, -.22, z), .1, .035)
    for u in (-.82, .82):
        b.beam('hardware', P(u, .2, .05), P(u, .1, .45), .05, .04)
        b.beam('hardware', P(u, -.16, .05), P(u, -.12, .45), .05, .04)
        b.beam('hardware', P(u, -.24, .45), P(u, -.22, .92), .05, .04)
        b.beam('hardware', P(u, .22, .64), P(u, -.2, .64), .05, .04)
        b.beam('hardware', P(u, .19, .47), P(u, .21, .62), .045, .045)        # front arm support down to the seat


def lamp(b, x, y, z0=ZG):
    z0 -= .02
    b.box('hardware', x, y, z0 + .2, .32, .32, .4)
    ngon(b, 'hardware', x, y, z0 + .38, z0 + 3.42, .065, 8)
    b.box('hardware', x, y, z0 + 3.45, .2, .2, .1)
    ngon(b, 'pale', x, y, z0 + 3.48, z0 + 3.95, .17, 8)
    ngon(b, 'hardware', x, y, z0 + 3.93, z0 + 4.25, .24, 8, cone=True)


def furniture():
    b = Batch()
    for s in (-1, 1):                                                          # benches on the outer side of the north arcs
        H = LOOPS[0 if s < 0 else 1]
        for yb in (11.0, 13.8):
            i = min((k for k in range(1, len(H) - 1) if H[k][1] > 1.0), key=lambda k: abs(H[k][1] - yb))
            (ax, ay), (cx, cy) = H[i - 1], H[i + 1]
            L = math.hypot(cx - ax, cy - ay)
            nx, ny = -(cy - ay) / L * -s, (cx - ax) / L * -s                    # outward, away from the inner lawn
            x, y = H[i]
            bench(b, x + nx * (LW + .55), y + ny * (LW + .55), -nx, -ny)
    for s in (-1, 1):                                                          # benches on the circle facing the bandstand
        a = math.radians(-90 + s * 55)
        bench(b, (RC - .55) * math.cos(a), (RC - .55) * math.sin(a), -math.cos(a), -math.sin(a), ZO - .02)
    d = (-math.sin(math.radians(32)), math.cos(math.radians(32)))
    bench(b, 7.6 + 2.3 * d[0], -35.0 + 2.3 * d[1], -d[0], -d[1], .10)         # the front-view bench: back to the camera, facing the garden
    for s in (-1, 1):
        lamp(b, s * 5.2, 6.2); lamp(b, s * 5.2, -6.2)
        lamp(b, s * (FX - 1.2), 3.6)
        lamp(b, s * 16.0, SS + 1.2, .12)                                   # clear of the gate_piers_fence view
    b.flush('furniture')


def context():
    """Street blocks round the garden as simple massing: brick mid-rises west and north, glass offices east and north-east."""
    blocks = [('West block south', -48.0, -36.0, -44.0, -14.0, 18.0, 'facade', 'x+'), ('West block middle', -48.0, -36.0, -13.0, 12.0, 24.0, 'facade', 'x+'),
              ('West block north', -48.0, -36.0, 13.0, 40.0, 16.0, 'facade2', 'x+'), ('East office', 36.0, 50.0, -44.0, -8.0, 26.0, 'facade3', 'x-'),
              ('East block north', 36.0, 50.0, -7.0, 40.0, 17.0, 'facade', 'x-'), ('North apartments', -26.0, -2.0, 42.4, 56.0, 32.0, 'facade', 'y-'),
              ('North office', 2.0, 26.0, 42.4, 56.0, 27.0, 'facade3', 'y-'), ('South row west', -40.0, -5.0, -64.0, -48.4, 15.0, 'facade2', 'y+'),
              ('South row east', 5.0, 40.0, -64.0, -48.4, 19.0, 'facade', 'y+')]
    b = Batch()
    for name, x0, x1, y0, y1, h, role, face in blocks:
        C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), role, 'context', 0)
        b.box('troof', (x0 + x1) / 2, (y0 + y1) / 2, h + .29, x1 - x0 + .3, y1 - y0 + .3, .6)
        glass = role == 'facade3'
        floors = int((h - 1.0) / 3.3)
        for f in range(floors):
            z = 1.0 + f * 3.3 + 1.6
            hh = 2.6 if glass else 1.6
            if face in ('x+', 'x-'):
                xf = x1 + .02 if face == 'x+' else x0 - .02
                b.box('dark', xf, (y0 + y1) / 2, z, .06, y1 - y0 - 1.2, hh)
            else:
                b.box('dark', (x0 + x1) / 2, y0 - .02 if face == 'y-' else y1 + .02, z, x1 - x0 - 1.2, .06, hh)
        if not glass:                                                          # brick piers between the window bays, full height
            span = (y1 - y0) if face in ('x+', 'x-') else (x1 - x0)
            for k in range(int((span - 1.2) / 3.0) + 1):
                if face in ('x+', 'x-'):
                    xf = x1 + .06 if face == 'x+' else x0 - .06
                    b.box(role, xf, y0 + .6 + k * 3.0, (h - .4) / 2 + .2, .06, .5, h - .6)
                else:
                    b.box(role, x0 + .6 + k * 3.0, y0 - .06 if face == 'y-' else y1 + .06, (h - .4) / 2 + .2, .5, .06, h - .6)
        if glass:
            n = int(((y1 - y0) if face != 'y-' else (x1 - x0)) / 1.5)
            for k in range(n + 1):
                if face == 'x-':
                    b.box('trim', x0 - .07, y0 + .3 + k * (y1 - y0 - .6) / n, h / 2, .06, .12, h - .4)
                else:
                    b.box('trim', x0 + .3 + k * (x1 - x0 - .6) / n, y0 - .07, h / 2, .12, .06, h - .4)
    b.flush('context')
    C.box('South far sidewalk', (0.0, SS - ST - 2.1, .064), (2 * (SW + ST + 2.38), 4.2 - .04, .12), 'concrete', 'sidewalks', 0)
    for s in (-1, 1):                                                          # street trees on the far sidewalks
        for y in (-30.0, 24.0):
            shade_tree('Street tree', s * (SW + ST + 1.2), y, 8.0, 1.6)


def build():
    ground()
    paths()
    planting()
    bandstand()
    gates_and_fence()
    furniture()
    context()
    C.CONTACTS.append(dict(name='Fenced Victorian garden with bandstand, paths, beds and gate on grade-zero streets', box=[-FX, FX, FS, FN]))


LIGHT_RIG = dict(key=(35, -45, 45), fill=(-40, -25, 30), rear=(-20, 40, 30), target=(0, 0, 2.0), gain=3.4)
