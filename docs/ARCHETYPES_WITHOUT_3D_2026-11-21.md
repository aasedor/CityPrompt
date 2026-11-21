# Catalogue archetypes without 3D, 2026-11-21

Nearly every archetype in the three catalogues has AI reference images: a street
view, and for most an oblique and a plan view, per variant. This inventory shows which ones
were never turned into a 3D model.

**Method.** "In the app" means the archetype has at least one card in today's
classroom picker (`CANONICAL_CHOICES`), which lists only cards backed by a real 3D
model, never a generic massing fallback. The registry was bundled and run from
commit `e4708133d` with production settings. "3D elsewhere" means a model for the
archetype exists in the repository or its ignored `artifacts/` folder (a LEGO family,
a park kit, a clay candidate) but has no picker card. "Never modelled" is the rest.

| Catalogue | Archetypes | In the app | 3D elsewhere, no card | Never modelled | Their image variants |
|---|---:|---:|---:|---:|---:|
| Buildings | 252 | 98 | 33 | 121 | 484 |
| Parks and open spaces | 130 | 23 | 11 | 96 | 384 |
| Streets and paths | 116 | 46 | 1 | 69 | 211 |
| **Total** | **498** | **167** | **45** | **286** | **1079** |

Notes:

- Counting is by archetype. An archetype in the app may still have variants that were
  never modelled; most cards are one student variant built from the catalogue images.
- Some picker cards have their own parent ids that are not catalogue archetypes,
  for example a pump-track park and an inclusive playground. Those concepts exist in
  3D as their own cards, separately from the catalogue archetypes of the same subject.
- Streets without a card cannot be drawn in 3D from the picker.
- High-Speed Rail Corridor is counted under streets in the app.
- 23 building archetypes have some or all reference images missing, and a few are
  duplicates of another archetype with the same title. Both are marked in the lists.
  Eleven never-modelled entries duplicate an archetype that does have 3D under its
  other id, so about 275 distinct subjects remain unmodelled.

## 3D elsewhere, no picker card (45)

