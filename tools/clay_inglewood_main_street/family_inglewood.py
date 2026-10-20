"""Inglewood main street (Calgary, 9 Avenue SE) street option, authored from the locked catalogue views of
inglewood_main_street / variant_0.

Read from the pixels (the top view governs the plan): a straight run of a historic main street, its north side a
continuous street wall of early-1900s two-storey red-brick commercial blocks with flat gravel roofs inside parapets
and a back lane behind them; a cross street at the west end. The section from the north building line: a wide pale
concrete sidewalk with scored joints and a red brick-paver furnishing strip at the curb carrying young street trees
in pits, black lamp standards with red banners, bins and bike hoops; a lane of angled parking with white stall lines
and an edge line; one travel lane each way divided by a double yellow centre line; the same parking and sidewalk on
the south side. Curb extensions (bulb-outs) at the cross street and at a mid-block ladder crossing; red brick-paver
crossings with white edge lines at the intersection. The blocks: a corner block with paired upper windows, a stone
belt and a white cornice; a middle block with cream cast pilasters, a sign band, segmental-arched upper windows and a
raised central parapet; a narrower block with a dark bracketed metal cornice over arched windows; and a taller end
block with a cream stone sign fascia and corner pilaster. Large storefront glazing with transoms and recessed-panel
bases at grade. A row of plainer two-storey commercial blocks on the south side and low buildings beyond the lane are
context only.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-inglewood-main-street'
XW, XE = -30.0, 46.0                            # west building face (on the cross street) and the east edge of the section
SWZ = .15                                       # sidewalk top: 150 mm curb
SW, PK, LN = 5.6, 4.9, 3.7                      # sidewalk (building line to curb face), angled parking, travel lane
YC = -(SW + PK + LN)                            # double yellow centre line
YS = 2 * YC                                     # south building line (the section is symmetric about the centre line)
BULB = SW + PK - .3                             # curb extensions reach to the parking edge, 300 mm short of the travel lane
XCW, XCE = -49.4, -35.0                         # cross street curbs (road west and east); its sidewalk XCE..XW
LANE0, LANE1 = 25.0, 31.0                       # back lane behind the north blocks
T = .4
EPS = .002
PALETTE = dict(wall=(.58, .29, .19), brick=(.58, .29, .19), joint=(.70, .64, .56), stone=(.80, .74, .62), cream=(.86, .81, .68),
    white=(.93, .92, .88), trim=(.93, .92, .88), frame=(.13, .21, .18), dark=(.15, .16, .17), sign=(.20, .24, .22),
    glass=(.20, .25, .27), interior=(.82, .78, .72), floor=(.56, .46, .36), roof=(.52, .48, .40), membrane=(.76, .76, .74),
    concrete=(.76, .75, .72), sidejoint=(.60, .59, .56), paver=(.55, .30, .23), asphalt=(.25, .25, .26), lane=(.33, .33, .34),
    marking=(.94, .94, .92), yellow=(.86, .66, .18), hardware=(.08, .08, .09), banner=(.62, .12, .14), timber=(.40, .30, .21),
    tree=(.32, .46, .20), planting=(.30, .44, .20), soil=(.24, .18, .12), grass=(.45, .52, .30),
    neighbour=(.62, .40, .30), context=(.80, .78, .72), car=(.20, .36, .30), car2=(.78, .72, .56), car3=(.70, .70, .72), tyre=(.07, .07, .07),
    pale=(.88, .88, .86), blue=(.20, .30, .40))


def manifest(version):
    h = 12.0
    cams = G.camera_roster(XE - XCW, LANE1 - YS, h, [
        ('storefront_close', (-2.0, -4.6, 1.8), (-2.0, 0.0, 2.6), 32),
        ('bracketed_cornice', (13.0, -3.2, 2.5), (16.0, 0.0, 8.8), 35),
        ('arched_windows', (25.4, -3.6, 3.2), (24.75, 0.0, 7.0), 35),
        ('corner_entrance', (-41.0, -6.0, 2.4), (-29.0, 0.0, 3.4), 32),
        ('angle_parking', (6.0, -22.0, 9.0), (8.0, -9.0, 0.0), 32),
        ('crosswalk_bulbout', (-12.0, -20.0, 6.5), (-28.0, -9.0, 0.0), 30),
        ('street_furniture', (-8.0, -10.6, 1.7), (-14.0, -4.6, 1.6), 30),
        ('sidewalk_section', (-20.0, -3.0, 1.7), (20.0, -2.4, 2.4), 26),
        ('roof_parapets', (-6.0, -14.0, 22.0), (2.0, 10.0, 9.0), 30),
        ('rear_lane', (-30.0, 28.0, 2.2), (10.0, 24.0, 4.5), 28)])
    for c in cams:
        if c['name'] == 'front':                                               # the locked front: eye level at the east bulb-out, looking west along the north sidewalk
            c.update(location=(38.5, -10.0, 1.7), target=(6.0, -1.5, 4.6), lens=22, whole=False)
        elif c['name'] == 'front_corner':                                      # the locked oblique: high over the south-west corner, looking up the street
            c.update(location=(-46.0, -32.0, 32.0), target=(-6.0, 2.0, 0.0), lens=30, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(36.0, -60.0, 46.0), target=(-4.0, -4.0, 0.0), lens=28, whole=False)
        elif c['name'] == 'top':                                               # the locked top view: north blocks above, the street below
            c.update(location=(-1.7, 9.5, 140.0), target=(-1.7, 9.501, 0.0), ortho_scale=75.0, whole=False)
        elif c['name'] == 'left_side':                                         # down the cross street from the south-west
            c.update(location=(-46.0, -48.0, 9.0), target=(-34.0, 6.0, 3.0), lens=26, whole=False)
        elif c['name'] == 'right_side':                                        # along the street from the east, raised
            c.update(location=(58.0, -14.0, 14.0), target=(0.0, -6.0, 3.0), lens=26, whole=False)
        elif c['name'] == 'rear':                                              # from over the back lane
            c.update(location=(4.0, 52.0, 24.0), target=(4.0, 8.0, 4.0), lens=26, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(-62.0, 46.0, 30.0), target=(-4.0, 2.0, 2.0), lens=28, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='inglewood_main_street/variant_0, modelled as Calgary\'s 9 Avenue SE in Inglewood',
        measurement_contract=dict(dimensions_m=dict(width=XE - XCW, depth=LANE1 - YS, height=h),
            observed_storeys=2, storey_programme='street option: a main-street section; the two-storey commercial blocks are the street wall it is read with',
            plan=f'{2 * -YC:.1f} m building line to building line (top view), 76 m run of the north street wall from the cross street, a back lane behind',
            section_m=dict(north_sidewalk=[0.0, -SW], north_parking_angled=[-SW, -(SW + PK)], north_travel_lane=[-(SW + PK), YC],
                           south_travel_lane=[YC, YC - LN], south_parking_angled=[YC - LN, YS + SW], south_sidewalk=[YS + SW, YS],
                           furnishing_strip=[-4.0, -5.3], curb_extension_depth=BULB, curb_height=SWZ),
            facade='pale scored concrete sidewalks, red brick-paver furnishing strips and crossings, young street trees, black lamp standards with red banners, angled parking with white stall lines, double yellow centre line; red-brick two-storey storefront blocks with cream stone and white trim, storefront glazing, sign bands and cornices',
            levels_m=[0.0, SWZ, 4.8, 9.2, 10.8], inferred='the south blocks, the lane and the buildings beyond it are context; the block interiors and rear walls are teaching assumptions'),
        roof_contract=dict(type='flat gravel and membrane roofs inside brick parapets with copings; a raised central parapet on the middle block', datum_m=9.0, crowns_m=[11.6]),
        identity_contract=dict(owner='Inglewood main street: a historic two-storey red-brick storefront street wall over wide sidewalks with brick furnishing strips, trees and banner lamps, angled parking each side, curb extensions and brick crossings'),
        material_contract=dict(profile='source-palette clay: red-orange brick, cream stone and white trim, dark green storefront frames, pale concrete, red brick pavers, dark asphalt with white and yellow markings, black lamp standards with red banners', textured_keeper=False),
        programme_contract=dict(storeys=2, ground='shops, galleries and cafes on the sidewalk', upper='offices and flats'),
        street_contract=dict(kind='fixed_native_section', width_m=-YS, axis='x', junction_finish='brick-paver crossings',
                             bands=['north_storefronts', 'north_sidewalk', 'furnishing_strip', 'angled_parking', 'travel_lane', 'centre_line', 'travel_lane', 'angled_parking', 'furnishing_strip', 'south_sidewalk', 'south_storefronts']),
        contact_contract=['Asphalt at grade zero', 'Sidewalks on the asphalt with a 150 mm curb', 'Building walls from grade with the sidewalk running under them', 'Trees and lamps in the furnishing strip'],
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


# ---- Inglewood main street ----

import random
from shapely.geometry import Polygon, LineString, box as sbox
from shapely.ops import unary_union

R_RET = 3.0                                     # curb-return radius at the cross street
TAPER_W, TAPER_E = (-17.5, -14.0), (28.0, 31.5) # bulb-out tapers (curb at -BULB to curb at -SW), west and east, as x pairs
R_TAPER = 2.0                                   # fillet radius rounding both ends of each taper (reverse curves, not chamfers)
LINE_X0, LINE_N, LINE_P = -13.5, 11, 3.5        # first stall line at the north curb, line count, spacing along the curb
STALL_DX = PK / math.tan(math.radians(50.0))    # 50-degree angled stalls: lean of a stall line across the parking lane
XCROSS = (-28.2, -25.8)                         # brick crossing over the main street at the intersection
LADDER = (32.5, 35.5)                           # mid-block ladder crossing at the east bulb-out
CL_X = (XCW + XCE) / 2                          # cross-street centre line


def mirror(pts):
    """The south side is the north side reflected about the centre line."""
    return [(x, YS - y) for x, y in pts]


def arc(cx, cy, r, a0, a1, n=8):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def chamfer_outline():
    """The north sidewalk in plan with straight tapers: under the building line, the west sidewalk of the cross street
    up to the lane, the corner curb return, the west curb extension and its taper, the straight curb, the east taper
    and extension."""
    pts = [(XCE, LANE0 + .05), (XW + .2, LANE0 + .05), (XW + .2, .2), (XE, .2), (XE, -BULB), (TAPER_E[1], -BULB), (TAPER_E[0], -SW),
           (TAPER_W[1], -SW), (TAPER_W[0], -BULB)]
    pts += arc(XCE + R_RET, -BULB + R_RET, R_RET, -90.0, -180.0)
    return pts


def taper_zones():
    return [sbox(TAPER_W[0] - 4.0, -BULB - 1.0, TAPER_W[1] + 4.0, -SW + 1.2), sbox(TAPER_E[0] - 4.0, -BULB - 1.0, TAPER_E[1] + 4.0, -SW + 1.2)]


def sidewalk_poly():
    """The north sidewalk polygon with each taper rounded into smooth reverse curves (opening rounds the convex bulb
    corner, closing the concave corner at the main curb); everything outside the taper zones is unchanged."""
    p = Polygon(chamfer_outline())
    r = p.buffer(-R_TAPER, join_style=1).buffer(R_TAPER, join_style=1).buffer(R_TAPER, join_style=1).buffer(-R_TAPER, join_style=1)
    z = unary_union(taper_zones())
    out = unary_union([r.intersection(z), p.difference(z)]).buffer(0)
    if out.geom_type != 'Polygon':
        out = max(out.geoms, key=lambda g: g.area)
    return out.simplify(.005)


def ring(poly):
    pts = list(poly.exterior.coords)[:-1]
    return [(round(x, 4), round(y, 4)) for x, y in pts]


def north_sidewalk_outline():
    return ring(sidewalk_poly())


def curb_line():
    """The curb edge of the north sidewalk from the cross-street crossing round the corner return, along the west
    curb extension, the taper, the main curb, the east taper and the east extension."""
    p = sidewalk_poly()
    edge = p.exterior.intersection(sbox(XCE - 1.0, -BULB - 1.0, XE + 1.0, -.6).difference(sbox(XCE + .05, -SW + .1, XE - .05, 1.0)))
    edge = edge.difference(sbox(XE - .05, -BULB - 1.0, XE + 1.0, 1.0))
    return edge.difference(sbox(XCE - 1.0, -1.2, XCE + .3, 1.0))


def brick_band():
    """The furnishing-strip brick band following the curb: 1.3 m wide (0.3..1.6 m from the curb face) on the main run,
    narrowing to 0.7 m round the curb extensions, whose bodies are pale scored concrete."""
    p = sidewalk_poly()
    cl = curb_line()
    wide = p.intersection(cl.buffer(1.6, cap_style=2)).difference(cl.buffer(.3, cap_style=2))
    narrow = p.intersection(cl.buffer(1.0, cap_style=2)).difference(cl.buffer(.3, cap_style=2))
    main = sbox(TAPER_W[1] - .2, -SW - .05, TAPER_E[0] + .2, 0.0)
    band = unary_union([wide.intersection(main), narrow.difference(main)]).buffer(0)
    return [g for g in getattr(band, 'geoms', [band]) if g.area > .05]


def west_sidewalk_outline(ytop=LANE1 + 14.0):
    """The sidewalk on the far (west) side of the cross street, with its own corner return."""
    pts = [(-62.0, ytop), (XCW, ytop)]
    pts += arc(XCW - R_RET, -SW + R_RET, R_RET, 0.0, -90.0)
    pts += [(-62.0, -SW)]
    return pts


def ground():
    # One asphalt sheet in plan: the main street crossed by the cross street, running under the curbs by 0.4 m.
    C.prism('Street asphalt', [(-62.0, -SW + .4), (XCW - .4, -SW + .4), (XCW - .4, LANE1 + 14.0), (XCE + .4, LANE1 + 14.0), (XCE + .4, -SW + .4),
                               (XE, -SW + .4), (XE, YS + SW - .4), (XCE + .4, YS + SW - .4), (XCE + .4, YS - 25.6), (XCW - .4, YS - 25.6),
                               (XCW - .4, YS + SW - .4), (-62.0, YS + SW - .4)], 'z', 0.0, .02, 'asphalt', 'street')
    C.prism('Back lane', [(XCE + .3, LANE0), (XE, LANE0), (XE, LANE1), (XCE + .3, LANE1)], 'z', .001, .018, 'lane', 'street')
    C.prism('North sidewalk', north_sidewalk_outline(), 'z', .005, SWZ, 'concrete', 'sidewalks')
    C.prism('South sidewalk', mirror(north_sidewalk_outline()), 'z', .005, SWZ, 'concrete', 'sidewalks')
    C.prism('North-west sidewalk', west_sidewalk_outline(), 'z', .005, SWZ, 'concrete', 'sidewalks')
    C.prism('South-west sidewalk', mirror(west_sidewalk_outline(25.6)), 'z', .005, SWZ, 'concrete', 'sidewalks')
    C.prism('Cross-street sidewalk beyond the lane', [(XCE, LANE1 - .05), (XW + .2, LANE1 - .05), (XW + .2, LANE1 + 14.0), (XCE, LANE1 + 14.0)], 'z', .005, SWZ, 'concrete', 'sidewalks')


def markings():
    """White and yellow road markings, lifted 1 cm-scale above the asphalt; brick-paver crossings."""
    b = Batch()
    zm = .0235                                                                                 # marking centre: 19..28 mm, through the asphalt top
    for y in (YC - .1, YC + .1):                                                               # double yellow centre line
        b.box('yellow', (XCROSS[1] + .6 + LADDER[0] - .6) / 2, y, zm, LADDER[0] - XCROSS[1] - 1.2, .1, .009)
        b.box('yellow', (LADDER[1] + .6 + XE) / 2, y, zm, XE - LADDER[1] - .6, .1, .009)
        b.box('yellow', (-62.0 + XCW - .6) / 2, y, zm, XCW - .6 + 62.0, .1, .009)
    for y0, y1 in ((-1.4, LANE1 + 14.0), (YS - 25.6, YS + 1.5)):                              # cross-street centre line, stopping short of the crossings
        b.box('yellow', CL_X, (y0 + y1) / 2, zm, .1, y1 - y0, .009)
    for side in (1, -1):                                                                       # angled stalls and parking edge lines both sides
        for k in range(LINE_N):
            if side == 1:
                xc = LINE_X0 + k * LINE_P
                b.beam('marking', (xc, -SW - .08, zm), (xc + STALL_DX, -SW - PK + .1, zm), .1, .009)
            else:
                xc = LINE_X0 + 4.0 + k * LINE_P
                b.beam('marking', (xc, YS + SW + .08, zm), (xc - STALL_DX, YS + SW + PK - .1, zm), .1, .009)
        ye = -SW - PK + .05 if side == 1 else YS + SW + PK - .05
        b.box('marking', (TAPER_W[1] - .3 + TAPER_E[0] + 1.6) / 2, ye, zm, TAPER_E[0] + 1.6 - TAPER_W[1] + .3, .1, .009)
    # Brick-paver crossing over the main street at the intersection, with white edge lines, running into both curb extensions.
    b.box('paver', (XCROSS[0] + XCROSS[1]) / 2, YC, .022, XCROSS[1] - XCROSS[0], -YS - 2 * BULB + .1, .006)
    for x in XCROSS:
        b.box('marking', x + (-.15 if x == XCROSS[0] else .15), YC, .0235, .2, -YS - 2 * BULB + .1, .009)
    # Brick-paver crossings over the cross street, north and south of the intersection.
    for ya, yb in ((-4.6, -2.0), (YS + 2.0, YS + 4.6)):
        b.box('paver', CL_X, (ya + yb) / 2, .022, XCE - XCW + .1, yb - ya, .006)
        for y in (ya - .15, yb + .15):
            b.box('marking', CL_X, y, .0235, XCE - XCW + .1, .2, .009)
    # Mid-block ladder crossing at the east curb extensions.
    n = int((-YS - 2 * BULB) / .8)
    for i in range(n):
        y = -BULB - .4 - i * .8
        if y - .2 > YS + BULB:
            b.box('marking', (LADDER[0] + LADDER[1]) / 2, y, zm, LADDER[1] - LADDER[0], .42, .009)
    for x in (LADDER[0] - .1, LADDER[1] + .1):
        b.box('marking', x, YC, zm, .15, -YS - 2 * BULB + .1, .009)
    b.box('paver', (LADDER[0] + LADDER[1]) / 2, YC, .022, LADDER[1] - LADDER[0] + .02, -YS - 2 * BULB + .1, .006)   # brick band under the ladder
    b.flush('road markings')


def lamp(b, x, y, toward):
    """Black lamp standard on a base with an acorn lantern and two banner arms carrying a red banner toward the road."""
    z = SWZ
    b.box('hardware', x, y, z + .18, .34, .34, .4)
    b.box('hardware', x, y, z + 2.5, .12, .12, 4.6)
    b.box('hardware', x, y, z + 4.86, .26, .26, .14)
    b.box('pale', x, y, z + 5.2, .32, .32, .55)
    b.box('hardware', x, y, z + 5.52, .4, .4, .1)
    b.box('hardware', x, y, z + 5.66, .08, .08, .2)
    for zz in (2.6, 3.9):
        b.box('hardware', x, y + toward * .4, z + zz, .05, .7, .05)
    b.box('banner', x, y + toward * .45, z + 3.25, .02, .55, 1.22)


def bin_(b, x, y):
    b.box('hardware', x, y, SWZ + .46, .5, .5, .92)
    b.box('dark', x, y, SWZ + .95, .56, .56, .08)


def bike_hoop(b, x, y):
    for dx in (-.35, .35):
        b.box('hardware', x + dx, y, SWZ + .45, .05, .05, .92)
    b.box('hardware', x, y, SWZ + .89, .75, .05, .05)


def bench(b, x, y, along='x'):
    if along == 'x':
        b.box('timber', x, y, SWZ + .46, 1.8, .45, .06)
        b.box('timber', x, y + .22, SWZ + .74, 1.8, .05, .36)
        for s in (-1, 1):
            b.box('hardware', x + s * .75, y, SWZ + .22, .06, .45, .48)
    else:
        b.box('timber', x, y, SWZ + .46, .45, 1.8, .06)
        b.box('timber', x - .22, y, SWZ + .74, .05, 1.8, .36)
        for s in (-1, 1):
            b.box('hardware', x, y + s * .75, SWZ + .22, .45, .06, .48)


def car(b, x, y, ux, uy, role):
    """A plain clay car: body, glass cabin with a roof, four wheels; axis (ux, uy), nose at the curb."""
    vx, vy = -uy, ux
    a = (x - ux * 2.25, y - uy * 2.25)
    f = (x + ux * 2.25, y + uy * 2.25)
    b.beam(role, (a[0], a[1], .64), (f[0], f[1], .64), 1.78, .64)
    b.beam('dark', (x - ux * 1.25, y - uy * 1.25, 1.14), (x + ux * .95, y + uy * .95, 1.14), 1.6, .46)
    b.beam(role, (x - ux * 1.2, y - uy * 1.2, 1.385), (x + ux * .9, y + uy * .9, 1.385), 1.52, .06)
    for s in (-1.42, 1.42):
        for t in (-.8, .8):
            cx, cy = x + ux * s + vx * t, y + uy * s + vy * t
            b.beam('tyre', (cx - vx * .13, cy - vy * .13, .335), (cx + vx * .13, cy + vy * .13, .335), .62, .62)


def furniture():
    """Brick furnishing strips at the curb with tree pits, lamps, bins and bike hoops; brick pads on the curb
    extensions; scored sidewalk joints; young street trees; benches; parked cars."""
    b = Batch()
    for side in (1, -1):
        def Y(y):
            return y if side == 1 else YS - y
        for x in (-24.0, 42.0):                                                              # small brick pads under the benches
            b.box('paver', x, Y(-SW - .9), SWZ + .002, 2.4, 1.1, .012)
        for k in range(int((XE - XCE) / 1.6)):                                              # scored joints across the sidewalk
            x = XCE + .8 + k * 1.6
            b.box('sidejoint', x, Y(-1.95), SWZ, .02, 3.8, .004)
        b.box('sidejoint', (XW + .4 + XE) / 2, Y(-2.0), SWZ, XE - XW - .4, .02, .004)
        for k in range(15):                                                                  # and along the cross-street sidewalk
            y = Y(1.2 + k * 1.6)
            b.box('sidejoint', (XCE + XW) / 2, y, SWZ, XW - XCE - .1, .02, .004)
        for x in ((-10.5, 6.0, 23.5) if side == 1 else (-6.0, 11.0, 26.0)):                   # tree pits
            b.box('soil', x, Y(-4.65), SWZ + .0045, 1.2, 1.2, .012)
            street_tree(x, Y(-4.65), z=SWZ + .008, height=5.6, spread=.9)
        for x in ((-20.0, -2.5, 14.5, 44.5) if side == 1 else (-21.0, 2.5, 18.5, 38.0)):
            lamp(b, x, Y(-4.7) if -14.0 < x < 28.0 else Y(-BULB + .8), -side)
        for x in ((-6.0, 19.0) if side == 1 else (-1.0, 22.5)):
            bin_(b, x, Y(-4.65))
        for x in ((-15.0, -14.0) if side == 1 else (5.0, 6.0)):
            bike_hoop(b, x + 3.0, Y(-4.65))
        bench(b, -24.0, Y(-SW - .9), 'x')
        bench(b, 42.0, Y(-SW - .9), 'x')
    street_tree(XCE + 1.6, 6.0, z=SWZ + .008, height=5.4, spread=.9)
    b.box('soil', XCE + 1.6, 6.0, SWZ + .0045, 1.2, 1.2, .012)
    street_tree(XCE + 1.6, YS - 6.0, z=SWZ + .008, height=5.4, spread=.9)
    b.box('soil', XCE + 1.6, YS - 6.0, SWZ + .0045, 1.2, 1.2, .012)
    lamp(b, XCE + .9, -BULB + 2.6, -1)
    lamp(b, XCW - .9, -SW + 1.2, -1)
    # Scored joints on the pale concrete of the curb extensions, clipped to the concrete inside the brick band.
    band = unary_union(brick_band())
    bulbs = sidewalk_poly().intersection(sbox(XCE + .3, -BULB - .1, XE - .05, -SW - .02)).difference(band.buffer(.05))
    for k in range(int((XE - XCE) / 1.5) + 1):
        ln = LineString([(XCE + .75 + k * 1.5, -BULB - .2), (XCE + .75 + k * 1.5, -SW)]).intersection(bulbs)
        for g in getattr(ln, 'geoms', [ln]):
            if g.length > .1:
                (ax, ay), (bx, by) = g.coords[0], g.coords[-1]
                for s in (1, -1):
                    yy0, yy1 = (ay, by) if s == 1 else (YS - ay, YS - by)
                    b.box('sidejoint', ax, (yy0 + yy1) / 2, SWZ, .02, abs(yy1 - yy0), .004)
    for yj in (-SW - 1.5, -SW - 3.0):
        ln = LineString([(XCE, yj), (XE, yj)]).intersection(bulbs)
        for g in getattr(ln, 'geoms', [ln]):
            if g.length > .1:
                (ax, ay), (bx, by) = g.coords[0], g.coords[-1]
                for s in (1, -1):
                    b.box('sidejoint', (ax + bx) / 2, yj if s == 1 else YS - yj, SWZ, abs(bx - ax), .02, .004)
    b.flush('street furniture')
    for i, g in enumerate(brick_band()):                                                        # the brick band, north and south
        pts = ring(g)
        C.prism(f'North brick band {i}', pts, 'z', SWZ - .004, SWZ + .008, 'paver', 'sidewalks')
        C.prism(f'South brick band {i}', mirror(pts), 'z', SWZ - .004, SWZ + .008, 'paver', 'sidewalks')
    c = Batch()
    ux, uy = STALL_DX / math.hypot(STALL_DX, PK), -PK / math.hypot(STALL_DX, PK)
    for k, role in ((7, 'car'), (9, 'car2')):                                                   # two cars nose-in on the north side (top view)
        xc = LINE_X0 + (k + .5) * LINE_P
        car(c, xc + ux * 2.85, -SW + uy * 2.85, -ux, -uy, role)
    for k, role in ((2, 'car3'), (6, 'car')):
        xc = LINE_X0 + 4.0 + (k + .5) * LINE_P
        car(c, xc - ux * 2.85, YS + SW - uy * 2.85, ux, uy, role)
    c.flush('parked cars')


# ---- the north street wall ----

def arch_head(f, h, rise, ring=.22, segs=14, ring_role='stone', proud=.03):
    """Segmental or round head on a rectangular cut: a brick spandrel infill fills the cut's corners above the curve,
    flush with the wall face, and a proud ring follows the curve."""
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


GZ0, GH = .70, 3.05                             # storefront glazing: bulkhead top and glazing height (head at 3.75)
DZ0 = .17                                       # door sill above the sidewalk
SIGN0, SIGN1 = 3.92, 4.52                       # sign band
BELT = 4.70                                     # belt course centre
FLOOR2 = 4.62                                   # upper floor level (top of slab)

XLB = -20.4                                     # the corner block ends here; a lower one-storey bay runs on to the middle block (top view)
BLOCKS = [
    dict(name='Corner block', x0=XW, x1=XLB, dy=0.0, top=9.8, depth=24.9, pil='stone', sign='frame', letters='cream',
         pattern=['door+shop', 'shop', 'shop+door'], up_per_bay=2, pair_gap=.3, up=(5.45, 1.05, 2.25), head='flat', cornice='white', frame='frame'),
    dict(name='Lower bay', x0=XLB, x1=-11.25, dy=.015, top=6.6, depth=24.6, pil='brick', sign='frame', letters='cream', roof='membrane',
         pattern=['shop+door', 'shop'], up=None, head='flat', cornice='stone', frame='frame'),
    dict(name='Middle block', x0=-11.25, x1=10.0, dy=.03, top=10.4, depth=24.4, pil='cream', sign='cream', letters='sign',
         pattern=['shop', 'shop+door', 'door', 'door+shop', 'shop'], up_per_bay=2, up=(5.45, 1.0, 2.35), head='seg', rise=.13, cornice='white_modillion', frame='frame'),
    dict(name='Arched block', x0=10.0, x1=21.0, dy=0.0, top=9.2, depth=23.0, pil='brick', sign='sign', letters='cream',
         pattern=['shop+door', 'shop', 'door+shop'], up_n=5, up=(5.35, .95, 2.25), head='seg', cornice='bracketed', frame='frame'),
    dict(name='Fine art block', x0=21.0, x1=28.5, dy=.03, top=10.0, depth=24.0, pil='cream', sign='cream', letters='sign',
         pattern=['shop', 'door+shop'], up_n=3, up=(5.4, 1.15, 2.6), head='round', cornice='corbel', frame='frame'),
    dict(name='Cafe block', x0=28.5, x1=38.0, dy=0.0, top=12.4, depth=24.8, pil='stone', sign='stone', letters='dark',
         pattern=['shop+door', 'shop'], up_per_bay=2, up=(5.7, 1.2, 3.3), head='flat', cornice='stone', frame='dark'),
]


def ground_bays(spec):
    """Pilaster centres and ground openings across a block front (u = x)."""
    x0, x1 = spec['x0'], spec['x1']
    n = len(spec['pattern'])
    pc = [x0 + .21 + k * (x1 - x0 - .42) / n for k in range(n + 1)]
    holes = []
    for k, kind in enumerate(spec['pattern']):
        a, c = pc[k] + .21, pc[k + 1] - .21
        nm = f"{spec['name']} bay {k}"
        if kind == 'shop':
            holes.append(hole(nm + ' shopfront', (a + c) / 2, GZ0, c - a - .5, GH, kind='shop'))
        elif kind == 'door':
            holes.append(hole(nm + ' double door', (a + c) / 2, DZ0, 1.7, GZ0 + GH - DZ0, kind='door'))
            for s in (-1, 1):
                w = (c - a - 1.7) / 2 - .5
                if w > .5:
                    holes.append(hole(nm + f' sidelight {s:+d}', (a + c) / 2 + s * (.85 + .25 + w / 2), GZ0, w, GH, kind='shop'))
        else:
            left = kind.startswith('door')
            du = a + .25 + .55 if left else c - .25 - .55
            holes.append(hole(nm + ' door', du, DZ0, 1.1, GZ0 + GH - DZ0, kind='door'))
            sa, sc = (du + .55 + .3, c - .25) if left else (a + .25, du - .55 - .3)
            holes.append(hole(nm + ' shopfront', (sa + sc) / 2, GZ0, sc - sa, GH, kind='shop'))
    return pc, holes


def upper_holes(spec, pc):
    if not spec['up']:
        return []
    z, w, h = spec['up']
    us = []
    if 'pair_gap' in spec:                                                                 # tight pairs split by a brick mullion pier
        for k in range(len(pc) - 1):
            mid = (pc[k] + pc[k + 1]) / 2
            us += [mid - (w + spec['pair_gap']) / 2, mid + (w + spec['pair_gap']) / 2]
    elif 'up_per_bay' in spec:
        for k in range(len(pc) - 1):
            mid = (pc[k] + pc[k + 1]) / 2
            bw = pc[k + 1] - pc[k]
            for j in range(spec['up_per_bay']):
                us.append(mid - bw / 2 + bw * (j + .5) / spec['up_per_bay'])
    else:
        n = spec['up_n']
        a, c = spec['x0'] + .9, spec['x1'] - .9
        us = [a + (c - a) * (j + .5) / n for j in range(n)]
    return [hole(f"{spec['name']} upper {i}", u, z, w, h) for i, u in enumerate(us)]


def letters(m, u0, u1, z, d, role, seed):
    """Abstract sign lettering: a run of small proud letter blocks in two words."""
    rng = random.Random(seed)
    u = u0
    while u < u1:
        lw = rng.uniform(.10, .2)
        if u + lw > u1:
            break
        m.box(role, u + lw / 2, d, z, lw, .025, rng.choice((.26, .3, .34)))
        u += lw + rng.choice((.05, .06, .07, .07, .32))


def storefront(spec, m, f, pc, gh):
    """Pilasters with capitals, glazing frames, transoms, bulkheads, doors and thresholds, sign band and lettering."""
    x0, x1 = spec['x0'], spec['x1']
    corner = spec['name'] == 'Corner block'
    zs = .01 if spec['dy'] else 0.0                                                        # neighbouring blocks' capitals and plinths never share a plane
    cap = 'stone' if spec['pil'] != 'cream' else 'cream'
    for k, u in enumerate(pc):
        if corner and k == 0:
            continue                                                                        # the corner pier replaces it
        m.box(spec['pil'], u, -.1, (.05 + SIGN0 - .04) / 2, .42, .22, SIGN0 - .09)
        m.box(cap, u, -.135, SIGN0 - .12 + zs, .54, .29, .2)
        m.box(cap, u, -.125, .205 + zs, .5, .27, .29)                                       # plinth block
    fr = spec['frame']
    for h in gh:
        if h['kind'] == 'shop':
            cols = max(1, round(h['w'] / 1.25))
            framed(m, f, h, cols=cols, rows=1, inset=.14, occupied='shop', kind='shopfront', frame=fr)
            m.box(fr, h['u'], .12, h['z'] + h['h'] - .72, h['w'] - .12, .09, .07)          # transom bar
            m.box(fr, h['u'], -.015, (.06 + GZ0 - .05) / 2, h['w'] + .05, .04, GZ0 - .11)  # panelled bulkhead
            n = max(1, round(h['w'] / 1.6))
            for k in range(n):                                                              # raised panel moulding
                pu = h['u'] - h['w'] / 2 + h['w'] * (k + .5) / n
                m.box(fr, pu, -.05, (.06 + GZ0 - .05) / 2, h['w'] / n - .3, .02, GZ0 - .33)
            m.box('stone', h['u'], -.05, GZ0 - .045, h['w'] + .12, .14, .08)                  # sill
        else:
            framed(m, f, h, cols=2 if h['w'] > 1.4 else 1, rows=1, inset=.16, occupied='shop', kind='door', frame=fr)
            m.box(fr, h['u'], .15, 2.92, h['w'] - .12, .09, .07)                           # transom bar over the leaf
            m.box(fr, h['u'], .19, DZ0 + .5, h['w'] - .14, .05, .8)                          # kick panel
            m.box('stone', h['u'], T / 2, DZ0 + .005, h['w'] - .02, T - .04, .03)            # threshold
    if not corner:                                                                          # the corner block's bands are runs that turn the corner (corner_bands)
        m.box(spec['sign'], (x0 + x1) / 2, -.07, (SIGN0 + SIGN1) / 2, x1 - x0 - .03, .16, SIGN1 - SIGN0)
        m.box('stone' if spec['sign'] != 'cream' else 'cream', (x0 + x1) / 2, -.1, SIGN1 + .04, x1 - x0 - .03, .26, .12)
        m.box('stone', (x0 + x1) / 2, -.06, BELT + .01, x1 - x0 - .03, .17, .2)
    letters(m, x0 + (x1 - x0) * .22, x0 + (x1 - x0) * .78, (SIGN0 + SIGN1) / 2, -.16, spec['letters'], int(x0 * 10))


def upper(spec, m, f, uh):
    for h in uh:
        framed(m, f, h, cols=1, rows=2, inset=.15, occupied='upper room', kind='window', frame='white' if spec['frame'] == 'frame' else 'dark')
        m.box('stone', h['u'], -.05, h['z'] - .055, h['w'] + .22, .14, .1)                     # sill
        if spec['head'] == 'flat':
            m.box('stone', h['u'], -.02, h['z'] + h['h'] + .155, h['w'] + .3, .08, .3)          # lintel
        elif spec['head'] == 'seg':
            arch_head(f, h, spec.get('rise', .32), ring=.2, ring_role='stone' if spec['name'] == 'Middle block' else 'cream')
        else:
            arch_head(f, h, h['w'] / 2, ring=.22, ring_role='wall', proud=.04)                  # brick voussoir arch (front view)


def cornice(spec, m, top):
    x0, x1 = spec['x0'], spec['x1']
    lo, hi = x0 + .01, x1 - .01
    kind = spec['cornice']
    if kind == 'white':                                                                    # the corner block: runs that turn the corner (corner_bands)
        return
    if kind == 'white_modillion':
        eave_cornice(m, lo, hi, top - .55, span_t=T, proj=.55, role='white', modillions=True)
        m.box('white', (lo + hi) / 2, -.04, top - 1.55, hi - lo, .12, .26)                    # frieze band
    elif kind == 'bracketed':                                                              # dark pressed-metal cornice on scrolled brackets
        eave_cornice(m, lo, hi, top - .2, span_t=T, proj=.8, role='dark', modillions=True)
        m.box('dark', (lo + hi) / 2, -.06, top - 1.15, hi - lo, .16, .5)                      # frieze panel
        a, c = spec['x0'] + .9, spec['x1'] - .9
        for u in (lo + .25, hi - .25, a + (c - a) * 2 / spec['up_n']):                       # the middle console sits between two windows
            m.box('dark', u, -.36, top - .95, .3, .76, .9)                                     # end and middle consoles
            m.box('dark', u, -.25, top - 1.55, .22, .54, .4)
    elif kind == 'corbel':                                                                 # corbelled brick table under a stone coping
        n = int((hi - lo) / .45)
        for i in range(n):
            u = lo + .25 + (hi - lo - .5) * i / max(1, n - 1)
            m.box('wall', u, -.08, top - 1.05, .23, .2, .3)
        m.box('wall', (lo + hi) / 2, -.06, top - .78, hi - lo, .16, .24)
        m.box('wall', (lo + hi) / 2, -.11, top - .58, hi - lo, .26, .16)
        m.box('stone', (lo + hi) / 2, -.05, top - 1.45, hi - lo, .14, .14)                    # stone band below
    else:                                                                                  # stone cornice band
        m.box('stone', (lo + hi) / 2, -.12, top - .55, hi - lo, .3, .3)
        m.box('stone', (lo + hi) / 2, -.05, top - 1.35, hi - lo, .14, .16)
    m.box('white' if kind == 'white_modillion' else 'stone', (lo + hi) / 2, T / 2 - .03, top + .04, hi - lo, T + .14, .1)    # coping
    if spec['name'] == 'Middle block':                                                     # raised central parapet with a name panel
        mid = (x0 + x1) / 2
        for w, za, z1, t in ((7.0, top - .02, top + 1.1, T - .01), (3.6, top + .3, top + 2.05, T - .02)):
            m.box('wall', mid, T / 2, (za + z1) / 2, w, t, z1 - za)
            m.box('white', mid, T / 2 - .03, z1 + .04, w + .14, T + .14, .1)
        m.box('cream', mid, -.02, top + .85, 3.2, .08, .75)
        letters(m, mid - 1.35, mid + 1.35, top + .85, -.065, 'sign', 77)
    if spec['name'] == 'Cafe block':                                                       # cream stone end pier with a capital (front view)
        m.box('cream', x1 - .32, -.14, (.05 + top - .6) / 2, .64, .3, top - .65)
        m.box('cream', x1 - .34, -.2, top - .52, .76, .42, .3)


def block(spec):
    x0, x1, dy, top, depth = spec['x0'], spec['x1'], spec['dy'], spec['top'], spec['depth']
    f = C.Face((0.0, dy, 0.0), (1, 0, 0), (0, 1, 0), spec['name'])
    pc, gh = ground_bays(spec)
    uh = upper_holes(spec, pc)
    z0 = .003 if dy else 0.0
    f.wall(f"{spec['name']} street carrier", x0, x1 + .01, z0, top, depth=T, role='wall', holes=gh + uh)
    G.brick_courses(f, x0 + .02, x1 - .02, GZ0 - .1, top - .12, gh + uh, spacing=.16)
    m = Merge(f)
    storefront(spec, m, f, pc, gh)
    upper(spec, m, f, uh)
    cornice(spec, m, top)
    # A blade sign on a bracket over the sidewalk.
    bu = pc[1] if len(pc) > 2 else (x0 + x1) / 2
    m.box('hardware', bu, -.49, SIGN1 + .25, .05, 1.02, .05)
    m.box(spec['sign'] if spec['sign'] != 'stone' else 'frame', bu, -.62, SIGN1 - .135, .05, .7, .73)
    m.flush(spec['name'])
    # Rear wall with service doors and windows, roof, floors, an interior back-of-shop wall and room lights.
    rz = top - .9
    rear_wall(spec)
    b = Batch()
    b.box(spec.get('roof', 'roof'), (x0 + x1) / 2, (dy + T - .05 + depth - T + .05) / 2, rz - .125, x1 - x0 - .3, depth - 2 * T + .1 - dy, .25)
    if top > 8.0:
        b.box('floor', (x0 + x1) / 2, (dy + T - .05 + depth - T + .05) / 2, FLOOR2 - .15, x1 - x0 - .3, depth - 2 * T + .1 - dy, .3)
    b.box('floor', (x0 + x1) / 2, (dy + T - .05 + depth - T + .05) / 2, .085, x1 - x0 - .3, depth - 2 * T + .1 - dy, .11)
    b.box('interior', (x0 + x1) / 2, 9.5, (.13 + FLOOR2 - .29) / 2, x1 - x0 - .3, .15, FLOOR2 - .29 - .13)
    for i, (hx, hy) in enumerate(((.3, .55), (.62, .4))):                                     # rooftop units
        ux, uy = x0 + (x1 - x0) * hx, depth * hy
        b.box('membrane', ux, uy, rz + .38, 1.4, 1.1, .8)
        b.box('hardware', ux, uy, rz + .82, 1.0, .7, .1)
    if spec['name'] == 'Middle block':
        for ux in (-4.0, 2.5):                                                                 # skylights
            b.box('pale', ux, 12.0, rz + .18, 1.2, 2.4, .4)
            b.box('glass', ux, 12.0, rz + .4, 1.0, 2.2, .06)
    b.flush(spec['name'] + ' body')
    C.qa_room_light(f"{spec['name']} shop", ((x0 + x1) / 2, 4.5, 2.6), 90, 3.0)
    if top > 8.0:
        C.qa_room_light(f"{spec['name']} upper", ((x0 + x1) / 2, 4.5, FLOOR2 + 2.3), 60, 3.0)


def rear_wall(spec):
    """The rear (lane) wall as a coursed brick carrier with cut openings: a service door and upper sashes in framed,
    glazed reveals under flat stone lintels on stone sills (one-storey bays get ground windows instead)."""
    x0, x1, top, depth = spec['x0'], spec['x1'], spec['top'], spec['depth']
    ra, rb = (XW if x0 == XW else x0 - .15), x1 + .15
    f = C.Face((0.0, depth, 0.0), (-1, 0, 0), (0, -1, 0), spec['name'] + ' rear')
    hs = [hole(f"{spec['name']} rear door", -(x0 + 1.4), .05, 1.0, 2.2, kind='door')]
    zw, hw = (5.7, 1.8) if top > 8.0 else (1.0, 1.4)
    hs += [hole(f"{spec['name']} rear window {i}", -u, zw, 1.0, hw) for i, u in enumerate(x0 + 2.0 + i * 2.6 for i in range(int((x1 - x0 - 2.0) / 2.6)))]
    f.wall(f"{spec['name']} rear carrier", -rb, -ra, 0.0, top - .05, depth=T, role='wall', holes=hs)
    G.brick_courses(f, -rb + .02, -ra - .02, .12, top - .17, hs, spacing=.16)
    m = Merge(f)
    for h in hs:
        if h.get('kind') == 'door':
            framed(m, f, h, cols=1, rows=1, inset=.14, occupied='back of shop', kind='door', frame='frame')
            m.box('frame', h['u'], .17, .05 + .9, h['w'] - .14, .04, 1.2)                       # door leaf panel
        else:
            framed(m, f, h, cols=1, rows=2, inset=.13, occupied='upper room' if top > 8.0 else 'back of shop', frame='frame')
            m.box('stone', h['u'], -.05, h['z'] - .055, h['w'] + .22, .14, .1)                  # sill
        m.box('stone', h['u'], -.02, h['z'] + h['h'] + .155, h['w'] + .3, .08, .3)              # lintel
    m.flush(spec['name'] + ' rear')


def party_walls():
    b = Batch()
    for i in range(1, len(BLOCKS)):
        a, c = BLOCKS[i - 1], BLOCKS[i]
        x = a['x1']
        if a['name'] == 'Lower bay':
            continue                                                                       # the middle block's exposed side wall (side_wall)
        b.box('wall', x, (T - .05 + max(a['depth'], c['depth']) - .05) / 2, (max(a['top'], c['top']) - .03) / 2,
              T, max(a['depth'], c['depth']) - .05 - (T - .05), max(a['top'], c['top']) - .03)
    e = BLOCKS[-1]
    b.box('wall', e['x1'], (T - .05 + e['depth'] - .05) / 2, (e['top'] - .03) / 2, T, e['depth'] - .05 - (T - .05), e['top'] - .03)
    b.flush('party walls')


def side_wall():
    """The middle block's west wall, exposed above the lower bay's roof: coursed brick with punched upper windows
    and a stone coping (oblique view)."""
    s = next(b for b in BLOCKS if b['name'] == 'Middle block')
    lb = next(b for b in BLOCKS if b['name'] == 'Lower bay')
    top, depth, x = s['top'], s['depth'], s['x0']
    f = C.Face((x - T / 2, 0.0, 0.0), (0, -1, 0), (1, 0, 0), 'Middle block west')
    lo, hi = -(depth - .05), -(T - .05)
    hs = [hole(f'Middle west upper {i}', -y, 7.1, 1.0, 1.9) for i, y in enumerate((4.5, 9.5, 14.5, 19.5))]
    f.wall('Middle block west carrier', lo, hi, 0.0, top - .03, depth=T, role='wall', holes=hs)
    G.brick_courses(f, lo + .02, hi - .02, lb['top'] + .12, top - .15, hs, spacing=.16)
    m = Merge(f)
    for h in hs:
        framed(m, f, h, cols=1, rows=2, inset=.15, occupied='upper room', frame='white')
        m.box('stone', h['u'], -.05, h['z'] - .055, h['w'] + .22, .14, .1)
        m.box('stone', h['u'], -.02, h['z'] + h['h'] + .155, h['w'] + .3, .08, .3)
    m.box('stone', (lo + hi) / 2, T / 2, top + .02, hi - lo, T + .12, .1)                        # coping
    m.flush('Middle block west')


def corner_bands(top):
    """(role, face-depth centre, thickness, z centre, height, west run end y) of the corner block's bands."""
    return [('frame', -.07, .16, (SIGN0 + SIGN1) / 2, SIGN1 - SIGN0, 11.6),           # sign band over the shopfronts
            ('stone', -.1, .26, SIGN1 + .04, .12, 11.6),                                 # its moulding
            ('stone', -.06, .17, BELT + .01, .2, None),                                  # belt course
            ('white', -.04, .12, top - 1.2, .3, None),                                   # frieze
            ('white', -.18, .4, top - .62, .26, None),                                   # corona
            ('white', -.22, .48, top - .41, .14, None),                                  # cap
            ('white', T / 2 - .03, T + .14, top + .04, .1, None)]                        # coping


