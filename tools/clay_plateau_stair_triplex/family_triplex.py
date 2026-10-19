"""Montreal Plateau stair triplex, authored from the locked catalogue views of
montreal_plateau_triplex / variant_0 (montreal_triplex_classic_iron).

Read from the pixels (the top view governs the plan): a flat-roofed two-storey plex over a half-basement on a
street corner, the street south and a side street east, an attached brick neighbour to the west. A grey
limestone front with block coursing and proud quoins; a recessed central porch on both floors, the ground porch
with a green door, the upper porch behind a stone balcony with an iron railing and a pair of red glazed doors,
sheltered by a flat canopy on two iron lattice columns. Wide timber-framed windows with transoms in the side
bays, stone sills and lintels, small basement windows at grade. The black iron exterior stair climbs from the
yard to the upper balcony and curls at its foot. A projecting bracketed cornice with a central attic panel
and cartouche; plain grey brick side and rear walls with narrow windows. A pale membrane roof with three
skylights and a roof hatch; a small lawn behind an iron fence, sidewalks and street trees.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-plateau-stair-triplex'
X0, X1, Y0, Y1 = -4.5, 4.5, -6.5, 6.5          # 9 m front, 13 m deep
T = .35
F1 = 1.0                                        # raised ground floor over the half-basement
F2 = 4.47                                       # upper floor (the balcony level)
ROOF = 7.8
PAR = 8.6                                       # front parapet top
PW = 1.7                                        # half-width of the central porch
PD = 1.5                                        # porch recess depth
EPS = .002
PALETTE = dict(wall=(.56, .56, .54), joint=(.44, .44, .43), brick=(.52, .52, .51), quoin=(.64, .64, .62),
    trim=(.44, .30, .16), pale=(.86, .86, .84), stone=(.60, .60, .58), roof=(.70, .70, .68), sand=(.66, .62, .56),
    foundation=(.52, .52, .50), glass=(.24, .28, .31), hardware=(.07, .07, .08), interior=(.84, .80, .74),
    floor=(.58, .48, .38), timber=(.44, .30, .16), red=(.62, .12, .10), green=(.14, .30, .24),
    planting=(.30, .46, .20), lawn=(.36, .52, .24), soil=(.22, .16, .10), concrete=(.70, .69, .66),
    white=(.95, .95, .93), asphalt=(.30, .30, .31), pot=(.60, .34, .22), neighbour=(.46, .29, .21),
    blue=(.20, .30, .40))


def manifest(version):
    h = PAR + 1.4
    cams = G.camera_roster(X1 - X0 + 3.0, Y1 - Y0 + 3.0, h, [
        ('facade_close', (0.0, -16.0, 4.6), (0.0, Y0, 4.6), 45),
        ('architecture_close', (8.0, -12.0, 8.4), (X1 - 1.0, Y0, 8.2), 45),
        ('glass_close', (-3.1, Y0 - 5.5, F2 + 1.4), (-3.1, Y0, F2 + 1.4), 45),
        ('iron_stair', (5.0, -13.0, 2.8), (-.6, Y0 - 2.4, 2.6), 40),
        ('balcony_canopy', (3.5, -9.5, 5.6), (0.0, Y0, 5.8), 40),
        ('cornice_parapet', (3.0, -10.0, 10.5), (0.0, Y0, 8.6), 40),
        ('east_side', (16.0, 0.0, 4.2), (X1, 0.0, 4.2), 45),
        ('roof_skylights', (-7.0, -9.0, 16.0), (0.0, 0.5, ROOF), 40),
        ('interior', (2.6, 4.0, F2 + 1.6), (-1.0, Y0, F2 + 1.6), 40),
        ('rear_north', (0.0, 22.0, 4.5), (0.0, Y1, 4.5), 45)])
    for c in cams:                       # the locked front and oblique look from the south-east
        if c['name'] == 'front':
            c['location'] = (7.0, -16.5, 1.6); c['target'] = (-.4, -6.5, 4.4); c['lens'] = 26; c['whole'] = False
        elif c['name'] == 'front_corner':                                      # the locked oblique: close and high from the south-east
            c.update(location=(14.0, -19.0, 15.0), target=(0.0, -2.5, 4.0), lens=35, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(9.0, -15.0, 26.0), target=(0.0, -1.0, 3.0), lens=35, whole=False)
        elif c['name'] == 'left_side':                                        # over the attached neighbour, from the north-west
            c.update(location=(-15.0, 17.0, 13.0), target=(0.0, 1.0, 4.5), lens=35, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(22.0, -1.0, 5.0), target=(X1, 0.0, 4.2), lens=35, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(0.0, Y1 + 18.0, 5.0), target=(0.0, Y1, 4.5), lens=35, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(15.0, 19.0, 12.0), target=(0.0, 1.0, 4.0), lens=35, whole=False)
        elif c['name'] == 'top':                                               # plan view framed on the plex and its yard
            c.update(location=(0.0, -1.5, 40.0), target=(0.0, -1.499, 0.0), ortho_scale=28.0, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='montreal_plateau_triplex/variant_0 (montreal_triplex_classic_iron)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=2, storey_programme='two flats over a half-basement, the upper flat reached by the exterior iron stair',
            plan='9 x 13 m corner plex (top view), a 3.8 m front yard, an attached neighbour west',
            facade='grey limestone with quoins; recessed two-storey central porch; stone balcony and iron railing; canopy on iron lattice columns; wide timber windows; bracketed cornice with a central attic and cartouche',
            levels_m=[F1, F2, ROOF, PAR], roof_m=dict(flat=ROOF, parapet=PAR),
            inferred='interiors and the rear face are teaching assumptions; the rear repeats the side wall grammar'),
        roof_contract=dict(type='flat membrane roof behind a bracketed cornice and central attic panel, three skylights and a roof hatch', datum_m=ROOF, crowns_m=[9.07]),
        identity_contract=dict(owner='grey limestone Plateau plex with a curling black iron exterior stair to a canopied upper balcony, red and green doors, bracketed cornice'),
        material_contract=dict(profile='source-palette clay: grey limestone with joints and pale quoins, grey brick sides, timber frames, black iron, red upper doors, green lower door, pale membrane roof', textured_keeper=False),
        programme_contract=dict(storeys=2, ground='lower flat and porch', upper='upper flat off the balcony', basement='half-basement'),
        contact_contract=['Grade-zero sidewalks, lawn and fence', 'Stone walls from grade', 'Stair foot on the yard paving', 'Cornice on the front wall'],
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


# ---- Montreal Plateau stair triplex ----

def stone_window(m, f, h, cols=2, rows=2, occupied='room', lite=False, lintel=True):
    framed(m, f, h, cols=cols, rows=rows, inset=.13, occupied=occupied, lite=lite)
    m.box('quoin', h['u'], -.04, h['z'] - .07, h['w'] + .2, .12, .12)                       # sill
    if lintel:
        m.box('quoin', h['u'], -.05, h['z'] + h['h'] + .165, h['w'] + .3, .1, .32)           # lintel block


def fence(b, a, c, height=1.05, spacing=.14):
    """Batched iron fence on a low curb: rails and pickets in one mesh."""
    (ax, ay), (cx, cy) = a, c
    L = math.hypot(cx - ax, cy - ay)
    b.beam('stone', (ax, ay, .1), (cx, cy, .1), .22, .2)
    for z in (.32, height - .04):
        b.beam('hardware', (ax, ay, z), (cx, cy, z), .035, .035)
    n = max(2, int(L / spacing))
    for i in range(n + 1):
        px, py = ax + (cx - ax) * i / n, ay + (cy - ay) * i / n
        top = height + (.1 if i % 12 == 0 else 0)
        b.box('hardware', px, py, (.2 + top) / 2, .025 if i % 12 else .06, .025 if i % 12 else .06, top - .2)


CZ, RC, ATT = 8.15, 1.9, .75                    # cornice top, half-width and height of the flush central attic


def cornice_run(m, lo, hi, z, wrap=(False, False), behind=False):
    """Bed mould, modillions, corona and cymatium between lo and hi; a wrapped end runs on by each band's
    projection so the corner square is closed by this run. A return run (behind=True) starts each band just
    behind the matching front band's back face, so the two never share volume or faces."""
    for d, t, zc, h in ((-.10, T + .2, z - .62, .26), (-.29, T + .62, z - .13, .26), (-.29, T + .52, z + .03, .06)):
        p = -(d - t / 2)
        a = lo - (p if wrap[0] else 0.0) + ((d + t / 2 + .003) if behind else 0.0)
        c = hi + (p if wrap[1] else 0.0)
        m.box('stone', (a + c) / 2, d, zc, c - a, t, h)
    n = max(1, int((hi - lo) / .7))
    for i in range(n):
        m.box('stone', lo + .35 + (hi - lo - .7) * i / max(1, n - 1), -.34, z - .32, .22, .6, .3)


