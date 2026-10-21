"""Planting kit showcase: one kerbed bed per element of the shared planting kit (plantkit.py), plus a Halifax-style
Victorian carpet bed and a Prince's-Island-style naturalistic perennial bed, on a small lawn with two gravel walks.

KIT SHOWCASE ONLY, NOT A CATALOGUE CANDIDATE. There is no locked source, no archetype or variant in any catalogue and
nothing here may be enrolled, seeded or published. The module exists so the kit can be reviewed once, at eye level,
before park families reuse it.

South row (y = -6.5), west to east: flower_head_cluster (mophead, coneflower, rudbeckia, salvia, yarrow), perennial_drift,
arching_grass (fountain, feather-reed with plumes, blue), shrub_mass. Middle row (y = +1): groundcover with floret dots,
bedding_band rings, and the leaf-shaped Halifax carpet bed (silver, begonia, purple and pink ribbons round white
hydrangeas). North (y = +8): the Prince's Island bed (drifts of coneflower, rudbeckia, salvia, yarrow and grasses over a
groundcover, with a shrub backdrop).
"""
import math
import os
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-planting-kit-showcase'
SX0, SX1, SY0, SY1 = -14.5, 14.5, -10.5, 11.5    # lawn
ZG, ZP, ZS = .04, .055, .07                      # lawn top, walk top, bed soil (mulch) top: no shared planes
KERB = .14                                       # granite bed kerb width; the kit plants inside outline minus KERB
KT, KB = .11, .02                                # kerb top and bottom
T = .3
PALETTE = dict(grass=(.33, .49, .20), gravel=(.66, .61, .53), granite=(.74, .73, .70))
INSTANCING = os.environ.get('PK_INSTANCING', '1') != '0'


def manifest(version):
    eye = 1.6
    cams = [
        dict(name='front_corner', location=(-15.5, -17.0, 9.5), target=(-1.0, -1.0, 0.2), lens=24),
        dict(name='top', location=(0.0, .5, 60.0), target=(0.0, .501, 0.0), ortho_scale=31.0),
        dict(name='eye_flower_heads', location=(-9.7, -9.9, eye), target=(-10.5, -6.6, .35), lens=30),
        dict(name='eye_perennial_drift', location=(-3.3, -9.8, eye), target=(-4.0, -6.6, .35), lens=30),
        dict(name='eye_arching_grass', location=(2.9, -9.6, eye), target=(2.2, -6.6, .35), lens=30),
        dict(name='eye_shrub_mass', location=(9.9, -10.3, eye), target=(9.0, -6.6, .5), lens=30),
        dict(name='eye_groundcover', location=(-9.9, -1.9, eye), target=(-10.5, 1.0, .08), lens=30),
        dict(name='eye_bedding_band', location=(-3.4, -1.9, eye), target=(-4.0, 1.0, .08), lens=30),
        dict(name='eye_carpet_bed', location=(.6, -1.7, eye), target=(4.8, 1.3, .15), lens=24),
        dict(name='eye_perennial_bed', location=(-2.8, 3.9, eye), target=(.5, 8.0, .4), lens=24)]
    for c in cams:
        c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='kit_showcase_not_a_catalogue_candidate', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='none: shared planting kit showcase (no catalogue archetype, no locked sources)',
        measurement_contract=dict(dimensions_m=dict(width=SX1 - SX0, depth=SY1 - SY0, height=1.4),
            observed_storeys=0, storey_programme='kit showcase: eight kerbed planting beds on a lawn',
            plan='29 x 22 m lawn, two gravel walks, eight beds with granite kerbs',
            facade='none', levels_m=[0.0, ZG, ZP, ZS, KT], inferred='every bed is a kit demonstration, not a source reading'),
        roof_contract=dict(type='none', datum_m=0.0, crowns_m=[]),
        identity_contract=dict(owner='shared planting kit showcase: flower heads, perennial drift, arching grasses, shrub masses, groundcover, bedding bands, Victorian carpet bed, naturalistic perennial bed'),
        material_contract=dict(profile='semantic clay planting palette (PK_PALETTE)', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='review of planting at eye level'),
        contact_contract=['Lawn on grade zero', 'Kerbs and mulch on the lawn', 'Every plant base sunk 2.5 cm into the mulch'],
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
import random as _pkr
import numpy as _pknp
import shapely as _pksh
from shapely.geometry import Polygon as _PkPolygon

