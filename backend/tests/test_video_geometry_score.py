import numpy as np
import pytest

cv2 = pytest.importorskip("cv2")

from app.services.video_fidelity import (  # noqa: E402
    VideoFidelityReport,
    classify_geometry,
    score_frame_similarity,
    score_geometry_frame,
)

WIDTH, HEIGHT = 640, 360


def _depth_frame() -> np.ndarray:
    """Two buildings (bright, near) standing on a dark inverse-depth ground ramp."""
    ramp = np.linspace(40, 10, HEIGHT, dtype=np.float32)[:, None].repeat(WIDTH, axis=1)
    depth = ramp.astype(np.uint8)
    depth[90:260, 120:260] = 200
    depth[60:250, 380:520] = 170
    return depth


def _beauty_frame(shift: int = 0) -> np.ndarray:
    """The same scene with facade texture the depth track does not carry.

    `shift` moves only the first building, the way a model redraws one block
    while the rest of the frame stays put.
    """
    frame = np.full((HEIGHT, WIDTH, 3), 150, dtype=np.uint8)
    frame[260:, :] = (95, 110, 90)
    frame[90:260, 120 + shift:260 + shift] = (185, 180, 175)
    frame[60:250, 380:520] = (120, 110, 100)
    for row in range(105, 250, 30):  # window rows
        frame[row:row + 12, 130 + shift:250 + shift:24] = (60, 70, 90)
        frame[row:row + 12, 390:510:24] = (60, 70, 90)
    return frame


def _night(frame: np.ndarray) -> np.ndarray:
    night = frame.astype(np.float32) * 0.25
    night[:, :, 0] += 30  # blue tint (BGR)
    return np.clip(night, 0, 255).astype(np.uint8)


def test_identical_geometry_scores_high():
    assert score_geometry_frame(_depth_frame(), _beauty_frame(), _beauty_frame()) >= 95


def test_relit_output_keeps_geometry_while_appearance_similarity_drops():
    geometry = score_geometry_frame(_depth_frame(), _beauty_frame(), _night(_beauty_frame()))
    appearance = score_frame_similarity(_beauty_frame(), _night(_beauty_frame()))
    assert geometry >= 90
    assert appearance < 72


def test_moved_building_lowers_geometry_more_than_relighting():
    moved = score_geometry_frame(_depth_frame(), _beauty_frame(), _beauty_frame(shift=40))
    relit = score_geometry_frame(_depth_frame(), _beauty_frame(), _night(_beauty_frame()))
    assert moved < 80
    assert moved < relit - 15


def test_invented_structure_lowers_precision():
    invented = _beauty_frame()
    invented[40:300, 560:620] = (200, 200, 205)  # an extra tower the depth never had
    invented[50:290:20, 565:615] = (40, 40, 50)
    clean = score_geometry_frame(_depth_frame(), _beauty_frame(), _beauty_frame())
    with_tower = score_geometry_frame(_depth_frame(), _beauty_frame(), invented)
    assert with_tower < clean - 5


def test_geometry_bands():
    assert classify_geometry(80, 70) == "stable"
    assert classify_geometry(80, 40) == "review"
    assert classify_geometry(50, 35) == "review"
    assert classify_geometry(40, 30) == "drift"


def test_report_metadata_keeps_legacy_keys_and_adds_geometry():
    report = VideoFidelityReport(score=80.0, minimum_score=70.0, status="stable", samples=())
    assert set(report.metadata()) == {"fidelity_score", "fidelity_min_score", "fidelity_status", "fidelity_samples"}
    with_geometry = VideoFidelityReport(
        score=61.0,
        minimum_score=50.0,
        status="review",
        samples=(),
        geometry_score=91.0,
        geometry_min_score=88.0,
        geometry_status="stable",
        geometry_source="depth_video",
    )
    metadata = with_geometry.metadata()
    assert metadata["fidelity_status"] == "review"
    assert metadata["geometry_status"] == "stable"
    assert metadata["geometry_source"] == "depth_video"
    assert metadata["geometry_samples"] == []
