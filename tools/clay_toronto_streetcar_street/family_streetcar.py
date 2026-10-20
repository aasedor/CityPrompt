"""Toronto streetcar main street street option, authored from the locked catalogue views of
toronto_streetcar_street / variant_0.

Read from the pixels (the top view governs the plan): a straight north-south four-lane main street with a cross street
at its south end. The section, building line to building line about 25 m: a 3.9 m west sidewalk and a 5.3 m east
sidewalk of pale scored concrete with red brick-paver furnishing strips at the curb, young street trees in pits and tall
grey steel poles; a wide curb lane each way with white lane dashes; two centre track lanes on a pale concrete track slab
with transverse joints, carrying twin embedded grooved-rail streetcar tracks (1495 mm TTC gauge) either side of a yellow
centre line. Overhead: span wires strung pole to pole across the street carry two contact wires, one over each track,
and the same poles carry long-armed cobra-head street lights. A red-and-white articulated low-floor streetcar (Flexity
type) runs on the east (northbound) track mid-block with its pantograph raised to the wire. At the cross street:
corner curb returns, crosswalk lines and a stop bar, a yellow centre line on the cross street. The street wall: on the
west a three-storey red-brick Romanesque corner block with round-arched upper windows and a central gabled parapet, a
plainer three-storey brick block, and a seven-storey brick condominium wing with balconies in front of a ten-storey
glass slab with a green roof; on the east a three-storey red-brick corner block with storefronts and roof skylights, a
second three-storey brick block, a low two-storey block, and a six-storey charcoal condominium with glass-railed
balconies and a green roof. Storefront glazing at grade throughout. Blocks beyond the back lanes and south of the cross
street are context only.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-toronto-streetcar-street'
RH = 8.1                                        # half road width, curb face to centre line (16.2 m curb to curb)
XWB, XEB = -12.0, 13.4                          # west and east building lines (3.9 m and 5.3 m sidewalks)
TC = 1.85                                       # track centre offset from the centre line (3.7 m track centres)
GAUGE = 1.495                                   # TTC broad gauge between rail inner faces
SLAB = 3.65                                     # concrete track slab half width
LANE_X = 3.9                                    # white lane line between the curb lane and the track lane
YN0 = 3.7                                       # south faces of the corner blocks on the cross street (3.7 m sidewalk)
YX0, YX1 = -10.0, 0.0                           # cross street curbs (south, north)
Y1, YS_END = 80.0, -60.0                        # north and south ends of the modelled main street
XW_END, XE_END = -62.0, 56.0                    # west and east ends of the modelled cross street
R_RET = 3.0                                     # corner curb-return radius
SWZ = .15                                       # 150 mm curb
WIRE_Z = 5.6                                    # contact wire height
T = .4
EPS = .002
PALETTE = dict(wall=(.56, .27, .18), brick=(.56, .27, .18), brick2=(.60, .31, .21), brick3=(.50, .25, .19), tan=(.70, .52, .38),
    joint=(.70, .64, .56), stone=(.80, .74, .62), cream=(.86, .81, .68), white=(.93, .92, .88), trim=(.93, .92, .88),
    frame=(.12, .13, .14), dark=(.15, .16, .17), sign=(.18, .20, .21), charcoal=(.27, .28, .29), panel=(.40, .41, .42),
    glass=(.20, .25, .27), curtain=(.36, .44, .48), railglass=(.66, .74, .76), interior=(.82, .78, .72), floor=(.56, .46, .36), roof=(.66, .64, .60),
    membrane=(.76, .76, .74), concrete=(.76, .75, .72), slab=(.70, .69, .66), sidejoint=(.60, .59, .56), paver=(.55, .30, .23),
    asphalt=(.25, .25, .26), lane=(.33, .33, .34), marking=(.94, .94, .92), yellow=(.86, .66, .18), rail=(.45, .44, .42),
    groove=(.10, .10, .10), steel=(.55, .56, .57), hardware=(.08, .08, .09), wire=(.10, .10, .11), lamp=(.88, .88, .84),
    timber=(.40, .30, .21), tree=(.32, .46, .20), planting=(.30, .44, .20), soil=(.24, .18, .12), green=(.42, .50, .28),
    car_red=(.72, .08, .08), car_white=(.92, .92, .90), car_roof=(.62, .63, .64), car_glass=(.07, .08, .09), amber=(.95, .62, .12),
    rubber=(.06, .06, .06), context=(.80, .78, .72), neighbour=(.62, .40, .30), pale=(.88, .88, .86), ttc=(.80, .10, .12))


def manifest(version):
    h = 14.0
    cams = G.camera_roster(XE_END - XW_END, Y1 - YS_END, h, [
        ('streetcar_nose', (4.6, 63.5, 2.3), (1.85, 56.0, 1.8), 30),
        ('pantograph_wire', (7.0, 33.0, 7.6), (1.85, 40.4, 5.0), 32),
        ('track_slab', (-.9, 15.0, 1.5), (-1.85, 26.0, 0.0), 30),
        ('span_wire_pole', (11.8, 28.5, 1.7), (7.0, 33.5, 6.6), 22),
        ('intersection_crossing', (-6.5, 26.0, 7.0), (0.0, 0.0, 0.0), 28),
        ('corner_storefront', (6.2, 1.8, 1.8), (13.4, 10.0, 2.8), 30),
        ('victorian_arches', (-5.0, 21.0, 3.0), (-12.0, 14.0, 9.6), 32),
        ('condo_balconies', (4.6, 49.0, 2.0), (13.4, 64.0, 11.0), 30),
        ('east_sidewalk', (11.6, 46.0, 1.7), (10.6, 26.0, 1.4), 30),
        ('roof_skylights', (20.0, -8.0, 24.0), (28.0, 12.0, 12.0), 32)])
    for c in cams:
        if c['name'] == 'front':                                               # the locked front: eye level in the west curb lane, looking south at the streetcar
            c.update(location=(-5.4, 68.5, 1.65), target=(1.0, 25.0, 4.6), lens=22, whole=False)
        elif c['name'] == 'front_corner':                                      # the locked oblique: high over the south-west, looking up the street
            c.update(location=(34.0, -38.0, 50.0), target=(-10.0, 33.0, 5.0), lens=30, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(-56.0, -36.0, 54.0), target=(0.0, 32.0, 2.0), lens=28, whole=False)
        elif c['name'] == 'top':                                               # the locked top view: north up, the cross street at the foot
            c.update(location=(-4.2, 34.1, 160.0), target=(-4.2, 34.101, 0.0), ortho_scale=116.0, whole=False)
        elif c['name'] == 'left_side':                                         # along the cross street from the west
            c.update(location=(-58.0, -6.0, 9.0), target=(0.0, 18.0, 5.0), lens=26, whole=False)
        elif c['name'] == 'right_side':                                        # along the cross street from the east
            c.update(location=(56.0, -7.0, 11.0), target=(0.0, 22.0, 4.0), lens=26, whole=False)
        elif c['name'] == 'rear':                                              # from the north, raised, looking down the street
            c.update(location=(2.0, 122.0, 34.0), target=(0.0, 40.0, 4.0), lens=28, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(62.0, 112.0, 46.0), target=(0.0, 36.0, 2.0), lens=28, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='toronto_streetcar_street/variant_0, modelled as a Toronto mixed-traffic streetcar main street',
        measurement_contract=dict(dimensions_m=dict(width=XE_END - XW_END, depth=Y1 - YS_END, height=34.7),
            observed_storeys=3, storey_programme='street option: a streetcar main-street section; the storefront blocks and condominiums are the street wall it is read with',
            plan=f'{XEB - XWB:.1f} m building line to building line, {2 * RH:.1f} m curb to curb (top view), an 80 m run north of a cross street and 50 m of context south of it',
            section_m=dict(west_sidewalk=[XWB, -RH], west_curb_lane=[-RH, -LANE_X], west_track_lane=[-LANE_X, 0.0], east_track_lane=[0.0, LANE_X],
                           east_curb_lane=[LANE_X, RH], east_sidewalk=[RH, XEB], track_centres=[-TC, TC], track_gauge=GAUGE,
                           track_slab=[-SLAB, SLAB], contact_wire_height=WIRE_Z, curb_height=SWZ, cross_street=[YX0, YX1]),
            facade='pale scored concrete sidewalks with red brick-paver furnishing strips, grey steel poles with span wires, contact wires and cobra-head lights, a concrete track slab with twin grooved-rail tracks, white lane dashes and a yellow centre line; a red-and-white articulated streetcar; red-brick storefront blocks with stone and white trim, brick and charcoal condominiums with glass balconies',
            levels_m=[0.0, SWZ, 4.62, 8.2, 11.8, WIRE_Z], inferred='the block interiors, rear walls, the back lanes and the context south of the cross street are teaching assumptions'),
        roof_contract=dict(type='flat membrane and gravel roofs inside brick parapets with copings; green roofs with penthouses on the condominiums', datum_m=12.0, crowns_m=[12.6, 23.0, 31.5, 34.7]),
        identity_contract=dict(owner='Toronto streetcar main street: twin embedded streetcar tracks in the centre lanes under overhead contact wires on span wires, a red-and-white articulated streetcar, wide curb lanes, sidewalks with brick furnishing strips, and a mixed street wall of Victorian red-brick storefront blocks and newer condominiums'),
        material_contract=dict(profile='source-palette clay: red-brick, stone and white trim, charcoal cladding, glass, pale concrete, brick pavers, dark asphalt with white and yellow markings, grey steel poles and dark wires, a red-and-white streetcar', textured_keeper=False),
        programme_contract=dict(storeys=3, ground='shops and cafes on the sidewalk', upper='offices and flats; condominium flats in the mid-rises'),
        street_contract=dict(kind='fixed_native_section', width_m=XEB - XWB, axis='y', junction_finish='crosswalk lines and stop bars at the cross street',
                             bands=['west_storefronts', 'west_sidewalk', 'furnishing_strip', 'curb_lane', 'track_lane', 'centre_line', 'track_lane', 'curb_lane', 'furnishing_strip', 'east_sidewalk', 'east_storefronts'],
                             transit=dict(mode='streetcar in mixed traffic', tracks=2, gauge_m=GAUGE, overhead='span-wire contact system', vehicle='articulated low-floor streetcar on the northbound track')),
        contact_contract=['Asphalt at grade zero', 'Sidewalks on the asphalt with a 150 mm curb', 'Track slab flush with the road, rails proud by about 1 cm',
                          'Streetcar wheels on the rails, pantograph at the contact wire', 'Building walls from grade with the sidewalk running under them', 'Poles and trees in the furnishing strip'],
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
# ---- Toronto streetcar main street ----

import random

YS0 = YX0 - 3.7                                 # north faces of the blocks south of the cross street (3.7 m sidewalk)
XP = RH + .55                                   # pole line in the furnishing strips
POLES = (-41.5, -16.5, 8.5, 33.5, 58.5)         # span-wire poles, paired across the street
SPAN_Z, SAG = 7.0, .35                          # span wire height at the poles and its sag at mid-street
CAR_N = 56.0                                    # north (leading) end of the streetcar on the east track
MODS = (6.3, 5.4, 6.2, 5.4, 6.3)                # module lengths from the north
GAP = .3                                        # articulation (bellows) gap
CAR_W = 2.54


def arc(cx, cy, r, a0, a1, n=8):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def quadrant(sx, sy):
    """One corner quadrant of sidewalk in plan, curb face to the model edge, with its curb return (mirrored by sx, sy)."""
    xe = XE_END if sx > 0 else -XW_END
    ye = Y1 if sy > 0 else -YS_END
    ry = YX1 if sy > 0 else -YX0
    pts = [(xe, ry), (xe, ye), (RH, ye), (RH, ry + R_RET)] + arc(RH + R_RET, ry + R_RET, R_RET, 180.0, 270.0)[1:-1] + [(RH + R_RET, ry)]
    pts = [(sx * x, sy * y) for x, y in pts]
    return pts if sx * sy > 0 else pts[::-1]


def ground():
    """Asphalt for both streets, concrete sidewalk quadrants with curb returns, and the streetcar track slab."""
    C.prism('Street asphalt', [(-RH - .4, YS_END), (RH + .4, YS_END), (RH + .4, YX0 - .4), (XE_END, YX0 - .4), (XE_END, YX1 + .4),
                               (RH + .4, YX1 + .4), (RH + .4, Y1), (-RH - .4, Y1), (-RH - .4, YX1 + .4), (XW_END, YX1 + .4),
                               (XW_END, YX0 - .4), (-RH - .4, YX0 - .4)], 'z', 0.0, .02, 'asphalt', 'street')
    for sx in (1, -1):
        for sy in (1, -1):
            C.prism(f'Sidewalk {"NE" if sx > 0 and sy > 0 else "NW" if sy > 0 else "SE" if sx > 0 else "SW"}', quadrant(sx, sy), 'z', .005, SWZ, 'concrete', 'sidewalks')
    C.box('Track slab', (0.0, (YS_END + Y1) / 2, .0155), (2 * SLAB, Y1 - YS_END, .021), 'slab', 'track', 0)


def track_and_markings():
    """Twin grooved-rail tracks proud of the slab, slab joints, white lane dashes, yellow centre line, crossings, stop bars."""
    b = Batch()
    for tc in (-TC, TC):
        for s in (-1, 1):
            b.box('rail', tc + s * (GAUGE / 2 + .036), (YS_END + Y1) / 2, .027, .072, Y1 - YS_END, .018)
            b.box('groove', tc + s * (GAUGE / 2 - .022), (YS_END + Y1) / 2, .02525, .044, Y1 - YS_END, .0065)
    y = YS_END + 3.0
    while y < Y1 - 1.0:
        b.box('sidejoint', 0.0, y, .0275, 2 * SLAB - .1, .03, .005)                          # transverse slab joints
        y += 6.0
    zm = .0235
    b.box('yellow', 0.0, (YX1 + 5.6 + Y1) / 2, .0265, .12, Y1 - YX1 - 5.6, .009)            # single yellow centre line between the tracks
    b.box('yellow', 0.0, (YS_END + YX0 - 5.6) / 2, .0265, .12, YX0 - 5.6 - YS_END, .009)
    for sx in (-1, 1):                                                                       # white lane dashes, 3 m every 9 m
        for y0, y1 in ((YX1 + 7.0, Y1 - 1.0), (YS_END + 1.0, YX0 - 7.0)):
            y = y0
            while y + 3.0 <= y1:
                b.box('marking', sx * LANE_X, y + 1.5, zm, .12, 3.0, .009)
                y += 9.0
    for ya, yb in ((YX1 + .6, YX1 + 3.4), (YX0 - 3.4, YX0 - .6)):                           # Toronto two-line crossings over the main street
        for yy in (ya, yb):
            b.box('marking', 0.0, yy, .0275, 2 * RH - .1, .3, .009)
    b.box('marking', -RH / 2, YX1 + 4.9, .0275, RH - .2, .45, .009)                         # stop bars
    b.box('marking', RH / 2, YX0 - 4.9, .0275, RH - .2, .45, .009)
    for sx in (-1, 1):                                                                       # crossings over the cross street
        for xx in (RH + R_RET + .4, RH + R_RET + 3.4):
            b.box('marking', sx * xx, (YX0 + YX1) / 2, zm, .3, YX1 - YX0 - .1, .009)
        b.box('marking', sx * (RH + R_RET + 4.9), (YX0 + YX1) / 2 + sx * 2.5, zm, .45, (YX1 - YX0) / 2 - .2, .009)
        x0, x1 = (RH + R_RET + 6.0, XE_END - .2) if sx > 0 else (XW_END + .2, -(RH + R_RET + 6.0))
        b.box('yellow', (x0 + x1) / 2, (YX0 + YX1) / 2, zm, x1 - x0, .12, .009)
    b.flush('track and markings')


def tree_pit(b, x, y):
    b.box('soil', x, y, SWZ + .0045, 1.2, 1.2, .012)
    street_tree(x, y, z=SWZ + .008, height=4.8, spread=1.0)


def furniture():
    """Brick-paver furnishing strips, scored sidewalk joints, tree pits and young trees, bins, the TTC stop pole."""
    b = Batch()
    for sx, x_in, w in ((-1, XWB, 1.15), (1, XEB, 1.5)):
        xc = sx * (RH + .1 + w / 2)
        for y0, y1 in ((YX1 + R_RET + .4, Y1 - .05), (YS_END + .05, YX0 - R_RET - .4)):
            b.box('paver', xc, (y0 + y1) / 2, SWZ + .002, w, y1 - y0, .012)
            y = y0 + 1.0
            clear = abs(x_in) - (RH + .1 + w)
            while y < y1 - .5:                                                              # scored joints across the clear sidewalk
                b.box('sidejoint', sx * (RH + .1 + w + clear / 2), y, SWZ, clear - .1, .02, .004)
                y += 1.6
    for x0, x1 in ((XW_END + .5, -(RH + R_RET + .5)), (RH + R_RET + .5, XE_END - .5)):      # joints along the cross-street sidewalks
        for yy in (YX1 + 1.85, YX0 - 1.85):
            b.box('sidejoint', (x0 + x1) / 2, yy, SWZ, x1 - x0, .02, .004)
    for y in (14.0, 24.0, 46.0, 66.0, -24.0, -50.0):
        tree_pit(b, -(RH + .68), y)
    for y in (19.0, 27.0, 49.0, 68.0, -28.0, -52.0):
        tree_pit(b, RH + .85, y)
    for x, y in ((-(RH + .7), 20.0), (RH + 1.0, 15.5), (RH + 1.0, 44.0), (-(RH + .7), YS0 - 6.0)):
        b.box('hardware', x, y, SWZ + .46, .5, .5, .92)                                    # litter bins
        b.box('dark', x, y, SWZ + .95, .56, .56, .08)
    # TTC stop pole on the east sidewalk north of the corner (northbound stop).
    b.box('steel', RH + .5, 6.2, SWZ + 1.6, .07, .07, 3.2)
    b.box('ttc', RH + .5, 6.2, SWZ + 2.75, .05, .5, .62)
    b.box('car_white', RH + .5, 6.2, SWZ + 2.32, .052, .5, .22)
    # No-stopping sign on the west sidewalk (front view).
    b.box('steel', -(RH + .5), 71.5, SWZ + 1.4, .06, .06, 2.8)
    b.box('car_white', -(RH + .5), 71.5, SWZ + 2.5, .04, .45, .55)
    b.box('ttc', -(RH + .48), 71.5, SWZ + 2.5, .02, .3, .3)
    b.flush('street furniture')


def sag(x):
    return SPAN_Z - SAG * (1 - (x / XP) ** 2)


def overhead():
    """Steel poles carrying span wires, hangers and two contact wires (one over each track), and cobra-head lights."""
    b = Batch()
    for y in POLES:
        for sx in (-1, 1):
            C.rod('Overhead pole', (sx * XP, y, SWZ), (sx * XP, y, 10.2), .13, 'steel', 'overhead', 12)
            b.box('steel', sx * XP, y, SWZ + .16, .5, .5, .3)                                   # base plate and collar
            b.box('steel', sx * XP, y, 10.24, .3, .3, .08)                                      # pole cap
            b.beam('steel', (sx * XP, y, 9.4), (sx * (XP - 1.6), y, 9.85), .09, .09)             # cobra-head arm
            b.beam('steel', (sx * (XP - 1.6), y, 9.85), (sx * (XP - 3.0), y, 9.95), .08, .08)
            b.box('lamp', sx * (XP - 3.25), y, 9.88, .8, .34, .14)
            b.box('steel', sx * (XP - 3.25), y, 9.99, .84, .38, .08)
            b.box('hardware', sx * (XP - .2), y, SPAN_Z, .26, .12, .12)                       # span clamp
            b.box('hardware', sx * (XP - 1.3), y, sag(sx * (XP - 1.3)), .32, .07, .07)          # strain insulator
        xs = [-XP + .13 + (2 * XP - .26) * i / 10 for i in range(11)]
        for i in range(10):
            C.rod('Span wire', (xs[i], y, sag(xs[i])), (xs[i + 1], y, sag(xs[i + 1])), .012, 'wire', 'overhead', 6)
        for tc in (-TC, TC):
            C.rod('Contact wire hanger', (tc, y, WIRE_Z), (tc, y, sag(tc)), .014, 'wire', 'overhead', 6)
            b.box('hardware', tc, y, WIRE_Z + .03, .08, .3, .07)                               # trolley-wire clamp
            b.box('car_white', tc, y, WIRE_Z + .45, .07, .07, .22)                              # hanger insulator
    for tc in (-TC, TC):
        C.rod('Contact wire', (tc, YS_END, WIRE_Z), (tc, Y1, WIRE_Z), .012, 'wire', 'overhead', 6)
    b.flush('overhead')


def car_bodies():
    """Module spans (south, north) from the leading north end."""
    out, y = [], CAR_N
    for L in MODS:
        out.append((y - L, y)); y -= L + GAP
    return out


# Cab nose profile: (height, forward reach beyond the cab-end line, side inset). The lower front stands near vertical,
# the windscreen rakes back about 20 degrees and steepens into the domed red roof cap, which curves back about 1 m.
NOSE = [(.30, .32, .02), (.52, .44, 0), (.84, .50, 0), (1.18, .52, 0), (1.30, .51, 0), (1.70, .43, 0), (2.10, .31, .01),
        (2.40, .18, .02), (2.65, .02, .035), (2.85, -.12, .055), (3.00, -.28, .09), (3.10, -.43, .14), (3.18, -.60, .21),
        (3.23, -.80, .30), (3.26, -.95, .40)]
CAB_D = 2.6                                      # cab section length behind the cab-end line, lofted instead of boxed


def _nose(z, k):
    pr = NOSE
    if z <= pr[0][0]:
        return pr[0][k]
    for p0, p1 in zip(pr, pr[1:]):
        if z <= p1[0]:
            return p0[k] + (p1[k] - p0[k]) * (z - p0[0]) / (p1[0] - p0[0])
    return pr[-1][k]


def nose_f(z):
    """Forward reach of the raked cab nose beyond the cab-end line at height z."""
    return _nose(z, 1)


def nose_curve(ye, sgn, z, off=0.0, wrap=None, n=8, hwb=None):
    """Plan ring of the cab at height z, offset outward by off: the sides leave the module body at CAB_D behind the cab-end
    line at the body's half-width hwb, taper to the nose half-width, and turn round two corner arcs across the front.
    With wrap, only the front part, from wrap metres behind each corner start."""
    xc = TC
    f = nose_f(z) + off
    hwf = CAR_W / 2 - _nose(z, 2) + off
    hwb = (CAR_W / 2 if hwb is None else hwb) + off
    rc = .62 + .23 * min(1.0, max(0.0, (z - 2.85) / .41))                                       # corners round more up the cap
    rc = min(rc, hwf - .05)
    yf = ye + sgn * f
    ys = yf - sgn * rc                                                                         # where the corner arc leaves the side
    yb = ye - sgn * CAB_D

    def hw_at(y):
        t = min(1.0, max(0.0, (y - yb) * sgn / max(1e-6, abs(ys - yb))))
        return hwb + (hwf - hwb) * t * t * (3 - 2 * t)                                         # smooth taper, tangent at both ends
    y0 = yb if wrap is None else ys - sgn * wrap
    side = [yb + (ys - yb) * u for u in (.2, .4, .6, .8)] if wrap is None else []
    pts = [(xc - hw_at(y0), y0, z)] + [(xc - hw_at(y), y, z) for y in side]
    for i in range(n + 1):                                                                     # left corner
        a = math.pi / 2 * i / n
        pts.append((xc - hwf + rc * (1 - math.cos(a)), ys + sgn * rc * math.sin(a), z))
    for i in range(n + 1):                                                                     # right corner
        a = math.pi / 2 * (1 - i / n)
        pts.append((xc + hwf - rc * (1 - math.cos(a)), ys + sgn * rc * math.sin(a), z))
    pts += [(xc + hw_at(y), y, z) for y in side[::-1]] + [(xc + hw_at(y0), y0, z)]
    if sgn < 0:
        pts = pts[::-1]
    return pts


def smooth_loft(name, rings, role):
    """Open loft capped at both ends; the swept faces are smooth-shaded, the two flat caps stay flat."""
    obj = loft(name, rings, role, 'streetcar', closed=False)
    ps = obj.data.polygons
    for k, poly in enumerate(ps):
        poly.use_smooth = k < len(ps) - 2
    return obj


def cab_loft(name, rings, role):
    """Cab band loft from open plan rings that start and end on the cab-start line. The swept skin is smooth-shaded on
    its own vertices; the flat back strip on the cab-start line and the two flat caps get separate vertices, so no
    smoothed normal bends round a square edge."""
    n, m = len(rings), len(rings[0])
    vs = [v for ring in rings for v in ring]
    fs = [(i * m + j, (i + 1) * m + j, (i + 1) * m + j + 1, i * m + j + 1) for i in range(n - 1) for j in range(m - 1)]
    ns = len(fs)
    base = len(vs)
    for ring in rings:
        vs += [ring[-1], ring[0]]
    fs += [(base + 2 * i, base + 2 * i + 2, base + 2 * i + 3, base + 2 * i + 1) for i in range(n - 1)]
    base = len(vs); vs += list(rings[0]); fs.append(tuple(range(base + m - 1, base - 1, -1)))
    base = len(vs); vs += list(rings[-1]); fs.append(tuple(base + j for j in range(m)))
    obj = C.mesh(name, vs, fs, role, 'streetcar')
    for k, poly in enumerate(obj.data.polygons):
        poly.use_smooth = k < ns
    return obj


def nose(b, ye, sgn):
    """Raked, domed Flexity cab lofted from plan rings in the livery bands of the body: red skirt, white band, the glass
    band that is the wrapped windscreen at the front, white band and a red roof cap that domes back into the roof.
    Front overlays give the white apron, the red light band, the tall windscreen head and the red brow."""
    hb = CAR_W / 2
    bands = [('skirt', [.30, .52, .749], 'car_red', lambda z: hb),
             ('white band', [.751, .84, 1.00, 1.179], 'car_white', lambda z: hb + .01),
             ('glass band', [1.181, 1.30, 1.50, 1.70, 1.90, 2.10, 2.25, 2.399], 'car_glass', lambda z: hb - .02),
             ('upper white band', [2.401, 2.55, 2.70, 2.849], 'car_white', lambda z: hb),
             ('roof cap', [2.851, 2.95, 3.03, 3.099], 'car_red', lambda z: hb),                 # meets the boxed red roof band
             ('roof dome', [3.10, 3.16, 3.21, 3.245, 3.26], 'car_red', lambda z: hb - .05)]     # meets the boxed roof, same step
    for nm, zs, role, hwb in bands:
        cab_loft(f'Streetcar cab {nm}', [nose_curve(ye, sgn, z, hwb=hwb(z)) for z in zs], role)

    def shell(name, zs, role, wrap, o1=.016, o0=.004):
        rings = [nose_curve(ye, sgn, z, off=o1, wrap=wrap) + nose_curve(ye, sgn, z, off=o0, wrap=wrap)[::-1] for z in zs]
        smooth_loft(name, rings, role)
    shell('Streetcar apron', [.52, .62, .72, .84], 'car_white', .10)                           # white lower apron
    shell('Streetcar light band', [.842, 1.00, 1.18, 1.30], 'car_red', .12)                     # red light band under the windscreen
    shell('Streetcar windscreen head', [2.38, 2.52, 2.68], 'car_glass', .42)                    # windscreen runs up past the side band
    shell('Streetcar brow', [2.682, 2.78, 2.86], 'car_red', .42)                                 # red brow joining the cap
    xc = TC

    def front(z, off):
        return (xc, ye + sgn * (nose_f(z) + off), z)
    b.beam('amber', front(2.44, .03), front(2.62, .03), 1.3, .012)                             # destination sign
    for s in (-1, 1):
        y = ye + sgn * (nose_f(1.0) + .025)
        b.box('lamp', xc + s * .72, y, 1.02, .30, .06, .11)                                     # headlights in the red light band
        for k in (1, 2):
            b.box('car_white', xc + s * (.18 + .17 * k), y, 1.02, .09, .05, .09)
        yp = ye + sgn * (nose_f(1.8) - .62 - .40)                                              # white pillar behind the wrapped windscreen
        b.box('car_white', xc + s * (CAR_W / 2 - .01), yp, 1.79, .03, .12, 1.22)
    b.box('rubber', xc, ye + sgn * (nose_f(.36) + .02), .38, 1.6, .1, .1)                      # anti-climber


def streetcar():
    """Five-module red-and-white articulated low-floor streetcar on the east track, pantograph up to the wire."""
    b = Batch()
    xc, hw = TC, CAR_W / 2
    mods = car_bodies()
    for i, (m0, m1) in enumerate(mods):
        y0 = m0 + (CAB_D if i == len(mods) - 1 else 0.0)                                      # end modules stop where the cab begins
        y1 = m1 - (CAB_D if i == 0 else 0.0)
        L, yc = y1 - y0, (y0 + y1) / 2
        b.box('car_red', xc, yc, .525, CAR_W, L, .45)                                        # red skirt .30-.75
        b.box('car_white', xc, yc, .965, CAR_W + .02, L, .43)                                 # wide white band .75-1.18
        b.box('car_glass', xc, yc, 1.79, CAR_W - .04, L, 1.22)                                # window band 1.18-2.40
        n = max(3, round(L / 1.3))
        for k in range(n + 1):                                                                 # slim window mullions
            py = y0 + .05 + (L - .1) * k / n
            b.box('car_white', xc, py, 1.79, CAR_W - .01, .07, 1.22)
        cab_end = y1 if i == 0 else (y0 if i == len(mods) - 1 else None)
        for py in (y0 + .1, y1 - .1):                                                          # black joint stripes at the articulations
            if cab_end is not None and abs(py - cab_end) < .2:
                continue                                                                       # the lofted cab continues the bands here
            b.box('rubber', xc, py, 1.75, CAR_W + .03, .2, 2.5)
        b.box('car_white', xc, yc, 2.625, CAR_W, L, .45)                                      # wide white band 2.40-2.85
        b.box('car_red', xc, yc, 2.975, CAR_W, L, .25)                                        # red roof band 2.85-3.10
        r0, r1 = y0 + (0.0 if i == len(mods) - 1 else .02), y1 - (0.0 if i == 0 else .02)        # roof runs into the cab cap
        b.box('car_roof', xc, (r0 + r1) / 2, 3.18, CAR_W - .1, r1 - r0, .16)                  # roof 3.10-3.26
        if i in (0, 4):
            b.box('car_roof', xc, yc + (.5 if i == 4 else -.5), 3.44, 1.6, L - 1.4, .36)      # roof equipment
        if i in (0, 2, 4):                                                                     # bogies: frame and wheels on the rails
            for ax in (-.9, .9):
                for s in (-1, 1):
                    xr = xc + s * (GAUGE / 2 + .036)
                    C.rod('Streetcar wheel', (xr - .06, yc + ax, .366), (xr + .06, yc + ax, .366), .33, 'rubber', 'streetcar', 16)
            b.box('rubber', xc, yc, .25, 1.40, 2.7, .14)
        if i < len(mods) - 1:                                                                  # bellows to the next module
            b.box('rubber', xc, y0 - GAP / 2, 1.7, CAR_W - .24, GAP + .02, 2.6)
        if i in (1, 3):                                                                        # a door each side
            for s in (-1, 1):
                b.box('car_red', xc + s * (hw + .014), yc, 1.38, .01, 1.3, 2.1)
                b.box('car_glass', xc + s * (hw + .022), yc, 1.62, .01, .9, 1.3)
    nose(b, mods[0][1], 1)
    nose(b, mods[-1][0], -1)
    # Pantograph on the centre module: base, lower and upper arm, collector head at the contact wire.
    y0, y1 = mods[2]
    yp = (y0 + y1) / 2
    b.box('car_roof', xc, yp, 3.32, 1.2, 1.4, .12)
    for s in (-1, 1):
        b.box('car_white', xc + s * .45, yp, 3.44, .12, .12, .14)
    b.beam('hardware', (xc, yp - .7, 3.46), (xc, yp + .9, 4.6), .08, .08)
    b.beam('hardware', (xc, yp + .9, 4.6), (xc, yp - .2, WIRE_Z - .04), .06, .06)
    b.beam('hardware', (xc - .8, yp - .2, WIRE_Z - .035), (xc + .8, yp - .2, WIRE_Z - .035), .05, .05)
    b.flush('streetcar')


# ---- street walls ----

GZ0, GH = .62, 3.0                               # storefront bulkhead top and glazing height
DZ0 = .17                                        # door sill above the sidewalk
SIGN0, SIGN1 = 3.80, 4.36                        # sign band
FL2, FL3 = 4.62, 8.2                             # upper floor levels
UPS = ((5.35, 2.2), (8.9, 2.05))                 # second and third storey window sill and height


def hole_set(name, ua, ub, nb, per, floors, pattern, wscale=1.0):
    pc = [ua + .25 + k * (ub - ua - .5) / nb for k in range(nb + 1)]
    gh = []
    for k in range(nb):
        a, c = pc[k] + .22, pc[k + 1] - .22
        kind = pattern[k % len(pattern)]
        nm = f'{name} bay {k}'
        if kind == 'shop':
            gh.append(hole(nm + ' shopfront', (a + c) / 2, GZ0, c - a - .5, GH, kind='shop'))
        else:
            left = kind == 'door+shop'
            du = a + .25 + .55 if left else c - .25 - .55
            gh.append(hole(nm + ' door', du, DZ0, 1.1, GZ0 + GH - DZ0, kind='door'))
            sa, sc = (du + .85, c - .25) if left else (a + .25, du - .85)
            gh.append(hole(nm + ' shopfront', (sa + sc) / 2, GZ0, sc - sa, GH, kind='shop'))
    uh = []
    for fi in range(floors - 1):
        z, h = UPS[fi]
        for k in range(nb):
            bw = pc[k + 1] - pc[k]
            w = min(1.15, bw / per - .75) * wscale
            for j in range(per):
                u = pc[k] + bw * (j + .5) / per
                uh.append(hole(f'{name} storey {fi + 2} {k}.{j}', u, z, w, h, floor=fi))
    return pc, gh, uh


def letters(m, u0, u1, z, d, role, seed):
    rng = random.Random(seed)
    u = u0
    while u < u1:
        lw = rng.uniform(.10, .2)
        if u + lw > u1:
            break
        m.box(role, u + lw / 2, d, z, lw, .025, rng.choice((.24, .28, .32)))
        u += lw + rng.choice((.05, .06, .07, .3))


def arch_head(f, h, rise, ring=.2, segs=12, ring_role='stone', proud=.03):
    """Segmental or round head on a rectangular cut: brick spandrel infill above the curve, flush with the wall face,
    and a proud stone ring following the curve."""
    u, w, top = h['u'], h['w'], h['z'] + h['h']
    R = (w * w / 4 + rise * rise) / (2 * rise)
    cz = top - R
    a0 = math.asin(min(1.0, (w / 2) / R))
    pts_arc = [(u + R * math.sin(-a0 + 2 * a0 * i / segs), cz + R * math.cos(-a0 + 2 * a0 * i / segs)) for i in range(segs + 1)]
    pts = [(u - w / 2, top - rise)] + pts_arc + [(u + w / 2, top - rise)]
    vs, fs = [], []
    for (pu, pz) in pts:
        for d in (0.0, T - .01):
            vs.append(f.p(pu, d, pz)); vs.append(f.p(pu, d, top))
    for i in range(len(pts) - 1):
        a, b = 4 * i, 4 * (i + 1)
        fs += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3)]
    n = 4 * (len(pts) - 1)
    fs += [(0, 1, 3, 2), (n, n + 2, n + 3, n + 1)]
    C.mesh(f'{h["id"]} spandrel', vs, fs, 'wall', 'arches')
    vs, fs = [], []
    for (pu, pz) in pts_arc:
        r = math.hypot(pu - u, pz - cz)
        nu, nz = (pu - u) / r, (pz - cz) / r
        for d in (-proud, .02):
            vs.append(f.p(pu, d, pz)); vs.append(f.p(pu + nu * ring, d, pz + nz * ring))
    for i in range(segs):
        a, b = 4 * i, 4 * (i + 1)
        fs += [(a, b, b + 1, a + 1), (a + 2, a + 3, b + 3, b + 2), (a, a + 2, b + 2, b), (a + 1, b + 1, b + 3, a + 3)]
    n = 4 * segs
    fs += [(0, 1, 3, 2), (n, n + 2, n + 3, n + 1)]
    C.mesh(f'{h["id"]} arch ring', vs, fs, ring_role, 'arches')


def dress(spec, f, ua, ub, pc, gh, uh, skip, lite=False, bands=True, sign_span=None):
    """Storefront level, upper windows and (for mid-row blocks) the sign band, belt courses and cornice on one face."""
    m = Merge(f)
    top = spec['top']
    pil = spec.get('pil', 'stone')
    for k, u in enumerate(pc):
        if k == skip:
            continue
        m.box(pil, u, -.1, (.05 + SIGN0 - .04) / 2, .42, .22, SIGN0 - .09)                    # pilaster
        m.box('stone', u, -.135, SIGN0 - .12, .54, .29, .2)                                   # capital
        m.box('stone', u, -.125, .205, .5, .27, .29)                                          # plinth block
    fr = spec.get('frame', 'frame')
    for h in gh:
        if h['kind'] == 'shop':
            framed(m, f, h, cols=max(1, round(h['w'] / 1.25)), rows=1, inset=.14, occupied='shop', kind='shopfront', frame=fr)
            m.box(fr, h['u'], .12, h['z'] + h['h'] - .7, h['w'] - .12, .09, .07)              # transom bar
            m.box(fr, h['u'], -.015, (.06 + GZ0 - .05) / 2, h['w'] + .05, .04, GZ0 - .11)     # panelled bulkhead
            m.box('stone', h['u'], -.05, GZ0 - .045, h['w'] + .12, .14, .08)                    # sill
        else:
            framed(m, f, h, cols=1, rows=1, inset=.16, occupied='shop', kind='door', frame=fr)
            m.box(fr, h['u'], .15, 2.92, h['w'] - .12, .09, .07)
            m.box(fr, h['u'], .19, DZ0 + .5, h['w'] - .14, .05, .8)
            m.box('stone', h['u'], T / 2, DZ0 + .005, h['w'] - .02, T - .04, .03)
    heads = spec['heads']
    for h in uh:
        fi = h['floor']
        framed(m, f, h, cols=1, rows=2, inset=.15, occupied='upper room', frame='white', lite=lite)
        m.box('stone', h['u'], -.05, h['z'] - .055, h['w'] + .22, .14, .1)                     # sill
        hd = heads[fi]
        if hd == 'flat':
            m.box('stone', h['u'], -.02, h['z'] + h['h'] + .155, h['w'] + .3, .08, .3)          # lintel
        elif hd == 'seg':
            arch_head(f, h, .3, ring=.2, segs=8, ring_role='stone')
        else:
            arch_head(f, h, h['w'] / 2, ring=.22, segs=12, ring_role='stone')
            m.box('stone', h['u'], -.045, h['z'] + h['h'] + .11, .2, .1, .26)                 # keystone
    la, lb = sign_span if sign_span else (ua + (ub - ua) * .2, ua + (ub - ua) * .8)
    letters(m, la, lb, (SIGN0 + SIGN1) / 2, -.16, 'cream', int(abs(ua) * 10))
    if bands:
        lo, hi = ua + .01, ub - .01
        m.box('sign', (lo + hi) / 2, -.07, (SIGN0 + SIGN1) / 2, hi - lo, .16, SIGN1 - SIGN0)
        m.box('stone', (lo + hi) / 2, -.1, SIGN1 + .04, hi - lo, .26, .12)
        m.box('stone', (lo + hi) / 2, -.06, FL2 + .05, hi - lo, .17, .2)
        if spec['floors'] > 2:
            m.box('stone', (lo + hi) / 2, -.06, FL3 + .05, hi - lo, .17, .18)
        cornice(spec, m, lo, hi, top)
    if spec.get('corbels'):
        n = int((ub - ua - .6) / .5)
        for i in range(n + 1):
            m.box('wall', ua + .3 + (ub - ua - .6) * i / n, -.09, top - 1.0, .22, .2, .3)
    m.flush(spec['name'] + ' ' + f.label)


def cornice(spec, m, lo, hi, top):
    kind = spec['cornice']
    if kind == 'bracket':                                                                    # pressed-metal cornice on scrolled brackets
        eave_cornice(m, lo, hi, top - .25, span_t=T, proj=.75, role='white', modillions=True)
        m.box('white', (lo + hi) / 2, -.05, top - 1.2, hi - lo, .14, .5)
        for u in (lo + .25, hi - .25):
            m.box('white', u, -.34, top - 1.0, .3, .7, .9)
    else:
        m.box('stone', (lo + hi) / 2, -.12, top - .55, hi - lo, .3, .3)
        m.box('stone', (lo + hi) / 2, -.05, top - 1.35, hi - lo, .14, .16)
    m.box('stone', (lo + hi) / 2, T / 2 - .03, top + .04, hi - lo, T + .14, .1)                # coping


VIC = [
    dict(name='West corner block', side='W', a=YN0, b=24.0, top=12.6, depth=31.0, nb=5, per=2, floors=3, heads=('seg', 'round'),
         role='wall', pil='stone', cornice='stone', corner=True, south_nb=7, corbels=True, gable=True, letters='cream', side_sign=5.2),
    dict(name='West brick block', side='W', a=24.0, b=37.0, top=11.8, depth=24.0, nb=3, per=2, floors=3, heads=('flat', 'flat'),
         role='brick2', pil='brick2', cornice='bracket', dy=.03, letters='sign', frame='dark'),
    dict(name='East corner block', side='E', a=YN0, b=22.0, top=11.8, depth=28.0, nb=4, per=2, floors=3, heads=('flat', 'flat'),
         role='wall', pil='stone', cornice='stone', corner=True, south_nb=6, letters='cream'),
    dict(name='East brick block', side='E', a=22.0, b=34.0, top=11.4, depth=24.0, nb=3, per=2, floors=3, heads=('seg', 'seg'),
         role='brick3', pil='stone', cornice='bracket', dy=.03, letters='sign', frame='dark'),
    dict(name='East low block', side='E', a=34.0, b=44.0, top=8.2, depth=22.0, nb=2, per=3, floors=2, heads=('flat',),
         role='brick2', pil='brick2', cornice='stone', letters='cream', dark_roof=True),
]


def street_face(spec):
    dy = spec.get('dy', 0.0)
    if spec['side'] == 'W':
        return C.Face((XWB - dy, 0.0, 0.0), (0, 1, 0), (-1, 0, 0), spec['name'] + ' street'), spec['a'], spec['b']
    return C.Face((XEB + dy, 0.0, 0.0), (0, -1, 0), (1, 0, 0), spec['name'] + ' street'), -spec['b'], -spec['a']


def corner_bands(spec):
    """Sign band, belts and cornice of a corner block as world runs: the street run wraps the corner by its projection and
    the cross-street run stops at the street run's back face, so the two never overlap."""
    top, depth, e = spec['top'], spec['depth'], spec['side'] == 'E'
    bands = [('sign', .15, .01, (SIGN0 + SIGN1) / 2, SIGN1 - SIGN0), ('stone', .23, .03, SIGN1 + .04, .12),
             ('stone', .145, .025, FL2 + .05, .2), ('stone', .145, .025, FL3 + .05, .18),
             ('stone', .10, .02, top - 1.35, .16), ('stone', .27, .03, top - .55, .3), ('stone', .1, T + .04, top + .04, .1)]
    b = Batch()
    side_sign = spec.get('side_sign')
    for role, p, q, z, h in bands:
        if not e and side_sign and z in ((SIGN0 + SIGN1) / 2, SIGN1 + .04):                    # only over the corner shopfront
            b.box(role, XWB + (p - q) / 2, (YN0 - p + spec['b'] - .01) / 2, z, p + q, spec['b'] - .01 - YN0 + p, h)
            b.box(role, XWB - q - side_sign / 2, YN0 + (q - p) / 2, z, side_sign, p + q, h)
            continue
        if e:
            b.box(role, XEB + (q - p) / 2, (YN0 - p + spec['b'] - .01) / 2, z, p + q, spec['b'] - .01 - YN0 + p, h)
            b.box(role, (XEB + q + XEB + depth - .01) / 2, YN0 + (q - p) / 2, z, depth - .01 - q, p + q, h)
        else:
            b.box(role, XWB + (p - q) / 2, (YN0 - p + spec['b'] - .01) / 2, z, p + q, spec['b'] - .01 - YN0 + p, h)
            b.box(role, (XWB - q + XWB - depth + .01) / 2, YN0 + (q - p) / 2, z, depth - .01 - q, p + q, h)
    s = 1 if e else -1                                                                         # corner pier wrapping both faces
    xo = XEB if e else XWB
    b.box('stone', xo + s * .04, YN0 + .04, (.05 + SIGN0 - .06) / 2, .56, .56, SIGN0 - .11)
    b.box('stone', xo + s * .04, YN0 + .04, SIGN0 - .14, .66, .66, .16)
    b.box('stone', xo + s * .04, YN0 + .04, .2, .64, .64, .3)
    b.flush(spec['name'] + ' corner bands')