| Archetype | Kind | Model and status |
|---|---|---|
| Airport Terminal Building (`airport_terminal_building`) | Buildings | LEGO modular family in the model library; no picker card |
| Autonomous Tech Campus (`autonomous_tech_campus`) | Buildings | LEGO modular family in the model library; no picker card |
| Biophilic Modern Healthcare (`biophilic_healthcare`) | Buildings | LEGO modular family in the model library; no picker card |
| Brownstone Rowhouse Frontage (`brownstone_rowhouse_frontage`) | Buildings | LEGO modular family in the model library; no picker card |
| Civic Monumental Institution (`civic_monumental_institution`) | Buildings | LEGO modular family in the model library; no picker card |
| Coastal / Resort Terrace Block (`coastal_resort_terrace_block`) | Buildings | LEGO modular family in the model library; no picker card |
| Collegiate Gothic (`collegiate_gothic_education`) | Buildings | LEGO modular family in the model library; no picker card |
| Concert Hall (Modern) (`concert_hall_modern`) | Buildings | LEGO modular family in the model library (Wave 2, approved); no picker card |
| Contemporary Mid-Rise Residential (`contemporary_midrise_residential`) | Buildings | LEGO modular family in the model library; no picker card |
| Eco-Urban Bioclimatic Block (`eco_urban_bioclimatic_block`) | Buildings | LEGO modular family in the model library; no picker card |
| Highway Motor Hotel (`highway_motor_hotel`) | Buildings | LEGO modular family in the model library; no picker card |
| Hotel Particulier (`hotel_particulier`) | Buildings | LEGO modular family in the model library; no picker card |
| Intermodal Transit Hub (`intermodal_transit_hub`) | Buildings | LEGO modular family in the model library (Wave 2, approved); no picker card |
| Japanese Contemporary Lanehouse (`japanese_contemporary_lanehouse`) | Buildings | LEGO modular family in the model library; no picker card |
| Large Art Museum Gallery (`large_art_museum_gallery`) | Buildings | LEGO modular family in the model library (Wave 2, approved); no picker card |
| Machine Aesthetic Heavy Industrial (`machine_aesthetic_heavy_industrial`) | Buildings | LEGO modular family in the model library (Wave 2, approved); no picker card |
| Mid-Century Modern Pavilion Block (`mid_century_modern_pavilion_block`) | Buildings | LEGO modular family in the model library; no picker card |
| Minimalist Courtyard Block (`minimalist_courtyard_block`) | Buildings | LEGO modular family in the model library; no picker card |
| Modern Glass Office / Institutional (`modern_glass_office_institutional`) | Buildings | LEGO modular family in the model library; no picker card |
| Modern Sports Arena (`modern_sports_arena`) | Buildings | LEGO modular family in the model library; no picker card |
| Modernist Civic Block (`modernist_civic_block`) | Buildings | LEGO modular family in the model library; no picker card |
| Mountain / Alpine Chalet (`mountain_alpine_chalet`) | Buildings | LEGO modular family in the model library; no picker card |
| Parametric Future Hub (`parametric_future_hub`) | Buildings | LEGO modular family in the model library; no picker card |
| Rural Gas Station (`rural_gas_station`) | Buildings | LEGO modular family in the model library; no picker card |
| Scandinavian Urban Residential (`scandinavian_urban_residential`) | Buildings | LEGO modular family in the model library; no picker card |
| Second Empire Civic Building (`second_empire_civic_building`) | Buildings | LEGO modular family in the model library (Wave 2, approved); no picker card |
| Skyline Glass Office Cluster (`skyline_glass_office_cluster`) | Buildings | LEGO modular family in the model library; no picker card |
| Traditional Vernacular Market Street (`traditional_vernacular_market_street`) | Buildings | LEGO modular family in the model library; no picker card |
| Transit-Oriented Station Block (`transit_oriented_station_block`) | Buildings | LEGO modular family in the model library; no picker card |
| Vancouver Laneway House (`vancouver_laneway_house`) | Buildings | Clay model (Garage Suite) passed independent review; awaiting your approval |
| Vertical Farm / Indoor Agriculture (`vertical_farm`) | Buildings | LEGO modular family in the model library (Wave 2, approved); no picker card |
| Vertical Forest Residential (`vertical_forest_residential`) | Buildings | LEGO modular family in the model library; no picker card |
| Waste-to-Energy Plant (`waste_to_energy_plant`) | Buildings | LEGO modular family in the model library (Wave 2, approved); no picker card |
| Baseball / Softball Diamond (`baseball_softball_diamond`) | Parks | Archetype-owned park kit in code; no picker card |
| Community Garden / Allotments (`community_garden`) | Parks | Archetype-owned park kit in code; no picker card |
| Cricket Ground (`cricket_pitch_oval`) | Parks | Archetype-owned park kit in code; no picker card |
| Inclusive Accessible Playground (`inclusive_playground`) | Parks | Archetype-owned park kit in code; no picker card |
| Memorial Garden (`memorial_garden`) | Parks | Archetype-owned park kit in code; no picker card |
| Neighborhood Park (`neighborhood_park`) | Parks | Landscape pilot (rustic neighbourhood park) in code; no picker card |
| Outdoor Fitness Circuit (`outdoor_fitness_circuit`) | Parks | Archetype-owned park kit in code; no picker card |
| Pump Track (`pump_track`) | Parks | Archetype-owned park kit in code; no picker card |
| Running Track & Athletic Oval (`running_track_oval`) | Parks | Archetype-owned park kit in code; no picker card |
| Skate Park (`skate_park`) | Parks | Archetype-owned park kit in code; no picker card |
| Sports Field Complex (`sports_field_complex`) | Parks | Archetype-owned park kit in code; no picker card |
| Barcelona Passatge (Covered Passage) (`barcelona_passatge`) | Streets | Clay model passed independent review at v006; awaiting your decision |

## Buildings: 121 never modelled

### Detached homes (13)

