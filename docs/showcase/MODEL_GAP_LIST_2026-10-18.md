# Catalogue archetypes with complete reference images but no in-use 3D model, 2026-10-18

This lists every catalogue archetype that has a complete set of quality reference images but no 3D model that the app currently uses.

**Reference images.** An archetype counts as having quality references when it appears in the `complete*Ids` lists of `frontend/src/data/archetypeReferenceAvailability.json`. Archetypes with missing or partial references are left out.

**In-use model.** An archetype counts as modelled if any of these registries covers it:

- **Buildings:**
  - the current native models in `backend/app/data/native_model_contract.json`, mapped from catalogue variant to archetype;
  - LEGO modules in `seed/model-library/model_library.json`;
  - runtime LEGO families in `frontend/public/families/`;
  - the two RLASM keepers in `tools/archetype_compiler/rlasm_keeper_registry.json` that map to catalogue archetypes.
- **Parks and streets:**
  - the executable public-realm LEGO families in `backend/app/services/public_realm_lego.py`;
  - the street families in `streetFamilyCatalog.ts`;
  - native park pilots (`nativeParks.json`) and native street pilots (`nativeStreetPilots.json`);
  - park kits in `frontend/public/park-kits/`;
  - the landscape pilots: the neighbourhood park, the park trio and the sports parks.

A park ground profile on its own is not counted as a model. It only drives the generic stand-in drawing that catalogue cards without a family receive.

**Clay candidates.** Families built in the clay waves on this branch are not enrolled or in use, so their archetypes still appear here. The "clay candidate" column names the family where one exists.

**Near-equivalents.** Pilots that are near-equivalents under a different id are not counted. Examples:

- the student "Timber and stone square" next to the London garden square;
- the student "Pedestrian Market Street" next to the Stephen Avenue mall.

Before building any entry, check the closest existing pilot.

## Summary

| domain | archetypes with complete references | with an in-use model | **without one (listed below)** |
|---|---|---|---|
| Buildings | 224 | 111 | **113** |
| Parks and plazas | 130 | 51 | **79** |
| Streets and paths | 115 | 30 | **85** |
| Total | 469 | 192 | **277** |

22 of the listed archetypes already have a clay candidate on this branch. None of those candidates is enrolled.

## Buildings (113)

### Agriculture (1)

| archetype id | title | clay candidate |
|---|---|---|
| `vertical_farm_indoor_agriculture` | Vertical Farm Indoor Agriculture | `clay_led_grow_block` |

### Civic / Institutional (5)

| archetype id | title | clay candidate |
|---|---|---|
| `calgary_cbe_brutalist_hq` | Calgary Board of Education HQ |  |
| `contemporary_civic` | Contemporary Civic |  |
| `halifax_georgian_colonial` | Halifax Georgian Colonial |  |
| `montreal_second_empire_civic` | Second Empire Civic Building | `clay_second_empire_city_hall` |
| `neoclassical_institutional` | Neoclassical Institutional |  |

### Commercial — Main Street / Heritage Retail (6)

| archetype id | title | clay candidate |
|---|---|---|
| `barcelona_corner_chamfer` | Barcelona Corner Chamfer | `clay_chamfer_corner_dome_block` |
| `calgary_sandstone_heritage` | Calgary Sandstone Heritage |  |
| `corner_dépanneur` | Corner Dépanneur |  |
| `gastown_heritage_commercial` | Gastown Heritage Commercial |  |
| `halifax_waterfront_warehouse` | Halifax Waterfront Warehouse |  |
| `old_montreal_limestone_commercial` | Old Montreal Limestone Commercial |  |

### Commercial — Market / Specialty Retail (4)

| archetype id | title | clay candidate |
|---|---|---|
| `grand_magasin` | Grand Magasin | `clay_grand_magasin` |
| `marche_couvert` | Marche Couvert |  |
| `parisian_corner_with_dome` | Parisian Corner with Dome | `clay_zinc_dome_corner_block` |
| `passage_couvert` | Passage Couvert |  |

### Commercial — Mixed-Use Mid-Rise (4)

| archetype id | title | clay candidate |
|---|---|---|
| `halifax_maritime_commercial` | Halifax Maritime Commercial |  |
| `mall_redevelopment` | Mall Redevelopment |  |
| `new_york_art_deco_tower` | New York Art Deco Tower |  |
| `parisian_mid_rise` | Parisian Mid Rise |  |

### Commercial — Office / Office Tower (3)

