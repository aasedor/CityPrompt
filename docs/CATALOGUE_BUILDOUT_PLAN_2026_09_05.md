# City Prompt catalogue buildout plan

Proposed September 5, 2026. Teaching target: January 2027, 60 students working in approximately eight groups. This is a coverage and implementation plan, not an asset approval or a generation run.

## Outcome and scope

Give students **at least two meaningfully different, reviewed, placeable choices in every defined asset collection**, with a consistent pick, place and reshape experience. Complete useful coverage before producing third and fourth alternatives. Existing additional approved choices remain available; this is a minimum, not a cap.

Use the Calgary-informed student collections already implemented in `frontend/src/features/calgaryCatalogue/guide.ts`. Architectural styles and land-use district codes remain filters and teaching references, rather than multiplying production quotas. For example, a student exploring detached homes and R-C1 should find both a modern infill home and a Craftsman bungalow. Neither card should claim the selected design automatically complies with that parcel's zoning.

**Recommended scope assumption:** the current guide has 33 navigation groups. One, “Other building ideas,” contains two custom/prompt placeholders. Keep that as an import/design workflow, not a fixed-model collection. Cover the other **32 collections with 64 choices**: 13 building collections / 26 choices, 10 parks and open-space collections / 20 choices, and 9 street collections / 18 choices. Parking remains visibly separate from parks. Global street inspiration retains two real choices. This explicitly excludes custom placeholders from the finished-model count.

This first pass gives the broad “Schools, civic & recreation” collection two choices total. It does not yet promise two schools, two hospitals and two arenas separately. If those become separate student-facing subcategories, each new collection receives its own two-choice requirement before it is advertised as complete. The same rule applies to future taxonomy changes.

Covering every historical architectural-style category would be a separate, larger programme.

## What exists and what it means

| Evidence inspected | Finding | Consequence |
| --- | --- | --- |
| Current source catalogues | 224 building parents / 896 variants; 130 open-space parents / 520 variants; 115 street parents / 355 variants | A large reference library exists. These counts do not measure 3D readiness. |
| Current pick/place pilot | Two cards: exact flat-roof infill and the adaptive neighbourhood park; a separate sidewalk-road tool | Expand this interaction deliberately; do not expose every reference as a finished 3D object. |
| Original checkout's RLASM 6.1 clay manifest | Ten exact variants declare runtime activation and independent clay review; six are nominated in this minimum set | Reuse exact deliveries after verifying files, provenance and integration. A manifest entry does not establish terrain, arbitrary scaling or final-render fidelity. |
| Neighbourhood park pilot | Functional adaptive composition, but visual P1 findings remain; catalogue/production approval withheld | Finish this one park before extending the recipe. |
| Calgary street research | Thirteen authored Draft 4.0 sections already contain dimensional data; seven are nominated here | Reuse the section data and diagrams; verify actual 3D networks and rendering rather than generating arbitrary street pictures. |
| Older building waves and basketball experiments | Useful source, geometry and review evidence; some historical approval claims conflict with current restrictions | Recover exact candidate files and compare them to the current contract. Do not automatically promote, delete or regenerate them. |

The accompanying matrix separates **six reviewed-clay reuse candidates, one functional park pilot, seven authored draft street sections, and fifty reference nominations**. These are origins, not release approvals. Twenty of the 26 building slots still need current-method review or production; the audit has not established that all twenty must be built from scratch.

The other four clay deliveries—Vancouver Special, laneway house, Brown Cafe and vintage service station—remain useful extras. They are not discarded or used twice to inflate minimum coverage.

## Proposed two-choice roster

These are nominations using existing exact parent/variant IDs. The machine-readable matrix records every ID, intended difference, source status, reshape contract, release evidence and wave. **A nomination is not a source lock or a quality approval.** Where two variants share a parent, their geometry or programme must actually differ. A recolour, thumbnail change, alternate name or random tree seed cannot satisfy the second slot.

† Existing independently reviewed architectural-clay delivery according to the original manifest; complete runtime release checks are still required.

### Buildings — 13 collections, 26 choices

