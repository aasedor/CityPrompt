"""Two-storey campus office in a converted sawtooth industrial shed, authored from the
locked catalogue views of corporate_office_campus_headquarters / variant_3
(industrial_warehouse_campus_hq).

Read from the pixels: a corner-lot shed with four south-glazed sawtooth monitors
running east-west, a two-storey flat-roofed office box along the south edge whose
roof is a terrace with a perimeter rail and a packaged rooftop unit, galvanised
portal-frame columns and X-braces proud of charcoal corrugated cladding, a
corner entrance under a low canopy at the south-west, a cantilevered dock canopy
over a raised loading dock with a ramp on the south apron, and a plain gable end
to the east.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G
from contract import subtract_openings

SLUG = 'clay-campus-shed-office'
L, D = 42.0, 30.0                # east-west length, north-south depth of the enclosed building
BOX_D = 8.4                      # two-storey office box along the south edge
TOOTH = 5.4                      # sawtooth monitor pitch (four teeth)
T = .28                          # carrier thickness
G0, U = .15, 4.30                # slab top, upper office floor
EAVE = 8.40                      # box roof / terrace top and the low eave of every tooth
TOP = [12.0, 10.4, 10.4, 10.4]   # clerestory crown per tooth, south to north
FRONT_Y, REAR_Y = -D / 2, D / 2
WEST_X, EAST_X = -L / 2, L / 2
BOX_N = FRONT_Y + BOX_D          # north wall line of the office box = south edge of tooth 0
TEETH_Y = [BOX_N + k * TOOTH for k in range(4)]
BAYS = [WEST_X + 7.0 * i for i in range(7)]   # portal column lines on the south face
APRON = 9.0                      # south loading apron depth
CANOPY_Z, CANOPY_OUT = 5.2, 3.2
DOCK_H, DOCK_OUT = 1.10, 2.6
EPS = .002
# Source-sampled clay: charcoal corrugated cladding, galvanised portal steel, warm concrete
# plinths, tan-grey corrugated monitor roofs, blue-grey terrace membrane, near-black frames.
PALETTE = dict(wall=(.075, .082, .09), joint=(.04, .045, .05), trim=(.03, .028, .026),
    pale=(.50, .52, .51), stone=(.44, .40, .36), roof=(.24, .23, .21), sand=(.47, .50, .54),
    foundation=(.30, .31, .32), glass=(.50, .54, .52), hardware=(.07, .075, .08),
    interior=(.74, .70, .60), floor=(.40, .39, .37), timber=(.40, .30, .20), blue=(.14, .22, .28),
    planting=(.46, .34, .12), soil=(.19, .14, .08), membrane=(.34, .37, .40))


def manifest(version):
    h = TOP[0]
    cams = G.camera_roster(L, D + APRON, h, [
        ('facade_close', (-30.0, -27.0, 4.2), (-14.0, FRONT_Y, 3.6), 45),
        ('architecture_close', (-12.0, -24.0, 9.5), (-4.0, FRONT_Y, 7.2), 50),
        ('glass_close', (-20.5, -22.0, 2.6), (-17.5, FRONT_Y, 2.3), 50),
        ('entrance_corner', (-31.0, -23.0, 2.4), (WEST_X, -12.0, 2.4), 40),
        ('dock_contact', (12.0, -26.0, 2.2), (3.0, -16.0, 1.4), 40),
        ('terrace_roof', (-30.0, -22.0, 14.5), (-10.0, -10.5, 8.8), 45),
        ('sawtooth_contact', (-34.0, -12.0, 12.0), (WEST_X, 1.0, 9.8), 45),
        ('clerestory_close', (-6.0, -15.0, 11.2), (-2.0, BOX_N, 10.4), 45),
        ('interior', (-17.5, -24.0, 2.0), (-17.5, -9.0, 1.9), 30),
        ('stairs', (-9.0, -9.5, 3.2), (-13.5, -10.5, 2.8), 30)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='corporate_office_campus_headquarters/variant_3 (industrial_warehouse_campus_hq)',
        measurement_contract=dict(dimensions_m=dict(width=L, depth=D + APRON, height=h),
            observed_storeys=2, storey_programme='two-storey office box along the south edge; single-volume sawtooth shed behind; fixed authored assembly',
            plan='corner lot: street to the west, loading apron and lane to the south; enclosed rectangle 42 x 30 m read as 820 x 550 px in the top view',
            south_bays=6, south_bay_m=7.0, south_ground='bay 1 multi-lite window under the entrance canopy, bay 2 roll-up door, bay 3 personnel door and small window, bays 4-6 dock doors under the dock canopy',
            south_upper='blank corrugated panels between galvanised portal columns with X-braces in bays 1-2 and single diagonals in bays 3-6',
            west_face='corner entrance and sign canopy at the south end, upper multi-lite window over it, shed windows under the second and third teeth, zigzag gable crown',
            teeth=4, tooth_pitch_m=TOOTH, tooth_crowns_m=TOP, eave_m=EAVE, glazing='vertical clerestory facing south on every tooth; the south-most tooth is the tallest and its clerestory stands above the terrace',
            levels_m=[G0, U], terrace='box roof with perimeter rail, one packaged rooftop unit and ducting at the west end, access ladder at the east end',
            loading='cantilevered dock canopy over bays 2-6, raised dock with a west ramp and east steps',
            inferred='42 m length calibrates the six 7 m portal bays; the east gable end and the north wall are not visible and repeat the west/eave grammar without the entrance; interiors are teaching assumptions.'),
        roof_contract=dict(type='four single-pitch sawtooth monitors glazed to the south, low eaves to the north, plus a flat membrane terrace over the office box', datum_m=EAVE, crowns_m=TOP,
            furniture='packaged rooftop unit with ducts on the terrace; no chimneys'),
        identity_contract=dict(owner='sawtooth silhouette over a braced portal-frame office box, charcoal corrugated skin, galvanised columns and X-braces, corner entrance canopy, cantilevered dock canopy and raised dock'),
        material_contract=dict(profile='source-palette clay: charcoal corrugated cladding with recessed seams, galvanised steel frames, warm concrete plinth and dock, tan-grey corrugated monitor roofs, blue-grey terrace membrane, near-black multi-lite frames', textured_keeper=False),
        programme_contract=dict(storeys=2, ground='reception and open office in the box, open studio in the shed', upper='offices over the box with terrace access', stairs='straight supported flight in the box with a floor aperture'),
        contact_contract=['Grade-zero slab and apron', 'Dock ramp and steps meet the apron at grade', 'Dock canopy cantilevered from the portal columns with tie rods', 'Entrance canopy wraps the south-west corner', 'Tooth roofs bear on the gable walls and clerestory frames', 'Terrace rail posts seated on the box roof slab'],
        runtime_contract=dict(scale='fixed_native_only', installation='not installed', review='NOT TESTED'),
        camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])


def hole(name, u, z, w, h, **kw):
    return dict(id=name, u=u, z=z, w=w, h=h, **kw)


def reveal(f, u, z, w, h, inset=.14, role='trim'):
    d = inset / 2 + .005
    for s in (-1, 1):
        f.part('Reveal jamb liner', u + s * (w / 2 - .011), d, z + h / 2, .022, inset + .01, h, role, 'reveals', 0)
    f.part('Reveal head liner', u, d, z + h - .011, w, inset + .01, .022, role, 'reveals', 0)
    f.part('Reveal sill liner', u, d, z + .011, w, inset + .01, .022, role, 'reveals', 0)


def multilite(f, name, u, z, w, h, cols=3, rows=2, curtain=False):
    f.window(name, u, z, w, h, cols=cols, rows=rows, frame='trim', depth=T, sill=False, curtain=curtain)
    reveal(f, u, z, w, h)
    f.part('Steel sill angle', u, -.03, z - .03, w + .16, .20, .06, 'pale', 'window surrounds', 0)


def rollup(f, name, u, z, w, h):
    """Roll-up door: recessed ribbed leaf behind a steel guide frame; carrier is cut by the caller."""
    inset = .16
    for s in (-1, 1):
        f.part(name + ' guide', u + s * (w / 2 - .04), inset, z + h / 2, .08, .12, h, 'pale', 'roll-up doors', 0)
    f.part(name + ' hood', u, inset - .02, z + h - .17, w, .34, .34, 'pale', 'roll-up doors', 0)
    f.part(name + ' leaf', u, inset + .04, z + (h - .34) / 2, w - .16, .05, h - .34, 'pale', 'roll-up doors', 0)
    for k in range(1, 5):
        f.part(name + ' slat seam', u, inset + .012, z + k * (h - .34) / 5, w - .18, .012, .012, 'joint', 'roll-up doors', 0)
    reveal(f, u, z, w, h, inset=inset, role='pale')
    C.OPENINGS.append(dict(id=name, face=f.label, u=u, z=z, width=w, height=h, kind='roll-up door', clear_wall_cut=True,
        carrier_depth_m=T, frame_inset_m=inset, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n),
        occupied_space='enclosed workspace beyond door'))


def corrugation(f, lo, hi, z0, z1, holes, spacing=.30):
    """Recessed vertical seams of the corrugated cladding, batched in one mesh per elevation."""
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


def column(f, u, z0, z1, proud=.14, w=.36):
    f.part('Galvanised portal column', u, -proud / 2 + EPS, (z0 + z1) / 2, w, proud, z1 - z0, 'pale', 'portal frame', 0)


def girt(f, u0, u1, z, proud=.10, h=.30):
    f.part('Galvanised frame girt', (u0 + u1) / 2, -proud / 2 + EPS, z, (u1 - u0) - .36, proud, h, 'pale', 'portal frame', 0)


def brace(f, u0, u1, z0, z1, both=True):
    a, b = f.p(u0 + .20, -.07, z0 + .18), f.p(u1 - .20, -.07, z1 - .18)
    C.beam('Portal X-brace', a, b, .06, .06, 'pale', 'portal frame')
    if both:
        C.beam('Portal X-brace', f.p(u0 + .20, -.07, z1 - .18), f.p(u1 - .20, -.07, z0 + .18), .06, .06, 'pale', 'portal frame')


def south(f):
    """Street-side office box: six portal bays, ground openings, dock and entrance canopies."""
    b = BAYS
    gh = [hole('Bay 1 studio window', b[0] + 3.5, .95, 5.0, 2.9, cols=4),
          hole('Bay 2 roll-up door', b[1] + 3.5, G0, 4.2, 3.8),
          hole('Bay 3 staff door', b[2] + 1.9, G0, 1.05, 2.25), hole('Bay 3 window', b[2] + 5.0, 1.30, 1.6, 1.5, cols=2),
          hole('Bay 4 dock door', b[3] + 3.5, DOCK_H + .02, 3.2, 3.0), hole('Bay 5 dock door', b[4] + 3.5, DOCK_H + .02, 3.2, 3.0),
          hole('Bay 6 dock window', b[5] + 3.5, 2.2, 2.4, 1.5, cols=2)]
    f.wall('South box carrier', WEST_X, EAST_X, G0, EAVE, depth=T, holes=gh)
    corrugation(f, WEST_X, EAST_X, G0, EAVE, gh)
    multilite(f, gh[0]['id'], gh[0]['u'], gh[0]['z'], gh[0]['w'], gh[0]['h'], cols=4, rows=2, curtain=True)
    rollup(f, gh[1]['id'], gh[1]['u'], gh[1]['z'], gh[1]['w'], gh[1]['h'])
    f.door(gh[2]['id'], gh[2]['u'], gh[2]['z'], gh[2]['w'], gh[2]['h'], role='trim', panels=1)
    reveal(f, gh[2]['u'], gh[2]['z'], gh[2]['w'], gh[2]['h'], inset=.19)
    multilite(f, gh[3]['id'], gh[3]['u'], gh[3]['z'], gh[3]['w'], gh[3]['h'], cols=2, rows=1)
    rollup(f, gh[4]['id'], gh[4]['u'], gh[4]['z'], gh[4]['w'], gh[4]['h'])
    rollup(f, gh[5]['id'], gh[5]['u'], gh[5]['z'], gh[5]['w'], gh[5]['h'])
    multilite(f, gh[6]['id'], gh[6]['u'], gh[6]['z'], gh[6]['w'], gh[6]['h'], cols=2, rows=1)
    for u in b[1:-1]:
        column(f, u, 0, EAVE + .25)
    for x, y in ((WEST_X, FRONT_Y), (EAST_X, FRONT_Y)):
        sx = 1 if x < 0 else -1
        C.box('Galvanised corner column', (x - sx * .07, y - .07, (EAVE + .25) / 2), (.50, .50, EAVE + .25), 'pale', 'portal frame', 0)
    for i in range(6):
        girt(f, b[i], b[i + 1], U - .05)
        girt(f, b[i], b[i + 1], EAVE + .10)
    brace(f, b[0], b[1], U + .12, EAVE - .08)                 # corner bay: full-height X
    brace(f, b[5], b[6], CANOPY_Z + .75, EAVE - .08)          # east-end bay: X above the dock canopy
    plinth(f, WEST_X, EAST_X, gh)
    dock(f)


def dock(f):
    """Cantilevered dock canopy over bays 2-6, raised dock with ramp and steps."""
    u0, u1 = BAYS[1], EAST_X
    f.part('Dock canopy slab', (u0 + u1) / 2, -CANOPY_OUT / 2, CANOPY_Z + .06, u1 - u0, CANOPY_OUT, .12, 'trim', 'dock canopy', 0)
    f.part('Dock canopy fascia', (u0 + u1) / 2, -CANOPY_OUT + .03, CANOPY_Z + .20, u1 - u0, .06, .36, 'trim', 'dock canopy', 0)
    for u in BAYS[1:]:
        uu = min(u, EAST_X - .40)
        C.beam('Canopy tie rod', f.p(uu, -.07, CANOPY_Z + 2.0), f.p(uu, -CANOPY_OUT + .30, CANOPY_Z + .14), .05, .05, 'pale', 'dock canopy')
    # Raised dock from bay 3 to bay 6 with a ramp rising eastward across bay 2 and steps at the east end.
    d0, d1 = BAYS[2], EAST_X - 1.6
    f.part('Dock platform', (d0 + d1) / 2, -DOCK_OUT / 2 - .004, DOCK_H / 2, d1 - d0, DOCK_OUT, DOCK_H, 'stone', 'loading dock', 0)
    f.part('Dock edge bumper', (d0 + d1) / 2, -DOCK_OUT - .04, DOCK_H - .10, d1 - d0, .08, .16, 'trim', 'loading dock', 0)
    ramp_len = BAYS[2] - BAYS[1]
    x0 = BAYS[1]
    C.prism('Dock ramp', [(x0, 0), (x0 + ramp_len, DOCK_H), (x0 + ramp_len, 0)], 'y', FRONT_Y - DOCK_OUT, FRONT_Y - .004, 'stone', 'loading dock')
    C.railing('Ramp guard rail', (x0 + .3, FRONT_Y - DOCK_OUT + .10, DOCK_H * .3 / ramp_len), (x0 + ramp_len, FRONT_Y - DOCK_OUT + .10, DOCK_H), height=1.0, spacing=.25, role='hardware')
    C.railing('Dock guard rail', (d0, FRONT_Y - DOCK_OUT + .10, DOCK_H), (d0 + 1.6, FRONT_Y - DOCK_OUT + .10, DOCK_H), height=1.0, spacing=.25, role='hardware')
    for i in range(4):
        h = DOCK_H * (4 - i) / 4
        C.box('Dock step', (d1 + .20 + i * .30, FRONT_Y - DOCK_OUT / 2, h / 2), (.30, DOCK_OUT, h), 'stone', 'loading dock', 0)
    C.railing('Dock step rail', (d1, FRONT_Y - DOCK_OUT + .10, DOCK_H), (d1 + 1.3, FRONT_Y - DOCK_OUT + .10, DOCK_H * .1), height=1.0, spacing=.25, role='hardware')
    for i in range(4):
        h = DOCK_H * (4 - i) / 4
        C.box('Dock front step', (d0 + 6.0, FRONT_Y - DOCK_OUT - .15 - i * .30, h / 2), (1.2, .30, h), 'stone', 'loading dock', 0)
    C.CONTACTS.append(dict(name='Dock ramp from apron grade to dock level', grade_m=0, rise_m=DOCK_H, run_m=ramp_len))
    C.CONTACTS.append(dict(name='Dock steps at the east end', steps=4, grade_m=0))


def gable_end(f, entrance):
    """West (entrance=True) or east gable end: box portion south, shed portion north, zigzag crown."""
    def uu(y):                          # u grows toward the south on the west face, toward the north on the east face
        return -y if entrance else y
    holes = []
    if entrance:
        holes.append(hole('Corner entrance storefront', uu(-12.9), G0, 3.4, 3.3, cols=3, rows=2, kind='storefront'))
        holes.append(hole('Box upper window', uu(-12.9), U + .85, 3.4, 2.3, cols=3))
        holes.append(hole('Corner bay ground window', uu(-8.7), 1.1, 2.6, 2.2, cols=3))
    else:
        holes.append(hole('East staff door', uu(-11.5), G0, 1.05, 2.25, kind='door'))
        holes.append(hole('East box ground window', uu(-8.6), 1.1, 2.6, 2.2, cols=3))
        holes.append(hole('East box upper window', uu(-11.0), U + .85, 3.4, 2.0, cols=3))
    # Shed windows under the second and third teeth, ground and upper, as read from the front view.
    for k in (1, 2):
        yc = TEETH_Y[k] + TOOTH / 2
        holes.append(hole(f'Shed ground window {k}', uu(yc), 1.2, 2.4, 2.0, cols=3))
        holes.append(hole(f'Shed upper window {k}', uu(yc), 5.3, 2.4, 1.8, cols=3))
    if entrance:
        holes.append(hole('Shed ground window 0', uu(TEETH_Y[0] + TOOTH / 2), 1.2, 2.4, 2.0, cols=3))
        holes.append(hole('Shed upper window 0', uu(TEETH_Y[0] + TOOTH / 2), 5.3, 2.4, 1.8, cols=3))
    u0, u1 = -D / 2 + T, D / 2 - T
    f.wall(f.label + ' gable carrier', u0, u1, G0, EAVE, depth=T, holes=holes)
    corrugation(f, u0, u1, G0, EAVE, holes)
    for h in holes:
        if h.get('kind') == 'door':
            f.door(h['id'], h['u'], h['z'], h['w'], h['h'], role='trim', panels=1); reveal(f, h['u'], h['z'], h['w'], h['h'], inset=.19)
            f.part('Door step', h['u'], -.17, G0 / 2, 1.4, .34, G0, 'stone', 'entry steps', 0)
        elif h.get('kind') == 'storefront':
            f.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=4, rows=2, frame='trim', depth=T, sill=False, kind='glazed door')
            reveal(f, h['u'], h['z'], h['w'], h['h'])
            for du in (-.12, .12):
                C.rod('Entrance door pull', f.p(h['u'] + du, .01, h['z'] + .9), f.p(h['u'] + du, .01, h['z'] + 1.5), .018, 'hardware', 'door hardware')
            f.part('Entrance threshold', h['u'], .04, G0 - .005, h['w'] + .2, .40, .03, 'stone', 'entrance', 0)
        else:
            multilite(f, h['id'], h['u'], h['z'], h['w'], h['h'], cols=h.get('cols', 3), rows=2 if h['h'] > 2.1 else 1, curtain=h['id'].startswith('Box upper'))
    # Galvanised columns at the box corner line and at every tooth valley; girts on the box portion.
    for y in [BOX_N] + TEETH_Y[1:] + ([-10.8] if entrance else []):
        column(f, uu(y), 0, EAVE + .25)
    girt(f, min(uu(FRONT_Y), uu(BOX_N)), max(uu(FRONT_Y), uu(BOX_N)), U - .05)
    girt(f, min(uu(FRONT_Y), uu(BOX_N)), max(uu(FRONT_Y), uu(BOX_N)), EAVE + .10)
    if entrance:
        brace(f, uu(-6.6), uu(-10.8), U + .12, EAVE - .08)     # corner bay X-brace over the corner window
    plinth(f, u0, u1, holes)
    if not entrance:
        access_ladder(f, uu(-9.5))
    # Sawtooth gable crowns: one trapezoid per tooth, bearing on the carrier top.
    for k in range(4):
        y_hi, y_lo = TEETH_Y[k], TEETH_Y[k] + TOOTH
        poly = [(uu(y_hi), EAVE), (uu(y_lo), EAVE), (uu(y_hi), TOP[k])]
        if not entrance:
            poly = [(uu(y_hi), EAVE), (uu(y_hi), TOP[k]), (uu(y_lo), EAVE)]
        f.panel(f'Gable crown tooth {k}', poly, 0, T, 'wall', 'gable crowns')
    if entrance:
        entrance_canopy_west(f)


def plinth(f, lo, hi, holes):
    """Concrete plinth band at grade, interrupted at every ground opening; less proud than the columns."""
    for a, b in subtract_openings(lo + .05, hi - .05, 0, .60, [h for h in holes if h['z'] < .60]):
        if b - a > .10:
            f.part('Concrete plinth', (a + b) / 2, -.02, .30, b - a, .20, .60, 'stone', 'plinth', 0)


def access_ladder(f, u):
    for du in (-.22, .22):
        C.rod('Terrace access ladder stile', f.p(u + du, -.22, 1.8), f.p(u + du, -.22, EAVE + 1.0), .022, 'pale', 'access ladder', 8)
    for i in range(int((EAVE + 1.0 - 2.0) / .45) + 1):
        z = 2.0 + i * .45
        C.rod('Ladder rung', f.p(u - .22, -.22, z), f.p(u + .22, -.22, z), .014, 'pale', 'access ladder', 8)
    for z in (3.0, 5.0, 7.0, EAVE + .6):
        C.beam('Ladder wall bracket', f.p(u, -.02, z), f.p(u, -.22, z), .03, .03, 'pale', 'access ladder')


def entrance_canopy_west(f):
    """Thin steel canopy over the entrance bay only, dying into the corner column."""
    u0, u1 = 10.8 + .18, -FRONT_Y - .36
    f.part('Entrance canopy slab', (u0 + u1) / 2, -.80, 3.55, u1 - u0, 1.60, .10, 'trim', 'entrance canopy', 0)
    f.part('Entrance canopy fascia', (u0 + u1) / 2, -1.58, 3.68, u1 - u0, .04, .32, 'trim', 'entrance canopy', 0)
    f.part('Sign board', (u0 + u1) / 2, -1.605, 3.68, 2.6, .02, .24, 'pale', 'entrance canopy', 0)
    for uu in (u0 + .3, u1 - .3):
        C.beam('Canopy hanger rod', f.p(uu, -.05, 5.6), f.p(uu, -1.45, 3.62), .035, .035, 'pale', 'entrance canopy')


def north(f):
    holes = [hole(f'Rear upper window {i}', u, 5.3, 2.4, 1.8, cols=3) for i, u in enumerate((-15.0, -5.0, 5.0, 15.0))]
    holes += [hole('Rear ground window 0', -12.0, 1.2, 2.4, 2.0, cols=3), hole('Rear ground window 1', 10.0, 1.2, 2.4, 2.0, cols=3),
              hole('Rear service door', 3.5, G0, 1.05, 2.25, kind='door')]
    f.wall('North shed carrier', WEST_X, EAST_X, G0, EAVE, depth=T, holes=holes)
    corrugation(f, WEST_X, EAST_X, G0, EAVE, holes)
    for h in holes:
        if h.get('kind') == 'door':
            f.door(h['id'], h['u'], h['z'], h['w'], h['h'], role='trim', panels=1); reveal(f, h['u'], h['z'], h['w'], h['h'], inset=.19)
            f.part('Door step', h['u'], -.17, G0 / 2, 1.4, .34, G0, 'stone', 'entry steps', 0)
        else:
            multilite(f, h['id'], h['u'], h['z'], h['w'], h['h'], cols=3, rows=1)
    for u in (-14.0, -7.0, 0.0, 7.0, 14.0):
        column(f, -u, 0, EAVE)
    plinth(f, WEST_X, EAST_X, holes)
    f.part('Eave gutter', 0, -.11, EAVE + .07, L, .22, .18, 'pale', 'gutters', 0)


def roofs():
    x0, x1 = WEST_X + T, EAST_X - T
    for k in range(4):
        y_hi, y_lo = TEETH_Y[k], TEETH_Y[k] + TOOTH
        top = TOP[k]
        y_end = y_lo - T if k == 3 else y_lo          # the last plate stops inside the north wall under its fascia
        # Sloped corrugated monitor roof: thick plate from the clerestory crown down to the north eave.
        z_end = top - (top - EAVE - .02) * (y_end - y_hi) / TOOTH
        C.prism(f'Tooth {k} monitor roof', [(y_hi, top), (y_end, z_end), (y_end, z_end - .24), (y_hi, top - .24)], 'x', x0, x1, 'roof', 'sawtooth roofs')
        for xx in range(int(x0) + 1, int(x1), 3):
            C.beam('Roof corrugation rib', (xx, y_hi, top + .006), (xx, y_end, z_end + .006), .02, .012, 'joint', 'sawtooth roofs')
        # Clerestory band on the south edge of the tooth: frame, mullions and panes above the lower eave.
        clerestory(k, y_hi, EAVE, top - .24, x0, x1)
        if k:
            C.box(f'Tooth {k - 1} eave gutter', (0, y_hi - .13, EAVE - .32), (L - 2 * T, .26, .16), 'pale', 'gutters', 0)
    C.box('North eave fascia', (0, REAR_Y - T / 2, EAVE + .10), (L - 2 * T, T, .20), 'pale', 'gutters', 0)
    # Office box roof: membrane terrace with a perimeter rail, rooftop unit and ducts.
    ry0, ry1 = FRONT_Y + T, BOX_N + .28
    C.box('Box roof slab', (0, (ry0 + ry1) / 2, EAVE - .12), (L - 2 * T, ry1 - ry0, .24), 'floor', 'roof', 0)
    C.box('Terrace membrane', (0, (ry0 + BOX_N - .01) / 2, EAVE + .004), (L - 2 * T - .02, BOX_N - .01 - ry0, .008), 'membrane', 'roof', 0)
    for xx in range(-18, 19, 4):
        C.box('Membrane seam', (xx, (ry0 + BOX_N) / 2, EAVE + .010), (.015, BOX_N - ry0 - .1, .004), 'joint', 'roof', 0)
    rail_y = FRONT_Y + .30
    terrace_rail('Terrace south rail', (WEST_X + .30, rail_y, EAVE + .008), (EAST_X - .30, rail_y, EAVE + .008))
    terrace_rail('Terrace west rail', (WEST_X + .30, rail_y, EAVE + .008), (WEST_X + .30, BOX_N - .30, EAVE + .008))
    terrace_rail('Terrace east rail', (EAST_X - .30, rail_y, EAVE + .008), (EAST_X - .30, BOX_N - .30, EAVE + .008))
    ux, uy = -15.5, FRONT_Y + 3.6
    C.box('Rooftop unit plinth', (ux, uy, EAVE + .15), (3.2, 2.4, .30), 'pale', 'rooftop plant', 0)
    C.box('Packaged rooftop unit', (ux, uy, EAVE + .30 + 1.05), (3.0, 2.2, 2.1), 'pale', 'rooftop plant', 0)
    C.rod('Rooftop unit fan cowl', (ux - .6, uy, EAVE + 2.40), (ux - .6, uy, EAVE + 2.62), .55, 'hardware', 'rooftop plant', 16)
    for i in range(3):
        C.box('Rooftop unit louvre', (ux + 1.505, uy, EAVE + 1.0 + i * .45), (.01, 1.6, .18), 'hardware', 'rooftop plant', 0)
    C.rod('Supply duct', (ux + 1.5, uy + .5, EAVE + 1.4), (ux + 4.0, uy + .5, EAVE + 1.4), .32, 'pale', 'rooftop plant', 14)
    C.rod('Supply duct riser', (ux + 4.0, uy + .5, EAVE + 1.4), (ux + 4.0, uy + .5, EAVE + .30), .32, 'pale', 'rooftop plant', 14)
    dx = WEST_X + T + 2 * (L - 2 * T) / 10   # second clerestory mullion line
    C.rod('Return duct', (ux + 1.5, uy - .5, EAVE + 1.9), (dx, uy - .5, EAVE + 1.9), .28, 'pale', 'rooftop plant', 14)
    C.rod('Return duct elbow', (dx, uy - .5, EAVE + 1.9), (dx, BOX_N - .3, EAVE + 1.9), .28, 'pale', 'rooftop plant', 14)
    C.box('Duct wall penetration collar', (dx, BOX_N - .11, EAVE + 1.9), (.50, .20, .50), 'trim', 'rooftop plant', 0)


def desk(x, y, z):
    """Lean office desk: top, two leg panels, monitor, task chair."""
    C.box('Desk top', (x, y, z + .74), (1.8, .8, .05), 'timber', 'office furniture', 0)
    for dx in (-.8, .8):
        C.box('Desk leg panel', (x + dx, y, z + .36), (.05, .7, .72), 'trim', 'office furniture', 0)
    C.box('Monitor', (x, y + .2, z + 1.05), (.6, .05, .36), 'trim', 'office furniture', 0)
    C.box('Chair seat', (x, y - .85, z + .46), (.48, .48, .10), 'blue', 'office furniture', 0)
    C.box('Chair back', (x, y - 1.05, z + .78), (.48, .07, .5), 'blue', 'office furniture', 0)


def terrace_rail(name, a, b, height=1.10):
    """Industrial guard rail: vertical bars at 400 mm between posts seated on base plates every 2.4 m."""
    C.railing(name, a, b, height=height, spacing=.40, role='hardware', end_posts=False)
    count = max(1, math.ceil(math.dist(a, b) / 2.4))
    for i in range(count + 1):
        x, y, z = (a[j] + (b[j] - a[j]) * i / count for j in range(3))
        C.box(name + ' base plate', (x, y, z + .01), (.14, .14, .02), 'hardware', 'rail posts', 0)
        C.beam(name + ' post', (x, y, z + .02), (x, y, z + height + .02), .045, .045, 'hardware', 'rail posts')


def clerestory(k, y, z0, z1, x0, x1):
    """South-facing glazed band between the lower eave and the monitor crown: carrier-free curtain band."""
    h = z1 - z0
    C.box(f'Tooth {k} clerestory sill', (0, y + .14, z0 + .08), (x1 - x0, .28, .16), 'trim', f'clerestory {k}', 0)
    C.box(f'Tooth {k} clerestory head', (0, y + .14, z1 - .06), (x1 - x0, .28, .12), 'trim', f'clerestory {k}', 0)
    n = 10
    w = (x1 - x0) / n
    for i in range(n + 1):
        xx = x0 + i * w
        C.box(f'Tooth {k} clerestory mullion', (xx, y + .14, (z0 + z1) / 2), (.08 if i in (0, n) else .06, .20, h - .28), 'trim', f'clerestory {k}', 0)
    for i in range(n):
        C.box(f'Tooth {k} clerestory pane', (x0 + (i + .5) * w, y + .17, (z0 + z1) / 2), (w - .07, .01, h - .30), 'glass', f'clerestory {k}', 0)
    C.box(f'Tooth {k} clerestory transom', (0, y + .12, (z0 + z1) / 2), (x1 - x0, .16, .05), 'trim', f'clerestory {k}', 0)


def floors():
    C.box('Ground slab', (0, 0, G0 / 2), (L, D, G0), 'foundation', 'foundation', 0)
    C.box('South apron paving', (0, FRONT_Y - APRON / 2, .0075), (L + 4.0, APRON, .015), 'foundation', 'apron paving', 0)
    C.box('West sidewalk', (WEST_X - 2.0, 0, .0075), (4.0, D, .015), 'foundation', 'apron paving', 0)
    C.box('Sidewalk kerb', (WEST_X - 3.95, -APRON / 2, .06), (.12, D + APRON, .12), 'stone', 'apron paving', 0)
    fy0, fy1 = FRONT_Y + T, BOX_N - .20
    upper = C.box('Box upper floor', (0, (fy0 + fy1) / 2, U - .075), (L - 2 * T, fy1 - fy0, .15), 'floor', 'occupied floors', 0)
    y_end = FRONT_Y + .45 + 4.6
    C.cut_box(upper, 'Upper stair aperture', (-13.0, y_end - 1.9, U), (1.3, 3.6, .6))
    A.seated_guard('Upper stair guard', (-12.3, y_end - 3.7, U), (-12.3, y_end - .1, U), spacing=.25)
    A.seated_guard('Upper stair end guard', (-12.3, y_end - .1, U), (-13.7, y_end - .1, U), spacing=.25)
    G.stair('Ground to upper stair', -13.0, FRONT_Y + .45, G0, U, length=4.6, width=1.1, landing_gap=.12)
    # Box north wall (internal, between the shed and the office box) with wide openings.
    f = C.Face((0, BOX_N, 0), (1, 0, 0), (0, -1, 0), 'box internal')
    holes = [hole('Shed link opening ground', -8.0, G0, 3.0, 2.8), hole('Shed link opening ground 2', 8.0, G0, 3.0, 2.8),
             hole('Shed link opening upper', 0.0, U, 2.4, 2.3)]
    f.wall('Box internal carrier', WEST_X + T, EAST_X - T, G0, EAVE - .24, depth=.20, holes=holes)
    for h in holes:
        reveal(f, h['u'], h['z'], h['w'], h['h'], inset=.10, role='pale')
    # Shed interior columns at the tooth valleys, read through the clerestories.
    for xx in (-14.0, -7.0, 0.0, 7.0, 14.0):
        for y in TEETH_Y[1:]:
            C.box('Shed interior column', (xx, y, (G0 + EAVE) / 2), (.30, .30, EAVE - G0), 'pale', 'interior structure', 0)


def programme():
    for xx in (-17.5, -10.5):
        desk(xx, FRONT_Y + 4.2, G0); desk(xx, FRONT_Y + 2.4, G0)
    C.qa_room_light('Reception', (-17.5, FRONT_Y + 3.5, U - .3), 70, 3.0)
    C.qa_room_light('Ground office', (-9.5, FRONT_Y + 3.5, U - .3), 60, 3.0)
    for xx in (-16.0, -9.0, -2.0):
        desk(xx, FRONT_Y + 4.4, U)
        C.qa_room_light('Upper office', (xx, FRONT_Y + 3.6, EAVE - .4), 70, 3.0)
    C.qa_room_light('Upper office east', (10.0, FRONT_Y + 3.6, EAVE - .4), 60, 3.0)
    desk(12.0, FRONT_Y + 3.6, U); A.sofa(6.0, FRONT_Y + 4.4, U)
    C.box('Dock storage racking', (10.0, FRONT_Y + 1.6, G0 + 1.2), (8.0, .9, 2.4), 'pale', 'ground office', 0)
    for i, xx in enumerate((-16.0, -2.0, 12.0)):
        for yy in (-3.0, 7.0):
            desk(xx + (i % 2) * 1.5, yy, G0)
    for xx in (-14.0, 0.0, 14.0):
        for yy in (-3.0, 3.0, 9.0):
            C.qa_room_light('Shed studio', (xx, yy, EAVE - 1.0), 110, 4.0)
    A.small_tree(WEST_X - 2.6, -3.0, .015, height=5.5, spread=1.2)


def build():
    floors()
    f_front, f_right, f_rear, f_left = A.faces(L, D)
    south(f_front)
    gable_end(f_left, True)
    gable_end(f_right, False)
    north(f_rear)
    roofs()
    programme()
    C.CONTACTS.append(dict(name='Corner entrance threshold at slab level under the wrap-around canopy', grade_m=0, step_m=G0))
    C.CONTACTS.append(dict(name='Tooth roofs bear on the gable crowns and clerestory frames; lower eaves carry gutters', eave_m=EAVE))


# Neutral review rig scaled to the 42 m shed: the pilot's rig at 2.4x the distance needs ~6x the power.
LIGHT_RIG = dict(key=(-38, -50, 44), fill=(46, -22, 38), rear=(-20, 52, 42), target=(0, -3, 6.0), gain=7.0)
