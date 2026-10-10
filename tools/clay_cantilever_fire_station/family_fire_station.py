"""Cantilevered modern fire station, authored from the locked catalogue views of
modern_fire_station / variant_2 (fire_cantilevered_modern).

Read from the pixels: a two-storey oxblood-red panel box whose upper storey cantilevers
over a glazed apparatus hall; four glazed apparatus bays on the south apron under a lit
soffit; a deep glazed loggia cut into the south-west of the upper storey and a ribbon
window on the west; a white membrane roof; a tall glass clock tower at the south-east
corner standing proud of the front; a flagpole, memorial wall and benches on the
south-west forecourt and a small flat-roofed shelter east of the tower.
"""
import math
import clay_core as C
import assemblies as A
import geometry as G
from contract import subtract_openings

SLUG = 'clay-cantilever-fire-station'
W, D = 44.0, 32.0
T = .30
G0, U, ROOF, CROWN = .15, 5.50, 10.00, 10.60
FRONT_Y, REAR_Y, WEST_X, EAST_X = -D / 2, D / 2, -W / 2, W / 2
SETBACK = 2.0                      # ground-floor south wall sits this far under the upper storey
GY = FRONT_Y + SETBACK             # ground south wall plane
BAYS = [-3.4, 2.2, 7.8, 13.4]      # apparatus bay centres
BAY_W, BAY_H = 4.6, 4.6
TW_X0, TW_X1, TW_Y0, TW_Y1, TW_H = EAST_X, EAST_X + 5.5, FRONT_Y - 4.0, FRONT_Y + 4.0, 15.6
APRON = 18.0
EPS = .002
PALETTE = dict(wall=(.25, .06, .07), joint=(.17, .04, .045), trim=(.03, .03, .032),
    pale=(.56, .57, .56), stone=(.20, .20, .21), roof=(.82, .82, .80), sand=(.42, .40, .36),
    foundation=(.42, .42, .41), glass=(.50, .55, .54), hardware=(.09, .09, .095),
    interior=(.72, .68, .60), floor=(.40, .40, .39), timber=(.40, .30, .20), blue=(.14, .22, .28),
    planting=(.28, .45, .16), soil=(.19, .14, .08), glow=(.98, .88, .62), red=(.72, .08, .06), white=(.90, .90, .88))


