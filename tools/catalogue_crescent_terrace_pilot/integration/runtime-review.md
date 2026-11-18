# Runtime integration review — london_crescent_terrace / london-crescent-terrace-bath-stone

**Nothing in this review was run in the app.** The session that built the model had no
database, object storage or map key, so every applicable gate and matrix row below is
NOT TESTED. This file records only declarations, native measurements taken from the
model's own numbers, and which rows do not apply to a building. It follows
`docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md` and `docs/ARCHETYPE_RUNTIME_INTEGRATION.md`.
No pass is carried over from any other archetype.

## Candidate and scope

- Kind: building
- Archetype ID and exact variant ID: `london_crescent_terrace` / `london-crescent-terrace-bath-stone` (variant 0)
- Model SHA-256 or procedural recipe ID/revision/hash: `705fc02b21d5704bf6b97a565b1c48df079b47d8d4f38f5304f5fb0d623b0284`, candidate `crescent-terrace-bath-stone-clay-v006`, 8594664 bytes. Rebuilt byte for byte by `tools/catalogue_crescent_terrace_pilot/build.py`
- Runtime source commit and integration-checklist version: not run. Branch base `4922d9771e` on `deployment-version`; checklist as at that commit
- Reviewer, date, project URL, viewport/device/input: none. No project was opened
- Vacant test site, protected reference, disposable test project: none
- Mixed-scene project and separate oversized-candidate project, if applicable: none
- Supported plot dimensions, axes/base datum, reshape/repetition behavior: declared, not tested. Metres. In the GLB, Y is up, east is +X, and the crescent opens toward +Z. Base datum Y = 0 at grade; nothing lies below it. Complete native envelope 126.3175 m wide by 48.4002 m deep by 19.16 m high, including the 1.8 m paved strip with its railings. The envelope is symmetrical about X = 0; its centre is at Z = -22.4, that far behind the line joining the two ends. `fixed_native`: move and rotate only, no stretch, no repetition. Smallest plot 129.3 m by 51.4 m, the envelope plus 3 m. The catalogue lists a 6 m by 12 m plot for this archetype, the size of one house; this model is the whole crescent
- Authored storey programme: exact source/module hashes, shared whole-source origin, complete-assembly bounds centre, native-lock flag, and any bounded uniform-scale opt-in: one complete model, three storeys, `fixed_authored_assembly`. No storey edits are advertised. Centred by its whole-model bounds; native lock required; no scale opt-in
- Supported terrain modes and connection capabilities: not tested. Thirty-six doors: sixteen on the concave front, eighteen on the convex side, one at each end. The two end houses are entered from their ends
- Public-realm detail: metric plant height/footprint, paving scale, instance/texture budgets, and native close/aerial evidence: N/A: building only; the model contains no such element
- Replacement furniture: complete mesh envelope/base datum, legacy-asset flag independence, component and in-site evidence: N/A: building only; the model contains no such element
- Vegetation: canopy envelope, seeded prototype/triangle budget, furniture-scale comparison and route/entrance visibility: N/A: building only; the model contains no such element
- Hardscape trees: paired bed/well style and footprint, visible root opening, shared surface datum, paving/joint exclusion, clear routes and sloped-contact evidence: N/A: building only; the model contains no such element
- Sports: sourced playing dimensions, full run-off/equipment reserve, measured net/rim heights, open gates, crown clearance and non-coplanar floor finishes; separate recreational adaptations: N/A: building only; the model contains no such element
- Reference-image fidelity: exact image hashes, observed amenity cues, borrowed/inferred details, native before/after views and separately exported reusable amenity modules: three references locked by hash in `prework-manifest.json`. The roof-plan reference shows a different, shorter building; seven disagreements are recorded, with the inferred far end, convex side and interiors. No amenity modules
- Native park seams and raised/cycle access: full-width closed-loop/bend support, local-origin furniture transforms, measured ramp/landing or track-entry height continuity; separate offline contacts from runtime slope walking: N/A: building only; the model contains no such element
- Street asset handoff: metric band widths, metre-scale paving phase, supported full-width endpoints, native amenity contacts, and flush versus raised boarding/kerb limitations: N/A: building only; the model contains no such element
- Asset review status and separate publication/activation status: independent review not complete for this candidate. Publication and activation: not authorized
- Model Library storage check, configured bucket and result (building GLBs): NOT RUN. The GLB is not in the model library
- Fresh installation: exact binding/recipe/module seed, byte readback, conflict preservation and disposable DB/bucket evidence: NOT RUN
- Evidence manifest location and hashes; durable shared location for delivery: `tools/catalogue_crescent_terrace_pilot/evidence/` and `candidate.json`. Renders and boards exist only in the build session's ignored `artifacts/` directory, which is not a durable shared location; they can be regenerated from the generator

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
| C1 Exact identity | NOT TESTED | Not in the catalogue, so there is nothing to place |
| C2 Dimensions and transformations | NOT TESTED | Declared above; not exercised |
| C3 Full footprint ground support | NOT TESTED | |
| C4 Freshness and late results | NOT TESTED | |
| C5 Pedestrian continuity and public-road access for vehicle streets | NOT TESTED | Entrance/park path; street endpoint, marker, real-road match, clear route |
| C6 Edit / Undo / save / reopen | NOT TESTED | |
| C7 Failure and recovery | NOT TESTED | |
| C8 Low/aerial views, exact capture and any AI-image comparison | NOT TESTED | Same-camera source/output; count, outline, location, scale, access, material/function, additions; pass/review/fallback |
| C9 Student controls and supported inputs | NOT TESTED | |