| archetype id | title | clay candidate |
|---|---|---|
| `calgary_15_connected_tower` | Calgary 15 Connected Tower |  |
| `calgary_plus_15_connected_tower` | Calgary +15 Connected Tower | `clay_plus15_glass_office_tower` |
| `glass_tower_modern` | Glass Tower Modern |  |

### Education (11)

| archetype id | title | clay candidate |
|---|---|---|
| `campus_dining_hall_food_court` | Campus Dining Hall Food Court |  |
| `campus_lecture_hall_complex` | Campus Lecture Hall Complex | `clay_vaulted_lecture_hall` |
| `campus_parking_structure` | Campus Parking Structure | `clay_brick_parkade` |
| `campus_recreation_athletics_centre` | Campus Recreation Athletics Centre |  |
| `collegiate_gothic` | Collegiate Gothic |  |
| `graduate_family_housing` | Graduate Family Housing |  |
| `research_laboratory` | Research Laboratory | `clay_exoskeleton_research_lab` |
| `research_laboratory_innovation_hub` | Research Laboratory Innovation Hub |  |
| `science_engineering_lab_complex` | Science Engineering Lab Complex |  |
| `student_residence_tower` | Student Residence Tower | `clay_student_residence_tower` |
| `student_union_campus_centre` | Student Union Campus Centre |  |

### Energy / Infrastructure (5)

| archetype id | title | clay candidate |
|---|---|---|
| `central_utilities_plant_energy_centre` | Central Utilities Plant Energy Centre | `clay_energy_centre` |
| `ev_charging_hub` | EV Charging Hub / Mobility Station |  |
| `ev_charging_hub_mobility_station` | Ev Charging Hub Mobility Station |  |
| `hyperscale_data_center` | Hyperscale Data Center |  |
| `solar_farm_agrivoltaics` | Solar Farm / Agrivoltaics |  |

### Entertainment / Culture (7)

| archetype id | title | clay candidate |
|---|---|---|
| `concrete_megastructure_arena` | Concrete Megastructure Arena |  |
| `convention_exhibition_center` | Convention Exhibition Center |  |
| `high_tech_arena` | High-Tech Structural Arena |  |
| `high_tech_structural_arena` | High Tech Structural Arena |  |
| `immersive_experience_venue` | Immersive Experience Venue |  |
| `monumental_antiquity_arena` | Monumental Antiquity Arena |  |
| `outdoor_sports_stadium` | Outdoor Sports Stadium | `clay_etfe_truss_stadium` |

### Healthcare (5)

| archetype id | title | clay candidate |
|---|---|---|
| `art_deco_healthcare` | Art Deco Healthcare |  |
| `biophilic_modern_healthcare` | Biophilic Modern Healthcare |  |
| `functionalist_healthcare` | Functionalist Healthcare |  |
| `regional_hospital_medical_center` | Regional Hospital / Medical Center | `clay_braced_frame_hospital` |
| `senior_living_complex` | Senior Living Complex | `clay_garden_court_senior_residence` |

### Hospitality (4)

| archetype id | title | clay candidate |
|---|---|---|
| `amsterdam_brown_cafe` | Amsterdam Brown Cafe |  |
| `corporate_tower_hotel` | Corporate Tower Hotel |  |
| `parisian_cafe_brasserie` | Parisian Cafe Brasserie |  |
| `resort_modernism_hotel` | Resort Modernism Hotel |  |

### Industrial (11)

| archetype id | title | clay candidate |
|---|---|---|
| `amsterdam_canal_warehouse` | Amsterdam Canal Warehouse |  |
| `art_deco_industrial` | Art Deco Industrial |  |
| `barcelona_modernist_workshop` | Barcelona Modernist Workshop |  |
| `brutalist_utility_heavy_industrial` | Brutalist Utility Heavy Industrial |  |
| `e_commerce_fulfillment_center` | E Commerce Fulfillment Center |  |
| `early_20c_megastructure_industrial` | Early 20th Century Megastructure | `clay_craneway_hall` |
| `early_20th_century_megastructure` | Early 20th Century Megastructure |  |
| `junction_converted_industrial_loft` | Junction Converted Industrial Loft |  |
| `mid_century_distribution_warehouse` | Mid Century Distribution Warehouse | `clay_cmu_dock_warehouse` |
| `modern_big_box_logistics` | Modern Big Box Logistics |  |
| `structural_expressionism_industrial` | Structural Expressionism Industrial |  |

