# Runtime integration review — <archetype / exact variant>

Copy this template into the candidate evidence package. Complete it using
[Runtime integration for every archetype](ARCHETYPE_RUNTIME_INTEGRATION.md).
Replace this relative link with the repository document path if copied elsewhere.
Default status is NOT TESTED. Do not prefill a pass from another archetype.

## Candidate and scope

- Kind: building / street or path / park or open space
- Archetype ID and exact variant ID:
- Model SHA-256 or procedural recipe ID/revision/hash:
- Runtime source commit and integration-checklist version:
- Reviewer, date, project URL, viewport/device/input:
- Vacant test site, protected reference, disposable test project:
- Supported plot dimensions, axes/base datum, reshape/repetition behavior:
- Supported terrain modes and connection capabilities:
- Asset review status and separate publication/activation status:
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
| C5 Pedestrian continuity | NOT TESTED | |
| C6 Edit / Undo / save / reopen | NOT TESTED | |
| C7 Failure and recovery | NOT TESTED | |
| C8 Low/aerial views and exact capture | NOT TESTED | |
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
| Sloped site; contacts and route continuity | NOT TESTED | |
| Prepared level: actual native step pick, current review and route; unresolved export guard | NOT TESTED | |
| Multiple low steps: choose street-facing step; opposite-side rejection and Cancel preserve saved link | NOT TESTED | |
| Edge/unsupported case and inward recovery | NOT TESTED | |
| Local ground hole: unaffected object works; affected object rejects; recovery/reload/export guard | NOT TESTED | |
| Park measurement unavailable: visible warning, move/resize or explicit prepared-level recovery | NOT TESTED | |
| Supported minimum/maximum size and rotation | NOT TESTED | |
| Edit during pending ground / tile refinement | NOT TESTED | |
| Delete / Undo / Redo; referenced route target | NOT TESTED | |
| Interrupted navigation or measurement | NOT TESTED | |
| Failed/conflicting save; retry without lost edits | NOT TESTED | |
| Save/reload/reopen; exact persisted identity | NOT TESTED | |
| Generate to 3D: panel recipe matches locked compiler; reload and inspect visible models | NOT TESTED | |
| Capture blocked while stale, then succeeds | NOT TESTED | |
| Student-authored placement and connections | NOT TESTED | |

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

Use the practical classroom target in `CLASSROOM_READINESS_PLAN_2026-09-20.md`.
For every open item, record whether it prevents authoring, plausible geometry,
reliable recovery or faithful presentation (blocker), or is a finer concept
limitation (follow-up). Keep visual acceptance and publication decisions separate.
Do not require construction-level detail to pass a concept-design classroom pilot.
When ground rejects a placement/site, verify its review highlights the actual
rejected samples and offers a usable recovery through ordinary controls.

## Verification and decision

- Focused test commands/results and reused shared-test evidence:
- Type-check/lint or relevant backend/compiler checks for source changes:
- Console/network failures and recovery:
- Original fixture preservation and final disposable-project state:
- Open failures, untested advertised features, owner and next bounded action:
- Runtime integration decision: NOT REVIEWED
- Asset visual decision (separate): NOT REVIEWED
- Publication/activation authorization (separate; cite actual authorization):

A passing solver, successful compiler, CLI preflight, or attractive screenshot
alone is not student-ready acceptance. Do not invent a review or approval.
