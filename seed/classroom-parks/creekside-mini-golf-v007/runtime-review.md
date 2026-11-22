# Runtime integration review — mini_golf_course / student_creekside_mini_golf_v1

**Nothing in this review was run in the app.** Creekside Mini Golf was built and checked offline only, so every
applicable gate and matrix row is NOT TESTED. Building, street and bridge rows are N/A with a reason. Offline
evidence is listed at the end and is not a runtime pass. It follows `docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md` and
`docs/ARCHETYPE_RUNTIME_INTEGRATION.md` (version 2026-09-24).

## Candidate and scope

- Kind: park or open space: fixed native assembly (native_park_v2)
- Archetype ID and exact variant ID: `mini_golf_course` / `student_creekside_mini_golf_v1` (Creekside Mini Golf); layout `student_creekside_mini_golf_v1--native-v1`
- Model SHA-256 or procedural recipe ID/revision/hash: assembly `c989175c73f3cb0d1c554ba672694ee4e9785e7fedf1ae418e1c695a04fb6179`; content revision `6c42838d5da4766390a9844049be150ae74d26af9a7d1e3b498163daa64b28d3`
- Runtime source commit and integration-checklist version: registered on `claude/tender-albattani-fsnp50`; checklist 2026-09-24
- Reviewer, date, project URL, viewport/device/input: none; not run
- Vacant test site, protected reference, disposable test project: not set up
- Mixed-scene project and separate oversized-candidate project, if applicable: not set up
- Supported plot dimensions, axes/base datum, reshape/repetition behavior: native 48 x 40 m; occupied 48 x 40 m; `authored_footprint`, never stretched
- Authored storey programme: N/A: park
- Supported terrain modes and connection capabilities: prepared level ground only; the assembly owns its ground; one entrance at the south edge
- Public-realm detail: metric plant height/footprint, paving scale, instance/texture budgets, and native close/aerial evidence: no textures; 549,862 rendered triangles, 457 mesh instances; renders under `artifacts/park-batch/minigolf/` (ignored, reproducible) and `docs/park-batch-1/review.jpg`
- Replacement furniture: N/A: no replacement furniture
- Vegetation: plants from the shared foliage generator, placed as instances; canopies stay inside the site and plant origins stay clear of every route (offline check)
- Hardscape trees: N/A: no tree wells or grates
- Sports: N/A
- Reference-image fidelity: exact image hashes, observed amenity cues, borrowed/inferred details, native before/after views and separately exported reusable amenity modules: original concept after `frontend/public/archetypes/openspaces/mini-golf-putting-course/variant_3.png` and its oblique and plan views; not traced
- Native park seams and raised/cycle access: one fixed assembly, no seams; level routes only; offline route rays from the entrance pass
- Street asset handoff: N/A
- Asset review status and separate publication/activation status: builder visual review only; no independent review; status `pilot`, runtime `not_tested`; publication not authorized
- Model Library storage check, configured bucket and result (building GLBs): N/A
- Fresh installation: exact binding/recipe/module seed, byte readback, conflict preservation and disposable DB/bucket evidence: offline only: `scripts/register_park_batch1.py` refuses changed content; the generator rebuilds the registered bytes
- Evidence manifest location and hashes; durable shared location for delivery: `seed/classroom-parks/creekside-mini-golf-v007` (recipe, assembly, preview, geometry verification)

## Gates

For a new exact variant, check both the backend trusted parent/child inventory
and generated native-model reporting facts before the browser compile. A picker
card or successful `/plan` response alone does not prove `/place-community` accepts it.
Verify the actual visible model and camera before saving capture evidence; a new
reshape-panel title can coexist with a previously selected native mesh. Record any
explicit re-selection needed, and exclude stale-camera drafts from delivery.

