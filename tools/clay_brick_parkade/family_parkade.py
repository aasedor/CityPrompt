"""Campus parking structure with a brick frame and bronze stair towers, authored from the locked
catalogue views of campus_parking_structure / variant_0 (urban_infill_brick_concrete_tower).

Read from the pixels: a 54 x 40 m corner block with streets south and east. A red-brick frame of piers
and a parapet holds four open parking decks above a ground storey of glazed retail bays; each deck
opening sits over a pale precast spandrel and carries dark horizontal guard screens. At the south-east
street corner a square stair tower in a dark bronze frame rises above the parapet: its faces are
divided into strips of precast panel, glass and vertical louvres, with a bronze band at the first
deck and a louvred crown with a patinated coping. A larger tower of the same kind stands at the
north-east corner, a narrow glazed stair tower at the west end of the south face. The roof is an open
parking deck with stripes and light poles round a dark ribbed lift overrun, rooftop units and an open
stair well.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-brick-parkade'
X0, X1, Y0, Y1 = -27.0, 27.0, -20.0, 20.0        # main block (top view at 0.0755 m/px)
T = .40
G0 = .15
DECKS = [4.5, 7.7, 10.9, 14.1]                    # parking decks above the retail storey
ROOF = 17.3
PARA = ROOF + 1.1
SE = (18.0, 28.0, -21.4, -13.4)                   # bronze stair tower at the street corner
NE = (16.8, 29.2, 11.5, 22.4)                     # larger tower at the north-east corner
SWT = (-27.0, -22.5, -21.0, -16.0)                # narrow glazed stair tower
CROWN = 22.4
EPS = .002
PALETTE = dict(wall=(.52, .26, .19), joint=(.38, .19, .14), trim=(.16, .17, .18),
    pale=(.80, .79, .76), stone=(.70, .68, .64), roof=(.66, .65, .62), sand=(.68, .66, .62),
    foundation=(.42, .42, .41), glass=(.46, .56, .60), hardware=(.18, .18, .19),
    interior=(.78, .76, .72), floor=(.60, .59, .56), timber=(.40, .28, .16), blue=(.20, .28, .40),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.74, .72, .68), bronze=(.15, .12, .09),
    patina=(.36, .56, .50), asphalt=(.30, .30, .31), white=(.90, .90, .88), metal=(.26, .27, .29),
    car_red=(.50, .14, .12), car_grey=(.56, .58, .60), car_dark=(.18, .19, .21), car_white=(.84, .84, .82))


def manifest(version):
    h = CROWN + .6
    cams = G.camera_roster(X1 - X0 + 4.0, Y1 - Y0 + 4.0, h, [
        ('facade_close', (-6.0, -42.0, 9.0), (-6.0, Y0, 9.0), 45),
        ('architecture_close', (40.0, -36.0, 12.0), (SE[1], SE[2], 11.0), 45),
        ('glass_close', (26.0, -30.0, 8.0), (23.0, SE[2], 9.0), 45),
        ('tower_crown', (36.0, -34.0, 26.0), (23.0, -17.4, 20.4), 40),
        ('retail_base', (-8.0, -30.0, 2.0), (-8.0, Y0, 2.4), 45),
        ('vehicle_entry', (40.0, 0.0, 2.6), (X1, 0.0, 2.6), 45),
        ('roof_deck', (-30.0, -30.0, 30.0), (-2.0, 0.0, ROOF + 1.0), 45),
        ('stair_penthouse', (16.0, -12.0, 24.0), (4.0, 0.0, ROOF + 1.5), 45),
        ('interior', (-20.0, -14.0, DECKS[1] + 1.6), (6.0, -14.0, DECKS[1] + 1.0), 55),
        ('north_lane', (-4.0, 40.0, 6.0), (-4.0, Y1, 7.0), 40)])
    for c in cams:                       # the locked front and oblique look from the south-east street corner
        if c['name'] == 'front_corner':
            lx, ly, lz = c['location']; c['location'] = (-lx, ly, lz)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='campus_parking_structure/variant_0 (urban_infill_brick_concrete_tower)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0 + 2.2, depth=Y1 - Y0 + 3.8, height=h),
            observed_storeys=5, storey_programme='glazed retail ground storey, four open parking decks, roof parking deck',
            plan='54 x 40 m deck block (top view); 10 x 8 m bronze stair tower at the south-east corner projecting 1 m east and 1.4 m south; 12.4 x 11 m tower at the north-east corner; 4.5 x 5 m glazed stair tower at the west end of the south face; lift overrun, plant and open stair well on the roof',
            facade='brick piers on an 8 m bay, open deck openings over pale precast spandrels with dark horizontal guard screens, glazed retail bays at grade, brick parapet',
            towers='dark bronze frame dividing each face into strips of precast panel, glass and vertical louvres; bronze band at the first deck; louvred crown 4 m above the parapet with a patinated coping',
            levels_m=[G0] + DECKS + [ROOF], parapet_m=PARA, crown_m=CROWN,
            inferred='deck heights and interiors are teaching assumptions; the north and west faces are not visible in the front or oblique and repeat the visible grammar'),
        roof_contract=dict(type='open roof parking deck with parapet; flat tower roofs inside louvred crowns', datum_m=ROOF, crowns_m=[PARA, CROWN]),
        identity_contract=dict(owner='brick-framed open parking decks with precast spandrels and screens, bronze louvred corner stair tower above the parapet, glazed retail base, roof deck with lift overrun'),
        material_contract=dict(profile='source-palette clay: red brick, pale precast concrete, dark bronze frames and louvres, patinated coping, clear glass, grey concrete decks, simple car massing', textured_keeper=False),
        programme_contract=dict(storeys=5, ground='retail and a campus mobility hub with the vehicle entry and exit on the east street', decks='about 75 stalls per deck', roof='open parking, lift overrun, stair well'),
        contact_contract=['Grade-zero slab and sidewalks', 'Decks on the brick frame and internal columns', 'Towers founded at grade and rising through the parapet', 'Penthouse and light poles on the roof deck', 'Cars on the deck slabs'],
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


# ---- brick parking structure ----

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


LEVEL_TOPS = DECKS[1:] + [ROOF]


def deck_face(f, lo, hi, ground, lite=False, precast=True, bays=None, solid_first=False):
    """Brick frame elevation: piers on an 8 m bay, open deck openings over precast spandrels with guard screens."""
    span = hi - lo
    n = max(1, round(span / 8.2))
    pitch = span / n
    holes = []
    for i in range(n):
        u = lo + pitch * (i + .5)
        g = ground[i] if i < len(ground) else 'blank'
        if g == 'retail':
            holes.append(hole(f'{f.label} retail bay {i}', u, G0, pitch - 1.3, 3.75 - G0, kind='storefront'))
        elif g == 'entry':
            holes.append(hole(f'{f.label} vehicle opening {i}', u, G0, pitch - 2.0, 3.45 - G0, kind='vehicle'))
        elif g == 'window':
            holes.append(hole(f'{f.label} ground window {i}', u, 1.2, pitch - 1.6, 2.2))
        kind = (bays or {}).get(i)
        if kind == 'curtain':                                          # glazed curtain-wall bay over all decks
            holes.append(hole(f'{f.label} curtain bay {i}', u, DECKS[0] + .3, pitch - .9, ROOF - .4 - DECKS[0] - .3, kind='curtain'))
            continue
        for k, z in enumerate(DECKS):
            top = LEVEL_TOPS[k] - .40
            if kind == 'ribbon':
                holes.append(hole(f'{f.label} deck {k + 2} ribbon {i}', u, z + 1.2, pitch - .9, 1.2, kind='ribbon'))
            elif solid_first and k == 0:
                holes.append(hole(f'{f.label} deck 2 slot {i}', u, z + 1.2, pitch - .9, .9, kind='deck'))
            else:
                holes.append(hole(f'{f.label} deck {k + 2} opening {i}', u, z + 1.05, pitch - .9, top - z - 1.05, kind='deck'))
    f.wall(f'{f.label} brick frame', lo, hi - EPS, G0, PARA, depth=T, holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, G0 + .02, PARA - .25, holes, spacing=.2 if not lite else .32)
    m = Merge(f)
    for h in holes:
        if h.get('kind') == 'deck':
            for zr in (h['z'] + .55, h['z'] + 1.15):                         # dark horizontal guard screens
                m.box('metal', h['u'], .12, zr, h['w'] - .02, .06, .10)
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='open parking deck', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='parking deck'))
        elif h.get('kind') == 'vehicle':
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='vehicle entry', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='ramp'))
            m.box('bronze', h['u'], -.05, h['z'] + h['h'] + .2, h['w'] + .4, .2, .4)
        elif h.get('kind') == 'storefront':
            framed(m, f, h, cols=max(2, round(h['w'] / 1.6)), rows=2, inset=.16, occupied='retail unit', kind='storefront', frame='bronze', lite=lite)
        elif h.get('kind') == 'curtain':
            framed(m, f, h, cols=4, rows=len(DECKS) * 2, inset=.12, occupied='stair and lobby', kind='curtain wall', frame='bronze')
        elif h.get('kind') == 'ribbon':
            framed(m, f, h, cols=5, rows=1, inset=.14, occupied='parking office', kind='ribbon window', frame='bronze')
        else:
            framed(m, f, h, cols=3, rows=1, inset=.16, occupied='mobility hub office', frame='bronze', lite=lite)
    # Precast spandrels between the piers (deck slab edge and upstand), a brick parapet band, a stone base.
    for i in range(n):
        u = lo + pitch * (i + .5)
        for z in DECKS + [ROOF]:
            if (bays or {}).get(i) == 'curtain' and z != ROOF:
                continue
            if precast:
                m.box('concrete', u, -.05, z + .35, pitch - .9, .10, 1.4 if z != ROOF else .9)
            else:
                m.box('concrete', u, -.03, z - .22, pitch - .9, .06, .36)              # slab edge only; brick spandrel above
    m.box('stone', (lo + hi) / 2, -.05, G0 + .25, span - 2 * EPS, T + .10, .5)
    m.box('concrete', (lo + hi) / 2, -.06, PARA + .05, span - 2 * EPS, T + .14, .10)
    m.flush('frame')
    return holes


def frame_block():
    cx = lambda a, b: (a + b) / 2
    south = C.Face((cx(SWT[1], SE[0]), Y0, 0), (1, 0, 0), (0, 1, 0), 'south')
    w = (SE[0] - SWT[1]) / 2
    deck_face(south, -w, w, ['retail', 'retail', 'retail', 'retail', 'window'], precast=False, bays={0: 'ribbon', 4: 'curtain'}, solid_first=True)
    east = C.Face((X1, cx(SE[3], NE[2]), 0), (0, 1, 0), (-1, 0, 0), 'east')
    d = (NE[2] - SE[3]) / 2
    deck_face(east, -d, d, ['window', 'entry', 'entry'])
    north = C.Face((cx(X0, NE[0]), Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')
    w = (NE[0] - X0) / 2
    deck_face(north, -w, w, ['blank', 'window', 'blank', 'window', 'blank'], lite=True)
    west = C.Face((X0, cx(SWT[3], Y1 - T), 0), (0, -1, 0), (1, 0, 0), 'west')
    d = (Y1 - T - SWT[3]) / 2
    deck_face(west, -d, d, ['blank', 'window', 'blank', 'blank'], lite=True, precast=False)
    # Decks, internal columns, cars, lights.
    b = Batch()
    C.box('Ground slab', (0, 0, G0 / 2), (X1 - X0, Y1 - Y0, G0), 'foundation', 'decks', 0)
    for k, z in enumerate(DECKS):
        b.box('floor', 0, 0, z - .175, X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .35)
        b.box('concrete', 0, 0, z - .55, X1 - X0 - 2 * T - .2, .5, .4)          # spine beam
    for x in [X0 + 6.8 + 8.1 * i for i in range(6)]:
        for y in (-12.0, -4.0, 4.0, 12.0):
            b.box('concrete', x, y, (G0 + ROOF - .4) / 2, .6, .6, ROOF - .4 - G0)        # stop under the roof slab
    b.flush('decks')
    cars = Batch()
    tones = ['car_grey', 'car_dark', 'car_white', 'car_red', 'car_grey', 'car_white', 'car_dark']
    for k, z in enumerate(DECKS):
        for i, x in enumerate([X0 + 3.0 + 2.6 * j for j in range(17)]):
            if (i * 3 + k) % 4 == 0 or x > SE[0] - 2.0:
                continue
            tone = tones[(i + 2 * k) % len(tones)]
            cars.box(tone, x, Y0 + 3.4, z + .45, 1.8, 4.4, .7)
            cars.box(tone, x, Y0 + 3.6, z + 1.05, 1.6, 2.4, .55)
            cars.box('glass', x, Y0 + 3.6, z + 1.06, 1.62, 2.2, .45)
        for j, y in enumerate([SE[3] + 2.0 + 2.6 * q for q in range(9)]):
            if (j + k) % 3 == 0:
                continue
            tone = tones[(j + k) % len(tones)]
            cars.box(tone, X1 - 3.4, y, z + .45, 4.4, 1.8, .7)
            cars.box(tone, X1 - 3.6, y, z + 1.05, 2.4, 1.6, .55)
            cars.box('glass', X1 - 3.6, y, z + 1.06, 2.2, 1.62, .45)
        for x in (-20.0, -8.0, 4.0, 14.0):
            C.qa_room_light(f'Deck {k + 2} {x:+.0f}', (x, -10.0, LEVEL_TOPS[k] - .6), 60, 6.0)
    cars.flush('parked cars')
    for x in (-18.0, -8.0, 2.0, 10.0):
        C.qa_room_light(f'Retail {x:+.0f}', (x, Y0 + 4.0, 3.9), 110, 5.0)
        C.box('Retail counter', (x, Y0 + 6.0, G0 + .5), (3.0, .8, 1.0), 'pale', 'retail', 0)
    C.box('Retail back wall', (-2.0, Y0 + 9.0, (G0 + DECKS[0]) / 2), (38.0, .3, DECKS[0] - G0 - .4), 'interior', 'retail', 0)
    # Vehicle entry: barrier arms and a pay station.
    for y in (-2.8, 5.5):
        C.box('Barrier post', (X1 - 1.6, y - 2.2, G0 + .55), (.3, .3, 1.1), 'car_red', 'entry', 0)
        C.box('Barrier arm', (X1 - 1.6, y, G0 + 1.0), (.1, 4.0, .1), 'white', 'entry', 0)
    C.CONTACTS.append(dict(name='Decks on the brick frame and a column grid; cars on the deck slabs', decks_m=DECKS))


def roof_deck():
    hx0, hx1, hy0, hy1 = 2.8, 10.3, -3.6, 2.8                      # open stair well in the roof slab
    zt = ROOF
    for a, c, e, g in ((X0 + T, X1 - T, Y0 + T, hy0), (X0 + T, X1 - T, hy1, Y1 - T), (X0 + T, hx0, hy0, hy1), (hx1, X1 - T, hy0, hy1)):
        C.box('Roof deck slab', ((a + c) / 2, (e + g) / 2, zt - .175), (c - a, g - e, .35), 'floor', 'roof deck', 0)
    b = Batch()
    for i in range(18):                                            # stall stripes in two bands
        x = X0 + 3.0 + 2.7 * i
        if hx0 - 1.0 < x < hx1 + 1.0 or x > NE[0] - 1.0:
            continue
        for y in (Y0 + 3.4, Y1 - 3.4, -7.2, 6.4):
            b.box('white', x, y, zt + .006, .12, 4.8, .012)
    b.box('white', 0, -10.4, zt + .006, X1 - X0 - 6.0, .12, .012)
    b.box('white', 0, 9.6, zt + .006, X1 - X0 - 6.0, .12, .012)
    for x, y in ((-20.0, -10.0), (-4.0, -10.0), (12.0, -10.0), (-20.0, 10.0), (-4.0, 10.0)):
        b.box('hardware', x, y, zt + .4, .5, .5, .8)
    b.flush('roof deck')
    for x, y in ((-20.0, -10.0), (-4.0, -10.0), (12.0, -10.0), (-20.0, 10.0), (-4.0, 10.0)):
        C.rod('Light pole', (x, y, zt + .8), (x, y, zt + 7.5), .09, 'hardware', 'roof deck', 8)
        C.box('Light head', (x + .5, y, zt + 7.5), (1.0, .4, .15), 'hardware', 'roof deck', 0)
    # Lift overrun with vertical ribs, plant in the middle, guard rail round the open stair well.
    ox0, ox1 = -12.7, -5.3
    C.box('Lift overrun', ((ox0 + ox1) / 2, (hy0 + hy1) / 2, zt + 2.2), (ox1 - ox0, hy1 - hy0, 4.4), 'metal', 'penthouse', 0)
    C.box('Lift overrun roof', ((ox0 + ox1) / 2, (hy0 + hy1) / 2, zt + 4.45), (ox1 - ox0 + .3, hy1 - hy0 + .3, .1), 'trim', 'penthouse', 0)
    r = Batch()
    for i in range(int((ox1 - ox0) / .45)):
        x = ox0 + .2 + i * .45
        for y in (hy0 - .04, hy1 + .04):
            r.box('trim', x, y, zt + 2.2, .08, .08, 4.3)
    for j in range(int((hy1 - hy0) / .45)):
        y = hy0 + .2 + j * .45
        for x in (ox0 - .04, ox1 + .04):
            r.box('trim', x, y, zt + 2.2, .08, .08, 4.3)
    r.flush('overrun ribs')
    for x, y, s in ((-3.6, -1.4, 1.2), (-1.0, 1.0, 1.0), (1.2, -1.6, 1.0)):
        C.box('Rooftop unit', (x, y, zt + s / 2 + .1), (2.0, 1.6, s), 'pale', 'penthouse', 0)
        C.rod('Unit fan', (x, y, zt + s + .1), (x, y, zt + s + .18), .45, 'hardware', 'penthouse', 10)
    for (ax, ay), (bx, by) in (((hx0, hy0), (hx1, hy0)), ((hx1, hy0), (hx1, hy1)), ((hx1, hy1), (hx0, hy1)), ((hx0, hy1), (hx0, hy0))):
        C.beam('Stair well rail', (ax, ay, zt + 1.07), (bx, by, zt + 1.07), .05, .05, 'hardware', 'stair well')
        C.beam('Stair well mid rail', (ax, ay, zt + .55), (bx, by, zt + .55), .04, .04, 'hardware', 'stair well')
        n = max(2, int(math.hypot(bx - ax, by - ay) / 1.5))
        for i in range(n + 1):
            x, y = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
            C.beam('Stair well post', (x, y, zt), (x, y, zt + 1.07), .05, .05, 'hardware', 'stair well')
    for k in range(2):
        z = ROOF - (k + 1) * 1.6
        C.beam('Stair flight', (hx0 + 1.0, hy0 + 1.0 + k * 2.6, z), (hx1 - 1.0, hy0 + 1.0 + k * 2.6, z + 1.6), 1.2, .2, 'concrete', 'stair well')
    C.box('Stair well landing', ((hx0 + hx1) / 2, (hy0 + hy1) / 2, DECKS[3] - .175), (hx1 - hx0, hy1 - hy0, .35), 'floor', 'stair well', 0)


def tower(name, box, strips, top, patina_face=None):
    """Bronze-framed stair tower: faces of precast panel, glass and louvre strips, bronze band at the first deck,
    louvred crown with a patinated coping."""
    x0, x1, y0, y1 = box
    faces = dict(south=(C.Face(((x0 + x1) / 2, y0, 0), (1, 0, 0), (0, 1, 0), name + ' south'), x1 - x0, False),
                 north=(C.Face(((x0 + x1) / 2, y1, 0), (-1, 0, 0), (0, -1, 0), name + ' north'), x1 - x0, False),
                 east=(C.Face((x1, (y0 + y1) / 2, 0), (0, 1, 0), (-1, 0, 0), name + ' east'), y1 - y0, True),
                 west=(C.Face((x0, (y0 + y1) / 2, 0), (0, -1, 0), (1, 0, 0), name + ' west'), y1 - y0, True))
    zc = PARA + .2
    for side, (f, W, inner) in faces.items():
        lo, hi = (-W / 2 + T, W / 2 - T) if inner else (-W / 2, W / 2)
        kinds = strips.get(side, ('panel', 'panel', 'panel'))
        ws = [.3, .4, .3]
        edges = [lo + (hi - lo) * sum(ws[:i]) for i in range(4)]
        holes = []
        for i, kind in enumerate(kinds):
            a, c = edges[i] + .15, edges[i + 1] - .15
            if kind == 'glass':
                holes.append(hole(f'{f.label} glass strip', (a + c) / 2, G0 + .3, c - a, zc - G0 - .6, kind='glass'))
            elif kind == 'louvre':
                holes.append(hole(f'{f.label} louvre strip', (a + c) / 2, DECKS[0] + .4, c - a, zc - DECKS[0] - .8, kind='louvre'))
        f.wall(f'{f.label} precast carrier', lo, hi - EPS, G0, zc, depth=T, role='concrete', holes=holes)
        m = Merge(f)
        for h in holes:
            if h['kind'] == 'glass':
                framed(m, f, dict(h), cols=2, rows=round(h['h'] / 3.2), inset=.14, occupied='stair', kind='curtain wall', frame='bronze')
            else:
                n = int(h['h'] / .32)
                for k in range(n):
                    m.box('bronze', h['u'], .12, h['z'] + .16 + k * .32, h['w'] - .02, .26, .06)
                for k in range(int(h['w'] / .9) + 1):
                    m.box('bronze', h['u'] - h['w'] / 2 + .05 + k * (h['w'] - .1) / max(1, int(h['w'] / .9)), .12, h['z'] + h['h'] / 2, .06, .30, h['h'])
                C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='louvre screen', clear_wall_cut=True,
                    carrier_depth_m=T, frame_inset_m=.12, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='stair'))
        if inner:
            pass
        for e in edges:                                                      # bronze frame verticals
            m.box('bronze', e, -.08, (G0 + top) / 2, .24, .16, top - G0)
        for z in DECKS + [ROOF]:
            m.box('bronze', (lo + hi) / 2, -.13, z, hi - lo + .2, .16, .18)           # in front of the verticals, no coplanar crossings
        m.box('bronze', (lo + hi) / 2, -.45, DECKS[0] - .1, hi - lo + .5, .9, .3)   # projecting band at the first deck
        # Louvred crown above the parapet.
        n = int((top - zc - .4) / .3)
        for k in range(n):
            m.box('bronze', (lo + hi) / 2, -.02, zc + .25 + k * .3, hi - lo, .22, .07)
        if side == patina_face:                                                # patinated copper panel on the crown
            m.box('patina', lo + (hi - lo) * .7, -.16, (zc + top) / 2, (hi - lo) * .5, .06, top - zc - .2)
        m.flush(name)
    x0c, x1c, y0c, y1c = x0 - .25, x1 + .25, y0 - .25, y1 + .25            # closed patinated coping ring
    for yy in (y0c + .25, y1c - .25):
        C.box(name + ' coping', ((x0c + x1c) / 2, yy, top + .1), (x1c - x0c, .5, .2), 'patina', name, 0)
    for xx in (x0c + .25, x1c - .25):
        C.box(name + ' coping', (xx, (y0c + y1c) / 2, top + .1), (.5, y1c - y0c - 1.0, .2), 'patina', name, 0)
    C.box(name + ' crown core', ((x0 + x1) / 2, (y0 + y1) / 2, (zc + top) / 2), (x1 - x0 - 1.2, y1 - y0 - 1.2, top - zc), 'metal', name, 0)
    C.box(name + ' roof', ((x0 + x1) / 2, (y0 + y1) / 2, top + .06), (x1 - x0 - .2, y1 - y0 - .2, .12), 'pale', name, 0)
    for k in range(6):
        z = G0 + .3 + k * 3.2
        C.beam(name + ' stair flight', (x0 + 1.5, (y0 + y1) / 2 - 1.2, z), (x1 - 1.5, (y0 + y1) / 2 - 1.2, z + 1.6), 1.2, .2, 'concrete', name + ' stair')
        C.beam(name + ' stair flight', (x1 - 1.5, (y0 + y1) / 2 + 1.2, z + 1.6), (x0 + 1.5, (y0 + y1) / 2 + 1.2, z + 3.2), 1.2, .2, 'concrete', name + ' stair')
    C.qa_room_light(name + ' stair light', ((x0 + x1) / 2, (y0 + y1) / 2, ROOF - 1.0), 120, 4.0)


def glass_tower():
    x0, x1, y0, y1 = SWT
    top = PARA + 1.6
    b = Batch()
    for x in (x0 + .15, x1 - .15):
        for y in (y0 + .15, y1 - .15):
            b.box('bronze', x, y, (G0 + top) / 2, .3, .3, top - G0)
    b.box('glass', (x0 + x1) / 2, y0 + .05, (G0 + top) / 2, x1 - x0 - .3, .02, top - G0 - .2)
    b.box('glass', x0 + .05, (y0 + y1) / 2, (G0 + top) / 2, .02, y1 - y0 - .3, top - G0 - .2)
    b.box('glass', x1 - .05, (y0 + Y0) / 2, (G0 + top) / 2, .02, Y0 - y0 - .3, top - G0 - .2)
    for z in [G0 + .3] + DECKS + [ROOF, top - .3]:
        b.box('bronze', (x0 + x1) / 2, y0 + .02, z, x1 - x0, .1, .12)
        b.box('bronze', x0 + .02, (y0 + y1) / 2, z, .1, y1 - y0, .12)
    for k in range(1, 3):
        b.box('bronze', x0 + (x1 - x0) * k / 3, y0 + .02, (G0 + top) / 2, .08, .1, top - G0)
    b.box('metal', (x0 + x1) / 2, (y0 + y1) / 2, top + .3, x1 - x0 + .3, y1 - y0 + .3, .6)
    b.flush('glass stair tower')
    C.box('Glass tower north wall', ((x0 + x1) / 2, y1 - T / 2, (G0 + top) / 2), (x1 - x0, T, top - G0), 'wall', 'glass stair tower', 0)
    for k in range(6):
        z = G0 + .3 + k * 3.2
        C.beam('Glass tower stair', (x0 + .8, (y0 + y1) / 2, z), (x1 - .8, (y0 + y1) / 2, z + 3.2), 1.1, .2, 'concrete', 'glass stair tower')
    C.qa_room_light('Glass tower light', ((x0 + x1) / 2, (y0 + y1) / 2, top - 1.0), 80, 2.5)


def site():
    C.box('South sidewalk', (2.0, Y0 - 3.8, .07), (70.0, 7.6, .14), 'concrete', 'site', 0)
    C.box('East sidewalk', (X1 + 3.4, (Y0 + Y1 + 6.0) / 2, .07), (6.8, Y1 - Y0 + 6.0, .14), 'concrete', 'site', 0)
    C.box('South street', (6.0, Y0 - 13.6, .01), (82.0, 12.0, .02), 'asphalt', 'site', 0)
    C.box('East street', (X1 + 12.8, 3.2, .01), (12.0, 61.6, .02), 'asphalt', 'site', 0)
    b = Batch()
    b.box('car_red', 6.0, Y0 - 13.6, .025, 82.0, .12, .01)
    b.box('car_red', X1 + 12.8, 3.2, .025, .12, 61.6, .01)
    b.flush('street lines')
    for x in (-22.0, -8.0, 6.0):
        street_tree(x, Y0 - 3.4, z=.14, height=7.5, spread=1.8)
    for y in (-6.0, 8.0):
        street_tree(X1 + 3.2, y, z=.14, height=7.5, spread=1.8)


def build():
    site()
    frame_block()
    roof_deck()
    tower('south-east tower', SE, dict(south=('panel', 'glass', 'louvre'), east=('glass', 'louvre', 'panel'), north=('louvre', 'panel', 'panel'), west=('panel', 'panel', 'panel')), CROWN, patina_face='east')
    tower('north-east tower', NE, dict(east=('panel', 'glass', 'louvre'), north=('louvre', 'glass', 'panel'), south=('panel', 'louvre', 'panel'), west=('panel', 'panel', 'panel')), CROWN - .6, patina_face='north')
    glass_tower()
    C.CONTACTS.append(dict(name='Stair towers founded at grade and rising through the parapet; lift overrun on the roof deck', parapet_m=PARA))


LIGHT_RIG = dict(key=(-50, -60, 60), fill=(56, -30, 40), rear=(-20, 60, 50), target=(0, 0, 9.0), gain=9.0)
