import uuid
from types import SimpleNamespace

from app.tasks import processing


class DummySession:
    def __init__(self):
        self.commit_calls = 0
        self.rollback_calls = 0

    def commit(self):
        self.commit_calls += 1

    def rollback(self):
        self.rollback_calls += 1


def test_get_sync_engine_is_lazy_singleton(monkeypatch):
    sentinel = object()
    calls = []

    monkeypatch.setattr(processing, "_sync_engine", None)
    monkeypatch.setattr(processing, "_sync_session_factory", None)

    def fake_create_engine(*args, **kwargs):
        calls.append((args, kwargs))
        return sentinel

    monkeypatch.setattr(processing, "create_engine", fake_create_engine)

    assert processing._get_sync_engine() is sentinel
    assert processing._get_sync_engine() is sentinel
    assert len(calls) == 1
    assert calls[0][1]["pool_pre_ping"] is True


def test_queue_procedural_generation_jobs_records_task_ids_and_failures(monkeypatch):
    good = SimpleNamespace(
        id=uuid.uuid4(),
        specifications={"existing": "value"},
        generation_status="generating",
    )
    bad = SimpleNamespace(
        id=uuid.uuid4(),
        specifications=None,
        generation_status="generating",
    )
    document = SimpleNamespace(
        extracted_data={"building_ids": [str(good.id), str(bad.id)]},
    )
    session = DummySession()

    def fake_delay(building_id, building_data):
        if building_id == str(bad.id):
            raise RuntimeError("broker down")
        return SimpleNamespace(id=f"task-{building_id}")

    monkeypatch.setattr(processing, "generate_3d_model", SimpleNamespace(delay=fake_delay))

    failures = processing._queue_procedural_generation_jobs(
        session,
        document,
        [(good, {"name": "good"}), (bad, {"name": "bad"})],
    )

    assert failures == [{"building_id": str(bad.id), "error": "broker down"}]
    assert good.specifications["existing"] == "value"
    assert good.specifications["celery_task_id"] == f"task-{good.id}"
    assert bad.generation_status == "failed"
    assert "generation_error" in bad.specifications
    assert document.extracted_data["generation_queue_failures"] == failures
    assert session.commit_calls == 1
    assert session.rollback_calls == 0


def test_queue_procedural_generation_jobs_skips_commit_when_no_jobs(monkeypatch):
    session = DummySession()
    document = SimpleNamespace(extracted_data={})

    monkeypatch.setattr(
        processing,
        "generate_3d_model",
        SimpleNamespace(delay=lambda *args, **kwargs: None),
    )

    assert processing._queue_procedural_generation_jobs(session, document, []) == []
    assert session.commit_calls == 0
    assert session.rollback_calls == 0


class _DummyQuery:
    def __init__(self, building):
        self._building = building

    def filter_by(self, **kwargs):
        return self

    def first(self):
        return self._building


class _DummyAISession:
    def __init__(self, building, linked_zones=None):
        self._building = building
        self._linked_zones = list(linked_zones or [])
        self.executed = []
        self.commit_calls = 0
        self.rollback_calls = 0
        self.closed = False

    def query(self, model):
        return _DummyQuery(self._building)

    def execute(self, statement, *_args, **_kwargs):
        # Project-lock result is ignored; linked-zone invalidation consumes an
        # optional scalar collection supplied by the focused freshness test.
        self.executed.append(statement)
        values = self._linked_zones if "FROM site_zones" in str(statement) else []
        return SimpleNamespace(
            scalars=lambda: SimpleNamespace(all=lambda: values),
        )

    def refresh(self, _value):
        return None

    def commit(self):
        self.commit_calls += 1

    def rollback(self):
        self.rollback_calls += 1

    def close(self):
        self.closed = True


def test_generate_3d_model_ai_treats_deleted_building_as_source_removed(monkeypatch):
    building_id = str(uuid.uuid4())
    session = _DummyAISession(None)

    monkeypatch.setattr(processing, "_get_sync_session", lambda: session)
    monkeypatch.setattr(
        processing,
        "get_engine",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(
            AssertionError("provider must not be created for a removed source")
        ),
    )
    monkeypatch.setattr(
        processing,
        "log_api_usage_sync",
        lambda **_kwargs: (_ for _ in ()).throw(
            AssertionError("removed sources must not record failed provider usage")
        ),
    )
    monkeypatch.setattr(
        processing.generate_3d_model_ai,
        "retry",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("removed sources are terminal and must not retry")
        ),
    )

    task_result = processing.generate_3d_model_ai.apply(args=[building_id, "unused prompt"])

    assert task_result.successful() is True
    assert task_result.get() == {
        "status": "source_removed",
        "building_id": building_id,
    }
    assert session.commit_calls == 0
    assert session.rollback_calls == 0
    assert session.closed is True


