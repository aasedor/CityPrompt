# Mixed Community 3D QA

Last verified: 2026-07-18 (America/Edmonton)

## Live QA project

- Project: `Mixed Parks + Streets QA`
- Project ID: `d062b9f4-eef5-42f1-a02c-aedb0c99a2ec`
- Context: Westbrook Communities, Calgary
- Repaired boundary: 56.0 ha, approximately 1,056 m x 971 m
- Applied scenario: Economic
- Plan score: 0.977
- Explicit context connections: 9

The generated plan contains 742 building zones, 83 green-space/courtyard
zones, 95 street zones, and 51 height-framework overlays. All emitted plan
polygons passed geometry validation after the legacy boundary and courtyard
repair work.

## Completion-gate snapshot

| Product requirement | Authoritative evidence | State |
| --- | --- | --- |
| Planning-principled mixed community | Live Economic plan: 742 buildings, 83 parks/courtyards, 95 streets, plan score 0.977; emitted polygons passed geometry validation | Proven |
| Roads and paths connect to existing context | 9/9 connectors touch the site boundary; 8/9 intersect cached Calgary road/path centreline data; maximum residual gap 0.99 m | Proven |
| One Generate/LEGO action creates the mixed interactive scene | Both entry points use one atomic `place-community` transaction; 742/742 buildings are linked and 178/178 public-realm zones are compiled | Proven |
| Buildings, parks and streets sit on Google terrain | Terrain-mesh sampling covers prepared site, representative park and street geometry; live reservoir and district inspections show seated proposal surfaces | Proven |
| Six recurring public-realm archetypes have authored geometry | Neighborhood Park, Urban Pocket Park, Linear Park/Greenway, Formal Civic Plaza, Fountain, and Stormwater Pond have explicit profiles, program guides, zero-call compiled surfaces and one atomic six-archetype API contract test | Proven |
| Trees and benches cannot collide with live paths/water | Interactive scene and ground diagrams assign neither trees nor bench pads; Render places both only after circulation, water and fixed programs are known | Proven |
| Geometry-faithful final render | Reservoir night, documentary, isometric and site-plan-photo variants preserve water and perimeter circulation; local park diagrams constrain internal geometry | Proven for reservoir; mixed-district proof pending detailed families |
| Detailed building-family coverage | Current database: 96 `contemporary_midrise_residential` LEGO stacks; 356 vernacular courtyard, 168 walk-up, 121 bodega and 1 civic zone remain exact-footprint planned massing | Pending four exact family manifests |
| User-controlled API spend | Community compilation uses no image/model credits; park batches are capped; current-view Render discloses 2 calls normally and 3 with shared high fidelity | Proven |
| Regression and production build | Frontend 45 files / 348 tests; production build 3,354 modules; backend planner/geometry/LEGO combined suite 75/75 in the current checkout | Proven |

The objective therefore remains active. Final completion requires the four
correct building-family manifests, an in-place Rebuild of the 646 planned
masses, and one mixed-district visual/render audit. Unrelated lookalike modules
are not acceptable completion evidence.

## Community 3D compile

- Park/street/courtyard ground layers compiled: 178/178
- Building recipes placed during this QA pass: 96/742
- Supported contemporary-midrise recipes: 96/96
- Remaining building-family gap: 646/742 zones correctly report no matching
  family and 0 report unexplained recipe failures. Earlier counts of 431
  no-family and 255 other failures were caused by launching 742 local planning
  requests simultaneously, not by invalid geometry. LEGO planning and saving
  are now bounded to eight concurrent requests while preserving input order.
  Building-family generation is being developed concurrently and was
  deliberately not overwritten in this pass.

The detailed-family upgrade seam is covered before those four assets arrive.
An atomic Community 3D Rebuild reuses the existing exact-footprint Building,
removes only its `plannedMassing` fallback, installs the detailed
`legoAssembly` recipe and preserves unrelated specifications. Parks and
streets in the same transaction retain their archetype and gateway data while
receiving the same server compile timestamp. No per-item commit can leave a
half-upgraded district.

## Ground-contact gate

The Google Elevation endpoint currently returns its low-fidelity constant
fallback at this location. Compiled proposal surfaces therefore do not trust
that batch response. They use staggered, one-time raycasts against the loaded
Google 3D Tiles mesh and reject implausible unrefined root-tile hits.

Live measurements captured before removing diagnostics:

- Prepared site surface: 100% vertex coverage, 12.41 m sampled relief.
- `Economic · Park 4`: 100% vertex coverage, 1.31 m sampled relief.
- Sample street: 100% vertex coverage, 0.06 m sampled relief.

The same lower-plausible-surface rule now seats park props, street stations,
roundabouts, generated GLB buildings, LEGO stacks, and legacy stored
elevations. A stored roof click and a current roof/canopy hit can no longer
win over a materially lower plausible ground sample.

## API use during this QA pass

- Planning/scenario calls: 4
- Park-ground image calls: 2
- Final stylized render calls: 0

The second Park 4 ground image was retained; the first was rejected as too
generic. No further paid render was started because full building-family
coverage remains the current quality gate.

## Verification

- Frontend type check: passed.
- Frontend tests: 30 files, 261 tests passed.
- Frontend production build: passed.
- Focused backend tests from this pass: 32 passed, including 24 plan-geometry
  tests.
