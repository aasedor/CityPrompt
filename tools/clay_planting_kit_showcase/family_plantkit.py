"""Planting kit showcase: one kerbed bed per element of the shared planting kit (plantkit.py), plus a Halifax-style
Victorian carpet bed, a Prince's-Island-style naturalistic perennial bed, a green-bridge-style strip against a rail and a
stepped-plaza wall with a draped climber, a parapet cascade and pot plants, on a lawn with two gravel walks.

KIT SHOWCASE ONLY, NOT A CATALOGUE CANDIDATE. There is no locked source, no archetype or variant in any catalogue and
nothing here may be enrolled, seeded or published. The module exists so the kit can be reviewed once, at eye level,
before park families reuse it.

South row (y = -6.5), west to east: B1 flower_head_cluster specimens (mophead, coneflower, rudbeckia, salvia, yarrow,
panicle, poppy, lavender), B2 perennial_drift, B3 arching_grass (fountain, feather-reed with plumes, blue), B4 shrub_mass
size range (0.4-1.6 m), B9 green-bridge strip (lavender, poppies, small shrubs) against a railing. Middle row (y = +1):
B5 groundcover with florets and leaf grain, B6 clipped bedding rings with bedding cushions, B7 leaf-shaped Halifax carpet
bed (flat clipped silver, begonia, ageratum and alyssum bands with micro-florets round white hydrangeas). North (y = +8):
B8 Prince's Island bed (drifts over a groundcover with a layered shrub backdrop). East (x = +17..26): B10 stepped-plaza
corner: a rendered wall with a door and window carrying a bougainvillea trained up and over its coping, a low terrace
wall with a parapet cascade, and pot plants.
"""
import math
import os
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-planting-kit-showcase'
SX0, SX1, SY0, SY1 = -14.5, 26.5, -10.5, 11.5    # lawn
ZG, ZP, ZS = .04, .055, .07                      # lawn top, walk top, bed soil (mulch) top: no shared planes
ZV = .065                                         # plaza paving top (B10)
KERB = .14                                       # granite bed kerb width; the kit plants inside outline minus KERB
KT, KB = .11, .02                                # kerb top and bottom
T = .3
PALETTE = dict(grass=(.33, .49, .20), gravel=(.66, .61, .53), granite=(.74, .73, .70), paving=(.70, .64, .55),
               stucco=(.84, .76, .64), coping=(.74, .71, .66), door=(.30, .21, .14), dark_pane=(.12, .15, .17),
               rail_steel=(.22, .23, .24))
INSTANCING = os.environ.get('PK_INSTANCING', '1') != '0'


def manifest(version):
    eye = 1.6
    cams = [
        dict(name='front_corner', location=(-11.0, -20.5, 13.5), target=(6.0, 0.0, 0.0), lens=24),
        dict(name='top', location=(6.0, .5, 60.0), target=(6.0, .501, 0.0), ortho_scale=42.0),
        dict(name='eye_flower_heads', location=(-9.7, -9.9, eye), target=(-10.5, -6.6, .35), lens=30),
        dict(name='eye_specimen_close', location=(-9.3, -8.75, 1.45), target=(-10.4, -6.7, .55), lens=35),
        dict(name='eye_perennial_drift', location=(-3.3, -9.8, eye), target=(-4.0, -6.6, .35), lens=30),
        dict(name='eye_arching_grass', location=(2.9, -9.6, eye), target=(2.2, -6.6, .35), lens=30),
        dict(name='eye_shrub_mass', location=(9.9, -10.3, eye), target=(9.0, -6.6, .5), lens=30),
        dict(name='eye_lavender_rail', location=(20.7, -10.2, eye), target=(20.0, -6.3, .45), lens=26),
        dict(name='eye_groundcover', location=(-9.9, -1.9, eye), target=(-10.5, 1.0, .08), lens=30),
        dict(name='eye_bedding_band', location=(-3.4, -1.9, eye), target=(-4.0, 1.0, .08), lens=30),
        dict(name='eye_carpet_bed', location=(.6, -1.7, eye), target=(4.8, 1.3, .15), lens=24),
        dict(name='eye_perennial_bed', location=(-2.8, 3.9, eye), target=(.5, 8.0, .4), lens=24),
        dict(name='eye_b8_rear', location=(2.0, 11.2, eye), target=(.3, 8.6, .35), lens=24),
        dict(name='eye_climber_wall', location=(20.0, 1.6, eye), target=(20.0, 7.6, 1.9), lens=22),
        dict(name='eye_cascade_pots', location=(23.9, 2.6, 1.5), target=(24.2, 5.8, .65), lens=28)]
    for c in cams:
        c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='kit_showcase_not_a_catalogue_candidate', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='none: shared planting kit showcase (no catalogue archetype, no locked sources)',
        measurement_contract=dict(dimensions_m=dict(width=SX1 - SX0, depth=SY1 - SY0, height=3.1),
            observed_storeys=0, storey_programme='kit showcase: nine kerbed planting beds and a plaza wall corner on a lawn',
            plan='41 x 22 m lawn, two gravel walks, nine beds with granite kerbs, a paved plaza corner with a 3 m wall and a terrace wall',
            facade='none', levels_m=[0.0, ZG, ZP, ZV, ZS, KT, 3.08], inferred='every bed is a kit demonstration, not a source reading'),
        roof_contract=dict(type='none', datum_m=0.0, crowns_m=[]),
        identity_contract=dict(owner='shared planting kit showcase: flower heads, perennial drift, arching grasses, shrub masses, groundcover, clipped bedding bands and cushions, Victorian carpet bed, naturalistic perennial bed, lavender and rail clearance, wall-trained climber, parapet cascade, pot plants'),
        material_contract=dict(profile='semantic clay planting palette (PK_PALETTE)', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='review of planting at eye level'),
        contact_contract=['Lawn on grade zero', 'Kerbs and mulch on the lawn', 'Every plant base sunk 2.5 cm into the mulch',
                          'Plaza paving, walls and pots on the lawn; climber canopy edges dive 2.5 cm into the masonry'],
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


# ---- shared planting kit (cat after gcommon.py in every park module; kept identical) ----
# One reviewed vocabulary of eye-level plants for RLASM park families. Every builder works in metres, plant bases sit on
# the soil top and are sunk PK_SINK below it (flat buried caps), curved surfaces are smooth-shaded, flat caps are
# flat-shaded and buried, and nothing is built from coplanar faces. Prototype plants are shared mesh datablocks placed as
# linked instances (glTF: one mesh, many nodes) when PlantKit(instancing=True); the family build.py must keep instances out
# of clay_core.deliver()'s per-role join (see tools/clay_planting_kit_showcase/build.py, keep_instances()).
# Kit v002: smooth (non-ridged) noise everywhere, leaf-skinned shrubs, floret-skinned mopheads, corymb umbels, spikelet
# plumes, flat clipped carpets with shoulder rings and lapped band joints, a kit-wide clearance rule (kerbs and rails),
# and the lavender, cup, panicle, bedding-cushion, pot-plant and wall-drape modules.
import random as _pkr
import numpy as _pknp
import shapely as _pksh
from shapely.geometry import Polygon as _PkPolygon

PK_SINK = .025                                  # every plant base and carpet edge dives this far below the soil top
PK_CLEAR = .05                                  # clearance between a plant's buried base and a kerb's inner edge or a rail
PK_PALETTE = dict(
    pk_leaf=(.21, .37, .14), pk_leaf2=(.31, .47, .19), pk_leaf_dark=(.13, .26, .10), pk_leaf_light=(.40, .55, .22),
    pk_leaf_silver=(.42, .47, .36), pk_leaf_red=(.38, .14, .15), pk_leaf_hairy=(.17, .29, .11), pk_lav_leaf=(.25, .31, .22),
    pk_groundcover=(.17, .30, .11), pk_shrub_core=(.05, .11, .04),
    pk_stem=(.25, .37, .16), pk_crown=(.11, .19, .08), pk_crown_blue=(.24, .32, .29), pk_bark=(.30, .23, .16),
    pk_blade=(.36, .50, .21), pk_blade_blue=(.44, .55, .50), pk_straw=(.74, .64, .42), pk_plume=(.84, .74, .55),
    pk_white=(.93, .93, .89), pk_white2=(.98, .97, .92), pk_cream=(.88, .87, .70), pk_pink=(.88, .55, .66),
    pk_pink2=(.95, .72, .80), pk_magenta=(.72, .24, .48), pk_bract2=(.84, .34, .58), pk_purple=(.43, .29, .63),
    pk_purple2=(.56, .43, .76), pk_lavender=(.40, .28, .66), pk_yellow=(.92, .74, .20), pk_yellow2=(.96, .84, .42),
    pk_orange=(.88, .46, .18), pk_red=(.76, .13, .14), pk_red2=(.88, .30, .30), pk_terracotta=(.66, .34, .21),
    pk_boss=(.30, .18, .09), pk_mulch=(.25, .18, .12))


def pk_palette(palette):
    """Add the kit's default plant roles to a family PALETTE without overriding any role the family already defines."""
    for k, v in PK_PALETTE.items():
        palette.setdefault(k, v)
    return palette


class _PkNoise:
    """Smooth band-limited noise: a sum of plane waves with random directions near `freq` rad/m (deterministic per seed)."""
    def __init__(self, seed, freq, waves=7):
        r = _pkr.Random(seed); self.k = []
        for _ in range(waves):
            z = r.uniform(-1, 1); a = r.uniform(0, 2 * math.pi); s = math.sqrt(1 - z * z); f = freq * r.uniform(.75, 1.3)
            self.k.append((s * math.cos(a) * f, s * math.sin(a) * f, z * f, r.uniform(0, 2 * math.pi)))
        self.norm = 1 / math.sqrt(waves / 2)

    def __call__(self, x, y, z=0.):
        return self.norm * sum(math.sin(kx * x + ky * y + kz * z + ph) for kx, ky, kz, ph in self.k)

    def arr(self, X, Y):
        return self.norm * sum(_pknp.sin(kx * X + ky * Y + ph) for kx, ky, kz, ph in self.k)


class PkGeo:
    """Vertex/face accumulator for one role of a prototype; `flat` lists face indices to flat-shade (buried caps)."""
    def __init__(self):
        self.v = []; self.f = []; self.flat = []

    def add(self, vs, fs, flat=()):
        o = len(self.v); b = len(self.f)
        self.v.extend(vs); self.f.extend(tuple(o + i for i in face) for face in fs); self.flat.extend(b + i for i in flat)

    def tris(self):
        return sum(len(f) - 2 for f in self.f)


def _pk_parts(*roles):
    out = {}
    for r in roles:
        out.setdefault(r, PkGeo())
    return out


def _pk_norm(v):
    n = math.sqrt(sum(c * c for c in v)) or 1.
    return tuple(c / n for c in v)


def _pk_cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _pk_rot(v, axis, ang):
    """Rodrigues rotation of v about the unit axis."""
    c, s = math.cos(ang), math.sin(ang); kx, ky, kz = axis; x, y, z = v
    d = kx * x + ky * y + kz * z; cx, cy, cz = _pk_cross(axis, v)
    return (x * c + cx * s + kx * d * (1 - c), y * c + cy * s + ky * d * (1 - c), z * c + cz * s + kz * d * (1 - c))


def _pk_tilt(axis):
    """Rotation (axis, angle) taking local +z onto the unit `axis`, or None."""
    if abs(axis[2]) >= .999:
        return None
    return (_pk_norm(_pk_cross((0., 0., 1.), axis)), math.acos(max(-1., min(1., axis[2]))))


def _pk_smooth(t):
    t = min(1., max(0., t))
    return t * t * (3 - 2 * t)


def _pk_dome(g, c, r, base, seed=0, bump=0., wave=.15, lo=0., seg=18, rings=9):
    """Ellipsoid lobe (centre c, radii r) cut flat at z = base: smooth-shaded skin displaced by soft signed noise
    (amplitude `bump` m at `wave` m, plus a gentle `lo` m swell; no ridged |noise| term, so no creases or spurs), fading
    to zero at the buried base ring; the flat cap is flat-shaded. Neighbouring lobes interpenetrate, never share a plane."""
    cx, cy, cz = c; rx, ry, rz = r
    tmax = math.acos(max(-.995, min(.995, (base - cz) / rz)))
    hi = _PkNoise(seed, 2 * math.pi / wave); low = _PkNoise(seed + 101, 2 * math.pi / (wave * 4))
    vs = []; fs = []
    for i in range(rings + 1):
        t = tmax * i / rings; st, ct = math.sin(t), math.cos(t)
        for j in range(1 if i == 0 else seg):
            a = 2 * math.pi * j / seg
            u = (st * math.cos(a), st * math.sin(a), ct)
            p = (cx + rx * u[0], cy + ry * u[1], cz + rz * u[2] if i < rings else base)
            fade = _pk_smooth((p[2] - base) / (.35 * rz))
            d = (bump * .6 * hi(*p) + lo * low(*p)) * fade
            vs.append((p[0] + u[0] * d, p[1] + u[1] * d, p[2] + u[2] * d if i < rings else base))
    for j in range(seg):
        fs.append((0, 1 + j, 1 + (j + 1) % seg))
    for i in range(1, rings):
        a0 = 1 + (i - 1) * seg; a1 = 1 + i * seg
        for j in range(seg):
            k = (j + 1) % seg
            fs.append((a0 + j, a1 + j, a1 + k, a0 + k))
    ctr = len(vs); vs.append((cx, cy, base)); last = 1 + (rings - 1) * seg
    cap0 = len(fs)
    for j in range(seg):
        fs.append((last + (j + 1) % seg, last + j, ctr))
    g.add(vs, fs, range(cap0, len(fs)))


