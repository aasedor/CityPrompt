# Standalone sidewalks — bounded runtime review

Date: 2026-10-13. Initiative: `codex/standalone-sidewalks-2026-10-13`.
Integration baseline: `cd7f824ab`. Reviewer: Codex browser trial.
Checklist: `docs/ARCHETYPE_RUNTIME_INTEGRATION.md` and runtime review template.

Three conceptual pedestrian surfaces use the existing narrow-pathway-v1
procedural adapter. Units metres; X across, Y along, Z up; surface-centre
origin; 6 m authoring fixture and 0.025 m display lift. Fixed widths;
route length and bends use existing drawing/editing. No motor lanes, raised
curbs, furniture, trees, working-door or repeatable-floor metadata.
Supported terrain: prepared level site. Natural/sloped terrain is unsupported.
These are design references, not certified Calgary standard sections.

The first narrow pilot was drawn and visually reviewed before the bounded
three-profile installation. Existing data entries and historic fingerprints
are preserved. Generator rejects conflicting IDs without writing and backs up
all touched manifests. Originals and output: `D:/CityPrompt-sidewalks-2026-10-13`.

Trial: http://127.0.0.1:5184/projects/d8491f31-543f-4c62-bb4b-2db329539e2c
Vacant field: Range Rd 284, Calgary; approximate unsurveyed rectangular
prepared site. Desktop browser/mouse/keyboard; Balanced 3D setting;
1280x720 initially, resized by user to 2177x1246 during review.
No paid image/video generations. Photographic picker illustrations were made
with built-in imagegen; contextual buildings/planting are not sidewalk geometry.

## Verification

- 46 focused frontend tests passed; TypeScript check passed.
- 27 focused backend tests passed.
- Whole catalogue byte audit:156 choices, 514 dependencies, 0 failures.
- Broader public-realm suite:99 passed, 1 pre-existing stale Calgary-local variant
  expectation failed; unrelated manual/draft variants were already present.
- Exact street editor identity now uses canonical choice ID, avoiding accidental
  selection of the earlier Concrete neighbourhood walk sharing the parent ID.
- Three previews load; all 3 routes draw and save; exact fixed widths appear in
  editor; edited routes remain after browser reload. Urban bend reshaped;
  narrow route moved; urban delete/Undo restored it. Neighbourhood unchanged
  Apply retained its exact variant. No extrapolation to all edit combinations.
- Urban eye-level walk moved along the paving with its edge strip flush.
  Actual 3D capture preview retained the sidewalk, paving and position.
- Student-laptop/frame-time/memory benchmarks and paid AI fidelity: NOT TESTED.

## Evidence

Ignored browser evidence: `picker.png`, `urban-walk.png`, `capture-preview.png`
and `narrow-walk.png` (narrow walking camera faces away from route; not evidence
of continuous route traversal). Recipe manifests, immutable backups,
preservation receipts and test/audit logs are beside these screenshots.
Publication remains candidate status; local catalogue exposes supported routes.
No deployment or main merge. New photographic PNGs use the existing Git LFS policy.

## Standalone narrow sidewalk — standalone_narrow_sidewalk_v1

- Recipe/assembly SHA256: `322b6b9382cd811e18c81ae6c23e8d4868fe48d840c20dbea094bf7dbbb1ecf1`
- Program SHA256: `bde3ea5956bb1992baff8d7886f1dbdadeb0368484394ce0879d3bea13c87b61`
- Hero SHA256: `dabc9ecf7d4fd90e86e140294a80ed0b9bb8f27b527d7c9ead15426630cd0044`
- Width:1.5 m; supported length:2–300m.
- Finish: plain concrete.

| Gate | Status | Evidence / limitation |
|---|---|---|
| C1 Exact identity | PASS | Recipe hash, exact picker/editor ID; frontend/backend contract tests |
| C2 Dimensions/transforms | PASS | Fixed metric section; straight/reversed/bent/min-max geometry tests |
| C3 Full-footprint support | PASS | Prepared level site browser layout; unsupported terrain remains gated |
| C4 Freshness/late results | NOT TESTED | No interrupted-measurement trial for this exact recipe |
| C5 Pedestrian continuity | NOT TESTED | Grounded surface reviewed; full exact-route traversal not completed |
| C6 Edit/save/reopen | PASS | All 3 saved/reloaded; representative move/reshape/delete/Undo; not every combination |
| C7 Failure/recovery | PASS | Generator conflict preservation and backend width/length rejection tests; live conflicting save NOT TESTED |
| C8 Low/aerial/capture | NOT TESTED | Aerial placement passed; individual close capture not retained |
| C9 Controls | PASS | Picker/drawing/section editor; fixed-width route contract |
| S1 Metric section | PASS | No lanes/curbs/markings; geometry width checks |
| S2 Route/junction topology | PASS | Automated mixed-width joins/crossings; live joined-road case NOT TESTED |
| S3 Shared grade/public connection | N/A | Prepared-level pedestrian surface; no vehicle-road access claim |
| S4 Clearance/target identity | PASS | No fixtures; exact variant selected and unchanged Apply regression |
| B1–B5 / P1–P4 | N/A | No building or park program in this initiative |

