# Codex prompt: check that every clay model is being used in City Prompt

Copy everything below the line into Codex as its first message.

---

Check that every 3D model built on branch `claude/ten-new-buildings` of
https://github.com/aasedor/CityPrompt is actually being used in City Prompt, and fix the gaps. Read
`CLAUDE.md` first and follow it.

**What to check.** The table at the end lists all 74 model families (`tools/clay_<name>/`). For each one,
find out whether a student in the current app (`origin/main`, run on localhost:5174) can pick that
catalogue archetype and variant and get **this** model, at the candidate version listed. Check every
link in the chain, for example:

- the GLB is on `main` (through Git LFS) and is the same file as the candidate listed;
- buildings: the promotion package and model-library entry (`tools/catalogue_promotion.py`,
  `tools/seed_model_library.py`, `seed/model-library/model_library.json`) and any runtime family in
  `frontend/public/families/`;
- parks and streets: the native registries (`nativeParks.json`, `nativeStreetPilots.json`) and
  `streetFamilyCatalog.ts`;
- the picker card for that archetype and variant resolves to the model, and it loads when placed.

Then open the app and confirm it like a student: place it, rotate it, save, reload, capture, and check
for console errors.

**Classify each model** as:

- **USED**: works end to end with the candidate version listed;
- **PARTIAL**: say which link is missing or wrong (for example an older version, a different variant,
  missing from the picker, fails to load);
- **NOT USED**: not wired in at all.

**Then fix the gaps.** For every model marked `passed` that is not fully USED, implement it with the
repository's existing process, as in `docs/showcase/CODEX_INTEGRATION_PROMPT_2026-10-23.md`
(`docs/BUILDING_CATALOGUE_WORKFLOW.md`, the native park and street registries, and
`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`). Do one end to end first and show me screenshots, then do the
rest in batches. For models marked `open findings`, only report them; do not implement them unless I
say so. Their README lists the open findings.

**Rules:**

- The models' branch is far from `main`, so do not merge it. Work on `codex/*` branches from
  `origin/main` and copy over only each model's folder.
- Don't change the GLBs. If a model is broken, skip it and tell me.
- Never parse-and-rewrite `buildingArchetypes.json` or the other archetype catalogues.
- Commit GLBs through Git LFS as the workflow requires.
- Open PRs to `main` and merge only when CI passes. Never force-push.

**Send me back:**

- This table with a USED / PARTIAL / NOT USED column added, and for PARTIAL what is missing.
- What you implemented, with screenshots in the app and the PR links.
- Anything in the app that points at an older or different version of one of these models.

## The models

39 passed their last independent review with zero P0 and zero P1 findings; 35 still have open findings.

