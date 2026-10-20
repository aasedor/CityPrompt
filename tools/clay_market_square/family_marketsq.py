"""Market square (flexible civic event plaza), authored from the locked catalogue views of
market_square / variant_0 (market_square_v0).

Read from the pixels (the top view governs the plan): a large plaza of pale square concrete slabs that flares
outward toward the viewer, set out with a regular grid of short grey utility bollards (market-stall and event
power points) and small square floor drains; at its head a curved bowl of three concentric seating tiers, each
three low steps of stacked warm-grey stone risers under pale concrete treads with a wide terrace walk, rising to
a raised stage platform with a gently curved dark front edge; on the stage an open-fronted pavilion whose back and
side walls are clad in vertical timber slats of mixed widths, depths and tones, under a deep flat dark roof slab,
with a loudspeaker near each end of the back wall; two slender floodlight masts with stacked lamp heads just
outside the pavilion; stacked-stone cheek walls that step up beside the bowl and raised planting beds of meadow
grass retained by stacked stone along both flared plaza edges, with broad shade trees; lawn and meadow beyond.
There are no stalls or chalets in the source: the square is an open, serviced event floor.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-market-square'
OX, OY = 0.0, 29.0                  # centre of the seating-bowl arcs (north of the stage)
R0 = 29.0                           # outer (lowest) step radius: the bowl meets the plaza at y = 0 on the axis
ARC = 41.0                          # half-angle of the bowl measured from due south (top view: about 38 m chord)
RISE, TREAD, TERRACE = .17, .36, 2.15
PAVE = .06                          # plaza paving top
STAGE = 1.90                        # stage deck top
ROOF_Z = 6.30                       # underside of the pavilion roof slab
X0, X1, Y0, Y1 = -36.0, 36.0, -30.0, 34.0
EPS = .002
T = .3
PALETTE = dict(paving=(.71, .70, .67), joint=(.52, .51, .49), joint2=(.44, .43, .41), concrete=(.80, .78, .74),
    stone=(.63, .56, .46), mortar=(.42, .37, .30), dark=(.17, .17, .18), deck=(.36, .36, .37), roof=(.25, .25, .26),
    timber=(.46, .28, .16), timber2=(.60, .39, .22), timber3=(.33, .20, .12), hardware=(.12, .12, .13),
    pale=(.95, .92, .80), bollard=(.50, .50, .49), lawn=(.30, .44, .20), meadow=(.50, .53, .29), meadow2=(.64, .59, .35),
    tree=(.20, .36, .16), tree2=(.28, .43, .20), bark=(.30, .22, .15), trim=(.22, .22, .23), wall=(.17, .17, .18),
    glass=(.62, .70, .74), interior=(.70, .62, .50))


def manifest(version):
    h = 12.0
    cams = G.camera_roster(X1 - X0, Y1 - Y0, h, [
        ('stage_pavilion', (0.0, 3.0, 3.4), (0.0, 15.5, 3.9), 30),
        ('slat_wall', (2.8, 11.2, 3.4), (1.2, 16.1, 3.9), 40),
        ('seating_tiers', (-15.5, -1.5, 1.7), (-4.0, 11.0, .7), 30),
        ('cheek_walls', (10.0, -5.0, 1.8), (17.5, 9.0, 1.0), 32),
        ('bollard_grid', (-5.0, -24.0, 1.3), (1.5, -8.0, .2), 34),
        ('paving_drain', (5.5, -14.5, 1.6), (6.2, -11.0, .0), 40),
        ('light_mast', (4.0, 5.0, 2.2), (9.4, 15.2, 7.5), 30),
        ('backstage_door', (11.6, 11.0, 3.2), (6.2, 14.4, 3.0), 34),
        ('meadow_beds', (-31.0, -12.0, 4.5), (-20.0, 8.0, 2.0), 30),
        ('rear_north', (4.0, 42.0, 9.0), (0.0, 14.0, 3.0), 30)])
    for c in cams:
        if c['name'] == 'front':                    # the locked front stands on the plaza at eye height, looking north at the stage
            c.update(location=(0.0, -24.5, 1.65), target=(0.0, 14.0, -2.4), lens=31, whole=False)
        elif c['name'] == 'front_corner':           # the locked oblique looks north from high over the south plaza
            c.update(location=(0.0, -37.0, 24.0), target=(0.0, 12.0, 3.0), lens=30, whole=False)
        elif c['name'] == 'aerial':                 # the locked top view is a steep oblique from the south
            c.update(location=(0.0, -29.0, 40.0), target=(0.0, 6.0, 0.0), lens=30, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='market_square/variant_0 (market_square_v0)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=0, storey_programme='open space: a serviced market and event plaza with a seating bowl and a stage pavilion',
            plan='51 m wide flared plaza of square slabs with a 3 m bollard grid; a three-tier seating bowl of 38 m chord on 29 m arcs; 16 m curved stage with a 12.4 m slatted pavilion; raised stone-walled meadow beds both sides',
            facade='stacked warm-grey stone risers and walls with pale concrete treads and copings; vertical timber slat cladding in three tones; dark flat roof slab; grey bollards; slender dark floodlight masts',
            levels_m=[0.0, PAVE, .51, 1.02, 1.53, STAGE, ROOF_Z], inferred='the backstage door, stage side steps, the far lawn and tree belt are teaching assumptions; the meadow grass is abstracted as tufts'),
        roof_contract=dict(type='open space; flat dark roof slab over the stage pavilion', datum_m=0.0, crowns_m=[ROOF_Z + .38]),
        identity_contract=dict(owner='flared bollard-gridded plaza facing a curved three-tier stone-and-concrete seating bowl and a timber-slatted stage pavilion, framed by stacked-stone meadow beds, shade trees and floodlight masts'),
        material_contract=dict(profile='source-palette clay: pale concrete slabs with grey joints, warm stacked stone, pale concrete treads, mixed-tone timber slats, charcoal stage and roof, grey bollards, green lawn and golden meadow', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='market stalls and events on the serviced plaza, seating on the tiers, performance on the stage'),
        contact_contract=['Grade-zero lawn and paving', 'Bowl tiers on grade', 'Stage on the top terrace', 'Pavilion on the stage deck', 'Beds on grade'],
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
# ---- Market square: serviced event plaza, seating bowl and stage pavilion ----

def rnd(i, k=0):
    """Deterministic hash in [0, 1)."""
    return (math.sin(i * 12.9898 + k * 78.233) * 43758.5453) % 1.0


def arc_pts(r, a0, a1, n):
    """Points on a circle about the bowl centre; angles in degrees from due south, east positive."""
    out = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n if n else a0)
        out.append((OX + r * math.sin(a), OY - r * math.cos(a)))
    return out


def mirror(poly):
    return [(-x, y) for (x, y) in reversed(poly)]


def area(poly):
    return .5 * sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(len(poly)))


def inset(poly, d):
    """Mitred inward offset of a simple polygon."""
    s = 1.0 if area(poly) > 0 else -1.0
    out, n = [], len(poly)
    for i in range(n):
        (px, py), (qx, qy), (rx, ry) = poly[i - 1], poly[i], poly[(i + 1) % n]
        def nrm(ax, ay, bx, by):
            L = math.hypot(bx - ax, by - ay)
            return -s * (by - ay) / L, s * (bx - ax) / L                  # inward normal
        n1, n2 = nrm(px, py, qx, qy), nrm(qx, qy, rx, ry)
        mx, my = n1[0] + n2[0], n1[1] + n2[1]
        L = math.hypot(mx, my); mx, my = mx / L, my / L
        k = d / max(.35, mx * n1[0] + my * n1[1])
        out.append((qx + mx * k, qy + my * k))
    return out


def inside(poly, x, y):
    c = False
    for i in range(len(poly)):
        (ax, ay), (bx, by) = poly[i - 1], poly[i]
        if (ay > y) != (by > y) and x < ax + (y - ay) * (bx - ax) / (by - ay):
            c = not c
    return c


def ngon(b, role, cx, cy, z0, z1, r, n=12):
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


def tuft(b, role, x, y, z, h, r, lean):
    """Closed grass clump: a leaning square pyramid seated just into the bed."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2 + lean
        V.append((x + r * math.cos(a), y + r * math.sin(a), z))
    V.append((x + .25 * r * math.cos(lean * 7), y + .25 * r * math.sin(lean * 7), z + h))
    F.extend([(o + 3, o + 2, o + 1, o), (o, o + 1, o + 4), (o + 1, o + 2, o + 4), (o + 2, o + 3, o + 4), (o + 3, o, o + 4)])


