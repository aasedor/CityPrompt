from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.api.v1 import direct_3d_render
from app.api.v1.video import (
    RoutePoint,
    VideoPilotRequest,
    _validate_video_scene_revision,
)


class _ScalarRows:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return self

    def all(self):
        return self._rows

    def scalar_one_or_none(self):
        return self._rows


@pytest.mark.asyncio
async def test_video_scene_revision_binds_uncompiled_surface_material():
    from tests.test_direct_3d_render import _compiled_zone, _zone, _claims_for, _surface_claims_for
    park = _compiled_zone("green_space")
    surface = _zone(uuid.uuid4(), "development_area", properties={"ground_surface_material": "black_pavers"})
    request = VideoPilotRequest(**{**_request().model_dump(), "community_3d_claims": _claims_for([park]),
        "residual_landscape_claim": None, "authored_surface_claims": _surface_claims_for([surface])})
    async def validate():
        db = AsyncMock()
        db.execute.side_effect = [_ScalarRows([park, surface]), _ScalarRows([]), _ScalarRows(None)]
        return await _validate_video_scene_revision(request, db)
    assert len(await validate()) == 64
    surface.properties["ground_surface_material"] = "red_brick"
    with pytest.raises(HTTPException) as stale:
        await validate()
    assert stale.value.status_code == 409
    assert stale.value.detail["billed"] is False
    assert stale.value.detail["code"] == "video_project_state_changed"


def _request(*, reverse: bool = False) -> VideoPilotRequest:
    zone_ids = [uuid.UUID(int=2), uuid.UUID(int=1)]
    if reverse:
        zone_ids.reverse()
    return VideoPilotRequest(
        project_id=uuid.UUID(int=99),
        guide_frame_base64="a" * 100,
        route_points=[RoutePoint(x=0.1, y=0.1), RoutePoint(x=0.9, y=0.9)],
        community_3d_claims=[
            {
                "zone_id": zone_id,
                "source_hash": f"{zone_id.int:x}" * 64,
                "representation_hash": f"{zone_id.int + 2:x}" * 64,
            }
            for zone_id in zone_ids
        ],
        residual_landscape_claim={
            "boundary_id": uuid.UUID(int=10),
            "source_hash": "f" * 64,
        },
    )


@pytest.mark.asyncio
async def test_video_scene_revision_requires_compiled_scene_claims():
    request = VideoPilotRequest(
        project_id=uuid.UUID(int=99),
        guide_frame_base64="a" * 100,
        route_points=[RoutePoint(x=0.1, y=0.1), RoutePoint(x=0.9, y=0.9)],
    )

    with pytest.raises(HTTPException) as exc_info:
        await _validate_video_scene_revision(request, AsyncMock())

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail["code"] == "video_project_state_changed"
    assert exc_info.value.detail["billed"] is False


@pytest.mark.asyncio
async def test_video_scene_revision_is_canonical_and_skips_static_instance_binding(monkeypatch):
    calls: list[bool] = []

    def validate(_request, _zones, _buildings, *, bind_capture_instances=True, project_details=None):
        assert project_details is None
        calls.append(bind_capture_instances)
        return []

    monkeypatch.setattr(direct_3d_render, "_validate_direct_3d_project_zones", validate)

    async def revision(request: VideoPilotRequest) -> str:
        db = AsyncMock()
        db.execute.side_effect = [_ScalarRows([]), _ScalarRows([]), _ScalarRows(None)]
        return await _validate_video_scene_revision(request, db)

    first = await revision(_request())
    second = await revision(_request(reverse=True))

    # Claim order is not part of scene identity; zone/source/representation is.
    assert first == second
    assert len(first) == 64
    assert calls == [False, False]


@pytest.mark.asyncio
async def test_video_scene_revision_translates_direct_conflicts_before_billing(monkeypatch):
    def reject(*_args, **_kwargs):
        raise HTTPException(
            status_code=409,
            detail={"code": "direct_3d_project_state_changed", "message": "Rebuild the scene."},
        )

    monkeypatch.setattr(direct_3d_render, "_validate_direct_3d_project_zones", reject)
    db = AsyncMock()
    db.execute.side_effect = [_ScalarRows([]), _ScalarRows([]), _ScalarRows(None)]

    with pytest.raises(HTTPException) as exc_info:
        await _validate_video_scene_revision(_request(), db)

    assert exc_info.value.detail == {
        "code": "video_project_state_changed",
        "billed": False,
        "message": "Rebuild the scene.",
    }


@pytest.mark.asyncio
async def test_no_details_capture_rejected_after_people_are_added_with_unchanged_zone_claims():
    from tests.test_direct_3d_render import _compiled_zone, _claims_for

    zone = _compiled_zone('green_space')
    request = VideoPilotRequest.model_validate({**_request().model_dump(),
        'community_3d_claims': _claims_for([zone]), 'residual_landscape_claim': None})
    current = SimpleNamespace(metadata_={'scene_details': {'version': 1, 'revision': 1,
        'benches': [], 'props': [{'id': 'new-person', 'variant': 'people-pilot-commuter',
                                 'people_action': 'reading'}]}})
    db = AsyncMock()
    db.execute.side_effect = [_ScalarRows([zone]), _ScalarRows([]), _ScalarRows(current)]
    with pytest.raises(HTTPException) as error:
        await _validate_video_scene_revision(request, db)
    assert error.value.status_code == 409
    assert error.value.detail['billed'] is False
    assert error.value.detail['code'] == 'video_project_state_changed'


@pytest.mark.asyncio
async def test_current_details_are_read_even_when_capture_has_no_details_revision():
    current = SimpleNamespace(metadata_={'scene_details': {'revision': 1, 'props': [{'id': 'person'}]}})
    db = AsyncMock()
    db.execute.return_value = _ScalarRows(current)
    assert await direct_3d_render._current_render_details(_request(), db) == current.metadata_['scene_details']
    db.execute.assert_awaited_once()


def test_direct_image_without_details_revision_rejects_new_saved_people_but_allows_empty_legacy_details():
    from tests.test_direct_3d_render import _compiled_zone, _claims_for, _project_request

    zone = _compiled_zone('green_space')
    req = _project_request(uuid.uuid4(), community_claims=_claims_for([zone]))
    details = {'revision': 1, 'props': [{'id': 'new-person', 'variant': 'people-pilot-commuter',
                                     'people_action': 'reading'}]}
    with pytest.raises(HTTPException) as error:
        direct_3d_render._validate_direct_3d_project_zones(req, [zone], {}, project_details=details)
    assert error.value.status_code == 409 and error.value.detail['billed'] is False
    direct_3d_render._validate_direct_3d_project_zones(req, [zone], {},
        project_details={'revision': 2, 'props': [], 'benches': [], 'trees': [], 'surfaces': []})
