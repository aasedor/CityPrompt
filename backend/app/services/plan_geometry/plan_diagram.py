"""Conditioning diagram: the drawn plan as an annotation-free flat-color
nadir PNG.

Per the diagram-conditioning research (docs/DIAGRAM_CONDITIONING_RESEARCH
_2026_06_17.md): image models treat a diagram as a soft reference, and it
works best as one flat color per element, no text, no scale bar, no north
arrow, no gradients — embedded characters come back as garbled artifacts.
This diagram is the authoritative-geometry input for renders and the
layout figure in the hearing pack.
"""

from __future__ import annotations

import io
from typing import Any

from PIL import Image, ImageDraw
from shapely.geometry import Polygon

from app.services.site_engine import (
    build_transformer,
    local_metric_crs_for_polygon,
    project_geometry,
)

# Flat Streetmix-style palette — one color per role, white ground. Buildings
# additionally get a thin white outline: abutting same-color bars of a
# perimeter block otherwise merge into one unreadable mass. Courtyards draw
# green like parks (their role is 'courtyard', not 'open_space'; without
# them the block centre reads as unplanned white ground).
DIAGRAM_COLORS = {
    "background": (255, 255, 255),
    "site": (243, 240, 235),        # faint site tint so the boundary reads
    "street": (128, 128, 128),
    "open_space": (124, 179, 66),
    "courtyard": (124, 179, 66),
    "building": (176, 58, 46),
}
ROLE_DRAW_ORDER = ("street", "open_space", "courtyard", "building")
BUILDING_OUTLINE = {"outline": (255, 255, 255), "width": 3}


def render_plan_diagram_png(
    boundary_wgs84: Polygon,
    plan_zones: list[dict[str, Any]],
    size_px: int = 1024,
) -> bytes:
    """Rasterize the plan to a nadir PNG. ``plan_zones`` entries carry
    ``role`` and WGS84 ``coordinates`` (single exterior ring, unclosed) —
    the same shape the plan-sheet endpoint already assembles."""
    crs = local_metric_crs_for_polygon(boundary_wgs84)
    to_metric = build_transformer("EPSG:4326", crs)
    boundary_m = project_geometry(boundary_wgs84, to_metric)

    minx, miny, maxx, maxy = boundary_m.bounds
    span = max(maxx - minx, maxy - miny) or 1.0
    pad = span * 0.04
    minx, miny, span = minx - pad, miny - pad, span + 2 * pad
    scale = size_px / span
    # Height honours the aspect ratio inside the padded square frame.
    height_px = size_px

    def to_px(x_m: float, y_m: float) -> tuple[float, float]:
        return ((x_m - minx) * scale, height_px - (y_m - miny) * scale)

    image = Image.new("RGB", (size_px, height_px), DIAGRAM_COLORS["background"])
    draw = ImageDraw.Draw(image)

    draw.polygon([to_px(x, y) for x, y in boundary_m.exterior.coords], fill=DIAGRAM_COLORS["site"])

    for role in ROLE_DRAW_ORDER:
        for zone in plan_zones:
            if zone.get("role") != role:
                continue
            coords = zone.get("coordinates") or []
            if len(coords) < 3:
                continue
            ring = project_geometry(Polygon(coords), to_metric).exterior.coords
            outline = BUILDING_OUTLINE if role == "building" else {}
            draw.polygon(
                [to_px(x, y) for x, y in ring],
                fill=DIAGRAM_COLORS[role],
                **outline,
            )

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
