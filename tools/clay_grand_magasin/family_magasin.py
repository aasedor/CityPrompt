"""Belle Epoque department store with a glass corner dome, authored from the locked catalogue views of
grand_magasin / variant_0 (grand-magasin-belle-epoque).

Read from the pixels: a corner block with streets south and west around an inner light well. A
double-height ground floor of continuous display windows under a glass marquise carrying a sign band;
four upper storeys of tall iron-and-glass bays with gilded balcony fronts between limestone pilasters,
the top storey round-arched under a bracketed cornice; a zinc mansard with dormers; a curved glazed
corner bay crowned by a drum and a ribbed glass dome with a lantern; a smaller glass dome at the far
end of the west face (top view).
"""
import math
import clay_core as C
import assemblies as A
import geometry as G
from contract import subtract_openings

SLUG = 'clay-grand-magasin'
W, D = 44.0, 36.0
R = 7.0                           # corner bay radius
COURT = (1.0, 7.0, 3.0, 6.0)      # inner court: cx, half width, cy, half depth (large and central, v001 P1 4)
T = .36
G0 = .15
GF = 6.2                          # double-height ground floor
LEVELS = [6.2, 10.0, 13.6, 17.2]  # upper floor levels
CORNICE = 21.0
MANS_H, MANS_IN = 3.4, 1.4
UPPER_RISE = 2.4                  # hipped upper roofs over each wing (v001 P1 3)
ATTIC_H = 3.6                     # solid stone attic of the corner drum above the cornice (v001 P0 1)
PAV_OUT = .5                      # flanking pavilion projection beside the corner bay (v001 P1 6)
DRUM_R, DRUM_H = 6.0, 3.6
DOME_R, DOME_H = 6.2, 5.8
SMALL = (-W / 2 + 4.6, D / 2 - 4.6, 2.8, 2.4)   # second glass dome: x, y, radius, height
BAY = 5.0
CANOPY_Z, CANOPY_OUT = 4.4, 2.4
EPS = .002
PALETTE = dict(wall=(.76, .72, .62), joint=(.60, .56, .48), trim=(.16, .17, .16),
    pale=(.80, .77, .70), stone=(.74, .70, .60), roof=(.40, .44, .48), sand=(.70, .64, .52),
    foundation=(.46, .46, .45), glass=(.46, .54, .56), hardware=(.14, .14, .13),
    interior=(.80, .76, .68), floor=(.46, .44, .42), timber=(.34, .22, .14), blue=(.14, .22, .28),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.64, .62, .58), zinc=(.40, .44, .48),
    gilt=(.78, .62, .24), signband=(.40, .08, .08), rustic=(.70, .66, .56))

ACX, ACY = -W / 2 + R, -D / 2 + R          # arc centre (also the dome centre)
CN = (-1 / math.sqrt(2), -1 / math.sqrt(2))


def manifest(version):
    h = CORNICE + ATTIC_H + DRUM_H + .4 + DOME_H + 4.0
    cams = G.camera_roster(W + 8.0, D + 8.0, h, [
        ('facade_close', (-6.0, -36.0, 7.0), (0.0, -D / 2, 10.0), 45),
        ('architecture_close', (-40.0, -38.0, 16.0), (ACX, ACY, 14.0), 50),
        ('glass_close', (-8.0, -26.0, 2.4), (-3.0, -D / 2, 3.0), 50),
        ('corner_dome', (-42.0, -42.0, 32.0), (ACX, ACY, 29.0), 45),
        ('marquise_sign', (-30.0, -30.0, 2.6), (ACX + CN[0] * R, ACY + CN[1] * R, 4.0), 40),
        ('gilded_balconies', (-10.0, -28.0, 11.0), (-4.0, -D / 2, 12.0), 45),
        ('mansard_dormers', (8.0, -34.0, 22.0), (10.0, -D / 2, 22.5), 45),
        ('roof_domes', (-46.0, -50.0, 46.0), (0.0, 2.0, 20.0), 45),
        ('interior', (-2.0, -D / 2 + 1.2, 1.7), (-2.0, -D / 2 + 9.0, 3.0), 45),
        ('rear_court', (COURT[0] + 5.0, COURT[2] + 4.5, 26.0), (COURT[0] - 5.0, COURT[2] - 4.0, 4.0), 35)])
    for c in cams:
        if c['name'] == 'front':          # eye level on the corner axis (locked front)
            c['location'] = (ACX + CN[0] * 70.0, ACY + CN[1] * 70.0, 1.7); c['target'] = (ACX, ACY, 15.0); c['lens'] = 30; c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='grand_magasin/variant_0 (grand-magasin-belle-epoque)',
        measurement_contract=dict(dimensions_m=dict(width=W + 8.0, depth=D + 8.0, height=h),
            observed_storeys=5, storey_programme='double-height display ground floor, four sales storeys, mansard attic',
            plan='44 x 36 m corner block (top view) around a 14 x 12 m central court with inner facades, streets south and west, a 7 m radius curved corner bay under the dome, one-bay stone pavilions projecting 0.5 m beside it',
            facade='bays at 5.0 m: display windows 4.2 x 4.1 m with transoms at the ground floor under a glass marquise projecting 2.4 m with a sign band; upper bays 3.6 x 3.0 m of iron-and-glass with solid gilded panel fronts at every storey between limestone pilasters; round-arched top storey; bracketed cornice at 21.0 m with a continuous gilded balustrade on the street faces; flanking pavilions with segmental-arched gable dormers through the mansard',
            levels_m=[G0] + LEVELS, cornice_m=CORNICE, mansard='3.4 m zinc mansard set in 1.4 m with arched dormers at every bay; hipped zinc upper roofs rising 2.4 m to ridges along each wing, inner slopes to the court',
            dome='stone attic cylinder 12 m across rising 3.6 m above the corner-bay cornice with five arched windows and a gilded balcony ring on top; glazed drum 3.6 m high with sixteen iron posts and a cornice; ribbed glass dome 12.4 m across and 5.8 m high with sixteen iron ribs and purlin rings; glazed lantern and finial; a second glass dome 5.6 m across at the north end of the west face',
            corner='quarter-round glazed bay on seven facets between stone piers, glazed doors at the centre, gilded balconies at every storey',
            inferred='north and east faces repeat the grammar without balconies; light-well faces plain; interiors are teaching assumptions; the second dome position is read from the top view'),
        roof_contract=dict(type='zinc mansard with dormers and hipped upper roofs; glass domes', datum_m=CORNICE, crowns_m=[CORNICE + MANS_H + UPPER_RISE, CORNICE + ATTIC_H + DRUM_H + .4 + DOME_H, h]),
        identity_contract=dict(owner='glass corner dome over the curved glazed bay, gilded balcony fronts on iron-and-glass bays between limestone pilasters, marquise with sign band over continuous display windows, zinc mansard, second glass dome'),
        material_contract=dict(profile='source-palette clay: pale limestone with recessed joints, dark iron frames, gilt balcony lattices, glass drum and domes, zinc roofs, dark red sign band', textured_keeper=False),
        programme_contract=dict(storeys=6, ground='sales hall and display windows, corner entrance', upper='sales floors around the light well', roof='attic workrooms in the mansard'),
        contact_contract=['Grade-zero slab and sidewalks', 'Balconies cantilevered from the carriers', 'Marquise on brackets from the ground-floor carrier', 'Mansard seated on the cornice', 'Drum on the corner bay walls through the mansard; dome on the drum cornice; lantern on a solid collar', 'Second dome on a curb on the flat'],
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


