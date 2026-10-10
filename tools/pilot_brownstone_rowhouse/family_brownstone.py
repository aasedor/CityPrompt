"""Five-bay end-of-row brownstone with raised garden level, authored from the locked
catalogue views of brownstone_rowhouse_frontage / variant_0.

v005 incorporates the independent review of v004: three flank window columns and
a garden-level side entrance read from the oblique; two mid-depth chimneys and a
brick-cheeked shed skylight; a solid brownstone stoop with a recessed under-stoop
entry; the rear wing at the top view's proportion; measured palette (brick field
lighter than the brownstone base and hoods, light cornice); lined window reveals;
butted parapets; bands stopping short of the party-wall plane.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'pilot-brownstone-end-rowhouse'
W, D1 = 11.6, 12.8            # main block
WW, WD = 10.44, 5.1           # rear wing: 0.9 x width, 0.4 x depth; flush with the party wall
YARD = 4.4                    # areaway depth in front of the facade
G0, P, U = .15, 2.10, 5.80    # finished floor datums: garden, parlour, upper
ROOF_TOP = 9.30; MAIN_WALL_TOP = ROOF_TOP
WING_ROOF_TOP = 6.00; WING_WALL_TOP = WING_ROOF_TOP
FRONT_Y, REAR_Y = -D1 / 2, D1 / 2
WING_X0, WING_X1 = W / 2 - WW, W / 2
BAYS = [-4.64, -2.32, 0, 2.32, 4.64]
EPS = .002                    # bands and wing walls stop this short of a coplanar face
# Base colours chosen so the AgX review render lands near the source samples:
# brick ~ (174,126,90), hoods ~ (141,100,66), base/stoop ~ (70,52,40), membrane ~ (163,141,126).
PALETTE = dict(wall=(.55, .28, .15), joint=(.40, .22, .13), trim=(.10, .08, .07),
    sand=(.45, .30, .19), stone=(.26, .18, .12), pale=(.78, .74, .68),
    roof=(.50, .40, .33), foundation=(.42, .41, .39),
    glass=(.47, .53, .51), hardware=(.05, .05, .055), interior=(.74, .68, .55),
    floor=(.49, .37, .23), timber=(.28, .16, .09), planting=(.21, .33, .095),
    blue=(.12, .23, .25), soil=(.19, .14, .08), flower=(.78, .69, .23))


def manifest(version):
    h = 11.37
    cams = G.camera_roster(W, D1 + WD + YARD, h, [
        ('facade_close', (-5.2, -15.5, 3.6), (0, -7.6, 2.3), 45),
        ('architecture_close', (-4.5, -11.8, 7.6), (-1.6, FRONT_Y, 8.7), 50),
        ('glass_close', (-3.6, -9.4, 3.7), (-2.32, FRONT_Y, 4.1), 50),
        ('stoop_contact', (2.4, -13.4, 1.4), (.7, -10.4, .6), 40),
        ('areaway_door', (-2.6, -7.3, 1.25), (.3, FRONT_Y - .55, 1.0), 30),
        ('roof_contact', (-10.5, -10.5, 13.2), (-5.3, -6.1, 9.5), 55),
        ('roof_furniture', (-5.5, 8.5, 13.5), (.6, 1.6, 10.0), 45),
        ('rear_wing', (-9.5, 14.5, 6.2), (-3.4, 8.0, 4.0), 40),
        ('side_openings', (-14.0, 2.0, 5.0), (-5.8, -.5, 4.6), 35),
        ('side_entrance', (-9.5, 9.5, 2.2), (-5.8, 5.3, 1.4), 40),
        ('interior', (-2.32, -9.6, 3.9), (-2.32, -2.5, 3.3), 30),
        ('stairs', (2.6, -3.6, 3.5), (4.9, 1.2, 3.3), 24)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='brownstone_rowhouse_frontage/variant_0',
        measurement_contract=dict(dimensions_m=dict(width=W, depth=D1 + WD + YARD, height=h),
            observed_storeys=3, storey_programme='raised garden level, parlour, upper; fixed authored assembly',
            front_bays=5, parlour_bays='window window entrance window window', garden_bays='four grilled windows and an under-stoop passage',
            flank='front half blank; three sash columns per floor in the rear half; garden-level side entrance at the rear corner',
            main_block_m=[W, D1], rear_wing_m=[WW, WD], areaway_m=YARD, levels_m=[G0, P, U],
            roof_furniture='two double-pot chimneys at 58% depth on both parapets; brick-cheeked shed skylight at 55% width, 35% from rear',
            inferred='11.6 m frontage calibrates the five-bay rhythm; wing depth from the top view; interiors are teaching assumptions.'),
        roof_contract=dict(type='flat membrane behind a bracketed front cornice; lower flat rear wing', datum_m=ROOF_TOP, parapet_m=.6,
            lantern='brick-cheeked shed skylight glazed to the east', chimneys='one each on the west and east parapets at 58% depth; one on the wing'),
        identity_contract=dict(owner='five-bay brick front with brownstone hoods, pedimented entrance, solid brownstone stoop with recessed under-stoop entry, urn newels, grilled garden windows, light bracketed cornice, blank right party wall, flank side entrance'),
        material_contract=dict(profile='source-palette clay: orange-red brick field, mid-brown sandstone hoods and sills, dark brownstone base, stoop and string course, light cornice, dark sash, iron rails', textured_keeper=False),
        programme_contract=dict(storeys=3, garden='garden suite with under-stoop entrance, flank side entrance and rear door', parlour='living and dining rooms entered from the stoop', upper='two bedrooms', stairs='straight supported flights on the party-wall side with floor apertures'),
        contact_contract=['Grade-zero foundation slab', 'Solid stoop seated on the areaway with newels on the fence line', 'Recessed under-stoop passage to the garden door', 'Flank side entrance with two stone steps', 'Cornice returns on the exposed flank only', 'Wing roof seated below main parapet'],
        runtime_contract=dict(scale='fixed_native_only', installation='not installed', review='NOT TESTED'),
        camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])


def hole(name, u, z, w, h, **kw):
    return dict(id=name, u=u, z=z, w=w, h=h, **kw)


def reveal(f, u, z, w, h, inset=.14, role='sand'):
    """Line the four reveal faces from the wall plane to the frame so no unlit cavity shows."""
    d = inset / 2 + .005
    for s in (-1, 1):
        f.part('Reveal jamb liner', u + s * (w / 2 - .011), d, z + h / 2, .022, inset + .01, h, role, 'reveals', 0)
    f.part('Reveal head liner', u, d, z + h - .011, w, inset + .01, .022, role, 'reveals', 0)
    f.part('Reveal sill liner', u, d, z + .011, w, inset + .01, .022, role, 'reveals', 0)


def stone_sill(f, u, z, w):
    f.part('Sandstone sill', u, -.07, z - .05, w + .30, .40, .10, 'sand', 'window surrounds', 0)


def carved_hood(f, u, z, w, h):
    top = z + h
    f.part('Carved sandstone hood', u, -.11, top + .17, w + .46, .24, .34, 'sand', 'window surrounds', 0)
    f.part('Hood foliate panel', u, -.24, top + .17, w * .55, .03, .20, 'stone', 'window surrounds', 0)
    for s in (-1, 1):
        f.part('Hood console', u + s * (w / 2 + .14), -.14, top + .05, .14, .30, .22, 'sand', 'window surrounds', 0)


def flat_lintel(f, u, z, w, h):
    f.part('Flat sandstone lintel', u, -.03, z + h + .08, w + .26, .32, .14, 'sand', 'window surrounds', 0)


def sash(f, name, u, z, w, h, hood=True, curtain=False):
    f.window(name, u, z, w, h, cols=1, rows=2, frame='trim', depth=.28, sill=False, curtain=curtain)
    reveal(f, u, z, w, h)
    stone_sill(f, u, z, w)
    (carved_hood if hood else flat_lintel)(f, u, z, w, h)


def door(f, name, u, z, w, h, panels=3, panel_cols=1):
    f.door(name, u, z, w, h, role='timber', panels=panels, panel_cols=panel_cols)
    reveal(f, u, z, w, h, inset=.19)


def grille(f, u, z, w, h):
    for k in range(5):
        a = f.p(u - w / 2 + .12 + k * (w - .24) / 4, -.04, z + .02)
        b = f.p(u - w / 2 + .12 + k * (w - .24) / 4, -.04, z + h - .02)
        C.rod('Garden window iron grille bar', a, b, .011, 'hardware', 'garden grilles', 8)
    for zz in (z + .18, z + h - .18):
        C.beam('Garden grille rail', f.p(u - w / 2 + .04, -.04, zz), f.p(u + w / 2 - .04, -.04, zz), .022, .022, 'hardware', 'garden grilles')


def band(f, u0, u1, d, z, t, h, role, module):
    """A horizontal band that stops EPS short of both ends it was given."""
    f.part(module + ' band', (u0 + u1) / 2, d, z, (u1 - u0) - 2 * EPS, t, h, role, module, 0)


def front(f):
    gh = [hole(f'Garden window {i}', u, .45, 1.0, 1.0) for i, u in enumerate(BAYS) if u != 0]
    gd = hole('Garden suite door', 0, G0, .95, 1.70)
    f.wall('Front garden storey', -W / 2, W / 2, G0, P, depth=.28, holes=gh + [gd])
    G.brick_courses(f, -W / 2, W / 2, G0, P, gh + [gd])
    for h in gh:
        f.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=2, rows=1, frame='trim', depth=.28, sill=False)
        reveal(f, h['u'], h['z'], h['w'], h['h'])
        stone_sill(f, h['u'], h['z'], h['w']); grille(f, h['u'], h['z'], h['w'], h['h'])
        flat_lintel(f, h['u'], h['z'], h['w'], h['h'])
    door(f, gd['id'], 0, G0, .95, 1.70)
    band(f, -W / 2, W / 2, -.04, P - .02, .36, .16, 'stone', 'water table')
    ph = [hole(f'Parlour window {i}', u, P + .65, 1.15, 2.75) for i, u in enumerate(BAYS) if u != 0]
    ed = hole('Entrance double door', 0, P, 1.45, 3.00)
    f.wall('Front parlour storey', -W / 2, W / 2, P, U, depth=.28, holes=ph + [ed])
    G.brick_courses(f, -W / 2, W / 2, P, U, ph + [ed])
    for i, h in enumerate(ph):
        sash(f, h['id'], h['u'], h['z'], h['w'], h['h'], curtain=i in (0, 3))
    door(f, ed['id'], 0, P, 1.45, 2.55, panels=3, panel_cols=2)
    f.part('Entrance transom bar', 0, .19, P + 2.585, 1.45, .13, .07, 'trim', 'entrance', 0)
    f.part('Entrance transom light', 0, .22, P + 2.81, 1.33, .02, .36, 'glass', 'entrance', 0)
    architrave = f.part('Entrance architrave', 0, -.10, P + 1.50, 1.95, .22, 3.08, 'stone', 'entrance', 0)
    f.cut(architrave, 'Entrance architrave clear opening', 0, P, 1.45, 3.00, .4)
    f.part('Entrance entablature', 0, -.25, P + 3.22, 2.25, .52, .32, 'sand', 'entrance', 0)
    for s in (-1, 1):
        f.part('Entrance console', s * .86, -.22, P + 3.00, .18, .40, .26, 'sand', 'entrance', 0)
    C.prism('Entrance pediment', [(-1.15, P + 3.38), (1.15, P + 3.38), (0, P + 3.98)], 'y', FRONT_Y - .50, FRONT_Y + .02, 'sand', 'entrance')
    uh = [hole(f'Upper window {i}', u, U + .85, 1.15, 1.90) for i, u in enumerate(BAYS)]
    f.wall('Front upper storey', -W / 2, W / 2, U, MAIN_WALL_TOP, depth=.28, holes=uh)
    G.brick_courses(f, -W / 2, W / 2, U, MAIN_WALL_TOP, uh)
    for i, h in enumerate(uh):
        sash(f, h['id'], h['u'], h['z'], h['w'], h['h'], curtain=i in (1, 3))
    cornice(f, -W / 2, W / 2)
    cornice_corner()


def cornice(f, u0, u1):
    span, u = (u1 - u0) - 2 * EPS, (u0 + u1) / 2
    f.part('Cornice frieze', u, -.04, 9.05, span, .36, .30, 'pale', 'cornice', 0)
    n = max(2, round(span / .58))
    for i in range(n + 1):
        f.part('Cornice modillion', u0 + EPS + .12 + i * (span - .24) / n, -.30, 9.42, .12, .52, .28, 'pale', 'cornice', 0)
    f.part('Cornice fascia', u, -.34, 9.68, span, .64, .36, 'pale', 'cornice', 0)
    f.part('Cornice crown', u, -.40, 9.90, span, .80, .08, 'pale', 'cornice', 0)


def cornice_corner():
    x1, y1 = -W / 2, FRONT_Y
    for name, proj, z, h in (('frieze', .22, 9.05, .30), ('fascia', .66, 9.68, .36), ('crown', .80, 9.90, .08)):
        C.box('Cornice corner ' + name, (x1 - proj / 2, y1 - proj / 2, z), (proj, proj, h), 'pale', 'cornice', 0)


def flank(f):
    """Left flank: blank front half, three sash columns per floor behind, side entrance at the rear corner."""
    span = D1 - .56
    cols = (-1.3, -3.3, -5.3)
    holes = [hole('Flank garden window', -3.3, .55, .80, .80), hole('Flank side door', -5.55, G0, .95, 1.95)]
    holes += [hole(f'Flank parlour window {i}', u, P + .75, .95, 1.95) for i, u in enumerate(cols)]
    holes += [hole(f'Flank upper window {i}', u, U + .85, .95, 1.70) for i, u in enumerate(cols)]
    f.wall('Left flank brick', -span / 2, span / 2, G0, MAIN_WALL_TOP, depth=.28, holes=holes)
    G.brick_courses(f, -span / 2, span / 2, G0, MAIN_WALL_TOP, holes)
    for h in holes[2:]:
        sash(f, h['id'], h['u'], h['z'], h['w'], h['h'], hood=False)
    g = holes[0]
    f.window(g['id'], g['u'], g['z'], g['w'], g['h'], cols=1, rows=2, frame='trim', depth=.28, sill=False)
    reveal(f, g['u'], g['z'], g['w'], g['h']); stone_sill(f, g['u'], g['z'], g['w']); flat_lintel(f, g['u'], g['z'], g['w'], g['h'])
    grille(f, g['u'], g['z'], g['w'], g['h'])
    sd = holes[1]
    door(f, sd['id'], sd['u'], G0, .95, 1.95)
    flat_lintel(f, sd['u'], G0, .95, 1.95)
    # Two stone steps and a short iron rail outside the side door.
    for i, (depth, top) in enumerate(((.34, G0), (.68, G0 / 2))):
        f.part(f'Side entrance step {i}', sd['u'], -depth / 2 - .004, top / 2, 1.30, depth, top, 'stone', 'entry steps', 0)
    C.railing('Side entrance rail', f.p(sd['u'] - .70, -.02, G0), f.p(sd['u'] - .70, -.72, 0), height=.95, spacing=.11, role='hardware')
    band(f, -D1 / 2, D1 / 2, -.04, P - .02, .36, .16, 'stone', 'water table')
    C.box('Water table corner', (-W / 2 - .12, FRONT_Y - .12, P - .02), (.24, .24, .16), 'stone', 'water table', 0)
    cornice(f, D1 / 2 - 1.1, D1 / 2)
    chimney(-W / 2 + .36, FRONT_Y + .58 * D1, 9.10, 10.95)


def chimney(x, y, z0, z1):
    C.box('Brick chimney stack', (x, y, (z0 + z1) / 2), (.60, 1.00, z1 - z0), 'wall', 'chimneys', 0)
    C.box('Chimney stone cap', (x, y, z1 + .05), (.72, 1.12, .10), 'sand', 'chimneys', 0)
    for dy in (-.25, .25):
        C.rod('Clay flue pot', (x, y + dy, z1 + .10), (x, y + dy, z1 + .42), .11, 'sand', 'chimneys', 10)


def party_wall(f):
    f.wall('Right party wall main', -D1 / 2 + .28, D1 / 2 - .28, G0, MAIN_WALL_TOP, depth=.28, role='wall')
    G.brick_courses(f, -D1 / 2 + .28, D1 / 2 - .28, G0, MAIN_WALL_TOP, [])
    f.wall('Right party wall wing', D1 / 2 + EPS, D1 / 2 + WD - .28, G0, WING_WALL_TOP, depth=.28, role='wall')
    G.brick_courses(f, D1 / 2 + EPS, D1 / 2 + WD - .28, G0, WING_WALL_TOP, [])
    chimney(W / 2 - .36, FRONT_Y + .58 * D1, 9.10, 10.75)


def rear(f_main, f_wing, f_wing_side):
    holes = [hole(f'Rear upper window {i}', u, U + .85, 1.0, 1.70) for i, u in enumerate((4.0, .8, -2.4, -4.6))]
    passages = [hole('Wing passage garden', -1.0, G0, 1.2, 1.95), hole('Wing passage parlour', -1.0, P, 1.6, 2.4)]
    f_main.wall('Rear main brick', -W / 2, W / 2, G0, MAIN_WALL_TOP, depth=.28, holes=holes + passages)
    G.brick_courses(f_main, -W / 2, W / 2, G0, MAIN_WALL_TOP, holes)
    for h in holes:
        sash(f_main, h['id'], h['u'], h['z'], h['w'], h['h'], hood=False)
    wh = [hole(f'Wing parlour window {i}', u, P + .75, 1.1, 2.0) for i, u in enumerate((-3.0, 0, 3.0))]
    wh += [hole('Wing garden window 0', 0, .45, .9, 1.0), hole('Wing garden window 1', 3.0, .45, .9, 1.0), hole('Rear garden door', -3.0, G0, .95, 1.95)]
    f_wing.wall('Wing rear brick', -WW / 2, WW / 2, G0, WING_WALL_TOP, depth=.28, holes=wh)
    G.brick_courses(f_wing, -WW / 2, WW / 2, G0, WING_WALL_TOP, wh)
    for h in wh[:5]:
        sash(f_wing, h['id'], h['u'], h['z'], h['w'], h['h'], hood=False)
    door(f_wing, 'Rear garden door', -3.0, G0, .95, 1.95)
    flat_lintel(f_wing, -3.0, G0, .95, 1.95)
    x, y, _ = f_wing.p(-3.0, 0, 0)
    C.box('Rear door stone step', (x, y + .17, G0 / 2), (1.3, .34, G0), 'stone', 'entry steps', 0)
    sh = [hole('Wing flank parlour window 0', -1.3, P + .75, 1.0, 2.0), hole('Wing flank parlour window 1', 1.3, P + .75, 1.0, 2.0)]
    f_wing_side.wall('Wing flank brick', -WD / 2 + .28, WD / 2 - EPS, G0, WING_WALL_TOP, depth=.28, holes=sh)
    G.brick_courses(f_wing_side, -WD / 2 + .28, WD / 2 - EPS, G0, WING_WALL_TOP, sh)
    for h in sh:
        sash(f_wing_side, h['id'], h['u'], h['z'], h['w'], h['h'], hood=False)


def parapet(x0, x1, y0, y1, z0, height, overhang_x=True, overhang_y=True):
    """Brick parapet with a sandstone coping; the coping grows only across the thickness,
    never along the run, and side runs are butted into front and rear runs."""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    C.box('Brick roof parapet', (cx, cy, z0 + height / 2), (x1 - x0, y1 - y0, height), 'wall', 'parapet', 0)
    along_x = (x1 - x0) > (y1 - y0)
    gx = (.06 if (along_x is False and overhang_x) else 0)
    gy = (.06 if (along_x and overhang_y) else 0)
    lx = (x1 - x0) - (0 if along_x is False else .06)
    ly = (y1 - y0) - (0 if along_x else .06)
    C.box('Sandstone coping', (cx, cy, z0 + height + .035), (lx + gx, ly + gy, .07), 'sand', 'coping', 0)


def roofs():
    C.box('Main flat roof', (0, 0, ROOF_TOP - .10), (W - .56, D1 - .56, .20), 'roof', 'roof', 0)
    for yy in range(-5, 6, 2):
        C.box('Roof membrane seam', (0, yy, ROOF_TOP + .002), (W - .60, .015, .004), 'joint', 'roof', 0)
    parapet(-W / 2, -W / 2 + .28, -D1 / 2 + .28, D1 / 2 - .28, ROOF_TOP, .60)             # left, butted
    parapet(-W / 2, W / 2, -D1 / 2, -D1 / 2 + .28, ROOF_TOP, .60)                          # front, behind the cornice
    parapet(-W / 2, WING_X0, D1 / 2 - .28, D1 / 2, ROOF_TOP, .60)                          # rear, left of the wing
    parapet(WING_X0, W / 2, D1 / 2 - .28, D1 / 2, ROOF_TOP, .60)
    parapet(W / 2 - .28, W / 2, -D1 / 2 + .28, D1 / 2 - .28, ROOF_TOP, .90, overhang_x=False)  # party wall, no outward lip
    C.box('Wing flat roof', ((WING_X0 + WING_X1) / 2, D1 / 2 + WD / 2 - .14, WING_ROOF_TOP - .10), (WW - .56, WD - .28, .20), 'roof', 'roof', 0)
    parapet(WING_X0, WING_X0 + .28, D1 / 2 + EPS, D1 / 2 + WD - .28, WING_ROOF_TOP, .45)
    parapet(WING_X0, WING_X1, D1 / 2 + WD - .28, D1 / 2 + WD, WING_ROOF_TOP, .45)
    parapet(WING_X1 - .28, WING_X1, D1 / 2 + EPS, D1 / 2 + WD - .28, WING_ROOF_TOP, .70, overhang_x=False)
    # Brick-cheeked shed skylight: tall west face, glazing falling to the east.
    lx, ly = FRONT_Y * 0 + (-W / 2 + .55 * W), REAR_Y - .35 * D1
    x0, x1, y0, y1 = lx - .80, lx + .80, ly - .70, ly + .70
    hw, he = 1.55, .45
    # Hollow shed: low brick curb, tall west brick face, triangular brick cheeks, air beneath the glazing.
    C.box('Skylight brick curb', ((x0 + x1) / 2, ly, ROOF_TOP + (he - .05) / 2), (x1 - x0, y1 - y0, he - .05), 'wall', 'roof skylight', 0)
    C.box('Skylight west brick face', (x0 + .12, ly, ROOF_TOP + (hw - .03) / 2), (.24, y1 - y0, hw - .03), 'wall', 'roof skylight', 0)
    for ya, yb in ((y0, y0 + .22), (y1 - .22, y1)):
        C.prism('Skylight brick cheek', [(x0 + .24, ROOF_TOP + he - .05), (x1, ROOF_TOP + he - .05), (x0 + .24, ROOF_TOP + hw - .05)], 'y', ya, yb, 'wall', 'roof skylight')
    C.prism('Skylight sloped glazing', [(x0, ROOF_TOP + hw - .03), (x1, ROOF_TOP + he - .03), (x1, ROOF_TOP + he), (x0, ROOF_TOP + hw)], 'y', y0 + .04, y1 - .04, 'glass', 'roof skylight')
    for yy in (y0, (y0 + y1) / 2, y1):
        C.beam('Skylight glazing bar', (x0, yy, ROOF_TOP + hw + .01), (x1, yy, ROOF_TOP + he + .01), .05, .05, 'trim', 'roof skylight')
    xm, zm = (x0 + x1) / 2, ROOF_TOP + (hw + he) / 2 + .01
    C.beam('Skylight transom bar', (xm, y0, zm), (xm, y1, zm), .05, .05, 'trim', 'roof skylight')
    C.box('Wing chimney stack', ((WING_X0 + WING_X1) / 2, D1 / 2 + .62, (6.0 + 7.6) / 2), (.60, .90, 1.6), 'wall', 'chimneys', 0)
    C.box('Wing chimney cap', ((WING_X0 + WING_X1) / 2, D1 / 2 + .62, 7.65), (.72, 1.02, .10), 'sand', 'chimneys', 0)


def floors():
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
    """Solid brownstone stoop: closed cheeks to grade, landing block with a recessed under-stoop entry."""
    y_wall = FRONT_Y
    landing = C.box('Stoop landing block', (0, y_wall - .65, P / 2), (1.50, 1.30, P), 'stone', 'stoop', 0)
    # Recessed passage from the west cheek to the garden door, beneath the landing.
    C.cut_box(landing, 'Under-stoop recess', (-.075, y_wall - .50, .95), (1.35, 1.00, 1.90))
    C.railing('Landing left guard', (-.73, y_wall - .02, P), (-.73, y_wall - 1.28, P), height=1.0, spacing=.11, role='hardware')
    C.railing('Landing right guard', (.73, y_wall - .02, P), (.73, y_wall - 1.28, P), height=1.0, spacing=.11, role='hardware')
    length = YARD - 1.30 - .22
    y = y_wall - 1.30 - length
    count = 11; run = length / count; rise = P / count
    points = [(y, 0)]
    for i in range(count):
        points.extend([(y + i * run, (i + 1) * rise), (y + (i + 1) * run, (i + 1) * rise)])
    points.extend([(y + length, P - .02), (y + length, 0)])
    C.prism('Solid stoop mass', points, 'x', -.75, .75, 'stone', 'stoop')
    for xx in (-.75 + .035, .75 - .035):
        C.beam('Stoop iron handrail', (xx, y + .08, rise + 1.0), (xx, y + length - .08, P + .98), .045, .045, 'hardware', 'stoop')
        for i in range(0, count, 2):
            C.box('Stoop baluster', (xx, y + (i + .5) * run, (i + 1) * rise + .5), (.03, .03, 1.0), 'hardware', 'stoop', 0)
    for s in (-1, 1):
        x, yn = s * .95, FRONT_Y - YARD
        C.box('Stoop newel post', (x, yn, .60), (.40, .40, 1.20), 'stone', 'stoop', 0)
        C.box('Newel cap', (x, yn, 1.24), (.48, .48, .08), 'stone', 'stoop', 0)
        A.foliage('Stone newel urn', (x, yn, 1.52), (.20, .20, .26), role='stone', detail=2)


def areaway():
    fence_y = FRONT_Y - YARD
    C.box('Areaway stone curb', (-3.48, fence_y, .14), (4.64, .26, .28), 'stone', 'areaway fence', 0)
    C.box('Areaway stone curb', (3.48, fence_y, .14), (4.64, .26, .28), 'stone', 'areaway fence', 0)
    C.railing('Areaway iron fence', (-W / 2, fence_y, .28), (-1.16, fence_y, .28), height=1.10, spacing=.12, role='hardware')
    C.railing('Areaway iron fence', (1.16, fence_y, .28), (W / 2, fence_y, .28), height=1.10, spacing=.12, role='hardware')
    C.box('Left areaway return curb', (-W / 2 + .13, fence_y + YARD / 2, .14), (.26, YARD, .28), 'stone', 'areaway fence', 0)
    C.railing('Left areaway return fence', (-W / 2 + .13, fence_y, .28), (-W / 2 + .13, FRONT_Y, .28), height=1.10, spacing=.12, role='hardware')
    for x in (-3.4, 3.4):
        C.box('Areaway planter', (x, FRONT_Y - 1.0, .20), (2.4, 1.0, .40), 'stone', 'areaway planting', 0)
        C.box('Planter soil', (x, FRONT_Y - 1.0, .38), (2.2, .8, .04), 'soil', 'areaway planting', 0)
        for dx in (-.7, 0, .7):
            A.shrub(x + dx, FRONT_Y - 1.0, .40, .32)
    C.box('Areaway paving', (0, FRONT_Y - YARD / 2, .0075), (W, YARD, .015), 'foundation', 'areaway paving', 0)


def programme():
    for x in (-3.4, 3.4):
        C.box('Garden suite kitchen counter', (x, -5.2, G0 + .45), (2.2, .6, .90), 'timber', 'garden suite', 0)
        C.box('Garden counter top', (x, -5.2, G0 + .92), (2.3, .66, .05), 'pale', 'garden suite', 0)
        C.qa_room_light('Garden suite room', (x, -3.5, P - .25), 45, 2.4)
    A.sofa(-2.6, 2.0, G0); A.bed(3.2, 3.4, G0)
    C.qa_room_light('Garden suite rear', (0, 2.5, P - .25), 45, 2.4)
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
    C.qa_room_light('Stair hall', (3.2, 0, U - .30), 70, 2.4)
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
    C.CONTACTS.append(dict(name='Recessed under-stoop passage to garden suite door', clear_width_m=1.0, clear_height_m=1.90, grade_m=0))
    C.CONTACTS.append(dict(name='Stoop newels on the fence line and first riser', grade_m=0, risers=11, rise_m=P / 11, run_m=round((YARD - 1.52) / 11, 3)))
    C.CONTACTS.append(dict(name='Flank side entrance', steps=2, grade_m=0))