For context removal from merged-material GLBs, check complete functional assemblies
against the authoring recipe as well as retained bounds/counts. A touching kilometre
of quay can weld to a bridge footway; removing vehicle bodies can leave their glass
behind. Prove whole decks/footways, original closed end faces and complete prop removal.
Use the same pinned ownership revision in hover preview, placed geometry and saved
identity. A compact bounding box or matching triangle total alone is insufficient.

Use PASS / FAIL / NOT TESTED / N/A. Attach evidence to each PASS and a reason
to each N/A. Use the shared checklist for each gate's full meaning.

| Gate | Status | Evidence / limitation / next action |
| --- | --- | --- |
| C1 Exact identity | NOT TESTED | Exact layout, content revision and model hash registered offline; not checked in the app |
| C2 Dimensions and transformations | NOT TESTED | Fixed native assembly at true size; the parcel must be at least the occupied footprint |
| C3 Full footprint ground support | NOT TESTED | Prepared level ground only; record the result on natural ground (expected: guidance to prepare the site) |
| C4 Freshness and late results | NOT TESTED |  |
| C5 Pedestrian continuity and public-road access for vehicle streets | NOT TESTED | Entrance/park path; street endpoint, marker, real-road match, clear route |
| C6 Edit / Undo / save / reopen | NOT TESTED |  |
| C7 Failure and recovery | NOT TESTED |  |
| C8 Low/aerial views, exact capture and any AI-image comparison | NOT TESTED | Same-camera source/output; count, outline, location, scale, access, material/function, additions; pass/review/fallback |
| C9 Student controls and supported inputs | NOT TESTED |  |

For fixed-native buildings, record Q/E and rotation-field evidence at the actual
site latitude: metre dimensions/right angles preserved, exact model retained
after save/reopen. A displayed angle alone does not prove detailed-model fit.
| B1 Native placement | N/A | N/A: park, not a building |
| B2 Measured entrance evidence | N/A | N/A: park, not a building |
| B3 Entrance authoring | N/A | N/A: park, not a building |
| B4 Approach and setback recovery | N/A | N/A: park, not a building |
| B5 Foundation/stair/access design review | N/A | N/A: park, not a building |
| S1 Metric section | N/A | N/A: park, not a street |
| S2 Route and junction topology | N/A | N/A: park, not a street |
| S3 Shared grade and public connection | N/A | N/A: park, not a street |
| S4 Clearance and target identity | N/A | N/A: park, not a street |
| P1 Exact program and rigid amenities | NOT TESTED | Exact native program; offline checks list every module and route |
| P2 Shared park terrain | NOT TESTED | The assembly owns its ground; check tile and prepared-ground cut-outs around it |
| P3 Automatic remeasurement | NOT TESTED | Not run |
| P4 Park access and grade review | NOT TESTED | Walk the routes from the entrance in the app; offline route rays pass |

## Bounded live matrix

Record actual measurements, steps, and relevant screenshots/API readback.
Mark type-specific gates N/A with a reason; keep applicable unrun cases open.

