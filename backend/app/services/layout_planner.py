"""
AI-powered site layout planner service.

Generates realistic building placements, internal roads, and green spaces
for multi-unit zones using Claude, Gemini, or an improved algorithmic fallback.
"""

import base64
import json
import logging
import math
import re
from io import BytesIO
from typing import Any, Optional

import anthropic
from PIL import Image, ImageDraw
import random as _random_module
from shapely.geometry import Polygon, Point, LineString, MultiPoint, MultiPolygon, box
from shapely.affinity import rotate, translate
from shapely.ops import unary_union, split
from shapely import minimum_rotated_rectangle

from app.core.config import get_settings
from app.services.master_plan_design_knowledge import build_site_preview_design_brief
from app.services.site_engine import RealWorldSiteEngine
from app.schemas.schemas import (
    LayoutBuilding,
    LayoutGreenSpace,
    LayoutRoad,
    SiteLayoutResponse,
    SiteLayoutOption,
    SiteMassingOption,
    SiteMassingResponse,
    SiteMassingZone,
)

logger = logging.getLogger(__name__)
settings = get_settings()

METERS_PER_DEG_LAT = 111320


def _zone_requires_district_fabric(zone_type: str, unit_count: int, properties: dict[str, Any]) -> bool:
    dev_type = str(properties.get("development_type") or zone_type or "").strip().lower()
    description = str(properties.get("description_text") or "").strip().lower()
    aesthetic = str(properties.get("development_aesthetic") or properties.get("development_subcategory") or "").strip().lower()
    generation_style_input = properties.get("generation_style_input") if isinstance(properties.get("generation_style_input"), dict) else {}
    generation_style_inputs = properties.get("generation_style_inputs") if isinstance(properties.get("generation_style_inputs"), dict) else {}
    building_input = generation_style_inputs.get("building") if isinstance(generation_style_inputs.get("building"), dict) else {}
    tokens = " ".join(
        filter(
            None,
            [
                description,
                aesthetic,
                str(properties.get("development_archetype_label") or "").lower(),
                str(generation_style_input.get("subtype") or generation_style_input.get("buildingSubcategory") or "").lower(),
                str(building_input.get("subcategory") or building_input.get("buildingSubcategory") or "").lower(),
            ],
        )
    )
    try:
        floors = int(float(properties.get("floors") or properties.get("floor_count") or properties.get("floorCount") or 0))
    except (TypeError, ValueError):
        floors = 0

    strong_signals = (
        "mixed-use", "mixed use", "main street", "district", "precinct", "courtyard", "townhouse",
        "rowhouse", "podium", "park", "civic", "public realm", "retail", "mews", "woonerf",
    )
    if any(token in tokens for token in strong_signals):
        return True
    if zone_type in ("development_area", "residential") and unit_count >= 6:
        return True
    if dev_type in ("mixed_use", "mixed-use", "mixed use", "residential", "commercial") and unit_count >= 8:
        return True
    return floors >= 6


def _generate_civic_anchor_spaces(
    zone_polygon: Polygon,
    properties: dict[str, Any],
    center_lat: float,
) -> list[LayoutGreenSpace]:
    bounds = zone_polygon.bounds
    mlon = _meters_per_deg_lon(center_lat)
    zone_width_m = abs(bounds[2] - bounds[0]) * mlon
    zone_depth_m = abs(bounds[3] - bounds[1]) * METERS_PER_DEG_LAT
    area_m2 = zone_polygon.area * mlon * METERS_PER_DEG_LAT
    if area_m2 < 6500:
        return []

    description = str(properties.get("description_text") or "").strip().lower()
    dev_type = str(properties.get("development_type") or "").strip().lower()
    half_w = _m_to_deg_lon(max(min(zone_width_m * 0.17, 32.0), 12.0), center_lat)
    half_d = _m_to_deg_lat(max(min(zone_depth_m * 0.15, 28.0), 10.0))
    civic_green = LayoutGreenSpace(
        polygon=[
            [-half_w * 0.95, -half_d * 0.40],
            [-half_w * 0.50, -half_d],
            [half_w * 0.30, -half_d * 0.92],
            [half_w, -half_d * 0.08],
            [half_w * 0.72, half_d * 0.82],
            [-half_w * 0.12, half_d],
            [-half_w, half_d * 0.22],
        ],
        space_type="civic_green",
    )
    spaces = [civic_green]

    if any(token in description for token in ("pond", "lake", "water", "basin", "wetland")) or (
        area_m2 >= 16000 and dev_type in {"mixed_use", "mixed-use", "mixed use", "residential"}
    ):
        pond_w = half_w * 0.42
        pond_d = half_d * 0.46
        spaces.append(
            LayoutGreenSpace(
                polygon=[
                    [-pond_w * 0.82, -pond_d * 0.10],
                    [-pond_w * 0.26, -pond_d],
                    [pond_w * 0.62, -pond_d * 0.72],
                    [pond_w, pond_d * 0.10],
                    [pond_w * 0.44, pond_d],
                    [-pond_w * 0.62, pond_d * 0.76],
                    [-pond_w, pond_d * 0.22],
                ],
                space_type="reflecting_pond",
            )
        )
    return spaces



def _gemini_2d_image_model() -> str:
    """Return the configured Gemini model for AI 2D image previews."""
    model = str(getattr(settings, "gemini_2d_image_model", "") or "").strip()
    return model or "gemini-3-pro-image-preview"


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

    # Try base64 decoding - the SDK sometimes returns base64-encoded strings as bytes
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


def _building_footprint(
    cx_deg: float, cy_deg: float,
    width_m: float, depth_m: float,
    rotation_deg: float, mlon: float,
) -> Polygon:
    """Return the rotated rectangle footprint of a building as a Shapely Polygon in degree-space."""
    hw = (width_m / 2) / mlon
    hd = (depth_m / 2) / METERS_PER_DEG_LAT
    rect = Polygon([
        (cx_deg - hw, cy_deg - hd),
        (cx_deg + hw, cy_deg - hd),
        (cx_deg + hw, cy_deg + hd),
        (cx_deg - hw, cy_deg + hd),
    ])
    return rotate(rect, -rotation_deg, origin=(cx_deg, cy_deg))

# =============================================================================
# Building typology palette — varied building types by development type
# =============================================================================

TYPOLOGY_PALETTE: dict[str, list[dict[str, Any]]] = {
    "residential": [
        {"type": "mid_rise_apartment", "width": (16, 24), "depth": (14, 20), "floors": (3, 5), "height_per_floor": 3.2, "weight": 0.35},
        {"type": "townhouse_row", "width": (5, 7), "depth": (10, 14), "floors": (2, 3), "height_per_floor": 3.0, "weight": 0.40},
        {"type": "apartment_block", "width": (20, 30), "depth": (16, 22), "floors": (4, 6), "height_per_floor": 3.2, "weight": 0.15},
        {"type": "walk_up", "width": (12, 16), "depth": (10, 14), "floors": (3, 4), "height_per_floor": 3.0, "weight": 0.10},
    ],
    "mixed_use": [
        {"type": "mixed_use_podium", "width": (18, 28), "depth": (16, 24), "floors": (4, 8), "height_per_floor": 3.5, "weight": 0.30},
        {"type": "retail_liner", "width": (8, 14), "depth": (12, 16), "floors": (2, 3), "height_per_floor": 4.0, "weight": 0.20},
        {"type": "mid_rise_apartment", "width": (16, 24), "depth": (14, 20), "floors": (3, 5), "height_per_floor": 3.2, "weight": 0.25},
        {"type": "townhouse_row", "width": (5, 7), "depth": (10, 14), "floors": (2, 3), "height_per_floor": 3.0, "weight": 0.15},
        {"type": "office_block", "width": (20, 30), "depth": (16, 24), "floors": (4, 8), "height_per_floor": 3.5, "weight": 0.10},
    ],
    "commercial": [
        {"type": "office_block", "width": (20, 35), "depth": (18, 28), "floors": (4, 10), "height_per_floor": 3.5, "weight": 0.40},
        {"type": "retail_liner", "width": (8, 14), "depth": (12, 16), "floors": (1, 2), "height_per_floor": 4.5, "weight": 0.30},
        {"type": "mixed_use_podium", "width": (18, 28), "depth": (16, 24), "floors": (3, 6), "height_per_floor": 3.5, "weight": 0.30},
    ],
}


def _pick_building_type(
    dev_type: str,
    block_role: str,
    rng: _random_module.Random,
) -> dict[str, Any]:
    """Select a building typology from the palette based on development type and block role.

    block_role: 'corner', 'primary_frontage', 'secondary', 'interior'
    """
    palette = TYPOLOGY_PALETTE.get(dev_type, TYPOLOGY_PALETTE["residential"])

    # Corner and primary frontage blocks favour taller/larger types
    if block_role in ("corner", "primary_frontage"):
        # Boost weight for taller types
        adjusted = []
        for t in palette:
            boost = 1.5 if t["floors"][1] >= 4 else 0.7
            adjusted.append({**t, "weight": t["weight"] * boost})
        palette = adjusted

    total = sum(t["weight"] for t in palette)
    r = rng.random() * total
    cumulative = 0.0
    for t in palette:
        cumulative += t["weight"]
        if r <= cumulative:
            return t
    return palette[-1]


def _sample_building_dims(
    typology: dict[str, Any],
    rng: _random_module.Random,
) -> tuple[float, float, int, float]:
    """Return (width_m, depth_m, floors, height_m) sampled from a typology entry."""
    w = rng.uniform(typology["width"][0], typology["width"][1])
    d = rng.uniform(typology["depth"][0], typology["depth"][1])
    floors = rng.randint(typology["floors"][0], typology["floors"][1])
    h = floors * typology["height_per_floor"]
    return round(w, 1), round(d, 1), floors, round(h, 1)


# =============================================================================
# Road network generation — connected streets forming blocks
# =============================================================================

def _generate_road_network(
    zone_polygon: Polygon,
    unit_count: int,
    primary_angle_rad: float,
    center_lat: float,
) -> tuple[list[dict[str, Any]], list[Polygon]]:
    """Generate a connected road network and the block polygons they create.

    Returns (roads, blocks) where:
      roads: list of dicts with keys 'centerline_deg' (list of (lon, lat) tuples),
             'width_m', 'road_type'
      blocks: list of Shapely Polygon in degree-space
    """
    centroid = zone_polygon.centroid
    mlon = _meters_per_deg_lon(center_lat)
    bounds = zone_polygon.bounds
    zone_width_m = abs(bounds[2] - bounds[0]) * mlon
    zone_depth_m = abs(bounds[3] - bounds[1]) * METERS_PER_DEG_LAT
    zone_span = max(zone_width_m, zone_depth_m)

    cos_a = math.cos(primary_angle_rad)
    sin_a = math.sin(primary_angle_rad)
    perp_rad = primary_angle_rad + math.pi / 2
    cos_p = math.cos(perp_rad)
    sin_p = math.sin(perp_rad)

    road_half_len = zone_span / 2 * 0.88

    roads: list[dict[str, Any]] = []

    # --- Primary road (collector for large zones, local for small) ---
    primary_width = 8.0 if unit_count > 20 else 6.0
    primary_type = "collector" if unit_count > 20 else "local"
    p_start = (centroid.x + _m_to_deg_lon(-road_half_len * cos_a, center_lat),
               centroid.y + _m_to_deg_lat(-road_half_len * sin_a))
    p_end = (centroid.x + _m_to_deg_lon(road_half_len * cos_a, center_lat),
             centroid.y + _m_to_deg_lat(road_half_len * sin_a))
    primary_line = LineString([p_start, p_end]).intersection(zone_polygon)
    if primary_line.is_empty or not isinstance(primary_line, LineString):
        primary_line = LineString([p_start, p_end])

    roads.append({
        "centerline_deg": list(primary_line.coords),
        "width_m": primary_width,
        "road_type": primary_type,
    })

    # --- Cross streets (perpendicular) ---
    # For medium+ zones, add cross streets at ~70m intervals
    cross_width = 6.0
    cross_interval_m = 70.0
    cross_half_len = zone_span / 2 * 0.75

    num_crosses = 0
    if unit_count >= 8:
        num_crosses = max(1, min(int(zone_span / cross_interval_m) - 1, 4))

    if num_crosses > 0:
        # Distribute cross streets evenly along primary road
        primary_len_m = zone_span * 0.88
        for i in range(num_crosses):
            t = (i + 1) / (num_crosses + 1)
            along_m = -road_half_len + t * primary_len_m * 2
            # Cross street center point
            cx_m = along_m * cos_a
            cy_m = along_m * sin_a
            # Cross street endpoints
            c_start = (centroid.x + _m_to_deg_lon(cx_m - cross_half_len * cos_p, center_lat),
                        centroid.y + _m_to_deg_lat(cy_m - cross_half_len * sin_p))
            c_end = (centroid.x + _m_to_deg_lon(cx_m + cross_half_len * cos_p, center_lat),
                      centroid.y + _m_to_deg_lat(cy_m + cross_half_len * sin_p))
            cross_line = LineString([c_start, c_end]).intersection(zone_polygon)
            if cross_line.is_empty or not isinstance(cross_line, LineString):
                continue
            roads.append({
                "centerline_deg": list(cross_line.coords),
                "width_m": cross_width,
                "road_type": "local",
            })

    # --- Subdivide zone into blocks by buffering roads and subtracting ---
    road_corridors = []
    for rd in roads:
        line = LineString(rd["centerline_deg"])
        # Buffer in degree-space (approximate)
        buf_lon = (rd["width_m"] / 2 + 1.0) / mlon  # +1m for sidewalk
        buf_lat = (rd["width_m"] / 2 + 1.0) / METERS_PER_DEG_LAT
        avg_buf = (buf_lon + buf_lat) / 2
        corridor = line.buffer(avg_buf, cap_style=2)  # flat cap
        road_corridors.append(corridor)

    if road_corridors:
        all_corridors = unary_union(road_corridors)
        remaining = zone_polygon.difference(all_corridors)
    else:
        remaining = zone_polygon

    # Extract individual block polygons
    blocks: list[Polygon] = []
    if isinstance(remaining, Polygon) and remaining.area > 0:
        blocks.append(remaining)
    elif isinstance(remaining, MultiPolygon):
        for geom in remaining.geoms:
            if isinstance(geom, Polygon) and geom.area > 0:
                blocks.append(geom)
    elif hasattr(remaining, 'geoms'):
        for geom in remaining.geoms:
            if isinstance(geom, Polygon) and geom.area > 0:
                blocks.append(geom)

    # Filter out slivers (blocks too small to place a building)
    min_block_area_m2 = 120.0
    min_block_area_deg = min_block_area_m2 / (mlon * METERS_PER_DEG_LAT)
    blocks = [b for b in blocks if b.area >= min_block_area_deg]

    return roads, blocks


