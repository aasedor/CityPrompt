# Twenty more neighbourhood buildings

The user authorized twenty additional normal everyday buildings on 2026-10-03,
to be built while they are away. This continues the local school/fourplex
prototype work. Do the work autonomously within this finite scope; do not ask
again for routine design/build/review steps or publish anything.

## Resume locations

- Worktree: `C:/Users/andre/.codex/worktrees/neighborhood-refinement/CityPrompt`
- Branch: `codex/neighborhood-refinement`
- Base source checkpoint: `3ea075106ce4f6595b5f82fe4f7bb1e1988954bb`
- Live progress: `C:/dev-artifacts/CityPrompt/neighborhood-expansion-20-2026-10-03/progress.json`
- Source batch manifest: `tools/neighborhood_expansion/batch-20.json`
- Prior reusable helpers and browser/check scripts: `tools/neighborhood_refinement/`
- Prior reviewed models: `C:/dev-artifacts/CityPrompt/neighborhood-refinement-2026-10-03`
- Preserve the prior preview on port 5201 and the unrelated process on5202;
  use port5203 for this batch (5202 was already occupied).

The main checkout and original neighborhood-essentials worktree contain unrelated
pending user work. Do not edit, stage, clean or reset them. All heavyweight output
goes under the new external batch root. New source images belong in that root's
`reference-repo/frontend/public/archetypes/buildings/<family-slug>/` tree. Record
the exact root and authority in each manifest; never use legacy image folders.

## Fixed scope

Exactly 20 variants are enrolled: three schools, three childcare centres, three
fourplexes, four sixplexes, three branch libraries and four community halls.
Their original briefs are copied into the batch manifest. Exclude the already
built school/fourplex and the childcare/library beneath housing variants.
`childcare_garden_pavilion` is the representative pilot. After it passes the
local independent architecture/walking review, advance in finite groups of four
(the final group may be smaller), with a checkpoint after every candidate.

The user's request authorizes this bounded expansion following the prior visible
pilots. Human catalogue/publication approval is still absent. No external paid
image API is authorized; use the built-in image generator for required original
designs and source-conditioned derivatives. Use one call per asset, preserve
prompts, inputs, output paths and hashes. Do not replace a failed built-in call
with a paid CLI/API. Existing exact compatible source pixels can be reused.

## Execution

1. Read repo instructions, the RLASM skill and canonical v6.1 method/policy/memory.
   Check git status and progress; resume an existing render/job before starting
   anything new. Never run duplicate work against one candidate.
2. Establish each variant's own front, compatible oblique and roof/top references.
   Inspect them, record inferred rear/program decisions, and lock exact hashes.
   The 20 briefs are design intent, not pixel proof. Do not model before locking
   a coherent source set. Preserve rejected source attempts separately.
3. Write the dimensions, plan/roof graph, wall/opening schedule, room programme,
   circulation, landscaping, material authority and complete camera roster.
   Reuse low-level geometry helpers, not a universal recoloured building shell.
4. Build a complete editable scene and exact GLB with native walking metadata.
   Furnish program-specific rooms. Fourplex/sixplex dwelling counts stay exact;
   provide kitchens, bathrooms, beds and connected stairs. Civic buildings need
   their actual reading/play/meeting/classroom uses and relevant outside spaces.
5. Exercise the app's actual walking solver plus real-GLB physical path checks.
   Test entry, every occupied floor, meaningful room routes and furniture
   exclusions. Add threshold/body-clearance checks before final rendering.
6. Render every mandatory view from the exported/reimported GLB, with source and
   phone boards. Inspect the full set. Fix nonarchitectural QA-light reflections
   early instead of repeating the old blown-white pane artefacts.
7. Use a separate independent RLASM verifier, as explicitly required by the skill.
   Builders cannot self-approve. Review every required view and source. A local
   architecture/circulation pass and full textured-keeper assessment are separate.
   Keep every real limitation visible; never relabel a scoped pass as a keeper.
