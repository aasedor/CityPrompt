"""The Spine climbing tower, authored from the locked catalogue views of climbing_wall_building / variant_2
(a mixed-use tower with a full-height sculpted climbing strip on its street front).

Read from the pixels (the top view governs the plan): a fifteen-storey tower on a downtown block about 52 m wide and
27 m deep, a double-height glazed retail base under thirteen floors of dark bronze glass curtain wall with bronze
vertical fins (wider-spaced on the street front, close fins and sunshade bars on the side faces), on a plaza between
two side streets (front, oblique, top). The street front (south) has a deep central notch: the left wing and the right
wing come forward, and in the notch stands the spine, a light warm-grey sculpted precast-concrete climbing strip about
7.4 m wide running from the plaza to about six metres above the roof, its faces carved into vertical flakes and
ledges with sparse holds (front, oblique, top). West of the spine the notch is dark recessed glazing; east of it six
rest-station balconies with copper-faced slab edges, timber soffits and steel railings span from the spine to the
right wing and step a little past the wing's face, at the first, third, fifth, seventh, ninth and twelfth tower floors
(front, oblique, top). The roof of the street half is a U-shaped terrace inside a light coped parapet, paved, with
planting beds and large sculptural granite boulders on three sides; behind it a one-storey glazed amenity block with
bronze fins rises over the north part of the roof, its white roof carrying condensers, air handlers and ducts (front,
oblique, top). At the base a white canopy runs in front of the west wing's shopfronts; at the foot of the spine a
boulder garden of curved planters with granite boulders and grasses spreads into the plaza, with a second planter to
the east, street-tree pits and lamp posts along the sidewalk (front, oblique, top). Tan brick walk-ups face it across
the west street, a white mid-rise and glass towers stand to the north and east (front, oblique, top).
"""
import math
import random
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-climbing-spine'
X0, X1, Y0, Y1 = -26.0, 26.0, -13.5, 13.5            # tower plan: 52 m street front (south), 27 m deep (top view, fitted)
T = .30                                               # curtain-wall carrier (spandrel) depth
BASE = 8.0                                            # double-height retail base
FH, NF = 3.8, 13                                      # tower floor pitch and count above the base
ROOF = BASE + FH * NF                                 # 57.4: terrace roof slab top
PARA = ROOF + 1.1                                     # parapet coping top
SPAN = .75                                            # spandrel band under each floor's vision glass
NOTCH = (-6.7, 11.5)                                  # street-front notch (x), back face at YN
YN = Y0 + 3.5
SPX = (-1.4, 6.0)                                     # the spine's core (x); front face at SPY0, runs past the notch back to SPY1
SPY0, SPY1 = YN - 2.4, YN + 3.6                     # v002: SPY0 is the straight outer face; relief is carved inward
SPTOP = ROOF + 5.7                                    # spine cap (fitted to front, oblique and top)
BAL_FLOORS = (1, 3, 5, 7, 9, 11)                      # rest-station balconies (v008: storeys counted over the base on the source front and oblique)
BAL_X1, BAL_Y = NOTCH[1] + 1.8, Y0 - 1.2              # balcony east end (v008: steps 1.8 m past the notch) and front edge (2.3 m past the spine)
RB = (-18.1, 16.0, -3.8, Y1)                          # glazed amenity block over the north of the roof (fitted)
RBTOP = ROOF + 8.4                                     # v004: the crown clears the spine cap by ~2.7 m
CANOPY = (X0 + .4, SPX[0] - .02, Y0 - 4.4, BASE + .25)  # west-wing shopfront canopy (v005: ~4 m deep): x0, x1, front y, top z
CURB = Y0 - 16.0                                      # plaza and sidewalk to the south curb
SIDE = 4.5                                            # side sidewalks
EPS = .002
FLOORS = [BASE + FH * i for i in range(NF)]
PALETTE = dict(glass=(.13, .10, .075), spandrel=(.10, .085, .07), bronze=(.50, .34, .17), frame=(.20, .16, .12),
    rock=(.98, .67, .38), rock2=(.55, .37, .22), hold=(.46, .42, .38), hold2=(.58, .53, .47), concrete=(.82, .80, .78), coping=(.88, .87, .84),
    canopy=(.90, .89, .86), stone=(.70, .68, .64), copper=(.70, .32, .15), timber=(.62, .45, .28), hardware=(.18, .18, .19),
    steel=(.55, .55, .55), interior=(.80, .76, .68), floor=(.48, .43, .36), core=(.66, .64, .60), roof=(.86, .86, .84),
    membrane=(.80, .80, .78), metal=(.52, .53, .54), duct=(.60, .61, .62), granite=(.58, .55, .49), granite2=(.52, .49, .44), granite3=(.64, .61, .55),
    paver=(.78, .76, .71), paver2=(.70, .68, .63), kerb=(.76, .75, .72), asphalt=(.25, .25, .26), line=(.86, .85, .80),
    mulch=(.26, .20, .14), brick=(.62, .44, .30), brick2=(.52, .30, .22), tan=(.74, .62, .46), white=(.84, .83, .80),
    ctxglass=(.36, .44, .50), lamp=(.22, .22, .23), tree=(.24, .38, .16), tree2=(.30, .44, .19), bark=(.30, .23, .16))


def manifest(version):
    h = RBTOP
    cams = G.camera_roster(X1 - X0 + 6.0, Y1 - Y0 + 12.0, h, [
        ('boulder_garden', (13.0, -36.0, 6.5), (1.5, -17.0, 1.2), 28),               # spine foot, boulders and curved planters
        ('rest_balconies', (30.0, -50.0, 30.0), (9.0, Y0, 31.0), 50),           # the balcony stack against the spine
        ('roof_terrace', (-38.0, -34.0, 76.0), (-9.0, -5.0, ROOF + 1.5), 32),        # U terrace, beds and boulders
        ('retail_base', (-12.5, -26.6, 3.2), (-16.0, Y0, 4.4), 28),               # from the plaza, inside the tree and lamp line: canopy and shopfronts
        ('facade_close', (-16.5, -50.0, 30.0), (-16.5, Y0, 30.0), 42),               # one curtain-wall bay through several floors
        ('architecture_close', (10.0, -27.0, 22.0), (2.3, SPY0, 24.0), 32),           # carved spine faces and holds
        ('glass_close', (19.0, -24.0, 21.0), (19.0, Y0, 21.5), 34),                  # vision glass, fins and transoms
        ('interior', (-23.0, Y0 + 1.6, FLOORS[5] + 1.7), (-11.0, Y0 + 6.0, FLOORS[5] + 1.6), 18),
        ('rooftop_plant', (32.0, 26.0, 88.0), (-1.0, 4.0, RBTOP - 7.0), 30),                # amenity block roof and plant
        ('east_facade', (44.0, -30.0, 30.0), (X1, 0.0, 30.0), 24)])
    for c in cams:                       # the locked front, oblique and top (fitted to the sources)
        if c['name'] == 'front':
            c.update(location=(68.7, -134.3, 55.0), target=(-3.1, -.8, 28.7), lens=50.1, whole=False)
        elif c['name'] == 'front_corner':
            c.update(location=(81.8, -171.9, 127.5), target=(-22.6, 36.9, 6.8), lens=68.6, whole=False)
        elif c['name'] == 'top':
            c.pop('ortho_scale', None)
            c.update(location=(-.4, -66.0, 279.2), target=(-.6, -21.7, 111.4), lens=98.0, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(70.0, -95.0, 120.0), target=(0.0, -2.0, 25.0), lens=34.0, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(62.0, 78.0, 110.0), target=(0.0, 0.0, 28.0), lens=34.0, whole=False)
        elif c['name'] == 'right_side':                                  # over the low white block across the east street, south of the glass tower
            c.update(location=(88.0, -14.0, 80.0), target=(X1, 0.0, 33.0), lens=20, whole=False)   # amenity roof and spine cap ~10% under the top edge
        elif c['name'] == 'left_side':                                   # over the walk-ups across the west street
            c.update(location=(-82.0, 2.0, 78.0), target=(X0, 0.0, 34.0), lens=20, whole=False)
        elif c['name'] == 'rear':                                        # over the white mid-rise to the north
            c.update(location=(8.0, 74.0, 112.0), target=(0.0, Y1, 27.0), lens=21, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='climbing_wall_building/variant_2 (The Spine: bronze glass tower with a full-height sculpted climbing strip)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=15, storey_programme='double-height retail base, thirteen floors of offices and apartments, a glazed roof amenity storey',
            plan='52 m by 27 m tower (top view, fitted to all three views) with an 18.2 m wide, 3.5 m deep notch in the street front holding the 7.4 m climbing spine',
            facade='dark bronze glass curtain wall: vision glass over dark spandrels, bronze fins at 1.9 m on the street and rear faces, fins at 1.0 m with sunshade bars on the side faces',
            spine='light warm-grey sculpted precast climbing strip from the plaza to 5.7 m above the roof, carved into vertical flakes and ledges with holds; six rest-station balconies on its east side',
            base='double-height retail base: white canopy over the west shopfronts, glazed lobby and shops east of the spine',
            roof='U-shaped paved terrace with planting beds and granite boulders inside a coped parapet; a glazed amenity block with plant on its roof over the north half',
            streetscape='plaza with a boulder garden at the spine foot, a second planter, street-tree pits and lamp posts; side streets west and east, a street in front',
            levels_m=[BASE] + FLOORS[1:] + [ROOF], roof_m=dict(terrace=ROOF, parapet=PARA, spine=SPTOP, amenity_roof=RBTOP),
            inferred='interiors, the north face and the north half of the side faces follow the visible grammar; the catalogue text says 20-35 storeys, the pixels show fifteen; metric dimensions are authored teaching assumptions'),
        roof_contract=dict(type='flat terrace roof inside a coped parapet; glazed amenity block with a flat plant roof', datum_m=ROOF, crowns_m=[PARA, SPTOP, RBTOP]),
        identity_contract=dict(owner='bronze glass tower with a full-height sculpted concrete climbing spine in a street-front notch, stacked rest-station balconies and a boulder roof terrace'),
        material_contract=dict(profile='source-palette clay: dark bronze glass and fins, light warm-grey sculpted concrete, copper and timber balcony edges, white canopy and coping, granite boulders, grey pavers', textured_keeper=False),
        programme_contract=dict(storeys=15, ground='shops and the climbing gym lobby', upper='offices and apartments', roof='terrace and amenity room'),
        contact_contract=['Grade-zero plaza, sidewalks and streets', 'Tower, spine and canopy from grade', 'Balconies carried by the spine, the notch wall and the east wing', 'Terrace, boulders and beds on the roof slab inside the parapet'],
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
# Kit v003: canopy leaves are curved, tapered ovate cards whose custom normals lean toward the canopy normal (so a shrub
# shades as one leafy mass, not as chips); shrubs and hydrangea bodies are irregular multi-lobe hulls (bays, a wide low
# base, stems at the foot, sprigs breaking the outline); open branched racemes for panicles; needle-leaf lavender with
# whorled spikes in a vase-shaped fan; leaf-skinned lumpy bedding cushions; wall climbers built from instanced leafy and
# flowering sprays (three-bract clusters) over a hidden dark carrier, with trailing canes and a woody armature; pots and
# opposing near-coincident shell faces are audited with the clearance rule (audit() must be 0).
# Kit v003.1: canopy clearance is measured from each prototype's delivered plan extent (scale and lean included), so no
# canopy may cross a kerb's inner line.
import random as _pkr
import numpy as _pknp
import shapely as _pksh
from shapely.geometry import Polygon as _PkPolygon

PK_SINK = .025                                  # every plant base and carpet edge dives this far below the soil top
PK_CLEAR = .05                                  # clearance between a plant's buried base and a kerb's inner edge or a rail
PK_CANOPY_CLEAR = .03                           # a delivered canopy's plan extent stays this far inside the kerb's inner line
PK_PALETTE = dict(
    pk_leaf=(.21, .37, .14), pk_leaf2=(.31, .47, .19), pk_leaf_dark=(.13, .26, .10), pk_leaf_light=(.40, .55, .22),
    pk_leaf_silver=(.36, .44, .37), pk_leaf_red=(.38, .14, .15), pk_leaf_hairy=(.17, .29, .11), pk_lav_leaf=(.25, .31, .22),
    pk_groundcover=(.17, .30, .11), pk_shrub_core=(.15, .25, .10),
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
    """Vertex/face accumulator for one role of a prototype; `flat` lists face indices to flat-shade (buried caps); `n`
    holds optional per-vertex custom normals (None = the mesh's own smooth normal). A role that carries custom normals is
    stored as triangles only, so the build's triangulate pass and the glTF round trip keep them exactly."""
    def __init__(self):
        self.v = []; self.f = []; self.flat = []; self.n = None

    def add(self, vs, fs, flat=(), ns=None):
        o = len(self.v); b = len(self.f)
        if ns is not None and self.n is None:
            self.n = [None] * o
        self.v.extend(vs); self.f.extend(tuple(o + i for i in face) for face in fs); self.flat.extend(b + i for i in flat)
        if self.n is not None:
            self.n.extend(ns if ns is not None else [None] * len(vs))

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


def _pk_speck(g, c, n, r, a0=0., ns=None):
    """Tiny smooth 3-sided cap (4 vertices, 3 triangles) standing r x 1.1 proud of c along the normal n: the cheapest
    readable fleck for micro-florets, bracts and leaf grain. ns (unit) gives all four vertices that custom normal."""
    rot = _pk_tilt(n); vs = [(0., 0., r * 1.1)] + [(r * math.cos(a0 + 2.0944 * j), r * math.sin(a0 + 2.0944 * j), 0.) for j in range(3)]
    g.add([tuple(c[k] + (_pk_rot(p, *rot) if rot else p)[k] for k in range(3)) for p in vs], [(0, 1, 2), (0, 2, 3), (0, 3, 1)],
          ns=None if ns is None else [ns] * 4)


def _pk_ovate(g, base, d, cn, L, W, cup=.10, droop=.10, bend=None, lean=.72):
    """Curved, tapered ovate leaf card (6 vertices, 4 triangles): widest near 30% of its length, a rounded shoulder at
    66%, a pointed tip; the edges cup back and the tip droops along -cn. Its custom normals lean `lean` of the way from
    the card normal cn toward `bend` (the canopy normal at the leaf), with a slight cross-leaf roll, so a mass of leaves
    shades as one soft canopy instead of a heap of flat chips. Faces always wind toward cn."""
    side = _pk_norm(_pk_cross(d, cn))
    P = lambda q, s, z: tuple(base[k] + d[k] * L * q + side[k] * W * s + cn[k] * L * z for k in range(3))
    vs = [P(0., 0., 0.), P(.30, -.50, -cup * .5), P(.30, .50, -cup * .5), P(.66, -.36, -cup * .3 - droop * .45),
          P(.66, .36, -cup * .3 - droop * .45), P(1., 0., -droop)]
    b = _pk_norm(tuple(cn[k] * (1 - lean) + (bend or cn)[k] * lean for k in range(3)))
    nl = _pk_norm(tuple(b[k] - side[k] * .22 for k in range(3))); nr = _pk_norm(tuple(b[k] + side[k] * .22 for k in range(3)))
    g.add(vs, [(0, 2, 1), (1, 2, 4), (1, 4, 3), (3, 4, 5)], ns=[b, nl, nr, nl, nr, b])


def _pk_tangent(nrm, rnd):
    """A random unit vector perpendicular to nrm."""
    j = _pk_norm((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1)))
    dt = sum(j[i] * nrm[i] for i in range(3))
    return _pk_norm(tuple(j[k] - nrm[k] * dt for k in range(3)))


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


def _pk_panicle(g, base, axis, length, r0, rnd, branches=None):
    """Open branched raceme (astilbe, panicle hydrangea, white phlox, persicaria): a slender rachis nodding near its tip,
    8-14 side branches that shorten toward the tip and rise 35-60 degrees, each carrying 6-12 tiny floret specks
    (r 6-10 mm) with visible air between branches, and a fine tuft of florets at the tip; r0 is the half-width of the
    widest (lowest) branch tier. Feathery in outline, never a solid cone."""
    br = branches or rnd.randint(9, 13); up = axis
    side0 = _pk_tangent(up, rnd); nod = math.radians(rnd.uniform(14, 28))
    pts = []; p = tuple(base)
    for i in range(7):                                           # rachis: straight below, nodding over the top third
        q = i / 6; ang = nod * max(0., (q - .55) / .45) ** 1.5
        dr = _pk_norm(tuple(up[k] * math.cos(ang) + side0[k] * math.sin(ang) for k in range(3)))
        if i:
            p = tuple(p[k] + dr[k] * length / 6 for k in range(3))
        pts.append(p)
    _pk_tube(g, pts, .0032, .0015, 3)
    def at(q):
        f = q * 6; i = min(5, int(f)); w = f - i
        return tuple(pts[i][k] * (1 - w) + pts[i + 1][k] * w for k in range(3))
    for b in range(br):
        q = .06 + .80 * b / (br - 1); p0 = at(q); a = b * 2.39996 + rnd.uniform(-.25, .25)
        t = _pk_norm(_pk_rot(side0, up, a)); el = math.radians(rnd.uniform(35, 60))
        d = _pk_norm(tuple(up[k] * math.sin(el) + t[k] * math.cos(el) for k in range(3)))
        Lb = (r0 * (1 - q) ** .8 + .012) * rnd.uniform(.8, 1.1)
        p1 = tuple(p0[k] + d[k] * Lb for k in range(3))
        _pk_tube(g, [p0, p1], .0016, .001, 3)
        m = max(5, min(9, int(Lb / .009)))
        for j in range(m):
            s = .2 + .8 * j / (m - 1); fr = rnd.uniform(.006, .009)
            c = tuple(p0[k] + d[k] * Lb * s + rnd.uniform(-.006, .006) for k in range(3))
            _pk_speck(g, c, _pk_norm((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1) + .6)), fr, rnd.uniform(0, 6.3))
    tip = pts[-1]
    for j in range(5):                                           # tip tuft
        c = tuple(tip[k] + rnd.uniform(-.012, .012) for k in range(3))
        _pk_speck(g, c, _pk_norm((rnd.gauss(0, 1), rnd.gauss(0, 1), 1.)), rnd.uniform(.006, .008), rnd.uniform(0, 6.3))
    for j in range(6):                                           # florets along the rachis between branches
        c = at(rnd.uniform(.1, .95)); c = tuple(c[k] + rnd.uniform(-.006, .006) for k in range(3))
        _pk_speck(g, c, _pk_norm((rnd.gauss(0, 1), rnd.gauss(0, 1), .5)), rnd.uniform(.005, .007), rnd.uniform(0, 6.3))


