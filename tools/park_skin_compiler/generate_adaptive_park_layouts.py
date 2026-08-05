"""Generate a bounded three-shape park layout matrix from metric rules."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from shapely import affinity
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import triangulate

try:
    from .compile_neighborhood_park_skins import REPO_ROOT
except ImportError:  # direct script execution
    from compile_neighborhood_park_skins import REPO_ROOT

DEFAULT_OUT = REPO_ROOT / "artifacts/neighborhood-park-adaptive-urban-v1/layouts"
ROLE_COLOURS = {
    "paver": "#7b8380",
    "lawn": "#3e6c31",
    "planting": "#8a813f",
    "safety": "#b89062",
    "asphalt": "#343b40",
    "timber": "#8a6542",
}


def font(size: int, bold: bool = False):
    for name in ("arialbd.ttf" if bold else "arial.ttf", "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def ellipse(center: tuple[float, float], radii: tuple[float, float], resolution: int = 48):
    return affinity.scale(Point(center).buffer(1.0, resolution=resolution), radii[0], radii[1])


def polygon_triangles(geometry) -> list[list[list[float]]]:
    result: list[list[list[float]]] = []
    for part in getattr(geometry, "geoms", [geometry]):
        if part.is_empty or part.area < 0.04:
            continue
        for triangle in triangulate(part):
            if not part.covers(triangle.representative_point()):
                continue
            coords = list(triangle.exterior.coords)[:3]
            result.append([[round(x, 4), round(y, 4)] for x, y in coords])
    return result


def boundary_points(polygon: Polygon, spacing: float, exclusions) -> list[list[float]]:
    inset = polygon.buffer(-0.9)
    boundary = inset.boundary if not inset.is_empty else polygon.boundary
    count = max(1, int(boundary.length // spacing))
    points: list[list[float]] = []
    for index in range(count):
        point = boundary.interpolate((index + 0.35) / count, normalized=True)
        if any(zone.buffer(1.1).contains(point) for zone in exclusions):
            continue
        if all(point.distance(Point(existing)) >= spacing * 0.72 for existing in points):
            points.append([round(point.x, 3), round(point.y, 3)])
    return points


def build_layout(name: str, label: str, parcel: Polygon) -> dict:
    min_x, min_y, max_x, max_y = parcel.bounds
    width, height = max_x - min_x, max_y - min_y
    center_x, center_y = parcel.centroid.x, parcel.centroid.y
    inner = parcel.buffer(-1.25, join_style="round")
    if inner.is_empty:
        inner = parcel

    lawn_center = (center_x - width * 0.07, center_y + height * 0.06)
    lawn = ellipse(lawn_center, (min(width * 0.28, 10.5), min(height * 0.29, 6.8))).intersection(inner)
    play_center = (center_x + width * 0.29, center_y + height * 0.23)
    play = ellipse(play_center, (min(4.2, width * 0.13), min(3.4, height * 0.18))).intersection(inner).difference(lawn)
    planting_a = ellipse((center_x - width * 0.33, center_y - height * 0.25), (min(4.4, width * 0.15), min(3.2, height * 0.17)))
    planting_b = ellipse((center_x + width * 0.34, center_y - height * 0.25), (min(3.7, width * 0.12), min(2.8, height * 0.15)))
    planting = planting_a.union(planting_b).intersection(inner).difference(lawn.union(play))

    pavilion_width, pavilion_height = min(4.6, width * 0.16), min(3.3, height * 0.18)
    pavilion_center = (center_x + width * 0.22, center_y - height * 0.27)
    pavilion = box(
        pavilion_center[0] - pavilion_width / 2,
        pavilion_center[1] - pavilion_height / 2,
        pavilion_center[0] + pavilion_width / 2,
        pavilion_center[1] + pavilion_height / 2,
    ).intersection(inner)

    main_line = LineString([
        (min_x - 1.0, center_y - height * 0.08),
        (center_x - width * 0.16, center_y + height * 0.02),
        (center_x + width * 0.18, center_y - height * 0.02),
        (max_x + 1.0, center_y + height * 0.08),
    ])
    cross_x = center_x + width * 0.08
    cross_line = LineString([(cross_x, min_y - 1.0), (cross_x - width * 0.04, center_y), (cross_x, max_y + 1.0)])
    play_line = LineString([(center_x + width * 0.18, center_y), play_center])
    paths = main_line.buffer(1.15, cap_style="round", join_style="round")
    paths = paths.union(cross_line.buffer(0.9, cap_style="round", join_style="round"))
    paths = paths.union(play_line.buffer(0.75, cap_style="round", join_style="round")).intersection(inner)

    surfaces = {
        "paver": parcel,
        "lawn": lawn.difference(paths),
        "planting": planting.difference(paths),
        "safety": play.difference(paths),
        "asphalt": paths,
        "timber": pavilion.difference(paths),
    }
    trees = boundary_points(parcel, 5.2, [paths, play, pavilion])
    return {
        "id": name,
        "label": label,
        "widthM": round(width, 2),
        "heightM": round(height, 2),
        "areaM2": round(parcel.area, 1),
        "parcel": [[round(x, 4), round(y, 4)] for x, y in list(parcel.exterior.coords)[:-1]],
        "surfaces": {role: polygon_triangles(surface) for role, surface in surfaces.items()},
        "surfaceAreasM2": {role: round(surface.area, 1) for role, surface in surfaces.items()},
        "trees": trees,
        "playCenter": [round(play_center[0], 3), round(play_center[1], 3)],
        "pavilionCenter": [round(pavilion_center[0], 3), round(pavilion_center[1], 3)],
    }


def render_plan(layout: dict, output: Path) -> None:
    size, margin = 720, 54
    image = Image.new("RGB", (size, size), "#eceae4")
    draw = ImageDraw.Draw(image)
    parcel = layout["parcel"]
    xs, ys = [point[0] for point in parcel], [point[1] for point in parcel]
    min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)
    scale = min((size - margin * 2) / max(max_x - min_x, 1), (size - margin * 2) / max(max_y - min_y, 1))

    def project(point):
        x = margin + (point[0] - min_x) * scale + ((size - margin * 2) - (max_x - min_x) * scale) / 2
        y = size - margin - (point[1] - min_y) * scale - ((size - margin * 2) - (max_y - min_y) * scale) / 2
        return x, y

    for role in ("paver", "lawn", "planting", "safety", "asphalt", "timber"):
        for triangle in layout["surfaces"][role]:
            draw.polygon([project(point) for point in triangle], fill=ROLE_COLOURS[role])
    for point in layout["trees"]:
        x, y = project(point)
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill="#274b2f", outline="#172e20", width=2)
    draw.line([project(point) for point in parcel + [parcel[0]]], fill="#13231c", width=5, joint="curve")
    draw.text((28, 22), layout["label"], font=font(28, True), fill="#14231d")
    draw.text((28, 58), f"{layout['widthM']:.0f} × {layout['heightM']:.0f} m · {layout['areaM2']:.0f} m²", font=font(17), fill="#4a5b53")
    image.save(output, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    parcels = (
        ("square", "Compact square parcel", Polygon([(-14, -12), (14, -12), (14, 12), (-14, 12)])),
        ("long", "Long, narrow parcel", Polygon([(-24, -9), (24, -9), (24, 9), (-24, 9)])),
        ("irregular", "Irregular corner parcel", Polygon([(-18, -8), (-10, -12), (7, -11), (18, -4), (14, 10), (2, 13), (-13, 8), (-19, 1)])),
    )
    if args.dry_run:
        for name, label, parcel in parcels:
            print(f"{name}: {label} bounds={parcel.bounds} area={parcel.area:.1f}m2")
        print("planned: 3 parcel shapes, one metric grammar, api_calls=0")
        return
    args.out.mkdir(parents=True, exist_ok=True)
    payload = {"schemaVersion": 1, "method": "metric_semantic_park_grammar", "apiCalls": 0, "layouts": {}}
    for name, label, parcel in parcels:
        layout = build_layout(name, label, parcel)
        payload["layouts"][name] = layout
        render_plan(layout, args.out / f"{name}_plan.png")
    (args.out / "adaptive_layouts.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"wrote {args.out / 'adaptive_layouts.json'}")


if __name__ == "__main__":
    main()
