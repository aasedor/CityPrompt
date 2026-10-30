# Building-only runtime review — 29 October 2026

The user requested that building placements contain buildings without embedded roads.
18 exact deployed-catalogue sources now use explicit source-ownership extraction in an
owned runtime clone. Original GLBs, library entries and saved source identities are unchanged.
This is a runtime presentation patch, not a new RLASM keeper approval.

Target: deployment-version `62e31ad621238c6ce1da62934710128831df3b5e` plus
branch `codex/building-only-20261029`. The controlled browser frontend is
`http://127.0.0.1:5175`; its backend is the unchanged deployment backend at port 8002.
It has not been pushed or deployed live. The earlier local app on 5174 was not modified.

Evidence folder: https://drive.google.com/drive/folders/188USn4T7_1w7QVOzmWQnBYDGdespB45e
Local original dossier: `D:/CityPrompt-review-artifacts/building-only-20261029`.
Policy and exact SHA/geometry signatures: `frontend/src/features/legoAssembly/buildingOnlyContracts.json`.

## Shared method and actual browser scope

Review follows `docs/ARCHETYPE_RUNTIME_INTEGRATION.md` and the fields/gates in
`docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md`. Shared unchanged or unrun gates are recorded
below rather than inheriting acceptance from another variant.

- Reviewer: Codex agent simulation, 29 October 2026; Edge, mouse/keyboard, 1681x1280 viewport.
- Disposable project: `2715f44e-9ca9-4fc7-976f-350302496ccc`, Deployment 74 — Student Archetype Trials.
- One QA building zone `349a7e26-7733-4010-9f17-78bf83daead1` on a prepared level vacant site.
  CBE was initially placed through the catalogue card. The other 17 were selected through
  Building type / Apply building, replacing this same zone. They were not 18 independent placements.
- Saved QA plot: 150x150m, rotation 15 degrees, native model scale 1. Legacy plot reserves remain
  unchanged; this patch does not claim compact placement or collision-envelope reduction.
- All 18 choices rendered and saved. Read-only zone history independently contains all 18 exact
  candidate revisions. Full page reload was checked for hotel and Toronto only.
- Exact free PNG source capture content was exported for CBE (wide/close) and hotel (after reload).
  The preview's provided PNG data URL was saved. The browser Download action itself was not tested.
- Each original GLB SHA, source/retained total and per-mesh triangle counts, extracted bbox and
  original buffer/bbox immutability were verified using hydrated actual-asset tests.
- Mesh material labels mix architecture with context. Explicit source prisms/component ownership
  and original triangle ordinal ranges retain complete architecture; no triangle cutting or GLB edits.
- Preserve building steps, plinths, podiums, enclosed courts, roof planting, station structure and
  Plus15 bridge. Remove scene roads, perimeter paving/lawns, scene vegetation/furniture and neighbours.
- Native review, compiled LEGO, generic model layer, composer, placement previews and model viewer
  all use the same extracted scene. Bounds and ground footprint derive from retained geometry.
- Bounded browser console read contained 12 runtime.onMessage promise errors (extension-style
  messages); no extraction/Three.js application exceptions appeared in that read. This is not a
  clean-console claim or a complete network audit.

## Shared verification and remaining cases

63 tests passed in 7 files, including 19 hydrated asset tests (18 exact candidates and detailed CBE).
Command from frontend, with CITYPROMPT_BUILDING_ONLY_MODEL_DIR pointing to the hydrated models:

```text
npm run test -- --run src/features/legoAssembly/buildingOnlyScene.test.ts src/features/legoAssembly/buildingOnlyScene.asset.test.ts src/features/legoAssembly/nativeClayPlacement.test.ts src/features/legoAssembly/LegoAssemblyPreview.test.tsx src/components/viewer/globe/reviewBuildingGround.test.ts src/features/pickPlace/assetRegistry.test.ts src/features/pickPlace/CanonicalCatalogueCard.test.tsx
npm run type-check
```

Both commands exited 0. Source geometry analysis, actual component output, original source hashes,
UI snapshots and saved history are separate evidence. Independent code review found no P0/P1
in the scoped extraction; the initially missed generic model layer was subsequently corrected.
Runtime matches the exact immutable candidate URL/revision; hashes are checked offline, not at runtime.

