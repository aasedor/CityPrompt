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
from shapely.geometry import GeometryCollection, LineString, MultiLineString, MultiPolygon, Point, Polygon, box
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
FAL_DEFAULT_STYLE_MODEL = "fal-ai/fast-sdxl/image-to-image"

MASTER_PLAN_2D_PROVIDER_DEFAULT = "vertex"
MASTER_PLAN_3D_PROVIDER_DEFAULT = "vertex"
MASTER_PLAN_2D_RENDER_MODE_DEFAULT = "orthographic_aerial_site_insert"
MASTER_PLAN_2D_RENDER_MODES = {"orthographic_aerial_site_insert", "legacy_prompt_first"}

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

# =============================================================================
# Render style catalog — maps style keys to AI style pass parameters
# =============================================================================

RENDER_STYLE_CATALOG: dict[str, dict[str, Any]] = {
    "photorealistic_aerial": {
        "label": "Photorealistic Aerial",
        "description": "Drone-photograph realism with accurate materials and natural lighting",
        "category": "realistic",
        "prompt": (
            "photorealistic aerial photograph of completed urban development, drone photography, "
            "natural daylight, realistic material textures, high resolution architectural photography, "
            "sharp building edges, real vegetation, asphalt roads, concrete sidewalks"
        ),
        "negative_prompt": "illustration, painting, cartoon, sketch, stylized, watercolor, flat colors, diagram",
        "denoising_strength": 0.25,
        "compositing_blend": 0.55,
        "provider_preference": "gemini",
        "palette_overrides": {},
    },
    "photoreal_orthographic_aerial": {
        "label": "Orthographic Aerial",
        "description": "True top-down plan view with photorealistic materials and crisp shadows",
        "category": "realistic",
        "prompt": (
            "orthographic aerial architectural site visualization, true top-down camera, "
            "realistic roofs, paving textures, tree canopy, parking geometry, "
            "sharp natural shadows, cool neutral tones, professional architectural photography"
        ),
        "negative_prompt": "illustration, painting, sketch, diagram, washed out, side view",
        "denoising_strength": 0.25,
        "compositing_blend": 0.50,
        "provider_preference": "gemini",
        "palette_overrides": {},
    },
    "digital_watercolor_map": {
        "label": "Digital Watercolor",
        "description": "Elegant vellum-textured plan with architectural color palette",
        "category": "artistic",
        "prompt": (
            "professional architectural illustration on textured vellum, "
            "sophisticated desaturated palette, opaque textures with 3D drop shadows, "
            "clean line-weight hierarchy, elegant paving, readable roof plans, top-down canopy"
        ),
        "negative_prompt": "photorealistic, 3D render, cartoon, faded, ghosting",
        "denoising_strength": 0.40,
        "compositing_blend": 0.55,
        "provider_preference": "gemini",
        "palette_overrides": {},
    },
    "watercolor_wash": {
        "label": "Watercolor Wash",
        "description": "Soft hand-painted washes with visible brushwork — warm and approachable",
        "category": "artistic",
        "prompt": (
            "watercolor architectural masterplan, hand-painted, wet-on-wet washes, "
            "soft bleeding edges, visible paper texture, muted earth tones, loose brushwork, "
            "light pencil underdrawing, architectural illustration, warm approachable atmosphere, "
            "granulation from pigment settling, white paper highlights showing through"
        ),
        "negative_prompt": "photorealistic, sharp edges, digital, 3D render, glossy, saturated colors, neon",
        "denoising_strength": 0.50,
        "compositing_blend": 0.60,
        "provider_preference": "gemini",
        "palette_overrides": {
            "paper": "#f5efe6",
            "building": "#c4b5a0",
            "shadow": "#8a7e70",
            "park": "#7a9a6a",
            "road": "#b8b0a4",
            "path": "#d6cfc2",
            "water": "#8aacbe",
        },
    },
    "ink_line_drawing": {
        "label": "Ink Line Drawing",
        "description": "Black ink on white paper with hatching — precise yet human",
        "category": "artistic",
        "prompt": (
            "architectural ink line drawing, hand-drawn sketch, pen and ink on white paper, "
            "varied line weight, cross-hatching for shadows, confident loose strokes, "
            "architectural masterplan sketch, stippling for texture, no color fills"
        ),
        "negative_prompt": "photorealistic, color, painted, digital render, smooth gradients, 3D, watercolor",
        "denoising_strength": 0.65,
        "compositing_blend": 0.70,
        "provider_preference": "gemini",
        "palette_overrides": {
            "paper": "#ffffff",
            "building": "#1a1a1a",
            "shadow": "#444444",
            "park": "#c8c8c8",
            "road": "#3a3a3a",
            "path": "#888888",
            "water": "#aaaaaa",
        },
    },
    "marker_render": {
        "label": "Marker Render",
        "description": "Bold Prismacolor/Copic marker strokes with saturated fills",
        "category": "artistic",
        "prompt": (
            "marker rendering, architectural illustration, Prismacolor markers, Copic marker style, "
            "hand-drawn ink outlines, saturated color fills, visible brush strokes, "
            "architectural presentation board quality, white paper highlights, bold confident style"
        ),
        "negative_prompt": "photorealistic, digital, 3D render, watercolor, pencil, muted colors, pastel",
        "denoising_strength": 0.55,
        "compositing_blend": 0.60,
        "provider_preference": "gemini",
        "palette_overrides": {
            "paper": "#fefcf8",
            "building": "#9a8a78",
            "shadow": "#4a4040",
            "park": "#2d8a28",
            "road": "#5a5a60",
            "path": "#d4c8b8",
            "water": "#2878b0",
        },
    },
    "cinematic_dusk": {
        "label": "Cinematic Dusk",
        "description": "Dramatic blue hour with warm interior glows and wet reflections",
        "category": "realistic",
        "prompt": (
            "cinematic architectural rendering at dusk, blue hour, warm interior lighting glowing from windows, "
            "wet street reflections, atmospheric fog, dramatic indigo sky, moody urban scene, "
            "professional architectural photography, golden hour to blue hour transition, "
            "amber street lamp pools, deep blue shadows"
        ),
        "negative_prompt": "daytime, bright, flat lighting, cartoon, illustration, overexposed, washed out",
        "denoising_strength": 0.45,
        "compositing_blend": 0.57,
        "provider_preference": "gemini",
        "palette_overrides": {
            "paper": "#1a2030",
            "building": "#3a4050",
            "shadow": "#0a0e18",
            "park": "#1a3020",
            "road": "#2a2a35",
            "path": "#3a3840",
            "water": "#152030",
            "accent": "#e8a840",
        },
    },
    "collage_mixed_media": {
        "label": "Collage / Mixed Media",
        "description": "Layered photographic cutouts with flat color and hand-drawn marks",
        "category": "artistic",
        "prompt": (
            "architectural collage, mixed media, cut-out photographs, flat color shapes, "
            "hand-drawn annotations, layered composition, post-digital architecture illustration, "
            "textured paper background, eclectic palette, photographic textures for vegetation, "
            "bold graphic shapes for buildings"
        ),
        "negative_prompt": "photorealistic, uniform style, 3D render, smooth, clinical, single medium",
        "denoising_strength": 0.60,
        "compositing_blend": 0.65,
        "provider_preference": "gemini",
        "palette_overrides": {},
    },
    "lush_landscape": {
        "label": "Lush Landscape",
        "description": "Nature-forward with dense vegetation, green roofs, and sunlit canopy",
        "category": "realistic",
        "prompt": (
            "lush green urban masterplan, abundant mature vegetation, dense tree canopy cover, "
            "bioswales, green roofs, sustainable urbanism, aerial view, bright sunlit atmosphere, "
            "nature-integrated architecture, rich foliage variety, landscape architecture rendering, "
            "dappled light through trees, flower beds, garden paths"
        ),
        "negative_prompt": "barren, concrete, grey, industrial, winter, dead trees, sparse, parking lots",
        "denoising_strength": 0.50,
        "compositing_blend": 0.60,
        "provider_preference": "gemini",
        "palette_overrides": {
            "park": "#3a8a30",
            "path": "#c8be9a",
            "water": "#4a90b0",
        },
    },
    "white_massing_model": {
        "label": "White Massing Model",
        "description": "Monochrome clay/foam model emphasizing pure form and shadow",
        "category": "technical",
        "prompt": (
            "white architectural massing model, clay render, monochrome, "
            "soft ambient occlusion shadows, physical scale model appearance, "
            "foam board model, clean minimal, aerial view, no materials no textures, "
            "uniform white surfaces, subtle grey shadows"
        ),
        "negative_prompt": "color, materials, texture, photorealistic, people, vegetation, detailed, busy",
        "denoising_strength": 0.20,
        "compositing_blend": 0.45,
        "provider_preference": "gemini",
        "palette_overrides": {
            "paper": "#f0f0f0",
            "building": "#e8e8e8",
            "shadow": "#999999",
            "park": "#d8d8d8",
            "road": "#cccccc",
            "path": "#dddddd",
            "water": "#c0c0c0",
            "site": "#e4e4e4",
        },
    },
    "flat_diagrammatic": {
        "label": "Flat Diagrammatic",
        "description": "Bold infographic colors, clean zones, no gradients — data-forward",
        "category": "technical",
        "prompt": "",  # No AI pass for this style
        "negative_prompt": "",
        "denoising_strength": 0.0,  # No AI pass
        "compositing_blend": 0.0,
        "provider_preference": "none",
        "palette_overrides": {
            "paper": "#f8f9fa",
            "building": "#6b7280",
            "shadow": "#9ca3af",
            "park": "#22c55e",
            "road": "#374151",
            "path": "#d1d5db",
            "water": "#3b82f6",
            "site": "#fef3c7",
            "accent": "#ef4444",
        },
    },
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

STYLE_PASS_NEGATIVE_PROMPT = "side view, facade sheet, elevation, front-facing perspective, collage board, floating annotations, legends, title blocks, north arrow, scale bar"

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

VIEW_FAMILY_DIRECTIVES: dict[str, str] = {
    "aerial_oblique": "Show the full district as a coherent neighborhood, with the civic green or water anchor visible and the surrounding suburban fabric still readable.",
    "street_level_eye_height": "Frame an active mixed-use main street with podium frontage, retail transparency, trees, sidewalks, seating, cyclists, and believable pedestrian scale.",
    "corner_perspective": "Use a corner-framing camera that clarifies street-wall alignment, podium edges, and the transition from major frontage to quieter side streets.",
    "promenade_view": "Focus on the park, water edge, or promenade as a premium public realm sequence surrounded by coherent building massing.",
}


def _view_family_directive(selected_perspective: str) -> str:
    return VIEW_FAMILY_DIRECTIVES.get(selected_perspective, VIEW_FAMILY_DIRECTIVES["aerial_oblique"])


def _coords_to_line(coords: Sequence[Sequence[float]] | None) -> LineString | None:
    if not isinstance(coords, Sequence):
        return None
    points: list[tuple[float, float]] = []
    for item in coords:
        if not isinstance(item, Sequence) or len(item) < 2:
            continue
        try:
            points.append((float(item[0]), float(item[1])))
        except (TypeError, ValueError):
            continue
    if len(points) < 2:
        return None
    return LineString(points)


def _coords_to_polygon(coords: Sequence[Sequence[float]] | None) -> Polygon | None:
    if not isinstance(coords, Sequence):
        return None
    points: list[tuple[float, float]] = []
    for item in coords:
        if not isinstance(item, Sequence) or len(item) < 2:
            continue
        try:
            points.append((float(item[0]), float(item[1])))
        except (TypeError, ValueError):
            continue
    if len(points) < 3:
        return None
    if points[0] != points[-1]:
        points.append(points[0])
    try:
        polygon = Polygon(points)
    except Exception:
        return None
    return _polygon_from_geometry(polygon)


def _append_osm_context_layers(scene: dict[str, Any], boundary: Polygon | None, osm_context: dict[str, Any]) -> None:
    if not isinstance(osm_context, dict):
        return

    def outside_site(poly: Polygon | None) -> bool:
        if poly is None:
            return False
        if boundary is None or boundary.is_empty:
            return True
        try:
            return not boundary.contains(poly.representative_point())
        except Exception:
            return True

    for road in osm_context.get("roads", []) or []:
        geometry = _coords_to_line(road.get("coordinates"))
        if geometry is None:
            continue
        scene["context_roads"].append(
            {
                "geometry": geometry,
                "kind": "context_road",
                "width_m": float(road.get("width_m") or 6.0),
                "properties": {"source": "osm", "road_type": road.get("road_type"), "name": road.get("name")},
            }
        )

    for item in osm_context.get("buildings", []) or []:
        poly = _coords_to_polygon(item.get("coordinates"))
        if poly is None or not outside_site(poly):
            continue
        scene["context_buildings"].append(
            {
                "geometry": poly,
                "name": item.get("name"),
                "properties": {
                    "source": "osm",
                    "building_type": item.get("building_type"),
                    "height_m": item.get("height_m"),
                },
            }
        )

    for item in osm_context.get("parks", []) or []:
        poly = _coords_to_polygon(item.get("coordinates"))
        if poly is None or not outside_site(poly):
            continue
        scene["context_parks"].append(
            {
                "geometry": poly,
                "name": item.get("name"),
                "properties": {"source": "osm", "park_type": item.get("park_type")},
            }
        )

    for item in osm_context.get("water", []) or []:
        poly = _coords_to_polygon(item.get("coordinates"))
        if poly is None or not outside_site(poly):
            continue
        scene["context_water"].append(
            {
                "geometry": poly,
                "name": item.get("name"),
                "properties": {"source": "osm", "water_type": item.get("water_type")},
            }
        )


DEFAULT_STYLE_TOGGLES = {
    "show_legend": True,
    "show_north_arrow": True,
    "show_scale_bar": True,
    "show_callout_markers": True,
    "show_surrounding_context": True,
}

STYLE_PALETTES: dict[str, dict[str, str]] = {
    "rendered_sales_plan": {
        "paper": "#f0ede4",
        "site": "#c8c4b8",
        "building": "#a8a098",
        "shadow": "#484a46",
        "park": "#5aa04a",
        "road": "#8a8680",
        "path": "#c4bca8",
        "water": "#5a98bc",
        "accent": "#136f8d",
    },
    "hybrid_annotated_master_plan": {
        "paper": "#f2f0ea",
        "site": "#c6c4ba",
        "building": "#a4a098",
        "shadow": "#454740",
        "park": "#58a048",
        "road": "#888480",
        "path": "#c2b8a4",
        "water": "#5b98bb",
        "accent": "#0a6d8c",
    },
    "illustrative_landscape_plan": {
        "paper": "#f0ece2",
        "site": "#c4c0b4",
        "building": "#a6a098",
        "shadow": "#585550",
        "park": "#5aa04a",
        "road": "#8a8678",
        "path": "#d0c6ae",
        "water": "#6aa0c8",
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


def _normalize_provider(
    value: str | None, *, default: Literal["vertex", "stability", "gemini"]
) -> Literal["vertex", "stability", "gemini"]:
    token = str(value or "").strip().lower()
    if token in {"vertex", "stability", "gemini"}:
        return token  # type: ignore[return-value]
    return default


def _normalize_render_mode(value: str | None) -> str:
    token = str(value or "").strip().lower()
    if token in MASTER_PLAN_2D_RENDER_MODES:
        return token
    return MASTER_PLAN_2D_RENDER_MODE_DEFAULT


def _map_bounds_polygon(bounds: Any) -> Polygon | None:
    payload = bounds.model_dump() if hasattr(bounds, "model_dump") else bounds
    if not isinstance(payload, dict):
        return None
    try:
        west = float(payload.get("west"))
        south = float(payload.get("south"))
        east = float(payload.get("east"))
        north = float(payload.get("north"))
    except (TypeError, ValueError):
        return None
    if not all(math.isfinite(value) for value in (west, south, east, north)):
        return None
    if east <= west or north <= south:
        return None
    return box(west, south, east, north)


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


def _safe_to_shape(value: Any) -> BaseGeometry | None:  # noqa: C901
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


def _extract_linestrings(geometry: Any) -> list[LineString]:
    """Extract all LineString segments from any geometry type.

    Handles LineString, MultiLineString, GeometryCollection, and nested collections.
    This fixes a critical bug where `LineString.intersection(Polygon)` returns a
    GeometryCollection and the LineStrings inside are silently dropped.
    """
    if geometry is None:
        return []
    if isinstance(geometry, LineString) and not geometry.is_empty:
        return [geometry]
    if isinstance(geometry, MultiLineString):
        return [ls for ls in geometry.geoms if isinstance(ls, LineString) and not ls.is_empty]
    if hasattr(geometry, "geoms"):
        # GeometryCollection or other multi-types
        result: list[LineString] = []
        for g in geometry.geoms:
            if isinstance(g, LineString) and not g.is_empty:
                result.append(g)
            elif isinstance(g, MultiLineString):
                result.extend(ls for ls in g.geoms if isinstance(ls, LineString) and not ls.is_empty)
        return result
    return []


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


def _polygon_coordinates_wgs84(polygon: Polygon | None) -> list[list[float]] | None:
    if polygon is None or polygon.is_empty:
        return None
    return [[round(float(x), 8), round(float(y), 8)] for x, y in polygon.exterior.coords]


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

    # Use separate X/Y scales to match Mapbox Web Mercator projection.
    # A degree of longitude is shorter than a degree of latitude at most latitudes.
    center_lat = (miny + maxy) / 2.0
    meters_per_deg_lon = _meters_per_degree_lon(center_lat)
    meters_per_deg_lat = _meters_per_degree_lat(center_lat)
    # Convert degree extents to approximate meter extents
    dx_m = dx * meters_per_deg_lon
    dy_m = dy * meters_per_deg_lat
    # Find a uniform meters-to-pixels scale that fits both axes
    scale_m = min(usable_w / max(dx_m, 1e-3), usable_h / max(dy_m, 1e-3))
    # Derive per-axis degree-to-pixel scales
    scale_x = scale_m * meters_per_deg_lon
    scale_y = scale_m * meters_per_deg_lat
    # Centre features in canvas when one axis has leftover space
    used_w = dx * scale_x
    used_h = dy * scale_y
    offset_x = margin + (usable_w - used_w) / 2.0
    offset_y = margin + (usable_h - used_h) / 2.0

    def to_px(x: float, y: float) -> tuple[float, float]:
        px = offset_x + (x - minx) * scale_x
        py = height - offset_y - (y - miny) * scale_y
        return (px, py)

    def geom_to_px(geometry: BaseGeometry) -> BaseGeometry:
        if isinstance(geometry, Polygon):
            exterior = [to_px(x, y) for x, y in geometry.exterior.coords]
            interiors = [[to_px(x, y) for x, y in ring.coords] for ring in geometry.interiors]
            return Polygon(exterior, interiors)
        if isinstance(geometry, MultiPolygon):
            return MultiPolygon([geom_to_px(poly) for poly in geometry.geoms if isinstance(poly, Polygon)])
        if isinstance(geometry, MultiLineString):
            return MultiLineString([geom_to_px(ls) for ls in geometry.geoms if isinstance(ls, LineString)])
        if isinstance(geometry, LineString):
            return LineString([to_px(x, y) for x, y in geometry.coords])
        if isinstance(geometry, Point):
            x, y = to_px(geometry.x, geometry.y)
            return Point(x, y)
        # GeometryCollection fallback — transform each sub-geometry
        if hasattr(geometry, "geoms"):
            transformed = [geom_to_px(g) for g in geometry.geoms]
            if transformed:
                return transformed[0] if len(transformed) == 1 else geometry.__class__(transformed)
        return geometry

    px_per_meter = scale_m  # Already in pixels-per-meter
    transform = {
        "minx": minx,
        "miny": miny,
        "maxx": maxx,
        "maxy": maxy,
        "scale": scale_m,
        "scale_x": scale_x,
        "scale_y": scale_y,
        "margin": margin,
        "to_px": to_px,
        "geom_to_px": geom_to_px,
    }
    return transform, px_per_meter


def _resolve_scene_view_extent(
    boundary: Polygon,
    payload: dict[str, Any],
    *,
    render_mode: str,
    map_screenshot_bounds: Any,
) -> Polygon:
    if _normalize_render_mode(render_mode) != MASTER_PLAN_2D_RENDER_MODE_DEFAULT:
        return boundary

    screenshot_extent = _map_bounds_polygon(map_screenshot_bounds)
    if screenshot_extent is not None:
        return screenshot_extent

    minx, miny, maxx, maxy = boundary.bounds
    dx = max(maxx - minx, 1e-9)
    dy = max(maxy - miny, 1e-9)
    extent = box(minx - dx * 0.30, miny - dy * 0.30, maxx + dx * 0.30, maxy + dy * 0.30)

    context_geometries: list[BaseGeometry] = []
    for feature in payload.get("context_buildings", []) or []:
        poly = _polygon_from_geometry(feature.get("geometry"))
        if poly is not None and not poly.is_empty:
            context_geometries.append(poly)
    for feature in payload.get("context_parks", []) or []:
        poly = _polygon_from_geometry(feature.get("geometry"))
        if poly is not None and not poly.is_empty:
            context_geometries.append(poly)
    for feature in payload.get("context_water", []) or []:
        poly = _polygon_from_geometry(feature.get("geometry"))
        if poly is not None and not poly.is_empty:
            context_geometries.append(poly)
    for feature in payload.get("context_roads", []) or []:
        geometry = _safe_to_shape(feature.get("geometry"))
        if geometry is None or geometry.is_empty:
            continue
        if isinstance(geometry, LineString):
            width_m = max(float(feature.get("width_m") or 6.0), 2.0)
            lat = float(boundary.centroid.y)
            degrees = width_m / max((_meters_per_degree_lat(lat) + _meters_per_degree_lon(lat)) / 2.0, 1.0)
            context_geometries.append(geometry.buffer(max(degrees * 0.9, 1e-5), cap_style=2, join_style=2))
        else:
            context_geometries.append(geometry)

    if context_geometries:
        expanded = _polygon_from_geometry(unary_union([extent, *context_geometries]).envelope)
        if expanded is not None and not expanded.is_empty:
            # Cap expansion so context doesn't push the site too small
            max_extent = box(minx - dx * 0.55, miny - dy * 0.55, maxx + dx * 0.55, maxy + dy * 0.55)
            extent = _polygon_from_geometry(expanded.intersection(max_extent)) or extent

    return extent


def _prepare_scene(
    payload: dict[str, Any],
    export_width: int,
    toggles: dict[str, bool],
    *,
    render_mode: str | None = None,
    map_screenshot_bounds: Any = None,
) -> dict[str, Any]:
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

    mode = _normalize_render_mode(render_mode)
    view_extent = _resolve_scene_view_extent(
        boundary,
        payload,
        render_mode=mode,
        map_screenshot_bounds=map_screenshot_bounds,
    )

    width = int(max(export_width, 1200))
    # Match canvas aspect ratio to view_extent so satellite and projected features align.
    # Previously forced 3:2, which caused features to shift when satellite had different aspect.
    ve_minx, ve_miny, ve_maxx, ve_maxy = view_extent.bounds
    ve_dx = max(ve_maxx - ve_minx, 1e-9)
    ve_dy = max(ve_maxy - ve_miny, 1e-9)
    # Approximate geo-extent aspect ratio (account for latitude-dependent x-stretch)
    center_lat = (ve_miny + ve_maxy) / 2.0
    lat_stretch = max(math.cos(math.radians(center_lat)), 0.3)
    geo_aspect = (ve_dx * lat_stretch) / ve_dy  # width / height in real-world metres
    # Clamp to reasonable bounds so we never get extreme aspect ratios
    geo_aspect = max(0.6, min(geo_aspect, 2.5))
    height = int(round(width / geo_aspect))
    # Ensure even dimensions for image encoding compatibility
    height = max(height, 800)
    if height % 2:
        height += 1
    transform, pixels_per_meter = _project_geometry_to_pixels(view_extent, width, height)
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
    pixel_view_extent = geom_to_px(view_extent)
    geometry_hash = _scene_geometry_hash(boundary, raw_layers)
    prompt_zones = list(payload.get("prompt_zones") or [])
    return {
        "width": width,
        "height": height,
        "boundary": boundary,
        "view_extent": view_extent,
        "render_mode": mode,
        "pixel": {
            "boundary": pixel_boundary,
            "view_extent": pixel_view_extent,
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
        floors = int(
            float(properties.get("floors") or properties.get("floor_count") or properties.get("floorCount") or 0)
        )
    except (TypeError, ValueError):
        floors = 0
    return bool(area_m2 >= 2800 or (max_dim >= 60 and min_dim >= 25) or (floors >= 6 and area_m2 >= 2000))


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
        base["paper"] = _blend_hex(base["paper"], "#e4e8e4", 0.35)
        base["site"] = _blend_hex(base["site"], "#a8b0a6", 0.45)
        base["building"] = _blend_hex(base["building"], "#7a8288", 0.55)
        base["shadow"] = _blend_hex(base["shadow"], "#141e28", 0.55)
        base["park"] = _blend_hex(base["park"], "#3a7830", 0.50)
        base["road"] = _blend_hex(base["road"], "#5a6268", 0.55)
        base["path"] = _blend_hex(base["path"], "#a8a094", 0.35)
        base["water"] = _blend_hex(base["water"], "#3a6890", 0.50)
    elif render_key == "photorealistic_aerial":
        base["paper"] = _blend_hex(base["paper"], "#ece8e0", 0.20)
        base["site"] = _blend_hex(base["site"], "#b0aea4", 0.35)
        base["building"] = _blend_hex(base["building"], "#8a8478", 0.45)
        base["shadow"] = _blend_hex(base["shadow"], "#202830", 0.40)
        base["park"] = _blend_hex(base["park"], "#408830", 0.42)
        base["road"] = _blend_hex(base["road"], "#6a6860", 0.35)
        base["water"] = _blend_hex(base["water"], "#407898", 0.38)
    elif render_key == "digital_watercolor_map":
        base = _apply_palette_bias(base, "#f7f3ea", 0.12, keys=["paper", "site", "building", "road", "path"])
        base["park"] = _blend_hex(base["park"], "#98b283", 0.25)
        base["water"] = _blend_hex(base["water"], "#88acc5", 0.18)

    # Apply palette overrides from render style catalog (new styles)
    catalog_entry = RENDER_STYLE_CATALOG.get(render_key, {})
    overrides = catalog_entry.get("palette_overrides", {})
    if overrides:
        for key, hex_color in overrides.items():
            if key in base:
                # Blend strongly toward the override color
                base[key] = _blend_hex(base[key], hex_color, 0.75)
            else:
                base[key] = hex_color

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
    render_mode: str | None = None,
) -> dict[str, Any]:
    render_key = str(render_style_preset or "photorealistic_aerial").strip().lower()
    lighting_key = str(lighting_atmosphere_preset or "crisp_summer_day").strip().lower()
    hash_seed = int(
        hashlib.sha256(f"{geometry_hash}:{style_preset}:{render_key}:{lighting_key}".encode("utf-8")).hexdigest()[:12],
        16,
    )
    layout_seed = hash_seed % 1_000_000
    style_seed = (hash_seed + variant_index * 977) % 1_000_000
    quality_boost = {"draft": 0.9, "presentation": 1.0, "board_ready": 1.08}.get(quality_level, 1.0)
    photoreal = render_key in {"photorealistic_aerial", "photoreal_orthographic_aerial"}
    orthographic = render_key == "photoreal_orthographic_aerial"
    mode = _normalize_render_mode(render_mode)
    site_insert_mode = mode == MASTER_PLAN_2D_RENDER_MODE_DEFAULT

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
        "draft": 2400,
        "presentation": 4800,
        "board_ready": 7200,
    }.get(quality_level, 4800)
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
        "render_mode": mode,
        "site_insert_mode": site_insert_mode,
        "photoreal_mode": photoreal,
        "orthographic_mode": orthographic,
        "shadow_offset": shadow_offset,
        "tree_shadow_offset": (shadow_offset[0] * 0.55, shadow_offset[1] * 0.55),
        "shadow_blur": shadow_blur,
        "shadow_alpha": 180 if orthographic else 165 if photoreal else 140,
        "context_alpha": (
            214 if site_insert_mode and orthographic else 198 if orthographic else 178 if photoreal else 150
        ),
        "roof_detail_alpha": 118 if orthographic else 92 if photoreal else 60,
        "roof_detail_lines": 4 if orthographic else 3 if photoreal else 2,
        "rooftop_unit_count": 4 if orthographic else 3 if photoreal else 2,
        "building_edge_alpha": 160 if orthographic else 130 if photoreal else 100,
        "lane_marking_alpha": 150 if orthographic else 122 if photoreal else 88,
        "lane_marking_width": 2 if orthographic else 1,
        "park_texture_points": 420 if orthographic else 320 if photoreal else 180,
        "tree_shadow_alpha": 120 if orthographic else 100 if photoreal else 75,
        "water_edge_alpha": 122 if orthographic else 100 if photoreal else 70,
        "surface_texture_points": base_texture_points,
        "contrast_boost": 1.15 if orthographic else 1.12 if photoreal else 1.05,
        "color_boost": 1.12 if lighting_key != "overcast_soft" else 0.98,
        "brightness_boost": 1.04 if lighting_key == "winter_snow" else 1.0,
        "sharpness_boost": 1.20 if orthographic else 1.12 if photoreal else 1.04,
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


def _tree_points(
    geometry: Polygon, properties: dict[str, Any], variant: dict[str, Any]
) -> list[tuple[float, float, float, str]]:
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

    tree_types = ["deciduous_round", "deciduous_spread", "conifer"]
    tree_cum_weights = [0.55, 0.85, 1.0]

    points: list[tuple[float, float, float, str]] = []
    for row in range(rows):
        for col in range(cols):
            if len(points) >= target_count:
                break
            x = minx + (col + 0.5) * step_x + rng.uniform(-0.22, 0.22) * step_x
            y = miny + (row + 0.5) * step_y + rng.uniform(-0.22, 0.22) * step_y
            pt = Point(x, y)
            if not geometry.buffer(1e-9).contains(pt):
                continue
            radius = max(min(step_x, step_y) * 0.65 * size_multiplier * rng.uniform(0.7, 1.3), 3.5)
            # Assign tree type
            r = rng.random()
            tree_type = tree_types[0]
            for i, cw in enumerate(tree_cum_weights):
                if r <= cw:
                    tree_type = tree_types[i]
                    break
            points.append((x, y, radius, tree_type))
    return points


def _park_program_geometries(
    geometry: Polygon, properties: dict[str, Any], variant: dict[str, Any]
) -> list[tuple[str, BaseGeometry]]:
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


def _line_feature(
    geometry: BaseGeometry | None, *, width_m: float, properties: dict[str, Any] | None = None, kind: str = "path"
) -> dict[str, Any] | None:
    shape = _safe_to_shape(geometry)
    if shape is None or shape.is_empty:
        return None
    return {
        "geometry": shape,
        "kind": kind,
        "width_m": float(width_m),
        "properties": dict(properties or {}),
    }


def _polygon_feature(
    geometry: BaseGeometry | None, *, name: str | None = None, properties: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    poly = _polygon_from_geometry(geometry)
    if poly is None or poly.is_empty:
        return None
    return {
        "geometry": poly,
        "name": name,
        "properties": dict(properties or {}),
    }


def _generate_precinct_site_features(
    zone_geometry: Polygon,
    footprints: Sequence[dict[str, Any]],
    *,
    zone_name: str | None,
    zone_properties: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    features: dict[str, list[dict[str, Any]]] = {
        "roads": [],
        "paths": [],
        "parks": [],
        "plazas": [],
        "water": [],
    }
    center_lat = zone_geometry.centroid.y
    meters_lon = _meters_per_degree_lon(center_lat)
    meters_lat = _meters_per_degree_lat(center_lat)
    meters_per_degree = max((meters_lon + meters_lat) / 2.0, 1.0)

    zone_width_m, zone_height_m = _geometry_extent_m(zone_geometry)
    min_dim_m = max(min(zone_width_m, zone_height_m), 1.0)
    inset_distance_m = max(min(min_dim_m * 0.045, 12.0), 2.0)
    inset_distance_deg = inset_distance_m / meters_per_degree
    usable = _polygon_from_geometry(zone_geometry.buffer(-inset_distance_deg))
    if usable is None:
        usable = zone_geometry

    footprint_polys = [
        poly
        for poly in (_polygon_from_geometry(item.get("geometry")) for item in footprints)
        if poly is not None and not poly.is_empty
    ]
    if not footprint_polys:
        return features

    built_union = unary_union(footprint_polys).buffer(0)
    open_area_geom = usable.difference(built_union)
    open_area = _polygon_from_geometry(open_area_geom)
    if open_area is None:
        open_area = usable

    width_deg = usable.bounds[2] - usable.bounds[0]
    height_deg = usable.bounds[3] - usable.bounds[1]
    width_m = abs(width_deg) * meters_lon
    height_m = abs(height_deg) * meters_lat
    min_dim_m = max(min(width_m, height_m), 1.0)
    center_x = (usable.bounds[0] + usable.bounds[2]) / 2
    center_y = (usable.bounds[1] + usable.bounds[3]) / 2
    zone_area_m2 = zone_geometry.area * meters_lon * meters_lat

    def area_m2(geometry: BaseGeometry | None) -> float:
        shape = _safe_to_shape(geometry)
        if shape is None or shape.is_empty:
            return 0.0
        return float(shape.area) * meters_lon * meters_lat

    def meters_to_degrees(distance_m: float) -> float:
        return float(distance_m) / meters_per_degree

    # Primary streets: E-W drive + N-S pedestrian spine
    east_west = LineString([(usable.bounds[0], center_y), (usable.bounds[2], center_y)]).intersection(usable)
    north_south = LineString([(center_x, usable.bounds[1]), (center_x, usable.bounds[3])]).intersection(usable)
    for geometry, width_m_value, kind in (
        (east_west, max(min_dim_m * 0.08, 5.5), "internal_drive"),
        (north_south, max(min_dim_m * 0.05, 3.0), "pedestrian_spine"),
    ):
        feature = _line_feature(
            geometry,
            width_m=width_m_value,
            properties={"generated": True, "kind": kind},
            kind="road" if "drive" in kind else "path",
        )
        if feature is None:
            continue
        if feature["kind"] == "road":
            features["roads"].append(feature)
        else:
            features["paths"].append(feature)

    # Secondary streets: quarter-lines for larger sites to create block structure
    if zone_area_m2 > 8000:
        quarter_positions = [0.30, 0.70]
        for frac in quarter_positions:
            sec_x = usable.bounds[0] + width_deg * frac
            sec_y = usable.bounds[1] + height_deg * frac
            # E-W secondary lane
            sec_ew = LineString([(usable.bounds[0], sec_y), (usable.bounds[2], sec_y)]).intersection(usable)
            feat = _line_feature(
                sec_ew,
                width_m=max(min_dim_m * 0.04, 3.5),
                properties={"generated": True, "kind": "secondary_lane"},
                kind="road",
            )
            if feat is not None:
                features["roads"].append(feat)
            # N-S secondary lane
            sec_ns = LineString([(sec_x, usable.bounds[1]), (sec_x, usable.bounds[3])]).intersection(usable)
            feat = _line_feature(
                sec_ns,
                width_m=max(min_dim_m * 0.035, 3.0),
                properties={"generated": True, "kind": "secondary_lane"},
                kind="path",
            )
            if feat is not None:
                features["paths"].append(feat)

    # Diagonal paths connecting corners for pedestrian permeability
    corners = [
        (usable.bounds[0] + width_deg * 0.15, usable.bounds[1] + height_deg * 0.15),
        (usable.bounds[0] + width_deg * 0.85, usable.bounds[1] + height_deg * 0.15),
        (usable.bounds[0] + width_deg * 0.85, usable.bounds[3] - height_deg * 0.15),
        (usable.bounds[0] + width_deg * 0.15, usable.bounds[3] - height_deg * 0.15),
    ]
    diag_a = LineString([corners[0], (center_x, center_y)]).intersection(usable)
    diag_b = LineString([corners[1], (center_x, center_y)]).intersection(usable)
    for diag_geom in (diag_a, diag_b):
        feat = _line_feature(
            diag_geom,
            width_m=max(min_dim_m * 0.025, 2.0),
            properties={"generated": True, "kind": "pedestrian_link"},
            kind="path",
        )
        if feat is not None:
            features["paths"].append(feat)

    promenade_outer = meters_to_degrees(max(min_dim_m * 0.035, 2.2))
    promenade_inner = meters_to_degrees(max(min_dim_m * 0.015, 1.1))
    promenade_ring = _polygon_from_geometry(
        built_union.buffer(promenade_outer).difference(built_union.buffer(promenade_inner))
    )
    if promenade_ring is not None and area_m2(promenade_ring) > 40.0:
        plaza_feature = _polygon_feature(
            promenade_ring.intersection(usable),
            name=f"{zone_name or 'Precinct'} promenade",
            properties={"generated": True, "surface": "promenade"},
        )
        if plaza_feature is not None:
            features["plazas"].append(plaza_feature)

    description = _normalize_whitespace(zone_properties.get("description_text")).lower()
    anchor_candidate = _polygon_from_geometry(
        box(
            center_x - width_deg * 0.18,
            center_y - height_deg * 0.16,
            center_x + width_deg * 0.18,
            center_y + height_deg * 0.16,
        ).intersection(open_area_geom)
    )
    if anchor_candidate is not None and area_m2(anchor_candidate) > max(zone_area_m2 * 0.04, 160.0):
        anchor_park = _polygon_feature(
            anchor_candidate,
            name=f"{zone_name or 'Precinct'} civic green",
            properties={
                "generated": True,
                "tree_density_level": "medium",
                "tree_density": 0.20,
                "has_paths": True,
                "landscape_role": "civic_anchor",
            },
        )
        if anchor_park is not None:
            features["parks"].append(anchor_park)
        if ("pond" in description or "water" in description or zone_area_m2 > 1200.0) and area_m2(
            anchor_candidate
        ) > 120.0:
            pond = _polygon_from_geometry(
                Point(center_x, center_y).buffer(meters_to_degrees(min_dim_m * 0.11)).intersection(anchor_candidate)
            )
            pond_feature = _polygon_feature(
                pond,
                name=f"{zone_name or 'Precinct'} water anchor",
                properties={"generated": True, "surface": "water_feature"},
            )
            if pond_feature is not None:
                features["water"].append(pond_feature)

    courtyard_buffer_deg = meters_to_degrees(max(min_dim_m * 0.03, 1.8))
    courtyard = _polygon_from_geometry(open_area.buffer(-courtyard_buffer_deg))
    if courtyard is not None and area_m2(courtyard) > max(zone_area_m2 * 0.06, 180.0):
        park_feature = _polygon_feature(
            courtyard,
            name=f"{zone_name or 'Precinct'} courtyard",
            properties={
                "generated": True,
                "tree_density_level": "dense",
                "tree_density": 0.24,
                "has_paths": True,
                "description_text": zone_properties.get("description_text") or "Generated internal courtyard landscape",
            },
        )
        if park_feature is not None:
            features["parks"].append(park_feature)
    elif area_m2(open_area) > max(zone_area_m2 * 0.08, 120.0):
        park_feature = _polygon_feature(
            open_area,
            name=f"{zone_name or 'Precinct'} open space",
            properties={"generated": True, "tree_density_level": "medium", "tree_density": 0.16, "has_paths": True},
        )
        if park_feature is not None:
            features["parks"].append(park_feature)

    if not features["parks"] and any(
        token in description for token in ("courtyard", "park", "green", "plaza", "promenade", "public realm")
    ):
        fallback_anchor = _polygon_from_geometry(
            Point(center_x, center_y).buffer(meters_to_degrees(max(min_dim_m * 0.14, 8.0))).intersection(open_area_geom)
        )
        if fallback_anchor is not None and area_m2(fallback_anchor) > 90.0:
            park_feature = _polygon_feature(
                fallback_anchor,
                name=f"{zone_name or 'Precinct'} civic green",
                properties={
                    "generated": True,
                    "tree_density_level": "medium",
                    "tree_density": 0.18,
                    "has_paths": True,
                    "landscape_role": "civic_anchor",
                },
            )
            if park_feature is not None:
                features["parks"].append(park_feature)

    if "parking" in description or "retail" in description or "mixed-use" in description or "mixed use" in description:
        pad_depth_deg = (max(height_m * 0.16, min_dim_m * 0.14)) / meters_lat
        parking_pad = box(
            usable.bounds[0] + width_deg * 0.06,
            usable.bounds[1] + height_deg * 0.72,
            usable.bounds[2] - width_deg * 0.06,
            usable.bounds[1] + height_deg * 0.72 + pad_depth_deg,
        )
        parking_feature = _polygon_feature(
            parking_pad.intersection(open_area_geom),
            name=f"{zone_name or 'Precinct'} forecourt",
            properties={"generated": True, "surface": "parking_court"},
        )
        if parking_feature is not None and area_m2(parking_feature["geometry"]) > 80.0:
            features["plazas"].append(parking_feature)

    return features


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

    # Park ground is lighter yellow-green (lawn) vs darker tree canopy green
    park_fill = _hex_to_rgba(_blend_hex(palette["park"], "#98c878", 0.40), 255)
    park_texture_dark = _hex_to_rgba(_blend_hex(palette["park"], "#2a4a28", 0.35), 55)
    park_texture_light = _hex_to_rgba(_blend_hex(palette["park"], "#c8e0b0", 0.30), 45)
    path_fill = _hex_to_rgba(palette["path"], 248)
    water_fill = _hex_to_rgba(palette["water"], 232)
    water_edge = _hex_to_rgba(_blend_hex(palette["water"], "#ffffff", 0.42), int(variant.get("water_edge_alpha") or 88))
    tree_shadow_fill = _hex_to_rgba(
        _blend_hex(palette["shadow"], "#000000", 0.28), int(variant.get("tree_shadow_alpha") or 64)
    )
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
                    # Ripple lines inside park water features
                    park_water_ripple = _hex_to_rgba(_blend_hex(palette["water"], "#ffffff", 0.22), 34)
                    pwminx, pwminy, pwmaxx, pwmaxy = program_geometry.bounds
                    pw_gap = max(3.0, min(6.0, (pwmaxy - pwminy) / 10))
                    pwy = pwminy + pw_gap
                    while pwy < pwmaxy:
                        ripple_seg = LineString([(pwminx - 1, pwy), (pwmaxx + 1, pwy)]).intersection(program_geometry)
                        if isinstance(ripple_seg, LineString) and not ripple_seg.is_empty:
                            _draw_line(draw, ripple_seg, park_water_ripple, width=1)
                        pwy += pw_gap
                else:
                    _draw_polygon(
                        draw, program_geometry, _hex_to_rgba(_blend_hex(palette["park"], "#cadab7", 0.12), 224)
                    )
            elif isinstance(program_geometry, LineString):
                width = 6 if kind == "promenade" else 4
                _draw_line(draw, program_geometry, path_fill, width=width)

        for x, y, radius, tree_type in _tree_points(geometry, park.get("properties") or {}, variant):
            sx = x + float(tree_shadow_offset[0])
            sy = y + float(tree_shadow_offset[1])
            shadow_radius = radius * 1.2
            shadow_draw.ellipse(
                (sx - shadow_radius, sy - shadow_radius, sx + shadow_radius, sy + shadow_radius), fill=tree_shadow_fill
            )
            tree_canopies.append((x, y, radius, tree_type))

    image.alpha_composite(texture_image.filter(ImageFilter.GaussianBlur(radius=0.45)))
    image.alpha_composite(
        shadow_image.filter(ImageFilter.GaussianBlur(radius=max(float(variant.get("shadow_blur") or 2.0) - 0.8, 1.2)))
    )

    # Multi-layer canopy rendering with tree type variation
    # Use strongly saturated greens — these must read as rich foliage, not pale dots
    canopy_greens = [
        _blend_hex("#3a7a3a", palette["park"], 0.20),  # dominant dark green
        _blend_hex("#2d6830", palette["park"], 0.15),  # forest green
        _blend_hex("#4a8848", palette["park"], 0.22),  # slightly lighter
        _blend_hex("#357035", palette["park"], 0.18),  # medium dark
        _blend_hex("#508a4a", palette["park"], 0.25),  # brightest variant
    ]
    conifer_green = _blend_hex("#1a3a1a", palette["park"], 0.10)
    tree_rng = random.Random(base_seed + 777)

    for x, y, radius, tree_type in tree_canopies:
        if tree_type == "conifer":
            # Single dark circle, smaller
            cr = radius * 0.65
            cfill = _hex_to_rgba(conifer_green, 240)
            draw.ellipse((x - cr, y - cr, x + cr, y + cr), fill=cfill)
            # Tiny trunk dot
            draw.ellipse((x - 1.0, y - 1.0, x + 1.0, y + 1.0), fill=_hex_to_rgba("#4a3a2a", 180))
        elif tree_type == "deciduous_spread":
            # Wider ellipse with dome-shaped radial gradient: dark rim → lighter center
            ew = radius * 1.3
            eh = radius * 0.85
            base_green = tree_rng.choice(canopy_greens)
            rim_green = _blend_hex(base_green, "#1a3018", 0.35)
            # Outer dark rim
            draw.ellipse((x - ew, y - eh, x + ew, y + eh), fill=_hex_to_rgba(rim_green, 240))
            # Inner lighter fill (80% of radius)
            draw.ellipse(
                (x - ew * 0.80, y - eh * 0.80, x + ew * 0.80, y + eh * 0.80), fill=_hex_to_rgba(base_green, 235)
            )
            # 3–4 sub-canopy blobs for texture
            for _ in range(tree_rng.randint(3, 4)):
                bx = x + tree_rng.uniform(-radius * 0.35, radius * 0.35)
                by = y + tree_rng.uniform(-radius * 0.25, radius * 0.25)
                br = radius * tree_rng.uniform(0.35, 0.65)
                blob_green = tree_rng.choice(canopy_greens)
                draw.ellipse(
                    (bx - br * 1.2, by - br * 0.8, bx + br * 1.2, by + br * 0.8), fill=_hex_to_rgba(blob_green, 210)
                )
            # Highlight center — simulates dome lit from above
            hx = x - radius * 0.12
            hy = y - radius * 0.12
            hr = radius * 0.38
            draw.ellipse(
                (hx - hr, hy - hr, hx + hr, hy + hr), fill=_hex_to_rgba(_blend_hex(base_green, "#a8d89a", 0.40), 100)
            )
        else:
            # deciduous_round — richest rendering: dome gradient + overlapping sub-canopy
            base_green = tree_rng.choice(canopy_greens)
            rim_green = _blend_hex(base_green, "#1a3018", 0.35)
            # Dark rim ring
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=_hex_to_rgba(rim_green, 245))
            # Inner lighter fill (75% of radius)
            inner_r = radius * 0.78
            draw.ellipse((x - inner_r, y - inner_r, x + inner_r, y + inner_r), fill=_hex_to_rgba(base_green, 240))
            # 3–5 overlapping sub-blobs for organic look
            blob_count = tree_rng.randint(3, 5)
            for _ in range(blob_count):
                bx = x + tree_rng.uniform(-radius * 0.30, radius * 0.30)
                by = y + tree_rng.uniform(-radius * 0.30, radius * 0.30)
                br = radius * tree_rng.uniform(0.40, 0.70)
                blob_green = tree_rng.choice(canopy_greens)
                draw.ellipse((bx - br, by - br, bx + br, by + br), fill=_hex_to_rgba(blob_green, 200))
            # Bright center highlight — dome lit from above
            hx = x - radius * 0.10
            hy = y - radius * 0.10
            hr = radius * 0.35
            draw.ellipse(
                (hx - hr, hy - hr, hx + hr, hy + hr), fill=_hex_to_rgba(_blend_hex(base_green, "#b8dca8", 0.38), 120)
            )


def _render_street_trees(
    image: Image.Image,
    scene: dict[str, Any],
    palette: dict[str, str],
    variant: dict[str, Any],
) -> None:
    """Add tree-lined streets by placing trees along road edges."""
    draw = ImageDraw.Draw(image, "RGBA")
    shadow_layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer, "RGBA")
    base_seed = int(variant.get("seed") or 0)
    rng = random.Random(base_seed + 9999)

    canopy_greens = [
        _blend_hex("#3a7a3a", palette["park"], 0.20),
        _blend_hex("#2d6830", palette["park"], 0.15),
        _blend_hex("#4a8848", palette["park"], 0.22),
        _blend_hex("#508a4a", palette["park"], 0.25),
    ]
    shadow_fill = _hex_to_rgba(_blend_hex(palette["shadow"], "#1a3018", 0.30), 100)

    ppm = float(scene.get("pixels_per_meter") or 1.0)
    tree_spacing = 8.0 * ppm  # 8m spacing
    tree_radius_min = 4.0 * ppm * 0.5
    tree_radius_max = 7.0 * ppm * 0.5

    for road in scene["pixel"].get("roads", []):
        geom = road.get("geometry")
        if geom is None:
            continue
        # Extract LineStrings from any geometry type (including GeometryCollection)
        raw_lines = _extract_linestrings(geom)
        if not raw_lines and isinstance(geom, Polygon):
            # Roads stored as buffered polygons — extract centerline approximation
            try:
                raw_lines.append(LineString([geom.centroid, Point(geom.bounds[2], geom.centroid.y)]))
            except Exception:
                pass
        for line in raw_lines:
            if line.is_empty or line.length < 2:
                continue
            road_width_px = float(road.get("width_m", 8.0)) * ppm
            offset_dist = road_width_px / 2 + 4.0 * ppm  # 4m from road edge

            for side in [1, -1]:
                try:
                    offset_line = line.parallel_offset(offset_dist * side, "left" if side > 0 else "right")
                except Exception:
                    continue
                if offset_line.is_empty:
                    continue
                # Extract LineStrings from parallel_offset result
                offset_segments = _extract_linestrings(offset_line)
                if not offset_segments:
                    continue

                for seg in offset_segments:
                    length = seg.length
                    dist = rng.uniform(0, tree_spacing * 0.3)
                    while dist < length:
                        pt = seg.interpolate(dist)
                        tx, ty = pt.x, pt.y
                        tr = rng.uniform(tree_radius_min, tree_radius_max)

                        # Shadow
                        sx, sy = tx + 2.5, ty + 3.0
                        sr = tr * 1.15
                        shadow_draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=shadow_fill)

                        # Canopy — strong green fill
                        base_green = rng.choice(canopy_greens)
                        draw.ellipse((tx - tr, ty - tr, tx + tr, ty + tr), fill=_hex_to_rgba(base_green, 235))
                        # 2 sub-blobs for texture variation
                        for _ in range(2):
                            bx = tx + rng.uniform(-tr * 0.25, tr * 0.25)
                            by = ty + rng.uniform(-tr * 0.25, tr * 0.25)
                            br = tr * rng.uniform(0.35, 0.60)
                            draw.ellipse(
                                (bx - br, by - br, bx + br, by + br), fill=_hex_to_rgba(rng.choice(canopy_greens), 210)
                            )

                        dist += tree_spacing * rng.uniform(0.85, 1.15)

    image.alpha_composite(shadow_layer.filter(ImageFilter.GaussianBlur(radius=1.8)))


def _render_ground_textures(
    image: Image.Image,
    scene: dict[str, Any],
    palette: dict[str, str],
    variant: dict[str, Any],
) -> None:
    """Add material textures to ground areas between buildings, roads, and parks."""
    draw = ImageDraw.Draw(image, "RGBA")
    ppm = float(scene.get("pixels_per_meter") or 1.0)
    base_seed = int(variant.get("seed") or 0)
    rng = random.Random(base_seed + 6789)

    boundary = _polygon_from_geometry(scene["pixel"].get("boundary"))
    if boundary is None:
        return

    # Collect all "occupied" areas (buildings, parks, roads, water, plazas, paths)
    occupied: list[BaseGeometry] = []
    for key in ("building_masses", "building_footprints", "parks", "plazas", "water"):
        for feature in scene["pixel"].get(key, []):
            geom = _polygon_from_geometry(feature.get("geometry"))
            if geom is not None:
                occupied.append(geom)
    for key in ("roads", "paths"):
        for feature in scene["pixel"].get(key, []):
            geom = feature.get("geometry")
            line_segs = _extract_linestrings(geom)
            if line_segs:
                w = float(feature.get("width_m", 6.0)) * ppm
                for ls in line_segs:
                    occupied.append(ls.buffer(max(w * 0.6, 3)))
            else:
                poly = _polygon_from_geometry(geom)
                if poly is not None:
                    occupied.append(poly)

    if not occupied:
        return

    try:
        occupied_union = unary_union(occupied).buffer(0)
        remaining = boundary.difference(occupied_union)
    except Exception as exc:
        logger.debug("Ground texture: geometry union failed: %s", exc)
        return
    remaining_poly = _polygon_from_geometry(remaining)
    if remaining_poly is None or remaining_poly.is_empty:
        return

    # --- Paving grid near buildings ---
    building_polys: list[Polygon] = []
    for key in ("building_masses", "building_footprints"):
        for feature in scene["pixel"].get(key, []):
            geom = _polygon_from_geometry(feature.get("geometry"))
            if geom is not None:
                building_polys.append(geom)

    paving_color = _hex_to_rgba(_blend_hex(palette.get("site", "#c0bab0"), "#808080", 0.25), 40)
    for bpoly in building_polys:
        try:
            paving_zone = bpoly.buffer(5 * ppm).intersection(remaining_poly)
        except Exception:
            continue
        pz = _polygon_from_geometry(paving_zone)
        if pz is None or pz.is_empty or pz.area < 20:
            continue
        pminx, pminy, pmaxx, pmaxy = pz.bounds
        spacing = max(3.0, 2.5 * ppm)
        # Horizontal paving lines
        py_val = pminy + spacing
        while py_val < pmaxy:
            seg = LineString([(pminx - 1, py_val), (pmaxx + 1, py_val)])
            try:
                clipped = seg.intersection(pz)
            except Exception:
                py_val += spacing
                continue
            if isinstance(clipped, LineString) and not clipped.is_empty:
                _draw_line(draw, clipped, paving_color, width=1)
            elif hasattr(clipped, "geoms"):
                for g in clipped.geoms:
                    if isinstance(g, LineString) and not g.is_empty:
                        _draw_line(draw, g, paving_color, width=1)
            py_val += spacing

    # --- Garden/planting beds in remaining open space ---
    garden_fill = _hex_to_rgba(_blend_hex(palette.get("park", "#5aa04a"), "#6a6048", 0.30), 75)
    minx, miny, maxx, maxy = remaining_poly.bounds
    for _ in range(min(20, max(3, int(remaining_poly.area / 3000)))):
        gx = rng.uniform(minx, maxx)
        gy = rng.uniform(miny, maxy)
        if not remaining_poly.buffer(1e-9).contains(Point(gx, gy)):
            continue
        gw = rng.uniform(3, 6) * ppm * 0.4
        gh = rng.uniform(2, 5) * ppm * 0.4
        draw.ellipse((gx - gw, gy - gh, gx + gw, gy + gh), fill=garden_fill)


def _render_setback_vegetation(
    image: Image.Image,
    scene: dict[str, Any],
    palette: dict[str, str],
    variant: dict[str, Any],
) -> None:
    """Add small shrub/hedge dots in setback areas between buildings and roads."""
    draw = ImageDraw.Draw(image, "RGBA")
    ppm = float(scene.get("pixels_per_meter") or 1.0)
    base_seed = int(variant.get("seed") or 0)
    rng = random.Random(base_seed + 4321)

    boundary = _polygon_from_geometry(scene["pixel"].get("boundary"))
    if boundary is None:
        return

    building_polys: list[Polygon] = []
    for key in ("building_masses", "building_footprints"):
        for feature in scene["pixel"].get(key, []):
            geom = _polygon_from_geometry(feature.get("geometry"))
            if geom is not None:
                building_polys.append(geom)

    if not building_polys:
        return

    shrub_greens = [
        _hex_to_rgba(_blend_hex(palette.get("park", "#5aa04a"), "#2a5828", 0.45), 140),
        _hex_to_rgba(_blend_hex(palette.get("park", "#5aa04a"), "#3a6838", 0.40), 130),
        _hex_to_rgba(_blend_hex(palette.get("park", "#5aa04a"), "#4a7848", 0.35), 120),
    ]

    # Road/path geometries for exclusion
    road_union_parts: list[BaseGeometry] = []
    for key in ("roads", "paths"):
        for feature in scene["pixel"].get(key, []):
            geom = feature.get("geometry")
            line_segs = _extract_linestrings(geom)
            if line_segs:
                w = float(feature.get("width_m", 6.0)) * ppm
                for ls in line_segs:
                    road_union_parts.append(ls.buffer(max(w * 0.5, 2)))
            else:
                poly = _polygon_from_geometry(geom)
                if poly is not None:
                    road_union_parts.append(poly)

    try:
        road_union = unary_union(road_union_parts).buffer(0) if road_union_parts else Polygon()
    except Exception as exc:
        logger.debug("Setback vegetation: road union failed: %s", exc)
        road_union = Polygon()

    for bpoly in building_polys:
        try:
            setback = bpoly.buffer(4 * ppm).difference(bpoly.buffer(1 * ppm))
            setback = setback.intersection(boundary)
            if not road_union.is_empty:
                setback = setback.difference(road_union)
        except Exception:
            continue

        setback_poly = _polygon_from_geometry(setback)
        if setback_poly is None or setback_poly.is_empty or setback_poly.area < 10:
            continue

        sminx, sminy, smaxx, smaxy = setback_poly.bounds
        shrub_count = min(30, max(3, int(setback_poly.area / max(200, 80 / max(ppm, 0.1)))))
        placed = 0
        for _ in range(shrub_count * 4):
            sx = rng.uniform(sminx, smaxx)
            sy = rng.uniform(sminy, smaxy)
            if not setback_poly.buffer(1e-9).contains(Point(sx, sy)):
                continue
            sr = rng.uniform(1.5, 3.5)
            color = rng.choice(shrub_greens)
            draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=color)
            placed += 1
            if placed >= shrub_count:
                break


def _classify_building_typology(props: dict[str, Any], height_m: float) -> str:
    """Classify a building into a roof typology for rendering."""
    grammar = str(props.get("generated_precinct_grammar", "")).lower()
    hint = str(props.get("description_text", "")).lower()
    dev_type = str(props.get("development_type", "")).lower()
    typology = str(props.get("building_typology", "")).lower()

    if "townhouse" in grammar or "townhouse" in hint or "townhouse" in typology or "rowhouse" in hint:
        return "townhouse"
    if "mixed_use" in grammar or "mixed_use" in dev_type or "mixed_use" in typology or "podium" in typology:
        return "mixed_use"
    if height_m > 20:
        return "highrise"
    if "perimeter" in grammar or "mid_rise" in typology or "apartment" in typology or 10 < height_m <= 20:
        return "midrise"
    if "office" in typology or "commercial" in dev_type or "retail" in typology:
        return "commercial"
    return "generic"


def _render_entourage(
    image: Image.Image,
    scene: dict[str, Any],
    palette: dict[str, str],
    variant: dict[str, Any],
) -> None:
    """Add people dots, cafe furniture, and moving cars for life and scale."""
    draw = ImageDraw.Draw(image, "RGBA")
    ppm = float(scene.get("pixels_per_meter") or 1.0)
    base_seed = int(variant.get("seed") or 0)
    rng = random.Random(base_seed + 11111)

    # People colors — warm tones suggesting clothing
    people_colors = [
        _hex_to_rgba("#3a3a4a", 200),  # dark jacket
        _hex_to_rgba("#6a3a2a", 190),  # brown
        _hex_to_rgba("#2a4a6a", 185),  # blue shirt
        _hex_to_rgba("#8a3a3a", 180),  # red top
        _hex_to_rgba("#e8d8c8", 175),  # light clothing
        _hex_to_rgba("#4a6a3a", 180),  # green jacket
    ]
    person_radius = max(1.5, ppm * 0.4)

    # People on paths
    for feature in scene["pixel"].get("paths", []):
        geom = feature.get("geometry")
        segments: list[LineString] = []
        if isinstance(geom, LineString):
            segments.append(geom)
        elif isinstance(geom, MultiLineString):
            segments.extend(ls for ls in geom.geoms if isinstance(ls, LineString))
        for seg in segments:
            spacing = max(15 * ppm, 20)
            dist = rng.uniform(0, spacing * 0.4)
            while dist < seg.length:
                if rng.random() < 0.35:  # 35% chance at each spot
                    pt = seg.interpolate(dist)
                    color = rng.choice(people_colors)
                    draw.ellipse(
                        (pt.x - person_radius, pt.y - person_radius, pt.x + person_radius, pt.y + person_radius),
                        fill=color,
                    )
                    # Occasional pair (couple walking together)
                    if rng.random() < 0.30:
                        px = pt.x + rng.uniform(-2.5, 2.5)
                        py = pt.y + rng.uniform(-2.5, 2.5)
                        draw.ellipse(
                            (px - person_radius, py - person_radius, px + person_radius, py + person_radius),
                            fill=rng.choice(people_colors),
                        )
                dist += spacing * rng.uniform(0.8, 1.2)

    # People in plazas
    for feature in scene["pixel"].get("plazas", []):
        poly = _polygon_from_geometry(feature.get("geometry"))
        if poly is None or poly.is_empty:
            continue
        minx, miny, maxx, maxy = poly.bounds
        count = min(15, max(3, int(poly.area / 2000)))
        placed = 0
        for _ in range(count * 5):
            px = rng.uniform(minx, maxx)
            py = rng.uniform(miny, maxy)
            if not poly.buffer(1e-9).contains(Point(px, py)):
                continue
            draw.ellipse(
                (px - person_radius, py - person_radius, px + person_radius, py + person_radius),
                fill=rng.choice(people_colors),
            )
            placed += 1
            if placed >= count:
                break

        # Cafe furniture clusters in large plazas
        if poly.area > 3000:
            furniture_count = rng.randint(1, 3)
            furniture_color = _hex_to_rgba(_blend_hex(palette.get("path", "#c4bca8"), "#e0d8c8", 0.30), 160)
            for _ in range(furniture_count * 4):
                fx = rng.uniform(minx + 5, maxx - 5)
                fy = rng.uniform(miny + 5, maxy - 5)
                if not poly.buffer(-3).contains(Point(fx, fy)):
                    continue
                fw = rng.uniform(3, 5) * max(ppm * 0.3, 1)
                fh = rng.uniform(3, 5) * max(ppm * 0.3, 1)
                draw.rectangle((fx - fw, fy - fh, fx + fw, fy + fh), fill=furniture_color)
                furniture_count -= 1
                if furniture_count <= 0:
                    break


# -- Roof color palettes per typology -- distinct, high-contrast values
_ROOF_COLORS: dict[str, str] = {
    "townhouse": "#6A5540",  # warm terracotta/slate — reads clearly as residential pitched
    "midrise": "#707880",  # cool concrete grey — distinct from townhouse
    "highrise": "#5A6470",  # dark steel blue-grey — tallest = darkest
    "mixed_use": "#585E68",  # urban charcoal — podium + tower
    "commercial": "#646A72",  # neutral dark — office/retail
    "generic": "#6E757D",  # mid-dark grey fallback
}


def _render_roof_townhouse(
    draw: ImageDraw.ImageDraw,
    poly: Polygon,
    inset: Polygon,
    palette: dict[str, str],
    rng: random.Random,
    variant: dict[str, Any],
) -> None:
    """Pitched roof with ridge line, slope shading, and chimney."""
    roof_base = _ROOF_COLORS["townhouse"]
    minx, miny, maxx, maxy = inset.bounds
    spanx, spany = max(maxx - minx, 1), max(maxy - miny, 1)

    # Fill the whole roof with warm slate base — strong coverage
    _draw_polygon(draw, inset, _hex_to_rgba(roof_base, 255))
    _draw_polygon_outline(draw, inset, _hex_to_rgba(_blend_hex(roof_base, "#1a1a1a", 0.40), 100), width=1)

    # Ridge line along the long axis
    if spanx >= spany:
        cy = miny + spany * 0.5
        ridge = LineString([(minx + 2, cy), (maxx - 2, cy)])
        # Two slope faces: lighter top, darker bottom
        top_half = _polygon_from_geometry(box(minx, miny, maxx, cy).intersection(inset))
        bot_half = _polygon_from_geometry(box(minx, cy, maxx, maxy).intersection(inset))
        if top_half:
            _draw_polygon(draw, top_half, _hex_to_rgba(_blend_hex(roof_base, "#ffffff", 0.22), 100))
        if bot_half:
            _draw_polygon(draw, bot_half, _hex_to_rgba(_blend_hex(roof_base, "#000000", 0.18), 80))
    else:
        cx = minx + spanx * 0.5
        ridge = LineString([(cx, miny + 2), (cx, maxy - 2)])
        left_half = _polygon_from_geometry(box(minx, miny, cx, maxy).intersection(inset))
        right_half = _polygon_from_geometry(box(cx, miny, maxx, maxy).intersection(inset))
        if left_half:
            _draw_polygon(draw, left_half, _hex_to_rgba(_blend_hex(roof_base, "#ffffff", 0.22), 100))
        if right_half:
            _draw_polygon(draw, right_half, _hex_to_rgba(_blend_hex(roof_base, "#000000", 0.18), 80))

    detail_line = ridge.intersection(inset)
    if isinstance(detail_line, LineString) and not detail_line.is_empty:
        _draw_line(draw, detail_line, _hex_to_rgba(_blend_hex(roof_base, "#ffffff", 0.45), 140), width=2)

    # Chimney near one end
    if spanx > 16 and spany > 12:
        ch_x = minx + spanx * (0.8 + rng.random() * 0.12)
        ch_y = miny + spany * (0.25 + rng.random() * 0.15)
        ch_w, ch_h = max(3, spanx * 0.06), max(3, spany * 0.08)
        chimney = _polygon_from_geometry(box(ch_x, ch_y, ch_x + ch_w, ch_y + ch_h).intersection(inset))
        if chimney:
            _draw_polygon(draw, chimney, _hex_to_rgba("#5a4a3a", 180))


def _render_roof_midrise(
    draw: ImageDraw.ImageDraw,
    poly: Polygon,
    inset: Polygon,
    palette: dict[str, str],
    rng: random.Random,
    variant: dict[str, Any],
) -> None:
    """Flat roof with HVAC units, elevator shaft, possible green roof."""
    roof_base = _ROOF_COLORS["midrise"]
    minx, miny, maxx, maxy = inset.bounds
    spanx, spany = max(maxx - minx, 1), max(maxy - miny, 1)

    # Green roof (20% chance)
    is_green_roof = rng.random() < 0.20
    if is_green_roof:
        _draw_polygon(draw, inset, _hex_to_rgba("#4a8a4a", 255))
    else:
        _draw_polygon(draw, inset, _hex_to_rgba(roof_base, 255))

    # Parapet shadow — 1px dark line along inner edge
    _draw_polygon_outline(draw, inset, _hex_to_rgba(_blend_hex(roof_base, "#1a1a1a", 0.35), 120), width=1)

    # Elevator shaft — larger rectangle near center
    shaft_w = max(6, spanx * 0.14)
    shaft_h = max(6, spany * 0.14)
    shaft_x = minx + spanx * (0.40 + rng.random() * 0.20)
    shaft_y = miny + spany * (0.40 + rng.random() * 0.20)
    shaft = _polygon_from_geometry(box(shaft_x, shaft_y, shaft_x + shaft_w, shaft_y + shaft_h).intersection(inset))
    if shaft:
        _draw_polygon(draw, shaft, _hex_to_rgba(_blend_hex(roof_base, "#4a5258", 0.55), 200))
        _draw_polygon_outline(draw, shaft, _hex_to_rgba("#3a4248", 160), width=1)

    # HVAC units along one edge (3–6 units)
    unit_count = rng.randint(3, min(6, max(3, int(spanx * spany / 800))))
    edge_y = miny + spany * 0.12
    for i in range(unit_count):
        uw = max(5, spanx * rng.uniform(0.06, 0.10))
        uh = max(4, spany * rng.uniform(0.05, 0.08))
        ux = minx + spanx * 0.08 + (spanx * 0.84 / max(unit_count, 1)) * i + rng.uniform(-2, 2)
        unit_rect = _polygon_from_geometry(box(ux, edge_y, ux + uw, edge_y + uh).intersection(inset))
        if unit_rect:
            _draw_polygon(draw, unit_rect, _hex_to_rgba(_blend_hex(roof_base, "#90989e", 0.50), 190))
            _draw_polygon_outline(draw, unit_rect, _hex_to_rgba("#5a6268", 150), width=1)

    # Roof highlight
    _draw_polygon_outline(draw, inset, _hex_to_rgba(_blend_hex(palette["building"], "#ffffff", 0.55), 35), width=1)


def _render_roof_highrise(
    draw: ImageDraw.ImageDraw,
    poly: Polygon,
    inset: Polygon,
    palette: dict[str, str],
    rng: random.Random,
    variant: dict[str, Any],
) -> None:
    """Flat roof with mechanical core, double parapet, and floor plate lines."""
    roof_base = _ROOF_COLORS["highrise"]
    minx, miny, maxx, maxy = inset.bounds
    spanx, spany = max(maxx - minx, 1), max(maxy - miny, 1)

    _draw_polygon(draw, inset, _hex_to_rgba(roof_base, 255))

    # Double parapet: outer + inner insets
    inner = _polygon_from_geometry(inset.buffer(-max(3, min(spanx, spany) * 0.08)))
    if inner:
        _draw_polygon_outline(draw, inner, _hex_to_rgba(_blend_hex(roof_base, "#1a1a1a", 0.30), 100), width=1)

    # Central mechanical core (15–20% of footprint)
    core_frac = rng.uniform(0.15, 0.22)
    core_w = spanx * core_frac
    core_h = spany * core_frac
    core_x = minx + (spanx - core_w) * 0.5
    core_y = miny + (spany - core_h) * 0.5
    core = _polygon_from_geometry(box(core_x, core_y, core_x + core_w, core_y + core_h).intersection(inset))
    if core:
        _draw_polygon(draw, core, _hex_to_rgba(_blend_hex(roof_base, "#3a4248", 0.55), 220))
        _draw_polygon_outline(draw, core, _hex_to_rgba("#2a3238", 180), width=1)

    # Faint concentric floor plate lines
    for i in range(2, min(5, int(min(spanx, spany) / 8))):
        ring = _polygon_from_geometry(inset.buffer(-i * max(3, min(spanx, spany) * 0.04)))
        if ring:
            _draw_polygon_outline(draw, ring, _hex_to_rgba(_blend_hex(roof_base, "#ffffff", 0.30), 16), width=1)

    # Outer parapet highlight
    _draw_polygon_outline(draw, inset, _hex_to_rgba(_blend_hex(palette["building"], "#ffffff", 0.55), 45), width=1)


def _render_roof_mixed_use(
    draw: ImageDraw.ImageDraw,
    poly: Polygon,
    inset: Polygon,
    palette: dict[str, str],
    rng: random.Random,
    variant: dict[str, Any],
) -> None:
    """Mixed-use: podium base + tower portion if elongated, otherwise midrise treatment."""
    minx, miny, maxx, maxy = inset.bounds
    spanx, spany = max(maxx - minx, 1), max(maxy - miny, 1)

    if spanx / spany > 2.0 or spany / spanx > 2.0:
        # Split into podium and tower
        if spanx > spany:
            split = minx + spanx * 0.55
            podium = _polygon_from_geometry(box(minx, miny, split, maxy).intersection(inset))
            tower = _polygon_from_geometry(box(split, miny, maxx, maxy).intersection(inset))
        else:
            split = miny + spany * 0.55
            podium = _polygon_from_geometry(box(minx, miny, maxx, split).intersection(inset))
            tower = _polygon_from_geometry(box(minx, split, maxx, maxy).intersection(inset))

        # Podium: lighter, retail-like
        if podium:
            _draw_polygon(draw, podium, _hex_to_rgba(_blend_hex(palette["building"], "#c8cdd2", 0.30), 255))
            _draw_polygon_outline(draw, podium, _hex_to_rgba("#8a9098", 60), width=1)
            # Small HVAC units on podium
            pmx, pmy, pmxx, pmxy = podium.bounds
            for _ in range(rng.randint(2, 4)):
                uw = max(3, (pmxx - pmx) * rng.uniform(0.05, 0.08))
                uh = max(3, (pmxy - pmy) * rng.uniform(0.05, 0.08))
                ux = pmx + rng.random() * max((pmxx - pmx) - uw - 4, 1)
                uy = pmy + rng.random() * max((pmxy - pmy) - uh - 4, 1)
                unit = _polygon_from_geometry(box(ux, uy, ux + uw, uy + uh).intersection(podium))
                if unit:
                    _draw_polygon(draw, unit, _hex_to_rgba("#aab2ba", 80))

        # Tower: midrise treatment
        if tower:
            _render_roof_midrise(draw, poly, tower, palette, rng, variant)
    else:
        _render_roof_midrise(draw, poly, inset, palette, rng, variant)


def _render_roof_generic(
    draw: ImageDraw.ImageDraw,
    poly: Polygon,
    inset: Polygon,
    palette: dict[str, str],
    rng: random.Random,
    variant: dict[str, Any],
    height_m: float,
) -> None:
    """Enhanced generic roof with more HVAC units and height-based color."""
    roof_base = _ROOF_COLORS["generic"]
    minx, miny, maxx, maxy = inset.bounds
    spanx, spany = max(maxx - minx, 1), max(maxy - miny, 1)

    height_tint = max(0.0, min((height_m - 9.0) / 36.0, 0.18))
    base_color = roof_base
    if height_tint > 0.02:
        base_color = _blend_hex(base_color, "#b8c0c8", height_tint)
    _draw_polygon(draw, inset, _hex_to_rgba(base_color, 255))
    _draw_polygon_outline(draw, inset, _hex_to_rgba(_blend_hex(roof_base, "#1a1a1a", 0.35), 110), width=1)

    # Grid lines
    line_count = max(1, min(int(variant.get("roof_detail_lines") or 2), int(max(spanx, spany) / 24)))
    detail_color = _hex_to_rgba(
        _blend_hex(palette["building"], "#79828a", 0.55), int(variant.get("roof_detail_alpha") or 72)
    )
    for li in range(1, line_count + 1):
        t = li / (line_count + 1)
        if spanx >= spany:
            guide = LineString([(minx + 3, miny + spany * t), (maxx - 3, miny + spany * t)])
        else:
            guide = LineString([(minx + spanx * t, miny + 3), (minx + spanx * t, maxy - 3)])
        detail_line = guide.intersection(inset)
        if isinstance(detail_line, LineString) and not detail_line.is_empty:
            _draw_line(draw, detail_line, detail_color, width=1)

    # HVAC units (4–8)
    max_units = min(8, max(2, int(spanx * spany / 600)))
    for _ in range(max_units):
        uw = max(5, spanx * rng.uniform(0.06, 0.12))
        uh = max(4, spany * rng.uniform(0.05, 0.10))
        ux = minx + 3 + rng.random() * max(spanx - uw - 6, 1)
        uy = miny + 3 + rng.random() * max(spany - uh - 6, 1)
        unit = _polygon_from_geometry(box(ux, uy, ux + uw, uy + uh).intersection(inset))
        if unit:
            _draw_polygon(draw, unit, _hex_to_rgba(_blend_hex(roof_base, "#b0b8c0", 0.45), 85))
            _draw_polygon_outline(draw, unit, _hex_to_rgba("#7a828a", 70), width=1)

    _draw_polygon_outline(draw, inset, _hex_to_rgba(_blend_hex(palette["building"], "#ffffff", 0.55), 35), width=1)


def _render_buildings(
    image: Image.Image,
    scene: dict[str, Any],
    palette: dict[str, str],
    variant: dict[str, Any],
) -> None:
    building_edge = _hex_to_rgba(
        _blend_hex(palette["building"], "#3a4248", 0.50), int(variant.get("building_edge_alpha") or 160)
    )
    shadow_fill = _hex_to_rgba(_blend_hex(palette["shadow"], "#000000", 0.35), int(variant.get("shadow_alpha") or 128))
    shadow_offset = variant.get("shadow_offset") or (8, 9)
    shadow_blur = float(variant.get("shadow_blur") or 2.4)
    base_seed = int(variant.get("seed") or 0)

    # Collect buildings with their properties for typology classification
    building_entries: list[tuple[Polygon, float, dict[str, Any]]] = []
    for building in scene["pixel"]["building_masses"]:
        geometry = _polygon_from_geometry(building.get("geometry"))
        if geometry is not None:
            building_entries.append((geometry, _feature_height_m(building), building.get("properties") or {}))
    for building in scene["pixel"]["building_footprints"]:
        geometry = _polygon_from_geometry(building.get("geometry"))
        if geometry is not None:
            building_entries.append((geometry, _feature_height_m(building), building.get("properties") or {}))

    # Draw shadows — grouped into height bands for per-band blur
    base_sx, base_sy = float(shadow_offset[0]), float(shadow_offset[1])
    height_bands: list[tuple[float, float, float]] = [
        (0.0, 12.0, shadow_blur * 0.7),  # low-rise: tighter shadow
        (12.0, 25.0, shadow_blur * 1.0),  # mid-rise: base shadow
        (25.0, 999.0, shadow_blur * 1.5),  # high-rise: softer diffuse shadow
    ]
    for band_min, band_max, band_blur in height_bands:
        band_shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
        band_draw = ImageDraw.Draw(band_shadow, "RGBA")
        band_has_entries = False
        for poly, height_m, _props in building_entries:
            if not (band_min <= height_m < band_max):
                continue
            band_has_entries = True
            height_factor = max(0.4, min(height_m / 18.0, 2.5))
            sx = base_sx * height_factor
            sy = base_sy * height_factor
            shifted = translate(poly, xoff=sx, yoff=sy)
            _draw_polygon(band_draw, shifted, shadow_fill)
        if band_has_entries:
            image.alpha_composite(band_shadow.filter(ImageFilter.GaussianBlur(radius=max(band_blur, 1.0))))
    draw = ImageDraw.Draw(image, "RGBA")

    for index, (poly, height_m, props) in enumerate(building_entries):
        typology = _classify_building_typology(props, height_m)
        # Building base fill — darker than roof for parapet edge effect
        height_tint = max(0.0, min((height_m - 9.0) / 36.0, 0.18))
        base_hex = _blend_hex(palette["building"], "#606870", 0.45)
        bld_fill = _hex_to_rgba(
            _blend_hex(base_hex, "#8a9098", height_tint) if height_tint > 0.02 else base_hex,
            255,
        )
        _draw_polygon(draw, poly, bld_fill)
        _draw_polygon_outline(draw, poly, building_edge, width=2)

        # Inner parapet shadow — dark band just inside the footprint for depth
        parapet_inner = _polygon_from_geometry(poly.buffer(-1.5))
        if parapet_inner is not None:
            parapet_shadow_color = _hex_to_rgba(_blend_hex(base_hex, "#2a2a30", 0.45), 80)
            _draw_polygon_outline(draw, parapet_inner, parapet_shadow_color, width=1)

        # Adaptive inset: use smaller buffer for small buildings so roof detail is never lost
        minx_b, miny_b, maxx_b, maxy_b = poly.bounds
        min_dim = min(maxx_b - minx_b, maxy_b - miny_b)
        inset_px = min(3.0, max(1.0, min_dim * 0.12))
        inset = _polygon_from_geometry(poly.buffer(-inset_px))
        if inset is None:
            # Fallback: use the polygon itself as inset for very tiny buildings
            inset = poly

        rng = random.Random(base_seed + index * 173 + int(poly.area))

        # Dispatch to per-typology roof renderer
        if typology == "townhouse":
            _render_roof_townhouse(draw, poly, inset, palette, rng, variant)
        elif typology == "midrise":
            _render_roof_midrise(draw, poly, inset, palette, rng, variant)
        elif typology == "highrise":
            _render_roof_highrise(draw, poly, inset, palette, rng, variant)
        elif typology == "mixed_use":
            _render_roof_mixed_use(draw, poly, inset, palette, rng, variant)
        elif typology == "commercial":
            _render_roof_generic(draw, poly, inset, palette, rng, variant, height_m)
        else:
            _render_roof_generic(draw, poly, inset, palette, rng, variant, height_m)


def _render_streets_and_context(
    image: Image.Image,
    scene: dict[str, Any],
    palette: dict[str, str],
    toggles: dict[str, bool],
    variant: dict[str, Any],
) -> None:
    draw = ImageDraw.Draw(image, "RGBA")
    road_fill = _hex_to_rgba(palette["road"], 255)
    road_edge = _hex_to_rgba(_blend_hex(palette["road"], "#2a3038", 0.50), 230)
    lane_fill = _hex_to_rgba(
        _blend_hex(palette["road"], "#ffffff", 0.82), int(variant.get("lane_marking_alpha") or 140)
    )
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

    sidewalk_fill = _hex_to_rgba(_blend_hex(palette["path"], "#e8e2d8", 0.22), 210)
    sidewalk_edge_color = _hex_to_rgba(_blend_hex(palette["path"], "#b5ae9f", 0.28), 90)
    for feature in scene["pixel"]["roads"]:
        geometry = feature.get("geometry")
        # Extract all LineString segments — handles LineString, MultiLineString, GeometryCollection
        road_segments = _extract_linestrings(geometry)
        if road_segments:
            width = int(max(round(float(feature.get("width_m", 8.0)) * scene["pixels_per_meter"]), 3))
            for seg in road_segments:
                # Sidewalk strips alongside roads (drawn first, behind road)
                sidewalk_width = max(width + 6, int(width * 1.35))
                _draw_line(draw, seg, sidewalk_edge_color, width=sidewalk_width + 1)
                _draw_line(draw, seg, sidewalk_fill, width=sidewalk_width)
                # Road with curb effect
                _draw_line(draw, seg, road_edge, width=width + 2)
                _draw_line(draw, seg, road_fill, width=width)
                if width >= 10:
                    _draw_dashed_line(
                        draw,
                        seg,
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
        path_segments = _extract_linestrings(geometry)
        if path_segments:
            width = int(max(round(float(feature.get("width_m", 4.0)) * scene["pixels_per_meter"]), 2))
            for seg in path_segments:
                _draw_line(draw, seg, path_edge, width=width + 1)
                _draw_line(draw, seg, path_fill, width=width)
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

    # --- Crosswalks at road intersections ---
    ppm = float(scene.get("pixels_per_meter") or 1.0)
    crosswalk_fill = _hex_to_rgba("#ffffff", 190)
    road_lines: list[tuple[LineString, float]] = []
    for feature in scene["pixel"]["roads"]:
        geom = feature.get("geometry")
        rw = float(feature.get("width_m", 8.0)) * ppm
        for ls in _extract_linestrings(geom):
            road_lines.append((ls, rw))

    for i, (line_a, w_a) in enumerate(road_lines):
        for j, (line_b, w_b) in enumerate(road_lines):
            if j <= i:
                continue
            try:
                ix = line_a.intersection(line_b)
            except Exception:
                continue
            if ix.is_empty:
                continue
            pts = []
            if isinstance(ix, Point):
                pts = [(ix.x, ix.y)]
            elif hasattr(ix, "geoms"):
                pts = [(g.x, g.y) for g in ix.geoms if isinstance(g, Point)]
            for px, py in pts:
                # Draw crosswalk bars perpendicular to each road
                for line, rw in [(line_a, w_a), (line_b, w_b)]:
                    nearest_pt = line.interpolate(line.project(Point(px, py)))
                    frac = line.project(nearest_pt) / max(line.length, 1e-6)
                    frac2 = min(frac + 0.01, 1.0)
                    p1 = line.interpolate(frac, normalized=True)
                    p2 = line.interpolate(frac2, normalized=True)
                    angle = math.atan2(p2.y - p1.y, p2.x - p1.x)
                    perp = angle + math.pi / 2
                    bar_len = rw * 0.45
                    bar_w = max(2, rw * 0.04)
                    for k in range(-3, 4):
                        cx = px + math.cos(angle) * k * bar_w * 2.5
                        cy = py + math.sin(angle) * k * bar_w * 2.5
                        x1 = cx + math.cos(perp) * bar_len
                        y1 = cy + math.sin(perp) * bar_len
                        x2 = cx - math.cos(perp) * bar_len
                        y2 = cy - math.sin(perp) * bar_len
                        draw.line([(x1, y1), (x2, y2)], fill=crosswalk_fill, width=max(int(bar_w), 2))

    # --- Parked cars along roads ---
    car_rng = random.Random(int(variant.get("seed", 0)) + 5555)
    car_colors = [
        _hex_to_rgba("#e8e8e8", 200),  # white
        _hex_to_rgba("#c0c0c0", 200),  # silver
        _hex_to_rgba("#3a3a3a", 200),  # black
        _hex_to_rgba("#4a6a8a", 200),  # blue
        _hex_to_rgba("#8a3a3a", 200),  # red
    ]
    car_windshield = _hex_to_rgba("#2a3040", 160)
    for line, road_width_px in road_lines:
        if road_width_px < 8 * ppm:
            continue  # Only park on wider roads
        car_w = 2.5 * ppm
        car_h = 5.0 * ppm
        offset_dist = road_width_px / 2 - car_w * 0.6
        for side_mult in [1, -1]:
            try:
                side_line = line.parallel_offset(offset_dist * side_mult, "left" if side_mult > 0 else "right")
            except Exception:
                continue
            if side_line.is_empty:
                continue
            # Extract LineStrings from parallel_offset result
            side_segments = _extract_linestrings(side_line)
            for side_line in side_segments:
                dist = car_rng.uniform(0, 6 * ppm)
                while dist < side_line.length:
                    if car_rng.random() < 0.60:  # 60% fill rate
                        pt = side_line.interpolate(dist)
                        # Car rectangle — keep proportional to pixels_per_meter
                        cw, ch = max(car_w * 0.5, 3), max(car_h * 0.5, 5)
                        car_color = car_rng.choice(car_colors)
                        # Simple axis-aligned rectangle approximation
                        cx, cy = pt.x, pt.y
                        draw.rectangle(
                            (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2),
                            fill=car_color,
                        )
                        # Windshield at front
                        draw.rectangle(
                            (cx - cw / 2 + 1, cy - ch / 2, cx + cw / 2 - 1, cy - ch / 2 + max(ch * 0.2, 1.5)),
                            fill=car_windshield,
                        )
                    dist += (6.0 + car_rng.uniform(0, 2.0)) * ppm

    # --- Water with depth gradient and wave ripples ---
    water_ripple = _hex_to_rgba(_blend_hex(palette["water"], "#ffffff", 0.22), 38)
    for feature in scene["pixel"]["water"]:
        poly = _polygon_from_geometry(feature.get("geometry"))
        if poly is not None:
            _draw_polygon(draw, poly, water_fill)
            # Depth gradient: progressively deeper blue toward center
            for step in range(1, 4):
                inner = _polygon_from_geometry(poly.buffer(-step * max(3, (poly.bounds[3] - poly.bounds[1]) * 0.06)))
                if inner:
                    deeper_blue = _hex_to_rgba(_blend_hex(palette["water"], "#1a3a5a", step * 0.08), 35)
                    _draw_polygon(draw, inner, deeper_blue)
            _draw_polygon_outline(draw, poly, water_edge, width=1)
            # Wave ripple lines with subtle curvature
            wminx, wminy, wmaxx, wmaxy = poly.bounds
            ripple_gap = max(4.0, min(8.0, (wmaxy - wminy) / 12))
            ry = wminy + ripple_gap
            while ry < wmaxy:
                # Sinusoidal wave offset for organic feel
                wave_pts = []
                wx = wminx - 1
                while wx < wmaxx + 1:
                    wy = ry + 1.5 * math.sin(wx / max(15.0, ripple_gap * 2))
                    wave_pts.append((wx, wy))
                    wx += 3.0
                if len(wave_pts) >= 2:
                    wave_line = LineString(wave_pts).intersection(poly)
                    if isinstance(wave_line, LineString) and not wave_line.is_empty:
                        _draw_line(draw, wave_line, water_ripple, width=1)
                ry += ripple_gap

    # --- Entourage: people on paths and plazas ---
    ent_rng = random.Random(int(variant.get("seed", 0)) + 8888)
    person_colors = [
        _hex_to_rgba("#8a6a5a", 180),
        _hex_to_rgba("#5a6a8a", 180),
        _hex_to_rgba("#a08060", 180),
        _hex_to_rgba("#6a5a7a", 180),
        _hex_to_rgba("#4a7a6a", 180),
        _hex_to_rgba("#8a4a4a", 180),
    ]
    # People on paths
    for feature in scene["pixel"]["paths"]:
        geom = feature.get("geometry")
        if isinstance(geom, LineString) and geom.length > 20:
            dist = ent_rng.uniform(5, 15) * ppm
            while dist < geom.length:
                pt = geom.interpolate(dist)
                color = ent_rng.choice(person_colors)
                r = 1.5
                draw.ellipse((pt.x - r, pt.y - r, pt.x + r, pt.y + r), fill=color)
                # Occasional pair (couple walking)
                if ent_rng.random() < 0.3:
                    draw.ellipse(
                        (pt.x - r + 3, pt.y - r + 1, pt.x + r + 3, pt.y + r + 1), fill=ent_rng.choice(person_colors)
                    )
                dist += ent_rng.uniform(15, 25) * ppm

    # People in plazas
    for feature in scene["pixel"]["plazas"]:
        poly = _polygon_from_geometry(feature.get("geometry"))
        if poly is not None and poly.area > 100:
            count = min(15, max(3, int(poly.area / 500)))
            minx, miny, maxx, maxy = poly.bounds
            placed = 0
            for _ in range(count * 3):
                px = ent_rng.uniform(minx, maxx)
                py = ent_rng.uniform(miny, maxy)
                if poly.contains(Point(px, py)):
                    color = ent_rng.choice(person_colors)
                    r = 1.5
                    draw.ellipse((px - r, py - r, px + r, py + r), fill=color)
                    placed += 1
                    if placed >= count:
                        break


def _feature_height_m(feature: dict[str, Any]) -> float:
    properties = feature.get("properties") if isinstance(feature.get("properties"), dict) else {}
    for key in ("height_m", "height"):
        try:
            value = float(properties.get(key))
        except (TypeError, ValueError):
            continue
        if value > 0:
            return value
    for key in ("floors", "floor_count", "floorCount"):
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
    width = int(scene["width"])
    height = int(scene["height"])
    boundary = _polygon_from_geometry(scene["pixel"]["boundary"])
    if boundary is None:
        raise ValueError("Scene boundary is missing in control-map render payload.")

    massing = Image.new("RGBA", (width, height), (18, 20, 22, 255))
    depth = Image.new("L", (width, height), 10)
    segmentation = Image.new("RGBA", (width, height), (14, 16, 18, 255))

    massing_draw = ImageDraw.Draw(massing, "RGBA")
    depth_draw = ImageDraw.Draw(depth)
    segmentation_draw = ImageDraw.Draw(segmentation, "RGBA")

    boundary_coords = _polygon_coords(boundary)
    massing_draw.polygon(boundary_coords, fill=(214, 218, 212, 255))
    depth_draw.polygon(boundary_coords, fill=40)
    segmentation_draw.polygon(boundary_coords, fill=(42, 44, 48, 255))

    if toggles.get("show_surrounding_context", True):
        for feature in scene["pixel"]["context_roads"]:
            geometry = feature.get("geometry")
            width_px = int(max(round(float(feature.get("width_m", 6.0)) * scene["pixels_per_meter"]), 2))
            if isinstance(geometry, LineString):
                _draw_line(massing_draw, geometry, (46, 50, 56, 196), width=width_px)
                _draw_line(depth_draw, geometry, 24, width=width_px)
                _draw_line(segmentation_draw, geometry, (34, 36, 40, 255), width=width_px)
            else:
                poly = _polygon_from_geometry(geometry)
                if poly is not None:
                    _draw_polygon(massing_draw, poly, (46, 50, 56, 188))
                    _draw_polygon(depth_draw, poly, 24)
                    _draw_polygon(segmentation_draw, poly, (34, 36, 40, 255))
        for feature in scene["pixel"]["context_buildings"]:
            poly = _polygon_from_geometry(feature.get("geometry"))
            if poly is not None:
                _draw_polygon(massing_draw, poly, (74, 78, 84, 168))
                _draw_polygon(depth_draw, poly, 30)
                _draw_polygon(segmentation_draw, poly, (56, 58, 62, 255))
        for feature in scene["pixel"]["context_parks"]:
            poly = _polygon_from_geometry(feature.get("geometry"))
            if poly is not None:
                _draw_polygon(massing_draw, poly, (62, 88, 60, 152))
                _draw_polygon(depth_draw, poly, 22)
                _draw_polygon(segmentation_draw, poly, (36, 62, 40, 255))
        for feature in scene["pixel"]["context_water"]:
            poly = _polygon_from_geometry(feature.get("geometry"))
            if poly is not None:
                _draw_polygon(massing_draw, poly, (52, 74, 98, 160))
                _draw_polygon(depth_draw, poly, 26)
                _draw_polygon(segmentation_draw, poly, (40, 56, 72, 255))

    for feature in scene["pixel"]["roads"]:
        geometry = feature.get("geometry")
        width_px = int(max(round(float(feature.get("width_m", 8.0)) * scene["pixels_per_meter"]), 3))
        if isinstance(geometry, LineString):
            _draw_line(massing_draw, geometry, (98, 102, 108, 255), width=width_px)
            _draw_line(massing_draw, geometry, (126, 130, 136, 176), width=max(width_px - 2, 1))
            _draw_line(depth_draw, geometry, 62, width=width_px)
            _draw_line(segmentation_draw, geometry, (76, 104, 182, 255), width=width_px)
        else:
            poly = _polygon_from_geometry(geometry)
            if poly is not None:
                _draw_polygon(massing_draw, poly, (98, 102, 108, 255))
                _draw_polygon(depth_draw, poly, 62)
                _draw_polygon(segmentation_draw, poly, (76, 104, 182, 255))

    for feature in scene["pixel"]["paths"]:
        geometry = feature.get("geometry")
        width_px = int(max(round(float(feature.get("width_m", 4.0)) * scene["pixels_per_meter"]), 2))
        if isinstance(geometry, LineString):
            _draw_line(massing_draw, geometry, (188, 180, 160, 255), width=width_px)
            _draw_line(depth_draw, geometry, 74, width=width_px)
            _draw_line(segmentation_draw, geometry, (214, 182, 122, 255), width=width_px)
        else:
            poly = _polygon_from_geometry(geometry)
            if poly is not None:
                _draw_polygon(massing_draw, poly, (188, 180, 160, 255))
                _draw_polygon(depth_draw, poly, 74)
                _draw_polygon(segmentation_draw, poly, (214, 182, 122, 255))

    for feature in scene["pixel"]["plazas"]:
        poly = _polygon_from_geometry(feature.get("geometry"))
        if poly is not None:
            _draw_polygon(massing_draw, poly, (196, 188, 170, 255))
            _draw_polygon(depth_draw, poly, 84)
            _draw_polygon(segmentation_draw, poly, (224, 196, 132, 255))

    for feature in scene["pixel"]["parks"]:
        poly = _polygon_from_geometry(feature.get("geometry"))
        if poly is not None:
            _draw_polygon(massing_draw, poly, (92, 126, 84, 255))
            _draw_polygon(depth_draw, poly, 92)
            _draw_polygon(segmentation_draw, poly, (72, 156, 92, 255))

    for feature in scene["pixel"]["water"]:
        poly = _polygon_from_geometry(feature.get("geometry"))
        if poly is not None:
            _draw_polygon(massing_draw, poly, (76, 108, 134, 255))
            _draw_polygon(depth_draw, poly, 104)
            _draw_polygon(segmentation_draw, poly, (66, 128, 196, 255))

    building_features = list(scene["pixel"]["building_masses"]) + list(scene["pixel"]["building_footprints"])
    building_heights = [_feature_height_m(feature) for feature in building_features]
    max_height = max(building_heights, default=24.0)
    shadow_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_image, "RGBA")
    shadow_offset = variant.get("shadow_offset") or (7, 8)
    skirt_px = max(float(scene["pixels_per_meter"]) * 3.0, 2.0)

    for feature in building_features:
        poly = _polygon_from_geometry(feature.get("geometry"))
        if poly is None:
            continue
        skirt = _polygon_from_geometry(poly.buffer(skirt_px).intersection(boundary))
        if skirt is not None:
            _draw_polygon(massing_draw, skirt, (88, 92, 98, 255))
            _draw_polygon(depth_draw, skirt, 108)
            _draw_polygon(segmentation_draw, skirt, (90, 104, 116, 255))
        shifted = translate(poly, xoff=float(shadow_offset[0]) * 0.62, yoff=float(shadow_offset[1]) * 0.62)
        _draw_polygon(shadow_draw, shifted, (10, 12, 16, 126))

    massing.alpha_composite(
        shadow_image.filter(ImageFilter.GaussianBlur(radius=max(float(variant.get("shadow_blur") or 2.0) * 0.75, 1.3)))
    )

    for feature, height_m in zip(building_features, building_heights):
        poly = _polygon_from_geometry(feature.get("geometry"))
        if poly is None:
            continue
        normalized = max(0.0, min(height_m / max(max_height, 1.0), 1.0))
        tone = int(176 + normalized * 70)
        depth_value = int(150 + normalized * 90)
        _draw_polygon(massing_draw, poly, (tone, tone + 4, tone + 10, 255))
        _draw_polygon_outline(massing_draw, poly, (244, 246, 248, 228), width=2)
        _draw_polygon(depth_draw, poly, depth_value)
        _draw_polygon(segmentation_draw, poly, (224, 108, 84, 255))
        _draw_polygon_outline(segmentation_draw, poly, (255, 244, 236, 255), width=2)

    if base_image is not None:
        structure = Image.blend(base_image.convert("RGBA"), massing, 0.46)
    else:
        structure = massing.copy()
    depth_rgb = Image.merge("RGBA", (depth, depth, depth, Image.new("L", (width, height), 255)))
    structure = Image.blend(structure, depth_rgb, 0.20)

    structure_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(structure_overlay, "RGBA")
    overlay_draw.line(boundary_coords, fill=(255, 255, 255, 160), width=2, joint="curve")
    for feature in building_features:
        poly = _polygon_from_geometry(feature.get("geometry"))
        if poly is not None:
            _draw_polygon_outline(overlay_draw, poly, (255, 255, 255, 148), width=1)
    structure.alpha_composite(structure_overlay)

    return {
        "massing": massing,
        "depth": depth,
        "segmentation": segmentation,
        "structure": structure,
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


def _fetch_mapbox_satellite_underlay(
    view_extent: Polygon, width: int, height: int
) -> tuple[Image.Image | None, str | None]:
    if not settings.mapbox_access_token:
        return None, "MAPBOX_ACCESS_TOKEN not configured"
    try:
        httpx = importlib.import_module("httpx")
    except Exception as exc:
        return None, f"mapbox http client unavailable: {exc}"

    minx, miny, maxx, maxy = view_extent.bounds
    if maxx <= minx or maxy <= miny:
        return None, "invalid view extent for map underlay"

    css_width = min(1280, max(640, width))
    css_height = min(1280, max(480, height))
    bbox_path = f"[{minx:.6f},{miny:.6f},{maxx:.6f},{maxy:.6f}]"
    url = (
        f"https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/"
        f"{bbox_path}/{css_width}x{css_height}@2x"
        f"?padding=0&access_token={settings.mapbox_access_token}"
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
    render_mode: str | None,
    render_style_preset: str | None,
    map_screenshot_satellite: str | None,
    map_screenshot_bounds: Any = None,
) -> tuple[Image.Image | None, dict[str, Any]]:
    mode = _normalize_render_mode(render_mode)
    render_key = str(render_style_preset or "").strip().lower()
    wants_underlay = mode == MASTER_PLAN_2D_RENDER_MODE_DEFAULT or render_key in {
        "photorealistic_aerial",
        "photoreal_orthographic_aerial",
    }
    status = {
        "requested": wants_underlay or bool(_normalize_whitespace(map_screenshot_satellite)),
        "applied": False,
        "source": None,
        "reason": None,
        "render_mode": mode,
        "screenshot_bounds_available": bool(_map_bounds_polygon(map_screenshot_bounds)),
    }

    screenshot_image = _image_from_data_uri(map_screenshot_satellite)
    view_extent = _polygon_from_geometry(scene.get("view_extent")) or _polygon_from_geometry(scene.get("boundary"))

    if mode == MASTER_PLAN_2D_RENDER_MODE_DEFAULT:
        if screenshot_image is not None and status["screenshot_bounds_available"]:
            status.update({"applied": True, "source": "viewer_map_screenshot", "reason": None})
            return screenshot_image, status

        if wants_underlay and view_extent is not None:
            fetched, error = _fetch_mapbox_satellite_underlay(view_extent, int(scene["width"]), int(scene["height"]))
            if fetched is not None:
                status.update({"applied": True, "source": "mapbox_static", "reason": None})
                return fetched, status
            status["reason"] = error or "context underlay unavailable"

        if screenshot_image is not None:
            status.update(
                {
                    "applied": True,
                    "source": "viewer_map_screenshot_unbounded",
                    "reason": status.get("reason") or "map bounds unavailable; screenshot alignment may vary",
                }
            )
            return screenshot_image, status

        if not wants_underlay:
            status["reason"] = status.get("reason") or "render mode does not request real aerial context underlay"
            return None, status

        if view_extent is None:
            status["reason"] = status.get("reason") or "scene extent unavailable for context underlay"
            return None, status

        status["reason"] = status.get("reason") or "context underlay unavailable"
        return None, status

    if screenshot_image is not None:
        status.update({"applied": True, "source": "viewer_map_screenshot", "reason": None})
        return screenshot_image, status

    if not wants_underlay:
        status["reason"] = "render preset does not request a real aerial context underlay"
        return None, status

    if view_extent is None:
        status["reason"] = "scene boundary unavailable for context underlay"
        return None, status

    fetched, error = _fetch_mapbox_satellite_underlay(view_extent, int(scene["width"]), int(scene["height"]))
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

    boundary = _polygon_from_geometry(scene["pixel"]["boundary"])
    if boundary is None:
        raise ValueError("Scene boundary is missing in pixel-space render payload.")

    # Build clip mask early — used by satellite masking and later composition
    clip_mask = Image.new("L", (width, height), 0)
    clip_draw = ImageDraw.Draw(clip_mask)
    clip_draw.polygon(_polygon_coords(boundary), fill=255)
    outside_mask = ImageOps.invert(clip_mask)

    if underlay_active:
        # --- Satellite ONLY outside the site boundary ---
        # Resize satellite to fill canvas — use LANCZOS stretch instead of crop-fit
        # because we now match the canvas aspect ratio to the view_extent bounds.
        sat_image = context_underlay.convert("RGB").resize((width, height), Image.Resampling.LANCZOS).convert("RGBA")
        sat_image = ImageEnhance.Contrast(sat_image).enhance(1.04 if variant.get("orthographic_mode") else 1.03)
        sat_image = ImageEnhance.Color(sat_image).enhance(1.00 if variant.get("orthographic_mode") else 1.02)
        sat_image = ImageEnhance.Sharpness(sat_image).enhance(1.10 if variant.get("orthographic_mode") else 1.05)
        # Desaturate satellite context 35% — site should pop by comparison
        desat = ImageEnhance.Color(sat_image).enhance(0.55)
        sat_image = Image.blend(sat_image, desat, 0.35)
        # Slightly lighten to push context further into background
        sat_image = ImageEnhance.Brightness(sat_image).enhance(1.06)
        atmosphere_wash = Image.new(
            "RGBA", (width, height), _hex_to_rgba(_blend_hex(palette["paper"], "#eef2ee", 0.12), 18)
        )
        sat_image.alpha_composite(atmosphere_wash)

        # Composite: satellite outside boundary, clean ground inside
        canvas = Image.new("RGBA", (width, height), _hex_to_rgba(palette["paper"], 255))
        # Paste satellite ONLY outside boundary — at near-full strength for realism
        sat_outside = Image.composite(sat_image, Image.new("RGBA", (width, height), (0, 0, 0, 0)), outside_mask)
        canvas.alpha_composite(sat_outside)

        # Fill inside boundary with opaque site ground color
        site_base = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        site_base_draw = ImageDraw.Draw(site_base, "RGBA")
        _draw_polygon(site_base_draw, boundary, _hex_to_rgba(palette["site"], 255))
        canvas.alpha_composite(site_base)

        # Subtle ground material noise inside boundary
        ground_noise = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        gn_draw = ImageDraw.Draw(ground_noise, "RGBA")
        gn_rng = random.Random(int(variant.get("seed", 0)) + 7)
        for _ in range(int(width * height / 200)):
            gx = gn_rng.randint(0, width - 1)
            gy = gn_rng.randint(0, height - 1)
            if gn_rng.random() > 0.5:
                noise_col = _hex_to_rgba(_blend_hex(palette["site"], "#ffffff", 0.15), gn_rng.randint(8, 18))
            else:
                noise_col = _hex_to_rgba(_blend_hex(palette["site"], "#000000", 0.10), gn_rng.randint(6, 14))
            gn_draw.point((gx, gy), fill=noise_col)
        ground_noise = ground_noise.filter(ImageFilter.GaussianBlur(radius=1.2))
        ground_noise_masked = Image.composite(ground_noise, Image.new("RGBA", (width, height), (0, 0, 0, 0)), clip_mask)
        canvas.alpha_composite(ground_noise_masked)

        # Crisp boundary edge: dark inner border + bright outer glow
        boundary_glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        boundary_draw = ImageDraw.Draw(boundary_glow, "RGBA")
        # Outer glow — soft white halo
        _draw_polygon_outline(boundary_draw, boundary, _hex_to_rgba("#ffffff", 180), width=6)
        canvas.alpha_composite(boundary_glow.filter(ImageFilter.GaussianBlur(radius=2.5)))
        # Crisp dark border on top
        boundary_edge = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        boundary_edge_draw = ImageDraw.Draw(boundary_edge, "RGBA")
        _draw_polygon_outline(boundary_edge_draw, boundary, _hex_to_rgba("#2a2a2a", 200), width=3)
        canvas.alpha_composite(boundary_edge)
    else:
        canvas = Image.new("RGBA", (width, height), _hex_to_rgba(palette["paper"], 255))
        draw = ImageDraw.Draw(canvas, "RGBA")
        draw.rectangle((0, 0, width, height), fill=_hex_to_rgba(palette["paper"], 255))

        # Fill site boundary with opaque ground
        site_base = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        site_base_draw = ImageDraw.Draw(site_base, "RGBA")
        _draw_polygon(site_base_draw, boundary, _hex_to_rgba(palette["site"], 255))
        canvas.alpha_composite(site_base)

    # clip_mask and outside_mask already created above

    context_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    context_toggles = dict(toggles)
    _render_streets_and_context(context_overlay, scene, palette, context_toggles, variant)
    if underlay_active:
        transparent = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        # Inside boundary: full opacity streets/context on clean ground
        inside_site = Image.composite(context_overlay, transparent, clip_mask)
        canvas.alpha_composite(inside_site)
        # Outside boundary: context over satellite at moderate opacity
        outside_site = Image.composite(context_overlay, transparent, outside_mask)
        outside_site = Image.blend(transparent, outside_site, 0.70)
        canvas.alpha_composite(outside_site)
    else:
        canvas.alpha_composite(context_overlay)

    site_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    logger.info(
        "Rendering plan: %dx%d, ppm=%.3f, buildings=%d+%d, roads=%d, parks=%d, paths=%d, plazas=%d, water=%d, underlay=%s",
        width,
        height,
        float(scene.get("pixels_per_meter", 0)),
        len(scene["pixel"].get("building_masses", [])),
        len(scene["pixel"].get("building_footprints", [])),
        len(scene["pixel"].get("roads", [])),
        len(scene["pixel"].get("parks", [])),
        len(scene["pixel"].get("paths", [])),
        len(scene["pixel"].get("plazas", [])),
        len(scene["pixel"].get("water", [])),
        underlay_active,
    )
    # Log road geometry types for debugging
    for ri, road in enumerate(scene["pixel"].get("roads", [])):
        geom = road.get("geometry")
        logger.debug("Road %d: type=%s, width_m=%s", ri, type(geom).__name__ if geom else "None", road.get("width_m"))

    _render_parks(site_overlay, scene, variant, palette)
    _render_street_trees(site_overlay, scene, palette, variant)
    _render_ground_textures(site_overlay, scene, palette, variant)
    _render_setback_vegetation(site_overlay, scene, palette, variant)
    _render_buildings(site_overlay, scene, palette, variant)
    _render_entourage(site_overlay, scene, palette, variant)

    if underlay_active:
        site_overlay = Image.composite(site_overlay, Image.new("RGBA", (width, height), (0, 0, 0, 0)), clip_mask)
        canvas.alpha_composite(site_overlay)
    else:
        canvas = Image.composite(site_overlay, canvas, clip_mask)

    noise_seed = int(variant["seed"])
    rng = random.Random(noise_seed)
    if variant["quality_level"] != "draft":
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

    # ── Warm colour wash ──────────────────────────────────────────────
    if variant["quality_level"] != "draft":
        warm_wash = Image.new("RGBA", (width, height), (245, 239, 230, 8))
        canvas.alpha_composite(warm_wash)

    # ── Vignette ──────────────────────────────────────────────────────
    if variant["quality_level"] != "draft":
        import numpy as np  # local import – only for this pass

        cx, cy = width / 2.0, height / 2.0
        max_r = math.sqrt(cx * cx + cy * cy)
        ys = np.arange(height, dtype=np.float32)
        xs = np.arange(width, dtype=np.float32)
        yy, xx = np.meshgrid(ys, xs, indexing="ij")
        dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        # Normalise 0‥1, apply power curve so centre stays bright
        normed = np.clip(dist / max_r, 0.0, 1.0)
        vignette_strength = 0.12 if variant["quality_level"] == "board_ready" else 0.08
        alpha_arr = (normed**2.2 * 255 * vignette_strength).astype(np.uint8)
        vignette_layer = Image.fromarray(
            np.stack(
                [np.zeros_like(alpha_arr), np.zeros_like(alpha_arr), np.zeros_like(alpha_arr), alpha_arr],
                axis=-1,
            ),
            mode="RGBA",
        )
        canvas.alpha_composite(vignette_layer)

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


def _render_plan_svg(
    scene: dict[str, Any], style_preset: str, variant: dict[str, Any], toggles: dict[str, bool]
) -> str:
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

    # --- SVG overlay elements ---
    overlay_parts: list[str] = []

    # North arrow (top-right corner)
    if toggles.get("show_north_arrow", True):
        na_x = width - 48
        na_y = 28
        overlay_parts.append(
            f'<g id="north-arrow" transform="translate({na_x},{na_y})">'
            '<polygon points="0,-18 -6,12 6,12" fill="#2a3038" opacity="0.85" />'
            '<polygon points="0,-18 0,12 6,12" fill="#5a6068" opacity="0.70" />'
            '<text x="0" y="-22" text-anchor="middle" font-size="11" font-family="Arial,sans-serif" fill="#2a3038" font-weight="bold">N</text>'
            "</g>"
        )

    # Scale bar (bottom-left)
    if toggles.get("show_scale_bar", True):
        ppm = float(scene.get("pixels_per_meter") or 1.0)
        if ppm > 0.01:
            target_bar_px = int(width * 0.15)
            target_dist_m = target_bar_px / ppm
            nice_distances = [10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 5000]
            chosen_m = nice_distances[0]
            for nd in nice_distances:
                if nd <= target_dist_m * 1.5:
                    chosen_m = nd
            bar_px = int(chosen_m * ppm)
            bar_px = max(30, min(bar_px, int(width * 0.25)))
            sb_x = 20
            sb_y = height - 30
            seg_w = bar_px // 4
            sb_rects = ""
            for i in range(4):
                sx = sb_x + i * seg_w
                fill_c = "#2a3038" if i % 2 == 0 else "#f4f1e8"
                sb_rects += f'<rect x="{sx}" y="{sb_y}" width="{seg_w}" height="5" fill="{fill_c}" stroke="#2a3038" stroke-width="0.5" />'
            dist_label = f"{chosen_m / 1000:.1f} km" if chosen_m >= 1000 else f"{chosen_m} m"
            overlay_parts.append(
                f'<g id="scale-bar">{sb_rects}'
                f'<text x="{sb_x}" y="{sb_y + 16}" font-size="9" font-family="Arial,sans-serif" fill="#2a3038">0</text>'
                f'<text x="{sb_x + bar_px}" y="{sb_y + 16}" text-anchor="end" font-size="9" font-family="Arial,sans-serif" fill="#2a3038">{dist_label}</text>'
                "</g>"
            )

    # Legend (bottom-right)
    if toggles.get("show_legend", True):
        legend_entries = _collect_legend_entries(scene, palette)
        if legend_entries:
            lg_x = width - 180
            lg_y = height - 20 - len(legend_entries) * 20 - 28
            lg_parts = [
                f'<rect x="{lg_x - 8}" y="{lg_y - 8}" width="180" height="{len(legend_entries) * 20 + 36}" rx="6" fill="#f8f6f1" fill-opacity="0.88" stroke="#d5d1c8" />'
            ]
            lg_parts.append(
                f'<text x="{lg_x}" y="{lg_y + 12}" font-size="10" font-family="Arial,sans-serif" fill="#126a8b" font-weight="bold">LEGEND</text>'
            )
            lg_cy = lg_y + 28
            for label, color_hex, shape_type in legend_entries:
                if shape_type == "rect":
                    lg_parts.append(
                        f'<rect x="{lg_x}" y="{lg_cy}" width="12" height="12" fill="{color_hex}" stroke="#5a6068" stroke-opacity="0.5" stroke-width="0.5" />'
                    )
                elif shape_type == "circle":
                    lg_parts.append(
                        f'<circle cx="{lg_x + 6}" cy="{lg_cy + 6}" r="6" fill="{color_hex}" stroke="#5a6068" stroke-opacity="0.5" stroke-width="0.5" />'
                    )
                elif shape_type == "line":
                    lg_parts.append(
                        f'<line x1="{lg_x}" y1="{lg_cy + 6}" x2="{lg_x + 12}" y2="{lg_cy + 6}" stroke="{color_hex}" stroke-width="3" />'
                    )
                lg_parts.append(
                    f'<text x="{lg_x + 18}" y="{lg_cy + 10}" font-size="9" font-family="Arial,sans-serif" fill="#2a3038">{label}</text>'
                )
                lg_cy += 20
            overlay_parts.append(f'<g id="legend">{"".join(lg_parts)}</g>')

    overlay_markup = "".join(overlay_parts)

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'<defs><clipPath id="siteClip"><path d="{boundary_path}" /></clipPath></defs>'
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{palette["paper"]}" />'
        f'<path d="{boundary_path}" fill="{palette["site"]}" />'
        f'<g id="geometry-layer" clip-path="url(#siteClip)">{geometry_markup}</g>'
        f"{overlay_markup}"
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


def _derive_board_title(title: str, scene: dict[str, Any]) -> tuple[str, str]:
    """Derive a dynamic board heading and subtitle from project context.

    Returns (heading, subtitle) — e.g. ("ILLUSTRATIVE MASTER PLAN", "Mixed-Use Urban Village").
    """
    clean_title = _normalize_whitespace(title)

    # Collect zone typologies for a descriptive subtitle
    zone_types: list[str] = []
    for zone in scene.get("prompt_zones", []):
        zt = _normalize_zone_type(zone.get("zone_type"))
        props = zone.get("properties") if isinstance(zone.get("properties"), dict) else {}
        gsi = props.get("generation_style_input") if isinstance(props.get("generation_style_input"), dict) else {}
        label = _normalize_whitespace(gsi.get("archetypeLabel") or gsi.get("subtype") or zone.get("name") or "")
        if label:
            zone_types.append(label)
        elif zt in {"building", "residential", "development_area"}:
            zone_types.append("Development")
        elif zt == "green_space":
            zone_types.append("Green Space")
        elif zt == "road":
            zone_types.append("Road Network")

    # Build heading — project name if available, else generic
    if clean_title:
        heading = clean_title.upper()
    else:
        heading = "ILLUSTRATIVE MASTER PLAN"

    # Build subtitle from unique zone types (max 3)
    seen: set[str] = set()
    unique_types: list[str] = []
    for zt in zone_types:
        key = zt.lower()
        if key not in seen:
            seen.add(key)
            unique_types.append(zt)
    subtitle = " \u2022 ".join(unique_types[:3]) if unique_types else "Master Plan"

    return heading, subtitle


def _collect_legend_entries(
    scene: dict[str, Any],
    palette: dict[str, str],
) -> list[tuple[str, str, str]]:
    """Collect legend entries as (label, color_hex, shape_type) from the scene.

    shape_type is one of: "rect", "circle", "line".
    """
    entries: list[tuple[str, str, str]] = []

    # Building typologies present in the scene
    typology_seen: set[str] = set()
    for building in scene.get("pixel", {}).get("building_footprints", []) + scene.get("pixel", {}).get(
        "building_masses", []
    ):
        props = building.get("properties") or {}
        height_m = _feature_height_m(building)
        typology = _classify_building_typology(props, height_m)
        typology_seen.add(typology)

    typology_labels = {
        "townhouse": "Townhouse",
        "midrise": "Mid-Rise Residential",
        "highrise": "High-Rise Tower",
        "mixed_use": "Mixed-Use",
        "commercial": "Commercial",
        "generic": "Building",
    }
    for typo in ["townhouse", "midrise", "highrise", "mixed_use", "commercial", "generic"]:
        if typo in typology_seen:
            color = _ROOF_COLORS.get(typo, _ROOF_COLORS["generic"])
            entries.append((typology_labels.get(typo, typo.title()), color, "rect"))

    # Parks / green space
    if scene.get("pixel", {}).get("parks"):
        entries.append(("Park / Green Space", palette.get("park", "#7ab86a"), "circle"))

    # Roads
    if scene.get("pixel", {}).get("roads"):
        entries.append(("Road", palette.get("road", "#a09c94"), "line"))

    # Paths
    if scene.get("pixel", {}).get("paths"):
        entries.append(("Pedestrian Path", palette.get("path", "#d0c8b6"), "line"))

    # Water
    if scene.get("pixel", {}).get("water"):
        entries.append(("Water Feature", palette.get("water", "#6aa8cc"), "rect"))

    # Plazas
    if scene.get("pixel", {}).get("plazas"):
        entries.append(("Plaza / Hardscape", _blend_hex(palette.get("road", "#a09c94"), "#d4c8b0", 0.4), "rect"))

    return entries


def _draw_north_arrow(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int) -> None:
    """Draw a minimal north arrow at (cx, cy) with given size."""
    half = size // 2
    tip = (cx, cy - half)
    bl = (cx - size // 5, cy + half)
    br = (cx + size // 5, cy + half)
    # Dark filled triangle
    draw.polygon([tip, bl, br], fill=_hex_to_rgba("#2a3038", 255))
    # White right half for contrast
    mid_bottom = (cx, cy + half)
    draw.polygon([tip, mid_bottom, br], fill=_hex_to_rgba("#5a6068", 220))
    # "N" label above
    draw.text((cx - 4, cy - half - 16), "N", fill=_hex_to_rgba("#2a3038", 255))


def _draw_scale_bar(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    bar_width_px: int,
    distance_m: float,
    palette: dict[str, str],
) -> None:
    """Draw a scale bar at (x, y) with alternating black/white segments."""
    segments = 4
    seg_w = bar_width_px // segments
    bar_h = 5
    for i in range(segments):
        sx = x + i * seg_w
        fill = _hex_to_rgba("#2a3038", 255) if i % 2 == 0 else _hex_to_rgba("#f4f1e8", 255)
        draw.rectangle((sx, y, sx + seg_w, y + bar_h), fill=fill, outline=_hex_to_rgba("#2a3038", 200))
    # Labels
    if distance_m >= 1000:
        label = f"{distance_m / 1000:.1f} km"
    else:
        label = f"{int(distance_m)} m"
    draw.text((x, y + bar_h + 3), "0", fill=_hex_to_rgba("#2a3038", 255))
    draw.text((x + bar_width_px - len(label) * 6, y + bar_h + 3), label, fill=_hex_to_rgba("#2a3038", 255))


def _draw_legend_block(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    entries: list[tuple[str, str, str]],
    max_width: int,
) -> int:
    """Draw a legend block and return the total height consumed."""
    if not entries:
        return 0
    row_h = 22
    swatch_size = 14
    cursor_y = y
    # Section header
    draw.text((x, cursor_y), "LEGEND", fill=_hex_to_rgba("#126a8b", 255))
    cursor_y += 24
    draw.line((x, cursor_y, x + max_width - 32, cursor_y), fill=_hex_to_rgba("#d6d2c8", 255), width=1)
    cursor_y += 8

    for label, color_hex, shape_type in entries:
        sx = x
        sy = cursor_y + 3
        swatch_fill = _hex_to_rgba(color_hex, 255)
        if shape_type == "rect":
            draw.rectangle(
                (sx, sy, sx + swatch_size, sy + swatch_size), fill=swatch_fill, outline=_hex_to_rgba("#5a6068", 120)
            )
        elif shape_type == "circle":
            draw.ellipse(
                (sx, sy, sx + swatch_size, sy + swatch_size), fill=swatch_fill, outline=_hex_to_rgba("#5a6068", 120)
            )
        elif shape_type == "line":
            mid_y = sy + swatch_size // 2
            draw.line((sx, mid_y, sx + swatch_size, mid_y), fill=swatch_fill, width=3)
        draw.text((sx + swatch_size + 8, cursor_y + 1), label, fill=_hex_to_rgba("#2a3038", 255))
        cursor_y += row_h

    return cursor_y - y


def _compose_board_image(
    title: str,
    plan_image: Image.Image,
    scene: dict[str, Any],
    *,
    board_template: str,
    include_photo_strip: bool,
    reference_images: Sequence[str] | None,
    palette: dict[str, str] | None = None,
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

    # --- Right Panel Content ---
    rx = right_rect[0] + 16
    ry = right_rect[1] + 16
    rw = right_rect[2] - right_rect[0]

    # Dynamic title
    heading, subtitle = _derive_board_title(title, scene)
    draw.text((rx, ry), heading, fill=_hex_to_rgba("#126a8b", 255))
    ry += 28
    draw.text((rx, ry), subtitle, fill=_hex_to_rgba("#4a5a52", 255))
    ry += 24
    draw.line((rx, ry, right_rect[2] - 16, ry), fill=_hex_to_rgba("#d6d2c8", 255), width=1)
    ry += 14

    # Site statistics
    stats_lines: list[str] = []
    boundary = scene.get("boundary")
    if boundary is not None and hasattr(boundary, "area"):
        try:
            center_lat = (boundary.bounds[1] + boundary.bounds[3]) / 2.0
            m_per_deg_lon = _meters_per_degree_lon(center_lat)
            m_per_deg_lat = _meters_per_degree_lat(center_lat)
            area_m2 = boundary.area * m_per_deg_lon * m_per_deg_lat
            if area_m2 > 10000:
                stats_lines.append(f"Site Area: {area_m2 / 10000:.1f} ha")
            else:
                stats_lines.append(f"Site Area: {area_m2:.0f} m\u00b2")
        except Exception:
            pass

    n_buildings = len(scene.get("pixel", {}).get("building_footprints", [])) + len(
        scene.get("pixel", {}).get("building_masses", [])
    )
    if n_buildings:
        stats_lines.append(f"Buildings: {n_buildings}")
    n_parks = len(scene.get("pixel", {}).get("parks", []))
    if n_parks:
        stats_lines.append(f"Parks & Green: {n_parks}")

    if stats_lines:
        draw.text((rx, ry), "SITE STATISTICS", fill=_hex_to_rgba("#126a8b", 230))
        ry += 20
        for stat_line in stats_lines:
            draw.text((rx, ry), stat_line, fill=_hex_to_rgba("#2a3038", 255))
            ry += 18
        ry += 10
        draw.line((rx, ry, right_rect[2] - 16, ry), fill=_hex_to_rgba("#d6d2c8", 255), width=1)
        ry += 14

    # Legend
    use_palette = palette or STYLE_PALETTES.get("rendered_sales_plan", {})
    legend_entries = _collect_legend_entries(scene, use_palette)
    if legend_entries:
        legend_h = _draw_legend_block(draw, rx, ry, legend_entries, rw)
        ry += legend_h + 14
        draw.line((rx, ry, right_rect[2] - 16, ry), fill=_hex_to_rgba("#d6d2c8", 255), width=1)
        ry += 14

    # North arrow — positioned in the right panel
    arrow_cx = right_rect[2] - 40
    arrow_cy = right_rect[3] - 70
    _draw_north_arrow(draw, arrow_cx, arrow_cy, 36)

    # Scale bar — bottom of right panel
    pixels_per_meter = float(scene.get("pixels_per_meter") or 1.0)
    if pixels_per_meter > 0.01:
        # Choose a round distance that produces a bar ~40-70% of right panel width
        target_bar_px = int(rw * 0.55)
        target_dist_m = target_bar_px / pixels_per_meter
        # Round to a nice number
        nice_distances = [10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 5000]
        chosen_m = nice_distances[0]
        for nd in nice_distances:
            if nd <= target_dist_m * 1.5:
                chosen_m = nd
        bar_px = int(chosen_m * pixels_per_meter)
        bar_px = max(40, min(bar_px, rw - 40))
        _draw_scale_bar(draw, rx, right_rect[3] - 34, bar_px, float(chosen_m), use_palette)

    # Reference photo strip (bottom of right panel, above scale bar)
    valid_refs = _valid_reference_urls(reference_images)
    render_reference_strip = include_photo_strip and len(valid_refs) > 0
    strip_top = right_rect[3] - int(height * 0.20)
    if render_reference_strip:
        draw.text((rx, strip_top - 28), "REFERENCE IMAGES", fill=_hex_to_rgba("#126a8b", 230))
        thumb_h = int(height * 0.07)
        thumb_w = int((rw - 36) / max(min(len(valid_refs), 3), 1))
        for idx, url in enumerate(valid_refs[:3]):
            x0 = rx + idx * (thumb_w + 6)
            y0 = strip_top
            color_hash = hashlib.sha1(url.encode("utf-8")).hexdigest()
            fill = f"#{color_hash[0:6]}"
            draw.rounded_rectangle((x0, y0, x0 + thumb_w, y0 + thumb_h), radius=6, fill=_hex_to_rgba(fill, 255))

    board_meta = {
        "template": board_template,
        "left_panel": {
            "x": left_rect[0],
            "y": left_rect[1],
            "width": left_rect[2] - left_rect[0],
            "height": left_rect[3] - left_rect[1],
        },
        "right_panel": {
            "x": right_rect[0],
            "y": right_rect[1],
            "width": right_rect[2] - right_rect[0],
            "height": right_rect[3] - right_rect[1],
        },
        "reference_strip_rendered": render_reference_strip,
        "reference_strip_count": len(valid_refs) if render_reference_strip else 0,
        "scene_geometry_hash": scene.get("geometry_hash"),
        "legend_entry_count": len(legend_entries),
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
    style_pass_surface_directive = (
        "Treat the entire site as one coherent orthographic aerial image with one light direction, one atmospheric condition, and one continuous material world."
        if style_preset in {"photorealistic_aerial", "photoreal_orthographic_aerial"}
        else "Treat the entire site as one continuous sheet with one palette family, one light direction, and one shared paper texture."
    )
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
            archetype = _normalize_whitespace(
                gsi.get("archetypeLabel")
                or gsi.get("subtype")
                or zone.get("name")
                or "the defined architectural precinct"
            )
            directive = f"Render the roof plan and building footprint for {archetype}."
        elif zone_type == "green_space":
            gsi_all = (
                props.get("generation_style_inputs") if isinstance(props.get("generation_style_inputs"), dict) else {}
            )
            park = gsi_all.get("parks") if isinstance(gsi_all.get("parks"), dict) else {}
            profile = park.get("styleProfile") if isinstance(park.get("styleProfile"), dict) else {}
            landscape = _normalize_whitespace(
                profile.get("landscapeCharacter") or park.get("subcategory") or "formal civic garden composition"
            )
            directive = f"Render a top-down landscape plan with {landscape}."
        elif zone_type == "road":
            gsi_all = (
                props.get("generation_style_inputs") if isinstance(props.get("generation_style_inputs"), dict) else {}
            )
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

    # Inject style-specific prompt from the catalog
    catalog_entry = RENDER_STYLE_CATALOG.get(style_preset)
    if catalog_entry and catalog_entry.get("prompt"):
        lines.append(f"AESTHETIC TARGET: {catalog_entry['prompt']}")
        if catalog_entry.get("negative_prompt"):
            lines.append(f"AVOID: {catalog_entry['negative_prompt']}")

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

    # Look up blend factor from catalog
    render_style = str(variant.get("render_style_preset") or "")
    catalog_entry = RENDER_STYLE_CATALOG.get(render_style, {})
    blend_factor = float(catalog_entry.get("compositing_blend", 0.33))

    # ── Style-specific pre-processing on the AI image ─────────────────
    if render_style == "lush_landscape":
        styled = ImageEnhance.Color(styled).enhance(1.15)  # boost green saturation
    elif render_style == "marker_render":
        styled = ImageEnhance.Contrast(styled).enhance(1.20)  # bolder markers
    elif render_style == "watercolor_wash":
        # Warm paper-colour overlay before blend
        paper_wash = Image.new("RGBA", styled.size, (245, 239, 230, 18))
        styled.alpha_composite(paper_wash)

    boundary = _polygon_from_geometry(scene.get("pixel", {}).get("boundary"))
    if boundary is None:
        blended = Image.blend(base, styled, min(blend_factor, 0.30))
        return blended

    # ── Boundary-aware blend mask ─────────────────────────────────────
    # Full blend inside zone, reduced outside, smooth 5px transition
    inside_mask = Image.new("L", base.size, 0)
    mask_draw = ImageDraw.Draw(inside_mask)
    mask_draw.polygon(_polygon_coords(boundary), fill=255)
    # Smooth transition at edge
    inside_mask_blurred = inside_mask.filter(ImageFilter.GaussianBlur(radius=5.0))

    # Inside: full blend_factor.  Outside: reduced (0.25 × blend_factor)
    import numpy as np

    inside_arr = np.array(inside_mask_blurred, dtype=np.float32) / 255.0
    outside_blend = blend_factor * 0.25
    blend_arr = outside_blend + (blend_factor - outside_blend) * inside_arr
    # Build per-pixel alpha mask for the styled layer
    alpha_mask_arr = (blend_arr * 255).clip(0, 255).astype(np.uint8)
    alpha_mask = Image.fromarray(alpha_mask_arr, mode="L")

    merged = Image.composite(styled, base, alpha_mask)

    contrast = 1.02 + (int(variant.get("seed") or 0) % 3) * 0.01
    merged = ImageEnhance.Contrast(merged).enhance(contrast)
    saturation = 1.03 if variant.get("quality_level") == "board_ready" else 1.0
    merged = ImageEnhance.Color(merged).enhance(saturation)

    # ── Post-composition sharpening ───────────────────────────────────
    merged = ImageEnhance.Sharpness(merged).enhance(1.12)

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
        return None, "STABILITY_API_KEY not configured"
    try:
        httpx = importlib.import_module("httpx")
    except Exception as exc:
        return None, f"stability http client unavailable: {exc}"

    image_bytes = _image_to_png_bytes(control_image.convert("RGB"))
    url = f'{settings.stability_api_base.rstrip("/")}/v2beta/stable-image/control/structure'
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
                "control_strength": f"{max(0.0, min(control_strength, 1.0)):.2f}",
                "output_format": "png",
            },
            files={"image": ("structure.png", image_bytes, "image/png")},
            timeout=90.0,
        )
        response.raise_for_status()
        styled = Image.open(io.BytesIO(response.content)).convert("RGBA")
        return styled, None
    except Exception as exc:
        return None, f"stability structure pass failed: {exc}"


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


def _run_fal_style_pass(
    *,
    base_image: Image.Image,
    prompt: str,
    negative_prompt: str,
    strength: float = 0.65,
) -> tuple[Image.Image | None, str | None]:
    """Run an image-to-image style pass via fal.ai (SDXL or configured model)."""
    fal_key = getattr(settings, "fal_key", "") or ""
    if not fal_key:
        return None, "FAL_KEY not configured"
    try:
        fal_client = importlib.import_module("fal_client")
    except Exception as exc:
        return None, f"fal_client unavailable: {exc}"

    # Encode image as data-URI so we don't need to upload to fal CDN
    import base64 as _b64

    image_bytes = _image_to_png_bytes(base_image.convert("RGB"))
    data_uri = "data:image/png;base64," + _b64.b64encode(image_bytes).decode("ascii")

    fal_model = str(getattr(settings, "fal_style_model", "") or FAL_DEFAULT_STYLE_MODEL)
    try:
        # Set FAL_KEY in environment for the client library
        import os as _os

        _os.environ["FAL_KEY"] = fal_key

        result = fal_client.run(
            fal_model,
            arguments={
                "prompt": prompt,
                "image_url": data_uri,
                "strength": max(0.05, min(1.0, strength)),
                "guidance_scale": 7.5,
                "num_inference_steps": 30,
                "negative_prompt": negative_prompt,
                "num_images": 1,
                "format": "png",
                "enable_safety_checker": False,
                "image_size": {
                    "width": base_image.width,
                    "height": base_image.height,
                },
            },
        )

        images = result.get("images") if isinstance(result, dict) else None
        if not images or not isinstance(images, list) or len(images) == 0:
            return None, "fal style pass returned no images"

        image_url = images[0].get("url") if isinstance(images[0], dict) else None
        if not image_url:
            return None, "fal style pass returned no image URL"

        # Download the result image
        httpx = importlib.import_module("httpx")
        img_response = httpx.get(image_url, timeout=30.0)
        img_response.raise_for_status()
        styled = Image.open(io.BytesIO(img_response.content)).convert("RGBA")
        return styled, None
    except Exception as exc:
        return None, f"fal style pass failed: {exc}"


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
    # Check catalog — skip AI pass for styles that don't use it
    render_style = str(variant.get("render_style_preset") or style_preset or "")
    catalog_entry = RENDER_STYLE_CATALOG.get(render_style, {})
    if catalog_entry.get("denoising_strength", 1.0) <= 0.0 or catalog_entry.get("provider_preference") == "none":
        return base_image, {
            "requested": True,
            "applied": False,
            "reason": f"Style '{render_style}' uses deterministic rendering only (no AI pass)",
            "provider": None,
            "model": None,
            "control_mode": None,
            "requested_provider": provider_preference,
            "attempted_providers": [],
        }

    # Pre-processing for specific styles
    working_image = base_image
    if render_style == "white_massing_model":
        # Desaturate the base image to greyscale before AI pass
        grey = ImageEnhance.Color(working_image.convert("RGBA")).enhance(0.0)
        working_image = ImageEnhance.Brightness(grey).enhance(1.15)
    elif render_style == "cinematic_dusk":
        # Shift base toward blue/amber dusk tones before AI pass
        dusk_wash = Image.new("RGBA", working_image.size, (20, 30, 60, 40))
        working_image = Image.alpha_composite(working_image.convert("RGBA"), dusk_wash)
        working_image = ImageEnhance.Brightness(working_image).enhance(0.65)

    # Use catalog provider preference if not overridden
    effective_provider = provider_preference
    if effective_provider == "auto" and catalog_entry.get("provider_preference") not in (None, "any", "none"):
        effective_provider = catalog_entry["provider_preference"]

    providers = ["gemini", "fal", "stability"] if effective_provider == "auto" else [effective_provider]
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
            styled, error = _run_gemini_style_pass(base_image=working_image, prompt=prompt_text)
            if styled is not None:
                composited = _compose_ai_style_pass(working_image, styled, scene, variant)
                status["applied"] = True
                status["provider"] = "gemini"
                status["model"] = str(
                    getattr(settings, "master_plan_2d_style_model", "") or "gemini-3.1-flash-image-preview"
                )
                status["reason"] = None
                return composited, status
        elif provider == "stability":
            styled = None
            error = None
            structure_image = control_maps.get("structure") if isinstance(control_maps, dict) else None
            if variant.get("orthographic_mode") and isinstance(structure_image, Image.Image):
                styled, error = _run_stability_structure_pass(
                    control_image=structure_image,
                    prompt=prompt_text,
                    negative_prompt=STYLE_PASS_NEGATIVE_PROMPT,
                    control_strength=float(variant.get("stability_control_strength") or 0.88),
                )
                if styled is not None:
                    composited = _compose_ai_style_pass(working_image, styled, scene, variant)
                    status["applied"] = True
                    status["provider"] = "stability"
                    status["model"] = STABILITY_STRUCTURE_MODEL
                    status["reason"] = None
                    status["control_mode"] = "structure"
                    return composited, status
            styled, error = _run_stability_style_pass(
                base_image=working_image,
                prompt=prompt_text,
                negative_prompt=STYLE_PASS_NEGATIVE_PROMPT,
            )
            if styled is not None:
                composited = _compose_ai_style_pass(working_image, styled, scene, variant)
                status["applied"] = True
                status["provider"] = "stability"
                status["model"] = STABILITY_STYLE_PASS_MODEL
                status["reason"] = None
                status["control_mode"] = "search_and_replace"
                return composited, status
        elif provider == "fal":
            denoising = float(catalog_entry.get("denoising_strength", 0.65))
            styled, error = _run_fal_style_pass(
                base_image=working_image,
                prompt=prompt_text,
                negative_prompt=STYLE_PASS_NEGATIVE_PROMPT,
                strength=denoising,
            )
            if styled is not None:
                composited = _compose_ai_style_pass(working_image, styled, scene, variant)
                status["applied"] = True
                status["provider"] = "fal"
                status["model"] = str(getattr(settings, "fal_style_model", "") or FAL_DEFAULT_STYLE_MODEL)
                status["reason"] = None
                status["control_mode"] = "image_to_image"
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
    map_screenshot_bounds: Any = None,
    render_mode: str | None = None,
) -> dict[str, Any]:
    _ = debug
    variant = _make_variant_profile(
        style_preset,
        quality_level,
        variant_index,
        scene["geometry_hash"],
        render_style_preset=render_style_preset,
        lighting_atmosphere_preset=lighting_atmosphere_preset,
        render_mode=render_mode,
    )
    context_underlay, context_underlay_status = _resolve_context_underlay(
        scene,
        render_mode=render_mode,
        render_style_preset=render_style_preset,
        map_screenshot_satellite=map_screenshot_satellite,
        map_screenshot_bounds=map_screenshot_bounds,
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
        "conditioning_mode": (
            "stability_structure_ready" if variant.get("orthographic_mode") else "deterministic_control_maps_only"
        ),
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
            palette=variant.get("palette"),
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
    buckets: dict[str, list[str]] = {
        "aesthetic": [],
        "architectural": [],
        "materials": [],
        "roof": [],
        "landscape": [],
        "paving": [],
        "typologies": [],
        "district": [],
    }
    seen: dict[str, set[str]] = {key: set() for key in buckets}

    def remember(bucket: str, value: Any) -> None:
        text_value = _normalize_whitespace(value)
        if not text_value:
            return
        token = text_value.lower()
        if token in seen[bucket]:
            return
        seen[bucket].add(token)
        buckets[bucket].append(text_value)

    def ingest_style_input(payload: dict[str, Any]) -> None:
        profile = payload.get("styleProfile") if isinstance(payload.get("styleProfile"), dict) else {}
        remember(
            "aesthetic",
            payload.get("aestheticCategoryLabel")
            or payload.get("subcategory")
            or payload.get("buildingSubcategory")
            or payload.get("subtype"),
        )
        remember(
            "typologies",
            payload.get("archetypeLabel")
            or payload.get("buildingSubcategory")
            or payload.get("subcategory")
            or payload.get("subtype"),
        )
        remember(
            "architectural", profile.get("massing") or profile.get("streetRelationship") or profile.get("publicRealm")
        )
        materials = payload.get("materials") or profile.get("materials")
        if isinstance(materials, (list, tuple)):
            remember("materials", ", ".join(str(item) for item in materials if _normalize_whitespace(item)))
        else:
            remember("materials", materials)
        remember("roof", profile.get("roofForm"))
        remember(
            "landscape", profile.get("plantingType") or profile.get("landscapeCharacter") or profile.get("publicRealm")
        )
        remember("paving", profile.get("pavingType"))

    for zone in zones:
        props = getattr(zone, "properties", None)
        if not isinstance(props, dict):
            continue
        remember("aesthetic", props.get("development_type"))
        remember("materials", props.get("facade_material"))
        remember("roof", props.get("roof_style") or props.get("roof_type"))
        remember("landscape", props.get("ground_texture") or props.get("green_space_aesthetic"))
        remember("paving", props.get("paving_material") or props.get("road_surface"))
        description = _normalize_whitespace(props.get("description_text"))
        if description:
            lowered = description.lower()
            if any(
                token in lowered
                for token in (
                    "mixed-use",
                    "mixed use",
                    "main street",
                    "retail",
                    "townhouse",
                    "rowhouse",
                    "courtyard",
                    "podium",
                    "tower",
                )
            ):
                remember("typologies", description)
            if any(
                token in lowered
                for token in ("park", "civic", "plaza", "pond", "water", "green", "public realm", "promenade", "mews")
            ):
                remember("district", description)

        generation_style_input = props.get("generation_style_input")
        if isinstance(generation_style_input, dict):
            ingest_style_input(generation_style_input)

        generation_style_inputs = props.get("generation_style_inputs")
        if isinstance(generation_style_inputs, dict):
            for payload in generation_style_inputs.values():
                if isinstance(payload, dict):
                    ingest_style_input(payload)

    typology_mix = (
        ", ".join(buckets["typologies"][:3])
        or "mixed-use podium blocks, courtyard mid-rise housing, and fine-grain residential edges"
    )
    district_structure = (
        ", ".join(buckets["district"][:2])
        or "perimeter-aligned blocks, internal mews, structured forecourts, planted courtyards, and at least one civic landscape anchor"
    )
    context_alignment = "align new blocks and streets to real surrounding roads and neighboring houses while keeping context subdued and secondary"

    return {
        "aesthetic_category": ", ".join(buckets["aesthetic"][:2]) or "eco-urban mixed-use",
        "architectural_language": ", ".join(buckets["architectural"][:2])
        or "contemporary mixed-use urban architecture with disciplined street walls and readable roof planes",
        "facade_materials": ", ".join(buckets["materials"][:2]) or "refined concrete, brick, and glazing",
        "roof_style": ", ".join(buckets["roof"][:2]) or "articulated contemporary roof expression",
        "landscape_character": ", ".join(buckets["landscape"][:2])
        or "layered planting, courtyards, civic greens, and pedestrian-focused public realm",
        "paving_type": ", ".join(buckets["paving"][:2])
        or "warm neutral paving, asphalt streets, and crisp sidewalk edges",
        "typology_mix": typology_mix,
        "district_structure": district_structure,
        "context_alignment": context_alignment,
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
    typology_mix: str,
    district_structure: str,
    context_alignment: str,
    global_style_payload: str,
) -> str:
    return (
        f"Create a premium professional orthographic aerial district visualization for a proposed urban redevelopment in {city_context}. "
        "Render the proposal in a true top-down orthographic to controlled slight aerial-oblique view, preserving the exact site footprint, block geometry, podium arrangement, tower placement, courtyard organization, path network, and public realm structure defined by the project geometry.\n\n"
        "This is an image of the SITE AND ITS IMMEDIATE DISTRICT CONTEXT ONLY, not a presentation board.\n\n"
        f"Render a complete {aesthetic_category} district with approximately {height_m:.1f} m / {floor_count} storey development intensity. "
        f"Typology mix: {typology_mix}. "
        "Show clear tower footprints, podium edges, street walls, rowhouse or fine-grain edge conditions where appropriate, framed urban corners, refined roof planes, planted terraces, green roofs where appropriate, active storefront frontage, canopies, widened sidewalks, serviceable internal mews, parking courts, elegant paving, and high-quality urban open space.\n\n"
        f"Architectural language: {architectural_language}. Materials and expression: {facade_materials}, {roof_style}, {landscape_character}, {paving_type}. "
        f"District construction rules: {district_structure}. Context alignment: {context_alignment}. "
        "Every residual area inside the site must resolve into building, street, sidewalk, plaza, parking, landscape, or water; do not leave undefined pale filler.\n\n"
        "Use strong contrast, crisp edges, realistic roof detail, believable asphalt and curb geometry, deep but controlled planting, warm neutral hardscape, refined glazing and concrete tones, and premium developer-visualization quality. "
        "Surrounding context must remain subdued and slightly desaturated so the proposal reads as the visual focus while still matching real-world roads and houses.\n\n"
        f"{global_style_payload}\n\n"
        "Important: do not generate any presentation-board graphics or UI. No title, no legend, no labels, no callout markers, no north arrow, no scale bar, no reference strip, no descriptive copy, and no text of any kind. "
        "Do not create a collage, diagram board, or faded conceptual wash. Do not simplify the proposal into blank beige bars, floating blocks, or generic massing. "
        "The result must read as a believable, detailed, premium architectural district image."
    )


def _collect_scene_payload(
    project: Project, zones: Sequence[SiteZone], buildings: Sequence[Building]
) -> dict[str, Any]:
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

    for zone in sorted(
        zones, key=lambda item: (getattr(item, "sort_order", 0), getattr(item, "created_at", _now_utc()))
    ):
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
            osm_context = properties.get("_osm_context") if isinstance(properties, dict) else None
            if isinstance(osm_context, dict):
                _append_osm_context_layers(scene, boundary, osm_context)
            continue

        if zone_type in {"building", "residential", "development_area"}:
            scene["buildable_zones"].append(
                {"geometry": geometry, "name": getattr(zone, "name", None), "properties": properties}
            )
            generated_footprints: list[dict[str, Any]] = []
            if zone_type == "building":
                if _should_generate_precinct_for_building_zone(geometry, properties):
                    generated_footprints = _generate_precinct_footprints(zone, geometry, scene)
                    for footprint in generated_footprints:
                        scene["building_footprints"].append(footprint)
                else:
                    scene["building_footprints"].append(
                        {"geometry": geometry, "name": getattr(zone, "name", None), "properties": properties}
                    )
            else:
                generated_footprints = _generate_precinct_footprints(zone, geometry, scene)
                for footprint in generated_footprints:
                    scene["building_footprints"].append(footprint)

            if generated_footprints:
                generated_site = _generate_precinct_site_features(
                    geometry,
                    generated_footprints,
                    zone_name=getattr(zone, "name", None),
                    zone_properties=properties,
                )
                scene["roads"].extend(generated_site.get("roads", []))
                scene["paths"].extend(generated_site.get("paths", []))
                scene["parks"].extend(generated_site.get("parks", []))
                scene["plazas"].extend(generated_site.get("plazas", []))
                scene["water"].extend(generated_site.get("water", []))
        elif zone_type == "road":
            scene["roads"].append(
                {
                    "geometry": geometry,
                    "kind": "road",
                    "width_m": float(properties.get("width") or 8.0),
                    "properties": properties,
                }
            )
        elif zone_type == "green_space":
            scene["parks"].append({"geometry": geometry, "name": getattr(zone, "name", None), "properties": properties})
        elif zone_type == "water":
            scene["water"].append({"geometry": geometry, "name": getattr(zone, "name", None), "properties": properties})
        elif zone_type == "parking":
            scene["plazas"].append(
                {"geometry": geometry, "name": getattr(zone, "name", None), "properties": properties}
            )
        scene["prompt_zones"].append(zone_payload)

    if boundary is None:
        candidates = [item["geometry"] for item in scene["buildable_zones"]]
        if not candidates:
            candidates = [
                item["geometry"]
                for item in scene["parks"] + scene["roads"] + scene["plazas"] + scene["water"]
                if item.get("geometry")
            ]
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
        scene["context_buildings"].append(
            {"geometry": footprint, "name": getattr(building, "name", None), "properties": {"source": "building_model"}}
        )

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
        "district_blocks",
    ]
    deterministic_seed = int(hashlib.sha1(f"{zone_id}:{description}".encode("utf-8")).hexdigest()[:8], 16)
    hint_text = " ".join(
        str(properties.get(key) or "")
        for key in ("development_type", "development_subcategory", "development_archetype_label", "description_text")
    ).lower()
    if any(token in hint_text for token in ("townhouse", "rowhouse", "row house")):
        grammar = "townhouse_courtyard"
    elif any(token in hint_text for token in ("mid-rise", "mid rise", "courtyard", "perimeter", "court")):
        grammar = "perimeter_courtyard"
    elif any(token in hint_text for token in ("mixed-use", "mixed use", "retail", "main street", "podium")):
        grammar = "mixed_use_edge"
    elif zone_geometry.area > 0.00000045:
        grammar = "district_blocks"
    else:
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
            poly = box(
                minx + width * g - bar_w / 2, miny + height * 0.18, minx + width * g + bar_w / 2, miny + height * 0.84
            )
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
    elif grammar == "district_blocks":
        pieces = [
            box(minx + width * 0.10, miny + height * 0.10, minx + width * 0.34, miny + height * 0.34),
            box(minx + width * 0.40, miny + height * 0.10, minx + width * 0.68, miny + height * 0.28),
            box(minx + width * 0.72, miny + height * 0.12, minx + width * 0.90, miny + height * 0.42),
            box(minx + width * 0.14, miny + height * 0.54, minx + width * 0.40, miny + height * 0.86),
            box(minx + width * 0.48, miny + height * 0.58, minx + width * 0.88, miny + height * 0.82),
        ]
        for piece in pieces:
            clipped = _polygon_from_geometry(piece.intersection(usable))
            if clipped is not None and clipped.area > 0:
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
                    "floor_count": properties.get("floor_count")
                    or properties.get("floors")
                    or properties.get("floorCount"),
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
    logger.warning(
        "Zone %s contains malformed properties payload (%s)", getattr(zone, "id", "unknown"), type(properties).__name__
    )
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
        zone_id = str(
            getattr(zone, "zone_id", None)
            or (zone.get("zone_id") if isinstance(zone, dict) else "")
            or f"zone-{idx + 1}"
        )
        zone_type_raw = getattr(zone, "zone_type", None) if not isinstance(zone, dict) else zone.get("zone_type")
        zone_type = _normalize_zone_type(zone_type_raw)
        polygon_payload = getattr(zone, "polygon", None) if not isinstance(zone, dict) else zone.get("polygon")
        geometry = _polygon_from_coordinates(polygon_payload)
        if geometry is None:
            logger.warning("Skipping zone snapshot %s due to invalid polygon payload.", zone_id)
            continue
        name = (
            _normalize_whitespace(
                getattr(zone, "zone_label", None) if not isinstance(zone, dict) else zone.get("zone_label")
            )
            or f"Zone {idx + 1}"
        )
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
    polygons = [
        zone.geometry for zone in snapshot_zones if isinstance(zone.geometry, Polygon) and not zone.geometry.is_empty
    ]
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
        geometry = _polygon_from_geometry(getattr(zone, "geometry", None))
        if geometry is None or geometry.is_empty:
            continue
        zone_id = str(getattr(zone, "zone_id", getattr(zone, "id", "")))
        zone_type = _normalize_zone_type(getattr(zone, "zone_type", None))
        properties = getattr(zone, "properties", None) if isinstance(getattr(zone, "properties", None), dict) else {}
        height_m = (
            _feature_height_m({"properties": properties})
            if zone_type in {"building", "residential", "development_area"}
            else 0.0
        )
        zone_features.append(
            {
                "zone_id": zone_id,
                "zone_type": zone_type,
                "geometry": geometry,
                "properties": properties,
                "height_m": height_m,
            }
        )
        if zone_id == primary_zone_id:
            primary_polygon = geometry
            primary_height_m = max(height_m, 18.0)

    primary_centroid = primary_polygon.centroid
    focus = _world_point(primary_centroid.x, primary_centroid.y, max(primary_height_m * 0.24, 4.0))
    if selected_perspective == "street_level_eye_height":
        camera = (
            focus[0] - site_span * 0.92,
            max(14.0, min(primary_height_m * 0.42, 34.0)),
            focus[2] + site_span * 0.22,
        )
        fov_deg = 52.0
        horizon = 0.64
    elif selected_perspective == "promenade_view":
        camera = (
            focus[0] - site_span * 0.48,
            max(12.0, min(primary_height_m * 0.36, 30.0)),
            focus[2] + site_span * 0.88,
        )
        fov_deg = 47.0
        horizon = 0.62
    elif selected_perspective == "corner_perspective":
        camera = (
            focus[0] - site_span * 1.02,
            max(site_span * 0.78, primary_height_m * 2.1),
            focus[2] + site_span * 0.58,
        )
        fov_deg = 38.0
        horizon = 0.60
    else:
        camera = (
            focus[0] - site_span * 1.14,
            max(site_span * 1.10, primary_height_m * 2.5),
            focus[2] + site_span * 1.04,
        )
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
    faces.append(
        {
            "points": boundary_world,
            "massing_fill": (60, 66, 72, 255),
            "seg_fill": (54, 58, 66, 255),
            "outline": (255, 255, 255, 80),
        }
    )

    for feature in zone_features:
        geometry = feature["geometry"]
        zone_type = feature["zone_type"]
        zone_id = feature["zone_id"]
        is_primary = zone_id == primary_zone_id
        coords_world = [_world_point(x, y, 0.0) for x, y in list(geometry.exterior.coords)]
        if len(coords_world) < 4:
            continue
        if zone_type in {"building", "residential", "development_area"}:
            height_m = max(float(feature["height_m"] or 0.0), 14.0)
            top_points = [(point[0], height_m, point[2]) for point in coords_world]
            roof_fill = (224, 226, 230, 255) if is_primary else (198, 202, 208, 240)
            side_fill = (152, 158, 168, 255) if is_primary else (128, 134, 144, 220)
            seg_fill = (236, 122, 88, 255) if is_primary else (176, 98, 74, 232)
            faces.append(
                {"points": top_points, "massing_fill": roof_fill, "seg_fill": seg_fill, "outline": (255, 255, 255, 180)}
            )
            for idx in range(len(coords_world) - 1):
                side = [coords_world[idx], coords_world[idx + 1], top_points[idx + 1], top_points[idx]]
                if _face_visible(side):
                    faces.append(
                        {
                            "points": side,
                            "massing_fill": side_fill,
                            "seg_fill": seg_fill,
                            "outline": (255, 255, 255, 90),
                        }
                    )
        else:
            if zone_type == "green_space":
                massing_fill = (98, 136, 92, 255)
                seg_fill = (72, 158, 96, 255)
            elif zone_type == "water":
                massing_fill = (78, 112, 142, 255)
                seg_fill = (66, 130, 202, 255)
            elif zone_type in {"road", "parking"}:
                massing_fill = (130, 134, 140, 255) if zone_type == "road" else (182, 174, 156, 255)
                seg_fill = (92, 116, 192, 255) if zone_type == "road" else (228, 190, 128, 255)
            else:
                massing_fill = (142, 146, 150, 255)
                seg_fill = (132, 136, 142, 255)
            faces.append(
                {
                    "points": coords_world,
                    "massing_fill": massing_fill,
                    "seg_fill": seg_fill,
                    "outline": (255, 255, 255, 60),
                }
            )

    projected_faces: list[dict[str, Any]] = []
    for face in faces:
        projected_points: list[tuple[float, float]] = []
        depths: list[float] = []
        for point in face["points"]:
            projected = _project(point)
            if projected is None:
                projected_points = []
                break
            projected_points.append((projected[0], projected[1]))
            depths.append(projected[2])
        if len(projected_points) >= 3:
            projected_faces.append(
                {
                    "points": projected_points,
                    "avg_depth": sum(depths) / len(depths),
                    "massing_fill": face["massing_fill"],
                    "seg_fill": face["seg_fill"],
                    "outline": face["outline"],
                }
            )

    if not projected_faces:
        return None

    min_depth = min(face["avg_depth"] for face in projected_faces)
    max_depth = max(face["avg_depth"] for face in projected_faces)
    depth_span = max(max_depth - min_depth, 1.0)

    massing = Image.new("RGBA", (image_width, image_height), (18, 22, 28, 255))
    segmentation = Image.new("RGBA", (image_width, image_height), (20, 22, 28, 255))
    depth = Image.new("L", (image_width, image_height), 18)
    massing_draw = ImageDraw.Draw(massing, "RGBA")
    segmentation_draw = ImageDraw.Draw(segmentation, "RGBA")
    depth_draw = ImageDraw.Draw(depth)

    for face in sorted(projected_faces, key=lambda item: item["avg_depth"], reverse=True):
        depth_ratio = 1.0 - ((face["avg_depth"] - min_depth) / depth_span)
        depth_value = int(42 + depth_ratio * 196)
        massing_draw.polygon(face["points"], fill=face["massing_fill"])
        segmentation_draw.polygon(face["points"], fill=face["seg_fill"])
        depth_draw.polygon(face["points"], fill=depth_value)
        massing_draw.line(face["points"] + [face["points"][0]], fill=face["outline"], width=1)

    depth_rgba = Image.merge("RGBA", (depth, depth, depth, Image.new("L", (image_width, image_height), 255)))
    structure = Image.blend(massing, depth_rgba, 0.18)
    structure_draw = ImageDraw.Draw(structure, "RGBA")
    for face in sorted(projected_faces, key=lambda item: item["avg_depth"], reverse=True):
        structure_draw.line(face["points"] + [face["points"][0]], fill=(255, 255, 255, 96), width=1)

    return {
        "perspective_structure_image_url": _png_data_uri(_preview_png(structure, target_width=1200)),
        "perspective_depth_map_url": _png_data_uri(_preview_png(depth, target_width=1200)),
        "perspective_segmentation_map_url": _png_data_uri(_preview_png(segmentation, target_width=1200)),
        "perspective_massing_image_url": _png_data_uri(_preview_png(massing, target_width=1200)),
        "camera_perspective": selected_perspective,
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
    metadata = getattr(option, "metadata_", None) or {}
    assets = metadata.get("assets") if isinstance(metadata, dict) else {}
    control_meta = metadata.get("control_maps") if isinstance(metadata, dict) else {}
    if not isinstance(assets, dict):
        return None
    payload = {
        "structure_image_url": assets.get("control_structure_png_url"),
        "depth_map_url": assets.get("control_depth_png_url"),
        "segmentation_map_url": assets.get("control_segmentation_png_url"),
        "massing_image_url": assets.get("control_massing_png_url"),
        "control_mode": control_meta.get("conditioning_mode") if isinstance(control_meta, dict) else None,
        "control_strength": control_meta.get("control_strength") if isinstance(control_meta, dict) else None,
    }
    if any(
        payload.get(key)
        for key in ("structure_image_url", "depth_map_url", "segmentation_map_url", "massing_image_url")
    ):
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
    archetype_title = next(
        (_normalize_whitespace(item) for item in title_candidates if _normalize_whitespace(item)),
        "Mixed-Use Urban Development",
    )
    archetype_metadata["resolved_archetype_title"] = archetype_title
    return archetype_title, archetype_metadata


def _resolve_height_and_floors(
    zone: Any, properties: dict[str, Any], skipped_zones: list[dict[str, Any]]
) -> tuple[float, int]:
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
    view_family = _view_family_directive(selected_perspective)
    lighting_text = LIGHTING_VARIANTS.get(selected_lighting, LIGHTING_VARIANTS["clear_daylight"])
    lines = [
        intro,
        view_family,
        "Create this as the same approved development from the selected 2D concept image, preserving site composition, podium placement, tower placement, courtyard organization, path structure, public realm hierarchy, and neighborhood registration.",
        f"Camera/viewpoint: {selected_perspective}.",
        f"Lighting/atmosphere: {selected_lighting} ({lighting_text}).",
        f"Render the proposal as an {aesthetic_category} mixed-use development in {city_context}, with approximately {height_m:.1f} m / {floor_count} storey residential and mixed-use intensity.",
        "Maintain the same massing logic, same tower and block locations, same podium edges, same open-space structure, and same urban design intent shown in the approved 2D concept.",
        f"Architectural language: {architectural_language}. Materials and expression: {facade_materials}, {roof_style}, integrated balcony planting, planted terraces, refined concrete, brick, contemporary glazing, and high-quality detailing.",
        f"Ground-level public realm: {landscape_character}; paving language: {paving_type}; include active retail edges, canopies, widened sidewalks, street trees, furnishing, and coherent civic or courtyard space.",
        "The final image should feel premium, realistic, and coherent. Do not invent a different site plan, unrelated building arrangement, or mismatched neighborhood context.",
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
        zone_candidates = [
            zone for zone in zones if str(getattr(zone, "zone_id", getattr(zone, "id", ""))) in selected_ids
        ]
    else:
        zone_candidates = list(zones)
    if not zone_candidates:
        raise ValueError("No eligible zones with valid geometry were available to generate 3D render packages.")

    style_notes = _dedupe_sentences(
        [
            request.global_style_notes,
            (
                (getattr(option, "metadata_", {}) or {}).get("prompt")
                if isinstance(getattr(option, "metadata_", {}), dict)
                else None
            ),
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
        default="vertex",
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
            skipped_zones.append(
                {"zone_id": zone_id, "zone_label": zone_label, "reason": "Zone geometry is missing or invalid."}
            )
            continue
        clipped, clip_error = _clip_zone_polygon_to_boundary(geometry, boundary)
        if clipped is None:
            raise ValueError(clip_error or f"Zone {zone_id} could not be clipped to the site boundary.")

        properties = _extract_zone_properties(zone, skipped_zones)
        height_m, floor_count = _resolve_height_and_floors(zone, properties, skipped_zones)
        archetype_title, archetype_metadata = _zone_archetype(zone, properties)
        user_note = _normalize_whitespace(properties.get("user_notes") or properties.get("description_text"))

        architectural_language = (
            _normalize_whitespace(
                archetype_metadata.get("generation_style_input", {}).get("styleProfile", {}).get("massing")
                if isinstance(archetype_metadata.get("generation_style_input"), dict)
                else None
            )
            or "contemporary mixed-use architectural language"
        )
        facade_materials = (
            _normalize_whitespace(
                archetype_metadata.get("generation_style_input", {}).get("styleProfile", {}).get("materials")
                if isinstance(archetype_metadata.get("generation_style_input"), dict)
                else None
            )
            or "refined concrete and glazing"
        )
        roof_style = (
            _normalize_whitespace(
                archetype_metadata.get("generation_style_input", {}).get("styleProfile", {}).get("roofForm")
                if isinstance(archetype_metadata.get("generation_style_input"), dict)
                else None
            )
            or "articulated urban roof expression"
        )
        landscape_character = (
            _normalize_whitespace(
                archetype_metadata.get("generation_style_input", {}).get("styleProfile", {}).get("plantingType")
                if isinstance(archetype_metadata.get("generation_style_input"), dict)
                else None
            )
            or "layered landscape structure"
        )
        paving_type = (
            _normalize_whitespace(
                archetype_metadata.get("generation_style_input", {}).get("styleProfile", {}).get("pavingType")
                if isinstance(archetype_metadata.get("generation_style_input"), dict)
                else None
            )
            or "high-quality public-realm paving"
        )

        render_prompt = _build_3d_from_2d_prompt(
            selected_perspective=request.selected_perspective,
            selected_lighting=request.lighting_variant,
            aesthetic_category=_normalize_whitespace(
                archetype_metadata.get("generation_style_input", {}).get("aestheticCategoryLabel")
                if isinstance(archetype_metadata.get("generation_style_input"), dict)
                else None
            )
            or "eco-urban",
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
            package_conditioning_assets["control_strength"] = max(
                float(package_conditioning_assets.get("control_strength") or 0.0), 0.84
            )

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
            "integration_status": (
                "camera_conditioned_packages_ready"
                if has_camera_conditioning
                else "conditioned_packages_ready" if conditioning_assets else "structured_packages_ready"
            ),
            "notes": (
                "3D packages preserve approved 2D footprint geometry and include camera-aware control images for the selected perspective."
                if has_camera_conditioning
                else (
                    "3D packages preserve approved 2D footprint geometry and include control-image assets for conditioned provider execution."
                    if conditioning_assets
                    else "3D packages preserve approved 2D footprint geometry and are ready for provider execution."
                )
            ),
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
            "show_surrounding_context": (
                request.show_surrounding_context if request.show_surrounding_context is not None else True
            ),
        }
        scene = _prepare_scene(
            scene_payload,
            int(request.export_width),
            toggles,
            render_mode=request.render_mode,
            map_screenshot_bounds=request.map_screenshot_bounds,
        )

        requested_style = request.style_preset or "auto"
        if requested_style == "auto":
            style_sequence = DEFAULT_STYLE_SEQUENCE
        else:
            style_sequence = [requested_style]

        reference_images = request.reference_images or request.selected_image_urls or []
        sanitized_reference_metadata = _sanitize_reference_metadata_bundle(
            [
                item.model_dump() if hasattr(item, "model_dump") else dict(item)
                for item in (request.reference_metadata or [])
            ]
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
        scene_boundary_coords = _polygon_coordinates_wgs84(_polygon_from_geometry(scene.get("boundary")))
        scene_view_extent_coords = _polygon_coordinates_wgs84(_polygon_from_geometry(scene.get("view_extent")))

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
                typology_mix=style_brief["typology_mix"],
                district_structure=style_brief["district_structure"],
                context_alignment=style_brief["context_alignment"],
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
                map_screenshot_bounds=request.map_screenshot_bounds,
                render_mode=request.render_mode,
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
                "conditioning_mode": (
                    control_map_payload.get("conditioning_mode") if isinstance(control_map_payload, dict) else None
                ),
                "control_strength": (
                    control_map_payload.get("control_strength") if isinstance(control_map_payload, dict) else None
                ),
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
                "ai_polish_applied": bool((rendered.get("ai_style_pass") or {}).get("applied")),
                "context_underlay": rendered["context_underlay"],
                "control_maps": control_map_summary,
                "reference_images": list(reference_images),
                "reference_metadata": sanitized_reference_metadata,
                "width": scene["width"],
                "height": scene["height"],
                "geometry_hash": scene["geometry_hash"],
                "scene_inputs": {
                    "site_boundary_wgs84": scene_boundary_coords,
                    "view_extent_wgs84": scene_view_extent_coords,
                    "layer_counts": {key: len(value) for key, value in scene["raw_layers"].items()},
                },
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

        await db.execute(
            update(MasterPlan2DOption).where(MasterPlan2DOption.project_id == project_id).values(is_selected=False)
        )
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
                properties = (
                    getattr(zone, "properties", None) if isinstance(getattr(zone, "properties", None), dict) else {}
                )
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
