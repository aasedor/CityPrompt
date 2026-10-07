import asyncio
from unittest.mock import AsyncMock

import pytest
from shapely.geometry import box, mapping

from app.services import site_assessment as service

SITE = box(-114.12, 51.01, -114.119, 51.011)


def record(roll="1", value="100000", geometry=SITE, year="2026"):
    return {"roll_number": roll, "roll_year": year, "assessed_value": value,
            "multipolygon": mapping(geometry), "address": "Public test address", "property_type": "LI"}


def test_deduplicates_accounts_without_merging_distinct_accounts_on_same_land():
    result = service.summarize_assessments([record(), record(), record("2", "250000")], SITE)
    assert result["property_count"] == 2
    assert result["full_property_assessed_total"] == 350000
    assert result["area_weighted_estimate"] == 350000
    assert result["assessed_coverage_pct"] == 100
    assert result["complete"]


def test_partial_property_reports_full_value_and_separate_area_estimate():
    larger = box(-114.12, 51.01, -114.118, 51.011)
    result = service.summarize_assessments([record(geometry=larger)], SITE)
    assert result["full_property_assessed_total"] == 100000
    assert result["area_weighted_estimate"] == pytest.approx(50000, abs=2)
    assert result["records"][0]["overlap_pct"] == pytest.approx(50, abs=.01)
    assert result["partial_property_count"] == 1
    assert result["warnings"]


def test_total_uses_all_accounts_even_when_breakdown_is_bounded():
    result = service.summarize_assessments([record(str(i), "1000") for i in range(251)], SITE)
    assert result["property_count"] == 251
    assert result["full_property_assessed_total"] == 251000
    assert len(result["records"]) == 200
    assert result["details_omitted"] == 51


def test_missing_nonfinite_and_conflicting_values_are_visible_subtotals():
    result = service.summarize_assessments([
        record("1", "NaN"), record("2", "-1"), record("3", None),
        record("4", "1000"), record("4", "2000"), record("5", "0"), record("6", "500"),
    ], SITE)
    assert result["missing_value_count"] == 4
    assert result["full_property_assessed_total"] == 500
    assert not result["complete"]


def test_mixed_years_are_rejected_and_touching_land_is_excluded():
    with pytest.raises(service.AssessmentError, match="multiple assessment years"):
        service.summarize_assessments([record(), record("2", year="2025")], SITE)
    touching = box(-114.119, 51.01, -114.118, 51.011)
    assert service.summarize_assessments([record(geometry=touching)], SITE)["property_count"] == 0


def test_incomplete_identity_geometry_and_fetch_cap_are_disclosed():
    malformed = record("2"); malformed["multipolygon"] = None
    result = service.summarize_assessments([record(), record(""), malformed], SITE, truncated=True)
    assert not result["complete"]
    assert result["skipped_record_count"] == 2
    assert result["full_property_assessed_total"] == 100000


@pytest.mark.parametrize("site", [box(-123, 49, -122.9, 49.1), box(-114.3, 50.9, -114, 51.1)])
def test_unavailable_or_large_boundary_rejected(site):
    with pytest.raises(service.AssessmentError):
        service.validate_boundary(site)


@pytest.mark.asyncio
async def test_concurrent_classmates_share_lookup_and_cancellation_does_not_cancel_it(monkeypatch):
    service._cache.clear(); service._pending.clear()
    release = asyncio.Event()
    async def fetch(site):
        await release.wait()
        return {"full_property_assessed_total": 100000}
    fetch_mock = AsyncMock(side_effect=fetch)
    monkeypatch.setattr(service, "_fetch", fetch_mock)
    first = asyncio.create_task(service.get_site_assessment(SITE))
    second = asyncio.create_task(service.get_site_assessment(SITE))
    await asyncio.sleep(0); await asyncio.sleep(0)
    first.cancel()
    with pytest.raises(asyncio.CancelledError): await first
    release.set()
    assert (await second)["full_property_assessed_total"] == 100000
    assert await service.get_site_assessment(SITE) == await second
    fetch_mock.assert_awaited_once()
    service._cache.clear()
