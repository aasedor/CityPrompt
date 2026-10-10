"""Three-unit Queen Anne bay-window rowhouse, authored from the locked catalogue views of
brick_rowhouse_terrace / variant_2 (queen_anne_bay_window_terrace).

Source conflict recorded, not averaged: the locked views show a continuing terrace. The
brief asks for a discrete three-unit building with individual grade entrances, so the
three east-end units are authored as one building: the east wall is the exposed end of
the row as in the source, the west wall is a blank party wall with its chimney, and the
contract records that the row continues westward in the source.

Read from the pixels: 2.5-storey red-brown brick with cream stone bands and window
surrounds; each unit has its own front door up a short stoop; the end units carry a
canted ground-floor bay window under a slate hip cap and a steep front gable with
decorative bargeboards, green timber infill and a finial; the middle unit has a small
gabled dormer; a slate main roof with chimney stacks at the party lines; rear cross
gables over rear wings; iron fences on a low wall, hedged front gardens and paths.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G
from contract import subtract_openings

SLUG = 'clay-queen-anne-rowhouse-trio'
UW = 5.8                          # unit width
W, D = 3 * UW, 11.0
T = .28
G0, U, EAVE = .15, 3.40, 6.60
RIDGE = 11.2
PITCH = (RIDGE - EAVE) / (D / 2)  # main roof rise per metre of run
FRONT_Y, REAR_Y, WEST_X, EAST_X = -D / 2, D / 2, -W / 2, W / 2
GARDEN, YARD = 4.2, 6.0
UNITS = [('A', EAST_X - UW / 2, 'bay_east'), ('B', 0.0, 'middle'), ('C', WEST_X + UW / 2, 'bay_west')]
EPS = .002
PALETTE = dict(wall=(.36, .14, .09), joint=(.24, .10, .06), trim=(.30, .20, .10),
    pale=(.76, .70, .56), stone=(.42, .40, .36), roof=(.15, .16, .19), sand=(.62, .56, .44),
    foundation=(.40, .40, .39), glass=(.50, .55, .54), hardware=(.07, .07, .075),
    interior=(.74, .70, .60), floor=(.42, .40, .36), timber=(.40, .28, .16), blue=(.14, .22, .28),
    planting=(.22, .40, .14), soil=(.19, .14, .08), green=(.14, .28, .17), door_green=(.16, .30, .20),
    door_brown=(.36, .14, .10), lead=(.45, .47, .50))


def manifest(version):
    h = RIDGE + 1.2
    cams = G.camera_roster(W, D + GARDEN + YARD, h, [
        ('facade_close', (3.0, -17.0, 3.2), (4.5, FRONT_Y, 3.0), 45),
        ('architecture_close', (-2.0, -13.0, 8.5), (3.0, FRONT_Y, 9.0), 50),
        ('glass_close', (5.0, -11.5, 2.4), (6.6, FRONT_Y - 1.0, 2.0), 50),
        ('entrance_steps', (-1.5, -12.5, 1.6), (0.8, FRONT_Y, 1.2), 40),
        ('bay_window', (10.0, -12.0, 2.2), (6.9, FRONT_Y - .5, 1.9), 40),
        ('gable_close', (9.0, -14.0, 9.5), (5.8, FRONT_Y, 9.6), 45),
        ('roof_contact', (-9.0, -14.0, 13.0), (-4.0, -2.0, 10.0), 45),
        ('rear_yards', (6.0, 20.0, 6.0), (0.0, REAR_Y, 3.5), 40),
        ('interior', (6.6, -13.0, 1.9), (6.6, -2.0, 1.6), 30),
        ('party_wall', (-18.0, -8.0, 5.0), (WEST_X, 0.0, 5.0), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='brick_rowhouse_terrace/variant_2 (queen_anne_bay_window_terrace)',
        measurement_contract=dict(dimensions_m=dict(width=W, depth=D + GARDEN + YARD, height=h),
            observed_storeys=2.5, storey_programme='ground, first floor and gable attic rooms; fixed authored assembly',
            units=3, unit_width_m=UW, unit_pattern='end unit A: bay window right, door left, front gable; middle unit B: door, window, small dormer; unit C: door right, bay window left, front gable',
            levels_m=[G0, U], eave_m=EAVE, ridge_m=RIDGE, main_pitch_deg=round(math.degrees(math.atan(PITCH)), 1),
            front='cream stone string courses at first-floor sill and head; stone lintels and sills; stoops of three steps with iron handrails; low wall and iron fence; hedged gardens',
            roof='slate main roof with front cross gables over the end units, a small dormer over the middle unit, rear cross gables over rear wings, chimney stacks at the party lines and both ends',
            source_conflict='the locked views show the terrace continuing west; three east-end units are authored as one discrete building with a blank west party wall',
            inferred='5.8 m unit width calibrates the bay-door rhythm; depth 11 m and rear wings from the top view; interiors are teaching assumptions.'),
        roof_contract=dict(type='pitched slate main roof with cross gables front and rear, hip cap over each bay, chimney stacks', datum_m=EAVE, crowns_m=[RIDGE, RIDGE + 1.0]),
        identity_contract=dict(owner='steep bargeboard gables with green timber infill and finials over canted bay windows, cream banded red brick, three individual stooped entrances, iron fence'),
        material_contract=dict(profile='source-palette clay: red-brown brick with recessed courses and cream stone bands, cream surrounds, dark green painted timber, green and brown doors, dark slate, black iron', textured_keeper=False),
        programme_contract=dict(storeys=3, ground='hall, front room in the bay, kitchen in the rear wing per unit', upper='two bedrooms per unit', attic='gable room per end unit', stairs='straight supported flight against each party wall'),
        contact_contract=['Grade-zero slab and paths', 'Stoop of three solid steps per door', 'Bay windows seated on the plinth with hip caps', 'Gables bear on the front carrier; bargeboards follow the rakes', 'Chimneys penetrate the ridge', 'Fence on a low wall at the garden line'],
        runtime_contract=dict(scale='fixed_native_only', installation='not installed', review='NOT TESTED'),
        camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])


def hole(name, u, z, w, h, **kw):
    return dict(id=name, u=u, z=z, w=w, h=h, **kw)


def reveal(f, u, z, w, h, inset=.14, role='sand'):
    d = inset / 2 + .005
    for s in (-1, 1):
        f.part('Reveal jamb liner', u + s * (w / 2 - .011), d, z + h / 2, .022, inset + .01, h, role, 'reveals', 0)
    f.part('Reveal head liner', u, d, z + h - .011, w, inset + .01, .022, role, 'reveals', 0)
    f.part('Reveal sill liner', u, d, z + .011, w, inset + .01, .022, role, 'reveals', 0)


def sash(f, name, u, z, w, h, curtain=False, arched=False):
    f.window(name, u, z, w, h, cols=1, rows=2, frame='trim', depth=T, sill=False, curtain=curtain)
    reveal(f, u, z, w, h)
    f.part('Stone sill', u, -.06, z - .05, w + .30, .36, .10, 'pale', 'window surrounds', 0)
    f.part('Stone lintel', u, -.04, z + h + .09, w + .36, .32, .18, 'pale', 'window surrounds', 0)
    if arched:
        f.part('Arch keystone', u, -.08, z + h + .22, .22, .40, .34, 'pale', 'window surrounds', 0)


def door(f, name, u, z, w, h, role):
    f.door(name, u, z, w, h, role=role, panels=4, panel_cols=1)
    reveal(f, u, z, w, h, inset=.19)
    f.part('Door transom light', u, .20, z + h - .36, w - .10, .02, .32, 'glass', 'entrance', 0)
    f.part('Transom bar', u, .19, z + h - .54, w, .06, .05, 'trim', 'entrance', 0)
    f.part('Stone door lintel', u, -.04, z + h + .09, w + .36, .32, .18, 'pale', 'window surrounds', 0)


def band(f, u0, u1, z, h=.14, d=-.03, t=.34):
    f.part('Cream string course', (u0 + u1) / 2, d, z, (u1 - u0) - 2 * EPS, t, h, 'pale', 'string courses', 0)


def stoop(x, y_wall, role='stone'):
    """Three solid stone steps up to the door threshold with iron handrails."""
    for i in range(3):
        depth = .32 * (i + 1)
        top = G0 + .20 + .20 * (2 - i)
        C.box('Stoop step', (x, y_wall - .32 * 3 + depth / 2 - .004, top / 2), (1.30, depth, top), role, 'stoop', 0)
    for s in (-1, 1):
        C.railing('Stoop handrail', (x + s * .6, y_wall - .96, .20), (x + s * .6, y_wall - .05, G0 + .60), height=.95, spacing=.20, role='hardware')
    C.CONTACTS.append(dict(name='Stoop of three solid steps to the door threshold', grade_m=0, risers=3, rise_m=.20))


def bay_window(xc, y_wall, z1=U - .25):
    """Canted ground-floor bay: three carriers with sash windows, brick courses, stone cap band and a slate hip cap."""
    half, out, side = 1.3, 1.0, .9
    pts = [(xc - half - side, y_wall), (xc - half, y_wall - out), (xc + half, y_wall - out), (xc + half + side, y_wall)]
    faces = []
    for i in range(3):
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        length = math.dist((ax, ay), (bx, by))
        tx, ty = (bx - ax) / length, (by - ay) / length
        nx, ny = -ty, tx    # inward (toward the house) for a path running west-to-east along the front
        if ny < 0: nx, ny = -nx, -ny
        f = C.Face(((ax + bx) / 2, (ay + by) / 2, 0), (tx, ty, 0), (nx, ny, 0), f'bay {xc:+.1f} face {i}')
        w = length - .36 if i == 1 else length - .30
        h = [hole(f'Bay window {xc:+.1f}-{i}', 0.0, .95, min(w - .5, 1.4 if i == 1 else .8), 1.9)]
        f.wall(f'Bay carrier {xc:+.1f}-{i}', -length / 2, length / 2, G0, z1, depth=T, holes=h)
        G.brick_courses(f, -length / 2 + .02, length / 2 - .02, G0, z1, h, spacing=.075)
        sash(f, h[0]['id'], 0.0, .95, h[0]['w'], 1.9, curtain=i == 1)
        f.part('Bay plinth band', 0.0, -.03, .45, length - .04, .34, .30, 'pale', 'string courses', 0)
        f.part('Bay head band', 0.0, -.04, z1 - .12, length - .04, .36, .22, 'pale', 'string courses', 0)
        faces.append(f)
    # Slate hip cap: ridge against the house wall, slopes falling to the three bay edges.
    z0, zt = z1, z1 + .75
    verts = [(pts[0][0], pts[0][1], z0), (pts[1][0], pts[1][1], z0), (pts[2][0], pts[2][1], z0), (pts[3][0], pts[3][1], z0),
             (xc - half - .2, y_wall - .02, zt), (xc + half + .2, y_wall - .02, zt)]
    tops = [(0, 1, 4), (1, 2, 5, 4), (2, 3, 5)]
    base = [(3, 2, 1, 0)]
    back = [(0, 4, 5, 3)]
    C.mesh(f'Bay hip cap {xc:+.1f}', verts, tops + base + back, 'roof', 'bay caps')
    C.box(f'Bay cap fascia {xc:+.1f}', (xc, y_wall - out + .05, z1 - .02), (2 * half + .10, .12, .16), 'green', 'bay caps', 0)


def front(f):
    """Street elevation: three units; bays at the ends, doors beside them, middle unit door and window."""
    holes = []
    for name, xc, kind in UNITS:
        if kind == 'bay_east':
            holes.append(hole(f'Unit {name} door', xc - 1.95, G0, .95, 2.35, kind='door', role='door_green'))
            holes.append(hole(f'Unit {name} bay opening', xc + .7, G0, 3.0, U - .25 - G0, kind='bay'))
        elif kind == 'bay_west':
            holes.append(hole(f'Unit {name} door', xc + 1.95, G0, .95, 2.35, kind='door', role='door_brown'))
            holes.append(hole(f'Unit {name} bay opening', xc - .7, G0, 3.0, U - .25 - G0, kind='bay'))
        else:
            holes.append(hole(f'Unit {name} door', xc - 1.6, G0, .95, 2.35, kind='door', role='door_brown'))
            holes.append(hole(f'Unit {name} ground window', xc + 1.2, .95, 1.1, 2.0))
        for s in (-1, 1):
            holes.append(hole(f'Unit {name} upper window {s}', xc + s * 1.3, U + .85, 1.0, 1.8))
    f.wall('Front carrier', WEST_X, EAST_X, G0, EAVE, depth=T, holes=holes)
    G.brick_courses(f, WEST_X + .02, EAST_X - .02, G0, EAVE, holes, spacing=.075)
    for h in holes:
        if h.get('kind') == 'door':
            door(f, h['id'], h['u'], h['z'], h['w'], h['h'], h['role'])
            x = f.p(h['u'], 0, 0)[0]
            stoop(x, FRONT_Y)
        elif h.get('kind') == 'bay':
            reveal(f, h['u'], h['z'], h['w'], h['h'], inset=T, role='wall')
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='bay opening', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='front room continuing into the bay'))
        else:
            sash(f, h['id'], h['u'], h['z'], h['w'], h['h'], curtain='upper' in h['id'])
    band(f, WEST_X, EAST_X, U + .60)
    band(f, WEST_X, EAST_X, U + .85 + 1.8 + .30)
    band(f, WEST_X, EAST_X, .45, h=.30)
    for name, xc, kind in UNITS:
        if kind != 'middle':
            x = f.p(xc + (.7 if kind == 'bay_east' else -.7), 0, 0)[0]
            bay_window(x, FRONT_Y)
    eaves_fascia(f)


def eaves_fascia(f):
    for name, xc, kind in UNITS:
        if kind == 'middle':
            f.part('Eaves fascia', xc, -.10, EAVE + .08, UW - .06, .20, .16, 'green', 'eaves', 0)
            f.part('Eaves gutter', xc, -.24, EAVE + .18, UW - .10, .14, .12, 'lead', 'eaves', 0)


def gable(xc, y_wall, width, apex, eave, face_dir=-1, infill=True, finial=True):
    """Front or rear cross gable: brick lower triangle, green timber infill above, bargeboards, finial."""
    s = face_dir
    hw = width / 2
    f = C.Face((xc, y_wall, 0), (1 if s < 0 else -1, 0, 0), (0, -s, 0), f'gable {xc:+.1f} {"front" if s < 0 else "rear"}')
    mid = eave + (apex - eave) * .45
    f.panel('Gable brick', [(-hw, eave - EPS), (hw, eave - EPS), (hw * (1 - .45) * 1.0, mid), (-hw * (1 - .45), mid)], 0, T, 'wall', 'gables')
    if infill:
        f.panel('Gable timber infill', [(-hw * .55, mid), (hw * .55, mid), (0, apex)], .02, T, 'green', 'gables')
        for k in range(-2, 3):
            uu = k * hw * .22
            zz = apex - (apex - mid) * abs(uu) / (hw * .55)
            f.part('Gable batten', uu, -.01, (mid + zz) / 2, .06, .05, zz - mid - .02, 'pale', 'gables', 0)
        f.window(f'Gable window {xc:+.1f}', 0.0, mid + .15, .8, 1.5, cols=1, rows=2, frame='trim', depth=.2, sill=False)
        reveal(f, 0.0, mid + .15, .8, 1.5, inset=.10, role='pale')
    else:
        f.panel('Gable brick upper', [(-hw * .55, mid), (hw * .55, mid), (0, apex)], 0, T, 'wall', 'gables')
    for side in (-1, 1):
        a = f.p(side * (hw + .25), -.22, eave - .15)
        b = f.p(0, -.22, apex + .22)
        C.beam('Bargeboard', a, b, .05, .30, 'pale', 'bargeboards')
        C.beam('Rake trim', f.p(side * (hw + .1), -.10, eave + .02), f.p(0, -.10, apex + .30), .04, .12, 'green', 'bargeboards')
    if finial:
        C.rod('Finial', (xc, y_wall - .22 * -s if False else y_wall + s * .22, apex + .22), (xc, y_wall + s * .22, apex + 1.2), .05, 'pale', 'bargeboards', 8)


def roofs():
    """Main slate roof planes, cross gables, dormer, chimneys."""
    x0, x1 = WEST_X, EAST_X
    t = .22
    # Front and rear planes of the main roof, thickened plates, meeting at the ridge.
    C.prism('Main roof front plane', [(FRONT_Y - .30, EAVE - .30 * PITCH), (0, RIDGE), (0, RIDGE - t), (FRONT_Y - .30, EAVE - .30 * PITCH - t)], 'x', x0, x1, 'roof', 'main roof')
    C.prism('Main roof rear plane', [(REAR_Y + .30, EAVE - .30 * PITCH), (0, RIDGE), (0, RIDGE - t), (REAR_Y + .30, EAVE - .30 * PITCH - t)], 'x', x0, x1, 'roof', 'main roof')
    C.beam('Ridge cap', (x0, 0, RIDGE + .04), (x1, 0, RIDGE + .04), .18, .10, 'lead', 'main roof')
    for name, xc, kind in UNITS:
        if kind != 'middle':
            # Front cross gable over the bay: ridge from the front wall back to the main ridge.
            gw = UW - .4
            gable(xc, FRONT_Y, gw, RIDGE, EAVE, face_dir=-1)
            C.prism(f'Cross gable roof {name}', [(xc - gw / 2 - .25, EAVE - .25 * (RIDGE - EAVE) / (gw / 2)), (xc, RIDGE + .02), (xc + gw / 2 + .25, EAVE - .25 * (RIDGE - EAVE) / (gw / 2)),
                                                 (xc + gw / 2 + .25, EAVE - .25 * (RIDGE - EAVE) / (gw / 2) - t), (xc, RIDGE + .02 - t), (xc - gw / 2 - .25, EAVE - .25 * (RIDGE - EAVE) / (gw / 2) - t)],
                    'y', FRONT_Y - .30, 0.0, 'roof', 'cross gables')
        else:
            # Small gabled dormer in the front plane.
            dw, apex = 2.2, EAVE + 3.0
            dy = FRONT_Y + 1.0
            C.box('Dormer cheek', (xc - dw / 2 + .08, dy + 1.0, EAVE + 1.4), (.16, 2.2, 2.6), 'wall', 'dormer', 0)
            C.box('Dormer cheek', (xc + dw / 2 - .08, dy + 1.0, EAVE + 1.4), (.16, 2.2, 2.6), 'wall', 'dormer', 0)
            gable(xc, dy, dw, apex, EAVE + .8, face_dir=-1, infill=True, finial=True)
            C.prism('Dormer roof', [(xc - dw / 2 - .2, EAVE + .8 - .2 * (apex - EAVE - .8) / (dw / 2)), (xc, apex + .02), (xc + dw / 2 + .2, EAVE + .8 - .2 * (apex - EAVE - .8) / (dw / 2)),
                                   (xc + dw / 2 + .2, EAVE + .8 - .2 * (apex - EAVE - .8) / (dw / 2) - t), (xc, apex + .02 - t), (xc - dw / 2 - .2, EAVE + .8 - .2 * (apex - EAVE - .8) / (dw / 2) - t)],
                    'y', dy - .25, dy + 2.4, 'roof', 'dormer')
        # Rear cross gable over the rear wing of every unit.
        rw, rapex = 3.4, EAVE + 2.6
        xr = xc + (1.0 if kind == 'bay_east' else -1.0 if kind == 'bay_west' else 0.0)
        gable(xr, REAR_Y, rw, rapex, EAVE, face_dir=1, infill=False, finial=False)
        C.prism(f'Rear gable roof {name}', [(xr - rw / 2 - .2, EAVE - .2 * (rapex - EAVE) / (rw / 2)), (xr, rapex + .02), (xr + rw / 2 + .2, EAVE - .2 * (rapex - EAVE) / (rw / 2)),
                                           (xr + rw / 2 + .2, EAVE - .2 * (rapex - EAVE) / (rw / 2) - t), (xr, rapex + .02 - t), (xr - rw / 2 - .2, EAVE - .2 * (rapex - EAVE) / (rw / 2) - t)],
                'y', REAR_Y - (rapex - EAVE) / PITCH, REAR_Y + .30, 'roof', 'cross gables')
    # Chimney stacks at the party lines and both ends, astride the ridge.
    for x in (WEST_X + .35, -UW / 2, UW / 2, EAST_X - .35):
        C.box('Chimney stack', (x, 0, RIDGE - .6 + 1.2), (.70, 1.10, 2.4), 'wall', 'chimneys', 0)
        C.box('Chimney cap', (x, 0, RIDGE + 1.85), (.82, 1.22, .10), 'pale', 'chimneys', 0)
        for dy in (-.28, .28):
            C.rod('Chimney pot', (x, dy, RIDGE + 1.9), (x, dy, RIDGE + 2.35), .12, 'sand', 'chimneys', 10)


def sides_and_rear(f_right, f_rear, f_left):
    """East end wall exposed (end of row): windows at the rear half; west party wall blank; rear with wings."""
    span = D - 2 * T
    eh = [hole('End wall ground window', 2.0, .95, 1.0, 1.9), hole('End wall upper window', 2.0, U + .85, 1.0, 1.8), hole('End wall attic window', 0.0, EAVE + 1.0, .8, 1.3)]
    f_right.wall('East end carrier', -span / 2, span / 2, G0, EAVE, depth=T, holes=eh[:2])
    G.brick_courses(f_right, -span / 2 + .02, span / 2 - .02, G0, EAVE, eh[:2], spacing=.075)
    for h in eh[:2]:
        sash(f_right, h['id'], h['u'], h['z'], h['w'], h['h'])
    # End gable above the eaves following the main roof section.
    f_right.panel('East end gable', [(-span / 2, EAVE - EPS), (span / 2, EAVE - EPS), (0, RIDGE - .05)], 0, T, 'wall', 'gables')
    band(f_right, -span / 2, span / 2, U + .60)
    band(f_right, -span / 2, span / 2, .45, h=.30)
    f_left.wall('West party carrier', -span / 2, span / 2, G0, EAVE, depth=T)
    G.brick_courses(f_left, -span / 2 + .02, span / 2 - .02, G0, EAVE, [], spacing=.075)
    f_left.panel('West party gable', [(-span / 2, EAVE - EPS), (span / 2, EAVE - EPS), (0, RIDGE - .05)], 0, T, 'wall', 'gables')
    rh = []
    for name, xc, kind in UNITS:
        u = -xc
        rh.append(hole(f'Unit {name} rear door', u + 1.9, G0, .9, 2.1, kind='door'))
        rh.append(hole(f'Unit {name} rear ground window', u - 1.2, .95, 1.1, 1.8))
        rh.append(hole(f'Unit {name} rear upper window', u - 1.2, U + .85, 1.0, 1.7))
        rh.append(hole(f'Unit {name} rear upper window 2', u + 1.6, U + .85, 1.0, 1.7))
    f_rear.wall('Rear carrier', WEST_X, EAST_X, G0, EAVE, depth=T, holes=rh)
    G.brick_courses(f_rear, WEST_X + .02, EAST_X - .02, G0, EAVE, rh, spacing=.075)
    for h in rh:
        if h.get('kind') == 'door':
            f_rear.door(h['id'], h['u'], h['z'], h['w'], h['h'], role='timber', panels=4); reveal(f_rear, h['u'], h['z'], h['w'], h['h'], inset=.19)
            f_rear.part('Rear door step', h['u'], -.17, G0 / 2, 1.3, .34, G0, 'stone', 'entry steps', 0)
        else:
            sash(f_rear, h['id'], h['u'], h['z'], h['w'], h['h'])
    band(f_rear, WEST_X, EAST_X, U + .60)


def floors():
    C.box('Ground slab', (0, 0, G0 / 2), (W, D, G0), 'foundation', 'foundation', 0)
    C.box('Front paving', (0, FRONT_Y - GARDEN - 1.0, .0075), (W + 2.0, 2.0, .015), 'foundation', 'sidewalk', 0)
    C.box('Rear yard paving', (0, REAR_Y + YARD / 2, .0075), (W, YARD, .015), 'foundation', 'yards', 0)
    upper = C.box('First floor', (0, 0, U - .075), (W - 2 * T, D - 2 * T, .15), 'floor', 'occupied floors', 0)
    attic = C.box('Attic floor', (0, 0, EAVE - .075), (W - 2 * T, D - 2 * T, .15), 'floor', 'occupied floors', 0)
    for name, xc, kind in UNITS:
        xs = xc + (UW / 2 - .75) * (1 if kind != 'bay_east' else -1)
        y_end = -3.0 + 4.0
        C.cut_box(upper, f'Unit {name} stair aperture', (xs, y_end - 1.6, U), (1.1, 3.0, .6))
        G.stair(f'Unit {name} stair', xs, -3.0, G0, U, length=4.0, width=.95, landing_gap=.12)
        C.railing(f'Unit {name} stair guard', (xs + .6, y_end - 3.0, U), (xs + .6, y_end - .1, U), height=1.0, spacing=.25, role='hardware')
        C.qa_room_light(f'Unit {name} front room', (xc, -3.2, U - .3), 45, 2.4)
        C.qa_room_light(f'Unit {name} bedroom', (xc, -3.2, EAVE - .3), 40, 2.4)
        C.qa_room_light(f'Unit {name} rear', (xc, 3.0, U - .3), 40, 2.4)
        A.sofa(xc + (.6 if kind == 'bay_east' else -.6 if kind == 'bay_west' else 0), -2.6, G0)
        A.bed(xc - 1.2, -3.0, U); A.bed(xc + 1.4, 3.0, U)
    # Party walls between units (internal, blank).
    for x in (-UW / 2, UW / 2):
        C.box('Internal party wall', (x, 0, (G0 + EAVE) / 2), (.22, D - 2 * T, EAVE - G0), 'wall', 'party walls', 0)


def gardens():
    fy = FRONT_Y - GARDEN
    C.box('Garden wall', (0, fy, .25), (W, .26, .50), 'stone', 'garden wall', 0)
    for name, xc, kind in UNITS:
        gate = xc - 1.95 if kind == 'bay_east' else xc + 1.95 if kind == 'bay_west' else xc - 1.6
        C.railing('Garden fence', (xc - UW / 2 + .02, fy, .50), (gate - .55, fy, .50), height=1.0, spacing=.16, role='hardware')
        C.railing('Garden fence', (gate + .55, fy, .50), (xc + UW / 2 - .02, fy, .50), height=1.0, spacing=.16, role='hardware')
        C.railing('Garden gate', (gate - .5, fy, .50), (gate + .5, fy, .50), height=1.05, spacing=.16, role='hardware')
        C.box('Garden path', (gate, (fy + FRONT_Y - .96) / 2, .02), (1.1, FRONT_Y - .96 - fy, .04), 'stone', 'garden paths', 0)
        for dx in (-2.3, 2.3):
            hx = xc + dx
            if abs(hx - gate) > 1.0:
                C.box('Hedge', (hx, fy + 1.2, .45), (1.4, .6, .80), 'planting', 'garden planting', 0)
        C.box('Garden bed soil', (xc, FRONT_Y - GARDEN / 2, .03), (UW - .3, GARDEN - .8, .05), 'soil', 'garden planting', 0)
    for x in (-UW / 2, UW / 2):
        C.railing('Garden divider', (x, fy + .2, .05), (x, FRONT_Y - .3, .05), height=.7, spacing=.2, role='hardware')
    # Rear yard fences.
    for x in (WEST_X, -UW / 2, UW / 2, EAST_X):
        C.box('Yard fence', (x, REAR_Y + YARD / 2, .95), (.06, YARD, 1.8), 'timber', 'yards', 0)
    C.box('Yard fence rear', (0, REAR_Y + YARD - .03, .95), (W, .06, 1.8), 'timber', 'yards', 0)
    A.shrub(EAST_X - 1.5, REAR_Y + 3.0, .015, .9)
    A.shrub(WEST_X + 1.5, REAR_Y + 3.0, .015, .9)
    A.shrub(0.5, REAR_Y + 4.5, .015, .8)


def build():
    floors()
    f_front, f_right, f_rear, f_left = A.faces(W, D)
    front(f_front)
    sides_and_rear(f_right, f_rear, f_left)
    roofs()
    gardens()
    C.CONTACTS.append(dict(name='Bay windows seated on the plinth band with slate hip caps under the first-floor sill band', cap_m=U - .25))
    C.CONTACTS.append(dict(name='Chimney stacks astride the ridge at both ends and the party lines', ridge_m=RIDGE))


LIGHT_RIG = dict(key=(-16, -24, 22), fill=(20, -10, 18), rear=(-10, 24, 20), target=(0, -2, 5.0), gain=2.2)