PK_SINK = .025                                  # every plant base and carpet edge dives this far below the soil top
PK_PALETTE = dict(
    pk_leaf=(.21, .37, .14), pk_leaf2=(.31, .47, .19), pk_leaf_dark=(.13, .26, .10), pk_leaf_light=(.40, .55, .22),
    pk_leaf_silver=(.56, .61, .56), pk_leaf_red=(.38, .14, .15), pk_stem=(.25, .37, .16), pk_crown=(.11, .19, .08),
    pk_blade=(.36, .50, .21), pk_blade_blue=(.44, .55, .50), pk_straw=(.74, .64, .42), pk_plume=(.84, .74, .55),
    pk_white=(.93, .93, .89), pk_pink=(.88, .55, .66), pk_magenta=(.72, .24, .48), pk_purple=(.43, .29, .63),
    pk_lavender=(.60, .54, .80), pk_yellow=(.92, .74, .20), pk_orange=(.88, .46, .18), pk_red=(.76, .13, .14),
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
    return {r: PkGeo() for r in roles}


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


def _pk_smooth(t):
    t = min(1., max(0., t))
    return t * t * (3 - 2 * t)


def _pk_dome(g, c, r, base, seed=0, bump=0., wave=.15, lo=0., seg=18, rings=9):
    """Ellipsoid lobe (centre c, radii r) cut flat at z = base: smooth-shaded skin displaced by billowy leaf-cluster noise
    (amplitude `bump` m at `wave` m, plus a gentle `lo` m swell), fading to zero at the buried base ring; the flat cap is
    flat-shaded. Neighbouring lobes interpenetrate and never share a plane."""
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
            d = (bump * (abs(hi(*p)) - .45) + lo * low(*p)) * fade
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
    """Closed smooth ellipsoid head (florets as `bump` noise); `axis` (unit) tilts its local z."""
    cx, cy, cz = c; rx, ry, rz = r
    hi = _PkNoise(seed, 2 * math.pi / wave)
    zax = (0., 0., 1.)
    rot = None
    if axis is not None and abs(axis[2]) < .999:
        ax = _pk_norm(_pk_cross(zax, axis)); rot = (ax, math.acos(max(-1., min(1., axis[2]))))
    vs = []; fs = []
    for i in range(rings + 1):
        t = math.pi * i / rings; st, ct = math.sin(t), math.cos(t)
        for j in range(1 if i in (0, rings) else seg):
            a = 2 * math.pi * j / seg
            u = (st * math.cos(a), st * math.sin(a), ct)
            p = (rx * u[0], ry * u[1], rz * u[2])
            d = bump * (abs(hi(p[0] + cx, p[1] + cy, p[2] + cz)) - .4)
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
    rot = None
    if abs(axis[2]) < .999:
        ax = _pk_norm(_pk_cross((0., 0., 1.), axis)); rot = (ax, math.acos(max(-1., min(1., axis[2]))))
    tr = lambda p: tuple(c[k] + (_pk_rot(p, *rot) if rot else p)[k] for k in range(3))
    gp.add([tr(p) for p in vs], fs)
    hb = PkGeo(); _pk_ball(hb, (0., 0., rc * .35 * cone), (rc, rc, rc * .8 * cone), bump=rc * .25, wave=rc * .9, seg=10, rings=5)
    gb.add([tr(p) for p in hb.v], hb.f)


def _pk_spike(g, base, axis, length, r0, seed, seg=7):
    """Whorled flower spire (salvia, lavender, veronica): separated, shrinking floret beads up a slightly nodding axis,
    so it reads as whorls of florets rather than a solid capsule."""
    rnd = _pkr.Random(seed); n = max(4, int(length / (r0 * 1.55)))
    for i in range(n):
        q = i / (n - 1); rr = r0 * (1 - .55 * q)
        off = (rnd.uniform(-.25, .25) * rr, rnd.uniform(-.25, .25) * rr)
        p = (base[0] + axis[0] * length * q + off[0], base[1] + axis[1] * length * q + off[1], base[2] + axis[2] * length * q)
        _pk_ball(g, p, (rr, rr, rr * .85), seed=seed + i, bump=rr * .25, wave=rr * 1.2, seg=seg, rings=5)


class PlantKit:
    """Prototype registry and placer. proto() turns {role: PkGeo} into one shared mesh datablock per role; place() puts a
    prototype at (x, y, z) with spin and scale, as linked instances (instancing=True: glTF reuses the mesh, ~0.5 KB per
    node) or merged into per-role batches (instancing=False: every vertex is paid again). Merge anything under ~20
    triangles per role (dots, tiny florets): a node costs more than its geometry. Call flush() once after planting."""
    def __init__(self, module='planting', instancing=True):
        self.module = module; self.instancing = instancing; self.batch = {}; self.placed = 0; self.nodes = 0
        self.unique_triangles = 0; self.counts = {}

    def proto(self, name, parts):
        datas = {}
        for role, g in parts.items():
            if not g.f:
                continue
            me = C.bpy.data.meshes.new(f'PK {name} {role}')
            me.from_pydata(g.v, [], g.f); C.normalise(me)
            flat = set(g.flat)
            for p in me.polygons:
                p.use_smooth = p.index not in flat
            me.materials.append(C.MATS[role]); datas[role] = (me, g)
            self.unique_triangles += g.tris()
        return dict(name=name, parts=datas, tris=sum(g.tris() for _, g in datas.values()))

    def place(self, p, x, y, z, rot=0., s=1., sz=None, instance=None):
        inst = self.instancing if instance is None else instance
        sz = s if sz is None else sz
        self.placed += 1; self.counts[p['name']] = self.counts.get(p['name'], 0) + 1
        for role, (me, g) in p['parts'].items():
            if inst:
                o = C.bpy.data.objects.new(f"{p['name']} {role} {self.placed}", me)
                C.bpy.context.collection.objects.link(o)
                o.location = (x, y, z); o.rotation_euler = (0., 0., rot); o.scale = (s, s, sz)
                for k, v in (('rlasm_building_object', True), ('rlasm_method', C.METHOD), ('cityprompt_semantic_role', role),
                             ('cityprompt_lego_module', self.module), ('representation_kind', 'architectural_clay'),
                             ('native_geometry_only', True), ('rlasm_instance', True)):
                    o[k] = v
                self.nodes += 1
            else:
                c, sn = math.cos(rot), math.sin(rot)
                V, F, FL = self.batch.setdefault(role, ([], [], []))
                o = len(V); b = len(F)
                V.extend((x + s * (c * vx - sn * vy), y + s * (sn * vx + c * vy), z + sz * vz) for vx, vy, vz in g.v)
                F.extend(tuple(o + i for i in face) for face in g.f); FL.extend(b + i for i in g.flat)

    def flush(self):
        for role, (V, F, FL) in self.batch.items():
            if F:
                pk_mesh(f'{self.module} merged {role}', V, F, FL, role, self.module)
        self.batch = {}
        C.MODULES.setdefault(self.module, []).append(dict(planting_kit=True, instancing=self.instancing, plants=self.placed,
            instance_nodes=self.nodes, prototypes=self.counts))

    def stats(self):
        return dict(instancing=self.instancing, plants=self.placed, instance_nodes=self.nodes, prototypes=len(self.counts),
                    prototype_triangles=self.unique_triangles)


def pk_mesh(name, V, F, flat, role, module):
    """C.mesh with smooth shading on every face not listed in `flat`."""
    o = C.mesh(name, V, F, role, module)
    fl = set(flat)
    for p in o.data.polygons:
        p.use_smooth = p.index not in fl
    return o


# ---- outlines and scatter ----

def pk_ellipse(cx, cy, a, b, rot=0., n=72):
    c, s = math.cos(rot), math.sin(rot)
    return [(cx + a * math.cos(t) * c - b * math.sin(t) * s, cy + a * math.cos(t) * s + b * math.sin(t) * c)
            for t in (2 * math.pi * i / n for i in range(n))]


def pk_leaf(cx, cy, length, width, rot=0., n=96):
    """Leaf (vesica) bed outline with softly rounded tips, long axis at angle rot."""
    c, s = math.cos(rot), math.sin(rot); pts = []
    for i in range(n):
        t = 2 * math.pi * i / n; x = length / 2 * math.cos(t); y = width / 2 * math.sin(t) * abs(math.sin(t)) ** .35
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
    return pts


def pk_blob(cx, cy, a, b, seed=1, amp=.12, n=96, rot=0.):
    """Irregular naturalistic bed outline: an ellipse with low-order radial wobble (stays star-shaped)."""
    r = _pkr.Random(seed); h = [(k, r.uniform(-amp, amp) / k ** .5, r.uniform(0, 2 * math.pi)) for k in (2, 3, 4, 5)]
    c, s = math.cos(rot), math.sin(rot); pts = []
    for i in range(n):
        t = 2 * math.pi * i / n; f = 1 + sum(A_ * math.sin(k * t + ph) for k, A_, ph in h)
        x, y = a * f * math.cos(t), b * f * math.sin(t)
        pts.append((cx + x * c - y * s, cy + x * s + y * c))
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
           module='beds'):
    """Kerbed planting bed: a mitred granite kerb ring (outline = its outer edge, CCW, smooth) and a flat mulch surface at
    soil_z whose edge is buried inside the kerb. Plants then use kerb=<this kerb> to stay inside it."""
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
    return soil_obj


