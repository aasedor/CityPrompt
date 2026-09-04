"""Read reference datasets without turning their geometry into design objects.

Unlike the legacy design-zone importer, this path retains holes, multipart
features, lines, points and attributes. Import is atomic: malformed or oversized
data is rejected, never silently truncated or converted into buildings.
"""

from __future__ import annotations

import codecs
import io
import json
import math
import zipfile
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

from pyproj import CRS, Transformer
from shapely.geometry import mapping, shape
from shapely.ops import transform
from shapely.errors import ShapelyError

from app.services.shapefile_import import _jsonable, _sibling

MAX_UPLOAD_BYTES = 25 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 100 * 1024 * 1024
MAX_FEATURES = 2000
MAX_POSITIONS = 100_000
MAX_STORED_BYTES = 4 * 1024 * 1024
MAX_ATTRIBUTE_BYTES = 32 * 1024
GEOMETRY_TYPES = {
    "Point", "MultiPoint", "LineString", "MultiLineString",
    "Polygon", "MultiPolygon", "GeometryCollection",
}


def _finite_number(value: Any) -> bool:
    try:
        return not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
    except OverflowError:
        return False


def _geometry_members(geometry: dict) -> dict:
    """Keep geometry, excluding unvalidated foreign members such as custom bbox."""
    if geometry["type"] == "GeometryCollection":
        return {"type": "GeometryCollection", "geometries": [_geometry_members(child) for child in geometry["geometries"]]}
    return {"type": geometry["type"], "coordinates": geometry["coordinates"]}


class ReferenceImportError(ValueError):
    """A source needs correction before it can become a reference layer."""


@dataclass
class ParsedReference:
    feature_collection: dict[str, Any]
    source_crs: str
    bounds: list[float]
    warnings: list[str]
    storage_bytes: int

    @property
    def feature_count(self) -> int:
        return len(self.feature_collection["features"])


def _validate_json_tree(value: Any, depth: int = 0) -> None:
    if depth > 12:
        raise ReferenceImportError("Attributes are nested too deeply (maximum 12 levels).")
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ReferenceImportError("The dataset contains a non-finite number.")
        return
    if isinstance(value, dict):
        if not all(isinstance(key, str) for key in value):
            raise ReferenceImportError("Attribute names must be strings.")
        for item in value.values():
            _validate_json_tree(item, depth + 1)
        return
    if isinstance(value, list):
        for item in value:
            _validate_json_tree(item, depth + 1)
        return
    raise ReferenceImportError("Attributes must contain JSON values.")


def _positions(geometry: dict, depth: int = 0):
    if depth > 8 or not isinstance(geometry, dict) or geometry.get("type") not in GEOMETRY_TYPES:
        raise ReferenceImportError("Unsupported geometry or geometry collection nested too deeply.")
    if geometry["type"] == "GeometryCollection":
        children = geometry.get("geometries")
        if not isinstance(children, list):
            raise ReferenceImportError("A geometry collection needs a geometries array.")
        for child in children:
            yield from _positions(child, depth + 1)
        return

    dimensions = {"Point": 0, "MultiPoint": 1, "LineString": 1,
                  "MultiLineString": 2, "Polygon": 2, "MultiPolygon": 3}

    def walk(coords: Any, remaining: int):
        if not isinstance(coords, (list, tuple)):
            raise ReferenceImportError("Geometry coordinates must be arrays.")
        if remaining:
            for child in coords:
                yield from walk(child, remaining - 1)
            return
        if len(coords) not in (2, 3) or any(not _finite_number(v) for v in coords):
            raise ReferenceImportError("Each coordinate must contain two or three finite numbers.")
        if not (-180 <= coords[0] <= 180 and -90 <= coords[1] <= 90):
            raise ReferenceImportError("Coordinates are outside WGS84 longitude/latitude bounds. Check the source CRS.")
        yield coords

    yield from walk(geometry.get("coordinates"), dimensions[geometry["type"]])