| Collection | Choice A | Choice B | Wave |
| --- | --- | --- | --- |
| Detached homes | Modern flat-roof infill home † | Craftsman bungalow † | 1 |
| Duplexes & semi-detached homes | Side-by-side duplex infill | Stacked Montreal duplex | 1 |
| Rowhouses & townhomes | Contemporary street-facing townhomes | Siheyuan courtyard housing † | 1 |
| Apartments | Timber-and-glass mid-rise apartments | Brick courtyard apartments | 1 |
| Residential towers | Slender residential tower with podium | Balcony slab residential tower | 3 |
| Homes over shops & mixed use | Courtyard mixed-use block | Converted mill mixed-use block | 2 |
| Shops & services | Corner neighbourhood shop † | Single-storey retail strip † | 1 |
| Hotels & visitor accommodation | Urban corner hotel | Timber lodge hotel | 3 |
| Offices | Urban office block | Timber office campus | 3 |
| Schools, civic & recreation | Brick neighbourhood school | Timber community hall | 2 |
| Industry & warehouses | Gabled industrial workshop † | Tilt-wall warehouse | 2 |
| Indoor farms & food production | Enclosed indoor farm | Warehouse with rooftop greenhouses | 3 |
| Transit & utilities | Urban CTrain platform and shelter | Civic energy centre | 3 |

### Parks and other open spaces — 10 collections, 20 choices

| Collection | Choice A | Choice B | Wave |
| --- | --- | --- | --- |
| Pocket & sub-neighbourhood parks | Timber-and-gravel pocket park | Meadow pocket park | 2 |
| Neighbourhood & community parks | Rustic neighbourhood park | Pastoral community park | 1 |
| Regional & destination parks | Pastoral destination park | Industrial-reuse destination park | 3 |
| Linear parks & green connections | Rail-trail greenway | Riverfront greenway | 2 |
| Natural areas & restoration | Native urban woodland | Prairie pollinator meadow | 3 |
| Plazas & gathering places | Formal civic plaza | Market and event square | 1 |
| Play & sport amenities | Classic basketball court | Inclusive playground concept | 2 |
| Gardens & quiet spaces | Community growing garden | Quiet Japanese garden | 2 |
| Waterfront & stormwater spaces | Wetland and rain garden | Naturalized riparian promenade | 3 |
| Parking, special sites & custom spaces | Conventional parking court | Planted parking court | 3 |

### Streets and pathways — 9 collections, 18 choices

| Collection | Choice A | Choice B | Wave |
| --- | --- | --- | --- |
| Local & residential streets | Calgary local — 16 m | Calgary high-activity local — 21 m | 1 |
| Collector streets | Calgary collector — 20 m | Calgary high-activity collector — 27 m | 2 |
| Arterial & major streets | Calgary four-lane arterial — 33 m | Calgary high-activity arterial — 36 m | 3 |
| Alleys & service lanes | Calgary alley — source figure 1 | Custom bioswale alley | 2 |
| Walking, wheeling & shared streets | Green-corridor multi-use pathway | Protected two-way cycle track | 1 |
| Transit corridors | Bus rapid-transit corridor | Tram avenue | 3 |
| Intersections & crossings | Protected corner-island intersection | Compact single-lane roundabout | 2 |
| Traffic calming & safer streets | Planted curb-extension crossing | Raised crossing | 2 |
| Other streets & global inspiration | Tree-lined main street | Scenic parkway | 3 |

The two indoor-farm choices deliberately use different forms within one parent. The duplicate “Vertical Farm / Indoor Agriculture” parent listing is not counted as another design. Likewise, the two linear-park variants must have different route/edge programmes, not duplicated scenery.

The `infill_duplex` variant currently inherits its parent's detached-home browsing group. Add a reviewed variant-level override to “Duplexes & semi-detached homes”; do not move every variant of the infill parent. The same variant-level programme review applies before report generation for converted mills, mixed-use buildings and courtyard housing.

If a nominated source pair proves contradictory or insufficiently distinct, substitute one exact, reviewed candidate within that slot and update the matrix. Do not complete the quota with an inferior proxy. The pocket-park and neighbourhood/community-park pairs particularly need this source/layout comparison before both are commissioned.