| Case | Status | Observation and evidence |
| --- | --- | --- |
| Level site; low views from multiple sides | NOT TESTED |  |
| Irregular site between mapped roads; natural and prepared modes; exposed site edge | NOT TESTED | Record ordinary-control boundary draw, approximate vs surveyed status, contained objects, pad edge and capture consequence. |
| Direct selection where an authored zone overlaps prepared ground | NOT TESTED | After reload, select the contained zone from the canvas, select the site elsewhere, then reselect the zone; confirm its edit handles and settings. |
| Proposed off-site public-road endpoint; Undo/Redo/reload and low junction grade | N/A | N/A: street endpoint |
| Fixed street bend through ordinary controls | N/A | N/A: street route |
| Long repeatable route and exact edit datum | N/A | N/A: street route |
| Repeated street travel-surface ownership | N/A | N/A: street surface |
| X-to-T and T-to-X recovery | N/A | N/A: street junctions |
| Narrow pedestrian section and bend control retention | N/A | N/A: street section |
| Nonexclusive ground paths across building and park plots | NOT TESTED | Draw and edit an exact surface-path variant through an existing plot; reverse the placement order. Keep the route in place, its finish above shallow ground caps, and walls/steps/raised amenities depth-tested. Verify variant change, Undo/Redo and reload; retain site limits and motor-road protections. |
| Native street production recipe and unchanged Apply | N/A | N/A: street recipe |
| Finite street draft and connected section replacement | N/A | N/A: street draft |
| Angled join and short-arm recovery | N/A | N/A: street joins |
| Sloped site; contacts and route continuity | NOT TESTED |  |
| Prepared level: actual native step pick, current review and route; unresolved export guard | N/A | N/A: building step pick |
| Revision-locked fixed-native step pick | N/A | N/A: building step pick |
| Native park short arrival and sidewalk width | NOT TESTED | On a level site, aim the authored gateway at both a narrow and a wider pedestrian band; preserve its full width, fit the short approach to the band, and keep the whole ingress clear of protected park equipment. |
| Multiple low steps: choose street-facing step; opposite-side rejection and Cancel preserve saved link | N/A | N/A: building entrances |
| Edge/unsupported case and inward recovery | NOT TESTED |  |
| Local ground hole: unaffected object works; affected object rejects; recovery/reload/export guard | NOT TESTED |  |
| Park measurement unavailable: visible warning, move/resize or explicit prepared-level recovery | NOT TESTED |  |
| Hillside park profile: whole-site and house-route verification still gates capture | NOT TESTED |  |
| Supported minimum/maximum size and rotation | NOT TESTED |  |
| Edit during pending ground / tile refinement | NOT TESTED |  |
| Delete / Undo / Redo; referenced route target | NOT TESTED |  |
| Interrupted navigation or measurement | NOT TESTED |  |
| Interrupted building asset download; Retry after an unrelated save | N/A | N/A: building asset |
| Embedded display slab / street on prepared ground | NOT TESTED | Check both GLB-owned ground and runtime foundation, native and repeated podiums; retain entrance paving, architectural materials, complete bounds and source bytes. |
| Failed/conflicting save; retry without lost edits | NOT TESTED |  |
| Boundary exclusion: readable object labels and unchanged saved geometry | NOT TESTED |  |
| Save/reload/reopen; exact persisted identity | NOT TESTED |  |
| Generate to 3D: panel recipe matches locked compiler; reload and inspect visible models | NOT TESTED |  |
| Supported storey edit: plan and saved-zone compilation agree | N/A | N/A: no storeys |
| Storey source frame and complete-model centring | N/A | N/A: no storeys |
| Capture blocked while stale, then succeeds | NOT TESTED |  |
| Site landscape compatibility | NOT TESTED | Continuous custom base stays below the archetype; trees respect complete plot and access. Move or route/variant edit invalidates; Undo/Redo/reload/export retain the correct result. Verify surrounding-tile colour feathering and ground-height seams separately. Custom artwork cannot cover objects or export before loading. |
| Student-authored placement and connections | NOT TESTED |  |
| Empty-lot mixed scene before batch scale-up | NOT TESTED | Several buildings plus street/path and park/open space through ordinary controls; remove unsupported fallbacks from final evidence. |
| Oversized fixed-native candidate on an appropriately sized vacant parcel | N/A | N/A: fixed-native building |
| Collision preview, assisted snap and final occupied envelope agree | NOT TESTED | A visibly clear route/placement must not hard reject against an unexplained hidden plot envelope; record nearest-valid recovery. |
| Repeat placement on both sides of a bent street | N/A | N/A: building placement |
| Assisted placement and automatic entrance | N/A | N/A: building entrance |
| Fixed-native entrance after plot resize | N/A | N/A: building entrance |
| Default park programme and status text | NOT TESTED | First placement uses recommended size with advertised programme. Compact minima remain deliberate choices. An explicit adaptive renderer must not be described as missing solely because its external family is pending; unsupported siblings still show warnings. |
| Export file delivery | NOT TESTED | Separately verify settled capture, preview, actual Download action and saved file. Record browser cancellation honestly; extracting a data URL only proves the PNG content. |
| Paid-image cost and fidelity review | NOT TESTED | Before calling: selected engine, exact server reservation, balance and call count. After calling: audit debit, same-camera comparison, automatic result, human status and fallback. Stop further calls if accounting is unexplained. |