- Final live browser check: no runtime errors after Google tiles settled.

## Runtime note

The live frontend and active backend/celery containers are now mounted from
`PlaygroundNEW`. Earlier in the session the backend was mounted from the older
`Playground` checkout; do not restore that stale mount when restarting the
development stack.

## Reservoir ground-truth trial

- Project: `empty lot in downtown`
- Project ID: `67931c5d-c9a2-403d-89ba-12968bc8f870`
- Zone ID: `37a13a43-9c45-4407-8728-80eed3b9f1ba`
- Archetype: Reservoir / Watershed Park
- Drawn parcel: approximately 146 m x 80 m (1.1 ha)
- Ground profile: `reservoir-watershed-park-v3`

The interactive Google-tiles scene now uses the generated drape as the exact
parcel-clipped ground surface. Public-realm tile stencil holes are disabled by
default, eliminating the pale hovering void that previously appeared when the
mask and drape used different elevation anchors. The drape renders above the
source photogrammetry within the exact polygon, so source cars, roofs and bare
soil do not bleed through the proposal surface.

Trees and benches are intentionally deferred to the final render for generated
green-space drapes. This keeps the navigable tile scene free of lightweight
procedural props and prevents furniture or trunks from crossing paths, water,
dams, spillways and fixed pads. The render prompt adds photorealistic planting
and furniture only on dry landscape areas with explicit circulation and water
setbacks. Ground-conditioning diagrams no longer draw bench dashes or pads;
they retain only fixed program anchors, so benches cannot bias circulation
before the path and water design is complete.

Three Gemini park-ground calls were used while isolating the reservoir issue.
No additional paid generation was used after the root cause moved to local
geometry/render integration. The newest night and isometric renders were
reviewed in the project gallery. Both preserved the reservoir and surrounding
circulation while adding mature planting and appropriately styled site detail
at architectural-visualization quality.

Reservoir-pass regression evidence:

- Frontend type check: passed.
- Frontend tests: 32 files, 278 tests passed.
- Frontend production build: passed (only the existing bundle-size warnings).
- Live browser QA: clean reservoir surface, exact parcel fit, no white stencil
  void, no source-ground bleed-through, and no standing props in water or on
  paths.

## Recurring planner public-realm coverage

The six public-realm archetypes emitted repeatedly by the master planner now
have explicit, geometry-first ground profiles rather than a generic catalog
fallback:

1. Neighborhood Park
2. Urban Pocket Park
3. Linear Park / Greenway
4. Formal Civic Plaza
5. Fountain / Decorative Water Feature
6. Stormwater Retention Pond

Each profile defines authoritative program geometry, material hierarchy,
archetype-specific prohibitions, canopy intent for the final render and a
matching furniture/planting recipe. The linear greenway's through-trail guide
uses the polygon's computed principal axis, so a rotated corridor retains an
end-to-end path aligned with its real geometry. Legacy `parking` plazas and
planner courtyards with development-like zone types are now eligible for the
same authored ground system.

Planner output now stamps these identities consistently rather than leaving
scenario-generated open space on the generic fallback. Environmental plans
assign `stormwater_retention_pond` to ponds and
`linear_park_greenway` to greenways. City Beautiful plans retain their formal
palette, assigning `fountain_water_feature` to water features and
`formal_civic_plaza` to plazas. Backend regression covers both scenarios so
the authored ground profile survives from planning through Generate 3D.

Circulation connectivity is now a cross-scenario invariant rather than a
single-plan observation. Every non-water public space emitted by all seven
current and legacy planner palettes carries at least one persisted
`park_access_points` gateway to the plan street/path network. Regression also
projects every gateway back to metres and proves it lies on its park boundary
and within 3.1 m of the emitted street/path ground, so a non-empty metadata
array cannot masquerade as connectivity. In the live
`Mixed Parks + Streets QA` district, all 14 non-water open spaces have network
gateways. The only open-space polygon without one is the pond waterbody itself;
its surrounding greenway owns the accessible perimeter circulation.

The atomic backend compiler is also exercised with all six archetypes in one
request. It preserves every park/plaza archetype identifier, assigns the shared
`park_kit` generator and one server timestamp, creates no Building records and
uses no image/model API. Frontend regression independently proves that each
compiled archetype immediately receives its local procedural ground while
trees and benches remain render-only.

Paid multi-park generation is capped at six sequential calls per explicit
batch. A large plan can no longer launch dozens of image requests from one
click; selected-park generation remains available as a one-call action.

Context and regression evidence for this extension:

- Backend plan geometry: 24/24 tests passed in the mounted
  `devplatform-backend` container, including park gateways and existing
  road/path boundary connectors.
- Frontend: 32 files, 289 tests passed.
- Frontend type check and production build passed; only the pre-existing Vite
  bundle-size warnings remain.

## Zero-credit Generate 3D fallback

LEGO Builder now gives every compiled park, plaza and courtyard an immediate
in-memory ground surface without calling an image model. The local surface uses
the same archetype profile, source signature, UV mapping, program guides,
fixed pads and master-plan `park_access_points` as the optional Gemini
orthophoto. Upgrading a hero park therefore changes material fidelity without
changing its geometry.

