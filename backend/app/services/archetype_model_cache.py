"""
Archetype model cache — generate a building GLB once per
(archetype_id, variant_id, engine), reuse it everywhere.

Claim protocol (sync, runs in the Celery worker):
  1. claim_entry() INSERTs a status='generating' row; ON CONFLICT DO NOTHING
     makes exactly one worker the claimant for a key.
  2. The claimant generates, uploads to the immutable key
     archetype-cache/{archetype}/{variant}/{engine}/{cache_id}.glb, then
     complete_entry(). On error, fail_entry() releases the key for retry.
  3. Losers poll get_completed_entry() (bounded by
     settings.archetype_cache_wait_s) and fall back to an uncached
     generation on failure/timeout.

Stale claims (worker died mid-generation) are taken over once claimed_at is
older than the Meshy runtime ceiling.
"""

import logging
import re
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.generation.engine import MESHY_MAX_RUNTIME_S
from app.models.models import ArchetypeModelCache

logger = logging.getLogger(__name__)

# Zone creation historically stored archetype ids as "{seed_id}_front_day"
# (see model_library.py archetype-previews), and some ids arrive with the
# variant baked in as "{archetype_id}_variant_N".
_LEGACY_SUFFIX = "_front_day"
_VARIANT_RE = re.compile(r"^(?P<base>.+)_(?P<variant>variant_\d+)$")

# A 'generating' claim older than this is presumed dead and taken over.
STALE_CLAIM_S = MESHY_MAX_RUNTIME_S + 120


def normalize_cache_key(specs: dict | None) -> tuple[str, str] | None:
    """Resolve Building.specifications to a (archetype_id, variant_id) cache
    key, or None when the building has no archetype identity to cache under."""
    if not specs:
        return None
    raw = (specs.get("development_archetype_id") or "").strip()
    if not raw:
        return None
    archetype_id = raw.replace(_LEGACY_SUFFIX, "")

    variant_id = (specs.get("development_selected_variant_id") or "").strip()
    match = _VARIANT_RE.match(archetype_id)
    if match:
        archetype_id = match.group("base")
        variant_id = variant_id or match.group("variant")

    # Variant ids usually embed the archetype id ("glass_tower_modern_variant_1");
    # strip it so the same logical variant yields ONE key regardless of whether
    # it arrived via selected_variant_id or baked into the archetype id.
    if variant_id.startswith(f"{archetype_id}_"):
        variant_id = variant_id[len(archetype_id) + 1 :]

    return archetype_id, variant_id or "default"


def cache_storage_key(entry: ArchetypeModelCache) -> str:
    """Immutable MinIO key for a cache entry's GLB. Includes the row id so a
    future regeneration writes a NEW key — existing buildings keep working."""
    return f"archetype-cache/{entry.archetype_id}/{entry.variant_id}/" f"{entry.engine}/{entry.id}.glb"


# --- sync API (Celery worker) ------------------------------------------------


def get_completed_entry(
    session: Session, archetype_id: str, variant_id: str, engine: str
) -> ArchetypeModelCache | None:
    return session.execute(
        select(ArchetypeModelCache).where(
            ArchetypeModelCache.archetype_id == archetype_id,
            ArchetypeModelCache.variant_id == variant_id,
            ArchetypeModelCache.engine == engine,
            ArchetypeModelCache.status == "completed",
        )
    ).scalar_one_or_none()


