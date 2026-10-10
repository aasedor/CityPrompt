"""Courtyard mixed-use mid-rise, authored from the locked catalogue views of
rndsqr_terraced_mixed_use_midrise / variant_0 (rndsqr_midrise_courtyard).

Read from the pixels: a corner site with streets south and east. Street-level retail with dark
storefronts fills the ground floor; above it a U-plan of three residential storeys in dark
vertically ribbed metal cladding wraps a raised courtyard that opens south and is reached by a
wide concrete stair from the sidewalk. Balconies are recessed into the volumes with cedar-lined
reveals and glass balustrades; windows are tall and black-framed. A set-back penthouse storey
with roof terraces caps the front end of each wing; rooftop units stand on the rear bar.
"""
import clay_core as C
import assemblies as A
import geometry as G

SLUG = 'clay-courtyard-mixed-use-midrise'
X0, X1, Y0, Y1 = -19.0, 19.0, -15.0, 15.0
CX0, CX1, CY1 = -6.0, 6.0, 5.0          # courtyard between the wings, open to the south
T = .30
G0 = .15
L1 = 4.5                                # courtyard deck and first residential level
LEVELS = [L1, L1 + 3.2, L1 + 6.4]
ROOF = L1 + 9.6                         # 14.1
PENT_H = 3.2
RROOF = ROOF + PENT_H                   # 17.3 rear bar roof, level with the wing penthouses
RLEVELS = LEVELS + [ROOF]                # four residential storeys in the rear bar
PENT_Y = (-10.5, -1.0)
SB = 2.0                                # top storey set back from the street face behind a terrace
STAIR_W = 6.0
STAIR_RUN = 7.0
EPS = .002
PALETTE = dict(wall=(.17, .17, .18), joint=(.10, .10, .11), trim=(.08, .08, .09),
    pale=(.70, .68, .64), stone=(.62, .60, .56), roof=(.24, .24, .25), sand=(.60, .56, .50),
    foundation=(.46, .46, .45), glass=(.50, .56, .58), hardware=(.26, .27, .29),
    interior=(.80, .76, .68), floor=(.46, .44, .42), timber=(.62, .42, .22), blue=(.14, .22, .28),
    planting=(.26, .42, .16), soil=(.20, .15, .09), concrete=(.64, .62, .58), cedar=(.66, .44, .22), tan=(.50, .40, .30),
    membrane=(.30, .30, .31))


def manifest(version):
    h = ROOF + PENT_H + 2.5
    cams = G.camera_roster(X1 - X0, Y1 - Y0, h, [
        ('facade_close', (-10.0, -30.0, 6.0), (-12.0, Y0, 8.0), 45),
        ('architecture_close', (26.0, -26.0, 10.0), (X1, Y0, 9.0), 50),
        ('glass_close', (10.0, -22.0, 2.2), (12.0, Y0, 2.4), 50),
        ('courtyard_stair', (0.0, -30.0, 3.0), (0.0, -10.0, 4.0), 45),
        ('retail_corner', (28.0, -24.0, 2.2), (X1, Y0, 2.6), 45),
        ('balcony_close', (-13.5, -26.0, 9.5), (-10.0, Y0, 9.3), 45),
        ('roof_terrace', (-36.0, -34.0, 28.0), (-12.0, -6.0, 15.5), 45),
        ('cladding_contact', (26.0, -24.0, 5.0), (X1, Y0, 5.2), 40),
        ('interior', (-16.8, -5.5, LEVELS[1] + 1.6), (-15.7, Y0 - 1.5, LEVELS[1] + 1.1), 45),
        ('rear_lane', (8.0, 30.0, 6.0), (0.0, Y1, 5.0), 40)])
    return dict(candidate=f'{SLUG}-clay-v{version:03d}', method=C.METHOD,
        archetype_id=SLUG, variant_id=SLUG + '-v1', representation_kind='architectural_clay',
        state='prework', keeper_claimed=False, runtime_seed_allowed=False,
        source_archetype='rndsqr_terraced_mixed_use_midrise/variant_0 (rndsqr_midrise_courtyard)',
        measurement_contract=dict(dimensions_m=dict(width=X1 - X0, depth=Y1 - Y0, height=h),
            observed_storeys=5, storey_programme='street retail; four residential storeys in the wings and the rear bar around a raised courtyard, the top storey tan and set back from the street',
            plan='38 x 30 m read from the top view (560 x 440 px at 0.068 m/px); wings 13 m wide; courtyard 12 x 20 m open to the south; rear bar 10 m deep and one storey taller than the wings, its roof level with the wing penthouses',
            facade='dark vertically ribbed metal panels; floor-to-ceiling black-framed windows; one recessed cedar-lined balcony per wing face per storey with a glass balustrade; tan rear bar with continuous courtyard balconies and a tan top storey; storefronts at street level; wide concrete stair 6 m wide rising 4.5 m to the courtyard',
            levels_m=[G0] + RLEVELS, roof_m=ROOF, rear_bar_roof_m=RROOF, penthouse_m=ROOF + PENT_H,
            roof='one flat membrane plane round the U at 17.3 m over a full-length tan top storey on each wing, set back 2 m behind a street terrace; mechanical screens on the roof',
            inferred='the north and west faces are not visible in any source and repeat the grammar; interiors are teaching assumptions'),
        roof_contract=dict(type='flat membranes behind low parapets; penthouses on the wing roofs; terraces with glass rails', datum_m=ROOF, crowns_m=[ROOF + PENT_H, ROOF + PENT_H + .6, RROOF + .5]),
        identity_contract=dict(owner='dark ribbed U-plan over street retail, raised courtyard with the wide street stair, cedar-lined recessed balconies, tan set-back top storey with street terraces'),
        material_contract=dict(profile='source-palette clay: charcoal ribbed metal panels, cedar reveals, black frames, clear glass balustrades, board-formed concrete stair and base', textured_keeper=False),
        programme_contract=dict(storeys=5, ground='retail and cafe units along the street faces, residential lobby beside the stair', upper='apartments in two wings and a rear bar around the courtyard', roof='penthouse apartments with terraces'),
        contact_contract=['Grade-zero slab and sidewalks', 'Stair from the sidewalk to the courtyard deck in a concrete slot', 'Courtyard deck over the retail floor', 'Balcony plates within the wing volumes', 'Penthouses on the wing roof slabs'],
        runtime_contract=dict(scale='fixed_native_only', installation='not installed', review='NOT TESTED'),
        camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])