# ---- plan ----
A_OUT = arc_pts(R0, ARC, ARC, 0)[0]                 # cheek line, outer end (east)
RIN = R0 - 8 * TREAD - 2 * TERRACE           # upper terrace edge radius
B_IN = arc_pts(RIN, ARC, ARC, 0)[0]                 # cheek line, inner end (east)
TOP = 9 * RISE                                     # upper terrace (stone) level


def cheek(t):
    return (A_OUT[0] + (B_IN[0] - A_OUT[0]) * t, A_OUT[1] + (B_IN[1] - A_OUT[1]) * t)


M_ = cheek(.42)
BED_LO = [(22.37, -10.0), A_OUT, M_, (21.8, 12.7), (31.0, 1.0)]                     # low meadow bed by the plaza
BED_HI = [cheek(.40), B_IN, (B_IN[0], 22.3), (24.5, 22.3), (21.8, 12.6)]           # high meadow bed by the cheek
H_LO, H_HI = .75, 1.95
PLAZA_E = ((25.6, -26.0), arc_pts(R0 + .3, ARC + .5, ARC + .5, 0)[0])            # east plaza edge (south end, north end)


def xe(y):
    (xa, ya), (xb, yb) = PLAZA_E
    return xa + (y - ya) / (yb - ya) * (xb - xa)