def _pk_ball(g, c, r, seed=0, bump=0., wave=.05, seg=10, rings=6, axis=None):
    """Closed smooth ellipsoid (soft signed `bump` noise, never ridged); `axis` (unit) tilts its local z."""
    cx, cy, cz = c; rx, ry, rz = r
    hi = _PkNoise(seed, 2 * math.pi / wave) if bump else None
    rot = _pk_tilt(axis) if axis is not None else None
    vs = []; fs = []
    for i in range(rings + 1):
        t = math.pi * i / rings; st, ct = math.sin(t), math.cos(t)
        for j in range(1 if i in (0, rings) else seg):
            a = 2 * math.pi * j / seg
            u = (st * math.cos(a), st * math.sin(a), ct)
            p = (rx * u[0], ry * u[1], rz * u[2])
            if hi:
                d = bump * .5 * hi(p[0] + cx, p[1] + cy, p[2] + cz)
                p = (p[0] + u[0] * d, p[1] + u[1] * d, p[2] + u[2] * d)
            if rot:
                p = _pk_rot(p, *rot)
            vs.append((cx + p[0], cy + p[1], cz + p[2]))
    bot = len(vs) - 1
    for j in range(seg):
        fs.append((0, 1 + j, 1 + (j + 1) % seg))
    for i in range(1, rings - 1):
        a0 = 1 + (i - 1) * seg; a1 = 1 + i * seg
        for j in range(seg):
            k = (j + 1) % seg
            fs.append((a0 + j, a1 + j, a1 + k, a0 + k))
    last = 1 + (rings - 2) * seg
    for j in range(seg):
        fs.append((last + (j + 1) % seg, last + j, bot))
    g.add(vs, fs)


def _pk_lathe(g, base, axis, length, radius, seg=8, rings=8):
    """Closed smooth solid of revolution along `axis` from `base`: radius(q) for q in (0, 1), poles at both ends
    (spindles, panicle cones, lavender spikes)."""
    rot = _pk_tilt(axis)
    vs = [base]; fs = []
    for i in range(1, rings):
        q = i / rings; rr = radius(q)
        for j in range(seg):
            a = 2 * math.pi * (j + .5 * (i % 2)) / seg
            p = (rr * math.cos(a), rr * math.sin(a), length * q)
            if rot:
                p = _pk_rot(p, *rot)
            vs.append((base[0] + p[0], base[1] + p[1], base[2] + p[2]))
    tip = (base[0] + axis[0] * length, base[1] + axis[1] * length, base[2] + axis[2] * length); vs.append(tip)
    for j in range(seg):
        fs.append((0, 1 + (j + 1) % seg, 1 + j))
    for i in range(1, rings - 1):
        a0 = 1 + (i - 1) * seg; a1 = 1 + i * seg
        for j in range(seg):
            k = (j + 1) % seg
            fs.append((a0 + j, a0 + k, a1 + k, a1 + j))
    last = 1 + (rings - 2) * seg; t = len(vs) - 1
    for j in range(seg):
        fs.append((last + j, last + (j + 1) % seg, t))
    g.add(vs, fs)


def _pk_tube(g, pts, r0, r1, sides=5):
    """Tapered open tube along a polyline (stems); ends are hidden in foliage or heads."""
    n = len(pts); vs = []; fs = []
    for i, p in enumerate(pts):
        t = _pk_norm(tuple(pts[min(n - 1, i + 1)][k] - pts[max(0, i - 1)][k] for k in range(3)))
        ref = (0., 0., 1.) if abs(t[2]) < .9 else (1., 0., 0.)
        s = _pk_norm(_pk_cross(t, ref)); u = _pk_cross(s, t); rr = r0 + (r1 - r0) * i / (n - 1)
        for j in range(sides):
            a = 2 * math.pi * j / sides
            vs.append(tuple(p[k] + rr * (math.cos(a) * s[k] + math.sin(a) * u[k]) for k in range(3)))
    for i in range(n - 1):
        for j in range(sides):
            k = (j + 1) % sides
            fs.append((i * sides + j, (i + 1) * sides + j, (i + 1) * sides + k, i * sides + k))
    g.add(vs, fs)


def _pk_arc(p0, phi, elev, bend, length, n=7, floor=None):
    """Centre line of a blade or stem leaving p0 at azimuth phi and `elev` above horizontal, bending down by `bend` rad
    over its length (gravity arch); stops early rather than dip below `floor`."""
    pts = [tuple(p0)]; ds = length / (n - 1)
    for i in range(1, n):
        a = elev - bend * (i - .5) / (n - 1); q = pts[-1]
        nq = (q[0] + math.cos(a) * math.cos(phi) * ds, q[1] + math.cos(a) * math.sin(phi) * ds, q[2] + math.sin(a) * ds)
        if floor is not None and nq[2] < floor and i > 2:
            break
        pts.append(nq)
    return pts


def _pk_blade(g, pts, phi, width, fold=.25, taper=1., ovate=False):
    """Strap leaf or grass blade along pts: three verts across (two edges and a raised keel, so it never reads as a flat
    ribbon), tapering to a single tip vertex; ovate=True gives a broad leaf (narrow petiole, widest near 40%, pointed)."""
    side = (-math.sin(phi), math.cos(phi), 0.); n = len(pts); vs = []; fs = []
    for i in range(n - 1):
        p = pts[i]; t = _pk_norm(tuple(pts[i + 1][k] - pts[max(0, i - 1)][k] for k in range(3)))
        nn = _pk_norm(_pk_cross(side, t)); q = i / (n - 1)
        w = width * (max(.12, math.sin(math.pi * q ** .6) ** .7) if ovate else (1 - .8 * q ** taper) * (.7 + .3 * min(1, i / 1.5)))
        vs += [tuple(p[k] - side[k] * w / 2 for k in range(3)), tuple(p[k] + nn[k] * fold * w for k in range(3)),
               tuple(p[k] + side[k] * w / 2 for k in range(3))]
    vs.append(pts[-1])
    for i in range(n - 2):
        a, b = 3 * i, 3 * (i + 1)
        fs += [(a, b, b + 1, a + 1), (a + 1, b + 1, b + 2, a + 2)]
    a, t = 3 * (n - 2), 3 * (n - 1)
    fs += [(a, t, a + 1), (a + 1, t, a + 2)]
    g.add(vs, fs)


def _pk_card(g, base, d, cn, length, width, fold=.18):
    """Small cupped leaf card (4 verts, 2 triangles): base, two side points at 40% raised by `fold` along the card
    normal cn, and the tip along direction d. The cheap leaf for shrub and fringe skins."""
    side = _pk_norm(_pk_cross(d, cn)); m = tuple(base[k] + d[k] * length * .4 + cn[k] * fold * width for k in range(3))
    g.add([tuple(base), tuple(m[k] - side[k] * width / 2 for k in range(3)), tuple(m[k] + side[k] * width / 2 for k in range(3)),
           tuple(base[k] + d[k] * length for k in range(3))], [(0, 2, 3), (0, 3, 1)])


def _pk_speck(g, c, n, r, a0=0.):
    """Tiny smooth 3-sided cap (4 vertices, 3 triangles) standing r x 1.1 proud of c along the normal n: the cheapest
    readable fleck for micro-florets, bracts and leaf grain."""
    rot = _pk_tilt(n); vs = [(0., 0., r * 1.1)] + [(r * math.cos(a0 + 2.0944 * j), r * math.sin(a0 + 2.0944 * j), 0.) for j in range(3)]
    g.add([tuple(c[k] + (_pk_rot(p, *rot) if rot else p)[k] for k in range(3)) for p in vs], [(0, 1, 2), (0, 2, 3), (0, 3, 1)])


def _pk_daisy(gp, gb, c, R, petals, droop, axis, cone=1.0, seg=4, rings=3):
    """Ray-flower head: a smooth scalloped petal disc (petal tips, notches between) drooping by `droop`, around a domed
    or conical boss; built facing local +z and tilted onto `axis`."""
    rc = R * .30; vs = []; fs = []; m = petals * seg
    for i in range(rings + 1):
        for j in range(m):
            th = 2 * math.pi * j / m; f = abs(math.cos(petals * th / 2)) ** .6
            rr = rc * .85 + (R * (.42 + .58 * f) - rc * .85) * i / rings
            q = (rr - rc) / (R - rc)
            vs.append((rr * math.cos(th), rr * math.sin(th), -droop * R * max(0., q) ** 1.6 + .12 * rc * (1 - i / rings)))
    for i in range(rings):
        for j in range(m):
            k = (j + 1) % m
            fs.append((i * m + j, (i + 1) * m + j, (i + 1) * m + k, i * m + k))
    rot = _pk_tilt(axis)
    tr = lambda p: tuple(c[k] + (_pk_rot(p, *rot) if rot else p)[k] for k in range(3))
    gp.add([tr(p) for p in vs], fs)
    hb = PkGeo(); _pk_ball(hb, (0., 0., rc * .35 * cone), (rc, rc, rc * .8 * cone), bump=rc * .25, wave=rc * .9, seg=10, rings=5)
    gb.add([tr(p) for p in hb.v], hb.f)


def _pk_cup(gp, gb, c, R, axis, petals=4):
    """Cup flower (poppy, tulip, anemone): a smooth bowl of `petals` broad rounded petals rising from a dark boss."""
    rot = _pk_tilt(axis); m = petals * 5; rings = 3; vs = [(0., 0., -R * .05)]; fs = []
    for i in range(1, rings + 1):
        q = i / rings
        for j in range(m):
            th = 2 * math.pi * j / m; f = .80 + .20 * abs(math.cos(petals * th / 2)) ** .5
            rr = R * q * f; vs.append((rr * math.cos(th), rr * math.sin(th), R * .62 * q ** 1.7 * f))
    for j in range(m):
        fs.append((0, 1 + j, 1 + (j + 1) % m))
    for i in range(rings - 1):
        a0 = 1 + i * m; a1 = a0 + m
        for j in range(m):
            k = (j + 1) % m
            fs.append((a0 + j, a1 + j, a1 + k, a0 + k))
    tr = lambda p: tuple(c[k] + (_pk_rot(p, *rot) if rot else p)[k] for k in range(3))
    gp.add([tr(p) for p in vs], fs)
    hb = PkGeo(); _pk_ball(hb, (0., 0., R * .12), (R * .24, R * .24, R * .2), seg=8, rings=4)
    gb.add([tr(p) for p in hb.v], hb.f)


def _pk_corymb(g, c, R, rnd, florets=8):
    """Flat-topped corymb (yarrow, sedum, achillea): a smooth low dome packed with small smooth floret domes that
    break its outline into a fine scalloped edge; never a single faceted plate."""
    _pk_ball(g, (c[0], c[1], c[2]), (R * .82, R * .82, R * .3), seg=12, rings=4)
    for k in range(florets):
        q = math.sqrt((k + .5) / florets); a = k * 2.39996 + rnd.uniform(-.2, .2); d = R * .78 * q
        rr = R * rnd.uniform(.25, .32); top = c[2] + R * .3 * math.sqrt(max(0., 1 - (d / (R * .82)) ** 2)) * .7
        _pk_ball(g, (c[0] + d * math.cos(a), c[1] + d * math.sin(a), top), (rr, rr, rr * .7), seg=7, rings=4)