## Implementation sequence

### Foundation: reconcile and benchmark, before broad production

1. Snapshot the exact catalogue IDs, clay manifest, source-view hashes, candidate paths, review status and rights/provenance. Inventory image-only, historical geometry, reviewed clay, local pilot and classroom-ready states separately. Preserve the dirty original checkout and its files.
2. Reconcile local asset packaging. The active pick/place checkout uses a separate local public-asset overlay and backend harness; the clay manifest lives in the original checkout. Define a portable runtime manifest and serving path before claiming a catalogue release. Preserve exact IDs and saved-project compatibility.
3. Add a small readiness manifest beside catalogue metadata: exact variant, visual tier, native dimensions, supported reshape/placement mode, source revision, model version/hash, dependencies, download/triangle counts, review and activation state. The default catalogue shows ready choices. Existing reference browsing remains available in the advanced workflow, clearly identified.
4. Implement the one known variant classification correction, plus many-to-many programme metadata only for selected candidates. Keep parcel zoning/reference layers separate from proposed buildings and avoid bundling the full historical bylaw study in the browser.
5. Measure a representative neighbourhood on a recorded student-like laptop/browser. Record current load, orbit, picking, reshape, save/compile, capture and memory behaviour before setting final budgets.
6. Close shared-ground failures: validate persistent ground samples through camera/LOD changes, cold close-up entry and fresh tile coverage. The current pilot can withhold assemblies when ground coverage is missing. Do not fix this by placing objects at guessed heights or silently freezing obsolete terrain.

Exit: an inventory with explicit gaps, a reproducible local environment, one reusable release checklist and baseline performance/contact evidence. No model family has been newly approved merely by appearing in this inventory.

### Wave 1: a complete neighbourhood starter — 18 choices

Finish two choices in each of nine collections: detached, duplexes, ground-oriented housing, apartments, shops, neighbourhood parks, plazas, local streets and walking/cycling routes.

**First five existing building deliveries to integrate:** modern infill, Craftsman bungalow, Siheyuan courtyard housing, corner shop and retail strip. This fills existing slots without paying to rebuild them.

**First five new building candidates:**

1. Side-by-side duplex — `calgary_modern_infill_house / infill_duplex`.
2. Stacked duplex — `montreal_duplex / montreal_duplex_plateau`.
3. Contemporary townhouse row — `rndsqr_missing_middle_townhomes / rndsqr_townhome_dark_wood_metal`.
4. Timber-and-glass apartments — `contemporary_midrise_residential / contemporary_midrise_variant_timber_glass`.
5. Courtyard apartments — `courtyard_family_housing / courtyard_family_brick_modern`.

Source-audit the five, then build **one** through full review and placement before scaling to the remaining four. These are separate exact sources, not variants to derive by relabelling one GLB. Together with the five reused deliveries, they complete five housing/shop collections.

For parks, close the existing rustic park's finish and ground-contact findings, then adapt one genuinely different community park and two plaza layouts. For streets, validate one sourced local section end-to-end, then the second local and both active-travel choices. Complete the pilot for each domain before its bounded batch proceeds.

Exit: a novice can create a mixed housing neighbourhood with a shop, connected park/plaza and streets, then save, reopen and capture the same scene. Release may proceed collection by collection once both choices meet their gates.

### Wave 2: everyday services and connected public space — 22 additional choices

Finish mixed use, civic, industry, pocket parks, play/sport, gardens, linear parks, collectors, alleys, intersections and traffic calming. Reuse the reviewed gabled industrial shed. Examine the historical brick-school, mixed-use and basketball candidates before commissioning replacements.

The intersection and calming work is a prerequisite for credible street networks, not just decorative catalogue expansion. Validate the complete route from a dwelling entrance to sidewalk, crossing and park entrance. A transit, park or street furnishing has one geometry owner so it is not duplicated by adjacent assets.

Exit: 40 minimum choices across 20 complete collections, including everyday services and meaningful movement connections.

