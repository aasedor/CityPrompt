# Recent memory and next steps — 19 September 2026

Read this first when resuming in a new window. This is the latest handoff after
live Batch A browser QA and the user's correction to test on an empty parcel.
Older handoffs saying Docker is unavailable or no browser testing occurred are
historical; the actual results below supersede those statements.

## Latest continuation checkpoint

**Reusable archetype integration (20 September):** the user requires these
lessons to carry into every future building, street and park archetype. Read
`docs/ARCHETYPE_RUNTIME_INTEGRATION.md` and complete
`docs/ARCHETYPE_RUNTIME_REVIEW_TEMPLATE.md` per exact variant. AGENTS, CLAUDE,
building publication and public-realm guidance now link this shared checklist.
Update it with subsequent generalizable findings. It is a contributor/reviewer
requirement, not yet a fully automated CLI gate; it does not retroactively
approve assets or change RLASM 6.1.

**3D entrance-picking pilot (20 September):** read
`docs/CURRIE_3D_ENTRANCE_PICK_BROWSER_QA_2026-09-20.md` first. Students can
choose a low native-house step directly in 3D, receive current-ground approach
feedback, and save explicitly. Drafts survive dragging/cancellation; stale
plot edits cannot be overwritten. The modern-infill pilot on the disposable
Currie copy passed pick/save/reload and restored its original entrance settings.
All seven houses returned to ready ground without warnings. Focused checks
passed 46 tests, type-check, and changed-file lint. Next: Craftsman/Edwardian
browser pilots and setback recovery, then high-foundation design review and
the full novice journey. Original Currie remains unchanged; no push occurred.

**Seven-house entrance continuation (20 September):** read
`docs/CURRIE_SEVEN_ENTRANCE_BROWSER_QA_2026-09-20.md` first. A disposable
full-layout copy now has all seven native-step entrance anchors; browser ground
was ready after reload with two stable passes, seven visible models, seven
connected routes, and zero building-ground warnings. West 3 required a bounded
0.6 m setback; the Edwardian and four infills connected at their original
locations. A form-step bug that prevented saving the Edwardian's exact 1.65 m
walkway width was fixed and browser checked. The original Currie project was
not edited. The high Craftsman foundation, long concept stairs, landings,
guards, accessible route, furniture clearance, and novice authoring journey
remain release work; zero warnings do not establish student-ready acceptance.

**Connections plot guide:** read
`docs/CURRIE_CONNECTION_GUIDE_BROWSER_QA_2026-09-19.md`. The building
Connections dialog now has a pointer/keyboard plot-position guide alongside
its exact offsets. Browser check on the disposable seven-house Currie copy
showed the saved marker, live offset updates, and Cancel restoring the saved
anchor. It does not infer or verify the native door or resolve the remaining
grounding work.

**Stair body pilot:** read `docs/CURRIE_STAIR_BODY_BROWSER_QA_2026-09-19.md`.
The approach now renders shallow treads with two slim continuous stringers
instead of a full-height wall below every tread. On the seven-house disposable
Currie copy at the 2.4 m setback, browser ground was ready with seven visible
houses; the first entrance remained issue-free and the other six remained
blocked. The screenshot is visibly less bulky, but the high foundation,
missing landing/edge treatment, and remaining entrances are not accepted.
The original Currie fixture remains untouched.

**Seven-house layout follow-up:** read
`docs/CURRIE_FULL_LAYOUT_ENTRANCE_REVIEW_2026-09-19.md`. A disposable copy
verified that 1.2 m and 2.4 m westward placements of `Shared street west 2`
fit the vacant Currie boundary without overlapping six neighbouring plots,
the street, or the park. Browser ground was ready with seven visible houses;
the first entrance was issue-free and the other six retained their warnings.
Pedestrian views show a high exposed foundation and long unguarded concept
stair. No placement was promoted to the original fixture; entrance design
and the other six houses remain release work. The working tree's latest source
commits are `65d28c884` and `726ba18ef`; no push was made.

