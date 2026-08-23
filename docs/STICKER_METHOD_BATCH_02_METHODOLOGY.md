# Sticker Method Batch 02 — proposed methodology

Status: **proposal, not yet approved.** Written 2026-08-23 against the state of
`cityprompt/main` at `274d9b7c`.

This document proposes how the next trial batch of high-quality 3D building
families should be produced. It is grounded in what Sticker Method Batch 01
actually delivered, measured from the repository rather than from memory.

Read alongside:

- [`HIGH_QUALITY_3D_BUILDING_MEMORY.md`](HIGH_QUALITY_3D_BUILDING_MEMORY.md) —
  the human runbook for construction quality. Batch 02 does not change it.
- [`../tools/archetype_compiler/high_quality_building_memory.json`](../tools/archetype_compiler/high_quality_building_memory.json)
  — the executable gates.
- [`../tools/archetype_compiler/sticker_method_batch_01.json`](../tools/archetype_compiler/sticker_method_batch_01.json)
  — the Batch 01 policy and per-building approvals.
- [`RUNTIME_ASSETS.md`](RUNTIME_ASSETS.md) — the delivery contract this proposal
  leans on heavily.

---

## 1. What Batch 01 delivered

Ten families, every one approved with an unrounded independent architect mean
strictly above 95 and zero hard stops, at a per-building push checkpoint. The
evidence discipline was excellent and is **not** what this proposal changes:

- exact reference images pinned by SHA-256 (`reference_sha256`);
- generator sources pinned by SHA-256 (`source_sha256`);
- per-tier `geometry_sha256`;
- a final surface audit — the collegiate corner block checked 17,306 faces with
  zero failures;
- nine locked-camera renders per tier;
- four comparison sheets per family.

That package makes a family reproducible and reviewable months later. Keep all
of it.

## 2. Three findings that shape Batch 02

### 2.1 Seven of ten approved families never reached the application

`seed/model-library/objects/lego/651daf60-.../` contains only three of the ten:
`old-montreal-textile-v98-native-tiers`, `civic-modernism-rec-centre-v98-canonical`
and `market-historic-iron-glass-v98-canonical`. Only the latter two appear in
`frontend/src/data/runtimeAssetManifest.json`.

The other seven — daylight sawtooth factory, Halifax waterfront warehouse,
administrative faculty office, Peranakan shophouse row, industrial tilt-up
concrete, collegiate brick corner block, brutalist heroic landmark — exist as
review folders and as build output under `build/`, which is gitignored
(`.gitignore:16`). They are approved and unplaceable.

This is the single largest problem to fix. Batch 01's definition of done ended
at the review folder; the application's definition of done starts at the runtime
manifest, and nothing joined the two.

### 2.2 The texture budget was not uniformly measured, let alone enforced

Reading `machine-evidence.json` across all ten families:

| Family | records `texture_budget` | records `material_consolidation` | canonical triangles |
| --- | --- | --- | --- |
| administrative-faculty-office | no | no | 38,932 |
| brutalist-heroic | no | yes | 7,756 |
| civic-modernism-rec-centre | no | no | 11,624 |
| collegiate-brick-corner-block | yes | yes | 123,460 |
| daylight-sawtooth-factory | no | no | 33,736 |
| halifax-waterfront-warehouse | no | no | 45,064 |
| industrial-tilt-up-concrete | no | yes | 10,636 |
| market-historic-iron-glass | yes | yes | 47,072 |
| old-montreal-textile-mill | no | no | 33,080 |
| peranakan-shophouse-row | no | yes | 59,694 |

Two families out of ten record a texture-budget result at all. Where numbers do
exist they are over: the market hall shipped at 8.1 MB and 1,247 materials
against an 8 MB budget, logged in its README as "a nonvisual follow-up"; the
Peranakan row records `canonical_glb_texture_budget_warning_mb = 13.5` and
`extended_glb_texture_budget_warning_mb = 15.1`.

The budget matters because `backend/app/processing/glb_optimizer.py` targets
under 8 MB explicitly for the globe viewer, which loads up to 20 models at once.
A gate that can be passed by writing "follow-up" in a README is not a gate.

### 2.3 Per-family cost was roughly 1,700 lines of bespoke Python

| Kind | Files | Lines |
| --- | --- | --- |
| `build_*_v98.py` | 10 | 3,529 |
| `compile_*_v98.py` | 10 | 3,106 |
| `prepare_*_v98_assets.py` | 10 | 3,669 |
| `create_*_v98_review.py` | 9 | 1,513 |
| `tests/*v98*.py` | 27 | 4,995 |
| **Total** | **66** | **16,812** |