For fixed-native buildings, record Q/E and rotation-field evidence at the actual
site latitude: metre dimensions/right angles preserved, exact model retained
after save/reopen. A displayed angle alone does not prove detailed-model fit.
| B1 Native placement | NOT TESTED | Needs the whole 126.3 m by 48.4 m envelope. The catalogue plot of 6 m by 12 m cannot hold it |
| B2 Measured entrance evidence | NOT TESTED | Native measurements recorded below from the model's own numbers. Not installed and not checked in the app |
| B3 Entrance authoring | NOT TESTED | |
| B4 Approach and setback recovery | NOT TESTED | |
| B5 Foundation/stair/access design review | NOT TESTED | Design notes below; not reviewed in a scene |
| S1 Metric section | N/A | Street gate; this is a building |
| S2 Route and junction topology | N/A | Street gate; this is a building |
| S3 Shared grade and public connection | N/A | Street gate; this is a building |
| S4 Clearance and target identity | N/A | Street gate; this is a building |
| P1 Exact program and rigid amenities | N/A | Park gate; this is a building |
| P2 Shared park terrain | N/A | Park gate; this is a building |
| P3 Automatic remeasurement | N/A | Park gate; this is a building |
| P4 Park access and grade review | N/A | Park gate; this is a building |

## Bounded live matrix

Record actual measurements, steps, and relevant screenshots/API readback.
Mark type-specific gates N/A with a reason; keep applicable unrun cases open.