class PlantKit:
    """Prototype registry, clearance checker and placer. proto() turns {role: PkGeo} into one shared mesh datablock per
    role and measures its buried base radius (`base_r`: vertices below kerb height) and canopy radius; place() puts a
    prototype at (x, y, z) with spin, non-uniform scale and lean, as linked instances (instancing=True: glTF reuses the
    mesh, ~0.6 KB per node) or merged into per-role batches (instancing=False). fits()/place_in() apply the kit-wide
    clearance rule: a plant's base stays PK_CLEAR inside every registered bed edge and clear of every obstacle, and its
    delivered canopy (extent(): the prototype's plan radius after the placement's non-uniform scale and lean) stays
    PK_CANOPY_CLEAR inside the kerb's inner line and clear of any tall obstacle (a rail or wall). audit() re-checks every
    delivered placement with the same rule (must be 0). Call flush() once after planting."""
    def __init__(self, module='planting', instancing=True, kerb_h=.045):
        self.module = module; self.instancing = instancing; self.batch = {}; self.placed = 0; self.nodes = 0
        self.unique_triangles = 0; self.counts = {}; self.kerb_h = kerb_h; self.beds = []; self.obstacles = []
        self.placements = []; self.rejected = 0; self.flushed = False

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
            if g.n is not None:                          # custom normals: triangles only (kept exactly by triangulate + glTF),
                fs = []; fl = []; flat0 = set(g.flat)    # each wound to face its custom normals (Cycles shades a back face
                for i, f in enumerate(g.f):              # with its normal flipped, which renders a leaf black)
                    for k in range(1, len(f) - 1):
                        if i in flat0:
                            fl.append(len(fs))
                        tri = (f[0], f[k], f[k + 1]); cs = [g.n[j] for j in tri if g.n[j] is not None]
                        if cs:
                            a, b, c = (g.v[j] for j in tri)
                            gn = _pk_cross(tuple(b[q] - a[q] for q in range(3)), tuple(c[q] - a[q] for q in range(3)))
                            if sum(gn[q] * sum(n[q] for n in cs) for q in range(3)) < 0:
                                tri = (tri[0], tri[2], tri[1])
                        fs.append(tri)
                g.f = fs; g.flat = fl
            me.from_pydata(g.v, [], g.f)
            if g.n is None:
                C.normalise(me)
            flat = set(g.flat)
            for p in me.polygons:
                p.use_smooth = p.index not in flat
            if g.n is not None:
                auto = [v.normal.copy() for v in me.vertices]
                me.normals_split_custom_set_from_vertices([n if n is not None else tuple(auto[i]) for i, n in enumerate(g.n)])
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

    @staticmethod
    def extent(p, s=1., sy=None, sz=None, lean=(0., 0.)):
        """Delivered plan radius of prototype p about its placement origin: the largest horizontal vertex radius times
        the larger plan scale, plus the horizontal throw of its top under the lean."""
        sy = s if sy is None else sy; sz = s if sz is None else sz
        return p['canopy_r'] * max(s, sy) + p['height'] * sz * math.sin(min(abs(lean[0]) + abs(lean[1]), 1.2))

    def _breaks(self, p, x, y, s, sy, sz, lean, clear, region=None):
        """The clearance rule shared by fits() and audit(): None when the placement is clean, else the reason."""
        pt = _pksh.points(x, y); br = p['base_r'] * max(s, s if sy is None else sy) + clear
        cr = self.extent(p, s, sy, sz, lean) + PK_CANOPY_CLEAR
        for reg in ([region] if region is not None else []) + self.beds:
            inside = _pksh.contains_xy(reg, x, y)
            if reg is region and not inside:
                return 'outside its bed'
            if inside:
                d = reg.boundary.distance(pt)
                if d < br:
                    return 'base crosses kerb'
                if d < cr:
                    return 'canopy crosses kerb'
        for geom, top in self.obstacles:
            d = geom.distance(pt)
            if d < br:
                return 'base on obstacle'
            if top > .3 and d < cr:
                return 'canopy in tall obstacle'
        return None

    def fits(self, p, x, y, s=1., region=None, clear=PK_CLEAR, sy=None, sz=None, lean=(0., 0.)):
        return self._breaks(p, x, y, s, sy, sz, lean, clear, region) is None

    def place_in(self, p, x, y, z, rot=0., s=1., region=None, shrink=(1., .85, .72), aspect=1., **kw):
        """Place p at (x, y) with scale s (y scale s x aspect) if it fits, trying the given shrink factors, else skip it;
        returns the scale used or 0."""
        for f in shrink:
            if self.fits(p, x, y, s * f, region, sy=s * f * aspect, sz=kw.get('sz'), lean=kw.get('lean', (0., 0.))):
                self.place(p, x, y, z, rot, s * f, sy=s * f * aspect, **kw)
                return s * f
        self.rejected += 1
        return 0.

    def place(self, p, x, y, z, rot=0., s=1., sz=None, sy=None, lean=(0., 0.), instance=None, track=True):
        """track=False for parts of a wall climber (sprays, trailing canes), which belong on their wall and are not
        ground plants; everything else is checked by audit()."""
        inst = self.instancing if instance is None else instance
        sz = s if sz is None else sz; sy = s if sy is None else sy
        self.placed += 1; self.counts[p['name']] = self.counts.get(p['name'], 0) + 1
        if track:
            self.placements.append((x, y, s, sy, sz, lean, p))
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
        """Placements whose buried base crosses a registered bed edge or obstacle, or whose canopy enters a tall one;
        pots (protos with a rim radius) closer than their two rims plus 3 cm; and pairs of shell faces (carpets,
        carriers) from different meshes that lie within 2 mm of each other with opposing or coincident normals (the
        black-slit and z-fighting signature; see shell_faces()). The count, or with detail=True the offending items."""
        bad = []
        for x, y, s, sy, sz, lean, p in self.placements:
            why = self._breaks(p, x, y, s, sy, sz, lean, 0.)
            if why:
                bad.append((p['name'], why, round(x, 2), round(y, 2)))
        pots = [(x, y, p['rim_r'] * max(s, sy), p['name']) for x, y, s, sy, sz, lean, p in self.placements if p.get('rim_r')]
        for i in range(len(pots)):
            for j in range(i):
                (x1, y1, r1, n1), (x2, y2, r2, n2) = pots[i], pots[j]
                if math.hypot(x1 - x2, y1 - y2) < r1 + r2 + .03:
                    bad.append(('pots overlap', n1, n2, round(x1, 2), round(y1, 2)))
        bad.extend(self.shell_faces())
        return bad if detail else len(bad)

    def shell_faces(self, tol=.002):
        """Opposing (dot < -0.5) or coincident (dot > 0.9) faces of two different registered shell meshes (pk_mesh(...,
        shell=True): carpets, bands, groundcover, climber carriers) whose centroids lie within tol of each other. Cached
        once computed after flush()."""
        if getattr(self, '_shell_bad', None) is not None:
            return self._shell_bad
        from mathutils import kdtree, Vector
        objs = [o for o in _PK_SHELLS if o.name in C.bpy.data.objects]
        items = []
        for k, o in enumerate(objs):
            mw = o.matrix_world
            for p in o.data.polygons:
                items.append((k, mw @ p.center, (mw.to_3x3() @ p.normal).normalized()))
        bad = []
        if items:
            kd = kdtree.KDTree(len(items))
            for i, (k, c, n) in enumerate(items):
                kd.insert(c, i)
            kd.balance()
            seen = set()
            for i, (k, c, n) in enumerate(items):
                for _, j, dist in kd.find_range(c, tol):
                    kj, cj, nj = items[j]
                    if kj == k or (kj, k) in seen:
                        continue
                    dt = n.dot(nj)
                    if dt < -.5 or dt > .9:
                        seen.add((k, kj)); bad.append(('shell faces', objs[k].name, objs[kj].name, round(dist, 4)))
        if self.flushed:
            self._shell_bad = bad
        return bad

    def flush(self):
        for role, (V, F, FL) in self.batch.items():
            if F:
                pk_mesh(f'{self.module} merged {role}', V, F, FL, role, self.module)
        self.batch = {}; self.flushed = True
        C.MODULES.setdefault(self.module, []).append(dict(planting_kit=True, instancing=self.instancing, plants=self.placed,
            instance_nodes=self.nodes, prototypes=self.counts, clearance_violations=self.audit(), rejected=self.rejected))

    def stats(self):
        return dict(instancing=self.instancing, plants=self.placed, instance_nodes=self.nodes, prototypes=len(self.counts),
                    prototype_triangles=self.unique_triangles, clearance_violations=self.audit(), rejected=self.rejected)


_PK_SHELLS = []                                  # carpets, bands and climber carriers checked by PlantKit.shell_faces()


def pk_mesh(name, V, F, flat, role, module, shell=False):
    """C.mesh with smooth shading on every face not listed in `flat`; shell=True registers it for the kit's
    near-coincident face audit."""
    o = C.mesh(name, V, F, role, module)
    fl = set(flat)
    for p in o.data.polygons:
        p.use_smooth = p.index not in fl
    if shell:
        _PK_SHELLS.append(o)
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


def groundcover(name, poly, z, kerb=.15, height=.06, bump=.012, wave=.45, grid=.2, ramp=.08, role='pk_groundcover', seed=1,
                module='planting', dots=None, grain=None, edge=.08):
    """Low continuous carpet (thyme, sedum, vinca, ajuga) over a bed outline minus the kerb (lapped 1.5 cm under the kerb,
    its rim held below the kerb's inner arris by the 8 cm shoulder, so the visible kerb width never wobbles): a softly
    cushioned heightfield with a clean clipped rim, grounded and leaving no bare fill between
    larger plants. dots=(roles, per_m2, radius[, seed]) adds merged floret specks; grain=(roles, per_m2, radius) adds
    merged leaf-rosette specks for leaf texture at eye level. Returns (object, hz)."""
    reg = pk_region(poly, kerb - .015) if kerb else pk_region(poly)
    V, F, hz = _pk_field(reg, z, height, bump, wave, grid, ramp, seed, edge)
    o = pk_mesh(name, V, F, (), role, module, shell=True)
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
    o = pk_mesh(name, V, F, (), role, module, shell=True)
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
      'panicle' astilbe / panicle hydrangea / phlox: open branched raceme of tiny florets with a nodding tip;
      'mophead' hydrangea: 7-9 heads, each a smooth dome under nine smooth floret-cluster domes (a fine lumpy outline,
                never creased or flaky; head_role2 = their role, default head_role), seated into and collared by the
                leaves of its own broad low domed body (3-4 lobes round a centre, h:w about 0.75) of large ovate leaves
                that splay out and droop to the soil at the skirt.
    Heights are metres above the soil; place it with kit.place() or kit.place_in()."""
    rnd = _pkr.Random(seed); stem_role = stem_role or leaf_role
    parts = _pk_parts(leaf_role, stem_role, head_role, *([head_role2] if head_role2 else []),
                      *([boss_role] if head in ('daisy', 'cup') else []))
    if head == 'mophead':
        core = parts.setdefault('pk_shrub_core', PkGeo()); F = foliage; L = .12 * size; lift = .06
        fh = height * .70 - L * .9                                 # hull top; leaves and seated heads make up the rest
        hull = [((0., 0., lift + (fh - lift) * .42), (F * .60, F * .56, (fh - lift) * .42))]
        a0 = rnd.uniform(0, 2 * math.pi); nl = 3 + seed % 2
        for k in range(nl):                                         # 3-4 broad low lobes round the centre (a domed mound)
            a = a0 + 2 * math.pi * k / nl + rnd.uniform(-.35, .35); rr = F * rnd.uniform(.44, .54); rz = rr * rnd.uniform(.58, .70)
            d = max(0., F - rr * 1.05 - L * .4); cz = lift + rz + (fh - lift - 2 * rz) * rnd.uniform(0., .35)
            hull.append(((d * math.cos(a), d * math.sin(a), cz), (rr, rr * rnd.uniform(.85, 1.), rz)))
        rz = (fh - lift) * .32
        hull.append(((rnd.uniform(-.06, .06), rnd.uniform(-.06, .06), fh - rz), (F * .52, F * .48, rz)))
        for c, r in hull:
            _pk_ball(core, c, r, seed=rnd.randrange(1 << 20), bump=min(r) * .1, wave=min(r) * 1.5, seg=12, rings=7)
        _pk_canopy(parts[leaf_role], parts[leaf_role], core, hull, leaves * 14, L, fh, rnd, off=(.03, .05), sprigs=.0, skirt=.42)
        dome = parts[head_role2 or head_role]
        for k in range(heads):                                      # heads seated into the leaf layer, collared by leaves
            a = k * 2.39996 + rnd.uniform(-.3, .3); d = F * .70 * math.sqrt((k + .5) / heads)
            x, y = d * math.cos(a), d * math.sin(a); zt = _pk_hull_top(hull, x, y)
            if zt is None:
                continue
            hr = .12 * size * rnd.uniform(.88, 1.12); c = (x, y, zt + .04 + hr * .25)
            _pk_ball(dome, c, (hr * .8, hr * .8, hr * .7), seg=9, rings=5)
            for j in range(9):                                      # floret clusters: a fine, smooth lumpy (never creased) outline
                q = 0 if j < 6 else 1; aj = j * (1.0472 if q == 0 else 2.0944) + a + q * .5
                u = _pk_norm((math.cos(aj), math.sin(aj), .35 if q == 0 else 1.3)); sr = hr * rnd.uniform(.36, .42)
                _pk_ball(dome, (c[0] + hr * .62 * u[0], c[1] + hr * .62 * u[1], c[2] + hr * .55 * u[2]), (sr, sr, sr * .85), seg=7, rings=4)
            for j in range(5):                                      # leaf collar under the head
                aj = a + j * 1.2566 + rnd.uniform(-.2, .2); dd = _pk_norm((math.cos(aj), math.sin(aj), -.25))
                b0 = (c[0] + dd[0] * hr * .3, c[1] + dd[1] * hr * .3, c[2] - hr * .45)
                _pk_ovate(parts[leaf_role], b0, dd, _pk_norm((-dd[0] * .3, -dd[1] * .3, 1.)), L * 1.05, L * .6,
                          bend=_pk_norm((dd[0] * .4, dd[1] * .4, 1.)))
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
            _pk_panicle(parts[head_role], (top[0], top[1], top[2] - .01), lean, .26 * size * rnd.uniform(.85, 1.15),
                        .075 * size, rnd)
        else:
            _pk_corymb(parts[head_role if k % 3 or not head_role2 else head_role2], (top[0], top[1], top[2] + .004),
                       .05 * size * rnd.uniform(.85, 1.15), rnd)
    return kit.proto(name, parts)


def lavender(kit, name, radius=.30, height=.52, spikes=34, leaf_role='pk_lav_leaf', head_role='pk_lavender', seed=1):
    """Lavender / catmint / perovskia as a kit prototype, with no solid dome: 40-48 short leafy stems rising steeply
    from the crown, each clothed in narrow grey-sage needle leaves (custom normals leaning to a low hemisphere, so the
    loose mass shades as a soft mound and the soil shows at its edge), under a vase-shaped upright fan of thin flower
    stems (within about 25 degrees of vertical) carrying spikes of 6-9 tiny paired whorls that taper to the tip."""
    rnd = _pkr.Random(seed); parts = _pk_parts(leaf_role, head_role); g = parts[leaf_role]; gh = parts[head_role]
    fh = height * .40; ctr = (0., 0., -fh * .35)
    for k in range(rnd.randint(40, 48)):                         # leafy stems and needle leaves
        phi = k * 2.39996 + rnd.uniform(-.3, .3); q = rnd.random() ** .7
        tilt = math.radians(10 + 50 * q); Ls = fh * rnd.uniform(.75, 1.1) * (1 - .25 * q)
        b0 = (radius * .12 * q * math.cos(phi), radius * .12 * q * math.sin(phi), -PK_SINK)
        d = (math.sin(tilt) * math.cos(phi), math.sin(tilt) * math.sin(phi), math.cos(tilt))
        top = tuple(b0[i] + d[i] * Ls for i in range(3))
        _pk_tube(g, [b0, top], .0035, .002, 3)
        for j in range(rnd.randint(8, 11)):
            s = .2 + .8 * j / 10; p = tuple(b0[i] + d[i] * Ls * s for i in range(3))
            if p[2] < .02:
                continue
            a = phi + j * 2.2 + rnd.uniform(-.4, .4)
            dn = _pk_norm((math.cos(a) * .9 + d[0] * .5, math.sin(a) * .9 + d[1] * .5, .55 + rnd.uniform(-.2, .2)))
            mn = _pk_norm(tuple(p[i] - ctr[i] for i in range(3)))
            cn = _pk_norm(tuple(mn[i] - sum(mn[q_] * dn[q_] for q_ in range(3)) * dn[i] for i in range(3)))
            _pk_ovate(g, p, dn, cn, rnd.uniform(.04, .055), .012, cup=.05, droop=.05, bend=mn, lean=.8)
    for k in range(spikes):                                      # vase-shaped fan of flower stems with whorled spikes
        phi = k * 2.39996 + rnd.uniform(-.3, .3); q = (k + .5) / spikes
        tilt = math.radians(25 * math.sqrt(q) + rnd.uniform(-4, 4)); H = height * rnd.uniform(.88, 1.06) * (1 - .12 * q)
        b0 = (radius * .1 * math.cos(phi), radius * .1 * math.sin(phi), fh * .4)
        d = (math.sin(tilt) * math.cos(phi), math.sin(tilt) * math.sin(phi), math.cos(tilt))
        Ls = (H - b0[2]) / max(.6, d[2]); top = tuple(b0[i] + d[i] * Ls for i in range(3))
        mid = tuple((b0[i] + top[i]) / 2 + (d[i] * .01 if i < 2 else 0.) for i in range(3))
        _pk_tube(g, [b0, mid, top], .0022, .0016, 3)
        sl = .085 * rnd.uniform(.85, 1.2); nw = rnd.randint(6, 8); a = rnd.uniform(0, 6.3)
        side = _pk_norm(_pk_cross(d, (0., 0., 1.) if abs(d[2]) < .99 else (1., 0., 0.)))
        for j in range(nw):                                      # paired whorls, alternating 90 degrees, tapering
            s = j / (nw - 1); c = tuple(top[i] - d[i] * sl * (1 - s) for i in range(3)); r = .0062 * (1 - .45 * s)
            for m in range(2):
                aa = a + j * 1.5708 + m * math.pi
                o = _pk_rot(side, d, aa); cc = tuple(c[i] + o[i] * r * .55 for i in range(3))
                _pk_speck(gh, cc, _pk_norm(tuple(o[i] + d[i] * .4 for i in range(3))), r, rnd.uniform(0, 6.3))
        _pk_speck(gh, tuple(top[i] + d[i] * .008 for i in range(3)), d, .004, 0.)
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


def _pk_inside(p, hull, skip=-1, f=.97):
    """True when p lies inside any hull lobe other than `skip` (scaled radius f)."""
    return any(j != skip and sum(((p[k] - c[k]) / r[k]) ** 2 for k in range(3)) < f * f for j, (c, r) in enumerate(hull))


def _pk_hull_top(hull, x, y):
    """Height of the hull's upper surface above (x, y), or None outside every lobe."""
    best = None
    for c, r in hull:
        q = 1 - ((x - c[0]) / r[0]) ** 2 - ((y - c[1]) / r[1]) ** 2
        if q > 0:
            z = c[2] + r[2] * math.sqrt(q); best = z if best is None else max(best, z)
    return best


