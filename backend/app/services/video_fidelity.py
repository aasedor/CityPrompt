"""Geometry-fidelity scoring for generated architectural videos.

The score is deliberately reference based: completed video frames are compared
with City Prompt's deterministic preview video or route keyframes at matching
points in time. It is not an aesthetic score and it never calls an AI model.
"""

from __future__ import annotations

import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal, Sequence

import numpy as np

try:  # OpenCV is part of the deployed backend image but optional in light test installs.
    import cv2
except ModuleNotFoundError:  # pragma: no cover - exercised by deployment smoke checks.
    cv2 = None  # type: ignore[assignment]

FidelityStatus = Literal["stable", "review", "drift", "unavailable"]
GeometrySource = Literal["depth_video", "instance_maps"]
SAMPLE_PROGRESS = (0.0, 0.25, 0.5, 0.75, 1.0)


def _require_cv2():
    if cv2 is None:
        raise RuntimeError("Video fidelity scoring requires opencv-python-headless.")
    return cv2


@dataclass(frozen=True)
class FidelitySample:
    time_seconds: float
    score: float


@dataclass(frozen=True)
class VideoFidelityReport:
    score: float
    minimum_score: float
    status: FidelityStatus
    samples: tuple[FidelitySample, ...]
    protected_instance_min_score: float | None = None
    temporal_consistency_score: float | None = None
    # Lighting-invariant silhouette agreement with the geometry that produced
    # the preview. Reported beside the appearance score so a correct night
    # render is not called drift; advisory until calibrated.
    geometry_score: float | None = None
    geometry_min_score: float | None = None
    geometry_status: FidelityStatus | None = None
    geometry_samples: tuple[FidelitySample, ...] = ()
    geometry_source: GeometrySource | None = None

    def metadata(self) -> dict:
        metadata = {
            "fidelity_score": self.score,
            "fidelity_min_score": self.minimum_score,
            "fidelity_status": self.status,
            "fidelity_samples": [asdict(sample) for sample in self.samples],
        }
        if self.protected_instance_min_score is not None:
            metadata["protected_instance_min_score"] = self.protected_instance_min_score
        if self.temporal_consistency_score is not None:
            metadata["temporal_consistency_score"] = self.temporal_consistency_score
        if self.geometry_score is not None:
            metadata["geometry_score"] = self.geometry_score
            metadata["geometry_min_score"] = self.geometry_min_score
            metadata["geometry_status"] = self.geometry_status
            metadata["geometry_samples"] = [asdict(sample) for sample in self.geometry_samples]
            metadata["geometry_source"] = self.geometry_source
        return metadata


def _normalized_gray(frame: np.ndarray) -> np.ndarray:
    cv = _require_cv2()
    if frame is None or frame.size == 0:
        raise ValueError("A fidelity frame was empty.")
    resized = cv.resize(frame, (320, 180), interpolation=cv.INTER_AREA)
    if resized.ndim == 2:
        return resized.astype(np.uint8)
    return cv.cvtColor(resized, cv.COLOR_BGR2GRAY)


def _translation_align(reference: np.ndarray, candidate: np.ndarray) -> np.ndarray:
    cv = _require_cv2()
    try:
        (shift_x, shift_y), response = cv.phaseCorrelate(reference.astype(np.float32), candidate.astype(np.float32))
    except cv.error:
        return candidate
    if response < 0.05 or abs(shift_x) > 24 or abs(shift_y) > 24:
        return candidate
    matrix = np.float32([[1, 0, -shift_x], [0, 1, -shift_y]])
    return cv.warpAffine(
        candidate,
        matrix,
        (candidate.shape[1], candidate.shape[0]),
        flags=cv.INTER_LINEAR,
        borderMode=cv.BORDER_REFLECT,
    )


