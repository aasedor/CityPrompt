# Runtime integration review — high_speed_rail_corridor / student_high_speed_rail_line_v1

**Nothing in this review was run in the app.** The session that built High-Speed Rail Line had no
database, object storage or map key, so every applicable gate and matrix row below is
NOT TESTED. Building- and park-only rows are N/A with a reason. Offline checks are listed
separately at the end and are not runtime passes. It follows
`docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md` and `docs/ARCHETYPE_RUNTIME_INTEGRATION.md`
(version 2026-09-24). No pass is carried over from any other street.

## Candidate and scope

- Kind: street or path: fixed-section native street, repeated along a drawn route
- Archetype ID and exact variant ID: `high_speed_rail_corridor` / `student_high_speed_rail_line_v1` (High-Speed Rail Line)
- Model SHA-256 or procedural recipe ID/revision/hash: recipe `58e46729244ce89be0eeb4f6e051c5d7af85f3d45af90c8a3ce3ae69b3bf1c32`; program `b2f860b9e72abbc6b05c626661e83170115d13aab6f9fc360089867fda5ee0a5`; preview assembly `4eda6ccbc26702a15ffa9ffa22fe80186b9b5a4bb5a178f35945d3768339d08e`; modules `hsr_mast` eeab8f7b293c…; `security_fence` c79b5f1422b4…; `trackside_cabinet` 39b0429c902a…; `etcs_marker` 98f3e26bd1e0…
- Runtime source commit and integration-checklist version: registered in `8bc9b0758` on `claude/tender-albattani-fsnp50`, merged with `deployment-version` at `a13ef3872`; checklist 2026-09-24
- Reviewer, date, project URL, viewport/device/input: none; not run
- Vacant test site, protected reference, disposable test project: not set up
- Mixed-scene project and separate oversized-candidate project, if applicable: not set up
- Supported plot dimensions, axes/base datum, reshape/repetition behavior: fixed width 30 m; route 50 m to 2 km; one 50 m cycle repeats along `local_y`; base lift 0.025 m; `fixed_section_route`
- Authored storey programme: exact source/module hashes, shared whole-source origin, complete-assembly bounds centre, native-lock flag, and any bounded uniform-scale opt-in: N/A: street
- Supported terrain modes and connection capabilities: Prepared level site only (`preparedLevelOnly`). No motor lanes (`lane_count` 0), so public-road suggestions do not apply.
- Public-realm detail: metric plant height/footprint, paving scale, instance/texture budgets, and native close/aerial evidence: no textures; about 0.26 million triangles per km; close and aerial renders in `artifacts/rail-streets/hsr/v002/renders/` (ignored, reproducible) and `docs/rail-streets/review.jpg`
- Replacement furniture: complete mesh envelope/base datum, legacy-asset flag independence, component and in-site evidence: N/A: no replacement furniture
- Vegetation: canopy envelope, seeded prototype/triangle budget, furniture-scale comparison and route/entrance visibility: None: no trees inside the fences.
- Hardscape trees: paired bed/well style and footprint, visible root opening, shared surface datum, paving/joint exclusion, clear routes and sloped-contact evidence: N/A: no tree wells or grates
- Sports: sourced playing dimensions, full run-off/equipment reserve, measured net/rim heights, open gates, crown clearance and non-coplanar floor finishes; separate recreational adaptations: N/A
- Reference-image fidelity: exact image hashes, observed amenity cues, borrowed/inferred details, native before/after views and separately exported reusable amenity modules: N/A as fidelity: an original teaching section, not traced from photographs. The card image is a render of this model, locked as reference `8654d543033da56a325d1d78ad6fbcfd3f936c70b676161eaeb6cc6e130ae2ae`
- Native park seams and raised/cycle access: full-width closed-loop/bend support, local-origin furniture transforms, measured ramp/landing or track-entry height continuity; separate offline contacts from runtime slope walking: N/A: street
- Street asset handoff: metric band widths, metre-scale paving phase, supported full-width endpoints, native amenity contacts, and flush versus raised boarding/kerb limitations: Bands: margin 1.0, gravel maintenance road 3.5, ditch 2.0, formation 17.0 (rail track: 0.8 m embankment, 13 m crest), ditch 2.0, margin 4.5 m. Slab track; rail head 1.49 m above grade; contact wire 6.79 m above grade. Security fences 14.5 m either side of the centre. Route ends show the open cross-section of the track bed.
- Asset review status and separate publication/activation status: builder visual review only; no independent review; roster status `local-pilot-runtime-pending`; publication and activation not authorized
- Model Library storage check, configured bucket and result (building GLBs): N/A: street modules are static files under `frontend/public/street-kits/pilots/` in Git LFS
- Fresh installation: exact binding/recipe/module seed, byte readback, conflict preservation and disposable DB/bucket evidence: offline only: `tools/rail_streets/install.py` refuses conflicts, and a test proves the generator reproduces the registered row and module bytes; no database install run
- Evidence manifest location and hashes; durable shared location for delivery: `artifacts/rail-streets/hsr/v002/recipe.json` (ignored; rebuild with `tools/rail_streets/build.py`); no durable shared location yet

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
| C1 Exact identity | NOT TESTED | Backend contract admits the exact id, parent and module locks offline; not checked in the app |
| C2 Dimensions and transformations | NOT TESTED | Fixed width; route repeats one cycle. Offline engine test bends rails and wires along a curve; not checked in the app |
| C3 Full footprint ground support | NOT TESTED |  |
| C4 Freshness and late results | NOT TESTED |  |
| C5 Pedestrian continuity and public-road access for vehicle streets | NOT TESTED | No sidewalk-to-road connection exists on a closed rail corridor except the avenue's sidewalks; record what crossing students try |
| C6 Edit / Undo / save / reopen | NOT TESTED |  |
| C7 Failure and recovery | NOT TESTED |  |
| C8 Low/aerial views, exact capture and any AI-image comparison | NOT TESTED | Check the AI render prompt describes the track bed as rail track (offline profile test passes) |
| C9 Student controls and supported inputs | NOT TESTED |  |