Plus 30 JSON contract/carrier files. The only meaningful shared spine is
`sticker_carrier_space.py`, at 183 lines. At this rate Batch 02 is another
~10,000 lines of one-off code before a single new building is visible in the
app.

### 2.4 A smaller note: review happened at two of three required scales

Batch 01's renders are all Blender-side — `archetype_match`,
`front_corner_oblique`, `rear_corner_oblique`, `facade_close`, `roof_audit`,
`aerial`. The construction memory itself requires three scales before approval:
"rectified facade, standalone street/aerial GLB, and a close orbit inside Google
Tiles." The third is missing from every Batch 01 review folder.

Relatedly, the machine assessor (`quality_memory.py`, memory version
`2026-08-02-clean-3d-no-prisms-runtime-v118`) and the V98 architect score are now
two parallel ledgers that do not reference each other. A family can be
`high_quality_ready` in one and unmentioned in the other.

---

## 3. What the catalogue actually needs next

Batch 02 should not be more landmarks. Mapping the 224 catalogue archetypes
against the 62 distinct seeded families, by `developmentType` — the field the
planner actually selects on (`plan_geometry/archetypes.py:177`):

| developmentType | archetypes | covered | notable gaps |
| --- | ---: | ---: | --- |
| residential_single_family | 26 | 2 | detached_contemporary_infill, mountain_alpine_chalet |
| residential_multifamily | 24 | 6 | scandinavian_urban_residential, senior_living_complex |
| institutional_education | 18 | 3 | civic_monumental_institution |
| **commercial_retail** | **17** | **0** | mediterranean_arcade_mixed_use, commercial_strip_mall |
| mixed_use | 15 | 8 | parisian_midrise_block |
| residential_duplex | 12 | 5 | brownstone_rowhouse_frontage, victorian_heritage_avenue |
| **transit_station** | **12** | **0** | transit_oriented_station_block, urban_light_rail_stop |
| **residential_highrise** | **7** | **0** | art_deco_setback_tower, vertical_forest_residential |
| **sports_arena** | **7** | **0** | modern_sports_arena |
| **institutional_health** | **6** | **0** | functionalist_healthcare, biophilic_healthcare |
| **industrial_warehouse** | **5** | **0** | romanesque_revival_warehouse |
| **commercial** | **5** | **0** | gastown_heritage_commercial |

(Coverage is a token-overlap match between archetype ids and seeded family
directory names, so it is approximate. It correctly reports the seven Batch 01
orphans as uncovered, which is the intended behaviour.)

The seeded library is heavy on heritage and industrial set pieces — four Toronto
Junction industrials, four machiya, four collegiate gothics, three mid-century
pavilions, a titanium art museum, a natatorium — and thin on the ordinary fabric
a generated plan is mostly made of. A plan that asks for a retail main street or
a transit stop today gets a fallback.

**Evidence availability is not the constraint for the fabric types, but it is
patchy.** 226 of 239 archetype image directories carry three or more images;
however many named archetypes have no image directory at all (for example
`commercial_strip_mall`, `montreal_duplex`, `toronto_bay_and_gable_house`,
`calgary_ctrain_station` all resolve to zero files). Batch 02 candidates must be
checked individually, and the six below all have 13–17 images on disk.

## 4. Proposed Batch 02 — six families

Five ordinary-fabric families that reuse representations Batch 01 already
proved, plus one deliberate capability slot.

| # | Archetype | devType | Images | Suggested size | Representation | Why |
| --- | --- | --- | ---: | --- | --- | --- |
| 1 | `mediterranean_arcade_mixed_use` | commercial_retail | 16 | 20×16 m, 1–6 f | `discrete_horizontal_lego` | Main-street retail; the largest zero-coverage category. **Pilot.** |
| 2 | `brownstone_rowhouse_frontage` | residential_duplex | 17 | 6×15 m, 2–4 f | `whole_attached_unit_lego` | Row/terrace repeat unit; reuses the proven Peranakan representation. |
| 3 | `detached_contemporary_infill` | residential_single_family | 16 | 10×12 m, 1–3 f | small `fixed_landmark` / whole unit | Cheapest family in the batch; single-family is the biggest raw gap (26/2). |
| 4 | `urban_light_rail_stop` | transit_station | 13 | 30×7 m, 1 f | `discrete_panel_lego` | Single storey, very cheap; transit is 12/0. |
| 5 | `transit_oriented_station_block` | transit_station | 17 | 35×25 m, 4–12 f | `discrete_horizontal_lego` with podium | High planner value; podium-plus-residential is a recurring shape. |
| 6 | `art_deco_setback_tower` | residential_highrise | 17 | 25×20 m, 8–55 f | **new** `vertical_repeat_lego` | The capability slot — see below. |

### The capability slot, and how to drop it safely