def _pk_shrub_hull(rnd, radius, height, lobes, lift, top_gap):
    """Irregular multi-lobe shrub hull: `lobes` flattened ellipsoid lobes round the axis in a ring of lobes + 2 slots with
    two slots left empty (concave bays in plan and elevation), lower lobes reaching out and upper ones drawn in (a wide,
    low-shouldered base; the two empty slots are adjacent, so one deep bay), one or two crown lobes and a central filler;
    the hull rises from `lift` above the soil (stems
    show below it) to height - top_gap (the leaf layer makes up the rest)."""
    hull = []; slots = lobes + 2; g0 = rnd.randrange(slots); gaps = {g0, (g0 + 1) % slots}; a0 = rnd.uniform(0, 2 * math.pi)
    H = height - top_gap - lift
    for k in [k for k in range(slots) if k not in gaps]:
        a = a0 + 2 * math.pi * k / slots + rnd.uniform(-.22, .22); up = rnd.random()
        rr = radius * rnd.uniform(.30, .55) * (1 - .25 * up); rz = min(rr * rnd.uniform(.6, .85), H * .42)
        d = max(0., radius - rr * rnd.uniform(.7, 1.4)) * (1 - .45 * up)
        cz = lift + rz + (H - 2 * rz) * up * rnd.uniform(.55, 1.)
        hull.append(((d * math.cos(a), d * math.sin(a), cz), (rr, rr * rnd.uniform(.78, 1.), rz)))
    nc = 1 if radius < .45 else 3; ac = rnd.uniform(0, 2 * math.pi)
    for k in range(nc):                                           # an uneven crown: lobes off-centre at different heights
        rr = radius * rnd.uniform(.30, .44) * (1.25 if nc == 1 else 1.); rz = min(rr * .8, H * .36)
        a = ac + 2 * math.pi * k / nc + rnd.uniform(-.4, .4); d = radius * (rnd.uniform(.05, .2) if nc == 1 else rnd.uniform(.22, .42))
        top = lift + H * (1. if k == 0 else rnd.uniform(.80, .92))
        hull.append(((d * math.cos(a), d * math.sin(a), top - rz), (rr, rr * rnd.uniform(.8, 1.), rz)))
    hull.append(((0., 0., lift + H * .42), (radius * .52, radius * .48, H * .36)))
    return hull


def _pk_canopy(gl, gd, gt, hull, n, leaf, height, rnd, light=.5, off=(.015, .035), sprigs=.2, floor=.015, skirt=0., under=0.):
    """Clothe a hull in n curved ovate leaves (_pk_ovate) based `off` m outside it and lifting 15-35 degrees off it, so
    the hull lies about 4 cm under the leaf surface and shows only as depth between leaves; a fraction `sprigs` of the leaves
    ride in threes on short twigs (gt, 6-14 cm) standing out of the canopy, breaking its outline; custom normals lean to
    the hull normal so the mass shades as one canopy. Leaves above `light` x height (with jitter) go to gl, others to gd.
    skirt > 0: below skirt x height the leaves splay outward and droop to the soil (hydrangea skirt). under > 0: that
    fraction of the leaves forms an inner layer of larger (1.5x) dark leaves lying nearly flat on the hull, so gaps in
    the outer layer show leaves in shade, never a smooth hull. No leaf tip goes below `floor`."""
    wts = [r[0] * r[1] + r[0] * r[2] + r[1] * r[2] for _, r in hull]; placed = 0; tries = 0; nu = int(n * under)
    while placed < n and tries < n * 8:
        tries += 1
        i = rnd.choices(range(len(hull)), wts)[0]; c, r = hull[i]
        u = _pk_norm((rnd.gauss(0, 1), rnd.gauss(0, 1), rnd.gauss(0, 1) * .9 + .15))
        p = tuple(c[k] + r[k] * u[k] for k in range(3))
        if _pk_inside(p, hull, i):
            continue
        nrm = _pk_norm(tuple(u[k] / r[k] for k in range(3)))
        g = gl if (p[2] / height + rnd.uniform(-.25, .25)) > light else gd
        L = leaf * rnd.uniform(.8, 1.2)
        if placed < nu:                                             # inner layer: big dark leaves flat on the hull
            t = _pk_tangent(nrm, rnd); d = _pk_norm(tuple(t[k] + nrm[k] * rnd.uniform(0., .2) for k in range(3)))
            base = tuple(p[k] + nrm[k] * rnd.uniform(.004, .012) for k in range(3))
            if base[2] + min(0., d[2]) * L * 1.5 < floor:
                continue
            cn = _pk_norm(tuple(nrm[k] - sum(nrm[q] * d[q] for q in range(3)) * d[k] for k in range(3)))
            _pk_ovate(gd, base, d, cn, L * 1.5, L * .85, cup=.06, droop=.04, bend=nrm, lean=.8)
            placed += 1
            continue
        if rnd.random() < sprigs:                                   # a twig standing out with three leaves at its tip
            t = _pk_tangent(nrm, rnd)
            dr = _pk_norm(tuple(nrm[k] + t[k] * .6 + (.15 if k == 2 else 0.) for k in range(3)))
            b0 = tuple(p[k] - nrm[k] * .02 for k in range(3)); tl = rnd.uniform(.06, .14) * min(1.4, leaf / .08)
            tip = tuple(p[k] + dr[k] * tl for k in range(3))
            if tip[2] < floor + L:
                continue
            _pk_tube(gt, [b0, tip], .006 * min(1.5, leaf / .08), .003, 3)
            for j in range(3):
                tj = _pk_tangent(dr, rnd)
                d = _pk_norm(tuple(dr[k] * .55 + tj[k] for k in range(3)))
                cn = _pk_norm(tuple(nrm[k] - sum(nrm[q] * d[q] for q in range(3)) * d[k] for k in range(3)))
                _pk_ovate(g, tip, d, cn, L * .9, L * .52, bend=nrm)
            placed += 3
            continue
        base = tuple(p[k] + nrm[k] * rnd.uniform(*off) for k in range(3))
        if skirt and p[2] < skirt * height:                        # skirt: splay out and droop toward the soil
            h = _pk_norm((nrm[0], nrm[1], 0.)); d = _pk_norm((h[0], h[1], -rnd.uniform(.35, .7)))
            L *= 1.15
        else:
            t = _pk_tangent(nrm, rnd); lift = math.tan(math.radians(rnd.uniform(15, 35)))
            d = _pk_norm(tuple(t[k] + nrm[k] * lift - (.12 if k == 2 else 0.) for k in range(3)))
        if base[2] + min(0., d[2]) * L < floor:
            continue
        cn = _pk_norm(tuple(nrm[k] - sum(nrm[q] * d[q] for q in range(3)) * d[k] for k in range(3)))
        _pk_ovate(g, base, d, cn, L, L * .55, bend=nrm)
        placed += 1
    return placed


def shrub_mass(kit, name, radius=.8, height=1.0, lobes=7, role='pk_leaf_dark', role2='pk_leaf', seed=1, leaves=None, leaf=None,
               core_role='pk_shrub_core', stems=4):
    """Grounded leafy shrub as a kit prototype (sizes 0.4-1.6 m). Structure first: an irregular multi-lobe hull
    (_pk_shrub_hull: flattened lobes, two bays, a wide low-shouldered base, crown lobes) in a mid-dark leaf green
    (core_role), lifted off the soil on `stems` visible stems, clothed by _pk_canopy in curved ovate leaves 3.5-6 cm
    outside it (role2 above, role below) with a fifth of them on twig sprigs breaking the outline, custom normals
    leaning to the hull normal. leaves defaults to about 460 per m2 of hull surface; leaf length scales with size."""
    rnd = _pkr.Random(seed); parts = _pk_parts(core_role, role, role2); g = parts[core_role]
    leaf = leaf or (.065 + .045 * min(1., height / 1.4)); lift = min(.16, height * .1)
    hull = _pk_shrub_hull(rnd, radius - leaf * .9, height, lobes, lift, leaf * 1.1)
    for c, r in hull:
        _pk_ball(g, c, r, seed=rnd.randrange(1 << 20), bump=min(r) * .22, wave=min(r) * .7, seg=10, rings=6)
    for k in range(stems):                                           # stems from the soil into the hull's underside
        a = 2 * math.pi * k / stems + rnd.uniform(-.4, .4); d = radius * rnd.uniform(.08, .2)
        top = (d * 1.8 * math.cos(a), d * 1.8 * math.sin(a), lift + height * .14)
        _pk_tube(g, [(d * math.cos(a) * .5, d * math.sin(a) * .5, -PK_SINK), ((d * .9 + d * .5) / 2 * math.cos(a), (d * .9 + d * .5) / 2 * math.sin(a), lift * .7), top],
                 .014 * min(1.6, radius / .5), .009 * min(1.6, radius / .5), 5)
    area = sum(4 * math.pi * ((r[0] * r[1]) ** 1.6 + (r[0] * r[2]) ** 1.6 + (r[1] * r[2]) ** 1.6) ** (1 / 1.6) / 3 ** (1 / 1.6)
               for _, r in hull) * .55
    _pk_canopy(parts[role2], parts[role], g, hull, leaves or int(min(1500, max(240, 460 * area * (.08 / leaf) ** 2))), leaf,
               height, rnd, off=(.02, .04), sprigs=.16, under=.35)
    return kit.proto(name, parts)


def bedding_cushion(kit, name, radius=.28, height=.13, role='pk_leaf_red', floret_role='pk_red', kind='begonia', seed=1,
                    leaf_role=None):
    """Low bedding plant (begonia, ageratum, alyssum, impatiens) as a kit prototype: a broad lumpy mound (h:w about
    0.25-0.35) of 6-8 low sub-mounds, clothed in small ovate leaves (3-5 cm, about 550 per m2, custom normals leaning to
    the mound) with flower clusters over 40-70% of its top in a soft noise mask: kind='begonia' clusters of 3-4 beads,
    'ageratum' fuzzy puffs, 'alyssum' a dense froth of tiny specks. Neighbouring cushions placed closer than their
    diameter merge into a continuous band. leaf_role defaults to role (the sub-mounds' colour)."""
    rnd = _pkr.Random(seed); leaf_role = leaf_role or role; parts = _pk_parts(role, leaf_role, floret_role)
    hb = height - .03; hull = [((0., 0., hb * .2), (radius * .62, radius * .58, hb * .8))]
    n = rnd.randint(5, 7); a0 = rnd.uniform(0, 6.3)
    for k in range(n):
        a = a0 + 2 * math.pi * k / n + rnd.uniform(-.3, .3); rr = radius * rnd.uniform(.34, .44); d = radius - rr * 1.1
        hull.append(((d * math.cos(a), d * math.sin(a), hb * .1), (rr, rr * rnd.uniform(.85, 1.), hb * rnd.uniform(.62, .85))))
    for c, r in hull:
        _pk_dome(parts[role], c, r, -PK_SINK, seed=rnd.randrange(1 << 20), bump=.006, wave=.1, seg=12, rings=5)
    area = math.pi * radius * radius * 1.35
    _pk_canopy(parts[leaf_role], parts[leaf_role], parts[role], hull, int(550 * area), .042, height, rnd, off=(.012, .022),
               sprigs=0., floor=.005)
    mask = _PkNoise(seed + 3, 2 * math.pi / (radius * 1.1)); gf = parts[floret_role]
    per = dict(begonia=300, ageratum=420, alyssum=620)[kind]
    for k in range(int(per * area)):
        i = rnd.choices(range(len(hull)), [r[0] * r[1] for _, r in hull])[0]; c, r = hull[i]
        u = _pk_norm((rnd.gauss(0, 1), rnd.gauss(0, 1), abs(rnd.gauss(0, 1)) + .5))
        p = tuple(c[q] + r[q] * u[q] for q in range(3))
        if p[2] < hb * .4 or _pk_inside(p, hull, i) or mask(p[0], p[1]) < -.5:
            continue
        nrm = _pk_norm(tuple(u[q] / r[q] for q in range(3))); p = tuple(p[q] + nrm[q] * .022 for q in range(3))
        if kind == 'begonia':
            for j in range(rnd.randint(3, 4)):
                o = _pk_tangent(nrm, rnd); fr = rnd.uniform(.008, .011)
                _pk_speck(gf, tuple(p[q] + o[q] * .012 for q in range(3)), _pk_norm(tuple(nrm[q] + o[q] * .6 for q in range(3))), fr,
                          rnd.uniform(0, 6.3), ns=nrm)
        elif kind == 'ageratum':
            for j in range(5):
                o = _pk_tangent(nrm, rnd); fr = rnd.uniform(.007, .01)
                _pk_speck(gf, tuple(p[q] + o[q] * .008 + nrm[q] * .003 * j for q in range(3)),
                          _pk_norm(tuple(nrm[q] + o[q] for q in range(3))), fr, rnd.uniform(0, 6.3), ns=nrm)
        else:
            for j in range(4):
                o = _pk_tangent(nrm, rnd); fr = rnd.uniform(.005, .007)
                _pk_speck(gf, tuple(p[q] + o[q] * .009 for q in range(3)), _pk_norm(tuple(nrm[q] + o[q] * .8 for q in range(3))), fr,
                          rnd.uniform(0, 6.3), ns=nrm)
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
    p = kit.proto(name, parts); p['rim_r'] = pot_r * 1.09            # pots are audited against each other by their rims
    return p


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
                    module=kit.module, grid=.28, edge=.12)
    for x, y in pk_scatter(poly, spacing, kerb=kerb, margin=PK_CLEAR, seed=seed):
        order = sorted(range(len(mix)), key=lambda i: -(fields[i](x, y) + 1.4 * math.log(mix[i][1])))
        for i in order:
            s = rnd.uniform(*scale); rot = rnd.uniform(0, 2 * math.pi); sy = s * rnd.uniform(.9, 1.1)
            sz = s * rnd.uniform(.88, 1.12); ln = (rnd.uniform(-lean, lean), rnd.uniform(-lean, lean))
            if kit.fits(mix[i][0], x, y, s, reg, sy=sy, sz=sz, lean=ln):
                kit.place(mix[i][0], x, y, z, rot, s, sy=sy, sz=sz, lean=ln)
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


def _pk_bract_triad(g, c, rnd, size, up=(0., 0., 1.)):
    """Three papery bracts (bougainvillea) round a tiny centre: broad cupped ovate cards rising out of c at 120 degrees,
    their custom normals leaning to `up` so a panicle of triads shades as one soft flower mass."""
    a0 = rnd.uniform(0, 6.3); side = _pk_tangent(up, rnd); side2 = _pk_cross(up, side)
    for m in range(3):
        aa = a0 + m * 2.0944 + rnd.uniform(-.2, .2)
        r = tuple(side[k] * math.cos(aa) + side2[k] * math.sin(aa) for k in range(3))
        d = _pk_norm(tuple(r[k] * .62 + up[k] * .78 for k in range(3)))
        cn = _pk_norm(tuple(r[k] * .78 - up[k] * .62 for k in range(3)))
        L = size * rnd.uniform(.85, 1.15)
        _pk_ovate(g, c, d, tuple(-x for x in cn), L, L * .78, cup=.16, droop=.04, bend=up, lean=.6)


def _pk_spray(kit, name, leaf_role, bract_role, rnd, clusters=0):
    """One climber spray in a local frame whose +z is the canopy's outward normal: 5-6 short arching stems from the
    centre with ~60 ovate leaves (4.5-7 cm) along them, custom normals leaning to +z; with bract_role, `clusters`
    three-bract clusters grouped into an irregular panicle 0.15-0.30 m across near the stem ends."""
    parts = _pk_parts(leaf_role, *([bract_role] if bract_role else [])); g = parts[leaf_role]
    ns = rnd.randint(5, 6); a0 = rnd.uniform(0, 6.3); tips = []
    for k in range(ns):
        a = a0 + 2 * math.pi * k / ns + rnd.uniform(-.3, .3); L = rnd.uniform(.16, .24)
        pts = _pk_arc((0., 0., -.015), a, math.radians(rnd.uniform(18, 32)), math.radians(rnd.uniform(40, 60)), L, 5)
        _pk_tube(g, pts, .0045, .0025, 3); tips.append(pts[-1])
        for j, p in enumerate(pts[1:]):
            for sd in (-1, 1):
                aa = a + sd * math.radians(rnd.uniform(40, 65))
                d = _pk_norm((math.cos(aa), math.sin(aa), rnd.uniform(.1, .45)))
                cn = _pk_norm((-d[0] * d[2], -d[1] * d[2], 1 - d[2] * d[2]))
                Lf = rnd.uniform(.055, .08) * (1 - .15 * j / 4)
                _pk_ovate(g, p, d, cn, Lf, Lf * .6, bend=_pk_norm((rnd.uniform(-.25, .25), rnd.uniform(-.25, .25), 1.)))
    for k in range(6):                                           # a rosette of leaves over the centre
        aa = a0 + k * 1.047 + rnd.uniform(-.2, .2); d = _pk_norm((math.cos(aa), math.sin(aa), .35))
        _pk_ovate(g, (0., 0., .012), d, _pk_norm((-d[0] * .35, -d[1] * .35, 1.)), .06, .035, bend=(0., 0., 1.))
    if bract_role:                                               # bract panicles held above the leaves, as the plant flowers
        gb = parts[bract_role]
        for k in range(clusters):
            t = tips[k % len(tips)]; f = rnd.uniform(.15, 1.)
            c = (t[0] * f + rnd.uniform(-.04, .04), t[1] * f + rnd.uniform(-.04, .04), rnd.uniform(.05, .13))
            _pk_bract_triad(gb, c, rnd, rnd.uniform(.045, .06), _pk_norm((c[0] * 1.2, c[1] * 1.2, 1.)))
    return kit.proto(name, parts)