def hole(name, u, z, w, h, **kw):
    return dict(id=name, u=u, z=z, w=w, h=h, **kw)


class Merge:
    def __init__(self, f):
        self.f = f; self.groups = {}

    def box(self, role, u, d, z, w, t, h):
        vs, fs = self.groups.setdefault(role, ([], []))
        o = len(vs)
        vs.extend(self.f.p(u + du * w / 2, d + dd * t / 2, z + dz * h / 2) for dz in (-1, 1) for du, dd in ((-1, -1), (1, -1), (1, 1), (-1, 1)))
        fs.extend(tuple(o + i for i in face) for face in C.BOX_FACES)

    def quad(self, role, u, d, z, w, h):
        vs, fs = self.groups.setdefault(role, ([], []))
        o = len(vs)
        vs.extend([self.f.p(u - w / 2, d, z - h / 2), self.f.p(u + w / 2, d, z - h / 2), self.f.p(u + w / 2, d, z + h / 2), self.f.p(u - w / 2, d, z + h / 2)])
        fs.append((o, o + 1, o + 2, o + 3))

    def flush(self, module):
        for role, (vs, fs) in self.groups.items():
            if fs:
                C.mesh(f'{self.f.label} {module} {role}', vs, fs, role, module)
        self.groups = {}


def register(f, h, inset, kind, occupied):
    C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind=kind, clear_wall_cut=True,
        carrier_depth_m=T, frame_inset_m=inset, pane_inset_m=inset + .037, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space=occupied))


def framed(m, f, h, cols=1, rows=1, inset=.12, occupied='apartment', kind='window'):
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    per = .07
    for s in (-1, 1):
        m.box('trim', u + s * (w / 2 - per / 2), inset, z + hh / 2, per, .10, hh)
    m.box('trim', u, inset, z + hh - per / 2, w - 2 * per, .10, per)
    m.box('trim', u, inset, z + per / 2, w - 2 * per, .10, per)
    for i in range(1, cols):
        m.box('trim', u - w / 2 + w * i / cols, inset - .006, z + hh / 2, .05, .09, hh - 2 * per)
    for i in range(1, rows):
        m.box('trim', u, inset - .008, z + hh * i / rows, w - 2 * per, .085, .05)
    m.box('glass', u, inset + .037, z + hh / 2, w - 2 * per - .01, .009, hh - 2 * per - .01)
    register(f, h, inset, kind, occupied)