def test_generate_3d_model_ai_uses_provider_adapter(monkeypatch):
    from app.generation.engine import GenerationResult
    from app.models.models import SiteZone

    building = SimpleNamespace(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        generation_status="idle",
        generation_prompt=None,
        generation_engine=None,
        architectural_style=None,
        meshy_task_id=None,
        model_url=None,
        lod_urls=None,
        preview_url=None,
        preview_status="idle",
        # No archetype identity -> the archetype cache is bypassed and this
        # test keeps exercising the plain provider path.
        specifications=None,
    )
    linked_zone = SiteZone(
        id=uuid.uuid4(),
        project_id=building.project_id,
        zone_type="building",
        building_id=building.id,
        building_ids=[str(building.id)],
        properties={
            "community_3d": {
                "state": "compiled",
                "kind": "building",
                "generator": "meshy",
            },
        },
    )
    session = _DummyAISession(building, [linked_zone])
    storage_writes = []
    propagated = []
    progress_updates = []

    class FakeProvider:
        engine_id = "meshy"

        def is_available(self):
            return True

        async def run_generation(self, **kwargs):
            kwargs["progress_callback"](0.1, "calling_meshy")
            kwargs["task_callback"]("preview-task")
            kwargs["preview_callback"](b"preview-glb")
            return GenerationResult(
                glb_data=b"final-glb",
                engine="meshy",
                task_id="final-task",
            )

    def fake_upload(key, data, content_type):
        storage_writes.append((key, data, content_type))
        return f"https://storage.test/{key}"

    monkeypatch.setattr(processing, "_get_sync_session", lambda: session)
    monkeypatch.setattr(processing, "get_engine", lambda engine_id: FakeProvider())
    monkeypatch.setattr(processing, "_upload_to_storage", fake_upload)
    monkeypatch.setattr(processing, "_propagate_model_to_siblings", lambda *args: propagated.append(args))
    monkeypatch.setattr(processing, "log_api_usage_sync", lambda **kwargs: None)
    monkeypatch.setattr(
        processing.generate_3d_model_ai, "update_state", lambda **kwargs: progress_updates.append(kwargs)
    )
    monkeypatch.setattr(
        processing.generate_3d_model_ai,
        "retry",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("retry should not be called")),
    )

    result = processing.generate_3d_model_ai.run(
        str(building.id),
        "Tower prompt",
        mode="text",
        engine="meshy",
    )

    # model_url is the browser-reachable /api/v1/files proxy path (NOT the raw
    # storage endpoint _upload_to_storage returns) so the client GLB viewer can
    # actually fetch it.
    assert result == {
        "status": "completed",
        "building_id": str(building.id),
        "model_url": f"/api/v1/files/projects/{building.project_id}/models/{building.id}_ai.glb",
    }
    assert storage_writes == [
        (
            f"projects/{building.project_id}/models/{building.id}_preview.glb",
            b"preview-glb",
            "model/gltf-binary",
        ),
        (
            f"projects/{building.project_id}/models/{building.id}_ai.glb",
            b"final-glb",
            "model/gltf-binary",
        ),
    ]
    assert building.generation_status == "completed"
    assert building.generation_prompt == "Tower prompt"
    assert building.generation_engine == "meshy"
    assert building.meshy_task_id == "final-task"
    assert building.model_url == f"/api/v1/files/projects/{building.project_id}/models/{building.id}_ai.glb"
    assert building.lod_urls == {"0": building.model_url}
    assert any(update["meta"]["step"] == "preview_ready" for update in progress_updates)
    assert propagated
    assert linked_zone.properties["community_3d"]["state"] == "stale"
    assert any("FOR UPDATE" in str(statement) for statement in session.executed)
    assert session.commit_calls >= 4
    assert session.rollback_calls == 0
    assert session.closed is True


# ---------------------------------------------------------------------------
# Meshy runtime ceilings (2026-07-10)
#
# A slow refine used to soft-kill the Celery task mid-upload: the old poll
# ceilings (300s + 600s) summed to EXACTLY soft_time_limit=900s. The model was
# paid for and uploaded, then the row was flipped to "failed" and the whole
# generation retried from scratch (~20 credits per retry).
# ---------------------------------------------------------------------------


