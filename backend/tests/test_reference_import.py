"""Reference import must retain cartography, not infer physical design objects."""

import io
import json
import zipfile

import pytest
import shapefile
from pyproj import CRS

from app.services import reference_import as service


EXTERIOR = [[-114.08, 51.04], [-114.08, 51.06], [-114.04, 51.06], [-114.04, 51.04], [-114.08, 51.04]]
HOLE = [[-114.07, 51.045], [-114.05, 51.045], [-114.05, 51.055], [-114.07, 51.055], [-114.07, 51.045]]


def feature(geometry, properties=None):
    return {
        "type": "Feature",
        "id": "district-7",
        "geometry": geometry,
        "properties": properties or {"ZONE": "R-CG", "height": 11},
    }


def geojson(features):
    return json.dumps({"type": "FeatureCollection", "features": features}).encode()


def shapefile_zip(write, prj=None, encoding="utf-8", cpg=None):
    shp, shx, dbf = io.BytesIO(), io.BytesIO(), io.BytesIO()
    writer = shapefile.Writer(shp=shp, shx=shx, dbf=dbf, encoding=encoding)
    writer.field("ZONE", "C", 30)
    write(writer)
    writer.close()
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as archive:
        for suffix, data in (("shp", shp), ("shx", shx), ("dbf", dbf)):
            archive.writestr(f"nested/district.{suffix}", data.getvalue())
        if prj is not None:
            archive.writestr("nested/district.prj", prj)
        if cpg is not None:
            archive.writestr("nested/district.cpg", cpg)
    return output.getvalue()


def test_geojson_keeps_holes_multipart_properties_and_ids():
    polygon = {"type": "MultiPolygon", "coordinates": [[EXTERIOR, HOLE]]}
    parsed = service.parse_reference_file(geojson([feature(polygon)]), "zoning.geojson")
    result = parsed.feature_collection["features"][0]
    assert result == feature(polygon)
    assert "zone_type" not in result
    assert parsed.bounds == [-114.08, 51.04, -114.04, 51.06]
    assert parsed.feature_count == 1


def test_points_lines_and_geometry_collection_never_become_buffered_polygons():
    geometry = {
        "type": "GeometryCollection",
        "geometries": [
            {"type": "Point", "coordinates": [-114.06, 51.05, 1000]},
            {"type": "LineString", "coordinates": [[-114.1, 51], [-114.0, 51.1]]},
            {"type": "MultiPoint", "coordinates": [[-114.2, 51], [-114.3, 51.1]]},
        ],
    }
    parsed = service.parse_geojson_reference(geojson([feature(geometry)]))
    assert parsed.feature_collection["features"][0]["geometry"] == geometry


def test_shapefile_zoning_retains_hole_and_attributes():
    def write(writer):
        writer.poly([EXTERIOR, HOLE])
        writer.record("R-CG")

    parsed = service.parse_reference_file(shapefile_zip(write, CRS.from_epsg(4326).to_wkt()), "zone.zip")
    result = parsed.feature_collection["features"][0]
    assert result["geometry"]["type"] == "Polygon"
    assert result["geometry"]["coordinates"] == [EXTERIOR, HOLE]
    assert result["properties"] == {"ZONE": "R-CG"}
    assert "zone_type" not in result


def test_shapefile_line_retained_and_missing_crs_disclosed():
    def write(writer):
        writer.line([[[-114, 51], [-113.99, 51.01]]])
        writer.record("Contour")

    parsed = service.parse_shapefile_reference(shapefile_zip(write))
    assert parsed.feature_collection["features"][0]["geometry"]["type"] == "LineString"
    assert parsed.warnings and "No .prj" in parsed.warnings[0]


def test_shapefile_z_holes_and_measure_values_survive():
    exterior = [[*point, 100] for point in EXTERIOR]
    hole = [[*point, 110] for point in HOLE]

    def write(writer):
        writer.polyz([exterior, hole])
        writer.record("Elevation")

    parsed = service.parse_shapefile_reference(shapefile_zip(write, CRS.from_epsg(4326).to_wkt()))
    assert parsed.feature_collection["features"][0]["geometry"]["coordinates"] == [exterior, hole]

    def measure(writer):
        writer.pointm(-114, 51, 42)
        writer.record("Station")

    measured = service.parse_shapefile_reference(shapefile_zip(measure))
    assert measured.feature_collection["features"][0]["properties"]["_shapefile_m_values"] == [42]