- Amsterdam Bell Gable House (`amsterdam_bell_gable_house`), 4 variants
- Amsterdam Jordaan House (`amsterdam_jordaan_house`), 4 variants
- Amsterdam Neck Gable House (`amsterdam_neck_gable_house`), 4 variants
- Amsterdam Spout Gable House (`amsterdam_spout_gable_house`), 4 variants
- Amsterdam Step Gable House (`amsterdam_step_gable_house`), 4 variants
- Annex Mansion (`toronto_annex_mansion`), 4 variants (duplicate of `annex_mansion`)
- Annex Mansion (`annex_mansion`), 4 variants (duplicate of `toronto_annex_mansion`)
- Edwardian Foursquare (`edwardian_foursquare`), 4 variants (duplicate of `toronto_edwardian_foursquare`, which is in the app)
- Farnsworth House Glass Pavilion (`farnsworth_house_glass_pavilion`), 4 variants
- Georgian Terrace House (`georgian_terrace_house`), 4 variants
- Hydrostone Neighbourhood House (`hydrostone_neighbourhood_house`), 4 variants
- Vancouver Craftsman Bungalow (`vancouver_craftsman_bungalow`), 4 variants
- Vancouver Special (`vancouver_special`), 4 variants

### Duplexes & semi-detached homes (1)

- Bay and Gable House (`bay_and_gable_house`), 4 variants (duplicate of `toronto_bay_and_gable_house`, which is in the app)

### Rowhouses & townhomes (8)

- Brick Rowhouse Terrace (`toronto_brick_rowhouse`), 4 variants (duplicate of `brick_rowhouse_terrace`)
- Brick Rowhouse Terrace (`brick_rowhouse_terrace`), 4 variants (duplicate of `toronto_brick_rowhouse`)
- Classic Brownstone Streetwall (`classic_brownstone_streetwall`), 4 variants (some reference images missing)
- London Townhouse (`london_townhouse`), 4 variants
- Regency Stucco Terrace (`regency_stucco_terrace`), 4 variants
- Vernacular Courtyard Housing (`vernacular_courtyard_housing`), 4 variants (some reference images missing)
- Victorian Bay Window Terrace (`victorian_bay_window_terrace`), 4 variants
- Victorian Heritage Avenue (`victorian_heritage_avenue`), 4 variants (some reference images missing)

### Apartments (15)

- Adaptive Reuse Warehouse Lofts (`adaptive_reuse_warehouse_lofts`), 4 variants (some reference images missing)
- Amsterdam Cornice House (`amsterdam_cornice_house`), 4 variants
- Amsterdam Hofje (`amsterdam_hofje`), 4 variants
- Amsterdam School Housing (`amsterdam_school_housing`), 4 variants
- Barcelona Townhouse (`barcelona_townhouse`), 4 variants
- Contemporary Midrise (`contemporary_midrise`), 4 variants (some reference images missing)
- Eixample Apartment Block (`eixample_apartment_block`), 4 variants
- Modernisme Casa (`modernisme_casa`), 4 variants
- Montreal Plateau Triplex (`montreal_plateau_triplex`), 4 variants
- New York Pre-War Apartment (`new_york_pre_war_apartment`), 4 variants
- New York Walk-Up Tenement (`new_york_walk_up_tenement`), 4 variants
- Old Montreal Warehouse Loft (`old_montreal_warehouse_loft`), 4 variants
- Pre-Haussmann Marais Building (`pre_haussmann_marais_building`), 4 variants
- Residential Superblock (`residential_superblock`), 4 variants
- Terraced / Stepped Building (`terraced_stepped_building`), 4 variants

### Residential towers (1)

- Condo Podium Tower (`toronto_condo_podium_tower`), 4 variants (duplicate of `condo_podium_tower`, which is in the app)

### Homes over shops & mixed use (10)

- Alpine Mixed-Use Lodge (`alpine_mixed_use_lodge`), 4 variants (some reference images missing)
- Barcelona Corner Chamfer (`barcelona_corner_chamfer`), 4 variants
- Junction Converted Industrial Loft (`toronto_junction_converted_industrial`), 4 variants (duplicate of `junction_converted_industrial_loft`)
- Junction Converted Industrial Loft (`junction_converted_industrial_loft`), 4 variants (duplicate of `toronto_junction_converted_industrial`)
- London Heritage Mansion Block (`london_heritage_mansion_block`), 4 variants (no reference images)
- Mall Redevelopment (`mall_redevelopment`), 4 variants
- Mile End Cultural Triplex (`mile_end_cultural_triplex`), 4 variants
- Parisian Mid Rise (`parisian_mid_rise`), 4 variants (duplicate of `parisian_midrise_block`)
- Parisian Mid-Rise (`parisian_midrise_block`), 4 variants (duplicate of `parisian_mid_rise`)
- Transit Podium Residential (`transit_podium_residential`), 4 variants (some reference images missing)

