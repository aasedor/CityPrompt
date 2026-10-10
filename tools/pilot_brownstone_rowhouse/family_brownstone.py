"""Five-bay end-of-row brownstone with raised garden level, authored from the locked
catalogue views of brownstone_rowhouse_frontage / variant_0.

Measured from pixels: front shows W W D W W parlour bays over four grilled garden
windows and an under-stoop passage, five sash bays above, a bracketed cornice and a
flat parapet roof; oblique shows a blank-ish left flank with sparse rear-half
windows, roof chimneys and a lower rear wing; top shows the rear wing offset to the
party-wall side and a glazed roof lantern. Metric dimensions are teaching
assumptions calibrated to an 11.6 m frontage.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'pilot-brownstone-end-rowhouse'
W, D1 = 11.6, 12.8            # main block
WW, WD = 7.8, 4.0             # rear wing, flush with the right party wall
YARD = 4.4                    # areaway depth in front of the facade
G0, P, U = .15, 2.10, 5.80    # finished floor datums: garden, parlour, upper
ROOF_TOP = 9.30; MAIN_WALL_TOP = ROOF_TOP
WING_ROOF_TOP = 6.00; WING_WALL_TOP = WING_ROOF_TOP
FRONT_Y, REAR_Y = -D1 / 2, D1 / 2
WING_X0, WING_X1 = W / 2 - WW, W / 2
BAYS = [-4.64, -2.32, 0, 2.32, 4.64]
PALETTE = dict(wall=(.50, .26, .17), joint=(.36, .25, .19), trim=(.10, .08, .07),
    pale=(.56, .41, .30), roof=(.55, .55, .52), foundation=(.42, .41, .39),
    glass=(.47, .53, .51), hardware=(.05, .05, .055), interior=(.74, .68, .55),
    floor=(.49, .37, .23), timber=(.28, .16, .09), planting=(.21, .33, .095),
    blue=(.12, .23, .25), soil=(.19, .14, .08), flower=(.78, .69, .23))


def manifest(version):
    h = 10.95
    cams = G.camera_roster(W, D1 + WD + YARD, h, [
        ('facade_close', (-5.2, -15.5, 3.6), (0, -7.6, 2.3), 45),
        ('architecture_close', (-4.5, -11.8, 7.6), (-1.6, FRONT_Y, 8.7), 50),
        ('glass_close', (-3.6, -9.4, 3.7), (-2.32, FRONT_Y, 4.1), 50),
        ('stoop_contact', (2.4, -13.4, 1.4), (.7, -10.4, .6), 40),
        ('areaway_door', (-2.3, -8.1, 1.3), (.3, FRONT_Y - .15, 1.1), 32),
        ('roof_contact', (-10.5, -10.5, 13.2), (-5.3, -6.1, 9.5), 55),
        ('rear_wing', (-8.5, 14.5, 6.2), (-2.0, 8.0, 4.0), 40),
        ('side_openings', (-13.0, 4.0, 5.2), (-5.8, 1.0, 5.0), 40),
        ('interior', (-2.32, -9.6, 3.9), (-2.32, -2.5, 3.3), 30),
        ('stairs', (2.6, -3.6, 3.5), (4.9, 1.2, 3.3), 24)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='brownstone_rowhouse_frontage/variant_0',
        measurement_contract=dict(dimensions_m=dict(width=W, depth=D1 + WD + YARD, height=h),
            observed_storeys=3, storey_programme='raised garden level, parlour, upper; fixed authored assembly',
            front_bays=5, parlour_bays='window window entrance window window', garden_bays='four grilled windows and an under-stoop passage',
            main_block_m=[W, D1], rear_wing_m=[WW, WD], areaway_m=YARD, levels_m=[G0, P, U],
            inferred='11.6 m frontage calibrates the five-bay rhythm; wing depth and interiors are teaching assumptions.'),
        roof_contract=dict(type='flat membrane behind a bracketed front cornice; lower flat rear wing', datum_m=ROOF_TOP,
            parapet_m=.6, lantern='glazed gable roof lantern', chimneys='two on the left flank, one on the party wall'),
        identity_contract=dict(owner='five-bay brick front with brownstone lintels, pedimented entrance, high stoop with iron rails and urn newels, grilled garden windows, bracketed cornice, blank right party wall'),
        material_contract=dict(profile='source-palette architectural clay: red-brown brick with physical coursing, brownstone trim, dark sash, iron rails', textured_keeper=False),
        programme_contract=dict(storeys=3, garden='garden suite with its own under-stoop entrance and rear door', parlour='living and dining rooms entered from the stoop', upper='two bedrooms', stairs='straight supported flights on the party-wall side with floor apertures'),
        contact_contract=['Grade-zero foundation slab', 'Stoop seated on the areaway with newels at grade', 'Open under-stoop passage to the garden door', 'Cornice returns on the exposed flank only', 'Wing roof seated below main parapet'],
        runtime_contract=dict(scale='fixed_native_only', installation='not installed', review='NOT TESTED'),
        camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])


def hole(name, u, z, w, h, **kw):
    return dict(id=name, u=u, z=z, w=w, h=h, **kw)


def stone_sill(f, u, z, w):
    f.part('Brownstone sill', u, -.07, z - .05, w + .30, .40, .10, 'pale', 'window surrounds', 0)


def carved_lintel(f, u, z, w, h):
    top = z + h
    f.part('Carved brownstone lintel', u, -.11, top + .17, w + .46, .24, .34, 'pale', 'window surrounds', 0)
    f.part('Lintel foliate panel', u, -.24, top + .17, w * .55, .03, .20, 'trim', 'window surrounds', 0)
    for s in (-1, 1):
        f.part('Lintel console', u + s * (w / 2 + .14), -.14, top + .05, .14, .30, .22, 'pale', 'window surrounds', 0)


def sash(f, name, u, z, w, h, curtain=False):
    f.window(name, u, z, w, h, cols=1, rows=2, frame='trim', depth=.28, sill=False, curtain=curtain)
    stone_sill(f, u, z, w)
    carved_lintel(f, u, z, w, h)


def grille(f, u, z, w, h):
    for k in range(5):
        a = f.p(u - w / 2 + .12 + k * (w - .24) / 4, -.04, z + .02)
        b = f.p(u - w / 2 + .12 + k * (w - .24) / 4, -.04, z + h - .02)
        C.rod('Garden window iron grille bar', a, b, .011, 'hardware', 'garden grilles', 8)
    for zz in (z + .18, z + h - .18):
        C.beam('Garden grille rail', f.p(u - w / 2 + .04, -.04, zz), f.p(u + w / 2 - .04, -.04, zz), .022, .022, 'hardware', 'garden grilles')


def front(f):
    # Garden level: four grilled windows and the under-stoop passage door.
    gh = [hole(f'Garden window {i}', u, .45, 1.0, 1.0) for i, u in enumerate(BAYS) if u != 0]
    gd = hole('Garden suite door', 0, G0, .95, 1.70)
    f.wall('Front garden storey', -W / 2, W / 2, G0, P, depth=.28, holes=gh + [gd])
    G.brick_courses(f, -W / 2, W / 2, G0, P, gh + [gd])
    for h in gh:
        f.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=2, rows=1, frame='trim', depth=.28, sill=False)
        stone_sill(f, h['u'], h['z'], h['w']); grille(f, h['u'], h['z'], h['w'], h['h'])
        f.part('Garden stone lintel', h['u'], -.03, h['z'] + h['h'] + .10, h['w'] + .30, .34, .20, 'pale', 'window surrounds', 0)
    f.door(gd['id'], 0, G0, .95, 1.70, role='timber', panels=3)
    f.part('Stone water table', 0, -.04, P - .02, W, .36, .16, 'pale', 'water table', 0)
    # Parlour: two tall sash each side of the pedimented entrance.
    ph = [hole(f'Parlour window {i}', u, P + .65, 1.15, 2.75) for i, u in enumerate(BAYS) if u != 0]
    ed = hole('Entrance double door', 0, P, 1.45, 3.00)
    f.wall('Front parlour storey', -W / 2, W / 2, P, U, depth=.28, holes=ph + [ed])
    G.brick_courses(f, -W / 2, W / 2, P, U, ph + [ed])
    for i, h in enumerate(ph):
        sash(f, h['id'], h['u'], h['z'], h['w'], h['h'], curtain=i in (0, 3))
    f.door(ed['id'], 0, P, 1.45, 2.55, role='timber', panels=3, panel_cols=2)
    f.part('Entrance transom bar', 0, .19, P + 2.585, 1.45, .13, .07, 'trim', 'entrance', 0)
    f.part('Entrance transom light', 0, .22, P + 2.81, 1.33, .02, .36, 'glass', 'entrance', 0)
    architrave = f.part('Entrance architrave', 0, -.10, P + 1.50, 1.95, .22, 3.08, 'pale', 'entrance', 0)
    f.cut(architrave, 'Entrance architrave clear opening', 0, P, 1.45, 3.00, .4)
    f.part('Entrance entablature', 0, -.25, P + 3.22, 2.25, .52, .32, 'pale', 'entrance', 0)
    for s in (-1, 1):
        f.part('Entrance console', s * .86, -.22, P + 3.00, .18, .40, .26, 'pale', 'entrance', 0)
    y0 = FRONT_Y
    C.prism('Entrance pediment', [(-1.15, P + 3.38), (1.15, P + 3.38), (0, P + 3.98)], 'y', y0 - .50, y0 + .02, 'pale', 'entrance')
    # Upper storey: five sash bays.
    uh = [hole(f'Upper window {i}', u, U + .85, 1.15, 1.90) for i, u in enumerate(BAYS)]
    f.wall('Front upper storey', -W / 2, W / 2, U, MAIN_WALL_TOP, depth=.28, holes=uh)
    G.brick_courses(f, -W / 2, W / 2, U, MAIN_WALL_TOP, uh)
    for i, h in enumerate(uh):
        sash(f, h['id'], h['u'], h['z'], h['w'], h['h'], curtain=i in (1, 3))
    cornice(f, -W / 2, W / 2)
    cornice_corner()


def cornice(f, u0, u1):
    span, u = u1 - u0, (u0 + u1) / 2
    f.part('Cornice frieze', u, -.04, 9.05, span, .36, .30, 'pale', 'cornice', 0)
    n = max(2, round(span / .58))
    for i in range(n + 1):
        f.part('Cornice modillion', u0 + .12 + i * (span - .24) / n, -.30, 9.42, .12, .52, .28, 'pale', 'cornice', 0)
    f.part('Cornice fascia', u, -.34, 9.68, span, .64, .36, 'pale', 'cornice', 0)
    f.part('Cornice crown', u, -.40, 9.90, span, .80, .08, 'pale', 'cornice', 0)


def cornice_corner():
    x1, y1 = -W / 2, FRONT_Y
    for name, proj, z, h in (('frieze', .22, 9.05, .30), ('fascia', .66, 9.68, .36), ('crown', .80, 9.90, .08)):
        C.box('Cornice corner ' + name, (x1 - proj / 2, y1 - proj / 2, z), (proj, proj, h), 'pale', 'cornice', 0)


def flank(f):
    """Left flank: quiet brick band with sparse rear-half openings and the cornice return."""
    span = D1 - .56
    holes = [hole('Flank garden window', -2.6, .55, .80, .80),
             hole('Flank parlour window 0', -1.5, P + .75, .95, 1.95), hole('Flank parlour window 1', -3.9, P + .75, .95, 1.95),
             hole('Flank upper window 0', -1.5, U + .85, .95, 1.70), hole('Flank upper window 1', -3.9, U + .85, .95, 1.70)]
    f.wall('Left flank brick', -span / 2, span / 2, G0, MAIN_WALL_TOP, depth=.28, holes=holes)
    G.brick_courses(f, -span / 2, span / 2, G0, MAIN_WALL_TOP, holes)
    for h in holes:
        f.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=1, rows=2, frame='trim', depth=.28, sill=False)
        stone_sill(f, h['u'], h['z'], h['w'])
        f.part('Flank stone lintel', h['u'], -.02, h['z'] + h['h'] + .10, h['w'] + .26, .32, .20, 'pale', 'window surrounds', 0)
    f.part('Flank water table', 0, -.04, P - .02, D1, .36, .16, 'pale', 'water table', 0)
    C.box('Water table corner', (-W / 2 - .12, FRONT_Y - .12, P - .02), (.24, .24, .16), 'pale', 'water table', 0)
    cornice(f, D1 / 2 - 1.1, D1 / 2)
    for yy in (-1.2, 3.4):
        chimney(-W / 2 + .36, yy, 9.10, 10.95)


def chimney(x, y, z0, z1):
    C.box('Brick chimney stack', (x, y, (z0 + z1) / 2), (.60, 1.00, z1 - z0), 'wall', 'chimneys', 0)
    C.box('Chimney stone cap', (x, y, z1 + .05), (.72, 1.12, .10), 'pale', 'chimneys', 0)
    for dy in (-.25, .25):
        C.rod('Clay flue pot', (x, y + dy, z1 + .10), (x, y + dy, z1 + .42), .11, 'pale', 'chimneys', 10)


def party_wall(f):
    f.wall('Right party wall main', -D1 / 2 + .28, D1 / 2 - .28, G0, MAIN_WALL_TOP, depth=.28, role='wall')
    G.brick_courses(f, -D1 / 2 + .28, D1 / 2 - .28, G0, MAIN_WALL_TOP, [])
    f.wall('Right party wall wing', D1 / 2 + .002, D1 / 2 + WD - .28, G0, WING_WALL_TOP, depth=.28, role='wall')
    G.brick_courses(f, D1 / 2 + .002, D1 / 2 + WD - .28, G0, WING_WALL_TOP, [])
    chimney(W / 2 - .36, 1.0, 9.10, 10.75)


def rear(f_main, f_wing, f_wing_side):
    # Main rear wall: exposed above the wing and on the left strip beside it.
    holes = [hole(f'Rear upper window {i}', u, U + .85, 1.0, 1.70) for i, u in enumerate((4.0, .8, -2.4, -4.6))]
    holes += [hole('Rear parlour window', 3.9, P + .75, 1.0, 2.0), hole('Rear garden window', 3.9, .45, .9, 1.0)]
    passages = [hole('Wing passage garden', -2.0, G0, 1.2, 1.95), hole('Wing passage parlour', -2.0, P, 1.6, 2.4)]
    f_main.wall('Rear main brick', -W / 2, W / 2, G0, MAIN_WALL_TOP, depth=.28, holes=holes + passages)
    G.brick_courses(f_main, -W / 2, W / 2, G0, MAIN_WALL_TOP, holes)
    for h in holes:
        f_main.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=1, rows=2, frame='trim', depth=.28, sill=False)
        stone_sill(f_main, h['u'], h['z'], h['w'])
        f_main.part('Rear stone lintel', h['u'], -.02, h['z'] + h['h'] + .10, h['w'] + .26, .32, .20, 'pale', 'window surrounds', 0)
    # Wing rear: parlour windows, garden window and the rear garden door.
    wh = [hole('Wing parlour window 0', -1.9, P + .75, 1.1, 2.0), hole('Wing parlour window 1', 1.9, P + .75, 1.1, 2.0),
          hole('Wing garden window', 1.9, .45, .9, 1.0), hole('Rear garden door', -1.9, G0, .95, 1.95)]
    f_wing.wall('Wing rear brick', -WW / 2, WW / 2, G0, WING_WALL_TOP, depth=.28, holes=wh)
    G.brick_courses(f_wing, -WW / 2, WW / 2, G0, WING_WALL_TOP, wh)
    for h in wh[:3]:
        f_wing.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=1, rows=2, frame='trim', depth=.28, sill=False)
        stone_sill(f_wing, h['u'], h['z'], h['w'])
        f_wing.part('Wing stone lintel', h['u'], -.02, h['z'] + h['h'] + .10, h['w'] + .26, .32, .20, 'pale', 'window surrounds', 0)
    f_wing.door('Rear garden door', -1.9, G0, .95, 1.95, role='timber', panels=3)
    x, y, _ = f_wing.p(-1.9, 0, 0)
    C.box('Rear door stone step', (x, y + .17, G0 / 2), (1.3, .34, G0), 'pale', 'entry steps', 0)
    # Wing left flank (faces the rear yard strip).
    sh = [hole('Wing flank parlour window', 0, P + .75, 1.0, 2.0)]
    f_wing_side.wall('Wing flank brick', -WD / 2 + .28, WD / 2 - .002, G0, WING_WALL_TOP, depth=.28, holes=sh)
    G.brick_courses(f_wing_side, -WD / 2 + .28, WD / 2 - .002, G0, WING_WALL_TOP, sh)
    f_wing_side.window(sh[0]['id'], 0, P + .75, 1.0, 2.0, cols=1, rows=2, frame='trim', depth=.28, sill=False)
    stone_sill(f_wing_side, 0, P + .75, 1.0)
    f_wing_side.part('Wing flank stone lintel', 0, -.02, P + 2.85, 1.26, .32, .20, 'pale', 'window surrounds', 0)


def parapet(x0, x1, y0, y1, z0, height, coping=True):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    C.box('Brick roof parapet', (cx, cy, z0 + height / 2), (x1 - x0, y1 - y0, height), 'wall', 'parapet', 0)
    if coping:
        along_x = (x1 - x0) > (y1 - y0)
        C.box('Stone coping', (cx, cy, z0 + height + .035), (x1 - x0 + (0 if along_x else .06), y1 - y0 + (.06 if along_x else 0), .07), 'pale', 'coping', 0)


def roofs():
    C.box('Main flat roof', (0, 0, ROOF_TOP - .10), (W - .56, D1 - .56, .20), 'roof', 'roof', 0)
    for yy in range(-5, 6, 2):
        C.box('Roof membrane seam', (0, yy, ROOF_TOP + .002), (W - .60, .015, .004), 'joint', 'roof', 0)
    parapet(-W / 2, -W / 2 + .28, -D1 / 2 + .31, D1 / 2 - .31, ROOF_TOP, .60)  # left, between front and rear runs
    parapet(-W / 2, W / 2, -D1 / 2, -D1 / 2 + .28, ROOF_TOP, .60)              # front, behind the cornice
    parapet(-W / 2, WING_X0, D1 / 2 - .28, D1 / 2, ROOF_TOP, .60)              # rear, left of the wing
    parapet(WING_X0, W / 2, D1 / 2 - .28, D1 / 2, ROOF_TOP, .60)
    parapet(W / 2 - .28, W / 2, -D1 / 2 + .31, D1 / 2 - .31, ROOF_TOP, .90)    # party wall rises higher
    C.box('Wing flat roof', ((WING_X0 + WING_X1) / 2, D1 / 2 + WD / 2 - .14, WING_ROOF_TOP - .10), (WW - .56, WD - .28, .20), 'roof', 'roof', 0)
    parapet(WING_X0, WING_X0 + .28, D1 / 2 + .002, D1 / 2 + WD - .31, WING_ROOF_TOP, .45)
    parapet(WING_X0, WING_X1, D1 / 2 + WD - .28, D1 / 2 + WD, WING_ROOF_TOP, .45)
    parapet(WING_X1 - .28, WING_X1, D1 / 2 + .002, D1 / 2 + WD - .31, WING_ROOF_TOP, .70)
    # Glazed gable roof lantern on a curb, as the top view shows off-centre.
    lx, ly = .8, 1.2
    C.box('Lantern curb', (lx, ly, ROOF_TOP + .17), (1.70, 1.40, .34), 'pale', 'roof lantern', 0)
    C.prism('Lantern glazed gable', [(ly - .70, ROOF_TOP + .34), (ly + .70, ROOF_TOP + .34), (ly, ROOF_TOP + .84)], 'x', lx - .85, lx + .85, 'glass', 'roof lantern')
    C.beam('Lantern ridge', (lx - .85, ly, ROOF_TOP + .84), (lx + .85, ly, ROOF_TOP + .84), .06, .06, 'trim', 'roof lantern')
    for s in (-1, 1):
        C.beam('Lantern eave bar', (lx - .85, ly + s * .70, ROOF_TOP + .34), (lx + .85, ly + s * .70, ROOF_TOP + .34), .05, .05, 'trim', 'roof lantern')
    C.box('Roof access hatch', (-3.2, 3.6, ROOF_TOP + .30), (1.0, 1.0, .60), 'pale', 'roof access', 0)
    C.box('Roof hatch lid', (-3.2, 3.6, ROOF_TOP + .63), (1.08, 1.08, .06), 'roof', 'roof access', 0)


def floors():
    # Grade-zero slab under the whole house; nothing is modelled below the sidewalk.
    C.box('Garden level slab', (0, 0, G0 / 2), (W, D1, G0), 'foundation', 'foundation', 0)
    C.box('Wing garden slab', ((WING_X0 + WING_X1) / 2, D1 / 2 + WD / 2, G0 / 2), (WW, WD, G0), 'foundation', 'foundation', 0)
    parlour = C.box('Parlour floor', (0, 0, P - .075), (W - .56, D1 - .56, .15), 'floor', 'occupied floors', 0)
    C.box('Wing parlour floor', ((WING_X0 + WING_X1) / 2, D1 / 2 + WD / 2 - .14, P - .075), (WW - .56, WD - .28, .15), 'floor', 'occupied floors', 0)
    upper = C.box('Upper floor', (0, 0, U - .075), (W - .56, D1 - .56, .15), 'floor', 'occupied floors', 0)
    C.cut_box(parlour, 'Parlour stair aperture', (4.9, -.1, P), (1.20, 2.40, .60))
    C.cut_box(upper, 'Upper stair aperture', (4.9, 1.8, U), (1.20, 3.80, .60))
    A.seated_guard('Parlour stairwell guard', (4.3, -1.3, P), (4.3, 1.1, P), spacing=.14)
    A.seated_guard('Upper stairwell guard', (4.3, -.1, U), (4.3, 3.7, U), spacing=.14)
    A.seated_guard('Upper stairwell end guard', (4.3, 3.7, U), (5.5, 3.7, U), spacing=.14)
    G.stair('Garden to parlour stair', 4.9, -2.4, G0, P, length=2.97, width=1.0, landing_gap=.12)
    G.stair('Parlour to upper stair', 4.9, -1.6, P, U, length=5.40, width=1.0, landing_gap=.12)


def stoop():
    y_wall = FRONT_Y
    # Landing on one solid cheek and one slender pier; the passage beneath stays open.
    C.box('Stoop landing', (0, y_wall - .65, P - .10), (1.50, 1.30, .20), 'pale', 'stoop', 0)
    C.box('Stoop right cheek wall', (.62, y_wall - .65, (P - .20) / 2), (.26, 1.30, P - .20), 'pale', 'stoop', 0)
    C.box('Stoop front-left pier', (-.62, y_wall - 1.17, (P - .20) / 2), (.26, .26, P - .20), 'pale', 'stoop', 0)
    C.railing('Landing left guard', (-.73, y_wall - .02, P), (-.73, y_wall - 1.28, P), height=1.0, spacing=.11, role='hardware')
    C.railing('Landing right guard', (.73, y_wall - .02, P), (.73, y_wall - 1.28, P), height=1.0, spacing=.11, role='hardware')
    # Eleven brownstone risers rising toward the house, iron rails above the cheeks.
    length = YARD - 1.30 - .22
    G.stair('Front stoop', 0, y_wall - 1.30 - length, 0, P, length=length, width=1.50, landing_gap=.04)
    for s in (-1, 1):
        x = s * .95
        yn = FRONT_Y - YARD
        C.box('Stoop newel post', (x, yn, .60), (.40, .40, 1.20), 'pale', 'stoop', 0)
        C.box('Newel cap', (x, yn, 1.24), (.48, .48, .08), 'pale', 'stoop', 0)
        A.foliage('Stone newel urn', (x, yn, 1.52), (.20, .20, .26), role='pale', detail=2)


def areaway():
    fence_y = FRONT_Y - YARD
    C.box('Areaway stone curb', (-3.48, fence_y, .14), (4.64, .26, .28), 'pale', 'areaway fence', 0)
    C.box('Areaway stone curb', (3.48, fence_y, .14), (4.64, .26, .28), 'pale', 'areaway fence', 0)
    C.railing('Areaway iron fence', (-W / 2, fence_y, .28), (-1.16, fence_y, .28), height=1.10, spacing=.12, role='hardware')
    C.railing('Areaway iron fence', (1.16, fence_y, .28), (W / 2, fence_y, .28), height=1.10, spacing=.12, role='hardware')
    C.box('Left areaway return curb', (-W / 2 + .13, fence_y + YARD / 2, .14), (.26, YARD, .28), 'pale', 'areaway fence', 0)
    C.railing('Left areaway return fence', (-W / 2 + .13, fence_y, .28), (-W / 2 + .13, FRONT_Y, .28), height=1.10, spacing=.12, role='hardware')
    for x in (-3.4, 3.4):
        C.box('Areaway planter', (x, FRONT_Y - 1.0, .27), (2.4, 1.0, .54), 'pale', 'areaway planting', 0)
        C.box('Planter soil', (x, FRONT_Y - 1.0, .52), (2.2, .8, .04), 'soil', 'areaway planting', 0)
        for dx in (-.7, 0, .7):
            A.shrub(x + dx, FRONT_Y - 1.0, .54, .55)
    C.box('Areaway paving', (0, FRONT_Y - YARD / 2, .02), (W, YARD, .04), 'foundation', 'areaway paving', 0)


def programme():
    # Garden suite: kitchen and living room visible through the grilled windows.
    for x in (-3.4, 3.4):
        C.box('Garden suite kitchen counter', (x, -5.2, G0 + .45), (2.2, .6, .90), 'timber', 'garden suite', 0)
        C.box('Garden counter top', (x, -5.2, G0 + .92), (2.3, .66, .05), 'pale', 'garden suite', 0)
        C.qa_room_light('Garden suite room', (x, -3.5, P - .25), 45, 2.4)
    A.sofa(-2.6, 2.0, G0); A.bed(3.2, 3.4, G0)
    C.qa_room_light('Garden suite rear', (0, 2.5, P - .25), 45, 2.4)
    # Parlour: living room toward the street, dining to the rear.
    A.sofa(-2.4, -3.6, P); A.garden_chair(-.4, -4.3, P)
    C.box('Dining table', (2.6, -3.4, P + .72), (1.8, .95, .06), 'timber', 'parlour', 0)
    for dx in (-.75, .75):
        for dy in (-.38, .38):
            C.box('Dining table leg', (2.6 + dx, -3.4 + dy, P + .36), (.06, .06, .70), 'trim', 'parlour', 0)
    for dx in (-.6, .6):
        A.garden_chair(2.6 + dx, -4.3, P); A.garden_chair(2.6 + dx, -2.5, P)
    for x in (-2.4, 2.6):
        C.qa_room_light('Parlour room', (x, -3.2, U - .30), 60, 2.8)
    C.qa_room_light('Parlour rear', (0, 3.0, U - .30), 55, 2.8)
    # Upper: two bedrooms at the front.
    A.bed(-2.6, -3.4, U); A.bed(2.6, -3.4, U); A.bathroom(-3.6, 4.2, U)
    for x in (-2.6, 2.6):
        C.qa_room_light('Bedroom', (x, -3.2, 9.10 - .30), 50, 2.6)


def build():
    floors()
    f_front, f_right, f_rear, f_left = A.faces(W, D1)
    front(f_front)
    flank(f_left)
    party_wall(f_right)
    rear(f_rear,
         C.Face(((WING_X0 + WING_X1) / 2, D1 / 2 + WD, 0), (-1, 0, 0), (0, -1, 0), 'wing rear'),
         C.Face((WING_X0, D1 / 2 + WD / 2, 0), (0, -1, 0), (1, 0, 0), 'wing flank'))
    roofs()
    stoop()
    areaway()
    programme()
    C.CONTACTS.append(dict(name='Under-stoop passage to garden suite door', clear_width_m=.98, clear_height_m=1.85, grade_m=0))
    C.CONTACTS.append(dict(name='Stoop newels and first riser', grade_m=0, risers=11, rise_m=P / 11, run_m=.27))
