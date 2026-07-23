"""Calgary dataset transforms — verified Socrata rows -> normalized DNA facts.

Each function matches the DatasetSpec.transform signature:
    (features, site_polygon_wgs84) -> (facts keyed by DNA field path, warnings)

Column names come from scripts/verify_calgary_datasets.py output (2026-07-05),
NOT from memory. If Calgary renames a column the transform degrades to fewer
facts + a warning; it never raises (base.py guards regardless).
"""

from __future__ import annotations

import logging
from collections import Counter
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


# --- 1. Land Use Districts (qe6k-p9nh) --------------------------------------
# Columns: lu_bylaw, lu_code, label, description, major, generalize, dc_bylaw,
#          dc_site_no, density, height, far, multipolygon

def land_use_districts(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    site_coverage = se.coverage_by(frame, features, lambda f: _props(f).get("lu_code"))
    if not site_coverage:
        warnings.append(note("LAND_USE_EMPTY", "No land use districts intersect the site boundary."))
        return {}, warnings

    by_code: dict[str, dict[str, Any]] = {}
    for feature in features:
        props = _props(feature)
        code = props.get("lu_code")
        if not code or code not in site_coverage or code in by_code:
            continue
        by_code[code] = {
            "code": code,
            "label": props.get("label"),
            "description": (props.get("description") or "")[:280],
            "major": props.get("major"),
            "generalized": props.get("generalize"),
            "bylaw": props.get("lu_bylaw"),
            "dc_bylaw": props.get("dc_bylaw"),
            "dc_site_no": props.get("dc_site_no"),
            "density": _num(props.get("density")),
            "height_m": _num(props.get("height")),
            "far": _num(props.get("far")),
            "area_pct_of_site": site_coverage[code]["pct"],
        }

    districts = sorted(by_code.values(), key=lambda d: d["area_pct_of_site"], reverse=True)
    dominant = districts[0]

    adjacent = se.coverage_by(
        frame, features, lambda f: _props(f).get("major"), zone_m=se.ring_m(frame, 200.0)
    )
    adjacent_uses = {key: entry["pct"] for key, entry in sorted(adjacent.items(), key=lambda kv: -kv[1]["pct"])}

    majors_on_site = {d["major"] for d in districts if d["major"]}
    if any(d["dc_bylaw"] for d in districts):
        warnings.append(
            note(
                "DIRECT_CONTROL_DISTRICT",
                "Site includes a Direct Control (DC) district — rules are bespoke to its bylaw; "
                "standard district assumptions may not apply.",
                severity="info",
            )
        )

    facts = {
        "land_use.districts": districts,
        "land_use.dominant_district": dominant["code"],
        "land_use.far_assumption": dominant["far"],
        "land_use.height_assumption_m": dominant["height_m"],
        "land_use.density_assumption": dominant["density"],
        "land_use.adjacent_uses": adjacent_uses,
        "land_use.mixed_use_opportunity": len(majors_on_site) > 1,
    }
    return facts, warnings


# --- 2. Parcels / Current Year Property Assessments (4bsw-nn7w) --------------
# Columns: roll_number, address, assessed_value, assessment_class(_description),
#          comm_code, comm_name, year_of_construction, land_use_designation,
#          property_type, land_size_sm, sub_property_use, multipolygon

def parcels(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    on_site = se.intersecting(frame, features, min_overlap_m2=20.0)
    if not on_site:
        warnings.append(note("PARCELS_EMPTY", "No assessment parcels intersect the site boundary."))
        return {}, warnings

    records = []
    for feature, overlap_m2 in on_site:
        props = _props(feature)
        records.append(
            {
                "roll_number": props.get("roll_number"),
                "address": props.get("address"),
                "assessment_class": props.get("assessment_class_description") or props.get("assessment_class"),
                "land_use_designation": props.get("land_use_designation"),
                "property_type": props.get("property_type"),
                "sub_property_use": props.get("sub_property_use"),
                "land_size_sm": _num(props.get("land_size_sm")),
                "year_of_construction": _num(props.get("year_of_construction")),
                "assessed_value": _num(props.get("assessed_value")),
                "overlap_m2": round(overlap_m2, 1),
            }
        )

    parcel_count = len(records)
    classes = {r["assessment_class"] for r in records if r["assessment_class"]}
    if parcel_count == 1:
        assembly_risk = "low"
        rationale = "single parcel"
    elif parcel_count <= 4:
        assembly_risk = "medium"
        rationale = f"{parcel_count} parcels to assemble"
    else:
        assembly_risk = "high"
        rationale = f"{parcel_count} parcels to assemble"
    if len(classes) > 1:
        assembly_risk = "high" if assembly_risk != "low" else "medium"
        rationale += f"; mixed assessment classes ({', '.join(sorted(classes))})"

    communities = Counter(
        _props(f).get("comm_name") for f, _ in on_site if _props(f).get("comm_name")
    )
    years = [r["year_of_construction"] for r in records if r["year_of_construction"] and r["year_of_construction"] > 1800]

    facts = {
        "site.parcel_count": parcel_count,
        "site.parcels": records[:50],
        "site.assembly_risk": {"level": assembly_risk, "rationale": rationale},
        "site.community_name": communities.most_common(1)[0][0] if communities else None,
        "built_form.site_year_built_mean": round(sum(years) / len(years)) if years else None,
    }
    return facts, warnings


# --- 3. Policy Plan Boundaries (yi6d-a7q5) -----------------------------------
# Columns: plan_type, name, status, doc_name, app_date, modified_dt, multipolygon

def policy_plans(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    hits = se.intersecting(frame, features, min_overlap_m2=1.0)
    plans = []
    for feature, _ in hits:
        props = _props(feature)
        plans.append(
            {
                "plan_type": props.get("plan_type"),
                "name": props.get("name"),
                "status": props.get("status"),
                "document": props.get("doc_name"),
                "approved_date": props.get("app_date"),
            }
        )

    lap_name = None
    for plan in plans:
        plan_type = (plan["plan_type"] or "").lower()
        if "local area" in plan_type:
            lap_name = plan["name"]
            break
    if lap_name is None:
        for plan in plans:
            if "redevelopment" in (plan["plan_type"] or "").lower():
                lap_name = plan["name"]
                break

    if not plans:
        warnings.append(
            note(
                "NO_POLICY_PLAN",
                "No statutory policy plan boundary covers this site — citywide policies (MDP) still apply.",
                severity="info",
            )
        )

    facts = {
        "policy.applicable_plans": plans,
        "land_use.lap_name": lap_name,
    }
    return facts, warnings


# --- 4. Street Centreline (4dx8-rtm5) ----------------------------------------
# Columns: segment_id, full_name, name, street_type, octant, one_way,
#          built_status, plan_status, ctp_class, ownership, line

def roads(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    built = [f for f in features if (_props(f).get("built_status") or "").upper() != "PROPOSED"]
    if not built:
        warnings.append(note("ROADS_EMPTY", "No built street centrelines found near the site."))
        return {}, warnings

    hierarchy = se.length_within_by(
        frame, built, lambda f: _props(f).get("ctp_class") or "Unclassified", radius_m=200.0
    )

    fronting = se.frontage(frame, built, tolerance_m=25.0)
    seen_names: set[str] = set()
    frontage_streets = []
    for feature, shared_m in fronting:
        props = _props(feature)
        name = props.get("full_name") or props.get("name") or "unnamed"
        if name in seen_names:
            continue
        seen_names.add(name)
        frontage_streets.append(
            {
                "name": name,
                "ctp_class": props.get("ctp_class"),
                "street_type": props.get("street_type"),
                "one_way": props.get("one_way"),
                "frontage_m": shared_m,
            }
        )
    # Named streets before unnamed lanes/alleys — agents read the top entries.
    frontage_streets.sort(
        key=lambda s: (s["name"] == "unnamed" or (s["ctp_class"] or "") == "Lanes (Alleys)", -s["frontage_m"])
    )

    named_frontages = [s for s in frontage_streets if s["name"] != "unnamed"]

    facts = {
        "mobility.road_hierarchy": hierarchy,
        "mobility.frontage_streets": frontage_streets[:12],
        "site.corner_site": len(named_frontages) >= 2,
    }
    return facts, warnings


# --- 6. Calgary Bikeways (jjqk-9b73) ------------------------------------------
# Columns: status, type, bicycle_class, length, comfort_level, multilinestring

def bikeways(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    active = [f for f in features if (_props(f).get("status") or "").upper() not in ("REMOVED", "INACTIVE")]
    if not active:
        warnings.append(note("BIKEWAYS_EMPTY", "No bikeways within 800m of the site.", severity="info"))
        return {"mobility.bike_network_m_800m": {}, "mobility.bike_frontage": []}, warnings

    network = se.length_within_by(
        frame, active, lambda f: _props(f).get("bicycle_class") or _props(f).get("type") or "Unclassified",
        radius_m=800.0,
    )
    fronting = se.frontage(frame, active, tolerance_m=25.0)
    bike_frontage = []
    seen: set[str] = set()
    for feature, shared_m in fronting:
        props = _props(feature)
        key = f"{props.get('bicycle_class')}|{props.get('type')}"
        if key in seen:
            continue
        seen.add(key)
        bike_frontage.append({
            "bicycle_class": props.get("bicycle_class"),
            "type": props.get("type"),
            "comfort_level": props.get("comfort_level"),
            "frontage_m": shared_m,
        })

    facts = {
        "mobility.bike_network_m_800m": network,
        "mobility.bike_frontage": bike_frontage[:8],
    }
    return facts, warnings


# --- 7. Parks Pathways (qndb-27qm) ---------------------------------------------
# Columns: asset_class, asset_type, the_geom (multiline), life_cycle_status, ...

def pathways(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    if not features:
        warnings.append(note("PATHWAYS_EMPTY", "No park pathways within 800m of the site.", severity="info"))
        return {"mobility.pathway_m_800m": 0.0, "public_realm.nearest_pathway": None}, warnings

    totals = se.length_within_by(frame, features, lambda f: "pathway", radius_m=800.0)
    nearest = se.nearest(frame, features, k=1)
    nearest_fact = None
    if nearest:
        distance_m, feature = nearest[0]
        nearest_fact = {
            "asset_type": _props(feature).get("asset_type"),
            "distance_m": round(distance_m, 1),
            "network_estimate_m": se.network_distance_estimate_m(distance_m),
            "method": se.DISTANCE_METHOD,
        }

    facts = {
        "mobility.pathway_m_800m": totals.get("pathway", 0.0),
        "public_realm.nearest_pathway": nearest_fact,
    }
    return facts, warnings


# --- 8. Parks Sites (kami-qbfh) --------------------------------------------------
# Columns: site_name, the_geom (multipolygon), planning_category, type_description, ...

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
        nearest_fact = {
            "name": _props(feature).get("site_name"),
            "category": _props(feature).get("planning_category") or _props(feature).get("type_description"),
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


# --- 9. 3D Buildings - Citywide (cchr-krqg) --------------------------------------
# Columns: grd_elev_min_z, grd_elev_max_z, rooftop_elev_z, stage, struct_id, polygon
# Heights are LiDAR-derived: rooftop_elev_z - grd_elev_min_z.

def buildings_3d(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    if not features:
        warnings.append(note("BUILDINGS_EMPTY", "No building models within the fetch envelope.", severity="info"))
        return {}, warnings

    heights: list[float] = []
    ground_elevations: list[float] = []
    for feature in features:
        props = _props(feature)
        roof = _num(props.get("rooftop_elev_z"))
        ground_min = _num(props.get("grd_elev_min_z"))
        ground_max = _num(props.get("grd_elev_max_z"))
        if roof is not None and ground_min is not None and roof > ground_min:
            heights.append(roof - ground_min)
        for elevation in (ground_min, ground_max):
            if elevation is not None and elevation > 0:
                ground_elevations.append(elevation)

    on_site = se.intersecting(frame, features, min_overlap_m2=5.0)
    site_coverage_pct = round(
        100.0 * sum(overlap for _, overlap in on_site) / frame.area_m2, 1
    ) if frame.area_m2 else None

    ground_range = None
    if ground_elevations:
        ground_range = {
            "min_m": round(min(ground_elevations), 1),
            "max_m": round(max(ground_elevations), 1),
            "range_m": round(max(ground_elevations) - min(ground_elevations), 1),
            "method": "lidar_building_ground_elevations",
        }

    facts = {
        "built_form.context_building_count": se.count_within(frame, features, 200.0),
        "built_form.context_avg_height_m": round(sum(heights) / len(heights), 1) if heights else None,
        "built_form.context_max_height_m": round(max(heights), 1) if heights else None,
        "built_form.site_coverage_pct": site_coverage_pct,
        "environment.ground_elevation": ground_range,
    }
    return facts, warnings


# --- 5. Calgary Transit Stops (muzh-c9qc) ------------------------------------
# Columns: teleride_number, stop_name, status, point

def transit_stops(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    active = [
        f for f in features
        if (_props(f).get("status") or "ACTIVE").upper() not in ("INACTIVE", "CLOSED", "REMOVED")
    ]
    if not active:
        warnings.append(note("TRANSIT_EMPTY", "No transit stops found within the fetch envelope."))
        return {}, warnings

    nearest = se.nearest(frame, active, k=1)
    nearest_fact = None
    if nearest:
        distance_m, feature = nearest[0]
        nearest_fact = {
            "stop_name": _props(feature).get("stop_name"),
            "distance_m": round(distance_m, 1),
            "network_estimate_m": se.network_distance_estimate_m(distance_m),
            "method": se.DISTANCE_METHOD,
        }

    facts = {
        "mobility.transit_stops_400m": se.count_within(frame, active, 400.0),
        "mobility.transit_stops_800m": se.count_within(frame, active, 800.0),
        "mobility.nearest_transit": nearest_fact,
    }
    return facts, warnings
