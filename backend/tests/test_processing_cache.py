"""Archetype cache integration in generate_3d_model_ai.

Runs the Celery task eagerly against the real compose Postgres with a mocked
provider and mocked storage: first same-key building pays (one provider
call), the second cache-hits (zero provider calls, credits_used=0 log row).
"""

import uuid

import pytest
from sqlalchemy import delete, select

import app.tasks.processing as processing
from app.core.security import hash_password
from app.generation.engine import GenerationResult
from app.models.models import (
    ApiUsageLog,
    ArchetypeModelCache,
    Building,
    Project,
    User,
)
from app.tasks.processing import _get_sync_session, generate_3d_model_ai


class FakeProvider:
    engine_id = "meshy"

    def __init__(self):
        self.calls = 0

    def is_available(self) -> bool:
        return True

    async def run_generation(self, **kwargs):
        self.calls += 1
        return GenerationResult(
            engine="meshy",
            glb_data=b"fake-glb-bytes",
            lod_glb_data=None,
            thumbnail_url=None,
            task_id=f"fake-task-{self.calls}",
            metadata={},
        )


@pytest.fixture
def env(monkeypatch):
    """Real DB rows (user/project/2 buildings sharing an archetype key),
    fake provider, no-op storage."""
    session = _get_sync_session()
    arch = f"test_cache_arch_{uuid.uuid4().hex[:10]}"

    user = User(
        email=f"cache-test-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("x"),
        full_name="Cache Test",
        role="editor",
    )
    session.add(user)
    session.flush()
    project = Project(name="Cache Test Project", owner_id=user.id)
    session.add(project)
    session.flush()

    specs = {
        "development_archetype_id": f"{arch}_front_day",
        "development_selected_variant_id": "variant_0",
    }
    buildings = [Building(project_id=project.id, name=f"B{i}", specifications=dict(specs)) for i in range(2)]
    session.add_all(buildings)
    session.commit()
    building_ids = [str(b.id) for b in buildings]

    provider = FakeProvider()
    uploads: list[str] = []
    monkeypatch.setattr(processing, "get_engine", lambda _: provider)
    monkeypatch.setattr(processing, "_upload_to_storage", lambda key, data, ct: uploads.append(key))

    yield session, arch, building_ids, provider, uploads

    session.rollback()
    session.execute(delete(ApiUsageLog).where(ApiUsageLog.building_id.in_([uuid.UUID(b) for b in building_ids])))
    session.execute(delete(ArchetypeModelCache).where(ArchetypeModelCache.archetype_id == arch))
    session.execute(delete(Building).where(Building.id.in_([uuid.UUID(b) for b in building_ids])))
    session.execute(delete(Project).where(Project.id == project.id))
    session.execute(delete(User).where(User.id == user.id))
    session.commit()
    session.close()


def test_second_generation_hits_cache(env):
    session, arch, building_ids, provider, uploads = env

    r1 = generate_3d_model_ai.apply(args=[building_ids[0], "a building", "text"]).get()
    assert r1["status"] == "completed"
    assert provider.calls == 1
    assert "/archetype-cache/" in r1["model_url"]

    r2 = generate_3d_model_ai.apply(args=[building_ids[1], "a building", "text"]).get()
    assert r2["status"] == "completed"
    assert r2.get("cache_hit") is True
    assert provider.calls == 1, "second generation must not call the provider"
    assert r2["model_url"] == r1["model_url"]

    entry = session.execute(select(ArchetypeModelCache).where(ArchetypeModelCache.archetype_id == arch)).scalar_one()
    assert entry.status == "completed"
    assert entry.use_count == 1
    assert entry.model_key.startswith(f"archetype-cache/{arch}/variant_0/meshy/")
    # only ONE model object was ever uploaded
    assert [k for k in uploads if k.endswith(".glb")] == [entry.model_key]

    hit_logs = (
        session.execute(
            select(ApiUsageLog).where(
                ApiUsageLog.building_id == uuid.UUID(building_ids[1]),
                ApiUsageLog.operation == "cache_hit",
            )
        )
        .scalars()
        .all()
    )
    assert len(hit_logs) == 1
    assert float(hit_logs[0].credits_used) == 0


def test_image_mode_bypasses_cache(env):
    session, arch, building_ids, provider, uploads = env

    r = generate_3d_model_ai.apply(args=[building_ids[0], "a building", "image", "data:image/png;base64,xx"]).get()
    assert r["status"] == "completed"
    assert provider.calls == 1
    assert "/archetype-cache/" not in r["model_url"]
    assert (
        session.execute(
            select(ArchetypeModelCache).where(ArchetypeModelCache.archetype_id == arch)
        ).scalar_one_or_none()
        is None
    )


def test_failed_generation_releases_claim(env):
    session, arch, building_ids, provider, uploads = env

    async def boom(**kwargs):
        raise TimeoutError("meshy died")

    provider.run_generation = boom
    r = generate_3d_model_ai.apply(args=[building_ids[0], "a building", "text"]).get()
    assert r["status"] == "failed"

    entry = session.execute(select(ArchetypeModelCache).where(ArchetypeModelCache.archetype_id == arch)).scalar_one()
    assert entry.status == "failed"  # claim released — key is retryable
