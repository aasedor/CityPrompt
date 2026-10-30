import math
import pytest
from tools.claude_bridge_corrections.tied_arch_plan import trapezoid_plan


def unrotate(point):
    a = math.radians(13)
    x, y = point
    return x * math.cos(a) + y * math.sin(a), -x * math.sin(a) + y * math.cos(a)


def test_opposite_end_skews_and_longer_south_tie():
    for end in (-23, 23):
        a = unrotate(trapezoid_plan(end, -6.15))
        b = unrotate(trapezoid_plan(end, 6.15))
        angle = math.degrees(math.atan2(b[0] - a[0], b[1] - a[1]))
        assert angle == pytest.approx(6 if end < 0 else -6)
    lengths = [math.dist(trapezoid_plan(-23, y), trapezoid_plan(23, y)) for y in (-6.15, 6.15)]
    assert .05 < lengths[0] / lengths[1] - 1 < .07


def test_center_and_cross_width_are_preserved():
    assert trapezoid_plan(0, 0) == (0, 0)
    assert math.dist(trapezoid_plan(0, -6.15), trapezoid_plan(0, 6.15)) == pytest.approx(12.3)
    assert unrotate(trapezoid_plan(0, 6.15)) == pytest.approx((0, 6.15))


def test_degenerate_span_is_rejected():
    with pytest.raises(ValueError):
        trapezoid_plan(1, 1, halfspan=0)