# ---- carpets: groundcover and bedding bands ----

def _pk_field(region, z, height, bump, wave, grid, ramp, seed):
    """Heightfield carpet over a shapely region (holes allowed): interior grid points plus the region outline resampled
    every ~grid metres, Delaunay-triangulated and clipped to the region, so the edge is a clean line with no teeth. The
    surface rises from PK_SINK below the soil at the outline to `height` plus soft-billow cushion noise within `ramp`.
    Returns (V, F, hz)."""
    x0, y0, x1, y1 = region.bounds; bnd = region.boundary
    xs = _pknp.arange(x0, x1 + grid, grid); ys = _pknp.arange(y0, y1 + grid, grid * .866)
    X, Y = _pknp.meshgrid(xs, ys); X = X + (_pknp.arange(len(ys))[:, None] % 2) * grid / 2      # triangular lattice
    X, Y = X.ravel(), Y.ravel()
    D = _pksh.distance(bnd, _pksh.points(X, Y)); ok = _pksh.contains_xy(region, X, Y) & (D > grid * .45)
    X, Y, D = X[ok], Y[ok], D[ok]
    E = _pksh.get_coordinates(_pksh.segmentize(bnd, grid * .8))
    nh = _PkNoise(seed, 2 * math.pi / wave); nl = _PkNoise(seed + 9, 2 * math.pi / (wave * 3.5))

    def top(Xa, Ya, Da):
        t = _pknp.clip(Da / ramp, 0, 1); prof = t * t * (3 - 2 * t)
        n = nh.arr(Xa, Ya)                       # soft billow: rounded plant-scale cushions, no creases or peaks
        crown = height + bump * (_pknp.sqrt(n * n + .12) - .75) * 1.6 + bump * .5 * nl.arr(Xa, Ya)
        return z - PK_SINK + (PK_SINK + crown) * prof

    keys = {}; V = []
    for x, y, h in zip(_pknp.concatenate([X, E[:, 0]]), _pknp.concatenate([Y, E[:, 1]]),
                       _pknp.concatenate([top(X, Y, D), _pknp.full(len(E), z - PK_SINK)])):
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
        d = _pksh.distance(bnd, _pksh.points(x, y))
        return float(top(_pknp.array(x), _pknp.array(y), _pknp.array(d)))
    return V, F, hz


