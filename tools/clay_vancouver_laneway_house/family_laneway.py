"""Vancouver laneway house, authored from the locked catalogue views of
vancouver_laneway_house / variant_0.

Read from the pixels (the top view governs the plan): a compact two-storey house on a street corner, the street
south and a side street west, under one low hipped roof of dark standing-seam metal with a short ridge running
front to back, thin dark fascias and a skylight on the west slope. Every wall is clad in vertical cedar boards of
varied tone on an exposed concrete plinth. The south-west corner is a two-storey glazed bay in heavy black frames
(two lights on each face per storey, a black spandrel at the upper floor) projecting about a metre to the front
line; east of it, between the bay and a full-height cedar end fin, the upper storey is a recessed four-light sliding
wall behind a balcony with a grey steel channel fascia and a frameless glass railing, and under the balcony the
cedar-lined porch holds the wood front door with a sidelight and a two-light window, reached by concrete steps and
a walk from the front sidewalk. A deep cedar band runs across the whole front under the roof edge. On the side
street a tall narrow window pair, a wall lamp, a cedar-lined recessed side entry under a panel of horizontal
boards with its own steps, a small window over it and small rear windows. A one-storey cedar garage with a hipped
metal roof stands against the rear wall, its board door facing the side street. Planted front and side beds of
sword ferns, ornamental grasses, blue fescue and a red Japanese maple; sidewalks and a rounded curb on both
streets, two cars parked on the side street, a utility pole with wires, a two-and-a-half-storey stucco neighbour
with a hipped shingle roof and porch to the east behind a board fence, and large trees behind.
"""
import math
import random
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-vancouver-laneway-house'
X0, X1 = -3.7, 3.7                               # 7.4 m wide (west wall on the side street, east wall to the neighbour)
YF = -4.3                                        # front line: glazed bay front, cedar end fin and the front band
YS = -3.3                                        # main south wall behind the porch and balcony (1.0 m recess)
Y1 = 3.8                                         # rear wall (8.1 m from the front line: top-view proportion)
XB = X0 + 2.9                                    # east face of the glazed bay's cedar end wall (bay 2.9 m wide)
T = .25                                          # wall carrier depth
EPS = .002
FL1 = .48                                        # ground floor over the exposed concrete plinth
FL2 = 3.32                                       # upper floor (inside the black spandrel band)
HG = 5.55                                        # head of the upper glazing; underside of the front cedar band
EAVE = 6.35                                      # roof top over the wall lines
RISE = 1.75                                      # ridge above EAVE
OV = .38                                         # side eave overhang
HI = 2.9                                         # hip inset of the front and rear hips (a 2.3 m ridge, top view)
SL = RISE / ((X1 - X0) / 2)                      # side slope
SE = RISE / HI                                   # end (hip) slope, steeper
OVE = OV * SL / SE                               # end overhang that keeps one level eave
ZE = EAVE - OV * SL                              # top of the roof plate at the eave edge
ZR = EAVE + RISE                                 # ridge
WT = EAVE - .08                                  # wall carriers end inside the roof plate
XE0, XE1, YE0, YE1 = X0 - OV, X1 + OV, YF - OVE, Y1 + OVE      # eave rectangle
GX0, GX1, GY1 = -2.6, 2.4, Y1 + 2.6              # rear garage (against the rear wall; its north eave about 2.6 m beyond the main eave, top view)
GH, GEAVE, GRISE, GOV = 2.95, 3.05, 1.1, .3
XC, YC, R = -6.15, -9.3, 1.6                     # side and front curb faces, corner curb radius
XSW, YSW = -4.4, -7.3                            # inner edges of the side and front sidewalks
NX0, NX1, NY0, NY1 = 5.2, 13.2, -3.2, 8.6        # stucco neighbour to the east
XF = 4.25                                        # board fence on the east lot line
PALETTE = dict(wall=(.60, .39, .23), cedar=(.60, .39, .23), cedar_light=(.71, .50, .31), cedar_deep=(.47, .29, .17), cedar_joint=(.27, .17, .10),
    frame=(.08, .08, .09), glass=(.30, .36, .40), metal=(.22, .24, .27), metal_rib=(.31, .33, .36), fascia=(.13, .14, .16),
    skylight=(.78, .84, .88), steel=(.47, .51, .54), hardware=(.10, .10, .11), lamp=(.95, .90, .74), door_wood=(.70, .45, .25),
    concrete=(.70, .69, .66), foundation=(.58, .58, .56), paving=(.77, .76, .73), joint=(.56, .55, .52), curb=(.68, .67, .64),
    asphalt=(.31, .31, .32), yellow=(.86, .70, .22), lawn=(.37, .52, .25), gravel=(.55, .53, .50), interior=(.88, .85, .79),
    floor=(.63, .50, .36), furniture=(.82, .80, .74), dark_cloth=(.26, .27, .29), stucco=(.80, .77, .71), shingle=(.34, .34, .35),
    white=(.93, .93, .91), glass_dark=(.15, .18, .21), fence=(.44, .33, .23), tree=(.40, .54, .20), tree2=(.50, .62, .25),
    conifer=(.15, .29, .15), bark=(.30, .23, .16), car_blue=(.13, .24, .45), car_dark=(.14, .14, .16), car_glass=(.07, .09, .11),
    tyre=(.06, .06, .06), tail=(.62, .08, .08), pole=(.42, .35, .27), wire=(.07, .07, .07), maple_core=(.24, .07, .07),
    maple_red2=(.56, .17, .15))


def manifest(version):
    h = ZR + .2
    cams = G.camera_roster(X1 - X0 + 3.0, Y1 - YF + 3.0, h, [
        ('facade_close', (.8, -12.0, 3.1), (.8, YF, 3.2), 35),
        ('glass_close', (-7.4, -9.6, 2.6), (X0 + 1.1, YF + .4, 2.9), 40),
        ('architecture_close', (2.6, -8.6, 4.4), (1.4, YF, 3.7), 40),
        ('entry_steps', (.9, -9.0, 1.6), (-.1, YS, 1.25), 35),
        ('side_entry', (-8.2, -.6, 1.7), (X0, YS + 3.0, 1.6), 35),
        ('west_wall', (-13.5, .2, 4.0), (X0, .2, 3.0), 32),
        ('roof_seams', (-7.8, -6.6, 11.0), (-1.4, .4, 6.9), 40),
        ('garage', (-7.6, Y1 - 1.6, 2.1), (GX0, Y1 + 1.3, 1.6), 35),
        ('interior', (.6, -1.6, FL1 + 1.45), (-3.0, -4.0, FL1 + 1.2), 32),
        ('garden', (2.6, -10.4, 1.4), (2.2, -5.6, .45), 35)])
    for c in cams:
        if c['name'] == 'front':                    # the locked front: eye level from the corner, about 26 deg west of the front normal
            c.update(location=(-11.2, -15.0, 1.65), target=(-.9, -1.0, 3.5), lens=42, whole=False)
        elif c['name'] == 'front_corner':           # the locked oblique: high from the south-west, about 38 deg west of the front normal
            c.update(location=(-11.1, -12.0, 13.2), target=(-.2, -.6, 2.6), lens=36, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(13.0, -15.0, 17.0), target=(0.0, 0.0, 3.0), lens=33, whole=False)
        elif c['name'] == 'left_side':
            c.update(location=(-22.0, 1.5, 8.0), target=(X0, 1.5, 3.2), lens=35, whole=False)
        elif c['name'] == 'right_side':             # the east side yard is 1.5 m wide: a high south-east oblique over the fence and the neighbour's eave
            c.update(location=(9.6, -10.6, 13.6), target=(2.4, .9, 3.0), lens=30, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(.5, GY1 + 14.0, 7.5), target=(0.0, Y1 + 1.0, 3.4), lens=32, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(-15.0, GY1 + 7.0, 11.0), target=(-.5, 2.5, 3.2), lens=33, whole=False)
        elif c['name'] == 'top':                    # plan view framed like the locked top: side street left, front sidewalk at the bottom
            c.update(location=(-.6, .2, 40.0), target=(-.6, .201, 0.0), ortho_scale=20.6, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='vancouver_laneway_house/variant_0 (vancouver_laneway_house_v0)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - YF, height=h),
            observed_storeys=2, storey_programme='living and dining on the ground floor behind the glazed corner, bedrooms and a sitting room above off the front balcony',
            plan='7.4 x 8.1 m under one hipped roof (0.38 m side and 0.30 m end overhangs); a 2.9 x 1.0 m two-storey glazed bay at the south-west corner and a 1.0 m deep porch and balcony recess east of it, closed by a full-height cedar end fin; a 5.0 x 2.6 m one-storey garage and store against the rear wall, its hipped roof ridge running east-west along the rear wall',
            facade='vertical cedar boards of varied tone with fine dark joints on a concrete plinth; heavy black window frames; a deep cedar band under the front roof edge; a horizontal-board panel over the side entry; wood front and side doors',
            levels_m=[FL1, FL2, HG], roof_m=dict(eave=EAVE, ridge=ZR),
            inferred='interiors, the east and rear walls and the garage interior are teaching assumptions; the garage, which the front view shows as a low hip-roofed building with a board door behind the house, is placed on the plan of the lower roof in the top view'),
        roof_contract=dict(type='low hipped standing-seam metal roof, short ridge front to back, steeper end hips, thin dark fascia, cedar soffit, skylight on the west slope', datum_m=EAVE, crowns_m=[ZR]),
        identity_contract=dict(owner='compact two-storey cedar-clad Vancouver laneway house: low dark standing-seam hip roof, black-framed two-storey glazed corner, recessed balcony with a glass railing over a cedar-lined porch'),
        material_contract=dict(profile='source-palette clay: cedar boards in three tones with dark joints, black frames, dark standing-seam metal, grey steel balcony fascia, grey concrete plinth and steps, warm wood doors', textured_keeper=False),
        programme_contract=dict(storeys=2, ground='entry, living and dining behind the glazed corner, side entry hall', upper='bedrooms and a sitting room off the balcony'),
        contact_contract=['Grade-zero lawn, beds, walks and sidewalks', 'Cedar walls and glazed bay on a concrete plinth', 'Porch landing and steps on grade', 'Roof on the wall plates; garage roof dies into the rear wall'],
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


