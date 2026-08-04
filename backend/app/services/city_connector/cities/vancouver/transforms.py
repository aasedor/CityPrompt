"""Vancouver dataset transforms — verified Opendatasoft rows -> normalized DNA facts.

Each function matches the DatasetSpec.transform signature:
    (features, site_polygon_wgs84) -> (facts keyed by DNA field path, warnings)

Field names come from scripts/verify_vancouver_datasets.py output (2026-07-11),
NOT from memory. If Vancouver renames a field the transform degrades to fewer
facts + a warning; it never raises (base.py guards regardless).
"""

from __future__ import annotations

import logging
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


# The zoning layer groups districts via zoning_classification text (e.g.
# "Residential Inclusive", "Comprehensive Development"). Families derived from
# that text are approximate on purpose — used only for the adjacency grouping
# and the mixed-use boolean, never as a regulation.
def _zone_family(classification: str | None) -> str | None:
    if not classification:
        return None
    text = classification.lower()
    if "comprehensive" in text:
        return "comprehensive_development"
    if "residential" in text or "dwelling" in text:
        return "residential"
    if "commercial" in text:
        return "commercial"
    if "industrial" in text:
        return "industrial"
    if "agricultur" in text:
        return "agricultural"
    if "historic" in text:
        return "historic_area"
    return "other"


# --- 1. Zoning districts (zoning-districts-and-labels) -------------------------
# Fields: zoning_district (R1-1, CD-1 (413)...), zoning_classification,
#         zoning_category, cd_1_number, geom