def groundcover(name, poly, z, kerb=.15, height=.08, bump=.022, wave=.22, grid=.065, ramp=.14, role='pk_leaf2', seed=1,
                module='planting', dots=None):
    """Low continuous carpet (thyme, sedum, vinca, ajuga) over a bed outline minus the kerb: a smooth cushioned
    heightfield whose edge dives under the soil at the kerb, so it is grounded and leaves no bare fill between larger
    plants. dots=(role, per_m2, radius, seed) sprinkles merged smooth floret dots over it. Returns (object, hz)."""
    reg = pk_region(poly, kerb)
    V, F, hz = _pk_field(reg, z, height, bump, wave, grid, ramp, seed)
    o = pk_mesh(name, V, F, (), role, module)
    if dots:
        pk_dots(name + ' dots', reg, hz, *dots, module=module)
    return o, hz


def pk_dots(name, region, hz, role, per_m2, radius, seed=3, module='planting'):
    """Merged floret dots seated into a carpet surface hz (open 18-triangle smooth hemispheres, bases buried in the
    carpet); for flowering carpets such as begonias, alyssum or thyme."""
    pts = pk_scatter(region, 1 / math.sqrt(per_m2) * .85, margin=radius * 1.5, seed=seed)
    g = PkGeo(); r = _pkr.Random(seed)
    for x, y in pts:
        rr = radius * r.uniform(.75, 1.2)
        cz = hz(x, y) - rr * .25; vs = [(x, y, cz + rr * .8)]
        for i, t in ((1, .55), (2, 1.25)):
            for j in range(6):
                a = 2 * math.pi * (j + .5 * i) / 6
                vs.append((x + rr * math.sin(t) * math.cos(a), y + rr * math.sin(t) * math.sin(a), cz + rr * .8 * math.cos(t)))
        fs = [(0, 1 + j, 1 + (j + 1) % 6) for j in range(6)]
        fs += [(1 + j, 7 + j, 1 + (j + 1) % 6) for j in range(6)] + [(1 + (j + 1) % 6, 7 + j, 7 + (j + 1) % 6) for j in range(6)]
        g.add(vs, fs)
    if g.f:
        pk_mesh(name, g.v, g.f, (), role, module)
    return len(pts)


def bedding_band(name, outline, z, d_out, d_in, role, kerb=.15, height=.12, bump=.02, wave=.22, grid=.055, gap=.015,
                 seed=1, module='planting', dots=None):
    """One Victorian carpet-bedding ribbon between inward offsets d_out and d_in (m, measured from the kerb's inner edge;
    d_in=None fills the centre): a cushioned heightfield in one colour, shrunk by `gap` so neighbouring bands meet in a
    shallow soil valley, never on a shared plane. dots=(role, per_m2, radius) adds florets (begonias, alyssum) on top.
    Returns (object, region, hz)."""
    inner = pk_region(outline, kerb)
    reg = inner.buffer(-(d_out + gap), quad_segs=8)
    if d_in is not None:
        reg = reg.difference(inner.buffer(-(d_in - gap), quad_segs=8))
    if reg.is_empty:
        return None, reg, None
    V, F, hz = _pk_field(reg, z, height, bump, wave, grid, min(.12, (d_in - d_out) / 3 if d_in else .12), seed)
    o = pk_mesh(name, V, F, (), role, module)
    if dots:
        pk_dots(name + ' dots', reg, hz, dots[0], dots[1], dots[2], seed=seed + 5, module=module)
    return o, reg, hz


# ---- prototype plants ----