def _pk_trail(kit, name, leaf_role, bract_role, rnd, length):
    """A trailing cane in a local frame with +z up and -y outward from the wall: it leaves the canopy, arches out
    12-18 cm and hangs `length` m with a slight sway, leafy along its length (custom normals leaning outward) and
    ending in a small panicle of bract triads."""
    parts = _pk_parts(leaf_role, bract_role); g = parts[leaf_role]
    pts = [(0., 0., 0.), (rnd.uniform(-.02, .02), -.07, .035), (rnd.uniform(-.03, .03), -.14, .0)]
    n = max(4, int(length / .09)); sw = rnd.uniform(-.08, .08)
    for i in range(1, n + 1):
        q = i / n
        pts.append((pts[2][0] + sw * math.sin(q * 2.2), -.14 - .06 * q + .03 * math.sin(q * 3.1), -length * q))
    _pk_tube(g, pts, .0045, .002, 3)
    for i, p in enumerate(pts[2:]):
        for sd in (-1, 1):
            d = _pk_norm((sd * rnd.uniform(.5, .9), -rnd.uniform(.2, .6), -rnd.uniform(.2, .7)))
            cn = _pk_norm(_pk_cross(d, (sd * 1., 0., 0.))) if abs(d[0]) < .95 else (0., -1., 0.)
            if cn[1] > 0:
                cn = tuple(-x for x in cn)
            Lf = rnd.uniform(.05, .075)
            _pk_ovate(g, p, d, cn, Lf, Lf * .6, bend=_pk_norm((0., -1., .2)))
    gb = parts[bract_role]
    for k in range(0, len(pts) - 3, 2):                          # bract triads along the lower half and a tip panicle
        p = pts[-1 - k]
        if k > len(pts) // 2 and k:
            break
        _pk_bract_triad(gb, (p[0] + rnd.uniform(-.02, .02), p[1] - .02, p[2] + .01), rnd, rnd.uniform(.038, .05), _pk_norm((0., -1., -.2)))
    return kit.proto(name, parts)


def climber_sprays(kit, name='bougainvillea', leaf_role='pk_leaf', bract_roles=('pk_magenta', 'pk_bract2'), seed=1):
    """The instanced parts wall_drape() scatters: a leafy spray, two flowering sprays (one bract tone each, 16-20 triads held above the leaves)
    and two trailing canes (0.65 m and 1.0 m, one bract tone each). Returns a dict for wall_drape(sprays=...)."""
    rnd = _pkr.Random(seed)
    return dict(leafy=_pk_spray(kit, name + '_leafy', leaf_role, None, rnd),
                flower=[_pk_spray(kit, f'{name}_flower{i}', leaf_role, ro, rnd, clusters=rnd.randint(16, 20)) for i, ro in enumerate(bract_roles)],
                trail=[(L, _pk_trail(kit, f'{name}_trail{i}', leaf_role, ro, rnd, L)) for i, (L, ro) in enumerate(((.65, bract_roles[0]), (1.0, bract_roles[1])))])


def wall_drape(name, p0, p1, out, profile, curtain, kit, sprays, openings=(), thickness=.04, bump=.012, wave=.3, grid=.12,
               ramp=.06, carrier_role='pk_shrub_core', trunks=(), trunk_role='pk_bark', seed=1, module='planting', tongues=4,
               cover=.65, spacing=.21, trails_per_m=5., floor=0., canes=4, carrier_inset=0., rim_sprays=0.):
    """Wall-trained climber or parapet cascade (bougainvillea, wisteria, jasmine) over a wall cross-section `profile`
    [(n, z), ...] (n outward from the wall face line p0-p1, `out` its unit outward normal (x, y)), listed from the
    hanging lower end up and over the coping. A hidden dark carrier (carrier_role: a thin heightfield sheet in (u along
    the wall, s along the profile) whose edges dive 2.5 cm into the masonry) gives depth only; the visible canopy is
    instanced sprays (climber_sprays(): leafy, and flowering where a blob mask covers about `cover` of it) oriented to
    the carrier normal and spun at random, trailing canes hanging from the lower edge (`trails_per_m`, shortened so they
    stay above `floor`), a woody armature of `canes` canes fanning from each trunk over the wall and coping, and trunks
    [(u, (x, y, z) root), ...] from a pot. The hanging edge sits at s = curtain(u) with `tongues` longer lobes; openings
    [(u0, u1, z0, z1), ...] are cut with a 7 cm margin and sprays and canes keep clear of them. No two closed shells share
    a volume (the carrier is the only shell). Opt-in (defaults leave the result unchanged): carrier_inset > 0 stops the
    carrier that far inside the spray envelope, so no carrier rim shows past the leaves at the hem, ends or openings;
    rim_sprays > 0 adds a row of sprays at that spacing along the envelope's outer edge, at least 0.25 m clear of every
    opening, to break its outline. Returns the carrier area in m2."""
    from mathutils import Matrix, Vector
    rnd = _pkr.Random(seed); ss, PN, PZ, NN, NZ = _pk_profile(profile)
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); tx, ty = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    Smax = float(ss[-1]); z0p = profile[0][1]
    cur = curtain if callable(curtain) else (lambda u, c=curtain: c)
    tg = [(rnd.uniform(.12, .88) * L, rnd.uniform(.2, .45), rnd.uniform(.1, .2)) for _ in range(tongues)]
    nz_ = _PkNoise(seed + 5, 2 * math.pi / 1.1)

    def lo(u):
        return max(.0, cur(u) + .12 * nz_(u, 0.) - sum(dp * math.exp(-((u - uc) / w) ** 2) for uc, dp, w in tg))
    us = _pknp.linspace(0., L, max(12, int(L / .05)))
    poly = [(float(u), lo(float(u))) for u in us] + [(L, Smax), (0., Smax)]
    reg = _PkPolygon(poly).buffer(0).intersection(_pksh.box(.02, 0., L - .02, Smax - .015))
    keep = reg
    for u0, u1, a, b in openings:
        reg = reg.difference(_pksh.box(u0 - .07, a - z0p - .07, u1 + .07, b - z0p + .07))
        keep = keep.difference(_pksh.box(u0 - .17, a - z0p - .17, u1 + .17, b - z0p + .17))
    reg = reg.buffer(-.01).buffer(.01)
    V, F, hz = _pk_field(reg, 0., thickness, bump, wave, grid, ramp, seed, mid=True)
    if carrier_inset > 0:                               # the carrier stops inside the spray envelope; sprays keep the full hz
        rc = reg.buffer(-carrier_inset).buffer(-.01).buffer(.01)
        if not rc.is_empty:
            V, F, _ = _pk_field(rc, 0., thickness, bump, wave, grid, ramp, seed, mid=True)

    def world(u, s, h):
        n = _pknp.interp(s, ss, PN); zz = _pknp.interp(s, ss, PZ); a = _pknp.interp(s, ss, NN); c = _pknp.interp(s, ss, NZ)
        L2 = math.hypot(a, c) or 1.; a, c = a / L2, c / L2
        w = n + h * a
        return (p0[0] + u * tx + w * out[0], p0[1] + u * ty + w * out[1], zz + h * c), (a, c)
    pk_mesh(name + ' carrier', [world(u, s, h)[0] for u, s, h in V], F, (), carrier_role, module, shell=True)
    # flowering mask: irregular blobs over about `cover` of the canopy
    blobs = [_pksh.Point(u, s).buffer(rnd.uniform(.16, .34), quad_segs=6) for u, s in pk_scatter(reg, .5 / max(.2, cover) ** .5, seed=seed + 4)]
    patch = _pksh.union_all(blobs) if blobs else None
    if patch is not None:
        _pksh.prepare(patch)
    sreg = keep.intersection(reg.buffer(-.03))
    nfl = [0]

    def spray(u, s):
        (x, y, z), (a, c) = world(u, s, hz(u, s) + rnd.uniform(.004, .03))
        N = Vector((out[0] * a, out[1] * a, c)).normalized(); T = Vector((tx, ty, 0.)); B = N.cross(T).normalized()
        ph = rnd.uniform(0, 6.3); X = (T * math.cos(ph) + B * math.sin(ph)).normalized(); Y = N.cross(X)
        e = Matrix((X, Y, N)).transposed().to_euler('XYZ')
        fl = patch is not None and _pksh.contains_xy(patch, u, s)
        p = sprays['flower'][nfl[0] % len(sprays['flower'])] if fl else sprays['leafy']; nfl[0] += fl
        sc = rnd.uniform(.85, 1.15)
        kit.place(p, x, y, z, e.z, sc, sy=sc * rnd.uniform(.85, 1.1), sz=sc * rnd.uniform(.8, 1.1), lean=(e.x, e.y), track=False)
    for u, s in (pk_scatter(sreg, spacing, seed=seed + 8) if not sreg.is_empty else []):
        spray(u, s)
    if rim_sprays > 0 and not sreg.is_empty:            # a row of sprays along the envelope's outer edge, clear of openings
        holes = [_pksh.box(u0 - .25, a - z0p - .25, u1 + .25, b - z0p + .25) for u0, u1, a, b in openings]
        for ln in _pksh.get_parts(sreg.buffer(-.02).boundary):
            for d in _pknp.arange(rnd.uniform(0., rim_sprays), ln.length, rim_sprays):
                pt = ln.interpolate(float(d)); u, s = pt.x, pt.y
                if not any(h.contains(pt) for h in holes):
                    spray(u, s)
    # trailing canes from the hanging edge, clear of the openings and above the floor
    rot0 = math.atan2(out[0], -out[1])
    for u in _pknp.arange(.12, L - .12, 1 / trails_per_m):
        u = float(u) + rnd.uniform(-.04, .04); s = lo(u) + .06
        if any(u0 - .15 < u < u1 + .15 for u0, u1, a, b in openings) or not _pksh.contains_xy(reg, u, s):
            continue
        (x, y, z), _ = world(u, s, hz(u, s) * .6)
        room = z - floor - .1
        Lp, pr = sprays['trail'][1] if room > 1.05 and rnd.random() < .5 else sprays['trail'][0]
        sc = min(1.1, room / Lp) * rnd.uniform(.8, 1.)
        if sc < .35:
            continue
        kit.place(pr, x, y, z, rot0 + rnd.uniform(-.35, .35), sc, sy=1., sz=sc, track=False)
    # woody armature: trunks from their pots and canes fanning over the wall and coping, on the carrier under the sprays
    tb = PkGeo()
    for u, root in trunks:
        for u0, u1, a, b in openings:
            if u0 - .1 < u < u1 + .1:
                raise ValueError(f'{name}: trunk at u={u:.2f} crosses an opening')
        s_in = lo(u) + .3; (x1, y1, z1), _ = world(u, s_in, hz(u, s_in) * .5)
        (xm, ym, zm), _ = world(u, max(0., (z1 - z0p) * .5), .05)
        _pk_tube(tb, [root, ((root[0] + xm) / 2, (root[1] + ym) / 2, (root[2] + zm) / 2), (xm, ym, zm), (x1, y1, z1)], .035, .022, 6)
        for k in range(canes):
            ang = math.radians(-62 + 124 * k / max(1, canes - 1) + rnd.uniform(-8, 8)); pts = [(x1, y1, z1)]
            for j in range(1, 9):
                uu = u + math.sin(ang) * .3 * j; sj = s_in + math.cos(ang) * .3 * j + .04 * math.sin(j * 1.3 + k)
                if sj > Smax - .05 or not _pksh.contains_xy(keep, uu, sj):
                    break
                pts.append(world(uu, sj, hz(uu, sj) + .006)[0])
            if len(pts) > 2:
                _pk_tube(tb, pts, .016, .007, 5)
    if tb.f:
        pk_mesh(name + ' canes', tb.v, tb.f, (), trunk_role, module)
    return float(reg.area)
# ---- The Spine climbing tower ----
from scipy.spatial import ConvexHull as _Hull

PALETTE.update(trim=(.30, .28, .26), blue=(.20, .26, .32), wall=(.80, .78, .74), soffit=(.76, .60, .40), ctxroof=(.55, .53, .50),
               bedgreen=(.27, .33, .20), crown=(.30, .21, .13), plaza=(.62, .60, .56),
               footrock=(.62, .60, .55), footrock2=(.56, .54, .50), rockdeep=(.20, .14, .09))
pk_palette(PALETTE)
KIT = None
PROTOS = None
INSTANCING = True

SOUTH_L = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south front west wing')
SOUTH_R = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south front east wing')
NOTCH_B = C.Face((0, YN, 0), (1, 0, 0), (0, 1, 0), 'notch back')
NOTCH_W = C.Face((NOTCH[0], 0, 0), (0, 1, 0), (-1, 0, 0), 'notch west return')
NOTCH_E = C.Face((NOTCH[1], 0, 0), (0, -1, 0), (1, 0, 0), 'notch east return')
EAST = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east face')
WEST = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west face')
NORTH = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north face')
RB_S = C.Face((0, RB[2], 0), (1, 0, 0), (0, 1, 0), 'amenity block front')
RB_W = C.Face((RB[0], 0, 0), (0, -1, 0), (1, 0, 0), 'amenity block west')
RB_E = C.Face((RB[1], 0, 0), (0, 1, 0), (-1, 0, 0), 'amenity block east')
FIN_D = .28                                     # fin projection
BANDS = [(z, z + FH) for z in FLOORS]           # tower floors (floor z, next floor z)


def bands_holes(label, lo, hi, bands, margin=.12):
    """One vision-glass hole per floor across the face: spandrel from the floor to SPAN above it, glass up to 0.3 m
    under the next floor (the slab edge sits behind the spandrel)."""
    return [hole(f'{label} floor {i}', (lo + hi) / 2, z0 + SPAN, hi - lo - 2 * margin, z1 - z0 - SPAN - .3, kind='band')
            for i, (z0, z1) in enumerate(bands)]


def fins_at(lo, hi, pitch, start=None, stop=None):
    a = lo + .12 if start is None else start
    b = hi - .12 if stop is None else stop
    n = max(1, round((b - a) / pitch))
    return [a + (b - a) * k / n for k in range(n + 1)]


def curtain(f, lo, hi, z0, ztop, bands, label, pitch=1.2, fine=False, extra=(), fin_z0=None, fin_skip=(), carrier_lo=None, carrier_hi=None,
            fin_role='bronze', fin_d=FIN_D):
    """Bronze curtain wall: a dark spandrel carrier cut by one vision band per floor (plus `extra` holes), a recessed
    pane and slim mullions in each band, proud bronze fins at `pitch` (closer fins and shallower mid-floor sunshade
    bars when fine); the floor lines stay dark and flush (v002: no bronze transoms, so the verticals dominate)."""
    holes = bands_holes(label, lo, hi, bands) + list(extra)
    f.wall(label + ' carrier', lo if carrier_lo is None else carrier_lo, (hi if carrier_hi is None else carrier_hi) - EPS,
           z0, ztop, depth=T, role='spandrel', holes=holes)
    m = Merge(f)
    us = [u for u in fins_at(lo, hi, pitch) if not any(a <= u <= b for a, b in fin_skip)]
    bh = holes[:len(bands)]
    zm0, zm1 = bh[0]['z'], bh[-1]['z'] + bh[-1]['h']
    for u in us:                                                        # full-height mullions (inside the spandrels they are buried)
        if bh[0]['u'] - bh[0]['w'] / 2 + .05 < u < bh[0]['u'] + bh[0]['w'] / 2 - .05:
            m.box('frame', u, .07, (zm0 + zm1) / 2, .06, .10, zm1 - zm0)
    for h in bh:
        m.box('glass', h['u'], .13, h['z'] + h['h'] / 2, h['w'] - .02, .012, h['h'] - .02)
        m.box('frame', h['u'], .07, h['z'] + .03, h['w'], .10, .06)
        m.box('frame', h['u'], .07, h['z'] + h['h'] - .03, h['w'], .10, .06)
        register(f, h, .07, 'curtain wall', 'offices and apartments')
    fz0 = bands[0][0] if fin_z0 is None else fin_z0
    for u in us:
        m.box(fin_role, u, -fin_d / 2 + .004, (fz0 + ztop) / 2, .07, fin_d + .008, ztop - fz0)
    if fine:                                                            # v008: two thin bronze sunshade bars per storey, proud of the fins
        for z0b, z1b in bands:
            for q in (.42, .72):
                m.box('bronze', (lo + hi) / 2, -(fin_d + .05) / 2 + .004, z0b + SPAN + (z1b - z0b - SPAN - .3) * q, hi - lo - .04, fin_d + .05, .07)
    m.flush(label)
    return holes


def bays_between(lo, hi, piers, label, z1=7.45):
    """Double-height base: one glazed hole per bay between the light piers (u intervals)."""
    edges = [lo]
    for a, b in piers:
        edges += [a, b]
    edges.append(hi)
    holes = []
    for k in range(0, len(edges), 2):
        a, b = edges[k], edges[k + 1]
        if b - a > .6:
            holes.append(hole(f'{label} bay {k // 2}', (a + b) / 2, .15, b - a - .04, z1 - .15, kind='storefront'))
    return holes


def dress_storefront(f, holes, label, door_bays=(), pier_list=()):
    m = Merge(f)
    for k, h in enumerate(holes):
        u, w = h['u'], h['w']
        n = max(2, round(w / 1.9))
        framed(m, f, h, cols=n, rows=2, inset=.18, occupied='shops and lobby', kind='storefront', frame='frame')
        if k in door_bays:
            for s in (-1, 1):
                m.box('hardware', u + s * 1.0, .11, 1.4, .07, .04, 2.5)
                m.box('hardware', u + s * .25, .1, 1.1, .03, .04, .5)
            m.box('hardware', u, .11, 2.67, 2.07, .04, .07)
    for a, b in pier_list:
        m.box('concrete', (a + b) / 2, -.039, (BASE - .38) / 2, b - a, .102, BASE - .38)
    m.flush(label + ' storefront')


