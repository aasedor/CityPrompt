"""Site finishing recipes and hard-clipped, inward-feathered ground artwork."""

from __future__ import annotations
import hashlib
import json
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from shapely.geometry import Polygon, Point, shape, mapping
from shapely.ops import unary_union
from shapely.affinity import scale
from app.services.site_engine import (
    WGS84_CRS,
    build_transformer,
    local_metric_crs_for_polygon,
    project_geometry,
)
from app.services.residual_landscape import (
    ResidualSourceZone,
    build_residual_landscape_recipe,
    residual_landscape_source_hash,
)

PRESETS = {"gardens", "natural", "urban"}
PALETTE = {
    "foundation_planting": "#647650",
    "boulevard_planting": "#758453",
    "perimeter_planting": "#5f7650",
    "lawn": "#78965c",
    "low_groundcover": "#879275",
    "meadow": "#95936c",
    "shared_paving": "#bbb5a8",
}


def context_hash(boundary, zones):
    # Includes routes, exact variants and terrain choices; excludes only our own output.
    def props(z):
        return {
            k: v
            for k, v in (z.properties or {}).items()
            if k not in {"community_3d_landscape", "community_3d_landscape_mode"}
        }

    from geoalchemy2.shape import to_shape

    value = [
        (
            str(z.id),
            to_shape(z.geometry).wkb_hex,
            getattr(z, "zone_type", None),
            props(z),
        )
        for z in [boundary, *zones]
    ]
    return hashlib.sha256(json.dumps(sorted(value), sort_keys=True, default=str).encode()).hexdigest()


def build_site_landscape(boundary, sources, corridors, preset, *, boundary_id, compiled_at):
    if preset not in PRESETS:
        raise ValueError("Choose a landscape preset")
    protected = [ResidualSourceZone(f"access-{i}", "access", Polygon(ring)) for i, ring in enumerate(corridors)]
    if any(not s.geometry.is_valid or s.geometry.is_empty for s in protected):
        raise ValueError("An access route is invalid; refresh the scene")
    recipe = build_residual_landscape_recipe(
        boundary,
        [*sources, *protected],
        boundary_id=boundary_id,
        compiled_at=compiled_at,
    )
    # Retain canonical physical-zone identity for the existing direct-render gate.
    # The signed preview separately binds the complete property/context snapshot.
    recipe["source_hash"] = residual_landscape_source_hash(boundary, sources)
    recipe["preset"] = preset
    for region in recipe["regions"]:
        if region["kind"] == "lawn" and preset == "natural":
            region["kind"] = "meadow"
        if region["kind"] in {"foundation_planting", "low_groundcover"} and preset == "urban":
            region["kind"] = "shared_paving"
    if preset == "urban":
        recipe["placements"] = recipe["placements"][::2]
    # Planting islands tie sparse trees to the ground rather than scattering
    # isolated trunks over one unbroken lawn. Clip to the same protected remainder.
    crs = local_metric_crs_for_polygon(boundary)
    to_metric = build_transformer(WGS84_CRS, crs)
    to_wgs = build_transformer(crs, WGS84_CRS)
    remainder = project_geometry(shape(recipe["geometry"]), to_metric)
    beds = []
    for i, tree in enumerate(recipe["placements"]):
        point = project_geometry(Point(tree["lng"], tree["lat"]), to_metric)
        radius = 4.0 if preset == "urban" else 5.5 + (i % 3)
        bed = scale(point.buffer(radius, resolution=10), xfact=1.25, yfact=0.85, origin=point)
        beds.append(bed.intersection(remainder))
    if beds:
        geometry = unary_union(beds).buffer(0)
        recipe["regions"].insert(
            0,
            {
                "id": "planted-groups",
                "kind": "perimeter_planting",
                "area_sqm": round(geometry.area, 2),
                "minimum_width_m": 0,
                "geometry": mapping(project_geometry(geometry, to_wgs)),
            },
        )
    return recipe


def draw_geometry(draw, geometry, bounds, fill, *, hole=0):
    west, south, east, north = bounds
    width, height = draw._image.size

    def points(ring):
        return [((x - west) / (east - west) * width, (north - y) / (north - south) * height) for x, y, *_ in ring]

    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    for rings in polygons:
        if not rings:
            continue
        draw.polygon(points(rings[0]), fill=fill)
        for ring in rings[1:]:
            draw.polygon(points(ring), fill=hole)


def landscape_images(boundary, recipe, size=768, *, base_surface=False):
    bounds = boundary.bounds
    dimensions = (size, size)
    if base_surface:
        # Keep metre proportions in the guide. A tall parcel stretched into a
        # square encourages the provider to redraw its geography.
        crs = local_metric_crs_for_polygon(boundary)
        metric = project_geometry(boundary, build_transformer(WGS84_CRS, crs))
        west, south, east, north = metric.bounds
        span = max(east - west, north - south)
        dimensions = (
            max(128, round(size * (east - west) / span)),
            max(128, round(size * (north - south) / span)),
        )
    mask = Image.new("L", dimensions, 0)
    draw_geometry(
        ImageDraw.Draw(mask),
        mapping(boundary) if base_surface else recipe["geometry"],
        bounds,
        255,
    )
    base = Image.new("RGB", dimensions, "#697f4a")
    for region in reversed(recipe["regions"]):
        layer = Image.new("L", dimensions, 0)
        draw_geometry(ImageDraw.Draw(layer), region["geometry"], bounds, 255)
        base.paste(PALETTE[region["kind"]], mask=layer)
    # Full-base artwork runs below authored objects: no grey object cutouts.
    # Legacy preset previews retain their protected remainder.
    guide = Image.new("RGB", dimensions, "#777777")
    guide.paste(base, mask=mask)
    return base, guide, mask


