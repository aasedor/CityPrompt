from __future__ import annotations

import uuid
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

    def validate(_request, _zones, _buildings, *, bind_capture_instances=True):
        calls.append(bind_capture_instances)
        return []

    monkeypatch.setattr(direct_3d_render, "_validate_direct_3d_project_zones", validate)

    async def revision(request: VideoPilotRequest) -> str:
        db = AsyncMock()
        db.execute.side_effect = [_ScalarRows([]), _ScalarRows([])]
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
    db.execute.side_effect = [_ScalarRows([]), _ScalarRows([])]

    with pytest.raises(HTTPException) as exc_info:
        await _validate_video_scene_revision(_request(), db)

    assert exc_info.value.detail == {
        "code": "video_project_state_changed",
        "billed": False,
        "message": "Rebuild the scene.",
    }
