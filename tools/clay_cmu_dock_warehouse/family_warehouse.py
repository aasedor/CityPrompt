"""Mid-century distribution warehouse, authored from the locked catalogue views of
mid_century_distribution_warehouse / variant_0 (cmu_dock_utilitarian).

Read from the pixels (the top view governs the plan): a single-storey block of painted beige concrete
masonry units, about 1.3 times as wide as it is deep, on a street corner with the street south and a
parking lane east. Four raised loading bays along the west half of the south face, each an overhead
sectional door with a row of small lites inside a dark steel surround, with black dock bumpers and yellow
guide posts at dock height. East of them a glazed aluminium entry door with a sidelight under a flat
concrete canopy hung on two rods, a wide aluminium window beside it, and a long cast-concrete landing
with steps at its west end in front. Punched windows on the east face, one low near the south corner and
two high clerestory windows. A flat parapet with a thin pale metal coping round a grey membrane roof
carrying two rooftop units, four small vent domes and pipe vents.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-cmu-dock-warehouse'
X0, X1, Y0, Y1 = -17.0, 17.0, -13.0, 13.0       # 34 x 26 m block (top view: width about 1.3 x depth)
T = .30
G0 = .15
FL = 1.2                                          # dock-height floor
EAVE = 7.0                                        # top of the CMU wall
PARA = EAVE + .4
EPS = .002
DOCKS = [-14.0, -9.6, -5.2, -0.8]                # dock door centres along the south face (west half)
ENTRY = 4.6                                       # entry door centre
PALETTE = dict(wall=(.72, .64, .50), joint=(.62, .55, .43), trim=(.70, .72, .73),
    pale=(.88, .88, .86), stone=(.66, .65, .62), roof=(.50, .52, .54), sand=(.66, .64, .60),
    foundation=(.46, .46, .45), glass=(.38, .46, .50), hardware=(.14, .14, .15),
    interior=(.78, .76, .72), floor=(.56, .55, .53), timber=(.50, .36, .22), blue=(.20, .32, .52),
    planting=(.30, .44, .18), soil=(.22, .16, .10), concrete=(.70, .69, .66), white=(.90, .90, .88),
    asphalt=(.28, .28, .29), membrane=(.52, .54, .56), dock=(.16, .15, .14), bumper=(.08, .08, .08),
    yellow=(.86, .70, .12), door=(.86, .86, .84), car=(.50, .14, .12))


def manifest(version):
    h = PARA + 1.2
    cams = G.camera_roster(X1 - X0 + 4.0, Y1 - Y0 + 6.0, h, [
        ('facade_close', (-6.0, -30.0, 4.5), (-6.0, Y0, 4.0), 45),
        ('architecture_close', (24.0, -24.0, 6.0), (X1, Y0, 4.5), 45),
        ('glass_close', (ENTRY + 1.5, -22.0, 2.6), (ENTRY + 1.5, Y0, 2.8), 45),
        ('dock_doors', (-8.0, -20.0, 2.2), (-8.0, Y0, 2.6), 45),
        ('entry_canopy', (ENTRY - 4.0, -9.0 - 9.0, 3.4), (ENTRY, Y0, 3.6), 45),
        ('roof_units', (-12.0, -18.0, 16.0), (-2.0, 2.0, EAVE), 45),
        ('east_windows', (30.0, -8.0, 4.0), (X1, -6.0, 4.0), 45),
        ('parapet_corner', (24.0, -22.0, 12.0), (X1, Y0, PARA), 40),
        ('interior', (12.0, -2.5, FL + 1.7), (-12.0, -2.5, FL + 2.0), 40),
        ('rear_north', (0.0, 34.0, 5.0), (0.0, Y1, 4.0), 45)])
    for c in cams:                       # the locked front and oblique look from the south-west street corner
        if c['name'] == 'front':
            c['location'] = (-30.0, -36.0, 1.7); c['target'] = (-2.0, -6.0, 3.6); c['lens'] = 30; c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='mid_century_distribution_warehouse/variant_0 (cmu_dock_utilitarian)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=1, storey_programme='single-storey warehouse on a dock-height floor with an office corner behind the entry',
            plan='34 x 26 m block (top view); four loading bays along the west half of the south face; entry with a canopy and a concrete landing east of them',
            facade='painted beige CMU with horizontal coursing; dock doors in dark steel surrounds with black bumpers and yellow guides; aluminium entry door and windows; flat parapet with a thin pale metal coping',
            levels_m=[G0, FL, EAVE], parapet_m=PARA,
            inferred='the dock-height floor and interiors are teaching assumptions; the north and west faces are not visible in the front or oblique and repeat the visible grammar'),
        roof_contract=dict(type='flat grey membrane behind a low parapet with metal coping', datum_m=EAVE, crowns_m=[PARA, PARA + 1.0]),
        identity_contract=dict(owner='beige CMU box, four raised loading bays in dark surrounds, hung-rod entry canopy, concrete landing, flat parapet roof with rooftop units'),
        material_contract=dict(profile='source-palette clay: painted beige CMU, dark steel dock surrounds, white sectional doors, black bumpers, yellow guides, aluminium and glass, grey membrane, pale coping, concrete apron', textured_keeper=False),
        programme_contract=dict(storeys=1, ground='warehouse floor at dock height with pallet racking; office corner behind the entry', roof='rooftop units and vents'),
        contact_contract=['Grade-zero apron, sidewalks and landing', 'Dock doors at dock height above the apron', 'Canopy hung on rods from the wall', 'Rooftop units on the membrane'],
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


# ---- mid-century distribution warehouse ----

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


def cmu_face(f, lo, hi, holes, lite=False):
    """Painted CMU carrier from grade to the parapet with horizontal block coursing and a pale metal coping."""
    f.wall(f.label + ' CMU carrier', lo, hi - EPS, 0.0, PARA, depth=T, holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, .2, PARA - .1, holes, spacing=.2 if not lite else .4)
    m = Merge(f)
    m.box('pale', (lo + hi) / 2, (T - .08) / 2, PARA + .03, hi - lo - 2 * EPS, T + .08, .06)        # coping, ends butting the next face's
    m.box('pale', (lo + hi) / 2, -.05, PARA - .08, hi - lo - 2 * EPS, .04, .2)                      # coping fascia
    return m


def south_face():
    f = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south')
    lo, hi = X0, X1
    holes = [hole(f'dock door {i}', u, FL, 3.0, 3.0, kind='dock') for i, u in enumerate(DOCKS)]
    door = hole('entry door', ENTRY, FL, 1.9, 2.4, kind='door')
    win = hole('entry window', ENTRY + 3.4, FL + .85, 2.9, 1.75)
    holes += [door, win]
    m = cmu_face(f, lo, hi, holes)
    for h in holes[:4]:                                                   # loading bays
        u = h['u']
        for e in (-1, 1):
            m.box('dock', u + e * 1.72, -.18, FL + 1.55, .44, .36, 3.5)                # dark steel surround jambs
            m.box('bumper', u + e * 1.15, -.13, FL - .28, .34, .26, .42)               # dock bumpers
            m.box('yellow', u + e * 1.72, -.37, FL + 1.2, .06, .02, 2.2)               # yellow guide stripe on the jamb
        m.box('dock', u, -.21, FL + 3.32, 3.92, .42, .6)                                  # header, proud of the jambs
        m.box('dock', u, -.06, FL - .02, 2.7, .12, .1)                                    # leveller lip
        m.box('door', u, .14, FL + 1.5, 2.98, .04, 2.98)                                  # sectional door
        for k in range(1, 5):
            m.box('trim', u, .115, FL + .6 * k, 2.96, .02, .03)                           # panel joints
        for k in range(4):
            m.box('glass', u - 1.05 + k * .7, .11, FL + 1.9, .42, .02, .22)               # row of small lites
        C.OPENINGS.append(dict(id=h['id'], face=f.label, u=u, z=h['z'], width=h['w'], height=h['h'], kind='overhead dock door', clear_wall_cut=True,
            carrier_depth_m=T, frame_inset_m=.12, pane_inset_m=.14, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='warehouse'))
    framed(m, f, door, cols=2, rows=1, inset=.14, occupied='office lobby', kind='entry door')
    framed(m, f, win, cols=3, rows=1, inset=.14, occupied='office')
    m.box('stone', win['u'], -.04, win['z'] - .05, win['w'] + .16, .14, .1)
    m.flush('south')
    # Flat concrete canopy over the entry, hung on two rods from the wall.
    cz = FL + 2.75
    p = f.p(ENTRY, -.75, cz)
    C.box('Entry canopy', (p[0], p[1], p[2]), (3.6, 1.5, .18), 'concrete', 'entry', 0)
    for e in (-1, 1):
        C.rod('Canopy hanger rod', f.p(ENTRY + e * 1.5, -1.38, cz + .09), f.p(ENTRY + e * 1.7, -.02, cz + 1.45), .025, 'hardware', 'entry', 6)
        C.box('Canopy rod anchor', f.p(ENTRY + e * 1.7, -.03, cz + 1.45), (.16, .06, .16), 'hardware', 'entry', 0)
    # Cast-concrete landing in front of the entry, steps down at its west end.
    lx0, lx1 = ENTRY - 3.0, ENTRY + 5.6
    C.box('Entry landing', ((lx0 + lx1) / 2, Y0 - 1.1, FL / 2), (lx1 - lx0, 2.2, FL), 'concrete', 'entry', 0)
    for k in range(4):
        top = FL - (k + 1) * FL / 5
        C.box('Landing step', (lx0 - .15 - k * .3, Y0 - 1.1, top / 2), (.3, 1.6, top), 'concrete', 'entry', 0)


def other_faces():
    e = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    hd = (Y1 - Y0) / 2
    hs = [hole('east low window', -hd + 2.4, FL + .85, 1.3, 1.75)] + [hole(f'east clerestory {k}', u, 5.0, .8, 1.0) for k, u in enumerate((-4.5, 1.5))]
    m = cmu_face(e, -hd + T, hd - T, hs)
    for h in hs:
        framed(m, e, h, cols=2 if h['w'] > 1 else 1, rows=1, inset=.14, occupied='office' if h['w'] > 1 else 'warehouse')
        m.box('stone', h['u'], -.04, h['z'] - .05, h['w'] + .14, .14, .1)
    m.flush('east')
    n = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')
    hw = (X1 - X0) / 2
    hs = [hole('north service door', 6.0, FL, 1.0, 2.2, kind='door')] + [hole(f'north high window {k}', u, 5.0, .8, 1.0) for k, u in enumerate((-10.0, 0.0, 10.0))]
    m = cmu_face(n, -hw, hw, hs, lite=True)
    for h in hs:
        framed(m, n, h, cols=1, rows=1, inset=.14, occupied='warehouse', kind=h.get('kind', 'window'), lite=True)
    m.box('concrete', 6.0, -.9, FL / 2, 2.4, 1.8, FL)                                        # stoop at the service door
    m.flush('north')
    w = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west')
    hs = [hole(f'west high window {k}', u, 5.0, .8, 1.0) for k, u in enumerate((-5.0, 5.0))]
    m = cmu_face(w, -hd + T, hd - T, hs, lite=True)
    for h in hs:
        framed(m, w, h, cols=1, rows=1, inset=.14, occupied='warehouse', lite=True)
    m.flush('west')


def roof_and_interior():
    C.box('Ground slab', (0, 0, FL / 2), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, FL), 'floor', 'floor', 0)
    C.box('Roof deck', (0, 0, EAVE - .15), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .3), 'floor', 'roof', 0)
    C.box('Roof membrane', (0, 0, EAVE + .01), (X1 - X0 - 2 * T - .02, Y1 - Y0 - 2 * T - .02, .02), 'membrane', 'roof', 0)
    b = Batch()
    for k in range(1, 6):                                                # membrane seams
        b.box('roof', X0 + (X1 - X0) * k / 6, 0, EAVE + .025, .06, Y1 - Y0 - 2 * T - .1, .01)
    for x, y in ((-3.6, 2.4), (1.6, 2.4)):                               # rooftop units
        b.box('pale', x, y, EAVE + .55, 1.8, 1.3, 1.0)
        b.box('hardware', x - .3, y, EAVE + 1.06, .9, .9, .03)
        b.box('trim', x + .9, y - .4, EAVE + .2, .9, .12, .12)
    for x, y in ((-11.5, 9.0), (8.5, 9.0), (-12.0, -6.5), (9.0, -6.5)):  # vent domes
        b.box('white', x, y, EAVE + .2, .9, .7, .36)
    b.flush('roof plant')
    for x, y in ((-7.0, -1.0), (6.0, 4.0), (11.0, -1.0), (-14.0, 4.0)):  # pipe vents
        C.rod('Roof pipe vent', (x, y, EAVE + .02), (x, y, EAVE + .5), .06, 'pale', 'roof plant', 8)
    # Pallet racking and lights inside.
    b = Batch()
    for y in (-5.5, 0.5, 6.5):
        for k in range(9):
            x = -14.0 + k * 2.6
            for dy in (-.5, .5):
                b.box('blue', x, y + dy, FL + 2.3, .1, .1, 4.6)
            for zz in (FL + .15, FL + 1.7, FL + 3.2):
                b.box('yellow', x + 1.3, y - .5, zz, 2.6, .08, .1)
                b.box('yellow', x + 1.3, y + .5, zz, 2.6, .08, .1)
                b.box('timber', x + 1.3, y, zz + .12, 2.2, 1.0, .14)
                if (k + int(zz)) % 3:
                    b.box('pale', x + 1.3, y, zz + .7, 2.0, .9, 1.0)
    b.flush('racking')
    for x in (-10.0, 0.0, 10.0):
        for y in (-6.0, 4.0):
            C.qa_room_light(f'Warehouse {x:+.0f} {y:+.0f}', (x, y, EAVE - 1.0), 140, 6.0)
    C.qa_room_light('Office', (ENTRY + 2.0, Y0 + 3.0, FL + 2.6), 60, 4.0)
    C.CONTACTS.append(dict(name='Dock-height floor slab inside CMU walls from grade; docks open at dock height above the apron', floor_m=FL))


def site():
    C.box('South apron', (0, Y0 - 3.5, .03), (X1 - X0 + 10.0, 7.0, .06), 'concrete', 'site', 0)
    C.box('South street', (0, Y0 - 12.5, .01), (X1 - X0 + 26.0, 11.0, .02), 'asphalt', 'site', 0)
    C.box('East lane', (X1 + 6.0, 1.5, .01), (12.0, Y1 - Y0 + 3.0 - .01, .02), 'asphalt', 'site', 0)
    C.box('West truck court', (X0 - 7.0, 1.5, .01), (14.0, Y1 - Y0 + 3.0 - .01, .02), 'asphalt', 'site', 0)
    b = Batch()
    for k in range(10):
        b.box('white', X0 - 8.0 + k * 5.0, Y0 - 12.5, .025, 2.4, .14, .01)
    for k in range(5):
        b.box('white', X1 + 1.0 + 2.6 * 0, Y0 + 2.0 + k * 4.0, .025, 4.5, .12, .01)
    for (x, y) in ((X1 + 4.0, 4.0), (X1 + 4.0, -2.0)):                    # parked vehicles
        b.box('car', x, y, .7, 4.6, 1.9, 1.0)
        b.box('glass', x - .3, y, 1.45, 2.2, 1.7, .55)
        b.box('car', x - .3, y, 1.75, 2.2, 1.75, .06)
    b.flush('site')
    for x, y in ((X0 - 3.5, Y0 - 1.0), (X1 + 2.0, Y0 - 5.5)):
        street_tree(x, y, z=.06, height=7.5, spread=2.0)


def build():
    site()
    south_face()
    other_faces()
    roof_and_interior()
    C.CONTACTS.append(dict(name='Single-storey CMU warehouse: docks along the west half of the south face, hung canopy over the entry, flat parapet roof', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(-40, -60, 50), fill=(50, -30, 40), rear=(-20, 50, 40), target=(0, 0, 3.0), gain=6.0)