**Latest entrance continuation:** read
`docs/CURRIE_ENTRANCE_BROWSER_QA_2026-09-19.md` first, then
`docs/BUILDING_ENTRANCE_GROUND_HANDOFF_2026-09-19.md`. The source adds
terrain-supported entrance approaches and capture gating for raised
foundations. Browser review passed on a measured one-bungalow disposable
Currie copy after moving the house 1.2 m from the street. It also exposed an
Undo defect: a restored street acquired a new ID and stranded the entrance.
That identity path was fixed and rechecked live. The original seven-house
fixture remains unchanged and entrance-blocked, so Batch A is not accepted.
The earlier "no production source changed" statement below describes the
prior browser continuation only.

Read `docs/CURRIE_GROUNDING_CONTINUATION_2026-09-19.md` before executing the
older next-step list below. The vacant Currie browser continuation has now
verified rotation/Undo/Redo/reload, sampled tile-refinement stability, capture
waiting during refinement, a 0.40 m concave crossing and inward recovery in a
further disposable copy, park navigation/deletion cancellation, and one bounded
context interruption/recovery. **Batch A is still unaccepted:** the first western
bungalow's stairs end on a raised generated foundation, with an additional drop
to surrounding ground. This is visible despite the solver reporting ready.

The main Currie fixture retains seven houses, park, street and its unchanged
eight-vertex site boundary. `Shared street west 2` now retains the tested 95-degree
rotation; exact original geometry is saved externally. The further disposable
copy is `bfcc05d2-b5b8-4447-8fe3-79f0f6e60a3d`; its temporary notch was restored,
house moved 22 m north, and temporary cancellation park deleted. All browser
network interruption routes were removed. No production source or catalogue
assets changed in this continuation, and no paid AI generation or push occurred.
Use the new report's next bounded work and evidence qualifications. Do not repeat
fixture creation or mistake successful captures for entrance acceptance.

## Working location and rules

- **Use `C:/dev/CityPrompt-grounding-edit-race`**, branch
  `codex/grounding-edit-race-hardening`. Do not run the tests against the original
  OneDrive checkout or copy its unrelated changes into this worktree.
- Source checkpoints before this memory: `4792bd950` (park sampling race),
  `78e28c234` (full footprint support and stale-capture invalidation), and
  `b89a822cd` (vacant Currie fixture documentation). The tree was clean before
  this handoff; these commits have not been pushed. Recheck Git status and HEAD.
- Read `CLAUDE.md` and applicable `AGENTS.md`. Preserve other worktrees and
  unpublished building-family waves. Do not reset, clean or stage unrelated work.
- The user prefers coding first, then browser testing with Sol to manage usage.
  If resuming under another model, do source work and prepare a bounded browser
  handoff; do not silently change models. Browser testing was explicitly
  authorized in this session. Do not spawn subagents.
- Preserve **all 22 established render styles**. LiDAR and Gaussian splats,
  image polish and new video features remain deferred while core reliability
  is being verified. Use current canonical catalogue/RLASM systems.
- No paid AI generation for this batch. Mission-wide external validation ceiling
  remains US $10; account credit renewal did not renew it. The ledger at
  `C:/dev-artifacts/CityPrompt/student-design-transformation/api-test-ledger.json`
  records $0.116525 image spend plus a $2 Maps reservation (actual Maps billing
  unavailable). Recent browser QA added no paid image/video calls.

## User's latest site requirement

Tests must be on **visibly open land**, without placing the proposal over
photographed streets or buildings, and the proposal should resemble nearby
development. Use this current fixture:

**Vacant Currie parcel — grounding QA 2026-09-19**

`http://127.0.0.1:5174/projects/f5bffc94-def9-4c43-942e-9ae7411872e9`

It contains seven one- and two-storey homes (two Craftsman bungalows, one
Edwardian Foursquare and four modern infill homes), a neighbourhood park and
a six-metre internal yield street. The parcel is near `51.01652, -114.12461`.
Google context before placement showed bare ground, with public streets and
occupied structures beside it. All nine proposal polygons are inside the
saved site boundary, with no positive-area pairwise overlaps. The buildings
fit the scale of nearby residential development. Ground and models settled
after reload; subsequent pedestrian-level review found the entrance drop
described above, and the source repair still needs visual verification.

