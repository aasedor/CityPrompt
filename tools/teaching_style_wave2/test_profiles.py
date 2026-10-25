"""Curved openings must stay symmetric, above their spring and non-degenerate."""
import math

import pytest

from tools.teaching_style_wave2.profiles import cusped_arch_curve


def test_cusped_arch_preserves_native_spring_crown_and_symmetry():
    points = cusped_arch_curve(3.0, 2.85, 4.45)
    assert points[0] == (-1.5, 2.85)
    assert points[-1] == (1.5, 2.85)
    assert points[len(points)//2] == (0, 4.45)
    assert len(set(points)) == len(points)
    assert all(math.isfinite(u) and 2.85 <= z <= 4.45 for u,z in points)
    assert all(a[0] == pytest.approx(-b[0]) and a[1] == pytest.approx(b[1])
               for a,b in zip(points,reversed(points)))
    # The wide central high ray must clear a real arch, not its bounding box.
    left = points[:len(points)//2+1]
    assert all(a[1] <= b[1] for a,b in zip(left,left[1:]))
    assert any(-1.0 < u < -.7 and z > 3.65 for u,z in left)


@pytest.mark.parametrize('args',[(0,2,4),(-3,2,4),(3,4,2),(3,2,2)])
def test_invalid_arch_cannot_create_a_degenerate_carrier_cut(args):
    with pytest.raises(ValueError):
        cusped_arch_curve(*args)
