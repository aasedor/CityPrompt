"""
Pass 2: Apply remaining variant overrides with CORRECTED variant IDs.
The first pass applied 52 overrides. This handles the ~63 that failed due to mismatched IDs.
"""

import re

# Corrected variant IDs mapped to actual IDs in buildingArchetypes.json
VARIANT_OVERRIDES = {
    # historical_brick_main_street
    "historical_brick_industrial": {"minFloors": 3, "maxFloors": 6, "suggestedFloorHeight": 4.2, "suggestedAreaSqm": 600},

    # modern_glass_office_institutional
    "glass_office_timber_hybrid": {"minFloors": 5, "maxFloors": 12, "suggestedFloorHeight": 3.6, "suggestedAreaSqm": 2000},

    # mid_century_modern_pavilion_block
    "mid_century_pavilion_glass_steel": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 3.6, "suggestedAreaSqm": 1500},

    # industrial_brick_mixed_use
    "industrial_brick_original_mill": {"minFloors": 4, "maxFloors": 6, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 2000},
    "industrial_brick_powerstation": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 4000},

    # adaptive_reuse_warehouse_lofts
    "warehouse_loft_cast_iron": {"minFloors": 4, "maxFloors": 7, "suggestedFloorHeight": 4.2, "suggestedAreaSqm": 1800},

    # nordic_timber_midrise
    "nordic_timber_mass_timber": {"minFloors": 6, "maxFloors": 12, "suggestedFloorHeight": 3.2, "suggestedAreaSqm": 700},
    "nordic_timber_log_modern": {"minFloors": 2, "maxFloors": 3, "suggestedFloorHeight": 3.0, "suggestedAreaSqm": 400},

    # mediterranean_villa_estate
    "med_villa_greek_island": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 2.8, "suggestedAreaSqm": 200},
    "med_villa_spanish_colonial": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 600},

    # mediterranean_arcade_mixed_use
    "med_arcade_moorish": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 4.5, "suggestedAreaSqm": 1200},

    # parametric_future_hub
    "parametric_diagrid_tower": {"minFloors": 10, "maxFloors": 50, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 2500},

    # autonomous_tech_campus
    "tech_campus_silicon_valley": {"minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 8000},
    "tech_campus_data_center": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 15000},

    # deco_theater_mainstreet
    "deco_theater_movie_palace": {"minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 1200},

    # traditional_vernacular_market_street
    "vernacular_market_souk_bazaar": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 4.5, "suggestedAreaSqm": 400},

    # alpine_mixed_use_lodge
    "alpine_lodge_ski_resort": {"minFloors": 3, "maxFloors": 8, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 1500},

    # transit_podium_residential
    "transit_podium_glass_tower": {"minFloors": 8, "maxFloors": 25, "suggestedFloorHeight": 3.0, "suggestedAreaSqm": 1200},
    "transit_podium_courtyard": {"minFloors": 4, "maxFloors": 8, "suggestedFloorHeight": 3.0, "suggestedAreaSqm": 2200},

    # glass_tower_podium_modern
    "glass_tower_twisted": {"minFloors": 15, "maxFloors": 50, "suggestedFloorHeight": 3.8, "suggestedAreaSqm": 2000},
    "glass_tower_green_terraces": {"minFloors": 12, "maxFloors": 35, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 3000},

    # skyline_glass_office_cluster
    "skyline_cluster_campus_low": {"minFloors": 3, "maxFloors": 6, "suggestedFloorHeight": 3.8, "suggestedAreaSqm": 8000},
    "skyline_cluster_mixed_use_podium": {"minFloors": 15, "maxFloors": 40, "suggestedFloorHeight": 3.8, "suggestedAreaSqm": 2500},

    # monumental_museum_axis
    "museum_industrial_conversion": {"minFloors": 1, "maxFloors": 4, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 5000},

    # eco_urban_bioclimatic_block
    "eco_bioclimatic_tropical": {"minFloors": 5, "maxFloors": 12, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 1200},

    # vertical_forest_residential
    "vertical_forest_bosco": {"minFloors": 15, "maxFloors": 30, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 1500},

    # coastal_resort_terrace_block
    "coastal_resort_stone_cliff": {"minFloors": 2, "maxFloors": 5, "suggestedFloorHeight": 3.2, "suggestedAreaSqm": 1500},

    # coastal_breezeway_mixed_use
    "coastal_breeze_pacific": {"minFloors": 1, "maxFloors": 3, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 500},
    "coastal_breeze_new_england": {"minFloors": 2, "maxFloors": 3, "suggestedFloorHeight": 3.0, "suggestedAreaSqm": 600},

    # custom_contextual_experiment
    "custom_experiment_earthship": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 200},
    "custom_experiment_inflatable": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 300},

    # community_recreation_centre
    "rec_centre_aquatic": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 8.0, "suggestedAreaSqm": 5000},

    # modern_sports_arena
    "sports_arena_open_air": {"minFloors": 1, "maxFloors": 5, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 35000},
    "sports_arena_fieldhouse": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 10.0, "suggestedAreaSqm": 5000},

    # boutique_hotel_tower
    "hotel_urban_boutique": {"minFloors": 4, "maxFloors": 12, "suggestedFloorHeight": 3.2, "suggestedAreaSqm": 1500},
    "hotel_resort": {"minFloors": 2, "maxFloors": 5, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 4000},

    # neoclassical_institutional
    "neoclassical_beaux_arts": {"minFloors": 2, "maxFloors": 6, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 10000},

    # daylight_factory
    "factory_sawtooth_roof": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 8000},
    "factory_brick_timber_mill": {"minFloors": 2, "maxFloors": 5, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 4000},

    # functionalist_brick_industrial
    "brick_multistory_mill": {"minFloors": 4, "maxFloors": 8, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 6000},
    "brick_courtyard_factory": {"minFloors": 2, "maxFloors": 4, "suggestedFloorHeight": 4.5, "suggestedAreaSqm": 12000},

    # structural_expressionism_industrial
    "industrial_geodesic_span": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 15.0, "suggestedAreaSqm": 10000},

    # machine_aesthetic_heavy_industrial
    "heavy_blast_furnace": {"minFloors": 1, "maxFloors": 10, "suggestedFloorHeight": 6.0, "suggestedAreaSqm": 10000},
    "heavy_silo_cluster": {"minFloors": 1, "maxFloors": 8, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 8000},

    # early_20c_megastructure_industrial
    "heavy_craneway_hall": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 15.0, "suggestedAreaSqm": 30000},

    # modern_bigbox_warehouse
    "warehouse_tilt_wall_mega": {"minFloors": 1, "maxFloors": 1, "suggestedFloorHeight": 12.0, "suggestedAreaSqm": 50000},
    "warehouse_multistory_urban": {"minFloors": 3, "maxFloors": 5, "suggestedFloorHeight": 5.0, "suggestedAreaSqm": 10000},

    # parkitecture_recreational
    "rec_log_cabin_vernacular": {"minFloors": 1, "maxFloors": 2, "suggestedFloorHeight": 3.5, "suggestedAreaSqm": 800},

    # chateauesque_hotel — need actual ID
    "hotel_scottish_baronial": {"minFloors": 3, "maxFloors": 6, "suggestedFloorHeight": 4.0, "suggestedAreaSqm": 8000},
}


