# Runtime integration review — Brick courtyard path / brick_courtyard_path_v1

Copy this template into the candidate evidence package. Complete it using
[Runtime integration for every archetype](../../ARCHETYPE_RUNTIME_INTEGRATION.md).
The [Currie three-type rehearsal](../../CLASSROOM_CATALOGUE_ENTRY_REHEARSAL_2026-09-20.md)
shows how to keep scene-level passes separate from exact-variant untested gates.
Replace this relative link with the repository document path if copied elsewhere.
Unfilled gates remain NOT TESTED. Shared automated evidence is separated from live exact-variant checks. See ../../NARROW_PATHWAYS_2026-10-07.md for the bounded live scope.

## Candidate and scope

- Kind: street or path; surface-only pedestrian concept
- Archetype ID and exact variant ID: campus_pedestrian_spine / brick_courtyard_path_v1
- Model SHA-256 or procedural recipe ID/revision/hash: program 8853dbff75b53eab6a25d5df7988110b48d4388dc75583f50c1bb2c58ffd6527; assembly/source 987de3477b8a9bc658c9456ee4b5593a5e07648a118c620506be518ea7cab575 (procedural JSON, no GLB).
- Runtime source commit and integration-checklist version: base 3612e1cac + codex/five-narrow-pathways-2026-10-07; checklist updated 2026-10-07.
- Reviewer, date, project URL, viewport/device/input: Codex agent simulation; 2026-10-07; http://127.0.0.1:5181/projects/d7eb67d6-11a5-41ad-84d8-c48872fbb465; Windows Chromium 1280x720, mouse/keyboard.
- Vacant test site, protected reference, disposable test project:
- Mixed-scene project and separate oversized-candidate project, if applicable:
- Supported plot dimensions, axes/base datum, reshape/repetition behavior: fixed 2.0 m clear width; UI minimum 2 m, maximum 300 m route. X across, Y along, Z up; 0.025 m surface lift; 6 m repeat fixture; drawn centreline bends.
- Supported terrain modes and connection capabilities: prepared level only. Automated perpendicular T-junction checks for this exact variant passed. Slopes and mapped public-road joins are NOT TESTED.
- Public-realm detail: metric plant height/footprint, paving scale, instance/texture budgets, and native close/aerial evidence:
- Replacement furniture: complete mesh envelope/base datum, legacy-asset flag independence, component and in-site evidence:
- Vegetation: canopy envelope, seeded prototype/triangle budget, furniture-scale comparison and route/entrance visibility:
- Hardscape trees: paired bed/well style and footprint, visible root opening, shared surface datum, paving/joint exclusion, clear routes and sloped-contact evidence:
- Sports: sourced playing dimensions, full run-off/equipment reserve, measured net/rim heights, open gates, crown clearance and non-coplanar floor finishes; separate recreational adaptations:
- Reference-image fidelity: exact image hashes, observed amenity cues, borrowed/inferred details, native before/after views and separately exported reusable amenity modules:
- Street asset handoff: metric band widths, metre-scale paving phase, supported full-width endpoints, native amenity contacts, and flush versus raised boarding/kerb limitations:
- Asset review status and separate publication/activation status: candidate; local trial active as requested; human visual decision pending; not published.
- Model Library storage check, configured bucket and result (building GLBs): N/A, procedural surface recipe; no building GLB/bucket.
- Fresh installation: exact binding/recipe/module seed, byte readback, conflict preservation and disposable DB/bucket evidence:
- Evidence manifest location and hashes; durable shared location for delivery: ../../NARROW_PATHWAYS_2026-10-07.json; screenshots/API readbacks remain local external evidence, not published.

## Gates

Use PASS / FAIL / NOT TESTED / N/A. Attach evidence to each PASS and a reason
to each N/A. Use the shared checklist for each gate's full meaning.