# =============================================================================
# Block classification — determine role for building type selection
# =============================================================================

def _classify_block(
    block: Polygon,
    roads: list[dict[str, Any]],
    all_blocks: list[Polygon],
    center_lat: float,
) -> str:
    """Classify a block as 'corner', 'primary_frontage', 'secondary', or 'interior'."""
    mlon = _meters_per_deg_lon(center_lat)

    frontage_count = 0
    has_primary = False
    for rd in roads:
        line = LineString(rd["centerline_deg"])
        buf = (rd["width_m"] / 2 + 3.0) / ((mlon + METERS_PER_DEG_LAT) / 2)
        road_zone = line.buffer(buf)
        if block.intersects(road_zone):
            frontage_count += 1
            if rd["road_type"] == "collector":
                has_primary = True

    if frontage_count >= 2:
        return "corner"
    if has_primary:
        return "primary_frontage"
    if frontage_count == 1:
        return "secondary"
    return "interior"


# =============================================================================
# Block-perimeter building placement
# =============================================================================

def _infill_block(
    block: Polygon,
    block_role: str,
    dev_type: str,
    roads: list[dict[str, Any]],
    centroid_lon: float,
    centroid_lat: float,
    rng: _random_module.Random,
    max_buildings: int = 50,
    block_idx: int = 0,
) -> tuple[list[LayoutBuilding], list[LayoutGreenSpace]]:
    """Place buildings around the perimeter of a block facing streets.

    Returns (buildings, green_spaces) for this block.
    """
    mlon = _meters_per_deg_lon(centroid_lat)
    buildings: list[LayoutBuilding] = []
    placed_footprints: list[Polygon] = []

    # Get block edges
    coords = list(block.exterior.coords)
    if len(coords) < 4:
        return buildings, []

    # Find which edges face a road
    road_facing_edges: list[tuple[int, float]] = []  # (edge_index, road_angle)
    for i in range(len(coords) - 1):
        edge_mid = Point((coords[i][0] + coords[i + 1][0]) / 2,
                         (coords[i][1] + coords[i + 1][1]) / 2)
        edge_dx = (coords[i + 1][0] - coords[i][0]) * mlon
        edge_dy = (coords[i + 1][1] - coords[i][1]) * METERS_PER_DEG_LAT
        edge_len_m = math.hypot(edge_dx, edge_dy)
        if edge_len_m < 5.0:
            continue  # Skip very short edges
        edge_angle = math.degrees(math.atan2(edge_dy, edge_dx))

        # Check if this edge is near a road
        for rd in roads:
            line = LineString(rd["centerline_deg"])
            dist_deg = line.distance(edge_mid)
            dist_m = dist_deg * ((mlon + METERS_PER_DEG_LAT) / 2)
            if dist_m < rd["width_m"] + 8.0:  # Within road width + setback
                road_facing_edges.append((i, edge_angle))
                break

    # If no road-facing edges found, use longest edges
    if not road_facing_edges:
        edge_lengths = []
        for i in range(len(coords) - 1):
            dx = (coords[i + 1][0] - coords[i][0]) * mlon
            dy = (coords[i + 1][1] - coords[i][1]) * METERS_PER_DEG_LAT
            edge_lengths.append((math.hypot(dx, dy), i))
        edge_lengths.sort(reverse=True)
        for length, idx in edge_lengths[:2]:
            if length >= 10.0:
                dx = (coords[idx + 1][0] - coords[idx][0]) * mlon
                dy = (coords[idx + 1][1] - coords[idx][1]) * METERS_PER_DEG_LAT
                angle = math.degrees(math.atan2(dy, dx))
                road_facing_edges.append((idx, angle))

    setback_m = 3.0
    gap_m = 3.0

    for edge_idx, edge_angle_deg in road_facing_edges:
        if len(buildings) >= max_buildings:
            break

        p1 = coords[edge_idx]
        p2 = coords[edge_idx + 1]
        edge_dx = (p2[0] - p1[0]) * mlon
        edge_dy = (p2[1] - p1[1]) * METERS_PER_DEG_LAT
        edge_len_m = math.hypot(edge_dx, edge_dy)
        if edge_len_m < 10.0:
            continue

        # Unit vector along and perpendicular to edge
        ux = edge_dx / edge_len_m
        uy = edge_dy / edge_len_m
        # Inward normal (toward block interior)
        block_center = block.centroid
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        to_center_x = (block_center.x - mid_x) * mlon
        to_center_y = (block_center.y - mid_y) * METERS_PER_DEG_LAT
        # Two possible normals
        nx1, ny1 = -uy, ux
        nx2, ny2 = uy, -ux
        # Pick the one pointing toward block center
        if nx1 * to_center_x + ny1 * to_center_y > 0:
            nx, ny = nx1, ny1
        else:
            nx, ny = nx2, ny2

        # Place buildings along this edge
        cursor_m = gap_m
        while cursor_m < edge_len_m - gap_m and len(buildings) < max_buildings:
            typology = _pick_building_type(dev_type, block_role, rng)
            w, d, floors, h = _sample_building_dims(typology, rng)

            # Building center: along edge at cursor, offset inward by setback + depth/2
            along_frac = cursor_m / edge_len_m
            cx_deg = p1[0] + along_frac * (p2[0] - p1[0])
            cy_deg = p1[1] + along_frac * (p2[1] - p1[1])
            offset_m = setback_m + d / 2
            cx_deg += _m_to_deg_lon(nx * offset_m, centroid_lat)
            cy_deg += _m_to_deg_lat(ny * offset_m)

            # Building rotation: long side parallel to edge
            building_rot = edge_angle_deg

            # Convert to centroid-relative coords
            bx_rel = cx_deg - centroid_lon
            by_rel = cy_deg - centroid_lat

            # Check footprint fits within block
            footprint = _building_footprint(cx_deg, cy_deg, w, d, building_rot, mlon)
            overlap = footprint.intersection(block).area
            if footprint.area > 0 and overlap / footprint.area < 0.70:
                cursor_m += w / 2 + gap_m
                continue

            # Check minimum separation from other buildings
            too_close = False
            for existing_fp in placed_footprints:
                if footprint.distance(existing_fp) * ((mlon + METERS_PER_DEG_LAT) / 2) < 2.5:
                    too_close = True
                    break
            if too_close:
                cursor_m += w / 2 + gap_m
                continue

            buildings.append(LayoutBuilding(
                center_x=bx_rel,
                center_y=by_rel,
                width_m=w,
                depth_m=d,
                rotation_deg=building_rot % 360,
                height_m=h,
                floors=floors,
                building_type=dev_type if dev_type in ("residential", "commercial", "mixed_use", "retail", "civic", "institutional") else "residential",
                building_typology=typology["type"],
                block_id=block_idx,
                setback_front_m=setback_m,
                setback_side_m=1.5,
            ))
            placed_footprints.append(footprint)
            cursor_m += w + gap_m

    # --- Generate green spaces from remaining block interior ---
    green_spaces: list[LayoutGreenSpace] = []
    if placed_footprints:
        all_bldg = unary_union(placed_footprints)
        interior = block.difference(all_bldg.buffer(0.000001))
        # Find the largest open space as courtyard/garden
        if isinstance(interior, Polygon) and interior.area > 0:
            open_polygons = [interior]
        elif isinstance(interior, MultiPolygon):
            open_polygons = [g for g in interior.geoms if isinstance(g, Polygon) and g.area > 0]
        else:
            open_polygons = []

        min_green_area_deg = 80.0 / (mlon * METERS_PER_DEG_LAT)
        for open_poly in open_polygons:
            if open_poly.area < min_green_area_deg:
                continue
            area_m2 = open_poly.area * mlon * METERS_PER_DEG_LAT
            # Classify the space
            if area_m2 > 400:
                space_type = "courtyard"
            elif area_m2 > 150:
                space_type = "park"
            else:
                space_type = "buffer"

            poly_coords = [
                [c[0] - centroid_lon, c[1] - centroid_lat]
                for c in open_poly.exterior.coords
            ]
            green_spaces.append(LayoutGreenSpace(
                polygon=poly_coords,
                space_type=space_type,
            ))

    return buildings, green_spaces


# =============================================================================
# Layout variation strategies
# =============================================================================

def _generate_block_layout(
    zone_polygon: Polygon,
    zone_type: str,
    unit_count: int,
    properties: dict[str, Any],
    primary_angle_rad: float,
    strategy: str,
    seed: int = 0,
) -> SiteLayoutResponse:
    """Generate a complete block-based layout for one variation strategy.

    strategy: 'perimeter_courtyard', 'main_street', 'green_spine'
    """
    centroid = zone_polygon.centroid
    center_lat = centroid.y
    mlon = _meters_per_deg_lon(center_lat)
    rng = _random_module.Random(seed)

    dev_type = str(properties.get("development_type") or zone_type or "residential").lower()
    if dev_type not in TYPOLOGY_PALETTE:
        dev_type = "residential"

    # Generate road network
    roads_raw, blocks = _generate_road_network(
        zone_polygon, unit_count, primary_angle_rad, center_lat,
    )

    # Convert roads to LayoutRoad format
    layout_roads = []
    for rd in roads_raw:
        centerline_rel = [
            [c[0] - centroid.x, c[1] - centroid.y]
            for c in rd["centerline_deg"]
        ]
        layout_roads.append(LayoutRoad(
            centerline=centerline_rel,
            width_m=rd["width_m"],
            road_type=rd["road_type"],
        ))

    # Classify blocks
    all_buildings: list[LayoutBuilding] = []
    all_greens: list[LayoutGreenSpace] = []

    if not blocks:
        # Fallback: treat entire zone as one block
        blocks = [zone_polygon]

    # Strategy-specific adjustments
    if strategy == "green_spine":
        # Reserve the largest interior block for a linear park
        if len(blocks) > 2:
            blocks_by_area = sorted(blocks, key=lambda b: b.area, reverse=True)
            # Find an interior block (not the largest — that's usually an edge piece)
            park_block = None
            for blk in blocks_by_area[1:]:
                role = _classify_block(blk, roads_raw, blocks, center_lat)
                if role in ("interior", "secondary"):
                    park_block = blk
                    break
            if park_block:
                blocks = [b for b in blocks if b != park_block]
                park_coords = [
                    [c[0] - centroid.x, c[1] - centroid.y]
                    for c in park_block.exterior.coords
                ]
                all_greens.append(LayoutGreenSpace(
                    polygon=park_coords,
                    space_type="park",
                ))

    # Infill each block with buildings
    buildings_remaining = unit_count
    for bi, block in enumerate(blocks):
        if buildings_remaining <= 0:
            break
        role = _classify_block(block, roads_raw, blocks, center_lat)

        # Strategy-specific type override
        block_dev_type = dev_type
        if strategy == "main_street" and role in ("corner", "primary_frontage"):
            block_dev_type = "mixed_use"

        max_in_block = min(buildings_remaining, max(2, int(unit_count * block.area / zone_polygon.area * 1.3)))
        bldgs, greens = _infill_block(
            block, role, block_dev_type, roads_raw,
            centroid.x, centroid.y, rng,
            max_buildings=max_in_block,
            block_idx=bi,
        )
        all_buildings.extend(bldgs)
        all_greens.extend(greens)
        buildings_remaining -= len(bldgs)

    # Add civic anchor for large zones
    if _zone_requires_district_fabric(zone_type, unit_count, properties):
        civic = _generate_civic_anchor_spaces(zone_polygon, properties, center_lat)
        all_greens.extend(civic)

    area_ha = zone_polygon.area * mlon * METERS_PER_DEG_LAT / 10000

    strategy_labels = {
        "perimeter_courtyard": "Perimeter Courtyard — buildings frame streets, green courtyards inside",
        "main_street": "Main Street — mixed-use on primary road, residential on side streets",
        "green_spine": "Green Spine — linear park at center, buildings face inward",
    }

    return SiteLayoutResponse(
        buildings=all_buildings,
        roads=layout_roads,
        green_spaces=all_greens,
        layout_strategy=strategy,
        reasoning=strategy_labels.get(strategy, strategy) + f" — placed {len(all_buildings)} buildings in {len(blocks)} blocks",
        density_achieved=round(len(all_buildings) / max(area_ha, 0.01), 1),
    )


