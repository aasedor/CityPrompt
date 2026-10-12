"""Heavy-industrial crane-way hall with rail yard, authored from the locked catalogue views
of early_20c_megastructure_industrial / variant_1 (heavy_craneway_hall).

Read from the pixels: a long galvanised corrugated hall with a tall central nave and two
lower lean-to aisles; lattice steel columns with X-bracing on the aisle walls between
hooded windows; a continuous glazed clerestory band on the nave walls above the aisle
roofs; gabled roof monitors in three rows; a gable end whose lower storey carries three
green sliding doors and whose upper storey is an open steel frame revealing the overhead
crane; an external steel stair at the front corner; concrete yard apron and two rail
sidings with a boxcar along one long side.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G
from contract import subtract_openings

SLUG = 'clay-craneway-hall'
L = 84.0                                 # east-west length
NAVE, AISLE = 19.5, 8.25
W = NAVE + 2 * AISLE                     # 36 m across
T = .25
G0 = .15
A_EAVE, A_TOP = 8.6, 13.1                # gallery level on the aisle wall, and the aisle roof against the nave wall (v007: 8.6 so the glazed upper storey is 4 m tall)
AE2 = 12.6                               # aisle outer eave over the glazed upper storey: the roof strip above it is a narrow near-flat band
N_EAVE, RIDGE = 17.5, 20.5               # nave eaves and ridge
CL0, CL1 = 13.4, 16.4                    # nave clerestory band
BAY = 7.0
X0, X1 = -L / 2, L / 2
YA0, YA1 = -W / 2, W / 2                 # aisle outer walls
YN0, YN1 = -NAVE / 2, NAVE / 2           # nave walls
YARD_S, YARD_N, YARD_W, YARD_E = 12.0, 18.0, 12.0, 8.0
EPS = .002
PALETTE = dict(wall=(.50, .49, .44), joint=(.36, .34, .30), trim=(.12, .12, .12),
    pale=(.44, .44, .42), stone=(.46, .45, .43), roof=(.46, .44, .38), sand=(.52, .36, .22),
    foundation=(.42, .42, .41), glass=(.50, .55, .54), hardware=(.10, .10, .11),
    interior=(.72, .68, .60), floor=(.40, .40, .39), timber=(.40, .30, .20), blue=(.14, .22, .28),
    planting=(.40, .42, .22), soil=(.19, .14, .08), green=(.34, .44, .34), rust=(.50, .30, .18),
    rail=(.30, .28, .26), car=(.45, .20, .14))


def manifest(version):
    h = RIDGE + 2.8
    cams = G.camera_roster(L + YARD_W + YARD_E, W + YARD_S + YARD_N, h, [
        ('facade_close', (-36.0, -42.0, 6.0), (-22.0, YA0, 6.0), 45),
        ('architecture_close', (-20.0, -40.0, 16.0), (-6.0, YA0, 14.0), 50),
        ('glass_close', (-12.0, -32.0, 3.6), (-8.0, YA0, 3.6), 50),
        ('gable_mouth', (-70.0, -22.0, 8.0), (X0, 0.0, 9.0), 40),
        ('crane_interior', (-62.0, 0.0, 14.5), (X0 + 12.0, 0.0, 14.0), 40),
        ('monitor_close', (-30.0, -36.0, 30.0), (-18.0, -13.0, 16.0), 45),
        ('stair_contact', (-48.0, -34.0, 5.0), (X0 + 4.0, YA0, 6.0), 40),
        ('yard_sidings', (-30.0, 48.0, 8.0), (-6.0, YA1 + 8.0, 2.0), 40),
        ('interior', (X0 + 6.0, -3.0, 4.0), (X0 + 40.0, 3.0, 7.0), 30),
        ('side_doors', (X0 + 8.5 * BAY - 9.0, -36.0, 4.0), (X0 + 8.5 * BAY, YA0, 4.0), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='early_20c_megastructure_industrial/variant_1 (heavy_craneway_hall)',
        measurement_contract=dict(dimensions_m=dict(width=L + YARD_W + YARD_E, depth=W + YARD_S + YARD_N, height=h),
            observed_storeys=1, storey_programme='single-volume crane hall with a crane-rail level; fixed authored assembly',
            plan=f'long hall {L} x {W} m: nave {NAVE} m between lean-to aisles of {AISLE} m; twelve {BAY} m bays; gable end to the west; sidings on the north',
            section=dict(aisle_eave_m=A_EAVE, aisle_top_m=A_TOP, nave_eave_m=N_EAVE, ridge_m=RIDGE, clerestory_m=[CL0, CL1]),
            gable_end='lower storey clad with three green sliding doors across the nave; upper storey an open lattice frame with the crane girder visible; clad gable triangle above',
            aisle_walls='lattice columns with X-bracing every bay, a deep sloping corrugated pent roof across every bay at mid-wall over a low wide window band, roll-up doors in two bays',
            monitors='four gabled monitors on each aisle roof and three on the nave ridge, glazed on their long sides',
            yard='concrete apron all round; two rail sidings with a boxcar along the north side; external stair at the south-west corner',
            inferred='84 m length calibrates twelve bays; the east gable end is not visible and repeats the west end without the open frame; the crane and interior are teaching assumptions.'),
        roof_contract=dict(type='low-pitch gable over the nave, lean-to aisle roofs, nine gabled monitors in three staggered rows, ridges across the hall; corrugated plates', datum_m=A_EAVE, crowns_m=[RIDGE, RIDGE + 2.8]),
        identity_contract=dict(owner='stepped nave-and-aisle silhouette with glazed clerestory and monitor rows, open-framed gable mouth over green sliding doors, lattice X-braced aisle walls, external stair, rail sidings'),
        material_contract=dict(profile='source-palette clay: weathered galvanised corrugated cladding with recessed seams, dark steel lattice, green painted doors, rusty corrugated roofs, concrete apron, dark rails and sleepers', textured_keeper=False),
        programme_contract=dict(storeys=1, nave='crane hall with an overhead travelling crane on rails at 14 m', aisles='workshop bays with benches', stairs='external steel stair to the aisle roof at the south-west corner'),
        contact_contract=['Grade-zero slab and apron', 'Sliding doors on a floor track', 'Aisle roofs bear on the aisle walls and the nave columns', 'Monitors seated on the roof plates with cheek walls following the slope', 'Crane girder on the nave columns', 'Stair stringers bear on the apron and the aisle roof landing'],
        runtime_contract=dict(scale='fixed_native_only', installation='not installed', review='NOT TESTED'),
        camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])


def hole(name, u, z, w, h, **kw):
    return dict(id=name, u=u, z=z, w=w, h=h, **kw)


def seams(f, lo, hi, z0, z1, holes, spacing=.9):
    vertices, faces = [], []
    n = max(1, round((hi - lo) / spacing))
    for i in range(1, n):
        u = lo + i * (hi - lo) / n
        spans = [(z0, z1)]
        for h in holes:
            if h['u'] - h['w'] / 2 - .01 < u < h['u'] + h['w'] / 2 + .01:
                spans = [s for a, b in spans for s in ((a, min(b, h['z'])), (max(a, h['z'] + h['h']), b)) if s[1] - s[0] > .001]
        for a, b in spans:
            o = len(vertices)
            vertices.extend([f.p(u - .006, -.002, a), f.p(u + .006, -.002, a), f.p(u + .006, -.002, b), f.p(u - .006, -.002, b)])
            faces.append((o, o + 1, o + 2, o + 3))
    if faces:
        C.mesh(f.label + ' corrugation seams', vertices, faces, 'joint', 'cladding seams')


def punched(f, name, u, z, w, h, hood=True):
    inset = .16
    ring = f.part(name + ' reveal and frame', u, (inset + .07) / 2, z + h / 2, w, inset + .07, h, 'trim', 'window frames', 0)
    f.cut(ring, name + ' frame clear', u, z + .07, w - .14, h - .14, inset + .07)
    f.part(name + ' pane', u, inset + .06, z + h / 2, w - .14, .008, h - .14, 'glass', 'window glazing', 0)
    if hood:
        a = f.p(u - w / 2 - .2, -.02, z + h + .10); b = f.p(u + w / 2 + .2, -.02, z + h + .10)
        c = f.p(u + w / 2 + .2, -.70, z + h - .25); d = f.p(u - w / 2 - .2, -.70, z + h - .25)
        C.mesh(name + ' awning hood', [a, b, c, d, (a[0], a[1], a[2] - .04), (b[0], b[1], b[2] - .04), (c[0], c[1], c[2] - .04), (d[0], d[1], d[2] - .04)],
               [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 'roof', 'window hoods')
    C.OPENINGS.append(dict(id=name, face=f.label, u=u, z=z, width=w, height=h, kind='window', clear_wall_cut=True,
        carrier_depth_m=T, frame_inset_m=inset, pane_inset_m=inset + .06, face_origin=list(f.o), face_tangent=list(f.t),
        face_inward=list(f.n), occupied_space='workshop aisle behind carrier', cols=1, rows=1))


def lattice_column(f, u, z0, z1, proud=.60, w=2.8, panels=4):
    """Wide lattice pier: two flanges with stacked X-laced panels between them."""
    f.part('Lattice column flange', u - w / 2 + .06, -proud / 2 + EPS, (z0 + z1) / 2, .12, proud, z1 - z0, 'pale', 'lattice columns', 0)
    f.part('Lattice column flange', u + w / 2 - .06, -proud / 2 + EPS, (z0 + z1) / 2, .12, proud, z1 - z0, 'pale', 'lattice columns', 0)
    for i in range(panels):
        za, zb = z0 + .08 + i * (z1 - z0 - .16) / panels, z0 + .08 + (i + 1) * (z1 - z0 - .16) / panels
        C.beam('Lattice lacing', f.p(u - w / 2 + .12, -proud / 2, za), f.p(u + w / 2 - .12, -proud / 2, zb), .06, .06, 'pale', 'lattice columns')
        C.beam('Lattice lacing', f.p(u - w / 2 + .12, -proud / 2, zb), f.p(u + w / 2 - .12, -proud / 2, za), .06, .06, 'pale', 'lattice columns')
        f.part('Lattice batten', u, -proud / 2 + EPS, zb, w - .24, proud, .08, 'pale', 'lattice columns', 0)


def brace(f, u0, u1, z0, z1):
    C.beam('Wall X-brace', f.p(u0 + .35, -.08, z0 + .3), f.p(u1 - .35, -.08, z1 - .3), .07, .07, 'pale', 'wall bracing')
    C.beam('Wall X-brace', f.p(u0 + .35, -.08, z1 - .3), f.p(u1 - .35, -.08, z0 + .3), .07, .07, 'pale', 'wall bracing')


def aisle_wall(f, doors=(), stair_bay=None):
    """Long aisle wall: lattice columns every bay, X-braces, hooded windows, roll-up doors."""
    bays = [X0 + i * BAY for i in range(13)]
    holes = []
    for i in range(12):
        c = (bays[i] + bays[i + 1]) / 2
        u = c if f.label == 'south aisle' else -c
        if i in doors:
            holes.append(hole(f'{f.label} roll-up door {i}', u, G0, 4.2, 4.6, kind='door'))
        else:
            holes.append(hole(f'{f.label} window {i}', u, 1.15, 3.9, 2.05))      # low wide window band (sources: about 12-32 percent of the wall)
    f.wall(f.label + ' carrier', X0, X1, G0, A_EAVE, depth=T, holes=holes)
    seams(f, X0 + .3, X1 - .3, G0 + EPS, A_EAVE - EPS, holes)
    for h in holes:
        if h.get('kind') == 'door':
            f.part(h['id'] + ' leaf', h['u'], .22, h['z'] + h['h'] / 2, h['w'] - .06, .05, h['h'] - .02, 'pale', 'roll-up doors', 0)
            for k in range(1, 6):
                f.part(h['id'] + ' slat seam', h['u'], .19, h['z'] + k * h['h'] / 6, h['w'] - .10, .012, .012, 'joint', 'roll-up doors', 0)
            for s in (-1, 1):
                f.part(h['id'] + ' guide', h['u'] + s * (h['w'] / 2 - .05), .16, h['z'] + h['h'] / 2, .10, .14, h['h'], 'trim', 'roll-up doors', 0)
            f.part(h['id'] + ' head', h['u'], .16, h['z'] + h['h'] - .08, h['w'] - .2, .14, .16, 'trim', 'roll-up doors', 0)
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='roll-up door', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=.16, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='workshop aisle'))
        else:
            punched(f, h['id'], h['u'], h['z'], h['w'], h['h'], hood=False)
    # Deep corrugated pent roof over every bay, full clear width between the lattice columns, top at about 56 percent of
    # the wall, projecting 1.7 m at about 27 degrees: one continuous shadow band along the aisle wall.
    zt, proj = .56 * A_EAVE, 1.7
    drop = proj * math.tan(math.radians(27))
    for i in range(12):
        c = (bays[i] + bays[i + 1]) / 2
        u = c if f.label == 'south aisle' else -c
        hw = (BAY - 2.8) / 2 - .02
        a = f.p(u - hw, -.02, zt); b = f.p(u + hw, -.02, zt); cc = f.p(u + hw, -proj, zt - drop); d = f.p(u - hw, -proj, zt - drop)
        dz = .12
        C.mesh(f'{f.label} pent hood {i}', [a, b, cc, d, (a[0], a[1], a[2] - dz), (b[0], b[1], b[2] - dz), (cc[0], cc[1], cc[2] - dz), (d[0], d[1], d[2] - dz)],
               [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)], 'roof', 'window hoods')
    for i, x in enumerate(bays):
        u = x if f.label == 'south aisle' else -x
        lattice_column(f, u, 0, A_EAVE - .02)
    # Railed gallery walkway on a bracketed beam at the top of the lattice wall, with a tall mullioned glazed storey above it.
    f.part('Gallery beam', 0, -.38, A_EAVE - .22, L, .52, .44, 'pale', 'gallery', 0)
    f.part('Gallery deck', 0, -1.28, A_EAVE + .03, L, 1.32, .06, 'pale', 'gallery', 0)
    for i, x in enumerate(bays):
        u = x if f.label == 'south aisle' else -x
        C.beam('Gallery bracket', f.p(u, -.62, A_EAVE - 1.5), f.p(u, -1.85, A_EAVE - .02), .08, .08, 'pale', 'gallery')
    C.beam('Gallery top rail', f.p(X0, -1.9, A_EAVE + 1.06), f.p(X1, -1.9, A_EAVE + 1.06), .05, .05, 'hardware', 'gallery')
    C.beam('Gallery mid rail', f.p(X0, -1.9, A_EAVE + .55), f.p(X1, -1.9, A_EAVE + .55), .03, .03, 'hardware', 'gallery')
    for k in range(25):
        u = X0 + .1 + k * (L - .2) / 24
        C.beam('Gallery post', f.p(u, -1.9, A_EAVE + .06), f.p(u, -1.9, A_EAVE + 1.08), .05, .05, 'hardware', 'gallery')
    f.part('Upper storey sill', 0, .10, A_EAVE + .06, L - .02, .20, .12, 'trim', 'upper glazing', 0)
    f.part('Upper storey head', 0, .10, AE2 - .06, L - .02, .20, .12, 'trim', 'upper glazing', 0)
    f.part('Upper storey glazing', 0, .14, (A_EAVE + AE2) / 2, L - .1, .012, AE2 - A_EAVE - .24, 'glass', 'upper glazing', 0)
    for k in range(37):
        f.part('Upper storey mullion', X0 + .05 + k * (L - .1) / 36, .10, (A_EAVE + AE2) / 2, .09, .18, AE2 - A_EAVE - .24, 'trim', 'upper glazing', 0)
    f.part('Aisle eave channel', 0, -.12, AE2 + .10, L, .24, .20, 'pale', 'eaves', 0)
    f.part('Concrete plinth', 0, -.02, .25, L - .4, .20, .50, 'stone', 'plinth', 0)


def gable_end(f, open_frame=True):
    """West (open_frame) or east gable end across the full 36 m: aisle walls to their eaves, nave end."""
    s = -1 if open_frame else 1          # west face u = -y ; east face u = y
    def uu(y): return -y if open_frame else y
    holes = []
    if open_frame:
        holes.append(hole('Sliding door opening', 0.0, G0, 13.5, 8.6, kind='slider'))
    else:
        holes.append(hole('East roll-up door', 0.0, G0, 6.0, 6.5, kind='rollup'))
        holes.append(hole('East aisle window 0', uu(-13.0), 3.2, 3.2, 2.2)); holes.append(hole('East aisle window 1', uu(13.0), 3.2, 3.2, 2.2))
    # Lower storey: one solid corrugated wall across the full gable width on both ends (west: aisles included, sources).
    f.wall(f.label + ' lower carrier', -W / 2 + T, W / 2 - T, G0, A_EAVE, depth=T, holes=holes)
    seams(f, -W / 2 + T + .3, W / 2 - T - .3, G0 + EPS, A_EAVE - EPS, holes)
    if open_frame:
        for y in (YA0 + 1.5, YA1 - 1.5):                   # corner lattice columns only
            lattice_column(f, uu(y), 0, A_EAVE - .02, proud=.6, w=2.2, panels=4)
    for h in holes:
        if h.get('kind') == 'slider':
            # Three green sliding leaves on a head track, the middle one ajar.
            for k, du in enumerate((-4.5, 0.0, 4.5)):
                f.part(f'Sliding door leaf {k}', du, .30 + (.12 if k == 1 else 0), h['z'] + h['h'] / 2 - .05, 4.4, .08, h['h'] - .12, 'green', 'sliding doors', 0)
                for zz in (h['z'] + 2.1, h['z'] + 4.3, h['z'] + 6.5):
                    f.part('Sliding door rail', du, .255 + (.12 if k == 1 else 0), zz, 4.3, .02, .08, 'joint', 'sliding doors', 0)
            f.part('Door head track', 0.0, .12, h['z'] + h['h'] + .12, h['w'] + 1.0, .40, .24, 'trim', 'sliding doors', 0)
            for side in (-1, 1):
                f.part('Door jamb liner', side * (h['w'] / 2 - .011), T / 2, h['z'] + h['h'] / 2, .022, T, h['h'], 'pale', 'reveals', 0)
            f.part('Door head liner', 0.0, T / 2, h['z'] + h['h'] - .011, h['w'], T, .022, 'pale', 'reveals', 0)
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='sliding door', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=.30, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='crane hall'))
        elif h.get('kind') == 'door':
            f.door(h['id'], h['u'], h['z'], h['w'], h['h'], role='green', panels=1)
            f.part('Door step', h['u'], -.17, G0 / 2, 1.4, .34, G0, 'stone', 'entry steps', 0)
        elif h.get('kind') == 'rollup':
            f.part(h['id'] + ' leaf', h['u'], .22, h['z'] + h['h'] / 2, h['w'] - .06, .05, h['h'] - .02, 'pale', 'roll-up doors', 0)
            for k in range(1, 6):
                f.part(h['id'] + ' slat seam', h['u'], .19, h['z'] + k * h['h'] / 6, h['w'] - .10, .012, .012, 'joint', 'roll-up doors', 0)
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='roll-up door', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=.19, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='crane hall'))
        else:
            punched(f, h['id'], h['u'], h['z'], h['w'], h['h'], hood=False)
    # Aisle ends above the eaves: clad triangles on the east end, open X-braced frames with a rail on the west end.
    for sign in (-1, 1):
        ya, yb = sign * YN1, sign * YA1
        if not open_frame:
            poly = [(uu(yb), A_EAVE - EPS), (uu(ya), A_EAVE - EPS), (uu(ya), A_TOP), (uu(yb), AE2)]
            f.panel(f'Aisle end crown {sign}', poly, 0, T, 'wall', 'gable crowns')
        else:
            # Aisle upper storey as a full-height open truss frame above the solid lower wall.
            C.beam('Aisle end rafter', f.p(uu(yb), -.10, AE2), f.p(uu(ya), -.10, A_TOP), .18, .30, 'pale', 'open frame')
            C.beam('Aisle end post', f.p(uu(yb), -.10, A_EAVE), f.p(uu(yb), -.10, AE2), .25, .25, 'pale', 'open frame')
            C.beam('Aisle end truss diagonal', f.p(uu(yb), -.12, A_EAVE + .1), f.p(uu(ya), -.12, A_TOP - .2), .07, .07, 'pale', 'open frame')
            C.beam('Aisle end truss diagonal', f.p(uu(ya), -.12, A_EAVE + .1), f.p(uu(yb), -.12, AE2 - .2), .07, .07, 'pale', 'open frame')
            C.beam('Aisle end brace', f.p(uu(yb) + (.3 if uu(yb) < uu(ya) else -.3), -.12, A_EAVE), f.p(uu(ya) - (.3 if uu(yb) < uu(ya) else -.3), -.12, A_EAVE + .1), .07, .07, 'pale', 'open frame')
            C.beam('Aisle end brace', f.p(uu(ya) - (.3 if uu(yb) < uu(ya) else -.3), -.12, A_EAVE), f.p(uu((ya + yb) / 2), -.12, A_TOP - 1.3), .07, .07, 'pale', 'open frame')
            C.beam('Aisle end mid post', f.p(uu((ya + yb) / 2), -.10, A_EAVE), f.p(uu((ya + yb) / 2), -.10, (AE2 + A_TOP) / 2 - .15), .20, .20, 'pale', 'open frame')
            C.railing('Aisle end rail', f.p(uu(yb), -.10, A_EAVE), f.p(uu(ya), -.10, A_EAVE), height=1.0, spacing=.35, role='hardware')
    # Nave end: open lattice frame between the aisle top and the nave eaves (west) or clad (east); clad gable triangle above.
    if open_frame:
        for y in (YN0 + .4, -4.0, 4.0, YN1 - .4):
            lattice_column(f, uu(y), A_EAVE - EPS, N_EAVE + .2, proud=.5, w=.6)
        C.beam('Crane girder end truss top chord', f.p(uu(YN0), -.25, 14.6), f.p(uu(YN1), -.25, 14.6), .18, .18, 'pale', 'open frame')
        C.beam('Crane girder end truss bottom chord', f.p(uu(YN0), -.25, 13.2), f.p(uu(YN1), -.25, 13.2), .18, .18, 'pale', 'open frame')
        for k in range(8):
            ya = YN0 + k * NAVE / 8; yb = ya + NAVE / 8
            C.beam('End truss diagonal', f.p(uu(ya), -.25, 13.2), f.p(uu(yb), -.25, 14.6), .07, .07, 'pale', 'open frame')
        C.beam('Nave eave beam', f.p(uu(YN0), -.10, N_EAVE), f.p(uu(YN1), -.10, N_EAVE), .25, .35, 'pale', 'open frame')
        # Continuous mullioned glazed band across the nave gable directly under the clad triangle; the crane zone stays open below.
        gz0, gz1 = 14.95, N_EAVE - .18
        f.part('Gable band sill', 0.0, .10, gz0, NAVE - .1, .20, .14, 'trim', 'gable glazing', 0)
        f.part('Gable band glazing', 0.0, .14, (gz0 + gz1) / 2, NAVE - .2, .012, gz1 - gz0 - .1, 'glass', 'gable glazing', 0)
        for k in range(17):
            f.part('Gable band mullion', -NAVE / 2 + .1 + k * (NAVE - .2) / 16, .10, (gz0 + gz1) / 2, .08, .18, gz1 - gz0, 'trim', 'gable glazing', 0)
        C.OPENINGS.append(dict(id='Open gable frame', face=f.label, u=0.0, z=A_EAVE, width=NAVE - 1.2, height=N_EAVE - A_EAVE, kind='open frame', clear_wall_cut=True,
            carrier_depth_m=0.0, frame_inset_m=None, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='crane hall open to the gable'))
    else:
        f.wall(f.label + ' nave upper carrier', uu(YN0) if uu(YN0) < uu(YN1) else uu(YN1), max(uu(YN0), uu(YN1)), A_EAVE, N_EAVE, depth=T, role='wall')
        seams(f, min(uu(YN0), uu(YN1)) + .3, max(uu(YN0), uu(YN1)) - .3, A_EAVE + EPS, N_EAVE - EPS, [])
    f.panel('Nave gable crown', [(uu(YN0), N_EAVE - EPS), (uu(YN1), N_EAVE - EPS), (0.0, RIDGE)], 0, T, 'wall', 'gable crowns')
    C.beam('Gable rake trim', f.p(uu(YN0) - .2, -.06, N_EAVE - .1), f.p(0, -.06, RIDGE + .12), .08, .18, 'pale', 'gable crowns')
    C.beam('Gable rake trim', f.p(uu(YN1) + .2, -.06, N_EAVE - .1), f.p(0, -.06, RIDGE + .12), .08, .18, 'pale', 'gable crowns')


def nave_walls():
    """Nave side walls above the aisle roofs: columns, clerestory glazing band, cladding above."""
    for sign, label in ((-1, 'south nave'), (1, 'north nave')):
        y = sign * YN1
        f = C.Face((0, y, 0), (1 if sign < 0 else -1, 0, 0), (0, 1 if sign < 0 else -1, 0), label)
        f.wall(label + ' upper carrier', X0 + T, X1 - T, CL1, N_EAVE, depth=T, role='wall')
        seams(f, X0 + T + .3, X1 - T - .3, CL1 + EPS, N_EAVE - EPS, [])
        f.wall(label + ' lower carrier', X0 + T, X1 - T, A_TOP - .3, CL0, depth=T, role='wall')
        # Clerestory curtain band between the two carriers.
        f.part(label + ' clerestory sill', 0, .10, CL0 + .06, L - 2 * T, .20, .12, 'trim', 'clerestory', 0)
        f.part(label + ' clerestory head', 0, .10, CL1 - .06, L - 2 * T, .20, .12, 'trim', 'clerestory', 0)
        f.part(label + ' clerestory glazing', 0, .14, (CL0 + CL1) / 2, L - 2 * T - .1, .012, CL1 - CL0 - .24, 'glass', 'clerestory', 0)
        n = 24
        for i in range(n + 1):
            f.part(label + ' clerestory mullion', X0 + T + i * (L - 2 * T) / n, .10, (CL0 + CL1) / 2, .08, .18, CL1 - CL0 - .24, 'trim', 'clerestory', 0)
        f.part(label + ' nave eave channel', 0, -.12, N_EAVE + .10, L, .24, .20, 'pale', 'eaves', 0)
        # Nave columns from the slab to the eaves, inside the aisles below the aisle roof and exposed above it.
        for i in range(13):
            x = X0 + i * BAY
            C.box('Nave lattice column', (x, y - sign * .35, (G0 + N_EAVE) / 2), (.55, .55, N_EAVE - G0), 'pale', 'nave columns', 0)
        # Crane rail on brackets at 13.0 m along the inside of the nave columns.
        C.box('Crane rail girder', (0, y - sign * 1.0, 12.6), (L - 2 * T, .45, .9), 'pale', 'crane', 0)
        C.box('Crane rail', (0, y - sign * 1.0, 13.12), (L - 2 * T, .10, .14), 'rail', 'crane', 0)


def roofs():
    t = .22
    x0, x1 = X0, X1
    # Nave gable roof plates.
    for sign in (-1, 1):
        ya, yb = 0.0, sign * (YN1 + .4)
        za, zb = RIDGE, N_EAVE - .4 * (RIDGE - N_EAVE) / YN1
        C.prism(f'Nave roof plate {sign}', [(ya, za), (yb, zb), (yb, zb - t), (ya, za - t)], 'x', x0 + T, x1 - T, 'roof', 'roofs')
        ribs(x0 + T, x1 - T, ya, za, yb, zb)
        # Aisle lean-to plates from the nave wall down to the aisle eave.
        ya2, yb2 = sign * (YN1 - T), sign * (YA1 + .4)
        za2, zb2 = A_TOP, AE2 - .4 * (A_TOP - AE2) / AISLE
        C.prism(f'Aisle roof plate {sign}', [(ya2, za2), (yb2, zb2), (yb2, zb2 - t), (ya2, za2 - t)], 'x', x0 + T, x1 - T, 'roof', 'roofs')
        ribs(x0 + T, x1 - T, ya2, za2, yb2, zb2)
    C.beam('Ridge cap', (x0, 0, RIDGE + .05), (x1, 0, RIDGE + .05), .30, .10, 'pale', 'roofs')
    # Monitors: four per aisle roof, three on the nave ridge.
    nave_slope = lambda y: RIDGE - abs(y) * (RIDGE - N_EAVE) / YN1
    for yc, xs in ((-6.0, (-30.0, -10.0, 10.0)), (0.0, (-20.0, 0.0, 20.0)), (6.0, (-10.0, 10.0, 30.0))):
        for xc in xs:
            monitor(xc, yc, 6.0, 6.5, slope=nave_slope)   # wider and lower than v006 (P1 3)


def ribs(xa, xb, ya, za, yb, zb, spacing=1.2):
    """Corrugation seam lines down the slope of a roof plate, one dark bead every 1.2 m along the hall."""
    n = max(1, round((xb - xa) / spacing))
    for i in range(1, n):
        x = xa + i * (xb - xa) / n
        C.beam('Roof corrugation seam', (x, ya, za + .035), (x, yb, zb + .035), .05, .05, 'joint', 'roofs')


def monitor(xc, yc, w, length, slope, h=2.0, PF=.22):
    """Gabled roof monitor whose ridge runs across the hall: glazed cheeks face west and east, solid gable triangles face
    north and south, the base follows the nave roof (split at the ridge so every piece stays convex)."""
    xa, xb = xc - w / 2, xc + w / 2
    ya, yb = yc - length / 2, yc + length / 2
    top = max(slope(ya), slope(yb), slope(0.0) if ya < 0 < yb else -1e9) + h
    spans = [(ya, 0.0), (0.0, yb)] if ya < 0 < yb else [(ya, yb)]
    for x, lo, hi in ((xa, xa, xa + .16), (xb, xb - .16, xb)):
        for y0, y1 in spans:
            C.prism('Monitor cheek', [(y0, slope(y0) - .3), (y1, slope(y1) - .3), (y1, top - 1.4), (y0, top - 1.4)], 'x', lo, hi, 'wall', 'monitors')
        xm = (lo + hi) / 2
        C.box('Monitor glazing', (xm, yc, top - .7), (.012, length - .4, 1.2), 'glass', 'monitors', 0)
        C.box('Monitor head', (xm, yc, top - .06), (.16, length, .12), 'trim', 'monitors', 0)
        for k in range(1, 4):
            C.box('Monitor mullion', (xm, ya + k * length / 4, top - .7), (.14, .06, 1.2), 'trim', 'monitors', 0)
    for y, lo, hi in ((ya, ya - .16, ya), (yb, yb, yb + .16)):
        C.prism('Monitor gable end', [(xa, slope(y) - .3), (xb, slope(y) - .3), (xb, top), (xc, top + w * PF), (xa, top)], 'y', lo, hi, 'wall', 'monitors')
    for sgn in (-1, 1):
        C.prism('Monitor roof plate', [(xc, top + w * PF + .02), (xc + sgn * (w / 2 + .25), top - .25 * w * PF / (w / 2) + .02), (xc + sgn * (w / 2 + .25), top - .25 * w * PF / (w / 2) - .14), (xc, top + w * PF - .12)],
                'y', ya - .25, yb + .25, 'roof', 'monitors')


def stair():
    """Switchback steel stair at the south-west corner: two flights with an intermediate landing onto a railed walkway at the aisle eave."""
    x0, y = X0 + 2.0, YA0 - 1.3
    LZ = A_EAVE / 2
    runs = ((x0, 0.0, x0 + 7.0, LZ), (x0 + 7.0, LZ, x0, A_EAVE))
    for i, (xa, za, xb, zb) in enumerate(runs):
        n = 14
        for k in range(n):
            xk = xa + (k + .5) * (xb - xa) / n
            zk = za + (k + 1) * (zb - za) / n
            C.box('Stair tread', (xk, y, zk - .03), (abs(xb - xa) / n + .02, 1.1, .06), 'pale', 'external stair', 0)
        for s in (-1, 1):
            C.beam('Stair stringer', (xa + (.3 if xb > xa else -.3), y + s * .55, za + .32), (xb, y + s * .55, zb + .32), .06, .30, 'pale', 'external stair')
            C.railing(f'Stair rail {i}{s}', (xa, y + s * .55, za + .1), (xb, y + s * .55, zb + .1), height=1.0, spacing=.35, role='hardware')
    C.box('Intermediate landing', (x0 + 7.6, y, LZ - .03), (1.2, 1.4, .06), 'pale', 'external stair', 0)
    C.railing('Intermediate landing rail', (x0 + 7.0, y - .6, LZ + .1), (x0 + 8.2, y - .6, LZ + .1), height=1.0, spacing=.35, role='hardware')
    C.railing('Intermediate landing end rail', (x0 + 8.2, y - .6, LZ + .1), (x0 + 8.2, y + .6, LZ + .1), height=1.0, spacing=.35, role='hardware')
    for x, z in ((x0 + 7.6, LZ), (x0 - .6, A_EAVE)):
        for s in (-1, 1):
            C.box('Stair post', (x, y + s * .6, z / 2), (.12, .12, z), 'pale', 'external stair', 0)
    # The stair lands on the full-length aisle gallery.
    C.CONTACTS.append(dict(name='Switchback stair stringers bear on the apron and the intermediate landing; walkway bracketed from the aisle wall', grade_m=0, landing_m=A_EAVE))


def yard_and_programme():
    C.box('Hall slab', (0, 0, G0 / 2), (L, W, G0), 'foundation', 'foundation', 0)
    C.box('Concrete apron', ((X0 - YARD_W + X1 + YARD_E) / 2, (YA0 - YARD_S + YA1 + YARD_N) / 2, .0075), (L + YARD_W + YARD_E, W + YARD_S + YARD_N, .015), 'foundation', 'apron', 0)
    # Two sidings along the north side.
    for yy in (YA1 + 6.0, YA1 + 12.0):
        for dy in (-.72, .72):
            C.box('Rail', ((X0 - YARD_W + X1 + YARD_E) / 2, yy + dy, .085), (L + YARD_W + YARD_E, .07, .14), 'rail', 'sidings', 0)
        vertices, faces = [], []
        xs = X0 - YARD_W + 1.0
        while xs < X1 + YARD_E - 1.0:
            o = len(vertices)
            vertices.extend([(xs - .12, yy - 1.2, .015), (xs + .12, yy - 1.2, .015), (xs + .12, yy + 1.2, .015), (xs - .12, yy + 1.2, .015)])
            faces.append((o, o + 1, o + 2, o + 3)); xs += .7
        C.mesh(f'Sleepers {yy:.0f}', vertices, faces, 'rail', 'sidings')
    bx, by = 36.0, YA1 + 12.0
    C.box('Boxcar body', (bx, by, 1.3 + 1.6), (14.0, 2.8, 3.2), 'car', 'rolling stock', 0)
    C.box('Boxcar underframe', (bx, by, 1.15), (14.0, 2.4, .30), 'hardware', 'rolling stock', 0)
    for dx in (-4.5, 4.5):
        for dy in (-.72, .72):
            C.rod('Boxcar wheel', (bx + dx - .9, by + dy, .5), (bx + dx + .9, by + dy, .5), .45, 'hardware', 'rolling stock', 10)
    # Crane bridge across the nave and interior programme.
    cx = X0 + 14.0
    C.box('Crane bridge girder', (cx, 0, 13.6), (1.2, NAVE - 2.4, 1.1), 'pale', 'crane', 0)
    C.box('Crane bridge girder', (cx + 1.8, 0, 13.6), (1.2, NAVE - 2.4, 1.1), 'pale', 'crane', 0)
    for s in (-1, 1):
        C.box('Crane end carriage', (cx + .9, s * (YN1 - 1.0), 13.5), (4.0, .9, .9), 'pale', 'crane', 0)
    C.box('Crane trolley', (cx + .9, -2.0, 14.6), (3.4, 2.2, .9), 'rust', 'crane', 0)
    C.rod('Hoist rope', (cx + .9, -2.0, 14.1), (cx + .9, -2.0, 9.5), .03, 'hardware', 'crane', 6)
    C.box('Hook block', (cx + .9, -2.0, 9.3), (.5, .3, .6), 'rust', 'crane', 0)
    for x in (-24.0, 0.0, 24.0):
        C.box('Casting on the floor', (x, 0.0, G0 + .9), (6.0, 3.0, 1.8), 'rust', 'workshop', 0)
        C.qa_room_light('Nave', (x, 0.0, 16.0), 400, 8.0)
    for x in (-30.0, -10.0, 10.0, 30.0):
        for s in (-1, 1):
            C.box('Workbench', (x, s * 13.0, G0 + .45), (4.0, 1.0, .9), 'timber', 'workshop', 0)
            C.qa_room_light('Aisle', (x, s * 13.0, 8.5), 160, 5.0)


def build():
    yard_and_programme()
    f_front, f_right, f_rear, f_left = A.faces(L, W)
    f_front.label, f_rear.label = 'south aisle', 'north aisle'
    aisle_wall(f_front, doors=(8,))
    aisle_wall(f_rear, doors=(3,))
    gable_end(f_left, open_frame=True)
    gable_end(f_right, open_frame=False)
    nave_walls()
    roofs()
    stair()
    C.CONTACTS.append(dict(name='Sliding doors on a floor track across the nave at the west gable', grade_m=0, clear_width_m=13.5, clear_height_m=8.6))
    C.CONTACTS.append(dict(name='Crane girders on the nave columns at the crane-rail level', rail_m=13.12))


LIGHT_RIG = dict(key=(-90, -110, 90), fill=(100, -50, 80), rear=(-40, 110, 90), target=(0, 0, 10.0), gain=34.0)
