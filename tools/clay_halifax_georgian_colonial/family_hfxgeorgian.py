"""Halifax Georgian colonial house, authored from the locked catalogue views of
halifax_georgian_colonial / variant_0 (red-brick Georgian house on a garden lot).

Read from the pixels (the top view governs the plan): a free-standing two-storey house of red brick with pale
stone dressings on a corner garden lot, the street to the south. A nearly square main block, seven bays across the
south front and four along each side, with two shallow rear wings at the back corners and a recessed court between
them. Over the main block a hipped slate roof truncated in a flat lead deck, with four tall brick chimney stacks at
the corners of the deck carrying rows of clay pots; the rear wings have their own hipped slate roofs running into
the main roof. The centre three bays of the south front form a slightly projecting pavilion with four giant stone
pilasters and a pediment of brick with an oval cartouche, its slate gable running back into the hip. A one-storey
Tuscan portico of four columns with a low hipped standing-seam metal roof stands on a stone platform before the
door. Tall nine-over-nine sashes (three panes wide) with shouldered stone lintels and stone sills, a stone plinth,
a stone string course at the first floor and a modillioned white eave cornice; dark downpipes. Formal box-hedge
parterres to the west and north, brick paths, a lawn and low hedges before the front, a tall iron railing along the
street and the west side, a stone Georgian house to the east, street trees and a dark tree by the west front.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-halifax-georgian-colonial'
X0, X1, Y0, Y1 = -10.6, 10.6, -7.35, 7.35          # main block walls: seven bays by four (top view, 0.69 deep)
PX, PD = 3.6, .6                                    # centre pavilion half-width and projection
YP = Y0 - PD                                        # pavilion face
WX0, WX1, WY1 = 3.6, 9.4, 9.5                       # rear wings at |x| 3.6 to 9.4, back to y 9.5 (top view)
T = .45
G0 = .6                                             # ground floor on the stone plinth
F1 = 4.95                                           # first floor; stone string course just below
FR0, EAVE = 8.95, 9.6                               # frieze foot and top of the eave cornice
OV = .5                                             # roof overhang beyond the wall line
ZL = EAVE + .02                                     # roof eave line
DX, DY0, DY1 = 6.5, -2.9, 3.5                       # flat lead deck (top view: north of centre)
ZD = 13.34                                          # deck level
PR = 3.0                                            # pediment rise
SB = (-8.85, -5.35, 5.35, 8.85)                     # side bays of the south front
PB = (-2.2, 0.0, 2.2)                               # pavilion bays
EB = (-5.5, -1.85, 1.85, 5.5)                       # bays of the side fronts (y)
EPS = .002
PALETTE = dict(wall=(.56, .29, .21), joint=(.66, .60, .53), stone=(.84, .82, .76), trim=(.93, .92, .88),
    frame=(.93, .92, .88), roof=(.35, .38, .42), course=(.26, .28, .31), lead=(.64, .64, .62), metal=(.55, .57, .58),
    glass=(.19, .23, .26), hardware=(.07, .07, .08), door=(.50, .33, .17), interior=(.84, .80, .74),
    floor=(.58, .48, .38), timber=(.33, .25, .17), pot=(.70, .40, .28), planting=(.22, .36, .14),
    conifer=(.13, .25, .12), hedge=(.19, .32, .13), lawn=(.34, .47, .22), soil=(.24, .18, .12),
    paving=(.44, .24, .19), concrete=(.70, .69, .66), asphalt=(.27, .27, .28), white=(.95, .95, .93),
    neighbour=(.47, .45, .41), nbtrim=(.86, .85, .80), pane=(.2, .23, .26))


def manifest(version):
    h = ZD + 2.3
    cams = G.camera_roster(X1 - X0 + 3.0, WY1 - YP + 3.0, h, [
        ('facade_close', (0.0, -12.25, 1.7), (0.0, Y0, 5.0), 16),
        ('architecture_close', (7.5, -13.5, 11.5), (0.0, -8.2, 8.6), 30),
        ('porch_columns', (-2.6, -11.9, 1.8), (-.4, -9.3, 2.8), 26),
        ('glass_close', (-5.35, -11.8, 4.7), (-5.35, Y0, 4.6), 45),
        ('cornice_chimneys', (-17.0, -15.0, 17.0), (-6.5, -3.5, 12.0), 40),
        ('west_front', (-27.0, -4.5, 5.5), (X0, 0.0, 5.0), 35),
        ('roof_deck', (15.0, -13.0, 25.0), (0.0, .3, 12.8), 35),
        ('rear_wings', (6.0, 27.0, 9.5), (0.0, 8.0, 6.0), 35),
        ('interior', (-6.9, -4.4, 2.3), (-5.35, Y0, 2.6), 30),
        ('garden_fence', (-25.0, -15.5, 3.2), (-14.5, -5.5, 2.0), 35)])
    for c in cams:                       # the locked front and oblique look from the south-west; whole-envelope views are framed by hand
        c['whole'] = False
        if c['name'] == 'front':                                            # the locked front: eye level across the street, south-west
            c.update(location=(-41.3, -31.3, 1.6), target=(-4.9, -5.1, 4.9), lens=49)
        elif c['name'] == 'front_corner':                                   # the locked oblique: high over the south-west corner
            c.update(location=(-24.76, -22.41, 26.36), target=(-2.9, -2.27, 7.89), lens=39)
        elif c['name'] == 'top':                                            # the locked top: centred on the house, 43 m across
            c.update(location=(-.14, -.07, 90.0), target=(-.14, -.069, 0.0), ortho_scale=43.3)
        elif c['name'] == 'aerial':
            c.update(location=(31.0, -33.0, 31.0), target=(0.0, 0.0, 5.0), lens=35)
        elif c['name'] == 'left_side':
            c.update(location=(-44.0, 1.0, 7.0), target=(0.0, 1.0, 6.0), lens=35)
        elif c['name'] == 'right_side':                                     # east elevation: the stone neighbour 4 m east is cut away by the near clip plane (context hidden)
            c.update(location=(40.0, 1.0, 8.0), target=(X1, 1.0, 9.28), lens=40, clip_start=25.78)   # near clip just west of the neighbour's eave; frame bottom above the cut ground
        elif c['name'] == 'rear':
            c.update(location=(0.0, 38.0, 9.0), target=(0.0, 4.0, 6.0), lens=35)
        elif c['name'] == 'rear_side':
            c.update(location=(-28.0, 31.0, 21.0), target=(0.0, 2.0, 6.0), lens=35)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='halifax_georgian_colonial/variant_0 (red-brick Georgian house on a garden lot)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=WY1 - YP, height=h),
            observed_storeys=2, storey_programme='two storeys on a low stone plinth, with an attic under the hipped roof',
            plan='21.2 x 14.7 m main block, seven bays by four, a 7.2 m centre pavilion projecting 0.6 m on the south front, two 5.8 x 2.15 m rear wings at the back corners with a recessed court between (top view); 7.5 m portico on a stone platform',
            facade='red brick with a stone plinth, a stone string course and a modillioned white eave cornice; tall nine-over-nine sashes three panes wide with shouldered stone lintels and stone sills; centre pavilion with four giant stone pilasters and a brick pediment with an oval cartouche; one-storey Tuscan portico of four columns with a low hipped standing-seam roof',
            roof='hipped blue-grey slate roof truncated in a flat lead deck with four brick chimney stacks and clay pots at its corners; the pavilion gable and the rear-wing hips run into the main roof',
            levels_m=[G0, F1, FR0, EAVE], roof_m=dict(eave=ZL, deck=ZD, pediment=EAVE + PR, chimneys=15.0),
            inferred='interiors, the rear wings and the north front follow the visible grammar; metric dimensions are authored teaching assumptions'),
        roof_contract=dict(type='hipped slate roof with a flat lead deck, gabled pediment and hipped rear wings running into it, chimney stacks at the deck corners; low hipped standing-seam portico roof', datum_m=ZL, crowns_m=[ZD, EAVE + PR]),
        identity_contract=dict(owner='free-standing red-brick Georgian house with a pedimented pilastered centre pavilion, a four-column portico, a hipped slate roof with a flat deck and four chimney stacks, white sashes and stone dressings'),
        material_contract=dict(profile='source-palette clay: red brick with pale joints, pale stone dressings, white cornice and sashes, blue-grey slate, grey lead deck and portico roof, terracotta pots, black iron', textured_keeper=False),
        programme_contract=dict(storeys=2, ground='hall, reception rooms, dining room', first='drawing room and bedrooms', attic='storage under the roof'),
        contact_contract=['Grade-zero lawns, brick paths, sidewalks and streets', 'Brick walls from grade on a stone plinth', 'Roof on the eave cornice', 'Portico on its stone platform', 'Chimney stacks through the roof at the deck corners'],
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


# ---- Halifax Georgian colonial house ----

OUTLINE = [(X0, Y0), (-PX, Y0), (-PX, YP), (PX, YP), (PX, Y0), (X1, Y0), (X1, Y1), (WX1, Y1), (WX1, WY1),
           (WX0, WY1), (WX0, Y1), (-WX0, Y1), (-WX0, WY1), (-WX1, WY1), (-WX1, Y1), (X0, Y1)]   # counter-clockwise


def offset_poly(poly, d):
    """Offset an orthogonal counter-clockwise polygon outward by d (negative d: inward)."""
    n = len(poly); out = []
    for i in range(n):
        (ax, ay), (bx, by), (cx, cy) = poly[i - 1], poly[i], poly[(i + 1) % n]
        e1 = (bx - ax, by - ay); e2 = (cx - bx, cy - by)
        l1 = math.hypot(*e1); l2 = math.hypot(*e2)
        n1 = (e1[1] / l1, -e1[0] / l1); n2 = (e2[1] / l2, -e2[0] / l2)
        out.append((bx + d * (n1[0] + n2[0]), by + d * (n1[1] + n2[1])))
    return out


def ring(name, d_out, d_in, z0, z1, role='stone', module='bands'):
    """Closed band round the house outline from z0 to z1, from d_in (inside the wall) to d_out (outside)."""
    po, pi = offset_poly(OUTLINE, d_out), offset_poly(OUTLINE, d_in)
    n = len(po)
    vs = [(x, y, z0) for x, y in po] + [(x, y, z1) for x, y in po] + [(x, y, z0) for x, y in pi] + [(x, y, z1) for x, y in pi]
    OB, OT, IB, IT = 0, n, 2 * n, 3 * n
    fs = []
    for i in range(n):
        j = (i + 1) % n
        fs += [(OB + i, OB + j, OT + j, OT + i), (IB + j, IB + i, IT + i, IT + j), (OT + i, OT + j, IT + j, IT + i), (OB + j, OB + i, IB + i, IB + j)]
    return C.mesh(name, vs, fs, role, module)


def sash(m, f, h, occupied='room', lintel=True):
    """Tall nine-over-nine sash three panes wide, shouldered stone lintel with a raised centre, stone sill."""
    framed(m, f, h, cols=3, rows=6, inset=.12, occupied=occupied)
    m.box('trim', h['u'], .09, h['z'] + h['h'] / 2, h['w'] - .1, .1, .07)                     # meeting rail
    m.box('stone', h['u'], -.05, h['z'] - .07, h['w'] + .2, .14, .14)                         # sill
    if lintel:
        top = h['z'] + h['h']
        m.box('stone', h['u'], -.03, top + .13, h['w'] + .36, .1, .26)                       # lintel
        m.box('stone', h['u'], -.04, top + .31, .5, .12, .12)                                # raised centre block


def face_courses(f, lo, hi, holes, spacing=.15, z0=G0 + .05, z1=FR0 - .04):
    G.brick_courses(f, lo + .02, hi - .02, z0, z1, holes, spacing=spacing)


def walls():
    ground = lambda tag, u, w=1.15: hole(f'{tag} ground {u:+.2f}', u, 1.45, w, 2.4)
    upper = lambda tag, u, w=1.15: hole(f'{tag} first {u:+.2f}', u, 5.55, w, 2.3)
    top = FR0 + .05
    # South front either side of the pavilion.
    f = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south')
    for tag, lo, hi, bays in (('south west', X0, -PX, SB[:2]), ('south east', PX, X1, SB[2:])):
        hs = [ground('south', u) for u in bays] + [upper('south', u) for u in bays]
        f.wall(f'{tag} carrier', lo, hi, 0.0, top, depth=T, holes=hs)
        face_courses(f, lo, hi, hs)
        m = Merge(f)
        for h in hs:
            sash(m, f, h)
        m.flush(tag)
    # Centre pavilion: door with a fanlight, two ground sashes, three first-floor sashes.
    fp = C.Face((0, YP, 0), (1, 0, 0), (0, 1, 0), 'pavilion')
    door = hole('front door', 0.0, G0 + .02, 1.2, 2.75, kind='door')
    fan = hole('fanlight', 0.0, G0 + 2.92, 1.2, .43)
    hs = [ground('pavilion', u, 1.0) for u in PB if u != 0.0] + [upper('pavilion', u, 1.0) for u in PB]
    fp.wall('pavilion carrier', -PX, PX, 0.0, top, depth=PD + T, holes=hs + [door, fan])
    face_courses(fp, -PX, PX, hs + [door, fan])
    m = Merge(fp)
    for h in hs:
        sash(m, fp, h)
    m.box('door', 0.0, .22, door['z'] + door['h'] / 2, door['w'] - .02, .06, door['h'] - .02)
    for zz in (.45, 1.35, 2.25):                                                             # six raised panels
        for s in (-1, 1):
            m.box('door', s * .27, .185, door['z'] + zz, .4, .02, .72)
    m.box('hardware', .42, .17, door['z'] + 1.15, .05, .04, .05)
    register(fp, door, .2, 'entry door', 'hall')
    framed(m, fp, fan, cols=4, rows=1, inset=.2, occupied='hall')
    for s in (-1, 1):                                                                        # stone door architrave, 3 cm proud
        m.box('stone', s * .73, -.005, (G0 + 4.1) / 2, .22, .05, 4.1 - G0)                     # clear of the cut reveal; tops buried in the head
    m.box('stone', 0.0, -.015, 4.06, 1.68, .07, .2)                                           # head 2 cm prouder than the jambs: no shared face
    # Four giant stone pilasters with bases and capitals.
    for u in (-3.3, -1.1, 1.1, 3.3):
        m.box('stone', u, -.05, (G0 + 8.6) / 2, .5, .14, 8.6 - G0)
        m.box('stone', u, -.08, G0 + .2, .66, .2, .4)
        m.box('stone', u, -.09, 8.76, .7, .22, .42)
        m.box('stone', u, -.07, 8.5, .56, .18, .1)
    for s in (-1, 1):                                                                        # corner blocks under the raking cornice ends,
        m.box('trim', s * 3.755, -.24, 9.24, .61, .44, .62)                                   # lapped into the capital, frieze, corona and rake
    m.flush('pavilion')
    for s in (-1, 1):                                                                        # pavilion returns
        fr = C.Face((s * PX, 0, 0), (0, s, 0), (-s, 0, 0), f'pavilion return {s:+d}')
        G.brick_courses(fr, (YP if s > 0 else -Y0) + .02, (Y0 if s > 0 else -YP) - .02, G0 + .05, FR0 - .04, [], spacing=.15)
    # West and east fronts: four bays on both floors.
    for side, f in (('west', C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west')), ('east', C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east'))):
        us = [(-y if side == 'west' else y) for y in EB]
        hs = [ground(side, u) for u in us] + [upper(side, u) for u in us]
        f.wall(f'{side} carrier', Y0 + T, Y1 - T, 0.0, top, depth=T, holes=hs)
        face_courses(f, Y0 + T, Y1 - T, hs, spacing=.3)
        m = Merge(f)
        for h in hs:
            sash(m, f, h)
        m.flush(side)
    # North front across the court between the wings: a garden door and sashes.
    f = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')
    rdoor = hole('garden door', 0.0, G0 + .02, 1.2, 2.6, kind='door')
    hs = [ground('north', u, 1.0) for u in (-2.2, 2.2)] + [upper('north', u, 1.0) for u in PB]
    f.wall('north carrier', -X1, -X0, 0.0, top, depth=T, holes=hs + [rdoor])
    face_courses(f, -WX0, WX0, hs + [rdoor], spacing=.3)
    for lo, hi in ((-X1, -WX1), (WX1, -X0)):
        face_courses(f, lo, hi, [], spacing=.3)
    m = Merge(f)
    for h in hs:
        sash(m, f, h)
    m.box('door', 0.0, .2, rdoor['z'] + rdoor['h'] / 2, rdoor['w'] - .02, .06, rdoor['h'] - .02)
    register(f, rdoor, .18, 'garden door', 'hall')
    m.flush('north')
    # Rear wings: two bays on the north face, plain side walls.
    for s in (-1, 1):
        xa, xb = (s * WX0, s * WX1) if s > 0 else (s * WX1, s * WX0)
        f = C.Face((0, WY1, 0), (-1, 0, 0), (0, -1, 0), f'wing {s:+d} north')
        us = [-(xa + 1.45), -(xb - 1.45)]
        hs = [ground(f'wing {s:+d}', u, 1.0) for u in us] + [upper(f'wing {s:+d}', u, 1.0) for u in us]
        f.wall(f'wing {s:+d} north carrier', -xb, -xa, 0.0, top, depth=T, holes=hs)
        face_courses(f, -xb, -xa, hs, spacing=.3)
        m = Merge(f)
        for h in hs:
            sash(m, f, h)
        m.flush(f'wing {s:+d} north')
        for x, sgn in ((xa, 1), (xb, -1)):                        # sgn: +1 face looks west, -1 east
            fs = C.Face((x, 0, 0), (0, -sgn, 0), (sgn, 0, 0), f'wing {s:+d} side {x:+.1f}')
            lo, hi = (-(WY1 - T), -Y1) if sgn > 0 else (Y1, WY1 - T)
            fs.wall(f'wing side carrier {x:+.1f}', lo, hi, 0.0, top, depth=T)
            face_courses(fs, lo, hi, [], spacing=.3)


def bands():
    ring('Stone plinth', .06, -.3, 0.0, G0, 'stone', 'plinth')
    ring('First-floor string course', .07, -.2, 4.75, 4.95, 'stone', 'bands')
    ring('Frieze', .05, -.3, FR0, 9.25, 'trim', 'cornice')
    ring('Bed mould', .2, -.3, 9.24, 9.36, 'trim', 'cornice')
    ring('Corona', .45, -.3, 9.35, EAVE, 'trim', 'cornice')
    b = Batch()
    po = OUTLINE
    for i in range(len(po)):
        (ax, ay), (bx, by) = po[i], po[(i + 1) % len(po)]
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
        nx, ny = uy, -ux
        k = max(1, int((L - .5) / .62))
        for j in range(k + 1):
            t = .25 + (L - .5) * j / k if k else L / 2
            px, py = ax + ux * t, ay + uy * t
            cx, cy = px + nx * .235, py + ny * .235
            b.box('trim', cx, cy, 9.24, .12 if abs(ux) > .5 else .41, .41 if abs(ux) > .5 else .12, .24)   # modillion
    # Blocks filling the re-entrant corners of the bed-mould zone, so no pocket opens under the corona there.
    n = len(OUTLINE)
    for i in range(n):
        (ax, ay), (bx, by), (cx, cy) = OUTLINE[i - 1], OUTLINE[i], OUTLINE[(i + 1) % n]
        if (bx - ax) * (cy - by) - (by - ay) * (cx - bx) < 0:                                    # clockwise turn: re-entrant corner
            ox, oy = offset_poly(OUTLINE, .45)[i]
            b.box('trim', (bx + ox) / 2, (by + oy) / 2, 9.235, abs(ox - bx) + .02, abs(oy - by) + .02, .25)
    b.flush('modillions')
    # Dark downpipes with heads at the corners and beside the pavilion.
    b = Batch()
    for x, y in ((X0 + .3, Y0 - .05), (X1 - .3, Y0 - .05), (-PX - .25, Y0 - .05), (PX + .25, Y0 - .05),
                 (X0 - .05, -6.9), (X0 - .05, 6.9), (X1 + .05, -6.9), (X1 + .05, 6.9)):
        b.box('hardware', x, y, (.1 + 8.75) / 2, .11, .11, 8.65)
        b.box('hardware', x, y, 8.84, .24, .2, .26)                                             # head, 2 cm into the frieze
    b.flush('downpipes')


def hip_solid(name, lower, ridge, z_eave, thick, role, module):
    """Closed roof solid: a rectangle eave ring (four corners from the south-west, counter-clockwise) rising to a
    ridge of two points (or a deck of four); fascia faces of depth `thick` below the eave."""
    n = len(lower)
    vs = [(x, y, z_eave - thick) for x, y in lower] + [(x, y, z_eave) for x, y in lower] + list(ridge)
    B, E, R = 0, n, 2 * n
    fs = [tuple(range(n - 1, -1, -1))]
    for i in range(n):
        j = (i + 1) % n
        fs.append((B + i, B + j, E + j, E + i))
    if len(ridge) == 2:                                           # ridge along x (porch) or y (wing): faces by nearest ridge point
        r0, r1 = R, R + 1
        fs += [(E + 0, E + 1, r1, r0), (E + 1, E + 2, r1), (E + 2, E + 3, r0, r1), (E + 3, E + 0, r0)] if ridge[0][1] == ridge[1][1] \
            else [(E + 0, E + 1, r0), (E + 1, E + 2, r1, r0), (E + 2, E + 3, r1), (E + 3, E + 0, r0, r1)]
    return C.mesh(name, vs, fs, role, module)


def roofs():
    lower = [(X0 - OV, Y0 - OV), (X1 + OV, Y0 - OV), (X1 + OV, Y1 + OV), (X0 - OV, Y1 + OV)]
    upper = [(-DX, DY0), (DX, DY0), (DX, DY1), (-DX, DY1)]
    strip('Main hipped slate roof', lower, upper, ZL, ZD, 'roof', 'roof')
    C.box('Lead roof deck', (0.0, (DY0 + DY1) / 2, ZD - .06), (2 * DX + .1, DY1 - DY0 + .1, .22), 'lead', 'roof', 0)
    b = Batch()
    # Slate courses and hip rolls on the four slopes.
    for (ax, ay), (bx, by) in zip(lower, upper):
        b.beam('course', (ax, ay, ZL + .03), (bx, by, ZD + .03), .09, .06)
    for k in range(1, 10):
        t = k / 10
        z = ZL + (ZD - ZL) * t
        xl = lower[0][0] + (upper[0][0] - lower[0][0]) * t
        for y0_, y1_, sgn in ((lower[0][1], upper[0][1], -1), (lower[2][1], upper[2][1], 1)):
            y = y0_ + (y1_ - y0_) * t
            b.beam('course', (xl + .05, y + sgn * .012, z + .012), (-xl - .05, y + sgn * .012, z + .012), .04, .02)
        yl = lower[0][1] + (upper[0][1] - lower[0][1]) * t
        yh = lower[2][1] + (upper[2][1] - lower[2][1]) * t
        for x0_, x1_, sgn in ((lower[0][0], upper[0][0], -1), (lower[1][0], upper[1][0], 1)):
            x = x0_ + (x1_ - x0_) * t
            b.beam('course', (x + sgn * .012, yl + .05, z + .012), (x + sgn * .012, yh - .05, z + .012), .04, .02)
    b.flush('slate courses')
    # Four brick stacks at the deck corners, stone caps, three clay pots each.
    b = Batch()
    for x in (-5.15, 5.15):
        for y in (DY0 + .3, DY1 + .05):
            b.box('wall', x, y, (11.8 + 15.0) / 2, 1.0, 1.6, 3.2)
            b.box('stone', x, y, 15.07, 1.14, 1.74, .14)
            b.box('wall', x, y, 15.2, .9, 1.5, .14)
    b.flush('chimney stacks')
    for x in (-5.15, 5.15):
        for y in (DY0 + .3, DY1 + .05):
            for k in (-1, 0, 1):
                C.rod('Chimney pot', (x, y + k * .45, 15.22), (x, y + k * .45, 15.82), .14, 'pot', 'chimneys', 10)
    # Rear-wing hipped roofs running into the main roof (eave 2 cm above the main eave).
    for s in (-1, 1):
        xa, xb = sorted((s * WX0, s * WX1))
        xm, hw = (xa + xb) / 2, (xb - xa) / 2 + OV
        rise = hw * .8
        hip_solid(f'Rear wing roof {s:+d}', [(xa - OV, 4.0), (xb + OV, 4.0), (xb + OV, WY1 + OV), (xa - OV, WY1 + OV)],
                  [(xm, 4.0, ZL + .02 + rise), (xm, WY1 + OV - hw, ZL + .02 + rise)], ZL + .02, .18, 'roof', 'roof')
        b = Batch()
        for k in range(1, 8):
            t = k / 8
            z = ZL + .02 + rise * t
            yn = WY1 + OV - hw * t
            for x, sg in ((xa - OV + hw * t, -1), (xb + OV - hw * t, 1)):
                b.beam('course', (x + sg * .012, 4.2, z + .012), (x + sg * .012, yn - .03, z + .012), .04, .02)
            b.beam('course', (xa - OV + hw * t + .03, yn + .012, z + .012), (xb + OV - hw * t - .03, yn + .012, z + .012), .04, .02)
        b.beam('course', (xm, 4.2, ZL + .02 + rise + .02), (xm, WY1 + OV - hw, ZL + .02 + rise + .02), .1, .07)   # ridge roll
        for (cx, cy) in ((xa - OV, WY1 + OV), (xb + OV, WY1 + OV)):
            b.beam('course', (cx, cy, ZL + .05), (xm, WY1 + OV - hw, ZL + .02 + rise + .03), .09, .06)
        b.flush(f'rear wing slates {s:+d}')


def chevron(name, xh, zc, m, tv, y0, y1, role='trim', module='pediment'):
    """Raking cornice as one mitred inverted-V band: centreline z = zc - m|x|, vertical thickness tv, from y0 to y1."""
    lo, hi = zc - m * xh, zc
    pts = [(-xh, lo + tv / 2), (0.0, hi + tv / 2), (xh, lo + tv / 2), (xh, lo - tv / 2), (0.0, hi - tv / 2), (-xh, lo - tv / 2)]
    return C.prism(name, pts, 'y', y0, y1, role, module)


def pediment():
    # Slate gable roof over the pavilion running back into the main hip.
    C.prism('Pavilion gable roof', [(-4.05, 9.2), (4.05, 9.2), (0.0, 12.85)], 'y', YP + .02, -3.0, 'roof', 'roof')
    C.prism('Pediment tympanum', [(-PX - .02, 9.58), (PX + .02, 9.58), (0.0, 9.6 + PR + .02)], 'y', YP, YP + .35, 'wall', 'pediment')
    chevron('Raking cornice', 4.07, 12.78, 3.36 / 4.1, .543, YP - .47, YP + .03)                  # one mitred piece, 2 cm proud of the corona
    chevron('Raking cornice nosing', 4.0, 12.98, .84, .209, YP - .52, YP - .38)
    b = Batch()
    for k in range(1, 5):                                                                       # slate courses on the gable roof
        z = 9.2 + 3.65 * k / 5
        x = 4.05 * (1 - k / 5)
        for s in (-1, 1):
            b.beam('course', (s * (x + .03), YP + .3, z + .03), (s * (x + .03), -3.2, z + .03), .04, .02)
    b.beam('course', (0.0, YP + .3, 12.88), (0.0, -3.2, 12.88), .1, .07)                    # ridge roll
    b.flush('pediment cornices')
    # Oval cartouche with a moulded frame and two garland swags.
    pts = lambda rx, rz: [(rx * math.cos(a), 10.75 + rz * math.sin(a)) for a in [math.tau * i / 24 for i in range(24)]]
    C.prism('Cartouche frame', pts(.55, .66), 'y', YP - .07, YP + .05, 'stone', 'pediment')
    C.prism('Cartouche', pts(.38, .5), 'y', YP - .12, YP + .05, 'stone', 'pediment')
    b = Batch()
    for s in (-1, 1):
        b.beam('stone', (s * .5, YP - .08, 10.95), (s * 1.15, YP - .08, 10.55), .1, .16)
        b.beam('stone', (s * 1.15, YP - .08, 10.55), (s * 1.45, YP - .08, 10.25), .08, .12)
    b.flush('cartouche swags')


def portico():
    y_front, y_col = -9.6, -9.35
    b = Batch()
    b.box('stone', 0.0, (y_front + YP + .05) / 2, (G0 + .02) / 2, 7.5, YP + .05 - y_front, G0 + .02)   # platform
    for k, (z, y0_) in enumerate(((.413, y_front - .3), (.207, y_front - .6))):                      # two steps
        b.box('stone', 0.0, (y0_ + y_front + .02 + .3 * k) / 2, z / 2, 7.46 - .04 * k, y_front + .02 + .3 * k - y0_, z)   # each step 2 cm in from the one above
    for x in (-3.3, -1.1, 1.1, 3.3):
        b.box('stone', x, y_col, .68, .56, .56, .14)                                           # plinth
        b.box('stone', x, y_col, 3.89, .6, .6, .16)                                            # abacus
    b.box('trim', 0.0, (y_col - .27 + y_col + .27) / 2, (3.95 + 4.56) / 2, 7.24, .54, .61)     # entablature
    for s in (-1, 1):
        b.box('trim', s * 3.34, (-9.1 + YP + .05) / 2, (3.97 + 4.56) / 2, .52, YP + .05 + 9.1, .59)
    b.box('trim', 0.0, (-9.85 + YP + .05) / 2, (4.55 + 4.72) / 2, 7.7, YP + .05 + 9.85, .17)    # cornice slab and ceiling
    b.flush('portico')
    for x in (-3.3, -1.1, 1.1, 3.3):
        C.rod('Portico column base', (x, y_col, .74), (x, y_col, .82), .26, 'stone', 'portico', 20)
        C.rod('Portico column shaft', (x, y_col, .74), (x, y_col, 3.74), .2, 'stone', 'portico', 20)
        C.rod('Portico column necking', (x, y_col, 3.6), (x, y_col, 3.66), .225, 'stone', 'portico', 20)
        C.rod('Portico column echinus', (x, y_col, 3.7), (x, y_col, 3.83), .27, 'stone', 'portico', 20)
    yb, ye = YP + .1, -9.82
    hip_solid('Portico roof', [(-3.82, ye), (3.82, ye), (3.82, yb), (-3.82, yb)],
              [(-1.92, yb, 5.38), (1.92, yb, 5.38)], 4.73, .11, 'metal', 'portico')
    b = Batch()
    rise, run = 5.38 - 4.73, yb - ye
    for i in range(-7, 8):
        x = i * .5
        if abs(x) <= 1.92:
            b.beam('lead', (x, ye + .02, 4.75), (x, yb, 5.4), .04, .04)
        else:
            t = (3.82 - abs(x)) / 1.9
            b.beam('lead', (x, ye + .02, 4.75), (x, ye + run * t, 4.73 + rise * t + .02), .04, .04)
    for s in (-1, 1):
        b.beam('lead', (s * 3.82, ye, 4.76), (s * 1.92, yb, 5.41), .07, .05)
    b.flush('portico roof seams')
    # Garden-door landing on the north.
    b = Batch()
    b.box('stone', 0.0, Y1 + .58, (G0 + .02) / 2, 2.4, 1.2, G0 + .02)
    b.box('stone', 0.0, Y1 + 1.35, .15, 2.4, .32, .3)
    b.flush('garden door landing')


def inside():
    for z in (G0, F1):
        C.box(f'Floor {z:.2f}', (0, 0, z - .12), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .24), 'floor', 'inside', 0)
        for s in (-1, 1):
            xa, xb = sorted((s * WX0, s * WX1))
            C.box(f'Wing floor {s:+d} {z:.2f}', ((xa + xb) / 2, (Y1 - T + WY1 - T) / 2, z - .12), (xb - xa - 2 * T, WY1 - Y1, .24), 'floor', 'inside', 0)
    for z in (G0, F1):
        for x in (-7.2, -2.0, 2.0, 7.2):
            C.qa_room_light(f'Room {x:+.0f} {z:.0f}', (x, Y0 + 2.4, z + 2.1), 45, 2.2)
        for x in (-7.2, 7.2):
            C.qa_room_light(f'Side room {x:+.0f} {z:.0f}', (x, 2.0, z + 2.1), 35, 2.0)
        for x in (-6.5, 0.0, 6.5):
            C.qa_room_light(f'Rear room {x:+.0f} {z:.0f}', (x, Y1 - 1.6, z + 2.1), 30, 2.0)
    C.CONTACTS.append(dict(name='Brick walls from grade on a stone plinth; roofs on the eave cornice; portico on its platform', eave_m=EAVE))


def hedge(b, x0, x1, y0, y1, w=.42, h=.55):
    """Clipped box-hedge rectangle: long runs along x, the y runs 2 mm lower and narrower, lapped 3 cm into them."""
    for y in (y0, y1):
        b.box('hedge', (x0 + x1) / 2, y, h / 2, x1 - x0 + w, w, h)
    for x in (x0, x1):
        b.box('hedge', x, (y0 + y1) / 2, (h - .004) / 2, w - .004, y1 - y0 - w + .06, h - .004)


def cone(name, x, y, h, r, role='conifer', sides=14):
    vs = [(x + r * math.cos(math.tau * i / sides), y + r * math.sin(math.tau * i / sides), .02) for i in range(sides)] + [(x, y, h)]
    fs = [tuple(range(sides - 1, -1, -1))] + [(i, (i + 1) % sides, sides) for i in range(sides)]
    o = C.mesh(name, vs, fs, role, 'garden planting')
    for p in o.data.polygons[1:]:
        p.use_smooth = True
    return o


def tree(x, y, height, spread, role='planting', dense=False, high=False):
    C.rod('Tree trunk', (x, y, .02), (x, y, height * (.75 if high else .55)), .2 if height > 9 else .15, 'timber', 'trees', 8)
    if high:                                                      # tall street tree: crown held high above a clear stem
        for dx, dy, dz in ((-.45, -.25, .76), (.5, -.1, .8), (.05, .5, .84), (0, 0, .93)):
            tip = (x + dx * spread, y + dy * spread, height * dz)
            C.rod('Tree branch', (x, y, height * .7), tip, .07, 'timber', 'trees', 6)
            A.foliage('Tree crown', tip, (.8 * spread, .8 * spread, .6 * spread), role=role, detail=2)
        return
    if dense:
        for dx, dy, dz, r in ((0, 0, .45, 1.0), (-.4, .3, .62, .8), (.45, -.2, .7, .75), (0, .1, .85, .55), (.2, .4, .3, .7)):
            A.foliage('Dense crown', (x + dx * spread, y + dy * spread, height * dz), (r * spread, r * spread, r * spread * 1.25), role=role, detail=2)
        return
    for dx, dy, dz in ((-.45, -.25, .72), (.5, -.1, .76), (.05, .5, .82), (0, 0, .92)):
        tip = (x + dx * spread, y + dy * spread, height * dz)
        C.rod('Tree branch', (x, y, height * .5), tip, .07, 'timber', 'trees', 6)
        A.foliage('Tree crown', tip, (.85 * spread, .85 * spread, .75 * spread), role=role, detail=2)


def site():
    b = Batch()
    b.box('lawn', (-20.0 + 14.6) / 2, (-10.84 + 15.6) / 2, .015, 34.6, 26.44, .03)              # the house lot
    b.box('lawn', 21.0, (-10.84 + 15.6) / 2, .015, 12.8, 26.44, .03)                            # the neighbour's lot (butts)
    b.box('concrete', 1.0, -12.13, .07, 50.0, 2.6, .14)                                          # south sidewalk
    b.box('asphalt', 1.0, -17.2, .01, 50.0, 7.6, .02)                                            # street
    b.box('concrete', 1.0, -22.2, .07, 50.0, 2.4, .14)                                           # far sidewalk
    b.box('concrete', -21.2, 2.4, .065, 2.42, 26.5, .13)                                         # west sidewalk, 1 cm lower
    b.box('concrete', 1.0, 16.6, .07, 50.0, 2.0, .14)                                            # north sidewalk
    b.box('asphalt', 1.0, 21.0, .01, 50.0, 6.84, .02)                                           # north street
    b.box('concrete', 21.4, 9.4, .04, 9.0, 7.6, .04)                                             # paved court beside the neighbour
    # Brick paths (equal tops only where they butt).
    b.box('paving', 1.15, (-10.86 + -10.2) / 2, .025, 8.3, .66, .05)                             # front apron at the steps
    b.box('paving', 12.35, (-10.86 + 9.6) / 2, .025, 2.7, 20.46, .05)                            # east side path
    b.box('paving', -11.45, (-10.86 + 9.6) / 2, .025, 1.7, 20.46, .05)                          # west side path
    b.box('paving', -16.0, 5.3, .025, 7.4, 2.2, .05)                                             # west cross path
    b.box('paving', .7, 10.3, .025, 26.0, 1.4, .05)                                              # rear cross path
    b.box('paving', 0.0, (Y1 + 9.6) / 2, .025, 7.0, 9.6 - Y1, .05)                              # court between the wings
    b.box('paving', 0.0, (11.0 + 15.6) / 2, .025, 4.4, 4.6, .05)                                # north centre path
    # Box-hedge parterres west and north; low hedges before the front.
    hedge(b, -19.2, -12.9, -9.4, 4.0)
    hedge(b, -18.2, -13.9, -8.2, 2.8, w=.36, h=.45)
    hedge(b, -17.0, -15.1, -6.2, .8, w=.32, h=.4)
    hedge(b, -19.2, -12.9, 6.6, 14.8)
    hedge(b, -17.9, -14.2, 8.0, 13.4, w=.34, h=.42)
    for x0, x1 in ((-10.0, -2.6), (2.6, 10.6)):
        hedge(b, x0, x1, 11.7, 14.8)
        hedge(b, x0 + 1.2, x1 - 1.2, 12.5, 14.0, w=.32, h=.4)
    for x0, x1 in ((-10.4, -3.7), (3.7, 10.4)):                                                # front hedges lapped into the plinth and the platform
        b.box('hedge', (x0 + x1) / 2, Y0 - .35, .3, x1 - x0, .6, .6)
    b.box('hedge', 18.4, -9.6, .4, 7.0, .6, .8)                                                  # the neighbour's front hedge
    for x0, x1 in ((-20.0, -2.4), (2.4, 26.0)):
        b.box('hedge', (x0 + x1) / 2, 15.3, .45, x1 - x0, .5, .9)                               # north boundary hedge, gap at the path
    b.flush('site')
    iron_fence((-19.85, -10.75), (-12.4, -10.75), height=1.75, wall=.15, spacing=.2)            # the street railing runs along the west garden only (top view)
    C.rod('Fence end post', (-12.4, -10.75, .15), (-12.4, -10.75, 2.02), .035, 'hardware', 'fence', 6)
    b = Batch()                                                                                  # open front lawns: low stone curb and low box edging
    for x0, x1 in ((-10.58, -3.02), (5.32, 10.98)):
        b.box('stone', (x0 + x1) / 2, -10.76, .09, x1 - x0, .2, .18)
        b.box('hedge', (x0 + x1) / 2, -10.42, .21, x1 - x0 - .3, .4, .42)
    b.flush('front lawn curbs')
    iron_fence((-19.85, -10.58), (-19.85, 15.0), height=1.75, wall=.15, spacing=.26)
    tree(-1.0, -12.5, 11.0, 2.0)                                  # between the top view (x -4.4) and the front and oblique (x 0 to 1)
    tree(11.2, -12.5, 15.0, 2.3, high=True)                       # crowns stay clear of the right_side clip plane
    tree(-13.0, -4.4, 8.0, 2.0, role='conifer', dense=True)
    tree(11.4, -9.4, 8.0, 1.4)                                     # side-path tree south of the east front, clear of it and of the clip plane
    tree(-17.8, 13.0, 12.0, 3.2)
    tree(19.5, 12.0, 11.0, 2.8)                                   # in the court north of the neighbour, east of the right_side clip plane
    for x, y, h in ((-15.6, -10.1, 4.4), (-17.4, -10.1, 3.8)):
        cone('Evergreen cone', x, y, h, .45)
    neighbour()


def slope_plate(name, a, c, y0, y1, t=.16, role='roof', module='context'):
    """Closed sloped plate from (x, z) a to (x, z) c, extruded along y."""
    vs = []
    for (x, z) in (a, c):
        for y in (y0, y1):
            vs += [(x, y, z), (x, y, z - t)]
    fs = [(0, 2, 6, 4), (1, 5, 7, 3), (0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6)]
    return C.mesh(name, vs, fs, role, module)


def context_windows(m, f, hs):
    """Dark opaque panes with pale glazing bars and stone sills, for the context house."""
    for h in hs:
        u, z, w, hh = h['u'], h['z'], h['w'], h['h']
        m.box('pane', u, .2, z + hh / 2, w - .02, .04, hh - .02)
        m.box('nbtrim', u, .16, z + hh / 2, .05, .04, hh - .04)
        for k in (1, 2, 3):
            m.box('nbtrim', u, .162, z + hh * k / 4, w - .04, .036, .05)
        m.box('nbtrim', u, -.03, z - .06, w + .16, .1, .1)
        register(f, h, .2, 'context window', 'context')


def neighbour():
    """The grey stone Georgian house to the east, as context: three storeys, gabled slate roof running north-south,
    three dormers on the west slope, gable-end stacks."""
    nx0, nx1, ny0, ny1, ne = 14.8, 23.8, -8.6, 5.4, 10.2
    floors = ((1.1, 2.0), (4.4, 2.0), (7.6, 1.7))
    f = C.Face((nx0, 0, 0), (0, -1, 0), (1, 0, 0), 'neighbour west')
    hs = [hole(f'neighbour west {k} {i}', -y, z, .95, hh) for k, (z, hh) in enumerate(floors) for i, y in enumerate((-6.3, -2.5, 1.3, 4.0))]
    f.wall('neighbour west wall', -ny1, -ny0, 0.0, ne, depth=.5, role='neighbour', holes=hs)
    G.brick_courses(f, -ny1 + .02, -ny0 - .02, .5, ne - .1, hs, spacing=.42)
    m = Merge(f)
    context_windows(m, f, hs)
    m.box('nbtrim', (-ny1 - ny0) / 2, -.05, ne - .12, ny1 - ny0 + .1, .12, .24)
    m.flush('neighbour west')
    f = C.Face((0, ny0, 0), (1, 0, 0), (0, 1, 0), 'neighbour south')
    us = [nx0 + 2.0, nx0 + 4.5, nx0 + 7.0]
    hs = [hole(f'neighbour south {k} {i}', u, z, .95, hh) for k, (z, hh) in enumerate(floors) for i, u in enumerate(us) if not (k == 0 and i == 1)]
    door = hole('neighbour door', us[1], .3, 1.1, 2.6, kind='door')
    f.wall('neighbour south wall', nx0 + .5, nx1, 0.0, ne, depth=.5, role='neighbour', holes=hs + [door])
    G.brick_courses(f, nx0 + .52, nx1 - .02, .5, ne - .1, hs + [door], spacing=.42)
    m = Merge(f)
    context_windows(m, f, hs)
    m.box('door', door['u'], .18, door['z'] + door['h'] / 2, door['w'] - .02, .05, door['h'] - .02)
    register(f, door, .16, 'neighbour door', 'context')
    m.box('nbtrim', (nx0 + .5 + nx1) / 2, -.05, ne - .12, nx1 - nx0 - .4, .12, .24)
    m.flush('neighbour south')
    C.box('Neighbour body', ((nx0 + .5 + nx1) / 2, (ny0 + .5 + ny1) / 2, ne / 2), (nx1 - nx0 - .5, ny1 - ny0 - .5, ne), 'neighbour', 'context', 0)
    rise, xm, ov = 4.2, (nx0 + nx1) / 2, .3
    half = (nx1 - nx0) / 2
    for yy in (ny0 + .25, ny1 - .25):
        C.prism(f'Neighbour gable {yy:+.1f}', [(nx0 + .01, ne - .02), (nx1 - .01, ne - .02), (xm, ne + rise)], 'y', yy - .25, yy + .25, 'neighbour', 'context')
    k = rise / half
    zt = ne + rise + .2                                           # plate top at the ridge, 20 cm over the gable apex
    for s in (-1, 1):
        slope_plate(f'Neighbour slate slope {s:+d}', (xm + s * (half + ov), zt - k * (half + ov)), (xm - s * .05, zt + .05 * k), ny0 - .05, ny1 + .05, t=.22)
    b = Batch()
    b.beam('course', (xm, ny0 - .05, zt + .02), (xm, ny1 + .05, zt + .02), .14, .1)             # ridge roll
    for y in (-5.0, -1.0, 3.0):                                                               # dormers on the west slope
        xd = nx0 + 1.6
        zr = zt - k * (xm - (xd - .2))                                                        # roof at the dormer front
        b.box('roof', xd + .6, y, (zr - .35 + zr + 1.1) / 2, 1.6, 1.3, 1.45)
        b.box('nbtrim', xd - .2, y, zr + .45, .06, 1.0, .9)
        b.box('pane', xd - .235, y, zr + .45, .02, .74, .66)
    for yy in (ny0 + .35, ny1 - .35):
        yc = yy + (.12 if yy < 0 else -.12)                                                    # stacks set 12 cm behind the gable faces
        b.box('neighbour', xm, yc, ne + rise + .4, 1.8, .7, 3.2)                                # gable-end stacks
        b.box('nbtrim', xm, yc, ne + rise + 2.04, 1.95, .85, .12)
    b.flush('neighbour roof')
    for y in (-5.0, -1.0, 3.0):
        xd = nx0 + 1.6
        zr = zt - k * (xm - (xd - .2))
        C.prism(f'Neighbour dormer roof {y:+.1f}', [(y - .8, zr + 1.05), (y + .8, zr + 1.05), (y, zr + 1.6)], 'x', xd - .3, xd + 1.4, 'roof', 'context')


def build():
    site()
    walls()
    bands()
    roofs()
    pediment()
    portico()
    inside()
    C.CONTACTS.append(dict(name='Free-standing red-brick Georgian house on a garden lot, street to the south, stone neighbour to the east', box=[X0, X1, YP, WY1]))


LIGHT_RIG = dict(key=(-38, -34, 32), fill=(34, -26, 22), rear=(12, 34, 26), target=(0, 0, 6.0), gain=4.0)