def _ssim(reference: np.ndarray, candidate: np.ndarray) -> float:
    cv = _require_cv2()
    ref = reference.astype(np.float32)
    cand = candidate.astype(np.float32)
    mu_ref = cv.GaussianBlur(ref, (11, 11), 1.5)
    mu_cand = cv.GaussianBlur(cand, (11, 11), 1.5)
    sigma_ref = cv.GaussianBlur(ref * ref, (11, 11), 1.5) - mu_ref * mu_ref
    sigma_cand = cv.GaussianBlur(cand * cand, (11, 11), 1.5) - mu_cand * mu_cand
    sigma_cross = cv.GaussianBlur(ref * cand, (11, 11), 1.5) - mu_ref * mu_cand
    c1 = 6.5025
    c2 = 58.5225
    numerator = (2 * mu_ref * mu_cand + c1) * (2 * sigma_cross + c2)
    denominator = (mu_ref * mu_ref + mu_cand * mu_cand + c1) * (sigma_ref + sigma_cand + c2)
    value = float(np.mean(numerator / np.maximum(denominator, 1e-6)))
    return max(0.0, min(1.0, value))


def _edge_overlap(reference: np.ndarray, candidate: np.ndarray) -> float:
    cv = _require_cv2()
    ref_edges = cv.Canny(reference, 55, 140) > 0
    cand_edges = cv.Canny(candidate, 55, 140) > 0
    if not ref_edges.any() or not cand_edges.any():
        return 1.0 if np.array_equal(ref_edges, cand_edges) else 0.0
    kernel = np.ones((3, 3), np.uint8)
    ref_near = cv.dilate(ref_edges.astype(np.uint8), kernel) > 0
    cand_near = cv.dilate(cand_edges.astype(np.uint8), kernel) > 0
    ref_recall = float(np.count_nonzero(ref_edges & cand_near) / np.count_nonzero(ref_edges))
    cand_recall = float(np.count_nonzero(cand_edges & ref_near) / np.count_nonzero(cand_edges))
    return (ref_recall + cand_recall) / 2


def _histogram_similarity(reference: np.ndarray, candidate: np.ndarray) -> float:
    cv = _require_cv2()
    ref_hist = cv.calcHist([reference], [0], None, [64], [0, 256])
    cand_hist = cv.calcHist([candidate], [0], None, [64], [0, 256])
    correlation = float(cv.compareHist(ref_hist, cand_hist, cv.HISTCMP_CORREL))
    return max(0.0, min(1.0, (correlation + 1.0) / 2.0))


def score_frame_similarity(reference_frame: np.ndarray, candidate_frame: np.ndarray) -> float:
    """Return a 0-100 structural-fidelity score for two corresponding frames."""
    reference = _normalized_gray(reference_frame)
    candidate = _translation_align(reference, _normalized_gray(candidate_frame))
    score = (
        0.58 * _ssim(reference, candidate)
        + 0.32 * _edge_overlap(reference, candidate)
        + 0.10 * _histogram_similarity(reference, candidate)
    )
    return round(max(0.0, min(100.0, score * 100.0)), 1)


def _score_protected_region(
    reference_frame: np.ndarray,
    candidate_frame: np.ndarray,
    instance_map: np.ndarray,
) -> float | None:
    cv = _require_cv2()
    mask = np.any(instance_map != 0, axis=2) if instance_map.ndim == 3 else instance_map != 0
    mask = cv.resize(mask.astype(np.uint8), (320, 180), interpolation=cv.INTER_NEAREST) > 0
    if np.count_nonzero(mask) < 64:
        return None
    ys, xs = np.where(mask)
    padding = 4
    left = max(0, int(xs.min()) - padding)
    right = min(320, int(xs.max()) + padding + 1)
    top = max(0, int(ys.min()) - padding)
    bottom = min(180, int(ys.max()) + padding + 1)
    reference = cv.resize(reference_frame, (320, 180), interpolation=cv.INTER_AREA)[top:bottom, left:right]
    candidate = cv.resize(candidate_frame, (320, 180), interpolation=cv.INTER_AREA)[top:bottom, left:right]
    return score_frame_similarity(reference, candidate)