def manifest(version):
    h = TW_H + .6
    cams = G.camera_roster(W + 6.0, D + APRON, h, [
        ('facade_close', (-16.0, -34.0, 5.0), (0.0, FRONT_Y, 5.0), 45),
        ('architecture_close', (-30.0, -32.0, 9.5), (-12.0, FRONT_Y, 7.5), 50),
        ('glass_close', (-14.0, -24.0, 3.2), (-12.0, GY, 3.0), 50),
        ('apparatus_bays', (6.0, -30.0, 3.0), (5.0, GY, 3.2), 40),
        ('soffit_corner', (-30.0, -22.0, 3.0), (WEST_X, FRONT_Y, 5.2), 40),
        ('tower_clock', (18.0, -36.0, 10.0), ((TW_X0 + TW_X1) / 2, TW_Y0, 11.5), 45),
        ('loggia_close', (-34.0, -26.0, 9.0), (WEST_X, -10.0, 8.0), 45),
        ('apron_contact', (16.0, -24.0, 1.6), (8.0, GY, 1.2), 40),
        ('interior', (2.2, -28.0, 2.4), (2.2, -4.0, 2.2), 30),
        ('rear_door', (10.0, 26.0, 2.5), (0.0, REAR_Y, 2.4), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='modern_fire_station/variant_2 (fire_cantilevered_modern)',
        measurement_contract=dict(dimensions_m=dict(width=W + 6.0, depth=D + APRON, height=h),
            observed_storeys=2, storey_programme='tall apparatus hall level and one upper storey; fixed authored assembly',
            plan='rectangular box 490 x 350 px in the top view (1.4 : 1) with the glass tower on the east side projecting south of the front',
            apparatus_bays=4, bay_m=[BAY_W, BAY_H], bays_position='east half of the south face, recessed 2 m under the upper storey',
            south_west_ground='full-height curtain wall under the cantilever', loggia='deep glazed recess in the south-west of the upper storey framed by the red box',
            west='ribbon window on the upper storey, dark concrete ground wall', tower_m=[TW_X1 - TW_X0, TW_Y1 - TW_Y0, TW_H], tower='fully glazed, clock faces south and east, sign band below, red cap',
            levels_m=[G0, U], roof_m=ROOF, parapet_m=CROWN - ROOF,
            forecourt='concrete apron with bollards at each bay, flagpole, memorial wall and benches to the south-west, flat shelter east of the tower, lawn panels west',
            inferred='44 m frontage calibrates four 4.6 m bays plus the glazed hall; the north face is not visible and repeats the red panel grammar with service doors; interiors (four appliances, dormitory) are teaching assumptions.'),
        roof_contract=dict(type='flat white membrane behind a 0.6 m parapet; one rooftop hatch; tower roof capped in red', datum_m=ROOF, crowns_m=[CROWN, TW_H + .6]),
        identity_contract=dict(owner='oxblood panel box cantilevered over a glazed apparatus hall with four bays and a lit soffit edge, south-west loggia, and a slender glass clock tower'),
        material_contract=dict(profile='source-palette clay: oxblood composite panels with recessed joints, near-black mullions, dark concrete plinth, white membrane, pale aluminium tower frame, warm light strip', textured_keeper=False),
        programme_contract=dict(storeys=2, ground='apparatus hall with four appliances, watch room behind the south-west glass', upper='dormitory, day room and offices behind the loggia', stairs='straight supported flight behind the hall'),
        contact_contract=['Grade-zero slab and apron', 'Bay thresholds at slab level', 'Soffit slab cantilevers 2 m over the bay line with the light strip at its edge', 'Tower seated on its own slab and tied to the east wall', 'Bollards, flagpole, benches and memorial wall seated on the apron', 'Shelter posts on the apron'],
        runtime_contract=dict(scale='fixed_native_only', installation='not installed', review='NOT TESTED'),
        camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])


def hole(name, u, z, w, h, **kw):
    return dict(id=name, u=u, z=z, w=w, h=h, **kw)


def joints(f, lo, hi, z0, z1, holes, spacing=1.2, rows=(7.0, 8.6)):
    """Recessed panel joints: vertical at 1.2 m, horizontal at the stated datums, one mesh per elevation."""
    vertices, faces = [], []
    def quad(a, b, c, d):
        o = len(vertices); vertices.extend([a, b, c, d]); faces.append((o, o + 1, o + 2, o + 3))
    n = max(1, round((hi - lo) / spacing))
    for i in range(1, n):
        u = lo + i * (hi - lo) / n
        spans = [(z0, z1)]
        for h in holes:
            if h['u'] - h['w'] / 2 - .01 < u < h['u'] + h['w'] / 2 + .01:
                spans = [s for a, b in spans for s in ((a, min(b, h['z'])), (max(a, h['z'] + h['h']), b)) if s[1] - s[0] > .001]
        for a, b in spans:
            quad(f.p(u - .006, -.002, a), f.p(u + .006, -.002, a), f.p(u + .006, -.002, b), f.p(u - .006, -.002, b))
    for z in rows:
        if z0 < z < z1:
            for a, b in subtract_openings(lo, hi, z - .006, z + .006, holes):
                quad(f.p(a, -.002, z - .006), f.p(b, -.002, z - .006), f.p(b, -.002, z + .006), f.p(a, -.002, z + .006))
    if faces:
        C.mesh(f.label + ' panel joints', vertices, faces, 'joint', 'panel joints')


def lined(f, h, inset=.14, role='trim'):
    d = inset / 2 + .005
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    for s in (-1, 1):
        f.part('Reveal jamb liner', u + s * (w / 2 - .011), d, z + hh / 2, .022, inset + .01, hh, role, 'reveals', 0)
    f.part('Reveal head liner', u, d, z + hh - .011, w, inset + .01, .022, role, 'reveals', 0)
    f.part('Reveal sill liner', u, d, z + .011, w, inset + .01, .022, role, 'reveals', 0)


def curtain(f, h, cols, rows, kind='window'):
    f.window(h['id'], h['u'], h['z'], h['w'], h['h'], cols=cols, rows=rows, frame='trim', depth=T, sill=False, kind=kind)
    lined(f, h)


def bay_door(f, name, u, z, w, h):
    """Glazed sectional apparatus door: steel guide frame, four lites across, four panels high."""
    inset = .16
    for s in (-1, 1):
        f.part(name + ' guide', u + s * (w / 2 - .05), inset, z + h / 2, .10, .14, h, 'trim', 'apparatus doors', 0)
    f.part(name + ' head', u, inset, z + h - .08, w - .20, .14, .16, 'trim', 'apparatus doors', 0)
    for i in range(1, 4):
        f.part(name + f' rail {i}', u, inset, z + i * h / 4, w - .20, .09, .07, 'trim', 'apparatus doors', 0)
    for i in range(1, 4):
        f.part(name + f' stile {i}', u - w / 2 + .10 + i * (w - .20) / 4, inset, z + h / 2, .06, .09, h - .16, 'trim', 'apparatus doors', 0)
    f.part(name + ' glazing', u, inset + .05, z + (h - .16) / 2 + .01, w - .22, .008, h - .18, 'glass', 'apparatus doors', 0)
    lined(f, dict(u=u, z=z, w=w, h=h), inset=inset)
    C.OPENINGS.append(dict(id=name, face=f.label, u=u, z=z, width=w, height=h, kind='glazed sectional door', clear_wall_cut=True,
        carrier_depth_m=T, frame_inset_m=inset, pane_inset_m=inset + .05, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n),
        occupied_space='apparatus hall beyond door', cols=4, rows=4))


