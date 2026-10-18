"""Regency stucco terrace, authored from the locked catalogue views of
regency_stucco_terrace / variant_0 (regency-stucco-terrace-nash).

Read from the pixels (the top view governs the plan): a palatial Nash-style terrace block round a small light
court, streets on the south, east and west, a row of brick terrace houses against its north side. Cream stucco
throughout: a channelled (rusticated) ground storey; a giant order of fluted engaged Corinthian columns rising
through the first and second floors between the window bays; a full entablature and modillion cornice; a
balustraded parapet with pedestals over the columns. The long south front has three porches of paired Tuscan
columns carrying stone balconies; the east and west ends have a central pediment over the giant order. Tall
first-floor windows with iron balconettes and cornice heads, shorter second-floor windows. Above the
balustrade a steep grey slate mansard with dormers and white party-wall fins carrying chimney stacks, a flat
lead top. Basement areas behind iron railings along the pavements, street trees and lamps.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-regency-stucco-terrace'
X0, X1, Y0, Y1 = -20.0, 20.0, -17.0, 17.0      # 40 m south front, 34 m east and west ends
T = .5
G0 = .6                                         # raised ground floor over the basement area
F1, F2 = 4.4, 8.2
ENT = 11.6                                      # foot of the entablature (top of the capitals)
CORN = 13.0                                     # top of the cornice and of the walls
MSET, MRUN, MTOP = 1.2, 1.7, 16.4               # mansard setback, slope run, flat top
CX0, CX1, CY0, CY1 = -5.0, 5.0, -4.0, 8.0      # light court
BAY = 3.0
EPS = .002
PALETTE = dict(wall=(.86, .82, .72), joint=(.70, .66, .57), stone=(.90, .87, .78), trim=(.95, .94, .90),
    pale=(.88, .88, .86), roof=(.36, .39, .44), lead=(.46, .48, .50), sand=(.70, .66, .58), foundation=(.66, .62, .54),
    glass=(.20, .23, .26), hardware=(.06, .06, .07), interior=(.84, .80, .74), floor=(.58, .48, .38),
    timber=(.46, .34, .22), door=(.10, .11, .12), planting=(.30, .46, .20), soil=(.22, .16, .10),
    concrete=(.70, .69, .66), white=(.95, .95, .93), asphalt=(.27, .27, .28), brick=(.54, .42, .30),
    pot=(.70, .38, .24), paving=(.72, .70, .66), area=(.36, .35, .33), neighbour=(.56, .44, .32),
    nroof=(.34, .36, .40), blue=(.20, .30, .40))


def manifest(version):
    h = MTOP + 2.2
    cams = G.camera_roster(X1 - X0 + 3.0, Y1 - Y0 + 3.0, h, [
        ('facade_close', (0.0, -44.0, 7.5), (0.0, Y0, 7.5), 45),
        ('architecture_close', (30.0, -30.0, 15.0), (X1, Y0, 12.5), 45),
        ('glass_close', (-3.0, -26.0, 7.0), (-3.0, Y0, 7.0), 45),
        ('porch_balcony', (5.5, -26.0, 3.5), (0.0, Y0 - 1.0, 3.5), 40),
        ('giant_order', (12.0, -26.0, 12.0), (8.0, Y0, 11.0), 40),
        ('end_pediment', (40.0, -6.0, 14.0), (X1, 0.0, 13.5), 40),
        ('mansard_dormers', (6.0, -34.0, 22.0), (2.0, Y0 + 2.0, 14.5), 40),
        ('east_side', (55.0, 0.0, 8.0), (X1, 0.0, 8.0), 45),
        ('interior', (-1.0, Y0 + 5.5, F1 + 1.6), (-4.5, Y0, F1 + 2.0), 40),
        ('rear_north', (0.0, 60.0, 26.0), (0.0, 0.0, 12.0), 45)])
    for c in cams:                       # the locked front looks from the south-east; the oblique from the south-west
        if c['name'] == 'front':
            c['location'] = (30.0, -44.0, 1.6); c['target'] = (8.0, -12.0, 9.0); c['lens'] = 24; c['whole'] = False
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='regency_stucco_terrace/variant_0 (regency-stucco-terrace-nash)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=4, storey_programme='rusticated ground floor over a basement, first and second floors in the giant order, a mansard attic',
            plan='40 x 34 m block round a light court (top view), streets south, east and west, terrace houses north',
            facade='cream stucco; channelled ground storey; giant engaged Corinthian order; entablature and balustrade; three paired-column porches with balconies; end pediments; iron balconettes',
            levels_m=[G0, F1, F2, ENT, CORN], roof_m=dict(cornice=CORN, mansard_top=MTOP),
            inferred='interiors, the light court and the north party wall are teaching assumptions'),
        roof_contract=dict(type='steep slate mansard behind the balustrade with dormers and party-wall fins with stacks, a flat lead top round the light court', datum_m=CORN, crowns_m=[MTOP]),
        identity_contract=dict(owner='cream stucco palace-front terrace with a giant Corinthian order, balustraded parapet, porches carrying balconies, end pediments and a slate mansard'),
        material_contract=dict(profile='source-palette clay: cream stucco with channelled joints, pale stone dressings, black iron, grey slate, lead, brick terrace context', textured_keeper=False),
        programme_contract=dict(storeys=4, ground='entrance halls and dining rooms', first='drawing rooms', second='bedrooms', attic='bedrooms in the mansard'),
        contact_contract=['Grade-zero pavements, areas and roads', 'Stucco walls from grade', 'Order and entablature on the walls', 'Mansard on the roof deck behind the balustrade'],
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


# ---- Regency stucco terrace ----

def cyl(b, role, cx, cy, z0, z1, r, n=12):
    """Upright n-gon shaft added to a Batch (one mesh per role)."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V)
    for z in (z0, z1):
        for i in range(n):
            a = 2 * math.pi * (i + .5) / n
            V.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
    F.append(tuple(o + i for i in range(n - 1, -1, -1)))
    F.append(tuple(o + n + i for i in range(n)))
    for i in range(n):
        j = (i + 1) % n
        F.append((o + i, o + j, o + n + j, o + n + i))