def plaza():
    C.box('Lawn', (0.0, (Y0 + Y1) / 2, .015), (X1 - X0, Y1 - Y0, .03), 'lawn', 'site', 0)
    (xa, ya), (xb, yb) = PLAZA_E
    pts = [(-xa, ya), (xa, ya), (xb, yb)] + arc_pts(R0 + .3, ARC + .5, -ARC - .5, 72)[1:-1] + [(-xb, yb)]
    C.prism('Plaza paving', pts, 'z', 0.0, PAVE, 'paving', 'plaza')
    b = Batch()
    ymax_axis = OY - R0
    # Square slabs 1.5 m, a stronger joint every fourth line (6 m panels), clipped to the plaza and the bottom step.
    for k in range(int((yb - ya) / 1.5) + 1):
        y = ya + .75 + k * 1.5
        if y > yb - .1:
            break
        e = xe(y) - .06
        role, w = ('joint2', .03) if k % 4 == 0 else ('joint', .012)
        if y <= ymax_axis - .05:
            spans = [(-e, e)]
        else:
            x0 = math.sqrt(max(0.0, R0 ** 2 - (OY - y) ** 2)) + .05
            spans = [(-e, -x0), (x0, e)] if x0 < e else []
        for (p, q) in spans:
            b.box(role, (p + q) / 2, y, PAVE + .0018, q - p, w, .004)
    for k in range(-17, 18):
        x = k * 1.5
        if abs(x) <= A_OUT[0]:
            ytop = OY - math.sqrt(R0 ** 2 - x * x) - .05
        else:
            ytop = ya + (abs(x) - xa) / (xb - xa) * (yb - ya) - .06
        if ytop <= ya + .1:
            continue
        role, w = ('joint2', .03) if k % 4 == 0 else ('joint', .012)
        b.box(role, x, (ya + .05 + ytop) / 2, PAVE + .0020, w, ytop - ya - .05, .0044)
    # Bollard grid (3 m, alternate rows offset 1.5 m) and small square floor drains between them.
    for j, y in enumerate((-3.0, -7.5, -12.0, -16.5, -21.0)):
        off = 1.5 if j % 2 else 0.0
        lim = xe(y) - 1.2
        for i in range(-12, 13):
            x = i * 3.0 + off
            if abs(x) > lim:
                continue
            ngon(b, 'bollard', x, y, PAVE - .01, .60, .095, 12)
            ngon(b, 'dark', x, y, .58, .635, .105, 12)
            if (i + j) % 3 == 0 and abs(x + 1.5) < lim:
                b.box('dark', x + 1.5, y + .9, PAVE + .005, .36, .36, .014)
                for g in range(4):
                    b.box('hardware', x + 1.5 - .12 + g * .08, y + .9, PAVE + .008, .02, .3, .004)
    b.flush('plaza')


