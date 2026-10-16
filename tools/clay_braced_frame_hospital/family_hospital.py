"""Regional hospital with a braced-frame tower and a glazed atrium, authored from the locked catalogue
views of regional_hospital_medical_center / variant_0 (regional_hospital_contemporary_teaching).

Read from the pixels (the top view governs the plan): three volumes on a corner block with streets
south, west and east. A seven-storey clinical block at the south-west: a two-storey red-brick base with
large windows, five storeys clad in pale panels with perforated screens over the glazing, a tall dark
signage panel near its east end, a recessed plant storey behind a dark louvre band and a raised
canopy frame over its western roof. A taller L-shaped ward block wraps the north and east, glazed
behind a standing steel exoskeleton of columns, ring beams and full-height X-braces, on a brick base at
the east street. Between them a full-height glass atrium with a diagonal mullion net opens south over a
large glass entrance canopy hung on tension rods.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-braced-frame-hospital'
T = .32
G0 = .15
PB = (-38.0, 13.0, -27.0, 8.0)          # perforated clinical block (top view at 0.097 m/px)
LEG = (21.0, 31.0, -27.0, 26.0)         # braced block, east leg
BAR = (-29.0, 21.0, 8.0, 26.0)          # braced block, north bar
ATR = (13.0, 21.0, -30.0, 8.0)          # glass atrium, standing 3 m proud of the street faces
BASE = [G0, 5.0]                        # brick base storeys
BASE_TOP = 9.0
FH = 4.0
PB_TOP = BASE_TOP + 5 * FH              # 29.0
PLANT_TOP = PB_TOP + 4.0
BB_TOP = BASE_TOP + 7 * FH              # 37.0
ATR_TOP = 33.0
EXO = 1.1                               # exoskeleton stand-off
EPS = .002
PALETTE = dict(wall=(.55, .28, .21), joint=(.40, .20, .15), trim=(.30, .32, .34),
    pale=(.84, .83, .80), stone=(.70, .68, .64), roof=(.70, .69, .66), sand=(.68, .66, .62),
    foundation=(.42, .42, .41), glass=(.50, .60, .64), hardware=(.22, .23, .25),
    interior=(.82, .80, .76), floor=(.50, .48, .46), timber=(.40, .28, .16), blue=(.16, .30, .38),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.72, .71, .68), steel=(.62, .64, .66),
    perf=(.42, .42, .42), sign=(.16, .18, .20), signlight=(.50, .72, .78), louvre=(.24, .25, .27),
    asphalt=(.30, .30, .31), white=(.90, .90, .88), membrane=(.72, .71, .68))


def manifest(version):
    h = BB_TOP + 3.0
    cams = G.camera_roster(70.0, 54.0, h, [
        ('facade_close', (-14.0, -46.0, 18.0), (-14.0, PB[2], 18.0), 45),
        ('architecture_close', (30.0, -50.0, 20.0), (17.0, -23.0, 18.0), 45),
        ('glass_close', (17.0, -38.0, 10.0), (17.0, ATR[2], 14.0), 45),
        ('braced_frame', (52.0, -20.0, 24.0), (LEG[1], -4.0, 22.0), 45),
        ('entrance_canopy', (6.0, -42.0, 3.0), (17.0, -28.0, 4.6), 45),
        ('roof_canopy', (-46.0, -46.0, 44.0), (-20.0, -10.0, 33.0), 45),
        ('roof_plant', (40.0, 40.0, 50.0), (6.0, 16.0, BB_TOP), 45),
        ('brick_base', (-28.0, -40.0, 3.0), (-24.0, PB[2], 4.0), 45),
        ('interior', (15.0, -21.0, 1.8), (19.0, 2.0, 10.0), 60),
        ('rear_north', (-6.0, 60.0, 14.0), (-6.0, BAR[3], 16.0), 45)])
    for c in cams:                       # the locked front and oblique look from the south-east
        if c['name'] == 'front_corner':
            lx, ly, lz = c['location']; c['location'] = (-lx, ly, lz)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='regional_hospital_medical_center/variant_0 (regional_hospital_contemporary_teaching)',
        measurement_contract=dict(dimensions_m=dict(width=69.0, depth=53.0 + 6.0, height=h),
            observed_storeys=9, storey_programme='two-storey brick base (outpatients, emergency), five clinical storeys, plant storey; ward block of nine storeys',
            plan='clinical block 51 x 35 m at the south-west; L-shaped ward block (north bar 50 x 18 m, east leg 10 x 53 m); atrium 8 x 31 m between them opening south (top view at 0.097 m/px)',
            facade='clinical block: brick base with large windows, pale panels with perforated screens over strip glazing, dark vertical signage panel, dark louvre band at the plant storey; ward block: glazing behind a steel exoskeleton of 5 m bays, ring beams every two storeys and X-braces; atrium: glass with a diagonal mullion net',
            levels_m=BASE + [BASE_TOP + FH * i for i in range(7)] + [BB_TOP], roofs_m=[PB_TOP, PLANT_TOP, ATR_TOP, BB_TOP],
            inferred='storey heights and interiors are teaching assumptions; the north and west faces of the ward block are not visible in the front or oblique and repeat the visible grammar'),
        roof_contract=dict(type='flat membranes; raised canopy frame over the clinical roof; glazed atrium roof; rooftop plant', datum_m=PB_TOP, crowns_m=[PLANT_TOP + 2.6, BB_TOP]),
        identity_contract=dict(owner='braced steel exoskeleton over the glazed ward block, perforated pale screens over a brick base, glass atrium with the cable-hung entrance canopy, signage panel, raised roof canopy'),
        material_contract=dict(profile='source-palette clay: pale perforated panels, red brick base, grey steel exoskeleton, clear glass, dark louvres and signage', textured_keeper=False),
        programme_contract=dict(storeys=9, base='main entrance, outpatients and emergency', clinical='diagnostics, theatres and clinics', ward='inpatient wards', atrium='main hall with lifts and bridges'),
        contact_contract=['Grade-zero slabs and sidewalks', 'Exoskeleton columns from the brick base to the roof ring', 'Atrium between the clinical and ward blocks', 'Entrance canopy on rods and two posts', 'Roof canopy on posts over the plant storey'],
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


# ---- braced-frame hospital ----

class Batch:
    def __init__(self):
        self.g = {}

    def box(self, role, cx, cy, cz, sx, sy, sz):
        V, F = self.g.setdefault(role, ([], []))
        o = len(V)
        V.extend((cx + du * sx / 2, cy + dd * sy / 2, cz + dz * sz / 2) for dz in (-1, 1) for du, dd in ((-1, -1), (1, -1), (1, 1), (-1, 1)))
        F.extend(tuple(o + i for i in face) for face in C.BOX_FACES)

    def quad(self, role, pts):
        V, F = self.g.setdefault(role, ([], []))
        o = len(V); V.extend(pts); F.append((o, o + 1, o + 2, o + 3))

    def flush(self, module):
        for role, (V, F) in self.g.items():
            if F:
                C.mesh(f'{module} {role}', V, F, role, module)
        self.g = {}


def face_of(side, box):
    x0, x1, y0, y1 = box
    if side == 'south':
        return C.Face(((x0 + x1) / 2, y0, 0), (1, 0, 0), (0, 1, 0), 'south'), x1 - x0
    if side == 'east':
        return C.Face((x1, (y0 + y1) / 2, 0), (0, 1, 0), (-1, 0, 0), 'east'), y1 - y0
    if side == 'north':
        return C.Face(((x0 + x1) / 2, y1, 0), (-1, 0, 0), (0, -1, 0), 'north'), x1 - x0
    return C.Face((x0, (y0 + y1) / 2, 0), (0, -1, 0), (1, 0, 0), 'west'), y1 - y0


def brick_base(f, lo, hi, tag, entry_u=None):
    """Two-storey brick base: tall ground windows and second-floor windows on a 4.2 m rhythm."""
    span = hi - lo
    n = max(1, int(span / 4.2))
    holes = []
    for i in range(n):
        u = lo + span * (i + .5) / n
        if entry_u is not None and abs(u - entry_u) < 2.2:
            holes.append(hole(f'{tag} entrance {i}', u, G0, 3.0, 3.4, kind='door'))
        else:
            holes.append(hole(f'{tag} ground window {i}', u, .9, 2.6, 3.0))
        holes.append(hole(f'{tag} second window {i}', u, 5.8, 2.6, 2.3))
    f.wall(f'{tag} brick base', lo, hi - EPS, G0, BASE_TOP, depth=T, holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, G0 + .02, BASE_TOP - .3, holes, spacing=.2)
    m = Merge(f)
    for h in holes:
        framed(m, f, h, cols=2, rows=2 if h['h'] > 2.5 else 1, inset=.14, occupied='outpatients', kind=h.get('kind', 'window'))
        if h['z'] > .5:
            m.box('stone', h['u'], -.04, h['z'] - .06, h['w'] + .16, .14, .12)
    m.box('concrete', (lo + hi) / 2, -.06, BASE_TOP - .2, span - 2 * EPS, T + .12, .4)
    m.flush(tag + ' base')


def perforated_face(f, lo, hi, tag, sign_u=None, plant=True):
    """Pale clinical storeys: one strip window per floor behind perforated pale screen panels (dot fields), mullions."""
    span = hi - lo
    holes = [hole(f'{tag} strip window f{i + 3}', (lo + hi) / 2, BASE_TOP + i * FH + .8, span - 1.0, 2.5, kind='band') for i in range(5)]
    f.wall(f'{tag} pale carrier', lo, hi - EPS, BASE_TOP, PB_TOP, depth=T, role='pale', holes=holes)
    m = Merge(f)
    b = Batch()
    for h in holes:
        m.box('glass', h['u'], .14, h['z'] + h['h'] / 2, h['w'] - .02, .012, h['h'] - .02)
        register(f, h, .1, 'strip window', 'clinics')
        n = int(h['w'] / 1.6)
        for k in range(n + 1):
            m.box('trim', h['u'] - h['w'] / 2 + h['w'] * k / n, .1, h['z'] + h['h'] / 2, .06, .08, h['h'])
    n = int((span - .6) / 1.6)
    for fi in range(5):
        z = BASE_TOP + fi * FH
        for k in range(n):
            u = lo + .3 + 1.6 * (k + .5)
            if sign_u is not None and abs(u - sign_u) < 2.0:
                continue
            m.box('pale', u, -.38, z + FH / 2, 1.5, .06, FH - .2)                       # screen panel 0.35 m proud
            m.box('hardware', u, -.2, z + FH - .3, .08, .32, .08)                       # panel bracket
            for r in range(9):
                for c in range(3):
                    if (r + c + k) % 4 == 3:
                        continue
                    uu, zz = u - .45 + c * .45, z + .45 + r * .38
                    pts = [f.p(uu - .13, -.413, zz - .1), f.p(uu + .13, -.413, zz - .1), f.p(uu + .13, -.413, zz + .1), f.p(uu - .13, -.413, zz + .1)]
                    b.quad('perf', pts)
    m.box('concrete', (lo + hi) / 2, -.1, PB_TOP + .05, span - 2 * EPS, T + .2, .2)
    if sign_u is not None:                                                             # dark vertical signage panel
        m.box('sign', sign_u, -.55, BASE_TOP + 9.6, 2.6, .3, 18.4)
        for k, (z, hh) in enumerate(((22.0, 2.4), (16.5, 3.2), (11.4, 2.0))):
            m.box('signlight', sign_u, -.71, z, 2.0, .02, hh)
        for z in (26.6, 25.8, 13.6, 12.9):
            m.box('pale', sign_u, -.71, z, 1.6, .02, .18)
    m.flush(tag + ' clinical')
    b.flush(tag + ' perforation')


def clinical_block():
    x0, x1, y0, y1 = PB
    for side, entry in (('south', -16.0), ('west', None), ('east', None)):
        f, span = face_of(side, PB)
        f.label = 'clinical ' + side
        lo, hi = (-span / 2, span / 2) if side in ('south', 'north') else (-span / 2 + T, span / 2 - T)
        brick_base(f, lo, hi, f.label, entry)
        perforated_face(f, lo, hi, f.label, sign_u=8.4 - (x0 + x1) / 2 if side == 'south' else None)
    f, span = face_of('north', (x0, BAR[0], y0, y1))
    f.label = 'clinical north'
    brick_base(f, -span / 2, span / 2, f.label)
    perforated_face(f, -span / 2, span / 2, f.label)
    for z in [G0, BASE[1]] + [BASE_TOP + i * FH for i in range(5)]:
        C.box('Clinical floor', ((x0 + x1) / 2, (y0 + y1) / 2, z - .15 if z > G0 else G0 / 2), (x1 - x0 - (2 * T if z > G0 else 0), y1 - y0 - (2 * T if z > G0 else 0), .3 if z > G0 else G0), 'floor' if z > G0 else 'foundation', 'clinical floors', 0)
        for x in (-30.0, -18.0, -6.0, 6.0):
            C.qa_room_light(f'Clinical {x:+.0f} {z:.0f}', (x, y0 + 4.0, z + 3.2), 70, 6.0)
    C.box('Clinical roof slab', ((x0 + x1) / 2, (y0 + y1) / 2, PB_TOP - .15), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .3), 'floor', 'clinical roof', 0)
    C.box('Clinical core', (-12.0, -6.0, (G0 + PB_TOP) / 2), (10.0, 6.0, PB_TOP - G0), 'concrete', 'clinical core', 0)
    # Recessed plant storey behind a dark louvre band, its roof, and the raised canopy frame over the west roof.
    px0, px1, py0, py1 = x0 + 1.5, x1 - 1.5, y0 + 1.5, y1 - .3
    for side in ('south', 'west', 'east', 'north'):
        f, span = face_of(side, (px0, px1 - T, py0, py1) if side == 'north' else (px0, px1, py0, py1))
        f.label = 'plant ' + side
        lo, hi = (-span / 2, span / 2) if side in ('south', 'north') else (-span / 2 + T, span / 2)
        f.wall(f.label + ' backing', lo, hi - EPS, PB_TOP, PLANT_TOP, depth=T, role='louvre')
        m = Merge(f)
        for k in range(12):
            m.box('hardware', (lo + hi) / 2, -.1, PB_TOP + .3 + k * .32, hi - lo, .2, .08)
        m.box('trim', (lo + hi) / 2, -.12, PLANT_TOP + .05, hi - lo + .1, T + .3, .2)
        m.flush('plant storey')
    C.box('Plant roof', ((px0 + px1) / 2, (py0 + py1) / 2, PLANT_TOP - .15), (px1 - px0 - 2 * T, py1 - py0 - T, .3), 'membrane', 'plant storey', 0)
    C.box('Clinical terrace membrane', ((x0 + x1) / 2, (y0 + y1) / 2, PB_TOP + .005), (x1 - x0 - 2 * T - .02, y1 - y0 - 2 * T - .02, .01), 'membrane', 'clinical roof', 0)
    for x, y in ((4.0, -4.0), (7.0, -4.0), (4.0, 1.5)):
        C.box('Condenser', (x, y, PLANT_TOP + .7), (2.4, 1.6, 1.4), 'pale', 'plant', 0)
        for dx in (-.6, .6):
            C.rod('Condenser fan', (x + dx, y, PLANT_TOP + 1.4), (x + dx, y, PLANT_TOP + 1.5), .5, 'hardware', 'plant', 10)
    cx0, cx1, cy0, cy1 = x0 - .6, -4.0, y0 - .6, y1 - 2.2     # clear of the bar's braced frame
    za, zb = 35.2, 37.4                                                # canopy rises toward the west (front view)
    zl = lambda x: za + (zb - za) * (cx1 - x) / (cx1 - cx0)
    C.prism('Roof canopy plate', [(cx0 + 1.6, zl(cx0 + 1.6)), (cx1 - 1.6, zl(cx1 - 1.6)), (cx1 - 1.6, zl(cx1 - 1.6) - .25), (cx0 + 1.6, zl(cx0 + 1.6) - .25)], 'y', cy0 + 1.6, cy1 - 1.6, 'pale', 'roof canopy')
    for a, c in ((cx0, cx0 + 1.6), (cx1 - 1.6, cx1)):
        C.prism('Roof canopy glass edge', [(a, zl(a)), (c, zl(c)), (c, zl(c) - .06), (a, zl(a) - .06)], 'y', cy0, cy1, 'glass', 'roof canopy')
    for ya, yb in ((cy0, cy0 + 1.6), (cy1 - 1.6, cy1)):
        C.prism('Roof canopy glass edge', [(cx0 + 1.6, zl(cx0 + 1.6)), (cx1 - 1.6, zl(cx1 - 1.6)), (cx1 - 1.6, zl(cx1 - 1.6) - .06), (cx0 + 1.6, zl(cx0 + 1.6) - .06)], 'y', ya, yb, 'glass', 'roof canopy')
    b = Batch()
    for k in range(9):                                                 # steel frame under the canopy
        x = cx0 + (cx1 - cx0) * k / 8
        b.box('steel', x, (cy0 + cy1) / 2, zl(x) - .32, .16, cy1 - cy0, .18)
    for k in range(7):
        y = cy0 + (cy1 - cy0) * k / 6
        C.beam('Roof canopy purlin', (cx0, y, zl(cx0) - .32), (cx1, y, zl(cx1) - .32), .14, .16, 'steel', 'roof canopy')
    b.flush('roof canopy frame')
    for x in (cx0 + 2.0, (cx0 + cx1) / 2, cx1 - 2.0):
        for y in (cy0 + 2.0, (cy0 + cy1) / 2, cy1 - 2.0):
            base = PLANT_TOP if (px0 < x < px1 and py0 < y < py1) else PB_TOP
            C.rod('Roof canopy post', (x, y, base), (x, y, zl(x) - .4), .14, 'steel', 'roof canopy', 10)
    C.CONTACTS.append(dict(name='Plant storey set back behind louvres on the clinical roof; canopy on posts', plant_m=[PB_TOP, PLANT_TOP]))


def curtain_face(f, lo, hi, z0, z1, tag):
    holes = [hole(f'{tag} glazing f{i}', (lo + hi) / 2, z + .7, hi - lo - .8, FH - 1.0, kind='band') for i, z in enumerate(range(int(z0), int(z1) - 1, int(FH)))]
    f.wall(f'{tag} spandrel carrier', lo, hi - EPS, z0, z1, depth=T, role='trim', holes=holes)
    m = Merge(f)
    for h in holes:
        m.box('glass', h['u'], .12, h['z'] + h['h'] / 2, h['w'] - .02, .012, h['h'] - .02)
        register(f, h, .1, 'curtain wall', 'wards')
        n = max(1, int(h['w'] / 1.25))
        for k in range(1, n):
            m.box('steel', h['u'] - h['w'] / 2 + h['w'] * k / n, .06, h['z'] + h['h'] / 2, .06, .08, h['h'])
    m.box('steel', (lo + hi) / 2, -.1, z1 + .05, hi - lo - 2 * EPS, T + .2, .2)
    m.flush(tag + ' curtain wall')


def exo(f, lo, hi, ext_lo, ext_hi, tag, skip=(), z0=BASE_TOP, col_base=G0, tiers=None):
    """Standing steel exoskeleton: columns on a 5 m bay EXO off the glass, ring beams on five even tiers, X-braces with
    node plates. Corner columns shared with the neighbouring face are drawn once (skip holds their indices)."""
    a, c = lo - ext_lo, hi + ext_hi
    n = max(1, round((c - a) / 5.0))
    us = [a + (c - a) * i / n for i in range(n + 1)]
    skip = {i % (n + 1) for i in skip}
    if tiers is None:
        tiers = [BASE_TOP + (BB_TOP - BASE_TOP) * k / 5 for k in range(6)]
    tiers = [z0] + [z for z in tiers if z > z0 + 1.0]
    m = Merge(f)
    for i, u in enumerate(us):
        if i in skip:
            continue
        m.box('steel', u, -EXO, (col_base + BB_TOP + .3) / 2, .45, .45, BB_TOP + .3 - col_base)
        for z in tiers:
            m.box('steel', u, -EXO / 2, z, .2, EXO - .2, .2)                  # brackets back to the slab edge
    for z in tiers:
        m.box('steel', (a + c) / 2, -EXO, z, c - a - .46, .36, .36)
    for k in range(len(tiers) - 1):
        for i in range(n):
            m.box('steel', (us[i] + us[i + 1]) / 2, -EXO, (tiers[k] + tiers[k + 1]) / 2, .5, .34, .5)   # node plate at the X crossing
    m.flush(tag + ' exoskeleton')
    for k in range(len(tiers) - 1):
        za, zb = tiers[k] + .2, tiers[k + 1] - .2
        for i in range(n):
            u0, u1 = us[i] + .25, us[i + 1] - .25
            C.beam(f'{tag} brace', f.p(u0, -EXO, za), f.p(u1, -EXO, zb), .22, .22, 'steel', 'exoskeleton')
            C.beam(f'{tag} brace', f.p(u0, -EXO - .04, zb), f.p(u1, -EXO - .04, za), .22, .22, 'steel', 'exoskeleton')


def ward_block():
    lx0, lx1, ly0, ly1 = LEG
    bx0, bx1, by0, by1 = BAR
    outline = (bx0, lx1, ly0, ly1)
    # Leg south and east, combined north face, bar west: brick base under a curtain wall and the exoskeleton.
    fs, span = face_of('south', LEG); fs.label = 'ward south'
    brick_base(fs, -span / 2, span / 2, fs.label)
    curtain_face(fs, -span / 2, span / 2, BASE_TOP, BB_TOP, fs.label)
    exo(fs, -span / 2, span / 2, 0.0, EXO, fs.label)
    fe, span = face_of('east', LEG); fe.label = 'ward east'
    brick_base(fe, -span / 2 + T, span / 2 - T, fe.label, entry_u=-14.0)
    curtain_face(fe, -span / 2 + T, span / 2 - T, BASE_TOP, BB_TOP, fe.label)
    exo(fe, -span / 2, span / 2, EXO, EXO, fe.label, skip=(0, -1))      # both corners belong to the south and north faces
    fn, span = face_of('north', (bx0, lx1, by1 - 1, ly1)); fn.label = 'ward north'
    brick_base(fn, -span / 2, span / 2, fn.label, entry_u=4.0)
    curtain_face(fn, -span / 2, span / 2, BASE_TOP, BB_TOP, fn.label)
    exo(fn, -span / 2, span / 2, EXO, EXO, fn.label, skip=(-1,))
    fw, span = face_of('west', BAR); fw.label = 'ward west'
    brick_base(fw, -span / 2 + T, span / 2 - T, fw.label)
    curtain_face(fw, -span / 2 + T, span / 2 - T, BASE_TOP, BB_TOP, fw.label)
    exo(fw, -span / 2, span / 2, EXO, 0.0, fw.label)
    # Inner faces: leg west (south of the bar, partly behind the atrium), bar south above the clinical roof and behind the atrium.
    fi = C.Face((lx0, (ly0 + by0) / 2, 0), (0, -1, 0), (1, 0, 0), 'ward leg west')
    span = by0 - ly0
    brick_base(fi, -span / 2 + T, span / 2 - T, fi.label)
    curtain_face(fi, -span / 2 + T, span / 2 - T, BASE_TOP, BB_TOP, fi.label)
    fb = C.Face(((bx0 + ATR[0]) / 2, by0, 0), (1, 0, 0), (0, 1, 0), 'ward bar south')
    span = ATR[0] - bx0
    curtain_face(fb, -span / 2 + T, span / 2, PB_TOP + .05, BB_TOP, fb.label)
    fx = C.Face(((bx0 + lx0) / 2, by0, 0), (1, 0, 0), (0, 1, 0), 'ward bar south frame')
    exo(fx, -(lx0 - bx0) / 2, (lx0 - bx0) / 2, 0.0, 0.0, fx.label, z0=PLANT_TOP, col_base=PLANT_TOP)
    fa = C.Face(((ATR[0] + ATR[1]) / 2, by0, 0), (1, 0, 0), (0, 1, 0), 'ward atrium back')
    span = ATR[1] - ATR[0]
    curtain_face(fa, -span / 2, span / 2, G0, BB_TOP, fa.label)
    for z in [BASE[1]] + [BASE_TOP + i * FH for i in range(7)]:
        C.box('Ward bar floor', ((bx0 + bx1) / 2, (by0 + by1) / 2, z - .15), (bx1 - bx0 - 2 * T, by1 - by0 - 2 * T, .3), 'floor', 'ward floors', 0)
        C.box('Ward leg floor', ((lx0 + lx1) / 2, (ly0 + by1) / 2, z - .15), (lx1 - lx0 - 2 * T, by1 - ly0 - 2 * T, .3), 'floor', 'ward floors', 0)
        for x, y in ((-20.0, 20.0), (0.0, 20.0), (26.0, 0.0), (26.0, -18.0)):
            C.qa_room_light(f'Ward {x:+.0f} {y:+.0f} {z:.0f}', (x, y, z + 3.2), 60, 5.0)
    C.box('Ward ground slab', ((bx0 + lx1) / 2, (ly0 + ly1) / 2, G0 / 2), (lx1 - bx0, ly1 - ly0, G0), 'foundation', 'ward floors', 0)
    C.box('Ward bar roof', ((bx0 + bx1) / 2, (by0 + by1) / 2, BB_TOP - .15), (bx1 - bx0 - 2 * T, by1 - by0 - 2 * T, .3), 'floor', 'ward roof', 0)
    C.box('Ward leg roof', ((lx0 + lx1) / 2, (ly0 + by0) / 2, BB_TOP - .15), (lx1 - lx0 - 2 * T, by0 - ly0 - T, .3), 'floor', 'ward roof', 0)
    C.box('Ward roof membrane', ((bx0 + lx1) / 2, (by0 + by1) / 2, BB_TOP + .005), (lx1 - bx0 - 2 * T - .02, by1 - by0 - 2 * T - .02, .01), 'membrane', 'ward roof', 0)
    C.box('Ward leg roof membrane', ((lx0 + lx1) / 2, (ly0 + by0) / 2, BB_TOP + .005), (lx1 - lx0 - 2 * T - .02, by0 - ly0 - T - .02, .01), 'membrane', 'ward roof', 0)
    # Rooftop plant (top view): air handlers with ducts, a stair penthouse, three condensers in a row.
    C.box('Air handler', (-8.0, 15.0, BB_TOP + 1.0), (5.0, 3.0, 2.0), 'pale', 'ward plant', 0)
    C.box('Stair penthouse', (-2.0, 19.0, BB_TOP + 1.4), (4.0, 4.0, 2.8), 'pale', 'ward plant', 0)
    for x in (-14.0, 0.0, 8.0):
        C.box('Duct run', (x, 15.0, BB_TOP + .45), (6.0, .9, .9), 'pale', 'ward plant', 0)
    for x in (-2.4, 0.4, 3.2):
        C.box('Condenser', (x, 23.4, BB_TOP + .8), (2.2, 1.8, 1.6), 'pale', 'ward plant', 0)
    for x, y in ((14.0, 12.0), (18.0, 20.0), (-20.0, 22.0), (26.0, -10.0)):
        C.rod('Exhaust stack', (x, y, BB_TOP), (x, y, BB_TOP + 1.6), .3, 'pale', 'ward plant', 10)
    C.CONTACTS.append(dict(name='Exoskeleton columns from the brick base to the roof ring, bracketed to every second slab', top_m=BB_TOP))


def atrium():
    x0, x1, y0, y1 = ATR
    f = C.Face(((x0 + x1) / 2, y0, 0), (1, 0, 0), (0, 1, 0), 'atrium south')
    w = x1 - x0
    xr = x1 - .3                                                       # east return clear of the ward leg's corner column
    C.box('Atrium south glass', ((x0 + xr) / 2, y0 + .05, (G0 + ATR_TOP) / 2), (xr - x0 - .1, .03, ATR_TOP - G0), 'glass', 'atrium', 0)
    for xx, ye in ((x0 + .05, PB[2]), (xr, LEG[2])):
        C.box('Atrium return glass', (xx, (y0 + ye) / 2, (G0 + ATR_TOP) / 2), (.03, ye - y0, ATR_TOP - G0), 'glass', 'atrium', 0)
        C.box('Atrium return mullion', (xx, (y0 + ye) / 2, (G0 + ATR_TOP) / 2), (.1, .1, ATR_TOP - G0), 'steel', 'atrium', 0)
    C.box('Atrium closer', ((xr + x1) / 2, LEG[2] + .05, (G0 + ATR_TOP) / 2), (x1 - xr, .1, ATR_TOP - G0), 'steel', 'atrium', 0)
    C.OPENINGS.append(dict(id='atrium south glazing', face=f.label, u=0, z=G0, width=w, height=ATR_TOP - G0, kind='glass atrium', clear_wall_cut=True,
        carrier_depth_m=.1, frame_inset_m=0, pane_inset_m=.05, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='atrium hall'))
    b = Batch()
    b.box('steel', x0 + .12, y0 + .1, (G0 + ATR_TOP) / 2, .24, .24, ATR_TOP - G0)
    b.box('steel', xr - .12, y0 + .1, (G0 + ATR_TOP) / 2, .24, .24, ATR_TOP - G0)
    b.box('steel', (x0 + xr) / 2, y0 + .1, ATR_TOP - .1, xr - x0 - .5, .2, .2)        # between the edge posts, set back
    b.box('steel', (x0 + xr) / 2, y0 + .1, 3.9, xr - x0 - .5, .2, .16)
    b.flush('atrium frame')
    # Diagonal mullion net on the south glass.
    step = 2.4
    H = ATR_TOP - G0
    w = xr - x0
    mg = .26                                                           # members stop inside the edge posts
    u_of = lambda q: q - (x1 - x0) / 2                                 # net coordinate (0..w from the west post) to face u
    fam = {1: [], -1: []}
    for s in (1, -1):
        c = -H if s > 0 else 0.0
        c_end = w if s > 0 else w + H
        c += step / 2
        while c < c_end:
            lo, hi = (mg - c, w - mg - c) if s > 0 else (c - w + mg, c - mg)
            za, zb = max(0.0, lo), min(H, hi)
            if zb - za > .15:
                d = -.03 if s > 0 else -.045                             # the two sets interpenetrate as one net
                C.beam('Atrium diagrid', f.p(u_of(c + s * za), d, G0 + za), f.p(u_of(c + s * zb), d, G0 + zb), .08, .08, 'steel', 'atrium')
                fam[s].append(c)
            c += step
    nb = Batch()
    for c1 in fam[1]:
        for c2 in fam[-1]:
            z, q = (c2 - c1) / 2, (c1 + c2) / 2
            if 0.0 < z < H and mg < q < w - mg:
                p = f.p(u_of(q), -.05, G0 + z)
                nb.box('steel', p[0], p[1], p[2], .16, .12, .16)            # node block at each crossing
    nb.flush('atrium diagrid nodes')
    # Glass roof, west glass above the clinical roof, entrance doors, bridges, a glass lift.
    w = x1 - x0
    C.box('Atrium roof glass', ((x0 + x1) / 2, (y0 + y1) / 2, ATR_TOP), (w, y1 - y0 - .02, .06), 'glass', 'atrium', 0)
    for xx in (x0 + .1, x1 - .1):
        C.box('Atrium top edge', (xx, (y0 + y1) / 2, ATR_TOP + .12), (.2, y1 - y0, .24), 'steel', 'atrium', 0)
    for k in range(9):
        C.box('Atrium roof rib', ((x0 + x1) / 2, y0 + (y1 - y0) * k / 8, ATR_TOP + .08), (w + .1, .14, .14), 'steel', 'atrium', 0)
    C.box('Atrium west glass', (x0 + .05, (y0 + y1) / 2, (PB_TOP + ATR_TOP) / 2 + .1), (.03, y1 - y0, ATR_TOP - PB_TOP - .2), 'glass', 'atrium', 0)
    for x in (x0 + 2.2, x1 - 2.2):
        C.rod('Revolving door drum', (x, y0 + .9, G0), (x, y0 + .9, 2.6), 1.1, 'glass', 'atrium', 16)
        C.rod('Revolving door canopy', (x, y0 + .9, 2.6), (x, y0 + .9, 2.8), 1.2, 'steel', 'atrium', 16)
    for z in (BASE_TOP + 8.0, BASE_TOP + 16.0):
        C.box('Atrium bridge', ((x0 + x1) / 2, -6.0, z - .25), (w - .02, 2.6, .5), 'concrete', 'atrium', 0)
        C.box('Atrium bridge guard', ((x0 + x1) / 2, -7.3, z + .55), (w - .04, .03, 1.1), 'glass', 'atrium', 0)
    C.box('Atrium lift', (x0 + 2.0, y1 - 3.0, (G0 + ATR_TOP - 2) / 2), (2.4, 2.4, ATR_TOP - 2 - G0), 'glass', 'atrium', 0)
    C.box('Atrium floor', ((x0 + x1) / 2, (y0 + y1) / 2, G0 / 2), (w, y1 - y0, G0), 'sand', 'atrium', 0)
    for z in (4.0, 14.0, 24.0):
        C.qa_room_light(f'Atrium {z:.0f}', ((x0 + x1) / 2, -10.0, z), 140, 6.0)
    C.box('Reception desk', ((x0 + x1) / 2, -14.0, G0 + .55), (4.0, 1.0, 1.1), 'pale', 'atrium', 0)
    # Entrance canopy: glass on a steel frame in front of the atrium, hung on tension rods, two posts.
    a, c, e, g = 7.0, 27.0, -36.0, -30.4
    C.box('Entrance canopy glass', ((a + c) / 2, (e + g) / 2, 5.6), (c - a, g - e, .06), 'glass', 'entrance canopy', 0)
    for yy in (e, g):
        C.box('Entrance canopy edge', ((a + c) / 2, yy, 5.48), (c - a, .16, .18), 'steel', 'entrance canopy', 0)
    for xx in (a, c):
        C.box('Entrance canopy edge', (xx, (e + g) / 2, 5.48), (.16, g - e - .16, .18), 'steel', 'entrance canopy', 0)
    # Hanger rods fan from anchors on structure only: the atrium's two edge posts and the ward leg's frame column.
    leg_col = (21.0 + (LEG[1] + EXO)) / 2                              # the middle column of the ward leg's south frame
    anchors = (((x0 + .12, y0 - .15, 14.0), (8.0, 11.5)), ((xr - .12, y0 - .15, 14.0), (15.0, 18.5)),
               ((leg_col, LEG[2] - EXO - .25, BASE_TOP + (BB_TOP - BASE_TOP) / 5), (22.5, 26.0)))
    for (ax, ay, az), xs in anchors:
        C.box('Canopy rod anchor plate', (ax, ay - .02, az), (.34, .1, .34), 'steel', 'entrance canopy', 0)
        for x in xs:
            C.rod('Canopy tension rod', (ax, ay - .06, az), (x, e + .1, 5.62), .03, 'steel', 'entrance canopy', 6)
    for x in (9.0, 25.0):
        C.rod('Canopy post', (x, e + .6, .14), (x, e + .6, 5.4), .12, 'steel', 'entrance canopy', 10)
    C.CONTACTS.append(dict(name='Atrium between the clinical block and the ward leg; entrance canopy on rods and two posts', atrium=list(ATR)))


def site():
    C.box('South sidewalk', (-3.0, -31.5, .07), (82.0, 9.0, .14), 'concrete', 'site', 0)
    C.box('West sidewalk', (-41.5, 0.0, .07), (7.0, 54.0, .14), 'concrete', 'site', 0)
    C.box('East sidewalk', (34.5, 0.0, .07), (7.0, 54.0, .14), 'concrete', 'site', 0)
    C.box('South street', (-3.0, -42.0, .01), (100.0, 12.0, .02), 'asphalt', 'site', 0)
    C.box('West street', (-51.0, -2.0, .01), (12.0, 68.0, .02), 'asphalt', 'site', 0)
    C.box('East street', (44.0, -2.0, .01), (12.0, 68.0, .02), 'asphalt', 'site', 0)
    C.box('North lane', (-3.0, 29.0, .01), (82.0, 6.0, .02), 'asphalt', 'site', 0)
    b = Batch()
    for k in range(9):
        b.box('white', -40.0 + k * .9, -38.8, .025, .5, 2.6, .01)
        b.box('white', 31.0 + k * .9, -38.8, .025, .5, 2.6, .01)
    for k in range(10):
        b.box('white', -48.0 + k * 9.5, -42.0, .025, 3.0, .15, .01)
    b.flush('road markings')
    for x in (-30.0, -10.0, 4.0):
        street_tree(x, -30.0, z=.14, height=7.5, spread=1.8)
    for y in (-14.0, 2.0, 18.0):
        street_tree(-41.0, y, z=.14, height=7.5, spread=1.8)
        street_tree(35.5, y, z=.14, height=7.5, spread=1.8)


def build():
    site()
    clinical_block()
    ward_block()
    atrium()
    C.CONTACTS.append(dict(name='Three volumes on one podium: clinical block south-west, L-shaped ward block north and east, atrium between', plan=[PB, LEG, BAR, ATR]))


LIGHT_RIG = dict(key=(-80, -90, 100), fill=(90, -40, 70), rear=(-30, 90, 90), target=(0, 0, 16.0), gain=24.0)