def south_upper(f):
    """Oxblood upper box at the front plane with the deep loggia and the cantilever soffit below."""
    f.wall('South upper carrier', WEST_X, EAST_X, U, CROWN, depth=T)
    joints(f, WEST_X + .2, EAST_X - .2, U + EPS, CROWN - EPS, [])
    # Cantilever soffit slab from the front plane back to the ground-floor wall, lined pale underneath.
    C.box('Cantilever soffit slab', (0, FRONT_Y + SETBACK / 2 + T / 2, U - .25), (W, SETBACK + T, .50), 'wall', 'cantilever', 0)
    C.box('Soffit lining', (0, FRONT_Y + SETBACK / 2 + .10, U - .505), (W - 14.0 - .02, SETBACK - .2, .01), 'pale', 'cantilever', 0)
    # The red skin steps down at both ends to door-head height; the light strip traces the stepped profile.
    for x0, x1 in ((WEST_X, WEST_X + 7.0), (EAST_X - 7.0, EAST_X)):
        cx = (x0 + x1) / 2
        C.box('Stepped soffit volume', (cx, FRONT_Y + SETBACK / 2 + T / 2, (3.6 + U - .5) / 2), (x1 - x0, SETBACK + T, U - .5 - 3.6), 'wall', 'cantilever', 0)
        C.box('Stepped soffit lining', (cx, FRONT_Y + SETBACK / 2 + .10, 3.595), (x1 - x0 - .02, SETBACK - .2, .01), 'pale', 'cantilever', 0)
        C.box('Step light strip', (cx, FRONT_Y + .10, 3.58), (x1 - x0 - .40, .07, .05), 'glow', 'cantilever', 0)
        sx = x1 if x0 == WEST_X else x0
        C.box('Step riser light strip', (sx + (.04 if x0 == WEST_X else -.04), FRONT_Y + .10, (3.6 + U - .5) / 2), (.05, .07, U - .5 - 3.6 - .1), 'glow', 'cantilever', 0)
        C.qa_room_light('Soffit', (cx, FRONT_Y + SETBACK / 2, 3.2), 70, 2.4)
    C.box('Soffit light strip', (0, FRONT_Y + .10, U - .52), (W - 14.0 - .40, .07, .05), 'glow', 'cantilever', 0)
    C.qa_room_light('Soffit centre', (0, FRONT_Y + SETBACK / 2, U - .9), 30, 3.0)
    C.box('Parapet coping south', (0, FRONT_Y + T / 2, CROWN + .03), (W, T + .06, .06), 'wall', 'coping', 0)


