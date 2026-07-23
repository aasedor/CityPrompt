"""Edmonton dataset transforms — verified Socrata rows -> normalized DNA facts.

Each function matches the DatasetSpec.transform signature:
    (features, site_polygon_wgs84) -> (facts keyed by DNA field path, warnings)

Column names come from scripts/verify_edmonton_datasets.py output (2026-07-11),
NOT from memory. If Edmonton renames a column the transform degrades to fewer
facts + a warning; it never raises (base.py guards regardless).
"""

from __future__ import annotations

import logging
from collections import Counter
from datetime import date
from typing import Any

from shapely.geometry import Polygon

from app.services import spatial_engine as se
from app.services.city_connector.base import Feature, note

logger = logging.getLogger(__name__)


def _num(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _props(feature: Feature) -> dict[str, Any]:
    return feature.get("properties") or {}


# Bylaw 20001 publishes no "major"/general-use column, so zone families are
# derived from the code. Approximate on purpose — used only for the adjacency
# grouping and the mixed-use boolean, never as a regulation.
def _zone_family(code: str | None) -> str | None:
    if not code:
        return None
    code = code.upper()
    if code.startswith("DC"):
        return "direct_control"
    if code in ("MU",) or code.endswith("MU"):  # MU, CMU, RMU
        return "mixed_use"
    if code[0] in ("R", "H"):
        return "residential"
    if code[0] == "C":
        return "commercial"
    if code[0] == "I":
        return "industrial"
    if code[0] in ("P", "A", "N", "U"):
        return "parks_civic_open_space"
    return "other"


# --- 1. Zoning Bylaw Geographical Data (fixa-tstc) ----------------------------
# Columns: id, zoning, description, agreement_no, dc2_sub_area, date_ext, url,
#          geometry_multipolygon

def zoning(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    site_coverage = se.coverage_by(frame, features, lambda f: _props(f).get("zoning"))
    if not site_coverage:
        warnings.append(note("LAND_USE_EMPTY", "No zoning districts intersect the site boundary."))
        return {}, warnings

    by_code: dict[str, dict[str, Any]] = {}
    for feature in features:
        props = _props(feature)
        code = props.get("zoning")
        if not code or code not in site_coverage or code in by_code:
            continue
        by_code[code] = {
            "code": code,
            "label": props.get("description"),
            "family": _zone_family(code),
            # Every polygon deep-links to its zone's regulation page on
            # zoningbylaw.edmonton.ca — the citation hook for policy retrieval.
            "zone_page_url": props.get("url"),
            "dc2_sub_area": props.get("dc2_sub_area"),
            "agreement_no": props.get("agreement_no"),
            "area_pct_of_site": site_coverage[code]["pct"],
        }

    districts = sorted(by_code.values(), key=lambda d: d["area_pct_of_site"], reverse=True)
    dominant = districts[0]

    adjacent = se.coverage_by(
        frame, features, lambda f: _zone_family(_props(f).get("zoning")), zone_m=se.ring_m(frame, 200.0)
    )
    adjacent_uses = {key: entry["pct"] for key, entry in sorted(adjacent.items(), key=lambda kv: -kv[1]["pct"])}

    if any((d["code"] or "").startswith("DC") for d in districts):
        warnings.append(
            note(
                "DIRECT_CONTROL_PROVISION",
                "Site includes a Direct Control provision (DC1/DC2) — rules are bespoke to its "
                "provision (see zone_page_url); standard zone assumptions may not apply.",
                severity="info",
            )
        )
    # Bylaw 20001's spatial layer carries no numeric FAR/height/density columns
    # (verified 2026-07-11) — regulations live in the per-zone bylaw pages.
    warnings.append(
        note(
            "ZONE_RULES_IN_BYLAW",
            "Edmonton's zoning layer publishes zone codes but not numeric FAR/height/density — "
            "regulations are in each zone's Bylaw 20001 page (districts[].zone_page_url).",
            severity="info",
        )
    )

    developable_families = {"residential", "commercial", "mixed_use", "industrial"}
    families_on_site = {d["family"] for d in districts if d["family"] in developable_families}

    facts = {
        "land_use.districts": districts,
        "land_use.dominant_district": dominant["code"],
        "land_use.far_assumption": None,
        "land_use.height_assumption_m": None,
        "land_use.density_assumption": None,
        "land_use.adjacent_uses": adjacent_uses,
        "land_use.mixed_use_opportunity": len(families_on_site) > 1 or "mixed_use" in families_on_site,
    }
    return facts, warnings


# --- 2. Property Information (dkk9-cj3x) ---------------------------------------
# Columns: account_number, house_number, street_name, legal_description, zoning,
#          lot_size, total_gross_area, year_built, neighbourhood, point_location
# NOTE: these are address POINTS — Alberta parcel polygons moved to AltaLIS
# (commercial) in Nov 2021. q7d6-ambg (assessed values) has NO queryable
# geometry column (verified 2026-07-11), which is why this dataset is primary.

def parcel_points(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = [
        note(
            "PARCEL_GEOMETRY_UNAVAILABLE",
            "Edmonton publishes parcel address points, not parcel polygons (parcel fabric moved "
            "to AltaLIS in 2021) — parcel counts and assembly risk derive from points and carry "
            "reduced confidence.",
            severity="info",
        )
    ]

    on_site = se.intersecting(frame, features)
    if not on_site:
        warnings.append(note("PARCELS_EMPTY", "No property points fall inside the site boundary."))
        return {}, warnings

    records = []
    for feature, _ in on_site:
        props = _props(feature)
        house = props.get("house_number") or ""
        street = props.get("street_name") or ""
        records.append(
            {
                "account_number": props.get("account_number"),
                "address": f"{house} {street}".strip() or None,
                "legal_description": props.get("legal_description"),
                "zoning": props.get("zoning"),
                "lot_size_sm": _num(props.get("lot_size")),
                "year_built": _num(props.get("year_built")),
                "neighbourhood": props.get("neighbourhood"),
            }
        )

    parcel_count = len(records)
    zonings = {r["zoning"] for r in records if r["zoning"]}
    if parcel_count == 1:
        assembly_risk = "low"
        rationale = "single property"
    elif parcel_count <= 4:
        assembly_risk = "medium"
        rationale = f"{parcel_count} properties to assemble"
    else:
        assembly_risk = "high"
        rationale = f"{parcel_count} properties to assemble"
    if len(zonings) > 1:
        assembly_risk = "high" if assembly_risk != "low" else "medium"
        rationale += f"; mixed zoning ({', '.join(sorted(zonings))})"

    years = [r["year_built"] for r in records if r["year_built"] and r["year_built"] > 1800]

    facts = {
        "site.parcel_count": parcel_count,
        "site.parcels": records[:50],
        "site.assembly_risk": {"level": assembly_risk, "rationale": rationale},
        "built_form.site_year_built_mean": round(sum(years) / len(years)) if years else None,
    }
    return facts, warnings


# --- 3. Neighbourhoods (65fr-66s6) ----------------------------------------------
# Columns: name, neighbourhood_number, descriptive_name, description,
#          effective_start_date, effective_end_date, civic_ward_name, district,
#          geometry_multipolygon

def neighbourhoods(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    today = date.today().isoformat()
    current = [
        f for f in features
        if not (_props(f).get("effective_end_date") or "") or str(_props(f)["effective_end_date"])[:10] >= today
    ]
    coverage = se.coverage_by(frame, current, lambda f: _props(f).get("name"))
    if not coverage:
        warnings.append(note("NEIGHBOURHOOD_EMPTY", "No current neighbourhood polygon covers the site."))
        return {}, warnings

    dominant_name = max(coverage.items(), key=lambda kv: kv[1]["pct"])[0]
    dominant = next(f for f in current if _props(f).get("name") == dominant_name)
    props = _props(dominant)
    district = props.get("district")

    plans = []
    if district:
        # District Plans (adopted 2024-25) are statutory; boundaries via the
        # neighbourhood layer's district attribute — the retrieval key for the
        # policy corpus.
        plans.append(
            {
                "plan_type": "District Plan",
                "name": f"{district} District Plan",
                "status": "Adopted",
                "document": None,
                "approved_date": None,
            }
        )
    else:
        warnings.append(
            note(
                "NO_DISTRICT_PLAN",
                "No District Plan attribute on the covering neighbourhood — citywide policies "
                "(The City Plan) still apply.",
                severity="info",
            )
        )

    facts = {
        "site.community_name": props.get("descriptive_name") or dominant_name,
        "land_use.lap_name": f"{district} District Plan" if district else None,
        "policy.applicable_plans": plans,
    }
    return facts, warnings


# --- 4. Road Network (9j8t-zm52) -------------------------------------------------
# Columns: centerline_type (Road|Alley|Railway), functional_class_code,
#          street_name_full, street_name, road_segment_type_description, geometry
# Verified value distribution: functional_class_code is None for Alley/Railway.

def roads(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    def kind(feature: Feature) -> str:
        return (_props(feature).get("centerline_type") or "").title()

    drivable = [f for f in features if kind(f) in ("Road", "Alley")]
    if not drivable:
        warnings.append(note("ROADS_EMPTY", "No road centrelines found near the site."))
        return {}, warnings

    hierarchy = se.length_within_by(
        frame,
        drivable,
        lambda f: "Alley" if kind(f) == "Alley" else (_props(f).get("functional_class_code") or "Unclassified"),
        radius_m=200.0,
    )

    fronting = se.frontage(frame, drivable, tolerance_m=25.0)
    seen_names: set[str] = set()
    frontage_streets = []
    for feature, shared_m in fronting:
        props = _props(feature)
        name = props.get("street_name_full") or props.get("street_name") or "unnamed"
        if name in seen_names:
            continue
        seen_names.add(name)
        frontage_streets.append(
            {
                "name": name,
                "ctp_class": props.get("functional_class_code"),
                "street_type": props.get("road_segment_type_description"),
                "one_way": None,
                "frontage_m": shared_m,
            }
        )
    # Named streets before unnamed alleys — agents read the top entries.
    frontage_streets.sort(key=lambda s: (s["name"] == "unnamed", -s["frontage_m"]))

    named_frontages = [s for s in frontage_streets if s["name"] != "unnamed"]

    facts = {
        "mobility.road_hierarchy": hierarchy,
        "mobility.frontage_streets": frontage_streets[:12],
        "site.corner_site": len(named_frontages) >= 2,
    }
    return facts, warnings


# --- 5. ETS Transit Stops (4vt2-8zrq, GTFS) ---------------------------------------
# Columns: stop_id, stop_name, location_type (1 = station), geometry_point

def transit_stops(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    if not features:
        warnings.append(note("TRANSIT_EMPTY", "No transit stops found within the fetch envelope."))
        return {}, warnings

    nearest = se.nearest(frame, features, k=1)
    nearest_fact = None
    if nearest:
        distance_m, feature = nearest[0]
        props = _props(feature)
        nearest_fact = {
            "stop_name": props.get("stop_name"),
            "is_station": _num(props.get("location_type")) == 1,
            "distance_m": round(distance_m, 1),
            "network_estimate_m": se.network_distance_estimate_m(distance_m),
            "method": se.DISTANCE_METHOD,
        }

    facts = {
        "mobility.transit_stops_400m": se.count_within(frame, features, 400.0),
        "mobility.transit_stops_800m": se.count_within(frame, features, 800.0),
        "mobility.nearest_transit": nearest_fact,
    }
    return facts, warnings


# --- 6. Zoning Overlays (6w3s-58pv) -------------------------------------------------
# Columns: overlay_code, overlay_descr, bylaw_no, special_area, geometry_multipolygon

def zoning_overlays(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    hits = se.intersecting(frame, features, min_overlap_m2=1.0)
    overlays = []
    seen: set[str] = set()
    for feature, _ in hits:
        props = _props(feature)
        code = props.get("overlay_code") or props.get("overlay_descr") or "unknown"
        if code in seen:
            continue
        seen.add(code)
        overlays.append(
            {
                "code": props.get("overlay_code"),
                "description": props.get("overlay_descr"),
                "bylaw_no": props.get("bylaw_no"),
                "special_area": props.get("special_area"),
            }
        )

    if not overlays:
        warnings.append(
            note("NO_ZONING_OVERLAYS", "No zoning overlays apply to this site.", severity="info")
        )

    return {"land_use.overlays": overlays}, warnings


# --- 7. Parks (gdd9-eqv9) -------------------------------------------------------------
# Columns: official_name, common_name, status, type, class, area, geometry_multipolygon

def parks(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    if not features:
        warnings.append(note("PARKS_EMPTY", "No parks within 800m of the site.", severity="info"))
        return {}, warnings

    walkshed_area = se.coverage_by(
        frame, features, lambda f: "parks", zone_m=frame.site_m.buffer(800.0)
    )
    park_area_ha = round(walkshed_area.get("parks", {}).get("area_m2", 0.0) / 10_000.0, 2)

    nearest = se.nearest(frame, features, k=1)
    nearest_fact = None
    if nearest:
        distance_m, feature = nearest[0]
        props = _props(feature)
        nearest_fact = {
            "name": props.get("official_name") or props.get("common_name"),
            "category": props.get("type") or props.get("class"),
            "distance_m": round(distance_m, 1),
            "network_estimate_m": se.network_distance_estimate_m(distance_m),
            "method": se.DISTANCE_METHOD,
        }

    facts = {
        "public_realm.parks_within_800m": se.count_within(frame, features, 800.0),
        "public_realm.park_area_800m_ha": park_area_ha,
        "public_realm.nearest_park": nearest_fact,
    }
    return facts, warnings


# --- 8. Trees (eecg-fc54) ----------------------------------------------------------
# Columns: species, genus, diameter_breast_height, condition_percent, geometry_point
# NOTE: the `location` column (Socrata location type) 400s on intersects();
# geometry_point is the verified queryable column.

def trees(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    if not features:
        warnings.append(note("TREES_EMPTY", "No city-owned trees within 150m of the site.", severity="info"))
        return {"public_realm.street_tree_count_150m": 0}, warnings

    return {"public_realm.street_tree_count_150m": se.count_within(frame, features, 150.0)}, warnings