def _temporal_consistency(
    reference_frames: Sequence[np.ndarray],
    generated_frames: Sequence[np.ndarray],
) -> float:
    ratios: list[float] = []
    for reference_a, reference_b, generated_a, generated_b in zip(
        reference_frames[:-1],
        reference_frames[1:],
        generated_frames[:-1],
        generated_frames[1:],
        strict=True,
    ):
        ref_a = _normalized_gray(reference_a).astype(np.float32)
        ref_b = _normalized_gray(reference_b).astype(np.float32)
        gen_a = _normalized_gray(generated_a).astype(np.float32)
        gen_b = _normalized_gray(generated_b).astype(np.float32)
        reference_motion = float(np.mean(np.abs(ref_b - ref_a)))
        generated_motion = float(np.mean(np.abs(gen_b - gen_a)))
        ratio = (generated_motion + 1.0) / (reference_motion + 1.0)
        ratios.append(float(np.exp(-abs(np.log(ratio)))))
    return round(100.0 * sum(ratios) / max(1, len(ratios)), 1)


def classify_fidelity(score: float, minimum_score: float) -> FidelityStatus:
    if score >= 72 and minimum_score >= 60:
        return "stable"
    if score >= 52 and minimum_score >= 36:
        return "review"
    return "drift"


def _clahe_gray(frame: np.ndarray) -> np.ndarray:
    """Stretch and equalise contrast so a night or hazy finish keeps its silhouettes."""
    cv = _require_cv2()
    low, high = np.percentile(frame, (1, 99))
    stretched = np.clip((frame.astype(np.float32) - float(low)) * (255.0 / max(float(high - low), 1.0)), 0, 255)
    return cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(stretched.astype(np.uint8))


def _depth_structure_edges(depth_gray: np.ndarray) -> np.ndarray:
    """Silhouette edges of the inverse-depth track, without the ground ramp."""
    cv = _require_cv2()
    blurred = cv.GaussianBlur(depth_gray, (0, 0), 1.0)
    edges = cv.Canny(blurred, 12, 36) > 0
    gradient_x = cv.Sobel(blurred, cv.CV_32F, 1, 0, ksize=3)
    gradient_y = cv.Sobel(blurred, cv.CV_32F, 0, 1, ksize=3)
    magnitude = np.sqrt(gradient_x * gradient_x + gradient_y * gradient_y)
    return edges & (magnitude > 6.0)


def _long_edges(edges: np.ndarray, min_pixels: int = 24) -> np.ndarray:
    """Keep edge components long enough to be structure rather than texture."""
    cv = _require_cv2()
    count, labels, stats, _ = cv.connectedComponentsWithStats(edges.astype(np.uint8), connectivity=8)
    keep = np.zeros(count, dtype=bool)
    for label in range(1, count):
        keep[label] = stats[label, cv.CC_STAT_AREA] >= min_pixels
    return keep[labels]


def _within(edges: np.ndarray, radius: int) -> np.ndarray:
    cv = _require_cv2()
    size = 2 * radius + 1
    return cv.dilate(edges.astype(np.uint8), np.ones((size, size), np.uint8)) > 0


def score_geometry_frame(
    depth_gray: np.ndarray,
    reference_frame: np.ndarray,
    candidate_frame: np.ndarray,
    region_mask: np.ndarray | None = None,
) -> float:
    """0-100 agreement between the finished frame's edges and the source geometry.

    Recall: every depth silhouette must still be drawn (missing or moved
    buildings lower it). Precision: every long edge in the output must be
    explained by a depth silhouette or by an edge the preview already had
    (invented structure lowers it). Lighting changes leave both unchanged.
    """
    cv = _require_cv2()
    reference = _normalized_gray(reference_frame)
    candidate = _translation_align(reference, _normalized_gray(candidate_frame))
    depth = cv.resize(depth_gray, (320, 180), interpolation=cv.INTER_AREA)
    depth_edges = _depth_structure_edges(depth)
    # CLAHE recovers contrast in dark or hazy finishes; the lower thresholds
    # keep moderate-contrast silhouettes that the appearance score's 55/140
    # Canny would drop.
    candidate_edges = cv.Canny(_clahe_gray(candidate), 30, 90) > 0
    reference_edges = cv.Canny(_clahe_gray(reference), 30, 90) > 0
    if region_mask is not None:
        mask = cv.resize(region_mask.astype(np.uint8), (320, 180), interpolation=cv.INTER_NEAREST) > 0
        mask = _within(mask, 6)
        depth_edges &= mask
        candidate_edges &= mask
        reference_edges &= mask
    if not depth_edges.any():
        return 100.0 if not _long_edges(candidate_edges).any() else 0.0
    recall = float(np.count_nonzero(depth_edges & _within(candidate_edges, 2)) / np.count_nonzero(depth_edges))
    long_candidate = _long_edges(candidate_edges)
    explained = _within(depth_edges | reference_edges, 2)
    precision = (
        float(np.count_nonzero(long_candidate & explained) / np.count_nonzero(long_candidate))
        if long_candidate.any()
        else 1.0
    )
    return round(max(0.0, min(100.0, 100.0 * (0.7 * recall + 0.3 * precision))), 1)