The deterministic surface uses a muted Google-tiles palette, subtle turf or
paver variation and a gateway-derived path hierarchy. Three or more entrances
form a smooth irregular perimeter walk close to the parcel edge; two entrances
receive one continuous route; linear greenways retain their principal-axis
trail; reservoir and stormwater entrances terminate at the authoritative
shoreline/maintenance loop rather than crossing water.

Temporary cone/box park-kit placeholders are no longer shown in the Google
scene. Trees and benches are always render-finishing elements. Playground and
pavilion pads remain visible in the ground design, and those structures appear
in live 3D only when a real GLB exists in the park-kit manifest. Specialty
geometry such as the Japanese-garden bridge remains eligible because it is an
explicit part of the archetype rather than decorative scatter.

The Community 3D confirmation now states this division of labor before the
user compiles the scene. A dedicated render-prompt regression also prevents a
return to the older contradictory instruction that treated tree positions or
visible vegetation as authoritative proposal geometry. Only fixed ground and
program geometry is locked; Render composes planting and furniture afterward
with path, crossing, sightline, water, dam and spillway clearances.

Live evidence in `Mixed Parks + Streets QA`:

- 83 compiled parks/courtyards received deterministic surfaces; only Park 4
  retained its higher-fidelity AI drape.
- 95 compiled streets retained their procedural cross-sections and connected
  grid.
- Clean-3D inspection confirmed the surfaces appear without starting any paid
  generation. The first inspection exposed pale placeholder objects; the
  manifest gate removed them before handoff.

Regression evidence for this extension:

- Frontend focused tests: 38 passed.
- Frontend full suite: 32 files, 290 tests passed.
- Frontend type check: passed.
- Frontend production build: passed with only the existing bundle-size
  warnings.

## Terrain-mesh and depth-order hardening

Concave public-realm parcels no longer create the large triangular
"starbursts" seen during close Google Tiles inspection. The former terrain
grid shrank complete parcel rings toward an arithmetic centroid, which can lie
outside a concave polygon. The replacement keeps the authoritative boundary
and adds only per-triangle centroids, so every terrain-sampling vertex remains
inside its source face.

Boundary probes use wider object-filter sampling for compiled ground, while
interior probes use the nearest trusted boundary sample to reject isolated
roof and canopy hits. Unrefined root-tile elevations remain guarded out. The
surface schedule now starts within six seconds instead of leaving some zones
visibly unresolved for roughly half a minute.

Prepared community envelopes also changed their depth semantics. Once the
site-boundary mask owns source-tile replacement, parks and streets write and
respect normal scene depth; they can no longer paint across generated building
facades. Standalone park drapes keep overlay semantics so source cars and bare
soil cannot punch through the proposal.

The reservoir trial exposed one final near-coincident-surface failure: its
valid textured mesh was present but disappeared into the noisy photogrammetry
skin at the earlier 0.12 m clearance. A 0.32 m curb-scale clearance is now used
for flat proposal ground, with the outline at 0.40 m. Live aerial and close
inspection confirmed the reservoir remains visible without the former
metre-scale hovering effect.

The live mixed project still exposes a deliberate concurrent-work seam:
public-realm compile coverage is 178/178 and all 96 currently supported
building zones now have saved recipes. The former 20-stack viewer cap was
replaced by an explicit 96-stack detailed-render budget, and live logs confirm
that all 96 placeable stacks mount. The remaining 646 zones require real module
families for `vernacular_courtyard_housing`, `new_york_walk_up_tenement`,
`new_york_corner_bodega`, and `contemporary_civic`. Building-family coverage
beyond this seam is owned by the parallel building-archetype work and was not
faked with unrelated substitutions here.

Regression evidence for the terrain/depth hardening:

- Frontend full suite after the scalable mixed-scene seam: 36 files, 306 tests
  passed.
- Backend LEGO assembly, site-zone and plan-geometry regression: 61 tests
  passed in the mounted `devplatform-backend` container.
- Frontend type check: passed as part of the production build.
- Frontend production build: passed; only the existing bundle-size and mixed
  static/dynamic import warnings remain.
- Live reservoir QA: generated water, shoreline, paths and dry landscape are
  visible in the exact parcel at aerial and close oblique scales.
- Live mixed-plan QA: public-realm meshes remain inside their parcels and no
  longer draw over generated building facades.
- Live mixed-plan compile: 96 building records, 96 compiled building zones,
  83/83 compiled park/courtyard zones, and 95/95 compiled street zones; the
  atomic place-community request returned 200.

## Existing-context connection proof

The Economic plan contains five drivable access stubs and four multi-use-path
stubs tagged `context_connection=true`. These are not decorative edge arrows:
the street graph carries their exact boundary endpoint into the emitted
centerline and right-of-way geometry, counts the joined anchors, and gives
context connectivity its own deterministic plan-evaluation score.

The live project was checked against the exact Calgary road and pathway
GeoJSON cached for its Urban DNA run at `2026-07-18 02:14 UTC`. PostGIS metric
distance checks in EPSG:32612 found:

- 9/9 connection polygons touch the authoritative site-boundary zone.
- 8/9 intersect a cached existing road/path centreline.
- The remaining road connection is 0.99 m from its nearest cached corridor.
- Maximum connection-to-context distance: 0.99 m.

This proves the generated road and pathway surfaces reach real surrounding
corridors in the current plan. The final-render prompt separately treats these
stubs as mandatory seams: aligned centreline, grade, curb/path edge and usable
surface continuity may not be capped by lawn, planting, a building or a curb.

