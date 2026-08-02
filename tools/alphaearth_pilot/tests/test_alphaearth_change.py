from __future__ import annotations

import numpy as np

from tools.alphaearth_pilot.alphaearth_change import (
    Bounds,
    TileRecord,
    _overview_page_number,
    cosine_change,
    normalize_vectors,
    summarize_change,
)


def test_tile_path_converts_to_public_https_url() -> None:
    tile = TileRecord(
        path="gs://alphaearth_foundations/satellite_embedding/v1/annual/2025/11N/example.tiff",
        year=2025,
        crs="EPSG:32611",
        utm_zone="11N",
        wgs84_west=-115,
        wgs84_south=50,
        wgs84_east=-114,
        wgs84_north=52,
        utm_west=663840,
        utm_south=5652480,
        utm_east=745760,
        utm_north=5734400,
    )

    assert tile.https_url == (
        "https://storage.googleapis.com/alphaearth_foundations/"
        "satellite_embedding/v1/annual/2025/11N/example.tiff"
    )


def test_normalize_vectors_respects_valid_mask() -> None:
    data = np.array([[[3, 4]], [[4, 3]]], dtype=np.int8)
    valid = np.array([[True, False]])

    normalized = normalize_vectors(data, valid)

    np.testing.assert_allclose(normalized[0, 0], [0.6, 0.8])
    np.testing.assert_allclose(normalized[0, 1], [0.0, 0.0])


def test_cosine_change_is_zero_for_same_direction_and_one_for_orthogonal() -> None:
    first = np.array([[[10, 10]], [[0, 0]]], dtype=np.int8)
    second = np.array([[[20, 0]], [[0, 20]]], dtype=np.int8)
    valid = np.array([[True, True]])

    change, output_valid = cosine_change(first, second, valid, valid)

    np.testing.assert_allclose(change, [[0.0, 1.0]], atol=1e-6)
    np.testing.assert_array_equal(output_valid, valid)


def test_summarize_change_reports_threshold_share() -> None:
    change = np.array([[0.05, 0.15], [0.25, np.nan]], dtype=np.float32)
    mask = np.ones((2, 2), dtype=bool)

    summary = summarize_change(change, mask, threshold=0.15)

    assert summary["valid_pixel_count"] == 3
    assert summary["median_change"] == 0.15
    assert summary["changed_area_pct"] == 66.67


def test_bounds_validation_rejects_reversed_longitudes() -> None:
    try:
        Bounds(-114.0, 51.0, -115.0, 52.0).validate()
    except ValueError as exc:
        assert "longitude" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected invalid bounds to raise")


def test_bounded_reader_rejects_native_resolution() -> None:
    try:
        _overview_page_number(10)
    except ValueError as exc:
        assert "80 metres or coarser" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("Expected native resolution to require a production reader")
