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
from app.services.plan_boundary_identity import (
    PLAN_BOUNDARY_FINGERPRINT_VERSION,
    PLAN_BOUNDARY_RESTORE_STATE_KEY,
    plan_boundary_fingerprint,
    stamp_plan_boundary_identity,
)
from app.services.urban_dna.builder import build_dna
from app.services.urban_dna.schema import DNA_SCHEMA_VERSION
from app.tasks.worker import celery_app
from app.services.residual_landscape import (
    lock_residual_landscape_project_sync,
    mark_community_3d_stale,
)


def _get_sync_session():
    # Lazy import: app.tasks.processing itself imports app.tasks.worker, which
    # imports this module — a top-level import here is a circular-import trap.
    from app.tasks.processing import _get_sync_session as factory

    return factory()


logger = logging.getLogger(__name__)


class LegoInventoryChangedDuringPlan(RuntimeError):
    """Raised when the executable project LEGO catalog changes mid-draw."""


def _load_project_lego_inventory(session, owner_id):
    """Load the project-scoped LEGO rows and rebuild their executable catalog.

    ``populate_existing`` is important here: a plan task can run long enough
    for another transaction to update a module already present in this
    session's identity map.  A plain repeat query would otherwise hand final
    preflight the stale ORM object even though PostgreSQL returned the row.
    """

    from sqlalchemy import or_

    from app.models.models import ModelLibraryEntry
    from app.services.master_planner import build_lego_planning_catalog

    entries = (
        session.query(ModelLibraryEntry)
        .filter(
            or_(
                ModelLibraryEntry.owner_id == owner_id,
                ModelLibraryEntry.is_public.is_(True),
            )
        )
        .order_by(ModelLibraryEntry.created_at.desc(), ModelLibraryEntry.id.desc())
        .execution_options(populate_existing=True)
        .all()
    )
    return entries, build_lego_planning_catalog(entries)


def _refresh_project_lego_inventory(
    session,
    owner_id,
    expected_fingerprint: str,
):
    """Requery immediately before binding and reject a moving catalog."""

    entries, catalog = _load_project_lego_inventory(session, owner_id)
    if catalog.fingerprint != expected_fingerprint:
        raise LegoInventoryChangedDuringPlan("The executable LEGO inventory changed while the AI plan was drawing.")
    return entries, catalog


def _delete_community_3d_buildings_for_replaced_zones(
    session,
    project_id: uuid.UUID,
    replaced_zone_ids: set[uuid.UUID],
) -> int:
    """Delete derived 3D buildings owned by plan zones being replaced.

    The explicit ``community3DRepresentation`` marker is the sole deletion
    authority.  This deliberately preserves every unmarked/user-created
    building, even when its name or LEGO recipe resembles generated content.
    """

    if not replaced_zone_ids:
        return 0

    from app.models.models import Building
    from app.services.community_3d_artifacts import community_3d_buildings_for_zones

    project_buildings = session.query(Building).filter(Building.project_id == project_id).all()
    derived_buildings = community_3d_buildings_for_zones(
        project_buildings,
        replaced_zone_ids,
    )
    for building in derived_buildings:
        session.delete(building)
    return len(derived_buildings)


