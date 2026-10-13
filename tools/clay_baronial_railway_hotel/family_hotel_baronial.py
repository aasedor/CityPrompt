"""Scottish Baronial railway hotel, authored from the locked catalogue views of
chateauesque_grand_railway_hotel / variant_0 (scottish_baronial_granite_tower).

Read from the pixels: a six-storey pink-grey granite quadrangle around an open court, streets south and
west. A square entrance tower a quarter of the way along the south face with a pointed-arch porte-cochere
through to the court, a crenellated parapet and round tourelles with conical caps at its front corners;
round corner tourelles corbelled out above the first storey with conical slate roofs; crow-stepped wall
gables rising through the eaves; steep slate roofs with dormers and chimney stacks; sash windows with
stone surrounds in rusticated granite; an iron fence on a low wall with lawn strips and trees.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G
from contract import subtract_openings

SLUG = 'clay-baronial-railway-hotel'
W, D = 58.0, 50.0                 # quadrangle footprint
WING = 14.0                       # wing depth; court 30 x 22 m
T = .40
G0 = .15
LEVELS = [5.0, 9.2, 13.4]         # tall ground floor plus three upper floors below the wall head; the attic storey is in the gables and dormers (locked front, v002 P0 3)
EAVE = 17.6
RIDGE = 27.8                      # steep slate roofs, about 55 degrees
TX, TW, TD, TOUT = -11.6, 10.0, 11.6, 1.6     # entrance tower about a third along the south face from the west (locked front and oblique, v002 P1), width, depth, projection
PORCH_D, PORCH_W, PORCH_H = 2.4, 7.6, 9.6     # projecting crenellated entrance porch with corner bartizans (v002 P1)
TOWER_TOP = 30.4
PASS_W = 7.4                      # passage carrier width on the court face (arch 5 m between 1.2 m piers)
BAY = 3.8                         # tall narrow sash bays (v002 P1)
EPS = .002
SITE = (-W / 2 - 12.0, W / 2 + 8.0, -D / 2 - 14.0, D / 2 + 8.0)
PALETTE = dict(wall=(.63, .45, .39), joint=(.32, .23, .20), trim=(.20, .18, .16),
    pale=(.76, .72, .66), stone=(.70, .60, .53), roof=(.13, .15, .19), sand=(.70, .64, .52),
    foundation=(.46, .46, .45), glass=(.44, .50, .52), hardware=(.12, .12, .12),
    interior=(.80, .76, .68), floor=(.46, .44, .42), timber=(.36, .26, .16), blue=(.14, .22, .28),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.64, .62, .58), lead=(.42, .44, .46),
    rustic=(.56, .44, .39))


def manifest(version):
    h = TOWER_TOP + 6.0
    cams = G.camera_roster(W + 16.0, D + 16.0, h, [
        ('facade_close', (-24.0, -46.0, 6.0), (TX + 2.0, -D / 2, 9.0), 45),
        ('architecture_close', (-54.0, -52.0, 20.0), (-W / 2 + 4.0, -D / 2 + 4.0, 16.0), 50),
        ('glass_close', (2.0, -36.0, 6.5), (6.0, -D / 2, 7.5), 50),
        ('entrance_tower', (-22.0, -62.0, 26.0), (TX, -D / 2, 25.0), 45),
        ('porte_cochere', (TX - 9.0, -44.0, 2.0), (TX, -D / 2 - TOUT - PORCH_D, 4.5), 40),
        ('corner_tourelle', (-50.0, -50.0, 24.0), (-W / 2, -D / 2, 24.0), 45),
        ('crow_gables', (8.0, -46.0, 17.0), (-1.0, -D / 2, 21.0), 45),
        ('roof_court', (-60.0, -66.0, 56.0), (0.0, 0.0, 22.0), 45),
        ('interior', (14.0, -D / 2 + 9.0, LEVELS[0] + 1.6), (14.0, -D / 2 + .5, LEVELS[0] + 1.4), 50),
        ('rear_court', (2.0, 6.0, 2.5), (TX, -D / 2 + WING, 6.5), 40)])
    for c in cams:
        if c['name'] == 'front':          # eye level from the south-west on the street, tower at the left (locked front)
            c['location'] = (-22.0, -80.0, 1.7); c['target'] = (2.0, -D / 2, 10.0); c['lens'] = 26; c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='chateauesque_grand_railway_hotel/variant_0 (scottish_baronial_granite_tower)',
        measurement_contract=dict(dimensions_m=dict(width=SITE[1] - SITE[0], depth=SITE[3] - SITE[2], height=h),
            observed_storeys=5, storey_programme='tall ground floor of public rooms, three guest-room storeys, attic storey in the wall gables and dormers (five levels, as the locked front reads; the catalogue text says six storeys)',
            plan='58 x 50 m quadrangle (top view) of 14 m wings around a 30 x 22 m paved court with four corner trees, streets south and west; entrance tower 10 m square a third along the south face from the west corner, projecting 1.6 m with a 2.4 m crenellated porch',
            facade='bays at 3.8 m: tall ground-floor windows 1.5 x 3.3 m and tall sash windows 1.3 x 2.9 m with stone surrounds in rusticated granite with recessed joints; string courses at each floor; corbelled wall head at 17.6 m; crow-stepped wall gables about three bays wide rising to near the ridge, with two windows and an attic light',
            levels_m=[G0] + LEVELS, eave_m=EAVE, ridge_m=RIDGE,
            tower='entrance tower to 30.4 m on a corbel table with a crenellated parapet and corbelled round bartizans at the front corners, a stair tourelle with a conical cap at the rear corner, and a projecting two-storey crenellated porch with corner bartizans carrying the pointed-arch porte-cochere 4.6 x 6.6 m through the south wing to the court',
            tourelles='round corner tourelles 4.8 m across corbelled out above the ground floor at 5.6 m with cut windows and conical slate roofs to 28.1 m at the four outer corners; intermediate tourelles 3.2 m across corbelled out at 7 m on the west, east and north faces (locked top)',
            roof='steep slate hipped ring roof 17.6 to 27.8 m with gabled dormers between the wall gables, chimney stacks on the ridge',
            inferred='north and east faces repeat the grammar with tourelles and gables; court faces carry one central gable each; interiors are teaching assumptions'),
        roof_contract=dict(type='slate hipped ring roof with wall gables and dormers; flat tower roof behind crenellations; conical tourelle roofs', datum_m=EAVE, crowns_m=[RIDGE, TOWER_TOP, TOWER_TOP + 7.0]),
        identity_contract=dict(owner='crenellated entrance tower with the porte-cochere and tourelles, conical corner tourelles, crow-stepped gables, steep slate roofs, rusticated granite with sash windows, iron fence and lawn'),
        material_contract=dict(profile='source-palette clay: pink-grey granite with recessed rustication, pale stone dressings, dark slate, lead flashings, dark sash frames, black iron', textured_keeper=False),
        programme_contract=dict(storeys=7, ground='reception, lounges and dining through the porte-cochere', upper='guest rooms off double-loaded corridors', roof='attic rooms in the dormers'),
        contact_contract=['Grade-zero slab and sidewalks', 'Tower on the south wing; tourelles on corbel cones from the first-storey wall', 'Wall gables continuing the carriers through the eaves; gable roofs into the main slopes', 'Dormers seated on the slopes', 'Chimneys on the ridge'],
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

def cone(name, cx, cy, z0, r0, z1, r1, role, module, segs=24):
    vs = [(cx + r0 * math.cos(math.tau * i / segs), cy + r0 * math.sin(math.tau * i / segs), z0) for i in range(segs)]
    vs += [(cx + max(r1, .001) * math.cos(math.tau * i / segs), cy + max(r1, .001) * math.sin(math.tau * i / segs), z1) for i in range(segs)]
    fs = [tuple(range(segs - 1, -1, -1)), tuple(range(segs, 2 * segs))] + [(i, (i + 1) % segs, (i + 1) % segs + segs, i + segs) for i in range(segs)]
    return C.mesh(name, vs, fs, role, module)


def pointed_fill(f, u, z_top, w, rise, role='stone', d0=-.03, d1=None):
    d1 = T + .02 if d1 is None else d1
    pts = [(-w / 2, z_top), (w / 2, z_top), (w / 2, z_top - rise)]
    for k in range(1, 8):
        x = w / 2 - w * k / 8
        pts.append((x, z_top - rise + ((w ** 2 - (abs(x) + w / 2) ** 2) ** .5) * rise / (w * .866)))
    pts.append((-w / 2, z_top - rise))
    f.panel('Pointed arch spandrel', [(u + a, b) for a, b in pts], d0, d1, role, 'arches')


def rustication(f, lo, hi, z0, z1, holes, spacing=1.0, joint=.04, clip=None):
    """Recessed granite coursing: joint grooves as dark strips sunk into the carrier face (v001 P1 11), batched."""
    vs, fs = [], []
    for row in range(int((z1 - z0) / spacing)):
        z = z0 + row * spacing
        rlo, rhi = (lo, hi) if clip is None else clip(z + joint, lo, hi)
        if rhi - rlo < .2:
            continue
        for a, b in subtract_openings(rlo, rhi, z, z + joint, holes):
            o = len(vs)
            vs.extend([f.p(a, -.004, z), f.p(b, -.004, z), f.p(b, -.004, z + joint), f.p(a, -.004, z + joint), f.p(a, .05, z), f.p(b, .05, z), f.p(b, .05, z + joint), f.p(a, .05, z + joint)])
            fs.extend([(o, o + 1, o + 2, o + 3), (o + 7, o + 6, o + 5, o + 4), (o, o + 4, o + 5, o + 1), (o + 1, o + 5, o + 6, o + 2), (o + 2, o + 6, o + 7, o + 3), (o + 3, o + 7, o + 4, o)])
    if fs:
        C.mesh(f.label + ' rustication joints', vs, fs, 'joint', 'rustication')


def window_dressing(m, h, street):
    for sgn in (-1, 1):
        m.box('stone', h['u'] + sgn * (h['w'] / 2 + .10), -.03, h['z'] + h['h'] / 2, .20, T + .12, h['h'] + .20)
    m.box('stone', h['u'], -.05, h['z'] + h['h'] + .15, h['w'] + .50, T + .16, .22)
    m.box('stone', h['u'], -.07, h['z'] - .08, h['w'] + .36, T + .20, .12)


def elevation(f, lo, hi, street=True, gables=(), skip_bays=(), pad=0.0):
    """One face: rusticated granite carrier, tall ground-floor windows, sash windows with stone dressings, string
    courses, corbelled eaves course; optional two-bay wall gables centred on bay boundaries given in `gables`."""
    span = hi - lo
    nb = max(1, round(span / BAY))
    pitch = span / nb
    holes = []
    for i in range(nb):
        if i in skip_bays:
            continue
        c = lo + pitch * (i + .5)
        holes.append(hole(f'{f.label} ground window {i}', c, 1.0, 1.5, 3.3, level=-1))
        for k, zl in enumerate(LEVELS):
            holes.append(hole(f'{f.label} window {i}-{k}', c, zl + .75, 1.3, 2.9, level=k))
    f.wall(f'{f.label} carrier', lo, hi - EPS, G0, EAVE + .30, depth=T, role='wall', holes=holes)
    if street:
        rustication(f, lo + .02, hi - .02, G0 + .35, EAVE - .5, holes)
    else:
        G.brick_courses(f, lo + .02, hi - .02, G0 + .3, EAVE - .4, holes, spacing=2.2)
    m = Merge(f)
    for h in holes:
        if street:
            reveal(m, f, h, .16, 'stone', jambs_only=True)
        framed(m, f, h, cols=2, rows=2, occupied='guest room' if h['level'] >= 0 else 'lounge', lite=not street)
        if street:
            window_dressing(m, h, street)
        else:
            m.box('stone', h['u'], -.05, h['z'] + h['h'] + .15, h['w'] + .50, T + .16, .22)
    for zl in LEVELS:
        m.box('stone', (lo + hi) / 2, -.04 - pad, zl - .12, span - 2 * EPS, T + .14 + pad, .18 + 2 * pad)
    m.box('stone', (lo + hi) / 2, -.07 - pad, G0 + .55, span - 2 * EPS, T + .20 + pad, .40 + 2 * pad)          # plinth course
    # Corbelled eaves course: continuous corbel table under a projecting stone cornice (v001 P1 12).
    m.box('stone', (lo + hi) / 2, -.20 - pad, EAVE - .16, span - 2 * EPS, T + .46 + pad, .32 + 2 * pad)
    nc = max(2, int(span / 2.0))
    for i in range(nc + 1):
        m.box('stone', lo + .3 + (span - .6) * i / nc, -.14, EAVE - .52, .34, T + .34, .40)
    m.flush('facade')
    for gc, gw in gables:
        crow_gable(f, gc, EAVE, holes, w=gw)
    return pitch


def crow_gable(f, u, z_e, holes, w=10.0, rise=1.0, run=.55):
    """Crow-stepped wall gable about three bays wide rising to near the ridge (v002 P1): the carrier plane continued
    through the wall head as a stepped stone-coped gable; windows placed only where the stepped outline clears them by
    0.4 m (v002 P0 2), each with a lit room plate behind it; a slate gable roof whose ridge descends into the main slope."""
    k = (WING / 2) / (RIDGE - EAVE)
    half = w / 2
    steps_r = []
    x, z = half, z_e + .40
    while x - run > .45:
        x -= run; z += rise
        steps_r.append((x, z))
    top = z
    # The gable is a stack of rectangular step slabs, not one concave panel: window cuts through the concave panel
    # lost its tower-side flank (v003 P1: straight rake, missing risers).
    slabs = [(half, z_e - .6, z_e + .40)]
    zz = z_e + .40
    for (x2, z2) in steps_r:
        slabs.append((x2, zz, z2)); zz = z2
    pieces = [f.panel(f'{f.label} crow gable {u:.0f} step {k}', [(u - xs, za), (u + xs, za), (u + xs, zb), (u - xs, zb)], -.05, T, 'wall', 'gables')
              for k, (xs, za, zb) in enumerate(slabs)]
    def half_at(z):
        for xs, za, zb in slabs:
            if z <= zb:
                return xs
        return 0.0
    # Windows fitted so every head mould clears the copes by 0.45 m and every dressing stays 0.35 m inside the
    # risers (v003 P1): three lights where they fit, else two, else one; an attic light above where it fits.
    zl_, hl_ = z_e + .9, 2.2
    lim = half_at(zl_ + hl_ + .37 + .45) - .35
    wins = []
    for ww, n in ((1.1, 3), (.95, 3), (1.1, 2), (.8, 2), (1.1, 1)):
        d = min(lim - ww / 2 - .25, 2.0)
        if n == 1 and d >= 0:
            wins = [(0.0, zl_, ww, hl_)]; break
        if n == 3 and d >= ww + .55:
            wins = [(-d, zl_, ww, hl_), (0.0, zl_, ww, hl_), (d, zl_, ww, hl_)]; break
        if n == 2 and 2 * d >= ww + .55:
            wins = [(-d, zl_, ww, hl_), (d, zl_, ww, hl_)]; break
    za_, ha_ = z_e + 4.7, 1.5
    if half_at(za_ + ha_ + .37 + .45) - .35 >= .45 + .25:
        wins.append((0.0, za_, .9, ha_))
    m = Merge(f)
    gh = []
    for (du, zw, ww, hw) in wins:
        uu = u + du
        for pc, (xs, za, zb) in zip(pieces, slabs):
            if za < zw + hw and zb > zw:
                f.cut(pc, f'{f.label} gable window cut {u:.0f}{du:+.1f} {za:.1f}', uu, zw, ww, hw, depth=T + .1)
        h = hole(f'{f.label} gable window {u:.0f}{du:+.1f} {zw:.1f}', uu, zw, ww, hw)
        gh.append(h)
        reveal(m, f, h, .16, 'stone'); framed(m, f, h, cols=2, rows=2, occupied='attic room')
        window_dressing(m, h, True)
        m.box('interior', uu, T + .40, zw + hw / 2, ww + .3, .06, hw + .3)      # lit attic room behind the glass
    def clip(z, lo_, hi_):
        xs = [half] + [xs_ for (xs_, zs_) in steps_r]
        zs = [z_e + .40] + [zs_ for (xs_, zs_) in steps_r]
        allowed = max([x_ for x_, z_ in zip(xs, zs) if z_ >= z + .05] or [0.0]) - .08
        return max(lo_, u - allowed), min(hi_, u + allowed)
    rustication(f, u - half + .02, u + half - .02, z_e + .3, top - .3, gh, clip=clip)
    tread_edges = [(half, z_e + .40)] + steps_r
    for sgn in (-1, 1):
        for (xa, za), (xb, zb) in zip(tread_edges, tread_edges[1:]):
            m.box('stone', u + sgn * ((xa + xb) / 2 + .03), -.10, za + .07, (xa - xb) + .14, T + .26, .16)
    m.box('stone', u, -.10, top + .07, 1.1, T + .26, .16)
    m.flush('gables')
    z_apex = top - .30
    d_ridge = (z_apex - z_e) * k - .05
    for sgn in (-1, 1):
        a = f.p(u, T - .02, z_apex); bq = f.p(u, d_ridge, z_e + d_ridge / k + .02)
        c_ = f.p(u + sgn * (half - .50), T - .02, z_e + .42); d_ = f.p(u + sgn * (half - .50), d_ridge, z_e + d_ridge / k - 1.6)
        vs = [a, bq, d_, c_]
        vs += [(x, y, z - .18) for x, y, z in vs]
        C.mesh('Gable slate', vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 'roof', 'gables')


def roof_dormer(f, u, z_e, rise, run, w=1.9):
    k = run / rise
    d0 = .70
    z_em = z_e + d0 / k
    z_top = z_em + 2.30
    zw, hw, ww = z_em + .45, 1.5, .9
    front = f.panel(f'{f.label} dormer front', [(u - w / 2, z_em - .5), (u + w / 2, z_em - .5), (u + w / 2, z_top), (u, z_top + .75), (u - w / 2, z_top)], d0 - .16, d0 + .10, 'stone', 'dormers')
    f.cut(front, f'{f.label} dormer window cut', u, zw, ww, hw, depth=.30)
    g = C.Face(f.p(0, d0 - .16, 0), f.t, f.n, f.label + ' dormer')
    mg = Merge(g)
    h = hole(f'{f.label} dormer window {u:.1f}', u, zw, ww, hw)
    framed(mg, g, h, cols=1, rows=2, inset=.10, occupied='attic room', kind='dormer window')
    mg.flush('dormers')
    d_back = d0 + 2.4
    for sgn in (-1, 1):
        uu = u + sgn * (w / 2 - .14)
        pts = [(d0 - .12, z_em - .5), (d0 - .12, z_top - .03), (d_back, z_top - .03), (d_back, z_e + d_back / k - .9)]
        vs = [f.p(uu - .06, d, z) for d, z in pts] + [f.p(uu + .06, d, z) for d, z in pts]
        fs = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        C.mesh('Dormer cheek', vs, fs, 'stone', 'dormers')
    z_apex = z_top + .80
    d_ridge = (z_apex - z_e) * k - .1
    for sgn in (-1, 1):
        a = f.p(u, d0 - .32, z_apex); b = f.p(u, d_ridge, z_e + d_ridge / k + .02)
        c_ = f.p(u + sgn * (w / 2 + .22), d0 - .32, z_top - .10); d_ = f.p(u + sgn * (w / 2 + .22), d_ridge, z_e + d_ridge / k - .8)
        vs = [a, b, d_, c_]
        vs += [(x, y, z - .16) for x, y, z in vs]
        C.mesh('Dormer slate', vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 'roof', 'dormers')


def tourelle(cx, cy, r, base, top, cap_top, facing, windows=True, label='tourelle'):
    """Round corbelled tourelle: corbel cone, shaft with string courses and cut windows on the outward angles, conical
    slate roof and finial (v001 P0 5: windows are pockets cut into the shaft, framed and glazed inside)."""
    cone(f'{label} corbel', cx, cy, base - 2.2, .45, base, r, 'stone', 'tourelles', 22)
    shaft = C.rod(f'{label} shaft', (cx, cy, base), (cx, cy, top), r, 'wall', 'tourelles', 22)
    for zl in LEVELS:
        if zl > base + .5:
            C.rod(f'{label} string', (cx, cy, zl - .12), (cx, cy, zl + .06), r + .10, 'stone', 'tourelles', 22)
    if windows:
        for zl in [z for z in LEVELS if z > base + .5] + ([EAVE + .6] if top > EAVE + 3.4 else []):
            for da in (0.0,):
                a = facing + math.radians(da)
                ux, uy = math.cos(a), math.sin(a)
                g = C.Face((cx + ux * (r - .05), cy + uy * (r - .05), 0), (-uy, ux, 0), (-ux, -uy, 0), f'{label} window face')
                h = hole(f'{label} window {zl:.0f}{da:+.0f}', 0.0, zl + .9, 1.1, 2.0)
                g.cut(shaft, h['id'] + ' cut', 0.0, zl + .9, 1.1, 2.0, depth=.55)
                mg = Merge(g)
                framed(mg, g, h, cols=1, rows=2, inset=.16, occupied='tourelle room', lite=False)
                mg.box('stone', 0.0, -.03, zl + .9 + 2.0 + .14, 1.5, .20, .20)
                mg.box('stone', 0.0, -.04, zl + .9 - .08, 1.4, .22, .12)
                mg.flush('tourelles')
    C.rod(f'{label} eaves', (cx, cy, top), (cx, cy, top + .35), r + .25, 'stone', 'tourelles', 22)
    cone(f'{label} roof', cx, cy, top + .35, r + .30, cap_top, 0.0, 'roof', 'tourelles', 22)
    C.rod(f'{label} finial', (cx, cy, cap_top - .1), (cx, cy, cap_top + 1.0), .06, 'hardware', 'tourelles', 6)


def crenellation(ring, z, h=1.0, merlon=(.9, .7, 1.0), every=1.6, role='wall', module='parapet'):
    """Parapet wall along a closed polygon with merlons every `every` metres and one at each corner."""
    for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
        C.beam('Parapet wall', (ax, ay, z + h / 2), (bx, by, z + h / 2), .40, h, role, module)
        L = math.hypot(bx - ax, by - ay); n = max(1, int(L / every))
        for i in range(1, n):
            px, py = ax + (bx - ax) * i / n, ay + (by - ay) * i / n
            if i % 2 == 1:
                C.box('Merlon', (px, py, z + h + merlon[2] / 2), (merlon[0], merlon[0], merlon[2]), role, module, 0)
    for (px, py) in ring:
        C.box('Corner merlon', (px, py, z + h + merlon[2] / 2), (merlon[0] + .1, merlon[0] + .1, merlon[2] + .1), role, module, 0)


def corbel_table(ring, z, out=.30, every=.9):
    """Row of stone corbels carrying a parapet that oversails the wall by `out` (the ring is the wall line)."""
    for (ax, ay), (bx, by) in zip(ring, ring[1:] + ring[:1]):
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
        ox, oy = uy, -ux                   # outward for a counter-clockwise ring
        n = max(1, int(L / every))
        for i in range(n + 1):
            px, py = ax + ux * L * i / n + ox * out / 2, ay + uy * L * i / n + oy * out / 2
            C.box('Corbel', (px, py, z - .35), (.32 if abs(ox) < .5 else out + .02, out + .02 if abs(ox) < .5 else .32, .70), 'stone', 'parapet', 0)
        C.beam('Corbel table string', (ax + ox * out / 2, ay + oy * out / 2, z + .06), (bx + ox * out / 2, by + oy * out / 2, z + .06), out + .1, .12, 'stone', 'parapet')


def bartizan(cx, cy, r, z0, z1):
    """Round corbelled bartizan with a crenellated top."""
    cone('Bartizan corbel', cx, cy, z0 - 1.2, .25, z0, r, 'stone', 'tourelles', 20)
    C.rod('Bartizan shaft', (cx, cy, z0), (cx, cy, z1), r, 'wall', 'tourelles', 20)
    C.rod('Bartizan string', (cx, cy, z1 - .12), (cx, cy, z1 + .06), r + .12, 'stone', 'tourelles', 20)
    for k in range(6):
        a = math.tau * k / 6
        C.box('Bartizan merlon', (cx + math.cos(a) * (r - .15), cy + math.sin(a) * (r - .15), z1 + .45), (.42, .42, .8), 'wall', 'tourelles', 0)
    C.box('Bartizan slit', (cx, cy - r + .02, (z0 + z1) / 2), (.2, .1, 1.0), 'hardware', 'tourelles', 0)


def pointed_hood(f, u, z_spring, w, rise, d=-.08):
    """Hood moulding following a pointed arch: beams along the two arcs (v002 P1: no flat lintel)."""
    R = w * .866 / .866          # two-centre arch: each arc centred on the opposite springing
    pts = []
    for k in range(9):
        t = k / 8
        x = -w / 2 + (w / 2) * t
        zz = z_spring + ((w ** 2 - (abs(x) + w / 2) ** 2) ** .5) * rise / (w * .866)
        pts.append((x, zz))
    pts += [(-a, b) for a, b in reversed(pts[:-1])]
    for (xa, za), (xb, zb) in zip(pts, pts[1:]):
        C.beam('Arch hood', f.p(u + xa * 1.12, d, za + .25), f.p(u + xb * 1.12, d, zb + .25), .22, .20, 'stone', 'arches')


def pointed_fill16(f, u, z_top, w, rise, role='stone', d0=-.03, d1=None):
    d1 = T + .02 if d1 is None else d1
    pts = [(-w / 2, z_top), (w / 2, z_top), (w / 2, z_top - rise)]
    for k in range(1, 16):
        x = w / 2 - w * k / 16
        pts.append((x, z_top - rise + ((w ** 2 - (abs(x) + w / 2) ** 2) ** .5) * rise / (w * .866)))
    pts.append((-w / 2, z_top - rise))
    f.panel('Pointed arch spandrel', [(u + a, b) for a, b in pts], d0, d1, role, 'arches')


def tower():
    y0 = -D / 2 - TOUT
    x0, x1 = TX - TW / 2, TX + TW / 2
    yp = y0 - PORCH_D
    arch_w, arch_h, arch_r = 4.6, 6.6, 2.0
    # Tower front carrier: the passage arch at the foot (behind the porch) and windows above the porch.
    front = C.Face((TX, y0, 0), (1, 0, 0), (0, 1, 0), 'tower front')
    ta = hole('Tower passage arch', 0.0, G0, arch_w + .24, arch_h + .1, kind='open arch')   # reveal buried in the passage walls (v003 P0: coplanar reveal and wall face rendered a black slot)
    holes = [ta]
    for k, zl in enumerate(LEVELS):
        if zl + .75 > PORCH_H + 1.2:
            for du in (-1.6, 1.6):
                holes.append(hole(f'tower window {k}{du:+.0f}', du, zl + .75, 1.3, 2.9, level=k))
    holes.append(hole('tower upper window', 0.0, EAVE + 1.0, 2.0, 3.6, level=9))
    holes += [hole(f'tower top window {du:+.0f}', du, EAVE + 6.4, 1.0, 1.8, level=10) for du in (-1.8, 1.8)]
    front.wall('tower front carrier', -TW / 2, TW / 2, G0, TOWER_TOP - .20, depth=T, role='wall', holes=holes)
    rustication(front, -TW / 2 + .02, TW / 2 - .02, PORCH_H + .3, TOWER_TOP - 1.6, holes)
    pointed_fill16(front, 0.0, ta['z'] + ta['h'], ta['w'], arch_r, 'stone')
    m = Merge(front)
    for h in holes[1:]:
        reveal(m, front, h, .16, 'stone'); framed(m, front, h, cols=2, rows=2, occupied='tower rooms')
        window_dressing(m, h, True)
    for zl in LEVELS:
        if zl > PORCH_H:
            m.box('stone', 0.0, -.04, zl - .12, TW - 2 * EPS, T + .14, .18)
    m.box('stone', 0.0, -.12, PORCH_H + 2.6, 2.2, T + .26, 1.5)                 # armorial panel above the porch
    m.box('wall', 0.0, -.20, PORCH_H + 2.6, 1.5, T + .30, 1.0)
    m.flush('tower')
    C.OPENINGS.append(dict(id=ta['id'], face='tower front', u=0.0, z=ta['z'], width=ta['w'], height=ta['h'], kind='open arch', clear_wall_cut=True, carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None,
        face_origin=list(front.o), face_tangent=list(front.t), face_inward=list(front.n), occupied_space='porte-cochere passage'))
    # Tower side carriers start behind the front carrier so no two end faces coincide (v002 P0 1: coplanar end faces
    # rendered as a black slot), and a back carrier above the roof.
    for sgn, label in ((-1, 'tower west'), (1, 'tower east')):
        x = TX + sgn * TW / 2
        f = C.Face((x, y0 + TD / 2, 0), (0, sgn, 0), (-sgn, 0, 0), label)
        lo, hi = ((-TD / 2, TD / 2 - T) if sgn < 0 else (-TD / 2 + T, TD / 2))
        hs = [hole(f'{label} window {k}', 0.0, zl + .75, 1.3, 2.9) for k, zl in enumerate(LEVELS) if zl > 7.0] + [hole(f'{label} upper window', 0.0, EAVE + 1.0, 1.6, 3.6)]
        f.wall(f'{label} carrier', lo, hi, G0, TOWER_TOP - .20, depth=T, role='wall', holes=hs)
        rustication(f, lo + .02, hi - .02, G0 + .35, TOWER_TOP - 1.6, hs)
        mm = Merge(f)
        for h in hs:
            reveal(mm, f, h, .16, 'stone'); framed(mm, f, h, cols=2, rows=2, occupied='tower rooms')
            window_dressing(mm, h, True)
        mm.flush('tower')
    back = C.Face((TX, y0 + TD, 0), (-1, 0, 0), (0, -1, 0), 'tower back')
    bh = [hole('tower back window', 0.0, EAVE + 2.6, 1.6, 3.0)]
    back.wall('tower back carrier', -TW / 2 + T, TW / 2 - T, EAVE - 2.0, TOWER_TOP - .20, depth=T, role='wall', holes=bh)
    mb = Merge(back); framed(mb, back, bh[0], cols=2, rows=2, occupied='tower rooms', lite=True); mb.flush('tower')
    # Corbel table, oversailing crenellated parapet, corner bartizans, stair tourelle (v002 P1).
    zt = TOWER_TOP - .20
    ring = [(x0, y0), (x1, y0), (x1, y0 + TD), (x0, y0 + TD)]
    corbel_table(ring, zt, out=.30)
    over = [(x0 - .3, y0 - .3), (x1 + .3, y0 - .3), (x1 + .3, y0 + TD + .3), (x0 - .3, y0 + TD + .3)]
    crenellation(over, zt + .12, h=.9, merlon=(.9, .7, 1.0), every=1.5)
    C.box('Tower roof', (TX, y0 + TD / 2, zt - .12), (TW - .2, TD - .2, .24), 'lead', 'parapet', 0)
    C.rod('Flagpole', (TX, y0 + TD / 2, zt), (TX, y0 + TD / 2, zt + 5.0), .05, 'hardware', 'parapet', 8)
    for sgn in (-1, 1):
        bartizan(TX + sgn * (TW / 2 + .1), y0 - .1, 1.0, TOWER_TOP - 2.6, TOWER_TOP + 1.0)
    tourelle(x1 + .25, y0 + TD - 1.7, 1.7, RIDGE + .6, TOWER_TOP + 4.6, TOWER_TOP + 11.0, 0.0, windows=False, label='tower stair tourelle')   # rear-east stair tourelle corbelled out above the ridge, tall shaft and cone (v003 P1)
    for zz in (TOWER_TOP + 1.2, TOWER_TOP + 3.0):
        C.box('Stair tourelle slit', (x1 + .25 + 1.7 + .01, y0 + TD - 1.7, zz), (.08, .22, 1.0), 'hardware', 'tourelles', 0)
    # Projecting two-storey porch with the pointed porte-cochere, crenellated top and corner bartizans.
    pf = C.Face((TX, yp, 0), (1, 0, 0), (0, 1, 0), 'porch front')
    pa = hole('Porte-cochere', 0.0, G0, arch_w, arch_h, kind='open arch')
    pw_ = [hole('porch window', 0.0, PORCH_H - 2.0, 1.0, 1.4)]
    pf.wall('porch front carrier', -PORCH_W / 2, PORCH_W / 2, G0, PORCH_H, depth=T, role='wall', holes=[pa] + pw_)
    rustication(pf, -PORCH_W / 2 + .02, PORCH_W / 2 - .02, G0 + .35, PORCH_H - .4, [pa] + pw_)
    pointed_fill16(pf, 0.0, pa['z'] + pa['h'], pa['w'], arch_r, 'stone')
    pointed_hood(pf, 0.0, pa['z'] + pa['h'] - arch_r, pa['w'], arch_r)
    mp_ = Merge(pf)
    for sgn in (-1, 1):
        mp_.box('stone', sgn * (pa['w'] / 2 + .32), -.10, (G0 + pa['z'] + pa['h'] - arch_r) / 2, .50, T + .24, pa['z'] + pa['h'] - arch_r - G0)   # arch jamb piers
    framed(mp_, pf, pw_[0], cols=1, rows=2, occupied='porch room')
    mp_.flush('porch')
    for sgn in (-1, 1):
        side = C.Face((TX + sgn * PORCH_W / 2, yp + PORCH_D / 2, 0), (0, sgn, 0), (-sgn, 0, 0), f'porch side {sgn}')
        lo, hi = ((-PORCH_D / 2 - .05, PORCH_D / 2 - T) if sgn < 0 else (-PORCH_D / 2 + T, PORCH_D / 2 + .05))
        side.wall(f'porch side carrier {sgn}', lo, hi, G0, PORCH_H, depth=T, role='wall', holes=())
        rustication(side, lo + .02, hi - .02, G0 + .35, PORCH_H - .4, ())
    pring = [(TX - PORCH_W / 2, yp), (TX + PORCH_W / 2, yp), (TX + PORCH_W / 2, y0), (TX - PORCH_W / 2, y0)]
    corbel_table(pring[:2] + [(TX + PORCH_W / 2, y0 - .01), (TX - PORCH_W / 2, y0 - .01)], PORCH_H, out=.25)
    crenellation([(TX - PORCH_W / 2 - .25, yp - .25), (TX + PORCH_W / 2 + .25, yp - .25), (TX + PORCH_W / 2 + .25, y0 - .05), (TX - PORCH_W / 2 - .25, y0 - .05)], PORCH_H + .12, h=.7, merlon=(.7, .6, .8), every=1.2)
    C.box('Porch roof', (TX, (yp + y0) / 2, PORCH_H - .1), (PORCH_W - .2, PORCH_D - .1, .2), 'lead', 'porch', 0)
    for sgn in (-1, 1):
        bartizan(TX + sgn * (PORCH_W / 2 + .1), yp - .1, .75, PORCH_H - 2.2, PORCH_H + .8)
    C.OPENINGS.append(dict(id=pa['id'], face='porch front', u=0.0, z=pa['z'], width=pa['w'], height=pa['h'], kind='open arch', clear_wall_cut=True, carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None,
        face_origin=list(pf.o), face_tangent=list(pf.t), face_inward=list(pf.n), occupied_space='open porte-cochere passage to the court'))
    # Passage from the porch through the south wing: floor, walls, ceiling, court-side arch between two carriers.
    y1 = -D / 2 + WING
    C.box('Passage floor', (TX, (yp + y1) / 2, G0 / 2 + .001), (arch_w + .4, y1 - yp, G0), 'foundation', 'passage', 0)
    for sgn in (-1, 1):
        C.box('Passage wall', (TX + sgn * (arch_w / 2 + .26), (yp + T + y1 - T) / 2, (G0 + arch_h + .2) / 2), (.40, y1 - yp - 2 * T, arch_h + .2 - G0), 'wall', 'passage', 0)
    C.box('Passage ceiling', (TX, (yp + T + y1 - T) / 2, arch_h + G0 + .35), (arch_w + .8, y1 - yp - 2 * T, .30), 'stone', 'passage', 0)
    court_face = C.Face((TX, y1, 0), (-1, 0, 0), (0, -1, 0), 'passage court face')
    ca = hole('Court arch', 0.0, G0, arch_w, arch_h, kind='open arch')
    pw_holes = [hole(f'passage court window {k}', 0.0, zl + .75, 1.3, 2.9) for k, zl in enumerate(LEVELS) if zl > arch_h + .5]
    cw_half = W / 2 - WING
    p_hi = PASS_W / 2 - EPS if TX - PASS_W / 2 + cw_half > 2.5 else TX + cw_half - EPS      # u = TX - x: run to the court corner when no west run fits
    court_face.wall('Passage court carrier', -PASS_W / 2, p_hi, G0, EAVE + .30, depth=T, role='wall', holes=[ca] + pw_holes)
    pointed_fill16(court_face, 0.0, ca['z'] + ca['h'], ca['w'], arch_r, 'stone')
    pointed_hood(court_face, 0.0, ca['z'] + ca['h'] - arch_r, ca['w'], arch_r)
    mp = Merge(court_face)
    for h in pw_holes:
        framed(mp, court_face, h, cols=2, rows=2, occupied='guest room', lite=True)
        mp.box('stone', h['u'], -.05, h['z'] + h['h'] + .15, h['w'] + .50, T + .16, .22)
    pc, pwid = (-PASS_W / 2 + p_hi) / 2, p_hi + PASS_W / 2
    for zl in LEVELS:
        if zl > arch_h + .5:                       # no string course across the arch (v002 P1)
            mp.box('stone', pc, -.04, zl - .12, pwid - 2 * EPS, T + .14, .18)
    mp.box('stone', pc, -.20, EAVE - .16, pwid - 2 * EPS, T + .46, .32)
    mp.flush('passage')
    C.OPENINGS.append(dict(id=ca['id'], face='passage court face', u=0.0, z=ca['z'], width=ca['w'], height=ca['h'], kind='open arch', clear_wall_cut=True, carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None,
        face_origin=list(court_face.o), face_tangent=list(court_face.t), face_inward=list(court_face.n), occupied_space='open porte-cochere passage'))
    C.qa_room_light('Passage', (TX, (yp + y1) / 2, 5.5), 90, 4.0)
    C.CONTACTS.append(dict(name='Porch on the forecourt slab against the tower; tower on the south wing slab and carriers; bartizans on corbel cones; parapet on a corbel table; passage through the south wing between the two court carriers', tower_top_m=TOWER_TOP, porch_top_m=PORCH_H))


def roofs_and_floors():
    outer = [(-W / 2, -D / 2), (W / 2, -D / 2), (W / 2, D / 2), (-W / 2, D / 2)]
    ridge = [(-W / 2 + WING / 2, -D / 2 + WING / 2), (W / 2 - WING / 2, -D / 2 + WING / 2), (W / 2 - WING / 2, D / 2 - WING / 2), (-W / 2 + WING / 2, D / 2 - WING / 2)]
    court = [(-W / 2 + WING, -D / 2 + WING), (W / 2 - WING, -D / 2 + WING), (W / 2 - WING, D / 2 - WING), (-W / 2 + WING, D / 2 - WING)]
    C.prism('Ground slab', outer, 'z', 0.0, G0, 'foundation', 'foundation')
    C.prism('Court paving', [(x * .99, y * .99) for x, y in court], 'z', G0, G0 + .03, 'stone', 'court')
    for x, y in ((-11.0, -7.0), (11.0, -7.0), (11.0, 7.0), (-11.0, 7.0)):     # four corner trees (locked top, v001 P1 16)
        street_tree(x, y, G0 + .03, height=7.0, spread=1.8)
        C.box('Court planter', (x, y, G0 + .2), (2.4, 2.4, .34), 'stone', 'court', 0)
    ci = T + .02      # court-side floor edges stop inside the court walls (shared planes render black)
    wings = [((-W / 2 + T, -D / 2 + T), (W / 2 - T, -D / 2 + WING - ci)), ((-W / 2 + T, D / 2 - WING + ci), (W / 2 - T, D / 2 - T)),
             ((-W / 2 + T, -D / 2 + WING - ci - EPS), (-W / 2 + WING - ci, D / 2 - WING + ci + EPS)), ((W / 2 - WING + ci, -D / 2 + WING - ci - EPS), (W / 2 - T, D / 2 - WING + ci + EPS))]
    for zl in LEVELS + [EAVE]:
        for (x0, y0), (x1, y1) in wings:
            slab = C.prism(f'Floor {zl:.1f}', [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 'z', zl - .28, zl, 'floor', 'occupied floors')
            if y1 <= -D / 2 + WING + .01 and zl < 8.0:
                C.cut_box(slab, 'Passage cut', (TX, (y0 + y1) / 2, zl - .14), (5.6, WING + 2.0, 1.0))
    for zl in LEVELS[:3]:
        C.qa_room_light(f'South rooms {zl:.1f}', (14.0, -D / 2 + 5.0, zl + 2.6), 120, 5.0)
        C.qa_room_light(f'West rooms {zl:.1f}', (-W / 2 + 5.0, 4.0, zl + 2.6), 60, 5.0)
    C.qa_room_light('Lounge', (14.0, -D / 2 + 6.0, LEVELS[0] - .9), 120, 6.0)
    C.qa_room_light('Interior view room', (14.0, -D / 2 + 4.5, LEVELS[0] + 3.4), 220, 5.0)
    C.qa_room_light('Court south', (0.0, -5.0, 16.0), 900, 14.0); C.qa_room_light('Court north', (0.0, 5.0, 16.0), 700, 14.0)
    # Court faces: side walls run into the front and rear walls (closed corners, v001 P0 4); the south court face is
    # built in two runs either side of the passage carrier; one central gable per face.
    cw, cd = W - 2 * WING, D - 2 * WING
    cf = A.faces(cw, cd, 0, 0, 'court ')
    for i, f in enumerate(cf):
        f = C.Face(f.o, f.t, f.n * -1, f.label)
        span = cw if i % 2 == 0 else cd
        lo, hi = (-span / 2, span / 2 - EPS) if i % 2 == 0 else (-span / 2 - T + .02, span / 2 + T - .02)
        if i == 0:
            if TX - PASS_W / 2 - lo > 2.5:
                elevation(C.Face(f.o, f.t, f.n, 'court front west'), lo, TX - PASS_W / 2, street=False)
            elevation(C.Face(f.o, f.t, f.n, 'court front east'), TX + PASS_W / 2, hi, street=False)
            continue
        elevation(f, lo, hi, street=False, gables=((0.0, 9.0),), pad=.015 if i % 2 else 0.0)
    for (qx, qy) in court:                       # plug the inner eaves corners (v002 P1)
        C.box('Court corner eaves block', (qx * 1.004, qy * 1.004, EAVE - .1), (1.3, 1.3, .9), 'stone', 'roofs', 0)
    strip('Outer slate slopes', outer, ridge, EAVE, RIDGE, 'roof', 'roofs')
    strip('Court slate slopes', ridge, court, RIDGE, EAVE, 'roof', 'roofs')
    for (ax, ay), (bx, by) in zip(ridge, ridge[1:] + ridge[:1]):
        C.beam('Ridge lead', (ax, ay, RIDGE + .06), (bx, by, RIDGE + .06), .36, .14, 'lead', 'roofs')
    for x, y in ((-18.0, -D / 2 + WING / 2), (18.0, -D / 2 + WING / 2), (-W / 2 + WING / 2, 0.0), (W / 2 - WING / 2, 0.0), (-12.0, D / 2 - WING / 2), (12.0, D / 2 - WING / 2)):
        C.box('Chimney stack', (x, y, RIDGE + .9), (2.2, 1.1, 3.2), 'wall', 'chimneys', 0)
        C.box('Chimney cope', (x, y, RIDGE + 2.56), (2.5, 1.4, .16), 'stone', 'chimneys', 0)
        for dx in (-.6, 0.0, .6):
            C.rod('Chimney pot', (x + dx, y, RIDGE + 2.6), (x + dx, y, RIDGE + 3.3), .16, 'rustic', 'chimneys', 8)


def site():
    x0, x1, y0, y1 = SITE
    C.box('Street south', ((x0 + x1) / 2, y0 + 3.5, .004), (x1 - x0, 7.0, .008), 'concrete', 'street', 0)
    C.box('Street west', (x0 + 3.5, (y0 + 7.0 + y1) / 2, .004), (7.0, y1 - y0 - 7.0, .008), 'concrete', 'street', 0)
    C.box('Kerb south', ((x0 + 7.0 + x1) / 2, y0 + 7.06, .06), (x1 - x0 - 7.0, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb west', (x0 + 7.06, (y0 + 7.0 + y1) / 2, .06), (.12, y1 - y0 - 7.0, .12), 'stone', 'sidewalk', 0)
    C.box('South sidewalk', ((x0 + 7.0 + x1) / 2, (y0 + 7.0 + y0 + 10.0) / 2, .0075), (x1 - x0 - 7.0, 3.0, .015), 'foundation', 'sidewalk', 0)
    C.box('West sidewalk', ((x0 + 7.0 + x0 + 10.0) / 2, (y0 + 10.0 + y1) / 2, .0075), (3.0, y1 - y0 - 10.0, .015), 'foundation', 'sidewalk', 0)
    yf = y0 + 10.0
    xf = x0 + 10.0
    C.box('South lawn', ((-W / 2 + x1) / 2, (yf + (-D / 2 - TOUT)) / 2, .02), (x1 + W / 2, -D / 2 - TOUT - yf, .04), 'planting', 'lawn', 0)
    C.box('West lawn', ((xf + (-W / 2)) / 2, (yf + y1) / 2, .02), (-W / 2 - xf, y1 - yf, .04), 'planting', 'lawn', 0)
    C.box('East pavement', ((W / 2 + x1) / 2, (-D / 2 - TOUT + D / 2) / 2, .0075), (x1 - W / 2, D + TOUT, .015), 'foundation', 'sidewalk', 0)
    C.box('North pavement', ((xf + x1) / 2, (D / 2 + y1) / 2, .0075), (x1 - xf, y1 - D / 2, .015), 'foundation', 'sidewalk', 0)
    C.box('Entrance drive', (TX, (yf + (-D / 2 - TOUT - PORCH_D)) / 2, .05), (7.0, -D / 2 - TOUT - PORCH_D - yf + .2, .03), 'stone', 'lawn', 0)
    iron_fence((xf, yf), (TX - 4.0, yf), height=1.4, wall=.6, spacing=.55); iron_fence((TX + 4.0, yf), (x1 - 2.0, yf), height=1.4, wall=.6, spacing=.55)
    iron_fence((xf, y1 - 2.0), (xf, yf), height=1.4, wall=.6, spacing=.55)
    for sgn in (-1, 1):
        C.box('Gate pier', (TX + sgn * 4.2, yf, 1.1), (.8, .8, 2.2), 'stone', 'fence', 0); C.box('Gate pier cap', (TX + sgn * 4.2, yf, 2.28), (1.0, 1.0, .16), 'stone', 'fence', 0)
    for x in (-24.0, -2.0, 10.0, 22.0):
        street_tree(x, yf + 3.2, .02, height=8.0, spread=2.0)
    for y in (-12.0, 2.0, 14.0):
        street_tree(xf + 2.6, y, .02, height=8.0, spread=2.0)


def gable_layout(lo, hi, bays_list):
    """Gable centres and widths over runs of three bays: bays_list holds the first bay index of each gable."""
    nb = max(1, round((hi - lo) / BAY)); pitch = (hi - lo) / nb
    return tuple((lo + pitch * (i + 1.5), 3 * pitch - 1.4) for i in bays_list)


def build():
    site()
    roofs_and_floors()
    south = C.Face((0, -D / 2, 0), (1, 0, 0), (0, 1, 0), 'south')
    west = C.Face((-W / 2, 0, 0), (0, -1, 0), (1, 0, 0), 'west')
    north = C.Face((0, D / 2, 0), (-1, 0, 0), (0, -1, 0), 'north')
    east = C.Face((W / 2, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    sw = C.Face(south.o, south.t, south.n, 'south west run'); se = C.Face(south.o, south.t, south.n, 'south east run')
    sw_lo, sw_hi = -W / 2, TX - TW / 2 + .3
    se_lo, se_hi = TX + TW / 2 - .3, W / 2
    nse = max(1, round((se_hi - se_lo) / BAY))
    runs = [(sw, sw_lo, sw_hi, (((sw_lo + 3.4 + sw_hi) / 2, min(8.0, sw_hi - sw_lo - 4.6)),), ()),
            (se, se_lo, se_hi, gable_layout(se_lo, se_hi, (0, nse - 4)), ()),
            (west, -D / 2 + T, D / 2 - T, ((-16.15, 9.9), (16.15, 9.9)), (-9.0, 9.0)),
            (east, -D / 2 + T, D / 2 - T, ((-16.15, 9.9), (16.15, 9.9)), (-9.0, 9.0)),
            (north, -W / 2, W / 2, ((0.0, 10.0),), (-14.0, 14.0))]
    for f, lo, hi, gables, tours in runs:
        elevation(f, lo, hi, street=f.label != 'north', gables=gables)
    tower()
    for cx, cy, facing in ((-W / 2 + .9, -D / 2 + .9, math.radians(225)), (W / 2 - .9, -D / 2 + .9, math.radians(-45)), (W / 2 - .9, D / 2 - .9, math.radians(45)), (-W / 2 + .9, D / 2 - .9, math.radians(135))):
        tourelle(cx, cy, 2.4, LEVELS[0] + .6, EAVE + 4.0, EAVE + 10.5, facing, label='corner tourelle')
    for cx, cy, facing in ((-W / 2 + .2, -9.0, math.radians(180)), (-W / 2 + .2, 9.0, math.radians(180)), (W / 2 - .2, -9.0, 0.0), (W / 2 - .2, 9.0, 0.0), (-14.0, D / 2 - .2, math.radians(90)), (14.0, D / 2 - .2, math.radians(90))):
        tourelle(cx, cy, 1.6, LEVELS[0] + 2.0, EAVE + 3.0, EAVE + 8.0, facing, label='side tourelle')
    for f, lo, hi, gables, tours in runs:
        nb = max(1, round((hi - lo) / BAY)); pitch = (hi - lo) / nb
        for i in range(nb):
            u = lo + pitch * (i + .5)
            if i in (0, nb - 1) or i % 2 == 0:
                continue
            if any(abs(u - g) < gw / 2 + 1.0 for g, gw in gables) or any(abs(u - t_) < 2.6 for t_ in tours):
                continue
            roof_dormer(f, u, EAVE, RIDGE - EAVE, WING / 2)
    A.sofa(16.0, -D / 2 + 6.0, LEVELS[0]); A.desk(12.0, -D / 2 + 4.0, LEVELS[0] + .05)
    C.box('Lounge partition', (20.0, -D / 2 + 6.0, LEVELS[0] + 1.7), (.16, 10.0, 3.4), 'interior', 'partitions', 0)


LIGHT_RIG = dict(key=(-60, -70, 70), fill=(70, -36, 50), rear=(-26, 70, 60), target=(0, 0, 16.0), gain=11.0)
