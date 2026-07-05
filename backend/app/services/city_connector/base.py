"""City Connector core contracts.

A CityConnector owns the datasets registered for one city and knows how to
fetch each of them for a site boundary. Everything downstream (Spatial
Intelligence, Urban DNA, Planning Agents) is city-blind: it sees only
DatasetSpec metadata, normalized GeoJSON features, and fetch results with
explicit status — never raw Socrata/OSM/ArcGIS payloads.

Hard requirement enforced here: a dataset fetch NEVER raises out of
``CityConnector.fetch_dataset``. Failures become ``DatasetFetchResult`` with
``status`` in {"timeout", "error"} plus a warning note, so DNA assembly always
continues.
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any, ClassVar, Literal

from shapely.geometry import Polygon

logger = logging.getLogger(__name__)

FetchStatus = Literal["ok", "partial", "timeout", "error", "not_registered"]

# GeoJSON-shaped feature dict: {"geometry": {...}, "properties": {...}}
Feature = dict[str, Any]

# transform(features, site_polygon_wgs84) -> (facts keyed by DNA field path, warnings)
TransformFn = Callable[[list[Feature], Polygon], tuple[dict[str, Any], list[dict[str, Any]]]]


def note(code: str, message: str, severity: str = "warning", source_phase: str = "city_connector") -> dict[str, Any]:
    """Build a ValidationNote-shaped dict (typed model lives in urban_dna.schema)."""
    return {"code": code, "severity": severity, "message": message, "source_phase": source_phase}


@dataclass(frozen=True)
class DatasetSpec:
    """Self-describing dataset registration. Adding a dataset = one literal + one transform fn."""

    id: str                             # "calgary.land_use_districts"
    name: str
    priority: int                       # fetch/importance order within the city
    geometry_type: Literal["polygon", "line", "point", "table", "document"]
    refresh_days: int                   # -> cache TTL
    source_url: str                     # human-facing docs page
    api_endpoint: str                   # adapter-specific resource locator (Socrata 4x4 id, etc.)
    adapter: Literal["socrata", "osm"]  # more adapters (arcgis, gtfs) land in later milestones
    dna_fields: tuple[str, ...]         # dotted DNA paths this dataset produces, e.g. "land_use.districts"
    transform: TransformFn              # normalize raw features into DNA facts
    adapter_params: dict[str, Any] = field(default_factory=dict)  # e.g. {"geo_field": "multipolygon"}
    field_map: dict[str, str] = field(default_factory=dict)       # source property -> canonical name
    buffer_m: float = 50.0              # fetch envelope around the site boundary
    cache_policy: Literal["bbox_ttl", "none"] = "bbox_ttl"
    dataset_version: str = "v1"         # bump on regime change (part of the cache key)
    valid_until: date | None = None     # temporal trap guard: stale regime -> warning + degraded confidence
    timeout_s: float = 25.0
    confidence_weight: float = 1.0      # weight in section confidence math


@dataclass
class DatasetFetchResult:
    dataset_id: str
    status: FetchStatus
    features: list[Feature] = field(default_factory=list)
    facts: dict[str, Any] = field(default_factory=dict)          # DNA-field-path -> value (post transform)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    from_cache: bool = False
    fetched_at: str = ""
    elapsed_s: float = 0.0

    @property
    def ok(self) -> bool:
        return self.status in ("ok", "partial")


# Adapter signature: fetch(spec, boundary_wgs84) -> (features, status, warnings)
AdapterFn = Callable[[DatasetSpec, Polygon], Awaitable[tuple[list[Feature], FetchStatus, list[dict[str, Any]]]]]


class CityConnector:
    """Base connector. Subclass per city; register DatasetSpecs declaratively."""

    city_id: ClassVar[str] = "unknown"
    display_name: ClassVar[str] = "Unknown"

    # Per-subclass registry — __init_subclass__ prevents the shared-mutable-class-attribute bug.
    _dataset_registry: ClassVar[dict[str, DatasetSpec]]

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        cls._dataset_registry = {}

    @classmethod
    def register(cls, spec: DatasetSpec) -> DatasetSpec:
        if spec.id in cls._dataset_registry:
            raise ValueError(f"Dataset {spec.id!r} already registered on {cls.__name__}")
        cls._dataset_registry[spec.id] = spec
        return spec

    @property
    def datasets(self) -> dict[str, DatasetSpec]:
        return dict(self._dataset_registry)

    def capabilities(self) -> set[str]:
        """Union of DNA field paths this city can produce. Derived, never declared twice."""
        return {f for spec in self._dataset_registry.values() for f in spec.dna_fields}

    def _adapters(self) -> dict[str, AdapterFn]:
        # Imported lazily to keep base import-light and avoid cycles.
        from app.services.city_connector.adapters import osm, socrata

        return {"socrata": socrata.fetch, "osm": osm.fetch}

    async def fetch_dataset(self, dataset_id: str, boundary_wgs84: Polygon) -> DatasetFetchResult:
        """Fetch + normalize one dataset. Never raises."""
        spec = self._dataset_registry.get(dataset_id)
        if spec is None:
            return DatasetFetchResult(
                dataset_id=dataset_id,
                status="not_registered",
                warnings=[note("DATASET_NOT_REGISTERED", f"{dataset_id} is not registered for {self.city_id}")],
            )

        started = time.monotonic()
        warnings: list[dict[str, Any]] = []
        try:
            adapter = self._adapters()[spec.adapter]
            async with asyncio.timeout(spec.timeout_s):
                features, status, fetch_warnings = await adapter(spec, boundary_wgs84)
            warnings.extend(fetch_warnings)
        except TimeoutError:
            logger.warning("Dataset %s timed out after %.0fs", dataset_id, spec.timeout_s)
            return DatasetFetchResult(
                dataset_id=dataset_id,
                status="timeout",
                warnings=[note("DATASET_TIMEOUT", f"{spec.name} did not respond within {spec.timeout_s:.0f}s")],
                elapsed_s=time.monotonic() - started,
            )
        except Exception as exc:  # noqa: BLE001 — structural never-fail guard
            logger.warning("Dataset %s fetch failed: %s", dataset_id, exc)
            return DatasetFetchResult(
                dataset_id=dataset_id,
                status="error",
                warnings=[note("DATASET_ERROR", f"{spec.name} fetch failed: {exc}")],
                elapsed_s=time.monotonic() - started,
            )

        result = DatasetFetchResult(
            dataset_id=dataset_id,
            status=status,
            features=features,
            warnings=warnings,
            fetched_at=datetime.now(timezone.utc).isoformat(),
            elapsed_s=time.monotonic() - started,
        )
        self._apply_transform(spec, boundary_wgs84, result)
        self._apply_temporal_guard(spec, result)
        return result

    def _apply_transform(self, spec: DatasetSpec, boundary_wgs84: Polygon, result: DatasetFetchResult) -> None:
        """Run the per-dataset normalize step. A transform bug degrades, never fails."""
        if not result.ok:
            return
        try:
            facts, transform_warnings = spec.transform(result.features, boundary_wgs84)
            unexpected = set(facts) - set(spec.dna_fields)
            if unexpected:
                logger.warning("Dataset %s transform produced undeclared fields: %s", spec.id, unexpected)
            result.facts = facts
            result.warnings.extend(transform_warnings)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Dataset %s transform failed: %s", spec.id, exc)
            result.status = "error"
            result.facts = {}
            result.warnings.append(note("DATASET_TRANSFORM_ERROR", f"{spec.name} normalization failed: {exc}"))

    @staticmethod
    def _apply_temporal_guard(spec: DatasetSpec, result: DatasetFetchResult) -> None:
        if spec.valid_until and date.today() >= spec.valid_until:
            result.warnings.append(
                note(
                    "POLICY_REGIME_CHANGE",
                    f"{spec.name} ({spec.dataset_version}) is past its validity date "
                    f"{spec.valid_until.isoformat()} — a newer regulatory regime may apply.",
                )
            )
