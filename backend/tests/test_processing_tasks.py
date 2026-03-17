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

    monkeypatch.setattr(processing, '_sync_engine', None)
    monkeypatch.setattr(processing, '_sync_session_factory', None)

    def fake_create_engine(*args, **kwargs):
        calls.append((args, kwargs))
        return sentinel

    monkeypatch.setattr(processing, 'create_engine', fake_create_engine)

    assert processing._get_sync_engine() is sentinel
    assert processing._get_sync_engine() is sentinel
    assert len(calls) == 1
    assert calls[0][1]['pool_pre_ping'] is True


def test_queue_procedural_generation_jobs_records_task_ids_and_failures(monkeypatch):
    good = SimpleNamespace(
        id=uuid.uuid4(),
        specifications={'existing': 'value'},
        generation_status='generating',
    )
    bad = SimpleNamespace(
        id=uuid.uuid4(),
        specifications=None,
        generation_status='generating',
    )
    document = SimpleNamespace(
        extracted_data={'building_ids': [str(good.id), str(bad.id)]},
    )
    session = DummySession()

    def fake_delay(building_id, building_data):
        if building_id == str(bad.id):
            raise RuntimeError('broker down')
        return SimpleNamespace(id=f'task-{building_id}')

    monkeypatch.setattr(processing, 'generate_3d_model', SimpleNamespace(delay=fake_delay))

    failures = processing._queue_procedural_generation_jobs(
        session,
        document,
        [(good, {'name': 'good'}), (bad, {'name': 'bad'})],
    )

    assert failures == [{'building_id': str(bad.id), 'error': 'broker down'}]
    assert good.specifications['existing'] == 'value'
    assert good.specifications['celery_task_id'] == f'task-{good.id}'
    assert bad.generation_status == 'failed'
    assert 'generation_error' in bad.specifications
    assert document.extracted_data['generation_queue_failures'] == failures
    assert session.commit_calls == 1
    assert session.rollback_calls == 0


def test_queue_procedural_generation_jobs_skips_commit_when_no_jobs(monkeypatch):
    session = DummySession()
    document = SimpleNamespace(extracted_data={})

    monkeypatch.setattr(
        processing,
        'generate_3d_model',
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
    def __init__(self, building):
        self._building = building
        self.commit_calls = 0
        self.rollback_calls = 0
        self.closed = False

    def query(self, model):
        return _DummyQuery(self._building)

    def commit(self):
        self.commit_calls += 1

    def rollback(self):
        self.rollback_calls += 1

    def close(self):
        self.closed = True


def test_generate_3d_model_ai_uses_provider_adapter(monkeypatch):
    from app.generation.engine import GenerationResult

    building = SimpleNamespace(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        generation_status='idle',
        generation_prompt=None,
        generation_engine=None,
        architectural_style=None,
        meshy_task_id=None,
        model_url=None,
        lod_urls=None,
        preview_url=None,
        preview_status='idle',
    )
    session = _DummyAISession(building)
    storage_writes = []
    propagated = []
    progress_updates = []

    class FakeProvider:
        engine_id = 'meshy'

        def is_available(self):
            return True

        async def run_generation(self, **kwargs):
            kwargs['progress_callback'](0.1, 'calling_meshy')
            kwargs['task_callback']('preview-task')
            kwargs['preview_callback'](b'preview-glb')
            return GenerationResult(
                glb_data=b'final-glb',
                engine='meshy',
                task_id='final-task',
            )

    def fake_upload(key, data, content_type):
        storage_writes.append((key, data, content_type))
        return f'https://storage.test/{key}'

    monkeypatch.setattr(processing, '_get_sync_session', lambda: session)
    monkeypatch.setattr(processing, 'get_engine', lambda engine_id: FakeProvider())
    monkeypatch.setattr(processing, '_upload_to_storage', fake_upload)
    monkeypatch.setattr(processing, '_propagate_model_to_siblings', lambda *args: propagated.append(args))
    monkeypatch.setattr(processing, 'log_api_usage_sync', lambda **kwargs: None)
    monkeypatch.setattr(processing.generate_3d_model_ai, 'update_state', lambda **kwargs: progress_updates.append(kwargs))
    monkeypatch.setattr(processing.generate_3d_model_ai, 'retry', lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError('retry should not be called')))

    result = processing.generate_3d_model_ai.run(
        str(building.id),
        'Tower prompt',
        mode='text',
        engine='meshy',
    )

    assert result == {
        'status': 'completed',
        'building_id': str(building.id),
        'model_url': f'https://storage.test/projects/{building.project_id}/models/{building.id}_ai.glb',
    }
    assert storage_writes == [
        (
            f'projects/{building.project_id}/models/{building.id}_preview.glb',
            b'preview-glb',
            'model/gltf-binary',
        ),
        (
            f'projects/{building.project_id}/models/{building.id}_ai.glb',
            b'final-glb',
            'model/gltf-binary',
        ),
    ]
    assert building.generation_status == 'completed'
    assert building.generation_prompt == 'Tower prompt'
    assert building.generation_engine == 'meshy'
    assert building.meshy_task_id == 'final-task'
    assert building.model_url == f'https://storage.test/projects/{building.project_id}/models/{building.id}_ai.glb'
    assert building.lod_urls == {'0': building.model_url}
    assert any(update['meta']['step'] == 'preview_ready' for update in progress_updates)
    assert propagated
    assert session.commit_calls >= 4
    assert session.rollback_calls == 0
    assert session.closed is True