## Entrance measurements (buildings)

For each supported entrance, record the native coordinate frame and base datum,
door/step/landing edge coordinates, clear width, route direction, measured plot
anchor, `scaleWithPlot` behavior and reference dimensions. Link front/side/low
views to the exact model hash. Record repeated-house or multiple-entrance limits.
These are reviewed measurements; this template does not install runtime metadata.
Identify the actual step surface and its transform, even when it belongs to a
different material/mesh group. Distinguish lowest tread-top height from the
step-foot/base datum used by the generated approach; do not select by mesh name.
When the model has front and rear low steps, record both positions and test the
facing/recovery behavior against the chosen sidewalk. Automatic street-facing
rotation alone does not prove that a picked step connects.

For an automatic fixed-building approach, record the measured mesh-edge
coordinates, the 1.2–4 m connector width, and the opening width separately.
Verify contact at both ends in the rendered scene after reopening.

Record total route length and rise, building/street landing depths and elevations,
flight run and step count. Verify the landing is level at the native-step foot,
clears the entire measured terrain footprint and leaves enough stair run.
Include a bare-stairs-fit/landing-does-not-fit case and its move/Undo/Redo/reload
recovery. Preserve exact capture ownership and inspect the exported geometry.
List unresolved foundation height, landing support, guards, frontage clearance
and accessible-route design separately from geometric readiness.
Record clear walking width after rail intrusion, open entry/exit ends, detail
envelopes, measured support-foot elevations, and detail capture ownership.
Test picking with an intervening rail and after moving to a clear view. Verify
entrance-only Save/Undo/Redo/reload preserves compiled model markers and does not
request model planning/placement; verify real footprint changes still rebuild.

Record the student review panel's saved plot identity, measured generated steps,
signed rise, clear width and maximum foundation support height. Confirm sampling
hides numbers, current geometry restores them, an invalid edit replaces them with
repair guidance, and Select/Connections/Undo/Redo/reload preserves the plot. Match
retained display and verified ground by measured source/snapshot identity, not by
assuming their revision strings have the same format. Distinguish support-envelope
edges from authored walking surfaces, and nearly level approach from step-free
access to the native door. These design checks remain open after export.

## Classroom impact

- Participant: actual novice / instructor / agent simulation:
- Empty-project UI authoring, retries, save waits and ordinary recovery:
- Developer/API intervention (read-only verification separately):
- Prerequisites discoverable using actual control labels:

An agent simulation is a provisional prototype checkpoint while students are
unavailable, not independent usability evidence or new asset approval.

For prepared-site public connections, record the overhead endpoint/real-road
match, low inside-site view, outside tile cut, retained setbacks, open retaining
face and measured cut/fill sides. Test endpoint edit/Undo/Redo/reload and whether
free landscaping needs reapplication. For export, verify the actual saved file
and its bytes, not only a preview; Windows browser download paths need native
backslashes. See `CLASSROOM_GROUND_EXPORT_2026-09-22.md` for bounded evidence.

Use the practical classroom target in `CLASSROOM_READINESS_PLAN_2026-09-20.md`.
For every open item, record whether it prevents authoring, plausible geometry,
reliable recovery or faithful presentation (blocker), or is a finer concept
limitation (follow-up). Keep visual acceptance and publication decisions separate.
Do not require construction-level detail to pass a concept-design classroom pilot.
When ground rejects a placement/site, verify its review highlights the actual
rejected samples and offers a usable recovery through ordinary controls.