def balcony(m, f, h, depth=1.9):
    """Recessed balcony: cedar-lined back wall, soffit and cheeks behind the cut, glass balustrade in the face plane."""
    u, z, w, hh = h['u'], h['z'], h['w'], h['h']
    m.box('cedar', u, depth + .05, z + hh / 2, w + .30, .10, hh + .25)
    m.box('cedar', u, depth / 2 + .05, z + hh + .04, w + .30, depth + .10, .08)
    for s in (-1, 1):
        m.box('cedar', u + s * (w / 2 + .10), depth / 2 + .05, z + hh / 2, .08, depth + .10, hh + .25)
    m.box('concrete', u, depth / 2 - .03, z - .04, w + .30, depth + .16, .16)
    m.box('glass', u, .08, z + .6, w - .04, .02, 1.08)
    m.box('hardware', u, .08, z + 1.16, w, .06, .05)
    # Glazed double door at the back of the balcony: black jambs, head and centre mullion proud of the cedar, pale glass behind.
    dw, dh = 2.4, hh - .35
    for e in (-1, 1):
        m.box('trim', u + e * (dw / 2 - .04), depth - .04, z + dh / 2, .08, .10, dh)
    m.box('trim', u, depth - .04, z + dh - .04, dw - .16, .10, .08)
    m.box('trim', u, depth - .03, z + dh / 2, .06, .08, dh - .16)
    m.box('trim', u, depth - .02, z + .06, dw - .16, .06, .12)
    m.box('glass', u, depth + .02, z + dh / 2, dw - .16, .01, dh - .16)
    C.OPENINGS.append(dict(id=h['id'], face=f.label, u=u, z=z, width=w, height=hh, kind='recessed balcony', clear_wall_cut=True,
        carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='balcony opening onto the living room'))


def ribbed_face(f, lo, hi, z0, z1, pattern, holes_extra=(), module='upper', role='wall', ribs=True, levels=LEVELS):
    """Residential elevation from z0 to z1: per storey, the pattern lists (u, kind, width) with kind window or balcony."""
    holes = list(holes_extra)
    for k, zl in enumerate(levels):
        for j, (u, kind, w) in enumerate(pattern):
            if kind == 'balcony':
                holes.append(hole(f'{f.label} balcony {k}-{j}', u, zl + .15, w, 2.75, kind='balcony'))
            else:
                holes.append(hole(f'{f.label} window {k}-{j}', u, zl + .25, w, 2.55))
    f.wall(f'{f.label} {module} carrier', lo, hi - EPS, z0, z1, depth=T, role=role, holes=holes)
    m = Merge(f)
    for h in holes:
        if h.get('kind') == 'balcony':
            balcony(m, f, h)
        else:
            framed(m, f, h, cols=2)
    # Vertical ribs on the dark panels: thin recessed lines between the openings.
    u = lo + .25
    while ribs and u < hi - .25:
        for a, b in G.subtract_openings(u - .01, u + .01, z0 + .1, z1 - .1, holes) if False else [(u, u)]:
            pass
        spans = [(z0 + .1, z1 - .1)]
        for h in holes:
            if h['u'] - h['w'] / 2 - .02 < u < h['u'] + h['w'] / 2 + .02:
                spans = [s for a, b in spans for s in ((a, min(b, h['z'] - .30)), (max(a, h['z'] + h['h'] + .05), b)) if s[1] - s[0] > .05]
        for a, b in spans:
            m.quad('joint', u, -.004, (a + b) / 2, .03, b - a)
        u += .45
    m.flush(module)


