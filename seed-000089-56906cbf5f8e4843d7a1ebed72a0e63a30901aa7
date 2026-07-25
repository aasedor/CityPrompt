"""Edmonton city connector — datasets 1-9 of the Edmonton integration order.

Resource ids and geometry column names below were VERIFIED against live
data.edmonton.ca metadata by scripts/verify_edmonton_datasets.py on 2026-07-11.
Never edit these from memory — re-run the script. Notable corrections vs the
research notes:
  - q7d6-ambg (assessed values) has NO queryable geometry column; dkk9-cj3x
    (Property Information) is the spatial property-point dataset and also
    carries zoning/lot_size/year_built. Assessed-value enrichment by
    account_number stays a designed stretch.
  - The road network is 9j8t-zm52 ("Road Network"), discovered via catalog
    search — there is no "street centreline" dataset.
  - On point datasets the Socrata `location`-typed column 400s on intersects();
    the verified queryable column is `geometry_point`.
  - Edmonton publishes NO parcel polygons (AltaLIS/commercial since Nov 2021)
    and its building footprints (6n9r-ddf8) froze in 2017 — building context
    comes from OSM instead.
Verified-available stretch datasets (#10+): development permits 2ccn-pwtu,
heritage register jgsn-dhai, bike routes vd4b-a4iv.

Adding dataset #10+: append one DatasetSpec literal here + one transform in
transforms.py. Nothing else changes.
"""

from __future__ import annotations

from app.services.city_connector.base import CityConnector, DatasetSpec
from app.services.city_connector.cities import osm_fallback
from app.services.city_connector.cities.edmonton import transforms

SOCRATA_DOMAIN = "data.edmonton.ca"


class EdmontonConnector(CityConnector):
    city_id = "edmonton"
    display_name = "Edmonton, AB"