def console(m, u, z):
    """Scroll console under the bed mould, backed on the wall: a deep head, a tapering shank and a rolled foot."""
    for d, t, z0, z1, w in ((-.3, .6, z - 1.0, z - .74, .22), (-.2, .4, z - 1.22, z - 1.0, .2), (-.12, .24, z - 1.4, z - 1.22, .2)):
        m.box('stone', u, d, (z0 + z1) / 2, w, t, z1 - z0)
    m.box('stone', u, -.27, z - 1.34, .16, .14, .14)


def disc_y(b, role, cx, cz, r, y0, y1, n=12):
    """Disc on a south-facing wall: an n-gon in x/z extruded along y."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for y in (y0, y1):
        for i in range(n):
            a = 2 * math.pi * i / n
            V.append((cx + r * math.cos(a), y, cz + r * 1.15 * math.sin(a)))
    F.append(tuple(o + i for i in range(n)))
    F.append(tuple(o + n + i for i in range(n - 1, -1, -1)))
    for i in range(n):
        j = (i + 1) % n
        F.append((o + i, o + j, o + n + j, o + n + i))


def front_face():
    f = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south')
    pg = hole('ground porch', 0.0, F1, 2 * PW, 3.9 - F1)
    pu = hole('upper porch', 0.0, 4.5, 2 * PW, 2.7)
    wins = [hole(f'front window {s:+d} f{k}', s * 3.1, z, 1.35, 2.05) for k, z in ((0, F1 + .45), (1, F2 + .38)) for s in (-1, 1)]
    base = [hole(f'basement window {s:+d}', s * 3.1, .15, 1.1, .55) for s in (-1, 1)]
    holes = [pg, pu] + wins + base
    f.wall('south carrier', X0, X1 - EPS, 0.0, PAR, depth=T, role='wall', holes=holes)
    G.brick_courses(f, X0 + .02, X1 - .02, .5, PAR - .7, holes, spacing=.45)
    m = Merge(f)
    m.box('foundation', 0, -.03, .07, X1 - X0 - .02, .06, .14)
    for h in wins:
        stone_window(m, f, h, cols=2, rows=2)
        m.box('trim', h['u'], .1, h['z'] + h['h'] * .72, h['w'] - .1, .06, .07)               # transom bar
    for h in base:
        framed(m, f, h, cols=2, rows=1, inset=.13, occupied='basement')
    for s in (-1, 1):                                                                       # stone pilasters framing the porch
        m.box('quoin', s * (PW + .16), -.05, 3.85, .32, .1, 7.7)
    # One continuous bracketed cornice wrapping the east corner; above its middle a flush attic panel carries the cartouche.
    cornice_run(m, X0 - .1, X1, CZ, wrap=(False, True))
    m.box('stone', 0.0, -.05, PAR - .05, X1 - X0 - .1, .1, .1)                                # parapet coping band
    m.box('stone', 0.0, (-.62 + T + .04) / 2, CZ + .05 + ATT / 2, 2 * RC, T + .66, ATT)         # attic block on the cymatium
    m.box('stone', 0.0, (-.74 + T + .1) / 2, CZ + .05 + ATT + .05, 2 * RC + .24, T + .84, .12)  # attic cap cornice
    for s in (-1, 1):                                                                       # one scroll console each side, clear of the windows
        console(m, s * 2.15, CZ)
    m.flush('south')
    b = Batch()
    za = CZ + .05 + ATT / 2
    disc_y(b, 'quoin', 0.0, za, .26, Y0 - .7, Y0 - .6, 14)                                  # cartouche on the attic face: shield and scrolls
    disc_y(b, 'stone', 0.0, za, .17, Y0 - .76, Y0 - .69, 14)
    for s in (-1, 1):
        disc_y(b, 'quoin', s * .52, za - .05, .11, Y0 - .68, Y0 - .6, 10)
        b.beam('quoin', (s * .28, Y0 - .66, za - .2), (s * .82, Y0 - .66, za + .18), .1, .08)
    b.flush('cartouche')
    b = Batch()
    for k in range(int(PAR / .45)):                                                         # long-and-short quoins wrapping both corners
        L = .6 if k % 2 == 0 else .38
        z = .25 + k * .45
        for x, sx in ((X0, 1), (X1, -1)):
            b.box('quoin', x + sx * L / 2 - sx * .03, Y0 - .03, z, L + .06, .06, .41)
        L2 = .38 if k % 2 == 0 else .6
        b.box('quoin', X1 + .03, Y0 + L2 / 2, z, .06, L2, .41)
    b.flush('quoins')
    porch()


def porch():
    """The recessed two-storey porch: side walls, back wall with doors, ground slab and steps, balcony, canopy."""
    back = C.Face((0, Y0 + PD, 0), (1, 0, 0), (0, 1, 0), 'porch')
    gdoor = hole('lower flat door', .65, F1 + .02, 1.0, 2.35, kind='door')
    gwin = hole('porch window', -.85, F1 + .55, .9, 1.8)
    udoors = [hole(f'upper flat door {s:+d}', s * .6, F2 + .03, .8, 2.3, kind='door') for s in (-1, 1)]
    holes = [gdoor, gwin] + udoors
    back.wall('porch back wall', -PW, PW - EPS, 0.0, ROOF - .1, depth=.3, role='wall', holes=holes)
    m = Merge(back)
    m.box('green', gdoor['u'], .16, gdoor['z'] + gdoor['h'] / 2, gdoor['w'] - .02, .05, gdoor['h'] - .02)
    m.box('glass', gdoor['u'], .125, gdoor['z'] + 1.65, .5, .02, .8)
    register(back, gdoor, .14, 'lower flat door', 'lower flat')
    stone_window(m, back, gwin, occupied='lower flat', lintel=False)
    for h in udoors:
        framed(m, back, h, cols=1, rows=3, inset=.13, occupied='upper flat', kind='door', frame='red')
        m.box('red', h['u'], .15, h['z'] + .45, h['w'] - .1, .04, .75)
    m.flush('porch')
    b = Batch()
    for s in (-1, 1):
        b.box('wall', s * (PW + .15), (Y0 + T + Y0 + PD) / 2, (ROOF - .1) / 2, .3, PD - T, ROOF - .1)
    b.box('stone', 0.0, (Y0 - .4 + Y0 + PD) / 2, .91, 2 * PW + .2, PD + .4, .22)            # ground porch slab
    for k in range(4):                                                                      # front steps to the lower flat
        top = F1 - .2 * (k + 1) + .02
        b.box('stone', .85, Y0 - .4 - .14 - .28 * k, top / 2, 1.5, .28, top)
    b.box('stone', 0.0, (Y0 - .9 + Y0 + PD) / 2, F2 - .11, 2 * PW + .2, PD + .9, .22)        # upper balcony slab
    b.box('stone', 0.0, (Y0 + T + Y0 + PD) / 2, 7.33, 2 * PW, PD - T, .26)                  # porch ceiling (soffit at 7.2)
    b.box('stone', 0.0, Y0 - .525, 7.31, 2 * PW + .5, 1.05, .22)                            # canopy slab, one soffit plane with it
    b.box('stone', 0.0, Y0 - 1.06, 7.33, 2 * PW + .6, .1, .34)                              # canopy fascia
    for s in (-1, 1):
        b.box('stone', s * (PW + .28), Y0 - .53, 7.33, .1, 1.06, .34)
    # Iron: open lattice canopy columns (two uprights with crossed diagonals) and brackets clear of the soffit.
    for s in (-1, 1):
        x = s * (PW + .02)
        ya, yb = Y0 - 1.07, Y0 - .83
        for y in (ya, yb):
            b.box('hardware', x, y, (F2 + 7.2) / 2, .045, .045, 7.2 - F2)
        n = int((7.2 - F2 - .3) / .3)
        for i in range(n):
            z = F2 + .15 + i * .3
            b.beam('hardware', (x, ya, z), (x, yb, z + .3), .022, .022)
            b.beam('hardware', (x, yb, z), (x, ya, z + .3), .025, .022)
        for z in (F2 + .03, 7.17):
            b.box('hardware', x, (ya + yb) / 2, z, .12, .34, .06)
        b.beam('hardware', (x, Y0 - .95, 6.45), (x - s * .5, Y0 - .95, 7.15), .035, .035)
    rail(b, [(-PW - .05, Y0 - .85), (-1.5, Y0 - .85)], F2)
    rail(b, [(-.5, Y0 - .85), (PW + .05, Y0 - .85)], F2)
    for s in (-1, 1):
        rail(b, [(s * (PW + .05), Y0 - .85), (s * (PW + .05), Y0 - .02)], F2)
    rail(b, [(-PW + .05, Y0 - .35), (.05, Y0 - .35)], F1 + .02)
    b.flush('porch')
    stair(-1.0)


def rail(b, pts, z, h=1.0, spacing=.12):
    for (ax, ay), (cx, cy) in zip(pts, pts[1:]):
        L = math.hypot(cx - ax, cy - ay)
        b.beam('hardware', (ax, ay, z + h), (cx, cy, z + h), .045, .045, ext=.02)
        b.beam('hardware', (ax, ay, z + .1), (cx, cy, z + .1), .03, .03)
        n = max(2, int(L / spacing))
        for i in range(n + 1):
            px, py = ax + (cx - ax) * i / n, ay + (cy - ay) * i / n
            b.box('hardware', px, py, z + (h + .1) / 2 + .05, .02, .02, h - .1)


def stair(xs):
    """Black iron exterior stair: a straight open-riser flight from the balcony, curling clockwise at its foot."""
    b = Batch()
    rise, go, w = .2, .23, .9
    n1 = 10
    y_top = Y0 - .9
    outer_l, outer_r = [], []
    for k in range(1, n1 + 1):
        z = F2 - rise * k
        y = y_top - go * (k - .5)
        b.box('hardware', xs, y, z - .02, w, go + .02, .04)
        outer_l.append((xs - w / 2, y, z)); outer_r.append((xs + w / 2, y, z))
    zb = F2 - rise * n1
    for side in (outer_l, outer_r):
        p0 = (side[0][0], y_top, F2)
        pts = [p0] + side
        for a, c in zip(pts, pts[1:]):
            b.beam('hardware', (a[0], a[1], a[2] - .12), (c[0], c[1], c[2] - .12), .04, .2, ext=.01)
            b.beam('hardware', (a[0], a[1], a[2] + .9), (c[0], c[1], c[2] + .9), .045, .045, ext=.01)
        for p in pts[1:]:
            b.box('hardware', p[0], p[1], p[2] + .45, .02, .02, .9)
    # The curl: centre west of the flight foot, treads swept clockwise through south to the west.
    rin, rout = .25, 1.05
    cx, cy = xs - (rin + rout) / 2, y_top - go * n1 - .1
    n2 = 11
    rr = (2.47 - .0) / (n2 + 1)
    ring_o, ring_i = [], []
    for i in range(n2):
        a = -math.radians(200) * (i + .5) / n2
        z = zb - rr * (i + 1)
        dx, dy = math.cos(a), math.sin(a)
        b.beam('hardware', (cx + dx * rin, cy + dy * rin, z - .02), (cx + dx * rout, cy + dy * rout, z - .02), .3, .04)
        ring_o.append((cx + dx * rout, cy + dy * rout, z)); ring_i.append((cx + dx * rin, cy + dy * rin, z))
    pts = [outer_r[-1]] + ring_o
    for a, c in zip(pts, pts[1:]):
        b.beam('hardware', (a[0], a[1], a[2] + .9), (c[0], c[1], c[2] + .9), .045, .045, ext=.02)
        b.beam('hardware', (a[0], a[1], a[2] - .1), (c[0], c[1], c[2] - .1), .04, .16, ext=.02)
    for p in ring_o:
        b.box('hardware', p[0], p[1], p[2] + .45, .02, .02, .9)
    b.box('hardware', cx, cy, (zb + .4) / 2, .1, .1, zb + .4)                                # newel post at the curl's centre
    b.box('hardware', cx, cy, zb + .45, .16, .16, .1)
    b.flush('iron stair')


def side_and_rear():
    hd = (Y1 - Y0) / 2
    e = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    hs = [hole(f'east window f{k} {i}', u, z, .85, 1.9) for k, z in ((0, F1 + .5), (1, F2 + .45)) for i, u in enumerate((-3.6, 0.0, 3.6))]
    bs = [hole(f'east basement window {i}', u, .15, .8, .5) for i, u in enumerate((-3.6, 3.6))]
    e.wall('east carrier', -hd + T, hd - T, 0.0, 8.2, depth=T, role='brick', holes=hs + bs)
    G.brick_courses(e, -hd + T + .02, hd - T - .02, .3, 8.0, hs + bs, spacing=.2)
    m = Merge(e)
    m.box('foundation', 0, -.03, .07, 2 * hd - 2 * T - .02, .06, .14)
    for h in hs:
        stone_window(m, e, h, cols=1, rows=2)
    for h in bs:
        framed(m, e, h, cols=2, rows=1, inset=.13, occupied='basement')
    m.box('stone', 0.0, -.06, 8.2, 2 * hd - 2 * T + .1, .2, .12)                              # coping
    cornice_run(m, -hd, -hd + 1.4, CZ, behind=True)                                          # cornice return round the corner
    m.flush('east')
    w = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west party')
    w.wall('west party wall', -hd + T, hd - T, 0.0, 8.2, depth=T, role='brick', holes=[])
    n = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')
    hs = [hole(f'rear window f{k} {i}', u, z, .9, 1.8) for k, z in ((0, F1 + .5), (1, F2 + .45)) for i, u in enumerate((-2.6, 2.6))] + \
         [hole(f'rear door f{k}', 0.0, z, .9, 2.25, kind='door') for k, z in ((0, F1 + .02), (1, F2 + .03))]
    n.wall('north carrier', X0, X1 - EPS, 0.0, 8.2, depth=T, role='brick', holes=hs)
    m = Merge(n)
    for h in hs:
        framed(m, n, h, cols=1, rows=2, inset=.13, occupied='flat', kind=h.get('kind', 'window'), lite=True)
    m.box('stone', 0.0, -.06, 8.2, X1 - X0 + .1, .2, .12)
    m.flush('north')
    b = Batch()
    for z in (F1, F2):                                                                     # rear galleries
        b.box('timber', 0.0, Y1 + .6, z - .1, 3.0, 1.2, .16)
        rail(b, [(-1.5, Y1 + 1.15), (1.5, Y1 + 1.15)], z)
    b.box('hardware', -1.45, Y1 + 1.15, F2 / 2, .08, .08, F2)
    b.box('hardware', 1.45, Y1 + 1.15, F2 / 2, .08, .08, F2)
    b.flush('rear galleries')


def roof_and_inside():
    C.box('Roof deck', (0, 0, ROOF - .1), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .2), 'roof', 'roof', 0)
    b = Batch()
    for x in (-2.4, 0.0, 2.4):                                                             # three skylights
        b.box('pale', x, 2.2, ROOF + .12, 1.1, .9, .24)
        b.box('glass', x, 2.2, ROOF + .26, .9, .7, .05)
    b.box('pale', .6, 5.0, ROOF + .45, 1.0, 1.0, .9)                                         # roof hatch
    b.box('hardware', .6, 5.0, ROOF + .92, 1.1, 1.1, .06)
    for s in (-1, 1):
        b.box('hardware', .6 + s * .25, 4.45, ROOF + .55, .04, .04, 1.1)
    for k in range(4):
        b.box('hardware', .6, 4.45, ROOF + .2 + k * .25, .5, .03, .03)
    b.box('brick', -3.4, 5.6, ROOF + .6, .7, .5, 1.2)                                          # party-wall flue
    b.flush('roof furniture')
    for z in (F1, F2):
        C.box(f'Floor {z:.1f}', (0, (Y0 + PD + .26 + Y1 - T + .04) / 2, z - .14), (X1 - X0 - 2 * T + .08, Y1 - T - Y0 - PD - .22, .24), 'floor', 'inside', 0)
        for s in (-1, 1):
            C.box(f'Bay floor {z:.1f} {s:+d}', (s * (X1 - T + .04 + PW + .26) / 2, (Y0 + T - .04 + Y0 + PD + .3) / 2, z - .14), (X1 - T - PW - .22, PD + .34 - T, .24), 'floor', 'inside', 0)
    for z in (F1, F2):
        for x in (-3.0, 3.0):
            C.qa_room_light(f'Room {x:+.0f} {z:.0f}', (x, Y0 + 2.0, z + 1.9), 45, 2.2)
        C.qa_room_light(f'Hall {z:.0f}', (0.0, Y0 + PD + 1.4, z + 1.9), 30, 1.6)
    C.qa_room_light('Basement', (0.0, Y0 + 2.5, .5), 25, 2.0)
    C.CONTACTS.append(dict(name='Stone front and brick side walls from grade; bracketed cornice on the front wall; flat roof inside the parapets', roof_m=ROOF))


def site():
    yf = Y0 - 4.8
    C.box('Front yard paving', (0.0, (yf + Y0) / 2, .02), (X1 - X0, Y0 - yf, .04), 'concrete', 'site', 0)
    C.box('Front lawn west', (X0 + 1.0, (yf + Y0) / 2 - .4, .05), (1.8, Y0 - yf - 1.2, .02), 'lawn', 'site', 0)
    C.box('Front lawn east', (X1 - 1.0, (yf + Y0) / 2 - .4, .05), (1.8, Y0 - yf - 1.2, .02), 'lawn', 'site', 0)
    C.box('South sidewalk', (2.0, yf - 1.2, .06), (40.0, 2.4, .12), 'concrete', 'site', 0)
    C.box('East sidewalk', (X1 + 1.3, (yf + Y1 + 8.0) / 2, .06), (2.6, Y1 + 8.0 - yf, .12), 'concrete', 'site', 0)
    C.box('South street', (2.0, yf - 6.4, .01), (40.0, 8.0, .02), 'asphalt', 'site', 0)
    C.box('East lane', (X1 + 5.6, 4.0, .01), (6.0, 30.0, .02), 'asphalt', 'site', 0)
    b = Batch()
    fence(b, (X0, yf + .15), (-2.3, yf + .15))
    fence(b, (-1.2, yf + .15), (X1 - .1, yf + .15))
    fence(b, (X1 - .1, yf + .15), (X1 - .1, Y0 - .05))
    for k in range(-24, 28):
        b.box('joint', k * 1.5, yf - 1.2, .121, .02, 2.38, .004)
    b.flush('fence and sidewalks')
    street_tree(-6.5, yf - 1.5, z=.12, height=9.0, spread=2.6)
    street_tree(X1 + 1.3, 9.0, z=.12, height=8.5, spread=2.4)
    # The attached brick plex to the west, as context: its east wall buried in ours.
    nx0, nx1 = X0 - 7.5, X0 + .15
    C.box('Neighbour plex', ((nx0 + nx1) / 2, (Y0 + .3 + Y1 - .5) / 2, 4.2), (nx1 - nx0, Y1 - Y0 - .8, 8.4), 'neighbour', 'context', 0)
    b = Batch()
    for k, z in enumerate((1.5, 4.9)):
        for u in (nx0 + 1.4, nx0 + 3.6, nx0 + 5.8):
            b.box('glass', u, Y0 + .28, z + 1.0, 1.1, .04, 1.9)
            b.box('pale', u, Y0 + .27, z - .05, 1.3, .06, .1)
    b.box('stone', (nx0 + nx1) / 2, Y0 + .1, 8.2, nx1 - nx0 - .2, .5, .3)
    b.flush('neighbour')


def build():
    site()
    front_face()
    side_and_rear()
    roof_and_inside()
    C.CONTACTS.append(dict(name='Corner Plateau plex with exterior iron stair, front yard and attached neighbour west', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(30, -40, 30), fill=(-40, -20, 25), rear=(-15, 30, 25), target=(0, -1.0, 4.0), gain=3.3)
