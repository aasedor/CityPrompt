# City Prompt student studio implementation plan

Initiative: `codex/student-studio-2027`. Started 4 September 2026.

## Intended outcome

A novice can create a real-site community with buildings, parks, and roads and produce a presentation image in 15 minutes. The same proposal remains recognizable in images and videos. Optional context layers inform design. A sourced advisory report helps students explain their vision, implementation needs, and decisions to adopt, adapt, or decline recommendations.

The January class has 60 students in groups of approximately eight. Existing project sharing remains part of the workflow. Simultaneous editing and an interactive walkthrough are secondary to dependable design, saving, media, and reporting. The August presentation and goal-setting discussion supply the product requirements.

## Working rules and budget

- Work in the isolated `artifacts/worktrees/student-studio-2027` checkout, based on `679b76a35`. The original checkout and its pending building/ground changes remain untouched.
- Preserve the current catalogue and reuse existing building, public-realm, planning, rendering, and reporting infrastructure. No bulk asset generation or family promotion.
- Keep changes reviewable in coherent commits after relevant verification. Do not push or deploy as part of local implementation.
- Maximum live image/video API test spending authorized: **US$10 total**. Start with deterministic tests and mocked providers; track all live requests and conservative costs before dispatch. No unattended generation loop.
- The separate $50/student Google award is potential classroom capacity; provider eligibility, expiry, and pooling remain unknown.
- Test against an isolated local database and local files. Do not migrate or seed a deployed database.

## Implementation phases

| Phase | Work | Completion evidence |
| --- | --- | --- |
| 1. Baseline and working plan | Isolated source checkout, local services, asset reuse, brief, implementation ledger | Clean starting branch, local application loads, original user work preserved |
| 2. Reliable shared projects | Consistent permissions; invitation acceptance; public viewer repair; project-scoped undo; retain failed drawing saves; atomic paid admission | Permission and budget tests; two-account share/join; refresh/retry; public viewer and revoked link checks |
| 3. Reference information | Dedicated reference layers; shapefile/GeoJSON import preserving geometry and attributes; visibility/inspection; globe overlay; elevation readout | Import zoning inside/outside site; show/hide; confirm no new proposed buildings, masking, or inflated plan quantities |
| 4. Approachable studio | Clear Building/Park/Road entry points, sensible defaults, a compact home for layers/report/team/help; simple first-use guidance; readable save/render state | Browser exercise from project creation to placed elements and render preparation, including narrow screens and keyboard operation |
| 5. Planning report and decisions | Persisted plan snapshot, deterministic analysis plus available sourced city context, advisory findings and implementation steps; student response and rationale; printable submission | Report generated from actual geometry; no invented regulation; edit/refresh responses; stale-plan indication; submission export |
| 6. Faithful presentation media | Review geometry handoff, boundary and occlusion controls, same-scene capture, render/edit distinction, source revision association, video fidelity disclosure | Multi-angle fixture and capture tests; generated samples within budget; review recognizable identity, placement, boundaries, occlusion |
| 7. Integration and release rehearsal | Frontend/backend checks, production bundle, real local API/database flow, team/viewer/report/media rehearsal, feature documentation and rollback checkpoints | Explicit verified/unverified ledger, screenshots, test results, commit list, known limits |

Phases 2, 3, and 5 can be developed independently with root integration of shared models/router and the workspace. No agent commits while others are writing. Phase 4 is integrated around those stable feature contracts.

## Feature contracts

**Reference layers:** separate database records containing original GeoJSON geometry and properties, source metadata, and display settings. They do not enter the SiteZone proposal/compiler collections, boundary masking, or design quantities. Render capture excludes informational overlays by default. Existing explicitly authored plan layers retain their current semantics.

**Planning report:** students request analysis when ready. Findings include rationale, the relevant location, evidence or uncertainty, and possible next steps. Report generation never gates drawing or rendering. A named zoning alternative requires source support; missing evidence produces an investigation task. Students supply their own response and defense. Reports track the specific proposal snapshot and distinguish later changes.

**Media:** drawing and scale controls establish physical geometry. Render styles that geometry. Edit Render is a deliberate image change, distinguished from a model change. Hidden objects must not be repositioned to make them visible. Real-time walkthroughs are not a release dependency.

**Sharing:** accepted members use individual accounts; merely registering an invited address is not enough to access a project. Public viewing has its own revocable scope. Asset access must continue to work for images, video, and 3D loaders without exposing an account access token in URLs.

## Verification strategy

Use focused Vitest/pytest tests for each changed boundary, then TypeScript checking and lint for the integrated frontend. New persistence paths need local PostgreSQL verification in addition to mocks. Browser checks cover actual UI → API → database → reload and the resulting visible state. Generated media requires visual inspection, not just a successful HTTP response. Test failures are resolved before their checkpoint is described as complete.

The full release still needs an observed novice/student pilot and testing on the classroom's actual laptops and network. Local automated checks cannot establish usability for every student or prove perfect generative fidelity.

## Implementation status — 4 September

Implemented locally: the compact student toolbar and guide; reference-only GeoJSON/shapefile layers; optional sourced elevation; advisory report with persisted student decisions and printable plan; invitation acceptance and read-only viewing; scoped media downloads; atomic render credit admission; revision-aware drawing saves and undo; detached-house repetition inside the actual plot; concave boundary masks; same-camera geometry controls; server-recorded render provenance and conservative image review/fallback.

