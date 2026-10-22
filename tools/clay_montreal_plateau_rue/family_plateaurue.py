"""Montreal Plateau residential rue street option, authored from the locked catalogue views of
montreal_plateau_residential_rue / variant_0.

Read from the pixels (the top view governs the plan): the corner of two narrow one-way residential streets in the
Plateau, each lined by continuous rows of three-storey plexes with flat membrane roofs behind cornices. The corner
building is a large brick and grey-limestone plex whose corner and street ends carry teal sheet-metal mansard caps
with gabled dormers; along the east street a row of plexes alternates red brick and grey limestone, with teal
mansard caps over stone bays at the party lines; along the north street the corner building is followed by a grey
limestone plex with an octagonal turret under a slate spire, then plexes in limestone and red brick. Each plex has
a raised ground floor, door pairs and wide windows with coloured frames (blue, green, red), stone sills and lintels,
a gallery balcony on the second floor reached by a black iron exterior stair that runs down the front yard and
curls toward the sidewalk, and a smaller third-floor balcony with an iron railing; bracketed cornices under the
roofline. Small front yards with low iron fences; concrete sidewalks with street trees in square pits; narrow
asphalt roadways with cars parked along the far curbs; plainer rows across both streets are context. The
pedestrians, cafe tables and the dog in the sources are not modelled.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-montreal-plateau-rue'
T = .4                                          # facade wall depth
YD, SW, RW = 2.6, 3.0, 8.0                      # front yard (building line to property line), sidewalk, roadway
SWZ = .15                                       # sidewalk top (150 mm curb)
YZ = .18                                        # yard and lawn top
PL = -YD                                        # property line (back of sidewalk)
CB = -(YD + SW)                                 # curb, block side
CO = -(YD + SW + RW)                            # curb, opposite side
XO = -(2 * YD + 2 * SW + RW)                    # opposite building line (-19.2)
F1, F2, F3 = .75, 4.0, 7.15                     # ground, second and third floor levels
D = 14.0                                        # row depth (facade to rear wall)
XMAX, YMAX, XMIN, YMIN = 78.0, 78.0, -40.0, -40.0
EPS = .002
PALETTE = dict(wall=(.56, .56, .54), stone=(.63, .63, .61), stone2=(.74, .74, .72), joint=(.45, .45, .44),
    brick=(.56, .27, .19), brick2=(.62, .34, .24), mortar=(.66, .58, .52), teal=(.27, .56, .60), slate=(.38, .40, .43),
    hardware=(.06, .06, .07), glass=(.20, .25, .29), trim=(.90, .89, .86), green=(.12, .42, .26), blue=(.12, .32, .62),
    red=(.62, .13, .11), timber=(.45, .30, .17), deck=(.50, .38, .26), roof=(.66, .65, .62), membrane=(.58, .57, .55),
    concrete=(.74, .73, .70), sidejoint=(.60, .59, .56), asphalt=(.27, .27, .28), curb=(.68, .67, .64), yard=(.55, .52, .47),
    soil=(.25, .19, .13), lawn=(.38, .50, .26), planting=(.30, .45, .20), interior=(.80, .76, .70), floor=(.56, .46, .36),
    car=(.66, .67, .69), car2=(.24, .27, .30), car3=(.78, .76, .70), tyre=(.07, .07, .07), dark=(.16, .17, .18),
    context=(.70, .68, .64), context2=(.55, .36, .27), pale=(.88, .88, .86), marking=(.92, .92, .90))

# Row B: the north street front (facade plane x = 0, facing west); row A: the east street front (y = 0, facing south).
# u is measured along each row from the block corner. kind: corner, plex, turret. cap: teal mansard cap at u1.
ROW_B = [
    dict(name='B turret plex', u0=20.0, u1=29.0, mat='stone', frame='green', door='green', door2='red', zc=11.15, turret=True, stair='l'),
    dict(name='B limestone plex blue doors', u0=29.0, u1=37.0, mat='stone', frame='blue', door='blue', door2='red', zc=10.85, stair='l'),
    dict(name='B limestone plex green doors', u0=37.0, u1=45.0, mat='stone', frame='green', door='green', door2='green', zc=11.05, stair='l'),
    dict(name='B brick plex', u0=45.0, u1=53.0, mat='brick', frame='trim', door='red', door2='blue', zc=10.75, stair='l'),
    dict(name='B brick plex north', u0=53.0, u1=61.0, mat='brick', frame='green', door='blue', door2='green', zc=10.95, stair='l'),
    dict(name='B turret plex north', u0=61.0, u1=70.0, mat='stone', frame='trim', door='blue', door2='red', zc=11.25, turret=True, stair='l'),
]
ROW_A = [
    dict(name='A brick plex 1', u0=18.0, u1=26.0, mat='brick', frame='trim', door='blue', door2='red', zc=10.85, stair='r', cap=True),
    dict(name='A limestone plex 2', u0=26.0, u1=34.0, mat='stone', frame='teal', door='green', door2='blue', zc=11.05, stair='r', cap=True),
    dict(name='A brick plex 3', u0=34.0, u1=42.0, mat='brick', frame='trim', door='red', door2='blue', zc=10.95, stair='r', cap=True),
    dict(name='A brick plex 4', u0=42.0, u1=50.0, mat='brick2', frame='teal', door='blue', door2='green', zc=10.75, stair='r', cap=True),
    dict(name='A limestone plex 5', u0=50.0, u1=58.0, mat='stone', frame='trim', door='green', door2='red', zc=11.15, stair='r', cap=True),
    dict(name='A brick plex 6', u0=58.0, u1=66.0, mat='brick', frame='teal', door='red', door2='blue', zc=10.85, stair='r', cap=True),
    dict(name='A brick plex 7', u0=66.0, u1=74.0, mat='brick2', frame='trim', door='blue', door2='red', zc=11.05, stair='r', cap=False),
]
CORNER = dict(ua=18.0, ub=20.0, zc=11.4)        # corner building: 18 m along row A, 20 m along row B


def manifest(version):
    h = 13.6
    cams = G.camera_roster(60.0, 60.0, h, [
        ('facade_close', (-8.5, 33.0, 4.4), (0.0, 33.0, 5.2), 32),
        ('architecture_close', (-6.0, 29.0, 12.0), (0.0, 26.6, 11.4), 30),
        ('glass_close', (-3.4, 34.45, F2 + 1.4), (0.0, 34.45, F2 + 1.4), 35),
        ('iron_stair', (-4.8, 31.0, 3.0), (-1.0, 35.5, 2.2), 26),
        ('balcony_gallery', (-4.6, 36.0, 5.2), (0.0, 39.5, 4.6), 28),
        ('mansard_caps', (24.0, -7.5, 14.5), (26.0, 0.0, 11.8), 30),
        ('corner_building', (-9.0, -9.0, 6.5), (6.0, 6.0, 6.0), 26),
        ('sidewalk_trees', (-8.5, 10.5, 1.7), (-3.5, 30.0, 2.6), 24),
        ('roof_parapets', (30.0, 30.0, 26.0), (10.0, 10.0, 10.5), 30),
        ('rear_yards', (40.0, 40.0, 14.0), (20.0, 20.0, 6.0), 26)])
    for c in cams:
        if c['name'] == 'front':                                               # the locked front: eye level on the north-street sidewalk, looking north along the row
            c.update(location=(-5.3, 28.0, 1.6), target=(2.4, 41.5, 5.0), lens=22, whole=False)
        elif c['name'] == 'front_corner':                                      # the locked oblique: high over the intersection, looking north-east at the corner
            c.update(location=(-17.0, -20.0, 30.0), target=(12.0, 10.0, 3.0), lens=28, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(48.0, -40.0, 44.0), target=(16.0, 14.0, 4.0), lens=28, whole=False)
        elif c['name'] == 'top':                                               # the locked top view: the block corner at the bottom, rotated 45 degrees
            c.update(location=(-1.0, -1.0, 120.0), target=(9.0, 9.0, 0.0), ortho_scale=70.0, whole=False)
        elif c['name'] == 'left_side':                                         # along the north street from the far end
            c.update(location=(-9.5, 84.0, 9.0), target=(0.0, 30.0, 5.0), lens=26, whole=False)
        elif c['name'] == 'right_side':                                        # along the east street from the far end
            c.update(location=(84.0, -9.5, 9.0), target=(30.0, 0.0, 5.0), lens=26, whole=False)
        elif c['name'] == 'rear':                                              # over the block interior from the north-east
            c.update(location=(62.0, 62.0, 32.0), target=(12.0, 12.0, 5.0), lens=28, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(-30.0, 70.0, 30.0), target=(8.0, 24.0, 4.0), lens=28, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='montreal_plateau_residential_rue/variant_0, modelled as a Plateau Mont-Royal street corner',
        measurement_contract=dict(dimensions_m=dict(width=XMAX - XMIN, depth=YMAX - YMIN, height=h),
            observed_storeys=3, storey_programme='street option: two residential streets meeting at a corner; the three-storey plex rows are the street walls they are read with',
            plan=f'{-XO:.1f} m building line to building line on both streets (top view): {YD} m front yards, {SW} m sidewalks, an {RW} m one-way roadway with parking on the far side',
            section_m=dict(front_yard=[0.0, PL], sidewalk=[PL, CB], roadway=[CB, CO], far_sidewalk=[CO, CO - SW], far_yard=[CO - SW, XO], curb_height=SWZ),
            facade='grey limestone and red brick three-storey plexes with coloured door and window frames, iron gallery balconies, curling black iron exterior stairs, bracketed cornices, teal mansard caps and a slate turret spire',
            levels_m=[0.0, SWZ, F1, F2, F3, 10.0, 11.4], inferred='the rows across both streets, the block interior, the rear walls and the plex interiors are context and teaching assumptions'),
        roof_contract=dict(type='flat membrane roofs behind cornices and side parapets; teal sheet-metal mansard caps with dormers; an octagonal slate turret spire', datum_m=10.0, crowns_m=[13.6]),
        identity_contract=dict(owner='Plateau residential rue: continuous rows of limestone and brick plexes with curling black iron exterior stairs, iron balconies, coloured doors, cornices and teal mansard caps over small front yards and tree-lined sidewalks on narrow one-way streets'),
        material_contract=dict(profile='source-palette clay: grey limestone with joints, red brick with mortar courses, black iron, blue, green and red doors and frames, teal sheet metal, slate, pale concrete, dark asphalt', textured_keeper=False),
        programme_contract=dict(storeys=3, ground='ground-floor flats off the yards', upper='second- and third-floor flats reached by the exterior stairs and balconies'),
        street_contract=dict(kind='fixed_native_section', width_m=-XO, axis='two streets meeting at a corner', junction_finish='curb returns at the corner',
                             bands=['plex_row', 'front_yard', 'sidewalk_with_tree_pits', 'one_way_roadway', 'far_curb_parking', 'far_sidewalk', 'far_front_yard', 'context_row']),
        contact_contract=['Asphalt at grade zero', 'Sidewalks on the asphalt with a 150 mm curb', 'Yards and lawns at 180 mm', 'Plex walls from grade', 'Stair feet on the yard paving', 'Trees in sidewalk pits'],
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
# ---- Montreal Plateau residential rue ----

FB = C.Face((0, 0, 0), (0, 1, 0), (1, 0, 0), 'north street row')        # row B: u = y, inward +x
FA = C.Face((0, 0, 0), (1, 0, 0), (0, 1, 0), 'east street row')         # row A: u = x, inward +y
R_RET = 2.5                                                              # curb-return radius


def frustum(b, role, cx, cy, z0, z1, r0, r1, n=8, phase=.5):
    """Upright n-gon frustum added to a Batch (r1 = 0 gives a spire)."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for z, r in ((z0, r0), (z1, max(r1, .001))):
        for i in range(n):
            a = 2 * math.pi * (i + phase) / n
            V.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    F.append(tuple(o + i for i in range(n - 1, -1, -1)))
    F.append(tuple(o + n + i for i in range(n)))
    for i in range(n):
        j = (i + 1) % n
        F.append((o + i, o + j, o + n + j, o + n + i))


