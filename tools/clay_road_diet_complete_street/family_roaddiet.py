"""Road-diet complete street option, authored from the locked catalogue views of road_diet_complete_street /
variant_0.

Read from the pixels (the top view governs the plan): a former four-lane arterial running north-south through a
neighbourhood intersection, re-striped and rebuilt as a complete street. The main-street section from the west: a
grass verge with mature street trees and black lamp standards; a green-painted protected bike lane at road level
against the curb; a raised concrete separator island with white flexible delineator posts and a yellow-and-black
rubber curb stop at its nose; one travel lane each way either side of a centre two-way left-turn lane (solid outer and
dashed inner yellow lines, white turn arrows); the same separator and green bike lane on the east side; a wide east
sidewalk with trees in pits in front of one- and two-storey storefront blocks. At the crossing street, continental
zebra crosswalks span every leg (over the bike lanes too); in the centre lane beyond each main-street crosswalk a
raised pedestrian refuge island planted with tall grasses carries a keep-right sign and a yellow-and-black object
marker at its nose. The cross street has one travel lane each way with a dashed yellow centre line, painted buffers
and green bike lanes at the curbs. Signal poles with mast arms at the corners. Flat-roofed one- and two-storey
commercial and office blocks at the corners (the north-east one a storefront row in front of a four-storey brick
apartment block with balconies) are the street wall the section is read with; the blocks further out are context.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-road-diet-complete-street'
SWZ = .15                                       # sidewalk and island tops: 150 mm curb
TW = 1.8                                        # half width of the centre two-way left-turn lane (3.6 m)
LANE = 3.4                                      # main-street travel lanes
SEP = .9                                        # raised concrete separator
BIKE = 2.0                                      # green bike lane
X_TW = TW                                       # turn-lane edge |x|
X_SEP0 = TW + LANE                              # separator inner edge |x| = 5.2
X_SEP1 = X_SEP0 + SEP                           # separator outer edge = 6.1
A_CURB = X_SEP1 + BIKE                          # main-street curb |x| = 8.1
B_CURB = 5.6                                    # cross-street curb |y|
CR_LANE, CR_BUF = 3.2, .6                       # cross-street travel lane, painted buffer; green bike lane from 3.8 to the curb
R_RET = 3.0                                     # corner curb-return radius
XWALK = (B_CURB + R_RET + .2, B_CURB + R_RET + 3.2)   # main-street crosswalks |y| = 8.8..11.8
YWALK = (A_CURB + R_RET + .2, A_CURB + R_RET + 3.2)   # cross-street crosswalks |x| = 11.3..14.3
EAST_BL = 11.5                                  # east building line (3.4 m sidewalk)
VERGE = (A_CURB, 10.5)                          # west grass verge |x|
WSW = (10.5, 12.6)                              # west sidewalk |x|
WEST_BL = 16.0                                  # west building line, set back behind lawns
CROSS_BL = 8.6                                  # building line on the cross street (3.0 m sidewalk)
N_END, S_END, E_END, W_END = 80.0, -48.0, 48.0, -48.0
T = .4
EPS = .002
PALETTE = dict(wall=(.58, .31, .21), brick=(.58, .31, .21), joint=(.70, .64, .56), stone=(.80, .76, .66), cream=(.84, .78, .64),
    white=(.93, .92, .88), trim=(.93, .92, .88), frame=(.16, .17, .18), dark=(.15, .16, .17), sign=(.22, .26, .30),
    glass=(.20, .25, .27), interior=(.82, .78, .72), floor=(.56, .46, .36), roof=(.60, .57, .52), membrane=(.74, .73, .70),
    concrete=(.76, .75, .72), curbstone=(.82, .81, .78), sidejoint=(.60, .59, .56), asphalt=(.26, .26, .27),
    marking=(.94, .94, .92), yellow=(.88, .70, .16), green=(.30, .58, .36), hardware=(.08, .08, .09), post=(.92, .92, .90),
    rubber=(.12, .12, .12), signal=(.80, .64, .14), timber=(.40, .30, .21), tree=(.32, .46, .20), planting=(.33, .47, .22),
    grasses=(.62, .58, .36), soil=(.24, .18, .12), grass=(.42, .54, .28), stucco=(.83, .77, .64),
    neighbour=(.62, .42, .32), context=(.80, .78, .72), car=(.62, .63, .64), car2=(.18, .22, .28), car3=(.70, .66, .58), tyre=(.07, .07, .07),
    pale=(.88, .88, .86), blue=(.20, .30, .40))


def manifest(version):
    h = 14.0
    cams = G.camera_roster(E_END - W_END, N_END - S_END, h, [
        ('bike_lane_separator', (-7.3, 22.0, 1.5), (-6.6, 40.0, .6), 30),
        ('refuge_island', (-3.6, 6.5, 1.7), (0.0, 13.6, 1.0), 30),
        ('crosswalk_zebra', (-4.0, 3.0, 5.0), (1.5, 10.3, 0.0), 26),
        ('bike_symbol', (-7.1, -24.0, 3.4), (-7.1, -18.0, 0.0), 32),
        ('turn_lane', (4.0, -10.0, 9.0), (0.0, -28.0, 0.0), 30),
        ('storefronts', (7.0, 17.0, 1.7), (11.5, 22.0, 3.0), 30),
        ('corner_signal', (2.0, -2.0, 3.5), (9.5, 7.0, 3.5), 30),
        ('cross_street_lane', (12.5, -2.5, 2.2), (30.0, 4.6, .4), 30),
        ('verge_trees', (-13.5, -10.0, 1.7), (-9.5, -28.0, 3.5), 30),
        ('rubber_curb', (-7.4, 10.6, 1.4), (-5.6, 13.4, .2), 32)])
    for c in cams:
        if c['name'] == 'front':                                               # the locked front: eye level in the west bike lane at the north crosswalk, looking north
            c.update(location=(-7.4, 6.2, 1.6), target=(-2.4, 40.0, 3.4), lens=24, whole=False)
        elif c['name'] == 'front_corner':                                      # the locked oblique: high over the intersection's south-east, looking north up the main street
            c.update(location=(-19.0, -2.0, 30.0), target=(6.0, 42.0, 0.0), lens=26, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(-40.0, -55.0, 50.0), target=(0.0, 4.0, 0.0), lens=28, whole=False)
        elif c['name'] == 'top':                                               # the locked top view: north up, the intersection at the centre
            c.update(location=(0.0, 0.0, 150.0), target=(0.0, .001, 0.0), ortho_scale=92.0, whole=False)
        elif c['name'] == 'left_side':                                         # along the cross street from the west
            c.update(location=(-46.0, -3.0, 6.0), target=(0.0, 2.0, 2.0), lens=28, whole=False)
        elif c['name'] == 'right_side':                                        # along the cross street from the east
            c.update(location=(46.0, 3.0, 6.0), target=(0.0, -2.0, 2.0), lens=28, whole=False)
        elif c['name'] == 'rear':                                              # down the main street from the north
            c.update(location=(2.0, 58.0, 14.0), target=(0.0, 0.0, 1.0), lens=26, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(-38.0, 50.0, 34.0), target=(0.0, 0.0, 0.0), lens=28, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='road_diet_complete_street/variant_0, a four-lane arterial converted to a complete street at a neighbourhood intersection',
        measurement_contract=dict(dimensions_m=dict(width=E_END - W_END, depth=N_END - S_END, height=h),
            observed_storeys=2, storey_programme='street option: a complete-street section at an intersection; the one- and two-storey corner blocks are the street wall it is read with',
            plan=f'{2 * A_CURB:.1f} m main street curb to curb and {2 * B_CURB:.1f} m cross street curb to curb (top view), the intersection at the centre',
            section_m=dict(west_verge=[-VERGE[1], -VERGE[0]], west_sidewalk=[-WSW[1], -WSW[0]], west_bike_lane=[-A_CURB, -X_SEP1], west_separator=[-X_SEP1, -X_SEP0],
                           southbound_lane=[-X_SEP0, -X_TW], centre_turn_lane=[-X_TW, X_TW], northbound_lane=[X_TW, X_SEP0], east_separator=[X_SEP0, X_SEP1],
                           east_bike_lane=[X_SEP1, A_CURB], east_sidewalk=[A_CURB, EAST_BL], cross_street_lane=[0.0, CR_LANE], cross_street_buffer=[CR_LANE, CR_LANE + CR_BUF],
                           cross_street_bike_lane=[CR_LANE + CR_BUF, B_CURB], curb_height=SWZ, curb_return_radius=R_RET, refuge_island_width=2.8),
            facade='green protected bike lanes behind raised concrete separators with white delineator posts and rubber curb stops, a centre two-way turn lane with yellow lines, continental zebra crosswalks, planted refuge islands with keep-right signs and object markers, grass verges with mature trees, black lamp standards, signal mast arms; one- and two-storey storefront and office blocks',
            levels_m=[0.0, SWZ, 4.6, 7.6, 13.4], inferred='the blocks beyond the corners and their rear walls and interiors are context and teaching assumptions; the signal heads are generic'),
        roof_contract=dict(type='flat membrane roofs inside parapets with copings and rooftop units', datum_m=7.0, crowns_m=[13.4]),
        identity_contract=dict(owner='road-diet complete street: one travel lane each way and a centre turn lane where four lanes were, green bike lanes protected by raised separators with posts, zebra crosswalks and planted refuge islands'),
        material_contract=dict(profile='source-palette clay: dark asphalt, green bike-lane paint, white and yellow markings, pale concrete curbs, separators and sidewalks, grass verges, tall straw-coloured grasses, white posts, yellow-black markers, black lamp and signal poles, red-brick and beige storefront blocks', textured_keeper=False),
        programme_contract=dict(storeys=2, ground='shops and services on the corners', upper='offices and flats'),
        street_contract=dict(kind='fixed_native_section', width_m=2 * A_CURB, axis='y', junction_finish='continental zebra crosswalks and refuge islands',
                             bands=['west_verge', 'west_sidewalk', 'west_bike_lane', 'west_separator', 'southbound_lane', 'centre_turn_lane', 'northbound_lane', 'east_separator', 'east_bike_lane', 'east_sidewalk', 'east_storefronts']),
        contact_contract=['Asphalt at grade zero', 'Sidewalks, separators and refuge islands on the asphalt with a 150 mm curb', 'Paint on the asphalt', 'Building walls from grade with the sidewalk running under them', 'Trees in the verge and in pits'],
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


# ---- road-diet complete street ----

import random

ZM = .0235                                      # marking centre on asphalt: 19..28 mm (asphalt top 20 mm)
ZG = .0225                                      # green paint centre: 19..26 mm
ZW = .0275                                      # white paint over green (zebra, bike symbols): 23..32 mm
GRASS_Z = (SWZ - .004, SWZ + .012)              # lawn layer on the concrete base
ISL = (1.3, 12.6, 19.0)                         # refuge islands: half width, near and far |y|
STOP_Y = 12.25                                  # main-street stop bars |y|
STOP_X = 14.8                                   # cross-street stop bars |x|
CURB_STOP = (12.2, 14.4)                        # rubber curb stops between the crosswalk and each separator, |y|
SEP_START = 14.6                                # concrete separators start |y|


def arc(cx, cy, r, a0, a1, n=8):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def quadrant(sx, sy):
    """One corner's concrete in plan: everything behind both curbs, with the curb return at the corner."""
    yf = N_END if sy > 0 else -S_END
    xf = E_END if sx > 0 else -W_END
    pts = [(A_CURB, yf), (A_CURB, B_CURB + R_RET)] + arc(A_CURB + R_RET, B_CURB + R_RET, R_RET, 180.0, 270.0) + [(xf, B_CURB), (xf, yf)]
    return [(sx * x, sy * y) for x, y in pts]


