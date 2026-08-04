"""DNA builder — degradation semantics, confidence math, caching, never-fail.

Uses a FakeCityConnector so no network or DB is touched. The critical
invariants: every section always exists, a failed dataset yields nulls +
warnings + missing_datasets (never an exception), proxy values cap at 0.3,
and cached fetches degrade confidence with age.
"""

from datetime import datetime, timedelta, timezone

import pytest
from shapely.geometry import Polygon

from app.services.city_connector.base import CityConnector, DatasetSpec
from app.services.urban_dna.builder import bbox_hash_for, build_dna
from app.services.urban_dna.schema import SECTION_NAMES

SITE = Polygon([(-114.075, 51.043), (-114.062, 51.043), (-114.062, 51.049), (-114.075, 51.049)])


def _spec(connector_cls, dataset_id, dna_fields, transform, **overrides):
    defaults = dict(
        id=dataset_id,
        name=dataset_id,
        priority=1,
        geometry_type="point",
        refresh_days=7,
        source_url="",
        api_endpoint="x",
        adapter="socrata",
        adapter_params={"geo_field": "point"},
        dna_fields=dna_fields,
        transform=transform,
    )
    defaults.update(overrides)
    return connector_cls.register(DatasetSpec(**defaults))


def _make_connector(adapters_map):
    class FakeConnector(CityConnector):
        city_id = "faketown"
        display_name = "Faketown"

        def _adapters(self):
            return adapters_map

    return FakeConnector


async def _ok_adapter(spec, boundary):
    return [{"geometry": None, "properties": {}}], "ok", []


async def _partial_adapter(spec, boundary):
    return (
        [{"geometry": None, "properties": {}}],
        "partial",
        [
            {
                "code": "DATASET_TRUNCATED",
                "severity": "warning",
                "message": "truncated",
                "source_phase": "city_connector",
            }
        ],
    )


async def _failing_adapter(spec, boundary):
    raise RuntimeError("service down")


@pytest.mark.anyio
async def test_all_sections_exist_and_failure_degrades_gracefully():
    FakeConnector = _make_connector({"socrata": _ok_adapter, "broken": _failing_adapter})

    _spec(
        FakeConnector,
        "faketown.good",
        ("land_use.dominant_district",),
        lambda f, s: ({"land_use.dominant_district": "R-CG"}, []),
    )
    _spec(
        FakeConnector,
        "faketown.broken",
        ("mobility.transit_stops_400m",),
        lambda f, s: ({"mobility.transit_stops_400m": 3}, []),
        adapter="broken",
        priority=2,
    )

    dna = await build_dna(
        site_polygon=SITE,
        connector=FakeConnector(),
        project_id="p1",
        zone_id="z1",
    )

    for name in SECTION_NAMES:
        assert dna.section(name) is not None

    assert dna.land_use.fields["dominant_district"].value == "R-CG"
    assert dna.land_use.fields["dominant_district"].confidence == 1.0
    assert dna.land_use.meta.confidence == 1.0

    broken = dna.mobility.fields["transit_stops_400m"]
    assert broken.value is None
    assert broken.confidence == 0.0
    assert dna.mobility.meta.confidence == 0.0
    assert "faketown.broken" in dna.missing_datasets
    assert "faketown.broken" in dna.mobility.meta.missing_datasets
    assert any(w.code == "DATASET_ERROR" for w in dna.mobility.meta.warnings)

    # overall = mean of sections that have registered datasets, market excluded as stub
    assert 0.0 < dna.overall_confidence < 1.0


@pytest.mark.anyio
async def test_partial_status_caps_confidence_at_degraded():
    FakeConnector = _make_connector({"socrata": _partial_adapter})
    _spec(FakeConnector, "faketown.partial", ("site.parcel_count",), lambda f, s: ({"site.parcel_count": 12}, []))

    dna = await build_dna(site_polygon=SITE, connector=FakeConnector(), project_id="p", zone_id="z")
    field = dna.site.fields["parcel_count"]
    assert field.value == 12
    assert field.confidence == 0.6
    assert any(w.code == "DATASET_TRUNCATED" for w in dna.site.meta.warnings)


@pytest.mark.anyio
async def test_proxy_values_are_capped():
    FakeConnector = _make_connector({"socrata": _ok_adapter})
    _spec(
        FakeConnector,
        "faketown.transit",
        ("mobility.nearest_transit",),
        lambda f, s: (
            {
                "mobility.nearest_transit": {
                    "stop_name": "3 ST SW",
                    "distance_m": 120.0,
                    "network_estimate_m": 162.0,
                    "method": "euclidean_estimate",
                }
            },
            [],
        ),
    )

    dna = await build_dna(site_polygon=SITE, connector=FakeConnector(), project_id="p", zone_id="z")
    field = dna.mobility.fields["nearest_transit"]
    assert field.confidence == 0.3
    assert any("estimated" in n for n in field.notes)


