# Codex prompt: bring the reviewed clay models into City Prompt

Copy everything below the line into Codex as its first message. It asks Codex to integrate the
architectural-clay models that passed independent review on branch `claude/ten-new-buildings` into the
City Prompt app, using the repository's own catalogue-promotion workflow and runtime-integration checks.
It works in phases, pilots one model before scaling, and stops for the user's approval before anything
is published. Background on the models is in the wave reports in `docs/showcase/` and in each family's
`README.md`, `VERSIONS.md` and `evidence/` folder.

---

I want the 3D architectural-clay models that passed independent review on branch
`claude/ten-new-buildings` to become usable in City Prompt: placeable from the picker, sitting correctly
on the ground, and surviving save, reload and capture. Read this whole message, then `CLAUDE.md`, before
starting.

## Repository and branches

- Repository https://github.com/aasedor/CityPrompt. `origin/main` is the integration branch.
- The models live on `claude/ten-new-buildings`. That branch is not based on current `main` (each side has
  hundreds of commits the other lacks), so **do not merge it**. Start each piece of work on a fresh
  `codex/<name>` branch from `origin/main`, and bring over only the files you need for one model with
  `git checkout origin/claude/ten-new-buildings -- <paths>`.
- Each model is one family folder `tools/clay_<family>/`:
  - `candidates/*.glb`: the one candidate model, an ordinary git blob under 4 MiB (not Git LFS);
  - `sources.json`: the locked catalogue reference images (front, oblique, top) with SHA-256 hashes;
  - `evidence/<version>/`: renders, phone boards, `build-report.json` and `independent-review.md`;
  - `README.md` (state line, cameras, open findings) and `VERSIONS.md` (every version and its review).
- The GLBs are glTF 2.0, 1 unit = 1 m, built at grade with flat `CLAY_<ROLE>` PBR materials; glass uses
  `KHR_materials_transmission`. Measure bounds from the transformed scene, not accessor min/max. The four
  parks and the laneway house made with the shared planting kit (`tools/clay_planting_kit_showcase`) store
  each plant once and place it as glTF node instances, so the scene graph has many nodes sharing meshes;
  keep that sharing when loading.

## What is ready (33 models, all PASS_ZERO_P0_P1)

Only these 33 passed an independent RLASM v6.1 review with zero P0 and zero P1 findings. Each family's
README states the exact candidate, and its `evidence/<version>/independent-review.md` is the review.
Re-check the README state line before you start: if a family has moved on, use what the README says.

### Buildings (19)