def ground():
    C.prism('Street asphalt', [(W_END, S_END), (E_END, S_END), (E_END, N_END), (W_END, N_END)], 'z', 0.0, .02, 'asphalt', 'street')
    for sx in (1, -1):
        for sy in (1, -1):
            C.prism(f'Sidewalk and lots {sx:+d}{sy:+d}', quadrant(sx, sy), 'z', .005, SWZ, 'concrete', 'sidewalks')
    b = Batch()
    gz, gh = (GRASS_Z[0] + GRASS_Z[1]) / 2, GRASS_Z[1] - GRASS_Z[0]
    for y0, y1 in ((12.6, N_END - .3), (S_END + .3, -12.6)):                                 # west grass verge, mature trees and lamps
        b.box('grass', -(VERGE[0] + .35 + VERGE[1]) / 2, (y0 + y1) / 2, gz, VERGE[1] - VERGE[0] - .35, y1 - y0, gh)
    for y0, y1 in ((CROSS_BL + 1.0, N_END - .3), (S_END + .3, -CROSS_BL - 1.0)):             # west lawns between the sidewalk and the set-back blocks
        b.box('grass', -(WSW[1] + .1 + WEST_BL - .3) / 2, (y0 + y1) / 2, gz, WEST_BL - .3 - WSW[1] - .1, y1 - y0, gh)
    b.box('grass', -(WEST_BL + 36.0) / 2, (CROSS_BL + 1.0 + 15.5) / 2, gz, 36.0 - WEST_BL, 15.5 - CROSS_BL - 1.0, gh)   # lawn in front of the north-west office
    for k in range(int((N_END - 12.0) / 1.6)):                                                # scored sidewalk joints
        y = 12.4 + k * 1.6
        b.box('sidejoint', (A_CURB + EAST_BL) / 2, y, SWZ, EAST_BL - A_CURB - .3, .02, .004)
        b.box('sidejoint', -(WSW[0] + WSW[1]) / 2, y, SWZ, WSW[1] - WSW[0] - .2, .02, .004)
    for k in range(int((-S_END - 12.0) / 1.6)):
        y = -12.4 - k * 1.6
        b.box('sidejoint', (A_CURB + EAST_BL) / 2, y, SWZ, EAST_BL - A_CURB - .3, .02, .004)
        b.box('sidejoint', -(WSW[0] + WSW[1]) / 2, y, SWZ, WSW[1] - WSW[0] - .2, .02, .004)
    for sx in (1, -1):
        for k in range(int((E_END - 12.0) / 1.6)):
            x = sx * (12.4 + k * 1.6)
            for sy in (1, -1):
                b.box('sidejoint', x, sy * (B_CURB + CROSS_BL) / 2, SWZ, .02, CROSS_BL - B_CURB - .3, .004)
    b.flush('ground layers')


