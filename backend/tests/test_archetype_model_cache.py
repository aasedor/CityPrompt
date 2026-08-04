"""Archetype model cache tests.

normalize_cache_key is pure. The claim/complete lifecycle tests run against
the real compose Postgres (the claim primitive is ON CONFLICT DO NOTHING —
meaningless to test against a mock), using uuid-unique archetype ids and
deleting their rows on teardown.
"""

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import delete

from app.models.models import ArchetypeModelCache
from app.services.archetype_model_cache import (
    STALE_CLAIM_S,
    bump_use_count,
    cache_storage_key,
    claim_entry,
    complete_entry,
    fail_entry,
    get_completed_entry,
    normalize_cache_key,
)
from app.tasks.processing import _get_sync_session


# --- normalize_cache_key (pure) ----------------------------------------------


def test_normalize_plain_archetype_id():
    specs = {"development_archetype_id": "collegiate_gothic"}
    assert normalize_cache_key(specs) == ("collegiate_gothic", "default")


def test_normalize_strips_legacy_front_day_suffix():
    specs = {"development_archetype_id": "collegiate_gothic_front_day"}
    assert normalize_cache_key(specs) == ("collegiate_gothic", "default")


def test_normalize_uses_selected_variant():
    specs = {
        "development_archetype_id": "contemporary_mid_rise_residential",
        "development_selected_variant_id": "contemporary_mid_rise_residential_variant_2",
    }
    # archetype prefix stripped so the key matches the baked-in-id form
    assert normalize_cache_key(specs) == ("contemporary_mid_rise_residential", "variant_2")


def test_normalize_same_key_from_both_variant_forms():
    baked = {"development_archetype_id": "glass_tower_modern_variant_1"}
    selected = {
        "development_archetype_id": "glass_tower_modern",
        "development_selected_variant_id": "glass_tower_modern_variant_1",
    }
    assert (
        normalize_cache_key(baked)
        == normalize_cache_key(selected)
        == (
            "glass_tower_modern",
            "variant_1",
        )
    )


def test_normalize_splits_variant_baked_into_archetype_id():
    specs = {"development_archetype_id": "glass_tower_modern_variant_1"}
    assert normalize_cache_key(specs) == ("glass_tower_modern", "variant_1")


def test_normalize_returns_none_without_archetype():
    assert normalize_cache_key(None) is None
    assert normalize_cache_key({}) is None
    assert normalize_cache_key({"development_archetype_id": "  "}) is None
    assert normalize_cache_key({"development_subcategory": "residential"}) is None


# --- claim/complete lifecycle (real Postgres) ---------------------------------


@pytest.fixture
def db_session():
    session = _get_sync_session()
    created_archetypes: list[str] = []
    yield session, created_archetypes
    session.execute(delete(ArchetypeModelCache).where(ArchetypeModelCache.archetype_id.in_(created_archetypes)))
    session.commit()
    session.close()


def _unique_id() -> str:
    return f"test_arch_{uuid.uuid4().hex[:12]}"


def test_claim_then_complete_then_hit(db_session):
    session, created = db_session
    arch = _unique_id()
    created.append(arch)

    entry, claimed = claim_entry(session, arch, "variant_0", "meshy", generation_prompt="p")
    assert claimed and entry is not None and entry.status == "generating"
    assert get_completed_entry(session, arch, "variant_0", "meshy") is None

    key = cache_storage_key(entry)
    assert key == f"archetype-cache/{arch}/variant_0/meshy/{entry.id}.glb"
    complete_entry(session, entry.id, model_key=key, size_bytes=1234, source_task_id="t1")

    hit = get_completed_entry(session, arch, "variant_0", "meshy")
    assert hit is not None and hit.model_key == key and hit.size_bytes == 1234

    bump_use_count(session, hit.id)
    session.refresh(hit)
    assert hit.use_count == 1


def test_complete_entry_persists_dimension_metadata(db_session):
    session, created = db_session
    arch = _unique_id()
    created.append(arch)
    entry, claimed = claim_entry(session, arch, "default", "meshy")
    assert claimed
    dims = {"aspect": 1.5, "long_per_height": 0.6, "short_per_height": 0.4}
    complete_entry(
        session,
        entry.id,
        model_key=cache_storage_key(entry),
        size_bytes=99,
        metadata={"dimensions": dims},
    )
    hit = get_completed_entry(session, arch, "default", "meshy")
    assert hit is not None
    assert hit.metadata_ == {"dimensions": dims}


def test_complete_entry_without_metadata_leaves_it_null(db_session):
    session, created = db_session
    arch = _unique_id()
    created.append(arch)
    entry, claimed = claim_entry(session, arch, "default", "meshy")
    assert claimed
    complete_entry(session, entry.id, model_key=cache_storage_key(entry), size_bytes=1)
    hit = get_completed_entry(session, arch, "default", "meshy")
    assert hit is not None and hit.metadata_ is None


def test_second_claim_loses_while_first_in_flight(db_session):
    session, created = db_session
    arch = _unique_id()
    created.append(arch)

    _, claimed_first = claim_entry(session, arch, "default", "meshy")
    entry2, claimed_second = claim_entry(session, arch, "default", "meshy")
    assert claimed_first is True
    assert claimed_second is False
    assert entry2 is not None and entry2.status == "generating"


def test_failed_entry_is_reclaimable(db_session):
    session, created = db_session
    arch = _unique_id()
    created.append(arch)

    entry, _ = claim_entry(session, arch, "default", "meshy")
    fail_entry(session, entry.id, "meshy exploded")

    entry2, claimed = claim_entry(session, arch, "default", "meshy")
    assert claimed is True
    assert entry2.id == entry.id  # same row, re-claimed
    assert entry2.status == "generating" and entry2.error is None


def test_stale_generating_claim_is_taken_over(db_session):
    session, created = db_session
    arch = _unique_id()
    created.append(arch)

    entry, _ = claim_entry(session, arch, "default", "meshy")
    # Backdate the claim past the staleness horizon (dead-worker simulation).
    entry.claimed_at = datetime.now(timezone.utc) - timedelta(seconds=STALE_CLAIM_S + 60)
    session.commit()

    entry2, claimed = claim_entry(session, arch, "default", "meshy")
    assert claimed is True and entry2.id == entry.id


def test_different_engines_are_separate_keys(db_session):
    session, created = db_session
    arch = _unique_id()
    created.append(arch)

    _, claimed_meshy = claim_entry(session, arch, "default", "meshy")
    _, claimed_tripo = claim_entry(session, arch, "default", "tripo")
    assert claimed_meshy is True and claimed_tripo is True
