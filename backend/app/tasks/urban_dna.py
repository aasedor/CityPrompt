"""Celery task: build the Urban Intelligence DNA for a site-boundary zone.

Decomposed per the Celery budget (worker soft limit is 300s): this task does
fetch + spatial + assembly only; planning-agent scenario runs are separate
tasks (M3). A ``SoftTimeLimitExceeded`` marks the snapshot ``partial`` (or
``failed`` if nothing was assembled) — a snapshot can never hang in
``pending`` forever.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timedelta, timezone

from celery.exceptions import SoftTimeLimitExceeded
from geoalchemy2.shape import to_shape
from shapely.geometry import Polygon

from app.services.city_connector import get_connector_for_site
from app.services.city_connector.base import DatasetFetchResult, DatasetSpec
from app.services.urban_dna.builder import build_dna
from app.services.urban_dna.schema import DNA_SCHEMA_VERSION
from app.tasks.worker import celery_app


def _get_sync_session():
    # Lazy import: app.tasks.processing itself imports app.tasks.worker, which
    # imports this module — a top-level import here is a circular-import trap.
    from app.tasks.processing import _get_sync_session as factory

    return factory()

logger = logging.getLogger(__name__)


class PostgresDatasetCache:
    """DB-backed DatasetCacheProtocol using the task's sync session."""

    def __init__(self, session):
        self._session = session

    async def get(self, spec: DatasetSpec, bbox_hash: str):
        from app.models.models import DatasetCache

        row = (
            self._session.query(DatasetCache)
            .filter(
                DatasetCache.dataset_id == spec.id,
                DatasetCache.dataset_version == spec.dataset_version,
                DatasetCache.bbox_hash == bbox_hash,
                DatasetCache.expires_at > datetime.now(timezone.utc),
            )
            .order_by(DatasetCache.fetched_at.desc())
            .first()
        )
        return row

    async def set(self, spec: DatasetSpec, bbox_hash: str, result: DatasetFetchResult) -> None:
        from app.models.models import DatasetCache

        now = datetime.now(timezone.utc)
        self._session.add(
            DatasetCache(
                dataset_id=spec.id,
                dataset_version=spec.dataset_version,
                bbox_hash=bbox_hash,
                features=result.features,
                feature_count=len(result.features),
                source_status=result.status,
                fetched_at=now,
                expires_at=now + timedelta(days=spec.refresh_days),
            )
        )
        self._session.commit()


def _field_value(section, name: str):
    field = section.fields.get(name)
    return field.value if field is not None else None


def _make_policy_synthesizer(session, snapshot, city_id: str):
    """Policy phase closure: checkpoints the dataset-phase DNA, then retrieval + synthesis."""

    async def synthesize(dna):
        # Checkpoint before the LLM call — a soft-time-limit mid-synthesis
        # leaves a usable 'partial' snapshot rather than nothing.
        snapshot.dna = dna.model_dump(mode="json")
        snapshot.status = "partial"
        session.commit()

        from app.models.models import PolicyDocument
        from app.services.policy_intelligence.retrieval import (
            ChunkRecord,
            build_query_terms,
            rank_chunks,
        )
        from app.services.policy_intelligence.synthesis import synthesize_policy_insight

        now = datetime.now(timezone.utc)
        documents = (
            session.query(PolicyDocument)
            .filter(PolicyDocument.city == city_id, PolicyDocument.status == "active")
            .all()
        )
        effective = [
            d for d in documents
            if (d.effective_date is None or d.effective_date <= now)
            and (d.repealed_date is None or d.repealed_date > now)
        ]

        warnings: list[dict] = []
        for document in effective:
            if document.repealed_date is not None and (document.repealed_date - now).days < 365:
                warnings.append({
                    "code": "POLICY_INSTRUMENT_SUNSETTING",
                    "severity": "warning",
                    "message": f"{document.title} is repealed effective "
                               f"{document.repealed_date.date().isoformat()} — cite with care.",
                    "source_phase": "policy_intelligence",
                })

        site_facts = {
            "districts": _field_value(dna.land_use, "districts"),
            "dominant_district": _field_value(dna.land_use, "dominant_district"),
            "lap_name": _field_value(dna.land_use, "lap_name"),
            "community_name": _field_value(dna.site, "community_name"),
            "applicable_plans": _field_value(dna.policy, "applicable_plans"),
            "adjacent_uses": _field_value(dna.land_use, "adjacent_uses"),
            "frontage_streets": _field_value(dna.mobility, "frontage_streets"),
        }

        if not effective:
            insight, synth_warnings = await synthesize_policy_insight(
                site_facts=site_facts, chunks=[], corpus_status="absent", documents_consulted=[],
            )
            return {"insight": insight.model_dump()}, warnings + synth_warnings, insight.confidence

        records = [
            ChunkRecord(
                chunk_id=str(chunk.id),
                document_slug=document.slug,
                document_title=document.title,
                section_label=chunk.section_label,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                text=chunk.text,
            )
            for document in effective
            for chunk in document.chunks
        ]
        query_terms = build_query_terms(site_facts, topics=[
            "density", "height", "setback", "parking", "transit", "pedestrian",
            "cycling", "tree canopy", "flood", "housing", "affordable", "heritage",
            "climate", "complete streets", "emergency access",
        ])
        chunks = rank_chunks(records, query_terms)
        corpus_status = "complete" if len(effective) >= 4 else "partial"

        insight, synth_warnings = await synthesize_policy_insight(
            site_facts=site_facts,
            chunks=chunks,
            corpus_status=corpus_status,
            documents_consulted=[d.slug for d in effective],
        )
        return {"insight": insight.model_dump()}, warnings + synth_warnings, insight.confidence

    return synthesize