def zebra(b, x0, x1, y0, y1, along):
    """Continental crosswalk: bars 0.5 m wide, 0.5 m apart, running along the walking direction."""
    if along == 'y':                                      # crossing the main street: bars run north-south, stepped across x
        n = int((x1 - x0) / 1.0)
        for i in range(n):
            x = x0 + .5 + i * 1.0
            b.box('marking', x, (y0 + y1) / 2, ZW, .5, y1 - y0, .009)
    else:
        n = int((y1 - y0) / 1.0)
        for i in range(n):
            y = y0 + .5 + i * 1.0
            b.box('marking', (x0 + x1) / 2, y, ZW, x1 - x0, .5, .009)


def bike_symbol(b, x, y, along):
    """White bicycle on the green: two wheels, frame, bars and saddle; wheels are real rings."""
    ux, uy = (0.0, 1.0) if along == 'y' else (1.0, 0.0)
    w0 = (x - ux * .55, y - uy * .55); w1 = (x + ux * .55, y + uy * .55)
    for cx, cy in (w0, w1):
        annulus('Bike symbol wheel', (cx, cy, 0.0), (0, 0, 1), .30, .37, .0245, .031, 'marking', 'road markings', 16)
    p = lambda a, c: (x + ux * a + (-uy) * c, y + uy * a + ux * c, ZW + .001)
    for a, c in (((-.55, 0), (-.05, .32)), ((-.05, .32), (.55, 0)), ((-.55, 0), (.05, 0)), ((.05, 0), (-.05, .32)), ((.05, 0), (.4, .36)), ((-.15, .32), (-.15, .42))):
        b.beam('marking', p(*a), p(*c), .07, .009)
    b.beam('marking', p(.3, .42), p(.5, .3), .07, .009)


def arrow(b, x, y, dirn, turn=0):
    """White lane arrow pointing along +y (dirn=1) or -y (dirn=-1); turn=-1 hooks to the driver's left."""
    s = dirn
    b.box('marking', x, y, ZM, .16, 2.2, .009)
    if turn == 0:
        C.prism('Lane arrow head', [(x - .45, y + s * 1.1), (x + .45, y + s * 1.1), (x, y + s * 2.2)], 'z', ZM - .0045, ZM + .0045, 'marking', 'road markings')
    else:
        hx = -s                                              # driver's left for a vehicle heading +y is -x
        b.box('marking', x + hx * .4, y + s * 1.05, ZM, .8, .16, .009)
        C.prism('Turn arrow head', [(x + hx * .75, y + s * .6), (x + hx * .75, y + s * 1.5), (x + hx * 1.45, y + s * 1.05)], 'z', ZM - .0045, ZM + .0045, 'marking', 'road markings')


