"""Dataset Registry + City Connector guarantees.

Covers: per-city registry isolation, descriptor sanity (paths, buffers,
transforms), duplicate registration, city detection, and the never-fail
fetch guard around a raising adapter.
"""

import pytest
from shapely.geometry import Polygon

from app.services.city_connector import CITY_BOUNDS, detect_city, get_connector
from app.services.city_connector.base import CityConnector, DatasetSpec
from app.services.city_connector.cities.calgary import CalgaryConnector
from app.services.city_connector.cities.edmonton import EdmontonConnector
from app.services.city_connector.cities.osm_fallback import OSMFallbackConnector
from app.services.urban_dna.schema import SECTION_NAMES

DOWNTOWN_CALGARY = Polygon([
    (-114.075, 51.043), (-114.062, 51.043), (-114.062, 51.049), (-114.075, 51.049),
])


def _noop_transform(features, site):
    return {}, []


def test_registries_are_isolated_per_city():
    registries = {
        "calgary": set(CalgaryConnector().datasets),
        "edmonton": set(EdmontonConnector().datasets),
        "osm": set(OSMFallbackConnector().datasets),
    }
    for city, ids in registries.items():
        assert ids, f"{city} registered no datasets"
    cities = list(registries)
    for i, city_a in enumerate(cities):
        for city_b in cities[i + 1:]:
            shared = registries[city_a] & registries[city_b]
            assert not shared, f"per-subclass registries must not share entries: {shared}"


def test_calgary_registers_datasets_in_integration_order():
    specs = sorted(CalgaryConnector().datasets.values(), key=lambda s: s.priority)
    assert [s.id for s in specs] == [
        "calgary.land_use_districts",
        "calgary.parcels",
        "calgary.policy_plan_boundaries",
        "calgary.roads",
        "calgary.transit_stops",
        "calgary.bikeways",
        "calgary.pathways",
        "calgary.parks",
        "calgary.buildings_3d",
    ]


def test_edmonton_registers_datasets_in_integration_order():
    specs = sorted(EdmontonConnector().datasets.values(), key=lambda s: s.priority)
    assert [s.id for s in specs] == [
        "edmonton.zoning",
        "edmonton.parcels_info",
        "edmonton.neighbourhoods",
        "edmonton.roads",
        "edmonton.transit_stops",
        "edmonton.zoning_overlays",
        "edmonton.parks",
        "edmonton.trees",
        "edmonton.buildings",
    ]


@pytest.mark.parametrize("connector_cls", [CalgaryConnector, EdmontonConnector, OSMFallbackConnector])
def test_descriptor_sanity(connector_cls):
    for spec in connector_cls().datasets.values():
        assert spec.dna_fields, f"{spec.id} declares no DNA fields"
        for path in spec.dna_fields:
            section, _, field = path.partition(".")
            assert section in SECTION_NAMES, f"{spec.id}: unknown section in {path}"
            assert field, f"{spec.id}: field-less path {path}"
        assert callable(spec.transform)
        assert spec.timeout_s > 0
        assert spec.refresh_days > 0
        if spec.adapter == "socrata":
            assert spec.adapter_params.get("geo_field"), f"{spec.id}: socrata needs a verified geo_field"


def test_fetch_envelopes_cover_analysis_radii():
    specs = CalgaryConnector().datasets
    # 200m adjacency ring needs a >=200m fetch envelope; 800m walkshed needs >=800m.
    assert specs["calgary.land_use_districts"].buffer_m >= 200
    assert specs["calgary.roads"].buffer_m >= 200
    assert specs["calgary.transit_stops"].buffer_m >= 800

    edmonton = EdmontonConnector().datasets
    assert edmonton["edmonton.zoning"].buffer_m >= 200
    assert edmonton["edmonton.roads"].buffer_m >= 200
    assert edmonton["edmonton.transit_stops"].buffer_m >= 800
    assert edmonton["edmonton.parks"].buffer_m >= 800


def test_duplicate_registration_raises():
    class ScratchConnector(CityConnector):
        city_id = "scratch"

    spec = DatasetSpec(
        id="scratch.thing", name="Thing", priority=1, geometry_type="point",
        refresh_days=1, source_url="", api_endpoint="x", adapter="socrata",
        adapter_params={"geo_field": "point"}, dna_fields=("site.parcel_count",),
        transform=_noop_transform,
    )
    ScratchConnector.register(spec)
    with pytest.raises(ValueError):
        ScratchConnector.register(spec)