8. At most three repair versions per candidate in one pass. If still failing,
   preserve the blockers and move to another queued item instead of looping.
   Revisit held items only with a concrete new correction and finite next pass.
9. Verify passing candidates in the isolated browser inspector, including model
   load/switch, actual embedded walking, interior/exterior views, reload and
   visibility toggle. Save browser screenshots and readable evidence.
10. Save candidate lifecycle, exact hashes and progress after every material step.
    Keep `progress.json` and the source manifest synchronized at checkpoints.
    Commit only coherent verified source/manifests after diff checks. Never push
    or modify the seed/runtime catalogue or the user's live saved project.

## Lessons from the completed pair

- Reserve stair voids, landings, headroom and treads in geometry and navigation.
  A broad hidden navigation floor can trap upper flights or conceal physical gaps.
- A route solver pass is insufficient: raycast actual exported floors/ceilings.
- Check partitions against windows, counters, open door leaves and beds.
- Rooms must accommodate the app's 0.22 m movement clearance. The bathroom pilot
  needed a 0.95 m doorway and an offset path around its shower tray.
- Use cameras that prove complete fixtures and threshold edges. Browser review
  cameras must respect authored lens settings; generic FOVs can hide evidence.
- The old pair passed local architecture/walking review but still had two P1
  keeper limitations each. New work should improve those limitations; they are
  not permission to conceal finish defects or make keeper claims.

## Completion and follow-up

Count a model complete only after the agreed local architecture/circulation gates,
browser checks, reproducibility records and independent review pass. References,
render attempts, recolours and failed models do not count toward twenty. Full
keeper blockers remain separately recorded. Keep the previous pair intact.

The heartbeat continues this finite work from saved progress. Stay quiet for an
unchanged running job; notify the user on a meaningful batch checkpoint, completion,
failure needing intervention or required user action. Once all twenty have passed,
write a final contact sheet, interactive local catalogue and human/machine delivery
manifest, report the result, and pause this task's heartbeat. Do not archive the
chat automatically. If tools or a required approval block progress, record the
exact blocker and notify the user without claiming completion.

## Pilot commands and current tooling

Run from the worktree above. `build_childcare.py` is a dedicated constructor for
the garden pavilion; it does not build the other nineteen designs. Each needs
its own locked source set and authored composition. The original brief alone
does not authorize using this envelope for another family.

```powershell
$batchRoot = 'C:/dev-artifacts/CityPrompt/neighborhood-expansion-20-2026-10-03'
$blenderExe = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
# Choose a new unused version; never overwrite an existing candidate.
& $blenderExe --background --python tools/neighborhood_expansion/build_childcare.py -- --output-root $batchRoot --version vNNN --dry-run
& $blenderExe --background --python tools/neighborhood_expansion/build_childcare.py -- --output-root $batchRoot --version vNNN --resolution 1280
$candidate = "$batchRoot/childcare-garden-vNNN"
node tools/neighborhood_refinement/check-walking.mjs $candidate
node tools/neighborhood_expansion/check-garden.mjs $candidate
& $blenderExe --background --python tools/neighborhood_refinement/check-physical-walk.py -- $candidate
python tools/neighborhood_expansion/boards.py $candidate
python C:/Users/andre/.codex/skills/rlasm-expert/scripts/validate_candidate.py $candidate
# Start once; use --refresh to update the model list while it already runs.
node tools/neighborhood_expansion/preview.mjs $batchRoot 5203
node tools/neighborhood_expansion/preview.mjs $batchRoot 5203 --refresh
```

The source builder snapshots its own code, low-level dependencies, source pixels
and masonry tile into each external candidate. It renders the reimported GLB.
The tile's observed cadence was calibrated to1.25×2.2m; the requested2.4m square
was not produced by the image generator. Remaining palette finishes require a
separate full keeper material pass. Route checks cover authored paths and cannot
certify unrestricted collision or building-code compliance.

