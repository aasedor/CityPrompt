"""Downtown elevated CTrain station, authored from the locked catalogue views of
calgary_ctrain_station / variant_0 (ctrain_downtown_platform).

Read from the pixels (the top view governs the plan): a three-storey red-brick headhouse whose south
face meets an elevated light-rail guideway. Square brick stair towers stand at its two south corners,
each with a tall glazed stair bay on its outer face and a pale projecting cap above the roof; a
continuous glazed band runs along the top storey between them. Two side platforms flank two tracks on
a concrete deck carried on round piers and cap beams over the east-west street; each platform has a
long glazed gable canopy on steel posts, glass guards on the outer edges, yellow tactile edges and a
red station pylon at its south end. A glazed steel-truss Plus 15 skywalk leaves the west face across
the west street; another links the east face to a long north-south skywalk on columns over the east
street. A two-car red-and-white light-rail train stands at the west platform.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-ctrain-elevated-station'
T = .32
G0 = .15
HX0, HX1, HY0, HY1 = -18.0, 18.0, -11.0, 22.0     # headhouse (top view at 0.115 m/px)
L2, L3, ROOF = 6.0, 10.0, 14.0                    # platform level, upper concourse, roof
PARA = ROOF + .8
TW = 6.5                                          # corner stair towers
TOWER_TOP = 17.6
DECK = 5.1                                        # top of the track bed
PLAT = 6.0                                        # top of the platforms (= level 2)
DY0 = -46.0                                       # south end of the deck
PX = (4.0, 10.0)                                  # platform band (each side, mirrored)
CAN_Y = (-11.0, -31.0)                            # canopy run
STREET = (-36.0, -20.0)                           # east-west street under the deck
SKY_Z = (L2 + .5, L3 - .2)                        # Plus 15 skywalk floor and roof
SKY_W = (-2.8, 5.0)                               # west skywalk centre y and width: right beside the SW tower (top view)
SKY_E = (-3.7, 3.2)                               # east link centre y and width: right beside the SE tower
TAIL = 18.0                                       # tail track north of the headhouse
EXT = 10.0                                        # level guarded deck continuing south past the platform ends
STAIR_Y = (-44.0, -42.0)                          # street stairs at the platform south ends
EPS = .002
PALETTE = dict(wall=(.55, .28, .21), joint=(.40, .20, .15), trim=(.40, .42, .44),
    pale=(.86, .85, .82), stone=(.70, .68, .64), roof=(.72, .71, .68), sand=(.68, .66, .62),
    foundation=(.42, .42, .41), glass=(.50, .60, .64), hardware=(.30, .31, .33),
    interior=(.80, .76, .68), floor=(.46, .44, .42), timber=(.40, .28, .16), blue=(.14, .22, .28),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.56, .55, .52), asphalt=(.30, .30, .31),
    tactile=(.86, .70, .16), signal=(.70, .10, .10), train=(.66, .12, .12), white=(.90, .90, .88),
    rail=(.36, .34, .32), membrane=(.74, .73, .70))


def manifest(version):
    h = TOWER_TOP + 1.0
    cams = G.camera_roster(44.0, 50.0, h, [
        ('facade_close', (-30.0, -26.0, 6.0), (-14.75, -12.0, 8.0), 45),
        ('architecture_close', (-20.0, -34.0, 14.0), (-7.0, -12.0, 9.0), 45),
        ('glass_close', (-14.0, -30.0, 12.0), (-7.0, -24.0, 9.6), 45),
        ('platform_canopy', (-7.0, -38.0, 7.7), (-7.0, -14.0, 7.6), 45),
        ('skywalk_bridge', (-30.0, -22.0, 4.0), (-28.0, 2.0, 8.2), 45),
        ('street_underpass', (-18.0, -28.0, 1.7), (6.0, -28.0, 3.6), 40),
        ('tower_cap', (-30.0, -30.0, 22.0), (-14.75, -8.75, 16.5), 45),
        ('train_platform', (4.0, -40.0, 9.0), (-2.0, -22.0, 6.8), 45),
        ('interior', (0.0, 8.0, L3 + 1.7), (0.0, -11.0, L3 + 1.2), 60),
        ('east_skywalk', (48.0, -30.0, 14.0), (29.0, -6.0, 8.0), 45)])
    for c in cams:
        if c['name'] == 'front':        # eye level at the street corner, looking up at the south-west tower's glazed bay
            c['location'] = (-28.0, -26.0, 1.7); c['target'] = (-12.0, -10.0, 10.0); c['lens'] = 24; c['whole'] = False
        elif c['name'] in ('left_side', 'right_side'):   # raised so the deck, canopies and skywalks read; fit only moves out
            sx = -1 if c['name'] == 'left_side' else 1
            c['location'] = (sx * 40.0, -13.0, 24.0); c['target'] = (0.0, -13.0, 5.0); c['lens'] = 35
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='calgary_ctrain_station/variant_0 (ctrain_downtown_platform)',
        measurement_contract=dict(dimensions_m=dict(width=72.0, depth=72.0, height=h),
            observed_storeys=3, storey_programme='street lobby, platform-level concourse, upper concourse with the skywalk links',
            plan='36 x 26 m headhouse; twin 6 m side platforms either side of two tracks on an elevated deck running 35 m south over the east-west street and continuing level 10 m further; 20 m glazed canopies; west skywalk 22 m; east link and a 60 m north-south skywalk (top view at 0.115 m/px)',
            levels_m=[G0, L2, L3, ROOF], parapet_m=PARA, tower_top_m=TOWER_TOP, deck_m=DECK, platform_m=PLAT,
            facade='red brick with tall punched windows; glazed top-storey band between the towers; stair towers with full-height glazed bays and pale caps',
            inferred='storey heights and interiors are teaching assumptions; the neighbouring towers the skywalks reach are not part of the asset, so the skywalks end at glazed stair pavilions; the north face is not visible in any source'),
        roof_contract=dict(type='flat membrane with parapet; tower caps; shallow glazed gable canopies', datum_m=ROOF, crowns_m=[PARA, TOWER_TOP]),
        identity_contract=dict(owner='brick headhouse with glazed stair towers and pale caps, elevated side platforms with glazed gable canopies, guideway deck on piers over the street, Plus 15 skywalks, red station pylons, light-rail train'),
        material_contract=dict(profile='source-palette clay: red brick, grey steel frames, clear glass, pale concrete deck and piers, yellow tactile strips, red pylons, red-and-white train', textured_keeper=False),
        programme_contract=dict(storeys=3, ground='street lobby with stairs and lifts', level2='fare-paid concourse onto both platforms', level3='upper concourse and Plus 15 links', platforms='two side platforms with canopies, benches and pylons'),
        contact_contract=['Grade-zero street, sidewalks and pier footings', 'Deck on cap beams and round piers', 'Canopy posts on the platform slabs', 'Skywalks bearing on the headhouse and on columns', 'Train bogies on the rails'],
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


# ---- elevated CTrain station ----

class Batch:
    """Collect arbitrary boxes into one mesh per role (keeps the object count low)."""
    def __init__(self):
        self.g = {}

    def box(self, role, cx, cy, cz, sx, sy, sz):
        V, F = self.g.setdefault(role, ([], []))
        o = len(V)
        V.extend((cx + du * sx / 2, cy + dd * sy / 2, cz + dz * sz / 2) for dz in (-1, 1) for du, dd in ((-1, -1), (1, -1), (1, 1), (-1, 1)))
        F.extend(tuple(o + i for i in face) for face in C.BOX_FACES)

    def flush(self, module):
        for role, (V, F) in self.g.items():
            if F:
                C.mesh(f'{module} {role}', V, F, role, module)
        self.g = {}


def brick_wall(f, lo, hi, z0, z1, holes, courses=True, role='wall'):
    f.wall(f'{f.label} carrier', lo, hi - EPS, z0, z1, depth=T, role=role, holes=holes)
    if courses and role == 'wall':
        G.brick_courses(f, lo + .02, hi - .02, z0 + .02, z1 - .02, holes, spacing=.18)


def glaze(f, holes, occupied, cols_per=1.5, rows=1, inset=.12, frame='trim'):
    m = Merge(f)
    for h in holes:
        if h.get('kind') == 'portal':
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='track portal', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='trainshed'))
            continue
        if h.get('kind') == 'skywalk':
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='skywalk opening', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='skywalk'))
            continue
        cols = max(1, round(h['w'] / cols_per))
        framed(m, f, h, cols=cols, rows=h.get('rows', rows), inset=inset, occupied=occupied, kind=h.get('kind', 'window'), frame=frame)
        if h.get('sill', True) and h['z'] > 1.0:
            m.box('stone', h['u'], -.04, h['z'] - .06, h['w'] + .14, .14, .12)
    m.flush(f.label + ' glazing')


def headhouse():
    cx = (HX0 + HX1) / 2
    x0, x1 = HX0 + TW, HX1 - TW
    south = C.Face((0, HY0, 0), (1, 0, 0), (0, 1, 0), 'headhouse south')
    hw = (x1 - x0) / 2
    holes = [hole('south lobby doors west', -7.5, G0, 3.0, 3.2, kind='door', rows=2), hole('south lobby doors east', 7.5, G0, 3.0, 3.2, kind='door', rows=2),
             hole('track portal south', 0, DECK - .7, 8.6, 5.0, kind='portal'),
             hole('west platform doors', -7.0, PLAT + .05, 4.2, 3.0, kind='door', rows=2), hole('east platform doors', 7.0, PLAT + .05, 4.2, 3.0, kind='door', rows=2),
             hole('upper concourse band', 0, L3 + .45, 2 * hw - .6, ROOF - L3 - .75, rows=2)]
    brick_wall(south, -hw, hw, G0, PARA, holes)
    glaze(south, holes, 'concourse', cols_per=1.6)
    m = Merge(south)
    m.box('stone', 0, -.06, L3 + .2, 2 * hw - .02, T + .12, .32)                  # pale band under the glazed storey
    m.box('stone', 0, -.08, PARA + .05, 2 * hw - .02, T + .16, .12)
    m.box('trim', 0, -.6, DECK + 4.45, 9.6, 1.2, .25)                            # portal lintel hood
    m.flush('headhouse south')
    # East and west faces from the towers to the rear; skywalk openings right beside the towers.
    for side, xs, sgn in (('west', HX0, -1), ('east', HX1, 1)):
        f = C.Face((xs, (HY0 - 1 + TW + HY1) / 2, 0), (0, -sgn, 0), (-sgn, 0, 0), f'headhouse {side}')
        y0, y1 = HY0 - 1 + TW, HY1
        span = y1 - y0; lo, hi = -span / 2, span / 2
        def u_of(y):
            return -sgn * (y - (y0 + y1) / 2)
        sky_y = SKY_W[0] if side == 'west' else SKY_E[0]
        sky_w = SKY_W[1] if side == 'west' else SKY_E[1]
        hs = []
        for k, y in enumerate((-1.0, 5.0, 11.0, 17.0)):
            hs.append(hole(f'{side} lobby storefront {k}', u_of(y), G0 + .3, 3.8, 4.4, rows=2))
        hs.append(hole(f'{side} lobby entrance', u_of(20.0), G0, 2.6, 3.4, kind='door', rows=2))
        for k, y in enumerate((-2.0, 2.0, 6.0, 10.0, 14.0, 18.0)):
            if abs(y - sky_y) < sky_w / 2 + 1.4:
                continue
            hs.append(hole(f'{side} level 2 window {k}', u_of(y), L2 + .6, 1.8, 2.8, rows=2))
        hs.append(hole(f'{side} skywalk opening', u_of(sky_y), SKY_Z[0], sky_w - .2, SKY_Z[1] - SKY_Z[0] - .3, kind='skywalk'))
        hs.append(hole(f'{side} upper band', 0, L3 + .45, span - 1.2, ROOF - L3 - .75, rows=2))
        brick_wall(f, lo, hi, G0, PARA, hs)
        glaze(f, hs, 'concourse', cols_per=1.6)
        m = Merge(f)
        m.box('stone', 0, -.06, L3 + .2, span - .02, T + .12, .32)
        m.box('stone', 0, -.08, PARA + .05, span - .02, T + .16, .12)
        m.flush(f.label)
    north = C.Face((0, HY1, 0), (-1, 0, 0), (0, -1, 0), 'headhouse north')
    hw2 = (HX1 - HX0) / 2 - T
    hs = [hole(f'north window {k}-{j}', u, z, 1.8, 2.6) for j, z in enumerate((G0 + 1.2, L2 + .7)) for k, u in enumerate((-14.0, -9.0, 9.0, 14.0))]
    hs.append(hole('track portal north', 0, DECK - .7, 8.6, 5.0, kind='portal'))
    hs.append(hole('north upper band', 0, L3 + .45, 2 * hw2 - 1.0, ROOF - L3 - .75, rows=2))
    brick_wall(north, -hw2, hw2, G0, PARA, hs)
    glaze(north, hs, 'staff rooms')
    m = Merge(north)
    m.box('stone', 0, -.06, L3 + .2, 2 * hw2 - .02, T + .12, .32)
    m.box('stone', 0, -.08, PARA + .05, 2 * hw2 - .02, T + .16, .12)
    m.box('trim', 0, -.6, DECK + 4.45, 9.6, 1.2, .25)
    m.flush('headhouse north')
    # The tracks pass right through the headhouse in a trainshed between concrete walls; the concourse spans over it.
    ty0, ty1 = HY0 + T, HY1 - T
    C.box('Trainshed deck', (0, (ty0 + ty1) / 2, (4.4 + DECK) / 2), (8.6, ty1 - ty0, DECK - 4.4), 'concrete', 'trainshed', 0)
    for x in (-4.45, 4.45):
        C.box('Trainshed wall', (x, (ty0 + ty1) / 2, (G0 + DECK + 4.3) / 2), (.3, ty1 - ty0, DECK + 4.3 - G0), 'concrete', 'trainshed', 0)
    C.box('Trainshed ceiling', (0, (ty0 + ty1) / 2, DECK + 4.45), (9.2, ty1 - ty0, .3), 'concrete', 'trainshed', 0)
    for y in (HY0 + 4.0, (HY0 + HY1) / 2, HY1 - 4.0):
        C.qa_room_light(f'Trainshed {y:+.0f}', (0, y, DECK + 3.8), 70, 3.0)
    C.box('Headhouse ground slab', (cx, (HY0 + HY1) / 2, G0 / 2), (HX1 - HX0, HY1 - HY0, G0), 'foundation', 'headhouse', 0)
    for xa, xb in ((HX0 + T, -4.6), (4.6, HX1 - T)):
        C.box('Headhouse concourse slab', ((xa + xb) / 2, (ty0 + ty1) / 2, L2 - .15), (xb - xa, ty1 - ty0, .30), 'floor', 'headhouse', 0)
    for z, name in ((L3, 'upper concourse'), (ROOF, 'roof')):
        C.box(f'Headhouse {name} slab', (cx, (ty0 + ty1) / 2, z - .15), (HX1 - HX0 - 2 * T, ty1 - ty0, .30), 'floor', 'headhouse', 0)
    C.box('Roof membrane', (cx, (HY0 + HY1) / 2, ROOF + .01), (HX1 - HX0 - 2 * T - .02, HY1 - HY0 - 2 * T - .02, .02), 'membrane', 'roof', 0)
    C.box('Rooftop unit', (2.0, 12.0, ROOF + .7), (3.6, 2.2, 1.4), 'pale', 'roof', 0)
    C.box('Roof skylight curb', (-5.0, 6.0, ROOF + .3), (4.4, 3.2, .6), 'pale', 'roof', 0)
    C.box('Roof skylight', (-5.0, 6.0, ROOF + .62), (4.0, 2.8, .05), 'glass', 'roof', 0)
    # Lobby stairs and lifts either side of the trainshed, fare gates, upper concourse seating, lights.
    for x in (-11.0, 11.0):
        C.beam('Lobby stair', (x, HY0 + 4.0, G0 + .1), (x, HY0 + 12.0, L2 - .1), 2.4, .3, 'concrete', 'lobby')
        C.box('Lift shaft', (x + (2.6 if x > 0 else -2.6), HY0 + 14.0, (G0 + ROOF) / 2), (2.2, 2.2, ROOF - G0), 'glass', 'lobby', 0)
        for k in range(4):
            C.box('Fare gate', (x - 1.5 + k * 1.0, HY0 + 2.6, L2 + .5), (.2, 1.2, 1.0), 'hardware', 'concourse', 0)
    for x in (-10.0, -4.0, 4.0, 10.0):
        C.box('Concourse bench', (x, HY0 + 3.0, L3 + .45), (2.4, .5, .1), 'timber', 'upper concourse', 0)
        for e in (-1, 1):
            C.box('Concourse bench leg', (x + e * 1.0, HY0 + 3.0, L3 + .2), (.08, .4, .4), 'hardware', 'upper concourse', 0)
    for z in (G0, L2, L3):
        for x in (-10.0, 10.0):
            C.qa_room_light(f'Headhouse {x:+.0f} {z:.0f}', (x, HY0 + 4.0, z + 3.0), 110, 5.0)
    C.qa_room_light('Upper concourse centre', (0, HY0 + 5.0, ROOF - .6), 120, 6.0)
    C.CONTACTS.append(dict(name='Tracks pass through the headhouse in a trainshed under the concourse; deck abuts both faces', face_y=[HY0, HY1]))


def tower(xa, xb, side):
    """Square brick stair tower: a wide glazed stair bay projecting from its outer face between brick piers,
    and a pale cornice cap with a low hip."""
    ya, yb = HY0 - 1.0, HY0 - 1.0 + TW
    cx, cy = (xa + xb) / 2, (ya + yb) / 2
    s = C.Face((cx, ya, 0), (1, 0, 0), (0, 1, 0), f'{side} tower south')
    brick_wall(s, -TW / 2, TW / 2, G0, TOWER_TOP, [])          # brick-dominant south face, as in the sources
    outer_x, inner_x = (xa, xb) if side == 'west' else (xb, xa)
    sgn = -1 if side == 'west' else 1
    o = C.Face((outer_x, cy + T / 2, 0), (0, -sgn, 0), (-sgn, 0, 0), f'{side} tower outer')
    bw, bz0, bz1 = 4.0, G0 + .4, TOWER_TOP - 1.0
    bay = hole(f'{side} tower glazed stair bay', 0, bz0, bw, bz1 - bz0, kind='bay')
    brick_wall(o, -(TW - T) / 2, (TW - T) / 2, G0, TOWER_TOP, [bay])
    register(o, bay, -.6, 'projecting glazed bay', 'stair')
    m = Merge(o)
    d = -.65
    m.box('glass', 0, d, (bz0 + bz1) / 2, bw - .1, .02, bz1 - bz0 - .1)
    for e in (-1, 1):
        m.box('glass', e * (bw / 2 - .03), d / 2, (bz0 + bz1) / 2, .02, -d - .04, bz1 - bz0 - .1)
        m.box('trim', e * (bw / 2 - .05), d / 2 - .02, (bz0 + bz1) / 2, .1, -d + .02, bz1 - bz0)
    for k in range(5):
        m.box('trim', -bw / 2 + bw * k / 4, d - .04, (bz0 + bz1) / 2, .08, .1, bz1 - bz0)
    z = bz0
    while z <= bz1 + .01:
        m.box('trim', 0, d / 2 - .02, z, bw + .02, -d + .1, .12)
        z += 3.4
    m.box('trim', 0, d / 2 - .06, bz1 + .1, bw + .3, -d + .2, .2)
    m.box('trim', 0, d / 2 - .06, bz0 - .1, bw + .3, -d + .2, .2)
    m.flush(f'{side} tower bay')
    i = C.Face((inner_x, cy + T / 2, 0), (0, sgn, 0), (sgn, 0, 0), f'{side} tower inner')
    brick_wall(i, -(TW - T) / 2, (TW - T) / 2, G0, TOWER_TOP, [])
    n = C.Face((cx, yb, 0), (-1, 0, 0), (0, -1, 0), f'{side} tower north')
    brick_wall(n, -TW / 2 + T, TW / 2 - T, PARA - .2, TOWER_TOP, [])
    C.box(f'{side} tower cornice', (cx, cy, TOWER_TOP - .1), (TW + .7, TW + .7, .3), 'pale', 'towers', 0)
    C.box(f'{side} tower cap', (cx, cy, TOWER_TOP + .3), (TW + 1.2, TW + 1.2, .5), 'pale', 'towers', 0)
    h = TW / 2 + .45                       # eave edge kept inside the cap so no face lies on the cap fascia
    strip(f'{side} tower hip', [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h)],
          [(cx - 1.0, cy - 1.0), (cx + 1.0, cy - 1.0), (cx + 1.0, cy + 1.0), (cx - 1.0, cy + 1.0)], TOWER_TOP + .55, TOWER_TOP + 1.1, 'pale', 'towers')
    C.box(f'{side} tower hip top', (cx, cy, TOWER_TOP + 1.05), (2.1, 2.1, .1), 'pale', 'towers', 0)
    C.box(f'{side} tower roof', (cx, cy, TOWER_TOP - .3), (TW - 2 * T, TW - 2 * T, .3), 'floor', 'towers', 0)
    C.box(f'{side} tower stone base', (cx, ya - .06, G0 + .3), (TW + .02, .14, .6), 'stone', 'towers', 0)
    for k in range(5):                                                   # stair flights behind the bay
        z = G0 + .2 + k * 3.4
        C.beam(f'{side} tower stair flight', (outer_x - sgn * 1.4, cy - 1.4, z), (outer_x - sgn * 1.4, cy + 1.4, z + 1.7), 1.1, .2, 'concrete', 'tower stair')
        C.beam(f'{side} tower stair flight', (outer_x - sgn * 2.6, cy + 1.4, z + 1.7), (outer_x - sgn * 2.6, cy - 1.4, z + 3.4), 1.1, .2, 'concrete', 'tower stair')
    C.qa_room_light(f'{side} tower stair', (cx, cy, TOWER_TOP - 2.0), 90, 3.0)


def street_stair(sgn):
    """Solid stair from the south end of a platform down to the plaza, descending outward, with handrails on posts."""
    xa, ya, yb = sgn * PX[1], STAIR_Y[0], STAIR_Y[1]
    n = 20; rise = PLAT / n; run = .45
    pts = [(0.0, PLAT)]
    for k in range(n):
        pts.append(((k + 1) * run, PLAT - k * rise))
        pts.append(((k + 1) * run, PLAT - (k + 1) * rise))
    end = n * run
    pts += [(end - .9, 0.0), (0.4, PLAT - .55), (0.0, PLAT - .55)]
    poly = [(xa + sgn * u, z) for u, z in pts]
    if sgn < 0:
        poly = poly[::-1]
    C.prism('Street stair', poly, 'y', ya, yb, 'concrete', 'street stairs')
    C.box('Stair landing', (xa + sgn * (end + .6), (ya + yb) / 2, .14), (1.4, yb - ya, .28), 'concrete', 'street stairs', 0)
    for y in (ya + .06, yb - .06):
        C.beam('Stair handrail', (xa, y, PLAT + 1.0), (xa + sgn * end, y, 1.0), .05, .05, 'hardware', 'street stairs')
        for k in range(0, n + 1, 4):
            x = xa + sgn * k * run
            z = PLAT - k * rise
            C.beam('Stair rail post', (x, y, z), (x, y, z + 1.0), .05, .05, 'hardware', 'street stairs')


def deck_and_platforms():
    yd0, yd1 = DY0, HY0
    L = yd1 - yd0
    C.box('Guideway deck', (0, (yd0 + yd1) / 2, (4.4 + DECK) / 2), (20.0, L, DECK - 4.4), 'concrete', 'guideway', 0)
    C.box('Track bed', (0, (yd0 + yd1) / 2, DECK + .02), (7.96, L - .02, .04), 'sand', 'guideway', 0)
    b = Batch()
    for sgn in (-1, 1):
        xa, xb = PX
        px = sgn * (xa + xb) / 2
        C.box(f'Platform {sgn:+d}', (px, (yd0 + yd1) / 2, (DECK + PLAT) / 2), (xb - xa, L, PLAT - DECK), 'concrete', 'platforms', 0)
        b.box('tactile', sgn * (xa + .32), (yd0 + 1.0 + yd1) / 2, PLAT + .005, .6, L - 1.1, .03)
        # Glass guard along the outer edge with a gap at the stair head, and across the platform end.
        gx = sgn * (xb - .08)
        for ga, gb in ((yd0 + .1, STAIR_Y[0] - .1), (STAIR_Y[1] + .1, yd1 - .1)):
            b.box('glass', gx, (ga + gb) / 2, PLAT + .6, .02, gb - ga, 1.0)
            b.box('hardware', gx, (ga + gb) / 2, PLAT + 1.12, .06, gb - ga, .06)
            n = max(1, int((gb - ga) / 2.0))
            for k in range(n + 1):
                b.box('hardware', gx, ga + (gb - ga) * k / n, PLAT + .58, .06, .06, 1.12)
        b.box('glass', px, yd0 + .08, PLAT + .6, xb - xa - .1, .02, 1.0)
        b.box('hardware', px, yd0 + .08, PLAT + 1.12, xb - xa, .06, .06)
        for y in (-16.0, -24.0, -30.0):
            b.box('timber', sgn * (xb - 1.4), y, PLAT + .45, .5, 2.0, .08)
            b.box('hardware', sgn * (xb - 1.4), y, PLAT + .22, .4, .1, .44)
        b.box('signal', sgn * 6.4, -38.0, PLAT + 1.7, .9, .5, 3.4)
        b.box('white', sgn * 6.4, -38.26, PLAT + 2.7, .7, .04, 1.0)
        b.box('blue', sgn * 6.4, -38.26, PLAT + 1.8, .7, .04, .5)
    b.flush('platforms')
    street_stair(-1)
    street_stair(1)
    # Rails and sleepers on the two tracks, through the headhouse to the north tail track.
    yr1 = HY1 + TAIL
    b = Batch()
    ye = yd0 - EXT
    for tx in (-2.0, 2.0):
        for rx in (-.72, .72):
            b.box('rail', tx + rx, (ye + yr1) / 2, DECK + .12, .08, yr1 - ye - .02, .16)
        n = int((yr1 - ye) / .9)
        for k in range(n):
            b.box('concrete', tx, ye + .45 + k * .9, DECK + .06, 2.4, .26, .08)
        b.box('signal', tx, yr1 - .6, DECK + .6, 2.0, .5, 1.0)            # buffer stops on the tail track
        b.box('tactile', tx, yr1 - .86, DECK + .7, 1.8, .02, .3)
    b.flush('track')
    # North tail track on piers beyond the headhouse, guarded on both sides and across its end.
    C.box('Tail track deck', (0, (HY1 + yr1) / 2, (4.4 + DECK) / 2), (9.0, TAIL, DECK - 4.4), 'concrete', 'guideway', 0)
    C.box('Tail track bed', (0, (HY1 + yr1) / 2, DECK + .02), (7.96, TAIL - .02, .04), 'sand', 'guideway', 0)
    for x in (-4.4, 4.4):
        C.box('Tail track parapet', (x, (HY1 + yr1) / 2, DECK + .45), (.2, TAIL, .9), 'concrete', 'guideway', 0)
    C.box('Tail track end wall', (0, yr1 - .1, DECK + .45), (8.6, .2, .9), 'concrete', 'guideway', 0)
    for y in (HY1 + 5.0, HY1 + 11.0, yr1 - 1.0):
        C.box('Tail pier cap', (0, y, 3.9), (8.0, 1.2, 1.0), 'concrete', 'piers', 0)
        C.rod('Tail pier', (0, y, 0), (0, y, 3.42), .62, 'concrete', 'piers', 16)
    # South: the level double-track deck continues past the platform ends on round piers, guarded, to a closed end.
    C.box('South deck', (0, (yd0 + ye) / 2, (4.4 + DECK) / 2), (9.0, EXT, DECK - 4.4), 'concrete', 'guideway', 0)
    C.box('South track bed', (0, (yd0 + ye) / 2, DECK + .02), (7.96, EXT - .02, .04), 'sand', 'guideway', 0)
    b = Batch()
    for x in (-4.4, 4.4):
        b.box('concrete', x, (yd0 + ye) / 2, DECK + .2, .2, EXT, .4)
        b.box('glass', x, (yd0 + ye) / 2, DECK + .9, .02, EXT - .1, 1.0)
        b.box('hardware', x, (yd0 + ye) / 2, DECK + 1.43, .07, EXT, .06)
        for k in range(6):
            b.box('hardware', x, yd0 - .05 - (EXT - .1) * k / 5, DECK + .9, .06, .06, 1.06)
    b.box('concrete', 0, ye + .1, DECK + .45, 8.6, .2, .9)
    b.box('signal', -2.0, ye + .6, DECK + .6, 2.0, .5, 1.0)
    b.box('signal', 2.0, ye + .6, DECK + .6, 2.0, .5, 1.0)
    b.flush('south deck')
    for y in (yd0 - 5.0, ye + .8):
        C.box('South pier cap', (0, y, 3.9), (8.0, 1.2, 1.0), 'concrete', 'piers', 0)
        C.rod('South pier', (0, y, 0), (0, y, 3.42), .62, 'concrete', 'piers', 16)
    C.qa_room_light('Underpass fill', (0, (STREET[0] + STREET[1]) / 2, 2.6), 160, 5.0)
    # Piers and cap beams under the station deck; none in the street.
    for y in (-14.5, -19.2, -37.0, -44.0):
        C.box('Pier cap beam', (0, y, 4.4 - .5), (19.0, 1.4, 1.0), 'concrete', 'piers', 0)
        for x in (-6.0, 6.0):
            C.rod('Guideway pier', (x, y, 0), (x, y, 3.42), .62, 'concrete', 'piers', 16)
    C.CONTACTS.append(dict(name='Deck on cap beams and piers outside the street; tracks run through the headhouse to a tail track, and continue level past the platform ends to a closed south end', deck_m=[4.4, DECK, PLAT]))


def canopy(sgn):
    """Long glazed gable canopy over one platform: steel posts on the platform centreline, ridge, eaves, rafters."""
    xc = sgn * 7.0
    xa, xb = xc - 3.7, xc + 3.7
    ze, zr = 9.3, 10.65
    y0, y1 = CAN_Y[1], CAN_Y[0] - .05
    chev = [(xa, ze), (xc, zr), (xb, ze), (xb, ze - .05), (xc, zr - .05), (xa, ze - .05)]
    C.prism('Canopy glazing', chev, 'y', y0, y1, 'glass', 'canopies')
    b = Batch()
    for y in [y0 + (y1 - y0) * k / 12 for k in range(13)]:
        for (ax, az), (bx, bz) in (((xa, ze), (xc, zr)), ((xc, zr), (xb, ze))):
            C.beam('Canopy rafter', (ax, y, az - .07), (bx, y, bz - .07), .10, .10, 'trim', 'canopies')
    for x, z in ((xa, ze), (xb, ze), (xc, zr)):
        b.box('trim', x, (y0 + y1) / 2, z - .08, .22, y1 - y0, .22)
    b.flush('canopy frame')
    for y in [y0 + .4 + (y1 - y0 - .8) * k / 4 for k in range(5)]:
        C.rod('Canopy post', (xc, y, PLAT), (xc, y, zr - .2), .14, 'trim', 'canopies', 10)
    C.qa_room_light(f'Canopy {sgn:+d}', (xc, -22.0, ze - .6), 60, 4.0)


def skywalk(name, x0, x1, y0, y1, truss=True):
    """Glazed Plus 15 bridge: concrete floor, pale roof, glass sides, steel X-truss on the long sides."""
    za, zb = SKY_Z
    along_x = (x1 - x0) >= (y1 - y0)
    C.box(name + ' floor', ((x0 + x1) / 2, (y0 + y1) / 2, za - .2), (x1 - x0, y1 - y0, .4), 'concrete', 'skywalks', 0)
    C.box(name + ' roof', ((x0 + x1) / 2, (y0 + y1) / 2, zb + .2), (x1 - x0 + .2, y1 - y0 + .2, .4), 'pale', 'skywalks', 0)
    b = Batch()
    if along_x:
        L = x1 - x0
        for y in (y0 + .1, y1 - .1):
            b.box('glass', (x0 + x1) / 2, y, (za + zb) / 2, L - .02, .02, zb - za - .02)
            b.box('trim', (x0 + x1) / 2, y - .1 if y < (y0 + y1) / 2 else y + .1, za + .12, L, .16, .24)
            b.box('trim', (x0 + x1) / 2, y - .1 if y < (y0 + y1) / 2 else y + .1, zb - .12, L, .16, .24)
        n = max(2, round(L / 3.4))
        for k in range(n + 1):
            x = x0 + L * k / n
            for y in (y0 - .02, y1 + .02):
                b.box('trim', x, y, (za + zb) / 2, .16, .16, zb - za)
    else:
        L = y1 - y0
        for x in (x0 + .1, x1 - .1):
            b.box('glass', x, (y0 + y1) / 2, (za + zb) / 2, .02, L - .02, zb - za - .02)
            b.box('trim', x - .1 if x < (x0 + x1) / 2 else x + .1, (y0 + y1) / 2, za + .12, .16, L, .24)
            b.box('trim', x - .1 if x < (x0 + x1) / 2 else x + .1, (y0 + y1) / 2, zb - .12, .16, L, .24)
        n = max(2, round(L / 3.4))
        for k in range(n + 1):
            y = y0 + L * k / n
            for x in (x0 - .02, x1 + .02):
                b.box('trim', x, y, (za + zb) / 2, .16, .16, zb - za)
    b.flush(name + ' frame')
    if truss:
        n = max(2, round(L / 3.4))
        for k in range(n):
            if along_x:
                xa, xb = x0 + L * k / n, x0 + L * (k + 1) / n
                for y in (y0 - .04, y1 + .04):
                    off = -.09 if y < (y0 + y1) / 2 else .09
                    C.beam(name + ' truss diagonal', (xa, y, za + .2), (xb, y, zb - .2), .12, .12, 'trim', 'skywalks')
                    C.beam(name + ' truss diagonal', (xa, y + off, zb - .2), (xb, y + off, za + .2), .12, .12, 'trim', 'skywalks')
            else:
                ya, yb = y0 + L * k / n, y0 + L * (k + 1) / n
                for x in (x0 - .04, x1 + .04):
                    off = -.09 if x < (x0 + x1) / 2 else .09
                    C.beam(name + ' truss diagonal', (x, ya, za + .2), (x, yb, zb - .2), .12, .12, 'trim', 'skywalks')
                    C.beam(name + ' truss diagonal', (x + off, ya, zb - .2), (x + off, yb, za + .2), .12, .12, 'trim', 'skywalks')
    C.qa_room_light(name + ' light', ((x0 + x1) / 2, (y0 + y1) / 2, zb - .4), 40, 3.0)


def stair_pavilion(name, x0, x1, y0, y1):
    """Glazed stair pavilion where a skywalk comes down to the street (the towers it would join are not modelled)."""
    zt = SKY_Z[1] + .4
    C.box(name + ' slab', ((x0 + x1) / 2, (y0 + y1) / 2, G0 / 2), (x1 - x0, y1 - y0, G0), 'foundation', 'skywalks', 0)
    b = Batch()
    for x in (x0 + .25, x1 - .25):
        for y in (y0 + .25, y1 - .25):
            b.box('wall', x, y, zt / 2, .5, .5, zt)
    for x in (x0 + .03, x1 - .03):
        b.box('glass', x, (y0 + y1) / 2, zt / 2, .02, y1 - y0 - 1.0, zt - .3)
    for y in (y0 + .03, y1 - .03):
        b.box('glass', (x0 + x1) / 2, y, zt / 2, x1 - x0 - 1.0, .02, zt - .3)
    for z in (SKY_Z[0] - .2, 3.3):
        b.box('trim', (x0 + x1) / 2, (y0 + y1) / 2, z, x1 - x0 - .9, y1 - y0 - .9, .2)
    b.flush(name)
    C.box(name + ' roof', ((x0 + x1) / 2, (y0 + y1) / 2, zt + .2), (x1 - x0 + .4, y1 - y0 + .4, .4), 'pale', 'skywalks', 0)
    C.box(name + ' floor', ((x0 + x1) / 2, (y0 + y1) / 2, SKY_Z[0] - .2), (x1 - x0 - 1.0, y1 - y0 - 1.0, .3), 'concrete', 'skywalks', 0)
    C.beam(name + ' stair', ((x0 + x1) / 2 - 1.0, y0 + 1.0, G0 + .1), ((x0 + x1) / 2 - 1.0, y1 - 1.0, SKY_Z[0] - .3), 1.4, .25, 'concrete', 'skywalks')
    C.qa_room_light(name + ' light', ((x0 + x1) / 2, (y0 + y1) / 2, zt - .6), 60, 3.0)


def train():
    """Two-car red-and-white light-rail vehicle on the west track at the west platform."""
    x = -2.0
    z0 = DECK + .62
    for k, (ya, yb) in enumerate(((-38.6, -26.2), (-25.9, -13.5))):
        C.box('Train body lower', (x, (ya + yb) / 2, z0 + .65), (2.64, yb - ya, 1.3), 'train', 'train', 0)
        C.box('Train window band', (x, (ya + yb) / 2, z0 + 1.95), (2.62, yb - ya - .4, 1.3), 'blue', 'train', 0)
        for y in [ya + .6 + (yb - ya - 1.2) * i / 5 for i in range(6)]:
            C.box('Train window post', (x, y, z0 + 1.95), (2.66, .16, 1.3), 'white', 'train', 0)
        C.box('Train roof', (x, (ya + yb) / 2, z0 + 2.9), (2.64, yb - ya, .6), 'white', 'train', 0)
        C.box('Train roof equipment', (x, (ya + yb) / 2, z0 + 3.4), (1.6, (yb - ya) * .5, .4), 'pale', 'train', 0)
        for y in (ya + 2.0, yb - 2.0):
            C.box('Train bogie', (x, y, DECK + .3), (2.2, 2.6, .5), 'rail', 'train', 0)
        for y in ((ya + yb) / 2 - 2.6, (ya + yb) / 2 + 2.6):
            C.box('Train door', (x + 1.322, y, z0 + 1.2), (.01, 1.3, 2.2), 'white', 'train', 0)
    for y, s in ((-38.6, -1), (-13.5, 1)):
        C.prism('Train cab nose', [(y, z0), (y + s * .6, z0), (y + s * .6, z0 + 3.2), (y, z0 + 2.6)], 'x', x - 1.32, x + 1.32, 'white', 'train')
        C.box('Train cab window', (x, y + s * .35, z0 + 2.15), (2.2, .5, .9), 'glass', 'train', 0)
    C.box('Train gangway', (x, -26.05, z0 + 1.6), (2.2, .32, 2.6), 'rail', 'train', 0)
    C.qa_room_light('Train interior', (x, -26.0, z0 + 2.4), 12, 4.0)


def streets():
    sa, sb = STREET
    C.box('East-west street', (-6.0, (sa + sb) / 2, .01), (80.0, sb - sa, .02), 'asphalt', 'streets', 0)
    for y, name in ((sb + 1.5, 'north'), (sa - 1.5, 'south')):
        for a, c in ((-46.0, -32.0), (-22.0, 34.0)):
            C.box(f'Sidewalk {name}', ((a + c) / 2, y, .07), (c - a, 3.0, .14), 'concrete', 'streets', 0)
    C.box('Plaza under the deck', (0, (sb + 3.0 + HY0) / 2, .07), (36.0, HY0 - sb - 3.0, .14), 'concrete', 'streets', 0)
    ys = DY0 - EXT - 4.0
    C.box('South plaza', (0, (ys + sa - 3.0) / 2, .07), (48.0, sa - 3.0 - ys, .14), 'concrete', 'streets', 0)
    for x, name in ((-27.0, 'West'),):
        C.box(f'{name} street north', (x, (sb + 26.0) / 2, .01), (10.0, 26.0 - sb, .02), 'asphalt', 'streets', 0)
        C.box(f'{name} street south', (x, (sa - 52.0) / 2, .01), (10.0, sa + 52.0, .02), 'asphalt', 'streets', 0)
    b = Batch()
    for k in range(10):                                          # crosswalks at the west street
        b.box('white', -31.0 + k * .9, sa + .9, .025, .5, 1.6, .02)
        b.box('white', -31.0 + k * .9, sb - .9, .025, .5, 1.6, .02)
    for k in range(8):                                           # lane markings on the east-west street
        b.box('white', -42.0 + k * 9.5, (sa + sb) / 2, .025, 3.0, .15, .02)
    b.flush('road markings')
    for x, y in ((-21.0, sb + 1.6), (21.0, sa - 1.6)):            # traffic signals
        C.rod('Signal pole', (x, y, .14), (x, y, 6.0), .12, 'hardware', 'streets', 8)
        C.beam('Signal arm', (x, y, 5.8), (x - 5.0 if x > 0 else x + 5.0, y, 5.8), .1, .1, 'hardware', 'streets')
        C.box('Signal head', (x - 4.6 if x > 0 else x + 4.6, y, 5.3), (.35, .3, 1.0), 'hardware', 'streets', 0)
    for x in (-40.0, 22.0):
        street_tree(x, sb + 1.6, z=.14, height=7.0, spread=1.6)


def build():
    streets()
    headhouse()
    tower(HX0, HX0 + TW, 'west')
    tower(HX1 - TW, HX1, 'east')
    deck_and_platforms()
    canopy(-1)
    canopy(1)
    train()
    wy, ww = SKY_W
    skywalk('West skywalk', -38.0, HX0, wy - ww / 2, wy + ww / 2)
    stair_pavilion('West skywalk pavilion', -44.0, -38.0, wy - 4.0, wy + 4.0)
    ey, ewd = SKY_E
    skywalk('East link', HX1, 27.0, ey - ewd / 2, ey + ewd / 2, truss=False)
    skywalk('East skywalk', 27.0, 31.0, -40.0, 22.0)
    stair_pavilion('East skywalk south pavilion', 26.0, 32.0, -46.0, -40.0)
    stair_pavilion('East skywalk north pavilion', 26.0, 32.0, 22.0, 28.0)
    for y in (-46.0 + 12.0, -12.0, 0.0, 12.0):
        if not (STREET[0] - 3.0 < y < STREET[1] + 3.0):
            C.rod('East skywalk column', (29.0, y, .14), (29.0, y, SKY_Z[0] - .4), .32, 'concrete', 'skywalks', 12)
    C.CONTACTS.append(dict(name='Skywalks bear on the headhouse openings and on glazed stair pavilions and columns', sky_m=list(SKY_Z)))


LIGHT_RIG = dict(key=(-80, -90, 100), fill=(90, -40, 70), rear=(-30, 90, 90), target=(0, -10, 8.0), gain=24.0)
