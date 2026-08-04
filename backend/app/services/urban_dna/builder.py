"""Urban DNA builder — orchestrates connector fetches into a UrbanDNA document.

Never-fail contract, enforced structurally:
- every dataset fetch runs inside the connector's own guard (base.py) AND under
  ``asyncio.gather(..., return_exceptions=True)`` here;
- a failed/timed-out/absent dataset yields field-level nulls, a section warning,
  and an entry in ``missing_datasets`` — the build always completes;
- a city that never registered a dataset takes the *same* path as a Calgary
  timeout (capabilities-derived), which is what makes "zero agent changes for
  city #2" structural rather than aspirational.

The builder is DB-free. Caching is injected via the DatasetCacheProtocol so the
Celery task supplies a Postgres-backed cache while unit tests supply a fake.
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from datetime import datetime, timezone
from typing import Any, Protocol

from celery.exceptions import SoftTimeLimitExceeded
from shapely.geometry import Polygon, mapping

from app.services.city_connector.base import CityConnector, DatasetFetchResult, DatasetSpec
from app.services.spatial_engine import buffer_wgs84
from app.services.urban_dna.schema import (
    CONF_AGING_CACHE,
    CONF_DEGRADED,
    CONF_FRESH,
    CONF_MISSING,
    CONF_PROXY,
    SECTION_NAMES,
    DnaField,
    PlanningPhilosophy,
    UrbanDNA,
    ValidationNote,
    coerce_note,
)

logger = logging.getLogger(__name__)


class CachedFetch(Protocol):
    features: list[dict[str, Any]]
    fetched_at: datetime
    expires_at: datetime
    source_status: str


class DatasetCacheProtocol(Protocol):
    async def get(self, spec: DatasetSpec, bbox_hash: str) -> CachedFetch | None: ...

    async def set(self, spec: DatasetSpec, bbox_hash: str, result: DatasetFetchResult) -> None: ...


class PolicySynthesizer(Protocol):
    """Async policy phase: DNA-so-far -> (policy fields, warning dicts, confidence)."""

    async def __call__(self, dna: "UrbanDNA") -> tuple[dict[str, Any], list[dict[str, Any]], float]: ...


def bbox_hash_for(spec: DatasetSpec, site_polygon: Polygon) -> str:
    """Cache key: dataset id + version + rounded fetch-envelope GEOMETRY.

    Hashing only the bbox would false-hit for different-shaped sites sharing an
    envelope (the fetch itself filters by exact polygon WKT).
    """
    envelope = buffer_wgs84(site_polygon, spec.buffer_m)
    ring = ";".join(f"{x:.5f},{y:.5f}" for x, y in envelope.exterior.coords)
    raw = f"{spec.id}|{spec.dataset_version}|{ring}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _dataset_confidence(result: DatasetFetchResult, spec: DatasetSpec, cache_age_frac: float | None) -> float:
    if not result.ok:
        return CONF_MISSING
    if spec.valid_until is not None and any(w.get("code") == "POLICY_REGIME_CHANGE" for w in result.warnings):
        return CONF_DEGRADED
    if result.status == "partial":
        return CONF_DEGRADED
    if result.from_cache and cache_age_frac is not None and cache_age_frac > 0.5:
        return CONF_AGING_CACHE
    return CONF_FRESH


def _is_proxy_value(value: Any) -> bool:
    return isinstance(value, dict) and value.get("method") == "euclidean_estimate"


async def _fetch_with_cache(
    connector: CityConnector,
    spec: DatasetSpec,
    site_polygon: Polygon,
    cache: DatasetCacheProtocol | None,
) -> tuple[DatasetFetchResult, float | None]:
    """Returns (result, cache_age_fraction_of_ttl or None)."""
    bbox_hash = bbox_hash_for(spec, site_polygon)

    if cache is not None and spec.cache_policy == "bbox_ttl":
        try:
            cached = await cache.get(spec, bbox_hash)
        except SoftTimeLimitExceeded:
            raise
        except Exception as exc:  # noqa: BLE001 — cache trouble must not fail the build
            logger.warning("Dataset cache read failed for %s: %s", spec.id, exc)
            cached = None
        if cached is not None:
            now = datetime.now(timezone.utc)
            ttl = (cached.expires_at - cached.fetched_at).total_seconds() or 1.0
            age_frac = (now - cached.fetched_at).total_seconds() / ttl
            result = DatasetFetchResult(
                dataset_id=spec.id,
                status=cached.source_status if cached.source_status in ("ok", "partial") else "ok",
                features=list(cached.features),
                from_cache=True,
                fetched_at=cached.fetched_at.isoformat(),
            )
            # Re-run the transform on cached features so normalization fixes apply.
            connector._apply_transform(spec, site_polygon, result)
            connector._apply_temporal_guard(spec, result)
            return result, age_frac

    result = await connector.fetch_dataset(spec.id, site_polygon)

    if cache is not None and spec.cache_policy == "bbox_ttl" and result.ok:
        try:
            await cache.set(spec, bbox_hash, result)
        except SoftTimeLimitExceeded:
            raise
        except Exception as exc:  # noqa: BLE001
            logger.warning("Dataset cache write failed for %s: %s", spec.id, exc)

    return result, None


async def build_dna(
    *,
    site_polygon: Polygon,
    connector: CityConnector,
    project_id: str,
    zone_id: str,
    philosophy: PlanningPhilosophy | None = None,
    cache: DatasetCacheProtocol | None = None,
    policy_synthesizer: "PolicySynthesizer | None" = None,
    max_concurrency: int = 6,
) -> UrbanDNA:
    """Assemble the full UrbanDNA for a site boundary. Never raises for data reasons."""
    dna = UrbanDNA(
        city_id=connector.city_id,
        project_id=project_id,
        zone_id=zone_id,
        site_boundary=mapping(site_polygon),
        philosophy=philosophy,
    )

    specs = sorted(connector.datasets.values(), key=lambda s: s.priority)
    semaphore = asyncio.Semaphore(max_concurrency)

    async def guarded(spec: DatasetSpec) -> tuple[DatasetSpec, DatasetFetchResult, float | None]:
        async with semaphore:
            result, age_frac = await _fetch_with_cache(connector, spec, site_polygon, cache)
            return spec, result, age_frac

    outcomes = await asyncio.gather(*(guarded(spec) for spec in specs), return_exceptions=True)

    section_weights: dict[str, list[tuple[float, float]]] = {name: [] for name in SECTION_NAMES}

    for spec, outcome in zip(specs, outcomes):
        if isinstance(outcome, SoftTimeLimitExceeded):
            raise outcome  # the task-level handler must mark the snapshot partial/failed
        if isinstance(outcome, BaseException):
            # Belt-and-suspenders: fetch_dataset shouldn't raise, but nothing may escape.
            logger.error("Unexpected builder error for %s: %s", spec.id, outcome)
            result: DatasetFetchResult = DatasetFetchResult(
                dataset_id=spec.id,
                status="error",
                warnings=[
                    {
                        "code": "DATASET_ERROR",
                        "severity": "warning",
                        "message": f"{spec.name}: unexpected error during assembly: {outcome}",
                        "source_phase": "city_connector",
                    }
                ],
            )
            age_frac: float | None = None
        else:
            _, result, age_frac = outcome

        confidence = _dataset_confidence(result, spec, age_frac)
        _distribute(dna, spec, result, confidence, section_weights)

    # Policy phase (M2): runs AFTER dataset facts exist so retrieval can key off
    # district codes / plan names. Failure degrades the policy section only.
    if policy_synthesizer is not None:
        try:
            policy_fields, policy_warnings, policy_confidence = await policy_synthesizer(dna)
        except SoftTimeLimitExceeded:
            raise
        except Exception as exc:  # noqa: BLE001 — never-fail guard
            logger.warning("Policy synthesizer failed: %s", exc)
            policy_fields, policy_confidence = {}, 0.0
            policy_warnings = [
                {
                    "code": "POLICY_SYNTHESIS_UNAVAILABLE",
                    "severity": "warning",
                    "message": f"Policy intelligence unavailable: {exc}",
                    "source_phase": "policy_intelligence",
                }
            ]
        for field_name, value in policy_fields.items():
            dna.policy.fields[field_name] = DnaField(
                value=value,
                confidence=round(policy_confidence, 2),
                source_datasets=["policy_corpus"],
            )
        for raw in policy_warnings:
            dna.policy.meta.warnings.append(coerce_note(raw))
        section_weights["policy"].append((policy_confidence, 1.0))

    _finalize_confidence(dna, section_weights)
    return dna


def _distribute(
    dna: UrbanDNA,
    spec: DatasetSpec,
    result: DatasetFetchResult,
    confidence: float,
    section_weights: dict[str, list[tuple[float, float]]],
) -> None:
    """Place a dataset's facts (or their absence) into DNA sections."""
    touched_sections: set[str] = set()

    for path in spec.dna_fields:
        section_name, _, field_name = path.partition(".")
        if section_name not in SECTION_NAMES or not field_name:
            logger.warning("Dataset %s declares invalid DNA path %s", spec.id, path)
            continue
        section = dna.section(section_name)
        touched_sections.add(section_name)

        value = result.facts.get(path)
        field_conf = confidence if value is not None else CONF_MISSING
        notes: list[str] = []
        if _is_proxy_value(value):
            field_conf = min(field_conf, CONF_PROXY)
            notes.append("network distance estimated from straight line; real routing not yet available")
        if result.from_cache:
            notes.append(f"from cache ({result.fetched_at})")

        existing = section.fields.get(field_name)
        if existing is not None and existing.value is not None and value is None:
            continue  # never let a failed dataset blank a field another dataset filled
        section.fields[field_name] = DnaField(
            value=value,
            confidence=round(field_conf, 2),
            source_datasets=[spec.id],
            notes=notes,
        )

    if not result.ok:
        for section_name in touched_sections:
            meta = dna.section(section_name).meta
            if spec.id not in meta.missing_datasets:
                meta.missing_datasets.append(spec.id)
        if spec.id not in dna.missing_datasets:
            dna.missing_datasets.append(spec.id)

    # One home per note: the dataset's primary (alphabetically first) section,
    # falling back to the DNA-level list. Sorted for determinism.
    primary_section = sorted(touched_sections)[0] if touched_sections else None
    for raw in result.warnings:
        note = coerce_note(raw)
        if primary_section is not None:
            dna.section(primary_section).meta.warnings.append(note)
        else:
            dna.warnings.append(note)

    for section_name in touched_sections:
        section_weights[section_name].append((confidence, spec.confidence_weight))


def _finalize_confidence(dna: UrbanDNA, section_weights: dict[str, list[tuple[float, float]]]) -> None:
    """Overall = mean over ALL non-market sections, counting dataset-less sections as 0.

    Deliberate: a city with 5 of 18 datasets integrated must NOT read as 1.0
    "fully understood" — overall confidence should rise as datasets land.
    """
    section_scores: list[float] = []
    for name in SECTION_NAMES:
        contributions = section_weights[name]
        meta = dna.section(name).meta
        if not contributions:
            meta.confidence = 0.0
            if name != "market":  # market is an acknowledged stub, not a data gap
                meta.warnings.append(
                    ValidationNote(
                        code="SECTION_NO_DATASETS",
                        severity="info",
                        message=f"No datasets registered for the {name} section in this city.",
                        source_phase="city_connector",
                    )
                )
                section_scores.append(0.0)
            continue
        total_weight = sum(weight for _, weight in contributions)
        meta.confidence = (
            round(sum(conf * weight for conf, weight in contributions) / total_weight, 2) if total_weight else 0.0
        )
        if name != "market":
            section_scores.append(meta.confidence)

    dna.overall_confidence = round(sum(section_scores) / len(section_scores), 2) if section_scores else 0.0
