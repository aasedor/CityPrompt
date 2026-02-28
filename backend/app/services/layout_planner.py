"""
AI-powered site layout planner service.

Generates realistic building placements, internal roads, and green spaces
for multi-unit zones using Claude, Gemini, or an improved algorithmic fallback.
"""

import json
import logging
import math
from typing import Any, Optional

import anthropic
from shapely.geometry import Polygon, Point, LineString, MultiPoint
from shapely.affinity import rotate
from shapely import minimum_rotated_rectangle

from app.core.config import get_settings
from app.schemas.schemas import (
    LayoutBuilding,
    LayoutGreenSpace,
    LayoutRoad,
    SiteLayoutResponse,
)

logger = logging.getLogger(__name__)
settings = get_settings()

METERS_PER_DEG_LAT = 111320


def _meters_per_deg_lon(lat: float) -> float:
    return METERS_PER_DEG_LAT * abs(math.cos(math.radians(lat)))


def _m_to_deg_lon(m: float, lat: float) -> float:
    return m / _meters_per_deg_lon(lat)


def _m_to_deg_lat(m: float) -> float:
    return m / METERS_PER_DEG_LAT


class LayoutPlanner:
    """Generates realistic site layouts using AI or algorithmic fallback."""

    def __init__(self):
        self._provider: Optional[str] = None

    def _resolve_provider(self) -> str:
        """Check Redis for runtime override, then fall back to config."""
        if self._provider:
            return self._provider
        # Try Redis for runtime toggle
        try:
            import redis as redis_lib
            r = redis_lib.from_url(settings.redis_url, decode_responses=True)
            override = r.get("layout_ai_provider")
            if override:
                return override
        except Exception:
            pass
        return settings.layout_ai_provider

    async def generate_layout(
        self,
        zone_polygon: Polygon,
        zone_type: str,
        unit_count: int,
        properties: dict[str, Any],
        neighbors: Optional[list[dict[str, Any]]] = None,
    ) -> SiteLayoutResponse:
        """Main entry point: generate a site layout for a zone.

        Tries AI provider first, falls back to algorithmic layout on any failure.
        """
        provider = self._resolve_provider()
        centroid = zone_polygon.centroid
        center_lat = centroid.y

        try:
            if provider == "claude" and settings.anthropic_api_key:
                return await self._generate_with_claude(
                    zone_polygon, zone_type, unit_count, properties, neighbors
                )
            elif provider == "gemini" and settings.gemini_api_key:
                return await self._generate_with_gemini(
                    zone_polygon, zone_type, unit_count, properties, neighbors
                )
            else:
                logger.info("No AI provider configured for layout; using algorithmic fallback")
                return self._generate_algorithmic_layout(
                    zone_polygon, zone_type, unit_count, properties
                )
        except Exception as e:
            logger.warning("AI layout generation failed (%s): %s — using algorithmic fallback", provider, e)
            return self._generate_algorithmic_layout(
                zone_polygon, zone_type, unit_count, properties
            )

    # -------------------------------------------------------------------------
    # AI Prompt
    # -------------------------------------------------------------------------

    def _build_layout_prompt(
        self,
        zone_polygon: Polygon,
        zone_type: str,
        unit_count: int,
        properties: dict[str, Any],
        neighbors: Optional[list[dict[str, Any]]] = None,
    ) -> str:
        centroid = zone_polygon.centroid
        center_lat = centroid.y
        mlon = _meters_per_deg_lon(center_lat)

        bounds = zone_polygon.bounds
        width_m = abs(bounds[2] - bounds[0]) * mlon
        depth_m = abs(bounds[3] - bounds[1]) * METERS_PER_DEG_LAT
        area_m2 = zone_polygon.area * mlon * METERS_PER_DEG_LAT

        # Compute polygon coordinates in local meters for the AI
        coords_m = []
        for x, y in zone_polygon.exterior.coords:
            coords_m.append([
                round((x - centroid.x) * mlon, 1),
                round((y - centroid.y) * METERS_PER_DEG_LAT, 1),
            ])

        dev_type = properties.get("development_type", zone_type)
        aesthetic = properties.get("development_aesthetic", "")
        height = properties.get("height")
        floors = properties.get("floors")

        # Zone-type-specific strategy hints
        if dev_type in ("residential",) and unit_count <= 8:
            strategy_hint = "Use a cul-de-sac layout with buildings arranged around a turning circle."
        elif dev_type in ("residential",) and unit_count <= 20:
            strategy_hint = "Use a loop road layout with buildings along both sides."
        elif dev_type in ("residential",):
            strategy_hint = "Use a grid with a collector road connecting to local streets."
        elif dev_type in ("commercial",):
            strategy_hint = "Place buildings around the perimeter with interior parking."
        elif dev_type in ("mixed_use",):
            strategy_hint = "Place retail street-fronting along the main road, residential behind."
        else:
            strategy_hint = "Use a layout appropriate for the development type."

        neighbor_text = ""
        if neighbors:
            types = set(n.get("zone_type", "") for n in neighbors)
            if types:
                neighbor_text = f"\nSurrounding zone types: {', '.join(sorted(types))}"

        prompt = f"""You are an expert urban planner designing a realistic site layout.

## Zone Specifications
- Zone type: {dev_type}
- Aesthetic: {aesthetic or 'standard'}
- Number of units to place: {unit_count}
- Zone dimensions: {width_m:.0f}m wide x {depth_m:.0f}m deep ({area_m2:.0f} sq m)
- Zone polygon (meters from centroid): {json.dumps(coords_m)}
- Building height: {height or 'standard'}m, Floors: {floors or 'standard'}
{neighbor_text}

## Layout Strategy
{strategy_hint}

## Urban Planning Rules
- Front setback: minimum 3m from road
- Side setback: minimum 1.5m between buildings
- Buildings should face the nearest road
- Vary building orientations for visual interest (avoid perfect grid alignment)
- Include realistic road widths (6m for local, 8m for collector)
- Add green buffer spaces between road and buildings
- All building positions must be INSIDE the zone polygon
- Position values are DEGREE OFFSETS from zone centroid ({centroid.x:.8f}, {centroid.y:.8f})

## Conversion Reference
- 1 meter east/west = {_m_to_deg_lon(1, center_lat):.10f} degrees longitude
- 1 meter north/south = {_m_to_deg_lat(1):.10f} degrees latitude

## Required JSON Response
Return ONLY valid JSON matching this schema:
{{
  "buildings": [
    {{
      "center_x": <float: longitude offset from centroid in degrees>,
      "center_y": <float: latitude offset from centroid in degrees>,
      "width_m": <float: footprint width in meters>,
      "depth_m": <float: footprint depth in meters>,
      "rotation_deg": <float: rotation 0=north>,
      "building_type": "residential",
      "setback_front_m": 3.0,
      "setback_side_m": 1.5
    }}
  ],
  "roads": [
    {{
      "centerline": [[<x_offset_deg>, <y_offset_deg>], ...],
      "width_m": 6.0,
      "road_type": "local"
    }}
  ],
  "green_spaces": [
    {{
      "polygon": [[<x_offset_deg>, <y_offset_deg>], ...],
      "space_type": "buffer"
    }}
  ],
  "layout_strategy": "<strategy_name>",
  "reasoning": "<brief explanation of layout decisions>",
  "density_achieved": <float: units per hectare>
}}"""
        return prompt

    # -------------------------------------------------------------------------
    # Claude Provider
    # -------------------------------------------------------------------------

    async def _generate_with_claude(
        self,
        zone_polygon: Polygon,
        zone_type: str,
        unit_count: int,
        properties: dict[str, Any],
        neighbors: Optional[list[dict[str, Any]]] = None,
    ) -> SiteLayoutResponse:
        prompt = self._build_layout_prompt(zone_polygon, zone_type, unit_count, properties, neighbors)
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system="You are an expert urban planner. Return only valid JSON, no markdown fences or explanation outside JSON.",
            messages=[{"role": "user", "content": prompt}],
        )

        # Log usage
        try:
            from app.core.usage_logger import log_api_usage_sync
            log_api_usage_sync(
                provider="anthropic",
                operation="layout_generation",
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
            )
        except Exception:
            pass

        return self._parse_ai_response(message.content[0].text, zone_polygon)

    # -------------------------------------------------------------------------
    # Gemini Provider
    # -------------------------------------------------------------------------

    async def _generate_with_gemini(
        self,
        zone_polygon: Polygon,
        zone_type: str,
        unit_count: int,
        properties: dict[str, Any],
        neighbors: Optional[list[dict[str, Any]]] = None,
    ) -> SiteLayoutResponse:
        prompt = self._build_layout_prompt(zone_polygon, zone_type, unit_count, properties, neighbors)

        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7,
            ),
        )
        return self._parse_ai_response(response.text, zone_polygon)

    # -------------------------------------------------------------------------
    # Response Parsing
    # -------------------------------------------------------------------------

    def _parse_ai_response(self, text: str, zone_polygon: Polygon) -> SiteLayoutResponse:
        """Parse AI text response into validated SiteLayoutResponse."""
        text = text.strip()
        # Strip markdown code fences
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]

        data = json.loads(text)
        layout = SiteLayoutResponse(**data)

        # Validate buildings are inside zone polygon
        centroid = zone_polygon.centroid
        valid_buildings = []
        for b in layout.buildings:
            pt = Point(centroid.x + b.center_x, centroid.y + b.center_y)
            if zone_polygon.contains(pt) or zone_polygon.distance(pt) < 0.00001:
                valid_buildings.append(b)
            else:
                logger.warning("AI placed building outside zone polygon, skipping: (%f, %f)", b.center_x, b.center_y)
        layout.buildings = valid_buildings

        return layout

    # -------------------------------------------------------------------------
    # Algorithmic Fallback (improved over dumb grid)
    # -------------------------------------------------------------------------

    def _generate_algorithmic_layout(
        self,
        zone_polygon: Polygon,
        zone_type: str,
        unit_count: int,
        properties: dict[str, Any],
    ) -> SiteLayoutResponse:
        """Improved algorithmic layout: road-oriented placement with staggered offsets.

        Uses zone polygon's oriented bounding box for natural orientation,
        places a main road along the longest axis, positions buildings
        along both sides with realistic setbacks and varied rotations.
        """
        centroid = zone_polygon.centroid
        center_lat = centroid.y
        mlon = _meters_per_deg_lon(center_lat)

        # Get oriented bounding box for natural orientation
        obb = minimum_rotated_rectangle(zone_polygon)
        obb_coords = list(obb.exterior.coords)

        # Find the longest edge to determine road direction
        edges = []
        for i in range(len(obb_coords) - 1):
            dx = (obb_coords[i + 1][0] - obb_coords[i][0]) * mlon
            dy = (obb_coords[i + 1][1] - obb_coords[i][1]) * METERS_PER_DEG_LAT
            length = math.sqrt(dx * dx + dy * dy)
            edges.append((length, i))
        edges.sort(reverse=True)
        longest_idx = edges[0][1]

        # Road runs along the longest edge through the center
        p1 = obb_coords[longest_idx]
        p2 = obb_coords[longest_idx + 1]
        road_angle_rad = math.atan2(
            (p2[1] - p1[1]) * METERS_PER_DEG_LAT,
            (p2[0] - p1[0]) * mlon,
        )
        road_angle_deg = math.degrees(road_angle_rad)

        # Road parameters
        road_width_m = 6.0
        setback_front_m = 3.0
        setback_side_m = 1.5
        building_width_m = float(properties.get("building_width", 10))
        building_depth_m = float(properties.get("building_depth", 12))

        # Build road centerline through the zone center
        bounds = zone_polygon.bounds
        zone_width_m = abs(bounds[2] - bounds[0]) * mlon
        zone_depth_m = abs(bounds[3] - bounds[1]) * METERS_PER_DEG_LAT

        # Road centerline as offsets from centroid
        cos_a = math.cos(road_angle_rad)
        sin_a = math.sin(road_angle_rad)
        road_half_len = max(zone_width_m, zone_depth_m) / 2 * 0.85

        road_start = [
            _m_to_deg_lon(-road_half_len * cos_a, center_lat),
            _m_to_deg_lat(-road_half_len * sin_a),
        ]
        road_end = [
            _m_to_deg_lon(road_half_len * cos_a, center_lat),
            _m_to_deg_lat(road_half_len * sin_a),
        ]

        # Clip road to zone polygon
        road_line = LineString([
            (centroid.x + road_start[0], centroid.y + road_start[1]),
            (centroid.x + road_end[0], centroid.y + road_end[1]),
        ])
        clipped = road_line.intersection(zone_polygon)
        if clipped.is_empty:
            # Fallback: just use start/end
            road_centerline = [road_start, road_end]
        elif clipped.geom_type == "LineString":
            road_centerline = [
                [c[0] - centroid.x, c[1] - centroid.y]
                for c in clipped.coords
            ]
        else:
            road_centerline = [road_start, road_end]

        road = LayoutRoad(
            centerline=road_centerline,
            width_m=road_width_m,
            road_type="local" if unit_count <= 20 else "collector",
        )

        # Place buildings along both sides of road
        buildings: list[LayoutBuilding] = []
        perpendicular_rad = road_angle_rad + math.pi / 2

        # Distance from road center to building center
        offset_from_road_m = road_width_m / 2 + setback_front_m + building_depth_m / 2

        # Spacing along road
        spacing_m = building_width_m + setback_side_m * 2
        total_road_len = road_half_len * 2

        # Compute how many buildings per side
        buildings_per_side = math.ceil(unit_count / 2)
        actual_spacing = min(spacing_m, total_road_len / max(buildings_per_side, 1))

        placed = 0
        for side in [1, -1]:  # right side, then left side
            for i in range(buildings_per_side):
                if placed >= unit_count:
                    break

                # Position along road
                t = (i + 0.5) / buildings_per_side
                along_m = -road_half_len + t * total_road_len

                # Stagger offset: alternate slightly closer/farther
                stagger_m = (1.5 if i % 2 == 0 else 0) * side
                actual_offset = offset_from_road_m + stagger_m

                # Convert to degree offsets
                bx_m = along_m * cos_a + side * actual_offset * math.cos(perpendicular_rad)
                by_m = along_m * sin_a + side * actual_offset * math.sin(perpendicular_rad)

                cx = _m_to_deg_lon(bx_m, center_lat)
                cy = _m_to_deg_lat(by_m)

                # Verify inside zone
                pt = Point(centroid.x + cx, centroid.y + cy)
                if not zone_polygon.contains(pt):
                    # Try without stagger
                    actual_offset = offset_from_road_m
                    bx_m = along_m * cos_a + side * actual_offset * math.cos(perpendicular_rad)
                    by_m = along_m * sin_a + side * actual_offset * math.sin(perpendicular_rad)
                    cx = _m_to_deg_lon(bx_m, center_lat)
                    cy = _m_to_deg_lat(by_m)
                    pt = Point(centroid.x + cx, centroid.y + cy)
                    if not zone_polygon.contains(pt):
                        continue

                # Building faces the road (perpendicular rotation + small variation)
                face_angle = road_angle_deg + 90 * side
                rotation_variation = (i % 3 - 1) * 3  # -3, 0, or +3 degrees
                building_rotation = face_angle + rotation_variation

                buildings.append(LayoutBuilding(
                    center_x=cx,
                    center_y=cy,
                    width_m=building_width_m,
                    depth_m=building_depth_m,
                    rotation_deg=building_rotation % 360,
                    height_m=properties.get("height"),
                    floors=properties.get("floors"),
                    building_type=properties.get("development_type", "residential"),
                    setback_front_m=setback_front_m,
                    setback_side_m=setback_side_m,
                ))
                placed += 1

        # Green buffer strips along road
        green_spaces: list[LayoutGreenSpace] = []
        buffer_width_m = setback_front_m * 0.6
        for side in [1, -1]:
            buffer_offset = road_width_m / 2 + buffer_width_m / 2
            pts = []
            for endpoint in [road_start, road_end]:
                ex_m = endpoint[0] * mlon
                ey_m = endpoint[1] * METERS_PER_DEG_LAT
                # Doesn't need to be exact — just approximate rectangle
                pass

            # Simple rectangular buffer
            buf_start_x = road_start[0] + _m_to_deg_lon(side * buffer_offset * math.cos(perpendicular_rad), center_lat)
            buf_start_y = road_start[1] + _m_to_deg_lat(side * buffer_offset * math.sin(perpendicular_rad))
            buf_end_x = road_end[0] + _m_to_deg_lon(side * buffer_offset * math.cos(perpendicular_rad), center_lat)
            buf_end_y = road_end[1] + _m_to_deg_lat(side * buffer_offset * math.sin(perpendicular_rad))

            hw = _m_to_deg_lon(buffer_width_m / 2 * abs(math.cos(perpendicular_rad)), center_lat)
            hh = _m_to_deg_lat(buffer_width_m / 2 * abs(math.sin(perpendicular_rad)))

            green_spaces.append(LayoutGreenSpace(
                polygon=[
                    [buf_start_x - hw, buf_start_y - hh],
                    [buf_end_x - hw, buf_end_y - hh],
                    [buf_end_x + hw, buf_end_y + hh],
                    [buf_start_x + hw, buf_start_y + hh],
                ],
                space_type="buffer",
            ))

        strategy = "road_oriented"
        if unit_count <= 8:
            strategy = "cul_de_sac_algorithmic"
        elif unit_count <= 20:
            strategy = "loop_road_algorithmic"
        else:
            strategy = "grid_collector_algorithmic"

        area_ha = zone_polygon.area * mlon * METERS_PER_DEG_LAT / 10000

        return SiteLayoutResponse(
            buildings=buildings,
            roads=[road],
            green_spaces=green_spaces,
            layout_strategy=strategy,
            reasoning=f"Algorithmic fallback: placed {len(buildings)} of {unit_count} buildings along a main road oriented to zone geometry",
            density_achieved=round(len(buildings) / max(area_ha, 0.01), 1),
        )