def mansard_dormer(f, u, z_e, rise, setin, w=1.5, role='zinc'):
    k = setin / rise
    d0 = .30
    z_em = z_e + d0 / k
    z_top = z_e + 2.85
    zw, hw, ww = z_e + .95, 1.5, .95
    front = f.panel(f'{f.label} dormer front', [(u - w / 2, z_em - .6), (u + w / 2, z_em - .6), (u + w / 2, z_top), (u - w / 2, z_top)], d0 - .16, d0 + .10, role, 'dormers')
    f.cut(front, f'{f.label} dormer window cut', u, zw, ww, hw, depth=.30)
    g = C.Face(f.p(0, d0 - .16, 0), f.t, f.n, f.label + ' dormer')
    mg = Merge(g)
    h = hole(f'{f.label} dormer window {u:.1f}', u, zw, ww, hw)
    framed(mg, g, h, cols=1, rows=2, inset=.10, occupied='attic workroom', kind='dormer window')
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
    n = len(pts)
    lines = []
    for i in range(n):
        (ax, ay), (bx, by) = pts[i], pts[(i + 1) % n]
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
        lines.append((ax - uy * dist, ay + ux * dist, ux, uy))
    out = []
    for i in range(n):
        px, py, ux, uy = lines[i - 1]; qx, qy, vx, vy = lines[i]
        den = ux * vy - uy * vx
        t = ((qx - px) * vy - (qy - py) * vx) / den
        out.append((px + ux * t, py + uy * t))
    return out


def gilt_front(m, f, u, z, w, depth=.55):
    """Gilded balcony front: thin stone shelf, a solid gilt backing panel and raised scroll relief (dense, v001 P1 7)."""
    m.box('stone', u, -depth / 2 + .02, z - .08, w, depth + .04, .16)
    m.box('gilt', u, -depth + .05, z + .52, w, .04, .92)                       # solid panel
    m.box('gilt', u, -depth + .02, z + .98, w + .04, .09, .08)                 # top rail
    m.box('gilt', u, -depth + .02, z + .06, w + .04, .09, .08)                 # base rail
    n = max(2, int(w / .95))
    for i in range(n):
        c = u - w / 2 + w * (i + .5) / n
        m.box('gilt', c, -depth + .005, z + .52, .12, .03, .74)                # relief: central stem
        m.box('gilt', c, -depth + .005, z + .56, .46, .03, .12)                # relief: cross bar
    for e in (-1, 1):
        m.box('gilt', u + e * (w / 2 - .02), -depth / 2 + .02, z + .98, .06, depth - .04, .06)
        m.box('gilt', u + e * (w / 2 - .02), -depth / 2 + .02, z + .52, .04, depth - .08, .92)