def claim_entry(
    session: Session,
    archetype_id: str,
    variant_id: str,
    engine: str,
    *,
    generation_mode: str = "text",
    generation_prompt: str | None = None,
) -> tuple[ArchetypeModelCache | None, bool]:
    """Try to become the generator for a key.

    Returns (entry, claimed): claimed=True means this caller must generate
    and complete/fail the entry. claimed=False with an entry means another
    worker owns it (completed or in-flight). (None, False) means the row
    vanished mid-race — treat as uncacheable this round.
    """
    now = datetime.now(timezone.utc)
    result = session.execute(
        pg_insert(ArchetypeModelCache)
        .values(
            id=uuid.uuid4(),
            archetype_id=archetype_id,
            variant_id=variant_id,
            engine=engine,
            status="generating",
            generation_mode=generation_mode,
            generation_prompt=generation_prompt,
            claimed_at=now,
        )
        .on_conflict_do_nothing(index_elements=["archetype_id", "variant_id", "engine"])
        .returning(ArchetypeModelCache.id)
    )
    session.commit()
    inserted_id = result.scalar_one_or_none()
    if inserted_id is not None:
        entry = session.get(ArchetypeModelCache, inserted_id)
        return entry, True

    entry = session.execute(
        select(ArchetypeModelCache).where(
            ArchetypeModelCache.archetype_id == archetype_id,
            ArchetypeModelCache.variant_id == variant_id,
            ArchetypeModelCache.engine == engine,
        )
    ).scalar_one_or_none()
    if entry is None:
        return None, False
    if entry.status == "completed":
        return entry, False

    # failed row, or a stale claim from a dead worker → take it over
    # (optimistic guard on claimed_at so only one taker wins).
    stale_before = now - timedelta(seconds=STALE_CLAIM_S)
    takeover = session.execute(
        update(ArchetypeModelCache)
        .where(
            ArchetypeModelCache.id == entry.id,
            (ArchetypeModelCache.status == "failed")
            | ((ArchetypeModelCache.status == "generating") & (ArchetypeModelCache.claimed_at < stale_before)),
        )
        .values(
            status="generating",
            claimed_at=now,
            error=None,
            generation_mode=generation_mode,
            generation_prompt=generation_prompt,
        )
        .returning(ArchetypeModelCache.id)
    )
    session.commit()
    if takeover.scalar_one_or_none() is not None:
        session.refresh(entry)
        return entry, True
    session.refresh(entry)
    return entry, False


def complete_entry(
    session: Session,
    cache_id: uuid.UUID,
    *,
    model_key: str,
    size_bytes: int,
    source_task_id: str | None = None,
    source_building_id: uuid.UUID | None = None,
    thumbnail_key: str | None = None,
    lod_keys: dict | None = None,
    metadata: dict | None = None,
) -> None:
    values: dict = {
        "status": "completed",
        "model_key": model_key,
        "size_bytes": size_bytes,
        "source_task_id": source_task_id,
        "source_building_id": source_building_id,
        "thumbnail_key": thumbnail_key,
        "lod_keys": lod_keys,
        "error": None,
    }
    if metadata is not None:
        values["metadata_"] = metadata
    session.execute(update(ArchetypeModelCache).where(ArchetypeModelCache.id == cache_id).values(**values))
    session.commit()


def fail_entry(session: Session, cache_id: uuid.UUID, error: str) -> None:
    session.execute(
        update(ArchetypeModelCache)
        .where(ArchetypeModelCache.id == cache_id)
        .values(status="failed", error=error[:2000])
    )
    session.commit()


def set_entry_thumbnail(session: Session, cache_id: uuid.UUID, thumbnail_key: str) -> None:
    session.execute(
        update(ArchetypeModelCache).where(ArchetypeModelCache.id == cache_id).values(thumbnail_key=thumbnail_key)
    )
    session.commit()


def bump_use_count(session: Session, cache_id: uuid.UUID) -> None:
    session.execute(
        update(ArchetypeModelCache)
        .where(ArchetypeModelCache.id == cache_id)
        .values(use_count=ArchetypeModelCache.use_count + 1)
    )
    session.commit()


# --- async API (FastAPI request path) ----------------------------------------


async def has_completed_entry(db: AsyncSession, archetype_id: str, variant_id: str, engine: str) -> bool:
    """Advisory probe used at enqueue time (generate-all stagger bypass).
    The worker re-checks authoritatively."""
    result = await db.execute(
        select(ArchetypeModelCache.id).where(
            ArchetypeModelCache.archetype_id == archetype_id,
            ArchetypeModelCache.variant_id == variant_id,
            ArchetypeModelCache.engine == engine,
            ArchetypeModelCache.status == "completed",
        )
    )
    return result.scalar_one_or_none() is not None
