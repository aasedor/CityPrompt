"""Modernista iron-and-glass market hall, authored from the locked catalogue views of
barcelona_mercat / variant_0 (mercat_modernista).

Read from the pixels: a single-storey square hall on a paved plaza. Four gabled iron-and-glass wings
in a pinwheel cross around a square central lantern with a pyramidal roof (top view); the gable ends
carry great semicircular iron arches with stained-glass tympana, a wrought-iron crest and a coat of
arms, the south one over the main entrance between stone piers; lower aisle roofs fill the four corner
quadrants with small gablets along their eaves; the perimeter is a tiled dado wall with cast-iron
columns, iron-framed glazing above and coloured canvas awnings over every bay; stalls of produce inside.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-modernista-market-hall'
S = 46.0                          # square hall side
HW = 9.0                          # wing half-width (18 m wings)
EAVE_A = 6.8                      # aisle (quadrant) eave at the outer walls
EAVE_W = 10.5                     # wing eave over the quadrant roofs
RIDGE = 17.2                      # wing ridge (the great arch sits inside the gable, v001 P0 1)
LANT = 7.0                        # central lantern half-side
LANT_BASE, LANT_TOP, LANT_APEX = 11.0, 20.4, 27.0   # glazed lantern drum buried in the roof crossing, steep glazed pyramid (v001 P0 2, P1 6)
DADO = 1.3
T = .30
G0 = .15
BAY = 4.6
EPS = .002
PLAZA = 14.0
PALETTE = dict(wall=(.62, .54, .44), joint=(.46, .40, .32), trim=(.16, .18, .17),
    pale=(.78, .74, .66), stone=(.72, .66, .56), roof=(.38, .34, .28), sand=(.70, .64, .52),
    foundation=(.52, .52, .50), glass=(.46, .54, .56), hardware=(.14, .16, .15),
    interior=(.80, .76, .68), floor=(.50, .48, .44), timber=(.40, .28, .16), blue=(.14, .22, .28),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.64, .62, .58), tile=(.66, .46, .30), tile_dark=(.48, .30, .20),
    stain_red=(.62, .16, .14), stain_gold=(.84, .64, .20), stain_blue=(.20, .34, .58), stain_green=(.24, .48, .30),
    stain_teal=(.24, .46, .44), stain_aqua=(.32, .52, .50), stain_amber=(.66, .50, .24),
    awning_red=(.70, .14, .10), awning_yellow=(.86, .68, .16), awning_blue=(.16, .30, .60), gilt=(.80, .64, .26), produce=(.62, .32, .16))


def manifest(version):
    h = LANT_APEX + 2.5
    cams = G.camera_roster(S + 2 * PLAZA, S + 2 * PLAZA, h, [
        ('facade_close', (-14.0, -42.0, 5.0), (-4.0, -S / 2, 7.0), 45),
        ('architecture_close', (-40.0, -40.0, 14.0), (-S / 2 + 6.0, -S / 2 + 6.0, 8.0), 50),
        ('glass_close', (-14.0, -32.0, 3.0), (-14.0, -S / 2, 4.0), 50),
        ('great_arch', (-6.0, -52.0, 6.0), (0.0, -S / 2, 9.0), 40),
        ('aisle_arcade', (-30.0, -36.0, 3.0), (-14.0, -S / 2, 4.0), 40),
        ('lantern_roofs', (-40.0, -46.0, 30.0), (0.0, 0.0, 15.0), 45),
        ('crest_contact', (6.0, -40.0, 15.0), (0.0, -S / 2, 15.5), 45),
        ('plaza_awnings', (30.0, -38.0, 4.0), (10.0, -S / 2, 4.0), 40),
        ('interior', (0.0, -S / 2 + 2.0, 1.7), (0.0, 8.0, 5.0), 35),
        ('rear_court', (26.0, 44.0, 8.0), (0.0, S / 2, 9.0), 40)])
    for c in cams:
        if c['name'] == 'front':          # eye level on the plaza axis facing the great arch (locked front)
            c['location'] = (-16.0, -82.0, 1.7); c['target'] = (-2.0, -S / 2, 9.0); c['lens'] = 28; c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='barcelona_mercat/variant_0 (mercat_modernista)',
        measurement_contract=dict(dimensions_m=dict(width=S + 2 * PLAZA, depth=S + 2 * PLAZA, height=h),
            observed_storeys=1, storey_programme='single-storey market hall with a central lantern',
            plan='46 x 46 m square hall (top view) on a paved plaza: four 18 m gabled wings in a cross around a 14 m square lantern, lower aisle roofs in the four corner quadrants',
            section='tiled dado 1.3 m, cast-iron columns at 4.6 m with iron-framed glazing to the aisle eave at 6.8 m; wing eaves at 10.5 m over the quadrant roofs with louvred clerestories; wing ridges at 17.2 m with glazed ridge monitors beside the lantern; glazed lantern drum to 20.4 m with a steep glazed pyramid to 27 m',
            gables='each gable end a semicircular iron archivolt 14 m across set inside the gable with a stained-glass tympanum mosaic and rose, a coat-of-arms shield in the gable field, lattice spandrels, scrolled cresting along both rakes and a tall apex finial; the south gable over the main entrance between stone piers',
            perimeter='coloured canvas awnings over every bay, gablets along the quadrant eaves, bollards and trees on the plaza',
            inferred='the north and east gables repeat the south grammar with clear glass; interiors are stalls as teaching assumptions'),
        roof_contract=dict(type='gabled metal roofs with cut glazed strips and ridge monitors, glazed pyramid lantern, lean-to quadrant roofs with glazed strips and gablets', datum_m=EAVE_A, crowns_m=[RIDGE, LANT_APEX]),
        identity_contract=dict(owner='great iron gable arches with stained glass and crests, pinwheel of gabled wings around the square lantern, tiled dado with cast-iron columns and glazing, coloured awnings, plaza'),
        material_contract=dict(profile='source-palette clay: warm ochre tile dado with a darker base, dark cast iron, glass, stained-glass colour panels, brown-grey roof plates with glass strips, red, yellow and blue canvas awnings, stone piers', textured_keeper=False),
        programme_contract=dict(storeys=1, ground='market stalls in four aisles meeting under the lantern', upper='none', roof='lantern ventilation'),
        contact_contract=['Grade-zero slab and plaza', 'Columns on the dado plinth', 'Wing walls on interior columns over the quadrant roofs', 'Gable screens between the stone piers on the plinth', 'Lantern on the wing ridges', 'Awnings on arms from the columns'],
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


def iron_balcony(m, f, u, z, w, depth=.8, role='hardware', slab='stone'):
    """Cantilevered balcony: stone slab with a merged iron lattice (top rail, end rails, mid rail, pickets)."""
    m.box(slab, u, -depth / 2 + .02, z - .10, w, depth + .04, .20)
    m.box(role, u, -depth + .04, z + .98, w, .05, .05)
    for e in (-1, 1):
        m.box(role, u + e * (w / 2 - .02), -depth / 2 + .02, z + .98, .05, depth - .04, .05)
    m.box(role, u, -depth + .04, z + .50, w, .03, .03)
    n = max(4, int(w / .30))
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


# ---- building ----

def quad(name, p0, p1, p2, p3, t, role, module):
    """Thin plate from four world points (top surface), thickness t straight down."""
    vs = [p0, p1, p2, p3] + [(x, y, z - t) for x, y, z in (p0, p1, p2, p3)]
    return C.mesh(name, vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], role, module)


def tri(name, p0, p1, p2, t, role, module):
    vs = [p0, p1, p2] + [(x, y, z - t) for x, y, z in (p0, p1, p2)]
    return C.mesh(name, vs, [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], role, module)


def outer_faces():
    return [C.Face((0, -S / 2, 0), (1, 0, 0), (0, 1, 0), 'south'), C.Face((S / 2, 0, 0), (0, 1, 0), (-1, 0, 0), 'east'),
            C.Face((0, S / 2, 0), (-1, 0, 0), (0, -1, 0), 'north'), C.Face((-S / 2, 0, 0), (0, -1, 0), (1, 0, 0), 'west')]


def aisle_wall(f, lo, hi, colour_offset=0):
    """Dado wall, cast-iron columns, iron-framed glazing to the aisle eave, coloured awning per bay."""
    nb = max(1, round((hi - lo) / BAY)); pitch = (hi - lo) / nb
    f.wall(f'{f.label} dado {lo:.0f}', lo, hi - EPS, G0, DADO, depth=T, role='tile', holes=())
    m = Merge(f)
    m.box('tile_dark', (lo + hi) / 2, -.03, G0 + .22, hi - lo - 2 * EPS, T + .10, .44)   # darker base course
    m.box('stone', (lo + hi) / 2, -.05, G0 + .05, hi - lo - 2 * EPS, T + .14, .10)       # plinth
    m.box('stone', (lo + hi) / 2, -.04, DADO + .08, hi - lo - 2 * EPS, T + .12, .16)      # dado cope
    G.brick_courses(f, lo + .02, hi - .02, G0 + .7, DADO - .1, (), spacing=.30)
    m.box('hardware', (lo + hi) / 2, T / 2, EAVE_A - .10, hi - lo - 2 * EPS, .28, .34)   # eaves beam
    for i in range(nb + 1):
        u = lo + pitch * i
        uu = min(max(u, lo + .22), hi - .22)
        a = f.p(uu, T / 2, DADO + .16); b = f.p(uu, T / 2, EAVE_A - .26)
        C.rod(f'{f.label} column', a, b, .17, 'hardware', 'columns', 10)
        C.rod(f'{f.label} column base', f.p(uu, T / 2, DADO + .14), f.p(uu, T / 2, DADO + .46), .24, 'hardware', 'columns', 10)
        C.rod(f'{f.label} column capital', f.p(uu, T / 2, EAVE_A - .62), f.p(uu, T / 2, EAVE_A - .26), .24, 'hardware', 'columns', 10)
        for sgn in (-1, 1):   # brackets
            if (sgn < 0 and i == 0) or (sgn > 0 and i == nb):
                continue
            C.beam('Column bracket', f.p(uu, T / 2, EAVE_A - 1.6), f.p(uu + sgn * 1.1, T / 2, EAVE_A - .32), .08, .08, 'hardware', 'columns')
    for i in range(nb):
        c = lo + pitch * (i + .5)
        w = pitch - .50
        # glazing panel between columns: glass sheet with an iron frame and a transom
        m.box('glass', c, T / 2, (DADO + .22 + EAVE_A - .34) / 2, w - .10, .012, EAVE_A - .34 - DADO - .22)
        m.box('hardware', c, T / 2, DADO + .22, w, .07, .08)
        m.box('hardware', c, T / 2, EAVE_A - .40, w, .07, .08)
        m.box('hardware', c, T / 2, DADO + 2.6, w, .06, .07)
        for k in range(1, 3):
            m.box('hardware', c - w / 2 + w * k / 3, T / 2, (DADO + .22 + EAVE_A - .34) / 2, .06, .06, EAVE_A - .34 - DADO - .22)
        # semicircular iron fanlight bars at the head (decorative arch within the bay)
        rr = w / 2 - .04
        for j in range(6):
            a0, a1 = math.pi * j / 6, math.pi * (j + 1) / 6
            C.beam('Bay arch', f.p(c + math.cos(a0) * rr, T / 2, EAVE_A - .44 - rr + math.sin(a0) * rr), f.p(c + math.cos(a1) * rr, T / 2, EAVE_A - .44 - rr + math.sin(a1) * rr), .06, .06, 'hardware', 'columns')
        C.OPENINGS.append(dict(id=f'{f.label} glazed bay {lo:.0f}-{i}', face=f.label, u=c, z=DADO + .22, width=w, height=EAVE_A - .34 - DADO - .22, kind='iron framed glazing above the dado', clear_wall_cut=False,
            carrier_depth_m=T, frame_inset_m=T / 2, pane_inset_m=T / 2, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='market hall'))
        # awning: sloped canvas on two arms, scalloped valance
        role = ('awning_red', 'awning_yellow', 'awning_blue')[(i + colour_offset) % 3]
        out = 1.9
        lower = [f.p(c - w / 2, -out, 0)[:2], f.p(c + w / 2, -out, 0)[:2]]
        upper = [f.p(c - w / 2, -.02, 0)[:2], f.p(c + w / 2, -.02, 0)[:2]]
        strip(f'{f.label} awning {i}', lower, upper, DADO + 2.30, DADO + 3.05, role, 'awnings', closed=False)
        m.box(role, c, -out + .02, DADO + 2.12, w, .04, .30)
        for k in range(int(w / .5) + 1):
            m.box(role, c - w / 2 + w * k / int(w / .5), -out + .02, DADO + 1.94, .26, .04, .10)
        m.box('hardware', c, -out + .05, DADO + 2.32, w + .04, .05, .05)
        for sgn in (-1, 1):
            C.beam('Awning arm', f.p(c + sgn * (w / 2 - .2), .0, DADO + 3.05), f.p(c + sgn * (w / 2 - .2), -out + .08, DADO + 2.32), .05, .05, 'hardware', 'awnings')
    m.flush('aisle wall')


def gable_end(f, main=False):
    """Gable end: stone piers, a semicircular iron archivolt set inside the gable with a stained-glass tympanum mosaic,
    a coat-of-arms shield in the gable field, lattice spandrels, scrolled cresting on both rakes and a tall apex finial."""
    half = HW
    R_ = 7.0
    zc = EAVE_W - 2.3                  # arch springing
    apex = RIDGE + .55
    for sgn in (-1, 1):
        u = sgn * (half - .70)
        f.part(f'{f.label} gable pier', u, T / 2 + .1, (G0 + EAVE_W + .2) / 2, 1.40, 1.60, EAVE_W + .2 - G0, 'stone', 'gable piers', 0)
        f.part(f'{f.label} gable pier cap', u, T / 2 + .1, EAVE_W + .35, 1.70, 1.90, .30, 'stone', 'gable piers', 0)
        f.part(f'{f.label} gable pier base', u, T / 2 + .1, G0 + .35, 1.70, 1.90, .70, 'stone', 'gable piers', 0)
        f.part(f'{f.label} gable pier panel', u, T / 2 - .72, (DADO + 1.0 + EAVE_W - 1.6) / 2, .90, .06, EAVE_W - 2.6 - DADO, 'tile', 'gable piers', 0)
    # Glass screen: rectangle below the springing plus the semicircle; the entrance cut out of it.
    pts = [(-R_, DADO + .1), (R_, DADO + .1), (R_, zc)]
    for k in range(1, 16):
        a = math.pi * k / 16
        pts.append((R_ * math.cos(a), zc + R_ * math.sin(a)))
    pts.append((-R_, zc))
    screen = f.panel(f'{f.label} arch screen', pts, T / 2 - .006, T / 2 + .006, 'glass', 'gable screen')
    f.cut(screen, f'{f.label} entrance cut', 0.0, G0, 5.2, 5.4, depth=.4)
    m = Merge(f)
    # Stained-glass tympanum: dense radial mosaic of coloured panes (12 sectors x 3 rings) with a central rose, as
    # opaque colour panels on both sides of the screen so the colour reads from inside and outside (v001 P1 3).
    cols = ('stain_green', 'stain_gold', 'stain_blue', 'stain_red')
    rings = ((2.2, 3.9), (4.0, 5.6), (5.7, R_ - .25))
    for ri, (r0, r1) in enumerate(rings):
        nsec = 12 if ri else 8
        for k in range(nsec):
            a0, a1 = math.pi * k / nsec, math.pi * (k + 1) / nsec
            am = (a0 + a1) / 2; rm = (r0 + r1) / 2
            w_ = (a1 - a0) * rm - .10; h_ = r1 - r0 - .10
            role = cols[(k + ri) % 4] if main else ('stain_blue' if (k + ri) % 3 == 0 else 'glass')
            if role == 'glass':
                continue
            for dd in (T / 2 - .022, T / 2 + .022):
                # a pane as a thin box centred on the sector, rotated by placing it through a local face
                g = C.Face(f.p(math.cos(am) * rm, dd, zc + math.sin(am) * rm), (f.t * math.cos(am) + C.Vector((0, 0, 1)) * math.sin(am)), f.n, 'pane')
                g.part('Tympanum pane', 0.0, 0.0, 0.0, h_, .012, w_, role, 'gable screen', 0)
    for dd in (T / 2 - .03, T / 2 + .03):
        C.rod('Tympanum rose', f.p(0.0, dd, zc + 1.2), f.p(0.0, dd + (.012 if dd > T / 2 else -.012), zc + 1.2), 1.15, 'stain_gold' if main else 'stain_blue', 'gable screen', 16)
        C.rod('Tympanum rose heart', f.p(0.0, dd, zc + 1.2), f.p(0.0, dd + (.02 if dd > T / 2 else -.02), zc + 1.2), .55, 'stain_red', 'gable screen', 12)
    for k in range(13):
        a = math.pi * k / 12
        C.beam('Tympanum radial', f.p(math.cos(a) * 1.3, T / 2 - .06, zc + math.sin(a) * 1.3), f.p(math.cos(a) * (R_ - .22), T / 2 - .06, zc + math.sin(a) * (R_ - .22)), .07, .07, 'hardware', 'gable screen')
    for rr in (2.15, 3.95, 5.65):
        for k in range(16):
            a0, a1 = math.pi * k / 16, math.pi * (k + 1) / 16
            C.beam('Tympanum ring', f.p(math.cos(a0) * rr, T / 2 - .06, zc + math.sin(a0) * rr), f.p(math.cos(a1) * rr, T / 2 - .06, zc + math.sin(a1) * rr), .06, .06, 'hardware', 'gable screen')
    for u in (-5.2, -2.7, 2.7, 5.2):
        m.box('hardware', u, T / 2 - .05, (DADO + .1 + zc) / 2, .09, .09, zc - DADO - .1)
    for z in (DADO + .1, 5.6, zc - .05):
        m.box('hardware', 0.0, T / 2 - .05, z, 2 * R_, .09, .09)
    for sgn in (-1, 1):
        m.box('hardware', sgn * 2.65, T / 2 - .06, (G0 + 5.4) / 2, .16, .16, 5.4 - G0)
    m.box('hardware', 0.0, T / 2 - .06, 5.48, 5.5, .16, .16)
    # Archivolt inside the gable: thick iron ring with gilt rosettes.
    for k in range(16):
        a0, a1 = math.pi * k / 16, math.pi * (k + 1) / 16
        pa = f.p(math.cos(a0) * (R_ + .32), T / 2 - .25, zc + math.sin(a0) * (R_ + .32)); pb = f.p(math.cos(a1) * (R_ + .32), T / 2 - .25, zc + math.sin(a1) * (R_ + .32))
        C.beam('Archivolt', pa, pb, .62, .52, 'hardware', 'great arch')
        am = (a0 + a1) / 2
        C.rod('Archivolt rosette', f.p(math.cos(am) * (R_ + .32), T / 2 - .52, zc + math.sin(am) * (R_ + .32)), f.p(math.cos(am) * (R_ + .32), T / 2 - .60, zc + math.sin(am) * (R_ + .32)), .20, 'gilt', 'great arch', 8)
    # Gable field above the arch: a closed iron lattice panel (glass backed) between the archivolt and the rakes.
    field = [(-(half + .50), EAVE_W - .30), (half + .50, EAVE_W - .30), (0.0, apex - .05)]
    f.panel(f'{f.label} gable field', field, T / 2 - .004, T / 2 + .004, 'glass', 'gable screen')
    for k in range(1, 8):
        u = k * 1.15
        for sgn in (-1, 1):
            z_top = apex - .05 - (apex - .05 - EAVE_W + .30) * (u / (half + .50)) - .20
            z_bot = (zc + (max(R_ ** 2 - u ** 2, 0.0)) ** .5 + .75) if u < R_ else EAVE_W - .2
            if z_top > z_bot + .3:
                m.box('hardware', sgn * u, T / 2 - .10, (z_top + z_bot) / 2, .08, .08, z_top - z_bot)
    for z in (EAVE_W + 1.4, EAVE_W + 3.4, EAVE_W + 5.2):
        wz = 2 * (half + .50) * (apex - .05 - z) / (apex - .05 - EAVE_W + .30) - .4
        if wz > 1.0:
            m.box('hardware', 0.0, T / 2 - .10, z, wz, .08, .08)
    # Coat-of-arms shield in the gable field above the archivolt (v001 P1 4).
    sz = zc + R_ + 1.15
    shield = [(-.9, sz + 1.0), (.9, sz + 1.0), (.9, sz - .1), (0.0, sz - .9), (-.9, sz - .1)]
    f.panel('Shield', shield, T / 2 - .36, T / 2 - .12, 'stain_gold', 'crest')
    for i in range(4):
        f.part('Shield pale', -.675 + .45 * i, T / 2 - .38, sz + .05, .12, .04, 1.9 - .3, 'stain_red' if i % 2 == 0 else 'stain_gold', 'crest', 0)
    f.part('Shield crown', 0.0, T / 2 - .36, sz + 1.25, 1.2, .24, .35, 'gilt', 'crest', 0)
    # Rakes: bargeboards with continuous scrolled cresting and a tall apex finial (v001 P1 4).
    for sgn in (-1, 1):
        C.beam('Bargeboard', f.p(sgn * (half + .60), T / 2 - .25, EAVE_W - .45), f.p(0.0, T / 2 - .25, apex), .26, .40, 'hardware', 'great arch')
        C.beam('Bargeboard lower', f.p(sgn * (half + .60), T / 2 - .25, EAVE_W - .85), f.p(0.0, T / 2 - .25, apex - .40), .14, .14, 'hardware', 'great arch')
        C.beam('Cresting rail', f.p(sgn * (half + .40), T / 2 - .25, EAVE_W - .05), f.p(.40 * sgn, T / 2 - .25, apex + .40), .05, .05, 'hardware', 'crest')
        n = 9
        for k in range(n + 1):
            t = k / n
            u = sgn * ((half + .40) * (1 - t) + .40 * t)
            z = (EAVE_W - .45) * (1 - t) + apex * t
            C.rod('Cresting spike', f.p(u, T / 2 - .25, z + .1), f.p(u, T / 2 - .25, z + .75), .03, 'hardware', 'crest', 6)
            if k < n:
                u2 = sgn * ((half + .40) * (1 - (t + .5 / n)) + .40 * (t + .5 / n)); z2 = (EAVE_W - .45) * (1 - (t + .5 / n)) + apex * (t + .5 / n)
                C.rod('Cresting scroll', f.p(u2, T / 2 - .25, z2 + .15), f.p(u2, T / 2 - .25, z2 + .42), .12, 'hardware', 'crest', 8)
    for k in range(8):
        a = math.tau * k / 8
        C.beam('Finial star', f.p(0.0, T / 2 - .25, apex + 1.5), f.p(math.cos(a) * .9, T / 2 - .25, apex + 1.5 + math.sin(a) * .9), .05, .05, 'hardware', 'crest')
    for k in range(12):
        a0, a1 = math.tau * k / 12, math.tau * (k + 1) / 12
        C.beam('Finial ring', f.p(math.cos(a0) * .9, T / 2 - .25, apex + 1.5 + math.sin(a0) * .9), f.p(math.cos(a1) * .9, T / 2 - .25, apex + 1.5 + math.sin(a1) * .9), .06, .06, 'hardware', 'crest')
    C.rod('Crest finial', f.p(0.0, T / 2 - .25, apex), f.p(0.0, T / 2 - .25, apex + 3.3), .07, 'hardware', 'crest', 6)
    C.rod('Crest ball', f.p(0.0, T / 2 - .25, apex + 2.6), f.p(0.0, T / 2 - .25, apex + 2.95), .20, 'gilt', 'crest', 8)
    m.flush('gable screen')
    C.OPENINGS.append(dict(id=f'{f.label} entrance', face=f.label, u=0.0, z=G0, width=5.2, height=5.4, kind='open entrance', clear_wall_cut=True, carrier_depth_m=.012, frame_inset_m=None, pane_inset_m=None,
        face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='market hall'))
    C.OPENINGS.append(dict(id=f'{f.label} arch screen', face=f.label, u=0.0, z=DADO + .1, width=2 * R_, height=zc + R_ - DADO - .1, kind='glazed iron arch screen', clear_wall_cut=False, carrier_depth_m=.012, frame_inset_m=0.0, pane_inset_m=0.0,
        face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='market hall'))


def roof_plate_with_strips(name, pts_section, axis, lo, hi, strips, t=.18):
    """Pitched roof plate as a prism along one axis with glazed strips cut through it (plan-aligned cutters) and glass
    plates in the cuts, so light passes into the hall (v001 P1 5, P1 9)."""
    plate = C.prism(name, pts_section, axis, lo, hi, 'roof', 'wing roofs')
    for (a0, a1, g0, g1, za, zb) in strips:
        if axis == 'y':
            C.cut_box(plate, name + ' strip cut', ((a0 + a1) / 2, (g0 + g1) / 2, (za + zb) / 2), (abs(a1 - a0), abs(g1 - g0), 6.0))
            quad(name + ' glass', (a0, g0, za), (a1, g0, zb), (a1, g1, zb), (a0, g1, za), .05, 'glass', 'wing roofs')
        else:
            C.cut_box(plate, name + ' strip cut', ((g0 + g1) / 2, (a0 + a1) / 2, (za + zb) / 2), (abs(g1 - g0), abs(a1 - a0), 6.0))
            quad(name + ' glass', (g0, a0, za), (g0, a1, zb), (g1, a1, zb), (g1, a0, za), .05, 'glass', 'wing roofs')
    return plate


PANES = {}
PANE_COLS = ('stain_teal', 'stain_aqua', 'stain_teal', 'stain_amber', 'stain_aqua', 'glass', 'stain_teal')


def leaded_grid(a, b, c, n, seed):
    """Small leaded panes over triangle a-b-c: an n-step triangular grid, each pane shrunk toward its centre so the
    dark leading plate beneath shows between them, lifted clear of the plate."""
    def P(i, j):
        return tuple(a[k] + (b[k] - a[k]) * j / n + (c[k] - a[k]) * i / n for k in range(3))
    cells = []
    for i in range(n):
        for j in range(n - i):
            cells.append((P(i, j), P(i, j + 1), P(i + 1, j)))
            if j < n - i - 1:
                cells.append((P(i, j + 1), P(i + 1, j + 1), P(i + 1, j)))
    for q, (p0, p1, p2) in enumerate(cells):
        role = PANE_COLS[(q * 3 + seed) % len(PANE_COLS)]
        cen = tuple((p0[k] + p1[k] + p2[k]) / 3 for k in range(3))
        pts = [tuple(cen[k] + (p[k] - cen[k]) * .80 for k in range(3)) for p in (p0, p1, p2)]
        vs, fs = PANES.setdefault(role, ([], []))
        o = len(vs)
        vs += [(x, y, z + .05) for x, y, z in pts] + [(x, y, z + .03) for x, y, z in pts]
        fs += [(o, o + 1, o + 2), (o + 5, o + 4, o + 3), (o, o + 3, o + 4, o + 1), (o + 1, o + 4, o + 5, o + 2), (o + 2, o + 5, o + 3, o)]


def wing_roofs():
    """Two full-length gabled wings crossing under the lantern (no open valleys, v001 P0 2); glazed strips cut through the
    plates; clerestory louvre walls over the quadrant roofs; ridge monitors beside the lantern; quadrant roofs with glazed
    strips and closed double-pitch gablets; glazed lantern drum and steep glazed pyramid."""
    t = .18
    slope = (RIDGE - EAVE_W) / HW
    for axis in ('y', 'x'):
        lo, hi = -(S / 2 + .60), S / 2 + .60
        e = EAVE_W - .5 * slope
        pts = [(-(HW + .5), e), (0.0, RIDGE), (HW + .5, e), (HW + .5, e - t), (0.0, RIDGE - t), (-(HW + .5), e - t)]
        # Opaque standing-seam wing roofs, glazed only at the ridge monitors (locked top, v003 P2 5); the crossing under
        # the lantern is cut open so the lantern clerestory is seen from the hall (v003 P1 1).
        plate = roof_plate_with_strips(f'Wing roof {axis}', pts, axis, lo, hi, [])
        C.cut_box(plate, f'Wing roof {axis} crossing cut', (0.0, 0.0, (RIDGE + EAVE_W) / 2), (2 * LANT - .10, 2 * LANT - .10, 12.0))
        for q in range(1, 9):                    # standing seams
            for side in (-1, 1):
                a_ = side * HW * q / 9
                zq = RIDGE - abs(a_) * slope + .04
                for (g0, g1) in ((lo + .3, -LANT - .05), (LANT + .05, hi - .3)):
                    if axis == 'y':
                        C.beam('Standing seam', (a_, g0, zq), (a_, g1, zq), .04, .05, 'hardware', 'wing roofs')
                    else:
                        C.beam('Standing seam', (g0, a_, zq), (g1, a_, zq), .04, .05, 'hardware', 'wing roofs')
        for side in (1,):
            for (g0, g1) in ((lo, -LANT - .1), (LANT + .1, hi)):      # stops at the open crossing
                if axis == 'y':
                    C.beam('Ridge cap', (0.0, g0, RIDGE + .06), (0.0, g1, RIDGE + .06), .30, .12, 'hardware', 'wing roofs')
                else:
                    C.beam('Ridge cap', (g0, 0.0, RIDGE + .06), (g1, 0.0, RIDGE + .06), .30, .12, 'hardware', 'wing roofs')
        # Ridge monitors beside the lantern: raised glazed boxes 3.2 m wide and 1.4 m tall on the ridge (locked oblique).
        for sgn in (-1, 1):
            c0, c1 = sgn * (LANT + 1.8), sgn * (LANT + 9.0)
            zb = RIDGE - 1.6 * slope
            for side in (-1, 1):
                if axis == 'y':
                    f = C.Face((side * 1.6, (c0 + c1) / 2, 0), (0, 1, 0), (-side, 0, 0), f'monitor {axis}{sgn}{side}')
                else:
                    f = C.Face(((c0 + c1) / 2, side * 1.6, 0), (1, 0, 0), (0, -side, 0), f'monitor {axis}{sgn}{side}')
                L = abs(c1 - c0)
                f.panel(f'{f.label} glazing', [(-L / 2, zb - .3), (L / 2, zb - .3), (L / 2, zb + 1.4), (-L / 2, zb + 1.4)], -.006, .006, 'glass', 'monitors')
                mm = Merge(f)
                mm.box('hardware', 0.0, 0.0, zb + 1.46, L, .16, .16)
                for i in range(int(L / 1.2) + 1):
                    mm.box('hardware', -L / 2 + L * i / int(L / 1.2), 0.0, zb + .55, .10, .10, 1.7)
                mm.flush('monitors')
            if axis == 'y':
                vs = [(-1.9, c0, zb + 1.5), (1.9, c0, zb + 1.5), (1.9, c1, zb + 1.5), (-1.9, c1, zb + 1.5)]
                ends = ((0.0, c0), (0.0, c1))
            else:
                vs = [(c0, -1.9, zb + 1.5), (c0, 1.9, zb + 1.5), (c1, 1.9, zb + 1.5), (c1, -1.9, zb + 1.5)]
                ends = ((c0, 0.0), (c1, 0.0))
            for (p0, p1) in ((vs[0], vs[1]), (vs[1], vs[2]), (vs[2], vs[3]), (vs[3], vs[0])):
                pass
            # low glazed gable roof of the monitor: two plates to a ridge 1 m above the eaves
            if axis == 'y':
                for side in (-1, 1):
                    quad(f'Monitor roof {axis}{sgn}{side}', (0.0, c0, zb + 2.5), (0.0, c1, zb + 2.5), (side * 1.95, c1, zb + 1.45), (side * 1.95, c0, zb + 1.45), .08, 'glass', 'monitors')
                for cc, dirn in ((c0, -1.0 if c0 < c1 else 1.0), (c1, 1.0 if c0 < c1 else -1.0)):   # closed gable ends as panels with real thickness
                    gf = C.Face((0.0, cc + dirn * .02, 0), (1, 0, 0), (0, -dirn, 0), 'monitor end')
                    gf.panel(f'Monitor gable {axis}{sgn}', [(-1.95, zb - .3), (1.95, zb - .3), (1.95, zb + 1.45), (0.0, zb + 2.52), (-1.95, zb + 1.45)], -.08, .04, 'hardware', 'monitors')
            else:
                for side in (-1, 1):
                    quad(f'Monitor roof {axis}{sgn}{side}', (c0, 0.0, zb + 2.5), (c1, 0.0, zb + 2.5), (c1, side * 1.95, zb + 1.45), (c0, side * 1.95, zb + 1.45), .08, 'glass', 'monitors')
                for cc, dirn in ((c0, -1.0 if c0 < c1 else 1.0), (c1, 1.0 if c0 < c1 else -1.0)):
                    gf = C.Face((cc + dirn * .02, 0.0, 0), (0, 1, 0), (-dirn, 0, 0), 'monitor end')
                    gf.panel(f'Monitor gable {axis}{sgn}', [(-1.95, zb - .3), (1.95, zb - .3), (1.95, zb + 1.45), (0.0, zb + 2.52), (-1.95, zb + 1.45)], -.08, .04, 'hardware', 'monitors')
    # Clerestory louvre walls of the wings over the quadrant roofs.
    k_slope = 0.0      # quadrant pyramids meet the wing walls at the aisle eave (v002 P1 F3)
    for axis in ('y', 'x'):
        for sgn in (-1, 1):
            for side in (-1, 1):
                u0, u1 = sgn * HW, sgn * (S / 2 - 1.4)
                pts = []
                for u in (u0, u1):
                    z_q = EAVE_A + .4
                    pts.append((u, z_q - .35))
                pts.append((u1, EAVE_W + .30)); pts.append((u0, EAVE_W + .30))
                if axis == 'y':
                    f = C.Face((side * HW, 0, 0), (0, 1, 0), (-side, 0, 0), f'clerestory y{sgn}{side}')
                else:
                    f = C.Face((0, side * HW, 0), (1, 0, 0), (0, -side, 0), f'clerestory x{sgn}{side}')
                f.panel(f'{f.label} glazing', pts, -.006, .006, 'glass', 'clerestory')
                m = Merge(f)
                m.box('hardware', (u0 + u1) / 2, 0.0, EAVE_W + .18, abs(u1 - u0), .22, .28)
                n = max(1, round(abs(u1 - u0) / BAY))
                for i in range(n + 1):
                    u = u0 + (u1 - u0) * i / n
                    z_q = EAVE_A + .4
                    m.box('hardware', u, 0.0, (z_q - .35 + EAVE_W + .04) / 2, .12, .12, EAVE_W + .04 - z_q + .35)
                for j in range(6):           # louvre blades
                    zl = EAVE_W - .3 - j * .5
                    seg = [u for u in (u0 + (u1 - u0) * k / 24 for k in range(25)) if EAVE_A + .2 < zl]
                    if len(seg) > 1:
                        m.box('hardware', (seg[0] + seg[-1]) / 2, -.03, zl, abs(seg[-1] - seg[0]), .05, .09)
                m.flush('clerestory')
                C.OPENINGS.append(dict(id=f'{f.label} glazing', face=f.label, u=(u0 + u1) / 2, z=EAVE_A, width=abs(u1 - u0), height=EAVE_W - EAVE_A, kind='clerestory glazing', clear_wall_cut=False,
                    carrier_depth_m=.012, frame_inset_m=0.0, pane_inset_m=0.0, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='market hall'))
    # Quadrant roofs: steep glazed pyramids with stained-glass panes on iron hips (locked oblique and top, v002 P1 F3).
    PANES.clear()
    for sx in (-1, 1):
        for sy in (-1, 1):
            x0, x1 = sorted((sx * (HW + .02), sx * (S / 2 + .6)))
            y0, y1 = sorted((sy * (HW + .02), sy * (S / 2 + .6)))
            qc = ((x0 + x1) / 2, (y0 + y1) / 2, EAVE_A + 5.0)
            base = [(x0, y0, EAVE_A - .05), (x1, y0, EAVE_A - .05), (x1, y1, EAVE_A - .05), (x0, y1, EAVE_A - .05)]
            for j, (p0, p1) in enumerate(zip(base, base[1:] + base[:1])):
                # Outer zone opaque metal; inner zone a grid of small leaded panes in muted teal, aqua and amber on a
                # dark iron leading plate (locked top and oblique, v003 P1 3).
                pa_ = tuple(p0[i] + (qc[i] - p0[i]) * .38 for i in range(3)); pb_ = tuple(p1[i] + (qc[i] - p1[i]) * .38 for i in range(3))
                quad(f'Quadrant metal {sx}{sy}{j}', p0, p1, pb_, pa_, .05, 'roof', 'quadrant roofs')
                tri(f'Quadrant leading {sx}{sy}{j}', pa_, pb_, qc, .05, 'hardware', 'quadrant roofs')
                leaded_grid(pa_, pb_, qc, 6, (j + (sx > 0) + 2 * (sy > 0)) % 5)
                C.beam('Quadrant hip', p0, qc, .16, .16, 'hardware', 'quadrant roofs')
                C.beam('Quadrant eave', p0, p1, .22, .18, 'hardware', 'quadrant roofs')
                for fr in (.35, .65):
                    C.beam('Quadrant purlin', tuple(p0[i] + (qc[i] - p0[i]) * fr for i in range(3)), tuple(p1[i] + (qc[i] - p1[i]) * fr for i in range(3)), .07, .07, 'hardware', 'quadrant roofs')
            C.rod('Quadrant finial', qc, (qc[0], qc[1], qc[2] + 1.4), .06, 'hardware', 'quadrant roofs', 6)
            C.rod('Quadrant finial ball', (qc[0], qc[1], qc[2] + 1.0), (qc[0], qc[1], qc[2] + 1.25), .16, 'gilt', 'quadrant roofs', 8)
            for k in range(1, 3):
                for along in ('x', 'y'):
                    d = HW + k * 4.6 + .2
                    if along == 'x':
                        cx, cy = sx * d, sy * (S / 2 + .3)
                        f = C.Face((cx, cy, 0), (sx * 1.0, 0, 0), (0, -sy, 0), f'gablet {sx}{sy}{k}x')
                    else:
                        cx, cy = sx * (S / 2 + .3), sy * d
                        f = C.Face((cx, cy, 0), (0, sy * 1.0, 0), (-sx, 0, 0), f'gablet {sx}{sy}{k}y')
                    gablet(f, EAVE_A - .3, k_slope)
    for role, (vs, fs) in PANES.items():
        C.mesh(f'Quadrant panes {role}', vs, fs, role, 'quadrant roofs')
    # Lantern: clerestory glazed only above the wing-roof profiles it stands on, with a sill along those profiles and
    # posts and transoms carried down to it (v003 P1 2); opaque metal pyramid with iron hips and a finial (v003 P2 4).
    L = LANT
    slope = (RIDGE - EAVE_W) / HW
    lf = A.faces(2 * L, 2 * L, 0, 0, 'lantern ')
    def prof(u):
        return RIDGE - abs(u) * slope
    for f in lf:
        for sgn in (-1, 1):
            f.panel(f'{f.label} glazing {sgn}', [(0.0, LANT_TOP - .3), (sgn * L, LANT_TOP - .3), (sgn * L, prof(L) - .10), (0.0, RIDGE - .10)][::(1 if sgn < 0 else -1)], -.006, .006, 'glass', 'lantern')
            C.beam('Lantern sill', f.p(0.0, -.10, RIDGE + .02), f.p(sgn * (L + .15), -.10, prof(L + .15) + .02), .34, .26, 'hardware', 'lantern')
        m = Merge(f)
        for i in range(7):
            u = -L + 2 * L * i / 6
            z0_ = prof(u) - .05
            m.box('hardware', u, 0.0, (z0_ + LANT_TOP - .3) / 2, .16, .16, LANT_TOP - .3 - z0_)
        m.box('hardware', 0.0, 0.0, LANT_TOP - .34, 2 * L + .3, .26, .30)
        for zt_ in [LANT_TOP - 1.2 - j * .55 for j in range(4)] + [RIDGE - 1.0, RIDGE - 2.4, RIDGE - 3.8]:
            ua = max(0.05, (RIDGE - zt_) / slope)
            for sgn in (-1, 1):
                lo_, hi_ = sorted((sgn * ua, sgn * (L - .15)))
                if hi_ - lo_ > .3:
                    m.box('hardware', (lo_ + hi_) / 2, -.02, zt_, hi_ - lo_, .05, .09)
        m.flush('lantern')
    C.OPENINGS.append(dict(id='lantern glazing', face='lantern', u=0.0, z=RIDGE, width=2 * L, height=LANT_TOP - .3 - RIDGE, kind='lantern glazing', clear_wall_cut=False, carrier_depth_m=.012, frame_inset_m=0.0, pane_inset_m=0.0,
        face_origin=[0, -L, 0], face_tangent=[1, 0, 0], face_inward=[0, 1, 0], occupied_space='market hall'))
    o = L + .5
    apex = (0.0, 0.0, LANT_APEX)
    for (p0, p1) in (((-o, -o), (o, -o)), ((o, -o), (o, o)), ((o, o), (-o, o)), ((-o, o), (-o, -o))):
        tri('Lantern pyramid metal', (p0[0], p0[1], LANT_TOP - .2), (p1[0], p1[1], LANT_TOP - .2), apex, .06, 'roof', 'lantern')
        C.beam('Lantern hip', (p0[0], p0[1], LANT_TOP - .2), apex, .16, .16, 'hardware', 'lantern')
        for fr in (.33, .66):
            C.beam('Lantern purlin', (p0[0] * (1 - fr), p0[1] * (1 - fr), LANT_TOP - .2 + (LANT_APEX - LANT_TOP + .2) * fr), (p1[0] * (1 - fr), p1[1] * (1 - fr), LANT_TOP - .2 + (LANT_APEX - LANT_TOP + .2) * fr), .07, .07, 'hardware', 'lantern')
        C.beam('Lantern eave', (p0[0], p0[1], LANT_TOP - .2), (p1[0], p1[1], LANT_TOP - .2), .20, .16, 'hardware', 'lantern')
    C.rod('Lantern finial', (0, 0, LANT_APEX - .3), (0, 0, LANT_APEX + 2.4), .08, 'hardware', 'lantern', 6)
    C.rod('Lantern ball', (0, 0, LANT_APEX + 1.7), (0, 0, LANT_APEX + 2.1), .24, 'gilt', 'lantern', 8)
    C.CONTACTS.append(dict(name='Two full-length gabled wings crossing under the lantern; lantern drum rising out of the crossing; clerestory walls on interior columns over the quadrant roofs; monitors on the ridges', ridge_m=RIDGE, lantern_top_m=LANT_TOP))


def gablet(f, zb, k_slope):
    """Closed double-pitch gablet on the quadrant eave: lattice front with glass, two mirrored slate plates meeting at
    a ridge that descends into the quadrant slope, cheeks closed (v001 P1 7)."""
    f.panel(f'{f.label} front', [(-1.6, zb), (1.6, zb), (1.6, zb + 1.1), (0.0, zb + 2.3), (-1.6, zb + 1.1)], -.02, .12, 'hardware', 'gablets')
    f.panel(f'{f.label} glass', [(-1.2, zb + .2), (1.2, zb + .2), (1.2, zb + 1.0), (0.0, zb + 1.95), (-1.2, zb + 1.0)], -.035, -.025, 'glass', 'gablets')
    d_back = 2.4
    z_back = zb + .3 + d_back / 4.4      # quadrant slope is about 13 degrees: run per rise 4.4
    for sgn in (-1, 1):
        a = f.p(0.0, -.08, zb + 2.42); bq = f.p(0.0, d_back, z_back + .9)
        c_ = f.p(sgn * 1.78, -.08, zb + 1.02); d_ = f.p(sgn * 1.78, d_back, z_back - .5)
        vs = [a, bq, d_, c_]
        vs += [(x, y, z - .10) for x, y, z in vs]
        C.mesh(f'{f.label} slate', vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 'roof', 'gablets')
        C.beam('Gablet barge', a, c_, .10, .16, 'hardware', 'gablets')
        uu = sgn * 1.52
        pts = [(.0, zb - .2), (.0, zb + 1.05), (d_back - .3, z_back - .45), (d_back - .3, zb - .2)]
        vs2 = [f.p(uu - .05, d, z) for d, z in pts] + [f.p(uu + .05, d, z) for d, z in pts]
        C.mesh(f'{f.label} cheek', vs2, [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], 'hardware', 'gablets')


def interior():
    outline = [(-S / 2, -S / 2), (S / 2, -S / 2), (S / 2, S / 2), (-S / 2, S / 2)]
    C.prism('Hall slab', outline, 'z', 0.0, G0, 'foundation', 'foundation')
    # Interior cast-iron columns on the wing lines carry the clerestory walls; arched iron trusses across each wing.
    for axis in ('y', 'x'):
        for sgn in (-1, 1):
            for side in (-1, 1):
                n = 3
                for i in range(n + 1):
                    u = sgn * (HW + (S / 2 - 1.4 - HW) * i / n)
                    x, y = (side * HW, u) if axis == 'y' else (u, side * HW)
                    C.rod('Hall column', (x, y, G0), (x, y, EAVE_W - .3), .20, 'hardware', 'hall columns', 10)
                    C.rod('Hall column capital', (x, y, EAVE_W - .8), (x, y, EAVE_W - .3), .30, 'hardware', 'hall columns', 10)
            slope = (RIDGE - EAVE_W) / HW
            for i in range(0, 4):
                u = sgn * (HW + 1.0 + (S / 2 - 2.6 - HW) * i / 3)
                P = lambda a_, z_: (a_, u, z_) if axis == 'y' else (u, a_, z_)
                for s_ in (-1, 1):
                    C.beam('Hall truss rafter', P(s_ * (HW - .3), EAVE_W - .5 + .3 * slope - .35), P(0.0, RIDGE - .55), .14, .26, 'hardware', 'trusses')
                C.beam('Hall truss tie', P(-(HW - .3), EAVE_W - .45), P(HW - .3, EAVE_W - .45), .12, .16, 'hardware', 'trusses')
                arc = [(-math.cos(math.pi * k / 10) * (HW - .3), EAVE_W - 1.0 + math.sin(math.pi * k / 10) * 1.2) for k in range(11)]
                for (a_, za), (b_, zb) in zip(arc, arc[1:]):
                    C.beam('Hall truss arch', P(a_, za), P(b_, zb), .10, .18, 'hardware', 'trusses')
                C.beam('Hall truss king post', P(0.0, EAVE_W - .45), P(0.0, RIDGE - .6), .12, .12, 'hardware', 'trusses')
                for s_ in (-1, 1):
                    C.beam('Hall truss strut', P(s_ * (HW - .3) * .5, EAVE_W - .45), P(s_ * (HW - .3) * .25, RIDGE - .55 - (HW - .3) * .25 * slope), .10, .10, 'hardware', 'trusses')
                    C.beam('Hall truss post', P(s_ * (HW - .3), EAVE_W - 1.0), P(s_ * (HW - .3), EAVE_W - .3), .14, .14, 'hardware', 'trusses')
    # Stalls: timber counters with produce boxes along the four aisles and around the lantern.
    for (x, y, w, d) in ((-5.5, -14.0, 3.2, 8.0), (5.5, -14.0, 3.2, 8.0), (-5.5, 14.0, 3.2, 8.0), (5.5, 14.0, 3.2, 8.0),
                         (-14.0, -5.5, 8.0, 3.2), (-14.0, 5.5, 8.0, 3.2), (14.0, -5.5, 8.0, 3.2), (14.0, 5.5, 8.0, 3.2),
                         (-15.0, -15.0, 6.0, 3.0), (15.0, -15.0, 6.0, 3.0), (-15.0, 15.0, 6.0, 3.0), (15.0, 15.0, 6.0, 3.0)):
        C.box('Stall counter', (x, y, G0 + .45), (w, d, .90), 'timber', 'stalls', 0)
        C.box('Stall produce', (x, y, G0 + 1.05), (w - .3, d - .3, .30), 'produce', 'stalls', 0)
        C.box('Stall canopy', (x, y, G0 + 2.9), (w + .4, d + .4, .08), 'awning_red' if (x + y) > 0 else 'awning_yellow', 'stalls', 0)
        for sx in (-1, 1):
            for sy in (-1, 1):
                C.rod('Stall post', (x + sx * (w / 2 - .1), y + sy * (d / 2 - .1), G0 + .9), (x + sx * (w / 2 - .1), y + sy * (d / 2 - .1), G0 + 2.86), .03, 'hardware', 'stalls', 6)
    C.qa_room_light('Hall south', (0.0, -12.0, 8.0), 160, 8.0); C.qa_room_light('Hall north', (0.0, 12.0, 8.0), 120, 8.0)
    C.qa_room_light('Hall east', (12.0, 0.0, 8.0), 120, 8.0); C.qa_room_light('Hall west', (-12.0, 0.0, 8.0), 120, 8.0)
    C.qa_room_light('Lantern', (0.0, 0.0, 17.5), 220, 10.0)          # softer: the v003 lantern light blew out the corners
    for (lx, ly) in ((0.0, -16.0), (0.0, 16.0), (-16.0, 0.0), (16.0, 0.0)):
        C.qa_room_light(f'Wing roof {lx:.0f}{ly:.0f}', (lx, ly, EAVE_W + 1.0), 380, 9.0)
    C.qa_room_light('Hall entrance', (0.0, -18.0, 6.0), 160, 8.0)


def plaza():
    ext = PLAZA
    C.box('Plaza paving', (0, 0, .0075), (S + 2 * ext, S + 2 * ext, .015), 'foundation', 'plaza', 0)
    for u in range(-5, 6):
        for (bx, by) in ((u * 4.2, -S / 2 - 7.0), (u * 4.2, S / 2 + 7.0), (-S / 2 - 7.0, u * 4.2), (S / 2 + 7.0, u * 4.2)):
            C.rod('Bollard', (bx, by, .015), (bx, by, .9), .08, 'hardware', 'plaza', 6)
    for x, y in ((-S / 2 - 8.0, -14.0), (-S / 2 - 8.0, 2.0), (-S / 2 - 8.0, 18.0), (S / 2 + 8.0, -14.0), (S / 2 + 8.0, 2.0), (S / 2 + 8.0, 18.0), (-20.0, S / 2 + 9.0), (-6.0, S / 2 + 9.0), (8.0, S / 2 + 9.0)):
        street_tree(x, y, .015, height=9.0, spread=2.4)
    for sgn in (-1, 1):
        C.rod('Lamp post', (sgn * 16.0, -S / 2 - 9.0, .015), (sgn * 16.0, -S / 2 - 9.0, 6.0), .08, 'hardware', 'plaza', 8)
        C.rod('Lamp head', (sgn * 16.0, -S / 2 - 9.0, 6.0), (sgn * 16.0, -S / 2 - 9.0, 6.5), .25, 'pale', 'plaza', 8)


def build():
    plaza()
    interior()
    faces = outer_faces()
    for i, f in enumerate(faces):
        span = S
        lo, hi = (-span / 2, span / 2 - EPS) if i % 2 == 0 else (-span / 2 + T, span / 2 - T)
        aisle_wall(f, lo, -HW - 1.4, colour_offset=i)
        aisle_wall(f, HW + 1.4, hi, colour_offset=i + 1)
        gable_end(f, main=(i == 0))
    wing_roofs()


LIGHT_RIG = dict(key=(-46, -54, 50), fill=(50, -28, 36), rear=(-20, 54, 44), target=(0, 0, 8.0), gain=7.5)
