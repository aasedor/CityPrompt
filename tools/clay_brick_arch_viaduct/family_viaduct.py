"""Victorian brick rail viaduct, authored from the locked catalogue views of
rail_transit_viaduct / variant_0 (Victorian Brick Arch Viaduct).

Read from the pixels (the top view governs the plan): a long straight run of semicircular brick arches carrying
two ballasted tracks, a red-and-white train on the east track. Massive brick piers between the arches with flat
pilasters that rise through the parapet as capped pier blocks; a stone impost band at the springing, a stone
string course at deck level, a heavy brick parapet with stone coping. The arches on the street (east) side hold
glazed timber shopfronts with dark fascia signs, a few closed by grey roller shutters; the garden (west) side
shows blind arches. Along the east side a wide stone-flagged pavement with bollards, planters and cafe tables,
then a cobbled street, a narrow pavement and a terrace of brick houses with slate roofs; brick terraces with
gardens behind the viaduct to the west.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-brick-arch-viaduct'
NA, SPAN, PIER, END = 10, 6.0, 2.2, 3.0          # arches, clear span, pier width, end abutments (along y)
LEN = 2 * END + NA * SPAN + (NA - 1) * PIER       # 85.8 m modelled run
VX = 5.0                                         # half-width of the viaduct (outer faces at x = +-VX)
TW = 1.0                                         # face wall (arch ring) depth
SPRING, CROWN = 4.2, 7.2                         # springing and crown of the arches
DECK, PAR = 8.4, 9.8                             # deck top (under the ballast) and parapet top
PAVE, STREET, FAR = 10.0, 17.0, 19.5              # east pavement edge, street east edge, far pavement edge (x)
X0, X1, Y0, Y1 = -VX, VX, -LEN / 2, LEN / 2
T = .3
EPS = .002
PALETTE = dict(wall=(.50, .30, .20), brick=(.50, .30, .20), arch=(.56, .34, .23), joint=(.62, .56, .48), stone=(.70, .66, .58),
    trim=(.30, .22, .15), frame=(.18, .16, .14), glass=(.22, .26, .28), interior=(.82, .72, .58), floor=(.50, .40, .30),
    sign=(.16, .17, .19), shutter=(.46, .47, .48), ballast=(.40, .38, .36), timber=(.36, .26, .18), hardware=(.10, .10, .11),
    red=(.62, .10, .10), white=(.92, .92, .90), pale=(.86, .86, .84), dark=(.10, .10, .11), roof=(.24, .25, .27),
    setts=(.30, .29, .28), settjoint=(.46, .44, .40), paving=(.62, .60, .56), concrete=(.66, .65, .62), asphalt=(.28, .28, .29),
    planting=(.30, .44, .20), tree=(.28, .44, .18), soil=(.24, .18, .12), pot=(.60, .34, .22), grass=(.40, .52, .26),
    terrace=(.70, .58, .40), terrace2=(.56, .36, .26), sand=(.66, .60, .50), blue=(.20, .30, .40))


def manifest(version):
    h = PAR + 4.0
    w, d = 60.0, LEN
    yc = Y0 + END + SPAN / 2                     # first arch centre
    pitch = SPAN + PIER
    cams = G.camera_roster(w, d, h, [
        ('facade_close', (13.0, yc + 3 * pitch, 3.8), (VX, yc + 3 * pitch, 4.2), 40),
        ('architecture_close', (11.5, yc + 5 * pitch + 6.0, 7.5), (VX + .2, yc + 5 * pitch + pitch / 2, 7.4), 40),
        ('glass_close', (9.0, yc + 4 * pitch, 2.2), (VX, yc + 4 * pitch, 2.6), 40),
        ('arch_shopfront', (12.5, yc + 6 * pitch - 2.0, 2.8), (VX, yc + 6 * pitch, 3.8), 40),
        ('pier_pilasters', (8.8, yc + 2 * pitch - 7.0, 1.7), (VX + .3, yc + 2 * pitch + 2.0, 4.6), 35),
        ('track_ballast', (1.0, Y0 + 6.0, 11.0), (0.0, 0.0, DECK + .3), 40),
        ('parapet_coping', (8.5, -12.0, 12.2), (VX, -2.0, PAR), 40),
        ('train_cars', (15.0, 14.0, 14.0), (1.8, 2.0, 10.8), 40),
        ('cobbled_street', (13.5, Y0 + 2.0, 1.7), (13.0, 10.0, 1.4), 35),
        ('rear_north', (2.0, Y1 + 30.0, 15.0), (0.0, Y1 - 6.0, 6.0), 40)])
    for c in cams:
        if c['name'] == 'front':                 # the locked front: on the cobbles to the north-east, the arches receding south-west
            c.update(location=(13.5, 16.0, 1.6), target=(3.0, -12.0, 9.0), lens=26, whole=False)
        elif c['name'] == 'front_corner':        # the locked oblique: high over the south end, looking north along the run
            c.update(location=(-16.0, Y0 - 22.0, 30.0), target=(6.0, Y0 + 30.0, 3.0), lens=32, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(42.0, Y0 - 30.0, 48.0), target=(2.0, -4.0, 4.0), lens=32, whole=False)
        elif c['name'] == 'top':                 # the locked top is a steep oblique from the south-west
            c.update(location=(-8.0, -16.0, 36.0), target=(6.0, 10.0, 2.0), lens=30, whole=False)
        elif c['name'] == 'left_side':           # over the west terraces, which would hide the viaduct from the ground
            c.update(location=(-48.0, -6.0, 30.0), target=(0.0, 0.0, 5.0), lens=32, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(48.0, 6.0, 28.0), target=(2.0, 0.0, 5.0), lens=32, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(-6.0, Y1 + 46.0, 26.0), target=(2.0, Y1 - 24.0, 5.0), lens=32, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(40.0, Y1 + 36.0, 34.0), target=(2.0, 6.0, 4.0), lens=32, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='rail_transit_viaduct/variant_0 (Victorian Brick Arch Viaduct)',
        measurement_contract=dict(dimensions_m=dict(width=2 * VX, depth=LEN, height=h),
            observed_storeys=0, storey_programme='street option: a rail viaduct with shop units in its arches; terraces are context',
            plan=f'{2 * VX:.0f} m wide brick viaduct, {LEN:.1f} m modelled run of {NA} arches (top view), a 5 m flagged pavement and a 7 m cobbled street on its east side',
            facade='red-brown brick arches and piers with pilasters, stone impost band, string course and coping; glazed timber shopfronts with fascia signs; blind arches on the west',
            section_m=dict(viaduct=[-VX, VX], pavement=[VX, PAVE], street=[PAVE, STREET], far_pavement=[STREET, FAR]),
            levels_m=[0.0, SPRING, CROWN, DECK, PAR], inferred='the run is cut at both ends; the shop interiors and the west gardens are assumptions'),
        roof_contract=dict(type='open street option; ballasted twin-track deck inside the parapets', datum_m=DECK, crowns_m=[PAR]),
        identity_contract=dict(owner='long brick arch viaduct with pilastered piers, glazed shopfronts in the arches, coped parapet, twin tracks and a train on top, cobbled street alongside'),
        material_contract=dict(profile='source-palette clay: red-brown brick with joints, pale stone dressings, dark timber shopfronts and fascias, grey shutters, ballast and timber sleepers, red-and-white train, grey setts and pale flags', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='shops and workshops in the arches, pavement and street', upper='rail deck'),
        street_contract=dict(kind='fixed_native_section', width_m=PAVE - (-VX), axis='y', junction_finish='setts',
                             bands=['viaduct', 'flagged_pavement', 'cobbled_street', 'far_pavement']),
        contact_contract=['Street and pavements at grade', 'Piers and face walls from grade', 'Deck on the arches, ballast and tracks on the deck', 'Shopfronts inside the arch openings'],
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
# ---- Victorian brick rail viaduct ----

def arch_head(f, h, rise, ring=.26, segs=10, ring_role='arch', dep=None):
    """Segmental or round head on a rectangular cut: brick spandrel infill above the curve (set 1 cm back so it
    never shares a plane with the wall face) and a proud brick ring of headers over it."""
    u, w, top = h['u'], h['w'], h['z'] + h['h']
    R = (w * w / 4 + rise * rise) / (2 * rise)
    cz = top - R
    a0 = math.asin(min(1.0, (w / 2) / R))
    arc = [(u + R * math.sin(-a0 + 2 * a0 * i / segs), cz + R * math.cos(-a0 + 2 * a0 * i / segs)) for i in range(segs + 1)]
    pts = [(u - w / 2 - .06, top - rise)] + arc + [(u + w / 2 + .06, top - rise)]
    vs, fs = [], []
    for (pu, pz) in pts:
        for d in (.01, (dep or T) - .01):
            vs.append(f.p(pu, d, pz)); vs.append(f.p(pu, d, top + .06))
    for i in range(len(pts) - 1):
        a, b = 4 * i, 4 * (i + 1)
        fs += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3)]
    n = 4 * (len(pts) - 1)
    fs += [(0, 1, 3, 2), (n, n + 2, n + 3, n + 1)]
    C.mesh(f'{h["id"]} spandrel', vs, fs, 'wall', 'arches')
    vs, fs = [], []
    for (pu, pz) in arc:
        r = math.hypot(pu - u, pz - cz)
        nu, nz = (pu - u) / r, (pz - cz) / r
        for d in (-.035, .02):
            vs.append(f.p(pu, d, pz)); vs.append(f.p(pu + nu * ring, d, pz + nz * ring))
    for i in range(segs):
        a, b = 4 * i, 4 * (i + 1)
        fs += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3)]
    n = 4 * segs
    fs += [(0, 1, 3, 2), (n, n + 2, n + 3, n + 1)]
    C.mesh(f'{h["id"]} arch ring', vs, fs, ring_role, 'arches')


def courses(f, lo, hi, z0, z1, holes, course=.3, brick=.66, heads=True):
    """Brick bed joints and staggered head joints, cut round the openings (one mesh per face)."""
    G.brick_courses(f, lo + .02, hi - .02, z0, z1, holes, spacing=course)
    if not heads:
        return
    vs, fs = [], []
    for row in range(int((z1 - z0) / course)):
        zb = z0 + row * course
        u = lo + brick + (brick / 2) * (row % 2)
        while u < hi - .05:
            if not any(h['u'] - h['w'] / 2 - .5 < u < h['u'] + h['w'] / 2 + .5 and zb < h['z'] + h['h'] + .55 for h in holes):
                o = len(vs)
                vs += [f.p(u - .006, -.002, zb), f.p(u + .006, -.002, zb), f.p(u + .006, -.002, zb + course), f.p(u - .006, -.002, zb + course)]
                fs.append((o, o + 1, o + 2, o + 3))
            u += brick
    if fs:
        C.mesh(f.label + ' head joints', vs, fs, 'joint', 'brick joints')


PITCH = SPAN + PIER
ARCHES = [Y0 + END + SPAN / 2 + i * PITCH for i in range(NA)]
PIERS = [y + SPAN / 2 + PIER / 2 for y in ARCHES[:-1]]
SHUTTERED = (0, 7)                               # arches closed by grey roller shutters (oblique)
YA, YB = Y0 + .6, Y1 - .6                        # face walls run between the end walls


def pilaster(m, u, w=1.4):
    """Flat brick pilaster with a stone plinth, a narrower face strip, rising through the parapet to a capped pier."""
    m.box('wall', u, -.15, (PAR + .45) / 2, w, .3, PAR + .45)
    m.box('wall', u, -.36, (SPRING + DECK - .3) / 2 + .3, w - .5, .12, DECK - .3 - SPRING + .6)
    m.box('stone', u, -.21, .3, w + .16, .42, .6)
    m.box('stone', u, -.19, PAR + .51, w + .16, .48, .12)


def east_face():
    """Street face: arch openings with shopfronts or shutters, pilasters, impost blocks, string course and coping."""
    f = C.Face((VX, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    hs = [hole(f'arch {i}', y, 0.0, SPAN, CROWN, kind='shopfront') for i, y in enumerate(ARCHES)]
    f.wall('east face', YA, YB - EPS, 0.0, PAR, depth=TW, role='wall', holes=hs)
    courses(f, YA, YB, .62, PAR - .05, hs)
    m = Merge(f)
    for i, h in enumerate(hs):
        u = h['u']
        register(f, h, .6, 'shopfront', 'shop')
        m.box('sign', u, .45, 3.75, SPAN - .02, .12, .6)                                     # fascia sign board
        m.box('glass', u, .62, (4.06 + CROWN) / 2, SPAN - .06, .02, CROWN - 4.06)               # glazed lunette
        for k in (-1, 0, 1):
            m.box('trim', u + k * SPAN / 4, .6, (4.06 + CROWN) / 2, .1, .14, CROWN - 4.06)
        m.box('trim', u, .6, 5.6, SPAN - .04, .14, .1)
        if i in SHUTTERED:
            m.box('shutter', u, .5, 1.72, SPAN - .04, .1, 3.44)
            for k in range(22):
                m.box('dark', u, .44, .2 + k * .15, SPAN - .1, .02, .02)
            m.box('shutter', u, .45, 3.3, SPAN - .02, .2, .3)                                    # shutter box
        else:
            m.box('glass', u, .62, 1.94, SPAN - .06, .02, 3.0)                                   # shopfront glazing over a stall riser
            m.box('trim', u, .6, .22, SPAN - .04, .14, .44)
            for k in (-2, -1, 0, 1, 2):
                m.box('trim', u + k * SPAN / 4 + (.05 if k == -2 else -.05 if k == 2 else 0), .6, 1.72, .1, .14, 3.44)
            m.box('trim', u, .6, 3.4, SPAN - .04, .14, .1)                                       # transom under the fascia
            m.box('trim', u + SPAN / 8, .58, 1.3, 1.36, .12, 2.6)                                # glazed door
            m.box('glass', u + SPAN / 8, .52, 1.55, .9, .02, 1.6)
        arch_head(f, h, SPAN / 2, ring=.48, segs=14, ring_role='arch', dep=2 * VX - TW + .02)
    for u in PIERS + [YA + .8, YB - .8]:
        pilaster(m, u)
    for u in PIERS:                                                                         # stone imposts at the springing
        m.box('stone', u, -.1, SPRING - .12, PIER - .04, .2, .24)
    m.box('stone', 0.0, -.12, DECK - .1, Y1 - Y0, .24, .24)                                 # deck string course, end to end
    m.box('stone', 0.0, (TW - .12) / 2, PAR + .07, Y1 - Y0, TW + .12, .14)                   # parapet coping
    m.flush('east')


def west_face():
    """Garden face: blind arches (a shallow recess under each arch), pilasters, string course and coping."""
    f = C.Face((-VX, 0, 0), (0, -1, 0), (1, 0, 0), 'west')
    hs = [hole(f'west blind arch {i}', -y, 0.0, SPAN, CROWN, kind='blind arch') for i, y in enumerate(ARCHES)]
    f.wall('west face', -YB, -YA - EPS, 0.0, PAR, depth=TW, role='wall', holes=hs)
    courses(f, -YB, -YA, .62, PAR - .05, hs, heads=False)
    m = Merge(f)
    for h in hs:
        m.box('wall', h['u'], (.35 + TW) / 2, CROWN / 2, SPAN + .02, TW - .35, CROWN)          # recess infill
        arch_head(f, h, SPAN / 2, ring=.45, segs=14, ring_role='arch', dep=.38)
        m.box('dark', h['u'] + 1.2, .33, 1.2, 1.0, .04, 2.4)                                   # a back door into the arch
    for u in [-p for p in PIERS] + [-YB + .8, -YA - .8]:
        pilaster(m, u)
    m.box('stone', 0.0, -.12, DECK - .1, Y1 - Y0, .24, .24)
    m.box('stone', 0.0, (TW - .12) / 2, PAR + .07, Y1 - Y0, TW + .12, .14)
    m.flush('west')


def end_wall(label, y, sgn):
    """End of the modelled run: a brick end wall with a blind arch, corner pilasters and coping."""
    f = C.Face((0, y, 0), (sgn, 0, 0), (0, sgn, 0), label)
    h = hole(f'{label} blind arch', 0.0, 0.0, 5.0, 6.4, kind='blind arch')
    f.wall(f'{label} wall', -VX, VX - EPS, 0.0, PAR, depth=.6, role='wall', holes=[h])
    courses(f, -VX, VX, .62, PAR - .05, [h], heads=False)
    m = Merge(f)
    m.box('wall', 0.0, (.3 + .6) / 2, 3.2, 5.02, .3, 6.4)
    arch_head(f, h, 2.5, ring=.45, segs=12, ring_role='arch', dep=.33)
    for u in (-VX + .7, VX - .7):
        pilaster(m, u, w=1.36)
    m.box('stone', 0.0, -.12, DECK - .1, 2 * VX + .48, .24, .24)                         # wraps the corners of the side courses
    m.box('stone', 0.0, .3, PAR + .08, 2 * VX + .28, .84, .14)                              # 1 cm proud of the side copings
    m.flush(label)


def body_and_deck():
    xi = VX - TW
    b = Batch()
    for u in PIERS:
        b.box('wall', 0.0, u, CROWN / 2, 2 * xi, PIER, CROWN)
    for ya, yb in ((YA, ARCHES[0] - SPAN / 2), (ARCHES[-1] + SPAN / 2, YB)):
        b.box('wall', 0.0, (ya + yb) / 2, CROWN / 2, 2 * xi, yb - ya, CROWN)
    b.box('concrete', 0.0, 0.0, (CROWN + DECK) / 2, 2 * xi, YB - YA, DECK - CROWN)
    b.flush('viaduct body')
    # Shop interiors in the vaults: floor, back shelving, a counter, warm light.
    b = Batch()
    for i, y in enumerate(ARCHES):
        b.box('floor', (-xi + VX - .55) / 2, y, .04, VX - .55 + xi, SPAN - .02, .08)
        if i not in SHUTTERED:
            for k in range(4):
                b.box('interior', -xi + .3, y, .5 + k * .6, .5, SPAN - 1.2, .06)
            b.box('timber', 1.2, y - 1.2, .55, .7, 2.4, 1.1)
        C.qa_room_light(f'Arch {i} shop', (1.2, y, 2.6), 40, 2.5)
    b.flush('shops')
    # Twin ballasted tracks, sleepers and rails.
    b = Batch()
    b.box('ballast', 0.0, 0.0, DECK + .14, 2 * xi - .6, YB - YA, .28)
    zs = DECK + .28
    n = int((YB - YA - .6) / .7)
    for xt in (-1.8, 1.8):
        for k in range(n):
            b.box('timber', xt, YA + .5 + k * .7, zs + .06, 2.5, .24, .12)
        for s in (-1, 1):
            b.box('hardware', xt + s * .72, 0.0, zs + .2, .07, YB - YA - .1, .16)
    b.flush('tracks')


def train():
    """A red-and-white train of three cars on the east track."""
    xt, z0 = 1.8, DECK + .28 + .28
    b = Batch()
    y = -10.0
    for k in range(3):
        L = 17.0
        y0, y1 = y, y + L
        yc = (y0 + y1) / 2
        for yb in (y0 + 2.2, y1 - 2.2):
            b.box('dark', xt, yb, z0 + .25, 2.2, 2.4, .5)
        b.box('red', xt, yc, z0 + .5 + .55, 2.8, L, 1.1)
        b.box('white', xt, yc, z0 + 1.6 + 1.0, 2.8, L, 2.0)
        b.box('red', xt, yc, z0 + 3.6 + .15, 2.8, L, .3)
        b.box('pale', xt, yc, z0 + 3.9 + .15, 2.5, L - .4, .3)
        for s in (-1, 1):
            b.box('glass', xt + s * 1.415, yc, z0 + 2.4, .02, L - 2.0, 1.0)
            for j in range(1, 6):
                b.box('white', xt + s * 1.43, y0 + L * j / 6, z0 + 2.4, .02, .18, 1.02)
        y = y1 + .7
    b.box('dark', xt, -10.0 - .015, z0 + 2.5, 2.2, .02, 1.2)                                 # cab windscreen
    b.box('pale', xt, -10.0 - .015, z0 + 1.0, 2.0, .02, .3)
    b.flush('train')


def street():
    b = Batch()
    ya, yb = Y0 - 8.0, Y1 + 8.0
    C.box('Flagged pavement', ((VX + PAVE) / 2, 0.0, .07), (PAVE - VX, yb - ya, .14), 'paving', 'street', 0)
    C.box('Kerb', (PAVE + .1, 0.0, .07), (.2, yb - ya, .14), 'stone', 'street', 0)
    C.box('Cobbled street', ((PAVE + .2 + STREET) / 2, 0.0, .03), (STREET - PAVE - .2, yb - ya, .06), 'setts', 'street', 0)
    C.box('Far kerb', (STREET + .1, 0.0, .07), (.2, yb - ya, .14), 'stone', 'street', 0)
    C.box('Far pavement', ((STREET + .2 + FAR) / 2, 0.0, .07), (FAR - STREET - .2, yb - ya, .14), 'paving', 'street', 0)
    C.box('West gardens', ((-VX - 13.0) / 2, 0.0, .03), (13.0 - VX, yb - ya, .06), 'grass', 'gardens', 0)
    k = 0
    y = ya + .3
    while y < yb - .2:                                                                     # flags and setts courses
        b.box('settjoint', (PAVE + .2 + STREET) / 2, y, .061, STREET - PAVE - .2, .04, .004)
        if k % 4 == 0:
            b.box('settjoint', (VX + PAVE) / 2, y, .141, PAVE - VX - .02, .03, .004)
            b.box('settjoint', (STREET + .2 + FAR) / 2, y, .141, FAR - STREET - .22, .03, .004)
        y += .3
        k += 1
    for x in (VX + 1.6, VX + 3.3):
        b.box('settjoint', x, 0.0, .141, .03, yb - ya - .02, .004)
    for x in (PAVE + 2.4, PAVE + 4.6):
        b.box('settjoint', x, 0.0, .061, .04, yb - ya - .02, .004)
    for k in range(int((yb - ya) / 3.2)):                                                  # bollards at the kerb
        b.box('hardware', PAVE - .35, ya + 1.6 + k * 3.2, .14 + .5, .14, .14, 1.0)
        b.box('hardware', PAVE - .35, ya + 1.6 + k * 3.2, 1.17, .2, .2, .06)
    for i in (3, 4):                                                                       # cafe tables in front of two arches
        for j in (-1, 1):
            x, y = VX + 2.4, ARCHES[i] + j * 1.6
            b.box('hardware', x, y, .14 + .36, .06, .06, .72)
            b.box('white', x, y, .14 + .74, .7, .7, .04)
            for s in (-1, 1):
                b.box('timber', x + s * .55, y, .14 + .23, .4, .4, .46)
    b.flush('street furniture')
    for i in (2, 3, 5, 6, 8):                                                              # planters with shrubs by the piers
        y = PIERS[i - 1] if i - 1 < len(PIERS) else PIERS[-1]
        b = Batch()
        b.box('pot', VX + .9, y, .14 + .35, .7, .7, .7)
        b.flush(f'planter {i}')
        A.foliage(f'Planter shrub {i}', (VX + .9, y, 1.3), (.5, .5, .55), role='planting', detail=2)
    for y in (-30.0, -12.0, 6.0, 24.0, 40.0):
        street_tree(STREET + 1.2, y, z=.14, height=8.0, spread=2.2)


def terraces():
    """Brick terrace houses as context: slate roofs, chimneys on the party walls, framed sash windows."""
    for side, xf, sgn, role in (('East', FAR, 1, 'terrace'), ('West', -13.0 - 9.0, -1, 'terrace2')):
        ya, yb = Y0 - 8.0, Y1 + 8.0
        n = int((yb - ya) / 5.6)
        b = Batch()
        x0, x1 = (FAR, FAR + 9.0) if sgn > 0 else (-22.0, -13.0)
        h = 8.4
        C.box(f'{side} terrace', ((x0 + x1) / 2, (ya + yb) / 2, h / 2), (x1 - x0, yb - ya, h), role, 'context', 0)
        pitched_roof(f'{side} terrace roof', x0, x1, ya, yb, h, 2.6, hip_w=False, hip_e=False, axis='y', ov=.25, role='roof', module='context')
        for yg in (ya + .15, yb - .15):                                                       # gable end walls under the roof plate
            gable_wall(f'{side} terrace gable {yg:+.0f}', yg, x0, x1, h - .01, 2.5, axis='y', t=.3, role=role, module='context')
        for i in range(n):
            y0, y1 = ya + i * 5.6, ya + (i + 1) * 5.6
            if i:
                chimney(b, (x0 + x1) / 2, y0, h + 1.6, h + 3.4, w=.9, d=.6, pots=3)
            fx = x0 - .02 if sgn > 0 else x1 + .02                                         # the face towards the viaduct
            dx = -1 if sgn > 0 else 1
            for k, z in enumerate((1.0, 4.2)):
                for j, du in enumerate((-1.3, 1.3)):
                    yy = (y0 + y1) / 2 + du
                    if k == 0 and j == 0 and sgn > 0:
                        b.box('dark', fx + dx * .02, yy, 1.25, .04, 1.0, 2.3)              # front door
                        b.box('pale', fx + dx * .06, yy, 2.48, .1, 1.2, .14)
                        continue
                    b.box('glass', fx + dx * .01, yy, z + .95, .02, .9, 1.7)
                    for s in (-1, 1):
                        b.box('white', fx + dx * .05, yy + s * .5, z + .95, .08, .1, 1.9)
                    b.box('white', fx + dx * .05, yy, z + 1.85, .08, 1.1, .1)
                    b.box('white', fx + dx * .05, yy, z + .95, .06, .9, .05)
                    b.box('stone', fx + dx * .09, yy, z - .02, .16, 1.2, .1)
        b.flush(f'{side} terrace windows')


def build():
    east_face()
    west_face()
    end_wall('south end', Y0, 1)
    end_wall('north end', Y1, -1)
    body_and_deck()
    train()
    street()
    terraces()
    C.CONTACTS.append(dict(name='Brick viaduct from grade: piers, face walls and end walls; deck on the arches; ballast and tracks on the deck; shopfronts in the arches', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(40, -30, 45), fill=(-40, -20, 30), rear=(-15, 40, 30), target=(2.0, 0, 5.0), gain=3.4)