def _backfill_locked_street_plan_centerline(zone) -> bool:
    """Add only a safely recoverable line and invalidate any compiled proof."""

    properties = dict(getattr(zone, "properties", None) or {})
    if properties.get("plan_centerline"):
        return False

    from app.services.plan_geometry.generator import (
        recover_street_plan_centerline_wgs84,
    )

    recovered_centerline = recover_street_plan_centerline_wgs84(to_shape(zone.geometry))
    if not recovered_centerline:
        return False

    properties["plan_centerline"] = recovered_centerline
    zone.properties = properties
    mark_community_3d_stale(
        zone,
        reason=(
            "Locked street centerline recovered during master-plan redraw; "
            "rebuild Community 3D before Direct rendering."
        ),
    )
    return True


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
            d
            for d in documents
            if (d.effective_date is None or d.effective_date <= now)
            and (d.repealed_date is None or d.repealed_date > now)
        ]

        warnings: list[dict] = []
        for document in effective:
            if document.repealed_date is not None and (document.repealed_date - now).days < 365:
                warnings.append(
                    {
                        "code": "POLICY_INSTRUMENT_SUNSETTING",
                        "severity": "warning",
                        "message": f"{document.title} is repealed effective "
                        f"{document.repealed_date.date().isoformat()} — cite with care.",
                        "source_phase": "policy_intelligence",
                    }
                )

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
                site_facts=site_facts,
                chunks=[],
                corpus_status="absent",
                documents_consulted=[],
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
                source_url=document.source_url,
            )
            for document in effective
            for chunk in document.chunks
        ]
        query_terms = build_query_terms(
            site_facts,
            topics=[
                "density",
                "height",
                "setback",
                "parking",
                "transit",
                "pedestrian",
                "cycling",
                "tree canopy",
                "flood",
                "housing",
                "affordable",
                "heritage",
                "climate",
                "complete streets",
                "emergency access",
            ],
        )
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
            snapshot_id,
            dna.city_id,
            dna.overall_confidence,
            len(dna.missing_datasets),
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
    from app.services.planning_agents.scenarios import BASELINE_SCENARIO_ID, resolve_scenario_preset
    from app.services.planning_agents.schemas import MergedParameter, ScenarioDefinition, ScenarioResult
    from app.services.urban_dna.schema import ValidationNote

    session = _get_sync_session()
    row = None
    try:
        row = session.query(UrbanDnaScenario).filter_by(id=uuid.UUID(scenario_row_id)).first()
        if row is None:
            return {"status": "failed", "error": "scenario row not found"}

        definition = resolve_scenario_preset(row.scenario_id)
        if definition is None and row.scenario_id.startswith("custom_"):
            # Custom scenario: the definition was expanded from the user's
            # brief at creation time and stored on the row.
            custom_def = (row.payload or {}).get("custom_definition")
            if isinstance(custom_def, dict):
                try:
                    definition = ScenarioDefinition(**custom_def)
                except Exception:  # noqa: BLE001 — fall through to the failure path
                    logger.exception("Invalid custom_definition on scenario %s", row.scenario_id)
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
                    warnings.append(
                        ValidationNote(
                            code="BASELINE_UNAVAILABLE",
                            severity="info",
                            message=f"{BASELINE_SCENARIO_ID} baseline not complete yet; diff shows all parameters.",
                            source_phase="coordinator",
                        )
                    )

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
                warnings.append(
                    ValidationNote(
                        code="METRICS_UNAVAILABLE",
                        severity="warning",
                        message=f"Derived statistics unavailable: {exc}",
                        source_phase="coordinator",
                    )
                )

            total_in = sum(u["input_tokens"] for u in usage_records)
            total_out = sum(u["output_tokens"] for u in usage_records)
            cost = sum(estimate_cost_usd(u["model"], u["input_tokens"], u["output_tokens"]) for u in usage_records)
            return ScenarioResult(
                scenario_id=definition.scenario_id,
                label=definition.label,
                philosophy=definition.philosophy,
                plan_parameters=plan_parameters,
                trade_offs=trade_offs,
                expert_summaries={s.agent_id: s.summary for s in expert_sets if not s.failed},
                explanation=explanation,
                usage={"input_tokens": total_in, "output_tokens": total_out, "estimated_cost_usd": round(cost, 3)},
                warnings=warnings,
                metrics=metrics_report.model_dump(mode="json") if metrics_report else None,
            )

        result = asyncio.run(_run())
        # Carry creation-time custom keys forward — a bare model_dump() would
        # erase custom_definition and the completed run could never redraw
        # (rule hints) or be re-run/prefilled (brief) again.
        payload = {
            key: value
            for key, value in (row.payload or {}).items()
            if key in ("custom_definition", "brief", "expansion")
        }
        payload.update(result.model_dump(mode="json"))
        row.payload = payload
        row.status = "complete"
        row.error = None
        session.commit()
        logger.info(
            "Scenario %s (%s) complete: %d parameters, %d trade-offs, ~$%.2f",
            row.scenario_id,
            scenario_row_id,
            len(result.plan_parameters),
            len(result.trade_offs),
            result.usage.get("estimated_cost_usd", 0.0),
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
    from app.services.residual_landscape import mark_residual_landscape_stale
    from app.services.city_connector import get_connector_for_site
    from app.services.urban_dna.builder import _fetch_with_cache
    from sqlalchemy.orm.attributes import flag_modified

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
        boundary_fingerprint = plan_boundary_fingerprint(site_polygon)
        snapshot_boundary_fingerprint = plan_boundary_fingerprint((snapshot.dna or {}).get("site_boundary"))
        if boundary_fingerprint is None or snapshot_boundary_fingerprint != boundary_fingerprint:
            _set_plan_state(
                session,
                row,
                status="failed",
                error="Site boundary does not match the scenario's Urban DNA snapshot.",
            )
            return {"status": "failed", "error": "boundary_identity_mismatch"}

        _set_plan_state(session, row, status="drawing", locks=locks)

        # Raw features for entry points + district ceilings (cache-backed, fast).
        connector = get_connector_for_site(site_polygon)
        cache = PostgresDatasetCache(session)

        async def _features():
            roads_spec = next(
                (s for s in connector.datasets.values() if s.geometry_type == "line" and "road" in s.id),
                None,
            )
            path_specs = [
                spec
                for spec in connector.datasets.values()
                if spec.geometry_type == "line" and any(term in spec.id for term in ("path", "bike", "trail"))
            ]
            district_spec = next(
                (s for s in connector.datasets.values() if s.id.endswith("land_use_districts")),
                None,
            )
            roads, paths, districts = [], [], []
            if roads_spec is not None:
                fetched, _ = await _fetch_with_cache(connector, roads_spec, site_polygon, cache)
                roads = fetched.features if fetched.ok else []
            for path_spec in path_specs:
                fetched, _ = await _fetch_with_cache(connector, path_spec, site_polygon, cache)
                if fetched.ok:
                    paths.extend(fetched.features)
            if not paths:
                # Some city connectors (notably Edmonton) provide authoritative
                # road centrelines but no pedestrian network. Fetch only the
                # immediate OSM foot/cycle context for plan anchoring, behind
                # the normal bbox/TTL cache, without slowing the Site DNA build.
                from app.services.city_connector.base import CityConnector, DatasetSpec

                class _PlannerPathConnector(CityConnector):
                    city_id = "planner_context"
                    display_name = "Planner OSM Path Context"

                def _no_facts(_features, _site):
                    return {}, []

                fallback_path_spec = DatasetSpec(
                    id="planner_context.osm_paths",
                    name="Immediate OSM Paths",
                    priority=1,
                    geometry_type="line",
                    refresh_days=30,
                    source_url="https://www.openstreetmap.org",
                    api_endpoint="overpass",
                    adapter="osm",
                    adapter_params={"category": "paths"},
                    dna_fields=("mobility.pathway_m_800m",),
                    transform=_no_facts,
                    buffer_m=80.0,
                    timeout_s=45.0,
                    confidence_weight=0.7,
                )
                _PlannerPathConnector.register(fallback_path_spec)
                fallback_connector = _PlannerPathConnector()
                fetched, _ = await _fetch_with_cache(
                    fallback_connector,
                    fallback_path_spec,
                    site_polygon,
                    cache,
                )
                if fetched.ok:
                    paths.extend(fetched.features)
            if district_spec is not None:
                fetched, _ = await _fetch_with_cache(connector, district_spec, site_polygon, cache)
                districts = fetched.features if fetched.ok else []
            return roads, paths, districts

        road_features, path_features, district_features = asyncio.run(_features())

        # Existing plan zones for this scenario (filtered in SQL — a big project
        # shouldn't page every zone's geometry through Python).
        existing = (
            session.query(SiteZone)
            .filter(
                SiteZone.project_id == snapshot.project_id,
                SiteZone.properties["_plan_scenario"].astext == row.scenario_id,
            )
            .all()
        )
        locked_street_area = None
        if "streets" in locks:
            street_polys = [
                to_shape(z.geometry) for z in existing if (z.properties or {}).get("_plan_role") == "street"
            ]
            if street_polys:
                locked_street_area = unary_union(street_polys)
            else:
                # Locking a network that doesn't exist would silently drop the
                # generated streets (the insert skips street zones under lock).
                locks = [lock for lock in locks if lock != "streets"]
                logger.info("Streets lock requested but no street zones exist — generating fresh network")

        # --- generate → evaluate → refine loop (max 3 iterations) -----------------
        from app.services.plan_geometry.refinement import run_refinement_loop

        # Custom scenarios carry deterministic geometry hints from the brief
        # ("a large park" must move the drawn plan; experts have no vocabulary
        # path for open_space_share). Clamped inside resolve_rules.
        rule_hints: dict[str, float] | None = None
        palette_hint: str | None = None
        plan_parameters = dict(row.payload.get("plan_parameters") or {})
        custom_def = (row.payload or {}).get("custom_definition")
        if isinstance(custom_def, dict):
            raw_hints = custom_def.get("rule_hints")
            if isinstance(raw_hints, dict):
                rule_hints = {
                    key: float(value)
                    for key, value in raw_hints.items()
                    if isinstance(value, (int, float)) and not isinstance(value, bool)
                } or None
            # The extracted philosophy primary selects the nearest preset
            # palette ("make it beautiful" draws beaux-arts fabric, not the
            # default midrise mix).
            philosophy = custom_def.get("philosophy")
            if isinstance(philosophy, dict) and isinstance(philosophy.get("primary"), str):
                palette_hint = philosophy["primary"]
            # Brief-extracted character, only when no expert emitted one.
            aesthetic_hint = (
                (row.payload or {}).get("expansion", {}).get("aesthetic_hint")
                if isinstance((row.payload or {}).get("expansion"), dict)
                else None
            )
            if aesthetic_hint and "buildings.development_aesthetic" not in plan_parameters:
                plan_parameters["buildings.development_aesthetic"] = {"value": str(aesthetic_hint)}

        # Runtime LEGO capability is the sole building vocabulary for AI plans.
        # Use the same ownership/public visibility contract and newest-first
        # ordering as the assembly API; render cards and old Meshy cache rows
        # are not evidence that a modular building can actually be assembled.
        lego_entries, lego_catalog = _load_project_lego_inventory(
            session,
            snapshot.project.owner_id,
        )
        if not lego_catalog.capabilities:
            message = (
                "No executable archetyped LEGO building families are installed. "
                "Import at least one complete podium/floor/roof family before drawing the AI plan."
            )
            _set_plan_state(session, row, status="failed", error=message)
            return {"status": "failed", "error": message}

        # LEGO metadata supplies the authoritative native footprint. The old
        # Meshy cache measurement path is intentionally excluded from AI plans.
        measured_model_dims = None

        # --- Master Planner: the design intelligence ahead of the engine ----------
        # One LLM composes the whole-plan spec (band characters WITH variety,
        # massing typologies, open-space program, landscape structure). The
        # validated spec is cached on the row: redraws are free, deterministic,
        # and the narrative stays presentable. Any failure falls back to a
        # deterministic palette built from the same executable LEGO catalog.
        from app.core.config import get_settings
        from app.services.master_planner import (
            MasterPlanSpec,
            compose_master_plan,
            diversity_plan_for_site,
            lego_fallback_spec,
            palette_from_spec,
            validate_spec,
        )
        from app.services import spatial_engine as se
        from app.services.plan_geometry.community_rules import (
            _DEFAULTS,
            _SCENARIO_DEFAULTS,
        )
        from app.services.planning_agents.scenarios import resolve_scenario_preset
        from app.services.planning_agents.schemas import ScenarioDefinition

        settings = get_settings()
        frame = se.SiteFrame.from_wgs84(site_polygon)
        block_m = _SCENARIO_DEFAULTS.get(row.scenario_id, _DEFAULTS)["block"]
        site_summary = {
            "area_m2": frame.area_m2,
            "est_blocks": max(1, round(frame.area_m2 / (block_m * block_m))),
        }
        diversity_policy = diversity_plan_for_site(site_summary)
        master_notes: list[dict] = []
        master_spec = None
        master_usage = None
        master_source = "runtime_lego_fallback"
        cached_master = row.payload.get("master_plan") or {}
        cached_spec = cached_master.get("spec")
        cached_fingerprint = cached_master.get("lego_catalog_fingerprint")
        cached_reusable = cached_master.get("cache_reusable") is True
        if isinstance(cached_spec, dict) and cached_fingerprint == lego_catalog.fingerprint and cached_reusable:
            try:
                parsed_spec = MasterPlanSpec(**cached_spec).model_copy(
                    update={"diversity": diversity_policy}
                )
                master_spec, repair_notes = validate_spec(
                    parsed_spec,
                    row.scenario_id,
                    palette_hint,
                    lego_catalog=lego_catalog,
                )
                master_notes.extend(repair_notes)
                master_source = "cached_runtime_lego"
            except Exception:  # noqa: BLE001 — stale spec schema: recompose below
                master_spec = None

        if isinstance(cached_spec, dict) and cached_fingerprint != lego_catalog.fingerprint:
            master_notes.append(
                {
                    "code": "MASTER_PLAN_LEGO_CATALOG_CHANGED",
                    "severity": "info",
                    "message": (
                        "The imported LEGO inventory changed; the cached plan palette "
                        "was recomposed against the current executable families."
                    ),
                    "source_phase": "master_planner",
                }
            )

        if master_spec is None and settings.master_planner_enabled and settings.anthropic_api_key:
            definition = resolve_scenario_preset(row.scenario_id)
            if definition is None and isinstance(custom_def, dict):
                try:
                    definition = ScenarioDefinition(**custom_def)
                except Exception:  # noqa: BLE001 — invalid custom def: preset palette path
                    definition = None
            if definition is not None and snapshot.dna:
                from app.core.usage_logger import log_api_usage_sync
                # compose_master_plan never raises, but the event-loop plumbing
                # around it can — and the draw must never depend on the LLM.
                try:
                    composed_spec, master_usage, composition_notes = asyncio.run(
                        compose_master_plan(
                            dna_json=snapshot.dna,
                            definition=definition,
                            site_summary=site_summary,
                            parameters=plan_parameters,
                            brief=(row.payload or {}).get("brief"),
                            api_key=settings.anthropic_api_key,
                            model=settings.urban_dna_agent_model,
                            palette_hint=palette_hint,
                            lego_catalog=lego_catalog,
                        )
                    )
                    master_notes.extend(composition_notes)
                    if composed_spec is not None:
                        master_spec = composed_spec
                        master_source = (
                            "ai_runtime_lego" if master_usage.get("status") == "success" else "runtime_lego_fallback"
                        )
                except SoftTimeLimitExceeded:
                    raise
                except Exception as exc:  # noqa: BLE001 — preset palette path
                    logger.warning("Master planner composition errored: %s", exc)
                    master_spec = None
                    master_notes.append(
                        {
                            "code": "MASTER_PLANNER_UNAVAILABLE",
                            "severity": "warning",
                            "message": f"Master Planner unavailable ({type(exc).__name__}) — "
                            "the current imported LEGO catalog drew this plan.",
                            "source_phase": "master_planner",
                        }
                    )
                if master_usage is not None:
                    try:
                        log_api_usage_sync(
                            provider="anthropic",
                            operation="planning_agent.master_planner",
                            input_tokens=master_usage["input_tokens"],
                            output_tokens=master_usage["output_tokens"],
                            status=master_usage["status"],
                            metadata={"scenario": row.scenario_id, "model": master_usage["model"]},
                        )
                    except SoftTimeLimitExceeded:
                        raise
                    except Exception as exc:  # noqa: BLE001
                        logger.warning("Failed to log master planner usage: %s", exc)
        if master_spec is None:
            master_spec = lego_fallback_spec(
                row.scenario_id,
                lego_catalog,
                palette_hint,
                site_summary=site_summary,
            )
            master_notes.append(
                {
                    "code": "MASTER_PLAN_RUNTIME_LEGO_FALLBACK",
                    "severity": "info",
                    "message": (
                        "The plan was deterministically composed from the current imported "
                        "archetyped LEGO catalog; no unsupported building was substituted."
                    ),
                    "source_phase": "master_planner",
                }
            )

        pending_master_plan = {
            "spec": master_spec.model_dump(mode="json"),
            "narrative": master_spec.design_narrative,
            "generated_at": datetime.now(tz.utc).isoformat(),
            "usage": master_usage,
            "source": master_source,
            "diversity_policy": master_spec.diversity.model_dump(mode="json"),
            "lego_catalog_fingerprint": lego_catalog.fingerprint,
            "lego_parent_count": len(lego_catalog.parent_ids),
        }

        palette_override = palette_from_spec(
            master_spec,
            row.scenario_id,
            palette_hint,
            lego_catalog=lego_catalog,
        )

        # The planner's urban grain becomes a rule hint (block spacing + the
        # hard edge cap that forces subdivision), so it sizes blocks to the
        # local context instead of the scenario default.
        if master_spec is not None and master_spec.block_target_m:
            rule_hints = dict(rule_hints or {})
            rule_hints["block_target_m"] = float(master_spec.block_target_m)
            rule_hints.setdefault("max_block_edge_m", round(float(master_spec.block_target_m) * 1.15, 1))

        result, metrics_report, iterations = run_refinement_loop(
            site_polygon_wgs84=site_polygon,
            scenario_id=row.scenario_id,
            scenario_label=row.label,
            parameters=plan_parameters,
            dna=snapshot.dna or {},
            road_features=road_features,
            path_features=path_features,
            district_features=district_features,
            locked_street_area_wgs84=locked_street_area,
            rule_hints=rule_hints,
            locks=locks,
            palette_hint=palette_hint,
            measured_model_dims=measured_model_dims,
            palette_override=palette_override,
        )

        # The catalog above is a planning snapshot, not a lock. Imports and
        # module configuration can change while Anthropic/refinement runs.
        # Requery now so persisted zones are never certified against assets
        # that no longer exist. A changed capability vocabulary requires a
        # clean redraw/recomposition rather than a mixed-catalog result.
        try:
            lego_entries, lego_catalog = _refresh_project_lego_inventory(
                session,
                snapshot.project.owner_id,
                lego_catalog.fingerprint,
            )
        except LegoInventoryChangedDuringPlan as exc:
            message = (
                f"{exc} Retry Generate Plan so the Master Planner can recompose "
                "against the current project-owner LEGO catalog."
            )
            if cached_reusable:
                failed_payload = dict(row.payload or {})
                failed_master = dict(failed_payload.get("master_plan") or {})
                failed_master["cache_reusable"] = False
                failed_payload["master_plan"] = failed_master
                row.payload = failed_payload
            _set_plan_state(session, row, status="failed", error=message)
            return {"status": "failed", "error": message}

        from app.services.master_planner.lego_geometry import (
            LegoGeometryCompatibilityError,
            bind_building_zones_to_lego,
        )

        try:
            result.zones, lego_binding = bind_building_zones_to_lego(
                result.zones,
                lego_entries,
                lego_catalog,
            )
        except LegoGeometryCompatibilityError as exc:
            message = f"AI plan could not be bound entirely to the imported LEGO catalog: {exc}"
            if cached_reusable:
                failed_payload = dict(row.payload or {})
                failed_master = dict(failed_payload.get("master_plan") or {})
                failed_master["cache_reusable"] = False
                failed_payload["master_plan"] = failed_master
                row.payload = failed_payload
            _set_plan_state(session, row, status="failed", error=message)
            return {"status": "failed", "error": message}
        if lego_binding.omitted_count:
            # Building zones and metric-space masses are emitted in the same
            # order by the geometry generator. Keep the persisted plan,
            # reported yield and evaluator trace consistent after bounded
            # clipped slivers are returned to residual landscaping.
            if (
                len(result.masses_m) != lego_binding.building_count
                or len(result.mass_floors) != lego_binding.building_count
            ):
                message = (
                    "AI plan LEGO binding could not reconcile building zones with "
                    "the geometry metric trace; the previous plan was preserved."
                )
                if cached_reusable:
                    failed_payload = dict(row.payload or {})
                    failed_master = dict(failed_payload.get("master_plan") or {})
                    failed_master["cache_reusable"] = False
                    failed_payload["master_plan"] = failed_master
                    row.payload = failed_payload
                _set_plan_state(session, row, status="failed", error=message)
                return {"status": "failed", "error": message}
            omitted_indices = set(lego_binding.omitted_building_indices)
            retained_masses = [mass for index, mass in enumerate(result.masses_m) if index not in omitted_indices]
            retained_floors = [
                floors for index, floors in enumerate(result.mass_floors) if index not in omitted_indices
            ]
            result.masses_m = retained_masses
            result.mass_floors = retained_floors
            result.building_count = lego_binding.retained_count
            result.geometry_inputs["building_footprint_m2"] = sum(float(mass.area) for mass in retained_masses)
            result.geometry_inputs["gfa_m2"] = sum(
                float(mass.area) * floors for mass, floors in zip(retained_masses, retained_floors)
            )

            from app.services.plan_geometry.plan_evaluator import evaluate_plan
            from app.services.plan_metrics import compute_metrics

            metrics_report = compute_metrics(
                scenario_id=row.scenario_id,
                dna=snapshot.dna or {},
                parameters=plan_parameters,
                geometry_inputs=result.geometry_inputs,
                effective_floors=float(result.rules.get("floors") or 0) or None,
            )
            units_metric = metrics_report.metrics.get("units")
            evaluation = evaluate_plan(
                result,
                plan_parameters,
                units_estimate=units_metric.value if units_metric else None,
            )
            if iterations:
                iterations[-1]["overall_score"] = evaluation.overall
                iterations[-1]["scores"] = {key: score.model_dump() for key, score in evaluation.scores.items()}
                iterations[-1]["building_count"] = result.building_count
                iterations[-1]["postprocess"] = {"omitted_incompatible_lego_footprints": (lego_binding.omitted_count)}
            result.notes.append(
                {
                    "code": "LEGO_INCOMPATIBLE_SLIVER_TO_LANDSCAPE",
                    "severity": "info",
                    "message": (
                        f"{lego_binding.omitted_count} of {lego_binding.building_count} "
                        "clipped building footprints could not accept any imported LEGO "
                        "family and were returned to the site-boundary residual landscape."
                    ),
                    "source_phase": "building_placement",
                }
            )
        if lego_binding.repaired_count:
            result.notes.append(
                {
                    "code": "LEGO_ACTUAL_FOOTPRINT_REBOUND",
                    "severity": "info",
                    "message": (
                        f"{lego_binding.repaired_count} of {lego_binding.building_count} "
                        "building footprints were rebound to a stylistically closest "
                        "LEGO family proven at their final parcel dimensions."
                    ),
                    "source_phase": "building_placement",
                }
            )
        # The planner's own notes (composition + repairs) lead the plan notes.
        result.notes[:0] = master_notes

        lock_residual_landscape_project_sync(session, snapshot.project_id)
        session.refresh(zone)
        if plan_boundary_fingerprint(to_shape(zone.geometry)) != boundary_fingerprint:
            raise RuntimeError("Site boundary changed while the master plan was drawing")
        if mark_residual_landscape_stale(
            zone,
            changed_zone_id=str(zone.id),
            reason="Master plan regenerated; rebuild Community 3D landscaping.",
        ):
            flag_modified(zone, "properties")

        # Replace previous plan zones (keep locked streets).  Remove only the
        # Community 3D Building artifacts explicitly owned by those zones
        # before their source rows disappear; otherwise the old models remain
        # visible as ghosts beside the regenerated plan.
        zones_to_replace = []
        for old in existing:
            role = (old.properties or {}).get("_plan_role")
            if "streets" in locks and role == "street":
                _backfill_locked_street_plan_centerline(old)
                old.properties = stamp_plan_boundary_identity(
                    old.properties,
                    fingerprint=boundary_fingerprint,
                    boundary_zone_id=zone.id,
                    snapshot_id=snapshot.id,
                )
                flag_modified(old, "properties")
                continue
            zones_to_replace.append(old)
        stale_buildings_removed = _delete_community_3d_buildings_for_replaced_zones(
            session,
            snapshot.project_id,
            {old.id for old in zones_to_replace},
        )
        for old in zones_to_replace:
            session.delete(old)
        session.flush()

        inserted = 0
        for zone_dict in result.zones:
            if "streets" in locks and zone_dict["properties"].get("_plan_role") == "street":
                continue  # locked network kept as-is
            ring = zone_dict["coordinates"]
            if len(ring) < 3:
                continue
            properties = stamp_plan_boundary_identity(
                zone_dict["properties"],
                fingerprint=boundary_fingerprint,
                boundary_zone_id=zone.id,
                snapshot_id=snapshot.id,
            )
            session.add(
                SiteZone(
                    id=uuid.uuid4(),
                    project_id=snapshot.project_id,
                    name=zone_dict["name"],
                    zone_type=zone_dict["zone_type"],
                    geometry=from_shape(ShapelyPolygon(ring), srid=4326),
                    color=zone_dict["color"],
                    properties=properties,
                    sort_order=zone_dict.get("sort_order", 500),
                )
            )
            inserted += 1

        payload = dict(row.payload or {})
        payload["master_plan"] = {
            **pending_master_plan,
            "validated_for_lego_geometry": True,
            # A deterministic fallback is safe to draw but should not turn a
            # transient Anthropic failure into a permanent no-retry cache.
            "cache_reusable": master_source != "runtime_lego_fallback",
        }
        payload["metrics"] = metrics_report.model_dump(mode="json")
        payload["plan"] = {
            "status": "complete",
            "generated_at": datetime.now(tz.utc).isoformat(),
            "boundary_identity": {
                "schema_version": PLAN_BOUNDARY_FINGERPRINT_VERSION,
                "fingerprint": boundary_fingerprint,
                "zone_id": str(zone.id),
                "snapshot_id": str(snapshot.id),
            },
            "locks": locks,
            "zone_count": inserted,
            "block_count": result.block_count,
            "parcel_count": result.parcel_count,
            "building_count": result.building_count,
            "stale_buildings_removed": stale_buildings_removed,
            "lego_binding": {
                "catalog_fingerprint": lego_catalog.fingerprint,
                "catalog_parent_count": len(lego_catalog.parent_ids),
                "building_count": lego_binding.building_count,
                "retained_count": lego_binding.retained_count,
                "unchanged_count": lego_binding.unchanged_count,
                "repaired_count": lego_binding.repaired_count,
                "omitted_count": lego_binding.omitted_count,
            },
            "intersection_density_per_km2": round(result.intersection_density_per_km2, 1),
            "rules": result.rules,
            "geometry_inputs": {k: round(v, 1) for k, v in result.geometry_inputs.items()},
            "notes": result.notes,
            "iterations": iterations,
            "final_score": iterations[-1]["overall_score"] if iterations else None,
        }
        row.payload = payload
        boundary_props = dict(zone.properties or {})
        if boundary_props.pop(PLAN_BOUNDARY_RESTORE_STATE_KEY, None) is not None:
            zone.properties = boundary_props
            flag_modified(zone, "properties")
        session.commit()
        logger.info(
            "Plan drawn for %s: %d zones, %d blocks, %d parcels",
            row.scenario_id,
            inserted,
            result.block_count,
            result.parcel_count,
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
                    session,
                    row,
                    status="failed",
                    error=f"plan generation failed ({type(exc).__name__}) — see worker logs",
                )
        except Exception:  # noqa: BLE001
            logger.exception("Failed to mark plan %s failed", scenario_row_id)
        return {"status": "failed", "error": type(exc).__name__}

    finally:
        session.close()
