"""Vancouver city connector — datasets 1-10 of the Vancouver integration order.

Dataset slugs and field names below were VERIFIED against the live
opendata.vancouver.ca Explore v2.1 API by scripts/verify_vancouver_datasets.py
on 2026-07-11 (every geo dataset exposes `geom`; exports/geojson honours the
where filter; the property-tax-report IN(...) join returns live values).
Never edit these from memory — re-run the script. Notable findings:
  - property-tax-report holds MULTIPLE rows per parcel (report years x strata
    folios; one downtown parcel had 166 folios) — enrichment aggregates
    numerically server-side for the latest report_year and samples text fields
    (ODS StatAggregation rejects text columns).
  - The zoning layer carries codes/classifications only — no numeric FSR or
    height (district schedules are PDF-only; CD-1 rules live in per-site
    by-laws keyed by cd_1_number).
  - Transit is SkyTrain-only (22 stations); bus data is TransLink GTFS under a
    separate non-OGL licence. Roads and building context come from OSM
    (city footprints froze in 2015).
Verified-available stretch datasets (#11+): heritage-sites,
issued-building-permits, building-lines, development-cost-levy-dcl-areas.

Adding dataset #11+: append one DatasetSpec literal here + one transform in
transforms.py. Nothing else changes.
"""

from __future__ import annotations

from app.services.city_connector.base import CityConnector, DatasetSpec
from app.services.city_connector.cities import osm_fallback
from app.services.city_connector.cities.vancouver import transforms

ODS_DOMAIN = "opendata.vancouver.ca"


class VancouverConnector(CityConnector):
    city_id = "vancouver"
    display_name = "Vancouver, BC"


VancouverConnector.register(
    DatasetSpec(
        id="vancouver.zoning",
        name="Zoning Districts and Labels",
        priority=1,
        geometry_type="polygon",
        refresh_days=7,
        source_url="https://opendata.vancouver.ca/explore/dataset/zoning-districts-and-labels/",
        api_endpoint="zoning-districts-and-labels",
        adapter="opendatasoft",
        adapter_params={"domain": ODS_DOMAIN, "geo_field": "geom"},
        dna_fields=(
            "land_use.districts",
            "land_use.dominant_district",
            "land_use.far_assumption",
            "land_use.height_assumption_m",
            "land_use.density_assumption",
            "land_use.adjacent_uses",
            "land_use.mixed_use_opportunity",
        ),
        transform=transforms.zoning,
        buffer_m=220.0,  # fetch envelope must cover the 200m adjacency ring
        confidence_weight=1.0,
    )
)

VancouverConnector.register(
    DatasetSpec(
        id="vancouver.parcels",
        name="Property Parcels (+ tax report values)",
        priority=2,
        geometry_type="polygon",
        refresh_days=30,
        source_url="https://opendata.vancouver.ca/explore/dataset/property-parcel-polygons/",
        api_endpoint="property-parcel-polygons",
        adapter="opendatasoft",
        adapter_params={
            "domain": ODS_DOMAIN,
            "geo_field": "geom",
            # Weekly assessment roll; joins parcels via tax_coord<->land_coordinate.
            # Aggregations are numeric-only (ODS rejects text); year_built and
            # zoning are text -> sampled from raw rows instead.
            "enrich": {
                "dataset": "property-tax-report",
                "local_key": "tax_coord",
                "remote_key": "land_coordinate",
                "prefix": "tax_",
                "latest_field": "report_year",
                "aggregations": (
                    "count(*) as folio_count, "
                    "sum(current_land_value) as land_value_total, "
                    "sum(current_improvement_value) as improvement_value_total"
                ),
                "sample_fields": ["year_built", "zoning_district"],
                "batch_size": 40,
                "max_keys": 300,
            },
        },
        dna_fields=(
            "site.parcel_count",
            "site.parcels",
            "site.assembly_risk",
            "built_form.site_year_built_mean",
        ),
        transform=transforms.parcels,
        buffer_m=30.0,
        confidence_weight=0.9,
    )
)

VancouverConnector.register(
    DatasetSpec(
        id="vancouver.local_areas",
        name="Local Area Boundaries",
        priority=3,
        geometry_type="polygon",
        refresh_days=180,
        source_url="https://opendata.vancouver.ca/explore/dataset/local-area-boundary/",
        api_endpoint="local-area-boundary",
        adapter="opendatasoft",
        adapter_params={"domain": ODS_DOMAIN, "geo_field": "geom"},
        dna_fields=("site.community_name",),
        transform=transforms.local_areas,
        buffer_m=10.0,
        confidence_weight=0.8,
    )
)

