# Currie Craftsman and Edwardian entrance pilots

20 September 2026. Runtime under test: `13438b48a`, including direct-pick
implementation `d1c1c25a2`. Worktree: `C:/dev/CityPrompt-grounding-edit-race`.
This is a scoped runtime interaction review of existing assets, not new asset
approval or a completed archetype readiness review.

## Exact candidates

Test project: `54bb844c-1ff4-4d67-bc7f-0c8c36d0030e`, the disposable vacant
Currie seven-house layout. Browser viewport: 1440 × 900, desktop mouse.
Existing local frontend/backend at 5174/8000; authenticated smoke-test user.

| Candidate | Identity and exact delivered bytes |
| --- | --- |
| Shared street west 3 | `vancouver_craftsman_bungalow` / `craftsman_classic`; zone `b8945115-5442-46e1-8c06-ae0732a8d24f`; 1,058,796-byte GLB; SHA-256 `08e2c40e4af611e3e7c9e3ad1e987e8adeb2d1b5443a510211f00a8f70e3d014` |
| Shared street west 4 | `toronto_edwardian_foursquare` / `toronto_foursquare_red_brick`; zone `1b03b8cb-09e9-48e7-8f65-9f1a12bea6be`; 10,282,872-byte GLB; SHA-256 `3a6848fc6aa78151f3059b75f441092c4c1ff60ef4c17ccd0028ea27153c9dd7` |

Hashes were computed from the model URL in each saved assembly recipe, using
the actual returned GLB bytes. Both plots retained 90-degree rotation and
unscaled native models. Their starting plot sizes were 15 × 24 m and 15 × 22 m.

## Browser results

Actual pointer events selected projected, measured native step surfaces.
Camera helpers framed the views; no application selection callback or direct
API write was used to author the trial edits. API reads checked persistence.

| Bounded check | Craftsman | Edwardian |
| --- | --- | --- |
| Select house, open Connections, pick native lowest step | PASS | PASS |
| Draft returns with current-ground fit feedback | PASS | PASS |
| Retain authored width, zero entrance height and unscaled offsets | PASS: 1.8 m | PASS: 1.65 m |
| Save picked point | PASS: final trial (1.106, -10.345) | PASS: trial (0.1, -8.965) |
| Undo restores prior anchor; Redo restores exact picked anchor | PASS | PASS |
| Reload retains saved anchor | PASS | PASS |
| Ordinary selected-house body drag updates plot without moving camera | PASS | NOT TESTED |
| Insufficient setback gives recovery guidance after repicking | PASS | NOT TESTED |
| Undo movement restores exact footprint, repick returns valid fit | PASS | NOT TESTED |
| Restore original entrance through dialog and verify after reload | PASS | PASS |

For the Craftsman, two small body drags moved the plot approximately 1.083 m
east and 0.086 m south from the starting copy. The first half of that move still
allowed an approach; the second produced the expected insufficient-run message:
move the building farther from the street, choose another entrance, or use
flatter ground. Cancel retained the already saved anchor. Two Undo actions
restored the exact starting coordinate array, and repicking returned a valid
fit. The recovered pick was saved, undone, redone and reloaded successfully.

The native step is in `CLAY_STONE` on the Craftsman and `CLAY_FOUNDATION` on
the Edwardian. The shared picker handles both because it uses the actual model
hit and measured pad geometry, rather than a material or mesh-name lookup.
The Craftsman's lowest native tread top is approximately 0.214 m above its
native base near model-local Z = 11.05 m; the Edwardian's is approximately
0.17 m near Z = 10.255 m. These are asset-specific native coordinates, not
plot anchors or reusable defaults. They must pass through the actual model
transform. The saved approach anchor remains at the outer foot/base level.

Final readback verified all ten copy coordinate arrays and every saved entrance
match the pre-trial snapshot. All seven houses were visible in ready measured
ground with no building-ground issues. The protected original
`f5bffc94-def9-4c43-942e-9ae7411872e9` was not edited; its ten coordinate arrays
still match the earlier saved original snapshot. Page-error checks were empty.

No production source or catalogue assets changed. No paid generation or push
occurred. Existing source checks remain the 46-test direct-pick regression run,
type-check and lint recorded in the [first pilot](CURRIE_3D_ENTRANCE_PICK_BROWSER_QA_2026-09-20.md).
There was no source change requiring those tests to be repeated in this slice.

## Foundation design findings and next unit

Read-only scene/API measurements after restoring the fixture:

| House | Street-to-native-base rise | Plan approach length | Current concept treads |
| --- | ---: | ---: | ---: |
| West 2 Craftsman | 2.349 m | 5.318 m | 14 |
| West 3 Craftsman | 1.793 m | 3.400 m | 10 |
| West 4 Edwardian | 0.414 m | 4.185 m | 3 |

These rises stop at the model base; the native house steps continue above it.
Counts are calculated from the current 0.18 m maximum concept rise. They are
not building-code or accessibility findings. The two Craftsman approaches
remain long and unguarded; the Edwardian spreads a small rise across a long
route. The high base and the join between native steps and generated approach
still need design review despite a clear solver issue list.

The next bounded design unit should use these contrasting cases to reserve
space for a level transition at the native-step foot and a distinct stair
flight, then assess edge protection and unobstructed frontage. Recheck run and
terrain support after reserving landing space; a route that fits today's
all-tread geometry may become unresolved. Keep recovery explicit rather than
lowering the native model into terrain or adding a whole-site flat platform.
Review accessible alternatives separately. Do not claim that adding rails
alone resolves foundations, circulation, or student readiness.

Implement any accepted geometry policy in the shared approach system and its
tests, then pilot on both a high Craftsman and low Edwardian before scaling.
Exact landing/guard geometry and thresholds have not been selected or tested
in this checkpoint. Astra remains useful for that design and visual-review unit.

## Scope and evidence

This extends entrance-authoring evidence to two additional families. Touch,
keyboard-only 3D picking, multiple entrances/repeated homes, minimum/maximum
plot sizes, failed-save injection, a complete novice journey and final capture
were not tested in this slice. The original layout was API-authored. These
results do not close all C/B gates in the shared archetype checklist.

External evidence root: `C:/dev-artifacts/CityPrompt/grounding-batch-a/`.
Keep the saved files rather than rerunning fixture-mutation scripts blindly:

- `next-pilot-baseline-zones.json`, `next-pilot-final-verification.json`:
  exact before/after state, recipes, model hashes and final ground status.
- `next-persist-Shared-street-west-3.json`,
  `next-persist-Shared-street-west-4.json`: save/Undo/Redo/reload readback.
- `next-setback-recovery.json`: failed position, actual guidance and exact
  recovered footprints. The failure dialog was visually inspected; the working
  screenshot was subsequently overwritten by the successful recovered pick.
- `next-restored-Shared-street-west-3.png`,
  `next-restored-Shared-street-west-4.png`: inspected restored pedestrian views.
- `next-foundation-review.json`: measured rise/run evidence for the next unit.

One initial Craftsman persistence script lost a response body across browser
navigation; the revised script completed Save/Undo/Redo/reload and retained
the evidence above. A read-only verification script initially used the wrong
recipe envelope; corrected readback then verified model bytes and restoration.
Neither test-harness error is reported as an application failure.