def _pk_spike(g, base, axis, length, r0, seed, seg=5):
    """Whorled flower spire (salvia, veronica): tightly packed, shrinking floret whorls up a slightly nodding axis
    ending in a tapered tip, so it reads as a dense spire of florets, not a string of beads."""
    rnd = _pkr.Random(seed); n = max(5, int(length / (r0 * 1.15)))
    _pk_lathe(g, base, axis, length * .9, lambda q: r0 * .62 * (1 - .55 * q) * min(1., q * 6 + .3), seg=seg, rings=6)
    for i in range(n - 2):
        q = i / (n - 1); rr = r0 * (1 - .5 * q)
        off = (rnd.uniform(-.2, .2) * rr, rnd.uniform(-.2, .2) * rr)
        p = (base[0] + axis[0] * length * q + off[0], base[1] + axis[1] * length * q + off[1], base[2] + axis[2] * length * q)
        _pk_ball(g, p, (rr * .85, rr * .85, rr * .7), seg=seg, rings=4)
    q0 = (n - 3) / (n - 1)
    tb = tuple(base[k] + axis[k] * length * q0 for k in range(3))
    _pk_lathe(g, tb, axis, length * (1 - q0) + r0 * .4, lambda q: r0 * .55 * (1 - q) ** .7 * min(1, q * 4 + .3), seg=seg, rings=4)


def _pk_panicle(g, base, axis, length, r0, rnd, florets=13):
    """Loose conical panicle (astilbe, panicle hydrangea, white phlox): a smooth tapering cone of florets, widest
    near its base, with small floret domes standing proud of its surface so the outline is fine-grained."""
    _pk_lathe(g, base, axis, length, lambda q: r0 * min(1., q * 3.5) * (1 - q) ** .85, seg=9, rings=7)
    rot = _pk_tilt(axis)
    for k in range(florets):
        q = .12 + .78 * (k + .5) / florets; a = k * 2.39996 + rnd.uniform(-.3, .3)
        rr = r0 * min(1., q * 3.5) * (1 - q) ** .85; fr = r0 * rnd.uniform(.32, .42) * (1.1 - .5 * q)
        p = (rr * .95 * math.cos(a), rr * .95 * math.sin(a), length * q)
        if rot:
            p = _pk_rot(p, *rot)
        _pk_ball(g, (base[0] + p[0], base[1] + p[1], base[2] + p[2]), (fr, fr, fr * .85), seg=5, rings=4)


class PlantKit:
    """Prototype registry, clearance checker and placer. proto() turns {role: PkGeo} into one shared mesh datablock per
    role and measures its buried base radius (`base_r`: vertices below kerb height) and canopy radius; place() puts a
    prototype at (x, y, z) with spin, non-uniform scale and lean, as linked instances (instancing=True: glTF reuses the
    mesh, ~0.6 KB per node) or merged into per-role batches (instancing=False). fits()/place_in() apply the kit-wide
    clearance rule: a plant's base stays PK_CLEAR inside every registered bed edge and clear of every obstacle, and only
    canopy above kerb height may overhang a kerb; a tall obstacle (a rail) keeps the whole canopy clear. audit() counts
    placements that break the rule (must be 0). Call flush() once after planting."""
    def __init__(self, module='planting', instancing=True, kerb_h=.045):
        self.module = module; self.instancing = instancing; self.batch = {}; self.placed = 0; self.nodes = 0
        self.unique_triangles = 0; self.counts = {}; self.kerb_h = kerb_h; self.beds = []; self.obstacles = []
        self.placements = []; self.rejected = 0

    def proto(self, name, parts):
        datas = {}; base_r = canopy_r = height = 0.
        for role, g in parts.items():
            if not g.f:
                continue
            for x, y, z in g.v:
                h = math.hypot(x, y); canopy_r = max(canopy_r, h); height = max(height, z)
                if z < self.kerb_h:
                    base_r = max(base_r, h)
            me = C.bpy.data.meshes.new(f'PK {name} {role}')
            me.from_pydata(g.v, [], g.f); C.normalise(me)
            flat = set(g.flat)
            for p in me.polygons:
                p.use_smooth = p.index not in flat
            me.materials.append(C.MATS[role]); datas[role] = (me, g)
            self.unique_triangles += g.tris()
        return dict(name=name, parts=datas, tris=sum(g.tris() for _, g in datas.values()), base_r=base_r,
                    canopy_r=canopy_r, height=height)

    def register_bed(self, region):
        """A plantable region (bed outline minus kerb): plants whose centre falls in it keep their base inside it."""
        reg = region if hasattr(region, 'geom_type') else _PkPolygon(region)
        _pksh.prepare(reg); self.beds.append(reg)
        return reg

    def add_obstacle(self, geom, top):
        """A kerb, rail, wall or post footprint (shapely) with its top height above the soil: bases stay PK_CLEAR off it;
        if top > 0.3 m (a rail or wall) the whole canopy stays clear of it."""
        _pksh.prepare(geom); self.obstacles.append((geom, top))

    def fits(self, p, x, y, s=1., region=None, clear=PK_CLEAR):
        pt = _pksh.points(x, y); br = p['base_r'] * s + clear
        for reg in ([region] if region is not None else []) + self.beds:
            if _pksh.contains_xy(reg, x, y) and reg.boundary.distance(pt) < br:
                return False
            if reg is region and not _pksh.contains_xy(reg, x, y):
                return False
        for geom, top in self.obstacles:
            d = geom.distance(pt)
            if d < br or (top > .3 and d < p['canopy_r'] * s * .92):
                return False
        return True

    def place_in(self, p, x, y, z, rot=0., s=1., region=None, shrink=(1., .85, .72), aspect=1., **kw):
        """Place p at (x, y) with scale s (y scale s x aspect) if it fits, trying the given shrink factors, else skip it;
        returns the scale used or 0."""
        for f in shrink:
            if self.fits(p, x, y, s * f * max(1., aspect), region):
                self.place(p, x, y, z, rot, s * f, sy=s * f * aspect, **kw)
                return s * f
        self.rejected += 1
        return 0.

    def place(self, p, x, y, z, rot=0., s=1., sz=None, sy=None, lean=(0., 0.), instance=None):
        inst = self.instancing if instance is None else instance
        sz = s if sz is None else sz; sy = s if sy is None else sy
        self.placed += 1; self.counts[p['name']] = self.counts.get(p['name'], 0) + 1
        self.placements.append((x, y, max(s, sy), p))
        for role, (me, g) in p['parts'].items():
            if inst:
                o = C.bpy.data.objects.new(f"{p['name']} {role} {self.placed}", me)
                C.bpy.context.collection.objects.link(o)
                o.location = (x, y, z); o.rotation_euler = (lean[0], lean[1], rot); o.scale = (s, sy, sz)
                for k, v in (('rlasm_building_object', True), ('rlasm_method', C.METHOD), ('cityprompt_semantic_role', role),
                             ('cityprompt_lego_module', self.module), ('representation_kind', 'architectural_clay'),
                             ('native_geometry_only', True), ('rlasm_instance', True)):
                    o[k] = v
                self.nodes += 1
            else:
                ca, sa = math.cos(lean[0]), math.sin(lean[0]); cb, sb = math.cos(lean[1]), math.sin(lean[1])
                c, sn = math.cos(rot), math.sin(rot)

                def tf(v):
                    vx, vy, vz = v[0] * s, v[1] * sy, v[2] * sz
                    vy, vz = ca * vy - sa * vz, sa * vy + ca * vz          # Blender XYZ euler: X, then Y, then Z
                    vx, vz = cb * vx + sb * vz, -sb * vx + cb * vz
                    return (x + c * vx - sn * vy, y + sn * vx + c * vy, z + vz)
                V, F, FL = self.batch.setdefault(role, ([], [], []))
                o = len(V); b = len(F)
                V.extend(tf(v) for v in g.v)
                F.extend(tuple(o + i for i in face) for face in g.f); FL.extend(b + i for i in g.flat)

    def audit(self, detail=False):
        """Placements whose buried base crosses a registered bed edge or obstacle, or whose canopy enters a tall one
        (the count, or with detail=True the offending (name, x, y))."""
        bad = []
        for x, y, s, p in self.placements:
            pt = _pksh.points(x, y); br = p['base_r'] * s
            if any(_pksh.contains_xy(r, x, y) and r.boundary.distance(pt) < br for r in self.beds) or \
                    any(g.distance(pt) < br or (top > .3 and g.distance(pt) < p['canopy_r'] * s * .9) for g, top in self.obstacles):
                bad.append((p['name'], round(x, 2), round(y, 2)))
        return bad if detail else len(bad)

    def flush(self):
        for role, (V, F, FL) in self.batch.items():
            if F:
                pk_mesh(f'{self.module} merged {role}', V, F, FL, role, self.module)
        self.batch = {}
        C.MODULES.setdefault(self.module, []).append(dict(planting_kit=True, instancing=self.instancing, plants=self.placed,
            instance_nodes=self.nodes, prototypes=self.counts, clearance_violations=self.audit(), rejected=self.rejected))

    def stats(self):
        return dict(instancing=self.instancing, plants=self.placed, instance_nodes=self.nodes, prototypes=len(self.counts),
                    prototype_triangles=self.unique_triangles, clearance_violations=self.audit(), rejected=self.rejected)


def pk_mesh(name, V, F, flat, role, module):
    """C.mesh with smooth shading on every face not listed in `flat`."""
    o = C.mesh(name, V, F, role, module)
    fl = set(flat)
    for p in o.data.polygons:
        p.use_smooth = p.index not in fl
    return o


# ---- outlines and scatter ----

def pk_ellipse(cx, cy, a, b, rot=0., n=64):
    c, s = math.cos(rot), math.sin(rot)
    return [(cx + a * math.cos(t) * c - b * math.sin(t) * s, cy + a * math.cos(t) * s + b * math.sin(t) * c)
            for t in (2 * math.pi * i / n for i in range(n))]


def pk_leaf(cx, cy, length, width, rot=0., n=84):
    """Leaf (vesica) bed outline with softly rounded tips, long axis at angle rot."""
    c, s = math.cos(rot), math.sin(rot); pts = []
    for i in range(n):
        t = 2 * math.pi * i / n; x = length / 2 * math.cos(t); y = width / 2 * math.sin(t) * abs(math.sin(t)) ** .35
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def pk_blob(cx, cy, a, b, seed=1, amp=.12, n=72, rot=0.):
    """Irregular naturalistic bed outline: an ellipse with low-order radial wobble (stays star-shaped)."""
    r = _pkr.Random(seed); h = [(k, r.uniform(-amp, amp) / k ** .5, r.uniform(0, 2 * math.pi)) for k in (2, 3, 4, 5)]
    c, s = math.cos(rot), math.sin(rot); pts = []
    for i in range(n):
        t = 2 * math.pi * i / n; f = 1 + sum(A_ * math.sin(k * t + ph) for k, A_, ph in h)
        x, y = a * f * math.cos(t), b * f * math.sin(t)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def pk_rounded_rect(cx, cy, a, b, r=.35, n=6):
    """Rounded-rectangle bed or planter outline (half sizes a, b; corner radius r), CCW."""
    pts = []
    for qx, qy, a0 in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        ox, oy = cx + qx * (a - r), cy + qy * (b - r)
        for i in range(n + 1):
            t = math.radians(a0 + 90 * i / n); pts.append((ox + r * math.cos(t), oy + r * math.sin(t)))
    return pts


def pk_region(poly, kerb=0.):
    """Plantable region: bed outline (point list or shapely geometry) shrunk by the kerb width."""
    g = poly if hasattr(poly, 'geom_type') else _PkPolygon(poly)
    return g.buffer(-kerb, quad_segs=8) if kerb else g


def pk_scatter(poly, spacing, kerb=0., margin=0., seed=1, jitter=1.0):
    """Poisson-disc points at least `spacing` apart inside the bed outline shrunk by kerb + margin (margin = the item's
    footprint radius), so nothing overhangs the kerb. Deterministic per seed."""
    reg = pk_region(poly, kerb + margin)
    if reg.is_empty:
        return []
    _pksh.prepare(reg)
    r = _pkr.Random(seed); x0, y0, x1, y1 = reg.bounds; cell = spacing / math.sqrt(2); grid = {}; out = []
    tries = int(reg.area / (spacing * spacing) * 30) + 20
    for _ in range(tries):
        x, y = r.uniform(x0, x1), r.uniform(y0, y1)
        if not _pksh.contains_xy(reg, x, y):
            continue
        gi, gj = int((x - x0) / cell), int((y - y0) / cell); ok = True
        for di in (-2, -1, 0, 1, 2):
            for dj in (-2, -1, 0, 1, 2):
                q = grid.get((gi + di, gj + dj))
                if q and (q[0] - x) ** 2 + (q[1] - y) ** 2 < (spacing * jitter) ** 2:
                    ok = False; break
            if not ok:
                break
        if ok:
            grid[(gi, gj)] = (x, y); out.append((x, y))
    return out


