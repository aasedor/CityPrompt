# Plan Variety via Catalog Archetypes — Build Spec

**Date:** 2026-07-07
**Benchmark:** Calgary "West District" master plan render (density transect around a
naturalized central pond/greenway, curved collector streets + roundabout, mixed-use
core, townhouse rings with rear laneways, detached housing at the suburban edge).
**Goal:** Generated plans should place *different* buildings, parks, and streets
*strategically and logically*, drawn from the existing catalog — instead of the current
uniform grid of perimeter blocks + central courtyards.

---

## 1. Root cause (why every plan looks identical)

The pipeline has two layers, and **neither currently varies the built form**:

1. **LLM expert panel** (`backend/app/services/planning_agents/`) emits only *numbers and
   hints* from a fixed vocabulary (`schemas.py:19` `PARAMETER_VOCABULARY`): heights,
   coverage, ROW width, tree density, development type. `layout.strategy` exists
   (`schemas.py:53`) but maps to `_layout_strategy_preference` — a string the geometry
   engine **never reads** (a dead wire).

2. **Geometry engine** (`backend/app/services/plan_geometry/`) is 100% deterministic with
   exactly **one morphology**:
   - Streets → always an orthogonal grid (`street_graph.py:83` `generate_street_network`).
   - Buildings → always a perimeter ring around a courtyard (`parceling.py:96`
     `building_mass_for_block`).
   - The hollow ring center → always becomes a "courtyard" green zone (`generator.py:315`).
   - Parks → always whole blocks nearest the centroid (`generator.py:205`).

3. **The uniformity is entirely in the backend generator**, which stamps **ONE**
   `development_type`, **ONE** `development_aesthetic`, and **ONE** `row_width` on every
   zone:
   - `generator.py:145` — `development_type` / `development_aesthetic` read ONCE.
   - `generator.py:~232-334` — that same value baked onto EVERY building zone.
   - Scenarios (`community_rules.py:40`) differ by only 3 numbers (block spacing,
     open-space share, coverage); `building_depth_m`/`front_setback_m`/`parcel_width_m`
     are fixed constants for all of them.

## 2. Key enabler — the frontend resolver is ALREADY per-zone (no FE change needed)

`frontend/src/components/viewer/resolvePlanZoneArchetypes.ts` reads each zone's properties
*independently* and resolves it to a catalog archetype:

- **Buildings** — matches `development_type` (exact, then prefix), filters by
  `development_aesthetic` (`aestheticCategory`), then hard-filters to the archetype's
  `minFloors`/`maxFloors`. Winner via `stablePick` (prefers entries with variants). Writes
  `{prefix}_archetype_id` + `{prefix}_selected_variant_id` + `_plan_archetype_resolved`.
- **Streets** — matches on `width` band: `<10m` yield_street, `10-15m`
  narrow_residential_street, `15-22m` collector_road, `>=22m` main_street_complete.
- **Open space** — matches on `area`: `<1500 m²` urban_pocket_park, `>=1500 m²`
  neighborhood_park (civic/plaza types also exist via `spaceType`).

**Implication:** feeding the resolver varied, context-aware tags is enough to get building /
park / street *type* variety. The only reason it looks uniform today is the backend feeds
it one value everywhere.

## 3. The catalog already holds every West District element

The catalog is NOT the bottleneck — the geometry engine is. Confirmed real ids:

- **Buildings** — 26 `developmentType` families (`residential_single_family`,
  `residential_duplex`, `residential_multifamily`, `residential_highrise`, `mixed_use`,
  `commercial_retail`, `commercial_office`, `institutional_education`,
  `institutional_health`, `transit_hub`, …) and 50+ `aestheticCategory` families
  (`brownstone_rowhouse`, `parisian`, `eco_urban_green_architecture`,
  `scandinavian_nordic`, `biophilic_contemporary_institutional`, `contemporary_midrise`,
  `brutalism`, …). Each archetype carries `minWidth_m`/`maxWidth_m`/`minDepth_m`/
  `maxDepth_m`, `suggestedFloorHeight`, `scaleVariants` (lowrise/midrise/highrise/tower),
  `footprintVariants` (narrow/standard/wide).
- **Open space** — `stormwater_retention_pond`, `pond_lake`, `linear_park_greenway`,
  `constructed_wetland_eco_park`, `wetland_rain_garden`, `canal_waterway`,
  `reservoir_watershed_park`, `fountain_water_feature`, `urban_pocket_park`,
  `neighborhood_park`, `civic_plaza`, `parking_areas`.
- **Streets** — `arterial_boulevard`, `haussmann_boulevard`, `london_crescent_road`
  (curved), `montreal_commercial_boulevard`, `roundabout`, `collector_road`,
  `narrow_residential_street`, `woonerf_shared_street`, `toronto_laneway`,
  `commercial_alley_laneway`.

## 4. What the benchmark needs — reachable now vs. needs new geometry