The first broad rectangular boundary failed ground quality. The final fixture
uses the previously validated eight-vertex boundary from
`C:/dev-artifacts/CityPrompt/twenty-building-trial-2026-09-07/final-zone-inventory.json`,
which excludes the problematic patch. Preserve both the failure evidence and
final boundary. Do not keep reshaping or flattening it to conceal defects.

Details: `docs/VACANT_CURRIE_SITE_QA_2026-09-19.md`. The fixture was API-authored
using copied reviewed local representations, so it is not proof of the novice
placement journey. Visual openness does not establish current land ownership,
development rights, surveyed boundary or bare-earth elevation.

## Local runtime

At handoff, Docker was healthy, frontend `/login` returned 200, and backend
`/health` returned 200. Reuse healthy processes; do not start duplicate servers.

- Frontend: `http://127.0.0.1:5174`, from this worktree's `frontend` directory.
- Backend: `http://127.0.0.1:8000`, from this worktree via the external harness
  `C:/dev-artifacts/CityPrompt/grounding-batch-a/runtime.py`.
- Python: `C:/Users/andre/OneDrive/Documents/CityPrompt/backend/.venv/Scripts/python.exe`.
- Docker containers: `cityprompt-studio-2027-db-1` (PostGIS, port 55432),
  `cityprompt-studio-2027-redis-1` (56379), `cityprompt-studio-2027-media-1`
  (59002), and `cityprompt-studio-media-recovery` (19002, used by this harness).
- Local QA login: `studio-smoke@example.com`. The local fixture password is in
  the external harness's seed function; do not commit credentials or print
  API tokens. Existing agent-browser session is authenticated.

If a server has stopped, run these in separate terminals after checking ports:

```powershell
# Backend, working directory C:/dev/CityPrompt-grounding-edit-race/backend
$env:CITYPROMPT_STUDIO_MAPS_TEST = '1'
& 'C:/Users/andre/OneDrive/Documents/CityPrompt/backend/.venv/Scripts/python.exe' 'C:/dev-artifacts/CityPrompt/grounding-batch-a/runtime.py' serve
```

```powershell
# Frontend, working directory C:/dev/CityPrompt-grounding-edit-race/frontend
$env:CITYPROMPT_PUBLIC_DIR = 'C:/dev-artifacts/CityPrompt/student-design-transformation/public'
$env:VITE_ENV_DIR = 'C:/Users/andre/OneDrive/Documents/CityPrompt/frontend'
$env:API_PROXY_TARGET = 'http://127.0.0.1:8000'
npm run dev -- --host 127.0.0.1 --port 5174 --strictPort
```

The harness uses local services and disables paid AI providers. The Maps flag
loads only the existing Maps key for context. Do not run its seed/migrate modes
unnecessarily. Frontend `node_modules` is an existing ignored junction and the
public assets are hydrated externally; do not reinstall or regenerate blindly.

Browser automation uses the `vercel:agent-browser` skill and
`npx --yes agent-browser`. Quote refs in PowerShell (`'@e123'`), re-snapshot
after changes, and visually inspect screenshots. Do not dump raw network
JSON: it includes Authorization headers; print only needed URL/status fields.
Commands with long waits can outlast the shell tool's initial yield: preserve
the returned session ID and poll it rather than discarding the command result.

## Verified results and limits

- Source changes: stale park sampling callbacks/results are discarded after
  relevant edits; building support uses the complete site polygon (including
  narrow crossings and concave notches); capture freshness invalidates
  synchronously when relevant context changes.
- Automated checks already passed: 141 focused tests across 12 suites,
  TypeScript and changed-file lint. Exact commands are in
  `docs/GROUNDING_BATCH_A_BROWSER_HANDOFF_2026-09-19.md`. No source edits since
  that verification, only fixture documentation. Avoid rerunning everything
  unless new changes or findings warrant it.
- Real backend login, Google context, detailed model loading and free exact
  3D capture passed. All 22 image styles remain visible; people/vehicles default
  off. No paid generation was used in this QA.