### Wave 3: larger plans and specialist uses — 24 additional choices

Finish towers, hotels, offices, indoor farms, transit/utilities, regional parks, nature, waterfront/stormwater spaces, parking, arterials, transit corridors and global street references. Reuse the proven pipelines; review unusual roofs, large assemblies, water edges, track systems and higher instance counts separately.

Exit: 64 minimum choices across all 32 defined asset collections. Each collection has two real choices, and each choice has passed its own evidence requirements. Large scenes must meet the measured performance budget; “last collection added” is not sufficient to declare readiness.

### Classroom rehearsal and freeze

Have people unfamiliar with the implementation build a plan from a blank site. Test two collaborators taking turns, save/reopen, undo/redo, changing a variant, limited network conditions, reference zoning visibility, and presentation capture. Keep simultaneous editing improvements secondary to reliable sharing and persistence.

Aim to complete production by late November, rehearse and fix in early December, and freeze the classroom catalogue by mid-December. These are planning targets, not an effort estimate. Use the first complete pilot's measured build/rework time to forecast the remaining batches; reserve at least the final two weeks before teaching for fixes and setup. If that forecast exceeds the runway, report the shortfall explicitly rather than lowering review quality or quietly dropping collections.

## Three production methods, one student interaction

### Buildings: RLASM 6.1 architectural clay

Follow the canonical exact-source contract: compatible front, oblique and top references with hashes; measured plan/roof/opening relationships; complete clay geometry; export and reimport the actual GLB; full camera evidence; separate holistic visual review with zero unresolved P0/P1 issues. Keep clay-delivery approval distinct from textured keeper approval. Existing human activation covers only its named deliveries; new runtime activation follows the repository's explicit human-approval requirement after a concrete reviewed batch is ready.

The visible 3D geometry owns the building's massing, footprint, height and openings. Catalogue source images still guide selection and final-render conditioning. The delivery manifest preserves that relationship.

**Reshape honestly.** Start each new family at its verified native dimensions. A larger house plot can place additional whole houses only after its explicit repetition contract passes; a long footprint must never create one elongated house. Continuous stretching and arbitrary floor changes are not granted by the current clay contract. Repeated bays/floors, corner modules, end caps or discrete small/medium/large models are a separately verified capability. Until available, show the supported size clearly and retain the plot-size controls without implying they deform the house. Towers retain source-appropriate floor ranges; render text cannot change them.

### Parks and plazas: adaptable landscape assemblies

Continue the deterministic neighbourhood-park composer. Use a shared, versioned kit of vegetation, benches, play equipment, courts, pavilion, edges and ground materials, with separately authored layout recipes. Do not use a single stretched park mesh or one flat aerial image as the finished landscape.

Preserve metre dimensions for equipment, courts, paths and furniture. When the footprint changes, recompute paths, lawns, beds and equipment placement within the polygon. At small sizes omit secondary amenities explicitly; below the programme's minimum suggest a pocket park or suitable alternative. Never silently turn the chosen neighbourhood park into a different archetype. Large sites add landscape or repeated suitable components, not giant benches or hoops. Keep small/medium/large and concave cases deterministic through save/reload.

Close the known pilot defects before reuse: repetitive tree silhouettes/heights, isolated flower clumps, gravel/activity-edge transitions and appearance in Google lighting. Add source-matched opposite views, pedestrian contact evidence and faithful final-render tests. Recover basketball geometry, materials and source evidence as a candidate, then validate actual court proportions and ground contact.

Paths connect through explicit entrances to nearby eligible sidewalks; planting clears those approaches. Buildings, water, road carriageways and equipment footprints are barriers. Crossing a road requires a supported crossing node. No invented access through an unannotated building, no trees obstructing entrances, and no rectangular green apron covering existing Google context outside the design.

### Streets: parametric sections and connected networks

Build from existing section bands, widths, source figures and route geometry. Change route/length independently of section dimensions. Swapping a section rebuilds its lanes, curbs, footways, planting and crossings coherently; arbitrary proportional width scaling must not retain a “Calgary standard” claim.

