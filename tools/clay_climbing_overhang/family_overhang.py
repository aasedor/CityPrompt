"""The Overhang climbing building, authored from the locked catalogue views of
climbing_wall_building / variant_1 ("The Overhang": a recreation centre with a faceted timber climbing wall leaning
out over its plaza).

Read from the pixels (the three views were fitted together; the top view governs the plan): a white precast and
glass recreation centre on a corner block, 39 m on the south plaza and 36 m deep along a west street. The pool block
on the west is three storeys: a ground floor of recessed glazing behind white columns, two upper storeys of tall
recessed windows between white precast fins and spandrels, and a deep white parapet band; its roof is a deck with a
long infinity pool running north-south along the west edge, glass balustrades, a row of loungers along the pool and
a roof garden of raised planters, grasses and small trees at the north end (front, oblique, top). A one-storey white
penthouse stands on the middle of the roof, glazed towards the pool deck and solid to the north, with an air-handling
unit on its roof; a four-storey east block with a membrane roof, skylights and plant completes the plan (top,
oblique). On the south front the pool block shows a projecting white frame box holding two storeys of glass ribbons
over a recessed glazed ground floor with two pairs of entrance doors (front, oblique).
Beside it stands the climbing wall: a hollow, open-topped shell of honey-toned cross-laminated timber in folded
(origami) planes, 21 m tall. Its foot stands on the plaza up to 9 m in front of the facade; it leans east as it rises,
meeting the parapet of the pool block at a fold and reaching a rectangular rim, 13 m by 10 m with a light timber
fascia, that cantilevers about 10 m over the plaza and the ground-floor facade beside the pool block. The south-west
face is two facets (a sunlit upper facet over a lower one), the south face is a triangle widening from its foot, and
the east face overhangs the white facade below; dark and white climbing holds dot the faces, densest on the south
face, with three climbers (front, oblique, top). The open top shows the inner walls with white holds (top, front).
A grey granite plaza with two raised planters of tall ornamental grasses lies to the south; a concrete west sidewalk
with street trees and lamp posts, a west street with crossings, an east street with parked cars, and brick mid-rise
blocks and taller residential blocks around (front, oblique, top).
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-climbing-overhang'
X0, X1, Y0, Y1 = -23.0, 16.0, -18.0, 18.0             # the building (top view, fitted)
T = .3                                                # precast carrier depth
XP0, XP1 = -6.0, 5.5                                  # penthouse (x); the pool deck's east edge is XP0
XE = 5.5                                              # the four-storey east block starts here
G0 = .15                                              # ground floor over the plaza
F2, F3, F4 = 5.0, 9.4, 13.8                           # upper floor levels
PARA = 15.6                                           # pool block parapet top
DECK = 15.0                                           # pool deck surface
WATER = 15.25                                         # pool water (infinity edge on the west)
PH_TOP, PH_PARA = 19.0, 19.4                          # penthouse roof, parapet
EB_TOP, EB_PARA = 18.2, 18.6                          # east block roof, parapet
BOXX1 = -12.6                                         # the south frame box spans X0..BOXX1
FY = -17.8                                            # the climbing shell's back plane (laps 10 cm into the facade)
RIM = 21.0                                            # rim top of the climbing shell
# The climbing shell's outer corners (triangulated from the front and oblique views and the top view).
SH = dict(G=(-11.1, FY, 0.0), BW=(-17.8, -22.7, 0.0), BS=(-3.0, -26.5, 0.0), BN=(-6.0, FY, 0.0),
          KW=(-11.1, FY, PARA), KS=(-4.75, -27.55, 9.5), KX=(-6.3, -27.35, PARA),
          RNW=(-7.26, FY, RIM), RSW=(-6.04, -26.71, RIM), RSE=(6.22, -27.72, RIM), RNE=(4.37, FY, RIM))
SHELL_T = .35                                         # CLT shell thickness
TOP = RIM + .1
EPS = .002
PALETTE = dict(wall=(.86, .85, .82), precast=(.90, .89, .86), concrete2=(.70, .70, .68), frame=(.22, .24, .26),
    glass=(.15, .21, .25), interior=(.82, .79, .72), floor=(.60, .57, .52), timber=(.84, .48, .13), timber2=(.90, .64, .27),
    timber_in=(.76, .42, .11), hold=(.10, .10, .11), hold_w=(.91, .90, .86), mat=(.17, .19, .23), shirt=(.20, .60, .70),
    skin=(.78, .60, .47), harness=(.12, .12, .14), paving=(.63, .64, .64), paving2=(.53, .54, .55), granite=(.60, .60, .59),
    deck=(.80, .74, .64), coping=(.88, .86, .80), water=(.08, .52, .66), water2=(.06, .38, .50), membrane=(.86, .86, .84),
    mech=(.78, .78, .76), asphalt=(.26, .26, .27), curb=(.73, .73, .71), paint=(.93, .93, .91), soil=(.26, .20, .15),
    lounger=(.93, .93, .91), hardware=(.08, .08, .08), metal=(.55, .56, .57), brick=(.50, .25, .17), brick2=(.58, .32, .22),
    ctx=(.74, .72, .68), ctx2=(.62, .60, .57), stone=(.78, .74, .66), tree=(.53, .62, .22), tree3=(.66, .70, .16), tree2=(.40, .53, .19),
    bark=(.30, .24, .17), car1=(.56, .58, .61), car2=(.15, .15, .17), car3=(.76, .76, .77), planter=(.80, .79, .76))


def manifest(version):
    cams = G.camera_roster(X1 - X0 + 4.0, Y1 - Y0 + 4.0, PARA, [
        ('climbing_face', (3.0, -45.0, 8.0), (0.5, -27.6, 11.0), 32),            # the south face: holds, climbers, fascia
        ('wall_base_contact', (-25.0, -28.0, 1.7), (-11.0, -23.5, 1.4), 24),     # the shell's foot on the plaza
        ('rim_interior', (-1.0, -38.0, 42.0), (0.0, -22.6, 9.0), 38),            # down into the open top
        ('pool_deck', (-16.5, -16.0, 16.7), (-14.0, 6.0, 15.4), 22),             # the deck, pool, loungers and garden
        ('facade_close', (-31.0, -14.75, 11.5), (X0, -14.75, 9.5), 40),               # a west bay through both upper storeys
        ('architecture_close', (-31.0, -29.0, 11.5), (-20.5, Y0, 11.0), 38),     # the frame box corner and parapet band
        ('glass_close', (-17.8, -26.5, 9.4), (-17.8, Y0, 9.4), 38),              # the glass ribbons in the frame box
        ('interior', (-18.5, -12.3, 1.7), (-18.5, Y0, 2.4), 20),                 # the lobby looking out to the plaza
        ('plaza_planters', (-1.0, -41.0, 1.6), (-8.0, -31.0, .9), 28),           # the grass planters at eye level
        ('entrance', (-18.6, -29.0, 1.7), (-18.6, Y0, 2.3), 30)])                # the doors under the frame box
    for c in cams:                       # the locked front, oblique and top views are fitted to the source pixels
        c['whole'] = False
        c.pop('ortho_scale', None)
        if c['name'] == 'front':
            c.update(location=(-45.24, -52.34, 31.29), target=(-13.3, -14.34, 6.0), lens=35.0)
        elif c['name'] == 'front_corner':
            c.update(location=(-65.8, -71.99, 56.26), target=(-9.46, -9.1, 6.0), lens=51.57)
        elif c['name'] == 'top':
            c.update(location=(-5.65, -29.29, 64.45), target=(-3.55, -6.57, 6.0), lens=25.38)
        elif c['name'] == 'aerial':
            c.update(location=(48.0, -72.0, 56.0), target=(-3.0, -10.0, 8.0), lens=30)
        elif c['name'] == 'left_side':
            c.update(location=(-40.0, 0.0, 14.0), target=(X0, 0.0, 9.0), lens=13)
        elif c['name'] == 'right_side':
            c.update(location=(33.0, -38.0, 13.0), target=(8.0, -16.0, 9.0), lens=22)
        elif c['name'] == 'rear':
            c.update(location=(-3.5, 33.5, 15.0), target=(-3.5, Y1, 10.0), lens=12)
        elif c['name'] == 'rear_side':
            c.update(location=(-48.0, 62.0, 62.0), target=(-3.0, 0.0, 8.0), lens=30)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='climbing_wall_building/variant_1 (The Overhang: recreation centre with a cantilevered faceted timber climbing wall)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=RIM),
            observed_storeys=3, storey_programme='three-storey pool block (lobby, gym floors) with a one-storey penthouse lounge and a four-storey east block',
            plan='39 m by 36 m corner building (top view) on a south plaza, a west street and an east street; the climbing shell stands on the plaza at the south front',
            facade='white precast: west front of ten bays of tall recessed windows between fins and spandrels over a recessed glazed ground floor; south front: a projecting white frame box of two glass ribbons over recessed ground-floor glazing with two pairs of doors; a deep parapet band; white facade with glass ribbons under the overhang',
            climbing_wall='hollow open-topped shell of honey CLT in folded planes: foot on the plaza, south-west face in two facets with a fold at the parapet, triangular south face, overhanging east face, light timber rim fascia, dark and white holds, three climbers',
            roof='pool deck with an infinity pool along the west edge, glass balustrades, loungers and a roof garden of planters and small trees; penthouse with a glazed pool side and an air-handling unit; east block membrane roof with skylights and plant',
            streetscape='granite plaza with two raised planters of ornamental grasses and steps to the south sidewalk; west sidewalk with street trees in pits and lamp posts; west and east streets with crossings and parked cars; brick mid-rise and residential blocks around',
            levels_m=[G0, F2, F3, F4, DECK], roof_m=dict(parapet=PARA, penthouse=PH_TOP, east_block=EB_TOP, rim=RIM),
            inferred='interiors, the north and east fronts and the hollow interior follow the visible grammar; the shell corners were triangulated from the fitted views; metric dimensions are authored teaching assumptions'),
        roof_contract=dict(type='pool deck with infinity pool inside glass balustrades; penthouse flat roof; east block membrane roof', datum_m=DECK, crowns_m=[PH_PARA, RIM]),
        identity_contract=dict(owner='white precast and glass recreation centre with a rooftop infinity pool and a dramatic faceted honey-timber climbing wall leaning out over its granite plaza'),
        material_contract=dict(profile='source-palette clay: white precast, dark glazing frames, honey CLT with a lighter rim fascia, dark and white holds, turquoise water, grey granite and pavers', textured_keeper=False),
        programme_contract=dict(storeys=3, ground='lobby and climbing gym entrance', upper='gym floors, penthouse lounge, pool deck'),
        contact_contract=['Grade-zero plaza, sidewalks and streets', 'Climbing shell foot sunk into the plaza and its back plane lapped into the facade', 'Precast walls from grade', 'Pool deck and roofs inside parapets'],
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
# ---- The Overhang climbing building ----
import random


def cyl(b, role, cx, cy, z0, z1, r, n=12):
    """Upright n-gon shaft added to a Batch."""
    frustum(b, role, cx, cy, z0, z1, r, r, n)


def frustum(b, role, cx, cy, z0, z1, r0, r1, n=12):
    """Upright n-gon frustum (radius r0 at z0, r1 at z1) added to a Batch."""
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


def qa_light(name, loc, power, size):
    """Neutral inspection light that illuminates the rooms but is hidden from camera and glossy rays."""
    obj = C.qa_room_light(name, loc, power, size)
    obj.visible_camera = False
    obj.visible_glossy = False
    return obj


def fbox(b, role, axis, c, out, s0, s1, z0, z1, d0, d1):
    """Box in facade coordinates: s along the facade, z up, d outward from the facade plane (axis 'x': plane y = c,
    'y': plane x = c; out = +1 or -1 is the outward direction along the plane normal)."""
    if s1 - s0 < 1e-4 or z1 - z0 < 1e-4:
        return
    a, e = sorted((c + out * d0, c + out * d1))
    if axis == 'x':
        b.box(role, (s0 + s1) / 2, (a + e) / 2, (z0 + z1) / 2, s1 - s0, e - a, z1 - z0)
    else:
        b.box(role, (a + e) / 2, (s0 + s1) / 2, (z0 + z1) / 2, e - a, s1 - s0, z1 - z0)


def glazed(b, axis, c, out, s0, s1, z0, z1, per, d=-.12, transoms=()):
    """A glazed opening between solid members: a pane `d` behind the facade plane (its edges buried 3 cm in the members
    around it), perimeter frame bars, mullions every `per` and optional transoms, all 6-8 cm deep at their own depths."""
    fbox(b, 'glass', axis, c, out, s0 - .03, s1 + .03, z0 - .03, z1 + .03, d - .005, d + .005)
    for za, zb in ((z0, z0 + .07), (z1 - .07, z1)):
        fbox(b, 'frame', axis, c, out, s0, s1, za, zb, d - .03, d + .045)
    n = max(1, round((s1 - s0) / per))
    for k in range(n + 1):
        s = s0 + (s1 - s0) * k / n
        fbox(b, 'frame', axis, c, out, max(s0, s - .035), min(s1, s + .035), z0 + .07, z1 - .07, d - .028, d + .05)
    for zt in transoms:
        fbox(b, 'frame', axis, c, out, s0 + .07, s1 - .07, zt - .035, zt + .035, d - .025, d + .04)


def door_pair(b, axis, c, out, s, z0, z1, d):
    """Pair of glazed aluminium doors centred at s, set in a glazed screen at depth d; pulls on the outer face."""
    for k in (-1, 1):
        a0, a1 = s + (0 if k > 0 else -1.0), s + (1.0 if k > 0 else 0)
        fbox(b, 'frame', axis, c, out, a0, a0 + .09, z0, z1, d - .03, d + .03)
        fbox(b, 'frame', axis, c, out, a1 - .09, a1, z0, z1, d - .03, d + .03)
        fbox(b, 'frame', axis, c, out, a0 + .08, a1 - .08, z1 - .1, z1, d - .028, d + .028)
        fbox(b, 'frame', axis, c, out, a0 + .08, a1 - .08, z0, z0 + .22, d - .028, d + .028)
        fbox(b, 'glass', axis, c, out, a0 + .085, a1 - .085, z0 + .2, z1 - .08, d - .005, d + .005)
        fbox(b, 'hardware', axis, c, out, s + k * .14 - .02, s + k * .14 + .02, z0 + .7, z0 + 1.6, d + .03, d + .07)


# ---------------------------------------------------------------- precast fronts
def precast_front(b, axis, c, out, lo, hi, bays, levels, top, ground=True, fin_w=.55, ground_d=.6, room=4.2, cop_dz=0.0):
    """White precast front: full-height fins at the bay lines, spandrel bands at each floor, a parapet band up to
    `top`, tall recessed windows between them; a recessed glazed ground floor behind square columns. levels =
    [F2, F3, ...]; the last level is the base of the parapet band. cop_dz lowers this front's coping where it overlaps
    a neighbouring front's coping at a corner (no shared top faces)."""
    wb = (hi - lo) / bays
    fins = [lo + k * wb for k in range(bays + 1)]
    zb = levels[-1]
    for k, s in enumerate(fins):
        s0, s1 = max(lo, s - fin_w / 2), min(hi, s + fin_w / 2)
        fbox(b, 'precast', axis, c, out, s0, s1, levels[0] - .57, zb + .02, -.25, .42)
        if ground:
            fbox(b, 'precast', axis, c, out, s0 + .02, s1 - .02, 0.0, levels[0] - .5, -ground_d - .05, .08)
    for z in levels[:-1]:                                      # spandrels end 2 cm inside the end fins (no shared end faces)
        fbox(b, 'precast', axis, c, out, lo + .02, hi - .02, z - .55, z + .25, -.25, .38)
    fbox(b, 'precast', axis, c, out, lo - .02, hi + .02, zb, top - .05, -.25, .30)
    fbox(b, 'coping', axis, c, out, lo - .04, hi + .04, top - .06 + cop_dz, top + cop_dz, -.3, .34)
    for j, z in enumerate(levels[:-1]):
        z1 = levels[j + 1]
        for k in range(bays):
            s0, s1 = fins[k] + fin_w / 2, fins[k + 1] - fin_w / 2
            glazed(b, axis, c, out, s0, s1, z + .25, (z1 - .55) if j + 1 < len(levels) - 1 else zb, 1.4 if s1 - s0 > 2.2 else 9)
        fbox(b, 'interior', axis, c, out, lo + .3, hi - .3, z, z1, -room - .2, -room)
    if ground:
        for k in range(bays):
            s0, s1 = fins[k] + fin_w / 2 - .02, fins[k + 1] - fin_w / 2 + .02
            glazed(b, axis, c, out, s0, s1, G0, levels[0] - .5, 1.2, d=-ground_d, transoms=(3.3,))
        fbox(b, 'precast', axis, c, out, lo + .03, hi - .03, levels[0] - .55, levels[0] - .5, -ground_d - .3, -ground_d + .02)
        fbox(b, 'interior', axis, c, out, lo + .3, hi - .3, G0, levels[0] - .5, -room - 2.2, -room - 2.0)