def west_side_holes(spec, sa, sb):
    """The west corner block's cross-street side as the oblique shows it: one shopfront at the corner, a mostly solid brick
    ground storey with a few doors and small windows, and flat-headed sashes in pairs at an irregular rhythm above."""
    nm = spec['name'] + ' side'
    gh = [hole(nm + ' corner shopfront', sb - 2.9, GZ0, 4.2, GH, kind='shop'),
          hole(nm + ' door 1', sb - 9.6, DZ0, 1.1, 2.7, kind='door'),
          hole(nm + ' door 2', sb - 18.4, DZ0, 1.1, 2.7, kind='door'),
          hole(nm + ' service door', sa + 1.1, DZ0, 1.0, 2.6, kind='door')]
    uh = [hole(f'{nm} ground window {k}', u, 1.05, .95, 1.75, floor=0) for k, u in enumerate((sb - 13.2, sb - 22.4, sb - 26.0))]
    pairs = (2.7, 6.6, 10.9, 14.4, 18.6, 22.1, 26.4)                                            # pair centres from the corner
    for fi in range(spec['floors'] - 1):
        z, h = UPS[fi]
        for k, c in enumerate(pairs):
            for j, du in enumerate((-.62, .62)):
                uh.append(hole(f'{nm} storey {fi + 2} pair {k}.{j}', sb - c + du, z, .9, h, floor=fi))
    return [], gh, uh


