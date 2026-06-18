/**
 * Archetype Shade Map
 *
 * Maps every archetype ID to a unique hex "shadeId" colour, grouped by hue family:
 *   - Red   (h 5-15, s 55-90%, l 35-55%)  : commercial / mixed-use / institutional / industrial
 *   - Yellow (h 45-55, s 60-90%, l 40-55%) : purely residential
 *   - Gray  (h 0, s 0-8%, l 30-60%)        : streets & pathways
 *   - Green (h 90-160, s 30-70%, l 25-50%) : parks & green space
 *   - Teal  (h 170-200, s 30-60%, l 30-50%): plazas & hardscape
 *   - Blue  (h 200-230, s 40-70%, l 30-50%): water features & parking
 *
 * Every shade within a family is guaranteed >= 2 % HSL lightness or saturation
 * apart from its neighbours.
 */

// ---------------------------------------------------------------------------
// Shade map  (archetypeId -> hex)
// ---------------------------------------------------------------------------

export const SHADE_MAP: Record<string, string> = {
  // ── Red family: Commercial / Mixed-use / Institutional ──────────────
  brownstone_rowhouse_frontage:       '#8a3028',
  historical_brick_main_street:       '#9e382e',
  victorian_heritage_avenue:          '#b23f34',
  contemporary_midrise_residential:   '#c64739',
  modern_glass_office_institutional:  '#cb5a4d',
  modernist_civic_block:              '#8f2f24',
  mid_century_modern_pavilion_block:  '#a33729',
  civic_classical_building:           '#b83e2e',
  monumental_courthouse_axis:         '#cc4633',
  industrial_brick_mixed_use:         '#d15947',
  adaptive_reuse_warehouse_lofts:     '#932f1f',
  nordic_timber_midrise:              '#a83624',
  mediterranean_arcade_mixed_use:     '#bd3e28',
  parametric_future_hub:              '#d2462d',
  autonomous_tech_campus:             '#d75942',
  art_deco_setback_tower:             '#982f1b',
  deco_theater_mainstreet:            '#ad361f',
  traditional_vernacular_market_street: '#c33e22',
  parisian_midrise_block:             '#d94626',
  parisian_boulevard_corner:          '#dd593c',
  alpine_mixed_use_lodge:             '#9c2f16',
  transit_oriented_station_block:     '#b33719',
  transit_podium_residential:         '#c93f1d',
  glass_tower_podium_modern:          '#df4720',
  skyline_glass_office_cluster:       '#e25a36',
  civic_monumental_institution:       '#a13012',
  monumental_museum_axis:             '#b83814',
  japanese_machiya_mixed_use:         '#cf4017',
  eco_urban_bioclimatic_block:        '#e64819',
  coastal_resort_terrace_block:       '#e85b30',
  coastal_breezeway_mixed_use:        '#a5320d',
  custom_prompt_ready_archetype:      '#bd3a0f',
  custom_contextual_experiment:       '#d44211',
  rural_gas_station:                   '#d24f2a',
  commercial_strip_mall:              '#c84d2b',
  highway_motor_hotel:                '#d95a28',

  // ── Yellow family: Residential ──────────────────────────────────────
  rndsqr_missing_middle_townhomes:    '#c5a52c',
  classic_brownstone_streetwall:      '#a38529',
  contemporary_townhouse_courtyard:   '#c2a030',
  detached_contemporary_infill:       '#d1b347',
  courtyard_family_housing:           '#ab8f21',
  scandinavian_urban_residential:     '#cbac27',
  mediterranean_villa_estate:         '#dabf3f',
  vernacular_courtyard_housing:       '#b39a19',
  minimalist_courtyard_block:         '#d4ba1e',
  minimalist_infill_townhouse:        '#e2cc36',
  mountain_alpine_chalet:             '#baa712',
  japanese_contemporary_lanehouse:    '#ddc915',
  vertical_forest_residential:        '#ebdb2e',

  // ── Gray family: Streets & Pathways ─────────────────────────────────
  narrow_residential_street:          '#4d4d4d',
  suburban_residential_street:        '#565656',
  collector_road:                     '#5f5f5f',
  arterial_boulevard:                 '#686868',
  highway_freeway:                    '#717171',
  roundabout:                         '#7a7a7a',
  cul_de_sac:                         '#838383',
  back_alley_service_lane:            '#8c8c8c',
  separated_bike_lane:                '#959595',
  multi_use_trail:                    '#4f4a4a',
  pedestrian_promenade:               '#585353',
  woonerf_shared_street:              '#615c5c',
  brt_corridor:                       '#6a6565',
  light_rail_avenue:                  '#736e6e',
  main_street_complete:               '#7c7777',
  campus_pedestrian_spine:            '#858080',
  scenic_parkway:                     '#8e8989',
  riverfront_promenade:               '#979292',
  custom_streets_pathways:            '#a09b9b',

  // ── Calgary Street Manual (cool-gray sub-band) ──────────────────────
  calgary_collector:                  '#5a6066',
  calgary_alley:                      '#4e545a',
  calgary_local:                      '#545a60',
  calgary_local_industrial:           '#606870',
  calgary_local_high_activity:        '#666e76',
  calgary_local_rural:                '#6c747c',
  calgary_collector_industrial:       '#727a82',
  calgary_collector_high_activity:    '#787f86',
  calgary_arterial_4lane_50:          '#5d646b',
  calgary_arterial_4lane_70:          '#636a71',
  calgary_arterial_high_activity:     '#697077',
  calgary_arterial_6lane:             '#6f767d',
  calgary_skeletal:                   '#757c83',

  // ── Traffic Safety & Vision Zero (teal-green sub-band) ──────────────
  curb_extension_crossing_street:     '#2f6f5f',
  protected_intersection:             '#34766a',
  road_diet_complete_street:          '#3a7d68',
  refuge_island_arterial:             '#407f5c',
  raised_crossing_collector:          '#46836f',
  traffic_calmed_local_street:        '#4c8a77',
  school_street:                      '#52917f',
  floating_bus_stop_transit_street:   '#387a72',
  continuous_sidewalk_street:         '#2c6857',
  compact_safety_roundabout:          '#256353',
  pedestrian_scramble_intersection:   '#5a9887',
  daylighted_intersection:            '#609e8e',
  left_turn_calming_intersection:     '#2a5f50',
  neighborhood_gateway:               '#66a596',
  neighborhood_greenway:              '#3d8a6f',
  modal_filter_diverter:              '#2e7358',
  neighborhood_traffic_circle:        '#6ba98e',
  raised_intersection:                '#438f78',
  advisory_bike_lane_street:          '#5fa07d',
  speed_cushion_street:               '#357051',
  speed_hump_local_street:            '#4f9580',
  high_entry_angle_right_turn:        '#2b6b54',
  right_in_right_out_median:          '#266048',
  directional_full_closure:           '#56977f',
  protected_intersection_diagram:     '#2f8068',
  compact_safety_roundabout_diagram:  '#33856f',
  curb_extension_crossing_diagram:    '#3a9079',
  // Calgary Street Manual Ch10 traffic-calming technical-drawing diagram siblings
  speed_hump_diagram:                 '#3c8a6a',
  speed_table_diagram:                '#46977a',
  speed_cushion_diagram:              '#2e7e64',
  raised_crossing_diagram:            '#52a088',
  raised_intersection_diagram:        '#379070',
  two_stage_crossing_median_diagram:  '#5fa890',
  mini_roundabout_diagram:            '#2b7358',
  chicane_diagram:                    '#66b09a',

  // ── Blue family: Alberta Bike Design Guide ──────────────────────────
  protected_bike_lane_bidirectional:  '#2f7fb0',
  bicycle_shared_space:               '#3f93c0',
  bicycle_lane_painted:               '#4a9bc7',
  bicycle_accessible_shoulder:        '#5aa6cd',
  bicycle_pathway:                    '#6bb2d6',

  // ── Green family: Parks & Green Space ───────────────────────────────
  urban_pocket_park:                  '#2d6b30',
  neighborhood_park:                  '#357a38',
  community_park:                     '#3d8940',
  regional_park:                      '#2a5e2d',
  dog_park:                           '#4b8f4e',
  skate_park:                         '#539756',
  sports_field_complex:               '#3a7f3d',
  tennis_court_cluster:               '#5ba05e',
  botanical_garden:                   '#326e35',
  japanese_garden:                    '#427442',
  memorial_garden:                    '#4a7d4d',
  urban_forest:                       '#255725',
  riparian_buffer:                    '#2f632f',
  wetland_rain_garden:                '#376b3a',
  playground_adventure:               '#63a866',
  splash_pad_area:                    '#6bb06e',
  amphitheater_lawn:                  '#527f55',
  community_garden:                   '#5a8a5d',
  cemetery_memorial_grounds:          '#488048',

  // ── Teal family: Plazas & Hardscape ─────────────────────────────────
  formal_civic_plaza:                 '#2d6b6b',
  market_square:                      '#357a7a',
  courtyard_plaza:                    '#3d7878',
  promenade_boardwalk:                '#2a6060',
  transit_plaza:                      '#458585',
  amphitheater_performance_space:     '#4d8d8d',
  slip_lane_pocket_plaza:             '#3f8e7a',
  reclaimed_street_plaza:             '#2e8073',

  // ── Blue family: Water Features & Parking ───────────────────────────
  surface_parking_lot:                '#4a6a8a',
  structured_parking_garage:          '#527292',
  underground_parking_entry:          '#3f5f7f',
  green_parking_lot:                  '#5a7a9a',
  suburban_retail_parking_lot:        '#6486a4',
  pond_lake:                          '#2d5b8a',
  fountain_water_feature:             '#356392',
  stormwater_retention_pond:          '#3d6b9a',
  swimming_pool_complex:              '#4573a2',
  canal_waterway:                     '#2a5580',

  // ── Red family: Institutional (new) ─────────────────────────────────
  collegiate_gothic_education:        '#7a2820',
  neoclassical_institutional:         '#8e3325',
  brutalist_institutional:            '#6e241c',
  contemporary_civic:                 '#a33d2a',

  // ── Red family: Healthcare ────────────────────────────────────────
  art_deco_healthcare:                '#b7452f',
  functionalist_healthcare:           '#c44e38',
  biophilic_healthcare:               '#7f2b1e',

  // ── Red family: Industrial ────────────────────────────────────────
  daylight_factory:                   '#8b3520',
  industrial_park_modernism:          '#9a3c25',
  art_deco_industrial:                '#a9432a',
  functionalist_brick_industrial:     '#7c2e19',
  structural_expressionism_industrial:'#8d3721',
  corrugated_vernacular_industrial:   '#9e4029',
  machine_aesthetic_heavy_industrial: '#723118',
  brutalist_utility_heavy_industrial: '#833a20',
  early_20c_megastructure_industrial: '#944328',
  romanesque_revival_warehouse:       '#682a14',
  modern_bigbox_warehouse:            '#8a3c24',

  // ── Red family: Hospitality ───────────────────────────────────────
  boutique_hotel_tower:               '#ba4a35',
  chateauesque_hotel:                 '#c7533e',
  resort_modernism_hotel:             '#d45c47',
  corporate_tower_hotel:              '#ad4130',

  // ── Red family: Transit ───────────────────────────────────────────
  historic_grand_station:             '#96382b',
  contemporary_transit_hub:           '#a44133',
  urban_light_rail_stop:              '#b24a3b',

  // ── Red/Orange family: Recreation ─────────────────────────────────
  community_recreation_centre:        '#c05040',
  modern_sports_arena:                '#cd5948',
  parkitecture_recreational:          '#6a2915',
  civic_modernism_rec_centre:         '#7b321d',
  postmodern_rec_centre:              '#8c3b25',
  contemporary_sustainable_rec_centre:'#9d442d',
  monumental_antiquity_arena:         '#753019',
  high_tech_arena:                    '#863921',
  concrete_megastructure_arena:       '#974229',

  // ── Red/Orange family: Specialty ──────────────────────────────────
  climbing_wall_building:             '#ae4b31',
  waste_to_energy_plant:              '#6f2c16',
  brewery_distillery:                 '#80351e',
  solar_farm_agrivoltaics:            '#913e26',
  immersive_experience_venue:         '#a2472e',
  modern_fire_station:                '#b35036',

  // ── Yellow family: Senior Living ──────────────────────────────────
  senior_living_complex:              '#c4a510',

  // ── Gray family: Streets (new) ─────────────────────────────────────
  downtown_thoroughfare:              '#a4a0a0',
  pedestrian_only_street:             '#adaaa8',
  green_alley:                        '#b5b2b0',
  commercial_alley_laneway:           '#bdbab8',
  yield_street:                       '#c5c2c0',
  neighborhood_main_street:           '#cdc9c7',
  elevated_rail_transit:              '#d5d1cf',

  // ── Gray family: City-specific Streets ─────────────────────────────
  amsterdam_gracht:                   '#4e4847',
  amsterdam_steeg:                    '#544f4d',
  amsterdam_straat:                   '#5b5553',
  barcelona_eixample_carrer:          '#625b59',
  barcelona_passatge:                 '#68625f',
  barcelona_passeig:                  '#6f6865',
  haussmann_boulevard:                '#756f6b',
  parisian_passage:                   '#7c7571',
  parisian_rue:                       '#827c77',
  london_crescent_road:               '#89827d',
  london_mews_lane:                   '#908984',
  london_terrace_street:              '#96908a',
  new_york_brownstone_side_street:    '#4b4544',
  soho_cobblestone_street:            '#524c4a',
  montreal_commercial_boulevard:      '#585250',
  montreal_plateau_residential_rue:   '#5f5856',
  montreal_ruelle_verte:              '#655f5c',
  toronto_laneway:                    '#6c6562',
  toronto_streetcar_street:           '#726c68',
  toronto_victorian_residential_street:'#79726e',
  vancouver_back_lane:                '#7f7974',
  vancouver_cherry_blossom_street:    '#867f7a',
  bow_river_pathway:                  '#8c8681',
  inglewood_main_street:              '#938c87',
  skytrain_elevated_corridor:         '#9a938d',
  stephen_avenue_pedestrian_mall:     '#a09993',
  halifax_steep_residential_street:   '#504a48',
  halifax_waterfront_boardwalk:       '#574f4e',
  brt_bus_rapid_transit_corridor:     '#5d5754',
  elevated_rail_transit_corridor:     '#645d5a',
  light_rail_tram_avenue:             '#6b6460',

  // ── Gray family: Bridges ───────────────────────────────────────────
  urban_vehicular_bridge:             '#736d68',
  landmark_signature_bridge:          '#7a746f',
  rail_transit_viaduct:               '#817b76',
  transit_priority_bridge:            '#88827d',
  urban_pedestrian_footbridge:        '#4c4644',
  landscape_park_pedestrian_bridge:   '#534d4b',
  dedicated_cycle_bridge:             '#5a5452',
  shared_cycle_pedestrian_bridge:     '#615b59',

  // ── Green family: Parks (new) ──────────────────────────────────────
  linear_park_greenway:               '#2b5f32',
  nature_preserve:                    '#1e4f1e',
  rooftop_garden:                     '#4d9450',
  riverfront_park_beach:              '#3a7545',
  street_plaza_parklet:               '#558e58',

  // ── Green family: Sports & Recreation ────────────────────────────────
  basketball_court:                   '#367a28',
  pickleball_courts:                  '#378131',
  soccer_pitch_caged:                 '#227622',
  running_track_oval:                 '#3a8740',
  outdoor_fitness_circuit:            '#2b7c39',
  baseball_softball_diamond:          '#478329',
  cricket_pitch_oval:                 '#4a8536',
  disc_golf_course:                   '#387e4a',
  bocce_petanque_court:               '#2c7143',
  climbing_bouldering_wall:           '#246e43',
  pump_track:                         '#2c7742',
  outdoor_ice_rink:                   '#3e7e66',
  beach_volleyball_courts:            '#34794d',
  mini_golf_course:                   '#31932e',

  // ── Green family: Children & Nature ────────────────────────────────
  nature_play_area:                   '#518a28',
  inclusive_playground:                '#489635',

  // ── Green family: Ecological ───────────────────────────────────────
  pollinator_meadow:                  '#517a2e',
  urban_orchard_food_forest:          '#447627',
  bioswale_rain_garden:               '#327b40',

  // ── Green family: Cultural & Waterfront ────────────────────────────
  urban_beach:                        '#42896b',
  sculpture_garden:                   '#377b56',
  labyrinth_meditation:               '#417f62',
  festival_event_lawn:                '#3c8631',
  kayak_launch_dock:                  '#3a7c69',

  // ── Red family: City-Specific Buildings ─────────────────────────────
  amsterdam_bell_gable_house:         '#912f26',
  amsterdam_brown_cafe:               '#a12f23',
  amsterdam_canal_warehouse:          '#b12f1f',
  amsterdam_cornice_house:            '#c32f1a',
  amsterdam_hofje:                    '#d52f15',
  amsterdam_jordaan_house:            '#c34933',
  amsterdam_neck_gable_house:         '#d24c32',
  amsterdam_school_housing:           '#9c321b',
  amsterdam_spout_gable_house:        '#ac3317',
  amsterdam_step_gable_house:         '#be3512',
  barcelona_corner_chamfer:           '#af4a2e',
  barcelona_mercat:                   '#c04c2a',
  barcelona_modernist_workshop:       '#d24f25',
  barcelona_townhouse:                '#e15323',
  calgary_cbe_brutalist_hq:           '#a73910',
  concert_hall_modern:                '#9b4929',
  ev_charging_hub:                    '#ab4d25',
  farnsworth_house_glass_pavilion:    '#bc5121',
  food_hall_market_hall:              '#ce551c',
  hyperscale_data_center:             '#e15a16',
  mall_redevelopment:                 '#ca6c39',
  shophouse_southeast_asian:          '#964b21',
  terraced_stepped_building:          '#a6511d',
  vertical_farm:                      '#b85719',
  vertiport_evtol:                    '#c95d13',

  // ── Green family: City-Specific Parks ──────────────────────────────
  amsterdam_hofje_garden:             '#445a2e',
  amsterdam_plein:                    '#496830',
  amsterdam_vondelpark:               '#4d7730',
  barcelona_pati_interior:            '#4e8630',
  barcelona_placa_xamfra:             '#4e972f',
  barcelona_superilla:                '#4ca82e',
  calgary_prairie_plaza:              '#5c974e',
  calgary_princes_island:             '#5aa74d',
  community_garden_enhanced:          '#2d6127',
  halifax_coastal_park:               '#2c7028',
  halifax_public_gardens:             '#287f28',
  london_circus:                      '#27902c',
  london_garden_square:               '#438349',
  montreal_mount_royal:               '#43924f',
  montreal_square:                    '#42a255',
  newyork_community_garden:           '#40b35d',
  newyork_pocket_park:                '#216836',
  parisian_jardin:                    '#20783f',
  parisian_place:                     '#396f4e',
  parisian_square:                    '#397d58',
  toronto_ravine:                     '#398d63',
  toronto_urban_square:               '#389d70',
  vancouver_beach_park:               '#37ae7e',
  vancouver_seawall:                  '#34c08f',


  // ── Red family: City-Specific Buildings (batch 2) ───────────────
  calgary_beltline_mid_rise:                    '#822a25',
  calgary_ctrain_station:                       '#8f2a23',
  calgary_inner_city_bungalow:                  '#9d2a21',
  calgary_modern_infill_house:                  '#ab291e',
  calgary_new_central_library:                  '#ba291a',
  calgary_plus_15_connected_tower:              '#c92816',
  calgary_sandstone_heritage:                   '#d92711',
  rndsqr_terraced_mixed_use_midrise:            '#762b27',
  ecole_republicaine:                           '#bf4737',
  eixample_apartment_block:                     '#cc4935',
  gastown_heritage_commercial:                  '#8a2c1d',
  georgian_terrace_house:                       '#982d1a',
  grand_magasin:                                '#a62e17',
  halifax_ferry_terminal:                       '#b52f14',
  halifax_georgian_colonial:                    '#c5300f',
  halifax_maritime_commercial:                  '#ad4932',
  halifax_painted_clapboard_row:                '#bc4b2f',
  halifax_waterfront_warehouse:                 '#cb4c2b',
  hotel_particulier:                            '#d94f28',
  hydrostone_neighbourhood_house:               '#933215',
  inglewood_heritage_brick_commercial:          '#a13411',
  london_crescent_terrace:                      '#b0360e',
  london_mews_house:                            '#9c4a2d',
  london_townhouse:                             '#aa4d2a',
  marche_couvert:                               '#b95027',
  mile_end_cultural_triplex:                    '#c85323',
  modernisme_casa:                              '#d7561e',
  montreal_depanneur:                           '#e55a1c',
  montreal_duplex:                              '#9b3a0c',
  montreal_plateau_triplex:                     '#8b4828',
  montreal_second_empire_civic:                 '#984d26',
  new_york_art_deco_tower:                      '#a65123',
  new_york_corner_bodega:                       '#b5551f',
  new_york_pre_war_apartment:                   '#c45a1c',
  new_york_walk_up_tenement:                    '#d45f17',
  old_montreal_limestone_commercial:            '#e46412',
  old_montreal_warehouse_loft:                  '#c6733b',
  parisian_cafe_brasserie:                      '#864b21',
  parisian_corner_with_dome:                    '#94501f',
  passage_couvert:                              '#a2561c',
  pre_haussmann_marais_building:                '#b05b19',
  regency_stucco_terrace:                       '#bf6215',
  skytrain_elevated_station:                    '#cf6810',
  soho_cast_iron_loft_building:                 '#b67135',
  toronto_annex_mansion:                        '#c57831',
  toronto_bay_and_gable_house:                  '#d27f2f',
  toronto_brick_rowhouse:                       '#8f5419',
  toronto_condo_podium_tower:                   '#9d5b16',
  toronto_edwardian_foursquare:                 '#ab6213',
  toronto_junction_converted_industrial:        '#ba6a0f',
  toronto_streetcar_platform_stop:              '#a56f2f',
  vancouver_craftsman_bungalow:                 '#b3762c',
  vancouver_laneway_house:                      '#c27e29',
  vancouver_special:                            '#d18725',
  vancouverism_tower_podium:                    '#df9022',
  victorian_bay_window_terrace:                 '#976010',
  west_end_mid_century_tower:                   '#a6690d',

  // ── Custom ──────────────────────────────────────────────────────────
  custom_parks_plazas:                '#629062',
};