def building_mass():
    """Floor slabs, roof slabs and the cores that stop views through the building."""
    b = Batch()
    for z in (F2, F3, F4):
        b.box('interior', (X0 + X1) / 2, (Y0 + Y1) / 2, z - .15, X1 - X0 - .5, Y1 - Y0 - .5, .3)
    b.box('floor', (X0 + X1) / 2, (Y0 + Y1) / 2, G0 / 2, X1 - X0 - .2, Y1 - Y0 - .2, G0)
    b.box('interior', (X0 + XP1) / 2, (Y0 + Y1) / 2, DECK - .32, XP1 - X0 - .5, Y1 - Y0 - .5, .4)        # pool block roof slab
    b.box('interior', (XE + X1) / 2, (Y0 + Y1) / 2, EB_TOP - .2, X1 - XE - .5, Y1 - Y0 - .5, .4)         # east block roof slab
    for x0, x1, y0, y1, top in ((-14.0, -4.0, -6.0, 8.0, DECK - .45), (6.0, 12.0, -6.0, 6.0, EB_TOP - .45)):   # cores
        b.box('interior', (x0 + x1) / 2, (y0 + y1) / 2, (G0 + top) / 2, x1 - x0, y1 - y0, top - G0)
    b.flush('building mass')


def fronts():
    """West, north and east precast fronts; the pool block's south frame box; the white south front under the
    climbing shell's overhang."""
    b = Batch()
    precast_front(b, 'y', X0, -1, Y0, Y1, 13, [F2, F3, F4], PARA)                                        # west front (13 bays)
    precast_front(b, 'y', X1, 1, Y0, Y1, 10, [F2, F3, F4, EB_TOP], EB_PARA)                              # east front (4 storeys)
    precast_front(b, 'x', Y1, 1, X0, XE, 8, [F2, F3, F4], PARA, cop_dz=-.01)                            # north front, pool block
    precast_front(b, 'x', Y1, 1, XE, X1, 3, [F2, F3, F4, EB_TOP], EB_PARA, cop_dz=-.01)                  # north front, east block
    b.flush('precast fronts')
    south_frame_box()
    south_under_shell()
    corners()