def giant_column(b, x, y, nx, ny):
    """Engaged fluted Corinthian column on the wall face (outward normal nx, ny): base, shaft, two-stage capital."""
    cx, cy = x + nx * .25, y + ny * .25
    z0 = F1 + .35
    b.box('stone', cx, cy, z0 + .12, 1.0, 1.0, .24)
    b.box('stone', cx, cy, z0 + .3, .9, .9, .12)
    cyl(b, 'stone', cx, cy, z0 + .36, ENT - .6, .38, 16)
    for k in range(9):                                                                       # flutes on the visible half
        a = math.atan2(ny, nx) + math.radians(-80 + 20 * k)
        b.box('joint', cx + .375 * math.cos(a), cy + .375 * math.sin(a), (z0 + .5 + ENT - .75) / 2, .035, .035, ENT - .75 - z0 - .5)
    b.box('stone', cx, cy, ENT - .52, .8, .8, .16)                                           # bell with two leaf rows
    b.box('stone', cx, cy, ENT - .35, .9, .9, .18)
    for sx in (-1, 1):                                                                       # corner volutes
        for sy in (-1, 1):
            b.box('stone', cx + sx * .46, cy + sy * .46, ENT - .26, .2, .2, .2)
    b.box('stone', cx, cy, ENT - .1, 1.1, 1.1, .2)                                           # abacus