# ---- Vancouver laneway house ----

pk_palette(PALETTE)
KIT = None
INSTANCING = True
PSOIL = .09                                      # bed soil top; kit plants sink PK_SINK below it
NU, NW = YS + 3.2, 1.5                           # recessed side entry on the side street: centre (y) and width
ND = .45                                         # its depth: shallow, so the door shows from the south-west (front, oblique)
NDU = NU + .17                                   # the door sits toward the north return, as in the front source
GXM, GHALF = (GX0 + GX1) / 2, (GX1 - GX0) / 2
GYS = Y1 - .12                                   # the garage roof's upper edge (its ridge) dies inside the rear wall carrier
GXE0, GXE1, GYE1 = GX0 - GOV, GX1 + GOV, GY1 + GOV
GTOP, GIN = 1.1, 1.6                             # roof rise; plan inset of the ridge ends from the side eaves (top view)
GSE = GTOP / GIN                                 # end (hip) slope, steeper
GSN = GTOP / (GYE1 - GYS)                        # north slope, down from the ridge along the rear wall to the north eave
GZE = GH - .068                                  # eave plate edge: the wall tops (GH) stay inside the 0.18 m plate on every side
GZR = GZE + GTOP
GXR0, GXR1 = GXE0 + GIN, GXE1 - GIN              # ridge ends on the rear wall line (ridge east-west, parallel to it)


def zr(x, y):
    """Top of the main roof plate at plan point (x, y): four planes, one level eave, short ridge."""
    return min(ZR, ZE + min(SL * (x - XE0), SL * (XE1 - x), SE * (y - YE0), SE * (YE1 - y)))


def gzr(x, y):
    """Top of the garage roof plate: a north slope and two steeper hipped ends rising to an east-west ridge buried in the
    rear wall."""
    return min(GZR, GZE + min(GSE * (x - GXE0), GSE * (GXE1 - x), GSN * (GYE1 - y)))


def smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def segs(a0, a1, cuts, least=.04):
    """Intervals of [a0, a1] outside the cut ranges."""
    out = [(a0, a1)]
    for a, b in cuts:
        nxt = []
        for s, e in out:
            if b <= s or a >= e:
                nxt.append((s, e))
            else:
                if a > s:
                    nxt.append((s, a))
                if b < e:
                    nxt.append((b, e))
        out = nxt
    return [(s, e) for s, e in out if e - s > least]


def cladding(m, u0, u1, z0, z1, holes, seed, hzone=None, board=.14):
    """Vertical cedar boards on a carrier face: fine dark joints 1-7 mm proud and a scatter of lighter and deeper board
    overlays 0.5-3.5 mm proud (the joints lap their edges), all stopped 2 cm clear of every opening. hzone=(ua, ub, zh)
    turns the boards horizontal above zh between ua and ub (the panel over the side entry)."""
    rnd = random.Random(seed)

    def cuts(u, half):
        cs = [(h['z'] - .02, h['z'] + h['h'] + .02) for h in holes if abs(u - h['u']) < h['w'] / 2 + half + .02]
        if hzone and hzone[0] - half < u < hzone[1] + half:
            cs.append((hzone[2], z1 + 1.0))
        return cs
    n = int((u1 - u0) / board)
    for k in range(n + 1):
        u = u0 + k * board
        if k:
            for s, e in segs(z0, z1, cuts(u, .006)):
                m.box('cedar_joint', u, -.004, (s + e) / 2, .012, .006, e - s)
        if k < n:
            r = rnd.random()
            role = 'cedar_light' if r < .24 else 'cedar_deep' if r < .42 else None
            if role:
                uc = u + board / 2
                for s, e in segs(z0, z1, cuts(uc, board / 2)):
                    m.box(role, uc, -.002, (s + e) / 2, board - .004, .003, e - s)
    if hzone:
        ua, ub, zh = hzone
        k = 0
        z = zh
        while z < z1 - .05:
            zt = min(z + board, z1)
            ucuts = [(h['u'] - h['w'] / 2 - .02, h['u'] + h['w'] / 2 + .02) for h in holes
                     if h['z'] - .02 < zt and z < h['z'] + h['h'] + .02]
            r = rnd.random()
            role = 'cedar_light' if r < .35 else 'cedar_deep' if r < .55 else None
            for s, e in segs(ua, ub, ucuts):
                if role:
                    m.box(role, (s + e) / 2, -.002, (z + zt) / 2, e - s, .003, zt - z - .004)
                if k:
                    m.box('cedar_joint', (s + e) / 2, -.004, z, e - s, .006, .012)
            z = zt
            k += 1


def window(m, f, h, cols=1, rows=1, occupied='room', inset=.07):
    """Black aluminium window in a cut hole with a dark metal sill flashing."""
    framed(m, f, h, cols=cols, rows=rows, inset=inset, occupied=occupied, frame='frame')
    m.box('fascia', h['u'], -.012, h['z'] - .01, h['w'] + .05, .086, .04)


def slab_fan(name, c, pts, z0, z1, role, module='site'):
    """Closed slab over a fan from point c through an ordered run of boundary points (convex from c)."""
    n = len(pts)
    vs = [(c[0], c[1], z0), (c[0], c[1], z1)] + [(x, y, z0) for x, y in pts] + [(x, y, z1) for x, y in pts]
    fs = []
    for i in range(n - 1):
        fs.append((0, 3 + i, 2 + i))
        fs.append((1, 2 + n + i, 3 + n + i))
        fs.append((2 + i, 3 + i, 3 + n + i, 2 + n + i))
    fs.append((0, 2, 2 + n, 1))
    fs.append((0, 1, 1 + 2 * n, 1 + n))
    return C.mesh(name, vs, fs, role, module)


def arc(cx, cy, r, a0, a1, n=14):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def site():
    """Corner lot: side street west and front street south with a rounded curb, sidewalks, lawn base, walks, yards."""
    b = Batch()
    cx, cy = XC + R, YC + R
    b.box('asphalt', (-15.7 + XC) / 2, (cy + 24.0) / 2, .01, XC + 15.7, 24.0 - cy, .02)
    b.box('asphalt', (-15.7 + XC) / 2, (YC + cy) / 2, .01, XC + 15.7, cy - YC, .02)
    b.box('asphalt', (-15.7 + 22.0) / 2, (-19.0 + YC) / 2, .01, 37.7, YC + 19.0, .02)
    slab_fan('Corner asphalt', (XC, YC), arc(cx, cy, R, math.pi, 1.5 * math.pi), 0.0, .02, 'asphalt')
    # Curb: one swept section along the street edge (side street, corner radius, front street).
    line = [(XC, 24.0), (XC, cy)] + arc(cx, cy, R, math.pi, 1.5 * math.pi)[1:] + [(22.0, YC)]
    rings = []
    for i, (x, y) in enumerate(line):
        if i == 0 or y > cy + 1e-6:
            nx, ny = 1.0, 0.0
        elif x > cx - 1e-6 and abs(y - YC) < 1e-6:
            nx, ny = 0.0, 1.0
        else:
            d = math.hypot(cx - x, cy - y); nx, ny = (cx - x) / d, (cy - y) / d
        rings.append([(x, y, 0.0), (x, y, .125), (x + nx * .16, y + ny * .16, .125), (x + nx * .16, y + ny * .16, 0.0)])
    loft('Curb', rings, 'curb', 'site', closed=False)
    # Sidewalks (top 0.12): side strip, front strip and the corner sector inside the curb.
    b.box('paving', (XC + .15 + XSW) / 2, (cy + 24.0) / 2, .06, XSW - XC - .15, 24.0 - cy, .12)
    b.box('paving', (XSW + 22.0) / 2, (YC + .15 + YSW) / 2, .06, 22.0 - XSW, YSW - YC - .15, .12)
    b.box('paving', (cx + XSW) / 2, (YC + .15 + cy) / 2, .06, XSW - cx, cy - YC - .15, .12)
    slab_fan('Corner sidewalk', (cx, cy), arc(cx, cy, R - .15, math.pi, 1.5 * math.pi), 0.0, .12, 'paving')
    y = YSW + 1.5
    while y < 23.0:
        b.box('joint', (XC + .15 + XSW) / 2, y, .1205, XSW - XC - .19, .02, .004)
        y += 1.5
    x = XSW + 1.5
    while x < 21.0:
        b.box('joint', x, (YC + .15 + YSW) / 2, .1205, .02, YSW - YC - .19, .004)
        x += 1.5
    b.box('paving', -16.85, 2.5, .06, 2.3, 43.0, .12)                  # far side of the side street
    b.box('lawn', -22.0, 2.5, .025, 8.0, 43.0, .05)
    b.box('lawn', (XSW - .02 + 22.0) / 2, (YSW - .02 + 24.0) / 2, .025, 22.0 - XSW + .02, 24.0 - YSW + .02, .05)
    for k in range(7):                                            # dashed yellow centre lines
        b.box('yellow', XC - 4.8, -16.0 + 6.0 * k, .0215, .1, 3.0, .003)
        b.box('yellow', -13.0 + 6.0 * k, YC - 4.8, .0215, 3.0, .1, .003)
    # Front walk from the porch steps, the garage apron, side-yard gravel, the neighbour's walk.
    b.box('concrete', -.1, (YSW - .02 + YF - .62) / 2, .055, 1.5, YF - .62 - YSW + .02, .11)
    yy = YSW + 1.0
    while yy < YF - 1.0:
        b.box('joint', -.1, yy, .111, 1.46, .02, .004)
        yy += 1.0
    b.box('concrete', (XSW - .02 + GX0 + .02) / 2, Y1 + 1.3, .055, GX0 + .04 - XSW, 2.3, .11)      # garage apron
    b.box('gravel', (X1 + .01 + XF - .04) / 2, (YF + GY1 + .02) / 2, .035, XF - .05 - X1, GY1 + .02 - YF, .07)
    b.box('gravel', (XF + .04 + NX0) / 2, (NY0 + GY1) / 2, .035, NX0 - XF - .04, GY1 - NY0, .07)
    b.box('concrete', 8.0, (YSW - .02 + NY0 - 2.38) / 2, .055, .9, NY0 - 2.38 - YSW + .02, .11)
    b.flush('site')


