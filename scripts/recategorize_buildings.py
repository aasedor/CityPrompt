#!/usr/bin/env python3
"""
Recategorize building archetypes into the 13 functional categories from
docs/CATEGORY_AUDIT_REPORT-AndrewDesk.md.

Uses TEXT-LEVEL regex substitution to update `buildingSubcategory` per
archetype — never json.dump the whole catalog (corrupts thumbnailUrl paths
per CLAUDE.md).

Usage:
    python scripts/recategorize_buildings.py --dry-run   # preview + distribution
    python scripts/recategorize_buildings.py             # apply edits
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "frontend" / "src" / "data" / "buildingArchetypes.json"


# 13 functional top-level categories from CATEGORY_AUDIT_REPORT, with
# Residential and Commercial/Mixed-Use further split into 4 sub-buckets each
# (19 leaf categories total).
CATEGORIES = {
    # Residential sub-buckets
    "RES_DET": "Residential — Detached / Single-Family",
    "RES_ROW": "Residential — Rowhouse / Townhouse / Terrace",
    "RES_MID": "Residential — Mid-Rise Apartment",
    "RES_HIGH": "Residential — High-Rise / Tower",
    # Commercial sub-buckets
    "COM_MAIN": "Commercial — Main Street / Heritage Retail",
    "COM_OFFICE": "Commercial — Office / Office Tower",
    "COM_MIXED": "Commercial — Mixed-Use Mid-Rise",
    "COM_MARKET": "Commercial — Market / Specialty Retail",
    # Other functional categories (unchanged)
    "IND": "Industrial",
    "CIV": "Civic / Institutional",
    "TRA": "Transportation",
    "ENT": "Entertainment / Culture",
    "REC": "Recreation",
    "HOS": "Hospitality",
    "ENE": "Energy / Infrastructure",
    "HEA": "Healthcare",
    "EDU": "Education",
    "AGR": "Agriculture",
    "CUS": "Custom / Other",
}

# Top-level parent code for each leaf (used to know when to refine).
_PARENT = {"RES_DET": "RES", "RES_ROW": "RES", "RES_MID": "RES", "RES_HIGH": "RES",
           "COM_MAIN": "COM", "COM_OFFICE": "COM", "COM_MIXED": "COM", "COM_MARKET": "COM"}


# Explicit mapping from audit report, plus manual refinements from ambiguous-
# archetype analysis (primary-category only).
AUDIT_MAPPING: dict[str, str] = {
    # Transportation
    "historic_grand_station": "TRA",
    "contemporary_transit_hub": "TRA",
    "urban_light_rail_stop": "TRA",
    "vancouver_skytrain_station": "TRA",
    "toronto_streetcar_stop": "TRA",
    "calgary_ctrain_station": "TRA",
    "halifax_ferry_terminal": "TRA",
    "vertiport_evtol": "TRA",
    "airport_terminal_building": "TRA",
    "intermodal_transit_hub": "TRA",
    "cruise_ferry_terminal": "TRA",
    "ttc_streetcar_platform_stop": "TRA",
    # Energy / Infrastructure
    "waste_to_energy_plant": "ENE",
    "solar_farm_agrivoltaics": "ENE",
    "ev_charging_hub": "ENE",
    "ev_charging_hub_mobility_station": "ENE",
    "hyperscale_data_center": "ENE",
    "central_utilities_plant_energy_centre": "ENE",
    # Civic / Institutional
    "civic_classical_building": "CIV",
    "monumental_courthouse_axis": "CIV",
    "modernist_civic_block": "CIV",
    "civic_monumental_institution": "CIV",
    "monumental_museum_axis": "CIV",
    "neoclassical_institutional": "CIV",
    "brutalist_institutional": "CIV",
    "contemporary_civic": "CIV",
    "modern_fire_station": "CIV",
    "montreal_second_empire": "CIV",
    "halifax_georgian": "CIV",
    "calgary_central_library": "CIV",
    "large_art_museum_gallery": "CIV",
    "second_empire_civic_building": "CIV",
    "university_library": "CIV",
    # Agriculture
    "vertical_farm": "AGR",
    "vertical_farm_indoor_agriculture": "AGR",
    # Healthcare
    "art_deco_healthcare": "HEA",
    "functionalist_healthcare": "HEA",
    "biophilic_healthcare": "HEA",
    "biophilic_modern_healthcare": "HEA",
    "senior_living_complex": "HEA",
    "aquatic_natatorium_complex": "HEA",
    "regional_hospital_medical_center": "HEA",
    # Entertainment / Culture
    "deco_theater_mainstreet": "ENT",
    "modern_sports_arena": "ENT",
    "monumental_antiquity_arena": "ENT",
    "high_tech_arena": "ENT",
    "high_tech_structural_arena": "ENT",
    "concrete_megastructure_arena": "ENT",
    "immersive_experience_venue": "ENT",
    "concert_hall_modern": "ENT",
    "outdoor_sports_stadium": "ENT",
    "convention_exhibition_center": "ENT",
    # Hospitality
    "boutique_hotel_tower": "HOS",
    "boutique_hotel": "HOS",
    "chateauesque_hotel": "HOS",
    "chateauesque_grand_railway_hotel": "HOS",
    "resort_modernism_hotel": "HOS",
    "corporate_tower_hotel": "HOS",
    "amsterdam_brown_cafe": "HOS",
    "parisian_cafe_brasserie": "HOS",
    # Education
    "collegiate_gothic_education": "EDU",
    "collegiate_gothic": "EDU",
    "autonomous_tech_campus": "EDU",
    "parisian_ecole": "EDU",
    "campus_dining_hall_food_court": "EDU",
    "campus_lecture_hall_complex": "EDU",
    "campus_parking_structure": "EDU",
    "campus_recreation_athletics_centre": "EDU",
    "graduate_family_housing": "EDU",
    "research_laboratory": "EDU",
    "research_laboratory_innovation_hub": "EDU",
    "science_engineering_lab_complex": "EDU",
    "student_residence_tower": "EDU",
    "student_union_campus_centre": "EDU",
    "university_academic_complex": "EDU",
    "administrative_faculty_office_building": "EDU",
    # Recreation
    "community_recreation_centre": "REC",
    "civic_modernism_rec_centre": "REC",
    "postmodern_rec_centre": "REC",
    "postmodern_community_rec_centre": "REC",
    "contemporary_sustainable_rec_centre": "REC",
    "parkitecture_recreational": "REC",
    "parkitecture": "REC",
    "climbing_wall_building": "REC",
    # Industrial
    "daylight_factory": "IND",
    "industrial_park_modernism": "IND",
    "art_deco_industrial": "IND",
    "functionalist_brick_industrial": "IND",
    "structural_expressionism_industrial": "IND",
    "corrugated_vernacular_industrial": "IND",
    "machine_aesthetic_heavy_industrial": "IND",
    "brutalist_utility_heavy_industrial": "IND",
    "early_20c_megastructure_industrial": "IND",
    "early_20th_century_megastructure": "IND",
    "romanesque_revival_warehouse": "IND",
    "midcentury_distribution_warehouse": "IND",
    "mid_century_distribution_warehouse": "IND",
    "modern_bigbox_warehouse": "IND",
    "modern_big_box_logistics": "IND",
    "e_commerce_fulfillment_center": "IND",
    "junction_converted_industrial_loft": "IND",
    # Residential
    "brownstone_rowhouse_frontage": "RES",
    "classic_brownstone_streetwall": "RES",
    "victorian_heritage_avenue": "RES",
    "contemporary_midrise_residential": "RES",
    "contemporary_midrise": "RES",
    "contemporary_townhouse_courtyard": "RES",
    "detached_contemporary_infill": "RES",
    "courtyard_family_housing": "RES",
    "scandinavian_urban_residential": "RES",
    "nordic_timber_midrise": "RES",
    "nordic_timber_mid_rise": "RES",
    "mediterranean_villa_estate": "RES",
    "art_deco_setback_tower": "RES",
    "vernacular_courtyard_housing": "RES",
    "minimalist_courtyard_block": "RES",
    "minimalist_infill_townhouse": "RES",
    "mountain_alpine_chalet": "RES",
    "transit_podium_residential": "RES",
    "japanese_contemporary_lanehouse": "RES",
    "eco_urban_bioclimatic_block": "RES",
    "vertical_forest_residential": "RES",
    "terraced_stepped_building": "RES",
    "parisian_hotel_particulier": "RES",
    "parisian_marais_building": "RES",
    "amsterdam_neck_gable": "RES",
    "amsterdam_step_gable": "RES",
    "amsterdam_bell_gable": "RES",
    "amsterdam_cornice_house": "RES",
    "amsterdam_pakhuis": "RES",
    "amsterdam_hofje": "RES",
    "amsterdam_school_housing": "RES",
    "amsterdam_jordaan_house": "RES",
    "amsterdam_spout_gable": "RES",
    "barcelona_modernisme_casa": "RES",
    "barcelona_townhouse": "RES",
    "london_georgian_terrace": "RES",
    "london_regency_terrace": "RES",
    "london_victorian_terrace": "RES",
    "london_mews": "RES",
    "london_crescent": "RES",
    "london_townhouse": "RES",
    "newyork_prewar": "RES",
    "newyork_tenement": "RES",
    "montreal_triplex": "RES",
    "montreal_duplex": "RES",
    "montreal_warehouse_loft": "RES",
    "montreal_mile_end_triplex": "RES",
    "vancouver_special": "RES",
    "vancouver_laneway": "RES",
    "vancouver_craftsman": "RES",
    "vancouver_tower_podium": "RES",
    "vancouver_west_end_tower": "RES",
    "toronto_bay_and_gable": "RES",
    "toronto_annex_mansion": "RES",
    "annex_mansion": "RES",
    "toronto_rowhouse": "RES",
    "toronto_edwardian": "RES",
    "edwardian_foursquare": "RES",
    "toronto_condo_tower": "RES",
    "condo_podium_tower": "RES",
    "calgary_bungalow": "RES",
    "calgary_modern_infill": "RES",
    "halifax_hydrostone": "RES",
    "halifax_clapboard_row": "RES",
    "adaptive_reuse_warehouse_lofts": "RES",
    "brick_rowhouse_terrace": "RES",
    "residential_superblock": "RES",
    "bay_and_gable_house": "RES",
    "calgary_15_connected_tower": "COM",  # commercial_office per audit
    # Commercial / Mixed-Use
    "historical_brick_main_street": "COM",
    "modern_glass_office_institutional": "COM",
    "industrial_brick_mixed_use": "COM",
    "mediterranean_arcade_mixed_use": "COM",
    "parametric_future_hub": "COM",
    "traditional_vernacular_market_street": "COM",
    "mid_century_modern_pavilion_block": "COM",
    "parisian_midrise_block": "COM",
    "parisian_mid_rise": "COM",
    "parisian_boulevard_corner": "COM",
    "alpine_mixed_use_lodge": "COM",
    "transit_oriented_station_block": "COM",
    "glass_tower_podium_modern": "COM",
    "glass_tower_modern": "COM",
    "skyline_glass_office_cluster": "COM",
    "japanese_machiya_mixed_use": "COM",
    "coastal_resort_terrace_block": "COM",
    "coastal_breezeway_mixed_use": "COM",
    "brewery_distillery": "COM",
    "shophouse_southeast_asian": "COM",
    "food_hall_market_hall": "COM",
    "mall_redevelopment": "COM",
    "parisian_corner_dome": "COM",
    "parisian_passage_couvert": "COM",
    "parisian_marche_couvert": "COM",
    "parisian_grand_magasin": "COM",
    "barcelona_eixample_block": "COM",
    "barcelona_xamfra": "COM",
    "barcelona_mercat": "COM",
    "barcelona_taller": "COM",
    "newyork_cast_iron": "COM",
    "newyork_art_deco": "COM",
    "newyork_bodega": "COM",
    "montreal_limestone_commercial": "COM",
    "montreal_depanneur": "COM",
    "vancouver_gastown": "COM",
    "toronto_junction_industrial": "COM",
    "calgary_sandstone": "COM",
    "calgary_inglewood": "COM",
    "calgary_plus15_tower": "COM",
    "calgary_beltline_midrise": "COM",
    "halifax_waterfront_warehouse": "COM",
    "halifax_commercial": "COM",
    "corporate_office_campus_headquarters": "COM",
    "corner_dépanneur": "COM",
    # Custom
    "custom_prompt_ready_archetype": "CUS",
    "custom_contextual_experiment": "CUS",
    # Manual overrides for archetypes that keyword-inference put in Custom
    "pre_haussmann_marais_building": "RES",
    "halifax_georgian_colonial": "CIV",
    "calgary_beltline_mid_rise": "COM",
    "calgary_sandstone_heritage": "COM",
    "vancouverism_tower_podium": "RES",
    "west_end_mid_century_tower": "RES",
    "inglewood_heritage_brick_commercial": "COM",
    "calgary_new_central_library": "CIV",
    "calgary_cbe_brutalist_hq": "CIV",
    "montreal_second_empire_civic": "CIV",
    "skytrain_elevated_station": "TRA",
    "toronto_streetcar_platform_stop": "TRA",
    "vertiport_evtol_facility": "TRA",
    "hotel_particulier": "RES",
    "ecole_republicaine": "EDU",
    "mile_end_cultural_triplex": "RES",
    "montreal_plateau_triplex": "RES",
}


# Keyword-based inference for IDs not in the audit mapping.
# Note: use specific multi-word keywords to avoid false positives
# (e.g. "wind" matches "window"; use "wind_farm" / "wind_turbine" instead).
KEYWORD_RULES: list[tuple[str, list[str]]] = [
    ("TRA", ["transit", "station", "aviation", "airport", "terminal", "ferry",
             "vertiport", "platform_stop", "skytrain", "ctrain",
             "streetcar", "light_rail", "light rail"]),
    ("ENE", ["energy_plant", "data_center", "data center", "solar_farm",
             "wind_farm", "wind_turbine", "wind_energy", "battery_storage",
             "ev_charg", "ev charging", "utilities_plant"]),
    ("AGR", ["vertical_farm", "indoor_agriculture", "greenhouse", "agrivolt"]),
    ("HEA", ["hospital", "healthcare", "medical_center", "natatorium",
             "senior_living", "assisted_living", "clinic"]),
    ("EDU", ["campus", "university", "college", "student", "faculty",
             "academic", "research_lab", "laboratory", "school_housing",
             "high_school", "primary_school", "ecole", "schul"]),
    ("HOS", ["hotel", "resort_modernism", "hospitality", "boutique_hotel",
             "brown_cafe", "brasserie", "railway_hotel"]),
    ("REC", ["rec_centre", "rec centre", "community_centre", "recreation",
             "climbing_wall", "gym", "fitness"]),
    ("ENT", ["arena", "stadium", "concert_hall", "theater", "theatre",
             "museum", "art_gallery", "cultural_block", "immersive",
             "convention", "exhibition", "parkitecture"]),
    ("IND", ["warehouse", "factory", "industrial", "fulfillment",
             "distribution", "workshop", "brewery", "distillery",
             "manufacturing"]),
    ("CIV", ["civic", "institutional", "courthouse", "government",
             "monumental", "fire_station", "library", "cbe_brutalist",
             "heritage_civic"]),
    ("RES", ["rowhouse", "terrace", "townhouse", "bungalow", "cottage",
             "apartment", "condo", "mansion", "house", "tenement",
             "residential", "laneway", "gable", "craftsman",
             "single_family", "multi_family", "walk_up", "hofje",
             "courtyard_family", "modernisme_casa", "edwardian",
             "mile_end", "vancouver_special", "painted_clapboard"]),
    ("COM", ["commercial", "office", "retail", "shophouse", "boulevard",
             "main_street", "mainstreet", "mixed_use", "mixed-use",
             "market", "magasin", "marche", "passage_couvert", "couvert",
             "corner", "cafe", "bodega", "depanneur", "dépanneur",
             "mainstreet_commercial", "cast_iron", "loft_building",
             "chamfer", "gastown", "waterfront_warehouse",
             "heritage_commercial", "limestone_commercial",
             "beltline_midrise", "plus15", "plus_15", "art_deco_tower",
             "eixample_apartment", "eixample_block"]),
]


def infer_category(arch_id: str, title: str) -> str:
    hay = f"{arch_id} {title}".lower()
    for cat, kws in KEYWORD_RULES:
        for kw in kws:
            if kw in hay:
                return cat
    return "CUS"


# -----------------------------------------------------------------------------
# Sub-bucket refinement for RES and COM parents
# -----------------------------------------------------------------------------


def _refine_residential(arch: dict) -> str:
    """Return a RES_DET / RES_ROW / RES_MID / RES_HIGH sub-bucket."""
    hay = f"{arch.get('id','')} {arch.get('title','')}".lower()
    max_floors = arch.get("maxFloors") or 0

    # High-rise / tower — floor count is authoritative
    if max_floors >= 8:
        return "RES_HIGH"
    for kw in ["highrise", "high-rise", "high rise", "tower", "skyscraper",
              "condo_tower", "vertical_forest", "setback_tower",
              "tower_podium", "mid_century_tower"]:
        if kw in hay:
            return "RES_HIGH"

    # Rowhouse / Townhouse / Terrace — attached multi-unit street-facing
    for kw in ["rowhouse", "row_house", "row house", "townhouse",
              "terrace", "brownstone", "streetwall", "street wall",
              "hydrostone", "clapboard_row", "gable_house", "mews",
              "crescent", "bay_and_gable", "gable", "tenement",
              "triplex", "duplex"]:
        if kw in hay:
            return "RES_ROW"

    # Detached / Single-Family
    for kw in ["detached", "single_family", "single-family", "bungalow",
              "villa", "cottage", "laneway", "lanehouse", "infill_house",
              "craftsman", "farnsworth", "vancouver_special",
              "foursquare", "chalet", "mansion", "estate",
              "annex_mansion", "modern_infill", "calgary_bungalow",
              "calgary_modern_infill"]:
        if kw in hay:
            return "RES_DET"

    # Default: Mid-Rise Apartment (3-7 storey multi-family)
    return "RES_MID"


def _refine_commercial(arch: dict) -> str:
    """Return a COM_MAIN / COM_OFFICE / COM_MIXED / COM_MARKET sub-bucket."""
    hay = f"{arch.get('id','')} {arch.get('title','')}".lower()

    # Market / Specialty Retail first (most specific)
    for kw in ["food_hall", "market_hall", "mercat", "grand_magasin",
              "magasin", "marche", "covered_passage", "passage_couvert",
              "passage", "arcade", "cast_iron", "cast-iron",
              "shophouse_southeast", "brewery", "distillery",
              "department_store", "dome"]:
        if kw in hay:
            return "COM_MARKET"

    # Office / Office Tower
    for kw in ["office", "glass_tower", "skyline_glass",
              "corporate_office", "corporate_tower",
              "calgary_plus15", "calgary_15_connected", "plus15",
              "plus_15", "parametric_future_hub", "headquarters",
              "modern_glass_office", "innovation_hub"]:
        if kw in hay:
            return "COM_OFFICE"

    # Main Street / Heritage Retail
    for kw in ["main_street", "mainstreet", "main street",
              "heritage_commercial", "heritage_brick", "corner",
              "bodega", "dépanneur", "depanneur", "shophouse",
              "vernacular_market", "waterfront_warehouse",
              "limestone_commercial", "gastown", "sandstone_heritage",
              "inglewood_heritage", "traditional_vernacular",
              "chamfer", "xamfra", "boulevard_corner",
              "canal_warehouse", "workshop"]:
        if kw in hay:
            return "COM_MAIN"

    # Default: Mixed-Use Mid-Rise (transit-oriented, midrise mixed-use, coastal, etc.)
    return "COM_MIXED"


def refine_residential_or_commercial(arch: dict, parent_key: str) -> str:
    if parent_key == "RES":
        return _refine_residential(arch)
    if parent_key == "COM":
        return _refine_commercial(arch)
    return parent_key


def build_mapping() -> dict[str, tuple[str, str]]:
    """Return {archetype_id: (category_key, source)}.

    For RES/COM parents, refines to a sub-bucket (RES_DET/ROW/MID/HIGH,
    COM_MAIN/OFFICE/MIXED/MARKET) using archetype metadata (floor count +
    keyword match in id/title).
    """
    d = json.loads(CATALOG.read_text(encoding="utf-8"))
    archs = d.get("archetypes", [])
    mapping: dict[str, tuple[str, str]] = {}
    for a in archs:
        aid = a.get("id") or ""
        title = a.get("title") or ""
        if aid in AUDIT_MAPPING:
            parent = AUDIT_MAPPING[aid]
            source = "audit"
        else:
            parent = infer_category(aid, title)
            source = "inferred"
        # Refine RES and COM into 4-way sub-buckets
        if parent in ("RES", "COM"):
            leaf = refine_residential_or_commercial(a, parent)
        else:
            leaf = parent
        mapping[aid] = (leaf, source)
    return mapping


def show_distribution(mapping: dict[str, tuple[str, str]]) -> None:
    by_cat: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for aid, (cat, src) in mapping.items():
        by_cat[cat].append((aid, src))
    for cat in sorted(CATEGORIES, key=lambda c: -len(by_cat.get(c, []))):
        items = by_cat.get(cat, [])
        if not items:
            continue
        audit_count = sum(1 for _, s in items if s == "audit")
        inferred_count = sum(1 for _, s in items if s == "inferred")
        print(f"[{len(items):3d}] {CATEGORIES[cat]}  (audit: {audit_count}, inferred: {inferred_count})")
        # Show inferred entries so user can spot misclassifications
        inferred = [aid for aid, s in items if s == "inferred"]
        if inferred:
            for aid in inferred[:6]:
                print(f"        inferred: {aid}")
            if len(inferred) > 6:
                print(f"        ... +{len(inferred) - 6} more inferred")


def apply_mapping(mapping: dict[str, tuple[str, str]]) -> None:
    text = CATALOG.read_text(encoding="utf-8")
    changed = 0
    missed = []
    for aid, (cat_key, _) in mapping.items():
        new_cat = CATEGORIES[cat_key]
        pattern = re.compile(
            r'("id"\s*:\s*"' + re.escape(aid) + r'"\s*,[^}]*?"buildingSubcategory"\s*:\s*")[^"]*(")',
            re.DOTALL
        )
        new_text, n = pattern.subn(r"\g<1>" + new_cat + r"\g<2>", text, count=1)
        if n == 0:
            missed.append(aid)
        else:
            text = new_text
            changed += 1

    # Validate
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Resulting JSON does not parse: {e}") from e

    # Verify no thumbnailUrl corruption — compare count
    old_thumbs = sum(1 for a in json.loads(CATALOG.read_text(encoding="utf-8")).get("archetypes", []) for v in a.get("variants", []) if v.get("thumbnailUrl"))
    new_thumbs = sum(1 for a in parsed.get("archetypes", []) for v in a.get("variants", []) if v.get("thumbnailUrl"))
    if old_thumbs != new_thumbs:
        raise RuntimeError(f"ThumbnailUrl count changed: {old_thumbs} -> {new_thumbs}. ABORTING.")

    backup = CATALOG.with_suffix(CATALOG.suffix + ".bak-recat")
    backup.write_bytes(CATALOG.read_bytes())
    CATALOG.write_text(text, encoding="utf-8")
    print(f"\n  Updated {changed} archetypes")
    if missed:
        print(f"  Missed {len(missed)} archetypes (regex didn't match — field might be absent):")
        for aid in missed[:10]:
            print(f"    ! {aid}")
    print(f"  Backup saved to {backup.name}")


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    mapping = build_mapping()

    print("=" * 60)
    print(f"Archetypes: {len(mapping)} total")
    audit_count = sum(1 for _, s in mapping.values() if s == "audit")
    inferred_count = sum(1 for _, s in mapping.values() if s == "inferred")
    print(f"  {audit_count} from audit mapping, {inferred_count} keyword-inferred")
    print("=" * 60)
    print()
    show_distribution(mapping)

    if dry_run:
        print("\n[DRY RUN] No files modified.")
        return 0

    print("\nApplying...")
    apply_mapping(mapping)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
