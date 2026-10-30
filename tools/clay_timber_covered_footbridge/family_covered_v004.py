"""New bounded correction; the pinned v001-v003 sources/candidates stay intact."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.claude_bridge_corrections.geometry_contract import end_louvre_profile, approach_stair_treads
import family_covered as F
import clay_core as C
import geometry as G

PALETTE = dict(F.PALETTE)
PALETTE['glass'] = (.92, .97, .98)
LIGHT_RIG = F.LIGHT_RIG
HALF_DEPTH = 4.4
STAIRS = approach_stair_treads(F.DX, F.ZD)
HALF_LENGTH = STAIRS[-1][1]


def manifest(version):
    m = F.manifest(version)
    detail = [(c['name'], c['location'], c['target'], c['lens']) for c in m['camera_roster'] if c['name'] in (
        'facade_close', 'architecture_close', 'glass_close', 'portal_end', 'louvre_wall', 'roof_eaves',
        'deck_inside', 'pier_abutment', 'stream_under', 'rear_north')]
    detail += [('west_approach', (-24, -7, 6), (-17, 0, 2), 38),
               ('east_approach', (24, 7, 6), (17, 0, 2), 38)]
    cameras = G.camera_roster(2 * HALF_LENGTH, 2 * HALF_DEPTH, F.EAVE + .8, detail)
    m.update(camera_roster=cameras, mandatory_review_views=[c['name'] for c in cameras])
    m['measurement_contract']['dimensions_m'].update(width=2 * HALF_LENGTH, depth=2 * HALF_DEPTH)
    m['measurement_contract']['plan'] = '31 m timber deck, six covered bays, bounded banks and two inferred grade-to-deck approach stairs; background blocks omitted'
    m['measurement_contract']['inferred'] = 'Compact approach stairs are teaching assumptions outside the locked bridge envelope. No accessibility/engineering certification. Stream terminates at module edges.'
    m['contact_contract'] = ['Piers seated on lower paths', 'Edge beams seated on headstocks/abutments',
                             'Slats terminate above diagonal brace', 'Continuous clear guards through all bays',
                             'Approach treads connect grade to the exact deck datum']
    m['runtime_contract'].update(scale='fixed_native_only', installation='not installed', review='NOT TESTED',
                                 plot='actual occupied envelope plus small placement clearance',
                                 ground='prepared level grade only; stepped approaches, no ramp claim',
                                 unsupported=['resizing', 'terrain deformation', 'automatic road intersections'])
    return m


class CorrectedFrameBatch(F.Batch):
    def box(self, role, x, y, z, w, d, h):
        if role == 'timber' and h > 1.5 and w < .1:
            end = 0 if x < F.FRAMES[1] else len(F.FRAMES) - 2
            left, right = F.FRAMES[end] + .16, F.FRAMES[end + 1] - .16
            profile = end_louvre_profile(x - w / 2, x + w / 2, left, right,
                                          F.ZD + .3, F.EAVE - .5, end != 0)
            if profile:
                C.prism('Diagonal-clipped end-bay timber slat', profile, 'y', y - d / 2, y + d / 2,
                        'timber', 'corrected end-bay louvres')
            return
        # The previous bottom rail closed the triangle even after clipping slats.
        if role == 'glulam' and abs(z - (F.ZD + .2)) < 1e-6 and abs(h - .12) < 1e-6:
            return
        if role == 'glass':
            if abs(x) > 1e-6:
                return  # landing guards become part of the continuous pane
            return super().box(role, 0, y, F.ZD + .565, 2 * F.DX - .1, .012, 1.05)
        if role == 'hardware' and abs(z - (F.ZD + 1.02)) < 1e-6:
            return
        if role == 'hardware' and abs(z - (F.ZD + 1.14)) < 1e-6:
            return super().box(role, 0, y, F.ZD + 1.11, 2 * F.DX - .1, .035, .04)
        return super().box(role, x, y, z, w, d, h)


def compact_ground_and_approaches():
    C.box('Bounded stream beneath bridge', (0, 0, .01), (2 * F.WX, 2 * HALF_DEPTH, .02), 'water', 'stream', 0)
    for side in (-1, 1):
        C.box('Bounded lower riverside path', (side * (F.WX + F.LOWX) / 2, 0, F.LOW / 2),
              (F.LOWX - F.WX, 2 * HALF_DEPTH, F.LOW), 'paving', 'paths', 0)
        section = [(side * F.LOWX, 0), (side * F.BANKX, 0),
                   (side * F.BANKX, F.UP), (side * F.LOWX, F.LOW)]
        C.prism('Bounded planted bank', section, 'y', -HALF_DEPTH, HALF_DEPTH, 'planting', 'banks')
        C.box('Compact upper landing', (side * (F.BANKX + F.DX) / 2, 0, F.UP / 2),
              (F.DX - F.BANKX, 2 * HALF_DEPTH, F.UP), 'paving', 'landings', 0)
        for index, (lo, hi, top) in enumerate(STAIRS):
            C.box(f'Approach stair tread {side} {index}', (side * (lo + hi) / 2, 0, top / 2),
                  (hi - lo, 4, top), 'paving', 'approach stairs', 0)
        for edge in (-1, 1):
            C.beam('Approach stair handrail', (side * F.DX, edge * 2.08, F.ZD + 1.05),
                   (side * HALF_LENGTH, edge * 2.08, 1.05), .045, .045, 'hardware', 'approach guards')
            for index, (lo, hi, top) in enumerate(STAIRS):
                if index % 3:
                    continue
                x = (lo + hi) / 2
                rail_z = F.ZD * (HALF_LENGTH - x) / (HALF_LENGTH - F.DX) + 1.05
                C.rod('Approach guard post', (side * x, edge * 2.08, top),
                      (side * x, edge * 2.08, rail_z), .025, 'hardware', 'approach guards', 8)
            C.beam('Landing outer edge guard', (side * F.BANKX, edge * (HALF_DEPTH - .1), F.UP + 1.05),
                   (side * F.DX, edge * (HALF_DEPTH - .1), F.UP + 1.05), .045, .045, 'hardware', 'landing guards')
            for x in (F.BANKX, (F.BANKX + F.DX) / 2, F.DX):
                C.rod('Landing guard post', (side * x, edge * (HALF_DEPTH - .1), F.UP),
                      (side * x, edge * (HALF_DEPTH - .1), F.UP + 1.05), .025, 'hardware', 'landing guards', 8)


def build():
    glass = C.MATS['glass'].node_tree.nodes.get('Principled BSDF')
    glass.inputs['Alpha'].default_value = .08
    glass.inputs['Transmission Weight'].default_value = .9
    glass.inputs['Roughness'].default_value = .035
    original_batch, y0, y1 = F.Batch, F.Y0, F.Y1
    try:
        F.Batch = CorrectedFrameBatch
        F.Y0, F.Y1 = -HALF_DEPTH, HALF_DEPTH
        compact_ground_and_approaches()
        F.railings()
        F.bridge()
    finally:
        F.Batch, F.Y0, F.Y1 = original_batch, y0, y1
    C.CONTACTS.append(dict(name='Bounded timber bridge with clipped louvres and connected approach stairs',
                           box=[-HALF_LENGTH, HALF_LENGTH, -HALF_DEPTH, HALF_DEPTH]))