### Shops & services (11)

- Amsterdam Brown Cafe (`amsterdam_brown_cafe`), 4 variants
- Coastal Breezeway Mixed Use (`coastal_breezeway_mixed_use`), 4 variants (some reference images missing)
- Corner Dépanneur (`corner_dépanneur`), 4 variants (duplicate of `montreal_depanneur`, which is in the app)
- Halifax Maritime Commercial (`halifax_maritime_commercial`), 4 variants
- Historical Brick Main Street (`historical_brick_main_street`), 4 variants
- Marche Couvert (`marche_couvert`), 4 variants
- Mediterranean Arcade Mixed Use (`mediterranean_arcade_mixed_use`), 4 variants (some reference images missing)
- New York Corner Bodega (`new_york_corner_bodega`), 4 variants
- Parisian Cafe Brasserie (`parisian_cafe_brasserie`), 4 variants
- Passage Couvert (`passage_couvert`), 4 variants
- Shophouse (Southeast Asian) (`shophouse_southeast_asian`), 4 variants

### Hotels & visitor accommodation (4)

- Boutique Hotel (`boutique_hotel_tower`), 4 variants (some reference images missing; duplicate of `boutique_hotel`, which is in the app)
- Chateauesque / Grand Railway Hotel (`chateauesque_hotel`), 4 variants (duplicate of `chateauesque_grand_railway_hotel`, which is in the app)
- Corporate Tower Hotel (`corporate_tower_hotel`), 4 variants
- Resort Modernism Hotel (`resort_modernism_hotel`), 4 variants

### Offices (2)

- Glass Tower Modern (`glass_tower_modern`), 4 variants (duplicate of `glass_tower_podium_modern`, which is in the app)
- New York Art Deco Tower (`new_york_art_deco_tower`), 4 variants

### Schools, civic & recreation (30)

- Art Deco Healthcare (`art_deco_healthcare`), 4 variants
- Biophilic Modern Healthcare (`biophilic_modern_healthcare`), 4 variants (duplicate of `biophilic_healthcare`, which is 3D elsewhere)
- Brutalist Institutional (`brutalist_institutional`), 4 variants
- Calgary New Central Library (`calgary_new_central_library`), 4 variants
- Campus Dining Hall Food Court (`campus_dining_hall_food_court`), 4 variants
- Campus Lecture Hall Complex (`campus_lecture_hall_complex`), 4 variants
- Campus Parking Structure (`campus_parking_structure`), 4 variants
- Campus Recreation Athletics Centre (`campus_recreation_athletics_centre`), 4 variants
- Civic Classical Building (`civic_classical_building`), 4 variants (some reference images missing)
- Collegiate Gothic (`collegiate_gothic`), 4 variants (duplicate of `collegiate_gothic_education`, which is 3D elsewhere)
- Concrete Megastructure Arena (`concrete_megastructure_arena`), 4 variants
- Contemporary Civic (`contemporary_civic`), 4 variants
- Contemporary Sustainable Rec Centre (`contemporary_sustainable_rec_centre`), 4 variants
- Convention Exhibition Center (`convention_exhibition_center`), 4 variants
- Functionalist Healthcare (`functionalist_healthcare`), 4 variants
- Graduate Family Housing (`graduate_family_housing`), 4 variants
- High Tech Structural Arena (`high_tech_structural_arena`), 4 variants (duplicate of `high_tech_arena`)
- High-Tech Structural Arena (`high_tech_arena`), 4 variants (duplicate of `high_tech_structural_arena`)
- Immersive Experience Venue (`immersive_experience_venue`), 4 variants
- Monumental Antiquity Arena (`monumental_antiquity_arena`), 4 variants
- Monumental Courthouse Axis (`monumental_courthouse_axis`), 4 variants (some reference images missing)
- Neoclassical Institutional (`neoclassical_institutional`), 4 variants
- Outdoor Sports Stadium (`outdoor_sports_stadium`), 4 variants
- Parkitecture (`parkitecture`), 4 variants (duplicate of `parkitecture_recreational`, which is in the app)
- Postmodern Community Rec Centre (`postmodern_rec_centre`), 4 variants (duplicate of `postmodern_community_rec_centre`)
- Postmodern Community Rec Centre (`postmodern_community_rec_centre`), 4 variants (duplicate of `postmodern_rec_centre`)
- Research Laboratory (`research_laboratory`), 4 variants
- Research Laboratory Innovation Hub (`research_laboratory_innovation_hub`), 4 variants
- Science Engineering Lab Complex (`science_engineering_lab_complex`), 4 variants
- Student Union Campus Centre (`student_union_campus_centre`), 4 variants