def markings():
    b = Batch()
    # Green bike lanes: main street at the curbs behind the separators; cross street at the curbs behind painted buffers.
    for sx in (1, -1):
        xc = sx * (X_SEP1 + A_CURB) / 2
        for y0, y1 in ((B_CURB + R_RET + .1, N_END - .05), (S_END + .05, -B_CURB - R_RET - .1)):
            b.box('green', xc, (y0 + y1) / 2, ZG, BIKE - .04, y1 - y0, .007)
    for sy in (1, -1):
        yc = sy * (CR_LANE + CR_BUF + B_CURB) / 2
        for x0, x1 in ((A_CURB + R_RET + .1, E_END - .05), (W_END + .05, -A_CURB - R_RET - .1)):
            b.box('green', (x0 + x1) / 2, yc, ZG, x1 - x0, B_CURB - CR_LANE - CR_BUF - .04, .007)
    # Centre two-way left-turn lane: solid outer and dashed inner yellow lines both sides.
    for y0, y1 in ((STOP_Y + .3, N_END - .1), (S_END + .1, -STOP_Y - .3)):
        for sx in (1, -1):
            b.box('yellow', sx * (TW - .1), (y0 + y1) / 2, ZM, .12, y1 - y0, .009)
            n = int((y1 - y0) / 4.0)
            for k in range(n):
                ya = y0 + .5 + k * 4.0
                b.box('yellow', sx * (TW - .36), ya + 1.0, ZM, .12, 2.0, .009)
    # Opposing left-turn arrows in the centre lane, and straight arrows in the travel lanes.
    arrow(b, .55, 30.0, 1, -1); arrow(b, -.55, 36.0, -1, -1)
    arrow(b, .55, -36.0, 1, -1); arrow(b, -.55, -30.0, -1, -1)
    arrow(b, (TW + X_SEP0) / 2, -22.0, 1); arrow(b, -(TW + X_SEP0) / 2, 22.0, -1)
    # Stop bars.
    b.box('marking', -(TW + X_SEP0) / 2, STOP_Y, ZM, X_SEP0 - TW - .2, .45, .009)
    b.box('marking', (TW + X_SEP0) / 2, -STOP_Y, ZM, X_SEP0 - TW - .2, .45, .009)
    b.box('marking', -STOP_X, -CR_LANE / 2, ZM, .45, CR_LANE - .25, .009)
    b.box('marking', STOP_X, CR_LANE / 2, ZM, .45, CR_LANE - .25, .009)
    # Continental crosswalks over every leg (over the bike lanes too).
    for sy in (1, -1):
        zebra(b, -A_CURB + .25, A_CURB - .25, sy * XWALK[0] if sy > 0 else -XWALK[1], XWALK[1] if sy > 0 else -XWALK[0], 'y')
    for sx in (1, -1):
        zebra(b, YWALK[0] if sx > 0 else -YWALK[1], YWALK[1] if sx > 0 else -YWALK[0], -B_CURB + .25, B_CURB - .25, 'x')
    # Cross street: dashed yellow centre line, painted buffer lines with diagonal hatching.
    for sx in (1, -1):
        for k in range(int((E_END - STOP_X - 1.0) / 6.0)):
            xa = sx * (STOP_X + 1.0 + k * 6.0 + 1.5)
            b.box('yellow', xa, 0.0, ZM, 3.0, .12, .009)
        x0, x1 = (STOP_X + .6, E_END - .1) if sx > 0 else (W_END + .1, -STOP_X - .6)
        for sy in (1, -1):
            for yy in (CR_LANE + .06, CR_LANE + CR_BUF - .06):
                b.box('marking', (x0 + x1) / 2, sy * yy, ZM, x1 - x0, .1, .009)
            for k in range(int((x1 - x0) / 2.5)):
                xh = x0 + 1.0 + k * 2.5
                b.beam('marking', (xh - .2, sy * (CR_LANE + .12), ZM), (xh + .2, sy * (CR_LANE + CR_BUF - .12), ZM), .1, .009)
    # Bicycle symbols on the green.
    for sx in (1, -1):
        for y in (20.0, 52.0, -20.0, -40.0):
            bike_symbol(b, sx * (X_SEP1 + A_CURB) / 2, y, 'y')
    for sy in (1, -1):
        for x in (22.0, 40.0, -22.0, -40.0):
            bike_symbol(b, x, sy * (CR_LANE + CR_BUF + B_CURB) / 2, 'x')
    b.flush('road markings')


def post(b, x, y, z0, h=.9):
    """White flexible delineator post with a grey reflective band and a black base."""
    b.box('rubber', x, y, z0 + .03, .2, .2, .06)
    b.box('post', x, y, z0 + .06 + h / 2, .09, .09, h)
    b.box('pale', x, y, z0 + .06 + h - .2, .1, .1, .1)


