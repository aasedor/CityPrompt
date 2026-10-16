"""New York pre-war apartment tower, authored from the locked catalogue views of
new_york_pre_war_apartment / variant_0 (prewar_beaux_arts_grand).

Read from the pixels (the top view governs the plan): a twelve-storey corner block with streets south
and east. A two-storey limestone base with rusticated joints, tall windows and the entrance on the
south face under a dark metal marquee; ten storeys of red-brown brick above a limestone belt course,
limestone quoin strips at every corner, a stacked limestone-framed bay over the entrance, flat stone
lintels and sills on dark double-hung windows, stacked iron balconies on both street faces; a deep
limestone cornice with modillions under a balustraded parapet with pedestals and corner urns. On the
dark roof a brick water-tank house with stone quoins under a copper pyramid, a steel grating catwalk
round it, plant units and three brick chimneys with clay pots.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-prewar-apartment-tower'
X0, X1, Y0, Y1 = -16.0, 16.0, -12.5, 12.5          # 32 x 25 m (top view at 0.049 m/px)
T = .36
G0 = .15
GF = 4.4
FH = 3.1
LEVELS = [G0, G0 + GF] + [G0 + GF + i * FH for i in range(1, 11)]
BASE_TOP = LEVELS[2]                               # top of the two-storey limestone base
ROOF = G0 + GF + 11 * FH                           # 38.65
PARA = ROOF + 1.6
TANK = (-4.7, 4.7, -3.2, 7.4)
TANK_H = 9.4                                       # about three storeys (oblique)
BAY = 3.2
EPS = .002
PALETTE = dict(wall=(.44, .21, .16), joint=(.32, .16, .12), trim=(.14, .14, .15),
    pale=(.84, .80, .72), stone=(.82, .78, .68), roof=(.30, .30, .31), sand=(.70, .67, .62),
    foundation=(.42, .42, .41), glass=(.36, .44, .48), hardware=(.10, .10, .11),
    interior=(.80, .76, .68), floor=(.46, .44, .42), timber=(.40, .28, .16), blue=(.14, .22, .28),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.66, .65, .62), copper=(.34, .23, .16),
    membrane=(.24, .24, .25), stonejoint=(.62, .58, .50), asphalt=(.30, .30, .31), clay_pot=(.66, .42, .30))


def manifest(version):
    h = PARA + TANK_H + 2.5
    cams = G.camera_roster(X1 - X0 + 4.0, Y1 - Y0 + 4.0, h, [
        ('facade_close', (-4.0, -34.0, 20.0), (-4.0, Y0, 20.0), 45),
        ('architecture_close', (26.0, -26.0, 36.0), (X1, Y0, 37.0), 45),
        ('glass_close', (-1.0, -22.0, 12.0), (0.0, Y0, 13.0), 45),
        ('entrance_marquee', (5.0, -22.0, 2.0), (0.0, Y0, 3.4), 45),
        ('limestone_base', (-14.0, -24.0, 3.0), (-10.0, Y0, 4.0), 45),
        ('fire_balconies', (30.0, -4.0, 20.0), (X1, 6.0, 20.0), 45),
        ('cornice_balustrade', (-24.0, -24.0, 44.0), (-12.0, Y0, ROOF), 45),
        ('tank_house', (22.0, -22.0, 56.0), (0.0, 2.0, ROOF + 5.0), 45),
        ('interior', (-6.0, -6.0, LEVELS[6] + 1.6), (-8.0, Y0 - 1.0, LEVELS[6] + 1.2), 55),
        ('rear_court', (-6.0, 30.0, 16.0), (-4.0, Y1, 18.0), 45)])
    for c in cams:                       # the locked front and oblique look from the south-east street corner
        if c['name'] == 'front_corner':
            lx, ly, lz = c['location']; c['location'] = (-lx, ly, lz)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='new_york_pre_war_apartment/variant_0 (prewar_beaux_arts_grand)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=12, storey_programme='two-storey limestone base (lobby, doctors\' offices), ten brick storeys of flats',
            plan='32 x 25 m corner block, streets south and east (top view at 0.049 m/px); water-tank house 9.4 x 10.6 m on the roof north of centre',
            facade='limestone base with rusticated joints; brick above a stone belt course; limestone quoin strips at the corners; the iron balconies stacked over the entrance marquee with a wide projecting limestone-framed bay and a heavy stone pier beside them; dark double-hung windows on a 3.2 m bay with flat stone lintels and sills; stacked iron balconies on both street faces; deep modillion cornice and balustraded parapet with pedestals and corner urns',
            levels_m=LEVELS + [ROOF], parapet_m=PARA,
            inferred='storey heights and interiors are teaching assumptions; the north and west faces are not visible in the front or oblique and repeat the visible grammar'),
        roof_contract=dict(type='flat dark membrane behind the balustrade; water-tank house under a copper pyramid; grating catwalk; chimneys', datum_m=ROOF, crowns_m=[PARA, ROOF + TANK_H + 2.2]),
        identity_contract=dict(owner='red-brown brick tower on a limestone base with quoins, stacked iron balconies, deep cornice and balustrade, copper-roofed water-tank house, entrance marquee'),
        material_contract=dict(profile='source-palette clay: red-brown brick with recessed courses, warm limestone, black iron, dark window frames, copper pyramid, dark roof membrane', textured_keeper=False),
        programme_contract=dict(storeys=12, ground='lobby and doorman desk behind the marquee', upper='four to six flats per floor', roof='water tank, plant, chimneys'),
        contact_contract=['Grade-zero slab, sidewalks and areaway railing', 'Brick above the stone belt course', 'Balconies bracketed off the floor slabs', 'Cornice and balustrade on the parapet', 'Tank house and catwalk on the roof slab'],
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


# ---- New York pre-war apartment tower ----

from contract import subtract_openings


def grooves(f, lo, hi, z0, z1, holes, spacing=.62, role='stonejoint'):
    """Rusticated limestone: horizontal recessed joints, interrupted at the openings."""
    vs, fs = [], []
    z = z0 + spacing
    while z < z1 - .05:
        for a, b in subtract_openings(lo, hi, z, z + .04, holes):
            o = len(vs)
            vs.extend([f.p(a, -.004, z), f.p(b, -.004, z), f.p(b, -.004, z + .04), f.p(a, -.004, z + .04)])
            fs.append((o, o + 1, o + 2, o + 3))
        z += spacing
    if fs:
        C.mesh(f.label + ' rustication joints', vs, fs, role, 'limestone base')


def balcony(m, f, u, z, w, depth=1.0, role='hardware', spacing=.16):
    """Iron balcony: plate deck, pickets standing on the deck between a bottom rail and the top rail."""
    m.box(role, u, -depth / 2 + .02, z - .06, w, depth + .04, .12)
    for zr, s_ in ((z + .98, .05), (z + .06, .04)):
        m.box(role, u, -depth + .04, zr, w, s_, s_)
        for e in (-1, 1):
            m.box(role, u + e * (w / 2 - .02), -depth / 2 + .02, zr, s_, depth - .04, s_)
    n = max(4, int(w / spacing))
    for i in range(n + 1):
        m.box(role, u - w / 2 + .02 + (w - .04) * i / n, -depth + .04, z + .5, .03, .03, .96)
    for e in (-1, 1):
        for j in range(1, int(depth / spacing)):
            m.box(role, u + e * (w / 2 - .02), -.02 - (depth - .06) * j / int(depth / spacing), z + .5, .03, .03, .96)


def elevation(f, lo, hi, stone_bay=None, balcony_bay=None, entrance=None, lite=False, z_offset=0.0, ext=(0.0, 0.0)):
    span = hi - lo
    wrap = T + .16 if ext[0] else 0.0                  # end faces' bands and quoins return round the corner
    lift = .01 if ext[0] else 0.0
    n = max(1, round(span / BAY))
    pitch = span / n
    us = [lo + pitch * (i + .5) for i in range(n)]
    # Limestone base: tall ground windows (entrance door on the stone bay), second-storey windows.
    bholes = []
    for i, u in enumerate(us):
        if entrance is not None and i == entrance:
            bholes.append(hole(f'{f.label} entrance', u, G0, 2.4, 3.3, kind='door'))
        else:
            bholes.append(hole(f'{f.label} ground window {i}', u, 1.0, 1.5, 2.9))
        bholes.append(hole(f'{f.label} second window {i}', u, LEVELS[1] + .7, 1.3, 2.0))
    f.wall(f.label + ' limestone base', lo, hi - EPS, G0, BASE_TOP, depth=T, role='stone', holes=bholes)
    grooves(f, lo + .02, hi - .02, G0 + .5, BASE_TOP - .3, bholes)
    m = Merge(f)
    for h in bholes:
        framed(m, f, h, cols=2, rows=2 if h['h'] > 2.5 else 2, inset=.16, occupied='lobby' if h.get('kind') == 'door' else 'offices', kind=h.get('kind', 'window'), lite=lite)
    m.box('stone', (lo + hi) / 2, -.12, BASE_TOP + .05 + lift, span - 2 * EPS + 2 * wrap, T + .26, .42)   # belt course
    m.box('stone', (lo + hi) / 2, -.06, G0 + .35 + lift, span - 2 * EPS + 2 * wrap, T + .14, .7)          # water table
    m.flush(f.label + ' base')
    # Brick storeys.
    holes = []
    for k, z in enumerate(LEVELS[2:]):
        for i, u in enumerate(us):
            if i == balcony_bay and k >= 1:
                holes.append(hole(f'{f.label} f{k + 3} balcony door {i}', u, z + .05, 1.15, 2.3, kind='door'))
            else:
                holes.append(hole(f'{f.label} f{k + 3} window {i}', u, z + .8, 1.25, 1.95))
    top = ROOF + .5
    f.wall(f.label + ' brick carrier', lo, hi - EPS, BASE_TOP, top, depth=T, holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, BASE_TOP + .3, ROOF - .1, holes, spacing=.2 if not lite else .4)
    m = Merge(f)
    for h in holes:
        framed(m, f, h, cols=1, rows=2, inset=.14, occupied='flat', kind=h.get('kind', 'window'), lite=lite)
        if h.get('kind') == 'door':
            balcony(m, f, h['u'], h['z'] - .05, 3.0, depth=1.0)
            continue
        if stone_bay is not None and abs(h['u'] - us[stone_bay]) < .1:
            continue                                                                           # framed by the stone bay
        m.box('stone', h['u'], -.05, h['z'] + h['h'] + .17, h['w'] + .34, .12, .32)              # flat stone lintel
        m.box('stone', h['u'], -.05, h['z'] - .06, h['w'] + .2, .16, .12)                        # sill
    if stone_bay is not None:                                                                  # wide projecting limestone bay
        u = us[stone_bay]; w = 1.25; fw = 2.9
        for e in (-1, 1):
            m.box('stone', u + e * (fw / 2 - .4), -.22, (BASE_TOP + ROOF) / 2, .8, .44, ROOF - BASE_TOP)
        for z in LEVELS[2:]:
            m.box('stone', u, -.17, z + .4, w + .02, .34, .78)
            m.box('stone', u, -.17, z + .8 + 1.95 + .2, w + .02, .34, .36)
            m.box('stone', u, -.3, z + .8 + 1.95 + .42, fw + .3, .2, .14)                      # small cornice on each head
        m.box('stone', u + pitch / 2 + .95, -.1, (BASE_TOP + ROOF) / 2, 1.1, .2, ROOF - BASE_TOP)   # heavy stone pier toward the corner
    for k in range(int((ROOF - BASE_TOP - .4) / .62)):                                         # quoin strips at both corners
        z = BASE_TOP + .5 + k * .62 + .27
        L = 1.0 if k % 2 == 0 else .62
        if wrap:
            L = .62 if k % 2 == 0 else 1.0                                                     # interlocks with the other face
        m.box('stone', lo - wrap + L / 2, -.04, z, L, .08, .54)
        m.box('stone', hi + wrap - L / 2, -.04, z, L, .08, .54)
    m.box('stone', (lo + hi) / 2, -.06, LEVELS[-1] - .2 + lift, span - 2 * EPS + 2 * wrap, T + .14, .3)   # band under the top storey
    eave_cornice(m, lo - ext[0], hi + ext[1], top + z_offset, span_t=T, proj=1.1, role='stone', modillions=not lite)
    m.flush(f.label + ' brick')
    # Balustrade on the parapet: plinth, balusters, rail, pedestals.
    b = Merge(f)
    zb = top + .03 + z_offset
    b.box('stone', (lo + hi) / 2, T / 2, zb + .1, span - 2 * EPS, T + .1, .2)
    nb = int(span / .34)
    for i in range(nb):
        u = lo + .3 + (span - .6) * i / max(1, nb - 1)
        if (i % 12) in (0, 1):
            continue
        b.box('pale', u, T / 2, zb + .5, .13, .13, .6)
    for i in range(0, nb, 12):
        u = lo + .3 + (span - .6) * i / max(1, nb - 1)
        b.box('stone', u + .17, T / 2, zb + .55, .5, .5, .9)
    b.box('stone', (lo + hi) / 2, T / 2, zb + .88, span - 2 * EPS, T + .16, .16)
    b.flush(f.label + ' balustrade')
    return us


def build_faces():
    hw, hd = (X1 - X0) / 2, (Y1 - Y0) / 2
    south = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south')
    us = elevation(south, -hw, hw, stone_bay=4, balcony_bay=3, entrance=3)        # balconies stacked over the marquee
    east = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    elevation(east, -hd + T, hd - T, stone_bay=None, balcony_bay=5, z_offset=.006, ext=(1.3, 1.3))
    north = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')
    elevation(north, -hw, hw, lite=True)
    west = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west')
    elevation(west, -hd + T, hd - T, balcony_bay=2, lite=True, z_offset=.006, ext=(1.3, 1.3))
    # Corner urns on the balustrade pedestals.
    zt = ROOF + .5 + 1.1
    for x in (X0 + .3, X1 - .3):
        for y in (Y0 + .3, Y1 - .3):
            sx, sy = (1 if x < 0 else -1), (1 if y < 0 else -1)
            C.box('Corner pedestal', (x - sx * .05, y - sy * .05, (ROOF + .52 + zt + .1) / 2), (1.1, 1.1, zt + .1 - ROOF - .52), 'stone', 'balustrade', 0)
            C.rod('Corner urn', (x, y, zt + .1), (x, y, zt + .6), .26, 'stone', 'balustrade', 12)
            C.rod('Corner urn lid', (x, y, zt + .6), (x, y, zt + .8), .12, 'stone', 'balustrade', 10)
    # Entrance marquee with tie rods, door lanterns.
    ue = us[3]
    C.box('Entrance marquee', (ue, Y0 - 1.45, 3.85), (5.0, 2.8, .45), 'hardware', 'entrance', 0)
    C.box('Marquee name band', (ue, Y0 - 2.87, 3.85), (4.0, .04, .2), 'pale', 'entrance', 0)
    for dx in (-2.3, 2.3):
        C.beam('Marquee tie rod', (ue + dx, Y0 - .05, 6.0), (ue + dx, Y0 - 2.7, 4.1), .04, .04, 'hardware', 'entrance')
        C.rod('Door lantern', (ue + dx * .7, Y0 - .25, 2.6), (ue + dx * .7, Y0 - .25, 3.1), .14, 'pale', 'entrance', 8)
    # Areaway railing along the east face.
    for k in range(48):
        y = Y0 + 2.0 + (Y1 - Y0 - 4.0) * k / 47
        C.rod('Areaway picket', (X1 + .9, y, .14), (X1 + .9, y, 1.1), .018, 'hardware', 'areaway', 6)
    C.beam('Areaway rail', (X1 + .9, Y0 + 2.0, 1.1), (X1 + .9, Y1 - 2.0, 1.1), .05, .05, 'hardware', 'areaway')
    C.beam('Areaway rail low', (X1 + .9, Y0 + 2.0, .3), (X1 + .9, Y1 - 2.0, .3), .04, .04, 'hardware', 'areaway')


def floors_and_roof():
    for i, z in enumerate(LEVELS):
        if i == 0:
            C.box('Ground slab', (0, 0, G0 / 2), (X1 - X0, Y1 - Y0, G0), 'foundation', 'floors', 0)
            continue
        C.box(f'Floor {i}', (0, 0, z - .15), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .3), 'floor', 'floors', 0)
        for x in (-10.0, 0.0, 10.0):
            C.qa_room_light(f'Flat {x:+.0f} {i}', (x, Y0 + 3.0, (LEVELS[i + 1] if i + 1 < len(LEVELS) else ROOF) - .5), 45, 4.0)
    C.qa_room_light('Lobby', (0, Y0 + 4.0, LEVELS[1] - .6), 120, 5.0)
    C.box('Core', (0, 4.0, (G0 + ROOF) / 2), (7.0, 6.0, ROOF - G0), 'concrete', 'core', 0)
    zf = LEVELS[6]
    C.box('Party wall', (-5.0, Y0 + T + 3.0, zf + FH / 2), (.16, 6.0, FH - .3), 'interior', 'partitions', 0)
    A.sofa(-9.0, Y0 + 2.6, zf); A.desk(-12.0, Y0 + 2.2, zf); A.bed(-2.0, Y0 + 3.5, zf)
    C.box('Roof slab', (0, 0, ROOF - .15), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .3), 'floor', 'roof', 0)
    C.box('Roof membrane', (0, 0, ROOF + .01), (X1 - X0 - 2 * T - .02, Y1 - Y0 - 2 * T - .02, .02), 'membrane', 'roof', 0)
    # Water-tank house: brick with stone quoins and band, copper pyramid with seams, door.
    x0, x1, y0, y1 = TANK
    zt = ROOF + TANK_H
    for side, (f, span) in dict(south=(C.Face(((x0 + x1) / 2, y0, 0), (1, 0, 0), (0, 1, 0), 'tank south'), x1 - x0),
                                north=(C.Face(((x0 + x1) / 2, y1, 0), (-1, 0, 0), (0, -1, 0), 'tank north'), x1 - x0),
                                east=(C.Face((x1, (y0 + y1) / 2, 0), (0, 1, 0), (-1, 0, 0), 'tank east'), y1 - y0 - 2 * T),
                                west=(C.Face((x0, (y0 + y1) / 2, 0), (0, -1, 0), (1, 0, 0), 'tank west'), y1 - y0 - 2 * T)).items():
        holes = [hole(f'{f.label} door', 0, ROOF + .05, 1.1, 2.2, kind='door')] if side == 'south' else []
        holes += [hole(f'{f.label} window {j}', u_, ROOF + 4.2, .9, 1.6) for j, u_ in enumerate((-span / 4, span / 4))]
        f.wall(f.label + ' carrier', -span / 2, span / 2 - EPS, ROOF, zt, depth=T, holes=holes)
        G.brick_courses(f, -span / 2 + .02, span / 2 - .02, ROOF + .1, zt - .5, holes, spacing=.3)
        m = Merge(f)
        for h in holes:
            framed(m, f, h, cols=1, rows=1 if h.get('kind') == 'door' else 2, inset=.14, occupied='tank room', kind=h.get('kind', 'window'))
        m.box('stone', 0, -.06, zt - .25, span + .1, T + .14, .5)
        for k in range(int((TANK_H - .8) / .6)):
            L = .8 if k % 2 == 0 else .5
            z = ROOF + .35 + k * .6
            m.box('stone', -span / 2 + L / 2, -.04, z, L, .08, .5)
            m.box('stone', span / 2 - L / 2, -.04, z, L, .08, .5)
        m.flush('tank house')
    C.box('Tank house floor', ((x0 + x1) / 2, (y0 + y1) / 2, ROOF + TANK_H - .2), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .3), 'floor', 'tank house', 0)
    lower = [(x0 - .4, y0 - .4), (x1 + .4, y0 - .4), (x1 + .4, y1 + .4), (x0 - .4, y1 + .4)]
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    upper = [(cx - .05, cy - .05), (cx + .05, cy - .05), (cx + .05, cy + .05), (cx - .05, cy + .05)]
    strip('Tank house pyramid', lower, upper, zt, zt + 2.2, 'copper', 'tank house')
    apex = (cx, cy, zt + 2.2)
    for (ax, ay), (bx, by) in zip(lower, lower[1:] + lower[:1]):            # hips from the corners to the apex
        C.beam('Tank pyramid hip', (ax, ay, zt + .04), (apex[0], apex[1], apex[2] + .02), .1, .08, 'copper', 'tank house')
        L = math.hypot(bx - ax, by - ay); tx, ty = (bx - ax) / L, (by - ay) / L
        nx, ny = -ty, tx                                                   # inward normal of this eave (counter-clockwise loop)
        if (cx - ax) * nx + (cy - ay) * ny < 0:
            nx, ny = -nx, -ny
        hplan = (cx - ax) * nx + (cy - ay) * ny                            # eave to apex in plan
        for k in range(1, int(L / .6)):
            s_ = L * k / int(L / .6)
            px, py = ax + tx * s_, ay + ty * s_
            # The seam climbs straight up the face until it meets a hip line (corner to apex).
            reach = hplan * min(s_, L - s_) / (L / 2)
            if reach < .3:
                continue
            qx, qy = px + nx * (reach - .1), py + ny * (reach - .1)
            C.beam('Tank pyramid seam', (px, py, zt + .04), (qx, qy, zt + .04 + 2.2 * (reach - .1) / hplan), .04, .05, 'copper', 'tank house')
    # Grating catwalk round the tank house, plant units, chimneys with clay pots.
    for (a, b, c, d) in ((x0 - 2.2, x1 + 2.2, y0 - 2.2, y0 - .2), (x1 + .2, x1 + 2.2, y0 - .2, y1 + .2), (x0 - 2.2, x0 - .2, y0 - .2, y1 - 2.0)):
        C.box('Catwalk grating', ((a + b) / 2, (c + d) / 2, ROOF + .45), (b - a, d - c, .06), 'hardware', 'catwalk', 0)
        for (px, py) in ((a + .1, c + .1), (b - .1, c + .1), (a + .1, d - .1), (b - .1, d - .1)):
            C.box('Catwalk post', (px, py, ROOF + .23), (.08, .08, .44), 'hardware', 'catwalk', 0)
    for (ax, ay), (bx, by) in (((x0 - 2.2, y0 - 2.2), (x1 + 2.2, y0 - 2.2)), ((x1 + 2.2, y0 - 2.2), (x1 + 2.2, y1 + .2)), ((x0 - 2.2, y0 - 2.2), (x0 - 2.2, y1 - 2.0))):
        C.beam('Catwalk rail', (ax, ay, ROOF + 1.5), (bx, by, ROOF + 1.5), .05, .05, 'hardware', 'catwalk')
        C.beam('Catwalk rail mid', (ax, ay, ROOF + 1.0), (bx, by, ROOF + 1.0), .04, .04, 'hardware', 'catwalk')
        n = max(2, int(math.hypot(bx - ax, by - ay) / 1.6))
        for i in range(n + 1):
            x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
            C.beam('Catwalk stanchion', (x, y, ROOF + .48), (x, y, ROOF + 1.5), .05, .05, 'hardware', 'catwalk')
    for x, y, s in ((-3.2, 9.4, 1.4), (-.6, 9.4, 1.2), (2.0, 9.4, 1.4), (4.4, 9.4, 1.0)):
        C.box('Plant unit', (x, y, ROOF + s / 2), (2.2, 1.8, s), 'pale', 'roof plant', 0)
        C.rod('Plant fan', (x, y, ROOF + s), (x, y, ROOF + s + .08), .6, 'hardware', 'roof plant', 12)
    for x, y, w, d, hh, pots in ((-8.5, 11.2, 1.8, 1.0, 4.6, 3), (8.5, 11.2, 1.8, 1.0, 4.6, 3), (-8.5, -4.2, 1.0, 1.0, 4.0, 1)):
        C.box('Chimney stack', (x, y, ROOF + hh / 2), (w, d, hh), 'wall', 'chimneys', 0)
        C.box('Chimney cap', (x, y, ROOF + hh + .08), (w + .2, d + .2, .16), 'stone', 'chimneys', 0)
        for k in range(pots):
            px = x - (pots - 1) * .28 + k * .56
            C.rod('Chimney pot', (px, y, ROOF + hh + .16), (px, y, ROOF + hh + .75), .17, 'clay_pot', 'chimneys', 10)


def site():
    C.box('South sidewalk', (2.0, Y0 - 3.0, .07), (40.0, 6.0, .14), 'concrete', 'site', 0)
    C.box('East sidewalk', (X1 + 2.8, 0.5, .07), (5.6, Y1 - Y0 + 1.0, .14), 'concrete', 'site', 0)
    C.box('South street', (4.0, Y0 - 11.0, .01), (52.0, 10.0, .02), 'asphalt', 'site', 0)
    C.box('East street', (X1 + 10.6, 1.0, .01), (10.0, Y1 - Y0 + 2.0, .02), 'asphalt', 'site', 0)
    C.box('West lot', (X0 - 3.0, 0.5, .01), (6.0, Y1 - Y0 + 1.0, .02), 'concrete', 'site', 0)
    for x in (-12.0, 8.0):
        street_tree(x, Y0 - 3.4, z=.14, height=8.0, spread=2.0)
    street_tree(X1 + 4.0, 8.0, z=.14, height=8.0, spread=2.0)


def build():
    site()
    build_faces()
    floors_and_roof()
    C.CONTACTS.append(dict(name='Limestone base under brick storeys; cornice and balustrade on the parapet; tank house on the roof slab', roof_m=ROOF))


LIGHT_RIG = dict(key=(-50, -60, 70), fill=(60, -30, 50), rear=(-20, 60, 60), target=(0, 0, 20.0), gain=14.0)