def pk_bed(name, outline, soil_z, kerb=.15, kerb_top=None, kerb_bottom=None, kerb_role='granite', soil_role='pk_mulch',
           module='beds', kit=None):
    """Kerbed planting bed: a mitred granite kerb ring (outline = its outer edge, CCW, smooth) and a flat mulch surface at
    soil_z whose edge is buried inside the kerb. With kit=, the plantable region (outline minus kerb) is registered for
    the clearance rule. Plants then use kerb=<this kerb> to stay inside it."""
    kerb_top = soil_z + .04 if kerb_top is None else kerb_top
    kerb_bottom = soil_z - .05 if kerb_bottom is None else kerb_bottom
    n = len(outline); sec = []
    for i in range(n):
        p0, p1 = outline[i - 1], outline[(i + 1) % n]; dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1
        nx, ny = dy / L, -dx / L
        x, y = outline[i]; ix, iy = x - nx * kerb, y - ny * kerb
        sec.append([(ix, iy, kerb_bottom), (ix, iy, kerb_top - .012), (ix + nx * .012, iy + ny * .012, kerb_top),
                    (x - nx * .012, y - ny * .012, kerb_top), (x, y, kerb_top - .012), (x, y, kerb_bottom)])
    ko = loft(name + ' kerb', sec, kerb_role, module); m = len(sec[0])
    for p in ko.data.polygons:
        p.use_smooth = True
    for e in ko.data.edges:                      # profile corners stay crisp; vertices are shared round the ring
        a, b = e.vertices
        e.use_edge_sharp = (a // m) != (b // m)
    soil = pk_region(outline, kerb * .5)
    tris = [t for t in _pksh.get_parts(_pksh.delaunay_triangles(_pksh.segmentize(soil, .4))) if soil.contains(t.centroid)]
    V = []; F = []
    for t in tris:
        o = len(V); V.extend((x, y, soil_z) for x, y in list(t.exterior.coords)[:3]); F.append((o, o + 1, o + 2))
    soil_obj = pk_mesh(name + ' soil', V, F, (), soil_role, module)
    if kit is not None:
        kit.register_bed(pk_region(outline, kerb))
    return soil_obj


# ---- carpets: groundcover, clipped bedding bands and dots ----

def _pk_field(region, z, height, bump, wave, grid, ramp, seed, edge=None, mid=False, base=None):
    """Heightfield carpet over a shapely region (holes allowed). Vertices: the region outline (at PK_SINK below the
    soil), an inner shoulder ring at ramp (and one at ramp/2 with mid=True), all resampled every `edge` m, and an interior triangular lattice
    beyond the shoulder; Delaunay-triangulated and clipped to the region. The shoulder is a regular strip (no mixing of
    edge and lattice points, so no teeth); its profile 1-(1-t)^2 rises steeply like a clipped edge and rounds onto the
    top. The top is `height` plus soft signed noise (`bump` m at `wave` m): flat and clipped for bedding (bump <= 4 mm),
    gently cushioned for groundcover. Returns (V, F, hz)."""
    edge = edge or min(grid * .6, .06); bnd = region.boundary
    rings = [_pksh.get_coordinates(_pksh.segmentize(bnd, edge))]
    for t in ((.5, 1.) if mid else (1.,)):
        g = region.buffer(-ramp * t, quad_segs=8)
        if not g.is_empty:
            rings.append(_pksh.get_coordinates(_pksh.segmentize(g.boundary, edge)))
    x0, y0, x1, y1 = region.bounds
    xs = _pknp.arange(x0, x1 + grid, grid); ys = _pknp.arange(y0, y1 + grid, grid * .866)
    X, Y = _pknp.meshgrid(xs, ys); X = X + (_pknp.arange(len(ys))[:, None] % 2) * grid / 2      # triangular lattice
    X, Y = X.ravel(), Y.ravel()
    D = _pksh.distance(bnd, _pksh.points(X, Y)); ok = _pksh.contains_xy(region, X, Y) & (D > ramp + grid * .45)
    P = _pknp.concatenate([_pknp.stack([X[ok], Y[ok]], 1)] + rings[1:])
    nh = _PkNoise(seed, 2 * math.pi / wave); nl = _PkNoise(seed + 9, 2 * math.pi / (wave * 3.5))

    def top(Xa, Ya, Da):
        t = _pknp.clip(Da / ramp, 0, 1); prof = 1 - (1 - t) ** 2
        crown = height + bump * (.65 * nh.arr(Xa, Ya) + .35 * nl.arr(Xa, Ya))
        return (z if base is None else base(Xa, Ya)) - PK_SINK + (PK_SINK + crown) * prof

    DP = _pksh.distance(bnd, _pksh.points(P[:, 0], P[:, 1]))
    H = _pknp.concatenate([top(P[:, 0], P[:, 1], DP), _pknp.full(len(rings[0]), z - PK_SINK)])
    if base is not None:
        H[len(P):] = base(rings[0][:, 0], rings[0][:, 1]) - PK_SINK
    P = _pknp.concatenate([P, rings[0]])
    keys = {}; V = []
    for (x, y), h in zip(P, H):
        k = (round(float(x), 5), round(float(y), 5))
        if k not in keys:
            keys[k] = len(V); V.append((float(x), float(y), float(h)))
    tri = _pksh.get_parts(_pksh.delaunay_triangles(_pksh.multipoints([v[:2] for v in V])))
    cen = _pksh.centroid(tri); inside = _pksh.contains(region, cen)
    F = []
    for t in tri[inside]:
        c = _pksh.get_coordinates(t)[:3]
        f = tuple(keys[(round(float(x), 5), round(float(y), 5))] for x, y in c)
        if len(set(f)) == 3:
            F.append(f)

    def hz(x, y):
        X_, Y_ = _pknp.asarray(x, float), _pknp.asarray(y, float)
        h = top(X_, Y_, _pksh.distance(bnd, _pksh.points(X_, Y_)))
        return float(h) if _pknp.ndim(h) == 0 else h
    return V, F, hz


def groundcover(name, poly, z, kerb=.15, height=.06, bump=.012, wave=.45, grid=.2, ramp=.04, role='pk_groundcover', seed=1,
                module='planting', dots=None, grain=None, edge=.08):
    """Low continuous carpet (thyme, sedum, vinca, ajuga) over a bed outline minus the kerb (lapped 3 cm under the kerb so
    no edge shows): a softly cushioned heightfield with a clean clipped rim, grounded and leaving no bare fill between
    larger plants. dots=(roles, per_m2, radius[, seed]) adds merged floret specks; grain=(roles, per_m2, radius) adds
    merged leaf-rosette specks for leaf texture at eye level. Returns (object, hz)."""
    reg = pk_region(poly, kerb - .03) if kerb else pk_region(poly)
    V, F, hz = _pk_field(reg, z, height, bump, wave, grid, ramp, seed, edge)
    o = pk_mesh(name, V, F, (), role, module)
    sub = pk_region(reg, .05)
    if grain:
        pk_dots(name + ' grain', sub, hz, *grain[:3], seed=seed + 13, module=module, sink=.45)
    if dots:
        pk_dots(name + ' dots', sub, hz, *dots[:3], seed=dots[3] if len(dots) > 3 else seed + 7, module=module)
    return o, hz


def pk_dots(name, region, hz, roles, per_m2, radius, seed=3, module='planting', sink=.35):
    """Merged micro-floret specks seated into a carpet surface hz: smooth 3-sided caps (4 vertices, 3 triangles) with
    their base buried `sink` x radius into the carpet; `roles` may be one role or several (hue jitter between roles).
    For dense flowering carpets (begonia, ageratum, alyssum, thyme) at 100-300 per m2."""
    roles = (roles,) if isinstance(roles, str) else tuple(roles)
    pts = pk_scatter(region, 1 / math.sqrt(per_m2) * .85, seed=seed)
    gs = {ro: PkGeo() for ro in roles}; r = _pkr.Random(seed)
    for x, y in pts:
        rr = radius * r.uniform(.75, 1.25)
        _pk_speck(gs[roles[r.randrange(len(roles))]], (x, y, hz(x, y) - rr * sink), (0., 0., 1.), rr, r.uniform(0, 2 * math.pi))
    for ro, g in gs.items():
        if g.f:
            pk_mesh(f'{name} {ro}', g.v, g.f, (), ro, module)
    return len(pts)


def bedding_band(name, outline, z, d_out, d_in, role, kerb=.15, height=.075, bump=.003, wave=.6, grid=.16, ramp=.025,
                 lap_out=0., lap_in=0., seed=1, module='planting', dots=None, edge=.075):
    """One clipped carpet-bedding ribbon between inward offsets d_out and d_in (m from the kerb's inner edge; d_in=None
    fills the centre): a flat clipped heightfield (bump <= 4 mm) with a near-vertical 2.5 cm shoulder. lap_out / lap_in
    extend the band under its neighbour (or under the kerb), so bands meet at a clean clipped step, never a soil valley
    and never on a shared plane (use carpet_bands() to set laps and steps automatically). dots=(roles, per_m2, radius)
    adds micro-florets on its visible part. Returns (object, visible region, hz)."""
    inner = pk_region(outline, kerb)
    reg = inner.buffer(-(d_out - lap_out), quad_segs=8) if d_out - lap_out else inner
    vis = inner.buffer(-(d_out + .02), quad_segs=8)
    if d_in is not None:
        reg = reg.difference(inner.buffer(-(d_in + lap_in), quad_segs=8))
        vis = vis.difference(inner.buffer(-(d_in - .02), quad_segs=8))
    if reg.is_empty:
        return None, vis, None
    V, F, hz = _pk_field(reg, z, height, bump, wave, grid, ramp, seed, edge)
    o = pk_mesh(name, V, F, (), role, module)
    if dots and not vis.is_empty:
        pk_dots(name + ' dots', vis, hz, dots[0], dots[1], dots[2], seed=seed + 5, module=module)
    return o, vis, hz


def carpet_bands(name, outline, z, bands, kerb=.15, seed=1, module='planting', step=.015):
    """Halifax-style flat clipped carpet bed: concentric bands following the outline, outer to inner, each
    (width_m or None for the centre, role, height_m, dots or None). Neighbouring bands differ in height by at least
    `step` (raised automatically); the lower band laps 5 cm under the higher, the higher laps 1.2 cm over its edge, and
    the outer band laps 3 cm under the kerb. Returns [(object, visible region, hz), ...]."""
    hs = []
    for i, b in enumerate(bands):
        h = b[2]
        if i and abs(h - hs[-1]) < step:
            h = hs[-1] + step
        hs.append(h)
    out = []; d = 0.
    for i, b in enumerate(bands):
        d_in = None if b[0] is None else d + b[0]
        lo = .03 if i == 0 else (.05 if hs[i] < hs[i - 1] else .012)
        li = 0. if d_in is None or i == len(bands) - 1 else (.05 if hs[i] < hs[i + 1] else .012)
        out.append(bedding_band(f'{name} {i} {b[1]}', outline, z, d, d_in, b[1], kerb=kerb, height=hs[i], lap_out=lo,
                                lap_in=li, seed=seed + 7 * i, module=module, dots=b[3]))
        d = d_in if d_in is not None else d
    return out


# ---- prototype plants ----

def _pk_foliage(g, radius, height, rnd, leaves=32, lobes=0, bump=.02, wave=.08, leaf_w=1., ovate=True):
    """Leafy perennial mound: a small low core (radius x 0.30, hidden) clothed in keeled leaves that spring from it and
    arch out and down (top leaves rising, a basal skirt reaching the soil), so the clump reads as a mound of overlapping
    leaves; leaf_w scales leaf width (0.5 lanceolate salvia, 0.3 divided yarrow); lobes>0 adds smooth shrubby lobes."""
    core = (0., 0., height * .22); cr = (radius * .30, radius * .30, height * .45)
    _pk_dome(g, core, cr, -PK_SINK, seed=rnd.randrange(1 << 20), bump=bump * .5, wave=wave, seg=12, rings=5)
    for k in range(lobes):
        a = rnd.uniform(0, 2 * math.pi); d = radius * rnd.uniform(.15, .4); rr = radius * rnd.uniform(.5, .65)
        hz_ = height * rnd.uniform(.85, 1.0)
        _pk_dome(g, (d * math.cos(a), d * math.sin(a), hz_ - rr * .9), (rr, rr, rr * .9), -PK_SINK, seed=rnd.randrange(1 << 20),
                 bump=bump, wave=wave * 1.6, lo=rr * .04, seg=18, rings=8)
    top = cr[2] + core[2]
    for k in range(leaves):
        phi = k * 2.39996 + rnd.uniform(-.2, .2); q = (k + .5) / leaves          # q: 0 = crown leaves, 1 = basal skirt
        lat = math.radians(15 + 70 * q)
        p0 = (cr[0] * .8 * math.sin(lat) * math.cos(phi), cr[1] * .8 * math.sin(lat) * math.sin(phi),
              max(.0, core[2] + cr[2] * .8 * math.cos(lat)))
        reach = radius - math.hypot(p0[0], p0[1])
        elev = math.radians(55 - 55 * q + rnd.uniform(-8, 8)); bend = math.radians(70 + 35 * q)
        L = max(radius * .4, reach * 1.2) * rnd.uniform(.85, 1.1)
        _pk_blade(g, _pk_arc(p0, phi, elev, bend, L, 6, floor=.012), phi + rnd.uniform(-.35, .35),
                  radius * (.36 + .08 * q) * leaf_w * rnd.uniform(.85, 1.15), fold=.22 if ovate else .3, ovate=ovate)
    return top


def flower_head_cluster(kit, name, head='daisy', heads=7, height=.65, spread=.32, foliage=.26, size=1., head_role='pk_pink',
                        boss_role='pk_boss', leaf_role='pk_leaf', stem_role=None, seed=1, droop=.5, leaf_w=1., leaves=32,
                        head_role2=None):
    """One flowering perennial clump as a kit prototype: a leafy mound with `heads` stems rising to smooth heads of one
    kind (stems share the leaf role unless stem_role is given, to save instance nodes):
      'daisy'   coneflower / rudbeckia: scalloped, drooping ray disc round a domed boss (boss_role);
      'spike'   salvia / veronica: dense whorled spire with a tapered tip;
      'umbel'   yarrow / sedum: flat-topped corymb of small smooth floret domes;
      'cup'     poppy / tulip / anemone: a bowl of four broad petals round a dark boss (boss_role);
      'panicle' astilbe / panicle hydrangea / phlox: loose conical floret panicle;
      'mophead' hydrangea: 7-9 heads, each a smooth dome under nine smooth floret-cluster domes (a fine lumpy outline,
                never creased or flaky; head_role2 = their role, default head_role), seated in a shrubby mound of
                dark lobes (pk_shrub_core) skinned in broad leaf cards.
    Heights are metres above the soil; place it with kit.place() or kit.place_in()."""
    rnd = _pkr.Random(seed); stem_role = stem_role or leaf_role
    parts = _pk_parts(leaf_role, stem_role, head_role, *([head_role2] if head_role2 else []),
                      *([boss_role] if head in ('daisy', 'cup') else []))
    if head == 'mophead':
        fh = height * .78; core = parts.setdefault('pk_shrub_core', PkGeo())
        hull = [((0., 0., fh * .3), (foliage * .85, foliage * .8, fh * .55))]
        _pk_dome(core, hull[0][0], hull[0][1], -PK_SINK, seed=seed, bump=.008, wave=.4, seg=14, rings=6)
        for k in range(4):
            a = k * 1.5708 + rnd.uniform(-.4, .4); d = foliage * rnd.uniform(.25, .45); rr = foliage * rnd.uniform(.45, .55)
            c = (d * math.cos(a), d * math.sin(a), fh - rr * .85); hull.append((c, (rr, rr, rr * .85)))
            _pk_dome(core, c, hull[-1][1], -PK_SINK, seed=rnd.randrange(1 << 20), bump=.008, wave=.4, seg=12, rings=5)
        _pk_leaf_skin(parts[leaf_role], parts[leaf_role], hull, leaves * 22, .09 * size, fh, rnd)
        dome = parts[head_role2 or head_role]
        for k in range(heads):
            a = k * 2.39996 + rnd.uniform(-.3, .3); d = foliage * .78 * math.sqrt((k + .5) / heads)
            hr = .13 * size * rnd.uniform(.88, 1.12)
            zc = fh * (1 - .45 * (d / foliage) ** 2) + hr * .4
            c = (d * math.cos(a), d * math.sin(a), zc)
            _pk_ball(dome, c, (hr * .8, hr * .8, hr * .72), seg=10, rings=5)
            for j in range(9):                                   # floret clusters: a fine, smooth lumpy (never creased) outline
                q = 0 if j < 6 else 1; aj = j * (1.0472 if q == 0 else 2.0944) + a + q * .5
                u = _pk_norm((math.cos(aj), math.sin(aj), .35 if q == 0 else 1.3)); sr = hr * rnd.uniform(.36, .42)
                _pk_ball(dome, (c[0] + hr * .62 * u[0], c[1] + hr * .62 * u[1], c[2] + hr * .55 * u[2]), (sr, sr, sr * .85), seg=8, rings=5)
        return kit.proto(name, parts)
    _pk_foliage(parts[leaf_role], foliage, foliage * 1.15, rnd, leaves=leaves, leaf_w=leaf_w, ovate=leaf_w > .45)
    for k in range(heads):
        a = rnd.uniform(0, 2 * math.pi); d = spread * rnd.uniform(.25, 1.0); hgt = height * rnd.uniform(.82, 1.08)
        top = (d * math.cos(a), d * math.sin(a), hgt)
        mid = (top[0] * .55 + rnd.uniform(-.03, .03), top[1] * .55 + rnd.uniform(-.03, .03), hgt * .55)
        base = (top[0] * .15, top[1] * .15, foliage * .35)
        _pk_tube(parts[stem_role], [base, mid, top], .007 * size, .004 * size, 5)
        lean = _pk_norm((top[0] - mid[0], top[1] - mid[1], max(.05, top[2] - mid[2]) * 2.2))
        if head == 'daisy':
            _pk_daisy(parts[head_role], parts[boss_role], top, .042 * size * rnd.uniform(.85, 1.15), 11, droop,
                      _pk_norm((lean[0] * .8, lean[1] * .8, 1.)), cone=1.6 if droop > .35 else 1.0)
        elif head == 'spike':
            _pk_spike(parts[head_role], (top[0], top[1], top[2] - .01), lean, .17 * size * rnd.uniform(.8, 1.15), .016 * size,
                      rnd.randrange(1 << 20))
        elif head == 'cup':
            _pk_cup(parts[head_role], parts[boss_role], (top[0], top[1], top[2] - .005), .045 * size * rnd.uniform(.85, 1.15),
                    _pk_norm((lean[0] * .6, lean[1] * .6, 1.)))
        elif head == 'panicle':
            _pk_panicle(parts[head_role], (top[0], top[1], top[2] - .03), lean, .26 * size * rnd.uniform(.85, 1.15),
                        .055 * size, rnd)
        else:
            _pk_corymb(parts[head_role if k % 3 or not head_role2 else head_role2], (top[0], top[1], top[2] + .004),
                       .05 * size * rnd.uniform(.85, 1.15), rnd)
    return kit.proto(name, parts)


def lavender(kit, name, radius=.30, height=.52, spikes=38, leaf_role='pk_lav_leaf', head_role='pk_lavender', seed=1):
    """Lavender / catmint / perovskia as a kit prototype: a low grey-sage mound of narrow needle leaves under a dense
    dome-shaped haze of thin wiry stems, each ending in a slim smooth flower spike (never solid capsules)."""
    rnd = _pkr.Random(seed); parts = _pk_parts(leaf_role, head_role); g = parts[leaf_role]
    fh = height * .42
    _pk_dome(g, (0., 0., fh * .3), (radius * .55, radius * .55, fh * .62), -PK_SINK, seed=seed, bump=.008, wave=.1, seg=14, rings=5)
    for k in range(84):
        phi = k * 2.39996 + rnd.uniform(-.2, .2); q = (k + .5) / 84
        p0 = (radius * .4 * q ** .5 * math.cos(phi), radius * .4 * q ** .5 * math.sin(phi), fh * (.75 - .5 * q))
        _pk_blade(g, _pk_arc(p0, phi, math.radians(70 - 50 * q), math.radians(40), radius * rnd.uniform(.45, .65), 4, floor=.01),
                  phi, .014, fold=.3)
    for k in range(spikes):
        phi = k * 2.39996 + rnd.uniform(-.25, .25); q = (k + .5) / spikes; d = radius * .9 * q ** .5
        H = height * (1 - .3 * q ** 1.5) * rnd.uniform(.9, 1.06)
        top = (d * math.cos(phi) * 1.25, d * math.sin(phi) * 1.25, H)
        b0 = (d * .3 * math.cos(phi), d * .3 * math.sin(phi), fh * .6)
        mid = ((b0[0] + top[0]) / 2, (b0[1] + top[1]) / 2, (b0[2] + top[2]) / 2 - .01)
        _pk_tube(g, [b0, mid, top], .0035, .0025, 3)
        ax = _pk_norm((top[0] - mid[0], top[1] - mid[1], top[2] - mid[2]))
        L = .10 * rnd.uniform(.85, 1.2)
        _pk_lathe(parts[head_role], (top[0] - ax[0] * .005, top[1] - ax[1] * .005, top[2] - ax[2] * .005), ax, L,
                  lambda q: .0115 * min(1., q * 5 + .2) * (1 - q) ** .45, seg=6, rings=6)
    return kit.proto(name, parts)


def arching_grass(kit, name, blades=44, height=.55, width=.016, role='pk_blade', crown_role='pk_crown', plume_role=None,
                  plumes=0, plume_height=1.25, seed=1):
    """Ornamental grass tuft as a kit prototype: `blades` keeled, tapering blades rising steeply from a low dark crown
    (3 cm proud, mostly hidden by blade bases) and arching out and over under their own weight, with optional `plumes`
    upright stems carrying feathery plumes (plume_role): a smooth slim spindle wrapped in 22 hair-fine spikelets angled
    off a nodding rachis, at plume_height x height (+-10% per plume)."""
    rnd = _pkr.Random(seed); parts = _pk_parts(role, crown_role, *([plume_role] if plume_role else []))
    _pk_dome(parts[crown_role], (0., 0., -.02), (.085, .085, .05), -PK_SINK, seed=seed, bump=.004, wave=.05, seg=12, rings=4)
    for k in range(blades):
        phi = rnd.uniform(0, 2 * math.pi); rr = rnd.uniform(0, .07); q = rnd.random()
        elev = math.radians(88 - 38 * q); bend = math.radians(30 + 110 * q)
        L = height * rnd.uniform(.85, 1.25) * (1.15 - .25 * q)
        p0 = (rr * math.cos(phi), rr * math.sin(phi), -PK_SINK - (.02 if rnd.random() < .2 else 0.))
        _pk_blade(parts[role], _pk_arc(p0, phi, elev, bend, L, 8, floor=.03), phi + rnd.uniform(-.25, .25), width * rnd.uniform(.8, 1.2))
    if plume_role:
        for k in range(plumes):
            phi = rnd.uniform(0, 2 * math.pi); H = height * plume_height * rnd.uniform(.9, 1.1)
            top = (math.cos(phi) * H * .12, math.sin(phi) * H * .12, H)
            _pk_tube(parts[role], [(0., 0., -PK_SINK), (top[0] * .5, top[1] * .5, H * .55), top], .004, .003, 4)
            ax = _pk_norm((top[0] * 1.3, top[1] * 1.3, H)); Lp = .27 * rnd.uniform(.85, 1.15)
            b = (top[0] - ax[0] * Lp * .85, top[1] - ax[1] * Lp * .85, top[2] - ax[2] * Lp * .85)
            _pk_lathe(parts[plume_role], b, ax, Lp, lambda q: .014 * min(1., q * 4 + .15) * (1 - q) ** .6, seg=7, rings=7)
            for j in range(22):
                q = .08 + .84 * j / 21; a = j * 2.39996
                p = tuple(b[i] + ax[i] * Lp * q for i in range(3))
                rr = _pk_norm(_pk_rot(_pk_norm(_pk_cross(ax, (math.cos(a), math.sin(a), 0.))), ax, a))
                d = _pk_norm(tuple(ax[i] * .9 + rr[i] * rnd.uniform(.25, .45) for i in range(3)))
                Ls = (.045 + .03 * math.sin(math.pi * q)) * rnd.uniform(.85, 1.15)
                pts = [p, tuple(p[i] + d[i] * Ls * .5 for i in range(3)), tuple(p[i] + d[i] * Ls for i in range(3))]
                _pk_blade(parts[plume_role], pts, a, .0045, fold=.4)
    return kit.proto(name, parts)


def _pk_leaf_skin(gd, gl, hull, n, leaf, height, rnd, light=.45):
    """Skin a hull of lobes [((c), (r)), ...] in n broad cupped leaf cards of length ~leaf, lying mostly along the
    surface and lifting 20-35 degrees off it (gl above `light` x height, gd below, with jitter); leaves buried inside a
    neighbouring lobe are skipped. Shared by shrub_mass and the mophead's shrubby mound."""
    wts = [r[0] * r[2] for _, r in hull]; placed = 0; tries = 0
    while placed < n and tries < n * 6:
        tries += 1
        i = rnd.choices(range(len(hull)), wts)[0]; c, r = hull[i]
        u = _pk_norm((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1) * .8 + .25))
        p = (c[0] + r[0] * u[0], c[1] + r[1] * u[1], c[2] + r[2] * u[2])
        if p[2] < .04:
            continue
        if any(j != i and sum(((p[k] - cc[k]) / rr_[k]) ** 2 for k in range(3)) < .8 for j, (cc, rr_) in enumerate(hull)):
            continue
        nrm = _pk_norm((u[0] / r[0], u[1] / r[1], u[2] / r[2]))
        jit = _pk_norm((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1)))
        tan = _pk_norm(tuple(jit[k] - nrm[k] * sum(jit[i] * nrm[i] for i in range(3)) for k in range(3)))
        d = _pk_norm(tuple(tan[k] + nrm[k] * rnd.uniform(.35, .7) + (-.15 if k == 2 else 0.) for k in range(3)))
        dn = sum(nrm[k] * d[k] for k in range(3))
        cn = _pk_rot(_pk_norm(tuple(nrm[k] - dn * d[k] for k in range(3))), d, rnd.uniform(-.4, .4))
        L = leaf * rnd.uniform(.8, 1.2)
        base = tuple(p[k] - nrm[k] * .012 for k in range(3))
        if base[2] + min(0., d[2]) * L < .015:                  # no leaf tip below the soil
            continue
        up = (p[2] / height) + rnd.uniform(-.3, .3)
        _pk_card(gl if up > light else gd, base, d, cn, L, L * .78, fold=.12)
        placed += 1