Not tested in this round: natural/sloped ground, mixed streets/parks, minimum/maximum plot fit,
new placements for each individual picker card, walk collisions and entrance routes, drag move,
Undo/Redo/delete, save failure recovery, editing while tiles refine, offline fresh installation,
paid AI renders/videos, actual browser Download, or the entire 74-model catalogue.
These remain NOT TESTED, never implied passing from the level-site screenshots.
Street S1-S4 and park P1-P4 gates are N/A to this building-only change.

## Exact candidate results


### Calgary CBE Brutalist Hq

- Exact archetype / semantic variant: `calgary_cbe_brutalist_hq` / `calgary_cbe_original`.
- Exact source revision: `clay-calgary-cbe-brutalist-hq-clay-v004`; SHA-256 `a0836dc6e11577f734452f01e087fe1ee3c08c57ccfe63addd95f0428eb91433`.
- Native retained size X/Y(height)/Z: [43.3, 28.37, 40.6]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 35,078 → 28,938.
- Evidence: `browser/cbe-v004-building-only-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; PASS for provided original PNG content; Download action NOT TESTED; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### CMU Dock Warehouse

- Exact archetype / semantic variant: `mid_century_distribution_warehouse` / `cmu_dock_utilitarian`.
- Exact source revision: `clay-cmu-dock-warehouse-clay-v006`; SHA-256 `9551998b85a4dd9d1fa40081d53b441d6201344335a83ed98053eae8e9cb2f6e`.
- Native retained size X/Y(height)/Z: [30.19, 9.475, 28.425]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 20,340 → 19,744.
- Evidence: `browser/clay-cmu-dock-warehouse-clay-v006-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### Gastown Heritage Commercial

- Exact archetype / semantic variant: `gastown_heritage_commercial` / `gastown_italianate`.
- Exact source revision: `clay-gastown-heritage-commercial-clay-v003`; SHA-256 `657f66a2df048e606aebe626a76a77e66f93ec1992c2fb1f207833336fd67f14`.
- Native retained size X/Y(height)/Z: [27.9, 20.26, 25.5]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 37,878 → 27,490.
- Evidence: `browser/clay-gastown-heritage-commercial-clay-v003-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### Halifax Georgian Colonial

- Exact archetype / semantic variant: `halifax_georgian_colonial` / `georgian_clapboard_original`.
- Exact source revision: `clay-halifax-georgian-colonial-clay-v003`; SHA-256 `0359e7171c1b642ab82cb2b73451834ed90227b70f61a605efa5e274b033d7f3`.
- Native retained size X/Y(height)/Z: [22.286, 15.82, 20.242]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 26,574 → 17,940.
- Evidence: `browser/clay-halifax-georgian-colonial-clay-v003-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### Halifax Waterfront Warehouse

- Exact archetype / semantic variant: `halifax_waterfront_warehouse` / `warehouse_privateers_wharf`.
- Exact source revision: `clay-halifax-waterfront-warehouse-clay-v006`; SHA-256 `de39e474c1e41add78aad6bc5f54d162fe81be3c71258ca7fba9de00b79660e3`.
- Native retained size X/Y(height)/Z: [26.84, 13.3, 19.4]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 16,521 → 15,145.
- Evidence: `browser/clay-halifax-waterfront-warehouse-clay-v006-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### LED Grow Block

- Exact archetype / semantic variant: `vertical_farm_indoor_agriculture` / `dark_panel_led_grow_block`.
- Exact source revision: `clay-led-grow-block-clay-v007`; SHA-256 `f7ee7d1ee6a39c6ac8b8283279400b7810b741888b15c9ccb8b336c8dd53cdf7`.
- Native retained size X/Y(height)/Z: [22.06, 32.66, 23.06]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 14,820 → 14,452.
- Evidence: `browser/clay-led-grow-block-clay-v007-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### Slab Balcony Tower

- Exact archetype / semantic variant: `west_end_mid_century_tower` / `midcentury_concrete_slab`.
- Exact source revision: `clay-slab-balcony-tower-clay-v007`; SHA-256 `042c09a9198f60fb0116ab93b6fd073309717a24a59925f31c2db1aed67d7d40`.
- Native retained size X/Y(height)/Z: [26.4, 47.0, 26.4]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 19,700 → 19,284.
- Evidence: `browser/clay-slab-balcony-tower-clay-v007-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### Toronto Bay And Gable

- Exact archetype / semantic variant: `toronto_bay_and_gable_house` / `toronto_bay_gable_yellow_brick`.
- Exact source revision: `clay-toronto-bay-and-gable-house-clay-v004`; SHA-256 `c11761d97f80e7462c88fb7d68b2d44eaaaa3010601fe23f32a4e624720186c8`.
- Native retained size X/Y(height)/Z: [8.4, 12.42, 16.24]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 17,326 → 14,190.
- Evidence: `browser/clay-toronto-bay-and-gable-house-clay-v004-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; PASS — full page reload and visible saved model. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### Arched Mill Mixed Use