def south_ground(f):
    """Ground-floor south wall 2 m back under the cantilever: curtain wall west, four bays east."""
    cw = hole('Hall curtain wall', 0.0, G0, W - 2 * T - .4, U - .25 - G0, kind='curtain')
    f.wall('South ground carrier', WEST_X, EAST_X, G0, U - .25 + EPS, depth=T, role='stone', holes=[cw])
    lined(f, cw)
    # Glazed segments: watch room to the west, glazed strips between the bays, entrance lobby to the east.
    west = hole('Watch room glazing', (WEST_X + T + .2 + BAYS[0] - BAY_W / 2 - .5) / 2, G0, (BAYS[0] - BAY_W / 2 - .5) - (WEST_X + T + .2), U - .25 - G0)
    f.window(west['id'], west['u'], west['z'], west['w'], west['h'], cols=8, rows=2, frame='trim', depth=T, sill=False)
    for b in BAYS:
        bay_door(f, f'Apparatus bay {BAYS.index(b) + 1}', b, G0, BAY_W, BAY_H)
        f.part('Bay head glazing frame', b, .16, (BAY_H + G0 + U - .25) / 2, BAY_W, .10, U - .25 - BAY_H - G0, 'trim', 'apparatus doors', 0)
        f.part('Bay head glazing', b, .20, (BAY_H + G0 + U - .25) / 2, BAY_W - .14, .008, U - .25 - BAY_H - G0 - .14, 'glass', 'apparatus doors', 0)
    for u in (BAYS[0] + BAY_W / 2 + .5, BAYS[1] + BAY_W / 2 + .5, BAYS[2] + BAY_W / 2 + .5):
        f.window(f'Bay mullion strip {u:+.1f}', u, G0, 1.0, U - .25 - G0, cols=1, rows=2, frame='trim', depth=T, sill=False)
    east = hole('Entrance lobby glazing', (BAYS[3] + BAY_W / 2 + .5 + EAST_X - T - .2) / 2, G0, (EAST_X - T - .2) - (BAYS[3] + BAY_W / 2 + .5), U - .25 - G0)
    f.window(east['id'], east['u'], east['z'], east['w'], east['h'], cols=3, rows=2, frame='trim', depth=T, sill=False, kind='glazed door')
    for du in (-.12, .12):
        C.rod('Lobby door pull', f.p(east['u'] + du, .01, G0 + .9), f.p(east['u'] + du, .01, G0 + 1.5), .018, 'hardware', 'door hardware')
    f.part('Hall threshold', 0, .06, G0 - .005, W - .4, .40, .03, 'sand', 'apron', 0)


def west(f):
    """West face: dark concrete ground with a curtain-wall return at the south corner; red upper with a ribbon window."""
    loggia = hole('West loggia', 10.7, U + 1.2, 9.4, 2.8)
    f.wall('West upper carrier', -D / 2 + T, D / 2 - T, U, CROWN, depth=T, holes=[loggia])
    joints(f, -D / 2 + T + .2, D / 2 - .2, U + EPS, CROWN - EPS, [loggia])
    # Loggia: 1.2 m deep red returns and soffit, glazed wall at the back of the recess.
    lined(f, loggia, inset=1.20, role='wall')
    f.window(loggia['id'], loggia['u'], loggia['z'], loggia['w'], loggia['h'], cols=5, rows=1, frame='trim', inset=1.20, depth=T, sill=False)
    C.qa_room_light('Loggia', f.p(loggia['u'], .6, loggia['z'] + loggia['h'] - .3), 25, 2.0)
    ret = hole('West hall glass return', 8.0, G0, 10.0, U - .25 - G0, kind='curtain')
    sd = hole('West staff door', -4.0, G0, 1.1, 2.4, kind='door')
    gw = hole('West ground window', -10.0, 1.2, 2.4, 2.0)
    holes = [ret, sd, gw]
    f.wall('West ground carrier', -D / 2 + T, D / 2 - SETBACK - T, G0, U - .25 + EPS, depth=T, role='stone', holes=holes)
    curtain(f, ret, cols=5, rows=2)
    f.door(sd['id'], sd['u'], sd['z'], sd['w'], sd['h'], role='trim', panels=1); lined(f, sd, inset=.19)
    f.part('Door step', sd['u'], -.17, G0 / 2, 1.4, .34, G0, 'stone', 'entry steps', 0)
    curtain(f, gw, cols=2, rows=1)
    C.box('Parapet coping west', (WEST_X + T / 2, 0, CROWN + .03), (T + .06, D - 2 * T - .064, .06), 'wall', 'coping', 0)