def tower():
    """The six tower faces, the notch walls and the base."""
    tb = BANDS
    # South front, west wing: canopy shopfronts below the tower floors.
    piers = [(-18.8, -18.2), (-14.0, -13.4), (-9.6, -9.0)]
    sh = bays_between(X0 + .6, NOTCH[0], piers, 'west shopfronts')
    curtain(SOUTH_L, X0, NOTCH[0], 0.0, PARA - .08, tb, 'south west wing', extra=sh, fin_z0=CANOPY[3] - .01)
    dress_storefront(SOUTH_L, sh, 'south west wing', door_bays=(1,), pier_list=[(X0 + .06, X0 + .6)] + piers)
    # South front, east wing: glazed lobby base.
    piers = [(15.4, 16.0), (19.8, 20.4)]
    sh = bays_between(NOTCH[1], X1 - .4, piers, 'east lobby')
    curtain(SOUTH_R, NOTCH[1], X1, 0.0, PARA - .08, tb, 'south east wing', extra=sh, fin_z0=BASE - .4,
            fin_skip=[(NOTCH[1] - .1, BAL_X1 + .25)])
    dress_storefront(SOUTH_R, sh, 'south east wing', door_bays=(0,), pier_list=piers + [(X1 - .4, X1 - .06)])
    SOUTH_R.part('East lobby base head', (NOTCH[1] + X1) / 2, -.05, BASE - .2, X1 - NOTCH[1] - .02, .12, .4, 'concrete', 'base', 0)
    # Notch returns (glass) and the notch back: dark glazing west of the spine, a concrete wall with balcony doors east of it.
    for f, lo, hi, lab in ((NOTCH_W, Y0 + T, YN + T, 'notch west return'), (NOTCH_E, -(YN + T), -(Y0 + T), 'notch east return')):
        sh = [hole(f'{lab} base', (lo + hi) / 2, .15, hi - lo - .3, 7.1, kind='storefront')]
        curtain(f, lo, hi, 0.0, PARA - .08, tb, lab, pitch=1.2, extra=sh, fin_z0=BASE - .4)
        m = Merge(f)
        framed(m, f, sh[0], cols=2, rows=2, inset=.18, occupied='shops and lobby', kind='storefront', frame='frame')
        m.flush(lab + ' base')
    sh = [hole('notch west back base', (NOTCH[0] + SPX[0]) / 2, .15, SPX[0] - NOTCH[0] - .3, 7.1, kind='storefront')]
    curtain(NOTCH_B, NOTCH[0], SPX[0] + .05, 0.0, PARA - .08, tb, 'notch west back', pitch=1.3, extra=sh, fin_z0=BASE - .4,
            fin_role='frame', fin_d=.06)                              # darker recessed glazing, dark mullions, no bronze fins
    m = Merge(NOTCH_B)
    framed(m, NOTCH_B, sh[0], cols=3, rows=2, inset=.18, occupied='climbing gym', kind='storefront', frame='frame')
    m.flush('notch west back base')
    notch_east_wall()
    # Side and rear faces: close fins with sunshade bars on the sides (front source: the east face).
    for f, lo, hi, lab, fine, pitch in ((EAST, Y0 + T, Y1, 'east face', True, 1.6), (WEST, -Y1, -(Y0 + T), 'west face', True, 1.6)):
        sh = [hole(f'{lab} base glazing', (lo + hi) / 2, .15, hi - lo - 1.2, 7.1, kind='storefront')]
        curtain(f, lo, hi, 0.0, PARA - .08, tb, lab, pitch=pitch, fine=fine, extra=sh, fin_z0=BASE - .4, fin_d=.16)
        m = Merge(f)
        framed(m, f, sh[0], cols=8, rows=2, inset=.18, occupied='shops', kind='storefront', frame='frame')
        m.flush(lab + ' base')
    # North face: the full height to the roof, a parapet outside the amenity block, the amenity storey above it.
    lo, hi = -(X1 - T), -(X0 + T)
    grid = fins_at(lo, hi, 1.2)
    sh = [hole('north base glazing', -12.0, .15, 10.0, 3.6, kind='storefront'), hole('north service door', 6.0, .15, 4.2, 4.0, kind='door')]
    curtain(NORTH, lo, hi, 0.0, ROOF, tb, 'north face', extra=sh, fin_z0=BASE - .4)
    m = Merge(NORTH)
    framed(m, NORTH, sh[0], cols=5, rows=1, inset=.18, occupied='lobby', kind='storefront', frame='frame')
    m.box('metal', 6.0, .2, 2.15, 4.18, .06, 3.98)
    for k in range(1, 7):
        m.box('steel', 6.0, .16, .15 + 4.0 * k / 7, 4.1, .03, .03)
    register(NORTH, sh[1], .2, 'door', 'loading')
    m.flush('north base')
    for a, b, lab in ((lo, -RB[1], 'north parapet east'), (-RB[0], hi, 'north parapet west')):
        NORTH.wall(lab, a, b - EPS, ROOF, PARA - .08, depth=T, role='spandrel')
        m = Merge(NORTH)
        for u in [g for g in grid if a + .1 < g < b - .1]:
            m.box('bronze', u, -FIN_D / 2 + .004, (ROOF + PARA - .08) / 2, .07, FIN_D + .008, PARA - .08 - ROOF)
        m.flush(lab)
    amenity_block(grid)
    corners()


def notch_east_wall():
    """v006: dark recessed glazing immediately east of the spine (source front and oblique), the balconies projecting
    from it, the climbing-gym entrance in its double-height base."""
    f = NOTCH_B
    lo, hi = SPX[1] - .05, NOTCH[1]
    door = hole('climbing gym entrance', (lo + hi) / 2 + .2, .15, 3.4, 7.1, kind='door')
    curtain(f, lo, hi, 0.0, PARA - .08, BANDS, 'notch east back', pitch=1.3, extra=[door], fin_z0=BASE - .4, fin_role='frame', fin_d=.06)
    m = Merge(f)
    framed(m, f, door, cols=3, rows=2, inset=.18, occupied='climbing gym', kind='glazed door', frame='frame')
    m.flush('notch east base')


def corners():
    """Bronze corner posts at the outer corners and the notch mouths, from grade to the coping."""
    b = Batch()
    for x, y in ((X0, Y0), (X1, Y0), (X0, Y1), (X1, Y1), (NOTCH[0], Y0), (NOTCH[1], Y0)):
        sx = -1 if x in (X0, NOTCH[1]) else 1
        sy = -1 if y == Y0 else 1
        if x in NOTCH:
            sx = 1 if x == NOTCH[0] else -1
        b.box('bronze', x + sx * .12, y + sy * .12, (.0 + PARA - .08) / 2, .36, .36, PARA - .08)
    b.flush('corner posts')


def amenity_block(grid):
    """Glazed amenity storey over the north half of the roof: bronze fins, a white roof with plant."""
    z0 = ROOF
    band = [(ROOF + .06, RBTOP - .25)]
    for f, lo, hi, lab in ((RB_S, RB[0], RB[1], 'amenity front'), (RB_W, -(Y1 - T), -(RB[2] + T), 'amenity west'),
                           (RB_E, RB[2] + T, Y1 - T, 'amenity east')):
        holes = [hole(f'{lab} glazing', (lo + hi) / 2, ROOF + .55, hi - lo - .3, 1.9, kind='band')]
        f.wall(lab + ' carrier', lo, hi - EPS, z0, RBTOP - .08, depth=T, role='spandrel', holes=holes)
        m = Merge(f)
        h = holes[0]
        m.box('glass', h['u'], .13, h['z'] + h['h'] / 2, h['w'] - .02, .012, h['h'] - .02)
        # v005: flush bronze panels about 1.9 m wide with 6 cm reveals over the upper two thirds (about 19 panels
        # across the south face), the dark glazing band low on the face.
        zb0, zb1 = ROOF + 2.6, RBTOP - .14
        n = max(1, round((hi - lo) / 1.9))
        for i in range(n):
            a, b2 = lo + (hi - lo) * i / n, lo + (hi - lo) * (i + 1) / n
            m.box('crown', (a + b2) / 2, -.045, (zb0 + zb1) / 2, b2 - a - .06, .09, zb1 - zb0)
        m.box('frame', h['u'], .07, h['z'] + .03, h['w'], .10, .06)
        register(f, h, .07, 'curtain wall', 'roof amenity room')
        m.flush(lab)
    lo, hi = -RB[1], -RB[0]                                         # north face of the amenity storey (above the tower's north face)
    holes = [hole('amenity north glazing', (lo + hi) / 2, ROOF + .55, hi - lo - .6, 1.9, kind='band')]
    NORTH.wall('amenity north carrier', lo, hi - EPS, ROOF, RBTOP - .08, depth=T, role='spandrel', holes=holes)
    m = Merge(NORTH)
    h = holes[0]
    m.box('glass', h['u'], .13, h['z'] + h['h'] / 2, h['w'] - .02, .012, h['h'] - .02)
    n = max(1, round((hi - lo) / 1.9))
    for i in range(n):
        a, b2 = lo + (hi - lo) * i / n, lo + (hi - lo) * (i + 1) / n
        m.box('crown', (a + b2) / 2, -.045, (ROOF + 2.6 + RBTOP - .14) / 2, b2 - a - .06, .09, RBTOP - 2.74 - ROOF)
    register(NORTH, h, .07, 'curtain wall', 'roof amenity room')
    m.flush('amenity north')
    b = Batch()
    rx0, rx1, ry0, ry1 = RB[0] + T, RB[1] - T, RB[2] + T, Y1 - T
    b.box('roof', (rx0 + rx1) / 2, (ry0 + ry1) / 2, RBTOP - .65, rx1 - rx0 + .002, ry1 - ry0 + .002, .3)
    b.box('membrane', (rx0 + rx1) / 2, (ry0 + ry1) / 2, RBTOP - .495, rx1 - rx0 - .02, ry1 - ry0 - .02, .01)
    # coping ring (four runs, no overlap)
    zc = RBTOP - .08
    b.box('coping', (RB[0] + RB[1]) / 2, RB[2] + T / 2 - .1, zc + .04, RB[1] - RB[0] + .66, T + .62, .08)
    b.box('coping', (RB[0] + RB[1]) / 2, Y1 - T / 2 + .1, zc + .04, RB[1] - RB[0] + .66, T + .62, .08)
    for x in (RB[0] + T / 2 - .1, RB[1] - T / 2 + .1):
        b.box('coping', x, (RB[2] + T + .21 + Y1 - T - .21) / 2, zc + .041, T + .62, Y1 - RB[2] - 2 * T - .42, .08)
    # inner liners of the amenity parapet
    zl0, zl1 = RBTOP - .495, zc - .002
    b.box('concrete', (rx0 + rx1) / 2, ry0 + .0125, (zl0 + zl1) / 2, rx1 - rx0 - .002, .025, zl1 - zl0)
    b.box('concrete', (rx0 + rx1) / 2, ry1 - .0125, (zl0 + zl1) / 2, rx1 - rx0 - .002, .025, zl1 - zl0)
    b.box('concrete', rx0 + .0125, (ry0 + ry1) / 2, (zl0 + zl1) / 2, .025, ry1 - ry0 - .056, zl1 - zl0)
    b.box('concrete', rx1 - .0125, (ry0 + ry1) / 2, (zl0 + zl1) / 2, .025, ry1 - ry0 - .056, zl1 - zl0)
    rz = RBTOP - .49
    # plant: condenser rows, two air handlers, ducts, a stair and lift overrun
    for i in range(4):
        for j in range(2):
            x, y = 2.0 + 1.6 * i, 3.4 + 1.7 * j
            b.box('metal', x, y, rz + .55, 1.2, 1.2, 1.1)
            b.box('hardware', x, y, rz + 1.105, .9, .9, .012)
    for x, y, w, d, h in ((-6.5, 4.0, 4.2, 2.4, 1.8), (9.5, 1.6, 3.0, 2.0, 1.5)):
        b.box('metal', x, y, rz + h / 2, w, d, h)
        b.box('duct', x, y - d / 2 - .01, rz + h * .6, w * .6, .02, h * .4)
    for i in range(4):                                                  # v008: a second condenser bank
        for j in range(2):
            x, y = -6.0 + 1.6 * i, 7.6 + 1.7 * j
            b.box('metal', x, y, rz + .55, 1.2, 1.2, 1.1)
            b.box('hardware', x, y, rz + 1.105, .9, .9, .012)
    b.box('duct', -1.0, 4.0, rz + 1.2, 8.0, .7, .7)
    b.box('duct', -4.0, 6.3, rz + .9, 9.0, .5, .5)
    b.box('duct', 8.0, 6.6, rz + .9, .5, 3.6, .5)
    b.box('duct', 2.6, 1.5, rz + 1.2, .7, 4.3, .7)
    for x in (-3.0, 1.0):
        b.box('steel', x, 4.0, rz + .43, .08, .5, .86)
    b.box('concrete', -12.0, 6.0, rz + 1.5, 4.0, 4.6, 3.0)                     # stair / lift overrun
    b.box('coping', -12.0, 6.0, rz + 3.04, 4.2, 4.8, .08)
    b.box('metal', -12.0, 3.68, rz + 1.1, 1.0, .06, 2.1)
    b.flush('amenity roof')


def coping_and_liners():
    """Light coping ring on the terrace parapet (runs that butt, never overlap) and light liners on its inner faces."""
    b = Batch()
    zc0, zc1 = PARA - .081, PARA
    o, i = FIN_D + .04, T + .05                                 # coping covers the fins and the carrier
    w = o + i
    b.box('coping', (X0 - o + NOTCH[0] + o) / 2, Y0 - o + w / 2, (zc0 + zc1) / 2, NOTCH[0] - X0 + 2 * o, w, zc1 - zc0)
    b.box('coping', (NOTCH[1] - o + X1 + o) / 2, Y0 - o + w / 2, (zc0 + zc1) / 2, X1 - NOTCH[1] + 2 * o, w, zc1 - zc0)
    ya, yb = Y0 - o + w, Y1 + o - w
    b.box('coping', X1 + o - w / 2, (ya + Y1 + o) / 2, (zc0 + zc1) / 2 + .0005, w, Y1 + o - ya, zc1 - zc0 - .001)
    b.box('coping', X0 - o + w / 2, (ya + Y1 + o) / 2, (zc0 + zc1) / 2 + .0005, w, Y1 + o - ya, zc1 - zc0 - .001)
    for a, c in ((X0 - o + w, RB[0] - .002), (RB[1] + .002, X1 + o - w)):
        b.box('coping', (a + c) / 2, Y1 + o - w / 2, (zc0 + zc1) / 2 + .001, c - a, w, zc1 - zc0 - .002)
    # notch returns and back
    for x, s in ((NOTCH[0], -1), (NOTCH[1], 1)):                # return copings: fins point into the notch
        xa = x + s * (T + .05); xb = x - s * o
        b.box('coping', (xa + xb) / 2, (ya + YN + T + .05) / 2, (zc0 + zc1) / 2 + .0005, abs(xa - xb), YN + T + .05 - ya, zc1 - zc0 - .001)
    for a, c in ((NOTCH[0] + o, SPX[0]), (SPX[1], NOTCH[1] - o)):
        b.box('coping', (a + c) / 2, YN - o + w / 2, (zc0 + zc1) / 2 + .001, c - a, w, zc1 - zc0 - .002)
    b.flush('parapet coping')
    b = Batch()
    zl0, zl1 = ROOF + .07, PARA - .082
    li = T + .0125
    segs = [((X0 + T, Y0 + li), (NOTCH[0] - T, Y0 + li)), ((NOTCH[1] + T, Y0 + li), (X1 - T, Y0 + li)),
            ((NOTCH[0] - T, YN + li), (SPX[0] - .02, YN + li)), ((SPX[1] + .02, YN + li), (NOTCH[1] + T, YN + li)),
            ((X0 + T, Y1 - li), (RB[0] - .02, Y1 - li)), ((RB[1] + .02, Y1 - li), (X1 - T, Y1 - li))]
    for (ax, ay), (bx, by) in segs:
        b.box('concrete', (ax + bx) / 2, ay, (zl0 + zl1) / 2, bx - ax - .002, .025, zl1 - zl0)
    for x, s in ((X0, 1), (X1, -1)):
        b.box('concrete', x + s * li, 0.0, (zl0 + zl1) / 2, .025, Y1 - Y0 - 2 * T - .03, zl1 - zl0)
    for x, s in ((NOTCH[0], -1), (NOTCH[1], 1)):
        b.box('concrete', x + s * li, (Y0 + T + .03 + YN + T - .03) / 2, (zl0 + zl1) / 2, .025, YN - Y0 - .06, zl1 - zl0)
    b.flush('parapet liners')


# ---- the climbing spine ----

def _smooth01(t):
    t = max(0., min(1., t))
    return t * t * (3 - 2 * t)


NA = _PkNoise(101, 1.0)
NB = _PkNoise(202, 1.0)
NC = _PkNoise(303, 1.0)
ND = _PkNoise(404, 1.0)


FOOT = 8.0                                                            # the lower two storeys: a chunkier, greyer block mass
FOOT_OUT = .6                                                         # the foot's straight envelope stands this far proud


def _loop():
    """The spine's closed outline unrolled anticlockwise from its north-west corner: (perimeter length, corner s
    values, the exposed range below the roof - the notch edges at YN)."""
    Lf, W = SPY1 - SPY0, SPX[1] - SPX[0]
    corners = (0., Lf, Lf + W, 2 * Lf + W)
    return 2 * (Lf + W), corners, (Lf - (YN - SPY0), Lf + W + (YN - SPY0))


def _loop_xy(s, d):
    """Point at loop distance s moved d along the outward normal (d <= 0 is inside the envelope)."""
    Lf, W = SPY1 - SPY0, SPX[1] - SPX[0]
    for c, (mx, my) in ((Lf, (-1, -1)), (Lf + W, (1, -1)), (2 * Lf + W, (1, 1))):
        if abs(s - c) < 1e-6:                                           # corners move on the mitre
            return (SPX[0] if mx < 0 else SPX[1]) + mx * d, (SPY0 if my < 0 else SPY1) + my * d
    if s <= Lf:
        return SPX[0] - d, SPY1 - s
    if s <= Lf + W:
        return SPX[0] + (s - Lf), SPY0 - d
    if s <= 2 * Lf + W:
        return SPX[1] + d, SPY0 + (s - Lf - W)
    return SPX[1] - (s - 2 * Lf - W), SPY1 + d


def _cols(rnd, P, pins, step):
    """Loop columns between pinned values (corners and notch edges), irregularly spaced around `step`."""
    pins = sorted(set(pins)); cols, fixed = [], set()
    for a, b in zip(pins, pins[1:] + [P]):
        n = max(1, round((b - a) / step))
        w = [rnd.uniform(.5, 1.5) for _ in range(n)]
        acc = 0.
        for k in range(n):
            if k == 0:
                fixed.add(len(cols))
            cols.append(a + (b - a) * acc / sum(w)); acc += w[k]
    return cols, fixed