def separators():
    """Raised concrete separators between the travel lanes and the green bike lanes, with posts; rubber curb stops with
    yellow chevrons and posts in the gap at each crosswalk; the planted refuge islands with signs and object markers."""
    b = Batch()
    for sx in (1, -1):
        xc = sx * (X_SEP0 + X_SEP1) / 2
        for y0, y1 in ((SEP_START, N_END - .3), (S_END + .3, -SEP_START)):
            b.box('curbstone', xc, (y0 + y1) / 2, (.005 + SWZ) / 2, SEP, y1 - y0, SWZ - .005)
            k0 = y0 + 3.0 if y0 > 0 else y0 + 4.0
            for k in range(int((y1 - y0 - 6.0) / 9.0) + 1):
                post(b, xc, k0 + k * 9.0, SWZ - .01)
        for sy in (1, -1):
            ya, yc = sy * CURB_STOP[0], sy * CURB_STOP[1]
            b.box('rubber', xc, (ya + yc) / 2, .055, .32, abs(yc - ya), .1)
            for k in range(5):
                yy = sy * (CURB_STOP[0] + .25 + k * .45)
                b.box('yellow', xc, yy, .056, .34, .18, .104)
            for k in range(3):
                post(b, xc, sy * (CURB_STOP[0] + .35 + k * .8), .095)
    for sy in (1, -1):                                                                         # cross-street buffer posts
        for sx in (1, -1):
            for k in range(5):
                post(b, sx * (STOP_X + 4.0 + k * 6.0), sy * (CR_LANE + CR_BUF / 2), .015)
    b.flush('separators and posts')
    g = Batch()
    rng = random.Random(7)
    for sy in (1, -1):
        y0, y1 = sorted((sy * ISL[1], sy * ISL[2]))
        g.box('curbstone', 0.0, (y0 + y1) / 2, (.005 + SWZ) / 2, 2 * ISL[0], y1 - y0, SWZ - .005)
        g.box('soil', 0.0, (y0 + y1) / 2, (SWZ - .01 + SWZ + .016) / 2, 2 * ISL[0] - .4, y1 - y0 - .4, .026)
        for i in range(12):                                                                    # tall straw grasses in clumps
            cx = rng.uniform(-ISL[0] + .45, ISL[0] - .45)
            cy = rng.uniform(y0 + .6, y1 - .6)
            for j in range(9):
                a = math.tau * j / 9 + rng.uniform(-.2, .2)
                h = rng.uniform(.8, 1.25)
                lean = rng.uniform(.12, .32)
                g.beam('grasses', (cx, cy, SWZ + .01), (cx + math.cos(a) * lean, cy + math.sin(a) * lean, SWZ + h), .07, .03)
            g.box('planting', cx, cy, SWZ + .14, .38, .38, .26)
        # Keep-right sign and object marker at the nose facing the intersection; a second sign at the far nose.
        for ny, face in ((sy * (ISL[1] + .35), -sy), (sy * (ISL[2] - .35), sy)):
            g.box('hardware', 0.0, ny, SWZ + 1.3, .07, .07, 2.6)
            g.box('marking', 0.0, ny + face * .05, SWZ + 2.25, .6, .03, .75)
            g.beam('dark', (-.12, ny + face * .07, SWZ + 2.0), (.12, ny + face * .07, SWZ + 2.36), .07, .01)     # black keep-right arrow on white
            g.beam('dark', (.15, ny + face * .07, SWZ + 2.39), (.0, ny + face * .07, SWZ + 2.47), .07, .01)
            g.beam('dark', (.15, ny + face * .07, SWZ + 2.39), (.15, ny + face * .07, SWZ + 2.22), .07, .01)
            g.box('dark', 0.0, ny + face * .07, SWZ + 2.6, .56, .01, .03)
            g.box('dark', 0.0, ny + face * .07, SWZ + 1.9, .56, .01, .03)
            g.box('yellow', 0.0, ny + face * .05, SWZ + .85, .3, .03, .9)
            for k in range(4):
                zz = SWZ + .5 + k * .22
                g.beam('rubber', (-.13, ny + face * .07, zz), (.13, ny + face * .07, zz + .16), .06, .01)
    g.flush('refuge islands')


def lamp(b, x, y, z, toward):
    """Black cobra-head street lamp: base, pole, arm over the road, head."""
    b.box('hardware', x, y, z + .19, .38, .38, .42)
    b.box('hardware', x, y, z + 4.4, .16, .16, 8.4)
    b.beam('hardware', (x, y, z + 8.3), (x + toward * 2.2, y, z + 8.6), .1, .1)
    b.box('hardware', x + toward * 2.45, y, z + 8.55, .75, .3, .16)
    b.box('pale', x + toward * 2.45, y, z + 8.46, .6, .22, .03)


def signal_pole(b, x, y, ax, ay, reach):
    """Signal pole with a mast arm reaching over the road along (ax, ay); two three-lamp heads on it."""
    z = SWZ
    b.box('hardware', x, y, z + .24, .5, .5, .52)
    b.box('hardware', x, y, z + 3.6, .24, .24, 7.2)
    b.beam('hardware', (x, y, z + 6.7), (x + ax * reach, y + ay * reach, z + 6.85), .14, .16)
    b.beam('hardware', (x, y, z + 5.6), (x + ax * 2.0, y + ay * 2.0, z + 6.7), .07, .07)
    for f in (.55, .92):
        hx, hy = x + ax * reach * f, y + ay * reach * f
        b.box('hardware', hx, hy, z + 6.6, .06, .06, .3)
        b.box('signal', hx, hy, z + 5.95, .36 if ax else .34, .34 if ax else .36, 1.05)
        fx, fy = (-ay, ax)                                              # lamps face the traffic approaching the pole's corner
        for k in range(3):
            b.box('dark', hx + fx * .18, hy + fy * .18, z + 6.3 - k * .33, .2 if ax else .02, .02 if ax else .2, .2)
    b.box('signal', x - ay * .2, y + ax * .2, z + 2.6, .25, .25, .55)            # pedestrian head on the pole
    b.box('dark', x - ay * .33, y + ax * .33, z + 2.6, .16 if ax else .02, .02 if ax else .16, .4)


