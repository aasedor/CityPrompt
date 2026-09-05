import copy
import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from shapely.geometry import Polygon, box

from app.schemas.shared_ground import SharedGroundSnapshot
from app.services.shared_ground_provenance import SHARED_GROUND_EVIDENCE, bind_shared_ground_snapshot
from app.services.render_provenance import build_render_source_snapshot
from tests.test_render_fidelity_provenance import _snapshot_inputs


def inputs():
    req, building_zone, building = _snapshot_inputs()
    now = datetime(2026, 9, 5, 0, 3, 34, 431612, tzinfo=timezone.utc)
    boundary = SimpleNamespace(id=uuid.uuid4(), zone_type="site_boundary", updated_at=now,
        geometry=box(-114.1, 51, -114.0998, 51.0002), is_active_boundary=True,
        properties={"community_3d_mask_existing_tiles": False})
    raw = {"version": 1, "source": "google_3d_tiles", "verticalReference": "WGS84_ellipsoid",
        "boundaryId": str(boundary.id), "boundaryUpdatedAt": now.isoformat(),
        "boundaryCoordinates": [list(point) for point in boundary.geometry.exterior.coords][:-1],
        "sourceSignature": "client-source-cache", "signature": "client-surface-cache",
        "grid": {"west": -114.1, "south": 51, "columns": 2, "rows": 2, "stepLng": 0.0002, "stepLat": 0.0002},
        "heights": [1031.3, 1031.4, 1031.3, 1031.4],
        "quality": {"sampleCount": 4, "stablePasses": 2, "maxPassDeltaM": 0.01, "maxSlope": 0.01, "maxLocalResidualM": 0.01}}
    return req, [building_zone, boundary], building, raw


def test_exact_measured_snapshot_frozen_with_current_boundary_without_height_certification():
    req, zones, building, raw = inputs()
    req.shared_ground_snapshot = SharedGroundSnapshot.model_validate(raw)
    result = build_render_source_snapshot(req, zones, [building], captured_at="now")
    assert result["plan"]["shared_ground_snapshot"] == raw
    assert result["shared_ground_evidence"] == SHARED_GROUND_EVIDENCE
    assert result["scope"] == "rendered_zones_active_ground_boundary_and_linked_buildings"
    frozen_boundary = next(zone for zone in result["plan"]["zones"] if zone["id"] == raw["boundaryId"])
    assert frozen_boundary["updated_at"] == raw["boundaryUpdatedAt"]
    assert frozen_boundary["properties"]["community_3d_mask_existing_tiles"] is False
    req.shared_ground_snapshot.heights[0] += 0.1
    changed = build_render_source_snapshot(req, zones, [building], captured_at="later")
    assert result["plan"]["shared_ground_snapshot"] == raw
    assert changed["plan_revision_sha256"] != result["plan_revision_sha256"]
    # Same client cache key is not authority over actual heights.
    assert changed["plan"]["shared_ground_snapshot"]["signature"] == raw["signature"]


def test_geojson_roundtrip_noise_does_not_reject_an_unchanged_site():
    _, zones, _, raw = inputs()
    raw["boundaryCoordinates"][0][0] += 2e-14
    result = bind_shared_ground_snapshot(SharedGroundSnapshot.model_validate(raw), zones)
    assert result["boundaryId"] == raw["boundaryId"]


def test_actual_boundary_movement_still_requires_a_fresh_capture():
    _, zones, _, raw = inputs()
    raw["boundaryCoordinates"][0][0] -= 1e-8
    with pytest.raises(HTTPException) as exc:
        bind_shared_ground_snapshot(SharedGroundSnapshot.model_validate(raw), zones)
    assert exc.value.status_code == 409


