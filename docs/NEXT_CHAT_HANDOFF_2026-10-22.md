# CityPrompt next chat handoff

Prepared 22 October 2026, America/Edmonton. The latest student trial is complete
locally. The user is opening a fresh chat for a large task that has not yet been
specified. Do not infer a new implementation or deployment request from this
handoff.

## Use the correct checkout

- Active checkout: `C:/Users/andre/.codex/worktrees/add-details-recovery/CityPrompt`.
- Branch: `codex/scene-readiness-recovery`.
- Tested implementation: `d527ffc6a968571d40847412f7c13ba099a90fe2`
  (`Fix scene readiness for bent streets and recovery`). This handoff follows it.
- Canonical remote: `origin`, `https://github.com/aasedor/CityPrompt.git`.
- User-authorized deployment branch in this conversation: `deployment-version`.
  This overrides the older `CLAUDE.md` main-branch release guidance for this work.
- Last locally observed `origin/deployment-version`:
  `6fb1a885e93d431322cf58d7548ea5671aa0fa6b`. This is a local tracking ref,
  **not a fresh verification of production**. The readiness fix has not been
  pushed or deployed.
- The chat's default cwd, `C:/Users/andre/OneDrive/Documents/CityPrompt`, is a
  different dirty checkout. Do not edit it or copy files over it accidentally.
- The active checkout has 226 pre-existing hydrated LFS asset modifications.
  Preserve them; do not reset, clean, stage wholesale or include them in a push.

Read `AGENTS.md` and `CLAUDE.md`, run `git status --short --branch`, and inspect
overlap before editing. Relevant guidance: `docs/CLASSROOM_READINESS_PLAN_2026-09-20.md`,
`docs/ARCHETYPE_RUNTIME_INTEGRATION.md`, and, for building authoring, the current
RLASM method and repository policy. Isolate a new initiative from the readiness
branch and preserve the unpublished fix.

## Completed readiness fixes

Read `docs/SCENE_READINESS_RECOVERY_2026-10-22.md` for exact changes and commands.
The fix covers native bent-street width validation, stale readiness/error state
after undo or deletion, and the default-off automatic-landscape gate for valid
boundary/details-only captures. It retains real geometry, revision, source and
asset checks. Do not suppress genuine failures to make the interface say ready.

Verification already completed on that source: **543 backend tests**, **1,132
frontend tests across 95 files**, a final **45-test touched-file rerun**, TypeScript
type check, production build and diff checks passed. Independent review found a
cross-layer gate mismatch that was fixed and re-reviewed. Browser placement,
unchanged street Apply, undo/redo, reload, image capture and a free video preflight
passed. No paid calls were used in that earlier regression trial.

## Latest student project and media

- Project: **East Village Commons — student stress trial**.
- URL: `http://127.0.0.1:5184/projects/4afa9383-2c0b-4ae9-834b-ecf2304f4911`.
- Local results page: `http://127.0.0.1:18131/review.html`.
- Evidence folder: `C:/dev-artifacts/CityPrompt/student-community-stress-2026-10-22`.
  Contains `review.html`, `stress-checks.json`, `paid-ledger.json`, `receipts.json`,
  screenshots, exact sources and completed media. Heavy output is outside Git.
- Five buildings: Brick-and-timber Courtyard Office, Green Terraces Parkade,
  Nordic Roof-Garden Apartments, Machiya café and gallery, Narrow-lot Craftsman
  Cottage. Two flexible parks, Planted Shared Lane and Concrete neighbourhood
  walk. Nine details: six people, two benches and one café table set.
- Three completed **Sunburst 2.5** images: `aerial-guide.png`, `street-guide.png`
  (photographic video guides) and `community-sunburst.png` (independent overhead).
- Two completed **Omni 1.1** four-second films: `aerial-omni.mp4` and
  `street-omni.mp4`. Corresponding polygon recordings: `aerial-source.mp4` and
  `street-source-corrected.mp4`. The uncorrected street source is retained as
  evidence, not the approved comparison source.
- Both film outputs: H.264, 1920 x 1080, 24 fps, 96 decoded frames. Container
  duration 4.01 s; sources exactly 4 s. Full FFmpeg decoding and browser playback
  passed. Both comparison pairs played to the end on the results page.
