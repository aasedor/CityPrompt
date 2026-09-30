"""Contract checks for the private two-stage student photo-building pilot."""

import io
import hashlib
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, UploadFile
from PIL import Image

from app.api.v1 import buildings as buildings_api
from app.services.photo_building import (
    photo_state, prepare_photo, reference_prompt, refund_photo_tokens, reserve_photo_tokens,
)
from app.tasks import processing


def _png() -> bytes:
    image = Image.new("RGBA", (96, 64), (245, 245, 245, 0))
    image.putpixel((4, 4), (20, 30, 40, 255))
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def test_uploaded_photo_is_bounded_normalized_and_hashed():
    import hashlib

    prepared, digest = prepare_photo(_png())
    assert prepared.startswith(b"\xff\xd8")
    assert digest == hashlib.sha256(prepared).hexdigest()
    with Image.open(io.BytesIO(prepared)) as image:
        assert image.mode == "RGB"
        assert image.size == (96, 64)
    with pytest.raises(ValueError, match="readable"):
        prepare_photo(b"not a photo")
    with pytest.raises(ValueError, match="size limit"):
        prepare_photo(b"a" * (5 * 1024 * 1024 + 1))


def test_reference_prompt_preserves_architecture_and_bounds_student_text():
    prompt = reference_prompt("two mirrored homes, two doors")
    assert "SAME building" in prompt
    assert "roof" in prompt and "storey count" in prompt
    assert "two mirrored homes" in prompt
    assert len(reference_prompt("x" * 1000)) < len(prompt) + 600


@pytest.mark.anyio
async def test_photo_tokens_reserve_then_refund_once():
    from datetime import datetime, timezone

    user = SimpleNamespace(
        id=uuid.uuid4(), email="student@example.com", role="editor",
        render_credits=200, credits_reset_at=datetime.now(timezone.utc),
    )
    db = AsyncMock()
    db.add = MagicMock()
    audit_id = await reserve_photo_tokens(
        db, user, uuid.uuid4(), cost=50, stage="references", brief="test building"
    )
    assert user.render_credits == 150
    assert isinstance(audit_id, uuid.UUID)
    audit = next(call.args[0] for call in db.add.call_args_list if hasattr(call.args[0], "tokens_spent"))
    assert audit.tokens_spent == 50
    db.get = AsyncMock(side_effect=[audit, user, audit])
    await refund_photo_tokens(db, str(audit_id))
    await refund_photo_tokens(db, str(audit_id))
    assert user.render_credits == 200
    assert audit.tokens_spent == 0
    assert db.commit.await_count == 1


@pytest.mark.anyio
async def test_photo_tokens_reject_insufficient_balance_without_debit():
    from datetime import datetime, timezone

    user = SimpleNamespace(
        id=uuid.uuid4(), email="student@example.com", role="editor",
        render_credits=20, credits_reset_at=datetime.now(timezone.utc),
    )
    db = AsyncMock()
    db.add = MagicMock()
    with pytest.raises(HTTPException, match="costs 50 tokens"):
        await reserve_photo_tokens(db, user, uuid.uuid4(), cost=50, stage="references", brief="test")
    assert user.render_credits == 20
    db.add.assert_not_called()


@pytest.mark.anyio
async def test_photo_upload_saves_private_sources_then_queues_one_preparation(monkeypatch):
    building = SimpleNamespace(
        id=uuid.uuid4(), project_id=uuid.uuid4(), specifications={}, generation_status="idle"
    )
    user = SimpleNamespace(id=uuid.uuid4())
    db = AsyncMock()
    writes = []
    queued = []
    monkeypatch.setattr(buildings_api, "_editable_building", AsyncMock(return_value=building))
    monkeypatch.setattr(buildings_api, "_check_engine_available", lambda engine: None)
    monkeypatch.setattr(buildings_api, "reserve_photo_tokens", AsyncMock(return_value=uuid.UUID(int=1)))

    from app.tasks import processing

    monkeypatch.setattr(processing, "_upload_to_storage", lambda key, data, mime: writes.append((key, data, mime)))
    monkeypatch.setattr(
        processing.synthesize_building_photo_references,
        "apply_async",
        lambda args: queued.append(args) or SimpleNamespace(id="queued-once"),
    )
    file = UploadFile(filename="home.png", file=io.BytesIO(_png()))
    result = await buildings_api.create_photo_references(
        building.id, [file], "a white duplex", user, db
    )

    assert result["status"] == "synthesizing"
    assert len(writes) == len(queued) == 1
    state = photo_state(building.specifications)
    assert state["status"] == "synthesizing"
    assert state["source_keys"][0].startswith(f"projects/{building.project_id}/photo-buildings/{building.id}/")
    assert writes[0][2] == "image/jpeg"
    assert queued[0] == [str(building.id), state["batch_id"], str(uuid.UUID(int=1))]
    assert db.commit.await_count == 1