def car(b, x, y, ux, uy, role):
    """A plain clay car: body, glass cabin with a roof, four wheels; heading (ux, uy)."""
    vx, vy = -uy, ux
    a = (x - ux * 2.25, y - uy * 2.25)
    f = (x + ux * 2.25, y + uy * 2.25)
    b.beam(role, (a[0], a[1], .64), (f[0], f[1], .64), 1.78, .64)
    b.beam('glass', (x - ux * 1.25, y - uy * 1.25, 1.14), (x + ux * .95, y + uy * .95, 1.14), 1.6, .46)
    b.beam(role, (x - ux * 1.2, y - uy * 1.2, 1.385), (x + ux * .9, y + uy * .9, 1.385), 1.52, .06)
    for s in (-1.42, 1.42):
        for t in (-.8, .8):
            cx, cy = x + ux * s + vx * t, y + uy * s + vy * t
            b.beam('tyre', (cx - vx * .13, cy - vy * .13, .335), (cx + vx * .13, cy + vy * .13, .335), .62, .62)


def furniture():
    b = Batch()
    gz = GRASS_Z[1]
    for y in (22.0, 42.0, 62.0, -22.0, -42.0):
        lamp(b, -9.35, y, gz, 1)
    for y in (32.0, 55.0, -32.0):
        lamp(b, 8.65, y, SWZ, -1)
    signal_pole(b, 10.0, 7.6, -1, 0, 7.5)
    signal_pole(b, -10.0, -7.6, 1, 0, 7.5)
    signal_pole(b, -10.0, 7.6, 0, -1, 6.2)
    signal_pole(b, 10.0, -7.6, 0, 1, 6.2)
    for x, y in ((9.2, 9.6), (-9.2, -9.6)):                                       # bike-lane regulatory sign on a post at the corner
        b.box('hardware', x, y, SWZ + 1.4, .07, .07, 2.8)
        b.box('marking', x, y, SWZ + 2.45, .03, .5, .65)
    for x, y in ((9.6, 20.0), (9.6, 46.0), (9.6, -24.0)):                         # bins and bike racks on the east sidewalk
        b.box('hardware', x, y, SWZ + .46, .5, .5, .92)
        b.box('dark', x, y, SWZ + .95, .56, .56, .08)
        for dy in (-.35, .35):
            b.box('hardware', x, y + 2.0 + dy, SWZ + .45, .05, .05, .92)
        b.box('hardware', x, y + 2.0, SWZ + .89, .05, .75, .05)
    b.flush('street furniture')
    for y in (16.0, 27.0, 38.0, 49.0, 60.0, 71.0, -16.0, -27.0, -38.0):          # mature trees on the west verge
        street_tree(-9.4, y, z=gz, height=10.0, spread=3.0)
    t = Batch()
    for y in (16.5, 28.5, 40.5, -16.5, -28.5, -40.5):                             # young trees in pits on the east sidewalk
        t.box('soil', 9.5, y, SWZ + .0055, 1.2, 1.2, .015)
        street_tree(9.5, y, z=SWZ + .01, height=7.0, spread=1.7)
    for sx in (1, -1):
        for sy in (1, -1):
            for x in (24.0, 38.0):
                t.box('soil', sx * x, sy * 7.5, SWZ + .0055, 1.1, 1.1, .015)
                street_tree(sx * x, sy * 7.5, z=SWZ + .01, height=7.5, spread=1.8)
    t.flush('tree pits')
    c = Batch()
    car(c, -(TW + X_SEP0) / 2, 26.0, 0.0, -1.0, 'car')
    car(c, -(TW + X_SEP0) / 2, 44.0, 0.0, -1.0, 'car2')
    car(c, (TW + X_SEP0) / 2, -24.0, 0.0, 1.0, 'car3')
    car(c, -26.0, -CR_LANE / 2, 1.0, 0.0, 'car2')
    car(c, 30.0, CR_LANE / 2, -1.0, 0.0, 'car')
    c.flush('cars')


# ---- the corner blocks ----

def face_for(side, x0, x1, y0, y1):
    """Face on one side of a rectangular block, with its u span between corner piers."""
    if side == 'W':
        return C.Face((x0, 0.0, 0.0), (0, 1, 0), (1, 0, 0), 'W'), (y0 + .25, y1 - .25)
    if side == 'E':
        return C.Face((x1, 0.0, 0.0), (0, -1, 0), (-1, 0, 0), 'E'), (-(y1 - .25), -(y0 + .25))
    if side == 'S':
        return C.Face((0.0, y0, 0.0), (1, 0, 0), (0, 1, 0), 'S'), (x0 + .25, x1 - .25)
    return C.Face((0.0, y1, 0.0), (-1, 0, 0), (0, -1, 0), 'N'), (-(x1 - .25), -(x0 + .25))


def bays(u0, u1, width):
    n = max(1, round((u1 - u0) / width))
    w = (u1 - u0) / n
    return [(u0 + k * w, u0 + (k + 1) * w) for k in range(n)]


def storefront_holes(name, u0, u1, split, top, bay=6.0, upper=True, storeys=1):
    hs, ups = [], []
    for k, (a, c) in enumerate(bays(u0 + .3, u1 - .3, bay)):
        hs.append(hole(f'{name} door {k}', a + 1.0, .16, 1.1, 2.65, kind='door'))
        hs.append(hole(f'{name} shopfront {k}', (a + 1.75 + c - .35) / 2, .6, c - .35 - a - 1.75, 2.95, kind='shop'))
        if upper:
            for s in range(storeys):
                for j in (1, 2):
                    ups.append(hole(f'{name} upper {k}.{s}.{j}', a + (c - a) * j / 3, split + .75 + s * 3.0, 1.5, 1.65))
    return hs, ups