def test_detect_city_and_fallback():
    assert detect_city(-114.07, 51.045) == "calgary"
    assert detect_city(-73.57, 45.50) == "osm"  # Montreal -> generic fallback
    # Chestermere is INSIDE Calgary's coarse bbox — the committed boundary
    # polygon must reject it (two-tier detection), else its sites get a Calgary
    # connector whose datasets all come back empty.
    assert detect_city(-113.82, 51.04) == "osm"
    # Edmonton: downtown resolves, metro-adjacent suburbs inside the bbox do not.
    assert detect_city(-113.49, 53.54) == "edmonton"
    assert detect_city(-113.63, 53.63) == "osm"  # St. Albert
    assert detect_city(-113.28, 53.52) == "osm"  # Sherwood Park
    assert isinstance(get_connector("calgary"), CalgaryConnector)
    assert isinstance(get_connector("edmonton"), EdmontonConnector)
    assert isinstance(get_connector("not-a-city"), OSMFallbackConnector)
    for lon_min, lat_min, lon_max, lat_max in CITY_BOUNDS.values():
        assert lon_min < lon_max and lat_min < lat_max


def test_city_bounds_are_pairwise_disjoint():
    items = list(CITY_BOUNDS.items())
    for i, (city_a, a) in enumerate(items):
        for city_b, b in items[i + 1:]:
            overlaps = a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]
            assert not overlaps, f"{city_a} and {city_b} bboxes overlap — detection order-dependent"


@pytest.mark.anyio
async def test_unknown_dataset_returns_not_registered():
    result = await CalgaryConnector().fetch_dataset("calgary.nope", DOWNTOWN_CALGARY)
    assert result.status == "not_registered"
    assert not result.ok
    assert result.warnings


@pytest.mark.anyio
async def test_raising_adapter_never_escapes():
    class ExplodingConnector(CityConnector):
        city_id = "exploding"

        def _adapters(self):
            async def boom(spec, boundary):
                raise RuntimeError("adapter blew up")
            return {"socrata": boom}

    ExplodingConnector.register(DatasetSpec(
        id="exploding.data", name="Exploding", priority=1, geometry_type="point",
        refresh_days=1, source_url="", api_endpoint="x", adapter="socrata",
        adapter_params={"geo_field": "point"}, dna_fields=("site.parcel_count",),
        transform=_noop_transform,
    ))

    result = await ExplodingConnector().fetch_dataset("exploding.data", DOWNTOWN_CALGARY)
    assert result.status == "error"
    assert any(w["code"] == "DATASET_ERROR" for w in result.warnings)


def test_overpass_lock_survives_sequential_event_loops():
    """Regression (review finding): a module-level asyncio.Lock binds to the first
    loop it *waits* on; Celery runs a fresh loop per task in a warm worker child,
    so every build after the first would RuntimeError. The lock must be per-loop."""
    import asyncio

    from app.services.city_connector.adapters.osm import _get_overpass_lock

    async def contend():
        async def hold():
            async with _get_overpass_lock():
                await asyncio.sleep(0.01)
        await asyncio.gather(hold(), hold(), hold())  # forces the waiter path -> loop binding

    asyncio.run(contend())
    asyncio.run(contend())  # second fresh loop in the same process must NOT raise


@pytest.mark.anyio
async def test_soft_time_limit_propagates_through_fetch_guard():
    """Regression (review finding): SoftTimeLimitExceeded subclasses Exception; the
    never-fail guard must NOT swallow it or the task runs to SIGKILL and strands
    the snapshot in 'pending'."""
    from celery.exceptions import SoftTimeLimitExceeded

    class SoftLimitConnector(CityConnector):
        city_id = "softlimit"

        def _adapters(self):
            async def limited(spec, boundary):
                raise SoftTimeLimitExceeded()
            return {"socrata": limited}

    SoftLimitConnector.register(DatasetSpec(
        id="softlimit.data", name="SoftLimit", priority=1, geometry_type="point",
        refresh_days=1, source_url="", api_endpoint="x", adapter="socrata",
        adapter_params={"geo_field": "point"}, dna_fields=("site.parcel_count",),
        transform=_noop_transform,
    ))

    with pytest.raises(SoftTimeLimitExceeded):
        await SoftLimitConnector().fetch_dataset("softlimit.data", DOWNTOWN_CALGARY)


@pytest.mark.anyio
async def test_raising_transform_degrades_not_fails():
    class BadTransformConnector(CityConnector):
        city_id = "badtransform"

        def _adapters(self):
            async def ok(spec, boundary):
                return [{"geometry": None, "properties": {}}], "ok", []
            return {"socrata": ok}

    def bad_transform(features, site):
        raise KeyError("column renamed upstream")

    BadTransformConnector.register(DatasetSpec(
        id="badtransform.data", name="BadTransform", priority=1, geometry_type="point",
        refresh_days=1, source_url="", api_endpoint="x", adapter="socrata",
        adapter_params={"geo_field": "point"}, dna_fields=("site.parcel_count",),
        transform=bad_transform,
    ))

    result = await BadTransformConnector().fetch_dataset("badtransform.data", DOWNTOWN_CALGARY)
    assert result.status == "error"
    assert result.facts == {}
    assert any(w["code"] == "DATASET_TRANSFORM_ERROR" for w in result.warnings)