def east(f):
    """East face: red upper with two punched windows north of the tower; concrete ground with a door."""
    holes = [hole('East upper window 0', 8.0, U + 1.2, 3.0, 2.2), hole('East upper window 1', 12.5, U + 1.2, 3.0, 2.2)]
    f.wall('East upper carrier', -D / 2 + T, D / 2 - T, U, CROWN, depth=T, holes=holes)
    joints(f, -D / 2 + T + .2, D / 2 - .2, U + EPS, CROWN - EPS, holes)
    for h in holes:
        curtain(f, h, cols=2, rows=1)
    gh = [hole('East service door', 6.0, G0, 1.1, 2.4, kind='door'), hole('East ground window', 11.0, 1.2, 2.4, 2.0)]
    f.wall('East ground carrier', -D / 2 + SETBACK + T, D / 2 - T, G0, U - .25 + EPS, depth=T, role='stone', holes=gh)
    f.door(gh[0]['id'], gh[0]['u'], gh[0]['z'], gh[0]['w'], gh[0]['h'], role='trim', panels=1); lined(f, gh[0], inset=.19)
    f.part('Door step', gh[0]['u'], -.17, G0 / 2, 1.4, .34, G0, 'stone', 'entry steps', 0)
    curtain(f, gh[1], cols=2, rows=1)
    C.box('Parapet coping east', (EAST_X - T / 2, 0, CROWN + .03), (T + .06, D - 2 * T - .064, .06), 'wall', 'coping', 0)


def north(f):
    holes = [hole(f'Rear upper window {i}', u, U + 1.2, 3.0, 2.2) for i, u in enumerate((-12.0, -4.0, 4.0, 12.0))]
    f.wall('North upper carrier', WEST_X, EAST_X, U, CROWN, depth=T, holes=holes)
    joints(f, WEST_X + .2, EAST_X - .2, U + EPS, CROWN - EPS, holes)
    for h in holes:
        curtain(f, h, cols=2, rows=1)
    gh = [hole('Rear roll-up door', -8.0, G0, 4.0, 4.2, kind='rollup'), hole('Rear service door', 0.0, G0, 1.1, 2.4, kind='door'),
          hole('Rear ground window 0', 8.0, 1.2, 2.4, 2.0), hole('Rear ground window 1', 14.0, 1.2, 2.4, 2.0)]
    f.wall('North ground carrier', WEST_X, EAST_X, G0, U - .25 + EPS, depth=T, role='stone', holes=gh)
    r = gh[0]
    f.part(r['id'] + ' leaf', r['u'], .22, r['z'] + r['h'] / 2, r['w'] - .06, .05, r['h'] - .02, 'pale', 'rear door', 0)
    for k in range(1, 6):
        f.part(r['id'] + ' slat seam', r['u'], .19, r['z'] + k * r['h'] / 6, r['w'] - .10, .012, .012, 'joint', 'rear door', 0)
    lined(f, r, inset=.19, role='pale')
    C.OPENINGS.append(dict(id=r['id'], face=f.label, u=r['u'], z=r['z'], width=r['w'], height=r['h'], kind='roll-up door', clear_wall_cut=True,
        carrier_depth_m=T, frame_inset_m=.19, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='apparatus hall'))
    f.door(gh[1]['id'], gh[1]['u'], gh[1]['z'], gh[1]['w'], gh[1]['h'], role='trim', panels=1); lined(f, gh[1], inset=.19)
    f.part('Door step', gh[1]['u'], -.17, G0 / 2, 1.4, .34, G0, 'stone', 'entry steps', 0)
    for h in gh[2:]:
        curtain(f, h, cols=2, rows=1)
    C.box('Parapet coping north', (0, REAR_Y - T / 2, CROWN + .03), (W, T + .06, .06), 'wall', 'coping', 0)


