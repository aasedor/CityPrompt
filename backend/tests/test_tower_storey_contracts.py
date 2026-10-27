import pytest

from app.services.building_flex_contract import trusted_building_footprint_target


CASES = [
    ('clay_blue_glass_office_tower', 'glass_tower_blue_reflective', 'glass_tower_podium_modern-clay-v003',
     'blue-glass-office-storey-program-v001', 25, 99, (32.1200008392334, 30.074999809265137)),
    ('claude_trial_plus15_glass_office_tower', 'plus15_contemporary_glass', 'clay-plus15-glass-office-tower-clay-v006',
     'plus15-glass-office-storey-program-v001', 17, 82.66, (52, 83)),
    ('claude_trial_slab_balcony_tower', 'midcentury_concrete_slab', 'clay-slab-balcony-tower-clay-v007',
     'slab-balcony-storey-program-v001', 13, 47, (37.357473373413086, 37.20000076293945)),
]


def properties(case):
    asset, variant, revision, programme, floors, height, _ = case
    return dict(pick_place_asset=asset, development_selected_variant_id=variant,
                pick_place_model_revision=revision, building_footprint_program_id=programme+'-native-footprint',
                building_footprint_scale=1, floors=floors, floor_count=floors,
                height_m=height, height=height, development_height_override_m=height,
                building_footprint_native_width_m=999, building_footprint_native_depth_m=999)


@pytest.mark.parametrize('case', CASES)
def test_tower_model_target_is_trusted_independently_of_reserved_plot_and_client_claims(case):
    assert trusted_building_footprint_target(properties(case)) == case[-1]


@pytest.mark.parametrize('changes', [
    {'pick_place_asset': 'another_asset'},
    {'development_selected_variant_id': 'another_variant'},
    {'pick_place_model_revision': 'another_revision'},
    {'building_footprint_scale': 1.01},
    {'building_footprint_scale': float('nan')},
    {'floor_count': 41, 'floors': 41},
    {'floor_count': 14, 'floors': 14},
    {'floor_count': 25.5, 'floors': 25.5},
    {'height_m': 120, 'height': 120, 'development_height_override_m': 120},
])
def test_known_tower_programme_rejects_unbound_identity_scale_count_and_height(changes):
    with pytest.raises(ValueError):
        trusted_building_footprint_target({**properties(CASES[0]), **changes})


@pytest.mark.parametrize("floors,height,valid", [(20,79.7,True),(30,113.7,True),(40,147.7,True),(25,96.7,False)])
def test_landmark_rejects_intermediate_unbuilt_choices(floors,height,valid):
    case=("clay_twisting_glass_sky_garden_tower","glass_tower_twisted","glass-tower-twisted-clay-v005",
          "glass_tower_twisted-authored-heights-v001",floors,height,(43.4902229309082,44.0266170501709))
    if valid:
        assert trusted_building_footprint_target(properties(case)) == case[-1]
    else:
        with pytest.raises(ValueError):
            trusted_building_footprint_target(properties(case))