- Exact archetype / semantic variant: `industrial_brick_mixed_use` / `industrial_brick_original_mill`.
- Exact source revision: `clay-arched-mill-mixed-use-clay-v005`; SHA-256 `218c0f8d8a84c34169af41490f8d0284e0bf2ac48dfe9a423b0985533c39ffdc`.
- Native retained size X/Y(height)/Z: [22.76, 25.7, 22.68]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 14,088 → 13,572.
- Evidence: `browser/arched-mill-v005-building-only-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### Brick Podium Condo Tower

- Exact archetype / semantic variant: `condo_podium_tower` / `brick_podium_glass_tower`.
- Exact source revision: `clay-brick-podium-condo-tower-clay-v006`; SHA-256 `1ce717fb6f9246312cb359b4808e726088447f12d2c571954cb33a6a91dd0869`.
- Native retained size X/Y(height)/Z: [44.9, 50.1, 33.24]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 19,194 → 18,530.
- Evidence: `browser/clay-brick-podium-condo-tower-clay-v006-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### Campus Shed Office

- Exact archetype / semantic variant: `corporate_office_campus_headquarters` / `industrial_warehouse_campus_hq`.
- Exact source revision: `clay-campus-shed-office-clay-v009`; SHA-256 `3da93f5933a04669806e0192d9c9871af8bfbd5699ce7e15bba7cc8639d01a95`.
- Native retained size X/Y(height)/Z: [43.955, 11.02, 34.14]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 20,692 → 19,408.
- Evidence: `browser/clay-campus-shed-office-clay-v009-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### Courtyard Primary School

- Exact archetype / semantic variant: `ecole_republicaine` / `ecole-republicaine-art-deco`.
- Exact source revision: `clay-courtyard-primary-school-clay-v009`; SHA-256 `8ab45251a971c91aeb217447f2f96fef8e98bdc2e8d2ecefe328d206175a3bd7`.
- Native retained size X/Y(height)/Z: [40.4, 12.979, 46.4]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 18,568 → 18,224.
- Evidence: `browser/clay-courtyard-primary-school-clay-v009-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### Garden Court Senior Residence

- Exact archetype / semantic variant: `senior_living_complex` / `senior_garden_courtyard`.
- Exact source revision: `clay-garden-court-senior-residence-clay-v006`; SHA-256 `17e50488c4753c0c91de4a88724d31f335757464cf1cbc96ca48bf9e6e00f8df`.
- Native retained size X/Y(height)/Z: [74.5, 15.05, 65.0]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 77,642 → 74,750.
- Evidence: `browser/clay-garden-court-senior-residence-clay-v006-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### Scottish Baronial railway hotel

- Exact archetype / semantic variant: `chateauesque_grand_railway_hotel` / `scottish_baronial_granite_tower`.
- Exact source revision: `clay-baronial-railway-hotel-clay-v006`; SHA-256 `424b00606c40c0bb455bf00d0af51fd12d0506049b065863fdc7827b4e9ffbd9`.
- Native retained size X/Y(height)/Z: [61.6, 42.4, 56.743]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 83,012 → 76,696.
- Evidence: `browser/clay-baronial-railway-hotel-clay-v006-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; PASS — full page reload and visible saved model. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; PASS for provided original PNG content; Download action NOT TESTED; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### CTrain Elevated Station