def _finish(features: list[dict], source_crs: str, warnings: list[str]) -> ParsedReference:
    if not features:
        raise ReferenceImportError("The file contains no non-empty reference features.")
    if len(features) > MAX_FEATURES:
        raise ReferenceImportError(f"A reference layer supports up to {MAX_FEATURES:,} features. Export a smaller area.")
    bounds = [180.0, 90.0, -180.0, -90.0]
    position_count = 0
    for index, feature in enumerate(features, 1):
        if not isinstance(feature, dict) or feature.get("type") != "Feature":
            raise ReferenceImportError(f"Item {index} must be a GeoJSON Feature.")
        geometry = feature.get("geometry")
        if not isinstance(geometry, dict):
            raise ReferenceImportError(f"Feature {index} has no geometry.")
        for position in _positions(geometry):
            position_count += 1
            if position_count > MAX_POSITIONS:
                raise ReferenceImportError(f"A layer supports up to {MAX_POSITIONS:,} coordinates. Export a smaller area.")
            bounds = [min(bounds[0], position[0]), min(bounds[1], position[1]),
                      max(bounds[2], position[0]), max(bounds[3], position[1])]
        try:
            geom = shape(geometry)
            if geom.is_empty or not geom.is_valid:
                raise ValueError("empty or invalid geometry")
        except (ValueError, TypeError, KeyError, IndexError, ShapelyError) as exc:
            raise ReferenceImportError(f"Feature {index} has invalid geometry; correct the source before importing.") from exc
        feature["geometry"] = _geometry_members(geometry)
        properties = feature.get("properties")
        if properties is None:
            properties = {}
        if not isinstance(properties, dict):
            raise ReferenceImportError(f"Feature {index} properties must be an object.")
        _validate_json_tree(properties)
        if len(json.dumps(properties, ensure_ascii=False).encode("utf-8")) > MAX_ATTRIBUTE_BYTES:
            raise ReferenceImportError(f"Feature {index} has too much attribute data (maximum 32 KB).")
        feature["properties"] = properties
        if "id" in feature and (isinstance(feature["id"], bool) or not isinstance(feature["id"], (str, int, float))):
            raise ReferenceImportError(f"Feature {index} ID must be a string or number.")
        if isinstance(feature.get("id"), float) and not math.isfinite(feature["id"]):
            raise ReferenceImportError(f"Feature {index} ID must be finite.")
    # Normalize tuples to JSON arrays, and exclude foreign members that the
    # parser has not validated. Attributes and supported feature IDs survive.
    collection = {"type": "FeatureCollection", "features": [
        {key: feature[key] for key in ("type", "geometry", "properties", "id") if key in feature}
        for feature in features
    ]}
    encoded = json.dumps(collection, ensure_ascii=False, allow_nan=False, separators=(",", ":")).encode("utf-8")
    if len(encoded) > MAX_STORED_BYTES:
        raise ReferenceImportError("The reference data exceeds 4 MB after parsing. Export a smaller area.")
    return ParsedReference(json.loads(encoded), source_crs, bounds, warnings, len(encoded))


def parse_geojson_reference(data: bytes) -> ParsedReference:
    if len(data) > MAX_UPLOAD_BYTES:
        raise ReferenceImportError("Reference files must be 25 MB or smaller.")
    try:
        document = json.loads(data.decode("utf-8-sig"))
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise ReferenceImportError("The file is not valid UTF-8 GeoJSON.") from exc
    if not isinstance(document, dict):
        raise ReferenceImportError("GeoJSON must be an object.")
    if document.get("crs"):
        crs = document["crs"]
        try:
            name = ((crs.get("properties") or {}).get("name", "")) if isinstance(crs, dict) else ""
            source = CRS.from_user_input(name)
            if not source.equals(CRS.from_epsg(4326), ignore_axis_order=True):
                raise ValueError("not WGS84")
        except Exception as exc:
            raise ReferenceImportError("GeoJSON must use WGS84 longitude/latitude. Reproject it or import a shapefile with its .prj.") from exc
    if document.get("type") == "FeatureCollection":
        features = document.get("features")
        if not isinstance(features, list):
            raise ReferenceImportError("A FeatureCollection needs a features array.")
    elif document.get("type") == "Feature":
        features = [document]
    else:
        features = [{"type": "Feature", "geometry": document, "properties": {}}]
    return _finish(features, "WGS84 (EPSG:4326)", [])