def victorian(spec):
    top, depth, floors = spec['top'], spec['depth'], spec['floors']
    f, ua, ub = street_face(spec)
    corner = spec.get('corner')
    pattern = ['door+shop', 'shop'] if spec['side'] == 'W' else ['shop', 'shop+door']
    pc, gh, uh = hole_set(spec['name'], ua, ub, spec['nb'], spec['per'], floors, pattern)
    z0 = .003 if spec.get('dy') else 0.0
    f.wall(spec['name'] + ' street carrier', ua, ub, z0, top, depth=T, role=spec['role'], holes=gh + uh)
    G.brick_courses(f, ua + .02, ub - .02, GZ0 - .1, top - .12, gh + uh, spacing=.16)
    skip = (0 if spec['side'] == 'W' else spec['nb']) if corner else -1
    dress(spec, f, ua, ub, pc, gh, uh, skip, lite=spec['side'] == 'E' and not corner, bands=not corner)
    if corner:
        e = spec['side'] == 'E'
        sf = C.Face((0.0, YN0, 0.0), (1, 0, 0), (0, 1, 0), spec['name'] + ' cross street')
        sa, sb = (XEB + T, XEB + depth) if e else (XWB - depth, XWB - T)
        if e:
            spc, sgh, suh = hole_set(spec['name'] + ' side', sa, sb, spec['south_nb'], 2, floors, ['shop', 'door+shop', 'shop'])
            sgh.append(hole(spec['name'] + ' side service door', sb - 1.1, DZ0, 1.0, 2.6, kind='door'))
            sgh = [h for h in sgh if not (h['kind'] == 'shop' and abs(h['u'] - (sb - 1.1)) < h['w'] / 2 + .7)]
            sspec, span = spec, None
        else:
            spc, sgh, suh = west_side_holes(spec, sa, sb)
            sspec, span = dict(spec, heads=('flat', 'flat')), (sb - 5.0, sb - .8)
        sf.wall(spec['name'] + ' side carrier', sa, sb, 0.0, top, depth=T, role=spec['role'], holes=sgh + suh)
        G.brick_courses(sf, sa + .02, sb - .02, GZ0 - .1, top - .12, sgh + suh, spacing=.16)
        dress(sspec, sf, sa, sb, spc, sgh, suh, 0 if e else -1, lite=True, bands=False, sign_span=span)
        corner_bands(spec)
    body(spec)
    if spec.get('gable'):
        ym = (spec['a'] + spec['b']) / 2
        gable_wall(spec['name'] + ' street gable', XWB - T / 2, ym - 3.6, ym + 3.6, top, 2.4, axis='x', role=spec['role'])
        b = Batch()
        for s in (-1, 1):
            b.beam('stone', (XWB - T / 2, ym + s * 3.85, top - .12), (XWB - T / 2, ym, top + 2.4 + .06), T + .2, .22)
        b.box('stone', XWB + .03, ym, top + 1.0, .1, 1.3, 1.0)                                  # date plaque
        b.box('stone', XWB - T / 2, ym, top + 2.75, .5, .5, .4)                                # finial block
        b.flush(spec['name'] + ' gable')