@pytest.mark.anyio
async def test_photo_model_requires_server_issued_views_and_accepts_selected_subset(monkeypatch):
    building = SimpleNamespace(
        id=uuid.uuid4(), project_id=uuid.uuid4(), specifications={}, generation_status="idle"
    )
    user = SimpleNamespace(id=uuid.uuid4())
    db = AsyncMock()
    monkeypatch.setattr(buildings_api, "_editable_building", AsyncMock(return_value=building))
    with pytest.raises(HTTPException) as exc:
        await buildings_api.generate_photo_model(building.id, user, db, selected_reference_indices=None)
    assert exc.value.status_code == 409

    prefix = f"projects/{building.project_id}/photo-buildings/{building.id}/abc/"
    building.specifications = {"photo_generation": {
        "version": 1, "batch_id": "abc", "status": "references_ready",
        "reference_keys": [f"{prefix}reference-{i}.jpg" for i in range(3)],
        "reference_hashes": ["0" * 64] * 3, "brief": "two storeys",
    }}
    monkeypatch.setattr(buildings_api, "_check_engine_available", lambda engine: None)
    monkeypatch.setattr(buildings_api, "reserve_photo_tokens", AsyncMock(return_value=uuid.UUID(int=2)))
    queued = []
    monkeypatch.setattr(
        buildings_api, "queue_ai_generation_task",
        AsyncMock(side_effect=lambda *args, **kwargs: queued.append(kwargs)),
    )
    result = await buildings_api.generate_photo_model(building.id, user, db, selected_reference_indices=None)
    assert result.status == "generating"
    assert queued[0]["mode"] == "multi_image"
    assert queued[0]["photo_batch_id"] == "abc"
    assert queued[0]["photo_audit_id"] == str(uuid.UUID(int=2))
    assert building.specifications["photo_generation"]["status"] == "model_generating"

    building.generation_status = "idle"
    building.specifications["photo_generation"]["status"] = "references_ready"
    queued.clear()
    await buildings_api.generate_photo_model(building.id, user, db, selected_reference_indices=[1])
    assert queued[0]["photo_reference_keys"] == [f"{prefix}reference-1.jpg"]
    assert building.specifications["photo_generation"]["selected_reference_indices"] == [1]

    building.generation_status = "idle"
    building.specifications["photo_generation"]["status"] = "references_ready"
    for invalid_indices in ([], [3], [1, 1]):
        with pytest.raises(HTTPException) as exc:
            await buildings_api.generate_photo_model(
                building.id, user, db, selected_reference_indices=invalid_indices,
            )
        assert exc.value.status_code == 422

    building.specifications["photo_generation"]["reference_keys"][0] = "projects/other/private.jpg"
    with pytest.raises(HTTPException) as exc:
        await buildings_api.generate_photo_model(building.id, user, db, selected_reference_indices=None)
    assert exc.value.status_code == 409