def _pk_foliage(g, radius, height, rnd, leaves=32, lobes=0, bump=.02, wave=.08):
    """Leafy perennial mound: a small noisy core dome clothed in broad, keeled, blunt-ovate leaves that spring from its
    surface and arch out and down (top leaves rising, side leaves drooping past the rim), so the clump reads as a mound
    of overlapping leaves, not a ball or a spiky rosette; lobes>0 adds overlapping shrubby lobes (hydrangea)."""
    core = (0., 0., height * .32); cr = (radius * .52, radius * .52, height * .62)
    _pk_dome(g, core, cr, -PK_SINK, seed=rnd.randrange(1 << 20), bump=bump, wave=wave, seg=14, rings=6)
    for k in range(lobes):
        a = rnd.uniform(0, 2 * math.pi); d = radius * rnd.uniform(.15, .4); rr = radius * rnd.uniform(.5, .65)
        hz_ = height * rnd.uniform(.85, 1.0)
        _pk_dome(g, (d * math.cos(a), d * math.sin(a), hz_ - rr * .9), (rr, rr, rr * .9), -PK_SINK, seed=rnd.randrange(1 << 20),
                 bump=bump * 1.4, wave=wave * 1.2, lo=rr * .06, seg=20, rings=9)
    top = cr[2] + core[2]
    for k in range(leaves):
        phi = k * 2.39996 + rnd.uniform(-.2, .2); q = (k + .5) / leaves          # q: 0 = crown leaves, 1 = basal skirt
        lat = math.radians(15 + 70 * q)                                          # where the leaf springs from the core
        p0 = (cr[0] * .8 * math.sin(lat) * math.cos(phi), cr[1] * .8 * math.sin(lat) * math.sin(phi),
              max(.0, core[2] + cr[2] * .8 * math.cos(lat)))
        reach = radius - math.hypot(p0[0], p0[1])
        elev = math.radians(52 - 50 * q + rnd.uniform(-8, 8)); bend = math.radians(70 + 30 * q)
        L = max(radius * .35, reach * 1.25) * rnd.uniform(.85, 1.1)
        _pk_blade(g, _pk_arc(p0, phi, elev, bend, L, 6, floor=.012), phi + rnd.uniform(-.35, .35),
                  radius * (.36 + .08 * q) * rnd.uniform(.85, 1.15), fold=.22, ovate=True)
    return top


def flower_head_cluster(kit, name, head='daisy', heads=7, height=.65, spread=.32, foliage=.26, size=1., head_role='pk_pink',
                        boss_role='pk_boss', leaf_role='pk_leaf', stem_role='pk_stem', seed=1, droop=.5):
    """One flowering perennial clump as a kit prototype: a leafy mound (overlapping smooth lobes and an arching leaf
    skirt) with `heads` stems rising to smooth heads of one kind:
      'daisy'   coneflower / rudbeckia: scalloped, drooping ray disc round a domed boss (boss_role);
      'spike'   salvia / lavender / veronica: whorls of separated floret beads up a nodding spire;
      'umbel'   yarrow / sedum: flat-topped domed floret plate;
      'mophead' hydrangea: lumpy floret balls seated in a taller shrubby mound (stems hidden).
    Heights are metres above the soil; place it with kit.place()."""
    rnd = _pkr.Random(seed)
    parts = _pk_parts(leaf_role, stem_role, head_role, *([boss_role] if head == 'daisy' else []))
    if head == 'mophead':
        _pk_foliage(parts[leaf_role], foliage, height * .82, rnd, leaves=26, lobes=4, bump=.03, wave=.09)
        for k in range(heads):
            a = rnd.uniform(0, 2 * math.pi); d = foliage * rnd.uniform(.1, .85); hr = .11 * size * rnd.uniform(.85, 1.15)
            zc = height * .82 * (1 - .5 * (d / foliage) ** 2) + hr * .2
            _pk_ball(parts[head_role], (d * math.cos(a), d * math.sin(a), zc), (hr, hr, hr * .88), seed=rnd.randrange(1 << 20),
                     bump=hr * .22, wave=hr * .55, seg=14, rings=9)
        return kit.proto(name, parts)
    _pk_foliage(parts[leaf_role], foliage, foliage * 1.15, rnd)
    for k in range(heads):
        a = rnd.uniform(0, 2 * math.pi); d = spread * rnd.uniform(.25, 1.0); hgt = height * rnd.uniform(.82, 1.08)
        top = (d * math.cos(a), d * math.sin(a), hgt)
        mid = (top[0] * .55 + rnd.uniform(-.03, .03), top[1] * .55 + rnd.uniform(-.03, .03), hgt * .55)
        base = (top[0] * .15, top[1] * .15, foliage * .45)
        _pk_tube(parts[stem_role], [base, mid, top], .007 * size, .004 * size, 5)
        lean = _pk_norm((top[0] - mid[0], top[1] - mid[1], max(.05, top[2] - mid[2]) * 2.2))
        if head == 'daisy':
            _pk_daisy(parts[head_role], parts[boss_role], top, .042 * size * rnd.uniform(.85, 1.15), 11, droop,
                      _pk_norm((lean[0] * .8, lean[1] * .8, 1.)), cone=1.6 if droop > .35 else 1.0)
        elif head == 'spike':
            _pk_spike(parts[head_role], (top[0], top[1], top[2] - .01), lean, .17 * size * rnd.uniform(.8, 1.15), .017 * size,
                      rnd.randrange(1 << 20))
        else:
            hr = .055 * size * rnd.uniform(.85, 1.15)
            _pk_ball(parts[head_role], (top[0], top[1], top[2] + hr * .2), (hr, hr, hr * .38), seed=rnd.randrange(1 << 20),
                     bump=hr * .12, wave=hr * .45, seg=12, rings=6)
    return kit.proto(name, parts)


