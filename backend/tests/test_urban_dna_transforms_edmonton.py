"""Edmonton transform tests — canned Socrata-shaped features -> DNA facts.

Geometry is a ~100m square in downtown Edmonton; features are hand-placed at
known metric offsets so walkshed counts and frontage checks are deterministic.
Column names mirror scripts/verify_edmonton_datasets.py output (2026-07-11).
"""

from shapely.geometry import Polygon

from app.services.city_connector.cities.edmonton import transforms

# ~100m x 100m site square (lon 0.0015 deg ~= 99m at 53.5N; lat 0.0009 deg ~= 100m)
SITE = Polygon([
    (-113.4948, 53.5415), (-113.4933, 53.5415),
    (-113.4933, 53.5424), (-113.4948, 53.5424),
])


def _poly(lon0, lat0, lon1, lat1, props):
    return {
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[lon0, lat0], [lon1, lat0], [lon1, lat1], [lon0, lat1], [lon0, lat0]]],
        },
        "properties": props,
    }


def _point(lon, lat, props):
    return {"geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": props}


def _line(coords, props):
    return {"geometry": {"type": "LineString", "coordinates": coords}, "properties": props}


# --- zoning -------------------------------------------------------------------

def test_zoning_captures_urls_and_stays_honest_about_rules():
    features = [
        _poly(-113.4950, 53.5413, -113.4930, 53.5426, {
            "zoning": "HDR", "description": "High Density Residential Zone",
            "url": "https://zoningbylaw.edmonton.ca/hdr", "dc2_sub_area": None,
        }),
        _poly(-113.4936, 53.5413, -113.4930, 53.5426, {
            "zoning": "DC2", "description": "Site Specific Development Control Provision",
            "url": "https://zoningbylaw.edmonton.ca/dc2-1060", "dc2_sub_area": "2",
        }),
        _poly(-113.4950, 53.5413, -113.4945, 53.5426, {
            "zoning": "CMU", "description": "Commercial Mixed Use Zone",
            "url": "https://zoningbylaw.edmonton.ca/cmu", "dc2_sub_area": None,
        }),
        # Adjacent commercial zone ~90m east of the site (inside the 200m ring)
        _poly(-113.4920, 53.5415, -113.4900, 53.5424, {
            "zoning": "CN", "description": "Neighbourhood Commercial Zone",
            "url": "https://zoningbylaw.edmonton.ca/cn", "dc2_sub_area": None,
        }),
    ]
    facts, warnings = transforms.zoning(features, SITE)

    assert facts["land_use.dominant_district"] == "HDR"
    codes = {d["code"] for d in facts["land_use.districts"]}
    assert codes == {"HDR", "DC2", "CMU"}
    assert all(d["zone_page_url"] for d in facts["land_use.districts"])
    # Bylaw 20001's layer has no numeric regulation columns — honesty over guesses.
    assert facts["land_use.far_assumption"] is None
    assert facts["land_use.height_assumption_m"] is None
    assert facts["land_use.mixed_use_opportunity"] is True  # residential + mixed_use on site
    codes_in_warnings = {w["code"] for w in warnings}
    assert "ZONE_RULES_IN_BYLAW" in codes_in_warnings
    assert "DIRECT_CONTROL_PROVISION" in codes_in_warnings
    assert "commercial" in facts["land_use.adjacent_uses"]


def test_zoning_empty_degrades():
    facts, warnings = transforms.zoning([], SITE)
    assert facts == {}
    assert any(w["code"] == "LAND_USE_EMPTY" for w in warnings)


# --- parcel points -------------------------------------------------------------

def test_parcel_points_counts_and_flags_missing_fabric():
    features = [
        _point(-113.4945, 53.5417, {
            "account_number": "1", "house_number": "10145", "street_name": "104 Street NW",
            "zoning": "RS", "lot_size": 500, "year_built": 1950, "neighbourhood": "OLIVER",
        }),
        _point(-113.4940, 53.5420, {
            "account_number": "2", "house_number": "10147", "street_name": "104 Street NW",
            "zoning": "RS", "lot_size": 510, "year_built": 1960, "neighbourhood": "OLIVER",
        }),
        _point(-113.4936, 53.5422, {
            "account_number": "3", "house_number": "10149", "street_name": "104 Street NW",
            "zoning": "CMU", "lot_size": None, "year_built": None, "neighbourhood": "OLIVER",
        }),
        # outside the site — must not count
        _point(-113.4900, 53.5420, {"account_number": "4", "zoning": "RS"}),
    ]
    facts, warnings = transforms.parcel_points(features, SITE)

    assert facts["site.parcel_count"] == 3
    assert facts["site.assembly_risk"]["level"] == "high"  # 3 properties + mixed zoning
    assert facts["built_form.site_year_built_mean"] == 1955
    assert any(w["code"] == "PARCEL_GEOMETRY_UNAVAILABLE" for w in warnings)


def test_parcel_points_empty_degrades():
    facts, warnings = transforms.parcel_points([], SITE)
    assert facts == {}
    assert any(w["code"] == "PARCELS_EMPTY" for w in warnings)


# --- neighbourhoods --------------------------------------------------------------

