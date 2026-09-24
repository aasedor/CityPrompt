# Student-ready release plan

Updated: 23 September 2026. Owner: Andrew and the City Prompt implementation task.
Planning baseline: `17096bc99`, worktree `C:/dev/CityPrompt-sol-empty-lot-trial`.

This is the active execution plan for the first classroom release. It consolidates
the practical [readiness target](CLASSROOM_READINESS_PLAN_2026-09-20.md), the
broader [studio plan](STUDENT_STUDIO_IMPLEMENTATION_PLAN.md), and the recent
Currie trials. Earlier checkpoint documents remain evidence; their historical
"next steps" are not separate, cumulative release requirements.

## The finish line

A student can use a normal desktop browser to create a plausible neighbourhood
on a real vacant site, change their mind without losing work, and produce useful
presentation images. It should feel quick, forgiving and enjoyable at concept
scale. It does not need construction-level detail.

The release exercise is the existing approximately 35-minute assignment:

1. Create a project and an irregular boundary in the vacant Currie field, between
   the winding west road and straight east road. Make the terrain choice explicit.
2. Place 4–6 buildings with useful variety, a park, and connected streets. Include
   a curved street, a T or X intersection, a public-road connection and entrances.
3. Move/rotate an object, edit a street bend, change a supported variant, delete
   something, and use Undo/Redo. Placement offers a usable nearby fit when possible.
4. Generate the residual site landscape; keep trees in planting or wells on
   hardscape. Check the scene against surrounding Google tiles at close and wide views.
5. Save, close and reopen. The same geometry, connections and landscape return.
6. Download an exact PNG that opens outside the application. Create an optional
   attractive AI finish with honest fidelity status and retain the exact source.
7. Share the project with the intended classmate/instructor role and submit the
   images with the short design explanation in the existing handout.

No paid image call is needed to complete the basic assignment. Strong AI finishes
remain a release objective, but an illustrative image cannot count as proof that
the student's design was preserved.

## Scope decisions

- **First supported environment:** desktop/laptop Chrome and Edge, initially at
  1280×720 or larger, with mouse or trackpad. Check actual classroom hardware and
  network before the class rehearsal. Embedded Codex downloads are a separate
  support item; a working preview alone does not count as a downloaded file.
- **Terrain:** explicit prepared-site redevelopment is the primary complete
  exercise. Preserve the existing natural-ground option and explain incomplete
  measurements/recovery. Do not silently flatten natural ground or claim a partial
  site is fully verified. Expanding natural-ground capability is later work unless
  the first assignment requires it.
- **Catalogue:** freeze a documented starter set of exact runtime variants in
  milestone 1. Start with the demonstrated infill, bungalow and mixed-use building
  types; local street; neighbourhood/teaching garden parks; one reviewed sports
  park; and the two native street pilots once accepted. Verify exact identities
  before promising any of these. Existing usable choices are preserved. A reference
  thumbnail or standalone GLB does not prove that an entry works in a saved project.
- **Teaching features:** existing sharing, reference layers and advisory reports
  stay available. Include a short share/view and report/export check in release
  verification; expanding these systems is not a new prerequisite for drawing.
- **Defer:** further catalogue generation, fine seams, exhaustive street engineering,
  automated legal/code certification, unrestricted terrain cases, mobile support,
  simultaneous editing, new video features and interactive walkthrough expansion.
  Preserve completed candidate assets for subsequent bounded catalogue releases.
- **No new spending or publication is authorized by this document.** Prepare all
  local work and review evidence first. Use existing funded test limits only;
  account refills and a classroom deployment require their own concrete decision.

## What is already demonstrated