Every Batch 01 contract sets `vertical_scaling_allowed: false`. There is
currently no family that can answer a tall polygon, and `residential_highrise`
is 7 archetypes with zero coverage. Family 6 is where the fixed-signature /
repeat-middle contract gets extended to the vertical axis: fixed podium, fixed
setback crown, whole repeatable floor modules in between — repeated, never
stretched.

This is the riskiest item in the batch. It is placed last deliberately: if it
does not converge, drop it and ship five. The five fabric families do not depend
on it.

## 5. The proposed methodology

### Phase 0 — promote the seven orphans, before authoring anything new

Rebuild each of the seven from its locked contract, verify the rebuilt
`geometry_sha256` still matches the recorded machine evidence, land the GLBs in
`seed/model-library`, regenerate the runtime manifest, and run
`npm run check:runtime-assets`.

No new geometry, no image generation, no new review. This recovers work already
paid for — and, more importantly, it exercises the promotion path end to end
*before* Batch 02 depends on it. If Phase 0 is painful, that pain is the Batch 02
blocker and we have found it for free.

**Contingency:** if a rebuilt geometry SHA does not match, the compiler has moved
under that family. The honest response is to re-review it, not to re-approve it
on the old score. Treat a SHA mismatch as a finding to report, not an
inconvenience to route around.

### Phase 1 — extract the spine, proven against two existing families

Refactor the pipeline so that contract schema, carrier packages, surface audit,
validation and review-sheet generation are one shared code path, and each family
is a spec JSON plus a small geometry module.

Prove it by porting two Batch 01 families first — `collegiate-brick-corner-block`
(discrete horizontal LEGO) and `market-historic-iron-glass` (fixed landmark).

**Acceptance is exact:** both must reproduce their recorded `geometry_sha256`
and their surface-audit face counts. If they do not, the refactor is wrong, not
the memory.

Only after that do new families get authored on the runner.

### Phase 2 — one pilot family, all the way to a placed building

`mediterranean_arcade_mixed_use`, in this order:

1. `--grammar-only` first — zero API cost, exposes the exact variant, dimension
   and signature contract. This is the existing cheap-to-expensive rule and it
   stays.
2. Full source generation, assembly, validation and review sheets.
3. Promotion into the seed library and runtime manifest.
4. **Placement in a real City Prompt plan, orbited in Google Tiles**, with
   screenshots at street, oblique and aerial in the review folder.

Show that before authorizing the remaining five. This follows the repository's
standing pilot → confirm → scale rule; the only change is that the pilot now
has to reach the application, not the review folder.

### Phase 3 — the remaining five, push checkpoint per family

Unchanged from Batch 01. Per-building push discipline is why that batch had no
rollbacks.

## 6. Definition of done — what changes

Everything Batch 01 required is retained. Four gates are added, all pass/fail
**before** approval rather than as follow-ups:

| Gate | Batch 01 | Batch 02 |
| --- | --- | --- |
| Architect mean > 95 unrounded, 0 hard stops | required | unchanged |
| Reference / source / geometry SHA locks | required | unchanged |
| Final surface audit | required | unchanged |
| Locked-camera Blender renders | required | unchanged |
| **Texture budget ≤ 8 MB + declared triangle ceiling** | recorded for 2 of 10 | **measured for every family, enforced at build time** |
| **In `seed/model-library` and `runtimeAssetManifest.json`** | 3 of 10 / 2 of 10 | **required; approval and shipping are one event** |
| **Live Google Tiles placement screenshots** | absent | **required, three scales, in the review folder** |
| **`quality_memory.py` assessment recorded beside the architect score** | separate ledger | **required; memory version bumped with the batch** |

On the budget gate specifically: the tooling already exists. `package_ktx2.py`
does UASTC KTX2 with mipmaps and zstd, and `glb_optimizer.py` already targets
under 8 MB. The market hall's 1,247 materials is a deduplication problem, not a
texture-resolution problem — material and texture dedup should run before any
resolution is sacrificed, so budget compliance costs identity last rather than
first.

## 7. Open judgement calls

Two things in this proposal are genuinely the user's call, not mine:

**Six instead of ten** trades catalogue breadth for pipeline durability. If the
priority is a demo with visible variety, ten is defensible — but then Phase 1
should be dropped explicitly and named as debt for Batch 03, not skipped
quietly.

**Phase 0 assumes the orphans still rebuild cleanly.** If several geometry SHAs
drift, Phase 0 grows from a promotion task into a re-review task, and the batch
timeline moves. Running the Phase 0 diagnostic on a single family first is the
cheap way to find out.

---

## Appendix A — external tooling and prior art

A scan of publicly available projects and agent skills doing something adjacent
to this pipeline, and an assessment of whether any is worth adopting.