def stucco_face(label, origin, tangent, inward, lo, hi, bays, end=False):
    # Horizontal bands reach the outer corner lines: the long front wraps the corner square, the ends stop at it.
    def band(m, d, t, z, h, extra=0.0):
        p = -(d - t / 2)
        a, c = (lo - T, hi + T) if end else (lo - p - extra, hi + p + extra)
        m.box('stone', (a + c) / 2, d, z, c - a, t, h)
    """One street front: channelled ground storey, podium band, giant order between bays, entablature, balustrade."""
    f = C.Face(origin, tangent, inward, label)
    nx, ny = -inward[0], -inward[1]
    porch_us = [b for b in bays if b in PORCH_BAYS] if not end else [0.0]
    holes = []
    for u in bays:
        if u in porch_us:
            holes.append(hole(f'{label} door {u:+.0f}', u, G0, 1.4, 2.9, kind='door'))
            holes.append(hole(f'{label} fanlight {u:+.0f}', u, G0 + 3.0, 1.4, .55))
        else:
            holes.append(hole(f'{label} ground {u:+.0f}', u, 1.1, 1.3, 2.4))
        holes.append(hole(f'{label} first {u:+.0f}', u, F1 + .75, 1.3, 2.7, kind='french window' if u in porch_us else 'window'))
        holes.append(hole(f'{label} second {u:+.0f}', u, F2 + .7, 1.3, 2.0))
    f.wall(f'{label} carrier', lo, hi - EPS, 0.0, CORN, depth=T, role='wall', holes=holes)
    G.brick_courses(f, lo + .02, hi - .02, .45, F1 - .1, holes, spacing=.45)
    m = Merge(f)
    m.box('foundation', (lo + hi) / 2, -.03, .22, hi - lo, .06, .44)
    band(m, -.12, .24, F1 + .17, .35)                                                        # podium band under the order
    for h in holes:
        kind = h.get('kind', 'window')
        if kind == 'door':
            m.box('door', h['u'], .2, h['z'] + h['h'] / 2, h['w'] - .02, .06, h['h'] - .02)
            for s in (-1, 1):
                for zz in (.6, 1.8):
                    m.box('trim', h['u'] + s * .33, .165, h['z'] + zz, .5, .012, .8)
            register(f, h, .18, 'entry door', 'hall')
            continue
        tall = h['h'] > 2.5
        framed(m, f, h, cols=2 if 'fanlight' not in h['id'] else 4, rows=4 if h['h'] > 1.8 else (1 if 'fanlight' in h['id'] else 3),
               inset=.16, occupied='room', kind=kind)
        if 'fanlight' in h['id']:
            continue
        m.box('stone', h['u'], -.05, h['z'] - .07, h['w'] + .24, .12, .12)
        if h['z'] > F1 and h['z'] < F2:                                                       # first floor: cornice head, iron balconette
            m.box('stone', h['u'], -.1, h['z'] + h['h'] + .28, h['w'] + .5, .2, .12)
            m.box('stone', h['u'], -.05, h['z'] + h['h'] + .13, h['w'] + .3, .1, .2)
            if h['u'] not in porch_us:
                for s in (-1, 1):
                    m.box('hardware', h['u'] + s * (h['w'] / 2 + .05), -.3, h['z'] + .45, .04, .5, .04)
                m.box('hardware', h['u'], -.55, h['z'] + .9, h['w'] + .14, .04, .045)
                m.box('hardware', h['u'], -.55, h['z'] + .12, h['w'] + .14, .03, .03)
                for i in range(9):
                    m.box('hardware', h['u'] - h['w'] / 2 + h['w'] * i / 8, -.55, h['z'] + .5, .02, .02, .78)
                m.box('stone', h['u'], -.3, h['z'] - .04, h['w'] + .2, .55, .08)
        elif h['z'] > F2:
            m.box('stone', h['u'], -.05, h['z'] + h['h'] + .1, h['w'] + .24, .1, .14)
    # Entablature: architrave, frieze, modillion cornice.
    band(m, -.1, .2, ENT + .25, .5)
    band(m, -.06, .12, ENT + .8, .6)
    for i in range(int((hi - lo) / .55)):
        m.box('stone', lo + .3 + i * .55, -.42, CORN - .45, .18, .7, .2)
    band(m, -.38, .76, CORN - .22, .26)
    band(m, -.42, .84, CORN - .05, .1)
    m.flush(label)
    b = Batch()
    cols = [u + BAY / 2 for u in bays[:-1]] + [lo + .7, hi - .7]
    for u in cols:
        p = f.p(u, 0.0, 0.0)
        giant_column(b, p[0], p[1], nx, ny)
    b.flush(f'{label} order')
    return f, cols


def balustrade(b, a, c, z, posts):
    """Balustrade along a-c (world xy) at height z: plinth, balusters, rail, solid pedestals at posts (fractions)."""
    (ax, ay), (cx, cy) = a, c
    L = math.hypot(cx - ax, cy - ay)
    ux, uy = (cx - ax) / L, (cy - ay) / L
    b.beam('stone', (ax, ay, z + .1), (cx, cy, z + .1), .5, .2)
    b.beam('stone', (ax, ay, z + .93), (cx, cy, z + .93), .48, .14)
    n = int(L / .32)
    for i in range(n):
        t = (i + .5) / n * L
        if any(abs(t - p) < .45 for p in posts):
            continue
        b.box('stone', ax + ux * t, ay + uy * t, z + .53, .14, .14, .66)
    for p in posts:
        b.box('stone', ax + ux * p, ay + uy * p, z + .5, .6, .52, .8)


