"""The Reef: an organic bouldering community centre, authored from the locked catalogue views of
climbing_wall_building / variant_3 (climbing_reef, "The Reef").

Read from the pixels (the top view governs the plan): one low, continuous, climbable fibreglass shell shaped like a
four-lobed coral reef or starfish in plan, about 30 m east-west by 27 m north-south, the lobes pointing north (the
narrowest, slightly east of the centre line), east, south and west (the longest) with soft concave bays between them
(top). The shell rises from a slightly tucked-in dark base in near-vertical bulging walls about 5 m high and rolls over
into a gently undulating roof plateau about 7 m above the ground (front, oblique: climbers give the scale); it is
banded in horizontal contour layers, deep teal at the base through teal and aquamarine to pale seafoam on the roof,
the band edges reading as contour lines on the roof (top). The walls are pocked with rounded rock-like pockets and
covered in small multicoloured climbing holds; the roof carries twelve circular glazed skylight domes on white rims,
one large dome at the centre and eleven small ones on the lobes (top, front, oblique). Dark arched cave-like
entrances open at the foot of the bays between the south lobe and its neighbours (front, oblique). A sand-coloured
rubber crash-pad apron follows the outline at 2-7 m width inside a low rounded sand-coloured curb, broken by four
diagonal gaps where white crushed-shell paths arrive (top, oblique). Around it, native meadow beds of grasses,
palmetto clumps and shrubs on dark mulch, small trees, and a concrete ring path about 46 m across with lawns, trees
and more meadow beyond (top, front, oblique). People are not modelled.
"""
import math
import random
import numpy as np
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-climbing-reef'
PX, CU, CV = 24.4, 603.0, 428.0                     # top-view pixels per metre and the plan origin (the central dome)
T = 1.0                                             # shell depth: fibreglass skin on its sculpted structure (pockets sink into it)
EPS = .002
H = 6.9                                             # roof plateau at the centre
ZW = 5.0                                            # wall shoulder: near-vertical below, rolling over above
DOME_Z = 7.3                                        # fitted visible dome centres (front and oblique camera fits)
RING_R0, RING_R1 = 22.0, 24.0                       # concrete ring path, inner and outer radius
SITE_R = 32.0
APRON_Z, CURB_Z, BED_Z = .06, .50, .085             # rubber apron top, curb top, mulch bed top
# Outline of the shell base (top view pixels, clockwise from the north lobe tip).
SHELL_PX = [(620, 121), (662, 138), (690, 172), (708, 220), (728, 262), (765, 295), (830, 322), (895, 345), (935, 370),
            (952, 410), (947, 455), (925, 495), (880, 530), (815, 552), (755, 575), (722, 610), (712, 660), (690, 720),
            (655, 765), (605, 779), (555, 768), (520, 735), (500, 690), (485, 645), (462, 605), (420, 580), (360, 560),
            (290, 532), (245, 500), (222, 450), (225, 400), (250, 355), (300, 328), (370, 312), (430, 300), (480, 288),
            (522, 255), (548, 205), (570, 160), (592, 128)]
# Outer line of the curb round the crash-pad apron (top view pixels).
APRON_PX = [(600, 73), (680, 78), (740, 100), (780, 150), (800, 215), (840, 258), (905, 276), (965, 302), (1010, 350),
            (1026, 420), (1016, 500), (990, 560), (940, 600), (850, 626), (805, 668), (790, 725), (760, 790), (700, 838),
            (620, 858), (540, 850), (470, 820), (425, 760), (405, 668), (350, 610), (260, 582), (192, 540), (155, 480),
            (148, 420), (160, 360), (200, 310), (262, 280), (320, 255), (370, 210), (420, 160), (470, 128), (530, 95)]
# Skylights: (u, v, radius in px of the glazed dome, rim excluded) from the top view.
DOMES_PX = [(603, 428, 40), (620, 212, 22), (613, 305, 19), (680, 312, 19), (550, 348, 19), (727, 397, 19),
            (830, 398, 23), (347, 413, 23), (450, 442, 19), (573, 560, 19), (653, 549, 19), (610, 632, 23)]
GAPS = (113.0, 41.5, -44.7, -137.0)                 # curb gaps (degrees about the origin) where the shell paths arrive
ENTRANCES = (-135.0, -50.0, 45.0, 132.0)            # arched entrances at the foot of the four bays (searched to the bay minima)
PALETTE = dict(reef0=(.008, .11, .14), reef1=(0.001, 0.130, 0.204), reef2=(0.004, 0.249, 0.364), reef3=(0.000, 0.536, 0.667), reef4=(0.000, 0.667, 0.775),
    reef5=(0.271, 0.875, 0.911), reef6=(0.371, 0.954, 0.975), reef7=(0.786, 1.000, 1.000), reef8=(0.706, 1.000, 1.000), reef_inner=(.52, .66, .63), rim=(.93, .93, .91), glass=(.30, .36, .40), dome=(.58, .64, .68), tint=(.025, .03, .035),
    frame=(.10, .13, .14), hardware=(.06, .06, .06), floor=(.20, .25, .30), mat=(.11, .17, .26), interior=(.70, .70, .66),
    apron=(.72, .55, .34), curb=(.78, .62, .42), liner=(.62, .76, .73), shellpath=(.95, .94, .91), shell2=(.80, .76, .70), shell3=(.97, .96, .94), concrete=(.50, .48, .44), lawn=(.20, .31, .10),
    mulch=(.22, .15, .09), hold_r=(.72, .10, .08), hold_y=(.90, .70, .10), hold_b=(.08, .22, .62), hold_p=(.42, .16, .55),
    reef1p=(0.012, 0.110, 0.133), reef2p=(0.012, 0.180, 0.209), reef3p=(0.000, 0.261, 0.302), reef4p=(0.023, 0.336, 0.348), reef5p=(0.116, 0.394, 0.360), reef6p=(0.209, 0.458, 0.394), reef7p=(0.278, 0.499, 0.429), reef8p=(0.348, 0.522, 0.458),
    hold_k=(.10, .10, .11), hold_n=(.52, .49, .44), hold_o=(.88, .40, .08), hold_g=(.20, .55, .18), bark=(.30, .23, .16), tree=(.20, .33, .12), tree2=(.27, .40, .15),
    tree3=(.34, .45, .18), wall=(.5, .5, .5), trim=(.84, .85, .82), stone=(.6, .6, .58), timber=(.42, .30, .18))


