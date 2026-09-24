# Runtime integration review — <archetype / exact variant>

Copy this template into the candidate evidence package. Complete it using
[Runtime integration for every archetype](ARCHETYPE_RUNTIME_INTEGRATION.md).
The [Currie three-type rehearsal](CLASSROOM_CATALOGUE_ENTRY_REHEARSAL_2026-09-20.md)
shows how to keep scene-level passes separate from exact-variant untested gates.
Replace this relative link with the repository document path if copied elsewhere.
Default status is NOT TESTED. Do not prefill a pass from another archetype.

## Candidate and scope

- Kind: building / street or path / park or open space
- Archetype ID and exact variant ID:
- Model SHA-256 or procedural recipe ID/revision/hash:
- Runtime source commit and integration-checklist version:
- Reviewer, date, project URL, viewport/device/input:
- Vacant test site, protected reference, disposable test project:
- Mixed-scene project and separate oversized-candidate project, if applicable:
- Supported plot dimensions, axes/base datum, reshape/repetition behavior:
- Supported terrain modes and connection capabilities:
- Public-realm detail: metric plant height/footprint, paving scale, instance/texture budgets, and native close/aerial evidence:
- Replacement furniture: complete mesh envelope/base datum, legacy-asset flag independence, component and in-site evidence:
- Vegetation: canopy envelope, seeded prototype/triangle budget, furniture-scale comparison and route/entrance visibility:
- Hardscape trees: paired bed/well style and footprint, visible root opening, shared surface datum, paving/joint exclusion, clear routes and sloped-contact evidence:
- Sports: sourced playing dimensions, full run-off/equipment reserve, measured net/rim heights, open gates, crown clearance and non-coplanar floor finishes; separate recreational adaptations:
- Reference-image fidelity: exact image hashes, observed amenity cues, borrowed/inferred details, native before/after views and separately exported reusable amenity modules:
- Street asset handoff: metric band widths, metre-scale paving phase, supported full-width endpoints, native amenity contacts, and flush versus raised boarding/kerb limitations:
- Asset review status and separate publication/activation status:
- Model Library storage check, configured bucket and result (building GLBs):
- Fresh installation: exact binding/recipe/module seed, byte readback, conflict preservation and disposable DB/bucket evidence:
- Evidence manifest location and hashes; durable shared location for delivery:

## Gates

Use PASS / FAIL / NOT TESTED / N/A. Attach evidence to each PASS and a reason
to each N/A. Use the shared checklist for each gate's full meaning.

| Gate | Status | Evidence / limitation / next action |
| --- | --- | --- |
| C1 Exact identity | NOT TESTED | |
| C2 Dimensions and transformations | NOT TESTED | |
| C3 Full footprint ground support | NOT TESTED | |
| C4 Freshness and late results | NOT TESTED | |
| C5 Pedestrian continuity and public-road access for vehicle streets | NOT TESTED | Entrance/park path; street endpoint, marker, real-road match, clear route |
| C6 Edit / Undo / save / reopen | NOT TESTED | |
| C7 Failure and recovery | NOT TESTED | |
| C8 Low/aerial views, exact capture and any AI-image comparison | NOT TESTED | Same-camera source/output; count, outline, location, scale, access, material/function, additions; pass/review/fallback |
| C9 Student controls and supported inputs | NOT TESTED | |
| B1 Native placement | NOT TESTED | |
| B2 Measured entrance evidence | NOT TESTED | |
| B3 Entrance authoring | NOT TESTED | |
| B4 Approach and setback recovery | NOT TESTED | |
| B5 Foundation/stair/access design review | NOT TESTED | |
| S1 Metric section | NOT TESTED | |
| S2 Route and junction topology | NOT TESTED | |
| S3 Shared grade and public connection | NOT TESTED | |
| S4 Clearance and target identity | NOT TESTED | |
| P1 Exact program and rigid amenities | NOT TESTED | |
| P2 Shared park terrain | NOT TESTED | |
| P3 Automatic remeasurement | NOT TESTED | |
| P4 Park access and grade review | NOT TESTED | |

## Bounded live matrix

Record actual measurements, steps, and relevant screenshots/API readback.
Mark type-specific gates N/A with a reason; keep applicable unrun cases open.