def classify_geometry(score: float, minimum_score: float) -> FidelityStatus:
    """Provisional bands; calibrated by the evaluation harness."""
    if score >= 68 and minimum_score >= 55:
        return "stable"
    if score >= 48 and minimum_score >= 32:
        return "review"
    return "drift"


def _instance_map_edges(instance_map: np.ndarray) -> np.ndarray:
    """Boundaries of the authored instances when no depth track exists."""
    cv = _require_cv2()
    mask = np.any(instance_map != 0, axis=2) if instance_map.ndim == 3 else instance_map != 0
    labels = (
        instance_map[:, :, 0].astype(np.int32) * 65536
        + instance_map[:, :, 1].astype(np.int32) * 256
        + instance_map[:, :, 2].astype(np.int32)
        if instance_map.ndim == 3
        else instance_map.astype(np.int32)
    )
    gradient = cv.morphologyEx(labels.astype(np.float32), cv.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
    return (gradient & mask).astype(np.uint8) * 255


def _decode_image(data: bytes) -> np.ndarray:
    cv = _require_cv2()
    frame = cv.imdecode(np.frombuffer(data, dtype=np.uint8), cv.IMREAD_COLOR)
    if frame is None:
        raise ValueError("A route keyframe could not be decoded.")
    return frame


def _sample_video(data: bytes, progress_points: Sequence[float], suffix: str) -> list[np.ndarray]:
    cv = _require_cv2()
    if not data:
        raise ValueError("The video supplied for fidelity scoring is empty.")
    with tempfile.TemporaryDirectory(prefix="city-prompt-fidelity-") as temp_dir:
        path = Path(temp_dir) / f"video{suffix}"
        path.write_bytes(data)
        capture = cv.VideoCapture(str(path))
        try:
            if not capture.isOpened():
                raise ValueError("The video supplied for fidelity scoring could not be decoded.")
            frame_count = int(capture.get(cv.CAP_PROP_FRAME_COUNT))
            if frame_count < 2:
                # Browser-recorded WebM files can omit a reliable frame count.
                # Decode them sequentially before concluding the clip is empty.
                capture.set(cv.CAP_PROP_POS_FRAMES, 0)
                decoded: list[np.ndarray] = []
                while True:
                    ok, frame = capture.read()
                    if not ok or frame is None:
                        break
                    decoded.append(frame)
                if len(decoded) < 2:
                    raise ValueError("The video supplied for fidelity scoring has too few frames.")
                return [decoded[round(progress * (len(decoded) - 1))] for progress in progress_points]
            frames: list[np.ndarray] = []
            for progress in progress_points:
                frame_index = round(max(0.0, min(1.0, progress)) * (frame_count - 1))
                capture.set(cv.CAP_PROP_POS_FRAMES, frame_index)
                ok, frame = capture.read()
                if not ok or frame is None:
                    raise ValueError(f"Could not decode fidelity frame {frame_index}.")
                frames.append(frame)
            return frames
        finally:
            capture.release()


def score_video_fidelity(
    *,
    generated_video: bytes,
    duration_seconds: int,
    preview_video: bytes | None = None,
    preview_mime_type: str | None = None,
    route_keyframes: Sequence[bytes] = (),
    instance_id_maps: Sequence[bytes] = (),
    depth_video: bytes | None = None,
    depth_mime_type: str | None = None,
) -> VideoFidelityReport:
    """Compare generated frames with corresponding deterministic controls."""
    generated_frames = _sample_video(generated_video, SAMPLE_PROGRESS, ".mp4")
    if preview_video:
        suffix = ".webm" if (preview_mime_type or "").startswith("video/webm") else ".mp4"
        reference_frames = _sample_video(preview_video, SAMPLE_PROGRESS, suffix)
    elif len(route_keyframes) >= 2:
        decoded = [_decode_image(frame) for frame in route_keyframes]
        reference_frames = [decoded[round(progress * (len(decoded) - 1))] for progress in SAMPLE_PROGRESS]
    else:
        raise ValueError("Fidelity scoring requires a route preview or at least two route keyframes.")

    samples = tuple(
        FidelitySample(
            time_seconds=round(progress * duration_seconds, 1),
            score=score_frame_similarity(reference, generated),
        )
        for progress, reference, generated in zip(SAMPLE_PROGRESS, reference_frames, generated_frames, strict=True)
    )
    score = round(sum(sample.score for sample in samples) / len(samples), 1)
    minimum_score = min(sample.score for sample in samples)
    protected_scores: list[float] = []
    if instance_id_maps:
        decoded_maps = [_decode_image(value) for value in instance_id_maps]
        for progress, reference, generated in zip(
            SAMPLE_PROGRESS,
            reference_frames,
            generated_frames,
            strict=True,
        ):
            map_index = round(progress * (len(decoded_maps) - 1))
            protected_score = _score_protected_region(
                reference,
                generated,
                decoded_maps[map_index],
            )
            if protected_score is not None:
                protected_scores.append(protected_score)
    protected_min = min(protected_scores) if protected_scores else None
    temporal_score = _temporal_consistency(reference_frames, generated_frames)
    status = classify_fidelity(score, minimum_score)
    if protected_min is not None:
        if protected_min < 40:
            status = "drift"
        elif protected_min < 58 and status == "stable":
            status = "review"
    if temporal_score < 45:
        status = "drift"
    elif temporal_score < 65 and status == "stable":
        status = "review"

    geometry_samples: tuple[FidelitySample, ...] = ()
    geometry_source: GeometrySource | None = None
    cv = _require_cv2()
    if depth_video:
        depth_suffix = ".webm" if (depth_mime_type or "").startswith("video/webm") else ".mp4"
        depth_frames = _sample_video(depth_video, SAMPLE_PROGRESS, depth_suffix)
        geometry_source = "depth_video"
        geometry_samples = tuple(
            FidelitySample(
                time_seconds=round(progress * duration_seconds, 1),
                score=score_geometry_frame(
                    cv.cvtColor(depth, cv.COLOR_BGR2GRAY) if depth.ndim == 3 else depth,
                    reference,
                    generated,
                ),
            )
            for progress, depth, reference, generated in zip(
                SAMPLE_PROGRESS, depth_frames, reference_frames, generated_frames, strict=True
            )
        )
    elif instance_id_maps:
        decoded_maps = [_decode_image(value) for value in instance_id_maps]
        geometry_source = "instance_maps"
        geometry_samples = tuple(
            FidelitySample(
                time_seconds=round(progress * duration_seconds, 1),
                score=score_geometry_frame(
                    _instance_map_edges(decoded_maps[round(progress * (len(decoded_maps) - 1))]),
                    reference,
                    generated,
                ),
            )
            for progress, reference, generated in zip(SAMPLE_PROGRESS, reference_frames, generated_frames, strict=True)
        )
    geometry_score = (
        round(sum(sample.score for sample in geometry_samples) / len(geometry_samples), 1) if geometry_samples else None
    )
    geometry_min = min(sample.score for sample in geometry_samples) if geometry_samples else None
    return VideoFidelityReport(
        score=score,
        minimum_score=minimum_score,
        status=status,
        samples=samples,
        protected_instance_min_score=protected_min,
        temporal_consistency_score=temporal_score,
        geometry_score=geometry_score,
        geometry_min_score=geometry_min,
        geometry_status=classify_geometry(geometry_score, geometry_min) if geometry_score is not None else None,
        geometry_samples=geometry_samples,
        geometry_source=geometry_source,
    )