### Recreation (5)

| archetype id | title | clay candidate |
|---|---|---|
| `climbing_wall_building` | Climbing Wall Building |  |
| `contemporary_sustainable_rec_centre` | Contemporary Sustainable Rec Centre |  |
| `parkitecture` | Parkitecture |  |
| `postmodern_community_rec_centre` | Postmodern Community Rec Centre |  |
| `postmodern_rec_centre` | Postmodern Community Rec Centre |  |

### Residential — Detached / Single-Family (6)

| archetype id | title | clay candidate |
|---|---|---|
| `annex_mansion` | Annex Mansion |  |
| `farnsworth_house_glass_pavilion` | Farnsworth House Glass Pavilion |  |
| `toronto_annex_mansion` | Annex Mansion |  |
| `vancouver_craftsman_bungalow` | Vancouver Craftsman Bungalow |  |
| `vancouver_laneway_house` | Vancouver Laneway House |  |
| `vancouver_special` | Vancouver Special |  |

### Residential — High-Rise / Tower (3)

| archetype id | title | clay candidate |
|---|---|---|
| `condo_podium_tower` | Condo Podium Tower | `clay_brick_podium_condo_tower` |
| `new_york_pre_war_apartment` | New York Pre-War Apartment | `clay_prewar_apartment_tower` |
| `toronto_condo_podium_tower` | Condo Podium Tower |  |

### Residential — Mid-Rise Apartment (6)

| archetype id | title | clay candidate |
|---|---|---|
| `amsterdam_cornice_house` | Amsterdam Cornice House |  |
| `amsterdam_jordaan_house` | Amsterdam Jordaan House |  |
| `amsterdam_school_housing` | Amsterdam School Housing |  |
| `modernisme_casa` | Modernisme Casa |  |
| `pre_haussmann_marais_building` | Pre-Haussmann Marais Building |  |
| `residential_superblock` | Residential Superblock | `clay_sculptural_superblock` |

### Residential — Rowhouse / Townhouse / Terrace (17)

| archetype id | title | clay candidate |
|---|---|---|
| `amsterdam_neck_gable_house` | Amsterdam Neck Gable House |  |
| `amsterdam_spout_gable_house` | Amsterdam Spout Gable House |  |
| `amsterdam_step_gable_house` | Amsterdam Step Gable House |  |
| `barcelona_townhouse` | Barcelona Townhouse |  |
| `bay_and_gable_house` | Bay and Gable House |  |
| `brick_rowhouse_terrace` | Brick Rowhouse Terrace | `clay_queen_anne_rowhouse_trio` |
| `georgian_terrace_house` | Georgian Terrace House |  |
| `hydrostone_neighbourhood_house` | Hydrostone Neighbourhood House |  |
| `london_crescent_terrace` | London Crescent Terrace |  |
| `london_mews_house` | London Mews House |  |
| `london_townhouse` | London Townhouse |  |
| `mile_end_cultural_triplex` | Mile End Cultural Triplex |  |
| `montreal_plateau_triplex` | Montreal Plateau Triplex |  |
| `regency_stucco_terrace` | Regency Stucco Terrace |  |
| `terraced_stepped_building` | Terraced / Stepped Building | `clay_terraced_stepped_tower` |
| `toronto_bay_and_gable_house` | Bay-and-Gable House |  |
| `victorian_bay_window_terrace` | Victorian Bay Window Terrace |  |

### Transportation (10)

| archetype id | title | clay candidate |
|---|---|---|
| `calgary_ctrain_station` | Calgary CTrain Station | `clay_ctrain_elevated_station` |
| `contemporary_transit_hub` | Contemporary Transit Hub |  |
| `cruise_ferry_terminal` | Cruise Ferry Terminal |  |
| `halifax_ferry_terminal` | Halifax Ferry Terminal |  |
| `skytrain_elevated_station` | SkyTrain Elevated Station |  |
| `toronto_streetcar_platform_stop` | TTC Streetcar Platform Stop |  |
| `ttc_streetcar_platform_stop` | Ttc Streetcar Platform Stop |  |
| `urban_light_rail_stop` | Urban Light Rail Stop |  |
| `vertiport_evtol` | Vertiport / eVTOL Facility |  |
| `vertiport_evtol_facility` | Vertiport Evtol Facility |  |

## Parks and plazas (79)

### park (50)

