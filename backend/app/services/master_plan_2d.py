
from __future__ import annotations

import base64
import hashlib
import importlib
import io
import logging
import math
import random
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Literal, Sequence

from geoalchemy2.shape import to_shape
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageOps
from shapely.affinity import translate
from shapely.geometry import GeometryCollection, LineString, MultiPolygon, Point, Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.models import Building, MasterPlan2DOption, Project, SiteZone
from app.schemas.schemas import MasterPlan2DGenerateRequest, MasterPlan3DGenerateRequest
from app.services.master_plan_design_knowledge import build_master_plan_style_guide

logger = logging.getLogger(__name__)
settings = get_settings()


STYLE_LABELS: dict[str, str] = {
    "rendered_sales_plan": "Rendered Sales Plan",
    "hybrid_annotated_master_plan": "Hybrid Annotated Master Plan",
    "illustrative_landscape_plan": "Illustrative Landscape Plan",
}

DEFAULT_STYLE_SEQUENCE = [
    "rendered_sales_plan",
    "hybrid_annotated_master_plan",
    "illustrative_landscape_plan",
]

STABILITY_STYLE_PASS_MODEL = "stable-image-core"
STABILITY_STRUCTURE_MODEL = "stable-image-control-structure"
STABILITY_3D_MODEL = "stable-image-ultra"

MASTER_PLAN_2D_PROVIDER_DEFAULT = "vertex"
MASTER_PLAN_3D_PROVIDER_DEFAULT = "stability"

RENDER_STYLE_MATRIX: dict[str, str] = {
    "photorealistic_aerial": (
        "Render a premium, photorealistic architectural master plan with deep color saturation and vibrant, rich tones. "
        "Direct 90-degree nadir or controlled slight aerial-oblique perspective as appropriate. High-contrast architectural rendering quality. "
        "Apply crisp, high-contrast, nearly pitch-black 45-degree drop shadows with soft ambient occlusion. "
        "Background context must be desaturated to approximately 30 percent so the site reads as the visual priority. "
        "Zero illustrative washes. Opaque materials only. Strong contrast between building roofs, landscape, and corridor surfaces. "
        "Premium developer-presentation quality."
    ),
    "photoreal_orthographic_aerial": (
        "Render a premium orthographic aerial architectural site visualization with realistic roofs, paving, planting texture, parking geometry, and subdued but believable surrounding context. "
        "Maintain a true top-down orthographic camera with crisp site geometry and disciplined roof-plan legibility. "
        "Use cool neutral roof tones, realistic asphalt and sidewalk variation, deep green canopy texture, and clean curb definition. "
        "Shadows should be sharp but natural, with clear edge definition and restrained atmospheric haze. "
        "Surrounding context must remain desaturated and secondary while still reading as a credible aerial environment. "
        "No illustrative washes, no faded diagrammatic treatment, and no presentation-board graphics."
    ),
    "digital_watercolor_map": (
        "A professional, direct overhead 90-degree nadir planimetric illustrative master plan rendered on textured heavyweight digital vellum. "
        "Use a sophisticated, desaturated architectural palette. Opaque, high-fidelity architectural textures with sharp 45-degree 3D drop-shadows. "
        "Clean line-weight hierarchy, elegant paving textures, readable roof plans, and beautiful top-down canopy graphics. "
        "No fading, no ghosting, no transparent washes."
    ),
}

LIGHTING_MATRIX: dict[str, str] = {
    "crisp_summer_day": "Clear daytime lighting. Intense sunlight. Lush deep green tree canopies. Strong contrast. Crisp summer atmosphere.",
    "golden_hour": "Warm sunset golden-hour lighting with long dramatic shadows, rich terracotta warmth, and enhanced depth across roofs, planting, and paving.",
    "overcast_soft": "Soft diffuse overcast lighting with moody atmospheric shadows, realistic reflections where appropriate, and subtle tonal transitions without washing out the site.",
    "winter_snow": "Winter setting with snow-covered roofs, bare trees, frosted ground plane, and soft diffuse winter light. Maintain strong site legibility and contrast despite the snow palette.",
}

TWO_D_NEGATIVE_PROMPT = (
    "text, labels, legend, title, north arrow, scale bar, callouts, reference strip, board layout, collage, presentation board, "
    "faded, washed out, blurry, low contrast, ghosting, transparent overlay, oversoft, simple beige blocks, generic massing, "
    "blank podium bars, posterized, cartoon, warped geometry, unrelated buildings, side-view architecture, elevation view, facade sheet"
)

THREE_D_NEGATIVE_PROMPT = (
    "text, labels, legend, title, scale bar, north arrow, board layout, collage, diagram, washed out, blurry, low contrast, "
    "ghosting, oversoft, generic block massing, unrelated site design, incorrect tower placement, distorted podium, warped geometry, "
    "cartoon, facade sheet, presentation board, floating annotations"
)

STYLE_PASS_NEGATIVE_PROMPT = (
    "side view, facade sheet, elevation, front-facing perspective, collage board, floating annotations, legends, title blocks, north arrow, scale bar"
)

NON_PLAN_VIEW_TOKENS = re.compile(
    r"\b(front[-\s]?facing|front elevation|street[-\s]?level|eye[-\s]?height|perspective|elevation|facade sheet)\b",
    re.IGNORECASE,
)

SANITIZE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (r"\bfront_day\b", "daytime plan reference"),
    (r"\bfront_golden_hour\b", "golden-hour plan reference"),
    (r"\bfront_overcast\b", "overcast plan reference"),
    (r"\bfront_rain_reflection\b", "rain-washed plan reference"),
    (r"\bfront[-\s]?facing\b", "plan-view"),
    (r"\bfront elevation\b", "roof plan reference"),
    (r"\bresidential front elevation\b", "residential roof plan reference"),
    (r"\bstreet[-\s]?level(?:\s+eye[-\s]?height)?\b", "overhead orthographic"),
    (r"\beye[-\s]?height\b", "overhead orthographic"),
    (r"\bperspective\b", "plan reference"),
    (r"\belevation\b", "plan reference"),
    (r"\bfacade sheet\b", "plan reference"),
)

PERSPECTIVE_LEADS: dict[str, str] = {
    "aerial_oblique": "A premium photorealistic architectural 3D rendering from an aerial-oblique perspective.",
    "street_level_eye_height": "A premium photorealistic architectural 3D rendering from a street-level eye-height perspective.",
    "corner_perspective": "A premium photorealistic architectural 3D rendering from a corner-perspective framing.",
    "promenade_view": "A premium photorealistic architectural 3D rendering from a promenade-view camera perspective.",
}

LIGHTING_VARIANTS: dict[str, str] = {
    "golden_hour": "Warm golden-hour lighting with long shadows and cinematic depth.",
    "clear_daylight": "Clear daytime light with high legibility and balanced contrast.",
    "overcast_soft_light": "Soft overcast atmospheric lighting with diffuse shadows.",
    "blue_hour_dusk": "Blue-hour dusk lighting with subtle ambient glow and evening character.",
}

DEFAULT_STYLE_TOGGLES = {
    "show_legend": True,
    "show_north_arrow": True,
    "show_scale_bar": True,
    "show_callout_markers": True,
    "show_surrounding_context": True,
}

STYLE_PALETTES: dict[str, dict[str, str]] = {
    "rendered_sales_plan": {
        "paper": "#f4f1e8",
        "site": "#ecebe7",
        "building": "#f3eee4",
        "shadow": "#7f807a",
        "park": "#b8d3a7",
        "road": "#d5d1c8",
        "path": "#e2d6c3",
        "water": "#a9c8de",
        "accent": "#136f8d",
    },
    "hybrid_annotated_master_plan": {
        "paper": "#f6f4ef",
        "site": "#edece6",
        "building": "#ece6dc",
        "shadow": "#777973",
        "park": "#b7cfab",
        "road": "#d2cec4",
        "path": "#e0d5c4",
        "water": "#abc8dd",
        "accent": "#0a6d8c",
    },
    "illustrative_landscape_plan": {
        "paper": "#f5f0e6",
        "site": "#ebe8df",
        "building": "#f0eadf",
        "shadow": "#8f8a81",
        "park": "#b7cca0",
        "road": "#d4cebf",
        "path": "#e3d6bf",
        "water": "#a4c2d9",
        "accent": "#0f6481",
    },
}


@dataclass(slots=True)
class ZoneSnapshot:
    zone_id: str
    zone_type: str
    name: str
    color: str
    geometry: Polygon
    properties: dict[str, Any]
    sort_order: int = 0
    created_at: datetime | None = None


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_whitespace(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    elif isinstance(value, dict):
        text = " ".join(str(v) for v in value.values() if v not in (None, ""))
    elif isinstance(value, (list, tuple, set)):
        text = ", ".join(str(v) for v in value if v not in (None, ""))
    else:
        text = str(value)
    return re.sub(r"\s+", " ", text).strip()


def _ensure_sentence(value: str | None) -> str:
    text = _normalize_whitespace(value)
    if not text:
        return ""
    return text if text.endswith((".", "!", "?")) else f"{text}."


def _dedupe_sentences(values: Sequence[str | None]) -> str:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = _ensure_sentence(value)
        if not text:
            continue
        key = re.sub(r"[^a-z0-9]+", "", text.lower())
        if not key or key in seen:
            continue
        seen.add(key)
        output.append(text)
    return " ".join(output)


def _normalize_zone_type(zone_type: str | None) -> str:
    token = str(zone_type or "").strip().lower()
    aliases = {
        "residential_area": "residential",
        "residential": "residential",
        "building": "building",
        "road": "road",
        "green_space": "green_space",
        "park": "green_space",
        "plaza": "green_space",
        "parking": "parking",
        "water": "water",
        "development_area": "development_area",
        "infrastructure": "development_area",
        "infrastructure_area": "development_area",
        "barrier": "development_area",
        "site_boundary": "site_boundary",
    }
    return aliases.get(token, "development_area")


def _normalize_provider(value: str | None, *, default: Literal["vertex", "stability", "gemini"]) -> Literal["vertex", "stability", "gemini"]:
    token = str(value or "").strip().lower()
    if token in {"vertex", "stability", "gemini"}:
        return token  # type: ignore[return-value]
    return default


def resolve_render_style_preset(preset: str | None) -> str:
    key = str(preset or "photorealistic_aerial").strip().lower()
    return RENDER_STYLE_MATRIX.get(key, RENDER_STYLE_MATRIX["photorealistic_aerial"])


def resolve_lighting_preset(preset: str | None) -> str:
    key = str(preset or "crisp_summer_day").strip().lower()
    return LIGHTING_MATRIX.get(key, LIGHTING_MATRIX["crisp_summer_day"])


def build_global_style_payload(
    *,
    render_style_preset: str | None,
    lighting_atmosphere_preset: str | None,
    specific_overrides: str | None = None,
    legacy_global_style_notes: str | None = None,
) -> str:
    blocks = [
        resolve_render_style_preset(render_style_preset),
        resolve_lighting_preset(lighting_atmosphere_preset),
    ]
    legacy = _normalize_whitespace(legacy_global_style_notes)
    if legacy:
        blocks.append(f"Legacy Direction: {legacy}")
    override = _normalize_whitespace(specific_overrides)
    if override:
        blocks.append(f"Critical Directive: {override}")
    return "\n\n".join(blocks)


def compile_style_matrix_prompt(
    *,
    render_style_preset: str | None,
    lighting_atmosphere_preset: str | None,
    specific_overrides: str | None = None,
    legacy_global_style_notes: str | None = None,
) -> str:
    return build_global_style_payload(
        render_style_preset=render_style_preset,
        lighting_atmosphere_preset=lighting_atmosphere_preset,
        specific_overrides=specific_overrides,
        legacy_global_style_notes=legacy_global_style_notes,
    )


def _build_2d_negative_prompt() -> str:
    return TWO_D_NEGATIVE_PROMPT


def _build_3d_negative_prompt() -> str:
    return THREE_D_NEGATIVE_PROMPT


def _sanitize_planimetric_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value
    elif isinstance(value, dict):
        text = " ".join(str(v) for v in value.values() if v not in (None, ""))
    elif isinstance(value, (list, tuple, set)):
        text = " ".join(str(v) for v in value if v not in (None, ""))
    else:
        text = str(value)
    text = _normalize_whitespace(text)
    if not text:
        return None
    for pattern, replacement in SANITIZE_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    text = _normalize_whitespace(text)
    return text or None


def _contains_non_plan_view_language(text: str | None) -> bool:
    if not text:
        return False
    return bool(NON_PLAN_VIEW_TOKENS.search(text))


def _sanitize_reference_metadata_bundle(reference_metadata: Sequence[dict[str, Any]] | None) -> list[dict[str, Any]]:
    sanitized: list[dict[str, Any]] = []
    for raw_item in reference_metadata or []:
        item = dict(raw_item or {})
        for field in ("caption", "subcategory", "category", "source_label", "archetype_name"):
            cleaned = _sanitize_planimetric_text(item.get(field))
            if cleaned:
                item[field] = cleaned
            elif field in {"caption", "subcategory"}:
                item[field] = "plan reference"

        tags_value = item.get("tags")
        tags: list[str] = []
        if isinstance(tags_value, (list, tuple, set)):
            for tag in tags_value:
                cleaned = _sanitize_planimetric_text(tag)
                if cleaned:
                    tags.append(cleaned)
        elif isinstance(tags_value, str):
            cleaned = _sanitize_planimetric_text(tags_value)
            if cleaned:
                tags.append(cleaned)
        deduped_tags = []
        seen_tags: set[str] = set()
        for tag in tags:
            key = tag.lower()
            if key in seen_tags:
                continue
            seen_tags.add(key)
            deduped_tags.append(tag)
        item["tags"] = deduped_tags or ["plan reference"]

        prompt_text = _sanitize_planimetric_text(item.get("prompt_text"))
        if _contains_non_plan_view_language(str(raw_item.get("prompt_text") or "")):
            item["prompt_text"] = None
        else:
            item["prompt_text"] = prompt_text

        image_url = item.get("image_url")
        if image_url:
            item["image_url"] = str(image_url)
        sanitized.append(item)
    return sanitized


def _safe_to_shape(value: Any) -> BaseGeometry | None:
    if value is None:
        return None
    if isinstance(value, BaseGeometry):
        return value
    try:
        return to_shape(value)
    except Exception:
        return None


def _polygon_from_geometry(geometry: Any) -> Polygon | None:
    shape = _safe_to_shape(geometry)
    if shape is None or shape.is_empty:
        return None
    if isinstance(shape, Polygon):
        return shape.buffer(0)
    if isinstance(shape, MultiPolygon):
        largest = max(shape.geoms, key=lambda geom: geom.area, default=None)
        if largest is None:
            return None
        return largest.buffer(0)
    if isinstance(shape, GeometryCollection):
        polygons = [geom for geom in shape.geoms if isinstance(geom, Polygon)]
        if not polygons:
            return None
        largest = max(polygons, key=lambda geom: geom.area)
        return largest.buffer(0)
    return None


def _polygon_from_coordinates(polygon: Sequence[Sequence[float]] | None) -> Polygon | None:
    if not polygon or len(polygon) < 4:
        return None
    coords: list[tuple[float, float]] = []
    for pair in polygon:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            return None
        try:
            coords.append((float(pair[0]), float(pair[1])))
        except (TypeError, ValueError):
            return None
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    try:
        shape = Polygon(coords).buffer(0)
    except Exception:
        return None
    if shape.is_empty:
        return None
    if isinstance(shape, Polygon):
        return shape
    if isinstance(shape, MultiPolygon):
        return max(shape.geoms, key=lambda geom: geom.area, default=None)
    return None


def _meters_per_degree_lon(latitude: float) -> float:
    return 111320 * max(math.cos(math.radians(latitude)), 0.15)


def _meters_per_degree_lat(latitude: float) -> float:
    _ = latitude
    return 111132.0


def _geometry_extent_m(geometry: BaseGeometry | None) -> tuple[float, float]:
    shape = _safe_to_shape(geometry)
    if shape is None or shape.is_empty:
        return (0.0, 0.0)
    minx, miny, maxx, maxy = shape.bounds
    center_lat = (miny + maxy) / 2
    width_m = abs(maxx - minx) * _meters_per_degree_lon(center_lat)
    height_m = abs(maxy - miny) * _meters_per_degree_lat(center_lat)
    return (width_m, height_m)

def _scene_geometry_hash(boundary: Polygon, layers: dict[str, list[dict[str, Any]]]) -> str:
    chunks = [boundary.wkt]
    for key in sorted(layers.keys()):
        for item in layers[key]:
            geometry = item.get("geometry")
            shape = _safe_to_shape(geometry)
            if shape is None:
                continue
            chunks.append(f"{key}:{shape.wkt}")
    joined = "|".join(chunks)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:24]


def _project_geometry_to_pixels(boundary: Polygon, width: int, height: int) -> tuple[dict[str, Any], float]:
    minx, miny, maxx, maxy = boundary.bounds
    dx = max(maxx - minx, 1e-9)
    dy = max(maxy - miny, 1e-9)
    margin = max(int(width * 0.05), 40)
    usable_w = max(width - 2 * margin, 10)
    usable_h = max(height - 2 * margin, 10)
    scale = min(usable_w / dx, usable_h / dy)

    def to_px(x: float, y: float) -> tuple[float, float]:
        px = margin + (x - minx) * scale
        py = height - margin - (y - miny) * scale
        return (px, py)

    def geom_to_px(geometry: BaseGeometry) -> BaseGeometry:
        if isinstance(geometry, Polygon):
            exterior = [to_px(x, y) for x, y in geometry.exterior.coords]
            interiors = [[to_px(x, y) for x, y in ring.coords] for ring in geometry.interiors]
            return Polygon(exterior, interiors)
        if isinstance(geometry, MultiPolygon):
            return MultiPolygon([geom_to_px(poly) for poly in geometry.geoms if isinstance(poly, Polygon)])
        if isinstance(geometry, LineString):
            return LineString([to_px(x, y) for x, y in geometry.coords])
        if isinstance(geometry, Point):
            x, y = to_px(geometry.x, geometry.y)
            return Point(x, y)
        return geometry

    center_lat = (miny + maxy) / 2
    px_per_meter = scale / _meters_per_degree_lon(center_lat)
    transform = {
        "minx": minx,
        "miny": miny,
        "maxx": maxx,
        "maxy": maxy,
        "scale": scale,
        "margin": margin,
        "to_px": to_px,
        "geom_to_px": geom_to_px,
    }
    return transform, px_per_meter