def quad(b, role, pts):
    """One flat four-corner face (a picket or a scored joint): two triangles instead of a twelve-triangle box."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V); V.extend(pts); F.append((o, o + 1, o + 2, o + 3))


def picket(b, x, y, z0, z1, tx, ty, w=.024, role='hardware'):
    """Flat bar picket in the plane of its railing (tangent tx, ty)."""
    hx, hy = tx * w / 2, ty * w / 2
    quad(b, role, [(x - hx, y - hy, z0), (x + hx, y + hy, z0), (x + hx, y + hy, z1), (x - hx, y - hy, z1)])


def hexa(b, role, pts):
    """Eight corners (bottom four then top four, both anticlockwise) as one closed block."""
    b._hex(role, pts)


def sweep(name, path, outs, profile, role, module='cornices'):
    """Sweep a closed (out, z) profile along a plan path; each joint is mitred (a 90-degree corner gets the bisector at
    sqrt 2), so a cornice turns a corner as one solid with no overlap and no slot."""
    rings = []
    n = len(path)
    for i, (x, y) in enumerate(path):
        if i == 0:
            mx, my = outs[0]
        elif i == n - 1:
            mx, my = outs[-1]
        else:
            (ax, ay), (bx, by) = outs[i - 1], outs[i]
            k = 1.0 + ax * bx + ay * by
            mx, my = (ax + bx) / k, (ay + by) / k
        rings.append([(x + mx * o, y + my * o, z) for o, z in profile])
    return loft(name, rings, role, module, closed=False)


def cornice_profile(zc):
    """Bed mould, flat soffit, fascia and crown: one closed section (out from the wall face, z)."""
    return [(-.03, zc - .64), (.10, zc - .64), (.10, zc - .50), (.42, zc - .50), (.42, zc - .20), (.50, zc - .13),
            (.50, zc), (-.03, zc)]


def console_profile(zc):
    """Scroll console under the soffit: a rolled foot, a curved shank and a deep head buried in the cornice."""
    return [(-.03, zc - 1.05), (.07, zc - 1.05), (.12, zc - .97), (.14, zc - .86), (.22, zc - .74), (.32, zc - .66),
            (.38, zc - .60), (.38, zc - .47), (-.03, zc - .47)]


def consoles(f, us, zc, role='stone2'):
    """Each console is one extruded solid across its width (no stacked cubes)."""
    prof = console_profile(zc)
    for u in us:
        pts = [f.p(u - .09, -o, z) for o, z in prof] + [f.p(u + .09, -o, z) for o, z in prof]
        n = len(prof)
        fs = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
        C.mesh(f'{f.label} console', pts, fs, role, 'cornices')


def face_cornice(f, name, u0, u1, zc, role='stone2'):
    out = (-f.n[0], -f.n[1])
    sweep(name, [tuple(f.p(u0, 0, 0))[:2], tuple(f.p(u1, 0, 0))[:2]], [out], cornice_profile(zc), role)


def band_runs(a, c, z0, z1, holes):
    """Solid stretches of a horizontal band between a and c that do not cross an opening."""
    cuts = sorted((h['u'] - h['w'] / 2, h['u'] + h['w'] / 2) for h in holes if h['z'] < z1 and h['z'] + h['h'] > z0)
    out, cur = [], a
    for s, e in cuts:
        if e <= cur or s >= c:
            continue
        if s > cur:
            out.append((cur, s))
        cur = max(cur, e)
    if cur < c:
        out.append((cur, c))
    return out


def carrier(f, name, u0, u1, z0, z1, holes, role):
    """Opaque facade carrier assembled from solid runs around its openings (exact clear holes, no boolean)."""
    zs = sorted({z0, z1} | {min(max(h['z'], z0), z1) for h in holes} | {min(max(h['z'] + h['h'], z0), z1) for h in holes})
    vs, fs = [], []
    for za, zb in zip(zs, zs[1:]):
        if zb - za < 1e-4:
            continue
        for a, c in band_runs(u0, u1, za + 1e-5, zb - 1e-5, holes):
            if c - a < 1e-4:
                continue
            o = len(vs)
            vs.extend(f.p(uu, dd, zz) for zz in (za, zb) for uu, dd in ((a, 0.0), (c, 0.0), (c, T), (a, T)))
            fs.extend(tuple(o + i for i in face) for face in C.BOX_FACES)
    obj = C.mesh(name, vs, fs, role, 'envelope')
    obj['rlasm_wall_carrier'] = True
    return obj


def ashlar(f, lo, hi, z0, z1, holes, course=.42, block=1.15):
    """Limestone coursing: recessed bed joints and staggered head joints, batched per elevation."""
    vs, fs = [], []
    n = int((z1 - z0) / course)
    for k in range(1, n + 1):
        z = z0 + k * course
        for a, c in band_runs(lo, hi, z - .01, z + .02, holes):
            o = len(vs); vs.extend([f.p(a, -.002, z), f.p(c, -.002, z), f.p(c, -.002, z + .012), f.p(a, -.002, z + .012)])
            fs.append((o, o + 1, o + 2, o + 3))
        if k == n:
            break
        u = lo + (block / 2 if k % 2 else block)
        while u < hi - .2:
            if not any(h['u'] - h['w'] / 2 - .05 < u < h['u'] + h['w'] / 2 + .05 and h['z'] - .05 < z + course / 2 < h['z'] + h['h'] + .05 for h in holes):
                o = len(vs); vs.extend([f.p(u, -.002, z + .012), f.p(u + .012, -.002, z + .012), f.p(u + .012, -.002, z + course), f.p(u, -.002, z + course)])
                fs.append((o, o + 1, o + 2, o + 3))
            u += block
    if fs:
        C.mesh(f.label + ' limestone joints', vs, fs, 'joint', 'stone joints')


def courses(f, lo, hi, z0, z1, holes, spacing=.3):
    """Mortar courses on brick, in one mesh per elevation."""
    vs, fs = [], []
    z = z0 + spacing
    while z < z1:
        for a, c in band_runs(lo, hi, z - .005, z + .01, holes):
            o = len(vs); vs.extend([f.p(a, -.002, z), f.p(c, -.002, z), f.p(c, -.002, z + .008), f.p(a, -.002, z + .008)])
            fs.append((o, o + 1, o + 2, o + 3))
        z += spacing
    if fs:
        C.mesh(f.label + ' mortar courses', vs, fs, 'mortar', 'brick joints')


def door_pair(m, f, h, role, occupied):
    """Pair of panelled doors with glazed upper panels and a transom, inside one cut."""
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    ins = .2
    for s in (-1, 1):
        m.box('trim', u + s * (w / 2 - .04), ins, z + hh / 2, .08, .1, hh)
    m.box('trim', u, ins, z + hh - .04, w - .16, .1, .08)
    m.box('trim', u, ins, z + hh - .42, w - .16, .1, .07)
    m.box('glass', u, ins + .03, z + hh - .23, w - .18, .009, .3)
    m.box(role, u, ins + .02, z + (hh - .46) / 2, w - .16, .06, hh - .46)
    m.box('trim', u, ins - .01, z + (hh - .46) / 2, .06, .08, hh - .46)                # meeting stiles of the pair
    m.box('glass', u, ins - .015, z + (hh - .46) * .66, w - .5, .009, (hh - .46) * .42)
    m.box('trim', u, ins - .02, z + (hh - .46) * .25, w - .5, .02, .5)
    m.box('hardware', u + .1, ins - .03, z + 1.05, .04, .04, .18)
    register(f, h, ins, 'door', occupied)


def stoop(m, h):
    """Three stone steps up to a raised ground-floor door; the top step runs into the wall below the sill."""
    tops = (F1 - .01, F1 - .2, F1 - .39)
    for i, zt in enumerate(tops):
        d0, d1 = -.32 - .3 * i, (.05 if i == 0 else -.32 - .3 * (i - 1) + .02)
        m.box('stone2', h['u'], (d0 + d1) / 2, (zt + YZ - .02) / 2, h['w'] + .2, d1 - d0, zt - YZ + .02)


def window(m, f, h, frame, lite=False):
    framed(m, f, h, cols=2, rows=1, inset=.16, occupied='flat', frame=frame, lite=lite)
    if not lite:
        m.box(frame, h['u'], .145, h['z'] + h['h'] * .78, h['w'] - .14, .1, .06)            # transom bar


def sill_lintel(m, h, mat, door=False):
    if not door:
        m.box('stone2', h['u'], -.05, h['z'] - .07, h['w'] + .24, .14, .14)
    if mat != 'stone':
        m.box('stone2', h['u'], -.04, h['z'] + h['h'] + .15, h['w'] + .3, .1, .3)
    else:
        m.box('stone2', h['u'], -.035, h['z'] + h['h'] + .14, h['w'] + .2, .08, .28)


def rail(b, pts, z, h=.95, spacing=.14):
    """Iron railing along a polyline at deck level z: top rail, bottom rail and pickets."""
    for (ax, ay), (cx, cy) in zip(pts, pts[1:]):
        L = math.hypot(cx - ax, cy - ay)
        b.beam('hardware', (ax, ay, z + h), (cx, cy, z + h), .05, .045, ext=.025)
        b.beam('hardware', (ax, ay, z + .1), (cx, cy, z + .1), .03, .03, ext=.015)
        n = max(2, int(L / spacing))
        tx, ty = (cx - ax) / L, (cy - ay) / L
        for i in range(n + 1):
            px, py = ax + (cx - ax) * i / n, ay + (cy - ay) * i / n
            picket(b, px, py, z + .085, z + h - .02, tx, ty)


def balcony(b, f, a, c, z, depth, fascia, open_end=None):
    """Gallery balcony: timber deck on a slab with a painted fascia, iron railing round the free sides."""
    lo, hi = min(a, c), max(a, c)
    p = lambda u, d: tuple(f.p(u, d, 0))[:2]
    (x0, y0), (x1, y1) = p(lo, -depth), p(hi, .03)
    b.box('deck', (x0 + x1) / 2, (y0 + y1) / 2, z - .09, abs(x1 - x0), abs(y1 - y0), .18)
    (x0, y0), (x1, y1) = p(lo - .02, -depth - .03), p(hi + .02, -depth + .05)
    b.box(fascia, (x0 + x1) / 2, (y0 + y1) / 2, z - .15, abs(x1 - x0), abs(y1 - y0), .26)
    for u in (lo + .1, hi - .1):                                            # iron brackets under the slab
        b.beam('hardware', f.p(u, .0, z - .9), f.p(u, -depth + .1, z - .2), .05, .05)
    pts = [p(lo + .03, .0), p(lo + .03, -depth + .04), p(hi - .03, -depth + .04), p(hi - .03, .0)]
    if open_end == 'lo':
        pts = pts[1:]
    elif open_end == 'hi':
        pts = pts[:-1]
    rail(b, pts, z)


def ext_stair(b, f, u_top, dirn, z_top, open_side):
    """Black iron exterior stair: a straight open-riser flight alongside the facade from the balcony end, then a
    curl of winders turning toward the sidewalk, ending on the yard at the front fence line."""
    rise_total = z_top - YZ
    n1, n2 = 11, 6
    rise = rise_total / (n1 + n2)
    go = .25
    d_in, d_out = -.3, -1.2
    dm = (d_in + d_out) / 2
    nose_in, nose_out = [], []
    for k in range(1, n1 + 1):
        u = u_top + dirn * (go * (k - .5))
        z = z_top - rise * k
        a, c = f.p(u - dirn * go / 2 - dirn * .01, dm, z - .02), f.p(u + dirn * go / 2 + dirn * .01, dm, z - .02)
        b.beam('hardware', f.p(u, d_in, z - .02), f.p(u, d_out, z - .02), go + .02, .04)
        nose_in.append(f.p(u, d_in, z)); nose_out.append(f.p(u, d_out, z))
    # Curl: centre on the street side of the flight foot; treads swept a quarter turn and a half toward the fence.
    uf = u_top + dirn * go * n1
    ccu, ccd = uf, d_out - .25
    rin, rout = .25, 1.15
    zb = z_top - rise * n1
    ring_o = []
    for i in range(n2):
        a = math.radians(90.0 * (i + .5) / n2)
        uu, dd = math.sin(a) * dirn, math.cos(a)
        z = zb - rise * (i + 1)
        b.beam('hardware', f.p(ccu + uu * rin, ccd + dd * rin, z - .02), f.p(ccu + uu * rout, ccd + dd * rout, z - .02), .32, .04)
        ring_o.append(f.p(ccu + uu * rout, ccd + dd * rout, z))
    top = f.p(u_top, d_in, z_top), f.p(u_top, d_out, z_top)
    for side, start in ((nose_in, top[0]), (nose_out + ring_o, top[1])):
        pts = [start] + side
        for p0, p1 in zip(pts, pts[1:]):
            b.beam('hardware', (p0[0], p0[1], max(p0[2] - .14, YZ + .12)), (p1[0], p1[1], max(p1[2] - .14, YZ + .12)), .045, .2, ext=.02)
            b.beam('hardware', (p0[0], p0[1], p0[2] + .92), (p1[0], p1[1], p1[2] + .92), .05, .045, ext=.02)
        for p, q in zip(pts[1:], pts[:-1]):
            L = math.hypot(p[0] - q[0], p[1] - q[1]) or 1.0
            picket(b, p[0], p[1], p[2], p[2] + .9, (p[0] - q[0]) / L, (p[1] - q[1]) / L)
    pc = f.p(ccu, ccd, 0)
    b.box('hardware', pc[0], pc[1], (YZ + zb + .9) / 2, .09, .09, zb + .9 - YZ)            # newel at the curl's centre
    b.box('hardware', pc[0], pc[1], zb + .95, .15, .15, .1)
    for k in (n1 // 2, n1):                                                           # posts carrying the flight
        q = nose_out[k - 1]
        b.box('hardware', q[0], q[1], (YZ + q[2] - .2) / 2, .07, .07, q[2] - .2 - YZ)


def mansard_cap(b, f, uc, zlo, zhi):
    """Teal sheet-metal mansard cap over a stone bay at a party line: stone plinth, steep four-sided hood and a
    gabled dormer toward the street."""
    zb = zhi + .2
    P = lambda u, d, z: f.p(u, d, z)
    corners = lambda hu, d0, d1, z: [P(uc - hu, d0, z), P(uc + hu, d0, z), P(uc + hu, d1, z), P(uc - hu, d1, z)]
    hexa(b, 'stone2', corners(1.15, -.46, 1.4, zlo - .1) + corners(1.15, -.46, 1.4, zb))
    hexa(b, 'teal', corners(1.05, -.38, 1.3, zb) + corners(.38, .3, .62, zb + 2.05))
    hexa(b, 'teal', corners(.44, -.5, .55, zb) + corners(.44, -.5, .55, zb + 1.15))         # dormer cheeks
    hexa(b, 'glass', corners(.29, -.515, -.45, zb + .2) + corners(.29, -.515, -.45, zb + .98))
    hexa(b, 'trim', corners(.035, -.53, -.47, zb + .2) + corners(.035, -.53, -.47, zb + .98))
    pts = [P(uc - .54, -.56, zb + 1.13), P(uc + .54, -.56, zb + 1.13), P(uc, -.56, zb + 1.68)]
    pts2 = [P(uc - .54, .56, zb + 1.13), P(uc + .54, .56, zb + 1.13), P(uc, .56, zb + 1.68)]
    V, F = b.g.setdefault('teal', ([], []))
    o = len(V); V.extend(pts + pts2)
    F.extend([(o, o + 1, o + 2), (o + 5, o + 4, o + 3), (o, o + 3, o + 4, o + 1), (o + 1, o + 4, o + 5, o + 2), (o + 2, o + 5, o + 3, o)])
    q = P(uc, .46, zb + 2.05)
    b.box('hardware', q[0], q[1], zb + 2.25, .06, .06, .4)


def bay_pier(b, f, uc, zhi):
    """Stone bay pier under a mansard cap, straddling the party line."""
    a, c = f.p(uc - 1.1, -.3, 0), f.p(uc + 1.1, .02, 0)
    b.box('stone', (a[0] + c[0]) / 2, (a[1] + c[1]) / 2, (YZ - .05 + zhi + .1) / 2, abs(c[0] - a[0]), abs(c[1] - a[1]), zhi + .1 - YZ + .05)
    for z in (F2 - .3, F3 - .3):
        a, c = f.p(uc - 1.14, -.36, 0), f.p(uc + 1.14, -.2, 0)
        b.box('stone2', (a[0] + c[0]) / 2, (a[1] + c[1]) / 2, z, abs(c[0] - a[0]), abs(c[1] - a[1]), .22)


def body(b, f, u0, u1, zc, mat, rear_lite=True):
    """Everything behind the facade carrier: side and rear walls up to the parapet, the flats' front rooms (a liner
    1.2 m behind the glass, floors), the bulk and the membrane roof."""
    zr, zp = zc - 1.0, zc - .38
    P = lambda u, d: tuple(f.p(u, d, 0))[:2]
    def blk(role, ua, ub, da, db, za, zb):
        (x0, y0), (x1, y1) = P(ua, da), P(ub, db)
        b.box(role, (x0 + x1) / 2, (y0 + y1) / 2, (za + zb) / 2, abs(x1 - x0), abs(y1 - y0), zb - za)
    blk(mat, u0, u0 + .3, T, D, 0.0, zp)
    blk(mat, u1 - .3, u1, T, D, 0.0, zp)
    blk(mat, u0 + .3, u1 - .3, D - .3, D, 0.0, zp)
    blk('wall', u0 + .3, u1 - .3, 1.2, D - .3, 0.0, zr)
    blk('interior', u0 + .3, u1 - .3, 1.18, 1.205, 0.0, zr)
    for z in (F1, F2, F3):
        blk('floor', u0 + .3, u1 - .3, T, 1.18, z - .22, z)
    blk('membrane', u0 + .3, u1 - .3, T, D - .3, zr, zr + .2)
    for uu, w in (((u0 + u1) / 2 - 1.6, .9), ((u0 + u1) / 2 + 1.8, .6)):           # roof vents and a skylight
        blk('dark' if w > .7 else 'hardware', uu - w / 2, uu + w / 2, D / 2 - .4, D / 2 + .4, zr + .2, zr + .55)
    blk('stone2', u0, u0 + .3, T, D, zp, zp + .08)                                    # parapet copings
    blk('stone2', u1 - .3, u1, T, D, zp, zp + .08)
    blk('stone2', u0 + .3, u1 - .3, D - .3, D, zp, zp + .08)
    if rear_lite:                                                                     # rear windows and doors, proud panels
        for z, hh in ((F1 + .3, 2.0), (F2 + .3, 1.9), (F3 + .3, 1.8)):
            for uu in (u0 + 2.2, u1 - 2.2):
                blk('glass', uu - .6, uu + .6, D, D + .03, z, z + hh)
                blk('trim', uu - .7, uu + .7, D - .02, D + .015, z - .1, z)


def plex(spec, f, row):
    """One three-storey plex: raised ground floor, door pairs and wide windows on three floors, a gallery balcony and
    a curling iron stair, a third-floor balcony, a bracketed cornice; an optional octagonal turret with a slate spire."""
    u0, u1, zc, mat = spec['u0'], spec['u1'], spec['zc'], spec['mat']
    W = u1 - u0
    st = spec.get('stair', 'l')
    e, dirn = (u0, 1) if st == 'l' else (u1, -1)
    lite = row == 'A'
    holes, kinds = [], []
    for lvl, (z, dh, wh) in enumerate(((F1, 2.45, 2.0), (F2, 2.35, 1.95), (F3, 2.25, 1.85))):
        holes.append(hole(f'{spec["name"]} door {lvl}', e + dirn * 2.5, z, 2.0, dh, kind='door')); kinds.append('door')
        wu = e + dirn * (5.0 if spec.get('turret') else 5.45)
        holes.append(hole(f'{spec["name"]} window {lvl}', wu, z + .5, 1.7, wh - .1)); kinds.append('window')
    role = mat
    carrier(f, spec['name'] + ' facade carrier', u0, u1, 0.0, zc - .05, holes, role)
    m = Merge(f)
    for h, k in zip(holes, kinds):
        if k == 'door':
            door_pair(m, f, h, spec['door'] if h['z'] < 1 else spec['door2'], 'flat')
        else:
            window(m, f, h, spec['frame'], lite=lite)
        sill_lintel(m, h, mat, door=k == 'door')
    for h in holes:                                                                  # stoop under each ground-floor door
        if h['z'] < 1 and h.get('kind') == 'door':
            stoop(m, h)
    if mat != 'stone':
        m.box('stone2', (u0 + u1) / 2, -.055, F2 - .3, W, .13, .22)                    # belt course on brick
    m.flush(spec['name'])
    if mat == 'stone':
        ashlar(f, u0 + .01, u1 - .01, YZ, zc - .66, holes)
    else:
        courses(f, u0 + .01, u1 - .01, YZ, zc - .66, holes)
    b = Batch()
    a2, c2 = e + dirn * 1.3, e + dirn * 3.7
    balcony(b, f, a2, c2, F2, 1.2, spec['frame'] if spec['frame'] != 'trim' else 'teal', open_end='hi' if dirn > 0 else 'lo')
    balcony(b, f, a2, c2, F3, .9, spec['frame'] if spec['frame'] != 'trim' else 'teal')
    ext_stair(b, f, c2, dirn, F2, None)
    # cornice: consoles at the ends and over the piers
    face_cornice(f, spec['name'] + ' cornice', u0, u1, zc)
    consoles(f, [u0 + .5, (u0 + u1) / 2, u1 - .5] + ([] if lite else [e + dirn * 1.3, e + dirn * 3.7]), zc)
    if spec.get('turret'):
        tu = u1 - 1.5 if dirn > 0 else u0 + 1.5
        turret(b, f, tu, zc)
    body(b, f, u0, u1, zc, mat)
    b.flush(spec['name'] + ' works')
    C.qa_room_light(spec['name'] + ' rooms', f.p((u0 + u1) / 2, .8, F2 + 1.6), 12, .4)


def turret(b, f, tu, zc):
    """Octagonal limestone turret on a corbel from the second floor, windows on its street facets, a band at the
    cornice and a slate spire with a finial."""
    cx, cy = tuple(f.p(tu, -.3, 0))[:2]
    r = 1.15
    frustum(b, 'stone', cx, cy, F2 - 1.3, F2 - .25, .25, r)
    frustum(b, 'stone', cx, cy, F2 - .25, zc - .34, r, r)
    frustum(b, 'stone2', cx, cy, F2 - .4, F2 - .2, r + .1, r + .1)
    frustum(b, 'stone2', cx, cy, zc - .66, zc - .32, r + .12, r + .12)
    frustum(b, 'stone2', cx, cy, zc - .36, zc + .3, r + .02, r + .02)
    frustum(b, 'slate', cx, cy, zc + .3, zc + 4.2, r + .25, 0.0)
    b.box('hardware', cx, cy, zc + 4.5, .07, .07, .7)
    out = (-f.n[0], -f.n[1]); tang = (f.t[0], f.t[1])
    for i in range(8):
        a = 2 * math.pi * i / 8
        nx, ny = math.cos(a), math.sin(a)
        if nx * out[0] + ny * out[1] < -.1:
            continue                                                                  # facets facing into the wall
        ap = r * math.cos(math.pi / 8)
        px, py = cx + nx * (ap + .01), cy + ny * (ap + .01)
        tx, ty = -ny, nx
        for z0, hh in ((F2 + .45, 1.8), (F3 + .45, 1.7)):
            b.beam('glass', (px - tx * .3, py - ty * .3, z0 + hh / 2), (px + tx * .3, py + ty * .3, z0 + hh / 2), .03, hh)
            b.beam('trim', (px - tx * .36, py - ty * .36, z0 - .05), (px + tx * .36, py + ty * .36, z0 - .05), .08, .1)
            b.beam('trim', (px - tx * .36, py - ty * .36, z0 + hh + .05), (px + tx * .36, py + ty * .36, z0 + hh + .05), .08, .1)


def corner_building():
    """The large corner plex: brick with a grey limestone corner pavilion on the east street and limestone quoins on
    the north street, three floors of windows, a gallery balcony and iron stair at the north end, a mitred cornice
    round the corner, teal mansard caps at the corner and at both street ends."""
    ua, ub, zc = CORNER['ua'], CORNER['ub'], CORNER['zc']
    # North-street face (row B): u = y from 0 to ub
    hb, kb = [], []
    for lvl, z, wh in ((0, F1 + .5, 1.9), (1, F2 + .5, 1.85), (2, F3 + .5, 1.75)):
        for u in (3.6, 6.2, 8.8, 11.4):
            hb.append(hole(f'corner B {lvl} {u}', u, z, 1.3, wh)); kb.append('window')
        hb.append(hole(f'corner B door {lvl}', ub - 2.5, (F1, F2, F3)[lvl], 2.0, (2.45, 2.35, 2.25)[lvl], kind='door')); kb.append('door')
    carrier(FB, 'corner north-street carrier stone', 0.0, 2.4, 0.0, zc - .05, [], 'stone')
    carrier(FB, 'corner north-street carrier brick', 2.4, ub, 0.0, zc - .05, hb, 'brick')
    # East-street face (row A): u = x from T to ua; a limestone pavilion to 5.6 m
    ha, ka = [], []
    for lvl, z, wh in ((0, F1 + .5, 1.9), (1, F2 + .5, 1.85), (2, F3 + .5, 1.75)):
        for u in (2.9, 7.4, 10.0, 12.6, 15.2):
            ha.append(hole(f'corner A {lvl} {u}', u, z, 1.3 if u > 5 else 1.7, wh)); ka.append('window')
    ha.append(hole('corner A door', 7.4, F1, 1.3, 2.45, kind='door'))
    ha = [h for h in ha if not (h['id'] == 'corner A 0 7.4')]
    ka = ['door' if h.get('kind') == 'door' else 'window' for h in ha]
    stone_a = [h for h in ha if h['u'] < 5.6]
    carrier(FA, 'corner east-street carrier stone', T, 5.6, 0.0, zc - .05, stone_a, 'stone')
    carrier(FA, 'corner east-street carrier brick', 5.6, ua, 0.0, zc - .05, [h for h in ha if h['u'] > 5.6], 'brick')
    for f, holes, kinds in ((FB, hb, kb), (FA, ha, ka)):
        m = Merge(f)
        for h, k in zip(holes, kinds):
            if k == 'door':
                if h['w'] > 1.5:
                    door_pair(m, f, h, 'blue', 'flat')
                    if h['z'] < 1:
                        stoop(m, h)
                else:
                    _single_door(m, f, h)
            else:
                window(m, f, h, 'green')
            sill_lintel(m, h, 'stone' if (f is FA and h['u'] < 5.6) else 'brick', door=k == 'door')
        if f is FB:
            for z in (F2 - .3, F3 - .3):
                for a, c in band_runs(2.4, ub, z - .11, z + .11, holes):
                    m.box('stone2', (a + c) / 2, -.06, z, c - a, .12, .22)
            for k in range(int(zc / .55)):                                            # long-and-short quoins at the corner
                z = YZ + k * .55
                if z + .5 > zc - .66:
                    break
                L = 1.0 if k % 2 else .7
                m.box('stone2', (L - .08) / 2, -.035, z + .25, L + .08, .09, .5)
        else:
            for z in (F2 - .3, F3 - .3):
                for a, c in band_runs(5.6, ua, z - .11, z + .11, holes):
                    m.box('stone2', (a + c) / 2, -.06, z, c - a, .12, .22)
        m.flush('corner ' + f.label)
    ashlar(FB, .01, 2.39, YZ, zc - .66, [])
    courses(FB, 2.41, ub - .01, YZ, zc - .66, hb)
    ashlar(FA, T + .01, 5.59, YZ, zc - .66, stone_a)
    courses(FA, 5.61, ua - .01, YZ, zc - .66, [h for h in ha if h['u'] > 5.6])
    # mitred cornice round the corner
    sweep('corner cornice', [(0.0, ub - .002), (0.0, 0.0), (ua - .002, 0.0)], [(-1.0, 0.0), (0.0, -1.0)], cornice_profile(zc), 'stone2')
    consoles(FB, [2.0, 5.0, 7.5, 10.1, 12.7, ub - 1.3, ub - 3.7], zc)
    consoles(FA, [2.0, 5.0, 8.7, 11.3, 13.9], zc)
    b = Batch()
    balcony(b, FB, ub - 1.3, ub - 3.7, F2, 1.2, 'teal', open_end='lo')
    balcony(b, FB, ub - 1.3, ub - 3.7, F3, .9, 'teal')
    ext_stair(b, FB, ub - 3.7, -1, F2, None)
    # body: walls, front rooms and roof over the L of street faces
    zr, zp = zc - 1.0, zc - .38
    b.box('brick', ua - .15, (T + ub) / 2, zp / 2, .3, ub - T, zp)                      # east rear wall (x = ua)
    b.box('brick', (T + ua - .3) / 2, ub - .15, zp / 2, ua - .3 - T, .3, zp)          # north rear wall (y = ub)
    b.box('wall', (1.2 + ua - .3) / 2, (1.2 + ub - .3) / 2, zr / 2, ua - .3 - 1.2, ub - .3 - 1.2, zr)
    b.box('interior', 1.1925, (1.2 + ub - .3) / 2, zr / 2, .025, ub - .3 - 1.2, zr)
    b.box('interior', (1.205 + ua - .3) / 2, 1.1925, zr / 2, ua - .3 - 1.205, .025, zr)
    for z in (F1, F2, F3):
        b.box('floor', (T + 1.18) / 2, (T + ub - .3) / 2, z - .11, 1.18 - T, ub - .3 - T, .22)
        b.box('floor', (1.18 + ua - .3) / 2, (T + 1.18) / 2, z - .11, ua - .3 - 1.18, 1.18 - T, .22)
    b.box('membrane', (T + ua - .3) / 2, (T + ub - .3) / 2, zr + .1, ua - .3 - T, ub - .3 - T, .2)
    b.box('stone2', ua - .15, (T + ub) / 2, zp + .04, .3, ub - T, .08)
    b.box('stone2', (T + ua - .3) / 2, ub - .15, zp + .04, ua - .3 - T, .3, .08)
    for x, y, w in ((7.0, 9.0, 1.1), (12.0, 13.0, .6), (5.0, 15.0, .6)):
        b.box('dark' if w > .7 else 'hardware', x, y, zr + .37, w, w, .35)
    chimney(b, 9.5, 17.0, zr + .2, zr + 1.3, w=.9, d=.6, pots=2, role='brick', pot='hardware', cap='stone2')
    for z, hh in ((F1 + .3, 2.0), (F2 + .3, 1.9), (F3 + .3, 1.8)):                      # rear windows, proud panels
        for y in (16.0, 18.5):
            b.box('glass', ua + .015, y, z + hh / 2, .03, 1.2, hh)
        for x in (15.5,):
            b.box('glass', x, ub + .015, z + hh / 2, 1.2, .03, hh)
    # teal mansard caps: the corner, the east-street end and the north-street end
    corner_cap(b, zc)
    bay_pier(b, FA, ua, max(zc, ROW_A[0]['zc']))
    mansard_cap(b, FA, ua, min(zc, ROW_A[0]['zc']), max(zc, ROW_A[0]['zc']))
    bay_pier(b, FB, ub, max(zc, ROW_B[0]['zc']))
    mansard_cap(b, FB, ub, min(zc, ROW_B[0]['zc']), max(zc, ROW_B[0]['zc']))
    b.flush('corner building works')


def _single_door(m, f, h):
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    m.box('trim', u, .2, z + hh - .04, w - .02, .1, .08)
    for s in (-1, 1):
        m.box('trim', u + s * (w / 2 - .04), .2, z + hh / 2, .08, .1, hh)
    m.box('green', u, .22, z + (hh - .08) / 2, w - .16, .06, hh - .08)
    m.box('glass', u, .185, z + hh * .62, w - .5, .009, hh * .4)
    register(f, h, .2, 'door', 'flat')
    stoop(m, h)


def corner_cap(b, zc):
    """Teal mansard cap over the corner: a square hood with gabled dormers on both street faces."""
    zb = zc + .2
    s0, s1 = -.46, 1.9
    hexa(b, 'stone2', [(s0, s0, zc - .1), (s1, s0, zc - .1), (s1, s1, zc - .1), (s0, s1, zc - .1),
                       (s0, s0, zb), (s1, s0, zb), (s1, s1, zb), (s0, s1, zb)])
    hexa(b, 'teal', [(-.38, -.38, zb), (1.82, -.38, zb), (1.82, 1.82, zb), (-.38, 1.82, zb),
                     (.5, .5, zb + 2.15), (.95, .5, zb + 2.15), (.95, .95, zb + 2.15), (.5, .95, zb + 2.15)])
    b.box('hardware', .72, .72, zb + 2.4, .07, .07, .5)
    for f, uc in ((FA, 1.15), (FB, 1.15)):
        P = lambda u, d, z, f=f: f.p(u, d, z)
        corners = lambda hu, d0, d1, z, f=f: [f.p(uc - hu, d0, z), f.p(uc + hu, d0, z), f.p(uc + hu, d1, z), f.p(uc - hu, d1, z)]
        hexa(b, 'teal', corners(.4, -.5, .5, zb) + corners(.4, -.5, .5, zb + 1.1))
        hexa(b, 'glass', corners(.26, -.515, -.45, zb + .2) + corners(.26, -.515, -.45, zb + .95))
        V, F = b.g.setdefault('teal', ([], []))
        o = len(V)
        V.extend([P(uc - .5, -.56, zb + 1.08), P(uc + .5, -.56, zb + 1.08), P(uc, -.56, zb + 1.6),
                  P(uc - .5, .52, zb + 1.08), P(uc + .5, .52, zb + 1.08), P(uc, .52, zb + 1.6)])
        F.extend([(o, o + 1, o + 2), (o + 5, o + 4, o + 3), (o, o + 3, o + 4, o + 1), (o + 1, o + 4, o + 5, o + 2), (o + 2, o + 5, o + 3, o)])


def ground():
    """Asphalt, four corner blocks of sidewalk (curb returns at the intersection), front yards and lawns."""
    C.prism('Street asphalt', [(XMIN, YMIN), (XMAX, YMIN), (XMAX, YMAX), (XMIN, YMAX)], 'z', 0.0, .02, 'asphalt', 'street')
    for bx, by, sx, sy in ((0.0, 0.0, 1, 1), (XO, 0.0, -1, 1), (0.0, XO, 1, -1), (XO, XO, -1, -1)):
        pm = (XMAX - bx) if sx > 0 else (bx - XMIN)
        qm = (YMAX - by) if sy > 0 else (by - YMIN)
        L = lambda pts: [(bx + sx * p, by + sy * q) for p, q in pts]
        c = YD + SW
        arc = [(-c + R_RET - R_RET * math.cos(math.radians(a)), -c + R_RET - R_RET * math.sin(math.radians(a))) for a in range(0, 91, 10)]
        walk = [(-c, qm)] + arc[::1] + [(pm, -c), (pm, -YD), (-YD, -YD), (-YD, qm)]
        walk = [(-c, qm), (-c, -c + R_RET)] + [(-c + R_RET - R_RET * math.cos(math.radians(a)), -c + R_RET - R_RET * math.sin(math.radians(a))) for a in range(10, 81, 10)] + \
               [(-c + R_RET, -c), (pm, -c), (pm, -YD), (-YD, -YD), (-YD, qm)]
        C.prism('Sidewalk', L(walk), 'z', .005, SWZ, 'concrete', 'sidewalks')
        C.prism('Front yards', L([(-YD, qm), (-YD, -YD), (pm, -YD), (pm, .05), (.05, .05), (.05, qm)]), 'z', .005, YZ, 'yard', 'yards')
        C.prism('Block lawn', L([(.05, .05), (pm, .05), (pm, qm), (.05, qm)]), 'z', .005, YZ - .01, 'lawn', 'yards')


def sidewalk_details():
    """Scored joints, tree pits with young street trees, front-yard fences and planting."""
    b = Batch()
    for bx, by, sx, sy in ((0.0, 0.0, 1, 1), (XO, 0.0, -1, 1), (0.0, XO, 1, -1), (XO, XO, -1, -1)):
        pm = (XMAX - bx) if sx > 0 else (bx - XMIN)
        qm = (YMAX - by) if sy > 0 else (by - YMIN)
        W = lambda p, q: (bx + sx * p, by + sy * q)
        for along, length in (('q', qm), ('p', pm)):                                  # scored joints every 1.5 m
            t = 1.5
            while t < length - .5:
                if along == 'q':
                    (x0, y0), (x1, y1) = W(-YD - SW + .05, t), W(-YD - .05, t + .012)
                else:
                    (x0, y0), (x1, y1) = W(t, -YD - SW + .05), W(t + .012, -YD - .05)
                z = SWZ + .002
                quad(b, 'sidejoint', [(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)])
                t += 1.5
    b.flush('sidewalk joints')
    trees = [(-4.4, 24.0), (-4.4, 43.0), (-4.4, 58.0), (24.0, -4.4), (40.0, -4.4), (56.0, -4.4),
             (XO + 4.4, 12.0), (XO + 4.4, 36.0), (XO + 4.4, 60.0), (16.0, XO + 4.4), (44.0, XO + 4.4), (8.0, -4.4), (-4.4, 8.0)]
    for x, y in trees:
        b.box('soil', x, y, (SWZ + .012) / 2 + .002, 1.3, 1.3, SWZ + .01)
        street_tree2(x, y)
    b.flush('tree pits')
    # Front fences along the property line of the two plex rows, gapped at the stair feet and the ground-floor stoops.
    fb = Batch()
    for f, row, start in ((FB, ROW_B, CORNER['ub']), (FA, ROW_A, CORNER['ua'])):
        gaps = []
        for spec in row:
            e, dirn = (spec['u0'], 1) if spec.get('stair', 'l') == 'l' else (spec['u1'], -1)
            gaps.append(sorted((e + dirn * (3.7 + .25 * 11 - .6), e + dirn * (3.7 + .25 * 11 + 1.5))))
            gaps.append(sorted((e + dirn * 1.4, e + dirn * 3.6)))
        if f is FB:
            gaps.append(sorted((CORNER['ub'] - 3.7 - .25 * 11 - 1.5, CORNER['ub'] - 3.7 - .25 * 11 + .6)))
            gaps.append((CORNER['ub'] - 3.6, CORNER['ub'] - 1.4))
        else:
            gaps.append((6.5, 8.3))
        u = 2.0
        end = row[-1]['u1']
        segs = []
        for g0, g1 in sorted(tuple(g) for g in gaps):
            if g0 > u:
                segs.append((u, g0))
            u = max(u, g1)
        if u < end:
            segs.append((u, end))
        for a, c in segs:
            pa, pc = f.p(a, PL + .12, 0), f.p(c, PL + .12, 0)
            fence(fb, pa[:2], pc[:2], spacing=.2 if f is FB else 1.6)
    fb.flush('front fences')
    for f, row in ((FB, ROW_B), (FA, ROW_A)):                                          # shrubs in a few yards
        for spec in row[::2]:
            e, dirn = (spec['u0'], 1) if spec.get('stair', 'l') == 'l' else (spec['u1'], -1)
            for k, du in enumerate((6.3, 7.1)):
                p = f.p(e + dirn * du, -1.9 + .5 * k, 0)
                shrub2(p[0], p[1])


def fence(b, a, c, height=.95, spacing=.2):
    (ax, ay), (cx, cy) = a, c
    L = math.hypot(cx - ax, cy - ay)
    b.beam('stone2', (ax, ay, YZ + .06), (cx, cy, YZ + .06), .2, .16)
    for z in (YZ + .28, YZ + height - .03):
        b.beam('hardware', (ax, ay, z), (cx, cy, z), .035, .035)
    n = max(2, int(L / spacing))
    tx, ty = (cx - ax) / L, (cy - ay) / L
    for i in range(n + 1):
        px, py = ax + (cx - ax) * i / n, ay + (cy - ay) * i / n
        if i in (0, n) or (spacing > 1.0):
            b.box('hardware', px, py, (YZ + .14 + YZ + height + .08) / 2, .06, .06, height - .06)
        else:
            picket(b, px, py, YZ + .13, YZ + height + .02, tx, ty)


def smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def street_tree2(x, y, height=8.5, spread=2.4):
    """Young street tree: a trunk, three limbs and a rounded crown of smooth leaf masses."""
    z = SWZ
    C.rod('Street tree trunk', (x, y, z), (x, y, z + height * .5), .14, 'timber', 'street planting', 8)
    blobs = [(0, 0, .80, 1.0), (-.45, -.2, .66, .78), (.45, -.1, .68, .78), (.05, .48, .64, .74), (.05, -.3, .93, .62)]
    for i, (dx, dy, hz, s) in enumerate(blobs[1:4]):
        tip = (x + dx * spread * .8, y + dy * spread * .8, z + height * hz)
        C.rod('Street tree limb', (x, y, z + height * .45), tip, .06, 'timber', 'street planting', 6)
    for dx, dy, hz, s in blobs:
        smooth(A.foliage('Street tree crown', (x + dx * spread, y + dy * spread, z + height * hz), (1.0 * spread * s, 1.0 * spread * s, .82 * spread * s), detail=2))


def shrub2(x, y):
    for dx, dy, s in ((0, 0, .5), (.35, .1, .38), (-.3, .15, .36)):
        smooth(A.foliage('Yard shrub', (x + dx, y + dy, YZ + s * .8), (s, s, s * .9), detail=1))


def car(b, x, y, ux, uy, role):
    vx, vy = -uy, ux
    b.beam(role, (x - ux * 2.2, y - uy * 2.2, .62), (x + ux * 2.2, y + uy * 2.2, .62), 1.76, .6)
    b.beam('dark', (x - ux * 1.2, y - uy * 1.2, 1.12), (x + ux * .95, y + uy * .95, 1.12), 1.58, .46)
    b.beam(role, (x - ux * 1.15, y - uy * 1.15, 1.37), (x + ux * .9, y + uy * .9, 1.37), 1.5, .06)
    for s in (-1.4, 1.4):
        for t in (-.79, .79):
            cx, cy = x + ux * s + vx * t, y + uy * s + vy * t
            b.beam('tyre', (cx - vx * .13, cy - vy * .13, .34), (cx + vx * .13, cy + vy * .13, .34), .62, .62)


def cars():
    b = Batch()
    roles = ['car', 'car2', 'car3', 'car2', 'car', 'car3', 'car', 'car2']
    xs = CO + 1.1
    for i, y in enumerate((6.0, 16.5, 31.0, 48.0, 62.0)):
        car(b, xs, y, 0.0, 1.0, roles[i])
    for i, x in enumerate((7.0, 21.0, 37.5, 54.0, 69.0)):
        car(b, x, xs, 1.0, 0.0, roles[i + 3])
    b.flush('parked cars')


def context_row(f, u0, u1, zcs, mats, label):
    """Plainer plexes across the streets: bulk, proud windows and doors, a cornice band, balconies, an occasional cap."""
    b = Batch()
    n = len(zcs)
    w = (u1 - u0) / n
    for i in range(n):
        a, c = u0 + i * w, u0 + (i + 1) * w
        zc, mat = zcs[i], mats[i % len(mats)]
        P = lambda u, d: tuple(f.p(u, d, 0))[:2]
        def blk(role, ua, ub, da, db, za, zb):
            (x0, y0), (x1, y1) = P(ua, da), P(ub, db)
            b.box(role, (x0 + x1) / 2, (y0 + y1) / 2, (za + zb) / 2, abs(x1 - x0), abs(y1 - y0), zb - za)
        blk(mat, a, c, 0.0, D, 0.0, zc - .05)
        blk('membrane', a + .3, c - .3, .3, D - .3, zc - .05, zc - .02)
        blk('stone2', a, c, -.45, .02, zc - .45, zc)
        for z, hh in ((F1 + .45, 1.9), (F2 + .45, 1.85), (F3 + .45, 1.75)):
            for uu in (a + 2.3, a + 3.6, c - 2.0):
                if uu < c - 1.2 and uu > a + 1.2:
                    blk('glass', uu - .55 if uu != a + 3.6 else uu - .45, uu + .55 if uu != a + 3.6 else uu + .45, -.03, .01, z, z + hh)
                    blk('trim', uu - .65, uu + .65, -.06, .01, z - .12, z)
        blk('deck', a + 1.2, a + 4.4, -1.1, .02, F2 - .18, F2)
        blk('hardware', a + 1.2, a + 4.4, -1.12, -1.07, F2, F2 + .95)
        blk('deck', a + 1.2, a + 4.4, -.85, .02, F3 - .18, F3)
        blk('hardware', a + 1.2, a + 4.4, -.87, -.82, F3, F3 + .95)
        if i % 2 == 1 and i < n - 1:
            blk('teal', c - 1.0, c + 1.0, -.3, 1.2, zc, zc + 1.6)
    b.flush(label)


def context():
    FNW = C.Face((XO, 0, 0), (0, 1, 0), (-1, 0, 0), 'context north-west')          # facing east across the north street
    FSE = C.Face((0, XO, 0), (1, 0, 0), (0, -1, 0), 'context south-east')          # facing north across the east street
    context_row(FNW, 0.0, 72.0, [10.6, 11.0, 10.4, 10.9, 11.2, 10.5, 10.8, 11.1, 10.6], ['brick', 'stone', 'context2', 'brick2'], 'context north-west row')
    context_row(FSE, 0.0, 72.0, [10.9, 10.5, 11.1, 10.7, 10.4, 11.0, 10.6, 11.2, 10.8], ['stone', 'brick', 'brick2', 'context2'], 'context south-east row')
    FNWs = C.Face((XO, 0, 0), (-1, 0, 0), (0, 1, 0), 'context north-west south face')
    FSEw = C.Face((0, XO, 0), (0, -1, 0), (1, 0, 0), 'context south-east west face')
    context_row(FNWs, D, D + 6.0, [10.7], ['brick2'], 'context north-west corner')
    context_row(FSEw, D, D + 6.0, [11.0], ['brick'], 'context south-east corner')
    FSW1 = C.Face((XO, XO, 0), (0, -1, 0), (-1, 0, 0), 'context south-west east face')
    FSW2 = C.Face((XO, XO, 0), (-1, 0, 0), (0, -1, 0), 'context south-west north face')
    context_row(FSW1, D, D + 6.0, [10.8], ['stone'], 'context south-west east')
    context_row(FSW2, 0.0, D + 6.0, [10.9, 10.5], ['brick2', 'brick'], 'context south-west north')
    # rear: block-interior trees and lot-line fences
    for x, y in ((24.0, 24.0), (36.0, 22.0), (22.0, 40.0), (50.0, 26.0), (28.0, 56.0)):
        street_tree2(x, y, height=9.5, spread=2.8)


def build():
    ground()
    sidewalk_details()
    cars()
    corner_building()
    for s in ROW_B:
        plex(s, FB, 'B')
    for s in ROW_A:
        plex(s, FA, 'A')
    b = Batch()
    for s, nxt in zip(ROW_A, ROW_A[1:] + [None]):
        if s.get('cap'):
            zl, zr_ = s['zc'], (nxt['zc'] if nxt else s['zc'])
            bay_pier(b, FA, s['u1'], max(zl, zr_))
            mansard_cap(b, FA, s['u1'], min(zl, zr_), max(zl, zr_))
    b.flush('east street caps')
    context()
    C.CONTACTS.append(dict(name='Plateau street corner: plex rows with front yards and iron stairs, sidewalks with tree pits, one-way roadways, curb returns', box=[XMIN, XMAX, YMIN, YMAX]))


LIGHT_RIG = dict(key=(-50, -40, 60), fill=(40, -60, 35), rear=(30, 60, 45), target=(10.0, 10.0, 4.0), gain=5.0)