@celery_app.task(bind=True, name="generate_urban_dna")
def generate_urban_dna(self, snapshot_id: str) -> dict:
    """Fill a pending UrbanDnaSnapshot. Data problems degrade; only infra fails."""
    from app.models.models import SiteZone, UrbanDnaSnapshot

    session = _get_sync_session()
    snapshot = None
    try:
        snapshot = session.query(UrbanDnaSnapshot).filter_by(id=uuid.UUID(snapshot_id)).first()
        if snapshot is None:
            logger.error("UrbanDnaSnapshot %s not found", snapshot_id)
            return {"status": "failed", "error": "snapshot not found"}

        zone = session.query(SiteZone).filter_by(id=snapshot.zone_id).first()
        if zone is None:
            snapshot.status = "failed"
            snapshot.error = "zone not found"
            session.commit()
            return {"status": "failed", "error": "zone not found"}

        site_shape = to_shape(zone.geometry)
        site_polygon = site_shape if isinstance(site_shape, Polygon) else site_shape.convex_hull

        connector = get_connector_for_site(site_polygon)
        snapshot.city_id = connector.city_id
        snapshot.status = "pending"
        session.commit()

        dna = asyncio.run(
            build_dna(
                site_polygon=site_polygon,
                connector=connector,
                project_id=str(snapshot.project_id),
                zone_id=str(snapshot.zone_id),
                cache=PostgresDatasetCache(session),
                policy_synthesizer=_make_policy_synthesizer(session, snapshot, connector.city_id),
            )
        )

        snapshot.dna = dna.model_dump(mode="json")
        snapshot.dna_schema_version = DNA_SCHEMA_VERSION
        snapshot.overall_confidence = dna.overall_confidence
        snapshot.status = "complete"
        snapshot.error = None
        session.commit()
        logger.info(
            "Urban DNA %s complete: city=%s confidence=%.2f missing=%d",
            snapshot_id, dna.city_id, dna.overall_confidence, len(dna.missing_datasets),
        )
        return {"status": "complete", "overall_confidence": dna.overall_confidence}

    except SoftTimeLimitExceeded:
        logger.warning("Urban DNA %s hit the soft time limit", snapshot_id)
        try:
            session.rollback()
            if snapshot is not None:
                snapshot.status = "partial" if snapshot.dna else "failed"
                snapshot.error = "generation exceeded the worker time budget"
                session.commit()
        except Exception:  # noqa: BLE001
            logger.exception("Failed to mark snapshot %s after soft time limit", snapshot_id)
        return {"status": "partial"}

    except Exception as exc:  # noqa: BLE001
        logger.exception("Urban DNA generation failed for %s", snapshot_id)
        try:
            session.rollback()
            if snapshot is not None:
                snapshot.status = "failed"
                snapshot.error = str(exc)[:2000]
                session.commit()
        except Exception:  # noqa: BLE001
            logger.exception("Failed to mark snapshot %s failed", snapshot_id)
        return {"status": "failed", "error": str(exc)}

    finally:
        session.close()
