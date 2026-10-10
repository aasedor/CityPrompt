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
DOOR_Z = .60                      # raised ground floor: three 200 mm risers from grade
DOOR_X = {'A': EAST_X - UW / 2 - 2.15, 'B': 0.0, 'C': WEST_X + UW / 2 + 2.15}
BAY_X = {'A': EAST_X - UW / 2 + .7, 'C': WEST_X + UW / 2 - .7}
GW, GAPEX = 3.6, RIDGE - .6       # front cross gables span the bay only (source), apex just below the main ridge
CHIMNEYS = (EAST_X - .35, -UW / 2)  # east end and the party line between units B and C, as the sources show
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
        ('gable_close', (9.5, -14.0, 9.5), (6.5, FRONT_Y, 9.3), 45),
        ('roof_contact', (-9.0, -14.0, 13.0), (-4.0, -2.0, 10.0), 45),
        ('rear_yards', (6.0, 20.0, 6.0), (0.0, REAR_Y, 3.5), 40),
        ('interior', (5.6, 1.4, 1.7), (6.6, FRONT_Y - .4, 1.3), 60),
        ('party_wall', (-18.0, -8.0, 5.0), (WEST_X, 0.0, 5.0), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='brick_rowhouse_terrace/variant_2 (queen_anne_bay_window_terrace)',
        measurement_contract=dict(dimensions_m=dict(width=W, depth=D + GARDEN + YARD, height=h),
            observed_storeys=2.5, storey_programme='ground, first floor and gable attic rooms; fixed authored assembly',
            units=3, unit_width_m=UW, unit_pattern='end unit A: bay window right under a narrow front gable, green door left; middle unit B: window, door, window, small dormer; unit C: door right, bay window left under a narrow front gable', raised_ground_floor_m=DOOR_Z,
            levels_m=[G0, U], eave_m=EAVE, ridge_m=RIDGE, main_pitch_deg=round(math.degrees(math.atan(PITCH)), 1),
            front='continuous cream bands at ground-floor lintel, first-floor sill and first-floor lintel level, cream bay piers and head bands; stone lintels and sills; stoops of three steps with iron handrails; low wall and iron fence; hedged gardens',
            roof='slate main roof with front cross gables over the end units, a small dormer over the middle unit, rear cross gables over rear wings, two chimney stacks: east end and the party line between units B and C',
            source_conflict='the locked views show the terrace continuing west; three east-end units are authored as one discrete building with a blank west party wall',
            inferred='5.8 m unit width calibrates the bay-door rhythm; depth 11 m and rear wings from the top view; interiors are teaching assumptions.'),
        roof_contract=dict(type='pitched slate main roof with cross gables front and rear, hip cap over each bay, chimney stacks', datum_m=EAVE, crowns_m=[RIDGE, RIDGE + 1.0]),
        identity_contract=dict(owner='steep bargeboard gables with green timber infill and finials over canted bay windows, cream banded red brick, three individual stooped entrances, iron fence'),
        material_contract=dict(profile='source-palette clay: red-brown brick with recessed courses and cream stone bands, cream surrounds, dark green painted timber, green and brown doors, dark slate, black iron', textured_keeper=False),
        programme_contract=dict(storeys=3, ground='hall, front room in the bay, kitchen in the rear wing per unit', upper='two bedrooms per unit', attic='gable room per end unit', stairs='straight supported flight against each party wall'),
        contact_contract=['Grade-zero slab and paths', 'Stoop of three solid treads per door as one stepped prism', 'Bay windows seated on the plinth with hip caps', 'Gables bear on the front carrier; bargeboards follow the rakes', 'Two chimneys penetrate the ridge; roof plates stop inside the end gable walls', 'Fence on a low wall at the garden line'],
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


def sash(f, name, u, z, w, h, curtain=False, arched=False, lintel=True):
    f.window(name, u, z, w, h, cols=1, rows=2, frame='trim', depth=T, sill=False, curtain=curtain)
    reveal(f, u, z, w, h)
    f.part('Stone sill', u, -.06, z - .05, w + .30, .36, .10, 'pale', 'window surrounds', 0)
    if lintel:
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
    if u1 - u0 > .3:
        f.part('Cream string course', (u0 + u1) / 2, d, z, (u1 - u0) - 2 * EPS, t, h, 'pale', 'string courses', 0)


def stoop(x, y_wall, role='stone'):
    """Three solid stone treads (200 mm risers, 320 mm goings) as one stepped prism up to the raised threshold."""
    yw = y_wall
    profile = [(yw - 1.14, 0.0), (yw - 1.14, .20), (yw - .82, .20), (yw - .82, .40), (yw - .50, .40), (yw - .50, DOOR_Z), (yw + .01, DOOR_Z), (yw + .01, 0.0)]
    C.prism('Stoop treads', profile, 'x', x - .65, x + .65, role, 'stoop')
    for s in (-1, 1):
        C.railing('Stoop handrail', (x + s * .6, yw - 1.14, 0.0), (x + s * .6, yw - .06, DOOR_Z), height=.95, spacing=.20, role='hardware')
    C.CONTACTS.append(dict(name='Stoop of three solid treads to the raised threshold', grade_m=0, risers=3, rise_m=.20, threshold_m=DOOR_Z))


def bay_window(xc, y_wall, z1=U - .25):
    """Canted ground-floor bay: three carriers with sash windows, brick courses, cream piers, stone bands and a slate hip cap."""
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
        sash(f, h[0]['id'], 0.0, .95, h[0]['w'], 1.9, curtain=i == 1, lintel=False)
        f.part('Bay plinth band', 0.0, -.03, .45, length - .04, .34, .30, 'pale', 'string courses', 0)
        f.part('Bay head band', 0.0, -.04, z1 - .12, length - .04, .36, .22, 'pale', 'string courses', 0)
        faces.append(f)
    # Cream stone piers on the two outer bay corners (identity: banded brick with stone piers).
    for (px, py) in (pts[1], pts[2]):
        C.box(f'Bay pier {xc:+.1f}', (px, py, (G0 + z1 - .23) / 2), (.26, .26, z1 - .23 - G0), 'pale', 'bay piers', 0)
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
    """Street elevation, east to west as the sources read: bay A, green door A, window B, door B, window B, maroon door C, bay C."""
    holes = []
    for name, xc, kind in UNITS:
        if kind == 'bay_east':
            holes.append(hole(f'Unit {name} door', DOOR_X[name], DOOR_Z, .95, 2.35, kind='door', role='door_green'))
            holes.append(hole(f'Unit {name} bay opening', xc + .7, G0, 3.0, U - .25 - G0, kind='bay'))
            holes.append(hole(f'Unit {name} upper bay window', xc + .7, U + .85, 1.6, 1.8))
            holes.append(hole(f'Unit {name} upper door window', DOOR_X[name], U + .85, 1.0, 1.8))
        elif kind == 'bay_west':
            holes.append(hole(f'Unit {name} door', DOOR_X[name], DOOR_Z, .95, 2.35, kind='door', role='door_brown'))
            holes.append(hole(f'Unit {name} bay opening', xc - .7, G0, 3.0, U - .25 - G0, kind='bay'))
            holes.append(hole(f'Unit {name} upper bay window', xc - .7, U + .85, 1.6, 1.8))
            holes.append(hole(f'Unit {name} upper door window', DOOR_X[name], U + .85, 1.0, 1.8))
        else:
            holes.append(hole(f'Unit {name} door', DOOR_X[name], DOOR_Z, .95, 2.35, kind='door', role='door_brown'))
            for s in (-1, 1):
                holes.append(hole(f'Unit {name} ground window {s}', xc + s * 1.8, .95, 1.1, 2.0))
                holes.append(hole(f'Unit {name} upper window {s}', xc + s * 1.5, U + .85, 1.0, 1.8))
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
    # Continuous cream bands: ground-floor lintel level (between the bays), first-floor sill level, first-floor lintel level, plinth.
    bay_edge = 1.3 + .9 + .02
    band(f, BAY_X['C'] + bay_edge, BAY_X['A'] - bay_edge, 3.30, h=.20)
    band(f, WEST_X, EAST_X, U + .55, h=.18)
    band(f, WEST_X, EAST_X, U + .85 + 1.8 + .30)
    band(f, WEST_X, EAST_X, .45, h=.30)
    for name in ('A', 'C'):
        bay_window(BAY_X[name], FRONT_Y)
    eaves_fascia(f)


def eaves_fascia(f):
    """Fascia and gutter along the eaves between and beside the narrow front gables."""
    runs = [(WEST_X + .05, BAY_X['C'] - GW / 2 - .30), (BAY_X['C'] + GW / 2 + .30, BAY_X['A'] - GW / 2 - .30), (BAY_X['A'] + GW / 2 + .30, EAST_X - .05)]
    for u0, u1 in runs:
        if u1 - u0 > .3:
            f.part('Eaves fascia', (u0 + u1) / 2, -.10, EAVE + .08, u1 - u0, .20, .16, 'green', 'eaves', 0)
            f.part('Eaves gutter', (u0 + u1) / 2, -.24, EAVE + .18, u1 - u0 - .04, .14, .12, 'lead', 'eaves', 0)


def gable(xc, y_wall, width, apex, eave, face_dir=-1, infill=True, finial=True, infill_role='green', batten_role='pale'):
    """Front or rear cross gable: brick lower triangle, timber infill above with a cut window, bargeboards, finial."""
    s = face_dir
    hw = width / 2
    f = C.Face((xc, y_wall, 0), (1 if s < 0 else -1, 0, 0), (0, -s, 0), f'gable {xc:+.1f} {"front" if s < 0 else "rear"}')
    mid = eave + (apex - eave) * .45
    f.panel('Gable brick', [(-hw, eave - EPS), (hw, eave - EPS), (hw * (1 - .45) * 1.0, mid), (-hw * (1 - .45), mid)], 0, T, 'wall', 'gables')
    if infill:
        panel = f.panel('Gable timber infill', [(-hw * .55, mid), (hw * .55, mid), (0, apex)], .02, T, infill_role, 'gables')
        ww, wh, wz = .6, 1.1, mid + .12
        f.cut(panel, f'Gable window {xc:+.1f} cut', 0.0, wz, ww, wh, depth=T)
        f.window(f'Gable window {xc:+.1f}', 0.0, wz, ww, wh, cols=1, rows=2, frame='trim', depth=T, sill=False)
        reveal(f, 0.0, wz, ww, wh, inset=.10, role='pale')
        f.part('Gable window arch', 0.0, -.03, wz + wh + .10, ww + .30, .12, .20, 'pale', 'gables', 0)
        f.part('Gable window sill', 0.0, -.04, wz - .06, ww + .30, .14, .10, 'pale', 'gables', 0)
        C.OPENINGS.append(dict(id=f'Gable window {xc:+.1f}', face=f.label, u=0.0, z=wz, width=ww, height=wh, kind='window', clear_wall_cut=True,
            carrier_depth_m=T, frame_inset_m=.14, pane_inset_m=.177, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='attic gable room'))
        for k in (-2, -1, 1, 2):
            uu = k * hw * .22
            zz = apex - (apex - mid) * abs(uu) / (hw * .55)
            f.part('Gable batten', uu, -.01, (mid + zz) / 2, .06, .05, zz - mid - .02, batten_role, 'gables', 0)
    else:
        f.panel('Gable brick upper', [(-hw * .55, mid), (hw * .55, mid), (0, apex)], 0, T, 'wall', 'gables')
    for side in (-1, 1):
        a = f.p(side * (hw + .25), -.22, eave - .15)
        b = f.p(0, -.22, apex + .22)
        C.beam('Bargeboard', a, b, .05, .30, 'pale', 'bargeboards')
        C.beam('Rake trim', f.p(side * (hw + .1), -.10, eave + .02), f.p(0, -.10, apex + .30), .04, .12, 'green', 'bargeboards')
    if finial:
        C.rod('Finial', (xc, y_wall + s * .22, apex + .22), (xc, y_wall + s * .22, apex + 1.2), .05, 'pale', 'bargeboards', 8)


def roof_z(y):
    """Height of the front main roof plane at depth y (front half)."""
    return EAVE + PITCH * (y - FRONT_Y)


def dormer(xc):
    """Small closed gabled dormer over the middle unit: timber front with a cut window, timber cheeks seated on the slope, slate roof."""
    dw, hw = 2.2, 1.1
    dy = FRONT_Y + 1.0
    eave_d, apex = 8.0, 9.6
    f = C.Face((xc, dy, 0), (1, 0, 0), (0, 1, 0), 'dormer front')
    base = roof_z(dy) - .25
    panel = f.panel('Dormer front', [(-hw, base), (hw, base), (hw, eave_d), (0, apex), (-hw, eave_d)], 0, T, 'green', 'dormer')
    ww, wh, wz = .5, .8, 8.1
    f.cut(panel, 'Dormer window cut', 0.0, wz, ww, wh, depth=T)
    f.window('Dormer window', 0.0, wz, ww, wh, cols=1, rows=1, frame='trim', depth=T, sill=False)
    reveal(f, 0.0, wz, ww, wh, inset=.10, role='pale')
    f.part('Dormer window surround', 0.0, -.03, wz + wh + .08, ww + .26, .12, .16, 'pale', 'dormer', 0)
    f.part('Dormer window sill', 0.0, -.04, wz - .06, ww + .26, .14, .10, 'pale', 'dormer', 0)
    C.OPENINGS.append(dict(id='Dormer window', face=f.label, u=0.0, z=wz, width=ww, height=wh, kind='window', clear_wall_cut=True,
        carrier_depth_m=T, frame_inset_m=.14, pane_inset_m=.177, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='attic room of unit B'))
    for k in (-1, 1):
        uu = k * .62
        zz = apex - (apex - eave_d) * abs(uu) / hw
        f.part('Dormer batten', uu, -.01, (eave_d + zz) / 2, .06, .05, zz - eave_d - .04, 'pale', 'dormer', 0)
    # Cheeks: short quads whose underside stays beneath the main roof surface.
    for s in (-1, 1):
        x = xc + s * (hw - .08)
        C.prism('Dormer cheek', [(dy + .02, base), (dy + .02, eave_d), (dy + .85, eave_d), (dy + .85, roof_z(dy + .85) - .25)], 'x', x - .08, x + .08, 'green', 'dormer')
    # Roof: gabled slate plate, ridge running back into the main slope.
    t = .22
    slope = (apex - eave_d) / hw
    ez = eave_d - .25 * slope
    C.prism('Dormer roof', [(xc - hw - .25, ez), (xc, apex + .02), (xc + hw + .25, ez), (xc + hw + .25, ez - t), (xc, apex + .02 - t), (xc - hw - .25, ez - t)],
            'y', dy - .25, dy + 2.65, 'roof', 'dormer')
    for s in (-1, 1):
        C.beam('Dormer bargeboard', (xc + s * (hw + .22), dy - .20, ez + .02), (xc, dy - .20, apex + .20), .05, .24, 'pale', 'bargeboards')
    C.rod('Dormer finial', (xc, dy - .20, apex + .20), (xc, dy - .20, apex + 1.0), .04, 'pale', 'bargeboards', 8)
    C.CONTACTS.append(dict(name='Dormer front and cheeks seated on the front roof slope, roof ridge dying into the main slope', eave_m=eave_d, apex_m=apex))


def roofs():
    """Main slate roof planes (stopped inside the end gables), narrow cross gables over the bays, dormer, two chimneys."""
    x0, x1 = WEST_X + T, EAST_X - T
    t = .22
    C.prism('Main roof front plane', [(FRONT_Y - .30, EAVE - .30 * PITCH), (0, RIDGE), (0, RIDGE - t), (FRONT_Y - .30, EAVE - .30 * PITCH - t)], 'x', x0, x1, 'roof', 'main roof')
    C.prism('Main roof rear plane', [(REAR_Y + .30, EAVE - .30 * PITCH), (0, RIDGE), (0, RIDGE - t), (REAR_Y + .30, EAVE - .30 * PITCH - t)], 'x', x0, x1, 'roof', 'main roof')
    C.beam('Ridge cap', (WEST_X, 0, RIDGE + .04), (EAST_X, 0, RIDGE + .04), .18, .10, 'lead', 'main roof')
    for name, xc, kind in UNITS:
        if kind != 'middle':
            gx = BAY_X[name]
            gw, apex = GW, GAPEX
            slope = (apex - EAVE) / (gw / 2)
            gable(gx, FRONT_Y, gw, apex, EAVE, face_dir=-1, infill_role='green' if name == 'A' else 'sand', batten_role='pale' if name == 'A' else 'green')
            C.prism(f'Cross gable roof {name}', [(gx - gw / 2 - .25, EAVE - .25 * slope), (gx, apex + .02), (gx + gw / 2 + .25, EAVE - .25 * slope),
                                                 (gx + gw / 2 + .25, EAVE - .25 * slope - t), (gx, apex + .02 - t), (gx - gw / 2 - .25, EAVE - .25 * slope - t)],
                    'y', FRONT_Y - .30, FRONT_Y + (apex - EAVE) / PITCH + .3, 'roof', 'cross gables')
        else:
            dormer(xc)
        # Rear cross gable over the rear wing of every unit.
        rw, rapex = 3.4, EAVE + 2.6
        xr = xc + (1.0 if kind == 'bay_east' else -1.0 if kind == 'bay_west' else 0.0)
        gable(xr, REAR_Y, rw, rapex, EAVE, face_dir=1, infill=False, finial=False)
        C.prism(f'Rear gable roof {name}', [(xr - rw / 2 - .2, EAVE - .2 * (rapex - EAVE) / (rw / 2)), (xr, rapex + .02), (xr + rw / 2 + .2, EAVE - .2 * (rapex - EAVE) / (rw / 2)),
                                           (xr + rw / 2 + .2, EAVE - .2 * (rapex - EAVE) / (rw / 2) - t), (xr, rapex + .02 - t), (xr - rw / 2 - .2, EAVE - .2 * (rapex - EAVE) / (rw / 2) - t)],
                'y', REAR_Y - (rapex - EAVE) / PITCH, REAR_Y + .30, 'roof', 'cross gables')
    for x in CHIMNEYS:
        C.box('Chimney stack', (x, 0, RIDGE - .6 + 1.2), (.70, 1.10, 2.4), 'wall', 'chimneys', 0)
        C.box('Chimney cap', (x, 0, RIDGE + 1.85), (.82, 1.22, .10), 'pale', 'chimneys', 0)
        for dy in (-.28, .28):
            C.rod('Chimney pot', (x, dy, RIDGE + 1.93), (x, dy, RIDGE + 2.35), .12, 'sand', 'chimneys', 10)


def sides_and_rear(f_right, f_rear, f_left):
    """East end wall exposed (end of row) with the cream bands returning; west party wall blank; rear with wings."""
    span = D - 2 * T
    eh = [hole('End wall ground window', 2.0, .95, 1.0, 1.9), hole('End wall upper window', 2.0, U + .85, 1.0, 1.8)]
    f_right.wall('East end carrier', -span / 2, span / 2, G0, EAVE, depth=T, holes=eh)
    G.brick_courses(f_right, -span / 2 + .02, span / 2 - .02, G0, EAVE, eh, spacing=.075)
    for h in eh:
        sash(f_right, h['id'], h['u'], h['z'], h['w'], h['h'])
    f_right.panel('East end gable', [(-span / 2, EAVE - EPS), (span / 2, EAVE - EPS), (0, RIDGE + .02)], 0, T, 'wall', 'gables')
    for z, h in ((3.30, .20), (U + .55, .18), (U + .85 + 1.8 + .30, .14), (.45, .30)):
        band(f_right, -span / 2, span / 2, z, h=h)
    f_left.wall('West party carrier', -span / 2, span / 2, G0, EAVE, depth=T)
    G.brick_courses(f_left, -span / 2 + .02, span / 2 - .02, G0, EAVE, [], spacing=.075)
    f_left.panel('West party gable', [(-span / 2, EAVE - EPS), (span / 2, EAVE - EPS), (0, RIDGE + .02)], 0, T, 'wall', 'gables')
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
    band(f_rear, WEST_X, EAST_X, U + .55, h=.18)


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
        gate = DOOR_X[name]
        C.railing('Garden fence', (xc - UW / 2 + .02, fy, .50), (gate - .55, fy, .50), height=1.0, spacing=.16, role='hardware')
        C.railing('Garden fence', (gate + .55, fy, .50), (xc + UW / 2 - .02, fy, .50), height=1.0, spacing=.16, role='hardware')
        C.railing('Garden gate', (gate - .5, fy, .50), (gate + .5, fy, .50), height=1.05, spacing=.16, role='hardware')
        C.box('Garden path', (gate, (fy + FRONT_Y - 1.16) / 2, .02), (1.1, FRONT_Y - 1.16 - fy, .04), 'stone', 'garden paths', 0)
        # Continuous low hedge behind the fence, broken at the gate.
        for a, b in ((xc - UW / 2 + .12, gate - .75), (gate + .75, xc + UW / 2 - .12)):
            if b - a > .5:
                C.box('Hedge', ((a + b) / 2, fy + .55, .45), (b - a, .55, .80), 'planting', 'garden planting', 0)
        C.box('Garden bed soil', (xc, FRONT_Y - GARDEN / 2, .03), (UW - .3, GARDEN - .8, .05), 'soil', 'garden planting', 0)
        A.shrub(xc + (1.6 if kind != 'bay_east' else -1.6) * (1 if gate < xc else -1), FRONT_Y - 2.2, .055, .55)
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
    C.CONTACTS.append(dict(name='Two chimney stacks astride the ridge: east end and the B/C party line', ridge_m=RIDGE))


LIGHT_RIG = dict(key=(-16, -24, 22), fill=(20, -10, 18), rear=(-10, 24, 20), target=(0, -2, 5.0), gain=2.2)
