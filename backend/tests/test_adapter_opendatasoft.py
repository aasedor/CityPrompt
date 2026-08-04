"""Opendatasoft adapter tests — mocked HTTP, no network.

Covers the exports/geojson where-clause, client-side truncation semantics,
quota (429) handling, the Apikey header, and the batched attribute-enrichment
join (aggregations + sampled text fields + degrade-not-fail).
"""

from __future__ import annotations

from typing import Any, Callable

import httpx
import pytest
from shapely.geometry import Polygon

from app.core.config import get_settings
from app.services.city_connector.adapters import opendatasoft
from app.services.city_connector.base import DatasetSpec

SITE = Polygon(
    [
        (-123.1210, 49.2800),
        (-123.1195, 49.2800),
        (-123.1195, 49.2809),
        (-123.1210, 49.2809),
    ]
)


def _noop_transform(features, site):
    return {}, []


def _spec(**adapter_params_extra) -> DatasetSpec:
    return DatasetSpec(
        id="vancouver.test",
        name="Test Dataset",
        priority=1,
        geometry_type="polygon",
        refresh_days=7,
        source_url="",
        api_endpoint="test-dataset",
        adapter="opendatasoft",
        adapter_params={"domain": "opendata.vancouver.ca", "geo_field": "geom", **adapter_params_extra},
        dna_fields=("site.parcel_count",),
        transform=_noop_transform,
        buffer_m=50.0,
    )


class FakeResponse:
    def __init__(self, status_code: int = 200, payload: dict | None = None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self) -> dict:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            request = httpx.Request("GET", "https://test")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("error", request=request, response=response)


class FakeClient:
    """Records requests; routes them through a handler(url, params) callable."""

    instances: list["FakeClient"] = []

    handler: Callable[[str, dict], FakeResponse] = staticmethod(
        lambda url, params: FakeResponse(payload={"features": []})
    )

    def __init__(self, **kwargs: Any):
        self.init_kwargs = kwargs
        self.requests: list[tuple[str, dict]] = []
        FakeClient.instances.append(self)

    async def __aenter__(self) -> "FakeClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        return None

    async def get(self, url: str, params: dict | None = None) -> FakeResponse:
        params = params or {}
        self.requests.append((url, params))
        return FakeClient.handler(url, params)


@pytest.fixture(autouse=True)
def _fake_httpx(monkeypatch):
    FakeClient.instances = []
    FakeClient.handler = staticmethod(lambda url, params: FakeResponse(payload={"features": []}))
    monkeypatch.setattr(opendatasoft.httpx, "AsyncClient", FakeClient)
    monkeypatch.setattr(opendatasoft, "RETRY_AFTER_S", 0.0)  # no real sleeps in tests
    yield


def _feature(props: dict) -> dict:
    return {"geometry": {"type": "Point", "coordinates": [-123.12, 49.28]}, "properties": props}


@pytest.mark.anyio
async def test_exports_endpoint_and_where_clause():
    features, status, warnings = await opendatasoft.fetch(_spec(), SITE)
    assert status == "ok" and features == [] and warnings == []
    url, params = FakeClient.instances[0].requests[0]
    assert url.endswith("/api/explore/v2.1/catalog/datasets/test-dataset/exports/geojson")
    assert params["where"].startswith("intersects(geom, geom'POLYGON((")


@pytest.mark.anyio
async def test_truncation_yields_partial():
    many = [_feature({"i": i}) for i in range(opendatasoft.MAX_FEATURES + 5)]
    FakeClient.handler = staticmethod(lambda url, params: FakeResponse(payload={"features": many}))

    features, status, warnings = await opendatasoft.fetch(_spec(), SITE)
    assert len(features) == opendatasoft.MAX_FEATURES
    assert status == "partial"
    assert any(w["code"] == "DATASET_TRUNCATED" for w in warnings)


@pytest.mark.anyio
async def test_quota_429_retries_once_then_succeeds():
    calls = {"n": 0}

    def handler(url, params):
        calls["n"] += 1
        if calls["n"] == 1:
            return FakeResponse(status_code=429)
        return FakeResponse(payload={"features": [_feature({})]})

    FakeClient.handler = staticmethod(handler)
    features, status, _ = await opendatasoft.fetch(_spec(), SITE)
    assert status == "ok" and len(features) == 1 and calls["n"] == 2