def test_soft_time_limit_exceeds_the_sum_of_meshy_poll_timeouts():
    """The bug that killed paid generations: limits stacked flush against each
    other. soft_time_limit must leave headroom above preview + refine."""
    from app.generation.engine import (
        MESHY_MAX_RUNTIME_S,
        MESHY_PREVIEW_TIMEOUT_S,
        MESHY_REFINE_TIMEOUT_S,
    )

    from app.core.config import get_settings

    poll_sum = MESHY_PREVIEW_TIMEOUT_S + MESHY_REFINE_TIMEOUT_S
    task = processing.generate_3d_model_ai
    # Budget covers a full cache wait (claim-losing waiter) PLUS a complete
    # fallback generation — the wait alone must never eat the paid run's time.
    assert task.soft_time_limit == MESHY_MAX_RUNTIME_S + get_settings().archetype_cache_wait_s
    assert (
        task.soft_time_limit - get_settings().archetype_cache_wait_s > poll_sum
    ), "generation budget (after a worst-case cache wait) must exceed preview+refine"
    assert task.time_limit > task.soft_time_limit


def _ai_task_fixture(monkeypatch, run_generation):
    """Wire generate_3d_model_ai against a fake provider/session."""
    building = SimpleNamespace(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        generation_status="idle",
        generation_prompt=None,
        generation_engine=None,
        architectural_style=None,
        meshy_task_id=None,
        model_url=None,
        lod_urls=None,
        preview_url=None,
        preview_status="idle",
        specifications={},
    )
    session = _DummyAISession(building)

    class FakeProvider:
        engine_id = "meshy"

        def is_available(self):
            return True

        async def run_generation(self, **kwargs):
            return await run_generation(**kwargs)

    monkeypatch.setattr(processing, "_get_sync_session", lambda: session)
    monkeypatch.setattr(processing, "get_engine", lambda engine_id: FakeProvider())
    monkeypatch.setattr(processing, "_upload_to_storage", lambda k, d, c: f"https://storage.test/{k}")
    monkeypatch.setattr(processing, "_propagate_model_to_siblings", lambda *a: None)
    monkeypatch.setattr(processing, "log_api_usage_sync", lambda **kw: None)
    monkeypatch.setattr(processing.generate_3d_model_ai, "update_state", lambda **kw: None)
    monkeypatch.setattr(
        processing.generate_3d_model_ai,
        "retry",
        lambda *a, **kw: (_ for _ in ()).throw(AssertionError("retry must not be called")),
    )
    return building, session


def test_meshy_timeout_is_terminal_and_does_not_retry(monkeypatch):
    """A retry re-runs the whole paid generation; timeouts must not retry."""

    async def times_out(**kwargs):
        raise TimeoutError("Meshy task abc timed out after 900s")

    building, _ = _ai_task_fixture(monkeypatch, times_out)

    result = processing.generate_3d_model_ai.run(str(building.id), "p", mode="text", engine="meshy")

    assert result["status"] == "failed"
    assert "timed out" in result["error"]
    assert building.generation_status == "failed"
    assert "timed out" in building.specifications["generation_error"]


def test_soft_time_limit_kill_is_terminal_and_does_not_retry(monkeypatch):
    from celery.exceptions import SoftTimeLimitExceeded

    async def killed(**kwargs):
        raise SoftTimeLimitExceeded()

    building, _ = _ai_task_fixture(monkeypatch, killed)

    result = processing.generate_3d_model_ai.run(str(building.id), "p", mode="text", engine="meshy")

    assert result["status"] == "failed"
    assert building.generation_status == "failed"


def test_post_success_error_never_buries_a_committed_model(monkeypatch):
    """The exact pilot symptom: GLB uploaded and paid for, row said 'failed'.

    A soft-kill can land at any bytecode boundary — including after the success
    commit, in the trailing log line, which sits outside every inner
    try/except. The task must report the completed model, not bury it.
    """
    from celery.exceptions import SoftTimeLimitExceeded

    from app.generation.engine import GenerationResult

    async def ok(**kwargs):
        return GenerationResult(glb_data=b"glb", engine="meshy", task_id="t1", thumbnail_url=None)

    building, _ = _ai_task_fixture(monkeypatch, ok)

    real_info = processing.logger.info

    def late_kill(msg, *args, **kwargs):
        if isinstance(msg, str) and msg.startswith("AI 3D model generated"):
            raise SoftTimeLimitExceeded()
        return real_info(msg, *args, **kwargs)

    monkeypatch.setattr(processing.logger, "info", late_kill)

    result = processing.generate_3d_model_ai.run(str(building.id), "p", mode="text", engine="meshy")

    assert result["status"] == "completed"
    assert result["model_url"].endswith("_ai.glb")
    assert building.generation_status == "completed"
    assert building.model_url.endswith("_ai.glb")