## Verification and decision

For vegetation replacement, record full-crown parcel/fixed-program clearance,
preserved support and clump reserves. For paid close-ups, retain source/output
pairs, design-check status, audit charges and actual downloaded-file evidence.
Do not label an attractive unverified AI original as faithful.

For offline asset delivery, include native component GLBs, placement/surface
recipes and the preview assembly separately. Record material-aware route ray
checks on the reimported GLB, full-envelope bounds and static/instance budgets.
These checks cannot prefill runtime terrain, access or edit/recovery passes.

- Focused test commands/results and reused shared-test evidence:
- Type-check/lint or relevant backend/compiler checks for source changes:
- Console/network failures and recovery:
- Original fixture preservation and final disposable-project state:
- Oblique sky/ground-gap distinction; fallback excluded from picking/support:
- Exact generation inputs preserved separately from later corrected previews:
- Assisted/native-size trial versus ordinary student authoring and route connectivity:
- Park-to-street/entrance clearance in preview, drag and save; bounded fit retains size/rotation:
- Park approach clears neighbouring parks, fixed equipment and full-width street/boundary barriers:
- Report route evidence matches the scene; stale evidence rejected; absent evidence remains uncertain:
- Connected bend/body/section edit retains every renderable T/X patch; neighbours unchanged:
- Whole-site graph matches road-only graph; bounded road-ground recovery after new tiles:
- Open failures, untested advertised features, owner and next bounded action:
- Runtime integration decision: NOT REVIEWED
- Asset visual decision (separate): NOT REVIEWED
- Publication/activation authorization (separate; cite actual authorization):

A passing solver, successful compiler, CLI preflight, or attractive screenshot
alone is not student-ready acceptance. Do not invent a review or approval.

## Two-endpoint bridge draft and persistence regression

For route-capable bridges, verify first-click hover, both confirmed endpoints plus cursor motion, extra click endpoint adjustment, Enter/Finish and the complete click/click/double-click event sequence. Coordinates and sampled-height arrays must retain the same two endpoints; ordinary street bend/duplicate behavior must remain unchanged. Repeat endpoint edits against the actual PostgreSQL enum-backed API, then Undo/Redo/reload and download the exact source. Mocked session tests alone do not prove a valid database query. Keep original fixed saves and production gates distinct from the new route revision.


## Source-derived bridge route contracts

Use the complete occupied geometry to define each endpoint interval, including skew caps, tower backs and full stair flights. Preserve original source bytes and material ownership; record derivative-only stairs/approaches explicitly. At minimum span, complete landscape/support companion assemblies must fit rather than silently disappear. Keep road/rail lane counts tied to source programmes, not generic deck widths. Compare compiled metric envelopes at the same millimetre precision while retaining immutable source locks.

For overlapping stair flights, filter candidate walking surfaces by current foot height before choosing the nearest plan surface. Exact skew tread polygons can be necessary; an inscribed strip may leave corner holes. Offline ray and prior-height traversal tests do not replace browser walking. Endpoint edit, Undo/Redo, PostgreSQL persistence, full reload, source capture and at-grade connection acceptance remain separate evidence gates.

## Offline evidence (not runtime passes)

- delivered byte hashes
- self-contained GLB buffers
- no textures or images
- walk surface materials present
- finite metric bounds
- inside the 48 x 40 m footprint
- recipe bounds match the GLB
- below grade only inside the declared sunken areas
- nothing taller than 20 m
- 822 material-aware route rays on deck, grass, gravel
- 448 planted instances clear of every route
- the entrance is walkable at the site edge
- nine cups with flagsticks, each on its own green
- the creek is one water plane 0.12 m below grade

Geometry verification: `PASS_OFFLINE_GEOMETRY` for model `c989175c73f3cb0d1c554ba672694ee4e9785e7fedf1ae418e1c695a04fb6179`.
