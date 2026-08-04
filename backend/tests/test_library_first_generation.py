"""Library-first model selection in generate_3d_model_ai.

Runs the Celery task eagerly against the real compose Postgres with a mocked
provider and mocked storage: a saved ModelLibraryEntry whose source building
shares the archetype key substitutes for the paid generation (zero provider
calls, credits_used=0 "model_library_hit" log row, released cache claim).
No match, image mode, foreign private entries, and the kill-switch all fall
through to a normal generation.
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
    ModelLibraryEntry,
    Project,
    User,
)
from app.tasks.processing import _get_sync_session, generate_3d_model_ai


class FakeProvider:
    engine_id = "meshy"

    def __init__(self):
        self.calls = 0

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

    def is_available(self) -> bool:
        return True


def _make_user(session, tag: str) -> User:
    user = User(
        email=f"lib-test-{tag}-{uuid.uuid4().hex[:8]}@example.com",
        hashed_password=hash_password("x"),
        full_name="Library Test",
        role="editor",
    )
    session.add(user)
    session.flush()
    return user


def _make_entry(session, owner_id, source_building, **overrides) -> ModelLibraryEntry:
    entry = ModelLibraryEntry(
        owner_id=owner_id,
        source_building_id=source_building.id,
        source_project_id=source_building.project_id,
        name="Saved model",
        category="other",
        model_url=f"/api/v1/files/library/{owner_id}/saved.glb",
        lod_urls={"1": f"/api/v1/files/library/{owner_id}/saved_lod1.glb"},
        generation_engine="meshy",
        **overrides,
    )
    session.add(entry)
    session.commit()
    return entry


@pytest.fixture
def env(monkeypatch):
    """Real DB rows (owner/project, a completed source building and a target
    sharing an archetype key), fake provider, no-op storage, recorded copies."""
    session = _get_sync_session()
    arch = f"test_lib_arch_{uuid.uuid4().hex[:10]}"

    user = _make_user(session, "owner")
    project = Project(name="Library Test Project", owner_id=user.id)
    session.add(project)
    session.flush()

    # Legacy "_front_day" suffix on purpose — the library match must resolve
    # raw ids through the same normalizer the archetype cache uses.
    specs = {
        "development_archetype_id": f"{arch}_front_day",
        "development_selected_variant_id": "variant_0",
    }
    source = Building(
        project_id=project.id,
        name="Source",
        specifications=dict(specs),
        model_url="/api/v1/files/library-src/ignored.glb",
        generation_status="completed",
    )
    target = Building(project_id=project.id, name="Target", specifications=dict(specs))
    session.add_all([source, target])
    session.commit()

    provider = FakeProvider()
    uploads: list[str] = []
    copies: list[tuple[str, str]] = []
    monkeypatch.setattr(processing, "get_engine", lambda _: provider)
    monkeypatch.setattr(processing, "_upload_to_storage", lambda key, data, ct: uploads.append(key))
    monkeypatch.setattr(
        processing,
        "_copy_storage_object",
        lambda src, dest, content_type="model/gltf-binary": copies.append((src, dest)),
    )

    yield session, arch, user, project, source, target, provider, uploads, copies

    session.rollback()
    building_ids = [source.id, target.id]
    session.execute(delete(ApiUsageLog).where(ApiUsageLog.building_id.in_(building_ids)))
    session.execute(delete(ModelLibraryEntry).where(ModelLibraryEntry.source_building_id.in_(building_ids)))
    session.execute(delete(ArchetypeModelCache).where(ArchetypeModelCache.archetype_id == arch))
    session.execute(delete(Building).where(Building.id.in_(building_ids)))
    session.execute(delete(Project).where(Project.id == project.id))
    session.execute(delete(User).where(User.id == user.id))
    session.commit()
    session.close()


def test_library_hit_short_circuits_generation(env):
    session, arch, user, project, source, target, provider, uploads, copies = env
    entry = _make_entry(session, user.id, source)

    r = generate_3d_model_ai.apply(args=[str(target.id), "a building", "text"]).get()
    assert r["status"] == "completed"
    assert r.get("library_hit") is True
    assert provider.calls == 0, "library hit must not call the provider"

    dest_key = f"projects/{project.id}/models/{target.id}_ai.glb"
    assert r["model_url"] == f"/api/v1/files/{dest_key}"
    assert (f"library/{user.id}/saved.glb", dest_key) in copies
    assert any(src.endswith("saved_lod1.glb") for src, _ in copies)
    assert uploads == [], "nothing new is generated, so nothing is uploaded"

    session.refresh(target)
    assert target.generation_status == "completed"
    assert target.model_url == r["model_url"]
    assert target.lod_urls["0"] == r["model_url"]
    assert target.lod_urls["1"] == f"/api/v1/files/projects/{project.id}/models/{target.id}_lod1.glb"

    session.refresh(entry)
    assert entry.use_count == 1

    # The claim taken before the library was consulted must be released so
    # same-key waiters don't block until stale takeover.
    cache_row = session.execute(
        select(ArchetypeModelCache).where(ArchetypeModelCache.archetype_id == arch)
    ).scalar_one()
    assert cache_row.status == "failed"
    assert "model library hit" in (cache_row.error or "")

    hit_logs = (
        session.execute(
            select(ApiUsageLog).where(
                ApiUsageLog.building_id == target.id,
                ApiUsageLog.operation == "model_library_hit",
            )
        )
        .scalars()
        .all()
    )
    assert len(hit_logs) == 1
    assert float(hit_logs[0].credits_used) == 0


def test_no_library_match_falls_through_to_generation(env):
    session, arch, user, project, source, target, provider, uploads, copies = env

    r = generate_3d_model_ai.apply(args=[str(target.id), "a building", "text"]).get()
    assert r["status"] == "completed"
    assert "library_hit" not in r
    assert provider.calls == 1
    assert "/archetype-cache/" in r["model_url"]
    assert copies == []


def test_image_mode_never_consults_library(env):
    session, arch, user, project, source, target, provider, uploads, copies = env
    entry = _make_entry(session, user.id, source)

    r = generate_3d_model_ai.apply(args=[str(target.id), "a building", "image", "data:image/png;base64,xx"]).get()
    assert r["status"] == "completed"
    assert "library_hit" not in r
    assert provider.calls == 1
    assert copies == []

    session.refresh(entry)
    assert entry.use_count == 0


def test_kill_switch_restores_old_behavior(env, monkeypatch):
    session, arch, user, project, source, target, provider, uploads, copies = env
    entry = _make_entry(session, user.id, source)
    monkeypatch.setattr(processing.settings, "model_library_first_enabled", False)

    r = generate_3d_model_ai.apply(args=[str(target.id), "a building", "text"]).get()
    assert r["status"] == "completed"
    assert "library_hit" not in r
    assert provider.calls == 1
    assert copies == []

    session.refresh(entry)
    assert entry.use_count == 0


def test_foreign_private_entry_is_not_used(env):
    session, arch, user, project, source, target, provider, uploads, copies = env
    other = _make_user(session, "other")
    try:
        _make_entry(session, other.id, source, is_public=False)

        r = generate_3d_model_ai.apply(args=[str(target.id), "a building", "text"]).get()
        assert r["status"] == "completed"
        assert "library_hit" not in r
        assert provider.calls == 1
    finally:
        session.rollback()
        session.execute(delete(ModelLibraryEntry).where(ModelLibraryEntry.owner_id == other.id))
        session.execute(delete(User).where(User.id == other.id))
        session.commit()


def test_foreign_public_entry_is_used(env):
    session, arch, user, project, source, target, provider, uploads, copies = env
    other = _make_user(session, "other")
    try:
        _make_entry(session, other.id, source, is_public=True)

        r = generate_3d_model_ai.apply(args=[str(target.id), "a building", "text"]).get()
        assert r["status"] == "completed"
        assert r.get("library_hit") is True
        assert provider.calls == 0
    finally:
        session.rollback()
        session.execute(delete(ModelLibraryEntry).where(ModelLibraryEntry.owner_id == other.id))
        session.execute(delete(User).where(User.id == other.id))
        session.commit()