def elevation(f, lo, hi, street=True, pavilion_end=None):
    span = hi - lo
    nb = max(1, round(span / BAY))
    pitch = span / nb
    g, up = [], []
    for i in range(nb):
        c = lo + pitch * (i + .5)
        if street:
            g.append(hole(f'{f.label} display window {i}', c, G0, 4.2, 4.1, kind='storefront'))
        else:
            g.append(hole(f'{f.label} ground window {i}', c, 1.2, 2.4, 3.2))
        for k, zl in enumerate(LEVELS):
            up.append(hole(f'{f.label} bay {i}-{k}', c, zl + .25, 3.6, 3.0 if k < 3 else 2.9, kind='iron and glass bay', level=k))
    holes = g + up
    f.wall(f'{f.label} ground carrier', lo, hi - EPS, G0, LEVELS[0] - .30, depth=T, role='stone', holes=holes)
    f.wall(f'{f.label} upper carrier', lo, hi - EPS, LEVELS[0] - .30, CORNICE + .40, depth=T, role='wall', holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, LEVELS[0] + .2, CORNICE - .9, up, spacing=1.4)
    m = Merge(f)
    if pavilion_end is not None:       # closed return of the projecting pavilion, overlapping the wing carrier
        m.box('stone', pavilion_end[0] + pavilion_end[1] * (T / 2 + .012), (T - .03 + PAV_OUT + T * .6) / 2, (G0 + CORNICE + .45) / 2, T, PAV_OUT + T * .6 - (T - .03), CORNICE + .45 - G0)
    for h in g:
        if street:
            reveal(m, f, h, .18, 'stone')
        if street:
            framed(m, f, h, cols=3, rows=2, inset=.18, occupied='sales hall', kind='storefront', frame='trim')
            m.box('trim', h['u'], .12, h['z'] + .30, h['w'] - .14, .06, .40)         # stall riser
        else:
            framed(m, f, h, cols=1, rows=1, occupied='stock rooms')
        m.box('stone', h['u'], -.05, h['z'] + h['h'] + .20, h['w'] + .50, T + .16, .32)
    for h in up:
        if street:
            reveal(m, f, h, .16, 'stone')
        framed(m, f, h, cols=3 if street else 2, rows=2 if street else 1, occupied='sales floor', kind='iron and glass bay', frame='trim')
        k = h['level']
        if k == 3:
            arch_fill(f, h['u'], h['z'] + h['h'], h['w'], h['w'] * .32, 'wall')
            m.box('stone', h['u'], -.06, h['z'] + h['h'] + .26, h['w'] + .70, T + .18, .22)
        else:
            m.box('stone', h['u'], -.05, h['z'] + h['h'] + .16, h['w'] + .50, T + .16, .26)
        if street:
            gilt_front(m, f, h['u'], h['z'], h['w'] + .40)
        else:
            m.box('stone', h['u'], -.08, h['z'] - .08, h['w'] + .40, T + .22, .12)
    # Limestone pilasters between the bays from the first floor to the cornice, with capitals.
    for i in range(nb + 1):
        u = lo + pitch * i
        if i in (0, nb) and not street:
            continue
        uu = min(max(u, lo + .55), hi - .55)
        m.box('stone', uu, -.12, (LEVELS[0] - .30 + CORNICE - 1.10) / 2, 1.0, T + .28, CORNICE - 1.10 - LEVELS[0] + .30)
        m.box('stone', uu, -.18, CORNICE - 1.18, 1.24, T + .40, .36)
        m.box('stone', uu, -.16, LEVELS[0] - .10, 1.18, T + .36, .28)
    m.box('stone', (lo + hi) / 2, -.08, LEVELS[0] - .22, span - 2 * EPS, T + .24, .36)
    eave_cornice(m, lo, hi, CORNICE, T, .80)
    if street:
        gilt_balustrade(m, lo + .05, hi - .05, CORNICE + .03)
    m.flush('facade')
    if street:
        marquise(f, lo + .10, hi - .10)
    return pitch, g


def gilt_balustrade(m, lo, hi, z, d=-.30):
    """Continuous gilded balustrade on the cornice: solid gilt panel with pedestals, top rail and finial balls."""
    span = hi - lo
    m.box('gilt', (lo + hi) / 2, d, z + .50, span, .06, .80)
    m.box('gilt', (lo + hi) / 2, d, z + .94, span + .04, .12, .10)
    n = max(2, int(span / 2.5))
    for i in range(n + 1):
        u = lo + .15 + (span - .30) * i / n
        m.box('stone', u, d, z + .50, .36, .36, 1.0)
        m.box('gilt', u, d, z + 1.12, .22, .22, .22)


def marquise(f, lo, hi):
    """Glass marquise on iron brackets with the dark sign band on its fascia."""
    out = CANOPY_OUT
    lower = [f.p(lo, -out, 0)[:2], f.p(hi, -out, 0)[:2]]
    upper = [f.p(lo, -.02, 0)[:2], f.p(hi, -.02, 0)[:2]]
    strip(f'{f.label} marquise glass', lower, upper, CANOPY_Z - .18, CANOPY_Z + .10, 'glass', 'marquise', closed=False)
    m = Merge(f)
    m.box('hardware', (lo + hi) / 2, -out + .04, CANOPY_Z - .12, hi - lo, .08, .10)        # edge beam
    m.box('signband', (lo + hi) / 2, -out + .02, CANOPY_Z - .62, hi - lo, .06, .90)       # sign band
    m.box('gilt', (lo + hi) / 2, -out - .01, CANOPY_Z - .62, hi - lo - 1.2, .03, .34)      # gilt lettering band (no text in clay)
    m.box('gilt', (lo + hi) / 2, -out + .00, CANOPY_Z - .14, hi - lo + .04, .06, .06)
    m.box('hardware', (lo + hi) / 2, .02, CANOPY_Z + .20, hi - lo, .06, .12)
    n = max(2, int((hi - lo) / 2.5))
    for i in range(n + 1):
        u = lo + .3 + (hi - lo - .6) * i / n
        m.box('hardware', u, -out / 2, CANOPY_Z - .04, .06, out, .07)                        # purlin
        a = f.p(u, .0, CANOPY_Z + .18); b = f.p(u, -out + .15, CANOPY_Z - .10)
        C.beam('Marquise tie', a, b, .04, .04, 'hardware', 'marquise')
        c = f.p(u, .0, CANOPY_Z + 1.5)
        C.beam('Marquise hanger', c, b, .035, .035, 'hardware', 'marquise')
    m.flush('marquise')