def porch(b, x, y0):
    """Paired Tuscan columns carrying an entablature and a balustraded balcony at the first floor."""
    yf = y0 - 2.1
    b.box('stone', x, (yf + y0) / 2, G0 / 2, 3.8, y0 - yf, G0)
    for k in range(2):
        b.box('stone', x, yf - .15 - .3 * k, (G0 - .2 * (k + 1)) / 2, 2.6, .3, G0 - .2 * (k + 1))
    for sx in (-1.55, -1.0, 1.0, 1.55):
        cyl(b, 'stone', x + sx, yf + .3, G0 + .2, F1 - .55, .2, 12)
        b.box('stone', x + sx, yf + .3, G0 + .1, .5, .5, .2)
        b.box('stone', x + sx, yf + .3, F1 - .48, .5, .5, .14)
    b.box('stone', x, (yf + y0) / 2 - .05, F1 - .2, 3.9, y0 - yf + .3, .42)
    b.box('stone', x, (yf + y0) / 2 - .05, F1 + .05, 4.1, y0 - yf + .4, .1)
    balustrade(b, (x - 1.9, y0 - .05), (x - 1.9, yf + .05), F1 + .1, [.3, 1.9])
    balustrade(b, (x + 1.9, yf + .05), (x + 1.9, y0 - .05), F1 + .1, [.2, 1.8])
    balustrade(b, (x - 1.9, yf + .05), (x + 1.9, yf + .05), F1 + .1, [.2, 3.6])


def dormer(b, p, nx, ny, tx, ty):
    """Dormer standing on the mansard slope; p is the world point of its front face foot on the slope line."""
    w, h, dep = 1.1, 1.55, 1.8
    def at(u, d, z):
        return (p[0] + tx * u - nx * d, p[1] + ty * u - ny * d, z)
    z0 = CORN + .55
    for s in (-1, 1):
        c = at(s * (w / 2 + .08), dep / 2, z0 + h / 2)
        b.box('roof', c[0], c[1], c[2], .16 if tx else dep, dep if tx else .16, h)
    c = at(0, .06, z0 + .07); b.box('trim', c[0], c[1], c[2], (w + .1) if tx else .2, .2 if tx else (w + .1), .14)
    c = at(0, .06, z0 + h - .08); b.box('trim', c[0], c[1], c[2], (w + .3) if tx else .2, .2 if tx else (w + .3), .16)
    c = at(0, .16, z0 + h / 2); b.box('glass', c[0], c[1], c[2], (w - .04) if tx else .01, .01 if tx else (w - .04), h - .2)
    c = at(0, .1, z0 + h / 2); b.box('trim', c[0], c[1], c[2], .06 if tx else .07, .07 if tx else .06, h - .2)
    c = at(0, dep / 2 + .1, z0 + h / 2); b.box('interior', c[0], c[1], c[2], w if tx else dep - .3, dep - .3 if tx else w, h - .2)
    c = at(0, dep / 2, z0 + h + .14); b.box('lead', c[0], c[1], c[2], (w + .36) if tx else dep + .1, dep + .1 if tx else (w + .36), .28)


