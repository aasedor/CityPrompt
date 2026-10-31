"""Exact-source and research boundaries for the two-house RLASM batch."""
import json
import math
from pathlib import Path

from tools.teaching_style_wave2.contracts import candidate_path, source_lock


def lock_family_sources(archetype_id, variant_id, roles, authoritative_root, expected=None):
    locked = source_lock(archetype_id, variant_id, roles, authoritative_root)
    if expected is not None:
        if len(locked) != len(expected) or any(
            r['archetype_id'] != archetype_id or r['variant_id'] != variant_id for r in expected
        ):
            raise ValueError('Source identity differs from locked exact variant')
        actual = {r['role']: (r['sha256'], r['bytes']) for r in locked}
        prior = {r['role']: (r['sha256'], r['bytes']) for r in expected}
        if actual != prior:
            raise ValueError('Source bytes or enrolled roles changed')
    return locked


def load_cards():
    result = json.loads(Path(__file__).with_name('cards.json').read_text(encoding='utf-8'))
    for card in result.values():
        validate_card(card)
    return result


def validate_card(card):
    required = ('archetypeId', 'variantId', 'title', 'use', 'form', 'aesthetic',
                'designPeriod', 'dateBasis', 'description', 'lookFor',
                'planningConnections', 'sourceUrls')
    if any(not card.get(k) for k in required):
        raise ValueError('Missing individually authored teaching field')
    if card.get('constructionYear') is not None or card['dateBasis'] != 'approximate_design_association':
        raise ValueError('Original teaching designs cannot acquire a historic construction year')
    if card.get('tenure') != 'not_inferred' or card.get('affordability') != 'not_inferred':
        raise ValueError('Tenure and affordability cannot be inferred from appearance')
    if card.get('runtimeActivation') is not False:
        raise ValueError('Research metadata does not activate a runtime model')
    if len(card['lookFor']) != 3 or any(not url.startswith('https://') for url in card['sourceUrls']):
        raise ValueError('Use three visible cues and linked evidence')


def stair_flight(start, end, going=.28):
    """Finite concept stair datums used directly by the exact house builders."""
    if not all(math.isfinite(x) for x in (start, end, going)) or end == start or going < .28:
        raise ValueError('Stair needs distinct finite levels and at least .28m going')
    count = math.ceil(abs(end - start) / .18 - 1e-9)
    rise = (end - start) / count
    return dict(steps=count, rise=rise, going=going, run=count * going,
                levels=[start + rise * (i + 1) for i in range(count)])


def stair_posts(start, end, going=.28):
    """Post tops meet the actual sloped handrail, including descending flights."""
    flight = stair_flight(start, end, going)
    return [dict(step_index=i, x_offset=going*(i+.5),
                 bottom_z=flight['levels'][i]-.02,
                 top_z=start+(end-start)*(i+.5)/flight['steps']+.92+.015)
            for i in sorted({0, flight['steps']//2, flight['steps']-1})]


def roof_datums(wall_eave, wall_ridge, half_span, overhang, thickness):
    """Wall crest owns the roof underside, never its exposed upper surface."""
    if half_span <= 0 or thickness <= 0 or wall_ridge <= wall_eave or overhang < 0:
        raise ValueError('Invalid roof section')
    slope = (wall_ridge - wall_eave) / half_span
    return dict(slope=slope, ridge_top=wall_ridge + thickness,
                edge_top=wall_eave + thickness - slope * overhang, thickness=thickness)


def landing_bridge(last_tread_edge, floor_cut_edge):
    """Cover the entire gap, including positive bearing on tread and loft."""
    lo = min(last_tread_edge, floor_cut_edge) - .08
    hi = max(last_tread_edge, floor_cut_edge) + .12
    return dict(min_x=lo, max_x=hi, center_x=(lo + hi) / 2, length=hi - lo)


def split_level_datums():
    """Declared interior inference; occupied clearances and connected floor cuts.

    The generated reference supplies elevations, not a measured historic plan.
    These unequal offsets keep a full lower room above the native zero datum.
    """
    d = dict(lower=.10, living=.53, upper=2.30, slab=.10, low_eave=3.05,
             high_eave=4.45, start_x=-.70, join_x=.35,
             low_front=-4., low_rear=2., high_front=-4., high_rear=4.,
             low_center_y=-1., low_half_depth=3., down_y=.30)
    for name, target, cut_edge in (('up', d['upper'], 2.33), ('down', d['lower'], .60)):
        f = stair_flight(d['living'], target)
        f.update(end_x=d['start_x'] + f['run'], cut_edge=cut_edge)
        f['bridge'] = landing_bridge(f['end_x'], cut_edge)
        f.update(opening_min_x=d['start_x'] - .03, opening_max_x=cut_edge)
        d[name] = f
    return d