def body(spec):
    """Rear and side walls, floors, roof inside the parapets, interior back walls, rooftop units, room lights."""
    top, depth, e = spec['top'], spec['depth'], spec['side'] == 'E'
    y0, y1 = spec['a'], spec['b']
    corner = spec.get('corner')
    dy = spec.get('dy', 0.0)
    X = (lambda d: XEB + dy + d) if e else (lambda d: XWB - dy - d)                         # world x at inward depth d
    xm, wi = (X(T) + X(depth - T)) / 2, depth - 2 * T                                        # between the street carrier and the rear wall
    ya = y0 + T if corner else y0                                                            # a corner block's side carrier closes its low end
    b = Batch()
    b.box(spec['role'], X(depth - T / 2), (ya + y1) / 2, (top - .05) / 2, T, y1 - ya, top - .05)          # rear wall
    if not corner:
        b.box(spec['role'], xm, y0 + T / 2, (top - .05) / 2, wi, T, top - .05)                           # party walls
    b.box(spec['role'], xm, y1 - T / 2, (top - .05) / 2, wi, T, top - .05)
    yi0, yi1 = y0 + T, y1 - T
    yc, wy = (yi0 + yi1) / 2, yi1 - yi0
    rz = top - 1.0
    b.box('dark' if spec.get('dark_roof') else 'roof', xm, yc, rz - .1, wi, wy, .2)
    b.box('floor', xm, yc, .09, wi, wy, .14)
    for fz in ([FL2, FL3] if spec['floors'] > 2 else [FL2]):
        b.box('floor', xm, yc, fz - .13, wi, wy, .26)
    b.box('interior', X(7.0), yc, (.3 + FL2 - .3) / 2, .15, wy, FL2 - .6)
    b.box('interior', X(6.0), yc, (FL2 + rz - .25) / 2, .15, wy, rz - .25 - FL2)
    for hx, hy in ((.45, .3), (.7, .7)):
        b.box('membrane', X(depth * hx), y0 + (y1 - y0) * hy, rz + .4, 1.4, 1.1, .8)
        b.box('hardware', X(depth * hx), y0 + (y1 - y0) * hy, rz + .84, 1.0, .7, .08)
    if corner and e:                                                                          # the two glazed hipped roof skylights (top view)
        for hx, hy in ((.3, .42), (.55, .62)):
            cx, cy = X(depth * hx), y0 + (y1 - y0) * hy
            b.box('pale', cx, cy, rz + .2, 2.8, 2.2, .4)
            pitched_roof(spec['name'] + ' skylight', cx - 1.3, cx + 1.3, cy - 1.0, cy + 1.0, rz + .55, .6, True, True, 'x', .04, 'glass', 'roof')
    b.flush(spec['name'] + ' body')
    C.qa_room_light(spec['name'] + ' shop', (X(3.5), (y0 + y1) / 2, 2.6), 90, 3.0)
    C.qa_room_light(spec['name'] + ' upper', (X(3.0), (y0 + y1) / 2, FL2 + 2.3), 60, 3.0)