| archetype id | title | clay candidate |
|---|---|---|
| `amsterdam_hofje_garden` | Hofje Courtyard Garden |  |
| `amsterdam_vondelpark` | Vondelpark Garden |  |
| `barcelona_pati_interior` | Eixample Interior Courtyard |  |
| `calgary_princes_island` | Prince's Island Park |  |
| `canal_waterway` | Canal / Waterway |  |
| `cemetery_memorial_grounds` | Cemetery / Memorial Grounds |  |
| `constructed_wetland_eco_park` | Constructed Wetland Eco Park |  |
| `custom_parks_plazas` | Custom Parks / Plazas |  |
| `equestrian_center` | Equestrian Center |  |
| `estate_picnic_grove` | Estate Picnic Grove |  |
| `festival_event_lawn` | Festival Grounds & Event Lawn |  |
| `floating_park_pool` | Floating Park / Pool |  |
| `foothill_trail_park` | Foothill Trail Park |  |
| `golf_course_18_hole` | Golf Course 18 Hole |  |
| `golf_driving_range` | Golf Driving Range |  |
| `greenbelt_buffer_park` | Greenbelt Buffer Park |  |
| `halifax_coastal_park` | Halifax Coastal Forest Park |  |
| `halifax_public_gardens` | Halifax Public Gardens |  |
| `hilltop_topographic_park` | Hilltop Topographic Park |  |
| `kayak_launch_dock` | Kayak & Canoe Launch |  |
| `lighthouse_point_park` | Lighthouse Point / Headland Park |  |
| `london_circus` | London Circus |  |
| `london_garden_square` | London Garden Square |  |
| `marina_yacht_harbor` | Marina / Yacht Harbor |  |
| `montreal_mount_royal` | Mount Royal Park |  |
| `montreal_square` | Montreal Neighbourhood Square |  |
| `mountain_bike_park` | Mountain Bike Park |  |
| `multi_sport_complex` | Multi Sport Complex |  |
| `nature_preserve` | Nature Preserve |  |
| `newyork_community_garden` | New York Community Garden |  |
| `newyork_pocket_park` | New York Pocket Park |  |
| `outdoor_ice_rink` | Outdoor Ice Rink |  |
| `parisian_jardin` | Jardin a la Francaise |  |
| `parisian_square` | Square Parisien |  |
| `picturesque_olmsted_park` | Picturesque / Olmsted Park |  |
| `quarry_sunken_garden_park` | Quarry / Sunken Garden Park |  |
| `reclaimed_industrial_park` | Reclaimed Industrial Park |  |
| `regional_park` | Regional Park |  |
| `rewilding_ecological_restoration_zone` | Rewilding Ecological Restoration Zone |  |
| `riverfront_park_beach` | Riverfront Park / Beach |  |
| `rooftop_garden` | Rooftop Garden |  |
| `stormwater_naturalized_drainage_corridor` | Stormwater Naturalized Drainage Corridor |  |
| `stormwater_resilience_park` | Stormwater Resilience Park |  |
| `street_plaza_parklet` | Street Plaza / Parklet |  |
| `tidal_marsh_boardwalk` | Tidal Marsh Boardwalk |  |
| `toronto_ravine` | Toronto Ravine Park |  |
| `vancouver_beach_park` | Vancouver Beach Park |  |
| `vancouver_seawall` | Vancouver Seawall Promenade |  |
| `velodrome_cycling_track` | Velodrome Cycling Track |  |
| `working_pier_wharf_conversion` | Working Pier / Wharf Conversion |  |

### plaza (29)

| archetype id | title | clay candidate |
|---|---|---|
| `academic_courtyard` | Academic Courtyard |  |
| `airport_airfield` | Airport Airfield |  |
| `amphitheater_performance_space` | Outdoor Amphitheater / Performance Space |  |
| `amsterdam_plein` | Amsterdam Plein |  |
| `barcelona_placa_xamfra` | Chamfer Plaza |  |
| `barcelona_superilla` | Barcelona Superblock |  |
| `beer_garden` | Beer Garden |  |
| `calgary_prairie_plaza` | Calgary Prairie Urban Plaza |  |
| `campus_central_quad` | Campus Central Quad |  |
| `cathedral_religious_forecourt` | Cathedral / Religious Forecourt |  |
| `city_hall_government_plaza` | City Hall / Government Plaza |  |
| `courtyard_plaza` | Courtyard |  |
| `cultural_institution_forecourt` | Cultural Institution Forecourt |  |
| `food_truck_plaza` | Food-Truck Plaza |  |
| `green_parking_lot` | Green Parking (Permeable) |  |
| `lake_edge_plaza` | Lake Edge Plaza |  |
| `market_square` | Market Square |  |
| `night_market` | Night Market |  |
| `parade_ground` | Parade / Procession Ground |  |
| `parisian_place` | Place Royale |  |
| `promenade_boardwalk` | Promenade / Boardwalk |  |
| `stepped_terraced_plaza` | Stepped / Terraced Plaza |  |
| `structured_parking_garage` | Structured Parking Garage |  |
| `suburban_retail_parking_lot` | Suburban Retail Parking Lot |  |
| `surface_parking_lot` | Surface Parking Lot |  |
| `swimming_pool_complex` | Swimming Pool Complex |  |
| `toronto_urban_square` | Toronto Urban Square |  |
| `transit_plaza` | Transit Plaza |  |
| `underground_parking_entry` | Underground Parking (Entry Only) |  |