def test_shapefile_honors_declared_dbf_character_encoding():
    def write(writer):
        writer.point(-114, 51)
        writer.record("Cit\u00e9")

    parsed = service.parse_shapefile_reference(shapefile_zip(write, encoding="cp1252", cpg="1252"))
    assert parsed.feature_collection["features"][0]["properties"]["ZONE"] == "Cit\u00e9"


def test_shapefile_reprojection_preserves_multipart_identity():
    # Web Mercator equator points have independently known metre coordinates.
    def write(writer):
        writer.multipoint([[0, 0], [111319.49079327357, 0]])
        writer.record("Sites")

    parsed = service.parse_shapefile_reference(shapefile_zip(write, CRS.from_epsg(3857).to_wkt()))
    geom = parsed.feature_collection["features"][0]["geometry"]
    assert geom["type"] == "MultiPoint"
    assert geom["coordinates"][1] == pytest.approx([1, 0])


@pytest.mark.parametrize(
    "geometry",
    [
        {"type": "Point", "coordinates": [500000, 5700000]},
        {"type": "Point", "coordinates": [float("nan"), 51]},
        {"type": "Point", "coordinates": [True, 51]},
        {"type": "Point", "coordinates": [10**400, 51]},
        {"type": "Polygon", "coordinates": [[[0, 0], [1, 1], [0, 1], [1, 0], [0, 0]]]},
        {"type": "LineString", "coordinates": []},
        {"type": "LineString", "coordinates": [[0, 0]]},
    ],
)
def test_invalid_geometry_fails_whole_import(geometry):
    with pytest.raises(service.ReferenceImportError):
        service.parse_geojson_reference(geojson([feature({"type": "Point", "coordinates": [0, 0]}), feature(geometry)]))


def test_no_silent_feature_truncation(monkeypatch):
    monkeypatch.setattr(service, "MAX_FEATURES", 1)
    point = feature({"type": "Point", "coordinates": [0, 0]})
    with pytest.raises(service.ReferenceImportError, match="features"):
        service.parse_geojson_reference(geojson([point, point]))


def test_coordinate_and_attribute_caps(monkeypatch):
    monkeypatch.setattr(service, "MAX_POSITIONS", 1)
    with pytest.raises(service.ReferenceImportError, match="coordinates"):
        service.parse_geojson_reference(geojson([feature({"type": "LineString", "coordinates": [[0, 0], [1, 1]]})]))
    with pytest.raises(service.ReferenceImportError, match="attribute"):
        service.parse_geojson_reference(
            geojson([feature({"type": "Point", "coordinates": [0, 0]}, {"text": "a" * 33000})])
        )


def test_unsupported_geojson_crs_requires_explicit_reprojection():
    doc = {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": "EPSG:3857"}},
        "features": [feature({"type": "Point", "coordinates": [0, 0]})],
    }
    with pytest.raises(service.ReferenceImportError, match="WGS84"):
        service.parse_geojson_reference(json.dumps(doc).encode())


def test_foreign_geometry_members_do_not_bypass_validation():
    parsed = service.parse_geojson_reference(
        geojson([feature({"type": "Point", "coordinates": [0, 0], "custom": float("nan")})])
    )
    assert parsed.feature_collection["features"][0]["geometry"] == {"type": "Point", "coordinates": [0, 0]}
    with pytest.raises(service.ReferenceImportError, match="WGS84"):
        service.parse_geojson_reference(
            json.dumps({"type": "Point", "coordinates": [0, 0], "crs": {"properties": ["invalid"]}}).encode()
        )


def test_zip_expansion_and_invalid_prj_rejected(monkeypatch):
    def write(writer):
        writer.point(-114, 51)
        writer.record("Tree")

    with pytest.raises(service.ReferenceImportError, match=".prj"):
        service.parse_shapefile_reference(shapefile_zip(write, "not a CRS"))
    monkeypatch.setattr(service, "MAX_UNCOMPRESSED_BYTES", 10)
    with pytest.raises(service.ReferenceImportError, match="expanded"):
        service.parse_shapefile_reference(shapefile_zip(write))


@pytest.mark.parametrize("data,filename", [(b"not zip", "z.zip"), (b"not json", "z.geojson"), (b"{}", "z.csv")])
def test_malformed_or_unsupported_file_rejected(data, filename):
    with pytest.raises(service.ReferenceImportError):
        service.parse_reference_file(data, filename)
