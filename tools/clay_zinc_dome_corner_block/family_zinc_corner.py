"""Haussmann corner block with a zinc dome, authored from the locked catalogue views of
parisian_corner_with_dome / variant_0 (parisian-corner-with-dome-zinc-mansard).

Read from the pixels: a corner block with streets south and west around an inner court. A stone ground
floor with a cafe whose red awning wraps the chamfered corner; a stone first storey; three storeys of red
brick with stone string courses, quoins and window surrounds; tall French windows with individual iron
balconies on the first and third storeys and continuous iron balconies on the second and fourth; a
bracketed cornice; a zinc mansard with arched dormers; on the chamfer a stone drum with oeil-de-boeuf
windows carrying a ribbed zinc dome, an oculus dormer, an open lantern and a gilded finial.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G
from contract import subtract_openings

SLUG = 'clay-zinc-dome-corner-block'
W, D = 34.0, 30.0
CH = 6.5                          # chamfer length along the 45-degree face
COURT = (3.0, 6.0, 2.0, 5.0)      # inner court: cx, half width, cy, half depth
T = .34
G0 = .15
LEVELS = [4.6, 8.0, 11.3, 14.6]   # upper floor levels: ground plus four storeys (locked front)
CORNICE = 18.0
MANS_H, MANS_IN = 3.6, 1.5
DRUM_R, DRUM_H = 3.7, 3.0
DOME_R, DOME_H = 4.1, 5.0
BAY = 3.3
EPS = .002
AWN_Z = 3.45                      # awning bar height
PALETTE = dict(wall=(.58, .30, .22), joint=(.42, .22, .16), trim=(.26, .20, .14),
    pale=(.78, .74, .66), stone=(.74, .70, .60), roof=(.44, .48, .52), sand=(.70, .64, .52),
    foundation=(.46, .46, .45), glass=(.44, .50, .52), hardware=(.12, .12, .12),
    interior=(.80, .76, .68), floor=(.46, .44, .42), timber=(.34, .22, .14), blue=(.14, .22, .28),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.64, .62, .58), zinc=(.44, .48, .52),
    awning=(.62, .10, .08), gilt=(.80, .64, .26), rustic=(.70, .66, .56))

CX0, CY0 = -W / 2 + CH / math.sqrt(2), -D / 2
CX1, CY1 = -W / 2, -D / 2 + CH / math.sqrt(2)
CMX, CMY = (CX0 + CX1) / 2, (CY0 + CY1) / 2
CN = (-1 / math.sqrt(2), -1 / math.sqrt(2))
DX, DY = CMX - CN[0] * 2.3, CMY - CN[1] * 2.3     # drum centre 2.3 m behind the chamfer plane: the drum front projects 1.4 m over the chamfer cornice on a corbel ring (locked top and front, v001 P1 3)


def manifest(version):
    h = CORNICE + DRUM_H + DOME_H + 4.2
    cams = G.camera_roster(W + 8.0, D + 8.0, h, [
        ('facade_close', (-4.0, -32.0, 6.5), (0.0, -D / 2, 9.0), 45),
        ('architecture_close', (-36.0, -34.0, 15.0), (CMX, CMY, 14.0), 50),
        ('glass_close', (-6.0, -24.0, 2.0), (-2.0, -D / 2, 2.6), 50),
        ('corner_dome', (-36.0, -36.0, 26.0), (DX, DY, 23.5), 45),
        ('cafe_awning', (-26.0, -26.0, 2.2), (CMX, CMY, 3.0), 40),
        ('balcony_ironwork', (-9.0, -25.0, 9.5), (-5.0, -D / 2, 10.5), 45),
        ('mansard_dormers', (6.0, -30.0, 19.0), (8.0, -D / 2, 20.0), 45),
        ('roof_court', (-42.0, -46.0, 42.0), (2.0, 2.0, 18.0), 45),
        ('interior', (-4.0, -D / 2 + 1.2, LEVELS[0] + 1.6), (-4.0, -D / 2 + 7.0, LEVELS[0] + 1.3), 50),
        ('rear_court', (COURT[0] + 4.5, COURT[2] + 3.5, 19.0), (COURT[0] - 4.5, COURT[2] - 3.5, 3.0), 35)])
    for c in cams:
        if c['name'] == 'front':          # eye level on the chamfer axis (locked front)
            c['location'] = (CMX + CN[0] * 60.0, CMY + CN[1] * 60.0, 1.7); c['target'] = (CMX, CMY, 13.5); c['lens'] = 30; c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='parisian_corner_with_dome/variant_0 (parisian-corner-with-dome-zinc-mansard)',
        measurement_contract=dict(dimensions_m=dict(width=W + 8.0, depth=D + 8.0, height=h),
            observed_storeys=5, storey_programme='stone cafe ground floor, stone first storey, three brick storeys, zinc mansard attic',
            plan='34 x 30 m corner block (top view) with a 12 x 10 m inner court, streets south and west, a 6.5 m chamfer at the south-west corner under the dome',
            facade='bays at 3.3 m of French windows 1.3 x 2.6 m with stone surrounds; individual iron balconies on the first and third storeys, continuous iron balconies on the second and fourth; stone string courses in the brick; quoins at the corners and the chamfer; bracketed cornice at 18.0 m',
            levels_m=[G0] + LEVELS, cornice_m=CORNICE, mansard='3.6 m zinc mansard set in 1.5 m with arched dormers at every bay; flat zinc top',
            dome='stone drum 7.4 m across and 3.0 m high centred 2.3 m behind the chamfer plane on a corbel ring over the chamfer cornice, with three oeil-de-boeuf windows and a cornice; ribbed zinc dome 8.2 m across and 5.0 m high with a projecting framed oculus dormer at its base on the chamfer axis; open lantern and gilded finial to 30 m',
            ground='stone ground floor with timber shopfronts; the cafe occupies the chamfer and two bays each side under one continuous red awning projecting 2.6 m, mitred around both chamfer arrises',
            inferred='north and east faces repeat the grammar without balconies; court faces plain; interiors are teaching assumptions'),
        roof_contract=dict(type='zinc mansard with dormers and a flat top; zinc dome on the chamfer drum', datum_m=CORNICE, crowns_m=[CORNICE + MANS_H, CORNICE + DRUM_H + DOME_H, h]),
        identity_contract=dict(owner='zinc dome on the chamfer with oculus and lantern, brick-and-stone Haussmann facades with iron balconies, zinc mansard with dormers, red cafe awning wrapping the corner'),
        material_contract=dict(profile='source-palette clay: red brick with recessed joints and stone bands, pale stone base, surrounds and cornice, zinc roofs and dome, black iron, red canvas awning, gilt finial', textured_keeper=False),
        programme_contract=dict(storeys=6, ground='cafe on the corner, shops', upper='two apartments per floor', roof='attic rooms in the mansard'),
        contact_contract=['Grade-zero slab and sidewalks', 'Balconies cantilevered from the carriers', 'Awning on arms from the ground-floor carrier', 'Mansards seated on the cornice', 'Drum on the chamfer walls through the mansard; dome on the drum cornice; lantern on a solid neck', 'Dormers seated on the slope'],
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


# ---- building ----

def arch_fill(f, u, z_top, w, rise, role='stone', d0=-.03, d1=None):
    d1 = T + .02 if d1 is None else d1
    pts = [(-w / 2, z_top), (w / 2, z_top), (w / 2, z_top - rise)]
    for k in range(1, 8):
        x = w / 2 - w * k / 8
        pts.append((x, z_top - rise + rise * (1 - (2 * x / w) ** 2) ** .5))
    pts.append((-w / 2, z_top - rise))
    f.panel('Arch spandrel', [(u + a, b) for a, b in pts], d0, d1, role, 'arches')


def bands(f, lo, hi, zs, holes, h=.12, d=-.025, role='stone'):
    """Stone string courses proud of the brick, subtracted around every opening, batched in one mesh."""
    vs, fs = [], []
    for z in zs:
        for a, b in subtract_openings(lo, hi, z, z + h, holes):
            o = len(vs)
            vs.extend([f.p(a, d, z), f.p(b, d, z), f.p(b, d, z + h), f.p(a, d, z + h), f.p(a, T / 2, z), f.p(b, T / 2, z), f.p(b, T / 2, z + h), f.p(a, T / 2, z + h)])
            fs.extend([(o, o + 1, o + 2, o + 3), (o + 7, o + 6, o + 5, o + 4), (o, o + 4, o + 5, o + 1), (o + 1, o + 5, o + 6, o + 2), (o + 2, o + 6, o + 7, o + 3), (o + 3, o + 7, o + 4, o)])
    if fs:
        C.mesh(f.label + ' string courses', vs, fs, role, 'string courses')


def mansard_dormer(f, u, z_e, rise, setin, w=1.5, role='zinc'):
    """Arched zinc dormer standing on the mansard slope: front proud of the slope, cheeks back to the slope, small roof."""
    k = setin / rise
    d0 = .30
    z_em = z_e + d0 / k
    z_top = z_e + 2.95
    zw, hw, ww = z_e + .95, 1.6, .95
    front = f.panel(f'{f.label} dormer front', [(u - w / 2, z_em - .6), (u + w / 2, z_em - .6), (u + w / 2, z_top), (u - w / 2, z_top)], d0 - .16, d0 + .10, role, 'dormers')
    f.cut(front, f'{f.label} dormer window cut', u, zw, ww, hw, depth=.30)
    g = C.Face(f.p(0, d0 - .16, 0), f.t, f.n, f.label + ' dormer')
    mg = Merge(g)
    h = hole(f'{f.label} dormer window {u:.1f}', u, zw, ww, hw)
    framed(mg, g, h, cols=1, rows=2, inset=.10, occupied='attic room', kind='dormer window')
    mg.flush('dormers')
    arch_fill(g, u, zw + hw, ww, ww / 2, role, -.03, .28)
    for i in range(6):
        a0, a1 = math.pi * i / 6, math.pi * (i + 1) / 6
        pa = g.p(u + math.cos(a0) * (ww / 2 + .09), -.05, zw + hw - ww / 2 + math.sin(a0) * (ww / 2 + .09))
        pb = g.p(u + math.cos(a1) * (ww / 2 + .09), -.05, zw + hw - ww / 2 + math.sin(a1) * (ww / 2 + .09))
        C.beam('Dormer hood', pa, pb, .10, .09, role, 'dormers')
    g.part('Dormer pediment', u, -.08, z_top - .10, w + .16, .18, .20, role, 'dormers', 0)
    d_meet = (z_top - .02 - z_e - .14 * (d0 - .30) / 1.3) / (1 / k - .14 / 1.3)
    z_meet = z_e + d_meet / k
    for sgn in (-1, 1):
        uu = u + sgn * (w / 2 - .14)
        pts = [(d0 - .12, z_em - .6), (d0 - .12, z_top - .03), (d_meet, z_meet), (d_meet, z_meet - .7)]
        vs = [f.p(uu - .06, d, z) for d, z in pts] + [f.p(uu + .06, d, z) for d, z in pts]
        fs = [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        C.mesh('Dormer cheek', vs, fs, role, 'dormers')
    vs = [f.p(u - w / 2 - .12, d0 - .30, z_top - .02), f.p(u + w / 2 + .12, d0 - .30, z_top - .02), f.p(u + w / 2 + .12, d0 + 1.0, z_top + .12), f.p(u - w / 2 - .12, d0 + 1.0, z_top + .12)]
    vs += [f.p(u - w / 2 - .12, d0 - .30, z_top - .16), f.p(u + w / 2 + .12, d0 - .30, z_top - .16), f.p(u + w / 2 + .12, d0 + 1.0, z_top - .02), f.p(u - w / 2 - .12, d0 + 1.0, z_top - .02)]
    C.mesh('Dormer roof', vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], role, 'dormers')


def offset_polygon(pts, dist):
    """Inward offset of a convex counter-clockwise polygon by dist (edge-line intersections)."""
    n = len(pts)
    lines = []
    for i in range(n):
        (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
        nx, ny = -uy, ux                 # left normal = inward for CCW
        lines.append((ax + nx * dist, ay + ny * dist, ux, uy))
    out = []
    for i in range(n):
        px, py, ux, uy = lines[i - 1]; qx, qy, vx, vy = lines[i]
        den = ux * vy - uy * vx
        t = ((qx - px) * vy - (qy - py) * vx) / den
        out.append((px + ux * t, py + uy * t))
    return out


def elevation(f, lo, hi, street=True, cafe_bays=(), label=None):
    """One face: stone ground and first storey, brick storeys with stone courses, balconies, cornice."""
    span = hi - lo
    nb = max(1, round(span / BAY))
    pitch = span / nb
    g, up = [], []
    for i in range(nb):
        c = lo + pitch * (i + .5)
        if street:
            g.append(hole(f'{f.label} shop opening {i}', c, G0, 2.3, 3.5, kind='storefront', cafe=i in cafe_bays))
        elif i % 2 == 0:
            g.append(hole(f'{f.label} ground window {i}', c, 1.1, 1.3, 2.3))
        for k, zl in enumerate(LEVELS):
            up.append(hole(f'{f.label} window {i}-{k}', c, zl + .12, 1.3, 2.6, kind='french window', level=k))
    holes = g + up
    f.wall(f'{f.label} ground carrier', lo, hi - EPS, G0, LEVELS[1] - .30, depth=T, role='stone', holes=holes)
    f.wall(f'{f.label} brick carrier', lo, hi - EPS, LEVELS[1] - .30, CORNICE + .40, depth=T, role='wall', holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, LEVELS[1] + .10, CORNICE - .90, up, spacing=.42)
    G.brick_courses(f, lo + .02, hi - .02, G0 + .30, LEVELS[0] - .40, g, spacing=.62)       # rusticated ground floor
    zs = []
    for zl in LEVELS[1:]:
        zs += [zl + 1.00, zl + 1.70]      # brick-and-stone polychrome courses between the windows' head and sill zones
    bands(f, lo + .02, hi - .02, zs, up)
    m = Merge(f)
    for h in g:
        if h.get('kind') == 'storefront':
            reveal(m, f, h, .18, 'stone')
            framed(m, f, h, cols=2 if h.get('cafe') else 1, rows=2, inset=.18, occupied='cafe' if h.get('cafe') else 'shop', kind='storefront', frame='timber')
            m.box('timber', h['u'], .10, h['z'] + h['h'] - .55, h['w'] - .14, .06, .30)        # fascia board
            m.box('stone', h['u'], -.05, h['z'] + h['h'] + .18, h['w'] + .60, T + .16, .30)   # lintel
        else:
            framed(m, f, h, cols=1, rows=1, occupied='service')
    for h in up:
        if street:
            reveal(m, f, h, .16, 'stone')
        framed(m, f, h, cols=2 if street else 1, rows=1, occupied='apartment', kind='french window')
        for sgn in (-1, 1):
            m.box('stone', h['u'] + sgn * (h['w'] / 2 + .11), -.03, h['z'] + h['h'] / 2, .22, T + .12, h['h'] + .22)
        m.box('stone', h['u'], -.05, h['z'] + h['h'] + .17, h['w'] + .56, T + .16, .24)
        k = h['level']
        if street and k in (0, 2):
            iron_balcony(m, f, h['u'], h['z'], h['w'] + .8, depth=.70)
        elif not (street and k in (1, 3)):
            m.box('stone', h['u'], -.09, h['z'] - .09, h['w'] + .46, T + .24, .12)
    if street:
        for k in (1, 3):
            iron_balcony(m, f, (lo + hi) / 2, LEVELS[k], span - .30, depth=.85)
    m.box('stone', (lo + hi) / 2, -.07, LEVELS[0] - .20, span - 2 * EPS, T + .22, .30)      # ground-floor entablature band
    m.box('stone', (lo + hi) / 2, -.05, LEVELS[1] - .18, span - 2 * EPS, T + .16, .22)
    eave_cornice(m, lo, hi, CORNICE, T, .62)
    m.flush('facade')
    return pitch, g


def awning_path(path, out=2.6):
    """One continuous red awning along an open wall polyline (world xy points, building on the left): sloped canvas strip
    between the wall line and its mitred outward offset, hanging valance with scallops, iron arms every 2.2 m."""
    n = len(path)
    # outward offset of the open polyline (right-hand side of the direction of travel is outward)
    segs = []
    for (ax, ay), (bx, by) in zip(path, path[1:]):
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
        segs.append((ax + uy * out, ay - ux * out, ux, uy))
    outer = [(segs[0][0], segs[0][1])]
    for (px, py, ux, uy), (qx, qy, vx, vy) in zip(segs, segs[1:]):
        den = ux * vy - uy * vx
        t = ((qx - px) * vy - (qy - py) * vx) / den
        outer.append((px + ux * t, py + uy * t))
    lx, ly, lux, luy = segs[-1]
    L = math.hypot(path[-1][0] - path[-2][0], path[-1][1] - path[-2][1])
    outer.append((lx + lux * L, ly + luy * L))
    inner = [(x - 0.0, y - 0.0) for x, y in path]
    strip('Cafe awning canvas', outer, inner, AWN_Z - .45, AWN_Z + .25, 'awning', 'awning', closed=False)
    for (ax, ay), (bx, by) in zip(outer, outer[1:]):
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
        ix, iy = -uy, ux          # inward
        C.beam('Awning valance', (ax + ix * .06, ay + iy * .06, AWN_Z - .82), (bx + ix * .06, by + iy * .06, AWN_Z - .82), .04, .36, 'awning', 'awning')
        C.beam('Awning front bar', (ax + ix * .09, ay + iy * .09, AWN_Z - .48), (bx + ix * .09, by + iy * .09, AWN_Z - .48), .05, .05, 'hardware', 'awning')
        k = max(2, int(L / .55))
        for i in range(k + 1):
            px, py = ax + ux * L * i / k, ay + uy * L * i / k
            C.box('Awning scallop', (px + ix * .06, py + iy * .06, AWN_Z - 1.06), (.26, .26, .12), 'awning', 'awning', 0)
    for (ax, ay), (bx, by) in zip(path, path[1:]):
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
        ox, oy = uy, -ux          # outward
        C.beam('Awning wall rail', (ax + ox * .02, ay + oy * .02, AWN_Z + .30), (bx + ox * .02, by + oy * .02, AWN_Z + .30), .06, .10, 'hardware', 'awning')
        k = max(1, int(L / 2.2))
        for i in range(k + 1):
            t = (.35 + (L - .7) * i / k) if k else L / 2
            px, py = ax + ux * t, ay + uy * t
            a = (px, py, AWN_Z + .25); bq = (px + ox * (out - .10), py + oy * (out - .10), AWN_Z - .40)
            C.beam('Awning arm', a, bq, .05, .05, 'hardware', 'awning')
            C.beam('Awning brace', (px, py, AWN_Z - 1.2), (bq[0] + (a[0] - bq[0]) * .35, bq[1] + (a[1] - bq[1]) * .35, bq[2] + (a[2] - bq[2]) * .35), .035, .035, 'hardware', 'awning')


def chamfer_bay():
    nx, ny = CN
    tx, ty = -ny, nx
    half = CH / 2
    f = C.Face((CMX, CMY, 0), (tx, ty, 0), (-nx, -ny, 0), 'chamfer')
    g = [hole('Cafe door', 0.0, G0, 2.6, 3.5, kind='glazed door', cafe=True)]
    up = [hole(f'chamfer window {k}', 0.0, zl + .12, 1.9, 2.6, kind='french window', level=k) for k, zl in enumerate(LEVELS)]
    holes = g + up
    f.wall('chamfer ground carrier', -half, half, G0, LEVELS[1] - .30, depth=T, role='stone', holes=holes)
    f.wall('chamfer upper carrier', -half, half, LEVELS[1] - .30, CORNICE + .40, depth=T, role='stone', holes=holes)
    G.brick_courses(f, -half + .02, half - .02, G0 + .30, LEVELS[0] - .40, g, spacing=.62)
    m = Merge(f)
    reveal(m, f, g[0], .18, 'stone'); framed(m, f, g[0], cols=2, rows=2, inset=.18, occupied='cafe', kind='glazed door', frame='timber')
    m.box('timber', 0.0, .10, g[0]['z'] + g[0]['h'] - .55, g[0]['w'] - .14, .06, .30)
    m.box('stone', 0.0, -.05, g[0]['z'] + g[0]['h'] + .18, g[0]['w'] + .60, T + .16, .30)
    for h in up:
        reveal(m, f, h, .16, 'stone'); framed(m, f, h, cols=2, rows=1, occupied='salon', kind='french window')
        for sgn in (-1, 1):
            m.box('stone', h['u'] + sgn * (h['w'] / 2 + .14), -.04, h['z'] + h['h'] / 2, .28, T + .14, h['h'] + .28)
        m.box('stone', h['u'], -.06, h['z'] + h['h'] + .18, h['w'] + .70, T + .18, .26)
        k = h['level']
        if k == 0:        # projecting stone balcony on consoles (locked front)
            m.box('stone', 0.0, -.45, h['z'] - .12, CH - .8, 1.24, .22)
            for sgn in (-1, 1):
                m.box('stone', sgn * 1.6, -.40, h['z'] - .58, .36, .80, .70)
            balustrade_iron(m, f, -(CH - .8) / 2 + .05, (CH - .8) / 2 - .05, -1.02, h['z'])
        elif k in (1, 3):
            iron_balcony(m, f, 0.0, LEVELS[k], CH - .30, depth=.85)
        else:
            iron_balcony(m, f, h['u'], h['z'], h['w'] + .8, depth=.70)
    m.box('stone', 0.0, -.07, LEVELS[0] - .20, CH - 2 * EPS, T + .22, .30)
    m.box('stone', 0.0, -.05, LEVELS[1] - .18, CH - 2 * EPS, T + .16, .22)
    eave_cornice(m, -half, half, CORNICE, T, .62)
    m.flush('chamfer')
    # Quoin strips at the chamfer edges and the right-angle corners.
    for (qx, qy), (ox_, oy_) in (((CX0, CY0), (0, -1)), ((CX1, CY1), (-1, 0))):
        bxv, byv = ox_ + nx, oy_ + ny
        bl = (bxv ** 2 + byv ** 2) ** .5; bxv, byv = bxv / bl, byv / bl
        pf = C.Face((qx, qy, 0), (-byv, bxv, 0), (-bxv, -byv, 0), 'corner quoin')
        pf.part('Chamfer quoin', 0.0, 0.0, (CORNICE + .40) / 2, .80, .80, CORNICE + .40, 'stone', 'corner posts', 0)
        pf.part('Chamfer quoin cornice block', 0.0, 0.0, CORNICE - .36, 1.70, 1.70, .72, 'stone', 'corner posts', 0)
    for (qx, qy) in ((-W / 2 - .08, D / 2 + .08), (W / 2 + .08, D / 2 + .08), (W / 2 + .08, -D / 2 - .08)):
        C.box('Corner quoin', (qx, qy, (CORNICE + .40) / 2), (1.0, 1.0, CORNICE + .40), 'stone', 'corner posts', 0)
        C.box('Corner cornice block', (qx + (.12 if qx > 0 else -.12), qy + (.12 if qy > 0 else -.12), CORNICE - .36), (1.56, 1.56, .72), 'stone', 'corner posts', 0)


def balustrade_iron(m, f, lo, hi, d, z, height=1.0):
    m.box('hardware', (lo + hi) / 2, d, z + height, hi - lo, .05, .05)
    m.box('hardware', (lo + hi) / 2, d, z + .45, hi - lo, .03, .03)
    n = max(4, int((hi - lo) / .20))
    for i in range(n + 1):
        m.box('hardware', lo + (hi - lo) * i / n, d, z + height / 2 + .02, .028, .028, height - .04)
    for e in (lo, hi):
        for i in range(1, 5):
            m.box('hardware', e, d + .22 * i, z + height / 2 + .02, .028, .028, height - .04)
    m.box('hardware', lo, d + .5, z + height, .05, 1.0, .05); m.box('hardware', hi, d + .5, z + height, .05, 1.0, .05)


def drum_and_dome():
    cx, cy = DX, DY
    z0 = CORNICE - 1.0
    z1 = CORNICE + DRUM_H
    # Corbel ring carrying the drum front over the chamfer cornice, then the stone drum with a moulded cornice.
    cone('Drum corbel', cx, cy, z0, DRUM_R - 1.1, CORNICE + .30, DRUM_R, 'stone', 'dome', 48)
    C.rod('Dome drum', (cx, cy, CORNICE + .30), (cx, cy, z1 - .40), DRUM_R, 'stone', 'dome', 48)
    C.rod('Drum cornice bed', (cx, cy, z1 - .40), (cx, cy, z1 - .18), DRUM_R + .22, 'stone', 'dome', 48)
    C.rod('Drum cornice', (cx, cy, z1 - .18), (cx, cy, z1), DRUM_R + .42, 'stone', 'dome', 48)
    C.rod('Dome eave', (cx, cy, z1), (cx, cy, z1 + .20), DOME_R + .10, 'zinc', 'dome', 48)
    base = math.atan2(CN[1], CN[0])
    zc = CORNICE + 1.75
    drum = C.bpy.data.objects['Dome drum']
    for da in (-48.0, 0.0, 48.0):
        # Oeil-de-boeuf as a real opening (v002 P1 1): a pocket cut into the drum, a dark liner, recessed glass with a
        # cross bar, a moulded stone annulus frame proud of the drum and four keystones.
        a = base + math.radians(da)
        ux, uy = math.cos(a), math.sin(a); tx, ty = -uy, ux
        g = C.Face((cx + ux * (DRUM_R - .02), cy + uy * (DRUM_R - .02), 0), (tx, ty, 0), (-ux, -uy, 0), f'roundel {da:+.0f}')
        g.cut(drum, f'roundel cut {da:+.0f}', 0.0, zc - .55, 1.1, 1.1, depth=.55)
        mg = Merge(g)
        mg.box('hardware', 0.0, .30, zc, 1.06, .50, 1.06)                      # dark liner filling the pocket
        mg.flush('dome')
        C.rod('Oeil-de-boeuf glass', (cx + ux * (DRUM_R - .30), cy + uy * (DRUM_R - .30), zc), (cx + ux * (DRUM_R - .27), cy + uy * (DRUM_R - .27), zc), .50, 'glass', 'dome', 24)
        C.beam('Oeil-de-boeuf bar', (cx + ux * (DRUM_R - .26) + tx * .50, cy + uy * (DRUM_R - .26) + ty * .50, zc), (cx + ux * (DRUM_R - .26) - tx * .50, cy + uy * (DRUM_R - .26) - ty * .50, zc), .04, .04, 'hardware', 'dome')
        C.beam('Oeil-de-boeuf bar', (cx + ux * (DRUM_R - .26), cy + uy * (DRUM_R - .26), zc - .50), (cx + ux * (DRUM_R - .26), cy + uy * (DRUM_R - .26), zc + .50), .04, .04, 'hardware', 'dome')
        annulus('Oeil-de-boeuf reveal', (cx + ux * DRUM_R, cy + uy * DRUM_R, zc), (ux, uy, 0), .50, .58, -.28, .02, 'hardware', 'dome', 24)
        annulus('Oeil-de-boeuf frame', (cx + ux * DRUM_R, cy + uy * DRUM_R, zc), (ux, uy, 0), .52, .82, -.02, .20, 'stone', 'dome', 24)
        annulus('Oeil-de-boeuf frame bead', (cx + ux * DRUM_R, cy + uy * DRUM_R, zc), (ux, uy, 0), .66, .76, .20, .26, 'stone', 'dome', 24)
        for ak in (0.0, math.pi / 2, math.pi, 3 * math.pi / 2):
            C.box('Oeil-de-boeuf keystone', (cx + ux * (DRUM_R + .16) + tx * math.cos(ak) * .80, cy + uy * (DRUM_R + .16) + ty * math.cos(ak) * .80, zc + math.sin(ak) * .80), (.28, .28, .30), 'stone', 'dome', 0)
    for k in range(8):
        a = base + math.radians(24.0 + 45.0 * k)
        px, py = cx + math.cos(a) * DRUM_R, cy + math.sin(a) * DRUM_R
        C.beam('Drum pilaster', (px, py, CORNICE + .36), (px, py, z1 - .42), .55, .26, 'stone', 'dome')
    profile = [(1.0, 0.0), (1.05, .10), (1.04, .25), (.96, .42), (.82, .58), (.64, .72), (.44, .84), (.26, .93), (.10, .985), (0.0, 1.0)]
    dz = z1 + .20
    dome('Zinc dome', cx, cy, dz, DOME_R, DOME_H, profile, 'zinc', 'dome', 48, 28)
    sp = smooth_profile(profile, 36)
    for k in range(16):
        rib_mesh('Dome rib', cx, cy, dz, base + math.pi / 16 + math.tau * k / 16, [(rf * DOME_R, zf * DOME_H) for rf, zf in sp if zf <= .95], .11, .05, 'zinc', 'dome')
    # Projecting framed oculus dormer at the dome base on the chamfer axis (v001 P1 4, v002 P1 2): a zinc cylinder hood
    # seated on the shell, a moulded stone annulus frame on its face, a dark annular reveal and recessed glass, scroll
    # cheeks and a flat stone hood cap; nothing passes through anything else.
    ux, uy = math.cos(base), math.sin(base)
    px, py, pz = cx + ux * (DOME_R * .96), cy + uy * (DOME_R * .96), dz + DOME_H * .22
    n = (ux * .97, uy * .97, .24)
    q = lambda d: (px + n[0] * d, py + n[1] * d, pz + n[2] * d)
    C.rod('Oculus hood', q(-1.3), q(.36), .80, 'zinc', 'dome', 24)
    annulus('Oculus hood ring', q(0), n, .58, .80, .36, .78, 'zinc', 'dome', 24)
    C.rod('Oculus dark backing', q(.37), q(.40), .56, 'hardware', 'dome', 24)
    annulus('Oculus ring frame', q(0), n, .54, .86, .78, 1.02, 'stone', 'dome', 24)
    annulus('Oculus ring bead', q(0), n, .70, .80, 1.02, 1.08, 'stone', 'dome', 24)
    annulus('Oculus reveal', q(0), n, .50, .56, .40, .80, 'hardware', 'dome', 24)
    C.rod('Oculus glass', q(.44), q(.47), .52, 'glass', 'dome', 24)
    C.beam('Oculus bar', (q(.50)[0] - uy * .50, q(.50)[1] + ux * .50, q(.50)[2]), (q(.50)[0] + uy * .50, q(.50)[1] - ux * .50, q(.50)[2]), .04, .04, 'hardware', 'dome')
    for sgn in (-1, 1):
        C.box('Oculus cheek', (px + n[0] * .1 - uy * sgn * 1.02, py + n[1] * .1 + ux * sgn * 1.02, pz - .30), (.46, .46, 1.3), 'zinc', 'dome', 0)
    C.beam('Oculus hood cap', (q(-.2)[0], q(-.2)[1], q(-.2)[2] + .95), (q(1.0)[0], q(1.0)[1], q(1.0)[2] + .95), 2.0, .18, 'stone', 'dome')
    lz = dz + DOME_H + .30
    C.rod('Lantern neck', (cx, cy, dz + DOME_H * .82), (cx, cy, lz + .02), .55, 'zinc', 'dome', 8)
    C.rod('Lantern base', (cx, cy, lz), (cx, cy, lz + .22), .85, 'zinc', 'dome', 8)
    for k in range(8):
        a = math.tau * k / 8
        C.beam('Lantern column', (cx + math.cos(a) * .64, cy + math.sin(a) * .64, lz + .22), (cx + math.cos(a) * .64, cy + math.sin(a) * .64, lz + 1.4), .08, .08, 'pale', 'dome')
    C.rod('Lantern cap ring', (cx, cy, lz + 1.4), (cx, cy, lz + 1.6), .88, 'zinc', 'dome', 8)
    dome('Lantern bell', cx, cy, lz + 1.6, .82, 1.05, [(1.0, 0.0), (1.0, .18), (.86, .48), (.5, .8), (0.0, 1.0)], 'zinc', 'dome', 24, 10)
    C.rod('Finial', (cx, cy, lz + 2.55), (cx, cy, lz + 3.6), .05, 'gilt', 'dome', 8)
    C.rod('Finial ball', (cx, cy, lz + 3.0), (cx, cy, lz + 3.34), .17, 'gilt', 'dome', 12)
    C.CONTACTS.append(dict(name='Drum on a corbel ring over the chamfer cornice and the adjoining walls; zinc dome on the drum cornice; oculus dormer seated on the shell; lantern on a solid neck', drum_top_m=z1, dome_top_m=dz + DOME_H))


def cone(name, cx, cy, z0, r0, z1, r1, role, module, segs=24):
    vs = [(cx + r0 * math.cos(math.tau * i / segs), cy + r0 * math.sin(math.tau * i / segs), z0) for i in range(segs)]
    vs += [(cx + max(r1, .001) * math.cos(math.tau * i / segs), cy + max(r1, .001) * math.sin(math.tau * i / segs), z1) for i in range(segs)]
    fs = [tuple(range(segs - 1, -1, -1)), tuple(range(segs, 2 * segs))] + [(i, (i + 1) % segs, (i + 1) % segs + segs, i + segs) for i in range(segs)]
    return C.mesh(name, vs, fs, role, module)


def roofs_and_floors():
    outer = [(CX0, -D / 2), (W / 2, -D / 2), (W / 2, D / 2), (-W / 2, D / 2), (-W / 2, CY1)]
    inner = offset_polygon(outer, T)
    cx, hw, cy, hd = COURT
    court = [(cx - hw, cy - hd), (cx + hw, cy - hd), (cx + hw, cy + hd), (cx - hw, cy + hd)]
    C.prism('Ground slab', outer, 'z', 0.0, G0, 'foundation', 'foundation')
    C.prism('Court paving', [(x * .999, y * .999) for x, y in court], 'z', G0, G0 + .01, 'stone', 'court')
    # Floors as four strips around the court (the court sits inside the rectangle part of the plan).
    for zl in LEVELS + [CORNICE]:
        ci = T + .02      # court-side floor edges stop inside the court walls (shared planes render black, v002 P1 3)
        for poly in ([(CX0 + .2, -D / 2 + T), (W / 2 - T, -D / 2 + T), (W / 2 - T, cy - hd - ci), (-W / 2 + T, cy - hd - ci), (-W / 2 + T, CY1 + .2)],
                     [(-W / 2 + T, cy + hd + ci), (W / 2 - T, cy + hd + ci), (W / 2 - T, D / 2 - T), (-W / 2 + T, D / 2 - T)],
                     [(-W / 2 + T, cy - hd - ci - EPS), (cx - hw - ci, cy - hd - ci - EPS), (cx - hw - ci, cy + hd + ci + EPS), (-W / 2 + T, cy + hd + ci + EPS)],
                     [(cx + hw + ci, cy - hd - ci - EPS), (W / 2 - T, cy - hd - ci - EPS), (W / 2 - T, cy + hd + ci + EPS), (cx + hw + ci, cy + hd + ci + EPS)]):
            C.prism(f'Floor {zl:.1f}', poly, 'z', zl - .28, zl, 'floor', 'occupied floors')
    for zl in LEVELS:
        C.qa_room_light(f'South rooms {zl:.1f}', (-4.0, -D / 2 + 4.0, zl + 2.6), 70, 5.0)
        C.qa_room_light(f'West rooms {zl:.1f}', (-W / 2 + 4.0, 2.0, zl + 2.6), 60, 5.0)
    C.qa_room_light('Cafe', (CMX + 4.0, CMY + 4.0, LEVELS[0] - .8), 110, 6.0)
    C.qa_room_light('Court', (COURT[0], COURT[2], 17.5), 700, 10.0)
    # Court faces.
    cf = A.faces(2 * hw, 2 * hd, cx, cy, 'court ')
    for i, f in enumerate(cf):
        f = C.Face(f.o, f.t, f.n * -1, f.label)
        span = 2 * hw if i % 2 == 0 else 2 * hd
        lo, hi = (-span / 2, span / 2 - EPS) if i % 2 == 0 else (-span / 2 - T + .02, span / 2 + T - .02)   # side walls run into the front and rear walls (v003 P1 2)
        nb = max(1, int(span / 4.0)); pitch = span / nb
        hs = []
        for k in range(nb):
            c = lo + pitch * (k + .5)
            hs.append(hole(f'{f.label} ground window {k}', c, 1.1, 1.2, 2.2))
            for j, zl in enumerate(LEVELS):
                hs.append(hole(f'{f.label} window {k}-{j}', c, zl + .3, 1.2, 2.2))
        f.wall(f'{f.label} carrier', lo, hi, G0, CORNICE + .40, depth=T, role='wall', holes=hs)
        G.brick_courses(f, lo + .02, hi - .02, G0 + .3, CORNICE - .6, hs, spacing=.60)
        m = Merge(f)
        for h in hs:
            framed(m, f, h, cols=1, rows=1, occupied='apartment')
            m.box('stone', h['u'], -.04, h['z'] + h['h'] + .12, h['w'] + .36, T + .14, .16)
            m.box('stone', h['u'], -.06, h['z'] - .08, h['w'] + .30, T + .18, .12)
        eave_cornice(m, lo, hi, CORNICE, T, .36, modillions=False)
        m.flush('court')
    # Mansards: outer ring (closed pentagon), court ring, flat zinc annulus between them.
    top_outer = offset_polygon(outer, MANS_IN)
    strip('Outer mansard', outer, top_outer, CORNICE, CORNICE + MANS_H, 'zinc', 'mansard')
    court_top = [(x + (MANS_IN if x > cx else -MANS_IN), y + (MANS_IN if y > cy else -MANS_IN)) for x, y in court]
    strip('Court mansard', court[::-1], court_top[::-1], CORNICE, CORNICE + MANS_H, 'zinc', 'mansard')
    zt = CORNICE + MANS_H
    court5 = [court_top[0], court_top[1], court_top[2], court_top[3], court_top[0]]      # pentagon outer ring against the quad court: the chamfer ends both map to the court's south-west corner
    strip('Zinc flat', top_outer, court5, zt + .04, zt + .04, 'zinc', 'mansard')
    for x, y in ((W / 2 - 4.0, -D / 2 + 4.0), (W / 2 - 4.0, D / 2 - 4.0), (-W / 2 + 4.0, D / 2 - 4.0), (-2.0, -D / 2 + 4.5)):
        C.box('Chimney stack', (x, y, zt + 1.0), (1.4, .9, 2.4), 'stone', 'chimneys', 0)
        C.box('Chimney pots', (x, y, zt + 2.32), (1.1, .5, .30), 'rustic', 'chimneys', 0)
    # Dormers on every street bay and on the rear faces.
    for f, lo, hi in ((C.Face(((CX0 + W / 2) / 2, -D / 2, 0), (1, 0, 0), (0, 1, 0), 'south'), -(W / 2 - CX0) / 2, (W / 2 - CX0) / 2),
                      (C.Face((-W / 2, (CY1 + D / 2) / 2, 0), (0, -1, 0), (1, 0, 0), 'west'), -(D / 2 - CY1) / 2, (D / 2 - CY1) / 2),
                      (C.Face((0, D / 2, 0), (-1, 0, 0), (0, -1, 0), 'north'), -W / 2, W / 2),
                      (C.Face((W / 2, 0, 0), (0, 1, 0), (-1, 0, 0), 'east'), -D / 2, D / 2)):
        nb = max(1, round((hi - lo) / BAY)); pitch = (hi - lo) / nb
        for i in range(nb):
            u = lo + pitch * (i + .5)
            if f.label in ('south', 'west') and abs(u - lo) < pitch:    # the bay beside the chamfer is under the drum
                continue
            mansard_dormer(f, u, CORNICE, MANS_H, MANS_IN)
    # Interior for the cafe camera.
    A.sofa(-6.0, -D / 2 + 5.0, LEVELS[0]); A.desk(0.0, -D / 2 + 3.0, LEVELS[0] + .05)
    C.box('Salon partition', (3.0, -D / 2 + 5.0, LEVELS[0] + 1.6), (.16, 8.0, 3.2), 'interior', 'partitions', 0)


def site():
    ext = 7.0
    C.box('South sidewalk', (0, -D / 2 - 2.0, .0075), (W + 2 * ext, 4.0, .015), 'foundation', 'sidewalk', 0)
    C.box('West sidewalk', (-W / 2 - 2.0, 2.0, .0075), (4.0, D + ext - 4.0 + 1.0, .015), 'foundation', 'sidewalk', 0)
    C.box('Kerb south', (0, -D / 2 - 4.0 + .06, .06), (W + 2 * ext, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb west', (-W / 2 - 4.0 + .06, 1.5, .06), (.12, D + ext - 3.0, .12), 'stone', 'sidewalk', 0)
    C.box('Street south', (0, -D / 2 - 5.5, .004), (W + 2 * ext, 3.0, .008), 'concrete', 'street', 0)
    C.box('Street west', (-W / 2 - 5.5, 1.5, .004), (3.0, D + ext - 3.0, .008), 'concrete', 'street', 0)
    C.box('Rear lane', (0, D / 2 + 2.0, .0075), (W, 4.0, .015), 'foundation', 'court', 0)
    C.box('East lane', (W / 2 + 2.0, 0, .0075), (4.0, D, .015), 'foundation', 'court', 0)
    # Cafe terrace on the corner sidewalk: round tables and chairs.
    nx, ny = CN
    for k, (du, dd) in enumerate(((-2.2, 1.6), (0.0, 1.8), (2.2, 1.6), (-1.0, 3.2), (1.2, 3.2))):
        tx, ty = -ny, nx
        x, y = CMX + tx * du - nx * dd, CMY + ty * du - ny * dd
        C.rod('Cafe table top', (x, y, .70), (x, y, .74), .35, 'timber', 'cafe terrace', 16)
        C.rod('Cafe table leg', (x, y, .02), (x, y, .70), .03, 'hardware', 'cafe terrace', 8)
        for sgn in (-1, 1):
            A.garden_chair(x + tx * sgn * .6, y + ty * sgn * .6, .02)
    for sgn in (-1, 1):
        A.shrub(CMX - nx * 1.0 + (-ny) * sgn * 3.6, CMY - ny * 1.0 + nx * sgn * 3.6, .02, .9)
    street_tree(-W / 2 - 2.4, 8.0, height=9.0, spread=2.0)
    street_tree(9.0, -D / 2 - 2.4, height=9.0, spread=2.0)
    for u in range(-3, 4):
        C.rod('Bollard', (-W / 2 - 3.6, u * 3.0, 0.0), (-W / 2 - 3.6, u * 3.0, .9), .07, 'hardware', 'sidewalk', 8)


def build():
    site()
    roofs_and_floors()
    south = C.Face(((CX0 + W / 2) / 2, -D / 2, 0), (1, 0, 0), (0, 1, 0), 'south')
    west = C.Face((-W / 2, (CY1 + D / 2) / 2, 0), (0, -1, 0), (1, 0, 0), 'west')
    north = C.Face((0, D / 2, 0), (-1, 0, 0), (0, -1, 0), 'north')
    east = C.Face((W / 2, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    hs = (W / 2 - CX0) / 2; hw = (D / 2 - CY1) / 2
    pitch, gs = elevation(south, -hs, hs, street=True, cafe_bays=(0, 1))
    pitch, gw = elevation(west, -hw + T, hw, street=True, cafe_bays=(7, 8) if round(2 * hw / BAY) == 9 else tuple(range(round(2 * hw / BAY) - 2, round(2 * hw / BAY))))
    elevation(north, -W / 2, W / 2, street=False)
    elevation(east, -D / 2 + T, D / 2 - T, street=False)
    # One continuous awning: along the west face from the last cafe bay, round the chamfer, along the south face.
    cafe_s = [h for h in gs if h.get('cafe')]
    cafe_w = [h for h in gw if h.get('cafe')]
    s_end = south.p(cafe_s[-1]['u'] + pitch / 2 - .2, 0, 0)[:2]
    w_start = west.p(cafe_w[0]['u'] - pitch / 2 + .2, 0, 0)[:2]
    awning_path([w_start, (CX1, CY1), (CX0, CY0), s_end])
    chamfer_bay()
    drum_and_dome()


LIGHT_RIG = dict(key=(-40, -44, 46), fill=(44, -24, 34), rear=(-18, 44, 42), target=(0, 0, 12.0), gain=7.0)