def shrub_mass(kit, name, radius=.8, height=1.0, lobes=7, role='pk_leaf_dark', role2='pk_leaf', seed=1, leaves=None, leaf=None,
               core_role='pk_shrub_core'):
    """Grounded leafy shrub as a kit prototype (sizes 0.4-1.6 m): a smooth inner hull (a broad buried base lobe and
    `lobes` overlapping smooth lobes, no ridged noise) clothed in a skin of broad cupped leaf cards (role2 above, role
    below) lying along the surface and lifting 20-35 degrees off it, so the silhouette is broken by leaves, not by
    spurs or creases, and gaps in the very dark hull (core_role) read as foliage depth. leaves defaults to about 560
    per m2 of hull."""
    rnd = _pkr.Random(seed); parts = _pk_parts(core_role, role, role2); g = parts[core_role]
    hull = [((0., 0., height * .28), (radius * .82, radius * .78, height * .42))]
    _pk_dome(g, hull[0][0], hull[0][1], -PK_SINK, seed=seed, bump=.01, wave=.45, lo=.012, seg=16, rings=6)
    for k in range(lobes):
        a = 2 * math.pi * k / lobes + rnd.uniform(-.3, .3); up = rnd.random(); d = radius * (.55 - .4 * up) * rnd.uniform(.8, 1.1)
        rr = radius * rnd.uniform(.34, .46); cz = height * (.40 + .32 * up)
        rz = min(rr * .95, height * .94 - cz)
        c = (d * math.cos(a), d * math.sin(a), cz); r = (rr, rr * rnd.uniform(.85, 1), rz)
        hull.append((c, r))
        _pk_dome(g, c, r, -PK_SINK, seed=rnd.randrange(1 << 20), bump=.01, wave=.45, lo=.01, seg=13, rings=6)
    area = sum(r[0] * r[2] for _, r in hull) * 2.5
    _pk_leaf_skin(parts[role], parts[role2], hull, leaves or int(min(1500, max(220, 560 * area))),
                  leaf or (.075 + .05 * min(1., height / 1.4)), height, rnd)
    return kit.proto(name, parts)