@pytest.mark.parametrize("change", ["missing", "unknown", "stale", "inactive", "prepared", "duplicate_active", "geometry", "hole", "wrong_type"])
def test_shared_ground_must_match_the_current_active_retained_boundary(change):
    _, zones, _, raw = inputs()
    boundary = zones[-1]
    if change == "missing":
        zones.pop()
    elif change == "unknown":
        raw["boundaryId"] = str(uuid.uuid4())
    elif change == "stale":
        boundary.updated_at = datetime(2026, 9, 6, tzinfo=timezone.utc)
    elif change == "inactive":
        boundary.is_active_boundary = False
    elif change == "prepared":
        boundary.properties["community_3d_mask_existing_tiles"] = True
    elif change == "duplicate_active":
        zones.append(copy.deepcopy(boundary))
    elif change == "geometry":
        boundary.geometry = box(-114.1, 51, -114.0997, 51.0002)
    elif change == "hole":
        boundary.geometry = Polygon(boundary.geometry.exterior, [box(-114.09995, 51.00005, -114.0999, 51.0001).exterior])
    elif change == "wrong_type":
        boundary.zone_type = "green_space"
    with pytest.raises(HTTPException) as exc:
        bind_shared_ground_snapshot(SharedGroundSnapshot.model_validate(raw), zones)
    assert exc.value.status_code == 409


@pytest.mark.parametrize("change", ["nan", "inf", "too_many", "missing_height", "wrong_count", "zero_step", "wrong_grid", "wrong_reference", "low_stability", "excess_slope", "naive_time", "extra"])
def test_shared_ground_schema_finite_bounded_and_complete(change):
    _, _, _, raw = inputs()
    if change == "nan":
        raw["heights"][0] = float("nan")
    elif change == "inf":
        raw["grid"]["stepLng"] = float("inf")
    elif change == "too_many":
        raw["heights"] *= 301
    elif change == "missing_height":
        raw["heights"].pop()
    elif change == "wrong_count":
        raw["quality"]["sampleCount"] = 5
    elif change == "zero_step":
        raw["grid"]["stepLat"] = 0
    elif change == "wrong_grid":
        raw["grid"]["west"] -= 0.01
    elif change == "wrong_reference":
        raw["verticalReference"] = "mean_sea_level"
    elif change == "low_stability":
        raw["quality"]["stablePasses"] = 1
    elif change == "excess_slope":
        raw["quality"]["maxSlope"] = 0.46
    elif change == "naive_time":
        raw["boundaryUpdatedAt"] = "2026-09-05T00:00:00"
    elif change == "extra":
        raw["server_height_certified"] = True
    with pytest.raises(ValidationError):
        SharedGroundSnapshot.model_validate(raw)


def test_postgres_and_sqlite_revision_forms_compare_as_utc_and_ring_closure_is_equivalent():
    _, zones, _, raw = inputs()
    zones[-1].updated_at = zones[-1].updated_at.replace(tzinfo=None)
    raw["boundaryCoordinates"].append(raw["boundaryCoordinates"][0])
    assert bind_shared_ground_snapshot(SharedGroundSnapshot.model_validate(raw), zones) == raw


@pytest.mark.asyncio
async def test_stale_ground_rejects_before_provider_configuration_reservation_or_spend(monkeypatch):
    from app.api.v1 import direct_3d_render as endpoint

    req, zones, building, raw = inputs()
    req.shared_ground_snapshot = SharedGroundSnapshot.model_validate(raw)
    zones[-1].properties["community_3d_mask_existing_tiles"] = True
    results = []
    for items in (zones, [building]):
        result = MagicMock()
        result.scalars.return_value.all.return_value = items
        results.append(result)
    db = SimpleNamespace(execute=AsyncMock(side_effect=results))
    reservation, provider = AsyncMock(), AsyncMock()
    monkeypatch.setattr(endpoint, "get_settings", lambda: SimpleNamespace(openai_api_key=""))
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


def test_absent_legacy_ground_remains_compatible():
    req, zone, building = _snapshot_inputs()
    result = build_render_source_snapshot(req, [zone], [building], captured_at="now")
    assert "shared_ground_snapshot" not in result["plan"]
    assert "shared_ground_evidence" not in result