def _blocks(rnd, P, z0, z1, wide, tall, deep):  # deep: range of the plane offsets
    """Cleaved blocks as Voronoi cells over (s, z), stretched vertically (`tall` x `wide`), each a tilted plane up to
    `deep` inside the envelope; wraps around the loop."""
    from scipy.spatial import cKDTree
    pts, planes, s = [], [], 0.
    while s < P:
        z = z0 + rnd.uniform(0, tall)
        while z < z1 + tall:
            pts.append((s + rnd.uniform(-.25, .25) * wide, z / (tall / wide)))
            planes.append((-rnd.uniform(.0, deep), rnd.choice((-1, 1)) * rnd.uniform(.2, .5), rnd.uniform(-.15, .15)))
            z += tall * rnd.uniform(.6, 1.4)
        s += wide * rnd.uniform(.7, 1.3)
    ext = [(a + o, b) for o in (-P, 0., P) for a, b in pts]
    return cKDTree(ext), ext, planes * 3, tall / wide


def _depth(B, s, z, deep):
    _, i = B[0].query((s, z / B[3]))
    (cs, cz), (a, gs, gz) = B[1][i], B[2][i]
    return max(-deep, min(0., a + gs * (s - cs) + gz * (z - cz * B[3])))


def _lattice(name, roles, rnd, P, cols, fixed, wobble, rows, depth, offset, warp, emit, keep_z):
    """Lattice of rock facets over loop columns x rows. Vertex = loop point at offset + depth(column, s, z), where
    depth <= 0 always, so nothing passes the straight envelope; z is warped (staggered foot seam). Quads split on
    random diagonals; `emit(i, j)` picks the faces. Coplanar facets of one cleaved block are then merged into large
    planar faces, and each face takes the lit, turned or deep stone by how far it turns from its face plane."""
    nc, grid = len(cols), []
    for ri, r in enumerate(rows):
        line = []
        for ci, s in enumerate(cols):
            ss, rr = s, r
            if ci in wobble:                                             # fissures wander a little, as one
                ss = s + .3 * NB(wobble[ci] * 3.1, r * .06)
            elif ci not in fixed:
                nxt = cols[ci + 1] if ci + 1 < nc else P
                ss = s + rnd.uniform(-.28, .28) * min(nxt - s, s - cols[ci - 1])
            if ri not in keep_z:
                rr = r + rnd.uniform(-.3, .3) * min(r - rows[ri - 1], rows[ri + 1] - r)
            d = depth(ci, ss, rr)
            x, y = _loop_xy(ss, offset(ss, rr) + d)
            line.append((x, y, warp(ss, rr)))
        grid.append(line)
    F = []
    for i in range(len(rows) - 1):
        for j in range(nc):
            if not emit(i, j):
                continue
            k = (j + 1) % nc
            a, b, c, e = (i, j), (i, k), (i + 1, k), (i + 1, j)
            F += [(a, b, c), (a, c, e)] if rnd.random() < .5 else [(a, b, e), (b, c, e)]
    return grid, F


def _rock_object(name, grid, F, roles, extra=()):
    used = sorted({v for f in F for v in f}); idx = {v: n for n, v in enumerate(used)}
    V = [grid[i][j] for i, j in used]
    o = C.mesh(name, V, [tuple(idx[v] for v in f) for f in F] + [tuple(idx[v] for v in f) for f in extra], roles[0], 'climbing spine')
    C.bpy.context.view_layer.objects.active = o                          # merge each block's coplanar facets
    mod = o.modifiers.new('planar blocks', 'DECIMATE'); mod.decimate_type = 'DISSOLVE'; mod.angle_limit = math.radians(.8)
    C.bpy.ops.object.modifier_apply(modifier=mod.name)
    for r in roles[1:]:
        o.data.materials.append(C.MATS[r])
    count = [0, 0, 0]
    for poly in o.data.polygons:
        poly.use_smooth = False
        cx, cy, cz = poly.center
        if cz > SPTOP - .05:
            continue
        dn = min((abs(cx - SPX[0]), (1, 0)), (abs(cx - SPX[1]), (1, 0)), (abs(cy - SPY0), (0, 1)), (abs(cy - SPY1), (0, 1)))[1]
        n = poly.normal
        c = abs(n[0] * dn[0] + n[1] * dn[1])
        k = 2 if (c < .55 or n[2] < -.45) else 1 if c < .9 else 0
        poly.material_index = k; count[k] += 1
    return o, V, count


def spine():
    """The climbing spine (v008): a straight-edged rock prism. Above the foot, cleaved blocks (1-2 m wide, 2-4 m tall,
    tilted both ways) stand up to 0.8 m proud of the deepest recess, each merged into a few large planar faces, and
    eight continuous vertical fissures (0.26 m wide, 0.3 m deeper than the rock either side) wander down the shaft;
    every vertex is inside the envelope, so both arrises are straight. Faces turned from their plane take a mid or a
    deep stone. Above the roof the rock wraps all four faces of the solid 7.4 x 6 m crown block up to a flush coping.
    The lower two storeys are a greyer mass of larger blocks (1.5-2.5 m) within a straight envelope 0.6 m proud,
    meeting the shaft along a staggered seam."""
    import json
    rnd = random.Random(71)
    P, corners, (sE0, sE1) = _loop()
    Lf, W = SPY1 - SPY0, SPX[1] - SPX[0]
    exposed = lambda s: sE0 - 1e-6 <= s <= sE1 + 1e-6
    edge = lambda s: _smooth01(min(s - sE0, sE1 - s) / .8) if exposed(s) else 0.
    cap = lambda z: 1 - _smooth01((z - (SPTOP - 1.0)) / .7)

    def wn(s, z):                                                        # flat where the rock meets the notch glazing
        return max(edge(s), _smooth01((z - ROOF) / .8))
    # Staggered foot seam: linear between knots (corners included) so both lattices share it exactly.
    knots = [sE0, sE1, Lf, Lf + W]
    s = sE0 + rnd.uniform(1.6, 2.4)
    while s < sE1 - 1.2:
        if all(abs(s - c) > .5 for c in (Lf, Lf + W)):
            knots.append(s)
        s += rnd.uniform(1.6, 2.4)
    knots = sorted(knots)
    kz = {k: (FOOT if k in (sE0, sE1) else FOOT + rnd.uniform(-1.0, 1.0)) for k in knots}

    def seam(s):
        if not (sE0 < s < sE1):
            return FOOT
        for a, b in zip(knots, knots[1:]):
            if a <= s <= b:
                return kz[a] + (kz[b] - kz[a]) * (s - a) / (b - a)
        return FOOT
    # Shaft and crown.
    fis_at = [sE0 + .3 + (Lf - .5 - sE0 - .3) * rnd.uniform(.3, .7)]
    q = Lf + rnd.uniform(.5, 1.3)                                        # front: irregular gaps 1.2-3.2 m
    while q < Lf + W - .6:
        fis_at.append(q); q += rnd.uniform(1.2, 3.2)
    fis_at += [Lf + W + .5 + (sE1 - .3 - Lf - W - .5) * rnd.uniform(.3, .7)]
    fis_at += [sE1 + 1.6, 2 * Lf + W + W * .45]                        # crown: east side behind the notch, and back
    fdeep = [rnd.uniform(.12, .34) for _ in fis_at]                      # each fissure its own depth and width
    fwide = [rnd.uniform(.09, .18) for _ in fis_at]
    pins = list(corners) + [sE0, sE1] + knots
    for f, w in zip(fis_at, fwide):
        pins += [f - w, f, f + w]
    cols, fixed = _cols(rnd, P, pins, .62)
    wobble, centre, fcol = {}, set(), {}
    for n, f in enumerate(fis_at):
        for ci, s in enumerate(cols):
            if abs(s - f) < fwide[n] + 1e-6:
                wobble[ci] = n
                if abs(s - f) < 1e-6:
                    centre.add(ci); fcol[ci] = n
    rows, r = [FOOT], FOOT
    while r < SPTOP - .5:
        r += rnd.uniform(.45, 1.1)
        rows.append(min(r, SPTOP - .35))
    rows.append(SPTOP)
    B = _blocks(rnd, P, FOOT - 1, SPTOP, 1.5, 3.0, .5)
    nr = len(rows)

    def shaft_depth(ci, s, z):
        if abs(s - min(corners, key=lambda c: abs(c - s))) < 1e-6 or z <= FOOT + 1e-6 or z >= SPTOP - 1e-6:
            return 0.
        d = _depth(B, s, z, .8)
        if ci in centre:                                                 # deep runs and shallower stretches
            n = fcol[ci]                                                 # deep runs that fade out and return
            d = max(-.85, d - fdeep[n] * _smooth01(.5 + 1.4 * NC(n * 2.3, z * .09)))
        return d * wn(s, z) * cap(z)
    crown_from = next(i for i, r in enumerate(rows) if r >= ROOF - .9)
    ncol = len(cols)

    def emit(i, j):
        k = (j + 1) % ncol
        return i >= crown_from or (exposed(cols[j]) and exposed(cols[k] if k else P))
    shaft_warp = lambda s, z: seam(s) + (z - FOOT) * (SPTOP - seam(s)) / (SPTOP - FOOT)
    grid, F = _lattice('shaft', None, rnd, P, cols, fixed, wobble, rows, shaft_depth, lambda s, z: 0., shaft_warp, emit, {0, nr - 1})
    top = [tuple((nr - 1, j) for j in range(ncol))]                     # flush top under the coping
    o, V, count = _rock_object('Climbing spine fractured rock', grid, F, ('rock', 'rock2', 'rockdeep'), extra=top)
    out = max(max(SPX[0] - x, x - SPX[1], SPY0 - y, y - SPY1) for x, y, z in V)
    # Foot: larger greyer blocks inside a straight envelope 0.6 m proud, chamfered back to the shaft at the seam.
    fcols, ffixed = _cols(rnd, P, list(corners) + [sE0, sE1] + knots, 1.1)
    frows, r = [0.], 0.
    while r < FOOT - 1.6:
        r += rnd.uniform(1.0, 1.7)
        frows.append(min(r, FOOT - .9))
    frows.append(FOOT)
    FB = _blocks(rnd, P, 0., FOOT, 2.0, 2.4, .45)
    off = lambda s, z: FOOT_OUT * edge(s) * (1 - _smooth01((z - (FOOT - 1.6)) / 1.6))

    def foot_depth(ci, s, z):
        if ci in ffixed and abs(s - min(corners, key=lambda c: abs(c - s))) < 1e-6:
            return 0.
        return _depth(FB, s, z, .7) * edge(s) * (1 - _smooth01((z - (FOOT - .5)) / .5))
    fgrid, fF = _lattice('foot', None, rnd, P, fcols, ffixed, {}, frows, foot_depth, off, lambda s, z: z * seam(s) / FOOT,
                         lambda i, j: exposed(fcols[j]) and exposed(fcols[(j + 1) % len(fcols)] if (j + 1) % len(fcols) else P),
                         {0, len(frows) - 1})
    fo, fV, fcount = _rock_object('Climbing spine foot rock', fgrid, fF, ('footrock', 'footrock2', 'footrock2'))
    fout = max(max(SPX[0] - FOOT_OUT - x, x - SPX[1] - FOOT_OUT, SPY0 - FOOT_OUT - y) for x, y, z in fV)
    print('SPINE_ENVELOPE', json.dumps(dict(shaft_max_outside_m=round(out, 4), foot_max_outside_m=round(fout, 4),
                                            shaft_faces_lit_mid_deep=count, foot_faces_lit_mid_deep=fcount, fissures=len(fis_at),
                                            seam_z=[round(kz[k], 2) for k in knots])))
    b = Batch()
    b.box('coping', (SPX[0] + SPX[1]) / 2, (SPY0 + SPY1) / 2, SPTOP + .06, W + .08, SPY1 - SPY0 + .08, .12)   # flush coping, 40 mm drip
    b.flush('spine cap')
    # Large rounded-angular boulders heaped against the foot (source front and oblique).
    for k, (x, y, rx, ry, rz, lean) in enumerate(((SPX[0] + .3, SPY0 - 1.9, 1.6, 1.3, 2.6, .1), (SPX[0] + 2.8, SPY0 - 2.2, 1.3, 1.1, 1.8, 0.),
                                                   (SPX[1] - .4, SPY0 - 2.0, 1.5, 1.25, 2.3, .15), (SPX[0] - 1.5, SPY0 + 1.2, 1.15, 1.0, 1.7, .1),
                                                   (SPX[1] + 1.4, SPY0 + 1.0, 1.1, .95, 1.6, 0.))):
        stone(f'Spine foot boulder {k}', x, y, .12, rx, ry, rz, k, rot=k * 1.9, tilt=lean)
    # Holds: about 40 sparse holds on lattice points of the front, varied size and tint.
    front = [grid[i][j] for i in range(1, nr - 1) for j in range(ncol)
             if Lf + .4 < cols[j] < Lf + W - .4 and j not in wobble and 9.6 < grid[i][j][2] < SPTOP - 2.2]
    hrnd = random.Random(31)
    hb = Batch()
    for x, y, z in hrnd.sample(front, min(40, len(front))):
        r = hrnd.uniform(.05, .1)
        hb.beam('hold' if hrnd.random() < .6 else 'hold2', (x, y + .05, z), (x, y - r, z + hrnd.uniform(-.03, .05)),
                r * hrnd.uniform(1.2, 2.0), r * hrnd.uniform(.9, 1.4))
    hb.flush('spine holds')


def carved(rings, per):
    """The spine's carved skin as triangles: facets that turn away from the face (flake sides, ledge undersides)
    take the darker stone, so the relief reads in flat light as it does in the low sun of the sources."""
    V = [v for ring in rings for v in ring]
    m = len(rings[0]); n = len(per)
    light, dark = [], []
    for i in range(len(rings) - 1):
        a, b = i * m, (i + 1) * m
        for j in range(m):
            k = (j + 1) % m
            for tri in ((a + j, b + j, b + k), (a + j, b + k, a + k)):
                p0, p1, p2 = (V[q] for q in tri)
                u = [p1[c] - p0[c] for c in range(3)]; w = [p2[c] - p0[c] for c in range(3)]
                nn = (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0])
                L = math.sqrt(sum(c * c for c in nn)) or 1.
                nn = [c / L for c in nn]
                if j < n - 1:
                    bx, by = per[j][2] + per[j + 1][2], per[j][3] + per[j + 1][3]
                    bl = math.hypot(bx, by) or 1.
                    face = abs(nn[0] * bx / bl + nn[1] * by / bl)          # winding-agnostic: |cos| to the face normal
                    (dark if face < .8 else light).append(tri)
                else:
                    light.append(tri)
    fs_bottom = tuple(range(m - 1, -1, -1)); fs_top = tuple((len(rings) - 1) * m + j for j in range(m))
    o = C.mesh('Climbing spine carved precast', V, light + dark + [fs_bottom, fs_top], 'rock', 'climbing spine')
    o.data.materials.append(C.MATS['rock2'])                       # one closed solid, two stones
    for poly in o.data.polygons:
        poly.material_index = 1 if len(light) <= poly.index < len(light) + len(dark) else 0
    return o


def cleft_boulder(name, cx, cy, z0, rx, ry, rz, seed, role='granite', sink=.15, rot=0., planes=3, flat_top=False, tilt=0.):
    """Granite boulder: a convex hull of jittered points on a flat-topped ellipsoid, cut by `planes` planar cleavage
    faces (points beyond a plane are projected onto it), flat-shaded so the edges stay crisp; never pointed. With
    flat_top the crown is sheared level, and `tilt` leans the whole stone."""
    rnd = random.Random(seed)
    c, sn = math.cos(rot), math.sin(rot)
    pts = []
    N = 14
    for i in range(N):
        zf = 1 - 2 * (i + .5) / N; r = math.sqrt(max(0., 1 - zf * zf)); a = i * 2.39996 + rnd.uniform(-.25, .25)
        k = rnd.uniform(.86, 1.04)
        pts.append([rx * k * r * math.cos(a), ry * k * r * math.sin(a), rz * (.5 + .5 * max(-1., min(.82, zf * k)))])
    for _ in range(planes):                                             # cleavage planes
        ph = rnd.uniform(0, 2 * math.pi); el = rnd.uniform(-.2, .7)
        n = (math.cos(ph) * math.cos(el), math.sin(ph) * math.cos(el), math.sin(el))
        off = rnd.uniform(.35, .6) * (abs(n[0]) * rx + abs(n[1]) * ry + abs(n[2]) * rz * .5) * .8
        for p in pts:
            q = (p[0] * n[0] + p[1] * n[1] + (p[2] - rz * .5) * n[2]) - off
            if q > 0:
                p[0] -= q * n[0]; p[1] -= q * n[1]; p[2] -= q * n[2]
    if flat_top:
        top = rz * rnd.uniform(.82, .95)
        for p in pts:
            p[2] = min(p[2], top)
    if tilt:
        for p in pts:
            p[0] += tilt * (p[2] - rz * .5)
    base = -sink
    out = [(cx + p[0] * c - p[1] * sn, cy + p[0] * sn + p[1] * c, z0 + max(base, p[2])) for p in pts]
    for a in range(6):
        tt = a * math.tau / 6; k = rnd.uniform(.78, .9)
        x, y = rx * k * math.cos(tt), ry * k * math.sin(tt)
        out.append((cx + x * c - y * sn, cy + x * sn + y * c, z0 + base))
    hull = _Hull(out)
    used = sorted(set(i for f in hull.simplices for i in f)); idx = {v: j for j, v in enumerate(used)}
    return C.mesh(name, [out[i] for i in used], [tuple(idx[i] for i in f) for f in hull.simplices], role, 'boulders')


STONES = []


def lumpy_boulder(name, seed, role, lat=5, lon=8, cuts=5):
    """Unit granite boulder (v006): a lumpy, slightly squashed sphere (2 wide, 1 tall, base at 0) of broad flat facets,
    with two planar cleavage cuts; rounded overall mass, no pointed apex."""
    rnd = random.Random(seed); nz = _PkNoise(seed, 1.0)
    pts = []
    for i in range(lat + 1):
        th = math.pi * i / lat
        for j in range(lon if 0 < i < lat else 1):
            ph = 2 * math.pi * (j + (.5 if i % 2 else 0.)) / lon
            ux, uy, uz = math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)
            k = 1 + .24 * nz(ux * 1.9, uy * 1.9, uz * 1.9)
            pts.append([ux * k, uy * k * rnd.uniform(.9, 1.0), .5 + .5 * uz * k])
    for _ in range(cuts):
        ph = rnd.uniform(0, 2 * math.pi); el = rnd.uniform(-.1, .5)
        n = (math.cos(ph) * math.cos(el), math.sin(ph) * math.cos(el), math.sin(el))
        off = rnd.uniform(.44, .68)
        for p in pts:
            q = p[0] * n[0] + p[1] * n[1] + (p[2] - .5) * n[2] - off
            if q > 0:
                p[0] -= q * n[0]; p[1] -= q * n[1]; p[2] -= q * n[2]
    pts = [(p[0], p[1], max(-.1, p[2] - .06)) for p in pts]
    hull = _Hull(pts)
    used = sorted(set(i for f in hull.simplices for i in f)); idx = {v: j for j, v in enumerate(used)}
    return C.mesh(name, [pts[i] for i in used], [tuple(idx[i] for i in f) for f in hull.simplices], role, 'boulders')