def corner_bay():
    """Quarter-round glazed bay on seven facets between stone piers; glazed doors at the centre facet."""
    facets = 7
    a0, a1 = math.radians(180), math.radians(270)
    pts = [(ACX + R * math.cos(a0 + (a1 - a0) * i / facets), ACY + R * math.sin(a0 + (a1 - a0) * i / facets)) for i in range(facets + 1)]
    for i in range(facets):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        length = math.dist((ax, ay), (bx, by))
        ux, uy = (bx - ax) / length, (by - ay) / length
        inx, iny = -uy, ux
        mx, my = (ax + bx) / 2, (ay + by) / 2
        if (ACX - mx) * inx + (ACY - my) * iny < 0:
            inx, iny = -inx, -iny
        f = C.Face((mx, my, 0), (ux, uy, 0), (inx, iny, 0), f'corner facet {i}')
        centre = i == facets // 2
        g = hole(f'corner facet {i} door' if centre else f'corner facet {i} display', 0.0, G0, length - .34, 4.1, kind='glazed door' if centre else 'storefront')
        up = [hole(f'corner facet {i} bay {k}', 0.0, zl + .25, length - .34, 3.0 if k < 3 else 2.9, kind='iron and glass bay', level=k) for k, zl in enumerate(LEVELS)]
        holes = [g] + up
        f.wall(f'corner facet {i} ground carrier', -length / 2, length / 2, G0, LEVELS[0] - .30, depth=T, role='stone', holes=holes)
        f.wall(f'corner facet {i} upper carrier', -length / 2, length / 2, LEVELS[0] - .30, CORNICE + .40, depth=T, role='stone', holes=holes)
        m = Merge(f)
        reveal(m, f, g, .18, 'stone'); framed(m, f, g, cols=1, rows=2, inset=.18, occupied='entrance hall' if centre else 'sales hall', kind=g['kind'], frame='trim')
        for h in up:
            reveal(m, f, h, .16, 'stone'); framed(m, f, h, cols=1, rows=2, occupied='sales floor', kind='iron and glass bay', frame='trim')
            if h['level'] == 3:
                arch_fill(f, 0.0, h['z'] + h['h'], h['w'], h['w'] * .32, 'stone')
        m.box('stone', 0.0, -.08, LEVELS[0] - .22, length - .02, T + .24, .36)
        m.box('stone', 0.0, -.10, CORNICE - .62, length - .02, T + .20, .26)
        m.flush('corner bay')
    # Slender iron columns at the facet joints, continuous gilt balcony fronts around the bay at every storey.
    for i in range(1, facets):
        jx, jy = pts[i]
        d = math.dist((jx, jy), (ACX, ACY)); jx, jy = jx + (ACX - jx) / d * .10, jy + (ACY - jy) / d * .10
        C.rod('Corner bay column', (jx, jy, G0 + .02), (jx, jy, CORNICE - .66), .14, 'hardware', 'corner bay', 12)
    for k, zl in enumerate(LEVELS):
        ring = [(ACX + (R + .55) * math.cos(a0 + (a1 - a0) * i / 28), ACY + (R + .55) * math.sin(a0 + (a1 - a0) * i / 28)) for i in range(29)]
        inner = [(ACX + (R - .10) * math.cos(a0 + (a1 - a0) * i / 28), ACY + (R - .10) * math.sin(a0 + (a1 - a0) * i / 28)) for i in range(29)]
        posts = ring[::2]
        strip(f'Corner balcony shelf {k}', ring, inner, zl - .16 + .18, zl - .16 + .18, 'stone', 'corner bay', closed=False)
        for (px, py) in posts:
            C.rod('Corner balcony picket', (px, py, zl + .10), (px, py, zl + .94), .018, 'gilt', 'corner bay', 4)
        for (px, py), (qx, qy) in zip(ring, ring[1:]):
            C.beam('Corner balcony rail', (px, py, zl + .96), (qx, qy, zl + .96), .06, .06, 'gilt', 'corner bay')
            C.beam('Corner balcony mid rail', (px, py, zl + .52), (qx, qy, zl + .52), .035, .035, 'gilt', 'corner bay')
    # Stone piers at the two ends of the bay, full height, with capitals; glazed marquise around the bay.
    for (qx, qy) in (pts[0], pts[-1]):
        C.box('Corner bay pier', (qx, qy, (CORNICE + .40) / 2), (1.3, 1.3, CORNICE + .40), 'stone', 'corner posts', 0)
        C.box('Corner bay pier capital', (qx, qy, CORNICE - 1.18), (1.6, 1.6, .36), 'stone', 'corner posts', 0)
        C.box('Corner bay pier cornice block', (qx, qy, CORNICE - .36), (2.0, 2.0, .72), 'stone', 'corner posts', 0)
    outer = [(ACX + (R + CANOPY_OUT) * math.cos(a0 + (a1 - a0) * i / 14), ACY + (R + CANOPY_OUT) * math.sin(a0 + (a1 - a0) * i / 14)) for i in range(15)]
    inner = [(ACX + (R + .02) * math.cos(a0 + (a1 - a0) * i / 14), ACY + (R + .02) * math.sin(a0 + (a1 - a0) * i / 14)) for i in range(15)]
    strip('Corner marquise glass', outer, inner, CANOPY_Z - .18, CANOPY_Z + .10, 'glass', 'marquise', closed=False)
    for (px, py), (qx, qy) in zip(outer, outer[1:]):
        C.beam('Corner marquise edge', (px, py, CANOPY_Z - .12), (qx, qy, CANOPY_Z - .12), .08, .10, 'hardware', 'marquise')
        C.beam('Corner sign band', (px, py, CANOPY_Z - .62), (qx, qy, CANOPY_Z - .62), .06, .90, 'signband', 'marquise')
        C.beam('Corner gilt band', (px - (px - ACX) / (R + CANOPY_OUT) * .02, py - (py - ACY) / (R + CANOPY_OUT) * .02, CANOPY_Z - .62), (qx - (qx - ACX) / (R + CANOPY_OUT) * .02, qy - (qy - ACY) / (R + CANOPY_OUT) * .02, CANOPY_Z - .62), .03, .34, 'gilt', 'marquise')
    for i in range(0, 15, 2):
        ox, oy = outer[i]; ix, iy = inner[i]
        C.beam('Corner marquise purlin', (ix, iy, CANOPY_Z - .04), (ox, oy, CANOPY_Z - .04), .06, .07, 'hardware', 'marquise')
        C.beam('Corner marquise hanger', (ix, iy, CANOPY_Z + 1.5), (ox - (ox - ix) * .06, oy - (oy - iy) * .06, CANOPY_Z - .10), .035, .035, 'hardware', 'marquise')
    C.CONTACTS.append(dict(name='Curved bay facets on the ground slab; iron columns at the facet joints; gilt balconies on the shelves; piers close both ends', radius_m=R))