| model | family | candidate | GLB bytes | catalogue archetype / variant |
|---|---|---|---|---|
| Arched brick mill, mixed use | `tools/clay_arched_mill_mixed_use` | v005 | 744,024 | `industrial_brick_mixed_use` / `industrial_brick_original_mill` |
| Brick podium condo tower | `tools/clay_brick_podium_condo_tower` | v006 | 1,024,756 | `condo_podium_tower` / `brick_podium_glass_tower` |
| CTrain elevated station | `tools/clay_ctrain_elevated_station` | v004 | 1,094,572 | `calgary_ctrain_station` / `ctrain_downtown_platform` |
| Calgary Board of Education HQ | `tools/clay_calgary_cbe_brutalist_hq` | v004 | 1,717,448 | `calgary_cbe_brutalist_hq` / `calgary_cbe_brutalist_hq_v0` |
| Calgary sandstone heritage block | `tools/clay_calgary_sandstone_heritage` | v006 | 4,190,248 | `calgary_sandstone_heritage` / `sandstone_romanesque_revival` |
| Campus shed office HQ | `tools/clay_campus_shed_office` | v009 | 1,111,200 | `corporate_office_campus_headquarters` / `industrial_warehouse_campus_hq` |
| Gastown heritage commercial block | `tools/clay_gastown_heritage_commercial` | v003 | 2,083,784 | `gastown_heritage_commercial` / `gastown_heritage_commercial_v0` |
| Courtyard primary school | `tools/clay_courtyard_primary_school` | v009 | 1,009,176 | `ecole_republicaine` / `ecole-republicaine-art-deco` |
| Energy centre | `tools/clay_energy_centre` | v010 | 653,220 | `central_utilities_plant_energy_centre` / `transparent_plant_showcase_urban` |
| Garden-court senior residence | `tools/clay_garden_court_senior_residence` | v006 | 4,030,900 | `senior_living_complex` / `senior_garden_courtyard` |
| Halifax waterfront stone warehouse | `tools/clay_halifax_waterfront_warehouse` | v006 | 845,444 | `halifax_waterfront_warehouse` / `warehouse_privateers_wharf` |
| LED grow block (vertical farm) | `tools/clay_led_grow_block` | v007 | 790,632 | `vertical_farm_indoor_agriculture` / `dark_panel_led_grow_block` |
| London mews coach house | `tools/clay_mews_coach_house` | v006 | 2,708,724 | `london_mews_house` / `london-mews-house-original-stable` |
| Mid-century dock warehouse | `tools/clay_cmu_dock_warehouse` | v006 | 1,115,380 | `mid_century_distribution_warehouse` / `cmu_dock_utilitarian` |
| Old Montreal limestone commercial | `tools/clay_old_montreal_limestone_commercial` | v004 | 3,423,736 | `old_montreal_limestone_commercial` / `old_montreal_limestone_commercial_v0` |
| Plus 15 glass office tower | `tools/clay_plus15_glass_office_tower` | v006 | 910,328 | `calgary_plus_15_connected_tower` / `plus15_contemporary_glass` |
| Scottish Baronial railway hotel | `tools/clay_baronial_railway_hotel` | v006 | 4,172,400 | `chateauesque_grand_railway_hotel` / `scottish_baronial_granite_tower` |
| Slab balcony tower | `tools/clay_slab_balcony_tower` | v007 | 1,020,940 | `west_end_mid_century_tower` / `midcentury_concrete_slab` |
| Toronto bay-and-gable house | `tools/clay_toronto_bay_and_gable` | v004 | 911,108 | `toronto_bay_and_gable_house` / `toronto_bay_and_gable_house_v0` |

### Parks and plazas (4)

| model | family | candidate | GLB bytes | catalogue archetype / variant |
|---|---|---|---|---|
| Halifax Public Gardens | `tools/clay_halifax_public_gardens` | v005 | 4,126,476 | `halifax_public_gardens` / `halifax_public_gardens_v0` |
| Outdoor ice rink in a market square | `tools/clay_ice_rink_market_square` | v007 | 3,989,984 | `outdoor_ice_rink` / `outdoor_ice_rink_v0` |
| Prince's Island Park | `tools/clay_princes_island_park` | v005 | 4,184,552 | `calgary_princes_island` / `calgary_princes_island_v0` |
| Stepped terraced plaza | `tools/clay_stepped_terraced_plaza` | v005 | 3,339,416 | `stepped_terraced_plaza` / `stepped_terraced_plaza_v0` |

### Streets, paths and bridges (10)