### Industry & warehouses (11)

- Amsterdam Canal Warehouse (`amsterdam_canal_warehouse`), 4 variants
- Art Deco Industrial (`art_deco_industrial`), 4 variants
- Barcelona Modernist Workshop (`barcelona_modernist_workshop`), 4 variants
- Brutalist Utility Heavy Industrial (`brutalist_utility_heavy_industrial`), 4 variants
- E Commerce Fulfillment Center (`e_commerce_fulfillment_center`), 4 variants
- Early 20th Century Megastructure (`early_20c_megastructure_industrial`), 4 variants (duplicate of `early_20th_century_megastructure`)
- Early 20th Century Megastructure (`early_20th_century_megastructure`), 4 variants (duplicate of `early_20c_megastructure_industrial`)
- Functionalist Brick Industrial (`functionalist_brick_industrial`), 4 variants
- Modern Big Box Logistics (`modern_big_box_logistics`), 4 variants (duplicate of `modern_bigbox_warehouse`, which is in the app)
- Romanesque Revival Warehouse (`romanesque_revival_warehouse`), 4 variants
- Structural Expressionism Industrial (`structural_expressionism_industrial`), 4 variants

### Transit & utilities (13)

- Contemporary Transit Hub (`contemporary_transit_hub`), 4 variants
- Cruise Ferry Terminal (`cruise_ferry_terminal`), 4 variants
- EV Charging Hub / Mobility Station (`ev_charging_hub`), 4 variants (duplicate of `ev_charging_hub_mobility_station`)
- Ev Charging Hub Mobility Station (`ev_charging_hub_mobility_station`), 4 variants (duplicate of `ev_charging_hub`)
- Halifax Ferry Terminal (`halifax_ferry_terminal`), 4 variants
- Hyperscale Data Center (`hyperscale_data_center`), 4 variants
- SkyTrain Elevated Station (`skytrain_elevated_station`), 4 variants
- Solar Farm / Agrivoltaics (`solar_farm_agrivoltaics`), 4 variants
- TTC Streetcar Platform Stop (`toronto_streetcar_platform_stop`), 4 variants (duplicate of `ttc_streetcar_platform_stop`)
- Ttc Streetcar Platform Stop (`ttc_streetcar_platform_stop`), 4 variants (duplicate of `toronto_streetcar_platform_stop`)
- Urban Light Rail Stop (`urban_light_rail_stop`), 4 variants
- Vertiport / eVTOL Facility (`vertiport_evtol`), 4 variants (duplicate of `vertiport_evtol_facility`)
- Vertiport Evtol Facility (`vertiport_evtol_facility`), 4 variants (duplicate of `vertiport_evtol`)

### Other building ideas (2)

- Custom Contextual Experiment (`custom_contextual_experiment`), 4 variants (some reference images missing)
- Custom Prompt-Ready Archetype (`custom_prompt_ready_archetype`), 4 variants (some reference images missing)

## Parks and open spaces: 96 never modelled

### Pocket & sub-neighbourhood parks (1)

- New York Pocket Park (`newyork_pocket_park`), 4 variants

### Neighbourhood & community parks (1)

- Community Park (`community_park`), 4 variants

### Regional & destination parks (9)

- Estate Picnic Grove (`estate_picnic_grove`), 4 variants
- Foothill Trail Park (`foothill_trail_park`), 4 variants
- Greenbelt Buffer Park (`greenbelt_buffer_park`), 4 variants
- Hilltop Topographic Park (`hilltop_topographic_park`), 4 variants
- Picturesque / Olmsted Park (`picturesque_olmsted_park`), 4 variants
- Quarry / Sunken Garden Park (`quarry_sunken_garden_park`), 4 variants
- Reclaimed Industrial Park (`reclaimed_industrial_park`), 4 variants
- Regional Park (`regional_park`), 4 variants
- Reservoir / Watershed Park (`reservoir_watershed_park`), 4 variants

