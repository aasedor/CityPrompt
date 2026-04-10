"""
Apply per-variant floor/area specs to buildingArchetypes.json using TEXT-LEVEL insertion.
Does NOT use json.dump to avoid corrupting thumbnailUrl paths (see CLAUDE.md).

Each override adds minFloors, maxFloors, suggestedFloorHeight, suggestedAreaSqm
fields to specific variant entries identified by their "id" field.
"""

import re
import sys

# All researched variant overrides: variant_id -> specs
VARIANT_OVERRIDES = {
    # === BATCH 1 (archetypes 1-25) ===

    # historical_brick_main_street
    "industrial_loft": {"minFloors": 3, "maxFloors": 6, "suggestedFloorHeight": 4.2, "suggestedAreaSqm": 600},

    # modern_glass_office_institutional
    "mass_timber_hybrid": {"minFloors": 5, "maxFloors": 12, "suggestedFloorHeight": 3.6, "suggestedAreaSqm": 2000},

    # mid_century_modern_pavilion_block
    "glass_and_steel_pavilion": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 3.6, "suggestedAreaSqm": 1500},

    # industrial_brick_mixed_use
    "victorian_mill": {"minFloors": 4, "maxFloors": 6, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 2000},
    "power_station": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 4000},

    # adaptive_reuse_warehouse_lofts
    "cast_iron": {"minFloors": 4, "maxFloors": 7, "suggestedFloorHeight": 4.2, "suggestedAreaSqm": 1800},
    "maritime_wharf": {"minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 4.5, "suggestedAreaSqm": 3000},

    # nordic_timber_midrise
    "mass_timber_tower": {"minFloors": 6, "maxFloors": 12, "suggestedFloorHeight": 3.2, "suggestedAreaSqm": 700},
    "log_construction": {"minFloors": 2, "maxFloors": 3, "suggestedFloorHeight": 3.0, "suggestedAreaSqm": 400},

    # mediterranean_villa_estate
    "greek_island": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 2.8, "suggestedAreaSqm": 200},
    "spanish_colonial": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 600},

    # mediterranean_arcade_mixed_use
    "moorish_souk": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 4.5, "suggestedAreaSqm": 1200},

    # parametric_future_hub
    "diagrid": {"minFloors": 10, "maxFloors": 50, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 2500},

    # autonomous_tech_campus
    "silicon_valley_pavilion": {"minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 8000},
    "data_center_monolith": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 15000},

    # deco_theater_mainstreet
    "movie_palace": {"minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 1200},

    # traditional_vernacular_market_street
    "covered_souk": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 4.5, "suggestedAreaSqm": 400},
    "japanese_shotengai": {"minFloors": 2, "maxFloors": 3, "suggestedFloorHeight": 3.0, "suggestedAreaSqm": 150},

    # === BATCH 2 (archetypes 26-50) ===

    # vernacular_courtyard_housing
    "vernacular_courtyard_chinese_siheyuan": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 400},
    "vernacular_courtyard_moroccan_riad": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 200},
    "vernacular_courtyard_indian_haveli": {"minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 4.5, "suggestedAreaSqm": 350},

    # mountain_alpine_chalet
    "stone_berghaus": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 3.0, "suggestedAreaSqm": 350},

    # alpine_mixed_use_lodge
    "modern_ski_resort": {"minFloors": 3, "maxFloors": 8, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 1500},

    # transit_podium_residential
    "glass_tower_on_podium": {"minFloors": 8, "maxFloors": 25, "suggestedFloorHeight": 3.0, "suggestedAreaSqm": 1200},
    "courtyard_podium": {"minFloors": 4, "maxFloors": 8, "suggestedFloorHeight": 3.0, "suggestedAreaSqm": 2200},
    "heritage_podium_modern_tower": {"minFloors": 6, "maxFloors": 20, "suggestedFloorHeight": 3.0, "suggestedAreaSqm": 1500},

    # glass_tower_podium_modern
    "twisted_spiraling": {"minFloors": 15, "maxFloors": 50, "suggestedFloorHeight": 3.8, "suggestedAreaSqm": 2000},
    "green_terrace": {"minFloors": 12, "maxFloors": 35, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 3000},

    # skyline_glass_office_cluster
    "low_rise_campus": {"minFloors": 3, "maxFloors": 6, "suggestedFloorHeight": 3.8, "suggestedAreaSqm": 8000},
    "mixed_use_podium": {"minFloors": 15, "maxFloors": 40, "suggestedFloorHeight": 3.8, "suggestedAreaSqm": 2500},

    # monumental_museum_axis
    "industrial_conversion": {"minFloors": 1, "maxFloors": 4, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 5000},
    "earth_sheltered": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 6000},

    # japanese_machiya_mixed_use
    "nagaya_row": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 2.7, "suggestedAreaSqm": 80},

    # eco_urban_bioclimatic_block
    "tropical_bioclimatic": {"minFloors": 5, "maxFloors": 12, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 1200},
    "rammed_earth_timber": {"minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 800},

    # vertical_forest_residential
    "bosco_verticale": {"minFloors": 15, "maxFloors": 30, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 1500},
    "terraced_mountain_garden": {"minFloors": 5, "maxFloors": 15, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 2500},

    # coastal_resort_terrace_block
    "cliffside_stone": {"minFloors": 2, "maxFloors": 5, "suggestedFloorHeight": 3.2, "suggestedAreaSqm": 1500},

    # coastal_breezeway_mixed_use
    "pacific_island": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 500},
    "new_england_shingled": {"minFloors": 2, "maxFloors": 3, "suggestedFloorHeight": 3.0, "suggestedAreaSqm": 600},

    # custom_contextual_experiment
    "earthship": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 200},
    "pneumatic": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 300},
    "3d_printed": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 3.0, "suggestedAreaSqm": 150},

    # community_recreation_centre
    "aquatic_centre": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 8.0, "suggestedAreaSqm": 5000},
    "multipurpose_arena": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 10.0, "suggestedAreaSqm": 6000},

    # modern_sports_arena
    "open_air_stadium": {"minFloors": 1, "maxFloors": 5, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 35000},
    "collegiate_fieldhouse": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 10.0, "suggestedAreaSqm": 5000},
    "velodrome": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 12.0, "suggestedAreaSqm": 15000},

    # boutique_hotel_tower
    "urban_boutique": {"minFloors": 4, "maxFloors": 12, "suggestedFloorHeight": 3.2, "suggestedAreaSqm": 1500},
    "resort_hotel": {"minFloors": 2, "maxFloors": 5, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 4000},
    "contemporary_tower": {"minFloors": 10, "maxFloors": 30, "suggestedFloorHeight": 3.2, "suggestedAreaSqm": 2000},

    # neoclassical_institutional
    "beaux_arts": {"minFloors": 2, "maxFloors": 6, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 10000},
    "federal_style": {"minFloors": 2, "maxFloors": 3, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 3000},

    # === BATCH 3 (archetypes 51-75) ===

    # daylight_factory
    "sawtooth_roof": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 8000},
    "brick_timber_mill": {"minFloors": 2, "maxFloors": 5, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 4000},

    # functionalist_brick_industrial
    "multi_story_mill": {"minFloors": 4, "maxFloors": 8, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 6000},
    "courtyard_factory": {"minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 4.5, "suggestedAreaSqm": 12000},

    # structural_expressionism_industrial
    "geodesic_span": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 15.0, "suggestedAreaSqm": 10000},

    # machine_aesthetic_heavy_industrial
    "blast_furnace": {"minFloors": 1, "maxFloors": 10, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 10000},
    "silo_cluster": {"minFloors": 1, "maxFloors": 8, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 8000},
    "pipeline_network": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 30000},

    # early_20c_megastructure_industrial
    "craneway_hall": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 15.0, "suggestedAreaSqm": 30000},

    # modern_bigbox_warehouse
    "tilt_wall_mega": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 12.0, "suggestedAreaSqm": 50000},
    "multi_story_urban": {"minFloors": 3, "maxFloors": 5, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 10000},

    # parkitecture_recreational
    "log_cabin": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 800},

    # chateauesque_hotel
    "alpine_chateau": {"minFloors": 3, "maxFloors": 6, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 8000},

    # === BATCH 4 (archetypes 76-98) ===

    # resort_modernism_hotel
    "hotel_balinese_villa": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 4.5, "suggestedAreaSqm": 2000},
    "hotel_miami_art_deco": {"minFloors": 3, "maxFloors": 5, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 3000},
    "hotel_eco_lodge": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 1500},

    # corporate_tower_hotel
    "hotel_portman_atrium": {"minFloors": 15, "maxFloors": 52, "suggestedFloorHeight": 3.2, "suggestedAreaSqm": 30000},

    # contemporary_transit_hub
    "transit_calatrava_organic": {"minFloors": 1, "maxFloors": 4, "suggestedFloorHeight": 10.0, "suggestedAreaSqm": 20000},
    "transit_minimalist_concrete": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 4000},

    # climbing_wall_building
    "climbing_crucible": {"minFloors": 3, "maxFloors": 6, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 8000},
    "climbing_overhang": {"minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 5000},
    "climbing_spine": {"minFloors": 20, "maxFloors": 35, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 2500},
    "climbing_reef": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 4000},

    # waste_to_energy_plant
    "wte_ski_slope": {"minFloors": 5, "maxFloors": 12, "suggestedFloorHeight": 8.0, "suggestedAreaSqm": 41000},
    "wte_hillside": {"minFloors": 3, "maxFloors": 8, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 30000},
    "wte_mosaic": {"minFloors": 3, "maxFloors": 10, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 25000},

    # senior_living_complex
    "senior_garden_courtyard": {"minFloors": 2, "maxFloors": 3, "suggestedFloorHeight": 3.2, "suggestedAreaSqm": 12000},
    "senior_urban_tower": {"minFloors": 8, "maxFloors": 15, "suggestedFloorHeight": 3.2, "suggestedAreaSqm": 5000},
    "senior_timber_cohousing": {"minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 3.2, "suggestedAreaSqm": 3000},
    "senior_mediterranean_resort": {"minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 10000},

    # brewery_distillery
    "brewery_highland_distillery": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 4000},
    "brewery_crystal_brewhouse": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 6000},
    "brewery_farmstead": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 2500},

    # solar_farm_agrivoltaics
    "solar_csp_tower": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 200.0, "suggestedAreaSqm": 500000},

    # immersive_experience_venue
    "immersive_geodesic_dome": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 20.0, "suggestedAreaSqm": 3000},
    "immersive_mirror_droplet": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 5000},
    "immersive_underground": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 6000},

    # modern_fire_station
    "fire_craftsman_neighborhood": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 1500},

    # concert_hall_modern
    "concert_sculptural_organic": {"minFloors": 3, "maxFloors": 8, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 20000},
    "concert_timber_acoustic": {"minFloors": 2, "maxFloors": 5, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 8000},
    "concert_civic_landmark": {"minFloors": 3, "maxFloors": 8, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 18000},

    # vertiport_evtol
    "vertiport_rooftop": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 1500},
    "vertiport_transit_hub": {"minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 10000},

    # shophouse_southeast_asian
    "shophouse_adaptive_reuse": {"minFloors": 2, "maxFloors": 5, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 600},
    "shophouse_contemporary": {"minFloors": 3, "maxFloors": 6, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 800},

    # food_hall_market_hall
    "market_historic_iron_glass": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 10.0, "suggestedAreaSqm": 8000},
    "market_contemporary": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 6000},
    "market_open_air_pavilion": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 3000},

    # ev_charging_hub
    "ev_highway_reststop": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 5000},
    "ev_urban_garden": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 1500},

    # hyperscale_data_center
    "datacenter_campus": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 80000},
    "datacenter_urban_stealth": {"minFloors": 4, "maxFloors": 8, "suggestedFloorHeight": 4.5, "suggestedAreaSqm": 20000},
    "datacenter_futuristic_modular": {"minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 4.5, "suggestedAreaSqm": 40000},

    # mall_redevelopment
    "mall_new_town_center": {"minFloors": 2, "maxFloors": 6, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 60000},
    "mall_open_air_retrofit": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 45000},
    "mall_community_campus": {"minFloors": 1, "maxFloors": 4, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 40000},
    "mall_green_grid": {"minFloors": 2, "maxFloors": 8, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 50000},

    # terraced_stepped_building
    "terraced_ridgeline": {"minFloors": 5, "maxFloors": 12, "suggestedFloorHeight": 3.2, "suggestedAreaSqm": 8000},
    "terraced_canopy_tower": {"minFloors": 15, "maxFloors": 27, "suggestedFloorHeight": 3.2, "suggestedAreaSqm": 4000},
    "terraced_hillside_quarter": {"minFloors": 2, "maxFloors": 5, "suggestedFloorHeight": 3.2, "suggestedAreaSqm": 6000},
    "terraced_cascade_podium": {"minFloors": 4, "maxFloors": 15, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 8000},

    # farnsworth_house_glass_pavilion
    "farnsworth_river_gallery": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 1000},
}

