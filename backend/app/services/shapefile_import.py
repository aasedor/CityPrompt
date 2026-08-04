"""Parse a zipped ESRI Shapefile and reproject features to WGS84 (EPSG:4326).

Backs the "Upload Shapefile" feature in the globe view: it turns a georeferenced
vector file into site-zone polygons that drop onto the Google Photorealistic
3D Tiles environment.

Design notes
------------
- Pure function (no FastAPI / DB coupling) so it stays unit-testable.
- Reprojection is the critical step. Shapefiles are usually in a *projected* CRS
  (UTM, State Plane, a municipal grid) declared by the ``.prj`` sidecar. We read
  that CRS and transform every coordinate to lon/lat. ``always_xy=True`` is
  REQUIRED so pyproj returns ``(lon, lat)`` rather than the authority ``(lat,
  lon)`` axis order — getting this wrong silently swaps the globe placement.
- Every shapefile geometry type becomes a polygon zone (the SiteZone model is
  polygon-only):
    * Polygons / MultiPolygons -> area zones (holes dropped, parts exploded).
    * Closed polylines         -> filled area zones (boundary drawn as a line).
    * Open polylines           -> thin buffered "road" corridors.
    * Points / MultiPoints     -> small buffered marker discs.
  MultiPart geometry is exploded into one feature per part.
- Output rings are *open* (no duplicated closing vertex) to match how drawn
  zones are stored; the zone-create path re-closes them.
"""

from __future__ import annotations

import io
import zipfile
from dataclasses import dataclass, field
from typing import Any

from pyproj import CRS, Transformer

# Guardrails so a pathological upload can't exhaust memory or flood the client.
MAX_FEATURES = 2000
MAX_VERTICES_PER_RING = 20000
DEFAULT_ZONE_TYPE = "development_area"
LINE_ZONE_TYPE = "road"  # open polylines become buffered road corridors
LINE_HALF_WIDTH_M = 3.0  # ~6 m corridor for road / path / contour lines
POINT_RADIUS_M = 4.0  # points become small marker discs
SIMPLIFY_TOLERANCE_M = 0.5  # drop sub-0.5 m vertices to lighten dense geometry


class ShapefileImportError(ValueError):
    """Malformed / unsupported upload — mapped to HTTP 400 by the endpoint."""


@dataclass
class ParsedFeature:
    coordinates: list[list[float]]  # open ring: [[lon, lat], ...]
    zone_type: str
    properties: dict[str, Any]


@dataclass
class ParsedShapefile:
    features: list[ParsedFeature] = field(default_factory=list)
    detected_crs: str = "Unknown"
    feature_count: int = 0
    skipped_count: int = 0
    warnings: list[str] = field(default_factory=list)


