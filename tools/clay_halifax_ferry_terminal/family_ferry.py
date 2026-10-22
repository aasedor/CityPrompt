"""Halifax ferry terminal, authored from the locked catalogue views of
halifax_ferry_terminal / variant_0 (a contemporary glass and concrete ferry terminal on a downtown Halifax street).

Read from the pixels (the top view governs the plan): a long two-storey terminal, 20 m on the south street and 40.8 m
deep along a wide west street, between a brick heritage block on the east and the open west sidewalk (top, oblique).
The south front is a cantilevered glass box over the entrance: three tiers of clear glazing in a slim aluminium grid
between grey concrete end frames, a frosted top band and a projecting cap, over a deep canopy whose fascia carries
the lettering HALIFAX FERRY TERMINAL, with glazed storefronts and two pairs of glass doors below; the west third of
the south front is a lower glazed bay with its own canopy that wraps the corner (front, oblique, top). The west front
runs the long side: a projecting canopy over a glazed ground floor, glazed upper bays between three full-height
concrete fins, and on top of each fin a white box that cantilevers over the lawn strip (front, oblique, top); the
north end is a concrete wall with a few windows. The flat roof is a pale membrane in panels inside a gravel border
and a coped parapet, with a louvred mechanical enclosure holding an air-handling unit, three skylights, hatches and
vents (oblique, top). A three-storey brick heritage block with stone trim, round- and segment-headed windows, cast-iron
shopfronts, a bracketed cornice, a pedimented gable and a steep hipped clay-tile roof with chimneys adjoins on the east
(front, oblique, top); a parking court, a hipped brick wing and further brick blocks lie behind it. Concrete sidewalks
with a lawn strip and street trees on the west, tree pits and a tactile strip on the south, crossings at the corner,
low commercial blocks across the west street and the harbour with its piers beyond the blocks to the north (oblique).
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-halifax-ferry-terminal'
TX0, TX1, TY0, TY1 = -10.0, 10.0, -20.4, 20.4        # the terminal: 20 m south front, 40.8 m west front (top view)
T = .3                                                # concrete carrier depth
G0 = .15                                              # hall floor over the sidewalk
CAN0, CAN1 = 3.95, 4.35                               # wrapping canopy soffit and top
F1 = 4.6                                              # upper floor level
SPAND = 9.35                                          # upper glazing head / parapet band base
PARA = 10.0                                           # parapet top
ROOF = 9.45                                           # roof membrane top, inside the parapet
BOXX0 = -3.2                                          # the glass box spans x BOXX0..TX1 on the south front
BOXY = -21.0                                          # glass box face (cantilevered 0.6 m)
BOXTOP = 10.6                                         # glass box cap top
SIGNY = -21.9                                         # entrance canopy fascia (lettered)
SIGN0, SIGN1 = 3.75, 4.45
FINS = (-12.75, -2.6, 11.45)                          # west fins and roof boxes (y centres, top view)
NORTH_SOLID = 12.45                                   # west front is solid concrete north of fin 3
BX0, BX1, BY0, BY1 = 11.5, 40.5, -20.8, 4.0           # brick heritage block to the east (top view)
B_F2, B_F3, B_WALL, B_EAVE = 4.6, 8.0, 12.6, 12.7     # brick block floors, wall head (under the eaves), cornice top
TOP = 21.0
EPS = .002
PALETTE = dict(wall=(.70, .70, .68), concrete2=(.56, .56, .55), panel=(.80, .81, .81), frame=(.32, .34, .36),
    glass=(.14, .19, .22), spandrel=(.62, .68, .71), membrane=(.80, .81, .80), gravel=(.66, .62, .55), louvre=(.70, .71, .71),
    mech=(.84, .84, .82), sign=(.16, .18, .20), brick=(.50, .24, .16), joint=(.33, .27, .24), stone=(.70, .61, .47),
    iron=(.17, .22, .19), tile=(.55, .31, .21), timber=(.40, .26, .14), interior=(.80, .77, .70), floor=(.58, .56, .53),
    paving=(.68, .67, .64), asphalt=(.26, .26, .27), curb=(.74, .74, .72), lawn=(.33, .45, .22), soil=(.27, .21, .16),
    paint=(.90, .90, .88), yellow=(.84, .70, .22), redpave=(.56, .31, .25), water=(.24, .37, .45), hardware=(.08, .08, .08),
    planting=(.30, .43, .19), pot=(.62, .58, .52), cream=(.82, .78, .66), brick2=(.56, .32, .23), ctx=(.74, .72, .68))


def manifest(version):
    h = TOP
    cams = G.camera_roster(TX1 - TX0 + 4.0, TY1 - TY0 + 4.0, PARA, [
        ('entrance_canopy', (5.0, -30.5, 1.7), (5.0, -20.4, 3.0), 28),
        ('facade_close', (3.0, -28.5, 3.4), (3.0, SIGNY, 4.1), 40),
        ('glass_close', (-6.0, -34.0, 7.5), (3.5, BOXY, 7.2), 35),
        ('architecture_close', (-16.5, -27.0, 2.0), (-10.5, -5.0, 3.6), 30),
        ('roof_boxes', (-23.0, -18.0, 13.5), (-10.0, -7.0, 9.8), 30),
        ('roof_mechanical', (-14.0, -30.0, 22.0), (1.5, 1.0, 9.8), 32),
        ('interior', (6.5, -16.5, 1.7), (-5.0, -21.0, 3.0), 22),
        ('brick_neighbour', (22.0, -33.0, 7.0), (24.0, BY0, 8.0), 30),
        ('lawn_bench', (-15.5, -24.5, 1.7), (-11.5, -12.0, 1.4), 28),
        ('rear_north', (-15.0, 33.0, 10.0), (2.0, TY1, 5.5), 26)])
    for c in cams:                       # the locked front and oblique views are fitted to the source pixels
        c['whole'] = False
        if c['name'] == 'front':
            c.update(location=(-37.72, -36.79, 1.6), target=(12.63, -14.55, 7.17), lens=60.0)
        elif c['name'] == 'front_corner':
            c.update(location=(43.84, -97.7, 63.37), target=(4.13, -8.29, 4.27), lens=64.0)
        elif c['name'] == 'top':
            c.update(location=(8.4, -2.3, 150.0), target=(8.4, -2.299, 0.0), ortho_scale=71.3)
        elif c['name'] == 'aerial':
            c.update(location=(-62.0, 70.0, 58.0), target=(6.0, -4.0, 4.0), lens=40)
        elif c['name'] == 'left_side':
            c.update(location=(-33.0, 0.0, 12.0), target=(-10.0, 0.0, 5.0), lens=16)
        elif c['name'] == 'right_side':
            c.update(location=(32.0, 32.0, 24.0), target=(10.0, 11.0, 5.0), lens=30)
        elif c['name'] == 'rear':
            c.update(location=(0.0, 34.5, 4.5), target=(0.0, TY1, 5.0), lens=22)
        elif c['name'] == 'rear_side':
            c.update(location=(48.0, 58.0, 36.0), target=(6.0, 0.0, 5.0), lens=35)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='halifax_ferry_terminal/variant_0 (contemporary glass and concrete ferry terminal beside a brick heritage block)',
        measurement_contract=dict(dimensions_m=dict(width=TX1 - TX0, depth=TY1 - TY0, height=BOXTOP),
            observed_storeys=2, storey_programme='ground-floor concourse with ticketing and a cafe, upper-floor waiting lounge',
            plan='20 m by 40.8 m terminal (top view) on the corner of a south street and a wide west street; a brick heritage block adjoins on the east',
            facade='south front: cantilevered glass box (three tiers of clear glazing, frosted top band, aluminium cap) between concrete end frames over a lettered canopy and glazed storefronts with two pairs of glass doors; a lower glazed west bay with a canopy wrapping the corner; west front: canopy over a glazed ground floor, glazed upper bays between three full-height concrete fins carrying cantilevered white roof boxes, solid concrete north end',
            roof='flat membrane in panels inside a gravel border and a coped parapet; louvred mechanical enclosure with an air-handling unit; three skylights, hatches and vents',
            streetscape='concrete sidewalks, a lawn strip with a bench on the west front, street trees in pits, a tactile strip at the entrance, crossings at the corner, the harbour and piers beyond the blocks to the north',
            levels_m=[G0, F1, ROOF], roof_m=dict(parapet=PARA, box_cap=BOXTOP),
            inferred='interiors, the north and east walls and the context blocks follow the visible grammar; metric dimensions are authored teaching assumptions; the front view draws the south front wider than the top view allows, and the top view governs the plan'),
        roof_contract=dict(type='flat membrane roof inside a coped parapet; gravel border; louvred mechanical enclosure; skylights; cantilevered roof boxes on the west edge', datum_m=ROOF, crowns_m=[PARA, BOXTOP]),
        identity_contract=dict(owner='two-storey glass and concrete ferry terminal with a cantilevered glass box over a lettered entrance canopy, a long west front of glazed bays between concrete fins with white roof boxes, beside a three-storey brick heritage block'),
        material_contract=dict(profile='source-palette clay: light grey concrete, clear glass in a dark aluminium grid, frosted spandrel, pale membrane and gravel roof; red brick with buff stone trim and clay-tile roof next door', textured_keeper=False),
        programme_contract=dict(storeys=2, ground='concourse, ticketing, cafe', upper='waiting lounge and offices'),
        contact_contract=['Grade-zero sidewalks, lawn strips and streets', 'Concrete fins and frames from grade', 'Roof inside the parapet', 'Brick block walls from grade'],
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
# ---- Halifax ferry terminal ----

def cyl(b, role, cx, cy, z0, z1, r, n=12):
    """Upright n-gon shaft added to a Batch."""
    frustum(b, role, cx, cy, z0, z1, r, r, n)


def frustum(b, role, cx, cy, z0, z1, r0, r1, n=12):
    """Upright n-gon frustum (radius r0 at z0, r1 at z1) added to a Batch."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for z, r in ((z0, r0), (z1, max(r1, .001))):
        for i in range(n):
            a = 2 * math.pi * (i + .5) / n
            V.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    F.append(tuple(o + i for i in range(n - 1, -1, -1)))
    F.append(tuple(o + n + i for i in range(n)))
    for i in range(n):
        j = (i + 1) % n
        F.append((o + i, o + j, o + n + j, o + n + i))


