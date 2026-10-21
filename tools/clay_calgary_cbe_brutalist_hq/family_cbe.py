"""Calgary Board of Education brutalist headquarters, authored from the locked catalogue views of
calgary_cbe_brutalist_hq / variant_0 (calgary-board-of-education-hq).

Read from the pixels (the top view governs the plan): a near-square four-storey brutalist office block on a street
corner, a street east and a street south, a paved plaza with a round sculpture plinth in the south-east and a lawn to
the south-west. Three upper office floors in a precast concrete box that cantilevers over a recessed ground storey:
a deep plain fascia band over the ground floor, then a grid of deep-set windows, one per bay, framed by tapered
vertical fins and by horizontal spandrel noses whose tops slope down from each sill, and a tall plain parapet band.
The ground storey sits back behind the upper box on a low podium: dark storefront glazing between concrete
mullions, board-formed concrete wall panels and freestanding board-formed columns carrying the cantilever, glazed
entrance doors facing the plaza. On the flat roof a set-back concrete mechanical penthouse with a louvre and a door,
two air-handling units with round fans and small vents. Context: brick neighbours west and north, sidewalks, street
trees, a crossing on the east street, and the sculpture of standing figures on its round plinth.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-calgary-cbe-brutalist-hq'
BAY = 2.7                                       # precast window module
NS, NE = 14, 13                                 # bays on the south and east fronts (top view 37.8 x 35.1 m)
X0, X1 = -NS * BAY / 2, NS * BAY / 2
Y0, Y1 = -NE * BAY / 2, NE * BAY / 2
T = .5                                          # precast carrier depth
TG = .35                                        # ground-storey carrier depth
PODIUM = .45                                    # podium top, ground floor level
PITCH = 4.0                                     # office storey pitch = one precast cell high
SOFF = PODIUM + 1.45 * PITCH                    # underside of the cantilevered box: a tall recessed ground storey
FASCIA = 1.4                                    # plain fascia band over the ground storey (about .35 of the pitch)
CELL0 = SOFF + FASCIA                           # bottom of the first row of precast window cells
FLOORS = tuple(CELL0 + .1 + PITCH * r for r in range(3))     # office floor levels
SILL = tuple(CELL0 + .9 + PITCH * r for r in range(3))      # glass sills, one row per floor
WH, WW = 2.4, 1.85                              # glass clear height and width at the back of each coffer
PARB = CELL0 + 3 * PITCH                        # top of the cell grid = foot of the parapet band
PAR = PARB + .55 * PITCH                        # parapet top: one plain band about .55 of the pitch
D = .55                                         # depth of the precast cell grid in front of the carrier
FB, FS = .28, .45                               # front width of the vertical cell members, front height of the horizontal ones
PROUD = .05                                     # fascia, parapet and corner piers stand this far proud of the grid
GH = 4.6                                        # two-tier storefront glazing height in the ground storey
INS = 3.0                                       # ground glazing line set back from the south and east faces
INW = 2.0                                       # ... and from the west and north faces
PH = dict(x0=-9.6, x1=8.7, y0=-9.35, y1=14.55, top=PAR + 4.4)    # mechanical penthouse (top view)
SCULPT = (12.1, -28.0)                          # sculpture plinth centre (top view)
EPS = .002
PALETTE = dict(wall=(.62, .58, .50), precast=(.65, .60, .51), board=(.54, .50, .43), joint=(.41, .38, .33),
    concrete=(.67, .64, .57), paving=(.60, .58, .53), frame=(.13, .13, .13), trim=(.13, .13, .13),
    glass=(.17, .21, .23), hardware=(.10, .10, .11), interior=(.80, .77, .71), floor=(.50, .46, .40),
    timber=(.40, .30, .20), planting=(.36, .46, .20), grass=(.33, .45, .22), soil=(.24, .18, .12),
    roof=(.52, .49, .44), membrane=(.55, .53, .49), asphalt=(.27, .27, .28), white=(.92, .92, .90),
    pale=(.84, .84, .82), metal=(.72, .72, .70), sculpture=(.80, .79, .76), neighbour=(.50, .30, .22),
    neighbourtrim=(.78, .74, .64))


def manifest(version):
    h = PH['top'] + .8
    cams = G.camera_roster(X1 - X0 + 4.0, Y1 - Y0 + 4.0, h, [
        ('facade_close', (0.0, -44.0, 14.5), (0.0, Y0, 14.5), 40),
        ('window_module', (9.5, -30.0, CELL0 + PITCH * 1.5), (6.75, Y0, CELL0 + PITCH * 1.5), 50),
        ('corner_cantilever', (X1 + 9.0, Y0 - 11.0, 2.2), (X1 - 2.0, Y0 + 1.5, SOFF), 30),
        ('ground_entrance', (4.0, Y0 - 13.0, 2.0), (4.0, Y0 + INS, 2.6), 35),
        ('arcade_soffit', (X1 - .6, Y0 + 2.45, 1.7), (X0 + 6.0, Y0 + 1.2, SOFF - 1.0), 30),
        ('sculpture_plaza', (SCULPT[0] + 9.0, SCULPT[1] - 9.0, 3.0), (SCULPT[0] - 2.0, SCULPT[1] + 2.0, 3.0), 30),
        ('west_side', (X0 - 44.0, 0.0, 34.0), (X0, 0.0, 15.0), 35),     # west coherence view over the brick neighbour (right_side already covers the east face)
        ('roof_penthouse', (-6.0, -34.0, 34.0), (0.0, 2.5, PAR + 1.0), 35),
        ('interior', (2.0, Y0 + 9.0, FLOORS[0] + 1.7), (2.0, Y0, SILL[0] + 1.0), 35),
        ('rear_north', (0.0, Y1 + 46.0, 22.0), (0.0, Y1, 10.0), 40)])
    for c in cams:                       # the locked front and oblique look from the south
        if c['name'] == 'front':
            c.update(location=(60.2, -76.9, 2.0), target=(4.8, -9.0, 11.6), lens=68, whole=False)   # fitted to the locked front's corners, penthouse and plinth (rms about 14 px): long lens, near-parallel verticals
        elif c['name'] == 'front_corner':
            c.update(location=(42.7, -52.0, 46.7), target=(1.0, -4.0, 7.0), lens=35, whole=False)   # the locked oblique: about 41 deg east of south, about 32 deg down, south:east face widths about 1.3
        elif c['name'] == 'aerial':
            c.update(location=(52.0, -64.0, 72.0), target=(0.0, -4.0, 6.0), lens=35, whole=False)
        elif c['name'] == 'left_side':
            c.update(location=(-50.0, -50.0, 22.0), target=(X0, -4.0, 8.0), lens=35, whole=False)   # south-west, past the brick neighbour
        elif c['name'] == 'right_side':
            c.update(location=(70.0, 0.0, 11.0), target=(X1, 0.0, 11.0), lens=35, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(0.0, 70.0, 25.0), target=(0.0, Y1, 11.0), lens=35, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(-48.0, 56.0, 36.0), target=(0.0, 0.0, 8.0), lens=35, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='calgary_cbe_brutalist_hq/variant_0 (calgary-board-of-education-hq)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=4, storey_programme='recessed ground storey (lobby and public counters), three office floors in the cantilevered precast box, a mechanical penthouse',
            plan=f'{X1 - X0:.1f} x {Y1 - Y0:.1f} m corner block of {NS} x {NE} precast bays (top view); penthouse set back towards the north',
            facade='plain fascia over a tall recessed ground storey; a flush cellular precast grid, one deep coffer per bay and floor splayed on all four sides to the glass, continuous horizontal members at the floor lines; one continuous plain parapet band; board-formed columns and wall panels below',
            levels_m=[PODIUM, SOFF, *FLOORS, PAR, PH['top']], roof_m=dict(flat=PAR - 1.0, parapet=PAR, penthouse=PH['top']),
            inferred='interiors, the west and north elevations and the ground-floor layout behind the glass are teaching assumptions'),
        roof_contract=dict(type='flat membrane roof inside a precast parapet; a set-back concrete mechanical penthouse with air-handling units', datum_m=PAR - 1.0, crowns_m=[PH['top'] + 1.4]),
        identity_contract=dict(owner='1960s brutalist office headquarters: a precast window-grid box cantilevered over a recessed board-formed ground storey, with a rooftop penthouse and a sculpture plaza'),
        material_contract=dict(profile='source-palette clay: warm grey precast concrete, darker board-formed concrete, dark bronze frames and tinted glass, membrane roof', textured_keeper=False),
        programme_contract=dict(storeys=4, ground='lobby, public counters and board room behind storefront glazing', upper='open and cellular offices'),
        contact_contract=['Grade-zero sidewalks, streets and plaza', 'Podium and steps from grade', 'Board-formed columns and ground walls on the podium', 'Precast box on the columns and the ground walls', 'Penthouse on the roof slab'],
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


# ---- Calgary Board of Education brutalist headquarters ----

class Kit(Merge):
    """Merge plus prisms in face coordinates: a (u, d) plan polygon run up in z, or a (d, z) section run along u."""
    def _prism(self, role, lo, hi):
        vs, fs = self.groups.setdefault(role, ([], []))
        o, n = len(vs), len(lo)
        vs.extend(lo + hi)
        fs.append(tuple(o + i for i in range(n - 1, -1, -1)))
        fs.append(tuple(o + n + i for i in range(n)))
        fs.extend((o + i, o + (i + 1) % n, o + n + (i + 1) % n, o + n + i) for i in range(n))

    def zprism(self, role, pts, z0, z1):
        self._prism(role, [self.f.p(u, d, z0) for u, d in pts], [self.f.p(u, d, z1) for u, d in pts])

    def uprism(self, role, u0, u1, pts):
        self._prism(role, [self.f.p(u0, d, z) for d, z in pts], [self.f.p(u1, d, z) for d, z in pts])


def bay_centres(n):
    """Window centres, one per precast cell."""
    return [-n * BAY / 2 + BAY * (k + .5) for k in range(n)]


def coffer(m, role, u0, u1, z0, z1, g0, g1, h0, h1):
    """One precast window cell as a closed ring solid: a flush front frame at d = -D around the outer opening, four
    splayed reveals (jambs, head and a deep sloped sill) narrowing to the glass opening g0..g1 x h0..h1 at the
    carrier face d = 0, and a back ring on the carrier face."""
    vs, fs = m.groups.setdefault(role, ([], []))
    o = len(vs)
    a0, a1, b0, b1 = u0 + FB / 2, u1 - FB / 2, z0 + FS * .45, z1 - FS * .55
    ring = lambda us, zs, d: [m.f.p(us[0], d, zs[0]), m.f.p(us[1], d, zs[0]), m.f.p(us[1], d, zs[1]), m.f.p(us[0], d, zs[1])]
    vs.extend(ring((u0, u1), (z0, z1), -D) + ring((a0, a1), (b0, b1), -D) + ring((u0, u1), (z0, z1), 0.0) + ring((g0, g1), (h0, h1), 0.0))
    A, B, Cc, E = o, o + 4, o + 8, o + 12
    for i in range(4):
        j = (i + 1) % 4
        fs.append((A + i, A + j, B + j, B + i))          # front frame
        fs.append((B + i, B + j, E + j, E + i))          # splayed reveal
        fs.append((E + i, E + j, Cc + j, Cc + i))        # back ring on the carrier
        fs.append((Cc + i, Cc + j, A + j, A + i))        # outer sides (shared with the neighbouring cell, hidden)


def upper_face(label, origin, tangent, inward, n, wrap):
    """The precast office box: carrier with one glass opening per bay and floor, a flush cellular grid of deep
    coffers in front of it (continuous horizontal members at the floor lines, one tapered vertical member per cell
    and storey), a plain fascia over the ground storey and one continuous plain parapet band above the grid.
    South and north run the full length and wrap the corners; east and west butt between them."""
    f = C.Face(origin, tangent, inward, label)
    L = n * BAY
    lo, hi = (-L / 2, L / 2) if wrap else (-L / 2 + T, L / 2 - T)
    holes = [hole(f'{label} window f{r + 1} b{k + 1:02d}', u, SILL[r], WW, WH, kind='window')
             for r in range(3) for k, u in enumerate(bay_centres(n))]
    f.wall(f'{label} precast carrier', lo, hi - EPS, SOFF, PAR, depth=T, role='precast', holes=holes)
    m = Kit(f)
    for h in holes:
        framed(m, f, h, cols=1, rows=1, inset=.12, occupied='office', frame='frame')
        m.box('frame', h['u'], .11, h['z'] + .62, WW - .14, .06, .05)                    # hopper rail low in each light
    for r in range(3):                                                                     # the cellular grid
        z0 = CELL0 + PITCH * r
        for k, u in enumerate(bay_centres(n)):
            coffer(m, 'precast', u - BAY / 2, u + BAY / 2, z0, z0 + PITCH, u - WW / 2, u + WW / 2, SILL[r], SILL[r] + WH)
    F = D + PROUD
    bl, bh = (-L / 2 - F, L / 2 + F) if wrap else (-L / 2, L / 2)
    m.uprism('precast', bl, bh, [(0.0, SOFF), (-F, SOFF), (-F, CELL0), (0.0, CELL0)])        # plain fascia
    m.uprism('precast', bl, bh, [(0.0, PARB), (-F, PARB), (-F, PAR), (0.0, PAR)])            # one plain parapet band
    zj = PARB + (PAR - PARB) * .45
    m.box('joint', (bl + bh) / 2, -F - .002, zj, bh - bl - .04, .004, .025)                # its single horizontal joint
    cl, ch = (-L / 2 - F - .05, L / 2 + F + .05) if wrap else (-L / 2 + T, L / 2 - T)
    m.box('precast', (cl + ch) / 2, (T - F - .05) / 2, PAR + .06, ch - cl, T + F + .05, .12)               # coping
    m.flush(label)
    return f


def corner_piers():
    """Solid precast piers closing the grid at the four corners, flush with the fascia and parapet."""
    b = Batch()
    F = D + PROUD
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        xc = X1 if sx > 0 else X0
        yc = Y1 if sy > 0 else Y0
        xa, xb = sorted((xc, xc + sx * F))
        ya, yb = sorted((yc, yc + sy * F))
        b.box('precast', (xa + xb) / 2, (ya + yb) / 2, (CELL0 + PARB) / 2, xb - xa, yb - ya, PARB - CELL0)
    b.flush('corner piers')


def ground_face(label, origin, tangent, inward, lo, hi, bays):
    """Recessed ground storey: board-formed concrete carrier with storefront lights, entrance doors and small
    windows; bays is a list of (u, kind)."""
    f = C.Face(origin, tangent, inward, label)
    hs = []
    for u, kind in bays:
        if kind == 'glass':
            hs.append((hole(f'{label} storefront {u:+.2f}', u, PODIUM + .15, BAY - .4, GH, kind='shopfront'), kind))
        elif kind == 'door':
            hs.append((hole(f'{label} entrance {u:+.2f}', u, PODIUM, BAY - .4, GH + .15, kind='door'), kind))
        elif kind == 'window':
            hs.append((hole(f'{label} window {u:+.2f}', u, PODIUM + 1.3, BAY - .6, GH - 1.15), kind))
        elif kind == 'service':
            hs.append((hole(f'{label} service door {u:+.2f}', u, PODIUM, 1.1, 2.3, kind='door'), kind))
    holes = [h for h, k in hs]
    f.wall(f'{label} board-formed carrier', lo, hi - EPS, PODIUM, SOFF - EPS, depth=TG, role='board', holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, PODIUM + .3, SOFF - .1, holes, spacing=.3)       # board marks
    m = Kit(f)
    for h, kind in hs:
        if kind == 'glass':
            framed(m, f, h, cols=2, rows=1, inset=.12, occupied='lobby', kind='shopfront', frame='frame')
            m.box('frame', h['u'], .1, h['z'] + 3.0, h['w'] - .1, .1, .08)                     # transom bar
        elif kind == 'door':
            framed(m, f, h, cols=2, rows=1, inset=.12, occupied='lobby', kind='door', frame='frame')
            m.box('frame', h['u'], .1, h['z'] + 2.45, h['w'] - .1, .1, .1)                    # transom over the leaves
            m.box('frame', h['u'], .1, h['z'] + 1.2, .1, .1, 2.4)                             # meeting stiles
            for s in (-1, 1):                                                                 # push bars
                m.box('metal', h['u'] + s * .3, .06, h['z'] + 1.05, .5, .04, .04)
        elif kind == 'window':
            framed(m, f, h, cols=2, rows=1, inset=.12, occupied='office', frame='frame')
            m.box('frame', h['u'], .1, h['z'] + 1.9, h['w'] - .1, .1, .08)
        else:
            framed(m, f, h, cols=1, rows=1, inset=.12, occupied='service', kind='door', frame='frame', glass='metal')
    m.flush(label)
    return f


def build_box():
    upper_face('south', (0, Y0, 0), (1, 0, 0), (0, 1, 0), NS, True)
    upper_face('north', (0, Y1, 0), (-1, 0, 0), (0, -1, 0), NS, True)
    upper_face('east', (X1, 0, 0), (0, 1, 0), (-1, 0, 0), NE, False)
    upper_face('west', (X0, 0, 0), (0, -1, 0), (1, 0, 0), NE, False)
    corner_piers()
    # Ground storey behind the cantilever: glazing line set back 3 m on the street fronts, 2 m behind.
    gx0, gx1, gy0, gy1 = X0 + INW, X1 - INS, Y0 + INS, Y1 - INW
    sx = [X0 + BAY * (k + .5) for k in range(NS)]
    sy = [Y0 + BAY * (k + .5) for k in range(NE)]
    south = ['solid', 'board', 'board', 'board', 'board', 'glass', 'glass', 'glass', 'glass', 'door', 'glass', 'glass', 'glass', 'solid']
    ground_face('ground south', (0, gy0, 0), (1, 0, 0), (0, 1, 0), gx0, gx1, [(sx[k], kind) for k, kind in enumerate(south)])
    east = ['solid', 'solid', 'door', 'glass', 'glass', 'glass', 'board', 'board', 'board', 'glass', 'glass', 'glass', 'solid']
    ground_face('ground east', (gx1, 0, 0), (0, 1, 0), (-1, 0, 0), gy0 + TG, gy1 - TG, [(sy[k], kind) for k, kind in enumerate(east)])
    north = ['solid', 'window', 'board', 'service', 'board', 'window', 'board', 'window', 'board', 'window', 'board', 'window', 'board', 'solid']
    ground_face('ground north', (0, gy1, 0), (-1, 0, 0), (0, -1, 0), -gx1, -gx0, [(-sx[k], kind) for k, kind in enumerate(north)])
    west = ['solid', 'board', 'window', 'board', 'window', 'board', 'window', 'board', 'window', 'board', 'window', 'board', 'solid']
    ground_face('ground west', (gx0, 0, 0), (0, -1, 0), (1, 0, 0), -(gy1 - TG), -(gy0 + TG), [(-sy[k], kind) for k, kind in enumerate(west)])
    # Freestanding board-formed columns under the cantilever, on the bay lines.
    b = Batch()
    cols = [(X0 + BAY * k, Y0 + 1.4) for k in (3, 7, 11)] + [(X1 - 1.4, Y0 + BAY * k) for k in (3, 7, 10)] + \
           [(X0 + 1.0, Y0 + BAY * k) for k in (4, 9)] + [(X0 + BAY * k, Y1 - 1.0) for k in (4, 10)]
    for x, y in cols:
        b.box('board', x, y, (PODIUM + SOFF - EPS) / 2, .9, .9, SOFF - EPS - PODIUM)
        z = PODIUM + .3
        while z < SOFF - .1:                                                                   # board marks round the shaft
            b.box('joint', x, y, z, .904, .904, .006)
            z += .3
    b.flush('columns')
    C.CONTACTS.append(dict(name='Board-formed columns and ground walls on the podium; precast box on them', soffit_m=SOFF))


def floors_and_roof():
    w, d = X1 - X0 - 2 * T, Y1 - Y0 - 2 * T
    C.box('First floor slab and soffit', (0, 0, (SOFF + FLOORS[0]) / 2), (w, d, FLOORS[0] - SOFF), 'precast', 'inside', 0)
    for z in FLOORS[1:]:
        C.box(f'Floor {z:.1f}', (0, 0, z - .15), (w, d, .3), 'floor', 'inside', 0)
    C.box('Roof slab', (0, 0, PAR - 1.175), (w, d, .35), 'roof', 'roof', 0)
    C.box('Service core', (0, 0, (PODIUM + PAR - 1.35) / 2), (10.0, 7.0, PAR - 1.35 - PODIUM), 'interior', 'inside', 0)
    for z in (PODIUM, *FLOORS):
        for x in (-11.0, 0.0, 11.0):
            for y in (Y0 + 5.0, Y1 - 5.0):
                C.qa_room_light(f'Room {x:+.0f} {y:+.0f} {z:.0f}', (x, y, z + 2.8), 90, 3.0)
    # Mechanical penthouse, set back towards the north (top view): precast walls, a louvre and two steel doors.
    z0, z1, tp = PAR - 1.0, PH['top'], .3
    x0, x1, y0, y1 = PH['x0'], PH['x1'], PH['y0'], PH['y1']
    faces = [('penthouse south', (0, y0, 0), (1, 0, 0), (0, 1, 0), x0, x1,
              [('door', -8.3, .05, 1.0, 2.2), ('louvre', -5.6, 2.6, 2.6, 1.8), ('door', 7.0, .05, 1.0, 2.2)]),
             ('penthouse north', (0, y1, 0), (-1, 0, 0), (0, -1, 0), -x1, -x0, [('louvre', 2.0, 2.6, 3.2, 1.8)]),
             ('penthouse east', (x1, 0, 0), (0, 1, 0), (-1, 0, 0), y0 + tp, y1 - tp, [('louvre', 4.0, 2.6, 2.4, 1.8)]),
             ('penthouse west', (x0, 0, 0), (0, -1, 0), (1, 0, 0), -(y1 - tp), -(y0 + tp), [('louvre', -1.0, 2.6, 3.6, 1.8), ('door', 6.0, .05, 1.0, 2.2)])]
    for label, o, t, n, lo, hi, ops in faces:
        f = C.Face(o, t, n, label)
        hs = [(hole(f'{label} {k} {u:+.1f}', u, z0 + z, w_, h_, kind='door' if k == 'door' else 'louvre'), k) for k, u, z, w_, h_ in ops]
        f.wall(f'{label} wall', lo, hi - EPS, z0, z1, depth=tp, role='precast', holes=[h for h, k in hs])
        m = Kit(f)
        for h, k in hs:
            if k == 'door':
                framed(m, f, h, cols=1, rows=1, inset=.1, occupied='plant', kind='door', frame='frame', glass='hardware')
            else:
                framed(m, f, h, cols=1, rows=1, inset=.1, occupied='plant', kind='louvre', frame='frame', glass='hardware')
                for i in range(1, 9):                                                         # louvre blades
                    m.box('metal', h['u'], .06, h['z'] + h['h'] * i / 9, h['w'] - .16, .1, .05)
        for k in range(1, int((hi - lo) / 2.4)):                                              # precast panel joints
            u = lo + (hi - lo) * k / int((hi - lo) / 2.4)
            if all(abs(u - h['u']) > h['w'] / 2 + .1 for h, _ in hs):
                m.box('joint', u, -.002, (z0 + z1) / 2, .025, .004, z1 - z0 - .1)
        m.flush(label)
    C.box('Penthouse roof', ((x0 + x1) / 2, (y0 + y1) / 2, z1 + .15), (x1 - x0 + .3, y1 - y0 + .3, .3), 'precast', 'roof', 0)
    C.box('Penthouse floor', ((x0 + x1) / 2, (y0 + y1) / 2, z0 + .1), (x1 - x0 - 2 * tp, y1 - y0 - 2 * tp, .2), 'floor', 'inside', 0)
    C.qa_room_light('Penthouse plant', ((x0 + x1) / 2, (y0 + y1) / 2, z1 - 1.0), 60, 3.0)
    b = Batch()
    zt = z1 + .3
    for x in (-3.1, 2.35):                                                                     # two air-handling units with fans
        b.box('pale', x, -2.2, zt + .8, 2.4, 6.2, 1.6)
        b.box('metal', x, -2.2, zt + 1.62, 2.5, 6.3, .04)
    b.box('pale', 1.0, 12.3, zt + .5, 1.4, 1.4, 1.0)                                           # small unit and vents
    b.box('metal', 4.1, 6.0, zt + .35, .8, .8, .7)
    b.box('metal', -0.2, 0.6, zt + .3, 3.4, .12, .12)                                          # duct between the units
    rz = PAR - 1.0
    b.box('pale', 10.1, 1.0, rz + .6, 1.6, 2.2, 1.2)                                           # rooftop unit on the main roof, railed
    for xa, ya, xb, yb in ((9.0, -.5, 11.2, -.5), (9.0, 2.5, 11.2, 2.5), (9.0, -.5, 9.0, 2.5), (11.2, -.5, 11.2, 2.5)):
        b.beam('hardware', (xa, ya, rz + 1.1), (xb, yb, rz + 1.1), .05, ext=.025)
    for x, y in ((9.0, -.5), (11.2, -.5), (9.0, 2.5), (11.2, 2.5)):
        b.box('hardware', x, y, rz + .55, .05, .05, 1.1)
    b.box('metal', -14.0, 10.0, rz + .25, .7, .7, .5)
    b.box('metal', 13.5, -12.0, rz + .25, .7, .7, .5)
    b.box('pale', 14.0, 12.5, rz + .4, 1.2, 1.2, .8)
    b.flush('roof plant')
    for x in (-3.1, 2.35):
        for y in (-3.8, -.6):
            annulus('AHU fan shroud', (x, y, zt + 1.64), (0, 0, 1), .62, .72, 0.0, .18, 'metal', 'roof plant', 24)
            C.rod('AHU fan hub', (x, y, zt + 1.64), (x, y, zt + 1.72), .16, 'hardware', 'roof plant', 12)
    C.CONTACTS.append(dict(name='Flat roof inside the parapet; penthouse and plant on the roof slab', roof_m=PAR - 1.0))


def figure(x, y, z, a, s=1.0):
    """A standing figure of the sculpture group: legs, torso, arms and head as rods."""
    ux, uy = math.cos(a), math.sin(a)
    tx, ty = -uy, ux
    for e in (-1, 1):
        C.rod('Sculpture leg', (x + tx * e * .08 * s, y + ty * e * .08 * s, z), (x + tx * e * .07 * s, y + ty * e * .07 * s, z + 1.05 * s), .065 * s, 'sculpture', 'sculpture', 8)
        C.rod('Sculpture arm', (x + tx * e * .2 * s, y + ty * e * .2 * s, z + 1.0 * s), (x + tx * e * .18 * s, y + ty * e * .18 * s, z + 1.72 * s), .045 * s, 'sculpture', 'sculpture', 8)
    C.rod('Sculpture torso', (x, y, z + 1.0 * s), (x, y, z + 1.8 * s), .14 * s, 'sculpture', 'sculpture', 10)
    C.rod('Sculpture neck', (x, y, z + 1.78 * s), (x, y, z + 1.9 * s), .06 * s, 'sculpture', 'sculpture', 8)
    C.rod('Sculpture head', (x, y, z + 1.88 * s), (x, y, z + 2.16 * s), .1 * s, 'sculpture', 'sculpture', 12)


def site():
    PS, PE, PW, PN = 3.5, 3.5, 1.2, 1.2                                                        # podium margins
    C.box('Podium', ((X0 - PW + X1 + PE) / 2, (Y0 - PS + Y1 + PN) / 2, PODIUM / 2), (X1 + PE - X0 + PW, Y1 + PN - Y0 + PS, PODIUM), 'concrete', 'site', 0)
    for name, x0, x1, y0, y1, h in (('South step low', X0 - PW, X1 + PE + .8, Y0 - PS - .8, Y0 - PS - .4, .15),
                                    ('South step high', X0 - PW, X1 + PE + .4, Y0 - PS - .4, Y0 - PS, .30),
                                    ('East step low', X1 + PE + .4, X1 + PE + .8, Y0 - PS - .4, Y1 + PN, .15),
                                    ('East step high', X1 + PE, X1 + PE + .4, Y0 - PS, Y1 + PN, .30)):
        C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), 'concrete', 'site', 0)
    ys, xe = Y0 - PS - .8, X1 + PE + .8                                                        # edge of the steps
    plates = [('South street', -40.0, X1 + 26.0, -50.0, -40.5, .02, 'asphalt'),
              ('South sidewalk', -40.0, X1 + 7.0, -40.5, -37.5, .12, 'concrete'),
              ('East street', X1 + 7.0, X1 + 19.0, -40.5, Y1 + 22.0, .02, 'asphalt'),
              ('East far sidewalk', X1 + 19.0, X1 + 26.0, -40.5, Y1 + 22.0, .12, 'concrete'),
              ('East sidewalk', xe, X1 + 7.0, -37.5, Y1 + 22.0, .12, 'concrete'),
              ('Sculpture plaza', -0.6, xe, -37.5, ys, .05, 'paving'),
              ('South lawn', X0 - PW, -0.6, -37.5, ys, .06, 'grass'),
              ('West walk', X0 - PW - 3.0, X0 - PW, -37.5, Y1 + 6.0, .05, 'paving'),
              ('South-west lawn', -40.0, X0 - PW - 3.0, -37.5, -10.0, .06, 'grass'),
              ('West lawn', -25.0, X0 - PW - 3.0, -10.0, Y1 + 6.0, .06, 'grass'),
              ('North lawn', X0 - PW, xe, Y1 + PN, Y1 + 6.0, .06, 'grass')]
    for name, x0, x1, y0, y1, h, role in plates:
        C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), role, 'site', 0)
    b = Batch()
    x = -0.6 + 3.0                                                                             # plaza paving joints
    while x < xe - .2:
        b.box('joint', x, (ys - 37.5) / 2, .051, .03, ys + 37.5 - .02, .004)
        x += 3.0
    y = -37.5 + 3.0
    while y < ys - .2:
        b.box('joint', (xe - .6) / 2, y, .051, xe + .6 - .02, .03, .004)
        y += 3.0
    for k in range(8):                                                                         # crossing on the east street
        b.box('white', X1 + 7.8 + k * 1.45, -27.0, .024, .6, 3.6, .008)
    y = -22.0
    while y < Y1 + 20.0:                                                                       # lane line
        b.box('white', X1 + 13.0, y, .024, .14, 3.0, .008)
        y += 6.0
    x = -38.0
    while x < X1 + 5.0:
        b.box('white', x, -45.25, .024, 3.0, .14, .008)
        x += 6.0
    b.box('hardware', X1 + 6.2, -33.5, 2.6, .14, .14, 5.0)                                     # lamp standard at the corner
    b.box('pale', X1 + 6.2, -33.5, 5.3, .4, .4, .4)
    b.box('hardware', X1 + 6.2, -33.5, 5.55, .5, .5, .1)
    b.box('metal', X1 + 6.2, -20.0, 1.25, .1, .1, 2.3)                                         # sign post and sign
    b.box('white', X1 + 6.2, -20.0, 2.6, .06, .6, .8)
    for x0 in (-14.0, -7.0):                                                                   # benches on the lawn edge
        b.box('concrete', x0, ys - 1.0, .3, 2.0, .5, .1)
        for s in (-1, 1):
            b.box('concrete', x0 + s * .75, ys - 1.0, .155, .2, .45, .21)
    b.flush('street')
    sx, sy = SCULPT                                                                            # The sculpture on its round plinth
    C.rod('Sculpture plinth', (sx, sy, .05), (sx, sy, .8), 3.1, 'concrete', 'sculpture', 48)
    for i in range(12):
        a = math.tau * i / 12 + .2
        r = 2.1 if i % 2 else 1.7
        figure(sx + r * math.cos(a), sy + r * math.sin(a), .8, a, s=1.34 if i % 3 else 1.22)
    for x, y in ((X1 + 5.6, -15.5), (X1 + 5.6, -4.0), (X1 + 5.6, 6.0), (X1 + 5.6, 16.0)):
        street_tree(x, y, z=.12, height=8.0, spread=2.4)
    for x, y in ((-21.0, -26.5), (-29.0, -28.0), (-6.5, -27.0), (-33.0, -18.0), (-27.0, 2.0)):
        street_tree(x, y, z=.06, height=9.0, spread=2.8)
    # Brick neighbours: three storeys west, two to three storeys north (context only).
    nb = [('West neighbour', -37.0, -25.4, -9.4, 22.6, 11.0, 'east'),
          ('North-west neighbour', -25.0, -8.6, Y1 + 6.0, Y1 + 18.0, 9.0, 'south'),
          ('North-east neighbour', 4.3, 17.4, Y1 + 6.0, Y1 + 18.0, 9.5, 'south')]
    b = Batch()
    for name, x0, x1, y0, y1, h, face in nb:
        C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), 'neighbour', 'context', 0)
        b.box('membrane', (x0 + x1) / 2, (y0 + y1) / 2, h + .03, x1 - x0 - .4, y1 - y0 - .4, .06)
        for z in (1.0, 4.4, 7.6)[: int(h // 3.3)]:
            if face == 'east':
                yy = y0 + 1.8
                while yy < y1 - 1.0:
                    b.box('glass', x1 + .02, yy, z + .9, .04, 1.2, 1.8)
                    b.box('neighbourtrim', x1 + .04, yy, z - .02, .08, 1.4, .1)
                    yy += 3.2
            else:
                xx = x0 + 1.8
                while xx < x1 - 1.0:
                    b.box('glass', xx, y0 - .02, z + .9, 1.2, .04, 1.8)
                    b.box('neighbourtrim', xx, y0 - .04, z - .02, 1.4, .08, .1)
                    xx += 3.2
    b.flush('neighbours')


def build():
    site()
    build_box()
    floors_and_roof()
    C.CONTACTS.append(dict(name='Brutalist precast office box cantilevered over a recessed board-formed ground storey', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(-48.0, -66.0, 52.0), fill=(60.0, -30.0, 36.0), rear=(-24.0, 56.0, 44.0), target=(0, 0, 8.0), gain=6.0)