def _prepare_scene(payload: dict[str, Any], export_width: int, toggles: dict[str, bool]) -> dict[str, Any]:
    boundary = _polygon_from_geometry(payload.get("boundary"))
    if boundary is None:
        candidate_polygons: list[Polygon] = []
        for key in (
            "building_footprints",
            "building_masses",
            "parks",
            "plazas",
            "water",
            "buildable_zones",
        ):
            for item in payload.get(key, []) or []:
                poly = _polygon_from_geometry(item.get("geometry"))
                if poly is not None and not poly.is_empty:
                    candidate_polygons.append(poly)
        if not candidate_polygons:
            raise ValueError("Master plan scene requires a boundary or at least one polygon feature.")
        boundary = unary_union(candidate_polygons).convex_hull.buffer(0)
        if not isinstance(boundary, Polygon):
            boundary = boundary.envelope

    width = int(max(export_width, 1200))
    height = int(round(width * (2.0 / 3.0)))
    transform, pixels_per_meter = _project_geometry_to_pixels(boundary, width, height)
    geom_to_px = transform["geom_to_px"]

    layer_keys = (
        "building_footprints",
        "building_masses",
        "roads",
        "paths",
        "parks",
        "plazas",
        "water",
        "callouts",
        "context_buildings",
        "context_parks",
        "context_water",
        "context_roads",
        "buildable_zones",
    )
    raw_layers: dict[str, list[dict[str, Any]]] = {key: list(payload.get(key, []) or []) for key in layer_keys}
    pixel_layers: dict[str, list[dict[str, Any]]] = {}
    for key, items in raw_layers.items():
        converted: list[dict[str, Any]] = []
        for item in items:
            geometry = _safe_to_shape(item.get("geometry"))
            if geometry is None or geometry.is_empty:
                continue
            converted_item = dict(item)
            converted_item["geometry"] = geom_to_px(geometry)
            converted.append(converted_item)
        pixel_layers[key] = converted

    pixel_boundary = geom_to_px(boundary)
    geometry_hash = _scene_geometry_hash(boundary, raw_layers)
    prompt_zones = list(payload.get("prompt_zones") or [])
    return {
        "width": width,
        "height": height,
        "boundary": boundary,
        "pixel": {
            "boundary": pixel_boundary,
            **pixel_layers,
        },
        "raw_layers": raw_layers,
        "prompt_zones": prompt_zones,
        "geometry_hash": geometry_hash,
        "pixels_per_meter": pixels_per_meter,
        "toggles": {**DEFAULT_STYLE_TOGGLES, **(toggles or {})},
    }


def _supports_precinct_generation(properties: dict[str, Any]) -> bool:
    if not isinstance(properties, dict) or properties.get("treat_as_single_building") is True:
        return False
    return any(
        properties.get(key)
        for key in (
            "development_type",
            "development_subcategory",
            "development_archetype_label",
            "generation_style_input",
            "generation_style_inputs",
        )
    )


def _should_generate_precinct_for_building_zone(geometry: Polygon, properties: dict[str, Any]) -> bool:
    if not _supports_precinct_generation(properties):
        return False
    width_m, height_m = _geometry_extent_m(geometry)
    max_dim = max(width_m, height_m)
    min_dim = min(width_m, height_m)
    area_m2 = width_m * height_m
    try:
        floors = int(float(properties.get("floors") or properties.get("floor_count") or properties.get("floorCount") or 0))
    except (TypeError, ValueError):
        floors = 0
    return bool(
        area_m2 >= 2800
        or (max_dim >= 60 and min_dim >= 25)
        or (floors >= 6 and area_m2 >= 2000)
    )


def _hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    text = (hex_color or "").strip().lstrip("#")
    if len(text) != 6:
        return (0, 0, 0, alpha)
    try:
        return (int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16), alpha)
    except ValueError:
        return (0, 0, 0, alpha)


def _blend_hex(a: str, b: str, t: float) -> str:
    t = max(0.0, min(1.0, t))
    ar, ag, ab, _ = _hex_to_rgba(a)
    br, bg, bb, _ = _hex_to_rgba(b)
    rr = round(ar + (br - ar) * t)
    rg = round(ag + (bg - ag) * t)
    rb = round(ab + (bb - ab) * t)
    return f"#{rr:02x}{rg:02x}{rb:02x}"


def _apply_palette_bias(
    palette: dict[str, str],
    target: str,
    amount: float,
    *,
    keys: Sequence[str] | None = None,
) -> dict[str, str]:
    updated = dict(palette)
    selected_keys = list(keys) if keys is not None else [key for key in updated.keys() if key != "accent"]
    for key in selected_keys:
        if key in updated and key != "accent":
            updated[key] = _blend_hex(updated[key], target, amount)
    return updated


def _resolve_variant_palette(
    style_preset: str,
    variant_index: int,
    *,
    render_style_preset: str | None = None,
    lighting_atmosphere_preset: str | None = None,
) -> dict[str, str]:
    base = dict(STYLE_PALETTES.get(style_preset, STYLE_PALETTES["rendered_sales_plan"]))
    offset = ((variant_index % 5) - 2) * 0.06
    if offset > 0:
        target = "#ffffff"
        ratio = min(offset, 0.18)
    else:
        target = "#000000"
        ratio = min(abs(offset), 0.16)
    for key, value in list(base.items()):
        if key in {"accent"}:
            continue
        base[key] = _blend_hex(value, target, ratio)

    render_key = str(render_style_preset or "photorealistic_aerial").strip().lower()
    lighting_key = str(lighting_atmosphere_preset or "crisp_summer_day").strip().lower()

    if render_key == "photoreal_orthographic_aerial":
        base["paper"] = _blend_hex(base["paper"], "#edf1ed", 0.42)
        base["site"] = _blend_hex(base["site"], "#dde3dc", 0.58)
        base["building"] = _blend_hex(base["building"], "#c4cbd0", 0.64)
        base["shadow"] = _blend_hex(base["shadow"], "#25303a", 0.48)
        base["park"] = _blend_hex(base["park"], "#6f9157", 0.52)
        base["road"] = _blend_hex(base["road"], "#8d949a", 0.58)
        base["path"] = _blend_hex(base["path"], "#cbc3b4", 0.30)
        base["water"] = _blend_hex(base["water"], "#5c86a1", 0.52)
    elif render_key == "photorealistic_aerial":
        base["paper"] = _blend_hex(base["paper"], "#f1efe9", 0.22)
        base["site"] = _blend_hex(base["site"], "#e3e1d8", 0.32)
        base["building"] = _blend_hex(base["building"], "#d8d4cd", 0.44)
        base["shadow"] = _blend_hex(base["shadow"], "#34383d", 0.30)
        base["park"] = _blend_hex(base["park"], "#7fa15c", 0.38)
        base["road"] = _blend_hex(base["road"], "#b2afa8", 0.20)
        base["water"] = _blend_hex(base["water"], "#6f99b2", 0.28)
    elif render_key == "digital_watercolor_map":
        base = _apply_palette_bias(base, "#f7f3ea", 0.12, keys=["paper", "site", "building", "road", "path"])
        base["park"] = _blend_hex(base["park"], "#98b283", 0.25)
        base["water"] = _blend_hex(base["water"], "#88acc5", 0.18)

    if lighting_key == "golden_hour":
        base = _apply_palette_bias(base, "#e3ad73", 0.12, keys=["site", "building", "road", "path"])
        base["park"] = _blend_hex(base["park"], "#8b9357", 0.16)
        base["shadow"] = _blend_hex(base["shadow"], "#1f1a19", 0.20)
        base["water"] = _blend_hex(base["water"], "#688b9d", 0.14)
    elif lighting_key == "overcast_soft":
        base = _apply_palette_bias(base, "#eef1f3", 0.16, keys=["paper", "site", "building", "road", "path"])
        base["park"] = _blend_hex(base["park"], "#8fa58a", 0.12)
        base["shadow"] = _blend_hex(base["shadow"], "#868b8f", 0.22)
    elif lighting_key == "winter_snow":
        base["paper"] = _blend_hex(base["paper"], "#fbfcfd", 0.55)
        base["site"] = _blend_hex(base["site"], "#f3f5f6", 0.72)
        base["building"] = _blend_hex(base["building"], "#eceff2", 0.68)
        base["park"] = _blend_hex(base["park"], "#cdd5cf", 0.56)
        base["road"] = _blend_hex(base["road"], "#bcc4cb", 0.42)
        base["path"] = _blend_hex(base["path"], "#e9ecef", 0.54)
        base["water"] = _blend_hex(base["water"], "#a7bfd0", 0.30)
        base["shadow"] = _blend_hex(base["shadow"], "#6b7278", 0.20)

    return base


def _make_variant_profile(
    style_preset: str,
    quality_level: str,
    variant_index: int,
    geometry_hash: str,
    *,
    render_style_preset: str | None = None,
    lighting_atmosphere_preset: str | None = None,
) -> dict[str, Any]:
    render_key = str(render_style_preset or "photorealistic_aerial").strip().lower()
    lighting_key = str(lighting_atmosphere_preset or "crisp_summer_day").strip().lower()
    hash_seed = int(hashlib.sha256(f"{geometry_hash}:{style_preset}:{render_key}:{lighting_key}".encode("utf-8")).hexdigest()[:12], 16)
    layout_seed = hash_seed % 1_000_000
    style_seed = (hash_seed + variant_index * 977) % 1_000_000
    quality_boost = {"draft": 0.9, "presentation": 1.0, "board_ready": 1.08}.get(quality_level, 1.0)
    photoreal = render_key in {"photorealistic_aerial", "photoreal_orthographic_aerial"}
    orthographic = render_key == "photoreal_orthographic_aerial"

    shadow_offset = {
        "crisp_summer_day": (7, 8),
        "golden_hour": (12, 11),
        "overcast_soft": (5, 6),
        "winter_snow": (6, 6),
    }.get(lighting_key, (7, 8))
    if orthographic:
        shadow_offset = (max(shadow_offset[0] - 1, 4), max(shadow_offset[1] - 1, 5))

    shadow_blur = {
        "crisp_summer_day": 2.2,
        "golden_hour": 2.8,
        "overcast_soft": 3.1,
        "winter_snow": 2.6,
    }.get(lighting_key, 2.3)
    if orthographic:
        shadow_blur = max(1.7, shadow_blur - 0.35)

    base_texture_points = {
        "draft": 1200,
        "presentation": 1800,
        "board_ready": 2600,
    }.get(quality_level, 1800)
    if photoreal:
        base_texture_points = int(base_texture_points * 1.18)
    if orthographic:
        base_texture_points = int(base_texture_points * 1.10)

    return {
        "seed": style_seed,
        "layout_seed": layout_seed,
        "variant_index": variant_index,
        "tree_pattern": "formal_allee" if style_preset == "illustrative_landscape_plan" else "organic_cluster",
        "tree_size": quality_boost + (variant_index * 0.05),
        "quality_level": quality_level,
        "render_style_preset": render_key,
        "lighting_atmosphere_preset": lighting_key,
        "photoreal_mode": photoreal,
        "orthographic_mode": orthographic,
        "shadow_offset": shadow_offset,
        "tree_shadow_offset": (shadow_offset[0] * 0.55, shadow_offset[1] * 0.55),
        "shadow_blur": shadow_blur,
        "shadow_alpha": 152 if orthographic else 140 if photoreal else 122,
        "context_alpha": 198 if orthographic else 178 if photoreal else 150,
        "roof_detail_alpha": 118 if orthographic else 92 if photoreal else 60,
        "roof_detail_lines": 4 if orthographic else 3 if photoreal else 2,
        "rooftop_unit_count": 4 if orthographic else 3 if photoreal else 2,
        "building_edge_alpha": 92 if orthographic else 72 if photoreal else 48,
        "lane_marking_alpha": 150 if orthographic else 122 if photoreal else 88,
        "lane_marking_width": 2 if orthographic else 1,
        "park_texture_points": 420 if orthographic else 320 if photoreal else 180,
        "tree_shadow_alpha": 88 if orthographic else 72 if photoreal else 52,
        "water_edge_alpha": 122 if orthographic else 100 if photoreal else 70,
        "surface_texture_points": base_texture_points,
        "contrast_boost": 1.10 if orthographic else 1.07 if photoreal else 1.0,
        "color_boost": 1.05 if lighting_key != "overcast_soft" else 0.94,
        "brightness_boost": 1.04 if lighting_key == "winter_snow" else 1.0,
        "sharpness_boost": 1.14 if orthographic else 1.08 if photoreal else 1.0,
        "stability_control_strength": 0.88 if orthographic else 0.0,
        "palette": _resolve_variant_palette(
            style_preset,
            variant_index,
            render_style_preset=render_key,
            lighting_atmosphere_preset=lighting_key,
        ),
    }


def _polygon_coords(geometry: Polygon) -> list[tuple[float, float]]:
    return [(float(x), float(y)) for x, y in geometry.exterior.coords]


def _draw_polygon(draw: ImageDraw.ImageDraw, geometry: Polygon, fill: tuple[int, int, int, int]) -> None:
    draw.polygon(_polygon_coords(geometry), fill=fill)


def _draw_line(
    draw: ImageDraw.ImageDraw,
    geometry: LineString,
    fill: tuple[int, int, int, int],
    *,
    width: int = 2,
) -> None:
    coords = [(float(x), float(y)) for x, y in geometry.coords]
    if len(coords) >= 2:
        draw.line(coords, fill=fill, width=max(int(width), 1), joint="curve")


def _draw_polygon_outline(
    draw: ImageDraw.ImageDraw,
    geometry: Polygon,
    outline: tuple[int, int, int, int],
    *,
    width: int = 1,
) -> None:
    coords = _polygon_coords(geometry)
    if len(coords) >= 2:
        draw.line(coords, fill=outline, width=max(int(width), 1), joint="curve")


def _draw_dashed_line(
    draw: ImageDraw.ImageDraw,
    geometry: LineString,
    fill: tuple[int, int, int, int],
    *,
    width: int = 1,
    dash_px: float = 12.0,
    gap_px: float = 8.0,
) -> None:
    coords = [(float(x), float(y)) for x, y in geometry.coords]
    if len(coords) < 2:
        return
    dash_px = max(float(dash_px), 2.0)
    gap_px = max(float(gap_px), 1.0)
    for (x1, y1), (x2, y2) in zip(coords, coords[1:]):
        segment_length = math.hypot(x2 - x1, y2 - y1)
        if segment_length <= 0.1:
            continue
        ux = (x2 - x1) / segment_length
        uy = (y2 - y1) / segment_length
        progress = 0.0
        while progress < segment_length:
            end = min(progress + dash_px, segment_length)
            start_point = (x1 + ux * progress, y1 + uy * progress)
            end_point = (x1 + ux * end, y1 + uy * end)
            draw.line((start_point, end_point), fill=fill, width=max(int(width), 1), joint="curve")
            progress += dash_px + gap_px


def _tree_points(geometry: Polygon, properties: dict[str, Any], variant: dict[str, Any]) -> list[tuple[float, float, float]]:
    density_level = str(properties.get("tree_density_level") or "").strip().lower()
    density = properties.get("tree_density")
    try:
        density_value = float(density) if density is not None else None
    except (TypeError, ValueError):
        density_value = None
    if density_value is None:
        density_lookup = {"sparse": 0.10, "medium": 0.18, "dense": 0.28}
        density_value = density_lookup.get(density_level, 0.16)

    area = max(geometry.area, 1.0)
    target_count = max(4, int(area * density_value / 140))
    minx, miny, maxx, maxy = geometry.bounds
    width = max(maxx - minx, 1e-6)
    height = max(maxy - miny, 1e-6)
    aspect = width / height
    cols = max(2, int(round(math.sqrt(target_count * aspect))))
    rows = max(2, int(round(target_count / cols)))
    step_x = width / cols
    step_y = height / rows
    rng = random.Random(int(variant.get("layout_seed") or 0) + int(area * 1000))
    size_multiplier = float(variant.get("tree_size") or 1.0)

    points: list[tuple[float, float, float]] = []
    for row in range(rows):
        for col in range(cols):
            if len(points) >= target_count:
                break
            x = minx + (col + 0.5) * step_x + rng.uniform(-0.22, 0.22) * step_x
            y = miny + (row + 0.5) * step_y + rng.uniform(-0.22, 0.22) * step_y
            pt = Point(x, y)
            if not geometry.buffer(1e-9).contains(pt):
                continue
            radius = max(min(step_x, step_y) * 0.28 * size_multiplier, 0.8)
            points.append((x, y, radius))
    return points