## Standalone neighbourhood sidewalk — standalone_neighbourhood_sidewalk_v1

- Recipe/assembly SHA256: `d859f4e399f17e9f6db270c6630fbc43dab8a4e355d61c880f558a102ca78b74`
- Program SHA256: `cd0acec45a0a0194b59d260e7f518c47eafc12b0ea3991dcc082cf8476436ba0`
- Hero SHA256: `abaa73c45e121bf0cc4dee215cc4dee03f9357b7fa232e1d825986fa4dd64b13`
- Width:2.0m; supported length:2–300m.
- Finish: concrete with 1.5 m transverse joints.

| Gate | Status | Evidence / limitation |
|---|---|---|
| C1 Exact identity | PASS | Recipe hash, exact picker/editor ID; frontend/backend contract tests |
| C2 Dimensions/transforms | PASS | Fixed metric section; straight/reversed/bent/min-max geometry tests |
| C3 Full-footprint support | PASS | Prepared level site browser layout; unsupported terrain remains gated |
| C4 Freshness/late results | NOT TESTED | No interrupted-measurement trial for this exact recipe |
| C5 Pedestrian continuity | NOT TESTED | Grounded surface reviewed; full exact-route traversal not completed |
| C6 Edit/save/reopen | PASS | All 3 saved/reloaded; representative move/reshape/delete/Undo; not every combination |
| C7 Failure/recovery | PASS | Generator conflict preservation and backend width/length rejection tests; live conflicting save NOT TESTED |
| C8 Low/aerial/capture | NOT TESTED | Aerial placement passed; individual close capture not retained |
| C9 Controls | PASS | Picker/drawing/section editor; fixed-width route contract |
| S1 Metric section | PASS | No lanes/curbs/markings; geometry width checks |
| S2 Route/junction topology | PASS | Automated mixed-width joins/crossings; live joined-road case NOT TESTED |
| S3 Shared grade/public connection | N/A | Prepared-level pedestrian surface; no vehicle-road access claim |
| S4 Clearance/target identity | PASS | No fixtures; exact variant selected and unchanged Apply regression |
| B1–B5 / P1–P4 | N/A | No building or park program in this initiative |

## Standalone urban sidewalk — standalone_urban_sidewalk_v1

- Recipe/assembly SHA256: `4ff46e23abc65c10c77525e82f5d5b8c614218b9c920c0cfbed72060f62f165f`
- Program SHA256: `ad796579bdf9f8e2216b2778e264ce19dbc8e96a37042109a28c3ab0cce7b0df`
- Hero SHA256: `315a0b4a08fb04afccc1ffb52d7fcdb19d3aa85b00b41efe0a733718297f5ae6`
- Width:3.0m; supported length:3.0–300m.
- Finish: 0.6 x 0.4 m paving and one 0.2 m flush charcoal strip within full width.

| Gate | Status | Evidence / limitation |
|---|---|---|
| C1 Exact identity | PASS | Recipe hash, exact picker/editor ID; frontend/backend contract tests |
| C2 Dimensions/transforms | PASS | Fixed metric section; straight/reversed/bent/min-max geometry tests |
| C3 Full-footprint support | PASS | Prepared level site browser layout; unsupported terrain remains gated |
| C4 Freshness/late results | NOT TESTED | No interrupted-measurement trial for this exact recipe |
| C5 Pedestrian continuity | PASS | Urban walking view and forward movement; no raised curb |
| C6 Edit/save/reopen | PASS | All 3 saved/reloaded; representative move/reshape/delete/Undo; not every combination |
| C7 Failure/recovery | PASS | Generator conflict preservation and backend width/length rejection tests; live conflicting save NOT TESTED |
| C8 Low/aerial/capture | PASS | Urban low view and exact 3D preview; paid AI not tested |
| C9 Controls | PASS | Picker/drawing/section editor; fixed-width route contract |
| S1 Metric section | PASS | No lanes/curbs/markings; geometry width checks |
| S2 Route/junction topology | PASS | Automated mixed-width joins/crossings; live joined-road case NOT TESTED |
| S3 Shared grade/public connection | N/A | Prepared-level pedestrian surface; no vehicle-road access claim |
| S4 Clearance/target identity | PASS | No fixtures; exact variant selected and unchanged Apply regression |
| B1–B5 / P1–P4 | N/A | No building or park program in this initiative |