### Natural areas & restoration (6)

- Constructed Wetland Eco Park (`constructed_wetland_eco_park`), 4 variants
- Nature Preserve (`nature_preserve`), 4 variants
- Pollinator Meadow & Wildflower Garden (`pollinator_meadow`), 4 variants
- Rewilding Ecological Restoration Zone (`rewilding_ecological_restoration_zone`), 4 variants
- Riparian Buffer / Creek Corridor (`riparian_buffer`), 4 variants
- Urban Forest (`urban_forest`), 4 variants

### Plazas & gathering places (26)

- Academic Courtyard (`academic_courtyard`), 4 variants
- Amsterdam Plein (`amsterdam_plein`), 4 variants
- Barcelona Superblock (`barcelona_superilla`), 4 variants
- Beer Garden (`beer_garden`), 4 variants
- Calgary Prairie Urban Plaza (`calgary_prairie_plaza`), 4 variants
- Campus Central Quad (`campus_central_quad`), 4 variants
- Campus Pedestrian Spine (`campus_pedestrian_spine`), 4 variants
- Cathedral / Religious Forecourt (`cathedral_religious_forecourt`), 4 variants
- Chamfer Plaza (`barcelona_placa_xamfra`), 4 variants
- City Hall / Government Plaza (`city_hall_government_plaza`), 4 variants
- Concert Pavilion Lawn (`concert_pavilion_lawn`), 4 variants
- Courtyard (`courtyard_plaza`), 4 variants
- Cultural Institution Forecourt (`cultural_institution_forecourt`), 4 variants
- Festival Grounds & Event Lawn (`festival_event_lawn`), 4 variants
- Food-Truck Plaza (`food_truck_plaza`), 4 variants
- Formal Civic Plaza (`formal_civic_plaza`), 4 variants
- Market Square (`market_square`), 4 variants
- Night Market (`night_market`), 4 variants
- Outdoor Amphitheater / Performance Space (`amphitheater_performance_space`), 4 variants
- Outdoor Cinema Lawn (`outdoor_cinema_lawn`), 4 variants
- Parade / Procession Ground (`parade_ground`), 4 variants
- Place Royale (`parisian_place`), 4 variants
- Stepped / Terraced Plaza (`stepped_terraced_plaza`), 4 variants
- Street Plaza / Parklet (`street_plaza_parklet`), 4 variants
- Toronto Urban Square (`toronto_urban_square`), 4 variants
- Transit Plaza (`transit_plaza`), 4 variants

### Play & sport amenities (15)

- Athletics Precinct Sports Fields (`athletics_precinct_sports_fields`), 4 variants
- Beach Volleyball Courts (`beach_volleyball_courts`), 4 variants
- Bocce / Pétanque Court (`bocce_petanque_court`), 4 variants
- Caged Soccer Pitch (`soccer_pitch_caged`), 4 variants
- Disc Golf Course (`disc_golf_course`), 4 variants
- Equestrian Center (`equestrian_center`), 4 variants
- Golf Course 18 Hole (`golf_course_18_hole`), 4 variants
- Golf Driving Range (`golf_driving_range`), 4 variants
- Mini Golf / Putting Course (`mini_golf_course`), 4 variants
- Mountain Bike Park (`mountain_bike_park`), 4 variants
- Multi Sport Complex (`multi_sport_complex`), 4 variants
- Outdoor Climbing & Bouldering Wall (`climbing_bouldering_wall`), 4 variants
- Playground / Adventure Play (`playground_adventure`), 4 variants
- Swimming Pool Complex (`swimming_pool_complex`), 4 variants
- Velodrome Cycling Track (`velodrome_cycling_track`), 4 variants

### Gardens & quiet spaces (17)