def _jsonable(value: Any) -> Any:
    """Coerce a DBF attribute value into something JSON-serializable."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return value.decode("utf-8", "replace").strip()
    return str(value)


def _sibling(names: list[str], base: str, ext: str) -> str | None:
    """Find ``base + ext`` in the archive, case-insensitively."""
    target = (base + ext).lower()
    for n in names:
        if n.lower() == target:
            return n
    return None


def _close_enough(a: Any, b: Any, tol: float) -> bool:
    """True if two coordinates coincide within ``tol`` (detects closed polylines)."""
    return abs(a[0] - b[0]) <= tol and abs(a[1] - b[1]) <= tol


def parse_shapefile_zip(data: bytes) -> ParsedShapefile:
    """Parse a zipped shapefile (bytes) into reprojected WGS84 polygon features."""
    # pyshp is imported lazily: a missing optional dependency should surface as a
    # clean 400 on this endpoint, never crash the whole API at import time.
    try:
        import shapefile  # pyshp
        from shapely.geometry import Polygon as _Polygon, shape as _shape
    except ModuleNotFoundError as e:
        raise ShapefileImportError(
            "Shapefile support is not installed on the server (missing 'pyshp' / 'shapely')."
        ) from e

    try:
        zf = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as e:
        raise ShapefileImportError("Uploaded file is not a valid .zip archive.") from e

    names = [n for n in zf.namelist() if not n.endswith("/")]
    shp_name = next((n for n in names if n.lower().endswith(".shp")), None)
    if not shp_name:
        raise ShapefileImportError("No .shp file found inside the archive.")

    base = shp_name[:-4]
    dbf_name = _sibling(names, base, ".dbf")
    shx_name = _sibling(names, base, ".shx")
    prj_name = _sibling(names, base, ".prj")
    if not dbf_name:
        raise ShapefileImportError(
            "Archive is missing the .dbf component. Please zip all shapefile "
            "parts together (.shp, .dbf, .shx, .prj)."
        )

    result = ParsedShapefile()

    # --- Build the reprojection transformer from the .prj CRS -> WGS84 lon/lat.
    transformer: Transformer | None = None
    if prj_name:
        try:
            src_crs = CRS.from_wkt(zf.read(prj_name).decode("utf-8", "replace"))
            result.detected_crs = src_crs.name or "Unknown"
            if src_crs.is_geographic or src_crs.to_epsg() == 4326:
                # Already lon/lat degrees; no projected->geographic transform needed.
                transformer = None
            else:
                transformer = Transformer.from_crs(src_crs, CRS.from_epsg(4326), always_xy=True)
        except Exception as e:  # noqa: BLE001 - pyproj raises varied error types
            result.warnings.append(f"Could not read .prj CRS ({e}); assuming coordinates are already lon/lat.")
            result.detected_crs = "Unreadable .prj — assumed WGS84"
    else:
        result.warnings.append("No .prj file found; assuming coordinates are already lon/lat (WGS84).")
        result.detected_crs = "Assumed WGS84 (no .prj)"

    def reproject(ring: list[list[float]]) -> list[list[float]]:
        if transformer is None:
            return [[float(x), float(y)] for x, y in ring]
        xs = [c[0] for c in ring]
        ys = [c[1] for c in ring]
        lons, lats = transformer.transform(xs, ys)
        return [[float(lon), float(lat)] for lon, lat in zip(lons, lats)]

    # --- Read geometry + attributes from in-memory file objects.
    try:
        reader = shapefile.Reader(
            shp=io.BytesIO(zf.read(shp_name)),
            dbf=io.BytesIO(zf.read(dbf_name)),
            shx=io.BytesIO(zf.read(shx_name)) if shx_name else None,
        )
    except Exception as e:  # noqa: BLE001
        raise ShapefileImportError(f"Failed to read shapefile geometry: {e}") from e

    # Buffer / simplify sizes in SOURCE units: metres when the source CRS is
    # projected (transformer set), otherwise approximate degrees.
    if transformer is not None:
        line_buf, point_buf = LINE_HALF_WIDTH_M, POINT_RADIUS_M
        simplify_tol = SIMPLIFY_TOLERANCE_M
    else:
        line_buf = LINE_HALF_WIDTH_M / 111_320.0
        point_buf = POINT_RADIUS_M / 111_320.0
        simplify_tol = SIMPLIFY_TOLERANCE_M / 111_320.0

    def emit_polygon(poly: Any, zone_type: str, props: dict[str, Any]) -> None:
        """Reproject a shapely Polygon's exterior ring and append one feature."""
        # Thin out redundant vertices (dense contours / hi-res parcels) so the
        # globe doesn't raycast thousands of near-identical points per zone.
        if simplify_tol > 0:
            simplified = poly.simplify(simplify_tol)
            if simplified.geom_type == "Polygon" and not simplified.is_empty:
                poly = simplified
        ring = [[float(c[0]), float(c[1])] for c in poly.exterior.coords]
        if len(ring) >= 2 and ring[0] == ring[-1]:
            ring = ring[:-1]  # open the ring
        if len(ring) < 3:
            result.skipped_count += 1
            return
        if len(ring) > MAX_VERTICES_PER_RING:
            result.warnings.append("A polygon exceeded the vertex cap and was skipped.")
            result.skipped_count += 1
            return
        result.features.append(ParsedFeature(coordinates=reproject(ring), zone_type=zone_type, properties=props))

    for sr in reader.iterShapeRecords():
        if len(result.features) >= MAX_FEATURES:
            result.warnings.append(f"Stopped at {MAX_FEATURES} features; the file contains more.")
            break

        try:
            geom = _shape(sr.shape.__geo_interface__)
        except Exception:  # noqa: BLE001 - skip null / unreadable geometries
            result.skipped_count += 1
            continue
        if geom.is_empty:
            result.skipped_count += 1
            continue

        try:
            props = {str(k): _jsonable(v) for k, v in sr.record.as_dict().items()}
        except Exception:  # noqa: BLE001 - bad/empty DBF records shouldn't kill the import
            props = {}

        gt = geom.geom_type
        if gt in ("Polygon", "MultiPolygon"):
            # Footprints / parcels / zoning. MultiPolygons explode; holes drop.
            for poly in geom.geoms if gt == "MultiPolygon" else [geom]:
                emit_polygon(poly, DEFAULT_ZONE_TYPE, props)
        elif gt in ("LineString", "MultiLineString"):
            for line in geom.geoms if gt == "MultiLineString" else [geom]:
                pts = list(line.coords)
                # A closed polyline (a boundary drawn as a line) is filled into an
                # area zone; an open one (road / path / contour) is buffered into a
                # thin corridor so it still has renderable width.
                filled = None
                if len(pts) >= 4 and _close_enough(pts[0], pts[-1], line_buf):
                    candidate = _Polygon(pts)
                    if candidate.is_valid and candidate.area > 0:
                        filled = candidate
                if filled is not None:
                    emit_polygon(filled, DEFAULT_ZONE_TYPE, props)
                    continue
                corridor = line.buffer(line_buf, cap_style=2, join_style=2)
                if corridor.is_empty:
                    continue
                for poly in corridor.geoms if corridor.geom_type == "MultiPolygon" else [corridor]:
                    emit_polygon(poly, LINE_ZONE_TYPE, props)
        elif gt in ("Point", "MultiPoint"):
            for pt in geom.geoms if gt == "MultiPoint" else [geom]:
                disc = pt.buffer(point_buf, quad_segs=4)
                if not disc.is_empty:
                    emit_polygon(disc, DEFAULT_ZONE_TYPE, props)
        else:
            result.skipped_count += 1
            continue

    result.feature_count = len(result.features)
    if result.feature_count == 0 and result.skipped_count > 0:
        result.warnings.append("No usable geometry found in the shapefile (only empty or unsupported shapes).")
    return result