def return_x(y):
    """x of the shell's vertical return face (the plan line BW-G) at y, plus 3 cm into the CLT."""
    return SH['G'][0] + (y - FY) / (SH['BW'][1] - FY) * (SH['BW'][0] - SH['G'][0]) + .03


def to_return(b, role, x0, ya, yb, z0, z1):
    """A horizontal member from x0 east to the shell's return face, its east end cut along that face."""
    ya, yb = min(ya, yb), max(ya, yb)
    b._hex(role, [(x, y, z) for z in (z0, z1) for x, y in ((x0, ya), (return_x(ya), ya), (return_x(yb), yb), (x0, yb))])


def south_frame_box():
    """South front of the pool block: a white frame box (two storeys of glass ribbons) projecting 0.75 m over a
    recessed glazed ground floor with two pairs of doors; the parapet band above."""
    b = Batch()
    ax, c, o = 'x', Y0, -1
    s0, s1 = X0, BOXX1
    # The box's east end, its top, bottom and middle spandrel, the parapet band and the coping all die into the shell's
    # vertical return face along one straight line (each lapped 3 cm into the CLT, so the junction is a single clean edge).
    to_return(b, 'precast', s0 + .02, Y0 - .78, Y0 + .3, F2 - .45, F2 + .2)                          # box bottom
    to_return(b, 'precast', s0 + .02, Y0 - .78, Y0 + .3, F4 - .25, F4 + .25)                         # box top
    fbox(b, 'precast', ax, c, o, s0, s0 + .5, F2 - .47, F4 + .27, -.3, .80)                            # box west end
    to_return(b, 'precast', s1 - .5, Y0 - .8, Y0 + .3, F2 - .47, F4 + .27)                           # box east end
    to_return(b, 'precast', s0 + .5, Y0 - .74, Y0 + .3, F3 - .4, F3 + .2)                            # middle spandrel
    for z0, z1 in ((F2 + .2, F3 - .4), (F3 + .2, F4 - .25)):
        glazed(b, ax, c, o, s0 + .5, s1 - .5, z0, z1, 1.9, d=.3)
    fbox(b, 'interior', ax, c, o, s0 + .6, s1 - .6, F2, F4, -4.4, -4.2)
    to_return(b, 'precast', s0 - .28, Y0 - .3, Y0 + .25, F4 - .01, PARA - .05)                        # parapet band
    to_return(b, 'coping', s0 - .32, Y0 - .34, Y0 + .3, PARA - .07, PARA - .01)
    # Ground floor: recessed glazing with two pairs of doors, the corner column.
    gd = -.7
    fbox(b, 'precast', ax, c, o, s0, s0 + .55, 0.0, F2 - .4, gd - .05, .1)
    pieces = [(s0 + .55, -21.0), (-19.0, -18.5), (-16.5, s1)]
    for a, e in pieces:
        glazed(b, ax, c, o, a, e, G0, F2 - .45, 1.2, d=gd, transoms=(3.3,))
    for sc in (-20.0, -17.5):
        door_pair(b, ax, c, o, sc, G0, 3.1, gd)
        fbox(b, 'frame', ax, c, o, sc - 1.0, sc + 1.0, 3.1, 3.2, gd - .03, gd + .03)
        glazed(b, ax, c, o, sc - .97, sc + .97, 3.2, F2 - .45, 9, d=gd)
    fbox(b, 'precast', ax, c, o, s0, s1, F2 - .5, F2 - .45, gd - .3, gd + .02)
    fbox(b, 'interior', ax, c, o, s0 + .6, s1, G0, F2 - .5, -7.0, -6.8)
    b.box('concrete2', -18.75, Y0 - .25, G0 + .005, 5.4, .9, .01)                                       # entrance mat
    b.flush('south frame box')


def shell_edge_x(z):
    """x of the climbing shell's east back edge (BN to RNE) at height z: the facade east of it is open to view."""
    return SH['BN'][0] + (SH['RNE'][0] - SH['BN'][0]) * z / RIM


XV = 8.0                            # ribbons start beyond the east overhang (plain white wall under it)


def south_under_shell():
    """South front from the frame box to the east street, seen beside and under the shell's overhang: flush white
    floor bands and glass ribbons that start just east of the shell's back edge (they step with it), white fillers
    between the edge and each ribbon (their west ends tucked behind the shell's back plane), the penthouse and the east
    block above."""
    b = Batch()
    ax, c, o = 'x', Y0, -1
    fbox(b, 'precast', ax, c, o, -12.7, -10.5, 0.0, PARA, -.5, -.1)                                     # beside the return
    # Plain white wall under the overhang, from behind the shell's back edge to the ribbons: one box per height zone
    # (stacked, never overlapping, so no two front faces share a plane).
    fbox(b, 'precast', ax, c, o, shell_edge_x(0.0) - .6, XV + .05, 0.0, F4 + .25, -.4, -.1)
    fbox(b, 'precast', ax, c, o, XE - .02, XV + .05, F4 + .25, EB_TOP - .5, -.4, -.1)
    levels = [(G0, F2), (F2, F3), (F3, F4), (F4, EB_TOP)]
    for k, (za, zb) in enumerate(levels):
        x_lo = XE + .2 if k == 3 else -12.2
        g0, g1 = (G0 if k == 0 else za + .25), zb - .55
        if k > 0:
            fbox(b, 'precast', ax, c, o, max(x_lo, XV - .1), X1, za - .55, za + .25, -.4, .05)
        xs = max(x_lo, XV)
        if X1 - .4 - xs > 1.0:
            glazed(b, ax, c, o, xs, X1 - .4, g0, g1, 2.0, d=-.38)
            fbox(b, 'interior', ax, c, o, xs, X1 - .4, za, zb, -4.4, -4.2)
        fbox(b, 'precast', ax, c, o, X1 - .45, X1, g0, g1 + .02, -.4, .05)                              # east end pier
    fbox(b, 'precast', ax, c, o, max(-12.0, shell_edge_x(F4 - .55) + .02), XE + .2, F4 - .55, PARA - .05, -.4, .05)
    fbox(b, 'coping', ax, c, o, max(-12.0, shell_edge_x(PARA)), XE + .2, PARA - .06, PARA, -.45, .09)
    fbox(b, 'precast', ax, c, o, XE + .2, X1, EB_TOP - .55, EB_PARA - .05, -.4, .3)                       # east block parapet
    fbox(b, 'coping', ax, c, o, XE + .2, X1, EB_PARA - .07, EB_PARA - .01, -.45, .34)
    fbox(b, 'precast', ax, c, o, max(XP0, shell_edge_x(PARA) - .4), XE + .2, PARA - .05, PH_TOP - .3, -.5, -.08)   # penthouse
    fbox(b, 'precast', ax, c, o, max(XP0, shell_edge_x(PH_TOP) - .4), XE + .2, PH_TOP - .3, PH_PARA - .05, -.5, .25)
    fbox(b, 'coping', ax, c, o, max(XP0, shell_edge_x(PH_PARA) - .4), XE + .2, PH_PARA - .06, PH_PARA, -.55, .3)
    b.flush('south front under the shell')


def corners():
    """Corner piers closing the precast fronts at the four building corners (the fronts' fins stop at the corner line)."""
    b = Batch()
    for x, y, sx, sy, top in ((X0, Y1, -1, 1, PARA), (X1, Y1, 1, 1, EB_PARA), (X1, Y0, 1, -1, EB_PARA)):
        b.box('precast', x + sx * .23, y + sy * .23, top / 2, .5, .5, top - .002)
    b.flush('corners')