- Cemetery / Memorial Grounds (`cemetery_memorial_grounds`), 4 variants
- Eixample Interior Courtyard (`barcelona_pati_interior`), 4 variants
- Halifax Coastal Forest Park (`halifax_coastal_park`), 4 variants
- Hofje Courtyard Garden (`amsterdam_hofje_garden`), 4 variants
- Jardin a la Francaise (`parisian_jardin`), 4 variants
- London Circus (`london_circus`), 4 variants
- London Garden Square (`london_garden_square`), 4 variants
- Montreal Neighbourhood Square (`montreal_square`), 4 variants
- Mount Royal Park (`montreal_mount_royal`), 4 variants
- New York Community Garden (`newyork_community_garden`), 4 variants
- Rooftop Garden (`rooftop_garden`), 4 variants
- Square Parisien (`parisian_square`), 4 variants
- Toronto Ravine Park (`toronto_ravine`), 4 variants
- Urban Orchard & Food Forest (`urban_orchard_food_forest`), 4 variants
- Vancouver Beach Park (`vancouver_beach_park`), 4 variants
- Vancouver Seawall Promenade (`vancouver_seawall`), 4 variants
- Vondelpark Garden (`amsterdam_vondelpark`), 4 variants

### Waterfront & stormwater spaces (14)

- Bioswale & Rain Garden Corridor (`bioswale_rain_garden`), 4 variants
- Canal / Waterway (`canal_waterway`), 4 variants
- Floating Park / Pool (`floating_park_pool`), 4 variants
- Kayak & Canoe Launch (`kayak_launch_dock`), 4 variants
- Lake Edge Plaza (`lake_edge_plaza`), 4 variants
- Lighthouse Point / Headland Park (`lighthouse_point_park`), 4 variants
- Marina / Yacht Harbor (`marina_yacht_harbor`), 4 variants
- Pond / Lake (`pond_lake`), 4 variants
- Promenade / Boardwalk (`promenade_boardwalk`), 4 variants
- Riverfront Park / Beach (`riverfront_park_beach`), 4 variants
- Stormwater Naturalized Drainage Corridor (`stormwater_naturalized_drainage_corridor`), 4 variants
- Stormwater Resilience Park (`stormwater_resilience_park`), 4 variants
- Tidal Marsh Boardwalk (`tidal_marsh_boardwalk`), 4 variants
- Working Pier / Wharf Conversion (`working_pier_wharf_conversion`), 4 variants

### Parking, special sites & custom spaces (7)

- Airport Airfield (`airport_airfield`), 4 variants
- Custom Parks / Plazas (`custom_parks_plazas`), 4 variants
- Green Parking (Permeable) (`green_parking_lot`), 4 variants
- Structured Parking Garage (`structured_parking_garage`), 4 variants
- Suburban Retail Parking Lot (`suburban_retail_parking_lot`), 4 variants
- Surface Parking Lot (`surface_parking_lot`), 4 variants
- Underground Parking (Entry Only) (`underground_parking_entry`), 4 variants

## Streets and paths: 69 never modelled

### Local & residential streets (4)

- Calgary Local – Rural (`calgary_local_rural`), 1 variant
- Cul-de-Sac (`cul_de_sac`), 4 variants
- Suburban Residential Street (`suburban_residential_street`), 4 variants
- Yield Street (`yield_street`), 4 variants

### Collector streets (1)

- Collector Road (`collector_road`), 4 variants

### Arterial & major streets (3)

- Arterial Boulevard (`arterial_boulevard`), 4 variants
- Downtown Thoroughfare (`downtown_thoroughfare`), 4 variants
- Highway / Freeway (`highway_freeway`), 4 variants

### Alleys & service lanes (3)

- Back Alley / Service Lane (`back_alley_service_lane`), 4 variants
- Commercial Alley / Laneway (`commercial_alley_laneway`), 4 variants
- Green Alley (`green_alley`), 4 variants

### Walking, wheeling & shared streets (11)

- Advisory Bike Lane Street (`advisory_bike_lane_street`), 3 variants
- Amsterdam Steeg (Narrow Alley) (`amsterdam_steeg`), 4 variants
- Bicycle Accessible Shoulder (`bicycle_accessible_shoulder`), 1 variant
- Bicycle Lane (Painted) (`bicycle_lane_painted`), 2 variants
- Bicycle Pathway (`bicycle_pathway`), 1 variant
- Bicycle Shared Space (`bicycle_shared_space`), 1 variant
- Parisian Passage Couvert (`parisian_passage`), 4 variants
- Pedestrian Promenade (`pedestrian_promenade`), 4 variants
- Separated Bike Lane (`separated_bike_lane`), 4 variants
- Toronto Laneway (`toronto_laneway`), 4 variants
- Woonerf / Shared Street (`woonerf_shared_street`), 4 variants