### Directly relevant, worth a look

- **[glTF-Transform](https://github.com/donmccurdy/glTF-Transform)** (MIT) — the
  strongest concrete recommendation here. Its `dedup` pass removes duplicate
  Accessor, Mesh, Texture and Material properties; `prune` removes unused data.
  This is exactly the market hall's 1,247-material problem, and it is a mature,
  scriptable CLI. Worth trialling in the Batch 02 budget gate before writing
  bespoke consolidation logic.
- **[BuildingGeneratorThreeJS](https://github.com/achrefelouafi/BuildingGeneratorThreeJS)**
  (MIT) — a procedural Hong Kong building generator for Three.js, ported from
  Blender geometry nodes. Its packaging choice is the interesting part: ~190
  parts (walls, windows, AC units, storefronts, roof props) ship as **one
  instanced `kit.glb` plus a `kit_manifest.json`**, rather than per-part GLBs.
  Worth comparing against our per-assembly GLB layout for families that share
  many small repeated pieces.
- **[ProceduralToolkit](https://github.com/Syomus/ProceduralToolkit)** (Unity,
  MIT) — contains `ProceduralFacadePlanner`, `ProceduralFacadeConstructor` and a
  library of facade panel elements. The planner/constructor split is a cleaner
  separation than our current one and is a useful reference for the Phase 1
  spine, even though the runtime is wrong for us.

### Relevant background, not adoptable as-is

- **Esri CityEngine CGA shape grammar** — proprietary, but the canonical prior
  art for our fixed-versus-repeatable decomposition. Its component split
  producing distinct front / side / roof shapes, and the `repeat` operator on
  upper floors, is essentially the contract our families encode by hand.
  CityEngine 2025.1 added a Python 3 API. Worth reading the facade-modelling
  tutorials before finalising the Phase 1 spec schema.
- **[Random3Dcity](https://github.com/tudelft3d/Random3Dcity)** (TU Delft) —
  procedural CityGML building generation. Useful for LOD taxonomy vocabulary,
  not for asset quality at our target.

### Image-to-3D — informative, but not a replacement

Single-image and sketch-conditioned 3D generation matured considerably through
2025–2026: Trellis 2 (4B DiT, 1536³, 4K PBR), Hunyuan 3D 3.5 (sub-60s, up to 8K
PBR), Meshy v6, Tripo, Hyper3D Rodin. Recent work explicitly conditions TRELLIS
on facade images to recover textured building meshes.

Assessment: these remain the wrong tool for our acceptance bar. They produce a
single sculpture, not a fixed-signature / repeatable-middle family that survives
resizing — the thing the whole Sticker Method exists to guarantee. The repository
has already been down this road: `convert_meshy_concert_reference.py` and
`convert_meshy_markthal_reference.py` treat Meshy output as *reference*, and
`glb_optimizer.py`'s docstring records that Meshy/Tripo GLBs arrive at 70–80 MB.
That is the right role for them and I would not expand it.

On the material side, **MatE** and **Material Palette** (CVPR 2024) are the
closest research to our rectification-and-derivation stage — MatE does coarse
rectification from an estimated depth map, then a dual-branch diffusion model
producing albedo, normal, roughness and height. If our facade derivation ever
needs rebuilding, that literature is the place to start.

### Agent skills and MCP servers

- **[blender-mcp](https://github.com/ahujasid/blender-mcp)** and its forks —
  prompt-driven Blender control over MCP. Genuinely useful for exploratory
  modelling and one-off inspection. It is the opposite of what our batch
  pipeline needs, though: our value is in deterministic, SHA-pinned, replayable
  builds, and a conversational modelling loop is not reproducible. Best use is
  interactive diagnosis of a family that failed review, not authoring.
- **[skills-for-architects](https://github.com/AlpacaLabsLLC/skills-for-architects)**
  (MIT) — Claude Code skills for architecture practice: zoning analysis, site
  planning, due diligence, programming, specifications, FF&E. Checked
  specifically for overlap: it contains **no** 3D generation, massing, facade or
  asset-pipeline skills. No overlap with this work.
- **[DDC_Skills_for_AI_Agents_in_Construction](https://github.com/datadrivenconstruction/DDC_Skills_for_AI_Agents_in_Construction)**
  — 221 construction skills (BIM analysis, RVT/IFC/DWG conversion, cost,
  scheduling). Downstream of us, not adjacent.

**Bottom line:** nobody publicly is doing the specific thing this repository is
doing — reference-locked, evidence-audited, resizable architectural families with
a per-face surface audit and a formal approval score. The ecosystem has better
*components* than we do in exactly one place worth acting on now: glTF-Transform
for the material and texture budget gate. The rest is worth reading, not
adopting.