def bedding_cushion(kit, name, radius=.28, height=.2, role='pk_leaf_red', floret_role='pk_red', florets=80, seed=1):
    """Low mounded bedding plant (begonia, impatiens, ageratum, alyssum) as a kit prototype: a smooth softly lumpy
    leafy cushion skinned in small floret domes over its upper surface; for ring and strip beds."""
    rnd = _pkr.Random(seed); parts = _pk_parts(role, floret_role)
    _pk_dome(parts[role], (0., 0., height * .2), (radius, radius * .94, height * .8), -PK_SINK, seed=seed, bump=.012, wave=.12,
             seg=20, rings=7)
    for k in range(florets):
        u = _pk_norm((rnd.gauss(0, 1), rnd.gauss(0, 1), abs(rnd.gauss(0, 1)) + .35))
        p = (radius * .97 * u[0], radius * .94 * .97 * u[1], height * .2 + height * .8 * .97 * u[2])
        if p[2] < .04:
            continue
        fr = .016 * rnd.uniform(.8, 1.2)
        _pk_ball(parts[floret_role], p, (fr, fr, fr * .8), seg=5, rings=3)
    return kit.proto(name, parts)


def pot_plant(kit, name, pot_r=.22, pot_h=.34, plant='geranium', pot_role='pk_terracotta', soil_role='pk_mulch',
              leaf_role='pk_leaf', flower_role='pk_red', seed=1):
    """Pot plant as a kit prototype: a smooth tapered terracotta pot with a rolled rim (its foot sunk 1 cm), a soil top
    set 4 cm below the rim and, unless plant=None, a geranium (round-leaved mound with corymb flower clusters) or a
    'box' ball (leaf-skinned clipped sphere). The plant's base sits on the soil; the trunk of a wall climber can rise
    from an empty pot."""
    rnd = _pkr.Random(seed); parts = _pk_parts(pot_role, soil_role, *([leaf_role, flower_role] if plant == 'geranium' else
                                                                      [leaf_role] if plant == 'box' else []))
    prof = [(0., -.01), (pot_r * .70, -.01), (pot_r * .74, .02), (pot_r * .94, pot_h - .045), (pot_r * 1.06, pot_h - .04),
            (pot_r * 1.09, pot_h - .015), (pot_r * 1.03, pot_h), (pot_r * .93, pot_h - .01), (pot_r * .9, pot_h - .07), (0., pot_h - .07)]
    seg = 22; fs = []; ring = prof[1:-1]
    vs = [(0., 0., prof[0][1])]
    for r, z in ring:
        for j in range(seg):
            a = 2 * math.pi * j / seg; vs.append((r * math.cos(a), r * math.sin(a), z))
    vs.append((0., 0., prof[-1][1])); m = len(ring)
    for j in range(seg):
        fs.append((0, 1 + (j + 1) % seg, 1 + j))
    for i in range(m - 1):
        for j in range(seg):
            k = (j + 1) % seg; a0 = 1 + i * seg; a1 = a0 + seg
            fs.append((a0 + j, a0 + k, a1 + k, a1 + j))
    t = len(vs) - 1; last = 1 + (m - 1) * seg
    for j in range(seg):
        fs.append((last + j, last + (j + 1) % seg, t))
    parts[pot_role].add(vs, fs, [0])
    sz = pot_h - .04; sr = pot_r * .925                         # soil disc: its rim buried in the pot's inner wall
    parts[soil_role].add([(0., 0., sz)] + [(sr * math.cos(2 * math.pi * j / seg), sr * math.sin(2 * math.pi * j / seg), sz - .004)
                                           for j in range(seg)], [(0, 1 + j, 1 + (j + 1) % seg) for j in range(seg)])
    if plant == 'geranium':
        g = PkGeo(); _pk_foliage(g, pot_r * 1.25, .2, rnd, leaves=24)
        parts[leaf_role].add([(x, y, z + sz - .01) for x, y, z in g.v], g.f)
        for k in range(7):
            a = k * 2.39996; d = pot_r * .75 * math.sqrt((k + .5) / 7); top = (d * math.cos(a), d * math.sin(a), sz + .26 + rnd.uniform(-.03, .03))
            _pk_tube(parts[leaf_role], [(top[0] * .3, top[1] * .3, sz + .05), top], .005, .004, 4)
            _pk_corymb(parts[flower_role], top, .045, rnd, florets=8)
    elif plant == 'box':
        g = PkGeo(); g2 = PkGeo()
        _pk_dome(g, (0., 0., sz + pot_r * .9), (pot_r * 1.05, pot_r * 1.05, pot_r * 1.0), sz - .01, seed=seed, bump=.006, wave=.2, seg=18, rings=8)
        for k in range(220):
            u = _pk_norm((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1) * .8 + .2))
            p = (pot_r * 1.05 * u[0], pot_r * 1.05 * u[1], sz + pot_r * .9 + pot_r * u[2])
            if p[2] < sz + .03:
                continue
            ref = (0., 0., 1.) if abs(u[2]) < .95 else (1., 0., 0.)
            cn = _pk_norm(_pk_cross(_pk_norm(_pk_cross(u, ref)), u))
            _pk_card(g, tuple(p[i] - u[i] * .01 for i in range(3)), u, cn, .035, .02)
        parts[leaf_role].add(g.v, g.f, g.flat)
    return kit.proto(name, parts)


def perennial_drift(kit, poly, z, mix, kerb=.15, spacing=.42, seed=1, drift=2.4, scale=(.85, 1.15), underlay='pk_groundcover',
                    lean=.08):
    """Naturalistic drift planting: Poisson-spaced positions inside the bed minus the kerb, each assigned a species from
    mix = [(proto, weight[, unused]), ...] by low-frequency noise fields (wavelength about `drift` m), so species form
    contiguous interlocking drifts (Prince's Island, Oudolf) rather than salt-and-pepper. Each plant passes the kit
    clearance rule with its own base radius (falling back to the next-best species that fits, else skipped), gets a
    non-uniform scale and a small lean, and by default a groundcover underlay (underlay=None to skip) hides the fill.
    Returns the number placed."""
    rnd = _pkr.Random(seed); fields = [_PkNoise(seed + 17 * i, 2 * math.pi / drift) for i in range(len(mix))]
    reg = pk_region(poly, kerb); n = 0
    if underlay:
        groundcover(f'drift underlay {seed}', reg.buffer(.03), z, kerb=0., height=.045, role=underlay, seed=seed + 3,
                    module=kit.module, grid=.22, edge=.1)
    for x, y in pk_scatter(poly, spacing, kerb=kerb, margin=PK_CLEAR, seed=seed):
        order = sorted(range(len(mix)), key=lambda i: -(fields[i](x, y) + 1.4 * math.log(mix[i][1])))
        for i in order:
            s = rnd.uniform(*scale)
            if kit.fits(mix[i][0], x, y, s, reg):
                kit.place(mix[i][0], x, y, z, rnd.uniform(0, 2 * math.pi), s, sy=s * rnd.uniform(.9, 1.1),
                          sz=s * rnd.uniform(.88, 1.12), lean=(rnd.uniform(-lean, lean), rnd.uniform(-lean, lean)))
                n += 1
                break
    return n


# ---- wall-trained climbers and parapet cascades ----