## District-scale building LOD seam

The former `96` detailed-stack guard no longer makes later supported buildings
fall back to colored plan polygons. Camera-nearest stacks retain their complete
module GLBs, physical glazing LOD and terrain raycasts. Every additional saved
recipe receives a local exact-footprint prism at its assembled height and
stored/fallback terrain elevation. These lightweight massing proxies remain
valid 3D/render-conditioning geometry and swap to detailed stacks as the camera
moves closer.

The proxy triangulates the real concave parcel ring rather than its bounding
rectangle, so L/U/courtyard footprints do not overhang parks, paths or adjacent
lots. The detailed and simplified tiers are deterministic, mutually exclusive,
and exhaustive: every renderable recipe is present in exactly one tier.

No paid API call was used for the context audit or LOD implementation.

## Render capture tile-readiness gate

A paid globe render no longer captures immediately after two browser frames.
Before the screenshot is taken, City Prompt now waits for the active Google
tile renderer to remain idle for 600 ms. Any new tile-load event caused by
camera movement cancels and restarts that stable window.

The wait has an eight-second safety ceiling. If detailed tiles do not settle,
the render panel returns to a retryable state with an explicit message to hold
the view still; no image-generation request is started and no render credits
are consumed. While the preflight is active, the panel identifies the phase as
`Preparing detailed Google tiles` rather than implying that paid rendering has
already begun.

Verification evidence:

- Tile readiness tests cover initially idle tiles, load restarts after camera
  movement, timeout cleanup, and an unavailable renderer: 4/4 passed.
- Current frontend full suite: 37 files, 310 tests passed.
- Frontend type check and production build passed.
- The live mixed-project render panel opened after a full reload with all 96
  placed building stacks available as geometry conditioning and no runtime
  errors.
- No paid preview or park-ground call was made during this verification.

## Generated-building district LOD and stale-asset fallback

The alternate generated-GLB viewer no longer stops after the first 20
buildings. It now uses a camera-relative district LOD: the nearest 20 completed
buildings receive their full GLBs, while every other completed building keeps
an exact-footprint, terrain-seated massing representation at its authoritative
height. The two tiers are exhaustive and mutually exclusive, and re-partition
as the camera moves.

The live `Tester` project provided a larger proof case with 40 completed
building records. All 40 mounted: 20 detailed GLBs and 20 massing proxies. Its
records reference three shared asset URLs. Two assets are present, while the
12-building Brutalist shared URL is stale. City Prompt now sends one
metadata-only `HEAD` request per distinct URL before mounting a GLB; a definite
404 degrades every affected building to exact-footprint massing without
creating holes or a repeated GLTF-loader error storm. Network failures and
legacy servers without HEAD support remain backward-compatible and still let
the normal model loader/fallback boundary decide.

Verification evidence:

- Backend file HEAD endpoint: valid/stale/valid shared assets returned
  `200 / 404 / 200`, each with zero response-body bytes.
- Backend focused route tests: 2/2 passed.
- Frontend LOD, massing and asset-availability focused tests: 11/11 passed.
- Current frontend full suite: 39 files, 315 tests passed.
- Frontend type check and production build passed; 3,351 modules transformed.
- Live reload: one HEAD request for each of the three distinct shared URLs,
  all 40 building representations mounted, and no new stale-GLB loader warning.
- No paid API call was used for this verification.

## Reservoir render benchmark

The reservoir trial now contains ten saved render variants spanning
documentary, site-plan, isometric and night treatments. The latest night
variant establishes the desired render-stage quality bar: the reservoir and
perimeter circulation remain legible, contextual city lighting is coherent,
and added planting, furniture and atmosphere are resolved photographically.
This supports the intended separation of concerns: editable Google Tiles 3D
keeps authoritative water, shoreline, paths and terrain clean, while the final
render stage supplies the richer scene dressing.

## Zero-hole mixed-community building coverage

The mixed-plan compiler now persists an exact-footprint `plannedMassing`
Building for any planner building whose detailed LEGO family has not yet been
imported. This is an explicit interim representation, not a substitute
architectural family: it carries the planner's footprint, floor count and
authoritative height, participates in the same terrain-seating path as detailed
stacks, and is replaced in place when the real family recipe becomes available.
The linked Building ID also enters the existing modeled-zone handshake, so its
colored planning prism is suppressed without creating a gap in the render
conditioning geometry.

Live evidence from `Mixed Parks + Streets QA` on 2026-07-18:

- 742/742 building zones have linked Building records; 0 are unlinked.
- 96 zones use detailed `lego_assembly`; 646 use family-pending
  `planned_massing`.
- 646/646 fallback footprints are PostGIS-equal to their source zone geometry;
  0 mismatches.
- 83/83 park zones and 95/95 street zones remain compiled.
- The browser viewer reported all 742 representations mounted in one scene:
  96 detailed and 646 planned-family massing.
- The atomic 646-building local compile returned HTTP 200 in 6.48 seconds.
- Clean-plan-overlay visual QA showed the district forms seated against the
  Google photogrammetry terrain with no missing colored building polygons.
- Frontend: 39 files / 318 tests passed; TypeScript and the production build
  passed with 3,351 modules transformed.
- Backend LEGO assembly suite: 30/30 tests passed.
- No paid image-generation or rendering API call was used.

## Render-only landscape-dressing invariant