def arching_grass(kit, name, blades=44, height=.55, width=.016, role='pk_blade', crown_role='pk_crown', plume_role=None,
                  plumes=0, plume_height=1.25, seed=1):
    """Ornamental grass tuft as a kit prototype: `blades` keeled, tapering blades rising steeply from a dark buried crown
    and arching out and over under their own weight (inner blades upright, outer ones falling past horizontal), with
    optional `plumes` upright flowering stems carrying feathery multi-lobe plumes (plume_role) at plume_height x height."""
    rnd = _pkr.Random(seed); parts = _pk_parts(role, crown_role, *([plume_role] if plume_role else []))
    _pk_dome(parts[crown_role], (0., 0., .0), (.10, .10, .07), -PK_SINK, seed=seed, bump=.01, wave=.05, seg=14, rings=5)
    for k in range(blades):
        phi = rnd.uniform(0, 2 * math.pi); rr = rnd.uniform(0, .07); q = rnd.random()
        elev = math.radians(88 - 38 * q); bend = math.radians(30 + 110 * q)
        L = height * rnd.uniform(.85, 1.25) * (1.15 - .25 * q)
        p0 = (rr * math.cos(phi), rr * math.sin(phi), -PK_SINK)
        _pk_blade(parts[role], _pk_arc(p0, phi, elev, bend, L, 8, floor=.03), phi + rnd.uniform(-.25, .25), width * rnd.uniform(.8, 1.2))
    if plume_role:
        for k in range(plumes):
            phi = rnd.uniform(0, 2 * math.pi); H = height * plume_height * rnd.uniform(.9, 1.1)
            top = (math.cos(phi) * H * .12, math.sin(phi) * H * .12, H)
            _pk_tube(parts[role], [(0., 0., -PK_SINK), (top[0] * .5, top[1] * .5, H * .55), top], .004, .003, 4)
            ax = _pk_norm((top[0], top[1], H))
            for j in range(4):
                q = j / 3; c = (top[0] - ax[0] * .16 * q + rnd.uniform(-.012, .012), top[1] - ax[1] * .16 * q + rnd.uniform(-.012, .012),
                                top[2] - ax[2] * .16 * q)
                _pk_ball(parts[plume_role], c, (.022 * (1 - .3 * q), .022 * (1 - .3 * q), .06), seed=seed + 31 * k + j,
                         bump=.008, wave=.02, seg=8, rings=6, axis=ax)
    return kit.proto(name, parts)


def shrub_mass(kit, name, radius=.8, height=1.0, lobes=9, role='pk_leaf_dark', role2='pk_leaf', seed=1, bump=.06, wave=.17):
    """Grounded multi-lobe shrub as a kit prototype: a broad buried base lobe, `lobes` overlapping noisy lobes stepping
    up to the crown (upper lobes in the lighter role2) and a few small sunlit tip lobes breaking the silhouette. The
    billowy leaf-cluster noise (`bump` m at `wave` m) and the irregular lobed outline keep it from reading as a boulder
    or a gumdrop."""
    rnd = _pkr.Random(seed); parts = _pk_parts(role, role2)
    _pk_dome(parts[role], (0., 0., height * .28), (radius * .92, radius * .86, height * .42), -PK_SINK, seed=seed, bump=bump,
             wave=wave, lo=.03, seg=30, rings=12)
    for k in range(lobes):
        a = 2 * math.pi * k / lobes + rnd.uniform(-.3, .3); up = rnd.random(); d = radius * (.62 - .45 * up) * rnd.uniform(.8, 1.1)
        rr = radius * rnd.uniform(.36, .5); cz = height * (.38 + .36 * up)
        rz = min(rr * .95, height - cz + rr * .05)
        _pk_dome(parts[role2 if up > .5 else role], (d * math.cos(a), d * math.sin(a), cz), (rr, rr * rnd.uniform(.85, 1), rz),
                 -PK_SINK, seed=rnd.randrange(1 << 20), bump=bump, wave=wave, lo=.02, seg=26, rings=11)
    for k in range(6):
        a = rnd.uniform(0, 2 * math.pi); up = rnd.uniform(.35, .9); rr = radius * rnd.uniform(.16, .24)
        d = radius * (1 - .55 * up) * .92
        _pk_ball(parts[role2], (d * math.cos(a), d * math.sin(a), height * up), (rr, rr, rr * .85), seed=rnd.randrange(1 << 20),
                 bump=bump * .7, wave=wave * .8, seg=16, rings=9)
    return kit.proto(name, parts)


