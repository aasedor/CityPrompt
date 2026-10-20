"""Elevated steel rail viaduct, authored from the locked catalogue views of
rail_transit_viaduct / variant_2 (Steel Through-Truss Rail).

Read from the pixels (the top view governs the plan): a long elevated twin-track rail viaduct running along a city
street. Each span is a riveted steel deck arch: a solid riveted plate rib in each of two planes springing low from
built-up box columns on concrete pedestals, an open spandrel lattice of posts and N-diagonals up to a deep plate
girder, and riveted transverse portal arches between the paired columns (no bracing to the ground), a steel
deck with sleepers and rails and edge railings. At the near (south) end the line enters a bowstring through-truss
whose heavy riveted arched trusses rise above the deck on both sides while the viaduct's own deck arches continue beneath it on columns and pedestals. A silver stainless train on the street-side (east) track. Beneath and
west of the viaduct a pale paved promenade with trees; to its east a pale strip, a red cycle lane, a two-lane road,
a sidewalk; flat-roofed brick apartment blocks on both sides.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-rail-through-truss'
X0, X1, Y0, Y1 = -4.6, 4.6, -60.0, 60.0          # the viaduct deck and its 120 m modelled run
BOW = 30.0                                       # the bowstring through-truss span at the south end
SPANS = 6                                        # deck-arch spans north of it
SP = (Y1 - Y0 - BOW) / SPANS                     # 15 m spans
CX = 3.8                                         # the two planes of columns, ribs and girders (x = +-CX)
GB, GT, DT = 11.8, 12.8, 13.05                   # plate girder bottom and top, deck top
RIB, FL = .70, .05                               # solid plate rib depth and flange plate thickness
PED, SPRING = 1.6, 4.0                           # pedestal top, arch springing (rib centre line), low on the columns
RISE = 5.3                                       # rib rise: a near-semicircle on the 15 m span
CROWN = SPRING + RISE                            # rib centre line at the crown, about 0.4 x rise below the girder: a full spandrel lattice runs over it
TSPRING = 8.1                                    # springing of the transverse portal arches between paired columns
TX = 1.9                                         # track centres at x = +-TX
EAST_STRIP, LANE, ROAD, WALK = 6.6, 9.0, 19.0, 23.0   # east kerb lines (x)
WEST = -13.0                                     # west promenade edge (x)
T = .3
EPS = .002
PALETTE = dict(steel=(.40, .45, .46), plate=(.35, .40, .42), rivet=(.30, .34, .35), concrete=(.68, .67, .64),
    paving=(.70, .68, .64), joint=(.56, .55, .52), red=(.55, .19, .16), asphalt=(.24, .24, .25), white=(.92, .92, .90),
    stone=(.66, .65, .62), timber=(.36, .27, .19), hardware=(.12, .12, .13), silver=(.80, .80, .78), dark=(.10, .11, .12),
    glass=(.20, .24, .27), pale=(.88, .88, .86), brick=(.56, .31, .22), brick2=(.62, .38, .27), trim=(.86, .84, .80),
    roof=(.74, .73, .70), wall=(.56, .31, .22), interior=(.82, .78, .72), floor=(.58, .48, .38), planting=(.30, .44, .20),
    tree=(.28, .44, .18), soil=(.24, .18, .12), sand=(.66, .60, .50), blue=(.20, .30, .40), deck=(.25, .27, .28))


def manifest(version):
    h = DT + 7.0
    w, d = 70.0, Y1 - Y0
    cams = G.camera_roster(w, d, h, [
        ('facade_close', (0.5, -48.0, 18.5), (-CX, -55.5, 14.6), 35),          # bowstring close: the inner face at the south shoe and first panels
        ('architecture_close', (9.5, 8.0, 9.0), (CX, 15.0, 9.5), 40),
        ('glass_close', (7.5, -8.0, 15.4), (TX, -14.0, 15.4), 40),
        ('arch_span', (19.0, 7.5, 4.0), (CX, 7.5, 7.5), 40),
        ('column_base', (7.5, -5.0, 1.7), (CX, 0.0, 2.6), 40),
        ('lattice_detail', (9.5, 27.0, 9.6), (CX, 22.5, 10.4), 40),
        ('track_deck', (-.2, 6.5, 17.4), (-.2, 32.0, DT), 40),                 # above the deck between the tracks, north of the train
        ('train_cars', (7.5, -4.0, 16.6), (TX, -12.0, 15.2), 40),
        ('street_under', (5.5, 42.0, 1.7), (-1.0, 10.0, 6.5), 35),
        ('rear_north', (2.0, Y1 + 32.0, 17.0), (0.0, Y1 - 10.0, 9.0), 40)])
    for c in cams:
        if c['name'] == 'front':                 # the locked front: from the east strip, the arches receding south on the right
            c.update(location=(13.5, 52.0, 1.6), target=(2.0, 18.0, 7.0), lens=26, whole=False)
        elif c['name'] == 'front_corner':        # the locked oblique: high in the south-west over the bowstring end
            c.update(location=(-31.0, Y0 - 31.0, 44.0), target=(3.0, -14.0, 5.0), lens=30, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(48.0, Y0 - 12.0, 56.0), target=(0.0, -6.0, 6.0), lens=30, whole=False)
        elif c['name'] == 'top':                 # the locked top is a steep oblique from the south-west
            c.update(location=(30.0, Y0 - 6.0, 74.0), target=(0.0, -2.0, 6.0), lens=30, whole=False)
            c.pop('ortho_scale', None)                                           # a perspective, like the locked top
        elif c['name'] == 'left_side':
            c.update(location=(-11.5, -22.0, 26.0), target=(2.0, 8.0, 7.0), lens=26, whole=False)
        elif c['name'] == 'right_side':
            c.update(location=(34.0, 4.0, 40.0), target=(0.0, 0.0, 8.0), lens=30, whole=False)
        elif c['name'] == 'rear':
            c.update(location=(-6.0, Y1 + 52.0, 32.0), target=(0.0, Y1 - 24.0, 8.0), lens=30, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(46.0, Y1 + 40.0, 42.0), target=(0.0, 10.0, 6.0), lens=30, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='rail_transit_viaduct/variant_2 (Steel Through-Truss Rail)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=0, storey_programme='street option: an elevated rail viaduct over a promenade beside a street; the blocks are context',
            plan=f'{X1 - X0:.1f} m twin-track deck, {Y1 - Y0:.0f} m modelled run (top view): a {BOW:.0f} m bowstring through-truss at the south end, then {SPANS} deck-arch spans of {SP:.0f} m',
            facade='solid riveted plate-rib deck arches with open latticed spandrels and plate girders on built-up columns and concrete pedestals; riveted transverse portal arches; a bowstring through-truss; edge railings',
            section_m=dict(promenade=[WEST, X0], viaduct=[X0, X1], east_strip=[X1, EAST_STRIP], cycle_lane=[EAST_STRIP, LANE], road=[LANE, ROAD], sidewalk=[ROAD, WALK]),
            levels_m=[0.0, PED, SPRING, round(CROWN, 2), GB, GT, DT], inferred='the run is cut at both ends; the blocks are simplified context'),
        roof_contract=dict(type='open street option; elevated twin-track deck', datum_m=DT, crowns_m=[DT + 6.5]),
        identity_contract=dict(owner='long elevated riveted steel arch viaduct on columns over a street, latticed spandrels, twin tracks and a train'),
        material_contract=dict(profile='source-palette clay: grey-green riveted steel, pale concrete pedestals, timber sleepers and steel rails, silver train, pale paving, red cycle lane, dark road, red-brown brick blocks', textured_keeper=False),
        programme_contract=dict(storeys=0, ground='promenade, cycle lane and road beneath and beside the viaduct', upper='rail deck'),
        street_contract=dict(kind='fixed_native_section', width_m=WALK - WEST, axis='y', junction_finish='paving',
                             bands=['promenade', 'viaduct', 'east_strip', 'cycle_lane', 'road', 'sidewalk']),
        contact_contract=['Paving, lane and road at grade', 'Pedestals from grade, columns on pedestals', 'Arches and girders on the columns', 'Deck, sleepers and rails on the girders'],
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
# ---- Elevated steel rail viaduct ----

BOWEND = Y0 + BOW
COLS = [Y0, Y0 + BOW / 2, BOWEND] + [BOWEND + SP * k for k in range(1, SPANS + 1)]   # the deck arches run on under the bowstring too


def arc3(ya, yb, z0, zc, n):
    """Points on the circular arc through (ya, z0), the crown (mid, zc) and (yb, z0)."""
    c, r = yb - ya, zc - z0
    R = (c * c / 4 + r * r) / (2 * r)
    ym, zm = (ya + yb) / 2, zc - R
    a0 = math.asin(min(1.0, (c / 2) / R))
    return [(ym + R * math.sin(-a0 + 2 * a0 * i / n), zm + R * math.cos(-a0 + 2 * a0 * i / n)) for i in range(n + 1)]


def arc_z(ya, yb, z0, zc, y):
    c, r = yb - ya, zc - z0
    R = (c * c / 4 + r * r) / (2 * r)
    ym, zm = (ya + yb) / 2, zc - R
    return zm + math.sqrt(max(0.0, R * R - (y - ym) ** 2))


def chain(b, role, x, pts, w, d):
    """Consecutive beams along a polyline in the plane x; alternating widths so the overlapping joints share no plane."""
    for i, ((ya, za), (yb, zb)) in enumerate(zip(pts, pts[1:])):
        b.beam(role, (x, ya, za), (x, yb, zb), w + .03 * (i % 2), d, ext=.06)


def arc_frame(ya, yb, z0, zc):
    """Centre (ym, zm), radius and half-angle of the circular arc through (ya, z0), the crown (mid, zc) and (yb, z0)."""
    c, r = yb - ya, zc - z0
    R = (c * c / 4 + r * r) / (2 * r)
    return (ya + yb) / 2, zc - R, R, math.asin(min(1.0, (c / 2) / R))


def sweep(b, role, ring_at, n):
    """A solid swept through n + 1 stations; ring_at(i) gives the four corners of station i (one hexahedron per step)."""
    rings = [ring_at(i) for i in range(n + 1)]
    for r0, r1 in zip(rings, rings[1:]):
        b._hex(role, list(r0) + list(r1))


def curved_plate(b, role, plane, at, ym, zm, r0, r1, a0, a1, w, n, axis='x'):
    """A ring-sector plate of thickness w about the plane at `at` (x = at for axis 'x', y = at for axis 'y'),
    between radii r0 and r1 and angles a0..a1 measured from the vertical about the centre (ym, zm)."""
    def pt(u, rad, ang):
        h, z = ym + rad * math.sin(ang), zm + rad * math.cos(ang)
        return (at + u, h, z) if axis == 'x' else (h, at + u, z)
    def ring_at(i):
        ang = a0 + (a1 - a0) * i / n
        return [pt(-w / 2, r0, ang), pt(w / 2, r0, ang), pt(w / 2, r1, ang), pt(-w / 2, r1, ang)]
    sweep(b, role, ring_at, n)


def plate_rib(b, x, ya, yb, z0, zc, n=16, axis='x', depth=RIB, web=.30, flange=.60, rivet_pitch=1.2):
    """A solid built-up riveted plate rib: a curved web, intrados and extrados flange plates, two rivet rows a side.
    (ya, z0)-(yb, z0) is the springing chord of the rib centre line, zc its crown."""
    ym, zm, R, a = arc_frame(ya, yb, z0, zc)
    ri, ro = R - depth / 2, R + depth / 2
    curved_plate(b, 'plate', 'web', x, ym, zm, ri + .02, ro - .02, -a, a, web, n, axis)
    curved_plate(b, 'steel', 'intrados flange', x, ym, zm, ri - FL + .02, ri + .02, -a + .004, a - .004, flange, n, axis)
    curved_plate(b, 'steel', 'extrados flange', x, ym, zm, ro - .02, ro + FL - .02, -a + .004, a - .004, flange, n, axis)
    m = max(2, int(R * 2 * a / rivet_pitch))
    for i in range(1, m):
        ang = -a + 2 * a * i / m
        for rad in (ri + .12, ro - .12):
            h, z = ym + rad * math.sin(ang), zm + rad * math.cos(ang)
            for sd in (-1, 1):
                if axis == 'x':
                    b.box('rivet', x + sd * (web / 2 + .012), h, z, .03, .06, .06)
                else:
                    b.box('rivet', h, x + sd * (web / 2 + .012), z, .06, .03, .06)
    return ym, zm, ro + FL - .02


def extrados_z(ym, zm, rtop, y):
    return zm + math.sqrt(max(0.0, rtop * rtop - (y - ym) ** 2))


def columns(b):
    for j, y in enumerate(COLS):
        end = j in (0, len(COLS) - 1)
        top = GB - .7 if end else GB                                                          # end bents stop inside the end cap girder
        for x in (-CX, CX):
            b.box('concrete', x, y, PED / 2, 1.8, 1.8, PED)
            b.box('concrete', x, y, PED + .1, 1.4, 1.4, .2)
            b.box('plate', x, y, PED + .25, 1.3, 1.3, .1)
            for s in (-1, 1):                                                                 # gusseted base shoe
                b.beam('plate', (x + s * .62, y, PED + .3), (x + s * .47, y, PED + 1.3), .5, .05)
            b.box('steel', x, y, (PED + .3 + top) / 2, .9, .9, top - PED - .3)
            for s in (-1, 1):                                                                 # built-up flanges
                b.box('plate', x + s * .51, y, (PED + .3 + top) / 2, .12, 1.1, top - PED - .3)
            b.box('plate', x, y, SPRING + .15, 1.16, 1.2, .5)                                 # springing seat
            if not end:
                b.box('plate', x, y, GB - .35, 1.2, 1.3, .6)                                  # capital flare under the girder
        if not end and j > 0:                                                                 # transverse riveted portal arch
            xa, xb = -CX + .30, CX - .30
            ym_, zm_, rt = plate_rib(b, y, xa, xb, TSPRING, GB - .82, n=12, axis='y', depth=.5, web=.26, flange=.46, rivet_pitch=2.2)
            b.box('steel', 0.0, y, GB - .3, 2 * CX - .9, .5, .5)                              # portal head girder
            for xp in (-2.0, -1.0, 1.0, 2.0):                                                 # spandrel posts
                zt = extrados_z(ym_, zm_, rt, xp)
                if GB - .55 - zt > .15:
                    b.box('steel', xp, y, (zt + GB - .52) / 2, .22, .28, GB - .52 - zt)


def deck_arches(b):
    """Deck arches: a solid riveted plate rib in each plane, springing low from the columns, its crown well below the
    plate girder, and a deep continuous open spandrel lattice over the whole span: evenly spaced vertical posts (one on
    the crown) with V-diagonals rising from gusseted nodes on the rib to the girder, as in the source front."""
    for k in range(len(COLS) - 1):
        c0, c1 = COLS[k], COLS[k + 1]
        ya, yb = c0 + .05, c1 - .05
        for x in (-CX, CX):
            ym, zm, rt = plate_rib(b, x, ya, yb, SPRING, CROWN, n=18, rivet_pitch=2.0)
            n = 12
            nodes = []                                                                           # (y, z on the rib extrados)
            for i in range(n + 1):
                y = c0 + .55 + (c1 - c0 - 1.1) * i / n
                nodes.append((y, extrados_z(ym, zm, rt, y) - .01))
            for i, (y, zt) in enumerate(nodes):
                if i in (0, n):
                    continue
                b.box('steel', x, y, (zt + GB - .04) / 2, .34, .30, GB - .04 - zt)             # vertical post
                for sd in (-1, 1):
                    b.box('plate', x + sd * .2, y, GB - .32, .04, .62, .5)                       # gusset at the girder
            for i in range(n):                                                                   # V-diagonals: up from every even rib node
                (y0, z0), (y1, z1) = nodes[i], nodes[i + 1]
                if i % 2 == 0:
                    b.beam('steel', (x, y0, z0 + .1), (x, y1, GB - .14), .24, .20)
                else:
                    b.beam('steel', (x, y0, GB - .14), (x, y1, z1 + .1), .24, .20)


def bowstring(b):
    """The bowstring at the south end, as in the locked oblique and top: in each girder plane a heavy riveted arched
    truss rises low over the deck (crown about at the car roof): a deep built-up arched top chord (curved web, flange
    plates, rivet rows), a deep riveted bottom chord along the deck edge, built-up verticals, a heavy main diagonal and a
    lighter counter in every panel, riveted gusset plates at the nodes. Below the deck the same planes carry the viaduct's
    own plate-rib arches down to columns on concrete pedestals (deck_arches), so the truss reads as standing on the arcade.
    Open above (no overhead struts), like the sources."""
    ya, yb = Y0 + .35, BOWEND - .35
    zb, zc = DT + .45, DT + 4.5                                  # top-chord centre line: springing at the deck, crown at car-roof height
    dep, web, fl = .9, .46, .72
    for x in (-CX, CX):
        sx = 1 if x > 0 else -1
        ym, zm, rt = plate_rib(b, x, ya, yb, zb, zc, n=24, depth=dep, web=web, flange=fl, rivet_pitch=1.3)
        ri = rt - dep - FL + .02                                 # intrados face of the top chord
        zbt = DT + .62                                           # bottom chord top
        b.box('steel', x, (ya + yb) / 2, (GT - .22 + zbt) / 2, .56, yb - ya, zbt - GT + .22)   # deep riveted bottom chord
        b.box('plate', x, (ya + yb) / 2, zbt + .025, .76, yb - ya + .02, .05)                    # top cover plate
        m = int((yb - ya) / 1.5)
        for i in range(m):
            y = ya + .75 + i * 1.5
            for sd in (-1, 1):
                b.box('rivet', x + sd * .292, y, zbt - .14, .03, .06, .06)
        for yy in (ya, yb):                                      # bearing shoes over the cap girders
            b.box('plate', x, yy + (.25 if yy == ya else -.25), (GT - .25 + zbt) / 2, .8, .7, zbt - GT + .25)
        n = 10
        nodes = []                                               # (y, z of the top chord intrados)
        for i in range(n + 1):
            y = ya + (yb - ya) * i / n
            nodes.append((y, zm + math.sqrt(max(0.0, ri * ri - (y - ym) ** 2))))
        for i, (y, zt) in enumerate(nodes):
            if i in (0, n) or zt - zbt < .3:
                continue
            b.box('steel', x, y, (zbt + zt) / 2 + .02, .40, .30, zt - zbt + .1)                   # built-up vertical: web
            for s in (-1, 1):
                b.box('plate', x, y + s * .17, (zbt + zt) / 2 + .02, .52, .04, zt - zbt + .06)   # flange plates
            if zt - .8 > zbt + .9:                                   # riveted gussets both faces, top and bottom of the vertical
                gus = [(zbt + .45, .9, (zbt + .45,)), (zt - .4, .8, (zt - .4,))]
            else:                                                    # short end-panel vertical: one full-height gusset, never two
                gus = [((zbt + zt) / 2, zt - zbt, (zbt + .3, zt - .3))]  # overlapping coincident plates (they rendered black)
            for zz, hh, rows in gus:
                for sd in (-1, 1):
                    b.box('plate', x + sd * .275, y, zz, .03, 1.0, hh)
                    for zr in rows:
                        for dy in (-.25, .25):
                            b.box('rivet', x + sd * .293, y + dy, zr, .02, .05, .05)
        rf = ri - .005                                           # just inside the intrados flange plate
        def end_fill(y_from, y_to, k=10):                        # solid riveted end-panel plate between the chords at each shoe:
            def ring_at(j):                                      # closes the narrow wedge slot the low top chord made with the bottom chord
                y = y_from + (y_to - y_from) * j / k
                ztop = max(zbt + .08, zm + math.sqrt(max(0.0, rf * rf - (y - ym) ** 2)))
                return [(x - .35, y, zbt + .03), (x + .35, y, zbt + .03), (x + .35, y, ztop), (x - .35, y, ztop)]
            sweep(b, 'plate', ring_at, k)
            for j in range(1, int(abs(y_to - y_from) / .6)):
                y = min(y_from, y_to) + j * .6
                ztop = zm + math.sqrt(max(0.0, rf * rf - (y - ym) ** 2))
                for zz in (zbt + .2, zbt + .55):
                    if ztop - zz > .15:
                        for sd in (-1, 1):
                            b.box('rivet', x + sd * .362, y, zz, .03, .06, .06)
        end_fill(ya, nodes[1][0])
        end_fill(nodes[n - 1][0], yb)
        mid = n // 2
        for i in range(n):                                       # heavy main diagonal falling towards midspan, a lighter counter
            (y0, z0), (y1, z1) = nodes[i], nodes[i + 1]
            if i < mid:
                main = ((y0, zbt - .05), (y1, z1 - .05)) if i > 0 else ((y0 + .4, zbt - .05), (y1, z1 - .05))
                ctr = ((y0, z0 - .05), (y1, zbt - .05)) if i > 0 else None
            else:
                main = ((y0, z0 - .05), (y1, zbt - .05)) if i < n - 1 else ((y0, z0 - .05), (y1 - .4, zbt - .05))
                ctr = ((y0, zbt - .05), (y1, z1 - .05)) if i < n - 1 else None
            if min(main[0][1], main[1][1]) < zbt - .1 and max(main[0][1], main[1][1]) - zbt < .5:
                continue
            b.beam('steel', (x, main[0][0], main[0][1]), (x, main[1][0], main[1][1]), .34, .26)
            if ctr and max(ctr[0][1], ctr[1][1]) - zbt > .6:
                b.beam('plate', (x - sx * .09, ctr[0][0], ctr[0][1]), (x - sx * .09, ctr[1][0], ctr[1][1]), .18, .14)


def girders_and_deck(b):
    for x in (-CX, CX):
        b.box('steel', x, 0.0, (GB + GT) / 2, .46, Y1 - Y0, GT - GB)                            # plate girders, end to end
        b.box('plate', x, 0.0, GB + .01, .72, Y1 - Y0 + .02, .12)                               # bottom flanges
        for k in range(int((Y1 - Y0) / 1.875) + 1):                                            # web stiffeners
            y = Y0 + .2 + k * 1.875
            for s in (-1, 1):
                b.box('plate', x + s * .245, y, (GB + .07 + GT) / 2, .03, .14, GT - GB - .07)
    for y, top in ((Y0, DT - .02), (BOWEND, GT + .1), (Y1, DT - .02)):                       # closed cap girders on the end and bowstring bents
        b.box('plate', 0.0, y, (GB - .7 + top) / 2, 2 * (X1 + .7), 1.1, top - GB + .7)
        for sd in (-1, 1):
            for k in range(13):
                b.box('rivet', -(X1 + .55) + k * (2 * X1 + 1.1) / 12, y + sd * .562, GB - .45, .06, .03, .06)
    for k in range(int((Y1 - Y0) / 3.75) + 1):                                                 # floor beams under the deck
        b.box('steel', 0.0, Y0 + .4 + k * 3.75, GT - .3, 2 * CX - .46, .36, .6)
    b.box('deck', 0.0, 0.0, (GT + DT) / 2, X1 - X0, Y1 - Y0, DT - GT)                         # dark steel deck plate
    n = int((Y1 - Y0) / .7)
    for xt in (-TX, TX):                                                                       # sleepers and rails
        for k in range(n):
            b.box('timber', xt, Y0 + .35 + k * .7, DT + .075, 2.6, .25, .15)
        for s in (-1, 1):
            b.box('hardware', xt + s * .72, 0.0, DT + .23, .07, Y1 - Y0 - .1, .16)
    for x in (X0 + .15, X1 - .15):                                                             # deck edge railings
        for k in range(int((Y1 - Y0) / 2.5) + 1):
            b.box('hardware', x, Y0 + .1 + k * 2.5 - (.2 if k == int((Y1 - Y0) / 2.5) else 0), DT + .55, .07, .07, 1.1)
        b.box('hardware', x, 0.0, DT + 1.12, .09, Y1 - Y0, .07)
        b.box('hardware', x, 0.0, DT + .6, .05, Y1 - Y0, .04)


def gaps(lo, hi, cuts):
    """The solid intervals of [lo, hi] left between the sorted cut intervals."""
    out, y = [], lo
    for c0, c1 in sorted(cuts):
        if c0 > y + .01:
            out.append((y, c0))
        y = max(y, c1)
    if hi > y + .01:
        out.append((y, hi))
    return out


def train():
    """A silver stainless train of three cars on the street-side (east) track, entering the bowstring span: a dark interior core
    behind a silver skin cut by real window openings (glazing set back in the reveal) and recessed door leaves."""
    xt, z0 = TX, DT + .31
    zb, zw0, zw1, zt = z0 + .5, z0 + 1.9, z0 + 2.95, z0 + 3.9          # body bottom, window band, body top
    b = Batch()
    y = -52.0
    for k in range(3):
        L = 18.0
        y0, y1 = y, y + L
        yc = (y0 + y1) / 2
        for yb in (y0 + 2.4, y1 - 2.4):
            b.box('dark', xt, yb, z0 + .25, 2.3, 2.6, .5)                                         # bogies
        b.box('dark', xt, yc, (zb + zt) / 2, 2.8, L - .24, zt - zb - .02)                       # interior core
        b.box('silver', xt, yc, zt - .06, 3.0, L, .12)                                          # roof skin
        b.box('pale', xt, yc, zt + .12, 2.7, L - .4, .24)
        for j in range(3):
            b.box('pale', xt, y0 + 4.0 + j * 5.0, zt + .24 + .15, 1.4, 1.8, .3)                 # roof units
        doors = [(y0 + 2.2 + j * (L - 4.4) / 3 - .65, y0 + 2.2 + j * (L - 4.4) / 3 + .65) for j in range(4)]
        wins = []
        for (p0, p1) in gaps(y0 + .35, y1 - .35, doors):
            n = max(1, int((p1 - p0 - .3) / 1.35))
            w = (p1 - p0 - .3 * (n + 1)) / n
            wins += [(p0 + .3 + i * (w + .3), p0 + .3 + i * (w + .3) + w) for i in range(n)]
        for sd in (-1, 1):
            xs = xt + sd * 1.45                                                                  # skin centre (faces at 1.40 and 1.50)
            for (p0, p1) in gaps(y0, y1, doors):
                b.box('silver', xs, (p0 + p1) / 2, (zb + zw0) / 2, .1, p1 - p0, zw0 - zb)       # skirt below the windows
            b.box('silver', xs, yc, (zw1 + zt - .12) / 2, .1, L, zt - .12 - zw1)               # band above the windows
            for (p0, p1) in gaps(y0, y1, doors + wins):                                          # piers between the openings
                b.box('silver', xs, (p0 + p1) / 2, (zw0 + zw1) / 2, .1, p1 - p0, zw1 - zw0)
            for (p0, p1) in wins:                                                                # glazing set 7 cm back, a frame round it
                b.box('glass', xt + sd * 1.42, (p0 + p1) / 2, (zw0 + zw1) / 2, .02, p1 - p0 + .02, zw1 - zw0 + .02)
                b.box('hardware', xt + sd * 1.425, (p0 + p1) / 2, zw0 + .03, .03, p1 - p0, .06)
            for (p0, p1) in doors:                                                               # recessed leaves with door windows
                b.box('plate', xt + sd * 1.43, (p0 + p1) / 2, (zb + .1 + zw1) / 2, .04, p1 - p0 + .02, zw1 - zb - .1)
                b.box('glass', xt + sd * 1.452, (p0 + p1) / 2, zw0 + .45, .006, .9, .9)
                b.box('silver', xt + sd * 1.45, (p0 + p1) / 2, zb + .05, .1, p1 - p0, .1)        # threshold
        for ye, sd in ((y0, -1), (y1, 1)):                                                       # end skins
            cab = k == 0 and ye == y0
            yy = ye + sd * -.055                                                                 # outer face 5 mm inside the side-skin ends
            for s2 in (-1, 1):                                                                   # corner posts wrap the side/end corner
                b.box('silver', xt + s2 * 1.45, ye - sd * .06, (zb + zt - .12) / 2, .14, .14, zt - .12 - zb)
            if cab:                                                                              # cab end: inset windscreen and headlights
                b.box('silver', xt, yy, (zb + zw0) / 2, 2.8, .1, zw0 - zb)
                b.box('silver', xt, yy, (zw1 + zt - .12) / 2, 2.8, .1, zt - .12 - zw1)
                for s2 in (-1, 1):
                    b.box('silver', xt + s2 * 1.25, yy, (zw0 + zw1) / 2, .3, .1, zw1 - zw0)
                b.box('glass', xt, ye + .06, (zw0 + zw1) / 2, 2.22, .02, zw1 - zw0 + .02)
                for s2 in (-1, 1):
                    b.box('dark', xt + s2 * 1.0, ye - .01, zb + .55, .38, .02, .26)
                    b.box('pale', xt + s2 * 1.0, ye - .025, zb + .55, .3, .02, .18)
            else:
                b.box('silver', xt, yy, (zb + zt - .12) / 2, 2.8, .1, zt - .12 - zb)
                b.box('dark', xt, ye + sd * .02, (zb + zt) / 2 - .2, 1.0, .03, 2.0)               # gangway door
        y = y1 + .8
    b.flush('train')


def street():
    ya, yb = Y0 - 6.0, Y1 + 6.0
    L = yb - ya
    C.box('Promenade paving', ((WEST + EAST_STRIP) / 2, 0.0, .06), (EAST_STRIP - WEST, L, .12), 'paving', 'street', 0)
    C.box('East kerb', (EAST_STRIP + .1, 0.0, .07), (.2, L, .14), 'stone', 'street', 0)
    C.box('Cycle lane', ((EAST_STRIP + .2 + LANE) / 2, 0.0, .025), (LANE - EAST_STRIP - .2, L, .05), 'red', 'street', 0)
    C.box('Road', ((LANE + ROAD) / 2, 0.0, .02), (ROAD - LANE, L, .04), 'asphalt', 'street', 0)
    C.box('Road kerb', (ROAD + .1, 0.0, .07), (.2, L, .14), 'stone', 'street', 0)
    C.box('Sidewalk', ((ROAD + .2 + WALK) / 2, 0.0, .06), (WALK - ROAD - .2, L, .12), 'paving', 'street', 0)
    b = Batch()
    for k in range(int(L / 1.5)):
        b.box('joint', (WEST + EAST_STRIP) / 2, ya + .75 + k * 1.5, .121, EAST_STRIP - WEST - .02, .03, .004)
        b.box('joint', (ROAD + .2 + WALK) / 2, ya + .75 + k * 1.5, .121, WALK - ROAD - .22, .03, .004)
    for x in (WEST + 1.5 + 1.5 * k for k in range(int((EAST_STRIP - WEST) / 1.5) - 1)):
        b.box('joint', x, 0.0, .121, .03, L - .02, .004)
    b.box('white', LANE, 0.0, .052, .12, L, .01)
    for k in range(int(L / 6.0)):
        b.box('white', (LANE + ROAD) / 2, ya + 1.5 + k * 6.0, .045, .14, 3.0, .01)
    b.flush('street markings')
    for y in (-50.0, -34.0, -18.0, -2.0, 14.0, 30.0, 46.0):
        street_tree(WEST + 3.5, y, z=.12, height=7.5, spread=2.0)
    for y in (-40.0, -10.0, 20.0, 50.0):
        street_tree(ROAD + 1.8, y, z=.12, height=7.0, spread=1.8)


def blocks():
    """Flat-roofed brick apartment blocks as context: framed windows on the street faces, coped parapets, roof units."""
    for side, x0, x1, fx, dx, spans in (('West', WEST - 20.0, WEST, WEST, 1, ((-66.0, -30.0, 15.0), (-24.0, 8.0, 18.0), (14.0, 66.0, 15.0))),
                                        ('East', WALK, WALK + 17.0, WALK, -1, ((-66.0, -22.0, 14.0), (-16.0, 22.0, 16.0), (28.0, 66.0, 13.0)))):
        for i, (y0, y1, h) in enumerate(spans):
            role = 'brick' if i % 2 == 0 else 'brick2'
            C.box(f'{side} block {i}', ((x0 + x1) / 2, (y0 + y1) / 2, h / 2), (x1 - x0, y1 - y0, h), role, 'context', 0)
            b = Batch()
            b.box('roof', (x0 + x1) / 2, (y0 + y1) / 2, h + .03, x1 - x0 - .6, y1 - y0 - .6, .06)
            for (cx, cy, sx, sy) in (((x0 + x1) / 2, y0 + .15, x1 - x0, .3), ((x0 + x1) / 2, y1 - .15, x1 - x0, .3),
                                     (x0 + .15, (y0 + y1) / 2, .3, y1 - y0 - .6), (x1 - .15, (y0 + y1) / 2, .3, y1 - y0 - .6)):
                b.box('trim', cx, cy, h + .3, sx + .04, sy + .04, .6)
            for j in range(3):
                b.box('pale', (x0 + x1) / 2 + (j - 1) * 3.0, (y0 + y1) / 2 + (j - 1) * 5.0, h + .7, 2.0, 2.6, 1.4)
            n = int((y1 - y0 - 2.0) / 3.0)
            for f in range(int((h - 1.0) / 3.0)):
                z = 1.3 + f * 3.0
                for j in range(n):
                    y = y0 + 2.5 + j * 3.0
                    sg = 1 if dx > 0 else -1                 # one frame plate with the glass proud of it: no corner joints
                    b.box('trim', fx + sg * .03, y, z + .9, .06, 1.5, 1.9)
                    b.box('glass', fx + sg * .07, y, z + .9, .02, 1.3, 1.7)
                    b.box('stone', fx + (.09 if dx > 0 else -.09), y, z - .02, .16, 1.6, .1)
            b.flush(f'{side} block {i} details')


def build():
    b = Batch()
    columns(b)
    deck_arches(b)
    bowstring(b)
    girders_and_deck(b)
    b.flush('viaduct steel')
    train()
    street()
    blocks()
    C.CONTACTS.append(dict(name='Concrete pedestals from grade, steel columns on them; deck arches and the bowstring on the columns; girders, deck, sleepers and rails above', box=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(40, -35, 50), fill=(-45, -20, 35), rear=(-15, 45, 35), target=(0, -5, 8.0), gain=3.6)