| Case | Status | Observation and evidence |
| --- | --- | --- |
| Level site; low views from multiple sides | NOT TESTED | |
| Irregular site between mapped roads; natural and prepared modes; exposed site edge | NOT TESTED | Record ordinary-control boundary draw, approximate vs surveyed status, contained objects, pad edge and capture consequence. |
| Direct selection where an authored zone overlaps prepared ground | N/A | Street or park case; this is a fixed-native building |
| Proposed off-site public-road endpoint; Undo/Redo/reload and low junction grade | N/A | Street or park case; this is a fixed-native building |
| Fixed street bend through ordinary controls | N/A | Street or park case; this is a fixed-native building |
| Long repeatable route and exact edit datum | N/A | Street or park case; this is a fixed-native building |
| Repeated street travel-surface ownership | N/A | Street or park case; this is a fixed-native building |
| X-to-T and T-to-X recovery | N/A | Street or park case; this is a fixed-native building |
| Narrow pedestrian section and bend control retention | N/A | Street or park case; this is a fixed-native building |
| Nonexclusive ground paths across building and park plots | N/A | Street or park case; this is a fixed-native building |
| Native street production recipe and unchanged Apply | N/A | Street or park case; this is a fixed-native building |
| Finite street draft and connected section replacement | N/A | Street or park case; this is a fixed-native building |
| Angled join and short-arm recovery | N/A | Street or park case; this is a fixed-native building |
| Sloped site; contacts and route continuity | NOT TESTED | |
| Prepared level: actual native step pick, current review and route; unresolved export guard | NOT TESTED | |
| Revision-locked fixed-native step pick | NOT TESTED | Confirm the button and real mesh hit are available when `native_plot_axes` is true and `native_home_plot` is false; plan reach alone cannot pass the foundation-edge review. |
| Native park short arrival and sidewalk width | N/A | Street or park case; this is a fixed-native building |
| Multiple low steps: choose street-facing step; opposite-side rejection and Cancel preserve saved link | NOT TESTED | |
| Edge/unsupported case and inward recovery | NOT TESTED | |
| Local ground hole: unaffected object works; affected object rejects; recovery/reload/export guard | NOT TESTED | |
| Park measurement unavailable: visible warning, move/resize or explicit prepared-level recovery | N/A | Street or park case; this is a fixed-native building |
| Hillside park profile: whole-site and house-route verification still gates capture | N/A | Street or park case; this is a fixed-native building |
| Supported minimum/maximum size and rotation | NOT TESTED | |
| Edit during pending ground / tile refinement | NOT TESTED | |
| Delete / Undo / Redo; referenced route target | NOT TESTED | |
| Interrupted navigation or measurement | NOT TESTED | |
| Interrupted building asset download; Retry after an unrelated save | NOT TESTED | Bounded automatic retry; actual cache reload; preserved source identity; no proxy reported as detailed-ready. |
| Embedded display slab / street on prepared ground | NOT TESTED | Check both GLB-owned ground and runtime foundation, native and repeated podiums; retain entrance paving, architectural materials, complete bounds and source bytes. |
| Failed/conflicting save; retry without lost edits | NOT TESTED | |
| Boundary exclusion: readable object labels and unchanged saved geometry | NOT TESTED | |
| Save/reload/reopen; exact persisted identity | NOT TESTED | |
| Generate to 3D: panel recipe matches locked compiler; reload and inspect visible models | NOT TESTED | |
| Supported storey edit: plan and saved-zone compilation agree | N/A | Three fixed storeys; no storey edit is advertised |
| Storey source frame and complete-model centring | NOT TESTED | Measure the whole source centre. Repeated modules share one rotated/scaled origin offset; complete native-locked assemblies centre by whole bounds even in module delivery format. Preserve bounded house opt-ins. Verify actual row metadata, rotated plots, native → alternate → native, unit vertical scale and reopen. |
| Capture blocked while stale, then succeeds | NOT TESTED | |
| Site landscape compatibility | NOT TESTED | Continuous custom base stays below the archetype; trees respect complete plot and access. Move or route/variant edit invalidates; Undo/Redo/reload/export retain the correct result. Verify surrounding-tile colour feathering and ground-height seams separately. Custom artwork cannot cover objects or export before loading. |
| Student-authored placement and connections | NOT TESTED | |
| Empty-lot mixed scene before batch scale-up | NOT TESTED | Several buildings plus street/path and park/open space through ordinary controls; remove unsupported fallbacks from final evidence. |
| Oversized fixed-native candidate on an appropriately sized vacant parcel | NOT TESTED | Preserve the complete native envelope; record natural/prepared terrain result and required service/public circulation. |
| Collision preview, assisted snap and final occupied envelope agree | NOT TESTED | A visibly clear route/placement must not hard reject against an unexplained hidden plot envelope; record nearest-valid recovery. |
| Repeat placement on both sides of a bent street | N/A | Street or park case; this is a fixed-native building |
| Assisted placement and automatic entrance | NOT TESTED | Place without opening Connections, overlap a neighbour, preserve existing paths/street space, confirm preview/drop agree, then move/Undo/Redo/reload/capture. Register reviewed native entrance metadata and supported sizes; preserve manual overrides. |
| Fixed-native entrance after plot resize | NOT TESTED | Bind default to exact asset/variant/revision; distinguish door from apron anchor. Enlarge the plot and prove the entry stays attached to the unscaled building. Reject repeated-house inheritance and unsupported variants. |
| Default park programme and status text | N/A | Street or park case; this is a fixed-native building |
| Export file delivery | NOT TESTED | Separately verify settled capture, preview, actual Download action and saved file. Record browser cancellation honestly; extracting a data URL only proves the PNG content. |
| Paid-image cost and fidelity review | N/A | No paid image call was made or is needed for this pilot |

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

