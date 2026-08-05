"""Generate one metric LEGO park layout with an exact basketball program pad.

This is intentionally a single-parcel pilot. The LEGO grammar owns every
horizontal surface; the authored GLBs own only standing depth assets.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw
from shapely.geometry import LineString, Point, Polygon, box

try:
    from .compile_neighborhood_park_skins import REPO_ROOT
    from .generate_adaptive_park_layouts import (
        ROLE_COLOURS,
        boundary_points,
        ellipse,
        font,
        polygon_triangles,
    )
except ImportError:  # direct script execution
    from compile_neighborhood_park_skins import REPO_ROOT
    from generate_adaptive_park_layouts import (
        ROLE_COLOURS,
        boundary_points,
        ellipse,
        font,
        polygon_triangles,
    )


DEFAULT_OUT = REPO_ROOT / "artifacts/neighborhood-park-lego-depth-pilot/layout"
COURT_ENVELOPE_M = (32.0, 19.0)
PLAYING_COURT_M = (28.0, 15.0)


def build_layout() -> dict:
    parcel = Polygon([(-36, -27), (36, -27), (36, 27), (-36, 27)])
    inner = parcel.buffer(-1.5, join_style="round")
    court_center = (12.0, 1.5)
    court = box(
        court_center[0] - COURT_ENVELOPE_M[0] / 2,
        court_center[1] - COURT_ENVELOPE_M[1] / 2,
        court_center[0] + COURT_ENVELOPE_M[0] / 2,
        court_center[1] + COURT_ENVELOPE_M[1] / 2,
    )
    court_clearance = court.buffer(2.2, join_style="round")

    lawn = ellipse((-17.0, 6.0), (12.0, 11.0)).intersection(inner)
    planting = (
        ellipse((-22.0, -17.0), (8.5, 5.5))
        .union(ellipse((24.0, -17.5), (7.0, 4.2)))
        .union(box(-34.0, 19.0, -4.0, 24.5))
        .intersection(inner)
    )
    pavilion_center = (-15.5, -12.0)
    pavilion = box(-18.2, -14.1, -12.8, -9.9)

    spine = LineString([(-37.0, -3.5), (-10.0, -1.5), (0.0, 0.0), (36.5, -2.0)])
    lawn_loop = Point(-17.0, 6.0).buffer(15.1, resolution=64).boundary
    court_link = LineString([(-1.0, 0.0), (court_center[0] - 16.0, court_center[1])])
    pavilion_link = LineString([(-12.0, -2.0), pavilion_center])
    paths = (
        spine.buffer(1.35, cap_style="round", join_style="round")
        .union(lawn_loop.buffer(1.1, cap_style="round", join_style="round"))
        .union(court_link.buffer(1.0, cap_style="round", join_style="round"))
        .union(pavilion_link.buffer(0.9, cap_style="round", join_style="round"))
        .intersection(inner)
    )

    lawn = lawn.difference(paths)
    planting = planting.difference(paths.union(court_clearance).union(pavilion))
    surfaces = {
        "paver": parcel,
        "lawn": lawn,
        "planting": planting,
        "safety": Polygon(),
        "asphalt": paths,
        "timber": pavilion.difference(paths),
        "court": court,
    }
    trees = boundary_points(parcel, 6.0, [paths, court_clearance, pavilion])
    return {
        "schemaVersion": 1,
        "id": "basketball_neighborhood_park",
        "label": "Neighborhood park + basketball depth kit",
        "method": "lego_surface_plus_metric_program_assets",
        "apiCalls": 0,
        "widthM": 72.0,
        "heightM": 54.0,
        "areaM2": round(parcel.area, 1),
        "parcel": [[x, y] for x, y in list(parcel.exterior.coords)[:-1]],
        "surfaces": {role: polygon_triangles(surface) for role, surface in surfaces.items()},
        "surfaceAreasM2": {role: round(surface.area, 1) for role, surface in surfaces.items()},
        "trees": trees,
        "pavilionCenter": list(pavilion_center),
        "court": {
            "center": list(court_center),
            "rotationDeg": 0,
            "envelopeM": list(COURT_ENVELOPE_M),
            "playingSurfaceM": list(PLAYING_COURT_M),
            "surfaceOwner": "lego_park_grammar",
            "depthOwner": "basketball_program_glbs",
            "metricScale": 1.0,
            "groundContactOriginZM": 0.0,
        },
    }


def render_plan(layout: dict, output: Path) -> None:
    size, margin = 920, 68
    image = Image.new("RGB", (size, 720), "#eceae4")
    draw = ImageDraw.Draw(image)
    parcel = layout["parcel"]
    min_x, max_x = min(p[0] for p in parcel), max(p[0] for p in parcel)
    min_y, max_y = min(p[1] for p in parcel), max(p[1] for p in parcel)
    scale = min((size - margin * 2) / (max_x - min_x), (720 - margin * 2) / (max_y - min_y))

    def project(point):
        return (
            margin + (point[0] - min_x) * scale,
            720 - margin - (point[1] - min_y) * scale,
        )

    colours = {**ROLE_COLOURS, "court": "#276078"}
    for role in ("paver", "lawn", "planting", "asphalt", "timber", "court"):
        for triangle in layout["surfaces"][role]:
            draw.polygon([project(point) for point in triangle], fill=colours[role])
    for point in layout["trees"]:
        x, y = project(point)
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill="#274b2f", outline="#172e20", width=2)
    draw.line([project(point) for point in parcel + [parcel[0]]], fill="#13231c", width=5)
    court = layout["court"]
    cx, cy = project(court["center"])
    court_w = court["playingSurfaceM"][0] * scale
    court_h = court["playingSurfaceM"][1] * scale
    draw.rectangle((cx - court_w / 2, cy - court_h / 2, cx + court_w / 2, cy + court_h / 2), outline="#f2eee4", width=3)
    draw.line((cx, cy - court_h / 2, cx, cy + court_h / 2), fill="#f2eee4", width=2)
    draw.ellipse((cx - 1.8 * scale, cy - 1.8 * scale, cx + 1.8 * scale, cy + 1.8 * scale), outline="#f2eee4", width=2)
    draw.rounded_rectangle((18, 14, 610, 88), radius=10, fill="#eceae4")
    draw.text((28, 22), layout["label"], font=font(28, True), fill="#14231d")
    draw.text((28, 58), "72 x 54 m · exact 32 x 19 m court envelope", font=font(17), fill="#4a5b53")
    image.save(output, optimize=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    layout = build_layout()
    if args.dry_run:
        print(
            f"parcel={layout['widthM']:.0f}x{layout['heightM']:.0f}m "
            f"court={layout['court']['envelopeM']} metric_scale=1 api_calls=0"
        )
        return
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "layout.json").write_text(json.dumps(layout, indent=2), encoding="utf-8")
    render_plan(layout, args.out / "plan.png")
    print(f"wrote {args.out / 'layout.json'}")


if __name__ == "__main__":
    main()
