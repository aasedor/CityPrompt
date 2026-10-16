"""Calgary Beltline brick mid-rise with street retail, authored from the locked catalogue views of
calgary_beltline_mid_rise / variant_0 (beltline_glass_panel).

Read from the pixels: a corner building with streets south and east. A ground storey of retail
projects 1.6 m in front of the upper south face, its storefronts between brick piers under dark sign
bands: a brewery taproom with a patio at the west, the residential lobby under a dark canopy in the
middle, a market wrapping the south-east corner. Above it three storeys of red brick in two wings
either side of a recessed full-height glazed slot over the lobby, the floor-2 flats opening onto the
retail roof behind a glass guard, projecting concrete balconies with glass balustrades on floors 3
and 4 (two stacks on the west wing, one wide stack on the east wing, two stacks on the east face),
a dark metal cap at the brick parapet. A dark-panelled penthouse storey is set back behind wood-decked
terraces with planters and a glass guard; its gravel roof carries paver walkways and a stair and
lift bulkhead with an L-shaped notch. A lower neighbour abuts the west side.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-beltline-brick-midrise'
X0, X1 = -15.0, 15.0              # upper south face 30 m (top view: 555 px at 0.054 m/px)
Y0, Y1 = -16.0, 16.0              # 32 m deep
PROJ = 1.6                        # retail storey projects in front of the upper south face
T = .30
G0 = .15
L2 = 5.0                          # floor 2 and retail roof
FH = 3.1
LEVELS = [L2, L2 + FH, L2 + 2 * FH]
ROOF = L2 + 3 * FH                # 14.3, brick roof
PARA = ROOF + 1.0                 # brick parapet with dark metal cap
PH = (X0 + 3.2, X1 - 3.0, Y0 + 4.3, Y1 - 2.2)   # penthouse set back behind terraces (top view)
PH_TOP = ROOF + 3.4
SLOT = (-1.2, 3.3)                # recessed glazed slot over the lobby (oblique)
SLOT_IN = 1.6
BAL_D = 1.7
EPS = .002
PALETTE = dict(wall=(.55, .26, .19), joint=(.40, .19, .15), trim=(.15, .16, .17),
    pale=(.78, .77, .74), stone=(.70, .68, .64), roof=(.62, .60, .56), sand=(.66, .63, .58),
    foundation=(.44, .44, .43), glass=(.48, .56, .60), hardware=(.18, .19, .20),
    interior=(.80, .76, .68), floor=(.46, .44, .42), timber=(.46, .31, .19), blue=(.14, .22, .28),
    planting=(.25, .42, .15), soil=(.20, .15, .09), concrete=(.70, .69, .66), metal=(.27, .28, .30),
    signband=(.17, .17, .18), bronze=(.31, .27, .23), gravel=(.70, .62, .54), canvas=(.86, .84, .78))


def manifest(version):
    h = PH_TOP + 3.0
    cams = G.camera_roster(X1 - X0 + 4.0, Y1 - Y0 + 4.0, h, [
        ('facade_close', (6.0, -36.0, 9.0), (6.0, Y0, 9.0), 45),
        ('architecture_close', (30.0, -30.0, 10.0), (X1, Y0, 8.0), 50),
        ('glass_close', (1.0, -27.0, 8.5), (1.0, Y0 + SLOT_IN, 9.0), 45),
        ('storefront_patio', (-6.0, -30.0, 2.0), (-9.0, Y0 - PROJ, 2.6), 45),
        ('lobby_slot', (1.0, -26.0, 2.0), (1.0, Y0 - PROJ, 3.2), 40),
        ('balcony_stack', (32.0, 2.0, 10.0), (X1, 6.0, 10.0), 45),
        ('penthouse_terrace', (-10.0, -30.0, 24.0), (-6.0, PH[2] - 1.5, ROOF + 1.5), 45),
        ('roof_bulkhead', (24.0, -26.0, 34.0), (0.0, 0.0, PH_TOP + 1.0), 45),
        ('interior', (-7.0, -3.0, LEVELS[1] + 1.6), (-9.0, Y0 - 1.0, LEVELS[1] + 1.2), 55),
        ('rear_lane', (-6.0, 34.0, 6.0), (0.0, Y1, 7.0), 40)])
    for c in cams:                       # the locked front and oblique look from the south-east street corner
        if c['name'] == 'front_corner':
            lx, ly, lz = c['location']; c['location'] = (-lx, ly, lz)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='calgary_beltline_mid_rise/variant_0 (beltline_glass_panel)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0 + PROJ, height=h),
            observed_storeys=5, storey_programme='retail ground storey, three brick residential storeys, set-back penthouse storey',
            plan='30 x 32 m upper floor plate on a corner (top view at 0.054 m/px); retail storey projects 1.6 m on the south; penthouse 23.8 x 25.5 m set back 3.0 to 4.3 m behind decked terraces',
            facade='two brick wings either side of a 4.5 m recessed glazed slot over the lobby; floor-2 flats onto the retail roof behind a glass guard; projecting balconies on floors 3 and 4 (two on the west wing, one wide on the east wing, two stacks on the east face, two on the north)',
            ground='storefronts between brick piers under dark sign bands: brewery taproom with patio (west), lobby under a dark canopy (middle), market wrapping the south-east corner',
            levels_m=[G0, L2] + LEVELS[1:] + [ROOF], parapet_m=PARA, penthouse_top_m=PH_TOP,
            inferred='storey height 3.1 m and interiors are teaching assumptions; the north face is not visible in any source and repeats the visible grammar; the west face is a party condition above a lower neighbour'),
        roof_contract=dict(type='flat: retail-roof terrace, decked penthouse terraces with planters and glass guard, gravel penthouse roof with paver walkways and a bulkhead', datum_m=ROOF, crowns_m=[PARA, PH_TOP]),
        identity_contract=dict(owner='red-brick wings either side of the glazed slot, projecting glass-balustraded balconies, retail storey with dark sign bands, set-back dark penthouse with terraces'),
        material_contract=dict(profile='source-palette clay: red brick with recessed courses, dark storefront frames and sign bands, clear glass, pale concrete balcony slabs with glass balustrades, dark metal parapet cap and penthouse panels, timber decks', textured_keeper=False),
        programme_contract=dict(storeys=5, ground='three retail units and the residential lobby', upper='flats around a central corridor', penthouse='four penthouse flats on terraces', roof='stair and lift bulkhead'),
        contact_contract=['Grade-zero slab and sidewalks', 'Retail storey bearing the floor-2 terrace', 'Balcony slabs cast with the floor slabs', 'Penthouse on the brick roof slab inside the terraces', 'Bulkhead on the penthouse roof'],
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


# ---- Beltline mid-rise ----

def faces(y_south):
    south = C.Face(((X0 + X1) / 2, y_south, 0), (1, 0, 0), (0, 1, 0), 'south')
    east = C.Face((X1, (Y0 + Y1) / 2, 0), (0, 1, 0), (-1, 0, 0), 'east')
    north = C.Face(((X0 + X1) / 2, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')
    west = C.Face((X0, (Y0 + Y1) / 2, 0), (0, -1, 0), (1, 0, 0), 'west')
    return south, east, north, west


def balcony(m, u, z, w):
    """Projecting concrete balcony with a glass balustrade on three sides and a dark top rail."""
    m.box('concrete', u, -BAL_D / 2, z - .07, w, BAL_D, .26)
    m.box('glass', u, -BAL_D + .06, z + .06 + .52, w - .10, .02, 1.0)
    for e in (-1, 1):
        m.box('glass', u + e * (w / 2 - .05), -BAL_D / 2, z + .06 + .52, .02, BAL_D - .14, 1.0)
    m.box('hardware', u, -BAL_D + .06, z + 1.10, w - .04, .05, .05)
    for e in (-1, 1):
        m.box('hardware', u + e * (w / 2 - .05), -BAL_D / 2, z + 1.10, .05, BAL_D - .10, .05)


def pair(tag, c, w, z):
    """Glazed door and window side by side behind a balcony (front and oblique views)."""
    return [hole(f'{tag} door', c + w * .22, z + .05, min(1.5, w * .3), 2.45, kind='door'),
            hole(f'{tag} window', c - w * .18, z + .45, min(2.4, w * .45), 2.05)]


def storefront_face(f, lo, hi, units, top, piers=()):
    """Retail storey carrier: storefronts between brick piers under dark sign bands."""
    holes = []
    for k, (u, w, kind) in enumerate(units):
        if kind == 'door':
            holes.append(hole(f'{f.label} service door {k}', u, G0, w, 2.6, kind='door'))
        elif kind == 'garage':
            holes.append(hole(f'{f.label} garage door {k}', u, G0, w, 3.4, kind='garage'))
        elif kind == 'window':
            holes.append(hole(f'{f.label} rear window {k}', u, 1.4, w, 1.6))
        else:
            holes.append(hole(f'{f.label} storefront {k}', u, G0, w, 3.75 - G0, kind=kind))
    f.wall(f'{f.label} retail carrier', lo, hi - EPS, G0, top, depth=T, holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, G0 + .02, top - .02, holes, spacing=.15)
    m = Merge(f)
    for h in holes:
        if h.get('kind') in ('door', 'garage'):
            m.box('metal', h['u'], .20, h['z'] + h['h'] / 2, h['w'] - .04, .05, h['h'] - .02)
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='service door', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=.18, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='service'))
        elif h.get('kind') == 'window':
            framed(m, f, h, cols=2, inset=.12, occupied='back of house')
        else:
            cols = max(2, round(h['w'] / 1.6))
            framed(m, f, h, cols=cols, rows=2, inset=.14, occupied='retail unit', kind='storefront')
            m.box('trim', h['u'], .04, h['z'] + .25, h['w'] - .1, .10, .40)              # dark kick plate
        if h.get('kind') in ('storefront', 'lobby'):
            m.box('signband', h['u'], -.08, 4.32, h['w'] + .5, .16, .78)                 # dark sign band over each unit
            for k in range(3):
                m.box('pale', h['u'] - h['w'] * .25 + k * h['w'] * .25, -.18, 4.32, min(2.4, h['w'] * .18), .04, .22)   # sign lettering bar (no text in clay)
            for e in (-1, 1):
                C.rod('Gooseneck lamp', f.p(h['u'] + e * (h['w'] / 2 + .2), -.02, 3.95), f.p(h['u'] + e * (h['w'] / 2 + .2), -.30, 3.95), .03, 'hardware', 'retail lamps', 6)
    m.box('stone', (lo + hi) / 2, -.06, G0 + .2, hi - lo, T + .12, .40)                   # concrete base course
    m.flush('retail storey')
    return holes


def retail_storey():
    south, east, north, west = faces(Y0 - PROJ)
    hw = (X1 - X0) / 2
    storefront_face(south, -hw, hw, [(-11.3, 5.6, 'storefront'), (-5.0, 5.4, 'storefront'), (1.05, 3.9, 'lobby'),
                                     (6.4, 4.8, 'storefront'), (11.9, 4.8, 'storefront')], L2 + .4)
    # Lobby: recessed glazed doors under a dark canopy and the building's sign band.
    sx = (SLOT[0] + SLOT[1]) / 2
    C.box('Lobby canopy', (sx, Y0 - PROJ - .7, 3.72), (SLOT[1] - SLOT[0] + 1.2, 1.6, .16), 'signband', 'lobby', 0)
    C.box('Lobby canopy soffit light', (sx, Y0 - PROJ - .7, 3.63), (SLOT[1] - SLOT[0], .2, .02), 'pale', 'lobby', 0)
    # East face from the projection to the rear: the market wraps the corner, then shops, then a lane-side garage door.
    ue0 = Y0 - PROJ + T
    east_ground = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    storefront_face(east_ground, ue0, Y1, [(-13.0, 3.6, 'storefront'), (-7.4, 4.6, 'storefront'), (-1.6, 4.6, 'storefront'),
                                           (5.0, 1.2, 'door'), (10.4, 4.0, 'garage')], L2)
    # North (lane) face: loading door, service door, small windows.
    north_ground = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')
    storefront_face(north_ground, -hw + T, hw - T, [(-10.0, 3.8, 'garage'), (-4.0, 1.1, 'door'), (2.0, 2.4, 'window'), (8.0, 2.4, 'window')], L2)
    # West party wall at grade (a lower neighbour abuts it).
    west_ground = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west')
    west_ground.wall('west party wall', -(Y1 - T), -(ue0), G0, L2, depth=T)
    G.brick_courses(west_ground, -(Y1 - T) + .02, -ue0 - .02, G0 + .02, L2 - .02, [], spacing=.15)
    # Parapet returns closing the floor-2 terrace on the retail roof, east and west.
    for x in (X1 - T / 2, X0 + T / 2):
        C.box('Terrace parapet return', (x, Y0 - PROJ / 2 + T / 2, (L2 + L2 + .4) / 2), (T, PROJ - T, .4), 'wall', 'retail storey', 0)
    C.box('Retail roof coping', (0, Y0 - PROJ + T / 2, L2 + .43), (X1 - X0 + .1, T + .1, .06), 'stone', 'retail storey', 0)
    # Slabs, pavers, glass guard on the retail roof (the floor-2 terrace).
    C.box('Ground slab', (0, (Y0 - PROJ + Y1) / 2, G0 / 2), (X1 - X0, Y1 - Y0 + PROJ, G0), 'foundation', 'foundation', 0)
    C.box('Floor 2 slab', (0, (Y0 - PROJ + T + Y1 - T) / 2, L2 - .14), (X1 - X0 - 2 * T, Y1 - Y0 + PROJ - 2 * T, .28), 'floor', 'occupied floors', 0)
    C.box('Floor 2 terrace pavers', (0, Y0 - PROJ / 2 + T / 2, L2 + .006), (X1 - X0 - 2 * T - .02, PROJ - T - .02, .012), 'pale', 'terrace', 0)
    gy = Y0 - PROJ + T / 2
    C.box('Floor 2 terrace glass guard', (0, gy, L2 + .4 + .36), (X1 - X0 - .1, .02, .62), 'glass', 'terrace', 0)
    C.box('Floor 2 terrace guard rail', (0, gy, L2 + 1.10), (X1 - X0 - .06, .05, .05), 'hardware', 'terrace', 0)
    for x in (SLOT[0] - .1, SLOT[1] + .1, -8.0, 9.0):          # privacy screens between the terrace flats
        C.box('Terrace privacy screen', (x, Y0 - PROJ / 2 + T / 2, L2 + .9), (.08, PROJ - T - .04, 1.8), 'metal', 'terrace', 0)
    for x in (-13.0, -6.6, 6.0, 12.4):
        C.box('Terrace planter', (x, Y0 - .55, L2 + .3), (1.6, .5, .6), 'concrete', 'terrace', 0)
        A.shrub(x, Y0 - .55, L2 + .6, .6)
    # Retail interiors: lights, brewery tables and market shelving behind the storefronts.
    for x, power in ((-11.0, 120), (-5.0, 120), (1.0, 80), (6.4, 120), (11.6, 120)):
        C.qa_room_light(f'Retail {x:+.0f}', (x, Y0 - PROJ + 3.0, L2 - .6), power, 4.0)
    for x in (-12.6, -10.0, -6.2, -3.8):
        C.box('Taproom table', (x, Y0 - PROJ + 2.4, G0 + .74), (1.2, .8, .05), 'timber', 'taproom', 0)
        C.box('Taproom table base', (x, Y0 - PROJ + 2.4, G0 + .37), (.12, .12, .72), 'hardware', 'taproom', 0)
    C.box('Taproom bar', (-8.0, Y0 - PROJ + 7.0, G0 + .55), (7.0, .8, 1.1), 'timber', 'taproom', 0)
    for x in (5.0, 7.6, 10.4, 13.0):
        C.box('Market shelving', (x, Y0 - PROJ + 4.0, G0 + .9), (.6, 3.0, 1.8), 'pale', 'market', 0)
    C.box('Lobby mailbox wall', (sx, Y0 - PROJ + 5.0, G0 + 1.2), (3.0, .3, 2.2), 'metal', 'lobby', 0)
    C.CONTACTS.append(dict(name='Retail storey projecting 1.6 m on the south bears the floor-2 terrace with glass guard and privacy screens', roof_m=L2))


def wing(f, lo, hi, plan, stacks, label):
    """One brick wing: floor-2 door pairs onto the terrace, floors 3 and 4 door pairs behind projecting balconies."""
    holes = []
    for fi, z in enumerate(LEVELS):
        for k, (u, w) in enumerate(plan):
            holes.append(hole(f'{f.label} {label} f{fi + 2} window {k}', u, z + .45, w, 2.05))
        for k, (u, w) in enumerate(stacks):
            holes += pair(f'{f.label} {label} f{fi + 2} bay {k}', u, w, z)
    f.wall(f'{f.label} {label} brick carrier', lo, hi - EPS, L2, PARA, depth=T, holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, L2 + .02, PARA - .3, holes, spacing=.15)
    m = Merge(f)
    for h in holes:
        if h.get('kind') == 'door':
            framed(m, f, h, cols=1, rows=1, inset=.18, occupied='flat living room', kind='glazed door')
        else:
            framed(m, f, h, cols=2, rows=1, inset=.18, occupied='flat')
            m.box('stone', h['u'], -.04, h['z'] - .05, h['w'] + .12, .14, .10)
    return holes, m


def cap(m, lo, hi, ext=(0.0, 0.0), dz=0.0):
    a, c = lo - ext[0], hi + ext[1]
    m.box('metal', (a + c) / 2, -.12, PARA + .06 + dz, c - a - 2 * EPS, T + .36, .14)
    m.box('metal', (a + c) / 2, -.20, PARA - .18 + dz, c - a - 2 * EPS, .14, .34)


def brick_upper():
    south, east, north, west = faces(Y0)
    hw, hd = (X1 - X0) / 2, (Y1 - Y0) / 2
    # South west wing: two stacks; floor 2 onto the terrace, floors 3 and 4 behind projecting balconies.
    for lo, hi, plan, stacks, label in ((-hw, SLOT[0], [], [(-11.7, 5.6), (-5.3, 6.0)], 'west wing'),
                                        (SLOT[1], hw, [(5.0, 1.5), (14.1, 1.2)], [(10.0, 6.6)], 'east wing')):
        holes, m = wing(south, lo, hi, plan, stacks, label)
        for u, w in stacks:
            for z in LEVELS[1:]:
                balcony(m, u, z, w)
        cap(m, lo, hi)
        m.flush(label)
    # Slot returns and the recessed glazed slot.
    for x in (SLOT[0] - T / 2, SLOT[1] + T / 2):
        C.box('Slot brick return', (x, Y0 + T + SLOT_IN / 2, (L2 + PARA) / 2), (T, SLOT_IN, PARA - L2), 'wall', 'slot', 0)
        C.box('Slot return cap', (x, Y0 + T + SLOT_IN / 2, PARA + .06), (T + .3, SLOT_IN, .14), 'metal', 'slot', 0)
    slot = C.Face(((SLOT[0] + SLOT[1]) / 2, Y0 + SLOT_IN + T, 0), (1, 0, 0), (0, 1, 0), 'slot')
    sw = SLOT[1] - SLOT[0]
    bands = [hole(f'slot glazing f{i + 2}', 0, z + .55, sw - .3, FH - .6, kind='band') for i, z in enumerate(LEVELS)]
    bands.append(hole('slot glazing parapet', 0, ROOF + .3, sw - .3, PARA - ROOF - .35, kind='band'))
    slot.wall('Slot spandrel carrier', -sw / 2, sw / 2 - EPS, L2, PARA, depth=T, role='metal', holes=bands)
    m = Merge(slot)
    for h in bands:
        m.box('glass', h['u'], .12, h['z'] + h['h'] / 2, h['w'] - .02, .012, h['h'] - .02)
        register(slot, h, .10, 'curtain wall', 'stair and corridor')
    n = 3
    for i in range(n + 1):
        m.box('trim', -sw / 2 + .15 + (sw - .3) * i / n, -.03, (L2 + PARA) / 2, .08, .10, PARA - L2 - .04)
    for z in LEVELS + [ROOF]:
        m.box('trim', 0, -.04, z + .28, sw - .2, .08, .06)
    m.flush('slot curtain wall')
    for i, z in enumerate(LEVELS):                             # stair flights seen through the slot
        C.box('Slot corridor back wall', ((SLOT[0] + SLOT[1]) / 2, Y0 + SLOT_IN + T + 3.2, z + FH / 2), (SLOT[1] - SLOT[0] + 1.0, .2, FH - .3), 'interior', 'corridor', 0)
        C.qa_room_light(f'Slot stair {i}', ((SLOT[0] + SLOT[1]) / 2, Y0 + SLOT_IN + T + 1.5, z + FH - .4), 50, 2.0)
    # East face: two balcony stacks on all three floors and a window rhythm.
    holes, m = wing(east, -hd + T, hd, [(-12.6, 1.6), (-8.6, 1.6), (-4.6, 1.6), (6.0, 1.6), (14.0, 1.2)], [(1.6, 4.6), (10.4, 4.6)], 'east')
    for u, w in ((1.6, 4.6), (10.4, 4.6)):
        for z in LEVELS:
            balcony(m, u, z, w)
    cap(m, -hd + T, hd, ext=(.5, .5), dz=.012)
    m.flush('east')
    # North face (not in any source): window rhythm and two stacks, after the visible grammar.
    holes, m = wing(north, -hw + T, hw - T, [(-12.0, 1.6), (-2.0, 1.6), (2.0, 1.6), (12.0, 1.6)], [(-7.0, 4.6), (7.0, 4.6)], 'north')
    for u, w in ((-7.0, 4.6), (7.0, 4.6)):
        for z in LEVELS:
            balcony(m, u, z, w)
    cap(m, -hw + T, hw - T)
    m.flush('north')
    # West face above the lower neighbour: windows on floors 3 and 4 only.
    holes = [hole(f'west f{fi + 3} window {k}', u, z + .45, 1.6, 2.05) for fi, z in enumerate(LEVELS[1:]) for k, u in enumerate((-11.0, -3.0, 5.0, 12.0))]
    west.wall('west brick carrier', -hd, hd - T - EPS, L2, PARA, depth=T, holes=holes)
    G.brick_courses(west, -hd + .02, hd - T - .02, L2 + .02, PARA - .3, holes, spacing=.15)
    m = Merge(west)
    for h in holes:
        framed(m, west, h, cols=2, inset=.12, occupied='flat')
        m.box('stone', h['u'], -.04, h['z'] - .05, h['w'] + .12, .14, .10)
    cap(m, -hd, hd - T, ext=(.5, .5), dz=.012)
    m.flush('west')
    # Floor slabs avoid the open slot; a corridor core; flat interiors behind the south windows.
    sx0, sx1 = SLOT[0] - T, SLOT[1] + T
    yb = Y0 + SLOT_IN + T
    for i, z in enumerate(LEVELS[1:] + [ROOF]):
        C.box(f'Floor slab {i + 3}', (0, (yb + Y1 - T) / 2, z - .14), (X1 - X0 - 2 * T, Y1 - T - yb, .28), 'floor', 'occupied floors', 0)
        for a, b in ((X0 + T, sx0), (sx1, X1 - T)):
            C.box(f'Floor slab {i + 3} wing', ((a + b) / 2, (Y0 + T + yb) / 2, z - .14), (b - a, yb - Y0 - T, .28), 'floor', 'occupied floors', 0)
    C.box('Corridor core', (1.0, 4.0, (L2 + ROOF) / 2), (6.0, 4.0, ROOF - L2), 'concrete', 'core', 0)
    for z in LEVELS:
        for x in (-10.0, -4.0, 8.0, 12.0):
            C.qa_room_light(f'Flat {x:+.0f} {z:.1f}', (x, Y0 + 3.0, z + FH - .5), 45, 3.0)
        C.qa_room_light(f'East flats {z:.1f}', (X1 - 3.0, 6.0, z + FH - .5), 45, 3.0)
    zf = LEVELS[1]
    C.box('Party wall', (-8.5, Y0 + T + 2.8, zf + FH / 2), (.16, 5.6, FH - .3), 'interior', 'partitions', 0)
    A.sofa(-11.5, Y0 + 2.6, zf); A.desk(-5.0, Y0 + 2.4, zf); A.bed(-12.5, Y0 + 6.0, zf)
    C.CONTACTS.append(dict(name='Brick wings on the floor-2 slab, balcony slabs cast with the floor slabs, slot glazing between the brick returns', roof_m=ROOF))


def penthouse_and_roof():
    px0, px1, py0, py1 = PH
    # Decked terraces round the penthouse, the slot roof as a paved walkway, planters and a glass guard on the parapet.
    C.box('Roof slab', (0, 0, ROOF - .14), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .28), 'floor', 'roof', 0)
    zd = ROOF + .02
    for name, (a, b, c, d) in (('south', (X0 + T, SLOT[0] - T, Y0 + T, py0)), ('south east', (SLOT[1] + T, X1 - T, Y0 + T, py0)),
                               ('north', (X0 + T, X1 - T, py1, Y1 - T)), ('west', (X0 + T, px0, py0, py1)), ('east', (px1, X1 - T, py0, py1))):
        C.box(f'Terrace deck {name}', ((a + b) / 2, (c + d) / 2, zd + .05), (b - a - .02, d - c - .02, .10), 'timber', 'terraces', 0)
    C.box('Slot roof walkway', ((SLOT[0] + SLOT[1]) / 2, (Y0 + py0) / 2 + T / 2, zd + .04), (SLOT[1] - SLOT[0] + 2 * T - .04, py0 - Y0 - T - .02, .08), 'pale', 'terraces', 0)
    for x in (X0 + 1.0, X1 - 1.0):
        for y in (-10.0, -4.0, 2.0, 8.0, 13.0):
            C.box('Terrace planter', (x, y, ROOF + .45), (.7, 1.8, .7), 'concrete', 'terraces', 0)
            A.shrub(x, y, ROOF + .8, .7)
    for x in (-12.0, -7.0, 6.0, 11.0):
        C.box('Terrace planter', (x, Y0 + 1.0, ROOF + .45), (1.8, .7, .7), 'concrete', 'terraces', 0)
        A.shrub(x, Y0 + 1.0, ROOF + .8, .7)
    for x, y in ((-11.0, Y0 + 2.6), (9.0, Y0 + 2.6)):
        C.rod('Terrace umbrella pole', (x, y, zd + .1), (x, y, zd + 2.4), .03, 'hardware', 'terraces', 6)
        umbrella(x, y, zd + 2.2, 1.3)
        C.box('Terrace table', (x + .4, y, zd + .8), (1.0, 1.0, .05), 'timber', 'terraces', 0)
    for (a, b), (c, d) in ((((X0 + .15, Y0 + .15)), ((X1 - .15, Y0 + .15))), (((X1 - .15, Y0 + .15)), ((X1 - .15, Y1 - .15))),
                          (((X1 - .15, Y1 - .15)), ((X0 + .15, Y1 - .15))), (((X0 + .15, Y1 - .15)), ((X0 + .15, Y0 + .15)))):
        C.beam('Terrace glass guard', (a, b, PARA + .38), (c, d, PARA + .38), .02, .5, 'glass', 'terraces')
        C.beam('Terrace guard rail', (a, b, PARA + .66), (c, d, PARA + .66), .05, .05, 'hardware', 'terraces')
    # Penthouse: dark metal panels with tall glazing, a pale overhanging roof edge.
    ph_s = C.Face(((px0 + px1) / 2, py0, 0), (1, 0, 0), (0, 1, 0), 'penthouse south')
    ph_e = C.Face((px1, (py0 + py1) / 2, 0), (0, 1, 0), (-1, 0, 0), 'penthouse east')
    ph_n = C.Face(((px0 + px1) / 2, py1, 0), (-1, 0, 0), (0, -1, 0), 'penthouse north')
    ph_w = C.Face((px0, (py0 + py1) / 2, 0), (0, -1, 0), (1, 0, 0), 'penthouse west')
    w, d = px1 - px0, py1 - py0
    for f, lo, hi, units in ((ph_s, -w / 2, w / 2, (-8.5, -4.5, 3.5, 7.5)), (ph_n, -w / 2, w / 2, (-7.0, -1.0, 5.0)),
                             (ph_e, -d / 2 + T, d / 2 - T, (-8.0, -2.0, 4.0, 9.0)), (ph_w, -d / 2 + T, d / 2 - T, (-8.0, -2.0, 4.0, 9.0))):
        holes = [hole(f'{f.label} glazing {k}', u, ROOF + .2, 3.0, 2.6, kind='door') for k, u in enumerate(units)]
        f.wall(f'{f.label} panel carrier', lo, hi - EPS, ROOF, PH_TOP, depth=.26, role='bronze', holes=holes)
        m = Merge(f)
        for h in holes:
            framed(m, f, h, cols=3, inset=.10, occupied='penthouse flat', kind='glazed door')
        for k in range(int((hi - lo) / 1.2) + 1):
            u = lo + .3 + k * 1.2
            if all(abs(u - h['u']) > h['w'] / 2 + .1 for h in holes) and u < hi - .2:
                m.box('hardware', u, -.02, (ROOF + PH_TOP) / 2, .04, .04, PH_TOP - ROOF - .1)   # panel joints
        m.flush('penthouse')
    C.box('Penthouse roof slab', ((px0 + px1) / 2, (py0 + py1) / 2, PH_TOP - .12), (w - .52, d - .52, .24), 'floor', 'penthouse', 0)
    C.box('Penthouse fascia', ((px0 + px1) / 2, py0 - .25, PH_TOP - .05), (w + 1.0, .5, .6), 'stone', 'penthouse', 0)
    C.box('Penthouse fascia', ((px0 + px1) / 2, py1 + .25, PH_TOP - .05), (w + 1.0, .5, .6), 'stone', 'penthouse', 0)
    C.box('Penthouse fascia', (px0 - .25, (py0 + py1) / 2, PH_TOP - .05), (.5, d, .6), 'stone', 'penthouse', 0)
    C.box('Penthouse fascia', (px1 + .25, (py0 + py1) / 2, PH_TOP - .05), (.5, d, .6), 'stone', 'penthouse', 0)
    C.box('Penthouse gravel', ((px0 + px1) / 2, (py0 + py1) / 2, PH_TOP + .02), (w - .1, d - .1, .04), 'gravel', 'penthouse roof', 0)
    # Paver walkways: a ring round the bulkhead and spokes to the edge (top view).
    bx0, bx1, by0, by1 = -2.0, 4.8, -4.2, 6.3
    zp = PH_TOP + .045
    for a, b, c, d2 in ((bx0 - 2.4, bx1 + 2.4, by0 - 2.4, by0 - 1.2), (bx0 - 2.4, bx1 + 2.4, by1 + 1.2, by1 + 2.4),
                        (bx0 - 2.4, bx0 - 1.2, by0 - 1.2, by1 + 1.2), (bx1 + 1.2, bx1 + 2.4, by0 - 1.2, by1 + 1.2),
                        (px0 + .3, bx0 - 2.4, 0.8, 2.0), (bx1 + 2.4, px1 - .3, 0.8, 2.0), (0.6, 1.8, py0 + .3, by0 - 2.4), (0.6, 1.8, by1 + 2.4, py1 - .3)):
        C.box('Roof paver walkway', ((a + b) / 2, (c + d2) / 2, zp), (b - a, d2 - c, .03), 'pale', 'penthouse roof', 0)
    ny0, ny1 = by1 - 4.8, by1 - 2.4                    # L-shaped notch in the east side (top view)
    outline = [(bx0, by0), (bx1, by0), (bx1, ny0), (bx1 - 1.8, ny0), (bx1 - 1.8, ny1), (bx1, ny1), (bx1, by1), (bx0, by1)]
    C.prism('Stair and lift bulkhead', outline, 'z', PH_TOP + .03, PH_TOP + 2.9, 'bronze', 'bulkhead')
    C.prism('Bulkhead roof', outline, 'z', PH_TOP + 2.9, PH_TOP + 3.0, 'pale', 'bulkhead')
    C.box('Bulkhead notch railing', (bx1 - .9, ny0 + .02, PH_TOP + .6), (1.8, .04, 1.1), 'hardware', 'bulkhead', 0)
    C.box('Bulkhead door', (bx0 + 1.6, by0 - .02, PH_TOP + 1.1), (1.0, .06, 2.1), 'hardware', 'bulkhead', 0)
    for x, y in ((-6.0, 5.0), (3.0, -9.0), (-7.0, -6.0)):
        C.box('Rooftop unit', (x, y, PH_TOP + .5), (1.4, 1.0, .9), 'pale', 'rooftop plant', 0)
    for x in (-8.0, -1.0, 7.0):
        C.qa_room_light(f'Penthouse {x:+.0f}', (x, py0 + 3.0, PH_TOP - .5), 50, 3.0)
    C.CONTACTS.append(dict(name='Penthouse on the brick roof slab inside decked terraces; bulkhead on the penthouse roof', penthouse_m=[ROOF, PH_TOP]))


def umbrella(x, y, z, r):
    """Round market umbrella: a low octagonal cone."""
    lower = [(x + r * math.cos(math.tau * k / 8), y + r * math.sin(math.tau * k / 8)) for k in range(8)]
    upper = [(x + .08 * math.cos(math.tau * k / 8), y + .08 * math.sin(math.tau * k / 8)) for k in range(8)]
    strip('Market umbrella', lower, upper, z, z + .45, 'canvas', 'umbrellas')


def site():
    ys = Y0 - PROJ
    C.box('South sidewalk', (2.0, ys - 3.0, .0075), (X1 - X0 + 14.0, 6.0, .015), 'sand', 'sidewalk', 0)
    C.box('East sidewalk', (X1 + 3.0, (ys + Y1) / 2, .0075), (6.0, Y1 - ys, .015), 'sand', 'sidewalk', 0)
    C.box('Kerb south', (2.0, ys - 6.0 + .06, .06), (X1 - X0 + 14.0, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb east', (X1 + 6.0 - .06, (ys + Y1) / 2, .06), (.12, Y1 - ys, .12), 'stone', 'sidewalk', 0)
    C.box('Rear lane', (0, Y1 + 3.0, .0075), (X1 - X0 + 12.0, 6.0, .015), 'foundation', 'lane', 0)
    C.box('West neighbour lot', (X0 - 3.0, (ys + Y1) / 2, .0075), (6.0, Y1 - ys, .015), 'foundation', 'lane', 0)
    # Taproom patio on the sidewalk: low black fence, tables and market umbrellas.
    py = ys - 1.6
    C.beam('Patio fence rail', (X0 + .4, py - 1.4, .9), (-2.4, py - 1.4, .9), .05, .05, 'hardware', 'patio')
    C.beam('Patio fence rail', (X0 + .4, py - 1.4, .3), (-2.4, py - 1.4, .3), .04, .04, 'hardware', 'patio')
    for k in range(24):
        x = X0 + .4 + (-2.4 - X0 - .4) * k / 23
        C.rod('Patio fence picket', (x, py - 1.4, .015), (x, py - 1.4, .92), .02, 'hardware', 'patio', 6)
    for x in (X0 + .4, -2.4):
        C.beam('Patio fence end', (x, py - 1.4, .9), (x, ys - .05, .9), .05, .05, 'hardware', 'patio')
    for x in (-12.4, -8.4, -4.4):
        C.rod('Patio umbrella pole', (x, py - .2, .015), (x, py - .2, 2.5), .03, 'hardware', 'patio', 6)
        umbrella(x, py - .2, 2.3, 1.25)
        C.box('Patio table', (x, py - .2, .74), (.9, .9, .05), 'timber', 'patio', 0)
        C.box('Patio table base', (x, py - .2, .38), (.1, .1, .72), 'hardware', 'patio', 0)
    for x in (-1.8, 4.0):
        C.box('Entrance planter', (x, ys - .5, .35), (.8, .8, .7), 'metal', 'sidewalk', 0)
        A.shrub(x, ys - .5, .7, .7)
    for x in (-17.0, 8.6, 19.0):
        street_tree(x, ys - 4.6, height=7.5, spread=1.6)
    for y in (-6.0, 8.0):
        street_tree(X1 + 4.4, y, height=7.5, spread=1.6)
    for k in range(4):
        C.rod('Bike rack hoop', (X1 + 2.0, -12.0 + k * .8, .015), (X1 + 2.0, -12.0 + k * .8, .85), .025, 'hardware', 'sidewalk', 6)


def build():
    site()
    retail_storey()
    brick_upper()
    penthouse_and_roof()
    C.CONTACTS.append(dict(name='Upper south face set 1.6 m behind the retail storey; west party condition above grade', plan_m=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(-40, -56, 48), fill=(50, -26, 42), rear=(-20, 56, 46), target=(0, -2, 8.0), gain=9.0)