def apply_overrides(filepath: str) -> int:
    """Apply variant overrides using text-level insertion. Returns count of applied overrides."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    applied = 0
    skipped = 0

    for variant_id, specs in VARIANT_OVERRIDES.items():
        # Skip the vertical farm variants (already applied manually)
        if variant_id in ('farm_glass_greenhouse_tower', 'farm_led_indoor', 'farm_timber_farmscraper', 'farm_rooftop_greenhouse'):
            continue

        # Check if this variant already has overrides
        if f'"id": "{variant_id}"' not in content:
            print(f"  WARNING: variant '{variant_id}' not found in JSON")
            skipped += 1
            continue

        # Check if already has minFloors (already applied)
        # Find the variant block
        id_pos = content.find(f'"id": "{variant_id}"')
        # Look ahead ~500 chars for the next variant or closing brace
        block_end = content.find('}', id_pos)
        block = content[id_pos:block_end]
        if '"minFloors"' in block:
            print(f"  SKIP: variant '{variant_id}' already has overrides")
            skipped += 1
            continue

        # Find the thumbnailUrl line for this variant (insert after it)
        # Strategy: find "id": "variant_id", then find the next "thumbnailUrl" line
        search_start = id_pos
        thumb_pattern = '"thumbnailUrl":'
        thumb_pos = content.find(thumb_pattern, search_start)

        if thumb_pos == -1 or thumb_pos > id_pos + 800:
            # Try inserting before the closing brace of this variant instead
            # Find the closing } for this variant entry
            brace_pos = content.find('}', id_pos)
            if brace_pos == -1:
                print(f"  ERROR: could not find insertion point for '{variant_id}'")
                skipped += 1
                continue

            # Insert before the closing brace
            indent = '          '
            insert_text = (
                f',\n'
                f'{indent}"minFloors": {specs["minFloors"]},\n'
                f'{indent}"maxFloors": {specs["maxFloors"]},\n'
                f'{indent}"suggestedFloorHeight": {specs["suggestedFloorHeight"]},\n'
                f'{indent}"suggestedAreaSqm": {specs["suggestedAreaSqm"]}'
            )
            content = content[:brace_pos] + insert_text + '\n' + content[brace_pos:]
            applied += 1
            continue

        # Find the end of the thumbnailUrl line
        line_end = content.find('\n', thumb_pos)
        if line_end == -1:
            print(f"  ERROR: could not find line end for '{variant_id}'")
            skipped += 1
            continue

        # Check if line ends with comma
        line_content = content[thumb_pos:line_end].rstrip()

        # Determine indentation (match the thumbnailUrl line)
        line_start = content.rfind('\n', 0, thumb_pos) + 1
        indent = ''
        for ch in content[line_start:thumb_pos]:
            if ch in (' ', '\t'):
                indent += ch
            else:
                break

        # Ensure the thumbnailUrl line ends with a comma
        if not line_content.endswith(','):
            # Add comma to end of thumbnailUrl line
            content = content[:line_end] + ',' + content[line_end:]
            line_end += 1

        # Build the override text
        insert_text = (
            f'\n'
            f'{indent}"minFloors": {specs["minFloors"]},\n'
            f'{indent}"maxFloors": {specs["maxFloors"]},\n'
            f'{indent}"suggestedFloorHeight": {specs["suggestedFloorHeight"]},\n'
            f'{indent}"suggestedAreaSqm": {specs["suggestedAreaSqm"]}'
        )

        content = content[:line_end] + insert_text + content[line_end:]
        applied += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\nDone! Applied {applied} overrides, skipped {skipped}")
    return applied


if __name__ == '__main__':
    filepath = 'frontend/src/data/buildingArchetypes.json'
    apply_overrides(filepath)