VancouverConnector.register(
    DatasetSpec(
        id="vancouver.roads",
        name="OSM Roads (no city centreline dataset)",
        priority=4,
        geometry_type="line",
        refresh_days=30,
        source_url="https://www.openstreetmap.org",
        api_endpoint="overpass",
        adapter="osm",
        adapter_params={"category": "roads"},
        dna_fields=("mobility.road_hierarchy", "mobility.frontage_streets", "site.corner_site"),
        transform=osm_fallback._roads,  # noqa: SLF001 — city-agnostic OSM normalization
        buffer_m=220.0,
        confidence_weight=0.8,
        timeout_s=90.0,  # covers queueing behind sibling Overpass queries + one 429 retry
    )
)

VancouverConnector.register(
    DatasetSpec(
        id="vancouver.rapid_transit",
        name="Rapid Transit Stations (SkyTrain)",
        priority=5,
        geometry_type="point",
        refresh_days=60,
        source_url="https://opendata.vancouver.ca/explore/dataset/rapid-transit-stations/",
        api_endpoint="rapid-transit-stations",
        adapter="opendatasoft",
        adapter_params={"domain": ODS_DOMAIN, "geo_field": "geom"},
        dna_fields=(
            "mobility.transit_stops_400m",
            "mobility.transit_stops_800m",
            "mobility.nearest_transit",
        ),
        transform=transforms.rapid_transit,
        buffer_m=850.0,  # envelope must cover the 800m walkshed / TOA tier
        confidence_weight=0.7,  # SkyTrain-only; bus network is out of scope
    )
)

VancouverConnector.register(
    DatasetSpec(
        id="vancouver.parks",
        name="Parks (polygon representation)",
        priority=6,
        geometry_type="polygon",
        refresh_days=60,
        source_url="https://opendata.vancouver.ca/explore/dataset/parks-polygon-representation/",
        api_endpoint="parks-polygon-representation",
        adapter="opendatasoft",
        adapter_params={"domain": ODS_DOMAIN, "geo_field": "geom"},
        dna_fields=(
            "public_realm.parks_within_800m",
            "public_realm.park_area_800m_ha",
            "public_realm.nearest_park",
        ),
        transform=transforms.parks,
        buffer_m=850.0,
        confidence_weight=1.0,
    )
)

VancouverConnector.register(
    DatasetSpec(
        id="vancouver.buildings",
        name="OSM Buildings (city footprints froze in 2015)",
        priority=7,
        geometry_type="polygon",
        refresh_days=30,
        source_url="https://www.openstreetmap.org",
        api_endpoint="overpass",
        adapter="osm",
        adapter_params={"category": "buildings"},
        dna_fields=("built_form.context_building_count", "built_form.context_avg_height_m"),
        transform=osm_fallback._buildings,  # noqa: SLF001 — city-agnostic OSM normalization
        buffer_m=220.0,
        confidence_weight=0.6,
        timeout_s=90.0,
    )
)

VancouverConnector.register(
    DatasetSpec(
        id="vancouver.floodplain",
        name="Designated Floodplain (incl. 2100 SLR scenario)",
        priority=8,
        geometry_type="polygon",
        refresh_days=180,
        source_url="https://opendata.vancouver.ca/explore/dataset/designated-floodplain/",
        api_endpoint="designated-floodplain",
        adapter="opendatasoft",
        adapter_params={"domain": ODS_DOMAIN, "geo_field": "geom"},
        dna_fields=("environment.flood_risk",),
        transform=transforms.floodplain,
        buffer_m=50.0,
        confidence_weight=0.9,
    )
)

VancouverConnector.register(
    DatasetSpec(
        id="vancouver.trees",
        name="Public Trees",
        priority=9,
        geometry_type="point",
        refresh_days=30,
        source_url="https://opendata.vancouver.ca/explore/dataset/public-trees/",
        api_endpoint="public-trees",
        adapter="opendatasoft",
        adapter_params={"domain": ODS_DOMAIN, "geo_field": "geom"},
        dna_fields=("public_realm.street_tree_count_150m",),
        transform=transforms.trees,
        buffer_m=150.0,
        confidence_weight=0.6,
    )
)

VancouverConnector.register(
    DatasetSpec(
        id="vancouver.view_cones",
        name="View Cones (protected view corridors)",
        priority=10,
        geometry_type="polygon",
        refresh_days=180,
        source_url="https://opendata.vancouver.ca/explore/dataset/view-cones/",
        api_endpoint="view-cones",
        adapter="opendatasoft",
        adapter_params={"domain": ODS_DOMAIN, "geo_field": "geom"},
        dna_fields=("built_form.view_cone_constraint",),
        transform=transforms.view_cones,
        buffer_m=10.0,
        confidence_weight=0.8,
    )
)
