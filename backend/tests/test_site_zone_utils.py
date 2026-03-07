"""Unit tests for site zone generation utility helpers."""

import uuid
from types import SimpleNamespace

from app.api.v1.site_zones import (
    _normalize_building_ids,
    _resolve_unit_count,
    _safe_int,
    _safe_optional_float,
    _safe_optional_int,
)


def test_safe_int_handles_blank_and_invalid_values() -> None:
    assert _safe_int("", 7) == 7
    assert _safe_int("12", 0) == 12
    assert _safe_int("12.9", 0) == 12
    assert _safe_int("abc", 5) == 5


def test_safe_optional_parsers_handle_invalid_values() -> None:
    assert _safe_optional_int("") is None
    assert _safe_optional_int("4") == 4
    assert _safe_optional_int("4.0") == 4
    assert _safe_optional_int("abc") is None

    assert _safe_optional_float("") is None
    assert _safe_optional_float("4.5") == 4.5
    assert _safe_optional_float("abc") is None


def test_normalize_building_ids_filters_invalid_entries() -> None:
    valid_1 = uuid.uuid4()
    valid_2 = uuid.uuid4()

    normalized = _normalize_building_ids([
        str(valid_1),
        valid_2,
        "not-a-uuid",
        None,
        "",
    ])

    assert normalized == [valid_1, valid_2]


def test_resolve_unit_count_is_robust_to_bad_property_values() -> None:
    residential_zone = SimpleNamespace(
        zone_type="residential",
        properties={"unit_count": "", "description_text": ""},
    )
    assert _resolve_unit_count(residential_zone) == 1

    parsed_zone = SimpleNamespace(
        zone_type="residential",
        properties={"unit_count": "abc", "description_text": "14 homes with front porches"},
    )
    assert _resolve_unit_count(parsed_zone) == 14

    development_zone = SimpleNamespace(
        zone_type="development_area",
        properties={"unit_count": "invalid", "description_text": ""},
    )
    assert _resolve_unit_count(development_zone) == 10
