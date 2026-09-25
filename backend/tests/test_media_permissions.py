"""Accepted viewers may read presentation media but cannot create or mutate it."""

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.api.v1 import direct_3d_render, render, video
from tests.conftest import FakeProject


def result(value):
    response = MagicMock()
    response.scalar_one_or_none.return_value = value
    return response


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "operation",
    [
        "classic",
        "direct_3d",
        "save",
        "delete",
        "video_preflight",
        "video_backfill",
        "video_benchmark",
        "video_generate",
    ],
)
async def test_project_viewer_cannot_start_or_mutate_media(operation, mock_db, test_user, monkeypatch):
    # Exercise the legacy endpoint's permission branch independently of the
    # environment's durable-only switch (which correctly rejects it with 409).
    settings = direct_3d_render.get_settings().model_copy(update={"direct_3d_jobs_enabled": False})
    monkeypatch.setattr(direct_3d_render, "get_settings", lambda: settings)
    project = FakeProject()
    mock_db.execute.side_effect = [result(project), result(SimpleNamespace(permission="viewer"))]
    request = SimpleNamespace(project_id=project.id)
    callbacks = {
        "classic": lambda: render.generate_render(request, test_user, mock_db),
        "direct_3d": lambda: direct_3d_render.generate_direct_3d_render(request, test_user, mock_db),
        "save": lambda: render.save_render(project.id, request, test_user, mock_db),
        "delete": lambda: render.delete_render(project.id, "saved-image", test_user, mock_db),
        "video_preflight": lambda: video.preflight_video(request, test_user, mock_db),
        "video_backfill": lambda: video.backfill_video_fidelity(request, test_user, mock_db),
        "video_benchmark": lambda: video.set_video_benchmark(request, test_user, mock_db),
        "video_generate": lambda: video.generate_video(request, test_user, mock_db),
    }
    with pytest.raises(HTTPException) as exc:
        await callbacks[operation]()
    assert exc.value.status_code == 403
    assert exc.value.detail == "Requires editor permission on this project"
    # Permission rejection precedes credit locks, provider work, and persistence.
    assert mock_db.execute.await_count == 2
    mock_db.add.assert_not_called()
    mock_db.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["images", "videos"])
async def test_accepted_viewer_can_still_list_project_media(kind, mock_db, test_user):
    project = FakeProject()
    project.metadata_ = {}
    mock_db.execute.side_effect = [result(project), result(SimpleNamespace(permission="viewer"))]
    mock_db.get.return_value = project
    if kind == "images":
        response = await render.list_renders(project.id, test_user, mock_db)
        assert response == []
    else:
        response = await video.list_video_attempts(project.id, test_user, mock_db)
        assert response.attempts == []