### Native measurements for this candidate (not installed, not checked in the app)

Thirty-six doors, all alike: a six-panel leaf under a fanlight, set 0.22 m into a
0.9 m wall, reached by a level stone path through the railings. None has a step.

| Quantity | Value |
|---|---|
| Frame | GLB frame: Y up, east +X, the crescent opens toward +Z, metres. The origin is at grade, midway between the two inner corners of the ends |
| Clear width between frames | 1.01 m |
| Leaf height | 2.25 m, under a fanlight to 3.05 m |
| Threshold top above base datum | 0.035 m |
| Outer step foot | none: the paved strip meets grade at Y = 0 |
| Total rise from grade to threshold | 0.035 m, under the 0.04 m at which the runtime adds a landing |
| Gap in the railings at each door | 1.65 m, with a return of railings each side of the path |
| Path length from railing line to door | 1.70 m |

Door centres on the door's own plane, and the direction a person walks out of each.
The bay number counts round the building from the east end of the concave front.

| Bay | Kind | X (m) | Z (m) | Out direction (X, Z) |
|---|---|---|---|---|
| 5 | front door | 44.62 | -11.02 | -0.87, +0.50 |
| 8 | front door | 40.52 | -16.46 | -0.73, +0.69 |
| 11 | front door | 35.39 | -20.93 | -0.59, +0.81 |
| 14 | front door | 29.58 | -24.49 | -0.46, +0.89 |
| 17 | front door | 23.35 | -27.22 | -0.34, +0.94 |
| 20 | front door | 16.84 | -29.20 | -0.24, +0.97 |
| 23 | front door | 10.17 | -30.49 | -0.14, +0.99 |
| 26 | front door | 3.40 | -31.13 | -0.05, +1.00 |
| 29 | front door | -3.40 | -31.13 | +0.05, +1.00 |
| 32 | front door | -10.17 | -30.49 | +0.14, +0.99 |
| 35 | front door | -16.84 | -29.20 | +0.24, +0.97 |
| 38 | front door | -23.35 | -27.22 | +0.34, +0.94 |
| 41 | front door | -29.58 | -24.49 | +0.46, +0.89 |
| 44 | front door | -35.39 | -20.93 | +0.59, +0.81 |
| 47 | front door | -40.52 | -16.46 | +0.73, +0.69 |
| 50 | front door | -44.62 | -11.02 | +0.87, +0.50 |
| 59 | end door | -53.45 | -0.22 | -0.00, +1.00 |
| 66 | garden door | -60.22 | -7.24 | -0.98, -0.21 |
| 69 | garden door | -56.23 | -17.60 | -0.87, -0.50 |
| 72 | garden door | -50.27 | -25.59 | -0.73, -0.69 |
| 75 | garden door | -43.26 | -31.72 | -0.59, -0.81 |
| 78 | garden door | -35.75 | -36.33 | -0.46, -0.89 |
| 81 | garden door | -27.98 | -39.75 | -0.34, -0.94 |
| 84 | garden door | -20.06 | -42.17 | -0.24, -0.97 |
| 87 | garden door | -12.06 | -43.72 | -0.14, -0.99 |
| 90 | garden door | -4.03 | -44.48 | -0.05, -1.00 |
| 93 | garden door | 4.03 | -44.48 | +0.05, -1.00 |
| 96 | garden door | 12.06 | -43.72 | +0.14, -0.99 |
| 99 | garden door | 20.06 | -42.17 | +0.24, -0.97 |
| 102 | garden door | 27.98 | -39.75 | +0.34, -0.94 |
| 105 | garden door | 35.75 | -36.33 | +0.46, -0.89 |
| 108 | garden door | 43.26 | -31.72 | +0.59, -0.81 |
| 111 | garden door | 50.27 | -25.59 | +0.73, -0.69 |
| 114 | garden door | 56.23 | -17.60 | +0.87, -0.50 |
| 117 | garden door | 60.22 | -7.24 | +0.98, -0.21 |
| 124 | end door | 53.45 | -0.22 | -0.00, +1.00 |

