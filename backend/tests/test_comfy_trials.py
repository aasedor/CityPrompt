"""Local GPU calls are mocked; ownership/recovery use disposable PostgreSQL."""

import asyncio
import io
from types import SimpleNamespace
from unittest.mock import AsyncMock
from datetime import datetime, timedelta, timezone
import uuid

import httpx
import pytest
from fastapi import HTTPException
from PIL import Image

from app.services import comfy_trials as service
from app.api.v1 import comfy_trials as routes, render_animation, documents, video
from app.models.models import Project, User, ProjectShare
from tests.test_render_attempts import isolated as isolated
from tests.test_kling_video import png


def test_local_capture_is_an_image_source_but_not_a_finished_video_source():
    project_id, render_id = uuid.uuid4(), uuid.uuid4()
    project = SimpleNamespace(id=project_id, metadata_={"saved_renders": [{
        "id": str(render_id), "model": "3d-capture", "variant": "manual",
        "image_url": f"/api/v1/files/projects/{project_id}/renders/{render_id}.png",
    }]})
    assert render_animation._source_render(project, render_id, require_finished=False)[0]["model"] == "3d-capture"
    with pytest.raises(HTTPException, match="finished AI render"):
        render_animation._source_render(project, render_id)


def test_workflows_use_native_reference_conditioning_and_bounded_sizes():
    for p in service.PRESETS.values():
        data, w, h = service.prepare_source(png(), p)
        assert max(w, h) <= p.max_edge and w % 32 == h % 32 == 0
        assert Image.open(io.BytesIO(data)).size == (w, h)
        g = service.workflow(
            p, "full-source.png", "A restrained photograph", 42, w, h, "job"
        )
        assert g["4"]["inputs"]["image"] == "full-source.png"
        assert not any(n["class_type"].startswith("Kling") for n in g.values())
        if p.id == "flux-klein":
            assert g["11"]["inputs"]["latent"] == ["7", 0]
            assert g["16"]["inputs"]["steps"] == 4
        if p.id == "qwen-image":
            assert g["5"]["inputs"]["images.image_1"] == ["4", 0]
        if p.kind == "video":
            assert g["7"]["inputs"]["length"] == 49
            assert g["18"]["inputs"]["fps"] == 24
            assert "audio" not in g["18"]["inputs"]


@pytest.mark.asyncio
async def test_native_job_id_submission_and_output_download(monkeypatch):
    job_id = str(uuid.uuid4())
    calls = []

    def handle(req):
        calls.append(req)
        if req.url.path == "/upload/image":
            return httpx.Response(
                200, json={"name": "source.png", "subfolder": "", "type": "input"}
            )
        if req.url.path == "/prompt":
            import json

            payload = json.loads(req.content)
            assert payload["prompt_id"] == job_id
            assert payload["prompt"]["4"]["inputs"]["image"] == "source.png"
            return httpx.Response(200, json={"prompt_id": job_id, "node_errors": {}})
        if req.url.path.startswith("/history"):
            return httpx.Response(
                200,
                json={
                    job_id: {
                        "status": {"completed": True},
                        "outputs": {
                            "10": {
                                "images": [
                                    {
                                        "filename": "finished.png",
                                        "subfolder": "cityprompt_trials",
                                        "type": "output",
                                    }
                                ]
                            }
                        },
                    }
                },
            )
        assert req.url.path == "/view"
        return httpx.Response(200, content=png())

    monkeypatch.setattr(
        service,
        "client",
        lambda _: httpx.AsyncClient(
            base_url="http://127.0.0.1:8188", transport=httpx.MockTransport(handle)
        ),
    )
    await service.submit(
        None, service.PRESETS["flux-klein"], png(), "Photo", 42, 768, 448, job_id
    )
    state, output = await service.poll(None, job_id)
    assert state == "saving" and output == png()
    assert sum(c.url.path == "/prompt" for c in calls) == 1


def test_loopback_only_configuration_and_no_client_graph():
    with pytest.raises(service.ComfyFailure):
        service.client(
            SimpleNamespace(comfy_trials_base_url="https://external.example")
        )
    with pytest.raises(ValueError):
        routes.TrialRequest(
            project_id=uuid.uuid4(),
            source_render_id=uuid.uuid4(),
            request_id=uuid.uuid4(),
            preset="flux-klein",
            prompt="Test",
            workflow={},
        )


@pytest.fixture
async def pilot(isolated, monkeypatch):
    f = isolated
    settings = f.settings.model_copy(update={"comfy_trials_enabled": True})
    monkeypatch.setattr(routes, "get_settings", lambda: settings)
    monkeypatch.setattr(render_animation, "_read_source", lambda _: png())
    monkeypatch.setattr(
        service,
        "available_presets",
        AsyncMock(
            return_value=[
                {"id": p.id, "available": True} for p in service.PRESETS.values()
            ]
        ),
    )
    submit = AsyncMock()
    poll = AsyncMock(return_value=("saving", png()))
    monkeypatch.setattr(service, "submit", submit)
    monkeypatch.setattr(service, "poll", poll)
    saved = {}

    async def upload(key, data, mime):
        saved[key] = data

    monkeypatch.setattr(documents, "_upload_to_storage", upload)
    source_id = uuid.uuid4()
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        project.metadata_ = {
            "saved_renders": [
                {
                    "id": str(source_id),
                    "image_url": f"/api/v1/files/projects/{project.id}/renders/{source_id}.png",
                    "variant": "final",
                }
            ]
        }
        await db.commit()
    req = routes.TrialRequest(
        project_id=f.project.id,
        source_render_id=source_id,
        request_id=uuid.uuid4(),
        preset="flux-klein",
        prompt="Natural architectural photograph",
    )
    return SimpleNamespace(
        **vars(f), request=req, submit=submit, poll=poll, saved=saved
    )