def disc(b, role, centre, normal, r, t=.04, n=24):
    """Flat disc standing proud along a horizontal outward normal (an oculus or a fan)."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    nx, ny = normal
    tx, ty = -ny, nx
    for d in (0.0, t):
        for i in range(n):
            a = 2 * math.pi * i / n
            V.append((centre[0] + nx * d + tx * r * math.cos(a), centre[1] + ny * d + ty * r * math.cos(a), centre[2] + r * math.sin(a)))
    F.append(tuple(o + i for i in range(n)))
    F.append(tuple(o + n + i for i in range(n - 1, -1, -1)))
    for i in range(n):
        j = (i + 1) % n
        F.append((o + i, o + j, o + n + j, o + n + i))


def hdisc(b, role, cx, cy, z, r, t=.02, n=20):
    """Flat horizontal disc (a fan or a drain) lying on a surface, its underside 5 mm below it."""
    frustum(b, role, cx, cy, z - .005, z + t, r, r, n)


def arch_head(f, h, rise, ring=.2, segs=10, ring_role='stone', wall_role='brick', dep=.45):
    """Round or segmental head on a rectangular cut: wall infill above the curve (1 cm inside both faces, so it never
    shares a plane with the carrier) and a proud stone hood ring over it."""
    u, w, top = h['u'], h['w'], h['z'] + h['h']
    R = (w * w / 4 + rise * rise) / (2 * rise)
    cz = top - R
    a0 = math.asin(min(1.0, (w / 2) / R))
    arc = [(u + R * math.sin(-a0 + 2 * a0 * i / segs), cz + R * math.cos(-a0 + 2 * a0 * i / segs)) for i in range(segs + 1)]
    pts = [(u - w / 2 - .06, top - rise)] + arc + [(u + w / 2 + .06, top - rise)]
    vs, fs = [], []
    for (pu, pz) in pts:
        for d in (.01, dep - .01):
            vs.append(f.p(pu, d, pz)); vs.append(f.p(pu, d, top + .06))
    for i in range(len(pts) - 1):
        a, b = 4 * i, 4 * (i + 1)
        fs += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3)]
    n = 4 * (len(pts) - 1)
    fs += [(0, 1, 3, 2), (n, n + 2, n + 3, n + 1)]
    C.mesh(f'{h["id"]} head infill', vs, fs, wall_role, 'arches')
    vs, fs = [], []
    for (pu, pz) in arc:
        r = math.hypot(pu - u, pz - cz)
        nu, nz = (pu - u) / r, (pz - cz) / r
        for d in (-.07, .02):
            vs.append(f.p(pu, d, pz)); vs.append(f.p(pu + nu * ring, d, pz + nz * ring))
    for i in range(segs):
        a, b = 4 * i, 4 * (i + 1)
        fs += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3)]
    n = 4 * segs
    fs += [(0, 1, 3, 2), (n, n + 2, n + 3, n + 1)]
    C.mesh(f'{h["id"]} hood', vs, fs, ring_role, 'arches')
    return cz, R


FONT = {
    'A': ('.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'),
    'E': ('#####', '#....', '#....', '####.', '#....', '#....', '#####'),
    'F': ('#####', '#....', '#....', '####.', '#....', '#....', '#....'),
    'H': ('#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'),
    'I': ('.###.', '..#..', '..#..', '..#..', '..#..', '..#..', '.###.'),
    'L': ('#....', '#....', '#....', '#....', '#....', '#....', '#####'),
    'M': ('#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'),
    'N': ('#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#', '#...#'),
    'R': ('####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'),
    'T': ('#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'),
    'X': ('#...#', '#...#', '.#.#.', '..#..', '.#.#.', '#...#', '#...#'),
    'Y': ('#...#', '#...#', '.#.#.', '..#..', '..#..', '..#..', '..#..'),
    'C': ('.####', '#....', '#....', '#....', '#....', '#....', '.####'),
    'O': ('.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'),
    'S': ('.####', '#....', '#....', '.###.', '....#', '....#', '####.'),
    'P': ('####.', '#...#', '#...#', '####.', '#....', '#....', '#....'),
    'K': ('#...#', '#..#.', '#.#..', '##...', '#.#..', '#..#.', '#...#'),
    'B': ('####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'),
    'D': ('####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'),
    'U': ('#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.')}


def letters(m, text, u0, u1, zc, hgt, d, role='sign'):
    """Lettering in a 5 x 7 block face: each glyph row merged into runs of raised strokes, centred in u0..u1 at zc."""
    px = min(hgt / 7, (u1 - u0) / (len(text) * 6 - 1))
    start = (u0 + u1) / 2 - (len(text) * 6 - 1) * px / 2
    for i, ch in enumerate(text):
        rows = FONT.get(ch)
        if not rows:
            continue
        for r, row in enumerate(rows):
            z = zc + 3 * px - r * px
            c = 0
            while c < 5:
                if row[c] != '#':
                    c += 1
                    continue
                e = c
                while e < 5 and row[e] == '#':
                    e += 1
                m.box(role, start + (i * 6 + (c + e) / 2) * px, d, z, (e - c) * px, .03, px * 1.02)
                c = e


def windows_grid(m, lo, hi, z0, z1, floors, per, w=1.1, hh=1.9, role='frame', frame='paint'):
    """Windows on a solid face (Merge in face coordinates): a surround standing 15 cm proud (jambs, head, sill, all
    lapping 1 cm into the wall) makes the reveal; inside it a lit room plate on the wall, a transmissive pane and a sash
    with a meeting rail, each layer at its own depth so no two faces share a plane."""
    n = max(1, int((hi - lo) / per))
    for k in range(n):
        u = lo + (hi - lo) * (k + .5) / n
        for j in range(floors):
            z = z0 + (z1 - z0) * j / floors + .9
            zc = z + hh / 2
            m.box('interior', u, -.009, zc, w - .02, .01, hh - .02)                       # lit room plate
            for s in (-1, 1):
                m.box(frame, u + s * (w / 2 + .05), -.07, zc, .1, .16, hh + .2)          # jambs
            m.box(frame, u, -.075, z + hh + .06, w + .24, .17, .12)                         # head
            m.box(frame, u, -.09, z - .08, w + .3, .2, .08)                                 # sill
            m.box('glass', u, -.05, zc, w - .02, .008, hh - .02)
            for s in (-1, 1):
                m.box(role, u + s * (w / 2 - .025), -.07, zc, .06, .03, hh - .01)           # sash stiles
            for zr in (z + .03, z + hh - .035, zc):
                m.box(role, u, -.07, zr, w - .1, .03, .05)                                   # rails and meeting rail
            if w > 1.0:
                m.box(role, u, -.072, zc, .04, .026, hh - .06)                               # centre muntin


def curtain(b, axis, c, lo, hi, z0, z1, per, transoms=(), face=0.0, out=-1, pane=.06, mull=.07, depth=.16, glass='glass'):
    """Stick curtain wall in a vertical plane: axis 'x' means the plane y = c (running along x), 'y' the plane x = c.
    Mullions and transoms project `depth` outward (direction `out`) from the plane; the single pane sits `pane` behind it."""
    n = max(1, round((hi - lo) / per))
    pc = c - out * pane

    def put(role, s0, s1, za, zb, d0, d1):
        sm, sw = (s0 + s1) / 2, s1 - s0
        dm, dw = (d0 + d1) / 2, abs(d1 - d0)
        if axis == 'x':
            b.box(role, sm, dm, (za + zb) / 2, sw, dw, zb - za)
        else:
            b.box(role, dm, sm, (za + zb) / 2, dw, sw, zb - za)
    put(glass, lo, hi, z0, z1, pc - .006, pc + .006)
    for k in range(n + 1):
        s = lo + (hi - lo) * k / n
        put('frame', s - mull / 2, s + mull / 2, z0, z1, c + out * depth, c - out * (pane + .03))
    for zt in (z0 + mull / 2,) + tuple(transoms) + (z1 - mull / 2,):
        put('frame', lo, hi, zt - mull / 2, zt + mull / 2, c + out * (depth - .02), c - out * (pane + .025))


def door_leaf(b, axis, c, s, lw, z0, z1, out=-1):
    """Glazed aluminium door leaf in a vertical plane (axis as in curtain): stiles, top and bottom rails 6 cm deep, a pane
    held inside them and a pull on the outer side; the pane is embedded in the frame so no edge is open."""
    def put(role, s0, s1, za, zb, d0, d1):
        sm, sw = (s0 + s1) / 2, s1 - s0
        dm, dw = (d0 + d1) / 2, abs(d1 - d0)
        if axis == 'x':
            b.box(role, sm, dm, (za + zb) / 2, sw, dw, zb - za)
        else:
            b.box(role, dm, sm, (za + zb) / 2, dw, sw, zb - za)
    a0, a1 = s - lw / 2, s + lw / 2
    for e0, e1 in ((a0, a0 + .1), (a1 - .1, a1)):
        put('frame', e0, e1, z0, z1, c - .03, c + .03)
    put('frame', a0 + .08, a1 - .08, z1 - .1, z1, c - .03, c + .03)
    put('frame', a0 + .08, a1 - .08, z0, z0 + .25, c - .03, c + .03)
    put('glass', a0 + .09, a1 - .09, z0 + .24, z1 - .09, c - .005, c + .005)
    return put


def band(m, lo, hi, z0, z1, proj, role='stone'):
    """Horizontal member proud of a face: front at -proj, back 1 cm inside the wall (never on the face plane)."""
    m.box(role, (lo + hi) / 2, (-proj + .01) / 2, (z0 + z1) / 2, hi - lo, proj + .01, z1 - z0)


def qa_light(name, loc, power, size):
    """Neutral inspection light that illuminates the rooms but is hidden from camera and glossy rays (no glowing
    disks seen through the glazing)."""
    obj = C.qa_room_light(name, loc, power, size)
    obj.visible_camera = False
    obj.visible_glossy = False
    return obj


TS = C.Face((0, TY0, 0), (1, 0, 0), (0, 1, 0), 'terminal south front')
TW = C.Face((TX0, 0, 0), (0, -1, 0), (1, 0, 0), 'terminal west front')
TN = C.Face((0, TY1, 0), (-1, 0, 0), (0, -1, 0), 'terminal north wall')
TE = C.Face((TX1, 0, 0), (0, 1, 0), (-1, 0, 0), 'terminal east wall')
BS = C.Face((0, BY0, 0), (1, 0, 0), (0, 1, 0), 'brick block south front')


def terminal_frame():
    """Slabs, the corner pier, west fins, parapet bands, copings and the solid north end walls."""
    b = Batch()
    b.box('concrete2', 0.0, 0.0, G0 / 2, TX1 - TX0, TY1 - TY0, G0)                               # hall slab
    b.box('interior', 0.0, 0.0, F1 - .15, TX1 - TX0 - .5, TY1 - TY0 - .5, .3)                     # upper floor slab (pale soffit)
    b.box('interior', 0.0, 0.0, ROOF - .3, TX1 - TX0 - .4, TY1 - TY0 - .4, .42)                   # roof slab (ceiling)
    # SW corner pier and the three full-height west fins under the roof boxes.
    b.box('wall', TX0 + .25, TY0 + .2, PARA / 2, .9, .8, PARA)
    for yc in FINS:
        b.box('wall', TX0 - .1, yc, 9.0 / 2, .95, 2.0, 9.0)
    # Floor bands (slab edges) and parapet bands over the glazed fronts.
    for y0, y1 in ((TY0 + .6, FINS[0] - 1.0), (FINS[0] + 1.0, FINS[1] - 1.0), (FINS[1] + 1.0, FINS[2] - 1.0)):
        b.box('panel', TX0 + .1, (y0 + y1) / 2, (4.3 + 4.76) / 2, .32, y1 - y0, .46)
    b.box('panel', TX0 + .1, (TY0 + .6 + NORTH_SOLID) / 2, (SPAND - .01 + PARA) / 2, .32, NORTH_SOLID - TY0 - .6 + .02, PARA - SPAND + .01)
    b.box('panel', (TX0 + .65 + BOXX0 - .45) / 2, TY0 + .1, (4.3 + 4.76) / 2, BOXX0 - .45 - TX0 - .65, .32, .46)
    b.box('panel', (TX0 + .65 + BOXX0 - .45) / 2, TY0 + .1, (SPAND - .01 + PARA) / 2, BOXX0 - .45 - TX0 - .65, .32, PARA - SPAND + .01)
    # Parapet walls behind the bands and on the solid ends (inner faces 1 cm off the band backs).
    b.box('wall', (TX0 + BOXX0) / 2, TY0 + .44, (ROOF - .4 + PARA) / 2, BOXX0 - TX0 - .9, .3, PARA - ROOF + .4)
    b.box('wall', TX0 + .44, (TY0 + .7 + NORTH_SOLID) / 2, (ROOF - .4 + PARA) / 2, .3, NORTH_SOLID - TY0 - .7, PARA - ROOF + .4)
    # Copings: the south leg up to the glass box, the west leg, the north and east legs on the solid walls.
    b.box('panel', (TX0 - .06 + BOXX0 - .6) / 2, TY0 + .2, PARA + .03, BOXX0 - .6 - TX0 + .06, .62, .06)
    b.box('panel', TX0 + .25, (TY0 + .51 + TY1 + .06) / 2, PARA + .031, .62, TY1 - TY0 - .45, .062)
    b.box('panel', (TX0 + .56 + TX1 + .06) / 2, TY1 - .2, PARA + .032, TX1 - TX0 - .5, .52, .064)
    b.box('panel', TX1 - .2, (BOXY + 3.2 + TY1 - .46) / 2, PARA + .033, .52, TY1 - .46 - BOXY - 3.2, .066)
    # Hidden east wall behind the infill strip.
    b.box('wall', TX1 - .15, (TY0 + .4 + 3.8) / 2, PARA / 2, .3, 3.8 - TY0 - .4, PARA - .01)
    b.flush('terminal frame')


def canopies():
    """The canopy that wraps the SW corner and runs the west front, and the lettered entrance canopy under the box."""
    pts = [(TX0 - 1.4, NORTH_SOLID + .05), (TX0 - 1.4, TY0 - 1.4), (BOXX0 - .45, TY0 - 1.4), (BOXX0 - .45, TY0 + .06),
           (TX0 + .06, TY0 + .06), (TX0 + .06, NORTH_SOLID + .05)]
    C.prism('Wrapping canopy', pts, 'z', CAN0, CAN1, 'panel', 'canopies')
    b = Batch()
    for x0, x1, y0, y1 in ((TX0 - 1.42, TX0 - 1.3, TY0 - 1.42, NORTH_SOLID + .05), (TX0 - 1.3, BOXX0 - .45, TY0 - 1.42, TY0 - 1.3)):
        b.box('frame', (x0 + x1) / 2, (y0 + y1) / 2, CAN0 + .05, x1 - x0, y1 - y0, .12)            # drip edge under the fascia
    # Entrance canopy: a deeper slab with a lettered fascia, from the box frame to the brick block.
    b.box('panel', (-2.6 + 9.7) / 2, (SIGNY + TY0 + .05) / 2, (SIGN0 + SIGN1) / 2, 12.3, TY0 + .05 - SIGNY, SIGN1 - SIGN0)
    b.box('frame', (-2.6 + 9.7) / 2, SIGNY + .5, SIGN0 - .03, 12.1, .3, .07)
    b.flush('canopies')
    m = Merge(C.Face((0, SIGNY, 0), (1, 0, 0), (0, 1, 0), 'entrance canopy fascia'))
    letters(m, 'HALIFAX FERRY TERMINAL', -1.6, 8.8, (SIGN0 + SIGN1) / 2, .44, -.01, 'sign')
    m.flush('entrance canopy fascia')


def south_front():
    """The lower west bay and the cantilevered glass box with its concrete end frames, frosted band and cap."""
    b = Batch()
    # West bay: storefront under the canopy, clear upper glazing over the floor band.
    curtain(b, 'x', TY0 + .32, TX0 + .7, BOXX0 - .5, G0, CAN0 - .06, 1.55, transoms=(3.05,), out=-1, depth=.1)
    curtain(b, 'x', TY0 + .02, TX0 + .7, BOXX0 - .5, 4.75, SPAND, 1.6, transoms=(7.05,), out=-1, depth=.12)
    b.box('panel', (TX0 + .7 + BOXX0 - .5) / 2, TY0 + .38, (CAN0 - .07 + 4.3) / 2, BOXX0 - .5 - TX0 - .7, .1, 4.3 - CAN0 + .07)
    # Glass box: concrete end frames to grade, soffit, three tiers of clear glazing, frosted band and the cap.
    for x0, x1 in ((BOXX0 - .5, BOXX0 + .1), (TX1 - .6, TX1)):
        b.box('wall', (x0 + x1) / 2, (BOXY - .1 + TY0 + .4) / 2, (BOXTOP - .03) / 2, x1 - x0, TY0 + .4 - BOXY + .1, BOXTOP - .03)
    b.box('panel', (BOXX0 + .1 + TX1 - .6) / 2, (BOXY - .16 + TY0 + .3) / 2, 4.51, TX1 - .6 - BOXX0 - .1 + .02, TY0 + .3 - BOXY + .16, .22)
    curtain(b, 'x', BOXY + .02, BOXX0 + .1, TX1 - .6, 4.62, 8.9, 2.5, transoms=(6.05, 7.45), out=-1, depth=.14)
    curtain(b, 'x', BOXY + .02, BOXX0 + .1, TX1 - .6, 8.9, 9.95, 2.5, out=-1, depth=.1, glass='spandrel')
    b.box('panel', (BOXX0 - .55 + TX1 + .03) / 2, (BOXY - .14 + TY0 + .2) / 2, (9.95 + BOXTOP) / 2, TX1 + .03 - BOXX0 + .55, TY0 + .2 - BOXY + .14, BOXTOP - 9.95)
    b.box('panel', (BOXX0 - .55 + TX1 + .03) / 2, (TY0 + .2 + TY0 + 3.2) / 2, (ROOF - .05 + BOXTOP) / 2, TX1 + .03 - BOXX0 + .55, 3.0, BOXTOP - ROOF + .05)
    b.box('frame', (BOXX0 - .55 + TX1) / 2, BOXY - .15, 9.97, TX1 - BOXX0 + .53, .04, .05)              # shadow line under the cap
    # Storefront under the entrance canopy, with two pairs of glass doors.
    sx0, sx1 = BOXX0 + .1, TX1 - .6
    gy = TY0 + .3
    pieces = [(sx0, 3.0), (7.4, sx1)]
    for a, c in pieces:
        curtain(b, 'x', gy, a, c, G0, SIGN0 - .05, 1.5, transoms=(3.05,), out=-1, depth=.1)
    for dc in (4.1, 6.3):
        for s in (-1, 1):
            door_leaf(b, 'x', gy, dc + s * .525, 1.05, G0, 2.74)
            b.box('hardware', dc + s * .1, gy - .08, 1.2, .04, .04, .9)
    b.box('frame', 5.2, gy, (G0 + 2.86) / 2, .1, .14, 2.86 - G0)                                     # centre post
    b.box('frame', 5.2, gy, 2.8, 4.24, .12, .1)                                                       # transom, inside the mullions
    b.box('glass', 5.2, gy, (2.85 + SIGN0 - .1) / 2, 4.2, .01, SIGN0 - .1 - 2.85)
    b.box('frame', 3.05, gy, (G0 + SIGN0) / 2, .1, .14, SIGN0 - G0)
    b.box('frame', 7.35, gy, (G0 + SIGN0) / 2, .1, .14, SIGN0 - G0)
    b.box('panel', (sx0 + sx1) / 2, gy + .08, (SIGN0 - .06 + 4.45) / 2, sx1 - sx0, .1, 4.45 - SIGN0 + .06)
    b.box('concrete2', 5.2, TY0 - .3, .075, 3.4, .6, .15)                                             # entrance threshold
    b.flush('south front')


def west_front():
    """Long west front: glazed ground floor under the canopy, glazed upper bays between the fins, a pair of doors,
    and the solid concrete north end with punched windows."""
    b = Batch()
    bays = ((TY0 + .6, FINS[0] - 1.0), (FINS[0] + 1.0, FINS[1] - 1.0), (FINS[1] + 1.0, FINS[2] - 1.0))
    for y0, y1 in bays:
        curtain(b, 'y', TX0 + .02, y0, y1, 4.75, SPAND, 1.6, transoms=(7.05,), out=-1, depth=.12)
        if y0 < -9.0 < y1 - 2.0:
            continue
        curtain(b, 'y', TX0 + .3, y0, y1, G0, CAN0 - .06, 1.55, transoms=(3.05,), out=-1, depth=.1)
        b.box('panel', TX0 + .36, (y0 + y1) / 2, (CAN0 - .07 + 4.3) / 2, .1, y1 - y0, 4.3 - CAN0 + .07)
    # Bay 2 holds a pair of doors in its storefront.
    y0, y1 = bays[1]
    for a, c in ((y0, -9.9), (-8.1, y1)):
        curtain(b, 'y', TX0 + .3, a, c, G0, CAN0 - .06, 1.55, transoms=(3.05,), out=-1, depth=.1)
    b.box('panel', TX0 + .36, (y0 + y1) / 2, (CAN0 - .07 + 4.3) / 2, .1, y1 - y0, 4.3 - CAN0 + .07)
    for s in (-1, 1):
        door_leaf(b, 'y', TX0 + .3, -9.0 + s * .45, .9, G0, 2.74)
        b.box('hardware', TX0 + .2, -9.0 + s * .1, 1.2, .04, .04, .9)
    b.box('frame', TX0 + .3, -9.0, 2.8, .12, 1.86, .1)                                               # transom, inside the posts
    b.box('glass', TX0 + .3, -9.0, (2.85 + CAN0 - .1) / 2, .01, 1.82, CAN0 - .1 - 2.85)
    for y in (-9.95, -8.05):
        b.box('frame', TX0 + .3, y, (G0 + CAN0) / 2, .14, .1, CAN0 - G0)
    b.flush('west front glazing')
    # Solid north end of the west front, the north wall and the exposed east wall: concrete carriers with windows.
    for f, u0, u1, holes, label in (
            (TW, -TY1 + .28, -NORTH_SOLID, [hole('W n door', -17.6, G0 + .01, 1.1, 2.3, kind='door'), hole('W n g1', -14.6, 1.2, 1.6, 2.0),
                                            hole('W n u1', -17.6, 5.9, 1.6, 2.4), hole('W n u2', -14.6, 5.9, 1.6, 2.4)], 'west north end'),
            (TN, -TX1 + .01, -TX0 - .01, [hole(f'N u{k}', -8.0 + 4.0 * k, 5.9, 1.8, 2.4) for k in range(5)] +
                                         [hole('N load', 5.0, G0 + .01, 3.2, 3.3, kind='door'), hole('N door', -1.0, G0 + .01, 1.1, 2.3, kind='door'),
                                          hole('N g1', -6.0, 1.2, 1.8, 2.0)], 'north wall'),
            (TE, 3.8, TY1 - .28, [hole(f'E u{k}', 6.4 + 4.0 * k, 5.9, 1.8, 2.4) for k in range(4)] +
                                 [hole('E door', 16.6, G0 + .01, 1.1, 2.3, kind='door'), hole('E g1', 8.4, 1.2, 1.8, 2.0)], 'east wall')):
        f.wall(label + ' carrier', u0, u1, 0.0, PARA, depth=T, role='wall', holes=holes)
        m = Merge(f)
        for h in holes:
            if h.get('kind') == 'door':
                u, top = h['u'], h['z'] + h['h']
                z0 = h['z']
                m.box('frame', u, T - .12, (z0 + top) / 2, h['w'] - .02, .06, top - z0 - .005)
                m.box('sign' if h['w'] > 2 else 'panel', u, T - .15, (z0 + top) / 2 - .01, h['w'] - .16, .04, top - z0 - .03)
                if h['w'] > 2:
                    for k in range(1, 8):
                        m.box('frame', u, T - .175, G0 + (top - G0) * k / 8, h['w'] - .2, .02, .03)
                m.box('hardware', u + h['w'] * .3, T - .19, 1.1, .04, .04, .15)
                register(f, h, T - .15, 'door', 'service room')
            else:
                framed(m, f, h, cols=2, rows=1, inset=.16, occupied='office', frame='frame')
                m.box('panel', h['u'], -.04, h['z'] - .06, h['w'] + .1, .1, .07)
        m.flush(label)


def roof():
    """Membrane in panels inside a gravel border; louvred mechanical enclosure with an AHU; skylights, hatches, vents;
    the white roof boxes over the west fins."""
    b = Batch()
    xi0, xi1, yi0, yi1 = TX0 + .5, TX1 - .25, TY0 + .5, TY1 - .25
    b.box('concrete2', (xi0 + xi1) / 2, (yi0 + yi1) / 2, ROOF - .09, xi1 - xi0, yi1 - yi0, .1)        # deck under membrane
    mx0, mx1, my0, my1 = -6.7, 7.6, -17.6, 19.0
    b.box('membrane', (mx0 + mx1) / 2, (my0 + my1) / 2, ROOF - .02, mx1 - mx0, my1 - my0, .04)
    for x0, x1, y0, y1 in ((xi0, xi1, yi0, my0), (xi0, xi1, my1, yi1), (xi0, mx0, my0, my1), (mx1, xi1, my0, my1)):
        b.box('gravel', (x0 + x1) / 2, (y0 + y1) / 2, ROOF - .005, x1 - x0, y1 - y0, .07)
    for k in range(1, 9):                                                                             # membrane seams
        b.box('concrete2', mx0 + (mx1 - mx0) * k / 9, (my0 + my1) / 2, ROOF + .001, .05, my1 - my0 - .1, .006)
    for k in range(1, 7):
        b.box('concrete2', (mx0 + mx1) / 2, my0 + (my1 - my0) * k / 7, ROOF + .0015, mx1 - mx0 - .1, .05, .006)
    # Mechanical enclosure: a ribbed screen on four sides around an air-handling unit, pipes and a duct.
    ex0, ex1, ey0, ey1, eh = -3.1, 6.1, -3.0, 10.4, 2.7
    for x0, x1, y0, y1 in ((ex0, ex1, ey0, ey0 + .12), (ex0, ex1, ey1 - .12, ey1), (ex0, ex0 + .12, ey0 + .12, ey1 - .12), (ex1 - .12, ex1, ey0 + .12, ey1 - .12)):
        b.box('louvre', (x0 + x1) / 2, (y0 + y1) / 2, ROOF + eh / 2, x1 - x0, y1 - y0, eh)
    for k in range(int((ex1 - ex0) / .5) + 1):
        x = ex0 + .1 + k * .5
        if x < ex1 - .05:
            b.box('louvre', x, ey0 - .03, ROOF + eh / 2, .08, .08, eh - .02)
    for k in range(int((ey1 - ey0) / .5) + 1):
        y = ey0 + .1 + k * .5
        if y < ey1 - .05:
            b.box('louvre', ex0 - .03, y, ROOF + eh / 2, .08, .08, eh - .02)
            b.box('louvre', ex1 + .03, y, ROOF + eh / 2, .08, .08, eh - .02)
    b.box('frame', (ex0 + ex1) / 2, ey0 + .06, ROOF + eh + .03, ex1 - ex0 + .02, .16, .06)
    b.box('frame', ex0 + .06, (ey0 + ey1) / 2, ROOF + eh + .035, .16, ey1 - ey0 - .2, .06)
    b.box('frame', ex1 - .06, (ey0 + ey1) / 2, ROOF + eh + .04, .16, ey1 - ey0 - .2, .06)
    b.box('frame', (ex0 + ex1) / 2, ey1 - .06, ROOF + eh + .045, ex1 - ex0 - .2, .16, .06)
    b.box('mech', 1.1, 3.65, ROOF + .95, 3.6, 6.9, 1.9)
    for y in (5.8, 4.6, 3.4):
        hdisc(b, 'hardware', .4, y, ROOF + 1.9, .5)
        b.box('frame', .4, y, ROOF + 1.925, 1.0, .06, .03)
    for x, y, w, d, hgt in ((3.6, 2.0, 1.2, 2.6, 1.1), (4.6, 6.6, 1.4, 1.2, .9), (3.9, -1.6, .8, .8, 1.3)):
        b.box('mech', x, y, ROOF + hgt / 2, w, d, hgt)
    b.beam('hardware', (3.0, 7.4, ROOF + 1.2), (3.0, 9.9, ROOF + 1.2), .18)
    b.beam('hardware', (3.6, 7.4, ROOF + .7), (3.6, 9.9, ROOF + .7), .14)
    b.beam('hardware', (2.95, 1.6, ROOF + .55), (2.95, -2.6, ROOF + .55), .12)
    # Skylights: upstand curbs with glazed hipped lights.
    for x0, x1, y0, y1 in ((4.8, 7.2, -6.6, -4.7), (4.8, 7.2, -10.7, -8.6), (1.1, 3.6, -12.6, -10.7)):
        b.box('panel', (x0 + x1) / 2, (y0 + y1) / 2, ROOF + .2, x1 - x0, y1 - y0, .4)
        b.box('frame', (x0 + x1) / 2, (y0 + y1) / 2, ROOF + .43, x1 - x0 - .1, y1 - y0 - .1, .06)
    b.flush('roof')
    for k, (x0, x1, y0, y1) in enumerate(((4.8, 7.2, -6.6, -4.7), (4.8, 7.2, -10.7, -8.6), (1.1, 3.6, -12.6, -10.7))):
        pitched_roof(f'Skylight {k}', x0 + .12, x1 - .12, y0 + .12, y1 - .12, ROOF + .46, .45, True, True,
                     'x' if x1 - x0 >= y1 - y0 else 'y', .0, 'spandrel', 'roof skylights')
    b = Batch()
    for x, y in ((-1.2, -6.0), (2.0, 13.0), (-4.6, 15.6)):                                         # hatches
        b.box('panel', x, y, ROOF + .3, 1.2, 1.0, .6)
        b.box('frame', x, y, ROOF + .62, 1.26, 1.06, .05)
    for x, y in ((-2.0, -12.0), (-5.2, 2.0), (6.6, 14.0), (-1.5, 17.5), (2.6, -15.8), (-5.4, -9.4)):
        cyl(b, 'frame', x, y, ROOF - .02, ROOF + .55, .09, 8)
        cyl(b, 'frame', x, y, ROOF + .55, ROOF + .62, .14, 8)
    for x, y in ((-3.0, -16.4), (6.3, -16.4), (-3.0, 18.2), (6.3, 18.2), (1.5, 0.5)):
        hdisc(b, 'hardware', x, y, ROOF, .12, t=.01, n=10)
    # Roof boxes over the west fins: white rendered hoods cantilevered past the west front.
    for yc in FINS:
        b.box('paint', -10.2, yc, (8.85 + 11.15) / 2, 5.0, 3.3, 11.15 - 8.85)
        b.box('cream', -10.2, yc, 11.17, 4.4, 2.7, .06)
        b.box('frame', -12.71, yc, 9.0, .04, 3.0, .08)
    b.flush('roof furniture')


def interiors():
    """Concourse, west hall and upper lounge behind the glazing: partitions, a ticket counter, benches, a stair and
    lounge seating, lit by neutral inspection lights."""
    b = Batch()
    for x0, x1, y0, y1, z0, z1 in ((-3.0, 9.7, -8.0, -7.8, G0, F1 - .3), (-3.2, -3.0, -8.0, NORTH_SOLID, G0, F1 - .3),
                                   (-2.2, -2.0, -14.0, NORTH_SOLID, F1, ROOF - .5), (-2.0, 9.7, -14.2, -14.0, F1, ROOF - .5),
                                   (-9.7, -3.2, NORTH_SOLID, NORTH_SOLID + .2, G0, ROOF - .5),
                                   (7.3, 7.5, 3.8, 19.9, G0, ROOF - .5), (-9.7, 7.3, 17.6, 17.8, G0, ROOF - .5)):
        b.box('interior', (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, x1 - x0, y1 - y0, z1 - z0)
    b.box('timber', 3.0, -8.9, .6 + G0, 6.0, .8, 1.1)                                                 # ticket counter
    b.box('panel', 3.0, -8.9, 1.22 + G0, 6.2, .9, .06)
    b.box('sign', 3.0, -7.75, 3.0, 4.0, .06, .7)                                                        # departures board
    for x in (-1.0, 1.4, 3.8, 6.2):                                                                   # benches
        for y in (-17.0, -14.5, -12.0):
            b.box('timber', x, y, .45 + G0, 1.9, .5, .08)
            b.box('timber', x, y + .22, .75 + G0, 1.9, .06, .55)
            b.box('hardware', x, y, .22 + G0, 1.7, .08, .44)
    for k in range(24):                                                                               # stair to the lounge
        y = -17.9 + k * .3
        z = G0 + (k + 1) * (F1 - G0) / 24
        b.box('floor', -6.2, y + .15, z - .09, 1.6, .3, .18)
    b.beam('hardware', (-7.05, -17.9, G0 + 1.0), (-7.05, -10.7, F1 + 1.0), .05)
    b.beam('hardware', (-5.35, -17.9, G0 + 1.0), (-5.35, -10.7, F1 + 1.0), .05)
    b.box('interior', -6.2, -10.0, (F1 - .3 + F1) / 2, 1.8, 1.4, .3)
    for x in (-7.8, -5.8, -3.8):                                                                      # west hall cafe tables
        for y in (-4.0, 0.0, 4.0, 8.0):
            cyl(b, 'timber', x, y, G0 + .72, G0 + .76, .4, 10)
            cyl(b, 'hardware', x, y, G0, G0 + .72, .04, 6)
    for x in (-6.5, -4.0):                                                                            # lounge seating rows
        for y in (-8.0, -3.0, 2.0, 7.0):
            b.box('timber', x, y, F1 + .45, .5, 3.2, .1)
            b.box('timber', x - .22, y, F1 + .75, .06, 3.2, .55)
    for x in (0.0, 3.0, 6.0):
        b.box('timber', x, -18.5, F1 + .45, 2.4, .5, .1)
        b.box('timber', x, -18.28, F1 + .75, 2.4, .06, .55)
    b.flush('interiors')
    for name, loc in (('concourse', (3.0, -14.0, 4.2)), ('west hall', (-6.0, 2.0, 4.2)), ('lounge south', (3.5, -16.0, 8.85)),
                      ('lounge west', (-6.0, -4.0, 8.85)), ('lounge north', (-6.0, 8.0, 8.85)),
                      ('east offices', (8.6, 12.0, 8.85)), ('east stores', (8.6, 12.0, 4.2)), ('north offices', (0.0, 18.95, 8.85)),
                      ('north stores', (0.0, 18.95, 4.2))):
        small = 'east' in name or 'north' in name
        qa_light(name, loc, 60 if small else 140, 1.2 if small else 3.0)
    for k, (x, y) in enumerate(((-8.4, -15.5), (-8.4, -6.5), (-8.4, 5.0), (-6.5, -18.8), (1.5, -18.8), (7.0, -18.8))):
        qa_light(f'facade {k}', (x, y, 4.2), 70, 1.5)
    C.CONTACTS.append(dict(name='Concrete fins and frames from grade; roof inside the parapet; glass box on its concrete frames', parapet_m=PARA))


def brick_shopfront(m, f, h, door):
    """Cast-iron shopfront in a cut: bulkhead, plate glass with mullions, a small-paned transom, a recessed door."""
    u, w, z0, top = h['u'], h['w'], h['z'], h['z'] + h['h']
    gl = .3
    m.box('iron', u - w / 2 + .06, gl, (z0 + top) / 2, .12, .14, top - z0)
    m.box('iron', u + w / 2 - .06, gl, (z0 + top) / 2, .12, .14, top - z0)
    m.box('iron', u, gl, top - .07, w - .24, .14, .14)
    m.box('iron', u, gl, 3.05, w - .24, .14, .1)
    m.box('glass', u, gl + .05, (3.1 + top - .14) / 2, w - .24, .01, top - .14 - 3.1)
    for i in range(1, 5):
        m.box('iron', u - w / 2 + .12 + (w - .24) * i / 5, gl - .01, (3.1 + top - .14) / 2, .04, .06, top - .14 - 3.1)
    if door:
        dc = u + w / 2 - .12 - .6
        spans = [(u - w / 2 + .12, dc - .6)]
        m.box('timber', dc, gl + .6, (z0 + 2.9) / 2, 1.1, .07, 2.9 - z0)
        m.box('glass', dc, gl + .55, 2.0, .7, .01, 1.4)
        for s in (-1, 1):
            m.box('iron', dc + s * .58, gl + .3, (z0 + 3.0) / 2, .05, .6, 3.0 - z0)
        m.box('iron', dc, gl + .3, 3.0, 1.2, .6, .08)
    else:
        spans = [(u - w / 2 + .12, u + w / 2 - .12)]
    for s0, s1 in spans:
        sm = (s0 + s1) / 2
        m.box('iron', sm, gl, z0 + .35, s1 - s0, .14, .7)
        m.box('glass', sm, gl + .05, (z0 + .7 + 3.0) / 2, s1 - s0, .01, 3.0 - z0 - .7)
        if s1 - s0 > 1.6:
            m.box('iron', sm, gl - .01, (z0 + .7 + 3.0) / 2, .06, .08, 3.0 - z0 - .7)
    register(f, h, gl, 'shopfront', 'shop')


def brick_block():
    """Three-storey brick heritage block on the east: cast-iron shopfronts, segment- and round-headed windows with stone
    hoods, brick pilasters, string courses, a corbelled frieze and bracketed cornice, a pedimented gable, hipped
    clay-tile roofs with chimneys."""
    f = BS
    n = 8
    bw = (BX1 - BX0) / n
    holes, kind = [], []
    for i in range(n):
        uc = BX0 + bw * (i + .5)
        holes.append(hole(f'B shop {i}', uc, .3, 3.0, 3.75)); kind.append(('shop', i % 3 == 1))
        for s in (-1, 1):
            holes.append(hole(f'B f2 {i}{s:+d}', uc + s * .85, 5.3, 1.0, 2.2)); kind.append(('seg', None))
            holes.append(hole(f'B f3 {i}{s:+d}', uc + s * .85, 8.6, 1.0, 2.2)); kind.append(('round', None))
    f.wall('brick block south front carrier', BX0, BX1, 0.0, B_WALL, depth=.45, role='brick', holes=holes)
    G.brick_courses(f, BX0 + .02, BX1 - .02, 4.8, 10.7, holes, spacing=.45)
    m = Merge(f)
    for h, (k, door) in zip(holes, kind):
        if k == 'shop':
            brick_shopfront(m, f, h, door)
        else:
            framed(m, f, h, cols=1, rows=2, inset=.2, occupied='office', frame='frame')
            arch_head(f, h, .25 if k == 'seg' else h['w'] / 2, ring=.16, segs=8 if k == 'seg' else 10)
            m.box('stone', h['u'], -.06, h['z'] - .07, h['w'] + .24, .16, .14)
            m.box('stone', h['u'], -.11, h['z'] + h['h'] + .12, .22, .12, .3)                          # keystone
    # Pilasters, piers, courses, the corbelled frieze and the cornice.
    for i in range(n + 1):
        u = BX0 + bw * i
        w = .8 if i in (0, n) else .55
        lo, hi = max(BX0 + .005, u - w / 2), min(BX1 - .005, u + w / 2)
        m.box('brick', (lo + hi) / 2, -.07, (4.8 + 10.75) / 2, hi - lo, .16, 5.95)
        m.box('stone', (lo + hi) / 2, -.1, 10.62, hi - lo + .1, .22, .26)
        m.box('iron', (lo + hi) / 2, -.06, 2.1, hi - lo - .05, .14, 4.2)
        m.box('iron', (lo + hi) / 2, -.1, 4.17, hi - lo + .05, .22, .18)
    band(m, BX0, BX1, 4.25, 4.75, .12, 'iron')                                                         # shop fascia
    band(m, BX0, BX1, 4.75, 4.9, .16, 'stone')
    band(m, BX0, BX1, 5.12, 5.24, .1, 'stone')
    band(m, BX0, BX1, 7.95, 8.1, .14, 'stone')
    band(m, BX0, BX1, 8.42, 8.54, .1, 'stone')
    band(m, BX0, BX1, 10.75, 11.0, .2, 'brick')
    for k in range(int((BX1 - BX0) / .45)):
        m.box('brick', BX0 + .25 + k * .45, -.24, 10.9, .2, .12, .16)                              # dentil course
    eave_cornice(m, BX0 - .05, BX1 + .05, B_EAVE, span_t=.45, proj=.75, role='stone')
    for ue in (BX0 - .05, BX1 + .05):
        m.box('stone', ue, -.355, B_EAVE - .135, .02, 1.22, .285)                                    # cornice end plates
    band(m, BX0, BX1, .0, .3, .06, 'stone')
    m.flush('brick block south front')
    # Brick parapet over the cornice (hides the eaves from the street), stone coping and corner finials.
    b = Batch()
    b.box('brick', (BX0 + BX1) / 2, BY0 + .225, (B_WALL + 13.45) / 2, BX1 - BX0 - .01, .35, 13.45 - B_WALL)
    b.box('stone', (BX0 + BX1) / 2, BY0 + .225, 13.51, BX1 - BX0 + .1, .51, .12)
    for x in (BX0 + .4, BX1 - .4):
        b.box('stone', x, BY0 + .2, 13.9, .95, .9, .8)
        frustum(b, 'stone', x, BY0 + .2, 14.3, 14.75, .5, .08, 4)
    b.flush('brick block parapet')
    # Pediment gable over bays 5 and 6 and its little cross roof.
    px0, px1, rise = 27.9, 33.1, 3.4
    C.prism('Brick block pediment', [(px0, B_EAVE - .15), (px1, B_EAVE - .15), ((px0 + px1) / 2, B_EAVE + rise)], 'y', BY0 - .02, BY0 + .43, 'brick', 'pediment')
    L = math.hypot((px1 - px0) / 2, rise)
    for s in (-1, 1):
        a = ((px0 + px1) / 2 + s * ((px1 - px0) / 2 + .2), BY0 - .2, B_EAVE - .02 - .2 * rise / ((px1 - px0) / 2))
        c = ((px0 + px1) / 2, BY0 - .2, B_EAVE + rise + .14)
        C.beam('Pediment raking coping', a, c, .36, .3, 'stone', 'pediment')
    b = Batch()
    disc(b, 'stone', ((px0 + px1) / 2, BY0 - .02, B_EAVE + 1.25), (0, -1), .62, t=.06, n=24)
    disc(b, 'glass', ((px0 + px1) / 2, BY0 - .05, B_EAVE + 1.25), (0, -1), .44, t=.04, n=24)
    b.box('stone', (px0 + px1) / 2, BY0 - .1, B_EAVE + rise + .35, .5, .4, .6)                          # apex block
    b.flush('pediment details')
    pitched_roof('Pediment cross roof', px0 - .1, px1 + .1, BY0 + .5, -12.0, B_EAVE + .05, rise - .4, False, False, 'y', .3, 'tile', 'roof')
    # Plain side and back walls, floors and interior depth behind the windows.
    b = Batch()
    b.box('brick', BX0 + .005 + .225, (BY0 + .44 + BY1) / 2, B_WALL / 2, .45, BY1 - BY0 - .44, B_WALL)
    b.box('brick', BX1 - .005 - .225, (BY0 + .44 + BY1) / 2, B_WALL / 2, .45, BY1 - BY0 - .44, B_WALL)
    b.box('brick', (BX0 + .46 + BX1 - .46) / 2, BY1 - .005 - .225, B_WALL / 2, BX1 - BX0 - .92, .45, B_WALL)
    b.box('stone', BX0 - .085, (BY0 + .5 + BY1) / 2, 12.4, .2, BY1 - BY0 - .5, .4)
    b.box('interior', (BX0 + BX1) / 2, BY0 + 3.6, B_WALL / 2, BX1 - BX0 - 1.0, .2, B_WALL - .1)
    for z in (4.45, 7.85):
        b.box('floor', (BX0 + BX1) / 2, BY0 + 2.0, z, BX1 - BX0 - 1.0, 3.0, .2)
    b.box('floor', (BX0 + BX1) / 2, BY0 + 2.0, .2, BX1 - BX0 - 1.0, 3.0, .1)
    for k in range(5):
        b.box('timber', BX0 + 3.0 + k * 6.0, BY0 + 1.6, .75, 1.6, .7, .9)                                   # shop counters
    b.flush('brick block shell')
    for x in (14.0, 22.0, 30.0, 38.0):
        for z in (3.6, 7.2, 10.6):
            qa_light(f'brick block {x:.0f} {z:.0f}', (x, BY0 + 2.0, z), 30, 2.0)
    f = C.Face((0, BY1, 0), (-1, 0, 0), (0, -1, 0), 'brick block north wall')
    m = Merge(f)
    windows_grid(m, -21.2, -BX0 - .6, 0.0, B_WALL, 3, 2.4, w=1.0, hh=2.1, frame='stone')
    m.flush('brick block north wall')
    f = C.Face((BX0, 0, 0), (0, -1, 0), (1, 0, 0), 'brick block west wall')
    G.brick_courses(f, -BY1 + .05, -BY0 - .05, 8.2, B_WALL - .1, [], spacing=.45)
    for x, y, z1 in ((12.5, -2.1, 15.6), (12.5, -12.9, 15.6), (24.4, -13.8, 17.0), (19.6, 3.2, 15.6), (39.5, -1.0, 15.6), (39.5, -12.9, 15.6)):
        chimney(b, x, y, 12.0, z1, 1.2, .9, 3, role='brick', pot='pot', cap='stone')
    b.flush('brick block chimneys')
    pitched_roof('Brick block west roof', BX0, 26.5, BY0, BY1, B_EAVE, 6.0, True, True, 'y', .35, 'tile', 'roof')
    pitched_roof('Brick block east roof', 26.5, BX1, BY0, BY1, B_EAVE + .002, 5.6, True, True, 'y', .42, 'tile', 'roof')
    C.CONTACTS.append(dict(name='Brick heritage block walls from grade; hipped tile roofs on the cornice', eave_m=B_EAVE))


def back_blocks():
    """Behind the brick block: a hipped brick wing, a narrow flat-roofed range and the parking court; the brick block
    beyond it on the east."""
    b = Batch()
    b.box('brick2', (25.3 + 36.0) / 2, (BY1 - .3 + 16.4) / 2, 10.6 / 2, 10.7, 16.4 - BY1 + .3, 10.6)
    b.box('brick2', (21.4 + 25.32) / 2, (BY1 - .25 + 16.4) / 2, 7.5 / 2, 3.92, 16.4 - BY1 + .25, 7.5)
    b.box('soil', (21.4 + 25.32) / 2, (BY1 - .25 + 16.4) / 2, 7.53, 3.6, 16.4 - BY1 - .1, .06)
    b.box('brick2', (40.3 + 62.0) / 2, (BY0 + .02 + 18.7) / 2, 12.5 / 2, 21.7, 18.7 - BY0 - .02, 12.5)
    b.box('membrane', (40.3 + 62.0) / 2, (BY0 + 18.7) / 2, 12.53, 21.2, 18.7 - BY0 - .5, .06)
    b.box('stone', (40.3 + 62.0) / 2, BY0 - .12, 12.1, 21.6, .3, .5)
    b.flush('back blocks')
    pitched_roof('Brick wing roof', 25.3, 36.0, BY1 - .3, 16.4, 10.6, 4.4, True, True, 'y', .3, 'tile', 'roof')
    for f, lo, hi, z0, z1, floors, label in ((C.Face((0, BY0 + .02, 0), (1, 0, 0), (0, 1, 0), 'east block south front'), 41.0, 61.5, 4.0, 12.0, 3, 'east block south front'),
                                             (C.Face((25.3, 0, 0), (0, -1, 0), (1, 0, 0), 'brick wing west face'), -16.0, -BY1 - .3, 7.0, 10.0, 1, 'brick wing west face'),
                                             (C.Face((0, 16.4, 0), (-1, 0, 0), (0, -1, 0), 'brick wing north face'), -35.6, -25.6, .2, 10.0, 3, 'brick wing north face')):
        m = Merge(f)
        windows_grid(m, lo, hi, z0, z1, floors, 2.5, w=1.1, hh=2.0, frame='stone')
        if 'east' in label:
            for k in range(5):
                m.box('frame', 42.5 + k * 4.0, -.02, 2.0, 3.0, .06, 2.8)
                m.box('sign', 42.5 + k * 4.0, -.04, 3.8, 3.6, .08, .5)
        m.flush(label)


def context():
    """Low commercial blocks across the west street and the north street, and the harbour with its piers."""
    b = Batch()
    blocks = (('west block 1', -50.0, -34.0, -23.0, -6.0, 9.5, 'brick2'), ('west block 2', -50.0, -34.0, -5.0, 12.0, 12.0, 'cream'),
              ('west block 3', -50.0, -34.0, 13.0, 34.0, 10.5, 'ctx'), ('west block 4', -50.0, -34.0, 37.0, 58.0, 8.0, 'brick2'),
              ('north block 1', -30.0, -8.0, 37.0, 56.0, 10.0, 'ctx'), ('north block 2', -6.0, 14.0, 37.0, 54.0, 7.5, 'brick2'),
              ('north block 3', 16.0, 40.0, 37.0, 55.0, 11.0, 'cream'), ('north block 4', 42.0, 62.0, 37.0, 56.0, 9.0, 'brick2'),
              ('south-west block', -50.0, -34.0, -60.0, -42.0, 9.0, 'ctx'))
    for name, x0, x1, y0, y1, h, role in blocks:
        b.box(role, (x0 + x1) / 2, (y0 + y1) / 2, h / 2, x1 - x0, y1 - y0, h)
        b.box('membrane', (x0 + x1) / 2, (y0 + y1) / 2, h + .03, x1 - x0 - .6, y1 - y0 - .6, .06)
        b.box('mech', (x0 + x1) / 2 + 2.0, (y0 + y1) / 2, h + .6, 2.4, 1.6, 1.2)
    b.flush('context')
    for name, x0, x1, y0, y1, h, role in blocks:
        if x1 == -34.0:
            f = C.Face((x1, 0, 0), (0, 1, 0), (-1, 0, 0), name + ' east face')
            m = Merge(f)
            windows_grid(m, y0 + .6, y1 - .6, 3.6, h - .4, max(1, int((h - 4.0) / 3.0)), 2.6, w=1.1, hh=1.8)
            for k in range(int((y1 - y0) / 4.5)):
                m.box('frame', y0 + 2.2 + k * 4.5, -.02, 1.8, 3.2, .06, 2.6)
                m.box('sign', y0 + 2.2 + k * 4.5, -.05, 3.4, 3.8, .1, .5)
            m.flush(name + ' east face')
        else:
            f = C.Face((0, y0, 0), (1, 0, 0), (0, 1, 0), name + ' south face')
            m = Merge(f)
            windows_grid(m, x0 + .6, x1 - .6, 3.4, h - .4, max(1, int((h - 4.0) / 3.0)), 2.6, w=1.1, hh=1.8)
            m.flush(name + ' south face')
    b = Batch()
    b.box('water', 15.0, 106.0, .015, 150.0, 88.0, .03)                                                 # harbour
    b.box('concrete2', 15.0, 61.6, .45, 150.0, .8, .9)                                                  # quay wall cap
    for x0, x1, y1 in ((0.0, 8.0, 92.0), (28.0, 36.0, 80.0), (-40.0, -30.0, 84.0)):
        b.box('concrete2', (x0 + x1) / 2, (62.0 + y1) / 2, .6, x1 - x0, y1 - 62.0, 1.2)
        b.box('paving', (x0 + x1) / 2, (62.0 + y1) / 2, 1.22, x1 - x0 - .3, y1 - 62.3, .04)
    b.box('paint', 11.5, 78.0, 1.2, 5.0, 24.0, 2.4)                                                   # ferry hull
    b.box('paint', 11.5, 78.0, 3.4, 4.2, 15.0, 2.0)
    b.box('frame', 11.5, 78.0, 3.6, 4.25, 13.0, .7)
    b.box('panel', 11.5, 79.0, 4.6, 3.2, 6.0, .5)
    b.flush('harbour')


def site():
    """Streets, sidewalks, the west lawn strip, curbs, markings, tree pits, street trees, a bench, lights."""
    WC, EC = -31.5, -18.3                    # west street curbs (x)
    SC = -24.2                               # south street north curb (y)
    NC = 23.0                                # north street south curb (y)
    for name, x0, x1, y0, y1, role, top in (
            ('West street', WC, EC, -62.0, 62.0, 'asphalt', .04), ('South street', EC, 64.0, -38.0, SC, 'asphalt', .04),
            ('North street', EC, 64.0, NC, 34.0, 'asphalt', .041), ('Far west sidewalk', -34.0, WC, -62.0, 62.0, 'paving', .14),
            ('Far south sidewalk', EC, 64.0, -41.0, -38.0, 'paving', .14), ('Far north apron', EC, 90.0, 34.0, 61.2, 'paving', .1),
            ('South sidewalk', EC, 64.0, SC, TY0, 'paving', .14), ('West sidewalk', EC, TX0, TY0, NC, 'paving', .14),
            ('North sidewalk', TX0, 64.0, TY1, NC, 'paving', .141), ('Parking court', BX0, 21.4, BY1 - .03, 16.4, 'concrete2', .06),
            ('Rear yard', TX1 - .02, 64.0, 16.4, TY1, 'paving', .12), ('Side passage', TX1 - .02, BX0, BY1 - .03, 16.4, 'paving', .121),
            ('East yard', 36.0, 40.3, BY1, 16.4, 'paving', .122)):
        C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, top / 2), (x1 - x0, y1 - y0, top), role, 'site', 0)
    b = Batch()
    for y0, y1 in ((-19.2, -6.3), (-3.0, 17.3)):                                                      # lawn strips
        b.box('lawn', (-13.6 + TX0 - .02) / 2, (y0 + y1) / 2, .09, TX0 - .02 + 13.6, y1 - y0, .14)
        b.box('curb', -13.63, (y0 + y1) / 2, .1, .1, y1 - y0 + .1, .1)
    b.box('curb', EC + .05, (SC + NC) / 2, .075, .2, NC - SC + .1, .15)                                # curbs, 5 cm proud of the walks
    b.box('curb', (EC + .15 + 64.0) / 2, SC + .05, .076, 64.0 - EC - .15, .2, .152)
    b.box('curb', (EC + .15 + 64.0) / 2, NC - .05, .077, 64.0 - EC - .15, .2, .154)
    b.box('curb', WC + .05, 0.0, .074, .2, 124.0, .148)
    b.box('redpave', EC + 1.8, SC + 1.6, .141, 3.2, 2.8, .006)                                         # corner pavers
    b.box('yellow', 2.9, SC + .55, .141, 13.6, .45, .006)                                               # tactile strip
    for k in range(int((64.0 - EC) / 1.5)):                                                            # sidewalk joints
        b.box('concrete2', EC + .75 + k * 1.5, (SC + TY0) / 2, .1405, .02, TY0 - SC - .3, .003)
    for k in range(int((NC - TY0) / 1.5)):
        b.box('concrete2', (EC + .2 - 13.7) / 2, TY0 + .75 + k * 1.5, .1406, -13.7 - EC - .2, .02, .003)
    for k in range(-26, 26):                                                                           # lane markings
        if -39.0 < k * 2.4 < -23.0:
            continue
        b.box('paint', -28.2, k * 2.4, .042, .12, 1.2, .004)
        b.box('paint', -21.6, k * 2.4, .042, .12, 1.2, .004)
    for x in (-24.95, -24.75):
        for y0, y1 in ((-62.0, -38.5), (-23.8, 62.0)):
            b.box('yellow', x, (y0 + y1) / 2, .041, .1, y1 - y0, .003)
    for k in range(-6, 26):
        b.box('paint', k * 2.4, -27.6, .042, 1.2, .12, .004)
        b.box('paint', k * 2.4, -34.6, .042, 1.2, .12, .004)
    for y in (-31.2, -31.0):
        b.box('yellow', 24.0, y, .041, 80.0, .1, .003)
    for y in (-21.2, -23.6):                                                                           # crossing over the west street
        b.box('paint', (WC + EC) / 2, y, .043, EC - WC - .2, .3, .004)
    for x in (EC + .6, EC + 3.4):                                                                      # crossing over the south street
        b.box('paint', x, (SC - 38.0) / 2, .043, .3, 38.0 + SC - .2, .004)
    for x, y in ((-7.6, -23.0), (10.3, -23.0), (23.5, -23.0), (36.9, -23.0), (-16.4, 12.5), (-16.6, 1.5)):
        b.box('soil', x, y, .145, 1.3, 1.3, .01)
    # Bench, bin, light poles.
    b.box('timber', -14.25, -14.6, .62, .5, 1.9, .07)
    b.box('timber', -14.47, -14.6, .92, .06, 1.9, .5)
    for y in (-15.4, -13.8):
        b.box('hardware', -14.25, y, .38, .5, .06, .5)
    cyl(b, 'frame', -14.2, -12.6, .13, 1.05, .28, 10)
    for x, y in ((-17.8, -16.5), (-17.8, 8.0), (-1.0, -23.8), (17.0, -23.8), (30.0, -23.8)):
        cyl(b, 'frame', x, y, .13, 7.2, .08, 8)
        b.beam('frame', (x, y, 7.1), (x + (1.4 if x < -15 else 0.0), y + (0.0 if x < -15 else -1.4), 7.3), .1)
        b.box('panel', x + (1.5 if x < -15 else 0.0), y + (0.0 if x < -15 else -1.5), 7.25, .5, .3, .12)
    b.flush('site')
    for x, y, hgt in ((-7.6, -23.0, 8.5), (10.3, -23.0, 7.5), (23.5, -23.0, 8.0), (36.9, -23.0, 7.5), (-16.4, 12.5, 9.0), (-16.6, 1.5, 9.0)):
        street_tree(x, y, z=.14, height=hgt, spread=2.1)


def infill():
    """The narrow service link between the terminal and the brick block (a lit roof strip from above)."""
    b = Batch()
    y0, y1 = BY0 + .05, BY1 + .05
    b.box('concrete2', (TX1 - .05 + BX0 + .1) / 2, (y0 + y1) / 2, 10.55 / 2, BX0 + .1 - TX1 + .05, y1 - y0, 10.55)
    b.box('membrane', (TX1 + .05 + BX0 - .05) / 2, (y0 + y1) / 2, 10.565, BX0 - TX1 - .1, y1 - y0 - .1, .04)
    b.box('panel', (TX1 + BX0) / 2, y0, 1.35, 1.0, .06, 2.4)
    b.box('hardware', (TX1 + BX0) / 2 + .3, y0 - .05, 1.2, .04, .04, .15)
    b.flush('service link')


def build():
    site()
    terminal_frame()
    canopies()
    south_front()
    west_front()
    roof()
    interiors()
    infill()
    brick_block()
    back_blocks()
    context()
    C.CONTACTS.append(dict(name='Halifax ferry terminal beside a brick heritage block', box=[TX0, TX1, TY0, TY1]))


LIGHT_RIG = dict(key=(-70, -75, 70), fill=(70, -55, 40), rear=(20, 80, 60), target=(6, -4, 6.0), gain=4.0)
