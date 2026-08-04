"""Vancouver transform tests — canned ODS-shaped features -> DNA facts.

Geometry is a ~100m square in downtown Vancouver; features are hand-placed at
known metric offsets. Field names mirror scripts/verify_vancouver_datasets.py
output (2026-07-11).
"""

from shapely.geometry import Polygon

from app.services.city_connector.cities.vancouver import transforms

# ~110m x 100m site square (lon 0.0015 deg ~= 109m at 49.28N; lat 0.0009 ~= 100m)
SITE = Polygon(
    [
        (-123.1210, 49.2800),
        (-123.1195, 49.2800),
        (-123.1195, 49.2809),
        (-123.1210, 49.2809),
    ]
)


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


# --- zoning -------------------------------------------------------------------


def test_zoning_captures_cd1_and_stays_honest_about_rules():
    features = [
        _poly(
            -123.1212,
            49.2798,
            -123.1200,
            49.2811,
            {
                "zoning_district": "R1-1",
                "zoning_classification": "Residential Inclusive",
                "zoning_category": "R1-1",
                "cd_1_number": None,
            },
        ),
        _poly(
            -123.1200,
            49.2798,
            -123.1193,
            49.2811,
            {
                "zoning_district": "CD-1 (413)",
                "zoning_classification": "Comprehensive Development",
                "zoning_category": "CD-1",
                "cd_1_number": "413",
            },
        ),
        # Adjacent commercial ~90m east (inside the 200m ring)
        _poly(
            -123.1180,
            49.2800,
            -123.1165,
            49.2809,
            {
                "zoning_district": "C-3A",
                "zoning_classification": "Commercial",
                "zoning_category": "C-3A",
                "cd_1_number": None,
            },
        ),
    ]
    facts, warnings = transforms.zoning(features, SITE)

    codes = {d["code"] for d in facts["land_use.districts"]}
    assert codes == {"R1-1", "CD-1 (413)"}
    cd1 = next(d for d in facts["land_use.districts"] if d["cd_1_number"])
    assert cd1["cd_1_number"] == "413"
    assert facts["land_use.far_assumption"] is None
    assert facts["land_use.height_assumption_m"] is None
    assert facts["land_use.mixed_use_opportunity"] is True  # residential + comprehensive_development
    warning_codes = {w["code"] for w in warnings}
    assert "CD_1_DISTRICT" in warning_codes
    assert "DISTRICT_SCHEDULE_PDF" in warning_codes
    assert "commercial" in facts["land_use.adjacent_uses"]


# --- parcels -------------------------------------------------------------------


def test_parcels_reads_enriched_values_and_flags_strata():
    features = [
        _poly(
            -123.1208,
            49.2801,
            -123.1203,
            49.2808,
            {
                "civic_number": "1100",
                "streetname": "ROBSON ST",
                "tax_coord": "111",
                "tax_folio_count": 1,
                "tax_land_value_total": 5_000_000,
                "tax_improvement_value_total": 1_000_000,
                "tax_year_built": "1950",
                "tax_zoning_district": "DD",
            },
        ),
        _poly(
            -123.1202,
            49.2801,
            -123.1197,
            49.2808,
            {
                "civic_number": "1110",
                "streetname": "ROBSON ST",
                "tax_coord": "222",
                "tax_folio_count": 40,
                "tax_land_value_total": 60_000_000,
                "tax_improvement_value_total": 20_000_000,
                "tax_year_built": "1990",
                "tax_zoning_district": "DD",
            },
        ),
    ]
    facts, warnings = transforms.parcels(features, SITE)

    assert facts["site.parcel_count"] == 2
    assert facts["site.assembly_risk"]["level"] == "high"  # strata-titled parcel present
    assert "strata" in facts["site.assembly_risk"]["rationale"]
    assert facts["built_form.site_year_built_mean"] == 1970
    assert facts["site.parcels"][0]["land_value_total"] is not None
    assert not any(w["code"] == "VALUES_UNENRICHED" for w in warnings)


