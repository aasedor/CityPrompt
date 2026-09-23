# Summer market plaza — offline model pilot

User request: build new parks/open spaces and streets before the combined Sol
runtime session. This is one open-space pilot, not a catalogue-wide generation.
Worktree: `C:/dev/CityPrompt-market-plaza-model`, branch `codex/market-plaza-model`.
The existing building worktree and protected student projects remain untouched.

## Delivered concept

`student_summer_market_plaza_v1` is an original 32 × 28 m summer market design:
six inward-facing timber stalls, four benches, four prairie planters and four
lights around a clear 12 × 14 m event square. Separate origin-centred GLBs carry
the furniture. `recipe.json` records their placements and rotations in metres.
Front/back entrances have a 4 m corridor; the lateral entrances at y=3.5 have
a 3 m corridor. All furniture feet have a zero native datum.

The model intentionally does not claim exact identity with an existing card.
Direct inspection found that `calgary_prairie_plaza_v1` / “Summer Market Square”
shows an office building and garden, while `market_square_v0` shows an
amphitheatre. Neither source was used to invent a false reconstruction approval.
Existing IDs, references and saved projects were not changed. Use a new card
with the actual model preview if this concept is later approved for trial.

## Evidence and checks

External package:
`C:/dev-artifacts/CityPrompt/public-realm-pilots-2026-09-22/market-v001/`.

Assembly preview SHA-256:
`206d8b89724b18f49f4adfb4fc3491e61e7111905ab1c8233a9708950db8146b`.
227,328 bytes; 2,584 triangles, excluding future shared runtime trees.
Individual asset hashes and geometry checks are in the package. Four renders
were made from the reimported GLB and individually inspected: aerial, top,
entrance and market close-up. Builder visual check passes for this concept;
independent visual review has not been performed.

Blender verification passes finite geometry, full furniture containment,
non-overlap, module ground datum, programme counts, clear event area and both
crossing corridors. The paving-joint preview extends 7.5 mm beyond its nominal
edge; runtime paving must be clipped to the actual plot. No engineering,
accessibility, field performance or classroom acceptance is claimed.

## Sol integration work before browser tests

1. Read `ARCHETYPE_RUNTIME_INTEGRATION.md` and the package's copied review
   template. Keep all untested runtime gates open.
2. Add an isolated local trial adapter with a new exact ID. Load the separate
   furniture modules, preserving native scale and declared placement rotations.
3. Generate paving through the shared park surface and current measured terrain.
   **Never place `assembly-preview.glb` as a rigid park slab** or stretch the
   market fixture over an arbitrary polygon. Begin with the fixed 32 × 28 m
   rectangle; unsupported small/irregular plots require an explicit fit result.
4. Seat rigid furniture through shared support measurements. Use shared park
   access resolution for the four entrances and landscape exclusion for the
   complete occupied plot and approach corridors. No baked tree asset is added;
   future trees must use the shared stand and clear the routes and stall roofs.
5. On a disposable vacant Currie layout, test ordinary placement, connections,
   move/rotation, Undo/Redo, reload, readiness and actual exact export. Browser,
   natural terrain, failure recovery and publication remain NOT TESTED.

Replay with Blender 5.2: run `tools/market_plaza_model/build.py` with
`-- --output <fresh-external-directory> --dry-run`, then without `--dry-run`.
Run `tools/market_plaza_model/verify.py -- <candidate-directory>` afterwards.
Use Blender's `--python-exit-code 1`. No paid generation is involved.
GLBs, renders and verification output stay external; source and this handoff only
are committed. This model-stage work retains the user's deferred browser checks.