# ---------------------------------------------------------------- roofs
def pool_deck():
    """Pool deck: pavers, the infinity pool along the west edge with its overflow trough, coping, glass balustrades,
    loungers, and the planters of the roof garden at the north end."""
    b = Batch()
    dx0, dx1, dy0, dy1 = X0 + .3, XP0, Y0 + .08, Y1 - .3
    px0, px1, py0, py1 = -20.9, -10.8, -15.6, 6.9
    for x0, x1, y0, y1 in ((dx0, px0 - 1.7, dy0, dy1), (px1, dx1, dy0, dy1), (px0 - 1.7, px1, dy0, py0), (px0 - 1.7, px1, py1, dy1)):
        b.box('deck', (x0 + x1) / 2, (y0 + y1) / 2, DECK - .1, x1 - x0, y1 - y0, .2)
    for k in range(1, 12):                                                                            # paver joints
        y = dy0 + (dy1 - dy0) * k / 12
        b.box('coping', (px1 + dx1) / 2, y, DECK + .002, dx1 - px1 - .1, .03, .006)
    # Pool tank: water to the west edge (infinity), coping on the north, east and south, trough below the edge.
    b.box('water', (px0 + px1) / 2, (py0 + py1) / 2, WATER - .3, px1 - px0, py1 - py0, .6)
    for x0, x1, y0, y1 in ((px1, px1 + .45, py0 - .45, py1 + .45), (px0 - .02, px1, py0 - .45, py0), (px0 - .02, px1, py1, py1 + .45)):
        b.box('coping', (x0 + x1) / 2, (y0 + y1) / 2, (DECK - .2 + WATER + .06) / 2, x1 - x0, y1 - y0, WATER + .06 - DECK + .2)
    b.box('water2', px0 - .85, (py0 + py1) / 2, DECK - .2, 1.7, py1 - py0 + .9, .2)                   # overflow trough
    b.box('glass', px0 - .03, (py0 + py1) / 2, (DECK - .2 + WATER - .005) / 2, .05, py1 - py0, WATER - .005 - DECK + .2)   # infinity weir
    for y in (py0 + 1.0, py1 - 1.0):                                                                  # pool ladders
        for dyy in (-.25, .25):
            b.beam('metal', (px1 - .1, y + dyy, WATER - .5), (px1 + .2, y + dyy, WATER + .9), .045)
            b.beam('metal', (px1 + .2, y + dyy, WATER + .9), (px1 + .45, y + dyy, WATER + .9), .045)
    # Glass balustrades on the parapet: west, south and north edges of the deck.
    for (x0, y0), (x1, y1) in (((X0 + .12, Y0 + .1), (X0 + .12, Y1 - .1)), ((X0 + .1, Y0 + .12), (-11.7, Y0 + .12)),
                               ((X0 + .1, Y1 - .12), (XP0, Y1 - .12))):
        L = math.hypot(x1 - x0, y1 - y0)
        ux, uy = (x1 - x0) / L, (y1 - y0) / L
        b.beam('glass', (x0, y0, PARA + .55), (x1, y1, PARA + .55), .025, 1.0)
        b.beam('metal', (x0, y0, PARA + 1.08), (x1, y1, PARA + 1.08), .05, .05)
        n = max(1, int(L / 1.5))
        for k in range(n + 1):
            px, py = x0 + ux * L * k / n, y0 + uy * L * k / n
            b.box('metal', px, py, PARA + .53, .06, .06, 1.06)
    # Loungers in a row along the penthouse glazing, facing the pool; a second row at the garden.
    for k in range(8):
        lounger(b, -8.4, -14.6 + k * 1.65, DECK, 1)
    for k in range(6):
        lounger(b, -20.6 + k * 1.45, 8.3, DECK, 2)
    # Roof garden planters: a large raised planter with trees and grasses, a strip along the penthouse wall.
    for x0, x1, y0, y1 in GARDEN:
        for xa, xb, ya, yb in ((x0, x1, y0, y0 + .25), (x0, x1, y1 - .25, y1), (x0, x0 + .25, y0 + .25, y1 - .25), (x1 - .25, x1, y0 + .25, y1 - .25)):
            b.box('planter', (xa + xb) / 2, (ya + yb) / 2, (DECK - .05 + DECK + .7) / 2, xb - xa, yb - ya, .75)
    b.box('coping', -13.0, 13.2, DECK + .45, 1.6, .5, .45)                                             # garden bench
    b.flush('pool deck')


GARDEN = ((-22.4, -12.4, 9.6, 17.4), (-9.6, -6.35, 9.6, 17.4))       # roof garden planters (x0, x1, y0, y1)
ROOF_TREES = ((-20.4, 13.6), (-17.2, 15.6), (-14.6, 12.4))


def lounger(b, x, y, z, face):
    """Sun lounger: a white slatted bed on four legs with a raised back; face 1 = back to the east, 2 = back to the north."""
    if face == 1:
        b.box('lounger', x - .2, y, z + .36, 1.4, .68, .07)
        b.beam('lounger', (x + .5, y, z + .38), (x + 1.0, y, z + .85), .68, .07)
        for dx in (-.8, .4):
            for dy in (-.28, .28):
                b.box('metal', x + dx, y + dy, z + .17, .05, .05, .36)
    else:
        b.box('lounger', x, y - .2, z + .36, .68, 1.4, .07)
        b.beam('lounger', (x, y + .5, z + .38), (x, y + 1.0, z + .85), .68, .07)
        for dx in (-.28, .28):
            for dy in (-.8, .4):
                b.box('metal', x + dx, y + dy, z + .17, .05, .05, .36)


def penthouse():
    """One-storey penthouse: glazed to the pool deck at its south end, solid white with a door to the north; flat
    roof with a parapet, an air-handling unit with a fan and small plant."""
    b = Batch()
    ax, c, o = 'y', XP0, -1
    fbox(b, 'precast', ax, c, o, -18.1, Y1, DECK - .3, DECK + .1, -.3, .05)                             # base kerb
    fbox(b, 'precast', ax, c, o, 2.6, Y1, DECK, PH_TOP - .3, -.3, 0.0)                                  # solid north wall
    fbox(b, 'precast', ax, c, o, -18.1, -16.9, DECK, PH_TOP - .3, -.3, 0.0)
    fbox(b, 'precast', ax, c, o, -18.1, Y1, PH_TOP - .32, PH_PARA - .05, -.3, .25)                      # parapet band
    fbox(b, 'coping', ax, c, o, -18.1, Y1, PH_PARA - .06, PH_PARA, -.35, .3)
    glazed(b, ax, c, o, -16.9, 2.6, DECK + .1, PH_TOP - .32, 2.2, d=-.15)
    fbox(b, 'interior', ax, c, o, -16.8, 2.5, DECK, PH_TOP - .3, -6.2, -6.0)
    fbox(b, 'frame', ax, c, o, 5.2, 6.4, DECK + .1, DECK + 2.8, -.04, .03)                              # door
    fbox(b, 'hardware', ax, c, o, 6.2, 6.25, DECK + 1.0, DECK + 1.15, .03, .08)
    # Other walls: north (on the north front), east (over the east block roof).
    b.box('precast', (XP0 + .05 + XE) / 2, Y1 - .12, (PARA + PH_PARA - .01) / 2, XE - XP0 - .05, .36, PH_PARA - .01 - PARA)
    b.box('precast', XE + .15, (Y0 + Y1) / 2, (EB_TOP + PH_PARA - .01) / 2, .3, Y1 - Y0 - .2, PH_PARA - .01 - EB_TOP)
    # Roof.
    b.box('membrane', (XP0 + XE) / 2, (-18.1 + Y1) / 2, PH_TOP - .05, XE - XP0 - .2, Y1 + 18.1 - .2, .1)
    b.box('mech', -.6, 9.5, PH_TOP + .8, 3.0, 3.4, 1.6)
    frustum(b, 'hardware', -.6, 8.9, PH_TOP + 1.6, PH_TOP + 1.66, .9, .9, 16)
    b.box('frame', -.6, 8.9, PH_TOP + 1.68, 1.9, .06, .04)
    b.box('frame', -.6, 8.9, PH_TOP + 1.685, .06, 1.9, .04)
    for x, y, w, d, h in ((2.4, 1.0, 1.1, .9, .8), (1.8, -4.0, 1.2, 1.4, .9), (-3.2, 3.0, .8, .8, .6)):
        b.box('mech', x, y, PH_TOP + h / 2, w, d, h)
    b.flush('penthouse')


def east_roof():
    """East block roof: membrane inside the parapet, two dark skylights, hatches, plant boxes and vents."""
    b = Batch()
    b.box('membrane', (XE + X1) / 2, (Y0 + Y1) / 2, EB_TOP + .02, X1 - XE - .6, Y1 - Y0 - .6, .06)
    for x, y in ((10.5, 2.5), (11.0, -4.5)):
        b.box('concrete2', x, y, EB_TOP + .2, 2.4, 1.8, .3)
        b.box('glass', x, y, EB_TOP + .36, 2.2, 1.6, .04)
    for x, y, w, d, h in ((8.2, -9.5, .9, .7, .7), (9.0, 8.0, 1.2, 1.0, .8), (13.5, 11.0, .8, .8, .6), (8.5, -1.0, .7, .9, .5)):
        b.box('mech', x, y, EB_TOP + h / 2, w, d, h)
    for x, y in ((12.0, -12.0), (7.5, 13.0), (14.0, 5.0)):
        cyl(b, 'frame', x, y, EB_TOP, EB_TOP + .55, .1, 8)
    b.flush('east block roof')