def parse_shapefile_reference(data: bytes) -> ParsedReference:
    if len(data) > MAX_UPLOAD_BYTES:
        raise ReferenceImportError("Reference files must be 25 MB or smaller.")
    import shapefile

    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as exc:
        raise ReferenceImportError("The file is not a valid ZIP archive.") from exc
    with archive:
        entries = archive.infolist()
        if len(entries) > 100 or sum(entry.file_size for entry in entries) > MAX_UNCOMPRESSED_BYTES:
            raise ReferenceImportError("The ZIP is too large when expanded (maximum 100 MB and 100 entries).")
        if any(entry.flag_bits & 1 for entry in entries):
            raise ReferenceImportError("Encrypted ZIP archives are not supported.")
        names = [entry.filename for entry in entries if not entry.is_dir()]
        shps = [name for name in names if name.lower().endswith(".shp")]
        if len(shps) != 1:
            raise ReferenceImportError("Upload exactly one shapefile dataset per ZIP.")
        base = shps[0][:-4]
        dbf, shx, prj = (_sibling(names, base, ext) for ext in (".dbf", ".shx", ".prj"))
        if not dbf or not shx:
            raise ReferenceImportError("The ZIP must contain matching .shp, .shx and .dbf files; include .prj for the source CRS.")
        warnings: list[str] = []
        if prj:
            try:
                source = CRS.from_wkt(archive.read(prj).decode("utf-8-sig"))
            except Exception as exc:
                raise ReferenceImportError("The .prj cannot be read. Supply a valid CRS before importing.") from exc
        else:
            source = CRS.from_epsg(4326)
            warnings.append("No .prj supplied: assumed WGS84 longitude/latitude. Verify placement against the map.")
        transformer = Transformer.from_crs(source, CRS.from_epsg(4326), always_xy=True)
        try:
            encoding = "utf-8"
            cpg = _sibling(names, base, ".cpg")
            if cpg:
                code_page = archive.read(cpg).decode("ascii").strip()
                encoding = "utf-8" if code_page == "65001" else f"cp{code_page}" if code_page.isdigit() else code_page
                codecs.lookup(encoding)
            reader = shapefile.Reader(shp=io.BytesIO(archive.read(shps[0])),
                                      shx=io.BytesIO(archive.read(shx)), dbf=io.BytesIO(archive.read(dbf)), encoding=encoding)
            if len(reader) > MAX_FEATURES:
                raise ReferenceImportError(f"A reference layer supports up to {MAX_FEATURES:,} features. Export a smaller area.")
            features = []
            for index, record in enumerate(reader.iterShapeRecords(), 1):
                if record.shape.shapeType == shapefile.NULL:
                    warnings.append(f"Skipped empty feature {index}.")
                    continue
                source_shape = record.shape
                # PyShp's GeoJSON adapter otherwise omits its separate Z array.
                # Add it before ring grouping so multipart geometry and holes
                # retain their original vertex elevations and ordering.
                if getattr(source_shape, "z", None) is not None:
                    if len(source_shape.z) != len(source_shape.points):
                        raise ReferenceImportError(f"Feature {index} has an incomplete elevation array.")
                    source_shape.points = [(*point[:2], z) for point, z in zip(source_shape.points, source_shape.z)]
                geometry = shape(source_shape.__geo_interface__)
                projected = transform(transformer.transform, geometry)
                properties = {str(k): _jsonable(v) for k, v in record.record.as_dict().items()}
                measures = getattr(source_shape, "m", None)
                if measures and any(value is not None for value in measures):
                    key = "_shapefile_m_values"
                    while key in properties:
                        key += "_"
                    properties[key] = list(measures)
                    warning = "Shapefile measure values are retained as additional _shapefile_m_values attributes, not used as heights."
                    if warning not in warnings:
                        warnings.append(warning)
                features.append({"type": "Feature", "geometry": mapping(projected),
                                 "properties": properties})
            reader.close()
        except ReferenceImportError:
            raise
        except Exception as exc:
            raise ReferenceImportError("The shapefile could not be read or reprojected. Check its geometry, encoding and sidecar files.") from exc
    return _finish(features, (source.name or str(source))[:255], warnings)


def parse_reference_file(data: bytes, filename: str) -> ParsedReference:
    extension = PurePosixPath(filename.replace("\\", "/")).suffix.lower()
    if extension == ".zip":
        return parse_shapefile_reference(data)
    if extension in (".geojson", ".json"):
        return parse_geojson_reference(data)
    raise ReferenceImportError("Choose a GeoJSON (.geojson or .json) or zipped shapefile (.zip).")
