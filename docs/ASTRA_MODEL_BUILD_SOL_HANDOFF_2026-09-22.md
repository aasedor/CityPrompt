# Astra model phase → Sol runtime phase

User direction, 22 September: build the catalogue models using Astra first,
then test them with Sol to avoid expensive browser work on Astra. This supersedes
the earlier ordering that put entrance integration before further model work.

Worktree: `C:/dev/CityPrompt-grounding-edit-race`.
Branch: `codex/astra-catalogue-models`, based on `f80fda754`.
External batch: `C:/dev-artifacts/CityPrompt/astra-model-batch-2026-09-22/`.

The user then requested a few more models before any combined Sol trial. This bounded batch adds:
[timber community hall and tilt-wall warehouse](SERVICES_MODEL_BATCH_2026-09-22.md).
Include their final reviewed packages in the same test session; do not start
browser testing merely because the earlier housing packages are ready.

No browser checks, runtime seeding, new API/image-provider calls, catalogue
activation or publication belong to this model phase. Blender rendering and
separate source-locked model review do belong here. Browser acceptance remains
NOT TESTED until the user switches to Sol and continues.

## Model inventory

| Model | Current package | Status |
| --- | --- | --- |
| Side-by-side duplex | `catalogue-cycle-2026-09-05/duplex/v004` | Previously built and independently reviewed; existing local trial. Multiple entrance integration still open. |
| Montreal stacked duplex | `catalogue-batch-2026-09-06/montreal-v004` | Recovered intact; fresh separate holistic clay review passes. Ready for Sol trial. |
| Brick courtyard entrance building | This batch, `courtyard-v004` | Delivery, preflight and independent holistic clay review pass. Ready for Sol trial. |
| Cedar/black townhouse row | No new model | Source reconciliation required: current four-home hero conflicts with older four-storey row views. |
| Timber/glass apartments | No new model | Source reconciliation required: current variant image is a previous 3D preview; alternate photographic views depict different massing and central recess. |

The last two source sets have not been blended into invented hybrid buildings.
The user was asked whether to retain the current cards and prepare compatible
references, or use the older coherent designs. No answer or image budget is
assumed. Exact conflict paths and hashes are in `source-conflicts.json` externally.

## Montreal reuse saves a rebuild

Exact model `montreal-plateau-duplex-clay-v004.glb`, SHA-256
`28fe10a3f8c5fc2e96b1e7c01382d6ec8ce546410a4976cd13c35b26c5cc4ab3`.
2,148,056 bytes; 37,314 triangles; 11 meshes/materials; no images/textures.
Complete envelope: **12.649098 × 19.320000 × 8.105000 m**, two storeys.
Do not use the older report's nominal 10.4 × 13.8 m wall dimensions for fit.

The independent reviewer inspected three sources, fourteen full-resolution
renders and four boards. New record: `montreal-review.json`, SHA-256
`722075ca8076a2c3bd75641e3db42b7db5549da96fe1676c0719e0efbb357aa7`.
Zero P0/P1. This grants clay model review only, not runtime acceptance.
`montreal-trial-package.json` is prepared externally, not applied or seeded.
Proposed initial plot: 16 × 23 m; single complete native assembly.

Preserve the curved front stair, side entry and their full projection. Connect
the upper home's stair foot at ground level; do not attach a floating path to
the upper-floor doorway. Multi-entrance route support remains a shared runtime
task, not a reason to tag a duplex as `native_home_plot`.

## Brick model construction

Replay scripts: `tools/catalogue_courtyard_pilot/`. Sources are the exact
`courtyard_family_housing/variant_2.png`, `_angle_60.jpg` and `_angle_90.jpg`.
The named variant depicts one buff-brick entrance building, not an entire
enclosed courtyard block. Red-brick neighbours and public landscape are context.
Three storeys, four segmental arches, outer balcony stacks, gabled roof, six
rooflights and two through-passages define the asset. Rear fenestration and
internal apartments/stairs are explicitly inferred.

Version 001 is preserved with a builder finding: wall joints read like siding.
Version 002 corrects brick cadence and balcony glazing, but delivery checks
found twelve degenerate triangles from Boolean export. Version 003 triangulates
and removes zero-area faces before export. Its independent review then found
one P1: exposed strips along the roof verges. Version 004 lowers wall/gable heads
to the roof underside and clips gable joints. The failed v003 review is preserved
as `courtyard-review.json`; it must never be used to approve v004.
Every version retains its own sources, script snapshot, GLB and renders.
Review images are rendered from reimported delivery bytes, not authoring geometry.

Final model: `courtyard-v004/courtyard-brick-modern-clay-v004.glb`, SHA-256
`6aedca74a28fd10deddda1659556968b86c9b32310b0697523559888b4ecd55a`.
4,422,584 bytes; 70,066 triangles; 11 meshes/materials; no images/textures.
Complete envelope: **25.582001 × 13.382000 × 12.275001 m**, three storeys.
Suggested initial plot: 30 × 17 m, fixed native size. Reserve both through-passages
and recessed entrances. Delivery verification and skill preflight pass; the
builder inspected all fourteen final renders and four boards. Browser acceptance
remains NOT TESTED.

Independent final review: `courtyard-v004-review.json`, SHA-256
`d80f69e3bb72c567a72f419dfedf888ef42dc5d9f62d2fe7a524d8be9fa14d5a`.
All fourteen renders, three sources and four boards inspected; zero P0/P1.
Canonical review validation passes. Only the architectural-clay profile is
approved; textured-keeper and runtime approval are not claimed. Sol should prepare
the courtyard trial package using these exact model/review bytes and source lock.

Source changes contain replay scripts and this handoff only. GLBs, Blender files,
render boards, rejected versions and review evidence remain in the external batch;
Python caches are ignored. No generated asset is staged or published.

## Sol trial sequence

1. Read `BUILDING_CATALOGUE_WORKFLOW.md` and `ARCHETYPE_RUNTIME_INTEGRATION.md`.
   Verify model and review hashes before preparing any trial. Hydrate only the
   exact source files needed, checking their package hashes; sparse checkout may
   omit them. Preserve existing protected projects and user edits.
2. Use `tools.catalogue_promotion trial <package>` dry run, then apply locally.
   Keep `local_trial_only`; ordinary publication validation should remain blocked.
   Seed only the named candidate into isolated QA database/storage, then read back.
3. Use a disposable copy of the **vacant Currie parcel**. Existing duplex fixture:
   `76903dbe-238f-432b-bfdc-e5f08e7c381b`. Do not edit the protected student rehearsal
   or accepted landscape projects. Existing isolated frontend/backend were
   `5175/8001`; verify service identity before use.
4. Find each model through ordinary search and its correct category; place at
   native scale, inspect all ground contacts and entrance/arch clearance. Test
   move, rotation, plot resize, Undo/Redo, reload and exact saved model identity.
5. Complete the shared multiple-entrance route integration where needed. A model
   pass does not establish automatic paths. Reserve separate front approaches,
   full stairs and passage exits; preserve landscape exclusion and route freshness.
6. Inspect low and aerial views, then save and inspect an actual free exact-3D
   export. Check readiness and faithful model counts/scale. No paid image test is
   required for this handoff. Record each exact-variant gate using the template.

Runtime findings that require geometric repair return to Astra as a finite list.
Do not alter passed model bytes or silently substitute another building in Sol's
test phase. Human activation remains separate from model and runtime passes.
