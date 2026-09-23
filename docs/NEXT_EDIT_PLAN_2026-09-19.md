# Next edits: grounding and editing reliability

Planning only. No production changes are authorized by this document beyond
the user's task instructions. Implement in small checkpoints; do not treat
passing automated checks as browser or release acceptance.

## Starting point

- Main checkpoint: `7378ce2a7` (student transformation, all 22 render styles).
- Local follow-up: `4792bd950`, automatic park-ground race protection; 108
  focused tests, TypeScript and lint passed. Browser validation remains pending.
- Worktree: `C:/dev/CityPrompt-grounding-edit-race`. Other checkouts have unrelated
  uncommitted edits, including grounding changes; preserve them and inventory
  overlap before implementation. Recheck main and branch status before starting.
- Keep existing scene, catalogue, RLASM, grounding and undo ownership. No new
  parallel scene system, destructive migration or dependency is planned.

## Batch A: correct contact with ground

### 1. Building footprints at site boundaries

Investigate `buildingGroundContact.ts` and its existing geometry tests first.
The early outside-site decision currently checks footprint vertices and the
object origin. Add cases where edges cross a narrow or concave site even though
those points are outside, and where a footprint surrounds the measured site.
These are coverage gaps to reproduce, not yet confirmed runtime failures.

If reproduced, use the existing geographic boundary and geometry utilities to
distinguish fully outside, partially supported and fully supported footprints.
Reject unresolved contact explicitly; do not hide it with a guessed elevation.
Retain native geometry, separate detached pads, the current foundation limit and
truthful recovery messages. Do not enlarge or flatten the site to make a test pass.

Acceptance: narrow/concave crossings, rotation, detached modules, incomplete
samples and wholly outside footprints classify correctly; existing flat/slope
contact tests pass. Browser handoff: inspect a normal building and a building
straddling a site edge from above and at pedestrian height.

### 2. Terrain refinement and reload consistency

Audit `SharedSiteGroundProvider.tsx`, `sharedSiteGround.ts`, the contact consumers,
`parkTerrain.ts`, and capture readiness. Trace one measured revision from tile
events through displayed contact and capture. Use deterministic provider-event
tests to reproduce any mismatch before changing production behavior.

Check relevant versus off-site tile events, late callbacks, temporary failures,
recovery, boundary edits, and reload of existing saved terrain. Preserve any
intentional distinction between retaining a safe visible surface and requiring
a newly validated surface for capture. Do not invalidate saved park terrain
merely because a label changed or a row received unrelated metadata.

Acceptance: old results cannot become current geometry; capture cannot claim
fresh grounding from an invalid revision; unrelated tile churn does not make the
proposal disappear. No invented vertical offset, weakened validation threshold,
provider switch that rewrites proposal coordinates, or automatic paid retry.

**Batch A browser gate:** another model verifies the park-race handoff plus flat,
slope, boundary-edge, refinement and reload cases on disposable fixtures. Capture
and inspect screenshots; record coordinates, revisions, console and network
results. Keep the frozen Gold Standard unchanged. Findings return as a bounded
fix list. Do not call grounding accepted before this gate passes.

## Batch B: predictable edits and recoverable saves

### 3. Building property edits and generated-model freshness

Trace `BuildingDesignControls.tsx`, its mounting/key behavior, `useAutomatic3D.ts`,
and the existing compiler/source-revision contract. Verify rapid type, variant,
storey and height changes; switching selection; undo while generation is pending;
and a late result after a newer edit. Inspect backend code only if the source
tests identify an actual contract gap.

Fix only reproduced cases. Essential controls must show the selected object's
current properties while preserving legitimate unsaved drafts. A requested
unsupported size must retain its authored dimensions using planned massing;
it must not stretch a reviewed RLASM model or silently restore an older model.

Acceptance: latest authored edit wins, one edit has one undo step, footprint and
orientation survive type/height edits, and fallback/recovery remains truthful.
Use the existing RLASM skill and repository method documents if implementation
touches representation or compiler rules; do not weaken review gates.

### 4. Undo, failed saves and older-project fixtures

Extend existing `useSiteZones`, `undoRevision`, and project-scope tests around the
actual defects found above. Use small representative fixtures for detailed and
massing buildings, terrain-following parks, and older boundary-free projects.
Cover move/rotate/type/height edits, derived writes, conflicts, deletion and
navigation away with a request in flight. Include backend tests if an endpoint
changes. Avoid duplicating existing passing tests or building a new test framework.

Acceptance: failed writes preserve recoverable work; undo/redo targets the correct
project and revision; reopening retains coordinates, identity, dimensions and
valid ground data. No duplicate objects or silent conversion of an old project.

**Batch B browser gate:** another model runs place -> edit -> undo -> redo -> save
-> reload on a new project and representative older projects. Check keyboard
property controls and desktop/laptop layouts while exercising the same workflow.
Feed failures back before merging dependent changes.

## Working and verification contract

1. Inspect current source and overlapping local work; write the smallest failing
   regression for a concrete defect. If a proposed risk does not reproduce,
   record the evidence and avoid speculative production changes.
2. Implement one coherent fix. Run focused Vitest, TypeScript and relevant lint;
   run narrow pytest/compiler checks only when those systems change.
3. Review diff/check/status, checkpoint locally, and update the short testing
   handoff. Label it **implemented, awaiting browser validation**.
4. Browser work runs under the user's chosen other model. Supply exact branch,
   setup, fixtures, expected outcomes and failure evidence requirements. Do not
   start browser automation or switch models as part of the coding stage.
5. Merge or publish only within current user authorization and after applicable
   validation. Refresh the runtime manifest only if reachable source inputs or
   assets actually change. Do not include unrelated files or generated evidence.

Batch A is the next coding target. Batch B may begin with independent source
investigation while browser validation is pending, but should not accumulate
dependent changes over an unresolved grounding regression.

## Deferred scope and cost

Keep all 22 render styles. Defer image polish, new video modes, environment
expansion, LiDAR and Gaussian splats until this reliability batch is accepted.
This plan requires no paid generation and no new dependencies. Account credit
renewal does not renew the separate US $10 mission API validation allowance.
Broad performance claims and the final student journey remain later gates.