// ---------------------------------------------------------------------------
// Reverse lookup  (hex -> archetypeId)
// ---------------------------------------------------------------------------

export const SHADE_TO_ARCHETYPE: Map<string, string> = new Map(
  Object.entries(SHADE_MAP).map(([id, hex]) => [hex.toLowerCase(), id]),
);

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Return the unique shade hex for a given archetype ID.
 * Falls back to a neutral mid-gray (`#888888`) if the ID is unknown.
 */
export function getShadeForArchetype(archetypeId: string): string {
  // Exact match first
  if (SHADE_MAP[archetypeId]) return SHADE_MAP[archetypeId];

  // Prefix match: the stored ID may be an image-level ID like
  // "parisian_midrise_block_front_day" while the shade map key is the
  // option-level "parisian_midrise_block".  Try all shade map keys as prefixes.
  for (const key of Object.keys(SHADE_MAP)) {
    if (archetypeId.startsWith(key + '_') || archetypeId.startsWith(key)) {
      return SHADE_MAP[key];
    }
  }

  return '#888888';
}

/**
 * Given a hex colour, find the archetype whose shade is closest within
 * an optional per-channel RGB tolerance (default +-3).
 *
 * Returns `null` when no archetype falls within the tolerance window.
 */
export function getArchetypeForShade(
  shadeHex: string,
  tolerance = 3,
): string | null {
  const target = hexToRgb(shadeHex);
  if (!target) return null;

  // Fast exact match first
  const exact = SHADE_TO_ARCHETYPE.get(shadeHex.toLowerCase());
  if (exact) return exact;

  // Fuzzy scan
  let bestId: string | null = null;
  let bestDist = Infinity;

  for (const [hex, id] of SHADE_TO_ARCHETYPE) {
    const rgb = hexToRgb(hex)!;
    const dr = Math.abs(rgb.r - target.r);
    const dg = Math.abs(rgb.g - target.g);
    const db = Math.abs(rgb.b - target.b);

    if (dr <= tolerance && dg <= tolerance && db <= tolerance) {
      const dist = dr + dg + db;
      if (dist < bestDist) {
        bestDist = dist;
        bestId = id;
      }
    }
  }

  return bestId;
}

// ---------------------------------------------------------------------------
// Internal
// ---------------------------------------------------------------------------

function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const m = /^#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$/i.exec(hex);
  if (!m) return null;
  return { r: parseInt(m[1], 16), g: parseInt(m[2], 16), b: parseInt(m[3], 16) };
}