@pytest.mark.anyio
async def test_failed_reference_task_resumes_without_new_charge(monkeypatch):
    building = SimpleNamespace(
        id=uuid.uuid4(), project_id=uuid.uuid4(), generation_status="idle",
        specifications={"photo_generation": {
            "version": 1, "batch_id": "batch-3", "status": "failed",
            "provider_task_id": "already-paid-task", "reference_keys": [],
            "reference_audit_id": str(uuid.uuid4()),
        }},
    )
    db = AsyncMock()
    monkeypatch.setattr(buildings_api, "_editable_building", AsyncMock(return_value=building))
    monkeypatch.setattr(buildings_api, "reserve_photo_tokens", AsyncMock(side_effect=AssertionError("no charge")))
    queued = []
    monkeypatch.setattr(
        processing.synthesize_building_photo_references, "apply_async",
        lambda args: queued.append(args) or SimpleNamespace(id="resume-queued"),
    )
    result = await buildings_api.resume_photo_references(building.id, SimpleNamespace(id=uuid.uuid4()), db)
    assert result["status"] == "synthesizing"
    assert queued[0][1] == "batch-3"
    assert building.specifications["photo_generation"]["provider_task_id"] == "already-paid-task"


class _WorkerSession:
    def __init__(self, building):
        self.building = building

    def query(self, model):
        return SimpleNamespace(filter_by=lambda **kwargs: SimpleNamespace(first=lambda: self.building))

    def commit(self):
        pass

    def rollback(self):
        pass

    def refresh(self, value):
        pass

    def close(self):
        pass


