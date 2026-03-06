"""
AI-powered site layout planner service.

Generates realistic building placements, internal roads, and green spaces
for multi-unit zones using Claude, Gemini, or an improved algorithmic fallback.
"""

import base64
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


def _ensure_image_bytes(data: bytes) -> bytes:
    """Validate and fix image data from Gemini.

    The google-genai SDK may return inline_data.data as either raw bytes
    or base64-encoded bytes depending on SDK version and transport.
    This function detects base64-encoded data and decodes it.
    """
    if not data:
        raise ValueError("Empty image data received from Gemini")

    # PNG magic bytes: \x89PNG\r\n\x1a\n
    PNG_MAGIC = b'\x89PNG\r\n\x1a\n'
    # JPEG magic bytes: \xff\xd8\xff
    JPEG_MAGIC = b'\xff\xd8\xff'

    # Already valid image bytes
    if data[:8] == PNG_MAGIC or data[:3] == JPEG_MAGIC:
        logger.info("Image data is valid raw bytes (%d bytes)", len(data))
        return data

    # Try base64 decoding — the SDK sometimes returns base64-encoded strings as bytes
    try:
        # Check if it looks like base64 (only contains valid base64 characters)
        if isinstance(data, bytes):
            text = data.decode('ascii', errors='strict')
        else:
            text = str(data)

        # Strip data URL prefix if present
        if ',' in text[:100]:
            text = text.split(',', 1)[1]

        decoded = base64.b64decode(text, validate=True)
        if decoded[:8] == PNG_MAGIC or decoded[:3] == JPEG_MAGIC:
            logger.info("Image data was base64-encoded, decoded to %d bytes", len(decoded))
            return decoded
    except Exception:
        pass

    # If we get here, data might still be a valid image in another format,
    # or it could be corrupt. Log a warning but proceed anyway.
    logger.warning(
        "Image data (%d bytes) does not have recognized magic bytes "
        "(first 16 bytes: %s). Uploading as-is.",
        len(data), data[:16].hex() if data else "empty"
    )
    return data


def _upload_image_to_storage(key: str, data: bytes, content_type: str) -> str:
    """Upload binary data to S3-compatible storage (MinIO). Returns the public URL."""
    import boto3
    from botocore.config import Config

    # Validate/fix image bytes before upload
    data = _ensure_image_bytes(data)

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
    logger.info("Uploaded image to MinIO: %s (%d bytes)", key, len(data))
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
            um = response.usage_metadata
            input_toks = (um.prompt_token_count if um else 0) or 0
            output_toks = (um.candidates_token_count if um else 0) or 0
            logger.debug("Gemini layout_preview usage_metadata: %s (input=%d, output=%d)", um, input_toks, output_toks)
            log_api_usage_sync(
                provider="gemini",
                operation="layout_preview",
                input_tokens=input_toks,
                output_tokens=output_toks,
            )
        except Exception as exc:
            logger.warning("Failed to log Gemini usage for layout_preview: %s", exc)

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
Each layout must use a DIFFERENT building arrangement strategy:
1. **Buildings Only** — buildings arranged in a clean grid or cluster pattern with NO roads and NO green_spaces. The "roads" array MUST be empty []. The "green_spaces" array MUST be empty []. This is the DEFAULT option.
2. **Loop Road** — buildings arranged along both sides of an oval/loop road with green buffers
3. **Grid / Diagonal** — buildings in a grid pattern with connecting roads

IMPORTANT: The first option (Buildings Only) must have an EMPTY roads array and an EMPTY green_spaces array. Do NOT add any roads or green spaces to it.