def _pk_profile(profile, step=.04, smooth=.08):
    """Resample a wall cross-section polyline [(n, z), ...] (n outward from the wall face) every `step` m; returns
    arrays (s, n, z, nn, nz) with outward normals (right of the direction of travel) averaged over +-smooth m, so an
    offset surface rounds over corners instead of folding."""
    P = [tuple(p) for p in profile]; S = [0.]
    for a, b in zip(P, P[1:]):
        S.append(S[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    ss = _pknp.arange(0., S[-1] + 1e-9, step)
    if ss[-1] < S[-1] - 1e-6:
        ss = _pknp.append(ss, S[-1])
    N = _pknp.interp(ss, S, [p[0] for p in P]); Z = _pknp.interp(ss, S, [p[1] for p in P])
    segn = [((b[1] - a[1]) / max(1e-9, S[i + 1] - S[i]), -(b[0] - a[0]) / max(1e-9, S[i + 1] - S[i])) for i, (a, b) in enumerate(zip(P, P[1:]))]
    NN = []; NZ = []
    for s in ss:
        acc = [0., 0.]
        for w in _pknp.linspace(-smooth, smooth, 9):
            q = min(S[-1] - 1e-9, max(0., s + w)); i = max(0, min(len(segn) - 1, int(_pknp.searchsorted(S, q, 'right')) - 1))
            acc[0] += segn[i][0]; acc[1] += segn[i][1]
        L = math.hypot(*acc) or 1.; NN.append(acc[0] / L); NZ.append(acc[1] / L)
    return ss, N, Z, _pknp.array(NN), _pknp.array(NZ)


def wall_drape(name, p0, p1, out, profile, curtain, openings=(), thickness=.2, bump=.07, wave=.3, grid=.1, ramp=.14,
               role='pk_leaf', role2='pk_leaf_dark', bract_roles=('pk_magenta', 'pk_bract2'), bracts_per_m2=6, trunks=(),
               trunk_role='pk_bark', seed=1, module='planting', tongues=4, cover=1., leaf_per_m2=55, mass_bracts_per_m2=170):
    """Wall-trained climber or parapet cascade (bougainvillea, wisteria, ivy, jasmine) as unique geometry: a continuous
    leafy canopy shell draped over a wall cross-section `profile` [(n, z), ...] (n measured outward from the wall face
    line p0-p1, `out` its unit outward normal (x, y)), listed from the hanging lower end up and over the coping. The
    shell is a heightfield in (u along the wall, s along the profile) whose edges dive 2.5 cm into the masonry, so it is
    grounded on the wall and coping. Its hanging edge sits at s = curtain(u) metres (a float or a function) with
    `tongues` longer hanging lobes and a fringe of dangling leaves; `openings` [(u0, u1, z0, z1), ...] (doors, windows,
    measured on the wall face) are cut out with a 7 cm margin so it never crosses them. Lumpy bract masses (bract_roles,
    `cover` scales them) ride on about half the shell with their edges diving into it, leaf cards (leaf_per_m2) and
    bract specks (bracts_per_m2) texture it; `trunks` [(u, (x, y, z) root), ...] add woody stems from a pot or
    planter that climb into the canopy and branch along the wall. Returns the shell area in m2."""
    rnd = _pkr.Random(seed); ss, PN, PZ, NN, NZ = _pk_profile(profile)
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); tx, ty = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    Smax = float(ss[-1]); z0p = profile[0][1]
    cur = curtain if callable(curtain) else (lambda u, c=curtain: c)
    tg = [(rnd.uniform(.12, .88) * L, rnd.uniform(.25, .6), rnd.uniform(.1, .2)) for _ in range(tongues)]
    nz_ = _PkNoise(seed + 5, 2 * math.pi / 1.1)

    def lo(u):
        return max(.0, cur(u) + .12 * nz_(u, 0.) - sum(dp * math.exp(-((u - uc) / w) ** 2) for uc, dp, w in tg))
    us = _pknp.linspace(0., L, max(12, int(L / .05)))
    poly = [(float(u), lo(float(u))) for u in us] + [(L, Smax), (0., Smax)]
    reg = _PkPolygon(poly).buffer(0).intersection(_pksh.box(.02, 0., L - .02, Smax - .015))
    for u0, u1, a, b in openings:
        reg = reg.difference(_pksh.box(u0 - .07, a - z0p - .07, u1 + .07, b - z0p + .07))
    reg = reg.buffer(-.01).buffer(.01)
    V, F, hz = _pk_field(reg, 0., thickness, bump, wave, grid, ramp, seed, mid=True)

    def world(u, s, h):
        n = _pknp.interp(s, ss, PN); zz = _pknp.interp(s, ss, PZ); a = _pknp.interp(s, ss, NN); c = _pknp.interp(s, ss, NZ)
        L2 = math.hypot(a, c) or 1.; a, c = a / L2, c / L2
        w = n + h * a
        return (p0[0] + u * tx + w * out[0], p0[1] + u * ty + w * out[1], zz + h * c), (a, c)
    pk_mesh(name + ' canopy', [world(u, s, h)[0] for u, s, h in V], F, (), role, module)
    # bract masses: lumpy magenta clouds riding on the canopy (their edges dive into it), covering about half of it
    inner = reg.buffer(-.06)
    blobs = [_pksh.Point(u, s).buffer(rnd.uniform(.14, .32) * cover ** .5, quad_segs=6)
             for u, s in (pk_scatter(inner, .42, seed=seed + 4) if not inner.is_empty else [])]
    patch = _pksh.union_all(blobs).intersection(inner) if blobs else None
    if patch is not None and not patch.is_empty:
        Vb, Fb, hb = _pk_field(patch, 0., .03, .012, .2, .1, .04, seed + 6, edge=.07, base=lambda X, Y: hz(X, Y))
        pk_mesh(name + ' bract masses', [world(u, s, h)[0] for u, s, h in Vb], Fb, (), bract_roles[0], module)
        gm = {ro: PkGeo() for ro in bract_roles}            # papery bracts: dense flecks facing every way over the masses
        for u, s in pk_scatter(patch, 1 / math.sqrt(mass_bracts_per_m2) * .85, seed=seed + 7):
            r = rnd.uniform(.022, .036); (x, y, z), (a, c) = world(u, s, hb(u, s) - r * .45)
            nv = _pk_norm((out[0] * a + rnd.uniform(-.6, .6), out[1] * a + rnd.uniform(-.6, .6), c + rnd.uniform(-.6, .6)))
            _pk_speck(gm[bract_roles[rnd.randrange(len(bract_roles))]], (x, y, z), nv, r, rnd.uniform(0, 6.3))
        for ro, g in gm.items():
            if g.f:
                pk_mesh(f'{name} mass bracts {ro}', g.v, g.f, (), ro, module)
    # leaf cards and bract specks for texture
    gl = PkGeo(); gs = {ro: PkGeo() for ro in bract_roles}
    for u, s in (pk_scatter(inner, 1 / math.sqrt(leaf_per_m2) * .85, seed=seed + 8) if not inner.is_empty else []):
        h = hz(u, s); (x, y, z), (a, c) = world(u, s, h - .01)
        nv = _pk_norm((out[0] * a, out[1] * a, c)); jit = _pk_norm((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1)))
        tan = _pk_norm(tuple(jit[k] - nv[k] * sum(jit[i] * nv[i] for i in range(3)) for k in range(3)))
        d = _pk_norm(tuple(tan[k] + nv[k] * .5 for k in range(3))); Lc = rnd.uniform(.06, .09)
        dn = sum(nv[k] * d[k] for k in range(3))
        _pk_card(gl, (x, y, z), d, _pk_norm(tuple(nv[k] - dn * d[k] for k in range(3))), Lc, Lc * .65)
    if gl.f:
        pk_mesh(name + ' leaves', gl.v, gl.f, (), role2, module)
    for u, s in (pk_scatter(inner, 1 / math.sqrt(bracts_per_m2) * .85, seed=seed + 2) if not inner.is_empty else []):
        h = hz(u, s); g = gs[bract_roles[rnd.randrange(len(bract_roles))]]
        for j in range(4):
            du, ds = rnd.uniform(-.05, .05), rnd.uniform(-.05, .05); r = rnd.uniform(.022, .034)
            hh = hz(u + du, s + ds) if _pksh.contains_xy(reg, u + du, s + ds) else h
            (x, y, z), (a, c) = world(u + du, s + ds, hh - r * .3)
            nv = _pk_norm((out[0] * a + rnd.uniform(-.3, .3), out[1] * a + rnd.uniform(-.3, .3), c + rnd.uniform(-.3, .3)))
            _pk_speck(g, (x, y, z), nv, r, rnd.uniform(0, 6.3))
    for ro, g in gs.items():
        if g.f:
            pk_mesh(f'{name} bracts {ro}', g.v, g.f, (), ro, module)
    # dangling leaf fringe along the hanging edge
    fr = PkGeo(); fb = PkGeo()
    for u in _pknp.arange(.15, L - .15, .06):
        u = float(u) + rnd.uniform(-.02, .02); s = lo(u) + .05
        if not reg.buffer(.02).contains(_pksh.points(u, s)):
            continue
        (x, y, z), (a, c) = world(u, s, max(.02, hz(u, s) * .5))
        d = _pk_norm((out[0] * a * .5, out[1] * a * .5, -1.))
        cn = (out[0], out[1], 0.)
        for j in range(2):
            Lf = rnd.uniform(.07, .13)
            _pk_card(fb if rnd.random() < .3 else fr, (x + tx * rnd.uniform(-.02, .02), y + ty * rnd.uniform(-.02, .02), z),
                     _pk_norm((d[0] + tx * rnd.uniform(-.3, .3), d[1] + ty * rnd.uniform(-.3, .3), d[2])), cn, Lf, Lf * .6)
    if fr.f:
        pk_mesh(name + ' fringe', fr.v, fr.f, (), role2, module)
    if fb.f:
        pk_mesh(name + ' fringe bracts', fb.v, fb.f, (), bract_roles[0], module)
    # woody trunks from a root point, climbing into the canopy and branching along the wall
    tb = PkGeo()
    for u, root in trunks:
        for u0, u1, a, b in openings:
            if u0 - .1 < u < u1 + .1:
                raise ValueError(f'{name}: trunk at u={u:.2f} crosses an opening')
        s_in = lo(u) + .35; (x1, y1, z1), _ = world(u, s_in, thickness * .3)
        (xm, ym, zm), _ = world(u, max(0., (z1 - z0p) * .5), .05)
        pts = [root, ((root[0] + xm) / 2, (root[1] + ym) / 2, (root[2] + zm) / 2), (xm, ym, zm), (x1, y1, z1)]
        _pk_tube(tb, pts, .035, .022, 6)
        for side in (-1, 1):
            br = [world(u + side * k * .22, s_in + k * .18, thickness * .3)[0] for k in range(4)]
            _pk_tube(tb, [(x1, y1, z1)] + br[1:], .018, .01, 5)
    if tb.f:
        pk_mesh(name + ' trunks', tb.v, tb.f, (), trunk_role, module)
    return float(reg.area)


# ---- showcase layout ----
pk_palette(PALETTE)
KIT = None


def protos(kit):
    """The showcase prototype library: two seeds for the species that repeat most, one for accents, and the shrub size
    range 0.4 / 0.8 / 1.2 / 1.6 m."""
    P = {}
    for s in (1, 2):
        P[f'mophead{s}'] = flower_head_cluster(kit, f'hydrangea{s}', 'mophead', heads=8, height=.95, foliage=.48,
                                                head_role='pk_white' if s == 1 else 'pk_cream', leaf_role='pk_leaf_dark',
                                                leaves=26, seed=10 + s)
        P[f'salvia{s}'] = flower_head_cluster(kit, f'salvia{s}', 'spike', heads=11, height=.48, spread=.26, foliage=.27,
                                               head_role='pk_purple', leaf_w=.5, leaves=28, seed=40 + s)
        P[f'feather{s}'] = arching_grass(kit, f'feather_reed{s}', blades=60, height=.5, width=.018, role='pk_straw', plume_role='pk_plume',
                                         plumes=6 if s == 1 else 5, plume_height=2.3 if s == 1 else 1.8, seed=90 + s)
    P['cone1'] = flower_head_cluster(kit, 'coneflower1', 'daisy', heads=9, height=.66, foliage=.3, head_role='pk_pink', droop=.35,
                                     size=1.3, seed=21)
    P['panicle1'] = flower_head_cluster(kit, 'panicle1', 'panicle', heads=6, height=.82, spread=.26, foliage=.3, head_role='pk_white',
                                        leaf_role='pk_leaf_dark', seed=61)
    P['lavender1'] = lavender(kit, 'lavender1', radius=.30, height=.52, seed=71)
    P['fountain1'] = arching_grass(kit, 'fountain_grass1', blades=70, height=.55, width=.019, seed=81)
    P['blue1'] = arching_grass(kit, 'blue_grass1', blades=56, height=.32, width=.013, role='pk_blade_blue', crown_role='pk_crown_blue',
                               seed=101)
    P['rud1'] = flower_head_cluster(kit, 'rudbeckia1', 'daisy', heads=10, height=.55, foliage=.3, head_role='pk_yellow',
                                    leaf_role='pk_leaf_hairy', droop=.15, size=1.25, seed=31)
    P['yarrow1'] = flower_head_cluster(kit, 'yarrow1', 'umbel', heads=7, height=.6, foliage=.3, head_role='pk_yellow', leaf_w=.3,
                                       leaves=40, seed=51)
    P['yarrow2'] = flower_head_cluster(kit, 'yarrow2', 'umbel', heads=7, height=.58, foliage=.28, head_role='pk_cream', leaf_w=.3,
                                       leaves=40, seed=52)
    P['poppy1'] = flower_head_cluster(kit, 'poppy1', 'cup', heads=7, height=.55, spread=.24, foliage=.22, head_role='pk_orange',
                                      leaf_role='pk_leaf2', leaf_w=.7, leaves=24, seed=111)
    for key, r, h, s in (('sh04', .30, .40, 1), ('sh08a', .50, .80, 2), ('sh08b', .52, .78, 3), ('sh12a', .66, 1.2, 4),
                         ('sh12b', .70, 1.15, 5), ('sh16', .85, 1.6, 6)):
        P[key] = shrub_mass(kit, 'shrub_' + key, radius=r, height=h, lobes=5 if h < .5 else 7, seed=120 + s)
    P['begonia_c'] = bedding_cushion(kit, 'begonia_cushion', role='pk_leaf_red', floret_role='pk_red', seed=131)
    P['ageratum_c'] = bedding_cushion(kit, 'ageratum_cushion', radius=.26, role='pk_leaf', floret_role='pk_purple2', seed=132)
    P['alyssum_c'] = bedding_cushion(kit, 'alyssum_cushion', radius=.24, height=.16, role='pk_leaf2', floret_role='pk_white2', seed=133)
    P['geranium_pot'] = pot_plant(kit, 'geranium_pot', seed=141)
    P['box_pot'] = pot_plant(kit, 'box_pot', pot_r=.24, pot_h=.40, plant='box', leaf_role='pk_leaf_dark', seed=142)
    P['big_pot'] = pot_plant(kit, 'climber_pot', pot_r=.30, pot_h=.46, plant=None, seed=143)
    return P