def _park_program_geometries(geometry: Polygon, properties: dict[str, Any], variant: dict[str, Any]) -> list[tuple[str, BaseGeometry]]:
    _ = int(variant.get("layout_seed") or 0)
    minx, miny, maxx, maxy = geometry.bounds
    width = maxx - minx
    height = maxy - miny
    margin = min(width, height) * 0.08
    core = geometry.buffer(-margin)
    if core.is_empty or not isinstance(core, Polygon):
        core = geometry
    items: list[tuple[str, BaseGeometry]] = [("lawn", core)]
    description = str(properties.get("description_text") or properties.get("park_typology") or "").lower()
    has_paths = bool(properties.get("has_paths")) or "promenade" in description or "path" in description
    if has_paths:
        center_x = (minx + maxx) / 2
        center_y = (miny + maxy) / 2
        horizontal = LineString([(minx + margin, center_y), (maxx - margin, center_y)]).intersection(geometry)
        vertical = LineString([(center_x, miny + margin), (center_x, maxy - margin)]).intersection(geometry)
        if not horizontal.is_empty:
            items.append(("promenade", horizontal))
        if not vertical.is_empty:
            items.append(("path", vertical))
    if "basin" in description or "fountain" in description:
        basin_size = min(width, height) * 0.12
        basin = box(
            (minx + maxx) / 2 - basin_size,
            (miny + maxy) / 2 - basin_size,
            (minx + maxx) / 2 + basin_size,
            (miny + maxy) / 2 + basin_size,
        ).intersection(geometry)
        if not basin.is_empty:
            items.append(("water_feature", basin))
    return items


def _render_parks(
    image: Image.Image,
    scene: dict[str, Any],
    variant: dict[str, Any],
    palette: dict[str, str],
) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    texture_image = Image.new("RGBA", image.size, (0, 0, 0, 0))
    texture_draw = ImageDraw.Draw(texture_image, "RGBA")
    shadow_image = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_image, "RGBA")

    park_fill = _hex_to_rgba(palette["park"], 255)
    park_texture_dark = _hex_to_rgba(_blend_hex(palette["park"], "#45633a", 0.28), 28)
    park_texture_light = _hex_to_rgba(_blend_hex(palette["park"], "#dce8d0", 0.32), 22)
    path_fill = _hex_to_rgba(palette["path"], 248)
    water_fill = _hex_to_rgba(palette["water"], 232)
    water_edge = _hex_to_rgba(_blend_hex(palette["water"], "#ffffff", 0.42), int(variant.get("water_edge_alpha") or 88))
    canopy_fill = _hex_to_rgba(_blend_hex(palette["park"], "#416640", 0.36), 196)
    canopy_highlight = _hex_to_rgba(_blend_hex(palette["park"], "#c4d6ae", 0.46), 116)
    tree_shadow_fill = _hex_to_rgba(_blend_hex(palette["shadow"], "#000000", 0.28), int(variant.get("tree_shadow_alpha") or 64))
    tree_shadow_offset = variant.get("tree_shadow_offset") or (4.0, 5.0)
    tree_canopies: list[tuple[float, float, float]] = []
    base_seed = int(variant.get("seed") or 0)

    for index, park in enumerate(scene["pixel"]["parks"]):
        geometry = _polygon_from_geometry(park.get("geometry"))
        if geometry is None:
            continue
        _draw_polygon(draw, geometry, park_fill)

        rng = random.Random(base_seed + index * 211 + int(geometry.area))
        minx, miny, maxx, maxy = geometry.bounds
        texture_points = max(24, min(int(variant.get("park_texture_points") or 240), int(geometry.area / 55)))
        attempts = max(texture_points * 5, 80)
        sprinkled = 0
        while attempts > 0 and sprinkled < texture_points:
            attempts -= 1
            x = rng.uniform(minx, maxx)
            y = rng.uniform(miny, maxy)
            if not geometry.buffer(1e-9).contains(Point(x, y)):
                continue
            radius = rng.uniform(0.5, 1.45)
            color = park_texture_dark if rng.random() > 0.42 else park_texture_light
            texture_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
            sprinkled += 1

        for kind, program_geometry in _park_program_geometries(geometry, park.get("properties") or {}, variant):
            if isinstance(program_geometry, Polygon):
                if kind == "water_feature":
                    _draw_polygon(draw, program_geometry, water_fill)
                    _draw_polygon_outline(draw, program_geometry, water_edge, width=1)
                else:
                    _draw_polygon(draw, program_geometry, _hex_to_rgba(_blend_hex(palette["park"], "#cadab7", 0.12), 224))
            elif isinstance(program_geometry, LineString):
                width = 6 if kind == "promenade" else 4
                _draw_line(draw, program_geometry, path_fill, width=width)

        for x, y, radius in _tree_points(geometry, park.get("properties") or {}, variant):
            sx = x + float(tree_shadow_offset[0])
            sy = y + float(tree_shadow_offset[1])
            shadow_radius = radius * 1.14
            shadow_draw.ellipse((sx - shadow_radius, sy - shadow_radius, sx + shadow_radius, sy + shadow_radius), fill=tree_shadow_fill)
            tree_canopies.append((x, y, radius))

    image.alpha_composite(texture_image.filter(ImageFilter.GaussianBlur(radius=0.45)))
    image.alpha_composite(shadow_image.filter(ImageFilter.GaussianBlur(radius=max(float(variant.get("shadow_blur") or 2.0) - 0.8, 1.2))))

    for x, y, radius in tree_canopies:
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=canopy_fill)
        inner_radius = max(radius * 0.56, 0.9)
        draw.ellipse((x - inner_radius, y - inner_radius, x + inner_radius, y + inner_radius), fill=canopy_highlight)


def _render_buildings(
    image: Image.Image,
    scene: dict[str, Any],
    palette: dict[str, str],
    variant: dict[str, Any],
) -> None:
    shadow_image = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_image, "RGBA")

    building_fill = _hex_to_rgba(palette["building"], 255)
    roof_fill = _hex_to_rgba(_blend_hex(palette["building"], "#eef1f3", 0.24 if variant.get("orthographic_mode") else 0.14), 255)
    roof_detail_fill = _hex_to_rgba(_blend_hex(palette["building"], "#79828a", 0.55), int(variant.get("roof_detail_alpha") or 72))
    roof_highlight = _hex_to_rgba(_blend_hex(palette["building"], "#ffffff", 0.58), max(int((variant.get("roof_detail_alpha") or 72) * 0.75), 32))
    roof_unit_fill = _hex_to_rgba(_blend_hex(palette["building"], "#a9b1b7", 0.48), max(int(variant.get("roof_detail_alpha") or 72) + 12, 48))
    building_edge = _hex_to_rgba(_blend_hex(palette["building"], "#7e878d", 0.32), int(variant.get("building_edge_alpha") or 54))
    shadow_fill = _hex_to_rgba(_blend_hex(palette["shadow"], "#000000", 0.35), int(variant.get("shadow_alpha") or 128))
    shadow_offset = variant.get("shadow_offset") or (8, 9)
    shadow_blur = float(variant.get("shadow_blur") or 2.4)
    base_seed = int(variant.get("seed") or 0)

    building_polys: list[Polygon] = []
    for building in scene["pixel"]["building_masses"]:
        geometry = _polygon_from_geometry(building.get("geometry"))
        if geometry is not None:
            building_polys.append(geometry)
    for building in scene["pixel"]["building_footprints"]:
        geometry = _polygon_from_geometry(building.get("geometry"))
        if geometry is not None:
            building_polys.append(geometry)

    for poly in building_polys:
        shifted = translate(poly, xoff=float(shadow_offset[0]), yoff=float(shadow_offset[1]))
        _draw_polygon(shadow_draw, shifted, shadow_fill)

    image.alpha_composite(shadow_image.filter(ImageFilter.GaussianBlur(radius=shadow_blur)))
    draw = ImageDraw.Draw(image, "RGBA")

    for index, poly in enumerate(building_polys):
        _draw_polygon(draw, poly, building_fill)
        _draw_polygon_outline(draw, poly, building_edge, width=1)
        inset = _polygon_from_geometry(poly.buffer(-3.0))
        if inset is None:
            continue
        _draw_polygon(draw, inset, roof_fill)
        _draw_polygon_outline(draw, inset, roof_highlight, width=1)

        minx, miny, maxx, maxy = inset.bounds
        spanx = max(maxx - minx, 1.0)
        spany = max(maxy - miny, 1.0)
        if spanx < 14 or spany < 14:
            continue

        line_count = max(1, min(int(variant.get("roof_detail_lines") or 2), int(max(spanx, spany) / 24)))
        for line_index in range(1, line_count + 1):
            t = line_index / (line_count + 1)
            if spanx >= spany:
                guide = LineString([(minx + 3.0, miny + spany * t), (maxx - 3.0, miny + spany * t)])
            else:
                guide = LineString([(minx + spanx * t, miny + 3.0), (minx + spanx * t, maxy - 3.0)])
            detail_line = guide.intersection(inset)
            if isinstance(detail_line, LineString) and not detail_line.is_empty:
                _draw_line(draw, detail_line, roof_detail_fill, width=1)

        rng = random.Random(base_seed + index * 173 + int(poly.area))
        max_units = min(int(variant.get("rooftop_unit_count") or 2), max(1, int((spanx * spany) / 1600)))
        for _ in range(max_units):
            unit_w = max(6.0, min(spanx * (0.12 + rng.random() * 0.06), spanx * 0.28))
            unit_h = max(5.0, min(spany * (0.10 + rng.random() * 0.06), spany * 0.24))
            available_w = max(spanx - unit_w - 8.0, 1.0)
            available_h = max(spany - unit_h - 8.0, 1.0)
            x0 = minx + 4.0 + rng.random() * available_w
            y0 = miny + 4.0 + rng.random() * available_h
            equipment = _polygon_from_geometry(box(x0, y0, x0 + unit_w, y0 + unit_h).intersection(inset))
            if equipment is None:
                continue
            _draw_polygon(draw, equipment, roof_unit_fill)
            _draw_polygon_outline(draw, equipment, roof_detail_fill, width=1)


def _render_streets_and_context(
    image: Image.Image,
    scene: dict[str, Any],
    palette: dict[str, str],
    toggles: dict[str, bool],
    variant: dict[str, Any],
) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    road_fill = _hex_to_rgba(palette["road"], 255)
    road_edge = _hex_to_rgba(_blend_hex(palette["road"], "#747b80", 0.32), 158)
    lane_fill = _hex_to_rgba(_blend_hex(palette["road"], "#ffffff", 0.78), int(variant.get("lane_marking_alpha") or 108))
    path_fill = _hex_to_rgba(palette["path"], 248)
    path_edge = _hex_to_rgba(_blend_hex(palette["path"], "#c2b7a4", 0.28), 130)
    water_fill = _hex_to_rgba(palette["water"], 238)
    water_edge = _hex_to_rgba(_blend_hex(palette["water"], "#ffffff", 0.42), int(variant.get("water_edge_alpha") or 80))
    context_alpha = int(variant.get("context_alpha") or 170)
    context_fill = _hex_to_rgba(_blend_hex(palette["road"], "#ffffff", 0.42), context_alpha)
    context_building_fill = _hex_to_rgba(_blend_hex(palette["building"], "#ffffff", 0.26), max(context_alpha - 20, 96))
    context_park_fill = _hex_to_rgba(_blend_hex(palette["park"], "#dfe8d8", 0.22), max(context_alpha - 40, 84))
    context_water_fill = _hex_to_rgba(_blend_hex(palette["water"], "#c8dae7", 0.22), max(context_alpha - 24, 92))
    plaza_fill = _hex_to_rgba(_blend_hex(palette["path"], "#ffffff", 0.12), 250)
    plaza_edge = _hex_to_rgba(_blend_hex(palette["path"], "#c9bea9", 0.30), 104)

    if toggles.get("show_surrounding_context", True):
        for feature in scene["pixel"]["context_roads"]:
            geometry = feature.get("geometry")
            if isinstance(geometry, LineString):
                _draw_line(draw, geometry, context_fill, width=2)
            else:
                poly = _polygon_from_geometry(geometry)
                if poly is not None:
                    _draw_polygon(draw, poly, context_fill)
        for feature in scene["pixel"]["context_buildings"]:
            poly = _polygon_from_geometry(feature.get("geometry"))
            if poly is not None:
                _draw_polygon(draw, poly, context_building_fill)
        for feature in scene["pixel"]["context_parks"]:
            poly = _polygon_from_geometry(feature.get("geometry"))
            if poly is not None:
                _draw_polygon(draw, poly, context_park_fill)
        for feature in scene["pixel"]["context_water"]:
            poly = _polygon_from_geometry(feature.get("geometry"))
            if poly is not None:
                _draw_polygon(draw, poly, context_water_fill)

    for feature in scene["pixel"]["roads"]:
        geometry = feature.get("geometry")
        if isinstance(geometry, LineString):
            width = int(max(round(float(feature.get("width_m", 8.0)) * scene["pixels_per_meter"]), 3))
            _draw_line(draw, geometry, road_edge, width=width + 2)
            _draw_line(draw, geometry, road_fill, width=width)
            if width >= 10:
                _draw_dashed_line(
                    draw,
                    geometry,
                    lane_fill,
                    width=max(int(variant.get("lane_marking_width") or 1), 1),
                    dash_px=max(width * 0.78, 12),
                    gap_px=max(width * 0.52, 8),
                )
        else:
            poly = _polygon_from_geometry(geometry)
            if poly is not None:
                _draw_polygon(draw, poly, road_fill)
                _draw_polygon_outline(draw, poly, road_edge, width=1)

    for feature in scene["pixel"]["paths"]:
        geometry = feature.get("geometry")
        if isinstance(geometry, LineString):
            width = int(max(round(float(feature.get("width_m", 4.0)) * scene["pixels_per_meter"]), 2))
            _draw_line(draw, geometry, path_edge, width=width + 1)
            _draw_line(draw, geometry, path_fill, width=width)
        else:
            poly = _polygon_from_geometry(geometry)
            if poly is not None:
                _draw_polygon(draw, poly, path_fill)
                _draw_polygon_outline(draw, poly, path_edge, width=1)

    for feature in scene["pixel"]["plazas"]:
        poly = _polygon_from_geometry(feature.get("geometry"))
        if poly is not None:
            _draw_polygon(draw, poly, plaza_fill)
            _draw_polygon_outline(draw, poly, plaza_edge, width=1)

    for feature in scene["pixel"]["water"]:
        poly = _polygon_from_geometry(feature.get("geometry"))
        if poly is not None:
            _draw_polygon(draw, poly, water_fill)
            _draw_polygon_outline(draw, poly, water_edge, width=1)



def _feature_height_m(feature: dict[str, Any]) -> float:
    properties = feature.get('properties') if isinstance(feature.get('properties'), dict) else {}
    for key in ('height_m', 'height'):
        try:
            value = float(properties.get(key))
        except (TypeError, ValueError):
            continue
        if value > 0:
            return value
    for key in ('floors', 'floor_count', 'floorCount'):
        try:
            floors = int(float(properties.get(key)))
        except (TypeError, ValueError):
            continue
        if floors > 0:
            return float(floors) * 3.2
    return 18.0