| Gate | Status | Evidence / limitation / next action |
| --- | --- | --- |
| C1 Exact identity | PASS | Exact catalogue option, recipe locks, HTTP hero hash, saved variant and reload inspected; manifest records hashes. |
| C2 Dimensions and transformations | NOT TESTED | |
| C3 Full footprint ground support | NOT TESTED | |
| C4 Freshness and late results | NOT TESTED | |
| C5 Pedestrian continuity and public-road access for vehicle streets | NOT TESTED | Entrance/park path; street endpoint, marker, real-road match, clear route |
| C6 Edit / Undo / save / reopen | NOT TESTED | |
| C7 Failure and recovery | NOT TESTED | |
| C8 Low/aerial views, exact capture and any AI-image comparison | NOT TESTED | Same-camera source/output; count, outline, location, scale, access, material/function, additions; pass/review/fallback |
| C9 Student controls and supported inputs | NOT TESTED | |
| B1 Native placement | N/A | Surface-only path; no building or park programme. |
| B2 Measured entrance evidence | N/A | Surface-only path; no building or park programme. |
| B3 Entrance authoring | N/A | Surface-only path; no building or park programme. |
| B4 Approach and setback recovery | N/A | Surface-only path; no building or park programme. |
| B5 Foundation/stair/access design review | N/A | Surface-only path; no building or park programme. |
| S1 Metric section | PASS | 2.0 m section, graph and footprint width; zero motor lanes/curbs/modules; automated exact-variant geometry checks. |
| S2 Route and junction topology | NOT TESTED | |
| S3 Shared grade and public connection | NOT TESTED | |
| S4 Clearance and target identity | NOT TESTED | |
| P1 Exact program and rigid amenities | N/A | Surface-only path; no building or park programme. |
| P2 Shared park terrain | N/A | Surface-only path; no building or park programme. |
| P3 Automatic remeasurement | N/A | Surface-only path; no building or park programme. |
| P4 Park access and grade review | N/A | Surface-only path; no building or park programme. |

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
| Narrow pedestrian section and bend control retention | NOT TESTED | Zero motor lanes; identical footprint/graph/section width; sparse handles survive boundary snap, save, Undo/Redo and reload. |
| Native street production recipe and unchanged Apply | NOT TESTED | Backend catalogue, exact profile/revision/module locks, editor variant/width, reload without DEV marker; no fallback to a sibling. |
| Finite street draft and connected section replacement | NOT TESTED | Exact variant/archetype/width before recipe creation, real existing zone ID, unchanged neighbours, no persisted preview flag; invalid saved recipes and lost junctions reject. |
| Angled join and short-arm recovery | NOT TESTED | Width-aware snapping, sampled-curve node identity, owned pavement/sidewalk surface, no crossing-only fallback on unsupported joins. |
| Sloped site; contacts and route continuity | NOT TESTED | |
| Prepared level: actual native step pick, current review and route; unresolved export guard | NOT TESTED | |
| Revision-locked fixed-native step pick | NOT TESTED | Confirm the button and real mesh hit are available when `native_plot_axes` is true and `native_home_plot` is false; plan reach alone cannot pass the foundation-edge review. |
| Native park short arrival and sidewalk width | NOT TESTED | On a level site, aim the authored gateway at both a narrow and a wider pedestrian band; preserve its full width, fit the short approach to the band, and keep the whole ingress clear of protected park equipment. |
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
| Save/reload/reopen; exact persisted identity | PASS | Drawn using catalogue; all five persisted and reappeared after browser reload. API readback in five-paths-after-edit.json. |
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

- Participant: actual novice / instructor / agent simulation: agent simulation only; no student acceptance claim.
- Empty-project UI authoring, retries, save waits and ordinary recovery:
- Developer/API intervention (read-only verification separately): server setup/catalogue installation; QA login recovery; read-only zone API verification. All path geometry authored using normal UI controls.
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

- Focused test commands/results and reused shared-test evidence: 163 frontend tests, 21 backend tests; exact variants covered in narrowPathways.test.ts and test_narrow_pathways.py.
- Type-check/lint or relevant backend/compiler checks for source changes: npm run type-check PASS; native street registry parity check PASS.
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
- Open failures, untested advertised features, owner and next bounded action: see batch report. Next bounded instructor trial: slopes only after support is implemented, failed-save recovery, full walk traversal and actual export download. No slope support advertised.
- Runtime integration decision: provisional local prepared-level trial; full classroom matrix remains open.
- Asset visual decision (separate): agent reviewed native overview; instructor review pending.
- Publication/activation authorization (separate; cite actual authorization): user requested five pathways in Streets; local implementation only. No push or publication requested.

A passing solver, successful compiler, CLI preflight, or attractive screenshot
alone is not student-ready acceptance. Do not invent a review or approval.

## Exact-variant observation

Five-point standalone curved route drawn at northwest of test site. Native aerial view and persisted identity inspected; full walking traversal/edit recovery not run.