def ring(name, r_out, r_in, top, n=72):
    """Annular sector of the bowl from grade to `top`, with a pale concrete tread cap (40 mm nosing)."""
    pts = arc_pts(r_out, -ARC - .5, ARC + .5, n) + arc_pts(r_in, ARC + .5, -ARC - .5, n)
    C.prism(name, pts, 'z', 0.0, top, 'stone', 'seating bowl')
    cap = arc_pts(r_out + .04, -ARC - .5, ARC + .5, n) + arc_pts(r_in + .02, ARC + .5, -ARC - .5, n)
    C.prism(name + ' tread', cap, 'z', top - .03, top + .03, 'concrete', 'seating bowl')


def bowl():
    b = Batch()
    r, z, k = R0, 0.0, 0
    lower = PAVE
    for t in range(3):
        for s in range(3):
            z += RISE
            depth = TREAD + (TERRACE if (s == 2 and t < 2) else 0.0)
            if t == 2 and s == 2:
                break                                                  # the last riser is the upper terrace edge
            r_in = r - depth
            ring(f'Tier {t + 1} step {s + 1}', r + (.03 if k else 0.0), r_in, z)
            # Stacked-stone riser: a bed joint at mid height and staggered head joints along the arc.
            zj = (lower + .03 + z - .03) / 2
            pts = arc_pts(r + .004, -ARC, ARC, 72)
            for (p, q) in zip(pts, pts[1:]):
                b.beam('mortar', (p[0], p[1], zj), (q[0], q[1], zj), .02, .012)
            L = math.radians(2 * ARC) * r
            m = int(L / .55)
            for i in range(m):
                a = -ARC + 2 * ARC * (i + .5 * ((t + s) % 2) + .25) / m
                lo, hi = (lower + .035, zj) if i % 2 else (zj, z - .035)
                p = arc_pts(r + .004, a, a, 0)[0]
                b.beam('mortar', (p[0], p[1], lo), (p[0], p[1], hi), .02, .012)
            lower = z + .03
            r = r_in
            k += 1
    b.flush('seating bowl joints')
    # Upper terrace: stone mass at the top level, its paved cap in front of and beside the stage, meadow behind.
    up = arc_pts(RIN + .03, -ARC - .5, ARC + .5, 72) + [(B_IN[0] + .05, 22.0), (-B_IN[0] - .05, 22.0)]
    C.prism('Upper terrace', up, 'z', 0.0, TOP, 'stone', 'seating bowl')
    cap = arc_pts(RIN + .07, -ARC - .5, ARC + .5, 72) + [(B_IN[0] - .25, 17.35), (-B_IN[0] + .25, 17.35)]
    C.prism('Upper terrace paving', cap, 'z', TOP - .03, TOP + .03, 'concrete', 'seating bowl')
    C.box('Upper terrace meadow', (0.0, 19.5, TOP + .035), (2 * B_IN[0] - .55, 4.4, .11), 'meadow', 'planting', 0)
    b = Batch()
    wall_courses(b, (B_IN[0] + .05, 22.0), (-B_IN[0] - .05, 22.0), 0.0, TOP)
    b.flush('upper terrace joints')


def wall_courses(b, p, q, z0, z1, outward=None):
    """Stacked-stone dress on the straight face p->q between z0 and z1: bed joints and staggered head joints,
    set 6 mm proud of the face on its outward side (right of p->q unless given)."""
    (px, py), (qx, qy) = p, q
    L = math.hypot(qx - px, qy - py)
    tx, ty = (qx - px) / L, (qy - py) / L
    nx, ny = outward if outward else (ty, -tx)
    o = .006
    z, c = z0 + .13, 0
    while z < z1 - .07:
        b.beam('mortar', (px + nx * o + tx * .05, py + ny * o + ty * .05, z), (qx + nx * o - tx * .05, qy + ny * o - ty * .05, z), .02, .012)
        s = .35 * (c % 2) + .3
        while s < L - .2:
            x, y = px + tx * s + nx * o, py + ty * s + ny * o
            b.beam('mortar', (x, y, z - .125), (x, y, z - .005), .02, .012)
            s += 1.0 + .4 * rnd(c, s)
        z += .16 + .03 * (c % 3)
        c += 1


