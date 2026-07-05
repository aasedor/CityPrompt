"""Calgary city connector — V1 datasets 1-5 of the 18-dataset integration order.

Resource ids and geometry column names below were VERIFIED against live
data.calgary.ca metadata by scripts/verify_calgary_datasets.py on 2026-07-05.
Never edit these from memory — re-run the script. Notable correction: the Land
Use Districts spatial dataset is qe6k-p9nh (the previously-researched
mw9j-jik5 has no geometry columns).

Adding dataset #6+: append one DatasetSpec literal here + one transform in
transforms.py. Nothing else changes.
"""

from __future__ import annotations

from app.services.city_connector.base import CityConnector, DatasetSpec
from app.services.city_connector.cities.calgary import transforms

SOCRATA_DOMAIN = "data.calgary.ca"


class CalgaryConnector(CityConnector):
    city_id = "calgary"
    display_name = "Calgary, AB"


CalgaryConnector.register(
    DatasetSpec(
        id="calgary.land_use_districts",
        name="Land Use Districts (Bylaw 1P2007)",
        priority=1,
        geometry_type="polygon",
        refresh_days=7,
        source_url="https://data.calgary.ca/Base-Maps/Land-Use-Districts/qe6k-p9nh",
        api_endpoint="qe6k-p9nh",
        adapter="socrata",
        adapter_params={"domain": SOCRATA_DOMAIN, "geo_field": "multipolygon"},
        dna_fields=(
            "land_use.districts",
            "land_use.dominant_district",
            "land_use.far_assumption",
            "land_use.height_assumption_m",
            "land_use.density_assumption",
            "land_use.adjacent_uses",
            "land_use.mixed_use_opportunity",
        ),
        transform=transforms.land_use_districts,
        buffer_m=220.0,  # fetch envelope must cover the 200m adjacency ring
        confidence_weight=1.0,
    )
)

CalgaryConnector.register(
    DatasetSpec(
        id="calgary.parcels",
        name="Parcels (Current Year Property Assessments)",
        priority=2,
        geometry_type="polygon",
        refresh_days=30,
        source_url="https://data.calgary.ca/dataset/Current-Year-Property-Assessments-Parcel-/4bsw-nn7w",
        api_endpoint="4bsw-nn7w",
        adapter="socrata",
        adapter_params={"domain": SOCRATA_DOMAIN, "geo_field": "multipolygon"},
        dna_fields=(
            "site.parcel_count",
            "site.parcels",
            "site.assembly_risk",
            "site.community_name",
            "built_form.site_year_built_mean",
        ),
        transform=transforms.parcels,
        buffer_m=30.0,
        confidence_weight=0.9,
    )
)

CalgaryConnector.register(
    DatasetSpec(
        id="calgary.policy_plan_boundaries",
        name="Policy Plan Boundaries (ARP/ASP/LAP)",
        priority=3,
        geometry_type="polygon",
        refresh_days=30,
        source_url="https://data.calgary.ca/dataset/Policy-Plan-Boundaries/yi6d-a7q5",
        api_endpoint="yi6d-a7q5",
        adapter="socrata",
        adapter_params={"domain": SOCRATA_DOMAIN, "geo_field": "multipolygon"},
        dna_fields=(
            "policy.applicable_plans",
            "land_use.lap_name",
        ),
        transform=transforms.policy_plans,
        buffer_m=10.0,
        confidence_weight=0.8,
    )
)

CalgaryConnector.register(
    DatasetSpec(
        id="calgary.roads",
        name="Street Centreline",
        priority=4,
        geometry_type="line",
        refresh_days=30,
        source_url="https://data.calgary.ca/Transportation-Transit/Street-Centreline/4dx8-rtm5",
        api_endpoint="4dx8-rtm5",
        adapter="socrata",
        adapter_params={"domain": SOCRATA_DOMAIN, "geo_field": "line"},
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

CalgaryConnector.register(
    DatasetSpec(
        id="calgary.transit_stops",
        name="Calgary Transit Stops",
        priority=5,
        geometry_type="point",
        refresh_days=14,
        source_url="https://data.calgary.ca/Transportation-Transit/Calgary-Transit-Stops/muzh-c9qc",
        api_endpoint="muzh-c9qc",
        adapter="socrata",
        adapter_params={"domain": SOCRATA_DOMAIN, "geo_field": "point"},
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