def _render_control_maps(
    scene: dict[str, Any],
    variant: dict[str, Any],
    toggles: dict[str, bool],
    *,
    base_image: Image.Image | None = None,
) -> dict[str, Image.Image]:
    width = int(scene['width'])
    height = int(scene['height'])
    boundary = _polygon_from_geometry(scene['pixel']['boundary'])
    if boundary is None:
        raise ValueError('Scene boundary is missing in control-map render payload.')

    massing = Image.new('RGBA', (width, height), (22, 24, 28, 255))
    depth = Image.new('L', (width, height), 16)
    segmentation = Image.new('RGBA', (width, height), (18, 20, 22, 255))

    massing_draw = ImageDraw.Draw(massing, 'RGBA')
    depth_draw = ImageDraw.Draw(depth)
    segmentation_draw = ImageDraw.Draw(segmentation, 'RGBA')

    boundary_coords = _polygon_coords(boundary)
    massing_draw.polygon(boundary_coords, fill=(224, 228, 223, 255))
    depth_draw.polygon(boundary_coords, fill=34)
    segmentation_draw.polygon(boundary_coords, fill=(48, 50, 56, 255))

    if toggles.get('show_surrounding_context', True):
        for feature in scene['pixel']['context_roads']:
            geometry = feature.get('geometry')
            if isinstance(geometry, LineString):
                _draw_line(massing_draw, geometry, (60, 64, 70, 180), width=2)
        for feature in scene['pixel']['context_buildings']:
            poly = _polygon_from_geometry(feature.get('geometry'))
            if poly is not None:
                _draw_polygon(massing_draw, poly, (96, 100, 108, 144))

    for feature in scene['pixel']['roads']:
        geometry = feature.get('geometry')
        width_px = int(max(round(float(feature.get('width_m', 8.0)) * scene['pixels_per_meter']), 3))
        if isinstance(geometry, LineString):
            _draw_line(massing_draw, geometry, (112, 116, 122, 255), width=width_px)
            _draw_line(massing_draw, geometry, (142, 146, 152, 140), width=max(width_px - 2, 1))
            _draw_line(depth_draw, geometry, 48, width=width_px)
            _draw_line(segmentation_draw, geometry, (76, 104, 182, 255), width=width_px)
        else:
            poly = _polygon_from_geometry(geometry)
            if poly is not None:
                _draw_polygon(massing_draw, poly, (112, 116, 122, 255))
                _draw_polygon(depth_draw, poly, 48)
                _draw_polygon(segmentation_draw, poly, (76, 104, 182, 255))

    for feature in scene['pixel']['paths']:
        geometry = feature.get('geometry')
        width_px = int(max(round(float(feature.get('width_m', 4.0)) * scene['pixels_per_meter']), 2))
        if isinstance(geometry, LineString):
            _draw_line(massing_draw, geometry, (190, 182, 164, 255), width=width_px)
            _draw_line(depth_draw, geometry, 62, width=width_px)
            _draw_line(segmentation_draw, geometry, (214, 182, 122, 255), width=width_px)
        else:
            poly = _polygon_from_geometry(geometry)
            if poly is not None:
                _draw_polygon(massing_draw, poly, (190, 182, 164, 255))
                _draw_polygon(depth_draw, poly, 62)
                _draw_polygon(segmentation_draw, poly, (214, 182, 122, 255))

    for feature in scene['pixel']['plazas']:
        poly = _polygon_from_geometry(feature.get('geometry'))
        if poly is not None:
            _draw_polygon(massing_draw, poly, (204, 196, 176, 255))
            _draw_polygon(depth_draw, poly, 70)
            _draw_polygon(segmentation_draw, poly, (224, 196, 132, 255))

    for feature in scene['pixel']['parks']:
        poly = _polygon_from_geometry(feature.get('geometry'))
        if poly is not None:
            _draw_polygon(massing_draw, poly, (108, 140, 88, 255))
            _draw_polygon(depth_draw, poly, 82)
            _draw_polygon(segmentation_draw, poly, (72, 156, 92, 255))

    for feature in scene['pixel']['water']:
        poly = _polygon_from_geometry(feature.get('geometry'))
        if poly is not None:
            _draw_polygon(massing_draw, poly, (78, 108, 132, 255))
            _draw_polygon(depth_draw, poly, 92)
            _draw_polygon(segmentation_draw, poly, (66, 128, 196, 255))

    building_features = list(scene['pixel']['building_masses']) + list(scene['pixel']['building_footprints'])
    building_heights = [_feature_height_m(feature) for feature in building_features]
    max_height = max(building_heights, default=24.0)
    shadow_image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_image, 'RGBA')
    shadow_offset = variant.get('shadow_offset') or (7, 8)

    for feature in building_features:
        poly = _polygon_from_geometry(feature.get('geometry'))
        if poly is None:
            continue
        shifted = translate(poly, xoff=float(shadow_offset[0]) * 0.62, yoff=float(shadow_offset[1]) * 0.62)
        _draw_polygon(shadow_draw, shifted, (12, 14, 18, 118))

    massing.alpha_composite(shadow_image.filter(ImageFilter.GaussianBlur(radius=max(float(variant.get('shadow_blur') or 2.0) * 0.7, 1.2))))

    for feature, height_m in zip(building_features, building_heights):
        poly = _polygon_from_geometry(feature.get('geometry'))
        if poly is None:
            continue
        normalized = max(0.0, min(height_m / max(max_height, 1.0), 1.0))
        tone = int(164 + normalized * 72)
        depth_value = int(118 + normalized * 120)
        _draw_polygon(massing_draw, poly, (tone, tone + 4, tone + 8, 255))
        _draw_polygon_outline(massing_draw, poly, (238, 242, 244, 210), width=1)
        _draw_polygon(depth_draw, poly, depth_value)
        _draw_polygon_outline(segmentation_draw, poly, (255, 244, 236, 255), width=2)
        _draw_polygon(segmentation_draw, poly, (214, 98, 78, 255))

    if base_image is not None:
        structure = Image.blend(base_image.convert('RGBA'), massing, 0.44)
    else:
        structure = massing.copy()
    depth_rgb = Image.merge('RGBA', (depth, depth, depth, Image.new('L', (width, height), 255)))
    structure = Image.blend(structure, depth_rgb, 0.16)

    structure_overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(structure_overlay, 'RGBA')
    overlay_draw.line(boundary_coords, fill=(255, 255, 255, 160), width=2, joint='curve')
    for feature in building_features:
        poly = _polygon_from_geometry(feature.get('geometry'))
        if poly is not None:
            _draw_polygon_outline(overlay_draw, poly, (255, 255, 255, 140), width=1)
    structure.alpha_composite(structure_overlay)

    return {
        'massing': massing,
        'depth': depth,
        'segmentation': segmentation,
        'structure': structure,
    }
def _image_from_data_uri(data_uri: str | None) -> Image.Image | None:
    text = _normalize_whitespace(data_uri)
    if not text or not text.startswith("data:image") or "," not in text:
        return None
    try:
        _, encoded = text.split(",", 1)
        return Image.open(io.BytesIO(base64.b64decode(encoded))).convert("RGBA")
    except Exception:
        logger.warning("Failed to decode master-plan context image data URI.", exc_info=True)
        return None


def _fetch_mapbox_satellite_underlay(boundary: Polygon, width: int, height: int) -> tuple[Image.Image | None, str | None]:
    if not settings.mapbox_access_token:
        return None, "MAPBOX_ACCESS_TOKEN not configured"
    try:
        httpx = importlib.import_module("httpx")
    except Exception as exc:
        return None, f"mapbox http client unavailable: {exc}"

    minx, miny, maxx, maxy = boundary.bounds
    center_lng = (minx + maxx) / 2
    center_lat = (miny + maxy) / 2
    width_m = max((maxx - minx) * _meters_per_degree_lon(center_lat), 120.0)
    height_m = max((maxy - miny) * _meters_per_degree_lat(center_lat), 120.0)
    coverage_width_m = width_m * 3.2
    coverage_height_m = height_m * 3.2
    css_width = min(1280, max(640, width))
    css_height = min(1280, max(480, height))
    cos_lat = max(math.cos(math.radians(center_lat)), 0.15)
    meters_per_css_px = max(coverage_width_m / css_width, coverage_height_m / css_height, 0.3)
    zoom = math.log2((78271.51696402048 * cos_lat) / meters_per_css_px)
    zoom = max(10.0, min(20.5, zoom))
    url = (
        f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
        f"{center_lng:.6f},{center_lat:.6f},{zoom:.4f},0/{css_width}x{css_height}@2x"
        f"?access_token={settings.mapbox_access_token}"
    )
    try:
        response = httpx.get(url, timeout=25.0)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert("RGBA"), None
    except Exception as exc:
        return None, f"Mapbox static underlay failed: {exc}"


def _resolve_context_underlay(
    scene: dict[str, Any],
    *,
    render_style_preset: str | None,
    map_screenshot_satellite: str | None,
) -> tuple[Image.Image | None, dict[str, Any]]:
    render_key = str(render_style_preset or "").strip().lower()
    wants_underlay = render_key in {"photorealistic_aerial", "photoreal_orthographic_aerial"}
    status = {
        "requested": wants_underlay or bool(_normalize_whitespace(map_screenshot_satellite)),
        "applied": False,
        "source": None,
        "reason": None,
    }

    screenshot_image = _image_from_data_uri(map_screenshot_satellite)
    if screenshot_image is not None:
        status.update({"applied": True, "source": "viewer_map_screenshot", "reason": None})
        return screenshot_image, status

    if not wants_underlay:
        status["reason"] = "render preset does not request a real aerial context underlay"
        return None, status

    boundary = _polygon_from_geometry(scene.get("boundary"))
    if boundary is None:
        status["reason"] = "scene boundary unavailable for context underlay"
        return None, status

    fetched, error = _fetch_mapbox_satellite_underlay(boundary, int(scene["width"]), int(scene["height"]))
    if fetched is None:
        status["reason"] = error or "context underlay unavailable"
        return None, status

    status.update({"applied": True, "source": "mapbox_static", "reason": None})
    return fetched, status


def _render_plan_image(
    scene: dict[str, Any],
    *,
    style_preset: str,
    variant: dict[str, Any],
    toggles: dict[str, bool],
    context_underlay: Image.Image | None = None,
) -> Image.Image:
    _ = style_preset
    width = int(scene["width"])
    height = int(scene["height"])
    palette = variant["palette"]
    underlay_active = context_underlay is not None

    if underlay_active:
        canvas = ImageOps.fit(context_underlay.convert("RGB"), (width, height), method=Image.Resampling.LANCZOS).convert("RGBA")
        canvas = ImageEnhance.Contrast(canvas).enhance(1.05 if variant.get("orthographic_mode") else 1.03)
        canvas = ImageEnhance.Color(canvas).enhance(1.04)
        canvas = ImageEnhance.Sharpness(canvas).enhance(1.10 if variant.get("orthographic_mode") else 1.04)
        atmosphere_wash = Image.new("RGBA", (width, height), _hex_to_rgba(_blend_hex(palette["paper"], "#eef2ee", 0.35), 42))
        canvas.alpha_composite(atmosphere_wash)
    else:
        canvas = Image.new("RGBA", (width, height), _hex_to_rgba(palette["paper"], 255))
        draw = ImageDraw.Draw(canvas, "RGBA")
        draw.rectangle((0, 0, width, height), fill=_hex_to_rgba(palette["paper"], 255))

    draw = ImageDraw.Draw(canvas, "RGBA")
    boundary = _polygon_from_geometry(scene["pixel"]["boundary"])
    if boundary is None:
        raise ValueError("Scene boundary is missing in pixel-space render payload.")
    site_alpha = 118 if underlay_active else 255
    _draw_polygon(draw, boundary, _hex_to_rgba(palette["site"], site_alpha))
    if underlay_active:
        _draw_polygon_outline(draw, boundary, _hex_to_rgba(_blend_hex(palette["paper"], "#ffffff", 0.70), 120), width=2)

    clip_mask = Image.new("L", (width, height), 0)
    clip_draw = ImageDraw.Draw(clip_mask)
    clip_draw.polygon(_polygon_coords(boundary), fill=255)

    clipped = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    context_toggles = dict(toggles)
    if underlay_active:
        context_toggles["show_surrounding_context"] = False
    _render_streets_and_context(clipped, scene, palette, context_toggles, variant)
    _render_parks(clipped, scene, variant, palette)
    _render_buildings(clipped, scene, palette, variant)

    canvas = Image.composite(clipped, canvas, clip_mask)

    noise_seed = int(variant["seed"])
    rng = random.Random(noise_seed)
    if variant["quality_level"] != "draft" and not underlay_active:
        texture = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        texture_draw = ImageDraw.Draw(texture, "RGBA")
        dots = int(variant.get("surface_texture_points") or 1600)
        light_tint = _hex_to_rgba("#ffffff", 0)
        dark_tint = _hex_to_rgba(_blend_hex(palette["paper"], "#000000", 0.18), 0)
        for _ in range(dots):
            x = rng.randint(0, width - 1)
            y = rng.randint(0, height - 1)
            if rng.random() > 0.55:
                alpha = rng.randint(5, 14)
                fill = (light_tint[0], light_tint[1], light_tint[2], alpha)
            else:
                alpha = rng.randint(4, 10)
                fill = (dark_tint[0], dark_tint[1], dark_tint[2], alpha)
            texture_draw.point((x, y), fill=fill)
        canvas.alpha_composite(texture.filter(ImageFilter.GaussianBlur(radius=0.35)))

    brightness_boost = float(variant.get("brightness_boost") or 1.0)
    contrast_boost = float(variant.get("contrast_boost") or 1.0)
    color_boost = float(variant.get("color_boost") or 1.0)
    sharpness_boost = float(variant.get("sharpness_boost") or 1.0)
    if brightness_boost != 1.0:
        canvas = ImageEnhance.Brightness(canvas).enhance(brightness_boost)
    if contrast_boost != 1.0:
        canvas = ImageEnhance.Contrast(canvas).enhance(contrast_boost)
    if color_boost != 1.0:
        canvas = ImageEnhance.Color(canvas).enhance(color_boost)
    if sharpness_boost != 1.0:
        canvas = ImageEnhance.Sharpness(canvas).enhance(sharpness_boost)
    return canvas


def _svg_path_from_polygon(poly: Polygon) -> str:
    coords = list(poly.exterior.coords)
    if not coords:
        return ""
    parts = [f"M {coords[0][0]:.2f} {coords[0][1]:.2f}"]
    for x, y in coords[1:]:
        parts.append(f"L {x:.2f} {y:.2f}")
    parts.append("Z")
    return " ".join(parts)


def _polygon_path_from_feature(feature: dict[str, Any], default_width: float = 3.0) -> tuple[str, Polygon | None]:
    geometry = _safe_to_shape(feature.get("geometry"))
    if geometry is None:
        return "", None
    if isinstance(geometry, Polygon):
        return _svg_path_from_polygon(geometry), geometry
    if isinstance(geometry, MultiPolygon):
        poly = max(geometry.geoms, key=lambda geom: geom.area, default=None)
        if poly is None:
            return "", None
        return _svg_path_from_polygon(poly), poly
    if isinstance(geometry, LineString):
        width = float(feature.get("width_m") or default_width)
        buffered = geometry.buffer(max(width, 1.0) * 0.5, cap_style=2, join_style=2)
        poly = _polygon_from_geometry(buffered)
        if poly is None:
            return "", None
        return _svg_path_from_polygon(poly), poly
    return "", None


def _render_plan_svg(scene: dict[str, Any], style_preset: str, variant: dict[str, Any], toggles: dict[str, bool]) -> str:
    _ = style_preset
    width = int(scene["width"])
    height = int(scene["height"])
    boundary = _polygon_from_geometry(scene["pixel"]["boundary"])
    if boundary is None:
        raise ValueError("Scene boundary is missing while constructing SVG.")
    boundary_path = _svg_path_from_polygon(boundary)
    palette = variant["palette"]

    geometry_paths: list[str] = []

    def push_path(layer: str, color_key: str, opacity: float = 1.0, default_width: float = 3.0) -> None:
        color = palette[color_key]
        for feature in scene["pixel"][layer]:
            path_data, _ = _polygon_path_from_feature(feature, default_width=default_width)
            if not path_data:
                continue
            geometry_paths.append(f'<path d="{path_data}" fill="{color}" fill-opacity="{opacity:.3f}" />')

    push_path("roads", "road", 1.0, default_width=8.0)
    push_path("paths", "path", 0.96, default_width=4.0)
    push_path("parks", "park", 1.0)
    push_path("plazas", "path", 0.95)
    push_path("water", "water", 0.95)
    push_path("building_masses", "building", 1.0)
    push_path("building_footprints", "building", 1.0)

    if toggles.get("show_surrounding_context", True):
        for layer, color in (
            ("context_roads", _blend_hex(palette["road"], "#ffffff", 0.35)),
            ("context_buildings", "#d7d6d1"),
            ("context_parks", "#c4d5bf"),
            ("context_water", "#b8cfe1"),
        ):
            for feature in scene["pixel"][layer]:
                path_data, _ = _polygon_path_from_feature(feature, default_width=2.0)
                if not path_data:
                    continue
                geometry_paths.insert(0, f'<path d="{path_data}" fill="{color}" fill-opacity="0.75" />')

    geometry_markup = "".join(geometry_paths)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'<defs><clipPath id="siteClip"><path d="{boundary_path}" /></clipPath></defs>'
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{palette["paper"]}" />'
        f'<path d="{boundary_path}" fill="{palette["site"]}" />'
        f'<g id="geometry-layer" clip-path="url(#siteClip)">{geometry_markup}</g>'
        "</svg>"
    )


def _image_to_png_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG", optimize=True)
    return buffer.getvalue()


def _png_data_uri(image_bytes: bytes) -> str:
    return "data:image/png;base64," + base64.b64encode(image_bytes).decode("ascii")


def _svg_data_uri(svg: str) -> str:
    encoded = base64.b64encode(svg.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _preview_png(image: Image.Image, target_width: int = 1600) -> bytes:
    if image.width <= target_width:
        return _image_to_png_bytes(image)
    ratio = target_width / image.width
    resized = image.resize((target_width, max(1, int(image.height * ratio))), Image.Resampling.LANCZOS)
    return _image_to_png_bytes(resized)


def _valid_reference_urls(reference_images: Sequence[str] | None) -> list[str]:
    output: list[str] = []
    for value in reference_images or []:
        text = str(value or "").strip()
        if not text:
            continue
        if text.startswith("http://") or text.startswith("https://") or text.startswith("data:image/"):
            output.append(text)
    return output


def _compose_board_image(
    title: str,
    plan_image: Image.Image,
    scene: dict[str, Any],
    *,
    board_template: str,
    include_photo_strip: bool,
    reference_images: Sequence[str] | None,
) -> tuple[Image.Image, dict[str, Any]]:
    width, height = plan_image.size
    board = Image.new("RGBA", (width, height), _hex_to_rgba("#f4f1e8", 255))
    draw = ImageDraw.Draw(board, "RGBA")
    panel_bg = _hex_to_rgba("#f8f6f1", 255)
    left_margin = int(width * 0.03)
    right_margin = int(width * 0.03)
    gutter = int(width * 0.02)
    left_width = int(width * 0.62)
    right_width = width - left_margin - right_margin - left_width - gutter
    left_rect = (
        left_margin,
        int(height * 0.05),
        left_margin + left_width,
        int(height * 0.95),
    )
    right_rect = (
        left_rect[2] + gutter,
        int(height * 0.05),
        left_rect[2] + gutter + right_width,
        int(height * 0.95),
    )
    draw.rounded_rectangle(left_rect, radius=18, fill=panel_bg, outline=_hex_to_rgba("#d5d1c8", 210), width=1)
    draw.rounded_rectangle(right_rect, radius=18, fill=panel_bg, outline=_hex_to_rgba("#d5d1c8", 210), width=1)

    plan_target_w = left_rect[2] - left_rect[0] - 28
    plan_target_h = left_rect[3] - left_rect[1] - 36
    fitted_plan = ImageOps.fit(plan_image, (plan_target_w, plan_target_h), method=Image.Resampling.LANCZOS)
    board.alpha_composite(fitted_plan, (left_rect[0] + 14, left_rect[1] + 18))

    draw.text((right_rect[0] + 16, right_rect[1] + 16), "RENDERED ILLUSTRATIVE MASTER PLAN", fill=_hex_to_rgba("#126a8b", 255))
    draw.text((right_rect[0] + 16, right_rect[1] + 44), _normalize_whitespace(title) or "Master Plan", fill=_hex_to_rgba("#26332a", 255))
    draw.line((right_rect[0] + 16, right_rect[1] + 84, right_rect[2] - 16, right_rect[1] + 84), fill=_hex_to_rgba("#d6d2c8", 255), width=1)
    draw.text((right_rect[0] + 16, right_rect[1] + 96), "Change of Program", fill=_hex_to_rgba("#1f2927", 255))

    valid_refs = _valid_reference_urls(reference_images)
    render_reference_strip = include_photo_strip and len(valid_refs) > 0
    strip_top = right_rect[3] - int(height * 0.17)
    if render_reference_strip:
        draw.text((right_rect[0] + 16, strip_top - 28), "Reference Strip", fill=_hex_to_rgba("#1f2927", 255))
        thumb_h = int(height * 0.07)
        thumb_w = int((right_rect[2] - right_rect[0] - 36) / max(min(len(valid_refs), 3), 1))
        for idx, url in enumerate(valid_refs[:3]):
            x0 = right_rect[0] + 16 + idx * (thumb_w + 6)
            y0 = strip_top
            color_hash = hashlib.sha1(url.encode("utf-8")).hexdigest()
            fill = f"#{color_hash[0:6]}"
            draw.rounded_rectangle((x0, y0, x0 + thumb_w, y0 + thumb_h), radius=6, fill=_hex_to_rgba(fill, 255))

    board_meta = {
        "template": board_template,
        "left_panel": {"x": left_rect[0], "y": left_rect[1], "width": left_rect[2] - left_rect[0], "height": left_rect[3] - left_rect[1]},
        "right_panel": {"x": right_rect[0], "y": right_rect[1], "width": right_rect[2] - right_rect[0], "height": right_rect[3] - right_rect[1]},
        "reference_strip_rendered": render_reference_strip,
        "reference_strip_count": len(valid_refs) if render_reference_strip else 0,
        "scene_geometry_hash": scene.get("geometry_hash"),
    }
    return board, board_meta


def _compose_board_svg(image_bytes: bytes, width: int, height: int) -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'<image href="data:image/png;base64,{encoded}" x="0" y="0" width="{width}" height="{height}" preserveAspectRatio="none" />'
        "</svg>"
    )

