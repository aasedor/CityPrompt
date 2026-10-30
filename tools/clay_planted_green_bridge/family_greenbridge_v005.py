"""Second bounded pass: overlapping foliage, spreading crowns and bounded grass fans."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.claude_bridge_corrections.plant_clearance import disk_inside_convex
from tools.claude_bridge_corrections.geometry_contract import approach_stair_treads
import family_greenbridge as F
import clay_core as C
import geometry as G

PALETTE = dict(F.PALETTE)
LIGHT_RIG = F.LIGHT_RIG
STAIRS = approach_stair_treads(40, F.ZD)
END = STAIRS[-1][1]
WIDTH = 38.8


def manifest(version):
    m = F.manifest(version)
    details = [
        ('facade_close', (34, 3, 6), (11, 3, 5.8), 40),
        ('architecture_close', (-27, -13, 12), (-12, 2, 6), 40),
        # No glass exists here: the mandatory legacy role inspects the inner rail.
        ('glass_close', (0, -10, 8), (3.3, -4, 6.8), 35),
        ('planting_bed', (0, -23, 9), (-4.5, -13, 7), 40),
        ('central_path', (0, -34, 7.7), (0, 0, 7.1), 35),
        ('viewing_pod', (-3, -9, 11), (-12.5, 2.5, 6.4), 35),
        ('pier_column', (-28, -12, 2.2), (-14, -1, 3), 40),
        ('rail_bollard', (0, -17, 7.8), (2.78, -13.5, 6.8), 40),
        ('water_under', (14, -8.5, 1), (0, 4, 4.2), 35),
        ('rear_north', (0, 63, 17), (0, 0, 6), 35),
        ('south_approach', (-15, -55, 10), (0, -43, 3), 35),
        ('north_approach', (15, 55, 10), (0, 43, 3), 35),
    ]
    cams = G.camera_roster(WIDTH, 2 * END, 12, details)
    for c in cams:
        if c['name'] == 'front':
            c.update(location=(0, -32, 12), target=(0, 2, 6.5), lens=24, whole=False)
        elif c['name'] == 'front_corner':
            c.update(location=(0, -40, 21), target=(0, 5, 5.5), lens=28, whole=False)
        elif c['name'] == 'aerial':
            c.update(location=(38, -48, 45), target=(0, 0, 4), lens=28, whole=False)
    m.update(camera_roster=cams, mandatory_review_views=[c['name'] for c in cams])
    m['measurement_contract']['dimensions_m'].update(width=WIDTH, depth=2 * END, height=12)
    m['measurement_contract']['inferred'] = ('Metric scale, compact bank extent, two end abutments and 6 m grade-to-deck stairs are teaching assumptions. '
        'Original river, pods, path/bed proportions, supports, rails and bollards retained. External parking and buildings omitted. No accessibility or engineering claim.')
    m['planting_contract'] = dict(clearance='Every clump envelope stays inside the bed or inset convex pod; threshold corridors excluded',
        composition='Fine bunch/plume grasses, many separate lavender spikes, small red cups, layered green leaf clusters and few multi-stem trees; no solid purple capsule',
        camera_alias='glass_close is the inner-rail inspection; no glazing is present')
    m['contact_contract'] += ['End girders seat on two concrete abutments', 'Two inferred stairs join bridge path to prepared grade']
    m['runtime_contract'].update(scale='fixed_native_only', installation='not installed', review='NOT TESTED',
        ground='prepared level grade only; bounded river and banks with pedestrian stairs',
        unsupported=['stretching', 'bending', 'automatic intersections', 'sloped ground', 'engineering/accessibility certification'])
    return m


def bounded_ground_and_ends():
    C.box('Bounded river', (0, (F.RN + F.RS) / 2, .01), (WIDTH, F.RN - F.RS, .02), 'water', 'river', 0)
    for s, edge in ((1, F.RN), (-1, -F.RS)):
        section = [(edge, 0), (44, 0), (40, F.ZB), (edge + 2.6, F.ZB)]
        if s < 0:
            section = [(-y, z) for y, z in section]
        C.prism('Bounded planted bank', section, 'x', -WIDTH / 2, WIDTH / 2, 'grass', 'banks')
        C.box('Riverside path below deck', (0, s * (edge + 4.7), F.ZB + .015), (WIDTH - .1, 2.6, .05), 'path', 'bank paths', 0)
        C.box('Seated end abutment', (0, s * 39.1, 2), (11, 1.8, 4), 'concrete', 'end abutments', 0)
        for lo, hi, top in STAIRS:
            C.box('Inferred grade approach tread', (0, s * (lo + hi) / 2, top / 2),
                  (2 * F.PW, hi - lo, top), 'path', 'approach stairs', 0)
        for edge_x in (-1, 1):
            x = edge_x * (F.PW + .1)
            C.beam('Approach handrail', (x, s * 40, 7.05), (x, s * END, 1.05), .045, .045, 'rail', 'approach guards')
            for i, (lo, hi, top) in enumerate(STAIRS):
                if i % 3 == 0:
                    y = (lo + hi) / 2
                    rz = 6 * (END - y) / (END - 40) + 1.05
                    C.rod('Approach post', (x, s * y, top), (x, s * y, rz), .025, 'rail', 'approach guards', 8)
    b = F.Batch()
    for s, edge in ((1, F.RN), (-1, -F.RS)):
        for k in range(45):
            f = F.RNG.random()
            F.blob(b, 'rock', F.RNG.uniform(-18.6, 18.6), s * (edge + 2.6 * f), F.ZB * f + .05,
                   .45, .35, .25, j=.15)
    b.flush('bounded riprap')


def leaf_cluster(smooth, x, y, z, radius, height):
    # Broad overlapping crown lobes make an irregular continuous foliage mass.
    for k in range(6):
        angle = k * 2.39996
        r = radius * (.32 if k else 0)
        F.dome(smooth, F.RNG.choice(('planting', 'shrub', 'sage', 'leaf', 'moss')),
               x + r * math.cos(angle), y + r * math.sin(angle),
               z + height * (.16 if k % 2 else .02), radius * .6, radius * .58,
               height * (.55 if k % 2 else .7), seg=10, prof=F.ROUND)


def lavender_spikes(b, smooth, x, y, z, radius):
    leaf_cluster(smooth, x, y, z, radius, .32)
    for k in range(36):
        angle = k * 2.39996
        r = radius * .78 * math.sqrt((k + .5) / 36)
        px, py = x + r * math.cos(angle), y + r * math.sin(angle)
        h = F.RNG.uniform(.48, .75)
        F.fine_blade(b, 'sage', px, py, z + .1, h, angle, .025, .009)
        for j in range(3):
            F.dot(b, F.RNG.choice(('lavender', 'lavspike')), px, py, z + .1 + h - j * .05, .028)


def small_tree(b, smooth, x, y, z, height=3.7):
    for dx, dy in ((-.35, -.15), (.3, .2), (0, -.4)):
        b.beam('timber', (x, y, z), (x + dx, y + dy, z + height * .68), .07)
    # Fewer broad crown lobes; each spread remains within a 1.5 m radius.
    for k in range(7):
        angle = k * 2.39996
        r = .64 * math.sqrt((k + .5) / 7)
        F.dome(smooth, F.RNG.choice(('tree', 'leaf', 'planting')),
               x + r * math.cos(angle), y + r * math.sin(angle),
               z + height * .56 + .25 * math.sin(angle * 2), .72, .7, .95,
               seg=12, prof=F.ROUND)


def bounded_grass(b, x, y, z, radius, height):
    for k in range(22):
        angle = k * 2.39996
        F.fine_blade(b, F.RNG.choice(('grass', 'grass', 'straw')),
                     x, y, z, height * F.RNG.uniform(.75, 1), angle,
                     radius * F.RNG.uniform(.45, .82), .018)


def planting():
    b, smooth = F.Batch(), F.Batch()
    b.smooth = smooth
    z = 6.15

    def clump(x, y, radius, style):
        if style < .22:
            lavender_spikes(b, smooth, x, y, z, radius)
        elif style < .7:
            leaf_cluster(smooth, x, y, z, radius, F.RNG.uniform(.65, 1.6))
        else:
            leaf_cluster(smooth, x, y, z, radius, .42)
            bounded_grass(b, x, y, z + .12, radius, F.RNG.uniform(.9, 1.6))
        if style > .78:
            for k in range(5):
                F.poppy(b, x + F.RNG.uniform(-.2, .2), y + F.RNG.uniform(-.2, .2), z, F.RNG.uniform(.55, .85))

    for s in (-1, 1):
        y = -39
        while y < 39:
            for x, radius in ((3.35, .58), (4.45, .72), (5.6, .7), (6.25, .4)):
                px, py = s * (x + F.RNG.uniform(-.08, .08)), y + F.RNG.uniform(-.28, .28)
                # Threshold stones remain clear from central path into each pod.
                t = (abs(px) - F.PW - .5) / (F.DW - F.PW)
                threshold_y = F.THR[s] + (9.35 - F.THR[s]) * t
                if abs(py - threshold_y) > 1.25:
                    clump(px, py, radius, F.RNG.random())
            y += .85
        for ty in (25,):
            small_tree(b, smooth, s * 4.7, ty, z)
        polygon = F.pod_poly(s)
        x = F.DW + 1.4
        while x < 17:
            y = -3.5
            while y < 8.5:
                if disk_inside_convex(polygon, s * x, y, 1.2):
                    clump(s * x, y, .72, F.RNG.random())
                y += .85
            x += 1.05
        for tx, ty in ((12.5, 2.5),):
            if disk_inside_convex(polygon, s * tx, ty, 1.65):
                small_tree(b, smooth, s * tx, ty, z, 4)
    b.flush('fine grasses flowers and multi-stem trunks')
    F.flush_smooth(smooth, 'layered leaves and individual flower cups')


def build():
    bounded_ground_and_ends()
    F.deck()
    F.pods()
    planting()
    C.CONTACTS.append(dict(name='Bounded planted bridge with seated abutments, clear planting envelopes and grade stairs',
                           box=[-WIDTH / 2, WIDTH / 2, -END, END]))