def tower():
    """Glass clock tower: corner columns, floor plates, glazed faces with mullions, clock faces, sign band, red cap."""
    x0, x1, y0, y1, h = TW_X0, TW_X1, TW_Y0, TW_Y1, TW_H
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    C.box('Tower slab', (cx, cy, G0 / 2), (x1 - x0, y1 - y0, G0), 'foundation', 'tower', 0)
    for xx, yy in ((x0 + .22, y0 + .22), (x1 - .22, y0 + .22), (x1 - .22, y1 - .22), (x0 + .22, y1 - .22)):
        C.box('Tower corner column', (xx, yy, G0 + (h - G0) / 2), (.40, .40, h - G0), 'trim', 'tower', 0)
    for z in (U, 9.5, 13.5):
        C.box('Tower floor plate', (cx, cy, z - .10), (x1 - x0 - .5, y1 - y0 - .5, .20), 'floor', 'tower', 0)
    # Glazed faces: south, east, north full; west only where it stands proud of the station box.
    faces = [((cx, y0 + .02), (1, 0), x1 - x0 - .44, 'south'), ((x1 - .02, cy), (0, 1), y1 - y0 - .44, 'east'),
             ((cx, y1 - .02), (1, 0), x1 - x0 - .44, 'north'), ((x0 + .02, (y0 + FRONT_Y) / 2), (0, 1), FRONT_Y - y0 - .24, 'west')]
    for (px, py), (tx, ty), span, label in faces:
        C.box(f'Tower {label} glazing', (px, py, G0 + (h - G0) / 2), (max(.012, span * abs(tx)), max(.012, span * abs(ty)), h - G0 - .4), 'glass', 'tower glazing', 0)
        n = max(2, round(span / 1.4))
        for i in range(1, n):
            mx, my = px + tx * (-span / 2 + i * span / n), py + ty * (-span / 2 + i * span / n)
            C.box(f'Tower {label} mullion', (mx, my, G0 + (h - G0) / 2), (max(.06, .10 * abs(ty)), max(.06, .10 * abs(tx)), h - G0 - .4), 'pale', 'tower frame', 0)
        for z in (U, 9.5, 13.5):
            C.box(f'Tower {label} transom', (px + tx * 0, py + ty * 0, z), (max(.10, span * abs(tx)), max(.10, span * abs(ty)), .12), 'pale', 'tower frame', 0)
    C.box('Tower fascia', (cx, cy, h + .25), (x1 - x0 + .10, y1 - y0 + .10, .50), 'wall', 'tower', 0)
    C.box('Tower roof membrane', (cx, cy, h + .504), (x1 - x0 - .10, y1 - y0 - .10, .008), 'roof', 'tower', 0)
    C.box('Tower head beam', (cx, cy, h - .20), (x1 - x0 - .40, y1 - y0 - .40, .40), 'trim', 'tower', 0)
    for (px, py, nx, ny) in ((cx, y0 - .03, 0, -1), (x1 + .03, cy, 1, 0)):
        C.rod('Clock face', (px - nx * .012, py - ny * .012, 12.4), (px + nx * .012, py + ny * .012, 12.4), 1.3, 'white', 'clock', 48)
        C.beam('Clock hour hand', (px + nx * .02, py + ny * .02, 12.4), (px + nx * .02 + ny * .75, py + ny * .02 - nx * .75, 13.0), .08, .02, 'trim', 'clock')
        C.beam('Clock minute hand', (px + nx * .02, py + ny * .02, 12.4), (px + nx * .02, py + ny * .02, 13.55), .06, .02, 'trim', 'clock')
        C.box('Sign band', (px - nx * .005, py - ny * .005, 10.2), (max(.02, 4.4 * abs(ny)), max(.02, 4.4 * abs(nx)), .9), 'red', 'clock', 0)
    # Tie beams into the station east wall where the tower stands beside it.
    for z in (U, 9.5):
        C.box('Tower tie', (x0 + .15, (FRONT_Y + y1) / 2, z - .10), (.30, y1 - FRONT_Y - .4, .20), 'trim', 'tower', 0)


