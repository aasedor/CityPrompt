"""Convert free monocular/multi-view geometry outputs into architectural evidence.

The pass deliberately treats learned geometry as evidence rather than production
mesh.  MoGe contributes a sharp single-view depth/normal estimate, while Depth
Anything 3 contributes multi-view depth, camera alignment and confidence.  The
result is a small JSON contract and review board that can safely drive authored
Blender assemblies.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


SCHEMA = "archetype-geometry-evidence@1"


def _font(size: int, bold: bool = False):
    path = Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf")
    return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default()


def _normalise(values: np.ndarray, mask: np.ndarray, low: float = 5.0, high: float = 95.0) -> np.ndarray:
    selected = values[mask & np.isfinite(values)]
    if not selected.size:
        return np.zeros(values.shape, dtype=np.float32)
    floor, ceiling = np.percentile(selected, [low, high])
    span = max(float(ceiling - floor), 1e-6)
    return np.clip((values - floor) / span, 0.0, 1.0).astype(np.float32)


def _colour_map(values: np.ndarray, mask: np.ndarray, invert: bool = False) -> np.ndarray:
    normalised = _normalise(values, mask)
    if invert:
        normalised = 1.0 - normalised
    raster = np.uint8(np.clip(normalised * 255.0, 0, 255))
    colour = cv2.applyColorMap(raster, cv2.COLORMAP_TURBO)
    colour[~mask] = (226, 224, 218)
    return cv2.cvtColor(colour, cv2.COLOR_BGR2RGB)


def _polygon_mask(shape: tuple[int, int], polygon: list[list[float]]) -> np.ndarray:
    height, width = shape
    points = np.array([[round(x * width), round(y * height)] for x, y in polygon], np.int32)
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(mask, [points], 255)
    return mask > 0


def _fit_affine(source: np.ndarray, target: np.ndarray, mask: np.ndarray) -> tuple[float, float, np.ndarray]:
    valid = mask & np.isfinite(source) & np.isfinite(target)
    design = np.column_stack([source[valid], np.ones(int(valid.sum()))])
    values = target[valid]
    keep = np.ones(values.shape, dtype=bool)
    coefficients = np.array([1.0, 0.0])
    for _ in range(4):
        coefficients = np.linalg.lstsq(design[keep], values[keep], rcond=None)[0]
        residual = np.abs(values - design @ coefficients)
        median = float(np.median(residual[keep]))
        sigma = max(1e-6, 1.4826 * median)
        keep = residual <= 3.0 * sigma
    aligned = source * float(coefficients[0]) + float(coefficients[1])
    return float(coefficients[0]), float(coefficients[1]), aligned


def _fit_image_plane(depth: np.ndarray, mask: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    height, width = depth.shape
    ys, xs = np.indices(depth.shape, dtype=np.float32)
    valid = mask & np.isfinite(depth)
    x = (xs - width * 0.5) / max(width, 1)
    y = (ys - height * 0.5) / max(height, 1)
    design = np.column_stack([x[valid], y[valid], np.ones(int(valid.sum()))])
    values = depth[valid]
    keep = np.ones(values.shape, dtype=bool)
    coefficients = np.zeros(3, dtype=np.float64)
    for _ in range(4):
        coefficients = np.linalg.lstsq(design[keep], values[keep], rcond=None)[0]
        residual = np.abs(values - design @ coefficients)
        median = float(np.median(residual[keep]))
        keep = residual <= max(1e-6, 3.0 * 1.4826 * median)
    plane = coefficients[0] * x + coefficients[1] * y + coefficients[2]
    residual_map = np.abs(depth - plane)
    robust_range = max(float(np.percentile(values, 95) - np.percentile(values, 5)), 1e-6)
    return residual_map, {
        "median_ratio": round(float(np.median(residual_map[valid]) / robust_range), 5),
        "p90_ratio": round(float(np.percentile(residual_map[valid], 90) / robust_range), 5),
    }


def _roof_peaks(depth: np.ndarray, mask: np.ndarray) -> list[dict[str, float]]:
    base = float(np.percentile(depth[mask], 90))
    height = np.where(mask, base - depth, float(np.median(base - depth[mask])))
    smooth = cv2.GaussianBlur(height.astype(np.float32), (0, 0), sigmaX=max(3.0, min(depth.shape) / 40.0))
    neighbourhood = max(21, int(round(min(depth.shape) / 10.0)) | 1)
    maxima = cv2.dilate(smooth, np.ones((neighbourhood, neighbourhood), np.uint8))
    candidates = (smooth == maxima) & mask & (smooth > np.percentile(smooth[mask], 55))
    count, labels = cv2.connectedComponents(candidates.astype(np.uint8))
    peaks: list[dict[str, float]] = []
    for index in range(1, count):
        ys, xs = np.where(labels == index)
        if not xs.size:
            continue
        peaks.append({
            "x": round(float(xs.mean() / depth.shape[1]), 4),
            "y": round(float(ys.mean() / depth.shape[0]), 4),
            "relative_height": round(float(smooth[ys, xs].max()), 5),
        })
    return sorted(peaks, key=lambda item: item["relative_height"], reverse=True)[:12]


def _confidence_stats(confidence: np.ndarray, mask: np.ndarray) -> dict[str, float]:
    selected = confidence[mask & np.isfinite(confidence)]
    return {
        "mean": round(float(selected.mean()), 4),
        "p10": round(float(np.percentile(selected, 10)), 4),
        "median": round(float(np.median(selected)), 4),
        "p90": round(float(np.percentile(selected, 90)), 4),
    }


def _contain(path: Path, size: tuple[int, int], background: str = "#e8e5df") -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, background)
    canvas.paste(image, ((size[0] - image.width) // 2, (size[1] - image.height) // 2))
    return canvas


def _write_board(output: Path, panels: list[tuple[str, Path]], summary: list[str]) -> None:
    board = Image.new("RGB", (2200, 1430), "#f5f1e9")
    draw = ImageDraw.Draw(board)
    draw.text((55, 30), "Free Archetype Geometry Pass v75", font=_font(42, True), fill="#101b2b")
    draw.text((57, 89), "MoGe-2 normals + DA3 multi-view confidence, converted into authored-geometry evidence.", font=_font(21), fill="#536174")
    draw.rectangle((55, 132, 2145, 141), fill="#2aa7a1")
    for index, (label, path) in enumerate(panels):
        left = 55 + (index % 3) * 710
        top = 180 + (index // 3) * 515
        board.paste(_contain(path, (660, 420)), (left, top))
        draw.rectangle((left, top, left + 660, top + 420), outline="#b8b1a5", width=2)
        draw.rectangle((left, top, left + 440, top + 38), fill="#111c2b")
        draw.text((left + 14, top + 9), label, font=_font(15, True), fill="white")
    draw.rectangle((55, 1240, 2145, 1380), fill="#e1ddd4")
    for index, line in enumerate(summary):
        draw.text((75, 1260 + index * 35), line, font=_font(19, index == 0), fill="#273548")
    board.save(output, optimize=True)


def analyse(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    moge_depth = cv2.imread(str(args.moge_depth), cv2.IMREAD_UNCHANGED)
    if moge_depth is None or moge_depth.ndim != 2:
        raise ValueError(f"Unable to read MoGe depth EXR: {args.moge_depth}")
    audited = cv2.imread(str(args.street_mask), cv2.IMREAD_GRAYSCALE)
    moge_valid = cv2.imread(str(args.moge_mask), cv2.IMREAD_GRAYSCALE)
    if audited is None or moge_valid is None:
        raise ValueError("Street and MoGe validity masks are required")
    audited = cv2.resize(audited, (moge_depth.shape[1], moge_depth.shape[0]), interpolation=cv2.INTER_NEAREST) > 0
    moge_valid = moge_valid > 0
    street_mask = audited & moge_valid & np.isfinite(moge_depth)

    prediction = np.load(args.da3_npz)
    da3_depth = prediction["depth"].astype(np.float32)
    da3_conf = prediction["conf"].astype(np.float32)
    if da3_depth.shape[0] < 3:
        raise ValueError("The bounded geometry pass requires street, oblique and roof DA3 views")

    street_da3 = cv2.resize(da3_depth[0], (moge_depth.shape[1], moge_depth.shape[0]), interpolation=cv2.INTER_CUBIC)
    street_conf = cv2.resize(da3_conf[0], (moge_depth.shape[1], moge_depth.shape[0]), interpolation=cv2.INTER_LINEAR)
    scale, offset, aligned_da3 = _fit_affine(street_da3, moge_depth, street_mask)
    disagreement = np.abs(moge_depth - aligned_da3)
    robust_depth_range = max(float(np.percentile(moge_depth[street_mask], 95) - np.percentile(moge_depth[street_mask], 5)), 1e-6)
    agreement_median = float(np.median(disagreement[street_mask]) / robust_depth_range)
    agreement_p90 = float(np.percentile(disagreement[street_mask], 90) / robust_depth_range)

    plane_residual, plane_metrics = _fit_image_plane(moge_depth, street_mask)
    smooth_depth = np.where(street_mask, moge_depth, float(np.median(moge_depth[street_mask])))
    smooth_depth = cv2.GaussianBlur(smooth_depth.astype(np.float32), (0, 0), sigmaX=2.0)
    curvature = np.abs(cv2.Laplacian(smooth_depth, cv2.CV_32F))
    curvature_scaled = _normalise(curvature, street_mask, 20, 98)
    curved_ratio = float(np.mean(curvature_scaled[street_mask] > 0.18))

    ys, xs = np.where(street_mask)
    bbox_height = max(1, int(ys.max() - ys.min()))
    upper_mask = street_mask.copy()
    candidate_top = int(ys.min() + bbox_height * 0.14)
    candidate_bottom = int(ys.min() + bbox_height * 0.64)
    upper_mask[:candidate_top, :] = False
    upper_mask[candidate_bottom:, :] = False
    vertical_edge = np.abs(cv2.Sobel(smooth_depth, cv2.CV_32F, 0, 1, ksize=5))
    row_strength = np.full(moge_depth.shape[0], -np.inf, dtype=np.float32)
    for row in range(candidate_top, candidate_bottom):
        selected = vertical_edge[row, upper_mask[row]]
        if selected.size >= max(8, int(moge_depth.shape[1] * 0.04)):
            row_strength[row] = float(np.median(selected))
    overhang_row = int(np.argmax(row_strength))
    overhang_y = float(overhang_row / moge_depth.shape[0])
    above_depth = moge_depth[max(0, overhang_row - 8):overhang_row, :]
    below_depth = moge_depth[overhang_row:min(moge_depth.shape[0], overhang_row + 8), :]
    depth_step = 0.0
    common_columns = street_mask[max(0, overhang_row - 8):overhang_row, :].any(axis=0)
    common_columns &= street_mask[overhang_row:min(moge_depth.shape[0], overhang_row + 8), :].any(axis=0)
    if common_columns.any():
        upper_values = above_depth[:, common_columns]
        lower_values = below_depth[:, common_columns]
        depth_step = abs(float(np.median(upper_values) - np.median(lower_values))) / robust_depth_range

    contract = json.loads(args.contract.read_text(encoding="utf-8"))
    roof_polygon = next(view for view in contract["views"] if view["role"] == "roof_plan")["reference_silhouette_polygon"]
    roof_mask = _polygon_mask(da3_depth[2].shape, roof_polygon)
    roof_peaks = _roof_peaks(da3_depth[2], roof_mask)
    roof_range = float(np.percentile(da3_depth[2][roof_mask], 90) - np.percentile(da3_depth[2][roof_mask], 10))
    roof_median = max(abs(float(np.median(da3_depth[2][roof_mask]))), 1e-6)
    roof_edges = cv2.Canny(np.uint8(_normalise(da3_depth[2], roof_mask) * 255), 45, 120) > 0
    roof_edge_density = float(np.mean(roof_edges[roof_mask]))

    conf_norm = _normalise(street_conf, street_mask, 10, 90)
    disagreement_norm = np.clip(disagreement / max(float(np.percentile(disagreement[street_mask], 95)), 1e-6), 0, 1)
    uncertainty = np.clip(0.62 * disagreement_norm + 0.28 * (1.0 - conf_norm) + 0.10 * curvature_scaled, 0, 1)
    uncertainty[~street_mask] = 0.0
    reliable_fraction = float(np.mean(uncertainty[street_mask] < 0.55))
    valid_coverage = float(street_mask.sum() / max(1, audited.sum()))

    street_depth_path = output_dir / "street-depth.png"
    street_curvature_path = output_dir / "street-curvature.png"
    street_uncertainty_path = output_dir / "street-uncertainty.png"
    roof_depth_path = output_dir / "roof-depth.png"
    Image.fromarray(_colour_map(moge_depth, street_mask, invert=True)).save(street_depth_path)
    Image.fromarray(_colour_map(curvature_scaled, street_mask)).save(street_curvature_path)
    Image.fromarray(_colour_map(uncertainty, street_mask)).save(street_uncertainty_path)
    Image.fromarray(_colour_map(da3_depth[2], roof_mask, invert=True)).save(roof_depth_path)

    accepted = (
        valid_coverage >= 0.88
        and agreement_median <= 0.06
        and _confidence_stats(da3_conf[2], roof_mask)["median"] >= 1.25
    )
    evidence: dict[str, Any] = {
        "schema": SCHEMA,
        "id": args.id,
        "status": "accepted_for_authored_geometry" if accepted else "review",
        "scope": "one_archetype_bounded_pilot",
        "source": {
            "archetype_id": args.archetype_id,
            "variant_id": args.variant_id,
            "reference_images": [str(args.street_image), str(args.oblique_image), str(args.roof_image)],
            "audited_street_mask": str(args.street_mask),
        },
        "provenance": {
            "moge": {"model": "Ruicheng/moge-2-vits-normal", "license": "MIT", "role": "street metric depth and normals"},
            "da3": {"model": "depth-anything/DA3-BASE", "license": "Apache-2.0", "role": "three-view relative depth, cameras and confidence"},
            "opencv": {"role": "registered masks, robust alignment, curvature and edge analysis"},
        },
        "declared_dimensions_m": {"width": args.width_m, "depth": args.depth_m, "height": args.height_m},
        "street_geometry": {
            "valid_coverage": round(valid_coverage, 5),
            "cross_model_alignment": {"scale": round(scale, 5), "offset": round(offset, 5)},
            "cross_model_disagreement": {"median_ratio": round(agreement_median, 5), "p90_ratio": round(agreement_p90, 5)},
            "front_plane_residual": plane_metrics,
            "curved_surface_ratio": round(curved_ratio, 5),
            "visible_horizontal_depth_edge_candidate": {
                "image_y": round(overhang_y, 5),
                "depth_step_ratio": round(depth_step, 5),
                "confidence": round(max(0.0, 1.0 - agreement_p90), 4),
                "policy": "Advisory edge location only; confirm overhang direction from the reference image.",
            },
            "confidence": _confidence_stats(street_conf, street_mask),
        },
        "roof_geometry": {
            "dominant_elevation_peaks": roof_peaks,
            "dominant_peak_count": len(roof_peaks),
            "relative_height_range": round(roof_range / roof_median, 5),
            "edge_density": round(roof_edge_density, 5),
            "confidence": _confidence_stats(da3_conf[2], roof_mask),
        },
        "uncertainty": {
            "reliable_street_fraction": round(reliable_fraction, 5),
            "hidden_sides": "high",
            "reflective_perforated_envelope": "high",
            "visible_cantilever_and_front_curvature": "low",
            "roof_plan_from_declared_top_view": "medium",
            "policy": "Use learned output only for visible plan/section constraints; hidden construction remains authored from architectural knowledge.",
        },
        "authored_geometry_constraints": {
            "front_envelope": "continuous_curved_screen_with_visible_layer_separation",
            "cantilever": "deep_left_biased_projecting_gallery_with_real_soffit",
            "inner_massing": "multiple_asymmetric_curved_pods_not_orthogonal_boxes",
            "roof": "multi-level_curvilinear_roofscape_with_interstitial_courts",
            "do_not_copy": ["raw point cloud", "vegetation depth", "sky depth", "occluded rear geometry"],
        },
        "gates": {
            "valid_coverage_min_0_88": valid_coverage >= 0.88,
            "cross_model_median_disagreement_max_0_06": agreement_median <= 0.06,
            "roof_confidence_median_min_1_25": _confidence_stats(da3_conf[2], roof_mask)["median"] >= 1.25,
        },
        "outputs": {
            "moge_proxy_glb": str(args.moge_glb),
            "da3_proxy_glb": str(args.da3_glb),
            "review_board": str(output_dir / "geometry-evidence-board.png"),
        },
    }

    evidence_path = output_dir / "architectural-geometry-evidence.json"
    evidence_path.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    panels = [
        ("ARCHETYPE — STREET", args.street_image),
        ("MOGE — DEPTH", street_depth_path),
        ("MOGE — NORMALS", args.moge_normal),
        ("ARCHETYPE — ROOF", args.roof_image),
        ("DA3 — ROOF HEIGHT", roof_depth_path),
        ("ENSEMBLE — UNCERTAINTY", street_uncertainty_path),
    ]
    _write_board(output_dir / "geometry-evidence-board.png", panels, [
        f"Gate: {evidence['status'].upper()} | valid coverage {valid_coverage:.3f} | median disagreement {agreement_median:.3f}",
        f"Visible surface curvature {curved_ratio:.3f} | roof elevation peaks {len(roof_peaks)} | reliable street area {reliable_fraction:.3f}",
        "Red/yellow evidence remains advisory: reflective veil, glazing and hidden sides require authored architectural logic.",
    ])
    return evidence


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    value.add_argument("--id", default="titanium-museum-free-geometry-v75")
    value.add_argument("--archetype-id", required=True)
    value.add_argument("--variant-id", required=True)
    value.add_argument("--street-image", type=Path, required=True)
    value.add_argument("--oblique-image", type=Path, required=True)
    value.add_argument("--roof-image", type=Path, required=True)
    value.add_argument("--street-mask", type=Path, required=True)
    value.add_argument("--moge-depth", type=Path, required=True)
    value.add_argument("--moge-mask", type=Path, required=True)
    value.add_argument("--moge-normal", type=Path, required=True)
    value.add_argument("--moge-glb", type=Path, required=True)
    value.add_argument("--da3-npz", type=Path, required=True)
    value.add_argument("--da3-glb", type=Path, required=True)
    value.add_argument("--contract", type=Path, required=True)
    value.add_argument("--width-m", type=float, required=True)
    value.add_argument("--depth-m", type=float, required=True)
    value.add_argument("--height-m", type=float, required=True)
    value.add_argument("--output-dir", type=Path, required=True)
    return value


def main() -> None:
    evidence = analyse(parser().parse_args())
    print(json.dumps({"status": evidence["status"], "outputs": evidence["outputs"]}, indent=2))


if __name__ == "__main__":
    main()