def apply_overrides(filepath: str) -> int:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    applied = 0
    skipped = 0

    for variant_id, specs in VARIANT_OVERRIDES.items():
        if f'"id": "{variant_id}"' not in content:
            print(f"  WARNING: variant '{variant_id}' not found")
            skipped += 1
            continue

        id_pos = content.find(f'"id": "{variant_id}"')
        block_end = content.find('}', id_pos)
        block = content[id_pos:block_end]
        if '"minFloors"' in block:
            print(f"  SKIP: '{variant_id}' already has overrides")
            skipped += 1
            continue

        # Find thumbnailUrl for this variant
        thumb_pattern = '"thumbnailUrl":'
        thumb_pos = content.find(thumb_pattern, id_pos)

        if thumb_pos == -1 or thumb_pos > id_pos + 800:
            brace_pos = content.find('}', id_pos)
            if brace_pos == -1:
                skipped += 1
                continue
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

        line_end = content.find('\n', thumb_pos)
        if line_end == -1:
            skipped += 1
            continue

        line_content = content[thumb_pos:line_end].rstrip()
        line_start = content.rfind('\n', 0, thumb_pos) + 1
        indent = ''
        for ch in content[line_start:thumb_pos]:
            if ch in (' ', '\t'):
                indent += ch
            else:
                break

        if not line_content.endswith(','):
            content = content[:line_end] + ',' + content[line_end:]
            line_end += 1

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

    print(f"\nPass 2 done! Applied {applied}, skipped {skipped}")
    return applied


if __name__ == '__main__':
    apply_overrides('frontend/src/data/buildingArchetypes.json')