| Area | Evidence already available | Still to establish for release |
| --- | --- | --- |
| Basic authoring and recovery | September 22 fresh-project exercise; September 23 mixed building/park/curved-street trial; several edit, Undo/Redo and reload checks | One frozen release build, supported catalogue and regular-browser repeat |
| Ground and landscape | Explicit prepared datum, measured edge closure, generated gardens, landscape refresh after street edits | Same behaviour across starter variants and deployed assets |
| Street geometry | Shared curved routes and T/X graph; native and compiled junction tests; mixed native pilot review | Native pilot catalogue/compiler integration and saved-project acceptance |
| Presentation | Exact PNG download in Edge; two attractive GPT Image 2.5 originals | Chrome download, supported-device timing, masked AI fidelity diagnosis |
| Asset availability | Local configured Model Library bucket has 28/28 checked GLBs | Complete starter catalogue manifests/modules/textures and classroom bucket |
| Teaching support | In-app guide, exercise and instructor observation sheet; earlier sharing/report work | Current build rehearsal with separate accounts and class infrastructure |

These are provisional agent trials. They do not establish independent novice
usability or classroom deployment readiness. Students are unavailable until winter;
complete the release rehearsal now and observe real beginners when available.

## Implementation milestones

Execute these in order, in coherent changes with their own verification. Start
each milestone from the preceding accepted checkpoint. Record completed evidence
here instead of creating another competing roadmap.

### 1. Lock the release baseline and starter catalogue

Approved implementation decisions: 60 students working in approximately eight
group projects; individual home placement; a starter-first picker with the larger
catalogue explicitly exploratory. AI finishes use concept fidelity (arrangement,
scale, street topology and park programme retained), with exact sources and honest
human/automatic review status. Hosting is undecided. No paid retry, refill, push
or deployment is authorized by the implementation approval.

**Deliverables**

- Create one release inventory: exact archetype/variant IDs, source revision,
  runtime representation, asset locations and hashes, visual approval status,
  supported edits/connections, and the current runtime review for each starter.
- Separate ready entries from candidates and reference-only assets. Resolve any
  starter entry whose card promises features absent from its 3D representation.
- Audit all starter dependencies, including generated family manifests, GLBs,
  textures and street modules. Use `scripts/check_model_library_storage.py` for
  its Model Library coverage and explicitly account for other asset stores.
- Triage the current assembly-suite result (114 passed, 71 failed). Some observed
  failures reference missing generated manifests; classify every failure before
  attributing it to setup. Repair release prerequisites or actual defects, and
  record the test/environment contract for unrelated catalogue candidates.

**Done when:** the starter roster is finite, every required asset is reproducible
from documented setup, candidate status is visible, and the release test baseline
has no unexplained failures. Do not skip tests merely to obtain a green result.

### 2. Finish reusable placement, street and park behaviour

**Deliverables**

- Complete Main Street and Market Street native pilots through the real catalogue,
  server compiler/recipe validation, saved project and export ownership paths.
  Keep rigid furniture at native dimensions along sampled street routes.
- Use the shared route/junction system for each starter street: straight and
  curved routes, both T orientations, X, mixed widths, and vehicle/pedestrian
  combinations. No overlapping slabs, fourth T stub or furniture in crossings.
- Verify forgiving building placement and entrance-to-sidewalk connections for
  the starter buildings. Apply shared nearest-valid-placement recovery where
  needed; offer an understandable recovery when no fit exists. Do not silently
  alter neighbouring objects or place outside the site to force a fit.
- Verify the starter parks at their supported sizes, including one sports park:
  recognizable programme, intact court markings/equipment, paths and street
  access, clearances, vegetation and wells where appropriate. Do not shrink away
  the defining programme while retaining the same promise in the picker.
- Capture reusable findings in
  [ARCHETYPE_RUNTIME_INTEGRATION.md](ARCHETYPE_RUNTIME_INTEGRATION.md) and the
  [per-variant review template](ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md).

**Done when:** each starter's exact runtime review passes its applicable tests
and live Currie placement/edit/Undo/Redo/reload/free-capture checks. The two native
pilots must pass before applying their integration pattern to the remaining new
streets. Other completed models remain preserved for bounded follow-on batches;
their rollout does not hold this release unless they are in the frozen roster.

### 3. Close authoring and recovery gaps as one student workflow

**Deliverables**

- Exercise Site → Design → Present using only ordinary controls, including a
  freshly drawn irregular boundary and typed project location.