def foundations():
    C.box('Foundation', ((X0 - .015 + X1 + .015) / 2, (YS - .015 + Y1 + .019) / 2, .21), (X1 - X0 + .03, Y1 + .034 - YS, .42), 'foundation', 'envelope', 0)
    # Fin plinth and bay plinth 4 mm proud of the main foundation and lapped 0.3 m along it: no shared face at the junction.
    C.box('Fin foundation', ((X1 - T - .012 + X1 + .019) / 2, (YF - .019 + YS + .30) / 2, .21), (T + .031, YS + .319 - YF, .42), 'foundation', 'envelope', 0)
    C.box('Bay plinth', ((X0 - .019 + XB + .012) / 2, (YF - .019 + YS + .30) / 2, .2325), (XB - X0 + .031, YS + .319 - YF, .465), 'foundation', 'envelope', 0)   # 5 mm under the porch landing: no pocket at its side


def glazed_bay():
    """Two-storey corner bay: black posts, mullions, rails, transoms and spandrel round two lights per face per storey;
    a solid cedar end wall on its east side; glass registered as curtain-wall openings."""
    b = Batch()
    xa, xb = X0 + .12, XB - T
    ya, yb = YF + .12, YS - .08
    zb, zt = .38, HG
    # Corner post and the jamb post where the west glazing meets the side-street wall.
    b.box('frame', X0 + .05, YF + .05, (zb + zt + .02) / 2, .14, .14, zt + .02 - zb)
    b.box('frame', X0 + .05, YS - .03, (zb + zt + .02) / 2, .14, .10, zt + .02 - zb)
    # South face (y = YF): mullion, end jamb, rails, transom, spandrel, glass.
    xm = (xa + xb) / 2
    for x, w in ((xm, .07), (xb - .025, .07)):
        b.box('frame', x, YF + .06, (zb + zt) / 2, w, .12, zt - zb)
    for z, h in ((FL1 - .02, .10), (zt - .03, .08), (FL2 + .95, .06)):          # rails and transom 6 mm inside the mullion faces
        b.box('frame', (xa + xb) / 2, YF + .06, z, xb - xa, .108, h)
    b.box('frame', (xa + xb) / 2, YF + .025, FL2 - .09, xb - xa, .07, .42)
    for z0, z1 in ((FL1 + .03, FL2 - .30), (FL2 + .12, zt - .07)):
        b.box('glass', (xa + xb) / 2, YF + .06, (z0 + z1) / 2, xb - xa + .02, .012, z1 - z0)
    # West face (x = X0).
    ym = (ya + yb) / 2
    b.box('frame', X0 + .06, ym, (zb + zt) / 2, .12, .07, zt - zb)
    for z, h in ((FL1 - .02, .10), (zt - .03, .08), (FL2 + .95, .06)):
        b.box('frame', X0 + .06, (ya + yb) / 2, z, .108, yb - ya, h)
    b.box('frame', X0 + .025, (ya + yb) / 2, FL2 - .09, .07, yb - ya, .42)
    for z0, z1 in ((FL1 + .03, FL2 - .30), (FL2 + .12, zt - .07)):
        b.box('glass', X0 + .06, (ya + yb) / 2, (z0 + z1) / 2, .012, yb - ya + .02, z1 - z0)
    b.flush('glazed bay')
    # Cedar end wall on the bay's east side (its south end is the cedar strip between the glass and the balcony).
    C.box('Bay end wall', (XB - T / 2, (YF + YS + .02) / 2, (.35 + WT) / 2), (T, YS + .02 - YF, WT - .35), 'cedar', 'envelope', 0)
    e = C.Face((XB, 0, 0), (0, 1, 0), (-1, 0, 0), 'bay end east')
    m = Merge(e)
    cladding(m, YF, YS, .43, HG, [], seed=11)
    m.flush('bay end')
    fs = C.Face((0, YF, 0), (1, 0, 0), (0, 1, 0), 'bay south')
    fw = C.Face((X0, 0, 0), (0, 1, 0), (1, 0, 0), 'bay west')
    for i, x in enumerate((xa, xm)):
        for z0, z1 in ((FL1 + .03, FL2 - .30), (FL2 + .12, zt - .07)):
            register(fs, hole(f'bay south light {i} {"lower" if z0 < 1 else "upper"}', x + (xm - xa) / 2, z0, xm - xa - .07, z1 - z0), .06, 'curtain wall', 'living room')
    for i, y in enumerate((ya, ym)):
        for z0, z1 in ((FL1 + .03, FL2 - .30), (FL2 + .12, zt - .07)):
            register(fw, hole(f'bay west light {i} {"lower" if z0 < 1 else "upper"}', y + (ym - ya) / 2, z0, ym - ya - .07, z1 - z0), .06, 'curtain wall', 'living room')


def front_band():
    """The deep cedar band across the whole front under the roof edge, its return over the bay's west glazing, and the
    cedar ceiling of the recessed balcony."""
    C.box('Front cedar band', (0.0, (YF - .012 + YF + .30) / 2, (HG + WT) / 2), (X1 - X0 + .024, .312, WT - HG), 'cedar', 'envelope', 0)
    f = C.Face((0, YF - .012, 0), (1, 0, 0), (0, 1, 0), 'front band')
    m = Merge(f)
    cladding(m, X0 - .012, X1 + .012, HG + .01, ZE - .2, [], seed=13)
    m.flush('front band')
    C.box('Bay west band', ((X0 - .010 + X0 + T) / 2, (YF + .29 + YS + .02) / 2, (HG + WT) / 2), (T + .01, YS + .02 - YF - .29, WT - HG), 'cedar', 'envelope', 0)
    f = C.Face((X0 - .010, 0, 0), (0, 1, 0), (1, 0, 0), 'bay west band')
    m = Merge(f)
    cladding(m, YF + .3, YS, HG + .01, ZE - .2, [], seed=15)
    m.flush('bay west band')
    C.box('Balcony ceiling', ((XB - .02 + X1 - T + .02) / 2, (YF + .29 + YS) / 2, HG + .035), (X1 - T - XB + .04, YS - YF - .29, .06), 'cedar', 'balcony', 0)


def porch():
    """Concrete landing and steps under the balcony; the balcony slab, cedar porch ceiling, grey steel channel fascia
    with bolt heads, and a frameless glass railing in a base shoe under a steel cap."""
    C.box('Porch landing', ((XB - .02 + XB + 2.25) / 2, (YF + YS + .02) / 2, .235), (2.27, YS + .02 - YF, .47), 'concrete', 'porch', 0)
    C.prism('Porch steps', [(YF + .02, 0.0), (YF + .02, .35), (YF - .32, .35), (YF - .32, .23), (YF - .64, .23), (YF - .64, 0.0)],
            'x', -.88, .68, 'concrete', 'porch')
    x0, x1 = XB - .02, X1 - T + .02
    C.box('Balcony slab', ((x0 + x1) / 2, (YF + YS + .02) / 2, FL2 - .22), (x1 - x0, YS + .02 - YF, .32), 'concrete', 'balcony', 0)
    C.box('Porch ceiling', ((x0 + x1) / 2, (YF + .02 + YS) / 2, FL2 - .40), (x1 - x0, YS - YF - .02, .06), 'cedar', 'balcony', 0)
    C.box('Balcony fascia', ((x0 + x1) / 2, YF - .03, FL2 - .23), (x1 - x0, .08, .40), 'steel', 'balcony', 0)
    b = Batch()
    n = 8                                                     # paired standoff bolts, not a perforated grid
    for i in range(n):
        x = XB + .15 + (X1 - T - XB - .3) * i / (n - 1)
        for z in (FL2 - .30, FL2 - .16):
            b.box('hardware', x, YF - .078, z, .04, .02, .04)
    b.box('steel', (XB + X1 - T) / 2, YF + .06, FL2 - .02, X1 - T - XB, .06, .10)
    wp = (X1 - T - XB - .06 - .04) / 3
    for i in range(3):
        x = XB + .03 + wp / 2 + i * (wp + .02)
        b.box('glass', x, YF + .06, FL2 + .48, wp, .015, 1.04)
    b.box('steel', (XB + X1 - T) / 2, YF + .06, FL2 + 1.02, X1 - T - XB, .05, .045)
    b.flush('balcony')


