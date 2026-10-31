import math

import pytest

from tools.claude_bridge_corrections.geometry_contract import end_louvre_profile, approach_stair_treads


def test_end_slats_leave_the_whole_triangle_below_the_diagonal_open():
    for reverse in (False, True):
        for x in (.3, 1.2, 2.1, 3.7):
            polygon = end_louvre_profile(x - .03, x + .03, 0, 4, 3.75, 6.25, reverse)
            assert polygon is not None
            for px, pz in polygon[:2]:
                fraction = (4 - px) / 4 if reverse else px / 4
                assert pz >= 3.75 + fraction * 2.5 + .08 - 1e-9
            assert polygon[2][1] == polygon[3][1] == 6.25


def test_slats_at_the_high_end_do_not_invert_or_gain_negative_height():
    assert end_louvre_profile(3.9, 3.96, 0, 4, 3.75, 6.25, False) is None
    with pytest.raises(ValueError):
        end_louvre_profile(1, 2, 0, 0, 3.75, 6.25, False)


def test_stairs_connect_grade_to_the_exact_deck_without_excessive_risers():
    steps = approach_stair_treads(15.5, 3.45)
    assert len(steps) == math.ceil(3.45 / .2)
    assert steps[0][0] == 15.5
    assert steps[0][2] == 3.45
    assert steps[-1][2] <= .2
    for current, following in zip(steps, steps[1:]):
        assert current[1] == following[0]
        assert 0 < current[2] - following[2] <= .2 + 1e-9
    assert steps[-1][1] - 15.5 == pytest.approx(len(steps) * .35)
