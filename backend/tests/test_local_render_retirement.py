"""Retired desktop engines cannot submit jobs; saved media stays readable."""

from types import SimpleNamespace
import uuid

from fastapi import FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient
import pytest

from app.api.v1.router import api_router
from app.api.v1 import render_animation


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "method,path",
    [
        ("GET", "/presets"),
        ("POST", "/jobs"),
        ("GET", "/projects/00000000-0000-0000-0000-000000000001/jobs"),
        ("POST", "/projects/00000000-0000-0000-0000-000000000001/jobs/00000000-0000-0000-0000-000000000002/recover"),
        (
            "POST",
            "/projects/00000000-0000-0000-0000-000000000001/jobs/00000000-0000-0000-0000-000000000002/resolve-missing",
        ),
    ],
)
async def test_local_generation_routes_are_removed_even_with_a_stale_enable_flag(monkeypatch, method, path):
    monkeypatch.setenv("COMFY_TRIALS_ENABLED", "true")
    app = FastAPI()
    app.include_router(api_router, prefix="/api/v1")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.request(method, f"/api/v1/local-render{path}")
    assert response.status_code == 404


def test_saved_original_capture_remains_an_image_source_but_not_a_finished_video_source():
    project_id, render_id = uuid.uuid4(), uuid.uuid4()
    project = SimpleNamespace(
        id=project_id,
        metadata_={
            "saved_renders": [
                {
                    "id": str(render_id),
                    "model": "3d-capture",
                    "variant": "manual",
                    "image_url": f"/api/v1/files/projects/{project_id}/renders/{render_id}.png",
                }
            ],
        },
    )
    assert render_animation._source_render(project, render_id, require_finished=False)[0]["model"] == "3d-capture"
    with pytest.raises(HTTPException, match="finished AI render"):
        render_animation._source_render(project, render_id)
