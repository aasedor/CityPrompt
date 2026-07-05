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
from app.tasks.processing import _get_sync_session
from app.tasks.worker import celery_app

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