# ---------------------------------------------------------------- the climbing shell
SHELL_TRIS = [('KW', 'KX', 'RSW'), ('KW', 'RSW', 'RNW'),           # upper west panel: from the pool-block parapet corner up to the rim
              ('BW', 'KX', 'KW'),                                   # lower flared west face; the fold KW-KX runs at parapet height
              ('BW', 'BS', 'KS'), ('BW', 'KS', 'KX'),               # south-west facets over the foot
              ('KS', 'BS', 'RSE'), ('KS', 'RSE', 'KX'), ('KX', 'RSE', 'RSW'),   # south face
              ('BS', 'BN', 'RNE'), ('BS', 'RNE', 'RSE'),            # east face, overhanging the facade
              ('BN', 'G', 'KW'), ('BN', 'KW', 'RNW'), ('BN', 'RNW', 'RNE'),     # back plane, lapped into the facade
              ('BW', 'KW', 'G'),                                    # return to the facade under the fold
              ('G', 'BN', 'BS'), ('G', 'BS', 'BW')]                 # foot
RIM_LOOP = ['RNW', 'RSW', 'RSE', 'RNE']


def _v(a, b): return (b[0] - a[0], b[1] - a[1], b[2] - a[2])
def _x(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
def _d(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _n(a):
    L = math.sqrt(_d(a, a)) or 1.0
    return (a[0] / L, a[1] / L, a[2] / L)


def shell_frame():
    """Outward-wound outer triangles with unit normals, and the inner (offset) vertices of the CLT shell."""
    # Orient the (not convex) folded surface consistently across shared edges, then outward by its signed volume
    # (closed with the open rim for the volume only).
    tl = [list(t) for t in SHELL_TRIS]
    done = {0}; todo = [0]
    while todo:
        i = todo.pop()
        ei = {(tl[i][k], tl[i][(k + 1) % 3]) for k in range(3)}
        for j in range(len(tl)):
            if j in done:
                continue
            ej = {(tl[j][k], tl[j][(k + 1) % 3]) for k in range(3)}
            if ei & ej:
                tl[j] = [tl[j][0], tl[j][2], tl[j][1]]; done.add(j); todo.append(j)
            elif {(b, a) for a, b in ei} & ej:
                done.add(j); todo.append(j)
    cap = [(RIM_LOOP[0], RIM_LOOP[k], RIM_LOOP[k + 1]) for k in (1, 2)]
    vol = 0.0
    for t in [tuple(x) for x in tl]:
        a, b_, c = (SH[k] for k in t)
        vol += _d(a, _x(b_, c))
    edges = {(t[k], t[(k + 1) % 3]) for t in tl for k in range(3)}
    rim_dir = (RIM_LOOP[1], RIM_LOOP[0]) in edges              # the rim cap closes the surface against the open loop
    for t in cap:
        a, b_, c = (SH[k] for k in (t if rim_dir else (t[0], t[2], t[1])))
        vol += _d(a, _x(b_, c))
    tris = []
    for t in tl:
        t = tuple(t) if vol > 0 else (t[0], t[2], t[1])
        a, b_, c = (SH[k] for k in t)
        tris.append((t, _n(_x(_v(a, b_), _v(a, c)))))
    inner = {}
    for k, p in SH.items():
        planes = []
        for t, n in tris:
            if k in t and all(abs(_d(n, q)) < .999 for q in planes):
                planes.append(n)
        rows = [list(n) for n in planes]; rhs = [SHELL_T] * len(planes)
        if k in RIM_LOOP:
            rows.append([0.0, 0.0, 4.0]); rhs.append(0.0)                 # the rim stays level
        # least squares N d = t via the 3x3 normal equations
        M = [[sum(r[i] * r[j] for r in rows) for j in range(3)] for i in range(3)]
        y = [sum(r[i] * h for r, h in zip(rows, rhs)) for i in range(3)]
        det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
               + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
        def col(i):
            m = [r[:] for r in M]
            for j in range(3):
                m[j][i] = y[j]
            return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
                    + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))
        d = [col(i) / det for i in range(3)]
        inner[k] = (p[0] - d[0], p[1] - d[1], p[2] - d[2])
    return tris, inner


def shell():
    """The hollow, open-topped CLT climbing shell: outer folded planes, the inner surface offset 35 cm, a level rim cap
    and a light timber fascia applied 4 cm proud around the top of the three street faces."""
    tris, inner = shell_frame()
    keys = list(SH)
    V = [SH[k] for k in keys] + [inner[k] for k in keys]
    io = len(keys)
    F = []; roles = []
    for t, n in tris:
        F.append(tuple(keys.index(k) for k in t))
        F.append(tuple(io + keys.index(k) for k in reversed(t)))
    caps = []
    for i in range(4):
        a, e = RIM_LOOP[i], RIM_LOOP[(i + 1) % 4]
        caps.append((keys.index(a), keys.index(e), io + keys.index(e), io + keys.index(a)))
    # outer and inner surfaces as separate role meshes (outer honey, inner a touch lighter), rim cap in the fascia tone
    out_f = [f for k, f in enumerate(F) if k % 2 == 0]
    in_f = [f for k, f in enumerate(F) if k % 2 == 1]
    obj = C.mesh('Climbing shell CLT', V, out_f + in_f + caps, 'timber', 'climbing shell')
    for p in obj.data.polygons:                                        # folded CLT planes: flat shaded
        p.use_smooth = False
    for p in obj.data.polygons:                                        # inner faces and the rim cap get their own tones
        if p.index >= len(out_f) + len(in_f):
            p.material_index = 2
        elif p.index >= len(out_f):
            p.material_index = 1
    obj.data.materials.append(C.MATS['timber_in']); obj.data.materials.append(C.MATS['timber2'])
    # Fascia: 0.55 m plates on the south-west upper facet, the south face and the east face, 4 cm proud, ends lapped.
    b = Batch()
    for a, e in (('RNW', 'RSW'), ('RSW', 'RSE'), ('RSE', 'RNE')):
        n = next(n for t, n in tris if a in t and e in t)
        dn = _n((n[2] * n[0], n[2] * n[1], -1.0 + n[2] * n[2]))      # down the face, in its plane
        s = .55 / max(.2, -dn[2])
        pa, pe = SH[a], SH[e]
        u = _n(_v(pa, pe))
        pa = tuple(pa[i] - u[i] * .06 for i in range(3)); pe = tuple(pe[i] + u[i] * .06 for i in range(3))
        quad = [pa, pe, tuple(pe[i] + dn[i] * s for i in range(3)), tuple(pa[i] + dn[i] * s for i in range(3))]
        quad = [(q[0], q[1], q[2] + (.07 if q[2] > RIM - .01 else 0)) for q in quad]
        V2, F2_ = b.g.setdefault('timber2', ([], []))
        o = len(V2)
        V2.extend(tuple(q[i] - n[i] * .01 for i in range(3)) for q in quad)
        V2.extend(tuple(q[i] + n[i] * .045 for i in range(3)) for q in quad)
        F2_.extend([(o, o + 1, o + 2, o + 3), (o + 7, o + 6, o + 5, o + 4), (o, o + 4, o + 5, o + 1), (o + 1, o + 5, o + 6, o + 2),
                    (o + 2, o + 6, o + 7, o + 3), (o + 3, o + 7, o + 4, o + 0)])
    # The hollow's floor: a crash mat on the inner foot.
    fl = [inner[k] for k in ('G', 'BN', 'BS', 'BW')]
    cx = sum(p[0] for p in fl) / 4; cy = sum(p[1] for p in fl) / 4
    mat = [(cx + (p[0] - cx) * .97, cy + (p[1] - cy) * .97) for p in fl]
    b.flush('climbing shell fascia')
    C.prism('Climbing shell crash mat', mat, 'z', fl[0][2] - .02, fl[0][2] + .45, 'mat', 'climbing shell')
    # The lean hides the foot from above, so a padded bouldering deck spans the hollow at 5.5 m: its dark mat is what
    # the top view sees through the rim. Its outline is the inner surface's section at that height, grown 10 cm so its
    # edges bury in the CLT.
    zm = 5.5
    pts = []
    for tr, n in tris:
        q = [inner[k] for k in tr]
        for i in range(3):
            a, e = q[i], q[(i + 1) % 3]
            if (a[2] - zm) * (e[2] - zm) < 0:
                s = (zm - a[2]) / (e[2] - a[2])
                pts.append((a[0] + (e[0] - a[0]) * s, a[1] + (e[1] - a[1]) * s))
    hull = _PkPolygon(pts).convex_hull.buffer(.1, join_style=2)
    C.prism('Climbing shell bouldering deck', list(hull.exterior.coords)[:-1][::-1] if hull.exterior.is_ccw is False else list(hull.exterior.coords)[:-1],
            'z', zm - .35, zm + .1, 'mat', 'climbing shell')
    C.CONTACTS.append(dict(name='Climbing shell: foot sunk 15 cm into the plaza, back plane lapped 10 cm into the facade', rim_m=RIM))
    return tris, inner


def tri_point(a, b_, c, u, v):
    if u + v > 1:
        u, v = 1 - u, 1 - v
    return tuple(a[i] + (b_[i] - a[i]) * u + (c[i] - a[i]) * v for i in range(3))