## Corner-entry fourplex tooling

`build_corner_fourplex.py` authors the separate corner-entry design; its three
source locks and inferred dimensions live in `corner-prework.json`. It uses
`delivery.py` only for source validation, export, script snapshots and exact-GLB
rendering. The shared delivery module does not compose building geometry.
Run it with the same `--output-root`, `--version` and `--resolution` arguments
as the childcare builder. Its masonry cadence is1.92x2.0m, distinct from the
childcare tile. The generalized boards tool selects the locked front source and
an existing interior camera. The expansion viewer excludes the earlier
central-entry fourplex's one-off shower camera.

The finite corner repair pass ends at `fourplex-corner-v004`. Its33 views prove
four furnished homes, two separate stairs, intersecting roofs, shower fixtures
and a clear rear bicycle bay. The20 authored routes include both stairs in each
direction and access to the rear bench/bikes. Run `check-garden.mjs` after the
native walking check; three rear props have explicit collision probes.
Do not begin another repair version in this pass. Consult its independent
review and delivery manifest for the final scoped decision.

Carry these concrete corrections into later constructors:

- Guard the upper slab lip above a lower flight as well as both inner stair
  edges. Cross the half landing beyond the guard ends and include guards in
  navigation obstacles. Match navigation triangles to actual tread/slab edges.
- Do not place an opaque bathroom liner behind an exterior window. Show complete
  fixtures with dedicated cameras, and avoid open door leaves obscuring beds.
- Reserve the bicycle parking footprint before placing shrubs. Include hardware
  helpers explicitly in obstacles when their default module is not a site prop.

## Brick sixplex tooling

`build_brick_sixplex.py` authors a three-storey brick walk-up with exactly six
furnished flats and one stacked shared stair. Its revised wide front, compatible
oblique and roof study are locked in `sixplex-prework.json`; generation records
are in the external `sixplex-locked-generation.json`. The original narrow front
in `source-attempts/sixplex_brick_walk_up/front-001.png` remains preserved with
its original provenance. The roof study governs topology, not metric dimensions.

Use the same builder arguments as the other constructors. The sixplex reuses
atomic wall, door, bed and bathroom helpers from `build_corner_fourplex.py`;
`delivery.py` snapshots that dependency through its optional `extra_scripts`.
The envelope, flat roof, facade composition, plan and circulation are sixplex
specific. Its source-conditioned brick tile maps to2.16x2.08m.

V001 has40 completed views but fails six apartment entry paths beside protruding
books. V002 offsets those aisles by0.20m and adds two clear kitchen sink/contact
views, making42 required views. Those views exposed cabinet timber filling the
sink recesses. V003 cuts the cabinet around each bowl. Preserve both failed
versions. The gate requires all25 routes,20 furniture probes,4 garden probes,
physical checks, browser and independent review. Read live progress for the
final decision; machine checks alone cannot approve a candidate.

Carry the middle-floor stair distinction forward: a stacked continuing flight
needs an open upward mouth; the guard across the lower-flight lip belongs only
on the top floor. Disable camera, glossy and transmission visibility on QA lights
as well as their specular/transmission factors. This removes the oversized light
ovals established in earlier prototypes; material finish remains a separate gate.
For sinks, cut the supporting cabinet as well as the worktop and bowl. A real
bowl can otherwise be filled by solid timber even when the countertop hole looks
correct from a distance. Require a close kitchen view before accepting it.

The following library has source attempts saved under
`source-attempts/library_neighborhood_pavilion/`, with separate `library-*.json`
generation records. Proposed sources are widened `front-002.png`, corrected
`oblique-002.png` and `top-001.png`. The original oblique has a rejected rear roof
notch. Reconcile the front's distant rear roof against the corrected oblique,
then finish the independent compatibility check, material tile and detailed
prework before geometry. The overhead study governs topology only. The library
is unbuilt and not counted as complete.
