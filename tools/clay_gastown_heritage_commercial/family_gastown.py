"""Gastown heritage commercial block, authored from the locked catalogue views of
gastown_heritage_commercial / variant_0 (a Victorian brick and sandstone corner commercial block in Gastown, Vancouver).

Read from the pixels (the top view governs the plan): a nearly square three-storey corner block of red brick with
rusticated buff sandstone corner piers, on the corner of a cobbled street (south, the front) and an asphalt street
(east). The south front has five bays between a stone west end pier and a stone corner pier: four bays with one wide
round-arched window on the top floor and a three-light window with a transom below, and a wider corner bay with a
pair of arched windows over a pair of sash windows; brick pilasters with carved stone capitals, stone sill bands and
lintels, a deep stone frieze lettered GASTOWN COMMERCE BUILDING and a bracketed modillion cornice, with a pediment
over the central bay carrying an acanthus crest (front, oblique, top). The ground floor is a row of shopfronts
between rusticated stone piers: panelled bulkheads, plate glass, small-paned transoms, recessed timber doors and a
dark signboard fascia under a moulded shop cornice; the corner shop wraps onto the east street. The east front
continues the cornice: the wide corner bay, four narrow bays of single sash windows on all three floors over a stone
plinth, and a pilastered end bay with paired arched windows (front, oblique). A flat tar roof inside a stone-coped
parapet with a brick chimney, a clapboard stair penthouse, a small skylight and two glazed pyramid skylights (top,
oblique). On the brick sidewalk at the corner the steam clock stands among chained bollards; globe-cluster lamp
posts line the sidewalks. A lower cream-painted neighbour adjoins on the west (front), with a cobbled lane and
brick blocks beyond; a brick block adjoins on the north and brick warehouse blocks face it across the east street
(top, oblique).
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-gastown-heritage-commercial'
X0, X1, Y0, Y1 = -13.0, 13.0, -11.8, 11.8            # the block: 26 m front (south), 23.6 m deep (top view)
T = .5                                                # brick carrier depth
G0 = .15                                              # shop floor over the sidewalk
SHOP, FASCIA, SHOPC = 4.30, 5.10, 5.45                # shopfront head, signboard top, shop cornice top
F2, F3 = 5.6, 10.3                                    # second and third floors
W2Z, W2H = 6.3, 3.0                                   # second-floor windows: sill and height
W3Z, W3H = 10.9, 3.6                                  # third-floor arched windows: sill and height (to the crown)
FRIEZE0, FRIEZE1 = 14.95, 15.75                       # lettered stone frieze
EAVE = 16.5                                           # top of the cornice corona
PARA = 17.2                                           # parapet top (coping above)
PED_RISE, PED_W = 2.1, 6.4                            # pediment over the central bay
ROOF = 16.55                                          # roof membrane top, inside the parapet
TOP = EAVE + PED_RISE + .9
EPS = .002
# South front bays (x): stone west end pier, five bays, stone corner pier (front, oblique).
S_PIERS = [(-12.99, -11.8), (-8.0, -7.1), (-3.3, -2.4), (1.4, 2.3), (6.1, 7.0), (11.8, 13.0)]
S_BAYS = [(-11.8, -8.0), (-7.1, -3.3), (-2.4, 1.4), (2.3, 6.1), (7.0, 11.8)]
# East front bays (y): corner pier, wide corner bay, four narrow bays, pilastered end bay with paired arches, end pier.
E_PIERS = [(-11.8, -10.6), (-6.4, -5.6), (4.4, 5.3), (10.6, 11.79)]
E_CORNER = (-10.6, -6.4)
E_NARROW = [-4.35, -1.85, .65, 3.15]
E_END = (5.3, 10.6)
CLOCK = (9.1, -13.95)                                 # the steam clock on the corner sidewalk, about 1.9 m off the front (top, front)
PALETTE = dict(wall=(.52, .23, .15), joint=(.31, .25, .21), stone=(.66, .56, .40), arch=(.61, .52, .37),
    trim=(.80, .75, .64), frame=(.09, .12, .11), glass=(.12, .14, .15), hardware=(.05, .05, .05), timber=(.42, .24, .12),
    sign=(.07, .13, .11), gold=(.78, .62, .30), roof=(.50, .44, .35), membrane=(.66, .61, .53), interior=(.78, .70, .58),
    floor=(.50, .40, .30), cobble=(.46, .44, .41), paver=(.52, .28, .22), concrete=(.67, .65, .61), asphalt=(.27, .27, .28),
    cream=(.86, .82, .70), brick2=(.56, .30, .21), metal=(.50, .48, .45), bronze=(.36, .27, .15), dial=(.93, .90, .80),
    globe=(.95, .94, .90), planting=(.30, .42, .20), clad=(.82, .78, .67), pot=(.62, .60, .56))


def manifest(version):
    h = TOP
    cams = G.camera_roster(X1 - X0 + 3.0, Y1 - Y0 + 3.0, h, [
        ('steam_clock', (15.0, -22.5, 3.6), (CLOCK[0], CLOCK[1], 4.3), 38),
        ('storefronts', (-1.0, -19.5, 2.2), (-1.0, Y0, 3.0), 30),
        ('name_frieze_pediment', (-2.0, -24.0, 9.0), (0.0, Y0, 16.2), 40),
        ('glass_close', (-5.2, -16.2, 12.2), (-5.2, Y0, 12.6), 40),             # one arched top-floor window: reveal, frame, fan
        ('architecture_close', (18.5, -17.5, 13.0), (X1, Y0, 14.5), 35),        # corner pier capital, frieze and bracketed cornice
        ('east_facade', (24.0, 10.0, 6.0), (X1, -2.0, 8.0), 30),
        ('facade_close', (-9.9, -31.0, 8.6), (-9.9, Y0, 8.6), 40),              # a typical south bay through all three floors
        ('roof_skylights', (16.0, -16.0, 30.0), (0.0, 1.0, ROOF), 35),
        ('interior', (-10.0, Y0 + 3.2, F2 + 1.7), (-4.0, Y0, F2 + 2.6), 22),
        ('rear_north', (-11.5, 30.0, 8.5), (-10.4, Y1, 7.5), 35)])         # down the gap west of the north block: the exposed north wall to grade
    for c in cams:                       # the locked front and oblique look from the south-east (fitted to the sources)
        if c['name'] == 'front':
            c.update(location=(35.2, -44.8, 1.6), target=(13.5, -19.2, 7.0), lens=49.5, whole=False)
        elif c['name'] == 'front_corner':
            c.update(location=(45.3, -49.3, 42.6), target=(-3.3, 2.5, 6.0), lens=57.0, whole=False)
        elif c['name'] == 'top':
            c.update(location=(0.0, -.7, 120.0), target=(0.0, -.699, 0.0), ortho_scale=45.0, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(27.0, -1.0, 7.0), target=(X1, -1.0, 8.5), lens=18, whole=False)   # from the east street, under the warehouses' eaves
        elif c['name'] == 'left_side':                                   # elevated over the lower west neighbours: west wall, parapet and footprint
            c.update(location=(-52.0, 2.0, 36.0), target=(X0 + 4.0, 1.0, 7.0), lens=32, whole=False)
        elif c['name'] == 'rear':                                        # elevated over the north block: north wall, parapet and footprint
            c.update(location=(4.0, 52.0, 38.0), target=(1.0, 2.0, 7.0), lens=32, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='gastown_heritage_commercial/variant_0 (brick and sandstone corner commercial block with the steam clock)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=3, storey_programme='ground-floor shops and two floors of offices',
            plan='26 m by 23.6 m corner block (top view), party walls to a lower neighbour on the west and a block on the north',
            facade='red brick with rusticated sandstone piers; south front of five bays (four wide arched-window bays and a paired corner bay), east front of a wide corner bay, four narrow sash bays and a paired-arch end bay; stone sill bands and lintels, carved pier capitals, lettered frieze and modillion cornice; pediment with an acanthus crest over the central bay',
            shopfronts='panelled bulkheads, plate glass, small-paned transoms, recessed timber doors, dark signboard fascia with gilt lettering and a moulded shop cornice',
            streetscape='brick sidewalks, cobbled south street, asphalt east street, steam clock, chained bollards, globe-cluster lamp posts, two street trees',
            levels_m=[G0, F2, F3, EAVE], roof_m=dict(eave=EAVE, parapet=PARA, pediment=EAVE + PED_RISE, top=TOP),
            inferred='interiors, the north and west walls above the neighbours and the roof penthouse interior follow the visible grammar; metric dimensions are authored teaching assumptions'),
        roof_contract=dict(type='flat tar roof inside a stone-coped parapet; chimney, stair penthouse, small skylight, two glazed pyramid skylights', datum_m=ROOF, crowns_m=[PARA, EAVE + PED_RISE]),
        identity_contract=dict(owner='three-storey red brick and sandstone Gastown corner block with arched top-floor windows, a lettered frieze, a bracketed cornice and pediment, shopfronts, and the steam clock on the corner'),
        material_contract=dict(profile='source-palette clay: red brick with dark joints, buff sandstone, dark green window frames and shop fascia, gilt lettering, tar roof, red brick paving and grey setts', textured_keeper=False),
        programme_contract=dict(storeys=3, ground='shops and a cafe', upper='offices'),
        contact_contract=['Grade-zero sidewalks and streets', 'Brick and stone walls from grade', 'Roof inside the parapet', 'Steam clock, bollards and lamp posts on the sidewalk'],
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
# ---- Gastown corner commercial block ----

def cyl(b, role, cx, cy, z0, z1, r, n=12):
    """Upright n-gon shaft added to a Batch."""
    frustum(b, role, cx, cy, z0, z1, r, r, n)


def frustum(b, role, cx, cy, z0, z1, r0, r1, n=12):
    """Upright n-gon frustum (radius r0 at z0, r1 at z1) added to a Batch; r1 = 0 gives a cone."""
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
    """Flat disc standing proud along a horizontal outward normal (a clock dial or a rosette)."""
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


def arch_head(f, h, rise, ring=.26, segs=10, ring_role='arch', dep=None):
    """Round head on a rectangular cut: wall infill above the curve (1 cm inside both faces, so it never shares a
    plane with the carrier) and a proud dressed ring over it."""
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
        for d in (-.07, .02):
            vs.append(f.p(pu, d, pz)); vs.append(f.p(pu + nu * ring, d, pz + nz * ring))
    for i in range(segs):
        a, b = 4 * i, 4 * (i + 1)
        fs += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3)]
    n = 4 * segs
    fs += [(0, 1, 3, 2), (n, n + 2, n + 3, n + 1)]
    C.mesh(f'{h["id"]} arch ring', vs, fs, ring_role, 'arches')
    return cz, R


def arched_window(m, b, f, h, inset=.2, occupied='office', fan=4):
    """Round-arched window of two or three lights: jambs, sill, a transom at the springing, mullions below it and a
    radial fanlight above; one pane fills the cut (the wall infill hides it outside the curve)."""
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    rise = w / 2
    spring = z + hh - rise
    per = .07
    lights = 3 if w > 2.0 else 2
    m.box('glass', u, inset + .04, z + hh / 2, w - .04, .01, hh - .04)
    for s in (-1, 1):
        m.box('frame', u + s * (w / 2 - per / 2), inset, (z + spring) / 2, per, .1, spring - z)
    m.box('frame', u, inset, z + per / 2, w - 2 * per, .1, per)
    m.box('frame', u, inset, spring, w - 2 * per, .1, .08)
    for i in range(1, lights):
        m.box('frame', u - w / 2 + w * i / lights, inset - .005, (z + spring) / 2, .06, .09, spring - z - 2 * per)
    m.box('frame', u, inset - .008, z + (spring - z) * .5, w - 2 * per, .085, .05)
    for i in range(fan):
        a = math.pi * (i + 1) / (fan + 1)
        r = rise - .05
        b.beam('frame', f.p(u + .1 * math.cos(a), inset, spring + .1 * math.sin(a)), f.p(u + r * math.cos(a), inset, spring + r * math.sin(a)), .05, .05)
    register(f, h, inset, 'window', occupied)


def runs(a, c, z0, z1, holes, pad=.04):
    """Stretches of a band between a and c that do not cross an opening."""
    cuts = sorted((h['u'] - h['w'] / 2 - pad, h['u'] + h['w'] / 2 + pad) for h in holes if h['z'] < z1 and h['z'] + h['h'] > z0)
    out, cur = [], a
    for s, e in cuts:
        if e <= cur or s >= c:
            continue
        if s > cur:
            out.append((cur, s))
        cur = max(cur, e)
    if cur < c:
        out.append((cur, c))
    return out


SOUTH = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south front')
EAST = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east front')
WEST = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west wall')
NORTH = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north wall')


def band(m, lo, hi, z0, z1, proj, role='stone'):
    """Horizontal member proud of a face: front at -proj, back 1 cm inside the wall (never on the face plane)."""
    m.box(role, (lo + hi) / 2, (-proj + .01) / 2, (z0 + z1) / 2, hi - lo, proj + .01, z1 - z0)


def rusticated(m, lo, hi, z0, z1, proj=.18, course=.56, inset=.07):
    """Rusticated sandstone pier: a recessed joint core with proud blocks; alternate courses inset at both ends."""
    m.box('joint', (lo + hi) / 2, (-proj + .05 + .01) / 2, (z0 + z1 - .02) / 2, hi - lo - .06, proj - .05 + .01, z1 - z0 - .02)
    n = max(1, round((z1 - z0) / course))
    hgt = (z1 - z0) / n
    for k in range(n):
        e = 0.0 if k % 2 == 0 else inset
        dz = .035 if k < n - 1 else 0.0
        m.box('stone', (lo + hi) / 2, (-proj + .01) / 2, z0 + hgt * k + (hgt - dz) / 2, hi - lo - 2 * e, proj + .01, hgt - dz)


def capital(m, lo, hi, z0, z1, proj=.24):
    """Carved stone pier capital: a proud block with a sunk panel and a raised rosette."""
    m.box('stone', (lo + hi) / 2, (-proj + .01) / 2, (z0 + z1) / 2, hi - lo + .12, proj + .01, z1 - z0)
    m.box('joint', (lo + hi) / 2, -proj - .004, (z0 + z1) / 2, hi - lo - .16, .012, z1 - z0 - .22)
    m.box('arch', (lo + hi) / 2, -proj - .03, (z0 + z1) / 2, min(.34, hi - lo - .3), .05, min(.34, z1 - z0 - .36))


FONT = {
    'A': ('.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'),
    'B': ('####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'),
    'C': ('.####', '#....', '#....', '#....', '#....', '#....', '.####'),
    'D': ('####.', '#...#', '#...#', '#...#', '#...#', '#...#', '####.'),
    'E': ('#####', '#....', '#....', '####.', '#....', '#....', '#####'),
    'F': ('#####', '#....', '#....', '####.', '#....', '#....', '#....'),
    'G': ('.####', '#....', '#....', '#.###', '#...#', '#...#', '.###.'),
    'H': ('#...#', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'),
    'I': ('.###.', '..#..', '..#..', '..#..', '..#..', '..#..', '.###.'),
    'K': ('#...#', '#..#.', '#.#..', '##...', '#.#..', '#..#.', '#...#'),
    'L': ('#....', '#....', '#....', '#....', '#....', '#....', '#####'),
    'M': ('#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#'),
    'N': ('#...#', '##..#', '#.#.#', '#..##', '#...#', '#...#', '#...#'),
    'O': ('.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'),
    'R': ('####.', '#...#', '#...#', '####.', '#.#..', '#..#.', '#...#'),
    'S': ('.####', '#....', '#....', '.###.', '....#', '....#', '####.'),
    'T': ('#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'),
    'U': ('#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'),
    'W': ('#...#', '#...#', '#...#', '#.#.#', '#.#.#', '##.##', '#...#'),
    '&': ('.##..', '#..#.', '.##..', '.#...', '#.#.#', '#..#.', '.##.#')}


def letters(m, text, u0, u1, zc, hgt, d, role='joint'):
    """Lettering in a 5 x 7 block face: each glyph row merged into runs of raised (or engraved) strokes, centred in
    the span u0..u1 at height zc."""
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
                m.box(role, start + (i * 6 + (c + e) / 2) * px, d, z, (e - c) * px, .02, px * 1.02)
                c = e


def shopfront(m, f, h, door=None, dw=1.7):
    """Recessed timber shopfront in a cut: panelled bulkhead, plate glass with mullions, a small-paned transom, and a
    pair of glazed doors set 0.6 m behind the glass line with framed returns (door: 'l', 'c', 'r' or None)."""
    u, w = h['u'], h['w']
    gl = .34                                                          # glass line inset
    a, c = u - w / 2, u + w / 2
    for e in (a + .023, c - .023):                                    # stone jamb liners close the cut from the face to the frame
        m.box('stone', e, (gl - .03) / 2, (G0 + SHOP) / 2, .042, gl + .03, SHOP - G0 - .004)
    m.box('frame', a + .05, gl, (G0 + SHOP) / 2, .1, .12, SHOP - G0)
    m.box('frame', c - .05, gl, (G0 + SHOP) / 2, .1, .12, SHOP - G0)
    m.box('frame', u, gl, SHOP - .06, w - .2, .12, .12)
    m.box('frame', u, gl, 3.42, w - .2, .12, .1)                       # transom bar
    m.box('glass', u, gl + .05, (3.47 + SHOP - .12) / 2, w - .2, .01, SHOP - .12 - 3.47)
    nt = max(3, round((w - .2) / .32))
    for i in range(1, nt):
        m.box('frame', a + .1 + (w - .2) * i / nt, gl - .01, (3.47 + SHOP - .12) / 2, .035, .06, SHOP - .12 - 3.47)
    m.box('frame', u, gl - .012, (3.47 + SHOP - .12) / 2, w - .2, .06, .035)
    if door:
        dc = {'l': a + .1 + dw / 2, 'r': c - .1 - dw / 2, 'c': u}[door]
        spans = [(a + .1, dc - dw / 2), (dc + dw / 2, c - .1)]
    else:
        spans = [(a + .1, c - .1)]
    dd = gl + .6
    for s0, s1 in spans:
        if s1 - s0 < .2:
            continue
        sm = (s0 + s1) / 2
        m.box('frame', sm, gl, (G0 + .82) / 2, s1 - s0, .14, .82 - G0)                      # bulkhead
        m.box('sign', sm, gl - .075, (G0 + .82) / 2, s1 - s0 - .24, .01, .82 - G0 - .22)       # sunk bulkhead panel
        m.box('frame', sm, gl, .87, s1 - s0, .14, .1)
        m.box('glass', sm, gl + .05, (.92 + 3.37) / 2, s1 - s0, .01, 3.37 - .92)
        nl = max(1, round((s1 - s0) / 1.4))
        for i in range(1, nl):
            m.box('frame', s0 + (s1 - s0) * i / nl, gl - .01, (.92 + 3.37) / 2, .07, .1, 3.37 - .92)
    if door:
        for s in (-1, 1):                                                                   # framed returns to the door
            m.box('frame', dc + s * (dw / 2 + .03), (gl + dd) / 2, (G0 + 3.37) / 2, .06, dd - gl, 3.37 - G0)
            m.box('glass', dc + s * (dw / 2 + .065), (gl + dd) / 2, (.92 + 3.37) / 2, .01, dd - gl - .1, 3.37 - .92)
        m.box('frame', dc, (gl + dd) / 2, 3.42, dw + .12, dd - gl, .1)
        m.box('stone', dc, (gl + dd) / 2, G0 - .03, dw + .1, dd - gl + .1, .06)
        for s in (-1, 1):
            lc = dc + s * dw / 4
            m.box('timber', lc, dd, (G0 + 3.37) / 2, dw / 2 - .03, .07, 3.37 - G0 - .02)
            m.box('glass', lc, dd - .045, 2.2, dw / 2 - .3, .01, 1.7)
            m.box('timber', lc, dd - .05, .9, dw / 2 - .3, .02, .7)
            m.box('hardware', dc + s * .12, dd - .06, 1.6, .03, .03, .5)
    register(f, h, gl, 'shopfront', 'shop')


def sash(m, f, h, inset=.18, cols=1, rows=2, transom=False, lintel=True):
    """Window with a stone sill and a flat stone lintel; transom: a bar at three quarters of the height."""
    framed(m, f, h, cols=cols, rows=rows, inset=inset, occupied='office', frame='frame')
    if transom:
        m.box('frame', h['u'], inset - .01, h['z'] + h['h'] * .74, h['w'] - .14, .1, .07)
        for i in range(1, cols * 2):
            m.box('frame', h['u'] - h['w'] / 2 + h['w'] * i / (cols * 2), inset - .012, h['z'] + h['h'] * .87, .03, .07, h['h'] * .24)
    m.box('stone', h['u'], -.06, h['z'] - .07, h['w'] + .26, .16, .14)
    if lintel:
        m.box('stone', h['u'], -.05, h['z'] + h['h'] + .17, h['w'] + .36, .12, .34)
        m.box('arch', h['u'], -.085, h['z'] + h['h'] + .19, .26, .06, .4)                  # keystone


def south_front():
    f = SOUTH
    holes, kind = [], []
    doors = ['l', 'r', 'c', None, 'r']
    for i, (a, c) in enumerate(S_BAYS):
        u = (a + c) / 2
        holes.append(hole(f'S shop {i}', u, G0, c - a, SHOP - G0)); kind.append(('shop', doors[i]))
        if i < 4:
            holes.append(hole(f'S f2 {i}', u, W2Z, 2.6, W2H)); kind.append(('f2wide', None))
            holes.append(hole(f'S f3 {i}', u, W3Z, 2.5, W3H)); kind.append(('arch', None))
        else:
            for s in (-1, 1):
                holes.append(hole(f'S f2 {i}{s:+d}', u + s * 1.15, W2Z, 1.5, W2H)); kind.append(('f2pair', None))
                holes.append(hole(f'S f3 {i}{s:+d}', u + s * 1.15, W3Z, 1.5, W3H)); kind.append(('arch', None))
    f.wall('south front carrier', X0, X1 - EPS, 0.0, PARA, depth=T, role='wall', holes=holes)
    G.brick_courses(f, X0 + .02, X1 - .02, SHOPC + .1, FRIEZE0 - .25, holes, spacing=.42)
    return f, holes, kind


def east_front():
    f = EAST
    holes, kind = [], []
    u = sum(E_CORNER) / 2
    holes.append(hole('E shop corner', u, G0, E_CORNER[1] - E_CORNER[0], SHOP - G0)); kind.append(('shop', 'l'))
    holes.append(hole('E f2 corner', u, W2Z, 2.8, W2H)); kind.append(('f2wide', None))
    holes.append(hole('E f3 corner', u, W3Z, 2.6, W3H)); kind.append(('arch', None))
    for k, y in enumerate(E_NARROW):
        holes.append(hole(f'E g {k}', y, 1.45, 1.15, 2.55)); kind.append(('narrow', None))
        holes.append(hole(f'E f2 {k}', y, W2Z + .1, 1.1, 2.7)); kind.append(('narrow', None))
        holes.append(hole(f'E f3 {k}', y, W3Z + .1, 1.1, 2.9)); kind.append(('narrow', None))
    ue = sum(E_END) / 2
    for s in (-1, 1):
        holes.append(hole(f'E f2 end{s:+d}', ue + s * 1.35, W2Z, 1.3, W2H)); kind.append(('f2pair', None))
        holes.append(hole(f'E f3 end{s:+d}', ue + s * 1.35, W3Z, 1.3, W3H - .1)); kind.append(('arch', None))
    holes.append(hole('E door end', ue - 1.35, G0, 1.4, 3.3, kind='door')); kind.append(('door', None))
    holes.append(hole('E g end', ue + 1.35, 1.45, 1.3, 2.55)); kind.append(('narrow', None))
    f.wall('east front carrier', Y0 + T, Y1 - EPS, 0.0, PARA, depth=T, role='wall', holes=holes)
    G.brick_courses(f, Y0 + T + .02, Y1 - .02, 1.25, FRIEZE0 - .25, [h for h in holes] + [hole('E corner shop zone', u, 0.0, E_CORNER[1] - E_CORNER[0] + 1.0, SHOPC + .1)], spacing=.42)
    return f, holes, kind


def dress(f, holes, kind, label):
    m = Merge(f)
    b = Batch()
    for h, (k, door) in zip(holes, kind):
        if k == 'shop':
            shopfront(m, f, h, door)
        elif k == 'f2wide':
            sash(m, f, h, cols=3, rows=1, transom=True, lintel=False)
        elif k == 'f2pair':
            sash(m, f, h, cols=1, rows=2, transom=True, lintel=False)
        elif k == 'narrow':
            sash(m, f, h, cols=1, rows=2)
        elif k == 'arch':
            arched_window(m, b, f, h)
            arch_head(f, h, h['w'] / 2, ring=.24, segs=10)
            m.box('arch', h['u'], -.1, h['z'] + h['h'] + .14, .3, .14, .42)                 # keystone
            m.box('stone', h['u'], -.06, h['z'] - .07, h['w'] + .26, .16, .14)
        elif k == 'door':
            u, top = h['u'], h['z'] + h['h']
            m.box('timber', u, T - .2, (G0 + 2.6) / 2, h['w'] - .02, .08, 2.6 - G0)
            m.box('frame', u, T - .2, 2.65, h['w'] - .02, .1, .1)
            m.box('glass', u, T - .25, (2.7 + top - .05) / 2, h['w'] - .12, .01, top - .05 - 2.7)
            m.box('glass', u, T - .25, 1.95, h['w'] - .5, .01, .9)
            m.box('hardware', u + .45, T - .26, 1.3, .04, .04, .2)
            m.box('stone', u, -.06, top + .17, h['w'] + .5, .12, .34)
            m.box('stone', u, .3, G0 / 2, h['w'], .6, G0)
            register(f, h, T - .2, 'door', 'stair hall')
    m.flush(label)
    b.flush(label + ' fanlights')
    return m


def bands_and_piers():
    # South front: bands run past the corner by their projection (the east runs butt their back face) and to the
    # west end, where the cornice returns over the lower neighbour.
    f = SOUTH
    m = Merge(f)
    z_sign0, z_sign1 = SHOP + .05, FASCIA - .02
    for a, c in S_BAYS:
        band(m, a + .02, c - .02, z_sign0, z_sign1, .1, 'sign')                                 # signboards
    letters(m, 'THE STEAM CLOCK CAFE', S_BAYS[2][0] + .12, S_BAYS[2][1] - .12, (z_sign0 + z_sign1) / 2, .32, -.105, 'gold')
    letters(m, 'BOOKS', S_BAYS[0][0] + .6, S_BAYS[0][1] - .6, (z_sign0 + z_sign1) / 2, .3, -.105, 'gold')
    letters(m, 'TEA', S_BAYS[1][0] + .9, S_BAYS[1][1] - .9, (z_sign0 + z_sign1) / 2, .3, -.105, 'gold')
    letters(m, 'OAK & IRON GIFTS', 7.4, 11.5, (z_sign0 + z_sign1) / 2, .3, -.105, 'gold')
    for z0, z1, proj, e_w, role in ((FASCIA, FASCIA + .14, .26, .26, 'stone'), (FASCIA + .14, SHOPC, .38, .38, 'stone'),
                                    (W2Z - .2, W2Z - .04, .12, .12, 'stone'), (W2Z + W2H + .02, W2Z + W2H + .38, .1, .1, 'stone'),
                                    (W3Z - .2, W3Z - .04, .12, .12, 'stone'), (FRIEZE0 - .24, FRIEZE0, .2, .2, 'stone'),
                                    (FRIEZE0, FRIEZE1, .16, .16, 'stone'), (FRIEZE1, FRIEZE1 + .2, .3, .3, 'stone'),
                                    (EAVE - .3, EAVE, .95, .95, 'stone'), (EAVE, EAVE + .07, .86, .86, 'trim')):
        band(m, X0 - e_w if z0 > 12.8 else X0 + .01, X1 + proj, z0, z1, proj, role)
    n = int((X1 - X0) / .66)
    for i in range(n + 1):                                                                       # paired modillion brackets
        u = X0 + .25 + (X1 - X0 - .5) * i / n
        m.box('stone', u, -.42, FRIEZE1 + .2 + (EAVE - .3 - FRIEZE1 - .2) / 2, .2, .82, EAVE - .3 - FRIEZE1 - .2)
    for i in range(int((X1 - X0) / .2)):                                                         # dentils under the corona
        m.box('arch', X0 + .1 + i * .2, -.4, EAVE - .37, .1, .1, .12)
    letters(m, 'GASTOWN COMMERCE BUILDING', -10.6, 5.6, (FRIEZE0 + FRIEZE1) / 2, .4, -.165)
    for k, (a, c) in enumerate(S_PIERS):
        if k == len(S_PIERS) - 1:
            continue                                                                             # the corner pier is built in corner()
        if k == 0:
            rusticated(m, a, c, 0.0, FRIEZE0 - .24)
        else:
            rusticated(m, a, c, 0.0, FASCIA, proj=.2)
            m.box('wall', (a + c) / 2, -.07, (SHOPC + FRIEZE0 - .24) / 2, c - a, .16, FRIEZE0 - .24 - SHOPC)   # brick pilaster, proud of the bands
        capital(m, a, c, W3Z + 1.75, W3Z + 2.55)
        if k in (0, 4):                                                                          # the lettering runs over the inner piers
            capital(m, a, c, FRIEZE0 + .04, FRIEZE1 - .04, proj=.3)
    m.flush('south bands and piers')
    # East front: bands from the corner (butting the south runs) to the north end.
    f = EAST
    m = Merge(f)
    for a, c in (E_CORNER,):
        band(m, a + .02, c - .02, z_sign0, z_sign1, .1, 'sign')
    letters(m, 'OAK & IRON GIFTS', a + .4, c - .4, (z_sign0 + z_sign1) / 2, .3, -.105, 'gold')
    for z0, z1, proj, role in ((FASCIA, FASCIA + .14, .26, 'stone'), (FASCIA + .14, SHOPC, .38, 'stone'),
                               (W2Z - .2, W2Z - .04, .12, 'stone'), (W2Z + W2H + .02, W2Z + W2H + .38, .1, 'stone'),
                               (W3Z - .2, W3Z - .04, .12, 'stone'), (FRIEZE0 - .24, FRIEZE0, .2, 'stone'),
                               (FRIEZE0, FRIEZE1, .16, 'stone'), (FRIEZE1, FRIEZE1 + .2, .3, 'stone'),
                               (EAVE - .3, EAVE, .95, 'stone'), (EAVE, EAVE + .07, .86, 'trim')):
        hi = E_PIERS[1][1] if z0 < SHOPC - .01 else (Y1 + proj if z0 > 12.8 else Y1 - .01)
        band(m, Y0 + .01, hi, z0, z1, proj, role)
    n = int((Y1 - Y0) / .66)
    for i in range(n + 1):
        u = Y0 + .5 + (Y1 - Y0 - .75) * i / n
        m.box('stone', u, -.42, FRIEZE1 + .2 + (EAVE - .3 - FRIEZE1 - .2) / 2, .2, .82, EAVE - .3 - FRIEZE1 - .2)
    for i in range(int((Y1 - Y0 - .3) / .2)):
        m.box('arch', Y0 + .35 + i * .2, -.4, EAVE - .37, .1, .1, .12)
    band(m, E_NARROW[0] - 1.25, E_PIERS[2][0], .0, 1.2, .12, 'stone')                            # stone plinth under the narrow bays
    band(m, E_PIERS[2][1], 5.86, .0, 1.2, .12, 'stone')
    band(m, 7.34, E_PIERS[3][0], .0, 1.2, .12, 'stone')
    for k, (a, c) in enumerate(E_PIERS):
        if k == 0:
            continue
        if k == len(E_PIERS) - 1:
            rusticated(m, a, c, 0.0, FRIEZE0 - .24)
        else:
            rusticated(m, a, c, 0.0, FASCIA if k == 1 else 1.25, proj=.2)
            z0 = SHOPC if k == 1 else 1.25
            m.box('wall', (a + c) / 2, -.07, (z0 + FRIEZE0 - .24) / 2, c - a, .16, FRIEZE0 - .24 - z0)
        capital(m, a, c, W3Z + 1.75, W3Z + 2.55)
        capital(m, a, c, FRIEZE0 + .04, FRIEZE1 - .04, proj=.3)
    m.flush('east bands and piers')


def corner():
    """Rusticated sandstone corner pier wrapping both street fronts, with carved capitals."""
    b = Batch()
    x0, x1 = S_PIERS[-1][0], X1 + .2
    y0, y1 = Y0 - .2, E_PIERS[0][1]
    z1 = FRIEZE0 - .24
    b.box('joint', (x0 + .06 + x1 - .05) / 2, (y0 + .05 + y1 - .06) / 2, z1 / 2 - .01, x1 - .05 - x0 - .06, y1 - .06 - y0 - .05, z1 - .02)
    n = round(z1 / .56)
    hgt = z1 / n
    for k in range(n):
        dz = .035 if k < n - 1 else 0.0
        e = 0.0 if k % 2 == 0 else .07
        b.box('stone', (x0 + e + x1) / 2, (y0 + y1 - e) / 2, hgt * k + (hgt - dz) / 2, x1 - x0 - e, y1 - y0 - e, hgt - dz)
    for z0, z1_, pr in ((W3Z + 1.75, W3Z + 2.55, .26), (FRIEZE0 + .04, FRIEZE1 - .04, .32)):
        b.box('stone', (x0 - .06 + X1 + pr) / 2, (Y0 - pr + y1 + .06) / 2, (z0 + z1_) / 2, X1 + pr - x0 + .06, y1 + .06 - Y0 + pr, z1_ - z0)
    b.flush('corner pier')
    m = Merge(SOUTH)
    m.box('joint', (x0 + X1) / 2, -.264, (W3Z + 1.75 + W3Z + 2.55) / 2, X1 - x0 - .16, .012, .58)
    m.flush('corner capital panel south')
    m = Merge(EAST)
    m.box('joint', (Y0 + y1) / 2, -.264, (W3Z + 1.75 + W3Z + 2.55) / 2, y1 - Y0 - .16, .012, .58)
    m.flush('corner capital panel east')


def plain_walls():
    """West and north walls: common brick above the neighbours, a few windows, a coped parapet."""
    f = WEST
    holes = [hole(f'W f{k} {u:+.1f}', u, z, 1.1, 2.4) for u in (-9.0, -5.0) for k, z in ((2, 6.6), (3, 11.2))]
    f.wall('west wall carrier', -Y1, -(Y0 + T) - EPS, 0.0, PARA, depth=T, role='wall', holes=holes)
    G.brick_courses(f, -Y1 + .02, -(Y0 + T) - .02, 12.7, PARA - .3, holes, spacing=.42)
    m = Merge(f)
    for h in holes:
        sash(m, f, h, lintel=False)
    m.flush('west wall')
    f = NORTH
    holes = [hole(f'N f{k} {u:+.1f}', u, z, 1.1, 2.4) for u in (-11.8, -10.4) for k, z in ((2, 6.6), (3, 11.2))]
    f.wall('north wall carrier', -(X1 - T), -(X0 + T) - EPS, 0.0, PARA, depth=T, role='wall', holes=holes)
    G.brick_courses(f, -(X1 - T) + .02, -(X0 + T) - .02, 1.0, PARA - .3, holes, spacing=.42)
    m = Merge(f)
    for h in holes:
        sash(m, f, h, lintel=False)
    m.flush('north wall')
    b = Batch()                                                    # stone coping on the whole parapet ring (four runs, no overlap)
    zc0, zc1 = PARA - .001, PARA + .14
    b.box('trim', 0.0, Y0 + T / 2, (zc0 + zc1) / 2, X1 - X0 + .16, T + .16, zc1 - zc0)
    b.box('trim', 0.0, Y1 - T / 2, (zc0 + zc1) / 2, X1 - X0 + .16, T + .16, zc1 - zc0)
    b.box('trim', X0 + T / 2, 0.0, (zc0 + zc1 + .002) / 2, T + .16, Y1 - Y0 - 2 * T - .16, zc1 - zc0 - .002)
    b.box('trim', X1 - T / 2, 0.0, (zc0 + zc1 + .002) / 2, T + .16, Y1 - Y0 - 2 * T - .16, zc1 - zc0 - .002)
    b.flush('parapet coping')
    b = Batch()                                                    # light render on the parapet's inner faces (top, oblique)
    zl0, zl1 = ROOF - .01, PARA - .005
    b.box('trim', 0.0, Y0 + T + .0125, (zl0 + zl1) / 2, X1 - X0 - 2 * T - .002, .035, zl1 - zl0)
    b.box('trim', 0.0, Y1 - T - .0125, (zl0 + zl1) / 2, X1 - X0 - 2 * T - .002, .035, zl1 - zl0)
    b.box('trim', X0 + T + .0125, 0.0, (zl0 + zl1) / 2, .035, Y1 - Y0 - 2 * T - .072, zl1 - zl0)
    b.box('trim', X1 - T - .0125, 0.0, (zl0 + zl1) / 2, .035, Y1 - Y0 - 2 * T - .072, zl1 - zl0)
    b.flush('parapet liner')


def pediment():
    """Pediment over the central bay on the cornice: stone tympanum with an acanthus shell, raking cornices, an
    acroterion crest and short pedestals at both ends."""
    xc = (S_BAYS[2][0] + S_BAYS[2][1]) / 2
    zb = EAVE - .04
    yf = Y0 - .25
    C.prism('Pediment tympanum', [(xc - PED_W / 2, zb), (xc + PED_W / 2, zb), (xc, zb + PED_RISE)], 'y', yf, Y0 + T, 'stone', 'pediment')
    b = Batch()
    th = math.atan2(PED_RISE, PED_W / 2)
    lift = .10 / math.cos(th)                                    # cornice centre .10 m above the slope (normal), so its underside overlaps the tympanum
    ov = .12                                                     # raking ends die 0.12 m into the pedestals
    for s in (-1, 1):
        a0 = (xc + s * (PED_W / 2 + ov), yf - .2, zb - ov * math.tan(th) + lift)
        c0 = (xc, yf - .2, zb + PED_RISE + lift)
        yb = Y0 + T - .05                                        # raking cornices run over the full tympanum depth: a closed sloping back
        ym = (yf - .45 + yb) / 2
        b.beam('stone', (a0[0], ym, a0[2]), (c0[0], ym, c0[2]), yb - (yf - .45), .34)
        b.beam('trim', (a0[0], ym - .01, a0[2] + .22), (c0[0], ym - .01, c0[2] + .22), yb - (yf - .45) - .06, .12)
        b.box('stone', xc + s * (PED_W / 2 + .45), (Y0 - .78 + Y0 + T) / 2, (EAVE + PARA + .5) / 2, .9, T + .78, PARA + .5 - EAVE)   # end pedestals, deeper than the raking cornice
        b.box('trim', xc + s * (PED_W / 2 + .45), (Y0 - .78 + Y0 + T) / 2, PARA + .57, 1.04, T + .92, .14)
    za = zb + PED_RISE + lift
    b.box('stone', xc, (yf - .5 + Y0 + T - .03) / 2, za + .12, .8, Y0 + T - .03 - (yf - .5), .62)   # apex block over the cornice mitre, full depth
    for k in range(9):                                                                           # acanthus shell in the tympanum
        a = math.pi * (k + .5) / 9
        r = .95
        b.beam('arch', (xc, yf - .06, zb + .35), (xc + r * math.cos(a), yf - .06, zb + .35 + r * math.sin(a)), .12, .1)
    disc(b, 'arch', (xc, yf - .005, zb + .35), (0, -1), .32, t=.12)
    zc = za + .42                                                                                # palmette crest on the apex block: one solid silhouette, no crevices
    pal = [(-.33, 0.0), (-.5, .22), (-.64, .44), (-.44, .44), (-.48, .72), (-.27, .62), (-.24, .96), (0.0, 1.18),
           (.24, .96), (.27, .62), (.48, .72), (.44, .44), (.64, .44), (.5, .22), (.33, 0.0)]
    C.prism('Pediment crest', [(xc + px, zc - .02 + pz) for px, pz in pal], 'y', yf - .36, yf - .04, 'arch', 'pediment')
    b.flush('pediment')


def roof():
    b = Batch()
    b.box('roof', 0.0, 0.0, ROOF - .14, X1 - X0 - 2 * T + .002, Y1 - Y0 - 2 * T + .002, .28)
    for k in range(1, 12):                                                                       # membrane laps
        b.box('membrane', 0.0, Y0 + T + (Y1 - Y0 - 2 * T) * k / 12, ROOF + .006, X1 - X0 - 2 * T - .1, .06, .012)
    chimney(b, -7.0, 6.0, ROOF - .1, ROOF + 2.6, w=1.2, d=1.2, pots=0, role='brick2', cap='stone')
    # Clapboard stair penthouse with a door and a window (top, oblique).
    px0, px1, py0, py1, ph = -.9, 3.0, 4.8, 11.0, 2.8
    b.box('clad', (px0 + px1) / 2, (py0 + py1) / 2, ROOF + ph / 2 - .05, px1 - px0, py1 - py0, ph + .1)
    b.box('membrane', (px0 + px1) / 2, (py0 + py1) / 2, ROOF + ph + .06, px1 - px0 + .3, py1 - py0 + .3, .12)
    for k in range(1, 10):
        b.box('joint', (px0 + px1) / 2, py0 - .006, ROOF + ph * k / 10, px1 - px0, .012, .02)
        b.box('joint', px1 + .006, (py0 + py1) / 2, ROOF + ph * k / 10 + .01, .012, py1 - py0, .02)
    b.box('frame', 1.9, py0 - .02, ROOF + 1.05, 1.0, .05, 2.1)
    b.box('timber', 1.9, py0 - .045, ROOF + 1.02, .86, .02, 1.98)
    b.box('frame', .2, py0 - .02, ROOF + 1.8, .9, .05, .8)
    b.box('glass', .2, py0 - .045, ROOF + 1.8, .76, .02, .66)
    b.box('metal', 3.6, 6.2, ROOF + .45, .9, .9, .9)                                              # vent box
    # Small hipped skylight and two glazed pyramid skylights on curbs (top).
    for (x, y, w, d, rise) in ((1.0, 2.65, 1.8, 1.3, .55), (-4.25, -2.35, 2.4, 2.2, 1.0), (3.8, -2.35, 2.4, 2.2, 1.0)):
        b.box('membrane', x, y, ROOF + .2, w + .2, d + .2, .42)
        z0 = ROOF + .41
        for s in (-1, 1):
            for t in (-1, 1):
                b.beam('frame', (x + s * w / 2, y + t * d / 2, z0), (x + s * (w / 2 - min(w, d) / 2), y + t * (d / 2 - min(w, d) / 2), z0 + rise), .06, .06)
        for s in (-1, 1):
            b.beam('frame', (x, y + s * d / 2, z0), (x, y, z0 + rise), .05, .05)
            b.beam('frame', (x + s * w / 2, y, z0), (x, y, z0 + rise), .05, .05)
    b.flush('roof')
    for (x, y, w, d, rise) in ((1.0, 2.65, 1.8, 1.3, .55), (-4.25, -2.35, 2.4, 2.2, 1.0), (3.8, -2.35, 2.4, 2.2, 1.0)):
        ax = 'x' if w >= d else 'y'
        pitched_roof(f'Skylight {x:+.1f}', x - w / 2, x + w / 2, y - d / 2, y + d / 2, ROOF + .41, rise, True, True, ax, .02, 'glass', 'roof')


def inside():
    i = T + .01
    pts = [(X0 + i, Y0 + i), (X1 - i, Y0 + i), (X1 - i, Y1 - i), (X0 + i, Y1 - i)]
    for z in (G0, F2, F3):
        C.prism(f'Floor {z:.1f}', pts, 'z', z - .24 if z > 1 else 0.0, z, 'floor', 'inside')
    b = Batch()
    for z, top in ((G0, F2 - .25), (F2, F3 - .25), (F3, ROOF - .3)):
        b.box('interior', 0.0, Y0 + 3.6, (z + top) / 2, X1 - X0 - 2 * T - .4, .16, top - z)            # back partitions
        b.box('interior', X1 - 3.6, 0.0, (z + top) / 2 - .005, .16, Y1 - Y0 - 2 * T - .4, top - z - .01)
    b.flush('partitions')
    for x, y in ((-8.0, -9.0), (0.0, -9.0), (8.0, -9.0), (10.5, -4.0), (10.5, 4.0), (0.0, 2.0)):
        for z in (G0, F2, F3):
            C.qa_room_light(f'Room {x:+.0f} {y:+.0f} {z:.0f}', (x, y, z + 2.6), 18, 2.5)
    C.CONTACTS.append(dict(name='Brick and sandstone walls from grade; roof inside the parapet; pediment on the cornice', eave_m=EAVE))


def steam_clock():
    """The Gastown steam clock: granite base, bronze pedestal, glazed cabinet with the brass works, a four-faced
    clock head above the shop cornice, a small roof with steam whistles (sized from the front source)."""
    x, y = CLOCK
    SV, SH, Z0 = 1.42, 1.3, .14                                     # vertical and horizontal scale about the sidewalk
    def Z(z):
        return Z0 + (z - Z0) * SV
    class _S:                                                       # scaled proxy over the batch
        def box(self, role, bx, by, bz, sx, sy, sz):
            b.box(role, x + (bx - x) * SH, y + (by - y) * SH, Z(bz), sx * SH, sy * SH, sz * SV)
        def beam(self, role, p0, p1, w, h):
            P = lambda p: (x + (p[0] - x) * SH, y + (p[1] - y) * SH, Z(p[2]))
            b.beam(role, P(p0), P(p1), w * SH, h * SH)
    b = Batch()
    q = _S()
    q.box('stone', x, y, .14 + .2, 1.25, 1.25, .4)
    q.box('bronze', x, y, .54 + .45, 1.0, 1.0, .9)
    q.box('bronze', x, y, 1.44 + .08, 1.1, 1.1, .16)
    for s in (-1, 1):
        for axis in ('x', 'y'):
            if axis == 'x':
                q.box('gold', x + s * .505, y, .99, .02, .6, .5)
            else:
                q.box('gold', x, y + s * .505, .99, .6, .02, .5)
    q.box('bronze', x, y, 1.6 + 1.05, .56, .56, 2.1)                                              # cabinet core
    for s in (-1, 1):
        for axis in ('x', 'y'):
            dx, dy = (s, 0.0) if axis == 'x' else (0.0, s)
            sx, sy = (.02, .66) if axis == 'x' else (.66, .02)
            q.box('glass', x + dx * .38, y + dy * .38, 2.65, sx, sy, 1.9)                         # glazed sides
            q.box('gold', x + dx * .31, y + dy * .31, 2.55, .04 if axis == 'x' else .3, .3 if axis == 'x' else .04, 1.2)   # brass works
            q.box('bronze', x + dx * .38, y + dy * .38, 1.65, sx + .04 if axis == 'x' else .7, sy + .04 if axis == 'y' else .7, .1)
            q.box('bronze', x + dx * .38, y + dy * .38, 3.65, sx + .04 if axis == 'x' else .7, sy + .04 if axis == 'y' else .7, .1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            q.box('bronze', x + sx * .38, y + sy * .38, 2.65, .1, .1, 2.1)                         # corner posts
    q.box('bronze', x, y, 3.78, .98, .98, .16)
    q.box('bronze', x, y, 3.86 + .42, .92, .92, .84)                                              # clock head
    q.box('gold', x, y, 4.75, 1.02, 1.02, .1)
    frustum(b, 'bronze', x, y, Z(4.8), Z(5.25), .62 * SH, .2 * SH, 4)
    for dx in (-.15, 0.0, .15):
        cyl(b, 'gold', x + dx * SH, y, Z(5.2), Z(5.55 + (.1 if dx == 0 else 0)), .05 * SH, 8)
    for nx, ny in ((0, -1), (0, 1), (1, 0), (-1, 0)):
        c = (x + nx * .46 * SH, y + ny * .46 * SH, Z(4.28))
        disc(b, 'gold', c, (nx, ny), .38 * SH, t=.02)
        disc(b, 'dial', (c[0] + nx * .02, c[1] + ny * .02, c[2]), (nx, ny), .33 * SH, t=.015)
        tx, ty = -ny, nx
        b.beam('hardware', (c[0] + nx * .04, c[1] + ny * .04, c[2]), (c[0] + nx * .04 + tx * .26, c[1] + ny * .04 + ty * .26, c[2] + .1), .035, .012)
        b.beam('hardware', (c[0] + nx * .045, c[1] + ny * .045, c[2]), (c[0] + nx * .045, c[1] + ny * .045, c[2] + .34), .03, .012)
    b.flush('steam clock')
    # Chained bollards on the curb round the clock (front).
    b = Batch()
    posts = [(x - 2.6, -15.15), (x - 1.0, -15.15), (x + .6, -15.15), (x + 2.2, -15.15), (x + 3.6, -14.4)]
    for px, py in posts:
        cyl(b, 'hardware', px, py, .14, 1.0, .07, 10)
        frustum(b, 'hardware', px, py, 1.0, 1.12, .09, .03, 10)
    for (ax, ay), (cx, cy) in zip(posts, posts[1:]):
        mx, my = (ax + cx) / 2, (ay + cy) / 2
        b.beam('hardware', (ax, ay, .9), (mx, my, .62), .025, .025)
        b.beam('hardware', (mx, my, .62), (cx, cy, .9), .025, .025)
    b.flush('bollards')


def lamp(x, y, z=.14):
    """Globe-cluster lamp post: fluted base, shaft, crossarms with four globes and a top globe."""
    b = Batch()
    frustum(b, 'hardware', x, y, z, z + .9, .2, .11, 10)
    cyl(b, 'hardware', x, y, z + .9, z + 3.6, .07, 10)
    b.box('hardware', x, y, z + 3.62, .9, .06, .06)
    b.box('hardware', x, y, z + 3.62, .06, .9, .06)
    b.flush('lamp post')
    for dx, dy in ((.42, 0), (-.42, 0), (0, .42), (0, -.42)):
        A.foliage('Lamp globe', (x + dx, y + dy, z + 3.86), (.17, .17, .17), role='globe', detail=2)
    A.foliage('Lamp globe', (x, y, z + 4.2), (.19, .19, .19), role='globe', detail=2)


def windows_grid(m, lo, hi, z0, z1, floors, per, w=1.1, hh=1.9, role='glass', frame='trim'):
    """Dark window panes with a light frame on a context facade (Merge in face coordinates, proud by a few mm)."""
    n = max(1, int((hi - lo) / per))
    for k in range(n):
        u = lo + (hi - lo) * (k + .5) / n
        for j in range(floors):
            z = z0 + (z1 - z0) * j / floors + .9
            m.box(frame, u, -.03, z + hh / 2, w + .16, .06, hh + .16)
            m.box(role, u, -.065, z + hh / 2, w, .02, hh)


def context():
    """Neighbours: a lower cream block on the west, a brick block across the lane, a brick block on the north and a
    row of brick warehouses across the east street."""
    b = Batch()
    for name, x0, x1, y0, y1, h, role in (('west neighbour', -26.0, X0 + .1, Y0 + .05, -1.8, 12.6, 'cream'),
                                          ('north-west block', -26.0, -15.6, -1.8, 16.0, 11.0, 'brick2'),
                                          ('north block', -8.1, X1 - .05, Y1 - .1, 24.0, 13.4, 'brick2'),
                                          ('east warehouse 1', 31.5, 42.0, -27.0, -12.0, 17.5, 'brick2'),
                                          ('east warehouse 2', 31.5, 42.0, -12.0, 2.0, 20.5, 'wall'),
                                          ('east warehouse 3', 31.5, 42.0, 2.0, 16.0, 15.8, 'brick2'),
                                          ('east warehouse 4', 31.5, 42.0, 16.0, 30.0, 19.0, 'wall')):
        b.box(role, (x0 + x1) / 2, (y0 + y1) / 2, h / 2, x1 - x0, y1 - y0, h)
        b.box('membrane', (x0 + x1) / 2, (y0 + y1) / 2, h + .03, x1 - x0 - .5, y1 - y0 - .5, .06)
    b.box('stone', (-26.0 + X0) / 2, Y0 - .15, 12.1, X0 + 26.0 - .1, .42, .5)                      # cream neighbour cornice
    b.box('sign', (-26.0 + X0) / 2, Y0 - .03, 4.4, X0 + 26.0 - .2, .18, .6)
    for y0, y1, h in ((-27.0, -12.0, 17.5), (-12.0, 2.0, 20.5), (2.0, 16.0, 15.8), (16.0, 30.0, 19.0)):
        b.box('stone', 31.5 - .15, (y0 + y1) / 2, h - .4, .42, y1 - y0 - .04, .5)                  # warehouse cornices
    b.flush('context')
    f = C.Face((0, Y0 + .05, 0), (1, 0, 0), (0, 1, 0), 'west neighbour front')
    m = Merge(f)
    windows_grid(m, -25.5, X0 - .5, 5.0, 12.0, 2, 2.6, w=1.0, hh=2.2)
    for k in range(4):
        u = -24.5 + 3.0 * k
        m.box('glass', u, -.03, 2.2, 2.2, .06, 3.2)
        m.box('frame', u, -.015, 2.2, 2.5, .03, 3.5)
    m.flush('west neighbour front')
    f = C.Face((31.5, 0, 0), (0, -1, 0), (1, 0, 0), 'east warehouses front')
    m = Merge(f)
    for y0, y1, h in ((-27.0, -12.0, 17.5), (-12.0, 2.0, 20.5), (2.0, 16.0, 15.8), (16.0, 30.0, 19.0)):
        windows_grid(m, -y1 + .6, -y0 - .6, 4.6, h - 1.2, int((h - 5.8) / 3.3), 2.4, w=1.1, hh=2.0)
    for k in range(10):
        u = -28.0 + 5.6 * k
        m.box('glass', u, -.03, 2.0, 3.6, .06, 3.0)
        m.box('sign', u, -.05, 3.9, 4.6, .1, .5)
    m.flush('east warehouses front')
    f = C.Face((-15.6, 0, 0), (0, 1, 0), (-1, 0, 0), 'north-west block lane face')
    m = Merge(f)
    windows_grid(m, -1.0, 15.0, .6, 10.0, 3, 2.6, w=1.0, hh=1.9)
    m.flush('north-west block lane face')


def site():
    SW, CURB = -15.5, 16.8                    # south curb line (y) and east curb line (x)
    for name, x0, x1, y0, y1, role, top in (
            ('South sidewalk', -40.0, CURB, SW, Y0, 'paver', .14), ('East sidewalk', X1, CURB, Y0, 30.0, 'paver', .14),
            ('South street', -40.0, CURB, -27.0, SW, 'cobble', .06), ('Corner crossing', CURB, 28.0, -27.0, SW, 'cobble', .06),
            ('East street', CURB, 28.0, SW, 30.0, 'asphalt', .04), ('Far east sidewalk', 28.0, 31.5, -27.0, 30.0, 'paver', .14),
            ('Far south sidewalk', -40.0, 31.5, -31.0, -27.0, 'paver', .14), ('West lane', -15.6, X0, -1.8, 30.0, 'cobble', .06),
            ('North sidewalk strip', X0, X1, Y1, 30.0, 'paver', .1)):
        C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, top / 2), (x1 - x0, y1 - y0, top), role, 'site', 0)
    b = Batch()
    b.box('concrete', (-40.0 + CURB) / 2, SW + .1, .075, CURB + 40.0, .2, .15)                    # curbs, a hair above the walks
    b.box('concrete', CURB - .1, (SW + .2 + 30.0) / 2, .076, .2, 30.0 - SW - .2, .152)
    b.box('concrete', 28.1, (-27.0 + 30.0) / 2, .075, .2, 57.0, .15)
    for k in range(1, 38):                                                                       # sett courses
        b.box('joint', (-40.0 + 28.0) / 2, -27.0 + k * (SW + 27.0) / 38, .061, 67.6, .025, .004)
    for k in range(-60, 70):
        b.box('joint', k * .5 + .25, (-27.0 + SW) / 2, .0605, .022, SW + 27.0 - .05, .004)
    for k in range(1, 9):                                                                        # brick paver joints
        b.box('joint', (-40.0 + CURB) / 2, SW + .2 + k * (Y0 - SW - .2) / 9, .1405, CURB + 40.0 - .3, .02, .003)
    for k in range(1, 9):
        b.box('joint', X1 + k * (CURB - .2 - X1) / 9, (Y0 + 30.0) / 2, .1405, .02, 30.0 - Y0 - .1, .003)
    for k in range(6):                                                                           # zebra crossing on the east street
        b.box('trim', CURB + .9 + k * 1.75, -16.6, .045, .9, 2.0, .01)
    for k in range(20):
        b.box('trim', 22.4, -12.0 + k * 2.2, .044, .12, 1.2, .008)                                  # centre line
    b.flush('paving')
    steam_clock()
    for x, y in ((-11.0, -15.0), (CURB - .6, -8.0), (CURB - .6, 6.5), (28.6, -2.0), (28.6, 14.0)):
        lamp(x, y)
    for x in (-17.0, -22.5):
        street_tree(x, -14.4, z=.14, height=7.5, spread=2.0)


def build():
    site()
    f, holes, kind = south_front()
    dress(f, holes, kind, 'south front')
    f, holes, kind = east_front()
    dress(f, holes, kind, 'east front')
    bands_and_piers()
    corner()
    plain_walls()
    pediment()
    roof()
    inside()
    context()
    C.CONTACTS.append(dict(name='Gastown corner commercial block with the steam clock', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(-45, -60, 55), fill=(60, -25, 30), rear=(15, 60, 45), target=(0, -2, 8.0), gain=3.0)