EdmontonConnector.register(
    DatasetSpec(
        id="edmonton.zoning",
        name="Zoning Bylaw Geographical Data (Bylaw 20001)",
        priority=1,
        geometry_type="polygon",
        refresh_days=7,
        source_url="https://data.edmonton.ca/Urban-Planning-Economy/Zoning-Bylaw-Geographical-Data/fixa-tstc",
        api_endpoint="fixa-tstc",
        adapter="socrata",
        adapter_params={"domain": SOCRATA_DOMAIN, "geo_field": "geometry_multipolygon"},
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

EdmontonConnector.register(
    DatasetSpec(
        id="edmonton.parcels_info",
        name="Property Information (Current Calendar Year)",
        priority=2,
        geometry_type="point",
        refresh_days=30,
        source_url="https://data.edmonton.ca/City-Administration/Property-Information-Data-Current-Calendar-Year-/dkk9-cj3x",
        api_endpoint="dkk9-cj3x",
        adapter="socrata",
        adapter_params={"domain": SOCRATA_DOMAIN, "geo_field": "point_location"},
        dna_fields=(
            "site.parcel_count",
            "site.parcels",
            "site.assembly_risk",
            "built_form.site_year_built_mean",
        ),
        transform=transforms.parcel_points,
        buffer_m=30.0,
        confidence_weight=0.6,  # address points, not parcel fabric
    )
)

EdmontonConnector.register(
    DatasetSpec(
        id="edmonton.neighbourhoods",
        name="Neighbourhoods (current, with District)",
        priority=3,
        geometry_type="polygon",
        refresh_days=60,
        source_url="https://data.edmonton.ca/Geospatial-Boundaries/City-of-Edmonton-Neighbourhoods/65fr-66s6",
        api_endpoint="65fr-66s6",
        adapter="socrata",
        adapter_params={"domain": SOCRATA_DOMAIN, "geo_field": "geometry_multipolygon"},
        dna_fields=(
            "site.community_name",
            "land_use.lap_name",
            "policy.applicable_plans",
        ),
        transform=transforms.neighbourhoods,
        buffer_m=10.0,
        confidence_weight=0.8,
    )
)

EdmontonConnector.register(
    DatasetSpec(
        id="edmonton.roads",
        name="Road Network",
        priority=4,
        geometry_type="line",
        refresh_days=30,
        source_url="https://data.edmonton.ca/Transportation/Road-Network/9j8t-zm52",
        api_endpoint="9j8t-zm52",
        adapter="socrata",
        adapter_params={"domain": SOCRATA_DOMAIN, "geo_field": "geometry"},
        dna_fields=(
            "mobility.road_hierarchy",
            "mobility.frontage_streets",
            "site.corner_site",
        ),
        transform=transforms.roads,
        buffer_m=220.0,
        confidence_weight=1.0,
    )
)

EdmontonConnector.register(
    DatasetSpec(
        id="edmonton.transit_stops",
        name="ETS Transit Stops (GTFS)",
        priority=5,
        geometry_type="point",
        refresh_days=14,
        source_url="https://data.edmonton.ca/Transit/ETS-Bus-Schedule-GTFS-Data-Feed-Stops/4vt2-8zrq",
        api_endpoint="4vt2-8zrq",
        adapter="socrata",
        adapter_params={"domain": SOCRATA_DOMAIN, "geo_field": "geometry_point"},
        dna_fields=(
            "mobility.transit_stops_400m",
            "mobility.transit_stops_800m",
            "mobility.nearest_transit",
        ),
        transform=transforms.transit_stops,
        buffer_m=850.0,  # envelope must cover the 800m walkshed
        confidence_weight=0.9,
    )
)

EdmontonConnector.register(
    DatasetSpec(
        id="edmonton.zoning_overlays",
        name="Zoning Overlays",
        priority=6,
        geometry_type="polygon",
        refresh_days=30,
        source_url="https://data.edmonton.ca/Urban-Planning-Economy/Zoning-Overlays/6w3s-58pv",
        api_endpoint="6w3s-58pv",
        adapter="socrata",
        adapter_params={"domain": SOCRATA_DOMAIN, "geo_field": "geometry_multipolygon"},
        dna_fields=("land_use.overlays",),
        transform=transforms.zoning_overlays,
        buffer_m=220.0,
        confidence_weight=0.7,
    )
)

EdmontonConnector.register(
    DatasetSpec(
        id="edmonton.parks",
        name="Parks",
        priority=7,
        geometry_type="polygon",
        refresh_days=60,
        source_url="https://data.edmonton.ca/Outdoor-Recreation/Parks/gdd9-eqv9",
        api_endpoint="gdd9-eqv9",
        adapter="socrata",
        adapter_params={"domain": SOCRATA_DOMAIN, "geo_field": "geometry_multipolygon"},
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

EdmontonConnector.register(
    DatasetSpec(
        id="edmonton.trees",
        name="Trees (city-owned)",
        priority=8,
        geometry_type="point",
        refresh_days=30,
        source_url="https://data.edmonton.ca/Environmental-Services/Trees/eecg-fc54",
        api_endpoint="eecg-fc54",
        adapter="socrata",
        adapter_params={"domain": SOCRATA_DOMAIN, "geo_field": "geometry_point"},
        dna_fields=("public_realm.street_tree_count_150m",),
        transform=transforms.trees,
        buffer_m=150.0,
        confidence_weight=0.6,
    )
)

EdmontonConnector.register(
    DatasetSpec(
        id="edmonton.buildings",
        name="OSM Buildings (Edmonton footprints froze in 2017)",
        priority=9,
        geometry_type="polygon",
        refresh_days=30,
        source_url="https://www.openstreetmap.org",
        api_endpoint="overpass",
        adapter="osm",
        adapter_params={"category": "buildings"},
        dna_fields=("built_form.context_building_count", "built_form.context_avg_height_m"),
        # Same normalization as the fallback connector — OSM features are
        # city-agnostic by construction.
        transform=osm_fallback._buildings,  # noqa: SLF001
        buffer_m=220.0,
        confidence_weight=0.6,
        timeout_s=90.0,  # covers queueing behind sibling Overpass queries + one 429 retry
    )
)