- Exactly three paid images and two paid videos completed, no automatic paid
  retries. Allowance **exhausted**. Local app tokens: 696 -> 394 (302 used).
  One initial guide attempt stopped before any provider call because saved jobs
  were disabled. Provider invoice totals were unavailable; video UI estimate was
  US$1.0136 each, with input charges extra. Do not treat old allowances as new
  authorization or regenerate these outputs.

Student checks passed for normal placement/save/reload; bench selection,
highlight, rotation, movement, deletion and undo/redo; walking and exit; and
Calgary zoning overlay loading and removal. Invalid boundary/overlap/size edits
were rejected without losing the valid scene. The café entrance connection saved;
the parkade auto-connection correctly rejected an approach over 30 m. Final reload
restored all nine details, five buildings, two parks and both routes; the gallery
showed both videos, the independent image and its 3D source. Final console check
captured no errors. No readiness failure recurred in this bounded trial.

## Remaining limitations and possible next work

- Dense-scene cost: first high-quality street capture measured **1,265 draw calls,
  2,855,604 triangles, 911 geometries and 790 textures**. CPU submission median
  **43.1 ms**, p95 **60.6 ms**; GPU/encoding time is additional. Desktop was an
  i5-14400F / RTX 5060 / 15.8 GB system RAM. These are capture statistics, not
  interactive FPS or decoded memory. Student-laptop/mobile suitability is untested.
- People have fixed forward animation without automatic collision avoidance.
  Opposing pedestrians intersected in a free preview; placement was adjusted
  before the paid street film. Paths and obstacles still need manual clearance.
- AI changes some planting and fine detail; aerial output is less photographic
  than its guide. The app flags both films for review. Similarity scores are not
  proof of building identity. Google tiles retain distorted/floating geometry.
- Optional OSM nearby-road suggestions returned 503; manual drawing worked.
  Street-name toggle state was exercised but actual label appearance was not
  visually verified. This was not an exhaustive test of every feature or model.
- No application source changes were made during the latest student trial.
  Runtime setup was repaired locally, as below. Nothing from this trial was
  pushed or deployed. Re-establish hosted identity before any future deployment.

## Local runtime and safe restart

At handoff, frontend `http://127.0.0.1:5184` and review page returned HTTP 200;
API `http://127.0.0.1:8012/health` returned healthy. Ports/processes may change
after restart; inspect rather than kill or replace an unknown listener.

- Local database: localhost:55432 / `cityprompt_repairs_20261004`.
- Local Redis: localhost:56380, DB 2. Media object storage: localhost:19003.
- API/worker/beat PIDs at trial: 32360 / 33840 / 28820. These are observations,
  not durable process identities. Local review server PID was 31660.
- Local setup already had migration 030/table `render_attempts`, but
  `DIRECT_3D_JOBS_ENABLED` was unset and no worker ran. After confirming zero
  queued/running jobs and empty queues, started existing Celery worker/beat and
  enabled saved jobs **in the API process environment**. No migration or persistent
  backend `.env` edit was made. No secrets are in this handoff.
- Guarded trial launcher and process/log evidence are in the evidence folder:
  `start-render-runtime.py`, `runtime-processes.json`, `api.*.log`, `worker.*.log`,
  `beat.*.log`. It starts API + worker + beat. Do not rerun it against active
  processes or pending jobs. Inspect queue contents before starting a worker so
  old paid jobs cannot run unintentionally. The older `start-local-api.py` launcher
  alone does not enable durable image jobs or start their worker.
- Review server: run `serve-review.py` from that evidence folder if port 18131
  is free. It binds localhost and only serves whitelisted media and `review.html`.
- Frontend uses ignored `artifacts/local-runtime.json` in the active checkout.
  It points to the hydrated public assets, production catalogue packet, local env
  directory and API proxy. Preserve it. Default builds without that hydrated
  setup can fail correctly; do not disable asset guards.

The live URL historically used is `https://www.cityprompt.ca`; production commit,
Render service state and authentication were not inspected in this latest task.
Do not assume local parity or reuse a stale deployment ID. Preserve real user
scenes, credentials, domains and services. No new paid resources, LFS-policy changes,
paid retries, bulk asset publication or deployment without applicable authorization.