The final audit found a second tree path in the street-detail layer after park
trees and benches had already been deferred. That path is now removed as well:
the editable Google Tiles scene carries only terrain-seated park ground,
authoritative paths/water/fixed pads, engineered street cross-sections and
genuine fixed-structure assets. It can no longer instantiate procedural street
trees, cone trees, box benches or placeholder playground/pavilion objects.

The render handoff was corrected at the same time. Street prompts no longer
claim that a non-existent live tree row must be preserved. Profiles with real
planting bands instead ask the final render for varied mature trees only inside
those bands, with clear crossings, driveways, cycle tracks, sidewalks and
sight triangles. Sections without planting bands explicitly prohibit invented
trees on circulation surfaces.

Fixed authored structures remain independent from scene dressing. In
particular, a Japanese-garden bridge now mounts and terrain-samples even when
its recipe's trees and benches have all been correctly filtered out. The old
all-or-nothing 120-park prop cutoff was replaced by content-aware selection, so
a large district cannot silently discard a real fixed structure merely because
it contains many parks.

Verification evidence:

- Six recurring master-planner park/plaza profiles retain authoritative guides
  and constraints; the expanded focused public-realm matrix passed 98/98.
- Render-only park/street dressing, fixed-structure retention and street prompt
  rules have direct regression assertions.
- Frontend full suite: 39 files / 321 tests passed.
- TypeScript and production build passed; 3,349 modules transformed.
- Removing the live EZ-tree dependency reduced the main production bundle from
  8.55 MB to 4.58 MB (gzip 4.06 MB to 1.08 MB) in the current build.
- No-credit live reloads preserved the clean reservoir surface and mounted all
  742 mixed-district building representations; neither page emitted a runtime
  error, and the reservoir render count remained unchanged at 10.
- No paid API call was used.

## Authoritative park geometry in final renders

The successful artistic reservoir variants exposed one remaining fidelity
risk: the whole-plan conditioning diagram records which parcel is a park, but
not the park's internal shoreline, loop trail, field, fountain, bridge or dam
geometry. Final mixed-scene renders now attach local, to-scale park diagrams
ahead of appearance cards. These diagrams are geometry-only constraints; the
source Google Tiles capture and archetype photographs continue to control
materials, atmosphere and visual style.

Reference selection is bounded and deterministic. A one-park reservoir view
attaches exactly its reservoir diagram. A district plan attaches at most four
visible diagrams, prioritizing reservoirs and stormwater infrastructure, then
Japanese gardens, sports fields, plazas/fountains and linear greenways. This
keeps GPT Image 2 inside its 15-reference limit and prevents an 83-park plan
from crowding out building and style references. The whole-plan diagram remains
first when present; internal park diagrams follow it, and style cards follow
those. The same ordering applies to the opt-in per-zone render path.

This addition is local canvas work and makes no image-generation call.

Verification evidence on 2026-07-18:

- Deterministic selection and the four-reference ceiling have direct tests;
  reservoirs rank first and parks without an authoritative internal guide are
  excluded.
- Frontend full suite: 39 files / 322 tests passed.
- TypeScript and production build passed; 3,349 modules transformed.
- A no-credit live reservoir reload retained the exact water/shoreline/trail
  surface, showed 10 saved renders, and emitted no runtime error.
- No paid API call was used.

## One mixed-community compiler from both user entry points

The Render panel's `Generate Community 3D` action had retained the legacy
building-only Meshy queue even after LEGO Builder moved to the atomic mixed
compiler. That was both a behavioural mismatch and a serious cost risk: the
old confirmation advertised roughly 20 Meshy credits for every building in a
plan. The action now uses the same shared zone derivation and atomic backend
transaction as LEGO Builder.

Both entry points now resolve the same archetype, geographic footprint, floor
count, footprint profile and family. A supported family produces the detailed
modular GLB stack. A missing family is an expected 422 and produces an honest
exact-footprint planned mass. Parks and engineered street/path sections enter
the same transaction. Any other modular-planning failure aborts before the
save, so the scene cannot be partially compiled or silently downgraded.

The confirmation explicitly states that the operation uses no external
model-generation credits. Optional AI park ground drapes remain a separate,
bounded and clearly labelled paid action.

The old Meshy route also required a saved site boundary for every generation.
That restriction is now scoped correctly: AI-generated master plans still
require the persisted boundary that authored them and are blocked if it is
missing or stale, while persisted hand-drawn buildings, parks and streets can
compile their own footprints without inventing a redundant boundary. The
reservoir trial therefore offers Community 3D directly as one park.

Verification evidence on 2026-07-18:

- Shared-compiler tests cover one detailed building, one family-pending mass,
  one park and one street in a single request, plus unexpected-planner and
  invalid-footprint aborts before persistence.
- The complete frontend suite passed: 43 files / 337 tests.
- TypeScript and the production build passed; 3,352 modules transformed.
- The current-worktree backend LEGO assembly suite passed 30/30 in an
  ephemeral container mounted from `PlaygroundNEW` (not the older running
  backend checkout).
- Live mixed-plan confirmation reported exactly 742 buildings, 83 parks and
  95 streets and the no-external-credit policy. The confirmation was cancelled
  without sending a compile or render request.