def test_neighbourhoods_district_becomes_plan_and_lap():
    features = [
        _poly(-113.4960, 53.5410, -113.4920, 53.5430, {
            "name": "OLIVER", "descriptive_name": "Oliver", "district": "Central",
            "effective_end_date": None,
        }),
        # historical row must be ignored
        _poly(-113.4960, 53.5410, -113.4920, 53.5430, {
            "name": "OLD NAME", "descriptive_name": "Old Name", "district": "Central",
            "effective_end_date": "2020-01-01T00:00:00",
        }),
    ]
    facts, warnings = transforms.neighbourhoods(features, SITE)

    assert facts["site.community_name"] == "Oliver"
    assert facts["land_use.lap_name"] == "Central District Plan"
    assert facts["policy.applicable_plans"][0]["plan_type"] == "District Plan"
    assert not warnings


def test_neighbourhoods_without_district_notes_citywide_policy():
    features = [
        _poly(-113.4960, 53.5410, -113.4920, 53.5430, {
            "name": "OLIVER", "descriptive_name": "Oliver", "district": None,
            "effective_end_date": None,
        }),
    ]
    facts, warnings = transforms.neighbourhoods(features, SITE)
    assert facts["land_use.lap_name"] is None
    assert facts["policy.applicable_plans"] == []
    assert any(w["code"] == "NO_DISTRICT_PLAN" for w in warnings)


# --- roads ------------------------------------------------------------------------

def test_roads_excludes_railway_and_sorts_alleys_last():
    features = [
        _line([[-113.4950, 53.54245], [-113.4930, 53.54245]], {
            "centerline_type": "Road", "functional_class_code": "Local-Residential",
            "street_name_full": "104 Avenue NW", "road_segment_type_description": "Local",
        }),
        _line([[-113.4950, 53.54135], [-113.4930, 53.54135]], {
            "centerline_type": "Alley", "functional_class_code": None,
            "street_name_full": None, "road_segment_type_description": None,
        }),
        _line([[-113.4950, 53.5440], [-113.4930, 53.5440]], {
            "centerline_type": "Railway", "functional_class_code": None,
            "street_name_full": None,
        }),
    ]
    facts, warnings = transforms.roads(features, SITE)

    assert "Local-Residential" in facts["mobility.road_hierarchy"]
    assert "Alley" in facts["mobility.road_hierarchy"]
    assert not any("Railway" in k for k in facts["mobility.road_hierarchy"])
    assert facts["mobility.frontage_streets"][0]["name"] == "104 Avenue NW"
    assert facts["site.corner_site"] is False  # one named frontage only
    assert not warnings


# --- transit / overlays / parks / trees --------------------------------------------

def test_transit_stops_counts_and_nearest():
    features = [
        _point(-113.4925, 53.5420, {"stop_name": "104 St / Jasper Ave", "location_type": 0}),
    ]
    facts, _ = transforms.transit_stops(features, SITE)
    assert facts["mobility.transit_stops_400m"] == 1
    assert facts["mobility.transit_stops_800m"] == 1
    assert facts["mobility.nearest_transit"]["stop_name"] == "104 St / Jasper Ave"


def test_zoning_overlays_lists_and_dedupes():
    features = [
        _poly(-113.4960, 53.5410, -113.4920, 53.5430, {
            "overlay_code": "PGA", "overlay_descr": "Priority Growth Area Rezoning",
            "bylaw_no": "20001", "special_area": False,
        }),
        _poly(-113.4955, 53.5412, -113.4925, 53.5428, {
            "overlay_code": "PGA", "overlay_descr": "Priority Growth Area Rezoning",
            "bylaw_no": "20001", "special_area": False,
        }),
    ]
    facts, warnings = transforms.zoning_overlays(features, SITE)
    assert len(facts["land_use.overlays"]) == 1
    assert facts["land_use.overlays"][0]["code"] == "PGA"
    assert not warnings


def test_zoning_overlays_empty_is_informational():
    facts, warnings = transforms.zoning_overlays([], SITE)
    assert facts["land_use.overlays"] == []
    assert any(w["code"] == "NO_ZONING_OVERLAYS" for w in warnings)


def test_parks_walkshed_and_nearest():
    features = [
        _poly(-113.4890, 53.5415, -113.4870, 53.5424, {
            "official_name": "Test Park", "type": "District Park", "status": "Open",
        }),
    ]
    facts, _ = transforms.parks(features, SITE)
    assert facts["public_realm.parks_within_800m"] == 1
    assert facts["public_realm.nearest_park"]["name"] == "Test Park"
    assert 150 < facts["public_realm.nearest_park"]["distance_m"] < 450


def test_trees_count_and_empty():
    features = [
        _point(-113.4940, 53.5418, {"species": "Green Ash"}),
        _point(-113.4931, 53.5420, {"species": "Bur Oak"}),  # ~13m east of the site
    ]
    facts, _ = transforms.trees(features, SITE)
    assert facts["public_realm.street_tree_count_150m"] == 2

    facts_empty, warnings = transforms.trees([], SITE)
    assert facts_empty["public_realm.street_tree_count_150m"] == 0
    assert any(w["code"] == "TREES_EMPTY" for w in warnings)