def test_reference_worker_accepts_two_reviewable_images_without_model(monkeypatch):
    from app.generation import meshy_client
    import httpx

    source, digest = prepare_photo(_png())
    building = SimpleNamespace(
        id=uuid.uuid4(), project_id=uuid.uuid4(), model_url="old-model.glb", specifications={},
    )
    prefix = f"projects/{building.project_id}/photo-buildings/{building.id}/batch-2/"
    building.specifications["photo_generation"] = {
        "version": 1, "status": "synthesizing", "batch_id": "batch-2",
        "source_keys": [prefix + "source-0.jpg"], "source_hashes": [digest], "brief": "white duplex",
    }
    monkeypatch.setattr(processing, "_get_sync_session", lambda: _WorkerSession(building))
    monkeypatch.setattr(processing, "_get_s3_client", lambda: SimpleNamespace(
        get_object=lambda **kwargs: {"Body": io.BytesIO(source)}
    ))
    writes = []
    monkeypatch.setattr(processing, "_upload_to_storage", lambda *args: writes.append(args))
    monkeypatch.setattr(processing, "log_api_usage_sync", lambda **kwargs: None)
    monkeypatch.setattr(processing, "refund_photo_tokens_sync", lambda *args: pytest.fail("unexpected refund"))

    class Client:
        async def image_to_image_multiview(self, inputs, prompt):
            assert len(inputs) == 1 and inputs[0].startswith("data:image/jpeg;base64,")
            assert "white duplex" in prompt
            return "provider-views"

        async def poll_until_done(self, task_id, **kwargs):
            assert task_id == "provider-views"
            return {"image_urls": ["https://provider.example/1", "https://provider.example/2"]}

    class HTTP:
        def __init__(self, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

        async def get(self, url):
            return SimpleNamespace(content=_png(), raise_for_status=lambda: None)

    monkeypatch.setattr(meshy_client, "MeshyClient", Client)
    monkeypatch.setattr(httpx, "AsyncClient", HTTP)
    result = processing.synthesize_building_photo_references.run(str(building.id), "batch-2", str(uuid.uuid4()))
    assert result == {"status": "references_ready", "reference_count": 2}
    assert len(writes) == 2
    assert photo_state(building.specifications)["status"] == "references_ready"
    assert building.model_url == "old-model.glb"


def _photo_worker(monkeypatch, run_generation, *, corrupt=False):
    image, digest = prepare_photo(_png())
    building = SimpleNamespace(
        id=uuid.uuid4(), project_id=uuid.uuid4(), generation_status="generating",
        generation_prompt=None, generation_engine=None, architectural_style=None,
        meshy_task_id=None, model_url="/api/v1/files/old-model.glb", lod_urls={"0": "/api/v1/files/old-model.glb"},
        preview_url=None, preview_status="idle", specifications={},
    )
    prefix = f"projects/{building.project_id}/photo-buildings/{building.id}/batch-1/"
    keys = [f"{prefix}reference-{i}.jpg" for i in range(3)]
    building.specifications["photo_generation"] = {
        "version": 1, "status": "model_generating", "batch_id": "batch-1",
        "reference_keys": keys, "reference_hashes": [digest] * 3,
    }
    monkeypatch.setattr(processing, "_get_sync_session", lambda: _WorkerSession(building))
    monkeypatch.setattr(processing, "_get_s3_client", lambda: SimpleNamespace(
        get_object=lambda **kwargs: {"Body": io.BytesIO(b"corrupt" if corrupt else image)}
    ))
    monkeypatch.setattr(processing, "_begin_building_representation_mutation", lambda *args: None)
    monkeypatch.setattr(processing, "_mark_building_representation_stale", lambda *args: None)
    monkeypatch.setattr(processing, "_upload_to_storage", lambda *args: None)
    monkeypatch.setattr(processing, "_propagate_model_to_siblings", lambda *args: pytest.fail("private model propagated"))
    monkeypatch.setattr(processing, "log_api_usage_sync", lambda **kwargs: None)
    monkeypatch.setattr(processing.generate_3d_model_ai, "update_state", lambda **kwargs: None)
    monkeypatch.setattr(processing.generate_3d_model_ai, "retry", lambda **kwargs: pytest.fail("paid retry"))

    class Provider:
        engine_id = "meshy"

        def is_available(self):
            return True

        async def run_generation(self, **kwargs):
            return await run_generation(**kwargs)

    monkeypatch.setattr(processing, "get_engine", lambda engine: Provider())
    return building, keys


def test_photo_model_worker_keeps_old_model_until_private_result_commits(monkeypatch):
    from app.generation.engine import GenerationResult

    async def generate(**kwargs):
        assert kwargs["mode"] == "multi_image"
        assert len(kwargs["image_urls"]) == 2
        assert all(url.startswith("data:image/jpeg;base64,") for url in kwargs["image_urls"])
        assert kwargs["preview_callback"] is None
        assert building.model_url == "/api/v1/files/old-model.glb"
        return GenerationResult(glb_data=b"new-glb", engine="meshy", task_id="provider-task")

    building, keys = _photo_worker(monkeypatch, generate)
    keys = keys[:2]
    building.specifications["photo_generation"]["reference_keys"] = keys
    building.specifications["photo_generation"]["reference_hashes"] = building.specifications["photo_generation"]["reference_hashes"][:2]
    result = processing.generate_3d_model_ai.run(
        str(building.id), "materials", mode="multi_image", engine="meshy",
        photo_reference_keys=keys, photo_batch_id="batch-1",
    )
    assert result["status"] == "completed"
    assert building.model_url.endswith("_photo_batch-1.glb")
    assert photo_state(building.specifications)["status"] == "completed"


def test_photo_model_worker_uses_only_reviewed_selected_view(monkeypatch):
    from app.generation.engine import GenerationResult

    async def generate(**kwargs):
        assert len(kwargs["image_urls"]) == 1
        return GenerationResult(glb_data=b"selected-view-glb", engine="meshy", task_id="selected-task")

    building, keys = _photo_worker(monkeypatch, generate)
    building.specifications["photo_generation"]["selected_reference_indices"] = [1]
    result = processing.generate_3d_model_ai.run(
        str(building.id), "materials", mode="multi_image", engine="meshy",
        photo_reference_keys=[keys[1]], photo_batch_id="batch-1",
    )
    assert result["status"] == "completed"


def test_photo_model_worker_rejects_changed_reference_without_spending(monkeypatch):
    async def unexpected(**kwargs):
        pytest.fail("provider must not be called for a changed reference")

    building, keys = _photo_worker(monkeypatch, unexpected, corrupt=True)
    result = processing.generate_3d_model_ai.run(
        str(building.id), "materials", mode="multi_image", engine="meshy",
        photo_reference_keys=keys, photo_batch_id="batch-1",
    )
    assert result["status"] == "failed"
    assert building.model_url == "/api/v1/files/old-model.glb"
    assert photo_state(building.specifications)["status"] == "failed"