- Verify pending saves, failed saves/retry, optional context-service failure,
  object removal/restoration, street edits and reload. A saved boundary remains
  usable when optional context lookup fails. Failed edits preserve prior work.
- Confirm that automatic recompilation retains generated landscape and explains
  when it needs refreshing. Refresh updates the same proposal and unblocks media.
- Review close/wide scene quality: no missing, floating or buried starter assets,
  obvious scale errors, blocked entrances or exposed giant site slab; the sky
  stays blue and the ground-gap treatment stays on the ground.
- Measure cold project load, repeat load, normal edit/save and ready-scene free
  capture on the supported test device. Record device, viewport, cache and network.
  Use a working target of a ready-scene 1280×720 exact preview within 20 seconds;
  long work must show progress and an actionable timeout/retry without losing work.

**Done when:** the complete exercise has no blocking failure or developer-only
repair, saves survive reload, and slow/error paths are understandable. Previously
passed checks are repeated only where changes or the final integrated run justify it.

### 4. Make presentation outputs dependable and credible

**Deliverables**

- Download and open actual exact PNG files in Chrome and Edge, at a close detail
  view and a whole-site view. Include Google context, final ground and landscape.
- Prepare a fixed close/wide AI comparison with retained source, proposal/instance
  masks, model/settings, returned original and gate diagnostics. Diagnose changed
  buildings, street topology and park layout separately from allowed vegetation,
  material, lighting and surrounding-context changes.
- Prefer offline replay and deterministic checks first. The next live comparison
  is at most two image requests, only within available authorized credit, with
  explicit accounting and no automatic retry loop. The last local trial recorded
  only 14 tokens remaining; recheck availability before dispatch.
- Correct proven capture/gate/prompt defects. Never lower a threshold just to pass
  attractive images. Save the exact source, AI original and understandable review
  status together, including when the source is used as fallback.

**Done when:** exact exports work and the bounded comparison yields useful,
visually reviewed AI finishes that preserve the important authored design. If
fidelity remains unresolved, record that limitation explicitly; the basic exact-3D
exercise may be usable, but the polished faithful-AI goal remains open.

### 5. Prepare and verify the classroom deployment

**Deliverables**

- Prepare a release candidate, reproducible build/asset setup and deployment
  checklist for the actual HTTPS class URL. Localhost is not a class deployment.
- Verify account creation/sign-in, project isolation, invitations, editing/viewing
  roles, revoked access and saved-media access with separate test accounts. Review
  the previously flagged OAuth state, media accounting and worker configuration.
- Audit the actual destination asset bucket; exercise model loading and downloads
  from student accounts. Confirm required LFS/artifact files reach the deployment.
- Verify budget enforcement, failed-job refund/recovery and bounded queues with
  deterministic tests. Rehearse class-shaped concurrency using mocked paid
  providers. The earlier studio brief says 60 students in groups of about eight;
  confirm current enrolment, active projects and paid allowance before provisioning.
- Demonstrate backup/restore on a disposable project, record the known-good release
  and rollback steps, and provide a short instructor setup/support checklist.
- Review a concrete deployment candidate before any external release action that
  still needs authorization. Do not mark Git integration as hosted verification.

**Done when:** the deployed candidate passes login, asset, save/reopen, sharing,
export, budget and recovery checks from the intended class environment. An
instructor knows how to recover work and respond to a failed generation.

### 6. Run the final class rehearsal and freeze the release

**Deliverables**

- Use a new student account and fresh Currie project. Complete the finish-line
  exercise through the deployed UI, including a second-account instructor view
  and a short advisory-report/export check. Do not seed proposal geometry by API.
- Record completion time, help needed, load/export timings, exact outputs, visual
  evidence and any remaining minor limitations. Repeat the saved project on the
  other supported browser; inspect the plan and media after another sign-in.
- Fix release blockers, rerun their affected checks, then freeze the release
  revision, catalogue roster and first-session handouts. Add the real novice
  observation to the winter teaching schedule without calling simulation novice proof.

**Done when:** one coherent deployed release completes the assignment with no
lost work, no glaring scene errors, useful outputs and a documented support path.
Any remaining AI limitation is separately stated. Further ideas go into the next
release instead of restarting this plan.

