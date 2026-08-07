"""Tests for deterministic OpenCV building-reference fidelity gates."""
from __future__ import annotations

import numpy as np


def test_normalized_polygon_mask_rasterizes_the_audited_outline():
    from reference_fidelity import normalized_polygon_mask

    mask = normalized_polygon_mask((100, 80), [[0.1, 0.2], [0.9, 0.2], [0.9, 0.9], [0.1, 0.9]])
    assert mask.shape == (80, 100)
    assert mask[40, 50] == 255
    assert mask[2, 2] == 0


def test_compare_silhouettes_detects_a_stretched_box_and_roof_change():
    from reference_fidelity import compare_silhouettes

    reference = np.zeros((240, 320), dtype=np.uint8)
    render = np.zeros_like(reference)
    reference[80:220, 45:275] = 255
    for x in range(90, 231):
        roof_y = 80 - round((70 - abs(x - 160)) * 0.45)
        reference[roof_y:80, x] = 255
    render[70:220, 75:245] = 255

    identical = compare_silhouettes(reference, reference)
    changed = compare_silhouettes(reference, render)
    assert identical["silhouette_iou"] == 1.0
    assert identical["roofline_rmse"] == 0.0
    assert changed["silhouette_iou"] < 0.9
    assert changed["aspect_ratio_error"] > 0.1


def test_extract_render_silhouette_uses_neutral_background_and_central_component():
    from reference_fidelity import extract_render_silhouette

    image = np.full((180, 240, 3), (145, 155, 165), dtype=np.uint8)
    image[45:160, 45:200] = (85, 70, 62)
    image[20:36, 5:20] = (30, 40, 30)
    mask = extract_render_silhouette(image, [0.0, 0.0, 1.0, 0.95], 15.0)
    assert mask[100, 120] == 255
    assert mask[25, 10] == 0