def fbox(b, side, role, y, d, z, w, t, h):
    """Axis-aligned box on a main-street face: y along the street, d inward from the building line."""
    x = XWB - d if side == 'W' else XEB + d
    b.box(role, x, y, z, t, w, h)


def condo(name, side, y0, y1, depth, top, piers, pier_role, band_role, step, balcony, glass_role='glass', mullion='white'):
    """Concrete-frame condominium front: ground storefronts under a canopy, piers, slab-edge bands, recessed glazing,
    glass-railed balconies; end, rear and roof closure with a green roof."""
    b = Batch()
    nb = round((y1 - y0 - .7) / step)
    ys = [y0 + .36 + (y1 - y0 - .72) * k / nb for k in range(nb + 1)]
    floors = [4.6 + 3.0 * i for i in range(int((top - .4 - 4.6) / 3.0) + 1) if 4.6 + 3.0 * i < top - 1.0]
    for k, y in enumerate(ys):
        if k % piers == 0 or k in (0, nb):
            fbox(b, side, pier_role, y, .125, (top - .05) / 2, .7, .65, top - .05)           # piers, full height
    for f in floors:
        fbox(b, side, band_role, (y0 + y1) / 2, .15, f + .15, y1 - y0 - .04, .54, .3)        # slab edges
    fbox(b, side, band_role, (y0 + y1) / 2, .15, top - .2, y1 - y0 - .04, .54, .4)           # parapet band
    fbox(b, side, 'charcoal', (y0 + y1) / 2, -.55, 4.2, y1 - y0 - .8, 1.3, .2)               # canopy over the storefronts
    for k in range(nb):
        ya, yb = ys[k] + .36, ys[k + 1] - .36
        fbox(b, side, glass_role, (ya + yb) / 2, .40, (.17 + top - .45) / 2, yb - ya, .02, top - .62)
        fbox(b, side, mullion, (ya + yb) / 2, .36, (.17 + top - .45) / 2, .08, .06, top - .62)
        for f in floors[1:] if balcony == 'all' else (floors[1:] if k % 2 == 0 else []):
            fbox(b, side, 'pale', (ya + yb) / 2, -.75, f + .15, yb - ya - .02, 1.3, .22)       # balcony slab
            fbox(b, side, 'railglass', (ya + yb) / 2, -1.36, f + .78, yb - ya - .06, .02, 1.04)  # glass rail
            fbox(b, side, 'hardware', (ya + yb) / 2, -1.37, f + 1.32, yb - ya - .06, .05, .05)
            for ye_ in (ya + .045, yb - .045):                                                 # glass returns at both balcony ends
                fbox(b, side, 'railglass', ye_, -.7275, f + .78, .02, 1.255, 1.03)              # 5 mm inside the front panel
                fbox(b, side, 'hardware', ye_, -.74, f + 1.317, .04, 1.24, .04)
        for f in floors:
            fbox(b, side, 'stone', (ya + yb) / 2, .3, f + .36, yb - ya, .12, .06)            # sill
    # Interior behind the glass, floors, closure walls and the green roof.
    fbox(b, side, 'interior', (y0 + y1) / 2, 5.0, (top - .45) / 2, y1 - y0 - .8, .2, top - .85)
    fbox(b, side, 'floor', (y0 + y1) / 2, 2.7, .09, y1 - y0 - .82, 4.4, .14)
    for f in floors:
        fbox(b, side, 'floor', (y0 + y1) / 2, 2.7, f - .12, y1 - y0 - .82, 4.4, .24)
    for yy in (y0 + .2, y1 - .2):
        fbox(b, side, pier_role, yy, (depth + .45) / 2, top / 2, .4, depth - .45, top)
    fbox(b, side, pier_role, (y0 + y1) / 2, depth - .2, top / 2, y1 - y0 - .8, .4, top)
    fbox(b, side, 'green', (y0 + y1) / 2, (5.0 + depth - .4) / 2, top - .5, y1 - y0 - .8, depth - .4 - 5.0, .2)
    fbox(b, side, 'membrane', (y0 + y1) / 2, (.42 + 5.0) / 2, top - .5, y1 - y0 - .8, 5.0 - .42, .2)
    b.flush(name)
    xs = XWB - 3.0 if side == 'W' else XEB + 3.0
    C.qa_room_light(name + ' lobby', (xs, (y0 + y1) / 2, 2.6), 150, 4.0)