### Design notes left open (B5)

- No exposed foundation: the model stops at grade. On a slope the runtime must supply
  the base under a building 126 m long, and the paved strip will not follow the ground.
- The real building type has a sunken area in front of each house with a bridge to the
  door. Here the doors are level with the pavement and the areas are left out.
- Thirty-six entrances is far more than the runtime's one saved entrance per plot. Which
  door is the plot's entrance, and whether the garden and end doors count, is undecided.
- Railings enclose the building except at the doors, so nothing but the 36 paths
  reaches the wall.

## Classroom impact

- Participant: actual novice / instructor / agent simulation: none. No session was run
- Empty-project UI authoring, retries, save waits and ordinary recovery: not run
- Developer/API intervention (read-only verification separately): none
- Prerequisites discoverable using actual control labels: not assessed

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

- Focused test commands/results and reused shared-test evidence: `python3 -m pytest tools/catalogue_crescent_terrace_pilot` passes; these are generator tests, not runtime tests
- Type-check/lint or relevant backend/compiler checks for source changes: no application source was changed. `ruff check` passes on the tool folder
- Console/network failures and recovery: not run
- Original fixture preservation and final disposable-project state: no project was created
- Oblique sky/ground-gap distinction; fallback excluded from picking/support:
- Exact generation inputs preserved separately from later corrected previews:
- Assisted/native-size trial versus ordinary student authoring and route connectivity:
- Park-to-street/entrance clearance in preview, drag and save; bounded fit retains size/rotation:
- Park approach clears neighbouring parks, fixed equipment and full-width street/boundary barriers:
- Report route evidence matches the scene; stale evidence rejected; absent evidence remains uncertain:
- Connected bend/body/section edit retains every renderable T/X patch; neighbours unchanged:
- Whole-site graph matches road-only graph; bounded road-ground recovery after new tiles:
- Open failures, untested advertised features, owner and next bounded action: everything above marked NOT TESTED. Next bounded action: local install with `--local-trial`, then the student trial in `docs/BUILDING_CATALOGUE_WORKFLOW.md`, on a prepared level plot of at least 129.3 m by 51.4 m
- Runtime integration decision: NOT REVIEWED
- Asset visual decision (separate): NOT REVIEWED by a person. Recorded separately: independent review not complete for this candidate
- Publication/activation authorization (separate; cite actual authorization): none given

A passing solver, successful compiler, CLI preflight, or attractive screenshot
alone is not student-ready acceptance. Do not invent a review or approval.

## Two-endpoint bridge draft and persistence regression

For route-capable bridges, verify first-click hover, both confirmed endpoints plus cursor motion, extra click endpoint adjustment, Enter/Finish and the complete click/click/double-click event sequence. Coordinates and sampled-height arrays must retain the same two endpoints; ordinary street bend/duplicate behavior must remain unchanged. Repeat endpoint edits against the actual PostgreSQL enum-backed API, then Undo/Redo/reload and download the exact source. Mocked session tests alone do not prove a valid database query. Keep original fixed saves and production gates distinct from the new route revision.


## Source-derived bridge route contracts

Use the complete occupied geometry to define each endpoint interval, including skew caps, tower backs and full stair flights. Preserve original source bytes and material ownership; record derivative-only stairs/approaches explicitly. At minimum span, complete landscape/support companion assemblies must fit rather than silently disappear. Keep road/rail lane counts tied to source programmes, not generic deck widths. Compare compiled metric envelopes at the same millimetre precision while retaining immutable source locks.

For overlapping stair flights, filter candidate walking surfaces by current foot height before choosing the nearest plan surface. Exact skew tread polygons can be necessary; an inscribed strip may leave corner holes. Offline ray and prior-height traversal tests do not replace browser walking. Endpoint edit, Undo/Redo, PostgreSQL persistence, full reload, source capture and at-grade connection acceptance remain separate evidence gates.