def stone_protos(n=6):
    """v006: six lumpy rounded-angular granite prototypes in a light grey-beige, shared as mesh datablocks; every
    roof, plaza and spine-foot boulder is a linked instance with its own scale, spin and lean (one mesh, many nodes)."""
    roles = ('granite', 'granite2', 'granite3')
    for k in range(n):
        o = lumpy_boulder(f'Stone prototype {k}', 500 + 11 * k, roles[k % 3])
        me = o.data
        C.bpy.data.objects.remove(o, do_unlink=True)
        STONES.append(me)


def stone(name, x, y, z, rx, ry, rz, k, rot=0., tilt=0.):
    """A linked instance of stone prototype k at (x, y) seated on z (the prototype's flat base is sunk 0.1 x rz)."""
    me = STONES[k % len(STONES)]
    o = C.bpy.data.objects.new(name, me)
    C.bpy.context.collection.objects.link(o)
    z = z + .06 * rz                                                    # the prototype's base is sunk 0.1 x rz: seat it 4 cm x rz down
    low = z - .1 * rz - math.sin(tilt) * max(rx, ry)
    if low < 0:                                                         # never below grade
        z -= low - .002
    o.location = (x, y, z); o.rotation_euler = (tilt * math.cos(rot), tilt * math.sin(rot), rot); o.scale = (rx, ry, rz)
    role = me.materials[0]['cityprompt_semantic_role']
    for key, v in (('rlasm_building_object', True), ('rlasm_method', C.METHOD), ('cityprompt_semantic_role', role),
                   ('cityprompt_lego_module', 'boulders'), ('representation_kind', 'architectural_clay'),
                   ('native_geometry_only', True), ('rlasm_instance', True)):
        o[key] = v
    return o


def round_boulder(name, cx, cy, z0, rx, ry, rz, seed, role='granite', sink=.1, lat=9, lon=16):
    """Rounded granite boulder (v003): a smooth-shaded squashed sphere with low-frequency lumps, its bottom flattened
    and sunk `sink` below z0; never pointed."""
    rnd = random.Random(seed); nz = _PkNoise(seed, 1.0)
    vs = []
    base = z0 - sink
    for i in range(lat + 1):
        th = math.pi * i / lat
        for j in range(lon if 0 < i < lat else 1):
            ph = 2 * math.pi * j / lon
            ux, uy, uz = math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)
            k = 1 + .2 * nz(ux * 2.2, uy * 2.2, uz * 2.2) + .07 * nz(ux * 5.0 + 3, uy * 5.0, uz * 5.0)
            vs.append((cx + rx * k * ux, cy + ry * k * uy, max(base, z0 + rz * .5 + rz * .5 * k * uz)))
    fs = []
    top, bot = 0, len(vs) - 1
    def ring(i): return 1 + (i - 1) * lon
    for j in range(lon):
        fs.append((top, ring(1) + (j + 1) % lon, ring(1) + j))
        fs.append((bot, ring(lat - 1) + j, ring(lat - 1) + (j + 1) % lon))
    for i in range(1, lat - 1):
        for j in range(lon):
            a, b2 = ring(i) + j, ring(i) + (j + 1) % lon
            c, d = ring(i + 1) + (j + 1) % lon, ring(i + 1) + j
            fs.append((a, b2, c, d))
    o = C.mesh(name, vs, fs, role, 'boulders')
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def boulder(name, cx, cy, z0, rx, ry, rz, seed, role='granite', sink=.06):
    """Faceted granite boulder: convex hull of jittered points on an ellipsoid, flat bottom sunk `sink` below z0."""
    rnd = random.Random(seed)
    pts = []
    N = 22
    for i in range(N):
        zf = 1 - 2 * (i + .5) / N; r = math.sqrt(max(0., 1 - zf * zf)); a = i * 2.39996 + rnd.uniform(-.3, .3)
        k = rnd.uniform(.78, 1.05)
        pts.append((cx + rx * k * r * math.cos(a), cy + ry * k * r * math.sin(a), z0 + rz * (.42 + .58 * zf * k)))
    base = z0 - sink
    pts = [(x, y, max(base, z)) for x, y, z in pts]
    for a in range(10):                                                  # footprint ring at the base
        t = a * math.tau / 10 + rnd.uniform(-.1, .1); k = rnd.uniform(.82, .95)
        pts.append((cx + rx * k * math.cos(t), cy + ry * k * math.sin(t), base))
    hull = _Hull(pts)
    used = sorted(set(i for f in hull.simplices for i in f)); idx = {v: j for j, v in enumerate(used)}
    vs = [pts[i] for i in used]
    fs = [tuple(idx[i] for i in f) for f in hull.simplices]
    return C.mesh(name, vs, fs, role, 'boulders')


def balconies():
    """Rest-station balconies east of the spine: slab spanning spine, notch wall and east wing, stepping 1 m past the
    wing; copper slab edge, timber deck and soffit, steel picket railing (front, oblique, top)."""
    b = Batch()
    for i in BAL_FLOORS:
        z = FLOORS[i]
        x0, x1 = SPX[1] - .55, NOTCH[1] + .02                        # v006: the slab is let into the carved east face
        b.box('concrete', (x0 + x1) / 2, (SPY0 + .3 + YN + .03) / 2, z - .1, x1 - x0, YN + .03 - SPY0 - .3, .26)   # into the rock and walls
        b.box('concrete', (SPX[1] + .03 + x1) / 2, (BAL_Y + SPY0 + .3) / 2, z - .1, x1 - SPX[1] - .03, SPY0 + .3 - BAL_Y, .26)   # v007: clear of the spine front
        b.box('copper', SPX[1], (BAL_Y - .06 + SPY0) / 2, z - .13, .06, SPY0 - BAL_Y + .06, .46)                 # west end fascia
        b.box('steel', SPX[1] + .1, (BAL_Y + .07 + SPY0 - .05) / 2, z + 1.08, .06, SPY0 - .05 - BAL_Y - .07, .05)   # west end rail
        for k in range(1, 6):
            b.box('steel', SPX[1] + .1, BAL_Y + .07 + (SPY0 - .05 - BAL_Y - .07) * k / 6, z + .62, .018, .018, .9)
        b.box('concrete', (NOTCH[1] + .021 + BAL_X1) / 2, (BAL_Y + Y0 + .02) / 2, z - .1, BAL_X1 - NOTCH[1] - .021, Y0 + .02 - BAL_Y, .26)
        b.box('timber', (SPX[1] + .06 + NOTCH[1] - .05) / 2, (BAL_Y + .03 + YN - .08) / 2, z + .045, NOTCH[1] - .11 - SPX[1], YN - .08 - BAL_Y - .03, .03)
        b.box('timber', (NOTCH[1] - .05 + BAL_X1 - .05) / 2, (BAL_Y + .03 + Y0 - .03) / 2, z + .045, BAL_X1 - NOTCH[1], Y0 - .03 - BAL_Y - .03, .03)
        b.box('copper', (SPX[1] - .03 + BAL_X1) / 2, BAL_Y - .03, z - .13, BAL_X1 - SPX[1] + .05, .06, .46)              # slab edge (deeper copper fascia)
        b.box('copper', BAL_X1 + .03, (BAL_Y + Y0) / 2, z - .13, .06, Y0 - BAL_Y + .06, .46)
        b.box('soffit', (SPX[1] + .06 + NOTCH[1] - .05) / 2, (BAL_Y + .1 + YN - .1) / 2, z - .245, NOTCH[1] - .11 - SPX[1], YN - BAL_Y - .2, .03)  # soffit
        b.box('soffit', (NOTCH[1] - .05 + BAL_X1 - .05) / 2, (BAL_Y + .1 + Y0 - .1) / 2, z - .245, BAL_X1 - NOTCH[1], Y0 - BAL_Y - .2, .03)
        ry = BAL_Y + .07
        b.box('steel', (SPX[1] + .07 + BAL_X1) / 2, ry, z + 1.08, BAL_X1 - SPX[1] - .07, .06, .05)                                    # top rail
        b.box('steel', (SPX[1] + .07 + BAL_X1) / 2, ry, z + .16, BAL_X1 - SPX[1] - .07, .04, .04)
        x0 = SPX[1] + .07
        n = int((BAL_X1 - x0) / .2)
        for k in range(n + 1):
            b.box('steel', x0 + .05 + (BAL_X1 - x0 - .1) * k / n, ry, z + .62, .018, .018, .9)
        for k in range(0, n + 1, 7):
            b.box('steel', x0 + .05 + (BAL_X1 - x0 - .1) * k / n, ry, z + .55, .05, .05, 1.06)
        rx = BAL_X1 - .07
        b.box('steel', rx, (ry + Y0 - .02) / 2, z + 1.08, .06, Y0 - .02 - ry, .05)
        for k in range(1, 5):
            b.box('steel', rx, ry + (Y0 - .02 - ry) * k / 5, z + .62, .018, .018, .9)
    b.flush('balconies')


def canopy():
    """White canopy over the west wing's shopfronts, on the wing face (front, oblique, top)."""
    x0, x1, yf, zt = CANOPY
    b = Batch()
    b.box('canopy', (x0 + x1) / 2, (yf + Y0 - FIN_D) / 2, zt - .45, x1 - x0, Y0 - FIN_D - yf, .9)
    b.box('canopy', (x0 + x1) / 2, (Y0 - FIN_D + Y0 + .01) / 2 + .0005, zt - .45 - .0005, x1 - x0, FIN_D + .01, .899)
    b.box('bronze', (x0 + x1) / 2, yf - .03, zt - .3, x1 - x0 + .04, .08, .5)                   # dark bronze fascia band
    b.box('canopy', x0 + .45, (yf + 1.4 + Y0 - FIN_D) / 2, zt - .45 - .001, .9, Y0 - FIN_D - yf - 1.4, .898)      # west return
    b.box('bronze', x0 + .45, (yf + 1.4 + Y0) / 2, zt - .3, .96, Y0 - yf - 1.4, .5)
    b.box('canopy', (NOTCH[0] + T + SPX[0] - .02) / 2, (Y0 - .01 + YN - .02) / 2, zt - .45, SPX[0] - .02 - NOTCH[0] - T, YN - .01 - Y0, .9)   # v007: runs to the spine
    for k in range(9):                                                         # downlights in the soffit
        b.box('coping', x0 + 1.4 + (x1 - x0 - 2.4) * k / 8, (yf + Y0) / 2, zt - .905, .5, .5, .012)
    b.flush('canopy')


def floors_and_inside():
    i = T + .01
    plan = [(X0 + i, Y0 + i), (NOTCH[0] - i, Y0 + i), (NOTCH[0] - i, YN + i), (NOTCH[1] + i, YN + i), (NOTCH[1] + i, Y0 + i),
            (X1 - i, Y0 + i), (X1 - i, Y1 - i), (X0 + i, Y1 - i)]
    C.prism('Ground floor slab', plan, 'z', 0.0, .15, 'floor', 'inside')
    for k, z in enumerate(FLOORS + [ROOF]):
        C.prism(f'Floor slab {k}', plan, 'z', z - .3, z, 'floor' if z < ROOF else 'roof', 'inside')
    C.box('Core', (0.0, 5.5, ROOF / 2), (12.0, 7.0, ROOF - .02), 'core', 'core', 0)
    b = Batch()
    for z0, z1 in [(.15, BASE - .3)] + [(z, z + FH - .3) for z in FLOORS]:
        b.box('interior', -15.5, 4.5, (z0 + z1) / 2, 18.0, .16, z1 - z0)          # back partitions
        b.box('interior', 15.5, 4.5, (z0 + z1) / 2 + .001, 18.0, .16, z1 - z0 - .002)
    b.flush('partitions')
    for k, z in enumerate([.15] + FLOORS):
        h = (BASE - .15 if k == 0 else FH) - .5
        for x, y in ((-17.0, -7.5), (-4.0, -5.0), (8.5, -4.5), (19.0, -7.5), (-17.0, 8.5), (18.0, 8.5)):
            C.qa_room_light(f'Floor {k} {x:+.0f} {y:+.0f}', (x, y, z + h), 34 if k else 110, 5.0)
    C.qa_room_light('Amenity room west', (-9.0, 2.0, RBTOP - 1.2), 30, 6.0)
    C.qa_room_light('Amenity room east', (8.0, 2.0, RBTOP - 1.2), 30, 6.0)
    zf = FLOORS[5]
    for x in (-22.5, -19.0, -15.5, -12.0):
        for y in (-10.5, -7.0):
            A.desk(x, y, zf)
    for x in (-18.0, -11.0):
        A.sofa(x, -3.0 + 4.0, .15)
    C.box('Gym reception', (6.2, -3.4, .15 + .55), (3.2, .8, 1.1), 'timber', 'lobby', 0)
    C.CONTACTS.append(dict(name='Tower floors, core and partitions inside the curtain wall', roof_m=ROOF))


# ---- roof terrace ----

def terrace():
    """Paved U-shaped terrace inside the parapet: L-shaped raised beds along the parapet, paths, granite boulders and
    planting with the shared kit (front, oblique, top)."""
    zp = ROOF + .08
    b = Batch()
    i = T - .02                                                       # paving laps 2 cm into the parapet carriers
    r2 = RB[2] + .02
    regions = [(X0 + i, NOTCH[0] - i, Y0 + i, r2), (NOTCH[1] + i, X1 - i, Y0 + i, r2),
               (NOTCH[0] - i, SPX[0], YN + i, r2), (SPX[1], NOTCH[1] + i, YN + i, r2), (SPX[0], SPX[1], SPY1, r2),
               (X0 + i, RB[0] + .02, r2, Y1 - i), (RB[1] - .02, X1 - i, r2, Y1 - i)]
    for x0, x1, y0, y1 in regions:
        b.box('paver', (x0 + x1) / 2, (y0 + y1) / 2, ROOF + .04, x1 - x0, y1 - y0, .08)
    b.flush('terrace paving')
    # Paving joints (top, oblique): a 1.2 m grid of flag joints over every paved region.
    j = Batch()
    for x0, x1, y0, y1 in regions:
        for k in range(1, int((x1 - x0) / 1.2) + 1):
            j.box('paver2', x0 + (x1 - x0) * k / (int((x1 - x0) / 1.2) + 1), (y0 + y1) / 2, zp + .0015, .025, y1 - y0 - .1, .003)
        for k in range(1, int((y1 - y0) / 1.2) + 1):
            j.box('paver2', (x0 + x1) / 2, y0 + (y1 - y0) * k / (int((y1 - y0) / 1.2) + 1), zp + .0016, x1 - x0 - .1, .025, .0032)
    j.flush('terrace joints')
    soil = ROOF + .36
    kit = KIT
    P = PROTOS
    # v004: L-shaped beds wrap each wing corner (top, oblique); boulders sit in them 1-2 m apart.
    beds = {
        'L': [(X0 + .45, Y1 - .45), (X0 + .45, Y0 + .45), (NOTCH[0] - .9, Y0 + .45), (NOTCH[0] - .9, Y0 + 4.1),
              (RB[0] - 3.9, Y0 + 4.1), (RB[0] - 3.9, Y1 - .45)],
        'R': [(X1 - .45, Y0 + .45), (X1 - .45, Y1 - .45), (RB[1] + 4.6, Y1 - .45), (RB[1] + 4.6, Y0 + 4.1),
              (NOTCH[1] + .9, Y0 + 4.1), (NOTCH[1] + .9, Y0 + .45)],
    }
    for k, poly in beds.items():
        pk_bed(f'Terrace bed {k}', poly, soil, kerb=.16, kerb_top=soil + .06, kerb_bottom=zp - .03, kerb_role='concrete', kit=kit)
    # Measured on the source front and oblique: a tight cluster of six big stones on each wing's street corner
    # (2.4-3.8 m tall, 0.3-0.6 m apart, two upright slabs), one more along the street edge and two down the side
    # strip; the tallest rise ~2.5 m over the coping.
    def seat(x, y):
        return soil if any(_PkPolygon(p).contains(_pksh.points(x, y)) for p in beds.values()) else zp

    # Measured on the source oblique, front and top: two or three irregular groups per wing with 1-3 m gaps,
    # a mix of tall standing slabs, flat-topped blocks and tilted stones, two or three of them out in the paving.
    # v006 (source front, oblique, top): clusters of large lumpy granite boulders on each wing corner, 2.5-3.4 m
    # across and 1.8-2.8 m tall, a couple leaning, more spaced along the street edge and side strip.
    cluster = [(2.6, 2.3, 1.55, 1.3, 2.6, 0), (5.8, 2.0, 1.3, 1.1, 2.1, 1), (2.5, 5.6, 1.45, 1.25, 2.4, 2), (5.4, 5.1, 1.0, .9, 1.6, 3),
               (9.4, 2.2, 1.35, 1.15, 2.2, 4), (2.6, 9.4, 1.2, 1.0, 2.7, 5), (13.6, 2.3, 1.4, 1.2, 2.1, 1), (2.5, 15.0, 1.3, 1.1, 2.2, 3)]
    n = 0
    for side in (-1, 1):
        xo = X0 if side < 0 else X1
        for dx, dy, rx, ry, rz, k in cluster:
            x, y = xo - side * (dx + .9), Y0 + dy + .9                # v007: >= 0.6 m clear of the parapet
            low = n % 3 == 1                                             # v008: a third lie low and wide
            stone(f'Terrace boulder {n}', x, y, seat(x, y), rx * (1.3 if low else 1.2), ry * (1.3 if low else 1.2), rz * (.85 if low else 1.6), k,
                  rot=(n * 1.37) % math.pi, tilt=.26 if k == 5 else .12 if low else .08 if k == 3 else 0.)
            kit.add_obstacle(_PkPolygon(pk_ellipse(x, y, max(rx, ry) * 1.26, max(rx, ry) * 1.26)), rz)
            n += 1
    fill_beds(kit, P, beds, soil, 55, spacing=.72)
    for k, poly in beds.items():
        groundcover(f'Terrace bed {k} groundcover', poly, soil, kerb=.16, height=.05, bump=.02, wave=.6, grid=.9, role='bedgreen',
                    seed=90 + ord(k[0]), dots=(('pk_yellow', 'pk_yellow2'), 2.5, .03))
    return kit