For fixed-native buildings, record Q/E and rotation-field evidence at the actual
site latitude: metre dimensions/right angles preserved, exact model retained
after save/reopen. A displayed angle alone does not prove detailed-model fit.
| B1 Native placement | N/A | N/A: street, not a building |
| B2 Measured entrance evidence | N/A | N/A: street, not a building |
| B3 Entrance authoring | N/A | N/A: street, not a building |
| B4 Approach and setback recovery | N/A | N/A: street, not a building |
| B5 Foundation/stair/access design review | N/A | N/A: street, not a building |
| S1 Metric section | NOT TESTED | Offline: sections tile the width and resolve with zone types; check the drawn bands match |
| S2 Route and junction topology | NOT TESTED | Draw straight, bent and curved routes and a junction; rails and wires must stay continuous |
| S3 Shared grade and public connection | NOT TESTED | Prepared level ground only; record the result on natural ground (expected: refused with guidance) |
| S4 Clearance and target identity | NOT TESTED | Offline: nothing below 4 m in a train envelope; check modules near junctions and bends in the app |
| P1 Exact program and rigid amenities | N/A | N/A: street, not a park |
| P2 Shared park terrain | N/A | N/A: street, not a park |
| P3 Automatic remeasurement | N/A | N/A: street, not a park |
| P4 Park access and grade review | N/A | N/A: street, not a park |

## Bounded live matrix

Record actual measurements, steps, and relevant screenshots/API readback.
Mark type-specific gates N/A with a reason; keep applicable unrun cases open.