def corner_west():
    """The corner block's side on the cross street: shopfronts by the corner, a side door, high windows, upper
    windows; the sign band, belt, cornice and coping run along the street front and turn the corner; the corner pier."""
    s = BLOCKS[0]
    top, depth = s['top'], s['depth']
    f = C.Face((XW, 0.0, 0.0), (0, -1, 0), (1, 0, 0), 'Corner block west')
    lo, hi = -(depth - T), -T
    hs = [hole('Corner west shopfront 0', -3.0, GZ0, 3.4, GH, kind='shop'), hole('Corner west shopfront 1', -7.4, GZ0, 3.4, GH, kind='shop'),
          hole('Corner west side door', -10.4, DZ0, 1.1, GZ0 + GH - DZ0, kind='door')]
    hs += [hole(f'Corner west high window {i}', u, 2.3, 1.2, 1.3, kind='high') for i, u in enumerate((-13.4, -16.6, -19.8))]
    hs += [hole('Corner west rear door', -22.6, DZ0, 1.1, 2.6, kind='door')]
    uh = [hole(f'Corner west upper {i}', -2.2 - i * 2.45, 5.45, 1.05, 2.25) for i in range(9)]
    f.wall('Corner block west carrier', lo, hi, 0.0, top, depth=T, role='wall', holes=hs + uh)
    G.brick_courses(f, lo + .02, hi - .02, GZ0 - .1, top - .12, hs + uh, spacing=.16)
    m = Merge(f)
    for h in hs:
        if h['kind'] == 'shop':
            framed(m, f, h, cols=3, rows=1, inset=.14, occupied='shop', kind='shopfront', frame='frame')
            m.box('frame', h['u'], .12, h['z'] + h['h'] - .72, h['w'] - .12, .09, .07)
            m.box('frame', h['u'], -.015, (.06 + GZ0 - .05) / 2, h['w'] + .05, .04, GZ0 - .11)
            m.box('stone', h['u'], -.05, GZ0 - .045, h['w'] + .12, .14, .08)
        elif h['kind'] == 'door':
            framed(m, f, h, cols=1, rows=1, inset=.16, occupied='shop', kind='door', frame='frame')
            m.box('frame', h['u'], .19, DZ0 + .5, h['w'] - .14, .05, .8)
            m.box('stone', h['u'], T / 2, DZ0 + .005, h['w'] - .02, T - .04, .03)
        else:
            framed(m, f, h, cols=2, rows=1, inset=.15, occupied='shop', frame='frame')
            m.box('stone', h['u'], -.05, h['z'] - .055, h['w'] + .2, .14, .1)
    for h in uh:
        framed(m, f, h, cols=1, rows=2, inset=.15, occupied='upper room', frame='white')
        m.box('stone', h['u'], -.05, h['z'] - .055, h['w'] + .22, .14, .1)
        m.box('stone', h['u'], -.02, h['z'] + h['h'] + .155, h['w'] + .3, .08, .3)
    for u in (-5.2, -9.4):                                                                 # pilasters between the side shopfronts
        m.box('stone', u, -.1, (.05 + SIGN0 - .04) / 2, .42, .22, SIGN0 - .09)
        m.box('stone', u, -.135, SIGN0 - .12, .54, .29, .2)
        m.box('stone', u, -.125, .205, .5, .27, .29)
    letters(m, -9.5, -2.0, (SIGN0 + SIGN1) / 2, -.16, 'cream', 11)
    m.flush('Corner block west')
    # Band runs in world coordinates: the street run starts at the west run's outer face and the west run starts at the
    # street run's back face, so the two meet edge to edge at the corner and never overlap.
    b = Batch()
    x1 = s['x1'] - .01
    for role, c, t, z, h, yend in corner_bands(top):
        xa = XW + c - t / 2
        b.box(role, (xa + x1) / 2, c, z, x1 - xa, t, h)
        y0, y1 = c + t / 2, (yend if yend else depth - T - .3)
        b.box(role, XW + c, (y0 + y1) / 2, z, t, y1 - y0, h)
    b.box('stone', XW + .12, .12, (.05 + SIGN0 - .04) / 2, .66, .66, SIGN0 - .09)                 # the corner pier wraps both faces
    b.box('stone', XW + .1, .1, SIGN0 - .12, .78, .78, .2)
    b.box('stone', XW + .1, .1, .205, .74, .74, .29)
    b.flush('Corner bands and pier')


