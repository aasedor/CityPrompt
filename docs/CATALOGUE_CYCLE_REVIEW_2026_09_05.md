# City Prompt catalogue pilot — review checkpoint

The approved catalogue plan is underway. Four distinct choices now work
together in a saved local empty-site project. The fifth choice, a new RLASM
6.1 duplex, has passed independent architectural-clay review and awaits human
activation. This is a first-cycle checkpoint, not completion of the 64-choice
catalogue or a production release.

## Try the local scene

Open [Catalogue acceptance — build a community](http://127.0.0.1:5174/projects/9535da89-4b5c-4839-aa7f-ccde56f1eded).
If that local browser is signed out, the isolated demo account is
`studio-smoke@example.com` / `Studio-local-2027!` (local fixture credentials).
The project was created through the student UI using the Fort Calgary search
result and an approximately 87 × 90 m boundary in the open field. The saved
scene contains two whole bungalows on one widened plot, two infill homes,
one adaptive park and one Calgary local street. It retains the Google ground
and surrounding context. This site is a local design fixture, not a proposal
to develop the real historic site.

| Choice | Current state |
| --- | --- |
| Modern infill home | Existing reviewed clay; native dimensions and whole-house plot repetition verified. |
| Craftsman bungalow | Existing reviewed clay; its own 15 × 24 m minimum plot, native roof/porch envelope and whole-house repetition verified. |
| Side-by-side duplex | New exact `infill_duplex` candidate v004; independent clay review passed. Not in the runtime catalogue. |
| Rustic neighbourhood park | v5 shared kit and adaptive layout tested locally; final visual acceptance remains separate from geometry checks. |
| Calgary local street | Existing draft Figure 2 section exposed as a 16 m placeable route; straight/bent editing and near-side park access verified. |

The coverage matrix records three object cards plus the separate street choice.
It preserves the original inventory hashes as historical baseline evidence.
Two geometric home choices are available in the detached collection; other
collections still need their second choice.

## Changes that mattered in the student trial

- Buildings retain their native form. At a 36 m plot width the planner places
  three infills or two bungalows, instead of stretching one oversized house.
  Invalid dimensions and overlap attempts explain why placement cannot fit.
- Shared ground now requests coverage for the whole site even from a
  pedestrian camera. A previously reproducible 102-missing-sample failure
  reached complete measured coverage after the fix. New sites start with
  Follow existing terrain; existing saved ground settings are preserved.
- The park has less repetitive trees and more coherent planting. Export checks
  caught floating rocks and grounded their actual meshes. Small parks retain
  metric equipment, omit items explicitly and keep a contained walking loop
  at the supported 40 × 30 m minimum case.
- The street keeps its 16 m section when bent or lengthened. Its near-side
  sidewalk connects to the park entrance without using the carriageway.
  The street's draft source label remains visible.
- An initial saved building disappeared from the client cache until another
  placement. Local FastAPI dependency cleanup could commit after the success
  response. Authored saves and the complete mixed-scene transaction now
  commit before reporting success. Delayed/failed-commit tests reproduced
  the defect and passed after the correction.
- At 390 × 844, the student can position the map and use Place at centre.
  Editing now hides the catalogue and uses a smaller scrolling bottom panel.
  Rotation, overlap rejection and saved reload were exercised. No physical
  touch-device claim is made.

## Images and geometry evidence

[Final local scene](C:/dev/CityPrompt-place/artifacts/catalogue-cycle/student-final-beautyImageBase64.png)
and [pedestrian sidewalk/park connection](C:/dev/CityPrompt-place/artifacts/catalogue-cycle/student-pedestrian-beautyImageBase64.png)
are direct renderer captures. No AI image polishing is applied.

The capture bundle includes the beauty image, proposal mask, semantic classes,
instance and material IDs, encoded depth, normals, camera and ground/access
snapshots. Final sampling records 1,122 points, two stable passes and zero
between-pass change; local residual is approximately 0.111 m. This measures
tile consistency, not survey accuracy. Relevant tile refinement temporarily
shows Aligning to ground and the capture waits for measured readiness.

The pedestrian capture includes partial occlusion, and the mask follows the
visible silhouettes. Instance IDs currently identify source zones/assemblies:
the two repeated bungalows share their plot's identity. These controls do not
prove that an image/video provider will preserve hidden objects. Paid media
fidelity and video continuity remain unverified in this cycle.

Review the duplex's [source comparison](C:/dev-artifacts/CityPrompt/catalogue-cycle-2026-09-05/duplex/v004/boards/phone-source-comparison.png)
and [construction evidence](C:/dev-artifacts/CityPrompt/catalogue-cycle-2026-09-05/duplex/v004/boards/phone-construction.png).
The 13-view independent review found no unresolved P0/P1 findings. Its exact
3.11 MB GLB has no embedded images/textures and measures 13.34 × 21.472 × 9 m.
It is one two-home assembly with two visible storeys; rear/interior arrangements
are inferred. A 17 × 25 m plot is proposed, not yet terrain-tested. The
[candidate record](C:/dev/CityPrompt-place/tools/catalogue_duplex_pilot/candidate.json) carries hashes,
programme, review and activation state.

## Verification and practical limits

Feature checks passed as the work progressed: ground coverage (26), detached
placement (17), street/section/access/undo (126), compact parks (33), transaction
and mixed-community persistence (60), and the final picker/mobile suite (26).
These suites overlap; their counts are not a unique-test total. Required
TypeScript and scoped ESLint checks passed after production frontend changes.
The park export verifier checked all nine actual GLBs and their contacts.

Short 1440 × 1000 warm development-browser samples measured:

| Observation | Mean frame interval | p95 | Used JS heap |
| --- | --- | --- | --- |
| Earlier smaller baseline | 17.74 ms | 18.10 ms | ~224 MB |
| Final scene, stationary | 17.53 ms | 18.10 ms | ~294 MB |
| Final scene, orbit gesture | 17.82 ms | 18.10 ms | ~326 MB |
| Temporary repeated-model rendering load | 17.80 ms | 18.20 ms | ~333 MB |

The rendering-only load added 30 shared-resource clone groups (40 extra homes),
with 22 group centres inside the camera view. All clones were removed afterwards;
none were saved. The scenes/cache conditions differ from the baseline, so these
numbers are not proof of a percentage performance improvement. GPU memory,
long-session growth, cold downloads and 60-student concurrency need separate
release testing. The nine-file park bundle is about 10% smaller than v2.

One first park click showed its preview without saving; the next click worked.
An earlier rapid rotate/duplicate error was not captured well enough to prove
its cause. Later traced saves and reloads passed, including after the commit
correction. Keep these interaction cases in the next acceptance run. Development
HMR can leave stale map listeners; verification after source edits uses a full
reload. This is not claimed fixed by the production save correction.

## Exact next step

Obtain visual activation of duplex v004, then wire its exact variant into the
two-home collection without moving the parent's detached variants. Place one
fixed native assembly, verify terrain/contact and the complete five-choice
student flow, and repeat rapid edits and direct captures. Only after that
representative passes should the next bounded four-building batch start.
The applicable [RLASM runtime contract](C:/dev/CityPrompt-place/docs/RLASM_LATEST_METHOD.md)
requires that “a human explicitly activates the architectural-clay runtime tier.”

## Source, output and spending

Source work is committed locally in `C:/dev/CityPrompt-place`; the current
`codex/catalogue-cycle-review` branch includes the preceding named initiatives.
Nothing was pushed or deployed. The original OneDrive checkout and historical
experiments were preserved. Generated model/evidence output is external under
`C:/dev-artifacts/CityPrompt/catalogue-cycle-2026-09-05/`; browser evidence is
ignored under `artifacts/catalogue-cycle/`. Heavy assets were not added as Git
blobs.

The active prepared public root is `runtime-v4/public` under that external
directory. `tools/catalogue_runtime/serve.ps1` validates it before serving the
frontend. Common reference assets still use explicit read-only junctions to the
hydrated source checkout; this is not a standalone fresh-machine bootstrap.
The isolated local backend is on port 8002. No paid image/video generation was
used in this cycle. Reconcile prior spending before using the existing $10
total media-test allowance.