Use explicit street-edge, sidewalk, crossing, stop and junction connections. Intersections and traffic calming attach to compatible network geometry; they are not floating props. Test T and four-way joins, curves, unequal section widths, service access, cycle tracks, stop platforms and transitions to park paths. Rails, shelters, curbs and vegetation have one owner across adjacent catalogue choices.

Only one sourced Calgary alley section exists in the current set. Pair it with a clearly labelled **custom bioswale alley**, with its own dimensional/access review, rather than inventing a second manual variant. Every draft-derived street card carries its source revision and status.

## Release criteria for every choice and every pair

| Gate | Required evidence |
| --- | --- |
| Identity and difference | Exact parent/variant and compatible source views; both choices visibly differ in massing, layout, programme or sourced street section. No aliases, recolours, bare size copies or duplicate sources counted twice. |
| Visual quality | Actual delivered asset reviewed from overhead, aerial, opposite side and pedestrian views; appropriate close-ups, native bounds, contact details and a phone comparison. Buildings meet the RLASM clay review contract. Parks/streets receive their own complete source/scene review. |
| Ground and containment | On an identified empty lot, verify full footprint inside the boundary, flat and sloping cases, rigid equipment pads, building bases and street-to-path transitions. Inspect cold load and LOD/camera changes, not just one warmed aerial view. No obvious floating/buried geometry or blanket ground cover. Record terrain uncertainty rather than presenting survey accuracy. |
| Student interaction | Pick, preview, place, move, rotate, valid and invalid reshape, duplicate, undo/redo, save and reopen through the real UI. Previews and final saved geometry agree; unsupported changes explain themselves in plain language. |
| Park size/network cases | Compact, typical, large, rotated concave and too-narrow footprints; fixed-size amenities, explicit omissions and connected entrances. Roads test compatible joins, curves, crossings and section changes. |
| Render identity | Direct capture's camera, model versions, transforms, class/instance IDs, depth and masks agree with the saved plan. Final-image polishing may improve appearance without moving, adding or swapping structures. Test a partially hidden building, a hidden park amenity and a site-edge object from two views. Reject invented visible replacements for occluded objects. |
| Performance and persistence | Measured load/frame/memory/interaction budgets; bounded layout/instance counts; no compile storm during drag; preserved IDs and deterministic reopening. |
| Review and activation | Complete evidence, recorded independent result, required human activation and an intentional runtime manifest change. Two released choices are required before marking a collection complete. |

The previous park image-edit trial improved appearance but changed camera/composition and some scene details. It was rejected as geometry-faithful proof. Keep the deterministic 3D capture as authority and report image/video fidelity honestly. Full interactive generative walkthroughs are not a dependency for finishing this catalogue.

## Prevent catalogue growth from slowing the application

- Load only lightweight card metadata and thumbnails while browsing; lazy-load selected models. Do not eagerly fetch 64 GLBs or bundle research documents.
- Share materials, geometry and park equipment; instance repeated houses/vegetation, use culling and appropriate detail levels, and give caches/disposal explicit bounds. Avoid one copied kit per park variant.
- Debounce committed rebuilds; keep placement/drag previews local and responsive. Resize should not trigger a model download or paid image generation for every pointer movement.
- Record bytes, triangles, meshes, materials and dependencies for each delivery. RLASM clay remains texture-free. Existing clay examples are roughly 0.7–4.8 MB; use a provisional target of 3 MB per routine new building and review justified exceptions instead of destroying identity to meet a cap.
- Proposed performance fixtures: 50 building instances, six parks and twenty street segments, plus a doubled stress scene. On a documented representative laptop, aim for at least 30 FPS during a normal warmed orbit, cached preview response within 100 ms and ordinary save-to-rebuild within three seconds. These are starting targets to calibrate in the foundation phase, not measurements or promises. Record cold-load time and peak memory separately.
- Promote only reviewed runtime assets through LFS/artifact storage. Keep raw renders, failed candidates, experimental textures and camera boards outside the source tree or in ignored `artifacts/` output. Do not clean preserved historical output as a side effect of this work.

## Batches, costs and verification