| Case | Status | Observation and evidence |
| --- | --- | --- |
| Level site; low views from multiple sides | NOT TESTED |  |
| Irregular site between mapped roads; natural and prepared modes; exposed site edge | NOT TESTED | Record ordinary-control boundary draw, approximate vs surveyed status, contained objects, pad edge and capture consequence. |
| Direct selection where an authored zone overlaps prepared ground | NOT TESTED | After reload, select the contained zone from the canvas, select the site elsewhere, then reselect the zone; confirm its edit handles and settings. |
| Proposed off-site public-road endpoint; Undo/Redo/reload and low junction grade | NOT TESTED | Confirm the mapped road visually; marker or stored height alone is insufficient. |
| Fixed street bend through ordinary controls | NOT TESTED | Add bend point, drag the route handle, then reload and compare centreline, compiler identity and handle count. |
| Long repeatable route and exact edit datum | NOT TESTED | Draw beyond the former length cap; retain native section/module scale, complete geometry and sparse handles. Extend, Undo/Redo and reopen. Verify handles and pointer picks use prepared ground rather than hidden tiles. Record browser-tested length separately from validator maximum; retain fixed bridge/reference limits. |
| Repeated street travel-surface ownership | NOT TESTED | Sample full native road/cycle widths at source-fixture centres, module seams, endpoints and a partial final module in both directions. Keep pedestrian access links and authored local crossings/markings, with no repeated full-ROW false sidewalk across travel bands. Check explicit junction clipping/crossings separately; geometry rays do not establish a native visual pass. |
| X-to-T and T-to-X recovery | NOT TESTED | Preserve a complete junction between the same streets while allowing a supported change in arm count. Check for a clamped spur, multiple crossings, near-angle-limit gestures and saved/reopened topology. |
| Narrow pedestrian section and bend control retention | N/A | N/A: not a narrow-pathway adapter; fixed section with its own width |
| Nonexclusive ground paths across building and park plots | N/A | N/A: surface-path variants only |
| Native street production recipe and unchanged Apply | NOT TESTED | Backend catalogue, exact profile/revision/module locks, editor variant/width, reload without DEV marker; no fallback to a sibling. |
| Finite street draft and connected section replacement | NOT TESTED | Exact variant/archetype/width before recipe creation, real existing zone ID, unchanged neighbours, no persisted preview flag; invalid saved recipes and lost junctions reject. |
| Angled join and short-arm recovery | NOT TESTED | Width-aware snapping, sampled-curve node identity, owned pavement/sidewalk surface, no crossing-only fallback on unsupported joins. |
| Sloped site; contacts and route continuity | NOT TESTED |  |
| Prepared level: actual native step pick, current review and route; unresolved export guard | N/A | N/A: building step pick |
| Revision-locked fixed-native step pick | N/A | N/A: building step pick |
| Native park short arrival and sidewalk width | N/A | N/A: park gateway |
| Multiple low steps: choose street-facing step; opposite-side rejection and Cancel preserve saved link | N/A | N/A: building entrances |
| Edge/unsupported case and inward recovery | NOT TESTED |  |
| Local ground hole: unaffected object works; affected object rejects; recovery/reload/export guard | NOT TESTED |  |
| Park measurement unavailable: visible warning, move/resize or explicit prepared-level recovery | N/A | N/A: park |
| Hillside park profile: whole-site and house-route verification still gates capture | N/A | N/A: park |
| Supported minimum/maximum size and rotation | NOT TESTED |  |
| Edit during pending ground / tile refinement | NOT TESTED |  |
| Delete / Undo / Redo; referenced route target | NOT TESTED |  |
| Interrupted navigation or measurement | NOT TESTED |  |
| Interrupted building asset download; Retry after an unrelated save | N/A | N/A: building asset; street modules are static files |
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
| Default park programme and status text | N/A | N/A: park |
| Export file delivery | NOT TESTED | Separately verify settled capture, preview, actual Download action and saved file. Record browser cancellation honestly; extracting a data URL only proves the PNG content. |
| Paid-image cost and fidelity review | NOT TESTED | Before calling: selected engine, exact server reservation, balance and call count. After calling: audit debit, same-camera comparison, automatic result, human status and fallback. Stop further calls if accounting is unexplained. |

## Entrance measurements (buildings)

N/A: a street has no building entrances. The template text below is kept for reference only.

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

- Participant: actual novice / instructor / agent simulation: none; not run
- Empty-project UI authoring, retries, save waits and ordinary recovery: not run
- Developer/API intervention (read-only verification separately): none
- Prerequisites discoverable using actual control labels: not checked. The street needs a prepared level site; the app says so when a student starts drawing without one

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