def edge_out(poly, i):
    """Outward unit normal of edge i -> i+1."""
    (px, py), (qx, qy) = poly[i], poly[(i + 1) % len(poly)]
    L = math.hypot(qx - px, qy - py)
    s = 1.0 if area(poly) > 0 else -1.0
    return s * (qy - py) / L, -s * (qx - px) / L


def ekey(p, q):
    """Side-independent key of a bed edge (the west beds mirror the east ones)."""
    return frozenset(((round(abs(p[0]), 4), round(p[1], 4)), (round(abs(q[0]), 4), round(q[1], 4))))


def beds():
    b = Batch()
    tufts = Batch()
    for side in (1, -1):
        lo = BED_LO if side > 0 else mirror(BED_LO)
        hi = BED_HI if side > 0 else mirror(BED_HI)
        tag = 'east' if side > 0 else 'west'
        C.prism(f'Low meadow bed {tag}', lo, 'z', 0.0, H_LO, 'stone', 'planting')
        C.prism(f'High meadow bed {tag}', hi, 'z', 0.0, H_HI, 'stone', 'planting')
        C.prism(f'Low bed meadow {tag}', inset(lo, .3), 'z', H_LO - .06, H_LO + .06, 'meadow', 'planting')
        C.prism(f'High bed meadow {tag}', inset(hi, .3), 'z', H_HI - .06, H_HI + .06, 'meadow', 'planting')
        for poly, h in ((lo, H_LO), (hi, H_HI)):
            for i in range(len(poly)):
                p, q = poly[i], poly[(i + 1) % len(poly)]
                z0 = 0.0
                e = ekey(p, q)
                if e == ekey(BED_HI[-1], BED_HI[0]):
                    z0 = H_LO                                          # face above the low bed only
                elif e == ekey(BED_HI[1], BED_HI[2]):
                    z0 = TOP                                           # face above the upper terrace only
                elif e == ekey(BED_LO[2], BED_LO[3]):
                    continue                                           # under the high bed
                wall_courses(b, p, q, z0, h, edge_out(poly, i))
        for poly, h, n in ((inset(lo, .45), H_LO, 190), (inset(hi, .45), H_HI, 150)):
            xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
            i = got = 0
            while got < n and i < n * 6:
                i += 1
                x = min(xs) + (max(xs) - min(xs)) * rnd(i, 3 + side)
                y = min(ys) + (max(ys) - min(ys)) * rnd(i, 11 + side)
                if not inside(poly, x, y):
                    continue
                got += 1
                tuft(tufts, 'meadow2' if got % 3 else 'meadow', x, y, h + .02, .35 + .35 * rnd(i, 5), .16 + .14 * rnd(i, 7), rnd(i, 9) * .5)
    # Meadow behind the stage on the upper terrace and in the field to the north.
    i = got = 0
    while got < 110:
        i += 1
        x, y = -B_IN[0] + .7 + (2 * B_IN[0] - 1.4) * rnd(i, 21), 17.9 + 3.5 * rnd(i, 22)
        got += 1
        tuft(tufts, 'meadow2' if got % 2 else 'meadow', x, y, TOP + .07, .3 + .3 * rnd(i, 23), .15 + .12 * rnd(i, 24), rnd(i, 25))
    i = got = 0
    while got < 260:
        i += 1
        x, y = X0 + 1.0 + (X1 - X0 - 2.0) * rnd(i, 31), 23.2 + (Y1 - 24.0) * rnd(i, 32)
        if abs(x) < B_IN[0] + .4 and y < 22.6:
            continue
        got += 1
        tuft(tufts, 'meadow2' if got % 3 else 'meadow', x, y, .02, .35 + .4 * rnd(i, 33), .16 + .14 * rnd(i, 34), rnd(i, 35))
    b.flush('bed joints')
    tufts.flush('meadow tufts')


