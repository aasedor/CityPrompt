"""Connected-network street ground-drape pilot for the live City Prompt project.

The pilot deliberately separates authoritative geometry from generated appearance:

1. fetch the project's current road polygons and metric street recipes;
2. draw one north-up, to-scale semantic atlas for the connected network;
3. ask Gemini and/or GPT Image for surface materials only;
4. hard-clip the returned raster locally to the exact road ROW mask.

Generated images are written outside the source tree by default.  A persistent
call ledger prevents this pilot from exceeding five paid image requests.

Examples:
    python scripts/_pilot_connected_street_drape_ab.py --diagram-only
    python scripts/_pilot_connected_street_drape_ab.py --providers gemini,gpt
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import math
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import httpx
import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import Polygon


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ID = "fc279bd0-8549-4607-811b-59606a2e6534"
DEFAULT_API_BASE = "http://127.0.0.1:8000/api/v1"
DEFAULT_OUT = Path(
    r"C:\Users\andre\OneDrive\Documents\Playground\artifacts"
) / "connected-street-drape-pilot-2026-08-04"
DEFAULT_STYLE_REFERENCE = Path(
    r"C:\Users\andre\OneDrive\Documents\Playground\artifacts"
) / "drape-vs-lego-2026-07-14" / "tex_v2_street_main.png"

CANVAS = 1024
FIT = 0.90
MAX_API_CALLS = 5
METERS_PER_DEG_LAT = 111_320.0
GEMINI_MODEL = "gemini-3.1-flash-image"
OPENAI_MODEL = "gpt-image-2"


def _load_env_value(name: str) -> str | None:
    value = os.environ.get(name)
    if value:
        return value.strip()
    candidates = (
        ROOT / ".env",
        ROOT / "backend" / ".env",
        Path(r"C:\Users\andre\OneDrive\Documents\Playground") / ".env",
        Path(r"C:\Users\andre\OneDrive\Documents\Playground") / "backend" / ".env",
    )
    for env_path in candidates:
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, raw_value = line.split("=", 1)
            if key.strip() == name:
                return raw_value.strip().strip('"').strip("'")
    return None


def _json_write(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True), encoding="utf-8")


def _load_ledger(out_dir: Path) -> dict[str, Any]:
    ledger_path = out_dir / "call_ledger.json"
    if not ledger_path.exists():
        return {"max_calls": MAX_API_CALLS, "attempts": []}
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    ledger.setdefault("max_calls", MAX_API_CALLS)
    ledger.setdefault("attempts", [])
    return ledger


def _reserve_call(out_dir: Path, provider: str, output_name: str) -> int:
    ledger = _load_ledger(out_dir)
    attempts = ledger["attempts"]
    if len(attempts) >= MAX_API_CALLS:
        raise RuntimeError(
            f"Pilot call ceiling reached ({len(attempts)}/{MAX_API_CALLS}); "
            "no request was sent."
        )
    attempt = {
        "number": len(attempts) + 1,
        "provider": provider,
        "output": output_name,
        "requested_at": datetime.now(timezone.utc).isoformat(),
        "status": "requested",
    }
    attempts.append(attempt)
    _json_write(out_dir / "call_ledger.json", ledger)
    return attempt["number"]


def _finish_call(out_dir: Path, call_number: int, status: str, detail: str) -> None:
    ledger = _load_ledger(out_dir)
    for attempt in ledger["attempts"]:
        if attempt.get("number") == call_number:
            attempt["status"] = status
            attempt["detail"] = detail
            attempt["completed_at"] = datetime.now(timezone.utc).isoformat()
            break
    _json_write(out_dir / "call_ledger.json", ledger)


def _fetch_zones(api_base: str, project_id: str) -> list[dict[str, Any]]:
    url = f"{api_base.rstrip('/')}/site-zones/projects/{project_id}/zones"
    response = httpx.get(url, timeout=60.0)
    response.raise_for_status()
    zones = response.json()
    if not isinstance(zones, list):
        raise RuntimeError("Site-zone endpoint did not return a list")
    return zones


def _matches_active_plan(zone: dict[str, Any], boundary_id: str, scenario: str | None) -> bool:
    properties = zone.get("properties") or {}
    if properties.get("_plan_boundary_zone_id") not in (None, boundary_id):
        return False
    if scenario and properties.get("_plan_scenario") not in (None, scenario):
        return False
    return True


def _select_network(zones: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    boundaries = [zone for zone in zones if zone.get("zone_type") == "site_boundary"]
    if not boundaries:
        raise RuntimeError("Project has no site boundary")
    boundary = next((zone for zone in boundaries if zone.get("is_active_boundary")), boundaries[0])
    boundary_id = str(boundary["id"])
    boundary_props = boundary.get("properties") or {}
    scenario = None
    directives = boundary_props.get("_urban_dna_directives")
    if isinstance(directives, dict):
        scenario = directives.get("scenario_id")

    roads = [
        zone
        for zone in zones
        if zone.get("zone_type") == "road"
        and (zone.get("properties") or {}).get("_plan_role") == "street"
        and _matches_active_plan(zone, boundary_id, scenario)
        and len(zone.get("coordinates") or []) >= 3
    ]
    if not roads:
        raise RuntimeError("Active plan has no road polygons")
    roads.sort(key=lambda zone: (zone.get("sort_order") or 0, str(zone.get("id"))))
    return boundary, roads


def _all_points(zones: Iterable[dict[str, Any]]) -> Iterable[tuple[float, float]]:
    for zone in zones:
        for coordinate in zone.get("coordinates") or []:
            if isinstance(coordinate, list) and len(coordinate) >= 2:
                yield float(coordinate[0]), float(coordinate[1])


def _fallback_centerline(zone: dict[str, Any]) -> list[list[float]]:
    ring = zone.get("coordinates") or []
    polygon = Polygon(ring)
    if polygon.is_empty or not polygon.is_valid:
        return []
    rectangle = polygon.minimum_rotated_rectangle
    rect = list(rectangle.exterior.coords)[:4]
    edges: list[tuple[float, tuple[float, float]]] = []
    for index in range(4):
        x0, y0 = rect[index]
        x1, y1 = rect[(index + 1) % 4]
        edges.append((math.hypot(x1 - x0, y1 - y0), (x1 - x0, y1 - y0)))
    _, (dx, dy) = max(edges, key=lambda item: item[0])
    magnitude = math.hypot(dx, dy)
    if magnitude <= 1e-12:
        return []
    ux, uy = dx / magnitude, dy / magnitude
    center = polygon.centroid
    half_length = max(edge[0] for edge in edges) * 0.48
    return [
        [center.x - ux * half_length, center.y - uy * half_length],
        [center.x + ux * half_length, center.y + uy * half_length],
    ]


def _draw_polygon(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], **kwargs: Any) -> None:
    if len(points) >= 3:
        draw.polygon(points, **kwargs)


def _draw_dashed_line(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[float, float]],
    *,
    fill: str,
    width: int,
    dash_px: float,
    gap_px: float,
) -> None:
    for start, end in zip(points, points[1:]):
        x0, y0 = start
        x1, y1 = end
        length = math.hypot(x1 - x0, y1 - y0)
        if length <= 0:
            continue
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        cursor = 0.0
        while cursor < length:
            dash_end = min(length, cursor + dash_px)
            draw.line(
                [
                    (x0 + ux * cursor, y0 + uy * cursor),
                    (x0 + ux * dash_end, y0 + uy * dash_end),
                ],
                fill=fill,
                width=width,
            )
            cursor += dash_px + gap_px


def build_diagram(
    boundary: dict[str, Any],
    roads: list[dict[str, Any]],
    out_dir: Path,
    project_id: str,
) -> dict[str, Any]:
    points = list(_all_points([boundary]))
    if not points:
        points = list(_all_points(roads))
    west = min(point[0] for point in points)
    east = max(point[0] for point in points)
    south = min(point[1] for point in points)
    north = max(point[1] for point in points)
    latitude = (south + north) / 2
    metres_per_deg_lon = METERS_PER_DEG_LAT * math.cos(math.radians(latitude))
    width_m = (east - west) * metres_per_deg_lon
    height_m = (north - south) * METERS_PER_DEG_LAT
    px_per_m = CANVAS * FIT / max(width_m, height_m)
    atlas_width = width_m * px_per_m
    atlas_height = height_m * px_per_m
    x0 = (CANVAS - atlas_width) / 2
    y0 = (CANVAS - atlas_height) / 2

    def to_px(lng: float, lat: float) -> tuple[float, float]:
        return (
            x0 + (lng - west) * metres_per_deg_lon * px_per_m,
            y0 + (north - lat) * METERS_PER_DEG_LAT * px_per_m,
        )

    diagram = Image.new("RGB", (CANVAS, CANVAS), "#e5e1d7")
    draw = ImageDraw.Draw(diagram)
    mask = Image.new("L", (CANVAS, CANVAS), 0)
    mask_draw = ImageDraw.Draw(mask)

    boundary_points = [to_px(*coordinate[:2]) for coordinate in boundary.get("coordinates") or []]
    _draw_polygon(draw, boundary_points, fill="#c8d8b8", outline="#746f66", width=3)

    # Exact full right-of-way footprints form both the diagram substrate and
    # the hard local mask. Overlap is intentional at network nodes.
    for zone in roads:
        row = [to_px(*coordinate[:2]) for coordinate in zone.get("coordinates") or []]
        _draw_polygon(draw, row, fill="#d4d0c5", outline="#3d3e3f")
        _draw_polygon(mask_draw, row, fill=255)

    for zone in roads:
        properties = zone.get("properties") or {}
        role = str(properties.get("street_role") or "local")
        if role == "roundabout":
            row = [to_px(*coordinate[:2]) for coordinate in zone.get("coordinates") or []]
            _draw_polygon(draw, row, fill="#5d6161", outline="#343636")
            if row:
                xs = [point[0] for point in row]
                ys = [point[1] for point in row]
                cx = (min(xs) + max(xs)) / 2
                cy = (min(ys) + max(ys)) / 2
                radius = min(max(xs) - min(xs), max(ys) - min(ys)) * 0.25
                draw.ellipse(
                    [cx - radius, cy - radius, cx + radius, cy + radius],
                    fill="#91aa73",
                    outline="#ece9df",
                    width=max(2, round(px_per_m * 0.5)),
                )
            continue

        centerline = properties.get("plan_centerline")
        if not isinstance(centerline, list) or len(centerline) < 2:
            centerline = _fallback_centerline(zone)
        line_points = [to_px(*coordinate[:2]) for coordinate in centerline]
        if len(line_points) < 2:
            continue

        clear_width = properties.get("clear_width_m")
        if not isinstance(clear_width, (int, float)):
            if role == "path":
                clear_width = min(4.0, float(properties.get("width") or 4.0))
            elif role == "lane":
                clear_width = min(5.5, float(properties.get("width") or 7.0))
            else:
                clear_width = 6.5 if role == "spine" else 6.0
        carriageway_px = max(3, round(float(clear_width) * px_per_m))
        carriageway_fill = "#756f66" if role == "path" else "#5d6161"
        draw.line(line_points, fill=carriageway_fill, width=carriageway_px, joint="curve")

        # These markings communicate hierarchy to the image model. The final
        # application will restore deterministic markings over the material.
        if role == "spine":
            _draw_dashed_line(
                draw,
                line_points,
                fill="#d9b75b",
                width=max(1, round(px_per_m * 0.16)),
                dash_px=max(4, px_per_m * 3.0),
                gap_px=max(3, px_per_m * 2.0),
            )
        elif role == "local":
            _draw_dashed_line(
                draw,
                line_points,
                fill="#eceae4",
                width=max(1, round(px_per_m * 0.12)),
                dash_px=max(3, px_per_m * 2.0),
                gap_px=max(4, px_per_m * 3.0),
            )

    diagram_path = out_dir / "network_diagram.png"
    mask_path = out_dir / "network_mask.png"
    diagram.save(diagram_path)
    mask.save(mask_path)

    source_payload = [
        {
            "id": zone.get("id"),
            "coordinates": zone.get("coordinates"),
            "properties": {
                key: (zone.get("properties") or {}).get(key)
                for key in (
                    "width",
                    "clear_width_m",
                    "street_role",
                    "plan_centerline",
                    "road_archetype_id",
                    "road_selected_variant_id",
                )
            },
        }
        for zone in roads
    ]
    source_hash = hashlib.sha256(
        json.dumps(source_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    meta = {
        "project_id": project_id,
        "boundary_zone_id": boundary.get("id"),
        "road_zone_ids": [zone.get("id") for zone in roads],
        "road_zone_count": len(roads),
        "source_hash": source_hash,
        "bbox": {"west": west, "south": south, "east": east, "north": north},
        "size_m": {"width": round(width_m, 2), "height": round(height_m, 2)},
        "uv_rect": {
            "u0": x0 / CANVAS,
            "v0": (CANVAS - (y0 + atlas_height)) / CANVAS,
            "u1": (x0 + atlas_width) / CANVAS,
            "v1": (CANVAS - y0) / CANVAS,
        },
        "pixels_per_metre": px_per_m,
    }
    _json_write(out_dir / "network_meta.json", meta)
    return meta


def build_prompt(meta: dict[str, Any], has_style_reference: bool) -> str:
    style_clause = (
        "Image 2 is a MATERIAL-QUALITY REFERENCE only. Borrow its restrained Calgary asphalt, "
        "concrete, curb, turf and weathering character, but ignore every line, boundary and layout in it. "
        if has_style_reference
        else ""
    )
    return (
        "Create one photorealistic north-up orthographic MATERIAL ATLAS for the connected street network "
        "shown in Image 1. Image 1 is the immutable, to-scale geometry contract. The site is approximately "
        f"{meta['size_m']['width']:.0f} by {meta['size_m']['height']:.0f} metres and contains "
        f"{meta['road_zone_count']} coordinated street polygons. {style_clause}"
        "Replace only the flat semantic colours with realistic ground surfaces: restrained medium-grey "
        "Calgary asphalt with subtle aggregate and wear, pale cast-in-place concrete sidewalks with correctly "
        "scaled joints, narrow muted turf boulevards, curb-and-gutter bands, and crisp but slightly weathered "
        "road markings. Preserve every roadway footprint, width, tangent, right angle, connection, junction and "
        "the compact roundabout EXACTLY as drawn. Every road must connect continuously through intersections; "
        "there must be no seams, overlapping texture panels, disconnected lanes, invented ramps, channelized "
        "highway turns, added roads, removed roads or shifted curves. The central roundabout must remain the exact "
        "drawn circle with one small landscaped island and a continuous asphalt ring. The pale-green areas are "
        "quiet turf/context only, not new park designs. Keep all building pads empty and flat. Generate GROUND "
        "MATERIALS ONLY: no buildings, roofs, tree canopies, vehicles, people, benches, light poles, signs, "
        "playground equipment, shadows from vertical objects, text, labels, legend or watermark. Camera exactly "
        "straight down at 90-degree nadir, zero perspective, even overcast midday illumination, no directional "
        "shadow. The output must align pixel-for-pixel with Image 1; geometry is not negotiable."
    )


def _gemini_call(
    diagram_path: Path,
    prompt: str,
    output_path: Path,
    api_key: str,
    style_reference: Path | None,
) -> str:
    parts: list[dict[str, Any]] = [
        {"text": "Image 1 (AUTHORITATIVE NETWORK GEOMETRY — preserve pixel-for-pixel):"},
        {
            "inlineData": {
                "mimeType": "image/png",
                "data": base64.b64encode(diagram_path.read_bytes()).decode("ascii"),
            }
        },
    ]
    if style_reference:
        style_image = Image.open(style_reference).convert("RGB")
        style_image.thumbnail((1536, 1536), Image.Resampling.LANCZOS)
        style_buffer = io.BytesIO()
        style_image.save(style_buffer, format="JPEG", quality=88)
        parts.extend(
            [
                {"text": "Image 2 (MATERIAL QUALITY ONLY — ignore its geometry):"},
                {
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": base64.b64encode(style_buffer.getvalue()).decode("ascii"),
                    }
                },
            ]
        )
    parts.append({"text": prompt})
    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "imageConfig": {"aspectRatio": "1:1", "imageSize": "2K"},
        },
    }
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={api_key}"
    )
    response = httpx.post(url, json=payload, timeout=300.0)
    if response.status_code != 200:
        raise RuntimeError(f"Gemini HTTP {response.status_code}: {response.text[:300]}")
    body = response.json()
    candidates = body.get("candidates") or []
    for candidate in candidates:
        for part in (candidate.get("content") or {}).get("parts") or []:
            inline = part.get("inlineData") or {}
            if str(inline.get("mimeType") or "").startswith("image/") and inline.get("data"):
                output_path.write_bytes(base64.b64decode(inline["data"]))
                return f"{output_path.stat().st_size // 1024} KiB"
    raise RuntimeError("Gemini response contained no image")


def _openai_call(
    diagram_path: Path,
    prompt: str,
    output_path: Path,
    api_key: str,
    style_reference: Path | None,
) -> str:
    positional_prompt = (
        "The first attached image is the authoritative network diagram. "
        + (
            "The second attached image is material quality only and must not alter the first image's geometry. "
            if style_reference
            else ""
        )
        + prompt
    )
    files: list[tuple[str, tuple[str, bytes, str]]] = [
        ("image[]", (diagram_path.name, diagram_path.read_bytes(), "image/png"))
    ]
    if style_reference:
        mime = "image/png" if style_reference.suffix.lower() == ".png" else "image/jpeg"
        files.append(("image[]", (style_reference.name, style_reference.read_bytes(), mime)))
    response = httpx.post(
        "https://api.openai.com/v1/images/edits",
        headers={"Authorization": f"Bearer {api_key}"},
        data={
            "model": OPENAI_MODEL,
            "prompt": positional_prompt,
            "n": "1",
            "size": "1024x1024",
            "quality": "high",
            "output_format": "png",
        },
        files=files,
        timeout=420.0,
    )
    if response.status_code != 200:
        raise RuntimeError(f"OpenAI HTTP {response.status_code}: {response.text[:300]}")
    data = response.json().get("data") or []
    if not data:
        raise RuntimeError("OpenAI response contained no image entry")
    image_b64 = data[0].get("b64_json")
    if image_b64:
        output_path.write_bytes(base64.b64decode(image_b64))
    elif data[0].get("url"):
        image_response = httpx.get(data[0]["url"], timeout=120.0)
        image_response.raise_for_status()
        output_path.write_bytes(image_response.content)
    else:
        raise RuntimeError("OpenAI response contained neither image bytes nor URL")
    return f"{output_path.stat().st_size // 1024} KiB"


def _detect_generated_site_bbox(image: Image.Image) -> tuple[int, int, int, int]:
    """Find the model-reframed site rectangle before deterministic rectification.

    Image models frequently preserve topology but expand or inset the diagram's
    letterboxed site frame.  The site is still bounded by strong orthogonal
    transitions, so estimate its four edges from repeated scanline gradients and
    full-row foreground coverage.  This is registration, not generated geometry.
    """
    rgb = np.asarray(image.convert("RGB"), dtype=np.float32)
    height, width = rgb.shape[:2]
    top_sample = rgb[: max(8, height // 20), width // 4 : 3 * width // 4]
    background = np.median(top_sample, axis=(0, 1))
    difference = np.linalg.norm(rgb - background, axis=2)
    foreground = difference > 25.0
    row_coverage = foreground.mean(axis=1)
    content_rows = np.where(row_coverage > 0.45)[0]
    if len(content_rows) < max(20, height // 8):
        return 0, 0, width, height
    y_start = int(content_rows[0])
    y_end = int(content_rows[-1] + 1)

    sample_rows = np.linspace(
        y_start + max(1, (y_end - y_start) // 10),
        y_end - max(2, (y_end - y_start) // 10),
        9,
        dtype=int,
    )
    left_edges: list[int] = []
    right_edges: list[int] = []
    left_limit = max(2, int(width * 0.25))
    right_start = min(width - 2, int(width * 0.75))
    right_end = max(right_start + 1, int(width * 0.99))
    for row_index in sample_rows:
        gradient = np.linalg.norm(np.diff(rgb[row_index], axis=0), axis=1)
        left_edges.append(int(np.argmax(gradient[:left_limit])))
        right_slice = gradient[right_start:right_end]
        right_edges.append(right_start + int(np.argmax(right_slice)))

    x_start = max(0, int(np.median(left_edges)) + 1)
    x_end = min(width, int(np.median(right_edges)) + 1)
    if x_end - x_start < width * 0.6:
        content_columns = np.where(foreground.mean(axis=0) > 0.45)[0]
        if len(content_columns):
            x_start = int(content_columns[0])
            x_end = int(content_columns[-1] + 1)
    return x_start, y_start, x_end, y_end


def rectify_to_authoritative_frame(
    output_path: Path,
    meta: dict[str, Any],
    rectified_path: Path,
) -> Image.Image:
    generated = Image.open(output_path).convert("RGBA")
    source_bbox = _detect_generated_site_bbox(generated)
    source_site = generated.crop(source_bbox)
    uv = meta["uv_rect"]
    target_bbox = (
        round(float(uv["u0"]) * CANVAS),
        round((1.0 - float(uv["v1"])) * CANVAS),
        round(float(uv["u1"]) * CANVAS),
        round((1.0 - float(uv["v0"])) * CANVAS),
    )
    target_width = max(1, target_bbox[2] - target_bbox[0])
    target_height = max(1, target_bbox[3] - target_bbox[1])
    source_site = source_site.resize((target_width, target_height), Image.Resampling.LANCZOS)
    rectified = Image.new("RGBA", (CANVAS, CANVAS), "#e5e1d7")
    rectified.paste(source_site, (target_bbox[0], target_bbox[1]))
    rectified.save(rectified_path)
    return rectified


def hard_clip(
    output_path: Path,
    mask_path: Path,
    meta: dict[str, Any],
    rectified_path: Path,
    clipped_path: Path,
    preview_path: Path,
) -> None:
    generated = rectify_to_authoritative_frame(output_path, meta, rectified_path)
    mask = Image.open(mask_path).convert("L").resize((CANVAS, CANVAS), Image.Resampling.NEAREST)
    clipped = generated.copy()
    clipped.putalpha(mask)
    clipped.save(clipped_path)

    context = Image.new("RGBA", (CANVAS, CANVAS), "#c8d8b8")
    context.alpha_composite(clipped)
    context.convert("RGB").save(preview_path, quality=94)


def create_contact_sheet(out_dir: Path) -> None:
    paths = [out_dir / "network_diagram.png"]
    for provider in ("gemini", "gpt"):
        raw = out_dir / f"street_network_{provider}.png"
        preview = out_dir / f"street_network_{provider}_hardmask_preview.png"
        if raw.exists():
            paths.extend([raw, preview])
    images = [Image.open(path).convert("RGB").resize((512, 512), Image.Resampling.LANCZOS) for path in paths]
    if not images:
        return
    sheet = Image.new("RGB", (512 * len(images), 512), "white")
    for index, image in enumerate(images):
        sheet.paste(image, (index * 512, 0))
    sheet.save(out_dir / "contact_sheet.jpg", quality=92)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", default=PROJECT_ID)
    parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--providers", default="gemini,gpt")
    parser.add_argument("--diagram-only", action="store_true")
    parser.add_argument("--postprocess-only", action="store_true")
    parser.add_argument("--no-style-reference", action="store_true")
    args = parser.parse_args()

    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    zones = _fetch_zones(args.api_base, args.project_id)
    boundary, roads = _select_network(zones)
    meta = build_diagram(boundary, roads, out_dir, args.project_id)
    style_reference = None
    if not args.no_style_reference and DEFAULT_STYLE_REFERENCE.exists():
        style_reference = DEFAULT_STYLE_REFERENCE
    prompt = build_prompt(meta, bool(style_reference))
    (out_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
    print(
        f"diagram: {meta['road_zone_count']} roads, "
        f"{meta['size_m']['width']:.1f} x {meta['size_m']['height']:.1f} m, "
        f"source {meta['source_hash'][:12]}"
    )
    if args.diagram_only:
        print("diagram-only: 0 API calls")
        return

    providers = [provider.strip().lower() for provider in args.providers.split(",") if provider.strip()]
    unknown = [provider for provider in providers if provider not in {"gemini", "gpt"}]
    if unknown:
        raise SystemExit(f"Unknown providers: {', '.join(unknown)}")
    diagram_path = out_dir / "network_diagram.png"
    mask_path = out_dir / "network_mask.png"

    if args.postprocess_only:
        processed = 0
        for provider in providers:
            output_path = out_dir / f"street_network_{provider}.png"
            if not output_path.exists():
                continue
            hard_clip(
                output_path,
                mask_path,
                meta,
                out_dir / f"street_network_{provider}_rectified.png",
                out_dir / f"street_network_{provider}_hardmask.png",
                out_dir / f"street_network_{provider}_hardmask_preview.png",
            )
            processed += 1
        create_contact_sheet(out_dir)
        print(f"postprocess-only: {processed} existing outputs, 0 API calls")
        return

    for provider in providers:
        output_path = out_dir / f"street_network_{provider}.png"
        call_number = _reserve_call(out_dir, provider, output_path.name)
        try:
            if provider == "gemini":
                key = _load_env_value("GEMINI_API_KEY")
                if not key:
                    raise RuntimeError("GEMINI_API_KEY is not configured")
                detail = _gemini_call(diagram_path, prompt, output_path, key, style_reference)
            else:
                key = _load_env_value("OPENAI_API_KEY") or _load_env_value("OPENAI")
                if not key:
                    raise RuntimeError("OPENAI_API_KEY is not configured")
                detail = _openai_call(diagram_path, prompt, output_path, key, style_reference)
            clipped_path = out_dir / f"street_network_{provider}_hardmask.png"
            rectified_path = out_dir / f"street_network_{provider}_rectified.png"
            preview_path = out_dir / f"street_network_{provider}_hardmask_preview.png"
            hard_clip(output_path, mask_path, meta, rectified_path, clipped_path, preview_path)
            _finish_call(out_dir, call_number, "succeeded", detail)
            print(f"call {call_number}/{MAX_API_CALLS} {provider}: OK ({detail})")
        except Exception as exc:
            _finish_call(out_dir, call_number, "failed", f"{type(exc).__name__}: {exc}")
            print(f"call {call_number}/{MAX_API_CALLS} {provider}: FAILED: {exc}", file=sys.stderr)

    create_contact_sheet(out_dir)


if __name__ == "__main__":
    main()
