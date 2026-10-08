"""Student image renders must not be blocked by advisory junction geometry."""
import uuid

import pytest
from fastapi import HTTPException

from app.api.v1 import direct_3d_render as api
from app.services.native_street_candidate_contract import native_street_runtime_capabilities
from app.services.public_realm_lego import PublicRealmPlanRequest, StreetSegmentTarget, plan_public_realm_recipe
from tests.test_direct_3d_render import (
    _tee_street_zones, _junction_topology, _connected_junction_request,
    _street_junction_request, _compiled_zone, _claims_for,
)


@pytest.mark.parametrize("arms", [3, 4])
def test_registered_narrow_pathways_form_render_junctions(arms):
    tested = 0
    for capability in native_street_runtime_capabilities():
        selection = capability.selections[0]
        width = selection.compatibility.nominal_row_width_m
        if width is None or width >= 5:
            continue
        streets = _tee_street_zones()
        if arms == 4:
            streets[1].properties["plan_centerline"][0] = [-114.08, 51.039]
        recipe = plan_public_realm_recipe(PublicRealmPlanRequest(
            archetype_id=selection.archetype_id, variant_id=selection.variant_id,
            target=StreetSegmentTarget(row_width_m=width, length_m=100),
        ))
        for street in streets:
            street.properties.update(width=width, lane_count=0,
                road_archetype_id=selection.archetype_id, road_selected_variant_id=selection.variant_id,
                public_realm_lego=recipe.model_dump(mode="json"))
        topology = _junction_topology(streets, arms=arms)
        assert api._validate_junction_topology(streets, streets, topology), selection.variant_id
        # Geometry eligibility still requires a real, unchanged catalogue recipe.
        streets[0].properties["public_realm_lego"]["component_set_ids"] = ["invented"]
        assert not api._street_supports_v1_four_way_junction(streets[0])
        tested += 1
    assert tested == 5


@pytest.mark.parametrize("explicit_topology", [False, True])
def test_image_junction_mismatch_is_recorded_without_blocking(explicit_topology):
    streets = _tee_street_zones()
    request = (_connected_junction_request(streets, _junction_topology(streets, arms=4))
               if explicit_topology else _street_junction_request(streets))
    inventory = api._bind_instance_manifest_to_server_zones(
        request, streets, streets, junction_checks_advisory=True)
    junction = next(item for item in inventory if item["zone_id"] is None)
    assert junction["junction_geometry_verified"] is False
    assert "junction_topology" not in junction
    assert len(inventory) == 3
    # The original capture stays intact; only its server interpretation changes.
    if explicit_topology:
        assert next(item for item in request.instance_id_manifest.values() if item.zone_id is None).junction_topology


def test_advisory_junction_check_still_rejects_foreign_project_sources():
    streets = _tee_street_zones()
    request = _street_junction_request(streets, source_zone_ids=[streets[0].id, uuid.uuid4()])
    with pytest.raises(HTTPException, match="no longer part of this project"):
        api._bind_instance_manifest_to_server_zones(request, streets, streets, junction_checks_advisory=True)


def test_verified_image_junction_keeps_topology():
    streets = _tee_street_zones()
    topology = _junction_topology(streets)
    request = _connected_junction_request(streets, topology)
    inventory = api._bind_instance_manifest_to_server_zones(request, streets, streets, junction_checks_advisory=True)
    junction = next(item for item in inventory if item["zone_id"] is None)
    assert junction["junction_geometry_verified"] is True
    assert junction["junction_topology"] == topology.model_dump()


def test_narrow_path_cannot_be_omitted_from_verified_junction():
    from tests.test_direct_3d_render import _zone
    streets = _tee_street_zones()
    recipe = plan_public_realm_recipe(PublicRealmPlanRequest(
        archetype_id="campus_pedestrian_spine", variant_id="concrete_neighbourhood_walk_v1",
        target=StreetSegmentTarget(row_width_m=1.8, length_m=100),
    ))
    fourth = _zone(uuid.uuid4(), "street", properties={
        "width": 1.8, "lane_count": 0, "road_archetype_id": "campus_pedestrian_spine",
        "road_selected_variant_id": "concrete_neighbourhood_walk_v1",
        "public_realm_lego": recipe.model_dump(mode="json"),
        "plan_centerline": [[-114.08, 51.04], [-114.08, 51.039]],
    })
    assert not api._validate_junction_topology(streets, [*streets, fourth], _junction_topology(streets))


def test_image_project_preflight_uses_advisory_junction_checks():
    streets = [_compiled_zone("street"), _compiled_zone("street")]
    request = _street_junction_request(streets)
    payload = request.model_dump()
    payload.update(community_3d_claims=_claims_for(streets), residual_landscape_claim=None)
    request = type(request)(**payload)
    inventory = api._validate_direct_3d_project_zones(request, streets, {})
    junction = next(item for item in inventory if item["zone_id"] is None)
    assert junction["junction_geometry_verified"] is False