def ground_face(f, lo, hi, kind='shops', stair=False, corner_only=False):
    """Street-level elevation: storefronts between dark piers; stair slot at the front centre; service on the lane."""
    span = hi - lo
    holes = []
    if kind == 'party':
        pass
    elif kind == 'shops':
        n = max(2, int(span // 6.0))
        for i in range(n):
            c = lo + span * (i + .5) / n
            if stair and abs(c) < STAIR_W / 2 + 2.0:
                continue
            if corner_only and i > 0:
                if i == 1:
                    holes.append(hole(f'{f.label} lobby door', c, G0, 1.8, 2.8, kind='lobby'))
                elif i % 2 == 0:
                    holes.append(hole(f'{f.label} ground window {i}', c, 1.2, 2.0, 2.0))
                continue
            holes.append(hole(f'{f.label} storefront {i}', c, G0, span / n - 1.4, L1 - .9, kind='shop'))
        if stair:
            holes.append(hole(f'{f.label} stair slot', 0.0, G0, STAIR_W + .4, L1 - .3 - G0 + .2, kind='slot'))
    else:
        holes.append(hole(f'{f.label} loading door', (lo + hi) / 2 + 4.0, G0, 3.4, 3.6, kind='door'))
        holes.append(hole(f'{f.label} lobby window', (lo + hi) / 2 - 6.0, 1.0, 3.0, 2.2))
    f.wall(f'{f.label} ground carrier', lo, hi - EPS, G0, L1 - .3, depth=T, holes=holes)
    m = Merge(f)
    for h in holes:
        if h.get('kind') == 'shop':
            framed(m, f, h, cols=3, inset=.14, occupied='retail unit', kind='storefront')
        elif h.get('kind') == 'door':
            m.box('pale', h['u'], .22, h['z'] + h['h'] / 2, h['w'] - .06, .05, h['h'] - .02)
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='roll-up door', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=.19, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='loading'))
        elif h.get('kind') == 'lobby':
            framed(m, f, h, cols=2, occupied='residential lobby', kind='glazed door')
        elif h.get('kind') == 'slot':
            C.OPENINGS.append(dict(id=h['id'], face=f.label, u=h['u'], z=h['z'], width=h['w'], height=h['h'], kind='open stair slot', clear_wall_cut=True,
                carrier_depth_m=T, frame_inset_m=None, pane_inset_m=None, face_origin=list(f.o), face_tangent=list(f.t), face_inward=list(f.n), occupied_space='open-air stair to the courtyard'))
        else:
            framed(m, f, h, cols=2, occupied='residential lobby')
    if kind == 'shops' and not corner_only:
        # Dark fascia band over the storefronts; it stops either side of the open stair slot so the stair is never roofed.
        segs = [(lo, -STAIR_W / 2 - .3), (STAIR_W / 2 + .3, hi)] if stair else [(lo, hi)]
        for a, b in segs:
            m.box('trim', (a + b) / 2, -.20, L1 - .55, b - a - 2 * EPS, .40, .30)
    m.flush('ground')


def stair_and_courtyard():
    # Concrete stair slot from the sidewalk to the courtyard deck.
    y0 = Y0; y1 = Y0 + STAIR_RUN
    rise = L1
    steps = 24
    profile = [(y0 - .02, .015)]
    for i in range(1, steps + 1):
        yy = y0 + STAIR_RUN * (i - 1) / steps; yn = y0 + STAIR_RUN * i / steps
        profile.append((yy, rise * i / steps)); profile.append((yn, rise * i / steps))
    profile.append((y1 + .6, rise)); profile.append((y1 + .6, .015))
    C.prism('Courtyard stair', profile, 'x', -STAIR_W / 2, STAIR_W / 2, 'concrete', 'stair')
    for s in (-1, 1):
        C.box('Stair cheek wall', (s * (STAIR_W / 2 + .15), (y0 + y1) / 2 + .3 + (T + .01) / 2, (G0 + L1) / 2), (.30, STAIR_RUN + .6 - T - .01, L1 - G0), 'concrete', 'stair', 0)
        C.railing('Stair handrail', (s * (STAIR_W / 2 - .3), y0 + .2, .9), (s * (STAIR_W / 2 - .3), y1, L1 + .9), height=.0, spacing=1.2, role='hardware')
    C.box('Stair landing', (0, y1 + 1.2 + EPS, L1 - .05), (STAIR_W, 1.2 - 2 * EPS, .10), 'concrete', 'stair', 0)
    C.CONTACTS.append(dict(name='Stair of 24 risers from the sidewalk to the courtyard deck inside concrete cheek walls', grade_m=0, rise_m=L1))
    # Courtyard deck over the retail floor, planters, benches, glass rail at the street edge.
    ys = Y0 + STAIR_RUN + 1.8
    C.box('Courtyard deck', ((CX0 + CX1) / 2, (ys + CY1) / 2, L1 - .15), (CX1 - CX0, CY1 - ys, .30), 'floor', 'courtyard', 0)
    for sgn in (-1, 1):
        C.box('Courtyard deck wing', (sgn * (STAIR_W / 2 + .3 + (CX1 - STAIR_W / 2 - .3) / 2), (Y0 + ys) / 2, L1 - .15), (CX1 - STAIR_W / 2 - .3, ys - Y0, .30), 'floor', 'courtyard', 0)
    C.box('Courtyard paving', ((CX0 + CX1) / 2, (Y0 + STAIR_RUN + 1.8 + CY1) / 2, L1 + .004), (CX1 - CX0 - .1, CY1 - Y0 - STAIR_RUN - 1.8, .008), 'sand', 'courtyard', 0)
    for s in (-1, 1):
        C.box('Deck edge paving', (s * (STAIR_W / 2 + .3 + (CX1 - STAIR_W / 2 - .3) / 2), (Y0 + Y0 + STAIR_RUN + 1.8) / 2, L1 + .004), (CX1 - STAIR_W / 2 - .3, STAIR_RUN + 1.8, .008), 'sand', 'courtyard', 0)
        C.box('Street-edge planter', (s * (STAIR_W / 2 + 1.7), Y0 + .9, L1 + .35), (2.6, 1.4, .70), 'concrete', 'courtyard', 0)
        C.box('Street-edge planting', (s * (STAIR_W / 2 + 1.7), Y0 + .9, L1 + .72), (2.4, 1.2, .06), 'planting', 'courtyard', 0)
        C.box('Deck glass rail', (s * (STAIR_W / 2 + 1.7), Y0 + .12, L1 + .6), (2.8, .02, 1.1), 'glass', 'courtyard', 0)
        C.box('Deck rail cap', (s * (STAIR_W / 2 + 1.7), Y0 + .12, L1 + 1.16), (2.8, .06, .05), 'hardware', 'courtyard', 0)
    for x, y in ((-3.5, -3.0), (3.5, -3.0)):
        C.box('Courtyard planter', (x, y, L1 + .3), (2.4, 2.4, .60), 'timber', 'courtyard', 0)
        C.box('Courtyard planter soil', (x, y, L1 + .62), (2.2, 2.2, .04), 'soil', 'courtyard', 0)
    A.small_tree(-3.5, -3.0, L1 + .6, 4.5) if hasattr(A, 'small_tree') else A.shrub(-3.5, -3.0, L1 + .6, 1.4)
    A.shrub(3.5, -3.0, L1 + .62, 1.0)
    for y in (0.0, 2.5):
        C.box('Courtyard bench', (0.0, y, L1 + .22), (2.2, .5, .44), 'timber', 'courtyard', 0)
    C.box('Courtyard table', (-1.0, 3.5, L1 + .38), (1.4, .8, .76), 'timber', 'courtyard', 0)