| model | family | candidate | GLB bytes | catalogue archetype / variant |
|---|---|---|---|---|
| Cable-stayed circular cycle bridge | `tools/clay_cable_stayed_cycle_ring` | v003 | 1,941,156 | `dedicated_cycle_bridge` / `dedicated_cycle_bridge_v1` |
| Calgary RiverWalk | `tools/clay_calgary_riverwalk` | v003 | 3,766,080 | `bow_river_pathway` / `bow_river_pathway_v0` |
| Heritage stone arch road bridge | `tools/clay_stone_arch_road_bridge` | v003 | 3,878,388 | `urban_vehicular_bridge` / `urban_vehicular_bridge_v0` |
| Inglewood main street | `tools/clay_inglewood_main_street` | v004 | 1,910,720 | `inglewood_main_street` / `inglewood_main_street_v0` |
| Riveted steel arch rail viaduct | `tools/clay_rail_through_truss` | v005 | 3,906,840 | `rail_transit_viaduct` / `rail_transit_viaduct_v2` |
| Riveted steel truss road bridge | `tools/clay_steel_truss_road_bridge` | v002 | 3,282,652 | `urban_vehicular_bridge` / `urban_vehicular_bridge_v1` |
| Road-diet complete street | `tools/clay_road_diet_complete_street` | v003 | 3,189,736 | `road_diet_complete_street` / `road_diet_complete_street_v0` |
| Swooping elevated cycle flyover | `tools/clay_swooping_cycle_flyover` | v003 | 3,850,284 | `dedicated_cycle_bridge` / `dedicated_cycle_bridge_v0` |
| Victorian brick arch rail viaduct | `tools/clay_brick_arch_viaduct` | v003 | 3,928,328 | `rail_transit_viaduct` / `rail_transit_viaduct_v0` |
| Weathering-steel truss footbridge | `tools/clay_weathering_steel_footbridge` | v003 | 1,442,444 | `urban_pedestrian_footbridge` / `urban_pedestrian_footbridge_v0` |

Variant ids ending in `_v0`, `_v1` or `_v2` are the family's own labels for "catalogue variant 0, 1, 2". Use
`sources.json` (the locked image paths under `frontend/public/archetypes/...`) to find the real catalogue
variant the model was built from, and bind to that variant.

**Not ready:** every other `tools/clay_*` family has open P0/P1 findings (see its README) and must not be
integrated. The rest of wave J (Halifax Georgian colonial, Vancouver laneway house, Halifax ferry terminal,
Montreal Plateau residential rue) is still being reviewed; treat a wave J family as ready only if its
README state line says PASS_ZERO_P0_P1 when you start.

## Rules (from `CLAUDE.md`; they override anything below)

- Never `json.dump` (parse-modify-dump) `buildingArchetypes.json`, `streetPathArchetypes.json` or
  `openSpaceArchetypes.json`; it corrupts `thumbnailUrl` paths. Edit catalogue JSON only by text-level
  insertion, and only if a step truly requires it. All 32 archetypes above already exist in main's
  catalogues, so you should not need to add any.
- Use only `frontend/public/archetypes/{buildings,openspaces,streets}` for images. Never read from or write to
  `parks_plazas`, `streets_pathways` or their hyphenated variants.
- Do not change, re-export, decimate or "fix" a delivered GLB or its review. If a model fails a runtime check,
  record the failure and leave the model alone; geometry fixes go back to the RLASM pipeline.
- Published GLBs go through Git LFS as the workflow requires (`git check-attr filter` must report `lfs`, and
  `git show :<path>` must show an LFS pointer).
- Test on localhost:5174 before every commit: cards load, placement works, no console errors.
- Push only to your own `codex/*` branches. Never force-push, never push to `main` directly, never bypass CI.
- Review, runtime acceptance, catalogue publication and keeper approval are separate checkpoints. Do not
  describe any model as keeper-approved. Do not invent or paraphrase approval: the promotion `approval`
  block needs the user's own words.
- Scope every commit to one model or one coherent support change. Never `git add .`.

## Phase 1: one building pilot

1. Read `docs/BUILDING_CATALOGUE_WORKFLOW.md`, `docs/ARCHETYPE_RUNTIME_INTEGRATION.md` and
   `docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md` in full, plus `tools/catalogue_promotion.py` and
   `tools/seed_model_library.py`.
2. Pilot with **Halifax waterfront stone warehouse** (`tools/clay_halifax_waterfront_warehouse`, v006, a
   fixed-native landmark under 1 MB).
