import copy
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from shapely.geometry import box

from app.schemas.park_access import ParkAccessSnapshot
from app.services.park_access_provenance import PARK_ACCESS_EVIDENCE, bind_park_access_snapshot
from app.services.render_provenance import build_render_source_snapshot
from tests.test_render_fidelity_provenance import _snapshot_inputs


def inputs():
    request, building_zone, building = _snapshot_inputs()
    now = datetime(2026, 9, 5, 0, 3, 34, 431612, tzinfo=timezone.utc)
    building_zone.updated_at = now
    zones = [building_zone]
    for kind in ("green_space", "road", "site_boundary"):
        zones.append(
            SimpleNamespace(
                id=uuid.uuid4(),
                zone_type=kind,
                updated_at=now,
                geometry=box(-114.1, 51, -114.09, 51.01),
                properties={"hidden_barrier": kind == "site_boundary"},
            )
        )
    point = [-114.095, 51.005]
    snapshot = {
        "version": 1,
        "sourceSignature": "client-cache-key-only",
        "settings": {"maxGapM": 8, "pathWidthM": 2.2, "obstacleClearanceM": 0.25, "maxConnections": 2, "gridStepM": 2},
        "eligibleStreetZoneIds": [str(zones[2].id)],
        "sources": [
            {"zoneId": str(zone.id), "updatedAt": now.isoformat(), "geometrySignature": "client-geometry-key"}
            for zone in zones
        ],
        "parks": [
            {
                "parkZoneId": str(zones[1].id),
                "status": "connected",
                "connections": [
                    {
                        "id": "test-route",
                        "streetZoneId": str(zones[2].id),
                        "streetBand": "sidewalk",
                        "streetPoint": point,
                        "gateway": point,
                        "path": [point, point],
                        "widthM": 2.2,
                        "streetLiftM": 0.17,
                    }
                ],
                "paths": [{"points": [point, point], "widthM": 2.2}],
            }
        ],
    }
    return request, zones, building, snapshot


def test_snapshot_preserves_exact_routes_and_freezes_all_sources_without_claiming_geometry_proof():
    req, zones, building, raw = inputs()
    req.park_access_snapshot = ParkAccessSnapshot.model_validate(raw)
    result = build_render_source_snapshot(req, zones, [building], captured_at="now")
    assert result["plan"]["park_access_snapshot"] == raw
    assert result["park_access_evidence"] == PARK_ACCESS_EVIDENCE
    assert {source["id"] for source in result["plan"]["zones"]} == {str(zone.id) for zone in zones}
    assert all(source["updated_at"] for source in result["plan"]["zones"])
    original_hash = result["plan_revision_sha256"]
    req.park_access_snapshot.parks[0].paths[0].points[0] = (-114.09, 51.003)
    changed = build_render_source_snapshot(req, zones, [building], captured_at="later")
    assert changed["plan_revision_sha256"] != original_hash
    assert result["plan"]["park_access_snapshot"] == raw
    # The service deliberately records a route claim rather than recomputing
    # it. An unchanged client cache key does not grant geometric authority.
    assert changed["plan"]["park_access_snapshot"]["sourceSignature"] == raw["sourceSignature"]