def perennial_drift(kit, poly, z, mix, kerb=.15, spacing=.42, seed=1, drift=2.4, scale=(.85, 1.15)):
    """Naturalistic drift planting: Poisson-spaced positions inside the bed minus the kerb, each assigned a species from
    mix = [(proto, weight, footprint_m), ...] by low-frequency noise fields (wavelength about `drift` m), so species form
    contiguous interlocking drifts (Prince's Island, Oudolf) rather than salt-and-pepper. A plant whose footprint would
    cross the kerb falls back to the next-best species that fits, else is skipped. Returns the number placed."""
    rnd = _pkr.Random(seed); fields = [_PkNoise(seed + 17 * i, 2 * math.pi / drift) for i in range(len(mix))]
    reg = pk_region(poly, kerb); bnd = reg.boundary; n = 0
    for x, y in pk_scatter(poly, spacing, kerb=kerb, margin=min(m[2] for m in mix) * .6, seed=seed):
        order = sorted(range(len(mix)), key=lambda i: -(fields[i](x, y) + 1.4 * math.log(mix[i][1])))
        edge = bnd.distance(_pksh.points(x, y))
        for i in order:
            s = rnd.uniform(*scale)
            if mix[i][2] * s * .75 <= edge:
                kit.place(mix[i][0], x, y, z, rnd.uniform(0, 2 * math.pi), s); n += 1
                break
    return n


# ---- showcase layout ----
pk_palette(PALETTE)
KIT = None


def protos(kit):
    """The showcase prototype library (two seeds per species so repeats do not read as clones)."""
    P = {}
    for s in (1, 2):
        P[f'mophead{s}'] = flower_head_cluster(kit, f'hydrangea{s}', 'mophead', heads=11, height=.95, foliage=.48,
                                                head_role='pk_white', leaf_role='pk_leaf_dark', seed=10 + s)
        P[f'cone{s}'] = flower_head_cluster(kit, f'coneflower{s}', 'daisy', heads=9, height=.66, foliage=.3, head_role='pk_pink',
                                             droop=.35, size=1.3, seed=20 + s)
        P[f'rud{s}'] = flower_head_cluster(kit, f'rudbeckia{s}', 'daisy', heads=10, height=.55, foliage=.3, head_role='pk_yellow',
                                            droop=.15, size=1.25, seed=30 + s)
        P[f'salvia{s}'] = flower_head_cluster(kit, f'salvia{s}', 'spike', heads=11, height=.48, spread=.26, foliage=.27, head_role='pk_purple',
                                               seed=40 + s)
        P[f'yarrow{s}'] = flower_head_cluster(kit, f'yarrow{s}', 'umbel', heads=7, height=.6, foliage=.3, head_role='pk_yellow', seed=50 + s)
        P[f'fountain{s}'] = arching_grass(kit, f'fountain_grass{s}', blades=70, height=.55, width=.019, seed=60 + s)
        P[f'feather{s}'] = arching_grass(kit, f'feather_reed{s}', blades=60, height=.5, width=.018, role='pk_straw', plume_role='pk_plume',
                                         plumes=9, plume_height=2.4, seed=70 + s)
        P[f'blue{s}'] = arching_grass(kit, f'blue_grass{s}', blades=56, height=.32, width=.013, role='pk_blade_blue', seed=80 + s)
        P[f'shrub{s}'] = shrub_mass(kit, f'shrub{s}', radius=.85 if s == 1 else .7, height=1.15 if s == 1 else .9, seed=90 + s)
    return P


def ground():
    b = Batch()
    b.box('grass', (SX0 + SX1) / 2, (SY0 + SY1) / 2, ZG / 2, SX1 - SX0, SY1 - SY0, ZG)
    for y0, y1 in ((-3.3, -1.7), (4.2, 5.4)):
        b.box('gravel', 0., (y0 + y1) / 2, (ZP + .01) / 2, 27.0, y1 - y0, ZP - .01)
    b.flush('ground')


def bed(name, outline):
    pk_bed(name, outline, ZS, kerb=KERB, kerb_top=KT, kerb_bottom=KB)
    return outline


def place_ring(kit, p, cx, cy, items, rnd):
    for (dx, dy, key) in items:
        kit.place(p[key], cx + dx, cy + dy, ZS, rnd.uniform(0, 2 * math.pi), rnd.uniform(.92, 1.08))