def slats(b, p0, t, n, L, z0, z1, skip=(), seed=0, wide=False):
    """Vertical timber slats of mixed width, depth and tone along a face from p0 in tangent t, standing out along n."""
    s, i = .02, 0
    while s < L - .03:
        w = (.16 + .10 * rnd(i, seed)) if wide else (.07 + .09 * rnd(i, seed))
        w = min(w, L - .02 - s)
        d = .03 + .10 * rnd(i, seed + 1)
        c = s + w / 2
        if not any(a <= c <= z for (a, z) in skip):
            role = ('timber', 'timber2', 'timber3')[int(rnd(i, seed + 2) * 3)]
            cx = p0[0] + t[0] * c + n[0] * (d / 2 - .01)
            cy = p0[1] + t[1] * c + n[1] * (d / 2 - .01)
            sx = w if abs(t[0]) > .5 else d
            sy = d if abs(t[0]) > .5 else w
            b.box(role, cx, cy, (z0 + z1) / 2, sx, sy, z1 - z0)
        s += w + .012 + .02 * rnd(i, seed + 3)
        i += 1


def stage():
    # Stage platform with a dark curved front fascia and a grey deck.
    a = math.degrees(math.asin(8.2 / 19.4))
    pts = arc_pts(19.4, -a, a, 40) + [(8.2, 16.6), (-8.2, 16.6)]
    C.prism('Stage platform', pts, 'z', TOP - .03, STAGE - .04, 'dark', 'stage')
    a2 = math.degrees(math.asin(8.13 / 19.33))
    C.prism('Stage deck', arc_pts(19.33, -a2, a2, 40) + [(8.13, 16.53), (-8.13, 16.53)], 'z', STAGE - .06, STAGE, 'deck', 'stage')
    b = Batch()
    for s in (1, -1):                                                  # side steps down to the terrace
        b.box('concrete', s * 8.37, 13.9, (TOP + STAGE - RISE) / 2 - .01, .38, 1.6, STAGE - RISE - TOP + .02)
    # Pavilion: back wall and returns (dark carriers) clad in slats, under a deep flat roof slab.
    zc0, zc1 = STAGE - .02, ROOF_Z + .02
    C.box('Pavilion back wall', (0.0, 16.25, (zc0 + zc1) / 2), (12.4, .3, zc1 - zc0), 'dark', 'pavilion', 0)
    C.box('Pavilion west return', (-6.05, 14.38, (zc0 + zc1) / 2), (.3, 3.55, zc1 - zc0), 'dark', 'pavilion', 0)
    f = C.Face((6.2, 16.15, STAGE), (0, -1, 0), (-1, 0, 0), 'Pavilion east return')
    door = hole('Backstage door', 1.8, 0.0, 1.0, 2.2)
    f.wall('Pavilion east return', 0.0, 3.55, -.02, ROOF_Z - STAGE + .02, depth=.3, role='dark', holes=[door])
    f.door('Backstage door', 1.8, 0.0, 1.0, 2.2, role='timber3', panels=3)
    C.box('Pavilion roof slab', (0.0, 14.475, ROOF_Z + .18), (13.7, 4.95, .36), 'dark', 'pavilion', 0)
    C.box('Pavilion roof membrane', (0.0, 14.475, ROOF_Z + .37), (13.5, 4.75, .03), 'roof', 'pavilion', 0)
    z0, z1 = STAGE - .01, ROOF_Z + .01
    slats(b, (-5.9, 16.1), (1, 0), (0, -1), 11.8, z0, z1, seed=1)                      # stage face of the back wall
    slats(b, (-6.2, 16.4), (1, 0), (0, 1), 12.4, z0, z1, seed=5, wide=True)            # rear face
    slats(b, (6.2, 16.4), (0, -1), (1, 0), 3.8, z0, z1, skip=[(1.8 + .25 - .62, 1.8 + .25 + .62)], seed=9)
    slats(b, (5.9, 16.1), (0, -1), (-1, 0), 3.5, z0, z1, skip=[(1.8 - .05 - .62, 1.8 - .05 + .62)], seed=13)
    slats(b, (-6.2, 12.6), (0, 1), (-1, 0), 3.8, z0, z1, seed=17)
    slats(b, (-5.9, 12.6), (0, 1), (1, 0), 3.5, z0, z1, seed=21)
    for s in (1, -1):
        b.box('timber3', s * 6.05, 12.57, (z0 + z1) / 2, .36, .08, z1 - z0)              # end caps of the returns
        b.box('dark', s * 5.2, 15.83, STAGE + 2.85, .62, .42, .95)                        # loudspeakers
        b.box('trim', s * 5.2, 15.605, STAGE + 2.85, .5, .02, .8)
        b.box('hardware', s * 5.2, 16.0, STAGE + 3.4, .08, .3, .08)
    b.flush('pavilion')
    # Floodlight masts with stacked lamp heads facing the stage and the plaza.
    b = Batch()
    for s in (1, -1):
        x, y = s * 9.6, 15.4
        b.box('concrete', x, y, TOP + .2, .7, .7, .45)
        C.rod('Floodlight mast', (x, y, TOP + .4), (x, y, 11.2), .09, 'hardware', 'masts', 12)
        b.box('hardware', x, y, 11.22, .24, .24, .06)
        for k in range(6):
            z = 6.6 + k * .85
            dx = -s * .22 if k % 2 else -s * .05
            b.box('hardware', x + dx / 2, y - .12, z, abs(dx) + .06, .06, .06)
            b.box('dark', x + dx, y - .3, z, .3, .26, .24)
            b.box('pale', x + dx, y - .44, z, .24, .02, .18)
    b.flush('masts')