Keep buildings, parks, streets and shared runtime fixes in distinct initiatives/branches. Follow dry run → one exact pilot → independent review → bounded batch of no more than five new choices → checkpoint. Each batch has a finite candidate list, evidence requirements, elapsed-time/cost log and a local commit. No unattended open-ended generation loop and no push/deployment merely to make a review available.

Measure the first pilot's production and correction cost before forecasting the total. The prior authorization was **up to $10 total for live image/video API tests**; it is not a fresh $10 per wave or authorization for a larger catalogue-generation budget. Reconcile earlier spend before any further paid test. Prefer local geometry, mock provider tests and free direct captures until a specific paid fidelity test has a known remaining allowance. This planning task spends none of that budget.

For implementation, run narrow frontend Vitest suites for the affected catalogue, placement, layout, street, grounding and capture features; then TypeScript checking for production TS changes. Run narrow backend/compiler tests when those paths change. Add tests for meaningful new contracts and regressions rather than mechanical mirrors of the code. Follow with the actual browser/student trial and independent visual evidence. An asset is not complete solely because structural tests pass.

Maintain the matrix as the release ledger: exact IDs, source lock, distinction proof, build/review state, supported dimensions, reuse/new-work decision, byte/triangle counts, integration result, human activation and remaining blockers. Add immutable evidence paths as work proceeds. Do not overwrite a failed candidate to make the ledger appear clean.

## Calgary source status and teaching behaviour

Use plain-language forms such as “Detached homes,” with district references available as guidance. R-C1 is one district to investigate for single-detached homes; the district assigned to the actual site, chosen programme and design dimensions still require review. Keep planning recommendations advisory: explain the zoning, access, servicing or policy changes needed to make a proposal possible. Do not block the student's design solely for disagreeing with existing zoning. [City land-use district summaries](https://www.calgary.ca/planning/land-use/districts.html).

Retain the distinction between the approved [Complete Streets Policy and Guide](https://www.calgary.ca/planning/transportation/complete-streets.html) and the emerging [Street Manual](https://www.calgary.ca/planning/city-building-program/city-building-program/the-street-manual.html). The latter's current project page anticipates final-draft administrative approvals in Q2 2027, after this course begins. The existing Draft 4.0 sections are useful sourced design references, not newly certified standards.

Use [Connect: Calgary's Parks Plan](https://www.calgary.ca/planning/parks-rec/parks-plan.html), approved by Council in May 2025, to inform park functions and connections. Our catalogue group names are educational browsing labels and do not automatically assign an official park classification.

Recheck source status before the December freeze. Keep source date, status and link with the selected asset/report; no citywide zoning file belongs inside each model.

## Local records and deliverables

- Plan: `docs/CATALOGUE_BUILDOUT_PLAN_2026_09_05.md`.
- Coverage matrix: `docs/CATALOGUE_COVERAGE_MATRIX_2026_09_05.json`; 32 groups and 64 unique exact parent/variant pairs.
- Existing context: `docs/PICK_PLACE_RESHAPE_PILOT_2026-09-05.md`, `docs/NEIGHBOURHOOD_PARK_PILOT_2026-09-05.md`, its independent review in `docs/reviews/`, and `docs/CALGARY_RESEARCH_RECONCILIATION_2026_09_05.md`.
- Building authority: `docs/RLASM_LATEST_METHOD.md`, `docs/RLASM_REPOSITORY_POLICY.md`, `docs/HIGH_QUALITY_3D_BUILDING_MEMORY.md` and their machine companions. This plan does not change those methods or inherited asset approvals.
- Original read-only asset inventory: `C:/Users/andre/OneDrive/Documents/CityPrompt/seed/model-library/rlasm-architectural-clay/library.json`. Its state and source hashes are recorded in the matrix; copying that manifest alone would not make the deliveries available in another checkout.

Work is local on `codex/catalogue-coverage-plan`, based on `9126498ca`. The two documents are the intended source changes. The inventory, generation helper and table draft are ignored planning output under `artifacts/catalogue-coverage-plan/`. No application code, model assets, saved projects or source catalogue entries were changed for this plan.