- Exact archetype / semantic variant: `calgary_ctrain_station` / `ctrain_downtown_platform`.
- Exact source revision: `clay-ctrain-elevated-station-clay-v004`; SHA-256 `d51715e11ca257c68b18214c1a7a4c9f7815f60b7b810d0c7bd1be5c92f48962`.
- Native retained size X/Y(height)/Z: [76.4, 18.7, 96.0]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 20,602 → 19,758.
- Evidence: `browser/clay-ctrain-elevated-station-clay-v004-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### Energy Centre

- Exact archetype / semantic variant: `central_utilities_plant_energy_centre` / `transparent_plant_showcase_urban`.
- Exact source revision: `clay-energy-centre-clay-v010`; SHA-256 `1c4849fedf76e226f5b0dc545f61c7c3350debb4ff845c5010d5931224eb05c3`.
- Native retained size X/Y(height)/Z: [36.11, 23.805, 34.13]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 12,442 → 11,938.
- Evidence: `browser/clay-energy-centre-clay-v010-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.


Existing Energy Centre architectural P1 remains OPEN. This context removal does not resolve it.

### Old Montreal Limestone Commercial

- Exact archetype / semantic variant: `old_montreal_limestone_commercial` / `old_mtl_french_colonial`.
- Exact source revision: `clay-old-montreal-limestone-commercial-clay-v004`; SHA-256 `eee62a12874fc1248a17383fe5f6c98e41b01511a50e1e44533db25b538ad3a8`.
- Native retained size X/Y(height)/Z: [108.83, 42.5, 51.16]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 66,776 → 63,728.
- Evidence: `browser/clay-old-montreal-limestone-commercial-clay-v004-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

### Plus15 Glass Office Tower

- Exact archetype / semantic variant: `calgary_plus_15_connected_tower` / `plus15_contemporary_glass`.
- Exact source revision: `clay-plus15-glass-office-tower-clay-v006`; SHA-256 `1f12b3c94ed7405e43fde35450b31a7e5561b937fd854ff8a0c92bc65db35851`.
- Native retained size X/Y(height)/Z: [37.7, 82.66, 65.85]m. Axes/data remain original; centre/bounds use extracted scene.
- Source → retained triangles: 16,500 → 15,812.
- Evidence: `browser/clay-plus15-glass-office-tower-clay-v006-SCREENSHOT.png`, `browser/persisted-browser-history.json` and exact asset tests.

| Gate | Result and limit |
| --- | --- |
| C1 exact identity | PASS — SHA/count/bbox verified; same revision saved in browser history |
| C2 dimensions/transforms | PASS for native scale and saved 15° rotation; extrema NOT TESTED |
| C3 full ground support | NOT TESTED in full; level native appearance checked only |
| C4 freshness/late results | NOT TESTED; original buffers immutability PASS in tests |
| C5 pedestrian continuity | NOT TESTED; scene roads removed, no new entrance connection claim |
| C6 edit/save/reopen | Save PASS via UI and history; NOT TESTED — save/history confirmed; no full reload of this exact revision. Undo/Redo NOT TESTED |
| C7 failure/recovery | NOT TESTED |
| C8 views/capture | Aerial screenshot PASS for road removal; NOT TESTED — browser screenshot only; multi-side low views NOT TESTED |
| C9 student controls | PASS for exact Building type / Apply building; every main card NOT TESTED |
| B1 native placement | PASS for unit-size rendered replacement in QA zone; independent drop NOT TESTED |
| B2/B3/B4 entrance evidence/authoring/recovery | NOT TESTED; preserved source steps do not establish access |
| B5 foundation/stair design | NOT TESTED; original selected surfaces preserved by geometry tests |
| S1-S4; P1-P4 | N/A — this candidate is a building |

Runtime decision: scoped level-site building-only visual checkpoint passed. Asset keeper,
terrain/access acceptance, fresh-install verification and publication decisions remain separate.

## Held candidate — Mews Coach House v006

`london_mews_house` / `variant_0` candidate `clay-mews-coach-house-clay-v006` remains
unmodified. Its source describes the x<0 neighbour and x>=0 selected house, but 50 original
WALL and 24 FLOOR triangles span the boundary. Removing existing components/faces cannot
retain a complete isolated house. Source clipping/rebuild and new reviewed GLB would be needed;
the user required original GLBs unchanged in the 74-model integration. All building-only gates
for this model are FAIL/HOLD or NOT TESTED, not covered by the 18 passes. Catalogue copy now
states that the attached context remains. Evidence: `complex-b/clay-mews-coach-house-clay-v006-hold-proof.json`.

## Handoff decision

Ready as a local, tested runtime patch for 18 exact variants. Mews remains a known unmet
building-only requirement. Legacy reserved plot dimensions remain conservative. No paid jobs,
source GLB changes, catalogue publication, pushes or live deployment were performed.