- Focused test commands/results and reused shared-test evidence: `python3 -m pytest tools/rail_streets` 24 passed; `npx vitest run src/features/pickPlace/railStreets.test.ts` 15 passed; full frontend suite 4,612 passed; backend street and catalogue tests 371 passed
- Type-check/lint or relevant backend/compiler checks for source changes: `npm run type-check` and eslint on the changed files pass
- Console/network failures and recovery: not run
- Original fixture preservation and final disposable-project state: not run
- Oblique sky/ground-gap distinction; fallback excluded from picking/support: not run
- Exact generation inputs preserved separately from later corrected previews: the build is deterministic; v001 was superseded by v002 (fence footings kept inside each panel, aspens kept inside the corridor); only v002 is registered
- Assisted/native-size trial versus ordinary student authoring and route connectivity: not run
- Park-to-street/entrance clearance in preview, drag and save; bounded fit retains size/rotation: N/A: street
- Park approach clears neighbouring parks, fixed equipment and full-width street/boundary barriers: N/A: street
- Report route evidence matches the scene; stale evidence rejected; absent evidence remains uncertain: not run
- Connected bend/body/section edit retains every renderable T/X patch; neighbours unchanged: not run
- Whole-site graph matches road-only graph; bounded road-ground recovery after new tiles: not run
- Open failures, untested advertised features, owner and next bounded action: every NOT TESTED row; owner: the runtime trial; next action: the rail-specific checks at the end
- Runtime integration decision: NOT REVIEWED
- Asset visual decision (separate): NOT REVIEWED
- Publication/activation authorization (separate; cite actual authorization): none

A passing solver, successful compiler, CLI preflight, or attractive screenshot
alone is not student-ready acceptance. Do not invent a review or approval.

## Two-endpoint bridge draft and persistence regression

N/A: not a bridge. The template text below is kept for reference only.

For route-capable bridges, verify first-click hover, both confirmed endpoints plus cursor motion, extra click endpoint adjustment, Enter/Finish and the complete click/click/double-click event sequence. Coordinates and sampled-height arrays must retain the same two endpoints; ordinary street bend/duplicate behavior must remain unchanged. Repeat endpoint edits against the actual PostgreSQL enum-backed API, then Undo/Redo/reload and download the exact source. Mocked session tests alone do not prove a valid database query. Keep original fixed saves and production gates distinct from the new route revision.


## Source-derived bridge route contracts

N/A: not a bridge. The template text below is kept for reference only.

Use the complete occupied geometry to define each endpoint interval, including skew caps, tower backs and full stair flights. Preserve original source bytes and material ownership; record derivative-only stairs/approaches explicitly. At minimum span, complete landscape/support companion assemblies must fit rather than silently disappear. Keep road/rail lane counts tied to source programmes, not generic deck widths. Compare compiled metric envelopes at the same millimetre precision while retaining immutable source locks.

For overlapping stair flights, filter candidate walking surfaces by current foot height before choosing the nearest plan surface. Exact skew tread polygons can be necessary; an inscribed strip may leave corner holes. Offline ray and prior-height traversal tests do not replace browser walking. Endpoint edit, Undo/Redo, PostgreSQL persistence, full reload, source capture and at-grade connection acceptance remain separate evidence gates.

## Rail-specific checks for the runtime trial

- Draw it on a prepared level site: straight 50 m and 300 m routes, a bent route, a curved route of about 500 m, and a 2 km route. Rails, ballast or slabs, curbs and wires must run continuously through bends and across every 50 m cycle seam.
- High-speed lines have no level crossings. The engine still draws a flush junction where another street meets it, cutting into a 0.8 m embankment. Record what students see and decide whether junctions should be refused or shown as a bridge.
- The new parent archetype `high_speed_rail_corridor` must reach the picker, backend trust index and saved recipe exactly; check it survives save and reopen.
- Real lines need curve radii of several kilometres; the drawing tools do not enforce that. Record whether students need guidance.
- Save, reload and reopen: the exact variant, width, archetype and recipe revision return, with no fallback to a sibling street.
- Capture an aerial and a low view, and check the AI render prompt names the track bed as rail track.

## Offline evidence (not runtime passes)

- `tools/rail_streets/test_rail_streets.py`: the generator reproduces the registered row and module bytes; sections tile the width; every module fits the corridor and its cycle; nothing below 4 m stands in a train envelope; rails are standard gauge and continuous; each cantilever ends on its contact wire.
- `frontend/src/features/pickPlace/railStreets.test.ts`, on the real street engine: the card is an ordinary drawable street card; the track bed resolves as rail track; straight, bent, curved and 2 km routes are accepted; every module repeats; rails and wires bend along a curve end to end.
- Backend: the native street contract admits the exact id with a trusted parent and module locks.

## Open items by classroom impact

- **Blocker until run:** every NOT TESTED gate above. None has been observed in the app.
- **Possible blocker, to check:** how junctions meet the raised track bed and the high-speed embankment, which real lines never cross at grade.
- **Follow-up:** the open cross-section at route ends; no stations, platforms, crossings or trains.