def ground():
    b = Batch()
    b.box('grass', (SX0 + SX1) / 2, (SY0 + SY1) / 2, ZG / 2, SX1 - SX0, SY1 - SY0, ZG)
    for y0, y1 in ((-3.3, -1.7), (4.2, 5.4)):
        b.box('gravel', 0., (y0 + y1) / 2, (ZP + .01) / 2, 27.0, y1 - y0, ZP - .01)
    b.box('paving', 21.45, 4.9, (ZV + .02) / 2, 9.1, 7.0, ZV - .02)
    b.flush('ground')


def bed(name, outline):
    pk_bed(name, outline, ZS, kerb=KERB, kerb_top=KT, kerb_bottom=KB, kit=KIT)
    return outline


def place_ring(kit, p, cx, cy, items, rnd, region):
    for (dx, dy, key) in items:
        s = rnd.uniform(.92, 1.08)
        kit.place_in(p[key], cx + dx, cy + dy, ZS, rnd.uniform(0, 2 * math.pi), s, region=region, aspect=rnd.uniform(.9, 1.1),
                     lean=(rnd.uniform(-.06, .06), rnd.uniform(-.06, .06)))


def plaza(kit, P):
    """B10: a rendered wall with a door and a window, a bougainvillea trained up and over its coping from a pot, a low
    terrace wall with a parapet cascade, and pot plants on the paving."""
    b = Batch(); yf, yb = 7.6, 7.9
    for x0, x1, z0, z1 in ((17.5, 18.2, .03, 3.01), (18.2, 19.2, 2.2, 3.01), (19.2, 20.7, .03, 3.01), (20.7, 21.7, .03, 1.0),
                           (20.7, 21.7, 2.1, 3.01), (21.7, 22.5, .03, 3.01)):
        b.box('stucco', (x0 + x1) / 2, (yf + yb) / 2, (z0 + z1) / 2, x1 - x0, yb - yf, z1 - z0)
    b.box('coping', 20.0, 7.75, 3.04, 5.1, .40, .08)
    b.box('door', 18.7, 7.76, 1.135, 1.1, .08, 2.23)
    b.box('dark_pane', 21.2, 7.73, 1.55, 1.1, .06, 1.2)
    b.box('coping', 21.2, 7.59, .99, 1.16, .14, .06)
    b.box('stucco', 24.25, 5.85, .57, 2.7, .5, 1.08)                        # terrace wall, top at 1.11 (inside its coping)
    b.box('coping', 24.25, 5.84, 1.125, 2.8, .58, .05)
    b.flush('plaza')
    kit.add_obstacle(_pksh.box(17.45, yf, 22.55, yb), 3.0)
    kit.add_obstacle(_pksh.box(22.85, 5.55, 25.65, 6.13), 1.15)
    kit.place(P['big_pot'], 19.95, 7.16, ZV, .3)
    wall_drape('B10 bougainvillea', (17.5, yf), (22.5, yf), (0., -1.), [(0., 1.2), (0., 3.0), (.05, 3.0), (.05, 3.08), (-.32, 3.08)],
               lambda u: .85 + .25 * math.sin(u * 1.7), openings=[(.7, 1.7, 0., 2.2), (3.2, 4.2, 1.0, 2.1)],
               trunks=[(2.45, (19.95, 7.16, ZV + .42))], seed=5, module='planting')
    wall_drape('B10 cascade', (22.9, 5.6), (25.6, 5.6), (0., -1.), [(0., .40), (0., 1.1), (.05, 1.1), (.05, 1.15), (-.52, 1.15)],
               lambda u: .22 + .08 * math.sin(u * 2.3), thickness=.15, tongues=3, seed=9, module='planting')
    for x, y, key in ((17.85, 7.18, 'geranium_pot'), (19.55, 7.2, 'box_pot'), (23.25, 5.08, 'geranium_pot'),
                      (24.35, 5.1, 'box_pot'), (25.35, 5.08, 'geranium_pot')):
        kit.place(P[key], x, y, ZV, x * 1.7)


def planting():
    global KIT
    kit = KIT = PlantKit('planting', instancing=INSTANCING); P = protos(kit); rnd = _pkr.Random(7)
    # B1 flower_head_cluster specimens round a hydrangea, over a groundcover underlay
    o1 = bed('B1 flower heads', pk_ellipse(-10.5, -6.5, 2.4, 1.6))
    groundcover('B1 underlay', o1, ZS, kerb=KERB, height=.045, seed=51)
    place_ring(kit, P, -10.5, -6.5, [(0, .05, 'mophead1'), (-1.35, .5, 'cone1'), (-1.45, -.4, 'rud1'), (1.35, .55, 'panicle1'),
               (1.45, -.4, 'poppy1'), (-.55, -.95, 'salvia1'), (.6, -.95, 'yarrow1'), (-.5, 1.0, 'lavender1'), (.55, 1.0, 'yarrow2')],
               rnd, pk_region(o1, KERB))
    # B2 perennial_drift (underlay by default)
    o2 = bed('B2 perennial drift', pk_blob(-4.0, -6.5, 2.3, 1.6, seed=3))
    perennial_drift(kit, o2, ZS, [(P['cone1'], 1.6), (P['salvia1'], 1), (P['salvia2'], 1), (P['yarrow1'], .8),
                    (P['rud1'], .8), (P['panicle1'], .6), (P['poppy1'], .5)], kerb=KERB, spacing=.46, seed=5, drift=2.0)
    # B3 arching_grass
    o3 = bed('B3 arching grass', pk_ellipse(2.2, -6.5, 2.2, 1.5))
    perennial_drift(kit, o3, ZS, [(P['fountain1'], 1.6), (P['feather1'], 1), (P['feather2'], 1), (P['blue1'], 1.2)],
                    kerb=KERB, spacing=.62, seed=8, drift=2.2)
    # B4 shrub_mass size range, 0.4 to 1.6 m, over an underlay
    o4 = bed('B4 shrub mass', pk_blob(9.0, -6.5, 2.6, 1.7, seed=4))
    groundcover('B4 underlay', o4, ZS, kerb=KERB, height=.045, seed=53)
    place_ring(kit, P, 9.0, -6.5, [(-1.1, .45, 'sh16'), (.35, .6, 'sh12a'), (1.55, .3, 'sh08a'), (-.15, -.55, 'sh08b'),
               (1.15, -.75, 'sh12b'), (-1.6, -.55, 'sh04'), (2.15, -.35, 'sh04'), (-.9, -1.0, 'blue1')], rnd, pk_region(o4, KERB))
    # B5 groundcover with florets and leaf grain
    o5 = bed('B5 groundcover', pk_ellipse(-10.5, 1.0, 2.2, 1.4))
    groundcover('B5 carpet', o5, ZS, kerb=KERB, role='pk_leaf', seed=11, dots=(('pk_pink', 'pk_pink2'), 60, .009, 4),
                grain=(('pk_leaf_light', 'pk_leaf2'), 25, .022))
    # B6 clipped bedding rings with bedding cushions and a salvia at the centre
    o6 = bed('B6 bedding bands', pk_ellipse(-4.0, 1.0, 1.9, 1.9))
    rings = carpet_bands('B6', o6, ZS, [(.30, 'pk_leaf_silver', .07, None),
                                        (.32, 'pk_leaf_red', .085, (('pk_red', 'pk_red2'), 130, .01)),
                                        (.30, 'pk_leaf_dark', .07, (('pk_purple', 'pk_purple2'), 130, .009)),
                                        (None, 'pk_leaf2', .085, (('pk_white2', 'pk_cream'), 110, .009))], kerb=KERB, seed=21)
    hz6 = rings[-1][2]
    kit.place(P['salvia1'], -4.0, 1.0, hz6(-4.0, 1.0) - .03, 0., 1.1)
    for i in range(6):
        a = i * math.pi / 3 + .3; x, y = -4.0 + .62 * math.cos(a), 1.0 + .62 * math.sin(a)
        kit.place_in(P[('begonia_c', 'ageratum_c', 'alyssum_c')[i % 3]], x, y, hz6(x, y) - .03, a, .95)
    # B7 Halifax-style Victorian carpet bed: flat clipped ribbons following the leaf outline round white hydrangeas
    o7 = bed('B7 Halifax carpet bed', pk_leaf(5.3, 1.2, 9.0, 3.1))
    bands = carpet_bands('B7', o7, ZS, [(.28, 'pk_leaf_silver', .07, None),
                                        (.30, 'pk_leaf_red', .085, (('pk_red', 'pk_red2'), 130, .01)),
                                        (.28, 'pk_leaf_dark', .07, (('pk_purple', 'pk_purple2'), 130, .009)),
                                        (None, 'pk_leaf', .085, (('pk_pink', 'pk_pink2'), 120, .009))], kerb=KERB, seed=31)
    _, centre, hz = bands[-1]
    for i, (x, y) in enumerate(pk_scatter(centre, 1.3, margin=.45, seed=6)):
        kit.place_in(P['mophead%d' % (1 + i % 2)], x, y, hz(x, y) - .03, rnd.uniform(0, 2 * math.pi), .8)
    # B8 Prince's-Island-style perennial bed: layered shrub backdrop, drifts of perennials and grasses over a groundcover
    o8 = bed('B8 perennial bed', pk_blob(0.0, 8.0, 6.5, 2.5, seed=8, amp=.10))
    reg8 = pk_region(o8, KERB)
    groundcover('B8 carpet', o8, ZS, kerb=KERB, height=.05, seed=41)
    back = reg8.intersection(_pksh.box(-20, 8.7, 20, 20))
    holes = []; sizes = ('sh16', 'sh12a', 'sh08a', 'sh12b', 'sh16', 'sh08b', 'sh12a')
    for i, (x, y) in enumerate(sorted(pk_scatter(back, 1.3, seed=9))):
        p = P[sizes[i % len(sizes)]]; s = kit.place_in(p, x, y, ZS, rnd.uniform(0, 2 * math.pi), rnd.uniform(.9, 1.08),
                                                      region=reg8, aspect=rnd.uniform(.9, 1.05), lean=(rnd.uniform(-.05, .05), 0.))
        if s:
            holes.append(_pksh.Point(x, y).buffer(p['canopy_r'] * s * .9))
    front = reg8.difference(_pksh.union_all(holes)) if holes else reg8
    perennial_drift(kit, front, ZS, [(P['cone1'], 1.6), (P['rud1'], .9), (P['salvia1'], 1), (P['salvia2'], 1),
                    (P['yarrow1'], .6), (P['yarrow2'], .5), (P['panicle1'], 1.1), (P['feather1'], .9),
                    (P['feather2'], .9), (P['fountain1'], .7)], kerb=0., spacing=.52, seed=12, drift=2.6, underlay=None)
    # B9 green-bridge strip: lavender, poppies, grasses and small shrubs held clear of a railing by the kit rule
    o9 = bed('B9 green bridge strip', pk_rounded_rect(20.0, -6.5, 3.4, .95, r=.4))
    rb = Batch(); yr = -5.43
    for i in range(6):
        x = 16.8 + i * 6.4 / 5; rb.box('rail_steel', x, yr, (ZG + 1.1) / 2, .06, .06, 1.1 - ZG)
    rb.box('rail_steel', 20.0, yr, 1.075, 6.52, .07, .05)
    rb.box('rail_steel', 20.0, yr, .55, 6.46, .03, .03)
    rb.flush('rail')
    kit.add_obstacle(_pksh.LineString([(16.75, yr), (23.25, yr)]).buffer(.04), 1.1)
    perennial_drift(kit, o9, ZS, [(P['lavender1'], 2.8), (P['poppy1'], .6), (P['fountain1'], .5),
                    (P['sh04'], .45), (P['sh08a'], .35)], kerb=KERB, spacing=.5, seed=14, drift=2.4)
    plaza(kit, P)
    kit.flush()
    bad = kit.audit(detail=True)
    if bad:
        raise RuntimeError(f'planting kit clearance rule: {len(bad)} placements cross a kerb or obstacle: {bad}')


def build():
    ground()
    planting()
    C.CONTACTS.append(dict(name='Planting kit showcase: kerbed beds and a plaza corner on a lawn at grade zero', box=[SX0, SX1, SY0, SY1]))


LIGHT_RIG = dict(key=(-18, -26, 26), fill=(22, -14, 18), rear=(-10, 26, 22), target=(0, 0, .5), gain=1.6)