def south_face():
    """Main south wall behind the porch and balcony: wood front door with a sidelight, a two-light window, and the
    four-light sliding wall onto the balcony."""
    f = C.Face((0, YS, 0), (1, 0, 0), (0, 1, 0), 'south')
    door = hole('front door', XB + .7, FL1 - .03, .96, 2.2, kind='door')
    side = hole('front sidelight', XB + 1.38, FL1 - .03, .32, 2.2)
    win = hole('porch window', XB + 2.95, FL1 + .5, 1.3, 1.6)
    slide = hole('balcony sliding wall', (XB + .3 + X1 - T - .2) / 2, FL2, (X1 - T - .2) - (XB + .3), HG - FL2, kind='door')
    holes = [door, side, win, slide]
    f.wall('south carrier', XB - .24, X1 - T + .01, .35, WT, depth=T, role='cedar', holes=holes)
    m = Merge(f)
    cladding(m, XB, X1 - T, .43, HG, holes, seed=17)
    # Wood front door in a black frame, a long pull, and a threshold.
    u, z, w, h = door['u'], door['z'], door['w'], door['h']
    for s in (-1, 1):
        m.box('frame', u + s * (w / 2 - .03), .09, z + h / 2, .06, .10, h)
    m.box('frame', u, .09, z + h - .03, w - .12, .10, .06)
    m.box('door_wood', u, .09, z + .03 + (h - .06) / 2, w - .12, .05, h - .06)
    m.box('hardware', u + w / 2 - .17, .055, z + 1.05, .03, .02, .9)
    m.box('steel', u, .12, FL1 - .025, w, .24, .04)
    register(f, door, .09, 'entry door', 'entry hall')
    framed(m, f, side, cols=1, rows=1, inset=.07, occupied='entry hall', frame='frame')
    m.box('steel', side['u'], .12, FL1 - .025, side['w'], .24, .04)
    window(m, f, win, cols=2, occupied='living room')
    framed(m, f, slide, cols=4, rows=1, inset=.09, occupied='sitting room', kind='door', frame='frame')
    m.flush('south')


def west_face():
    """Side-street wall: tall narrow window pair, wall lamp, the recessed side entry under a horizontal-board panel with
    a small window above, small rear windows, a downpipe at the glazed bay."""
    w = C.Face((X0, 0, 0), (0, 1, 0), (1, 0, 0), 'west')
    tg = hole('west tall ground window', YS + 1.55, FL1 + .3, .5, 2.05)
    tu = hole('west tall upper window', YS + 1.55, FL2 + .45, .5, 1.75)
    nc = hole('side entry recess', NU, FL1 - .03, NW, 2.52, kind='door')
    su = hole('west small upper window', YS + 3.55, FL2 + 1.2, .55, .75)
    ru = hole('west rear upper window', YS + 6.05, FL2 + 1.25, 1.15, .8)
    rg = hole('west rear ground window', YS + 6.05, FL1 + 1.35, 1.0, .6)
    holes = [tg, tu, nc, su, ru, rg]
    w.wall('west carrier', YS, Y1 - .01, .35, WT, depth=T, role='cedar', holes=holes)
    m = Merge(w)
    cladding(m, YS, Y1 - .01, .43, ZE - .2, holes, seed=3, hzone=(YS + 2.3, YS + 4.1, nc['z'] + nc['h']))
    for h in (tg, tu):
        window(m, w, h, occupied='stair hall')
    window(m, w, su, occupied='bathroom')
    window(m, w, ru, cols=2, occupied='bedroom')
    window(m, w, rg, cols=2, occupied='kitchen')
    register(w, nc, ND, 'recessed side entry', 'side entry hall')
    m.box('hardware', YS + .75, -.03, FL1 + 1.95, .1, .06, .22)
    m.box('lamp', YS + .75, -.10, FL1 + 1.9, .12, .1, .16)
    m.box('hardware', YS + .75, -.10, FL1 + 2.0, .14, .12, .03)
    m.flush('west')
    b = Batch()
    b.box('fascia', X0 - .04, YS + .14, (.05 + ZE - .3) / 2, .07, .07, ZE - .3 - .05)
    b.beam('fascia', (X0 - .04, YS + .14, ZE - .33), (XE0 + .03, YS + .14, ZE - .16), .062, .062, ext=.03)
    b.flush('downpipe')


def niche():
    """The recessed side entry: a shallow reveal lined in horizontal cedar boards (both returns, the back wall beside the
    door and the head), a wood door toward the north return, a concrete floor and two steps down across the planting
    strip to the side sidewalk. Linings lap 10 mm into the wall carrier and into each other: no open corner at the head."""
    b = Batch()
    u0, u1 = NU - NW / 2, NU + NW / 2
    z0, zt = FL1 - .03, FL1 - .03 + 2.52
    xd = X0 + ND                                     # face of the back wall
    for ua, ub in ((u0 - .01, u0 + .1), (u1 - .1, u1 + .01)):      # returns stop 1 cm inside the head lining
        b.box('cedar', X0 + (.015 + ND) / 2, (ua + ub) / 2, (z0 + zt - .01) / 2, ND + .005, ub - ua, zt - .01 - z0)
    b.box('cedar', X0 + (.022 + ND) / 2, NU, zt + .04, ND - .002, NW + .016, .14)                 # head: zt - .03 .. zt + .11, its face 7 mm behind the returns' faces
    b.box('cedar', xd + .06, NU, (z0 + zt + .1) / 2, .12, NW + .1, zt + .1 - z0)                   # back wall
    # Horizontal board joints on both return faces and on the back wall south of the door and over it.
    z = z0 + .14
    while z < zt - .05:
        for u in (u0 + .1 + .002, u1 - .1 - .002):                  # joints sit 1 mm into the lining
            b.box('cedar_joint', X0 + (.01 + ND) / 2, u, z, ND - .02, .006, .012)
        b.box('cedar_joint', xd - .002, (u0 + .1 + NDU - .5) / 2, z, .006, NDU - .5 - u0 - .1, .012)
        if z > z0 + 2.24:
            b.box('cedar_joint', xd - .002, (NDU - .5 + u1 - .1) / 2, z, .006, u1 - .1 - NDU + .5, .012)
        z += .14
    for k, uu in enumerate((u0 + .25, u0 + .43)):
        b.box('cedar_light', xd - .0015, uu, (z0 + zt) / 2, .004, .17, zt - z0 - .04)
    # Wood door (0.92 m) in a slim black frame, a long pull, a threshold, a mailbox on the south return.
    b.box('frame', xd - .012, NDU, z0 + 1.1, .03, .98, 2.2)
    b.box('door_wood', xd - .035, NDU, z0 + 1.08, .03, .9, 2.12)
    b.box('hardware', xd - .057, NDU - .34, z0 + 1.1, .02, .03, .8)
    b.box('hardware', X0 + .24, u0 + .1 + .035, z0 + 1.35, .2, .06, .26)
    b.box('concrete', X0 + (.012 + ND - .005) / 2, NU, (FL1 - .02) / 2, ND - .017, NW, FL1 - .02)   # floor edge 7 mm behind the returns' faces
    b.flush('side entry')
    C.prism('Side entry steps', [(X0 + .02, 0.0), (X0 + .02, .29), (X0 - .35, .29), (X0 - .35, .115), (XSW - .02, .115), (XSW - .02, 0.0)],
            'y', NU - .7, NU + .7, 'concrete', 'side entry')


def east_face():
    """East wall to the neighbour (teaching assumption: two upper and two ground windows) and the cedar end fin."""
    e = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    hs = [hole('east upper window south', -.3, FL2 + .9, .9, 1.2), hole('east upper window north', 2.1, FL2 + .9, .9, 1.2),
          hole('east ground window', .9, FL1 + 1.0, 1.2, 1.0), hole('east small window', 2.6, FL1 + 1.2, .6, .8)]
    e.wall('east carrier', YF, Y1 - .01, .35, WT, depth=T, role='cedar', holes=hs)
    m = Merge(e)
    cladding(m, YF, Y1 - .01, .43, ZE - .2, hs, seed=5)
    for h in hs:
        window(m, e, h, cols=2 if h['w'] > 1 else 1, occupied='bedroom' if h['z'] > 3 else 'kitchen')
    m.flush('east')
    fi = C.Face((X1 - T, 0, 0), (0, 1, 0), (1, 0, 0), 'fin inner')
    m = Merge(fi)
    cladding(m, YF, YS, .43, HG, [], seed=19)
    m.flush('fin inner')