def volumes():
    C.box('Ground slab', (0, 0, G0 / 2), (X1 - X0, Y1 - Y0, G0), 'foundation', 'foundation', 0)
    for name, (x0, x1, y0, y1) in (('west', (X0 + T, CX0, Y0 + T, Y1 - T)), ('east', (CX1, X1 - T, Y0 + T, Y1 - T)), ('rear', (CX0, CX1, CY1, Y1 - T))):
        C.box(f'{name} retail ceiling', ((x0 + x1) / 2, (y0 + y1) / 2, L1 - .15), (x1 - x0, y1 - y0, .30), 'floor', 'occupied floors', 0)
    for x in (-12.0, 0.0, 12.0):
        C.qa_room_light(f'Retail {x:+.0f}', (x, Y0 + 5.0, L1 - .7), 100, 6.0)
    # Wings and rear bar: floor plates, roofs, penthouses, parapets.
    blocks = {'west': (X0, CX0, Y0, Y1), 'east': (CX1, X1, Y0, Y1), 'rear': (CX0, CX1, CY1, Y1)}
    for name, (x0, x1, y0, y1) in blocks.items():
        rear = name == 'rear'
        lv, rf = (RLEVELS, RROOF) if rear else (LEVELS, ROOF)
        for zl in lv[1:]:
            C.box(f'{name} floor {zl:.1f}', ((x0 + x1) / 2, (y0 + y1) / 2, zl - .13), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .26), 'floor', 'occupied floors', 0)
        C.box(f'{name} roof slab', ((x0 + x1) / 2, (y0 + y1) / 2, rf - .12), (x1 - x0 - 2 * T, y1 - y0 - 2 * T, .24), 'floor', 'roof', 0)
        C.box(f'{name} membrane', ((x0 + x1) / 2, (y0 + y1) / 2, rf + .004), (x1 - x0 - 2 * T - .02, y1 - y0 - 2 * T - .02, .008), 'membrane', 'roof', 0)
        for zl in lv:
            C.qa_room_light(f'{name} apartments {zl:.1f}', ((x0 + x1) / 2, (y0 + y1) / 2 if name == 'rear' else y0 + 6.0, zl + 2.7), 70, 4.5)
    # Top storey of each wing: full wing length at the rear-bar roof level, tan with large windows, set back 2 m from the
    # street face behind a terrace, flush with the outer and courtyard faces (carriers built in build()).
    for name, (x0, x1) in (('west', (X0, CX0)), ('east', (CX1, X1))):
        C.box(f'{name} top roof slab', ((x0 + x1) / 2, (Y0 + SB + Y1) / 2, RROOF - .12), (x1 - x0 - 2 * T, Y1 - Y0 - SB - 2 * T, .24), 'floor', 'roof', 0)
        C.box(f'{name} top membrane', ((x0 + x1) / 2, (Y0 + SB + Y1) / 2, RROOF + .004), (x1 - x0 - 2 * T - .02, Y1 - Y0 - SB - 2 * T - .02, .008), 'membrane', 'roof', 0)
        C.qa_room_light(f'{name} top apartments', ((x0 + x1) / 2, 0.0, ROOF + 2.7), 70, 4.5)
        # Street terrace in front of the top storey: pavers and a glass guard just inside the parapet.
        C.box(f'{name} terrace pavers', ((x0 + x1) / 2, Y0 + T + (SB - T) / 2, ROOF + .012), (x1 - x0 - 2 * T - .1, SB - T - .05, .024), 'sand', 'terrace', 0)
        glass_rail((x0 + T + .2, Y0 + T + .25), (x1 - T - .2, Y0 + T + .25), ROOF)
    for x, y, w, d, zr in ((-1.0, 10.5, 7.0, 3.2, RROOF), (13.5, 10.0, 5.0, 3.0, RROOF), (-13.5, 9.0, 4.0, 3.0, RROOF)):
        C.box('Mechanical enclosure', (x, y, zr + .02 + 1.2), (w, d, 2.4), 'wall', 'rooftop plant', 0)
        for k in range(5):
            C.box('Enclosure louvre', (x, y - d / 2 - .02, zr + .5 + k * .4), (w - .3, .04, .06), 'hardware', 'rooftop plant', 0)
    for x, y, zr in ((3.0, 12.5, RROOF), (4.4, 12.5, RROOF), (-8.0, 12.5, RROOF), (-9.4, 12.5, RROOF), (16.0, 5.0, RROOF), (16.0, 6.4, RROOF)):
        C.box('Condenser', (x, y, zr + .02 + .45), (1.0, 1.0, .9), 'hardware', 'rooftop plant', 0)
    zl = LEVELS[1]
    A.sofa(-16.5, Y0 + 3.5, zl); A.bed(-16.0, Y0 + 12.5, zl)
    C.box('Apartment partition', (-12.0, Y0 + 10.5, zl + 1.5), (10.0, .16, 3.0), 'interior', 'partitions', 0)


