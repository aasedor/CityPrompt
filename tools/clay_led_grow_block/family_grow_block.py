"""Compact controlled-environment grow block, authored from the locked catalogue views of
vertical_farm_indoor_agriculture / variant_1 (dark_panel_led_grow_block).

Read from the pixels: a near-square corner block on a concrete ground-floor plinth with a
glazed entrance near the south-west corner; five grow levels clad in dark charcoal composite
panels with six tall slot windows per face lit magenta by horticultural LED racks; a parapet
roof carrying five gabled glasshouses with ridges running north-south on the southern half,
a low planter strip, an open-topped mechanical penthouse at the north-west corner, four raised
beds at the north-east, and a perimeter guard rail.

Source conflict recorded, not averaged: the front view shows four slot rows above the plinth,
the oblique shows five. The oblique (the highest view) governs the storey count here.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G
from contract import subtract_openings

SLUG = 'clay-led-grow-block'
W, D = 22.0, 23.0
T = .30
G0 = .15
LEVELS = [4.8, 9.0, 13.2, 17.4, 21.6]        # grow floors above the plinth
ROOF = 25.8                                  # roof slab top
PARAPET = 1.0
CROWN = ROOF + PARAPET
FRONT_Y, REAR_Y, WEST_X, EAST_X = -D / 2, D / 2, -W / 2, W / 2
SLOT_W, SLOT_H = .95, 3.6
EPS = .002
PALETTE = dict(wall=(.055, .058, .065), joint=(.03, .032, .036), trim=(.03, .03, .032),
    pale=(.52, .53, .52), stone=(.36, .35, .33), roof=(.30, .31, .32), sand=(.40, .40, .38),
    foundation=(.30, .31, .32), glass=(.52, .56, .55), hardware=(.08, .085, .09),
    interior=(.72, .68, .60), floor=(.40, .40, .39), timber=(.40, .30, .20), blue=(.14, .22, .28),
    planting=(.24, .40, .14), soil=(.19, .14, .08), membrane=(.34, .36, .38),
    led=(.95, .25, .80), rack=(.60, .62, .62), leaf=(.30, .55, .18))


def manifest(version):
    h = CROWN + 3.6
    cams = G.camera_roster(W, D, h, [
        ('facade_close', (-24.0, -26.0, 6.0), (-6.0, FRONT_Y, 7.0), 45),
        ('architecture_close', (-20.0, -24.0, 24.0), (-6.0, FRONT_Y, 22.0), 50),
        ('glass_close', (-14.0, -20.0, 7.5), (-10.0, FRONT_Y, 7.4), 50),
        ('entrance_contact', (-16.0, -22.0, 2.2), (-6.0, FRONT_Y, 2.0), 40),
        ('slot_close', (-19.0, -16.5, 10.5), (WEST_X, -9.0, 10.6), 40),
        ('roof_greenhouses', (-26.0, -34.0, 37.0), (-1.0, -3.0, 27.0), 45),
        ('penthouse_contact', (-24.0, 2.0, 32.0), (-6.0, 7.5, 28.0), 45),
        ('parapet_corner', (-16.0, -17.5, 28.5), (WEST_X, FRONT_Y, 26.5), 40),
        ('interior', (-17.0, -5.0, 10.5), (WEST_X + 2.5, -5.0, 10.6), 30),
        ('beds', (21.0, 1.0, 34.0), (6.5, 8.0, 26.5), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='vertical_farm_indoor_agriculture/variant_1 (dark_panel_led_grow_block)',
        measurement_contract=dict(dimensions_m=dict(width=W, depth=D, height=h),
            observed_storeys=6, storey_programme='concrete plinth level plus five clad grow levels; fixed authored assembly',
            plan='near-square corner block, 540 x 560 px in the top view, streets to the west and south',
            slot_columns_per_face=6, slot_rows=5, slot_m=[SLOT_W, SLOT_H],
            plinth='concrete ground floor 4.8 m with a glazed entrance near the south-west corner and narrow lit slits',
            roof='five gabled glasshouses with north-south ridges on the southern half, planter strip, open-topped mechanical penthouse at the north-west, four raised beds at the north-east, perimeter rail',
            levels_m=[G0] + LEVELS, roof_m=ROOF, parapet_m=PARAPET,
            source_conflict='front view shows four slot rows, oblique shows five; oblique governs. Oblique places the penthouse toward the north-east, top view at the north-west; top view governs plan.',
            inferred='22 m frontage calibrates the six-slot cadence; north and east faces repeat the slot grammar; interiors are hydroponic rack rooms as teaching assumptions.'),
        roof_contract=dict(type='flat membrane roof behind a 1.0 m parapet; five glazed gable houses, penthouse walls and beds all seated on the slab', datum_m=ROOF, crowns_m=[CROWN, CROWN + 2.8, CROWN + 3.6]),
        identity_contract=dict(owner='dark flush panel block with six-by-five magenta-lit slot windows per face, concrete plinth with corner entrance, rooftop glasshouse row and open plant penthouse'),
        material_contract=dict(profile='source-palette clay: charcoal composite panels with recessed vertical joints, pale aluminium glasshouse frames, grey concrete plinth, blue-grey membrane, magenta LED bars behind glazing (coloured clay, not emissive)', textured_keeper=False),
        programme_contract=dict(storeys=6, ground='reception, packing and loading behind the plinth', grow='hydroponic rack rooms on five levels lit by LED bars', roof='glasshouse propagation, soil beds, plant room'),
        contact_contract=['Grade-zero slab', 'Entrance threshold at slab level', 'Slot windows cut through the carrier with lined reveals', 'Glasshouses seated on the roof slab with curb plates', 'Penthouse walls and beds bear on the roof slab', 'Rail posts seated on the parapet coping'],
        runtime_contract=dict(scale='fixed_native_only', installation='not installed', review='NOT TESTED'),
        camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])


def hole(name, u, z, w, h, **kw):
    return dict(id=name, u=u, z=z, w=w, h=h, **kw)


def seams(f, lo, hi, z0, z1, holes, spacing=.60):
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
            vertices.extend([f.p(u - .008, -.002, a), f.p(u + .008, -.002, a), f.p(u + .008, -.002, b), f.p(u - .008, -.002, b)])
            faces.append((o, o + 1, o + 2, o + 3))
    if faces:
        C.mesh(f.label + ' panel joints', vertices, faces, 'joint', 'panel joints')


def slot(f, name, u, z, w, h):
    """Slot window as a wall section: one lined reveal-and-frame ring through the carrier, pane behind it."""
    inset = .22
    ring = f.part(name + ' reveal and frame', u, (inset + .07) / 2, z + h / 2, w, inset + .07, h, 'trim', 'slot frames', 0)
    f.cut(ring, name + ' frame clear', u, z + .09, w - .18, h - .18, inset + .07)
    f.part(name + ' pane', u, inset + .06, z + h / 2, w - .18, .008, h - .18, 'glass', 'slot glazing', 0)
    C.OPENINGS.append(dict(id=name, face=f.label, u=u, z=z, width=w, height=h, kind='window', clear_wall_cut=True,
        carrier_depth_m=T, frame_inset_m=inset, pane_inset_m=inset + .06, face_origin=list(f.o), face_tangent=list(f.t),
        face_inward=list(f.n), occupied_space='grow rack room behind carrier', cols=1, rows=1))


def face_grammar(f, span, entrance=False, plinth_windows=(-6.0, 6.0)):
    """One clad elevation: plinth level, five slot rows of six columns, parapet band."""
    cols = [(-2.5 + i) * span / 7.0 for i in range(6)]
    holes = []
    for r, lvl in enumerate(LEVELS):
        for i, u in enumerate(cols):
            holes.append(hole(f'{f.label} slot {r}-{i}', u, lvl + .35, SLOT_W, SLOT_H))
    ph = []
    if entrance:
        ph.append(hole('Entrance recess', -span / 2 + 3.4, G0, 5.4, 4.0, kind='storefront'))
    if f.label == 'rear':
        ph.append(hole('Plinth loading door', span / 2 - 4.5, G0, 3.2, 3.6, kind='rollup'))
    for u in plinth_windows:
        ph.append(hole(f'{f.label} plinth slit {u:+.0f}', u, 1.4, .7, 2.2, kind='slit'))
    # Plinth carrier (concrete) and clad carrier above it, both cut by their own openings.
    f.wall(f.label + ' plinth carrier', -span / 2 + (0 if f.label in ('front', 'rear') else T), span / 2 - (0 if f.label in ('front', 'rear') else T), G0, LEVELS[0], depth=T, role='stone', holes=ph)
    f.wall(f.label + ' clad carrier', -span / 2 + (0 if f.label in ('front', 'rear') else T), span / 2 - (0 if f.label in ('front', 'rear') else T), LEVELS[0], CROWN, depth=T, role='wall', holes=holes)
    seams(f, -span / 2 + .3, span / 2 - .3, LEVELS[0] + EPS, CROWN - EPS, holes)
    for h in holes:
        slot(f, h['id'], h['u'], h['z'], h['w'], h['h'])
    # Continuous hydroponic racks behind every slot row: three shelves with LED bars and leafy trays.
    for lvl in LEVELS:
        for k in range(4):
            zz = lvl + .6 + k * .85
            f.part(f'{f.label} rack shelf {k}', 0, .95, zz, span - 2 * T - 1.0, 1.0, .04, 'rack', 'grow racks', 0)
            f.part(f'{f.label} leaf tray {k}', 0, .95, zz + .13, span - 2 * T - 1.2, .80, .18, 'leaf', 'grow racks', 0)
        # Magenta-lit rack backboard behind the slot row, washed by one magenta inspection light per face and level.
        f.part(f'{f.label} LED backboard', 0, 1.50, lvl + 2.1, span - 2 * T - 1.0, .04, 3.8, 'led', 'grow racks', 0)
        C.bpy.ops.object.light_add(type='AREA', location=f.p(0, .75, lvl + 2.1))
        light = C.bpy.context.object; light.name = f'QA grow wash {f.label} {lvl:.0f}'
        light.data.energy = 900; light.data.shape = 'RECTANGLE'; light.data.size = span - 3.0; light.data.size_y = 3.4
        light.data.color = (1.0, .32, .82)
        C.look_at(light, f.p(0, 1.5, lvl + 2.1))
    for h in ph:
        if h['kind'] == 'storefront':
            # Recessed glazed entry cut 2.2 m into the plinth: concrete returns, dark soffit, glazed screen with doors at the back.
            lined_reveal(f, h, inset=2.2, role='stone')
            f.part('Entrance recess soffit', h['u'], 1.1, h['z'] + h['h'] - .034, h['w'] - .05, 2.2, .025, 'trim', 'entrance', 0)
            f.window(h['id'] + ' screen', h['u'], h['z'], h['w'], h['h'], cols=4, rows=2, frame='trim', inset=2.2, depth=T, sill=False, kind='glazed door')
            for du in (-.12, .12):
                C.rod('Entrance door pull', f.p(h['u'] + du, 2.18, h['z'] + .9), f.p(h['u'] + du, 2.18, h['z'] + 1.5), .018, 'hardware', 'door hardware')
            f.part('Entrance recess paving', h['u'], 1.1, G0 - .005, h['w'] - .05, 2.2, .03, 'sand', 'entrance', 0)
            C.qa_room_light('Entrance recess', f.p(h['u'], 1.1, h['z'] + h['h'] - .3), 40, 2.0)
        elif h['kind'] == 'rollup':
            f.part(h['id'] + ' leaf', h['u'], .22, h['z'] + h['h'] / 2, h['w'] - .06, .05, h['h'] - .02, 'pale', 'loading door', 0)
            for k in range(1, 6):
                f.part(h['id'] + ' slat seam', h['u'], .19, h['z'] + k * h['h'] / 6, h['w'] - .10, .012, .012, 'joint', 'loading door', 0)
            lined_reveal(f, h, inset=.19, role='pale')
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='roll-up door', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=.19, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='loading bay'))
        else:
            f.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=1, rows=1, frame='trim', depth=T, sill=False)
            lined_reveal(f, h)
    # Parapet coping and a recessed shadow joint between plinth and cladding.
    f.part(f.label + ' plinth shadow joint', 0, .02, LEVELS[0] - .03, span - (0 if f.label in ('front', 'rear') else 2 * T) - .02, .10, .06, 'joint', 'panel joints', 0)


def lined_reveal(f, h, inset=.14, role='trim'):
    d = inset / 2 + .005
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    for s in (-1, 1):
        f.part('Reveal jamb liner', u + s * (w / 2 - .011), d, z + hh / 2, .022, inset + .01, hh, role, 'reveals', 0)
    f.part('Reveal head liner', u, d, z + hh - .011, w, inset + .01, .022, role, 'reveals', 0)
    f.part('Reveal sill liner', u, d, z + .011, w, inset + .01, .022, role, 'reveals', 0)


def glasshouse(cx, y0, y1, width=3.7, eave=2.2, ridge=3.4, k=0):
    """Gabled aluminium glasshouse seated on the roof slab: curb, posts, glazed walls, gable ends, glazed roof."""
    z0 = ROOF
    hw = width / 2
    C.box(f'Glasshouse {k} curb', (cx, (y0 + y1) / 2, z0 + .06), (width + .10, y1 - y0 + .10, .12), 'sand', 'glasshouse curbs', 0)
    n = max(2, round((y1 - y0) / 2.75))
    for i in range(n + 1):
        yy = y0 + i * (y1 - y0) / n
        for s in (-1, 1):
            C.box(f'Glasshouse {k} post', (cx + s * hw, yy, z0 + .12 + eave / 2), (.06, .06, eave), 'pale', f'glasshouse {k}', 0)
        C.beam(f'Glasshouse {k} rafter', (cx - hw, yy, z0 + .12 + eave), (cx, yy, z0 + .12 + ridge), .05, .05, 'pale', f'glasshouse {k}')
        C.beam(f'Glasshouse {k} rafter', (cx + hw, yy, z0 + .12 + eave), (cx, yy, z0 + .12 + ridge), .05, .05, 'pale', f'glasshouse {k}')
    for s in (-1, 1):
        C.beam(f'Glasshouse {k} eave beam', (cx + s * hw, y0, z0 + .12 + eave), (cx + s * hw, y1, z0 + .12 + eave), .06, .06, 'pale', f'glasshouse {k}')
        C.box(f'Glasshouse {k} side glazing', (cx + s * (hw - .02), (y0 + y1) / 2, z0 + .12 + eave / 2), (.012, y1 - y0 - .06, eave - .06), 'glass', f'glasshouse {k}', 0)
    C.beam(f'Glasshouse {k} ridge', (cx, y0, z0 + .12 + ridge), (cx, y1, z0 + .12 + ridge), .07, .07, 'pale', f'glasshouse {k}')
    for s in (-1, 1):
        C.prism(f'Glasshouse {k} roof glazing', [(cx + s * (hw - .03), z0 + .12 + eave + .03), (cx, z0 + .12 + ridge - .03), (cx, z0 + .12 + ridge - .015), (cx + s * (hw - .03), z0 + .12 + eave + .045)], 'y', y0 + .03, y1 - .03, 'glass', f'glasshouse {k}')
    for yy, s in ((y0, 1), (y1, -1)):
        C.prism(f'Glasshouse {k} gable glazing', [(cx - hw + .03, z0 + .12), (cx + hw - .03, z0 + .12), (cx + hw - .03, z0 + .12 + eave), (cx, z0 + .12 + ridge - .03), (cx - hw + .03, z0 + .12 + eave)], 'y', yy + (s * .02 if s > 0 else -.032), yy + (s * .032 if s > 0 else -.02), 'glass', f'glasshouse {k}')
    C.box(f'Glasshouse {k} end door frame', (cx, y0 + .03, z0 + .12 + 1.05), (.9, .05, 2.1), 'pale', f'glasshouse {k}', 0)
    # Two long benches of leafy trays inside.
    for s in (-1, 1):
        C.box(f'Glasshouse {k} bench', (cx + s * .95, (y0 + y1) / 2, z0 + .12 + .40), (1.2, y1 - y0 - 1.6, .06), 'rack', 'glasshouse benches', 0)
        C.box(f'Glasshouse {k} tray crop', (cx + s * .95, (y0 + y1) / 2, z0 + .12 + .55), (1.1, y1 - y0 - 1.7, .24), 'leaf', 'glasshouse benches', 0)
        for yy in (y0 + 1.2, (y0 + y1) / 2, y1 - 1.2):
            C.box(f'Glasshouse {k} bench leg', (cx + s * .95, yy, z0 + .12 + .19), (.05, .05, .38), 'pale', 'glasshouse benches', 0)


def roof():
    C.box('Roof slab', (0, 0, ROOF - .12), (W - 2 * T, D - 2 * T, .24), 'floor', 'roof', 0)
    C.box('Roof membrane', (0, 0, ROOF + .004), (W - 2 * T - .02, D - 2 * T - .02, .008), 'membrane', 'roof', 0)
    for xx in range(-9, 10, 3):
        C.box('Membrane seam', (xx, 0, ROOF + .010), (.015, D - 2 * T - .2, .004), 'joint', 'roof', 0)
    # Parapet coping on the four carrier tops (carriers already rise to CROWN) and the guard rail inside it.
    C.box('Coping south', (0, FRONT_Y + T / 2, CROWN + .03), (W, T + .06, .06), 'pale', 'coping', 0)
    C.box('Coping north', (0, REAR_Y - T / 2, CROWN + .03), (W, T + .06, .06), 'pale', 'coping', 0)
    C.box('Coping west', (WEST_X + T / 2, 0, CROWN + .03), (T + .06, D - 2 * T - .064, .06), 'pale', 'coping', 0)
    C.box('Coping east', (EAST_X - T / 2, 0, CROWN + .03), (T + .06, D - 2 * T - .064, .06), 'pale', 'coping', 0)
    pts = [(WEST_X + T / 2, FRONT_Y + T / 2), (EAST_X - T / 2, FRONT_Y + T / 2), (EAST_X - T / 2, REAR_Y - T / 2), (WEST_X + T / 2, REAR_Y - T / 2)]
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        if i % 2:   # side runs stop short of the corner posts of the south and north runs
            d = .3 if a[1] < b[1] else -.3
            a, b = (a[0], a[1] + d), (b[0], b[1] - d)
        C.railing(f'Parapet rail {i}', (a[0], a[1], CROWN + .06), (b[0], b[1], CROWN + .06), height=1.0, spacing=.80, role='hardware', bottom=.05)
    # Five glasshouses on the southern half, with a wider walkway between the third and fourth.
    xs = [-8.6, -4.6, -0.6, 4.2, 8.2]
    y0, y1 = FRONT_Y + 1.4, FRONT_Y + 11.6
    for k, cx in enumerate(xs):
        glasshouse(cx, y0, y1, k=k)
    # Planter strips north of the glasshouses.
    for cx, w in ((-5.5, 9.0), (5.5, 9.0)):
        C.box('Planter strip', (cx, y1 + .9, ROOF + .25), (w, .9, .50), 'sand', 'roof planters', 0)
        C.box('Planter strip soil', (cx, y1 + .9, ROOF + .48), (w - .1, .8, .04), 'soil', 'roof planters', 0)
        C.box('Planter strip crop', (cx, y1 + .9, ROOF + .62), (w - .3, .6, .28), 'leaf', 'roof planters', 0)
    # Open-topped mechanical penthouse at the north-west corner.
    px0, px1, py0, py1 = WEST_X + 4.6, WEST_X + 13.2, REAR_Y - 9.0, REAR_Y - T - .4
    ph = 6.8
    C.box('Penthouse south wall', ((px0 + px1) / 2, py0 + .15, ROOF + ph / 2), (px1 - px0, .30, ph), 'wall', 'penthouse', 0)
    C.box('Penthouse north wall', ((px0 + px1) / 2, py1 - .15, ROOF + ph / 2), (px1 - px0, .30, ph), 'wall', 'penthouse', 0)
    C.box('Penthouse west wall', (px0 + .15, (py0 + py1) / 2, ROOF + ph / 2), (.30, py1 - py0 - .60 - 2 * EPS, ph), 'wall', 'penthouse', 0)
    C.box('Penthouse east wall', (px1 - .15, (py0 + py1) / 2, ROOF + ph / 2), (.30, py1 - py0 - .60 - 2 * EPS, ph), 'wall', 'penthouse', 0)
    C.box('Penthouse coping south', ((px0 + px1) / 2, py0 + .15, ROOF + ph + .03), (px1 - px0 + .06, .36, .06), 'pale', 'penthouse', 0)
    C.box('Penthouse coping north', ((px0 + px1) / 2, py1 - .15, ROOF + ph + .03), (px1 - px0 + .06, .36, .06), 'pale', 'penthouse', 0)
    C.box('Penthouse coping west', (px0 + .15, (py0 + py1) / 2, ROOF + ph + .03), (.36, py1 - py0 - .72, .06), 'pale', 'penthouse', 0)
    C.box('Penthouse coping east', (px1 - .15, (py0 + py1) / 2, ROOF + ph + .03), (.36, py1 - py0 - .72, .06), 'pale', 'penthouse', 0)
    C.box('Penthouse door', ((px0 + px1) / 2 + 2.0, py0 - .012, ROOF + 1.1), (1.0, .024, 2.2), 'trim', 'penthouse', 0)
    C.box('Penthouse door frame', ((px0 + px1) / 2 + 2.0, py0 - .02, ROOF + 2.24), (1.1, .04, .06), 'pale', 'penthouse', 0)
    C.box('Penthouse louvre', ((px0 + px1) / 2 - 2.0, py0 - .012, ROOF + 2.2), (2.0, .024, 1.2), 'hardware', 'penthouse', 0)
    cx, cy = (px0 + px1) / 2, (py0 + py1) / 2
    C.box('Air handling unit', (cx - 1.6, cy + .6, ROOF + 1.0), (3.0, 2.0, 2.0), 'pale', 'rooftop plant', 0)
    C.rod('Air handling fan cowl', (cx - 1.6, cy + .6, ROOF + 2.0), (cx - 1.6, cy + .6, ROOF + 2.25), .55, 'hardware', 'rooftop plant', 16)
    C.rod('Nutrient tank', (cx + 2.2, cy + 1.2, ROOF), (cx + 2.2, cy + 1.2, ROOF + 2.4), .7, 'pale', 'rooftop plant', 16)
    C.rod('Nutrient tank', (cx + 2.2, cy - 1.0, ROOF), (cx + 2.2, cy - 1.0, ROOF + 2.4), .7, 'pale', 'rooftop plant', 16)
    C.box('Switchgear cabinet', (cx - 1.0, cy - 2.4, ROOF + .9), (2.4, .8, 1.8), 'hardware', 'rooftop plant', 0)
    # Four raised beds at the north-east.
    for i in range(4):
        bx = EAST_X - 7.8 + i * 1.75
        by0, by1 = REAR_Y - 9.0, REAR_Y - 2.2
        C.box('Raised bed', (bx, (by0 + by1) / 2, ROOF + .30), (1.2, by1 - by0, .60), 'sand', 'roof beds', 0)
        C.box('Raised bed soil', (bx, (by0 + by1) / 2, ROOF + .58), (1.1, by1 - by0 - .1, .04), 'soil', 'roof beds', 0)
        C.box('Raised bed crop', (bx, (by0 + by1) / 2, ROOF + .74), (.9, by1 - by0 - .3, .32), 'leaf', 'roof beds', 0)


def floors():
    C.box('Ground slab', (0, 0, G0 / 2), (W, D, G0), 'foundation', 'foundation', 0)
    C.box('Sidewalk', (0, FRONT_Y - 2.0, .0075), (W + 4.0, 4.0, .015), 'foundation', 'sidewalk', 0)
    C.box('Sidewalk west', (WEST_X - 2.0, 0, .0075), (4.0, D, .015), 'foundation', 'sidewalk', 0)
    C.box('Kerb', (0, FRONT_Y - 3.94, .06), (W + 4.0, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb west', (WEST_X - 3.94, 0, .06), (.12, D, .12), 'stone', 'sidewalk', 0)
    C.box('Rear lane', (0, REAR_Y + 1.5, .0075), (W + 4.0, 3.0, .015), 'foundation', 'sidewalk', 0)
    C.box('East lane', (EAST_X + 1.5, 0, .0075), (3.0, D, .015), 'foundation', 'sidewalk', 0)
    for lvl in LEVELS:
        C.box('Grow floor', (0, 0, lvl - .10), (W - 2 * T, D - 2 * T, .20), 'floor', 'occupied floors', 0)
    # Stair on the north-east, with a floor aperture per level.
    for i, lvl in enumerate(LEVELS[:2]):
        lower = G0 if i == 0 else LEVELS[i - 1]
        G.stair(f'Stair {i}', EAST_X - 2.4, REAR_Y - 9.5, lower, lvl, length=6.0, width=1.2, landing_gap=.12)
    # Goods lift shaft serves the upper grow levels (teaching assumption; not visible in the sources).
    C.box('Goods lift shaft', (EAST_X - 5.0, REAR_Y - 6.5, (G0 + ROOF - .24) / 2), (2.6, 3.0, ROOF - .24 - G0), 'wall', 'lift shaft', 0)
    # Interior lights: low-power magenta-tinted inspection light per level on the street faces.
    for lvl in [G0] + LEVELS:
        top = LEVELS[0] if lvl == G0 else lvl + 4.2
        for x, y in ((-7.0, -9.0), (7.0, -9.0), (-9.0, 0.0), (9.0, 0.0), (-7.0, 9.0), (7.0, 9.0)):
            light = C.qa_room_light('Grow room', (x, y, top - .5), 140 if lvl != G0 else 60, 3.5)
            if lvl != G0:
                light.data.color = (1.0, .40, .85)


def cut_stair_apertures():
    floors_ = [o for o in C.objects() if o.name.startswith('Grow floor')]
    for i, lvl in enumerate(LEVELS[:2]):
        owner = min(floors_, key=lambda o: abs(max(v.co.z for v in o.data.vertices) - lvl))
        y_end = REAR_Y - 9.5 + 6.0
        C.cut_box(owner, f'Stair aperture {i}', (EAST_X - 2.4, y_end - 1.9, lvl), (1.4, 3.6, .6))
        C.railing(f'Stair guard {i}', (EAST_X - 3.2, y_end - 3.7, lvl), (EAST_X - 3.2, y_end - .1, lvl), height=1.02, spacing=.30, role='hardware')
        C.railing(f'Stair end guard {i}', (EAST_X - 3.2, y_end - .1, lvl), (EAST_X - 1.7, y_end - .1, lvl), height=1.02, spacing=.30, role='hardware')


def programme():
    for lvl in [G0] + LEVELS:
        for x in (-4.0, 4.0):
            for y in (-3.0, 3.0):
                C.box('Central rack', (x, y, lvl + 1.6), (1.2, 5.0, 3.0), 'rack', 'grow racks', 0)
    C.box('Reception desk', (-3.0, FRONT_Y + 3.0, G0 + .5), (2.4, .8, 1.0), 'timber', 'reception', 0)
    street_tree(WEST_X - 3.0, 7.0)
    street_tree(5.0, FRONT_Y - 3.0)


def street_tree(x, y, z=.015, height=6.0, spread=1.3):
    C.rod('Street tree trunk', (x, y, z), (x, y, z + height * .55), .14, 'timber', 'street planting', 8)
    for i, (dx, dy) in enumerate(((-.5, -.2), (.5, -.1), (.0, .5))):
        tip = (x + dx * spread, y + dy * spread, z + height * .72)
        C.rod('Street tree branch', (x, y, z + height * .5), tip, .06, 'timber', 'street planting', 6)
        A.foliage('Street tree crown', tip, (.9 * spread, .9 * spread, 1.2), detail=1)


def build():
    floors()
    f_front, f_right, f_rear, f_left = A.faces(W, D)
    face_grammar(f_front, W, entrance=True, plinth_windows=(-1.5, 1.5))
    face_grammar(f_left, D, plinth_windows=(-7.0, -2.0, 3.0))
    face_grammar(f_right, D, plinth_windows=(-5.0, 5.0))
    face_grammar(f_rear, W, plinth_windows=(-6.0, 0.0, 6.0))
    cut_stair_apertures()
    roof()
    programme()
    C.CONTACTS.append(dict(name='Corner entrance threshold at slab level under a plate canopy', grade_m=0, step_m=G0))
    C.CONTACTS.append(dict(name='Glasshouse curbs, penthouse walls and beds seated on the roof slab', datum_m=ROOF))


LIGHT_RIG = dict(key=(-30, -42, 48), fill=(40, -20, 40), rear=(-18, 46, 46), target=(0, 0, 13.0), gain=7.0)