def gable_dormer(f, u, w=4.2):
    """Tall segmental-arched gable dormer rising from the pavilion cornice through the mansard: stone front with a round-headed
    window, cheeks back to the slope, zinc hipped cap."""
    z_e = CORNICE
    k = MANS_IN / MANS_H
    d0 = .10
    z_top = z_e + 4.6
    front = f.panel(f'{f.label} gable dormer front', [(u - w / 2, z_e - .2), (u + w / 2, z_e - .2), (u + w / 2, z_top - 1.2), (u + w * .3, z_top - .3), (u, z_top), (u - w * .3, z_top - .3), (u - w / 2, z_top - 1.2)], d0 - .20, d0 + .16, 'stone', 'dormers')
    ww, hw_, zw = 2.2, 2.6, z_e + .7
    f.cut(front, f'{f.label} gable window cut', u, zw, ww, hw_, depth=.4)
    g = C.Face(f.p(0, d0 - .20, 0), f.t, f.n, f.label + ' gable dormer')
    mg = Merge(g)
    h = hole(f'{f.label} gable window', u, zw, ww, hw_)
    reveal(mg, g, h, .14, 'stone'); framed(mg, g, h, cols=2, rows=2, inset=.14, occupied='attic salon', kind='arched window', frame='trim')
    for sgn in (-1, 1):
        mg.box('stone', u + sgn * (ww / 2 + .16), -.06, zw + hw_ / 2, .32, .20, hw_ + .32)
        mg.box('gilt', u + sgn * (ww / 2 + .16), -.10, zw + hw_ + .55, .32, .14, .32)
    mg.box('stone', u, -.08, z_top - 1.1, w - .4, .24, .30)                     # springing course
    mg.flush('dormers')
    arch_fill(g, u, zw + hw_, ww, ww / 2, 'stone', -.03, .40)
    for i in range(8):
        a0, a1 = math.pi * i / 8, math.pi * (i + 1) / 8
        pa = g.p(u + math.cos(a0) * (w / 2 - .25), -.12, z_top - 1.2 + math.sin(a0) * 1.05); pb = g.p(u + math.cos(a1) * (w / 2 - .25), -.12, z_top - 1.2 + math.sin(a1) * 1.05)
        C.beam('Gable dormer arch moulding', pa, pb, .16, .22, 'stone', 'dormers')
    for sgn in (-1, 1):
        uu = u + sgn * (w / 2 - .14)
        d_back = (z_top - .6 - z_e) * k
        pts = [(d0 - .16, z_e - .2), (d0 - .16, z_top - 1.3), (d_back, z_top - 1.3), (d_back, z_e + d_back / k - .9)]
        vs = [f.p(uu - .06, d, z) for d, z in pts] + [f.p(uu + .06, d, z) for d, z in pts]
        C.mesh('Gable dormer cheek', vs, [(3, 2, 1, 0), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], 'stone', 'dormers')
    d_back = (z_top - .6 - z_e) * k
    vs = [f.p(u - w / 2 - .15, d0 - .30, z_top - 1.25), f.p(u + w / 2 + .15, d0 - .30, z_top - 1.25), f.p(u + w / 2 + .15, d_back + .3, z_top - .55), f.p(u - w / 2 - .15, d_back + .3, z_top - .55)]
    vs += [(x, y, z - .18) for x, y, z in vs]
    C.mesh('Gable dormer cap', vs, [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 'zinc', 'dormers')


def glass_dome(cx, cy, z0, r, h, ribs=16, rings=4, lantern=True, module='dome', scale=1.0):
    profile = [(1.0, 0.0), (1.0, .10), (.97, .30), (.88, .50), (.72, .68), (.50, .84), (.26, .95), (0.0, 1.0)]
    dome('Glass dome', cx, cy, z0, r, h, profile, 'glass', module, 28, 16)
    sp = smooth_profile(profile, 22)
    for k in range(ribs):
        rib_mesh('Dome rib', cx, cy, z0, math.tau * k / ribs, [(rf * r, zf * h) for rf, zf in sp if zf <= .96], .10 * scale, .05 * scale, 'hardware', module)
    for j in range(1, rings + 1):
        rf, zf = sp[int(len(sp) * j / (rings + 1))]
        rr, zz = rf * r + .05, z0 + zf * h
        pts_ = [(cx + rr * math.cos(math.tau * i / 24), cy + rr * math.sin(math.tau * i / 24)) for i in range(25)]
        for (px, py), (qx, qy) in zip(pts_, pts_[1:]):
            C.beam('Dome purlin', (px, py, zz), (qx, qy, zz), .06 * scale, .06 * scale, 'hardware', module)
    if lantern:
        lz = z0 + h
        C.rod('Lantern collar', (cx, cy, lz - .45 * scale), (cx, cy, lz + .10 * scale), .70 * scale, 'hardware', module, 12)
        C.rod('Lantern glass', (cx, cy, lz + .10 * scale), (cx, cy, lz + 1.2 * scale), .55 * scale, 'glass', module, 12)
        for k in range(8):
            a = math.tau * k / 8
            C.beam('Lantern post', (cx + math.cos(a) * .58 * scale, cy + math.sin(a) * .58 * scale, lz + .10 * scale), (cx + math.cos(a) * .58 * scale, cy + math.sin(a) * .58 * scale, lz + 1.2 * scale), .05 * scale, .05 * scale, 'hardware', module)
        dome('Lantern cap', cx, cy, lz + 1.2 * scale, .72 * scale, .55 * scale, [(1.0, 0.0), (.8, .5), (0.0, 1.0)], 'zinc', module, 24, 8)
        C.rod('Finial', (cx, cy, lz + 1.7 * scale), (cx, cy, lz + 2.6 * scale), .05 * scale, 'gilt', module, 8)
        C.rod('Finial ball', (cx, cy, lz + 2.2 * scale), (cx, cy, lz + 2.5 * scale), .15 * scale, 'gilt', module, 12)


def drum_and_domes():
    cx, cy = ACX, ACY
    za = CORNICE + ATTIC_H                 # top of the solid stone attic (clear of the mansard top, v001 P0 1)
    z0, z1 = za, za + DRUM_H
    # Stone attic cylinder from the corner-bay cornice with five arched windows facing the streets, a cornice and a
    # gilded balcony ring on top; then the glazed drum of sixteen iron posts and the stone entablature.
    C.rod('Attic cylinder', (cx, cy, CORNICE - .40), (cx, cy, za - .36), DRUM_R + .10, 'stone', 'dome', 48)
    C.rod('Attic cornice', (cx, cy, za - .36), (cx, cy, za - .02), DRUM_R + .55, 'stone', 'dome', 48)
    base = math.atan2(CN[1], CN[0])
    for da in (-50.0, -25.0, 0.0, 25.0, 50.0):
        a = base + math.radians(da)
        ux, uy = math.cos(a), math.sin(a); tx, ty = -uy, ux
        for d_, role, wdt, hgt in ((.18, 'stone', 2.2, 2.9), (-.02, 'hardware', 1.6, 2.5), (-.08, 'glass', 1.5, 2.4)):
            px, py = cx + ux * (DRUM_R + .10 + d_), cy + uy * (DRUM_R + .10 + d_)
            C.beam('Attic window ' + role, (px - tx * wdt / 2, py - ty * wdt / 2, CORNICE + 1.3 + (hgt - 2.9) / 2), (px + tx * wdt / 2, py + ty * wdt / 2, CORNICE + 1.3 + (hgt - 2.9) / 2), .16, hgt, role, 'dome')
        for sgn in (-1, 1):
            C.beam('Attic window mullion', (cx + ux * (DRUM_R + .06) + tx * sgn * .3, cy + uy * (DRUM_R + .06) + ty * sgn * .3, CORNICE + .1), (cx + ux * (DRUM_R + .06) + tx * sgn * .3, cy + uy * (DRUM_R + .06) + ty * sgn * .3, CORNICE + 2.5), .06, .06, 'hardware', 'dome')
    ring = [(cx + (DRUM_R + .40) * math.cos(math.tau * i / 32), cy + (DRUM_R + .40) * math.sin(math.tau * i / 32)) for i in range(33)]
    inner = [(cx + (DRUM_R + .32) * math.cos(math.tau * i / 32), cy + (DRUM_R + .32) * math.sin(math.tau * i / 32)) for i in range(33)]
    strip('Attic balustrade panel', ring, inner, za + .86, za + .06, 'gilt', 'dome', closed=False)
    for (px, py), (qx, qy) in zip(ring, ring[1:]):
        C.beam('Attic balustrade rail', (px, py, za + .92), (qx, qy, za + .92), .10, .08, 'gilt', 'dome')
    for i in range(0, 32, 2):
        px, py = ring[i]
        C.box('Attic balustrade pedestal', (px, py, za + .5), (.34, .34, 1.0), 'stone', 'dome', 0)
    C.rod('Drum plinth', (cx, cy, za - .02), (cx, cy, za + .30), DRUM_R + .10, 'stone', 'dome', 48)
    C.rod('Drum glass', (cx, cy, za + .30), (cx, cy, z1 - .45), DRUM_R - .06, 'glass', 'dome', 48)
    for k in range(16):
        a = math.tau * k / 16
        px, py = cx + math.cos(a) * DRUM_R, cy + math.sin(a) * DRUM_R
        C.beam('Drum post', (px, py, za + .30), (px, py, z1 - .45), .26, .26, 'hardware', 'dome')
        for zz in (za + 1.3, za + 2.3):
            qx, qy = cx + math.cos(a + math.tau / 16) * DRUM_R, cy + math.sin(a + math.tau / 16) * DRUM_R
            C.beam('Drum transom', (px, py, zz), (qx, qy, zz), .05, .05, 'hardware', 'dome')
    C.rod('Drum entablature', (cx, cy, z1 - .45), (cx, cy, z1 - .12), DRUM_R + .30, 'stone', 'dome', 48)
    C.rod('Drum cornice', (cx, cy, z1 - .12), (cx, cy, z1 + .08), DRUM_R + .50, 'stone', 'dome', 48)
    C.rod('Dome base ring', (cx, cy, z1 + .08), (cx, cy, z1 + .30), DOME_R + .08, 'hardware', 'dome', 48)
    glass_dome(cx, cy, z1 + .30, DOME_R, DOME_H)
    sx, sy, sr, sh = SMALL
    zt = CORNICE + MANS_H + UPPER_RISE + .06
    C.rod('Second dome curb', (sx, sy, zt - 1.2), (sx, sy, zt + .5), sr + .15, 'stone', 'second dome', 32)
    glass_dome(sx, sy, zt + .5, sr, sh, ribs=8, rings=2, module='second dome', scale=.6)
    C.CONTACTS.append(dict(name='Stone attic on the corner bay cornice; gilded balustrade and glazed drum on the attic; dome on the drum cornice; second dome on its curb on the ridge band', attic_top_m=za, drum_top_m=z1, dome_top_m=z1 + .30 + DOME_H))


def roofs_and_floors():
    a0, a1 = math.radians(180), math.radians(270)
    arc = [(ACX + R * math.cos(a0 + (a1 - a0) * i / 7), ACY + R * math.sin(a0 + (a1 - a0) * i / 7)) for i in range(1, 7)]
    outer = [(ACX, -D / 2), (W / 2, -D / 2), (W / 2, D / 2), (-W / 2, D / 2), (-W / 2, ACY)] + arc
    cx, hw, cy, hd = COURT
    court = [(cx - hw, cy - hd), (cx + hw, cy - hd), (cx + hw, cy + hd), (cx - hw, cy + hd)]
    C.prism('Ground slab', outer, 'z', 0.0, G0, 'foundation', 'foundation')
    C.prism('Court paving', [(x * .999, y * .999) for x, y in court], 'z', G0, G0 + .01, 'stone', 'court')
    inner = offset_polygon(outer, T)
    for zl in LEVELS + [CORNICE]:
        slab = C.prism(f'Floor {zl:.1f}', inner, 'z', zl - .30, zl, 'floor', 'occupied floors')
        C.cut_box(slab, 'Light well cut', (cx, cy, zl - .15), (2 * hw + 2 * (T + .02), 2 * hd + 2 * (T + .02), 1.0))   # clear of the court wall planes
    for zl in [G0] + LEVELS:
        C.qa_room_light(f'South hall {zl:.1f}', (-6.0, -D / 2 + 5.0, zl + 2.8), 90, 6.0)
        C.qa_room_light(f'West hall {zl:.1f}', (-W / 2 + 5.0, 2.0, zl + 2.8), 70, 6.0)
    cf = A.faces(2 * hw, 2 * hd, cx, cy, 'light well ')
    for i, f in enumerate(cf):
        f = C.Face(f.o, f.t, f.n * -1, f.label)
        span = 2 * hw if i % 2 == 0 else 2 * hd
        lo, hi = (-span / 2, span / 2 - EPS) if i % 2 == 0 else (-span / 2 - T + .02, span / 2 + T - .02)   # side walls run into the front and rear walls
        nb = max(1, int(span / 4.0)); pitch = span / nb
        hs = []
        for k in range(nb):
            c = lo + pitch * (k + .5)
            hs.append(hole(f'{f.label} ground window {k}', c, 1.2, 2.4, 3.4))
            for j, zl in enumerate(LEVELS):
                hs.append(hole(f'{f.label} window {k}-{j}', c, zl + .4, 2.4, 2.6))
        f.wall(f'{f.label} carrier', lo, hi, G0, CORNICE + .40, depth=T, role='wall', holes=hs)
        m = Merge(f)
        for h in hs:
            framed(m, f, h, cols=1, rows=1, occupied='sales floor', frame='trim')
            m.box('stone', h['u'], -.04, h['z'] + h['h'] + .12, h['w'] + .36, T + .14, .16)
            m.box('stone', h['u'], -.06, h['z'] - .08, h['w'] + .30, T + .18, .12)
        for k in range(nb + 1):      # pilaster grid of the inner facades
            u = min(max(lo + pitch * k, lo + .4), hi - .4)
            m.box('stone', u, -.08, (LEVELS[0] + CORNICE - .9) / 2, .7, T + .20, CORNICE - .9 - LEVELS[0])
        for zl in LEVELS:
            m.box('stone', (lo + hi) / 2, -.05, zl - .16, hi - lo - 2 * EPS, T + .16, .22)
        eave_cornice(m, lo, hi, CORNICE, T, .36, modillions=False)
        m.flush('court')
        nbd = max(1, int(span / 5.0))
        for k in range(nbd):
            mansard_dormer(f, lo + span * (k + .5) / nbd, CORNICE, MANS_H, MANS_IN)
    C.qa_room_light('Court', (cx, cy, 12.0), 240, 10.0)
    top_outer = offset_polygon(outer, MANS_IN)
    strip('Outer mansard', outer, top_outer, CORNICE, CORNICE + MANS_H, 'zinc', 'mansard')
    court_top = [(x + (MANS_IN if x > cx else -MANS_IN), y + (MANS_IN if y > cy else -MANS_IN)) for x, y in court]
    strip('Court mansard', court[::-1], court_top[::-1], CORNICE, CORNICE + MANS_H, 'zinc', 'mansard')
    zt = CORNICE + MANS_H
    # Hipped upper roofs (v001 P1 3): outer slope from the mansard top to an outer ridge ring, a flat ridge band, and an
    # inner slope from an inner ridge ring down to the court mansard top.
    ridge_out = offset_polygon(outer, MANS_IN + 4.2)
    strip('Upper roof outer slope', top_outer, ridge_out, zt + .04, zt + .04 + UPPER_RISE, 'zinc', 'mansard')
    ridge_in = [(x + (3.6 if x > cx else -3.6), y + (3.6 if y > cy else -3.6)) for x, y in court_top]
    strip('Upper roof inner slope', ridge_in[::-1], court_top[::-1], zt + .04 + UPPER_RISE, zt + .04, 'zinc', 'mansard')
    band = C.prism('Ridge band', ridge_out, 'z', zt + UPPER_RISE - .10, zt + UPPER_RISE + .06, 'zinc', 'mansard')
    C.cut_box(band, 'Ridge band court cut', (cx, cy, zt + UPPER_RISE), (2 * (hw + MANS_IN + 3.6) - .02, 2 * (hd + MANS_IN + 3.6) - .02, 1.0))
    zr = zt + UPPER_RISE
    for x, y in ((W / 2 - 5.6, -D / 2 + 5.6), (W / 2 - 5.6, D / 2 - 5.6), (-2.0, D / 2 - 5.6)):
        C.box('Chimney stack', (x, y, zr + .9), (1.4, .9, 2.2), 'stone', 'chimneys', 0)
        C.box('Chimney pots', (x, y, zr + 2.12), (1.1, .5, .30), 'rustic', 'chimneys', 0)
    for x, y in ((12.0, -D / 2 + 5.6), (-W / 2 + 5.6, 8.0), (6.0, D / 2 - 5.6), (W / 2 - 5.6, 0.0)):
        C.box('Rooflight curb', (x, y, zr + .20), (2.2, 1.6, .30), 'stone', 'rooflights', 0)
        C.box('Rooflight', (x, y, zr + .50), (2.0, 1.4, .30), 'glass', 'rooflights', 0)
    for f, lo, hi in ((C.Face(((ACX + W / 2) / 2, -D / 2, 0), (1, 0, 0), (0, 1, 0), 'south'), -(W / 2 - ACX) / 2, (W / 2 - ACX) / 2),
                      (C.Face((-W / 2, (ACY + D / 2) / 2, 0), (0, -1, 0), (1, 0, 0), 'west'), -(D / 2 - ACY) / 2, (D / 2 - ACY) / 2),
                      (C.Face((0, D / 2, 0), (-1, 0, 0), (0, -1, 0), 'north'), -W / 2, W / 2),
                      (C.Face((W / 2, 0, 0), (0, 1, 0), (-1, 0, 0), 'east'), -D / 2, D / 2)):
        nb = max(1, round((hi - lo) / BAY)); pitch = (hi - lo) / nb
        for i in range(nb):
            u = lo + pitch * (i + .5)
            if f.label in ('south', 'west') and i == 0:        # the pavilion bay beside the corner carries the arched gable dormer
                continue
            if f.label == 'west' and i == nb - 1:               # under the second dome
                continue
            mansard_dormer(f, u, CORNICE, MANS_H, MANS_IN)
    # Sales hall for the interior view: counters and a column line.
    for x in (-8.0, -2.0, 4.0):
        C.rod('Hall column', (x, -D / 2 + 8.0, G0), (x, -D / 2 + 8.0, LEVELS[0] - .30), .30, 'hardware', 'hall', 12)
    for x, y in ((-6.0, -D / 2 + 5.0), (2.0, -D / 2 + 5.0), (-3.0, -D / 2 + 11.0)):
        C.box('Sales counter', (x, y, G0 + .5), (3.2, 1.1, 1.0), 'timber', 'hall', 0)


def site():
    ext = 8.0
    C.box('South sidewalk', (0, -D / 2 - 2.25, .0075), (W + 2 * ext, 4.5, .015), 'foundation', 'sidewalk', 0)
    C.box('West sidewalk', (-W / 2 - 2.25, 2.25, .0075), (4.5, D + ext - 4.5 + 1.5, .015), 'foundation', 'sidewalk', 0)
    C.box('Kerb south', (0, -D / 2 - 4.5 + .06, .06), (W + 2 * ext, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb west', (-W / 2 - 4.5 + .06, 1.5, .06), (.12, D + ext - 3.0, .12), 'stone', 'sidewalk', 0)
    C.box('Street south', (0, -D / 2 - 6.25, .004), (W + 2 * ext, 3.5, .008), 'concrete', 'street', 0)
    C.box('Street west', (-W / 2 - 6.25, 1.75, .004), (3.5, D + ext - 3.5, .008), 'concrete', 'street', 0)
    C.box('Rear lane', (0, D / 2 + 2.0, .0075), (W, 4.0, .015), 'foundation', 'court', 0)
    C.box('East lane', (W / 2 + 2.0, 0, .0075), (4.0, D, .015), 'foundation', 'court', 0)
    street_tree(-W / 2 - 2.6, 12.0, height=10.0, spread=2.2); street_tree(16.0, -D / 2 - 2.6, height=10.0, spread=2.2)
    for u in range(-2, 3):
        C.rod('Bollard', (u * 8.0, -D / 2 - 4.0, 0.0), (u * 8.0, -D / 2 - 4.0, .9), .07, 'hardware', 'sidewalk', 8)
    for k in range(2):
        x, y = -W / 2 - 3.6, 4.0 + k * 9.0
        C.rod('Lamp post', (x, y, 0.0), (x, y, 5.0), .07, 'hardware', 'sidewalk', 8)
        C.rod('Lamp head', (x, y, 5.0), (x, y, 5.5), .22, 'pale', 'sidewalk', 8)


def build():
    site()
    roofs_and_floors()
    south = C.Face(((ACX + W / 2) / 2, -D / 2, 0), (1, 0, 0), (0, 1, 0), 'south')
    west = C.Face((-W / 2, (ACY + D / 2) / 2, 0), (0, -1, 0), (1, 0, 0), 'west')
    north = C.Face((0, D / 2, 0), (-1, 0, 0), (0, -1, 0), 'north')
    east = C.Face((W / 2, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    hs = (W / 2 - ACX) / 2; hw = (D / 2 - ACY) / 2
    # Flanking stone pavilions: the first bay beside the corner bay projects PAV_OUT on both street faces (v001 P1 6).
    sp = C.Face(south.o - south.n * PAV_OUT, south.t, south.n, 'south pavilion')
    wp = C.Face(west.o - west.n * PAV_OUT, west.t, west.n, 'west pavilion')
    elevation(sp, -hs, -hs + BAY, street=True, pavilion_end=(-hs + BAY, -1))
    elevation(south, -hs + BAY, hs, street=True)
    elevation(wp, hw - BAY, hw, street=True, pavilion_end=(hw - BAY, 1))
    elevation(west, -hw + T, hw - BAY, street=True)
    for f, u in ((sp, -hs + BAY / 2), (wp, hw - BAY / 2)):
        gable_dormer(f, u)
    elevation(north, -W / 2, W / 2, street=False)
    elevation(east, -D / 2 + T, D / 2 - T, street=False)
    for (qx, qy) in ((-W / 2 - .08, D / 2 + .08), (W / 2 + .08, D / 2 + .08), (W / 2 + .08, -D / 2 - .08)):
        C.box('Corner quoin', (qx, qy, (CORNICE + .40) / 2), (1.1, 1.1, CORNICE + .40), 'stone', 'corner posts', 0)
        C.box('Corner cornice block', (qx + (.14 if qx > 0 else -.14), qy + (.14 if qy > 0 else -.14), CORNICE - .36), (1.84, 1.84, .72), 'stone', 'corner posts', 0)
    corner_bay()
    drum_and_domes()


LIGHT_RIG = dict(key=(-46, -50, 52), fill=(50, -26, 38), rear=(-20, 50, 46), target=(0, 0, 14.0), gain=8.0)