def facades():
    global PORCH_BAYS
    sb = [X0 + 2.0 + BAY * i for i in range(13)]                                              # 13 bays, 2 m end margins
    PORCH_BAYS = [sb[2], sb[6], sb[10]]
    stucco_face('south', (0, Y0, 0), (1, 0, 0), (0, 1, 0), X0, X1, sb)
    eb = [Y0 + 2.0 + BAY * i for i in range(11)]
    _, ecols = stucco_face('east', (X1, 0, 0), (0, 1, 0), (-1, 0, 0), Y0 + T, Y1 - T, eb, end=True)
    stucco_face('west', (X0, 0, 0), (0, -1, 0), (1, 0, 0), -(Y1 - T), -(Y0 + T), [-u for u in reversed(eb)], end=True)
    n = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north party')
    n.wall('north party wall', -X1, -X0 - EPS, 0.0, CORN, depth=T, role='wall', holes=[])
    b = Batch()
    for x in PORCH_BAYS:
        porch(b, x, Y0)
    for x in (X1, X0):                                                                       # end entrances
        s = 1 if x > 0 else -1
        b.box('stone', x + s * 1.0, 0.0, G0 / 2, 2.0, 3.6, G0)
        for k in range(2):
            b.box('stone', x + s * (2.15 + .3 * k), 0.0, (G0 - .2 * (k + 1)) / 2, .3, 2.6, G0 - .2 * (k + 1))
    b.flush('porches')
    # Balustraded parapet on the three street fronts; the end pediments over the central bays.
    b = Batch()
    sposts = [p - X0 for p in [X0 + 2.0 + BAY * i + BAY / 2 for i in range(12)]] + [.3, X1 - X0 - .3]
    balustrade(b, (X0, Y0 + .1), (X1, Y0 + .1), CORN, sposts)
    ys = [Y0 + 2.0 + BAY * i + BAY / 2 for i in range(10)] + [Y1 - .3]
    for x in (X1 - .1, X0 + .1):                                                             # the ends start behind the front's plinth
        ya = Y0 + .35
        balustrade(b, (x, ya), (x, -5.0), CORN, [y - ya for y in ys if ya + .3 < y < -5.3])
        balustrade(b, (x, 5.0), (x, Y1), CORN, [y - 5.0 for y in ys if 5.3 < y < Y1])
    b.flush('balustrade')
    for x, sgn in ((X1, 1), (X0, -1)):
        xa, xb = (x - .6, x + .02) if sgn > 0 else (x - .02, x + .6)
        C.prism(f'Pediment {sgn:+d}', [(-5.2, CORN), (5.2, CORN), (0.0, CORN + 2.2)], 'x', xa, xb, 'wall', 'pediment')
        b = Batch()
        xm = x + sgn * .1
        for s in (-1, 1):
            b.beam('stone', (xm, s * 5.5, CORN + .02), (xm, 0.0, CORN + 2.4), .9 - .1 * (s > 0), .3, ext=.1)
        xr = x + sgn * .09
        b.box('stone', xr, -2.6, CORN + .55, .14, 1.4, .7)                                      # tympanum relief, touching the face
        b.box('stone', xr, 2.6, CORN + .55, .14, 1.4, .7)
        b.box('stone', xr, 0.0, CORN + .8, .14, 1.2, 1.1)
        b.flush(f'pediment {sgn:+d}')