def hold(b, role, p, n, r, h, rnd):
    """A climbing hold: an irregular 5-7 sided lump whose base is sunk 1.5 cm into the face along its normal n."""
    k = rnd.choice((5, 6, 7))
    ref = (0.0, 0.0, 1.0) if abs(n[2]) < .9 else (1.0, 0.0, 0.0)
    s = _n(_x(n, ref)); t = _x(n, s)
    rot = rnd.uniform(0, math.tau); el = rnd.uniform(.7, 1.3)
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    shift = (rnd.uniform(-.25, .25) * r, rnd.uniform(-.25, .25) * r)
    for lvl, (dd, rr) in enumerate(((-.015, 1.0), (h, .55))):
        for i in range(k):
            a = rot + math.tau * i / k
            rad = r * rr * rnd.uniform(.82, 1.12)
            du, dv = rad * math.cos(a) * el, rad * math.sin(a) / el
            if lvl:
                du += shift[0]; dv += shift[1]
            V.append(tuple(p[j] + n[j] * dd + s[j] * du + t[j] * dv for j in range(3)))
    F.append(tuple(o + i for i in range(k - 1, -1, -1)))
    F.append(tuple(o + k + i for i in range(k)))
    for i in range(k):
        j = (i + 1) % k
        F.append((o + i, o + j, o + k + j, o + k + i))


def fold_dist(p):
    """Distance from p to the west/south fold (the arris BS-KS-KX-RSW)."""
    best = 1e9
    pts = [SH[k] for k in ('BS', 'KS', 'KX', 'RSW')]
    for a, e in zip(pts, pts[1:]):
        d = _v(a, e); L2 = _d(d, d)
        s = max(0.0, min(1.0, _d(_v(a, p), d) / L2))
        q = tuple(a[i] + d[i] * s for i in range(3))
        best = min(best, math.sqrt(_d(_v(q, p), _v(q, p))))
    return best