- On a disposable prepared-site project, mid-rise rotation persisted through
  reload and Undo/Redo restored exact original coordinates. This is edit
  evidence, not empty-parcel or natural-ground acceptance.
- On a disposable Salisbury hillside copy, width/rotation edits during pending
  alignment and a descriptive-property edit during another pending alignment
  survived reload with a matching two-pass park terrain profile. Final width
  36 m, rotation 10 degrees, profile `reviewed-park-260d5642`, 1,020 samples,
  0 m pass difference, 0.337 m local residual. Other cancellation cases remain.
- Vacant Currie before/after overhead and oblique views were visually inspected;
  final reload showed all objects, no page errors and no failed requests.
- **Batch A/full grounding is not accepted yet.** Pedestrian contact, a complete
  mixed-object slope matrix, controlled tile-refinement/Z measurements, live
  boundary-crossing recovery, and bounded failure/recovery remain open.

## Next steps, in order

1. Verify branch, Docker and existing runtime. Open the vacant Currie project.
   Save its current zone/API snapshot and freeze useful aerial and pedestrian
   cameras before edits. Keep the empty-context screenshots for comparison.
2. Inspect house bases, entrances, street surface, park paths, trees and furniture
   close to ground from several directions. Rotate/move one house, Undo/Redo,
   reload and compare geometry. Record actual rendered base versus measured
   surface where tooling permits; report unresolved contact honestly.
3. Trigger relevant Google tile refinement by navigating aerial to close view.
   Confirm last safe proposal remains visible while verification is pending;
   free capture must wait, then succeed after stable passes. Check for Z jumps,
   flicker, excessive waiting and repeated network calls.
4. In a **further disposable copy**, exercise narrow/concave site crossings and
   move the object fully inside to test recovery. Preserve the occupied-land
   exclusion and do not weaken placement validation just to construct the test.
   An imported fixture may be needed for an otherwise correctly rejected plot.
5. Exercise remaining park cancellation/context-interruption cases from the
   park handoff. Use an open sloped parcel of appropriate surrounding scale;
   the earlier Salisbury copy is race evidence, not blanket acceptance of its
   expanded boundary as an empty-parcel test site.
6. Record PASS/FAIL/NOT TESTED with screenshots and source/API evidence. Fix only
   reproduced defects in coherent source slices, then focused tests/typecheck/
   lint and browser recheck. Once Batch A is accepted, start Batch B in
   `docs/NEXT_EDIT_PLAN_2026-09-19.md`: rapid building type/height/variant edits,
   late generation, failed saves, Undo and older-project recovery.

## Evidence and protected fixtures

All screenshots, API snapshots, runtime helpers and fixture manifests are in
`C:/dev-artifacts/CityPrompt/grounding-batch-a/`. Do not commit the directory or
rerun create/populate scripts: they create local DB state and may duplicate it.

- Latest live results: `LIVE_BROWSER_QA_ADDENDUM_2026-09-19.md`.
- Earlier mocked-only results: `BROWSER_QA_2026-09-19.md`; do not confuse them
  with live terrain proof.
- Vacant Currie manifest: `vacant-currie-project.json`.
- Before/after: `vacant-currie-empty-top.png`,
  `vacant-currie-proposal-top-settled.png`, `vacant-currie-reload-settled.png`.
- Earlier disposable prepared project: `2e4193cd-3963-445e-8459-4ec294122ffb`.
- Earlier disposable Salisbury project: `9464bbe3-6823-4e80-9fd0-ccbf4d246058`.
- Protected originals: Gold Standard `e18c8436-2612-4548-990e-0fa506748efd`,
  Salisbury `f289f565-1a52-43ec-accc-38cb5ac24ea2`, Currie 20-building source
  `3c12dda6-3b15-4151-bf8b-eb59628a99ff`.

Broader mission status: `docs/STUDENT_TRANSFORMATION_GATES.md`. Do not restart
Phase 0, replace strong systems, restore the five-style picker, or claim the
whole transformation complete from these bounded QA results. No push was made
for this batch; check current user authorization before publication.
