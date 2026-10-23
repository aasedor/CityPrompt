"""Barcelona passatge (covered passage) street option, authored from the locked catalogue views of
barcelona_passatge / variant_0 ("Morning Light Through Glass").

Read from the pixels (the top view governs the plan): a straight pedestrian passage, about 11 m between its facades
and about 30 m long (2.5 widths in the top view), cut north-south through a city block and roofed by a pointed glass
vault on transverse wrought-iron ribs; each rib drops onto a pilaster corbel through an openwork lattice bracket
(front). The vault springs from the cornices of the two passage facades, about 10.8 m up: cream stone pilasters
divide each facade into bays; the tall shop storey has timber shopfronts with plate glass under dark green
signboards with gilt lettering and a stone entablature at about 6 m; above it each bay is one deep recessed round
arch in red-orange brick (brick soffit and reveals) with a tall French window and fanlight at its back and one
wrought-iron balcony on the entablature; the vault brackets spring from corbels at the arch springing; wall lanterns
hang on the pilasters (front). The north end is a brick end wall about as tall as it is wide, with a round-arched
portal about half its width in a stone archivolt between stone piers, a continuous stone impost band in line with
the shop entablature, a stone medallion in each brick field, a small stone-framed side doorway and a glazed lunette
above; the portal opens onto a street with a pale stuccoed apartment house and bare trees (front). The south mouth
opens onto a small square paved in a diamond lattice between two two-storey pavilions (a cream stone shop storey, a
brick upper storey with one window and a small balcony, cornice, brick attic with urn finials and quoins), under an
ornamental iron end arch with a deep band, an inner round arch and a ringed spandrel; the vault ribs carry crests
along the outside (oblique). The passage floor is pale hydraulic tile in a grey diamond lattice with a border; two back-to-back
benches stand on the axis, a cafe has tables near the portal, and canvas awnings hang over two shops (front). The
west block has a flat terracotta roof deck behind a balustrade along the vault, with white rooftop rooms and a
pergola; the east range is a narrow brick strip on the east street (oblique, top). Cream stuccoed five- and
six-storey blocks with balconies line the streets either side (oblique, top). The pedestrians, cyclist, dog,
goods in the windows and the sunbeams are not modelled.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-barcelona-passatge'
T = .4                                          # facade carrier depth
HW = 5.5                                        # half the passage width between the facade faces (11 m)
L = 30.0                                        # passage length, south mouth (y = 0) to the end wall face
ENDT = 1.2                                      # north end wall thickness
YN = L + ENDT                                   # north face of the passage block
XW, XP, XE = -18.5, -12.0, 9.0                  # west face of the west block, west edge of the brick pavilion, east face of the east range
FZ = .12                                        # tile floor top in the passage and the square
SHOP = 4.4                                      # shopfront clear height above the floor (the shop zone runs to the entablature at 6 m)
F1 = 6.0                                        # upper floor level: top of the shop entablature, base of the arched bays
EAVE = 10.8                                     # top of the passage cornices; the glass vault springs here (end wall about 10.7 m in the front)
VX, VH = 5.3, 5.0                               # vault half-span at the eave gutters and vault rise
CORBEL = 8.35                                   # top of the pilaster corbels that carry the rib legs, at the arch springing
RIBS = [6.0, 10.8, 15.6, 20.4, 25.2]            # transverse ribs over the pilasters (y)
BAYS = [(.4, 6.0)] + [(6.0 + 4.8 * i, 10.8 + 4.8 * i) for i in range(5)]
ROOM, UPR = 3.0, 1.6                            # ground-floor shop depth, upper-room depth behind the facades
SW, RW = 2.0, 5.0                               # sidewalk and roadway widths of the surrounding streets
XWS, XES, YNS = XW - 2 * SW - RW, XE + 2 * SW + RW, YN + 2 * SW + RW   # opposite building lines
YSQ, YSS = -10.0, -17.0                         # south edge of the square, opposite building line on the south street
XMIN, XMAX, YMIN, YMAX = XWS - 12.0, XES + 12.0, YSS - 12.0, YNS + 12.0
EPS = .002
PALETTE = dict(brick=(.55, .26, .15), brick2=(.68, .44, .31), stone=(.80, .71, .55), stucco=(.86, .79, .65),
    stucco2=(.80, .72, .58), mortar=(.76, .64, .52), iron=(.17, .21, .19), frame=(.15, .20, .17), hardware=(.06, .06, .07),
    glass=(.62, .68, .68), trim=(.88, .86, .80), shopframe=(.36, .20, .10), timber=(.52, .33, .18), sign=(.07, .17, .13),
    gold=(.80, .62, .28), awning=(.88, .82, .68), lamp=(.95, .90, .72), tile=(.80, .76, .68), tile2=(.44, .44, .43), joint=(.70, .66, .58),
    terracotta=(.73, .46, .33), white=(.90, .89, .86), interior=(.86, .73, .54), floor=(.55, .42, .30),
    goods=(.62, .30, .20), asphalt=(.25, .25, .26), concrete=(.72, .70, .66), curb=(.66, .65, .62), planting=(.30, .43, .20),
    pot=(.60, .40, .28), car=(.66, .67, .69), car2=(.24, .27, .30), car3=(.78, .76, .70), tyre=(.07, .07, .07),
    dark=(.16, .17, .18), marking=(.92, .92, .90))


def manifest(version):
    h = 20.5
    cams = G.camera_roster(60.0, 60.0, h, [
        ('facade_close', (4.6, 13.2, 5.6), (-HW, 13.2, 5.8), 18),                  # one west bay through all floors
        ('architecture_close', (-2.2, 17.2, 6.6), (HW, 15.6, 10.0), 28),            # rib leg, corbel, lattice bracket and cornice
        ('glass_close', (0.0, 11.0, 2.0), (0.0, 18.0, 14.4), 22),                   # the vault glazing and ribs from below
        ('interior', (-.6, 27.6, 1.65), (.5, 0.0, 4.6), 20),                        # eye level near the portal, looking back to the mouth
        ('roof_vault', (-15.0, 5.0, 23.5), (0.0, 15.0, 13.0), 30),
        ('south_portal', (1.5, -9.0, 1.7), (0.0, 1.0, 7.0), 20),                   # the square: mouth, end arch and pavilions
        ('north_portal', (1.0, YN + 7.2, 1.7), (0.0, YN, 6.0), 22),                # the end wall and portal from the north street
        ('shopfronts', (-3.0, 19.0, 1.8), (HW, 22.8, 2.6), 24),
        ('floor_tiles', (2.5, 7.0, 3.6), (0.0, 16.0, .2), 24),
        ('pavilion_finial', (-2.5, -8.5, 15.0), (-6.0, .3, 12.7), 30)])
    for c in cams:
        if c['name'] == 'front':                                               # the locked front: eye level inside the passage, looking north to the portal
            c.update(location=(.6, 10.5, 1.65), target=(-.2, L, 4.7), lens=20, whole=False)
        elif c['name'] == 'front_corner':                                      # the locked oblique: high over the square, looking north-north-east along the vault
            c.update(location=(-17.0, -27.0, 52.0), target=(3.0, 15.0, 2.0), lens=30, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(40.0, -30.0, 45.0), target=(0.0, 15.0, 5.0), lens=26, whole=False)
        elif c['name'] == 'top':                                               # the locked top view: north up, the vault right of centre
            c.update(location=(-.7, 13.8, 120.0), target=(-.7, 13.801, 0.0), ortho_scale=60.0, whole=False)
        elif c['name'] == 'left_side':                                         # high over the west context: west face, roof deck and vault
            c.update(location=(-26.0, 15.0, 52.0), target=(-8.0, 15.0, 3.0), lens=28, whole=False)
        elif c['name'] == 'right_side':                                        # high over the east context: east range and vault
            c.update(location=(19.0, 15.0, 50.0), target=(1.0, 15.0, 3.0), lens=28, whole=False)
        elif c['name'] == 'rear':                                              # high over the north context: end wall, portal and north faces
            c.update(location=(0.0, 40.0, 50.0), target=(0.0, 17.0, 3.0), lens=28, whole=False)
        elif c['name'] == 'rear_side':
            c.update(location=(-24.0, 40.0, 54.0), target=(-3.0, 16.0, 3.0), lens=28, whole=False)
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='barcelona_passatge/variant_0 (Morning Light Through Glass), modelled as a glass-vaulted passage through an Eixample-era block',
        measurement_contract=dict(dimensions_m=dict(width=XMAX - XMIN, depth=YMAX - YMIN, height=h),
            observed_storeys=2, storey_programme='street option: a covered pedestrian passage; the brick facades (a tall shop storey and one tier of deep arched bays with balconies) are the walls it is read with',
            plan=f'{2 * HW:.0f} m between the passage facades and {L:.0f} m from the open south mouth to the end wall (top view); a {ENDT} m brick end wall with a round-arched portal to the north street; a tiled square in front of the mouth',
            section_m=dict(passage_width=2 * HW, floor=FZ, shop_head=FZ + SHOP, shop_entablature=F1, arch_springing=CORBEL, eave=EAVE, vault_crown=EAVE + .12 + VH),
            facade='red-orange brick with cream stone pilasters and a stone shop entablature; timber shopfronts with green gilt-lettered signboards; above, one deep recessed round brick arch per bay with a tall French window and fanlight at its back and one wrought-iron balcony at its base; wall lanterns',
            vault='pointed glass vault on five transverse wrought-iron ribs with lattice brackets on pilaster corbels, dense glazing bars, three purlins a side, crests on the ribs, a glazed north lunette and an ornamental south end arch',
            levels_m=[0.0, FZ, FZ + SHOP, F1, CORBEL, EAVE, EAVE + .12 + VH],
            inferred='shop interiors, upper rooms, the outer faces of the passage block and the surrounding blocks are context and teaching assumptions; metric dimensions are authored from the pixel ratios'),
        roof_contract=dict(type='pointed glass vault on iron ribs between the passage cornices; flat terracotta roof decks with parapets, a balustrade along the vault and rooftop rooms', datum_m=EAVE, crowns_m=[EAVE + .12 + VH]),
        identity_contract=dict(owner='Barcelona covered passage: a pointed glass vault on ornate wrought-iron ribs over a diamond-tiled pedestrian passage between brick shop facades with arched balconied windows, closed by an arched brick portal and opening onto a tiled square between brick pavilions'),
        material_contract=dict(profile='source-palette clay: red-orange brick, cream stone, dark green-black iron, pale glass, timber shopfronts, green and gilt signs, pale tile with grey lattice bands, terracotta roof decks, cream stucco', textured_keeper=False),
        programme_contract=dict(storeys=2, ground='shops and a cafe opening onto the passage', upper='flats with balconies over the passage'),
        street_contract=dict(kind='fixed_native_section', width_m=2 * HW, axis='north-south pedestrian passage through the block', junction_finish='open south mouth onto a tiled square; arched portal onto the north street',
                             bands=['shop_facade', 'tiled_passage_floor', 'shop_facade', 'glass_vault_overhead', 'square_at_the_mouth', 'surrounding_streets']),
        contact_contract=['Asphalt at grade zero', 'Tile floor and square at 120 mm, sidewalks at 150 mm', 'Facades and pavilions from grade', 'Vault on the cornice gutters, ribs on the pilaster corbels', 'Benches, tables and lamp posts on the tiles'],
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


# ---- Barcelona passatge (covered passage) ----

FD = .6                                                                     # passage facade depth: the arched bays are recessed this deep
RZ, RCROWN = F1, 9.95                                                       # bay arch base (on the shop entablature) and crown
FW = C.Face((-HW, 0, 0), (0, 1, 0), (-1, 0, 0), 'west passage facade')      # u = y, inward -x (into the west block)
FE = C.Face((HW, 0, 0), (0, 1, 0), (1, 0, 0), 'east passage facade')        # u = y, inward +x (into the east range)
FSW = C.Face((XP, 0, 0), (1, 0, 0), (0, 1, 0), 'west pavilion south face')  # x = XP + u, inward +y
FSE = C.Face((HW, 0, 0), (1, 0, 0), (0, 1, 0), 'east pavilion south face')  # x = HW + u
FN = C.Face((-HW - T, L, 0), (1, 0, 0), (0, 1, 0), 'north end wall')       # x = -5.9 + u, inward +y (passage face at y = L)
FNS = C.Face((HW + T, YN, 0), (-1, 0, 0), (0, -1, 0), 'north end wall street face')   # x = 5.9 - u, inward -y
PU = HW + T                                                                 # portal centre on the end wall faces (u)


def frustum(b, role, cx, cy, z0, z1, r0, r1, n=8, phase=.5):
    """Upright n-gon frustum added to a Batch (r1 = 0 gives a point)."""
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
    """One flat four-corner face (a floor band): two triangles instead of a twelve-triangle box."""
    V, F = b.g.setdefault(role, ([], []))
    o = len(V); V.extend(pts); F.append((o, o + 1, o + 2, o + 3))


def smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


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


def carrier(f, name, u0, u1, z0, z1, holes, role, depth=T):
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
            vs.extend(f.p(uu, dd, zz) for zz in (za, zb) for uu, dd in ((a, 0.0), (c, 0.0), (c, depth), (a, depth)))
            fs.extend(tuple(o + i for i in face) for face in C.BOX_FACES)
    obj = C.mesh(name, vs, fs, role, 'envelope')
    obj['rlasm_wall_carrier'] = True
    return obj


def courses(f, lo, hi, z0, z1, holes, spacing=.3, d=-.002, role='mortar'):
    """Mortar courses on brick, one quad per solid run, batched per elevation."""
    vs, fs = [], []
    z = z0 + spacing
    while z < z1:
        for a, c in band_runs(lo, hi, z - .005, z + .01, holes):
            o = len(vs); vs.extend([f.p(a, d, z), f.p(c, d, z), f.p(c, d, z + .012), f.p(a, d, z + .012)])
            fs.append((o, o + 1, o + 2, o + 3))
        z += spacing
    if fs:
        C.mesh(f.label + ' mortar courses', vs, fs, role, 'brick joints')


def arc_pts(uc, zs, r, a0, a1, n):
    return [(uc + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), zs + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def spandrels(f, name, uc, zs, r, depth, role, n=12):
    """Wall infill between a round arch and the square top of its clear cut, through the full carrier depth."""
    f.panel(name + ' left spandrel', arc_pts(uc, zs, r, 180, 90, n) + [(uc - r, zs + r)], 0.0, depth, role, 'envelope')
    f.panel(name + ' right spandrel', [(uc + r, zs + r)] + arc_pts(uc, zs, r, 90, 0, n), 0.0, depth, role, 'envelope')


def archivolt(f, name, uc, zs, r, width=.24, d0=-.05, d1=.01, role='stone', n=14):
    """Stone arch surround: a half ring proud of the face, 1 cm clear of the cut so no reveal face is shared."""
    ring = arc_pts(uc, zs, r + .01 + width, 180, 0, n) + arc_pts(uc, zs, r + .01, 0, 180, n)
    f.panel(name + ' archivolt', ring, d0, d1, role, 'openings')


def fanlight(b, f, name, uc, zs, r, inset=.16, frame='frame', n=14):
    """Arched head of a French window: a half-ring frame, three fan bars and a half-disc pane, all inside the cut."""
    ring = arc_pts(uc, zs, r - .005, 180, 0, n) + arc_pts(uc, zs, r - .075, 0, 180, n)
    f.panel(name + ' arch frame', ring, inset - .05, inset + .05, frame, 'openings')
    f.panel(name + ' fanlight', arc_pts(uc, zs, r - .07, 180, 0, n), inset + .032, inset + .041, 'glass', 'openings')
    for a in (45, 90, 135):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        b.beam(frame, f.p(uc, inset - .005, zs + .02), f.p(uc + (r - .07) * ca, inset - .005, zs + (r - .07) * sa), .035, .045)


def flat_balcony(m, b, f, u, z, w, depth, spacing=.09, slab=.12):
    """Cantilevered balcony: a thin stone slab with a moulded edge, iron top, mid and bottom rails and end frames as
    boxes, pickets and a band of crossed scroll bars as flat bars (one quad each) to keep the dense ironwork of the
    sources inside the size budget."""
    m.box('stone', u, -depth / 2 + .02, z - slab / 2, w, depth + .04, slab)
    m.box('stone', u, -depth - .01, z - slab - .03, w - .1, .08, .07)          # moulded edge under the slab
    m.box('iron', u, -depth + .04, z + .98, w, .05, .05)
    m.box('iron', u, -depth + .04, z + .12, w, .03, .03)
    m.box('iron', u, -depth + .04, z + .55, w, .025, .025)
    for e in (-1, 1):
        m.box('iron', u + e * (w / 2 - .02), -depth / 2 + .02, z + .98, .05, depth - .04, .05)
        m.box('iron', u + e * (w / 2 - .02), -depth + .04, z + .5, .04, .04, .96)
        m.box('iron', u + e * (w / 2 - .02), -depth / 2 + .02, z + .5, .03, .03, .96)
    n = max(4, int(w / spacing))
    for i in range(1, n):
        uu = u - w / 2 + w * i / n
        quad(b, 'iron', [f.p(uu - .012, -depth + .04, z), f.p(uu + .012, -depth + .04, z), f.p(uu + .012, -depth + .04, z + .55), f.p(uu - .012, -depth + .04, z + .55)])
    k = max(2, int(w / .32))
    for i in range(k):                                                        # crossed scroll bars in the upper band
        a, c = u - w / 2 + w * i / k, u - w / 2 + w * (i + 1) / k
        for (ua, za), (ub, zb) in (((a, z + .56), (c, z + .96)), ((a, z + .96), (c, z + .56))):
            quad(b, 'iron', [f.p(ua - .012, -depth + .045, za), f.p(ua + .012, -depth + .045, za), f.p(ub + .012, -depth + .045, zb), f.p(ub - .012, -depth + .045, zb)])


def arch_window(m, b, f, name, uc, z, w, rect, wall, balcony=0.0, frame='frame', depth=T):
    """Round-arched French window: clear cut to the crown, spandrels, framed lower lights with a transom at the
    springing, a fanlight, a stone archivolt and keystone, and a wrought-iron balcony (or a stone sill)."""
    r = w / 2; zs = z + rect
    framed(m, f, hole(name, uc, z, w, rect), cols=2, rows=1, inset=.16, occupied='flat', frame=frame)
    spandrels(f, name, uc, zs, r, depth, wall)
    fanlight(b, f, name, uc, zs, r, frame=frame)
    archivolt(f, name, uc, zs, r)
    m.box('stone', uc, -.05, zs + r + .23, .34, .12, .44)                   # keystone, its foot on the crown
    if balcony:
        flat_balcony(m, b, f, uc, z - .01, w + .9, balcony)
    else:
        m.box('stone', uc, -.07, z - .065, w + .3, .14, .12)                # sill, 5 mm below the cut


def french_window(m, b, f, name, uc, z, w, rect, balcony, plain=False):
    """Tall round-arched French window: two glazed leaves (three panes over a panel) to the springing, a fanlight
    with fan bars in the round head, frames 0.28 m back in brick reveals, a stone archivolt, imposts and keystone, and
    a shallow wrought-iron balcony at the sill."""
    r = w / 2; zs = z + rect
    framed(m, f, hole(name, uc, z, w, rect), cols=2, rows=3, inset=.28, occupied='flat', frame='frame')
    m.box('frame', uc, .245, z + .3, w - .16, .04, .46)                     # bottom panels of the leaves
    spandrels(f, name, uc, zs, r, T, 'brick')
    fanlight(b, f, name, uc, zs, r, inset=.28)
    if not plain:
        archivolt(f, name, uc, zs, r, width=.25)
        m.box('stone', uc, -.05, zs + r + .15, .32, .12, .3)                # keystone, its foot on the crown
        for s in (-1, 1):                                                    # imposts at the springing
            m.box('stone', uc + s * (r + .13), -.04, zs - .07, .38, .1, .14)
    if balcony:
        flat_balcony(m, b, f, uc, z - .01, w + .9, balcony)


def bay_arch(m, b, f, name, uc, rw):
    """Upper bay as one deep recessed round arch in brick: a brick arch ring, brick soffit and reveals through the
    0.6 m facade depth, a tall French window with a fanlight in the brick infill at the back of the recess, a stone
    recess floor, and one wrought-iron balcony standing on the shop entablature."""
    r = rw / 2; zs = RCROWN - r
    spandrels(f, name, uc, zs, r, FD, 'brick')
    archivolt(f, name, uc, zs, r, width=.32, role='brick2')
    m.box('stone', uc, .32, RZ + .06, rw, .56, .12)                         # recess floor at the balcony level
    fr = C.Face(f.p(0, FD, 0), tuple(f.t), tuple(f.n), f.label + ' recess')
    ww, wz = 2.4, RZ + .13
    wrect = zs + .05 - wz
    carrier(fr, name + ' infill', uc - r, uc + r, RZ, RCROWN, [hole(name + ' french', uc, wz, ww, wrect + ww / 2)], 'brick', depth=T)
    mr = Merge(fr)
    french_window(mr, b, fr, name + ' french', uc, wz, ww, wrect, 0.0, plain=True)
    mr.flush(name + ' recess')
    flat_balcony(m, b, f, uc, RZ + .12, rw + .1, .55)


def entablature(m, a, c):
    """Stone shop entablature over the signboards, its top at the upper floor level: frieze, bed moulding and a
    corona projecting 0.18 m that the balconies stand on."""
    m.box('stone', (a + c) / 2, -.03, (FZ + SHOP + .73 + F1 - .22) / 2, c - a - EPS, .06, F1 - .22 - (FZ + SHOP + .73))
    m.box('stone', (a + c) / 2, -.05, F1 - .17, c - a - EPS, .1, .1)
    m.box('stone', (a + c) / 2, -.09, F1 - .06, c - a - EPS, .18, .12)


def shopfront(m, f, name, uc, w, sign=True):
    """Timber shopfront inside a clear cut: three lights over a panelled bulkhead, a transom, a door stile, and a dark
    green signboard with a gilt name band above the cut."""
    framed(m, f, hole(name, uc, FZ, w, SHOP), cols=3, rows=1, inset=.22, occupied='shop', frame='shopframe')
    m.box('shopframe', uc, .21, FZ + SHOP * .76, w - .14, .08, .07)          # transom bar
    m.box('timber', uc, .15, FZ + .36, w - .16, .08, .58)                    # panelled timber bulkhead in front of the glass
    m.box('shopframe', uc, .105, FZ + .68, w - .14, .03, .06)                 # bulkhead capping rail
    for s in (-1, 0, 1):                                                     # raised panels on the bulkhead
        m.box('shopframe', uc + s * (w - .3) / 3, .102, FZ + .36, (w - .5) / 3, .02, .36)
    m.box('hardware', uc + w / 6 - .12, .15, FZ + 1.1, .04, .04, .3)        # door pull on the middle light
    if sign:
        m.box('sign', uc, -.06, FZ + SHOP + .45, w + .2, .08, .56)
        m.box('gold', uc, -.104, FZ + SHOP + .45, w * .62, .012, .15)       # the sign top meets the entablature frieze


def wall_lantern(b, f, u, z):
    """Wall lantern on a pilaster: an iron arm and a glazed lantern box with a cap."""
    b.beam('iron', f.p(u, -.10, z + .25), f.p(u, -.55, z + .25), .04, .04)
    b.beam('iron', f.p(u, -.10, z - .05), f.p(u, -.40, z + .22), .03, .03)
    x, y, _ = f.p(u, -.55, 0)
    b.box('lamp', x, y, z, .22, .22, .36)
    b.box('iron', x, y, z + .21, .28, .28, .06)
    b.box('iron', x, y, z - .2, .16, .16, .05)


def awning(f, u0, u1):
    """Canvas awning over a shopfront: a sloped plate from the fascia, iron arms."""
    pts = [(.03, FZ + SHOP + .2), (-1.3, FZ + SHOP - .35), (-1.3, FZ + SHOP - .5), (.03, FZ + SHOP + .1)]
    C.mesh('Awning', [f.p(u, d, z) for u in (u0, u1) for d, z in pts],
           [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 'awning', 'shopfronts')


def passage_facade(f, side):
    """One passage facade: brick carrier with shopfronts, arched balconied windows on two floors, stone pilasters,
    belts, corbels and a modillion cornice; lit shops and rooms behind."""
    holes, specs = [], []
    for i, (u0, u1) in enumerate(BAYS):
        uc = (u0 + u1) / 2 + (.25 if i == 0 else 0.0)
        ws = 3.0 if i == 0 else 3.4
        holes.append(hole(f'{f.label} shop {i}', uc, FZ, ws, SHOP))
        holes.append(hole(f'{f.label} arch {i}', uc, RZ, 3.0 if i == 0 else 3.2, RCROWN - RZ))
        specs.append((i, u0, u1, uc, ws))
    carrier(f, f.label + ' carrier', .4, L, 0.0, EAVE - .05, holes, 'brick', depth=FD)
    m = Merge(f); b = Batch()
    for i, u0, u1, uc, ws in specs:
        shopfront(m, f, f'{f.label} shop {i}', uc, ws)
        bay_arch(m, b, f, f'{f.label} bay {i}', uc, 3.0 if i == 0 else 3.2)
    for u in RIBS + [L - .3]:                                               # stone pilasters, ground to cornice
        m.box('stone', u, -.06, (EAVE - .62) / 2, .8 if u < L - 1 else .6, .12, EAVE - .62)
        if u < L - 1:
            for zc, w, d, h in ((CORBEL - .06, .7, .56, .12), (CORBEL - .3, .52, .48, .36), (CORBEL - .58, .42, .36, .2), (CORBEL - .76, .3, .24, .16)):
                m.box('stone', u, -d / 2, zc, w, d, h)                       # moulded corbel: abacus, block, scroll, drop
            wall_lantern(b, f, u, FZ + SHOP - 1.0)
    for k in range(int((EAVE - .7 - RZ) / .6)):                             # quoins returning from the pavilion corner (brick storey)
        w = .9 if k % 2 == 0 else .6
        m.box('stone', w / 2 - .03, -.03, RZ + .3 + .6 * k + .27, w, .1, .53)
    entablature(m, 0.0, L)
    m.box('stone', (.4 + L) / 2, -.04, .3, L - .4 - EPS, .08, .6)           # stone plinth band
    eave_cornice(m, 0.0, L, EAVE, proj=.7, role='stone')                     # mitred with the pavilion cornice by mouth_corners()
    m.flush(f.label)
    b.flush(f.label + ' iron')
    # rooms: shops 3 m deep with partitions, upper rooms 1.6 m deep, floors and ceilings (the core behind is lined)
    rb = Batch()
    def blk(role, ua, ub, da, db, za, zb):
        (x0, y0, _), (x1, y1, _) = f.p(ua, da, 0), f.p(ub, db, 0)
        rb.box(role, (x0 + x1) / 2, (y0 + y1) / 2, (za + zb) / 2, abs(x1 - x0), abs(y1 - y0), zb - za)
    blk('floor', .4, L, T - .02, ROOM, FZ - .1, FZ)
    blk('interior', .4, L, FD - .02, ROOM + .02, 4.8, 5.0)
    blk('floor', .4, L, FD - .02, UPR, F1 - .2, F1)
    blk('interior', .4, L, T - .02, UPR, EAVE - .5, EAVE - .3)
    blk('interior', .4, L, UPR, UPR + .02, 5.0, EAVE - .3)                  # upper-room liner
    blk('interior', .4, L, ROOM, ROOM + .02, FZ, 5.0)                       # shop back wall
    for u in RIBS:
        blk('interior', u - .08, u + .08, FD - .02, ROOM, FZ, 4.8)          # shop partitions
        blk('interior', u - .08, u + .08, T - .02, UPR, F1, EAVE - .5)
    for i, u0, u1, uc, ws in specs:                                          # goods shelves on the shop back walls
        blk('timber', uc - 1.3, uc + 1.3, ROOM - .45, ROOM, FZ + .9, FZ + .96)
        blk('timber', uc - 1.3, uc + 1.3, ROOM - .45, ROOM, FZ + 1.8, FZ + 1.86)
        blk('goods', uc - 1.1, uc + 1.1, ROOM - .4, ROOM - .05, FZ + .96, FZ + 1.4)
        blk('timber', uc - .6, uc + .6, 1.3, 1.9, FZ, FZ + .9)              # counter
    rb.flush(f.label + ' rooms')
    for i, u0, u1, uc, ws in specs:
        C.qa_room_light(f'{f.label} shop {i}', f.p(uc, 1.6, 3.6), 45, 1.2)
        C.qa_room_light(f'{f.label} flat {i}', f.p(uc, 1.3, F1 + 2.2), 10, .5)


def pavilion_face(f, name, u1, holes_u, pw, wall='brick', corner='east'):
    """South face of a two-storey pavilion at the mouth: a cream stone shop storey with a shopfront, signboard and
    entablature, one brick upper storey with a tall window under a corniced head on consoles and a small balcony,
    quoins on the brick storey, cornice and a brick attic parapet."""
    uc = holes_u
    hs, hw = hole(name + ' shop', uc, FZ, pw, SHOP), hole(name + ' upper', uc, F1 + .4, 1.4, 2.9)
    carrier(f, name + ' stone storey', 0.0, u1, 0.0, F1, [hs], 'stone')
    carrier(f, name + ' brick storey', 0.0, u1, F1, EAVE - .05, [hw], wall)
    m = Merge(f); b = Batch()
    shopfront(m, f, name + ' shop', uc, pw)
    framed(m, f, hw, cols=2, rows=3, inset=.28, occupied='flat', frame='frame')
    zt = hw['z'] + hw['h']
    m.box('stone', uc, -.05, zt + .14, hw['w'] + .4, .1, .28)              # head frieze
    m.box('stone', uc, -.1, zt + .33, hw['w'] + .66, .2, .1)               # head cornice
    for s in (-1, 1):
        m.box('stone', uc + s * (hw['w'] / 2 + .12), -.07, zt + .1, .14, .14, .36)     # consoles
    flat_balcony(m, b, f, uc, hw['z'] - .01, 1.9, .4)
    big, small = (.9, .6) if u1 > 5 else (.6, .4)
    for u in (.0, u1):                                                       # quoins on the brick storey
        for k in range(int((EAVE - .7 - F1) / .6)):
            w = big if k % 2 == 0 else small
            uu = u + (w / 2 - .03 if u == 0.0 else -(w / 2 - .03))
            m.box('stone', uu, -.03, F1 + .3 + .6 * k + .27, w, .1, .54)
    entablature(m, 0.0 if corner == 'west' else -.03, u1 if corner == 'east' else u1 + .03)
    for k in range(int((F1 - .9) / .45)):                                   # rusticated joints on the stone storey, around the shop
        z = .6 + .45 * k
        for a, c in band_runs(.01, u1 - .01, z - .02, z + .02, [dict(hs, w=hs['w'] + .1, h=hs['h'] + .9)]):
            m.box('stone', (a + c) / 2, -.012, z, c - a, .025, .03)
    eave_cornice(m, 0.0 if corner == 'west' else -.03, u1 if corner == 'east' else u1 + .03, EAVE, proj=.7, role='stone')
    m.box(wall, u1 / 2, T / 2, EAVE + .4, u1, T, .9)                         # parapet
    m.box('stone', u1 / 2, T / 2, EAVE + .9, u1 + .1, T + .1, .1)
    m.flush(name); b.flush(name + ' iron')


def mouth_corners(b):
    """Square corner blocks completing each cornice layer where a pavilion cornice meets a passage cornice at the
    mouth: the two cornices butt at the corner and these fill the outer quadrant, so the profiles turn without
    overlap or step."""
    for s in (-1, 1):
        for zc, h, out in ((EAVE - .62, .26, .4), (EAVE - .13, .26, .88), (EAVE, .06, .83),
                           ((FZ + SHOP + .73 + F1 - .22) / 2, F1 - .22 - (FZ + SHOP + .73), .06), (F1 - .17, .1, .1), (F1 - .06, .12, .18)):
            b.box('stone', s * (HW - out / 2), -out / 2, zc, out, out, h)


def finial(b, x, y, z):
    """Corner finial on the pavilion parapet: a stone pedestal, a moulded base and an urn with a flame."""
    b.box('stone', x, y, z + .55, .8, .8, 1.1)
    b.box('stone', x, y, z + 1.15, .95, .95, .12)
    for z0, z1, r0, r1 in ((1.21, 1.3, .2, .14), (1.3, 1.45, .14, .26), (1.45, 1.65, .26, .36), (1.65, 1.85, .36, .3),
                           (1.85, 1.97, .3, .16), (1.97, 2.03, .16, .24), (2.03, 2.12, .24, .14), (2.12, 2.24, .1, .07)):
        frustum(b, 'stone', x, y, z + z0, z + z1, r0, r1, 12)                # foot, bellied body, neck, lid and knob
    frustum(b, 'stone', x, y, z + 2.24, z + 2.32, .1, .02, 12)


def aa(b, role, c, t, n, along, out, z0, z1, off=0.0):
    """Axis-aligned box on a face: `along` the tangent, `out` along the outward normal, centred `off` out from c."""
    (tx, ty), (nx, ny) = t, n
    b.box(role, c[0] + nx * off, c[1] + ny * off, (z0 + z1) / 2, abs(tx) * along + abs(nx) * out, abs(ty) * along + abs(ny) * out, z1 - z0)


def proud_window_lite(b, c, t, n, z, w, hh, balcony=False):
    """Context window: surround and glass as single proud faces; on upper floors a stone slab and two iron rails."""
    (tx, ty), (nx, ny) = t, n
    P = lambda a, o, zz: (c[0] + tx * a + nx * o, c[1] + ty * a + ny * o, zz)
    quad(b, 'trim', [P(-w / 2 - .14, .015, z - .08), P(w / 2 + .14, .015, z - .08), P(w / 2 + .14, .015, z + hh + .08), P(-w / 2 - .14, .015, z + hh + .08)])
    quad(b, 'glass', [P(-w / 2, .03, z), P(w / 2, .03, z), P(w / 2, .03, z + hh), P(-w / 2, .03, z + hh)])
    if balcony:                                                              # slab top and edge, two rails: single faces at sill level
        a0, a1 = -w / 2 - .25, w / 2 + .25
        quad(b, 'stone', [P(a0, .02, z - .02), P(a1, .02, z - .02), P(a1, .58, z - .02), P(a0, .58, z - .02)])
        quad(b, 'stone', [P(a0, .58, z - .14), P(a1, .58, z - .14), P(a1, .58, z - .02), P(a0, .58, z - .02)])
        quad(b, 'iron', [P(a0, .56, z + .86), P(a1, .56, z + .86), P(a1, .56, z + .92), P(a0, .56, z + .92)])
        quad(b, 'iron', [P(a0, .56, z + .1), P(a1, .56, z + .1), P(a1, .56, z + .14), P(a0, .56, z + .14)])


def proud_window(b, c, t, n, z, w, hh, balcony=False):
    """Window on a face no source shows in detail: a pale surround 3 cm proud, glass 3 cm proud of it, and on the
    upper floors a stone balcony slab with an iron rail."""
    aa(b, 'trim', c, t, n, w + .28, .06, z - .08, z + hh + .08, .0)
    aa(b, 'glass', c, t, n, w, .02, z, z + hh, .045)
    if balcony:
        aa(b, 'stone', c, t, n, w + .5, .6, z - .14, z - .01, .28)
        (tx, ty), (nx, ny) = t, n
        for s in (-1, 1):
            b.beam('iron', (c[0] + nx * .55 + tx * s * (w / 2 + .2), c[1] + ny * .55 + ty * s * (w / 2 + .2), z - .01), (c[0] + nx * .55 + tx * s * (w / 2 + .2), c[1] + ny * .55 + ty * s * (w / 2 + .2), z + .9), .03, .03)
        b.beam('iron', (c[0] + nx * .55 - tx * (w / 2 + .22), c[1] + ny * .55 - ty * (w / 2 + .22), z + .9), (c[0] + nx * .55 + tx * (w / 2 + .22), c[1] + ny * .55 + ty * (w / 2 + .22), z + .9), .045, .04)
        b.beam('iron', (c[0] + nx * .55 - tx * (w / 2 + .2), c[1] + ny * .55 - ty * (w / 2 + .2), z + .12), (c[0] + nx * .55 + tx * (w / 2 + .2), c[1] + ny * .55 + ty * (w / 2 + .2), z + .12), .03, .03)


def passage_block():
    """The two passage facades, the pavilions at the mouth, the block's outer walls, rooms, roof decks, balustrade,
    parapets and rooftop rooms."""
    passage_facade(FW, 'w')
    passage_facade(FE, 'e')
    pavilion_face(FSW, 'west pavilion', -HW - XP, (-HW - XP) / 2, 3.0)
    pavilion_face(FSE, 'east pavilion', XE - HW, (XE - HW) / 2, 2.0, corner='west')
    cb = Batch(); mouth_corners(cb); cb.flush('mouth cornice corners')
    b = Batch()
    # west block outer walls (stucco), the core behind the rooms (lined in the interior tone), floors of the south rooms
    b.box('stucco', XW + T / 2, (0.0 + YN - T) / 2, (EAVE + .9) / 2, T, YN - T, EAVE + .9)
    b.box('stucco', (XW + T + XP) / 2, T / 2, (EAVE + .9) / 2, XP - XW - T, T, EAVE + .9)
    b.box('stucco', (XW - HW - T) / 2, YN - T / 2, (EAVE + .9) / 2, -HW - T - XW, T, EAVE + .9)
    b.box('interior', (XW + T - HW - ROOM - .02) / 2, (1.62 + YN - T) / 2, (EAVE - .3) / 2, -HW - ROOM - .02 - XW - T, YN - T - 1.62, EAVE - .3)
    b.box('interior', -HW - (ROOM + UPR) / 2 - .01, (1.62 + YN - T) / 2, (5.0 + EAVE - .3) / 2, ROOM - UPR + .02, YN - T - 1.62, EAVE - .3 - 5.0)
    for z in (F1,):
        b.box('floor', (XP - HW - UPR) / 2, (T - .02 + 1.62) / 2, z - .1, -HW - UPR - XP, 1.64 - T, .2)
        b.box('floor', (XE + HW + UPR) / 2 - .2, (T - .02 + 1.62) / 2, z - .1, XE - HW - UPR - .4, 1.64 - T, .2)
    # east range outer walls (brick) and core
    b.box('brick', XE - T / 2, (T + YN - T) / 2, (EAVE + .6) / 2, T, YN - 2 * T, EAVE + .6)
    b.box('brick', (HW + T + XE) / 2, YN - T / 2, (EAVE + .6) / 2, XE - HW - T, T, EAVE + .6)
    b.box('interior', (HW + UPR + XE - T) / 2, (1.62 + YN - T) / 2, (5.0 + EAVE - .3) / 2, XE - T - HW - UPR, YN - T - 1.62, EAVE - .3 - 5.0)
    # roof decks, parapet copings, balustrade along the vault on the west block, brick parapet on the east range
    b.box('terracotta', (XW + T - HW - T + .02) / 2, (T + YN - T) / 2, EAVE - .21, -HW - T + .02 - XW - T, YN - 2 * T, .18)
    b.box('terracotta', (HW + T - .02 + XE - T) / 2, (T + YN - T) / 2, EAVE - .21, XE - T - HW - T + .02, YN - 2 * T, .18)
    for x0, y0, x1, y1, z in ((XW - .05, -.05, XW + T + .05, YN + .05, EAVE + .9), (XW + T + .05, -.05, XP, T + .05, EAVE + .9),
                              (XW + T + .05, YN - T - .05, -HW - T, YN + .05, EAVE + .9), (XE - T - .05, T, XE + .05, YN + .05, EAVE + .6),
                              (HW + T, YN - T - .05, XE - T - .05, YN + .05, EAVE + .6)):
        b.box('stone', (x0 + x1) / 2, (y0 + y1) / 2, z + .05, x1 - x0, y1 - y0, .1)
    b.box('stone', -HW - .32, (T + YN - T) / 2, EAVE + .03, .7, YN - 2 * T, .36)          # balustrade plinth
    b.box('stone', -HW - .32, (T + YN - T) / 2, EAVE + .92, .5, YN - 2 * T, .1)           # rail
    y = T + .2
    while y < YN - T - .1:
        frustum(b, 'stone', -HW - .32, y, EAVE + .21, EAVE + .55, .07, .11, 4)
        frustum(b, 'stone', -HW - .32, y, EAVE + .55, EAVE + .87, .11, .06, 4)
        y += .4
    for y in (T + .1, 10.8, 20.4, YN - T - .1):
        b.box('stone', -HW - .32, y, EAVE + .5, .42, .3, .84)                             # balustrade dies
    b.box('brick', HW + .32, (T + YN - T) / 2, EAVE + .25, .5, YN - 2 * T, .8)
    b.box('stone', HW + .32, (T + YN - T) / 2, EAVE + .7, .6, YN - 2 * T, .1)
    # rooftop rooms and a pergola on the west deck
    for x0, x1, y0, y1, hh in ((-15.0, -11.0, 18.0, 24.0, 2.6), (-16.6, -13.4, 5.0, 8.4, 2.4), (-11.0, -9.0, 26.0, 29.0, 2.2)):
        b.box('white', (x0 + x1) / 2, (y0 + y1) / 2, EAVE - .12 + hh / 2, x1 - x0, y1 - y0, hh)
        b.box('stone', (x0 + x1) / 2, (y0 + y1) / 2, EAVE - .12 + hh + .05, x1 - x0 + .1, y1 - y0 + .1, .1)
    for x in (-16.4, -13.6):
        for yy in (11.0, 15.0):
            b.box('white', x, yy, EAVE - .12 + 1.2, .12, .12, 2.4)
    for yy in (11.0, 13.0, 15.0):
        b.box('timber', -15.0, yy, EAVE - .12 + 2.45, 3.4, .1, .12)
    for x in (-16.4, -13.6):
        b.box('timber', x, 13.0, EAVE - .12 + 2.35, .1, 4.4, .1)
    # corner finials on the pavilions at the mouth
    finial(b, -HW - .45, .4, EAVE + .95)
    finial(b, HW + .45, .4, EAVE + .95)
    finial(b, XP + .45, .4, EAVE + .95)
    finial(b, XE - .45, .4, EAVE + .95)
    b.flush('passage block')
    # windows on the outer faces (proud surrounds, glass, balcony slabs and rails; the flats behind are not modelled)
    w = Batch()
    for x0, y0, tx, ty, nx, ny, u0, u1, step in ((XW, 0.0, 0, 1, -1, 0, 2.0, YN - 2.0, 3.2), (XW, 0.0, 1, 0, 0, -1, 2.0, XP - XW - 1.6, 3.0),
                                                 (XW, YN, 1, 0, 0, 1, 2.0, -HW - T - XW - 1.5, 3.2), (XE, 0.0, 0, 1, 1, 0, 2.6, YN - 2.0, 3.6),
                                                 (HW + T, YN, 1, 0, 0, 1, 1.55, 1.55, 3.0)):
        u = u0
        while u <= u1 + 1e-6:
            for k, (z, hh) in enumerate(((1.0, 2.4), (F1 + .4, 2.6))):
                proud_window(w, (x0 + tx * u, y0 + ty * u), (tx, ty), (nx, ny), z, 1.1, hh, balcony=k > 0)
            u += step
    w.flush('outer windows')
    for k, (x, z) in enumerate(((-9.0, 3.0), (7.3, 3.0), (-9.0, F1 + 2.0), (7.3, F1 + 2.0))):
        C.qa_room_light(f'pavilion rooms {k}', (x, 1.0, z), 30 if z < 4 else 8, .6)


def north_end_wall():
    """Brick end wall measured from the locked front: a round-arched portal about half the wall width (5.8 m clear,
    springing at the 6 m impost, crown about 8.9 m) in a stone archivolt with a keystone, full-height stone piers on
    bases, a continuous stone impost band in line with the shop entablature, a stone medallion centred in each brick
    field, a small stone-framed side doorway on the west, a cornice and the glazed lunette above."""
    pw = 5.8
    r = pw / 2; zs = F1
    dw, du = 1.0, PU - 4.65                                                 # side doorway: width and centre (u)
    holes = [hole('portal', PU, 0.0, pw, zs + r), hole('side door', du, 0.0, dw, 3.0)]
    carrier(FN, 'north end wall', 0.0, 2 * PU, 0.0, EAVE + .15, holes, 'brick', depth=ENDT)
    courses(FN, .45, 2 * PU - .45, .6, EAVE - .7, [dict(h, w=h['w'] + 2.3, h=h['h'] + .5) for h in holes])
    spandrels(FN, 'portal', PU, zs, r, ENDT, 'brick', n=18)
    m = Merge(FN); b = Batch()
    archivolt(FN, 'portal passage', PU, zs, r, width=.45, n=18)
    m.box('stone', PU, -.06, zs + r + .32, .55, .14, .64)
    for s in (-1, 1):                                                       # stone piers on bases, medallions
        m.box('stone', PU + s * (r + .5), -.04, (zs - .18) / 2, 1.0, .08, zs - .18)
        m.box('stone', PU + s * (r + .5), -.08, .3, 1.16, .16, .6)
        mx, my, mz = FN.p(PU + s * 4.7, -.04, 8.0)
        annulus('medallion ring', (mx, my, mz), (0, 1, 0), .4, .56, -.06, .04, 'stone', 'end wall', 24)
        annulus('medallion disc', (mx, my, mz), (0, 1, 0), .001, .4, -.02, .03, 'stone', 'end wall', 24)
        annulus('medallion boss', (mx, my, mz), (0, 1, 0), .001, .16, -.12, -.01, 'stone', 'end wall', 16)
    for a, c in ((.37, PU - r), (PU + r, 2 * PU - .37)):                    # continuous impost band, in line with the shop entablature
        m.box('stone', (a + c) / 2, -.06, zs, c - a, .12, .36)
    for s in (-1, 1):                                                       # side doorway surround
        m.box('stone', du + s * (dw / 2 + .1), -.04, 1.6, .2, .08, 3.2)
    m.box('stone', du, -.05, 3.25, dw + .5, .1, .3)
    m.box('stone', PU + r + 1.0 + (2 * PU - .4 - PU - r - 1.0) / 2, -.04, .3, 2 * PU - .4 - PU - r - 1.0, .08, .6)   # plinth, east field
    eave_cornice(m, .37, 2 * PU - .37, EAVE + .012, proj=.7, role='stone')
    m.flush('north end wall passage face')
    courses(FNS, .05, 2 * PU - .05, .6, EAVE - .4, [dict(h, u=2 * PU - h['u'], w=h['w'] + 1.0, h=h['h'] + .5) for h in holes])
    ms = Merge(FNS)
    archivolt(FNS, 'portal street', PU, zs, r, width=.45, n=18)
    ms.box('stone', PU, -.06, zs + r + .32, .55, .14, .64)
    for s in (-1, 1):
        ms.box('stone', PU + s * (r + .25), -.05, zs - .1, .6, .12, .22)
    ms.box('stone', PU, -.06, EAVE - .1, 2 * PU - 2 * EPS, .14, .25)
    ms.flush('north end wall street face')
    # lunette: the vault section above the end wall glazed, with radial bars
    prof = vault_profile()
    poly = [(x, z) for x, z in prof if z > EAVE + .14]
    pts = [(-VX + .02, EAVE + .1)] + poly + [(VX - .02, EAVE + .1)]
    vs = [(x, y, z) for y in (L - .03, L - .005) for x, z in pts]
    n = len(pts)
    fs = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(i, (i + 1) % n, (i + 1) % n + n, i + n) for i in range(n)]
    C.mesh('North lunette glass', vs, fs, 'glass', 'vault')
    for k in range(2, len(poly) - 1, 3):
        x, z = poly[k]
        b.beam('iron', (0.0, L - .06, EAVE + .2), (x, L - .06, z - .04), .05, .05)
    b.beam('iron', (-VX + .3, L - .06, EAVE + .2), (VX - .3, L - .06, EAVE + .2), .08, .08)
    b.flush('north lunette bars')


def vault_z(ax):
    t = max(0.0, 1.0 - ax / VX)
    return EAVE + .12 + VH * t ** .7


def vault_profile(n=14):
    """Pointed vault section from the west gutter to the east gutter (x, z)."""
    left = [(-VX * (1 - k / n), vault_z(VX * (1 - k / n))) for k in range(n + 1)]
    return left + [(-x, z) for x, z in reversed(left[:-1])]


def normal(prof, k):
    a = prof[max(k - 1, 0)]; c = prof[min(k + 1, len(prof) - 1)]
    tx, tz = c[0] - a[0], c[1] - a[1]
    l = math.hypot(tx, tz) or 1.0
    return tz / l, -tx / l                                                  # into the vault (down and inward)


def vault():
    """Pointed glass vault: a glass shell between the gutters, glazing bars every 0.6 m, purlins, five transverse
    ribs with legs to the pilaster corbels and lattice brackets, crests on the ribs, a ridge cap and the ornamental
    south end arch."""
    prof = vault_profile()
    n = len(prof)
    top = [(x, z) for x, z in prof]
    bot = [(x, z - .025) for x, z in reversed(prof)]
    ring = top + bot
    loft('Glass vault', [[(x, y, z) for x, z in ring] for y in (0.0, L - .03)], 'glass', 'vault', closed=False)
    b = Batch()
    for s in (-1, 1):                                                        # eave gutters on the cornices
        b.box('iron', s * (HW - .15), (L - .04) / 2, EAVE + .175, .5, L + .04, .29)  # eaves gutter box, 4 cm proud of the pavilion faces
    y = .3
    while y < L - .2:                                                        # glazing bars on the glass (flat ribbons)
        for k in range(n - 1):
            (x0, z0), (x1, z1) = prof[k], prof[k + 1]
            quad(b, 'iron', [(x0, y - .025, z0 + .012), (x1, y - .025, z1 + .012), (x1, y + .025, z1 + .012), (x0, y + .025, z0 + .012)])
        y += .75
    for k in (3, 7, 11, n - 4, n - 8, n - 12):                               # purlins along the vault
        x, z = prof[k]
        b.beam('iron', (x, 0.0, z + .045), (x, L - .03, z + .045), .05, .05)
    xr, zr = prof[n // 2]
    b.beam('iron', (0.0, -.15, zr + .09), (0.0, L - .03, zr + .09), .3, .18)   # ridge cap roll
    ridge_crest(b, zr + .18)
    for yr in RIBS:
        rib(b, prof, yr, .12, .22)
        girder(b, prof, yr)
        crest(b, prof, yr)
        frustum(b, 'iron', 0.0, yr, zr + .1, zr + .95, .08, 0.0, 6)         # ridge finial
        for s in (-1, 1):
            leg(b, s, yr)
    for yr in [3.2] + [r + 2.4 for r in RIBS]:                               # lighter intermediate ribs on the gutters
        rib(b, prof, yr, .08, .14, off=.1)
    end_arch(b, prof)
    b.flush('glass vault iron')
    for y in (8.0, 16.0, 24.0):                                              # daylight under the vault (inspection only)
        C.qa_room_light(f'passage daylight {y:.0f}', (0.0, y, EAVE - 1.0), 260, 6.0)


def rib(b, prof, y, w, d, off=.13):
    """Transverse rib under the glass following the vault section."""
    for k in range(len(prof) - 1):
        (x0, z0), (x1, z1) = prof[k], prof[k + 1]
        nx0, nz0 = normal(prof, k); nx1, nz1 = normal(prof, k + 1)
        b.beam('iron', (x0 + nx0 * off, y, z0 + nz0 * off), (x1 + nx1 * off, y, z1 + nz1 * off), w, d, ext=.01)


def bar(b, y, a, c, w=.045, t=.04):
    """Iron bar in the rib plane y between two (x, z) points: a thin box, w wide in the plane and t thick along y, so
    it reads at grazing angles too."""
    (xa, za), (xc, zc) = a, c
    b.beam('iron', (xa, y, za), (xc, y, zc), t, w)


def clip_poly(p, d, poly):
    """Clip the line p + t d to a convex polygon; returns the segment ends or None."""
    t0, t1 = -1e9, 1e9
    cx = sum(q[0] for q in poly) / len(poly); cz = sum(q[1] for q in poly) / len(poly)
    for i in range(len(poly)):
        (ax, az), (bx, bz) = poly[i], poly[(i + 1) % len(poly)]
        nx, nz = -(bz - az), bx - ax
        if (cx - ax) * nx + (cz - az) * nz < 0:
            nx, nz = -nx, -nz
        num = (p[0] - ax) * nx + (p[1] - az) * nz
        den = d[0] * nx + d[1] * nz
        if abs(den) < 1e-9:
            if num < 0:
                return None
            continue
        tt = -num / den
        if den > 0:
            t0 = max(t0, tt)
        else:
            t1 = min(t1, tt)
    if t1 - t0 < .1:
        return None
    return (p[0] + d[0] * t0, p[1] + d[1] * t0), (p[0] + d[0] * t1, p[1] + d[1] * t1)


def leg(b, s, y):
    """Rib leg down the pilaster to its corbel (it stops under the cornice and resumes above it), with an openwork
    lattice bracket filling the panel between the leg, the strut and the rib: a diagonal lattice, an edge bar under the
    rib, three hangers and two scroll rings."""
    xl = s * (HW - .30)
    b.beam('iron', (xl, y, CORBEL - .05), (xl, y, EAVE - .74), .14, .16)
    b.beam('iron', (xl, y, EAVE + .02), (xl, y, EAVE + .2), .14, .16)
    ax = HW - 2.6                                                            # where the bracket strut meets the rib
    za = vault_z(ax) - .22
    zl = CORBEL + .25
    b.beam('iron', (xl, y, zl), (s * ax, y, za), .1, .12)
    xw, xi = abs(xl) - .07, HW - .95                                         # leg face, inner edge of the cornice zone
    poly = [(xw, zl + .12), (xw, EAVE - .8), (xi, vault_z(xi) - .25), (ax + .08, za - .02)]   # convex panel
    for (p0, p1) in ((poly[1], poly[2]), (poly[2], poly[3])):                                   # edge bars of the panel
        bar(b, y, (s * p0[0], p0[1]), (s * p1[0], p1[1]), .06, .05)
    for sign in (1, -1):                                                     # diagonal lattice at 0.3 m
        c = -12.0
        while c < 12.0:
            seg = clip_poly((0.0, c), (1.0, sign * 1.0), poly)
            if seg:
                (x0, z0), (x1, z1) = seg
                bar(b, y, (s * x0, z0), (s * x1, z1), .035, .03 + .01 * (sign > 0))
            c += .21 * math.sqrt(2)
    for f in (.35, .65, .9):                                                 # hangers from the strut to the rib
        x = xl + (s * ax - xl) * f
        z0 = zl + (za - zl) * f
        b.beam('iron', (x, y, z0), (x, y, vault_z(abs(x)) - .18), .05, .05)
    for cx, cz, r in ((xw - .42, zl + .75, .3), (xw - .35, EAVE - 1.35, .22)):
        annulus('bracket scroll', (s * cx, y, cz), (0, 1, 0), r - .06, r, -.035, .035, 'iron', 'vault', 12)


def girder(b, prof, y, depth=.5):
    """Main rib as a lattice girder: an inner chord 0.5 m below the outer rib and a zig-zag web of bars."""
    n = len(prof)
    inner = []
    for k in range(1, n - 1):
        x, z = prof[k]
        nx, nz = normal(prof, k)
        inner.append((x + nx * (.13 + depth), z + nz * (.13 + depth)))
    for (x0, z0), (x1, z1) in zip(inner, inner[1:]):
        b.beam('iron', (x0, y, z0), (x1, y, z1), .09, .08, ext=.01)
    for k in range(1, n - 2):
        x, z = prof[k]
        nx, nz = normal(prof, k)
        bar(b, y, (x + nx * .2, z + nz * .2), inner[k - 1] if k % 2 else inner[k], .04, .035)


def crest(b, prof, y, h=.5):
    """Openwork cresting standing proud of the glazing along a rib: posts, a top rail, a zig-zag and spikes."""
    n = len(prof)
    top = []
    for k in range(1, n - 1):
        x, z = prof[k]
        nx, nz = normal(prof, k)
        tip = (x - nx * h, z - nz * h)
        if k % 2 == 1:
            bar(b, y, (x - nx * .03, z - nz * .03), tip, .04, .035)                 # posts on every second point
        top.append(tip)
        if k % 4 == 2:
            bar(b, y, tip, (x - nx * (h + .22), z - nz * (h + .22)), .05, .03)
    for (x0, z0), (x1, z1) in zip(top, top[1:]):
        b.beam('iron', (x0, y, z0), (x1, y, z1), .05, .05, ext=.01)
    for k in range(1, n - 3, 2):
        (xa, za), (xb, zb) = prof[k], prof[k + 2]
        (na, ma), (nb, mb) = normal(prof, k), normal(prof, k + 2)
        lo_a, hi_b = (xa - na * .06, za - ma * .06), (xb - nb * (h - .03), zb - mb * (h - .03))
        hi_a, lo_b = (xa - na * (h - .03), za - ma * (h - .03)), (xb - nb * .06, zb - mb * .06)
        bar(b, y, *((lo_a, hi_b) if k % 4 == 1 else (hi_a, lo_b)), w=.03, t=.03)


def ridge_crest(b, z0, h=.5):
    """Continuous ridge cresting along the vault: posts every 0.75 m, a top rail, a zig-zag and spikes every 1.5 m."""
    y, k = 0.0, 0
    while y <= L - .03 + 1e-6:
        b.beam('iron', (0.0, y, z0), (0.0, y, z0 + h), .04, .035)
        if k % 2 == 0:
            b.beam('iron', (0.0, y, z0 + h), (0.0, y, z0 + h + .25), .05, .03)
        if y + .75 <= L - .03 + 1e-6:
            za, zb = (z0 + .04, z0 + h - .04) if k % 2 else (z0 + h - .04, z0 + .04)
            b.beam('iron', (0.0, y, za), (0.0, y + .75, zb), .03, .03)
        y += .75; k += 1
    b.beam('iron', (0.0, 0.0, z0 + h), (0.0, L - .03, z0 + h), .05, .05)


def end_arch(b, prof):
    """Ornamental south end arch as its own assembly: a deep pointed outer band (outer rib, an inner chord 0.9 m
    inside it, a zig-zag web and rings the whole way round), a semicircular inner arch springing from the pavilion
    corners on the leg columns, the spandrel between them filled with radial bars and rings, a crest and an apex
    finial."""
    y = .25
    n = len(prof)
    rib(b, prof, y, .22, .3)
    band = []
    for k in range(1, n - 1):
        x, z = prof[k]
        nx, nz = normal(prof, k)
        band.append((x + nx * 1.05, z + nz * 1.05))
    for (x0, z0), (x1, z1) in zip(band, band[1:]):
        b.beam('iron', (x0, y, z0), (x1, y, z1), .16, .14, ext=.01)
    for k in range(1, n - 2):                                                # zig-zag web of the band
        x, z = prof[k]
        nx, nz = normal(prof, k)
        bar(b, y, (x + nx * .25, z + nz * .25), band[k - 1] if k % 2 else band[k], .05, .045)
    for k in range(2, n - 2, 2):                                             # rings in the band
        x, z = prof[k]
        nx, nz = normal(prof, k)
        annulus('end arch band ring', (x + nx * .66, y, z + nz * .66), (0, 1, 0), .2, .26, -.035, .035, 'iron', 'vault', 12)
    zc, R = EAVE - 2.0, HW - 1.6                                            # inner semicircle, springing on ties from the leg columns
    semi = [(R * math.cos(math.radians(a)), zc + R * math.sin(math.radians(a))) for a in range(0, 181, 6)]
    for (x0, z0), (x1, z1) in zip(semi, semi[1:]):
        b.beam('iron', (x0, y, z0), (x1, y, z1), .18, .16, ext=.01)
    bx = [p[0] for p in band]; bz = [p[1] for p in band]
    def band_z(x):
        for i in range(len(bx) - 1):
            if bx[i] <= x <= bx[i + 1]:
                f = (x - bx[i]) / ((bx[i + 1] - bx[i]) or 1.0)
                return bz[i] + (bz[i + 1] - bz[i]) * f
        return None
    for i, a in enumerate(range(8, 173, 8)):                                 # radial spandrel bars from the semicircle to the band
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        x0, z0 = R * ca, zc + R * sa
        d = .05
        while d < 4.0:
            x, z = x0 + ca * d, z0 + sa * d
            bzx = band_z(x)
            if (bzx is not None and z >= bzx - .05) or z >= vault_z(abs(x)) - .3 or abs(x) >= HW - .38:
                break
            d += .02
        if d > .3:
            bar(b, y, (x0 + ca * .05, z0 + sa * .05), (x0 + ca * d, z0 + sa * d), .06, .05)
            if d > .8 and i % 2:
                ro = min(.42, d / 2 - .1)
                annulus('end arch spandrel ring', (x0 + ca * d / 2, y, z0 + sa * d / 2), (0, 1, 0), ro - .07, ro, -.035, .035, 'iron', 'vault', 14)
    crest(b, prof, y)
    xr, zr = prof[n // 2]
    frustum(b, 'iron', 0.0, y, zr + .2, zr + 1.4, .12, 0.0, 8)               # apex finial
    annulus('end arch apex ring', (0.0, y, zr + .85), (0, 1, 0), .18, .26, -.035, .035, 'iron', 'vault', 12)
    for s in (-1, 1):                                                        # leg columns on corbels at the pavilion faces
        xl = s * (HW - .3)
        b.beam('iron', (xl, y, CORBEL - .05), (xl, y, EAVE - .74), .16, .18)
        b.beam('iron', (xl, y, EAVE + .02), (xl, y, EAVE + .2), .16, .18)
        b.beam('iron', (xl, y, zc), (s * R, y, zc), .1, .1)                  # springing tie into the semicircle
        x, yy, _ = FW.p(.25, -.24, 0) if s < 0 else FE.p(.25, -.24, 0)
        b.box('stone', x, .25, CORBEL - .26, .48, .5, .52)


def diamond_bands(b, x0, x1, y0, y1, z, s, w, role):
    """Diagonal bands of a diamond lattice clipped to a rectangle (flat quads)."""
    h = w / 2 / math.sqrt(2)
    for sign in (1, -1):
        c = (y0 - x1) if sign > 0 else (y0 + x0)
        cmax = (y1 - x0) if sign > 0 else (y1 + x1)
        c = math.ceil(c / s) * s
        while c <= cmax:
            if sign > 0:
                xa, xb = max(x0, y0 - c), min(x1, y1 - c)
            else:
                xa, xb = max(x0, c - y1), min(x1, c - y0)
            if xb - xa > .05:
                ya, yb = sign * xa + c, sign * xb + c
                zz = z + (.0015 if sign < 0 else 0.0)
                quad(b, role, [(xa + sign * h, ya - h, zz), (xb + sign * h, yb - h, zz), (xb - sign * h, yb + h, zz), (xa - sign * h, ya + h, zz)])
            c += s


def border(b, x0, x1, y0, y1, z, w, role):
    z += .003
    quad(b, role, [(x0, y0, z), (x1, y0, z), (x1, y0 + w, z), (x0, y0 + w, z)])
    quad(b, role, [(x0, y1 - w, z), (x1, y1 - w, z), (x1, y1, z), (x0, y1, z)])
    quad(b, role, [(x0, y0 + w, z), (x0 + w, y0 + w, z), (x0 + w, y1 - w, z), (x0, y1 - w, z)])
    quad(b, role, [(x1 - w, y0 + w, z), (x1, y0 + w, z), (x1, y1 - w, z), (x1 - w, y1 - w, z)])


XQ = XP - 1.0                                                                # west edge of the square (pavilion width)


def ground():
    """Asphalt at grade zero, sidewalks with curbs, the tiled passage floor and the tiled square at the mouth."""
    C.prism('Street asphalt', [(XMIN, YMIN), (XMAX, YMIN), (XMAX, YMAX), (XMIN, YMAX)], 'z', 0.0, .02, 'asphalt', 'street')
    walks = [(XW - SW, XW, 0.0, YN), (XE, XE + SW, 0.0, YN), (XW - SW, XE + SW, YN, YN + SW),          # around the passage block
             (XWS, XWS + SW, YSQ, YN + SW), (XMIN + .01, XWS, YSQ, YSQ + SW), (XMIN + .01, XWS, YN, YN + SW),   # west context
             (XES - SW, XES, YSQ, YN + SW), (XES, XMAX - .01, YSQ, YSQ + SW), (XES, XMAX - .01, YN, YN + SW),   # east context
             (XMIN + .01, XMAX - .01, YNS - SW, YNS), (XMIN + .01, XMAX - .01, YSS, YSS + SW)]                       # north and south contexts
    for x0, x1, y0, y1 in walks:
        C.prism('Sidewalk', [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], 'z', .005, .15, 'concrete', 'sidewalks')
    C.prism('Sidewalk', [(XW - SW, YSQ), (XQ, YSQ), (XQ, 0.0), (XW - SW, 0.0)], 'z', .005, .15, 'concrete', 'sidewalks')
    C.prism('Square tiles', [(XQ, YSQ), (XE, YSQ), (XE, 0.0), (XQ, 0.0)], 'z', .005, FZ, 'tile', 'square')
    C.prism('Sidewalk', [(XE, YSQ), (XE + SW, YSQ), (XE + SW, 0.0), (XE, 0.0)], 'z', .005, .15, 'concrete', 'sidewalks')
    C.prism('Passage tiles', [(-HW, 0.0), (HW, 0.0), (HW, YN), (-HW, YN)], 'z', .005, FZ, 'tile', 'passage floor')
    b = Batch()
    diamond_bands(b, -HW + .55, HW - .55, .4, L - .4, FZ + .003, 1.0, .08, 'tile2')
    gx = -HW + .55 + .5
    while gx < HW - .6:                                                      # faint inner tile grid
        quad(b, 'joint', [(gx - .01, .4, FZ + .0012), (gx + .01, .4, FZ + .0012), (gx + .01, L - .4, FZ + .0012), (gx - .01, L - .4, FZ + .0012)])
        gx += .5
    gy = .9
    while gy < L - .45:
        quad(b, 'joint', [(-HW + .55, gy - .01, FZ + .002), (HW - .55, gy - .01, FZ + .002), (HW - .55, gy + .01, FZ + .002), (-HW + .55, gy + .01, FZ + .002)])
        gy += .5
    border(b, -HW + .25, HW - .25, .1, L - .1, FZ + .003, .2, 'tile2')
    diamond_bands(b, XQ + .5, XE - .5, YSQ + .5, -.5, FZ + .003, 1.6, .14, 'tile2')
    border(b, XQ + .2, XE - .2, YSQ + .2, -.2, FZ + .003, .28, 'tile2')
    b.flush('floor patterns')


def furniture():
    """Benches on the axis, cafe tables near the portal, wall-side planters, awnings, lamp posts on the square."""
    b = Batch()
    for yc in (15.6, 23.0):                                                  # back-to-back benches on the axis
        for s in (-1, 1):
            x = s * .48
            for k in range(4):
                b.box('timber', x + (k * .1 - .15), yc, FZ + .43, .08, 1.9, .04)
            for k in range(3):
                b.box('timber', x - s * .22, yc, FZ + .62 + k * .14, .04, 1.9, .09)
            for e in (-.8, .8):
                b.beam('iron', (x - .2, yc + e, FZ), (x + .05, yc + e, FZ + .41), .05, .05)
                b.beam('iron', (x + .2, yc + e, FZ), (x - .05, yc + e, FZ + .41), .05, .05)
                b.beam('iron', (x - s * .25, yc + e, FZ + .4), (x - s * .25, yc + e, FZ + .98), .05, .05)
    for xc, yc in ((3.4, 26.5), (3.4, 23.6), (2.2, 28.4)):                   # cafe tables and chairs (east side)
        frustum(b, 'iron', xc, yc, FZ, FZ + .7, .04, .04, 6)
        frustum(b, 'iron', xc, yc, FZ, FZ + .03, .25, .25, 10)
        frustum(b, 'trim', xc, yc, FZ + .7, FZ + .74, .38, .38, 14)
        for dx, dy in ((.7, 0.0), (-.7, 0.0)):
            cx, cy = xc + dx, yc + dy
            b.box('timber', cx, cy, FZ + .46, .42, .42, .04)
            b.box('timber', cx + (.19 if dx > 0 else -.19), cy, FZ + .74, .04, .4, .5)
            for ex in (-.17, .17):
                for ey in (-.17, .17):
                    b.box('iron', cx + ex, cy + ey, FZ + .22, .03, .03, .44)
    for x in (-4.6, 4.6):                                                    # planters by the portal
        frustum(b, 'pot', x, L - .9, FZ, FZ + .6, .3, .38, 10)
        smooth(A.foliage('Planter shrub', (x, L - .9, FZ + 1.0), (.42, .42, .5), detail=1))
    for x in (XQ + .8, XE - .8):                                              # lamp posts on the square
        y = -6.0
        frustum(b, 'iron', x, y, FZ, FZ + .5, .2, .14, 8)
        b.beam('iron', (x, y, FZ + .5), (x, y, FZ + 3.6), .1, .1)
        for s in (-1, 1):
            b.beam('iron', (x, y, FZ + 3.4), (x + s * .45, y, FZ + 3.75), .04, .04)
            b.box('lamp', x + s * .45, y, FZ + 3.55, .2, .2, .34)
            b.box('iron', x + s * .45, y, FZ + 3.76, .26, .26, .06)
    b.flush('furniture')
    awning(FE, 22.8 - 1.7, 22.8 + 1.7)                                       # clipped to the shop openings
    awning(FE, 27.6 - 1.7, 27.6 + 1.7)
    awning(FW, 18.0 - 1.7, 18.0 + 1.7)


def car(b, x, y, ux, uy, role):
    vx, vy = -uy, ux
    b.beam(role, (x - ux * 2.2, y - uy * 2.2, .62), (x + ux * 2.2, y + uy * 2.2, .62), 1.76, .6)
    b.beam('dark', (x - ux * 1.2, y - uy * 1.2, 1.12), (x + ux * .95, y + uy * .95, 1.12), 1.58, .46)
    b.beam(role, (x - ux * 1.15, y - uy * 1.15, 1.37), (x + ux * .9, y + uy * .9, 1.37), 1.5, .06)
    for s in (-1.4, 1.4):
        for t in (-.79, .79):
            cx, cy = x + ux * s + vx * t, y + uy * s + vy * t
            b.beam('tyre', (cx - vx * .13, cy - vy * .13, .34), (cx + vx * .13, cy + vy * .13, .34), .62, .62)


def ctx_block(x0, x1, y0, y1, h, faces, label):
    """Cream stuccoed apartment block: bulk, terracotta roof deck inside a parapet, a rooftop room, and proud windows
    with stone balcony slabs and iron rails on its street faces."""
    b = Batch()
    b.box('stucco2', (x0 + x1) / 2, (y0 + y1) / 2, h / 2, x1 - x0, y1 - y0, h)
    b.box('terracotta', (x0 + x1) / 2, (y0 + y1) / 2, h + .03, x1 - x0 - .6, y1 - y0 - .6, .06)
    for a0, b0, a1, b1 in ((x0, y0, x1, y0 + .3), (x0, y1 - .3, x1, y1), (x0, y0 + .3, x0 + .3, y1 - .3), (x1 - .3, y0 + .3, x1, y1 - .3)):
        b.box('stucco', (a0 + a1) / 2, (b0 + b1) / 2, h + .45, a1 - a0, b1 - b0, .9)
    for fx, fy, sx, sy in ((.35, .4, 3.0, 3.5), (.75, .7, 4.0, 2.6), (.15, .8, 2.4, 2.4)):     # rooftop rooms
        b.box('white', x0 + (x1 - x0) * fx, y0 + (y1 - y0) * fy, h + 1.2, sx, sy, 2.4)
    for face in faces:
        if face in 'ns':
            n = (0, -1) if face == 's' else (0, 1); t_ = (1, 0); yf = y0 if face == 's' else y1
            cs = [(x0 + 1.8 + 3.0 * i, yf) for i in range(int((x1 - x0 - 2.4) / 3.0) + 1)]
        else:
            n = (-1, 0) if face == 'w' else (1, 0); t_ = (0, 1); xf = x0 if face == 'w' else x1
            cs = [(xf, y0 + 1.8 + 3.0 * i) for i in range(int((y1 - y0 - 2.4) / 3.0) + 1)]
        for c in cs:
            z, k = .9, 0
            while z + 2.2 < h - .6:
                proud_window_lite(b, c, t_, n, z, 1.2, 2.4 if k == 0 else 2.1, balcony=k > 0)
                z += 3.2; k += 1
    b.flush(label)


def context():
    """Stuccoed blocks across the west, east, north and south streets; street trees and parked cars."""
    ctx_block(XMIN + .01, XWS, YSQ + SW, YN, 17.0, 'es', 'west context')
    ctx_block(XES, XMAX - .01, YSQ + SW, YN, 16.4, 'ws', 'east context')
    ctx_block(XMIN + .01, XMAX - .01, YNS, YMAX - .01, 17.6, 's', 'north context')
    ctx_block(XMIN + .01, XMAX - .01, YMIN + .01, YSS, 16.4, 'n', 'south context')
    for x in (-3.2, 4.0):
        street_tree(x, YNS - 1.0, z=.15, height=7.5, spread=1.7)
    b = Batch()
    for i, y in enumerate((5.0, 13.5, 26.0)):
        car(b, XE + SW + 1.1, y, 0.0, 1.0, ('car', 'car2', 'car3')[i])
    for i, x in enumerate((-12.0, 8.0)):
        car(b, x, YNS - SW - 1.1, 1.0, 0.0, ('car3', 'car')[i])
    b.flush('parked cars')


def build():
    ground()
    passage_block()
    north_end_wall()
    vault()
    furniture()
    context()
    C.CONTACTS.append(dict(name='Barcelona passatge: glass-vaulted passage on tiles between brick shop facades, end wall portal, tiled square, streets', box=[XMIN, XMAX, YMIN, YMAX]))


LIGHT_RIG = dict(key=(-40, -30, 55), fill=(40, -20, 35), rear=(10, 60, 45), target=(0.0, 15.0, 6.0), gain=5.0)