- Live reservoir confirmation reported 0 buildings, 1 park and 0 streets even
  though that manual trial has no site-boundary zone. Confirming it sent one
  atomic `place-community` request, which returned HTTP 200; no render,
  per-zone generation or external model request was emitted and Celery handled
  zero tasks.
- The reservoir zone now persists `community_3d.kind = park`,
  `generator = park_kit` and `state = compiled`. A clean reload consequently
  labels the action `Rebuild Community 3D (1 zone)` rather than presenting an
  already-built park as unfinished. Partially compiled plans use `Complete`;
  new plans use `Generate`.
- `Complete` now scopes its atomic transaction to unfinished zones only, so it
  does not re-plan or rewrite already-compiled buildings, parks or streets.
  `Generate` and explicit `Rebuild` continue to own the full community; the
  latter is the intentional upgrade path when a detailed module family lands.
- The reservoir retained its exact water, shoreline and path geometry after
  compilation, and all 10 saved renders remained unchanged.
- No paid API call was used.

## Exact render-call disclosure

The current-view renderer deliberately uses one bounded A/B pair rather than
automatically switching a large mixed plan into per-zone image generation.
The Render button now states the exact request count before work begins: two
image calls for the normal A/B pair. Eligible artistic styles expose an
optional high-fidelity pass that shares one full-frame restyle across both
previews, so the disclosed total becomes three rather than incorrectly
describing the option as a generic `2x` cost.

Verification evidence on 2026-07-18:

- Cost arithmetic has direct tests for the two-call comparison, the one-call
  shared restyle, and invalid/negative preview counts.
- Live reservoir UI inspection showed `2 image calls`, then `3 image calls`
  only after Watercolour and High fidelity were selected.
- The production render action was not clicked; the saved-render count stayed
  at 10 and no image API request was sent.
- Frontend full suite: 43 files / 337 tests passed. TypeScript and the
  production build passed with 3,352 modules transformed.

## District-scale render conditioning

Single-shot cost control does not by itself make a 900-zone render reliable:
the former prompt still repeated a long description for every polygon,
including zones wholly outside the captured image. The render pipeline now
performs a conservative screen-frustum test before labeling, masking and
prompt construction. Off-screen zones are excluded; partially visible and
frame-enclosing polygons remain eligible.

Views with at most 80 visible zones retain the proven per-zone schema. Larger
views switch to a district schema capped at 32 instruction lines that groups repeated archetype and
program families while retaining the exact total inventory, scale ranges,
screen regions, context-connection counts and authored park/street ground
truth. The screenshot, individual polygon mask, visible 3D proposal geometry
and whole-plan diagram remain authoritative, so grouping instructions cannot
merge footprints, fill courtyards, move parks or simplify circulation.
If an unusually varied plan exceeds 32 groups, public realm and context
connections are prioritized and the final line records the exact overflow
group/zone inventory with representative labels, group-consistent fills and
exact mask/3D geometry fallback.

Text labels are now independently capped at 80 for district views. Every
visible zone still keeps its dashed polygon, fill, mask and 3D geometry, so the
budget removes only overlapping text—not proposal geometry. The selector first
keeps one deterministic representative per program group, prioritizing context
connections, parks/streets, custom programs and modeled buildings, then fills
remaining slots by priority and footprint area. Small scenes remain fully
labeled, preserving the successful reservoir workflow unchanged.

Signature building identity is also preserved when a mixed district moves to
the grouped schema. The bounded building-feature allowance carries the
distinct titles and material cues for Vernacular Courtyard Housing, New York
Walk-Up Tenement, New York Corner Bodega and Contemporary Civic, including
internal gardens, cast-iron fire escapes, the corrugated metal awning and the
glass curtain wall. This does not claim detailed 3D family completion: those
four compiler manifests and live model-library rows remain the explicit
building-workstream dependency.

Verification evidence on 2026-07-18:

- A synthetic 110-zone mixed scene retained its exact `90 buildings / 20
  parks` inventory, collapsed to two repeated program groups and stayed below
  20,000 prompt characters.
- A 100-zone worst case with 100 uniquely named programs emitted exactly 32
  bounded lines, retained the overflow inventory and stayed below 50,000
  prompt characters.
- Small scenes still emit the detailed per-zone schema used by the successful
  reservoir renders.
- Frame-intersection tests cover on-screen, crossing, frame-enclosing,
  margin-visible, wholly off-screen and invalid projected bounds.
- Label-budget tests cover small-scene completeness, per-group representation,
  priority under overflow, determinism and the hard cap.
- Frontend full suite: 45 files / 348 tests passed; TypeScript and the
  production build passed with 3,354 modules transformed.
- Backend planner, geometry and LEGO combined suite: 75/75 tests passed,
  including scenario-specific public-realm identities and the atomic
  six-archetype compile contract. The LEGO assembly subset remains 31/31.
- No image-generation call was used.

## Inspectable district camera framing

Live QA exposed a separate usability failure at the Google Tiles stage: the
`Focus plan` action left the 1.0 x 1.1 km mixed district at roughly 13-20% of
the viewport, too small to inspect ground contact or public-realm geometry.
The stored site boundary and proposal content have matching extents, proving
this was camera math rather than an outlying polygon.

