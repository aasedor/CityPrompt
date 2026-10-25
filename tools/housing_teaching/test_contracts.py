from copy import deepcopy
from pathlib import Path

import pytest

from tools.housing_teaching.contracts import (
    candidate_path, landing_bridge, lock_family_sources, load_cards, roof_datums, split_level_datums, stair_flight, stair_posts, validate_card,
)


def source_set(tmp_path):
    root = tmp_path / 'buildings'
    root.mkdir()
    roles = {}
    for role in ('front', 'oblique', 'top', 'rear_oblique'):
        path = root / f'{role}.png'
        path.write_bytes(b'locked-' + role.encode())
        roles[role] = path
    return root, roles


def test_missing_top_fails_before_build(tmp_path):
    root, roles = source_set(tmp_path)
    del roles['top']
    with pytest.raises(ValueError, match='top'):
        lock_family_sources('house', 'exact', roles, root)


def test_all_available_roles_are_enrolled_and_bound_to_exact_variant(tmp_path):
    root, roles = source_set(tmp_path)
    locked = lock_family_sources('house', 'exact', roles, root)
    assert len(locked) == 4
    assert all(r['archetype_id'] == 'house' and r['variant_id'] == 'exact' for r in locked)
    assert len({r['sha256'] for r in locked}) == 4


def test_sources_outside_authority_cannot_be_substituted(tmp_path):
    root, roles = source_set(tmp_path)
    outside = tmp_path / 'front.png'
    outside.write_bytes(b'other')
    roles['front'] = outside
    with pytest.raises(ValueError, match='authoritative'):
        lock_family_sources('house', 'exact', roles, root)


def test_wrong_family_source_lock_cannot_be_replayed(tmp_path):
    root, roles = source_set(tmp_path)
    locked = lock_family_sources('house', 'exact', roles, root)
    with pytest.raises(ValueError, match='identity'):
        lock_family_sources('house', 'sibling', roles, root, expected=locked)


def test_source_byte_drift_cannot_be_replayed(tmp_path):
    root, roles = source_set(tmp_path)
    locked = lock_family_sources('house', 'exact', roles, root)
    roles['top'].write_bytes(b'secretly-changed-roof')
    with pytest.raises(ValueError, match='changed'):
        lock_family_sources('house', 'exact', roles, root, expected=locked)


def test_existing_candidate_and_escaping_paths_are_preserved(tmp_path):
    batch = tmp_path / 'batch'
    batch.mkdir()
    existing = batch / 'v001'
    existing.mkdir()
    for path, error in ((existing, FileExistsError), (batch, ValueError), (tmp_path / 'other', ValueError)):
        with pytest.raises(error):
            candidate_path(path, batch)
    assert existing.is_dir()


def test_teaching_fields_do_not_invent_tenure_or_build_dates():
    cards = load_cards()
    assert set(cards) == {'victory', 'split'}
    for card in cards.values():
        validate_card(card)
        assert card['constructionYear'] is None
        assert card['tenure'] == 'not_inferred'
        assert card['runtimeActivation'] is False
        assert len(card['lookFor']) == 3
        assert card['planningConnections'] and card['sourceUrls']


@pytest.mark.parametrize('field,value', [('constructionYear', 1947), ('tenure', 'owner_occupied'), ('runtimeActivation', True)])
def test_classification_rejects_unsupported_claims(field, value):
    card = deepcopy(load_cards()['victory'])
    card[field] = value
    with pytest.raises(ValueError):
        validate_card(card)


def test_staggered_flights_land_exactly_and_have_usable_goings():
    up = stair_flight(.48, 1.92, .28)
    down = stair_flight(.48, -.96, .28)
    for flight, end in ((up, 1.92), (down, -.96)):
        assert flight['levels'][-1] == pytest.approx(end)
        assert abs(flight['rise']) <= .18
        assert flight['going'] >= .28
        assert flight['run'] == pytest.approx(flight['steps'] * .28)
    with pytest.raises(ValueError):
        stair_flight(0, 0, .28)


def test_roof_underside_seats_on_complete_gable_without_exposed_carrier():
    roof = roof_datums(3.18, 5.55, 2.75, .22, .13)
    assert roof['ridge_top'] - roof['thickness'] == pytest.approx(5.55)
    wall_top = roof['edge_top'] + roof['slope'] * .22
    assert wall_top - roof['thickness'] == pytest.approx(3.18)
    assert roof['edge_top'] < 3.18


@pytest.mark.parametrize('start_z', [.48, .53])
def test_arrival_bridge_covers_the_slot_when_step_count_changes(start_z):
    flight = stair_flight(start_z, 3.05)
    end = -3.1 + flight['run']
    bridge = landing_bridge(end, 1.23)
    assert bridge['min_x'] < end
    assert bridge['max_x'] > 1.23
    # No missing floor surface anywhere between final tread and the loft floor.
    for x in (end, 1.03, 1.08, 1.13, 1.20, 1.23):
        assert bridge['min_x'] <= x <= bridge['max_x']


def test_split_level_has_occupied_clearance_and_bearing_at_both_arrivals():
    d = split_level_datums()
    assert 0 <= d['lower'] < d['living'] < d['upper']
    assert d['upper'] - d['slab'] - d['lower'] >= 2.10 - 1e-8
    assert d['low_eave'] - d['living'] >= 2.40
    assert d['high_eave'] - d['upper'] >= 2.10
    for name in ('up', 'down'):
        flight = d[name]
        target = d['upper'] if name == 'up' else d['lower']
        assert flight['levels'][-1] == pytest.approx(target)
        assert abs(flight['rise']) <= .18
        assert flight['bridge']['min_x'] < flight['end_x']
        assert flight['bridge']['max_x'] > flight['cut_edge']
    # The descending stair must cut the living slab AND its raised foundation.
    assert d['down']['opening_min_x'] < d['start_x']
    assert d['down']['opening_max_x'] > d['join_x']


@pytest.mark.parametrize('end', [.10, 2.30])
def test_stair_posts_reach_sloping_rail_in_both_directions(end):
    f = stair_flight(.53, end)
    posts = stair_posts(.53, end)
    for p in posts:
        expected_rail = .53 + (end-.53) * (p['step_index']+.5)/f['steps'] + .92
        assert p['bottom_z'] <= f['levels'][p['step_index']]
        assert p['top_z'] >= expected_rail
        assert p['top_z']-expected_rail < .03


def test_split_plan_preserves_source_depth_step_and_rear_door_arrival():
    d = split_level_datums()
    low_depth = d['low_rear']-d['low_front']
    high_depth = d['high_rear']-d['high_front']
    assert 1.30 <= high_depth/low_depth <= 1.40
    assert d['low_front'] == d['high_front']  # retain known front registration
    assert d['low_rear'] < d['high_rear']
    assert d['low_rear']-.25-(d['down_y']+.58) >= .80