def clip_custom_art(image_bytes, mask, *, feather=True):
    image = Image.open(BytesIO(image_bytes)).convert("RGBA").resize(mask.size, Image.Resampling.LANCZOS)
    # Feather inward and intersect with the requested surface (parcel for a
    # full base, protected remainder for legacy artwork).
    inset = mask.filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(2)) if feather else mask
    # Provider outputs may contain transparent areas. Preserve that coverage so
    # missing artwork reveals the underlying ground instead of opaque black.
    image.putalpha(ImageChops.multiply(image.getchannel("A"), ImageChops.multiply(inset, mask)))
    return image


def blend_site_edges(image, mask, boundary, samples, *, width_m=6.0):
    """Blend ground colour into sampled adjacent tiles, never copy their objects.

    Only the inward edge band changes. The mesh still clips at the exact parcel;
    alpha fading through its masked-out Google tiles would reveal a blank hole.
    """
    import numpy as np
    from scipy.ndimage import distance_transform_edt, gaussian_filter

    west, south, east, north = boundary.bounds
    crs = local_metric_crs_for_polygon(boundary)
    metric = project_geometry(boundary, build_transformer(WGS84_CRS, crs))
    mw, ms, me, mn = metric.bounds
    width, height = image.size
    colors = np.zeros((height, width, 3), dtype=np.uint8)
    known = np.zeros((height, width), dtype=bool)
    for sample in samples:
        x = min(
            width - 1,
            max(0, round((sample["lng"] - west) / (east - west) * (width - 1))),
        )
        y = min(
            height - 1,
            max(0, round((north - sample["lat"]) / (north - south) * (height - 1))),
        )
        colors[y, x] = sample["color"]
        known[y, x] = True
    if not known.any():
        return image
    indices = distance_transform_edt(~known, return_distances=False, return_indices=True)
    edge_colors = colors[indices[0], indices[1]].astype(float)
    edge_colors = gaussian_filter(edge_colors, sigma=(2, 2, 0))
    distance = distance_transform_edt(
        np.pad(np.asarray(mask) > 0, 1),
        sampling=((mn - ms) / height, (me - mw) / width),
    )[1:-1, 1:-1]
    mix = np.clip(distance / width_m, 0, 1)
    mix = (mix * mix * (3 - 2 * mix))[..., None]
    pixels = np.array(image)
    pixels[..., :3] = np.round(pixels[..., :3] * mix + edge_colors * (1 - mix)).astype(np.uint8)
    return Image.fromarray(pixels)


def png_bytes(image):
    stream = BytesIO()
    image.save(stream, format="PNG")
    return stream.getvalue()


def normalize_scene_reference(value):
    """Bounded uploaded pixels only; never fetch a user-provided URL."""
    import base64

    try:
        encoded = value.split(",", 1)[1] if value.startswith("data:image/") else value
        raw = base64.b64decode(encoded, validate=True)
        with Image.open(BytesIO(raw)) as image:
            if min(image.size) < 64 or image.width * image.height > 16_000_000:
                raise ValueError("Invalid context image dimensions")
            image = image.convert("RGB")
            image.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
            return base64.b64encode(png_bytes(image)).decode()
    except Exception as exc:
        raise ValueError("The neighbourhood reference could not be read. Capture the site again.") from exc


def site_landscape_prompt(boundary, zones, preset, brief):
    from collections import Counter
    from app.services.residual_landscape import community_3d_kind_for_source

    counts = Counter(community_3d_kind_for_source(z.zone_type, z.properties) or z.zone_type for z in zones)
    crs = local_metric_crs_for_polygon(boundary)
    metric = project_geometry(boundary, build_transformer(WGS84_CRS, crs))
    west, south, east, north = metric.bounds
    return (
        "Create one continuous realistic north-up landscape ground texture, viewed exactly vertically. "
        f"The parcel is approximately {east-west:.0f} by {north-south:.0f} metres. "
        f"The 3D development above this ground contains {json.dumps(dict(sorted(counts.items())))}. "
        "Image 1 fixes the parcel shape, proportions and extent. Its green and brown areas are only a starting ground palette. "
        "Fill the entire parcel with continuous ground, including the areas underneath future objects. No interior cutouts. "
        "The NEIGHBOURHOOD APPEARANCE REFERENCE shows the same proposed development and surrounding Google tiles. "
        "Fit the landscape to the buildings, parks and streets already designed AND to the neighbouring landscape. "
        "Use compatible paving hues, restrained grass colours, planting character and believable material scale. "
        "Carry adjacent street-edge and planting character gently into the parcel's edges; avoid a hard decorative carpet. "
        "Use the surrounding tiles as evidence of local character, not a requirement to copy construction rubble, "
        "photogrammetry defects, baked shadows or the temporary empty-site lawn. "
        f"Landscape character: {preset}. Student brief: {brief.strip()}\n"
        "OUTPUT CONSTRAINTS: This image will be the base UNDER existing 3D buildings, streets and parks. "
        "Those objects are rendered separately above it; do not draw them in this image. "
        "Output only the original Image 1 parcel extent and proportions, north-up and flat. "
        "Do not adopt the reference image's camera or larger neighbourhood extent. No text, labels, perspective, "
        "buildings, roofs, grey footprints, roads, sidewalks, park layouts, furniture, large trees or cast shadows. "
        "Use lawn, soil, low groundcover, modest paving accents and garden beds. Keep grass continuous under all objects. "
        "Do not copy the development from the neighbourhood reference, and do not paint outside the parcel. "
        "Treat water/pool requests as flat surface concepts; do not invent depth or structures."
    )
