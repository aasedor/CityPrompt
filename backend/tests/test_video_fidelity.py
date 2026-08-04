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