def _build_ai_style_pass_prompt(
    title: str,
    scene: dict[str, Any],
    style_preset: str,
    prompt: str | None,
    reference_metadata: Sequence[dict[str, Any]] | None,
    variant: dict[str, Any],
) -> str:
    _ = variant
    style_pass_surface_directive = "Treat the entire site as one coherent orthographic aerial image with one light direction, one atmospheric condition, and one continuous material world." if style_preset in {"photorealistic_aerial", "photoreal_orthographic_aerial"} else "Treat the entire site as one continuous sheet with one palette family, one light direction, and one shared paper texture."
    lines = [
        "90-degree direct overhead planimetric master plan. True top-down view only. No side views. No elevations. No collage elements.",
        style_pass_surface_directive,
        "Preserve every existing site boundary, zone clip, building footprint, roof edge, street alignment, planting bed, and water edge exactly as already drawn.",
        "Do not turn archetype labels, precedent captions, or reference metadata into separate picture tiles, facade inserts, or floating boards.",
        "Keep all geometry planimetric: roof plans and footprints only. No oblique or eye-level interpretation.",
    ]
    title_clean = _normalize_whitespace(title)
    if title_clean:
        lines.append(f"Project title context: {title_clean}.")

    prompt_clean = _sanitize_planimetric_text(prompt)
    if prompt_clean:
        lines.append(f"Style intent: {prompt_clean}.")

    for zone in scene.get("prompt_zones", []):
        color = str(zone.get("color") or "#9b59b6")
        zone_type = _normalize_zone_type(zone.get("zone_type"))
        props = zone.get("properties") if isinstance(zone.get("properties"), dict) else {}
        if zone_type in {"building", "residential", "development_area"}:
            gsi = props.get("generation_style_input") if isinstance(props.get("generation_style_input"), dict) else {}
            archetype = _normalize_whitespace(gsi.get("archetypeLabel") or gsi.get("subtype") or zone.get("name") or "the defined architectural precinct")
            directive = f"Render the roof plan and building footprint for {archetype}."
        elif zone_type == "green_space":
            gsi_all = props.get("generation_style_inputs") if isinstance(props.get("generation_style_inputs"), dict) else {}
            park = gsi_all.get("parks") if isinstance(gsi_all.get("parks"), dict) else {}
            profile = park.get("styleProfile") if isinstance(park.get("styleProfile"), dict) else {}
            landscape = _normalize_whitespace(profile.get("landscapeCharacter") or park.get("subcategory") or "formal civic garden composition")
            directive = f"Render a top-down landscape plan with {landscape}."
        elif zone_type == "road":
            gsi_all = props.get("generation_style_inputs") if isinstance(props.get("generation_style_inputs"), dict) else {}
            street = gsi_all.get("streets_paths") if isinstance(gsi_all.get("streets_paths"), dict) else {}
            profile = street.get("styleProfile") if isinstance(street.get("styleProfile"), dict) else {}
            corridor = _normalize_whitespace(profile.get("corridorCharacter") or "ceremonial paseo public realm")
            directive = f"Render a flat plan-view corridor with {corridor}."
        else:
            directive = "Render this zone in strict plan-view while preserving existing geometry."
        lines.append(f"[Within {color} Zone]: {directive}")
        description = _sanitize_planimetric_text(props.get("description_text"))
        if description:
            lines.append(f"CRITICAL DESIGN DIRECTIVE: {_ensure_sentence(description)}")

    for item in _sanitize_reference_metadata_bundle(reference_metadata):
        caption = _normalize_whitespace(item.get("caption") or item.get("prompt_text") or "")
        if caption:
            lines.append(f"Reference cue: {caption}.")

    lines.append(f"Do not output text labels in the image. Style pass target: {style_preset}.")
    return "\n".join(lines)


def _compose_ai_style_pass(
    base_image: Image.Image,
    styled_image: Image.Image,
    scene: dict[str, Any],
    variant: dict[str, Any],
) -> Image.Image:
    base = base_image.convert("RGBA")
    styled = styled_image.convert("RGBA")
    if base.size != styled.size:
        styled = ImageOps.fit(styled, base.size, method=Image.Resampling.LANCZOS)

    boundary = _polygon_from_geometry(scene.get("pixel", {}).get("boundary"))
    if boundary is None:
        blended = Image.blend(base, styled, 0.22)
        return blended

    mask = Image.new("L", base.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon(_polygon_coords(boundary), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=1.4))

    merged = Image.composite(styled, base, mask)
    merged = Image.blend(base, merged, 0.33)
    contrast = 1.02 + (int(variant.get("seed") or 0) % 3) * 0.01
    merged = ImageEnhance.Contrast(merged).enhance(contrast)
    saturation = 1.03 if variant.get("quality_level") == "board_ready" else 1.0
    merged = ImageEnhance.Color(merged).enhance(saturation)

    grain = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(grain, "RGBA")
    rng = random.Random(int(variant.get("seed") or 0) + 404)
    for _ in range(900):
        x = rng.randint(0, base.width - 1)
        y = rng.randint(0, base.height - 1)
        alpha = rng.randint(4, 12)
        draw.point((x, y), fill=(255, 255, 255, alpha))
    return ImageChops.add(merged, grain)



def _run_stability_structure_pass(
    *,
    control_image: Image.Image,
    prompt: str,
    negative_prompt: str,
    control_strength: float,
) -> tuple[Image.Image | None, str | None]:
    if not settings.stability_api_key:
        return None, 'STABILITY_API_KEY not configured'
    try:
        httpx = importlib.import_module('httpx')
    except Exception as exc:
        return None, f'stability http client unavailable: {exc}'

    image_bytes = _image_to_png_bytes(control_image.convert('RGB'))
    url = f'{settings.stability_api_base.rstrip("/")}/v2beta/stable-image/control/structure'
    try:
        response = httpx.post(
            url,
            headers={
                'Authorization': f'Bearer {settings.stability_api_key}',
                'Accept': 'image/*',
            },
            data={
                'prompt': prompt,
                'negative_prompt': negative_prompt,
                'control_strength': f'{max(0.0, min(control_strength, 1.0)):.2f}',
                'output_format': 'png',
            },
            files={'image': ('structure.png', image_bytes, 'image/png')},
            timeout=90.0,
        )
        response.raise_for_status()
        styled = Image.open(io.BytesIO(response.content)).convert('RGBA')
        return styled, None
    except Exception as exc:
        return None, f'stability structure pass failed: {exc}'
def _run_stability_style_pass(
    *,
    base_image: Image.Image,
    prompt: str,
    negative_prompt: str,
) -> tuple[Image.Image | None, str | None]:
    if not settings.stability_api_key:
        return None, "STABILITY_API_KEY not configured"
    try:
        httpx = importlib.import_module("httpx")
    except Exception as exc:
        return None, f"stability http client unavailable: {exc}"

    image_bytes = _image_to_png_bytes(base_image.convert("RGB"))
    url = f"{settings.stability_api_base.rstrip('/')}/v2beta/stable-image/edit/search-and-replace"
    try:
        response = httpx.post(
            url,
            headers={
                "Authorization": f"Bearer {settings.stability_api_key}",
                "Accept": "image/*",
            },
            data={
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "model": STABILITY_STYLE_PASS_MODEL,
            },
            files={"image": ("input.png", image_bytes, "image/png")},
            timeout=60.0,
        )
        response.raise_for_status()
        styled = Image.open(io.BytesIO(response.content)).convert("RGBA")
        return styled, None
    except Exception as exc:
        return None, f"stability style pass failed: {exc}"


def _run_gemini_style_pass(
    *,
    base_image: Image.Image,
    prompt: str,
) -> tuple[Image.Image | None, str | None]:
    if not settings.gemini_api_key:
        return None, "GEMINI_API_KEY not configured"
    try:
        google = importlib.import_module("google")
        genai = getattr(google, "genai")
        client = genai.Client(api_key=settings.gemini_api_key)
        payload = [
            genai.types.Part.from_bytes(data=_image_to_png_bytes(base_image.convert("RGB")), mime_type="image/png"),
            prompt,
        ]
        response = client.models.generate_content(
            model=str(getattr(settings, "master_plan_2d_style_model", "") or "gemini-3.1-flash-image-preview"),
            contents=payload,
            config=genai.types.GenerateContentConfig(
                temperature=0.2,
                candidate_count=1,
                response_modalities=["IMAGE"],
            ),
        )
        if not response or not getattr(response, "candidates", None):
            return None, "gemini style pass returned no candidates"
        parts = response.candidates[0].content.parts
        if not parts:
            return None, "gemini style pass returned no image parts"
        data = None
        for part in parts:
            inline = getattr(part, "inline_data", None)
            if inline is not None and getattr(inline, "data", None):
                data = inline.data
                break
        if not data:
            return None, "gemini style pass returned no inline image bytes"
        styled = Image.open(io.BytesIO(data)).convert("RGBA")
        return styled, None
    except Exception as exc:
        return None, f"gemini style pass failed: {exc}"


def _apply_ai_style_pass(
    *,
    base_image: Image.Image,
    title: str,
    scene: dict[str, Any],
    style_preset: str,
    prompt: str | None,
    reference_metadata: Sequence[dict[str, Any]] | None,
    variant: dict[str, Any],
    provider_preference: str,
    control_maps: dict[str, Image.Image] | None = None,
) -> tuple[Image.Image, dict[str, Any]]:
    providers = ["gemini", "stability"] if provider_preference == "auto" else [provider_preference]
    status = {
        "requested": True,
        "applied": False,
        "requested_provider": provider_preference,
        "attempted_providers": [],
        "provider": None,
        "model": None,
        "reason": None,
        "control_mode": None,
    }
    reasons: list[str] = []
    prompt_text = _build_ai_style_pass_prompt(title, scene, style_preset, prompt, reference_metadata, variant)
    for provider in providers:
        status["attempted_providers"].append(provider)
        styled: Image.Image | None
        error: str | None
        if provider == "gemini":
            styled, error = _run_gemini_style_pass(base_image=base_image, prompt=prompt_text)
            if styled is not None:
                composited = _compose_ai_style_pass(base_image, styled, scene, variant)
                status["applied"] = True
                status["provider"] = "gemini"
                status["model"] = str(getattr(settings, "master_plan_2d_style_model", "") or "gemini-3.1-flash-image-preview")
                status["reason"] = None
                return composited, status
        elif provider == "stability":
            styled = None
            error = None
            structure_image = control_maps.get('structure') if isinstance(control_maps, dict) else None
            if variant.get('orthographic_mode') and isinstance(structure_image, Image.Image):
                styled, error = _run_stability_structure_pass(
                    control_image=structure_image,
                    prompt=prompt_text,
                    negative_prompt=STYLE_PASS_NEGATIVE_PROMPT,
                    control_strength=float(variant.get('stability_control_strength') or 0.88),
                )
                if styled is not None:
                    composited = _compose_ai_style_pass(base_image, styled, scene, variant)
                    status["applied"] = True
                    status["provider"] = "stability"
                    status["model"] = STABILITY_STRUCTURE_MODEL
                    status["reason"] = None
                    status["control_mode"] = "structure"
                    return composited, status
            styled, error = _run_stability_style_pass(
                base_image=base_image,
                prompt=prompt_text,
                negative_prompt=STYLE_PASS_NEGATIVE_PROMPT,
            )
            if styled is not None:
                composited = _compose_ai_style_pass(base_image, styled, scene, variant)
                status["applied"] = True
                status["provider"] = "stability"
                status["model"] = STABILITY_STYLE_PASS_MODEL
                status["reason"] = None
                status["control_mode"] = "search_and_replace"
                return composited, status
        else:
            error = f"unknown style pass provider '{provider}'"
        if error:
            reasons.append(error)
    status["reason"] = " | ".join(reasons) if reasons else "No AI style pass provider succeeded."
    return base_image, status


def _render_variant_assets(
    title: str,
    scene: dict[str, Any],
    style_preset: str,
    toggles: dict[str, bool],
    prompt: str | None,
    reference_images: Sequence[str] | None,
    reference_metadata: Sequence[dict[str, Any]] | None,
    quality_level: str,
    variant_index: int,
    debug: bool,
    *,
    compose_board: bool = True,
    board_template: str = "master_plan_board_v1",
    include_photo_strip: bool = True,
    ai_style_pass_enabled: bool = False,
    ai_style_pass_provider: str = "auto",
    render_style_preset: str | None = None,
    lighting_atmosphere_preset: str | None = None,
    map_screenshot_satellite: str | None = None,
) -> dict[str, Any]:
    _ = debug
    variant = _make_variant_profile(
        style_preset,
        quality_level,
        variant_index,
        scene["geometry_hash"],
        render_style_preset=render_style_preset,
        lighting_atmosphere_preset=lighting_atmosphere_preset,
    )
    context_underlay, context_underlay_status = _resolve_context_underlay(
        scene,
        render_style_preset=render_style_preset,
        map_screenshot_satellite=map_screenshot_satellite,
    )
    variant["context_underlay_mode"] = bool(context_underlay)
    variant["context_underlay_source"] = context_underlay_status.get("source")

    plan_image = _render_plan_image(
        scene,
        style_preset=style_preset,
        variant=variant,
        toggles=toggles,
        context_underlay=context_underlay,
    )
    control_images = _render_control_maps(scene, variant, toggles, base_image=plan_image)
    control_maps = {
        "available": True,
        "conditioning_mode": "stability_structure_ready" if variant.get("orthographic_mode") else "deterministic_control_maps_only",
        "control_strength": float(variant.get("stability_control_strength") or 0.0),
        "images": control_images,
    }
    plan_svg = _render_plan_svg(scene, style_preset, variant, toggles)

    ai_style_status = {
        "requested": False,
        "applied": False,
        "requested_provider": ai_style_pass_provider,
        "attempted_providers": [],
        "provider": None,
        "model": None,
        "reason": "disabled",
    }
    styled_plan = plan_image
    if ai_style_pass_enabled:
        styled_plan, ai_style_status = _apply_ai_style_pass(
            base_image=plan_image,
            title=title,
            scene=scene,
            style_preset=style_preset,
            prompt=prompt,
            reference_metadata=reference_metadata,
            variant=variant,
            provider_preference=ai_style_pass_provider,
            control_maps=control_images,
        )

    plan_full_png = _image_to_png_bytes(styled_plan)
    plan_preview_png = _preview_png(styled_plan, target_width=1500)

    full_png = plan_full_png
    preview_png = plan_preview_png
    svg = plan_svg
    board_meta: dict[str, Any] = {"template": "plan_only"}
    if compose_board:
        board_image, board_meta = _compose_board_image(
            title,
            styled_plan,
            scene,
            board_template=board_template,
            include_photo_strip=include_photo_strip,
            reference_images=reference_images,
        )
        full_png = _image_to_png_bytes(board_image)
        preview_png = _preview_png(board_image, target_width=1500)
        svg = _compose_board_svg(full_png, board_image.width, board_image.height)

    style_guide = build_master_plan_style_guide(
        style_key=style_preset,
        style_name=STYLE_LABELS.get(style_preset, style_preset.replace("_", " ").title()),
        palette=variant["palette"],
        prompt=prompt,
        reference_images=reference_images,
    )

    return {
        "style_preset": style_preset,
        "style_name": STYLE_LABELS.get(style_preset, style_preset.replace("_", " ").title()),
        "variant": variant,
        "svg": svg,
        "plan_svg": plan_svg,
        "full_png": full_png,
        "preview_png": preview_png,
        "plan_full_png": plan_full_png,
        "plan_preview_png": plan_preview_png,
        "board": board_meta,
        "style_guide": style_guide,
        "ai_style_pass": ai_style_status,
        "context_underlay": context_underlay_status,
        "control_maps": control_maps,
    }

def _extract_city_context(project: Project, zones: Sequence[SiteZone]) -> str:
    location = getattr(project, "location", None) if project is not None else None
    if isinstance(location, dict):
        address = _normalize_whitespace(location.get("address"))
        if address:
            return address
    zone_names = [_normalize_whitespace(getattr(zone, "name", None)) for zone in zones]
    for name in zone_names:
        if name and len(name.split()) >= 2:
            return name
    return "downtown district"