def condos():
    condo('West brick condominium wing', 'W', 37.0, 78.0, 12.0, 23.0, 1, 'brick2', 'stone', 3.4, 'alt')
    condo('East charcoal condominium', 'E', 44.0, 78.0, 26.0, 20.0, 1, 'charcoal', 'pale', 4.2, 'all', mullion='frame')
    b = Batch()
    # Penthouse on the east condominium, set back from the street.
    b.box('charcoal', XEB + 11.0, 61.0, 21.3, 10.0, 16.0, 3.4)
    b.box('glass', XEB + 5.99, 61.0, 21.4, .02, 14.0, 2.2)
    b.box('pale', XEB + 11.0, 61.0, 23.05, 10.4, 16.4, .1)
    # The glass slab behind the west wing: ten storeys, floor bands, east-face mullions and balconies, green roof, penthouse.
    xa, xb, ya, yb, top = -46.0, -25.0, 46.0, 76.0, 31.5
    b.box('curtain', (xa + xb) / 2, (ya + yb) / 2, top / 2, xb - xa, yb - ya, top)
    for i in range(1, 10):
        b.box('panel', (xa + xb) / 2, (ya + yb) / 2, 3.1 * i, xb - xa + .16, yb - ya + .16, .26)
    b.box('panel', (xa + xb) / 2, (ya + yb) / 2, top - .1, xb - xa + .16, yb - ya + .16, .4)
    for k in range(1, 20):
        y = ya + (yb - ya) * k / 20
        b.box('frame', xb + .03, y, top / 2, .1, .08, top - .4)
    b.box('green', (xa + xb) / 2, (ya + yb) / 2, top + .1, xb - xa - 1.0, yb - ya - 1.0, .2)
    b.box('membrane', -36.0, 61.0, top + 1.7, 9.0, 12.0, 3.0)
    b.box('curtain', -31.49, 61.0, top + 1.5, .02, 10.0, 2.0)
    # Its low glass base to the south, behind the west brick block.
    b.box('curtain', (xa + xb) / 2, 41.7, 5.0, xb - xa, 8.0, 10.0)
    for i in (1, 2):
        b.box('panel', (xa + xb) / 2, 41.7, 3.3 * i, xb - xa + .16, 8.16, .24)
    b.box('membrane', (xa + xb) / 2, 41.7, 10.1, xb - xa - .6, 7.4, .2)
    b.flush('west glass slab')


