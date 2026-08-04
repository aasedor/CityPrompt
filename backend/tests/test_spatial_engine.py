"""Spatial Intelligence Engine — pure-geometry unit tests (no DB, no HTTP)."""

import math

from shapely.geometry import LineString, Point, Polygon, mapping

from app.services import spatial_engine as se

# ~100m x 100m square in downtown Calgary (WGS84)
LAT = 51.045
LON = -114.07
M_PER_DEG_LAT = 111_320.0
M_PER_DEG_LON = M_PER_DEG_LAT * math.cos(math.radians(LAT))


def _offset(lon_m: float, lat_m: float) -> tuple[float, float]:
    return (LON + lon_m / M_PER_DEG_LON, LAT + lat_m / M_PER_DEG_LAT)


def _square(size_m: float = 100.0) -> Polygon:
    return Polygon(
        [
            _offset(0, 0),
            _offset(size_m, 0),
            _offset(size_m, size_m),
            _offset(0, size_m),
        ]
    )


def _feature(geom, **props):
    return {"geometry": mapping(geom), "properties": props}


def test_site_frame_metric_area_and_perimeter():
    frame = se.SiteFrame.from_wgs84(_square(100))
    assert abs(frame.area_m2 - 10_000) / 10_000 < 0.03
    assert abs(frame.perimeter_m - 400) / 400 < 0.03
    lon, lat = frame.centroid_wgs84()
    assert abs(lon - (LON + 50 / M_PER_DEG_LON)) < 1e-4
    assert abs(lat - (LAT + 50 / M_PER_DEG_LAT)) < 1e-4


def test_coverage_by_area_weighted_split():
    frame = se.SiteFrame.from_wgs84(_square(100))
    west = Polygon([_offset(-10, -10), _offset(50, -10), _offset(50, 110), _offset(-10, 110)])
    east = Polygon([_offset(50, -10), _offset(110, -10), _offset(110, 110), _offset(50, 110)])
    coverage = se.coverage_by(
        frame,
        [_feature(west, code="R-CG"), _feature(east, code="C-COR1")],
        lambda f: f["properties"]["code"],
    )
    assert set(coverage) == {"R-CG", "C-COR1"}
    assert abs(coverage["R-CG"]["pct"] - 50) < 2
    assert abs(coverage["C-COR1"]["pct"] - 50) < 2


def test_invalid_bowtie_geometry_is_repaired_not_fatal():
    frame = se.SiteFrame.from_wgs84(_square(100))
    bowtie = Polygon([_offset(0, 0), _offset(100, 100), _offset(100, 0), _offset(0, 100)])
    assert not bowtie.is_valid
    geom = se.shape_of(_feature(bowtie, code="DC"))
    assert geom is not None and geom.is_valid
    coverage = se.coverage_by(frame, [_feature(bowtie, code="DC")], lambda f: f["properties"]["code"])
    assert "DC" in coverage  # repaired bowtie still overlaps ~half the site
    assert 30 < coverage["DC"]["pct"] < 70


def test_shape_of_rejects_garbage():
    assert se.shape_of({"geometry": None, "properties": {}}) is None
    assert se.shape_of({"geometry": {"type": "Polygon", "coordinates": []}, "properties": {}}) is None


def test_nearest_and_count_within():
    frame = se.SiteFrame.from_wgs84(_square(100))
    near = _feature(Point(_offset(400, 50)), name="near-stop")  # ~300m east of the square
    far = _feature(Point(_offset(700, 50)), name="far-stop")  # ~600m east
    very_far = _feature(Point(_offset(2000, 50)), name="too-far")  # ~1.9km

    ranked = se.nearest(frame, [far, near, very_far], k=2)
    assert [f["properties"]["name"] for _, f in ranked] == ["near-stop", "far-stop"]
    assert abs(ranked[0][0] - 300) < 15

    assert se.count_within(frame, [near, far, very_far], 400) == 1
    assert se.count_within(frame, [near, far, very_far], 800) == 2


def test_length_within_by_class():
    frame = se.SiteFrame.from_wgs84(_square(100))
    collector = _feature(LineString([_offset(-50, 120), _offset(150, 120)]), cls="Collector")
    skeletal = _feature(LineString([_offset(-50, 5000), _offset(150, 5000)]), cls="Skeletal")  # 5km away
    lengths = se.length_within_by(frame, [collector, skeletal], lambda f: f["properties"]["cls"], radius_m=200)
    assert abs(lengths["Collector"] - 200) < 10
    assert "Skeletal" not in lengths


def test_frontage_detects_boundary_streets_only():
    frame = se.SiteFrame.from_wgs84(_square(100))
    fronting = _feature(LineString([_offset(-20, -8), _offset(120, -8)]), name="9 AV SW")
    distant = _feature(LineString([_offset(-20, 160), _offset(120, 160)]), name="somewhere else")
    hits = se.frontage(frame, [fronting, distant], tolerance_m=25)
    assert [f["properties"]["name"] for f, _ in hits] == ["9 AV SW"]
    assert hits[0][1] > 80  # shares most of the 100m edge


def test_network_distance_estimate_flags_and_scales():
    assert se.network_distance_estimate_m(100) == 135.0
    assert se.DISTANCE_METHOD == "euclidean_estimate"


def test_buffer_wgs84_is_metric_accurate_east_west():
    """Regression (review finding): degree-averaged buffering is ~18% short
    east-west at Calgary latitudes, silently shrinking every walkshed."""
    buffered = se.buffer_wgs84(_square(100), 800.0)
    frame = se.SiteFrame.from_wgs84(buffered)
    bounds = frame.site_m.bounds
    width_m = bounds[2] - bounds[0]  # expected: 100m site + 2 x 800m buffer
    height_m = bounds[3] - bounds[1]
    assert abs(width_m - 1700) / 1700 < 0.03, f"E-W extent {width_m:.0f}m, want ~1700m"
    assert abs(height_m - 1700) / 1700 < 0.03


def test_coverage_by_unions_overlapping_same_key_features():
    """Regression (review finding): overlapping same-key municipal features must
    not double-count — pct can never exceed 100."""
    frame = se.SiteFrame.from_wgs84(_square(100))
    covering = Polygon([_offset(-10, -10), _offset(110, -10), _offset(110, 110), _offset(-10, 110)])
    coverage = se.coverage_by(
        frame,
        [_feature(covering, code="R-CG"), _feature(covering, code="R-CG")],  # identical overlap twice
        lambda f: f["properties"]["code"],
    )
    assert 99 <= coverage["R-CG"]["pct"] <= 100.5