## Release blockers and acceptable follow-up

Blockers include lost work, unauthorized project/media access, missing starter
models, impossible core tasks, visibly broken streets/entrances, major grounding
or scale errors, failed regular-browser export, unbounded spending, and misleading
claims that changed AI geometry is exact. A minor visual seam or optional feature
does not become a blocker simply because it can be improved.

Preserve existing asset/publication approvals as separate gates. Passing a student
exercise does not activate an unapproved family or grant construction compliance.

## Execution and evidence ledger

| Milestone | Current status | Exit evidence |
| --- | --- | --- |
| 1. Baseline and roster | Asset baseline and deployment inventory implemented locally | 185/185 assembly tests after restoring 65 tracked manifests; exact nine-variant roster and 47 byte-locked dependencies; local preflight 47/47; full inventory distinguishes metadata from hydration |
| 2. Shared runtime behaviour | Starter integration implemented; final acceptance partial | Native street backend/production renderer, individual homes, exact entrance revisions, starter picker; live Main/Market route check; [checkpoint](CLASSROOM_STARTER_RUNTIME_2026-09-23.md) |
| 3. Authoring/recovery | Partially demonstrated | September 22/23 local trials; release roster and regular-browser run pending |
| 4. Presentation | Durable recovery implemented and verified locally; image fidelity still open | Edge exact PNG; [concept fidelity, durable attempts and 60-student mock queue evidence](CLASSROOM_RENDER_RECOVERY_2026-09-23.md); faithful AI comparison and hosted recovery remain open |
| 5. Classroom deployment | OAuth state repair verified locally; deployment pending | [Single-use browser-bound sign-in](CLASSROOM_SIGNIN_RECOVERY_2026-09-23.md); local asset repair is not deployment evidence |
| 6. Release rehearsal | Pending | Depends on the accepted integrated candidate |

For each completed work package, record its commit, affected variants, checks,
artifact location and remaining limitation in this ledger or a linked checkpoint.
Keep one implementation initiative active, finish the relevant checks, and commit
the coherent unit. Run narrow tests and TypeScript checks for changed production
code, then the integrated release checks. Keep bulky evidence outside source and
never treat ignored local assets as shipped files.

Implementation checkpoint: the 71 assembly failures were individually matched to
FileNotFoundError paths in the saved test report; all 65 unique files were already
tracked and excluded by sparse checkout. Restoring them produced 185/185 passing
tests without changing assertions or regenerating assets. Evidence:
`artifacts/student-release-assembly-hydrated.xml` (ignored local output).

The versioned roster is `seed/classroom-release/starter-v1.json`; generated
frontend/backend copies and `scripts/classroom_release.py` provide identity/parity
and byte checks. All 47 dependencies pass against the current trial public root.
Sixteen street files were restored from local LFS cache. The existing infill v006
was packaged unchanged in LFS. `--require-release` remains red until exact-variant
runtime reviews pass. This is local source/asset evidence, not remote storage or
hosted success. Starter selection and native street compilation, saved recipes,
rendering and capture integration have since landed in milestone 2. Current work
addresses presentation recovery and classroom deployment prerequisites.

## Main evidence

- [September 22 simulated exercise](SIMULATED_STUDENT_EXERCISE_2026-09-22.md)
- [September 23 Currie trial and follow-ups](CURRIE_STUDENT_TRIAL_2026-09-23.md)
- [Native street catalogue pilots](NATIVE_STREET_CATALOGUE_PILOT_2026-09-23.md)
- [Shared junction follow-up](STREET_JUNCTION_NETWORK_FOLLOWUP_2026-09-23.md)
- [Curved route implementation](STREET_CURVE_GEOMETRY_2026-09-23.md)
- [First-session pack](CLASSROOM_FIRST_SESSION_2026-09-22.md)
- [Student assignment](CLASSROOM_STUDENT_EXERCISE.md)
- [Instructor observation sheet](CLASSROOM_TRIAL_OBSERVATION.md)