def zoning(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    site_coverage = se.coverage_by(frame, features, lambda f: _props(f).get("zoning_district"))
    if not site_coverage:
        warnings.append(note("LAND_USE_EMPTY", "No zoning districts intersect the site boundary."))
        return {}, warnings

    by_code: dict[str, dict[str, Any]] = {}
    for feature in features:
        props = _props(feature)
        code = props.get("zoning_district")
        if not code or code not in site_coverage or code in by_code:
            continue
        by_code[code] = {
            "code": code,
            "label": props.get("zoning_classification"),
            "category": props.get("zoning_category"),
            "family": _zone_family(props.get("zoning_classification")),
            # CD-1 by-law number — keys the future per-site by-law retrieval.
            "cd_1_number": props.get("cd_1_number"),
            "area_pct_of_site": site_coverage[code]["pct"],
        }

    districts = sorted(by_code.values(), key=lambda d: d["area_pct_of_site"], reverse=True)
    dominant = districts[0]

    adjacent = se.coverage_by(
        frame,
        features,
        lambda f: _zone_family(_props(f).get("zoning_classification")),
        zone_m=se.ring_m(frame, 200.0),
    )
    adjacent_uses = {key: entry["pct"] for key, entry in sorted(adjacent.items(), key=lambda kv: -kv[1]["pct"])}

    if any(d["cd_1_number"] or d["family"] == "comprehensive_development" for d in districts):
        warnings.append(
            note(
                "CD_1_DISTRICT",
                "Site includes a Comprehensive Development (CD-1) district — rules live in its "
                "site-specific enacting by-law (see cd_1_number); standard district assumptions "
                "do not apply.",
                severity="info",
            )
        )
    # District schedules are PDF-only (bylaws.vancouver.ca/zoning) — no numeric
    # FSR/height fields exist in the open data layer (verified 2026-07-11).
    warnings.append(
        note(
            "DISTRICT_SCHEDULE_PDF",
            "Vancouver's zoning layer publishes district codes but not numeric FSR/height — "
            "regulations are in each district schedule PDF at bylaws.vancouver.ca/zoning.",
            severity="info",
        )
    )

    developable_families = {"residential", "commercial", "industrial", "comprehensive_development"}
    families_on_site = {d["family"] for d in districts if d["family"] in developable_families}

    facts = {
        "land_use.districts": districts,
        "land_use.dominant_district": dominant["code"],
        "land_use.far_assumption": None,
        "land_use.height_assumption_m": None,
        "land_use.density_assumption": None,
        "land_use.adjacent_uses": adjacent_uses,
        "land_use.mixed_use_opportunity": len(families_on_site) > 1,
    }
    return facts, warnings


# --- 2. Parcels (property-parcel-polygons + property-tax-report enrichment) ----
# Fields: civic_number, streetname, tax_coord, site_id, geom; enrichment merges
# tax_folio_count, tax_land_value_total, tax_improvement_value_total (numeric
# sums across strata folios for the latest report_year), tax_year_built,
# tax_zoning_district (sampled).


def parcels(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    on_site = se.intersecting(frame, features, min_overlap_m2=20.0)
    if not on_site:
        warnings.append(note("PARCELS_EMPTY", "No property parcels intersect the site boundary."))
        return {}, warnings

    records = []
    for feature, overlap_m2 in on_site:
        props = _props(feature)
        civic = props.get("civic_number") or ""
        street = props.get("streetname") or ""
        records.append(
            {
                "address": f"{civic} {street}".strip() or None,
                "tax_coord": props.get("tax_coord"),
                "site_id": props.get("site_id"),
                "folio_count": _num(props.get("tax_folio_count")),
                "land_value_total": _num(props.get("tax_land_value_total")),
                "improvement_value_total": _num(props.get("tax_improvement_value_total")),
                "year_built": _num(props.get("tax_year_built")),
                "zoning": props.get("tax_zoning_district"),
                "overlap_m2": round(overlap_m2, 1),
            }
        )

    parcel_count = len(records)
    if parcel_count == 1:
        assembly_risk = "low"
        rationale = "single parcel"
    elif parcel_count <= 4:
        assembly_risk = "medium"
        rationale = f"{parcel_count} parcels to assemble"
    else:
        assembly_risk = "high"
        rationale = f"{parcel_count} parcels to assemble"
    strata = [r for r in records if (r["folio_count"] or 0) > 1]
    if strata:
        assembly_risk = "high"
        rationale += f"; {len(strata)} strata-titled parcel(s) (multiple owners per parcel)"

    enriched = [r for r in records if r["land_value_total"] is not None]
    if not enriched:
        warnings.append(
            note(
                "VALUES_UNENRICHED",
                "Parcel geometry fetched but tax-report values did not join — assessed values "
                "and year built are unavailable for this run.",
                severity="info",
            )
        )

    years = [r["year_built"] for r in records if r["year_built"] and r["year_built"] > 1800]

    facts = {
        "site.parcel_count": parcel_count,
        "site.parcels": records[:50],
        "site.assembly_risk": {"level": assembly_risk, "rationale": rationale},
        "built_form.site_year_built_mean": round(sum(years) / len(years)) if years else None,
    }
    return facts, warnings


# --- 3. Local areas (local-area-boundary) ----------------------------------------
# Fields: name, geom (22 planning areas)


def local_areas(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    coverage = se.coverage_by(frame, features, lambda f: _props(f).get("name"))
    if not coverage:
        warnings.append(note("NEIGHBOURHOOD_EMPTY", "No local planning area covers the site."))
        return {}, warnings

    dominant = max(coverage.items(), key=lambda kv: kv[1]["pct"])[0]
    return {"site.community_name": dominant}, warnings


# --- 5. Rapid transit stations (rapid-transit-stations) ---------------------------
# Fields: station, geo_local_area, geom. SkyTrain only — bus stops are TransLink
# GTFS under a separate non-OGL licence (out of scope).

TOA_TIERS = (  # Provincial TOA legislation (2024 designation by-law): distance_m -> storeys
    (200.0, 20),
    (400.0, 12),
    (800.0, 8),
)


def rapid_transit(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = [
        note(
            "BUS_NETWORK_UNAVAILABLE",
            "Bus stops/routes are TransLink GTFS under a separate licence — transit counts "
            "cover SkyTrain stations only.",
            severity="info",
        )
    ]

    if not features:
        warnings.append(note("TRANSIT_EMPTY", "No rapid transit stations within the fetch envelope.", severity="info"))
        return {}, warnings

    nearest = se.nearest(frame, features, k=1)
    nearest_fact = None
    if nearest:
        distance_m, feature = nearest[0]
        nearest_fact = {
            "stop_name": _props(feature).get("station"),
            "is_station": True,
            "distance_m": round(distance_m, 1),
            "network_estimate_m": se.network_distance_estimate_m(distance_m),
            "method": se.DISTANCE_METHOD,
        }
        for radius_m, storeys in TOA_TIERS:
            if distance_m <= radius_m:
                warnings.append(
                    note(
                        "TOA_DENSITY_TIER",
                        f"Site is within {radius_m:.0f}m of {nearest_fact['stop_name']} SkyTrain "
                        f"station — provincial Transit-Oriented Area legislation permits "
                        f"~{storeys} storeys at this distance (TOA Rezoning Policy, 2024).",
                        severity="info",
                    )
                )
                break

    facts = {
        "mobility.transit_stops_400m": se.count_within(frame, features, 400.0),
        "mobility.transit_stops_800m": se.count_within(frame, features, 800.0),
        "mobility.nearest_transit": nearest_fact,
    }
    return facts, warnings


# --- 6. Parks (parks-polygon-representation) ----------------------------------------
# Fields: park_name, area_ha, classification, park_url, geom


def parks(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    if not features:
        warnings.append(note("PARKS_EMPTY", "No parks within 800m of the site.", severity="info"))
        return {}, warnings

    walkshed_area = se.coverage_by(frame, features, lambda f: "parks", zone_m=frame.site_m.buffer(800.0))
    park_area_ha = round(walkshed_area.get("parks", {}).get("area_m2", 0.0) / 10_000.0, 2)

    nearest = se.nearest(frame, features, k=1)
    nearest_fact = None
    if nearest:
        distance_m, feature = nearest[0]
        nearest_fact = {
            "name": _props(feature).get("park_name"),
            "category": _props(feature).get("classification"),
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


# --- 8. Designated floodplain (designated-floodplain) -------------------------------
# Fields: name, description, area_in_sq_meters, url, geom. 8 polygons citywide,
# incl. the 2100 sea-level-rise (1m SLR + freeboard) scenario.


def floodplain(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    hits = se.intersecting(frame, features, min_overlap_m2=1.0)
    zones = []
    seen: set[str] = set()
    for feature, _ in hits:
        props = _props(feature)
        name = props.get("name") or "unnamed"
        if name in seen:
            continue
        seen.add(name)
        zones.append(
            {
                "name": name,
                "description": (props.get("description") or "")[:280],
                "url": props.get("url"),
            }
        )

    if zones:
        warnings.append(
            note(
                "DESIGNATED_FLOODPLAIN",
                f"Site intersects Vancouver's designated floodplain ({', '.join(z['name'] for z in zones)}) "
                "— flood construction levels apply.",
            )
        )

    facts = {
        "environment.flood_risk": {
            "in_designated_floodplain": bool(zones),
            "zones": zones,
            "source": "designated-floodplain (includes 2100 sea-level-rise scenario)",
        }
    }
    return facts, warnings


# --- 9. Public trees (public-trees) ---------------------------------------------------
# Fields: common_name, genus_name, species_name, height_m, diameter_cm, geom


def trees(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    if not features:
        warnings.append(note("TREES_EMPTY", "No public trees within 150m of the site.", severity="info"))
        return {"public_realm.street_tree_count_150m": 0}, warnings

    return {"public_realm.street_tree_count_150m": se.count_within(frame, features, 150.0)}, warnings


# --- 10. View cones (view-cones) --------------------------------------------------------
# Fields: view_cone_name, view_number, description, url, geom. 24 protected view
# corridors with height limits — a Vancouver-only development constraint.


def view_cones(features: list[Feature], site: Polygon) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    frame = se.SiteFrame.from_wgs84(site)
    warnings: list[dict[str, Any]] = []

    hits = se.intersecting(frame, features, min_overlap_m2=1.0)
    cones = []
    seen: set[str] = set()
    for feature, _ in hits:
        props = _props(feature)
        name = props.get("view_cone_name") or props.get("view_number") or "unnamed"
        if name in seen:
            continue
        seen.add(name)
        cones.append(
            {
                "name": name,
                "view_number": props.get("view_number"),
                "description": (props.get("description") or "")[:280],
                "url": props.get("url"),
            }
        )

    if cones:
        warnings.append(
            note(
                "VIEW_CONE_CONSTRAINT",
                f"Site lies under {len(cones)} protected view cone(s) "
                f"({', '.join(c['name'] for c in cones[:3])}) — council view-protection "
                "guidelines cap building heights below zoning maximums here.",
            )
        )

    facts = {
        "built_form.view_cone_constraint": {
            "under_view_cone": bool(cones),
            "cones": cones,
        }
    }
    return facts, warnings