Integration verification is in progress. The production bundle and TypeScript check have passed an initial integration run. PostgreSQL probes cover concurrent credit reservation, repeated drawing saves, stale edits and invitation access; both new migrations passed upgrade/downgrade in a separate database. Real WebGL testing found and fixed packed-depth information disappearing during PNG conversion. Final results, remaining limitations and live API spending belong in the verification record beside this plan.

## Completing the full vision

The product has three connected experiences: **design the community**, **experience and present it**, and **explain how to make it real**. The January release prioritizes a dependable version of all three. It does not require every advanced feature to be enabled at once.

| Delivery | Concrete implementation | Acceptance check |
| --- | --- | --- |
| Real-site studio | Keep the existing Google globe and archetype catalogue. Offer Building, Park and Road first; put specialist controls behind selection or More Tools. Scale and footprint edits change the model. Preserve drafts and conflict feedback. | A novice finds a site, draws all three element types, changes one building and reaches a saved image in 15 minutes. Measure this with people unfamiliar with the app. |
| Consistent 3D | Reuse the RLASM v6.1 asset pipeline. Preserve each family's identity and floor bounds. Repeat detached dwellings with spaces and containment; use truthful massing when an approved family is unavailable. Keep source fingerprints through compilation, capture and presentation. | Review one approved family on a small, long and concave plot, then one mixed community from aerial and street views. No swapped family, out-of-plot model or relocated hidden element. |
| Import routes | Keep proposal imports distinct from reference data. GeoJSON and zipped shapefiles supply context with source/CRS/attribute inspection. Existing custom-building/library uploads need a guided preview for scale, orientation and placement. | Import a real municipal zoning file without increasing proposed building counts. Import one reviewed custom model and confirm metres, orientation, owner access and saved placement after reopening. |
| Sketch and AI starting plans | Reuse existing proposal-generation endpoints behind a preview. Ask students to choose a site and intent, then show editable buildings/parks/roads before committing them. A sketch needs calibration/georeferencing or a clearly declared conceptual placement; do not infer survey accuracy. | Accept a proposal as an undoable operation; individual elements remain editable. Rejected previews leave the project unchanged. Geometry changes never come from an ordinary style prompt. |
| Images and video | Capture from the compiled scene with matching camera, depth, normals, class/instance masks and source references. Retain the original scene and AI attempt. Save source version and review status. Extend the same source/version contract to video keyframes and route captures. | A finite mixed-scene review matrix covers an occluded building, concave boundary, tall/short neighbours and all three public-realm element types. Video is visibly labelled illustrative if it cannot preserve the proposal. |
| Street-level experience | First prototype a pegman camera in the existing 3D scene: choose a ground point, move/look, return to aerial, bookmark a view. Use terrain height, collision/step limits and conservative navigation bounds. A generative world-model adapter is a later experiment, with no dependency on a particular provider being available. | Walk between two known buildings, revisit the starting point, and see the same geometry. Keyboard instructions, Escape/return and camera recovery work. If laptop performance or asset quality is inadequate, deliver saved street images and a guided video instead. |
| Planning adviser | Start with measured geometry and an explicitly scoped set of municipal documents. Separate observed quantities, sourced requirements and questions. Provide actionable investigation/implementation steps; suggest a specific rezoning designation only when evidence supports it. | Students can adopt, adapt or decline each suggestion and explain why. Reopening preserves their words. The hand-in includes the plan, sources, uncertainties and decisions. No advisory finding disables design. |
| Classroom operation | Test approximately eight projects with 60 accounts, realistic image queues and ordinary campus laptops. Configure account/project budgets using confirmed Google-credit rules. Provide project export/backup, recovery guidance, render cost/status and one instructor support path. | Recover from a dropped connection, concurrent save, revoked invite and failed provider call. A queued or failed paid render has a visible outcome and a reconcilable ledger. |
| Wider adoption | After teaching evidence, provide starter sites, a short demo, shareable presentations and an optional opt-in showcase. Keep project ownership and export clear. Measure completion and repeat use rather than adding more control panels. | A new user reaches a first result without live coaching; a reviewer can open a presentation without editing access. Publishing a student's work remains a deliberate action. |

The imported-building/sketch preview refinements, complete video provenance extension and interactive navigation prototype are further implementation work; they are not claimed as completed by this local change set. Existing features are retained where noted, but a retained feature is not automatically a verified one.

## Suggested teaching schedule and release gates

- **September:** review this local version together and integrate it with the owner's ongoing RLASM/ground branch. Run the one-family visual pilot and five novice sessions. Fix observed blockers before expanding the asset catalogue.
- **October:** rehearse a complete group assignment on one real community site. Curate a small set of relevant city sources; validate zoning import, report quantities, custom-model import and presentation consistency. Test the street-level prototype only after the core scene is dependable.
- **November:** rehearse the 60-account class setup, queues, credit limits, backups and recovery on the actual network and laptop range. Confirm which APIs the student Google credits cover. Choose the January image/video/walkthrough scope using evidence from the pilot.
- **December:** freeze the teaching workflow, create the short student guide and instructor rubric, capture a worked example, perform restore and rollback rehearsals, and fix critical defects without expanding scope.
- **January:** start with the simple design-to-presentation exercise. Use the report and student defenses as part of the learning activity. Collect consented feedback before planning wider release.

Release gates are observed tasks: five novices completing the exercise; zero lost drawings in recovery tests; public links and viewer permissions behaving correctly; approved small/long/concave building pilots; a report that distinguishes evidence from uncertainty; and a classroom rehearsal with predictable cost and recovery. Numeric performance targets should be set from the actual teaching devices. These gates require classroom and human review beyond local automated checks.