## Streets and paths (85)

### alberta_bike_design_guide (6)

| archetype id | title | clay candidate |
|---|---|---|
| `advisory_bike_lane_street` | Advisory Bike Lane Street |  |
| `bicycle_accessible_shoulder` | Bicycle Accessible Shoulder |  |
| `bicycle_lane_painted` | Bicycle Lane (Painted) |  |
| `bicycle_pathway` | Bicycle Pathway |  |
| `bicycle_shared_space` | Bicycle Shared Space |  |
| `separated_bike_lane` | Separated Bike Lane |  |

### auto_oriented (23)

| archetype id | title | clay candidate |
|---|---|---|
| `amsterdam_straat` | Amsterdam Straat (Main Street) |  |
| `arterial_boulevard` | Arterial Boulevard |  |
| `back_alley_service_lane` | Back Alley / Service Lane |  |
| `barcelona_eixample_carrer` | Barcelona Eixample Carrer |  |
| `collector_road` | Collector Road |  |
| `cul_de_sac` | Cul-de-Sac |  |
| `custom_streets_pathways` | Custom Streets / Pathways |  |
| `downtown_thoroughfare` | Downtown Thoroughfare |  |
| `halifax_steep_residential_street` | Halifax Steep Residential Street |  |
| `highway_freeway` | Highway / Freeway |  |
| `inglewood_main_street` | Inglewood Main Street |  |
| `london_crescent_road` | London Crescent Road |  |
| `london_terrace_street` | London Terrace Street |  |
| `montreal_commercial_boulevard` | Montreal Commercial Boulevard |  |
| `montreal_plateau_residential_rue` | Montreal Plateau Residential Rue |  |
| `new_york_brownstone_side_street` | New York Brownstone Side Street |  |
| `parisian_rue` | Parisian Rue (Typical Street) |  |
| `scenic_parkway` | Scenic Parkway |  |
| `soho_cobblestone_street` | SoHo Cobblestone Street |  |
| `suburban_residential_street` | Suburban Residential Street |  |
| `toronto_victorian_residential_street` | Toronto Victorian Residential Street |  |
| `urban_vehicular_bridge` | Urban Vehicular Bridge |  |
| `vancouver_back_lane` | Vancouver Back Lane |  |

### calgary_street_manual (12)

| archetype id | title | clay candidate |
|---|---|---|
| `calgary_alley` | Calgary Alley |  |
| `calgary_arterial_4lane_50` | Calgary Arterial – 4 Lanes Divided (50) |  |
| `calgary_arterial_4lane_70` | Calgary Arterial – 4 Lanes Divided (70) |  |
| `calgary_arterial_6lane` | Calgary Arterial – 6 Lanes |  |
| `calgary_arterial_high_activity` | Calgary Arterial – High Activity |  |
| `calgary_collector` | Calgary Collector |  |
| `calgary_collector_high_activity` | Calgary Collector – High Activity |  |
| `calgary_collector_industrial` | Calgary Collector – Industrial |  |
| `calgary_local_high_activity` | Calgary Local – High Activity |  |
| `calgary_local_industrial` | Calgary Local – Industrial |  |
| `calgary_local_rural` | Calgary Local – Rural |  |
| `calgary_skeletal` | Calgary Skeletal |  |

### cycling_oriented (3)

| archetype id | title | clay candidate |
|---|---|---|
| `bow_river_pathway` | Bow River Pathway |  |
| `dedicated_cycle_bridge` | Dedicated Cycle Bridge |  |
| `shared_cycle_pedestrian_bridge` | Shared Cycle-Pedestrian Bridge |  |

