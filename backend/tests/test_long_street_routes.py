import json
from pathlib import Path

import pytest

from app.services.public_realm_lego import (
    PublicRealmPlanRequest,
    StreetSegmentTarget,
    plan_public_realm_recipe,
    public_realm_recipe_identity,
)
from app.services.native_brt import validate_brt_properties
from app.services.native_tram import validate_tram_properties
from app.services.native_specialist_streets import validate_specialist_properties

PILOTS = json.loads((Path(__file__).resolve().parents[1] / "app/data/nativeStreetPilots.json").read_text())
REPEATABLE = [p for p in PILOTS if p["id"] != "landmark_signature_bridge_v2"]


@pytest.mark.parametrize("pilot", REPEATABLE, ids=lambda p: p["id"])
@pytest.mark.parametrize("length", [508, 2000])
def test_long_native_recipe_roundtrip(pilot, length):
    recipe = plan_public_realm_recipe(
        PublicRealmPlanRequest(
            archetype_id=pilot["sourceArchetypeId"],
            variant_id=pilot["id"],
            target=StreetSegmentTarget(row_width_m=pilot["widthM"], length_m=length),
        )
    )
    assert public_realm_recipe_identity(recipe) is not None
    if pilot.get("programSha256"):
        assert f"program:{pilot['programSha256']}" in recipe.component_set_ids


@pytest.mark.parametrize(
    "variant,parent,width,validator",
    [
        ("brt_bus_rapid_transit_corridor_v0", "brt_bus_rapid_transit_corridor", 40, validate_brt_properties),
        ("student_grass_tram_avenue_v1", "light_rail_tram_avenue", 22, validate_tram_properties),
        ("student_elevated_garden_rail_v1", "elevated_garden_rail", 26, validate_specialist_properties),
        ("skytrain_elevated_corridor_v0", "skytrain_elevated_corridor", 26, validate_specialist_properties),
        ("elevated_rail_transit_corridor_v0", "elevated_rail_transit_corridor", 26, validate_specialist_properties),
    ],
)
def test_long_specialist_server_authoring(variant, parent, width, validator):
    props = dict(
        road_selected_variant_id=variant,
        road_archetype_id=parent,
        width=width,
        road_native_stops=[],
        plan_centerline=[[0, 0], [0, 2000 / 111320]],
    )
    validator(props)
    with pytest.raises(ValueError):
        validator({**props, "plan_centerline": [[0, 0], [0, 2001 / 111320]]})
