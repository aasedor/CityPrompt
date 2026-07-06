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
    """DB-backed DatasetCacheProtocol using the task's sync session.

    A failed statement poisons the shared sync session (every later statement
    raises PendingRollbackError, which would mark a fully-built DNA 'failed'),
    so both methods roll back before re-raising to the builder's guard.
    """

    def __init__(self, session):
        self._session = session

    async def get(self, spec: DatasetSpec, bbox_hash: str):
        from app.models.models import DatasetCache

        try:
            return (
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
        except Exception:
            self._session.rollback()
            raise

    async def set(self, spec: DatasetSpec, bbox_hash: str, result: DatasetFetchResult) -> None:
        from app.models.models import DatasetCache

        now = datetime.now(timezone.utc)
        try:
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
        except Exception:
            self._session.rollback()
            raise


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
                # Detail stays in the worker logs — raw exception text can leak
                # infrastructure internals to any project viewer via the API.
                snapshot.error = f"generation failed ({type(exc).__name__}) — see worker logs"
                session.commit()
        except Exception:  # noqa: BLE001
            logger.exception("Failed to mark snapshot %s failed", snapshot_id)
        return {"status": "failed", "error": type(exc).__name__}

    finally:
        session.close()


@celery_app.task(bind=True, name="run_urban_dna_scenario")
def run_urban_dna_scenario(self, scenario_row_id: str) -> dict:
    """Run one planning-agent scenario against its snapshot's DNA.

    One task per scenario keeps each run well inside the 300s soft limit. The
    API dispatches runs independently (baseline first, others delayed) — a
    failed or killed run never strands its siblings.
    """
    from app.models.models import SiteZone, UrbanDnaScenario
    from app.services.planning_agents.coordinator import (
        diff_scenarios,
        merge_recommendations,
        write_explanation,
    )
    from app.services.planning_agents.runner import estimate_cost_usd, run_expert_panel
    from app.services.planning_agents.scenarios import BASELINE_SCENARIO_ID, SCENARIO_PRESETS
    from app.services.planning_agents.schemas import MergedParameter, ScenarioResult
    from app.services.urban_dna.schema import ValidationNote

    session = _get_sync_session()
    row = None
    try:
        row = session.query(UrbanDnaScenario).filter_by(id=uuid.UUID(scenario_row_id)).first()
        if row is None:
            return {"status": "failed", "error": "scenario row not found"}

        definition = SCENARIO_PRESETS.get(row.scenario_id)
        if definition is None:
            row.status = "failed"
            row.error = f"unknown scenario preset {row.scenario_id}"
            session.commit()
            return {"status": "failed", "error": row.error}

        snapshot = row.snapshot
        if snapshot is None or not snapshot.dna:
            row.status = "failed"
            row.error = "snapshot has no DNA"
            session.commit()
            return {"status": "failed", "error": row.error}

        row.status = "running"
        session.commit()

        async def _run() -> ScenarioResult:
            expert_sets, usage_records, warnings = await run_expert_panel(snapshot.dna, definition)
            plan_parameters, trade_offs = merge_recommendations(expert_sets, definition.philosophy)

            baseline_params = None
            if row.scenario_id != BASELINE_SCENARIO_ID:
                baseline_row = (
                    session.query(UrbanDnaScenario)
                    .filter_by(snapshot_id=row.snapshot_id, scenario_id=BASELINE_SCENARIO_ID, status="complete")
                    .order_by(UrbanDnaScenario.created_at.desc())
                    .first()
                )
                if baseline_row is not None and baseline_row.payload:
                    baseline_params = {
                        path: MergedParameter(**merged)
                        for path, merged in (baseline_row.payload.get("plan_parameters") or {}).items()
                    }
                else:
                    warnings.append(ValidationNote(
                        code="BASELINE_UNAVAILABLE", severity="info",
                        message="as_of_right baseline not complete yet; diff shows all parameters.",
                        source_phase="coordinator",
                    ))

            changed = diff_scenarios(baseline_params, plan_parameters)
            explanation = await write_explanation(definition, changed, trade_offs)

            # Derived statistics (P1: parameter mode). Site area from the real
            # boundary geometry — UrbanDNA v1 doesn't persist it.
            from app.services import spatial_engine as se
            from app.services.plan_metrics import compute_metrics

            metrics_report = None
            try:
                zone = session.query(SiteZone).filter_by(id=snapshot.zone_id).first()
                if zone is not None:
                    site_shape = to_shape(zone.geometry)
                    site_poly = site_shape if isinstance(site_shape, Polygon) else site_shape.convex_hull
                    frame = se.SiteFrame.from_wgs84(site_poly)
                    metrics_report = compute_metrics(
                        scenario_id=definition.scenario_id,
                        dna=snapshot.dna,
                        parameters={p: m.model_dump() for p, m in plan_parameters.items()},
                        geometry_inputs={"site_area_m2": frame.area_m2},
                    )
            except SoftTimeLimitExceeded:
                raise
            except Exception as exc:  # noqa: BLE001 — metrics degrade, run continues
                logger.warning("Metrics derivation failed for %s: %s", definition.scenario_id, exc)
                warnings.append(ValidationNote(
                    code="METRICS_UNAVAILABLE", severity="warning",
                    message=f"Derived statistics unavailable: {exc}", source_phase="coordinator",
                ))

            total_in = sum(u["input_tokens"] for u in usage_records)
            total_out = sum(u["output_tokens"] for u in usage_records)
            cost = sum(
                estimate_cost_usd(u["model"], u["input_tokens"], u["output_tokens"])
                for u in usage_records
            )
            return ScenarioResult(
                scenario_id=definition.scenario_id,
                label=definition.label,
                philosophy=definition.philosophy,
                plan_parameters=plan_parameters,
                trade_offs=trade_offs,
                expert_summaries={s.agent_id: s.summary for s in expert_sets if not s.failed},
                explanation=explanation,
                usage={"input_tokens": total_in, "output_tokens": total_out,
                       "estimated_cost_usd": round(cost, 3)},
                warnings=warnings,
                metrics=metrics_report.model_dump(mode="json") if metrics_report else None,
            )

        result = asyncio.run(_run())
        row.payload = result.model_dump(mode="json")
        row.status = "complete"
        row.error = None
        session.commit()
        logger.info(
            "Scenario %s (%s) complete: %d parameters, %d trade-offs, ~$%.2f",
            row.scenario_id, scenario_row_id, len(result.plan_parameters),
            len(result.trade_offs), result.usage.get("estimated_cost_usd", 0.0),
        )
        return {"status": "complete", "parameters": len(result.plan_parameters)}

    except SoftTimeLimitExceeded:
        logger.warning("Scenario %s hit the soft time limit", scenario_row_id)
        try:
            session.rollback()
            if row is not None:
                row.status = "failed"
                row.error = "scenario run exceeded the worker time budget"
                session.commit()
        except Exception:  # noqa: BLE001
            logger.exception("Failed to mark scenario %s after soft time limit", scenario_row_id)
        return {"status": "failed"}

    except Exception as exc:  # noqa: BLE001
        logger.exception("Scenario run failed for %s", scenario_row_id)
        try:
            session.rollback()
            if row is not None:
                row.status = "failed"
                row.error = f"scenario run failed ({type(exc).__name__}) — see worker logs"
                session.commit()
        except Exception:  # noqa: BLE001
            logger.exception("Failed to mark scenario %s failed", scenario_row_id)
        return {"status": "failed", "error": type(exc).__name__}

    finally:
        session.close()


def _set_plan_state(session, row, **fields) -> None:
    payload = dict(row.payload or {})
    plan = dict(payload.get("plan") or {})
    plan.update(fields)
    payload["plan"] = plan
    row.payload = payload
    session.commit()


@celery_app.task(bind=True, name="generate_scenario_plan")
def generate_scenario_plan(self, scenario_row_id: str, locks: list[str] | None = None) -> dict:
    """Draw the scenario's plan: streets/blocks/open space/building masses as
    real zones, geometry-mode metrics superseding the parameter estimates.

    locks=["streets"] keeps the existing street zones of this scenario and
    regenerates everything else around them.
    """
    from datetime import datetime, timezone as tz

    from geoalchemy2.shape import from_shape
    from shapely.geometry import Polygon as ShapelyPolygon
    from shapely.ops import unary_union

    from app.models.models import SiteZone, UrbanDnaScenario
    from app.services.city_connector import get_connector_for_site
    from app.services.urban_dna.builder import _fetch_with_cache

    locks = locks or []
    session = _get_sync_session()
    row = None
    try:
        row = session.query(UrbanDnaScenario).filter_by(id=uuid.UUID(scenario_row_id)).first()
        if row is None or row.snapshot is None or not row.payload:
            return {"status": "failed", "error": "scenario/payload not found"}
        snapshot = row.snapshot

        zone = session.query(SiteZone).filter_by(id=snapshot.zone_id).first()
        if zone is None:
            _set_plan_state(session, row, status="failed", error="boundary zone not found")
            return {"status": "failed"}
        site_shape = to_shape(zone.geometry)
        site_polygon = site_shape if isinstance(site_shape, ShapelyPolygon) else site_shape.convex_hull

        _set_plan_state(session, row, status="drawing", locks=locks)

        # Raw features for entry points + district ceilings (cache-backed, fast).
        connector = get_connector_for_site(site_polygon)
        cache = PostgresDatasetCache(session)

        async def _features():
            roads_spec = next(
                (s for s in connector.datasets.values()
                 if s.geometry_type == "line" and "road" in s.id),
                None,
            )
            district_spec = next(
                (s for s in connector.datasets.values() if s.id.endswith("land_use_districts")),
                None,
            )
            roads, districts = [], []
            if roads_spec is not None:
                fetched, _ = await _fetch_with_cache(connector, roads_spec, site_polygon, cache)
                roads = fetched.features if fetched.ok else []
            if district_spec is not None:
                fetched, _ = await _fetch_with_cache(connector, district_spec, site_polygon, cache)
                districts = fetched.features if fetched.ok else []
            return roads, districts

        road_features, district_features = asyncio.run(_features())

        # Existing plan zones for this scenario on this project.
        existing = [
            z for z in session.query(SiteZone).filter_by(project_id=snapshot.project_id).all()
            if (z.properties or {}).get("_plan_scenario") == row.scenario_id
        ]
        locked_street_area = None
        if "streets" in locks:
            street_polys = [
                to_shape(z.geometry) for z in existing
                if (z.properties or {}).get("_plan_role") == "street"
            ]
            if street_polys:
                locked_street_area = unary_union(street_polys)

        # --- generate → evaluate → refine loop (max 3 iterations) -----------------
        from app.services.plan_geometry.refinement import run_refinement_loop

        result, metrics_report, iterations = run_refinement_loop(
            site_polygon_wgs84=site_polygon,
            scenario_id=row.scenario_id,
            scenario_label=row.label,
            parameters=row.payload.get("plan_parameters") or {},
            dna=snapshot.dna or {},
            road_features=road_features,
            district_features=district_features,
            locked_street_area_wgs84=locked_street_area,
            locks=locks,
        )

        # Replace previous plan zones (keep locked streets).
        for old in existing:
            role = (old.properties or {}).get("_plan_role")
            if "streets" in locks and role == "street":
                continue
            session.delete(old)
        session.flush()

        inserted = 0
        for zone_dict in result.zones:
            if "streets" in locks and zone_dict["properties"].get("_plan_role") == "street":
                continue  # locked network kept as-is
            ring = zone_dict["coordinates"]
            if len(ring) < 3:
                continue
            session.add(SiteZone(
                id=uuid.uuid4(),
                project_id=snapshot.project_id,
                name=zone_dict["name"],
                zone_type=zone_dict["zone_type"],
                geometry=from_shape(ShapelyPolygon(ring), srid=4326),
                color=zone_dict["color"],
                properties=zone_dict["properties"],
                sort_order=zone_dict.get("sort_order", 500),
            ))
            inserted += 1

        payload = dict(row.payload or {})
        payload["metrics"] = metrics_report.model_dump(mode="json")
        payload["plan"] = {
            "status": "complete",
            "generated_at": datetime.now(tz.utc).isoformat(),
            "locks": locks,
            "zone_count": inserted,
            "block_count": result.block_count,
            "parcel_count": result.parcel_count,
            "building_count": result.building_count,
            "intersection_density_per_km2": round(result.intersection_density_per_km2, 1),
            "rules": result.rules,
            "geometry_inputs": {k: round(v, 1) for k, v in result.geometry_inputs.items()},
            "notes": result.notes,
            "iterations": iterations,
            "final_score": iterations[-1]["overall_score"] if iterations else None,
        }
        row.payload = payload
        session.commit()
        logger.info(
            "Plan drawn for %s: %d zones, %d blocks, %d parcels",
            row.scenario_id, inserted, result.block_count, result.parcel_count,
        )
        return {"status": "complete", "zones": inserted}

    except SoftTimeLimitExceeded:
        logger.warning("Plan generation %s hit the soft time limit", scenario_row_id)
        try:
            session.rollback()
            if row is not None:
                _set_plan_state(session, row, status="failed", error="plan generation exceeded the worker time budget")
        except Exception:  # noqa: BLE001
            logger.exception("Failed to mark plan %s after soft time limit", scenario_row_id)
        return {"status": "failed"}

    except Exception as exc:  # noqa: BLE001
        # A failed DRAWING must not fail the scenario row — the analysis stays valid.
        logger.exception("Plan generation failed for %s", scenario_row_id)
        try:
            session.rollback()
            if row is not None:
                _set_plan_state(
                    session, row, status="failed",
                    error=f"plan generation failed ({type(exc).__name__}) — see worker logs",
                )
        except Exception:  # noqa: BLE001
            logger.exception("Failed to mark plan %s failed", scenario_row_id)
        return {"status": "failed", "error": type(exc).__name__}

    finally:
        session.close()