@pytest.mark.anyio
async def test_persistent_429_becomes_rate_limited_error():
    FakeClient.handler = staticmethod(lambda url, params: FakeResponse(status_code=429))
    features, status, warnings = await opendatasoft.fetch(_spec(), SITE)
    assert status == "error" and features == []
    assert any(w["code"] == "RATE_LIMITED" for w in warnings)


@pytest.mark.anyio
async def test_apikey_header_present_only_when_configured(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "vancouver_ods_api_key", "test-key", raising=False)
    await opendatasoft.fetch(_spec(), SITE)
    assert FakeClient.instances[-1].init_kwargs["headers"] == {"Authorization": "Apikey test-key"}

    monkeypatch.setattr(settings, "vancouver_ods_api_key", "", raising=False)
    await opendatasoft.fetch(_spec(), SITE)
    assert FakeClient.instances[-1].init_kwargs["headers"] == {}


ENRICH = {
    "dataset": "property-tax-report",
    "local_key": "tax_coord",
    "remote_key": "land_coordinate",
    "prefix": "tax_",
    "latest_field": "report_year",
    "aggregations": "count(*) as folio_count, sum(current_land_value) as land_value_total",
    "sample_fields": ["year_built"],
    "batch_size": 2,
    "max_keys": 3,
}


def _enrich_handler(url, params):
    if url.endswith("/exports/geojson"):
        return FakeResponse(
            payload={
                "features": [
                    _feature({"tax_coord": "111"}),
                    _feature({"tax_coord": "222"}),
                    _feature({"tax_coord": "222"}),  # duplicate key must not duplicate queries
                ]
            }
        )
    # records endpoint
    if params.get("order_by") == "report_year desc":
        return FakeResponse(payload={"results": [{"report_year": "2026"}]})
    if params.get("group_by"):
        assert 'report_year = "2026"' in params["where"]
        return FakeResponse(
            payload={
                "results": [
                    {"land_coordinate": "111", "folio_count": 1, "land_value_total": 1_000_000},
                    {"land_coordinate": "222", "folio_count": 40, "land_value_total": 9_000_000},
                ]
            }
        )
    return FakeResponse(
        payload={
            "results": [
                {"land_coordinate": "111", "year_built": "1950"},
                {"land_coordinate": "222", "year_built": "1990"},
            ]
        }
    )


@pytest.mark.anyio
async def test_enrichment_merges_under_prefix():
    FakeClient.handler = staticmethod(_enrich_handler)
    features, status, warnings = await opendatasoft.fetch(_spec(enrich=ENRICH), SITE)
    assert status == "ok" and not warnings

    by_key = {f["properties"]["tax_coord"]: f["properties"] for f in features}
    assert by_key["111"]["tax_folio_count"] == 1
    assert by_key["111"]["tax_land_value_total"] == 1_000_000
    assert by_key["111"]["tax_year_built"] == "1950"
    assert by_key["222"]["tax_folio_count"] == 40


@pytest.mark.anyio
async def test_enrichment_key_cap_warns_join_truncated():
    def handler(url, params):
        if url.endswith("/exports/geojson"):
            return FakeResponse(
                payload={"features": [_feature({"tax_coord": str(i)}) for i in range(6)]}  # 6 keys > max_keys 3
            )
        return _enrich_handler(url, params)

    FakeClient.handler = staticmethod(handler)
    _, status, warnings = await opendatasoft.fetch(_spec(enrich=ENRICH), SITE)
    assert status == "ok"
    assert any(w["code"] == "JOIN_TRUNCATED" for w in warnings)


@pytest.mark.anyio
async def test_enrichment_failure_degrades_not_fails():
    def handler(url, params):
        if url.endswith("/exports/geojson"):
            return FakeResponse(payload={"features": [_feature({"tax_coord": "111"})]})
        return FakeResponse(status_code=500)

    FakeClient.handler = staticmethod(handler)
    features, status, warnings = await opendatasoft.fetch(_spec(enrich=ENRICH), SITE)
    assert status == "ok" and len(features) == 1  # geometry survives
    assert any(w["code"] == "JOIN_FAILED" for w in warnings)
    assert "tax_land_value_total" not in features[0]["properties"]
