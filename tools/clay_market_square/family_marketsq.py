"""Market square (flexible civic event plaza), authored from the locked catalogue views of
market_square / variant_0 (market_square_v0).

Read from the pixels (the top view governs the plan): a large plaza of pale square concrete slabs that flares
outward toward the viewer all the way to its south edge, first between stone bed walls that splay out from the foot of
the bowl and then against open lawn wedges, set out with a regular grid of short grey utility bollards (market-stall
and event power points) whose rows lengthen southward, and small square floor drains; at its head a bowl of three
seating tiers on concentric arcs concave to the plaza, each tier a band of three steps of coursed warm-grey
stacked-stone risers under light warm-stone treads, the bands separated by broad pale concrete terrace walks, the
upper tiers' ends curling north beside the stage up to the stacked-stone cheek walls; a wide raised stage platform
with a gently curved dark front edge; on the stage an open-fronted pavilion whose back and
side walls are clad in vertical timber slats of mixed widths, depths and tones, under a deep flat dark roof slab,
with a loudspeaker near each end of the back wall; two slender floodlight masts with stacked lamp heads just
outside the pavilion; stacked-stone cheek walls beside the stage and raised planting beds of meadow
grass retained by stacked stone beside the bowl, with broad shade trees; lawn and meadow beyond.
There are no stalls or chalets in the source: the square is an open, serviced event floor.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-market-square'
OX, OY = 0.0, 40.0                  # centre of the stage-front arc (the stage edge is convex toward the plaza)
YF, R0 = -3.0, 73.5                 # apex of the bowl foot on the axis; radius of the foot arc (centre on the plaza
                                    # axis R0 south of the apex), so every tier line is a concentric arc concave to the plaza
XB, CURL_K, CURL_P = 14.0, .099, 1.6    # beyond |x| = XB (just outside the stage) the upper tier lines curl north
FOOT_X, TOP_X = 18.0, 27.0          # half-width of the lowest riser and of the top tier at the bowl-end walls
RISE, TREAD, TERRACE = .30, .45, 2.3
PAVE = .06                          # plaza paving top
STAGE = 9 * RISE + .37              # stage deck top
ROOF_Z = STAGE + 5.6                # underside of the pavilion roof slab
X0, X1, Y0, Y1 = -40.0, 40.0, -30.0, 34.0
EPS = .002
T = .3
PALETTE = dict(paving=(.71, .70, .67), joint=(.52, .51, .49), joint2=(.44, .43, .41), concrete=(.80, .78, .74),
    stone=(.57, .50, .41), stone2=(.65, .58, .47), stone3=(.49, .43, .35), tread=(.74, .68, .58), mortar=(.30, .26, .21), dark=(.17, .17, .18), deck=(.36, .36, .37), roof=(.25, .25, .26),
    timber=(.46, .28, .16), timber2=(.66, .45, .27), timber3=(.27, .16, .09), hardware=(.12, .12, .13),
    pale=(.95, .92, .80), bollard=(.50, .50, .49), lawn=(.30, .44, .20), meadow=(.50, .53, .29), meadow2=(.64, .59, .35),
    tree=(.20, .36, .16), tree2=(.28, .43, .20), bark=(.30, .22, .15), trim=(.22, .22, .23), wall=(.17, .17, .18),
    glass=(.62, .70, .74), interior=(.70, .62, .50))


def manifest(version):
    h = 12.0
    cams = G.camera_roster(X1 - X0, Y1 - Y0, h, [
        ('stage_pavilion', (0.0, -4.0, 5.5), (0.0, 16.0, 5.8), 28),
        ('slat_wall', (4.0, 12.4, 5.2), (2.0, 17.4, 5.8), 40),
        ('seating_tiers', (-10.0, -8.0, 1.7), (-4.0, 4.0, 1.0), 30),
        ('cheek_walls', (7.0, 6.5, 4.8), (14.4, 12.0, 3.4), 30),
        ('bollard_grid', (-4.5, -28.0, 1.3), (1.5, -10.0, .15), 34),
        ('paving_drain', (-.15, -12.3, 1.6), (.75, -9.0, .0), 40),
        ('light_mast', (21.0, 4.0, 4.8), (16.1, 16.0, 9.5), 30),
        ('backstage_door', (13.0, 12.2, 4.8), (10.8, 15.45, 4.4), 34),
        ('meadow_beds', (-36.0, -15.0, 5.0), (-27.0, 1.0, 1.8), 30),
        ('rear_north', (5.0, 44.0, 10.0), (0.0, 15.0, 3.5), 30)])
    for c in cams:
        if c['name'] == 'front':                    # the locked front stands close on the plaza at eye height with a wide lens: the bowl foot fills about 70% of the frame and the low bed walls show at both edges
            c.update(location=(0.0, -27.0, 6.2), target=(0.0, 8.0, 1.6), lens=22, whole=False)
        elif c['name'] == 'front_corner':           # the locked oblique looks north from high over the south plaza
            c.update(location=(0.0, -37.0, 24.0), target=(0.0, 12.0, 3.0), lens=30, whole=False)
        elif c['name'] == 'aerial':                 # the locked top view is a steep oblique from the south
            c.update(location=(0.0, -29.0, 40.0), target=(0.0, 6.0, 0.0), lens=30, whole=False)
        elif c['name'] in ('left_side', 'right_side'):  # whole-site side views framed tight on the 64 m depth
            s = -1 if c['name'] == 'left_side' else 1
            c.update(location=(s * 58.0, 2.0, 10.0), target=(0.0, 2.0, 2.0), lens=30, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(0.0, 74.0, 13.0), target=(0.0, 2.0, 2.0), lens=30, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='market_square/variant_0 (market_square_v0)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=0, storey_programme='open space: a serviced market and event plaza with a seating bowl and a stage pavilion',
            plan='plaza of square slabs flaring continuously to its south edge, first between stone bed walls splayed about 22 degrees off the bowl foot and then against lawn wedges, with a 3 m grid of short bollards whose rows lengthen southward; a three-tier seating bowl on concentric arcs concave to the plaza (36 m foot chord, 54 m top tier), three-step warm-stone bands separated by broad pale terrace walks, the upper tier ends curling north beside the stage to the cheek walls; 27 m curved stage with a 21.6 m slatted pavilion; low wedge beds and raised stone-walled meadow beds both sides',
            facade='stacked warm-grey stone risers and walls with pale concrete treads and copings; vertical timber slat cladding in three tones; dark flat roof slab; grey bollards; slender dark floodlight masts',
            levels_m=[0.0, PAVE, 3 * RISE, 6 * RISE, 9 * RISE, STAGE, ROOF_Z], inferred='the backstage door, stage side steps, the far lawn and tree belt are teaching assumptions; the meadow grass is abstracted as tufts'),
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


# ---- plan: tier line u (distance up the axis from the bowl foot) is the arc of radius R0 + u about the centre
# (0, YF - R0), so all tier lines are concentric and concave to the plaza; beyond |x| = XB the upper lines curl north
# (weight rising with u) so the top tiers' ends wrap up beside the stage to the cheek walls. ----
U_TOP = 8 * TREAD + 2 * TERRACE                     # face of the last riser (upper-terrace edge) on the axis
U_W = U_TOP + 1.6                                   # high-bed retaining wall behind the top-tier walk
TOP = 9 * RISE                                     # upper terrace (stone) level
CHEEK_X = 14.7                                      # face of the high bed beside the stage cheek walls


def curl(u, x):
    ax = abs(x) - XB
    if ax <= 0.0:
        return 0.0
    w = min(1.0, max(0.0, u / U_TOP))
    return w * CURL_K * ax ** CURL_P


def cy(u, x):
    return YF - R0 + math.sqrt((R0 + u) ** 2 - x * x) + curl(u, x)


def curve_pts(u, x0, x1, n):
    return [(x0 + (x1 - x0) * i / n, cy(u, x0 + (x1 - x0) * i / n)) for i in range(n + 1)]


F_END = (FOOT_X, cy(0.0, FOOT_X))                   # foot of the east bowl-end (bed) wall
U_END = (TOP_X, cy(U_TOP, TOP_X))                   # upper end of the east bowl-end wall
_D = (U_END[0] - F_END[0], U_END[1] - F_END[1])
_DL = math.hypot(*_D)
N_OUT = (_D[1] / _DL, -_D[0] / _DL)                 # outward (bed-side) normal of the east bowl-end wall line


def wall_pt(t, d=0.0):
    return (F_END[0] + t * _D[0] + d * N_OUT[0], F_END[1] + t * _D[1] + d * N_OUT[1])


def end_x(u, d=0.0):
    """x where tier line u meets the east bowl-end wall line pushed d into the bed."""
    def f(x):
        y = cy(u, x)
        return (x - F_END[0]) * N_OUT[0] + (y - F_END[1]) * N_OUT[1] - d
    lo, hi = 2.0, 45.0
    for _ in range(60):
        m = (lo + hi) / 2
        if f(m) > 0:
            hi = m
        else:
            lo = m
    return (lo + hi) / 2


T1 = 3 * TREAD + TERRACE                            # top of the first tier (its walk's back edge)
F_MID = (end_x(T1), cy(T1, end_x(T1)))              # where the first tier meets the bowl-end wall: low bed ends here
W_X = end_x(U_W)
WALL_ARC = curve_pts(U_W, W_X, CHEEK_X, 12)         # high-bed front behind the top walk, curling up to the cheek wall
Y_CHEEK = WALL_ARC[-1][1] + .05                    # the stage cheek walls run forward to meet the high-bed corner
# Low wedge bed: the stone front wall splays about 22 degrees off the foot line to the bed corner S_END; from there the
# plaza edge keeps flaring south-outward against an open lawn wedge to the site's south edge.
S_END = (27.0, F_END[1] - (27.0 - F_END[0]) * math.tan(math.radians(22.0)))
B_E = (36.0, 2.0)
BED_LO = [F_END, F_MID, B_E, S_END]
BED_HI = [F_MID, U_END] + WALL_ARC + [(CHEEK_X, 22.3), (37.0, 22.3), B_E]
H_LO, H_HI = .9, TOP + .45
# per-edge treatment of the bed walls: base level of the dressed face, or None where the edge is buried
LO_EDGES = [0.0, None, 0.0, 0.0]
HI_EDGES = [0.0, 0.0] + [TOP] * (len(WALL_ARC) - 1) + [TOP, 0.0, 0.0, H_LO]
# Plaza east edge: 12 cm under the splayed low-bed wall, then on to the south edge at PA_X.
_SD = (S_END[0] - F_END[0], S_END[1] - F_END[1])
_SL = math.hypot(*_SD)
_SN = (-_SD[1] / _SL, _SD[0] / _SL)                 # normal of the splayed wall into the bed
if _SN[1] < 0:
    _SN = (-_SN[0], -_SN[1])
F_IN = (F_END[0] + .12 * _SN[0], F_END[1] + .12 * _SN[1])
_PBX = S_END[0] - .05
PB = (_PBX, F_IN[1] + (_PBX - F_IN[0]) / _SD[0] * _SD[1])
PA_X = 38.6


def xe(y):
    """Half-width of the plaza at y."""
    if y <= PB[1]:
        return PB[0] + (PB[1] - y) / (PB[1] - Y0) * (PA_X - PB[0])
    if y <= F_IN[1]:
        return F_IN[0] + (F_IN[1] - y) / (F_IN[1] - PB[1]) * (PB[0] - F_IN[0])
    return F_IN[0]


def foot_x(y):
    """Half-width of the bottom riser line at y (0 north of its apex)."""
    dy = y - (YF - R0)
    return math.sqrt(max(0.0, R0 * R0 - dy * dy)) if y < YF else 0.0


def plaza_end():
    """Where the splayed plaza edge, carried on toward the axis, meets the line 30 cm under the bottom riser."""
    s = 0.0
    while s < 4.0:
        x, y = F_IN[0] - _SD[0] / _SL * s, F_IN[1] - _SD[1] / _SL * s
        if y >= cy(.3, x):
            return x, y
        s += .01
    return F_IN


def plaza():
    C.box('Lawn', (0.0, (Y0 + Y1) / 2, .015), (X1 - X0, Y1 - Y0, .03), 'lawn', 'site', 0)
    fp = plaza_end()
    pts = [(-PA_X, Y0), (PA_X, Y0), PB, fp] + curve_pts(.3, fp[0], -fp[0], 72)[1:-1] + [(-fp[0], fp[1]), (-PB[0], PB[1])]
    C.prism('Plaza paving', pts, 'z', 0.0, PAVE, 'paving', 'plaza')
    b = Batch()
    # Square slabs 1.5 m, a stronger joint every fourth line (6 m panels), clipped to the plaza and the bottom riser.
    for k in range(40):
        y = Y0 + .75 + k * 1.5
        if y > YF - .1:
            break
        e = min(xe(y), foot_x(y) if y > YF - 12 else 99.0) - .06
        if e < .5:
            continue
        role, w = ('joint2', .03) if k % 4 == 0 else ('joint', .012)
        b.box(role, 0.0, y, PAVE + .0018, 2 * e, w, .004)
    for k in range(-25, 26):
        x = k * 1.5
        ax = abs(x)
        if ax <= FOOT_X:
            ytop = cy(0.0, x) - .05
        elif ax <= PB[0]:
            ytop = F_IN[1] - (ax - F_IN[0]) / (PB[0] - F_IN[0]) * (F_IN[1] - PB[1]) - .06
        elif ax < PA_X - .1:
            ytop = PB[1] - (ax - PB[0]) / (PA_X - PB[0]) * (PB[1] - Y0) - .06
        else:
            continue
        role, w = ('joint2', .03) if k % 4 == 0 else ('joint', .012)
        b.box(role, x, (Y0 + .05 + ytop) / 2, PAVE + .0020, w, ytop - Y0 - .05, .0044)
    # Short stubby utility bollards on a 3 m grid (alternate rows offset 1.5 m), with single square slotted floor
    # drains centred in a slab.
    for j, y in enumerate((-7.5, -12.0, -16.5, -21.0, -25.5)):
        off = 1.5 if j % 2 else 0.0
        lim = xe(y) - 1.2
        for i in range(-13, 14):
            x = i * 3.0 + off
            if abs(x) > lim:
                continue
            ngon(b, 'bollard', x, y, PAVE - .01, .49, .16, 10)
            ngon(b, 'joint2', x, y, .485, .525, .145, 10)
            dx, dy = x + 2.25, y + 1.5
            if (i + j) % 3 == 0 and abs(dx) < xe(dy) - .8 and dy < cy(0.0, dx) - .8:
                b.box('dark', dx, dy, PAVE + .0012, .42, .42, .004)
                for g in range(5):
                    b.box('hardware', dx - .16 + g * .08, dy, PAVE + .0035, .024, .34, .0022)
    b.flush('plaza')


def ring(name, u_in, u_out, top, n=56, cap_role='concrete'):
    """One step of the bowl from grade to `top` between tier lines u_in (riser face, toward the plaza) and u_out, ends
    buried 20 cm in the bowl-end walls, with a pale concrete tread cap 6 cm thick whose 5 cm nosing throws a shadow
    line over the stone riser below."""
    x_i, x_o = end_x(u_in, .2), end_x(u_out, .2)
    pts = curve_pts(u_in, -x_i, x_i, n) + curve_pts(u_out, x_o, -x_o, n)
    C.prism(name, pts, 'z', 0.0, top, 'mortar', 'seating bowl')
    c_i, c_o = end_x(u_in - .05, .15), end_x(u_out + .02, .15)
    cap = curve_pts(u_in - .05, -c_i, c_i, n) + curve_pts(u_out + .02, c_o, -c_o, n)
    C.prism(name + ' tread', cap, 'z', top - .04, top + .02, cap_role, 'seating bowl')


def riser_stones(b, u, z0, z1, seed):
    """Stacked ledgestone on a riser face (tier line u) between z0 and z1: long flat stones in courses, proud of the
    dark bedding mass behind, with staggered head joints."""
    a = end_x(u, .15)
    courses = 3 if z1 - z0 > .15 else 2
    h = (z1 - z0) / courses
    for c in range(courses):
        zc = z0 + h * (c + .5)
        s = -a + (.3 + .5 * rnd(seed, c))
        i = 0
        while s < a:
            L = 1.3 + 1.4 * rnd(seed * 31 + c, i)
            e = min(s + L, a)
            p, q = (s, cy(u - .008, s)), (e - .012, cy(u - .008, e - .012))
            role = ('stone', 'stone2', 'stone3')[int(rnd(seed + c, i) * 3)]
            b.beam(role, (p[0], p[1], zc), (q[0], q[1], zc), .034, h - .012)
            s, i = e, i + 1


def bowl():
    b = Batch()
    u, z, k = 0.0, 0.0, 0
    lower = PAVE
    for t in range(3):
        for s in range(3):
            z += RISE
            depth = TREAD + (TERRACE if (s == 2 and t < 2) else 0.0)
            face = u - (.03 if k else 0.0)
            if t == 2 and s == 2:
                riser_stones(b, face, lower, z - .045, k + 1)               # the last riser is the upper terrace edge
                break
            ring(f'Tier {t + 1} step {s + 1}', face, u + depth, z, cap_role='concrete' if s == 2 else 'tread')
            riser_stones(b, face, lower, z - .045, k + 1)
            lower = z + .02
            u += depth
            k += 1
    b.flush('seating bowl stones')
    # Upper terrace: stone mass at the top level reaching under the high beds, its pale paving in front of and
    # beside the stage, and meadow behind the pavilion.
    x_t, x_w = end_x(U_TOP - .03, .2), end_x(U_W + .3, .2)
    east = curve_pts(U_W + .3, x_w, CHEEK_X + .3, 10)
    up = curve_pts(U_TOP - .03, -x_t, x_t, 72) + east + [(CHEEK_X + .3, 22.0), (-CHEEK_X - .3, 22.0)] + mirror(east)
    C.prism('Upper terrace', up, 'z', 0.0, TOP, 'mortar', 'seating bowl')
    x_c, x_k = end_x(U_TOP - .05, .1), end_x(U_W + .1, .1)
    east = curve_pts(U_W + .1, x_k, CHEEK_X - .5, 10)
    cap = curve_pts(U_TOP - .05, -x_c, x_c, 72) + east + [(CHEEK_X - .5, 18.1), (-CHEEK_X + .5, 18.1)] + mirror(east)
    C.prism('Upper terrace paving', cap, 'z', TOP - .03, TOP + .03, 'concrete', 'seating bowl')
    C.box('Upper terrace meadow', (0.0, 20.05, TOP + .085), (2 * CHEEK_X - .6, 3.8, .11), 'meadow', 'planting', 0)
    C.box('Upper terrace back wall', (0.0, 22.04, TOP / 2), (2 * CHEEK_X + .5, .1, TOP), 'stone', 'seating bowl', 0)
    b = Batch()
    wall_courses(b, (CHEEK_X + .2, 22.09), (-CHEEK_X - .2, 22.09), 0.0, TOP, (0.0, 1.0))
    b.flush('terrace back joints')
    # Stacked-stone cheek walls at both stage ends, stepping up toward the back, with the side steps between
    # each wall and the stage.
    b = Batch()
    xc = CHEEK_X - .25
    for sgn in (1, -1):
        for (y0, y1, h) in ((Y_CHEEK, 13.0, TOP + .75), (13.0, 18.2, TOP + 1.15)):
            C.box('Stage cheek wall', (sgn * xc, (y0 + y1) / 2, h / 2), (.6, y1 - y0, h), 'stone', 'seating bowl', 0)
            C.box('Stage cheek wall coping', (sgn * xc, (y0 + y1) / 2 - .01, h + .03), (.7, y1 - y0 + .04 - (.02 if y0 > 10 else 0.0), .06),
                  'concrete', 'seating bowl', 0)
            xf = sgn * (xc - .3)
            wall_courses(b, (xf, y0 if sgn > 0 else y1), (xf, y1 if sgn > 0 else y0), TOP, h, (-sgn, 0.0))
        wall_courses(b, (sgn * (xc - .3), Y_CHEEK), (sgn * (xc + .3), Y_CHEEK), TOP, TOP + .75, (0.0, -1.0))
        wall_courses(b, (sgn * (xc - .3), 13.0), (sgn * (xc + .3), 13.0), TOP + .75, TOP + 1.15, (0.0, -1.0))
    b.flush('cheek wall joints')


def wall_courses(b, p, q, z0, z1, outward=None):
    """Stacked-stone dress on the straight face p->q between z0 and z1: bed joints and staggered head joints,
    set 6 mm proud of the face on its outward side (right of p->q unless given)."""
    (px, py), (qx, qy) = p, q
    L = math.hypot(qx - px, qy - py)
    if L < .1:
        return
    tx, ty = (qx - px) / L, (qy - py) / L
    nx, ny = outward if outward else (ty, -tx)
    o = .006
    z, c = z0 + .185, 0
    while z < z1 - .07:
        b.beam('mortar', (px + nx * o + tx * .05, py + ny * o + ty * .05, z), (qx + nx * o - tx * .05, qy + ny * o - ty * .05, z), .02, .012)
        s = .35 * (c % 2) + .3
        while s < L - .2:
            x, y = px + tx * s + nx * o, py + ty * s + ny * o
            b.beam('mortar', (x, y, z - .175), (x, y, z - .005), .02, .012)
            s += 1.5 + .6 * rnd(c, s)
        z += .21 + .04 * (c % 3)
        c += 1


def edge_out(poly, i):
    """Outward unit normal of edge i -> i+1."""
    (px, py), (qx, qy) = poly[i], poly[(i + 1) % len(poly)]
    L = math.hypot(qx - px, qy - py)
    s = 1.0 if area(poly) > 0 else -1.0
    return s * (qy - py) / L, -s * (qx - px) / L


def beds():
    b = Batch()
    tufts = Batch()
    for side in (1, -1):
        lo = BED_LO if side > 0 else mirror(BED_LO)
        hi = BED_HI if side > 0 else mirror(BED_HI)
        lo_e = LO_EDGES if side > 0 else list(reversed(LO_EDGES[:-1])) + [LO_EDGES[-1]]
        hi_e = HI_EDGES if side > 0 else list(reversed(HI_EDGES[:-1])) + [HI_EDGES[-1]]
        tag = 'east' if side > 0 else 'west'
        C.prism(f'Low meadow bed {tag}', lo, 'z', 0.0, H_LO, 'stone', 'planting')
        C.prism(f'High meadow bed {tag}', hi, 'z', 0.0, H_HI, 'stone', 'planting')
        C.prism(f'Low bed meadow {tag}', inset(lo, .3), 'z', H_LO - .06, H_LO + .06, 'meadow', 'planting')
        C.prism(f'High bed meadow {tag}', inset(hi, .3), 'z', H_HI - .06, H_HI + .06, 'meadow', 'planting')
        for poly, h, edges in ((lo, H_LO, lo_e), (hi, H_HI, hi_e)):
            for i in range(len(poly)):
                if edges[i] is None:
                    continue
                wall_courses(b, poly[i], poly[(i + 1) % len(poly)], edges[i], h, edge_out(poly, i))
        for poly, h, n in ((inset(lo, .45), H_LO, 120), (inset(hi, .45), H_HI, 140)):
            xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
            i = got = 0
            while got < n and i < n * 8:
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
        x, y = -13.6 + 27.2 * rnd(i, 21), 18.4 + 3.3 * rnd(i, 22)
        got += 1
        tuft(tufts, 'meadow2' if got % 2 else 'meadow', x, y, TOP + .12, .3 + .3 * rnd(i, 23), .15 + .12 * rnd(i, 24), rnd(i, 25))
    i = got = 0
    while got < 200:
        i += 1
        x, y = X0 + 1.0 + (X1 - X0 - 2.0) * rnd(i, 31), 23.2 + (Y1 - 24.0) * rnd(i, 32)
        if abs(x) < CHEEK_X + .4 and y < 22.6:
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
    # Wide stage platform with a dark curved front fascia and a grey deck.
    a = math.degrees(math.asin(13.5 / 32.0))
    pts = arc_pts(32.0, -a, a, 48) + [(13.5, 18.0), (-13.5, 18.0)]
    C.prism('Stage platform', pts, 'z', TOP - .03, STAGE - .04, 'dark', 'stage')
    a2 = math.degrees(math.asin(13.43 / 31.93))
    C.prism('Stage deck', arc_pts(31.93, -a2, a2, 48) + [(13.43, 17.93), (-13.43, 17.93)], 'z', STAGE - .06, STAGE, 'deck', 'stage')
    b = Batch()
    for s in (1, -1):                                                  # side steps down to the terrace
        b.box('concrete', s * 13.69, 14.6, (TOP + STAGE - RISE) / 2 - .01, .38, 1.6, STAGE - RISE - TOP + .02)
    # Pavilion: back wall and returns (dark carriers) clad in slats, under a deep flat roof slab.
    zc0, zc1 = STAGE - .02, ROOF_Z + .02
    C.box('Pavilion back wall', (0.0, 17.55, (zc0 + zc1) / 2), (21.6, .3, zc1 - zc0), 'dark', 'pavilion', 0)
    C.box('Pavilion west return', (-10.65, 15.45, (zc0 + zc1) / 2), (.3, 4.1, zc1 - zc0), 'dark', 'pavilion', 0)
    f = C.Face((10.8, 17.45, STAGE), (0, -1, 0), (-1, 0, 0), 'Pavilion east return')
    door = hole('Backstage door', 2.0, 0.0, 1.0, 2.2)
    f.wall('Pavilion east return', 0.0, 4.05, -.02, ROOF_Z - STAGE + .02, depth=.3, role='dark', holes=[door])
    f.door('Backstage door', 2.0, 0.0, 1.0, 2.2, role='timber3', panels=3)
    C.box('Pavilion roof slab', (0.0, 15.4, ROOF_Z + .18), (22.9, 5.3, .36), 'dark', 'pavilion', 0)
    C.box('Pavilion roof membrane', (0.0, 15.4, ROOF_Z + .37), (22.7, 5.1, .03), 'roof', 'pavilion', 0)
    z0, z1 = STAGE - .01, ROOF_Z + .01
    slats(b, (-10.5, 17.4), (1, 0), (0, -1), 21.0, z0, z1, seed=1)                     # stage face of the back wall
    slats(b, (-10.8, 17.7), (1, 0), (0, 1), 21.6, z0, z1, seed=5, wide=True)           # rear face
    slats(b, (10.8, 17.7), (0, -1), (1, 0), 4.3, z0, z1, skip=[(2.25 - .62, 2.25 + .62)], seed=9)
    slats(b, (10.5, 17.4), (0, -1), (-1, 0), 4.0, z0, z1, skip=[(1.95 - .62, 1.95 + .62)], seed=13)
    slats(b, (-10.8, 13.4), (0, 1), (-1, 0), 4.3, z0, z1, seed=17)
    slats(b, (-10.5, 13.4), (0, 1), (1, 0), 4.0, z0, z1, seed=21)
    for s in (1, -1):
        b.box('timber3', s * 10.65, 13.37, (z0 + z1) / 2, .36, .08, z1 - z0)              # end caps of the returns
        b.box('dark', s * 8.6, 17.13, STAGE + 3.4, .62, .42, .95)                         # loudspeakers
        b.box('trim', s * 8.6, 16.905, STAGE + 3.4, .5, .02, .8)
        b.box('hardware', s * 8.6, 17.3, STAGE + 3.95, .08, .3, .08)
    b.flush('pavilion')
    # Floodlight masts with stacked lamp heads facing the stage and the plaza, standing in the high beds.
    b = Batch()
    for s in (1, -1):
        x, y = s * 16.1, 16.0
        b.box('concrete', x, y, H_HI + .1, .7, .7, .3)
        C.rod('Floodlight mast', (x, y, H_HI + .2), (x, y, 12.6), .09, 'hardware', 'masts', 12)
        b.box('hardware', x, y, 12.62, .24, .24, .06)
        for k in range(6):
            z = 7.6 + k * .85
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
        for i, (x, y, z, h, sp) in enumerate(((19.5, 15.5, H_HI, 9.5, 3.0), (26.0, 19.5, H_HI, 10.0, 3.3), (17.8, 20.6, H_HI, 8.5, 2.6),
                                             (32.0, 14.0, H_HI, 9.0, 3.0), (31.0, -2.0, H_LO, 8.0, 2.8), (26.5, -3.5, H_LO, 7.0, 2.4))):
            park_tree(s * (x + .4 * (s < 0)), y - .5 * (s < 0), z, h, sp, i * 1.7 + (s < 0) * .9)
    for i, (x, y) in enumerate(((-32.0, 28.5), (-26.5, 30.0), (-21.0, 28.0), (21.5, 28.5), (27.0, 30.0), (32.0, 28.0),
                                (-9.0, 30.0), (9.5, 29.5))):
        park_tree(x, y, .03, 9.5, 3.0, 3.1 + i, detail=1, crowns=4)
    for i, x in enumerate((-38.9, 38.9)):
        park_tree(x, -22.0, .03, 7.0, 2.0, 7.3 + i, detail=1, crowns=4)


def build():
    plaza()
    bowl()
    beds()
    stage()
    trees()
    C.CONTACTS.append(dict(name='Market and event plaza with a seating bowl, stage pavilion and meadow beds', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(-30, -42, 45), fill=(40, -22, 30), rear=(-18, 50, 35), target=(0, 4, 1.5), gain=3.2)
