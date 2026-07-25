"""Tests for the shapefile import / reprojection service.

The critical behaviour under test is CRS reprojection with correct axis order:
a shapefile in a projected CRS (here EPSG:3857) must come back as lon/lat in the
right hemisphere. If ``always_xy`` were wrong, lon/lat would be swapped and these
assertions would fail.

Input geometry for the reprojection case is generated with the *spherical*
Mercator formula directly (independent of pyproj) so the test is a genuine
round-trip rather than pyproj checking its own output.
"""

import io
import math
import os
import tempfile
import zipfile

import pytest
import shapefile  # pyshp
from pyproj import CRS

from app.services.shapefile_import import ShapefileImportError, parse_shapefile_zip

_R = 6378137.0  # Web Mercator sphere radius


def _to_3857(lon: float, lat: float) -> list[float]:
    x = _R * math.radians(lon)
    y = _R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return [x, y]


def _make_zip(write_fn, prj_wkt: str | None = None) -> bytes:
    """Run a pyshp Writer via ``write_fn(writer)`` and return a zipped shapefile."""
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, "layer")
    w = shapefile.Writer(path)
    write_fn(w)
    w.close()
    if prj_wkt is not None:
        with open(path + ".prj", "w", encoding="utf-8") as f:
            f.write(prj_wkt)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for ext in (".shp", ".shx", ".dbf", ".prj"):
            p = path + ext
            if os.path.exists(p):
                z.write(p, arcname="layer" + ext)
    return buf.getvalue()


def test_reprojects_projected_crs_to_lonlat():
    """A square authored in EPSG:3857 must reproject back to its lon/lat bbox."""
    # Known lon/lat square near downtown Calgary.
    lon0, lon1, lat0, lat1 = -114.070, -114.060, 51.044, 51.050
    ring_lonlat = [(lon0, lat0), (lon1, lat0), (lon1, lat1), (lon0, lat1), (lon0, lat0)]
    ring_3857 = [_to_3857(lon, lat) for lon, lat in ring_lonlat]

    def write(w):
        w.field("NAME", "C", size=40)
        w.poly([ring_3857])
        w.record("Parcel A")

    data = _make_zip(write, prj_wkt=CRS.from_epsg(3857).to_wkt())
    parsed = parse_shapefile_zip(data)

    assert parsed.feature_count == 1
    assert parsed.skipped_count == 0
    assert "Mercator" in parsed.detected_crs

    feat = parsed.features[0]
    lons = [c[0] for c in feat.coordinates]
    lats = [c[1] for c in feat.coordinates]
    # Right hemisphere + right bbox => axis order and reprojection are correct.
    assert min(lons) == pytest.approx(lon0, abs=1e-4)
    assert max(lons) == pytest.approx(lon1, abs=1e-4)
    assert min(lats) == pytest.approx(lat0, abs=1e-4)
    assert max(lats) == pytest.approx(lat1, abs=1e-4)
    # Ring is returned open (closing vertex dropped).
    assert feat.coordinates[0] != feat.coordinates[-1]
    assert len(feat.coordinates) == 4
    assert feat.zone_type == "development_area"
    assert feat.properties["NAME"] == "Parcel A"


def test_no_prj_passthrough_lonlat():
    """With no .prj, coordinates are assumed to already be lon/lat and pass through."""
    ring = [(-114.07, 51.04), (-114.06, 51.04), (-114.06, 51.05), (-114.07, 51.05), (-114.07, 51.04)]

    def write(w):
        w.field("ID", "N")
        w.poly([list(ring)])
        w.record(7)

    parsed = parse_shapefile_zip(_make_zip(write, prj_wkt=None))

    assert parsed.feature_count == 1
    feat = parsed.features[0]
    assert min(c[0] for c in feat.coordinates) == pytest.approx(-114.07, abs=1e-9)
    assert max(c[1] for c in feat.coordinates) == pytest.approx(51.05, abs=1e-9)
    assert any("no .prj" in w.lower() or "prj" in w.lower() for w in parsed.warnings)
    assert feat.properties["ID"] == 7


def test_geographic_crs_detected_and_passthrough():
    """An EPSG:4326 .prj is geographic — no projected transform, name detected."""
    ring = [(-114.07, 51.04), (-114.06, 51.04), (-114.06, 51.05), (-114.07, 51.04)]

    def write(w):
        w.field("NAME", "C")
        w.poly([list(ring)])
        w.record("geo")

    parsed = parse_shapefile_zip(_make_zip(write, prj_wkt=CRS.from_epsg(4326).to_wkt()))
    assert parsed.feature_count == 1
    assert "WGS 84" in parsed.detected_crs
    assert min(c[0] for c in parsed.features[0].coordinates) == pytest.approx(-114.07, abs=1e-9)


