"""High-tech research laboratory with a white steel exoskeleton, authored from the locked catalogue views
of research_laboratory / variant_0 (high_tech_exoskeleton).

Read from the pixels (the top view governs the plan): a block about 1.2 times as wide as it is deep on a
street corner, streets south and east. Three fully glazed laboratory floors in a curtain wall with thin
white slab bands, colour-coded blue, green and yellow ductwork visible behind the glass; they cantilever
west over the street front on an angled soffit. The recessed ground floor is glazed behind two white
V-shaped pilotis on the south front, with concrete walls at its west end and round the service bays. On
the east elevation a white-painted steel exoskeleton of columns, floor beams and alternating diagonals,
infilled with grey vertical louvre panels and white panels, wraps the south-east corner. On the roof a
pale walkway round the edge, a perforated metal screen enclosing the plant, a raised penthouse with
units, duct runs and clusters of three exhaust stacks.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-exoskeleton-research-lab'
X0, X1, Y0, Y1 = -15.0, 15.0, -12.5, 12.5      # 30 x 25 m upper block (top view)
T = .30
G0 = .15
Z1, Z2, Z3, ROOF = 5.6, 9.8, 14.0, 18.2        # ground floor, three lab floors, roof
PARA = ROOF + .35                               # thin parapet: the glass runs nearly to the roof edge
SCREEN = (X0 + 1.4, X1 - 1.4, Y0 + 2.8, Y1 - 1.4)   # tall perforated plant screen behind the edge walkway (wider on the south)
SCREEN_H = 3.8
GX0 = X0 + 7.0                                  # ground floor starts east of the cantilever
GY0 = Y0 + 2.4                                  # recessed south ground-floor glazing
EXO = .7                                        # exoskeleton stand-off on the east face
EPS = .002
PALETTE = dict(wall=(.90, .90, .89), joint=(.80, .80, .79), trim=(.82, .84, .85),
    pale=(.88, .88, .87), stone=(.70, .70, .68), roof=(.70, .70, .68), sand=(.70, .68, .64),
    foundation=(.46, .46, .45), glass=(.52, .62, .66), hardware=(.18, .19, .20),
    interior=(.86, .86, .84), floor=(.60, .60, .58), timber=(.50, .36, .22), blue=(.06, .30, .92),
    green=(.10, .72, .26), yellow=(.98, .80, .04), planting=(.28, .42, .18), soil=(.22, .16, .10),
    concrete=(.66, .66, .64), white=(.94, .94, .93), steel=(.92, .92, .91), louvre=(.40, .42, .44),
    perf=(.80, .81, .82), asphalt=(.30, .30, .31), membrane=(.72, .72, .70), flue=(.74, .75, .76))


def manifest(version):
    h = ROOF + 8.0                                 # stacks stand well above the screen
    cams = G.camera_roster(X1 - X0 + 4.0, Y1 - Y0 + 4.0, h, [
        ('facade_close', (-2.0, -34.0, 12.0), (-2.0, Y0, 12.0), 45),
        ('architecture_close', (32.0, -26.0, 12.0), (X1, -4.0, 11.0), 45),
        ('glass_close', (2.0, -24.0, 11.5), (2.0, Y0, 11.5), 45),
        ('v_pilotis', (2.0, -22.0, 2.4), (2.0, Y0, 3.2), 45),
        ('exoskeleton', (30.0, -10.0, 10.0), (X1, 0.0, 10.0), 45),
        ('roof_screen', (-20.0, -24.0, 30.0), (0.0, 0.0, ROOF + 1.5), 45),
        ('cantilever', (-24.0, -22.0, 3.0), (X0 + 4.0, Y0 + 4.0, 5.0), 45),
        ('stacks', (18.0, 20.0, 28.0), (3.0, 3.0, ROOF + 2.5), 45),
        ('interior', (8.0, 6.0, Z2 + 1.7), (-2.0, Y0, Z2 + 1.6), 50),
        ('rear_north', (0.0, 40.0, 12.0), (0.0, Y1, 11.0), 45)])
    for c in cams:                       # the locked front and oblique look from the south-east, at the exoskeleton
        if c['name'] == 'front':
            c['location'] = (28.0, -44.0, 1.8); c['target'] = (-2.0, -4.0, 9.0); c['lens'] = 28; c['whole'] = False
        elif c['name'] == 'front_corner':
            lx, ly, lz = c['location']; c['location'] = (-lx, ly, lz)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='research_laboratory/variant_0 (high_tech_exoskeleton)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0 + 2 * EXO, depth=Y1 - Y0, height=h),
            observed_storeys=4, storey_programme='recessed glazed ground floor (lobby, service bays), three laboratory floors, roof plant',
            plan='30 x 25 m upper block (top view); the ground floor recessed 2.4 m behind V-pilotis on the south and set back 7 m at the west under a cantilever; plant screen set 3 m in from the roof edge',
            facade='curtain wall with white slab bands on the south, west and north; white steel exoskeleton with alternating diagonals and grey louvre infill on the east, wrapping the south-east corner; V-pilotis at the street; angled cantilever soffit at the west',
            levels_m=[G0, Z1, Z2, Z3, ROOF], parapet_m=PARA,
            inferred='storey heights and interiors are teaching assumptions; the north face is not visible in any source and repeats the curtain-wall grammar'),
        roof_contract=dict(type='flat roof with an edge walkway, a perforated metal plant screen, a penthouse, ducts and exhaust stacks', datum_m=ROOF, crowns_m=[PARA, ROOF + SCREEN_H, ROOF + 7.6]),
        identity_contract=dict(owner='glazed lab floors with coloured services behind glass, cantilever over V-pilotis, white steel exoskeleton with louvre infill, perforated rooftop plant screen with stacks'),
        material_contract=dict(profile='source-palette clay: clear glass, white steel and slab bands, grey louvres, concrete base walls, perforated aluminium screen, blue, green and yellow ducts', textured_keeper=False),
        programme_contract=dict(storeys=4, ground='lobby behind the pilotis, service bays east', labs='open laboratories with benches and coloured service runs', roof='air handling, exhaust stacks'),
        contact_contract=['Grade-zero slab and sidewalks', 'Upper block on the ground-floor core and the V-pilotis', 'Exoskeleton founded at grade and tied to every slab', 'Plant screen, penthouse and stacks on the roof slab'],
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


# ---- high-tech research laboratory ----

class Batch:
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


def curtain(f, lo, hi, levels, tag, lite=False):
    """Curtain wall over the lab floors: a band hole per floor in a white spandrel carrier, glass, mullions every 1.5 m."""
    holes = [hole(f'{tag} glazing f{i}', (lo + hi) / 2, za + .12, hi - lo - .3, zb - za - .24, kind='band') for i, (za, zb) in enumerate(zip(levels, levels[1:]))]   # one pane per storey, hairline floor joints
    f.wall(f'{tag} spandrel carrier', lo, hi - EPS, levels[0], PARA, depth=T, role='white', holes=holes)
    m = Merge(f)
    for h in holes:
        m.box('glass', h['u'], .12, h['z'] + h['h'] / 2, h['w'] - .02, .012, h['h'] - .02)
        register(f, h, .1, 'curtain wall', 'laboratory')
        n = max(1, round(h['w'] / (1.5 if not lite else 3.0)))
        for k in range(1, n):
            m.box('trim', h['u'] - h['w'] / 2 + h['w'] * k / n, .07, h['z'] + h['h'] / 2, .06, .08, h['h'])
    m.flush(tag)
    return holes


def upper_block():
    lv = [Z1, Z2, Z3, ROOF]
    s = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'lab south')
    curtain(s, X0, X1, lv, s.label)
    hd = (Y1 - Y0) / 2
    w = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'lab west')
    curtain(w, -hd + T, hd - T, lv, w.label)
    n = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'lab north')
    curtain(n, -(X1 - X0) / 2, (X1 - X0) / 2, lv, n.label, lite=True)
    # East: white panels and grey vertical louvre infill behind the exoskeleton.
    e = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'lab east')
    bays = 4
    pitch = (Y1 - Y0) / bays
    holes = []
    for i in range(bays):
        u = -hd + pitch * (i + .5)
        for k, (za, zb) in enumerate(zip(lv, lv[1:])):
            if 0 < i < bays - 1:                                         # full-bay louvres stacked in the middle bays
                holes.append(hole(f'east louvre bay {i}-{k}', u, za + .18, pitch - .3, zb - za - .36, kind='louvre'))
    e.wall('lab east panel carrier', -hd + T, hd - T, Z1 - .4, PARA, depth=T, role='white', holes=holes)
    m = Merge(e)
    for h in holes:
        m.box('louvre', h['u'], .12, h['z'] + h['h'] / 2, h['w'] - .02, .04, h['h'] - .02)      # backing
        nl = int(h['h'] / .24)
        for k in range(nl):                                               # horizontal blades filling the bay
            m.box('louvre', h['u'], -.02, h['z'] + .12 + (h['h'] - .24) * k / max(1, nl - 1), h['w'] - .04, .24, .07)   # blades flush with the face
        register(e, h, .1, 'louvre screen', 'plant and stair')
    for z in lv[1:-1]:
        m.box('steel', 0, -.04, z - .15, 2 * hd - 2 * T - .02, .1, .26)
    m.flush('lab east')
    for z in (Z2, Z3, ROOF):
        C.box('Lab floor slab', (0, 0, z - .15), (X1 - X0 - 2 * T, Y1 - Y0 - 2 * T, .3), 'floor', 'lab floors', 0)
    C.box('Lab first floor slab', ((X0 + X1 - T) / 2, 0, Z1 - .2), (X1 - T - X0, Y1 - Y0, .4), 'floor', 'lab floors', 0)   # out to the faces: no gap at the corners
    C.box('Roof membrane', (0, 0, ROOF + .01), (X1 - X0 - 2 * T - .02, Y1 - Y0 - 2 * T - .02, .02), 'membrane', 'roof', 0)
    # Angled cantilever soffit under the west end, and the white slab edge band along the street fronts.
    C.prism('Cantilever soffit', [(X0 + .02, Z1 - .38), (GX0, Z1 - .38), (GX0, Z1 - 2.0)], 'y', Y0 + .05, Y1 - .05, 'white', 'cantilever')   # bedded into the slab
    C.box('Street slab edge', (0, Y0 - .06, Z1 - .2), (X1 - X0, .12, .4), 'white', 'lab floors', 0)
    C.box('West slab edge', (X0 - .06, 0, Z1 - .2), (.12, Y1 - Y0 - .02, .4), 'white', 'lab floors', 0)
    # Colour-coded services behind the glass on every lab floor; benches.
    b = Batch()
    for z in lv[:-1]:
        for x, col in ((-11.0, 'yellow'), (-8.0, 'blue'), (-3.5, 'green'), (1.0, 'blue'), (6.0, 'yellow'), (10.5, 'green')):
            b.box(col, x, Y0 + .65, (z + z + 4.2) / 2, .46, .46, 4.2 - .3)
        for y, zz, col in ((Y0 + .7, z + 3.5, 'blue'), (Y0 + 1.25, z + 3.0, 'green'), (Y0 + 1.8, z + 3.55, 'yellow'), (Y0 + .7, z + 1.4, 'green')):
            b.box(col, 0, y, zz, X1 - X0 - 2.0, .4, .4)
        for y, col in ((-6.0, 'blue'), (-1.0, 'yellow'), (4.0, 'green')):
            b.box(col, X0 + .65, y, (z + z + 4.2) / 2, .46, .46, 4.2 - .3)
        b.box('blue', X0 + .7, 0, z + 3.5, .4, Y1 - Y0 - 2.0, .4)
        for x in (-10.0, -5.0, 0.0, 5.0, 10.0):
            for y in (Y0 + 4.0, Y0 + 8.0):
                b.box('white', x, y, z + .9, 3.2, 1.0, .06)
                b.box('interior', x, y, z + .45, 3.0, .8, .84)
                b.box('pale', x, y + .45, z + 1.6, 3.0, .1, 1.3)
        C.qa_room_light(f'Lab {z:.0f}', (0, Y0 + 5.0, z + 3.6), 160, 9.0)
        C.qa_room_light(f'Lab west {z:.0f}', (X0 + 4.0, 0, z + 3.6), 60, 6.0)
    b.flush('lab services')
    C.CONTACTS.append(dict(name='Upper block on the ground floor and pilotis, cantilevering west over the street front', soffit_m=Z1))


def ground_floor():
    # Recessed glazed south front between concrete walls; concrete walls round the service end.
    s = C.Face(((GX0 + X1) / 2, GY0, 0), (1, 0, 0), (0, 1, 0), 'ground south')
    hs = (X1 - GX0) / 2
    nb = 6
    bw = (2 * hs - 1.0) / nb
    us = [-hs + .5 + bw * (k + .5) for k in range(nb)]
    DB = 2                                                                # door bay, free between the two V-pilotis
    door = hole('lobby door', us[DB], G0, bw - .3, 2.9, kind='door')
    transom = hole('lobby door transom', us[DB], G0 + 3.1, bw - .3, Z1 - .6 - G0 - 3.1)
    glaze = [hole(f'lobby glazing {k}', u, G0, bw - .3, Z1 - .6 - G0) for k, u in enumerate(us) if k != DB]
    s.wall('ground south carrier', -hs, hs - EPS, G0, Z1 - .4, depth=T, role='concrete', holes=[door, transom] + glaze)
    m = Merge(s)
    framed(m, s, door, cols=2, rows=1, inset=.14, occupied='lobby', kind='entry door')
    framed(m, s, transom, cols=2, rows=1, inset=.14, occupied='lobby')
    for e_ in (-1, 1):                                                    # white door portal, proud of the glazing
        x_ = us[DB] + e_ * (bw / 2 - .05)
        m.box('white', x_, -.22, (G0 + G0 + 2.875) / 2, .3, .4, 2.875)             # posts stop under the head and resume above it
        m.box('white', x_, -.22, (G0 + 3.125 + Z1 - .4) / 2, .3, .4, Z1 - .4 - G0 - 3.125)
    m.box('white', us[DB], -.26, G0 + 3.0, bw + .2, .48, .25)                 # head proud of the posts
    for h in glaze:
        framed(m, s, h, cols=2, rows=2, inset=.14, occupied='lobby')
    m.flush('ground south')
    w = C.Face((GX0, (GY0 + Y1) / 2, 0), (0, -1, 0), (1, 0, 0), 'ground west')
    hd = (Y1 - GY0) / 2
    w.wall('ground west carrier', -hd + T, hd - T, G0, Z1 - .4, depth=T, role='concrete', holes=[])
    nn = C.Face(((GX0 + X1) / 2, Y1, 0), (-1, 0, 0), (0, -1, 0), 'ground north')
    hn = (X1 - GX0) / 2
    nd = [hole('ground north door', -hn + 6.0, G0, 1.8, 2.5, kind='door')]
    nn.wall('ground north carrier', -hn, hn - EPS, G0, Z1 - .4, depth=T, role='concrete', holes=nd)
    m = Merge(nn)
    framed(m, nn, nd[0], cols=2, rows=1, inset=.14, occupied='lobby', kind='door', lite=True)
    m.flush('ground north')
    e = C.Face((X1, (GY0 + Y1) / 2, 0), (0, 1, 0), (-1, 0, 0), 'ground east')
    he = (Y1 - GY0) / 2
    doors = [hole(f'service door {k}', u, G0, 3.4, 3.6, kind='service') for k, u in enumerate((-he + 4.0, -he + 9.0))]
    e.wall('ground east carrier', -he + T, he - T, G0, Z1 - .4, depth=T, role='concrete', holes=doors)
    m = Merge(e)
    for h in doors:
        m.box('louvre', h['u'], .14, h['z'] + h['h'] / 2, h['w'] - .02, .04, h['h'] - .02)
        for k in range(1, 12):
            m.box('hardware', h['u'], .11, h['z'] + h['h'] * k / 12, h['w'] - .04, .02, .03)
        register(e, h, .12, 'roller shutter', 'service bay')
    m.flush('ground east')
    C.box('Ground slab', ((GX0 + X1) / 2, (GY0 + Y1) / 2, G0 / 2), (X1 - GX0, Y1 - GY0, G0), 'foundation', 'ground', 0)
    C.box('Ground core', (GX0 + 4.0, 6.0, (G0 + Z1) / 2), (6.0, 6.0, Z1 - G0 - .4), 'concrete', 'ground', 0)
    C.box('Arcade paving', ((X0 + X1) / 2, (Y0 + GY0) / 2, .06), (X1 - X0, GY0 - Y0, .12), 'sand', 'ground', 0)
    C.box('Cantilever paving', ((X0 + GX0) / 2, (GY0 + Y1) / 2, .06), (GX0 - X0, Y1 - GY0, .12), 'sand', 'ground', 0)
    # Two white V-pilotis on the south front carry the slab edge.
    for xc in (-3.8, 7.2):                                                # either side of the door bay
        for e_ in (-1, 1):
            yl = Y0 + .35 + e_ * .03                                      # legs offset so their faces never coincide
            C.beam('V piloti', (xc, yl, G0 + .1), (xc + e_ * 2.6, yl, Z1 - .55), .36, .36, 'steel', 'pilotis')
            C.box('V piloti head plate', (xc + e_ * 2.6, Y0 + .35, Z1 - .51), (.9, .55, .22), 'steel', 'pilotis', 0)   # bears flat on the soffit
        C.box('V piloti shoe', (xc, Y0 + .35, G0 + .2), (.6, .5, .4), 'steel', 'pilotis', 0)
    C.qa_room_light('Lobby', (4.0, GY0 + 4.0, Z1 - 1.0), 120, 7.0)
    for x in (-13.0, -11.5, -10.0):
        A.shrub(x, Y0 - 1.6, .14, .7)


def exoskeleton():
    """White steel exoskeleton on the east face, wrapping the south-east corner: columns, floor beams, alternating diagonals."""
    xe = X1 + EXO
    bays = 4
    ys = [Y0 - EXO] + [Y0 + (Y1 - Y0) * i / bays for i in range(1, bays + 1)]     # the first column turns the south-east corner
    lv = [G0, Z1, Z2, Z3, ROOF]
    b = Batch()
    for i, y in enumerate(ys):
        b.box('steel', xe, y, (G0 + PARA + .2) / 2, .3, .3, PARA + .2 - G0)          # slender columns capped above the top beam
        for z in lv[1:]:
            if i:
                b.box('steel', (X1 + xe) / 2 + .05, y, z, EXO - .1, .14, .14)               # tie back to the slab edge
    for z in lv[1:] + [PARA - .11]:
        b.box('steel', xe, (Y0 - EXO + Y1) / 2, z, .22, Y1 - Y0 + EXO - .42, .22)
    # Corner bay on the south face: a column at the south-east corner line of the curtain wall.
    b.box('steel', X1 - 2.5, Y0 - EXO, (G0 + PARA + .2) / 2, .3, .3, PARA + .2 - G0)
    for z in lv[1:]:
        b.box('steel', (X1 - 2.5 + xe) / 2, Y0 - EXO, z, xe - X1 + 2.5 - .3, .22, .22)
        b.box('steel', X1 - 2.5, Y0 - EXO / 2, z, .2, EXO - .1, .2)
    b.flush('exoskeleton')
    for i in (0, bays - 1):                                               # braced white end bays; no bracing at ground level
        for k in range(1, len(lv) - 1):
            ya, yb = ys[i] + .25, ys[i + 1] - .25
            za, zb = lv[k] + .2, lv[k + 1] - .2
            if (i + k) % 2:
                ya, yb = yb, ya
            C.beam('Exoskeleton diagonal', (xe, ya, za), (xe, yb, zb), .16, .16, 'steel', 'exoskeleton')
    C.CONTACTS.append(dict(name='Exoskeleton columns founded at grade, tied back to every slab edge, wrapping the south-east corner', standoff_m=EXO))


def roof():
    # Perimeter walkway paving, perforated plant screen on posts, penthouse, units, ducts, exhaust stacks.
    x0, x1, y0, y1 = SCREEN
    b = Batch()
    for (a, c, d, e_) in ((x0, x1, y0, y0), (x0, x1, y1, y1), (x0, x0, y0, y1), (x1, x1, y0, y1)):
        L = max(c - a, e_ - d)
        n = int(L / 1.6)
        for k in range(n + 1):
            if c == a and k in (0, n):
                continue                                                   # corner posts belong to the long runs (no duplicate boxes)
            px, py = (a + (c - a) * k / n, d) if c > a else (a, d + (e_ - d) * k / n)
            b.box('steel', px, py, ROOF + (SCREEN_H + .08) / 2, .12, .12, SCREEN_H + .08)   # posts stand proud of the panels
        if c > a:                                                         # long runs pass the corners, short runs butt them
            b.box('perf', (a + c) / 2, d, ROOF + .2 + (SCREEN_H - .2) / 2, c - a + .04, .04, SCREEN_H - .2)
        else:
            b.box('perf', a, (d + e_) / 2, ROOF + .2 + (SCREEN_H - .2) / 2, .04, e_ - d - .04, SCREEN_H - .2)
    b.flush('plant screen')
    # Perforation dots on the two street faces of the screen.
    vs, fs = [], []
    for (a, c, yy, out) in ((x0 + .2, x1 - .2, y0, -1), (x0 + .2, x1 - .2, y1, 1), (x0 + .2, x1 - .2, y0, 1), (x0 + .2, x1 - .2, y1, -1)):   # both faces
        n = int((c - a) / .32)
        for k in range(n):
            for r in range(8):
                u = a + .16 + k * .32; z = ROOF + .5 + r * .34
                o = len(vs)
                vs += [(u - .07, yy + out * .025, z - .07), (u + .07, yy + out * .025, z - .07), (u + .07, yy + out * .025, z + .07), (u - .07, yy + out * .025, z + .07)]
                fs.append((o, o + 1, o + 2, o + 3))
    for (xx, a, c, out) in ((x1, y0 + .2, y1 - .2, 1), (x0, y0 + .2, y1 - .2, -1), (x1, y0 + .2, y1 - .2, -1), (x0, y0 + .2, y1 - .2, 1)):
        n = int((c - a) / .32)
        for k in range(n):
            for r in range(8):
                u = a + .16 + k * .32; z = ROOF + .5 + r * .34
                o = len(vs)
                vs += [(xx + out * .025, u - .07, z - .07), (xx + out * .025, u + .07, z - .07), (xx + out * .025, u + .07, z + .07), (xx + out * .025, u - .07, z + .07)]
                fs.append((o, o + 1, o + 2, o + 3))
    C.mesh('Plant screen perforations', vs, fs, 'hardware', 'plant screen')
    b = Batch()
    b.box('pale', 0.0, 1.0, ROOF + 1.2, 19.0, 12.0, 2.4)                                  # penthouse, about 70 x 54% of the screened area
    for x, y in ((-6.0, -2.0), (-1.5, -2.0), (3.0, -2.0), (-4.0, 4.0), (1.0, 4.0), (6.0, 4.0)):
        b.box('white', x, y, ROOF + 2.6, 1.6, 1.4, .4)
    for (cx, cy, sx, sy) in ((0.0, -7.0, 21.8, 1.0), (0.0, 8.4, 21.8, 1.0), (-10.4, .7, 1.0, 14.4), (10.4, .7, 1.0, 14.4)):
        b.box('pale', cx, cy, ROOF + .7, sx, sy, 1.2)                                         # a continuous duct loop round the penthouse
    b.flush('roof plant')
    for (gx, gy, axis) in ((-6.5, 9.4, 'x'), (11.8, 3.8, 'y'), (2.0, -8.6, 'x'), (-11.8, 0.0, 'y')):   # four clusters of three
        for k in range(3):
            x = gx + (k - 1) * 1.1 if axis == 'x' else gx
            y = gy if axis == 'x' else gy + (k - 1) * 1.1
            C.rod('Exhaust stack', (x, y, ROOF), (x, y, ROOF + 7.5), .38, 'flue', 'stacks', 16)       # well above the screen
            C.rod('Exhaust stack cap', (x, y, ROOF + 7.5), (x, y, ROOF + 7.6), .42, 'hardware', 'stacks', 16)
    # Parapet with a pale coping on the outer edge.
    for (cx, cy, sx, sy) in ((0, Y0 + T / 2 - .01, X1 - X0 + .04, T + .02), (0, Y1 - T / 2 + .01, X1 - X0 + .04, T + .02),
                             (X0 + T / 2 - .01, 0, T + .02, Y1 - Y0 - 2 * T), (X1 - T / 2 + .01, 0, T + .02, Y1 - Y0 - 2 * T)):
        C.box('Parapet coping', (cx, cy, PARA + .04), (sx, sy, .08), 'pale', 'roof', 0)
    C.CONTACTS.append(dict(name='Plant screen, penthouse, ducts and stacks on the roof slab, set back from the edge walkway', screen=list(SCREEN)))


def site():
    C.box('South sidewalk', (0, Y0 - 3.5, .07), (X1 - X0 + 12.0, 7.0, .14), 'sand', 'site', 0)
    C.box('East sidewalk', (X1 + 3.6, 0, .07), (5.0, Y1 - Y0, .14), 'sand', 'site', 0)
    C.box('South street', (2.0, Y0 - 12.0, .01), (X1 - X0 + 30.0, 10.0, .02), 'asphalt', 'site', 0)
    C.box('East street', (X1 + 11.0, 0, .01), (10.0, Y1 - Y0, .02), 'asphalt', 'site', 0)
    b = Batch()
    for k in range(9):
        b.box('white', X0 - 12.0 + k * 6.0, Y0 - 12.0, .025, 3.0, .14, .01)
    b.flush('road markings')
    for x, y in ((-13.0, Y0 - 3.2), (-9.0, Y0 - 3.6), (X0 - 3.0, 4.0)):      # west, under the cantilever, clear of the pilotis
        street_tree(x, y, z=.14, height=7.5, spread=2.0)


def build():
    site()
    ground_floor()
    upper_block()
    exoskeleton()
    roof()
    C.CONTACTS.append(dict(name='Four-storey lab block: glazed lab floors cantilevered over V-pilotis, east exoskeleton, rooftop plant screen', block=[X0, X1, Y0, Y1]))


LIGHT_RIG = dict(key=(-50, -70, 60), fill=(60, -30, 50), rear=(-20, 60, 50), target=(0, 0, 9.0), gain=12.0)