def planting():
    global KIT
    kit = KIT = PlantKit('planting', instancing=INSTANCING); P = protos(kit); rnd = _pkr.Random(7)
    # B1 flower_head_cluster: one clump of each head type round a hydrangea
    bed('B1 flower heads', pk_ellipse(-10.5, -6.5, 2.4, 1.6))
    place_ring(kit, P, -10.5, -6.5, [(0, .05, 'mophead1'), (-1.35, .55, 'cone1'), (-1.45, -.45, 'cone2'), (1.35, .55, 'rud1'),
               (1.45, -.45, 'rud2'), (-.55, -.95, 'salvia1'), (.6, -.95, 'yarrow1'), (-.45, 1.0, 'salvia2'), (.55, 1.0, 'yarrow2')], rnd)
    # B2 perennial_drift
    o2 = bed('B2 perennial drift', pk_blob(-4.0, -6.5, 2.3, 1.6, seed=3))
    perennial_drift(kit, o2, ZS, [(P['cone1'], 1, .3), (P['cone2'], 1, .3), (P['salvia1'], 1, .28), (P['salvia2'], 1, .28),
                    (P['yarrow1'], .8, .3), (P['rud1'], .8, .3)], kerb=KERB, spacing=.5, seed=5, drift=2.0)
    # B3 arching_grass
    o3 = bed('B3 arching grass', pk_ellipse(2.2, -6.5, 2.2, 1.5))
    perennial_drift(kit, o3, ZS, [(P['fountain1'], 1, .45), (P['fountain2'], 1, .45), (P['feather1'], 1, .35),
                    (P['feather2'], 1, .35), (P['blue1'], .7, .28), (P['blue2'], .7, .28)], kerb=KERB, spacing=.62, seed=8, drift=2.2)
    # B4 shrub_mass
    bed('B4 shrub mass', pk_blob(9.0, -6.5, 2.6, 1.7, seed=4))
    place_ring(kit, P, 9.0, -6.5, [(-1.25, .35, 'shrub1'), (.2, .5, 'shrub2'), (1.35, .25, 'shrub1'), (-.4, -.65, 'shrub2'),
               (1.0, -.75, 'blue1')], rnd)
    # B5 groundcover with floret dots
    o5 = bed('B5 groundcover', pk_ellipse(-10.5, 1.0, 2.2, 1.4))
    groundcover('B5 carpet', o5, ZS, kerb=KERB, role='pk_leaf2', seed=11, dots=('pk_pink', 26, .02, 4))
    # B6 bedding_band rings
    o6 = bed('B6 bedding bands', pk_ellipse(-4.0, 1.0, 1.9, 1.9))
    bedding_band('B6 silver', o6, ZS, 0., .32, 'pk_leaf_silver', kerb=KERB, height=.10, seed=21)
    bedding_band('B6 begonia', o6, ZS, .32, .66, 'pk_leaf_red', kerb=KERB, height=.13, seed=22, dots=('pk_red', 30, .022))
    bedding_band('B6 purple', o6, ZS, .66, 1.0, 'pk_leaf_dark', kerb=KERB, height=.15, seed=23, dots=('pk_purple', 34, .02))
    bedding_band('B6 centre', o6, ZS, 1.0, None, 'pk_leaf', kerb=KERB, height=.10, seed=24, dots=('pk_pink', 26, .022))
    kit.place(P['salvia1'], -4.0, 1.0, ZS + .06, 0., 1.1)
    # B7 Halifax-style Victorian carpet bed: ribbons following the leaf outline round white hydrangeas
    o7 = bed('B7 Halifax carpet bed', pk_leaf(5.3, 1.2, 10.0, 3.4))
    bedding_band('B7 silver', o7, ZS, 0., .30, 'pk_leaf_silver', kerb=KERB, height=.10, seed=31)
    bedding_band('B7 begonia', o7, ZS, .30, .62, 'pk_leaf_red', kerb=KERB, height=.13, seed=32, dots=('pk_red', 28, .022))
    bedding_band('B7 purple', o7, ZS, .62, .94, 'pk_leaf_dark', kerb=KERB, height=.15, seed=33, dots=('pk_purple', 32, .02))
    _, centre, hz = bedding_band('B7 pink', o7, ZS, .94, None, 'pk_leaf', kerb=KERB, height=.12, seed=34, dots=('pk_pink', 24, .022))
    for i, (x, y) in enumerate(pk_scatter(centre, 1.25, margin=.38, seed=6)):
        kit.place(P['mophead%d' % (1 + i % 2)], x, y, ZS + .05, rnd.uniform(0, 2 * math.pi), .8)
    # B8 Prince's-Island-style perennial bed: shrub backdrop, drifts of perennials and grasses over a groundcover
    o8 = bed('B8 perennial bed', pk_blob(0.0, 8.0, 6.5, 2.5, seed=8, amp=.10))
    reg8 = pk_region(o8, KERB)
    groundcover('B8 carpet', reg8, ZS, kerb=0., height=.06, role='pk_leaf2', seed=41)
    back = reg8.intersection(_pksh.box(-20, 9.0, 20, 20)).buffer(-.6)
    holes = []
    for i, (x, y) in enumerate(pk_scatter(back, 2.0, seed=9)):
        kit.place(P['shrub%d' % (1 + i % 2)], x, y, ZS, rnd.uniform(0, 2 * math.pi), rnd.uniform(.9, 1.1))
        holes.append(_pksh.Point(x, y).buffer(.95))
    front = reg8.difference(_pksh.union_all(holes)) if holes else reg8
    perennial_drift(kit, front, ZS, [(P['cone1'], 1, .3), (P['cone2'], 1, .3), (P['rud1'], .9, .3), (P['rud2'], .9, .3),
                    (P['salvia1'], 1, .28), (P['salvia2'], 1, .28), (P['yarrow1'], .6, .3), (P['yarrow2'], .6, .3),
                    (P['feather1'], .9, .35), (P['feather2'], .9, .35), (P['fountain1'], .7, .45)],
                    kerb=0., spacing=.52, seed=12, drift=2.6)
    kit.flush()


def build():
    ground()
    planting()
    C.CONTACTS.append(dict(name='Planting kit showcase: kerbed beds on a lawn at grade zero', box=[SX0, SX1, SY0, SY1]))


LIGHT_RIG = dict(key=(-18, -26, 26), fill=(22, -14, 18), rear=(-10, 26, 22), target=(0, 0, .5), gain=1.6)
