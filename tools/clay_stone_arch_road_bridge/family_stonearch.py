"""Heritage stone arch road bridge, authored from the locked catalogue views of
urban_vehicular_bridge / variant_0 (Heritage Stone Arch).

Read from the pixels (the top view governs the plan): a city road crossing a river that runs north-south between high
stone quays. Three semicircular river arches of warm cut sandstone on two piers with pointed cutwaters; the cutwaters
rise as pilaster buttresses to the deck, where the balustrade breaks forward into pedestals carrying ornate
double-lantern lamp standards (moulded cast bases, ringed fluted shafts, scroll arms, domed hexagonal lanterns);
voussoired arch rings, coursed ashlar spandrel walls, a dentilled cornice. The plan is asymmetric: the west bank is a
high quay with a quay road meeting the bridge road at grade; on the east the river is bounded by a low quay whose road
passes under a fourth, smaller land arch between the east river pier and the east abutment, the north-east quay
curving into the bridge so the upstream channel is narrower than the downstream one. At each abutment corner a
quadrant wall (balustrade on a plinth) sweeps the footway round onto the coped quay parapet, with the end pedestal and
its double lamp at the tangent point. On the deck four traffic lanes with dashed markings between paved footways and
stone balustrades with pedestals. Old town blocks with orange hipped roofs line the quays, a red double-decker bus,
a car and a van cross the bridge.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-stone-arch-road-bridge'
SPAN, PIER, NA = 16.0, 3.5, 3                   # clear span of each semicircular river arch, pier thickness, arch count
QX = (NA * SPAN + (NA - 1) * PIER) / 2          # 27.5 m: west abutment face at -QX, east river pier from +QX
QE = QX + PIER                                  # east face of the east river pier, where the land arch springs
LSPAN = 10.0                                    # clear span of the land arch over the east quay road
XA = QE + LSPAN                                 # east abutment face, 41 m
X0, X1, Y0, Y1 = -QX, XA, -9.0, 9.0             # the bridge itself: 68.5 m long, 18 m wide
ZS, RT = 1.2, .9                                # springing above the water, arch ring depth
ZL = 3.0                                        # the low east quay and its road
ZSL = ZL + 1.0                                  # springing of the land arch
DECK = 11.0                                     # road surface and quay street level
ZC = 7.0                                        # top of the cutwaters
HW = 8.9                                        # half-width of the spandrel faces
T = .3
EPS = .002
PALETTE = dict(water=(.030, .036, .026), stone=(.95, .43, .145), arch=(1.0, .52, .19), joint=(.52, .25, .085),
    quay=(.50, .37, .21), asphalt=(.25, .25, .26), white=(.92, .92, .90), paving=(.45, .46, .48), kerb=(.62, .62, .62),
    hardware=(.13, .15, .14), pale=(.96, .88, .62), glass=(.20, .24, .27), wall=(.84, .74, .58), facade2=(.86, .81, .71),
    brick=(.64, .40, .30), roof=(.68, .34, .20), red=(.72, .10, .10), van=(.42, .38, .26), car=(.16, .17, .19),
    dark=(.10, .10, .11), interior=(.84, .80, .74), floor=(.58, .48, .38), trim=(.92, .91, .88), planting=(.30, .44, .20),
    tree=(.28, .44, .18), timber=(.46, .34, .22), soil=(.22, .16, .10), concrete=(.70, .69, .66), sand=(.70, .66, .58),
    blue=(.20, .30, .40), pot=(.60, .34, .22))


FRONT_CAM = (-38.5, 21.0, 15.2)
FRONT_TARGET = (-6.0, 6.0, 6.5)


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
        ('roadway_deck', (-25.0, -3.0, 14.0), (14.0, -3.0, 11.0), 35),
        ('river_underside', (-19.5, -27.0, 1.6), (-19.5, 0.0, 5.0), 35),
        ('rear_north', (22.0, 42.0, ZL + 4.0), (2.0, HW, 6.0), 30)])
    for c in cams:
        if c['name'] == 'front':                     # the locked front: on the north-west quay promenade behind the near abutment,
            # looking along the north face to the far bank; river at left, end pedestal and lamp at right
            c.update(location=FRONT_CAM, target=FRONT_TARGET, lens=20, whole=False)
        elif c['name'] == 'front_corner':            # the locked oblique: high over the west bank, along the bridge, arches on the
            # right, the near south-west quadrant wall and apron in the lower third, the land arch at the far end
            c.update(location=(-62.0, -21.0, 36.0), target=(4.0, -2.0, 4.0), lens=26, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(54.0, -70.0, 50.0), target=(6.0, 0.0, 4.0), lens=28, whole=False)
        elif c['name'] == 'top':
            c.update(location=(6.0, 0.0, 160.0), target=(6.0, .001, 0.0), ortho_scale=130.0, whole=False)
        elif c['name'] == 'left_side':               # lateral view of the west abutment and quay junction from the river
            c.update(location=(-12.0, -36.0, 3.0), target=(-29.0, -10.5, 6.5), lens=26, whole=False)
        elif c['name'] == 'right_side':              # lateral view of the land arch, east pier and abutment from the low east quay road
            c.update(location=(35.5, -40.0, ZL + 1.7), target=(35.0, 0.0, 6.5), lens=24, whole=False)
        elif c['name'] == 'rear':                    # the north elevation from over the narrower upstream river
            c.update(location=(6.0, 70.0, 9.0), target=(6.0, HW, 6.0), lens=22, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(36.0, 52.0, 28.0), target=(2.0, 0.0, 6.0), lens=28, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='urban_vehicular_bridge/variant_0 (Heritage Stone Arch)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=0, storey_programme='bridge: a four-lane road with footways over a river; the quays and town blocks are context',
            plan='68.5 x 18 m bridge (top view): three river arches between the high west quay and the east river pier, a fourth land arch over the low east quay road; the north-east quay curves into the bridge so the upstream channel is narrower; the road continues east and west',
            section_m=dict(carriageway=[-6.0, 6.0], footways=[[-8.4, -6.0], [6.0, 8.4]], balustrades=[-8.65, 8.65]),
            facade='three semicircular 16 m cut-stone arches with voussoired rings, coursed ashlar spandrels, pointed cutwaters rising as pilasters, dentilled cornice, stone balustrades with pedestals, double-lantern lamp standards',
            levels_m=[0.0, ZS, ZL, ZSL, ZS + SPAN / 2, DECK], inferred='the river bed, foundations and the town blocks beyond the quays are context; the deck build-up is an assumption'),
        roof_contract=dict(type='open road deck; hipped tile roofs on the context blocks', datum_m=DECK, crowns_m=[h]),
        identity_contract=dict(owner='three-arch cut-stone road bridge with cutwaters, cornice, balustrades and double-lantern lamps over a river between quays'),
        material_contract=dict(profile='source-palette clay: warm honey sandstone with lighter voussoirs and cornice and darker joints, darker greyer quay walls, grey asphalt with white lane marks, cool grey paving, dark iron lamps with warm lanterns, dark olive river water, orange roofs', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='four traffic lanes, two footways'),
        street_contract=dict(kind='fixed_native_section', width_m=Y1 - Y0, axis='x', junction_finish='asphalt',
                             bands=['balustrade', 'footway', 'carriageway', 'footway', 'balustrade']),
        contact_contract=['River surface at grade zero', 'Piers and cutwaters from the water', 'River arches spring from the piers and the west abutment',
                          'Land arch springs from the east river pier and the east abutment over the low quay road',
                          'Quadrant walls on the curved abutment quay corners', 'Deck on the spandrels, road on the quays'],
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
CENTRES = [-QX + R + k * (SPAN + PIER) for k in range(NA)]               # river arch centres along x
PIERS = [(c + R, c + R + PIER) for c in CENTRES[:-1]] + [(QX, QE)]       # pier faces along x; the last is the east river pier
RL, RTL = LSPAN / 2, .7                                                    # land arch radius and ring depth
CL = QE + RL                                                               # land arch centre
ARCHES = [(c, R, ZS, RT) for c in CENTRES] + [(CL, RL, ZSL, RTL)]          # (centre, radius, springing, ring depth)
LONG = 2400.0                                                              # the river, quays and town run on far past every view
FOOT = 11.15                                                               # footway and quay paving level
QW = -QX - 4.5                                                             # west quay face, set back from the abutment face
RPW, RPE = 4.76, 3.26                                                      # quadrant parapet radii, west and east corners
RW = XA + RPE - .26                                                        # the east retaining wall (low quay to town) south of the bridge
QUAY_T = 4.3                                                               # low east quay: edge paving to the road
ROAD_T = 10.7                                                              # low east quay: road to the footway
LOW_W = RW - QX                                                            # width of the low east quay, river edge to retaining wall


def smooth(t):
    t = min(1.0, max(0.0, t))
    return t * t * (3 - 2 * t)


def xq(y):
    """River edge of the low east quay: straight at the east river pier, south of the bridge and just north of it;
    upstream it curves west so the upstream channel is narrower (the top view)."""
    y0 = 8.66 + RPE
    if y <= y0:
        return QX
    return QX - 15.5 * smooth((y - y0) / 36.0)


def xw(y):
    """The retaining wall between the low east quay and the town, parallel to the river edge."""
    return xq(y) + LOW_W


def ys_north(a, b, step=2.0):
    """Sample y values along the curved north-east quay, denser on the curve."""
    out, y = [], a
    while y < b:
        out.append(y)
        y += step if y < 60 else 400.0
    out.append(b)
    return out


def hexa(b, role, corners):
    """Add a closed hexahedron (eight corners: one end ring of four, then the other) to a Batch."""
    b._hex(role, corners)


def lathe(b, role, cx, cy, z0, profile, n=10, phase=0.0):
    """Turned solid into a Batch: profile is [(radius, dz)] or [(radius, dz, fluted)] bottom to top; a zero radius closes
    to an apex; fluted rings alternate their radius so the shaft between them reads fluted."""
    V, F = b.g.setdefault(role, ([], []))
    rings = []
    for p in profile:
        r, dz = p[0], p[1]
        if r <= 1e-6:
            rings.append([len(V)]); V.append((cx, cy, z0 + dz)); continue
        idx = []
        for j in range(n):
            a = phase + 2 * math.pi * j / n
            rr = r * (.8 if len(p) > 2 and p[2] and j % 2 else 1.0)
            idx.append(len(V)); V.append((cx + rr * math.cos(a), cy + rr * math.sin(a), z0 + dz))
        rings.append(idx)
    for lo, hi in zip(rings, rings[1:]):
        if len(lo) == 1 and len(hi) == 1:
            continue
        if len(lo) == 1:
            F.extend((lo[0], hi[(j + 1) % n], hi[j]) for j in range(n))
        elif len(hi) == 1:
            F.extend((lo[j], lo[(j + 1) % n], hi[0]) for j in range(n))
        else:
            F.extend((lo[j], lo[(j + 1) % n], hi[(j + 1) % n], hi[j]) for j in range(n))
    if len(rings[0]) > 1:
        F.append(tuple(reversed(rings[0])))
    if len(rings[-1]) > 1:
        F.append(tuple(rings[-1]))


def bridge_body():
    """One stone mass from the west abutment to the east abutment: its outline in x-z is the deck underside, the three
    semicircular river intrados, the pier shafts down to the water, the east river pier and the land arch over the low
    east quay, extruded across the full width (the barrel vaults are its underside)."""
    pts = [(-QX, DECK - .04), (-QX, ZS)]
    n = 28
    for k, c in enumerate(CENTRES):
        pts += [(c + R * math.cos(math.pi - math.pi * i / n), ZS + R * math.sin(math.pi - math.pi * i / n)) for i in range(1, n)]
        x0, x1 = PIERS[k]
        pts += [(x0, ZS), (x0, 0.0), (x1, 0.0), (x1, ZSL if k == NA - 1 else ZS)]
    pts += [(CL + RL * math.cos(math.pi - math.pi * i / 20), ZSL + RL * math.sin(math.pi - math.pi * i / 20)) for i in range(1, 20)]
    pts += [(XA, ZSL), (XA, DECK - .04)]
    C.prism('Bridge body', pts, 'y', -HW, HW, 'stone', 'bridge')


def arch_rings():
    """Voussoired arch rings standing proud of both spandrel faces, alternate stones a shade lighter, a keystone; the
    springing stones are trimmed to the abutment faces so nothing pokes out of the curved quay corners."""
    b = Batch()
    for (c, r, zs, rt) in ARCHES:
        n = 27 if r > 6 else 19
        for s in (-1, 1):
            ya, yb = (-HW - .18, -HW + .04) if s < 0 else (HW - .04, HW + .18)
            for k in range(n):
                ta, tb = math.pi - math.pi * k / n, math.pi - math.pi * (k + 1) / n
                key = k == n // 2
                r0, r1 = r - .04, r + rt + (.15 if key else 0.0)
                yy = (ya - (.06 if key and s < 0 else 0.0), yb + (.06 if key and s > 0 else 0.0))

                def ring(rad, t, y):
                    return (min(XA, max(-QX, c + rad * math.cos(t))), y, zs + rad * math.sin(t))
                hexa(b, 'arch' if k % 2 else 'stone', [ring(r0, ta, yy[0]), ring(r0, tb, yy[0]), ring(r1, tb, yy[0]), ring(r1, ta, yy[0]),
                                                       ring(r0, ta, yy[1]), ring(r0, tb, yy[1]), ring(r1, tb, yy[1]), ring(r1, ta, yy[1])])
    b.flush('arch rings')


def solid_intervals(z, pad=.06):
    """The x intervals of spandrel wall that are solid at height z (outside the arch openings and their rings)."""
    iv = [(-QX, XA)]
    for (c, r, zs, rt) in ARCHES:
        dz = z - zs
        if dz < 0:
            h = r
        elif dz < r + rt + pad:
            h = math.sqrt((r + rt + pad) ** 2 - dz * dz)
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
        while z < 10.0:
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
    """Pointed cutwaters on both faces of the two river piers (smaller upstream), capped with a stone hood, rising as
    pilaster buttresses with a recessed panel to the cornice; the east river pier stands at the low quay edge and
    carries the pilaster only. The cutwater runs 5 cm proud of the pier jambs and starts inside the pier body, so no
    face is shared with the jamb walls (the v001 see-through slit)."""
    for i, (x0, x1) in enumerate(PIERS):
        xm = (x0 + x1) / 2
        river = i < len(PIERS) - 1
        for s in (-1, 1):
            if river:
                tip, mid = (11.7, 10.3) if s < 0 else (10.9, 9.9)
                poly = [(x0 - .05, s * 8.75), (x0 - .05, s * mid), (xm, s * tip), (x1 + .05, s * mid), (x1 + .05, s * 8.75)]
                C.prism(f'Cutwater {i} {s:+d}', poly, 'z', 0.0, ZC, 'stone', 'bridge')
                vs = [(x, y, ZC) for x, y in poly] + [(xm, s * 8.75, ZC + 1.8)]
                C.mesh(f'Cutwater hood {i} {s:+d}', vs, [(4, 3, 2, 1, 0)] + [(j, (j + 1) % 5, 5) for j in range(5)], 'arch', 'bridge')
            z0 = ZC - .2 if river else ZL - .04
            b = Batch()
            b.box('stone', xm, s * 9.4, (z0 + 10.70) / 2, PIER - .7, 1.2, 10.70 - z0)                  # pilaster buttress (top under the corona)
            b.box('arch', xm, s * 9.42, ZC + 1.9, PIER - .5, 1.28, .22)                                # impost band on it
            zp0, zp1 = ZC + 2.15, 10.1                                                                 # recessed panel: a raised frame round a darker field
            for u in (-1, 1):
                b.box('arch', xm + u * (PIER - 1.2) / 2, s * 10.03, (zp0 + zp1) / 2, .14, .06, zp1 - zp0)
            for zz in (zp0, zp1):
                b.box('arch', xm, s * 10.03, zz, PIER - 1.06, .06, .14)
            b.box('joint', xm, s * 10.005, (zp0 + zp1) / 2, PIER - 1.3, .01, zp1 - zp0 - .14)
            b.flush(f'pier pilaster {i} {s:+d}')
            C.box(f'Pier refuge {i} {s:+d}', (xm, s * 9.15, (10.70 + 12.5) / 2), (2.0, 1.7, 12.5 - 10.70), 'stone', 'bridge', 0)
            C.box(f'Pier refuge cap {i} {s:+d}', (xm, s * 9.15, 12.56), (2.16, 1.86, .12), 'arch', 'bridge', 0)


def cornice():
    b = Batch()
    for s in (-1, 1):
        b.box('stone', (XA - QX) / 2, s * (HW + .12), 10.375, XA + QX, .3, .25)
        b.box('arch', (XA - QX) / 2, s * (HW + .2), 10.61, XA + QX, .46, .22)
        x = -QX + .25
        while x < XA - .2:
            if all(not (lo - .1 < x < hi + .1) for lo, hi in PIERS) and all(abs(x - c) > .6 for c, r, *_ in ARCHES if r > 6):
                b.box('stone', x, s * (HW + .06), 10.175, .22, .16, .15)
            x += .5
    b.flush('cornice')


def balusters(b, pts, y_of=None):
    """Turned-looking balusters at the given (x, y) points on a plinth at FOOT."""
    for (x, y) in pts:
        b.box('stone', x, y, 11.51, .22, .22, .3)
        b.box('stone', x, y, 11.78, .12, .12, .24)
        b.box('stone', x, y, 11.98, .2, .2, .16)


def balustrade_run(b, x0, x1, y):
    """Stone balustrade along x at y: plinth, balusters, rail."""
    b.box('stone', (x0 + x1) / 2, y, 11.16, x1 - x0, .52, .4)
    b.box('stone', (x0 + x1) / 2, y, 12.15, x1 - x0, .58, .18)
    n = max(1, int((x1 - x0 - .2) / .32))
    balusters(b, [(x0 + .16 + (x1 - x0 - .32) * i / max(1, n - 1), y) for i in range(n)] if n > 1 else [((x0 + x1) / 2, y)])


PEDESTALS = [(-23.5, .8), (-15.5, .8), (-4.0, .8), (4.0, .8), (15.5, .8), (23.5, .8), (CL, .8)]


def deck():
    """Asphalt carriageway with lane marks, raised paved footways with kerbs, balustrades with pedestals."""
    C.box('Carriageway', ((XA - QX) / 2, 0.0, DECK - .02), (XA + QX, 12.0, .04), 'asphalt', 'deck', 0)
    b = Batch()
    for s in (-1, 1):
        b.box('paving', (XA - QX) / 2, s * 7.2, (DECK - .04 + FOOT) / 2, XA + QX, 2.4, FOOT - DECK + .04)
        b.box('kerb', (XA - QX) / 2, s * 6.0, (DECK - .04 + FOOT + .02) / 2, XA + QX, .2, FOOT + .02 - DECK + .04)
    marks(b, -QX, XA)
    b.flush('deck')
    stops = sorted([(-QX, .9), (XA, .9)] + [((x0 + x1) / 2, 2.0) for x0, x1 in PIERS] + PEDESTALS)
    b = Batch()
    for s in (-1, 1):
        y = s * 8.66
        for (pa, wa), (pb, wb) in zip(stops, stops[1:]):
            balustrade_run(b, pa + wa / 2, pb - wb / 2, y)
        for p, w in PEDESTALS:
            b.box('stone', p, y, (DECK - .04 + 12.45) / 2, w, .8, 12.45 - DECK + .04)
            b.box('arch', p, y, 12.51, w + .16, .96, .12)
    b.flush('balustrades')


def marks(b, x0, x1, single=True):
    """Single solid centre line and dashed lane lines along x."""
    b.box('white', (x0 + x1) / 2, 0.0, DECK + .003, x1 - x0, .15, .006)
    x = x0 + 1.0
    while x < x1 - 2.0:
        for y in (-3.0, 3.0):
            b.box('white', x + 1.5, y, DECK + .003, 3.0, .12, .006)
        x += 6.0


def lamp(name, x, y, z0, big=False):
    """Ornate cast-iron double-lantern standard: a moulded bell base, a ringed fluted round shaft, a collar, two C-scroll
    arms with volutes, hexagonal glazed lanterns with corner posts, domed caps and finials, and a central finial."""
    k = 1.15 if big else 1.0
    b = Batch()
    lathe(b, 'hardware', x, y, z0, [(.30 * k, 0), (.30 * k, .10), (.25 * k, .15), (.25 * k, .26), (.20 * k, .33), (.15 * k, .55),
                                    (.19 * k, .60), (.19 * k, .68), (.13 * k, .76), (.11 * k, .82), (0.0, .82)], n=10)
    shaft = [(.105, .80), (.105, .84, 1), (.10, 1.52, 1)]
    for h, top in ((1.55, 2.32), (2.35, 2.92)):
        shaft += [(.10, h), (.135, h + .03), (.135, h + .10), (.10, h + .13), (.10, h + .16, 1), (.095, top, 1)]
    shaft += [(.095, 2.95), (.145, 3.0), (.145, 3.14), (.10, 3.2), (.075, 3.26), (.07, 4.12), (.11, 4.16), (.11, 4.26), (.075, 4.31),
              (.045, 4.5), (.06, 4.58), (.03, 4.66), (0.0, 4.82)]
    lathe(b, 'hardware', x, y, z0, [(p[0] * k, p[1] * k) + tuple(p[2:]) for p in shaft], n=12)
    zA = z0 + 3.12 * k
    for sgn in (-1, 1):
        lx = x + sgn * .64 * k
        pts = [(x + sgn * .64 * k * math.sin(t * math.pi / 2), zA + .62 * k * (1 - math.cos(t * math.pi / 2))) for t in [i / 6 for i in range(7)]]
        for (ax, az), (bx, bz) in zip(pts, pts[1:]):
            b.beam('hardware', (ax, y, az), (bx, y, bz), .05 * k, .06 * k, ext=.02)
        cx, cz = x + sgn * .26 * k, zA - .12 * k                       # volute under the arm
        sp = [(cx + sgn * (.15 - .1 * t) * k * math.cos(math.pi / 2 + 4.2 * t), cz + (.15 - .1 * t) * k * math.sin(math.pi / 2 + 4.2 * t)) for t in [i / 7 for i in range(8)]]
        b.beam('hardware', (x + sgn * .06, y, zA + .02), (sp[0][0], y, sp[0][1]), .04 * k, .05 * k, ext=.02)
        for (ax, az), (bx, bz) in zip(sp, sp[1:]):
            b.beam('hardware', (ax, y, az), (bx, y, bz), .04 * k, .05 * k, ext=.015)
        zl = zA + .62 * k                                              # lantern: bottom drop, frame rings, glass, posts, dome, finial
        lathe(b, 'hardware', lx, y, zl, [(0.0, -.12 * k), (.08 * k, -.04 * k), (.21 * k, 0.0), (.21 * k, .06 * k)], n=6, phase=math.pi / 6)
        lathe(b, 'hardware', lx, y, zl, [(.23 * k, .62 * k), (.23 * k, .68 * k), (.20 * k, .74 * k), (.15 * k, .82 * k), (.08 * k, .88 * k),
                                         (.04 * k, .91 * k), (.055 * k, .95 * k), (.03 * k, 1.0 * k), (0.0, 1.08 * k)], n=6, phase=math.pi / 6)
        for j in range(6):
            a = math.pi / 6 + j * math.pi / 3
            px, py = lx + .19 * k * math.cos(a), y + .19 * k * math.sin(a)
            b.beam('hardware', (px, py, zl + .05 * k), (px, py, zl + .63 * k), .03 * k, .03 * k)
        hexg = [(lx + .175 * k * math.cos(math.pi / 6 + j * math.pi / 3), y + .175 * k * math.sin(math.pi / 6 + j * math.pi / 3)) for j in range(6)]
        C.prism(f'{name} lantern glass {sgn:+d}', hexg, 'z', zl + .06 * k, zl + .62 * k, 'pale', 'lamps')
    b.flush(name)


def lamps():
    for x0, x1 in PIERS:
        for s in (-1, 1):
            lamp(f'Lamp pier {x0:+.0f} {s:+d}', (x0 + x1) / 2, s * 9.15, 12.62)
    for x in (-QX, XA):
        for s in (-1, 1):
            lamp(f'Lamp end {x:+.0f} {s:+d}', x, s * 8.66, 12.57, big=True)


def arc_pts(cx, cy, r, a0, a1, n):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def quadrant(b, cx, cy, rp, a0, a1, n=12):
    """Quadrant balustrade on a solid plinth along an arc (the parapet line), coping on top."""
    path = arc_pts(cx, cy, rp, a0, a1, n)
    for (ax, ay), (bx, by) in zip(path, path[1:]):
        b.beam('stone', (ax, ay, 11.16), (bx, by, 11.16), .52, .4, ext=.03)
        b.beam('stone', (ax, ay, 12.15), (bx, by, 12.15), .58, .18, ext=.03)
    L = rp * abs(a1 - a0)
    m = int(L / .32)
    pts = arc_pts(cx, cy, rp, a0 + (a1 - a0) * .5 / m, a1 - (a1 - a0) * .5 / m, m - 1)
    balusters(b, pts)


def parapet_line(b, pts, h=.84):
    """Solid coped quay parapet along a polyline at FOOT."""
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        b.beam('stone', (ax, ay, FOOT + h / 2), (bx, by, FOOT + h / 2), .5, h, ext=.02)
        b.beam('arch', (ax, ay, FOOT + h + .06), (bx, by, FOOT + h + .06), .62, .12, ext=.03)


def corners():
    """At each abutment the balustrade sweeps round a quadrant wall onto the coped quay parapet, with the end
    pedestal and its double lamp at the tangent point. West: the high quay face is set 4.5 m back from the abutment
    face and the quay wall itself curves round the corner under the parapet; east: the same at the top of the
    retaining wall above the low quay."""
    b = Batch()
    for sy in (-1, 1):
        cw = (-QX, sy * (8.66 + RPW))                                           # west corner: centre of the quadrant
        a0, a1 = (-math.pi / 2, -math.pi) if sy > 0 else (math.pi / 2, math.pi)
        quadrant(b, cw[0], cw[1], RPW, a0, a1)
        ce = (XA, sy * (8.66 + RPE))
        a0, a1 = (-math.pi / 2, 0.0) if sy > 0 else (math.pi / 2, 0.0)
        quadrant(b, ce[0], ce[1], RPE, a0, a1, n=9)
        for x in (-QX, XA):                                                     # end pedestals
            b.box('stone', x, sy * 8.66, (DECK - .04 + 12.45) / 2, .9, .9, 12.45 - DECK + .04)
            b.box('arch', x, sy * 8.66, 12.51, 1.06, 1.06, .12)
        # The coped quay parapet along the west quay and along the top of the east retaining wall.
        yq = sy * (8.66 + RPW)
        parapet_line(b, [(QW - .26, yq), (QW - .26, sy * LONG)])
        ye = sy * (8.66 + RPE)
        if sy < 0:
            parapet_line(b, [(RW + .26, ye), (RW + .26, -LONG)])
        else:
            parapet_line(b, [(xw(y) + .26, y) for y in ys_north(ye, LONG)])
    b.flush('quadrants and quay parapets')


def west_bank():
    """The high west quay: a solid bank whose quay face curves round each abutment corner (the quadrant), the quay
    promenade, the quay road meeting the bridge road at grade, paved block plots, a coursed quay face."""
    pts = [(-LONG, -LONG), (-LONG, LONG), (QW, LONG)]
    pts += arc_pts(-QX, 8.66 + RPW, RPW - .26, math.pi, math.pi * 1.5, 12)
    pts += arc_pts(-QX, -(8.66 + RPW), RPW - .26, math.pi / 2, math.pi, 12)
    pts += [(QW, -LONG)]
    C.prism('West bank', pts, 'z', 0.0, DECK - .04, 'quay', 'site')
    C.prism('West bank asphalt', pts, 'z', DECK - .04, DECK, 'asphalt', 'site')
    b = Batch()
    for sy in (-1, 1):
        ya, yb = sorted((sy * (8.66 + RPW), sy * LONG))
        b.box('paving', QW - 2.5, (ya + yb) / 2, (DECK + FOOT) / 2, 5.0, yb - ya, FOOT - DECK)            # quay promenade
        ya, yb = sorted((sy * 6.0, sy * LONG))
        b.box('paving', (-LONG + QW - 19.0) / 2, (ya + yb) / 2, (DECK + FOOT) / 2, LONG + QW - 19.0, yb - ya, FOOT - DECK)   # plots and footways
        for k in range(8):                                                                                  # zebra on the quay road
            b.box('white', QW - 5.0 - 1.2 - k * 1.6, sy * 9.0, DECK + .003, .6, 3.2, .006)
    for z in [.9 * k for k in range(1, 12)]:                                                                # coursed quay face
        for sy in (-1, 1):
            ya, yb = sorted((sy * (8.66 + RPW), sy * LONG))
            b.box('joint', QW - .002, (ya + yb) / 2, z, .008, yb - ya, .03)
    for y in [-300.0 + 3.0 * k for k in range(201)]:
        if abs(y) > 8.66 + RPW + .5:
            b.box('joint', QW - .002, y, DECK / 2, .008, .03, DECK - .2)
    marks(b, -LONG / 4, QW - 19.0)
    b.flush('west bank')
    for sy in (-1, 1):                                                                                      # apron round each quadrant
        poly = [(QW - 5.0, sy * 6.0), (-QX, sy * 6.0)] + arc_pts(-QX, sy * (8.66 + RPW), RPW - .26, -sy * math.pi / 2, -sy * math.pi, 12) + [(QW - 5.0, sy * (8.66 + RPW))]
        if sy < 0:
            poly = list(reversed(poly))
        C.prism(f'West apron {sy:+d}', poly, 'z', DECK - .04, FOOT, 'paving', 'site')
    for y in (-88.0, -72.0, -56.0, -40.0, 40.0, 56.0, 72.0, 88.0):
        street_tree(QW - 3.4, y, z=FOOT, height=8.0, spread=2.2)


def low_quay():
    """The low east quay at ZL: the river edge, a coped low parapet, edge paving, the quay road passing under the land
    arch, a footway along the retaining wall; it curves upstream with the north-east quay."""
    north = ys_north(HW, LONG)
    south = [-LONG, -HW]

    def band(name, o0, o1, z0, z1, role, ys):
        left = [(xq(y) + o0, y) for y in ys]
        right = [(xq(y) + o1, y) for y in reversed(ys)]
        C.prism(name, left + right, 'z', z0, z1, role, 'site')
    # The platform: under the bridge it starts inside the east river pier so no face is shared with the pier.
    pts = [(QX, -LONG), (QX, -HW), (QX + 1.5, -HW), (QX + 1.5, HW)] + [(xq(y), y) for y in north] + \
          [(xw(y) + 2.0, y) for y in reversed(north)] + [(RW + 2.0, -LONG)]
    C.prism('Low east quay', pts, 'z', 0.0, ZL - .04, 'quay', 'site')
    for ys in (south, north):
        band('Low quay parapet', -.02, .5, ZL - .04, ZL + .8, 'stone', ys)
        band('Low quay parapet coping', -.06, .56, ZL + .8, ZL + .92, 'arch', ys)
    band('Low quay edge paving', .5, QUAY_T, ZL - .04, ZL + .12, 'paving', [-LONG] + north)
    band('Low quay road', QUAY_T, ROAD_T, ZL - .04, ZL, 'asphalt', [-LONG] + north)
    band('Low quay footway', ROAD_T, LOW_W + .5, ZL - .04, ZL + .12, 'paving', [-LONG] + north)
    b = Batch()
    for y in [-300.0 + 6.0 * k for k in range(100)]:                                                       # centre line dashes
        if abs(y) > HW + 3:
            b.box('white', xq(y) + (QUAY_T + ROAD_T) / 2, y, ZL + .003, .12, 3.0, .006)
    for k in range(7):                                                                                      # zebra south of the bridge
        b.box('white', xq(-20) + QUAY_T + .5 + k * .9, -20.0, ZL + .003, .5, 3.0, .006)
    b.box('car', xq(-26) + 6.0, -26.0, ZL + .7, 1.8, 4.5, .8)                                               # a car on the low quay road
    b.box('glass', xq(-26) + 6.0, -26.2, ZL + 1.4, 1.6, 2.4, .6)
    b.flush('low quay')
    for y in (-48.0, -64.0, -80.0):
        street_tree(RW - 1.6, y, z=ZL + .12, height=8.5, spread=2.2)


def east_bank():
    """The town above the retaining wall east of the low quay: a solid bank whose corner by the bridge is the east
    quadrant, the bridge road continuing east, paved plots and footways, a coursed retaining wall face."""
    north = ys_north(8.66 + RPE, LONG)
    pts = [(LONG, -LONG), (RW, -LONG)] + arc_pts(XA, -(8.66 + RPE), RPE - .26, 0.0, math.pi / 2, 9) + \
          arc_pts(XA, 8.66 + RPE, RPE - .26, -math.pi / 2, 0.0, 9) + [(xw(y), y) for y in north[1:]] + [(LONG, LONG)]
    C.prism('East bank', pts, 'z', 0.0, DECK - .04, 'quay', 'site')
    C.prism('East bank asphalt', pts, 'z', DECK - .04, DECK, 'asphalt', 'site')
    for sy in (-1, 1):
        if sy < 0:
            poly = [(XA, -6.0), (LONG, -6.0), (LONG, -LONG), (RW, -LONG)] + arc_pts(XA, -(8.66 + RPE), RPE - .26, 0.0, math.pi / 2, 9)
        else:
            poly = [(XA, 6.0)] + arc_pts(XA, 8.66 + RPE, RPE - .26, -math.pi / 2, 0.0, 9) + [(xw(y), y) for y in north[1:]] + [(LONG, LONG), (LONG, 6.0)]
        C.prism(f'East plots {sy:+d}', poly, 'z', DECK - .04, FOOT, 'paving', 'site')
    b = Batch()
    marks(b, XA, LONG / 4)
    for z in [ZL + .9 * k for k in range(1, 9)]:                                                           # coursed retaining wall
        b.box('joint', RW - .002, (-LONG - 8.66 - RPE) / 2, z, .008, LONG - 8.66 - RPE, .03)
        ys = ys_north(8.66 + RPE, 120.0, 3.0)
        for ya, yb in zip(ys, ys[1:]):
            b.beam('joint', (xw(ya) - .002, ya, z), (xw(yb) - .002, yb, z), .008, .03, ext=.01)
    b.flush('east bank')


def block(name, xf, sx, ya, yb, h, role, depth=24.0, windows=True, detail=True):
    """A town block whose river face is at xf (sx = +1: the block lies east of xf), hipped tile roof; near blocks have
    real cut windows on the river face, the others dark window panes."""
    top = FOOT + h
    xb = xf + sx * depth
    xa_, xb_ = sorted((xf, xb))
    if detail:
        if sx > 0:
            f = C.Face((xf, 0, 0), (0, -1, 0), (1, 0, 0), name)
            lo, hi = -yb, -ya
        else:
            f = C.Face((xf, 0, 0), (0, 1, 0), (-1, 0, 0), name)
            lo, hi = ya, yb
        hs = [hole(f'{name} window {k} {j}', lo + 2.0 + 3.0 * j, FOOT + 1.0 + 3.4 * k, 1.2, 1.9)
              for k in range(int((h - 1.5) / 3.4)) for j in range(int((hi - lo - 2.5) / 3.0))]
        f.wall(f'{name} river face', lo, hi - EPS, FOOT, top, depth=T, role=role, holes=hs)
        m = Merge(f)
        for hh in hs:
            framed(m, f, hh, cols=2, rows=2, inset=.14, occupied='flat', lite=True)
        m.box('trim', (lo + hi) / 2, -.08, top - .2, hi - lo + .1, .16, .3)
        m.flush(name)
        xa_, xb_ = sorted((xf + sx * T, xb))
        C.qa_room_light(f'{name} rooms', (xf + sx * 3.0, (ya + yb) / 2, FOOT + 2.0), 60, 4.0)
    C.box(f'{name} body', ((xa_ + xb_) / 2, (ya + yb) / 2, (FOOT + top) / 2), (xb_ - xa_, yb - ya, top - FOOT), role, 'context', 0)
    pitched_roof(f'{name} roof', min(xf, xb), max(xf, xb), ya, yb, top, 4.0 + (h % 3), axis='y', ov=.35, role='roof', module='context')
    if windows and not detail:
        b = Batch()
        for k in range(int((h - 1.5) / 3.4)):
            for j in range(int((yb - ya - 2.5) / 3.0)):
                b.box('dark', xf - sx * .01, ya + 2.0 + 3.0 * j, FOOT + 1.95 + 3.4 * k, .03, 1.2, 1.9)
        b.flush(f'{name} windows')


def town():
    """Context: detailed blocks facing the river by the bridge, simpler blocks along the quays, plain massing rows
    beyond, so no view ends at the edge of the model."""
    block('Block W north', QW - 22.0, -1, 13.0, 45.0, 14.0, 'wall')
    block('Block W south', QW - 22.0, -1, -45.0, -13.0, 15.5, 'facade2')
    block('Block E south', RW + 8.0, 1, -45.0, -13.0, 16.5, 'wall')
    block('Block E north', 52.0, 1, 16.0, 44.0, 12.5, 'facade2')
    roles = ('wall', 'facade2', 'brick', 'wall', 'facade2')
    for sy in (-1, 1):
        for i, y0 in enumerate([(60.0 if sy > 0 else 53.0) + 40.0 * k for k in range(5)]):
            ya, yb = sorted((sy * y0, sy * (y0 + 32.0)))
            h = 12.0 + (i * 7 + (3 if sy > 0 else 0)) % 7
            block(f'Block W {sy:+d} {i}', QW - 22.0, -1, ya, yb, h, roles[i % 5], detail=False)
            xe = xw(y0) + 8.0 if sy > 0 else RW + 8.0
            block(f'Block E {sy:+d} {i}', xe, 1, ya, yb, h + 1.0, roles[(i + 2) % 5], detail=False)
    b = Batch()
    for sx in (-1, 1):
        for row in range(4):
            xf = (QW - 60.0 - 36.0 * row) if sx < 0 else (RW + 44.0 + 36.0 * row)
            for k in range(13):
                for sy in (-1, 1):
                    ya, yb = sorted((sy * (14.0 + 38.0 * k), sy * (44.0 + 38.0 * k)))
                    hgt = 10.0 + ((row * 5 + k * 3 + (2 if sy > 0 else 0)) % 9)
                    xa_, xb_ = sorted((xf, xf + sx * 28.0))
                    b.box(['wall', 'facade2', 'brick'][(row + k) % 3], (xa_ + xb_) / 2, (ya + yb) / 2, FOOT + hgt / 2, 28.0, yb - ya, hgt)
                    pitched_roof(f'Town roof {sx:+d} {row} {k} {sy:+d}', xa_, xb_, ya, yb, FOOT + hgt, 4.0, axis='y', ov=.3, role='roof', module='context')
    b.flush('town massing')


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
    for ob in C.bpy.data.objects:                       # the river and town run on far beyond the default clip distance
        if ob.type == 'CAMERA':
            ob.data.clip_end = 2 * LONG + 500.0
    C.box('River', (0.0, 0.0, .005), (2 * LONG, 2 * LONG, .01), 'water', 'site', 0)
    west_bank()
    low_quay()
    east_bank()
    bridge_body()
    arch_rings()
    ashlar()
    cutwaters()
    cornice()
    deck()
    lamps()
    corners()
    town()
    vehicles()
    C.CONTACTS.append(dict(name='Stone road bridge: three river arches between the high west quay and the east river pier, a land arch over the low east quay road; piers and cutwaters from the water, quadrant walls on curved abutment corners, deck on the spandrels', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(40, -55, 50), fill=(-45, -25, 35), rear=(-20, 45, 35), target=(0, 0, 8.0), gain=4.0)