The framing seed now derives camera height from the actual 75-degree
perspective frustum, 60-degree pitch-from-nadir, target frame fraction and
oblique ground foreshortening. It retains a 120 m minimum for small hero sites
such as the reservoir and a 20 km safety maximum for regional plans. A live
HMR retest of `Mixed Parks + Streets QA` moved the same district to roughly
half the viewport. With `Clean 3D` enabled, prepared-site ground,
exact-footprint masses, streets and park parcels remained coincident with the
surrounding Google context; no detached park card or roof-level ground was
visible at that scale. The estimator has monotonicity, kilometre-scale and
small-site regression coverage, and required no model/image API call.

The closer framing also exposed an overly olive prepared-site wash that made
authored parks disappear into the residual parcel. The preparation texture is
now a desaturated earth/retained-ground/aggregate mosaic with a smaller green
share and trilinear mip filtering. A second live `Clean 3D` inspection showed
the redevelopment parcel reading as neutral residual ground while streets,
parks and building footprints remained legible and aligned to the Google
photogrammetry. Texture tests enforce deterministic variation, bounded
channel means, low channel spread and generated mipmaps so this cannot regress
back to a flat planning slab.

The two newest saved reservoir night variants were also reviewed without
starting another generation. Both retain a clear impoundment, continuous
perimeter circulation and coherent context; the B variant has the clearest
reservoir geometry and the A variant the softer atmospheric presentation.
They confirm the intended division of responsibility: Google Tiles carries
the accurate fixed park geometry, while Render adds vegetation, furniture,
people, lighting and presentation finish.

## Reservoir Clean 3D and cache-stability recheck

A fresh live browser pass reopened the reservoir project, switched to Select,
focused the authored parcel and enabled `Clean 3D`. The saved orthographic
ground drape remained aligned to the vacant lot and showed the exact open-water
rectangle, continuous shoreline loop, dry-land paths and dam geometry. No
standing tree, bench or loose-furniture geometry was present; no park surface
hovered over a building or escaped the polygon. The project still contained
10 saved renders and this verification started no generation request.

The audit also verified that the saved ground texture's source signature is
current. Its cache key is now canonical across the two normal polygon-ring
serializations: the Site Zone API's open ring and GeoJSON/PostGIS's equivalent
ring with the first vertex repeated at the end. This prevents a harmless data
round-trip from discarding a valid paid drape or asking the user to regenerate
it. A direct regression test proves open and closed rings share a signature,
while material coordinate, archetype, variant and access changes still
invalidate the cache as intended.

- Frontend full suite: 45 files / 349 tests passed.
- TypeScript and production build passed; 3,354 modules transformed.
- No image, model or other paid generation call was used.

## Same-geography park archetype scale and render trial

Five isolated projects now exercise distinct park programs on the exact same
11,096.2 m2 downtown parcel. The repeatable fixture is
`tools/park_trials/seed_same_geography.sql`; it copies only the source polygon
and its grounded terrain datum, then marks each zone as a compiled Community
3D park. It does not copy an AI drape or render history.

- `0d73b4ea-31ea-48bf-8590-f1862f950101`: regulation sports fields.
- `0d73b4ea-31ea-48bf-8590-f1862f950102`: urban forest.
- `0d73b4ea-31ea-48bf-8590-f1862f950103`: botanical garden.
- `0d73b4ea-31ea-48bf-8590-f1862f950104`: Japanese stroll garden.
- `0d73b4ea-31ea-48bf-8590-f1862f950105`: nature-play landscape.

All fixed programs now resolve in real-world metres rather than stretching to
their parcel. The sports trial contains one 100 x 64 m football pitch and
three 36.58 x 18.29 m tennis safety envelopes, each with a 23.77 x 10.97 m
doubles court and correctly derived service/singles lines. The Japanese trial
contains a 34 x 20 m pond, 22 x 14 m raked-gravel court and 9 x 2.2 m arched
timber bridge. Botanical beds, the conservatory pad, forest clearings,
nature-play safety surfaces, the water rill and every circulation loop also
have fixed metre dimensions or widths.

Live Google Tiles QA verified each design remains inside the irregular parcel
and seated on its stored terrain. Small-site framing now targets about 70% of
the viewport with a 70 m safety floor, replacing the district-wide 55% / 120 m
view that hid low park structures. Procedural materials are archetype-specific:
sports mowing/court systems, woodland leaf litter, exact botanical collection
rooms with clustered planting texture and a granular 2.8 m loop, moss/water/
raked gravel for the Japanese garden, and meadow/engineered-fibre/water-play
materials for nature play. Trees and benches remain render-only so they cannot
land on paths, water or fixed safety surfaces. A live EZ-Tree experiment was
visually rejected and removed because its distant foliage read as skeletal
against Google photogrammetry. The interactive sports scene mounts only
conflict-free fixed infrastructure: regulation goals, tennis nets, low
bleachers and field lighting. The Japanese bridge and botanical conservatory
are similarly fixed live structures rather than flat texture marks.

A controlled A/B photorealistic render was generated from the verified sports
tile view. Both outputs retained the single football pitch, all three tennis
courts, the parcel boundary and the existing Google city context. Four
botanical render trials followed: the first photoreal pair invented a fountain
and parterre, while the geometry-locked documentary pair removed the fountain
and retained a compact conservatory plus three collection rooms. The render
prompt now places park topology before planting style and forbids reference
images from authorizing new features.