def north_face():
    n = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')                    # u = -x
    hs = [hole('north upper window west', 1.9, FL2 + 1.15, 1.1, 1.0), hole('north upper window east', -1.6, FL2 + 1.15, 1.1, 1.0)]
    n.wall('north carrier', -(X1 + .004), -(X0 - .004), .35, WT, depth=T, role='cedar', holes=hs)
    m = Merge(n)
    cladding(m, -(X1 + .004), -(X0 - .004), .43, ZE - .2, hs, seed=9)
    for h in hs:
        window(m, n, h, cols=2, occupied='bedroom')
    m.flush('north')


def interior():
    """Floors, ceiling, a white partition as the backdrop seen through the glass, furniture and room lights."""
    xi0, xi1 = X0 + T - .02, X1 - T + .02
    yi0, yi1 = YS + .05, Y1 - T + .02
    n0, n1 = NU - NW / 2 - .12, NU + NW / 2 + .12
    for name, x0, x1, y0, y1 in (('south', xi0, xi1, yi0, n0), ('niche', X0 + ND + .12, xi1, n0, n1), ('north', xi0, xi1, n1, yi1)):
        C.box(f'Ground floor {name}', ((x0 + x1) / 2, (y0 + y1) / 2, FL1 - .06), (x1 - x0, y1 - y0, .12), 'floor', 'inside', 0)
    C.box('Ground floor bay', ((X0 + .02 + XB - T + .02) / 2, (YF + .12 + yi0) / 2, FL1 - .06), (XB - T - X0, yi0 - YF - .12, .12), 'floor', 'inside', 0)
    for z0, z1, name in ((FL2 - .25, FL2, 'Upper floor'), (5.75, 5.85, 'Ceiling')):
        C.box(name, ((xi0 + xi1) / 2, (yi0 + yi1) / 2, (z0 + z1) / 2), (xi1 - xi0, yi1 - yi0, z1 - z0), 'floor' if z0 < 5 else 'interior', 'inside', 0)
        C.box(name + ' bay', ((X0 + .02 + XB - T + .02) / 2, (YF + .12 + yi0) / 2, (z0 + z1) / 2), (XB - T - X0, yi0 - YF - .12, z1 - z0), 'floor' if z0 < 5 else 'interior', 'inside', 0)
    C.box('Partition', ((xi0 + xi1) / 2, YS + 2.0, (FL1 + 5.75) / 2), (xi1 - xi0, .12, 5.75 - FL1), 'interior', 'inside', 0)
    b = Batch()
    tx, ty = -2.3, -3.15                                          # dining table and bench in the glazed corner
    b.box('floor', tx, ty, FL1 + .745, 1.5, .85, .05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.box('hardware', tx + sx * .68, ty + sy * .36, FL1 + .36, .04, .04, .72)
    b.box('floor', tx, ty + .72, FL1 + .44, 1.4, .36, .05)
    for sx in (-1, 1):
        b.box('hardware', tx + sx * .6, ty + .72, FL1 + .21, .04, .3, .42)
    b.box('lamp', tx, ty, FL1 + 2.05, .36, .36, .1)
    b.box('hardware', tx, ty, (FL1 + 2.1 + FL2 - .25) / 2, .015, .015, FL2 - .25 - FL1 - 2.1)
    b.box('dark_cloth', 1.4, YS + 1.5, FL1 + .22, 2.0, .9, .44)          # sofa against the partition
    b.box('dark_cloth', 1.4, YS + 1.86, FL1 + .58, 2.0, .2, .4)
    b.box('furniture', 1.4, YS + 1.15, FL1 + .58, .9, .5, .05)
    b.box('furniture', 1.6, YS + 1.3, FL2 + .25, 1.6, 1.0, .5)          # bed upstairs, headboard to the partition
    b.box('floor', 1.6, YS + 1.88, FL2 + .6, 1.7, .08, 1.0)
    b.box('dark_cloth', -2.4, -3.0, FL2 + .25, .8, .8, .5)              # armchair and floor lamp in the upper bay
    b.box('hardware', -1.7, -3.4, FL2 + .75, .03, .03, 1.5)
    b.box('lamp', -1.7, -3.4, FL2 + 1.55, .3, .3, .25)
    b.flush('furniture')
    for name, x, y, z, p in (('ground bay', -2.2, -3.0, FL1 + 2.2, 55), ('ground living', 1.3, -2.4, FL1 + 2.2, 45),
                             ('upper bay', -2.2, -3.0, FL2 + 2.0, 45), ('upper room', 1.3, -2.4, FL2 + 2.0, 45),
                             ('north ground', 0.0, 2.0, FL1 + 2.2, 30), ('north upper', 0.0, 2.0, FL2 + 2.0, 30)):
        C.qa_room_light(name, (x, y, z), p, 2.0)


def rib(b, p, q, f=zr, w=.028):
    b.beam('metal_rib', (p[0], p[1], f(*p) + .018), (q[0], q[1], f(*q) + .018), w, .04)


def roof():
    """Hipped standing-seam roof: plate, seams on all four planes (cut round the skylight), hip and ridge caps, thin dark
    fascia, cedar soffit, and the skylight on the west slope."""
    strip('Roof plate', [(XE0, YE0), (XE1, YE0), (XE1, YE1), (XE0, YE1)],
          [(0.0, YF + HI), (0.0, YF + HI), (0.0, Y1 - HI), (0.0, Y1 - HI)], ZE, ZR, 'metal', 'roof')
    b = Batch()
    xs, ys, hx, hy = -2.55, .9, .5, .42
    top = ZR - ZE
    y = YE0 + .25
    while y < YE1 - .2:
        lift = min(SE * (y - YE0), SE * (YE1 - y), top)
        if lift > .1:
            for s in (-1, 1):
                xe = XE0 + .03 if s < 0 else XE1 - .03
                xt = (XE0 + lift / SL - .05) if s < 0 else (XE1 - lift / SL + .05)
                if s < 0 and ys - hy - .06 < y < ys + hy + .06:
                    rib(b, (xe, y), (xs - hx - .04, y)); rib(b, (xs + hx + .04, y), (xt, y))
                else:
                    rib(b, (xe, y), (xt, y))
        y += .46
    x = XE0 + .25
    while x < XE1 - .2:
        lift = min(SL * (x - XE0), SL * (XE1 - x), top)
        if lift > .1:
            rib(b, (x, YE0 + .03), (x, YE0 + lift / SE - .05))
            rib(b, (x, YE1 - .03), (x, YE1 - lift / SE + .05))
        x += .46
    for (xa, ya), (xr, yr) in (((XE0, YE0), (0.0, YF + HI)), ((XE1, YE0), (0.0, YF + HI)), ((XE0, YE1), (0.0, Y1 - HI)), ((XE1, YE1), (0.0, Y1 - HI))):
        b.beam('metal_rib', (xa + (.02 if xa < 0 else -.02), ya + (.02 if ya < 0 else -.02), ZE + .015), (xr, yr, ZR + .015), .09, .05)
    b.beam('metal_rib', (0.0, YF + HI - .05, ZR + .018), (0.0, Y1 - HI + .05, ZR + .018), .11, .05)
    # Skylight: dark curb following the slope, pale glazing on top.
    def sk(x, y, dz):
        return (x, y, zr(x, y) + dz)
    b._hex('fascia', [sk(xs - hx, ys - hy, -.03), sk(xs + hx, ys - hy, -.03), sk(xs + hx, ys + hy, -.03), sk(xs - hx, ys + hy, -.03),
                      sk(xs - hx, ys - hy, .13), sk(xs + hx, ys - hy, .13), sk(xs + hx, ys + hy, .13), sk(xs - hx, ys + hy, .13)])
    i = .06
    b._hex('skylight', [sk(xs - hx + i, ys - hy + i, .12), sk(xs + hx - i, ys - hy + i, .12), sk(xs + hx - i, ys + hy - i, .12), sk(xs - hx + i, ys + hy - i, .12),
                        sk(xs - hx + i, ys - hy + i, .15), sk(xs + hx - i, ys - hy + i, .15), sk(xs + hx - i, ys + hy - i, .15), sk(xs - hx + i, ys + hy - i, .15)])
    # Fascia: front and rear boards a few mm deeper and taller than the side boards (no shared planes at the corners).
    for yy in (YE0 - .0125, YE1 + .0125):
        b.box('fascia', 0.0, yy, ZE - .085, XE1 - XE0 + .068, .035, .23)
    for xx in (XE0 - .0135, XE1 + .0135):
        b.box('fascia', xx, (YE0 + YE1) / 2, ZE - .0875, .037, YE1 - YE0 + .056, .225)
    # Cedar soffit: front and rear boards, side boards 4 mm higher.
    b.box('cedar', 0.0, (YE0 + .005 + YF + .03) / 2, ZE - .175, XE1 - XE0 - .01, YF + .025 - YE0, .03)
    b.box('cedar', 0.0, (YE1 - .005 + Y1 - .03) / 2, ZE - .175, XE1 - XE0 - .01, YE1 - Y1 + .025, .03)
    b.box('cedar', (XE0 + .005 + X0 + .03) / 2, (YF + Y1) / 2, ZE - .171, X0 + .025 - XE0, Y1 - YF - .04, .03)
    b.box('cedar', (XE1 - .005 + X1 - .03) / 2, (YF + Y1) / 2, ZE - .171, XE1 - X1 + .025, Y1 - YF - .04, .03)
    b.flush('roof trim')


def garage():
    """One-storey cedar garage against the rear wall: board door facing the side street, side door to the east."""
    C.box('Garage foundation', ((GX0 - .015 + GX1 + .015) / 2, (Y1 - .05 + GY1 + .019) / 2, .09), (GX1 - GX0 + .03, GY1 + .069 - Y1, .18), 'foundation', 'garage', 0)
    gd = hole('garage door', Y1 + 1.3, .16, 2.0, 2.2, kind='garage door')
    gw = C.Face((GX0, 0, 0), (0, 1, 0), (1, 0, 0), 'garage west')
    gw.wall('garage west carrier', Y1 - .05, GY1 - .01, .12, GH, depth=T, role='cedar', holes=[gd])
    sd = hole('garage side door', Y1 + 1.3, .18, .9, 2.1, kind='door')
    ge = C.Face((GX1, 0, 0), (0, 1, 0), (-1, 0, 0), 'garage east')
    ge.wall('garage east carrier', Y1 - .05, GY1 - .01, .12, GH, depth=T, role='cedar', holes=[sd])
    gn = C.Face((0, GY1, 0), (-1, 0, 0), (0, -1, 0), 'garage north')
    gn.wall('garage north carrier', -(GX1 + .004), -(GX0 - .004), .12, GH, depth=T, role='cedar')
    m = Merge(gw)
    cladding(m, Y1, GY1 - .01, .2, GZE - .2, [gd], seed=21)
    u, z, w, h = gd['u'], gd['z'], gd['w'], gd['h']
    m.box('cedar_light', u, .13, z + .025 + (h - .03) / 2, w - .02, .05, h - .03)
    zz = z + .17
    while zz < z + h - .1:
        m.box('cedar_joint', u, .103, zz, w - .06, .006, .012)
        zz += .15
    m.box('hardware', u + .9, .1, z + .95, .25, .02, .04)
    register(gw, gd, .13, 'garage door', 'garage')
    m.flush('garage west')
    m = Merge(ge)
    cladding(m, Y1, GY1 - .01, .2, GZE - .2, [sd], seed=23)
    m.box('door_wood', sd['u'], .1, sd['z'] + .02 + (sd['h'] - .03) / 2, sd['w'] - .02, .05, sd['h'] - .03)
    register(ge, sd, .1, 'garage side door', 'garage')
    m.flush('garage east')
    m = Merge(gn)
    cladding(m, -(GX1 + .004), -(GX0 - .004), .2, GZE - .2, [], seed=25)
    m.flush('garage north')
    # Roof (top view): a north slope and two steeper hipped ends rising to a short east-west ridge along the rear wall,
    # the ridge and the upper edges buried in the house's rear wall carrier.
    strip('Garage roof plate', [(GXE0, GYS), (GXE1, GYS), (GXE1, GYE1), (GXE0, GYE1)],
          [(GXR0, GYS), (GXR1, GYS), (GXR1, GYS), (GXR0, GYS)], GZE, GZR, 'metal', 'garage roof')
    b = Batch()
    x = GXE0 + .25                                   # seams down the north slope, stopped at the hips
    while x < GXE1 - .2:
        yh = max(GYE1 - GSE * min(x - GXE0, GXE1 - x) / GSN, Y1 + .03)
        if GYE1 - .03 - (yh + .05) > .12:
            rib(b, (x, GYE1 - .03), (x, yh + .05), gzr)
        x += .46
    y = Y1 + .18                                     # seams down the hipped ends (east-west), stopped at the hips
    while y < GYE1 - .2:
        dx = min(GSN * (GYE1 - y) / GSE, GIN)
        if dx > .15:
            rib(b, (GXE0 + .03, y), (GXE0 + dx - .05, y), gzr)
            rib(b, (GXE1 - .03, y), (GXE1 - dx + .05, y), gzr)
        y += .46
    for xa, xr in ((GXE0, GXR0), (GXE1, GXR1)):     # hip caps from the north corners up into the rear wall
        b.beam('metal_rib', (xa + (.02 if xa < GXM else -.02), GYE1 - .02, GZE + .015), (xr, GYS, GZR + .015), .11, .05)
    b.beam('metal_rib', (GXR0, Y1 + .045, gzr(GXR0, Y1 + .045) + .018), (GXR1, Y1 + .045, gzr(GXR1, Y1 + .045) + .018), .09, .05)   # wall flashing
    for xx in (GXE0 - .0135, GXE1 + .0135):
        b.box('fascia', xx, (Y1 - .02 + GYE1 + .028) / 2, GZE - .0875, .037, GYE1 + .048 - Y1, .225)
    b.box('fascia', GXM, GYE1 + .0125, GZE - .085, GXE1 - GXE0 + .068, .035, .23)
    for xx, x0, x1 in ((GXE0, GXE0 + .005, GX0 + .03), (GXE1, GX1 - .03, GXE1 - .005)):
        b.box('cedar', (x0 + x1) / 2, (Y1 - .02 + GY1) / 2, GZE - .175, x1 - x0, GY1 - Y1 + .02, .03)
    b.box('cedar', GXM, (GY1 - .03 + GYE1 - .005) / 2, GZE - .171, GXE1 - GXE0 - .01, GYE1 - GY1 + .025, .03)
    b.flush('garage roof trim')


def neighbour():
    """Context: the two-and-a-half-storey stucco house east of the lot, hipped shingle roof, white-trimmed windows and a
    front porch; a board fence on the lot line; an air-conditioning unit in the side yard."""
    C.box('Neighbour walls', ((NX0 + NX1) / 2, (NY0 + NY1) / 2, 3.25), (NX1 - NX0, NY1 - NY0, 6.5), 'stucco', 'context', 0)
    C.box('Neighbour foundation', ((NX0 + NX1) / 2, (NY0 + NY1) / 2, .45), (NX1 - NX0 + .03, NY1 - NY0 + .03, .9), 'foundation', 'context', 0)
    nov, nsl, xm = .45, .7, (NX0 + NX1) / 2
    strip('Neighbour roof', [(NX0 - nov, NY0 - nov), (NX1 + nov, NY0 - nov), (NX1 + nov, NY1 + nov), (NX0 - nov, NY1 + nov)],
          [(xm, NY0 + 4.0), (xm, NY0 + 4.0), (xm, NY1 - 4.0), (xm, NY1 - 4.0)], 6.6 - nov * nsl, 6.6 + 2.8, 'shingle', 'context')
    b = Batch()
    ze = 6.6 - nov * nsl
    for yy in (NY0 - nov - .0125, NY1 + nov + .0125):
        b.box('white', xm, yy, ze - .085, NX1 - NX0 + 2 * nov + .068, .035, .23)
    for xx in (NX0 - nov - .0135, NX1 + nov + .0135):
        b.box('white', xx, (NY0 + NY1) / 2, ze - .0875, .037, NY1 - NY0 + 2 * nov + .056, .225)

    def win(axis, pos, a, z, w, h, s):
        """Flat-applied context window: dark glazing 1.2 cm proud, white casing and sill."""
        if axis == 'x':
            b.box('glass_dark', pos - s * .004, a, z + h / 2, .032, w, h)
            for t in (-1, 1):
                b.box('white', pos - s * .02, a + t * (w / 2 + .05), z + h / 2, .04, .1, h + .2)
            b.box('white', pos - s * .02, a, z + h + .05, .04, w, .1)
            b.box('white', pos - s * .03, a, z - .04, .06, w + .25, .08)
            b.box('white', pos - s * .022, a, z + h * .55, .02, w, .04)
        else:
            b.box('glass_dark', a, pos - s * .004, z + h / 2, w, .032, h)
            for t in (-1, 1):
                b.box('white', a + t * (w / 2 + .05), pos - s * .02, z + h / 2, .1, .04, h + .2)
            b.box('white', a, pos - s * .02, z + h + .05, w, .04, .1)
            b.box('white', a, pos - s * .03, z - .04, w + .25, .06, .08)
            b.box('white', a, pos - s * .022, z + h * .55, w, .02, .04)
    for y in (-1.6, 1.4, 4.6):
        win('x', NX0, y, 3.9, .9, 1.4, 1)
    for y in (-.6, 3.2):
        win('x', NX0, y, 1.5, 1.0, 1.4, 1)
    for x in (6.4, 10.0, 12.0):
        win('y', NY0, x, 3.9, 1.0, 1.45, 1)
    win('y', NY0, 11.0, 1.45, 2.2, 1.55, 1)
    b.box('white', 8.0, NY0 - .02, 1.9, 1.1, .06, 2.2)                  # door casing and the door
    b.box('door_wood', 8.0, NY0 - .03, 1.88, .9, .05, 2.0)
    b.box('concrete', 8.0, NY0 - .64, .45, 2.2, 1.32, .9)               # porch deck, posts, beam
    for x in (7.05, 8.95):
        b.box('white', x, NY0 - 1.2, 2.15, .16, .16, 2.5)
    b.box('white', 8.0, NY0 - 1.2, 3.47, 2.3, .2, .2)
    b.box('steel', 4.75, 1.4, .4, .75, .75, .8)                          # air-conditioning unit in the side yard
    b.flush('neighbour')
    C.prism('Neighbour porch steps', [(NY0 - 1.28, 0.0), (NY0 - 1.28, .72), (NY0 - 1.56, .72), (NY0 - 1.56, .54), (NY0 - 1.84, .54),
                                      (NY0 - 1.84, .36), (NY0 - 2.12, .36), (NY0 - 2.12, .18), (NY0 - 2.4, .18), (NY0 - 2.4, 0.0)],
            'x', 7.4, 8.6, 'concrete', 'context')
    C.prism('Neighbour porch roof', [(NY0 + .1, 3.9), (NY0 + .1, 4.05), (NY0 - 1.55, 3.62), (NY0 - 1.55, 3.47)], 'x', 6.75, 9.25, 'shingle', 'context')
    f = Batch()                                                         # board fence on the lot line, posts every 2.4 m
    y0, y1 = YS - .1, GY1 + 2.5
    f.box('fence', XF, (y0 + y1) / 2, .92, .05, y1 - y0, 1.74)
    f.box('fence', XF, (y0 + y1) / 2, 1.82, .1, y1 - y0 + .04, .05)
    yy = y0
    while yy <= y1 + .01:
        f.box('fence', XF, yy, .93, .1, .1, 1.86)
        yy += 2.4
    k = 0
    yy = y0 + .15
    while yy < y1 - .05:
        for s in (-1, 1):
            f.box('cedar_joint', XF + s * .027, yy, .92, .006, .012, 1.7)
        yy += .15
    f.flush('fence')


def sword_fern(kit, name, fronds=18, length=.82, role='pk_leaf', crown_role='pk_crown', seed=7):
    """Western sword fern: a vase of arching pinnate fronds from a low dark crown. Each frond is a slim rachis carrying
    18 pairs of keeled leaflets (pinnae) that are short at the base, longest a quarter of the way up and taper to the
    tip, angled forward and slightly drooping; the fronds arch out and over, so the mass reads as a fountain of
    fronds, never as strap grass."""
    rnd = random.Random(seed); parts = {role: PkGeo(), crown_role: PkGeo()}
    _pk_dome(parts[crown_role], (0., 0., -.02), (.08, .08, .05), -PK_SINK, seed=seed, bump=.004, wave=.05, seg=12, rings=4)
    for k in range(fronds):
        phi = 2 * math.pi * (k + rnd.uniform(-.3, .3)) / fronds; q = rnd.random()
        elev = math.radians(78 - 30 * q); bend = math.radians(75 + 55 * q); L = length * rnd.uniform(.82, 1.1) * (1.06 - .22 * q)
        pts = _pk_arc((.03 * math.cos(phi), .03 * math.sin(phi), -PK_SINK), phi, elev, bend, L, 11, floor=.04)
        n = len(pts)
        _pk_tube(parts[role], pts, .006, .0025, 3)
        side = (-math.sin(phi), math.cos(phi), 0.)
        for j in range(18):
            tq = .1 + .86 * j / 17
            f = tq * (n - 1); i = min(int(f), n - 2); a = f - i
            pnt = tuple(pts[i][c] + (pts[i + 1][c] - pts[i][c]) * a for c in range(3))
            tan = _pk_norm(tuple(pts[i + 1][c] - pts[i][c] for c in range(3)))
            plen = .105 * (.55 + .45 * min(1., tq * 4)) * (1 - .78 * max(0., tq - .25) / .75)
            for s in (-1, 1):
                d = _pk_norm(tuple(side[c] * s * .82 + tan[c] * .5 for c in range(3)))
                d = _pk_norm((d[0], d[1], d[2] - .18))
                q1 = tuple(pnt[c] + d[c] * plen * .5 + (.008 if c == 2 else 0.) for c in range(3))
                q2 = tuple(pnt[c] + d[c] * plen for c in range(3))
                _pk_blade(parts[role], [pnt, q1, q2], math.atan2(d[1], d[0]), .024 * (1 - .45 * tq), fold=.16)
    return kit.proto(name, parts)


def protos(kit):
    """Laneway garden library: sword and deer ferns, a stiff spiky grass, feather reed grass with plumes, blue fescue,
    golden forest grass, a red Japanese maple and a small green shrub."""
    P = {}
    P['fern'] = sword_fern(kit, 'lw_sword_fern', seed=7)
    P['fern2'] = sword_fern(kit, 'lw_sword_fern_b', fronds=14, length=.62, role='pk_leaf2', seed=9)
    P['spiky'] = arching_grass(kit, 'lw_spiky_grass', blades=26, height=.68, width=.034, role='pk_leaf_dark', seed=27)
    P['reed'] = arching_grass(kit, 'lw_feather_reed', blades=48, height=.6, width=.016, role='pk_blade', plume_role='pk_plume',
                              plumes=6, plume_height=1.9, seed=11)
    P['fescue'] = arching_grass(kit, 'lw_blue_fescue', blades=38, height=.24, width=.011, role='pk_blade_blue', crown_role='pk_crown_blue', seed=13)
    P['golden'] = arching_grass(kit, 'lw_forest_grass', blades=40, height=.3, width=.02, role='pk_leaf_light', seed=15)
    P['maple'] = shrub_mass(kit, 'lw_japanese_maple', radius=.95, height=1.85, lobes=7, role='pk_leaf_red', role2='maple_red2',
                            core_role='maple_core', seed=17)
    P['shrub'] = shrub_mass(kit, 'lw_shrub', radius=.45, height=.7, lobes=5, seed=19)
    return P


def fill(kit, reg, mix, spacing, seed, placed, scales=(1.1, .95, .8, .65, .5), drift=2.2, within=None):
    """Dense drifts: Poisson points `spacing` apart (inside `within`, the mulched bed, when the registered region also
    takes in the overhang strip); each takes the species whose noise field (with its weight) is highest there, at the
    largest scale that passes the kit clearance rule; points inside a placed plant are skipped."""
    rnd = random.Random(seed); fields = [_PkNoise(seed + 17 * i, 2 * math.pi / drift) for i in range(len(mix))]
    for x, y in pk_scatter(within if within is not None else reg, spacing, margin=PK_CLEAR, seed=seed):
        if any(math.hypot(x - a, y - c) < r * .5 for a, c, r in placed):
            continue
        order = sorted(range(len(mix)), key=lambda i: -(fields[i](x, y) + 1.4 * math.log(mix[i][1])))
        for i in order[:2]:
            p = mix[i][0]
            for s in scales:
                sy = s * rnd.uniform(.9, 1.1); ln = (rnd.uniform(-.05, .05), rnd.uniform(-.05, .05))
                if kit.fits(p, x, y, s, reg, sy=sy, lean=ln):
                    kit.place(p, x, y, PSOIL, rnd.uniform(0, math.tau), s, sy=sy, lean=ln)
                    placed.append((x, y, kit.extent(p, s, sy, s, ln)))
                    break
            else:
                continue
            break


def planting():
    """Front and side beds on mulch (soil top PSOIL), planted with the shared kit as linked instances."""
    global KIT
    b = Batch()
    beds = {
        'A': ([(XSW - .02, YSW - .02, -.83, YF + .02), (XSW - .02, YF + .02, X0 + .02, NU - .68)],
              [(XSW, YSW), (-.87, YSW), (-.87, YF + .02), (X0 + .02, YF + .02), (X0 + .02, NU - .72), (XSW, NU - .72)]),
        'B': ([(.63, YSW - .02, XF - .04, YF + .02), (XB + 2.23, YF + .02, X1 - T + .02, YS + .02)],
              [(.67, YSW), (XF - .04, YSW), (XF - .04, YF + .02), (X1 - T + .02, YF + .02), (X1 - T + .02, YS + .02),
               (XB + 2.23, YS + .02), (XB + 2.23, YF + .02), (.67, YF + .02)]),
        'D': ([(XSW - .02, NU + .68, X0 + .02, Y1 + .13)], [(XSW, NU + .72), (X0 + .02, NU + .72), (X0 + .02, Y1 + .11), (XSW, Y1 + .11)]),
        'E': ([(XSW - .02, Y1 + 2.47, GX0 + .02, Y1 + 4.4)], [(XSW, Y1 + 2.51), (GX0 + .02, Y1 + 2.51), (GX0 + .02, Y1 + 4.38), (XSW, Y1 + 4.38)]),
    }
    for name, (boxes, poly) in beds.items():
        for x0, y0, x1, y1 in boxes:
            b.box('pk_mulch', (x0 + x1) / 2, (y0 + y1) / 2, PSOIL / 2, x1 - x0, y1 - y0, PSOIL)
    b.flush('beds')
    kit = KIT = PlantKit('planting', instancing=INSTANCING); P = protos(kit)
    # The side-street beds have no kerb: the sword ferns arch out over the sidewalk edge and back against the cedar
    # wall, as in the sources, so their registered planting regions take in a 0.3 m overhang strip on the sidewalk
    # and 0.25 m behind the wall face; stems and the scatter stay inside the mulched bed (`real`).
    ext = {'A': [(XSW - .3, YSW - .3), (-.87, YSW - .3), (-.87, YF + .02), (X0 + .25, YF + .02), (X0 + .25, NU - .72), (XSW - .3, NU - .72)],
           'D': [(XSW - .3, NU + .72), (X0 + .25, NU + .72), (X0 + .25, Y1 + .11), (XSW - .3, Y1 + .11)]}
    real = {k: _PkPolygon(poly) for k, (boxes, poly) in beds.items()}
    regs = {k: kit.register_bed(_PkPolygon(ext.get(k, poly))) for k, (boxes, poly) in beds.items()}
    placed = []
    kit.place_in(P['maple'], 3.1, -5.55, PSOIL, .6, 1.0, region=regs['B'], shrink=(1., .9, .8, .7))
    placed.append((3.1, -5.55, .95))
    kit.place_in(P['shrub'], 3.75, -6.75, PSOIL, 1.3, 1.0, region=regs['B'], shrink=(1., .85, .7))
    placed.append((3.75, -6.75, .45))
    front = [(P['fern'], 1.4), (P['fern2'], .8), (P['spiky'], .6), (P['fescue'], .4), (P['golden'], .4), (P['reed'], .3)]
    side = [(P['fern'], 1.2), (P['reed'], .9), (P['fern2'], .7), (P['golden'], .4)]
    right = [(P['fern'], 1.4), (P['fern2'], .8), (P['golden'], .5), (P['fescue'], .4), (P['shrub'], .2)]
    fine = (1.1, .95, .8, .68, .56, .46, .38, .3)
    ferns = [(P['fern'], 1.3), (P['fern2'], .8)]
    big = (1.1, 1.0, .9, .8, .7)
    for k, sp, sd in (('A', .62, 41), ('D', .55, 43), ('B', .7, 45), ('E', .7, 47)):     # first the sword-fern masses
        fill(kit, regs[k], ferns, sp, sd, placed, scales=big, drift=3.0, within=real[k])
    fill(kit, regs['A'], front, .3, 31, placed, scales=fine, within=real['A'])
    fill(kit, regs['B'], right, .32, 33, placed, scales=fine)
    fill(kit, regs['D'], side, .26, 35, placed, scales=fine, within=real['D'])
    fill(kit, regs['E'], side, .36, 37, placed, scales=fine)
    kit.flush()
    bad = kit.audit(detail=True)
    if bad:
        raise RuntimeError(f'planting kit clearance rule: {len(bad)} placements cross a bed edge: {bad[:12]}')


def tree(x, y, r, k, z=.05, role=('tree', 'tree2')):
    """Rounded deciduous tree: trunk, two limbs, a crown of four overlapping smooth masses."""
    H = 2.4 * r + 3.0
    top = (x + .2, y + .1, z + H * .55)
    C.rod('Tree trunk', (x, y, z - .04), top, .14 + .03 * r, 'bark', 'trees', 8)
    for a in (k * 1.3, k * 1.3 + 2.4):
        C.rod('Tree limb', (x, y, z + H * .35), (x + math.cos(a) * r * .5, y + math.sin(a) * r * .5, z + H * .62), .07 + .015 * r, 'bark', 'trees', 6)
    smooth(A.foliage('Tree crown', (top[0], top[1], z + H * .72), (r * .85, r * .85, r * .72), role=role[k % 2], detail=3))
    for j in range(3):
        a = k * .9 + j * math.tau / 3
        smooth(A.foliage('Tree crown mass', (top[0] + math.cos(a) * r * .5, top[1] + math.sin(a) * r * .5, z + H * (.6 + .04 * j)),
                         (r * .62, r * .62, r * .52), role=role[(k + j + 1) % 2], detail=3))


def conifer(x, y, h, r):
    C.rod('Conifer trunk', (x, y, .01), (x, y, h * .4), .16, 'bark', 'trees', 8)
    for i, (f, s) in enumerate(((.3, 1.0), (.52, .78), (.72, .55), (.88, .32))):
        smooth(A.foliage('Conifer tier', (x, y, h * f), (r * s, r * s, h * .2), role='conifer', detail=3))


def trees():
    for k, (x, y, r) in enumerate(((-5.2, 21.5, 3.4), (10.5, 18.5, 2.8), (-20.0, 14.0, 3.6), (-20.0, -12.0, 3.0))):
        tree(x, y, r, k)
    conifer(12.4, 12.2, 13.0, 2.4)
    conifer(9.6, 14.8, 11.0, 2.0)


def car(name, cx, cy, L, W, body, suv=True):
    """Parked car along the curb (front to +y): body, glazed cabin under a roof cap, pillars, wheels, lights."""
    zb, zt = (.34, 1.0) if suv else (.3, .9)
    C.box(name + ' body', (cx, cy, (zb + zt) / 2), (W, L, zt - zb), body, 'cars', 0)
    if suv:
        prof = [(cy - L / 2 + .2, zt - .02), (cy + L / 2 - 1.1, zt - .02), (cy + L / 2 - 1.62, 1.66), (cy - L / 2 + .32, 1.7)]
    else:
        prof = [(cy - L / 2 + .75, zt - .02), (cy + L / 2 - 1.35, zt - .02), (cy + L / 2 - 1.95, 1.42), (cy - L / 2 + 1.25, 1.44)]
    C.prism(name + ' cabin', prof, 'x', cx - W / 2 + .09, cx + W / 2 - .09, 'car_glass', 'cars')
    y0, y1 = prof[3][0] + .02, prof[2][0] - .02
    C.box(name + ' roof', (cx, (y0 + y1) / 2, prof[3][1] + .02), (W - .14, y1 - y0, .07), body, 'cars', 0)
    C.box(name + ' pillar', (cx, (y0 + y1) / 2 + .1, (zt + prof[3][1]) / 2), (W - .16, .1, prof[3][1] - zt + .02), body, 'cars', 0)
    for sy in (-1, 1):
        for sx in (-1, 1):
            C.rod(name + ' wheel', (cx + sx * (W / 2 - .2), cy + sy * (L / 2 - .78), .34), (cx + sx * (W / 2 + .03), cy + sy * (L / 2 - .78), .34),
                  .34, 'tyre', 'cars', 14)
    for sx in (-1, 1):
        C.box(name + ' tail light', (cx + sx * (W / 2 - .2), cy - L / 2 - .005, zt - .15), (.3, .03, .12), 'tail', 'cars', 0)
        C.box(name + ' head light', (cx + sx * (W / 2 - .22), cy + L / 2 + .005, zt - .2), (.3, .03, .1), 'lamp', 'cars', 0)


def pole():
    """Wood utility pole on the side sidewalk: crossarm, insulators, transformer, wires along the street and the service
    drop to the house."""
    px, py = XC + .45, Y1 + 2.6
    C.rod('Utility pole', (px, py, 0.0), (px, py, 11.2), .14, 'pole', 'utility', 10)
    C.beam('Crossarm', (px - 1.2, py, 10.4), (px + 1.2, py, 10.4), .1, .12, 'pole', 'utility')
    for dx in (-1.0, 0.0, 1.0):
        C.rod('Insulator', (px + dx, py, 10.46), (px + dx, py, 10.62), .04, 'white', 'utility', 8)
        C.rod('Wire', (px + dx, py, 10.6), (px + dx, 34.0, 10.6), .012, 'wire', 'utility', 6)          # the corner pole ends the run: wires go north
    C.rod('Transformer', (px + .42, py, 8.2), (px + .42, py, 9.1), .28, 'steel', 'utility', 14)
    C.beam('Transformer bracket', (px, py, 8.8), (px + .3, py, 8.8), .08, .08, 'steel', 'utility')
    C.rod('Telecom wire', (px - .16, py, 8.0), (px - .16, 34.0, 8.0), .015, 'wire', 'utility', 6)
    C.rod('Cross-street wire', (px - 1.0, py, 10.6), (-26.0, py + 1.5, 10.2), .012, 'wire', 'utility', 6)
    C.rod('Service drop', (px + .1, py, 9.0), (X0 + .02, Y1 - .5, 5.8), .012, 'wire', 'utility', 6)


def build():
    site()
    foundations()
    glazed_bay()
    front_band()
    porch()
    south_face()
    west_face()
    niche()
    east_face()
    north_face()
    interior()
    roof()
    garage()
    neighbour()
    planting()
    trees()
    car('Blue SUV', XC - 1.15, 6.3, 4.6, 1.86, 'car_blue', True)
    car('Dark sedan', XC - 1.12, 11.6, 4.8, 1.8, 'car_dark', False)
    pole()
    C.CONTACTS.append(dict(name='Cedar walls and glazed bay on a concrete plinth; hipped roof on the wall plates; garage roof buried in the rear wall',
                           eave_m=EAVE, ridge_m=ZR, box=[X0, X1, YF, Y1]))
    C.CONTACTS.append(dict(name='Corner laneway house with porch steps, side entry steps, planted beds, sidewalks and curbs on both streets'))


LIGHT_RIG = dict(key=(-30, -40, 30), fill=(40, -20, 25), rear=(-15, 30, 25), target=(0, -1.0, 4.0), gain=3.5)
