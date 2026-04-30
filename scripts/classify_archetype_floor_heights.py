"""
Classify each of the 218 building archetypes into a typology bucket and assign
a default `suggestedFloorHeight`. Used by Phase 3.5 floor-height backfill.

Default heights from research (BCO, GSA P100, IBC/IRC, FAA, FGI, Beranek, etc.).
See docs/ARCHETYPE_SIZES_FIX_PLAN_2026_04_28.md and the floor-height research
agent's results for citations.

Numbers are PER-FLOOR (slab-to-slab for multi-storey; clear-volume-divided-by-
catalog-floor-count for single-volume types like stadium/cathedral, where the
catalog already represents sub-decks as multiple floors).

Usage: python scripts/classify_archetype_floor_heights.py
       (dry-run only — prints the assignments)
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CATALOG = "frontend/src/data/buildingArchetypes.json"

# Typology -> per-floor default height (m). Order is most-specific-first;
# first match wins. SHORT WORDS use word boundaries (\b) so "inn" doesn't match
# "inner", "expo" doesn't match "expo_line", etc.
TYPOLOGY_RULES = [
    # === Transit infrastructure (specific — must match before "civic" which matches "civic_infrastructure" tag) ===
    ("ctrain_downtown|skytrain_elevated|streetcar_platform|urban_light_rail|rail_stop|transit_shelter",
                                                                          ("transit_platform", 4.5)),
    ("vertiport|heliport|airport_terminal|aviation_facility",             ("vertiport_airport", 6.0)),
    ("transit_hub|train_shed|cruise_ferry|ferry_terminal|intermodal|station_block|station_hub|halifax_ferry",
                                                                          ("transit_hub", 6.0)),

    # === Massive single-volume buildings (catalog uses multi-floor model) ===
    ("aircraft_hangar|airplane_hangar",                                   ("aircraft_hangar", 15.0)),
    ("power_station|powerstation|waste_to_energy|coal_plant|nuclear_plant",("power_plant", 15.0)),
    ("turbine_hall|machine_aesthetic_heavy|early_20c_megastructure",      ("heavy_industrial", 12.0)),
    ("modern_sports_arena|monumental_antiquity_arena|high_tech.*arena|concrete_megastructure_arena|outdoor_sports_stadium|stadium",
                                                                          ("stadium_arena", 8.0)),
    ("amphitheater|amphitheatre",                                         ("open_air_stadium", 6.5)),
    ("aquatic_natatorium|natatorium|swim",                                ("aquatic_natatorium", 8.5)),

    # === Towers and high-rises (4.0 office, 3.2 residential) ===
    ("art_deco_setback_tower|streamline_moderne_tower|setback_tower",      ("art_deco_tower", 4.0)),
    ("glass_tower_modern|glass_tower_podium|skyline_glass_office_cluster|skyline_cluster",
                                                                          ("glass_office_tower", 4.0)),
    ("corporate_tower|skyscraper|supertall|condo_podium_tower|condo_tower|residential_tower|highrise_residential|residential_highrise",
                                                                          ("podium_tower_resi", 3.3)),
    ("vancouverism_tower_podium|vancouverism|calgary_15_connected_tower|calgary_plus_15",
                                                                          ("podium_tower_mixed", 3.5)),
    ("hotel.*tower|tower.*hotel|chateauesque",                            ("hotel_tower", 3.6)),
    ("vertical_farm|farmscraper",                                         ("vertical_farm", 5.5)),
    ("vertical_forest",                                                   ("vertical_forest", 3.4)),
    ("student_residence_tower",                                           ("student_residence", 3.3)),

    # === Religious / monumental ===
    ("cathedral|basilica|church|temple|mosque|chapel|synagogue",          ("cathedral_temple", 12.0)),

    # === Cultural / performance ===
    ("opera_house|concert_hall|symphony_hall",                            ("concert_hall", 6.5)),
    ("theater|theatre|cinema_palace|movie_palace",                        ("theater", 6.0)),
    ("museum|gallery|library",                                            ("museum_library", 5.0)),

    # === Civic monumental ===
    ("monumental_courthouse|courthouse_axis|capitol|state_house|legislature|government",
                                                                          ("courthouse_civic", 5.5)),
    ("monumental|civic_classical|civic_monumental",                       ("monumental_civic", 5.5)),
    ("second_empire_civic|montreal_second_empire_civic",                  ("second_empire_civic", 4.5)),
    ("modernist_civic_block|contemporary_civic|brutalist_institutional|neoclassical_institutional",
                                                                          ("civic_institutional", 4.5)),
    ("monumental_museum",                                                 ("museum_grand", 6.5)),
    ("civic|municipal|town_hall|hall_of_records",                          ("civic_general", 4.5)),

    # === Healthcare / labs ===
    ("regional_hospital|hospital|medical_center",                         ("hospital", 4.4)),
    ("biophilic_modern_healthcare|art_deco_healthcare|functionalist_healthcare",
                                                                          ("healthcare", 4.4)),
    ("research_laboratory|research_lab|innovation_hub|biotech|science_engineering_lab",
                                                                          ("research_lab", 4.6)),

    # === Education ===
    ("collegiate_gothic|university_library|university_academic|academic_complex|administrative_faculty|graduate_family",
                                                                          ("collegiate", 4.0)),
    ("campus_lecture_hall|campus_dining_hall|student_union|campus_recreation|lecture_hall",
                                                                          ("campus_assembly", 4.5)),
    ("school|college|education|ecole|elementary|kindergarten",            ("school", 3.8)),
    ("calgary_cbe_brutalist_hq",                                          ("school_brutalist", 4.0)),
    ("campus_parking_structure|parking_garage|parking_structure",         ("parking_garage", 3.3)),
    ("campus_utilities|central_utilities_plant|energy_centre",            ("utility_plant", 6.0)),

    # === Hospitality ===
    ("boutique_hotel(?!_tower)",                                          ("boutique_hotel", 3.8)),
    (r"\binn\b|\blodge\b|resort_hotel|alpine.*lodge|alpine_mixed_use_lodge", ("lodge_resort", 3.5)),
    ("chateauesque_grand_railway_hotel",                                  ("railway_hotel", 4.2)),

    # === Cultural rec / community ===
    ("postmodern_community_rec|community_recreation|recreation_centre|recreation_center|community_centre",
                                                                          ("rec_centre", 6.5)),
    ("contemporary_sustainable_rec|sustainable_rec|rec_centre.*biophilic",("rec_centre_biophilic", 6.5)),
    ("climbing_wall_building",                                            ("climbing_wall", 6.0)),
    ("brewery|distillery",                                                ("brewery_distillery", 5.5)),
    (r"\bconvention\b|\bexhibition\b|exhibition_hall|expo_centre|expo_center", ("convention_centre", 7.0)),

    # === Transit moved to top so civic_infrastructure tag doesn't poach streetcar stops ===

    # === Industrial ===
    ("modern_bigbox|big_box|modern_big_box_logistics|e_commerce_fulfillment|hyperscale_data_center|data_center|fulfillment_center",
                                                                          ("modern_logistics", 8.5)),
    ("midcentury_distribution_warehouse|mid_century_distribution_warehouse",
                                                                          ("distribution_warehouse", 7.0)),
    ("adaptive_reuse_warehouse_lofts|warehouse_loft|amsterdam_canal_warehouse|halifax_waterfront_warehouse|junction_converted_industrial_loft|old_montreal_warehouse_loft|romanesque_revival_warehouse|soho_cast_iron_loft|barcelona_modernist_workshop",
                                                                          ("warehouse_loft", 4.2)),
    ("industrial_park_modernism|art_deco_industrial|functionalist_brick_industrial|structural_expressionism_industrial|corrugated_vernacular_industrial|brutalist_utility_heavy_industrial|industrial_brick_mixed_use",
                                                                          ("industrial_factory", 6.0)),
    ("daylight_factory",                                                  ("daylight_factory", 5.0)),
    ("solar_farm|wind_farm|solar_csp",                                    ("solar_infra", 6.0)),

    # === Speculative / Custom ===
    ("autonomous_tech_campus|silicon_valley|tech_campus",                 ("tech_campus", 4.0)),
    ("parametric_future_hub",                                             ("parametric_hub", 4.5)),
    ("immersive_experience_venue",                                        ("immersive_venue", 8.0)),
    ("ev_charging_hub|mobility_station",                                  ("ev_hub", 5.0)),
    ("custom_prompt_ready|custom_contextual",                             ("custom_generic", 3.5)),

    # === Mid-rise / mixed-use (specific names before generic) ===
    ("nordic_timber_midrise|scandinavian_urban_residential",              ("nordic_midrise", 3.2)),
    ("contemporary_midrise|condo_midrise|residential_superblock|eco_urban_bioclimatic_block|coastal_breezeway_mixed_use|coastal_resort_terrace_block",
                                                                          ("midrise_residential", 3.2)),
    ("parisian_midrise|parisian_mid_rise|parisian_boulevard|haussmann_boulevard|grand_magasin",
                                                                          ("parisian_midrise", 3.4)),
    ("contemporary_townhouse_courtyard|courtyard_family_housing|minimalist_courtyard_block|vertical_garden_residential",
                                                                          ("midrise_courtyard", 3.2)),
    ("transit_oriented_station_block|transit_podium_residential",        ("transit_oriented", 3.3)),
    ("mediterranean_arcade_mixed_use|coastal_breezeway|mediterranean_arcade",
                                                                          ("med_mixed_use", 3.6)),
    ("traditional_vernacular_market_street|vernacular_courtyard_housing|shophouse_southeast_asian|japanese_machiya|japanese_contemporary_lanehouse|amsterdam_.*_house|amsterdam_brown_cafe|amsterdam_hofje",
                                                                          ("vernacular_low_rise", 3.0)),

    # === Senior living ===
    ("senior_living|assisted_living|retirement|aged_care",                ("senior_living", 3.2)),

    # === Storefront / main street commercial ===
    ("historical_brick_main_street|victorian_heritage_avenue|inglewood_heritage_brick_commercial|new_york_corner_bodega|corner_dépanneur|montreal_depanneur|barcelona_mercat|parisian_cafe_brasserie|hydrostone_neighbourhood_house|halifax_painted_clapboard_row",
                                                                          ("main_street", 3.6)),
    ("deco_theater_mainstreet|art_deco_setback|art_deco_corner_block",    ("art_deco_main_street", 3.8)),

    # === Townhouses / rowhouses / brownstones ===
    ("brownstone_rowhouse_frontage|classic_brownstone_streetwall|brick_rowhouse_terrace|toronto_brick_rowhouse|toronto_bay_and_gable|bay_and_gable|new_york_walk_up_tenement|halifax_painted_clapboard_row|montreal_plateau_triplex|montreal_duplex|mile_end_cultural_triplex",
                                                                          ("rowhouse_brownstone", 3.2)),
    ("regency_stucco_terrace|georgian_terrace|victorian_bay_window_terrace|edwardian_semi_detached|london_mews_house",
                                                                          ("heritage_terrace", 3.4)),
    ("toronto_annex_mansion|annex_mansion|toronto_edwardian_foursquare|edwardian_foursquare|prewar_emery_roth|new_york_pre_war_apartment",
                                                                          ("foursquare_prewar", 3.4)),

    # === Bungalow / detached / cottage / villa ===
    ("calgary_inner_city_bungalow|vancouver_craftsman_bungalow|vancouver_special|calgary_modern_infill_house|vancouver_laneway_house|detached_contemporary_infill",
                                                                          ("bungalow_infill", 2.9)),
    ("mountain_alpine_chalet|farnsworth_house|mediterranean_villa_estate|coastal_breezeway_house",
                                                                          ("villa_chalet", 3.0)),

    # === Office / commercial generic (less-specific fallbacks) ===
    ("modern_glass_office|corporate_office_campus_headquarters|junction_converted_industrial_loft",
                                                                          ("modern_office", 4.0)),
    ("art_deco_theater|art_deco_hotel|art_deco_healthcare",               ("art_deco_civic", 4.0)),
    ("shophouse",                                                         ("shophouse", 3.4)),

    # === Park architecture (lodges, ranger stations) ===
    ("parkitecture",                                                      ("park_architecture", 3.5)),

    # === Fire station / police / service ===
    ("modern_fire_station|fire_station|police_station",                   ("emergency_service", 4.0)),

    # === Boutique hotels (tower vs not — the tower one already handled above) ===
    ("boutique_hotel_tower",                                              ("boutique_hotel_tower", 3.8)),

    # === Final fallback for anything unmatched ===
]

DEFAULT_FALLBACK = ("commercial_generic", 3.8)


def classify(arch: dict) -> tuple[str, float]:
    """Return (typology_label, default_height_m) for an archetype."""
    needle_parts = [
        arch.get("id", ""),
        arch.get("title", ""),
        arch.get("buildingSubcategory", ""),
        " ".join(arch.get("generationTags", []) or []),
    ]
    needle = " ".join(needle_parts).lower()
    for pattern, (label, h) in TYPOLOGY_RULES:
        if re.search(pattern, needle):
            return label, h
    return DEFAULT_FALLBACK


def main():
    with open(CATALOG, "r", encoding="utf-8") as f:
        data = json.load(f)
    arches = data["archetypes"]

    classifications = []
    for a in arches:
        label, h = classify(a)
        classifications.append((a["id"], label, h, a.get("minFloors"), a.get("maxFloors")))

    # Group by typology for review
    by_label = {}
    for aid, label, h, mnf, mxf in classifications:
        by_label.setdefault((label, h), []).append((aid, mnf, mxf))

    print(f"Classified {len(arches)} archetypes into {len(by_label)} typology buckets:\n")
    for (label, h), ids in sorted(by_label.items(), key=lambda x: -len(x[1])):
        print(f"== {label} (default fh={h}m, n={len(ids)}) ==")
        for aid, mnf, mxf in ids[:8]:
            implied = mxf * h if mxf else "?"
            print(f"   {aid:55} floors={mnf}-{mxf}  implied max height: {implied}m")
        if len(ids) > 8:
            print(f"   ... and {len(ids)-8} more")
        print()

    # Anomaly detection: implied total height way out of typology range
    print("=" * 70)
    print("ANOMALY CHECK — implied max heights that look wrong:")
    for aid, label, h, mnf, mxf in classifications:
        if not mxf:
            continue
        implied_max = mxf * h
        # flags: < 5m for any building (too short to occupy) or > 250m (too tall, except true supertalls)
        if implied_max < 5:
            print(f"  {aid:55} {label:25} fh={h}  floors={mnf}-{mxf}  -> {implied_max}m  (TOO SHORT)")
        elif implied_max > 200 and "tower" not in label and "vertical_farm" not in label and "supertall" not in label:
            print(f"  {aid:55} {label:25} fh={h}  floors={mnf}-{mxf}  -> {implied_max}m  (TOO TALL?)")


if __name__ == "__main__":
    main()