| Case | Status | Observation and evidence |
| --- | --- | --- |
| Level site; low views from multiple sides | NOT TESTED | |
| Irregular site between mapped roads; natural and prepared modes; exposed site edge | NOT TESTED | Record ordinary-control boundary draw, approximate vs surveyed status, contained objects, pad edge and capture consequence. |
| Direct selection where an authored zone overlaps prepared ground | NOT TESTED | After reload, select the contained zone from the canvas, select the site elsewhere, then reselect the zone; confirm its edit handles and settings. |
| Proposed off-site public-road endpoint; Undo/Redo/reload and low junction grade | NOT TESTED | Confirm the mapped road visually; marker or stored height alone is insufficient. |
| Fixed street bend through ordinary controls | NOT TESTED | Add bend point, drag the route handle, then reload and compare centreline, compiler identity and handle count. |
| Native street production recipe and unchanged Apply | NOT TESTED | Backend catalogue, exact profile/revision/module locks, editor variant/width, reload without DEV marker; no fallback to a sibling. |
| Angled join and short-arm recovery | NOT TESTED | Width-aware snapping, sampled-curve node identity, owned pavement/sidewalk surface, no crossing-only fallback on unsupported joins. |
| Sloped site; contacts and route continuity | NOT TESTED | |
| Prepared level: actual native step pick, current review and route; unresolved export guard | NOT TESTED | |
| Multiple low steps: choose street-facing step; opposite-side rejection and Cancel preserve saved link | NOT TESTED | |
| Edge/unsupported case and inward recovery | NOT TESTED | |
| Local ground hole: unaffected object works; affected object rejects; recovery/reload/export guard | NOT TESTED | |
| Park measurement unavailable: visible warning, move/resize or explicit prepared-level recovery | NOT TESTED | |
| Hillside park profile: whole-site and house-route verification still gates capture | NOT TESTED | |
| Supported minimum/maximum size and rotation | NOT TESTED | |
| Edit during pending ground / tile refinement | NOT TESTED | |
| Delete / Undo / Redo; referenced route target | NOT TESTED | |
| Interrupted navigation or measurement | NOT TESTED | |
| Failed/conflicting save; retry without lost edits | NOT TESTED | |
| Boundary exclusion: readable object labels and unchanged saved geometry | NOT TESTED | |
| Save/reload/reopen; exact persisted identity | NOT TESTED | |
| Generate to 3D: panel recipe matches locked compiler; reload and inspect visible models | NOT TESTED | |
| Capture blocked while stale, then succeeds | NOT TESTED | |
| Site landscape compatibility | NOT TESTED | Continuous custom base stays below the archetype; trees respect complete plot and access. Move or route/variant edit invalidates; Undo/Redo/reload/export retain the correct result. Verify surrounding-tile colour feathering and ground-height seams separately. Custom artwork cannot cover objects or export before loading. |
| Student-authored placement and connections | NOT TESTED | |
| Empty-lot mixed scene before batch scale-up | NOT TESTED | Several buildings plus street/path and park/open space through ordinary controls; remove unsupported fallbacks from final evidence. |
| Oversized fixed-native candidate on an appropriately sized vacant parcel | NOT TESTED | Preserve the complete native envelope; record natural/prepared terrain result and required service/public circulation. |
| Collision preview, assisted snap and final occupied envelope agree | NOT TESTED | A visibly clear route/placement must not hard reject against an unexplained hidden plot envelope; record nearest-valid recovery. |
| Repeat placement on both sides of a bent street | NOT TESTED | Check actual entry-facing geometry, Place another orientation, visible step picking and number of manual adjustments; separate assisted completion from novice usability. |
| Assisted placement and automatic entrance | NOT TESTED | Place without opening Connections, overlap a neighbour, preserve existing paths/street space, confirm preview/drop agree, then move/Undo/Redo/reload/capture. Register reviewed native entrance metadata and supported sizes; preserve manual overrides. |
| Fixed-native entrance after plot resize | NOT TESTED | Bind default to exact asset/variant/revision; distinguish door from apron anchor. Enlarge the plot and prove the entry stays attached to the unscaled building. Reject repeated-house inheritance and unsupported variants. |
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
- Open failures, untested advertised features, owner and next bounded action:
- Runtime integration decision: NOT REVIEWED
- Asset visual decision (separate): NOT REVIEWED
- Publication/activation authorization (separate; cite actual authorization):

A passing solver, successful compiler, CLI preflight, or attractive screenshot
alone is not student-ready acceptance. Do not invent a review or approval.