def _resolve_zone_design_brief(zones: Sequence[SiteZone]) -> dict[str, str]:
    for zone in zones:
        props = getattr(zone, "properties", None)
        if not isinstance(props, dict):
            continue
        generation_style_input = props.get("generation_style_input")
        if isinstance(generation_style_input, dict):
            profile = generation_style_input.get("styleProfile")
            materials = generation_style_input.get("materials")
            return {
                "aesthetic_category": _normalize_whitespace(generation_style_input.get("aestheticCategoryLabel") or generation_style_input.get("subtype") or "eco-urban"),
                "architectural_language": _normalize_whitespace(profile.get("massing") if isinstance(profile, dict) else generation_style_input.get("subtype") or "contemporary mixed-use urban architecture"),
                "facade_materials": _normalize_whitespace(materials if isinstance(materials, str) else ", ".join(materials) if isinstance(materials, (list, tuple)) else "refined concrete and glazing"),
                "roof_style": _normalize_whitespace(profile.get("roofForm") if isinstance(profile, dict) else "articulated contemporary roof"),
                "landscape_character": _normalize_whitespace(profile.get("plantingType") if isinstance(profile, dict) else "layered urban planting"),
                "paving_type": _normalize_whitespace(profile.get("pavingType") if isinstance(profile, dict) else "high-quality urban paving"),
            }
    return {
        "aesthetic_category": "eco-urban",
        "architectural_language": "contemporary mixed-use urban architecture",
        "facade_materials": "refined concrete and glazing",
        "roof_style": "articulated contemporary roof expression",
        "landscape_character": "layered planting and pedestrian-focused public realm",
        "paving_type": "warm neutral unit paving",
    }


def _resolve_height_floor_defaults(zones: Sequence[SiteZone]) -> tuple[float, int]:
    heights: list[float] = []
    floors: list[int] = []
    for zone in zones:
        props = getattr(zone, "properties", None)
        if not isinstance(props, dict):
            continue
        for key in ("height", "height_m"):
            try:
                val = float(props.get(key))
            except (TypeError, ValueError):
                continue
            if val > 0:
                heights.append(val)
                break
        for key in ("floors", "floor_count", "floorCount"):
            try:
                val_int = int(float(props.get(key)))
            except (TypeError, ValueError):
                continue
            if val_int > 0:
                floors.append(val_int)
                break
    height_m = round(sum(heights) / len(heights), 1) if heights else 30.0
    floor_count = max(1, round(sum(floors) / len(floors))) if floors else 8
    return height_m, floor_count


def _build_2d_site_image_prompt(
    *,
    city_context: str,
    aesthetic_category: str,
    height_m: float,
    floor_count: int,
    architectural_language: str,
    facade_materials: str,
    roof_style: str,
    landscape_character: str,
    paving_type: str,
    global_style_payload: str,
) -> str:
    return (
        f"Create a premium professional architectural site image for a proposed urban redevelopment in {city_context}. "
        "Render the proposal in a direct overhead to controlled slight aerial-oblique view, preserving the exact site footprint, block geometry, podium arrangement, tower placement, courtyard organization, and public realm structure defined by the project geometry.\n\n"
        "This is an image of the SITE ONLY, not a presentation board.\n\n"
        f"Render an {aesthetic_category} mixed-use development with approximately {height_m:.1f} m / {floor_count} storey residential towers over an active mixed-use podium with retail at grade. "
        "Show clear tower footprints, podium edges, framed urban corners, refined roof planes, planted terraces, green roofs where appropriate, active storefront frontage, canopies, widened sidewalks, street trees, pedestrian mews, internal courtyard landscaping, plaza moments, elegant paving, and high-quality urban open space.\n\n"
        f"Architectural language: {architectural_language}. Materials and expression: {facade_materials}, {roof_style}, {landscape_character}, {paving_type}. "
        "The site should feel investment-grade, climate-responsive, walkable, and highly designed.\n\n"
        "Use strong contrast, crisp edges, elegant architectural shadows, rich but controlled color, deep green planting, warm neutral hardscape, refined concrete and glazing tones, and premium developer-presentation quality. "
        "Surrounding context must remain subdued and desaturated so the proposal reads as the visual focus.\n\n"
        f"{global_style_payload}\n\n"
        "Important: do not generate any presentation-board graphics or UI. No title, no legend, no labels, no callout markers, no north arrow, no scale bar, no reference strip, no descriptive copy, no text of any kind. "
        "Do not create a collage, diagram board, or faded conceptual wash. Do not simplify the proposal into blank beige bars or generic massing blocks. "
        "The result must read as a believable, detailed, premium architectural site image."
    )


def _collect_scene_payload(project: Project, zones: Sequence[SiteZone], buildings: Sequence[Building]) -> dict[str, Any]:
    _ = project
    boundary: Polygon | None = None
    scene: dict[str, Any] = {
        "boundary": None,
        "building_footprints": [],
        "building_masses": [],
        "roads": [],
        "paths": [],
        "parks": [],
        "plazas": [],
        "water": [],
        "callouts": [],
        "context_buildings": [],
        "context_parks": [],
        "context_water": [],
        "context_roads": [],
        "buildable_zones": [],
        "prompt_zones": [],
    }

    for zone in sorted(zones, key=lambda item: (getattr(item, "sort_order", 0), getattr(item, "created_at", _now_utc()))):
        geometry = _polygon_from_geometry(getattr(zone, "geometry", None))
        if geometry is None:
            continue
        zone_type = _normalize_zone_type(getattr(zone, "zone_type", None))
        properties = getattr(zone, "properties", None) if isinstance(getattr(zone, "properties", None), dict) else {}
        zone_payload = {
            "zone_id": str(getattr(zone, "id", "")),
            "zone_type": zone_type,
            "name": getattr(zone, "name", None),
            "color": getattr(zone, "color", "#9b59b6"),
            "properties": properties,
        }
        if zone_type == "site_boundary":
            boundary = geometry
            continue

        if zone_type in {"building", "residential", "development_area"}:
            scene["buildable_zones"].append({"geometry": geometry, "name": getattr(zone, "name", None), "properties": properties})
            if zone_type == "building":
                if _should_generate_precinct_for_building_zone(geometry, properties):
                    for footprint in _generate_precinct_footprints(zone, geometry, scene):
                        scene["building_footprints"].append(footprint)
                else:
                    scene["building_footprints"].append({"geometry": geometry, "name": getattr(zone, "name", None), "properties": properties})
            else:
                for footprint in _generate_precinct_footprints(zone, geometry, scene):
                    scene["building_footprints"].append(footprint)
        elif zone_type == "road":
            scene["roads"].append({"geometry": geometry, "kind": "road", "width_m": float(properties.get("width") or 8.0), "properties": properties})
        elif zone_type == "green_space":
            scene["parks"].append({"geometry": geometry, "name": getattr(zone, "name", None), "properties": properties})
        elif zone_type == "water":
            scene["water"].append({"geometry": geometry, "name": getattr(zone, "name", None), "properties": properties})
        elif zone_type == "parking":
            scene["plazas"].append({"geometry": geometry, "name": getattr(zone, "name", None), "properties": properties})
        scene["prompt_zones"].append(zone_payload)

    if boundary is None:
        candidates = [item["geometry"] for item in scene["buildable_zones"]]
        if not candidates:
            candidates = [item["geometry"] for item in scene["parks"] + scene["roads"] + scene["plazas"] + scene["water"] if item.get("geometry")]
        if candidates:
            boundary_union = unary_union(candidates).convex_hull.buffer(0)
            boundary = boundary_union if isinstance(boundary_union, Polygon) else boundary_union.envelope
    if boundary is None:
        raise ValueError("Project does not include enough site geometry to generate a 2D master plan.")
    scene["boundary"] = boundary

    for building in buildings:
        footprint = _polygon_from_geometry(getattr(building, "footprint", None))
        if footprint is None:
            continue
        scene["context_buildings"].append({"geometry": footprint, "name": getattr(building, "name", None), "properties": {"source": "building_model"}})

    return scene


def _generate_precinct_footprints(zone: Any, zone_geometry: Polygon, context: dict[str, Any]) -> list[dict[str, Any]]:
    _ = context
    zone_id = str(getattr(zone, "id", ""))
    properties = getattr(zone, "properties", None) if isinstance(getattr(zone, "properties", None), dict) else {}
    description = _normalize_whitespace(properties.get("description_text"))
    grammars = [
        "parallel_bars",
        "perimeter_courtyard",
        "townhouse_courtyard",
        "mixed_use_edge",
        "clustered_bars",
    ]
    deterministic_seed = int(hashlib.sha1(f"{zone_id}:{description}".encode("utf-8")).hexdigest()[:8], 16)
    grammar = grammars[deterministic_seed % len(grammars)]
    minx, miny, maxx, maxy = zone_geometry.bounds
    width = maxx - minx
    height = maxy - miny
    pad = min(width, height) * 0.06
    usable = zone_geometry.buffer(-pad)
    if usable.is_empty or not isinstance(usable, Polygon):
        usable = zone_geometry

    footprints: list[Polygon] = []
    if grammar == "parallel_bars":
        bar_w = width * 0.24
        gaps = [0.27, 0.58]
        for g in gaps:
            poly = box(minx + width * g - bar_w / 2, miny + height * 0.18, minx + width * g + bar_w / 2, miny + height * 0.84)
            clipped = _polygon_from_geometry(poly.intersection(usable))
            if clipped is not None:
                footprints.append(clipped)
    elif grammar == "perimeter_courtyard":
        outer = box(minx + width * 0.14, miny + height * 0.14, minx + width * 0.86, miny + height * 0.86)
        inner = box(minx + width * 0.36, miny + height * 0.36, minx + width * 0.64, miny + height * 0.64)
        ring = _polygon_from_geometry(outer.difference(inner).intersection(usable))
        if ring is not None and ring.area > 0:
            pieces = [
                box(minx + width * 0.14, miny + height * 0.14, minx + width * 0.86, miny + height * 0.28),
                box(minx + width * 0.14, miny + height * 0.72, minx + width * 0.86, miny + height * 0.86),
                box(minx + width * 0.14, miny + height * 0.28, minx + width * 0.28, miny + height * 0.72),
                box(minx + width * 0.72, miny + height * 0.28, minx + width * 0.86, miny + height * 0.72),
            ]
            for piece in pieces:
                clipped = _polygon_from_geometry(piece.intersection(usable))
                if clipped is not None and clipped.area > 0:
                    footprints.append(clipped)
    elif grammar == "townhouse_courtyard":
        for row in (0.26, 0.74):
            for col in (0.24, 0.50, 0.76):
                poly = box(
                    minx + width * col - width * 0.09,
                    miny + height * row - height * 0.10,
                    minx + width * col + width * 0.09,
                    miny + height * row + height * 0.10,
                )
                clipped = _polygon_from_geometry(poly.intersection(usable))
                if clipped is not None:
                    footprints.append(clipped)
    elif grammar == "mixed_use_edge":
        edge = box(minx + width * 0.10, miny + height * 0.65, minx + width * 0.90, miny + height * 0.86)
        tower_a = box(minx + width * 0.24, miny + height * 0.24, minx + width * 0.40, miny + height * 0.56)
        tower_b = box(minx + width * 0.60, miny + height * 0.28, minx + width * 0.78, miny + height * 0.58)
        for poly in (edge, tower_a, tower_b):
            clipped = _polygon_from_geometry(poly.intersection(usable))
            if clipped is not None:
                footprints.append(clipped)
    else:
        rng = random.Random(deterministic_seed)
        for _ in range(4):
            cx = rng.uniform(minx + width * 0.22, minx + width * 0.78)
            cy = rng.uniform(miny + height * 0.24, miny + height * 0.78)
            w = width * rng.uniform(0.14, 0.22)
            h = height * rng.uniform(0.14, 0.22)
            poly = box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
            clipped = _polygon_from_geometry(poly.intersection(usable))
            if clipped is not None:
                footprints.append(clipped)

    if len(footprints) < 2:
        fallback_a = box(minx + width * 0.2, miny + height * 0.2, minx + width * 0.46, miny + height * 0.6)
        fallback_b = box(minx + width * 0.54, miny + height * 0.28, minx + width * 0.8, miny + height * 0.72)
        for poly in (fallback_a, fallback_b):
            clipped = _polygon_from_geometry(poly.intersection(usable))
            if clipped is not None:
                footprints.append(clipped)

    outputs: list[dict[str, Any]] = []
    for idx, poly in enumerate(footprints):
        outputs.append(
            {
                "geometry": poly,
                "name": f"{getattr(zone, 'name', 'Precinct')} {idx + 1}",
                "properties": {
                    "generated_precinct_grammar": grammar,
                    "source_zone_id": zone_id,
                    "description_text": description,
                    "height": properties.get("height") or properties.get("height_m"),
                    "height_m": properties.get("height_m") or properties.get("height"),
                    "floors": properties.get("floors") or properties.get("floor_count") or properties.get("floorCount"),
                    "floor_count": properties.get("floor_count") or properties.get("floors") or properties.get("floorCount"),
                },
            }
        )
    return outputs


def _extract_zone_properties(zone: Any, skipped_zones: list[dict[str, Any]]) -> dict[str, Any]:
    properties = getattr(zone, "properties", None)
    if properties is None:
        return {}
    if isinstance(properties, dict):
        return dict(properties)
    skipped_zones.append(
        {
            "zone_id": str(getattr(zone, "zone_id", getattr(zone, "id", "")) or ""),
            "zone_label": getattr(zone, "name", None),
            "reason": "Zone properties were malformed and could not be parsed; defaults were applied.",
        }
    )
    logger.warning("Zone %s contains malformed properties payload (%s)", getattr(zone, "id", "unknown"), type(properties).__name__)
    return {}


def _clip_zone_polygon_to_boundary(zone_geometry: Polygon, boundary: Polygon) -> tuple[Polygon | None, str | None]:
    if zone_geometry is None or zone_geometry.is_empty:
        return None, "Zone geometry is missing."
    if boundary is None or boundary.is_empty:
        return None, "Site boundary geometry is missing."
    try:
        clipped = zone_geometry.intersection(boundary)
    except Exception as exc:
        return None, f"Zone geometry failed while clipping to boundary: {exc}"
    polygon = _polygon_from_geometry(clipped)
    if polygon is None or polygon.is_empty:
        return None, "Zone geometry could not be clipped to the site boundary."
    return polygon, None


def _zone_snapshots_from_request(request: MasterPlan3DGenerateRequest) -> list[ZoneSnapshot]:
    snapshots: list[ZoneSnapshot] = []
    for idx, zone in enumerate(request.zones or []):
        zone_id = str(getattr(zone, "zone_id", None) or (zone.get("zone_id") if isinstance(zone, dict) else "") or f"zone-{idx + 1}")
        zone_type_raw = getattr(zone, "zone_type", None) if not isinstance(zone, dict) else zone.get("zone_type")
        zone_type = _normalize_zone_type(zone_type_raw)
        polygon_payload = getattr(zone, "polygon", None) if not isinstance(zone, dict) else zone.get("polygon")
        geometry = _polygon_from_coordinates(polygon_payload)
        if geometry is None:
            logger.warning("Skipping zone snapshot %s due to invalid polygon payload.", zone_id)
            continue
        name = _normalize_whitespace(
            getattr(zone, "zone_label", None) if not isinstance(zone, dict) else zone.get("zone_label")
        ) or f"Zone {idx + 1}"
        color = str(getattr(zone, "color", None) if not isinstance(zone, dict) else zone.get("color") or "#9b59b6")
        properties: dict[str, Any] = {}
        for key in ("height_m", "floor_count", "archetype_title", "archetype_metadata", "user_notes"):
            value = getattr(zone, key, None) if not isinstance(zone, dict) else zone.get(key)
            if value is not None:
                properties[key] = value
        snapshots.append(
            ZoneSnapshot(
                zone_id=zone_id,
                zone_type=zone_type,
                name=name,
                color=color,
                geometry=geometry,
                properties=properties,
                sort_order=idx,
                created_at=_now_utc(),
            )
        )
    return snapshots


def _boundary_from_snapshot_zones(snapshot_zones: Sequence[ZoneSnapshot]) -> Polygon | None:
    polygons = [zone.geometry for zone in snapshot_zones if isinstance(zone.geometry, Polygon) and not zone.geometry.is_empty]
    if not polygons:
        return None
    boundary = unary_union(polygons).convex_hull.buffer(0)
    if isinstance(boundary, Polygon):
        return boundary
    if isinstance(boundary, MultiPolygon):
        return max(boundary.geoms, key=lambda geom: geom.area, default=None)
    return None



