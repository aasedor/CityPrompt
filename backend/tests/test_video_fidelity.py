import numpy as np
import pytest

cv2 = pytest.importorskip("cv2")

from app.services.video_fidelity import classify_fidelity, score_frame_similarity  # noqa: E402


def _architectural_frame() -> np.ndarray:
    frame = np.full((360, 640, 3), 225, dtype=np.uint8)
    cv2.rectangle(frame, (45, 55), (275, 320), (175, 155, 130), -1)
    cv2.rectangle(frame, (365, 55), (595, 320), (175, 155, 130), -1)
    for x_start in (70, 390):
        for row in range(3):
            for column in range(4):
                x = x_start + column * 48
                y = 90 + row * 60
                cv2.rectangle(frame, (x, y), (x + 24, y + 34), (45, 55, 65), -1)
    cv2.rectangle(frame, (280, 210), (360, 330), (80, 140, 75), -1)
    return frame


def test_identical_frame_scores_as_stable():
    frame = _architectural_frame()

    score = score_frame_similarity(frame, frame.copy())

    assert score >= 99
    assert classify_fidelity(score, score) == "stable"


def test_small_camera_translation_is_tolerated():
    reference = _architectural_frame()
    transform = np.float32([[1, 0, 8], [0, 1, -5]])
    translated = cv2.warpAffine(reference, transform, (640, 360), borderMode=cv2.BORDER_REFLECT)

    assert score_frame_similarity(reference, translated) >= 90


def test_changed_building_geometry_is_flagged_below_identical():
    reference = _architectural_frame()
    changed = reference.copy()
    cv2.rectangle(changed, (275, 45), (430, 330), (175, 155, 130), -1)
    cv2.rectangle(changed, (285, 90), (415, 270), (45, 55, 65), -1)

    changed_score = score_frame_similarity(reference, changed)

    assert changed_score < score_frame_similarity(reference, reference)
    assert classify_fidelity(48, 30) == "drift"


def test_review_band_requires_no_catastrophic_frame():
    assert classify_fidelity(60, 45) == "review"
    assert classify_fidelity(74, 50) == "review"


def test_geometry_only_scoring_rewards_a_materialized_render():
    """A successful photoreal finish keeps every edge and changes every surface.
    The default weighting reads that as drift; geometry-only scoring must not."""
    clay = np.full((180, 320, 3), 200, dtype=np.uint8)
    cv2.rectangle(clay, (90, 40), (230, 150), (150, 150, 150), -1)

    # Same silhouette, materialized: darker facade plus fine surface texture.
    materialized = clay.copy()
    cv2.rectangle(materialized, (90, 40), (230, 150), (70, 80, 95), -1)
    rng = np.random.default_rng(11)
    noise = rng.integers(-18, 18, size=(111, 141, 3), dtype=np.int16)
    patch = materialized[40:151, 90:231].astype(np.int16) + noise
    materialized[40:151, 90:231] = np.clip(patch, 0, 255).astype(np.uint8)

    default_score = score_frame_similarity(clay, materialized)
    geometry_score = score_frame_similarity(clay, materialized, geometry_only=True)

    assert geometry_score > default_score


def test_geometry_only_scoring_still_punishes_moved_geometry():
    reference = np.full((180, 320, 3), 200, dtype=np.uint8)
    cv2.rectangle(reference, (90, 40), (230, 150), (150, 150, 150), -1)

    # A second building appears and the first one is re-proportioned.
    drifted = np.full((180, 320, 3), 200, dtype=np.uint8)
    cv2.rectangle(drifted, (60, 20), (180, 160), (150, 150, 150), -1)
    cv2.rectangle(drifted, (240, 60), (300, 150), (150, 150, 150), -1)

    assert score_frame_similarity(reference, drifted, geometry_only=True) < 72
