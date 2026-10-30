import pytest
from tools.claude_bridge_corrections.plant_clearance import disk_inside_convex


def test_shrub_radius_respects_every_sloped_pod_edge():
    polygon = [(7, -5), (18, -2), (18, 6), (7, 10)]
    assert disk_inside_convex(polygon, 12, 2, 1)
    assert not disk_inside_convex(polygon, 17.8, 2, .4)
    assert not disk_inside_convex(polygon, 12, -3.5, 1)
    assert not disk_inside_convex(polygon, 12, 8, 1)
    assert disk_inside_convex(list(reversed(polygon)), 12, 2, 1)


def test_boundary_touch_and_invalid_radius():
    square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    assert disk_inside_convex(square, 1, 1, 1)
    assert not disk_inside_convex(square, .99, 1, 1)
    with pytest.raises(ValueError):
        disk_inside_convex(square, 1, 1, -1)