def context():
    """South side blocks, the west corners across the cross street, and low buildings beyond the back lane."""
    b = Batch()
    for i, (xa, xb, h) in enumerate(((XW, -8.0, 8.6), (-8.0, 12.0, 9.6), (12.0, 28.0, 8.2), (28.0, XE, 9.2))):
        z0 = .002 * (1 + i % 2)
        xb2 = xb + (.01 if xb < XE else 0.0)
        b.box('neighbour' if i % 2 == 0 else 'wall', (xa + xb2) / 2, YS - 8.5, (z0 + h) / 2, xb2 - xa, 17.0, h - z0)
        b.box('white', (xa + xb) / 2, YS + .1, h - .55, xb - xa - .1, .24, .3)                      # cornice band
        b.box('white', (xa + xb) / 2, YS + .08, h + .03, xb - xa - .1, .2, .1)
        n = int((xb - xa) / 4.0)
        for k in range(n):
            u = xa + (xb - xa) * (k + .5) / n
            b.box('glass', u, YS + .005, 2.1, 3.0, .02, 2.8)                                     # storefronts
            b.box('frame', u, YS + .01, 3.85, 3.3, .03, .5)                                      # sign band
            for j in (-1, 1):
                b.box('glass', u + j * .9, YS + .005, 6.3, 1.0, .02, 1.9)
                b.box('white', u + j * .9, YS + .02, 5.28, 1.2, .05, .1)
        b.box('membrane', (xa + xb) / 2, YS - 8.5, h + .01, xb - xa - .6, 16.4, .04)
    for y0, y1 in ((0.0, 22.0), (YS - 22.0, YS)):                                               # corner blocks across the cross street
        b.box('neighbour', -58.0, (y0 + y1) / 2, 4.0 + .002, 7.2, y1 - y0, 8.0 - .004)
        side = 1 if y0 >= 0 else -1
        for k in range(5):
            y = y0 + 2.0 + k * 4.0
            b.box('glass', XCW - 5.0 + .005, y, 6.0, .02, 1.2, 1.8)
            b.box('glass', XCW - 5.0 + .005, y, 2.2, .02, 2.6, 2.6)
        b.box('white', XCW - 5.0 + .1, (y0 + y1) / 2, 7.6, .24, y1 - y0 - .1, .3)
    for xa, xb, h in ((XW + 1.0, -14.0, 6.5), (-10.0, 8.0, 8.4), (12.0, 30.0, 6.0), (33.0, XE - 1.0, 7.2)):   # beyond the lane
        b.box('context', (xa + xb) / 2, LANE1 + 7.5, h / 2, xb - xa, 11.0, h)
        b.box('membrane', (xa + xb) / 2, LANE1 + 7.5, h + .015, xb - xa - .4, 10.6, .04)
        for k in range(int((xb - xa) / 3.0)):
            b.box('glass', xa + 1.5 + k * 3.0, LANE1 + 2.0 - .005, h * .55, 1.1, .02, 1.4)
    b.box('neighbour', (BLOCKS[-1]['x1'] + .1 + XE) / 2, 12.25, (9.5 + .004) / 2, XE - BLOCKS[-1]['x1'] - .1, 24.5, 9.5 - .004)   # east neighbour
    b.box('white', (BLOCKS[-1]['x1'] + XE) / 2 + .1, -.08, 8.9, XE - BLOCKS[-1]['x1'] - .2, .24, .3)
    for k in range(2):
        u = BLOCKS[-1]['x1'] + 2.2 + k * 4.0
        b.box('glass', u, -.005, 2.1, 3.0, .02, 2.8)
        b.box('glass', u, -.005, 6.2, 1.2, .02, 2.0)
    b.flush('context')


def build():
    ground()
    markings()
    furniture()
    for s in BLOCKS:
        block(s)
    party_walls()
    side_wall()
    corner_west()
    context()
    C.CONTACTS.append(dict(name='Main-street section: storefront street wall, sidewalks with brick furnishing strips, angled parking, travel lanes, curb extensions and crossings', box=[XCW, XE, YS, LANE1]))


LIGHT_RIG = dict(key=(-40, -60, 55), fill=(50, -40, 35), rear=(-20, 55, 40), target=(0.0, -8.0, 3.0), gain=5.0)