def roof():
    C.box('Roof slab', (0, 0, ROOF - .12), (W - 2 * T, D - 2 * T, .24), 'floor', 'roof', 0)
    C.box('Roof membrane', (0, 0, ROOF + .004), (W - 2 * T - .02, D - 2 * T - .02, .008), 'roof', 'roof', 0)
    for xx in range(-18, 19, 6):
        C.box('Membrane seam', (xx, 0, ROOF + .010), (.015, D - 2 * T - .2, .004), 'joint', 'roof', 0)
    C.box('Roof hatch', (16.0, 10.0, ROOF + .40), (1.4, 1.2, .80), 'pale', 'roof', 0)
    C.box('Roof hatch lid', (16.0, 10.0, ROOF + .83), (1.5, 1.3, .06), 'trim', 'roof', 0)



def floors():
    C.box('Ground slab', (0, 0, G0 / 2), (W, D, G0), 'foundation', 'foundation', 0)
    C.box('Apron paving', (4.0, FRONT_Y - APRON / 2, .0075), (58.0, APRON, .015), 'foundation', 'apron', 0)
    C.box('West walk', (WEST_X - 3.0, 0, .0075), (6.0, D, .015), 'foundation', 'apron', 0)
    C.box('Lawn panel', (WEST_X - 9.0, 2.0, .006), (6.0, 20.0, .012), 'planting', 'landscape', 0)
    C.box('Lawn panel', (-14.0, FRONT_Y - 14.0, .021), (10.0, 4.0, .012), 'planting', 'landscape', 0)
    C.box('Lawn panel', (24.0, FRONT_Y - 14.0, .021), (10.0, 6.0, .012), 'planting', 'landscape', 0)
    fy0, fy1 = FRONT_Y + SETBACK + T, REAR_Y - T
    upper = C.box('Upper floor', (0, (fy0 + fy1) / 2, U - .075), (W - 2 * T, fy1 - fy0, .15), 'floor', 'occupied floors', 0)
    y_end = 2.0 + 5.2
    C.cut_box(upper, 'Stair aperture', (-18.0, y_end - 1.9, U), (1.4, 3.6, .6))
    C.railing('Stair guard', (-17.2, y_end - 3.7, U), (-17.2, y_end - .1, U), height=1.02, spacing=.30, role='hardware')
    C.railing('Stair end guard', (-17.2, y_end - .1, U), (-18.8, y_end - .1, U), height=1.02, spacing=.30, role='hardware')
    G.stair('Hall to dormitory stair', -18.0, 2.0, G0, U, length=5.2, width=1.2, landing_gap=.12)
    # Hall partition between the apparatus bays and the watch room / stair hall.
    f = C.Face((-7.0, 0, 0), (0, 1, 0), (1, 0, 0), 'hall partition')
    ph = [hole('Partition door', -8.0, G0, 1.4, 2.4), hole('Partition window', -2.0, 1.0, 4.0, 2.2)]
    f.wall('Hall partition carrier', -12.0, 14.0, G0, U - .25, depth=.20, holes=ph)
    for h in ph:
        lined(f, h, inset=.10, role='pale')


def appliance(x, y0, z=G0):
    """Fire appliance read through the bay glazing: red body, cab, pale ladder and hose bed, six wheels."""
    C.box('Appliance body', (x, y0 + 4.9, z + 1.9), (2.5, 6.6, 2.6), 'red', 'appliances', 0)
    C.box('Appliance cab', (x, y0 + 1.3, z + 1.75), (2.5, 2.6, 2.3), 'red', 'appliances', 0)
    C.box('Cab windscreen', (x, y0 + .02, z + 2.2), (2.1, .03, .9), 'glass', 'appliances', 0)
    C.box('Appliance ladder', (x, y0 + 5.2, z + 3.35), (.9, 6.0, .25), 'pale', 'appliances', 0)
    C.box('Appliance bumper', (x, y0 + .05, z + .5), (2.5, .20, .35), 'pale', 'appliances', 0)
    for dy in (1.2, 5.6, 7.0):
        for s in (-1, 1):
            C.rod('Appliance wheel', (x + s * 1.1, y0 + dy, z + .55), (x + s * 1.35, y0 + dy, z + .55), .55, 'hardware', 'appliances', 12)
    C.box('Appliance stripe', (x, y0 + 4.9, z + 1.2), (2.52, 6.0, .25), 'white', 'appliances', 0)


