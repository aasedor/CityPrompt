# Catalogue next steps: first implementation cycle

September 5, 2026. The user accepted the 64-choice catalogue direction. This document makes the first work cycle concrete; it does not record implementation or asset approval.

## First milestone

Deliver a local, reviewable empty-lot neighbourhood with **five selectable choices**:

| Choice | Exact existing catalogue identity | Work required |
| --- | --- | --- |
| Modern infill home | `calgary_modern_infill_house / infill_flat_roof_minimal` | Reuse the reviewed clay delivery and existing placement pilot; verify the portable setup. |
| Craftsman bungalow | `vancouver_craftsman_bungalow / craftsman_classic` | Reuse the reviewed clay delivery; integrate its own dimensions, preview and plot rules. |
| Side-by-side duplex | `calgary_modern_infill_house / infill_duplex` | Audit and lock sources, build one RLASM 6.1 clay pilot, independently review it, then verify local placement. |
| Rustic neighbourhood park | `neighborhood_park / neighborhood_park_v0` | Refine the existing adaptive pilot and close its visual and ground-contact findings. |
| Calgary local street | `calgary_local / calgary_local_v0` | Reuse the authored 16 m draft section; expose and verify route placement, sidewalks and park access. |

The scene can contain several instances of those choices. This milestone completes the two-choice detached-home collection and proves the production path for the other domains. It does not claim the duplex, park or street collections are complete yet.

Use the existing Fort Calgary open-field pilot near 51.04542, -114.04677 as the starting fixture, after checking its current tile context. Place everything through the student UI. Keep the site boundary visible, preserve surrounding Google context, and enlarge or select another empty site if the actual model envelopes do not fit. Do not reduce model scale to squeeze the fixture into a predetermined screenshot.

## Ordered work packages

| Order / ID | Work | Concrete deliverable | Exit check |
| --- | --- | --- | --- |
| 1 — CAT-01 | Verify the reusable assets and local environment | Exact-file inventory, source/model/review hashes, baseline screenshots and recorded startup instructions | The two existing homes and park pilot resolve in the intended checkout; missing files and unsupported states are explicit. |
| 2 — CAT-02 | Make asset availability reproducible and measure the baseline | Small versioned runtime manifest and intentional asset-serving configuration; timing/memory record | A fresh local launch loads only needed assets, preserves exact variants and reopens a saved project without the accidental dependency on another worktree's overlay. |
| 3 — CAT-03 | Stabilize ground contact | Bounded shared-ground fix with regression evidence | Cold opening, close-up camera entry, orbit/LOD changes and reopening keep valid contact or show a clear pending state; stale or missing terrain is never replaced with guessed elevations. |
| 4 — CAT-04 | Complete the detached-home pair | Modern-home and bungalow cards with correct previews, dimensions and supported controls | Both place, rotate, duplicate, save and reload. Large plots repeat whole houses only where verified; small plots explain why the selected building does not fit. |
| 5 — CAT-05 | Build one new duplex through the complete process | Immutable RLASM 6.1 source lock, model, complete evidence and independent review | Exact source identity survives GLB export/reimport and native placement. The duplex has its own identity and programme; the detached parent is not relabelled wholesale. |
| 6 — CAT-06 | Finish one park | Revised shared-kit components and the existing rustic layout recipe; source/Google comparison board | Better trees, planted beds and material edges; metric amenities, contained paths and explicit omissions across supported sizes. |
| 7 — CAT-07 | Complete one sourced street and its connections | Placeable local-street recipe using the existing section bands, plus street-to-park connection evidence | Route length and shape change without distorting the source cross-section; sidewalks meet park paths without crossing buildings or unmarked carriageways. |
| 8 — CAT-08 | Run the novice student trial and package the result | Saved local project, before/after captures, issue/fix log, performance comparison and review board | All five choices work together through the full student flow; significant defects are fixed and rechecked before the next batch. |

This is the integration order. Read-only source audits and isolated geometry preparation can proceed while unrelated runtime work is underway, but completed assets do not bypass the shared-ground or student-trial gates. Keep implementation for runtime, buildings, parks and streets on separate named branches and checkpoint coherent units.

## Details that matter in the first cycle

**CAT-01/02: verify rather than regenerate.** Read the existing clay manifest and actual binary files from the original checkout without changing its dirty work. Confirm exact candidate and review hashes, native full bounds, floors and dependencies. Retain previously authorized activation only for those exact existing deliveries. Record the public-asset overlay and backend harness currently used by the pilot, then replace that incidental dependency with deliberate packaging. Store readiness separately from a reference image's existence. Keep previous project IDs and saved asset references compatible.

Measure catalogue opening, first selected-asset load, cached preview, orbit frame time, memory and save/rebuild before changes. Record hardware/browser, cold versus warm state and fixture contents. The roadmap's performance targets remain provisional until this baseline exists. This cycle should also test a repeated-home scene for scaling costs; it does not require generating additional building families to create a load test.

**CAT-03: ground is shared evidence.** Reproduce the documented cold pedestrian-camera failure before changing the provider. Test whether a previously validated snapshot can remain usable across camera changes, deliberately obtain missing coverage, and invalidate it when site geometry or relevant tile evidence changes. Inspect building bases, sidewalk edges, park paths and rigid equipment pads at pedestrian scale. A warmed aerial screenshot alone cannot close this work package.