| # | type | family folder | catalogue archetype / variant | review status | candidate GLB |
|---|---|---|---|---|---|
| 1 | building | `tools/clay_arched_mill_mixed_use` | `industrial_brick_mixed_use` / `variant_0` | passed | `clay-arched-mill-mixed-use-clay-v005.glb` |
| 2 | building | `tools/clay_baronial_railway_hotel` | `chateauesque_grand_railway_hotel` / `variant_0` | passed | `clay-baronial-railway-hotel-clay-v006.glb` |
| 3 | building | `tools/clay_brick_podium_condo_tower` | `condo_podium_tower` / `variant_0` | passed | `clay-brick-podium-condo-tower-clay-v006.glb` |
| 4 | building | `tools/clay_calgary_cbe_brutalist_hq` | `calgary_cbe_brutalist_hq` / `variant_0` | passed | `clay-calgary-cbe-brutalist-hq-clay-v004.glb` |
| 5 | building | `tools/clay_calgary_sandstone_heritage` | `calgary_sandstone_heritage` / `variant_0` | passed | `clay-calgary-sandstone-heritage-clay-v006.glb` |
| 6 | building | `tools/clay_campus_shed_office` | `corporate_office_campus_headquarters` / `variant_3` | passed | `clay-campus-shed-office-clay-v009.glb` |
| 7 | building | `tools/clay_climbing_crucible` | `climbing_wall_building` / `variant_0` | passed | `clay-climbing-crucible-clay-v004.glb` |
| 8 | building | `tools/clay_climbing_overhang` | `climbing_wall_building` / `variant_1` | passed | `clay-climbing-overhang-clay-v007.glb` |
| 9 | building | `tools/clay_climbing_reef` | `climbing_wall_building` / `variant_3` | passed | `clay-climbing-reef-clay-v009.glb` |
| 10 | building | `tools/clay_cmu_dock_warehouse` | `mid_century_distribution_warehouse` / `variant_0` | passed | `clay-cmu-dock-warehouse-clay-v006.glb` |
| 11 | building | `tools/clay_courtyard_primary_school` | `ecole_republicaine` / `variant_3` | passed | `clay-courtyard-primary-school-clay-v009.glb` |
| 12 | building | `tools/clay_ctrain_elevated_station` | `calgary_ctrain_station` / `variant_0` | passed | `clay-ctrain-elevated-station-clay-v004.glb` |
| 13 | building | `tools/clay_energy_centre` | `central_utilities_plant_energy_centre` / `variant_1` | passed | `clay-energy-centre-clay-v010.glb` |
| 14 | building | `tools/clay_garden_court_senior_residence` | `senior_living_complex` / `variant_0` | passed | `clay-garden-court-senior-residence-clay-v006.glb` |
| 15 | building | `tools/clay_gastown_heritage_commercial` | `gastown_heritage_commercial` / `variant_0` | passed | `clay-gastown-heritage-commercial-clay-v003.glb` |
| 16 | building | `tools/clay_halifax_georgian_colonial` | `halifax_georgian_colonial` / `variant_0` | passed | `clay-halifax-georgian-colonial-clay-v003.glb` |
| 17 | building | `tools/clay_halifax_waterfront_warehouse` | `halifax_waterfront_warehouse` / `variant_0` | passed | `clay-halifax-waterfront-warehouse-clay-v006.glb` |
| 18 | building | `tools/clay_led_grow_block` | `vertical_farm_indoor_agriculture` / `variant_1` | passed | `clay-led-grow-block-clay-v007.glb` |
| 19 | building | `tools/clay_mews_coach_house` | `london_mews_house` / `variant_0` | passed | `clay-mews-coach-house-clay-v006.glb` |
| 20 | building | `tools/clay_old_montreal_limestone_commercial` | `old_montreal_limestone_commercial` / `variant_0` | passed | `clay-old-montreal-limestone-commercial-clay-v004.glb` |
| 21 | building | `tools/clay_plus15_glass_office_tower` | `calgary_plus_15_connected_tower` / `variant_2` | passed | `clay-plus15-glass-office-tower-clay-v006.glb` |
| 22 | building | `tools/clay_slab_balcony_tower` | `west_end_mid_century_tower` / `variant_0` | passed | `clay-slab-balcony-tower-clay-v007.glb` |
| 23 | building | `tools/clay_toronto_bay_and_gable` | `toronto_bay_and_gable_house` / `variant_0` | passed | `clay-toronto-bay-and-gable-house-clay-v004.glb` |
| 24 | building | `tools/clay_amsterdam_canal_warehouse` | `amsterdam_canal_warehouse` / `variant_0` | open findings | `clay-amsterdam-canal-warehouse-clay-v003.glb` |
| 25 | building | `tools/clay_anchored_plaza_supermarket` | `commercial_strip_mall` / `variant_1` | open findings | `clay-anchored-plaza-supermarket-clay-v010.glb` |
| 26 | building | `tools/clay_beltline_brick_midrise` | `calgary_beltline_mid_rise` / `variant_0` | open findings | none committed (stopped because the archetype already has a model) |
| 27 | building | `tools/clay_braced_frame_hospital` | `regional_hospital_medical_center` / `variant_0` | open findings | `clay-braced-frame-hospital-clay-v003.glb` |
| 28 | building | `tools/clay_brick_parkade` | `campus_parking_structure` / `variant_0` | open findings | `clay-brick-parkade-clay-v003.glb` |
| 29 | building | `tools/clay_cantilever_fire_station` | `modern_fire_station` / `variant_2` | open findings | `clay-cantilever-fire-station-clay-v009.glb` |
| 30 | building | `tools/clay_chamfer_corner_dome_block` | `barcelona_corner_chamfer` / `variant_0` | open findings | `clay-chamfer-corner-dome-block-clay-v006.glb` |
| 31 | building | `tools/clay_climbing_spine` | `climbing_wall_building` / `variant_2` | open findings | `clay-climbing-spine-clay-v007.glb` |
| 32 | building | `tools/clay_courtyard_mixed_use_midrise` | `rndsqr_terraced_mixed_use_midrise` / `variant_0` | open findings | `clay-courtyard-mixed-use-midrise-clay-v009.glb` |
| 33 | building | `tools/clay_craneway_hall` | `early_20c_megastructure_industrial` / `variant_1` | open findings | `clay-craneway-hall-clay-v007.glb` |
| 34 | building | `tools/clay_etfe_truss_stadium` | `outdoor_sports_stadium` / `variant_0` | open findings | `clay-etfe-truss-stadium-clay-v003.glb` |
| 35 | building | `tools/clay_exoskeleton_research_lab` | `research_laboratory` / `variant_0` | open findings | `clay-exoskeleton-research-lab-clay-v003.glb` |
| 36 | building | `tools/clay_georgian_terrace_house` | `georgian_terrace_house` / `variant_0` | open findings | `clay-georgian-terrace-house-clay-v003.glb` |
| 37 | building | `tools/clay_grand_magasin` | `grand_magasin` / `variant_0` | open findings | `clay-grand-magasin-clay-v004.glb` |
| 38 | building | `tools/clay_halifax_ferry_terminal` | `halifax_ferry_terminal` / `variant_0` | open findings | `clay-halifax-ferry-terminal-clay-v002.glb` |
| 39 | building | `tools/clay_limited_service_hotel` | `highway_motor_hotel` / `variant_2` | open findings | `clay-limited-service-hotel-clay-v007.glb` |
| 40 | building | `tools/clay_modernista_market_hall` | `barcelona_mercat` / `variant_0` | open findings | `clay-modernista-market-hall-clay-v003.glb` |
| 41 | building | `tools/clay_plateau_stair_triplex` | `montreal_plateau_triplex` / `variant_0` | open findings | `clay-plateau-stair-triplex-clay-v003.glb` |
| 42 | building | `tools/clay_prewar_apartment_tower` | `new_york_pre_war_apartment` / `variant_0` | open findings | `clay-prewar-apartment-tower-clay-v003.glb` |
| 43 | building | `tools/clay_queen_anne_rowhouse_trio` | `brick_rowhouse_terrace` / `variant_2` | open findings | `clay-queen-anne-rowhouse-trio-clay-v009.glb` |
| 44 | building | `tools/clay_regency_stucco_terrace` | `regency_stucco_terrace` / `variant_0` | open findings | `clay-regency-stucco-terrace-clay-v004.glb` |
| 45 | building | `tools/clay_sculptural_superblock` | `residential_superblock` / `variant_0` | open findings | `clay-sculptural-superblock-clay-v003.glb` |
| 46 | building | `tools/clay_second_empire_city_hall` | `montreal_second_empire_civic` / `variant_0` | open findings | `clay-second-empire-city-hall-clay-v004.glb` |
| 47 | building | `tools/clay_step_gable_canal_house` | `amsterdam_step_gable_house` / `variant_0` | open findings | `clay-step-gable-canal-house-clay-v003.glb` |
| 48 | building | `tools/clay_student_residence_tower` | `student_residence_tower` / `variant_0` | open findings | `clay-student-residence-tower-clay-v002.glb` |
| 49 | building | `tools/clay_terraced_stepped_tower` | `terraced_stepped_building` / `variant_0` | open findings | `clay-terraced-stepped-tower-clay-v001.glb` |
| 50 | building | `tools/clay_vancouver_laneway_house` | `vancouver_laneway_house` / `variant_0` | open findings | `clay-vancouver-laneway-house-clay-v002.glb` |
| 51 | building | `tools/clay_vancouver_special` | `vancouver_special` / `variant_0` | open findings | `clay-vancouver-special-clay-v001.glb` |
| 52 | building | `tools/clay_vaulted_lecture_hall` | `campus_lecture_hall_complex` / `variant_0` | open findings | `clay-vaulted-lecture-hall-clay-v003.glb` |
| 53 | building | `tools/clay_zinc_dome_corner_block` | `parisian_corner_with_dome` / `variant_0` | open findings | `clay-zinc-dome-corner-block-clay-v004.glb` |
| 54 | park/plaza | `tools/clay_halifax_public_gardens` | `halifax_public_gardens` / `variant_0` | passed | `clay-halifax-public-gardens-clay-v005.glb` |
| 55 | park/plaza | `tools/clay_ice_rink_market_square` | `outdoor_ice_rink` / `variant_0` | passed | `clay-ice-rink-market-square-clay-v007.glb` |
| 56 | park/plaza | `tools/clay_princes_island_park` | `calgary_princes_island` / `variant_0` | passed | `clay-princes-island-park-clay-v005.glb` |
| 57 | park/plaza | `tools/clay_stepped_terraced_plaza` | `stepped_terraced_plaza` / `variant_0` | passed | `clay-stepped-terraced-plaza-clay-v005.glb` |
| 58 | park/plaza | `tools/clay_market_square` | `market_square` / `variant_0` | open findings | `clay-market-square-clay-v004.glb` |
| 59 | street/path | `tools/clay_barcelona_passatge` | `barcelona_passatge` / `variant_0` | passed | `clay-barcelona-passatge-clay-v006.glb` |
| 60 | street/path | `tools/clay_brick_arch_viaduct` | `rail_transit_viaduct` / `variant_0` | passed | `clay-brick-arch-viaduct-clay-v003.glb` |
| 61 | street/path | `tools/clay_cable_stayed_cycle_ring` | `dedicated_cycle_bridge` / `variant_1` | passed | `clay-cable-stayed-cycle-ring-clay-v003.glb` |
| 62 | street/path | `tools/clay_calgary_riverwalk` | `bow_river_pathway` / `variant_0` | passed | `clay-calgary-riverwalk-clay-v003.glb` |
| 63 | street/path | `tools/clay_inglewood_main_street` | `inglewood_main_street` / `variant_0` | passed | `clay-inglewood-main-street-clay-v004.glb` |
| 64 | street/path | `tools/clay_montreal_plateau_rue` | `montreal_plateau_residential_rue` / `variant_0` | passed | `clay-montreal-plateau-rue-clay-v003.glb` |
| 65 | street/path | `tools/clay_rail_through_truss` | `rail_transit_viaduct` / `variant_2` | passed | `clay-rail-through-truss-clay-v005.glb` |
| 66 | street/path | `tools/clay_road_diet_complete_street` | `road_diet_complete_street` / `variant_0` | passed | `clay-road-diet-complete-street-clay-v003.glb` |
| 67 | street/path | `tools/clay_steel_truss_road_bridge` | `urban_vehicular_bridge` / `variant_1` | passed | `clay-steel-truss-road-bridge-clay-v002.glb` |
| 68 | street/path | `tools/clay_stone_arch_road_bridge` | `urban_vehicular_bridge` / `variant_0` | passed | `clay-stone-arch-road-bridge-clay-v003.glb` |
| 69 | street/path | `tools/clay_swooping_cycle_flyover` | `dedicated_cycle_bridge` / `variant_0` | passed | `clay-swooping-cycle-flyover-clay-v003.glb` |
| 70 | street/path | `tools/clay_weathering_steel_footbridge` | `urban_pedestrian_footbridge` / `variant_0` | passed | `clay-weathering-steel-footbridge-clay-v003.glb` |
| 71 | street/path | `tools/clay_planted_green_bridge` | `landscape_park_pedestrian_bridge` / `variant_2` | open findings | `clay-planted-green-bridge-clay-v002.glb` |
| 72 | street/path | `tools/clay_tied_arch_shared_bridge` | `shared_cycle_pedestrian_bridge` / `variant_1` | open findings | `clay-tied-arch-shared-bridge-clay-v003.glb` |
| 73 | street/path | `tools/clay_timber_covered_footbridge` | `urban_pedestrian_footbridge` / `variant_2` | open findings | `clay-timber-covered-footbridge-clay-v002.glb` |
| 74 | street/path | `tools/clay_toronto_streetcar_street` | `toronto_streetcar_street` / `variant_0` | open findings | `clay-toronto-streetcar-street-clay-v002.glb` |