def rear_bar_balconies(f):
    """Continuous full-width balconies with glass rails on every level of the rear bar's courtyard face."""
    span = CX1 - CX0 - 2 * T
    m = Merge(f)
    for zl in RLEVELS:
        m.box('trim', 0.0, -.70, zl - .06, span - .2, 1.6, .18)
        m.box('glass', 0.0, -1.45, zl + .03 + .55, span - .3, .02, 1.05)
        m.box('hardware', 0.0, -1.45, zl + .03 + 1.1 + .03, span - .26, .06, .05)
        for e in (-1, 1):
            m.box('glass', e * (span / 2 - .12), -.72, zl + .03 + .55, .02, 1.42, 1.05)
    m.flush('rear bar balconies')


def glass_rail(a, b, z, height=1.1):
    ax, ay = a; bx, by = b
    length = ((bx - ax) ** 2 + (by - ay) ** 2) ** .5
    if length < .2:
        return
    tx, ty = (bx - ax) / length, (by - ay) / length
    f = C.Face(((ax + bx) / 2, (ay + by) / 2, 0), (tx, ty, 0), (-ty, tx, 0), 'rail')
    f.part('Terrace glass rail', 0, 0, z + height / 2 + .05, length, .02, height - .05, 'glass', 'terrace rails', 0)
    f.part('Terrace rail cap', 0, 0, z + height + .08, length, .06, .05, 'hardware', 'terrace rails', 0)


def site():
    ext = 6.0
    C.box('South sidewalk', (0, Y0 - ext / 2, .0075), (X1 - X0 + 2 * ext, ext, .015), 'foundation', 'sidewalk', 0)
    C.box('East sidewalk', (X1 + ext / 2, 0, .0075), (ext, Y1 - Y0, .015), 'foundation', 'sidewalk', 0)
    C.box('Kerb south', (0, Y0 - ext + .06, .06), (X1 - X0 + 2 * ext, .12, .12), 'stone', 'sidewalk', 0)
    C.box('Kerb east', (X1 + ext - .06, 0, .06), (.12, Y1 - Y0, .12), 'stone', 'sidewalk', 0)
    C.box('Rear lane', (0, Y1 + 3.0, .0075), (X1 - X0 + 2 * ext, 6.0, .015), 'foundation', 'lane', 0)
    C.box('West lot', (X0 - 3.0, 0, .0075), (6.0, Y1 - Y0, .015), 'foundation', 'lane', 0)
    for x in (-14.0, -8.0, 9.0, 15.0):
        street_tree(x, Y0 - 3.6, height=5.0, spread=1.1)


