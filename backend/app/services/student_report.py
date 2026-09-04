"""Deterministic, advisory plan review with explicit evidence and uncertainty.

This reads saved design geometry. It neither calls a model nor changes the plan.
Metrics reuse the existing DerivedMetric contract, without its parameter-mode
housing assumptions or a site-wide conformance verdict for parcel regulations.
"""

from __future__ import annotations

import hashlib
import html
import json
import math
from typing import Any

from geoalchemy2.shape import to_shape
from shapely.geometry import mapping, shape
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from app.services.plan_metrics import DerivedMetric
from app.services.lego_assembly import DETACHED_ARCHETYPE_IDS, catalog_parent_archetype_id
from app.services.residual_landscape import community_3d_source_hash
from app.services.policy_intelligence.retrieval import (
    ChunkRecord,
    build_query_terms,
    rank_chunks,
)
from app.services.site_engine import (
    build_transformer,
    local_metric_crs_for_polygon,
    project_geometry,
)


def digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def geometry_json(value: Any) -> dict | None:
    if value is None:
        return None
    try:
        geom = (
            value if isinstance(value, BaseGeometry) else (shape(value) if isinstance(value, dict) else to_shape(value))
        )
        return json.loads(json.dumps(mapping(geom)))
    except (TypeError, ValueError, AssertionError):
        return None


