import pytest

from app.generation import engine as generation_engine


@pytest.mark.anyio
async def test_meshy_engine_runs_preview_refine_and_callbacks(monkeypatch):
    progress_updates = []
    task_ids = []
    preview_models = []
    usage_events = []

    class FakeMeshyClient:
        async def text_to_3d_preview(self, prompt, negative_prompt=""):
            assert prompt == "Modern mid-rise residential building"
            assert negative_prompt == "no clutter"
            return "preview-task"

        async def image_to_3d(self, image_url):
            raise AssertionError("image_to_3d should not be used in this test")

        async def text_to_3d_refine(self, preview_task_id, texture_prompt=""):
            assert preview_task_id == "preview-task"
            assert "Modern mid-rise residential building" in texture_prompt
            return "refine-task"

        async def poll_until_done(self, task_id, timeout=300, task_type="text"):
            if task_id == "preview-task":
                assert task_type == "text"
                return {"model_urls": {"glb": "https://example.test/preview.glb"}}
            if task_id == "refine-task":
                return {
                    "model_urls": {"glb": "https://example.test/final.glb"},
                    "thumbnail_url": "https://example.test/thumb.png",
                }
            raise AssertionError(f"unexpected task id: {task_id}")

    async def fake_download(self, url, timeout=60.0):
        payloads = {
            "https://example.test/preview.glb": b"preview-glb",
            "https://example.test/final.glb": b"final-glb",
        }
        return payloads[url]

    monkeypatch.setattr("app.generation.meshy_client.MeshyClient", FakeMeshyClient)
    monkeypatch.setattr(generation_engine.MeshyEngine, "_download_bytes", fake_download)
    monkeypatch.setattr(generation_engine, "log_api_usage_sync", lambda **kwargs: usage_events.append(kwargs))

    result = await generation_engine.MeshyEngine().run_generation(
        prompt="Modern mid-rise residential building",
        mode="text",
        refine=True,
        negative_prompt="no clutter",
        building_id="building-123",
        progress_callback=lambda progress, step: progress_updates.append((progress, step)),
        task_callback=lambda task_id: task_ids.append(task_id),
        preview_callback=lambda glb_data: preview_models.append(glb_data),
    )

    assert [step for _, step in progress_updates] == [
        "calling_meshy",
        "polling",
        "refining",
        "downloading",
    ]
    assert task_ids == ["preview-task", "refine-task"]
    assert preview_models == [b"preview-glb"]
    assert result.glb_data == b"final-glb"
    assert result.task_id == "refine-task"
    assert result.thumbnail_url == "https://example.test/thumb.png"
    assert [event["operation"] for event in usage_events] == [
        "text_to_3d_preview",
        "text_to_3d_refine",
    ]


@pytest.mark.anyio
async def test_tripo_engine_runs_image_generation_and_lod(monkeypatch):
    progress_updates = []
    task_ids = []
    usage_events = []

    class FakeTripoClient:
        async def image_to_3d(self, image_url):
            assert image_url == "https://example.test/reference.png"
            return "tripo-task"

        async def text_to_3d(self, prompt, negative_prompt=None):
            raise AssertionError("text_to_3d should not be used in this test")

        async def poll_until_done(self, task_id, timeout=120):
            if task_id == "tripo-task":
                return {"model_url": "https://example.test/tripo.glb"}
            if task_id == "lod-task":
                return {"model_url": "https://example.test/tripo-lod.glb"}
            raise AssertionError(f"unexpected task id: {task_id}")

        async def smart_low_poly(self, original_task_id):
            assert original_task_id == "tripo-task"
            return "lod-task"

        async def download_model(self, url):
            payloads = {
                "https://example.test/tripo.glb": b"tripo-glb",
                "https://example.test/tripo-lod.glb": b"tripo-lod-glb",
            }
            return payloads[url]

    monkeypatch.setattr("app.generation.tripo_client.TripoClient", FakeTripoClient)
    monkeypatch.setattr(generation_engine, "log_api_usage_sync", lambda **kwargs: usage_events.append(kwargs))

    result = await generation_engine.TripoEngine().run_generation(
        prompt="Ignored in image mode",
        mode="image",
        image_url="https://example.test/reference.png",
        building_id="building-456",
        progress_callback=lambda progress, step: progress_updates.append((progress, step)),
        task_callback=lambda task_id: task_ids.append(task_id),
    )

    assert [step for _, step in progress_updates] == [
        "calling_tripo",
        "polling_tripo",
        "smart_low_poly",
        "downloading",
    ]
    assert task_ids == ["tripo-task"]
    assert result.glb_data == b"tripo-glb"
    assert result.lod_glb_data == {"1": b"tripo-lod-glb"}
    assert [event["operation"] for event in usage_events] == [
        "image_to_3d",
        "retopology",
    ]