def test_parcels_unenriched_notes_missing_values():
    features = [
        _poly(
            -123.1208,
            49.2801,
            -123.1203,
            49.2808,
            {
                "civic_number": "1100",
                "streetname": "ROBSON ST",
                "tax_coord": "111",
            },
        ),
    ]
    facts, warnings = transforms.parcels(features, SITE)
    assert facts["site.parcel_count"] == 1
    assert facts["built_form.site_year_built_mean"] is None
    assert any(w["code"] == "VALUES_UNENRICHED" for w in warnings)


# --- local areas / transit / floodplain / view cones / trees ---------------------


def test_local_areas_dominant_name():
    features = [
        _poly(-123.1250, 49.2780, -123.1150, 49.2830, {"name": "Downtown"}),
    ]
    facts, warnings = transforms.local_areas(features, SITE)
    assert facts["site.community_name"] == "Downtown"
    assert not warnings


def test_rapid_transit_toa_tier_note():
    # Station ~150m east of the site edge -> inside the 200m TOA tier (20 storeys)
    features = [_point(-123.1174, 49.2804, {"station": "BURRARD"})]
    facts, warnings = transforms.rapid_transit(features, SITE)

    assert facts["mobility.transit_stops_400m"] == 1
    assert facts["mobility.nearest_transit"]["stop_name"] == "BURRARD"
    warning_codes = {w["code"] for w in warnings}
    assert "BUS_NETWORK_UNAVAILABLE" in warning_codes
    toa = next(w for w in warnings if w["code"] == "TOA_DENSITY_TIER")
    assert "20 storeys" in toa["message"]


def test_rapid_transit_empty_still_notes_bus_gap():
    facts, warnings = transforms.rapid_transit([], SITE)
    assert facts == {}
    warning_codes = {w["code"] for w in warnings}
    assert {"BUS_NETWORK_UNAVAILABLE", "TRANSIT_EMPTY"} <= warning_codes


def test_floodplain_inside_and_outside():
    inside = [
        _poly(
            -123.1250,
            49.2780,
            -123.1150,
            49.2830,
            {
                "name": "False Creek Flats",
                "description": "Coastal floodplain, 2100 SLR scenario",
            },
        ),
    ]
    facts, warnings = transforms.floodplain(inside, SITE)
    assert facts["environment.flood_risk"]["in_designated_floodplain"] is True
    assert any(w["code"] == "DESIGNATED_FLOODPLAIN" for w in warnings)

    facts_out, warnings_out = transforms.floodplain([], SITE)
    assert facts_out["environment.flood_risk"]["in_designated_floodplain"] is False
    assert not warnings_out


def test_view_cones_constraint():
    features = [
        _poly(
            -123.1250,
            49.2780,
            -123.1150,
            49.2830,
            {
                "view_cone_name": "Queen Elizabeth Park",
                "view_number": "3.1",
                "description": "Protected mountain view corridor",
            },
        ),
    ]
    facts, warnings = transforms.view_cones(features, SITE)
    assert facts["built_form.view_cone_constraint"]["under_view_cone"] is True
    assert facts["built_form.view_cone_constraint"]["cones"][0]["view_number"] == "3.1"
    assert any(w["code"] == "VIEW_CONE_CONSTRAINT" for w in warnings)

    facts_out, warnings_out = transforms.view_cones([], SITE)
    assert facts_out["built_form.view_cone_constraint"]["under_view_cone"] is False
    assert not warnings_out


def test_trees_count_and_empty():
    features = [
        _point(-123.1205, 49.2804, {"common_name": "Kwanzan Flowering Cherry"}),
        _point(-123.1193, 49.2805, {"common_name": "Red Maple"}),  # ~15m east of the site
    ]
    facts, _ = transforms.trees(features, SITE)
    assert facts["public_realm.street_tree_count_150m"] == 2

    facts_empty, warnings = transforms.trees([], SITE)
    assert facts_empty["public_realm.street_tree_count_150m"] == 0
    assert any(w["code"] == "TREES_EMPTY" for w in warnings)