def roof_and_court():
    # Flat deck behind the parapets, round the court.
    for name, cx, cy, sx, sy in (('south', 0, (Y0 + T + CY0) / 2, X1 - X0 - 2 * T, CY0 - Y0 - T),
                                 ('north', 0, (CY1 + Y1 - T) / 2, X1 - X0 - 2 * T, Y1 - T - CY1),
                                 ('west', (X0 + T + CX0) / 2, (CY0 + CY1) / 2, CX0 - X0 - T, CY1 - CY0),
                                 ('east', (CX1 + X1 - T) / 2, (CY0 + CY1) / 2, X1 - T - CX1, CY1 - CY0)):
        C.box(f'Roof deck {name}', (cx, cy, CORN - .12), (sx, sy, .2), 'lead', 'roof', 0)
    a, c = MSET, MSET + MRUN
    lower = [(X0 + a, Y0 + a), (X1 - a, Y0 + a), (X1 - a, Y1 - a), (X0 + a, Y1 - a)]
    upper = [(X0 + c, Y0 + c), (X1 - c, Y0 + c), (X1 - c, Y1 - c), (X0 + c, Y1 - c)]
    strip('Slate mansard', lower, upper, CORN + .02, MTOP, 'roof', 'roof')
    for name, cx, cy, sx, sy in (('south', 0, (Y0 + c + CY0 - .4) / 2, X1 - X0 - 2 * c, CY0 - .4 - Y0 - c),
                                 ('north', 0, (CY1 + .4 + Y1 - c) / 2, X1 - X0 - 2 * c, Y1 - c - CY1 - .4),
                                 ('west', (X0 + c + CX0 - .4) / 2, (CY0 + CY1) / 2, CX0 - .4 - X0 - c, CY1 - CY0 + .8),
                                 ('east', (CX1 + .4 + X1 - c) / 2, (CY0 + CY1) / 2, X1 - c - CX1 - .4, CY1 - CY0 + .8)):
        C.box(f'Lead flat {name}', (cx, cy, MTOP - .12), (sx, sy, .24), 'lead', 'roof', 0)
    # Light court: plain stucco walls with lite windows, up to the flat top.
    for label, o, t, n, lo, hi in (('court south', (0, CY0, 0), (-1, 0, 0), (0, -1, 0), -CX1 - .4, -CX0 + .4),
                                   ('court north', (0, CY1, 0), (1, 0, 0), (0, 1, 0), CX0 - .4, CX1 + .4),
                                   ('court west', (CX0, 0, 0), (0, 1, 0), (-1, 0, 0), CY0, CY1),
                                   ('court east', (CX1, 0, 0), (0, -1, 0), (1, 0, 0), -CY1, -CY0)):
        f = C.Face(o, t, n, label)
        span = hi - lo
        k = max(1, int(span / 3.2))
        hs = [hole(f'{label} {j} f{i}', lo + span * (j + .5) / k, z, 1.1, 1.8) for j in range(k) for i, z in enumerate((1.2, F1 + .8, F2 + .7, CORN + .6))]
        f.wall(f'{label} wall', lo, hi - EPS, 0.0, MTOP - .24, depth=.4, role='wall', holes=hs)
        m = Merge(f)
        for h in hs:
            framed(m, f, h, cols=2, rows=3, inset=.14, occupied='room', lite=True)
        m.flush(label)
    C.box('Court paving', ((CX0 + CX1) / 2, (CY0 + CY1) / 2, .02), (CX1 - CX0 + .8, CY1 - CY0 + .8, .04), 'concrete', 'court', 0)
    # Dormers and white party-wall fins with stacks on the mansard.
    b = Batch()
    yd = Y0 + a + .55
    for i in range(0, 13, 2):
        x = X0 + 2.0 + BAY * i
        if abs(x) < X1 - c - .8:
            dormer(b, (x, yd), 0, -1, 1, 0)
    for xd, nx in ((X1 - a - .55, 1), (X0 + a + .55, -1)):
        for i in range(11):
            y = Y0 + 2.0 + BAY * i
            if abs(y) < Y1 - c - .8 and abs(y) > 5.6:
                dormer(b, (xd, y), nx, 0, 0, 1)
    b.flush('dormers')
    for x in (X0 + 2.0 + BAY * 1.5, X0 + 2.0 + BAY * 5.5, X0 + 2.0 + BAY * 8.5):
        C.prism(f'Party fin {x:+.0f}', [(Y0 + .6, CORN), (Y0 + .6, CORN + 1.3), (Y0 + c + .3, MTOP + .35), (Y0 + c + 1.4, MTOP + .35), (Y0 + c + 1.4, CORN)],
                'x', x - .22, x + .22, 'white', 'party fins')
        b = Batch()
        b.box('white', x, Y0 + c + .9, MTOP + 1.0, 1.2, .9, 1.3)
        b.box('stone', x, Y0 + c + .9, MTOP + 1.71, 1.32, 1.02, .12)
        for k in range(3):
            b.box('pot', x - .4 + .4 * k, Y0 + c + .9, MTOP + 2.02, .2, .2, .5)
        b.flush(f'stack {x:+.0f}')
    for z in (G0, F1, F2):
        C.box(f'Floor west {z:.1f}', ((X0 + T + CX0 - .4) / 2, (CY0 - .4 + Y1 - T) / 2, z - .12), (CX0 - .4 - X0 - T, Y1 - T - CY0 + .4, .24), 'floor', 'inside', 0)
        C.box(f'Floor east {z:.1f}', ((CX1 + .4 + X1 - T) / 2, (CY0 - .4 + Y1 - T) / 2, z - .12), (X1 - T - CX1 - .4, Y1 - T - CY0 + .4, .24), 'floor', 'inside', 0)
        C.box(f'Floor south {z:.1f}', (0, (Y0 + T + CY0) / 2, z - .12), (X1 - X0 - 2 * T, CY0 - Y0 - T - .4, .24), 'floor', 'inside', 0)
        for x in (-12.0, -3.0, 6.0, 15.0):
            C.qa_room_light(f'Room {x:+.0f} {z:.0f}', (x, Y0 + 3.0, z + 2.2), 60, 3.0)
        for y in (-9.0, 0.0, 9.0):
            for x in (X1 - 3.0, X0 + 3.0):
                C.qa_room_light(f'End room {x:+.0f} {y:+.0f} {z:.0f}', (x, y, z + 2.2), 60, 3.0)
    C.CONTACTS.append(dict(name='Stucco walls from grade; order and entablature on the walls; mansard on the deck behind the balustrade', cornice_m=CORN))