def forecourt():
    for u in BAYS:
        for s in (-1, 1):
            C.rod('Bay bollard', (u + s * (BAY_W / 2 + .3), GY - 1.2, 0), (u + s * (BAY_W / 2 + .3), GY - 1.2, 1.0), .11, 'red', 'bollards', 10)
    C.rod('Flagpole', (-10.0, FRONT_Y - 7.0, 0), (-10.0, FRONT_Y - 7.0, 12.0), .07, 'pale', 'forecourt', 10)
    C.box('Flagpole base', (-10.0, FRONT_Y - 7.0, .20), (.8, .8, .40), 'stone', 'forecourt', 0)
    C.box('Memorial wall', (-16.0, FRONT_Y - 11.0, 1.1), (8.0, .45, 2.2), 'stone', 'forecourt', 0)
    C.box('Memorial plaque', (-16.0, FRONT_Y - 11.235, 1.2), (6.0, .02, 1.2), 'white', 'forecourt', 0)
    for x, y in ((-10.0, FRONT_Y - 8.0), (-6.0, FRONT_Y - 12.0), (4.0, FRONT_Y - 15.0)):
        C.box('Bench seat', (x, y, .45), (1.8, .5, .08), 'timber', 'forecourt', 0)
        for dx in (-.7, .7):
            C.box('Bench leg', (x + dx, y, .21), (.1, .45, .42), 'hardware', 'forecourt', 0)
    # Flat shelter east of the tower.
    sx, sy = TW_X1 + 3.5, FRONT_Y - 7.0
    C.box('Shelter roof', (sx, sy, 3.1), (6.0, 3.2, .20), 'pale', 'shelter', 0)
    for dx in (-2.7, 2.7):
        for dy in (-1.3, 1.3):
            C.box('Shelter post', (sx + dx, sy + dy, 1.5), (.14, .14, 3.0), 'trim', 'shelter', 0)
    C.box('Shelter bench', (sx, sy + 1.0, .45), (4.0, .45, .08), 'timber', 'shelter', 0)
    for dx in (-1.6, 1.6):
        C.box('Shelter bench leg', (sx + dx, sy + 1.0, .21), (.1, .4, .42), 'hardware', 'shelter', 0)
    A.small_tree(-28.0, FRONT_Y - 10.0, .015, height=5.5, spread=1.1)


def programme():
    for u in BAYS:
        appliance(u, GY + .8)
    for x in (-3.4, 7.8):
        C.qa_room_light('Apparatus hall', (x, -6.0, U - .5), 120, 4.0)
    C.qa_room_light('Watch room', (-14.0, -8.0, U - .5), 80, 3.5)
    for x in (-18.0, -12.0):
        A.desk(x, -9.0, G0)
    A.sofa(-14.0, -3.0, G0)
    for x, y in ((-18.0, -10.0), (-14.0, -10.0), (-10.0, -10.0)):
        A.bed(x, y, U)
    A.sofa(-6.0, -12.0, U)
    for x in (-16.0, -8.0, 4.0):
        C.qa_room_light('Dormitory', (x, -10.0, ROOF - .5), 70, 3.5)
    C.qa_room_light('Tower', ((TW_X0 + TW_X1) / 2, (TW_Y0 + TW_Y1) / 2, 12.5), 50, 2.5)


def build():
    floors()
    f_front, f_right, f_rear, f_left = A.faces(W, D)
    south_upper(f_front)
    south_ground(C.Face((0, GY, 0), (1, 0, 0), (0, 1, 0), 'front ground'))
    west(f_left)
    east(f_right)
    north(f_rear)
    roof()
    tower()
    forecourt()
    programme()
    C.CONTACTS.append(dict(name='Apparatus bay thresholds at slab level on the apron', grade_m=0, bays=4))
    C.CONTACTS.append(dict(name='Cantilever soffit over the bay line with light strip', overhang_m=SETBACK, soffit_m=U - .5))
    C.CONTACTS.append(dict(name='Tower on its own slab tied to the east wall at two levels', grade_m=0))


LIGHT_RIG = dict(key=(-44, -56, 50), fill=(52, -26, 42), rear=(-22, 56, 46), target=(0, -4, 8.0), gain=9.0)
