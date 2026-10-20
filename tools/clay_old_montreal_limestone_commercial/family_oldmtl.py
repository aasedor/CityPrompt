"""Old Montreal limestone commercial block, authored from the locked catalogue views of
old_montreal_limestone_commercial / variant_0 (a domed public-market hall of the Bonsecours type).

Read from the pixels (the top view governs the plan): a long three-storey hall of grey limestone ashlar over a low
basement, in two offset ranges joined by a square domed block. The west range lines up with the dome block; the
east range is stepped south of it by a full range depth, so the plan reads as a long bar with a joggle at the dome
(top view). Regular bays of six-over-six windows on three floors with small barred basement vents, dressed
pilaster strips, a plinth, sill bands and a strong modillioned eave cornice; low hipped slate roofs with stone
chimneys, small vent dormers and a skylight. At the east end an end pavilion, flush with the range, carries round-arched
windows with radial fanlights on all three floors, iron balconettes on the first floor, a balustrade along its eaves
and a pediment on the east front, with a corniced door on the east face (front and oblique). On the south street a
tetrastyle Tuscan portico with a pediment stands in front of the west end of the east range, below the dome. Over
the dome block a square stone attic with corner pedestals carries a drum of round-arched windows between pilasters,
a ribbed silver tin dome and an open lantern with a cupola and cross. A flat-roofed arcaded porch on the north
front of the dome block (top view). Cobbled squares, sidewalks, streets and street trees round the hall.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-old-montreal-limestone-commercial'
WX0, WX1, WY0, WY1 = -52.0, -11.0, -10.5, 10.5        # west range (top view: in line with the dome block)
DX0, DX1 = -11.0, 11.0                                # dome block, the west range's depth
EX0, EX1, EY0, EY1 = -11.0, 55.0, -30.0, -10.5        # east range, stepped a full depth south (top view)
PX0, PP = 43.0, 0.0                                   # east end pavilion from PX0 to EX1, flush with the range (oblique)
QX0, QX1, QD = -8.6, 8.6, 4.6                         # south portico span and depth
NX0, NX1, ND = -7.5, 7.5, 3.6                         # north arcaded porch span and depth
X0, X1, Y0, Y1 = WX0, EX1, EY0 - QD, WY1 + ND
T = .7
G0, F1, F2, EAVE = .9, 6.0, 10.6, 15.0                # ground floor, first, second, eave (corona top)
RISE = 4.4                                            # hipped slate roofs: eave to ridge
ATT = 21.0                                            # top of the square attic over the dome block
DR, DRUM = 7.3, 6.8                                   # drum radius and height
DOME_R, DOME_H = 7.7, 7.6
DOME0 = ATT + DRUM + 1.0                              # dome springing, over the drum entablature
LANT = DOME0 + DOME_H - .5
TOP = LANT + 6.6
EPS = .002
PALETTE = dict(wall=(.58, .58, .56), joint=(.42, .42, .41), stone=(.70, .70, .67), arch=(.66, .66, .63),
    trim=(.86, .86, .83), frame=(.86, .86, .83), roof=(.19, .21, .24), metal=(.76, .78, .80), membrane=(.80, .81, .82),
    glass=(.15, .17, .19), hardware=(.06, .06, .07), timber=(.60, .62, .58), interior=(.80, .76, .68),
    floor=(.52, .44, .36), cobble=(.40, .39, .37), concrete=(.68, .67, .64), asphalt=(.27, .27, .28),
    planting=(.30, .44, .20), soil=(.22, .16, .10), pot=(.62, .62, .60), brick=(.58, .58, .56))


def manifest(version):
    h = TOP
    cams = G.camera_roster(X1 - X0 + 3.0, Y1 - Y0 + 3.0, h, [
        ('portico', (16.0, -60.0, 8.0), (0.0, -32.0, 9.0), 40),
        ('dome_drum', (34.0, -44.0, 40.0), (0.0, 0.0, ATT + 6.0), 45),
        ('end_pavilion_arches', (38.0, -50.0, 6.5), (49.0, EY0 - PP, 8.0), 40),
        ('balconettes', (45.0, -40.0, 9.0), (49.0, EY0 - PP, 8.4), 45),
        ('east_door', (74.0, -24.0, 3.0), (EX1, (EY0 + EY1) / 2, 4.5), 40),
        ('long_facade', (20.0, -56.0, 8.0), (20.0, EY0, 8.0), 40),
        ('roofs_dormers', (44.0, 30.0, 44.0), (20.0, -12.0, 17.0), 40),
        ('west_range', (-66.0, -48.0, 12.0), (-34.0, WY0, 9.0), 40),
        ('interior', (30.6, EY0 + 3.2, F1 + 1.7), (30.6, EY0, F1 + 2.0), 50),
        ('rear_north', (0.0, 74.0, 16.0), (0.0, WY1, 15.0), 45)])
    for c in cams:                       # the locked front and oblique look from the south-east
        if c['name'] == 'front':
            c.update(location=(65.0, -50.0, 1.6), target=(30.0, -27.0, 13.5), lens=22, whole=False)
        elif c['name'] == 'front_corner':
            c.update(location=(92.0, -84.0, 66.0), target=(8.0, -14.0, 12.0), lens=35, whole=False)   # the locked oblique: high over the south-east
        elif c['name'] == 'top':
            c.update(location=(2.0, -10.0, 160.0), target=(2.0, -9.999, 0.0), ortho_scale=136.0, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='old_montreal_limestone_commercial/variant_0 (domed limestone market hall)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=3, storey_programme='low basement and three storeys of market hall, shops and assembly rooms',
            plan='107 m long hall in two 21 and 19.5 m deep ranges offset by one range depth at a 22 m square dome block (top view); south portico 17 m wide, north arcaded porch',
            facade='grey limestone ashlar; three tiers of six-over-six windows with barred basement vents; pilaster strips, plinth, sill bands and a modillioned eave cornice; east end pavilion with round-arched windows, radial fanlights, iron balconettes, an eaves balustrade and a pediment',
            dome='square stone attic with corner pedestals, drum of sixteen round-arched windows between pilasters, ribbed silver tin dome, open lantern with cupola and cross',
            levels_m=[G0, F1, F2, EAVE], roof_m=dict(eave=EAVE, ridge=EAVE + RISE, attic=ATT, dome=DOME0 + DOME_H, top=TOP),
            inferred='interiors, the north and west fronts and the dome block east face follow the visible grammar; metric dimensions are authored teaching assumptions'),
        roof_contract=dict(type='low hipped slate roofs, gabled at the pediment and against the attic; flat tin deck over the attic; tin dome and lantern', datum_m=EAVE, crowns_m=[EAVE + RISE, ATT, TOP]),
        identity_contract=dict(owner='long grey limestone market hall with a pedimented Tuscan portico, a silver ribbed dome on an arcaded drum and an arched end pavilion with iron balconettes'),
        material_contract=dict(profile='source-palette clay: grey limestone ashlar with dark joints and paler dressings, blue-grey slate, silver tin dome, off-white sashes, black ironwork', textured_keeper=False),
        programme_contract=dict(storeys=3, basement='storage and plant', ground='market hall and shops', upper='assembly rooms and offices'),
        contact_contract=['Grade-zero sidewalks, cobbled squares and streets', 'Limestone walls from grade', 'Roofs on the eave cornices', 'Attic, drum and dome on the dome block walls', 'Portico on its stepped podium'],
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
# ---- Old Montreal limestone market hall ----

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


def disc(b, role, centre, normal, r, t=.08, n=24):
    """Flat disc standing proud of a wall along its horizontal outward normal (an oculus or its ring)."""
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


def arch_head(f, h, rise, ring=.26, segs=8, ring_role='arch', dep=None):
    """Round head on a rectangular cut: wall infill above the curve (1 cm inside both faces, so it never shares a
    plane with the carrier) and a proud dressed-stone ring over it."""
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
        for d in (-.06, .02):
            vs.append(f.p(pu, d, pz)); vs.append(f.p(pu + nu * ring, d, pz + nz * ring))
    for i in range(segs):
        a, b = 4 * i, 4 * (i + 1)
        fs += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3)]
    n = 4 * segs
    fs += [(0, 1, 3, 2), (n, n + 2, n + 3, n + 1)]
    C.mesh(f'{h["id"]} arch ring', vs, fs, ring_role, 'arches')
    return cz, R


def arched_window(m, b, f, h, inset=.2, occupied='hall', lite=False, rows=3, fan=5):
    """Round-arched sash: jambs, sill and transom at the springing, glazing bars below it and a radial fanlight above;
    one pane fills the cut (the wall infill hides it outside the curve)."""
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    rise = w / 2
    spring = z + hh - rise
    per = .07
    m.box('glass', u, inset + .04, z + hh / 2, w - .04, .01, hh - .04)
    for s in (-1, 1):
        m.box('frame', u + s * (w / 2 - per / 2), inset, (z + spring) / 2, per, .1, spring - z)
    m.box('frame', u, inset, z + per / 2, w - 2 * per, .1, per)
    m.box('frame', u, inset, spring, w - 2 * per, .1, .08)
    if not lite:
        m.box('frame', u, inset - .005, (z + spring) / 2, .05, .09, spring - z - 2 * per)
        for i in range(1, rows):
            m.box('frame', u, inset - .008, z + (spring - z) * i / rows, w - 2 * per, .085, .05)
        for i in range(fan):                                                     # radial fanlight bars
            a = math.pi * (i + 1) / (fan + 1)
            r = rise - .05
            b.beam('frame', f.p(u + .12 * math.cos(a), inset, spring + .12 * math.sin(a)), f.p(u + r * math.cos(a), inset, spring + r * math.sin(a)), .05, .05)
    register(f, h, inset, 'window', occupied)


def sash(m, f, h, inset=.2, occupied='hall', lite=False):
    """Six-over-six sash with a stone sill and a flat dressed lintel."""
    framed(m, f, h, cols=3, rows=4 if not lite else 1, inset=inset, occupied=occupied, frame='frame', lite=lite)
    m.box('stone', h['u'], -.06, h['z'] - .07, h['w'] + .3, .16, .14)
    m.box('stone', h['u'], -.05, h['z'] + h['h'] + .2, h['w'] + .4, .1, .4)


def vent(m, f, h):
    """Barred basement vent: dark pane behind four iron bars."""
    m.box('glass', h['u'], .3, h['z'] + h['h'] / 2, h['w'] - .02, .01, h['h'] - .02)
    for i in range(4):
        m.box('hardware', h['u'] - h['w'] / 2 + h['w'] * (i + .5) / 4, .15, h['z'] + h['h'] / 2, .04, .04, h['h'] - .01)
    register(f, h, .15, 'basement vent', 'basement')


def door_in_arch(m, h, depth, rise):
    """Panelled leaves filling an arched doorway to the springing, a transom and a glazed fanlight above."""
    spring = h['z'] + h['h'] - rise
    m.box('timber', h['u'], depth - .2, h['z'] + (spring - h['z']) / 2, h['w'] - .02, .1, spring - h['z'] - .02)
    m.box('frame', h['u'], depth - .2, (spring + h['z'] + h['h']) / 2, h['w'] - .02, .1, h['h'] - (spring - h['z']) - .02)
    m.box('glass', h['u'], depth - .26, (spring + .15 + h['z'] + h['h']) / 2, h['w'] - .3, .02, h['h'] - (spring - h['z']) - .25)
    m.box('stone', h['u'], depth - .3, spring + .06, h['w'] - .02, .14, .12)
    m.box('hardware', h['u'], depth - .27, (spring + h['z']) / 2, .05, .04, spring - h['z'] - .3)
    for s in (-1, 1):
        for k in range(3):                                                       # sunk panels on each leaf
            m.box('frame', h['u'] + s * h['w'] / 4, depth - .26, h['z'] + .4 + (spring - h['z'] - .6) * (k + .5) / 3, h['w'] / 2 - .35, .02, (spring - h['z'] - .6) / 3 - .2)


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


# Horizontal members of every elevation: (bottom, top, projection). Plinth, plinth cap, first- and second-floor sill
# bands, and the eave cornice (bed mould and corona; modillions between them).
BANDS = ((0.0, G0 - .1, .1), (G0 - .15, G0 + .15, .16), (F1 + .5, F1 + .7, .12), (F2 + .5, F2 + .7, .12),
         (EAVE - .75, EAVE - .45, .25), (EAVE - .25, EAVE, .75))
PLAIN = dict(g=(1.7, 1.4, 2.9), f1=(6.8, 1.4, 2.7), f2=(11.4, 1.4, 2.4))       # sill z, width, height
PAV = dict(g=(1.3, 2.0, 4.4), f1=(6.6, 1.8, 3.6), f2=(11.2, 1.6, 2.6))


def facade(label, origin, tangent, inward, lo, hi, bays, ext, pils, lite=False, top=EAVE, cornice=True):
    """One straight elevation. bays: list of dicts u, kind ('plain' | 'pav'), and optional g/f1/f2 overrides
    (None = no opening, 'door' = arched doorway, 'sqdoor' = corniced square door), vent flag.
    ext: band extension at lo and hi: 'out' (outer corner of a wrapping run: by the band projection),
    'in' (inside corner: shortened by it) or a number (a run between wrapping runs: by the wall depth)."""
    f = C.Face(origin, tangent, inward, label)
    holes, kinds = [], []
    for bay in bays:
        u, k = bay['u'], bay.get('kind', 'plain')
        spec = PAV if k == 'pav' else PLAIN
        if bay.get('vent', True):
            holes.append(hole(f'{label} vent {u:+.1f}', u, .22, .9 if k == 'plain' else 1.2, .42)); kinds.append('vent')
        for lvl in ('g', 'f1', 'f2'):
            v = bay.get(lvl, k)
            if v is None:
                continue
            if v == 'door':
                holes.append(hole(f'{label} door {u:+.1f}', u, G0, bay.get('dw', 2.6), bay.get('dh', 5.0), kind='door')); kinds.append('door')
            elif v == 'sqdoor':
                holes.append(hole(f'{label} door {u:+.1f}', u, G0, 1.8, 3.4, kind='door')); kinds.append('sqdoor')
            else:
                z, w, hh = (PAV if v == 'pav' else PLAIN)[lvl]
                holes.append(hole(f'{label} {lvl} {u:+.1f}', u, z, w, hh)); kinds.append(v if lvl != 'f1' or v != 'pav' else 'pav_bal')
    f.wall(f'{label} carrier', lo, hi - EPS, 0.0, top, depth=T, role='wall', holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, G0 + .2, top - .8, holes, spacing=.55)
    m = Merge(f)
    b = Batch()
    for z0, z1, d in BANDS:
        if not cornice and z0 > EAVE - 1:
            continue
        e0, e1 = [d if e == 'out' else -d if e == 'in' else e for e in ext]
        for ra, rc in runs(lo - e0, hi + e1, z0, z1, holes):
            m.box('stone', (ra + rc) / 2, -d / 2, (z0 + z1) / 2, rc - ra, d, z1 - z0)
    if cornice:
        n = max(2, int((hi - lo) / .9))
        for i in range(n + 1):                                                    # modillions under the corona
            m.box('stone', lo + .3 + (hi - lo - .6) * i / n, -.28, EAVE - .35, .22, .5, .24)
    for a, c in pils:                                                             # dressed pilaster strips
        m.box('stone', (a + c) / 2, -.075, (G0 + .15 + EAVE - .75) / 2, c - a, .15, EAVE - .75 - G0 - .15)
    for h, k in zip(holes, kinds):
        if k == 'vent':
            vent(m, f, h)
        elif k == 'plain':
            sash(m, f, h, lite=lite)
        elif k in ('pav', 'pav_bal'):
            arched_window(m, b, f, h, lite=lite)
            arch_head(f, h, h['w'] / 2, ring=.3, segs=8)
            m.box('arch', h['u'], -.09, h['z'] + h['h'] + .12, .36, .18, .5)              # keystone
            if k == 'pav_bal':
                iron_balcony(m, f, h['u'], h['z'], h['w'] + .5, depth=.55)
            else:
                m.box('stone', h['u'], -.06, h['z'] - .07, h['w'] + .3, .16, .14)
        elif k == 'door':
            rise = h['w'] / 2
            door_in_arch(m, h, T, rise)
            register(f, h, T - .3, 'door', 'entrance hall')
            arch_head(f, h, rise, ring=.45, segs=10)
            m.box('arch', h['u'], -.1, h['z'] + h['h'] + .2, .5, .2, .7)
        elif k == 'sqdoor':
            u, top_ = h['u'], h['z'] + h['h']
            m.box('timber', u, T - .2, h['z'] + 1.35, h['w'] - .02, .1, 2.7)
            m.box('frame', u, T - .2, top_ - .35, h['w'] - .02, .1, .66)
            m.box('glass', u, T - .26, top_ - .35, h['w'] - .3, .02, .5)
            m.box('hardware', u + .3, T - .27, h['z'] + 1.2, .05, .04, .5)
            for s in (-1, 1):                                                     # architrave, consoles and hood
                m.box('stone', u + s * (h['w'] / 2 + .15), -.06, h['z'] + h['h'] / 2, .3, .12, h['h'])
                m.box('stone', u + s * (h['w'] / 2 + .35), -.25, top_ + .25, .26, .5, .7)
            m.box('stone', u, -.12, top_ + .15, h['w'] + .6, .24, .3)
            m.box('stone', u, -.3, top_ + .75, h['w'] + 1.3, .6, .3)
            m.box('stone', u, -.36, top_ + .96, h['w'] + 1.5, .72, .12)
            register(f, h, T - .2, 'door', 'stair hall')
    m.flush(label)
    b.flush(label + ' fanlights')
    return f


def steps(b, f, u, w, n=3, top=G0, run=.36):
    """Stone steps up to a door sill at `top` in front of face f."""
    for k in range(n):
        p = f.p(u, -run * (k + .5), 0.0)
        hgt = top * (n - k) / n
        sx = abs(f.t[0]) * (w + .3 * k) + abs(f.t[1]) * run
        sy = abs(f.t[1]) * (w + .3 * k) + abs(f.t[0]) * run
        b.box('stone', p[0], p[1], hgt / 2, sx, sy, hgt)


def plain_bays(us, **kw):
    return [dict(u=u, kind='plain', **kw) for u in us]


def pav_bays(us, **kw):
    return [dict(u=u, kind='pav', **kw) for u in us]


S_, E_, N_, W_ = ((1, 0, 0), (0, 1, 0)), ((0, 1, 0), (-1, 0, 0)), ((-1, 0, 0), (0, -1, 0)), ((0, -1, 0), (1, 0, 0))


def elevations():
    pav = [45.2, 48.9, 52.6]
    # East range, south front: fifteen plain bays, the portico doorway at x = 0, the end pavilion.
    bays = []
    for k in range(-2, 13):
        x = 3.4 * k
        if abs(x) < 9.0:                                                          # behind the portico
            bays.append(dict(u=x, kind='plain', vent=False, f2=None, g='door' if x == 0 else 'plain'))
        else:
            bays.append(dict(u=x, kind='plain'))
    bays += pav_bays(pav)
    pils = [(-11.0 - .15, -10.1), (14.85, 15.75), (25.05, 25.95), (35.25, 36.15),
            (42.3, 43.5), (46.6, 47.5), (50.3, 51.2), (54.1, 55.15)]
    f = facade('south front', (0, EY0, 0), *S_, EX0, EX1, bays, ('out', 'out'), pils)
    # East end: five pavilion bays round the corniced door.
    ys = [-27.45, -23.85, -20.25, -16.65, -13.05]
    bays = [dict(u=y, kind='pav', g='sqdoor', vent=False) if y == -20.25 else dict(u=y, kind='pav') for y in ys]
    f = facade('east end', (EX1, 0, 0), *E_, EY0 + T, EY1 - T, bays, (T, T),
               [(EY0, EY0 + .9), (-26.1, -25.2), (-22.5, -21.6), (-18.9, -18.0), (-15.3, -14.4), (EY1 - .9, EY1)])
    b = Batch()
    steps(b, f, -20.25, 2.6)
    b.flush('east door steps')
    # East range, north front (court side): pavilion and nine plain bays to the dome block.
    bays = pav_bays([-x for x in pav]) + plain_bays([-3.4 * k for k in range(12, 3, -1)])
    facade('east range north', (0, EY1, 0), *N_, -EX1, -DX1, bays, ('out', 0.0),
           [(-EX1 - .15, -54.1), (-51.2, -50.3), (-47.5, -46.6), (-43.5, -42.3), (-35.25 - .9, -35.25), (-25.95, -25.05), (-15.75, -14.85)], lite=True)
    # East range, west end over the cobbled square.
    facade('east range west', (EX0, 0, 0), *W_, -EY1, -EY0 - T, plain_bays([13.2, 16.6, 20.0, 23.4, 26.8]), (0.0, T),
           [(-EY1, -EY1 + .9), (-EY0 - .9, -EY0)], lite=True)
    # West range, south front over the cobbled square.
    us = [-48.6 + 3.4 * k for k in range(11)]
    facade('west range south', (0, WY0, 0), *S_, WX0, WX1, plain_bays(us), ('out', 'in'),
           [(WX0 - .15, WX0 + .9), (-43.95, -43.05), (-33.75, -32.85), (-23.55, -22.65), (-12.05 - .25, -11.15 - .25)])
    # West end.
    facade('west range west', (WX0, 0, 0), *W_, -WY1 + T, -WY0 - T, plain_bays([-7.2, -3.6, 0.0, 3.6, 7.2]), (T, T),
           [(-WY1, -WY1 + .9), (WY1 - .9, WY1)], lite=True)
    # North front: the west range and the dome block in one run, the porch doorway at x = 0.
    bays = plain_bays([-u for u in us])
    for x in (-8.4, -4.2, 0.0, 4.2, 8.4):
        if abs(x) < NX1:
            bays.append(dict(u=-x, kind='plain', vent=False, g='door' if x == 0 else 'plain', dw=2.4, dh=3.8))
        else:
            bays.append(dict(u=-x, kind='plain'))
    facade('north front', (0, WY1, 0), *N_, -DX1, -WX0, bays, ('out', 'out'),
           [(-DX1 - .15, -DX1 + .9), (10.1 + 1.5, 11.0 + 1.5), (43.05, 43.95), (32.85, 33.75), (22.65, 23.55), (-WX0 - .9, -WX0 + .15)], lite=True)
    # Dome block, east face over the court.
    facade('dome block east', (DX1, 0, 0), *E_, WY0, WY1 - T, plain_bays([-6.3, -2.1, 2.1, 6.3]), ('in', T),
           [(WY0 + .9, WY0 + 1.8), (WY1 - .9, WY1)])


def portico():
    """Tetrastyle Tuscan portico on a stepped podium: plain shafts with entasis, entablature, pediment with raking
    cornices and a slate roof running back into the front wall."""
    yf = EY0 - QD
    ZE, ZE1, rise = 10.1, 11.7, 3.0
    b = Batch()
    b.box('stone', 0.0, (yf - .3 + EY0 + .1) / 2, G0 / 2, QX1 - QX0 + .8, EY0 + .1 - (yf - .3), G0)            # podium
    for k in range(3):
        hgt = G0 * (3 - k) / 4
        b.box('stone', 0.0, yf - .3 - .36 * (k + .5), hgt / 2, QX1 - QX0 + .8 + .3 * k, .36, hgt)
    yc = yf + .9
    for x in (-8.0, -2.65, 2.65, 8.0):
        b.box('stone', x, yc, G0 + .15, 1.55, 1.55, .3)                                                      # plinth
        cyl(b, 'stone', x, yc, G0 + .3, G0 + .55, .72, 16)                                                     # torus
        frustum(b, 'stone', x, yc, G0 + .55, ZE - .8, .62, .52, 16)                                          # shaft with entasis
        cyl(b, 'stone', x, yc, ZE - .8, ZE - .68, .58, 16)                                                     # necking
        frustum(b, 'stone', x, yc, ZE - .68, ZE - .35, .55, .74, 16)                                         # echinus
        b.box('stone', x, yc, ZE - .15, 1.6, 1.6, .4)                                                        # abacus, seated into the beam
    for x in (-8.0, 8.0):                                                                                     # responds on the wall
        b.box('stone', x, EY0 - .1, (G0 + ZE) / 2, .9, .2, ZE - G0)
    b.box('stone', 0.0, (yf + EY0 + .15) / 2, (ZE + ZE1 - .2) / 2, QX1 - QX0, EY0 + .15 - yf, ZE1 - .2 - ZE)       # architrave and frieze
    for i in range(13):                                                                                       # triglyphs
        b.box('stone', QX0 + .4 + (QX1 - QX0 - .8) * i / 12, yf - .05, ZE + 1.0, .5, .12, .7)
    b.box('stone', 0.0, (yf - .3 + EY0 + .15) / 2, ZE1 - .175, QX1 - QX0 + .6, EY0 + .15 - yf + .3, .35)         # cornice
    C.prism('Portico tympanum', [(QX0 + .3, ZE1 - .1), (QX1 - .3, ZE1 - .1), (0.0, ZE1 + rise)], 'y', yf + .15, yf + .55, 'wall', 'portico')
    C.prism('Portico roof', [(QX0 - .35, ZE1 - .05), (QX1 + .35, ZE1 - .05), (0.0, ZE1 + rise + .45)], 'y', yf + .45, EY0 + .3, 'roof', 'portico')
    for s in (-1, 1):
        b.beam('stone', (s * (QX1 + .25), yf + .1, ZE1 + .05), (0.0, yf + .1, ZE1 + rise + .32), .9 + .04 * (s > 0), .42, ext=.05)
    disc(b, 'stone', (0.0, yf + .15, ZE1 + 1.15), (0, -1), .75, .06)
    disc(b, 'glass', (0.0, yf + .09, ZE1 + 1.15), (0, -1), .55, .03)
    b.flush('portico')


def north_porch():
    """Flat-roofed arcaded porch on the north front of the dome block, with a balustrade on its roof."""
    yf, top = WY1 + ND, 5.4
    f = C.Face((0, yf, 0), *N_, 'north porch front')
    hs = [hole(f'north porch arch {u:+.1f}', u, G0, 2.6, 4.0, kind='arcade') for u in (-4.4, 0.0, 4.4)]
    f.wall('north porch front carrier', NX0, NX1 - EPS, 0.0, top, depth=.6, role='wall', holes=hs)
    G.brick_courses(f, NX0 + .02, NX1 - .02, .2, top - .2, hs, spacing=.55)
    m = Merge(f)
    for h in hs:
        arch_head(f, h, 1.3, ring=.3, segs=8, dep=.6)
        register(f, h, 0.0, 'porch arch', 'entrance porch')
        m.box('arch', h['u'], -.09, h['z'] + h['h'] + .12, .36, .18, .5)
    m.box('stone', 0.0, -.08, top - .25, NX1 - NX0 + .16, .16, .5)
    m.flush('north porch front')
    for label, o, t, n, lo, hi in (('north porch east', (NX1, 0, 0), *E_, WY1, yf - .6), ('north porch west', (NX0, 0, 0), *W_, -(yf - .6), -WY1)):
        g = C.Face(o, t, n, label)
        uc = (lo + hi) / 2
        h = hole(f'{label} arch', uc, G0, 1.6, 3.6, kind='arcade')
        g.wall(label + ' carrier', lo, hi - EPS, 0.0, top, depth=.6, role='wall', holes=[h])
        arch_head(g, h, .8, ring=.25, segs=8, dep=.6)
        register(g, h, 0.0, 'porch arch', 'entrance porch')
        m = Merge(g)
        m.box('stone', uc, -.08, top - .25, hi - lo + .08, .16, .5)
        m.flush(label)
    b = Batch()
    b.box('stone', 0.0, (WY1 + .1 + yf - .6) / 2, G0 / 2, NX1 - NX0 - 1.2, yf - .6 - WY1 - .1, G0)                          # porch floor
    b.box('membrane', 0.0, (WY1 - .2 + yf + .2) / 2, top + .1, NX1 - NX0 + .4, yf + .2 - WY1 + .2, .4)              # flat roof
    for k in range(3):
        hgt = G0 * (3 - k) / 3
        b.box('stone', 0.0, yf + .36 * (k + .5), hgt / 2, 3.4 + .3 * k, .36, hgt)
    balustrade(b, (NX0 + .1, yf - .1), (NX1 - .1, yf - .1), top + .3, [(NX1 - NX0 - .2) / 2], ends=(True, True))
    for x in (NX0 + .1, NX1 - .1):
        balustrade(b, (x, WY1 - .1), (x, yf - .5), top + .3, [], ends=(True, False))
    b.flush('north porch')


def balustrade(b, a, c, z, posts, ends=(True, True), end_w=.62):
    """Balustrade along a-c (world xy) at height z: plinth, balusters, rail, pedestals at posts and ends."""
    (ax, ay), (cx, cy) = a, c
    L = math.hypot(cx - ax, cy - ay)
    ux, uy = (cx - ax) / L, (cy - ay) / L
    b.beam('stone', (ax, ay, z + .08), (cx, cy, z + .08), .5, .24)
    b.beam('stone', (ax, ay, z + .93), (cx, cy, z + .93), .48, .14)
    caps = [p for p, e in ((0.0, ends[0]), (L, ends[1])) if e]
    n = int(L / .32)
    for i in range(n):
        t = (i + .5) / n * L
        if any(abs(t - p) < .45 for p in list(posts) + caps):
            continue
        b.box('stone', ax + ux * t, ay + uy * t, z + .53, .14, .14, .66)
    for p in list(posts) + caps:
        b.box('stone', ax + ux * p, ay + uy * p, z + .52, end_w, end_w, 1.12)
        b.box('stone', ax + ux * p, ay + uy * p, z + 1.12, end_w + .08, end_w + .08, .08)


def roofs():
    ov = .35
    pitched_roof('West range roof', WX0, WX1, WY0, WY1, EAVE, RISE, hip_w=True, hip_e=False, axis='x', ov=ov)
    pitched_roof('East range roof', EX0, EX1 - 1.1, EY0, EY1, EAVE, RISE, hip_w=True, hip_e=False, axis='x', ov=ov)
    # East pediment: tympanum under the roof plate, raking cornices standing proud of the slates, a blind oculus.
    ym = (EY0 + EY1) / 2
    C.prism('East pediment tympanum', [(EY0 + .3, EAVE - .05), (EY1 - .3, EAVE - .05), (ym, EAVE + RISE)], 'x', EX1 - .7, EX1, 'wall', 'pediment')
    b = Batch()
    for s, y in ((-1, EY0), (1, EY1)):
        b.beam('stone', (EX1 - .1, y + s * .25, EAVE + .15), (EX1 - .1, ym, EAVE + RISE + .1), 1.4 + .04 * (s > 0), .6, ext=.05)
    disc(b, 'stone', (EX1, ym, EAVE + 1.7), (1, 0), .95, .08)
    disc(b, 'glass', (EX1 + .08, ym, EAVE + 1.7), (1, 0), .7, .03)
    # Eaves balustrades of the end pavilion.
    balustrade(b, (PX0, EY0 - .3), (EX1 - .3, EY0 - .3), EAVE, [6.0], ends=(True, True))
    balustrade(b, (PX0, EY1 + .3), (EX1 - .3, EY1 + .3), EAVE, [6.0], ends=(True, True))
    # Stone chimneys on the ridges, vent dormers on the court slope of the east range.
    for x, y in ((-44.0, 0.0), (-26.0, 0.0), (16.0, ym), (32.0, ym)):
        chimney(b, x, y, EAVE + RISE - .6, EAVE + RISE + 1.9, w=1.3, d=.8, pots=2, role='wall', pot='pot', cap='stone')
    b.flush('roof furniture')
    for i, x in enumerate((18.0, 22.0, 26.0, 30.0, 36.0)):
        zf = EAVE + RISE * (EY1 - (EY1 - 2.2)) / ((EY1 - EY0) / 2)
        C.prism(f'Vent dormer {i}', [(x - .55, zf - .15), (x + .55, zf - .15), (x, zf + .75)], 'y', EY1 - 4.4, EY1 - 2.2, 'roof', 'roof')
        C.box(f'Vent dormer louvre {i}', (x, EY1 - 2.18, zf + .12), (.5, .04, .4), 'glass', 'roof', 0)
    # Skylight on the south slope of the west range.
    za = EAVE + RISE * 3.5 / ((WY1 - WY0) / 2) + .1
    zb = EAVE + RISE * 6.5 / ((WY1 - WY0) / 2) + .1
    C.beam('West skylight frame', (-33.0, WY0 + 3.5, za), (-33.0, WY0 + 6.5, zb), 5.0, .14, 'frame', 'roof')
    C.beam('West skylight glass', (-33.0, WY0 + 3.6, za + .1), (-33.0, WY0 + 6.4, zb + .1), 4.7, .04, 'glass', 'roof')


def dome_block():
    """Square attic over the dome block, drum of sixteen arched windows between engaged columns, entablature,
    ribbed tin dome and open lantern with a cupola and cross."""
    for label, o, t, n, lo, hi in (('attic north', (0, WY1, 0), *N_, -DX1, -DX0), ('attic south', (0, WY0, 0), *S_, DX0, DX1),
                                   ('attic east', (DX1, 0, 0), *E_, WY0 + T, WY1 - T), ('attic west', (DX0, 0, 0), *W_, -WY1 + T, -WY0 - T)):
        f = C.Face(o, t, n, label)
        f.wall(label + ' carrier', lo, hi - EPS, EAVE - .01, ATT, depth=T, role='wall')
        G.brick_courses(f, lo + .02, hi - .02, EAVE + .3, ATT - .9, [], spacing=.55)
        m = Merge(f)
        wraps = label in ('attic north', 'attic south')
        for z0, z1, d in ((ATT - .9, ATT - .6, .2), (ATT - .3, ATT, .45)):
            e = d if wraps else T
            m.box('stone', (lo + hi) / 2, -d / 2, (z0 + z1) / 2, hi - lo + 2 * e, d, z1 - z0)
        for k in range(4):                                                         # sunk panels
            uc = lo + (hi - lo) * (k + .5) / 4
            m.box('joint', uc, -.004, (EAVE + .8 + ATT - 1.3) / 2, 3.4, .01, ATT - 2.1 - EAVE)
            m.box('wall', uc, -.012, (EAVE + .8 + ATT - 1.3) / 2, 3.1, .01, ATT - 2.4 - EAVE)
        m.flush(label)
    b = Batch()
    b.box('metal', 0.0, 0.0, ATT - .22, DX1 - DX0 - 2 * T + .2, WY1 - WY0 - 2 * T + .2, .25)                 # tin deck
    for x in (DX0 + .5, DX1 - .5):
        for y in (WY0 + .5, WY1 - .5):
            b.box('stone', x, y, ATT + .5, 1.3, 1.3, 1.2)                                                    # corner pedestals
            b.box('stone', x, y, ATT + 1.15, 1.45, 1.45, .1)
            frustum(b, 'stone', x, y, ATT + 1.2, ATT + 1.6, .35, .5, 12)                                     # urns
            frustum(b, 'stone', x, y, ATT + 1.6, ATT + 2.1, .5, .2, 12)
    cyl(b, 'stone', 0.0, 0.0, ATT - .1, ATT + .6, DR + .3, 32)                                               # drum base
    cyl(b, 'stone', 0.0, 0.0, ATT + DRUM - .15, ATT + DRUM + .55, DR + .25, 32)                              # drum entablature
    cyl(b, 'stone', 0.0, 0.0, ATT + DRUM + .55, ATT + DRUM + 1.0, DR + .55, 32)                               # drum cornice
    nseg = 16
    half = DR * math.sin(math.pi / nseg)
    ap = DR * math.cos(math.pi / nseg)
    for i in range(nseg):
        a = 2 * math.pi * (i + .5) / nseg
        o = (ap * math.cos(a), ap * math.sin(a), 0.0)
        f = C.Face(o, (-math.sin(a), math.cos(a), 0.0), (-math.cos(a), -math.sin(a), 0.0), f'drum {i:02d}')
        h = hole(f'drum window {i:02d}', 0.0, ATT + 1.2, 1.3, 4.2)
        f.wall(f'drum {i:02d} carrier', -half, half - EPS, ATT - .05, ATT + DRUM, depth=.6, role='wall', holes=[h])
        m = Merge(f)
        framed(m, f, h, cols=1, rows=1, inset=.18, occupied='drum', frame='frame', lite=True)
        arch_head(f, h, .65, ring=.16, segs=6, dep=.6)
        m.box('stone', 0.0, -.05, ATT + 1.13, 1.6, .14, .14)
        m.flush(f'drum {i:02d}')
        va = 2 * math.pi * (i + 1) / nseg                                                                    # engaged column on each angle
        vx, vy = (DR + .02) * math.cos(va), (DR + .02) * math.sin(va)
        cyl(b, 'stone', vx, vy, ATT + .6, ATT + DRUM - .55, .24, 10)
        b.box('stone', vx, vy, ATT + DRUM - .35, .6, .6, .4)
    b.flush('drum and attic')
    prof = [(1.0, 0.0), (.985, .2), (.93, .4), (.82, .6), (.62, .8), (.34, .95), (0.0, 1.0)]
    dome('Tin dome', 0.0, 0.0, DOME0 - .05, DOME_R, DOME_H, prof, 'metal', 'dome', segs=48, n=16)
    sp = smooth_profile(prof, 18)
    rib = [(DOME_R * r, DOME_H * z) for r, z in sp if DOME_R * r > 1.7]
    for k in range(16):
        rib_mesh(f'Dome rib {k:02d}', 0.0, 0.0, DOME0 - .05, 2 * math.pi * k / 16, rib, .14, .06, 'trim', 'dome')
    b = Batch()
    cyl(b, 'metal', 0.0, 0.0, LANT - .3, LANT + .45, 2.0, 16)                                                # lantern base
    cyl(b, 'glass', 0.0, 0.0, LANT + .45, LANT + 3.0, 1.15, 16)                                               # glazed core
    for k in range(8):
        a = 2 * math.pi * (k + .5) / 8
        cyl(b, 'trim', 1.6 * math.cos(a), 1.6 * math.sin(a), LANT + .45, LANT + 3.0, .14, 8)
    cyl(b, 'metal', 0.0, 0.0, LANT + 3.0, LANT + 3.5, 1.95, 16)
    b.flush('lantern')
    dome('Lantern cupola', 0.0, 0.0, LANT + 3.45, 1.75, 1.6, prof, 'metal', 'dome', segs=24, n=8)
    b = Batch()
    cyl(b, 'metal', 0.0, 0.0, LANT + 4.95, LANT + 5.3, .22, 10)
    b.box('hardware', 0.0, 0.0, LANT + 5.95, .1, .1, 1.3)
    b.box('hardware', 0.0, 0.0, LANT + 6.2, .7, .1, .1)
    b.flush('cross')


def inside():
    i = T + .01
    pts = [(WX0 + i, WY0 + i), (WX0 + i, WY1 - i), (DX1 - i, WY1 - i), (DX1 - i, EY1 - i), (EX1 - i, EY1 - i),
           (EX1 - i, EY0 + i), (EX0 + i, EY0 + i), (EX0 + i, WY0 + i)]
    for z in (G0, F1, F2):
        C.prism(f'Floor {z:.1f}', pts, 'z', z - .24, z, 'floor', 'inside')
    for x, y in ((-44.0, 0.0), (-28.0, 0.0), (0.0, 0.0), (-2.0, -20.0), (14.0, -20.0), (30.6, -20.0), (48.0, -20.0)):
        for z in (G0, F1, F2):
            C.qa_room_light(f'Room {x:+.0f} {y:+.0f} {z:.0f}', (x, y, z + 2.6), 120, 3.0)
    C.CONTACTS.append(dict(name='Limestone walls from grade; roofs on the eave cornices; attic and drum on the dome block walls', eave_m=EAVE))


def site():
    for name, x0, x1, y0, y1, role, top in (
            ('South street', -62.0, 66.0, -46.0, -38.5, 'asphalt', .02), ('North street', -62.0, 66.0, 14.5, 22.0, 'asphalt', .02),
            ('East street', 59.5, 66.0, -38.5, 14.5, 'asphalt', .02), ('West street', -62.0, -56.0, -38.5, 14.5, 'asphalt', .02),
            ('South sidewalk', -56.0, 59.5, -38.5, EY0, 'concrete', .14), ('North sidewalk', -56.0, 59.5, WY1, 14.5, 'concrete', .14),
            ('East sidewalk', EX1, 59.5, EY0, WY1, 'concrete', .14), ('West sidewalk', -56.0, WX0, EY0, WY1, 'concrete', .14),
            ('South-west cobbled square', WX0, EX0, EY0, WY0, 'cobble', .10), ('North-east cobbled court', DX1, EX1, EY1, WY1, 'cobble', .10)):
        C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, top / 2), (x1 - x0, y1 - y0, top), role, 'site', 0)
    b = Batch()
    for k in range(1, 20):                                                         # setts in courses
        b.box('joint', (WX0 + EX0) / 2, EY0 + k * (WY0 - EY0) / 20, .101, EX0 - WX0 - .2, .03, .004)
        b.box('joint', (DX1 + EX1) / 2, EY1 + k * (WY1 - EY1) / 20, .101, EX1 - DX1 - .2, .03, .004)
    for k in range(-27, 30):
        b.box('joint', k * 2.0, -34.25, .141, .02, 8.46, .004)
    b.flush('paving joints')
    for x in (-48.0, -32.0, -18.0, 14.0, 26.0):                                   # the pavilion end of the street stays open (front)
        street_tree(x, -37.2, z=.14, height=10.0, spread=2.6)
    for x, y in ((-44.0, -21.0), (-32.0, -21.0), (-20.0, -21.0)):
        street_tree(x, y, z=.10, height=9.0, spread=2.4)
    for x in (-40.0, -24.0, 24.0, 40.0):
        street_tree(x, 13.3, z=.14, height=9.0, spread=2.2)


def build():
    site()
    elevations()
    portico()
    north_porch()
    roofs()
    dome_block()
    inside()
    C.CONTACTS.append(dict(name='Domed limestone market hall with a portico on a city block', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(70, -80, 70), fill=(-70, -40, 45), rear=(-30, 60, 50), target=(0, -10, 12.0), gain=6.0)