| Design move in the West District render | Catalog piece (exists) | Engine status |
|---|---|---|
| Density transect — mid-rise core → townhouse rows → detached edge | residential_multifamily → brownstone_rowhouse → residential_single_family | Phase 1 tagging |
| Intra-type variety — heights/footprints/rooflines within a band | scaleVariants + footprintVariants + per-block floors | Phase 1 (floors/aesthetic) + Phase 2 (footprint) |
| Civic/commercial anchors + parking | commercial_office, institutional_*, parking_areas | Phase 1 tagging |
| Signature naturalized water feature (organic pond + greenway) | stormwater_retention_pond, linear_park_greenway | Phase 3 (organic open-space geometry) |
| Curvilinear street hierarchy — boulevard, crescents, roundabouts | arterial_boulevard, london_crescent_road, roundabout | Phase 3 (non-orthogonal streets) |
| Rear laneways behind townhouse rows (fine grain, not courtyards) | toronto_laneway, woonerf_shared_street | Phase 3 (block-interior lanes) |

---

## PHASE 1 — Strategic per-zone tagging (backend only; delivers TYPE variety)

Fastest, lowest-risk, biggest immediate jump. Resolver already consumes it.

**A. Building placement policy** (per block, in the `generator.py` block loop ~line 232).
Choose `development_type` + `development_aesthetic` + floor target from BLOCK CONTEXT, not
one global value:
- EDGE blocks abutting existing low-rise neighbourhoods → step DOWN:
  `residential_single_family` / `residential_duplex` / `brownstone_rowhouse`, 2–3 floors
  (compatibility transition — the site is ringed by detached housing).
- CORE / transit-adjacent / main-spine blocks → step UP: `residential_highrise` or
  `residential_multifamily`, tall floors.
- MAIN-STREET frontage blocks → `mixed_use` / `commercial_retail` (active ground floor).
- One or two ANCHOR blocks flanking the central park → `institutional_education` /
  `institutional_health` / `commercial_office` (a civic landmark).
- Interior/default → `residential_multifamily` or `mixed_use`, midrise.