def manifest(version):
    h = 8.2
    cams = G.camera_roster(31.0, 28.0, h, [
        ('facade_close', (-2.5, -24.0, 3.2), (-.5, -13.0, 3.0), 38),            # the south lobe wall: bands, pockets, holds
        ('architecture_close', (21.0, -10.5, 10.5), (11.5, -1.5, 5.8), 34),     # the east lobe roll-over and contour bands
        ('glass_close', (5.5, -9.5, 10.4), (2.05, -4.96, 7.2), 40),             # one skylight: rim, dome, the cut through the shell
        ('interior', (-3.6, -3.2, 1.65), (3.0, 3.2, 3.6), 16),                 # inside the bouldering hall under the skylights
        ('entrance_sw', (-10.6, -10.8, 1.7), (-6.4, -6.6, 1.4), 30),            # the south-west bay entrance
        ('entrance_se', (10.0, -11.0, 1.7), (5.9, -6.8, 1.4), 30),              # the south-east bay entrance
        ('curb_gap', (17.6, -13.4, 1.7), (11.4, -11.4, .3), 32),                # from the south-east shell path: the curb gap and apron
        ('roof_skylights', (-3.0, -22.0, 22.0), (0.0, -1.0, 6.6), 34),          # the roof plateau and its domes
        ('climbing_pockets', (-23.5, 1.5, 2.5), (-14.6, -1.2, 2.7), 34),        # pockets and holds on the west lobe
        ('meadow_path', (-18.2, -14.4, 1.65), (-6.5, -6.5, 2.8), 30)])          # eye level on the south-west shell path, looking in
    for c in cams:                       # the locked front and oblique look from the south (fitted to the sources)
        if c['name'] == 'front':
            c.update(location=(-1.75, -45.2, 22.4), target=(-.18, 6.65, -2.62), lens=45.6, whole=False)
        elif c['name'] == 'front_corner':
            c.update(location=(-2.1, -43.0, 29.6), target=(-.68, -12.2, 8.9), lens=40.0, whole=False)
        elif c['name'] == 'top':
            c.update(location=(-.25, -.82, 120.0), target=(-.25, -.819, 0.0), ortho_scale=49.0, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(32.0, -38.0, 30.0), target=(0.0, -1.0, 2.5), lens=34, whole=False)
        elif c['name'] == 'left_side':
            c.update(location=(-48.0, 1.0, 8.5), target=(0.0, 0.0, 3.2), lens=36, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(48.0, 2.0, 8.5), target=(0.0, 0.0, 3.2), lens=36, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(1.5, 48.0, 8.5), target=(0.0, 0.0, 3.2), lens=36, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(34.0, 36.0, 26.0), target=(0.0, 0.5, 2.5), lens=34, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='climbing_wall_building/variant_3 (climbing_reef: organic four-lobed bouldering shell)',
        measurement_contract=dict(dimensions_m=dict(width=30.0, depth=27.0, height=h),
            observed_storeys=1, storey_programme='one tall bouldering hall under the shell (climbable outside and in)',
            plan='four-lobed starfish plan about 30 m east-west by 27 m north-south (top view, 24.4 px to the metre), lobes north, east, south and west with concave bays between',
            facade='one continuous fibreglass shell: tucked dark base, near-vertical bulging walls to about 5 m, rolling over to a 6.9 m plateau; six horizontal contour bands from deep teal to pale seafoam; rounded pockets and multicoloured holds on the walls',
            openings='twelve glazed skylight domes on white rims (one large central dome, eleven small); four arched glazed entrances at the foot of the bays (two visible in the front and oblique)',
            landscape='sand rubber crash-pad apron inside a low rounded curb with four diagonal gaps; white crushed-shell paths to a concrete ring path; native meadow beds on mulch, small trees, lawn beyond',
            levels_m=[0.0, APRON_Z, ZW, H], roof_m=dict(shoulder=ZW, plateau=H, dome_centres=DOME_Z, top=h),
            inferred='the interior hall, the north-east and north-west entrances and the shell thickness follow the visible grammar; metric dimensions are authored teaching assumptions'),
        roof_contract=dict(type='continuous undulating shell roof with contour bands and twelve skylight domes on rims', datum_m=H, crowns_m=[DOME_Z, h]),
        identity_contract=dict(owner='low organic four-lobed teal-to-seafoam bouldering shell with pockets, holds and skylight domes, ringed by a sand crash-pad apron and curb in a meadow park'),
        material_contract=dict(profile='source-palette clay: six teal-to-seafoam contour bands, white dome rims and glazing, multicoloured holds, sand rubber apron and curb, white shell paths, concrete ring path, mulch, meadow greens', textured_keeper=False),
        programme_contract=dict(storeys=1, ground='bouldering hall and community room under the shell', upper='climbable shell exterior'),
        contact_contract=['Shell base from grade inside the apron', 'Apron and curb at grade', 'Skylight rims seated through the shell', 'Paths and beds at grade'],
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
# ---- The Reef: one continuous climbable shell, its apron and the meadow park ----

def W(u, v):
    """Top-view pixel to metres (24.4 px to the metre, origin at the central dome, north up)."""
    return ((u - CU) / PX, (CV - v) / PX)


def polar_fit(pts_px, harmonics=8):
    """Smooth periodic radius r(theta) through a traced outline (least-squares Fourier series)."""
    th, rr = [], []
    for u, v in pts_px:
        x, y = W(u, v); th.append(math.atan2(y, x)); rr.append(math.hypot(x, y))
    th = np.array(th); rr = np.array(rr)
    cols = [np.ones_like(th)]
    for k in range(1, harmonics + 1):
        cols += [np.cos(k * th), np.sin(k * th)]
    coef, *_ = np.linalg.lstsq(np.stack(cols, 1), rr, rcond=None)
    return coef


def polar(coef, th):
    th = np.asarray(th, float); out = np.full(th.shape, coef[0])
    for k in range(1, (len(coef) - 1) // 2 + 1):
        out = out + coef[2 * k - 1] * np.cos(k * th) + coef[2 * k] * np.sin(k * th)
    return out


R_SHELL = polar_fit(SHELL_PX, 8)
R_APRON = polar_fit(APRON_PX, 8)
DOMES = [(W(u, v), r / PX) for u, v, r in DOMES_PX]
BUMPS = []
NT = 256                                            # shell segments round the outline
# Meridian profile of the shell: (fraction of the outline radius, height). Tucked base, bulging near-vertical wall to the
# shoulder, roll-over, gently domed plateau (front, oblique).
PROFILE = [(.975, 0.0), (.986, .35), (.995, .9), (1.0, 1.6), (.998, 2.6), (.99, 3.5), (.975, 4.3), (.955, 4.9),
           (.925, 5.45), (.88, 5.95), (.82, 6.3), (.74, 6.55), (.62, 6.72), (.48, 6.82), (.32, 6.88), (.16, 6.9), (0., 6.9)]
BANDS = (.7, 1.4, 2.3, 3.2, 4.6, 5.7, 6.5)        # contour band edges (profile heights): darkest base .. roof seafoam
ROLES = ('reef1', 'reef2', 'reef3', 'reef4', 'reef5', 'reef6', 'reef7', 'reef8')
TUCK = PROFILE[0][0]                                # base ring: fraction of the outline radius
INNER = len(ROLES)                                  # material slot of the inner skin


def _bumps():
    """Broad lumps and hollows on the plateau (the source roof reads rock-like, not smooth), clear of the skylights."""
    rnd = random.Random(23); out = []
    while len(out) < 26:
        x, y = rnd.uniform(-14, 14), rnd.uniform(-13, 12)
        th = math.atan2(y, x); s = math.hypot(x, y) / float(polar(R_SHELL, [th])[0])
        if s > .82:
            continue
        r = rnd.uniform(1.2, 2.6)
        if any(math.hypot(x - dx, y - dy) < dr + r * .9 + .4 for (dx, dy), dr in DOMES):
            continue
        out.append((x, y, r, rnd.choice((-1, 1)) * rnd.uniform(.10, .20)))
    return out


def roof_noise(x, y):
    """Undulation of the plateau: broad waves, small lumps and the scattered bumps (works on floats and arrays)."""
    b = sum(a * np.exp(-((x - bx) ** 2 + (y - by) ** 2) / (r * r)) for bx, by, r, a in BUMPS)
    return b + (.30 * np.sin(.55 * x + .3 * y) + .20 * np.sin(.8 * y - .4 * x + 1.3) + .10 * np.sin(1.7 * x + 1.1 * y)
            + .09 * np.sin(2.4 * x - .9 * y + .5) + .07 * np.sin(2.9 * y + 1.6 * x + 2.1))      # small lumps: a rock-like roof


def rings():
    """Resample the profile (Catmull-Rom) at about 0.22 m along the wall and 0.4 m across the roof (12 m mean radius)."""
    P = [PROFILE[0]] + PROFILE + [PROFILE[-1]]
    dense = []
    for k in range(len(PROFILE) - 1):
        p0, p1, p2, p3 = P[k], P[k + 1], P[k + 2], P[k + 3]
        for j in range(40):
            u = j / 40
            dense.append(tuple(.5 * (2 * p1[c] + (-p0[c] + p2[c]) * u + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * u * u
                                     + (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * u ** 3) for c in range(2)))
    dense.append(PROFILE[-1])
    out = [dense[0]]; acc = 0.0
    for a, b in zip(dense, dense[1:]):
        acc += math.hypot((b[0] - a[0]) * 12.0, b[1] - a[1])
        step = .15 if b[1] < 5.6 else .40
        if acc >= step:
            out.append(b); acc = 0.0
    if out[-1][0] > 1e-6:
        out.append((0.0, PROFILE[-1][1]))
    else:
        out[-1] = (0.0, PROFILE[-1][1])
    return out


def band(z):
    return sum(1 for e in BANDS if z >= e)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


class Shell:
    """The shell surface as a grid of rings (outer skin) with its inner skin T inside it."""
    def __init__(self):
        self.prof = rings()
        K = len(self.prof); th = np.linspace(0, 2 * math.pi, NT, endpoint=False)
        self.th = th; r = polar(R_SHELL, th)
        s = np.array([p[0] for p in self.prof]); z = np.array([p[1] for p in self.prof])
        S_, TH = np.meshgrid(s, th, indexing='ij'); Z = np.meshgrid(z, th, indexing='ij')[0]
        wall = 1 - smoothstep(.70, .93, S_)                         # 0 on the walls, 1 on the plateau
        wob = 1 + (1 - wall) * (.011 * np.sin(5 * TH + .7 * Z) + .007 * np.sin(11 * TH - .5 * Z + 1.0))
        RHO = S_ * r[None, :] * wob
        X = RHO * np.cos(TH); Y = RHO * np.sin(TH)
        # the wall rings wander up and down round the shell, so the ring-aligned contour bands read as wavy layers
        amp = .62 * np.sin(3 * TH + 1.0) + .40 * np.sin(5 * TH + 2.0) + .20 * np.sin(11 * TH + .4)
        Z = Z + amp * np.where(Z < 5.6, np.sin(math.pi * np.clip(Z, 0, 5.6) / 5.6), 0.0)
        Zn = pads(X, Y, Z + wall * roof_noise(X, Y))
        self.P = np.stack([X, Y, Zn], -1)                           # (K, NT, 3); the last ring collapses to the centre
        self.P[-1, :, :] = (0.0, 0.0, Zn[-1].mean())
        self.zprof = z; self.r = r
        self.normals()

    def normals(self):
        P = self.P
        dth = np.roll(P, -1, 1) - np.roll(P, 1, 1)
        dk = np.empty_like(P)
        dk[1:-1] = P[2:] - P[:-2]; dk[0] = P[1] - P[0]; dk[-1] = P[-1] - P[-2]
        n = np.cross(dth, dk)
        L = np.linalg.norm(n, axis=-1, keepdims=True); L[L < 1e-9] = 1
        n = n / L
        n[-1] = (0, 0, 1)                                           # the centre faces up
        self.N = n

    def inner(self):
        Pi = self.P - T * self.N
        Pi[0] = self.P[0].copy(); Pi[0, :, 2] = 0.0                  # the base ring of the inner skin sits on the floor line
        rho = np.hypot(self.P[0, :, 0], self.P[0, :, 1])
        f = (rho - T) / rho
        Pi[0, :, 0] *= f; Pi[0, :, 1] *= f
        Pi[-1] = (0.0, 0.0, self.P[-1, 0, 2] - T)
        return Pi

    def grid_index(self, theta, z):
        i = int(round((theta % (2 * math.pi)) / (2 * math.pi) * NT)) % NT
        k = int(np.argmin(np.abs(self.zprof[:-2] - z)))
        return k, i


def bay_minimum(deg):
    """The bay floor near a nominal angle: the outline radius minimum within +-25 degrees."""
    ts = np.radians(np.linspace(deg - 25, deg + 25, 201)); rr = polar(R_SHELL, ts)
    return float(ts[int(np.argmin(rr))])


ENTRY_TH = [bay_minimum(d) for d in ENTRANCES]
BUMPS = _bumps()
PADS = []                                           # (centre, radius, pad height) per skylight, filled by build()
EW, EH = 3.5, 2.6                                   # entrance clear width and height (a low, wide cave-like arch)


# Shoulder pockets: where the locked top shows them on the roll-over (top-view pixels); seen from above they read as
# the dimples round the plateau edge.
SHOULDER_PX = [(560, 172), (530, 265), (705, 255), (320, 322), (390, 322), (377, 365), (780, 320), (425, 507), (515, 610),
               (675, 690), (805, 535), (875, 515), (280, 510), (925, 370)]
PK_N = 40                                           # segments round each pocket mouth
PK_BEAD = .05                                       # the raised rim round each mouth (catches the light on the lower lip)
PK_UNDERCUT = .14                                   # the upper inner wall runs this fraction beyond the mouth, under the lip
PK_UPPER = .22                                      # the upper half of the cup is this much deeper than the lower floor
# Rings of each pocket patch, outside in: (ellipse radius factor, kind). 'skin' rings lie on the shell, 'bead' rises to
# the rim crest, 'mouth' is the crisp lip, 'cup' rings go down into the bowl.
PK_RINGS = ((1.20, 'skin'), (1.10, 'skin'), (1.045, 'bead'), (1.0, 'mouth'), (.95, 'cup'), (.86, 'cup'), (.72, 'cup'),
            (.53, 'cup'), (.30, 'cup'))
PK_SHADE_LOWER = 2.2                                # extra shade steps on the lower floor of the cup
PK_SHADE_ON = True


def cup_shade(rho, cphi):
    """Graded shade suffix of a cup face from its mean ring radius and the cosine of its angle from 'up' (the shade
    steps deepen toward the bottom of the cup and on its lower floor), '' outside the mouth."""
    if rho >= 1.0:
        return ''
    step = 1 + (.95 - min(rho, .95)) / .95 * 3.2 + PK_SHADE_LOWER * max(-cphi, 0.0)
    return 'abcde'[min(int(round(step)), 5) - 1]


def entrance_clearance(p):
    """Distance (m) in the entrance plane from a point to the nearest arched entrance outline (lining included)."""
    best = 1e9
    for th in ENTRY_TH:
        rho, e, t = entry_frame(th)
        d = p - e * rho
        if np.linalg.norm(d[:2]) > 10.0:
            continue
        u = float(d @ t); z = float(p[2]); r = EW / 2 + .22; zs = EH - EW / 2
        dist = max(abs(u) - r, 0.0) if z <= zs else max(math.hypot(u, z - zs) - r, 0.0)
        best = min(best, dist)
    return best


def pockets(shell):
    """Round to slightly oval cups over the whole shell, as the locked front and oblique show them: about 40 on the walls
    (one per sector of the outline: a third on the upper wall, a third mid wall and a third low down in the deep-teal
    base band) and 14 on the roll-over shoulder where the locked top shows them as dimples round the plateau. Mouths
    0.9-1.6 m across (aspect 0.9-1.3 on the walls), cups about 0.6 of the mouth radius deep. Every mouth (rim included)
    stays at least 1 m clear of the entrance arches. Returns (depth, horizontal half-width, kind, mouth centre,
    outer radius, axis, aspect, up) per pocket; shell_mesh() keeps the ones it can seat."""
    rnd = random.Random(31); out = []
    P, N = shell.P, shell.N

    def frame(k, i):
        nb = N[max(1, k - 2):k + 3][:, [(i + j) % NT for j in range(-3, 4)]].reshape(-1, 3).sum(0)
        ax = nb / np.linalg.norm(nb)
        up = np.array([0.0, 0.0, 1.0]) - ax * ax[2]
        if np.linalg.norm(up) < .25:                                 # nearly flat: 'up' runs toward the plateau centre
            up = -np.array([P[k, i, 0], P[k, i, 1], 0.0]); up = up - ax * (up @ ax)
        return ax, up / np.linalg.norm(up)

    def ok(p, Au, Av, up):
        R_ = 1.2 * max(Au, Av)
        if any(np.linalg.norm(p - q[3]) < R_ + q[4] + .35 for q in out):
            return False
        if entrance_clearance(p) < R_ + 1.0:
            return False
        if p[2] - 1.25 * Au * abs(up[2]) < .30:                     # the patch stays clear of the base ring
            return False
        return not any(math.hypot(p[0] - dx, p[1] - dy) < R + R_ + 1.2 for (dx, dy), R in DOMES)

    K = P.shape[0]
    for u, v in SHOULDER_PX:
        x, y = W(u, v); th = math.atan2(y, x); s = math.hypot(x, y) / float(polar(R_SHELL, [th])[0])
        k = min((k for k in range(K - 4) if shell.prof[k][1] > 4.7), key=lambda k: abs(shell.prof[k][0] - s))
        i = int(round((th % (2 * math.pi)) / (2 * math.pi) * NT)) % NT
        ax, up = frame(k, i); p = P[k, i].copy()
        Av = rnd.uniform(.55, .78); Au = Av * rnd.uniform(.8, 1.0)
        if ok(p, Au, Av, up):
            out.append((min(.66, .72 * (Au + Av) / 2), Av, 'shoulder', p, 1.2 * max(Au, Av), ax, Au / Av, up))
    secs = np.linspace(0, 2 * math.pi, 40, endpoint=False)
    for j, s0 in enumerate(secs):
        for _ in range(60):
            th = s0 + rnd.uniform(0, 2 * math.pi / 40)
            band_ = j % 3
            z = rnd.uniform(3.4, 4.5) if band_ == 0 else rnd.uniform(2.2, 3.4) if band_ == 1 else rnd.uniform(.9, 2.2)
            k, i = shell.grid_index(th, z)
            ax, up = frame(k, i); p = P[k, i].copy()
            Av = rnd.uniform(.45, .80); Au = Av * rnd.uniform(.9, 1.3)
            if ok(p, Au, Av, up):
                out.append((min(.76, .72 * (Au + Av) / 2), Av, 'pocket', p, 1.2 * max(Au, Av), ax, Au / Av, up))
                break
    return out


def pocket_patch(q, grid, bvh, V, kap, rho_of, mouth_of, cphi_of):
    """One pocket as a polar patch replacing the grid faces under it: a ring on the skin, a low rounded rim bead, the
    crisp mouth and a cup whose upper wall runs back under the lip (undercut) and is deeper than its lower floor.
    Returns the patch polygons (vertex indices into V; the outer ring is still to be zipped to the hole)."""
    from mathutils import Vector
    D, Av, kind, p, Rq, ax, asp, up = q
    Au = Av * asp; side = np.cross(ax, up)
    rows = []
    for rho, rk in PK_RINGS:
        row = []
        for m in range(PK_N):
            ph = 2 * math.pi * m / PK_N; c, s_ = math.cos(ph), math.sin(ph)
            if rk == 'cup':
                g = float(smoothstep(.30, .72, rho))
                sc = 1 + PK_UNDERCUT * max(c, 0.0) ** 2 * g
                h = -D * math.sqrt(max(1 - rho * rho, 0.0)) * (1 + PK_UPPER * c)
            else:
                sc = 1.0; h = PK_BEAD * (1.0 if rk == 'bead' else .55 if rk == 'mouth' else 0.0)
            u = Au * rho * sc * c; v = Av * rho * sc * s_
            o = p + up * u + side * v
            hit = bvh.ray_cast(Vector(o + ax * 1.5), Vector(-ax), 4.0)
            if hit[0] is None:
                hit = bvh.find_nearest(Vector(o))
            x = np.array(hit[0]); fi = hit[2]
            kk = fi // NT; ii = fi % NT
            a0 = .5 * (grid[kk, ii] + grid[kk, (ii + 1) % NT]); a1 = .5 * (grid[kk + 1, ii] + grid[kk + 1, (ii + 1) % NT])
            dk = a1 - a0; t = float(np.clip((x - a0) @ dk / (dk @ dk), 0, 1))
            V.append(tuple(float(c_) for c_ in x + ax * h)); idx = len(V) - 1
            kap[idx] = kk + t; rho_of[idx] = rho; mouth_of[idx] = rk == 'mouth'; cphi_of[idx] = c
            row.append(idx)
        rows.append(row)
    centre = p + ax * (-D)
    V.append(tuple(float(c_) for c_ in centre)); ci = len(V) - 1
    kap[ci] = kap[rows[-1][0]]; rho_of[ci] = 0.0; mouth_of[ci] = False; cphi_of[ci] = 0.0
    polys = []
    for r0, r1 in zip(rows, rows[1:]):
        for m in range(PK_N):
            polys.append((r0[m], r0[(m + 1) % PK_N], r1[(m + 1) % PK_N], r1[m]))
    for m in range(PK_N):
        polys.append((rows[-1][m], rows[-1][(m + 1) % PK_N], ci))
    return rows[0], polys


def zip_loops(ring, ring_ang, loop, loop_ang):
    """Triangles stitching two closed loops ordered by increasing angle (radians, any start)."""
    def norm(seq, ang):
        k0 = int(np.argmin([a % (2 * math.pi) for a in ang]))
        seq = seq[k0:] + seq[:k0]; ang = [a % (2 * math.pi) for a in ang[k0:] + ang[:k0]]
        out = [ang[0]]
        for a in ang[1:]:
            while a < out[-1] - math.pi:
                a += 2 * math.pi
            out.append(max(a, out[-1]))
        return seq, out
    A, a = norm(list(ring), list(ring_ang)); B, b = norm(list(loop), list(loop_ang))
    n, m = len(A), len(B); a = a + [a[0] + 2 * math.pi]; b = b + [b[0] + 2 * math.pi]
    tris = []; i = j = 0
    while i < n or j < m:
        if j >= m or (i < n and a[i + 1] <= b[j + 1]):
            tris.append((A[i % n], A[(i + 1) % n], B[j % m])); i += 1
        else:
            tris.append((A[i % n], B[(j + 1) % m], B[j % m])); j += 1
    return tris


def seat_pockets(shell, V, F, M, pk):
    """Replace the outer-skin grid faces under each pocket by its polar patch, zipped to the hole's edge, and split the
    patch along the contour band lines so every band keeps its own crisp, straight edge across the cup. Returns the
    kept pockets and the mouth edges (vertex pairs, marked sharp)."""
    from mathutils.bvhtree import BVHTree
    K = shell.P.shape[0]; grid = shell.P
    nq = (K - 2) * NT                                                  # outer-skin quads come first in F
    bvh = BVHTree.FromPolygons([tuple(x) for x in V[:(K - 1) * NT]], [F[f] for f in range(nq)])
    rowband = [band(.5 * (shell.zprof[k] + shell.zprof[k + 1])) for k in range(K - 2)]
    lines = [k for k in range(1, K - 2) if rowband[k] != rowband[k - 1]]
    kap, rho_of, mouth_of, cphi_of = {}, {}, {}, {}
    for idx in range((K - 1) * NT):
        kap[idx] = float(idx // NT); rho_of[idx] = 9.0; mouth_of[idx] = False; cphi_of[idx] = 0.0
    removed = set(); kept = []; new_polys = []
    for q in pk:
        D, Av, kind, p, Rq, ax, asp, up = q
        Au = Av * asp; side = np.cross(ax, up)
        ks, is_ = np.unravel_index(np.argmin(np.linalg.norm(grid[:K - 2] - p, axis=-1)), grid[:K - 2].shape[:2])
        cand = set()
        for k in range(max(0, ks - 16), min(K - 4, ks + 16)):
            for di in range(-10, 11):
                i = (is_ + di) % NT
                vs = [grid[k, i], grid[k, (i + 1) % NT], grid[k + 1, (i + 1) % NT], grid[k + 1, i]]
                e = min(math.hypot(float((x - p) @ up) / Au, float((x - p) @ side) / Av) for x in vs)
                if e < PK_RINGS[0][0] + .06 and all(abs(float((x - p) @ ax)) < 1.0 for x in vs):
                    cand.add(k * NT + i)
        if not cand or cand & removed or any(f // NT == 0 for f in cand):
            continue
        for _ in range(6):                                             # close pinches until the hole has one simple edge
            nxt = {}; bad = set()
            for f in cand:
                fv = F[f]
                for a_, b_ in zip(fv, fv[1:] + fv[:1]):
                    nxt.setdefault(a_, []).append(b_)
            twin = {(a_, b_) for a_, bs in nxt.items() for b_ in bs}
            bnd = {}
            for a_, bs in nxt.items():
                for b_ in bs:
                    if (b_, a_) not in twin:
                        bnd.setdefault(a_, []).append(b_)
            bad = [a_ for a_, bs in bnd.items() if len(bs) > 1]
            if not bad:
                break
            for a_ in bad:
                k0, i0 = divmod(a_, NT)
                for dk_, di_ in ((0, 0), (-1, 0), (0, -1), (-1, -1)):
                    f = (k0 + dk_) * NT + (i0 + di_) % NT
                    if 0 < k0 + dk_ < K - 4:
                        cand.add(f)
        if bad:
            continue
        start = next(iter(bnd)); loop = [start]
        while True:
            nx = bnd[loop[-1]][0]
            if nx == start:
                break
            loop.append(nx)
            if len(loop) > len(bnd):
                break
        if len(loop) != len(bnd) or cand & removed:
            continue
        outer, polys = pocket_patch(q, grid, bvh, V, kap, rho_of, mouth_of, cphi_of)
        ang = lambda x: math.atan2(float((np.array(x) - p) @ side) / Av, float((np.array(x) - p) @ up) / Au)
        la = [ang(V[i]) for i in loop]
        if sum(((b_ - a_ + math.pi) % (2 * math.pi) - math.pi) for a_, b_ in zip(la, la[1:] + la[:1])) < 0:
            loop = loop[::-1]; la = la[::-1]
        polys += zip_loops(outer, [2 * math.pi * m / PK_N for m in range(PK_N)], loop, la)
        removed |= cand; kept.append(q); new_polys += [(pl, q) for pl in polys]
    # split along the band lines (kappa = line), sharing the new vertices between neighbours
    cache = {}

    def cut(a_, b_, L):
        key = (min(a_, b_), max(a_, b_), L)
        if key not in cache:
            ka, kb = kap[a_], kap[b_]; t = (L - ka) / (kb - ka)
            x = np.array(V[a_]) * (1 - t) + np.array(V[b_]) * t
            V.append(tuple(float(c_) for c_ in x)); n_ = len(V) - 1
            kap[n_] = L; rho_of[n_] = rho_of[a_] * (1 - t) + rho_of[b_] * t; mouth_of[n_] = mouth_of[a_] and mouth_of[b_]
            cphi_of[n_] = cphi_of[a_] * (1 - t) + cphi_of[b_] * t
            cache[key] = n_
        return cache[key]
    eps = 1e-7; out_polys = []
    for pl, q in new_polys:
        pieces = [list(pl)]
        for L in lines:
            nxt_ = []
            for pc in pieces:
                ds = [kap[v_] - L for v_ in pc]
                if min(ds) >= -eps or max(ds) <= eps:
                    nxt_.append(pc); continue
                hi, lo = [], []
                for j_ in range(len(pc)):
                    a_, b_ = pc[j_], pc[(j_ + 1) % len(pc)]; da, db = ds[j_], ds[(j_ + 1) % len(pc)]
                    if da >= -eps:
                        hi.append(a_)
                    if da <= eps:
                        lo.append(a_)
                    if (da > eps and db < -eps) or (da < -eps and db > eps):
                        c_ = cut(a_, b_, L); hi.append(c_); lo.append(c_)
                nxt_ += [x for x in (hi, lo) if len(x) >= 3]
            pieces = nxt_
        out_polys += [(tuple(pc), q) for pc in pieces]
    ax_of = {}
    F[:] = [f for j_, f in enumerate(F) if j_ not in removed]
    M[:] = [mm for j_, mm in enumerate(M) if j_ not in removed]
    mouth_edges = set()
    for pc, q in out_polys:
        km = sum(kap[v_] for v_ in pc) / len(pc)
        role = rowband[min(max(int(km), 0), K - 3)]
        rm = sum(min(rho_of[v_], 9.0) for v_ in pc) / len(pc)
        sh = cup_shade(rm, sum(cphi_of[v_] for v_ in pc) / len(pc)) if PK_SHADE_ON else ''
        F.append(pc); M.append((role, sh))
        for a_, b_ in zip(pc, pc[1:] + pc[:1]):
            if mouth_of[a_] and mouth_of[b_]:
                mouth_edges.add(frozenset((a_, b_)))
    return kept, mouth_edges, len(removed)


def shell_mesh(shell, Pi, pk):
    """One closed solid: the outer skin (contour-band materials) with each pocket seated as its own polar patch, the inner
    skin at half resolution (every other ring and segment) and the base annulus stitching the two. Returns the shell
    and the pockets kept."""
    K = shell.P.shape[0]; NI = NT // 2
    V = [tuple(p) for p in shell.P[:-1].reshape(-1, 3)] + [tuple(shell.P[-1, 0])]
    co = len(V) - 1                                                     # outer centre
    off = len(V)
    ks = list(range(0, K - 1, 2))
    if ks[-1] != K - 2:
        ks.append(K - 2)
    for k in ks:
        V += [tuple(p) for p in Pi[k, ::2]]
    V.append(tuple(Pi[-1, 0])); ci = len(V) - 1
    F, M, flat = [], [], []
    o = lambda k, i: k * NT + (i % NT)
    q = lambda j, i: off + j * NI + (i % NI)
    for k in range(K - 2):
        role = band(.5 * (shell.zprof[k] + shell.zprof[k + 1]))
        for i in range(NT):
            F.append((o(k, i), o(k, i + 1), o(k + 1, i + 1), o(k + 1, i))); M.append((role, ''))
    role = band(shell.zprof[K - 2])
    for i in range(NT):
        F.append((o(K - 2, i), o(K - 2, i + 1), co)); M.append((role, ''))
    for j in range(len(ks) - 1):
        for i in range(NI):
            F.append((q(j, i + 1), q(j, i), q(j + 1, i), q(j + 1, i + 1))); M.append((INNER, ''))
    for i in range(NI):
        F.append((q(len(ks) - 1, i + 1), q(len(ks) - 1, i), ci)); M.append((INNER, ''))
        for tri in ((o(0, 2 * i), o(0, 2 * i + 1), q(0, i)), (o(0, 2 * i + 1), o(0, 2 * i + 2), q(0, i + 1)),
                    (o(0, 2 * i + 1), q(0, i + 1), q(0, i))):
            flat.append(tri); F.append(tri); M.append((0, ''))
    kept, mouth_edges, nrem = seat_pockets(shell, V, F, M, pk)
    obj = C.mesh('Reef shell', V, F, 'reef1', 'shell')
    names = [ROLES[0]]
    for role in ROLES[1:] + ('reef_inner',):
        obj.data.materials.append(C.MATS[role]); names.append(role)
    for role in ROLES:
        for s_, f_ in SHADES:
            obj.data.materials.append(C.MATS[role + s_]); names.append(role + s_)
    fl = set(flat)
    for p, (m, sh) in zip(obj.data.polygons, M):
        nm = names[m] + sh
        p.material_index = names.index(nm); p.use_smooth = tuple(F[p.index]) not in fl   # the buried base annulus is flat
    for e in obj.data.edges:
        if frozenset(e.vertices) in mouth_edges:
            e.use_edge_sharp = True                                    # the crisp lip of each cup
    bm = C.bmesh.new(); bm.from_mesh(obj.data)
    C.bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.to_mesh(obj.data); bm.free(); obj.data.update()
    obj['rlasm_wall_carrier'] = True
    obj['pockets_seated'] = len(kept)
    return obj, kept


SHADES = (('a', .84), ('b', .76), ('c', .69), ('d', .62), ('e', .54))   # graded shades of each band inside a pocket cup
for _r in [r for r in PALETTE if r.startswith('reef') and r[4:].isdigit()]:
    for _s, _f in SHADES:
        PALETTE[_r + _s] = tuple(round(v * _f, 4) for v in PALETTE[_r])


def soft_pairs(obj):
    """Material index pairs within one band (the band and its graded cup shades) whose shared edges stay smooth."""
    names = [m.name for m in obj.data.materials]
    base = [nm[:-1] if nm[-1] in 'ABCDE' and nm[:-1] in names else nm for nm in names]
    return {frozenset((i, j)) for i in range(len(names)) for j in range(len(names)) if i != j and base[i] == base[j]}


def entry_frame(th):
    """Local frame at an entrance: the bay floor point O on the outer bulge line, tangent t, outward e."""
    e = np.array([math.cos(th), math.sin(th), 0.0]); t = np.array([-math.sin(th), math.cos(th), 0.0])
    rho = float(polar(R_SHELL, [th])[0])
    return rho, e, t


def arch_poly(w, h, grow=0.0, z0=0.0, n=16):
    """Arched opening outline (closed): right jamb foot, up and over the semicircular head, down to the left jamb foot."""
    r = w / 2 + grow; zs = h - w / 2
    return [(r, z0)] + [(r * math.cos(math.pi * j / n), zs + r * math.sin(math.pi * j / n)) for j in range(n + 1)] + [(-r, z0)]


def prism_local(name, O, e, t, poly, d0, d1, role, module):
    """Extrude a (u, z) polygon in the plane of tangent t from depth d0 to d1 along -e (inwards) from O."""
    V = []
    for d in (d0, d1):
        for u, z in poly:
            p = O - e * d + t * u
            V.append((float(p[0]), float(p[1]), float(z)))
    n = len(poly)
    F = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    return C.mesh(name, V, F, role, module)


def roof_z(x, y):
    """Plateau height of the (undented) outer skin at a plan point (skylights sit inside s < 0.8)."""
    th = math.atan2(y, x); s = math.hypot(x, y) / float(polar(R_SHELL, [th])[0])
    prof = [p for p in rings() if p[1] >= 4.9]
    ss = [p[0] for p in prof][::-1]; zz = [p[1] for p in prof][::-1]
    z = float(np.interp(s, ss, zz))
    wall = 1 - float(smoothstep(.70, .93, s))
    return float(pads(x, y, z + wall * float(roof_noise(x, y))))


def plateau_profile(x, y):
    """Noise-free profile height of the plateau at a plan point."""
    th = math.atan2(y, x); s = math.hypot(x, y) / float(polar(R_SHELL, [th])[0])
    prof = [p for p in rings() if p[1] >= 4.9]
    return float(np.interp(s, [p[0] for p in prof][::-1], [p[1] for p in prof][::-1]))


def pads(x, y, z):
    """Each skylight sits on a level circular pad: the roof relief blends to the pad height within 0.5-1.7 m of its rim
    (floats or arrays)."""
    for (dx, dy), R, zc in PADS:
        d = np.hypot(x - dx, y - dy)
        w = 1 - smoothstep(R + .5, R + 1.7, d)
        z = z * (1 - w) + zc * w
    return z


def cut_openings(obj):
    """One exact boolean: the twelve skylight holes and the four arched entrances (reveals deep teal, hidden by the
    collars and the tunnel linings)."""
    cutters = []
    from mathutils import Vector
    for (x, y), R in DOMES:
        c = C.rod('Skylight cutter', (x, y, 4.6), (x, y, 9.5), R, 'reef1', 'construction cutter', 48)
        cutters.append(c)
    for th in ENTRY_TH:
        rho, e, t = entry_frame(th)
        O = e * rho * 1.03
        cutters.append(prism_local('Entrance cutter', O, e, t, arch_poly(EW, EH, z0=-.12, n=48), -.55, 1.75, 'reef1', 'construction cutter'))
    for c in cutters:
        for p in c.data.polygons:
            p.use_smooth = False
    C.bpy.ops.object.select_all(action='DESELECT')
    for c in cutters:
        c.select_set(True)
    C.bpy.context.view_layer.objects.active = cutters[0]
    C.bpy.ops.object.join()
    cutter = C.bpy.context.object
    C.bpy.context.view_layer.objects.active = obj
    mod = obj.modifiers.new('openings', 'BOOLEAN'); mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'; mod.object = cutter
    mod.material_mode = 'TRANSFER'
    C.bpy.ops.object.modifier_apply(modifier=mod.name)
    C.remove_cutter(cutter)
    C.normalise(obj.data)
    crisp(obj, by_material=True, angle=89.0, soft=soft_pairs(obj))   # reveals and band edges crisp; pocket dishes smooth


def crisp(obj, by_material=False, angle=35.0, soft=()):
    """Sharp edges at creases (dihedral above `angle`), between flat and smooth faces and, by_material, between
    materials, so smooth shading never bends across a cut rim, a pocket lip or an arch reveal; the contour band edges
    read as crisp contour lines."""
    bm = C.bmesh.new(); bm.from_mesh(obj.data)
    lim = math.radians(angle)
    for ed in bm.edges:
        fl = ed.link_faces
        if len(fl) != 2:
            continue
        pair = frozenset((fl[0].material_index, fl[1].material_index))
        if pair in soft and fl[0].smooth and fl[1].smooth:
            continue
        if (fl[0].smooth != fl[1].smooth or ed.calc_face_angle(0.0) > lim
                or (by_material and fl[0].material_index != fl[1].material_index)):
            ed.smooth = False
    bm.to_mesh(obj.data); bm.free(); obj.data.update()


def tint_glazing():
    """The entrance glazing is dark tinted glass (the sources show the entrances as dark cave mouths)."""
    bs = C.MATS['tint'].node_tree.nodes.get('Principled BSDF')
    bs.inputs['Roughness'].default_value = .12


def dome_glazing():
    """The skylight domes are thick acrylic: mostly reflective with some transmission (the sources show silver bubbles)."""
    bs = C.MATS['dome'].node_tree.nodes.get('Principled BSDF')
    bs.inputs['Roughness'].default_value = .16; bs.inputs['Transmission Weight'].default_value = .35; bs.inputs['IOR'].default_value = 1.49


def skylights():
    """Each skylight: a rigid white collar standing level on its pad (12 cm proud, 22 cm wide), seated down through the
    shell to 5 cm above the inner skin (the cut's own wall shows below it inside), and a low glazed lens dome on it,
    open underneath so the hall sees the glazing."""
    n, prof = 36, [(1, 0), (.93, .30), (.78, .58), (.55, .82), (.28, .96), (.0, 1)]
    for j, (((x, y), R, zc)) in enumerate(PADS):
        top = zc + .12; bot = zc - T + .05
        rim = annulus(f'Skylight collar {j}', (x, y, 0.0), (0, 0, 1), R - .04, R + .22, bot, top, 'rim', 'skylights', n)
        liner = annulus(f'Skylight reveal liner {j}', (x, y, 0.0), (0, 0, 1), R - .07, R - .035, zc - T - .03, top - .02,
                        'liner', 'skylights', 32)                    # the full-depth reveal, seen from the hall
        for p in liner.data.polygons:
            p.use_smooth = abs(p.normal.z) < .5
        crisp(liner)
        for p in rim.data.polygons:
            p.use_smooth = abs(p.normal.z) < .5
        crisp(rim)
        a = [2 * math.pi * i / n for i in range(n)]; rise = .30 * R + .05; V = []
        for rf, hf in prof:
            for q in a:
                rr = max((R + .06) * rf, .002)
                V.append((x + rr * math.cos(q), y + rr * math.sin(q), top - .02 + rise * hf))
        F = []
        for jr in range(len(prof) - 1):
            for i in range(n):
                k = (i + 1) % n
                F.append((jr * n + i, jr * n + k, (jr + 1) * n + k, (jr + 1) * n + i))
        d = C.mesh(f'Skylight dome {j}', V, F, 'dome', 'skylights')
        for p in d.data.polygons:
            p.use_smooth = True


def arch_line(w, h, grow=0.0, z0=0.0, n=48):
    """Open arch line: right jamb foot, up and over the semicircular head, down to the left jamb foot."""
    r = w / 2 + grow; zs = h - w / 2
    return [(r, z0)] + [(r * math.cos(math.pi * j / n), zs + r * math.sin(math.pi * j / n)) for j in range(n + 1)] + [(-r, z0)]


def entrances(obj):
    """Each bay entrance is a cave mouth: an arched tunnel lined in the shell's deep teal runs from the outer skin (its lip
    3 cm inside the skin all round the cut) about 2 m through and into the hall as a short vault; dark glazing with a pair
    of thin dark doors closes its inner end; a sand threshold runs the tunnel floor."""
    bvh = C.BVHTree.FromObject(obj, C.bpy.context.evaluated_depsgraph_get()) if hasattr(C, 'BVHTree') else None
    if bvh is None:
        from mathutils.bvhtree import BVHTree
        bvh = BVHTree.FromObject(obj, C.bpy.context.evaluated_depsgraph_get())
    from mathutils import Vector
    for j, th in enumerate(ENTRY_TH):
        rho, e, t = entry_frame(th)
        O = e * rho * 1.03
        outer = arch_line(EW, EH, grow=.04); inner = arch_line(EW, EH, grow=-.18)
        depth = []
        for u, z in outer:
            start = O + t * u + np.array([0, 0, max(z, .05)]) + e * 1.5
            hit = bvh.ray_cast(Vector(start), Vector(-e), 4.0)
            depth.append(hit[3] - 1.5 if hit[0] is not None else None)
        known = [d for d in depth if d is not None]
        depth = [d if d is not None else min(known) for d in depth]
        dback = max(depth) + T + .18; dglass = dback - .12       # the tunnel ends just past the inner skin
        n = len(outer); V = []
        for line in (outer, inner):
            for (u, z), d in zip(line, depth):
                p = O - e * (d + .40) + t * u; V.append((float(p[0]), float(p[1]), float(z)))   # lining set back: the mouth is the skin's own edge
        for line in (outer, inner):
            for (u, z) in line:
                p = O - e * dback + t * u; V.append((float(p[0]), float(p[1]), float(z)))
        OF, IF, OB, IB = 0, n, 2 * n, 3 * n
        F = []
        for i in range(n - 1):
            k = i + 1
            F += [(IF + i, IF + k, IB + k, IB + i), (OF + k, OF + i, OB + i, OB + k),
                  (OF + i, OF + k, IF + k, IF + i), (OB + k, OB + i, IB + i, IB + k)]
        F += [(OF, IF, IB, OB), (OF + n - 1, OB + n - 1, IB + n - 1, IF + n - 1)]
        lin = C.mesh(f'Entrance {j} tunnel lining', V, F, 'reef2', 'entrances')
        for p in lin.data.polygons:
            p.use_smooth = True
        crisp(lin)
        prism_local(f'Entrance {j} glazing', O, e, t, arch_poly(EW, EH, grow=-.16, z0=.10), dglass - .006, dglass + .006, 'tint', 'entrances')
        f = C.Face(tuple(O), tuple(t), tuple(-e), f'Entrance {j}')
        mg = Merge(f)
        mg.box('frame', 0.0, dglass - .02, .10 + .95, .05, .04, 1.9)                   # door meeting stile
        mg.box('frame', 0.0, dglass - .02, 2.02, 1.74, .04, .05)                       # door head
        for s in (-1, 1):
            mg.box('frame', s * .85, dglass - .02, .10 + .95, .05, .04, 1.9)            # door jambs
            mg.box('hardware', s * .1, dglass - .045, 1.15, .025, .03, .6)              # pull handles
        d0 = min(depth) + .30
        mg.box('apron', 0.0, (d0 + dback) / 2, .031, 2 * (EW / 2 - .18) + .1, dback - d0, .062)     # tunnel floor, 2 mm above the apron
        mg.flush(f'entrance {j}')


def holds(shell, Pi, dent_list):
    """Multicoloured climbing holds: small rounded six-sided nubs seated 4 cm into the skin, scattered uniformly by
    area over the walls (outside) and the lower inner skin (inside), clear of the pocket hollows and entrances."""
    rnd = random.Random(11); roles = ('hold_r', 'hold_y', 'hold_b', 'hold_p', 'hold_o', 'hold_g', 'hold_k', 'hold_n', 'hold_k', 'hold_n')
    G_ = {r: ([], []) for r in roles}

    holes = [(q[3], q[4] * 1.05 + .08) for q in dent_list]            # holds stay off the pocket cups and rims

    placed = {}

    def add(p, n, sz, role):
        n = n / (np.linalg.norm(n) or 1); a = np.cross(n, [0, 0, 1.0])
        if np.linalg.norm(a) < 1e-6:
            a = np.array([1.0, 0, 0])
        a /= np.linalg.norm(a); b = np.cross(n, a)
        ang = rnd.uniform(0, math.pi); ca, sa = math.cos(ang), math.sin(ang)
        a, b = a * ca + b * sa, b * ca - a * sa
        key = (round(p[0] / .3), round(p[1] / .3), round(p[2] / .3))
        for q, r_ in placed.get(key, ()):
            if np.linalg.norm(q - p) < 1.2 * (r_ + sz):
                return False
        for dx_ in (-1, 0, 1):
            for dy_ in (-1, 0, 1):
                for dz_ in (-1, 0, 1):
                    placed.setdefault((key[0] + dx_, key[1] + dy_, key[2] + dz_), []).append((np.array(p), sz))
        V, F = G_[role]; o = len(V); h = rnd.uniform(.04, .07); sx = sz * rnd.uniform(.7, 1.2)
        for d, f in ((-.04, 1.0), (h, .55)):
            for m in range(6):
                ang6 = m * math.pi / 3
                q = p + n * d + (a * math.cos(ang6) * sx + b * math.sin(ang6) * sz) * f
                V.append(tuple(float(c) for c in q))
        F += [tuple(o + m for m in range(5, -1, -1)), tuple(o + 6 + m for m in range(6))]
        F += [(o + m, o + (m + 1) % 6, o + 6 + (m + 1) % 6, o + 6 + m) for m in range(6)]

    P, N = shell.P, shell.N
    K = P.shape[0]; n_out = 0
    step = np.linalg.norm(P[2:-1] - P[:-3], axis=-1).mean(1) / 2           # ring spacing (rings 1 .. K-3)
    rad = np.hypot(P[1:-2, :, 0], P[1:-2, :, 1]).mean(1)
    ks = list(range(1, K - 2)); wk = list(step * rad)                       # area weight of each ring band
    routes = []; tries = 0                                              # loose vertical routes from the base up the walls
    while len(routes) < 34 and tries < 5000:
        tries += 1; th = rnd.uniform(0, 2 * math.pi)
        if any(abs((th - e + math.pi) % (2 * math.pi) - math.pi) < .30 for e in ENTRY_TH):
            continue
        if any(abs((th - r_ + math.pi) % (2 * math.pi) - math.pi) < .07 for r_ in routes):
            continue
        routes.append(th)
    for th in routes:
        top = rnd.uniform(4.2, 5.5)
        z = .35
        while z < top:
            z += .34 * rnd.uniform(.6, 1.4)
            k, i = shell.grid_index(th + rnd.uniform(-.3, .3) / max(5.0, shell.r.mean()), z)
            if any(np.linalg.norm(P[k, i] - c) < r for c, r in holes):
                continue
            add(P[k, i], N[k, i], rnd.uniform(.04, .09), roles[rnd.randrange(len(roles))]); n_out += 1
    while n_out < 380:
        k = rnd.choices(ks, wk)[0]; i = rnd.randrange(NT)
        z = P[k, i, 2]
        if not (.3 < z < 5.3):
            continue
        th = shell.th[i]
        if any(abs((th - e + math.pi) % (2 * math.pi) - math.pi) < .24 and z < 3.2 for e in ENTRY_TH):
            continue
        if any(np.linalg.norm(P[k, i] - c) < r for c, r in holes):
            continue
        add(P[k, i], N[k, i], rnd.uniform(.04, .09), roles[rnd.randrange(len(roles))]); n_out += 1
    n_in = 0
    while n_in < 120:
        k = rnd.choices(ks, wk)[0]; i = rnd.randrange(NT)
        z = Pi[k, i, 2]
        if not (.4 < z < 4.4):
            continue
        th = shell.th[i]
        if any(abs((th - e + math.pi) % (2 * math.pi) - math.pi) < .28 for e in ENTRY_TH):
            continue
        add(Pi[k, i], -N[k, i], rnd.uniform(.04, .08), roles[rnd.randrange(len(roles))]); n_in += 1
    for role, (V, F) in G_.items():
        if F:
            o = C.mesh(f'Climbing holds {role}', V, F, role, 'holds')
            for p in o.data.polygons:
                p.use_smooth = True                                            # rounded lumps, not cubes


def interior(shell):
    """The bouldering hall: matting floor lapped 6 cm into the shell base, three free-standing boulders, lights."""
    th = shell.th[::2]
    rho0 = np.hypot(shell.P[0, ::2, 0], shell.P[0, ::2, 1]) - T + .08
    pts = [(float(r * math.cos(a)), float(r * math.sin(a))) for r, a in zip(rho0, th)]
    C.prism('Hall floor', pts, 'z', 0.0, .10, 'mat', 'inside')
    for j, (x, y, R, h) in enumerate(((5.0, .3, 1.5, 2.8), (-5.4, .6, 1.5, 2.6), (.3, 5.0, 1.3, 2.3))):   # off the entrance axes
        o = dome(f'Bouldering block {j}', x, y, .05, R, h, [(1, 0), (1.04, .25), (.95, .55), (.78, .8), (.45, .96), (0, 1)],
                 ('reef3', 'reef4', 'reef2')[j], 'inside', 24, 8)
        for p in o.data.polygons:
            p.use_smooth = len(p.vertices) < 6
    # inspection lights well inside the hall: each disc stays inside 0.6 of the outline radius, where the inner skin is
    # above 6 m (a light near a bay wall would poke through the skin and light it from outside)
    spots = [(0.0, 0.0)]
    for a in range(0, 360, 45):
        ta = math.radians(a); ra = float(polar(R_SHELL, [ta])[0])
        for f in (.30, .55):
            rr = f * ra
            if rr + 1.0 < .6 * ra:
                spots.append((rr * math.cos(ta), rr * math.sin(ta)))
    for x, y in spots:
        lt = C.qa_room_light(f'Hall {x:+.1f} {y:+.1f}', (x, y, 4.6), 40, 2.0)
        lt.visible_camera = False; lt.visible_glossy = False                 # the emitters light the hall but never show
    C.CONTACTS.append(dict(name='Hall floor lapped into the shell base; boulders on the floor', floor_m=.10))


def ring_polar(coef_or_r, th):
    r = polar(coef_or_r, th) if not np.isscalar(coef_or_r) else np.full(len(th), coef_or_r)
    return [(float(a * math.cos(t)), float(a * math.sin(t))) for a, t in zip(r, th)]


def band_mesh(name, outer, inner, z0, z1, role, module):
    n = len(outer)
    vs = [(x, y, z0) for x, y in outer] + [(x, y, z0) for x, y in inner] + [(x, y, z1) for x, y in outer] + [(x, y, z1) for x, y in inner]
    O0, I0, O1, I1 = 0, n, 2 * n, 3 * n
    fs = []
    for i in range(n):
        j = (i + 1) % n
        fs += [(O1 + i, O1 + j, I1 + j, I1 + i), (O0 + j, O0 + i, I0 + i, I0 + j), (O0 + i, O0 + j, O1 + j, O1 + i), (I0 + j, I0 + i, I1 + i, I1 + j)]
    return C.mesh(name, vs, fs, role, module)


def gap_windows():
    out = []
    for g in GAPS:
        ga = math.radians(g); ra = float(polar(R_APRON, [ga])[0])
        out.append((ga, 1.35 / ra))
    return out


def in_gap(th):
    return any(abs((th - g + math.pi) % (2 * math.pi) - math.pi) < hw for g, hw in gap_windows())


def apron_and_curb(shell):
    """The sand rubber crash-pad apron from under the shell wall to inside the curb, and the rounded curb segments."""
    th = np.linspace(0, 2 * math.pi, 240, endpoint=False)
    ra = polar(R_APRON, th); rs = polar(R_SHELL, th) * TUCK
    outer = [(float((r - .05) * math.cos(a)), float((r - .05) * math.sin(a))) for r, a in zip(ra, th)]
    inner = [(float((r - .25) * math.cos(a)), float((r - .25) * math.sin(a))) for r, a in zip(rs, th)]
    band_mesh('Crash-pad apron', outer, inner, 0.0, APRON_Z, 'apron', 'apron')
    # curb: a rounded section lofted along the outline between the four gaps
    wins = sorted(((g - hw) % (2 * math.pi), (g + hw) % (2 * math.pi)) for g, hw in gap_windows())
    for j in range(len(wins)):
        a0 = wins[j][1]; a1 = wins[(j + 1) % len(wins)][0]
        if a1 < a0:
            a1 += 2 * math.pi
        n = max(8, int((a1 - a0) * 16.0 / .45))
        secs = []
        for i in range(n + 1):
            a = a0 + (a1 - a0) * i / n; r = float(polar(R_APRON, [a])[0])
            c, s = math.cos(a), math.sin(a)
            prof = [(r, 0.0), (r, CURB_Z - .08), (r - .045, CURB_Z - .018), (r - .12, CURB_Z), (r - .26, CURB_Z),
                    (r - .335, CURB_Z - .018), (r - .38, CURB_Z - .08), (r - .38, 0.0)]
            secs.append([(rr * c, rr * s, z) for rr, z in prof])
        o = loft(f'Curb segment {j}', secs, 'curb', 'apron', closed=False)
        for p in o.data.polygons:
            p.use_smooth = len(p.vertices) == 4 and abs(p.normal.z) < .999
        crisp(o)
    C.CONTACTS.append(dict(name='Apron at grade from under the shell wall to the curb; curb on grade', apron_m=APRON_Z, curb_m=CURB_Z))


PATH_DIRS = {113.0: 100.0, 41.5: 31.0, -44.7: -13.5, -137.0: -154.0}


def shell_paths():
    """White crushed-shell paths from each curb gap out to the ring path: soft irregular edges, flaring where they meet
    the gap, and two tones of shell specks scattered on them (the granular crushed shell of the top view)."""
    polys = []; rnd = random.Random(31); specks = {'shell2': ([], []), 'shell3': ([], [])}
    for g, d in PATH_DIRS.items():
        ga = math.radians(g); ra = float(polar(R_APRON, [ga])[0])
        p0 = np.array([math.cos(ga), math.sin(ga)]) * (ra - .25)
        dd = math.radians(d); L = RING_R0 + .9 - ra
        v = np.array([math.cos(ga) + math.cos(dd), math.sin(ga) + math.sin(dd)]); v /= np.linalg.norm(v)
        mid = p0 + v * L * .45
        end = mid + np.array([math.cos(dd), math.sin(dd)]) * L
        line = _pksh.LineString([tuple(p0), tuple(mid), tuple(end)])
        line = line.intersection(_pksh.Point(0, 0).buffer(RING_R0 + .9, quad_segs=32))
        if line.geom_type != 'LineString':
            line = max(line.geoms, key=lambda q: q.length)
        Ln = line.length; m = int(Ln / .35) + 1; left, right = [], []
        for k in range(m + 1):
            s = Ln * k / m; p = line.interpolate(s); q = line.interpolate(min(Ln, s + .05)); q0 = line.interpolate(max(0, s - .05))
            tx, ty = q.x - q0.x, q.y - q0.y; tl = math.hypot(tx, ty) or 1; nx, ny = -ty / tl, tx / tl
            flare = 1.3 * max(0.0, 1 - s / 2.6) ** 2
            wl = 1.4 + flare / 2 + .10 * math.sin(1.3 * s + g) + .03 * math.sin(3.1 * s + 1.7 * g)
            wr = 1.4 + flare / 2 + .10 * math.sin(1.1 * s - g + .5) + .03 * math.sin(2.9 * s - g)
            left.append((p.x + nx * wl, p.y + ny * wl)); right.append((p.x - nx * wr, p.y - ny * wr))
        pts = left + right[::-1]
        poly = _PkPolygon(pts).buffer(.3, quad_segs=8).buffer(-.3, quad_segs=8).simplify(.01)   # soft organic edges
        polys.append(poly)
        C.prism(f'Shell path {g:+.0f}', [tuple(c) for c in list(poly.exterior.coords)[:-1]], 'z', 0.0, .045, 'shellpath', 'paths')
        for x, y in pk_scatter(poly.buffer(-.05), .2, seed=int(g * 10) % 997 + 3)[:300]:
            role = 'shell2' if rnd.random() < .55 else 'shell3'; V, F = specks[role]; o = len(V)
            a0 = rnd.uniform(0, math.tau)                                   # a small irregular flat flake 2 mm above the path
            V += [(x + rnd.uniform(.012, .028) * math.cos(a0 + k * 1.571 + rnd.uniform(-.4, .4)),
                   y + rnd.uniform(.012, .028) * math.sin(a0 + k * 1.571 + rnd.uniform(-.4, .4)), .047) for k in range(4)]
            F.append((o, o + 1, o + 2, o + 3))
    for role, (V, F) in specks.items():
        if F:
            C.mesh(f'Crushed shell {role}', V, F, role, 'paths')
    return polys


def site(paths):
    """Lawn disc under everything, the concrete ring path, and the mulch meadow beds inside and beyond it."""
    th = np.linspace(0, 2 * math.pi, 160, endpoint=False)
    C.prism('Park lawn', [(150.0 * math.cos(a), 150.0 * math.sin(a)) for a in th], 'z', 0.0, .03, 'lawn', 'site')   # past every frame edge
    band_mesh('Ring path', [(RING_R1 * math.cos(a), RING_R1 * math.sin(a)) for a in th],
              [(RING_R0 * math.cos(a), RING_R0 * math.sin(a)) for a in th], 0.0, .095, 'concrete', 'paths')   # 1 cm above the beds that lap under it
    th2 = np.linspace(0, 2 * math.pi, 240, endpoint=False)
    apron = _PkPolygon([(float((r - .12) * math.cos(a)), float((r - .12) * math.sin(a))) for r, a in zip(polar(R_APRON, th2), th2)])
    inner = _pksh.Point(0, 0).buffer(RING_R0 + .05, quad_segs=48).difference(apron)
    cut = _pksh.union_all([p.buffer(-.05) for p in paths])
    beds = []
    for g in getattr(inner.difference(cut), 'geoms', [inner.difference(cut)]):
        if g.area > 4:
            beds.append(g)
    outer_ring = _pksh.Point(0, 0).buffer(SITE_R - .5, quad_segs=48).difference(_pksh.Point(0, 0).buffer(RING_R1 - .05, quad_segs=48))
    for a0, a1 in ((95, 140), (150, 215), (-25, 22), (-82, -40)):
        sector = _PkPolygon([(0, 0)] + [(40 * math.cos(math.radians(a)), 40 * math.sin(math.radians(a))) for a in np.linspace(a0, a1, 24)])
        g = outer_ring.intersection(sector)
        if not g.is_empty:
            beds.append(g.buffer(-1.2).buffer(1.2, quad_segs=8).simplify(.02))     # rounded bed ends
    for j, g in enumerate(beds):
        g = g.simplify(.012)
        pts = list(g.exterior.coords)[:-1]
        C.prism(f'Meadow bed {j}', pts, 'z', 0.0, BED_Z, 'mulch', 'beds')
    return beds


# The meadow planting uses the shared planting kit (plantkit.py, cat before this body) as linked instances.
pk_palette(PALETTE)
KIT = None
INSTANCING = True
# Trees stand on the diagonals, clear of the four elevation views' sight lines and of the shell paths (the sources show
# small trees in the meadow beds and larger ones beyond the ring path).
TREES = [(14.6, 14.6, 1.6), (-14.6, 14.6, 1.7), (24.5, 14.0, 3.0), (-20.0, 20.0, 3.2), (-20.0, -20.0, 3.0), (13.5, -25.0, 2.8),
         (25.0, -14.5, 2.6), (-25.0, -14.0, 2.6), (17.0, 24.0, 3.0), (-24.5, 15.0, 3.2), (-15.0, -25.5, 2.8),
         (27.0, -19.0, 2.6)]


def protos(kit):
    P = {}
    P['palmetto'] = arching_grass(kit, 'reef_palmetto', blades=22, height=.82, width=.065, role='pk_leaf_dark', crown_role='pk_leaf_dark', seed=11)
    P['fountain'] = arching_grass(kit, 'reef_fountain', blades=56, height=.6, width=.018, role='pk_blade', crown_role='pk_blade', seed=21)
    P['straw'] = arching_grass(kit, 'reef_gold_grass', blades=52, height=.55, width=.02, role='pk_leaf_light', crown_role='pk_leaf_light',
                               seed=31)
    P['shrub'] = shrub_mass(kit, 'reef_shrub', radius=.55, height=.8, lobes=6, seed=41)
    P['tall'] = arching_grass(kit, 'reef_tall_gold', blades=60, height=.9, width=.02, role='pk_straw', crown_role='pk_straw', seed=51)
    return P


def planting(beds):
    global KIT
    kit = KIT = PlantKit('planting', instancing=INSTANCING); P = protos(kit)
    for x, y, r in TREES + SMALL:
        kit.add_obstacle(_pksh.Point(x, y).buffer(.25, quad_segs=6), 3.0)
    mix = [(P['palmetto'], 1.2), (P['tall'], 1.2), (P['fountain'], .9), (P['straw'], .8), (P['shrub'], .5)]
    rnd = random.Random(5); fields = [_PkNoise(91 + 17 * i, 2 * math.pi / 3.2) for i in range(len(mix))]
    for j, g in enumerate(beds):
        reg = kit.register_bed(pk_region(g))
        spacing = .68 if g.centroid.distance(_pksh.Point(0, 0)) < RING_R0 else 1.3
        for x, y in pk_scatter(reg, spacing, margin=PK_CLEAR, seed=40 + j):
            order = sorted(range(len(mix)), key=lambda i: -(fields[i](x, y) + 1.4 * math.log(mix[i][1])))
            for i in order[:2]:
                p = mix[i][0]; done = False
                for s in ((1.2, 1.0, .85) if p is P['palmetto'] else (1.9, 1.6, 1.3, 1.05) if p is P['shrub'] else (1.6, 1.35, 1.1, .9)):   # palmetto fronds droop to the soil
                    sz = s * rnd.uniform(.85, 1.08)
                    if kit.fits(p, x, y, s, reg, sz=sz):
                        kit.place(p, x, y, BED_Z, rnd.uniform(0, math.tau), s, sz=sz); done = True
                        break
                if done:
                    break
    kit.flush()
    bad = kit.audit(detail=True)
    if bad:
        raise RuntimeError(f'planting kit clearance rule: {len(bad)} placements cross a bed edge or obstacle: {bad[:12]}')


SMALL = []                                          # small multi-stem trees in the inner beds, placed by build()
SMALL_AT = [(-14.0, 10.6), (-18.6, 8.9), (-19.4, -6.2), (19.6, -8.0), (-13.2, -14.8), (11.4, -14.4)]


def small_trees(beds):
    """The sources show small trees through every meadow bed inside the ring (top: NW, W, SW, S/SE, E, N): each is
    nudged outward until it stands 0.8 m inside a bed."""
    inner = [g for g in beds if g.centroid.distance(_pksh.Point(0, 0)) < RING_R0]
    for x, y in SMALL_AT:
        r0 = math.hypot(x, y); ux, uy = x / r0, y / r0
        for k in range(10):
            q = (x + ux * .5 * k, y + uy * .5 * k)
            if any(g.buffer(-.8).contains(_pksh.Point(q)) for g in inner):
                SMALL.append((q[0], q[1], 1.0)); break


def small_tree(x, y, k=0):
    """Small multi-stem meadow tree (about 5 m): three slender stems fanning from one root and a loose crown."""
    z = BED_Z
    roles = ('tree', 'tree2', 'tree3')
    for j in range(3):
        a = k * 1.1 + j * math.tau / 3
        tip = (x + math.cos(a) * .7, y + math.sin(a) * .7, z + 3.2 + .3 * j)
        C.rod('Small tree stem', (x, y, z), tip, .07, 'bark', 'trees', 6)
        o = A.foliage('Small tree crown', (tip[0] + math.cos(a) * .2, tip[1] + math.sin(a) * .2, tip[2] + .6), (1.05, 1.05, .85),
                      role=roles[(k + j) % 3], detail=2)
        for p in o.data.polygons:
            p.use_smooth = True


def park_tree(x, y, r, k=0):
    """Small rounded park tree: a trunk, two limbs and a crown of overlapping smooth masses."""
    z = BED_Z if math.hypot(x, y) < RING_R0 else .03
    Ht = 2.3 * r + 2.6
    lean = ((.2, .1), (-.15, .2), (.1, -.2))[k % 3]
    top = (x + lean[0], y + lean[1], z + Ht * .55)
    C.rod('Tree trunk', (x, y, z), top, .12 + .03 * r, 'bark', 'trees', 8)   # on the soil; its tilted foot stays above grade
    for a in (k * 1.3, k * 1.3 + 2.4):
        C.rod('Tree limb', (x, y, z + Ht * .35), (x + math.cos(a) * r * .5, y + math.sin(a) * r * .5, z + Ht * .62), .06 + .015 * r, 'bark', 'trees', 6)
    roles = ('tree', 'tree2', 'tree3')
    for j in range(4):
        a = k * .9 + j * math.tau / 3
        c = (top[0], top[1], z + Ht * .72) if j == 0 else (top[0] + math.cos(a) * r * .5, top[1] + math.sin(a) * r * .5, z + Ht * (.58 + .04 * j))
        sc = (r * .85, r * .85, r * .72) if j == 0 else (r * .6, r * .6, r * .5)
        o = A.foliage('Tree crown', c, sc, role=roles[(k + j) % 3], detail=2)
        for p in o.data.polygons:
            p.use_smooth = True


def build():
    PADS[:] = [((x, y), R, plateau_profile(x, y)) for (x, y), R in DOMES]
    shell = Shell()
    Pi = shell.inner()                    # the inner skin follows the outer skin T inside it (pockets never reach it)
    obj, dent_list = shell_mesh(shell, Pi, pockets(shell))
    cut_openings(obj)
    dome_glazing()
    skylights()
    tint_glazing()
    entrances(obj)
    holds(shell, Pi, dent_list)
    interior(shell)
    apron_and_curb(shell)
    paths = shell_paths()
    beds = site(paths)
    small_trees(beds)
    planting(beds)
    for k, (x, y, r) in enumerate(SMALL):
        small_tree(x, y, k)
    for k, (x, y, r) in enumerate(TREES):
        park_tree(x, y, r, k)
    for j, th in enumerate(ENTRY_TH):
        rho, e, t = entry_frame(th)
        C.OPENINGS.append(dict(id=f'entrance_{j}', face=f'Entrance {j}', u=0.0, z=.15, width=EW - .4, height=EH - .9,
            kind='arched glazed entrance', clear_wall_cut=True, carrier_depth_m=.55 + rho * .03 + T, frame_inset_m=rho * .03 + .30,
            pane_inset_m=rho * .03 + .30, face_origin=list(e * rho * 1.03 + e * .0), face_tangent=list(t), face_inward=list(-e),
            occupied_space='bouldering hall'))
    C.CONTACTS.append(dict(name='The Reef bouldering shell on its apron in the meadow park', box=[-15.6, 14.4, -14.4, 12.6]))


LIGHT_RIG = dict(key=(-40, -50, 48), fill=(50, -25, 30), rear=(10, 55, 42), target=(0, 0, 3.0), gain=3.3)