def holds(tris, inner):
    """Dark and white holds: dense on the south face, a white route with a few dark holds on the south-west face,
    some on the east face, and white holds on the inner walls near the top (seen from above)."""
    rnd = random.Random(7)
    b = Batch()
    placed = []

    def scatter(tri, n, count, white, zmin=.6, zmax=RIM - .8, inner_face=False, band=None):
        a, b_, c = tri
        done = 0; tries = 0
        while done < count and tries < count * 40:
            tries += 1
            p = tri_point(a, b_, c, rnd.random(), rnd.random())
            if not zmin < p[2] < zmax:
                continue
            if band and not band(p):
                continue
            if any((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2 < .36 ** 2 for q in placed):
                continue
            placed.append(p); done += 1
            r = rnd.uniform(.07, .17); h = rnd.uniform(.05, .11)
            role = 'hold_w' if rnd.random() < white else 'hold'
            hold(b, role, p, n, r, h, rnd)
    for t, n in tris:
        names = set(t)
        P = [SH[k] for k in t]
        if names <= {'BS', 'RSE', 'KS', 'RSW', 'KX'} and 'RSE' in names:                  # south face
            scatter(P, n, 32, .22)
        elif names in ({'BW', 'BS', 'KS'}, {'BW', 'KS', 'KX'}, {'KW', 'KX', 'RSW'}):         # west faces: plain timber except
            scatter(P, n, 6, .9, band=lambda p: fold_dist(p) < 1.7)                          # a white band along the west/south fold
        elif names <= {'BS', 'BN', 'RNE', 'RSE'}:                                         # east face
            scatter(P, n, 12, .3, zmin=2.0)
    for t, n in tris:                                                                   # inner faces near the rim
        names = set(t)
        if names & set(RIM_LOOP) and not names <= {'G', 'BN', 'BS', 'BW'}:
            P = [inner[k] for k in t]
            ni = (-n[0], -n[1], -n[2])
            scatter(P, ni, 10, .85, zmin=RIM - 7.0, zmax=RIM - .9)
    b.flush('climbing holds')
    return placed


def face_point(tri, x, z):
    """Point on the plane of `tri` at (x, z) (planes that are not parallel to y)."""
    a, b_, c = tri
    n = _x(_v(a, b_), _v(a, c))
    y = a[1] - (n[0] * (x - a[0]) + n[2] * (z - a[2])) / n[1]
    return (x, y, z)


def inside_xz(tri, x, z, m=0.0):
    """(x, z) inside the triangle's x-z projection, at least m metres from its edges."""
    P = [(p[0], p[2]) for p in tri]
    s = []
    for i in range(3):
        (x0, z0), (x1, z1) = P[i], P[(i + 1) % 3]
        L = math.hypot(x1 - x0, z1 - z0) or 1.0
        s.append(((x1 - x0) * (z - z0) - (z1 - z0) * (x - x0)) / L)
    return all(v >= m for v in s) or all(v <= -m for v in s)


CLIMBERS = ((-3.4, 9.4, 'shirt', ((-.55, .95), (.45, .75), (-.45, -1.5), (.4, -1.35))),           # reaching
            (-1.6, 8.4, 'shirt', ((-.25, 1.05), (.6, .2), (-.35, -1.45), (.85, -.7))),             # flagged leg
            (-4.3, 12.6, 'harness', ((-.5, .9), (.35, -.35), (-.3, -1.4), (.3, -1.5))))           # resting, one arm low


def climbers(tris):
    """Three climbers on the middle of the south face (cyan, cyan and dark tops), each on the facet that contains it:
    torso, head, arms to holds above, legs to holds below, harness, 25-30 cm off the face; every hand and foot rests
    on a hold on that facet."""
    south = [(t, n) for t, n in tris if 'RSE' in t and set(t) <= {'KS', 'BS', 'RSE', 'KX', 'RSW'}]
    rnd = random.Random(31)
    b = Batch()
    for (x, z, shirt, ends) in CLIMBERS:
        t, n = next((t, n) for t, n in south if inside_xz([SH[k] for k in t], x, z, .9))
        tri = [SH[k] for k in t]
        p = face_point(tri, x, z)
        up = _n((-n[2] * n[0], -n[2] * n[1], 1.0 - n[2] * n[2]))
        side = _n(_x(up, n))
        q = lambda du, dv, dd: tuple(p[i] + side[i] * du + up[i] * dv + n[i] * dd for i in range(3))
        b.beam(shirt, q(0, -.3, .3), q(0, .3, .3), .36, .22)                                  # torso
        b.beam('harness', q(0, -.38, .3), q(0, -.24, .3), .4, .26)                            # harness belt
        b.beam('harness', q(-.1, -.95, .27), q(-.1, -.36, .3), .14, .14)                      # legs
        b.beam('harness', q(.1, -.95, .27), q(.1, -.36, .3), .14, .14)
        (ha, hb, fa, fb) = ends
        b.beam('harness', q(-.12, -.95, .27), q(fa[0], fa[1], .07), .12, .12)
        b.beam('harness', q(.12, -.95, .27), q(fb[0], fb[1], .07), .12, .12)
        b.beam('skin', q(-.2, .25, .3), q(ha[0], ha[1], .07), .09, .09)                       # arms
        b.beam('skin', q(.2, .25, .3), q(hb[0], hb[1], .07), .09, .09)
        frustum_on(b, 'skin', q(0, .48, .3), up, n, .11, .24)                                 # head
        for du, dv in ends:                                                                  # holds under hands and feet
            hold(b, 'hold', q(du, dv, 0.0), n, .1, .085, rnd)
    b.flush('climbers')


def frustum_on(b, role, c, axis, n, r, h, k=8):
    """Small closed octagonal head: a frustum pair along `axis` centred at c."""
    s = _n(_x(axis, n)); t = n
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for lvl, (dz, rr) in enumerate(((-h / 2, .7), (0.0, 1.0), (h / 2, .7))):
        for i in range(k):
            a = math.tau * i / k
            V.append(tuple(c[j] + axis[j] * dz + (s[j] * math.cos(a) + t[j] * math.sin(a)) * r * rr for j in range(3)))
    F.append(tuple(o + i for i in range(k - 1, -1, -1)))
    F.append(tuple(o + 2 * k + i for i in range(k)))
    for lv in range(2):
        for i in range(k):
            j = (i + 1) % k
            F.append((o + lv * k + i, o + lv * k + j, o + (lv + 1) * k + j, o + (lv + 1) * k + i))


# ---------------------------------------------------------------- site
PLAZA_S = -35.5                     # plaza's south edge (south sidewalk beyond)
WS0, WS1 = -28.0, X0                 # west sidewalk
ES0, ES1 = X1, 20.5                  # east sidewalk
PLANTERS = (((-16.5, -33.8), (-5.5, -33.8), (-5.5, -29.2), (-16.5, -29.2)),
            ((4.0, -33.6), (11.5, -33.6), (11.5, -26.0), (9.0, -26.0), (9.0, -31.0), (4.0, -31.0)),
            ((16.6, -31.0), (17.9, -31.0), (17.9, -19.0), (16.6, -19.0)))
TREE_PITS = [(-26.6, y) for y in (-31.0, -24.5, -18.0, -11.5, -5.0, 1.5, 8.0, 14.5)] + [(18.6, y) for y in (-7.0, 6.0)]


def site():
    """Plaza, sidewalks, streets, curbs, markings, crossings, tree pits, lamp posts, bollards, a bin and parked cars."""
    WX0, WX1, EX0, EX1 = -38.0, WS0, ES1, 31.0             # west and east streets (x)
    SY0, SY1, NY0, NY1 = -50.0, -39.5, 21.5, 31.0           # south and north streets (y)
    for name, x0, x1, y0, y1, role, top in (
            ('West street', WX0, WX1, -64.0, 64.0, 'asphalt', .04), ('East street', EX0, EX1, -64.0, 64.0, 'asphalt', .041),
            ('South street', WX1, EX0, SY0, SY1, 'asphalt', .042), ('North street', WX1, EX0, NY0, NY1, 'asphalt', .043),
            ('Plaza', X0, ES1, PLAZA_S, Y0 + .02, 'paving', .15), ('West sidewalk', WS0, WS1, SY1, NY0, 'concrete2', .15),
            ('East sidewalk', ES0, ES1, Y0 + .02, NY0, 'concrete2', .151), ('South sidewalk', WS0, ES1, SY1, PLAZA_S, 'concrete2', .152),
            ('North sidewalk', WS1, ES0, Y1 - .02, NY0, 'concrete2', .153), ('Far west sidewalk', -42.0, WX0, -64.0, 64.0, 'concrete2', .15),
            ('Far east sidewalk', EX1, 35.0, -64.0, 64.0, 'concrete2', .151), ('Far south sidewalk', WX1, EX0, -54.0, SY0, 'concrete2', .152),
            ('Far north sidewalk', WX1, EX0, NY1, 35.0, 'concrete2', .153)):
        C.box(name, ((x0 + x1) / 2, (y0 + y1) / 2, top / 2), (x1 - x0, y1 - y0, top), role, 'site', 0)
    b = Batch()
    # Plaza pavers: long grey bands of two tones running east-west, and cross joints.
    for k in range(int((Y0 - PLAZA_S) / 1.2)):
        if k % 2:
            b.box('paving2', (X0 + ES1) / 2, PLAZA_S + .6 + k * 1.2, .151, ES1 - X0 - .1, 1.1, .004)
    for k in range(int((ES1 - X0) / 2.4)):
        b.box('paving2', X0 + 1.2 + k * 2.4, (PLAZA_S + Y0) / 2, .1515, .03, Y0 - PLAZA_S - .1, .004)
    # Curbs, 5 cm proud of the walks, along every street edge.
    for x, y0, y1 in ((WX0, -64.0, 64.0), (EX1, -64.0, 64.0), (WX1, SY1, NY0), (EX0, SY1, NY0)):
        b.box('curb', x, (y0 + y1) / 2, .1, .2, y1 - y0, .2)
    for y, x0, x1 in ((SY0, WX1, EX0), (NY1, WX1, EX0), (SY1, WX1, EX0), (NY0, WX1, EX0)):
        b.box('curb', (x0 + x1) / 2, y, .101, x1 - x0 - .2, .2, .2)
    # Lane markings, crossings and stop lines.
    for k in range(-25, 26):
        y = k * 2.5
        if not (SY0 - 1 < y < SY1 + 1 or NY0 - 1 < y < NY1 + 1):
            b.box('paint', (WX0 + WX1) / 2, y, .044, .12, 1.3, .004)
            b.box('paint', (EX0 + EX1) / 2, y, .045, .12, 1.3, .004)
    for k in range(int((EX0 - WX1) / 2.5)):
        x = WX1 + 1.25 + k * 2.5
        b.box('paint', x, (SY0 + SY1) / 2, .046, 1.3, .12, .004)
        b.box('paint', x, (NY0 + NY1) / 2, .047, 1.3, .12, .004)
    for x0, x1 in ((WX0, WX1), (EX0, EX1)):                                                        # zebra crossings
        n = int((x1 - x0 - .6) / 1.1)
        for k in range(n):
            for y in (19.6, -37.5):
                b.box('paint', x0 + .6 + k * 1.1, y, .048, .55, 3.2, .004)
    # Tree pits, lamp posts, bollards, a bin.
    for x, y in TREE_PITS:
        b.box('soil', x, y, .152, 1.4, 1.4, .01)
    for x, y in ((-27.3, -21.2), (-27.3, -1.7), (-27.3, 18.0), (-12.8, -34.6), (2.0, -34.6), (20.0, 4.0)):
        cyl(b, 'hardware', x, y, .15, 5.6, .07, 8)
        b.box('hardware', x, y, 5.75, .34, .34, .3)
        b.box('paint', x, y, 5.55, .28, .28, .14)
    for k in range(7):
        cyl(b, 'metal', 13.0 + k * 1.2, PLAZA_S + .4, .15, 1.0, .1, 8)
    for k in range(5):
        cyl(b, 'metal', ES1 - .5, PLAZA_S + 1.6 + k * 1.4, .15, 1.0, .1, 8)
    cyl(b, 'metal', -12.0, -19.4, .15, 1.0, .3, 10)
    b.flush('site')
    for name, x, y, role in (('car 1', 22.2, -12.0, 'car1'), ('car 2', 22.2, -21.0, 'car2'),
                             ('car 3', -29.6, -30.0, 'car3'), ('car 4', 29.4, 14.0, 'car2')):
        car(name, x, y, role)


def car(name, x, y, role):
    """Simple parked car: lower body, cabin with dark glass, four tyres."""
    b = Batch()
    b.box(role, x, y, .62, 1.8, 4.4, .72)
    b.box(role, x, y - .2, 1.22, 1.6, 2.4, .5)
    b.box('glass', x, y - .2, 1.24, 1.64, 2.2, .4)
    for dx in (-.8, .8):
        for dy in (-1.35, 1.35):
            b.box('hardware', x + dx, y + dy, .34, .3, .66, .62)
    b.flush(name)


def street_trees():
    """Street trees in the sidewalk pits: a trunk, three limbs and a full crown of five overlapping leafy masses."""
    for k, (x, y) in enumerate(TREE_PITS):
        h = 7.0 + (k % 3) * .8
        C.rod('Street tree trunk', (x, y, .1), (x, y, .15 + h * .5), .14, 'bark', 'street trees', 7)
        for j, (dx, dy) in enumerate(((-.6, -.2), (.5, -.1), (.1, .55))):
            tip = (x + dx * 1.4, y + dy * 1.4, .15 + h * .66)
            C.rod('Street tree limb', (x, y, .15 + h * .45), tip, .06, 'bark', 'street trees', 6)
        for j in range(5):
            a = k * 1.3 + j * math.tau / 5
            r = .88 if j else .7
            A.foliage('Street tree crown', (x + .8 * math.cos(a) * (j > 0), y + .8 * math.sin(a) * (j > 0), .15 + h * (.7 + .06 * (j % 2))),
                      (r * 1.5, r * 1.5, r * 1.3), role=('tree', 'tree2')[(k + j) % 2], detail=2)
        A.foliage('Street tree crown', (x, y, .15 + h * .86), (1.1, 1.1, .95), role='tree', detail=2)


def roof_trees():
    """Three small yellow-green trees in the roof garden planter (multi-stem, light crowns)."""
    for k, (x, y) in enumerate(ROOF_TREES):
        z = DECK + .62
        C.rod('Roof tree trunk', (x, y, z - .1), (x, y, z + 2.2), .08, 'bark', 'roof garden', 6)
        for j in range(3):
            a = k * 1.7 + j * 2.1
            A.foliage('Roof tree crown', (x + .5 * math.cos(a), y + .5 * math.sin(a), z + 2.6 + .3 * j), (.9, .9, 1.0),
                      role=('tree3', 'tree')[(j + k) % 2], detail=2)


# ---------------------------------------------------------------- planting (shared kit)
pk_palette(PALETTE)
KIT = None


def walls(poly, wall, z0, z1, role='granite'):
    """Planter wall ring of an orthogonal CCW outline, `wall` thick inside it, as one closed mesh (mitred corners)."""
    n = len(poly)
    def inward(i):
        (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % n]
        L = math.hypot(x1 - x0, y1 - y0)
        return (-(y1 - y0) / L, (x1 - x0) / L)
    inner = []
    for i in range(n):
        a, e = inward(i - 1), inward(i)
        inner.append((poly[i][0] + wall * (a[0] + e[0]), poly[i][1] + wall * (a[1] + e[1])))
    V = [(x, y, z) for z in (z0, z1) for x, y in poly] + [(x, y, z) for z in (z0, z1) for x, y in inner]
    O0, O1, I0, I1 = 0, n, 2 * n, 3 * n
    F = []
    for i in range(n):
        j = (i + 1) % n
        F += [(O1 + i, O1 + j, I1 + j, I1 + i), (O0 + j, O0 + i, I0 + i, I0 + j),
              (O0 + i, O0 + j, O1 + j, O1 + i), (I0 + j, I0 + i, I1 + i, I1 + j)]
    C.mesh('Planter walls', V, F, role, 'planters')


def planting():
    """Raised granite planters of feather-reed grass with straw plumes on the plaza, a low green bed along the east
    sidewalk, and grasses in the roof garden planters (shared planting kit, linked instances)."""
    global KIT
    kit = KIT = PlantKit('planting', instancing=True)
    reed = arching_grass(kit, 'ov_feather_reed', blades=58, height=.85, width=.018, role='pk_straw', crown_role='pk_straw',
                         plume_role='pk_plume', plumes=9, plume_height=1.3, seed=91)
    fountain = arching_grass(kit, 'ov_fountain_grass', blades=60, height=.6, width=.019, crown_role='pk_blade', seed=81)
    low = arching_grass(kit, 'ov_edge_grass', blades=36, height=.3, width=.013, role='pk_blade', crown_role='pk_blade', seed=101)
    shrub = shrub_mass(kit, 'ov_shrub', radius=.5, height=.7, lobes=6, seed=122)
    rnd = random.Random(5)
    b = Batch()
    for i, poly in enumerate(PLANTERS):
        wall = .25
        top = .15 + (.55 if i < 2 else .35)
        soil = top - .08
        ring = _PkPolygon(poly).difference(_PkPolygon(poly).buffer(-wall, join_style=2))
        walls(poly, wall, .1, top)
        inner = _PkPolygon(poly).buffer(-.1, join_style=2)
        C.prism(f'Planter {i} soil', list(inner.exterior.coords)[:-1], 'z', .1, soil - .03, 'soil', 'planters')
        reg = kit.register_bed(pk_region(poly, wall))
        groundcover(f'Planter {i} groundcover', poly, soil, kerb=wall, height=.05, bump=.02, wave=.7, grid=.5, seed=40 + i)
        mix = (reed, reed, fountain) if i < 2 else (shrub, low, low)
        for x, y in pk_scatter(reg, .41 if i < 2 else .5, margin=PK_CLEAR, seed=60 + i):
            p = mix[rnd.randrange(len(mix))]
            s = rnd.uniform(.95, 1.2) if p is reed else rnd.uniform(.9, 1.15)
            kit.place_in(p, x, y, soil, rnd.uniform(0, math.tau), s, region=reg, shrink=(1., .85, .7, .55, .45),
                         sz=(1.55 if p is reed else 1.1) * rnd.uniform(.92, 1.08))
    for x, y in ROOF_TREES:
        kit.add_obstacle(_pksh.Point(x, y).buffer(.25), 3.0)
    for i, (x0, x1, y0, y1) in enumerate(GARDEN):
        poly = ((x0, y0), (x1, y0), (x1, y1), (x0, y1))
        soil = DECK + .62
        b.box('soil', (x0 + x1) / 2, (y0 + y1) / 2, DECK + .3, x1 - x0 - .2, y1 - y0 - .2, .6)
        reg = kit.register_bed(pk_region(poly, .25))
        groundcover(f'Roof garden {i} groundcover', poly, soil, kerb=.25, height=.05, bump=.02, wave=.7, grid=.5, seed=70 + i)
        for x, y in pk_scatter(reg, .65, margin=PK_CLEAR, seed=80 + i):
            p = (fountain, reed, low)[rnd.randrange(3)]
            kit.place_in(p, x, y, soil, rnd.uniform(0, math.tau), rnd.uniform(1.0, 1.35), region=reg, shrink=(1., .8, .6))
    b.flush('planters')
    kit.flush()
    bad = kit.audit(detail=True)
    if bad:
        raise RuntimeError(f'planting kit clearance rule: {len(bad)} placements cross a kerb or obstacle: {bad[:12]}')


# ---------------------------------------------------------------- interiors and context
def interiors():
    """Lobby desk, gym equipment rows behind the frame box, penthouse lounge seating; inspection lights everywhere
    behind glazing and inside the climbing shell."""
    b = Batch()
    b.box('timber', -14.2, -13.8, G0 + .55, 3.6, .9, 1.1)                                              # reception desk
    b.box('coping', -14.2, -13.8, G0 + 1.12, 3.8, 1.0, .05)
    for z in (F2, F3):
        for x in (-21.5, -19.6, -17.7, -15.8, -13.9):
            b.box('frame', x, -15.6, z + .55, .8, 1.9, 1.1)                                             # treadmills
            b.box('frame', x, -16.35, z + 1.25, .7, .1, .5)
    for y in (-14.0, -10.0, -6.0):                                                                      # penthouse lounge
        b.box('timber', -3.4, y, DECK + .25, .9, 2.4, .5)
        b.box('timber', -2.95, y, DECK + .6, .2, 2.4, .7)
    b.flush('interiors')
    for k, (x, y) in enumerate(((-18.0, -14.0), (-18.0, -2.0), (-18.0, 10.0), (-8.0, -14.0), (0.0, -14.0), (10.0, -14.0),
                                (10.0, 0.0), (10.0, 12.0), (-8.0, 12.0))):
        for z in (G0 + 4.2, F2 + 3.8, F3 + 3.8):
            qa_light(f'room {k} {z:.1f}', (x, y, z), 90, 2.5)
        if x > XE:
            qa_light(f'room {k} top', (x, y, F4 + 3.8), 90, 2.5)
    for y in (-14.0, -4.0, 6.0):
        qa_light(f'penthouse {y:.0f}', (-1.0, y, PH_TOP - .7), 110, 2.5)
    qa_light('shell hollow', (-1.0, -22.5, 18.0), 40, 8.0)                                            # inside the shell (dim)


def window_bands(m, lo, hi, z0, z1, floors, per, role='stone'):
    """Context windows on a solid face (Merge in face coordinates), per floor: one lit room band, one glass band 2 cm
    in front of it, a head band and a sill band standing 10 cm proud, and piers 12 cm proud between the windows."""
    n = max(1, int((hi - lo) / per))
    for j in range(floors):
        z = z0 + (z1 - z0) * j / floors + .9
        m.box('interior', (lo + hi) / 2, -.01, z + 1.0, hi - lo, .012, 2.0)
        m.box('glass', (lo + hi) / 2, -.035, z + 1.0, hi - lo, .008, 2.0)
        m.box(role, (lo + hi) / 2, -.06, z + 2.08, hi - lo + .2, .14, .18)
        m.box(role, (lo + hi) / 2, -.07, z - .07, hi - lo + .2, .16, .14)
        for k in range(n + 1):
            m.box(role if k in (0, n) else 'frame', lo + (hi - lo) * k / n, -.05, z + 1.0, .5 if k in (0, n) else .1, .12 if k in (0, n) else .1, 2.02)


def context():
    """Brick mid-rise blocks across the east and west streets, taller residential blocks to the north."""
    blocks = (('east block 1', 35.0, 62.0, -40.0, 2.0, 21.0, 'brick', 'x0'), ('east block 2', 35.0, 62.0, 4.0, 42.0, 18.0, 'brick2', 'x0'),
              ('west block 1', -68.0, -42.0, -40.0, -2.0, 14.0, 'brick', 'x1'), ('west block 2', -68.0, -42.0, 0.0, 40.0, 16.5, 'brick2', 'x1'),
              ('north block 1', -40.0, -12.0, 35.0, 62.0, 27.0, 'ctx', 'y0'), ('north block 2', -9.0, 22.0, 35.0, 64.0, 32.0, 'brick2', 'y0'),
              ('north block 3', 26.0, 60.0, 46.0, 70.0, 24.0, 'ctx2', 'y0'), ('south block', -30.0, 20.0, -78.0, -54.0, 12.0, 'ctx', 'y1'))
    b = Batch()
    for name, x0, x1, y0, y1, h, role, face in blocks:
        b.box(role, (x0 + x1) / 2, (y0 + y1) / 2, h / 2, x1 - x0, y1 - y0, h)
        b.box('membrane', (x0 + x1) / 2, (y0 + y1) / 2, h + .03, x1 - x0 - .6, y1 - y0 - .6, .06)
        b.box('mech', (x0 + x1) / 2 + 2.0, (y0 + y1) / 2, h + .6, 2.4, 1.6, 1.2)
    b.flush('context')
    for name, x0, x1, y0, y1, h, role, face in blocks:
        floors = max(1, int((h - 4.0) / 3.2))
        if face == 'x0':
            f = C.Face((x0, 0, 0), (0, -1, 0), (1, 0, 0), name + ' west face'); lo, hi = -y1 + .6, -y0 - .6
        elif face == 'x1':
            f = C.Face((x1, 0, 0), (0, 1, 0), (-1, 0, 0), name + ' east face'); lo, hi = y0 + .6, y1 - .6
        elif face == 'y0':
            f = C.Face((0, y0, 0), (1, 0, 0), (0, 1, 0), name + ' south face'); lo, hi = x0 + .6, x1 - .6
        else:
            f = C.Face((0, y1, 0), (-1, 0, 0), (0, -1, 0), name + ' north face'); lo, hi = -x1 + .6, -x0 - .6
        m = Merge(f)
        window_bands(m, lo, hi, 3.6, h - .6, floors, 2.6, role='stone' if 'brick' in role else 'paint')
        for k in range(int((hi - lo) / 5.0)):
            m.box('glass', lo + 2.5 + k * 5.0, -.03, 1.6, 3.6, .04, 2.6)
            m.box('frame', lo + 2.5 + k * 5.0, -.06, 3.1, 4.2, .1, .3)
        m.flush(name)


def build():
    site()
    building_mass()
    fronts()
    pool_deck()
    penthouse()
    east_roof()
    tris, inner = shell()
    holds(tris, inner)
    climbers(tris)
    street_trees()
    roof_trees()
    planting()
    interiors()
    context()
    C.CONTACTS.append(dict(name='The Overhang climbing building', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(-46, -30, 34), fill=(85, -95, 55), rear=(5, 70, 40), target=(-3, -12, 8.0), gain=4.8)