def context():
    """Blocks south of the cross street and beyond the corner blocks: simple brick and modern volumes with windows."""
    b = Batch()
    rows = [('W', YS_END, -44.0, 14.0, 'context'), ('W', -44.0, -27.0, 9.5, 'wall'), ('W', -27.0, YS0, 11.5, 'neighbour'),
            ('E', YS_END, -46.0, 9.0, 'neighbour'), ('E', -46.0, -30.0, 16.0, 'context'), ('E', -30.0, YS0, 10.5, 'brick2')]
    for side, y0, y1, h, role in rows:
        sx = -1 if side == 'W' else 1
        xin = XWB if side == 'W' else XEB
        dep = 26.0
        xc = xin + sx * dep / 2
        b.box(role, xc, (y0 + y1) / 2, h / 2, dep, y1 - y0, h)
        b.box('membrane', xc, (y0 + y1) / 2, h + .02, dep - .6, y1 - y0 - .6, .04)
        b.box('white' if role != 'context' else 'panel', xin + sx * .1, (y0 + y1) / 2, h - .5, .24, y1 - y0 - .1, .3)
        n = int((y1 - y0) / 3.6)
        for k in range(n):
            y = y0 + (y1 - y0) * (k + .5) / n
            b.box('glass', xin - sx * .005, y, 2.0, .02, 3.0, 2.8)                              # storefronts
            b.box('frame', xin - sx * .01, y, 3.8, .03, 3.3, .5)
            z = 5.4
            while z + 1.9 < h - .8:
                b.box('glass', xin - sx * .005, y, z + .95, .02, 1.1, 1.9)
                z += 3.4
        if y1 == YS0:                                                                          # their fronts on the cross street
            x0, x1 = sorted((xin, xin + sx * dep))
            m = int((x1 - x0) / 3.6)
            for k in range(m):
                x = x0 + (x1 - x0) * (k + .5) / m
                b.box('glass', x, YS0 + .005, 2.0, 3.0, .02, 2.8)
                z = 5.4
                while z + 1.9 < h - .8:
                    b.box('glass', x, YS0 + .005, z + .95, 1.1, .02, 1.9)
                    z += 3.4
    for x0, x1, y0, y1, h, role in ((XW_END, -44.5, YN0, 34.0, 8.5, 'context'), (42.0, XE_END, YN0, 34.0, 10.0, 'neighbour'),
                                    (XW_END, -40.5, YS_END, YS0, 9.0, 'neighbour'), (40.0, XE_END, YS_END, YS0, 8.0, 'context'),
                                    (XW_END, -47.0, 36.0, Y1, 12.0, 'context'), (42.0, XE_END, 36.0, Y1, 9.0, 'context')):
        b.box(role, (x0 + x1) / 2, (y0 + y1) / 2, h / 2, x1 - x0, y1 - y0, h)
        b.box('membrane', (x0 + x1) / 2, (y0 + y1) / 2, h + .02, x1 - x0 - .6, y1 - y0 - .6, .04)
        yf = y0 if y0 == YN0 else (y1 if y1 == YS0 else None)
        if yf is not None:
            m = int((x1 - x0) / 3.6)
            for k in range(m):
                x = x0 + (x1 - x0) * (k + .5) / m
                sgn = -1 if yf == y0 else 1
                b.box('glass', x, yf + sgn * .005, 2.0, 3.0, .02, 2.8)
                b.box('glass', x, yf + sgn * .005, 6.0, 1.2, .02, 1.8)
    b.flush('context')


def build():
    ground()
    track_and_markings()
    furniture()
    overhead()
    streetcar()
    for s in VIC:
        victorian(s)
    condos()
    context()
    C.CONTACTS.append(dict(name='Streetcar main street: track slab and grooved rails in the asphalt, sidewalks and furnishing strips, '
                                'span-wire poles, the streetcar on the rails under its contact wire, storefront street walls', box=[XW_END, XE_END, YS_END, Y1]))


LIGHT_RIG = dict(key=(45, -40, 60), fill=(-45, -30, 40), rear=(-10, 130, 45), target=(0.0, 30.0, 3.0), gain=6.0)
