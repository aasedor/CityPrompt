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
    SiteLayoutOption,
)

logger = logging.getLogger(__name__)
settings = get_settings()

METERS_PER_DEG_LAT = 111320


def _upload_image_to_storage(key: str, data: bytes, content_type: str) -> str:
    """Upload binary data to S3-compatible storage (MinIO). Returns the public URL."""
    import boto3
    from botocore.config import Config

    s3 = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
        config=Config(signature_version="s3v4"),
    )
    try:
        s3.head_bucket(Bucket=settings.s3_bucket_name)
    except Exception:
        try:
            s3.create_bucket(Bucket=settings.s3_bucket_name)
        except Exception:
            pass
    s3.put_object(
        Bucket=settings.s3_bucket_name,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return f"{settings.s3_endpoint_url}/{settings.s3_bucket_name}/{key}"


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
    # Multi-option Preview
    # -------------------------------------------------------------------------

    async def generate_layout_options(
        self,
        zone_polygon: Polygon,
        zone_type: str,
        unit_count: int,
        properties: dict[str, Any],
        neighbors: Optional[list[dict[str, Any]]] = None,
        count: int = 3,
        reference_context: Optional[dict[str, Any]] = None,
        locked_layers: Optional[dict[str, Any]] = None,
    ) -> list[SiteLayoutOption]:
        """Generate multiple layout options for preview.

        Tries AI provider first (single API call for all options),
        falls back to algorithmic variations.
        """
        provider = self._resolve_provider()

        try:
            if provider == "claude" and settings.anthropic_api_key:
                return await self._generate_options_with_claude(
                    zone_polygon, zone_type, unit_count, properties, neighbors, count,
                    reference_context, locked_layers,
                )
            elif provider == "gemini" and settings.gemini_api_key:
                return await self._generate_options_with_gemini(
                    zone_polygon, zone_type, unit_count, properties, neighbors, count,
                    reference_context, locked_layers,
                )
        except Exception as e:
            logger.warning("AI layout options failed (%s): %s — using algorithmic variations", provider, e)

        return self._generate_algorithmic_variations(
            zone_polygon, zone_type, unit_count, properties, count
        )

    async def _generate_options_with_claude(
        self,
        zone_polygon: Polygon,
        zone_type: str,
        unit_count: int,
        properties: dict[str, Any],
        neighbors: Optional[list[dict[str, Any]]],
        count: int,
        reference_context: Optional[dict[str, Any]] = None,
        locked_layers: Optional[dict[str, Any]] = None,
    ) -> list[SiteLayoutOption]:
        prompt = self._build_multi_layout_prompt(zone_polygon, zone_type, unit_count, properties, neighbors, count, reference_context, locked_layers)
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            system="You are an expert urban planner. Return only valid JSON, no markdown fences or explanation outside JSON.",
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            from app.core.usage_logger import log_api_usage_sync
            log_api_usage_sync(
                provider="anthropic",
                operation="layout_preview",
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
            )
        except Exception:
            pass

        return self._parse_multi_ai_response(message.content[0].text, zone_polygon, count)

    async def _generate_options_with_gemini(
        self,
        zone_polygon: Polygon,
        zone_type: str,
        unit_count: int,
        properties: dict[str, Any],
        neighbors: Optional[list[dict[str, Any]]],
        count: int,
        reference_context: Optional[dict[str, Any]] = None,
        locked_layers: Optional[dict[str, Any]] = None,
    ) -> list[SiteLayoutOption]:
        prompt = self._build_multi_layout_prompt(zone_polygon, zone_type, unit_count, properties, neighbors, count, reference_context, locked_layers)

        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.8,
            ),
        )

        try:
            from app.core.usage_logger import log_api_usage_sync
            log_api_usage_sync(
                provider="gemini",
                operation="layout_preview",
                input_tokens=getattr(response.usage_metadata, 'prompt_token_count', 0) or 0,
                output_tokens=getattr(response.usage_metadata, 'candidates_token_count', 0) or 0,
            )
        except Exception:
            pass

        return self._parse_multi_ai_response(response.text, zone_polygon, count)

    def _build_multi_layout_prompt(
        self,
        zone_polygon: Polygon,
        zone_type: str,
        unit_count: int,
        properties: dict[str, Any],
        neighbors: Optional[list[dict[str, Any]]] = None,
        count: int = 3,
        reference_context: Optional[dict[str, Any]] = None,
        locked_layers: Optional[dict[str, Any]] = None,
    ) -> str:
        """Build a prompt requesting multiple layout strategies in one response."""
        centroid = zone_polygon.centroid
        center_lat = centroid.y
        mlon = _meters_per_deg_lon(center_lat)

        bounds = zone_polygon.bounds
        width_m = abs(bounds[2] - bounds[0]) * mlon
        depth_m = abs(bounds[3] - bounds[1]) * METERS_PER_DEG_LAT
        area_m2 = zone_polygon.area * mlon * METERS_PER_DEG_LAT

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
        facade_material = properties.get("facade_material", "")
        roof_type = properties.get("roof_type", "")
        ground_texture = properties.get("ground_texture", "")
        description_text = properties.get("description_text", "")
        tree_density = properties.get("tree_density")
        unit_count_prop = properties.get("unit_count")

        # Build extra zone detail lines
        zone_extras = []
        if facade_material:
            zone_extras.append(f"- Facade material: {facade_material}")
        if roof_type:
            zone_extras.append(f"- Roof type: {roof_type}")
        if ground_texture:
            zone_extras.append(f"- Ground texture: {ground_texture}")
        if tree_density:
            zone_extras.append(f"- Tree density: {tree_density}")
        if unit_count_prop:
            zone_extras.append(f"- Target unit count: {unit_count_prop}")
        if description_text:
            zone_extras.append(f'- User description: "{description_text}"')
        zone_extras_text = chr(10).join(zone_extras) if zone_extras else ""

        # Build user-drawn sibling zones section (spatial context)
        sibling_section = ""
        if neighbors:
            sibling_parts = []
            zone_type_labels = {
                "road": "Road", "building": "Building", "residential": "Residential",
                "green_space": "Green Space", "parking": "Parking/Plaza",
                "water": "Water", "site_boundary": "Site Boundary",
                "development_area": "Development Area",
            }
            for n in neighbors:
                zt = n.get("zone_type", "")
                if zt == "site_boundary":
                    continue
                center = n.get("center")
                if not center:
                    continue
                dx = round((center[0] - centroid.x) * mlon, 1)
                dy = round((center[1] - centroid.y) * METERS_PER_DEG_LAT, 1)
                w = n.get("width_m", 0)
                d = n.get("depth_m", 0)
                name = n.get("name") or zone_type_labels.get(zt, zt)
                zp = n.get("properties") or {}

                # Build a rich description from ALL properties
                attrs = []
                if zp.get("development_type"):
                    attrs.append(f"type: {zp['development_type']}")
                if zp.get("development_aesthetic"):
                    attrs.append(f"aesthetic: {zp['development_aesthetic'].replace('_', ' ')}")
                if zp.get("unit_count"):
                    attrs.append(f"{zp['unit_count']} units")
                if zp.get("height"):
                    attrs.append(f"{zp['height']}m tall")
                if zp.get("floors"):
                    attrs.append(f"{zp['floors']} floors")
                if zp.get("floor_height"):
                    attrs.append(f"{zp['floor_height']}m/floor")
                if zp.get("facade_material"):
                    attrs.append(f"facade: {zp['facade_material']}")
                if zp.get("roof_type"):
                    attrs.append(f"roof: {zp['roof_type']}")
                # Road properties
                if zp.get("width"):
                    attrs.append(f"{zp['width']}m wide")
                if zp.get("lane_count"):
                    attrs.append(f"{zp['lane_count']} lanes")
                if zp.get("road_aesthetic"):
                    attrs.append(f"style: {zp['road_aesthetic'].replace('_', ' ')}")
                if zp.get("road_surface"):
                    attrs.append(f"surface: {zp['road_surface']}")
                if zp.get("volume"):
                    attrs.append(f"traffic: {zp['volume']}")
                if zp.get("has_sidewalks"):
                    attrs.append("sidewalks")
                # Green/landscape
                if zp.get("tree_density"):
                    attrs.append(f"tree density: {zp['tree_density']}")
                if zp.get("ground_texture"):
                    attrs.append(f"ground: {zp['ground_texture']}")
                # Description text — user-written, most important context
                if zp.get("description_text"):
                    attrs.append(f'description: "{zp["description_text"]}"')

                label = zone_type_labels.get(zt, zt)
                attr_str = f" ({', '.join(attrs)})" if attrs else ""
                line = f"  - {name} [{label}]{attr_str} — center at ({dx},{dy})m, {w:.0f}m x {d:.0f}m"
                sibling_parts.append(line)

            if sibling_parts:
                sibling_section = f"""
## User-Drawn Zones (already placed on site)
{chr(10).join(sibling_parts)}

**Coordination rules:**
- Do NOT place buildings or roads overlapping these existing zones
- Connect new roads to existing road zones where they touch the boundary
- Match aesthetics, materials, and setbacks of adjacent building zones
- Preserve green spaces and water features already placed
- Respect the described character and unit counts of each zone
"""

        # Build reference context section
        reference_section = ""
        if reference_context:
            ref_parts = []
            ref_roads = reference_context.get("roads", [])[:15]
            if ref_roads:
                road_lines = []
                for r in ref_roads:
                    name = r.get("name") or "unnamed"
                    rtype = r.get("road_type", "residential")
                    width = r.get("width_m", 6)
                    coords = r.get("coordinates", [])
                    # Convert to offsets from centroid
                    coord_offsets = []
                    for lon, lat in coords[:4]:
                        dx = round((lon - centroid.x) * mlon, 1)
                        dy = round((lat - centroid.y) * METERS_PER_DEG_LAT, 1)
                        coord_offsets.append(f"({dx},{dy})")
                    road_lines.append(f"  - {name} ({rtype}, {width}m wide): {' -> '.join(coord_offsets)}")
                ref_parts.append("Nearby roads:\n" + "\n".join(road_lines))

            ref_buildings = reference_context.get("buildings", [])[:10]
            if ref_buildings:
                bldg_lines = []
                for b in ref_buildings:
                    btype = b.get("building_type", "yes")
                    h = b.get("height_m")
                    h_str = f", {h}m tall" if h else ""
                    coords = b.get("coordinates", [])
                    if coords:
                        cx = sum(c[0] for c in coords) / len(coords)
                        cy = sum(c[1] for c in coords) / len(coords)
                        dx = round((cx - centroid.x) * mlon, 1)
                        dy = round((cy - centroid.y) * METERS_PER_DEG_LAT, 1)
                        bldg_lines.append(f"  - {btype}{h_str} at ({dx},{dy})m")
                ref_parts.append("Existing buildings:\n" + "\n".join(bldg_lines))

            ref_water = reference_context.get("water", [])
            if ref_water:
                ref_parts.append(f"Water features: {len(ref_water)} nearby")

            ref_parks = reference_context.get("parks", [])
            if ref_parks:
                ref_parts.append(f"Parks/green areas: {len(ref_parks)} nearby")

            if ref_parts:
                reference_section = f"""
## Surrounding Reference Context
{chr(10).join(ref_parts)}

**Integration rules:**
- Connect new internal roads to existing roads at boundary edges where possible
- Match building setbacks to surrounding context
- Respect water features and parks — do not place buildings over them
- Orient buildings to face existing roads when near the boundary
"""

        # Build locked layers section
        locked_section = ""
        if locked_layers:
            lock_parts = []
            if locked_layers.get("roads"):
                lock_parts.append(f"Locked roads ({len(locked_layers['roads'])} elements) — keep these road positions exactly as specified:")
                for i, r in enumerate(locked_layers["roads"]):
                    lock_parts.append(f"  Road {i}: centerline={json.dumps(r.get('centerline', []))}, width={r.get('width_m', 6)}m")
            if locked_layers.get("buildings"):
                lock_parts.append(f"Locked buildings ({len(locked_layers['buildings'])} elements) — keep these building positions exactly")
            if locked_layers.get("green_spaces"):
                lock_parts.append(f"Locked green spaces ({len(locked_layers['green_spaces'])} elements) — keep these green space positions exactly")

            if lock_parts:
                locked_section = f"""
## Locked Elements (DO NOT MODIFY)
{chr(10).join(lock_parts)}

**Locked layer rules:**
- Include all locked elements in your output UNCHANGED
- Generate new unlocked elements that work around the locked ones
- Ensure new buildings don't overlap with locked roads or green spaces
"""

        prompt = f"""You are an expert urban planner. Generate {count} DIFFERENT layout strategies for the same zone.

## Zone Specifications
- Zone type: {dev_type}
- Aesthetic: {aesthetic or 'standard'}
- Number of units to place: {unit_count}
- Zone dimensions: {width_m:.0f}m wide x {depth_m:.0f}m deep ({area_m2:.0f} sq m)
- Zone polygon (meters from centroid): {json.dumps(coords_m)}
- Building height: {height or 'standard'}m, Floors: {floors or 'standard'}
{zone_extras_text}
{sibling_section}
{reference_section}
{locked_section}

## Layout Strategies to Generate
Each layout must use a DIFFERENT road/building arrangement strategy:
1. **Cul-de-sac** — buildings arranged around a turning circle at the end of a dead-end road
2. **Loop Road** — buildings arranged along both sides of an oval/loop road
3. **Grid / Diagonal** — buildings in a grid pattern with connecting roads

## Urban Planning Rules
- Front setback: minimum 3m from road
- Side setback: minimum 1.5m between buildings
- Buildings should face the nearest road
- Vary building orientations for visual interest
- Include realistic road widths (6m for local, 8m for collector)
- Add green buffer spaces between road and buildings
- All building positions must be INSIDE the zone polygon
- Position values are DEGREE OFFSETS from zone centroid ({centroid.x:.8f}, {centroid.y:.8f})

## Conversion Reference
- 1 meter east/west = {_m_to_deg_lon(1, center_lat):.10f} degrees longitude
- 1 meter north/south = {_m_to_deg_lat(1):.10f} degrees latitude

## Required JSON Response
Return ONLY a JSON array of {count} layout objects. Each object has this schema:
[
  {{
    "layout_strategy": "<strategy_name>",
    "option_label": "<human readable label, e.g. Cul-de-sac>",
    "reasoning": "<brief explanation>",
    "density_achieved": <float>,
    "buildings": [
      {{
        "center_x": <float: longitude offset from centroid>,
        "center_y": <float: latitude offset from centroid>,
        "width_m": <float>, "depth_m": <float>,
        "rotation_deg": <float>,
        "building_type": "residential",
        "setback_front_m": 3.0, "setback_side_m": 1.5
      }}
    ],
    "roads": [
      {{ "centerline": [[<x_deg>, <y_deg>], ...], "width_m": 6.0, "road_type": "local" }}
    ],
    "green_spaces": [
      {{ "polygon": [[<x_deg>, <y_deg>], ...], "space_type": "buffer" }}
    ]
  }}
]"""
        return prompt

    def _parse_multi_ai_response(
        self, text: str, zone_polygon: Polygon, count: int
    ) -> list[SiteLayoutOption]:
        """Parse AI response containing a JSON array of layout options."""
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            text = text.rsplit("```", 1)[0]

        data = json.loads(text)
        logger.info("AI response parsed: type=%s, len=%s", type(data).__name__, len(data) if isinstance(data, list) else 1)

        # Handle both array and single-object responses
        if isinstance(data, dict):
            data = [data]

        centroid = zone_polygon.centroid
        logger.info("Zone centroid: (%f, %f), bounds: %s", centroid.x, centroid.y, zone_polygon.bounds)
        options: list[SiteLayoutOption] = []

        for idx, item in enumerate(data[:count]):
            layout = SiteLayoutResponse(**item)
            logger.info("Option %d: %d buildings, %d roads, strategy=%s",
                        idx, len(layout.buildings), len(layout.roads), layout.layout_strategy)

            # Validate buildings are inside zone
            valid_buildings = []
            for b in layout.buildings:
                pt = Point(centroid.x + b.center_x, centroid.y + b.center_y)
                inside = zone_polygon.contains(pt)
                dist = zone_polygon.distance(pt)
                if inside or dist < 0.00001:
                    valid_buildings.append(b)
                else:
                    logger.warning("Preview option %d: building at center_x=%f, center_y=%f -> point(%f,%f) outside zone (dist=%f)",
                                   idx, b.center_x, b.center_y, pt.x, pt.y, dist)
            logger.info("Option %d: %d/%d buildings passed validation", idx, len(valid_buildings), len(layout.buildings))
            layout.buildings = valid_buildings

            option = SiteLayoutOption(
                option_index=idx,
                option_label=item.get("option_label", layout.layout_strategy.replace("_", " ").title()),
                buildings=layout.buildings,
                roads=layout.roads,
                green_spaces=layout.green_spaces,
                layout_strategy=layout.layout_strategy,
                reasoning=layout.reasoning,
                density_achieved=layout.density_achieved,
            )
            options.append(option)

        return options

    def _generate_algorithmic_variations(
        self,
        zone_polygon: Polygon,
        zone_type: str,
        unit_count: int,
        properties: dict[str, Any],
        count: int = 3,
    ) -> list[SiteLayoutOption]:
        """Generate free algorithmic layout variations by rotating road orientation."""
        centroid = zone_polygon.centroid
        center_lat = centroid.y
        mlon = _meters_per_deg_lon(center_lat)

        obb = minimum_rotated_rectangle(zone_polygon)
        obb_coords = list(obb.exterior.coords)

        # Find longest and shortest edges
        edges = []
        for i in range(len(obb_coords) - 1):
            dx = (obb_coords[i + 1][0] - obb_coords[i][0]) * mlon
            dy = (obb_coords[i + 1][1] - obb_coords[i][1]) * METERS_PER_DEG_LAT
            length = math.sqrt(dx * dx + dy * dy)
            edges.append((length, i))
        edges.sort(reverse=True)

        longest_idx = edges[0][1]
        shortest_idx = edges[1][1] if len(edges) > 1 else longest_idx

        p1_long = obb_coords[longest_idx]
        p2_long = obb_coords[longest_idx + 1]
        angle_long = math.atan2(
            (p2_long[1] - p1_long[1]) * METERS_PER_DEG_LAT,
            (p2_long[0] - p1_long[0]) * mlon,
        )

        p1_short = obb_coords[shortest_idx]
        p2_short = obb_coords[shortest_idx + 1]
        angle_short = math.atan2(
            (p2_short[1] - p1_short[1]) * METERS_PER_DEG_LAT,
            (p2_short[0] - p1_short[0]) * mlon,
        )

        angle_diagonal = angle_long + math.pi / 4

        strategies = [
            ("longest_axis", "Road Along Longest Axis", angle_long),
            ("shortest_axis", "Road Along Shortest Axis", angle_short),
            ("diagonal", "Diagonal Road", angle_diagonal),
        ]

        options: list[SiteLayoutOption] = []
        for idx, (strategy_name, label, road_angle_rad) in enumerate(strategies[:count]):
            layout = self._generate_algorithmic_with_angle(
                zone_polygon, zone_type, unit_count, properties, road_angle_rad, strategy_name
            )
            option = SiteLayoutOption(
                option_index=idx,
                option_label=label,
                buildings=layout.buildings,
                roads=layout.roads,
                green_spaces=layout.green_spaces,
                layout_strategy=layout.layout_strategy,
                reasoning=layout.reasoning,
                density_achieved=layout.density_achieved,
            )
            options.append(option)

        return options

    def _generate_algorithmic_with_angle(
        self,
        zone_polygon: Polygon,
        zone_type: str,
        unit_count: int,
        properties: dict[str, Any],
        road_angle_rad: float,
        strategy_name: str,
    ) -> SiteLayoutResponse:
        """Generate an algorithmic layout with a specific road angle."""
        centroid = zone_polygon.centroid
        center_lat = centroid.y
        mlon = _meters_per_deg_lon(center_lat)
        road_angle_deg = math.degrees(road_angle_rad)

        road_width_m = 6.0
        setback_front_m = 3.0
        setback_side_m = 1.5
        building_width_m = float(properties.get("building_width", 10))
        building_depth_m = float(properties.get("building_depth", 12))

        bounds = zone_polygon.bounds
        zone_width_m = abs(bounds[2] - bounds[0]) * mlon
        zone_depth_m = abs(bounds[3] - bounds[1]) * METERS_PER_DEG_LAT

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

        # Clip road to zone
        road_line = LineString([
            (centroid.x + road_start[0], centroid.y + road_start[1]),
            (centroid.x + road_end[0], centroid.y + road_end[1]),
        ])
        clipped = road_line.intersection(zone_polygon)
        if clipped.is_empty or clipped.geom_type != "LineString":
            road_centerline = [road_start, road_end]
        else:
            road_centerline = [
                [c[0] - centroid.x, c[1] - centroid.y]
                for c in clipped.coords
            ]

        road = LayoutRoad(
            centerline=road_centerline,
            width_m=road_width_m,
            road_type="local" if unit_count <= 20 else "collector",
        )

        # Place buildings along both sides
        buildings: list[LayoutBuilding] = []
        perpendicular_rad = road_angle_rad + math.pi / 2
        offset_from_road_m = road_width_m / 2 + setback_front_m + building_depth_m / 2
        spacing_m = building_width_m + setback_side_m * 2
        total_road_len = road_half_len * 2
        buildings_per_side = math.ceil(unit_count / 2)
        actual_spacing = min(spacing_m, total_road_len / max(buildings_per_side, 1))

        placed = 0
        for side in [1, -1]:
            for i in range(buildings_per_side):
                if placed >= unit_count:
                    break
                t = (i + 0.5) / buildings_per_side
                along_m = -road_half_len + t * total_road_len
                stagger_m = (1.5 if i % 2 == 0 else 0) * side
                actual_offset = offset_from_road_m + stagger_m
                bx_m = along_m * cos_a + side * actual_offset * math.cos(perpendicular_rad)
                by_m = along_m * sin_a + side * actual_offset * math.sin(perpendicular_rad)
                cx = _m_to_deg_lon(bx_m, center_lat)
                cy = _m_to_deg_lat(by_m)

                pt = Point(centroid.x + cx, centroid.y + cy)
                if not zone_polygon.contains(pt):
                    actual_offset = offset_from_road_m
                    bx_m = along_m * cos_a + side * actual_offset * math.cos(perpendicular_rad)
                    by_m = along_m * sin_a + side * actual_offset * math.sin(perpendicular_rad)
                    cx = _m_to_deg_lon(bx_m, center_lat)
                    cy = _m_to_deg_lat(by_m)
                    pt = Point(centroid.x + cx, centroid.y + cy)
                    if not zone_polygon.contains(pt):
                        continue

                face_angle = road_angle_deg + 90 * side
                rotation_variation = (i % 3 - 1) * 3
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

        # Green buffer strips
        green_spaces: list[LayoutGreenSpace] = []
        buffer_width_m = setback_front_m * 0.6
        for side in [1, -1]:
            buffer_offset = road_width_m / 2 + buffer_width_m / 2
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

        area_ha = zone_polygon.area * mlon * METERS_PER_DEG_LAT / 10000

        return SiteLayoutResponse(
            buildings=buildings,
            roads=[road],
            green_spaces=green_spaces,
            layout_strategy=strategy_name,
            reasoning=f"Algorithmic: {strategy_name.replace('_', ' ')} — placed {len(buildings)} of {unit_count} buildings",
            density_achieved=round(len(buildings) / max(area_ha, 0.01), 1),
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

        try:
            from app.core.usage_logger import log_api_usage_sync
            log_api_usage_sync(
                provider="gemini",
                operation="layout_generation",
                input_tokens=getattr(response.usage_metadata, 'prompt_token_count', 0) or 0,
                output_tokens=getattr(response.usage_metadata, 'candidates_token_count', 0) or 0,
            )
        except Exception:
            pass

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

        # Handle array response (take first element)
        if isinstance(data, list):
            data = data[0]

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

    # -------------------------------------------------------------------------
    # 2D Image Preview (Gemini)
    # -------------------------------------------------------------------------

    async def generate_layout_preview_image(
        self,
        zone_polygon: Polygon,
        option: SiteLayoutOption,
        properties: dict[str, Any],
        neighbors: Optional[list[dict[str, Any]]] = None,
        reference_context: Optional[dict[str, Any]] = None,
    ) -> bytes:
        """Generate a photorealistic 2D aerial preview image using Gemini.

        Includes full site context (sibling zones, OSM features) for realism.
        Returns PNG bytes of the rendered image.
        """
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        centroid = zone_polygon.centroid
        center_lat = centroid.y
        mlon = _meters_per_deg_lon(center_lat)

        bounds = zone_polygon.bounds
        width_m = round(abs(bounds[2] - bounds[0]) * mlon, 1)
        depth_m = round(abs(bounds[3] - bounds[1]) * METERS_PER_DEG_LAT, 1)

        # Build descriptive prompt from layout data
        building_desc = []
        for b in option.buildings:
            btype = getattr(b, "building_type", "residential")
            building_desc.append(
                f"- {btype} building: {b.width_m}m x {b.depth_m}m, "
                f"{b.floors or properties.get('floors', 2)} floors"
            )

        road_desc = []
        for r in option.roads:
            road_desc.append(f"- {r.road_type} road: {r.width_m}m wide")

        green_desc = []
        for g in option.green_spaces:
            green_desc.append(f"- {g.space_type} green space")

        dev_type = properties.get("development_type", "residential")
        aesthetic = properties.get("development_aesthetic", "modern suburban")
        facade = properties.get("facade_material", "")
        roof = properties.get("roof_type", "")
        ground = properties.get("ground_texture", "")
        description = properties.get("description_text", "")

        # Zone material details
        material_details = []
        if facade:
            material_details.append(f"Building facades: {facade}")
        if roof:
            material_details.append(f"Roof style: {roof}")
        if ground:
            material_details.append(f"Ground/landscape: {ground}")
        if description:
            material_details.append(f"Character: {description}")
        material_text = chr(10).join(f"- {m}" for m in material_details) if material_details else ""

        # Sibling zones context for realism
        sibling_text = ""
        if neighbors:
            sibling_lines = []
            for n in neighbors:
                zt = n.get("zone_type", "")
                if zt == "site_boundary":
                    continue
                zp = n.get("properties") or {}
                name = n.get("name") or zt.replace("_", " ")
                parts = [name]
                if zp.get("development_aesthetic"):
                    parts.append(zp["development_aesthetic"].replace("_", " "))
                if zp.get("facade_material"):
                    parts.append(f"{zp['facade_material']} facade")
                if zp.get("height"):
                    parts.append(f"{zp['height']}m tall")
                if zp.get("width"):
                    parts.append(f"{zp['width']}m wide")
                if zp.get("description_text"):
                    parts.append(f'"{zp["description_text"]}"')
                sibling_lines.append(f"- {', '.join(parts)}")
            if sibling_lines:
                sibling_text = f"\nSurrounding zones on the site:\n{chr(10).join(sibling_lines)}"

        # OSM reference context
        osm_text = ""
        if reference_context:
            osm_parts = []
            ref_roads = reference_context.get("roads", [])
            if ref_roads:
                road_types = set(r.get("road_type", "residential") for r in ref_roads)
                road_names = [r.get("name") for r in ref_roads if r.get("name")]
                osm_parts.append(f"Existing roads nearby: {len(ref_roads)} ({', '.join(sorted(road_types))})")
                if road_names:
                    osm_parts.append(f"  Named streets: {', '.join(road_names[:5])}")
            ref_buildings = reference_context.get("buildings", [])
            if ref_buildings:
                heights = [b.get("height_m") for b in ref_buildings if b.get("height_m")]
                avg_h = round(sum(heights) / len(heights), 1) if heights else None
                osm_parts.append(f"Existing buildings nearby: {len(ref_buildings)}" + (f" (avg {avg_h}m)" if avg_h else ""))
            ref_water = reference_context.get("water", [])
            if ref_water:
                osm_parts.append(f"Water features: {len(ref_water)} nearby")
            ref_parks = reference_context.get("parks", [])
            if ref_parks:
                osm_parts.append(f"Parks/green areas: {len(ref_parks)} nearby")
            if osm_parts:
                osm_text = f"\nReal-world surroundings (OpenStreetMap):\n" + chr(10).join(f"- {p}" for p in osm_parts)

        prompt = f"""Generate a photorealistic top-down aerial view (bird's eye / drone photo) of a proposed {dev_type} development.

Site: {width_m:.0f}m wide x {depth_m:.0f}m deep
Layout: {option.layout_strategy}
Aesthetic: {aesthetic or 'modern suburban'}

Proposed buildings ({len(building_desc)}):
{chr(10).join(building_desc) if building_desc else 'None'}

Internal roads ({len(road_desc)}):
{chr(10).join(road_desc) if road_desc else 'None'}

Green spaces ({len(green_desc)}):
{chr(10).join(green_desc) if green_desc else 'None'}

{material_text}
{sibling_text}
{osm_text}

Requirements:
- Top-down aerial perspective, looking straight down like a high-altitude drone photo
- Photorealistic rendering — this must look like a real drone photograph, not a diagram or illustration
- Real materials: visible roof tiles/materials, asphalt roads with lane markings, concrete sidewalks, real grass textures, mature trees with shadows
- Realistic shadows cast by buildings based on afternoon sun
- Driveways connecting each building to the road network
- Landscaping: trees, shrubs, hedges around properties; lawn areas with visible grass texture
- Road details: curbs, sidewalks, crosswalks at intersections, road surface texture
- Surrounding context should be visible at the edges (neighboring roads, buildings, vegetation)
- Professional architectural visualization quality — indistinguishable from a real aerial photograph
- No labels, no annotations, no text overlays, no colored zones — pure photorealistic image
"""

        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",  # alternatives: gemini-2.5-flash-image, imagen-4.0-generate-001
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        # Extract image from response
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                return part.inline_data.data

        raise RuntimeError("Gemini did not return an image")
