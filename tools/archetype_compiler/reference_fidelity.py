"""OpenCV silhouette fidelity checks for camera-locked building pilots."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import cv2
import numpy as np


SCHEMA = "building-reference-fidelity@1"
REPORT_SCHEMA = "building-reference-fidelity-report@1"
EVIDENCE_SCHEMA = "building-reference-evidence@2"
EVIDENCE_REPORT_SCHEMA = "building-reference-evidence-report@2"


def normalized_polygon_mask(size: tuple[int, int], points: list[list[float]]) -> np.ndarray:
    """Rasterize an audited normalized building outline."""
    width, height = size
    polygon = np.asarray(
        [[round(float(x) * (width - 1)), round(float(y) * (height - 1))] for x, y in points],
        dtype=np.int32,
    )
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(mask, [polygon], 255)
    return mask


def extract_render_silhouette(
    image: np.ndarray,
    roi: list[float] | None = None,
    background_tolerance: float = 18.0,
) -> np.ndarray:
    """Extract the largest non-background subject from a neutral QA render.

    Presentation renders use a nearly uniform sky. Sampling the top/side border
    keeps the method deterministic and avoids a learned segmentation dependency.
    The ROI is part of the audited camera contract so roads and context props do
    not become building silhouette.
    """
    height, width = image.shape[:2]
    x0, y0, x1, y1 = roi or [0.0, 0.0, 1.0, 0.92]
    left, top = round(x0 * width), round(y0 * height)
    right, bottom = round(x1 * width), round(y1 * height)
    crop = image[top:bottom, left:right]
    if crop.size == 0:
        raise ValueError("render silhouette ROI is empty")

    strip = max(3, round(min(crop.shape[:2]) * 0.035))
    background_samples = np.concatenate(
        [crop[:strip].reshape(-1, 3), crop[:, :strip].reshape(-1, 3), crop[:, -strip:].reshape(-1, 3)],
        axis=0,
    )
    background = np.median(background_samples.astype(np.float32), axis=0)
    distance = np.linalg.norm(crop.astype(np.float32) - background, axis=2)
    candidate = np.where(distance >= float(background_tolerance), 255, 0).astype(np.uint8)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_CLOSE, kernel, iterations=2)
    candidate = cv2.morphologyEx(candidate, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    count, labels, stats, _centroids = cv2.connectedComponentsWithStats(candidate, 8)
    if count <= 1:
        raise ValueError("no foreground component found in render")

    centre_x = crop.shape[1] / 2
    best_label = max(
        range(1, count),
        key=lambda label: float(stats[label, cv2.CC_STAT_AREA])
        * (1.0 - min(0.55, abs((stats[label, cv2.CC_STAT_LEFT] + stats[label, cv2.CC_STAT_WIDTH] / 2) - centre_x) / crop.shape[1])),
    )
    subject = np.where(labels == best_label, 255, 0).astype(np.uint8)
    subject = cv2.morphologyEx(subject, cv2.MORPH_CLOSE, kernel, iterations=2)

    full = np.zeros((height, width), dtype=np.uint8)
    full[top:bottom, left:right] = subject
    return full


def _tight_bounds(mask: np.ndarray) -> tuple[int, int, int, int]:
    points = cv2.findNonZero(mask)
    if points is None:
        raise ValueError("silhouette mask is empty")
    x, y, width, height = cv2.boundingRect(points)
    return x, y, width, height


def normalize_silhouette(mask: np.ndarray, canvas: int = 512) -> tuple[np.ndarray, float]:
    """Bottom-centre a tight silhouette while preserving its aspect ratio."""
    x, y, width, height = _tight_bounds(mask)
    aspect = width / max(1, height)
    crop = mask[y:y + height, x:x + width]
    scale = min((canvas * 0.94) / width, (canvas * 0.94) / height)
    resized = cv2.resize(
        crop,
        (max(1, round(width * scale)), max(1, round(height * scale))),
        interpolation=cv2.INTER_NEAREST,
    )
    normalized = np.zeros((canvas, canvas), dtype=np.uint8)
    left = (canvas - resized.shape[1]) // 2
    top = canvas - round(canvas * 0.03) - resized.shape[0]
    normalized[top:top + resized.shape[0], left:left + resized.shape[1]] = resized
    return normalized, aspect


def _roofline(mask: np.ndarray) -> np.ndarray:
    result = np.full(mask.shape[1], np.nan, dtype=np.float32)
    for column in range(mask.shape[1]):
        rows = np.flatnonzero(mask[:, column])
        if rows.size:
            result[column] = float(rows[0]) / mask.shape[0]
    return result


def compare_silhouettes(reference: np.ndarray, render: np.ndarray) -> dict[str, float]:
    reference_norm, reference_aspect = normalize_silhouette(reference)
    render_norm, render_aspect = normalize_silhouette(render)
    intersection = np.count_nonzero((reference_norm > 0) & (render_norm > 0))
    union = np.count_nonzero((reference_norm > 0) | (render_norm > 0))
    roof_reference, roof_render = _roofline(reference_norm), _roofline(render_norm)
    valid = np.isfinite(roof_reference) & np.isfinite(roof_render)
    roof_rmse = float(np.sqrt(np.mean(np.square(roof_reference[valid] - roof_render[valid]))))
    return {
        "silhouette_iou": round(intersection / max(1, union), 5),
        "roofline_rmse": round(roof_rmse, 5),
        "aspect_ratio_error": round(abs(render_aspect / reference_aspect - 1.0), 5),
        "reference_aspect_ratio": round(reference_aspect, 5),
        "render_aspect_ratio": round(render_aspect, 5),
    }


def assess_contract(contract: dict[str, Any], render_path: Path) -> tuple[dict[str, Any], np.ndarray]:
    if contract.get("schema") != SCHEMA:
        raise ValueError(f"unsupported fidelity contract schema {contract.get('schema')!r}")
    reference_path = Path(contract["reference_image"])
    if not reference_path.is_absolute():
        reference_path = Path(__file__).resolve().parents[2] / reference_path
    reference_image = cv2.imread(str(reference_path), cv2.IMREAD_COLOR)
    render_image = cv2.imread(str(render_path), cv2.IMREAD_COLOR)
    if reference_image is None or render_image is None:
        raise FileNotFoundError("reference or render image could not be read")

    reference_mask = normalized_polygon_mask(
        (reference_image.shape[1], reference_image.shape[0]),
        contract["reference_silhouette_polygon"],
    )
    extraction = contract.get("render_extraction") or {}
    render_mask = extract_render_silhouette(
        render_image,
        extraction.get("roi"),
        float(extraction.get("background_tolerance", 18.0)),
    )
    metrics = compare_silhouettes(reference_mask, render_mask)
    thresholds = contract.get("thresholds") or {}
    checks = {
        "silhouette_iou": bool(
            metrics["silhouette_iou"]
            >= float(thresholds.get("silhouette_iou_min", 0.62))
        ),
        "roofline_rmse": bool(
            metrics["roofline_rmse"]
            <= float(thresholds.get("roofline_rmse_max", 0.12))
        ),
        "aspect_ratio_error": bool(
            metrics["aspect_ratio_error"]
            <= float(thresholds.get("aspect_ratio_error_max", 0.16))
        ),
    }
    report = {
        "schema": REPORT_SCHEMA,
        "contract": contract.get("id"),
        "reference_image": str(reference_path),
        "render_image": str(render_path),
        "status": "pass" if all(checks.values()) else "fail",
        "metrics": metrics,
        "checks": checks,
        "thresholds": thresholds,
    }

    reference_norm, _ = normalize_silhouette(reference_mask)
    render_norm, _ = normalize_silhouette(render_mask)
    overlay = np.zeros((512, 512, 3), dtype=np.uint8)
    overlay[reference_norm > 0] = (55, 190, 70)
    overlay[render_norm > 0] = np.maximum(overlay[render_norm > 0], (205, 80, 65))
    overlap = (reference_norm > 0) & (render_norm > 0)
    overlay[overlap] = (225, 220, 75)
    return report, overlay


def load_contract(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def assess_evidence_contract(
    contract: dict[str, Any],
    render_paths: dict[str, Path],
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    """Assess every declared reference role instead of approving one hero view.

    Each view remains a camera-locked v1 silhouette contract internally, which
    keeps old pilots and metrics stable. The v2 wrapper adds explicit roles,
    independent extraction settings and an aggregate release result. A roof
    or aerial view can therefore fail even when the street facade looks good.
    """
    if contract.get("schema") != EVIDENCE_SCHEMA:
        raise ValueError(f"unsupported evidence contract schema {contract.get('schema')!r}")
    views = contract.get("views") or []
    if len(views) < 2:
        raise ValueError("evidence contract requires at least two reference views")

    reports: list[dict[str, Any]] = []
    overlays: dict[str, np.ndarray] = {}
    for view in views:
        view_id = str(view["id"])
        render_key = str(view.get("render_key") or view_id)
        if render_key not in render_paths:
            raise KeyError(f"missing render path for evidence view {render_key!r}")
        legacy = {
            "schema": SCHEMA,
            "id": f"{contract.get('id')}-{view_id}",
            "reference_image": view["reference_image"],
            "reference_silhouette_polygon": view["reference_silhouette_polygon"],
            "render_extraction": view.get("render_extraction") or {},
            "thresholds": view.get("thresholds") or contract.get("thresholds") or {},
        }
        report, overlay = assess_contract(legacy, render_paths[render_key])
        report["view_id"] = view_id
        report["role"] = str(view.get("role") or view_id)
        report["render_key"] = render_key
        reports.append(report)
        overlays[view_id] = overlay

    metric_names = ("silhouette_iou", "roofline_rmse", "aspect_ratio_error")
    mean_metrics = {
        name: round(float(np.mean([view["metrics"][name] for view in reports])), 5)
        for name in metric_names
    }
    result = {
        "schema": EVIDENCE_REPORT_SCHEMA,
        "contract": contract.get("id"),
        "status": "pass" if all(view["status"] == "pass" for view in reports) else "fail",
        "required_roles": list(contract.get("required_roles") or []),
        "mean_metrics": mean_metrics,
        "views": reports,
    }
    return result, overlays
