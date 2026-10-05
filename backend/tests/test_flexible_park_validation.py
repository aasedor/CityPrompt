from types import SimpleNamespace

import pytest
from shapely.geometry import Polygon

from app.api.v1.site_zones import _validate_flexible_park
from app.services.public_realm_lego import plan_public_realm_zone_recipe


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


@pytest.mark.parametrize('key,variant,appearance,structure', [
    ('shade-courtyard-v1', 'urban_pocket_park_v1', 'modern_steel_turf_v1', 'formal_quad'),
    ('meadow-grove-v1', 'urban_pocket_park_v2', 'natural_meadow_v1', 'naturalistic_grove'),
])
@pytest.mark.parametrize('points', [
    [(0, 0), (35, 0), (35, 12), (20, 12), (20, 32), (0, 32)],
    [(0, 0), (35, 0), (5, 35)],
])
def test_new_programmes_preserve_irregular_outline_and_exact_recipe(key, variant, appearance, structure, points):
    shape = polygon(points)
    properties = {**POCKET, 'pick_place_flexible_park': key, 'green_space_selected_variant_id': variant}
    _validate_flexible_park(shape, properties, PREPARED)
    recipe = plan_public_realm_zone_recipe('green_space', shape, properties, strict=True)
    assert recipe.variant_id == variant
    assert recipe.appearance_kit_id == appearance
    assert recipe.planting_structure == structure
    with pytest.raises(ValueError, match='available flexible park'):
        _validate_flexible_park(shape, {**properties, 'green_space_selected_variant_id': 'urban_pocket_park_v0'}, PREPARED)
    with pytest.raises(ValueError, match='Prepare a level site'):
        _validate_flexible_park(shape, properties, None)