Two optional Gemini botanical ground-drape trials improved material richness
but were rejected because both still redesigned an authored collection room as
a circular parterre. The conflicting generic instruction to invent a path
network has been removed and paid drapes can now be regenerated explicitly,
but the botanical profile was advanced to v5 so both inaccurate drapes are
ignored without deleting their files. The live scene therefore uses the exact
deterministic v5 material instead of accepting a prettier topology error. Paid
work in this same-geography trial totals eight disclosed image calls: two sports
renders, four botanical renders and two botanical ground-drape evaluations. No
model-generation call was used.

- Final frontend suite: 45 files / 362 tests passed.
- Final park/camera-focused regression: 3 files / 77 tests passed.
- Final TypeScript and production build passed; 3,354 modules transformed.

## Settled mixed-district Clean 3D acceptance recheck

A fresh live pass reopened the authoritative 920-zone mixed district, focused
the full plan, switched to Clean 3D and enabled the compiled building layer.
The Google stream settled successfully after the district-scale LOD load; the
temporary `Loading tiles...` indicator cleared without a timeout or page
reload. The final scene retained all streets and parks at ground level and all
742 building representations, with the established honest split of 96
detailed assemblies and 646 planned-family massing placeholders.

The pass exposed scene-light saturation on the residual prepared-site mesh.
That material is now unlit and tone-map independent, and its deterministic
palette has been shifted from vegetation-heavy olive to neutral retained
earth/aggregate with only sparse seeded-cover variation. A live HMR recheck
showed the residual parcel as neutral taupe while authored courtyards and parks
remained distinctly green. No geometry, tile mask, park layout or street
cross-section changed.

The four signature building ids are present in the catalog and reference-image
library, but an authoritative database audit still found no live GLB cache row
for `vernacular_courtyard_housing`, `new_york_walk_up_tenement`,
`new_york_corner_bodega` or `contemporary_civic`. They therefore remain honest
planned-family massing until the parallel building workstream supplies exact
models; no lookalike was substituted.

- Frontend full suite: 45 files / 349 tests passed.
- TypeScript and production build passed; 3,354 modules transformed.
- Backend planner, placement, curvilinear and LEGO combined suite remains
  95/95 passed.
- No image, model or other paid generation call was used.

## Mixed-district render preflight and optional spend

The live Render panel was opened against the full `Mixed Parks + Streets QA`
scene without starting a render. It reported `Rebuild Community 3D (920
zones)`, matching the authoritative 742-building + 83-park + 95-street
inventory, kept `Render with 3D models (geometry-accurate)` enabled, and
disclosed exactly `2 image calls` for the current-view A/B previews.

The former park-material button still read like required missing work even
though every compiled park already has a complete deterministic procedural
surface. Its user-facing label, tooltip and progress messages now identify
Gemini drapes as optional material upgrades. The six-call safety cap remains,
but the panel explicitly states that these calls are not required for
Community 3D or Render and that any un-upgraded parks continue using complete
procedural grounds. A live HMR recheck showed `Optional AI Park Grounds (6
calls)` beside the two-call render disclosure; neither control was activated.

- Frontend full suite: 45 files / 349 tests passed.
- TypeScript and production build passed; 3,354 modules transformed.
- Mixed project saved-render count remained 0; no paid call was used.

## Metric collision invariant for public realm

A direct PostGIS audit of the authoritative mixed project tested every
proposal role pair in a metric CRS. It found zero material building/park,
building/street, building/building, park/park, park/street or street/street
intersections. The largest park/street contact artifact was only 0.1 m²,
below the 1 m² material-collision tolerance and consistent with a shared
boundary seam.

The generator's validation contract now matches that live evidence. Building
masses are unioned in site-local metric space and checked against streets,
every authored park or water polygon, every generated courtyard and each
other. Shared edges remain legal; any overlap greater than 1 m² emits an
explicit error before the colored plan is accepted as 3D-ready. This closes a
regression gap where only building/street collisions were previously checked,
and prevents plan-space overlap from presenting later as a park or reservoir
hovering through a building.

- Focused collision and full-generation checks: 3/3 passed.
- Backend planner, placement, curvilinear and LEGO combined suite: 95/95
  passed.
- No image, model or other paid generation call was used.

## Family-aware community rebuild preflight

The authoritative building inventory was re-audited by exact archetype id:
356 `vernacular_courtyard_housing`, 168 `new_york_walk_up_tenement`, 121
`new_york_corner_bodega`, 96 `contemporary_midrise_residential` and one
`contemporary_civic`. The first, second, third and fifth groups account for all
646 honest planned-family masses; the supported contemporary-midrise group
accounts for all 96 detailed assemblies.

Community compilation now probes each exact archetype once before issuing
per-footprint module plans. An explicit "no module family matches this
archetype" response classifies the remaining buildings of that same archetype
as exact-footprint massing without repeating the identical request hundreds of
times. For this district, rebuilding while the four families are absent drops
from 742 planning requests to approximately 100: all 96 supported footprints
plus one probe for each unavailable family. This changes no persistence or
geometry and makes no paid call.

The optimization is deliberately narrow. A 422 caused by footprint fit rather
than a missing family does not classify sibling buildings; every remaining
footprint is still planned independently and can upgrade successfully. Tests
cover both the four-family deduplication and the size-sensitive sibling case.

- Frontend full suite: 45 files / 351 tests passed.
- TypeScript and production build passed; 3,354 modules transformed.
- No image, model or other paid generation call was used.