def site():
    C.box('South pavement', (0.0, Y0 - 2.6, .06), (60.0, 5.2, .12), 'paving', 'site', 0)
    C.box('East pavement', (X1 + 2.6, 2.0, .06), (5.2, 38.0, .12), 'paving', 'site', 0)
    C.box('West pavement', (X0 - 2.6, 2.0, .06), (5.2, 38.0, .12), 'paving', 'site', 0)
    C.box('South road', (0.0, Y0 - 10.2, .01), (80.0, 10.0, .02), 'asphalt', 'site', 0)
    C.box('East road', (X1 + 10.2, 3.0, .01), (10.0, 50.4, .02), 'asphalt', 'site', 0)
    C.box('West road', (X0 - 10.2, 3.0, .01), (10.0, 50.4, .02), 'asphalt', 'site', 0)
    b = Batch()
    # Basement areas: dark strips behind iron railings, broken at the porches and end entrances.
    b.box('area', 0.0, Y0 - .95, .125, X1 - X0, 1.9, .01)
    b.box('area', X1 + .95, 0.0, .125, 1.9, Y1 - Y0, .01)
    b.box('area', X0 - .95, 0.0, .125, 1.9, Y1 - Y0, .01)
    def railing(a, c):
        (ax, ay), (cx, cy) = a, c
        L = math.hypot(cx - ax, cy - ay)
        b.beam('hardware', (ax, ay, 1.15), (cx, cy, 1.15), .05, .05)
        b.beam('hardware', (ax, ay, .3), (cx, cy, .3), .04, .04)
        b.beam('stone', (ax, ay, .18), (cx, cy, .18), .28, .12)
        for i in range(int(L / .14) + 1):
            px, py = ax + (cx - ax) * i * .14 / L, ay + (cy - ay) * i * .14 / L
            b.box('hardware', px, py, .7, .022, .022, 1.0)
    xs = [X0 - 1.95] + sum([[p - 2.2, p + 2.2] for p in PORCH_BAYS], []) + [X1 + 1.95]
    for xa, xc in zip(xs[::2], xs[1::2]):
        railing((xa, Y0 - 1.95), (xc, Y0 - 1.95))
    for x in (X1 + 1.95, X0 - 1.95):
        railing((x, Y0 - 1.8), (x, -2.0))
        railing((x, 2.0), (x, Y1))
    for k in range(-40, 40):
        b.box('joint', k * .9, Y0 - 3.9, .121, .02, 2.5, .004)
    for x in (-15.0, 7.0, 24.0):                                                              # lamp standards
        b.box('hardware', x, Y0 - 4.6, 2.4, .14, .14, 4.8)
        b.box('pale', x, Y0 - 4.6, 4.95, .34, .34, .4)
        b.box('hardware', x, Y0 - 4.6, 5.2, .44, .44, .1)
    b.flush('areas and street')
    for x in (-24.0, -7.0, 15.0):
        street_tree(x, Y0 - 4.4, z=.12, height=10.0, spread=3.0)
    # Brick terrace houses against the north party wall, as context.
    for i in range(6):
        x0 = X0 + .1 + i * (X1 - X0 - .2) / 6
        x1 = x0 + (X1 - X0 - .2) / 6
        C.box(f'Terrace house {i}', ((x0 + x1) / 2, Y1 + 6.4, 6.0), (x1 - x0 - .02, 13.0, 12.0), 'neighbour', 'context', 0)
        C.prism(f'Terrace roof {i}', [(Y1 - .1, 12.0), (Y1 + 12.9, 12.0), (Y1 + 6.4, 14.6)], 'x', x0 + .05, x1 - .05, 'nroof', 'context')
        C.box(f'Terrace stack {i}', (x1 - .05, Y1 + 6.4, 14.4), (.8, 2.4, 1.6), 'brick', 'context', 0)


def build():
    facades()
    site()
    roof_and_court()
    C.CONTACTS.append(dict(name='Regency palace-front terrace block on three streets with terrace houses north', box=[X0, X1, Y0, Y1]))


PORCH_BAYS = []
LIGHT_RIG = dict(key=(35, -45, 45), fill=(-45, -25, 30), rear=(-20, 40, 30), target=(0, 0, 9.0), gain=4.0)