### intersections (11)

| archetype id | title | clay candidate |
|---|---|---|
| `compact_safety_roundabout` | Compact Safety Roundabout |  |
| `compact_safety_roundabout_diagram` | Compact Safety Roundabout (Diagram) |  |
| `daylighted_intersection` | Daylighted Intersection |  |
| `high_entry_angle_right_turn` | High-Entry-Angle Right Turn |  |
| `left_turn_calming_intersection` | Left Turn Calming Intersection |  |
| `mini_roundabout_diagram` | Mini-Roundabout (Diagram) |  |
| `neighborhood_traffic_circle` | Neighborhood Traffic Circle |  |
| `pedestrian_scramble_intersection` | Pedestrian Scramble Intersection |  |
| `protected_intersection_diagram` | Protected Intersection (Diagram) |  |
| `raised_intersection` | Raised Intersection |  |
| `raised_intersection_diagram` | Raised Intersection (Diagram) |  |

### pedestrian_oriented (8)

| archetype id | title | clay candidate |
|---|---|---|
| `amsterdam_steeg` | Amsterdam Steeg (Narrow Alley) |  |
| `barcelona_passatge` | Barcelona Passatge (Covered Passage) |  |
| `commercial_alley_laneway` | Commercial Alley / Laneway |  |
| `landscape_park_pedestrian_bridge` | Landscape Park Pedestrian Bridge |  |
| `parisian_passage` | Parisian Passage Couvert |  |
| `pedestrian_promenade` | Pedestrian Promenade |  |
| `stephen_avenue_pedestrian_mall` | Stephen Avenue Pedestrian Mall |  |
| `urban_pedestrian_footbridge` | Urban Pedestrian Footbridge |  |

### traffic_safety_vision_zero (19)

| archetype id | title | clay candidate |
|---|---|---|
| `chicane_diagram` | Chicane (Diagram) |  |
| `continuous_sidewalk_street` | Continuous Crossing (Continuous Sidewalk) |  |
| `curb_extension_crossing_diagram` | Curb Extension Crossing (Diagram) |  |
| `curb_extension_crossing_street` | Curb Extension Crossing Street |  |
| `directional_full_closure` | Directional / Full Closure |  |
| `modal_filter_diverter` | Diverter (Modal Filter) |  |
| `neighborhood_gateway` | Neighborhood Gateway |  |
| `raised_crossing_collector` | Raised Crossing |  |
| `raised_crossing_diagram` | Raised Crossing (Diagram) |  |
| `refuge_island_arterial` | Two-Stage Crossing Median (Pedestrian Refuge) |  |
| `right_in_right_out_median` | Right-In Right-Out Median |  |
| `road_diet_complete_street` | Road Diet Complete Street |  |
| `speed_cushion_diagram` | Speed Cushion (Diagram) |  |
| `speed_cushion_street` | Speed Cushion Street |  |
| `speed_hump_diagram` | Speed Hump (Diagram) |  |
| `speed_hump_local_street` | Speed Hump (Local Street) |  |
| `speed_table_diagram` | Speed Table (Diagram) |  |
| `traffic_calmed_local_street` | Traffic Calmed Local Street |  |
| `two_stage_crossing_median_diagram` | Two-Stage Crossing Median (Diagram) |  |

### transit_oriented (3)

| archetype id | title | clay candidate |
|---|---|---|
| `rail_transit_viaduct` | Rail Transit Viaduct |  |
| `toronto_streetcar_street` | Toronto Streetcar Street |  |
| `transit_priority_bridge` | Transit-Priority Bridge |  |

## Notes

- **Diagram-type streets.** Several street entries are traffic-calming or intersection diagrams. These have ids ending `_diagram`, or are intersection treatments such as raised crossings and modal filters. They have reference images but are better served by the parametric street-section system than by a standalone model.
- **Custom cards.** Custom or prompt-ready cards are listed because they have references, but they are not real building types. These are `custom_prompt_ready_archetype`, `custom_contextual_experiment`, `custom_parks_plazas` and `custom_streets_pathways`.
- **Duplicates.** Some building ids are near-duplicates of each other in the catalogue. Examples:
  - `annex_mansion` and `toronto_annex_mansion`;
  - `boutique_hotel` and `boutique_hotel_tower`;
  - `modern_big_box_logistics` and `modern_bigbox_warehouse`.

  One model can serve both ids in each pair.