async def generate(f, req=None, user_id=None):
    async with f.sessions() as db:
        return await routes.generate(
            req or f.request, await db.get(User, user_id or f.user.id), db
        )


async def recover(f, job):
    async with f.sessions() as db:
        return await routes.recover(
            f.project.id, uuid.UUID(job["id"]), await db.get(User, f.user.id), db
        )


@pytest.mark.asyncio
async def test_concurrent_requests_submit_once_and_never_debit(pilot):
    f = pilot

    async def receipt(*args):
        async with f.sessions() as db:
            project = await db.get(Project, f.project.id)
            assert project.metadata_[routes.JOBS_KEY][0]["interaction_id"] == args[-1]

    f.submit.side_effect = receipt
    results = await asyncio.gather(*(generate(f) for _ in range(6)))
    assert len({r["id"] for r in results}) == 1
    f.submit.assert_awaited_once()
    async with f.sessions() as db:
        assert (await db.get(User, f.user.id)).render_credits == 1000
    with pytest.raises(HTTPException) as exc:
        await generate(f, f.request.model_copy(update={"prompt": "Different request"}))
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_lost_receipt_recovers_original_job_and_saves_image_once(pilot):
    f = pilot
    f.submit.side_effect = httpx.ReadTimeout("lost receipt")
    job = await generate(f)
    assert job["status"] == "submission_unknown"
    result = await recover(f, job)
    assert result["status"] == "complete"
    assert result["result"]["presentation_strategy"] == "local_model_trial"
    await recover(f, job)
    f.submit.assert_awaited_once()
    f.poll.assert_awaited_once_with(routes.get_settings(), job["id"])
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        assert len(project.metadata_["saved_renders"]) == 2
        assert project.metadata_[routes.JOBS_KEY][0]["source_render_id"] == str(
            f.request.source_render_id
        )
    assert any(k.endswith(".provenance.json") for k in f.saved)


@pytest.mark.asyncio
async def test_video_saved_to_existing_gallery_without_route_fidelity_claim(pilot):
    f = pilot
    f.poll.return_value = ("saving", b"\x00\x00\x00\x18ftypisom" + bytes(24))
    job = await generate(f, f.request.model_copy(update={"preset": "wan-video"}))
    result = await recover(f, job)
    assert result["status"] == "complete"
    assert result["result"]["provider"] == "comfyui"
    assert result["result"]["fidelity_status"] is None
    await recover(f, job)
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        assert len(project.metadata_["video_pilot_attempts"]) == 1
        assert (
            video._public_attempt(
                project.metadata_["video_pilot_attempts"][0]
            ).estimated_cost_usd
            == 0
        )


@pytest.mark.asyncio
async def test_wrong_project_source_and_viewer_cannot_submit(pilot):
    f = pilot
    with pytest.raises(HTTPException) as exc:
        await generate(
            f, f.request.model_copy(update={"source_render_id": uuid.uuid4()})
        )
    assert exc.value.status_code == 404
    async with f.sessions() as db:
        other = User(
            email=f"viewer-{uuid.uuid4()}@example.com",
            full_name="Viewer",
            role="viewer",
            render_credits=0,
        )
        db.add(other)
        await db.flush()
        db.add(
            ProjectShare(project_id=f.project.id, user_id=other.id, permission="viewer")
        )
        await db.commit()
    with pytest.raises(HTTPException) as exc:
        await generate(f, user_id=other.id)
    assert exc.value.status_code == 403
    f.submit.assert_not_awaited()


@pytest.mark.asyncio
async def test_3d_source_allowed_for_images_but_not_animation(pilot):
    f = pilot
    async with f.sessions() as db:
        project = await db.get(Project, f.project.id)
        meta = dict(project.metadata_)
        meta["saved_renders"] = [
            {
                **meta["saved_renders"][0],
                "presentation_strategy": "authoritative_source",
            }
        ]
        project.metadata_ = meta
        await db.commit()
    with pytest.raises(HTTPException) as exc:
        await generate(f, f.request.model_copy(update={"preset": "wan-video"}))
    assert exc.value.status_code == 400
    assert (await generate(f))["status"] == "queued"


@pytest.mark.asyncio
async def test_missing_job_resolution_requires_absence_and_does_not_resubmit(pilot):
    f = pilot
    f.submit.side_effect = httpx.ReadTimeout("lost")
    job = await generate(f)
    f.poll.return_value = ("submission_unknown", None)
    async with f.sessions() as db:
        user = await db.get(User, f.user.id)
        with pytest.raises(HTTPException) as exc:
            await routes.resolve_missing(f.project.id, uuid.UUID(job["id"]), user, db)
        assert exc.value.status_code == 409
        await db.rollback()
        await routes.update_job(
            db,
            f.project.id,
            job["id"],
            created_at=(datetime.now(timezone.utc) - timedelta(minutes=3)).isoformat(),
        )
        user = await db.get(User, f.user.id)
        f.poll.return_value = ("running", None)
        with pytest.raises(HTTPException) as exc:
            await routes.resolve_missing(f.project.id, uuid.UUID(job["id"]), user, db)
        assert exc.value.status_code == 409
        await db.rollback()
        f.poll.return_value = ("submission_unknown", None)
        user = await db.get(User, f.user.id)
        result = await routes.resolve_missing(
            f.project.id, uuid.UUID(job["id"]), user, db
        )
        assert result["status"] == "failed"
    f.submit.assert_awaited_once()
