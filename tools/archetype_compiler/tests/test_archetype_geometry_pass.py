"""Tests for the deterministic translator around learned geometry evidence."""
from __future__ import annotations

import numpy as np


def test_fit_affine_recovers_scale_and_offset_with_an_outlier():
    from archetype_geometry_pass import _fit_affine

    source = np.arange(100, dtype=np.float32).reshape(10, 10)
    target = source * 2.5 + 7.0
    target[0, 0] = 9000.0
    mask = np.ones_like(source, dtype=bool)
    scale, offset, aligned = _fit_affine(source, target, mask)

    assert np.isclose(scale, 2.5, atol=1e-4)
    assert np.isclose(offset, 7.0, atol=1e-4)
    assert np.isclose(aligned[5, 5], target[5, 5], atol=1e-4)


def test_roof_peaks_finds_separated_elevation_zones():
    from archetype_geometry_pass import _roof_peaks

    yy, xx = np.indices((120, 160), dtype=np.float32)
    depth = np.full((120, 160), 10.0, dtype=np.float32)
    depth -= 3.0 * np.exp(-((xx - 45) ** 2 + (yy - 50) ** 2) / 160.0)
    depth -= 2.0 * np.exp(-((xx - 115) ** 2 + (yy - 72) ** 2) / 220.0)
    mask = np.ones_like(depth, dtype=bool)

    peaks = _roof_peaks(depth, mask)

    assert len(peaks) == 2
    assert peaks[0]["relative_height"] > peaks[1]["relative_height"]