SITE_PLAN_PROMPT_BASELINE = (
    "Photoreal orthographic district master plan. True top-down view only. No side views. No elevations. "
    "Render one continuous urban ground plane with crisp roof plans, streets, hardscape, landscape, and water all shown in plan view. "
    "Context should remain visible but subdued. No board graphics. No floating images."
)
SITE_PLAN_NEGATIVE_CONSTRAINTS = (
    "STRICTLY FORBIDDEN: side-view elevations, elevation-style renderings, profile-view buildings, thumbnail perspectives, "
    "floating cutouts, pasted precedent images, semi-transparent reference boards, image-within-image compositions, eye-level views, architectural edge studies, undefined blank site filler, and embedded text."
)
SITE_PLAN_TEXT_REPLACEMENTS = (
    (r"\bfront_day\b", "daytime plan reference"),
    (r"\bfront_golden_hour\b", "golden-hour plan reference"),
    (r"\bfront_overcast\b", "overcast plan reference"),
    (r"\bfront_rain_reflection\b", "rain-washed plan reference"),
    (r"\bfront\s+day\b", "daytime plan reference"),
    (r"\bfront\s+golden\s+hour\b", "golden-hour plan reference"),
    (r"\bfront\s+overcast\b", "overcast plan reference"),
    (r"\bfront\s+rain\s+reflection\b", "rain-washed plan reference"),
    (r"\bresidential front elevation\b", "residential roof plan character"),
    (r"\bfront elevation\b", "roof plan character"),
    (r"\bfront[-\s]?facing\b", "plan-view"),
    (r"\bstreet[-\s]?level(?:\s+eye[-\s]?height)?\s+camera\b", "90-degree overhead orthographic view"),
    (r"\bstreet[-\s]?level\b", "plan-view"),
    (r"\beye[-\s]?height\b", "overhead orthographic"),
    (r"\brestrained perspective distortion\b", "orthographic clarity"),
    (r"\bbalanced verticals\b", "clean linework"),
    (r"\bperspective\b", "plan-view"),
    (r"\bsection perspective\b", "plan-view massing relationship"),
    (r"\bprofile[-\s]?view\b", "plan-view"),
    (r"\belevation board\b", "plan-view precedent"),
    (r"\bprecedent image\b", "plan-view precedent"),
    (r"\bfacade\b", "architectural edge"),
    (r"\bwindows?\b", "frontage rhythm"),
)
SITE_PLAN_DROP_PATTERNS = (
    r"\bcentered subject dominance\b\.?",
    r"\bsubject is centered and dominant in frame\b\.?",
    r"\bconsistent framing and crop\b\.?",
    r"\bcontrolled, low-clutter background\b\.?",
    r"\bgrounded cinematic atmosphere\b\.?",
    r"\bphotoreal architectural and urban design rendering\b\.?",
    r"\bno text overlays(?: inside image)?\b\.?",
    r"\bno collage layout\b\.?",
    r"\bno watermark or logo text\b\.?",
    r"\bno dominant crowds obscuring the subject\b\.?",
    r"\bno random unrelated backgrounds\b\.?",
    r"\bno fantasy impossible geometry\b\.?",
    r"\bno fantasy geometry\b\.?",
    r"\bno extreme fisheye perspective\b\.?",
    r"\btarget output \d+x\d+(?: \([^)]*\))?\b\.?",
    r"\bbenchmark visual direction:[^.]*\.?",
)


def _site_preview_clean_text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value
    elif isinstance(value, dict):
        text = ' '.join(str(child) for child in value.values() if child not in (None, ''))
    elif isinstance(value, (list, tuple, set)):
        text = ' '.join(str(child) for child in value if child not in (None, ''))
    else:
        text = str(value)
    text = re.sub(r"\s+", " ", text).strip()
    return text or None


def _site_preview_sanitize_text(value: Any) -> str | None:
    text = _site_preview_clean_text(value)
    if not text:
        return None
    for pattern, replacement in SITE_PLAN_TEXT_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    for pattern in SITE_PLAN_DROP_PATTERNS:
        text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    text = text.strip(' ,.;:-')
    return text or None

def _site_preview_color_name(hex_color: str | None) -> str | None:
    if not hex_color:
        return None
    color_map = {
        "#f59e0b": "amber/orange",
        "#9b59b6": "purple",
        "#e91e8a": "pink/magenta",
        "#444444": "dark gray",
        "#27ae60": "green",
        "#95a5a6": "light gray",
        "#3498db": "blue",
        "#d4a574": "tan/brown",
    }
    return color_map.get(hex_color.lower(), hex_color)


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
            logger.warning("AI layout generation failed (%s): %s - using algorithmic fallback", provider, e)
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
            logger.warning("AI layout options failed (%s): %s - using algorithmic variations", provider, e)

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
                # Description text - user-written, most important context
                if zp.get("description_text"):
                    attrs.append(f'description: "{zp["description_text"]}"')

                label = zone_type_labels.get(zt, zt)
                attr_str = f" ({', '.join(attrs)})" if attrs else ""
                line = f"  - {name} [{label}]{attr_str} - center at ({dx},{dy})m, {w:.0f}m x {d:.0f}m"
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
- Respect water features and parks - do not place buildings over them
- Orient buildings to face existing roads when near the boundary
"""

        # Build locked layers section
        locked_section = ""
        if locked_layers:
            lock_parts = []
            if locked_layers.get("roads"):
                lock_parts.append(f"Locked roads ({len(locked_layers['roads'])} elements) - keep these road positions exactly as specified:")
                for i, r in enumerate(locked_layers["roads"]):
                    lock_parts.append(f"  Road {i}: centerline={json.dumps(r.get('centerline', []))}, width={r.get('width_m', 6)}m")
            if locked_layers.get("buildings"):
                lock_parts.append(f"Locked buildings ({len(locked_layers['buildings'])} elements) - keep these building positions exactly")
            if locked_layers.get("green_spaces"):
                lock_parts.append(f"Locked green spaces ({len(locked_layers['green_spaces'])} elements) - keep these green space positions exactly")

            if lock_parts:
                locked_section = f"""
## Locked Elements (DO NOT MODIFY)
{chr(10).join(lock_parts)}

**Locked layer rules:**
- Include all locked elements in your output UNCHANGED
- Generate new unlocked elements that work around the locked ones
- Ensure new buildings don't overlap with locked roads or green spaces
"""
        district_mode = _zone_requires_district_fabric(zone_type, unit_count, properties)
        is_orientation_window = count > 3 and district_mode
        if is_orientation_window:
            layout_strategy_text = f"""## Layout Strategies to Generate
This zone should read as a complete district. Return {count} options that preserve approximately similar density while rotating the primary block and street orientation across options.
- Option 1 should emphasize perimeter courtyard urbanism aligned to the site's longest axis
- Option 2 should emphasize a mixed-use edge block with a civic green or water-ready anchor
- Option 3 should emphasize a townhouse or fine-grain residential edge with an internal mews or woonerf
- Later options should rotate the primary block orientation while keeping buildings parallel to roads or site edges
- Every option must define buildings, serviceable internal roads or mews where appropriate, and green_spaces/open-space polygons so no major residual space is left undefined
- Use roads and green_spaces arrays whenever they improve realism, circulation, or district legibility
- Include "orientation_deg" and set "orientation_mode" to "site_orientation" for each option
"""
        elif district_mode:
            layout_strategy_text = """## Layout Strategies to Generate
Each layout must use a different district-building strategy:
1. **Perimeter Courtyard Block** - edge-aligned buildings define a courtyard and street wall
2. **Mixed-Use Main Street** - perimeter massing with active frontage, internal access, and a civic green anchor
3. **Townhouse + Mid-Rise Mix** - finer-grain residential edge with a shared mews, forecourts, and planted open space

IMPORTANT:
- Treat this as district construction, not isolated placement
- Do not leave major white space; classify residual space as road, hardscape, or landscape
- Buildings should generally align parallel to the nearest road segment or site edge
- Roads and green_spaces arrays should be used to define circulation and civic space, not left empty by default
"""
        else:
            layout_strategy_text = """## Layout Strategies to Generate
Each layout must use a different coherent site strategy:
1. **Compact Building Cluster** - buildings with shared hardscape and planted edges
2. **Road-Served Court** - buildings organized around a serviceable internal lane
3. **Green-Centered Composition** - buildings framing a shared landscape room

IMPORTANT:
- Every option must define circulation clearly
- Residual space should become hardscape or landscape, not undefined filler
"""

        prompt = f"""You are a senior computational urban designer. Generate {count} DIFFERENT layout strategies for the same zone.

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

{layout_strategy_text}

## Urban Systems Rules
- Construct a coherent district or precinct, not isolated building objects
- Never leave major white space. If an area is not building footprint, make it road, hardscape, planted landscape, water, or civic space
- Align buildings parallel to the nearest road segment or site boundary where possible; prefer disciplined orthogonal geometry and 90-degree increments unless the site edge clearly demands otherwise
- Every building must be serviced by a realistic road, shared street, mews, or hardscape apron
- Anchor larger layouts with at least one primary civic or landscape space
- Keep all building positions inside the zone polygon and coordinate new roads to connect to existing roads when present
- Maintain a minimum 3.0m fire gap between distinct structures unless a perimeter block requires attached frontage logic
- Position values are DEGREE OFFSETS from zone centroid ({centroid.x:.8f}, {centroid.y:.8f})

## Conversion Reference
- 1 meter east/west = {_m_to_deg_lon(1, center_lat):.10f} degrees longitude
- 1 meter north/south = {_m_to_deg_lat(1):.10f} degrees latitude

## Building Typology
Assign each building an appropriate `building_typology` from:
- `townhouse_row`: 5-7m wide, 10-14m deep, 2-3 floors — fine-grain residential
- `mid_rise_apartment`: 16-24m wide, 14-20m deep, 3-5 floors — standard residential block
- `apartment_block`: 20-30m wide, 16-22m deep, 4-6 floors — larger residential
- `mixed_use_podium`: 18-28m wide, 16-24m deep, 4-8 floors — retail ground floor + residential above
- `retail_liner`: 8-14m wide, 12-16m deep, 1-3 floors — shopfront buildings
- `office_block`: 20-35m wide, 18-28m deep, 4-10 floors — commercial office

Group buildings into blocks using `block_id` (integer). Buildings in the same block share a street frontage and form a coherent cluster.

## Evaluation Criteria
- Every block must have street frontage on at least one side
- No building may be more than 50m from a road centerline
- The largest contiguous open space must be at least 400 sq m
- At least 2 different building typologies must be used for zones with 8+ units
- Building footprints must not overlap each other (minimum 3m separation)

