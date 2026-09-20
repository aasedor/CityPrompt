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
| Edge/unsupported case and inward recovery | NOT TESTED | |
| Supported minimum/maximum size and rotation | NOT TESTED | |
| Edit during pending ground / tile refinement | NOT TESTED | |
| Delete / Undo / Redo; referenced route target | NOT TESTED | |
| Interrupted navigation or measurement | NOT TESTED | |
| Failed/conflicting save; retry without lost edits | NOT TESTED | |
| Save/reload/reopen; exact persisted identity | NOT TESTED | |
| Capture blocked while stale, then succeeds | NOT TESTED | |
| Student-authored placement and connections | NOT TESTED | |

## Entrance measurements (buildings)

For each supported entrance, record the native coordinate frame and base datum,
door/step/landing edge coordinates, clear width, route direction, measured plot
anchor, `scaleWithPlot` behavior and reference dimensions. Link front/side/low
views to the exact model hash. Record repeated-house or multiple-entrance limits.
These are reviewed measurements; this template does not install runtime metadata.

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