## Urban Planning Rules
- Side setback: minimum 1.5m between buildings
- For options WITH roads: front setback minimum 3m from road, realistic road widths (6m for local, 8m for collector), add green buffer spaces
- For the Buildings Only option: just evenly space buildings with proper setbacks, NO roads, NO green spaces
- Vary building orientations for visual interest
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

            # Strip auto-generated roads and green spaces — roads should only
            # come from user-drawn road zones, not from layout generation.
            option = SiteLayoutOption(
                option_index=idx,
                option_label=item.get("option_label", layout.layout_strategy.replace("_", " ").title()),
                buildings=layout.buildings,
                roads=[],
                green_spaces=[],
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

        # Generate buildings-only options with different orientations (no roads)
        strategies = [
            ("along_longest", "Along Longest Axis", angle_long),
            ("along_shortest", "Along Shortest Axis", angle_short),
            ("diagonal", "Diagonal", angle_diagonal),
        ]

        options: list[SiteLayoutOption] = []
        for idx, (strategy_name, label, orientation_rad) in enumerate(strategies[:count]):
            layout = self._generate_algorithmic_buildings_only(
                zone_polygon, zone_type, unit_count, properties, orientation_rad,
            )
            option = SiteLayoutOption(
                option_index=idx,
                option_label=label,
                buildings=layout.buildings,
                roads=[],
                green_spaces=[],
                layout_strategy=strategy_name,
                reasoning=layout.reasoning,
                density_achieved=layout.density_achieved,
            )
            options.append(option)

        return options

    def _generate_algorithmic_buildings_only(
        self,
        zone_polygon: Polygon,
        zone_type: str,
        unit_count: int,
        properties: dict[str, Any],
        orientation_rad: float,
    ) -> SiteLayoutResponse:
        """Generate a layout with buildings only — no internal road."""
        centroid = zone_polygon.centroid
        center_lat = centroid.y
        mlon = _meters_per_deg_lon(center_lat)
        orientation_deg = math.degrees(orientation_rad)

        setback_side_m = 1.5
        setback_front_m = 3.0

        bounds = zone_polygon.bounds
        zone_width_m = abs(bounds[2] - bounds[0]) * mlon
        zone_depth_m = abs(bounds[3] - bounds[1]) * METERS_PER_DEG_LAT

        # When only 1 unit, size the building to fill the zone (minus setbacks)
        if unit_count == 1:
            usable_w = zone_width_m - setback_side_m * 2
            usable_d = zone_depth_m - setback_front_m * 2
            building_width_m = float(properties.get("building_width") or max(5, round(usable_w, 1)))
            building_depth_m = float(properties.get("building_depth") or max(5, round(usable_d, 1)))
        else:
            building_width_m = float(properties.get("building_width", 10))
            building_depth_m = float(properties.get("building_depth", 12))

        cos_a = math.cos(orientation_rad)
        sin_a = math.sin(orientation_rad)
        perp_rad = orientation_rad + math.pi / 2

        # Grid-based placement along and across the orientation axis
        spacing_along = building_width_m + setback_side_m * 2
        spacing_across = building_depth_m + setback_side_m * 2
        half_extent = max(zone_width_m, zone_depth_m) / 2

        buildings: list[LayoutBuilding] = []
        placed = 0

        # Determine how many rows/cols we need
        max_cols = max(1, int(half_extent * 2 / spacing_along))
        max_rows = max(1, int(half_extent * 2 / spacing_across))

        for row in range(max_rows):
            if placed >= unit_count:
                break
            for col in range(max_cols):
                if placed >= unit_count:
                    break

                along_m = -half_extent * 0.8 + (col + 0.5) * spacing_along
                across_m = -half_extent * 0.8 + (row + 0.5) * spacing_across

                # Offset to center the grid
                bx_m = along_m * cos_a + across_m * math.cos(perp_rad)
                by_m = along_m * sin_a + across_m * math.sin(perp_rad)

                cx = _m_to_deg_lon(bx_m, center_lat)
                cy = _m_to_deg_lat(by_m)

                pt = Point(centroid.x + cx, centroid.y + cy)
                if not zone_polygon.contains(pt):
                    continue

                rotation_variation = ((row + col) % 3 - 1) * 3
                building_rotation = orientation_deg + rotation_variation

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

        area_ha = zone_polygon.area * mlon * METERS_PER_DEG_LAT / 10000

        return SiteLayoutResponse(
            buildings=buildings,
            roads=[],
            green_spaces=[],
            layout_strategy="buildings_only",
            reasoning=f"Buildings only (no road) — placed {len(buildings)} of {unit_count} buildings in a grid",
            density_achieved=round(len(buildings) / max(area_ha, 0.01), 1),
        )

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
            strategy_hint = "Arrange buildings in a clean cluster or grid with proper spacing. Do NOT add internal roads or green spaces unless the user description explicitly mentions them."
        elif dev_type in ("residential",) and unit_count <= 20:
            strategy_hint = "Arrange buildings in rows or a grid pattern with proper spacing. Only add roads if the user description explicitly requests them."
        elif dev_type in ("residential",):
            strategy_hint = "Arrange buildings in a grid pattern. Only add internal roads if the user description explicitly requests them."
        elif dev_type in ("commercial",):
            strategy_hint = "Place buildings around the perimeter or in a grid. Only add internal roads if the user description explicitly requests them."
        elif dev_type in ("mixed_use",):
            strategy_hint = "Arrange buildings appropriately for mixed use. Only add internal roads if the user description explicitly requests them."
        else:
            strategy_hint = "Use a layout appropriate for the development type. Only add internal roads if the user description explicitly requests them."

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
- Side setback: minimum 1.5m between buildings
- Vary building orientations for visual interest (avoid perfect grid alignment)
- All building positions must be INSIDE the zone polygon
- Position values are DEGREE OFFSETS from zone centroid ({centroid.x:.8f}, {centroid.y:.8f})
- IMPORTANT: Do NOT generate roads or green_spaces unless the user description explicitly asks for them. Return empty arrays for "roads" and "green_spaces" by default.

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
  "roads": [],
  "green_spaces": [],
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
            um = response.usage_metadata
            input_toks = (um.prompt_token_count if um else 0) or 0
            output_toks = (um.candidates_token_count if um else 0) or 0
            logger.debug("Gemini layout_generation usage_metadata: %s (input=%d, output=%d)", um, input_toks, output_toks)
            log_api_usage_sync(
                provider="gemini",
                operation="layout_generation",
                input_tokens=input_toks,
                output_tokens=output_toks,
            )
        except Exception as exc:
            logger.warning("Failed to log Gemini usage for layout_generation: %s", exc)

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

        # Strip auto-generated roads and green spaces — roads should only
        # come from user-drawn road zones, not from layout generation.
        layout.roads = []
        layout.green_spaces = []

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
        """Algorithmic layout: buildings-only grid placement (no road).

        Uses zone polygon's oriented bounding box for natural orientation,
        places buildings in a grid pattern without generating roads.
        """
        centroid = zone_polygon.centroid
        center_lat = centroid.y
        mlon = _meters_per_deg_lon(center_lat)

        # Get oriented bounding box for natural orientation
        obb = minimum_rotated_rectangle(zone_polygon)
        obb_coords = list(obb.exterior.coords)

        # Find the longest edge to determine orientation
        edges = []
        for i in range(len(obb_coords) - 1):
            dx = (obb_coords[i + 1][0] - obb_coords[i][0]) * mlon
            dy = (obb_coords[i + 1][1] - obb_coords[i][1]) * METERS_PER_DEG_LAT
            length = math.sqrt(dx * dx + dy * dy)
            edges.append((length, i))
        edges.sort(reverse=True)
        longest_idx = edges[0][1]

        p1 = obb_coords[longest_idx]
        p2 = obb_coords[longest_idx + 1]
        orientation_rad = math.atan2(
            (p2[1] - p1[1]) * METERS_PER_DEG_LAT,
            (p2[0] - p1[0]) * mlon,
        )

        return self._generate_algorithmic_buildings_only(
            zone_polygon, zone_type, unit_count, properties, orientation_rad,
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
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        try:
            from app.core.usage_logger import log_api_usage_sync
            um = response.usage_metadata
            input_toks = (um.prompt_token_count if um else 0) or 0
            output_toks = (um.candidates_token_count if um else 0) or 0
            logger.debug("Gemini layout_preview_image usage_metadata: %s (input=%d, output=%d)", um, input_toks, output_toks)
            log_api_usage_sync(
                provider="gemini",
                operation="layout_preview_image",
                input_tokens=input_toks,
                output_tokens=output_toks,
            )
        except Exception as exc:
            logger.warning("Failed to log Gemini usage for layout_preview_image: %s", exc)

        # Extract image from response
        if not response.candidates:
            raise RuntimeError("Gemini returned no candidates")
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                data = part.inline_data.data
                logger.info(
                    "Gemini layout_preview returned image: type=%s, size=%s, first_bytes=%s",
                    type(data).__name__,
                    len(data) if data else 0,
                    data[:16].hex() if isinstance(data, bytes) and data else "N/A",
                )
                return data

        # Log what we got instead of an image
        part_types = [
            f"text({len(p.text)})" if p.text else "inline_data" if p.inline_data else "other"
            for p in response.candidates[0].content.parts
        ]
        raise RuntimeError(f"Gemini did not return an image. Parts received: {part_types}")

    async def generate_site_preview_image(
        self,
        boundary_polygon: Polygon,
        zone_layouts: list[dict[str, Any]],
        non_buildable_zones: list[dict[str, Any]],
        reference_context: Optional[dict[str, Any]] = None,
        map_screenshots: Optional[dict[str, str]] = None,
        zone_meta: Optional[dict[str, dict[str, str]]] = None,
        buildable_without_layouts: Optional[list[dict[str, Any]]] = None,
    ) -> bytes:
        """Generate a photorealistic 2D aerial preview of the ENTIRE site.

        Combines all buildable zones' chosen layouts, non-buildable zones
        (roads, green spaces, water, parking), and OSM context into one
        comprehensive aerial image.
        """
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        zone_meta = zone_meta or {}

        centroid = boundary_polygon.centroid
        center_lat = centroid.y
        mlon = _meters_per_deg_lon(center_lat)

        bounds = boundary_polygon.bounds
        site_width_m = round(abs(bounds[2] - bounds[0]) * mlon, 1)
        site_depth_m = round(abs(bounds[3] - bounds[1]) * METERS_PER_DEG_LAT, 1)

        def _position_description(shape_centroid, site_centroid, site_w, site_d, mlon_val):
            """Convert a zone's position to human-readable image-relative directions."""
            dx_m = (shape_centroid.x - site_centroid.x) * mlon_val
            dy_m = (shape_centroid.y - site_centroid.y) * METERS_PER_DEG_LAT
            # Normalize to -1..+1 range within site
            nx = dx_m / (site_w / 2) if site_w else 0
            ny = dy_m / (site_d / 2) if site_d else 0
            # Vertical: top (north) / center / bottom (south)
            if ny > 0.3:
                v = "top"
            elif ny < -0.3:
                v = "bottom"
            else:
                v = "center"
            # Horizontal: left (west) / center / right (east)
            if nx > 0.3:
                h = "right"
            elif nx < -0.3:
                h = "left"
            else:
                h = "center"
            if v == "center" and h == "center":
                return "center of the site"
            elif v == "center":
                return f"{h} side of the site"
            elif h == "center":
                return f"{v} of the site"
            else:
                return f"{v}-{h} of the site"

        def _color_name(hex_color: str) -> str:
            """Convert hex color to human-readable name for Gemini."""
            color_map = {
                "#f59e0b": "amber/orange", "#9b59b6": "purple", "#e91e8a": "pink/magenta",
                "#444444": "dark gray", "#27ae60": "green", "#95a5a6": "light gray",
                "#3498db": "blue", "#d4a574": "tan/brown",
            }
            return color_map.get(hex_color.lower(), hex_color)

        # Collect reference image URLs from all zones for multi-modal input
        reference_image_urls = []

        # Describe each buildable zone and its chosen layout
        zone_descriptions = []
        for zl in zone_layouts:
            zone = zl["zone"]
            shape = zl["shape"]
            option = zl["option"]
            props = zl["properties"]
            zt = zone.zone_type
            zid = str(zone.id)
            meta = zone_meta.get(zid, {})
            zname = meta.get("name") or zone.name or zt.replace("_", " ")
            zone_color = meta.get("color", "")
            dev_type = props.get("development_type", "residential")
            aesthetic = props.get("development_aesthetic", "modern")
            facade = props.get("facade_material", "")
            roof = props.get("roof_style", "")
            ground = props.get("ground_texture", "")
            desc_text = props.get("description_text", "")
            height = props.get("height")
            floors = props.get("floors")
            balconies = props.get("balconies", False)
            unit_count = props.get("unit_count")

            # Collect reference images for this zone
            ref_imgs = props.get("reference_images") or []
            for img_url in ref_imgs:
                reference_image_urls.append({"url": img_url, "zone_name": zname})

            z_bounds = shape.bounds
            z_w = round(abs(z_bounds[2] - z_bounds[0]) * mlon, 1)
            z_d = round(abs(z_bounds[3] - z_bounds[1]) * METERS_PER_DEG_LAT, 1)

            # Position as human-readable direction
            position = _position_description(shape.centroid, centroid, site_width_m, site_depth_m, mlon)

            building_lines = []
            for b in option.buildings:
                btype = getattr(b, "building_type", dev_type)
                b_floors = b.floors or floors or props.get("floors", 2)
                b_height = b.height_m or height or (b_floors * 3.5)
                building_lines.append(
                    f"    - {btype}: {b.width_m}m x {b.depth_m}m, "
                    f"{b_floors} floors ({b_height:.0f}m tall)"
                )

            road_lines = []
            for r in option.roads:
                road_lines.append(f"    - {r.road_type} road: {r.width_m}m wide")

            green_lines = []
            for g in option.green_spaces:
                green_lines.append(f"    - {g.space_type} green space")

            style_parts = []
            if aesthetic:
                style_parts.append(f"Style: {aesthetic}")
            if facade:
                style_parts.append(f"Facade: {facade}")
            if roof:
                style_parts.append(f"Roof: {roof}")
            if ground:
                style_parts.append(f"Ground: {ground}")
            if balconies:
                style_parts.append("Has balconies")
            if height:
                style_parts.append(f"Height: {height}m")
            if floors:
                style_parts.append(f"Floors: {floors}")
            if unit_count:
                style_parts.append(f"Units: {unit_count}")
            if ref_imgs:
                style_parts.append(f"{len(ref_imgs)} reference image(s) attached")

            desc_block = ""
            if desc_text:
                desc_block = f"\n    *** USER VISION: \"{desc_text}\" ***"

            zone_block = f"""  ZONE: "{zname}" — {dev_type} zone
    Location: {position}, {z_w:.0f}m x {z_d:.0f}m
    Layout strategy: {option.layout_strategy}{desc_block}
    Appearance: {'; '.join(style_parts) if style_parts else 'default modern'}
    Buildings ({len(option.buildings)}):
{chr(10).join(building_lines) if building_lines else '      (none)'}
    Roads ({len(option.roads)}):
{chr(10).join(road_lines) if road_lines else '      (none)'}
    Green spaces ({len(option.green_spaces)}):
{chr(10).join(green_lines) if green_lines else '      (none)'}"""
            zone_descriptions.append(zone_block)

        # Include buildable zones that didn't get AI layouts (their properties/descriptions still matter)
        for bwl in (buildable_without_layouts or []):
            zone = bwl["zone"]
            shape = bwl["shape"]
            props = bwl["properties"]
            zt = zone.zone_type
            zid = str(zone.id)
            meta = zone_meta.get(zid, {})
            zname = meta.get("name") or zone.name or zt.replace("_", " ")

            dev_type = props.get("development_type", "residential" if zt == "residential" else "commercial")
            aesthetic = props.get("development_aesthetic", "modern")
            facade = props.get("facade_material", "")
            roof = props.get("roof_style", "")
            ground = props.get("ground_texture", "")
            desc_text = props.get("description_text", "")
            height = props.get("height")
            floors = props.get("floors")
            balconies = props.get("balconies", False)
            unit_count = props.get("unit_count")

            ref_imgs = props.get("reference_images") or []
            for img_url in ref_imgs:
                reference_image_urls.append({"url": img_url, "zone_name": zname})

            z_bounds = shape.bounds
            z_w = round(abs(z_bounds[2] - z_bounds[0]) * mlon, 1)
            z_d = round(abs(z_bounds[3] - z_bounds[1]) * METERS_PER_DEG_LAT, 1)
            position = _position_description(shape.centroid, centroid, site_width_m, site_depth_m, mlon)

            style_parts = []
            if aesthetic: style_parts.append(f"Style: {aesthetic}")
            if facade: style_parts.append(f"Facade: {facade}")
            if roof: style_parts.append(f"Roof: {roof}")
            if ground: style_parts.append(f"Ground: {ground}")
            if balconies: style_parts.append("Has balconies")
            if height: style_parts.append(f"Height: {height}m")
            if floors: style_parts.append(f"Floors: {floors}")
            if unit_count: style_parts.append(f"Units: {unit_count}")
            if ref_imgs: style_parts.append(f"{len(ref_imgs)} reference image(s) attached")

            desc_block = ""
            if desc_text:
                desc_block = f"\n    *** USER VISION: \"{desc_text}\" ***"

            zone_block = f"""  ZONE: "{zname}" — {dev_type} zone
    Location: {position}, {z_w:.0f}m x {z_d:.0f}m{desc_block}
    Appearance: {'; '.join(style_parts) if style_parts else 'default modern'}
    (No specific building layout generated — render buildings according to the zone properties and user vision above)"""
            zone_descriptions.append(zone_block)

        # Describe non-buildable zones (existing infrastructure within boundary)
        infra_lines = []
        for nb in non_buildable_zones:
            zt = nb["zone_type"]
            props = nb["properties"]
            zname = nb.get("name") or zt.replace("_", " ")
            shape = nb["shape"]

            position = _position_description(shape.centroid, centroid, site_width_m, site_depth_m, mlon)

            # Collect reference images for non-buildable zones too
            ref_imgs = props.get("reference_images") or []
            for img_url in ref_imgs:
                reference_image_urls.append({"url": img_url, "zone_name": zname})

            details = []
            if zt == "road":
                width = props.get("width", 10)
                surface = props.get("road_surface", "asphalt")
                lanes = props.get("lane_count", 2)
                sidewalks = props.get("sidewalks", "both")
                volume = props.get("volume", "")
                details.append(f"{width}m wide, {lanes} lanes, {surface}")
                if sidewalks and sidewalks != "none":
                    details.append(f"sidewalks: {sidewalks}")
                if volume:
                    details.append(f"{volume} traffic")
                aesthetic = props.get("road_aesthetic", "")
                if aesthetic:
                    details.append(aesthetic.replace("_", " "))
                priorities = []
                if props.get("priority_pedestrian"):
                    priorities.append(f"pedestrian={props['priority_pedestrian']}")
                if props.get("priority_cycling"):
                    priorities.append(f"cycling={props['priority_cycling']}")
                if props.get("priority_transit"):
                    priorities.append(f"transit={props['priority_transit']}")
                if props.get("priority_auto"):
                    priorities.append(f"auto={props['priority_auto']}")
                if priorities:
                    details.append(f"priorities: {', '.join(priorities)}")
            elif zt == "green_space":
                density = props.get("tree_density_level", "medium")
                tree_val = props.get("tree_density")
                details.append(f"{density} trees" + (f" ({tree_val})" if tree_val else ""))
                if props.get("has_paths"):
                    details.append("walking paths")
                if props.get("has_benches"):
                    details.append("benches")
            elif zt == "water":
                wtype = props.get("water_type", "pond")
                details.append(wtype)
            elif zt == "parking":
                layout = props.get("parking_layout", "perpendicular")
                details.append(f"{layout} layout")
                if props.get("covered"):
                    details.append("covered")

            desc_text = props.get("description_text", "")
            desc_suffix = ""
            if desc_text:
                desc_suffix = f'\n      *** USER VISION: "{desc_text}" ***'

            infra_lines.append(f"  - {zname} ({zt}) at {position}: {', '.join(details)}{desc_suffix}")

        # OSM reference context
        osm_text = ""
        if reference_context:
            osm_parts = []
            ref_roads = reference_context.get("roads", [])
            if ref_roads:
                road_types = set(r.get("road_type", "residential") for r in ref_roads)
                road_names = [r.get("name") for r in ref_roads if r.get("name")]
                osm_parts.append(f"Surrounding roads: {len(ref_roads)} ({', '.join(sorted(road_types))})")
                if road_names:
                    osm_parts.append(f"  Streets: {', '.join(road_names[:5])}")
            ref_buildings = reference_context.get("buildings", [])
            if ref_buildings:
                heights = [b.get("height_m") for b in ref_buildings if b.get("height_m")]
                avg_h = round(sum(heights) / len(heights), 1) if heights else None
                osm_parts.append(f"Surrounding buildings: {len(ref_buildings)}" + (f" (avg {avg_h}m)" if avg_h else ""))
            ref_water = reference_context.get("water", [])
            if ref_water:
                osm_parts.append(f"Nearby water: {len(ref_water)}")
            ref_parks = reference_context.get("parks", [])
            if ref_parks:
                osm_parts.append(f"Nearby parks: {len(ref_parks)}")
            if osm_parts:
                osm_text = "SURROUNDING CONTEXT (from OpenStreetMap):\n" + chr(10).join(f"  {p}" for p in osm_parts)

        # Reference images text note
        ref_img_text = ""
        if reference_image_urls:
            ref_img_text = f"REFERENCE IMAGES ({len(reference_image_urls)} attached above):\n"
            for ri in reference_image_urls:
                ref_img_text += f"  - Zone '{ri['zone_name']}': match the style/materials shown in its reference image\n"

        prompt = f"""Generate a photorealistic aerial photograph of a proposed development.

The attached image shows ONLY the development area — tightly cropped. The entire image IS your canvas. Replace what is currently there with the proposed development described below. Every pixel of your output should show the new development.

Each zone's "Location" tells you where it sits in the image (top, center, bottom, left, right). Place each zone accordingly.

SITE: {site_width_m:.0f}m wide x {site_depth_m:.0f}m deep

{chr(10).join(zone_descriptions) if zone_descriptions else '(no buildable zones)'}

{chr(10).join(infra_lines) if infra_lines else ''}

{osm_text}
{ref_img_text}

OUTPUT RULES:
- Photorealistic drone photo from directly above
- Fill the ENTIRE frame — no empty/unchanged satellite land
- Follow each zone's *** USER VISION *** text precisely
- Real materials: roof tiles, asphalt, concrete sidewalks, real grass, mature trees with shadows
- Afternoon sun, realistic building shadows
- ZERO outlines, ZERO borders, ZERO labels, ZERO annotations
"""

        logger.info("=== GEMINI SITE PREVIEW PROMPT ===")
        logger.info("Zones: %d with layouts, %d buildable without layouts, %d infrastructure, %d reference images",
                     len(zone_layouts), len(buildable_without_layouts or []), len(non_buildable_zones), len(reference_image_urls))
        logger.info("Map screenshots: %s", "yes" if map_screenshots else "no")
        logger.info("Zone meta colors: %s", {m.get("name"): m.get("color") for m in zone_meta.values()} if zone_meta else "none")
        logger.info("Prompt length: %d chars", len(prompt))
        logger.info("Full prompt:\n%s", prompt)

        from google import genai
        import httpx

        # Build multi-modal content: map screenshots + reference images + text prompt
        contents = []

        # 1. Send ONLY the tight satellite crop — no zone diagram overlay
        if map_screenshots:
            for key, label in [
                ("satellite", "This is the development area. Replace everything in this image with the proposed development."),
            ]:
                b64_str = map_screenshots.get(key, "")
                if b64_str:
                    try:
                        if "," in b64_str:
                            header, b64_data = b64_str.split(",", 1)
                            mime = header.split(":")[1].split(";")[0] if ":" in header else "image/jpeg"
                        else:
                            b64_data = b64_str
                            mime = "image/jpeg"
                        img_bytes = base64.b64decode(b64_data)
                        contents.append(
                            genai.types.Part.from_bytes(data=img_bytes, mime_type=mime)
                        )
                        contents.append(f"[{label}]")
                    except Exception as e:
                        logger.warning("Failed to decode map screenshot (%s): %s", key, e)

        # 2. Reference images from individual zones
        fetched_ref_count = 0
        for ri in reference_image_urls:
            url = ri["url"]
            # Reference image URLs stored in DB may use localhost — rewrite to minio for Docker access
            fetch_url = url.replace("http://localhost:9000", "http://minio:9000")
            logger.info("Fetching reference image for zone '%s': %s", ri["zone_name"], fetch_url)
            try:
                resp = httpx.get(fetch_url, timeout=10, follow_redirects=True)
                logger.info("Reference image response: status=%d, content-type=%s, size=%d bytes",
                            resp.status_code, resp.headers.get("content-type", "?"), len(resp.content))
                if resp.status_code == 200 and resp.headers.get("content-type", "").startswith("image"):
                    img_data = resp.content
                    mime = resp.headers.get("content-type", "image/jpeg")
                    contents.append(
                        genai.types.Part.from_bytes(data=img_data, mime_type=mime)
                    )
                    contents.append(f"[Reference image for zone: {ri['zone_name']} — match this style/aesthetic]")
                    fetched_ref_count += 1
                else:
                    logger.warning("Reference image fetch failed: status=%d, content-type=%s", resp.status_code, resp.headers.get("content-type", "?"))
            except Exception as e:
                logger.warning("Failed to fetch reference image %s: %s", fetch_url, e)

        # Count total image parts being sent
        image_parts = sum(1 for c in contents if hasattr(c, 'inline_data') or (hasattr(c, '_raw_part') and hasattr(c._raw_part, 'inline_data')))
        logger.info("Sending to Gemini: %d image parts (1 satellite + %d reference), prompt %d chars",
                     image_parts, fetched_ref_count, len(prompt))

        # 3. Text prompt (after all images)
        contents.append(prompt)

        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=contents,
            config=genai.types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        try:
            from app.core.usage_logger import log_api_usage_sync
            um = response.usage_metadata
            input_toks = (um.prompt_token_count if um else 0) or 0
            output_toks = (um.candidates_token_count if um else 0) or 0
            logger.debug("Gemini site_preview_image usage_metadata: %s (input=%d, output=%d)", um, input_toks, output_toks)
            log_api_usage_sync(
                provider="gemini",
                operation="site_preview_image",
                input_tokens=input_toks,
                output_tokens=output_toks,
            )
        except Exception as exc:
            logger.warning("Failed to log Gemini usage for site_preview_image: %s", exc)

        # Extract image from response
        if not response.candidates:
            raise RuntimeError("Gemini returned no candidates for site preview")
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                data = part.inline_data.data
                logger.info(
                    "Gemini site_preview returned image: type=%s, size=%s, first_bytes=%s",
                    type(data).__name__,
                    len(data) if data else 0,
                    data[:16].hex() if isinstance(data, bytes) and data else "N/A",
                )
                return data

        part_types = [
            f"text({len(p.text)})" if p.text else "inline_data" if p.inline_data else "other"
            for p in response.candidates[0].content.parts
        ]
        raise RuntimeError(f"Gemini did not return an image for site preview. Parts received: {part_types}")