## Required JSON Response
Return ONLY a JSON array of {count} layout objects. Each object has this schema:
[
  {{
    "layout_strategy": "<strategy_name>",
    "option_label": "<human readable label>",
    "orientation_deg": <optional float>,
    "orientation_mode": "<optional string, e.g. site_orientation>",
    "reasoning": "<brief explanation>",
    "density_achieved": <float>,
    "buildings": [
      {{
        "center_x": <float: longitude offset from centroid>,
        "center_y": <float: latitude offset from centroid>,
        "width_m": <float>, "depth_m": <float>,
        "rotation_deg": <float>,
        "building_type": "<residential|commercial|mixed_use|retail|civic|institutional>",
        "building_typology": "<townhouse_row|mid_rise_apartment|apartment_block|mixed_use_podium|retail_liner|office_block>",
        "block_id": <int: which block this building belongs to>,
        "setback_front_m": 3.0, "setback_side_m": 1.5
      }}
    ],
    "roads": [
      {{ "centerline": [[<x_deg>, <y_deg>], ...], "width_m": 6.0, "road_type": "local" }}
    ],
    "green_spaces": [
      {{ "polygon": [[<x_deg>, <y_deg>], ...], "space_type": "<civic_green|courtyard|entry_plaza|planted_verge|pocket_park>" }}
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
            text = text.split(chr(10), 1)[1]
            text = text.rsplit("```", 1)[0]

        data = json.loads(text)
        logger.info("AI response parsed: type=%s, len=%s", type(data).__name__, len(data) if isinstance(data, list) else 1)

        if isinstance(data, dict):
            data = [data]

        centroid = zone_polygon.centroid
        logger.info("Zone centroid: (%f, %f), bounds: %s", centroid.x, centroid.y, zone_polygon.bounds)
        options: list[SiteLayoutOption] = []

        for idx, item in enumerate(data[:count]):
            layout = SiteLayoutResponse(**item)
            logger.info("Option %d: %d buildings, %d roads, strategy=%s", idx, len(layout.buildings), len(layout.roads), layout.layout_strategy)

            valid_buildings = []
            for b in layout.buildings:
                pt = Point(centroid.x + b.center_x, centroid.y + b.center_y)
                inside = zone_polygon.contains(pt)
                dist = zone_polygon.distance(pt)
                if inside or dist < 0.00001:
                    valid_buildings.append(b)
                else:
                    logger.warning("Preview option %d: building at center_x=%f, center_y=%f -> point(%f,%f) outside zone (dist=%f)", idx, b.center_x, b.center_y, pt.x, pt.y, dist)
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
                orientation_deg=item.get("orientation_deg"),
                orientation_mode=item.get("orientation_mode"),
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
        """Generate structurally different layout variations.

        For district-fabric zones, generates three different urban design
        strategies (perimeter courtyard, main street, green spine).
        For simpler zones, falls back to orientation-based grid placement.
        """
        centroid = zone_polygon.centroid
        center_lat = centroid.y
        mlon = _meters_per_deg_lon(center_lat)

        obb = minimum_rotated_rectangle(zone_polygon)
        obb_coords = list(obb.exterior.coords)

        edges = []
        for i in range(len(obb_coords) - 1):
            dx = (obb_coords[i + 1][0] - obb_coords[i][0]) * mlon
            dy = (obb_coords[i + 1][1] - obb_coords[i][1]) * METERS_PER_DEG_LAT
            length = math.sqrt(dx * dx + dy * dy)
            edges.append((length, i))
        edges.sort(reverse=True)

        longest_idx = edges[0][1]
        p1_long = obb_coords[longest_idx]
        p2_long = obb_coords[longest_idx + 1]
        angle_long = math.atan2(
            (p2_long[1] - p1_long[1]) * METERS_PER_DEG_LAT,
            (p2_long[0] - p1_long[0]) * mlon,
        )

        district_mode = _zone_requires_district_fabric(zone_type, unit_count, properties)

        options: list[SiteLayoutOption] = []

        if district_mode and unit_count >= 6:
            # Generate structurally different strategies
            strategy_defs = [
                ("perimeter_courtyard", "Perimeter Courtyard"),
                ("main_street", "Main Street"),
                ("green_spine", "Green Spine"),
            ]

            for idx, (strategy_key, label) in enumerate(strategy_defs[:count]):
                layout = _generate_block_layout(
                    zone_polygon, zone_type, unit_count, properties,
                    angle_long, strategy_key, seed=idx * 1337,
                )
                orientation_deg = (math.degrees(angle_long) + 360.0) % 360.0
                option = SiteLayoutOption(
                    option_index=idx,
                    option_label=label,
                    buildings=layout.buildings,
                    roads=layout.roads,
                    green_spaces=layout.green_spaces,
                    layout_strategy=strategy_key,
                    reasoning=layout.reasoning,
                    density_achieved=layout.density_achieved,
                    orientation_deg=round(orientation_deg, 1),
                    orientation_mode="strategy_mix",
                )
                options.append(option)

            return options

        # Fallback for non-district zones: orientation-based placement
        shortest_idx = edges[1][1] if len(edges) > 1 else longest_idx
        p1_short = obb_coords[shortest_idx]
        p2_short = obb_coords[shortest_idx + 1]
        angle_short = math.atan2(
            (p2_short[1] - p1_short[1]) * METERS_PER_DEG_LAT,
            (p2_short[0] - p1_short[0]) * mlon,
        )

        angle_diagonal = angle_long + math.pi / 4
        strategies = [
            ("along_longest", "Along Longest Axis", angle_long),
            ("along_shortest", "Along Shortest Axis", angle_short),
            ("diagonal", "Diagonal", angle_diagonal),
        ]

        for idx, (strategy_name, label, orientation_rad) in enumerate(strategies[:count]):
            layout = self._generate_algorithmic_buildings_only(
                zone_polygon, zone_type, unit_count, properties, orientation_rad,
            )
            orientation_deg = (math.degrees(orientation_rad) + 360.0) % 360.0
            option = SiteLayoutOption(
                option_index=idx,
                option_label=label,
                buildings=layout.buildings,
                roads=layout.roads,
                green_spaces=layout.green_spaces,
                layout_strategy=strategy_name,
                reasoning=layout.reasoning,
                density_achieved=layout.density_achieved,
                orientation_deg=round(orientation_deg, 1),
                orientation_mode="strategy_mix",
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
        """Generate a layout with buildings only - no internal road."""
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

                rotation_variation = ((row + col) % 3 - 1) * 3
                building_rotation = orientation_deg + rotation_variation

                # Check that the building footprint is mostly inside the zone
                bldg_rect = _building_footprint(
                    centroid.x + cx, centroid.y + cy,
                    building_width_m, building_depth_m,
                    building_rotation, mlon,
                )
                overlap = bldg_rect.intersection(zone_polygon).area
                if bldg_rect.area > 0 and overlap / bldg_rect.area < 0.85:
                    continue

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

        logger.info(
            "buildings_only: placed %d of %d in zone %.1fx%.1fm (building %.1fx%.1fm, orientation %.1f degrees)",
            len(buildings), unit_count, zone_width_m, zone_depth_m,
            building_width_m, building_depth_m, orientation_deg,
        )

        return SiteLayoutResponse(
            buildings=buildings,
            roads=[],
            green_spaces=[],
            layout_strategy="buildings_only",
            reasoning=f"Buildings only (no road) - placed {len(buildings)} of {unit_count} buildings in a grid",
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

                face_angle = road_angle_deg + 90 * side
                rotation_variation = (i % 3 - 1) * 3
                building_rotation = face_angle + rotation_variation

                bldg_rect = _building_footprint(
                    centroid.x + cx, centroid.y + cy,
                    building_width_m, building_depth_m,
                    building_rotation, mlon,
                )
                overlap = bldg_rect.intersection(zone_polygon).area
                if bldg_rect.area > 0 and overlap / bldg_rect.area < 0.85:
                    # Try without stagger
                    actual_offset = offset_from_road_m
                    bx_m = along_m * cos_a + side * actual_offset * math.cos(perpendicular_rad)
                    by_m = along_m * sin_a + side * actual_offset * math.sin(perpendicular_rad)
                    cx = _m_to_deg_lon(bx_m, center_lat)
                    cy = _m_to_deg_lat(by_m)
                    bldg_rect = _building_footprint(
                        centroid.x + cx, centroid.y + cy,
                        building_width_m, building_depth_m,
                        building_rotation, mlon,
                    )
                    overlap = bldg_rect.intersection(zone_polygon).area
                    if bldg_rect.area > 0 and overlap / bldg_rect.area < 0.85:
                        continue

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

        if _zone_requires_district_fabric(zone_type, unit_count, properties):
            green_spaces.extend(_generate_civic_anchor_spaces(zone_polygon, properties, center_lat))

        area_ha = zone_polygon.area * mlon * METERS_PER_DEG_LAT / 10000

        return SiteLayoutResponse(
            buildings=buildings,
            roads=[road],
            green_spaces=green_spaces,
            layout_strategy=strategy_name,
            reasoning=f"Algorithmic: {strategy_name.replace('_', ' ')} - placed {len(buildings)} of {unit_count} buildings",
            density_achieved=round(len(buildings) / max(area_ha, 0.01), 1),
        )

    # -------------------------------------------------------------------------
    # Site-Wide Massing (all zones in one call)
    # -------------------------------------------------------------------------

    async def generate_site_massing_options(
        self,
        zones: list[dict[str, Any]],
        project_id: str,
        count: int = 3,
    ) -> SiteMassingResponse:
        """Generate *count* holistic site massing configurations for ALL zones.

        Each option varies heights, arrangements, number of buildings, density,
        and park/plaza design while respecting every zone's geometry and
        archetype selection.

        Parameters
        ----------
        zones : list[dict]
            Each dict must contain at minimum:
                id, zone_type, geometry (GeoJSON Polygon), properties (dict)
        project_id : str
        count : int  (default 3)
        """
        provider = self._resolve_provider()

        try:
            if provider == "claude" and settings.anthropic_api_key:
                return await self._generate_site_massing_with_claude(zones, project_id, count)
            elif provider == "gemini" and settings.gemini_api_key:
                return await self._generate_site_massing_with_gemini(zones, project_id, count)
        except Exception as e:
            logger.warning("AI site massing failed (%s): %s - using algorithmic fallback", provider, e)

        return self._generate_site_massing_algorithmic(zones, project_id, count)

    # -- Claude provider --

    async def _generate_site_massing_with_claude(
        self, zones: list[dict[str, Any]], project_id: str, count: int,
    ) -> SiteMassingResponse:
        prompt = self._build_site_massing_prompt(zones, count)
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=12000,
            system="You are an expert urban planner and massing designer. Return only valid JSON, no markdown fences or explanation outside JSON.",
            messages=[{"role": "user", "content": prompt}],
        )
        try:
            from app.core.usage_logger import log_api_usage_sync
            log_api_usage_sync(
                provider="anthropic",
                operation="site_massing",
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
            )
        except Exception:
            pass

        return self._parse_site_massing_response(message.content[0].text, zones, project_id, count)

    # -- Gemini provider --

    async def _generate_site_massing_with_gemini(
        self, zones: list[dict[str, Any]], project_id: str, count: int,
    ) -> SiteMassingResponse:
        prompt = self._build_site_massing_prompt(zones, count)
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
            log_api_usage_sync(
                provider="gemini",
                operation="site_massing",
                input_tokens=input_toks,
                output_tokens=output_toks,
            )
        except Exception as exc:
            logger.warning("Failed to log Gemini usage for site_massing: %s", exc)

        return self._parse_site_massing_response(response.text, zones, project_id, count)

    # -- Prompt builder --

    def _build_site_massing_prompt(
        self, zones: list[dict[str, Any]], count: int,
    ) -> str:
        """Build prompt describing ALL zones so the AI generates holistic site options."""

        # Determine a shared reference centroid (average of zone centroids)
        all_centroids = []
        for z in zones:
            poly = Polygon(z["geometry"]["coordinates"][0])
            all_centroids.append((poly.centroid.x, poly.centroid.y))
        ref_lon = sum(c[0] for c in all_centroids) / len(all_centroids)
        ref_lat = sum(c[1] for c in all_centroids) / len(all_centroids)
        mlon = _meters_per_deg_lon(ref_lat)

        zone_descriptions = []
        for z in zones:
            poly = Polygon(z["geometry"]["coordinates"][0])
            centroid = poly.centroid
            props = z.get("properties", {})
            zone_type = z.get("zone_type", "building")
            zone_id = z.get("id", "unknown")
            zone_label = props.get("label", "") or props.get("name", "") or z.get("name", "")

            bounds = poly.bounds
            width_m = abs(bounds[2] - bounds[0]) * mlon
            depth_m = abs(bounds[3] - bounds[1]) * METERS_PER_DEG_LAT
            area_m2 = poly.area * mlon * METERS_PER_DEG_LAT

            # Zone polygon in meters from *its own* centroid
            coords_m = []
            for x, y in poly.exterior.coords:
                coords_m.append([
                    round((x - centroid.x) * mlon, 1),
                    round((y - centroid.y) * METERS_PER_DEG_LAT, 1),
                ])

            # Centroid offset from site reference in meters
            cx_m = round((centroid.x - ref_lon) * mlon, 1)
            cy_m = round((centroid.y - ref_lat) * METERS_PER_DEG_LAT, 1)

            # Gather properties
            dev_type = props.get("development_type", zone_type)
            aesthetic = props.get("development_aesthetic", "")
            height = props.get("height")
            floors = props.get("floors")
            archetype_image = props.get("archetype_image", "")
            gen_style = props.get("generation_style_input", {})
            if isinstance(gen_style, dict):
                style_prompt = gen_style.get("prompt", "")
            else:
                style_prompt = ""
            description_text = props.get("description_text", "")
            unit_count = props.get("unit_count")

            extras = []
            if aesthetic:
                extras.append(f"  Aesthetic: {aesthetic}")
            if height:
                extras.append(f"  Max height: {height}m")
            if floors:
                extras.append(f"  Floors: {floors}")
            if unit_count:
                extras.append(f"  Target units: {unit_count}")
            if description_text:
                extras.append(f'  Description: "{description_text}"')
            if style_prompt:
                extras.append(f'  Style: "{style_prompt}"')
            if archetype_image:
                extras.append(f"  Archetype image selected: yes")

            extras_text = chr(10).join(extras) if extras else "  (no extra properties)"

            zone_descriptions.append(f"""### Zone "{zone_label or zone_id}" (id={zone_id})
- Type: {dev_type}
- Centroid offset from site center: ({cx_m}, {cy_m}) meters
- Dimensions: {width_m:.0f}m x {depth_m:.0f}m ({area_m2:.0f} sq m)
- Polygon (meters from zone centroid): {json.dumps(coords_m)}
{extras_text}""")

        zones_text = chr(10).join(zone_descriptions)

        prompt = f"""You are a senior computational urban designer.
Generate {count} DIFFERENT holistic site massing configurations for a development site.
Each option should vary building heights, arrangement, number of buildings, density, and park/plaza design.
All options must respect every zone's geometry and intended use.

## Site Reference Point
- Site center: ({ref_lon:.8f}, {ref_lat:.8f})
- 1 meter east/west = {_m_to_deg_lon(1, ref_lat):.10f} degrees longitude
- 1 meter north/south = {_m_to_deg_lat(1):.10f} degrees latitude

## Zones on Site
{zones_text}

## Design Guidelines
- For building/residential/development zones: place building massing blocks (rectangular footprints with heights)
- For green_space/park zones: define green_spaces with descriptive space_type (civic_green, park, playground, garden, meadow)
- For road zones: define road centerlines with width
- For parking/plaza zones: define a mix of hardscape green_spaces and optional small structures
- Buildings must stay within their zone polygon
- Building positions are DEGREE OFFSETS from that zone's centroid (not the site center)
- Vary each option meaningfully:
  - Option 1: Dense urban — taller buildings, compact arrangement, maximise floor area
  - Option 2: Balanced — medium heights, good mix of open space and buildings
  - Option 3: Low-density campus — shorter buildings, generous spacing, more landscape
- Maintain minimum 3m gaps between buildings
- Each building needs: center_x, center_y (degree offsets from zone centroid), width_m, depth_m, rotation_deg, height_m, building_type
- For building heights use realistic values: townhouses 8-12m, mid-rise 12-25m, high-rise 30-80m

## Required JSON Response
Return ONLY a JSON array of {count} option objects:
[
  {{
    "option_index": 0,
    "option_label": "<human readable label>",
    "reasoning": "<brief explanation of the design approach>",
    "total_building_count": <int>,
    "total_floor_area_m2": <float>,
    "density_achieved": <float: buildings per hectare>,
    "zones": [
      {{
        "zone_id": "<matching zone id>",
        "zone_type": "<zone_type>",
        "zone_label": "<zone label>",
        "buildings": [
          {{
            "center_x": <float: longitude offset from zone centroid>,
            "center_y": <float: latitude offset from zone centroid>,
            "width_m": <float>, "depth_m": <float>,
            "rotation_deg": <float>,
            "height_m": <float>,
            "building_type": "<residential|commercial|mixed_use|retail|civic>"
          }}
        ],
        "roads": [
          {{ "centerline": [[<x_deg>, <y_deg>], ...], "width_m": 6.0, "road_type": "local" }}
        ],
        "green_spaces": [
          {{ "polygon": [[<x_deg>, <y_deg>], ...], "space_type": "<civic_green|courtyard|park|garden>" }}
        ]
      }}
    ]
  }}
]"""
        return prompt

    # -- Response parser --

    def _parse_site_massing_response(
        self,
        text: str,
        zones: list[dict[str, Any]],
        project_id: str,
        count: int,
    ) -> SiteMassingResponse:
        """Parse AI JSON response into SiteMassingResponse."""
        text = text.strip()
        # Strip markdown fences (```json ... ``` or ```JSON ... ```)
        if text.startswith("```"):
            text = text.split(chr(10), 1)[1]
            text = text.rsplit("```", 1)[0]
            text = text.strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            logger.error("Site massing AI response JSON parse error: %s\nRaw text (first 500 chars): %s", e, text[:500])
            raise RuntimeError(f"AI returned invalid JSON for site massing: {e}") from e

        if isinstance(data, dict):
            # Might be wrapped: {"options": [...]}
            data = data.get("options", [data])

        # Build zone polygon lookup for validation
        zone_polys: dict[str, Polygon] = {}
        for z in zones:
            zone_polys[z["id"]] = Polygon(z["geometry"]["coordinates"][0])

        options: list[SiteMassingOption] = []
        for idx, item in enumerate(data[:count]):
            massing_zones: list[SiteMassingZone] = []
            total_buildings = 0

            for zone_data in item.get("zones", []):
                zone_id = zone_data.get("zone_id", "")
                zone_poly = zone_polys.get(zone_id)

                # Validate buildings are inside zone
                valid_buildings: list[LayoutBuilding] = []
                for b in zone_data.get("buildings", []):
                    # Default height to 15m if AI omits it (useless for massing without height)
                    raw_height = b.get("height_m")
                    height_m = float(raw_height) if raw_height is not None else 15.0

                    bldg = LayoutBuilding(
                        center_x=b.get("center_x", 0),
                        center_y=b.get("center_y", 0),
                        width_m=b.get("width_m", 10),
                        depth_m=b.get("depth_m", 10),
                        rotation_deg=b.get("rotation_deg", 0),
                        height_m=height_m,
                        building_type=b.get("building_type", "residential"),
                    )
                    if zone_poly:
                        centroid = zone_poly.centroid
                        pt = Point(centroid.x + bldg.center_x, centroid.y + bldg.center_y)
                        if zone_poly.contains(pt) or zone_poly.distance(pt) < 0.00001:
                            valid_buildings.append(bldg)
                        else:
                            logger.warning(
                                "Site massing option %d zone %s: building at (%f,%f) outside zone",
                                idx, zone_id, bldg.center_x, bldg.center_y,
                            )
                    else:
                        valid_buildings.append(bldg)

                roads = [
                    LayoutRoad(
                        centerline=r.get("centerline", []),
                        width_m=r.get("width_m", 6.0),
                        road_type=r.get("road_type", "local"),
                    )
                    for r in zone_data.get("roads", [])
                ]
                green_spaces = [
                    LayoutGreenSpace(
                        polygon=g.get("polygon", []),
                        space_type=g.get("space_type", "civic_green"),
                    )
                    for g in zone_data.get("green_spaces", [])
                ]

                total_buildings += len(valid_buildings)
                massing_zones.append(SiteMassingZone(
                    zone_id=zone_id,
                    zone_type=zone_data.get("zone_type", ""),
                    zone_label=zone_data.get("zone_label", ""),
                    buildings=valid_buildings,
                    roads=roads,
                    green_spaces=green_spaces,
                ))

            # Always use the computed building count (AI may hallucinate numbers)
            options.append(SiteMassingOption(
                option_index=idx,
                option_label=item.get("option_label", f"Option {idx + 1}"),
                zones=massing_zones,
                reasoning=item.get("reasoning", ""),
                total_building_count=total_buildings,
                total_floor_area_m2=item.get("total_floor_area_m2"),
                density_achieved=item.get("density_achieved"),
            ))

        return SiteMassingResponse(project_id=project_id, options=options)

    # -- Algorithmic fallback --

    def _generate_site_massing_algorithmic(
        self,
        zones: list[dict[str, Any]],
        project_id: str,
        count: int = 3,
    ) -> SiteMassingResponse:
        """Simple algorithmic fallback: grid-fill each building zone with 3 density levels."""
        density_configs = [
            {"label": "Dense Urban", "height_range": (30, 60), "spacing_factor": 1.0},
            {"label": "Balanced Mix", "height_range": (15, 30), "spacing_factor": 1.3},
            {"label": "Low-Rise Campus", "height_range": (8, 15), "spacing_factor": 1.8},
        ]

        options: list[SiteMassingOption] = []
        for opt_idx in range(count):
            cfg = density_configs[opt_idx % len(density_configs)]
            massing_zones: list[SiteMassingZone] = []
            total_buildings = 0

            for z in zones:
                zone_type = z.get("zone_type", "building")
                zone_id = z.get("id", "unknown")
                props = z.get("properties", {})
                zone_label = props.get("label", "") or props.get("name", "") or z.get("name", "")
                poly = Polygon(z["geometry"]["coordinates"][0])
                centroid = poly.centroid
                center_lat = centroid.y
                mlon = _meters_per_deg_lon(center_lat)

                if zone_type in ("green_space", "park", "water", "parking"):
                    # Green space, park, water, parking → define as landscape/hardscape polygon
                    gs_coords = [
                        [round(x - centroid.x, 10), round(y - centroid.y, 10)]
                        for x, y in poly.exterior.coords
                    ]
                    space_type = "parking_plaza" if zone_type == "parking" else "park"
                    massing_zones.append(SiteMassingZone(
                        zone_id=zone_id,
                        zone_type=zone_type,
                        zone_label=zone_label,
                        green_spaces=[LayoutGreenSpace(polygon=gs_coords, space_type=space_type)],
                    ))
                    continue

                if zone_type == "road":
                    # Simple road centerline through zone
                    bounds = poly.bounds
                    mid_y = (bounds[1] + bounds[3]) / 2
                    road_cl = [
                        [bounds[0] - centroid.x, mid_y - centroid.y],
                        [bounds[2] - centroid.x, mid_y - centroid.y],
                    ]
                    massing_zones.append(SiteMassingZone(
                        zone_id=zone_id,
                        zone_type=zone_type,
                        zone_label=zone_label,
                        roads=[LayoutRoad(centerline=road_cl, width_m=8.0, road_type="local")],
                    ))
                    continue

                # Building zones: grid-fill
                bounds = poly.bounds
                width_m_zone = abs(bounds[2] - bounds[0]) * mlon
                depth_m_zone = abs(bounds[3] - bounds[1]) * METERS_PER_DEG_LAT

                bldg_w = 20.0
                bldg_d = 16.0
                spacing = (bldg_w + 6) * cfg["spacing_factor"]
                height_lo, height_hi = cfg["height_range"]

                buildings: list[LayoutBuilding] = []
                nx = max(1, int(width_m_zone / spacing))
                ny = max(1, int(depth_m_zone / spacing))

                for ix in range(nx):
                    for iy in range(ny):
                        fx = (ix + 0.5) / nx
                        fy = (iy + 0.5) / ny
                        # Position in degrees offset from centroid
                        px_deg = (bounds[0] + fx * (bounds[2] - bounds[0])) - centroid.x
                        py_deg = (bounds[1] + fy * (bounds[3] - bounds[1])) - centroid.y

                        pt = Point(centroid.x + px_deg, centroid.y + py_deg)
                        if not poly.contains(pt):
                            continue

                        h = height_lo + (height_hi - height_lo) * ((ix + iy) % 3) / 2
                        buildings.append(LayoutBuilding(
                            center_x=px_deg,
                            center_y=py_deg,
                            width_m=bldg_w,
                            depth_m=bldg_d,
                            rotation_deg=0,
                            height_m=round(h, 1),
                            building_type=props.get("development_type", "residential"),
                        ))

                total_buildings += len(buildings)
                massing_zones.append(SiteMassingZone(
                    zone_id=zone_id,
                    zone_type=zone_type,
                    zone_label=zone_label,
                    buildings=buildings,
                ))

            options.append(SiteMassingOption(
                option_index=opt_idx,
                option_label=cfg["label"],
                zones=massing_zones,
                reasoning=f"Algorithmic {cfg['label'].lower()} layout with heights {cfg['height_range'][0]}-{cfg['height_range'][1]}m",
                total_building_count=total_buildings,
            ))

        return SiteMassingResponse(project_id=project_id, options=options)

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

        district_mode = _zone_requires_district_fabric(zone_type, unit_count, properties)
        if district_mode:
            strategy_hint = "Construct a serviceable district fragment with perimeter-aligned buildings, an internal street or shared mews, hardscape around buildings, and at least one planted or civic anchor space. Do not leave major residual space undefined."
        elif dev_type in ("residential",) and unit_count <= 8:
            strategy_hint = "Arrange buildings in a clean cluster or court with shared hardscape and planted edges."
        elif dev_type in ("residential",) and unit_count <= 20:
            strategy_hint = "Arrange buildings in rows or a small block pattern with clear circulation and landscape structure."
        elif dev_type in ("residential",):
            strategy_hint = "Arrange buildings in a coherent block pattern with readable circulation and planted open space."
        elif dev_type in ("commercial", "mixed_use", "mixed-use", "mixed use"):
            strategy_hint = "Use edge-aligned building placement with service access, active frontage, and structured public realm."
        else:
            strategy_hint = "Use a realistic layout appropriate for the development type, with clear circulation and no undefined residual ground."

        neighbor_text = ""
        if neighbors:
            types = set(n.get("zone_type", "") for n in neighbors)
            if types:
                neighbor_text = f"\nSurrounding zone types: {', '.join(sorted(types))}"

        prompt = f"""You are a senior computational urban designer designing a realistic site layout.

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

## Urban Systems Rules
- Construct a coherent precinct or district fragment, not isolated buildings in empty space
- Never leave major white space. Residual land must become hardscape, landscape, water, or access geometry
- Align buildings to site edges or roads where possible; prefer disciplined orthogonal geometry and 90-degree increments unless the site clearly demands another angle
- Every building must be served by a realistic road, lane, shared street, or paved apron
- Keep all building positions INSIDE the zone polygon
- Position values are DEGREE OFFSETS from zone centroid ({centroid.x:.8f}, {centroid.y:.8f})

## Conversion Reference
- 1 meter east/west = {_m_to_deg_lon(1, center_lat):.10f} degrees longitude
- 1 meter north/south = {_m_to_deg_lat(1):.10f} degrees latitude

## Building Typology
Assign each building an appropriate `building_typology` from:
- `townhouse_row`: 5-7m wide, 10-14m deep, 2-3 floors — fine-grain residential
- `mid_rise_apartment`: 16-24m wide, 14-20m deep, 3-5 floors — standard residential block
- `apartment_block`: 20-30m wide, 16-22m deep, 4-6 floors — larger residential
- `mixed_use_podium`: 18-28m wide, 16-24m deep, 4-8 floors — retail ground floor + residential above
- `retail_liner`: 8-14m wide, 12-16m deep, 1-3 floors — shopfront buildings
- `office_block`: 20-35m wide, 18-28m deep, 4-10 floors — commercial office

Group buildings into blocks using `block_id` (integer). Buildings in the same block share a street frontage and form a coherent cluster.

## Evaluation Criteria
- Every block must have street frontage on at least one side
- No building may be more than 50m from a road centerline
- The largest contiguous open space must be at least 400 sq m
- At least 2 different building typologies must be used for zones with 8+ units
- Building footprints must not overlap each other (minimum 3m separation)

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
      "building_type": "<residential|commercial|mixed_use|retail|civic|institutional>",
      "building_typology": "<townhouse_row|mid_rise_apartment|apartment_block|mixed_use_podium|retail_liner|office_block>",
      "block_id": <int: which block this building belongs to>,
      "setback_front_m": 3.0,
      "setback_side_m": 1.5
    }}
  ],
  "roads": [
    {{ "centerline": [[<x_deg>, <y_deg>], ...], "width_m": 6.0, "road_type": "local" }}
  ],
  "green_spaces": [
    {{ "polygon": [[<x_deg>, <y_deg>], ...], "space_type": "<civic_green|courtyard|entry_plaza|planted_verge|pocket_park>" }}
  ],
  "layout_strategy": "<strategy_name>",
  "reasoning": "<brief explanation of layout decisions>",
  "density_achieved": <float: units per hectare>
}}

## Worked Example (12-unit residential courtyard, ~80x60m zone)
{{
  "buildings": [
    {{"center_x": -0.00025, "center_y": 0.00018, "width_m": 6, "depth_m": 12, "rotation_deg": 0, "building_type": "residential", "building_typology": "townhouse_row", "block_id": 1, "setback_front_m": 3.0, "setback_side_m": 1.5}},
    {{"center_x": -0.00017, "center_y": 0.00018, "width_m": 6, "depth_m": 12, "rotation_deg": 0, "building_type": "residential", "building_typology": "townhouse_row", "block_id": 1, "setback_front_m": 3.0, "setback_side_m": 1.5}},
    {{"center_x": -0.00009, "center_y": 0.00018, "width_m": 6, "depth_m": 12, "rotation_deg": 0, "building_type": "residential", "building_typology": "townhouse_row", "block_id": 1, "setback_front_m": 3.0, "setback_side_m": 1.5}},
    {{"center_x": -0.00001, "center_y": 0.00018, "width_m": 6, "depth_m": 12, "rotation_deg": 0, "building_type": "residential", "building_typology": "townhouse_row", "block_id": 1, "setback_front_m": 3.0, "setback_side_m": 1.5}},
    {{"center_x": 0.00020, "center_y": 0.00012, "width_m": 20, "depth_m": 16, "rotation_deg": 0, "building_type": "residential", "building_typology": "mid_rise_apartment", "block_id": 2, "setback_front_m": 4.0, "setback_side_m": 2.0}},
    {{"center_x": -0.00020, "center_y": -0.00012, "width_m": 22, "depth_m": 18, "rotation_deg": 0, "building_type": "mixed_use", "building_typology": "mixed_use_podium", "block_id": 3, "setback_front_m": 2.0, "setback_side_m": 1.5}},
    {{"center_x": 0.00015, "center_y": -0.00015, "width_m": 10, "depth_m": 14, "rotation_deg": 0, "building_type": "retail", "building_typology": "retail_liner", "block_id": 3, "setback_front_m": 1.0, "setback_side_m": 1.5}}
  ],
  "roads": [
    {{"centerline": [[-0.00035, 0.0], [0.00035, 0.0]], "width_m": 8.0, "road_type": "collector"}},
    {{"centerline": [[0.0, -0.00025], [0.0, 0.00025]], "width_m": 6.0, "road_type": "local"}}
  ],
  "green_spaces": [
    {{"polygon": [[-0.00008, 0.00005], [0.00008, 0.00005], [0.00008, 0.00015], [-0.00008, 0.00015]], "space_type": "courtyard"}},
    {{"polygon": [[0.00025, -0.00020], [0.00035, -0.00020], [0.00035, -0.00005], [0.00025, -0.00005]], "space_type": "pocket_park"}}
  ],
  "layout_strategy": "perimeter_courtyard",
  "reasoning": "Townhouse row along north edge creates street wall. Mid-rise apartment anchors east block. Mixed-use podium with retail liner activates south frontage. Central courtyard provides shared amenity space.",
  "density_achieved": 25.0
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
        if text.startswith("```"):
            text = text.split(chr(10), 1)[1]
            text = text.rsplit("```", 1)[0]

        data = json.loads(text)

        if isinstance(data, list):
            data = data[0]

        layout = SiteLayoutResponse(**data)

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
        """Algorithmic layout using block-based approach for district zones,
        grid placement for simpler zones.
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

        if _zone_requires_district_fabric(zone_type, unit_count, properties):
            return _generate_block_layout(
                zone_polygon, zone_type, unit_count, properties,
                orientation_rad, "perimeter_courtyard", seed=42,
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

        prompt = f"""Generate a photoreal orthographic aerial district-fragment view of a proposed {dev_type} development.

Site: {width_m:.0f}m wide x {depth_m:.0f}m deep
Layout: {option.layout_strategy}
Aesthetic: {aesthetic or 'contextual mixed-use urban'}

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
- True top-down orthographic aerial perspective with no eye-level or facade views
- Photoreal architectural rendering quality - this must read like a premium district visualization, not a diagram or watercolor
- Real materials and ground plane detail: roof membranes and equipment, asphalt and curb geometry, sidewalks, planted edges, paving, parking logic, and readable tree canopies
- Buildings must feel anchored to streets, hardscape, and open space; no floating blocks and no blank residual site filler
- Surrounding context should remain visible and believable at the edges so the proposal aligns with real roads, houses, and landscape
- Use one coherent daylight system with crisp but realistic shadows
- No labels, no annotations, no text overlays, no colored zones - pure image output only
"""

        from google import genai

        model_name = _gemini_2d_image_model()
        logger.info("Generating layout preview image with Gemini model: %s", model_name)
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=model_name,
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


    def _site_preview_view_bounds(
        self,
        boundary_polygon: Polygon,
        reference_context: Optional[dict[str, Any]],
        engine_result: Optional[dict[str, Any]],
    ) -> tuple[float, float, float, float]:
        xs: list[float] = []
        ys: list[float] = []

        def _extend_coords(coords: list[list[float]] | None) -> None:
            if not coords:
                return
            for lon, lat in coords:
                xs.append(float(lon))
                ys.append(float(lat))

        _extend_coords([[float(x), float(y)] for x, y in boundary_polygon.exterior.coords])

        for feature in (reference_context or {}).get("roads", []):
            _extend_coords(feature.get("coordinates"))
        for key in ("buildings", "water", "parks"):
            for feature in (reference_context or {}).get(key, []):
                _extend_coords(feature.get("coordinates"))
        for key in ("right_of_way_polygons", "developable_blocks"):
            for feature in (engine_result or {}).get(key, []):
                _extend_coords(feature.get("coordinates"))

        if not xs or not ys:
            minx, miny, maxx, maxy = boundary_polygon.bounds
        else:
            minx, miny, maxx, maxy = min(xs), min(ys), max(xs), max(ys)

        pad_x = max((maxx - minx) * 0.08, 0.00012)
        pad_y = max((maxy - miny) * 0.08, 0.00012)
        return minx - pad_x, miny - pad_y, maxx + pad_x, maxy + pad_y


    def _site_preview_point_to_pixel(
        self,
        lon: float,
        lat: float,
        view_bounds: tuple[float, float, float, float],
        image_width: int,
        image_height: int,
        margin: int = 36,
    ) -> tuple[float, float]:
        minx, miny, maxx, maxy = view_bounds
        drawable_w = max(image_width - margin * 2, 1)
        drawable_h = max(image_height - margin * 2, 1)
        span_x = max(maxx - minx, 1e-9)
        span_y = max(maxy - miny, 1e-9)
        scale = min(drawable_w / span_x, drawable_h / span_y)
        used_w = span_x * scale
        used_h = span_y * scale
        offset_x = margin + (drawable_w - used_w) / 2.0
        offset_y = margin + (drawable_h - used_h) / 2.0
        px = offset_x + (lon - minx) * scale
        py = offset_y + (maxy - lat) * scale
        return px, py


    def _site_preview_meters_per_pixel(
        self,
        view_bounds: tuple[float, float, float, float],
        image_width: int,
        image_height: int,
        center_lat: float,
        margin: int = 36,
    ) -> float:
        minx, miny, maxx, maxy = view_bounds
        drawable_w = max(image_width - margin * 2, 1)
        drawable_h = max(image_height - margin * 2, 1)
        width_m = abs(maxx - minx) * _meters_per_deg_lon(center_lat)
        height_m = abs(maxy - miny) * METERS_PER_DEG_LAT
        return max(width_m / drawable_w, height_m / drawable_h, 0.25)


    def _site_preview_draw_polygon(
        self,
        draw: ImageDraw.ImageDraw,
        polygon: Polygon,
        view_bounds: tuple[float, float, float, float],
        image_width: int,
        image_height: int,
        *,
        fill: tuple[int, int, int, int],
        outline: tuple[int, int, int, int] | None = None,
        line_width: int = 1,
    ) -> None:
        if polygon.is_empty:
            return
        coords = [
            self._site_preview_point_to_pixel(float(x), float(y), view_bounds, image_width, image_height)
            for x, y in polygon.exterior.coords
        ]
        if len(coords) < 3:
            return
        draw.polygon(coords, fill=fill, outline=outline)
        if outline is not None and line_width > 1:
            draw.line(coords, fill=outline, width=line_width)


    def _site_preview_draw_line(
        self,
        draw: ImageDraw.ImageDraw,
        line: LineString,
        view_bounds: tuple[float, float, float, float],
        image_width: int,
        image_height: int,
        *,
        fill: tuple[int, int, int, int],
        line_width: int = 1,
    ) -> None:
        if line.is_empty:
            return
        coords = [
            self._site_preview_point_to_pixel(float(x), float(y), view_bounds, image_width, image_height)
            for x, y in line.coords
        ]
        if len(coords) < 2:
            return
        draw.line(coords, fill=fill, width=line_width, joint="curve")


    def _absolute_layout_building_polygon(self, zone_shape: Polygon, building: LayoutBuilding) -> Polygon | None:
        centroid = zone_shape.centroid
        cx = float(centroid.x + float(getattr(building, "center_x", 0.0) or 0.0))
        cy = float(centroid.y + float(getattr(building, "center_y", 0.0) or 0.0))
        half_w = _m_to_deg_lon(float(building.width_m) / 2.0, cy)
        half_d = _m_to_deg_lat(float(building.depth_m) / 2.0)
        polygon = Polygon([
            (cx - half_w, cy - half_d),
            (cx + half_w, cy - half_d),
            (cx + half_w, cy + half_d),
            (cx - half_w, cy + half_d),
            (cx - half_w, cy - half_d),
        ])
        if float(getattr(building, "rotation_deg", 0.0) or 0.0):
            polygon = rotate(polygon, float(building.rotation_deg), origin=(cx, cy), use_radians=False)
        clipped = polygon.intersection(zone_shape)
        if clipped.is_empty or clipped.geom_type != "Polygon":
            return None
        return clipped


    def _absolute_layout_road_geometry(self, zone_shape: Polygon, road: LayoutRoad) -> LineString | None:
        centroid = zone_shape.centroid
        coords = [
            (float(centroid.x + float(point[0])), float(centroid.y + float(point[1])))
            for point in ((getattr(road, "centerline", None) or []))
            if len(point) >= 2
        ]
        if len(coords) < 2:
            return None
        clipped = LineString(coords).intersection(zone_shape)
        if clipped.is_empty or clipped.geom_type != "LineString":
            return None
        return clipped


    def _absolute_layout_green_polygon(self, zone_shape: Polygon, green_space: LayoutGreenSpace) -> Polygon | None:
        centroid = zone_shape.centroid
        coords = [
            (float(centroid.x + float(point[0])), float(centroid.y + float(point[1])))
            for point in ((getattr(green_space, "polygon", None) or []))
            if len(point) >= 2
        ]
        if len(coords) < 3:
            return None
        polygon = Polygon(coords)
        clipped = polygon.intersection(zone_shape)
        if clipped.is_empty or clipped.geom_type != "Polygon":
            return None
        return clipped


    async def _build_site_preview_geometry_guide(
        self,
        boundary_polygon: Polygon,
        zone_layouts: list[dict[str, Any]],
        non_buildable_zones: list[dict[str, Any]],
        reference_context: Optional[dict[str, Any]] = None,
        buildable_without_layouts: Optional[list[dict[str, Any]]] = None,
    ) -> bytes:
        engine = RealWorldSiteEngine()
        try:
            engine_result = await engine.extract_developable_blocks(
                boundary_polygon,
                osm_context=reference_context,
                buffer_m=float((reference_context or {}).get("buffer_m") or 50),
            )
        except Exception as exc:
            logger.warning("Failed to derive site-engine blocks for preview guide: %s", exc)
            engine_result = {"right_of_way_polygons": [], "developable_blocks": []}

        image_width = 1024
        image_height = 1024
        view_bounds = self._site_preview_view_bounds(boundary_polygon, reference_context, engine_result)
        center_lat = boundary_polygon.centroid.y
        meters_per_pixel = self._site_preview_meters_per_pixel(view_bounds, image_width, image_height, center_lat)

        image = Image.new("RGBA", (image_width, image_height), (245, 243, 238, 255))
        draw = ImageDraw.Draw(image, "RGBA")

        context = reference_context or {}
        for feature in context.get("parks", []):
            coords = feature.get("coordinates") or []
            if len(coords) >= 3:
                self._site_preview_draw_polygon(draw, Polygon(coords), view_bounds, image_width, image_height, fill=(191, 208, 183, 255))
        for feature in context.get("water", []):
            coords = feature.get("coordinates") or []
            if len(coords) >= 3:
                self._site_preview_draw_polygon(draw, Polygon(coords), view_bounds, image_width, image_height, fill=(149, 176, 194, 255))
        for feature in context.get("buildings", []):
            coords = feature.get("coordinates") or []
            if len(coords) >= 3:
                self._site_preview_draw_polygon(draw, Polygon(coords), view_bounds, image_width, image_height, fill=(188, 190, 191, 220), outline=(168, 171, 173, 255))
        for feature in context.get("roads", []):
            coords = feature.get("coordinates") or []
            if len(coords) >= 2:
                width_px = max(2, int(round(float(feature.get("width_m") or 6.0) / meters_per_pixel)))
                self._site_preview_draw_line(draw, LineString(coords), view_bounds, image_width, image_height, fill=(196, 196, 192, 255), line_width=width_px)

        self._site_preview_draw_polygon(draw, boundary_polygon, view_bounds, image_width, image_height, fill=(236, 232, 224, 80), outline=(211, 205, 191, 255), line_width=3)

        for row in engine_result.get("right_of_way_polygons", []):
            coords = row.get("coordinates") or []
            if len(coords) >= 3:
                self._site_preview_draw_polygon(draw, Polygon(coords), view_bounds, image_width, image_height, fill=(205, 206, 203, 210), outline=(184, 186, 183, 255), line_width=2)
        for block in engine_result.get("developable_blocks", []):
            coords = block.get("coordinates") or []
            if len(coords) >= 3:
                self._site_preview_draw_polygon(draw, Polygon(coords), view_bounds, image_width, image_height, fill=(233, 227, 214, 150), outline=(218, 210, 194, 180))

        for entry in (buildable_without_layouts or []):
            shape = entry.get("shape")
            if isinstance(shape, Polygon):
                self._site_preview_draw_polygon(draw, shape, view_bounds, image_width, image_height, fill=(230, 225, 215, 165), outline=(209, 201, 184, 220), line_width=2)

        for zone in non_buildable_zones:
            shape = zone.get("shape")
            if not isinstance(shape, Polygon):
                continue
            zone_type = str(zone.get("zone_type") or "").lower()
            if zone_type == "road":
                self._site_preview_draw_polygon(draw, shape, view_bounds, image_width, image_height, fill=(175, 177, 176, 225), outline=(152, 154, 153, 255), line_width=2)
            elif zone_type == "green_space":
                self._site_preview_draw_polygon(draw, shape, view_bounds, image_width, image_height, fill=(157, 187, 140, 225), outline=(124, 153, 110, 255), line_width=2)
            elif zone_type == "water":
                self._site_preview_draw_polygon(draw, shape, view_bounds, image_width, image_height, fill=(118, 155, 176, 235), outline=(96, 132, 152, 255), line_width=2)
            elif zone_type == "parking":
                self._site_preview_draw_polygon(draw, shape, view_bounds, image_width, image_height, fill=(174, 176, 178, 225), outline=(148, 151, 153, 255), line_width=2)
            else:
                self._site_preview_draw_polygon(draw, shape, view_bounds, image_width, image_height, fill=(220, 216, 207, 170), outline=(196, 191, 181, 230), line_width=2)

        for zl in zone_layouts:
            shape = zl.get("shape")
            option = zl.get("option")
            if not isinstance(shape, Polygon) or option is None:
                continue
            self._site_preview_draw_polygon(draw, shape, view_bounds, image_width, image_height, fill=(237, 233, 224, 92), outline=(215, 207, 191, 180), line_width=2)

            for road in getattr(option, "roads", []) or []:
                geometry = self._absolute_layout_road_geometry(shape, road)
                if geometry is None:
                    continue
                width_px = max(2, int(round(float(getattr(road, "width_m", 6.0) or 6.0) / meters_per_pixel)))
                self._site_preview_draw_line(draw, geometry, view_bounds, image_width, image_height, fill=(130, 134, 138, 235), line_width=width_px)

            for green_space in getattr(option, "green_spaces", []) or []:
                geometry = self._absolute_layout_green_polygon(shape, green_space)
                if geometry is None:
                    continue
                space_type = str(getattr(green_space, "space_type", "") or "")
                fill = (146, 184, 127, 232)
                outline = (106, 141, 92, 255)
                if "pond" in space_type or "water" in space_type:
                    fill = (123, 163, 184, 240)
                    outline = (93, 131, 150, 255)
                self._site_preview_draw_polygon(draw, geometry, view_bounds, image_width, image_height, fill=fill, outline=outline, line_width=2)

            for building in getattr(option, "buildings", []) or []:
                geometry = self._absolute_layout_building_polygon(shape, building)
                if geometry is None:
                    continue
                self._site_preview_draw_polygon(draw, geometry, view_bounds, image_width, image_height, fill=(230, 233, 236, 255), outline=(142, 149, 155, 255), line_width=2)

        buffer = BytesIO()
        image.convert("RGB").save(buffer, format="PNG")
        return buffer.getvalue()

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
        """Generate a unified illustrative top-down master plan preview of the entire site."""
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
            dx_m = (shape_centroid.x - site_centroid.x) * mlon_val
            dy_m = (shape_centroid.y - site_centroid.y) * METERS_PER_DEG_LAT
            nx = dx_m / (site_w / 2) if site_w else 0
            ny = dy_m / (site_d / 2) if site_d else 0
            if ny > 0.3:
                v = "top"
            elif ny < -0.3:
                v = "bottom"
            else:
                v = "center"
            if nx > 0.3:
                h = "right"
            elif nx < -0.3:
                h = "left"
            else:
                h = "center"
            if v == "center" and h == "center":
                return "center of the site"
            if v == "center":
                return f"{h} side of the site"
            if h == "center":
                return f"{v} of the site"
            return f"{v}-{h} of the site"

        def _zone_badge(zone_name: str, zone_color: str, position: str, width_m: float, depth_m: float) -> str:
            color_name = _site_preview_color_name(zone_color) if zone_color else None
            if color_name and zone_color:
                return f"{zone_name} ({color_name} zone {zone_color}) at {position}, approximately {width_m:.0f}m x {depth_m:.0f}m"
            return f"{zone_name} at {position}, approximately {width_m:.0f}m x {depth_m:.0f}m"

        has_style_reference = False
        zone_descriptions: list[str] = []
        for zl in zone_layouts:
            zone = zl["zone"]
            shape = zl["shape"]
            option = zl["option"]
            props = zl["properties"] or {}
            zone_type = zone.zone_type
            zone_id = str(zone.id)
            meta = zone_meta.get(zone_id, {})
            zone_name = _site_preview_sanitize_text(meta.get("name")) or _site_preview_sanitize_text(zone.name) or zone_type.replace("_", " ")
            zone_color = _site_preview_sanitize_text(meta.get("color")) or ""
            dev_type = _site_preview_sanitize_text(props.get("development_type")) or ("residential" if zone_type == "residential" else "mixed use")
            aesthetic = _site_preview_sanitize_text(props.get("development_aesthetic")) or "contextual architectural"
            edge_material = _site_preview_sanitize_text(props.get("facade_material")) or ""
            roof = _site_preview_sanitize_text(props.get("roof_style")) or ""
            ground = _site_preview_sanitize_text(props.get("ground_texture")) or ""
            desc_text = _site_preview_sanitize_text(props.get("description_text")) or ""
            height = props.get("height")
            floors = props.get("floors")
            balconies = props.get("balconies", False)
            unit_count = props.get("unit_count")
            if props.get("reference_images"):
                has_style_reference = True
            if props.get("development_archetype_id") or props.get("development_archetype_label") or props.get("generation_style_input"):
                has_style_reference = True

            z_bounds = shape.bounds
            z_w = round(abs(z_bounds[2] - z_bounds[0]) * mlon, 1)
            z_d = round(abs(z_bounds[3] - z_bounds[1]) * METERS_PER_DEG_LAT, 1)
            position = _position_description(shape.centroid, centroid, site_width_m, site_depth_m, mlon)
            badge = _zone_badge(zone_name, zone_color, position, z_w, z_d)

            building_lines = []
            for building in option.buildings:
                btype = _site_preview_sanitize_text(getattr(building, "building_type", None)) or dev_type
                b_floors = getattr(building, "floors", None) or floors or props.get("floors", 2)
                b_height = getattr(building, "height_m", None) or height or (b_floors * 3.5)
                building_lines.append(
                    f"    - {btype}: roof/footprint about {float(getattr(building, 'width_m', 0) or 0):g}m x {float(getattr(building, 'depth_m', 0) or 0):g}m, {int(round(float(b_floors)))} floors ({float(b_height):.0f}m tall)"
                )

            road_lines = []
            for road in option.roads:
                road_type = _site_preview_sanitize_text(getattr(road, "road_type", None)) or "internal road"
                road_lines.append(f"    - {road_type}: {float(getattr(road, 'width_m', 0) or 0):g}m wide, render strictly in plan view")

            green_lines = []
            for green in option.green_spaces:
                space_type = _site_preview_sanitize_text(getattr(green, "space_type", None)) or "green space"
                green_lines.append(f"    - {space_type}: render as top-down landscape plan")

            style_parts = [f"Character: {aesthetic}"]
            if edge_material:
                style_parts.append(f"Material cue: {edge_material}")
            if roof:
                style_parts.append(f"Roof cue: {roof}")
            if ground:
                style_parts.append(f"Ground-plane cue: {ground}")
            if balconies:
                style_parts.append("Translate balconies into terrace and perimeter rhythm visible from above")
            if height:
                style_parts.append(f"Height: {height}m")
            if floors:
                style_parts.append(f"Floors: {floors}")
            if unit_count:
                style_parts.append(f"Units: {unit_count}")
            if has_style_reference:
                style_parts.append("Use archetype metadata only as plan-view cues for roof, planting, and paving")

            desc_block = f"\n    Critical design directive: {desc_text}" if desc_text else ""
            zone_block = f"""[Within {badge}]: Render the roof plan and building footprints for this {dev_type} precinct.
    Layout strategy: {_site_preview_sanitize_text(option.layout_strategy) or 'coherent block organization'}{desc_block}
    Plan-view character: {'; '.join(style_parts)}
    Building footprints ({len(option.buildings)}):
{chr(10).join(building_lines) if building_lines else '      (derive coherent footprints within the zone)'}
    Internal corridors ({len(option.roads)}):
{chr(10).join(road_lines) if road_lines else '      (none)'}
    Open-space cues ({len(option.green_spaces)}):
{chr(10).join(green_lines) if green_lines else '      (none)'}
    Keep all geometry clipped to the zone boundary and integrated into the unified ground plane."""
            zone_descriptions.append(zone_block)

        for entry in (buildable_without_layouts or []):
            zone = entry["zone"]
            shape = entry["shape"]
            props = entry["properties"] or {}
            zone_type = zone.zone_type
            zone_id = str(zone.id)
            meta = zone_meta.get(zone_id, {})
            zone_name = _site_preview_sanitize_text(meta.get("name")) or _site_preview_sanitize_text(zone.name) or zone_type.replace("_", " ")
            zone_color = _site_preview_sanitize_text(meta.get("color")) or ""
            if props.get("reference_images") or props.get("development_archetype_id") or props.get("development_archetype_label"):
                has_style_reference = True
            z_bounds = shape.bounds
            z_w = round(abs(z_bounds[2] - z_bounds[0]) * mlon, 1)
            z_d = round(abs(z_bounds[3] - z_bounds[1]) * METERS_PER_DEG_LAT, 1)
            position = _position_description(shape.centroid, centroid, site_width_m, site_depth_m, mlon)
            badge = _zone_badge(zone_name, zone_color, position, z_w, z_d)
            desc_text = _site_preview_sanitize_text(props.get("description_text")) or ""
            style_parts = []
            for value in [props.get("development_aesthetic"), props.get("facade_material"), props.get("roof_style"), props.get("ground_texture")]:
                text_value = _site_preview_sanitize_text(value)
                if text_value:
                    style_parts.append(text_value)
            zone_block = f"""[Within {badge}]: Render a top-down building precinct derived from the zone properties and user vision.
    Plan-view character: {'; '.join(style_parts) if style_parts else 'contextual roof and ground-plane logic only'}
    Critical design directive: {desc_text or 'derive coherent roof plans and footprints from the programmed massing'}
    No facade boards, no side views, and no inserted reference imagery."""
            zone_descriptions.append(zone_block)

        infra_lines: list[str] = []
        for nb in non_buildable_zones:
            zone_type = nb["zone_type"]
            props = nb["properties"] or {}
            zone_name = _site_preview_sanitize_text(nb.get("name")) or zone_type.replace("_", " ")
            shape = nb["shape"]
            if props.get("reference_images") or props.get("road_archetype_id") or props.get("green_space_archetype_id") or props.get("plaza_archetype_id"):
                has_style_reference = True
            position = _position_description(shape.centroid, centroid, site_width_m, site_depth_m, mlon)
            details = []
            if zone_type == "road":
                details.append(f"{float(props.get('width', 10) or 10):g}m wide")
                details.append(f"{int(props.get('lane_count', 2) or 2)} lanes")
                surface = _site_preview_sanitize_text(props.get("road_surface")) or "refined corridor paving"
                details.append(surface)
                sidewalks = _site_preview_sanitize_text(props.get("sidewalks"))
                if sidewalks and sidewalks != "none":
                    details.append(f"sidewalks: {sidewalks}")
                mobility_profile = _site_preview_sanitize_text(props.get("mobility_profile"))
                if mobility_profile:
                    details.append(f"movement hierarchy: {mobility_profile}")
            elif zone_type == "green_space":
                density = _site_preview_sanitize_text(props.get("tree_density_level")) or "layered canopy"
                details.append(density)
                if props.get("has_paths"):
                    details.append("paths")
                if props.get("has_benches"):
                    details.append("seating")
                for value in [props.get("green_space_aesthetic"), props.get("park_typology"), props.get("shade_strategy"), props.get("water_feature")]:
                    text_value = _site_preview_sanitize_text(value)
                    if text_value:
                        details.append(text_value)
            elif zone_type == "water":
                details.append(_site_preview_sanitize_text(props.get("water_type")) or "flat reflective water element")
            elif zone_type == "parking":
                for value in [props.get("parking_layout"), props.get("plaza_aesthetic"), props.get("paving_material"), props.get("shade_strategy"), props.get("plaza_program"), props.get("water_feature")]:
                    text_value = _site_preview_sanitize_text(value)
                    if text_value:
                        details.append(text_value)
                if props.get("covered"):
                    details.append("covered portions where appropriate")
            desc_text = _site_preview_sanitize_text(props.get("description_text")) or ""
            detail_text = ', '.join(details) if details else 'render strictly in plan view'
            desc_suffix = f" Critical design directive: {desc_text}." if desc_text else ""
            infra_lines.append(f"[Within {zone_name} ({zone_type}) at {position}]: Render this zone strictly in plan view using {detail_text}. Keep it clipped to the zone boundary and integrated into the continuous ground plane.{desc_suffix}")

        osm_text = ""
        if reference_context:
            osm_parts = []
            ref_roads = reference_context.get("roads", [])
            if ref_roads:
                road_types = sorted({str(item.get("road_type") or "residential") for item in ref_roads})
                road_names = [_site_preview_sanitize_text(item.get("name")) for item in ref_roads if item.get("name")]
                line = f"Muted surrounding roads: {len(ref_roads)} ({', '.join(road_types)})"
                if road_names:
                    line = f"{line}; nearby names include {', '.join(name for name in road_names[:5] if name)}"
                osm_parts.append(line)
            ref_buildings = reference_context.get("buildings", [])
            if ref_buildings:
                heights = [item.get("height_m") for item in ref_buildings if item.get("height_m")]
                avg_h = round(sum(heights) / len(heights), 1) if heights else None
                osm_parts.append(f"Muted surrounding buildings: {len(ref_buildings)}" + (f" (average {avg_h:g}m)" if avg_h else ""))
            if reference_context.get("water"):
                osm_parts.append(f"Nearby water bodies: {len(reference_context.get('water', []))}")
            if reference_context.get("parks"):
                osm_parts.append(f"Nearby parks: {len(reference_context.get('parks', []))}")
            if osm_parts:
                osm_text = "MUTED CONTEXT CUES:\n" + chr(10).join(f"  - {part}" for part in osm_parts)

        reference_hint_text = ""
        if has_style_reference:
            reference_hint_text = (
                "ARCHETYPE METADATA RULE:\n"
                "  - Translate selected archetype and precedent metadata into roof form, massing, planting, frontage rhythm, and paving cues only.\n"
                "  - Do not paste, reproduce, or collage any source imagery into the master plan.\n"
            )

        has_water = any(nb["zone_type"] == "water" for nb in non_buildable_zones) or bool((reference_context or {}).get("water"))
        has_parks = any(nb["zone_type"] == "green_space" for nb in non_buildable_zones) or any(getattr(zl["option"], "green_spaces", None) for zl in zone_layouts)
        design_guidance = build_site_preview_design_brief(
            has_water=has_water,
            has_parks=has_parks,
            has_reference_images=has_style_reference,
        )
        design_guidance_text = "MASTER PLAN DESIGN GUIDANCE:\n" + chr(10).join(f"  - {line}" for line in design_guidance)

        prompt = f"""{SITE_PLAN_PROMPT_BASELINE}

This is a single unified architectural site plan. Treat the entire site as one continuous sheet with one palette family, one light direction, one paper texture, and one shadow system.

The attached image is a synthetic geometry guide only. It contains vectorized context, street corridors, developable blocks, and proposed site geometry. Preserve that structure, but do not treat it as aerial photography or copy it as an image-within-image composition.

SITE: {site_width_m:.0f}m wide x {site_depth_m:.0f}m deep

ZONE DIRECTIVES:
{chr(10).join(zone_descriptions) if zone_descriptions else '(no buildable zones)'}

{chr(10).join(infra_lines) if infra_lines else ''}

{osm_text}
{reference_hint_text}
{design_guidance_text}

OUTPUT RULES:
- Render a photoreal orthographic district visualization, not an illustrative board and not a perspective hero shot
- Keep buildings as crisp roof plans and footprints, with believable roof detail and disciplined street-wall geometry
- Keep streets, parking, sidewalks, plazas, parks, and water entirely in plan view and integrated into one continuous ground plane
- Fill residual site space intentionally as hardscape, landscape, or water; no blank white or beige filler zones
- Keep the proposal aligned to real surrounding roads and neighboring houses while keeping context slightly subdued
- No labels, no legends, no pasted reference images, no floating boards, and no image-within-image compositions

{SITE_PLAN_NEGATIVE_CONSTRAINTS}
"""

        logger.info("=== GEMINI SITE PREVIEW PROMPT ===")
        logger.info(
            "Zones: %d with layouts, %d buildable without layouts, %d infrastructure, %d style-reference bundles",
            len(zone_layouts),
            len(buildable_without_layouts or []),
            len(non_buildable_zones),
            int(has_style_reference),
        )
        logger.info("Map screenshots: %s", "yes" if map_screenshots else "no")
        logger.info("Zone meta colors: %s", {m.get("name"): m.get("color") for m in zone_meta.values()} if zone_meta else "none")
        logger.info("Prompt length: %d chars", len(prompt))
        logger.info("Full prompt:\n%s", prompt)

        geometry_guide_bytes: bytes | None = None
        geometry_guide_source = "none"
        try:
            geometry_guide_bytes = await self._build_site_preview_geometry_guide(
                boundary_polygon,
                zone_layouts,
                non_buildable_zones,
                reference_context=reference_context,
                buildable_without_layouts=buildable_without_layouts,
            )
            geometry_guide_source = "site_engine_synthetic"
        except Exception as exc:
            logger.warning("Failed to build synthetic site preview guide: %s", exc)

        from google import genai

        contents = []
        if geometry_guide_bytes:
            contents.append(genai.types.Part.from_bytes(data=geometry_guide_bytes, mime_type="image/png"))
            contents.append("[Authoritative synthetic geometry guide only. Use this image to preserve the site footprint, street hierarchy, developable blocks, and zone arrangement. Do not reproduce aerial photography, map labels, raster basemap textures, or image-within-image artifacts in the final master plan.]")
        elif map_screenshots:
            geometry_key = "with_zones" if map_screenshots.get("with_zones") else "satellite"
            b64_str = map_screenshots.get(geometry_key, "")
            if b64_str:
                try:
                    if "," in b64_str:
                        header, b64_data = b64_str.split(",", 1)
                        mime = header.split(":")[1].split(";")[0] if ":" in header else "image/jpeg"
                    else:
                        b64_data = b64_str
                        mime = "image/jpeg"
                    img_bytes = base64.b64decode(b64_data)
                    contents.append(genai.types.Part.from_bytes(data=img_bytes, mime_type=mime))
                    contents.append("[Fallback geometry guide only. Preserve the site footprint and zone arrangement, but do not reproduce aerial photography, basemap labels, or raster textures in the final master plan.]")
                    geometry_guide_source = "map_screenshot_fallback"
                except Exception as exc:
                    logger.warning("Failed to decode fallback site geometry screenshot (%s): %s", geometry_key, exc)

        contents.append(prompt)
        image_parts = sum(1 for item in contents if hasattr(item, "inline_data") or (hasattr(item, "_raw_part") and hasattr(item._raw_part, "inline_data")))
        logger.info("Sending to Gemini: %d geometry guide image parts, source=%s, prompt %d chars", image_parts, geometry_guide_source, len(prompt))

        model_name = _gemini_2d_image_model()
        logger.info("Generating site preview image with Gemini model: %s", model_name)
        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model=model_name,
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
            f"text({len(part.text)})" if part.text else "inline_data" if part.inline_data else "other"
            for part in response.candidates[0].content.parts
        ]
        raise RuntimeError(f"Gemini did not return an image for site preview. Parts received: {part_types}")