def test_holes_dropped_and_attributes_mapped():
    """Interior rings are dropped; DBF attributes land in properties."""
    # ESRI winding: exterior ring CLOCKWISE, hole COUNTER-CLOCKWISE.
    exterior = [(-114.07, 51.04), (-114.07, 51.06), (-114.05, 51.06), (-114.05, 51.04), (-114.07, 51.04)]
    hole = [(-114.065, 51.045), (-114.055, 51.045), (-114.055, 51.055), (-114.065, 51.055), (-114.065, 51.045)]

    def write(w):
        w.field("NAME", "C", size=40)
        w.field("ZONING", "C", size=20)
        w.poly([list(exterior), list(hole)])  # exterior + one hole
        w.record("Block 12", "C-1")

    parsed = parse_shapefile_zip(_make_zip(write, prj_wkt=None))
    assert parsed.feature_count == 1
    feat = parsed.features[0]
    # Only the exterior ring (4 open vertices) is kept — hole vertices excluded.
    assert len(feat.coordinates) == 4
    assert feat.properties == {"NAME": "Block 12", "ZONING": "C-1"}


def test_open_line_buffered_to_corridor():
    """An open polyline becomes a buffered 'road' corridor polygon."""
    def write(w):
        w.field("NAME", "C")
        w.line([[[-114.07, 51.04], [-114.06, 51.05], [-114.05, 51.045]]])
        w.record("Main St")

    parsed = parse_shapefile_zip(_make_zip(write, prj_wkt=None))
    assert parsed.feature_count >= 1
    feat = parsed.features[0]
    assert feat.zone_type == "road"
    assert len(feat.coordinates) >= 4  # a corridor polygon, not a bare line
    assert feat.properties["NAME"] == "Main St"


def test_closed_line_filled_to_polygon():
    """A closed polyline (a boundary drawn as a line) is filled into an area zone."""
    ring = [(-114.07, 51.04), (-114.05, 51.04), (-114.05, 51.06), (-114.07, 51.06), (-114.07, 51.04)]

    def write(w):
        w.field("NAME", "C")
        w.line([list(ring)])  # a LINE that happens to be closed
        w.record("Lot 9")

    parsed = parse_shapefile_zip(_make_zip(write, prj_wkt=None))
    assert parsed.feature_count == 1
    feat = parsed.features[0]
    assert feat.zone_type == "development_area"
    # Filled to the square's bbox, not a thin corridor.
    assert min(c[0] for c in feat.coordinates) == pytest.approx(-114.07, abs=1e-9)
    assert max(c[0] for c in feat.coordinates) == pytest.approx(-114.05, abs=1e-9)
    assert max(c[1] for c in feat.coordinates) == pytest.approx(51.06, abs=1e-9)


def test_point_buffered_to_marker():
    """A point becomes a small buffered marker polygon centred on the point."""
    def write(w):
        w.field("NAME", "C")
        w.point(-114.066, 51.045)
        w.record("Tree 1")

    parsed = parse_shapefile_zip(_make_zip(write, prj_wkt=None))
    assert parsed.feature_count == 1
    feat = parsed.features[0]
    assert len(feat.coordinates) >= 4
    cx = sum(c[0] for c in feat.coordinates) / len(feat.coordinates)
    cy = sum(c[1] for c in feat.coordinates) / len(feat.coordinates)
    assert cx == pytest.approx(-114.066, abs=1e-3)
    assert cy == pytest.approx(51.045, abs=1e-3)


def test_bad_zip_raises():
    with pytest.raises(ShapefileImportError):
        parse_shapefile_zip(b"this is not a zip file")


def test_missing_dbf_raises():
    """A .shp with no sibling .dbf is rejected with a helpful message."""
    tmp = tempfile.mkdtemp()
    path = os.path.join(tmp, "layer")
    w = shapefile.Writer(path)
    w.field("NAME", "C")
    w.poly([[[-114.07, 51.04], [-114.06, 51.04], [-114.06, 51.05], [-114.07, 51.04]]])
    w.record("x")
    w.close()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.write(path + ".shp", arcname="layer.shp")  # deliberately omit .dbf
    with pytest.raises(ShapefileImportError, match=".dbf"):
        parse_shapefile_zip(buf.getvalue())