def park_tree(x, y, z, height, spread, seed, detail=1, crowns=7):
    """Broad deciduous shade tree: a trunk sunk into its bed, forked limbs and a clustered crown."""
    C.rod('Tree trunk', (x, y, max(z - .15, .0)), (x, y, z + height * .45), .16 + .02 * spread, 'bark', 'trees', 8)
    top = z + height * .45
    for k in range(crowns):
        a = 2 * math.pi * k / crowns + seed
        rr = spread * (.45 + .25 * rnd(seed, k))
        tip = (x + rr * math.cos(a), y + rr * math.sin(a), z + height * (.62 + .12 * rnd(seed, k + 7)))
        C.rod('Tree limb', (x, y, top - .2), tip, .07, 'bark', 'trees', 6)
        A.foliage('Tree crown', tip, (spread * .62, spread * .62, height * .17), role='tree' if k % 2 else 'tree2', detail=detail)
    A.foliage('Tree crown', (x, y, z + height * .8), (spread * .7, spread * .7, height * .2), role='tree2', detail=detail)


def trees():
    for s in (1, -1):
        for i, (x, y, z, h, sp) in enumerate(((19.4, 16.6, H_HI, 8.5, 2.8), (22.6, 19.6, H_HI, 9.0, 3.0), (16.8, 20.2, H_HI, 7.5, 2.4),
                                             (25.6, 4.6, H_LO, 8.0, 2.7), (23.6, -3.2, H_LO, 7.0, 2.3))):
            park_tree(s * (x + .4 * (s < 0)), y - .5 * (s < 0), z, h, sp, i * 1.7 + (s < 0) * .9)
    for i, (x, y) in enumerate(((-32.0, 28.5), (-26.5, 30.0), (-21.0, 28.0), (21.5, 28.5), (27.0, 30.0), (32.0, 28.0),
                                (-32.0, -14.0), (32.0, -18.0), (-9.0, 30.0), (9.5, 29.5))):
        park_tree(x, y, .03, 9.5, 3.0, 3.1 + i, detail=1, crowns=4)


def furniture():
    b = Batch()
    for x, y in ((-28.0, -15.0), (28.0, -9.0)):
        b.box('concrete', x, y, .22, .5, 2.0, .44)
        for k in range(5):
            b.box('timber', x, y - .8 + k * .4, .47, .55, .3, .06)
    b.flush('benches')


def build():
    plaza()
    bowl()
    beds()
    stage()
    trees()
    furniture()
    C.CONTACTS.append(dict(name='Market and event plaza with a seating bowl, stage pavilion and meadow beds', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(-30, -42, 45), fill=(40, -22, 30), rear=(-18, 50, 35), target=(0, 4, 1.5), gain=3.2)