def window_holes(name, u0, u1, z_rows, spacing=3.2, w=1.4, h=1.6):
    hs = []
    for s, z in enumerate(z_rows):
        for k, (a, c) in enumerate(bays(u0 + .3, u1 - .3, spacing)):
            hs.append(hole(f'{name} window {s}.{k}', (a + c) / 2, z, w, h))
    return hs


def block(spec):
    """A flat-roofed block: corner piers, two-part carriers (ground and upper) on every side with cut and registered
    openings on the street sides, a coping ring over the parapet, roof and floors, interior partition and lights."""
    x0, x1, y0, y1, top, split = spec['x0'], spec['x1'], spec['y0'], spec['y1'], spec['top'], spec['split']
    nm = spec['name']
    rg, ru, band = spec['ground'], spec['upper'], spec['band']
    for side in 'WESN':
        f, (u0, u1) = face_for(side, x0, x1, y0, y1)
        f.label = f'{nm} {side}'
        gh, uh = spec['holes'].get(side, lambda u0, u1: ([], []))(u0, u1)
        f.wall(f'{nm} {side} ground carrier', u0, u1, 0.0, split + .005, depth=T, role=rg, holes=gh)
        f.wall(f'{nm} {side} upper carrier', u0, u1, split - .005, top - .02, depth=T, role=ru, holes=uh)
        if rg == 'wall':
            G.brick_courses(f, u0 + .02, u1 - .02, .2, split - .3, gh, spacing=.16)
        if ru == 'wall':
            G.brick_courses(f, u0 + .02, u1 - .02, split + .3, top - .4, uh, spacing=.16)
        m = Merge(f)
        for h in gh:
            if h.get('kind') == 'shop':
                framed(m, f, h, cols=max(1, round(h['w'] / 1.3)), rows=1, inset=.14, occupied='shop', kind='shopfront', frame='frame')
                m.box('frame', h['u'], .12, h['z'] + h['h'] - .7, h['w'] - .12, .09, .07)
                m.box('stone', h['u'], -.05, h['z'] - .045, h['w'] + .12, .14, .08)
            elif h.get('kind') == 'door':
                framed(m, f, h, cols=1, rows=1, inset=.16, occupied='shop', kind='door', frame='frame')
                m.box('frame', h['u'], .19, h['z'] + .45, h['w'] - .14, .05, .7)
                m.box('stone', h['u'], T / 2, h['z'] + .005, h['w'] - .02, T - .04, .03)
            else:
                framed(m, f, h, cols=2, rows=1, inset=.15, occupied='room', frame='white')
                m.box('stone', h['u'], -.05, h['z'] - .055, h['w'] + .2, .14, .1)
        for h in uh:
            framed(m, f, h, cols=1, rows=2, inset=.15, occupied='upper room', frame='white')
            m.box('stone', h['u'], -.05, h['z'] - .055, h['w'] + .22, .14, .1)
        m.box(band, (u0 + u1) / 2, -.035, split + .0, u1 - u0 - .02, .13, .45)           # sign band / belt over the carrier joint
        if spec.get('pilasters') and side in spec['holes']:
            for a, c in bays(u0 + .3, u1 - .3, spec.get('bay', 6.0))[1:]:
                m.box('wall', a, -.03, (split + .1 + top - .35) / 2, .55, .1, top - .35 - split - .1)
        if spec.get('balconies') and side == 'W':
            for h in uh:
                if int(h['id'].split('.')[-2]) % 2 == 0 and h['z'] > split:
                    iron_balcony(m, f, h['u'], h['z'], h['w'] + .6, depth=.9, role='hardware', slab='stone')
        m.flush(f'{nm} {side}')
    b = Batch()
    for cx in (x0 + .295, x1 - .295):                                                    # corner piers, 1 cm proud of both faces
        for cy in (y0 + .295, y1 - .295):
            b.box('wall' if rg == 'wall' or ru == 'wall' else rg, cx, cy, (top - .05) / 2, .61, .61, top - .05)
    ix0, ix1, iy0, iy1 = x0 + T - .05, x1 - T + .05, y0 + T - .05, y1 - T + .05
    b.box('membrane', (ix0 + ix1) / 2, (iy0 + iy1) / 2, top - 1.0, ix1 - ix0, iy1 - iy0, .2)        # roof
    if top - split > 2.0:
        b.box('floor', (ix0 + ix1) / 2, (iy0 + iy1) / 2, split - .1, ix1 - ix0, iy1 - iy0, .2)     # upper floor
    b.box('floor', (ix0 + ix1) / 2, (iy0 + iy1) / 2, .085, ix1 - ix0, iy1 - iy0, .15)              # ground floor (top .16)
    for s in range(1, spec.get('storeys', 1) - 1):
        b.box('floor', (ix0 + ix1) / 2, (iy0 + iy1) / 2, split - .1 + s * 3.0, ix1 - ix0, iy1 - iy0, .2)
    fx = spec.get('partition')
    if fx is not None:
        b.box('interior', fx, (iy0 + iy1) / 2, (.16 + split - .2) / 2, .15, iy1 - iy0, split - .36)
    rng = random.Random(int(abs(x0 * 7 + y0 * 13)))
    for i in range(spec.get('units', 3)):                                                # rooftop units
        ux = rng.uniform(x0 + 3.0, x1 - 3.0); uy = rng.uniform(y0 + 3.0, y1 - 3.0)
        b.box('pale', ux, uy, top - .9 + .38, 1.6, 1.2, .78)
        b.box('hardware', ux, uy, top - .9 + .79, 1.1, .8, .06)
    b.flush(f'{nm} body')
    o = .08; i_ = T + .06
    strip(f'{nm} parapet coping', [(x0 - o, y0 - o), (x1 + o, y0 - o), (x1 + o, y1 + o), (x0 - o, y1 + o)],
          [(x0 + i_, y0 + i_), (x1 - i_, y0 + i_), (x1 - i_, y1 - i_), (x0 + i_, y1 - i_)], top + .06, top + .06, spec.get('coping', 'stone'), 'roof')
    C.qa_room_light(f'{nm} ground', ((x0 + x1) / 2, (y0 + y1) / 2, split * .6), 90, 3.0)
    C.qa_room_light(f'{nm} upper', ((x0 + x1) / 2, (y0 + y1) / 2, split + 1.8), 60, 3.0)


