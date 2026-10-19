"""Heritage stone arch road bridge, authored from the locked catalogue views of
urban_vehicular_bridge / variant_0 (Heritage Stone Arch).

Read from the pixels (the top view governs the plan): a city road crossing a river that runs north-south between high
stone quays. Three semicircular arches of cut limestone on two piers with pointed cutwaters; the cutwaters rise as
pilaster buttresses to the deck, where the balustrade breaks forward into pedestals carrying ornate double-lantern
lamp standards; voussoired arch rings, coursed ashlar spandrel walls, a dentilled cornice. On the deck four traffic
lanes with dashed markings between paved footways and stone balustrades with pedestals; the balustrades turn the
corners at the bridge ends in curved parapets onto the quays. Old town blocks with orange hipped roofs line the
quays, a red double-decker bus, a car and a van cross the bridge.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-stone-arch-road-bridge'
SPAN, PIER, NA = 16.0, 3.5, 3                   # clear span of each semicircular arch, pier thickness, arch count
QX = (NA * SPAN + (NA - 1) * PIER) / 2          # quay faces (x), 27.5 m: the bridge runs east-west over the river
X0, X1, Y0, Y1 = -QX, QX, -9.0, 9.0             # the bridge itself: 55 m long, 18 m wide
ZS, RT = 1.2, .9                                # springing above the water, arch ring depth
DECK = 11.0                                     # road surface and quay street level
ZC = 7.0                                        # top of the cutwaters
HW = 8.9                                        # half-width of the spandrel faces
T = .3
EPS = .002
PALETTE = dict(water=(.10, .17, .18), stone=(.72, .67, .57), arch=(.65, .60, .50), joint=(.52, .48, .41),
    quay=(.60, .57, .51), asphalt=(.25, .25, .26), white=(.92, .92, .90), paving=(.66, .63, .58), kerb=(.74, .72, .68),
    hardware=(.13, .15, .14), pale=(.96, .88, .62), glass=(.20, .24, .27), wall=(.84, .74, .58), facade2=(.86, .81, .71),
    brick=(.64, .40, .30), roof=(.68, .34, .20), red=(.72, .10, .10), van=(.42, .38, .26), car=(.16, .17, .19),
    dark=(.10, .10, .11), interior=(.84, .80, .74), floor=(.58, .48, .38), trim=(.92, .91, .88), planting=(.30, .44, .20),
    tree=(.28, .44, .18), timber=(.46, .34, .22), soil=(.22, .16, .10), concrete=(.70, .69, .66), sand=(.70, .66, .58),
    blue=(.20, .30, .40), pot=(.60, .34, .22))


def manifest(version):
    h = 18.0
    cams = G.camera_roster(X1 - X0, Y1 - Y0, h, [
        ('facade_close', (0.0, -42.0, 7.0), (0.0, -HW, 6.0), 40),
        ('architecture_close', (-15.0, -23.0, 13.0), (-9.75, -9.6, 10.5), 40),
        ('glass_close', (6.5, -13.5, 15.5), (9.75, -9.1, 15.9), 40),
        ('arch_spandrel', (-19.5, -31.0, 5.0), (-19.5, -HW, 6.0), 40),
        ('cutwater_pier', (-3.0, -25.0, 3.0), (-9.75, -10.6, 3.5), 40),
        ('balustrade', (-3.0, -7.6, 12.8), (8.0, -8.65, 11.8), 40),
        ('lamp_standard', (16.0, -4.0, 14.0), (9.75, -9.15, 15.4), 35),
        ('roadway_deck', (-25.0, 0.5, 14.0), (10.0, 0.0, 11.0), 35),
        ('river_underside', (-19.5, -27.0, 1.6), (-19.5, 0.0, 5.0), 35),
        ('rear_north', (22.0, 42.0, 7.0), (0.0, HW, 6.0), 35)])
    for c in cams:
        if c['name'] == 'front':                     # the locked front: on the quay at the east end, south side, looking west
            c.update(location=(28.9, -12.6, DECK + .15 + 2.6), target=(-10.0, -8.4, 6.0), lens=24, whole=False)
        elif c['name'] == 'front_corner':            # the locked oblique: high over the west bank, along the bridge, arches on the right
            c.update(location=(-38.0, -17.0, 30.0), target=(12.0, 2.0, 6.0), lens=30, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(48.0, -62.0, 52.0), target=(0.0, 0.0, 8.0), lens=30, whole=False)
        elif c['name'] == 'top':
            c.update(location=(0.0, 0.0, 160.0), target=(0.0, .001, 0.0), ortho_scale=130.0, whole=False)
        elif c['name'] == 'left_side':               # along the road from the west approach
            c.update(location=(-80.0, 1.5, DECK + 3.5), target=(0.0, 0.0, DECK + .5), lens=35, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(80.0, -1.5, DECK + 3.5), target=(0.0, 0.0, DECK + .5), lens=35, whole=False)
        elif c['name'] == 'rear':                    # the north elevation from over the river
            c.update(location=(0.0, 58.0, 8.0), target=(0.0, HW, 6.0), lens=35, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(42.0, 52.0, 26.0), target=(0.0, 0.0, 7.0), lens=35, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='urban_vehicular_bridge/variant_0 (Heritage Stone Arch)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=0, storey_programme='bridge: a four-lane road with footways over a river; the quays and town blocks are context',
            plan='55 x 18 m three-arch bridge (top view) between quays 55 m apart, the road continuing east and west, quay roads north-south',
            section_m=dict(carriageway=[-6.0, 6.0], footways=[[-8.4, -6.0], [6.0, 8.4]], balustrades=[-8.65, 8.65]),
            facade='three semicircular 16 m cut-stone arches with voussoired rings, coursed ashlar spandrels, pointed cutwaters rising as pilasters, dentilled cornice, stone balustrades with pedestals, double-lantern lamp standards',
            levels_m=[0.0, ZS, ZS + SPAN / 2, DECK], inferred='the river bed, foundations and the town blocks beyond the quays are context; the deck build-up is an assumption'),
        roof_contract=dict(type='open road deck; hipped tile roofs on the context blocks', datum_m=DECK, crowns_m=[h]),
        identity_contract=dict(owner='three-arch cut-stone road bridge with cutwaters, cornice, balustrades and double-lantern lamps over a river between quays'),
        material_contract=dict(profile='source-palette clay: warm limestone with darker voussoirs and joints, grey asphalt with white lane marks, pale paving, dark iron lamps with warm lanterns, dark river water, orange roofs', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='four traffic lanes, two footways'),
        street_contract=dict(kind='fixed_native_section', width_m=Y1 - Y0, axis='x', junction_finish='asphalt',
                             bands=['balustrade', 'footway', 'carriageway', 'footway', 'balustrade']),
        contact_contract=['River surface at grade zero', 'Piers and cutwaters from the water', 'Arches spring from the piers and the quays', 'Deck on the spandrels, road on the quays'],
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


# ---- Heritage stone arch road bridge ----

R = SPAN / 2
CENTRES = [-QX + R + k * (SPAN + PIER) for k in range(NA)]               # arch centres along x
PIERS = [(c + R, c + R + PIER) for c in CENTRES[:-1]]                     # pier faces along x
BANK = 75.0                                                                # the modelled banks reach x = +-75
RIVER_Y = 60.0                                                             # and the river runs y = +-60
FOOT = 11.15                                                               # footway and quay paving level
APR = 1.8                                                                  # radius of the curved corner parapets


def hexa(b, role, corners):
    """Add a closed hexahedron (eight corners: one end ring of four, then the other) to a Batch."""
    b._hex(role, corners)


def bridge_body():
    """One stone mass between the quays: its outline in x-z is the deck underside, the three semicircular intrados
    and the pier shafts down to the water, extruded across the full width (the barrel vaults are its underside)."""
    pts = [(-QX, DECK - .04), (-QX, ZS)]
    for k, c in enumerate(CENTRES):
        n = 28
        pts += [(c + R * math.cos(math.pi - math.pi * i / n), ZS + R * math.sin(math.pi - math.pi * i / n)) for i in range(1, n)]
        if k < NA - 1:
            x0, x1 = PIERS[k]
            pts += [(x0, ZS), (x0, 0.0), (x1, 0.0), (x1, ZS)]
    pts += [(QX, ZS), (QX, DECK - .04)]
    C.prism('Bridge body', pts, 'y', -HW, HW, 'stone', 'bridge')


def arch_rings():
    """Voussoired arch rings standing proud of both spandrel faces, alternate stones a shade darker, a keystone."""
    b = Batch()
    n = 27
    for c in CENTRES:
        for s in (-1, 1):
            ya, yb = (-HW - .18, -HW + .04) if s < 0 else (HW - .04, HW + .18)
            for k in range(n):
                ta, tb = math.pi - math.pi * k / n, math.pi - math.pi * (k + 1) / n
                r0, r1 = R - .04, R + RT + (.3 if k == n // 2 else 0.0)
                yy = (ya - (.06 if k == n // 2 and s < 0 else 0.0), yb + (.06 if k == n // 2 and s > 0 else 0.0))
                ring = lambda r, t, y: (c + r * math.cos(t), y, ZS + r * math.sin(t))
                hexa(b, 'arch' if k % 2 else 'stone', [ring(r0, ta, yy[0]), ring(r0, tb, yy[0]), ring(r1, tb, yy[0]), ring(r1, ta, yy[0]),
                                                       ring(r0, ta, yy[1]), ring(r0, tb, yy[1]), ring(r1, tb, yy[1]), ring(r1, ta, yy[1])])
    b.flush('arch rings')


def solid_intervals(z, pad=.06):
    """The x intervals of spandrel wall that are solid at height z (outside the arch openings and their rings)."""
    iv = [(-QX, QX)]
    for c in CENTRES:
        dz = z - ZS
        if dz < 0:
            h = R
        elif dz < R + RT + pad:
            h = math.sqrt((R + RT + pad) ** 2 - dz * dz)
        else:
            continue
        nv = []
        for a, e in iv:
            if e <= c - h or a >= c + h:
                nv.append((a, e))
            else:
                if a < c - h:
                    nv.append((a, c - h))
                if e > c + h:
                    nv.append((c + h, e))
        iv = nv
    return [(a, e) for a, e in iv if e - a > .3]


def ashlar():
    """Coursed ashlar on both spandrel faces: bed joints every 0.6 m and staggered head joints, kept clear of the
    arch openings and rings."""
    b = Batch()
    for s in (-1, 1):
        y = s * HW
        k = 0
        z = .6
        while z < 10.2:
            for a, e in solid_intervals(z):
                b.box('joint', (a + e) / 2, y, z, e - a, .008, .03)
                u = a + .6 + (.6 if k % 2 else 0.0)
                upper = solid_intervals(z + .3)
                while u < e - .3:
                    if any(p + .05 <= u <= q - .05 for p, q in upper):
                        b.box('joint', u, y, z + .3, .03, .008, .57)
                    u += 1.2
            z += .6
            k += 1
    b.flush('ashlar')


def cutwaters():
    """Pointed cutwaters on both faces of each pier, capped with a stone hood, rising as pilaster buttresses to the
    cornice."""
    for i, (x0, x1) in enumerate(PIERS):
        xm = (x0 + x1) / 2
        for s in (-1, 1):
            poly = [(x0, s * 8.8), (x0, s * 10.3), (xm, s * 11.7), (x1, s * 10.3), (x1, s * 8.8)]
            C.prism(f'Cutwater {i} {s:+d}', poly, 'z', 0.0, ZC, 'stone', 'bridge')
            vs = [(x, y, ZC) for x, y in poly] + [(xm, s * 8.8, ZC + 1.8)]
            C.mesh(f'Cutwater hood {i} {s:+d}', vs, [(4, 3, 2, 1, 0)] + [(j, (j + 1) % 5, 5) for j in range(5)], 'arch', 'bridge')
            b = Batch()
            b.box('stone', xm, s * 9.4, (ZC - .2 + 10.70) / 2, PIER - .7, 1.2, 10.70 - ZC + .2)          # pilaster buttress (top under the corona)
            b.box('arch', xm, s * 9.42, ZC + 1.9, PIER - .5, 1.28, .22)                                  # impost band on it
            for z in (ZC + 3.1, ZC + 4.3, ZC + 5.5):                                                    # rusticated joints
                b.box('joint', xm, s * 10.0, z, PIER - .72, .03, .03)
            b.flush(f'pier pilaster {i} {s:+d}')
            C.box(f'Pier refuge {i} {s:+d}', (xm, s * 9.15, (10.70 + 12.5) / 2), (2.0, 1.7, 12.5 - 10.70), 'stone', 'bridge', 0)
            C.box(f'Pier refuge cap {i} {s:+d}', (xm, s * 9.15, 12.56), (2.16, 1.86, .12), 'arch', 'bridge', 0)


def cornice():
    b = Batch()
    for s in (-1, 1):
        b.box('stone', 0.0, s * (HW + .12), 10.375, 2 * QX, .3, .25)
        b.box('arch', 0.0, s * (HW + .2), 10.61, 2 * QX, .46, .22)
        x = -QX + .25
        while x < QX - .2:
            if all(not (lo - .1 < x < hi + .1) for lo, hi in PIERS) and all(abs(x - c) > .7 for c in CENTRES):
                b.box('stone', x, s * (HW + .06), 10.175, .22, .16, .15)
            x += .5
    b.flush('cornice')


def balustrade_run(b, x0, x1, y, posts):
    """Stone balustrade along x at y: plinth, turned balusters, rail; posts are pedestal x positions to keep clear."""
    s = 1 if y > 0 else -1
    b.box('stone', (x0 + x1) / 2, y, 11.16, x1 - x0, .52, .4)
    b.box('stone', (x0 + x1) / 2, y, 12.15, x1 - x0, .58, .18)
    x = x0 + .16
    while x < x1 - .1:
        if all(abs(x - p) > .62 for p in posts):
            b.box('stone', x, y, 11.51, .22, .22, .3)
            b.box('stone', x, y, 11.78, .12, .12, .24)
            b.box('stone', x, y, 11.98, .2, .2, .16)
        x += .32


def deck():
    """Asphalt carriageway with lane marks, raised paved footways with kerbs, balustrades with pedestals."""
    C.box('Carriageway', (0.0, 0.0, DECK - .02), (2 * QX, 12.0, .04), 'asphalt', 'deck', 0)
    b = Batch()
    for s in (-1, 1):
        b.box('paving', 0.0, s * 7.2, (DECK - .04 + FOOT) / 2, 2 * QX, 2.4, FOOT - DECK + .04)
        b.box('kerb', 0.0, s * 6.0, (DECK - .04 + FOOT + .02) / 2, 2 * QX, .2, FOOT + .02 - DECK + .04)
    marks(b, -QX, QX)
    b.flush('deck')
    posts = [-QX + .5, -23.5, -15.5, -4.0, 4.0, 15.5, 23.5, QX - .5]
    piers = [(x0 + x1) / 2 for x0, x1 in PIERS]
    b = Batch()
    xs = QX + .3 - APR                                                      # the straight runs stop where the corner curves begin
    for s in (-1, 1):
        y = s * 8.66
        stops = [(-xs + .5, piers[0] - 1.0), (piers[0] + 1.0, piers[1] - 1.0), (piers[1] + 1.0, xs - .5)]
        for a, e in stops:
            balustrade_run(b, a, e, y, posts)
        for p in posts[1:-1]:
            b.box('stone', p, y, (DECK - .04 + 12.45) / 2, .8, .8, 12.45 - DECK + .04)
            b.box('arch', p, y, 12.51, .96, .96, .12)
    b.flush('balustrades')


def marks(b, x0, x1):
    """Centre double line and dashed lane lines along x."""
    for y in (-.12, .12):
        b.box('white', (x0 + x1) / 2, y, DECK + .003, x1 - x0, .12, .006)
    x = x0 + 1.0
    while x < x1 - 2.0:
        for y in (-3.0, 3.0):
            b.box('white', x + 1.5, y, DECK + .003, 3.0, .12, .006)
        x += 6.0


def lamp(name, x, y, z0):
    """Ornate double-lantern lamp standard: plinth, fluted shaft, collar, crossarm, two lanterns and a finial."""
    b = Batch()
    b.box('hardware', x, y, z0 + .3, .5, .5, .6)
    b.box('hardware', x, y, z0 + .72, .34, .34, .24)
    b.box('hardware', x, y, z0 + 1.3, .24, .24, .16)
    b.box('hardware', x, y, z0 + 3.85, .22, .22, .14)
    b.beam('hardware', (x - .62, y, z0 + 4.0), (x + .62, y, z0 + 4.0), .08, .1)
    for dx in (-.55, .55):
        b.beam('hardware', (x, y, z0 + 3.5), (x + dx, y, z0 + 3.98), .05, .05)
        b.box('pale', x + dx, y, z0 + 4.33, .32, .32, .56)
        b.box('hardware', x + dx, y, z0 + 4.65, .44, .44, .08)
        b.box('hardware', x + dx, y, z0 + 4.77, .2, .2, .16)
        b.box('hardware', x + dx, y, z0 + 4.95, .05, .05, .2)
    b.box('hardware', x, y, z0 + 4.25, .12, .12, .5)
    b.flush(name)
    C.rod(f'{name} shaft', (x, y, z0 + .84), (x, y, z0 + 4.0), .085, 'hardware', 'lamps', 10)


def lamps():
    for x0, x1 in PIERS:
        for s in (-1, 1):
            lamp(f'Lamp pier {x0:+.0f} {s:+d}', (x0 + x1) / 2, s * 9.15, 12.62)
    for x in (-(QX + .3 - APR), QX + .3 - APR):
        for s in (-1, 1):
            lamp(f'Lamp end {x:+.0f} {s:+d}', x, s * 8.66, 12.57)


def corners():
    """At each bridge end the balustrade sweeps round a curved apron onto the quay parapet."""
    for sx in (-1, 1):
        for sy in (-1, 1):
            xs = sx * (QX + .3 - APR)                                         # where the curve starts on the bridge line
            cy = sy * (8.66 + APR)
            ang = [math.pi / 2 * i / 10 for i in range(11)]
            path = [(xs + sx * APR * math.sin(a), cy - sy * APR * math.cos(a)) for a in ang]
            # Apron: the curved stone platform under the sweep, from the water to the footway, inside the river only.
            Ro = APR + .35
            outer = []
            for a in [math.pi / 2 * i / 20 for i in range(21)]:
                px, py = xs + sx * Ro * math.sin(a), cy - sy * Ro * math.cos(a)
                if sx * px <= QX - .01 and abs(py) > HW + .05:
                    outer.append((px, py))
            ycut = cy - sy * math.sqrt(max(0.0, Ro * Ro - (QX - abs(xs)) ** 2))       # the outer curve meets the quay face
            poly = [(xs, sy * HW)] + outer + [(sx * QX, ycut), (sx * QX, sy * HW)]
            C.prism(f'Corner apron {sx:+d}{sy:+d}', poly, 'z', 0.0, DECK - .04, 'quay', 'bridge')
            C.prism(f'Corner apron paving {sx:+d}{sy:+d}', poly, 'z', DECK - .04, FOOT, 'paving', 'bridge')
            b = Batch()
            for (ax, ay), (bx, by) in zip(path, path[1:]):
                b.beam('stone', (ax, ay, FOOT + .42), (bx, by, FOOT + .42), .5, .84, ext=.02)
                b.beam('arch', (ax, ay, FOOT + .9), (bx, by, FOOT + .9), .62, .12, ext=.02)
            b.box('paving', (xs + sx * QX) / 2, sy * (8.4 + HW) / 2, (DECK - .04 + FOOT) / 2, abs(sx * QX - xs), HW - 8.4, FOOT - DECK + .04)
            b.box('stone', xs, sy * 8.66, (DECK - .04 + 12.45) / 2, 1.0, .9, 12.45 - DECK + .04)          # end pedestal of the straight run
            b.box('arch', xs, sy * 8.66, 12.51, 1.16, .96, .12)
            b.flush(f'corner parapet {sx:+d}{sy:+d}')


def banks():
    """High stone quays east and west with coursed faces, quay promenades with parapets, quay roads, the road
    running on from the bridge, footways, block plots."""
    C.box('River', (0.0, 0.0, .005), (2 * QX, 2 * RIVER_Y, .01), 'water', 'site', 0)
    for sx in (-1, 1):
        xa, xb = sorted((sx * QX, sx * BANK))
        xm = (xa + xb) / 2
        C.box(f'Quay {sx:+d}', (xm, 0.0, (DECK - .04) / 2), (xb - xa, 2 * RIVER_Y, DECK - .04), 'quay', 'site', 0)
        C.box(f'Bank road {sx:+d}', (xm, 0.0, DECK - .02), (xb - xa, 2 * RIVER_Y, .04), 'asphalt', 'site', 0)
        b = Batch()
        q0 = sx * QX
        for sy in (-1, 1):
            ya, yb = sorted((sy * 9.0, sy * RIVER_Y))
            b.box('paving', q0 + sx * 2.25, (ya + yb) / 2, (DECK + FOOT) / 2, 4.5, yb - ya, FOOT - DECK)          # quay promenade
            pa, pb = sorted((sy * (8.66 + APR), sy * RIVER_Y))
            b.box('stone', q0 + sx * .3, (pa + pb) / 2, FOOT + .42, .5, pb - pa, .84)                          # quay parapet
            b.box('arch', q0 + sx * .3, (pa + pb) / 2, FOOT + .9, .62, pb - pa - .02, .12)
            b.box('paving', xm, sy * 7.5, (DECK + FOOT) / 2, xb - xa, 3.0, FOOT - DECK)                          # footway along the road
            pa, pb = sorted((sy * 12.0, sy * RIVER_Y))
            b.box('paving', sx * (QX + 15.0 + BANK) / 2, (pa + pb) / 2, (DECK + FOOT) / 2, BANK - QX - 15.0, pb - pa, FOOT - DECK)   # block plots
        for z in [.9 * k for k in range(1, 12)]:                                                                # coursed quay face
            b.box('joint', q0 - sx * .002, 0.0, z, .008, 2 * RIVER_Y, .03)
        for y in [-RIVER_Y + 1.5 + 3.0 * k for k in range(40)]:
            b.box('joint', q0 - sx * .002, y, DECK / 2, .008, .03, DECK - .2)
        marks(b, xa, xb)
        b.flush(f'bank {sx:+d}')
        for y in (-34.0, -20.0, 20.0, 34.0):
            street_tree(sx * (QX + 2.6), y, z=FOOT, height=8.0, spread=2.2)


def blocks():
    """Old town blocks with orange hipped roofs facing the river across the quay roads (context): a river face with
    real cuts, windows on the road face, a body behind."""
    for sx in (-1, 1):
        for i, (ya, yb, h, role) in enumerate(((12.0, 44.0, 14.0, 'wall'), (-44.0, -12.0, 15.5, 'facade2'))):
            xf = sx * (QX + 16.0)
            if sx > 0:
                f = C.Face((xf, 0, 0), (0, -1, 0), (1, 0, 0), f'Block {sx:+d}{i}')
                lo, hi = -yb, -ya
            else:
                f = C.Face((xf, 0, 0), (0, 1, 0), (-1, 0, 0), f'Block {sx:+d}{i}')
                lo, hi = ya, yb
            hs = [hole(f'Block {sx:+d}{i} window {k} {j}', lo + 2.0 + 3.0 * j, FOOT + 1.0 + 3.4 * k, 1.2, 1.9)
                  for k in range(4) for j in range(int((hi - lo - 2.5) / 3.0))]
            top = FOOT + h
            f.wall(f'Block {sx:+d}{i} river face', lo, hi - EPS, FOOT, top, depth=T, role=role, holes=hs)
            m = Merge(f)
            for hh in hs:
                framed(m, f, hh, cols=2, rows=2, inset=.14, occupied='flat', lite=True)
            m.box('trim', (lo + hi) / 2, -.08, top - .2, hi - lo + .1, .16, .3)
            m.flush(f'Block {sx:+d}{i}')
            xa, xb = sorted((xf + sx * T, sx * (QX + 40.0)))
            C.box(f'Block {sx:+d}{i} body', ((xa + xb) / 2, (ya + yb) / 2, (FOOT + top) / 2), (xb - xa, yb - ya, top - FOOT), role, 'context', 0)
            pitched_roof(f'Block {sx:+d}{i} roof', min(xf, sx * (QX + 40.0)), max(xf, sx * (QX + 40.0)), ya, yb, top, 4.5, axis='y', ov=.35, role='roof', module='context')
            C.qa_room_light(f'Block {sx:+d}{i} rooms', (xf + sx * 3.0, (ya + yb) / 2, FOOT + 2.0), 60, 4.0)
            b = Batch()
            yr = ya if ya > 0 else yb                                                        # the face towards the road
            for k in range(4):
                for x in [xf + sx * (2.0 + 3.0 * j) for j in range(7)]:
                    b.box('dark', x, yr - (.01 if ya > 0 else -.01), FOOT + 1.95 + 3.4 * k, 1.2, .03, 1.9)
            b.flush(f'Block {sx:+d}{i} side windows')


def vehicles():
    """A red double-decker bus, a car and a van on the bridge, as simple massing."""
    b = Batch()

    def wheels(x0, x1, y, w):
        for x in (x0, x1):
            for s in (-1, 1):
                b.box('dark', x, y + s * (w / 2 - .15), DECK + .35, .8, .3, .7)
    b.box('red', -8.0, 1.6, DECK + 2.375, 10.0, 2.5, 4.05)                          # bus
    for z in (DECK + 1.9, DECK + 3.4):
        for s in (-1, 1):
            b.box('glass', -8.0, 1.6 + s * 1.26, z, 9.2, .03, 1.0)
    wheels(-11.5, -4.6, 1.6, 2.5)
    b.box('car', 7.0, -1.6, DECK + .7, 4.5, 1.8, .8)                                 # car
    b.box('glass', 7.2, -1.6, DECK + 1.4, 2.4, 1.6, .6)
    wheels(5.6, 8.4, -1.6, 1.8)
    b.box('van', 2.5, -4.5, DECK + 1.3, 4.8, 2.0, 2.0)                               # van
    b.box('glass', 4.85, -4.5, DECK + 1.75, .03, 1.8, .7)
    wheels(1.0, 4.0, -4.5, 2.0)
    b.flush('vehicles')


def build():
    banks()
    bridge_body()
    arch_rings()
    ashlar()
    cutwaters()
    cornice()
    deck()
    lamps()
    corners()
    blocks()
    vehicles()
    C.CONTACTS.append(dict(name='Three-arch stone road bridge between high quays: piers and cutwaters from the water, arches springing from piers and quays, deck on the spandrels', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(40, -55, 50), fill=(-45, -25, 35), rear=(-20, 45, 35), target=(0, 0, 8.0), gain=4.0)
