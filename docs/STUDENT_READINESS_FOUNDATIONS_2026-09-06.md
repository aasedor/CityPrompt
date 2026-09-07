# Student readiness foundations — implementation and trials

This follows the four-stage plan agreed after `STUDENT_BETA_TRIALS_2026-09-06.md`. It implements a first foundation release, not a claim that terrain engineering or generative-image fidelity is solved. Source branch: `codex/student-readiness-foundations`, based on `6dbfcfc18`. No catalogue expansion or production publication was performed.

## Ground review and recovery

- Added **Review ground** beside the globe controls. It shows a north-up sample grid, the measured range inside the site, missing/outside cells, and abrupt-change markers. Samples are visible-mesh measurements, not automatically classified bare earth.
- Students can retain existing terrain or explicitly set and save a common level for redevelopment. The panel explains the difference between the proposed level and the visible range. Selecting a coloured sample fills the level field; the numeric field also supports a chosen level.
- Fixed quality checks considering remote corners of the site's rectangular support grid. Every cell touching the actual boundary remains checked, including thin boundary intersections. Discontinuities in cells that cannot support the site no longer cause rejection. Full finite sample coverage and repeatability remain required; no values are interpolated to replace missing observations.
- The hillside fixture's reported maximum slope dropped from 3.433 to 0.994 after excluding irrelevant corners, but the edge still failed the existing 0.45 threshold. This is a real remaining edge mismatch, not grounds to relax the limit.
- Used the UI to set **Beta B - Sloped hillside** (`7e314bbc-cebd-4d9c-a8fe-a67cf48e7622`) to 1052.5 m. The bungalow became visible on the prepared surface. The free 3D export succeeded. The earlier follow-terrain failure remains documented in the beta report.
- Placement ghosts now use the prepared site's common level or ready shared ground, rather than the original Google roof height. Draft geometry and outlines are excluded from captures.

Remaining: this is a level-surface recovery workflow. It does not design sloped grading, ramps, retaining walls, cut/fill volumes or smooth boundary transitions. A terrain preview is available, but there is not yet a fully editable 3D grading preview. Realistic edge treatment remains a priority before calling hillside development classroom-ready.

## Pre-placement reshaping

- Added width, depth and rotation fields before dropping an asset. **Update placement preview** updates the ghost without creating a zone. Native minimum/maximum limits are enforced; rotation is normalized.
- Tested a zero-width entry: update stayed disabled. Tested an 18×20 m post-war bungalow at 90° on desktop and inspected the controls at 1024×768.
- Placed that bungalow on the occupied/redevelopment fixture **Beta C** (`c4477d4b-f0dc-4e0a-9a3e-1730b75a161f`) using the mouse. Saved zone `bbdfe823-dc9f-4c9f-a818-2a7cecd42cf8` read back as 18×20 m, rotation 90°, compiled. Reloaded the project afterward.
- Existing boundary/overlap rejection and cancel controls remain active. Automatic best-fit suggestions and richer clearance guidance are future refinements.

## Faithful presentation and controlled render trial

- Added **Export current 3D view · free**. It takes a fresh clean capture, opens a downloadable full-resolution image, and makes no image-provider call. It preserves the current geometry and Google context. The free QA thumbnail is not reused.
- Prevented a paid render from starting during a free capture/export.
- Compared the current presentation-first finish and the existing source-detail fusion route. The latter was enabled only in an external isolated launcher; it was not promoted or committed as the default.
- Both calls used project A (`4986a3f4-8653-4d71-b303-9c1724b46da0`), photorealistic/precise, identical custom instructions, identical attachments and capture fingerprint `b32b213e53e537e0`. Proposal coverage was 46.6%. Buildings were behind park trees and the foreground park was cropped. Browser camera zoom used a DOM wheel event through the existing handler, as in the earlier beta trial.

| Trial | Runtime route | Time | Result |
|---|---|---:|---|
| 6 overall / 1 this work | Existing presentation-first | 116.20 s | Source fallback. AI original added a straight paved strip along the park edge and changed visible fine details. |
| 7 overall / 2 this work | Existing source-detail fusion route | 126.62 s | Source fallback again. AI original changed materials and public-realm details; no demonstrated usable improvement from the alternative route. |

Final/original IDs:

- Trial 6: `4630aca2-5295-4d77-9275-346efcfbdf16` / `0fb251c9-e3a8-44d0-90cc-61a375b642ed`.
- Trial 7: `ea9ca260-2d28-454c-9088-605bec5e5ee6` / `a2982efe-52f5-43eb-890c-77bb2496b713`.

This is a controlled source/camera comparison with two independently generated AI images, not a statistically isolated comparison of post-processing on one identical provider output. Existing registration already separates luminance correlation from structural-context agreement; the experiment did not justify weakening its thresholds. Both originals remain available for review. Default presentation-first runtime was restored after the trial.

Two provider calls were used here: 170 application credits (9615 → 9445). Seven calls total across this and the preceding beta work, within the ten authorized. Application credits are not dollars; provider dollar cost was not independently reconciled. No further media generation is running.

Remaining: automatic AI finishing still cannot reliably preserve every pathway, opening and material. The dependable presentation option is the exact 3D export. A better material-constrained generation method needs another bounded pilot; the alternative tested here should not be advertised as a fix.

## Reports and classroom UI

- A single native, assembled detached-house recipe is now counted as one dwelling, in addition to repeated-house recipes. It must be a current compiled detached archetype with a native scale lock; stale or malformed recipes remain unknown.
- Direct building zones use the canonical `floor_count` field, with legacy `floors` support.
- Missing building footprints/floor areas now display **Unknown**, rather than misleading zero totals. Partial totals are labelled incomplete. Empty plans still report true zero where appropriate. Detached plot yards are never counted as floor plates.
- Requested a new report on A. It correctly showed **3 detached dwellings, 0 plots awaiting compilation**, and **Unknown** measured floor area. Existing reports and saved student decisions remain separate historical records.
- The render credit balance now refreshes after a successful charge. Observed 9615 → 9530 → 9445 immediately after the two calls, without reloading.
- Saved file counts explicitly include AI originals. Rendering closes an already-open gallery; saving a result updates the gallery badge without opening another floating panel over the render controls. This removes the observed automatic overlap on tablets.

Remaining: exact floor-plate metadata is still needed for published native assets; the report now honestly identifies that absence rather than inventing quantities. A human touchscreen trial and wider collaboration/reliability testing remain necessary before classroom rollout.

## Validation, runtime and evidence

- 109 frontend tests passed across 11 targeted files; TypeScript checking passed.
- 25 report tests passed, including native single-house counts, unknown quantities and canonical storeys.
- 17 existing render registration/fusion tests passed for the alternative-route pilot.
- Targeted ESLint and `git diff --check` passed. No uncaught browser page errors were returned during the trial.
- Local frontend: `http://127.0.0.1:5178`. Backend: isolated port 8002, standard presentation-first route restored. Other media providers remain disabled by the isolated harness.
- Screenshots, render originals/finals, audits and runtime logs are outside Git at `C:/dev-artifacts/CityPrompt/student-beta-2026-09-06/`, including `ground-review-new.png`, `b-prepared-level-1052-5.png`, `tablet-placement-reshape.png`, `c-reshaped-placed.png`, `fidelity-pair-source.png`, and `foundations-render-audit.json`.
- The original OneDrive checkout and its pre-existing changes were not modified. No heavyweight generated files are staged with this source work.