def blocks():
    sp = 4.1
    ne = dict(name='North-east storefront row', x0=EAST_BL, x1=31.0, y0=CROSS_BL, y1=46.0, top=7.6, split=sp, ground='wall', upper='cream',
              band='sign', pilasters=True, bay=6.0, partition=EAST_BL + 7.5, units=4,
              holes=dict(W=lambda a, c: storefront_holes('NE W', a, c, sp, 7.6), S=lambda a, c: storefront_holes('NE S', a, c, sp, 7.6)))
    se = dict(name='South-east block', x0=EAST_BL, x1=30.0, y0=-46.0, y1=-CROSS_BL, top=7.2, split=sp, ground='stucco', upper='stucco',
              band='frame', pilasters=False, partition=EAST_BL + 7.5, units=3,
              holes=dict(W=lambda a, c: storefront_holes('SE W', a, c, sp, 7.2, bay=6.4), N=lambda a, c: storefront_holes('SE N', a, c, sp, 7.2, bay=6.4)))
    apt = dict(name='North-east apartment block', x0=EAST_BL, x1=33.0, y0=50.0, y1=79.5, top=13.4, split=3.6, ground='wall', upper='wall',
               band='cream', storeys=4, units=4, balconies=True, coping='cream',
               holes=dict(W=lambda a, c: storefront_holes('APT W', a, c, 3.6, 13.4, bay=6.5, storeys=3),
                          S=lambda a, c: ([], window_holes('APT S', a, c, (4.35, 7.35, 10.35)))))
    nw = dict(name='North-west office', x0=-36.0, x1=-WEST_BL, y0=15.5, y1=38.0, top=7.0, split=3.5, ground='wall', upper='wall',
              band='stone', units=3,
              holes=dict(E=lambda a, c: (window_holes('NW E g', a, c, (1.0,), spacing=3.0, w=1.6, h=1.8), window_holes('NW E u', a, c, (4.3,), spacing=3.0, w=1.6, h=1.6)),
                         S=lambda a, c: (window_holes('NW S g', a, c, (1.0,), spacing=3.0, w=1.6, h=1.8), window_holes('NW S u', a, c, (4.3,), spacing=3.0, w=1.6, h=1.6))))
    sw = dict(name='South-west block', x0=-34.0, x1=-WEST_BL, y0=-31.0, y1=-CROSS_BL - 1.2, top=4.9, split=3.9, ground='wall', upper='cream',
              band='cream', units=2, coping='pale',
              holes=dict(E=lambda a, c: (window_holes('SW E', a, c, (.9,), spacing=3.4, w=2.2, h=2.2), []),
                         N=lambda a, c: (window_holes('SW N', a, c, (.9,), spacing=3.4, w=2.2, h=2.2), [])))
    for s in (ne, se, apt, nw, sw):
        block(s)


def context():
    """Blocks further out along both streets: plain massing with windows and flat roofs."""
    b = Batch()
    for x0, x1, y0, y1, h, role in ((34.5, E_END - .5, CROSS_BL, 30.0, 6.8, 'neighbour'), (34.5, E_END - .5, 33.0, 79.5, 9.0, 'context'),
                                    (32.0, E_END - .5, -46.0, -CROSS_BL, 6.2, 'context'), (-46.0, -38.0, 14.0, 34.0, 6.0, 'neighbour'),
                                    (-46.0, -18.0, 44.0, 79.5, 7.4, 'context'), (-46.0, -36.0, -46.0, -CROSS_BL - 1.2, 5.4, 'neighbour'),
                                    (-34.0, -WEST_BL, -47.0, -34.0, 4.6, 'context')):
        b.box(role, (x0 + x1) / 2, (y0 + y1) / 2, (.003 + h) / 2, x1 - x0, y1 - y0, h - .003)
        b.box('membrane', (x0 + x1) / 2, (y0 + y1) / 2, h + .015, x1 - x0 - .5, y1 - y0 - .5, .04)
        for z in ([1.6, 4.8] if h > 6.4 else [1.6]):
            n = int((y1 - y0) / 3.5)
            for k in range(n):
                y = y0 + 1.75 + k * 3.5
                xf = x0 if x0 > 0 else x1
                b.box('glass', xf + (-.01 if x0 > 0 else .01), y, z + .8, .02, 1.6, 1.6)
            n = int((x1 - x0) / 3.5)
            for k in range(n):
                x = x0 + 1.75 + k * 3.5
                yf = y0 if y0 > 0 else y1
                b.box('glass', x, yf + (-.01 if y0 > 0 else .01), z + .8, 1.6, .02, 1.6)
    b.flush('context')


def build():
    ground()
    markings()
    separators()
    furniture()
    blocks()
    context()
    C.CONTACTS.append(dict(name='Complete-street section at the intersection: green protected bike lanes, separators, travel lanes, centre turn lane, refuge islands and crosswalks', box=[W_END, E_END, S_END, N_END]))


LIGHT_RIG = dict(key=(-40, -60, 55), fill=(50, -40, 35), rear=(-20, 55, 40), target=(0.0, 8.0, 2.0), gain=5.0)