def street_tree(x, y, z=.015, height=7.0, spread=1.5):
    C.rod('Street tree trunk', (x, y, z), (x, y, z + height * .55), .12, 'timber', 'street planting', 8)
    for dx, dy in ((-.5, -.2), (.5, -.1), (.0, .5)):
        tip = (x + dx * spread, y + dy * spread, z + height * .72)
        C.rod('Street tree branch', (x, y, z + height * .5), tip, .05, 'timber', 'street planting', 6)
        A.foliage('Street tree crown', tip, (.9 * spread, .9 * spread, 1.2), detail=1)


def build():
    site()
    volumes()
    stair_and_courtyard()
    south = C.Face((0, Y0, 0), (1, 0, 0), (0, 1, 0), 'south')
    east = C.Face((X1, 0, 0), (0, 1, 0), (-1, 0, 0), 'east')
    north = C.Face((0, Y1, 0), (-1, 0, 0), (0, -1, 0), 'north')
    west = C.Face((X0, 0, 0), (0, -1, 0), (1, 0, 0), 'west')
    hw, hd = (X1 - X0) / 2, (Y1 - Y0) / 2
    ground_face(south, -hw, hw, 'shops', stair=True)
    ground_face(east, -hd + T, hd - T, 'shops', corner_only=True)
    ground_face(west, -hd + T, hd - T, 'party')
    ground_face(north, -hw, hw, 'lane')
    # Upper storeys: wing fronts (south), outer faces, north, and the three courtyard faces.
    z0, z1 = L1 - .30 + EPS, ROOF + .5
    ribbed_face(south, -hw, CX0, z0, z1, [(-17.6, 'window', 1.3), (-15.6, 'window', 1.3), (-13.6, 'window', 1.3), (-11.6, 'window', 1.3), (-8.6, 'balcony', 3.2)], module='west wing south')
    C.box('West wing tan end bay', (-6.5, Y0 - .065, (L1 + ROOF) / 2), (.9, .11, ROOF - L1 - .4), 'tan', 'west wing south', 0)
    ribbed_face(south, CX1, hw, z0, z1, [(8.0, 'balcony', 3.2), (14.2, 'window', 5.4)], module='east wing south')
    ribbed_face(west, -hd + T, hd - T, z0, ROOF - .30, [(2.0, 'window', 1.0)], module='west upper', ribs=False)
    ribbed_face(west, -hd + T, hd - SB, ROOF - .30 + EPS, RROOF + .5, [(-6.0, 'window', 2.4), (0.0, 'window', 2.4), (6.0, 'window', 2.4)], module='west top', role='tan', ribs=False, levels=[ROOF])
    ribbed_face(west, hd - SB + EPS, hd - T, ROOF - .30 + EPS, ROOF + .5, [], module='west terrace parapet', ribs=False, levels=[])
    ribbed_face(east, -hd + T, hd - T, z0, ROOF - .30, [(-11.0, 'window', 1.8), (-7.0, 'window', 1.8), (-3.0, 'window', 1.8), (1.0, 'window', 1.8), (5.0, 'window', 1.8), (9.0, 'window', 1.8)], module='east upper', role='tan', ribs=False)
    ribbed_face(east, -hd + SB, hd - T, ROOF - .30 + EPS, RROOF + .5, [(-7.0, 'window', 2.4), (-1.0, 'window', 2.4), (5.0, 'window', 2.4), (10.0, 'window', 1.8)], module='east top', role='tan', ribs=False, levels=[ROOF])
    ribbed_face(east, -hd + T, -hd + SB - EPS, ROOF - .30 + EPS, ROOF + .5, [], module='east terrace parapet', ribs=False, levels=[], role='tan')
    ribbed_face(north, -hw, -CX1 - T, z0, ROOF - .30, [(-14.0, 'window', 1.6), (-9.0, 'window', 2.4)], module='north east wing upper')
    ribbed_face(north, -CX0 + T, hw, z0, ROOF - .30, [(9.0, 'window', 2.4), (14.0, 'window', 1.6)], module='north west wing upper')
    ribbed_face(north, -hw, -CX1 - T, ROOF - .30 + EPS, RROOF + .5, [(-14.0, 'window', 2.4), (-9.0, 'window', 2.4)], module='north east wing top', role='tan', ribs=False, levels=[ROOF])
    ribbed_face(north, -CX0 + T, hw, ROOF - .30 + EPS, RROOF + .5, [(9.0, 'window', 2.4), (14.0, 'window', 2.4)], module='north west wing top', role='tan', ribs=False, levels=[ROOF])
    ribbed_face(north, -CX1 - T, -CX0 + T, z0, ROOF - .30, [(-3.0, 'window', 1.6), (3.0, 'window', 1.6)], module='north rear bar upper')
    ribbed_face(north, -CX1 - T, -CX0 + T, ROOF - .30 + EPS, RROOF + .5, [(-3.0, 'window', 2.4), (3.0, 'window', 2.4)], module='north rear bar top', role='tan', ribs=False, levels=[ROOF])
    # Rear bar side walls above the wing roofs (and the hollow between the wing and rear plates below them).
    for sx, lbl in ((CX0, 'rear bar west side'), (CX1, 'rear bar east side')):
        if sx < 0:
            rs = C.Face((sx - T, (CY1 + Y1) / 2, 0), (0, 1, 0), (1, 0, 0), lbl)
        else:
            rs = C.Face((sx + T, (CY1 + Y1) / 2, 0), (0, -1, 0), (-1, 0, 0), lbl)
        hs = (Y1 - CY1) / 2
        lo_s, hi_s = (-hs, hs - T - EPS) if sx < 0 else (-hs + T, hs - EPS)
        rs.wall(lbl + ' carrier', lo_s, hi_s, z0, ROOF - .30, depth=2 * T, role='tan', holes=[])
    cw = C.Face((CX0, (Y0 + CY1) / 2, 0), (0, 1, 0), (-1, 0, 0), 'courtyard west')
    ce = C.Face((CX1, (Y0 + CY1) / 2, 0), (0, -1, 0), (1, 0, 0), 'courtyard east')
    cr = C.Face(((CX0 + CX1) / 2, CY1, 0), (1, 0, 0), (0, 1, 0), 'courtyard rear')
    hc = (CY1 - Y0) / 2
    ribbed_face(cw, -hc + T, hc - EPS, z0, ROOF - .30, [(-5.5, 'balcony', 3.2), (-1.0, 'window', 1.6), (3.0, 'window', 2.2), (7.0, 'window', 1.6)], module='courtyard west upper')
    ribbed_face(ce, -hc + EPS, hc - T, z0, ROOF - .30, [(-7.0, 'window', 1.6), (-3.0, 'window', 2.2), (1.0, 'window', 1.6), (5.5, 'balcony', 3.2)], module='courtyard east upper')
    ribbed_face(cw, -hc + SB, hc - EPS, ROOF - .30 + EPS, RROOF + .5, [(-2.5, 'window', 2.4), (3.0, 'window', 2.4), (7.5, 'window', 1.8)], module='courtyard west top', role='tan', ribs=False, levels=[ROOF])
    ribbed_face(ce, -hc + EPS, hc - SB, ROOF - .30 + EPS, RROOF + .5, [(-7.5, 'window', 1.8), (-3.0, 'window', 2.4), (2.5, 'window', 2.4)], module='courtyard east top', role='tan', ribs=False, levels=[ROOF])
    ribbed_face(cw, -hc + T, -hc + SB - EPS, ROOF - .30 + EPS, ROOF + .5, [], module='courtyard west terrace parapet', ribs=False, levels=[])
    ribbed_face(ce, hc - SB + EPS, hc - T, ROOF - .30 + EPS, ROOF + .5, [], module='courtyard east terrace parapet', ribs=False, levels=[])
    # Set-back street faces of the top storey, behind the terraces.
    for name, (lo_t, hi_t), pat in (('west', (-hw + T, CX0 - T), [(-15.0, 'window', 3.0), (-10.0, 'window', 3.0)]), ('east', (CX1 + T, hw - T), [(10.0, 'window', 3.0), (15.0, 'window', 3.0)])):
        st = C.Face((0, Y0 + SB, 0), (1, 0, 0), (0, 1, 0), f'{name} top street')
        ribbed_face(st, lo_t, hi_t, ROOF - .30 + EPS, RROOF + .5, pat, module=f'{name} top street', role='tan', ribs=False, levels=[ROOF])
    ribbed_face(cr, -(CX1 - CX0) / 2 + T, (CX1 - CX0) / 2 - T, z0, RROOF + .5, [(-3.8, 'window', 3.2), (0.0, 'window', 3.2), (3.8, 'window', 3.2)], module='courtyard rear upper', role='cedar', ribs=False, levels=RLEVELS)
    rear_bar_balconies(cr)
    C.CONTACTS.append(dict(name='U-plan wings and rear bar bearing on the retail floor; courtyard deck at the first residential level', deck_m=L1))


LIGHT_RIG = dict(key=(-36, -44, 44), fill=(44, -22, 32), rear=(-18, 44, 40), target=(0, -2, 8.0), gain=6.5)