@pytest.mark.parametrize(
    "change",
    [
        "missing",
        "unknown",
        "duplicate",
        "stale_hidden",
        "unknown_park",
        "unknown_street",
        "ineligible_street",
        "duplicate_eligible",
        "nonroad_eligible",
        "duplicate_park",
    ],
)
def test_sources_and_route_references_must_bind_to_current_project_inventory(change):
    _, zones, _, raw = inputs()
    if change == "missing":
        raw["sources"].pop()
    elif change == "unknown":
        raw["sources"][-1]["zoneId"] = str(uuid.uuid4())
    elif change == "duplicate":
        raw["sources"].append(copy.deepcopy(raw["sources"][0]))
    elif change == "stale_hidden":
        zones[-1].updated_at = datetime(2026, 9, 6, tzinfo=timezone.utc)
    elif change == "unknown_park":
        raw["parks"][0]["parkZoneId"] = str(uuid.uuid4())
    elif change == "unknown_street":
        raw["parks"][0]["connections"][0]["streetZoneId"] = str(uuid.uuid4())
    elif change == "ineligible_street":
        raw["eligibleStreetZoneIds"] = []
    elif change == "duplicate_eligible":
        raw["eligibleStreetZoneIds"] *= 2
    elif change == "nonroad_eligible":
        raw["eligibleStreetZoneIds"] = [str(zones[1].id)]
    elif change == "duplicate_park":
        raw["parks"].append(copy.deepcopy(raw["parks"][0]))
    with pytest.raises(HTTPException) as exc:
        bind_park_access_snapshot(ParkAccessSnapshot.model_validate(raw), zones)
    assert exc.value.status_code == 409


@pytest.mark.parametrize(
    "change", ["nan", "huge_sources", "huge_path", "huge_width", "bad_coordinate", "naive_time", "extra_field"]
)
def test_park_snapshot_schema_is_finite_and_bounded(change):
    _, _, _, raw = inputs()
    if change == "nan":
        raw["settings"]["maxGapM"] = float("nan")
    elif change == "huge_sources":
        raw["sources"] *= 100
    elif change == "huge_path":
        raw["parks"][0]["paths"][0]["points"] *= 1000
    elif change == "huge_width":
        raw["parks"][0]["connections"][0]["widthM"] = 100
    elif change == "bad_coordinate":
        raw["parks"][0]["connections"][0]["gateway"] = [181, 0]
    elif change == "naive_time":
        raw["sources"][0]["updatedAt"] = "2026-09-05T00:00:00"
    elif change == "extra_field":
        raw["server_certified"] = True
    with pytest.raises(ValidationError):
        ParkAccessSnapshot.model_validate(raw)


@pytest.mark.asyncio
async def test_stale_park_snapshot_rejects_before_provider_configuration_reservation_or_spend(monkeypatch):
    from app.api.v1 import direct_3d_render as endpoint

    req, zones, building, raw = inputs()
    raw["sources"].pop()
    req.park_access_snapshot = ParkAccessSnapshot.model_validate(raw)
    results = []
    for items in (zones, [building]):
        result = MagicMock()
        result.scalars.return_value.all.return_value = items
        results.append(result)
    db = SimpleNamespace(execute=AsyncMock(side_effect=results))
    reservation = AsyncMock()
    provider = AsyncMock()
    monkeypatch.setattr(endpoint, "get_settings", lambda: SimpleNamespace(
        openai_api_key="", direct_3d_jobs_enabled=False, direct_3d_images_enabled=True,
    ))
    monkeypatch.setattr(endpoint, "check_project_permission", AsyncMock())
    monkeypatch.setattr(endpoint, "lock_residual_landscape_project", AsyncMock())
    monkeypatch.setattr(endpoint, "_validate_direct_3d_project_zones", MagicMock(return_value={}))
    monkeypatch.setattr(endpoint, "_reserve_direct_render", reservation)
    monkeypatch.setattr(endpoint, "_call_openai_image_edit", provider, raising=False)
    with pytest.raises(HTTPException) as exc:
        await endpoint.generate_direct_3d_render(req, SimpleNamespace(id=uuid.uuid4()), db)
    assert exc.value.status_code == 409
    reservation.assert_not_awaited()
    provider.assert_not_awaited()


def test_legacy_capture_without_snapshot_remains_compatible():
    req, zone, building = _snapshot_inputs()
    result = build_render_source_snapshot(req, [zone], [building], captured_at="now")
    assert "park_access_snapshot" not in result["plan"]
    assert "park_access_evidence" not in result
    assert result["scope"] == "rendered_zones_and_linked_buildings"
