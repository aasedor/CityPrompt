# Currie shared entrance landing pilot — 20 September 2026

## Result and scope

The shared entrance solver now separates a level building-end landing from a
stair flight. The high Craftsmen and low Edwardian were inspected in the live
vacant Currie copy. The tighter Craftsman initially failed the new space check;
an ordinary plot drag recovered it. Move, Undo, Redo, reload and free exact 3D
export passed. This completes the bounded landing/flight slice, not student-ready
architectural or accessibility acceptance.

Worktree: `C:/dev/CityPrompt-grounding-edit-race`, branch
`codex/grounding-edit-race-hardening`, source based on `7e7ebd920`.
Local frontend `http://127.0.0.1:5174`; real backend and measured terrain.
Browser: Chromium, 1440 × 900, pointer and normal editor controls. No mocks,
paid generation, native model edits, catalogue activation or push.

## Shared behavior

- Rises over 0.04 m reserve a 1.2 m level landing at the authored step foot.
  The remaining flight uses the existing maximum 0.18 m rise and minimum
  0.28 m going, with a new 0.40 m maximum concept going. Spare street-end run
  becomes a level approach area. Near-level routes remain walks.
- Landing and tread footprints must clear the measured ground and existing
  obstacle/domain checks. Terrain is not cut or flattened. Flight stringers
  stop at the landing rather than crossing its level surface.
- A route that fits bare stairs but lacks landing space reports
  `entrance_landing_run_too_short`, with guidance to move the plot, choose
  another entrance or use flatter ground. Saved anchors are not rewritten.
- Geometry records its sections in `entranceApproachSections`; street capture
  ownership and the original building owner are retained.

These dimensions are shared concept-layout choices. They do not establish
code compliance, structural support, edge protection or accessible access.

## Browser findings and fixture state

Protected original: `f5bffc94-def9-4c43-942e-9ae7411872e9`.
Disposable layout: `54bb844c-1ff4-4d67-bc7f-0c8c36d0030e`.

| House | Total route | Street-to-base rise | Flight | Building landing |
| --- | ---: | ---: | ---: | ---: |
| West 2 Craftsman | 5.318 m | 2.349 m | 14 steps / 4.118 m | 1.2 m |
| West 3 Craftsman, recovered | 4.565 m | 1.789 m | 10 steps / 3.365 m | 1.2 m |
| West 4 Edwardian | 4.185 m | 0.414 m | 3 steps / 1.2 m | 1.2 m |

The Edwardian also has a 1.785 m level street-end area. The native house steps
continue above the generated landing, so these rises are not total door rises.
All four infills remain ready, including two descending approaches and one
near-level walk. Their scene section metadata was recorded; their complete
visual acceptance was not repeated in this slice.

West 3 initially had only 3.400 m total route: insufficient for ten minimum
goings plus the landing. Picking its actual low step in Connections displayed
the new guidance. Cancel preserved its saved entrance. A browser body drag
moved the plot 1.165 m west and 0.086 m north; the landing then fit. Undo restored
the exact old coordinates and warning; Redo and reload restored the new
coordinates, seven approach meshes and zero grounding issues.

**The recovered west 3 position is retained in the disposable copy.** Its zone
is `b8945115-5442-46e1-8c06-ae0732a8d24f`, building
`dae4c628-8573-44ac-a891-cf249e374f46`. Read-only polygon checks found the whole
plot inside the boundary, with 3.396 m boundary clearance and zero intersection
area with all other plots, street and park. All other copy coordinates and
all saved entrance anchors match the start-of-slice snapshot. The full original
zone response matches the preceding pilot snapshot exactly.

The ordinary Image panel's **Export current 3D view · free** opened an exact
capture preview. Download render saved the inspected PNG showing the landing,
shortened flight, native steps and surrounding context. No AI image was used.
The landing failure was checked live; blocked export for that specific reason
was not separately exercised in the browser. Existing capture gating tests pass.

## Checks and evidence

86 tests passed across `buildingEntranceApproach`, `BuildingEntranceApproaches`,
`BuildingGroundProblems`, `buildingGroundContact`, `pedestrianCapture`,
`pickBuildingEntrance`, `ConnectionEditor`, and `pedestrianConnections`.
`npm run type-check` and ESLint on all five changed source/test files passed.
New regression cases cover a level building landing, insufficient landing run,
compact low-rise flight, short near-level walk, landing/terrain collision, and
readable selectable repair guidance. Descending and rotated routes remain covered.

External evidence: `C:/dev-artifacts/CityPrompt/grounding-batch-a/`:

- `landing-baseline-zones.json`, `landing-recovery.json`: exact starting state
  and move/Undo/Redo/reload responses plus section metadata.
- `landing-final-verification.json`, `landing-clearance.json`: protected-original
  equality, saved-anchor preservation and measured polygon clearance.
- `landing-too-short-dialog.png`, `landing-undo-warning.png`: distinct failure
  evidence, preserved separately from the successful views.
- `landing-Shared-street-west-2.png`, `landing-Shared-street-west-3.png`,
  `landing-Shared-street-west-4.png`: inspected oblique views.
- `landing-free-export.png`, `landing-free-export-panel.png`: inspected exact
  capture and its download preview. Evidence hashes: `landing-evidence-sha256.json`.

Key SHA-256 records (local evidence, not a shared backup):

| File | SHA-256 |
| --- | --- |
| `landing-recovery.json` | `1bad4e4445692fecd9b7db6d0f83a476fc5542b07d64edd06b549846a3607fa5` |
| `landing-final-verification.json` | `70223b0925b86f6bd2d2fec5942295f9625207aea24871428cf7216679c0f298` |
| `landing-free-export.png` | `f264a3ef8bc1a70e8deacdd709c57e3fd5830d56af6cf6cbb1d13213a2cbf826` |

The first Undo script checked before React published its new grounding issue;
the warning appeared normally. Verification then waited for the actual warning
and seven-mesh recovered state. The first export harness expected an immediate
download; the app correctly opened its preview and Download render completed.
These were harness timing/workflow errors, not reproduced application defects.
Page-error collection during final readback was empty; no full network audit
or paid-image availability test was performed. Evidence remains local-only.

## Next bounded unit

Stay on Astra for edge protection and exposed-foundation/landing-support design.
Use both Craftsmen and the low Edwardian as contrasting cases; inspect side and
pedestrian views and exact capture. Do not add generic rails and call the whole
route accepted. Check clear width and frontage furniture, then decide how the
student workflow handles a site without a supported accessible alternative.
The novice placement-to-presentation journey, touch/keyboard-only 3D authoring,
repeated-house entrances and the remaining shared checklist gates remain open.

The shared integration checklist and per-archetype template now require
landing/flight measurements, insufficient-space recovery and separate design
limitations for every future applicable archetype. RLASM 6.1 and its executable
quality rules are unchanged; no machine-readable method companion needs revision.