### Transit corridors (2)

- Toronto Streetcar Street (`toronto_streetcar_street`), 4 variants
- Transit-Priority Bridge (`transit_priority_bridge`), 4 variants

### Intersections & crossings (13)

- Compact Safety Roundabout (`compact_safety_roundabout`), 4 variants
- Compact Safety Roundabout (Diagram) (`compact_safety_roundabout_diagram`), 1 variant
- Daylighted Intersection (`daylighted_intersection`), 3 variants
- High-Entry-Angle Right Turn (`high_entry_angle_right_turn`), 1 variant
- Left Turn Calming Intersection (`left_turn_calming_intersection`), 3 variants
- Mini-Roundabout (Diagram) (`mini_roundabout_diagram`), 1 variant
- Neighborhood Traffic Circle (`neighborhood_traffic_circle`), 4 variants
- Pedestrian Scramble Intersection (`pedestrian_scramble_intersection`), 3 variants
- Protected Intersection (`protected_intersection`), 4 variants
- Protected Intersection (Diagram) (`protected_intersection_diagram`), 1 variant
- Raised Intersection (`raised_intersection`), 3 variants
- Raised Intersection (Diagram) (`raised_intersection_diagram`), 1 variant
- Roundabout (`roundabout`), 4 variants

### Traffic calming & safer streets (18)

- Chicane (Diagram) (`chicane_diagram`), 1 variant
- Continuous Crossing (Continuous Sidewalk) (`continuous_sidewalk_street`), 4 variants
- Curb Extension Crossing (Diagram) (`curb_extension_crossing_diagram`), 1 variant
- Curb Extension Crossing Street (`curb_extension_crossing_street`), 4 variants
- Directional / Full Closure (`directional_full_closure`), 2 variants
- Diverter (Modal Filter) (`modal_filter_diverter`), 4 variants
- Neighborhood Gateway (`neighborhood_gateway`), 3 variants
- Raised Crossing (`raised_crossing_collector`), 4 variants
- Raised Crossing (Diagram) (`raised_crossing_diagram`), 1 variant
- Right-In Right-Out Median (`right_in_right_out_median`), 1 variant
- Speed Cushion (Diagram) (`speed_cushion_diagram`), 1 variant
- Speed Cushion Street (`speed_cushion_street`), 3 variants
- Speed Hump (Diagram) (`speed_hump_diagram`), 1 variant
- Speed Hump (Local Street) (`speed_hump_local_street`), 1 variant
- Speed Table (Diagram) (`speed_table_diagram`), 1 variant
- Traffic Calmed Local Street (`traffic_calmed_local_street`), 4 variants
- Two-Stage Crossing Median (Diagram) (`two_stage_crossing_median_diagram`), 1 variant
- Two-Stage Crossing Median (Pedestrian Refuge) (`refuge_island_arterial`), 4 variants

### Other streets & global inspiration (14)

- Amsterdam Straat (Main Street) (`amsterdam_straat`), 4 variants
- Barcelona Eixample Carrer (`barcelona_eixample_carrer`), 4 variants
- Custom Streets / Pathways (`custom_streets_pathways`), 4 variants
- Halifax Steep Residential Street (`halifax_steep_residential_street`), 4 variants
- London Crescent Road (`london_crescent_road`), 4 variants
- London Terrace Street (`london_terrace_street`), 4 variants
- Main Street Complete (`main_street_complete`), 4 variants
- Montreal Commercial Boulevard (`montreal_commercial_boulevard`), 4 variants
- New York Brownstone Side Street (`new_york_brownstone_side_street`), 4 variants
- Parisian Rue (Typical Street) (`parisian_rue`), 4 variants
- Scenic Parkway (`scenic_parkway`), 4 variants
- SoHo Cobblestone Street (`soho_cobblestone_street`), 4 variants
- Toronto Victorian Residential Street (`toronto_victorian_residential_street`), 4 variants
- Vancouver Back Lane (`vancouver_back_lane`), 4 variants
