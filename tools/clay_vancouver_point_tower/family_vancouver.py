"""Vancouverism point tower on a curved podium, authored from the locked catalogue views of
vancouverism_tower_podium / variant_0 (vancouverism_classic).

Read from the pixels (the top view governs the plan): a corner block with streets south, west and
east. A three-storey pale concrete podium with rounded south corners: a colonnade of round columns in
front of recessed shopfront glazing, two storeys of windows between concrete frames and red-brick
infill panels, a continuous balcony at the second storey, a white curved parapet band with a glass
guard round a planted roof terrace; a two-storey east wing with a green roof. On the podium's north
half a glass residential tower with rounded corners: a blue-green curtain wall with white floor
bands, close white vertical fins on its western half, stacked balconies with glass fronts on the
eastern half of the south face and along the east face, and white sweeping blades that rise from the
podium up the south face and flare outward at their feet. A white roof band frames a planted roof
terrace round a pale mechanical penthouse.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-vancouver-point-tower'
T = .30
G0 = .15
PX0, PX1, PY0, PY1 = -24.0, 16.0, -22.0, 20.0     # podium main block
PR = 6.0                                          # podium corner radius (south corners)
EW = (16.0, 34.0, -12.0, 16.0)                    # east wing, two storeys, green roof
TX0, TX1, TY0, TY1 = -18.0, 14.0, -6.0, 18.0      # tower
TR = 4.0                                          # tower corner radius
P_LEVELS = [G0, 5.0, 8.5]
P_TOP = 12.0
EW_TOP = 8.5
FH = 3.0
N = 14
T_LEVELS = [P_TOP + i * FH for i in range(N)]
T_TOP = P_TOP + N * FH                            # 54.0
EPS = .002
PALETTE = dict(wall=(.55, .30, .23), joint=(.42, .22, .17), trim=(.24, .26, .28),
    pale=(.88, .88, .86), stone=(.76, .75, .72), roof=(.70, .69, .66), sand=(.70, .67, .62),
    foundation=(.42, .42, .41), glass=(.42, .56, .60), hardware=(.26, .27, .29),
    interior=(.82, .80, .76), floor=(.50, .48, .46), timber=(.46, .32, .20), blue=(.16, .30, .38),
    planting=(.28, .44, .18), soil=(.22, .16, .10), concrete=(.78, .77, .74), white=(.93, .93, .91),
    asphalt=(.30, .30, .31), membrane=(.74, .73, .70), greenroof=(.40, .48, .22))


def manifest(version):
    h = T_TOP + 4.5
    cams = G.camera_roster(58.0, 44.0, h, [
        ('facade_close', (-4.0, -40.0, 30.0), (-4.0, TY0, 30.0), 45),
        ('architecture_close', (14.0, -40.0, 10.0), (PX1 - 4.0, PY0, 8.0), 45),
        ('glass_close', (-12.0, -26.0, 20.0), (-10.0, TY0, 22.0), 45),
        ('podium_colonnade', (-6.0, -34.0, 2.0), (-6.0, PY0, 3.4), 45),
        ('balcony_stack', (24.0, -28.0, 30.0), (TX1 - 2.0, TY0, 30.0), 45),
        ('sweep_blade', (-30.0, -30.0, 16.0), (-14.0, TY0 - 2.0, 18.0), 45),
        ('podium_terrace', (-24.0, -36.0, 24.0), (-4.0, -14.0, P_TOP), 45),
        ('roof_garden', (26.0, -26.0, 72.0), (-2.0, 6.0, T_TOP), 45),
        ('interior', (6.0, 4.0, T_LEVELS[6] + 1.6), (6.0, TY0 - 2.0, T_LEVELS[6] + 1.2), 60),
        ('east_wing', (48.0, 6.0, 16.0), (EW[1], 2.0, 5.0), 45)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='vancouverism_tower_podium/variant_0 (vancouverism_classic)',
        measurement_contract=dict(dimensions_m=dict(width=58.0, depth=42.0, height=h),
            observed_storeys=3 + N, storey_programme='three-storey podium (retail colonnade, two storeys of flats), fourteen tower storeys, mechanical penthouse',
            plan='podium 40 x 42 m with 6 m rounded south corners; east wing 18 x 28 m of two storeys; tower 32 x 24 m with 4 m rounded corners on the podium north half, leaving a 16 m roof terrace to the south (top view)',
            facade='podium: round columns before recessed glazing, concrete frame with brick infill and windows, continuous second-storey balcony, white curved parapet with glass guard; tower: curtain wall with white floor bands, white fins at 1.2 m on the western half, stacked glass-fronted balconies on the eastern half and the east face, three white sweeping blades on the south face',
            levels_m=P_LEVELS + T_LEVELS + [T_TOP],
            inferred='the catalogue range is 25-60 storeys but the locked views show fourteen tower storeys over the podium, so the pixels govern; storey heights and interiors are teaching assumptions; the north face is not visible in any source'),
        roof_contract=dict(type='flat: planted podium terrace, green roof on the east wing, planted tower roof terrace round a penthouse', datum_m=T_TOP, crowns_m=[P_TOP + 1.1, T_TOP + 1.2, T_TOP + 4.0]),
        identity_contract=dict(owner='slender rounded glass tower with white sweeping blades and fins over a curved concrete podium with a colonnade and roof garden, stacked glass balconies'),
        material_contract=dict(profile='source-palette clay: blue-green glass, white bands, fins and blades, pale concrete podium with red-brick infill, glass guards, planting', textured_keeper=False),
        programme_contract=dict(storeys=3 + N, ground='retail and lobby behind the colonnade', podium='townhouse flats', tower='six flats per floor', roof='amenity terrace and penthouse plant'),
        contact_contract=['Grade-zero slab and sidewalks', 'Tower on the podium slab', 'Blades fixed to the tower face and bearing on the podium roof', 'Balcony slabs cast with the floor slabs', 'Penthouse on the tower roof'],
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


# ---- Vancouverism point tower ----

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


def arc_band(name, cx, cy, r0, r1, a0, a1, z0, z1, role, module, segs=10):
    """Solid ring sector between radii r0 and r1, angles a0 to a1, from z0 to z1."""
    vs = []
    for i in range(segs + 1):
        a = a0 + (a1 - a0) * i / segs
        for r in (r0, r1):
            for z in (z0, z1):
                vs.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    fs = []
    for i in range(segs):
        o, q = 4 * i, 4 * (i + 1)
        fs += [(o + 2, q + 2, q + 3, o + 3), (o + 0, o + 1, q + 1, q + 0), (o + 1, o + 3, q + 3, q + 1), (o + 0, q + 0, q + 2, o + 2)]
    fs += [(0, 2, 3, 1), (4 * segs, 4 * segs + 1, 4 * segs + 3, 4 * segs + 2)]
    return C.mesh(name, vs, fs, role, module)


def rounded_rect(x0, x1, y0, y1, r, corners=('sw', 'se', 'ne', 'nw'), segs=6):
    pts = []
    for key, cx, cy, a0 in (('sw', x0 + r, y0 + r, math.pi), ('se', x1 - r, y0 + r, 1.5 * math.pi), ('ne', x1 - r, y1 - r, 0.0), ('nw', x0 + r, y1 - r, .5 * math.pi)):
        if key in corners:
            pts += [(cx + r * math.cos(a0 + math.pi / 2 * i / segs), cy + r * math.sin(a0 + math.pi / 2 * i / segs)) for i in range(segs + 1)]
        else:
            pts.append({'sw': (x0, y0), 'se': (x1, y0), 'ne': (x1, y1), 'nw': (x0, y1)}[key])
    return pts


def slab(name, pts, z, t, role='floor', module='floors'):
    C.prism(name, pts, 'z', z - t, z, role, module)


def window_face(f, lo, hi, levels, top, bay=4.0, brick_every=3, ground='storefront', role='concrete', courses=False):
    """Concrete frame elevation: ground storefronts, windows per bay above, brick infill panels on every third bay."""
    span = hi - lo
    n = max(1, round(span / bay))
    pitch = span / n
    holes, bricks = [], []
    for i in range(n):
        u = lo + pitch * (i + .5)
        if ground == 'storefront':
            holes.append(hole(f'{f.label} storefront {i}', u, G0, pitch - .8, levels[1] - .55 - G0, kind='storefront'))
        elif ground == 'window':
            holes.append(hole(f'{f.label} ground window {i}', u, 1.0, pitch - 1.4, 2.6))
        for k, z in enumerate(levels[1:]):
            if brick_every and i % brick_every == 1:
                bricks.append((u, z))
                holes.append(hole(f'{f.label} f{k + 2} narrow window {i}', u + pitch * .3, z + .5, .8, 2.3))
            else:
                holes.append(hole(f'{f.label} f{k + 2} window {i}', u, z + .5, pitch - 1.2, 2.3))
    f.wall(f'{f.label} carrier', lo, hi - EPS, G0, top, depth=T, role=role, holes=holes)
    m = Merge(f)
    for h in holes:
        if h.get('kind') == 'storefront':
            framed(m, f, h, cols=max(2, round(h['w'] / 1.5)), rows=2, inset=.16, occupied='retail', kind='storefront')
        else:
            framed(m, f, h, cols=2 if h['w'] > 1.2 else 1, inset=.14, occupied='flat')
    for u, z in bricks:                                                    # red-brick infill panels
        m.box('wall', u - pitch * .12, -.04, z + 1.6, pitch * .55, .08, 2.9)
    for z in levels[1:]:
        m.box('concrete', (lo + hi) / 2, -.06, z, hi - lo - 2 * EPS, T + .12, .3)
    m.flush(f.label)
    return holes


def podium():
    x0, x1, y0, y1 = PX0, PX1, PY0, PY1
    ptop = P_TOP + 1.1
    # South face: upper storeys on the face line, ground glazing set back behind a colonnade.
    sx0, sx1 = x0 + PR, x1 - PR
    up = C.Face(((sx0 + sx1) / 2, y0, 0), (1, 0, 0), (0, 1, 0), 'podium south')
    hw = (sx1 - sx0) / 2
    n = 7
    holes = []
    for i in range(n):
        u = -hw + 2 * hw * (i + .5) / n
        for k, z in enumerate(P_LEVELS[1:]):
            if i % 3 == 1:
                holes.append(hole(f'podium south f{k + 2} narrow {i}', u + 1.2, z + .5, .8, 2.3))
            else:
                holes.append(hole(f'podium south f{k + 2} window {i}', u, z + .5, 2.6, 2.3))
    up.wall('podium south upper carrier', -hw, hw - EPS, P_LEVELS[1] - .4, ptop, depth=T, role='concrete', holes=holes)
    m = Merge(up)
    for h in holes:
        framed(m, up, h, cols=2 if h['w'] > 1.2 else 1, inset=.14, occupied='flat')
    for i in range(n):
        if i % 3 == 1:
            u = -hw + 2 * hw * (i + .5) / n
            for z in P_LEVELS[1:]:
                m.box('wall', u - .5, -.04, z + 1.6, 2.2, .08, 2.9)
    m.box('concrete', 0, -.6, P_LEVELS[2] - .1, 2 * hw - .02, 1.2, .22)                   # continuous second-storey balcony
    m.box('hardware', 0, -1.15, P_LEVELS[2] + 1.0, 2 * hw - .02, .05, .05)
    m.box('glass', 0, -1.15, P_LEVELS[2] + .5, 2 * hw - .04, .02, .9)
    m.box('white', 0, -.08, ptop - .45, 2 * hw - .02, T + .16, .9)                       # white parapet band
    m.flush('podium south')
    gr = C.Face(((sx0 + sx1) / 2, y0 + 1.6, 0), (1, 0, 0), (0, 1, 0), 'podium south shopfront')
    gholes = [hole(f'podium shopfront {i}', -hw + 2 * hw * (i + .5) / n, G0, 2 * hw / n - .5, P_LEVELS[1] - .65 - G0, kind='storefront') for i in range(n)]
    gr.wall('podium shopfront carrier', -hw, hw - EPS, G0, P_LEVELS[1] - .4, depth=T, role='concrete', holes=gholes)
    m = Merge(gr)
    for h in gholes:
        framed(m, gr, h, cols=3, rows=2, inset=.12, occupied='retail', kind='storefront')
    m.flush('podium shopfront')
    C.box('Colonnade soffit', ((sx0 + sx1) / 2, y0 + .8 + T / 2, P_LEVELS[1] - .3), (sx1 - sx0, 1.6 - T, .2), 'pale', 'podium', 0)
    for i in range(n + 1):
        C.rod('Colonnade column', (sx0 + (sx1 - sx0) * i / n, y0 + .45, G0), (sx0 + (sx1 - sx0) * i / n, y0 + .45, P_LEVELS[1] - .4), .28, 'concrete', 'podium', 14)
    # Rounded south corners: glazed upper storeys between concrete floor bands, white parapet arc, balcony arc, colonnade.
    for cx, a0 in ((x0 + PR, math.pi), (x1 - PR, 1.5 * math.pi)):
        cy = y0 + PR
        a1 = a0 + math.pi / 2
        arc_band('Podium corner glass', cx, cy, PR - .12, PR - .1, a0, a1, P_LEVELS[1] - .4, ptop - .9, 'glass', 'podium corners')
        for z in P_LEVELS[1:]:
            arc_band('Podium corner floor band', cx, cy, PR - .4, PR + .06, a0, a1, z - .15, z + .15, 'concrete', 'podium corners')
        arc_band('Podium corner balcony', cx, cy, PR - .2, PR + 1.2, a0, a1, P_LEVELS[2] - .21, P_LEVELS[2] + .01, 'concrete', 'podium corners')
        arc_band('Podium corner balcony glass', cx, cy, PR + 1.14, PR + 1.16, a0, a1, P_LEVELS[2] + .05, P_LEVELS[2] + .95, 'glass', 'podium corners')
        arc_band('Podium corner balcony rail', cx, cy, PR + 1.12, PR + 1.18, a0, a1, P_LEVELS[2] + .97, P_LEVELS[2] + 1.03, 'hardware', 'podium corners')
        arc_band('Podium corner parapet', cx, cy, PR - .3, PR + .08, a0, a1, ptop - .9, ptop, 'white', 'podium corners')
        arc_band('Podium corner shopfront', cx, cy, PR - 1.62, PR - 1.6, a0, a1, G0, P_LEVELS[1] - .4, 'glass', 'podium corners')
        arc_band('Podium corner soffit', cx, cy, PR - 1.6, PR - .1, a0, a1, P_LEVELS[1] - .4, P_LEVELS[1] - .2, 'pale', 'podium corners')
        for k in range(1, 3):
            a = a0 + (a1 - a0) * k / 3
            C.rod('Colonnade column', (cx + (PR - .45) * math.cos(a), cy + (PR - .45) * math.sin(a), G0), (cx + (PR - .45) * math.cos(a), cy + (PR - .45) * math.sin(a), P_LEVELS[1] - .4), .28, 'concrete', 'podium', 14)
        for k in range(7):
            a = a0 + (a1 - a0) * (k + .5) / 7
            C.box('Podium corner mullion', (cx + (PR - .05) * math.cos(a), cy + (PR - .05) * math.sin(a), (P_LEVELS[1] + ptop - .9) / 2), (.08, .08, ptop - .9 - P_LEVELS[1] + .4), 'trim', 'podium corners', 0)
    # West, north and east faces.
    w = C.Face((x0, (y0 + PR + y1) / 2, 0), (0, -1, 0), (1, 0, 0), 'podium west')
    hd = (y1 - y0 - PR) / 2
    window_face(w, -hd + T, hd, P_LEVELS, ptop, ground='storefront')
    nf = C.Face(((x0 + x1) / 2, y1, 0), (-1, 0, 0), (0, -1, 0), 'podium north')
    window_face(nf, -(x1 - x0) / 2, (x1 - x0) / 2, P_LEVELS, ptop, ground='window')
    e1 = C.Face((x1, (y0 + PR + EW[2]) / 2, 0), (0, 1, 0), (-1, 0, 0), 'podium east south')
    d1 = (EW[2] - y0 - PR) / 2
    window_face(e1, -d1, d1, P_LEVELS, ptop, bay=4.0, brick_every=0)
    e2 = C.Face((x1, (EW[2] + EW[3]) / 2, 0), (0, 1, 0), (-1, 0, 0), 'podium east upper')
    d2 = (EW[3] - EW[2]) / 2
    e2h = [hole(f'podium east upper window {i}', -d2 + 4.0 * (i + .5), EW_TOP + .6, 2.4, 2.3) for i in range(7)]
    e2.wall('podium east upper carrier', -d2, d2, EW_TOP, ptop, depth=T, role='concrete', holes=e2h)
    m = Merge(e2)
    for h in e2h:
        framed(m, e2, h, cols=2, inset=.14, occupied='flat')
    m.flush('podium east upper')
    e3 = C.Face((x1, (EW[3] + y1 - T) / 2, 0), (0, 1, 0), (-1, 0, 0), 'podium east north')
    d3 = (y1 - T - EW[3]) / 2
    window_face(e3, -d3, d3, P_LEVELS, ptop, bay=3.7, brick_every=0, ground='window')
    for f, span in ((w, 2 * hd - T), (nf, x1 - x0), (e1, 2 * d1), (e3, 2 * d3)):
        C.box(f.label + ' parapet band', tuple(f.p(0, -.08, ptop - .45)), (abs(f.t[0]) * span + abs(f.t[1]) * (T + .16), abs(f.t[1]) * span + abs(f.t[0]) * (T + .16), .9), 'white', 'podium', 0)
    # Slabs and the planted podium roof terrace.
    outline = rounded_rect(x0, x1, y0, y1, PR, corners=('sw', 'se'))
    C.prism('Podium ground slab', outline, 'z', 0, G0, 'foundation', 'podium')
    inner = rounded_rect(x0 + T, x1 - T, y0 + T, y1 - T, PR - T, corners=('sw', 'se'))
    for z in P_LEVELS[1:]:
        slab('Podium floor', inner, z, .3)
    slab('Podium roof slab', inner, P_TOP, .3)
    C.prism('Podium terrace paving', inner, 'z', P_TOP, P_TOP + .02, 'sand', 'podium terrace')
    for x, y, w_, d_ in ((-19.0, -16.0, 6.0, 1.6), (-8.0, -18.0, 7.0, 1.6), (4.0, -18.0, 6.0, 1.6), (-20.0, -4.0, 1.6, 7.0), (11.5, -12.0, 1.6, 6.0), (-6.0, -11.0, 4.0, 3.0)):
        C.box('Podium planter', (x, y, P_TOP + .4), (w_, d_, .8), 'concrete', 'podium terrace', 0)
        C.box('Podium planter planting', (x, y, P_TOP + .82), (w_ - .2, d_ - .2, .04), 'planting', 'podium terrace', 0)
        for k in range(max(1, int(max(w_, d_) / 2.0))):
            A.shrub(x + (k - (max(w_, d_) / 2.0 - 1) / 2) * (2.0 if w_ > d_ else 0), y + (k - (max(w_, d_) / 2.0 - 1) / 2) * (2.0 if d_ > w_ else 0), P_TOP + .84, .8)
    A.small_tree(-6.0, -11.0, P_TOP + .84, 3.2, 1.4)
    for x in (-14.0, -2.0, 8.0):
        C.qa_room_light(f'Podium retail {x:+.0f}', (x, y0 + 5.0, P_LEVELS[1] - .6), 120, 5.0)
        C.qa_room_light(f'Podium flats {x:+.0f}', (x, y0 + 4.0, P_LEVELS[2] - .5), 60, 5.0)


def east_wing():
    x0, x1, y0, y1 = EW
    s = C.Face(((x0 + x1) / 2, y0, 0), (1, 0, 0), (0, 1, 0), 'east wing south')
    window_face(s, -(x1 - x0) / 2, (x1 - x0) / 2, P_LEVELS[:2], EW_TOP + .9, bay=3.6, brick_every=0, ground='storefront')
    e = C.Face((x1, (y0 + y1) / 2, 0), (0, 1, 0), (-1, 0, 0), 'east wing east')
    window_face(e, -(y1 - y0) / 2 + T, (y1 - y0) / 2 - T, P_LEVELS[:2], EW_TOP + .9, bay=3.6, brick_every=2, ground='storefront')
    n = C.Face(((x0 + x1) / 2, y1, 0), (-1, 0, 0), (0, -1, 0), 'east wing north')
    window_face(n, -(x1 - x0) / 2, (x1 - x0) / 2, P_LEVELS[:2], EW_TOP + .9, bay=3.6, brick_every=0, ground='window')
    for f, span in ((s, x1 - x0), (e, y1 - y0 - 2 * T), (n, x1 - x0)):
        C.box(f.label + ' parapet band', tuple(f.p(0, -.06, EW_TOP + .45)), (abs(f.t[0]) * span + abs(f.t[1]) * (T + .12), abs(f.t[1]) * span + abs(f.t[0]) * (T + .12), .9), 'white', 'east wing', 0)
        for k in range(int(span / 3.6)):
            u = -span / 2 + 3.6 * (k + .5)
            C.box('East wing awning', tuple(f.p(u, -.8, P_LEVELS[1] - .9)), (abs(f.t[0]) * 2.8 + abs(f.t[1]) * 1.6, abs(f.t[1]) * 2.8 + abs(f.t[0]) * 1.6, .12), 'blue', 'east wing', 0)
    C.box('East wing ground slab', ((x0 + x1) / 2, (y0 + y1) / 2, G0 / 2), (x1 - x0, y1 - y0, G0), 'foundation', 'east wing', 0)
    C.box('East wing floor', ((x0 + x1) / 2, (y0 + y1) / 2, P_LEVELS[1] - .15), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .3), 'floor', 'east wing', 0)
    C.box('East wing roof', ((x0 + x1) / 2, (y0 + y1) / 2, EW_TOP - .15), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .3), 'floor', 'east wing', 0)
    C.box('East wing green roof', ((x0 + x1) / 2, (y0 + y1) / 2, EW_TOP + .04), (x1 - x0 - 2 * T - .02, y1 - y0 - 2 * T - .02, .08), 'greenroof', 'east wing', 0)
    C.box('East wing stair house', (x1 - 4.0, y0 + 6.0, EW_TOP + 1.3), (4.0, 5.0, 2.6), 'pale', 'east wing', 0)
    for y in (2.0, 8.0):
        C.box('East wing skylight', (x0 + 7.0, y, EW_TOP + .25), (1.6, 1.6, .5), 'glass', 'east wing', 0)
    C.qa_room_light('East wing shops', ((x0 + x1) / 2, y0 + 4.0, P_LEVELS[1] - .6), 100, 5.0)


def tower():
    x0, x1, y0, y1 = TX0, TX1, TY0, TY1
    faces = (('south', C.Face(((x0 + x1) / 2, y0, 0), (1, 0, 0), (0, 1, 0), 'tower south'), (x1 - x0) / 2 - TR),
             ('north', C.Face(((x0 + x1) / 2, y1, 0), (-1, 0, 0), (0, -1, 0), 'tower north'), (x1 - x0) / 2 - TR),
             ('east', C.Face((x1, (y0 + y1) / 2, 0), (0, 1, 0), (-1, 0, 0), 'tower east'), (y1 - y0) / 2 - TR),
             ('west', C.Face((x0, (y0 + y1) / 2, 0), (0, -1, 0), (1, 0, 0), 'tower west'), (y1 - y0) / 2 - TR))
    for side, f, hw in faces:
        holes = [hole(f'{f.label} glazing f{i}', 0, z + .55, 2 * hw - .4, FH - .75, kind='band') for i, z in enumerate(T_LEVELS)]
        f.wall(f.label + ' spandrel carrier', -hw, hw - EPS, P_TOP, T_TOP, depth=T, role='white', holes=holes)
        m = Merge(f)
        for h in holes:
            m.box('glass', h['u'], .12, h['z'] + h['h'] / 2, h['w'] - .02, .012, h['h'] - .02)
            register(f, h, .1, 'curtain wall', 'flats')
            for k in range(1, int(h['w'] / 1.5)):
                m.box('trim', h['u'] - h['w'] / 2 + h['w'] * k / int(h['w'] / 1.5), .06, h['z'] + h['h'] / 2, .05, .08, h['h'])
        fin_lo, fin_hi = {'south': (-hw, -2.0), 'west': (-hw, hw), 'north': (-hw, hw), 'east': (0, 0)}[side]
        u = fin_lo + .6
        while u < fin_hi - .3:
            m.box('white', u, -.28, (P_TOP + T_TOP) / 2, .1, .5, T_TOP - P_TOP)               # white vertical fins
            u += 1.2
        if side in ('south', 'east'):
            spans = [(2.0, hw)] if side == 'south' else [(-hw, hw)]
            for a, b in spans:
                for z in T_LEVELS[1:] + [T_TOP]:
                    if z >= T_TOP:
                        continue
                    m.box('white', (a + b) / 2, -.9, z - .1, b - a, 1.8, .22)
                    m.box('glass', (a + b) / 2, -1.76, z + .55, b - a - .1, .03, 1.0)
                    m.box('hardware', (a + b) / 2, -1.76, z + 1.08, b - a - .05, .05, .05)
                    for e in (a + .05, b - .05):
                        m.box('glass', e, -.95, z + .55, .03, 1.6, 1.0)
        m.box('white', 0, -.08, T_TOP + .6, 2 * hw - .02, T + .16, 1.2)                        # roof band
        m.flush(f.label)
    # Rounded corners: glass between white floor bands, roof band arcs.
    for cx, cy, a0 in ((x0 + TR, y0 + TR, math.pi), (x1 - TR, y0 + TR, 1.5 * math.pi), (x1 - TR, y1 - TR, 0.0), (x0 + TR, y1 - TR, .5 * math.pi)):
        a1 = a0 + math.pi / 2
        arc_band('Tower corner glass', cx, cy, TR - .14, TR - .12, a0, a1, P_TOP, T_TOP, 'glass', 'tower corners')
        for z in T_LEVELS + [T_TOP]:
            arc_band('Tower corner floor band', cx, cy, TR - .35, TR + .02, a0, a1, z - .12 if z < T_TOP else z - .3, z + .2 if z < T_TOP else z, 'white', 'tower corners')
        arc_band('Tower corner roof band', cx, cy, TR - .3, TR + .08, a0, a1, T_TOP, T_TOP + 1.2, 'white', 'tower corners')
        for k in range(5):
            a = a0 + (a1 - a0) * (k + .5) / 5
            C.box('Tower corner mullion', (cx + (TR - .08) * math.cos(a), cy + (TR - .08) * math.sin(a), (P_TOP + T_TOP) / 2), (.07, .07, T_TOP - P_TOP), 'trim', 'tower corners', 0)
    # White sweeping blades on the south face, flaring out at their feet on the podium roof.
    for bx in (x0 + TR - .3, 0.0, x1 - TR + .3):
        pts_out = []
        for i in range(13):
            z = P_TOP + (T_TOP + 1.2 - P_TOP) * i / 12
            d = .9 + 3.6 * math.exp(-(z - P_TOP) / 8.0)
            pts_out.append((y0 - d, z))
        poly = pts_out + [(y0 - .02, T_TOP + 1.2), (y0 - .02, P_TOP)]
        C.prism('Sweeping blade', poly, 'x', bx - .22, bx + .22, 'white', 'blades')
    # Floors, interiors, roof terrace and penthouse.
    inner = rounded_rect(x0 + T, x1 - T, y0 + T, y1 - T, TR - T)
    for i, z in enumerate(T_LEVELS[1:] + [T_TOP]):
        slab(f'Tower floor {i + 1}', inner, z, .3)
    C.box('Tower core', ((x0 + x1) / 2 - 2.0, (y0 + y1) / 2 + 3.0, (P_TOP + T_TOP) / 2), (8.0, 6.0, T_TOP - P_TOP), 'concrete', 'core', 0)
    for i, z in enumerate(T_LEVELS[::2]):
        C.qa_room_light(f'Tower flats {i}', ((x0 + x1) / 2, y0 + 3.0, z + FH - .5), 60, 6.0)
    zf = T_LEVELS[6]
    A.sofa(4.0, y0 + 2.6, zf); A.desk(10.0, y0 + 2.4, zf); A.bed(-10.0, y0 + 3.0, zf)
    C.prism('Tower roof paving', inner, 'z', T_TOP, T_TOP + .02, 'sand', 'roof garden')
    for x, y, w_, d_ in ((-13.0, 0.0, 1.4, 8.0), (11.0, 2.0, 1.4, 8.0), (-6.0, -3.2, 8.0, 1.4), (6.0, 16.4, 8.0, 1.2), (-12.0, 15.0, 4.0, 1.4), (9.0, -3.2, 5.0, 1.4)):
        C.box('Roof planter', (x, y, T_TOP + .35), (w_, d_, .7), 'concrete', 'roof garden', 0)
        C.box('Roof planter planting', (x, y, T_TOP + .72), (w_ - .2, d_ - .2, .04), 'planting', 'roof garden', 0)
        A.shrub(x, y, T_TOP + .74, .9)
    C.box('Roof penthouse', (-2.0, 9.0, T_TOP + 1.8), (14.0, 12.0, 3.6), 'pale', 'penthouse', 0)
    C.box('Roof penthouse green lid', (-.5, 10.0, T_TOP + 3.65), (3.0, 3.0, .1), 'greenroof', 'penthouse', 0)
    for k in range(5):
        C.box('Penthouse louvre', (5.06, 9.0, T_TOP + .8 + k * .5), (.12, 10.0, .14), 'hardware', 'penthouse', 0)
    for x, y in ((-6.0, 6.0), (-4.0, 12.0), (2.0, 5.0)):
        C.box('Penthouse unit', (x, y, T_TOP + 3.9), (1.2, 1.0, .6), 'membrane', 'penthouse', 0)
    C.CONTACTS.append(dict(name='Tower on the podium slab; blades bear on the podium roof; balconies cast with the slabs', tower=[x0, x1, y0, y1]))


def site():
    C.box('South sidewalk', (5.0, PY0 - 3.0, .07), (66.0, 6.0, .14), 'concrete', 'site', 0)
    C.box('West sidewalk', (PX0 - 3.0, (PY0 + PY1) / 2, .07), (6.0, PY1 - PY0, .14), 'concrete', 'site', 0)
    C.box('East sidewalk', (EW[1] + 2.6, (PY0 + PY1) / 2, .07), (5.2, PY1 - PY0, .14), 'concrete', 'site', 0)
    C.box('East wing forecourt', ((PX1 + EW[1]) / 2, (PY0 + EW[2]) / 2, .07), (EW[1] - PX1, EW[2] - PY0, .14), 'sand', 'site', 0)
    C.box('South street', (5.0, PY0 - 12.0, .01), (80.0, 12.0, .02), 'asphalt', 'site', 0)
    C.box('West street', (PX0 - 12.0, (PY0 + PY1) / 2, .01), (12.0, PY1 - PY0, .02), 'asphalt', 'site', 0)
    for x in (-18.0, -6.0, 6.0, 20.0, 30.0):
        street_tree(x, PY0 - 2.2, z=.14, height=7.0, spread=1.6)
    for y in (-10.0, 4.0, 16.0):
        street_tree(PX0 - 2.2, y, z=.14, height=7.0, spread=1.6)
    for x in (-12.0, 12.0):
        C.rod('Street lamp', (x, PY0 - 4.6, .14), (x, PY0 - 4.6, 7.5), .08, 'hardware', 'site', 8)
        C.beam('Street lamp arm', (x, PY0 - 4.6, 7.4), (x, PY0 - 2.6, 7.4), .06, .06, 'hardware', 'site')


def build():
    site()
    podium()
    east_wing()
    tower()


LIGHT_RIG = dict(key=(-80, -90, 100), fill=(90, -40, 70), rear=(-30, 90, 90), target=(0, 0, 24.0), gain=28.0)