def _render_perspective_conditioning_assets(
    boundary: Polygon,
    zones: Sequence[Any],
    *,
    primary_zone_id: str,
    selected_perspective: str,
) -> dict[str, Any] | None:
    if boundary is None or boundary.is_empty:
        return None

    image_width = 1280
    image_height = 896
    minx, miny, maxx, maxy = boundary.bounds
    center_lng = (minx + maxx) / 2.0
    center_lat = (miny + maxy) / 2.0
    meters_lon = _meters_per_degree_lon(center_lat)
    meters_lat = _meters_per_degree_lat(center_lat)
    site_width_m = max((maxx - minx) * meters_lon, 60.0)
    site_height_m = max((maxy - miny) * meters_lat, 60.0)
    site_span = max(site_width_m, site_height_m)

    def _world_point(lng: float, lat: float, elevation: float = 0.0) -> tuple[float, float, float]:
        return (
            (float(lng) - center_lng) * meters_lon,
            float(elevation),
            (center_lat - float(lat)) * meters_lat,
        )

    def _vec_sub(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
        return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

    def _vec_dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
        return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

    def _vec_cross(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
        return (
            a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0],
        )

    def _vec_len(v: tuple[float, float, float]) -> float:
        return math.sqrt(max(_vec_dot(v, v), 0.0))

    def _vec_norm(v: tuple[float, float, float]) -> tuple[float, float, float]:
        length = _vec_len(v)
        if length <= 1e-9:
            return (0.0, 0.0, 0.0)
        return (v[0] / length, v[1] / length, v[2] / length)

    primary_polygon = boundary
    primary_height_m = 24.0
    zone_features: list[dict[str, Any]] = []
    for zone in zones:
        geometry = _polygon_from_geometry(getattr(zone, 'geometry', None))
        if geometry is None or geometry.is_empty:
            continue
        zone_id = str(getattr(zone, 'zone_id', getattr(zone, 'id', '')))
        zone_type = _normalize_zone_type(getattr(zone, 'zone_type', None))
        properties = getattr(zone, 'properties', None) if isinstance(getattr(zone, 'properties', None), dict) else {}
        height_m = _feature_height_m({'properties': properties}) if zone_type in {'building', 'residential', 'development_area'} else 0.0
        zone_features.append({'zone_id': zone_id, 'zone_type': zone_type, 'geometry': geometry, 'properties': properties, 'height_m': height_m})
        if zone_id == primary_zone_id:
            primary_polygon = geometry
            primary_height_m = max(height_m, 18.0)

    primary_centroid = primary_polygon.centroid
    focus = _world_point(primary_centroid.x, primary_centroid.y, max(primary_height_m * 0.24, 4.0))
    if selected_perspective == 'street_level_eye_height':
        camera = (focus[0] - site_span * 0.92, max(14.0, min(primary_height_m * 0.42, 34.0)), focus[2] + site_span * 0.22)
        fov_deg = 52.0
        horizon = 0.64
    elif selected_perspective == 'promenade_view':
        camera = (focus[0] - site_span * 0.48, max(12.0, min(primary_height_m * 0.36, 30.0)), focus[2] + site_span * 0.88)
        fov_deg = 47.0
        horizon = 0.62
    elif selected_perspective == 'corner_perspective':
        camera = (focus[0] - site_span * 1.02, max(site_span * 0.78, primary_height_m * 2.1), focus[2] + site_span * 0.58)
        fov_deg = 38.0
        horizon = 0.60
    else:
        camera = (focus[0] - site_span * 1.14, max(site_span * 1.10, primary_height_m * 2.5), focus[2] + site_span * 1.04)
        fov_deg = 34.0
        horizon = 0.58
    target = (focus[0], max(primary_height_m * 0.34, 8.0), focus[2])

    forward = _vec_norm(_vec_sub(target, camera))
    right = _vec_norm(_vec_cross(forward, (0.0, 1.0, 0.0)))
    if _vec_len(right) <= 1e-6:
        right = (1.0, 0.0, 0.0)
    up = _vec_norm(_vec_cross(right, forward))
    aspect = image_width / image_height
    tan_half_fov = math.tan(math.radians(fov_deg) / 2.0)

    def _project(point: tuple[float, float, float]) -> tuple[float, float, float] | None:
        rel = _vec_sub(point, camera)
        depth = _vec_dot(rel, forward)
        if depth <= 1.0:
            return None
        cam_x = _vec_dot(rel, right)
        cam_y = _vec_dot(rel, up)
        ndc_x = cam_x / (depth * tan_half_fov * aspect)
        ndc_y = cam_y / (depth * tan_half_fov)
        px = (ndc_x * 0.5 + 0.5) * image_width
        py = (horizon - ndc_y * 0.5) * image_height
        return (px, py, depth)

    def _face_visible(points: list[tuple[float, float, float]]) -> bool:
        if len(points) < 3:
            return False
        normal = _vec_cross(_vec_sub(points[1], points[0]), _vec_sub(points[2], points[0]))
        center = (
            sum(point[0] for point in points) / len(points),
            sum(point[1] for point in points) / len(points),
            sum(point[2] for point in points) / len(points),
        )
        return _vec_dot(normal, _vec_sub(camera, center)) > 0.0

    faces: list[dict[str, Any]] = []
    boundary_world = [_world_point(x, y, 0.0) for x, y in list(boundary.exterior.coords)]
    faces.append({
        'points': boundary_world,
        'massing_fill': (60, 66, 72, 255),
        'seg_fill': (54, 58, 66, 255),
        'outline': (255, 255, 255, 80),
    })

    for feature in zone_features:
        geometry = feature['geometry']
        zone_type = feature['zone_type']
        zone_id = feature['zone_id']
        is_primary = zone_id == primary_zone_id
        coords_world = [_world_point(x, y, 0.0) for x, y in list(geometry.exterior.coords)]
        if len(coords_world) < 4:
            continue
        if zone_type in {'building', 'residential', 'development_area'}:
            height_m = max(float(feature['height_m'] or 0.0), 14.0)
            top_points = [(point[0], height_m, point[2]) for point in coords_world]
            roof_fill = (224, 226, 230, 255) if is_primary else (198, 202, 208, 240)
            side_fill = (152, 158, 168, 255) if is_primary else (128, 134, 144, 220)
            seg_fill = (236, 122, 88, 255) if is_primary else (176, 98, 74, 232)
            faces.append({'points': top_points, 'massing_fill': roof_fill, 'seg_fill': seg_fill, 'outline': (255, 255, 255, 180)})
            for idx in range(len(coords_world) - 1):
                side = [coords_world[idx], coords_world[idx + 1], top_points[idx + 1], top_points[idx]]
                if _face_visible(side):
                    faces.append({'points': side, 'massing_fill': side_fill, 'seg_fill': seg_fill, 'outline': (255, 255, 255, 90)})
        else:
            if zone_type == 'green_space':
                massing_fill = (98, 136, 92, 255)
                seg_fill = (72, 158, 96, 255)
            elif zone_type == 'water':
                massing_fill = (78, 112, 142, 255)
                seg_fill = (66, 130, 202, 255)
            elif zone_type in {'road', 'parking'}:
                massing_fill = (130, 134, 140, 255) if zone_type == 'road' else (182, 174, 156, 255)
                seg_fill = (92, 116, 192, 255) if zone_type == 'road' else (228, 190, 128, 255)
            else:
                massing_fill = (142, 146, 150, 255)
                seg_fill = (132, 136, 142, 255)
            faces.append({'points': coords_world, 'massing_fill': massing_fill, 'seg_fill': seg_fill, 'outline': (255, 255, 255, 60)})

    projected_faces: list[dict[str, Any]] = []
    for face in faces:
        projected_points: list[tuple[float, float]] = []
        depths: list[float] = []
        for point in face['points']:
            projected = _project(point)
            if projected is None:
                projected_points = []
                break
            projected_points.append((projected[0], projected[1]))
            depths.append(projected[2])
        if len(projected_points) >= 3:
            projected_faces.append({
                'points': projected_points,
                'avg_depth': sum(depths) / len(depths),
                'massing_fill': face['massing_fill'],
                'seg_fill': face['seg_fill'],
                'outline': face['outline'],
            })

    if not projected_faces:
        return None

    min_depth = min(face['avg_depth'] for face in projected_faces)
    max_depth = max(face['avg_depth'] for face in projected_faces)
    depth_span = max(max_depth - min_depth, 1.0)

    massing = Image.new('RGBA', (image_width, image_height), (18, 22, 28, 255))
    segmentation = Image.new('RGBA', (image_width, image_height), (20, 22, 28, 255))
    depth = Image.new('L', (image_width, image_height), 18)
    massing_draw = ImageDraw.Draw(massing, 'RGBA')
    segmentation_draw = ImageDraw.Draw(segmentation, 'RGBA')
    depth_draw = ImageDraw.Draw(depth)

    for face in sorted(projected_faces, key=lambda item: item['avg_depth'], reverse=True):
        depth_ratio = 1.0 - ((face['avg_depth'] - min_depth) / depth_span)
        depth_value = int(42 + depth_ratio * 196)
        massing_draw.polygon(face['points'], fill=face['massing_fill'])
        segmentation_draw.polygon(face['points'], fill=face['seg_fill'])
        depth_draw.polygon(face['points'], fill=depth_value)
        massing_draw.line(face['points'] + [face['points'][0]], fill=face['outline'], width=1)

    depth_rgba = Image.merge('RGBA', (depth, depth, depth, Image.new('L', (image_width, image_height), 255)))
    structure = Image.blend(massing, depth_rgba, 0.18)
    structure_draw = ImageDraw.Draw(structure, 'RGBA')
    for face in sorted(projected_faces, key=lambda item: item['avg_depth'], reverse=True):
        structure_draw.line(face['points'] + [face['points'][0]], fill=(255, 255, 255, 96), width=1)

    return {
        'perspective_structure_image_url': _png_data_uri(_preview_png(structure, target_width=1200)),
        'perspective_depth_map_url': _png_data_uri(_preview_png(depth, target_width=1200)),
        'perspective_segmentation_map_url': _png_data_uri(_preview_png(segmentation, target_width=1200)),
        'perspective_massing_image_url': _png_data_uri(_preview_png(massing, target_width=1200)),
        'camera_perspective': selected_perspective,
    }
def _source_concept_image(option: Any) -> tuple[str | None, str | None]:
    metadata = getattr(option, "metadata_", None) or {}
    assets = metadata.get("assets") if isinstance(metadata, dict) else {}
    if isinstance(assets, dict):
        source_url = (
            assets.get("plan_full_png_url")
            or assets.get("plan_preview_png_url")
            or assets.get("preview_png_url")
            or getattr(option, "preview_url", None)
        )
        source_asset_id = assets.get("source_asset_id")
        return source_url, source_asset_id
    return getattr(option, "preview_url", None), None


def _source_conditioning_assets(option: Any) -> dict[str, Any] | None:
    metadata = getattr(option, 'metadata_', None) or {}
    assets = metadata.get('assets') if isinstance(metadata, dict) else {}
    control_meta = metadata.get('control_maps') if isinstance(metadata, dict) else {}
    if not isinstance(assets, dict):
        return None
    payload = {
        'structure_image_url': assets.get('control_structure_png_url'),
        'depth_map_url': assets.get('control_depth_png_url'),
        'segmentation_map_url': assets.get('control_segmentation_png_url'),
        'massing_image_url': assets.get('control_massing_png_url'),
        'control_mode': control_meta.get('conditioning_mode') if isinstance(control_meta, dict) else None,
        'control_strength': control_meta.get('control_strength') if isinstance(control_meta, dict) else None,
    }
    if any(payload.get(key) for key in ('structure_image_url', 'depth_map_url', 'segmentation_map_url', 'massing_image_url')):
        return payload
    return None
def _zone_archetype(zone: Any, properties: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    archetype_metadata: dict[str, Any] = {}
    if isinstance(properties.get("archetype_metadata"), dict):
        archetype_metadata.update(properties["archetype_metadata"])
    generation_style_input = properties.get("generation_style_input")
    if isinstance(generation_style_input, dict):
        archetype_metadata.setdefault("generation_style_input", generation_style_input)
    generation_style_inputs = properties.get("generation_style_inputs")
    if isinstance(generation_style_inputs, dict):
        archetype_metadata.setdefault("generation_style_inputs", generation_style_inputs)

    title_candidates = [
        properties.get("archetype_title"),
        properties.get("development_archetype_label"),
        properties.get("road_archetype_label"),
        properties.get("green_space_archetype_label"),
        properties.get("plaza_archetype_label"),
        getattr(zone, "name", None),
    ]
    archetype_title = next((_normalize_whitespace(item) for item in title_candidates if _normalize_whitespace(item)), "Mixed-Use Urban Development")
    archetype_metadata["resolved_archetype_title"] = archetype_title
    return archetype_title, archetype_metadata


def _resolve_height_and_floors(zone: Any, properties: dict[str, Any], skipped_zones: list[dict[str, Any]]) -> tuple[float, int]:
    zone_id = str(getattr(zone, "zone_id", getattr(zone, "id", "")) or "")
    zone_label = getattr(zone, "name", None)

    height_raw = None
    for key in ("height", "height_m"):
        if key in properties and properties[key] not in (None, ""):
            height_raw = properties[key]
            break
    floor_raw = None
    for key in ("floors", "floor_count", "floorCount"):
        if key in properties and properties[key] not in (None, ""):
            floor_raw = properties[key]
            break

    try:
        height_m = float(height_raw) if height_raw is not None else 24.0
    except (TypeError, ValueError):
        height_m = 24.0
    try:
        floor_count = int(float(floor_raw)) if floor_raw is not None else 6
    except (TypeError, ValueError):
        floor_count = 6

    if height_raw is None or floor_raw is None or height_m <= 0 or floor_count <= 0:
        height_m = 24.0 if height_m <= 0 else height_m
        floor_count = 6 if floor_count <= 0 else floor_count
        skipped_zones.append(
            {
                "zone_id": zone_id,
                "zone_label": zone_label,
                "reason": "Missing zone height/floor metadata; defaulted this zone to 24m over 6 levels.",
            }
        )
    return float(height_m), int(floor_count)


def _build_3d_from_2d_prompt(
    *,
    selected_perspective: str,
    selected_lighting: str,
    aesthetic_category: str,
    city_context: str,
    height_m: float,
    floor_count: int,
    architectural_language: str,
    facade_materials: str,
    roof_style: str,
    landscape_character: str,
    paving_type: str,
    global_style_payload: str,
    specific_overrides: str | None,
    critical_directive: str | None,
) -> str:
    intro = PERSPECTIVE_LEADS.get(selected_perspective, PERSPECTIVE_LEADS["aerial_oblique"])
    lighting_text = LIGHTING_VARIANTS.get(selected_lighting, LIGHTING_VARIANTS["golden_hour"])
    lines = [
        intro,
        "Create this as the same approved development from the selected 2D concept image, preserving site composition, podium placement, tower placement, courtyard organization, path structure, and public realm hierarchy.",
        f"Camera/viewpoint: {selected_perspective}.",
        f"Lighting/atmosphere: {selected_lighting} ({lighting_text}).",
        f"Render the proposal as an {aesthetic_category} mixed-use development in {city_context}, with approximately {height_m:.1f} m / {floor_count} storey residential towers over an active retail podium.",
        "Maintain the same massing logic, same tower locations, same podium edges, same open-space structure, and same urban design intent shown in the approved 2D concept.",
        f"Architectural language: {architectural_language}. Materials and expression: {facade_materials}, {roof_style}, integrated balcony planting, planted terraces, refined concrete, contemporary glazing, and high-quality detailing.",
        f"Ground-level public realm: {landscape_character}; paving language: {paving_type}; include active retail edges, canopies, widened sidewalks, street trees, and a lush internal courtyard.",
        "The final image should feel premium, realistic, and coherent. Do not invent a different site plan or unrelated building arrangement.",
        global_style_payload,
    ]
    override = _normalize_whitespace(specific_overrides)
    if override:
        lines.append(f"Critical directive: {override}")
    directive = _normalize_whitespace(critical_directive)
    if directive:
        lines.append(f"Critical Directive: {_ensure_sentence(directive)}")
    lines.append(
        "Do not generate any presentation-board elements or overlays. No title, labels, legend, callout markers, north arrow, scale bar, or text."
    )
    return "\n\n".join(lines)


def _master_plan_3d_avoid_terms() -> list[str]:
    return [term.strip() for term in THREE_D_NEGATIVE_PROMPT.split(",") if term.strip()]


def _build_master_plan_3d_response(
    project: Any,
    option: Any,
    boundary: Polygon,
    zones: Sequence[Any],
    buildings: Sequence[Any],
    request: MasterPlan3DGenerateRequest,
) -> dict[str, Any]:
    _ = buildings
    if boundary is None or boundary.is_empty:
        raise ValueError("Cannot prepare 3D render packages without a valid site boundary.")

    selected_ids = [str(value) for value in request.selected_zone_ids]
    if request.scope in {"selected_zones", "focused_frontage"}:
        zone_candidates = [zone for zone in zones if str(getattr(zone, "zone_id", getattr(zone, "id", ""))) in selected_ids]
    else:
        zone_candidates = list(zones)
    if not zone_candidates:
        raise ValueError("No eligible zones with valid geometry were available to generate 3D render packages.")

    style_notes = _dedupe_sentences(
        [
            request.global_style_notes,
            (getattr(option, "metadata_", {}) or {}).get("prompt") if isinstance(getattr(option, "metadata_", {}), dict) else None,
            getattr(project, "default_style", None),
        ]
    )
    global_style_payload = compile_style_matrix_prompt(
        render_style_preset=request.render_style_preset,
        lighting_atmosphere_preset=request.lighting_atmosphere_preset,
        specific_overrides=request.specific_overrides,
        legacy_global_style_notes=style_notes,
    )
    provider = _normalize_provider(
        str(getattr(settings, "master_plan_3d_image_provider", MASTER_PLAN_3D_PROVIDER_DEFAULT)),
        default="stability",
    )
    source_concept_image_url, source_concept_asset_id = _source_concept_image(option)
    conditioning_assets = _source_conditioning_assets(option)
    skipped_zones: list[dict[str, Any]] = []
    render_packages: list[dict[str, Any]] = []

    for zone in zone_candidates:
        zone_id = str(getattr(zone, "zone_id", getattr(zone, "id", "")))
        zone_label = _normalize_whitespace(getattr(zone, "name", None)) or "Unnamed Zone"
        zone_type = _normalize_zone_type(getattr(zone, "zone_type", None))
        geometry = _polygon_from_geometry(getattr(zone, "geometry", None))
        if geometry is None:
            skipped_zones.append({"zone_id": zone_id, "zone_label": zone_label, "reason": "Zone geometry is missing or invalid."})
            continue
        clipped, clip_error = _clip_zone_polygon_to_boundary(geometry, boundary)
        if clipped is None:
            raise ValueError(clip_error or f"Zone {zone_id} could not be clipped to the site boundary.")

        properties = _extract_zone_properties(zone, skipped_zones)
        height_m, floor_count = _resolve_height_and_floors(zone, properties, skipped_zones)
        archetype_title, archetype_metadata = _zone_archetype(zone, properties)
        user_note = _normalize_whitespace(properties.get("user_notes") or properties.get("description_text"))

        architectural_language = _normalize_whitespace(
            archetype_metadata.get("generation_style_input", {}).get("styleProfile", {}).get("massing")
            if isinstance(archetype_metadata.get("generation_style_input"), dict)
            else None
        ) or "contemporary mixed-use architectural language"
        facade_materials = _normalize_whitespace(
            archetype_metadata.get("generation_style_input", {}).get("styleProfile", {}).get("materials")
            if isinstance(archetype_metadata.get("generation_style_input"), dict)
            else None
        ) or "refined concrete and glazing"
        roof_style = _normalize_whitespace(
            archetype_metadata.get("generation_style_input", {}).get("styleProfile", {}).get("roofForm")
            if isinstance(archetype_metadata.get("generation_style_input"), dict)
            else None
        ) or "articulated urban roof expression"
        landscape_character = _normalize_whitespace(
            archetype_metadata.get("generation_style_input", {}).get("styleProfile", {}).get("plantingType")
            if isinstance(archetype_metadata.get("generation_style_input"), dict)
            else None
        ) or "layered landscape structure"
        paving_type = _normalize_whitespace(
            archetype_metadata.get("generation_style_input", {}).get("styleProfile", {}).get("pavingType")
            if isinstance(archetype_metadata.get("generation_style_input"), dict)
            else None
        ) or "high-quality public-realm paving"

        render_prompt = _build_3d_from_2d_prompt(
            selected_perspective=request.selected_perspective,
            selected_lighting=request.lighting_variant,
            aesthetic_category=_normalize_whitespace(archetype_metadata.get("generation_style_input", {}).get("aestheticCategoryLabel") if isinstance(archetype_metadata.get("generation_style_input"), dict) else None) or "eco-urban",
            city_context=_extract_city_context(project, []),
            height_m=height_m,
            floor_count=floor_count,
            architectural_language=architectural_language,
            facade_materials=facade_materials if isinstance(facade_materials, str) else "refined concrete and glazing",
            roof_style=roof_style,
            landscape_character=landscape_character,
            paving_type=paving_type,
            global_style_payload=global_style_payload,
            specific_overrides=request.specific_overrides,
            critical_directive=user_note,
        )

        package_conditioning_assets = dict(conditioning_assets or {}) if isinstance(conditioning_assets, dict) else {}
        perspective_conditioning_assets = _render_perspective_conditioning_assets(
            boundary,
            zone_candidates,
            primary_zone_id=zone_id,
            selected_perspective=request.selected_perspective,
        )
        if perspective_conditioning_assets:
            package_conditioning_assets.update(perspective_conditioning_assets)
            package_conditioning_assets["control_mode"] = (
                "orthographic_source_plus_camera_controls"
                if package_conditioning_assets.get("structure_image_url")
                else "camera_controls_only"
            )
            package_conditioning_assets["control_strength"] = max(float(package_conditioning_assets.get("control_strength") or 0.0), 0.84)

        coords = [[float(x), float(y)] for x, y in list(clipped.exterior.coords)]
        package = {
            "scene_id": f"{str(option.id)}:{zone_id}",
            "zone_id": zone_id,
            "zone_label": zone_label,
            "zone_type": zone_type,
            "archetype_title": archetype_title,
            "height_m": float(height_m),
            "floor_count": int(floor_count),
            "footprint_reference": {
                "source_zone_label": zone_label,
                "geometry_type": "Polygon",
            },
            "footprint_geometry": {
                "type": "Polygon",
                "coordinates": [coords],
            },
            "archetype_metadata": archetype_metadata,
            "user_notes": user_note,
            "render_prompt": render_prompt,
            "renderer_notes": {
                "keep_footprint_alignment": True,
                "recommended_condition_strength": float(package_conditioning_assets.get("control_strength") or 0.82),
                "geometry_priority": "high",
                "style_override_applied": bool(style_notes or request.specific_overrides),
                "avoid": _master_plan_3d_avoid_terms(),
            },
            "source_concept_image_url": source_concept_image_url,
            "source_concept_asset_id": source_concept_asset_id,
            "conditioning_assets": package_conditioning_assets or None,
            "provider": provider,
            "model": STABILITY_3D_MODEL if provider == "stability" else "vertex-architectural-3d",
            "prompt_type": "3d_from_2d",
            "job_type": "3d",
            "render_image_url": None,
        }
        render_packages.append(package)

    if not render_packages:
        raise ValueError("No eligible zones with valid geometry were available to generate 3D render packages.")

    has_camera_conditioning = any(
        isinstance(package.get("conditioning_assets"), dict)
        and package["conditioning_assets"].get("perspective_structure_image_url")
        for package in render_packages
    )

    return {
        "site_id": str(getattr(project, "id")),
        "option_id": str(getattr(option, "id")),
        "source_option_label": getattr(option, "label", "Master Plan Option"),
        "selected_perspective": request.selected_perspective,
        "lighting_variant": request.lighting_variant,
        "scope": request.scope,
        "selected_zone_ids": selected_ids,
        "global_style_notes": (style_notes[:-1] if style_notes.endswith(".") else style_notes) or None,
        "render_style_preset": request.render_style_preset,
        "lighting_atmosphere_preset": request.lighting_atmosphere_preset,
        "specific_overrides": request.specific_overrides,
        "global_style_payload": global_style_payload,
        "source_concept_image_url": source_concept_image_url,
        "provider_routing": {
            "two_d_image_provider": _normalize_provider(
                str(getattr(settings, "master_plan_2d_image_provider", MASTER_PLAN_2D_PROVIDER_DEFAULT)),
                default="vertex",
            ),
            "three_d_image_provider": provider,
        },
        "render_packages": render_packages,
        "skipped_zones": skipped_zones,
        "renderer_adapter": {
            "status": "ready",
            "provider": provider,
            "integration_status": "camera_conditioned_packages_ready" if has_camera_conditioning else "conditioned_packages_ready" if conditioning_assets else "structured_packages_ready",
            "notes": "3D packages preserve approved 2D footprint geometry and include camera-aware control images for the selected perspective." if has_camera_conditioning else "3D packages preserve approved 2D footprint geometry and include control-image assets for conditioned provider execution." if conditioning_assets else "3D packages preserve approved 2D footprint geometry and are ready for provider execution.",
        },
        "created_at": _now_utc(),
    }


class MasterPlan2DService:
    """Service layer for deterministic 2D master-plan options and 2D->3D packaging."""

    @staticmethod
    async def list_options(db: AsyncSession, project_id: uuid.UUID) -> list[MasterPlan2DOption]:
        result = await db.execute(
            select(MasterPlan2DOption)
            .where(MasterPlan2DOption.project_id == project_id)
            .order_by(MasterPlan2DOption.variant_index.asc(), MasterPlan2DOption.created_at.asc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def generate_options(
        db: AsyncSession,
        project: Project,
        zones: Sequence[SiteZone],
        buildings: Sequence[Building],
        request: MasterPlan2DGenerateRequest,
    ) -> list[MasterPlan2DOption]:
        if not zones:
            raise ValueError("At least one site zone is required before generating master-plan options.")
        scene_payload = _collect_scene_payload(project, zones, buildings)
        toggles = {
            "show_legend": request.show_legend if request.show_legend is not None else True,
            "show_north_arrow": request.show_north_arrow if request.show_north_arrow is not None else True,
            "show_scale_bar": request.show_scale_bar if request.show_scale_bar is not None else True,
            "show_callout_markers": request.show_callout_markers if request.show_callout_markers is not None else True,
            "show_surrounding_context": request.show_surrounding_context if request.show_surrounding_context is not None else True,
        }
        scene = _prepare_scene(scene_payload, int(request.export_width), toggles)

        requested_style = request.style_preset or "auto"
        if requested_style == "auto":
            style_sequence = DEFAULT_STYLE_SEQUENCE
        else:
            style_sequence = [requested_style]

        reference_images = request.reference_images or request.selected_image_urls or []
        sanitized_reference_metadata = _sanitize_reference_metadata_bundle(
            [item.model_dump() if hasattr(item, "model_dump") else dict(item) for item in (request.reference_metadata or [])]
        )

        city_context = _extract_city_context(project, zones)
        style_brief = _resolve_zone_design_brief(zones)
        avg_height, avg_floors = _resolve_height_floor_defaults(zones)
        global_style_payload = compile_style_matrix_prompt(
            render_style_preset=request.render_style_preset,
            lighting_atmosphere_preset=request.lighting_atmosphere_preset,
            specific_overrides=request.specific_overrides,
            legacy_global_style_notes=request.prompt,
        )

        option_count = int(request.option_count)
        await db.execute(delete(MasterPlan2DOption).where(MasterPlan2DOption.project_id == project.id))
        await db.flush()

        created: list[MasterPlan2DOption] = []
        for index in range(option_count):
            style_preset = style_sequence[index % len(style_sequence)]
            compiled_prompt = _build_2d_site_image_prompt(
                city_context=city_context,
                aesthetic_category=style_brief["aesthetic_category"],
                height_m=avg_height,
                floor_count=avg_floors,
                architectural_language=style_brief["architectural_language"],
                facade_materials=style_brief["facade_materials"],
                roof_style=style_brief["roof_style"],
                landscape_character=style_brief["landscape_character"],
                paving_type=style_brief["paving_type"],
                global_style_payload=global_style_payload,
            )
            rendered = _render_variant_assets(
                getattr(project, "name", "Master Plan"),
                scene,
                style_preset,
                toggles,
                compiled_prompt,
                reference_images,
                sanitized_reference_metadata,
                request.quality_level or "presentation",
                index,
                bool(request.debug),
                compose_board=bool(request.compose_board),
                board_template=request.board_template or "master_plan_board_v1",
                include_photo_strip=bool(request.include_photo_strip),
                ai_style_pass_enabled=bool(request.ai_style_pass_enabled),
                ai_style_pass_provider=request.ai_style_pass_provider or "auto",
                render_style_preset=request.render_style_preset,
                lighting_atmosphere_preset=request.lighting_atmosphere_preset,
                map_screenshot_satellite=request.map_screenshot_satellite,
            )

            full_png_uri = _png_data_uri(rendered["full_png"])
            preview_png_uri = _png_data_uri(rendered["preview_png"])
            plan_full_png_uri = _png_data_uri(rendered["plan_full_png"])
            plan_preview_png_uri = _png_data_uri(rendered["plan_preview_png"])
            svg_uri = _svg_data_uri(rendered["svg"])
            plan_svg_uri = _svg_data_uri(rendered["plan_svg"])
            control_map_payload = rendered.get("control_maps") if isinstance(rendered, dict) else {}
            control_images = control_map_payload.get("images") if isinstance(control_map_payload, dict) else {}
            control_assets: dict[str, str] = {}
            if isinstance(control_images, dict):
                for key, image in control_images.items():
                    if isinstance(image, Image.Image):
                        control_assets[f"control_{key}_png_url"] = _png_data_uri(_preview_png(image, target_width=1200))
            control_map_summary = {
                "available": bool(control_assets),
                "conditioning_mode": control_map_payload.get("conditioning_mode") if isinstance(control_map_payload, dict) else None,
                "control_strength": control_map_payload.get("control_strength") if isinstance(control_map_payload, dict) else None,
                "maps": sorted(list(control_images.keys())) if isinstance(control_images, dict) else [],
            }

            assets = {
                "preview_png_url": preview_png_uri,
                "full_png_url": full_png_uri,
                "svg_url": svg_uri,
                "plan_preview_png_url": plan_preview_png_uri,
                "plan_full_png_url": plan_full_png_uri,
                "plan_svg_url": plan_svg_uri,
                "debug_png_url": None,
                "source_asset_id": f"{project.id}:{index}",
                **control_assets,
            }
            metadata = {
                "prompt": _normalize_whitespace(request.prompt) or None,
                "compiled_prompt": compiled_prompt,
                "negative_prompt": _build_2d_negative_prompt(),
                "render_style_preset": request.render_style_preset,
                "lighting_atmosphere_preset": request.lighting_atmosphere_preset,
                "specific_overrides": request.specific_overrides,
                "global_style_payload": global_style_payload,
                "provider": _normalize_provider(
                    str(getattr(settings, "master_plan_2d_image_provider", MASTER_PLAN_2D_PROVIDER_DEFAULT)),
                    default="vertex",
                ),
                "model": str(getattr(settings, "gemini_2d_image_model", "") or "gemini-3-pro-image-preview"),
                "prompt_type": "2d_site_image",
                "job_type": "2d",
                "assets": assets,
                "board": rendered["board"],
                "style_guide": rendered["style_guide"],
                "ai_style_pass": rendered["ai_style_pass"],
                "context_underlay": rendered["context_underlay"],
                "control_maps": control_map_summary,
                "reference_images": list(reference_images),
                "reference_metadata": sanitized_reference_metadata,
                "width": scene["width"],
                "height": scene["height"],
                "geometry_hash": scene["geometry_hash"],
            }

            option = MasterPlan2DOption(
                project_id=project.id,
                label=f"Version {chr(ord('A') + index)}",
                style_preset=style_preset,
                variant_index=index,
                preview_url=preview_png_uri,
                plan_svg=rendered["plan_svg"],
                metadata_=metadata,
                is_selected=index == 0,
            )
            db.add(option)
            created.append(option)

        await db.commit()
        for option in created:
            await db.refresh(option)
        return created

    @staticmethod
    async def select_option(db: AsyncSession, project_id: uuid.UUID, option_id: uuid.UUID) -> MasterPlan2DOption:
        result = await db.execute(
            select(MasterPlan2DOption).where(
                MasterPlan2DOption.project_id == project_id,
                MasterPlan2DOption.id == option_id,
            )
        )
        selected = result.scalar_one_or_none()
        if selected is None:
            raise ValueError("2D master plan option not found")

        await db.execute(update(MasterPlan2DOption).where(MasterPlan2DOption.project_id == project_id).values(is_selected=False))
        await db.execute(update(MasterPlan2DOption).where(MasterPlan2DOption.id == option_id).values(is_selected=True))
        await db.commit()
        await db.refresh(selected)
        return selected

    @staticmethod
    async def generate_3d_render_packages(
        db: AsyncSession,
        project: Project,
        option_id: uuid.UUID,
        zones: Sequence[SiteZone],
        buildings: Sequence[Building],
        request: MasterPlan3DGenerateRequest,
    ) -> dict[str, Any]:
        result = await db.execute(
            select(MasterPlan2DOption).where(
                MasterPlan2DOption.id == option_id,
                MasterPlan2DOption.project_id == project.id,
            )
        )
        option = result.scalar_one_or_none()
        if option is None:
            raise ValueError("2D master plan option not found")

        if request.zones:
            snapshot_zones = _zone_snapshots_from_request(request)
        else:
            snapshot_zones = []
            for idx, zone in enumerate(zones):
                zone_geometry = _polygon_from_geometry(getattr(zone, "geometry", None))
                if zone_geometry is None:
                    continue
                properties = getattr(zone, "properties", None) if isinstance(getattr(zone, "properties", None), dict) else {}
                snapshot_zones.append(
                    ZoneSnapshot(
                        zone_id=str(getattr(zone, "id")),
                        zone_type=_normalize_zone_type(getattr(zone, "zone_type", None)),
                        name=_normalize_whitespace(getattr(zone, "name", None)) or f"Zone {idx + 1}",
                        color=str(getattr(zone, "color", "#9b59b6")),
                        geometry=zone_geometry,
                        properties=properties,
                        sort_order=int(getattr(zone, "sort_order", idx)),
                        created_at=getattr(zone, "created_at", None),
                    )
                )
        boundary = _boundary_from_snapshot_zones(snapshot_zones)
        if boundary is None:
            raise ValueError("No eligible zones with valid geometry were available to generate 3D render packages.")

        response = _build_master_plan_3d_response(project, option, boundary, snapshot_zones, buildings, request)
        return response

    @staticmethod
    async def export_option(db: AsyncSession, option_id: uuid.UUID, width: int) -> dict[str, Any]:
        result = await db.execute(select(MasterPlan2DOption).where(MasterPlan2DOption.id == option_id))
        option = result.scalar_one_or_none()
        if option is None:
            raise ValueError("2D master plan option not found")
        metadata = option.metadata_ or {}
        assets = metadata.get("assets") if isinstance(metadata, dict) else {}
        if not isinstance(assets, dict):
            assets = {}
        height = int(metadata.get("height") or round(width * (2.0 / 3.0)))
        svg = option.plan_svg or "<svg xmlns='http://www.w3.org/2000/svg'></svg>"
        return {
            "option": option,
            "style_name": STYLE_LABELS.get(option.style_preset, option.style_preset.replace("_", " ").title()),
            "width": int(width),
            "height": height,
            "svg": svg,
            "preview_png_url": assets.get("preview_png_url") or option.preview_url,
            "full_png_url": assets.get("full_png_url"),
            "svg_url": assets.get("svg_url"),
            "plan_preview_png_url": assets.get("plan_preview_png_url"),
            "plan_full_png_url": assets.get("plan_full_png_url"),
            "plan_svg_url": assets.get("plan_svg_url"),
            "debug_png_url": assets.get("debug_png_url"),
        }


__all__ = [
    "MasterPlan2DService",
    "STYLE_LABELS",
    "_boundary_from_snapshot_zones",
    "_build_ai_style_pass_prompt",
    "_build_master_plan_3d_response",
    "_compose_ai_style_pass",
    "_generate_precinct_footprints",
    "_park_program_geometries",
    "_prepare_scene",
    "_render_variant_assets",
    "_sanitize_reference_metadata_bundle",
    "_tree_points",
    "_zone_snapshots_from_request",
]