class _FakeCacheHit:
    def __init__(self, age_days: float, ttl_days: float = 7.0):
        now = datetime.now(timezone.utc)
        self.features = [{"geometry": None, "properties": {"cached": True}}]
        self.fetched_at = now - timedelta(days=age_days)
        self.expires_at = self.fetched_at + timedelta(days=ttl_days)
        self.source_status = "ok"


class _FakeCache:
    def __init__(self, hit):
        self.hit = hit
        self.set_calls = []

    async def get(self, spec, bbox_hash):
        return self.hit

    async def set(self, spec, bbox_hash, result):
        self.set_calls.append((spec.id, bbox_hash, len(result.features)))


@pytest.mark.anyio
async def test_aging_cache_hit_degrades_confidence_and_skips_fetch():
    async def _never_called(spec, boundary):
        raise AssertionError("network adapter must not run on a cache hit")

    FakeConnector = _make_connector({"socrata": _never_called})
    _spec(FakeConnector, "faketown.cached", ("site.parcel_count",), lambda f, s: ({"site.parcel_count": len(f)}, []))

    cache = _FakeCache(_FakeCacheHit(age_days=5, ttl_days=7))  # >50% of TTL elapsed
    dna = await build_dna(
        site_polygon=SITE,
        connector=FakeConnector(),
        project_id="p",
        zone_id="z",
        cache=cache,
    )
    field = dna.site.fields["parcel_count"]
    assert field.value == 1  # transform re-ran over the cached features
    assert field.confidence == 0.8
    assert any("cache" in n for n in field.notes)
    assert cache.set_calls == []  # hit -> no write


@pytest.mark.anyio
async def test_fresh_fetch_writes_cache():
    FakeConnector = _make_connector({"socrata": _ok_adapter})
    spec = _spec(FakeConnector, "faketown.fresh", ("site.parcel_count",), lambda f, s: ({"site.parcel_count": 1}, []))

    cache = _FakeCache(hit=None)
    dna = await build_dna(
        site_polygon=SITE,
        connector=FakeConnector(),
        project_id="p",
        zone_id="z",
        cache=cache,
    )
    assert dna.site.fields["parcel_count"].confidence == 1.0
    assert len(cache.set_calls) == 1
    assert cache.set_calls[0][0] == "faketown.fresh"
    assert cache.set_calls[0][1] == bbox_hash_for(spec, SITE)


def test_bbox_hash_varies_by_version_and_envelope():
    FakeConnector = _make_connector({})
    spec_v1 = _spec(FakeConnector, "faketown.v", ("site.parcel_count",), lambda f, s: ({}, []))
    other_site = Polygon([(-114.2, 51.1), (-114.19, 51.1), (-114.19, 51.11), (-114.2, 51.11)])
    assert bbox_hash_for(spec_v1, SITE) != bbox_hash_for(spec_v1, other_site)


@pytest.mark.anyio
async def test_soft_time_limit_propagates_through_build_dna():
    """The builder's gather(return_exceptions=True) must re-raise the soft limit
    so the Celery task handler can mark the snapshot partial/failed."""
    from celery.exceptions import SoftTimeLimitExceeded

    async def _limited_adapter(spec, boundary):
        raise SoftTimeLimitExceeded()

    FakeConnector = _make_connector({"socrata": _limited_adapter})
    _spec(FakeConnector, "faketown.limited", ("site.parcel_count",), lambda f, s: ({}, []))

    with pytest.raises(SoftTimeLimitExceeded):
        await build_dna(site_polygon=SITE, connector=FakeConnector(), project_id="p", zone_id="z")


@pytest.mark.anyio
async def test_stale_regime_dataset_warns_and_degrades():
    from datetime import date

    FakeConnector = _make_connector({"socrata": _ok_adapter})
    _spec(
        FakeConnector,
        "faketown.stale",
        ("land_use.dominant_district",),
        lambda f, s: ({"land_use.dominant_district": "R-C1"}, []),
        valid_until=date(2020, 1, 1),
        dataset_version="v1-pre-repeal",
    )

    dna = await build_dna(site_polygon=SITE, connector=FakeConnector(), project_id="p", zone_id="z")
    assert any(w.code == "POLICY_REGIME_CHANGE" for w in dna.land_use.meta.warnings)
    assert dna.land_use.fields["dominant_district"].confidence == 0.6
