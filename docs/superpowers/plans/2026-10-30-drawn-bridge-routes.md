# Drawn Bridge Routes Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development for independent extraction and compiler tasks, with integration in this worktree. Track results in the external task ledger; preserve existing changes.

**Goal:** A bridge-only timber pilot whose span follows two drawn endpoints,
then bounded conversion of other bridge styles after its acceptance.

**Architecture:** Reuse native street profiles and verified modules. The pilot
has fixed end/stair modules and repeatable middle bays, an exact recipe and a
new variant ID. Old fixed placements retain their identity and behavior.

**Tech Stack:** TypeScript/React/Three, Python/trimesh, existing FastAPI compiler.

**Spec:** ../specs/2026-10-30-drawn-bridge-routes-design.md

## Global constraints

* Prepared level site; straight two-point pilot; stairs, no accessibility claim.
* Original source GLBs, saved fixed IDs and publication gates unchanged.
* Native width/height/end structures retained; no surrounding scene geometry.
* No new dependencies, paid calls, network/security changes or live deployment.
* Preserve nine pre-existing hydrated LFS files; stage only exact deliverables.
* Keep original performance budgets and test assertions; no blanket full suites.

## Review focus

* Very short/long spans must remain recoverable drafts, never crash the page.
* Arbitrary orientation and reversal must put the same stair ends at grade.
* Bay seams must have continuous deck, guards and roof without broad ground.
* Save/reload/Undo and delayed loads must preserve exact recipe and revision.
* Frontend/server must reject unknown IDs, widths, hashes and unsupported bends.

## Tasks

### 1. Bridge-only native modules

Files: tools/drawn_bridge_routes/build_timber.py and tests; generated pilot
modules under frontend/public/street-kits/pilots/timber_covered_bridge_route_v1/.
Output: standard nativeStreetPilots row with program.adapter modular-bridge-v1,
module bridge_left_stair/bridge_left_end/bridge_bay/bridge_right_end/bridge_right_stair,
program.bridge with approachM/endM/bayM/deckHeightM/clearWidthM and bounds.

- [x] Test exact source hash, explicit extraction, no water/banks/remote paving,
  fixed module contact/width/height and deterministic byte/provenance output.
- [x] Observe RED, extract a dry-run only and inspect measured module bounds.
- [x] Produce the five modules in local X-across/Y-along/Z-up convention via
  glTF Y-up. Extend retained pier/abutment feet to grade, without context slabs.
- [x] Inspect native-size reconstruction and three alternate lengths, from
  aerial, street/deck and underside views. Record all gaps honestly.

### 2. Executable route/recipe pilot

Files: nativeStreetPilot.ts, nativeStreetProgram.ts, nativeStreetInstances.ts,
specialistStreetProgram.ts, authoredCameraGround.ts, streetFamilyCatalog.ts;
matching backend native specialist/candidate contract and mirrored registries.
Interfaces: modularBridgeRouteProblem(program, route), modularBridgePoses(pilot,
route), modularBridgeWalkingHeight(program, lateral, station, length). Poses
may carry an explicit longitudinal scale for middle bays only.

- [x] RED tests: 45/80/150m routes repeat bays with exact endpoints; reverse and
  oblique routes preserve frame/height; too short/long/bent/NaN rejected.
- [x] Implement one shared route policy and native instancing; no grass plane
  or flat at-grade street generated across the elevated span.
- [x] Mirror identity, width, length, straight-route and module locks server-side;
  compile/readback exact saved recipe and reject tampering. Preserve old saves.
- [x] Test stair/deck walking and native readiness/mount inventory at bay seams.

### 3. Discovery and ordinary UI acceptance

Files: assetRegistry/canonicalCatalogue pilot supplement and tests, runtime review.

- [x] RED: new bridge card offers Choose & draw route and dispatches exact new
  ID; old fixed saved objects and production discovery gates unchanged.
- [x] Ordinary disposable browser project: draw short/long/oblique bridge,
  endpoint edit, Undo/Redo, save/reload, walk, free exact capture. No user project
  geometry mutation, paid call or security permission.
- [x] Narrow FE/BE tests, type-check, scoped lint, original build budgets,
  independent review, diff/status check and coherent exact-file commits.
- [x] Upload screenshots/source evidence and note privately to approved Drive;
  verify metadata, ledger IDs/hashes. Keep fixed vs route versions explicit.

### 4. Bounded next styles

- [ ] After the pilot's classroom blockers pass, define each remaining exact
  source's route axis, structural repeat/deform contract and context exclusion.
- [ ] Convert/review linear bridge styles in bounded batches using the shared
  route mechanism. Do not silently stretch a ring/flyover into a straight span.
- [ ] Keep failed/unrun styles visible in the final report; no invented passes.

## Pilot checkpoint

Timber ordinary browser preview/place/edit/Undo/Redo/reload/walk/exact-download evidence and explicit unrun limits are recorded in docs/showcase/TIMBER_DRAWN_BRIDGE_RUNTIME_REVIEW_2026-10-30.md. Remaining styles below this checkpoint are not converted or approved by this result.