def positive(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
        return number if math.isfinite(number) and number > 0 else None
    except (TypeError, ValueError):
        return None


def reference_attributes(layer: Any, extent: BaseGeometry | None) -> list[dict]:
    """Bounded examples at the actual site; layer display state is irrelevant."""
    if extent is None:
        return []
    examples = []
    for feature in (layer.feature_collection or {}).get("features", []):
        try:
            geom = shape(feature.get("geometry"))
            if geom.is_empty or not geom.is_valid or not geom.intersects(extent):
                continue
        except (AttributeError, TypeError, ValueError):
            continue
        attributes = {str(key): str(value)[:300] for key, value in list((feature.get("properties") or {}).items())[:16]}
        examples.append(
            {
                "feature_id": str(feature.get("id", len(examples) + 1)),
                "attributes": attributes,
            }
        )
        if len(examples) == 6:
            break
    return examples


def build_snapshot(
    project: Any,
    zones: list[Any],
    buildings: list[Any],
    references: list[Any],
    zone_ids: list[str] | None,
) -> dict:
    """Save geometry and evidence identities. Visibility and UI colour are not plan revisions."""
    zone_records = []
    for zone in zones:
        props = dict(zone.properties or {})
        # Visibility is presentation state; a hidden reference remains evidence.
        for key in ("visible", "is_visible", "hidden", "_visible", "_hidden"):
            props.pop(key, None)
        zone_records.append(
            {
                "id": str(zone.id),
                "name": zone.name or zone.zone_type.replace("_", " "),
                "zone_type": zone.zone_type,
                "geometry": geometry_json(zone.geometry),
                "properties": props,
                "active_boundary": bool(zone.is_active_boundary),
                "building_id": str(zone.building_id) if zone.building_id else None,
                "building_ids": sorted(str(value) for value in (zone.building_ids or [])),
            }
        )
    building_records = [
        {
            "id": str(building.id),
            "name": building.name or "Building",
            "geometry": geometry_json(building.footprint),
            "floors": building.floor_count,
            "height_m": float(building.height_meters) if building.height_meters is not None else None,
            "specifications": building.specifications or {},
        }
        for building in buildings
    ]
    project_boundary = geometry_json(project.site_boundary)
    boundary = boundary_record({"zones": zone_records, "project_boundary": project_boundary})
    extent = _shape(boundary) if boundary else None
    if extent is None:
        shapes = [
            _shape(record)
            for record in zone_records
            if record["zone_type"] != "site_boundary" and (zone_ids is None or record["id"] in zone_ids)
        ]
        shapes = [geom for geom in shapes if geom is not None]
        extent = unary_union(shapes) if shapes else None
    reference_records = [
        {
            "id": str(layer.id),
            "name": layer.name,
            "kind": layer.kind,
            "source_url": layer.source_url,
            "source_filename": layer.source_filename,
            "source_crs": layer.source_crs,
            "feature_count": layer.feature_count,
            "data_version": digest(layer.feature_collection),
            "site_attribute_examples": reference_attributes(layer, extent),
        }
        for layer in references
    ]
    return {
        "project_name": project.name,
        "description": project.description or "",
        "project_boundary": project_boundary,
        "scope_zone_ids": sorted(set(zone_ids)) if zone_ids is not None else None,
        "zones": sorted(zone_records, key=lambda item: item["id"]),
        "buildings": sorted(building_records, key=lambda item: item["id"]),
        "references": sorted(reference_records, key=lambda item: item["id"]),
    }


def boundary_record(snapshot: dict) -> dict | None:
    boundaries = [z for z in snapshot["zones"] if z["zone_type"] == "site_boundary"]
    active = [z for z in boundaries if z["active_boundary"]]
    if len(active) == 1:
        return active[0]
    if len(boundaries) == 1:
        return boundaries[0]
    if not boundaries and snapshot.get("project_boundary"):
        return {
            "id": "project-boundary",
            "geometry": snapshot["project_boundary"],
            "name": "Project boundary",
        }
    return None


def _shape(record: dict) -> BaseGeometry | None:
    try:
        geom = shape(record["geometry"])
        if geom.is_valid and not geom.is_empty and geom.geom_type in {"Polygon", "MultiPolygon"}:
            return geom
    except (TypeError, ValueError, KeyError, AttributeError):
        pass
    return None


def scoped_zones(snapshot: dict) -> list[dict]:
    selected = snapshot.get("scope_zone_ids")
    return [
        z
        for z in snapshot["zones"]
        if z["zone_type"] != "site_boundary"
        and (selected is None or z["id"] in selected)
        and z["properties"].get("_plan_role") != "framework_height"
        and z["properties"].get("_layer_role") != "reference"
        and not z["properties"].get("is_reference")
    ]


def _object(value: Any) -> dict:
    return value if isinstance(value, dict) else {}


def analyze_snapshot(snapshot: dict, policy_sources: list[dict] | None = None) -> dict:
    zones = scoped_zones(snapshot)
    buildings_by_id = {building["id"]: building for building in snapshot["buildings"]}
    detached_zone_ids: set[str] = set()
    detached_building_ids: set[str] = set()
    compiled_detached: dict[str, int] = {}
    compiled_detached_zone_ids: set[str] = set()
    for zone in zones:
        props = zone["properties"]
        identity = str(props.get("development_selected_variant_id") or props.get("development_archetype_id") or "")
        linked_ids = set(([zone["building_id"]] if zone["building_id"] else []) + zone["building_ids"])
        linked = [buildings_by_id[bid] for bid in linked_ids if bid in buildings_by_id]
        recipes = [
            (building, _object(_object(building.get("specifications")).get("legoAssembly"))) for building in linked
        ]
        if catalog_parent_archetype_id(identity) not in DETACHED_ARCHETYPE_IDS and not any(
            _object(recipe.get("fit")).get("placement_mode") == "detached_lots" for _, recipe in recipes
        ):
            continue
        detached_zone_ids.add(zone["id"])
        detached_building_ids.update(linked_ids)
        state = _object(props.get("community_3d"))
        geom = _shape(zone)
        if (
            state.get("state") != "compiled"
            or geom is None
            or state.get("source_hash") != community_3d_source_hash(zone["zone_type"], geom, props)
        ):
            continue
        use = str(props.get("development_type") or "residential")
        if use not in {"residential", "mixed_use"} and not use.startswith("residential_"):
            continue
        for building, recipe in recipes:
            fit = _object(recipe.get("fit"))
            count = fit.get("dwelling_count")
            instances = recipe.get("instances")
            if not isinstance(instances, list) or not all(
                isinstance(item, dict) and isinstance(item.get("segment_id"), str) and item["segment_id"]
                for item in instances
            ):
                continue
            segments = {item["segment_id"] for item in instances}
            if (
                fit.get("placement_mode") == "detached_lots"
                and isinstance(count, int)
                and not isinstance(count, bool)
                and 1 <= count <= 256
                and None not in segments
                and len(segments) == count
            ):
                compiled_detached[building["id"]] = count
                compiled_detached_zone_ids.add(zone["id"])
    boundary = boundary_record(snapshot)
    boundary_shape = _shape(boundary) if boundary else None
    valid = [(zone, _shape(zone)) for zone in zones]
    geometry = [geom for _, geom in valid if geom is not None]
    findings: list[dict] = []
    metrics: list[dict] = []
    limitations = [
        "Advisory review of saved proposal geometry; recommendations do not restrict drawing or rendering.",
        "No automatic zoning approval, accessibility certification, traffic simulation, or grading is performed.",
        "Dwelling quantities distinguish current compiled detached-house instances from student-recorded estimates; no housing yield is inferred for commercial or industrial buildings.",
    ]

    def finding(
        key: str,
        title: str,
        observation: str,
        recommendation: str,
        *,
        kind: str = "design_suggestion",
        records: list[dict] | None = None,
        basis: str = "Saved proposal geometry",
        uncertainty: str = "",
        sources: list[dict] | None = None,
    ):
        selected = records or []
        findings.append(
            {
                "id": key,
                "kind": kind,
                "title": title,
                "observation": observation,
                "recommendation": recommendation,
                "basis": basis,
                "uncertainty": uncertainty,
                "location": {
                    "label": ", ".join(z["name"] for z in selected) or "Whole proposal",
                    "zone_ids": [z["id"] for z in selected],
                },
                "sources": sources or [],
            }
        )

    def metric(
        key: str,
        label: str,
        value: float | None,
        unit: str,
        derivation: str,
        confidence: float = 1.0,
    ):
        metrics.append(
            DerivedMetric(
                key=key,
                label=label,
                value=round(value, 2) if value is not None else None,
                unit=unit,
                derivation=derivation,
                inputs=["saved proposal snapshot"],
                confidence=confidence,
                mode="geometry",
            ).model_dump()
        )

    metric(
        "proposal_zones",
        "Proposal areas",
        len(zones),
        "areas",
        "Count of saved proposal areas in this report's scope; not a building count.",
    )
    if not boundary_shape:
        finding(
            "boundary",
            "Choose a site boundary",
            "There is no single usable active boundary for this report.",
            "Draw or select the site boundary to measure site area and test proposal containment.",
            kind="unresolved_question",
            uncertainty="Site percentages and containment remain unassessed.",
        )
    if not zones:
        finding(
            "empty-plan",
            "Start shaping the proposal",
            "No proposal areas are included in this report.",
            "Draw a building, park, or street, then request a new report.",
            kind="unresolved_question",
        )
    invalid = [zone for zone, geom in valid if geom is None]
    if invalid:
        finding(
            "geometry",
            "Review unreadable geometry",
            f"{len(invalid)} proposal areas could not be measured.",
            "Repair these polygons and request a new report.",
            records=invalid,
            kind="unresolved_question",
        )
    alternatives = {z["properties"].get("_plan_scenario") for z in zones if z["properties"].get("_plan_scenario")}
    if len(alternatives) > 1:
        limitations.append(
            "Multiple saved scenario alternatives are included. Quantities describe this combined scope, not one coordinated proposal."
        )
        finding(
            "alternatives",
            "Review the selected proposal scope",
            "This report includes more than one saved scenario.",
            "Show the alternative you intend to defend and request a report for that proposal.",
            kind="unresolved_question",
        )

    parks = [z for z in zones if z["zone_type"] == "green_space"]
    roads = [z for z in zones if z["zone_type"] == "road"]
    # A development-area polygon may be a parcel holding many buildings. Never
    # multiply the entire parcel by storeys and present it as built floor area.
    building_zones = [z for z in zones if z["zone_type"] in {"building", "residential"}]
    development_areas = [z for z in zones if z["zone_type"] == "development_area"]
    if development_areas:
        limitations.append(
            "Development-area polygons are land allocations. Their area is not counted as building footprint or floor area unless linked building footprints exist."
        )
    if zones and not parks:
        finding(
            "open-space",
            "Explain access to public open space",
            "No park or green-space area is drawn in this proposal.",
            "Add public open space or explain how residents will reach an existing park.",
            uncertainty="Nearby parks and their capacity have not been assessed.",
        )
    if zones and not roads:
        finding(
            "access",
            "Show how people reach the proposal",
            "No street or path area is drawn in this proposal.",
            "Show the connections to surrounding streets and a walking route between homes and shared spaces.",
            uncertainty="Existing streets may already provide access; the absence of a drawn road does not prove missing access.",
        )

    if geometry or boundary_shape is not None:
        extent = boundary_shape if boundary_shape is not None else unary_union(geometry)
        transformer = build_transformer("EPSG:4326", local_metric_crs_for_polygon(extent))
        measured = {z["id"]: project_geometry(geom, transformer) for z, geom in valid if geom is not None}
        boundary_m = project_geometry(boundary_shape, transformer) if boundary_shape is not None else None

        def union_area(records: list[dict]) -> float:
            shapes = [measured[z["id"]] for z in records if z["id"] in measured]
            if not shapes:
                return 0.0
            combined = unary_union(shapes)
            return combined.intersection(boundary_m).area if boundary_m is not None else combined.area

        metric(
            "site_area_m2",
            "Site area",
            boundary_m.area if boundary_m is not None else None,
            "m²",
            "Active site boundary measured in a local metric coordinate system.",
        )
        metric(
            "park_area_m2",
            "Drawn park area",
            union_area(parks),
            "m²",
            "Union of drawn green-space polygons, clipped to the site when a boundary is available; overlaps counted once.",
        )
        metric(
            "street_area_m2",
            "Drawn street and path area",
            union_area(roads),
            "m²",
            "Union of road polygons, clipped to the site when a boundary is available; not a road length or accessibility assessment.",
        )
        metric(
            "development_land_m2",
            "Allocated development land",
            union_area(development_areas),
            "m²",
            "Union of development-area polygons; this is land allocation, not building footprint.",
        )
        if boundary_m is not None:
            outside = [z for z in zones if z["id"] in measured and measured[z["id"]].difference(boundary_m).area > 1]
            if outside:
                finding(
                    "outside-boundary",
                    "Review development outside the site",
                    f"{len(outside)} proposal areas extend more than 1 m² beyond the active boundary.",
                    "Move or resize the proposal, revise the intended boundary, or explain the off-site work and permissions needed.",
                    records=outside,
                    uncertainty="Boundary precision and ownership have not been independently surveyed.",
                )
        for park in parks[:20]:
            if park["id"] not in measured or not roads:
                continue
            distances = [measured[park["id"]].distance(measured[r["id"]]) for r in roads if r["id"] in measured]
            if distances and min(distances) > 3:
                finding(
                    "park-access-" + park["id"],
                    "Check the park's walking connection",
                    f"The nearest drawn street/path is approximately {min(distances):.0f} m from the park edge.",
                    "Draw a connecting path or explain the alternative entrance and route.",
                    records=[park],
                    uncertainty="This is straight-line polygon separation, not a network accessibility test; existing paths are not included.",
                )

        linked_ids = {
            str(bid) for z in zones for bid in ([z["building_id"]] if z["building_id"] else []) + z["building_ids"]
        }
        linked = [b for b in snapshot["buildings"] if b["id"] in linked_ids]
        # A linked Building replaces its zone's coarse footprint; never count both.
        footprints = [
            {**z, "floors": z["properties"].get("floors")}
            for z in building_zones
            if not z["building_id"] and not z["building_ids"]
        ] + linked
        missing_floors = []
        areas = []
        gfa = 0.0
        for building in footprints:
            if building["id"] in detached_zone_ids or building["id"] in detached_building_ids:
                # A detached recipe is anchored to its whole plot, including
                # yards. That parent polygon is never a building floor plate.
                missing_floors.append(building)
                continue
            geom = _shape(building)
            if geom is None:
                missing_floors.append(building)
                continue
            area = project_geometry(geom, transformer).area
            areas.append(project_geometry(geom, transformer))
            floors = positive(building.get("floors"))
            if floors is None:
                missing_floors.append(building)
            else:
                gfa += area * floors
        metric(
            "building_footprint_m2",
            "Known building footprints",
            unary_union(areas).area if areas else 0,
            "m²",
            "Union of direct building-zone footprints and linked building records; excludes unbuilt development allocations and detached housing plots whose individual floor plates are not measured.",
        )
        complete = not missing_floors and all(z["building_id"] or z["building_ids"] for z in development_areas)
        metric(
            "gfa_m2",
            "Floor-area estimate" if complete else "Known floor area (incomplete)",
            gfa,
            "m²",
            "Sum of known footprint × recorded storeys. Assumes equal floor plates; excludes unknown floors, unresolved development allocations, and detached housing plots (yards are not floor area).",
            0.7,
        )
        if missing_floors or not complete:
            finding(
                "floor-area-inputs",
                "Complete the building quantities",
                "Some building footprints or storey counts are not resolved, so the floor-area total is incomplete.",
                "Set storeys and build out development areas before using floor area for a density argument.",
                kind="unresolved_question",
                uncertainty="No floor count or housing yield has been guessed.",
            )

    known_units = 0.0
    units_recorded = False
    for zone in zones:
        props = zone["properties"]
        if zone["id"] in compiled_detached_zone_ids:
            continue
        use = props.get("development_type") or ("residential" if zone["zone_type"] == "residential" else None)
        if use not in {"residential", "mixed_use"} and not str(use).startswith("residential_"):
            continue
        raw_units = props.get("unit_count")
        units = 0.0 if raw_units == 0 and not isinstance(raw_units, bool) else positive(raw_units)
        if units is not None:
            known_units += units
            units_recorded = True
    metric(
        "recorded_units",
        "Other recorded dwelling-unit estimates" if compiled_detached else "Recorded dwelling-unit estimates",
        known_units if units_recorded else None,
        "units",
        "Sum of student-recorded residential/mixed-use zone unit estimates, excluding plots counted by a current detached recipe. Missing values are unknown; no area-to-unit conversion.",
        0.8,
    )

    if detached_zone_ids:
        metric(
            "compiled_detached_dwellings",
            "Compiled detached dwellings",
            sum(compiled_detached.values()) if compiled_detached else None,
            "dwellings",
            "Sum of current server-certified detached recipe dwelling counts, deduplicated by linked building. Repeated podium/floor/roof modules represent one dwelling per segment, not additional units.",
            0.95,
        )
        pending = len(detached_zone_ids - compiled_detached_zone_ids)
        metric(
            "detached_plots_pending",
            "Detached plots awaiting current 3D",
            pending,
            "plots",
            "Housing plot count, separate from dwelling count. Compile or rebuild Community 3D to resolve missing or stale dwelling recipes.",
        )
        finding(
            "detached-housing-quantities",
            "Resolve the detached housing quantities",
            f"{len(detached_zone_ids)} detached housing plots are present; {pending} await current compiled dwelling quantities. Plot area includes yards and is excluded from known building footprint and floor-area totals.",
            "Build or refresh Community 3D for dwelling counts. Record individual measured house floor plates before using these plots for floor-area or density calculations.",
            kind="unresolved_question",
            records=[zone for zone in zones if zone["id"] in detached_zone_ids],
            uncertainty="Concept placement counts are not occupancy, zoning approval, or surveyed floor area. Any uncompiled unit count remains a student estimate.",
        )

    refs = snapshot.get("references", [])
    if refs:
        finding(
            "reference-evidence",
            "Check site reference information",
            f"{len(refs)} reference layers are available independently of proposal geometry.",
            "Use their attributes and source dates to explain the site's existing zoning and constraints.",
            kind="source_context",
            basis="Imported project reference layers",
            sources=[
                {
                    "title": r["name"],
                    "url": r["source_url"],
                    "excerpt": f"{r['feature_count']} dataset features; source {r['source_filename']}; data version {r['data_version'][:12]}. "
                    + (
                        "Intersecting site attribute examples (up to 6 features, 16 fields each): "
                        + json.dumps(r["site_attribute_examples"], ensure_ascii=False)
                        if r.get("site_attribute_examples")
                        else "No intersecting attribute examples were found or site extent is unknown."
                    ),
                }
                for r in refs
            ],
            uncertainty="Imported attributes are evidence to check, not an automatic legal conformance determination.",
        )
    policy_sources = policy_sources or []
    if policy_sources:
        finding(
            "city-documents",
            "Read relevant city policy passages",
            "Stored city-document passages match housing, public-space, access, or built-form topics in the proposal.",
            "Explain how the proposal responds to these passages and verify that their geographic scope and current versions apply.",
            kind="source_context",
            sources=policy_sources,
            basis="Lexical retrieval from the existing city policy corpus",
            uncertainty="A text match is a reading lead. It does not establish that a rule applies to this parcel or that the proposal complies.",
        )
    else:
        finding(
            "city-documents",
            "Add the local policy basis",
            "No applicable saved city-document passages were available for this report.",
            "Identify the current land-use bylaw and local area plan for the site and record relevant provisions in your response.",
            kind="unresolved_question",
            uncertainty="Current zoning permissions and local policy conformity remain unassessed.",
        )
    finding(
        "implementation",
        "Explain the path to implementation",
        "This concept has no verified parcel-by-parcel zoning conformance assessment.",
        "Compare proposed uses, height, density, setbacks, and access with sourced parcel rules. If they conflict, investigate a land-use amendment or other applicable approval with the municipality; record the evidence and remaining steps.",
        kind="unresolved_question",
        basis="Planning implementation reasoning",
        uncertainty="No replacement district is recommended without verified proposal requirements and current municipal rules.",
    )
    return {
        "method_version": "student-review-v1",
        "metrics": metrics,
        "findings": findings,
        "limitations": limitations,
        "scope_zone_count": len(zones),
        "boundary_name": boundary["name"] if boundary else None,
    }


def select_policy_sources(records: list[ChunkRecord], site_facts: dict) -> list[dict]:
    ranked = rank_chunks(
        records,
        build_query_terms(site_facts, ["housing", "pedestrian", "pathway", "public space", "height"]),
        top_k=4,
        max_total_chars=12000,
    )
    return [
        {
            "title": item.document_title,
            "url": item.source_url,
            "page": item.page_start,
            "section": item.section_label,
            "excerpt": item.text[:1200],
            "chunk_id": item.chunk_id,
        }
        for item in ranked
    ]


def snapshot_drawing(snapshot: dict) -> str:
    """A measurable plan drawing of the saved report scope, preserving holes."""
    records = scoped_zones(snapshot)
    boundary = boundary_record(snapshot)
    if boundary:
        records = [*records, {**boundary, "zone_type": "site_boundary"}]
    valid = [(record, _shape(record)) for record in records]
    valid = [(record, geom) for record, geom in valid if geom is not None]
    if not valid:
        return "<p>No measurable geometry in this snapshot.</p>"
    extent = unary_union([geom for _, geom in valid])
    transformer = build_transformer("EPSG:4326", local_metric_crs_for_polygon(extent))
    projected = [(record, project_geometry(geom, transformer)) for record, geom in valid]
    minx, miny, maxx, maxy = unary_union([geom for _, geom in projected]).bounds
    span = max(maxx - minx, maxy - miny, 1)
    padding = span * 0.06
    width, height = maxx - minx + padding * 2, maxy - miny + padding * 2
    paths = []
    colors = {
        "green_space": "#94c7a6",
        "road": "#a3abb3",
        "building": "#9280bb",
        "residential": "#9280bb",
        "water": "#90c5db",
        "development_area": "#e1c897",
        "parking": "#ccd0d5",
    }
    for record, geom in projected:
        polygons = list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]
        commands = []
        for polygon in polygons:
            for ring in [polygon.exterior, *polygon.interiors]:
                coordinates = [(x - minx + padding, maxy - y + padding) for x, y in ring.coords]
                commands.append("M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in coordinates) + " Z")
        is_boundary = record["zone_type"] == "site_boundary"
        color = "none" if is_boundary else colors.get(record["zone_type"], "#ddd")
        dash = ' stroke-dasharray="4 3"' if is_boundary else ""
        paths.append(
            f'<path d="{" ".join(commands)}" fill="{color}" fill-rule="evenodd" stroke="#314c47" stroke-width="{span * 0.002:.3f}"{dash}><title>{html.escape(record["name"])}</title></path>'
        )
    return f'<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Saved proposal plan" viewBox="0 0 {width:.2f} {height:.2f}" style="width:100%;max-height:460px;background:#f5f6f2">{"".join(paths)}</svg><p class="meta">Saved plan geometry · north up · drawing extent {width:.0f} × {height:.0f} m · purple buildings, green parks, gray roads, sand development allocations; dashed site boundary.</p>'


def report_html(report: dict, snapshot: dict, decision_history: list[dict]) -> str:
    """Self-contained printable submission, including the original plan and response authors."""

    def esc(value: Any) -> str:
        return html.escape(str(value if value is not None else ""), quote=True)

    analysis = report["analysis"]
    rows = "".join(
        f"<tr><th>{esc(m['label'])}</th><td>{esc(m['value'] if m['value'] is not None else 'Unknown')} {esc(m['unit'])}</td><td>{esc(m['derivation'])}</td></tr>"
        for m in analysis["metrics"]
    )
    sections = []
    for finding in analysis["findings"]:
        sources = []
        for source in finding["sources"]:
            title = esc(source["title"])
            url = source.get("url") or ""
            if url.startswith(("https://", "http://")):
                title = f'<a href="{esc(url)}">{title}</a>'
            context_date = source.get("context_created_at")
            sources.append(
                f"<li>{title} {esc('p. ' + str(source['page']) if source.get('page') else '')}<blockquote>{esc(source.get('excerpt'))}</blockquote>"
                + (
                    f"<p class='meta'>Site context captured {esc(context_date)}; verify current applicability.</p>"
                    if context_date
                    else ""
                )
                + "</li>"
            )
        response = report["decisions"].get(finding["id"])
        student = (
            f"<p><b>Student choice:</b> {esc(response['choice'])} · {esc(response['author_name'])} · {esc(response['updated_at'])}</p>"
            f"<p class='reason'>{esc(response['rationale'])}</p><p><b>Follow-through:</b> {esc(response['follow_through']) or 'Not recorded'}</p>"
            if response
            else "<p>Student response: not yet recorded.</p>"
        )
        sections.append(
            f"<section><h2>{esc(finding['title'])}</h2><p class='meta'>{esc(finding['kind'].replace('_', ' '))} · {esc(finding['location']['label'])}</p>"
            f"<p>{esc(finding['observation'])}</p><p><b>Suggested next step:</b> {esc(finding['recommendation'])}</p>"
            f"<p><b>Basis:</b> {esc(finding['basis'])}</p><p><b>Uncertainty:</b> {esc(finding['uncertainty']) or 'None additional recorded.'}</p><ul>{''.join(sources)}</ul>{student}</section>"
        )
    # The exact saved geometry is embedded as an inert JSON download for audit.
    # Escape '<' even in a script application/json block to prevent closing it.
    snapshot_json = json.dumps(snapshot, ensure_ascii=False).replace("<", "\\u003c")
    history = "".join(
        f"<li>{esc(item['author_name'])} · {esc(item['updated_at'])} · {esc(item['finding_id'])}: {esc(item['choice'])}<p class='reason'>{esc(item['rationale'])}</p><p>{esc(item['follow_through'])}</p></li>"
        for item in decision_history
    )
    inventory = "".join(
        f"<tr><td>{esc(z['name'])}</td><td>{esc(z['zone_type'])}</td><td>{esc(z['id'])}</td></tr>"
        for z in scoped_zones(snapshot)
    )
    stale = (
        "The proposal has changed since this report. This submission describes the saved version below."
        if report["is_stale"]
        else "This report matches the current saved proposal at export time."
    )
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(report['project_name'])} — planning report</title>
<style>body{{font:15px/1.6 system-ui,sans-serif;color:#172b2a;max-width:920px;margin:36px auto;padding:0 24px}}h1{{font-size:30px}}h2{{font-size:20px;margin-top:30px}}.meta{{color:#536b68;font-size:12px}}.notice{{padding:16px;background:#edf5f2;border-left:4px solid #327565}}table{{border-collapse:collapse;width:100%;font-size:12px}}td,th{{border-bottom:1px solid #ccd8d4;padding:9px;text-align:left;vertical-align:top}}blockquote{{margin:8px 0;color:#405652;font-size:13px}}.reason{{white-space:pre-wrap}}section{{border-bottom:1px solid #ccd8d4;padding-bottom:16px}}@page{{size:A4;margin:15mm}}@media print{{body{{margin:0;padding:0;max-width:none}}h2{{break-after:avoid}}tr{{break-inside:avoid}}a{{color:inherit}}}}</style></head><body>
<h1>{esc(report['project_name'])}</h1><p>Planning report and student decision record</p>
<p class="meta">Requested by {esc(report['requested_by_name'])} · {esc(report['created_at'])}<br>Report {esc(report['id'])} · Plan version {esc(report['plan_version'])} · Response revision {esc(report['response_revision'])}</p>
<p class="notice">{esc(stale)} Recommendations are advisory. Student choices and reasoning are recorded in their own words; selecting “implement” records an intention, not a verified design change.</p>
<h2>The saved proposal</h2>{snapshot_drawing(snapshot)}<h2>Proposal quantities</h2><table>{rows}</table><ul>{''.join('<li>'+esc(x)+'</li>' for x in analysis['limitations'])}</ul>
{''.join(sections)}<h2>Saved proposal inventory</h2><table><tr><th>Area</th><th>Type</th><th>Stable ID</th></tr>{inventory}</table>
<h2>Decision history</h2><ul>{history or '<li>No responses recorded.</li>'}</ul>
<p class="meta">Use your browser’s Print command to save this self-contained report as PDF. The original geometry snapshot is embedded in this HTML for traceability.</p><script type="application/json" id="plan-snapshot">{snapshot_json}</script></body></html>"""