3. Build its promotion package outside the repository, starting from
   `python -m tools.catalogue_promotion template <dir>/promotion.json`:
   - Identity from `sources.json`, with the real catalogue variant.
   - A permanent unique picker `id` and a `group_id` from `frontend/src/features/calgaryCatalogue/guide.ts`.
   - `fixed_native` placement, and a plot at least the native envelope plus 3 m.
   - The review JSON the workflow requires, written truthfully from the family's
     `evidence/<version>/independent-review.md`:
     - `candidate` and `model_sha256` (computed from the GLB bytes);
     - `reviewer`: "independent RLASM v6.1 reviewer (separate agent session)";
     - `architectural_clay_pass: true` and `holistic_review_performed: true`;
     - `unresolved_p0: 0` and `unresolved_p1: 0`;
     - `inspected_files` carrying the SHA-256 of the three locked references from `sources.json`.

     Keep the markdown review alongside it. Do this only for families whose review really says
     PASS_ZERO_P0_P1.
4. Run the trial exactly as the workflow says: dry run, then `--apply`, then a local-trial seed, install and
   `--verify` against a local database and storage.
5. Trial it like a student on empty land on localhost:5174:
   - card and exact variant;
   - ground contact from low and aerial cameras;
   - entrance approach;
   - rotation, save, reload and reopen;
   - close and partly out-of-frame capture;
   - console errors.

   Fill in the runtime review template for this variant, with failing or untested checks left open.
6. **Stop and report to me.** Send:
   - the branch;
   - the trial checklist with screenshots: aerial, eye level, and after reload;
   - the review-template record;
   - anything that failed;
   - the exact `model_sha256`.

   Do not run `prepare --apply` or open a PR until I reply with my approval in my own words for that model.

## Phase 2: the other buildings

After I approve the pilot and say to continue, repeat Phase 1 for the other 18 buildings, in batches of
about five. Use one branch and one PR per model (or per batch, if the workflow's `check` accepts it).
Detached houses (the Toronto bay-and-gable house, the London mews coach house) need their parent supported
in the backend's `DETACHED_ARCHETYPE_IDS` and tested for unscaled repetition before they can use
`repeat_native`. Until then, propose `fixed_native` or report the dependency instead of stretching a house.
Stop for my approval before each batch's `prepare --apply`.

## Phase 3: parks, plazas and streets (investigate first)

The promotion tool covers buildings. Parks and streets use other registries:
- `frontend/src/data/nativeParks.json`;
- `frontend/src/data/nativeStreetPilots.json` and `nativeStreetModuleBounds.json`;
- `backend/app/services/public_realm_lego.py`;
- the street family catalogue (`streetFamilyCatalog.ts`).

They must also pass the park checks (P1–P4) and street checks (S1–S4) in
`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`: metric sections, junction finishes, shared grade, park access and
terrain remeasurement.
1. Read those registries and the runtime document and write a short plan:
   - how a reviewed clay GLB becomes a native street or park pilot;
   - what has to be registered (section bands, junction finish, footprint, access gateways);
   - which of the 14 models can be fixed-native as delivered;
   - which need runtime support that does not exist yet.
2. Pilot one street (**road-diet complete street**) and one park (**stepped terraced plaza**) end to end on
   localhost:5174.
3. Stop and report, with the same evidence as Phase 1.

The bridges are street options whose decks need endpoint and grade checks; say which runtime pieces they
need before attempting them.

## How to check every model

- Run the repository's own checks for each change. The workflow's step 5 lists them:
  - `python -m pytest` on the catalogue-promotion tests;
  - `python -m tools.catalogue_promotion check`;
  - the pick-place vitest suites;
  - `npm run type-check`;
  - `npm run generate:runtime-assets` and `npm run check:runtime-assets`;
  - `git diff --check`.
- Look at your own screenshots, and say in plain words what you see. Do not report success from console
  output or HTTP 200s alone.
- Record the installed model hash from `--verify`; a matching file size is not proof.

## What to send me back after each phase

1. The branch name(s) and commits.
2. For each model:
   - the trial checklist;
   - screenshots;
   - the runtime-review record;
   - the exact `model_sha256`;
   - what passed, what failed and what is untested.
3. Anything that needs a decision from me (a placement mode, a missing runtime capability, a model that
   should go back for rework), with options.