def protos(kit):
    """Roof and plaza planting: feather reed grass with plumes, a low fountain grass, blue fescue and two small shrubs."""
    P = {}
    P['reed'] = arching_grass(kit, 'sp_feather_reed', blades=44, height=.6, width=.016, role='pk_blade', plume_role='pk_plume',
                              plumes=7, plume_height=1.7, seed=11)
    P['fountain'] = arching_grass(kit, 'sp_fountain_grass', blades=40, height=.5, width=.014, role='pk_leaf2', seed=21)
    P['fescue'] = arching_grass(kit, 'sp_blue_fescue', blades=34, height=.24, width=.011, role='pk_blade_blue', crown_role='pk_crown_blue', seed=13)
    P['shrub'] = shrub_mass(kit, 'sp_shrub', radius=.5, height=.7, lobes=5, seed=19)
    P['shrub2'] = shrub_mass(kit, 'sp_shrub_b', radius=.35, height=.5, lobes=4, role='pk_leaf', role2='pk_leaf_light', seed=23)
    P['shrub3'] = shrub_mass(kit, 'sp_shrub_dark', radius=.65, height=.8, lobes=6, role='pk_leaf_dark', role2='pk_leaf_dark', seed=29)
    return P


def fill_beds(kit, P, beds, soil, seed, spacing=.62, shrubby=False):
    mix = [('reed', 1.0), ('fountain', 1.0), ('fescue', .7), ('shrub', .45), ('shrub2', .5)]
    if shrubby:                                                         # the plaza beds: dark shrub masses with grass clumps
        mix = [('shrub3', 1.8), ('shrub', 1.3), ('fountain', .6), ('reed', .3)]
    rnd = random.Random(seed)
    fields = [_PkNoise(seed + 17 * i, 2 * math.pi / 3.0) for i in range(len(mix))]
    for name, poly in beds.items():
        reg = pk_region(poly, .16)
        for x, y in pk_scatter(reg, spacing, margin=PK_CLEAR, seed=seed + ord(name[0])):
            order = sorted(range(len(mix)), key=lambda i: -(fields[i](x, y) + 1.4 * math.log(mix[i][1])))
            p = P[mix[order[0]][0]]
            kit.place_in(p, x, y, soil, rnd.uniform(0, math.tau), rnd.uniform(.9, 1.2) * (1.35 if shrubby else 1.), shrink=(1., .85, .7, .55, .45))


# ---- plaza, streets and context ----

def site():
    zw, zs = .12, .04
    S0 = X0 - SIDE; S1 = X1 + SIDE; ST = 13.0; FAR = 4.0; N = Y1 + 12.0
    for name, x0, x1, y0, y1, role, top in (
            ('Plaza', S0, S1, CURB, Y0, 'plaza', zw), ('Notch paving', NOTCH[0], NOTCH[1], Y0, YN, 'plaza', zw),
            ('West sidewalk', S0, X0, Y0, N, 'paver', zw),
            ('East sidewalk', X1, S1, Y0, N, 'paver', zw), ('North service court', X0, X1, Y1, N, 'paver2', zw),
            ('South street', -95.0, 95.0, CURB - ST, CURB, 'asphalt', zs), ('West street', S0 - ST, S0, CURB, 75.0, 'asphalt', zs),
            ('East street', S1, S1 + ST, CURB, 75.0, 'asphalt', zs), ('North lane', S0, S1, N, N + 7.0, 'asphalt', zs),
            ('Far south sidewalk', -95.0, 95.0, CURB - ST - FAR, CURB - ST, 'paver', zw),
            ('Far west sidewalk', S0 - ST - FAR, S0 - ST, CURB, 75.0, 'paver', zw), ('Far east sidewalk', S1 + ST, S1 + ST + FAR, CURB, 75.0, 'paver', zw),
            ('North far walk', S0, S1, N + 7.0, N + 10.0, 'paver', zw)):
        C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, top / 2), (x1 - x0, y1 - y0, top), role, 'site', 0)
    b = Batch()
    kz = zw + .015
    for a, c in ((S0 - .2, S1 + .2), (-95.0, S0 - ST - .2), (S1 + ST + .2, 95.0)):                 # curbs, 1.5 cm over the walks, 2 cm proud
        b.box('kerb', (a + c) / 2, CURB + .09, kz / 2, c - a, .22, kz)
    b.box('kerb', 0.0, CURB - ST - .09, kz / 2 + .0005, 190.0, .22, kz - .001)
    for x, s in ((S0, 1), (S1, -1), (S0 - ST, -1), (S1 + ST, 1)):
        segs = ((CURB + .2, N), (N + 7.0, 75.0)) if x in (S0, S1) else ((CURB + .2, 75.0),)
        for ya, yb in segs:
            b.box('kerb', x + s * .09, (ya + yb) / 2, kz / 2 + .001, .22, yb - ya, kz - .002)
    for k in range(8):                                                                       # zebra crossings
        b.box('line', S0 - ST + 1.0 + k * 1.55, CURB + 2.4, zs + .004, .8, 3.0, .008)
        b.box('line', S1 + 1.0 + k * 1.55, CURB + 2.4, zs + .004, .8, 3.0, .008)
        b.box('line', S0 - 2.4, CURB - 1.0 - k * 1.55, zs + .0042, 3.0, .8, .0084)
        b.box('line', S1 + 2.4, CURB - 1.0 - k * 1.55, zs + .0042, 3.0, .8, .0084)
    for k in range(-14, 15):
        if abs(k * 6.0) < 40:
            continue
        b.box('line', k * 6.0, CURB - ST / 2, zs + .004, 3.0, .12, .008)
    for k in range(9):
        b.box('line', S0 - ST / 2, 6.0 + k * 7.0, zs + .004, .12, 3.0, .008)
        b.box('line', S1 + ST / 2, 6.0 + k * 7.0, zs + .004, .12, 3.0, .008)
    # plaza paving joints (top view: large grey flags)
    for k in range(1, 12):
        y = CURB + .4 + k * (Y0 - CURB - .6) / 12
        b.box('paver2', 0.0, y, zw + .0015, S1 - S0 - .6, .03, .003)
    b.flush('paving')
    # Street-tree pits with young trees, lamp posts (front, oblique, top).
    pb = Batch()
    for x in (-27.0, -18.0, -9.0, 9.5, 18.5, 27.5):
        pb.box('kerb', x, CURB + 1.6, zw + .03, 1.5, 1.5, .06)
        pb.box('mulch', x, CURB + 1.6, zw + .065, 1.3, 1.3, .012)
        young_tree(x, CURB + 1.6, zw + .06, 4.2 + .3 * (x % 3))
    for y in (-6.0, 4.0):
        for x in (S0 + 1.2, S1 - 1.2):
            pb.box('kerb', x, y, zw + .03, 1.4, 1.4, .06)
            pb.box('mulch', x, y, zw + .065, 1.2, 1.2, .012)
            young_tree(x, y, zw + .06, 4.4)
    pb.flush('tree pits')
    for x, y in ((-30.0, CURB + .6), (-13.5, CURB + .6), (14.0, CURB + .6), (30.0, CURB + .6), (S0 + .5, 0.0), (S1 - .5, 0.0),
                 (S1 - .5, 12.0), (S0 + .5, 12.0)):
        lamp(x, y, zw)
    plaza_garden()
    context()


def young_tree(x, y, z, h):
    C.rod('Young tree trunk', (x, y, z - .04), (x, y, z + h * .6), .07, 'bark', 'street trees', 8)
    for a in (0.4, 2.5, 4.4):
        C.rod('Young tree limb', (x, y, z + h * .45), (x + .5 * math.cos(a), y + .5 * math.sin(a), z + h * .75), .035, 'bark', 'street trees', 6)
    A.foliage('Young tree crown', (x, y, z + h * .78), (1.1, 1.1, h * .26), role='tree', detail=2)
    A.foliage('Young tree crown', (x + .35, y - .2, z + h * .68), (.75, .75, h * .18), role='tree2', detail=2)


def lamp(x, y, z):
    C.rod('Lamp post', (x, y, z - .02), (x, y, z + 5.6), .07, 'lamp', 'street lamps', 10)
    C.box('Lamp base', (x, y, z + .25), (.3, .3, .5), 'lamp', 'street lamps', 0)
    C.box('Lamp head', (x, y, z + 5.7), (.9, .32, .2), 'lamp', 'street lamps', 0)
    C.box('Lamp lens', (x, y, z + 5.59), (.7, .22, .02), 'coping', 'street lamps', 0)


def crescent(cx, cy, a0, a1, r0, r1, sx=1.15, sy=.8, n=22):
    """Curved bed outline (CCW): an outer arc from a0 to a1 (degrees) and the inner arc back, on an ellipse scaled sx, sy."""
    out = []
    for k in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * k / n)
        out.append((cx + r1 * sx * math.cos(a), cy + r1 * sy * math.sin(a)))
    for k in range(n + 1):
        a = math.radians(a1 - (a1 - a0) * k / n)
        out.append((cx + r0 * sx * math.cos(a), cy + r0 * sy * math.sin(a)))
    return out


def plaza_garden():
    """Boulder garden at the spine foot (v002): one raised curved bed (0.45 m kerb) wrapping the west and south of the
    flared foot, split by a paved path that leads to the foot; one large granite boulder against the foot and a dozen
    smaller ones; the round planter to the east and the long planter to the west (top, front, oblique)."""
    kit = KIT
    fx, fy = (SPX[0] + SPX[1]) / 2, SPY0 - .8
    beds = {
        'A': (crescent(fx, fy, 172, 262, 4.8, 9.2, sy=.85), .50, .25, .57),
        'B': (crescent(fx, fy, 279, 352, 4.8, 8.6, sy=.85), .50, .25, .57),
        'G3': (pk_blob(18.0, Y0 - 7.2, 2.9, 2.2, seed=9, amp=.08), .36, .2, .46),
        'G4': (pk_rounded_rect(-17.5, Y0 - 8.0, 5.6, .9, r=.4), .36, .2, .46),
    }
    for k, (poly, soil, kerb, top) in beds.items():
        pk_bed(f'Plaza bed {k}', poly, soil, kerb=kerb, kerb_top=top, kerb_bottom=.06, kerb_role='kerb', kit=kit)

    def polar(a, r):
        return fx + r * 1.15 * math.cos(math.radians(a)), fy + r * .85 * math.sin(math.radians(a))
    # Measured on the source front base crop: one ~3 m stone against the foot, upright stones by the foot and
    # about twenty 0.6-1.5 m stones packed through both beds.
    rocks = [('A', 206, 5.9, 1.75, 1.5, 3.0), ('A', 184, 5.4, .7, .6, 1.9), ('A', 228, 5.5, .75, .6, 1.8), ('A', 194, 7.4, 1.0, .85, 1.1),
             ('A', 238, 7.4, 1.1, .9, 1.0), ('A', 254, 6.0, .75, .6, .85), ('A', 214, 8.4, .6, .55, .7), ('A', 175, 7.5, .7, .6, .75),
             ('A', 222, 7.0, .55, .5, .6), ('A', 200, 8.6, .5, .45, .55), ('A', 246, 8.5, .55, .5, .6), ('A', 186, 8.7, .45, .4, .5),
             ('A', 168, 6.4, .5, .45, .6), ('B', 290, 5.6, .75, .6, 1.7), ('B', 300, 7.1, 1.1, 1.0, 1.2), ('B', 322, 6.6, 1.0, .85, 1.0),
             ('B', 340, 5.8, .75, .6, .85), ('B', 312, 8.0, .6, .55, .65), ('B', 346, 7.6, .6, .55, .6), ('B', 284, 8.0, .5, .45, .55),
             ('B', 330, 8.2, .5, .45, .5), ('B', 306, 5.7, .5, .45, .6), ('G3', None, None, 1.35, 1.1, 1.25)]
    for k, (bed, a, r, rx, ry, rz) in enumerate(rocks):
        x, y = polar(a, r) if a is not None else (18.2, Y0 - 7.0)
        stone(f'Garden boulder {k}', x, y, beds[bed][1], rx, ry, rz, k + 2, rot=k * 1.3)
        kit.add_obstacle(_PkPolygon(pk_ellipse(x, y, max(rx, ry) * 1.05, max(rx, ry) * 1.05)), rz)
    rnd = random.Random(404); placed = [(polar(a, r) if a is not None else (18.2, Y0 - 7.0), max(rx, ry)) for bed, a, r, rx, ry, rz in rocks]
    m = 0
    for bed in ('A', 'B'):
        reg = pk_region(beds[bed][0], beds[bed][2] + .25)
        for x, y in pk_scatter(reg, 1.0, seed=31 + ord(bed)):
            r = rnd.uniform(.25, .45)
            if any(math.hypot(x - a, y - b) < r + q + .15 for (a, b), q in placed):
                continue
            stone(f'Garden cobble {m}', x, y, beds[bed][1], r, r * rnd.uniform(.75, .95), r * rnd.uniform(.7, 1.1), m + 5, rot=rnd.uniform(0, 3.1))
            kit.add_obstacle(_PkPolygon(pk_ellipse(x, y, r * 1.05, r * 1.05)), r)
            placed.append(((x, y), r)); m += 1
            if m >= 24:
                break
    for k, (poly, soil, kerb, top) in beds.items():
        fill_beds(kit, PROTOS, {k: poly}, soil, 77, spacing=.36, shrubby=True)
        groundcover(f'Plaza bed {k} groundcover', poly, soil, kerb=kerb, height=.07, bump=.03, wave=.6, grid=.6, role='pk_leaf_dark',
                    seed=150 + len(k) + ord(k[0]))


def ctx_block(b, x0, x1, y0, y1, h, role, faces=('s', 'e', 'w', 'n'), floor=3.3, win=1.6, glass='ctxglass', z0=0.0, piers=6.0):
    """Context massing: a block with a roof membrane and, on the named faces, one ribbon window per floor broken by
    piers every `piers` metres (proud by a few cm)."""
    b.box(role, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + h) / 2, x1 - x0, y1 - y0, h - z0)
    b.box('ctxroof', (x0 + x1) / 2, (y0 + y1) / 2, h + .03, x1 - x0 - .6, y1 - y0 - .6, .06)
    nf = int((h - 1.5) / floor)
    for f in faces:
        span = (x1 - x0) if f in 'sn' else (y1 - y0)
        n = max(1, int(span / piers))
        for j in range(1, nf):
            z = j * floor + .9 + win / 2
            for k in range(n):
                a, c = span * k / n + .5, span * (k + 1) / n - .5
                if f == 's':
                    b.box(glass, x0 + (a + c) / 2, y0 - .03, z, c - a, .08, win)
                elif f == 'n':
                    b.box(glass, x0 + (a + c) / 2, y1 + .03, z, c - a, .08, win)
                elif f == 'e':
                    b.box(glass, x1 + .03, y0 + (a + c) / 2, z, .08, c - a, win)
                else:
                    b.box(glass, x0 - .03, y0 + (a + c) / 2, z, .08, c - a, win)


def context():
    """Neighbours as simple massing: tan and red brick walk-ups across the west street, a white mid-rise behind,
    a white block and a glass tower across the east street, low brick blocks across the south street, and backdrop towers."""
    b = Batch()
    W0 = X0 - SIDE - 13.0 - 4.0 - .5                                   # west street frontage of the west blocks
    E0 = X1 + SIDE + 13.0 + 4.0 + .5
    ctx_block(b, W0 - 30.0, W0, -26.0, 2.0, 21.0, 'tan', faces=('e', 's'))
    ctx_block(b, W0 - 30.0, W0, 2.0, 30.0, 17.5, 'brick2', faces=('e',))
    ctx_block(b, -21.0, 21.0, Y1 + 22.5, Y1 + 46.0, 30.0, 'white', faces=('s',), glass='trim')
    ctx_block(b, E0, E0 + 18.0, -26.0, -4.0, 16.0, 'white', faces=('w', 's'))
    ctx_block(b, E0, E0 + 22.0, 16.0, 44.0, 92.0, 'ctxglass', faces=('w', 's'), floor=3.6, win=.8, glass='white', piers=30.0)
    ctx_block(b, E0 + 2.0, E0 + 32.0, CURB - 13.0 - 4.0 - 30.0, CURB - 13.0 - 4.5, 12.0, 'brick2', faces=('n', 'w'))
    ctx_block(b, W0 - 34.0, W0, CURB - 13.0 - 4.0 - 30.0, CURB - 13.0 - 4.5, 9.5, 'brick2', faces=('n', 'e'))
    ctx_block(b, W0 - 30.0, W0 - 10.0, 36.0, 58.0, 78.0, 'tan', faces=('e', 's'), floor=3.2)
    ctx_block(b, E0 + 10.0, E0 + 30.0, 40.0, 60.0, 98.0, 'ctxglass', faces=('w', 's'), floor=3.6, win=.8, glass='white', piers=30.0)
    ctx_block(b, -46.0, -24.0, 70.0, 92.0, 84.0, 'white', faces=('s', 'e'), floor=3.2)
    b.flush('context')


SUN = dict(strength=2.0, color=(1.0, .86, .66), source=(-150.0, -45.0, 62.0))    # v008: warm low key from the west-south-west (~22 deg)


def sun():
    """Review lighting only (lights are not exported): a warm sun low from the south-west, as in the sources."""
    C.bpy.ops.object.light_add(type='SUN', location=SUN['source'])
    o = C.bpy.context.object; o.name = 'QA sun'
    o.data.energy = SUN['strength']; o.data.color = SUN['color']; o.data.angle = math.radians(1.5)
    C.look_at(o, (0.0, 0.0, 0.0))


def build():
    global KIT, PROTOS
    sun()
    KIT = PlantKit('planting', instancing=INSTANCING)
    PROTOS = protos(KIT)
    stone_protos()
    site()
    tower()
    coping_and_liners()
    spine()
    balconies()
    canopy()
    floors_and_inside()
    # The plaza and the roof terrace overlap in plan: audit the plaza planting on its own, then give the terrace a
    # clean bed and obstacle register (the kit's clearance rule is planar).
    bad = KIT.audit(detail=True)
    if bad:
        raise RuntimeError(f'planting kit clearance rule (plaza): {len(bad)}: {bad[:12]}')
    KIT.placements, KIT.beds, KIT.obstacles = [], [], []
    terrace()
    KIT.flush()
    bad = KIT.audit(detail=True)
    if bad:
        raise RuntimeError(f'planting kit clearance rule: {len(bad)} placements cross a bed edge: {bad[:12]}')
    C.CONTACTS.append(dict(name='Spine, tower faces and canopy from grade; balconies carried by the spine, notch wall and east wing', top_m=RBTOP))


LIGHT_RIG = dict(key=(-160, -75, 80), fill=(110, -95, 125), rear=(-30, 130, 110), target=(0, -2, 30.0), gain=14.0)