Constrain `development_type` to the 26 real catalog values so the resolver hits (it defaults
to `mixed_use` on a miss — don't rely on that). Keep aesthetic within a COHERENT palette per
scenario (do not randomize): e.g. `climate_first` → `eco_urban_green_architecture` /
`scandinavian_nordic` / `biophilic_contemporary`; a heritage scenario → `brownstone_rowhouse`
/ `parisian`. Vary floors per block so the resolver's `minFloors`/`maxFloors` filter surfaces
different archetypes AND the archetype's own scaleVariant.

**B. Street hierarchy.** Emit at least TWO ROW widths so the width-band resolver yields
different street archetypes: a MAIN SPINE at `>=22m` (→ main_street_complete /
arterial_boulevard) and local streets at `10–15m` (→ narrow_residential_street). Keep every
ROW at/above the CSPS033 fire-clear floor (`community_rules.MIN_ROW_M`).

**C. Park variety.** Emit a MIX instead of only big central blocks: one signature central
green (large → neighborhood_park), small POCKET parks (`<1500 m²`) at a few intersections /
edge slivers (→ urban_pocket_park), and optionally one hardscape CIVIC PLAZA near the anchor
block (tag `spaceType`). Still meet `rules.open_space_share`; keep courtyards excluded from
the open-space metric.

**Control signal:** feed the policy from the experts where possible — let `layout.strategy` /
`development_aesthetic` set the PALETTE and character; the deterministic pass distributes
specific types across blocks by context. `layout.strategy` is the dead wire to reconnect
(`_param_value(parameters, "layout.strategy")`).

## PHASE 2 — Catalog-driven footprints (delivers FORM variety, breaks the courtyard look)

Once a block's archetype is chosen, shape its mass from THAT archetype's real dims
(`minWidth_m`/`maxWidth_m`/`minDepth_m`/`maxDepth_m` + `suggestedFloorHeight`) instead of
always a perimeter ring — a tower gets a compact point footprint, a rowhouse gets narrow
bars fronting the street, an institution gets one large mass. This ties morphology to the
catalog (choose from the library, don't invent shapes). Keep single-ring (no holes); keep
feeding `masses_m` / `mass_floors` so the frozen evaluator metrics stay valid. The courtyard
block (`generator.py:315`) must fire ONLY for perimeter-typology blocks — gate on typology,
not on `len(mass_polys) > 1`.

## PHASE 3 — Layout realism to hit the West District benchmark (biggest lift; new geometry)

Catalog is ready; the geometry engine is the only gap.

**3A. Density transect as an explicit layout model** (`generator.py`). Define a site "core"
(centroid, transit node, or main frontage) and grade `development_type` + floors DOWN with
distance to the site edge, so the plan reads core → mid → edge, matching surrounding context.
Replaces ad-hoc per-block rules with a continuous, deterministic gradient.

**3B. Curvilinear street hierarchy** (`street_graph.py` — currently orthogonal-only).
- Keep the orthogonal option; add a CURVED collector option: a smoothed spine polyline
  through the site with offset local streets, so streets resolve to arterial_boulevard /
  london_crescent_road, not just straight grid lines.
- Insert ROUNDABOUT nodes at major intersections (tag so the `roundabout` archetype
  resolves; the traffic-safety catalog set has these).
- Emit REAR LANEWAYS: split large residential blocks with a narrow mid-block lane (→
  toronto_laneway / woonerf_shared_street) instead of a perimeter courtyard, so townhouse
  rows front the street and back onto a lane.
- Maintain the CSPS033 fire-clear floor on every ROW.

**3C. Organic central open space** (`generator.py` open-space phase — currently rectangular
blocks only). Carve a SIGNATURE landscape feature with an irregular boundary instead of
picking whole rectangular blocks: buffer a curved spine polyline into a linear greenway,
and/or place an organic-edged basin so it resolves to stormwater_retention_pond / pond_lake /
linear_park_greenway. Keep inside `open_space_share`; keep excluded from building/courtyard
metrics; keep single-ring (approximate the curve with a dense vertex ring).

**3D. Footprint-from-archetype** (Phase 2) applies here too — a tower is a point, a rowhouse
is a narrow bar with a rear lane, an institution is one large mass, not a uniform ring.

---

## Hard constraints (do not break)

- **Deterministic** — no RNG. Placement must be a pure function of geometry + params + DNA
  (district land-use, transit, surrounding context) so re-runs and the refinement loop stay
  stable.
- **Frozen evaluator contract** — keep feeding `result.masses_m`, `result.mass_floors`,
  `result.blocks_m`, and `geometry_inputs` exactly as today; new typologies must append their
  masses + floors so `plan_metrics`/`plan_evaluator` see real footprints.
- **Single-ring zones** (no interior holes) — decompose any ring/holed mass (see
  `parceling.py:63` `_decompose_ring_mass` for the existing cut trick).
- **Unique zone names** — keep the "· Building A/B/C" suffixing so labels don't collide.
- **Never touch `buildingArchetypes.json`, and never `json.dump` it.**
- Tests run in Docker:
  `docker exec devplatform-backend pytest backend/tests/test_plan_geometry.py test_planning_agents.py -q`

## Validation (pilot → confirm → scale)

- **Unit tests:** per-zone `development_type` varies by block context and is deterministic;
  every emitted `development_type` is a real catalog value; `>=2` street widths emitted; a mix
  of pocket + neighborhood parks emitted; `open_space_share` still met; every ROW `>=`
  MIN_ROW_M.
- **Smoke:** run `backend/_smoke_scenarios.py` (real Anthropic calls, ~$1–2) and confirm the
  three scenarios now place DIFFERENT building/park/street types, not just different numbers.
- **Visual:** generate one globe render of a single scenario and compare before/after against
  the West District reference for: (a) visible density transect, (b) a naturalized central
  water/greenway feature, (c) at least one curved street + roundabout, (d) distinct building
  types by location.

## Recommended sequencing

1. **Phase 1 pilot on `climate_first`** — strategic building tags + spine/local street
   hierarchy + pocket/central park mix. Render, compare, green-light. (~1–2 days, backend
   only.)
2. **Phase 2** — footprint-from-archetype. Breaks the courtyard sameness.
3. **Phase 3** — curved streets + roundabouts + laneways + organic pond. The real lift; this
   is what closes the gap to the West District reference. De-risked because you draw to
   existing archetypes.

## File reference

| What | File | Anchor |
|---|---|---|
| Plan geometry orchestrator | `backend/app/services/plan_geometry/generator.py` | 127–383; tag stamping ~145, 232–334; open space 202–220; courtyard 315 |
| Perimeter massing (add typologies) | `backend/app/services/plan_geometry/parceling.py` | 96–133; ring cut trick 63–93 |
| Street grid (add curves/roundabouts/lanes) | `backend/app/services/plan_geometry/street_graph.py` | 83–185 |
| Rule profiles / scenario defaults | `backend/app/services/plan_geometry/community_rules.py` | 40–56, 127–139; MIN_ROW_M 17 |
| Parameter vocabulary (layout.strategy) | `backend/app/services/planning_agents/schemas.py` | 19–61 (line 53) |
| Frontend resolver (NO change; consumes tags) | `frontend/src/components/viewer/resolvePlanZoneArchetypes.ts` | buildings 80–134, open space 156–163, streets 166–177 |
| Building catalog (read-only; never json.dump) | `frontend/src/data/buildingArchetypes.json` | — |
| Street catalog | `frontend/src/data/streetPathArchetypes.json` | roundabout, boulevards, crescents, laneways |
| Open-space catalog | `frontend/src/data/openSpaceArchetypes.json` | pond/greenway/wetland ids |
| Scenario smoke test | `backend/_smoke_scenarios.py` | — |
