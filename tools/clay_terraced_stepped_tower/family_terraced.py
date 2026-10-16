"""Terraced stepped residential tower, authored from the locked catalogue views of
terraced_stepped_building / variant_0 (terraced_ridgeline).

Read from the pixels (the top view governs the plan): a fifteen-storey block of dark charcoal brick
across the north of a corner site, with narrow punched windows, a flat roof carrying rows of solar
panels and two skylight boxes; against its south face an east wing that steps down toward the south
in seven two-storey terraces. Each step face is floor-to-ceiling glazing between cedar panels with
white slab edges and a slim balcony rail at its upper floor; each terrace is a timber deck behind a
black steel railing with corten planters of grasses and small trees and garden furniture. A solid
charcoal raking wall with a light coping closes the wing's east side; the court-facing west side carries a
projecting glazed balcony on every floor; the ground storey is set back behind white round columns. West of the wing, at the foot
of the dark block, a paved garden court planted with a grove of birches.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-terraced-stepped-tower'
NB = (-15.0, 21.0, 10.0, 24.0)          # dark north block (top view at 0.075 m/px)
WX0, WX1 = -2.0, 21.0                   # stepped wing
WY0, WY1 = -18.0, 10.0
STEPS = 7
STEP_D = (WY1 - WY0) / STEPS            # 4 m per step
T = .32
G0 = .15
GF = 4.0
FH = 3.1
NF = 15                                 # storeys in the north block
Z = [G0] + [G0 + GF + (i - 1) * FH for i in range(1, NF + 1)]   # floor levels; Z[NF] is the roof
ROOF = Z[NF]
EPS = .002
PALETTE = dict(wall=(.20, .19, .19), joint=(.13, .12, .12), trim=(.12, .12, .13),
    pale=(.86, .85, .82), stone=(.74, .72, .68), roof=(.62, .60, .56), sand=(.72, .68, .60),
    foundation=(.42, .42, .41), glass=(.40, .48, .52), hardware=(.10, .10, .11),
    interior=(.80, .76, .68), floor=(.48, .46, .44), timber=(.66, .48, .30), blue=(.12, .18, .30),
    planting=(.40, .46, .18), soil=(.22, .16, .10), concrete=(.74, .73, .70), white=(.92, .92, .90),
    corten=(.52, .30, .16), deck=(.70, .56, .40), gravel=(.64, .62, .58), solar=(.12, .16, .26),
    birch=(.88, .86, .82), asphalt=(.30, .30, .31), grass=(.66, .55, .26))


def manifest(version):
    h = ROOF + 2.0
    cams = G.camera_roster(NB[1] - NB[0] + 4.0, NB[3] - WY0 + 4.0, h, [
        ('facade_close', (10.0, -34.0, 14.0), (9.5, WY0 + 2 * STEP_D, 14.0), 45),
        ('architecture_close', (34.0, -20.0, 26.0), (WX1, 0.0, 24.0), 45),
        ('glass_close', (9.0, -26.0, 6.0), (9.5, WY0, 5.0), 45),
        ('terrace_planters', (10.0, -30.0, 30.0), (9.5, WY0 + 3 * STEP_D, Z[8]), 45),
        ('raking_frame', (36.0, -34.0, 12.0), (WX1, -6.0, 18.0), 45),
        ('birch_court', (-22.0, -26.0, 10.0), (-8.0, -4.0, 3.0), 45),
        ('solar_roof', (-26.0, 34.0, 62.0), (3.0, 17.0, ROOF), 45),
        ('dark_block', (-32.0, 6.0, 26.0), (NB[0], 17.0, 26.0), 45),
        ('interior', (12.0, WY0 + 3 * STEP_D + 2.5, Z[6] + 1.6), (6.0, WY0 + 3 * STEP_D - 2.0, Z[6] + 1.2), 60),
        ('rear_north', (2.0, 46.0, 16.0), (2.0, NB[3], 18.0), 45)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='terraced_stepped_building/variant_0 (terraced_ridgeline)',
        measurement_contract=dict(dimensions_m=dict(width=NB[1] - NB[0], depth=NB[3] - WY0, height=h),
            observed_storeys=NF, storey_programme='fifteen storeys in the dark north block; the wing steps from fourteen storeys at the block down to two at the street in seven two-storey terraces',
            plan='north block 36 x 14 m; stepped wing 23 m wide running 28 m south from it in seven 4 m steps; birch court 13 x 28 m west of the wing (top view at 0.075 m/px)',
            facade='north block: dark charcoal brick with narrow punched windows in a staggered rhythm; wing: floor-to-ceiling glazing between cedar panels, white slab edges, slim balcony rail on each upper floor, raking concrete frame along the step edges',
            levels_m=Z,
            inferred='storey heights and interiors are teaching assumptions; the north face is not visible in any source and repeats the visible grammar'),
        roof_contract=dict(type='flat gravel roof with solar arrays on the block; seven timber-decked terraces on the wing', datum_m=ROOF, crowns_m=[ROOF + 1.0, ROOF + 1.6]),
        identity_contract=dict(owner='dark brick slab with solar roof and a stepped terraced wing of timber decks, corten planters and black railings, raking concrete frame, birch court'),
        material_contract=dict(profile='source-palette clay: charcoal brick, cedar, white slab edges, clear glass, black steel, corten planters, timber decks, birch grove', textured_keeper=False),
        programme_contract=dict(storeys=NF, ground='lobby and shared rooms opening to the birch court', wing='flats with private terraces, each step a two-storey duplex band', block='flats off a central corridor'),
        contact_contract=['Grade-zero slab, court paving and sidewalks', 'Each terrace on the roof slab of the step below', 'Raking frame on the step edges', 'Solar arrays on the block roof', 'Railings on the terrace edges'],
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


# ---- terraced stepped tower ----

YS = [WY0 + j * STEP_D for j in range(STEPS + 1)]       # south edge of step j; YS[STEPS] == WY1
SET = 1.5                                                # ground storey set back behind the colonnade


class Batch:
    def __init__(self):
        self.g = {}

    def box(self, role, cx, cy, cz, sx, sy, sz):
        V, F = self.g.setdefault(role, ([], []))
        o = len(V)
        V.extend((cx + du * sx / 2, cy + dd * sy / 2, cz + dz * sz / 2) for dz in (-1, 1) for du, dd in ((-1, -1), (1, -1), (1, 1), (-1, 1)))
        F.extend(tuple(o + i for i in face) for face in C.BOX_FACES)

    def flush(self, module):
        for role, (V, F) in self.g.items():
            if F:
                C.mesh(f'{module} {role}', V, F, role, module)
        self.g = {}


def glazed_band(f, lo, hi, z0, floors, tag, balcony=True):
    """Step face: floor-to-ceiling glazing between cedar panels, white slab edges, slim balcony on the upper floor."""
    span = hi - lo
    n = max(1, round(span / 3.8))
    pitch = span / n
    holes = []
    for k, (za, zb) in enumerate(floors):
        for i in range(n):
            holes.append(hole(f'{tag} f{k} glazing {i}', lo + pitch * (i + .5), za + .12, pitch - 1.1, zb - za - .55, kind='window'))
    f.wall(f'{tag} cedar carrier', lo, hi - EPS, z0, floors[-1][1], depth=T, role='timber', holes=holes)
    m = Merge(f)
    for h in holes:
        framed(m, f, h, cols=2, rows=1, inset=.12, occupied='flat', kind='french window', frame='trim')
    for k, (za, zb) in enumerate(floors):
        m.box('white', (lo + hi) / 2, -.08, za + .02, span - 2 * EPS, T + .16, .3)              # white slab edge
        if balcony and k == len(floors) - 1:
            m.box('white', (lo + hi) / 2, -.55, za - .02, span - .4, 1.1, .2)
            m.box('hardware', (lo + hi) / 2, -1.06, za + 1.0, span - .44, .05, .05)
            m.box('hardware', (lo + hi) / 2, -1.06, za + .45, span - .44, .03, .03)
            for i in range(int(span / 1.2) + 1):
                m.box('hardware', lo + .22 + (span - .44) * i / int(span / 1.2), -1.06, za + .52, .05, .05, .96)
    m.box('white', (lo + hi) / 2, -.1, floors[-1][1] - .2, span - 2 * EPS, T + .2, .4)          # step roof edge
    m.flush(tag)


def punched_face(f, lo, hi, z0, z1, levels, tag, lite=False):
    """Dark brick with narrow punched windows in a staggered rhythm."""
    span = hi - lo
    holes = []
    for k, z in enumerate(levels):
        off = .9 if k % 2 else 0.0
        u = lo + 1.2 + off
        i = 0
        while u < hi - 1.0:
            holes.append(hole(f'{tag} f{k} window {i}', u, z + .6, .9, 2.0))
            u += 2.6; i += 1
    f.wall(f'{tag} dark brick carrier', lo, hi - EPS, z0, z1, depth=T, holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, z0 + .05, z1 - .4, holes, spacing=.24 if not lite else .4)
    m = Merge(f)
    for h in holes:
        framed(m, f, h, cols=1, rows=1, inset=.2, occupied='flat', lite=lite)
    m.box('concrete', (lo + hi) / 2, -.06, z1 + .05, span - 2 * EPS, T + .14, .12)              # coping
    m.flush(tag)


def wing():
    hw = (WX1 - WX0) / 2
    cx = (WX0 + WX1) / 2
    for j in range(STEPS):
        f = C.Face((cx, YS[j], 0), (1, 0, 0), (0, 1, 0), f'step {j} south')
        floors = [(Z[2 * j], Z[2 * j + 1]), (Z[2 * j + 1], Z[2 * j + 2])] if j else [(Z[1], Z[2])]
        glazed_band(f, -hw + T, hw - T, floors[0][0], floors, f.label)
    # West (court) elevation in strips that follow the steps: full-height glazing between cedar panels, a projecting
    # balcony with white slab edge and black rail on every floor; the ground storey is set back behind columns.
    for k in range(STEPS):
        ya, yb = YS[k], YS[k + 1]
        L = yb - ya
        f = C.Face((WX0, (ya + yb) / 2, 0), (0, -1, 0), (1, 0, 0), f'wing west strip {k}')
        top = Z[2 * k + 2]
        levels = Z[1:2 * k + 2]
        holes = [hole(f'{f.label} f{i} glazing', 0, z + .12, L - 1.3, (Z[i + 2] - z) - .5, kind='window') for i, z in enumerate(levels)]
        f.wall(f.label + ' cedar carrier', -L / 2, L / 2 - EPS, Z[1], top, depth=T, role='timber', holes=holes)
        m = Merge(f)
        for h in holes:
            framed(m, f, h, cols=2, inset=.12, occupied='flat', kind='french window', frame='trim', lite=True)
        for z in levels:
            m.box('white', 0, -.65, z - .1, L - .12, 1.3, .2)                       # balcony slab and white edge
            m.box('hardware', 0, -1.28, z + 1.0, L - .14, .05, .05)                 # top rail
            m.box('hardware', 0, -1.28, z + .06, L - .14, .04, .04)                 # bottom rail
            for q in range(5):
                m.box('hardware', -L / 2 + .1 + (L - .2) * q / 4, -1.28, z + .53, .05, .05, .94)
            m.box('glass', 0, -1.27, z + .53, L - .2, .02, .9)
        m.box('white', 0, -.1, top - .2, L - 2 * EPS, T + .2, .4)
        m.flush(f.label)
    # Recessed glazed ground storey on the south and west fronts behind white round columns.
    gs = C.Face(((WX0 + SET + WX1 - T) / 2, WY0 + SET, 0), (1, 0, 0), (0, 1, 0), 'wing ground south')
    hs = (WX1 - T - WX0 - SET) / 2
    glazed_band(gs, -hs, hs, Z[0], [(Z[0], Z[1])], gs.label, balcony=False)
    gw = C.Face((WX0 + SET, (WY0 + SET + WY1) / 2, 0), (0, -1, 0), (1, 0, 0), 'wing ground west')
    hd = (WY1 - WY0 - SET) / 2
    glazed_band(gw, -hd + T, hd, Z[0], [(Z[0], Z[1])], gw.label, balcony=False)
    for x in [WX0 + .25 + (WX1 - T - WX0 - .5) * q / 6 for q in range(7)]:
        C.rod('Colonnade column', (x, WY0 + .2, G0), (x, WY0 + .2, Z[1]), .22, 'white', 'colonnade', 16)
    for y in [WY0 + .25 + (WY1 - WY0 - .5) * q / 7 for q in range(1, 8)]:
        C.rod('Colonnade column', (WX0 + .2, y, G0), (WX0 + .2, y, Z[1]), .22, 'white', 'colonnade', 16)
    C.box('Colonnade soffit', (cx, WY0 + SET / 2 + .16, Z[1] - .2), (WX1 - WX0 - 2 * T, SET - .32, .2), 'white', 'colonnade', 0)
    C.box('Colonnade soffit', (WX0 + SET / 2 + .16, (WY0 + SET + WY1) / 2, Z[1] - .2), (SET - .32, WY1 - WY0 - SET, .2), 'white', 'colonnade', 0)
    # Floor slabs: each covers its step and the terrace in front of it.
    for i in range(1, 2 * STEPS + 1):
        j = i // 2
        y0 = YS[j - 1] if (i % 2 == 0 and j >= 1) else YS[min(j, STEPS - 1)]
        C.box(f'Wing slab {i}', (cx, (y0 + T + WY1) / 2, Z[i] - .15), (WX1 - WX0 - 2 * T, WY1 - y0 - T, .3), 'floor', 'wing slabs', 0)
    C.box('Wing ground slab', (cx, (WY0 + WY1) / 2, G0 / 2), (WX1 - WX0, WY1 - WY0, G0), 'foundation', 'wing slabs', 0)
    # Terraces: timber decks, black steel railings, corten planters with grasses and small trees, furniture.
    for j in range(STEPS):
        ya, yb, zt = YS[j], YS[j + 1], Z[2 * j + 2]
        C.box(f'Terrace deck {j}', (cx, (ya + T + yb) / 2, zt + .05), (WX1 - WX0 - 2 * T - .02, yb - ya - T - .02, .1), 'deck', 'terraces', 0)
        ry = ya + .2
        xe = WX1 - T - .1                                                    # east end against the raking wall
        C.beam('Terrace rail', (WX0 + .2, ry, zt + 1.1), (xe, ry, zt + 1.1), .05, .05, 'hardware', 'terraces')
        C.beam('Terrace rail mid', (WX0 + .2, ry, zt + .55), (xe, ry, zt + .55), .03, .03, 'hardware', 'terraces')
        C.beam('Terrace side rail', (WX0 + .2, ry, zt + 1.1), (WX0 + .2, yb, zt + 1.1), .05, .05, 'hardware', 'terraces')
        gb = Batch()
        for i in range(17):
            x = WX0 + .2 + (xe - WX0 - .2) * i / 16
            gb.box('hardware', x, ry, zt + .6, .04, .04, 1.0)
        # Long corten planter along the front: tall golden grasses, multi-stem small trees.
        pa, pb, py = WX0 + .7, xe - .6, ya + .85
        gb.box('corten', (pa + pb) / 2, py, zt + .45, pb - pa, .9, .7)
        gb.box('soil', (pa + pb) / 2, py, zt + .81, pb - pa - .1, .8, .02)
        q = 0
        x = pa + .25
        while x < pb - .2:
            hgt = .7 + .25 * ((q * 7) % 3)
            gb.box('grass', x, py + (.18 if q % 2 else -.18), zt + .82 + hgt / 2, .42, .1, hgt)
            gb.box('grass', x + .12, py, zt + .82 + hgt * .4, .1, .5, hgt * .8)
            x += .45; q += 1
        gb.flush(f'terrace {j} planting')
        for tx in (pa + 2.2 + (j % 2) * 3.0, pb - 2.5 - (j % 3) * 2.0):
            for dx, dy in ((0, 0), (.35, .2), (-.3, .15)):
                A.small_tree(tx + dx, py + dy, zt + .82, 2.4 + .4 * ((j + int(dx * 10)) % 2), .9)
        # Furniture: a sofa and lounger at one end, a dining set at the other.
        A.sofa(WX0 + 3.0, ya + 2.9, zt + .1)
        C.box('Lounger', (WX0 + 6.4, ya + 2.7, zt + .4), (.7, 1.9, .14), 'white', 'terraces', 0)
        C.box('Lounger back', (WX0 + 6.4, ya + 3.55, zt + .62), (.7, .2, .5), 'white', 'terraces', 0)
        dx0 = xe - 4.0
        C.box('Terrace table', (dx0, ya + 2.8, zt + .8), (1.8, .9, .05), 'timber', 'terraces', 0)
        C.box('Terrace table base', (dx0, ya + 2.8, zt + .45), (.1, .1, .7), 'hardware', 'terraces', 0)
        for ddx in (-1.2, 1.2):
            A.garden_chair(dx0 + ddx, ya + 2.8, zt + .1)
        A.garden_chair(dx0 - .4, ya + 2.1, zt + .1); A.garden_chair(dx0 + .4, ya + 3.5, zt + .1)
    # Solid charcoal raking wall closing the wing's east side; its top follows the step line, under a light coping.
    zr = lambda y: Z[2] + 1.25 + (y - WY0) * (Z[2 * STEPS] - Z[2]) / (YS[STEPS - 1] - WY0)
    xa, xb = WX1 - T, WX1 + .35
    ztop = ROOF + .9                                                     # meets the block's parapet line
    yh = WY0 + (ztop - zr(WY0)) * (YS[STEPS - 1] - WY0) / (Z[2 * STEPS] - Z[2])
    C.prism('Raking wall', [(WY0, G0), (WY1, G0), (WY1, ztop), (yh, ztop), (WY0, zr(WY0))], 'x', xa, xb, 'wall', 'raking wall')
    C.prism('Raking wall coping', [(WY0 - .05, zr(WY0) - .01), (yh, ztop - .01), (WY1, ztop - .01), (WY1, ztop + .16), (yh, ztop + .16), (WY0 - .05, zr(WY0) + .16)], 'x', xa - .05, xb + .05, 'concrete', 'raking wall')
    C.CONTACTS.append(dict(name='Raking wall from grade to the step line on the wing east side; terraces end against it', top=[zr(WY0), ztop]))
    for j in range(STEPS):
        C.qa_room_light(f'Step {j} flats', (cx, YS[j] + 2.5, Z[2 * j + 1] - .5), 60, 5.0)
        C.qa_room_light(f'Step {j} upper', (cx, YS[j] + 2.5, Z[2 * j + 2] - .5), 60, 5.0)
    zf = Z[6]
    A.sofa(cx - 3.0, YS[3] + 2.4, zf); A.desk(cx + 4.0, YS[3] + 2.2, zf)


def north_block():
    x0, x1, y0, y1 = NB
    top = ROOF + .9
    s_a = C.Face(((x0 + WX0) / 2, y0, 0), (1, 0, 0), (0, 1, 0), 'block south west')
    punched_face(s_a, -(WX0 - x0) / 2, (WX0 - x0) / 2, G0, top, Z[:NF], s_a.label)
    s_b = C.Face(((WX0 + x1 - T) / 2, y0, 0), (1, 0, 0), (0, 1, 0), 'block south above wing')
    hb = (x1 - T - WX0) / 2
    hb_holes = [hole(f'top terrace door {i}', -hb + 3.2 * (i + .5), Z[14] + .12, 2.2, FH - .55, kind='door') for i in range(int(2 * hb / 3.2))]
    s_b.wall('block south above wing carrier', -hb, hb - EPS, Z[14], top, depth=T, holes=hb_holes)
    G.brick_courses(s_b, -hb + .02, hb - .02, Z[14] + .05, top - .4, hb_holes, spacing=.24)
    m = Merge(s_b)
    for h in hb_holes:
        framed(m, s_b, h, cols=2, inset=.14, occupied='penthouse flat', kind='glazed door')
    m.box('concrete', 0, -.06, top + .05, 2 * hb - 2 * EPS, T + .14, .12)
    m.flush('block south above wing')
    e = C.Face((x1, (y0 + y1) / 2, 0), (0, 1, 0), (-1, 0, 0), 'block east')
    punched_face(e, -(y1 - y0) / 2, (y1 - y0) / 2, G0, top, Z[:NF], e.label, lite=True)
    n = C.Face(((x0 + x1) / 2, y1, 0), (-1, 0, 0), (0, -1, 0), 'block north')
    punched_face(n, -(x1 - x0) / 2 + T, (x1 - x0) / 2, G0, top, Z[:NF], n.label, lite=True)
    w = C.Face((x0, (y0 + y1) / 2, 0), (0, -1, 0), (1, 0, 0), 'block west')
    punched_face(w, -(y1 - y0) / 2 + T, (y1 - y0) / 2 - T, G0, top, Z[:NF], w.label)
    for i in range(1, NF + 1):
        C.box(f'Block slab {i}', ((x0 + x1) / 2, (y0 + y1) / 2, Z[i] - .15), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .3), 'floor', 'block slabs', 0)
        if i % 2:
            C.qa_room_light(f'Block flats {i}', ((x0 + x1) / 2, y1 - 3.0, Z[i] - .5), 50, 6.0)
    C.box('Block ground slab', ((x0 + x1) / 2, (y0 + y1) / 2, G0 / 2), (x1 - x0, y1 - y0, G0), 'foundation', 'block slabs', 0)
    C.box('Block roof gravel', ((x0 + x1) / 2, (y0 + y1) / 2, ROOF + .02), (x1 - x0 - 2 * T - .02, y1 - y0 - 2 * T - .02, .04), 'gravel', 'roof', 0)
    # Solar arrays: tilted panel rows on low frames, two skylight boxes, a hatch.
    for (xa, xb, yc) in ((-11.0, 18.0, 16.6), (-11.0, -4.0, 21.0), (11.0, 18.0, 21.0)):
        poly = [(yc - 1.0, ROOF + .35), (yc + 1.0, ROOF + .85), (yc + 1.0, ROOF + .80), (yc - 1.0, ROOF + .30)]
        C.prism('Solar array', poly, 'x', xa, xb, 'solar', 'solar roof')
        k = xa + 1.0
        while k < xb:
            C.box('Solar frame leg', (k, yc + .8, ROOF + .45), (.08, .08, .82), 'hardware', 'solar roof', 0)
            k += 2.0
        for gx in [xa + 2.0 * q for q in range(1, int((xb - xa) / 2.0))]:
            C.box('Solar panel joint', (gx, yc, ROOF + .6), (.04, 2.0, .58), 'pale', 'solar roof', 0)
    C.box('Roof skylight', (-.5, 21.0, ROOF + .4), (2.2, 1.6, .8), 'glass', 'roof', 0)
    C.box('Roof hatch', (7.0, 21.0, ROOF + .35), (2.4, 1.6, .7), 'pale', 'roof', 0)


def court():
    x0, x1 = NB[0], WX0
    C.box('Court paving', ((x0 + x1) / 2, (WY0 + WY1) / 2, .06), (x1 - x0 - .02, WY1 - WY0, .12), 'sand', 'court', 0)
    bx0, bx1, by0, by1 = -12.8, -4.2, -4.0, 5.0
    C.box('Birch planter', ((bx0 + bx1) / 2, (by0 + by1) / 2, .5), (bx1 - bx0, by1 - by0, .76), 'corten', 'court', 0)
    C.box('Birch planter soil', ((bx0 + bx1) / 2, (by0 + by1) / 2, .89), (bx1 - bx0 - .2, by1 - by0 - .2, .02), 'soil', 'court', 0)
    k = 0
    for i in range(4):
        for jj in range(4):
            x = -11.6 + i * 2.1 + (.5 if jj % 2 else 0)
            y = -3.0 + jj * 2.3
            h = 6.0 + (k % 3) * .9
            C.rod('Birch trunk', (x, y, .88), (x, y, .88 + h * .7), .1, 'birch', 'court', 8)
            A.foliage('Birch crown', (x, y, .88 + h * .82), (1.0, 1.0, 1.4), detail=1)
            k += 1
    for i in range(7):                                                   # dense underplanting
        for jj in range(4):
            A.shrub(bx0 + .7 + i * 1.2, by0 + .8 + jj * 2.4 + (.6 if i % 2 else 0), .9, .6 + .2 * ((i + jj) % 3))
    for (a_, b_, c_, d_) in ((-13.6, -9.4, -14.5, -8.0), (-7.2, -3.4, -14.5, -8.0)):
        C.box('Court raised bed', ((a_ + b_) / 2, (c_ + d_) / 2, .38), (b_ - a_, d_ - c_, .52), 'corten', 'court', 0)
        C.box('Court raised bed soil', ((a_ + b_) / 2, (c_ + d_) / 2, .65), (b_ - a_ - .2, d_ - c_ - .2, .02), 'soil', 'court', 0)
        for i in range(3):
            for jj in range(4):
                A.shrub(a_ + .7 + i * 1.4, c_ + .8 + jj * 1.6, .66, .7 + .25 * ((i + jj) % 3))
    C.box('Court path', (-8.3, -11.25, .125), (2.2, 6.5, .01), 'stone', 'court', 0)
    for y in (-6.0, 6.5):
        C.box('Court bench', (-3.6, y, .45), (.5, 1.8, .08), 'timber', 'court', 0)
        for e in (-1, 1):
            C.box('Court bench leg', (-3.6, y + e * .8, .27), (.45, .08, .3), 'hardware', 'court', 0)


def site():
    C.box('South sidewalk', (3.0, WY0 - 3.0, .07), (46.0, 6.0, .14), 'concrete', 'site', 0)
    C.box('East sidewalk', (WX1 + 2.8, (WY0 + NB[3]) / 2, .07), (5.6, NB[3] - WY0, .14), 'concrete', 'site', 0)
    C.box('West sidewalk', (NB[0] - 2.5, (WY0 + NB[3]) / 2, .07), (5.0, NB[3] - WY0, .14), 'concrete', 'site', 0)
    C.box('South street', (3.0, WY0 - 11.0, .01), (56.0, 10.0, .02), 'asphalt', 'site', 0)
    C.box('East street', (WX1 + 10.6, (WY0 + NB[3]) / 2, .01), (10.0, NB[3] - WY0, .02), 'asphalt', 'site', 0)
    for x in (-10.0, 6.0, 16.0):
        street_tree(x, WY0 - 3.6, z=.14, height=7.0, spread=1.6)


def build():
    site()
    court()
    wing()
    north_block()
    C.CONTACTS.append(dict(name='Stepped wing against the dark block; each terrace on the roof slab of the step below; raking frame on the step corners', steps=YS))


LIGHT_RIG = dict(key=(-60, -70, 80), fill=(70, -30, 60), rear=(-20, 70, 70), target=(0, 0, 20.0), gain=18.0)
