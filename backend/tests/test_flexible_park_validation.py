from types import SimpleNamespace

import pytest
from shapely.geometry import Polygon

from app.api.v1.site_zones import _validate_flexible_park


def polygon(points):
    return Polygon([(-114 + x / 70_000, 51.12 + y / 111_000) for x, y in points])


PREPARED = SimpleNamespace(properties={'community_3d_mask_existing_tiles': True})
POCKET = {'pick_place_flexible_park': 'pocket-v1', 'green_space_archetype_id': 'urban_pocket_park',
          'green_space_selected_variant_id': 'urban_pocket_park_v0'}
GREENWAY = {'pick_place_flexible_park': 'greenway-v1', 'green_space_archetype_id': 'linear_park_greenway',
            'green_space_selected_variant_id': 'linear_park_greenway_v0'}


@pytest.mark.parametrize('points,properties', [
    ([(0, 0), (35, 0), (35, 12), (20, 12), (20, 32), (0, 32)], POCKET),
    ([(0, 0), (35, 0), (5, 35)], POCKET),
    ([(0, 0), (90, 0), (90, 15), (50, 18), (50, 24), (0, 20)], GREENWAY),
])
def test_flexible_shapes_resolve_complete_recipes(points, properties):
    _validate_flexible_park(polygon(points), properties, PREPARED)


def test_flexible_park_rejects_wrong_identity_unprepared_ground_and_wrong_shape():
    shape = polygon([(0, 0), (35, 0), (35, 12), (20, 12), (20, 32), (0, 32)])
    with pytest.raises(ValueError, match='available flexible park'):
        _validate_flexible_park(shape, {**POCKET, 'green_space_selected_variant_id': 'urban_pocket_park_v3'}, PREPARED)
    with pytest.raises(ValueError, match='Prepare a level site'):
        _validate_flexible_park(shape, POCKET, None)
    with pytest.raises(ValueError, match='supported size or shape'):
        _validate_flexible_park(polygon([(0, 0), (5, 0), (5, 5), (0, 5)]), POCKET, PREPARED)