**CAT-04/05: each building owns its supported shape.** The current infill pilot's 12 × 16 m default is not a universal house preset. Derive the bungalow's plot minimum and frontage from its actual complete model envelope and placement clearances. Preserve native proportions. Duplex placement begins as one fixed native assembly; do not automatically apply a detached-home repetition rule. Use an exact-variant browsing override for `infill_duplex`, retaining the parent's detached variants in the correct collection. Floors and building dimensions remain governed by authored geometry and supported controls, not render-prompt text.

For the new duplex, inspect compatible front, oblique and top sources before construction. If those references conflict, repair the source package or nominate a replacement within the duplex slot before building. Follow the canonical clay method, export/reimport the delivered GLB, supply the full evidence set and obtain the required separate review. Source quality, runtime integration and user activation remain separate states.

**CAT-06: close known park findings.** Improve repetitive crowns/branch silhouettes, coherent meadow/shrub beds, gravel/activity edges and appearance under the target renderer's lighting. Start with the already-tested 40 × 35 m, 70 × 55 m, 105 × 75 m, rotated-L and 8 × 80 m cases. They are regression fixtures, not universal size promises. Inspect the complete park at supported sizes; preserve the explicit too-narrow result and recorded amenity omissions. Furniture and play equipment retain real metre dimensions. Keep layouts deterministic through reopening, and measure shared-kit loading once rather than copying assets for each size.

**CAT-07: make the existing street definition visible in 3D.** Reuse the section's documented bands and source figure, retaining its draft label. The existing narrow-residential road pilot is not evidence that this exact Calgary section is already verified. Support route picking and editing, shared ground, a straight segment and a bent/joined case. Connect the near-side sidewalk to the park entrance, keeping planted areas clear. Unsupported junction configurations remain explicit until the later intersection work is ready.

## Student trial script

Run once from a clean local account/project and once after a saved reload. Use the real browser UI and keep a short record of confusion, not only technical pass/fail results.

1. Open the catalogue and find the two detached homes without knowing their internal IDs.
2. Place one of each on the empty site; place the duplex and confirm the correct building appears.
3. Move and rotate a home. Widen a supported detached plot and inspect whole-house repetition. Attempt a too-small plot and a boundary/overlap violation; feedback must explain the constraint without corrupting the saved plan.
4. Place the park, resize it through supported sizes and inspect the amenity count. A smaller plot must not stretch equipment or silently become another park type.
5. Pick the Calgary local street, place/edit its route and inspect the sidewalk-to-park connection at ground level. Moving the park or street should recompute the connection coherently.
6. Undo and redo changes, save, reload and return to the same camera. Confirm exact variants, dimensions, orientation and layout survive.
7. Orbit from aerial to pedestrian views and enter the site cold at close range. Check the object bases and surrounding tile context.
8. Produce a direct presentation capture with the saved camera, masks, depth and instance controls. Include a partially occluded building or amenity and an object near the site boundary.
9. If a paid image-polishing test fits the verified remaining allowance, compare it against the direct capture for moved, swapped, added or wrongly revealed objects. Otherwise record the test as pending; do not substitute an unrelated image-generation demo as proof.
10. Repeat the main interactions in a narrow viewport and compare timings/memory to the baseline. Record any manual workarounds a novice would not know.

For the eventual image render, students may customize atmosphere and surface appearance. Changes to building height, footprint or position belong in the saved model controls. A geometry-faithful image test does not automatically validate video continuity.

## Verification and review package

During implementation, run the narrow relevant tests, then TypeScript checking for production TS changes. Known starting points include the pick/place geometry and automatic-build suites, shared-ground provider/geometry/capture suites, neighbourhood-park layout/geometry suites, and street section/ground/visual-contract suites. Run backend and compiler tests where those paths change. Follow structural checks with the browser trial and actual asset review; no screenshots or performance results are claimed by this plan.

The first review package should contain the saved local project, a five-choice inventory with exact versions, source-versus-3D comparisons, overhead/aerial/pedestrian captures, small/large park cases, invalid-size examples, ground/connection evidence, test results, measured timings and a short remaining-issues list. Update the existing coverage matrix with real evidence and states as work proceeds. Mark the detached collection complete only when both choices pass release checks.

The canonical RLASM clay contract requires a separate review and human activation for new deliveries. Prepare the concrete model and evidence first; this is a final activation checkpoint, not permission needed to start authoring, fixing or testing locally. Existing authorization for named reviewed deliveries persists. The first-cycle scope does not authorize a production deployment or an open-ended paid generation run.

## Immediately following this milestone

Once the duplex pilot and integrated scene pass, continue the **remaining four** of the approved first-five building nominations in a bounded batch: stacked Montreal duplex, contemporary townhouse row, timber-and-glass apartments and courtyard apartments. Finish the other Wave 1 reuse integrations, then the second neighbourhood/community park, both plaza choices, the second local street and both active-travel choices. This completes the previously agreed 18-choice starter release without changing the 64-choice target.

Forecast that work from the measured pilot effort and correction time. Work does not advance merely because a time allowance expires; report a remaining blocker and its finite next fix. Retain the late-November production target and December rehearsal/freeze from the roadmap, adjusting the forecast openly if measured work requires it.

## Cost and current state

The prior live image/video test allowance remains **$10 total across the authorized work**, not a new allowance for this cycle. Check the spend record before any paid call; use local geometry and provider-free capture tests where possible. Keep generated assets and evidence in ignored or external storage and promote only reviewed deliverables. Do not delete historical output as part of setup.

**Current state: planned.** The next executable action is CAT-01: verify the existing exact assets and capture a reproducible baseline. No models, application code, saved projects or paid API calls were changed by preparing this next-step plan.
